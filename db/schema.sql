-- =============================================================================
-- schema.sql
-- Database schema for cs50 Final Project
-- =============================================================================


-- =============================================================================
-- WORLD
-- =============================================================================

CREATE TABLE rooms (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    description  TEXT    NOT NULL,
    lighting     INTEGER NOT NULL DEFAULT 1,
    smell        TEXT    NOT NULL DEFAULT '',
    sound        TEXT    NOT NULL DEFAULT '',
    area         TEXT    NOT NULL DEFAULT 'city', -- used for grouping/theming
    movement_cost INTEGER DEFAULT 3,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE exits (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id              INTEGER NOT NULL,
    direction            TEXT    NOT NULL,        -- 'north', 'east', 'up', etc.
    destination_room_id  INTEGER NOT NULL,
    secret               INTEGER NOT NULL DEFAULT 0,  -- 1 = hidden from exit list
    locked               INTEGER NOT NULL DEFAULT 0,  -- 1 = requires a key
    key_template_id      INTEGER DEFAULT NULL,         -- item_template needed to unlock (e.g. key)
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id)             REFERENCES rooms(id),
    FOREIGN KEY (destination_room_id) REFERENCES rooms(id),
    UNIQUE(room_id, direction)        -- one exit per direction per room
);


-- =============================================================================
-- ITEMS — Templates (blueprints) and Instances (physical copies in the world)
-- =============================================================================

