from game.commands.base import Command


class SayCommand(Command):
    def execute(self, player, db, args):
        if not args:
            return "Say what?"

        message = " ".join(args).strip()
        message = message.capitalize()

        if not message.endswith(("!", "?", ".")):
            message += "."

        return f'You say, "{message}"'
