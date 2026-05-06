"""
game/skills/active/greater_magic_missile.py

Greater Magic Missile: level 13 wizard spell.

Fires three bolts of arcane energy simultaneously, each rolled
independently. Like Magic Missile, it never misses — but the
three separate rolls mean variance is smoothed out, and the
total damage is substantially higher. Each bolt is also reported
individually so the player feels the impact.

Per bolt:  3-8 damage, +1 per 3 INT above 10.
Bolts:     3 (always).
Miss:      None - arcane force is unerring.
Cost:      16 power.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name


BOLT_COUNT = 3


class GreaterMagicMissile(Skill):

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        player.power -= self.power_cost

        int_bonus = max(0, (player.stats["INT"] - 10) // 3)
        npc_name  = get_npc_name(target, db)

        total_damage = 0
        bolt_lines   = []

        current_health = target["current_health"]

        for i in range(1, BOLT_COUNT + 1):
            if current_health <= 0:
                break  # target already dead — don't keep hitting
            bolt_damage     = random.randint(3, 8) + int_bonus
            current_health -= bolt_damage
            total_damage   += bolt_damage
            bolt_lines.append(f"  Bolt {i}: {bolt_damage} damage.")

        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (current_health, target["id"])
        )
        db.commit()

        killed = current_health <= 0
        lines  = [f"Three bolts of arcane energy streak toward {npc_name}!"]
        lines += bolt_lines

        if killed:
            lines.append(f"{npc_name} cannot withstand the barrage and crumples!")
        else:
            lines.append(f"{npc_name} takes {total_damage} damage in total.")

        return {
            "message":   "\n".join(lines),
            "damage":    total_damage,
            "target_id": target["id"],
            "killed":    killed,
        }
