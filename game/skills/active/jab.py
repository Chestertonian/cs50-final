"""
game/skills/active/jab.py

Jab: level 1 rogue power.

A quick, cheap strike — not about raw power but about getting the
first hit in. Scales with DEX rather than STR (rogues fight smart,
not hard). Low cost means it can be used frequently.

Damage: 1-5 base + DEX bonus.
DEX bonus: +1 per 3 DEX above 10.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name


class Jab(Skill):

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Attack whom?", "killed": False}

        player.power -= self.power_cost

        dex_bonus  = max(0, (player.stats["DEX"] - 10) // 3)
        damage     = random.randint(1, 5) + dex_bonus
        new_health = target["current_health"] - damage
        npc_name   = get_npc_name(target, db)

        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()

        if new_health <= 0:
            return {
                "message":   f"You jab {npc_name} sharply for {damage} damage. It drops!",
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        return {
            "message":   f"You jab {npc_name} sharply for {damage} damage.",
            "damage":    damage,
            "target_id": target["id"],
            "killed":    False,
        }
