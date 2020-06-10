import json
from datetime import datetime
from json import JSONEncoder
from operator import itemgetter

import discord
import random
from discord.ext import tasks, commands

DEBUG = False
TICK_RATE = 6  # Default
emoji_letters_dict = {'A': '🇦', 'B': '🇧', 'C': '🇨', 'D': '🇩', 'E': '🇪', 'F': '🇫', 'G': '🇬', 'H': '🇭', 'I': '🇮',
                      'J': '🇯', 'K': '🇰', 'L': '🇱', 'M': '🇲', 'N': '🇳', 'O': '🇴', 'P': '🇵', 'Q': '🇶', 'R': '🇷',
                      'S': '🇸', 'T': '🇹', 'U': '🇺', 'V': '🇻', 'W': '🇼', 'X': '🇽', 'Y': '🇾', 'Z': '🇿', ' ': '✴'}


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default


class Investment(commands.Cog):
    def __init__(self, bot):
        global TICK_RATE
        TICK_RATE = bot.TICK_RATE
        self.bot = bot
        self.member_currency = {}
        # Bonuses - Note: Cumulative - ie 1+0.5+4 = 5;0.5*IDLE_RATE
        self.IDLE_RATE = 6 / 60 / 60 * TICK_RATE  # (1 per hour)
        self.VOICE_BONUS = 0.5  # (100% while in a voice channel)
        self.ACTIVITY_BONUS = 0.5  # (50% while active)
        self.HAPPY_HOUR_BONUS = 4  # (400% during happy hour)
        self.time_elapsed = 0

    def get_user_investments(self, user_id=""):
        if user_id != "":
            return self.member_currency[user_id]
        else:
            print("Error, must specify a user_id")
            return False

    def remove_user_investment(self, user_id="", amount=0):
        # Removes currency from user balance, returns true if user has sufficient balance
        if user_id != "":
            if self.member_currency[user_id] >= amount:
                self.member_currency[user_id] -= amount
                return True
            else:
                return False
        else:
            print("Error, must specify a user_id")
            return False

    def add_user_investment(self, user_id="", amount=0):
        # adds currency from user balance, returns true if user has sufficient balance
        if user_id != "":
            if amount > 0:
                self.member_currency[user_id] += amount
                return True
            else:
                return False
        else:
            print("Error, must specify a user_id")
            return False

    async def load_data(self):
        try:
            with open(f'{self.qualified_name}_data.json', 'r+') as in_file:
                data = json.load(in_file)
                self.time_elapsed = data['uptime']
                self.member_currency = data['member_currency']
                print(f"Loaded {len(data['member_currency'])} Members Currency Data.")
        except FileNotFoundError:  # file doesn't exist, init all members with 0 currency to avoid index errors
            for member in self.bot.get_all_members():
                self.member_currency[str(member.id)] = 0

    async def save_data(self):
        if len(self.member_currency) > 0:
            save_data = {'uptime': self.time_elapsed,
                         'member_currency': self.member_currency}
            with open(f'{self.qualified_name}_data.json', 'w+') as out_file:
                json.dump(save_data, out_file, sort_keys=False, indent=4)

    @commands.command(name="mycurrency", aliases=["my$", "my $", "my$hekels", "user$", "user $"])
    async def mycurrency(self, ctx, *, member: discord.Member = None):
        """!my$ or user$ [user]"""
        member = member or ctx.author
        currency = self.member_currency[str(member.id)]
        currency_name = self.bot.CURRENCY_NAME if 2 > currency >= 1 else self.bot.CURRENCY_NAME + 's'
        msg = f"{member.mention} has {currency:.2f} {currency_name}"
        log = await self.bot.get_channel(self.bot.LOG_CHANNEL).send(msg)
        await ctx.send(msg, delete_after=self.bot.MEDIUM_DELETE_DELAY)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    async def timeout(self):
        debug_channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        log_channel = self.bot.get_channel(self.bot.LOG_CHANNEL)
        if not self.bot.is_closed() and len(self.member_currency) > 0:
            for member in self.bot.get_all_members():
                if str(member.id) not in self.member_currency.keys():
                    print("New Member:", member)
                    self.member_currency[str(member.id)] = 0.0
                    current_member_currency = 0.0
                else:
                    current_member_currency = self.member_currency[str(member.id)]
                # Apply Activity Bonuses to encourage member participation
                cumulative_activity_bonus = 1
                if member.activity is not None:
                    cumulative_activity_bonus += self.ACTIVITY_BONUS
                if member.voice is not None:
                    cumulative_activity_bonus += self.VOICE_BONUS

                # Apply Happy Hour Bonus, 6pm-midnight on weekdays, all hours on Saturday/Sunday
                weekday = datetime.today().weekday()
                hour = datetime.today().hour + datetime.today().minute / 60
                if weekday >= 5:
                    cumulative_activity_bonus += self.HAPPY_HOUR_BONUS
                else:
                    if 18 <= hour < 24:
                        cumulative_activity_bonus += self.HAPPY_HOUR_BONUS
                current_member_currency += self.IDLE_RATE * cumulative_activity_bonus
                self.member_currency[str(member.id)] = current_member_currency
                if DEBUG:
                    print(member.id, member, self.member_currency[str(member.id)], sep=",")
            self.time_elapsed += TICK_RATE


def setup(bot):
    bot.add_cog(Investment(bot))