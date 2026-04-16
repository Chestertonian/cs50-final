from game.commands.base import Command
from game.models import Item, find_item_by_name


class DropCommand(Command):
    def execute(self, player, db, args):
        if not args:
            return "Drop what?"

        item_name = " ".join(args)  # handles multi-word names

        player_items = Item.get_items_for_player(player.id, db)
        item = find_item_by_name(item_name, player_items)

        if item is None:
            return f"You don't have a '{item_name.lower()}'."

        if not item.is_droppable:
            return f"You can't drop the {item.name.lower()}."
        room=player.get_current_room(db)
        item.move_to_room(room.id)
        return f"You drop the {item.name.lower()}."