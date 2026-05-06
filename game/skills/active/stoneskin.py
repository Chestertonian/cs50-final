"""
game/skills/active/stoneskin.py

Stoneskin: level 17 wizard spell.

Hardens the wizard's skin to stone-like resilience. A much stronger
version of Mage Armor — higher reduction, longer duration, higher
cost. The two can stack: Mage Armor reduces damage first, then
Stoneskin reduces the remainder.

Combat loop application order (suggested):
    1. Shield absorption (flat)
    2. Mage Armor reduction (%)
    3. Stoneskin reduction (%)

Stored as player.stoneskin_ticks_remaining and
player.stoneskin_reduction.

Duration:  20 ticks.
Reduction: 30% of incoming damage.
Cost:      20 power.
"""

from game.skills.base import Skill


class Stoneskin(Skill):

    DURATION_TICKS = 20
    REDUCTION      = 0.30

    def execute(self, player, target, db):
        player.power -= self.power_cost

        player.stoneskin_ticks_remaining = self.DURATION_TICKS
        player.stoneskin_reduction       = self.REDUCTION

        return {
            "message": (
                "Your skin hardens and darkens, taking on the colour and "
                "weight of granite. You feel nearly impervious."
            ),
            "killed": False,
        }
