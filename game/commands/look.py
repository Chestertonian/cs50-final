# game/commands/look.py

from game.commands.base import Command  # pyright: ignore[reportMissingImports]
from game.models import Item, NpcInstance, find_item_by_name
from game.helpers import wrap_text, parse_target_and_index


class LookCommand(Command):
    def execute(self, player, db, args):

        # ─────────────────────────────
        # LOOK AT ROOM
        # ─────────────────────────────
        if not args:
            room = player.get_current_room(db)
            return room.describe(db)

        target_name = " ".join(args).lower()

        # ─────────────────────────────
        # NPCS IN ROOM
        # ─────────────────────────────
        room_npcs = NpcInstance.get_instances_in_room(
            player.current_room_id, db)
        npc_name, index = parse_target_and_index(args)
        npc_match = find_item_by_name(npc_name, room_npcs, index)

        if isinstance(npc_match, list):
            names = ", ".join(n.name for n in npc_match)
            return f"Which one do you mean? {names}."

        if npc_match:
            return wrap_text(f"\n{npc_match.description}\n")

        # ─────────────────────────────
        # ROOM ITEMS
        # ─────────────────────────────
        room_items = Item.get_items_in_room(player.current_room_id, db)
        item_name, index = parse_target_and_index(args)
        item_match = find_item_by_name(item_name, room_items, index)

        if isinstance(item_match, list):
            names = ", ".join(i.name for i in item_match)
            return f"Which one do you mean? {names}."

        if item_match:
            return wrap_text(item_match.description)

        # ─────────────────────────────
        # INVENTORY ITEMS
        # ─────────────────────────────
        inventory = Item.get_items_for_player(player.id, db)
        item_match = find_item_by_name(target_name, inventory)

        if isinstance(item_match, list):
            names = ", ".join(i.name for i in item_match)
            return f"Which one do you mean? {names}."

        if item_match:
            return wrap_text(item_match.description)

        # ─────────────────────────────
        # NOT FOUND
        # ─────────────────────────────
        return f"You don't see a '{target_name}' here."
