# game/commands/remove.py

from game.commands.base import Command
from game.models import Item, find_item_by_name
from game.helpers import parse_target_and_index


class RemoveCommand(Command):
    def execute(self, player, db, args):
        if not args:
            return "Remove what?"

        item_name, index = parse_target_and_index(args)
        equipped = Item.get_equipped_items(player.id, db)
        result = find_item_by_name(item_name, equipped, index)

        if result is None:
            return f"You don't have '{item_name}' equipped."

        if isinstance(result, list):
            names = ", ".join(i.name for i in result)
            return f"Which one? {names}"

        item = result

        item.unequip()
        return f"You remove the {item.name}."
