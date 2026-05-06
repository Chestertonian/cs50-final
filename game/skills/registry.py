
"""
game/skills/registry.py
 
Loads all skills from the DB at startup and stores them in two dicts:
 
  ACTIVE_SKILLS  = { 'magic_missile': <MagicMissile obj>, ... }
  PASSIVE_SKILLS = { 'each_round': [<obj>, ...], 'on_hit': [...] }
"""

from game.skills.active.magic_missile import MagicMissile
from game.skills.active.fire_bolt import FireBolt
from game.skills.active.arcane_pulse import ArcanePulse
from game.skills.active.minor_heal import MinorHeal
from game.skills.active.fireball import Fireball
from game.skills.active.lightning_bolt import LightningBolt
from game.skills.active.web import Web
from game.skills.active.shock import Shock
from game.skills.active.invisibility import Invisibility
from game.skills.active.greater_magic_missile import GreaterMagicMissile
from game.skills.active.greater_fireball import GreaterFireball
from game.skills.active.jab import Jab
from game.skills.active.strike import Strike
from game.skills.active.slash import Slash



SKILL_CLASS_MAP = {
    "magicmissile": MagicMissile,
    "firebolt":     FireBolt,
    "arcanepulse":  ArcanePulse,
    "minorheal":    MinorHeal,
    "fireball":     Fireball,
    "lightningbolt": LightningBolt,
    "web": Web,
    "shock": Shock,
    "invisibility":        Invisibility,
    "greatermagicmissile": GreaterMagicMissile,
    "greaterfireball":     GreaterFireball,
    "jab": Jab,
    "slash": Slash,
    "strike": Strike,
}
 
# These get populated by load_skills() at startup.
ACTIVE_SKILLS  = {}   # { name: Skill instance }
PASSIVE_SKILLS = {}   # { trigger: [Skill instance, ...] }
 
 
def load_skills(db):
    """
    Call this once at game startup, after your DB connection is open.
    Reads every row from the skills table, finds the matching class,
    and registers it in the right dict.
    """
    rows = db.execute("SELECT * FROM skills").fetchall()
 
    for row in rows:
        name = row["name"]
 
        if name not in SKILL_CLASS_MAP:
            # Skill exists in DB but has no implementation yet — skip silently.
            # This lets you seed future skills in the DB without crashing.
            print(f"[skills] Warning: '{name}' is in DB but has no class in SKILL_CLASS_MAP.")
            continue
 
        cls = SKILL_CLASS_MAP[name]
        skill = cls(row)  # passes the DB row to Skill.__init__()
 
        if skill.skill_type == "active":
            ACTIVE_SKILLS[name] = skill
 
        elif skill.skill_type == "passive":
            trigger = skill.trigger or "each_round"
            if trigger not in PASSIVE_SKILLS:
                PASSIVE_SKILLS[trigger] = []
            PASSIVE_SKILLS[trigger].append(skill)
 
 
def get_player_skills(player):
    """
    Returns a list of all skills the player currently qualifies for
    (right guild, high enough level). Useful for a 'skills' command.
    """
    all_skills = list(ACTIVE_SKILLS.values()) + [
        s for bucket in PASSIVE_SKILLS.values() for s in bucket
    ]
    return [s for s in all_skills if s.guild == player.guild and player.level >= s.min_level]