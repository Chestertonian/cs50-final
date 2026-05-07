# game/commands/DevDeathCommands
# Not for use by players.

from game.commands.base import Command
from game.combat.combat_loop import handle_death


class DeathCommand(Command):
    def execute(self, player, db, args):
        handle_death(player, db)
        return "Perhaps the gods will grant you another chance at life..."
