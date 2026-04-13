from game.commands.base import Command

class SaveCommand(Command):
    def execute(self, player, db, args):
        try:
            player.save(db)
            print("Saved.")
            # TODO: Save timer?
        except:
            print("Something went wrong.")