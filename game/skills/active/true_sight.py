"""
game/skills/active/true_sight.py

True Sight: level 6 wizard spell.

Grants the ability to see through illusions and darkness. While
active, two things happen:
  1. Dark rooms are described normally (same as having a light source).
  2. Invisible NPCs or players become visible.

Stored as player.true_sight_ticks_remaining.

Your room describe() and invisibility checks should treat
true_sight_ticks_remaining > 0 the same as light_ticks_remaining > 0
for lighting, and should reveal invisible entities when describing
the room.

Duration: 12 ticks.
Cost:     10 power.
"""

from game.skills.base import Skill


class TrueSight(Skill):

    DURATION_TICKS = 12

    def execute(self, player, target, db):
        player.power -= self.power_cost

        player.true_sight_ticks_remaining = self.DURATION_TICKS

        return {
            "message": (
                "Your eyes gleam with silver light. Shadows thin, "
                "illusions fray, and hidden things are laid bare."
            ),
            "killed": False,
        }
