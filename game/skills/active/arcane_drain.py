"""
game/skills/active/arcane_drain.py

Arcane Drain: level 16 wizard spell.

Deals moderate damage and restores power equal to half the damage
dealt. Sustain spell, allows for continued casting in long fight.

Damage:        8-14 base, +1 per 4 INT above 10.
Power restore: half of damage dealt (rounded down).
Cost:          18 power (net cost is lower due to restore).
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name


class ArcaneDrain(Skill):

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        player.power -= self.power_cost

        int_bonus  = max(0, (player.stats["INT"] - 10) // 4)
        damage     = random.randint(8, 14) + int_bonus
        new_health = target["current_health"] - damage
        restored   = damage // 2
        npc_name   = get_npc_name(target, db)

        # Apply damage.
        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )

        # Restore power, capped at max.
        player.power = min(player.power + restored, player.max_power)
        db.execute(
            "UPDATE players SET power = ? WHERE id = ?",
            (player.power, player.id)
        )
        db.commit()

        if new_health <= 0:
            return {
                "message": (
                    f"You tear the life force from {npc_name} for {damage} damage, "
                    f"restoring {restored} power. It collapses!"
                ),
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        return {
            "message": (
                f"You tear the life force from {npc_name} for {damage} damage, "
                f"restoring {restored} power. ({player.power}/{player.max_power})"
            ),
            "damage":    damage,
            "target_id": target["id"],
            "killed":    False,
        }
