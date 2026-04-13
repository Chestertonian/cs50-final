# Written by Lumo, edited by yours truly.
from game.commands.base import Command
import datetime

class TimeCommand(Command):
    def execute(self, player, db, args):
        now = datetime.datetime.now()
        current_hour = now.hour
        current_time = now.time()
        
        sunrise = datetime.time(6, 0)
        sunset = datetime.time(19, 0)
        if current_hour == 0:
            display_hour = 12
            period = "am"
        elif current_hour < 12:
            display_hour = current_hour
            period = "am"
        elif current_hour == 12:
            display_hour = 12
            period = "pm"
        else:
            display_hour = current_hour - 12
            period = "pm"
        next_hour = display_hour + 1
        if next_hour == 13:
            next_hour = 1

        if sunrise <= current_time <= sunset:
            return f"Judging by the sun's progress across the heavens, you deem that it is between {display_hour} and {next_hour} {period}."
        else:
            return f"Judging by the position of the stars, you deem that it is between {display_hour} and {next_hour} {period}."