import asyncio
import json

import discord
import random
from discord.ext import commands

DEBUG = False
TICK_RATE = 6  # Default
emoji_letters_dict = {'A': '🇦', 'B': '🇧', 'C': '🇨', 'D': '🇩', 'E': '🇪', 'F': '🇫', 'G': '🇬', 'H': '🇭', 'I': '🇮',
                      'J': '🇯', 'K': '🇰', 'L': '🇱', 'M': '🇲', 'N': '🇳', 'O': '🇴', 'P': '🇵', 'Q': '🇶', 'R': '🇷',
                      'S': '🇸', 'T': '🇹', 'U': '🇺', 'V': '🇻', 'W': '🇼', 'X': '🇽', 'Y': '🇾', 'Z': '🇿', ' ': '✴'}


class Gambling(commands.Cog):
    def __init__(self, bot):
        global TICK_RATE
        TICK_RATE = bot.TICK_RATE
        self.bot = bot
        self.gambling_history = {}
        self.user_gambling_history = {}
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

    @commands.command(aliases=["heads", "tails"])
    async def gamble(self, ctx):
        """Coin Toss"""
        bet_string = ctx.message.content.split(' ')
        print(ctx.author.id, )
        msg = f'Coin Toss:  {ctx.author} bets {bet_string[1]} on {bet_string[0]}...'
        message = await ctx.send(msg, delete_after=self.bot.LONG_DELETE_DELAY)
        message_head = message.content.split("...")[0]
        message_head = message_head + "```"
        bet_user = str(ctx.author)
        bet_user_id = str(ctx.author.id)
        bet_side = bet_string[0]
        if len(bet_string) > 1:
            bet_amount = float(bet_string[1])
        else:
            bet_amount = 1.0
        user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
        if user_balance >= bet_amount:
            self.bot.get_cog('Currency').remove_user_currency(bet_user_id, bet_amount)
        rolls = [0] * 5
        for i, roll in enumerate(rolls):
            random_roll = random.randint(0, 1)
            if DEBUG:
                print(i, random_roll)
            rolls.remove(0)
            if random_roll > 0:
                rolls.append(1)
                outcome = "heads"
            else:
                rolls.append(-1)
                outcome = "tails"
            msg = "Roll... {}\n".format(outcome)
            await message.edit(content=message_head + msg + "```")
            message_head = message_head + msg
            if rolls.count(1) >= 3 or rolls.count(-1) >= 3:
                break
            await asyncio.sleep(i / 2 + 2)
        if rolls.count(1) >= 3:
            if bet_side == "!heads":
                self.bot.get_cog('Currency').add_user_currency(bet_user_id, bet_amount * 2)
                # all_users[bet_user].add_gamblestat("Heads", True, bet)
                user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                msg = "**Heads**, {} **Wins** §{}, now has §{:.2f}".format(bet_user, bet_amount, user_balance)
            else:
                user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                # all_users[bet_user].add_gamblestat("Tails", False, bet)
                msg = "**Heads**, {} **Loses** §{}, now has §{:.2f}".format(bet_user, bet_amount, user_balance)
        else:
            if bet_side == "!tails":
                self.bot.get_cog('Currency').add_user_currency(bet_user_id, bet_amount * 2)
                user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                # all_users[bet_user].add_gamblestat("Tails", True, bet)
                msg = "**Tails**, {} **Wins** §{}, now has §{:.2f}".format(bet_user, bet_amount, user_balance)
            else:
                user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                # all_users[bet_user].add_gamblestat("Heads", False, bet)
                msg = "**Tails**, {} **Loses** §{}, now has §{:.2f}".format(bet_user, bet_amount, user_balance)
        bet_user = ""
        await message.edit(content=message_head + "```" + msg.format(bet_amount, user_balance))
        await asyncio.sleep(self.bot.MEDIUM_DELETE_DELAY)
        await message.edit(
            content=message.content.split("```")[0] + "\n" + msg.format(bet_user, bet_amount, user_balance))
        msg = message.content
        log = await self.bot.get_channel(self.bot.LOG_CHANNEL).send(msg)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)
        await message.delete(delay=self.bot.MEDIUM_DELETE_DELAY)

    async def timeout(self):
        channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        if not self.bot.is_closed():
            self.time_elapsed += TICK_RATE
            if DEBUG:
                await channel.send(f"{self.qualified_name}: {self.time_elapsed}")


def setup(bot):
    bot.add_cog(Gambling(bot))
