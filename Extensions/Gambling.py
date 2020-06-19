import asyncio
import json
from collections import defaultdict

import discord
import random
from discord.ext import commands

DEBUG = False
TICK_RATE = 6  # Default
LETTERS_TO_EMOJI_ASCII = {'A': '🇦', 'B': '🇧', 'C': '🇨', 'D': '🇩', 'E': '🇪', 'F': '🇫', 'G': '🇬', 'H': '🇭',
                          'I': '🇮',
                          'J': '🇯', 'K': '🇰', 'L': '🇱', 'M': '🇲', 'N': '🇳', 'O': '🇴', 'P': '🇵', 'Q': '🇶',
                          'R': '🇷',
                          'S': '🇸', 'T': '🇹', 'U': '🇺', 'V': '🇻', 'W': '🇼', 'X': '🇽', 'Y': '🇾', 'Z': '🇿',
                          ' ': '✴'}


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
        self.deathroll_users = []
        self.deathroll_status = ''
        self.deathroll_minimum = 100.0
        self.DEATHROLL_WAIT_TIME = 15
        self.DEATHROLL_MIN_PLAYERS = 2
        self.deathroll_max = 0
        self.deathroll_user_ids = []
        self.deathroll_ready = False
        self.deathroll_current_player = ''

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

    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            if message.content.lower().startswith("deathroll: "):
                roll_position = self.deathroll_buyin
                wait_time = self.DEATHROLL_WAIT_TIME
                user_count = 0
                for second in range(wait_time * 2, 0, -5):
                    user_count = len(self.deathroll_users)
                    self.deathroll_status = f'Deathroll: REQUESTED: ({self.deathroll_buyin:.0f} buy-in, (+1 User = ${(user_count + 1) * (self.deathroll_buyin * (1 + min(min(max(0, len(self.deathroll_users) - 1), 4) * .2, 0.5))):.0f} pot)): '
                    msg = self.deathroll_status + f'{user_count}/{self.DEATHROLL_MIN_PLAYERS} Users are Interested ... {second} seconds to go' + f'```Type !deathroll to participate.\n{self.deathroll_users}```'
                    await message.edit(content=msg)
                    await asyncio.sleep(5)
                user_count = len(self.deathroll_users)
                if user_count >= self.DEATHROLL_MIN_PLAYERS:
                    deathroll_total = self.deathroll_buyin * user_count + self.deathroll_buyin * user_count * (
                        +min(min(max(0, user_count - 2), 4) * .2, 0.5))
                    self.deathroll_status = f"Deathrolling for {deathroll_total:.0f} ({self.deathroll_buyin} buy-in): ```"
                    self.deathroll_max = self.deathroll_buyin
                    while len(self.deathroll_users) > 1:
                        print(self.deathroll_users)
                        user_index = 0
                        while user_index < len(self.deathroll_users) and len(self.deathroll_users) > 1:
                            self.deathroll_current_player = self.deathroll_users[user_index]
                            for second in range(wait_time, -1, -1):
                                if self.deathroll_ready or second <= 0:
                                    roll = random.randint(1, self.deathroll_max)
                                    self.deathroll_status = self.deathroll_status + f"{self.deathroll_users[user_index]}'s rolls 1-{self.deathroll_max:.0f}... drops a {roll:.0f} \n"
                                    await message.channel.send(
                                        f"{self.deathroll_users[user_index]}'s rolls 1-{self.deathroll_max:.0f}... drops a {roll:.0f}",
                                        delete_after=10.0)
                                    if roll == 1:
                                        self.deathroll_status = self.deathroll_status + f"{self.deathroll_users[user_index]} is out!\n"
                                        print("del", self.deathroll_user_ids[user_index])
                                        del self.deathroll_user_ids[user_index]
                                        print("Remove", self.deathroll_users[user_index])
                                        self.deathroll_users.remove(self.deathroll_users[user_index])
                                        print(self.deathroll_users, self.deathroll_user_ids)
                                    else:
                                        self.deathroll_max = roll
                                        user_index += 1
                                    msg = self.deathroll_status + '```'
                                    self.deathroll_ready = False
                                    break
                                else:
                                    msg = self.deathroll_status + f"{self.deathroll_users[user_index]}'s turn... {second} seconds till auto-roll." + '```'
                                await message.edit(content=msg)
                                await asyncio.sleep(1)
                    self.deathroll_status = self.deathroll_status + f"{self.deathroll_users[0]} is the last survivor, takes the pot {deathroll_total}\n"
                    msg = self.deathroll_status + '```'
                    await message.edit(content=msg)
                    log = await self.bot.get_channel(self.bot.LOG_CHANNEL).send(msg)
                    await asyncio.sleep(3)
                    winner = "```\n ________________________________________\n" \
                             "/ {:^38} \\\n\________________________________________/\n      " \
                             "        ...        /\n             ;::::;    " \
                             " /\n           ;::::; :;   /\n         " \
                             ";:::::'   :; /\n        ;:::::;     ;/\n     " \
                             "  ,:::::'      /;           OOO\n       " \
                             "::::::;     / ;          OOOOO\n       " \
                             ";:::::;       ;         OOOOOOOO\n      ," \
                             ";::::::;     ;'         / OOOOOOO\n    " \
                             ";:::::::::`. ,,,;.        /  / DOOOOOO\n  " \
                             ".';:::::::::::::::::;,     /  /     DOOOO\n " \
                             ",::::::;::::::;;;;::::;,   /  /        " \
                             "DOOO\n;`::::::`'::::::;;;::::: ,#/  /        " \
                             "  DOOO\n:`:::::::`;::::::;;::: ;::#  /       " \
                             "     DOOO\n::`:::::::`;:::::::: ;::::# /     " \
                             "         DOO\n`:`:::::::`;:::::: ;::::::#/   " \
                             "            DOO\n :::`:::::::`;; " \
                             ";:::::::::##                OO\n " \
                             "::::`:::::::`;::::::::;:::#                " \
                             "OO\n `:::::`::::::::::::;'`:;::#             " \
                             "   O\n  `:::::`::::::::;' /  / `:#\n   " \
                             "::::::`:::::;'  /  /   `#```".format(
                        self.deathroll_users[0] + ' wins this round...')
                    self.bot.get_cog('Currency').add_user_currency(self.deathroll_user_ids[0], deathroll_total)
                    msg = self.deathroll_status + '```'
                    # self.add_gamblestat("Deathroll", self.deathroll_user_ids[0], True, deathroll_total)
                    await message.channel.send(winner, delete_after=60)
                    self.deathroll_status = ''
                    self.deathroll_users = []
                    self.deathroll_user_ids = []
                    self.deathroll_current_player = ''
                else:
                    await message.edit(content="Deathroll: CANCELLED: Only {} users joined. ".format(
                        user_count) + "Requires {} users to start.".format(self.DEATHROLL_MIN_PLAYERS))
                    for user in self.deathroll_user_ids:
                        self.bot.get_cog('Currency').add_user_currency(user, self.deathroll_buyin)
                    self.deathroll_buyin = 0
                    self.deathroll_status = ''
                    self.deathroll_users = []
                    self.deathroll_user_ids = []

    @commands.command(aliases=["mybets", "mygambles", "my_gamble_stats"])
    async def usergamblestats(self, ctx):
        """!mybets or !mygambles"""
        print(self.user_gambling_stats)
        msg = f'{ctx.author} Gambling Stats```'
        for bet in self.user_gambling_stats[str(ctx.author.id)]:
            msg += f'\n{bet}: {self.user_gambling_stats[str(ctx.author.id)][bet][0]:>3} Wins, {self.user_gambling_stats[str(ctx.author.id)][bet][2]:>3} losses. Net Outcome: {self.user_gambling_stats[str(ctx.author.id)][bet][1] - self.user_gambling_stats[str(ctx.author.id)][bet][3]:>12.2f}'
        msg += '```'
        message = await ctx.send(msg, delete_after=self.bot.LONG_DELETE_DELAY)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    @commands.command(aliases=["allgambles", "all_gamble_stats"])
    async def gamblestats(self, ctx):
        """!gamblestats or !allgambles"""
        print(self.user_gambling_stats)
        msg = f'{ctx.guild.name} Gambling Stats \n'
        for gamble in self.gambling_history.keys():
            msg += f'{gamble}: {self.gambling_history[gamble]}\n'
        message = await ctx.send(msg, delete_after=self.bot.LONG_DELETE_DELAY)

    @commands.command(aliases=["dr", "Dr", "DR"])
    async def deathroll(self, ctx):
        """!Deathroll [amt] or !dr [amt]"""
        bet_string = ctx.message.content.split(' ')
        bet_user = str(ctx.author)
        bet_user_id = str(ctx.author.id)
        bet_side = bet_string[0]
        print(bet_user_id, self.deathroll_user_ids)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)
        if self.deathroll_status == "" or (
                self.deathroll_status.startswith('Deathroll') and bet_user_id in self.deathroll_user_ids):
            if bet_user_id in self.deathroll_user_ids:
                if bet_user == self.deathroll_current_player:
                    self.deathroll_ready = True  # skip the afk timer
                else:
                    await ctx.channel.send("Wait your Turn!", delete_after=5.0)
            else:
                bet_amount = self.deathroll_minimum
                if self.deathroll_status != '':
                    bet_amount = self.deathroll_buyin
                else:
                    try:
                        bet_amount = max(self.deathroll_minimum, float(bet_string[1]))
                    except IndexError:
                        bet_amount = self.deathroll_minimum
                    self.deathroll_buyin = bet_amount
                user_balance = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                valid_bet = False
                if float(user_balance) >= float(bet_amount):
                    if float(bet_amount) >= self.deathroll_minimum:
                        valid_bet = True
                        self.bot.get_cog('Currency').remove_user_currency(bet_user_id, bet_amount)
                    else:
                        valid_bet = False
                        msg = f'Deathroll: Invalid - Deathrolling only allowed above {self.deathroll_minimum}'
                        await ctx.send(msg, delete_after=self.bot.SHORT_DELETE_DELAY)
                else:
                    valid_bet = False
                    bet_amount = max(self.deathroll_minimum, self.deathroll_buyin)
                    msg = f'Deathroll: Invalid - You need to have {bet_amount} to join.'
                    await ctx.send(msg, delete_after=10)
                if valid_bet:  # User placed a valid bet/has enough currency.
                    """!deathroll - Starts a deathroll Request"""
                    if self.deathroll_status == '':
                        msg = f'Deathroll: REQUESTED: ({bet_amount:.0f} buy-in, (+1 User = ${bet_amount * (1 + min(min(max(0, len(self.deathroll_users) - 1), 4) * .2, 0.5)):.0f} pot)): '
                        self.deathroll_status = msg
                        self.deathroll_users.append(str(ctx.author))
                        self.deathroll_user_ids.append(str(ctx.author.id))
                        await ctx.channel.send(msg)
                    elif self.deathroll_status.startswith('Deathroll: REQUESTED: '):
                        if not str(ctx.author) in self.deathroll_users:
                            self.deathroll_users.append(str(ctx.author))
                            self.deathroll_user_ids.append(str(ctx.author.id))
                            await ctx.channel.send(f"{bet_user} is joining the Deathroll!", delete_after=10.0)
        else:
            await ctx.channel.send(f"Deathroll already in progress.", delete_after=10.0)

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
            valid_bet = True
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
            msg = f'Coin Toss: Not Enough Currency.'
            await ctx.send(msg, delete_after=self.bot.SHORT_DELETE_DELAY)

    async def timeout(self):
        channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        if not self.bot.is_closed():
            self.time_elapsed += TICK_RATE
            if DEBUG:
                await channel.send(f"{self.qualified_name}: {self.time_elapsed}")

def setup(bot):
    bot.add_cog(Gambling(bot))
