# game/commands/wealth.py

from game.commands.base import Command
from game.wealth import get_wealth

class WealthCommand(Command):
    """Show the player their current gold."""

    names = ["gold", "coins", "wealth"]

    def execute(self, player, db, args):
        amount = get_wealth(player.id)
        print(f"You are carrying {amount} gold coin{'s' if amount != 1 else ''}.")
