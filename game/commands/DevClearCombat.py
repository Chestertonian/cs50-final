# game/commands/DevClearCombat.py

from game.commands.base import Command

class DevClearCombatCommand(Command):
    def execute(self, player, db, args):
        player.combat.end_combat()
        return "Combat state cleared."