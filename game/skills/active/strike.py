"""
game/skills/active/strike.py

Strike: level 1 ranger power.

A focused melee strike, splitting the difference between the
warrior's brute STR and the rogue's DEX. Rangers scale off
whichever of STR or DEX is higher — they adapt to their weapon.

Damage: weapon damage (or 1-4 bare) + best of STR/DEX bonus.
Stat bonus: +1 per 3 points above 10, using the higher stat.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name


class Strike(Skill):

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Attack whom?", "killed": False}

        player.power -= self.power_cost

        # Rangers use whichever stat is higher.
        best_stat  = max(player.stats["STR"], player.stats["DEX"])
        stat_bonus = max(0, (best_stat - 10) // 3)

        weapon = player.get_equipped_weapon(db)
        if weapon:
            base        = random.randint(weapon["damage_min"], weapon["damage_max"])
            weapon_name = weapon["name"]
        else:
            base        = random.randint(1, 4)
            weapon_name = "your fists"

        damage     = base + stat_bonus
        new_health = target["current_health"] - damage
        npc_name   = get_npc_name(target, db)

        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()

        if new_health <= 0:
            return {
                "message":   f"You strike {npc_name} with {weapon_name} for {damage} damage. It falls!",
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        return {
            "message":   f"You strike {npc_name} with {weapon_name} for {damage} damage.",
            "damage":    damage,
            "target_id": target["id"],
            "killed":    False,
        }
