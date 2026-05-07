"""
game/skills/active/invisibility.py

Invisibility: level 6 wizard spell.

Renders the player invisible for a number of ticks. While invisible:
  - Aggressive NPCs will not initiate combat against the player.

Stored as player.invisible_ticks_remaining (session-only).

Duration: 15 ticks.
Cost:     10 power.

Invisibility breaks immediately if the player:
  - Attacks (handled in combat_loop.py — call player.break_invisibility())
  - Casts an offensive spell (handle in each offensive spell's execute())
  - Is struck by an enemy
  
NOTE: This currently does *not* tick down.
"""

from game.skills.base import Skill


class Invisibility(Skill):

    DURATION_TICKS = 15

    def execute(self, player, target, db):
        player.power -= self.power_cost
        # Reset duration if already invisible.
        player.invisible_ticks_remaining = self.DURATION_TICKS

        return {
            "message": (
                "You weave a veil of magic around yourself. "
                "Your form shimmers and fades from sight."
            ),
            "killed": False,
        }
