import json
from datetime import datetime
from operator import itemgetter
from collections import defaultdict
import discord
import random
from discord.ext import tasks, commands

DEBUG = False
TICK_RATE = 6  # Default
emoji_letters_dict = {'A': '🇦', 'B': '🇧', 'C': '🇨', 'D': '🇩', 'E': '🇪', 'F': '🇫', 'G': '🇬', 'H': '🇭', 'I': '🇮',
                      'J': '🇯', 'K': '🇰', 'L': '🇱', 'M': '🇲', 'N': '🇳', 'O': '🇴', 'P': '🇵', 'Q': '🇶', 'R': '🇷',
                      'S': '🇸', 'T': '🇹', 'U': '🇺', 'V': '🇻', 'W': '🇼', 'X': '🇽', 'Y': '🇾', 'Z': '🇿', ' ': '✴'}


class ActivityStats(commands.Cog):
    def __init__(self, bot):
        global TICK_RATE
        TICK_RATE = bot.TICK_RATE
        self.bot = bot
        self.activities = {}
        self.user_activities = {}
        # Bonuses are cumulative - ie 1+0.5+4 = 3.5*IDLE_RATE
        self.IDLE_RATE = 1 / 60 * TICK_RATE  # (1 per minute)
        self.VOICE_BONUS = 0.5  # (100% while in a voice channel)
        self.ACTIVITY_BONUS = 0.5  # (50% while active)
        self.HAPPY_HOUR_BONUS = 4  # (400% during happy hour)
        self.time_elapsed = 0

    async def load_data(self):
        try:
            with open(f'{self.qualified_name}_data.json', 'r+') as in_file:
                data = json.load(in_file)
                self.activities = data['activities']
                self.user_activities = data['user_activities']
                print(f"Loaded {len(data['user_activities'])} Members Activity Data.")
        except FileNotFoundError:  # file doesn't exist, init all members with 0 currency to avoid index errors
            for member in self.bot.get_all_members():
                if member.activity is not None:
                    self.activities[str(member.activity.name)] = 0
                    self.user_activities[str(member.id)] = {}
                    self.user_activities[str(member.id)][str(member.activity.name)] = 0

    async def save_data(self):
        if len(self.user_activities) > 0:
            save_data = {'activities': self.activities,
                         'user_activities': self.user_activities}
            with open(f'{self.qualified_name}_data.json', 'w+') as out_file:
                json.dump(save_data, out_file, sort_keys=False, indent=4)

    @commands.command(name="myactivities", aliases=["useractivities", "mygames", "usergames", "useract", "act"])
    async def myactivities(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        activity = self.user_activities[str(member.id)].keys()
        playtime = self.user_activities[str(member.id)].values()
        activities_and_playtime = list(zip(activity, playtime))
        activities_and_playtime = sorted(activities_and_playtime, key=itemgetter(1, 0), reverse=True)
        activities_and_playtime = activities_and_playtime[:10]
        msg = f"{member.mention}\n```User {member} Top Playtime:\n"
        for activity, playtime in activities_and_playtime:
            if playtime / 60 < 600:
                msg += "{0:<32.32} | {1:>.1f} minutes(s) \n".format(str(activity), playtime / 60)
            elif (playtime / 60 / 60) < 24:
                msg += "{0:<32.32} | {1:>.1f} hours(s) \n".format(str(activity), playtime / 60 / 60)
            else:
                msg += "{0:<32.32} | {1:>.1f} days(s) \n".format(str(activity), playtime / 60 / 60 / 24)
        msg += "```"
        # log = await self.bot.get_channel(self.bot.LOG_CHANNEL).send(msg)
        await ctx.send(msg, delete_after=self.bot.MEDIUM_DELETE_DELAY)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    @commands.command(name="topactivities", aliases=["topgames", "games", "activities"])
    async def topactivities(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        activity = self.activities.keys()
        playtime = self.activities.values()
        activity_and_playtime = list(zip(activity, playtime))
        activity_and_playtime = sorted(activity_and_playtime, key=itemgetter(1, 0), reverse=True)
        activity_and_playtime = activity_and_playtime[:10]
        msg = f"Server Wide\n```Top Activities\n"
        for activity, playtime in activity_and_playtime:
            if playtime / 60 < 600:
                msg += "{0:<32.32} | {1:>.1f} minutes(s) \n".format(str(activity), playtime / 60)
            elif (playtime / 60 / 60) < 24:
                msg += "{0:<32.32} | {1:>.1f} hours(s) \n".format(str(activity), playtime / 60 / 60)
            else:
                msg += "{0:<32.32} | {1:>.1f} days(s) \n".format(str(activity), playtime / 60 / 60 / 24)
        msg += "```"
        # log = await self.bot.get_channel(self.bot.LOG_CHANNEL).send(msg)
        await ctx.send(msg, delete_after=self.bot.MEDIUM_DELETE_DELAY)
        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    async def timeout(self):
        debug_channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        log_channel = self.bot.get_channel(self.bot.LOG_CHANNEL)
        if not self.bot.is_closed() and self.bot.time_elapsed > 0:
            for member in self.bot.get_all_members():
                if member.activity is not None:
                    # all activity
                    if str(member.activity.name) not in self.activities.keys():
                        print("New Activity:", member.activity.name)
                        self.activities[str(member.activity.name)] = self.bot.TICK_RATE
                    else:
                        self.activities[str(member.activity.name)] += self.bot.TICK_RATE
                    if str(member.id) not in self.user_activities.keys():
                        self.user_activities[str(member.id)] = {}
                    if str(member.activity.name) not in self.user_activities[str(member.id)].keys():
                        print("New User Activity:", member.activity.name)
                        self.user_activities[str(member.id)][str(member.activity.name)] = self.bot.TICK_RATE
                    else:
                        self.user_activities[str(member.id)][str(member.activity.name)] += self.bot.TICK_RATE
                if DEBUG:
                    print(member.id, member, self.user_activities[str(member.id)], sep=",")
            self.time_elapsed += TICK_RATE


def setup(bot):
    bot.add_cog(ActivityStats(bot))
