"""
game/skills/active/mage_armor.py

Mage Armor: level 7 wizard spell.

A sustained arcane barrier that reduces ALL incoming damage by a
percentage for its duration. Stronger than Shield but longer
cooldown and higher cost. Stacks differently — Shield absorbs
flat damage per hit, Mage Armor reduces by percentage.

Stored as player.mage_armor_ticks_remaining and
player.mage_armor_reduction (a float, e.g. 0.20 = 20% reduction).

The combat loop should apply this after shield absorption:
    damage = int(damage * (1 - player.mage_armor_reduction))

Duration: 15 ticks.
Reduction: 20% of incoming damage.
Cost:     12 power.
"""

from game.skills.base import Skill


class MageArmor(Skill):

    DURATION_TICKS = 15
    REDUCTION      = 0.20

    def execute(self, player, target, db):
        player.power -= self.power_cost

        player.mage_armor_ticks_remaining = self.DURATION_TICKS
        player.mage_armor_reduction       = self.REDUCTION

        return {
            "message": (
                "Crackling arcane energy weaves itself around your body, "
                "forming a sustained magical armor."
            ),
            "killed": False,
        }
