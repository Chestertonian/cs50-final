from game.commands.base import Command
from game.models import Item


class InventoryCommand(Command):
    def execute(self, player, db, args):
        player_items = Item.get_items_for_player(player.id, db)

        if not player_items:
            return "You are carrying nothing."

        output = ["\nYou are carrying:"]

        for item in player_items:
            output.append(f"- {item.name.capitalize()}\n")

        return "\n".join(output)