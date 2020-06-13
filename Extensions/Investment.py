import json
from json import JSONEncoder
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates

import discord
import random
from discord.ext import tasks, commands

DEBUG = True
DEBUG_TICKER = False
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
company_default_description = ["Low Risk", "Low Risk", "Low Risk",  # based on the risk factor
                               "Medium Risk", "Medium Risk", "Medium Risk",  # (0.33 = low, .5 = med, 1.0 = high )
                               "High Risk", "High Risk", "High Risk"]
company_default_price = [500, 100, 1000,
                         1000, 500, 100,
                         500, 1000, 100]
company_default_colours = ['#FFE4B5', '#4169E1', '#333333',
                           '#FF0000', '#9400D3', '#FFD700',
                           '#32CD32', '#800000', '#008B8B']
BASE_VOLATILITY = 0.025
INVESTMENT_TICKRATE = 60  # 900 = 15 minute update rate


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
        self.stock_holdings = {}
        self.recent_trades = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.time_elapsed = 0
        # save
        # for i, ticker in enumerate(self.company_tickers):
        #     self.all_company_details.append([self.company_tickers[i], self.company_names[i], self.company_desc[i],
        #                                  self.company_prices[i], self.company_volatility[i], self.price_history[i]])
        # with open(f'{self.qualified_name}_data.json', 'w+') as out_file:
        #     print(json.dump(self.all_company_details, out_file, sort_keys=False, indent=4))
        # load

    def get_investments(self, user_id=""):
        if user_id != "":
            return self.stock_holdings[user_id]
        else:
            print("Error, must specify a user_id")
            return False

    def sell_investment(self, user_id="", ticker="", amount=0):
        """ sells investments gives currency to user balance, returns true if sale completed """
        try:
            if DEBUG: print(f"{user_id} selling {amount} of {ticker}")
            if ticker != "":
                if user_id != "":
                    print(self.stock_holdings, user_id)
                    if user_id in self.stock_holdings:
                        if ticker in self.stock_holdings[user_id]:
                            current_stock = self.stock_holdings[user_id][ticker]
                            if current_stock >= amount:
                                current_stock_price = self.company_prices[self.company_tickers.index(ticker)]
                                price = amount * current_stock_price
                                self.stock_holdings[user_id][ticker] = current_stock - amount
                                self.bot.get_cog('Currency').add_user_currency(user_id, price)
                                return f"Sale Complete```SOLD: {amount} {ticker} for {price:.2f}\n" \
                                       f"You now hold {current_stock - amount} worth {(current_stock - amount) * current_stock_price:.2f}```"
                            else:
                                return f"Not enough {ticker}"
                        else:
                            return f"You don't have any {ticker}"
                    else:
                        return f"{ticker} doesn't Exist."
                else:
                    print("Error, must specify a user_id.")
                    return False
            else:
                print("Error, must specify a ticker.")
                return False
        except ValueError:
            return f"{ticker} doesn't Exist."

    def buy_investment(self, user_id="", ticker="", amount=0):
        """ Buys investment, removes currency from user balance, returns true if purchase completed """
        if DEBUG: print(f"{user_id} buying {amount} of {ticker}")
        try:
            if ticker != "":
                if user_id != "":
                    print(self.stock_holdings)
                    current_stock = 0
                    if user_id in self.stock_holdings:
                        if ticker in self.stock_holdings[user_id]:
                            current_stock = self.stock_holdings[user_id][ticker]
                    else:
                        self.stock_holdings[user_id] = {}
                    user_balance = self.bot.get_cog('Currency').get_user_currency(user_id)
                    current_stock_price = self.company_prices[self.company_tickers.index(ticker)]
                    price = amount * current_stock_price
                    if user_balance >= price:
                        self.bot.get_cog('Currency').remove_user_currency(user_id, price)
                        self.stock_holdings[user_id][ticker] = current_stock + amount
                        return f"Purchase Completed```BROUGHT: {amount} of {ticker} for {price:.2f} ({current_stock_price:.2f} ea)\n" \
                               f"You now hold {amount + current_stock} {ticker} worth {(amount + current_stock) * current_stock_price:.2f}```"
                    else:
                        return f"You don't have enough, you need {price:.2f} but have {user_balance:.2f}"

                else:
                    print("Error, must specify a user_id.")
                    return False
            else:
                print("Error, must specify a ticker.")
                return False
        except ValueError:
            return f"{ticker} doesn't Exist."

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
            with open(f'{self.qualified_name}_users.json', 'r+') as in_file:
                user = json.load(in_file)
                self.stock_holdings = user
                print(f"Loaded {len(self.stock_holdings)} Users Stock Holdings.")
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
        with open(f'{self.qualified_name}_users.json', 'w+') as out_file:
            print(json.dump(self.stock_holdings, out_file, sort_keys=False, indent=4))

    @commands.command(name="buy investments", aliases=["buy"])
    async def buy(self, ctx, ticker: str, amount: int):
        """!buy"""
        user_id = str(ctx.author.id)
        ticker = str(ticker).upper()
        amount = abs(amount)
        outcome = self.buy_investment(user_id=user_id, ticker=ticker, amount=amount)
        await ctx.channel.send(outcome, delete_after=self.bot.MEDIUM_DELETE_DELAY)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    @commands.command(name="sell investments", aliases=["sell"])
    async def sell(self, ctx, ticker: str, amount: int):
        """!sell"""
        user_id = str(ctx.author.id)
        ticker = str(ticker).upper()
        amount = abs(amount)
        outcome = self.sell_investment(user_id=user_id, ticker=ticker, amount=amount)
        await ctx.channel.send(outcome, delete_after=self.bot.MEDIUM_DELETE_DELAY)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    @commands.command(name="price check", aliases=["pc", "week", "day", "stocks", "stocklist"])
    async def check(self, ctx, chart: str):
        """chart prices"""
        if chart.startswith("day") or chart.startswith("8"):
            await ctx.channel.send(file=discord.File('8hours.png'), delete_after=self.bot.MEDIUM_DELETE_DELAY)
        elif chart.startswith("week") or chart.startswith("7"):
            await ctx.channel.send(file=discord.File('7days.png'), delete_after=self.bot.MEDIUM_DELETE_DELAY)
        else:
            msg = "Company Details:```"
            msg += f"{'Name':<30} | {'Desc':<15} | {'Price':<20}\n"
            msg += f"-----------------------------------------------------------------\n"
            for i, stock in enumerate(self.company_names):
                msg += f"{self.company_names[i] + ' (' + self.company_tickers[i] + ')':<30} | {self.company_desc[i]:<15} | {self.company_prices[i]:<20.2f}\n"
            msg += "```"
            await ctx.channel.send(msg, delete_after=self.bot.MEDIUM_DELETE_DELAY)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    @commands.command(name="investments", aliases=["myinv", "my inv", "myinvestments", "userinv", "user inv"])
    async def investments(self, ctx, *, member: discord.Member = None):
        """!myinv or userinv [user]"""
        user_id = str(ctx.author.id)
        if member != None:
            user_id = str(member.id)
        investments = self.get_investments(user_id=user_id)
        msg = "Current Investments:```"
        msg += f"{'Investment':<20} | {'Holding':<10} | {'Value':<15}\n"
        msg += "---------------------------------------------------\n"
        for investment in investments.keys():
            msg += f"{investment:<20} | {investments[investment]:<10} | {self.company_prices[self.company_tickers.index(investment)] * investments[investment]:<15.2f}\n"
        msg += '```'
        await ctx.channel.send(msg, delete_after=self.bot.MEDIUM_DELETE_DELAY)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    async def timeout(self):
        debug_channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        log_channel = self.bot.get_channel(self.bot.LOG_CHANNEL)
        if not self.bot.is_closed() and len(self.company_tickers) > 0:
            if self.investment_ticker >= INVESTMENT_TICKRATE:
                for i, company in enumerate(self.company_tickers):
                    if DEBUG_TICKER:
                        print(company)
                    previous_price = self.company_prices[i]
                    company_volatility = self.company_volatility[i]
                    current_momentum = 0
                    if DEBUG_TICKER:
                        print("HISTORY:: ", end=" ")
                    for j in range(len(self.price_history[i]) - 8, len(self.price_history[i])):
                        current_momentum += self.price_history[i][j] / self.price_history[i][j - 1]
                        if DEBUG_TICKER:
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
                    if DEBUG_TICKER:
                        print("total_change ", total_change, " random ", random_fluctuation, " momentum ",
                              current_momentum)
                        print(f"Momentum {current_momentum:.3f}, Total_Change = {random_fluctuation:.5f}")
                        print(previous_price, " -> ", next_price)
                    self.company_prices[i] = max(next_price, 1)
                    self.price_history[i].append(previous_price)
                    if len(self.price_history[i]) > 700:
                        self.price_history[i] = self.price_history[i][-700:]
                # 7 days 3x3 plot
                if len(self.price_history[-1]) > 672:  # ensure we have enough price history
                    my_timeperiods = [dt.datetime.now() - (dt.timedelta(minutes=15 * i)) for i in range(672, 0, -1)]
                    stock = []
                    leg = []
                    for i, history in enumerate(self.price_history):
                        stock.append(self.price_history[i][-672:])
                        leg.append(self.company_tickers[i][-672:])
                    date_format = mdates.DateFormatter('%a %d/%m/%y')
                    fig, ax = plt.subplots(3, 3, sharex=True, squeeze=False)
                    for x in range(3):
                        for y in range(3):
                            index = y * 3 + x
                            ax[x, y].plot(my_timeperiods, stock[index], color=company_default_colours[index],
                                          label=leg[index])
                            ax[x, y].xaxis.set_major_formatter(date_format)
                            ax[x, y].tick_params(axis='both', which='major', labelsize=6)
                            ax[x, y].legend(loc="best")
                    fig.autofmt_xdate()
                    fig.suptitle("All Stock Values, Last 7 days", fontsize=12, y=.95)
                    plt.draw()
                    plt.savefig('7days.png')
                    # plt.show()
                    print("Updated 7 day chart")
                # 8 hours 3x3 plot
                if len(self.price_history[-1]) > 24:  # ensure we have enough price history
                    my_timeperiods = [dt.datetime.now() - (dt.timedelta(minutes=15 * i)) for i in range(24, 0, -1)]
                    stock = []
                    leg = []
                    for i, history in enumerate(self.price_history):
                        stock.append(self.price_history[i][-24:])
                        leg.append(self.company_tickers[i][-24:])
                    date_format = mdates.DateFormatter('%a %H:%M')
                    fig, ax = plt.subplots(3, 3, sharex=True, squeeze=False)
                    for x in range(3):
                        for y in range(3):
                            index = y * 3 + x
                            ax[x, y].plot(my_timeperiods, stock[index], color=company_default_colours[index],
                                          label=leg[index])
                            ax[x, y].xaxis.set_major_formatter(date_format)
                            ax[x, y].tick_params(axis='both', which='major', labelsize=8)
                            ax[x, y].legend(loc="best")
                    fig.autofmt_xdate()
                    fig.suptitle("All Stock Values, Last 8 hours", fontsize=12, y=.95)
                    plt.draw()
                    plt.savefig('8hours.png')
                    # plt.show()
                    print("Updated 8 hour chart")
                await self.save_data()
                self.investment_ticker = 0
            self.time_elapsed += self.bot.TICK_RATE
            self.investment_ticker += self.bot.TICK_RATE


def setup(bot):
    bot.add_cog(Investment(bot))
