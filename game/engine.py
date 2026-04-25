# game/engine.py
from game.models import Player, Room
from game.tick import process_ticks
from game.commands.look import LookCommand
from game.commands.save import SaveCommand
from game.commands.score import ScoreCommand
from game.commands.time import TimeCommand
from game.commands.smell import SmellCommand
from game.commands.listen import ListenCommand
from game.commands.help import HelpCommand
from game.commands.get import GetCommand
from game.commands.drop import DropCommand
from game.commands.inventory import InventoryCommand
from game.commands.say import SayCommand
from game.commands.equip import EquipCommand
from game.commands.remove import RemoveCommand
from game.commands.health import HpCommand
from game.commands.ask import AskCommand
from game.commands.DevAddMove import AddMovementPointsCommand
from game.commands.wealth import WealthCommand
from game.commands.kill import KillCommand


class GameEngine:
    """Core game engine responsible for running the main loop."""

    def __init__(self, db, player):
        """Initialize game state."""
        self.db = db
        self.player = player
        self.is_running = True
        self.commands = {
            "look": LookCommand(),
            "save": SaveCommand(),
            "score": ScoreCommand(),
            "time": TimeCommand(),
            "smell": SmellCommand(),
            "listen": ListenCommand(),
            "help": HelpCommand(),
            "get": GetCommand(),
            "drop": DropCommand(),
            "inventory": InventoryCommand(),
            "say": SayCommand(),
            "equip": EquipCommand(),
            "remove": RemoveCommand(),
            "hp": HpCommand(),
            "add": AddMovementPointsCommand(),
            "ask": AskCommand(),
            "wealth": WealthCommand(),
            "kill": KillCommand(),
        }
        self.aliases = {
            # directions
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            "u": "up",
            "d": "down",
            # commands
            "i": "inventory",
            "inv": "inventory",
            "l": "look",
            "p": "hp",
            "health": "hp",
            "a": "wealth",
            "attack": "kill",
        }

    def run(self):
        """Start the main game loop."""
        self._print_welcome()

        while self.is_running:
            user_input = self._get_input()
            output = self._process_input(user_input)
            self._display_output(output)

    def _print_welcome(self):
        """On boot, should display the room the player is in.."""
        current_room = self.player.get_current_room(self.db)
        print(current_room.describe(self.db))

    def _get_input(self):
        """Get input from the player."""
        return input("> ").strip().lower()

    def _process_input(self, user_input):
        # Check if it's null (like always!)
        user_input = user_input.lower()
        if not user_input:
            return ">"
        # Turn user input into a command, with arguments.
        input_list = user_input.split()
        command = input_list[0]
        args = input_list[1:]
        
        # Handle tick if needed.
        tick_message = process_ticks(self.player, self.db)
        if tick_message:
            print(tick_message)

        # Alias directions.
        command = self.aliases.get(command, command)
        # Did the user quit?
        if command == "quit":
            self.quit()
            return "Farewell. Return soon."
        # Check the commands database and execute the command if it's in there (right now, this is a tiny database, but more will come.)
        if command in self.commands:
            return self.commands[command].execute(self.player, self.db, args)

        # Next, we have room exit lookup. This draws from the classes built in models.py earlier.
        room = self.player.get_current_room(self.db)
        if not room:
            return "You are nowhere."
        exits = self.player.get_current_room(self.db).get_exits(self.db)
        exit_directions = [row["direction"] for row in exits]
        # If the command's in there, we move!
        if command in exit_directions:
            moved = self.player.move(self.db, command)
            if moved:
                return self.player.get_current_room(self.db).describe(self.db)
            else:
                return "You can't go that way."

        # TODO: room special commands
        # not implemented yet. an example of this might be "dig" in a room where there's treasure to be found for the digging.

        return "Unknown command."

    def _display_output(self, output):
        """Display output to the player."""
        if output:
            print(output)

    def quit(self):
        """Save and exit."""
        self.player.save(self.db)
        self.is_running = False
