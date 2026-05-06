"""
game/skills/active/flame_shield.py

Flame Shield: level 10 wizard spell.

Wraps the wizard in fire that burns attackers. Each time the player
is hit while Flame Shield is active, the attacker takes reflected
fire damage.

Stored as player.flame_shield_ticks_remaining and
player.flame_shield_damage (damage reflected per hit).

The combat loop should check after each NPC attack lands:
    if player.flame_shield_ticks_remaining > 0:
        reflect = random.randint(*player.flame_shield_damage)
        npc.current_health -= reflect
        print(f"The flames around you scorch {npc.name} for {reflect} damage!")

Duration:        10 ticks.
Reflect damage:  2-5 per hit.
Cost:            15 power.
"""

from game.skills.base import Skill


class FlameShield(Skill):

    DURATION_TICKS  = 10
    REFLECT_MIN     = 2
    REFLECT_MAX     = 5

    def execute(self, player, target, db):
        player.power -= self.power_cost

        player.flame_shield_ticks_remaining = self.DURATION_TICKS
        player.flame_shield_damage          = (self.REFLECT_MIN, self.REFLECT_MAX)

        return {
            "message": (
                "Sheets of magical fire erupt around your body. "
                "Anyone who strikes you will burn."
            ),
            "killed": False,
        }
