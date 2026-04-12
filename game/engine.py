# game/engine.py
class GameEngine:
    """Core game engine responsible for running the main loop."""

    def __init__(self):
        """Initialize game state."""
        self.is_running = True

    def run(self):
        """Start the main game loop."""
        self._print_welcome()

        while self.is_running:
            user_input = self._get_input()
            output = self._process_input(user_input)
            self._display_output(output)

    def _print_welcome(self):
        """Display a welcome message."""
        print("Welcome to the game!")
        print("Type 'help' for a list of commands.\n")

    def _get_input(self):
        """Get input from the player."""
        return input("> ").strip()

    def _process_input(self, user_input):
        """
        Process user input.

        For now, this is a placeholder.
        Later, this will call the command system.
        """
        if not user_input:
            return "Please enter a command."

        # Temporary behavior (replace with command system later)
        if user_input.lower() in ("quit", "exit"):
            self.is_running = False
            return "Goodbye!"

        return f"You entered: {user_input}"

    def _display_output(self, output):
        """Display output to the player."""
        if output:
            print(output)
