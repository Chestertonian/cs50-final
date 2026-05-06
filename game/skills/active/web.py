"""
game/skills/active/web.py

Web: level 9 wizard spell.

Entangles the target in sticky magical webs. Does minimal damage
but prevents the NPC from fleeing. The 'webbed' flag is stored on
the npc_instance via a future status column — for now it's returned
in the result dict as a hook.

Also has a secondary effect: webbed NPCs have a 20% chance to lose
their attack each round (they're struggling against the webs).

Damage:  1-4 (the webs constrict, but this isn't a damage spell).
Webbed:  85% success chance — some creatures are too strong to hold.
"""

import random
from game.skills.base import Skill


class Web(Skill):

    WEB_CHANCE = 0.85

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        player.power -= self.power_cost

        npc_name = self._get_npc_name(target, db)

        # --- Constriction damage ---
        damage     = random.randint(1, 4)
        new_health = target["current_health"] - damage
        killed     = new_health <= 0

        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()

        if killed:
            return {
                "message": (
                    f"Thick webs of arcane silk engulf {npc_name}, crushing the life from it!"
                ),
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        # --- Web success check ---
        webbed = random.random() < self.WEB_CHANCE

        if webbed:
            msg = (
                f"Thick webs of arcane silk shoot from your fingers, "
                f"ensnaring {npc_name}! It struggles but cannot escape."
            )
        else:
            msg = (
                f"Webs shoot toward {npc_name}, but it tears free before they take hold."
            )

        return {
            "message":   msg,
            "damage":    damage,
            "target_id": target["id"],
            "killed":    False,
            "webbed":    webbed,
            # TODO: when status effects exist, apply 'webbed' to the NPC here
            # which should block its flee attempt and give 20% attack miss chance.
        }

    def _get_npc_name(self, target, db):
        row = db.execute(
            """SELECT npc_templates.name FROM npc_instances
               JOIN npc_templates ON npc_instances.template_id = npc_templates.id
               WHERE npc_instances.id = ?""",
            (target["id"],)
        ).fetchone()
        return row["name"] if row else "your target"
