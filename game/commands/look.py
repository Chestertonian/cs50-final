from game.commands.base import Command  # pyright: ignore[reportMissingImports]
from game.models import Item, find_item_by_name #NPC  # adjust if needed


class LookCommand(Command):
    def execute(self, player, db, args):
        # Look at room
        if not args:
            room = player.get_current_room(db)
            return room.describe(db)

        target_name = " ".join(args).lower()

        # --- Check room items ---
        room_items = Item.get_items_in_room(player.current_room_id, db)
        item = find_item_by_name(target_name, room_items)

        if isinstance(item, list):
            names = ", ".join(i.name for i in item)
            return f"Which one do you mean? {names}."

        if item:
            return item.description

        # --- Check inventory ---
        inventory = Item.get_items_for_player(player.id, db)
        item = find_item_by_name(target_name, inventory)

        if isinstance(item, list):
            names = ", ".join(i.name for i in item)
            return f"Which one do you mean? {names}."

        if item:
            return item.description

        # --- Check NPCs ---
        # npcs = NPC.get_npcs_in_room(player.current_room_id, db)
        # npc = find_item_by_name(target_name, npcs)  # reuse same matcher

        # if isinstance(npc, list):
        #    names = ", ".join(n.name for n in npc)
        #    return f"Which one do you mean? {names}."

        #if npc:
        #    return npc.description

        return f"You don't see a '{target_name}' here."
