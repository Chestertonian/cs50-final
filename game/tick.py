import time
from game.spawner import run_spawns

# --- Configuration ---
TICK_INTERVAL = 20
HP_PER_TICK = 1
SP_PER_TICK = 1
MP_PER_TICK = 2
MAX_TICKS_AT_ONCE = 10


def process_ticks(player, db):
    now = time.time()
    run_spawns(db)
    row = db.execute(
        "SELECT last_tick_at FROM players WHERE id = ?",
        (player.id,)
    ).fetchone()

    last_tick_at = row["last_tick_at"]
    last_tick_at = float(last_tick_at) if last_tick_at is not None else now

    seconds_elapsed = now - last_tick_at
    ticks_due = int(seconds_elapsed // TICK_INTERVAL)

    if ticks_due <= 0:
        return None

    ticks_to_run = min(ticks_due, MAX_TICKS_AT_ONCE)

    player.health = min(player.health + ticks_to_run *
                        HP_PER_TICK, player.max_health)
    player.power = min(player.power + ticks_to_run *
                       SP_PER_TICK, player.max_power)
    player.movement_points = min(
        player.movement_points + ticks_to_run * MP_PER_TICK,
        player.max_movement_points
    )

    db.execute(
        """
        UPDATE players
        SET health = ?, power = ?, movement_points = ?, last_tick_at = ?
        WHERE id = ?
        """,
        (player.health, player.power, player.movement_points, now, player.id)
    )

    db.commit()
    return None
