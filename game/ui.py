# Lots more to do here. This is where code surrounding login, registration, etc. will live.
from game.character_creation import create_character


def main_menu():
    """Display login/register menu."""
    while True:
        welcome_screen = open("game/text_files/ascii_art.txt", "r")
        print(welcome_screen.read())
        welcome_screen.close()

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            pass
            # Someday, this will call login_screen()
        elif choice == "2":
            create_character()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n\n\n")
