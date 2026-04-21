# game/commands/ask.py

from game.models import NpcInstance, find_item_by_name
from game.commands.base import Command
from game.helpers import wrap_text, parse_target_and_index

class AskCommand(Command):
    def execute(self, player, db, args):

        if len(args) < 3:
            return "Ask who about what?"

        # args might be: ['goblin', 'about', 'quest'] or ['goblin', '2', 'about', 'quest']
        # so we parse just the NPC part (everything before 'about')
        about_index = args.index("about") if "about" in args else 1
        npc_args = args[:about_index]
        keyword = args[about_index + 1] if about_index + 1 < len(args) else None

        if not keyword:
            return "Ask who about what?"

        npc_name, index = parse_target_and_index(npc_args)

        npcs = NpcInstance.get_instances_in_room(player.current_room_id, db)
        npc = find_item_by_name(npc_name, npcs, index)

        if npc is None:
            return f"You don't see '{npc_name}' here."

        response = npc.get_dialogue(keyword, db)

        if not response:
            return f"{npc.name} doesn't respond."

        return wrap_text(response)