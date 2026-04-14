import game.stats
import hashlib



def create_character(db):
    print()
    print("Welcome to character creation!")

    # Step 1: username
    while True:
        print()
        username = (
            input("By what name will you be known, adventurer?\n> ")
            .strip()
            .capitalize()
            .replace(" ", "")
            .encode("ascii", "ignore")
            .decode()
        )
        if len(username) > 25:
            print("\nYour name is far too long.")
            continue
        if len(username) < 3:
            print("\nYour name is too short.")
            continue
        if not username.strip().isalpha():
            print("\nUsername must contain only letters.")
            continue
        existing = db.execute("SELECT 1 FROM players WHERE name = ? LIMIT 1", (username,)).fetchone()
        if existing:
            print("\nThat name is already taken.")
            continue
        if username:
            print()
            print(f"\nYour name shall be {username}.")
            break
        print()
        print("\nInvalid response. Please try again.\n")

    # Step 2: password
    while True:
        print()
        password = (
            input(f"\nWhat shall your password be, {username}?\n> ")
            .strip()
            .encode("ascii", "ignore")
            .decode()
        )
        if len(password) > 25:
            print("\nYour password is far too long.")
            continue
        if len(password) < 3:
            print("\nYour password is too short.")
            continue
        if not password:
            print()
            print("\nPassword cannot be empty. Please try again.\n")
            continue
        print()
        confirmation = input("\nPlease retype your password.\n> ").strip()
        if confirmation == password:
            print()
            print("\nYou may proceed.\n")
            encrypted_password = hashlib.sha256(password.encode()).hexdigest()
            break
        print()
        print("\nPasswords did not match. Please try again.\n")

    # Step 3: gender
    while True:
        print()
        gender = input("'Male' or 'female'?\n> ").strip().capitalize()
        if gender.strip().capitalize() not in ["Male", "Female"]:
            continue
        if gender:
            print()
            print(f"You picked {gender}.")
            break
        # Check if string is male or female.
        print()
        print("\nInvalid response. Please try again.\n")

    # Step 4: race
    while True:
        race_list = ["human", "dwarf", "elf", "gnome", "centaur"]
        with open("game/text_files/races_screen.txt", "r") as races:
            race_text = races.read()
        print()
        num_chosen = input(race_text)
        try:
            int(num_chosen)
        except ValueError:
            print("Input a number.")
            continue
        if not 0 < int(num_chosen) < len(race_list) + 1:
            print("Input a valid number.")
            continue
        race = race_list[int(num_chosen) - 1]
        if race:
            print()
            print(f"You shall be a {race.capitalize()}.")
            break
        print()
        print("\nNot a race! Please try again.\n")

    # Step 5: guild
    while True:
        guild_list = ["warrior", "cleric", "rogue", "wizard", "ranger"]
        with open("game/text_files/guilds_screen.txt", "r") as guilds:
            guild_text = guilds.read()
        print()
        num_chosen = input(guild_text)
        try:
            int(num_chosen)
        except ValueError:
            print("Input a valid number.")
            continue
        if not 0 < int(num_chosen) < len(guild_list) + 1:
            print("Input a valid number.")
            continue
        guild = guild_list[int(num_chosen) - 1]
        if guild:
            print()
            print(f"You shall be a {race.capitalize()} {guild.capitalize()}.")
            break
        print()
        print("\nNot a guild! Please try again.\n")

    # Step 6: roll stats.
    stat_array = game.stats.assign_stats()
    
    # Step 7: Add racial bonuses for each stat.
    stat_bonus={"human": ('str', 1, 'cha', 1),
                "dwarf": ('str', 1, 'con', 1),
                "elf": ('dex', 1, 'int', 1),
                "gnome": ('cha', 1, 'int', 1),
                "centaur": ('wis', 1, 'con', 1)
                }
    stat_array[stat_bonus[race][0].upper()]+=stat_bonus[race][1]
    stat_array[stat_bonus[race][2].upper()]+=stat_bonus[race][3]
    

    db.execute(
        "INSERT INTO players (name, password, gender, race, guild, str_stat, dex_stat, con_stat, int_stat, wis_stat, cha_stat) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            username,
            encrypted_password,
            gender,
            race,
            guild,
            stat_array["STR"],
            stat_array["DEX"],
            stat_array["CON"],
            stat_array["INT"],
            stat_array["WIS"],
            stat_array["CHA"],
        ),
    )
    db.commit()
    return username
