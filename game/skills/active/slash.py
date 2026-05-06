"""
game/skills/active/slash.py

Slash: level 1 warrior power.

A basic weapon strike, slightly stronger than a bare-hands attack
from the combat loop. Scales with STR. Costs a little power but
deals reliably more damage than the auto-attack.

Damage: weapon damage + STR bonus, or bare hands + STR bonus if unarmed.
STR bonus: +1 per 3 STR above 10.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name


class Slash(Skill):

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Attack whom?", "killed": False}

        player.power -= self.power_cost

        str_bonus = max(0, (player.stats["STR"] - 10) // 3)

        weapon = player.get_equipped_weapon(db)
        if weapon:
            base = random.randint(weapon["damage_min"], weapon["damage_max"])
            weapon_name = weapon["name"]
        else:
            base = random.randint(1, 4)
            weapon_name = "your fists"

        damage     = base + str_bonus
        new_health = target["current_health"] - damage
        npc_name   = get_npc_name(target, db)

        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()

        if new_health <= 0:
            return {
                "message":   f"You slash {npc_name} with {weapon_name} for {damage} damage. It falls!",
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        return {
            "message":   f"You slash {npc_name} with {weapon_name} for {damage} damage.",
            "damage":    damage,
            "target_id": target["id"],
            "killed":    False,
        }
