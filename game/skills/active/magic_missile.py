"""
game/skills/active/magic_missile.py
 
Magic Missile: level 1 wizard spell.
"""
 
import random
from game.skills.base import Skill
from game.helpers import get_npc_name
 
 
class MagicMissile(Skill):
    """
    Damage formula:
      base:  3-6
      bonus: +1 for every 4 points of INT above 10
              e.g. INT 14 → +1, INT 18 → +2
    """
 
    def execute(self, player, target, db):

        if target is None:
            return {"message": "Cast at whom?", "killed": False}
        # --- 1. Deduct power cost ---
        player.power -= self.power_cost
 
        # --- 2. Calculate damage ---
        base_damage = random.randint(3, 6)
        int_bonus   = max(0, (player.stats["INT"] - 10) // 4)
        damage      = base_damage + int_bonus
 
        # --- 3. Apply damage to NPC ---
        new_health = target["current_health"] - damage
        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, target["id"])
        )
        db.commit()
 
        # --- 4. Build feedback message ---
        npc_name = get_npc_name(target, db)
 
        if new_health <= 0:
            msg = (
                f"A bolt of arcane energy surges from your hand, "
                f"striking {npc_name} for {damage} damage. It collapses!"
            )
        else:
            msg = (
                f"A bolt of arcane energy surges from your hand, "
                f"striking {npc_name} for {damage} damage."
            )
 
        return {
            "message":    msg,
            "damage":     damage,
            "target_id":  target["id"],
            "killed":     new_health <= 0,
        }
 
 
