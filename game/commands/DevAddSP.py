# game/commands/DevAddSP

from game.commands.base import Command


class AddSPCommand(Command):
    def execute(self, player, db, args):
        try:
            amount = int(args[0]) if args else 10
        except (ValueError, IndexError):
            amount = 10

        db.execute(
            """
            UPDATE players
            SET power = power + ?
            WHERE id = ?
            """,
            (amount, player.id),
        )
        db.commit()

        # keep in-memory object in sync
        player.power += amount

        return f"Added {amount} SP. (Now {player.power}/{player.max_power})"
