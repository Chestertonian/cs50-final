# game/commands/DevDeathCommands
# Not for use by players; to be removed.

from game.commands.base import Command
from game.combat.combat_loop import handle_death

class DeathCommand(Command):
    def execute(self, player, db, args):
        handle_death(player, db)
        return "Perhaps the gods will grant you another chance at life..."