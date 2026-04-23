# models.py, home to the loading, representation, and saving of various game entities. The purpose of this is to avoid constant raw SQL queries in the code later.
from game.helpers import wrap_text  # pyright: ignore[reportMissingImports]


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

    def get_visible_exits(self, db):
        rows = db.execute(
            "SELECT direction, destination_room_id FROM exits WHERE room_id = ? AND secret=0;",
            (self.id,),
        ).fetchall()
        return rows

    def describe(self, db):
        direction_order = {
            "north": 0,
            "northeast": 1,
            "east": 2,
            "southeast": 3,
            "south": 4,
            "southwest": 5,
            "west": 6,
            "northwest": 7,
            "up": 8,
            "down": 9,
        }
        exits = self.get_visible_exits(db)

        sorted_exits = sorted(
            exits, key=lambda row: direction_order.get(row["direction"], 99)
        )

        exit_list = ", ".join(row["direction"] for row in sorted_exits) or "none"
        wrapped_description = wrap_text(self.description)

        # Fetch items on the floor of this room
        items = Item.get_items_in_room(self.id, db)
        if items:
            item_names = ".\n".join(item.name.capitalize() for item in items)
            items_line = f"\n{item_names}.\n"
        else:
            items_line = ""
        npcs = NpcInstance.get_instances_in_room(self.id, db)
        if npcs:
            npc_lines = ".\n".join(npc.name.capitalize() for npc in npcs)
            npcs_line = f"\n{npc_lines}.\n"
        else:
            npcs_line = ""

        return (
            f"\n{self.name}\n"
            f"{'-' * len(self.name)}\n"
            "\n"
            f"{wrapped_description}\n"
            f"{items_line}"
            f"{npcs_line}"
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
        self.power = row["power"]
        self.max_power = row["max_power"]
        self.movement_points = row["movement_points"]
        self.max_movement_points = row["max_movement_points"]
        self.level = row["level"]
        self.experience = row["experience"]
        self.wealth = row["wealth"]
        self.stats = {
            "STR": row["str_stat"],
            "CON": row["con_stat"],
            "DEX": row["dex_stat"],
            "INT": row["int_stat"],
            "WIS": row["wis_stat"],
            "CHA": row["cha_stat"],
        }
        self.traits = row["traits"]

    def refresh(self, db):
        row = db.execute("SELECT * FROM players WHERE id = ?", (self.id,)).fetchone()
        self.__init__(row)

    @staticmethod
    def get_by_name(db, name):
        row = db.execute("SELECT * FROM players WHERE name = ?", (name,)).fetchone()
        return Player(row) if row else None

    def move(self, db, direction):
        if self.movement_points <= 0:
            print("You are too exhausted to move.")
            return False

        row = db.execute(
            "SELECT * FROM exits WHERE direction = ? AND room_id = ?",
            (direction, self.current_room_id),
        ).fetchone()

        if not row:
            return False

        if row["locked"]:
            key_id = row["key_template_id"]
            if key_id is None:
                print("The door is locked.")
                return False

            # Check if player is carrying the right key
            key = db.execute(
                """
                SELECT 1 FROM item_instances ii
                JOIN item_locations il ON ii.id = il.instance_id
                WHERE il.player_id = ?
                AND ii.template_id = ?
                """,
                (self.id, key_id),
            ).fetchone()

            if not key:
                print("The door is locked.")
                return False
            print("You unlock the door.")
        # optional: use room movement cost (fallback to 1 if None)
        cost = 1  # later you can replace with room-based cost

        if self.movement_points < cost:
            print("You don't have enough movement points.")
            return False

        new_room = row["destination_room_id"]

        db.execute(
            """
            UPDATE players
            SET current_room_id = ?,
                movement_points = movement_points - ?
            WHERE id = ?
            """,
            (new_room, cost, self.id),
        )
        db.commit()

        # keep object in sync
        self.current_room_id = new_room
        self.movement_points -= cost

        return True

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


# Largely AI-written. Edited by Luke Kuruvilla.


class Item:
    """
    Represents a single physical item instance in the game world.
    Combines data from item_instances, item_templates, and the
    type-specific template table (e.g. item_weapon_templates).
    """

    def __init__(self, instance_id: int, db):
        """
        Load all relevant data for this item from the database.
        Raises a ValueError if the instance doesn't exist.
        """
        self.db = db
        self.instance_id = instance_id

        # 1. Loads the base instance row.
        instance = db.execute(
            "SELECT * FROM item_instances WHERE id = ?", (instance_id,)
        ).fetchone()

        if instance is None:
            raise ValueError(f"No item instance with id={instance_id}")

        self.template_id = instance["template_id"]
        self.created_at = instance["created_at"]

        # 2. Loads the base template row.
        template = db.execute(
            "SELECT * FROM item_templates WHERE id = ?", (self.template_id,)
        ).fetchone()

        if template is None:
            raise ValueError(f"No item template with id={self.template_id}")

        self.name = template["name"]
        self.description = template["description"]
        self.item_type = template[
            "item_type"
        ]  # examples: 'weapon','armor','torch','food','treasure','container'
        self.weight = template["weight"]
        self.value = template["value"]
        self.is_takeable = bool(template["is_takeable"])
        self.is_droppable = bool(template["is_droppable"])

        # 3. Load the type-specific template row. Currently, this just returns 'Torch.'
        self.type_data = self._load_type_data()

        # 4. Load location.
        self._load_location()

    # PRIVATE HELPERS

    def _load_type_data(self) -> dict | None:
        """
        Load the type-specific template row and return it as a plain dict.
        Returns None for item types that have no extra table (e.g. 'treasure').
        """
        table_map = {
            "weapon": "item_weapon_templates",
            "armor": "item_armor_templates",
            "torch": "item_torch_templates",
            "food": "item_food_templates",
            "container": "item_container_templates",
        }

        table = table_map.get(self.item_type)
        if table is None:
            return None  # e.g. 'treasure' has no extra table

        row = self.db.execute(
            f"SELECT * FROM {table} WHERE template_id = ?", (self.template_id,)
        ).fetchone()

        # Convert sqlite3.Row to dict so can do type_data["damage_min"] etc.
        return dict(row) if row else None

    def _load_location(self):
        """
        Populate room_id, player_id, npc_id, and equipped_slot
        from the item_locations table.
        All four default to None if there's no location row yet.
        """
        row = self.db.execute(
            "SELECT * FROM item_locations WHERE instance_id = ?", (self.instance_id,)
        ).fetchone()

        if row:
            self.room_id = row["room_id"]
            self.player_id = row["player_id"]
            self.npc_id = row["npc_id"]
            self.equipped_slot = row["equipped_slot"]
        else:
            self.room_id = None
            self.player_id = None
            self.npc_id = None
            self.equipped_slot = None

    def _update_location(
        self, room_id=None, player_id=None, npc_id=None, equipped_slot=None
    ):
        """
        Internal: upsert item_locations for this instance.
        Exactly one of room_id / player_id / npc_id must be non-None
        (enforced by the DB CHECK constraint, but we also check here).
        """
        non_null = sum(x is not None for x in [room_id, player_id, npc_id])
        if non_null != 1:
            raise ValueError("Exactly one of room_id, player_id, npc_id must be set.")

        self.db.execute(
            """
            INSERT INTO item_locations (instance_id, room_id, player_id, npc_id, equipped_slot)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(instance_id) DO UPDATE SET
                room_id       = excluded.room_id,
                player_id     = excluded.player_id,
                npc_id        = excluded.npc_id,
                equipped_slot = excluded.equipped_slot
        """,
            (self.instance_id, room_id, player_id, npc_id, equipped_slot),
        )
        self.db.commit()

        # Mirror the change onto self so callers see fresh data immediately
        self.room_id = room_id
        self.player_id = player_id
        self.npc_id = npc_id
        self.equipped_slot = equipped_slot

    # ════════════════════════════════════════════════════════════════════
    # FACTORY / CLASS-LEVEL QUERIES
    # ════════════════════════════════════════════════════════════════════

    @classmethod
    def from_db(cls, instance_id: int, db) -> "Item":
        """
        Friendly factory method. Same as Item(instance_id, db)
        but reads more naturally in calling code:
            sword = Item.from_db(7, db)
        """
        return cls(instance_id, db)

    @classmethod
    def get_items_in_room(cls, room_id: int, db) -> list["Item"]:
        """
        Return a list of all Item objects currently located in room_id.
        """
        rows = db.execute(
            """
            SELECT il.instance_id
            FROM item_locations il
            WHERE il.room_id = ?
        """,
            (room_id,),
        ).fetchall()

        return load_items([row["instance_id"] for row in rows], db)

    @classmethod
    def get_items_for_player(cls, player_id: int, db) -> list["Item"]:
        """
        Return all items carried by player_id (equipped or not).
        """
        rows = db.execute(
            """
            SELECT il.instance_id
            FROM item_locations il
            WHERE il.player_id = ?
        """,
            (player_id,),
        ).fetchall()

        return load_items([row["instance_id"] for row in rows], db)

    @classmethod
    def get_equipped_items(cls, player_id: int, db) -> list["Item"]:
        # Return only the items that player_id currently has equipped.
        rows = db.execute(
            """
            SELECT il.instance_id
            FROM item_locations il
            WHERE il.player_id = ? AND il.equipped_slot IS NOT NULL
        """,
            (player_id,),
        ).fetchall()

        return load_items([row["instance_id"] for row in rows], db)

    @classmethod
    def create_instance(
        cls, template_id: int, db, room_id=None, player_id=None, npc_id=None
    ) -> "Item":
        """
        Create a brand-new item instance from a template and place it
        in a room, player inventory, or NPC inventory.

        Also creates the torch instance row if the template is a torch.
        Returns the newly created Item object.
        """
        # Insert into item_instances
        cursor = db.execute(
            "INSERT INTO item_instances (template_id) VALUES (?)", (template_id,)
        )
        db.commit()
        new_id = cursor.lastrowid

        # Determine item type so we know if we need a torch row
        template = db.execute(
            "SELECT item_type FROM item_templates WHERE id = ?", (template_id,)
        ).fetchone()

        if template and template["item_type"] == "torch":
            # Pull default burn time from torch template
            torch_tmpl = db.execute(
                "SELECT default_burn_time FROM item_torch_templates WHERE template_id = ?",
                (template_id,),
            ).fetchone()
            burn_time = torch_tmpl["default_burn_time"] if torch_tmpl else 100

            db.execute(
                "INSERT INTO item_torch_instances (instance_id, burn_time, is_lit) VALUES (?, ?, 0)",
                (new_id, burn_time),
            )
            db.commit()

        # Place the item somewhere (optional at creation time)
        if any(x is not None for x in [room_id, player_id, npc_id]):
            item = cls(new_id, db)
            item._update_location(room_id=room_id, player_id=player_id, npc_id=npc_id)
        else:
            item = cls(new_id, db)

        return item

    # ════════════════════════════════════════════════════════════════════
    # MOVEMENT METHODS
    # ════════════════════════════════════════════════════════════════════

    def move_to_room(self, room_id: int):
        """Drop this item into a room (unequips it automatically)."""
        self._update_location(room_id=room_id)

    def move_to_player(self, player_id: int):
        """Put this item in a player's inventory (not yet equipped)."""
        self._update_location(player_id=player_id)

    def move_to_npc(self, npc_id: int):
        """Give this item to an NPC."""
        self._update_location(npc_id=npc_id)

    # ════════════════════════════════════════════════════════════════════
    # EQUIP / UNEQUIP
    # ════════════════════════════════════════════════════════════════════

    def equip(self, slot: str):
        """
        Equip this item to the given slot.
        Item must already be in a player's inventory (player_id set).
        Raises ValueError if the item isn't carried by a player,
        or if the item type doesn't support the slot.
        """
        if self.player_id is None:
            raise ValueError("Cannot equip an item that isn't in a player's inventory.")

        # Basic slot validation
        valid_slots = {"head", "body", "hands", "feet", "weapon"}
        if slot not in valid_slots:
            raise ValueError(f"'{slot}' is not a valid equipment slot.")

        self.db.execute(
            """
            UPDATE item_locations
            SET equipped_slot = ?
            WHERE instance_id = ?
        """,
            (slot, self.instance_id),
        )
        self.db.commit()
        self.equipped_slot = slot

    def unequip(self):
        """Remove this item from its equipped slot (stays in inventory)."""
        self.db.execute(
            """
            UPDATE item_locations
            SET equipped_slot = NULL
            WHERE instance_id = ?
        """,
            (self.instance_id,),
        )
        self.db.commit()
        self.equipped_slot = None

    @property
    def is_equipped(self) -> bool:
        return self.equipped_slot is not None

    @property
    def location_description(self) -> str:
        """Human-readable location string, useful for debugging."""
        if self.room_id:
            return f"room {self.room_id}"
        if self.player_id:
            slot = f", equipped in {self.equipped_slot}" if self.equipped_slot else ""
            return f"player {self.player_id}{slot}"
        if self.npc_id:
            return f"npc {self.npc_id}"
        return "nowhere"

    def __repr__(self) -> str:
        return (
            f"<Item id={self.instance_id} '{self.name}' "
            f"type={self.item_type} @ {self.location_description}>"
        )


class Torch(Item):
    """
    A specialised Item with behavior for a torch.
    """

    def __init__(self, instance_id: int, db):
        super().__init__(
            instance_id, db
        )  # runs the init for Item, calling it from its superclass
        self.torch_state = self._load_torch_state()

    def _load_torch_state(
        self,
    ) -> dict | None:  # should return a dictionary or else none
        row = self.db.execute(
            "SELECT * FROM item_torch_instances WHERE instance_id = ?",
            (self.instance_id,),
        ).fetchone()
        return dict(row) if row else None

    def light(self):
        # method for lighting torch, checking if it's lit, etc.
        if self.torch_state["is_lit"]:
            raise ValueError(f"'{self.name}' is already lit.")
        if self.torch_state["burn_time"] <= 0:
            raise ValueError(f"'{self.name}' has burned out and cannot be relit.")
        self.db.execute(
            "UPDATE item_torch_instances SET is_lit = 1 WHERE instance_id = ?",
            (self.instance_id,),
        )
        self.db.commit()
        self.torch_state["is_lit"] = 1

    def douse(self):
        if not self.torch_state["is_lit"]:
            raise ValueError(f"'{self.name}' is not lit.")
        self.db.execute(
            "UPDATE item_torch_instances SET is_lit = 0 WHERE instance_id = ?",
            (self.instance_id,),
        )
        self.db.commit()
        self.torch_state["is_lit"] = 0

    def tick_burn(self) -> bool:
        # when ticks are implemented, this will be used
        if not self.torch_state["is_lit"]:
            return False
        new_time = max(0, self.torch_state["burn_time"] - 1)
        self.db.execute(
            "UPDATE item_torch_instances SET burn_time = ? WHERE instance_id = ?",
            (new_time, self.instance_id),
        )
        self.torch_state["burn_time"] = new_time
        if new_time == 0:
            self.douse()
            return True
        self.db.commit()
        return False


class NpcTemplate:
    """
    The blueprint for an NPC type — shared data that never changes per-instance.
    e.g. "Goblin Scout" with its description, stats, and dialogue.
    """

    def __init__(self, row):
        self.id = row["id"]
        self.name = row["name"]
        self.description = row["description"]
        self.max_health = row["max_health"]
        self.is_aggressive = bool(row["is_aggressive"])

    @staticmethod
    def get_by_id(db, template_id):
        row = db.execute(
            "SELECT * FROM npc_templates WHERE id = ?", (template_id,)
        ).fetchone()
        return NpcTemplate(row) if row else None

    def __repr__(self):
        return f"<NpcTemplate id={self.id} '{self.name}'>"


class NpcInstance:
    """
    A physical NPC living in the world — a specific copy of a template,
    placed in a room with its own current health and alive/dead state.
    """

    def __init__(self, row, db):
        self.id = row["id"]
        self.template_id = row["template_id"]
        self.room_id = row["room_id"]
        self.current_health = row["current_health"]
        self._is_alive = bool(row["is_alive"])

        # Load the template so we can access name, description, etc. directly
        self.template = NpcTemplate.get_by_id(db, self.template_id)
        if self.template is None:
            raise ValueError(f"No NPC template found for id={self.template_id}")

        # Shortcuts so callers can do npc.name instead of npc.template.name
        self.name = self.template.name
        self.description = self.template.description
        self.max_health = self.template.max_health
        self.is_aggressive = self.template.is_aggressive

    # ── Properties ──────────────────────────────────────────────────────

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    # ── Factory / class-level queries ───────────────────────────────────

    @staticmethod
    def get_by_id(db, instance_id):
        row = db.execute(
            "SELECT * FROM npc_instances WHERE id = ?", (instance_id,)
        ).fetchone()
        return NpcInstance(row, db) if row else None

    @classmethod
    def get_instances_in_room(cls, room_id: int, db) -> list["NpcInstance"]:
        """Return all living NPC instances currently in a given room."""
        rows = db.execute(
            "SELECT * FROM npc_instances WHERE room_id = ? AND is_alive = 1",
            (room_id,),
        ).fetchall()
        return [cls(row, db) for row in rows]

    @classmethod
    def create_instance(cls, template_id: int, room_id: int, db) -> "NpcInstance":
        """
        Spawn a new NPC instance from a template into a room.
        Sets current_health to the template's max_health automatically.
        """
        template = NpcTemplate.get_by_id(db, template_id)
        if template is None:
            raise ValueError(f"No NPC template with id={template_id}")

        cursor = db.execute(
            """
            INSERT INTO npc_instances (template_id, room_id, current_health, is_alive)
            VALUES (?, ?, ?, 1)
            """,
            (template_id, room_id, template.max_health),
        )
        db.commit()
        return cls.get_by_id(db, cursor.lastrowid)

    # ── Actions ─────────────────────────────────────────────────────────

    def take_damage(self, amount: int, db) -> bool:
        """
        Deal damage to this NPC. Returns True if the NPC died, False otherwise.
        """
        if not self.is_alive:
            raise ValueError(f"{self.name} is already dead.")

        new_health = max(0, self.current_health - amount)

        db.execute(
            "UPDATE npc_instances SET current_health = ? WHERE id = ?",
            (new_health, self.id),
        )
        db.commit()
        self.current_health = new_health

        if new_health == 0:
            self._kill(db)
            return True

        return False

    def _kill(self, db):
        """Mark this NPC as dead in the database."""
        db.execute("UPDATE npc_instances SET is_alive = 0 WHERE id = ?", (self.id,))
        db.commit()
        self._is_alive = False

    def move_to_room(self, room_id: int, db):
        """Move this NPC to a different room."""
        db.execute(
            "UPDATE npc_instances SET room_id = ? WHERE id = ?", (room_id, self.id)
        )
        db.commit()
        self.room_id = room_id

    def get_dialogue(self, topic: str, db) -> str | None:
        row = db.execute(
            "SELECT response FROM dialogue WHERE npc_id = ? AND topic = ?",
            (self.template_id, topic.lower()),
        ).fetchone()
        return row["response"] if row else None

    def describe(self) -> str:
        """Short description shown when a player looks at this NPC."""
        status = "" if self.is_alive else " (dead)"
        return f"{self.name}{status} — {self.description}"

    def __repr__(self):
        return (
            f"<NpcInstance id={self.id} '{self.name}' "
            f"hp={self.current_health}/{self.max_health} room={self.room_id}>"
        )


def load_item(instance_id: int, db) -> Item:
    """
    # Currently returns a Torch if the item is a torch, otherwise a plain Item.
    # This can be used everywhere instead calling Item(...) directly.
    """
    row = db.execute(
        "SELECT it.item_type FROM item_instances ii JOIN item_templates it ON ii.template_id = it.id WHERE ii.id = ?",
        (instance_id,),
    ).fetchone()

    if row is None:
        raise ValueError(f"No item instance with id={instance_id}")

    if row["item_type"] == "torch":
        return Torch(instance_id, db)
    # In the future, I'll have code here for Food, potentially Weapon, etc.
    return Item(instance_id, db)


def load_items(instance_ids: list[int], db) -> list[Item]:
    """
    Bulk-load multiple items efficiently, avoiding N+1 queries.
    Returns Item/Torch objects just like load_item().
    """

    if not instance_ids:
        return []

    # ─────────────────────────────────────────────
    # 1. Load all item_instances
    # ─────────────────────────────────────────────
    placeholders = ",".join("?" for _ in instance_ids)

    instance_rows = db.execute(
        f"""
        SELECT * FROM item_instances
        WHERE id IN ({placeholders})
    """,
        instance_ids,
    ).fetchall()

    # Map: instance_id → row
    instances = {row["id"]: row for row in instance_rows}

    # ─────────────────────────────────────────────
    # 2. Load all templates
    # ─────────────────────────────────────────────
    template_ids = list({row["template_id"] for row in instance_rows})

    placeholders = ",".join("?" for _ in template_ids)

    template_rows = db.execute(
        f"""
        SELECT * FROM item_templates
        WHERE id IN ({placeholders})
    """,
        template_ids,
    ).fetchall()

    templates = {row["id"]: row for row in template_rows}

    # ─────────────────────────────────────────────
    # 3. Load all locations
    # ─────────────────────────────────────────────
    # Step 3. Load all locations
    placeholders = ",".join("?" for _ in instance_ids)  # ← recalculate!
    location_rows = db.execute(
        f"""
        SELECT * FROM item_locations
        WHERE instance_id IN ({placeholders})
        """,
        instance_ids,
    ).fetchall()

    locations = {row["instance_id"]: row for row in location_rows}

    # ─────────────────────────────────────────────
    # 4. Group by item_type (for Torch handling)
    # ─────────────────────────────────────────────
    items = []

    for instance_id in instance_ids:
        inst = instances.get(instance_id)
        if not inst:
            continue

        tmpl = templates.get(inst["template_id"])
        if not tmpl:
            continue

        item_type = tmpl["item_type"]

        # Instantiate correct class
        if item_type == "torch":
            item = Torch(instance_id, db)
        else:
            item = Item(instance_id, db)

        # Inject location (avoid extra query)
        loc = locations.get(instance_id)
        if loc:
            item.room_id = loc["room_id"]
            item.player_id = loc["player_id"]
            item.npc_id = loc["npc_id"]
            item.equipped_slot = loc["equipped_slot"]

        items.append(item)

    return items


def find_item_by_name(name: str, items: list, index: int = 1) -> "Item | None":
    query_words = name.lower().split()

    matches = []
    for item in items:
        item_words = item.name.lower().split()
        if all(word in item_words for word in query_words):
            matches.append(item)

    if not matches:
        return None

    if index > len(matches):
        return None

    return matches[index - 1]
