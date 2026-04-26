from game.commands.base import Command


class AddHealthPointsCommand(Command):
    def execute(self, player, db, args):
        try:
            amount = int(args[0]) if args else 10
        except (ValueError, IndexError):
            amount = 10

        db.execute(
            """
            UPDATE players
            SET health = health + ?
            WHERE id = ?
            """,
            (amount, player.id),
        )
        db.commit()

        # keep in-memory object in sync
        player.health += amount

        return f"Added {amount} health points. (Now {player.health}/{player.max_health})"
