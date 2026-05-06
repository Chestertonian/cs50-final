"""
game/skills/base.py
 
Defines the base class for all Skills.
 
Every skill (active or passive) is an instance of Skill with an
execute() method that holds the actual effect logic.
 
Active skills:  player triggers them by typing a command.
Passive skills: the combat loop (or some other thing) calls them automatically.
"""
 
 
class Skill:
    def __init__(self, row):
        """
        Build a Skill from a DB row (sqlite3.Row or dict-like).
        """
        self.id           = row["id"]
        self.name         = row["name"]          # internal key: 'magic_missile'
        self.display_name = row["display_name"]  # player-facing: 'Magic Missile'
        self.description  = row["description"]
        self.guild        = row["guild"]
        self.min_level    = row["min_level"]
        self.power_cost   = row["power_cost"]
        self.skill_type   = row["skill_type"]    # 'active' or 'passive'
        self.trigger      = row["trigger"]        # None, 'each_round', 'on_hit', etc.
 
    def player_can_use(self, player):
        """
        Returns (bool, reason_string).
        Checks guild and level. Power is checked separately before execute().
        """
        if player.guild != self.guild:
            return False, f"Only {self.guild}s can use {self.display_name}."
        if player.level < self.min_level:
            return False, f"You need to be level {self.min_level} to use {self.display_name}."
        return True, None
 
    def execute(self, player, target, db):
        """
        Override this in *every* skill subclass.
        player: the Player object
        target: an NPC instance row (for active combat skills) or None
        db:     sqlite3 connection
        """
        raise NotImplementedError(f"{self.name} has no execute() defined.")