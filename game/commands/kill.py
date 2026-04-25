from game.commands.base import Command
from game.models import NpcInstance, find_item_by_name
from game.helpers import parse_target_and_index
import time


class KillCommand(Command):
    def execute(self, player, db, args):

        if not args:
            return "Kill what?"

        # ─────────────────────────────
        # FIND NPC IN ROOM
        # ─────────────────────────────
        room_npcs = NpcInstance.get_instances_in_room(player.current_room_id, db)

        if not room_npcs:
            return "There is nothing to fight here."

        npc_name, index = parse_target_and_index(args)
        npc_match = find_item_by_name(npc_name, room_npcs, index)

        if isinstance(npc_match, list):
            names = ", ".join(n.name for n in npc_match)
            return f"Which one do you mean? {names}."

        if not npc_match:
            return f"You don't see '{npc_name}' here."

        # ─────────────────────────────
        # CHECK COMBAT STATE
        # ─────────────────────────────
        if npc_match.id in player.combat.attacker_ids:
            return f"You are already fighting {npc_match.name}."

        # ─────────────────────────────
        # START COMBAT
        # ─────────────────────────────
        player.combat.start_combat(npc_match.id)
        npc_match.set_aggro(db)
        return f"You lunge at {npc_match.name}!"