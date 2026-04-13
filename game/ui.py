# This is where code calling for login, registration, etc. will live.
from game.character_creation import create_character
from game.login import login_screen
import game.helpers


def main_menu(db):
    """Display login/register menu."""
    while True:
        welcome_screen = open("game/text_files/ascii_art.txt", "r")
        print(welcome_screen.read())
        welcome_screen.close()

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            return(login_screen(db))
        elif choice == "2":
            return(create_character(db))
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n\n\n")
