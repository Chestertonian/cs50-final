from game.commands.base import Command

class AddMovementPointsCommand(Command):
    def execute(self, player, db, args):
        try:
            amount = int(args[0]) if args else 10
        except (ValueError, IndexError):
            amount = 10

        db.execute(
            """
            UPDATE players
            SET movement_points = movement_points + ?
            WHERE id = ?
            """,
            (amount, player.id),
        )
        db.commit()

        # keep in-memory object in sync
        player.movement_points += amount

        return f"Added {amount} movement points. (Now {player.movement_points}/{player.max_movement_points})"