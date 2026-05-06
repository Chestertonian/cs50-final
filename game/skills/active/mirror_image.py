"""
game/skills/active/mirror_image.py

Mirror Image: level 8 wizard spell.

Creates 3 illusory duplicates of the wizard. Each time the player
would take damage in combat, check for images first:

    if player.mirror_images > 0:
        player.mirror_images -= 1
        print("An image of you shatters! The attack strikes a duplicate.")
        return  # skip damage application entirely

Images absorb one hit each, in order. Once all three are gone the
player takes damage normally. Casting again resets to 3 images
regardless of how many remain.

Add this check to the TOP of the NPC attack section in
run_combat_round(), before applying damage to the player.

Images: 3.
Cost:   12 power.
"""

from game.skills.base import Skill


class MirrorImage(Skill):

    IMAGE_COUNT = 3

    def execute(self, player, target, db):
        player.power -= self.power_cost

        player.mirror_images = self.IMAGE_COUNT

        return {
            "message": (
                "Three perfect illusory copies of yourself flicker into existence, "
                "moving in eerie unison around you."
            ),
            "killed": False,
        }
