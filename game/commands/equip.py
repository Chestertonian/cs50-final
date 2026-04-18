# game/commands/equip.py

from game.commands.base import Command
from game.models import Item, find_item_by_name


class EquipCommand(Command):
    def execute(self, player, db, args):
        if not args:
            return "Equip what?"

        item_name = " ".join(args)

        inventory = Item.get_items_for_player(player.id, db)
        result = find_item_by_name(item_name, inventory)

        if result is None:
            return f"You don't have '{item_name}'."

        if isinstance(result, list):
            names = ", ".join(i.name for i in result)
            return f"Which one? {names}"

        item = result

        if item.is_equipped:
            return f"The {item.name} is already equipped."

        if item.item_type not in ("weapon", "armor"):
            return f"You can't equip the {item.name}."

        # Determine the slot
        if item.item_type == "weapon":
            slot = "weapon"
        else:
            # armor slot comes from the type-specific template data
            slot = item.type_data["armor_slot"]

        # Check if something is already in that slot
        equipped = Item.get_equipped_items(player.id, db)
        for equipped_item in equipped:
            if equipped_item.equipped_slot == slot:
                return f"You must remove your {equipped_item.name} first."

        item.equip(slot)
        return f"You equip the {item.name}."