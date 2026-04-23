# game/commands/listen.py

from game.commands.base import Command

class ListenCommand(Command):
    def execute(self, player, db, args):
        if not args:
            room=player.get_current_room(db)
            return room.sound
        
        if args:
            # listening to a specific item/npc
            # not implemented yet
            return "You can't listen to that yet."
