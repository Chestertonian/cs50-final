"""
game/skills/active/arcane_pulse.py

Arcane Pulse: level 4 wizard spell.

Hits ALL living NPCs in the room simultaneously. Any NPC struck that
isn't already fighting the player gets pulled into combat.

Damage:    2-5 base per target, +1 per 4 INT above 10.
Disorient: 35% chance per target. (Currently meaningless)
"""

import random
from game.skills.base import Skill


class ArcanePulse(Skill):

    DISORIENT_CHANCE = 0.35

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
            return {"message": "There is no one here to strike.", "killed": False}

        # --- 2. Deduct power ---
        player.power -= self.power_cost

        # --- 3. Calculate INT bonus (same for all targets) ---
        int_bonus = max(0, (player.stats["INT"] - 10) // 4)

        lines      = ["A pulse of arcane energy erupts outward from your hands!"]
        any_killed = False
        killed_ids = []

        for npc in npcs:
            # Pull into combat if not already fighting player.
            player.combat.start_combat(npc["id"], player)

            damage     = random.randint(2, 5) + int_bonus
            new_health = npc["current_health"] - damage
            killed     = new_health <= 0
            disoriented = (not killed) and (random.random() < self.DISORIENT_CHANCE)

            db.execute(
                "UPDATE npc_instances SET current_health = ? WHERE id = ?",
                (new_health, npc["id"])
            )

            if killed:
                any_killed = True
                killed_ids.append(npc["id"])
                lines.append(f"  {npc['npc_name']} takes {damage} damage and collapses!")
            elif disoriented:
                lines.append(f"  {npc['npc_name']} takes {damage} damage and looks disoriented!")
            else:
                lines.append(f"  {npc['npc_name']} takes {damage} damage.")

        db.commit()

        return {
            "message":    "\n".join(lines),
            "killed":     any_killed,
            "killed_ids": killed_ids,
            "target_id":  player.combat.primary_target_id,
        }