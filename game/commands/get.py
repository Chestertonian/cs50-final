# game/commands/get.py

from game.commands.base import Command
from game.models import Item, find_item_by_name
from game.helpers import parse_target_and_index
import time


class GetCommand(Command):
    def execute(self, player, db, args):
        if not args:
            return "Get what?"
        if args == ["all"]:
            for i in Item.get_items_in_room(player.current_room_id, db):
                if not i.is_takeable:
                    print(f"You can't take the {i.name.lower()}.")
                else:
                    i.move_to_player(player.id)
                    db.execute(
                        """
                        UPDATE item_spawns
                        SET last_spawn_at = ?
                        WHERE template_id = ? AND room_id = ?
                        """,
                        (time.time(), i.template_id, player.current_room_id)
                        )
                    db.commit()
                    print(f"You get the {i.name.lower()}.")
            return
        item_name, index = parse_target_and_index(args)
        room_items = Item.get_items_in_room(player.current_room_id, db)
        item = find_item_by_name(item_name, room_items, index)

        if item is None:
            return f"You don't see a '{item_name.lower()}' here."

        if not item.is_takeable:
            return f"You can't take the {item.name.lower()}."

        item.move_to_player(player.id)
        db.execute(
            """
            UPDATE item_spawns
            SET last_spawn_at = ?
            WHERE template_id = ? AND room_id = ?
            """,
            (time.time(), item.template_id, player.current_room_id)
        )
        db.commit()

        return f"You get the {item.name.lower()}."
