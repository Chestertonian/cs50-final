# game/commands/score.py
# Display player info.

from game.commands.base import Command


class ScoreCommand(Command):
    def execute(self, player, db, args):
        border = "═" * 47
        player.refresh(db)
        stats = player.stats
        room = player.get_current_room(db)
        return (
            f"\n{border}\n"
            f"  {player.name:<28} Level {player.level} {player.guild.capitalize()}\n"
            f"  Race: {player.race.capitalize():<22} Gender: {player.gender.capitalize()}\n"
            f"{border}\n"
            f"\n  Health:  {player.health}/{player.max_health}\n"
            f"  Power:  {player.power}/{player.max_power}\n"
            f"  Movement:  {player.movement_points}/{player.max_movement_points}\n"
            f"\n  Area: {room.area.title()}\n"
            f"\n  STR: {stats['STR']:>2}        INT: {stats['INT']:>2}\n"
            f"  DEX: {stats['DEX']:>2}        WIS: {stats['WIS']:>2}\n"
            f"  CON: {stats['CON']:>2}        CHA: {stats['CHA']:>2}\n"
            f"\n{border}\n"
            f"\n  Experience: {player.experience}\n"
            f"\n{border}\n"
        )
