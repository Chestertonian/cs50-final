# game/wealth.py
import random
from game.helpers import get_db


def get_wealth(player_id: int) -> int:
    """Return the player's current wealth balance."""
    db = get_db()
    row = db.execute("SELECT wealth FROM players WHERE id = ?",
                     (player_id,)).fetchone()
    return row["wealth"] if row else 0


def add_wealth(player_id: int, amount: int) -> int:
    """Add wealth to a player. Returns new balance."""
    db = get_db()
    db.execute("UPDATE players SET wealth = wealth + ? WHERE id = ?",
               (amount, player_id))
    db.commit()
    return get_wealth(player_id)


def spend_wealth(player_id: int, amount: int) -> bool:
    """
    Attempt to spend wealth. Returns True if successful, False if too poor.
    Doesn't go below 0.
    """
    db = get_db()
    current = get_wealth(player_id)
    if current < amount:
        return False
    db.execute("UPDATE players SET wealth = wealth - ? WHERE id = ?",
               (amount, player_id))
    db.commit()
    return True


def roll_npc_wealth(npc_template_id: int) -> int:
    """
    Roll how much wealth an NPC drops when killed.
    Returns 0 if the NPC has no wealth defined.
    """
    db = get_db()
    row = db.execute(
        "SELECT wealth_min, wealth_max FROM npc_templates WHERE id = ?",
        (npc_template_id,)
    ).fetchone()

    if not row or row["wealth_max"] == 0:
        return 0

    return random.randint(row["wealth_min"], row["wealth_max"])
