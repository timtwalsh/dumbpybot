import discord
import random
from discord.ext import commands

DEBUG = False
TICK_RATE = 6  # Default
emoji_letters_dict = {'A':  '🇦', 'B':  '🇧', 'C':  '🇨', 'D':  '🇩', 'E':  '🇪', 'F':  '🇫', 'G':  '🇬', 'H':  '🇭', 'I':  '🇮',
                      'J':  '🇯', 'K':  '🇰', 'L':  '🇱', 'M':  '🇲', 'N':  '🇳', 'O':  '🇴', 'P':  '🇵', 'Q':  '🇶', 'R':  '🇷',
                      'S':  '🇸', 'T':  '🇹', 'U':  '🇺', 'V':  '🇻', 'W':  '🇼', 'X':  '🇽', 'Y':  '🇾', 'Z':  '🇿', ' ': '✴'}

class Misc(commands.Cog):
    def __init__(self, bot):
        global TICK_RATE
        TICK_RATE = bot.TICK_RATE
        self.bot = bot
        self.SHORT_DELETE_DELAY = bot.SHORT_DELETE_DELAY
        self.time_elapsed = 0

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # tracks user activity.
        if DEBUG:
            channel = after.guild.get_channel(self.bot.DEBUG_CHANNEL)
            if channel is not None:
                if after.activity is not None:
                    await channel.send('{0.name}, now playing {0.activity.name}.'.format(after))
                elif before.activity is not None:
                    await channel.send('{0.name}, stopped playing {0.activity.name}.'.format(before))

    @commands.command(name='add', aliases=['plus'])
    async def do_addition(self, ctx, first: int, second: int):
        """A simple command which does addition on two integer values."""
        total = first + second
        await ctx.send(f'The sum of **{first}** and **{second}**  is  **{total}**')

    @commands.command()
    async def winners(self, ctx):
        """A simple command which does addition on two integer values."""
        past_winners = ["Season 1 - Mangles", "Season 2 - Mangles", "Season 3 - Dave"]
        msg = "Shekel Season Past Winners\n```"
        for winner in past_winners:
            msg += winner
            msg += '\n'
        msg += "```"
        await ctx.send(f'{msg}')

    @commands.command(name="nopeprevious", aliases=['nopethat'])
    async def nopethat(self, ctx, *, member: discord.Member = None):
        channel = ctx.channel
        async for message in channel.history(limit=10):
            if ctx.author != message.author:
                react_message = message
                break;
        letter_reaction = "NOPE"
        log = await self.bot.get_channel(self.bot.LOG_CHANNEL).send(str(react_message.author) + ": " + react_message.content)
        for letter in letter_reaction:
            try:
                await react_message.add_reaction(emoji_letters_dict[letter])
                await log.add_reaction(emoji_letters_dict[letter])
            except discord.HTTPException:
                print(self.qualified_name,"failed to react to Message by:",ctx.author,", Letter:",letter)
        await ctx.message.delete(delay=self.SHORT_DELETE_DELAY)

    @commands.command()
    async def sadkek(self, ctx):
        log = await self.bot.get_channel(self.bot.LOG_CHANNEL).send(str(ctx.author) + ": " + ctx.message.content)
        try:
            await ctx.message.add_reaction('<:sadKEK:688339429508775955>')
            await log.add_reaction('<:sadKEK:688339429508775955>')
        except discord.HTTPException:
            print(self.qualified_name, "failed to react to Message by", ctx.author)
        await ctx.message.delete(delay=self.SHORT_DELETE_DELAY)

    @commands.command()
    async def purge(self, ctx, purge_count=2):
        if str(ctx.author.id) == self.bot.ADMINISTRATOR:
            if purge_count >= 1:
                deleted = await ctx.channel.purge(limit=int(purge_count))
                delete_message = False
                await ctx.channel.send('{} Deleted {} message(s)'.format(ctx.author, len(deleted)),
                                       delete_after=self.bot.SHORT_DELETE_DELAY)

    async def timeout(self):
        channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        if not self.bot.is_closed():
            self.time_elapsed += TICK_RATE
            if DEBUG:
                await channel.send(f"{self.qualified_name}: {self.time_elapsed}")

def setup(bot):
    bot.add_cog(Misc(bot))
