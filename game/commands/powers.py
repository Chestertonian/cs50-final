# game/commands/powers.py
"""
Shows the player all skills/spells available to their guild,
grouped by level, with an indicator if they can use it yet.
"""

from game.commands.base import Command
from game.skills.registry import get_player_skills, ACTIVE_SKILLS, PASSIVE_SKILLS


class PowersCommand(Command):
    def execute(self, player, db, args):
        # Gather all skills for this guild from the DB directly,
        # so can show locked ones too .
        rows = db.execute(
            "SELECT * FROM skills WHERE guild = ? ORDER BY min_level, name",
            (player.guild,)
        ).fetchall()

        if not rows:
            return f"No powers are recorded for the {player.guild} guild."

        lines = [f"\n  Powers of the {player.guild.capitalize()} -- (your level: {player.level})\n"]
        lines.append(f"  {'Name':<22} {'Level':<8} {'Cost':<8} {'Type':<10} {'Status'}")
        lines.append("  " + "-" * 62)

        for row in rows:
            unlocked = player.level >= row["min_level"]
            status   = "known" if unlocked else f"unlocks at {row['min_level']}"
            ptype    = row["skill_type"]  # 'active' or 'passive'
            cost     = f"{row['power_cost']} pw" if row["power_cost"] > 0 else "free"

            # Dim locked spells with a marker
            marker = "  " if unlocked else "* "
            lines.append(
                f"{marker}{row['display_name']:<22} {row['min_level']:<8} {cost:<8} {ptype:<10} {status}"
            )

        lines.append("\n  * Not yet available")
        return "\n".join(lines)