-- Shared data for all items of a given type.
CREATE TABLE item_templates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL,
    item_type   TEXT    NOT NULL,           -- 'weapon','armor','torch','food','treasure','container'
    weight      INTEGER NOT NULL DEFAULT 1,
    value       INTEGER NOT NULL DEFAULT 0, -- gold value
    is_takeable INTEGER NOT NULL DEFAULT 1, -- 0 = fixed to the world
    is_droppable INTEGER NOT NULL DEFAULT 1, -- 0 = not used yet, maybe necessary someday.
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Extra data for weapons.
CREATE TABLE item_weapon_templates (
    template_id  INTEGER PRIMARY KEY,
    damage_min   INTEGER NOT NULL DEFAULT 1,
    damage_max   INTEGER NOT NULL DEFAULT 4,
    weapon_type  TEXT    NOT NULL DEFAULT 'melee',
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Extra data for armor pieces.
CREATE TABLE item_armor_templates (
    template_id      INTEGER PRIMARY KEY,
    defense          INTEGER NOT NULL DEFAULT 1,
    damage_reduction REAL    NOT NULL DEFAULT 0.05, -- fraction of damage blocked (0.0–1.0)
    armor_slot       TEXT    NOT NULL,              -- 'head', 'body', 'hands', 'feet'
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Extra data for torches.
CREATE TABLE item_torch_templates (
    template_id       INTEGER PRIMARY KEY,
    default_burn_time INTEGER NOT NULL DEFAULT 100, -- ticks before burning out
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Extra data for food. (TODO: flesh out)
CREATE TABLE item_food_templates (
    template_id  INTEGER PRIMARY KEY,
    heal_amount  INTEGER NOT NULL DEFAULT 5,
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Extra data for containers. (TODO: not yet used)
CREATE TABLE item_container_templates (
    template_id INTEGER PRIMARY KEY,
    capacity    INTEGER NOT NULL DEFAULT 5, -- max items it can hold
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- A physical copy of an item that exists somewhere in the world.
CREATE TABLE item_instances (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Per-instance state for torches (burn time ticks down, can be lit/doused).
CREATE TABLE item_torch_instances (
    instance_id INTEGER PRIMARY KEY,
    burn_time   INTEGER NOT NULL DEFAULT 100,
    is_lit      INTEGER NOT NULL DEFAULT 0,  -- 0 = unlit, 1 = lit
    FOREIGN KEY (instance_id) REFERENCES item_instances(id)
);

-- Tracks where every item instance currently is.
-- Exactly one of room_id / player_id / npc_id must be set (enforced by CHECK).
-- equipped_slot is only non-null when the item is worn/wielded by a player.
CREATE TABLE item_locations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id  INTEGER NOT NULL UNIQUE,
    room_id      INTEGER DEFAULT NULL,
    player_id    INTEGER DEFAULT NULL,
    npc_id       INTEGER DEFAULT NULL,
    equipped_slot TEXT   DEFAULT NULL,  -- 'head','body','hands','feet','weapon'
    FOREIGN KEY (instance_id) REFERENCES item_instances(id),
    FOREIGN KEY (room_id)     REFERENCES rooms(id),
    FOREIGN KEY (player_id)   REFERENCES players(id),
    FOREIGN KEY (npc_id)      REFERENCES npc_instances(id),
    CHECK (
        (room_id IS NOT NULL AND player_id IS NULL AND npc_id IS NULL) OR
        (player_id IS NOT NULL AND room_id IS NULL AND npc_id IS NULL) OR
        (npc_id IS NOT NULL AND room_id IS NULL AND player_id IS NULL)
    )
);

-- Controls where and how often items respawn in the world.
CREATE TABLE item_spawns (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id  INTEGER NOT NULL,
    room_id      INTEGER NOT NULL,
    max_count    INTEGER NOT NULL DEFAULT 1,
    respawn_time INTEGER NOT NULL DEFAULT 300, -- seconds between respawns
    last_spawn_at REAL   DEFAULT 0,
    FOREIGN KEY (template_id) REFERENCES item_templates(id),
    FOREIGN KEY (room_id)     REFERENCES rooms(id)
);


-- =============================================================================
-- NPCs — Templates (blueprints) and Instances (living copies in the world)
-- =============================================================================

-- Shared data for all NPCs of a given type.
CREATE TABLE npc_templates (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL,
    description      TEXT    NOT NULL,
    gender           INTEGER DEFAULT 0,          -- 0 = neutral, 1 = male, 2 = female
    max_health       INTEGER NOT NULL DEFAULT 25,
    is_aggressive    INTEGER NOT NULL DEFAULT 0, -- 1 = attacks player on sight
    damage_min       INTEGER NOT NULL DEFAULT 1,
    damage_max       INTEGER NOT NULL DEFAULT 4,
    damage_reduction REAL    NOT NULL DEFAULT 0.0, -- fraction of incoming damage blocked
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- A living copy of an NPC template, placed in a specific room.
CREATE TABLE npc_instances (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id      INTEGER NOT NULL,
    room_id          INTEGER NOT NULL,
    home_room_id     INTEGER DEFAULT NULL,       -- room to return to if wandering
    current_health   INTEGER NOT NULL,
    is_alive         INTEGER NOT NULL DEFAULT 1, -- 0 = dead
    last_action_tick INTEGER DEFAULT 0,          -- used for tick pacing
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES npc_templates(id),
    FOREIGN KEY (room_id)     REFERENCES rooms(id)
);

-- Controls where and how often NPCs respawn in the world.
CREATE TABLE npc_spawns (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id    INTEGER NOT NULL,
    room_id        INTEGER NOT NULL,
    max_count      INTEGER NOT NULL DEFAULT 1,
    respawn_delay  INTEGER NOT NULL DEFAULT 300, -- seconds between respawns by default
    last_spawn_at  REAL    DEFAULT 0,
    FOREIGN KEY (template_id) REFERENCES npc_templates(id),
    FOREIGN KEY (room_id)     REFERENCES rooms(id)
);


-- =============================================================================
-- DIALOGUE
-- =============================================================================

-- Simple dialogue table.
CREATE TABLE dialogue (
    id      INTEGER PRIMARY KEY,
    npc_id  INTEGER,  -- references npc_templates.id
    topic   TEXT,
    response TEXT
);


-- =============================================================================
-- COMBAT — NPC special attacks
-- =============================================================================

-- Optional special attacks that an NPC type can use in combat.
CREATE TABLE npc_special_attacks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    npc_template_id INTEGER NOT NULL,
    attack_name     TEXT    NOT NULL,         -- e.g. 'poison_bite', 'knockdown'
    chance          REAL    NOT NULL DEFAULT 0.2, -- probability per round (0.0–1.0)
    damage_min      INTEGER DEFAULT 0,
    damage_max      INTEGER DEFAULT 0,
    effect          TEXT    DEFAULT NULL,     -- e.g. 'poison', 'knockdown', 'flee'
    message         TEXT    NOT NULL,         -- shown to player when triggered
    FOREIGN KEY (npc_template_id) REFERENCES npc_templates(id)
);


-- =============================================================================
-- PLAYERS
-- =============================================================================

CREATE TABLE players (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT    NOT NULL UNIQUE,
    password             TEXT    NOT NULL,
    race                 TEXT    NOT NULL DEFAULT 'human',
    guild                TEXT    NOT NULL DEFAULT 'warrior',
    gender               INTEGER NOT NULL,          -- 0 = neutral, 1 = male, 2 = female
    save_name            TEXT    UNIQUE,
    current_room_id      INTEGER NOT NULL DEFAULT 1,

    -- Resources
    health               INTEGER NOT NULL DEFAULT 25,
    max_health           INTEGER NOT NULL DEFAULT 25,
    power                INTEGER DEFAULT 25,        -- mana / spell points
    max_power            INTEGER DEFAULT 25,
    movement_points      INTEGER DEFAULT 25,
    max_movement_points  INTEGER DEFAULT 25,

    -- Progression
    experience           INTEGER NOT NULL DEFAULT 0,
    level                INTEGER NOT NULL DEFAULT 1,

    -- Stats
    str_stat             INTEGER NOT NULL,
    con_stat             INTEGER NOT NULL,
    dex_stat             INTEGER NOT NULL,
    int_stat             INTEGER NOT NULL,
    wis_stat             INTEGER NOT NULL,
    cha_stat             INTEGER NOT NULL,

    traits               TEXT    NOT NULL DEFAULT '',
    last_tick_at         REAL    NOT NULL DEFAULT 0,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (current_room_id) REFERENCES rooms(id)
);