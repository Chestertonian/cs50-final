"""
game/skills/active/minor_heal.py

Minor Heal: level 3 wizard spell.

Heal amount: 5-12 base, +1 per 4 WIS above 10.
No target needed — always cast on self.
"""

import random
from game.skills.base import Skill


class MinorHeal(Skill):

    def execute(self, player, target, db):
        # Minor Heal always targets the player — ignore target entirely.

        # --- 1. Already at full health? ---
        if player.health >= player.max_health:
            return {
                "message": "You are already at full health.",
                "killed":  False,
            }

        # --- 2. Deduct power ---
        player.power -= self.power_cost

        # --- 3. Calculate heal ---
        base_heal = random.randint(5, 12)
        wis_bonus = max(0, (player.stats["WIS"] - 10) // 4)
        heal      = base_heal + wis_bonus

        # --- 4. Apply heal, capped at max ---
        player.health = min(player.health + heal, player.max_health)

        db.execute(
            "UPDATE players SET health = ? WHERE id = ?",
            (player.health, player.id)
        )
        db.commit()

        return {
            "message": (
                f"Warm arcane light flows through you, restoring health. "
                f"({player.health}/{player.max_health})"
            ),
            "killed": False,
        }
