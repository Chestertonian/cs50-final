# game/commands/help.py

from game.commands.base import Command
from game.helpers import wrap_text
from pathlib import Path

class HelpCommand(Command):
    def execute(self, player, db, args):
        if not args:
            self.show_all_help(player, db)
        else:
            self.show_specific_help(player, db, args[0])

    def show_all_help(self, player, db):
        """
        Lists all available help topics by scanning the helpfiles directory.
        """
        current_file_dir = Path(__file__).parent
        help_dir = current_file_dir.parent / "helpfiles"
        
        if not help_dir.exists() or not help_dir.is_dir():
            print("\n--------- Help Index ---------\n")
            print("No help directory found. Please contact an administrator.")
            print("------------------------------\n")
            return

        try:
            txt_files = [f.stem for f in help_dir.iterdir() if f.is_file() and f.suffix == ".txt"]
            topics = sorted(txt_files)
        except PermissionError:
            print("\n--------- Help Index ---------\n")
            print("Permission denied: Unable to read help directory.")
            print("------------------------------\n")
            return
        except Exception as e:
            print(f"\nError scanning help directory: {e}\n")
            return

        if not topics:
            print("\n--------- Help Index ---------\n")
            print("No help topics available.")
            print("------------------------------\n")
            return

        print("\n--------- Available Help Topics ---------\n")
        print("Type 'help <topic>' for details.\n")
        
        # Build the list without brackets
        lines = []
        current_line = ""
        
        for topic in topics:
            # Removed the brackets here
            item = topic 
            
            if not current_line:
                current_line = item
            elif len(current_line) + len(item) + 2 <= 60:
                current_line += f", {item}"
            else:
                lines.append(current_line)
                current_line = item
        
        if current_line:
            lines.append(current_line)

        for line in lines:
            print(wrap_text(line, width=60, indent=0))

        print(f"\nTotal topics: {len(topics)}")
        print("---------------------------------------\n")

    def show_specific_help(self, player, db, topic):
        filename = topic.strip().lower() + ".txt"
        current_file_dir = Path(__file__).parent
        help_dir = current_file_dir.parent / "helpfiles"
        file_path = help_dir / filename

        if not file_path.is_file():
            print(f"No help file found for '{topic}'.")
            return

        try:
            with open(file_path, "r") as f:
                content = f.read()
                print(f"\n--------- Help: {topic.upper()} ---------\n")
                print(wrap_text(content, width=48, indent=0))
                print(f"------------------------------------\n")
        except IOError as e:
            print(f"Error reading help file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
