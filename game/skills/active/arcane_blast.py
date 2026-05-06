"""
game/skills/active/arcane_blast.py

Arcane Blast: level 13 wizard spell.

Scales heavily with INT.

Damage: 20-28 base, +1 per 2 INT above 10.
Miss:   None.
Cost:   22 power.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name


class ArcaneBlast(Skill):

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        player.power -= self.power_cost

        int_bonus  = max(0, (player.stats["INT"] - 10) // 2)
        damage     = random.randint(20, 28) + int_bonus
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
                    f"A concentrated beam of pure arcane force tears through "
                    f"{npc_name} for {damage} damage. It is annihilated!"
                ),
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        return {
            "message": (
                f"A concentrated beam of pure arcane force tears through "
                f"{npc_name} for {damage} damage."
            ),
            "damage":    damage,
            "target_id": target["id"],
            "killed":    False,
        }
