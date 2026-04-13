from game.engine import GameEngine
from game.ui import *
from game.helpers import *
from game.models import Player


def main():
    db = get_db()
    username = main_menu(db)
    player = Player.get_by_name(db, username)
    engine = GameEngine(db, player)
    engine.run()


if __name__ == "__main__":
    main()
