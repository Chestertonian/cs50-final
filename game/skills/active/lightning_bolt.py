"""
game/skills/active/lightning_bolt.py

Lightning Bolt: level 11 wizard spell.

Unlike Fireball, Lightning Bolt is single-target but hits harder
against one enemy.

Damage:  20-28 base, +1 per 3 INT above 10.
Stun:    25% chance. The stunned NPC ID is returned so the combat
         loop can skip it. Not used now
Miss:    10% chance.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name


class LightningBolt(Skill):

    MISS_CHANCE = 0.10
    STUN_CHANCE = 0.25

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        npc_name = get_npc_name(target, db)

        # --- 1. Miss check ---
        if random.random() < self.MISS_CHANCE:
            player.power -= self.power_cost
            return {
                "message": f"A bolt of lightning crackles toward {npc_name} — and arcs wide!",
                "killed":  False,
            }

        # --- 2. Deduct power ---
        player.power -= self.power_cost

        # --- 3. Damage ---
        int_bonus = max(0, (player.stats["INT"] - 10) // 3)
        damage    = random.randint(10, 24) + int_bonus

        new_health = target["current_health"] - damage
        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()

        if new_health <= 0:
            return {
                "message": (
                    f"A searing bolt of lightning tears through {npc_name} "
                    f"for {damage} damage. It convulses and drops dead!"
                ),
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        # --- 4. Stun check ---
        # TODO: when you have a status effect system, apply 'stunned' here
        # so the combat loop skips this NPC's next attack.
        stunned = random.random() < self.STUN_CHANCE

        if stunned:
            msg = (
                f"A searing bolt of lightning tears through {npc_name} "
                f"for {damage} damage — it is stunned!"
            )
        else:
            msg = (
                f"A searing bolt of lightning tears through {npc_name} "
                f"for {damage} damage!"
            )

        return {
            "message":   msg,
            "damage":    damage,
            "target_id": target["id"],
            "killed":    False,
            "stunned":   stunned,
            "stunned_id": target["id"] if stunned else None,
        }

