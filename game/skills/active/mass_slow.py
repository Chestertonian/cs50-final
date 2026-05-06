"""
game/skills/active/mass_slow.py

Mass Slow: level 19 wizard spell.

Applies Slow to every living NPC in the room simultaneously.
Uses the same player.slowed_npcs dict as Slow — just populates
it for every target at once.

Skip chance per NPC per round: 40%.
Duration:  8 ticks per NPC.
Cost:      28 power.
"""

from game.skills.base import Skill

DURATION_TICKS = 8


class MassSlow(Skill):

    def execute(self, player, target, db):
        npcs = db.execute(
            """SELECT npc_instances.id, npc_templates.name AS npc_name
               FROM npc_instances
               JOIN npc_templates ON npc_instances.template_id = npc_templates.id
               WHERE npc_instances.room_id = ?
               AND npc_instances.is_alive = 1""",
            (player.current_room_id,)
        ).fetchall()

        if not npcs:
            return {"message": "There is no one here to slow.", "killed": False}

        player.power -= self.power_cost

        if not hasattr(player, "slowed_npcs"):
            player.slowed_npcs = {}

        names = []
        for npc in npcs:
            player.slowed_npcs[npc["id"]] = DURATION_TICKS
            names.append(npc["npc_name"])

        targets_str = ", ".join(names)
        return {
            "message": (
                f"Time itself seems to thicken. "
                f"{targets_str} struggle against an invisible weight."
            ),
            "killed": False,
        }
