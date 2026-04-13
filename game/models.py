# models.py, home to the loading, representation, and saving of various game entities. The purpose of this is to avoid constant raw SQL queries in the code later.
from game.helpers import wrap_text

class Room:
    def __init__(self, row):
        self.id = row["id"]
        self.name = row["name"]
        self.description = row["description"]
        self.area = row["area"]
        self.lighting = row["lighting"]
        self.smell = row["smell"]
        self.sound = row["sound"]
        self.movement_cost = row["movement_cost"]

    @staticmethod
    def get_by_id(db, room_id):
        row = db.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
        return Room(row) if row else None

    def get_exits(self, db):
        rows = db.execute(
            "SELECT direction, destination_room_id FROM exits WHERE room_id = ?;",
            (self.id,),
        ).fetchall()
        return rows

    def describe(self, db):
        exits = self.get_exits(db)
        exit_list = ", ".join([row["direction"] for row in exits]) or "none"
        wrapped_description = wrap_text(self.description)
        return (
            f"\n{self.name}\n"
            f"{'-' * len(self.name)}\n"
            "\n"
            f"{wrapped_description}\n"
            f"\nExits: {exit_list}\n"
        )


class Player:
    def __init__(self, row):
        self.id = row["id"]
        self.name = row["name"]
        self.race = row["race"]
        self.guild = row["guild"]
        self.gender = row["gender"]
        self.current_room_id = row["current_room_id"]
        self.health = row["health"]
        self.max_health = row["max_health"]
        self.level = row["level"]
        self.experience = row["experience"]
        self.stats = {
            "STR": row["str_stat"],
            "CON": row["con_stat"],
            "DEX": row["dex_stat"],
            "INT": row["int_stat"],
            "WIS": row["wis_stat"],
            "CHA": row["cha_stat"],
        }
        self.traits = row["traits"]

    @staticmethod
    def get_by_name(db, name):
        row = db.execute("SELECT * FROM players WHERE name = ?", (name,)).fetchone()
        return Player(row) if row else None

    def move(self, db, direction):
        row = db.execute(
            "SELECT * FROM exits WHERE direction = ? AND room_id = ?",
            (direction, self.current_room_id),
        ).fetchone()
        if row:
            self.current_room_id = row["destination_room_id"]
            db.execute(
                "UPDATE players SET current_room_id = ? WHERE id = ?",
                (row["destination_room_id"], self.id),
            )
            db.commit()
            return True
        else:
            return False

    def save(self, db):
        db.execute(
            """UPDATE players SET current_room_id = ?, health = ?,
            max_health = ?, level = ?, experience = ?, str_stat = ?,
            con_stat = ?, dex_stat = ?, int_stat = ?, wis_stat = ?,
            cha_stat = ?, traits = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?""",
            (
                self.current_room_id,
                self.health,
                self.max_health,
                self.level,
                self.experience,
                self.stats["STR"],
                self.stats["CON"],
                self.stats["DEX"],
                self.stats["INT"],
                self.stats["WIS"],
                self.stats["CHA"],
                self.traits,
                self.id,
            ),
        )
        db.commit()

    def get_current_room(self, db):
        return Room.get_by_id(db, self.current_room_id)
