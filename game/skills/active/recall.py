"""
game/skills/active/recall.py

Recall: wizard utility spell (level TBD).

Teleports the player instantly to a fixed recall room — typically
the starting room or a guild hall. Cannot be used in combat.

RECALL_ROOM_ID should match wherever you want wizards to return to.
Currently set to 1 (the default starting room) — change this to
your wizard guild hall room ID once it exists.

Cost: 15 power.
"""

from game.skills.base import Skill

RECALL_ROOM_ID = 1  # TODO: update to wizard guild hall room ID


class Recall(Skill):

    def execute(self, player, target, db):
        # Cannot recall mid-combat.
        if player.combat.is_in_combat():
            return {
                "message": "You cannot recall while in combat.",
                "killed":  False,
            }

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
            "message": f"Reality folds around you. You are standing in {room_name}.",
            "killed":  False,
            "recalled": True,  # engine can use this to trigger a room describe()
        }
