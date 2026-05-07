# game/spawner.py

import time
import sqlite3


def run_spawns(db: sqlite3.Connection) -> None:
    """Check all spawn rules and create new instances where needed."""
    now = time.time()
    _spawn_items(db, now)
    _spawn_npcs(db, now)


def _spawn_items(db: sqlite3.Connection, now: float) -> None:
    spawn_rules = db.execute("SELECT * FROM item_spawns").fetchall()

    for rule in spawn_rules:
        # Count how many instances of template are currently in this room
        current_count = db.execute("""
            SELECT COUNT(*)
            FROM item_instances ii
            JOIN item_locations il ON il.instance_id = ii.id
            WHERE ii.template_id = ?
              AND il.room_id = ?
        """, (rule["template_id"], rule["room_id"])).fetchone()[0]

        time_since_last = now - (rule["last_spawn_at"] or 0)
        ready_to_spawn = current_count < rule["max_count"] and time_since_last >= rule["respawn_time"]

        if ready_to_spawn:
            # Create the instance
            cursor = db.execute(
                "INSERT INTO item_instances (template_id) VALUES (?)",
                (rule["template_id"],)
            )
            new_instance_id = cursor.lastrowid

            # Handle torch sub-table if needed
            template = db.execute(
                "SELECT item_type FROM item_templates WHERE id = ?",
                (rule["template_id"],)
            ).fetchone()

            if template["item_type"] == "torch":
                default_burn = db.execute(
                    "SELECT default_burn_time FROM item_torch_templates WHERE template_id = ?",
                    (rule["template_id"],)
                ).fetchone()["default_burn_time"]
                db.execute(
                    "INSERT INTO item_torch_instances (instance_id, burn_time) VALUES (?, ?)",
                    (new_instance_id, default_burn)
                )

            # Place it in the room
            db.execute(
                "INSERT INTO item_locations (instance_id, room_id) VALUES (?, ?)",
                (new_instance_id, rule["room_id"])
            )

            # Update last_spawn_at
            db.execute(
                "UPDATE item_spawns SET last_spawn_at = ? WHERE id = ?",
                (now, rule["id"])
            )

    db.commit()


def _spawn_npcs(db: sqlite3.Connection, now: float) -> None:
    spawn_rules = db.execute("SELECT * FROM npc_spawns").fetchall()

    for rule in spawn_rules:
        # Count alive instances of this template in this room
        current_count = db.execute("""
            SELECT COUNT(*)
            FROM npc_instances
            WHERE template_id = ?
              AND room_id = ?
              AND is_alive = 1
        """, (rule["template_id"], rule["room_id"])).fetchone()[0]

        time_since_last = now - (rule["last_spawn_at"] or 0)
        ready_to_spawn = current_count < rule["max_count"] and time_since_last >= rule["respawn_delay"]

        if ready_to_spawn:
            template = db.execute(
                "SELECT max_health FROM npc_templates WHERE id = ?",
                (rule["template_id"],)
            ).fetchone()

            db.execute("""
                INSERT INTO npc_instances (template_id, room_id, current_health, home_room_id)
                VALUES (?, ?, ?, ?)
            """, (rule["template_id"], rule["room_id"], template["max_health"], rule["room_id"]))

            db.execute(
                "UPDATE npc_spawns SET last_spawn_at = ? WHERE id = ?",
                (now, rule["id"])
            )

    db.commit()
