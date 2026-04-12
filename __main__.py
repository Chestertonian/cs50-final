from game.engine import GameEngine
from game.ui import main_menu

# This is not being used yet.
def main():
    """Entry point for the game."""
    engine = GameEngine()
    engine.run()

if __name__ == "__main__":
    main_menu()
