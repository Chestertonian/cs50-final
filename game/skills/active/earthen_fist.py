"""
game/skills/active/earthen_fist.py

Earthen Fist: level 8 wizard spell.

No INT scaling.
Stun chance: 35% (stored in result dict for future status system).
Damage: 8-16 flat.
Cost:   12 power.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name

STUN_CHANCE = 0.35


class EarthenFist(Skill):

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        player.power -= self.power_cost

        # No INT scaling — intentional.
        damage     = random.randint(8, 16)
        new_health = target["current_health"] - damage
        npc_name   = get_npc_name(target, db)

        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()

        if new_health <= 0:
            return {
                "message": (
                    f"A massive fist of stone crashes into {npc_name} "
                    f"for {damage} damage. It crumbles under the blow!"
                ),
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        stunned = random.random() < STUN_CHANCE

        if stunned:
            msg = (
                f"A massive fist of stone crashes into {npc_name} "
                f"for {damage} damage, sending it reeling!"
            )
        else:
            msg = (
                f"A massive fist of stone crashes into {npc_name} "
                f"for {damage} damage."
            )

        return {
            "message":    msg,
            "damage":     damage,
            "target_id":  target["id"],
            "killed":     False,
            "stunned":    stunned,
            "stunned_id": target["id"] if stunned else None,
        }
