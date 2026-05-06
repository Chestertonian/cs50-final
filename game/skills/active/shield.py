"""
game/skills/active/shield.py

Shield: level 5 wizard spell.

Conjures a magical barrier that absorbs a flat amount of incoming
damage for N ticks. Implemented as player.shield_ticks_remaining
and player.shield_absorption (damage absorbed per hit).

The combat loop should check player.shield_absorption before
applying damage to the player:
    if player.shield_absorption > 0:
        absorbed = min(damage, player.shield_absorption)
        damage -= absorbed
        player.shield_absorption -= absorbed

Duration: 10 ticks.
Absorbs:  3 damage per hit (flat, not percentage).
Cost:     8 power.
"""

from game.skills.base import Skill


class Shield(Skill):

    DURATION_TICKS  = 10
    ABSORPTION      = 3

    def execute(self, player, target, db):
        player.power -= self.power_cost

        player.shield_ticks_remaining = self.DURATION_TICKS
        player.shield_absorption      = self.ABSORPTION

        return {
            "message": (
                "A shimmering barrier of force springs up around you, "
                "ready to absorb incoming blows."
            ),
            "killed": False,
        }
