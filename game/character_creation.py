import game.stats


def create_character():
    print()
    print("Welcome to character creation!")

    # Step 1: username
    while True:
        print()
        username = input("First, pick your name, adventurer.\n> ").strip().capitalize()
        if username:
            print()
            print(f"Your name shall be {username}.")
            break
        # Additionally, check if username matches any other username, or in any way does not fit with naming standards.
        print()
        print("\nInvalid response. Please try again.\n")

    # Step 2: password
    while True:
        print()
        password = input(f"\nWhat shall your password be, {username}?\n> ").strip()
        if not password:
            print()
            print("\nPassword cannot be empty. Please try again.\n")
            continue
        print()
        confirmation = input("\nPlease retype your password.\n> ").strip()
        if confirmation == password:
            print()
            print("\nYou may proceed.\n")
            break
        print()
        print("\nPasswords did not match. Please try again.\n")

    # Step 3: gender
    while True:
        print()
        gender = input("'Male' or 'female'?\n> ").strip().capitalize()
        if gender.strip().capitalize() not in ['Male','Female']:
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
        if not 0 < int(num_chosen) < len(race_list):
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
        guild = guild_list[int(num_chosen) - 1]
        if guild:
            print()
            print(f"You shall be a {guild.capitalize()}.")
            break
        print()
        print("\nNot a guild! Please try again.\n")

    # Step 6: roll stats.
    game.stats.assign_stats()

    # Step 7:
