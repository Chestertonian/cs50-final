# This is where code calling for login, registration, etc. will live.
from game.character_creation import create_character
from game.login import login_screen 
import game.helpers
db=game.helpers.get_db()

def main_menu():
    """Display login/register menu."""
    while True:
        welcome_screen = open("game/text_files/ascii_art.txt", "r")
        print(welcome_screen.read())
        welcome_screen.close()

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            login_screen(db)
            
        elif choice == "2":
            create_character(db)
            
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n\n\n")
