# game/commands/health.py

from game.commands.base import Command

class HpCommand(Command):
    def execute(self, player, db, args):
        player.refresh(db)
        health=player.health
        max_health=player.max_health
        power=player.power
        max_power=player.max_power
        movement_points=player.movement_points
        max_movement_points=player.max_movement_points
        return(f"\nHP: {health}/{max_health} | SP: {power}/{max_power} | MP: {movement_points}/{max_movement_points}")
    