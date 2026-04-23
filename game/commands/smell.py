# game/commands/smell.py

from game.commands.base import Command

class SmellCommand(Command):
    def execute(self, player, db, args):
        if not args:
            room=player.get_current_room(db)
            return room.smell
        
        if args:
            # smelling a specific item/npc
            # not implemented yet
            return "You can't smell that yet."
