"""
game/skills/active/swift_feet.py

Swift Feet: level 18 wizard spell.

Restores movement points.

Restore amount: 20 + WIS bonus (+1 per 4 WIS above 10).
Cannot exceed max_movement_points.
Cost: 10 power.
"""

from game.skills.base import Skill


class SwiftFeet(Skill):

    def execute(self, player, target, db):
        if player.movement_points >= player.max_movement_points:
            return {
                "message": "Your feet are already as swift as they can be.",
                "killed":  False,
            }

        player.power -= self.power_cost

        wis_bonus = max(0, (player.stats["WIS"] - 10) // 4)
        restore   = 20 + wis_bonus

        player.movement_points = min(
            player.movement_points + restore,
            player.max_movement_points
        )

        db.execute(
            "UPDATE players SET movement_points = ? WHERE id = ?",
            (player.movement_points, player.id)
        )
        db.commit()

        return {
            "message": (
                f"A tingling energy fills your legs. You feel fleet-footed and ready to run. "
                f"({player.movement_points}/{player.max_movement_points})"
            ),
            "killed": False,
        }
