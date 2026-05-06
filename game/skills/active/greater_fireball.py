"""
game/skills/active/greater_fireball.py

Greater Fireball: level 15 wizard spell.

An intensified fireball of devastating power. Hits all enemies in
the room like Fireball, but with higher damage and a burn effect:
each surviving NPC takes a small additional tick of fire damage
next round (stored in result dict as a hook for your status system).

Primary damage:  14-32 base per target, +1 per 2 INT above 10.
Burn damage:     2-5 (applied next round — TODO: status system hook).
Miss:            None.
Cost:            25 power.
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
            "You draw deeply on your arcane reserves.",
            "A massive bead of fire erupts from your outstretched hand —",
            "the air itself ignites as it detonates in a cataclysmic inferno!",
        ]

        any_killed = False
        killed_ids = []
        burning_ids = []  # surviving NPCs that are now burning

        for npc in npcs:
            player.combat.start_combat(npc["id"])

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
                burn_damage = random.randint(2, 5)
                burning_ids.append({"id": npc["id"], "burn_damage": burn_damage})
                lines.append(
                    f"  {npc['npc_name']} is engulfed for {damage} damage and is burning!"
                )

        db.commit()

        return {
            "message":     "\n".join(lines),
            "killed":      any_killed,
            "killed_ids":  killed_ids,
            "target_id":   player.combat.primary_target_id,
            "burning_ids": burning_ids,
            # TODO: apply burn status to each entry in burning_ids so the
            # combat loop deals burn_damage to them next round.
        }
