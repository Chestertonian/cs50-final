from game.commands.base import Command
from game.models import Item, find_item_by_name
from game.helpers import parse_target_and_index


class GetCommand(Command):
    def execute(self, player, db, args):
        if not args:
            return "Get what?"

        item_name, index = parse_target_and_index(args)
        room_items = Item.get_items_in_room(player.current_room_id, db)
        item = find_item_by_name(item_name, room_items, index)


        if item is None:
            return f"You don't see a '{item_name.lower()}' here."

        if not item.is_takeable:
            return f"You can't take the {item.name.lower()}."

        item.move_to_player(player.id)
        return f"You get the {item.name.lower()}."