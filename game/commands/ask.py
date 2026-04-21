from game.models import NpcInstance, find_item_by_name
from game.commands.base import Command
from game.helpers import wrap_text

class AskCommand(Command):
    def execute(self, player, db, args):

        if len(args) < 3:
            return "Ask who about what?"

        target = args[0]
        keyword = args[2]  # assumes: ask <npc> about <topic>

        npcs = NpcInstance.get_instances_in_room(player.current_room_id, db)

        npc = find_item_by_name(target, npcs)

        if npc is None:
            return f"You don't see '{target}' here."

        if isinstance(npc, list):
            return "Multiple matches: " + ", ".join(n.name for n in npc)
        if not npc:
            return f"You don't see '{target}' here."

        response = npc.get_dialogue(keyword, db)

        if not response:
            return f"{npc.name} doesn't respond."

        return wrap_text(response)