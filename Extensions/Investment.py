import json
from datetime import datetime
from json import JSONEncoder
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.dates as mdates

import discord
import random
from discord.ext import tasks, commands

DEBUG = True
TICK_RATE = 6  # Default
emoji_letters_dict = {'A': '🇦', 'B': '🇧', 'C': '🇨', 'D': '🇩', 'E': '🇪', 'F': '🇫', 'G': '🇬', 'H': '🇭', 'I': '🇮',
                      'J': '🇯', 'K': '🇰', 'L': '🇱', 'M': '🇲', 'N': '🇳', 'O': '🇴', 'P': '🇵', 'Q': '🇶', 'R': '🇷',
                      'S': '🇸', 'T': '🇹', 'U': '🇺', 'V': '🇻', 'W': '🇼', 'X': '🇽', 'Y': '🇾', 'Z': '🇿', ' ': '✴'}
company_default_names = ['Hand Job Nails',
                         'Blue Balls Inc',
                         'Fat Constructions',
                         'Umbrella Corp',
                         'Globo Gym',
                         'Aquisitions Inc.',
                         'Soylent Corp',
                         'Globex',
                         'Initech'
                         ]
company_default_tickers = ['HANDJB', 'BLUBLS', 'FATCNT',
                           'UMBREL', 'GLBGYM', 'AQUINC',
                           'SOYLNT', 'GLOBEX', 'INITEC'
                           ]
company_default_volatility = [0.75, 0.75, 0.75,
                              1.0, 1.0, 1.0,
                              1.25, 1.25, 1.25]
company_default_description = ["Low Risk", "Low Risk", "Low Risk",
                               "Medium Risk", "Medium Risk", "Medium Risk",
                               "High Risk", "High Risk",
                               "High Risk"]  # based on the risk factor (0.33 = low, .5 = med, 1.0 = high
company_default_price = [500, 100, 1000,
                         1000, 500, 100,
                         500, 1000, 100]
company_default_colours = ['#FFE4B5', '#4169E1', '#333333',
                           '#FF0000', '#9400D3', '#FFD700',
                           '#32CD32', '#800000', '#008B8B']
BASE_VOLATILITY = 0.025
INVESTMENT_TICKRATE = 6  # 900 = 15 minute update rate


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default


