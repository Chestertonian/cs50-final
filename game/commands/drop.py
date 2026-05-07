# game/commands/drop.py

from game.commands.base import Command
from game.models import Item, find_item_by_name
from game.helpers import parse_target_and_index


class DropCommand(Command):
    def execute(self, player, db, args):
        if not args:
            return "Drop what?"
        if args==["all"]:
            for item in (Item.get_items_for_player(player.id, db)):
                if not item.is_droppable:
                    return f"You can't drop the {item.name.lower()}."
                room = player.get_current_room(db)
                item.move_to_room(room.id)
                print(f"You drop the {item.name.lower()}.")
            return
        item_name = " ".join(args)  # handles multi-word names

        player_items = Item.get_items_for_player(player.id, db)
        item_name, index = parse_target_and_index(args)
        item = find_item_by_name(item_name, player_items, index)

        if item is None:
            return f"You don't have a '{item_name.lower()}'."

        if isinstance(item, list):          # ← add this
            names = ", ".join(i.name for i in item)
            return f"Which one? {names}"

        if not item.is_droppable:
            return f"You can't drop the {item.name.lower()}."

        room = player.get_current_room(db)
        item.move_to_room(room.id)
        return f"You drop the {item.name.lower()}."
