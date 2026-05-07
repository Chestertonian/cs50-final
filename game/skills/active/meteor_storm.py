"""
game/skills/active/meteor_storm.py

Meteor Storm: level 20 wizard spell. Capstone.

Calls down a cataclysmic rain of meteors on every enemy in the
room. Three waves of impacts, each rolled independently per target.
The most powerful spell in the wizard's arsenal.

Per wave per target: 10-13 damage, +1 per 2 INT above 10.
Waves:              3.
Miss:               None.
Cost:               40 power.
"""

import random
from game.skills.base import Skill

WAVES = 3


class MeteorStorm(Skill):

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
            return {"message": "There is no one here to destroy.", "killed": False}

        player.power -= self.power_cost

        int_bonus = max(0, (player.stats["INT"] - 10) // 2)

        lines = [
            "\nYou raise both hands to the heavens and speak the ancient words.",
            "The sky tears open. Streaks of fire scream downward —",
            "METEOR STORM!",
            "",
        ]

        any_killed = False
        killed_ids = []

        # Track current health per NPC across waves.
        health_map = {npc["id"]: npc["current_health"] for npc in npcs}
        name_map   = {npc["id"]: npc["npc_name"] for npc in npcs}

        for wave in range(1, WAVES + 1):
            lines.append(f"  Wave {wave}:")
            for npc in npcs:
                npc_id = npc["id"]
                if health_map[npc_id] <= 0:
                    continue  # already dead
                damage              = random.randint(10, 13) + int_bonus
                health_map[npc_id] -= damage
                if health_map[npc_id] <= 0:
                    lines.append(f"    {name_map[npc_id]} is struck for {damage} damage and obliterated!")
                else:
                    lines.append(f"    {name_map[npc_id]} is struck for {damage} damage.")

        # Commit all final health values.
        for npc_id, hp in health_map.items():
            db.execute(
                "UPDATE npc_instances SET current_health = ? WHERE id = ?",
                (hp, npc_id)
            )
            if hp <= 0:
                any_killed = True
                killed_ids.append(npc_id)
                player.combat.start_combat(npc_id, player)  # ensure they're in combat for death handling

        db.commit()

        return {
            "message":    "\n".join(lines),
            "killed":     any_killed,
            "killed_ids": killed_ids,
            "target_id":  player.combat.primary_target_id,
        }
