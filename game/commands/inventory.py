from game.commands.base import Command
from game.models import Item


class InventoryCommand(Command):
    def execute(self, player, db, args):
        player_items = Item.get_items_for_player(player.id, db)

        if not player_items:
            return "You are carrying nothing."

        equipped = [i for i in player_items if i.is_equipped]
        carried  = [i for i in player_items if not i.is_equipped]

        slot_order = ["weapon", "head", "body", "hands", "feet"]
        equipped.sort(key=lambda i: slot_order.index(i.equipped_slot)
                                    if i.equipped_slot in slot_order else 99)

        output = []

        if equipped:
            output.append("\nEquipped:")
            for item in equipped:
                output.append(f"  <{item.equipped_slot}>  {item.name.capitalize()}")

        if carried:
            output.append("\nCarrying:")
            for item in carried:
                output.append(f"  {item.name.capitalize()}")

        return "\n".join(output)