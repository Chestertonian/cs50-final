# game/commands/equip.py

from game.commands.base import Command
from game.models import Item, find_item_by_name
from game.helpers import parse_target_and_index


class EquipCommand(Command):
    def execute(self, player, db, args):
        if not args:
            return "Equip what?"

        # ─────────────────────────────
        # EQUIP ALL
        # ─────────────────────────────
        if args == ["all"]:
            inventory = Item.get_items_for_player(player.id, db)
            equippable = [i for i in inventory if i.item_type in ("weapon", "armor") and not i.is_equipped]

            if not equippable:
                return "You have nothing left to equip."

            equipped = Item.get_equipped_items(player.id, db)
            filled_slots = {i.equipped_slot for i in equipped}

            messages = []
            for item in equippable:
                slot = "weapon" if item.item_type == "weapon" else item.type_data["armor_slot"]

                if slot in filled_slots:
                    messages.append(f"You already have something in your {slot} slot ({item.name} skipped).")
                    continue

                item.equip(slot)
                filled_slots.add(slot)   # so the next iteration sees it as taken
                messages.append(f"You equip the {item.name}.")

            return "\n".join(messages)

        # ─────────────────────────────
        # EQUIP SINGLE (unchanged)
        # ─────────────────────────────
        inventory = Item.get_items_for_player(player.id, db)
        item_name, index = parse_target_and_index(args)
        result = find_item_by_name(item_name, inventory, index)

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

        slot = "weapon" if item.item_type == "weapon" else item.type_data["armor_slot"]

        equipped = Item.get_equipped_items(player.id, db)
        for equipped_item in equipped:
            if equipped_item.equipped_slot == slot:
                return f"You must remove your {equipped_item.name} first."

        item.equip(slot)
        return f"You equip the {item.name}."