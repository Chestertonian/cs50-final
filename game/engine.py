# game/engine.py
import time

from game.models import Player, Room
from game.tick import process_ticks
from game.combat.combat_loop import run_combat_round, handle_npc_death
from game.commands.look import LookCommand
from game.commands.save import SaveCommand
from game.commands.score import ScoreCommand
from game.commands.time import TimeCommand
from game.commands.smell import SmellCommand
from game.commands.listen import ListenCommand
from game.commands.help import HelpCommand
from game.commands.get import GetCommand
from game.commands.drop import DropCommand
from game.commands.inventory import InventoryCommand
from game.commands.say import SayCommand
from game.commands.equip import EquipCommand
from game.commands.remove import RemoveCommand
from game.commands.health import HpCommand
from game.commands.ask import AskCommand
from game.commands.DevAddMove import AddMovementPointsCommand
from game.commands.wealth import WealthCommand
from game.commands.kill import KillCommand
from game.commands.flee import FleeCommand
from game.commands.powers import PowersCommand
from game.commands.DevClearCombat import DevClearCombatCommand
from game.commands.DevDeathCommand import DeathCommand
from game.commands.DevAddHealth import AddHealthPointsCommand
from game.commands.DevAddSP import AddSPCommand
from game.skills.registry import ACTIVE_SKILLS, load_skills


class GameEngine:
    """Core game engine responsible for running the main loop."""

    def __init__(self, db, player):
        """Initialize game state."""
        self.db = db
        self.player = player
        self.is_running = True
        self.commands = {
            "look": LookCommand(),
            "save": SaveCommand(),
            "score": ScoreCommand(),
            "time": TimeCommand(),
            "smell": SmellCommand(),
            "listen": ListenCommand(),
            "help": HelpCommand(),
            "get": GetCommand(),
            "drop": DropCommand(),
            "inventory": InventoryCommand(),
            "say": SayCommand(),
            "equip": EquipCommand(),
            "remove": RemoveCommand(),
            "hp": HpCommand(),
            "add_movement": AddMovementPointsCommand(),
            "add_sp": AddSPCommand(),
            "ask": AskCommand(),
            "wealth": WealthCommand(),
            "kill": KillCommand(),
            "clear_combat": DevClearCombatCommand(),
            "flee": FleeCommand(),
            "die": DeathCommand(),
            "add_health": AddHealthPointsCommand(),
            "powers": PowersCommand(),
        }
        self.aliases = {
            # directions
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            "u": "up",
            "d": "down",
            # commands
            "i": "inventory",
            "inv": "inventory",
            "l": "look",
            "p": "hp",
            "health": "hp",
            "a": "wealth",
            "attack": "kill",
        }
        self.last_combat_round = 0
        self.combat_round_delay = 0.1  # seconds between rounds

        # Load skills from DB into the registry.
        load_skills(db)
        self.active_skills = ACTIVE_SKILLS
        print("Loaded skills:", list(self.active_skills.keys()))


    def run(self):
        """Start the main game loop."""
        self._print_welcome()

        while self.is_running:
            user_input = self._get_input()
            output = self._process_input(user_input)
            self._display_output(output)

    def _print_welcome(self):
        """On boot, should display the room the player is in."""
        current_room = self.player.get_current_room(self.db)
        print(current_room.describe(self.db))

    def _get_input(self):
        """Get input from the player."""
        return input("> ").strip().lower()

    def _process_input(self, user_input):
        user_input = user_input.lower()
        if not user_input:
            if self.player.combat.is_in_combat():
                now = time.time()
                if now - self.last_combat_round >= self.combat_round_delay:
                    run_combat_round(self.player, self.db)
                self.last_combat_round = now
            return ">"

        input_list = user_input.split()
        command = input_list[0]
        args = input_list[1:]

        # Handle tick if needed.
        tick_message = process_ticks(self.player, self.db)
        if tick_message:
            print(tick_message)

        # Handle combat round if needed.
        if self.player.combat.is_in_combat():
            now = time.time()
            if now - self.last_combat_round >= self.combat_round_delay:
                run_combat_round(self.player, self.db)
                self.last_combat_round = now

        # Alias directions.
        command = self.aliases.get(command, command)

        # Did the user quit?
        if command == "quit":
            self.quit()
            return "Farewell. Return soon."

        # Check the commands dict and execute if found.
        if command in self.commands:
            return self.commands[command].execute(self.player, self.db, args)

        # --- Skill dispatch ---
        # Skills are typed directly: 'magicmissile', 'firebolt', etc.
        # The engine resolves the target; the skill handles the effect.
        if command in self.active_skills:
            skill = self.active_skills[command]

            # Check guild + level.
            can_use, reason = skill.player_can_use(self.player)
            if not can_use:
                return reason

            # Check power cost.
            if self.player.power < skill.power_cost:
                return f"You don't have enough power. ({self.player.power}/{self.player.max_power})"

            # Resolve target.
            target = None
            if self.player.combat.is_in_combat():
                # Already fighting — use the current combat target.
                target = self.db.execute(
                    "SELECT * FROM npc_instances WHERE id = ?",
                    (self.player.combat.primary_target_id,)
                ).fetchone()
            elif args:
                # Not in combat but player named something — try to start combat.
                target_name = " ".join(args).lower()
                target = self.db.execute(
                    """SELECT npc_instances.* FROM npc_instances
                       JOIN npc_templates ON npc_instances.template_id = npc_templates.id
                       WHERE npc_instances.room_id = ?
                       AND npc_instances.is_alive = 1
                       AND LOWER(npc_templates.name) LIKE ?""",
                    (self.player.current_room_id, f"%{target_name}%")
                ).fetchone()
                if not target:
                    return f"You don't see '{target_name}' here."
                self.player.combat.start_combat(target["id"], self.player)

            result = skill.execute(self.player, target, self.db)
            self.player.save(self.db)

            if result.get("killed"):
                print(result["message"])
                from game.models import NpcInstance
                for npc_id in result.get("killed_ids", [result["target_id"]]):
                    dead_npc = NpcInstance.get_by_id(self.db, npc_id)
                    if dead_npc:
                        handle_npc_death(self.player, dead_npc, self.db)
                return ""

            return result["message"]

        # --- Room exit lookup ---
        room = self.player.get_current_room(self.db)
        if not room:
            return "You are nowhere."
        exits = room.get_exits(self.db)
        exit_directions = [row["direction"] for row in exits]

        if command in exit_directions and self.player.combat.is_in_combat():
            return "One does not simply walk away from battle."

        if command in exit_directions:
            moved = self.player.move(self.db, command)
            if moved:
                return self.player.get_current_room(self.db).describe(self.db)
            else:
                return "You can't go that way."

        # TODO: room special commands

        return "Unknown command."

    def _display_output(self, output):
        """Display output to the player."""
        if output:
            print(output)

    def quit(self):
        """Save and exit."""
        self.player.save(self.db)
        self.is_running = False