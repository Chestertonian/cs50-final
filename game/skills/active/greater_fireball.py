"""
game/skills/active/greater_fireball.py

Greater Fireball: level 15 wizard spell.

An intensified fireball of devastating power.

Primary damage:  16-36 base per target, +1 per 2 INT above 10.
Miss:            None.
Cost:            40 power.
"""

import random
from game.skills.base import Skill
from game.helpers import get_npc_name


class GreaterFireball(Skill):

    def execute(self, player, target, db):
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

        player.power -= self.power_cost

        # Stronger INT scaling than regular Fireball.
        int_bonus = max(0, (player.stats["INT"] - 10) // 2)

        lines = [
            "\n"
            "You draw deeply on your arcane reserves.",
            "A massive bead of fire erupts from your outstretched hand —",
            "the air itself ignites as it detonates in a cataclysmic inferno!",
        ]

        any_killed = False
        killed_ids = []

        for npc in npcs:
            player.combat.start_combat(npc["id"], player)

            damage     = random.randint(14, 32) + int_bonus
            new_health = npc["current_health"] - damage
            killed     = new_health <= 0

            db.execute(
                "UPDATE npc_instances SET current_health = ? WHERE id = ?",
                (new_health, npc["id"])
            )

            if killed:
                any_killed = True
                killed_ids.append(npc["id"])
                lines.append(
                    f"  {npc['npc_name']} is consumed by the inferno for {damage} damage!"
                )
            else:
                lines.append(
                    f"  {npc['npc_name']} is engulfed for {damage} damage!"
                )

        db.commit()

        return {
            "message":     "\n".join(lines),
            "killed":      any_killed,
            "killed_ids":  killed_ids,
            "target_id":   player.combat.primary_target_id,
        }
