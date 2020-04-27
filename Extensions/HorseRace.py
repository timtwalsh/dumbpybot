import asyncio
import random
import random
from collections import defaultdict

from discord.ext import commands

DEBUG = True
TICK_RATE = 6  # Default
emoji_letters_dict = {'A': '🇦', 'B': '🇧', 'C': '🇨', 'D': '🇩', 'E': '🇪', 'F': '🇫', 'G': '🇬', 'H': '🇭', 'I': '🇮',
                      'J': '🇯', 'K': '🇰', 'L': '🇱', 'M': '🇲', 'N': '🇳', 'O': '🇴', 'P': '🇵', 'Q': '🇶', 'R': '🇷',
                      'S': '🇸', 'T': '🇹', 'U': '🇺', 'V': '🇻', 'W': '🇼', 'X': '🇽', 'Y': '🇾', 'Z': '🇿', ' ': '✴'}
HORSE_NAMES = {"11": "Clockwork", "12": "Setsuna", "13": "Imperator", "21": "Magneto", "22": "Radar", "23": "Raven",
               "31": "Katana", "32": "Corona", "33": "Zefir"}
HORSE_DESCRIPTIONS = {"11": "{} is a sprinter".format(HORSE_NAMES["11"]),
                      "12": "{} is a all round mid runner".format(HORSE_NAMES["12"]),
                      "13": "{} is an marathon runner".format(HORSE_NAMES["13"]),
                      "21": "{} is a fast short runner".format(HORSE_NAMES["21"]),
                      "22": "{} is a fast all rounder".format(HORSE_NAMES["22"]),
                      "23": "{} is a fast long runner".format(HORSE_NAMES["23"]),
                      "31": "{} is a very fast short runner".format(HORSE_NAMES["31"]),
                      "32": "{} is a very fast mid runner".format(HORSE_NAMES["32"]),
                      "33": "{} is a very fast all rounder".format(HORSE_NAMES["33"])
                      }
HORSE_FINISH_IMAGE = [" .---------.          ~%%%/%%%%%%%,_        \n",
                      " \ GAMBLING |     ~~%/%%%/%%%%%%-/./        \n",
                      "  \ IS FUN! |   ~~%/%%/%/%%%-` /  |`.       \n",
                      "   `--------.\~%%/%%%/%%%`  .     .__;      \n",
                      "             \~%/%%%/%%`     :       O\      \n",
                      "          ~~/%%/%%%%`      :           `.     \n",
                      "        ~~%/%%/%%%`         `. _,         '.   \n",
                      "      ~~/%/%%%%%`          .'``-._          `. \n",
                      "  ~~%%%/%%%%%`           :       `-.   \   (,; \n",
                      " ~~%%%%%%%%`             :           `._\__.'\n"]
HORSE_FINISH_NAME = ["~~~%%%%%%%.              ;"]


def scaleBetween(unscaledNum, minAllowed, maxAllowed, min, max):
    try:
        return (maxAllowed - minAllowed) * (unscaledNum - min) / (max - min) + minAllowed
    except ZeroDivisionError:
        return 0


HORSE_ATTRIBUTE_INDEX_NAMES = ["SPEED", "ACCELERATION", "STAMINA"]


