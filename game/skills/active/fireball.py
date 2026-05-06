"""
game/skills/active/fireball.py

Fireball: level 10 wizard spell.

The wizard's signature spell. Hits ALL enemies in the room like
Arcane Pulse, but with dramatically higher damage and no disorient
— pure destruction. The fire is indiscriminate, pulling every NPC
in the room into combat just like Arcane Pulse does.

Damage: 8-20 base per target, +1 per 3 INT above 10.
Miss:   None — the explosion fills the room.
"""

import random
from game.skills.base import Skill

class Fireball(Skill):

    def execute(self, player, target, db):
        # --- 1. Fetch all living NPCs in the room ---
        npcs = db.execute(
            """SELECT npc_instances.*, npc_templates.name AS npc_name
               FROM npc_instances
               JOIN npc_templates ON npc_instances.template_id = npc_templates.id
               WHERE npc_instances.room_id = ?
               AND npc_instances.is_alive = 1""",
            (player.current_room_id,)
        ).fetchall()

        if not npcs:
            return {"message": "There is no one here to incinerate.", "killed": False}

        # --- 2. Deduct power ---
        player.power -= self.power_cost

        # --- 3. INT bonus ---
        int_bonus = max(0, (player.stats["INT"] - 10) // 3)

        lines      = [
            "You thrust your hands forward. A tiny bead of fire streaks outward —",
            "then ERUPTS into a roaring inferno!"
        ]
        any_killed = False
        killed_ids = []

        for npc in npcs:
            # Pull into combat.
            if npc["id"] not in player.combat.attacker_ids:
                player.combat.add_attacker(npc["id"])
                if not player.combat.is_in_combat():
                    player.combat.start_combat(npc["id"])

            damage     = random.randint(8, 20) + int_bonus
            new_health = npc["current_health"] - damage
            killed     = new_health <= 0

            db.execute(
                "UPDATE npc_instances SET current_health = ? WHERE id = ?",
                (new_health, npc["id"])
            )

            if killed:
                any_killed = True
                killed_ids.append(npc["id"])
                lines.append(f"  {npc['npc_name']} is engulfed in flames for {damage} damage and dies screaming!")
            else:
                lines.append(f"  {npc['npc_name']} is scorched for {damage} damage!")

        db.commit()

        return {
            "message":    "\n".join(lines),
            "killed":     any_killed,
            "killed_ids": killed_ids,
            "target_id":  player.combat.primary_target_id,
        }
