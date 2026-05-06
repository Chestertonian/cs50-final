"""
game/skills/active/fire_bolt.py

Fire Bolt: level 4 wizard spell.

Damage: 4-7 base, +1 per 3 INT above 10.
Miss chance: 15% (reduced by DEX maybe, but keeping it simple for now).
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name


class FireBolt(Skill):

    MISS_CHANCE = 0.15  # 15% base miss chance

    def execute(self, player, target, db):
        if target is None:
            return {"message": "Cast at whom?", "killed": False}

        # --- 1. Miss check ---
        if random.random() < self.MISS_CHANCE:
            npc_name = get_npc_name(target, db)
            player.power -= self.power_cost
            return {
                "message": f"You hurl a bolt of fire at {npc_name}, but it scorches the air harmlessly.",
                "killed": False,
            }

        # --- 2. Deduct power ---
        player.power -= self.power_cost

        # --- 3. Calculate damage ---
        base_damage = random.randint(4, 7)
        int_bonus   = max(0, (player.stats["INT"] - 10) // 3)
        damage      = base_damage + int_bonus

        # --- 4. Apply damage ---
        new_health = target["current_health"] - damage
        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()

        # --- 5. Build message ---
        npc_name = get_npc_name(target, db)

        if new_health <= 0:
            msg = (
                f"A crackling bolt of fire slams into {npc_name} for {damage} damage. "
                f"It bursts into flames and collapses!"
            )
        else:
            msg = f"A crackling bolt of fire slams into {npc_name} for {damage} damage."

        return {
            "message":   msg,
            "damage":    damage,
            "target_id": target["id"],
            "killed":    new_health <= 0,
        }


