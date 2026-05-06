"""
game/skills/active/shock.py

Shock: level 11 wizard spell.

A quick jolt of electricity — low damage, low cost, high stun chance.
Where Lightning Bolt is a sledgehammer, Shock is a scalpel: cheap
enough to spam, useful for interrupting dangerous NPCs or finishing
off weakened targets without burning your big spells.

Damage:  2-6 base. INT gives no bonus here — this is pure reflex magic.
Stun:    50% chance (higher than Lightning Bolt, that's the tradeoff).
Cost:    10 power (cheapest offensive spell after Magic Missile).
"""

import random
from game.skills.base import Skill


class Shock(Skill):

    STUN_CHANCE = 0.50

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        player.power -= self.power_cost

        npc_name = self._get_npc_name(target, db)

        # --- Damage (no INT scaling — intentional) ---
        damage     = random.randint(2, 6)
        new_health = target["current_health"] - damage
        killed     = new_health <= 0

        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()

        if killed:
            return {
                "message":   f"You zap {npc_name} with a jolt of electricity for {damage} damage. It spasms and dies.",
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        # --- Stun check ---
        stunned = random.random() < self.STUN_CHANCE

        if stunned:
            msg = (
                f"You send a sharp jolt of electricity into {npc_name} "
                f"for {damage} damage. It convulses — stunned!"
            )
        else:
            msg = f"You send a sharp jolt of electricity into {npc_name} for {damage} damage."

        return {
            "message":    msg,
            "damage":     damage,
            "target_id":  target["id"],
            "killed":     False,
            "stunned":    stunned,
            "stunned_id": target["id"] if stunned else None,
            # TODO: hook into status effect system to skip NPC's next attack.
        }

    def _get_npc_name(self, target, db):
        row = db.execute(
            """SELECT npc_templates.name FROM npc_instances
               JOIN npc_templates ON npc_instances.template_id = npc_templates.id
               WHERE npc_instances.id = ?""",
            (target["id"],)
        ).fetchone()
        return row["name"] if row else "your target"
