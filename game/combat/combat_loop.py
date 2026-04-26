# game/combat/combat_loop.py

# Am I somehow adding experience in this? Weird.

from game.helpers import XP_TABLE

RESPAWN_ROOM_ID = 206


import random
from game.models import NpcInstance

BARE_HANDS_MIN = 1
BARE_HANDS_MAX = 3

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
        print(f"You hit {npc.name} with your {weapon['name']} for {damage} damage.")
    else:
        damage = random.randint(BARE_HANDS_MIN, BARE_HANDS_MAX)
        print(f"You hit {npc.name} with your bare hands for {damage} damage.")

    npc.current_health -= damage
    db.execute(
        "UPDATE npc_instances SET current_health = ? WHERE id = ?",
        (npc.current_health, npc.id)
    )
    db.commit()

    if npc.current_health <= 0:
        handle_npc_death(player, npc, db)
        return

    # ─────────────────────────────
    # EACH ATTACKER HITS PLAYER
    # ─────────────────────────────
    for npc_id in list(player.combat.attacker_ids):
        attacker = NpcInstance.get_by_id(db, npc_id)
        if not attacker or not attacker.is_alive:
            continue
        damage = random.randint(attacker.damage_min, attacker.damage_max)
        print(f"{attacker.name} hits you for {damage} damage.")
        player.health -= damage

    if player.health <= 0:
        handle_death(player, db)
        return

    db.execute(
        "UPDATE players SET health = ? WHERE id = ?",
        (player.health, player.id)
    )
    db.commit()




def handle_death(player, db):
    # 1. XP loss
    xp_floor = XP_TABLE.get(player.level, 0)
    xp_loss = int(player.experience * 0.15)
    player.experience = max(xp_floor, player.experience - xp_loss)

    # 2 & 3. Drop all items (carried and equipped) into the death room
    db.execute("""
        UPDATE item_locations
        SET room_id = ?,
            player_id = NULL,
            equipped_slot = NULL
        WHERE player_id = ?
    """, (player.current_room_id, player.id))

    # 4. Restore HP to 10% (minimum 1)
    player.health = max(1, int(player.max_health * 0.10))

    # 5. Move to respawn room
    player.current_room_id = RESPAWN_ROOM_ID

    # 6. Save to DB
    db.execute("""
        UPDATE players
        SET health = ?, current_room_id = ?, experience = ?
        WHERE id = ?
    """, (player.health, player.current_room_id, player.experience, player.id))
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
        (npc.id,)
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
    # TODO: add experience value to npc_templates and award it here
    # xp_gain = npc.experience_value
    # player.experience += xp_gain
    # db.execute("UPDATE players SET experience = ? WHERE id = ?", (player.experience, player.id))
    # db.commit()

    # ─────────────────────────────
    # DROP ITEMS
    # ─────────────────────────────
    # TODO: implement when NPC inventory is ready
    # move all items in item_locations where npc_id = npc.id to npc's room

    print(f"\n{npc.name} is dead!\n")