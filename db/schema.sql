-- ============================================================
-- WORLD CORE
-- ============================================================

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,

    -- Environmental attributes
    lighting INTEGER NOT NULL DEFAULT 1,
    smell TEXT NOT NULL DEFAULT '',
    sound TEXT NOT NULL DEFAULT '',
    area TEXT NOT NULL DEFAULT 'city',

    -- Movement cost for entering this room
    movement_cost INTEGER DEFAULT 2,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- All connections between rooms
CREATE TABLE exits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    direction TEXT NOT NULL, -- aka exit name
    destination_room_id INTEGER NOT NULL,

    secret INTEGER NOT NULL DEFAULT 0,
    locked INTEGER NOT NULL DEFAULT 0,
    key_template_id INTEGER DEFAULT NULL, -- what unlocks this door, if it's locked?
    description TEXT DEFAULT '',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (destination_room_id) REFERENCES rooms(id),

    UNIQUE(room_id, direction)
);

-- ============================================================
-- ITEM SYSTEM (TEMPLATES = archetypes)
-- ============================================================

CREATE TABLE item_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,

    item_type TEXT NOT NULL,  -- weapon, armor, torch, food, treasure, container

    weight INTEGER NOT NULL DEFAULT 1,
    value INTEGER NOT NULL DEFAULT 0,

    is_takeable INTEGER NOT NULL DEFAULT 1, 
    is_droppable INTEGER NOT NULL DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weapon-specific data
