# game/commands/flee.py

from game.commands.base import Command
import random


class FleeCommand(Command):
    def execute(self, player, db, args):
        room = player.get_current_room(db)
        if not player.combat.is_in_combat():
            return "The wicked flee when no man pursueth..." # biblical reference obviously
        exits = room.get_visible_exits(db)
        if not exits: # if there are no exits
            return "There is nowhere to flee to!"
        direction = random.choice(exits)["direction"] # run randomly
        player.combat.end_combat()
        player.move(db, direction)
        print(player.get_current_room(db).describe(db))
        return f"You flee from combat, running {direction}!"
