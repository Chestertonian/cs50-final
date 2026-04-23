# game/commands/save.py

from game.commands.base import Command

class SaveCommand(Command):
    def execute(self, player, db, args):
        try:
            player.save(db)
            print("Saved.")
        except:
            print("Something went wrong.")