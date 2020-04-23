import json
import random
import discord
import asyncio
import config
from discord.ext import commands

from json import JSONEncoder


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

DEBUG = False
TOKEN = config.TOKEN
BOT_PREFIX = "!"
ACTIVE_EXTENSIONS = ['Extensions.Currency', 'Extensions.ActivityStats', 'Extensions.Gambling', 'Extensions.Misc']


class Context(commands.Context):
    async def tick(self, value):
        emoji = '\N{WHITE HEAVY CHECK MARK}' if value else '\N{CROSS MARK}'
        try:
            await self.message.add_reaction(emoji)
        except discord.HTTPException:
            pass
    #
    # async def on_message(self, message):
    #     if message.author == self.user:
    #         pass
    #     else:
    #         pass


class DumbClickerBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TICK_RATE = config.TICK_RATE  # 10 times per minute
        self.SAVE_RATE = 30  # Save Every minute
        self.SHORT_DELETE_DELAY = 5
        self.MEDIUM_DELETE_DELAY = 30
        self.LONG_DELETE_DELAY = 60
        self.VERY_LONG_DELETE_DELAY = 240
        self.CURRENCY_NAME = 'shekel'
        self.CURRENCY_TOKEN = '$'
        self.LOG_CHANNEL = config.LOG_CHANNEL  # Log Channel is used for story Bot Usage History
        self.DEBUG_CHANNEL = config.DEBUG_CHANNEL  # Test Channel is used for debugging
        self.ACTIVITY_IGNORE_LIST = ['Spiralling Ever Downwards', 'Yu-Gi-Oh! Duel Links']
        self.time_elapsed = 0
        if DEBUG:
            print(f'__init__', end='')
        self.bg_task = self.loop.create_task(self.timeout())

    async def on_ready(self):
        print('Logged in as', self.user.name, self.user.id)
        for cog in self.cogs:  # Call timeout on all cogs.
            cog = self.get_cog(cog)
            if hasattr(cog, 'load_data'):
                await cog.load_data()
        print('------------------------------------------------------------')

    async def timeout(self):
        if DEBUG:
            print(f', timeout() started', end='')
        await self.wait_until_ready()
        if DEBUG:
            print(f', wait_until_ready() complete')
        channel = self.get_channel(self.DEBUG_CHANNEL)
        while not self.is_closed():
            for cog in self.cogs:  # Call timeout on all cogs.
                cog = self.get_cog(cog)
                await cog.timeout()
            self.time_elapsed += self.TICK_RATE
            if self.time_elapsed % self.SAVE_RATE < self.TICK_RATE:
                for cog in self.cogs:  # Call save on all cogs.
                    cog = self.get_cog(cog)
                    if hasattr(cog, 'save_data'):
                        await cog.save_data()
                        if DEBUG:
                            print(f'{cog.qualified_name} COG saved. ', end='')
                    else:
                        print(cog.qualified_name, 'no data to be saved.')
                print()
            if DEBUG:
                await channel.send(f"Parent: {self.time_elapsed}")
            await asyncio.sleep(self.TICK_RATE)  # task runs every 60 seconds

    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)


bot = DumbClickerBot(command_prefix=BOT_PREFIX)
for extension in ACTIVE_EXTENSIONS:
    bot.load_extension(extension)

bot.run(TOKEN)
