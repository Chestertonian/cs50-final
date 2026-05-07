"""
game/skills/active/cataclysm.py

Cataclysm: level 20 wizard spell.

Unlike Meteor Storm, Cataclysm is single-target but hits harder
against one enemy.

Damage:  50-80 base, +5 per 3 INT above 10.
Miss:    10% chance.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name, wrap_text


class Cataclysm(Skill):

    MISS_CHANCE = 0.10
    STUN_CHANCE = 0.25

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        npc_name = get_npc_name(target, db)

        # --- 1. Miss check ---
        if random.random() < self.MISS_CHANCE:
            player.power -= self.power_cost
            player.health -= 30
            return {
                "message": f"You attempt to muster elemental forces against {npc_name} —"
                "and fail horribly!"
                "You take damage.",
                "killed":  False,
            }

        # --- 2. Deduct power ---
        player.power -= self.power_cost

        # --- 3. Damage ---
        int_bonus = max(0, (player.stats["INT"] - 10) // 3)
        damage    = random.randint(50, 80) + (int_bonus*5)

        new_health = target["current_health"] - damage
        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()

        if new_health <= 0:
            return {
                "message": wrap_text(
                    f"\nThe wrath of the elements smites {npc_name} "
                    f"for {damage} damage. They shudder and fall "
                    "as winds buffet them, fire falls from on high, "
                    "a torrent falls upon them, and the earth's maw "
                    "opens, as if nature itself rages against them!\n"
                ),
                "damage":    damage,
                "target_id": target["id"],
                "killed":    True,
            }

        else:
            msg = (
                f"The mightiest forces of nature buffet {npc_name} "
                f"for {damage} damage -- yet they still stand against you!"
            )

        return {
            "message":   msg,
            "damage":    damage,
            "target_id": target["id"],
            "killed":    False,
        }

