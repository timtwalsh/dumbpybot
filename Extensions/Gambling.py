import asyncio
import json
from collections import defaultdict

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
        self.user_gambling_history_old = {}
        self.user_gambling_stats = defaultdict()
        # self.gamblestats.setdefault('None',{'Heads': [0, 0, 0, 0]})
        self.SHORT_DELETE_DELAY = bot.SHORT_DELETE_DELAY
        self.time_elapsed = 0

    def add_gamblestat(self, bet_name="Bet", user_id="0", win=True, amount=0):
        try:
            if win:
                self.user_gambling_stats[user_id][bet_name][0] += 1
                self.user_gambling_stats[user_id][bet_name][1] += abs(amount)
            else:
                self.user_gambling_stats[user_id][bet_name][2] += 1
                self.user_gambling_stats[user_id][bet_name][3] += abs(amount)
        except Exception:
            print("ERROR")
            self.user_gambling_stats[user_id] = self.user_gambling_stats.get(user_id, {"Heads": [0, 0, 0, 0],
                                                                                       "Tails": [0, 0, 0, 0]})
            # self.gamblestats[user_id][bet_name] = [0, 0, 0, 0]
            if win:
                self.user_gambling_stats[user_id][bet_name][0] = 1
                self.user_gambling_stats[user_id][bet_name][1] = abs(amount)
            else:
                self.user_gambling_stats[user_id][bet_name][2] = 1
                self.user_gambling_stats[user_id][bet_name][3] = abs(amount)
        try:
            if win:
                self.gambling_history[f'{bet_name}_win'] += 1
            else:
                self.gambling_history[f'{bet_name}_loss'] += 1
        except Exception:
            if win:
                self.gambling_history[f'{bet_name}_win'] = 1
            else:
                self.gambling_history[f'{bet_name}_loss'] = 1

    async def load_data(self):
        try:
            with open(f'{self.qualified_name}_data.json', 'r+') as in_file:
                data = json.load(in_file)
                self.gambling_history = data['gambling_history']
                self.user_gambling_stats = data['user_gambling_stats']
                print(f"Loaded {len(data['user_gambling_stats'])} Members Gambling Data.")
        except FileNotFoundError:  # file doesn't exist, init all members with history to avoid index errors
            print("GAMBLING - LOAD ERROR")
            # for member in self.bot.get_all_members():
            #     if member.activity is not None:
            #         self.user_gambling_stats[str(member.id)] = {}
            #         self.user_gambling_stats[str(member.id)][member.activity] = 0

    async def save_data(self):
        try:
            save_data = {'gambling_history': self.gambling_history,
                         'user_gambling_stats': self.user_gambling_stats}
            with open(f'{self.qualified_name}_data.json', 'w+') as outfile:
                json.dump(save_data, outfile, sort_keys=False, indent=3)
        except:
            print(Exception)

    @commands.command(aliases=["mybets", "mygambles", "my_gamble_stats"])
    async def usergamblestats(self, ctx):
        """!mybets or !mygambles"""
        print(self.user_gambling_stats)
        msg = f'{ctx.author} Gambling Stats {self.user_gambling_stats[str(ctx.author.id)]}'
        message = await ctx.send(msg, delete_after=self.bot.LONG_DELETE_DELAY)

    @commands.command(aliases=["allgambles", "all_gamble_stats"])
    async def gamblestats(self, ctx):
        """!gamblestats or !allgambles"""
        print(self.user_gambling_stats)
        msg = f'{ctx.guild.name} Gambling Stats \n'
        for gamble in self.gambling_history.keys():
            msg += f'{gamble}: {self.gambling_history[gamble]}\n'
        message = await ctx.send(msg, delete_after=self.bot.LONG_DELETE_DELAY)

    @commands.command(aliases=["heads", "tails"])
    async def gamble(self, ctx):
        """!heads [amount] and !tails [amount]"""
        bet_string = ctx.message.content.split(' ')
        print(ctx.author.id, )
        bet_user = str(ctx.author)
        bet_user_id = str(ctx.author.id)
        bet_side = bet_string[0]
        if len(bet_string) > 1:
            bet_amount = float(bet_string[1])
        else:
            bet_amount = 1.0
        user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
        valid_bet = False
        if len(bet_string) < 2:
            bet_amount = 1
        if float(user_balance) >= float(bet_amount) > 0.0:
            valid_bet = True;
            self.bot.get_cog('Currency').remove_user_currency(bet_user_id, bet_amount)
        if valid_bet:
            msg = f'Coin Toss:  {ctx.author} bets {bet_amount} on {bet_side}...'
            message = await ctx.send(msg, delete_after=self.bot.LONG_DELETE_DELAY)
            message_head = message.content.split("...")[0]
            message_head = message_head + "```"
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
                    self.add_gamblestat("Heads", bet_user_id, True, bet_amount)
                    user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                    msg = "**Heads**, {} **Wins** §{}, now has §{:.2f}".format(bet_user, bet_amount, user_balance)
                else:
                    user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                    self.add_gamblestat("Tails", bet_user_id, False, bet_amount)
                    msg = "**Heads**, {} **Loses** §{}, now has §{:.2f}".format(bet_user, bet_amount, user_balance)
            else:
                if bet_side == "!tails":
                    self.bot.get_cog('Currency').add_user_currency(bet_user_id, bet_amount * 2)
                    user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                    self.add_gamblestat("Tails", bet_user_id, True, bet_amount)
                    msg = "**Tails**, {} **Wins** §{}, now has §{:.2f}".format(bet_user, bet_amount, user_balance)
                else:
                    user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                    self.add_gamblestat("Heads", bet_user_id, False, bet_amount)
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
        else:
            msg = f'Coin Toss:  Invalid Bet'
            await ctx.send(msg, delete_after=self.bot.SHORT_DELETE_DELAY)

    async def timeout(self):
        channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        if not self.bot.is_closed():
            self.time_elapsed += TICK_RATE
            if DEBUG:
                await channel.send(f"{self.qualified_name}: {self.time_elapsed}")

def setup(bot):
    bot.add_cog(Gambling(bot))
