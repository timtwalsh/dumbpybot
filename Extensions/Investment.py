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
company_names = ['Hand Job Nails', 'Blue Balls Inc', 'Fat Constructions', 'Umbrella Corp', 'Globo Gym',
                 'Aquisitions Inc.', 'Soylent Corp', 'Globex', 'Initech']
company_tickers = ['HANDJB', 'BLUBLS', 'FATCNT', 'UMBREL', 'GLBGYM', 'AQUINC' 'SOYLNT', 'GLOBEX', 'INTEC']
company_volatility = [0.33, 0.33, 0.33, 0.5, 0.5, 0.5, 1, 1, 1]
company_price = [500, 100, 1000, 1000, 500, 100, 500, 1000, 100]
company_description = ["Low Risk", "Low Risk", "Low Risk", "Medium Risk", "Medium Risk", "Medium Risk", "High Risk",
                       "High Risk", "High Risk"]
base_volatility = 0.025


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default


class Investment(commands.Cog):
    def __init__(self, bot):
        global TICK_RATE
        TICK_RATE = bot.TICK_RATE
        self.bot = bot
        for ticker in company_tickers:
            self.stock_holders[ticker] = []
        self.time_elapsed = 0

    def get_investors(self, ticker=""):
        if ticker != "":
            return self.stock_holders[ticker]
        else:
            print("Error, must specify a ticker")
            return False

    def sell_investment(self, user_id="", ticker="", amount=0):
        """ sells investments gives currency to user balance, returns true if user has sufficient investment """
        if ticker != "":
            if user_id != "":
                if ticker in self.stock_holders:
                    if user_id in self.stock_holders[ticker]:
                        if self.stock_holders[ticker][user_id] >= amount:
                            self.stock_holders[user_id] -= amount
                            return True
                        else:
                            print(f"{user_id} doesn't have {amount} {ticker}.")
                            return False
            else:
                print("Error, must specify a user_id.")
                return False
        else:
            print("Error, must specify a ticker.")
            return False

    def buy_investment(self, user_id="", ticker="", amount=0):
        """ Buys investment, removes currency from user balance, returns true if user has sufficient balance"""
        if ticker != "":
            if user_id != "":
                if ticker in self.stock_holders:  # is it a valid ticker
                    if user_id in self.stock_holders[ticker]:
                        current_stock = self.stock_holders[ticker][user_id]
                    else:
                        current_stock = 0
                    user_balance = self.bot.get_cog('Currency').get_user_currency(user_id)
                    self.stock_holders[ticker][user_id] = 1
            else:
                print("Error, must specify a user_id.")
                return False
        else:
            print("Error, must specify a ticker.")
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

    @commands.command(name="investments", aliases=["myinv", "my inv", "myinvestments", "userinv", "user inv"])
    async def investments(self, ctx, *, member: discord.Member = None):
        """!myinv or userinv [user]"""
        member = member or ctx.author
        # currency = self.member_currency[str(member.id)]
        # currency_name = self.bot.CURRENCY_NAME if 2 > currency >= 1 else self.bot.CURRENCY_NAME + 's'
        # msg = f"{member.mention} has {currency:.2f} {currency_name}"
        # log = await self.bot.get_channel(self.bot.LOG_CHANNEL).send(msg)
        # await ctx.send(msg, delete_after=self.bot.MEDIUM_DELETE_DELAY)
        # await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    async def timeout(self):
        debug_channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        log_channel = self.bot.get_channel(self.bot.LOG_CHANNEL)
        if not self.bot.is_closed() and len(self.member_currency) > 0:
            self.time_elapsed += TICK_RATE


def setup(bot):
    bot.add_cog(Investment(bot))