class Investment(commands.Cog):
    def __init__(self, bot):
        self.investment_ticker = INVESTMENT_TICKRATE
        global TICK_RATE
        TICK_RATE = bot.TICK_RATE
        self.bot = bot
        self.company_tickers = []
        self.company_names = []
        self.company_desc = []
        self.company_prices = []
        self.company_volatility = []
        self.price_history = []
        self.all_company_details = []
        self.recent_trades = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.time_elapsed = 0
        # save
        # for i, ticker in enumerate(self.company_tickers):
        #     self.all_company_details.append([self.company_tickers[i], self.company_names[i], self.company_desc[i],
        #                                  self.company_prices[i], self.company_volatility[i], self.price_history[i]])
        # with open(f'{self.qualified_name}_data.json', 'w+') as out_file:
        #     print(json.dump(self.all_company_details, out_file, sort_keys=False, indent=4))
        # load

    def get_investors(self, ticker=""):
        if ticker != "":
            return self.stock_holders[ticker]
        else:
            print("Error, must specify a ticker")
            return False

    def sell_investment(self, user_id="", ticker="", amount=0):
        """ sells investments gives currency to user balance, returns true if sale completed """
        if ticker != "":
            company_index = self.company_tickers.index(ticker)
            if user_id != "":
                if ticker in self.stock_holders:
                    if user_id in self.stock_holders[ticker]:
                        if self.stock_holders[ticker][user_id] >= amount:
                            self.stock_holders[ticker][user_id] -= amount
                            currency_earned = self.company_prices[company_index] * amount
                            self.bot.get_cog('Currency').add_user_currency(user_id, currency_earned)
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
        """ Buys investment, removes currency from user balance, returns true if purchase completed """
        if ticker != "":
            if user_id != "":
                if ticker in self.stock_holders:  # is it a valid ticker
                    if user_id in self.stock_holders[ticker]:
                        current_stock = self.stock_holders[ticker][user_id]
                    else:
                        current_stock = 0
                    user_balance = self.bot.get_cog('Currency').get_user_currency(user_id)
                    self.stock_holders[ticker][user_id] = current_stock + amount
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
                for i, detail in enumerate(data):
                    self.company_tickers.append(detail[0])
                    self.company_names.append(detail[1])
                    self.company_desc.append(detail[2])
                    self.company_prices.append(detail[3])
                    self.company_volatility.append(detail[4])
                    self.price_history.append(detail[5])  # set up a history of 10
                    self.all_company_details.append(
                        [self.company_tickers[i], self.company_names[i], self.company_desc[i],
                         self.company_prices[i], self.price_history[i]])
                print(f"Loaded {len(self.all_company_details)} Companies.")
        except FileNotFoundError:  # file doesn't exist, init all members with 0 currency to avoid index errors
            for i, ticker in enumerate(company_default_tickers):
                print(i, ticker)
                self.company_tickers.append(company_default_tickers[i])
                self.company_names.append(company_default_names[i])
                self.company_desc.append(company_default_description[i])
                self.company_prices.append(company_default_price[i])
                self.company_volatility.append(company_default_volatility[i])
                self.price_history.append([company_default_price[i] for j in range(10)])  # set up a history of 10
            await self.save_data()

    async def save_data(self):
        self.all_company_details = []
        for i, ticker in enumerate(self.company_tickers):
            self.all_company_details.append([self.company_tickers[i], self.company_names[i], self.company_desc[i],
                                             self.company_prices[i], self.company_volatility[i],
                                             self.price_history[i]])
        with open(f'{self.qualified_name}_data.json', 'w+') as out_file:
            print(json.dump(self.all_company_details, out_file, sort_keys=False, indent=4))

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
        if not self.bot.is_closed() and len(self.company_tickers) > 0:
            if self.investment_ticker >= INVESTMENT_TICKRATE:
                for i, company in enumerate(self.company_tickers):
                    if DEBUG:
                        print(company)
                    previous_price = self.company_prices[i]
                    company_volatility = self.company_volatility[i]
                    current_momentum = 0
                    if DEBUG:
                        print("HISTORY:: ", end=" ")
                    for j in range(len(self.price_history[i]) - 8, len(self.price_history[i])):
                        current_momentum += self.price_history[i][j] / self.price_history[i][j - 1]
                        if DEBUG:
                            print(f"{self.price_history[i][j]:.2f}", end=",")
                    current_momentum = round(current_momentum / 8, 5) - 1
                    if self.recent_trades[i] != 0:
                        if current_momentum < 0:
                            current_momentum = round(current_momentum / 8, 5) + self.recent_trades[i] - 1
                        else:
                            current_momentum = round(current_momentum / 8, 5) - self.recent_trades[i] - 1

                    random_fluctuation = round(random.uniform(-BASE_VOLATILITY, BASE_VOLATILITY), 5)
                    total_change = max(min(current_momentum / 2, BASE_VOLATILITY), -BASE_VOLATILITY) + max(
                        min(random_fluctuation, BASE_VOLATILITY), -BASE_VOLATILITY)
                    next_price = round(previous_price * (1 + total_change), 5)
                    print("total_change ", total_change, " random ", random_fluctuation, " momentum ", current_momentum)
                    if DEBUG:
                        print(f"Momentum {current_momentum:.3f}, Total_Change = {random_fluctuation:.5f}")
                        print(previous_price, " -> ", next_price)
                    self.company_prices[i] = max(next_price, 1)
                    self.price_history[i].append(previous_price)
                if self.time_elapsed % 60 == 0:
                    # 8 hour 3x3 plot
                    if len(self.price_history[-1]) > 24:  # ensure we have enough price history
                        my_timeperiods = [dt.datetime.now() - (dt.timedelta(minutes=15 * i)) for i in range(24, 0, -1)]
                        stock = []
                        leg = []
                        print(1)
                        for i, history in enumerate(self.price_history):
                            stock.append(self.price_history[i][-24:])
                            leg.append(self.company_tickers[i][-24:])
                        # my_series = pd.Series(self.price_history[-1], index=my_timeperiods)
                        # my_series_two = pd.Series(self.price_history[-4], index=my_timeperiods)
                        # frame = {self.company_names[-1]: my_series,self.company_names[-4]: my_series_two}
                        date_format = mdates.DateFormatter('%a %H:%M')
                        fig, ax = plt.subplots(3, 3, sharex=True, squeeze=False)
                        print(2)
                        for x in range(3):
                            for y in range(3):
                                index = y * 3 + x
                                ax[x, y].plot(my_timeperiods, stock[index], color=company_default_colours[index],
                                              label=leg[index])
                                ax[x, y].xaxis.set_major_formatter(date_format)
                                ax[x, y].tick_params(axis='both', which='major', labelsize=8)
                                ax[x, y].legend(loc="best")
                        fig.autofmt_xdate()
                        print(3)
                        fig.suptitle("All Stock Values, Last 8 hours", fontsize=12, y=1)
                        plt.figure(num=None, figsize=(40, 20))
                        fig = ax.flatten()[0].figure
                        s = fig.subplotpars
                        w, h = fig.get_size_inches()
                        figh = h - (1 - s.top) * h + 1
                        fig.subplots_adjust(bottom=s.bottom * h / figh, top=1 / figh)
                        fig.set_figheight(figh)
                        plt.show()
                        plt.savefig('8hour.png')
                        print(4)
                self.investment_ticker = 0
            self.time_elapsed += self.bot.TICK_RATE
            self.investment_ticker += self.bot.TICK_RATE


def setup(bot):
    bot.add_cog(Investment(bot))