def horse_race(track_length):
    horse_numbers = ["¹¹", "¹²", "¹³", "²¹", "²²", "²³", "³¹", "³²", "³³"]
    horse_number_to_horse_name_keys = {"¹¹": "11", "¹²": "12", "¹³": "13", "²¹": "21", "²²": "22", "²³": "23",
                                       "³¹": "31", "³²": "32", "³³": "33"}
    horse_stat_list = [[2.25, 2.25, 1.5], [2.25, 2.0, 1.75], [2.25, 1.75, 2.0],
                       [2.5, 2.0, 1.5], [2.5, 1.75, 1.75], [2.5, 1.625, 1.875],
                       [2.75, 1.75, 1.5], [2.75, 1.5, 1.75], [2.75, 1.625, 1.625]]
    horse_stats = {"¹¹": horse_stat_list[0], "¹²": horse_stat_list[1], "¹³": horse_stat_list[2],
                   "²¹": horse_stat_list[3], "²²": horse_stat_list[4], "²³": horse_stat_list[5],
                   "³¹": horse_stat_list[6], "³²": horse_stat_list[7], "³³": horse_stat_list[8]}
    random.shuffle(horse_numbers)
    horse_numbers = random.sample(horse_numbers, 4)
    horse_numbers_text = [horse_number_to_horse_name_keys[number] for number in horse_numbers]
    momentum_visual = ["   ", "' -", " -=", "-=="]
    horses = []
    horse_visual = "ɿ{}ʅʔ"
    horse_stamina = [1, 1, 1, 1]
    horse_momentum = [1, 1, 1, 1]
    horse_locations = [-2, -2, -2, -2]
    horse_tired_speed = 0.01
    acc_influence = 1.5
    random_influence = acc_influence
    stam_influence = 3
    speed_influence = 2
    base_speed = 1.5
    exhaustion_rate = 1.5
    race_horse_names = []
    display_scale_high = 35
    display_scale_low = 0
    frames = []
    for horse in horse_numbers:
        horse_key = horse_number_to_horse_name_keys[horse]
        race_horse_names.append(HORSE_NAMES[horse_key])
        horses.append(horse_visual.format(horse))
    for i in range(1, track_length, 2):
        horse_momentum_value = [0, 0, 0, 0]
        screen_mod = i - 7
        if screen_mod <= 0:
            screen_mod = 0
        if screen_mod >= 10:
            screen_mod = i - 7 + 1
        for horse in horse_numbers:
            loser = min(horse_locations)
            winner = max(horse_locations)
            if horse_locations[horse_numbers.index(horse)] == winner:
                boost = (random.randrange(-10, 0) / 5) * random_influence
            if horse_momentum[horse_numbers.index(horse)] > (base_speed + horse_stats[horse][
                0]) * speed_influence:  # mom > top speed / if the horse is over top speed
                horse_stamina[horse_numbers.index(horse)] -= horse_momentum[horse_numbers.index(
                    horse)] * exhaustion_rate  # reduce stamina by momentum modded by exh rate
            else:  # if the horse momentum is below top speed
                horse_momentum[horse_numbers.index(horse)] += horse_stats[horse][1] * acc_influence + (
                        random.randrange(-5,
                                         5) / 10) * random_influence + boost  # increase horse momentum using horse accel + random
            # then
            if horse_stamina[horse_numbers.index(horse)] <= 0:  # if horses stam < 0 it is exhausted
                horse_stamina[horse_numbers.index(horse)] = horse_stats[horse][
                                                                2] * stam_influence  # set its stamina to full
                horse_momentum[horse_numbers.index(horse)] = horse_tired_speed  # set its speed to tired
            horse_locations[horse_numbers.index(horse)] += horse_momentum[
                horse_numbers.index(horse)]  # make the horsie move
            # print(horse_momentum[horse_numbers.index(horse)] )
            if horse_momentum[horse_numbers.index(horse)] > 9:
                horse_momentum_value[horse_numbers.index(horse)] = 3
            elif horse_momentum[horse_numbers.index(horse)] > 6:
                horse_momentum_value[horse_numbers.index(horse)] = 2
            elif horse_momentum[horse_numbers.index(horse)] > 3:
                horse_momentum_value[horse_numbers.index(horse)] = 1
            elif horse_momentum[horse_numbers.index(horse)] > 1:
                horse_momentum_value[horse_numbers.index(horse)] = 0
            positions = [[race_horse_names[horse_locations.index(horse)],
                          horse_number_to_horse_name_keys[horse_numbers[horse_locations.index(horse)]]] for horse in
                         sorted(horse_locations)]
        leader = max(horse_locations)
        finish_line = [0, 0, 0, 0]
        for k, line in enumerate(finish_line):
            if track_length - i <= 7:
                finish_line[k] = ' ' * ((34 - (i - track_length)) - min(min(display_scale_high, i + 1),
                                                                        max(display_scale_low, round(
                                                                            scaleBetween(horse_locations[k],
                                                                                         display_scale_low,
                                                                                         min(display_scale_high, i + 1),
                                                                                         max(leader / 5 * 3,
                                                                                             display_scale_low),
                                                                                         leader))))) + '|'
            else:
                finish_line[k] = ''
        position_text = ""
        for horse, horse_number in positions:
            position_text += "(#{}){} ".format(horse_number, horse)
        race_board_top = ["```", " {:.0f}/{:.0f} Furlongs\n".format((i + 1) / 8, track_length / 8), position_text, '\n',
                          "__________________________________________________\n",
                          "|_______|_______|_______|_______|_______|_______|_______|_______|_______"[
                          screen_mod % 7:50 + screen_mod % 7], "\n\n"]  # for animating the field
        race_board_mid = [
            "{leadin}{momentum}{horse}{finishline}\n".format(
                horse=horses[0], momentum=momentum_visual[horse_momentum_value[0]],
                leadin=' ' * min(min(display_scale_high, i + 1), max(display_scale_low, round(
                    scaleBetween(horse_locations[0], display_scale_low, min(display_scale_high, i + 1),
                                 max(leader / 5 * 3, display_scale_low), leader)))),
                finishline=finish_line[0]),
            "{leadin}{momentum}{horse}{finishline}\n".format(
                horse=horses[1], momentum=momentum_visual[horse_momentum_value[1]],
                leadin=' ' * min(min(display_scale_high, i + 1), max(display_scale_low, round(
                    scaleBetween(horse_locations[1], display_scale_low, min(display_scale_high, i + 1),
                                 max(leader / 5 * 3, display_scale_low), leader)))),
                finishline=finish_line[1]),
            "{leadin}{momentum}{horse}{finishline}\n".format(
                horse=horses[2], momentum=momentum_visual[horse_momentum_value[2]],
                leadin=' ' * min(min(display_scale_high, i + 1), max(display_scale_low, round(
                    scaleBetween(horse_locations[2], display_scale_low, min(display_scale_high, i + 1),
                                 max(leader / 5 * 3, display_scale_low), leader)))),
                finishline=finish_line[2]),
            "{leadin}{momentum}{horse}{finishline}\n".format(
                horse=horses[3], momentum=momentum_visual[horse_momentum_value[3]],
                leadin=' ' * min(min(display_scale_high, i + 1), max(display_scale_low, round(
                    scaleBetween(horse_locations[3], display_scale_low, min(display_scale_high, i + 1),
                                 max(leader / 5 * 3, display_scale_low), leader)))),
                finishline=finish_line[3])
        ]
        race_board_bot = ["__________________________________________________\n",
                          "|_______|_______|_______|_______|_______|_______|_______|_______|_______"[
                          screen_mod % 7:50 + screen_mod % 7],
                          "```"]  # for animating the field
        race_board = race_board_top + race_board_mid + race_board_bot
        frames.append(race_board)
    return frames, horse_numbers_text, positions


