-- CS50 Game Schema


-- Rooms table for game world
CREATE TABLE IF NOT EXISTS rooms (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	description TEXT NOT NULL,
	lighting INTEGER NOT NULL DEFAULT 1,
	smell TEXT NOT NULL DEFAULT '' ,
	sound TEXT NOT NULL DEFAULT '',
	area TEXT NOT NULL DEFAULT 'Thornheim',
	movement_cost INTEGER DEFAULT 3,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exits table for connecting rooms
CREATE TABLE IF NOT EXISTS exits (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	room_id INTEGER NOT NULL,
	direction TEXT NOT NULL,
	destination_room_id INTEGER NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	secret INTEGER NOT NULL DEFAULT 0,
	locked INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY (room_id) REFERENCES rooms(id),
	FOREIGN KEY (destination_room_id) REFERENCES rooms(id),
	UNIQUE(room_id, direction)
);

-- Table for player characters
CREATE TABLE IF NOT EXISTS players (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL,
	race TEXT NOT NULL DEFAULT 'human',
	guild TEXT NOT NULL DEFAULT 'warrior',
	gender INTEGER NOT NULL,
	save_name TEXT UNIQUE,
	current_room_id INTEGER NOT NULL DEFAULT 1,
	health INTEGER NOT NULL DEFAULT 25,
	max_health INTEGER NOT NULL DEFAULT 25,
	experience INTEGER NOT NULL DEFAULT 0,
	level INTEGER NOT NULL DEFAULT 1,
	int_stat INTEGER NOT NULL,
	wis_stat INTEGER NOT NULL,
	dex_stat INTEGER NOT NULL,
	cha_stat INTEGER NOT NULL,
	con_stat INTEGER NOT NULL,
	str_stat INTEGER NOT NULL,
	traits TEXT NOT NULL DEFAULT '',
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (current_room_id) REFERENCES rooms(id)
);
 

-- Tables for non-player characters.
CREATE TABLE IF NOT EXISTS npc_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    max_health INTEGER NOT NULL DEFAULT 25,
    dialogue TEXT DEFAULT '',
    is_aggressive INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- The instance: marks a specific NPC in a certain room (e.g. the idea of a goblin vs. a goblin living in a specific cave.)
CREATE TABLE IF NOT EXISTS npc_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    current_health INTEGER NOT NULL,
    is_alive INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES npc_templates(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- For marking NPC spawning. (Default respawn time is 5 minutes/300 seconds.)
CREATE TABLE IF NOT EXISTS npc_spawns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    max_count INTEGER NOT NULL DEFAULT 1,
    respawn_delay INTEGER NOT NULL DEFAULT 300, -- seconds
    FOREIGN KEY (template_id) REFERENCES npc_templates(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);


-- TEMPLATES (blueprints)

CREATE TABLE IF NOT EXISTS item_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    item_type TEXT NOT NULL,          -- 'weapon', 'armor', 'torch', 'food', 'treasure', 'container'
    weight INTEGER NOT NULL DEFAULT 1,
    value INTEGER NOT NULL DEFAULT 0,
    is_takeable INTEGER NOT NULL DEFAULT 1,
    is_droppable INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS item_weapon_templates (
    template_id INTEGER PRIMARY KEY,
    damage_min INTEGER NOT NULL DEFAULT 1,
    damage_max INTEGER NOT NULL DEFAULT 4,
    damage_type TEXT NOT NULL DEFAULT 'pierce',
    weapon_type TEXT NOT NULL DEFAULT 'melee',
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

CREATE TABLE IF NOT EXISTS item_armor_templates (
    template_id INTEGER PRIMARY KEY,
    defense INTEGER NOT NULL DEFAULT 1,
    armor_slot TEXT NOT NULL,         -- 'head', 'body', 'hands', 'feet'
    dex_penalty INT NOT NULL DEFAULT 0,
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

CREATE TABLE IF NOT EXISTS item_torch_templates (
    template_id INTEGER PRIMARY KEY,
    default_burn_time INTEGER NOT NULL DEFAULT 100,
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

CREATE TABLE IF NOT EXISTS item_food_templates (-- TODO
    template_id INTEGER PRIMARY KEY,
    heal_amount INTEGER NOT NULL DEFAULT 5,
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

CREATE TABLE IF NOT EXISTS item_container_templates ( -- don't have any of these yet, they will be a feature added later
    template_id INTEGER PRIMARY KEY,
    capacity INTEGER NOT NULL DEFAULT 5,
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);


-- INSTANCES (physical copies)

CREATE TABLE IF NOT EXISTS item_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES item_templates(id)
);

-- Location of each instance (room, npc OR player, never more than one)
CREATE TABLE IF NOT EXISTS item_locations (
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
    CHECK (
        (room_id IS NOT NULL AND npc_id IS NULL AND player_id IS NULL) OR
        (room_id IS NULL AND npc_id IS NULL AND player_id IS NOT NULL) OR
	(room_id IS NULL AND npc_id IS NOT NULL AND player_id IS NULL)
    )
);

-- Only torches currently need per-instance state (can be lit or doused). Other things that will at some point will probably be consumable items with charges.
CREATE TABLE IF NOT EXISTS item_torch_instances (
    instance_id INTEGER PRIMARY KEY,
    burn_time INTEGER NOT NULL DEFAULT 100,
    is_lit INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (instance_id) REFERENCES item_instances(id)
);