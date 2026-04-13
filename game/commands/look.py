from game.commands.base import Command

class LookCommand(Command):
    def execute(self, player, db, args):
        if not args:
            room=player.get_current_room(db)
            return room.describe(db)
        
        if args:
            # looking at a specific item/npc
            # not implemented yet
            return "You can't look at that yet."
