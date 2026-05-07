# game/combat/combat_loop.py

# Includes player leveling up.

import time
from game.helpers import XP_TABLE, MAX_LEVEL

RESPAWN_ROOM_ID = 206


import random
from game.models import NpcInstance

BARE_HANDS_MIN = 1
BARE_HANDS_MAX = 3
PLAYER_BASE_DEFENSE = 0

def get_player_defense(player, db):
    """Sum defense from all equipped armor pieces."""
    rows = db.execute("""
        SELECT iat.defense
        FROM item_locations il
        JOIN item_instances ii ON il.instance_id = ii.id
        JOIN item_templates it ON ii.template_id = it.id
        JOIN item_armor_templates iat ON it.id = iat.template_id
        WHERE il.player_id = ? AND il.equipped_slot IS NOT NULL
    """, (player.id,)).fetchall()

    equipped_defense = sum(row["defense"] for row in rows)
    return PLAYER_BASE_DEFENSE + equipped_defense

def check_level_up(player, db):
    """Check if the player has enough XP to level up (possibly multiple times)."""
    while player.level < MAX_LEVEL:
        xp_needed = XP_TABLE.get(player.level)
        if xp_needed is None:
            break  # no entry in table means they're at the cap
        if player.experience >= xp_needed:
            player.level += 1
            apply_level_up(player, db)
        else:
            break


def apply_level_up(player, db):
    """Apply stat changes for a level-up and notify the player."""
    print(f"\n*** You have reached level {player.level}! ***\n")

    def stat_bonus(stat):
        # Smooth scaling, no penalties, no negatives
        # Every 4 stat points above 10 = +1 bonus
        return max((stat - 10) / 4, 0)

    def level_gain(base, stats):
        return base + sum(stat_bonus(s) for s in stats)

    # --- HP (STR / CON / DEX) ---
    hp_gain = level_gain(3, [
        player.stats["STR"],
        player.stats["CON"],
        player.stats["DEX"]
    ])

    player.max_health += round(hp_gain)

    # --- MP / Power (INT / WIS / CHA) ---
    sp_gain = level_gain(3, [
        player.stats["INT"],
        player.stats["WIS"],
        player.stats["CHA"]
    ])

    player.max_power += round(sp_gain)

    # --- Movement
    player.max_movement_points += 3

    # --- Heal on level up
    player.health = min(player.health + 10, player.max_health)
    
    db.execute(
        """
        UPDATE players
        SET level = ?, max_health = ?, max_power = ?,
            max_movement_points = ?, health = ?
        WHERE id = ?
    """,
        (
            player.level,
            player.max_health,
            player.max_power,
            player.max_movement_points,
            player.health,
            player.id,
        ),
    )
    db.commit()


def run_combat_round(player, db):

    # ─────────────────────────────
    # GET PRIMARY TARGET
    # ─────────────────────────────
    npc = NpcInstance.get_by_id(db, player.combat.primary_target_id)
    if not npc or not npc.is_alive:
        player.combat.remove_npc(player.combat.primary_target_id)
        return

    # ─────────────────────────────
    # PLAYER ATTACKS NPC
    # ─────────────────────────────
    weapon = player.get_equipped_weapon(db)
    if weapon:
        damage = random.randint(weapon["damage_min"], weapon["damage_max"])
    else:
        damage = random.randint(BARE_HANDS_MIN, BARE_HANDS_MAX)

    # Apply NPC's natural damage reduction (e.g. 0.1 = blocks 10% of damage)
    damage = max(1, int(damage * (1 - npc.template.damage_reduction)))

    if weapon:
        print(f"You hit {npc.name} with your {weapon['name']} for {damage} damage.")
    else:
        print(f"You hit {npc.name} with your bare hands for {damage} damage.")

    npc.current_health -= damage
    db.execute(
        "UPDATE npc_instances SET current_health = ? WHERE id = ?",
        (npc.current_health, npc.id),
    )
    db.commit()

    if npc.current_health <= 0:
        handle_npc_death(player, npc, db)
        return

    # ─────────────────────────────
    # EACH ATTACKER HITS PLAYER
    # ─────────────────────────────
    defense = get_player_defense(player, db)
    for npc_id in list(player.combat.attacker_ids):
        attacker = NpcInstance.get_by_id(db, npc_id)
        if not attacker or not attacker.is_alive:
            continue
        raw_damage = random.randint(attacker.damage_min, attacker.damage_max)
        max_absorb = int(raw_damage * 0.5)
        damage = max(2, raw_damage - min(defense, max_absorb))
        if defense > 0 and raw_damage > damage:
            print(f"{attacker.name} hits you for {damage} damage. ({raw_damage} - {defense} absorbed)")
        else:
            print(f"{attacker.name} hits you for {damage} damage.")
        player.health -= damage

    if player.health <= 0:
        handle_death(player, db)
        return

    db.execute("UPDATE players SET health = ? WHERE id = ?", (player.health, player.id))
    db.commit()


