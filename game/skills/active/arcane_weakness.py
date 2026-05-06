"""
game/skills/active/arcane_weakness.py

Arcane Weakness: level 14 wizard spell.
The combat loop should check this when calculating damage dealt
to the NPC, whether from auto-attack or skills:

    multiplier = 1.30 if npc.id in player.weakened_npcs else 1.0
    damage = int(damage * multiplier)

Your tick system should decrement weakened_npcs the same way as
slowed_npcs.

Duration: 8 ticks.
Cost:     14 power.
"""

from game.skills.base import Skill
from game.helpers import get_npc_name

DURATION_TICKS = 8


class ArcaneWeakness(Skill):

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        player.power -= self.power_cost

        if not hasattr(player, "weakened_npcs"):
            player.weakened_npcs = {}

        player.weakened_npcs[target["id"]] = DURATION_TICKS
        npc_name = get_npc_name(target, db)

        return {
            "message": (
                f"You tear at the magical defenses of {npc_name}. "
                f"It shudders as its resistance crumbles."
            ),
            "killed":    False,
            "target_id": target["id"],
        }
