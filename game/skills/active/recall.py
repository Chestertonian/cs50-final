"""
game/skills/active/recall.py

Recall: wizard utility spell (level 11).

Teleports the player instantly to a fixed recall room — typically
the starting room or a guild hall. Cannot be used in combat.

Cost: 15 power.
"""

from game.skills.base import Skill

RECALL_ROOM_ID = 2 


class Recall(Skill):

    def execute(self, player, target, db):
        player.power -= self.power_cost
        player.current_room_id = RECALL_ROOM_ID
        db.execute(
            "UPDATE players SET current_room_id = ? WHERE id = ?",
            (RECALL_ROOM_ID, player.id)
        )
        db.commit()

        room = db.execute(
            "SELECT name FROM rooms WHERE id = ?",
            (RECALL_ROOM_ID,)
        ).fetchone()
        room_name = room["name"] if room else "somewhere familiar"

        return {
            "message": f"\nReality folds around you. You are standing in {room_name}.\n",
            "killed":  False,
            }
