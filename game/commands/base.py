# game/commands/base.py
# The base Command class. All commands inherit from this. (Courtesy of Claude for this part of the structure.)

class Command:
    def execute(self, player, db, args):
        raise NotImplementedError(
            "Command subclasses must implement execute().")