CREATE TABLE item_weapon_templates (
    template_id INTEGER PRIMARY KEY,
    damage_min INTEGER NOT NULL DEFAULT 1,
    damage_max INTEGER NOT NULL DEFAULT 4,
    weapon_type TEXT NOT NULL DEFAULT 'melee',

    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Armor-specific data
CREATE TABLE item_armor_templates (
    template_id INTEGER PRIMARY KEY,
    defense INTEGER NOT NULL DEFAULT 1,
    armor_slot TEXT NOT NULL, -- e.g. 'body' or 'head'
    damage_reduction REAL NOT NULL DEFAULT 0.05,

    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Torch-specific data
CREATE TABLE item_torch_templates (
    template_id INTEGER PRIMARY KEY,
    default_burn_time INTEGER NOT NULL DEFAULT 100,

    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Future systems
CREATE TABLE item_food_templates (
    template_id INTEGER PRIMARY KEY,
    heal_amount INTEGER NOT NULL DEFAULT 5,

    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

CREATE TABLE item_container_templates (
    template_id INTEGER PRIMARY KEY,
    capacity INTEGER NOT NULL DEFAULT 5,

    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- ============================================================
-- ITEM INSTANCES
-- ============================================================

CREATE TABLE item_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Torch runtime state (not yet used)
CREATE TABLE item_torch_instances (
    instance_id INTEGER PRIMARY KEY,
    burn_time INTEGER NOT NULL DEFAULT 100,
    is_lit INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (instance_id) REFERENCES item_instances(id)
);

-- Where items currently exist (VERY important!)
CREATE TABLE item_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER NOT NULL UNIQUE,

    room_id INTEGER,
    player_id INTEGER,
    npc_id INTEGER,

    equipped_slot TEXT DEFAULT NULL,

    FOREIGN KEY (instance_id) REFERENCES item_instances(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (npc_id) REFERENCES npc_instances(id),

    -- ensures item exists in exactly ONE place
    CHECK (
        (room_id IS NOT NULL AND player_id IS NULL AND npc_id IS NULL) OR
        (room_id IS NULL AND player_id IS NOT NULL AND npc_id IS NULL) OR
        (room_id IS NULL AND player_id IS NULL AND npc_id IS NOT NULL)
    )
);

-- ============================================================
-- PLAYER SYSTEM
-- ============================================================

CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL, -- hashed password ONLY

    race TEXT NOT NULL DEFAULT 'human',
    guild TEXT NOT NULL DEFAULT 'wizard',
    gender INTEGER NOT NULL,

    save_name TEXT UNIQUE,

    current_room_id INTEGER NOT NULL DEFAULT 1,

    health INTEGER NOT NULL DEFAULT 25,
    max_health INTEGER NOT NULL DEFAULT 25,

    experience INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,

    -- stats
    int_stat INTEGER NOT NULL,
    wis_stat INTEGER NOT NULL,
    dex_stat INTEGER NOT NULL,
    cha_stat INTEGER NOT NULL,
    con_stat INTEGER NOT NULL,
    str_stat INTEGER NOT NULL,

    traits TEXT NOT NULL DEFAULT '', -- not yet used

    movement_points INTEGER DEFAULT 25,
    max_movement_points INTEGER DEFAULT 25,

    power INTEGER DEFAULT 25,
    max_power INTEGER DEFAULT 25,

    wealth INTEGER DEFAULT 25,

    last_tick_at REAL NOT NULL DEFAULT 0, -- when did they last regenerate, etc

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (current_room_id) REFERENCES rooms(id)
);

-- ============================================================
-- NPC SYSTEM
-- ============================================================

-- NPC archetypes (Platonic forms if you've taken HUM 201)
CREATE TABLE npc_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,

    max_health INTEGER NOT NULL DEFAULT 25,
    is_aggressive INTEGER NOT NULL DEFAULT 0,

    gender INTEGER DEFAULT 0, -- 1=male, 2=female.

    damage_min INTEGER NOT NULL DEFAULT 1,
    damage_max INTEGER NOT NULL DEFAULT 4,
    damage_reduction REAL NOT NULL DEFAULT 0.0,

    wealth_min INTEGER DEFAULT 0,
    wealth_max INTEGER DEFAULT 5,

    xp INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NPC instances in the world (an actual goblin running around in the world!)
CREATE TABLE npc_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,

    current_health INTEGER NOT NULL,
    is_alive INTEGER NOT NULL DEFAULT 1,

    last_action_tick INTEGER DEFAULT 0,
    home_room_id INTEGER,

    is_aggro_to_player INTEGER NOT NULL DEFAULT 0,
    aggro_since REAL DEFAULT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (template_id) REFERENCES npc_templates(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Respawn rules (where to put templates)
CREATE TABLE npc_spawns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,

    max_count INTEGER NOT NULL DEFAULT 1, -- How many can show up
    respawn_delay INTEGER NOT NULL DEFAULT 300, -- in seconds
    last_spawn_at REAL DEFAULT 0,

    FOREIGN KEY (template_id) REFERENCES npc_templates(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Simple dialogue system (e.g. "ask guard about name")
CREATE TABLE dialogue (
    id INTEGER PRIMARY KEY,
    npc_id INTEGER,
    topic TEXT,
    response TEXT
);

-- Keyword-based dialogue system. This is a fancier version of what I'm currently doing, for version 2.0 of my game.
CREATE TABLE npc_dialogue_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    npc_template_id INTEGER NOT NULL,

    keyword TEXT NOT NULL,
    response TEXT NOT NULL,

    required_state TEXT DEFAULT 'default',
    required_flag TEXT DEFAULT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (npc_template_id) REFERENCES npc_templates(id)
);

-- Special attacks per NPC type, not used yet.
CREATE TABLE npc_special_attacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    npc_template_id INTEGER NOT NULL,

    attack_name TEXT NOT NULL,
    chance REAL NOT NULL DEFAULT 0.2,

    damage_min INTEGER DEFAULT 0,
    damage_max INTEGER DEFAULT 0,

    effect TEXT DEFAULT NULL,
    message TEXT NOT NULL,

    FOREIGN KEY (npc_template_id) REFERENCES npc_templates(id)
);

-- ============================================================
-- SHOPS (not yet implemented)
-- ============================================================

CREATE TABLE shop_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    npc_template_id INTEGER NOT NULL,
    item_template_id INTEGER NOT NULL,

    price INTEGER NOT NULL,

    FOREIGN KEY (npc_template_id) REFERENCES npc_templates(id),
    FOREIGN KEY (item_template_id) REFERENCES item_templates(id)
);

-- ============================================================
-- WORLD SPAWNS (for items)
-- ============================================================

CREATE TABLE item_spawns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,

    max_count INTEGER NOT NULL DEFAULT 1,
    respawn_time INTEGER NOT NULL DEFAULT 300,

    last_spawn_at REAL DEFAULT 0,

    FOREIGN KEY (template_id) REFERENCES item_templates(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- ============================================================
-- SKILL SYSTEM (all powers go here)
-- ============================================================

CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT NOT NULL,

    guild TEXT NOT NULL,

    min_level INTEGER NOT NULL DEFAULT 1,
    power_cost INTEGER NOT NULL DEFAULT 0,

    skill_type TEXT NOT NULL DEFAULT 'active',
    trigger TEXT DEFAULT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);