class HorseRace(commands.Cog):
    def __init__(self, bot):
        global TICK_RATE
        TICK_RATE = bot.TICK_RATE
        self.bot = bot
        self.time_elapsed = 0

        self.HORSE_WAIT_TIME = 45
        self.HORSE_REQUIRED_BETTERS = 2
        self.horse_race_status = ""
        self.horse_race_numbers = []
        self.horse_users = []
        self.horse_positions = []
        self.horse_bets = {}
        self.horse_odds = {}
        self.horse_listing = ""
        self.user_name_to_user_id = defaultdict()

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.bot.user.id:
            if message.content.lower().startswith("horse race: "):
                self.horse_listing = ""
                self.horse_odds = {}
                self.horse_bets = {}
                track_length = random.randrange(50, 140, 10)
                wait_time = self.HORSE_WAIT_TIME
                required_betters = self.HORSE_REQUIRED_BETTERS
                horse_frames, self.horse_race_numbers, self.horse_positions = horse_race(track_length)
                if DEBUG:
                    print("horse_race run", self.horse_race_numbers, self.horse_positions)
                # shuffled_horse_positions = self.horse_positions
                # random.shuffle(shuffled_horse_positions)
                for horse in self.horse_race_numbers:
                    self.horse_odds[horse] = 6  # Default Odds
                    self.horse_listing += "(#{}){} at {} to 1\n     {}\n".format(horse, HORSE_NAMES[horse],
                                                                                 self.horse_odds[horse],
                                                                                 HORSE_DESCRIPTIONS[horse])
                if DEBUG:
                    print("desc text updated")
                for second in range(wait_time, 0, -1):
                    user_count = len(self.horse_users)
                    msg = self.horse_race_status + '{}/{} Users are Interested'.format(user_count,
                                                                                       required_betters) + "... {} seconds to go".format(
                        second) + '```Type "!race" to participate.```'
                    if user_count >= required_betters:
                        msg = self.horse_race_status + '{}/{} Users are Interested'.format(user_count,
                                                                                           required_betters) + "... SUCCESS.".format(
                            second) + '```Horse Listings are being generated...```'
                        await message.edit(content=msg)
                        await asyncio.sleep(3)
                        break
                    else:
                        await message.edit(content=msg)
                        asyncio.sleep(1)

                if user_count >= required_betters:
                    if DEBUG:
                        print("horse_race user_count >= required", required_betters)
                    self.horse_race_status = "Horse Race: LISTING: "
                    for second in range(wait_time * 2, wait_time, -5):
                        user_count = len(self.horse_users)
                        horse_listing = ""
                        for horse in self.horse_race_numbers:
                            horse_listing += "(#{}){} at {} to 1\n     {}\n".format(horse, HORSE_NAMES[horse],
                                                                                    self.horse_odds[horse],
                                                                                    HORSE_DESCRIPTIONS[horse])
                        msg = "Type !bet horse_number amount to place your bets ... {} seconds to go\nEg !bet 11 500 to bet 500 on Clockwork.```{} Furlong Race\n\n{}```".format(
                            second, round(track_length / 8), horse_listing)
                        await message.edit(content=self.horse_race_status + msg)
                        await asyncio.sleep(5)
                    if user_count >= required_betters:
                        horse_race_status = "Horse Race: TAKING BETS: "
                        for second in range(wait_time, 0, -5):
                            horse_listing = ""
                            for horse in self.horse_race_numbers:
                                horse_listing += "(#{}){} at {} to 1\n     {}\n".format(horse, HORSE_NAMES[horse],
                                                                                        self.horse_odds[horse],
                                                                                        HORSE_DESCRIPTIONS[horse])
                            msg = "{} Bets Placed, need {} to continue ... {} seconds to go\nEg !bet 11 500 to bet 500 on Clockwork.```{} Furlong Race\n\n{}```".format(
                                len(self.horse_bets.keys()), required_betters, second, track_length / 8, horse_listing)
                            await message.edit(content=horse_race_status + msg)
                            await asyncio.sleep(5)
                        if len(self.horse_bets.keys()) >= round(required_betters / 2):
                            horse_race_status = "Horse Race: STARTING: "
                            msg = ''.join([str(line) for line in horse_frames[0]])
                            if horse_race_status != "":
                                horse_race_status = "Horse Race: RUNNING: "
                                for frame in horse_frames:
                                    msg = ''.join([str(line) for line in frame])
                                    await message.edit(content=horse_race_status + msg)
                                    await asyncio.sleep(1)
                                await asyncio.sleep(3)
                                horse_race_status = "Horse Race: FINISHED: "
                                winning_horse = self.horse_positions[3]
                                msg = '```'
                                msg += ''.join([str(line) for line in HORSE_FINISH_IMAGE])
                                msg += ''.join([str(line) for line in HORSE_FINISH_NAME])
                                msg += '     #{} {} Takes the win!```'.format(winning_horse[1], winning_horse[0])
                                await message.edit(content=horse_race_status + msg)
                                msg += '```************ BET RESULTS ************'
                                winning_odds = self.horse_odds[winning_horse[1]]
                                winners = ''
                                losers = ''
                                for user in self.horse_bets.keys():
                                    user_bets = self.horse_bets[user].split("|")
                                    for user_bet in user_bets:
                                        user_bet_details = user_bet.split('_')
                                        if user_bet_details[0] != '':
                                            user_bet_horse = user_bet_details[0]
                                            bet_amount = user_bet_details[1]
                                            if winning_horse[1] == user_bet_horse:
                                                winners += '\n{} who bet §{} on {} and won §{}'.format(user,
                                                                                                       int(bet_amount),
                                                                                                       HORSE_NAMES[
                                                                                                           user_bet_horse],
                                                                                                       float(
                                                                                                           bet_amount) * int(
                                                                                                           winning_odds))
                                                # all_users[better_index].add_gamblestat("Horse Race", True,
                                                #                                        int(bet_amount) * int(
                                                #                                            winning_odds))
                                                # all_users[better_index].add_gamblestat(
                                                #     "Horse Race on {}".format(HORSE_NAMES[user_bet_horse]), True,
                                                #     int(bet_amount) * int(winning_odds))
                                                self.bot.get_cog('Currency').add_user_currency(
                                                    self.user_name_to_user_id[user],
                                                    float(bet_amount) * int(winning_odds))
                                            else:
                                                # all_users[better_index].add_gamblestat("Horse Race", False,
                                                #                                        int(bet_amount))
                                                # all_users[better_index].add_gamblestat(
                                                #     "Horse Race on {}".format(HORSE_NAMES[user_bet_horse]), False,
                                                #     int(bet_amount))
                                                losers += '\n{} who bet §{} on {} and lost'.format(user, bet_amount,
                                                                                                   HORSE_NAMES[
                                                                                                       user_bet_horse])
                                msg += winners
                                msg += losers
                                msg += ' ```'
                                await message.edit(content=horse_race_status + msg)
                                self.horse_race_status = ''
                                self.horse_users = []
                        else:
                            await message.edit(content="Horse Race: CANCELLED: Only {} users placed bets. ".format(
                                user_count) + "Requires {} bets to start.".format(round(required_betters / 2)))
                            for user in self.horse_bets.keys():
                                user_bets = self.horse_bets[user].split("|")
                                for user_bet in user_bets:
                                    user_bet_details = user_bet.split('_')
                                    if user_bet_details[0] != '':
                                        user_bet_horse = user_bet_details[0]
                                        bet_amount = user_bet_details[1]
                                        self.bot.get_cog('Currency').add_user_currency(self.user_name_to_user_id[user],
                                                                                       float(bet_amount))
                            self.horse_race_status = ''
                            self.horse_users = []

                else:
                    await message.edit(content="Horse Race: CANCELLED: Only {} users joined. ".format(
                        user_count) + "Requires {} users to start.".format(required_betters))
                    self.horse_race_status = ''
                    self.horse_users = []

    @commands.command()
    async def race(self, ctx):
        """!race - Starts a Race Request"""
        if self.horse_race_status == '':
            msg = 'Horse Race: REQUESTED: '
            self.horse_race_status = msg
            self.horse_users.append(str(ctx.author))
            await ctx.channel.send(msg)

        elif self.horse_race_status == 'Horse Race: REQUESTED: ':
            if not str(ctx.author) in self.horse_users:
                self.horse_users.append(str(ctx.author))

        await ctx.message.delete(delay=self.bot.SHORT_DELETE_DELAY)

    @commands.command()
    async def bet(self, ctx, bet_horse: str, horse_bet_amount: float):
        """!bet [horse] [amount] - Bets on race"""
        if self.horse_race_status == 'Horse Race: LISTING: ' or self.horse_race_status == 'Horse Race: TAKING BETS: ':
            try:
                horse_user = str(ctx.author)
                bet_user_id = str(ctx.author.id)
                print(horse_bet_amount, "on ", bet_horse)
                user_points = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                if horse_bet_amount <= user_points and horse_bet_amount >= 0.1:
                    valid_bet = True
                msg = ' '
                print(ctx.author.id, "with", user_points)
                print(self.horse_race_numbers)
                if bet_horse not in self.horse_race_numbers:
                    bet_horse = -1
                if horse_user in self.horse_bets:
                    bet_horse = -3
                if int(bet_horse) > 0:
                    horse_bet_amount = int(horse_bet_amount)
                    if valid_bet:
                        if horse_user in self.horse_bets.keys():
                            self.horse_bets[horse_user] += "{}_{}|".format(bet_horse, horse_bet_amount)
                        else:
                            self.horse_bets[horse_user] = "{}_{}|".format(bet_horse, horse_bet_amount)
                        # all_users[index].remove_points(horse_bet_amount)
                        self.bot.get_cog('Currency').remove_user_currency(bet_user_id, horse_bet_amount)
                        user_points = self.bot.get_cog('Currency').get_user_currency(bet_user_id)
                        temp_bets = []
                        for bet in "".join([j for i in self.horse_bets.values() for j in i]).split('|'):
                            temp_bets.append(bet.split('_')[0])
                        print(temp_bets.count(bet_horse))
                        self.horse_odds[bet_horse] = max(2, 6 - max(temp_bets.count(bet_horse),
                                                                    1))  # +random.randint(1, -2)
                        print(self.horse_odds)
                        msg = "{} placed bet {} on **{} (#{})** to win. §{:.2f} Left.".format(ctx.author.mention,
                                                                                              horse_bet_amount,
                                                                                              HORSE_NAMES[bet_horse],
                                                                                              bet_horse, user_points)
                    else:
                        msg = "{}: You don't have enough Shekels for that bet. §{:.2f} left".format(ctx.author.mention,
                                                                                                    user_points)
                else:
                    if bet_horse == -1:
                        msg = '{}: Not a valid horse number.'.format(ctx.author.mention)
                    if bet_horse == -3:
                        msg = '{}: You may only bet once per race.'.format(ctx.author.mention)
            except Exception as error:
                print(error)
                msg = '{} Invalid Bet Use: !bet **horse_number** *amount* to place your bets. ```(Eg !bet 11 500 to bet 500 on Clockwork.)```\n You have {}{}s '.format(
                    ctx.author.mention, user_points, str(self.bot.CURRENCY_NAME).capitalize())
        else:
            if self.horse_race_status == "":
                msg = "No Race is running, Use !race to initiate a race quest."
            else:
                msg = "The race is not elligible for bets right now. Ensure the Race is at the Listing or Betting stage to place bets."
        new_message = await ctx.channel.send(msg, delete_after=self.bot.MEDIUM_DELETE_DELAY)
        log = await self.bot.get_channel(self.bot.LOG_CHANNEL).send(msg)
        await ctx.message.delete(delay=self.bot.MEDIUM_DELETE_DELAY)

    async def timeout(self):
        channel = self.bot.get_channel(self.bot.DEBUG_CHANNEL)
        if not self.bot.is_closed():
            self.time_elapsed += TICK_RATE
            for member in self.bot.get_all_members():
                self.user_name_to_user_id[str(member)] = str(member.id)
            # if DEBUG:
            # await channel.send(f"{self.qualified_name}: {self.time_elapsed}")


def setup(bot):
    bot.add_cog(HorseRace(bot))
