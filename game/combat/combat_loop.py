# game/combat/combat_loop.py

from game.helpers import XP_TABLE

RESPAWN_ROOM_ID = 1

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
            ,:::::'       ;           OOO\          
            ::::::;       ;          OOOOO\         
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
    print("You wake up without your belongings.\n")