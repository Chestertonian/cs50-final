"""
game/skills/active/slow.py

Slow: level 12 wizard spell.

Reduces the target's attack frequency. Implemented via a
skip chance checked in the combat loop each round:

    if npc_id in player.slowed_npcs:
        if random.random() < SLOW_SKIP_CHANCE:
            print(f"{npc.name} moves sluggishly and loses its action.")
            continue

Stored as player.slowed_npcs = { npc_id: ticks_remaining }.
Your tick system should decrement these and remove expired entries.

Skip chance:  40% per round (the NPC acts 60% as often).
Duration:     8 ticks.
Cost:         14 power.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name

SLOW_SKIP_CHANCE = 0.40
DURATION_TICKS   = 8


class Slow(Skill):

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        player.power -= self.power_cost

        # Initialise the dict if it doesn't exist yet.
        if not hasattr(player, "slowed_npcs"):
            player.slowed_npcs = {}

        player.slowed_npcs[target["id"]] = DURATION_TICKS

        npc_name = get_npc_name(target, db)
        return {
            "message": (
                f"You weave a web of sluggish magic around {npc_name}. "
                f"Its movements become laboured and slow."
            ),
            "killed":  False,
            "target_id": target["id"],
        }
