import json

import discord
import random
from discord.ext import commands

DEBUG = False
TICK_RATE = 6  # Default
emoji_letters_dict = {'A':  '🇦', 'B':  '🇧', 'C':  '🇨', 'D':  '🇩', 'E':  '🇪', 'F':  '🇫', 'G':  '🇬', 'H':  '🇭', 'I':  '🇮',
                      'J':  '🇯', 'K':  '🇰', 'L':  '🇱', 'M':  '🇲', 'N':  '🇳', 'O':  '🇴', 'P':  '🇵', 'Q':  '🇶', 'R':  '🇷',
                      'S':  '🇸', 'T':  '🇹', 'U':  '🇺', 'V':  '🇻', 'W':  '🇼', 'X':  '🇽', 'Y':  '🇾', 'Z':  '🇿', ' ': '✴'}

class Gambling(commands.Cog):
    def __init__(self, bot):
        global TICK_RATE
        TICK_RATE = bot.TICK_RATE
        self.bot = bot
        self.SHORT_DELETE_DELAY = bot.SHORT_DELETE_DELAY
        self.time_elapsed = 0

    # async def load_data(self, gambling_history=None, user_gambling_history=None):
    #     pass

    async def save_data(self):
        save_data = [{f'{self.qualified_name}.gambling': self.gambling}, {
            f'{self.qualified_name}.user_gambling': self.user_gambling}]
        try:
            with open(f'{self.qualified_name}_data.json', 'w+') as outfile:
                json.dump(save_data, outfile, sort_keys=False, indent=3)
        except:
            print(Exception)

    @commands.command(name="gamble", aliases=["heads", "tails"])
    async def gamble(self, ctx, money: int):
        """Gambles some money."""
        currency = self.bot.get_cog('Currency')
        if currency is not None:
            await currency.withdraw_money(ctx.author, money)
            if self.coinflip() == 1:
                await currency.deposit_money(ctx.author, money * 2)

    async def timeout(self):
        channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        if not self.bot.is_closed():
            self.time_elapsed += TICK_RATE
            if DEBUG:
                await channel.send(f"{self.qualified_name}: {self.time_elapsed}")

def setup(bot):
    bot.add_cog(Gambling(bot))