def handle_death(player, db):
    player.combat.end_combat()
    # 1. XP loss
    xp_floor = XP_TABLE.get(player.level, 0)
    xp_loss = int(player.experience * 0.15)
    player.experience = max(xp_floor, player.experience - xp_loss)

    # 2 & 3. Drop all items (carried and equipped) into the death room
    db.execute(
        """
        UPDATE item_locations
        SET room_id = ?,
            player_id = NULL,
            equipped_slot = NULL
        WHERE player_id = ?
    """,
        (player.current_room_id, player.id),
    )

    # 4. Restore HP to 10% (minimum 1)
    player.health = max(1, int(player.max_health * 0.10))

    # 5. Move to respawn room
    player.current_room_id = RESPAWN_ROOM_ID

    # 6. Save to DB
    db.execute(
        """
        UPDATE players
        SET health = ?, current_room_id = ?, experience = ?
        WHERE id = ?
    """,
        (player.health, player.current_room_id, player.experience, player.id),
    )
    db.commit()

    # 7. Message
    print("""                
                    ...                            
                    ;::::;                            
                ;::::; :;                           
                ;:::::'   :;                          
                ;:::::;     ;.                         
            ,:::::'       ;           OOO\\          
            ::::::;       ;          OOOOO\\         
            ;:::::;       ;         OOOOOOOO        
            ,;::::::;     ;'         / OOOOOOO       
            ;:::::::::`. ,,,;.        /  / DOOOOOO     
        .';:::::::::::::::::;,     /  /     DOOOO    
        ,::::::;::::::;;;;::::;,   /  /        DOOO   
        ;`::::::`'::::::;;;::::: ,#/  /          DOOO  
        :`:::::::`;::::::;;::: ;::#  /            DOOO 
        ::`:::::::`;:::::::: ;::::# /              DOO 
        `:`:::::::`;:::::: ;::::::#/               DOO 
        :::`:::::::`;; ;:::::::::##                OO 
        ::::`:::::::`;::::::::;:::#                OO 
        `:::::`::::::::::::;'`:;::#                O  
        `:::::`::::::::;' /  / `:#                   
        ::::::`:::::;'  /  /   `#              
          """)
    print("\nYou have died.")
    print(f"You lost {xp_loss} experience.")
    print("You wake up without your belongings, alas.\n")


def handle_npc_death(player, npc, db):

    # ─────────────────────────────
    # MARK NPC AS DEAD IN DB (first)
    # ─────────────────────────────
    db.execute(
        "UPDATE npc_instances SET is_alive = 0, current_health = 0 WHERE id = ?",
        (npc.id,),
    )
    db.execute(
        """
        UPDATE npc_spawns
        SET last_spawn_at = ?
        WHERE template_id = ? AND room_id = ?
        """,
        (time.time(), npc.template_id, npc.room_id),
    )
    db.commit()

    # ─────────────────────────────
    # CLEAR COMBAT STATE
    # ─────────────────────────────
    npc.clear_aggro(db)
    player.combat.remove_npc(npc.id)

    # ─────────────────────────────
    # AWARD XP
    # ─────────────────────────────
    xp_gain = npc.experience_value
    player.experience += xp_gain
    db.execute(
        "UPDATE players SET experience = ? WHERE id = ?", (player.experience, player.id)
    )
    db.commit()
    print(f"You gain {xp_gain} experience.")
    check_level_up(player, db)

    # ─────────────────────────────
    # DROP ITEMS
    # ─────────────────────────────
    # TODO: implement when NPC inventory is ready
    # move all items in item_locations where npc_id = npc.id to npc's room

    print(f"\n{npc.name.capitalize()} is dead!\n")
