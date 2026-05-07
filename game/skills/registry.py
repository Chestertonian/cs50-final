
"""
game/skills/registry.py
 
Loads all skills from the DB at startup and stores them in two dicts:
"""

from game.skills.active.magic_missile import MagicMissile
from game.skills.active.fire_bolt import FireBolt
from game.skills.active.arcane_pulse import ArcanePulse
from game.skills.active.minor_heal import MinorHeal
from game.skills.active.fireball import Fireball
from game.skills.active.lightning_bolt import LightningBolt
from game.skills.active.web import Web
from game.skills.active.invisibility import Invisibility
from game.skills.active.greater_magic_missile import GreaterMagicMissile
from game.skills.active.greater_fireball import GreaterFireball
from game.skills.active.jab import Jab
from game.skills.active.strike import Strike
from game.skills.active.slash import Slash
from game.skills.active.shield import Shield
from game.skills.active.mage_armor import MageArmor
from game.skills.active.flame_shield import FlameShield
from game.skills.active.slow import Slow
from game.skills.active.arcane_blast import ArcaneBlast
from game.skills.active.stoneskin import Stoneskin
from game.skills.active.true_sight import TrueSight
from game.skills.active.recall import Recall
from game.skills.active.mass_slow import MassSlow
from game.skills.active.meteor_storm import MeteorStorm
from game.skills.active.swift_feet import SwiftFeet
from game.skills.active.earthen_fist import EarthenFist
from game.skills.active.arcane_drain import ArcaneDrain
from game.skills.active.mirror_image import MirrorImage
from game.skills.active.arcane_weakness import ArcaneWeakness
from game.skills.active.cataclysm import Cataclysm

SKILL_CLASS_MAP = {
    "magicmissile": MagicMissile,
    "firebolt":     FireBolt,
    "arcanepulse":  ArcanePulse,
    "minorheal":    MinorHeal,
    "fireball":     Fireball,
    "lightningbolt": LightningBolt,
    "web": Web,
    "invisibility":        Invisibility,
    "greatermagicmissile": GreaterMagicMissile,
    "greaterfireball":     GreaterFireball,
    "jab": Jab,
    "slash": Slash,
    "strike": Strike,
    "shield": Shield,
    "magearmor": MageArmor,
    "flameshield": FlameShield,
    "slow": Slow,
    "arcaneblast": ArcaneBlast,
    "stoneskin": Stoneskin,
    "truesight": TrueSight,
    "recall": Recall,
    "massslow": MassSlow,
    "meteorstorm": MeteorStorm,
    "swiftfeet": SwiftFeet,
    "earthenfist":    EarthenFist,
    "arcanedrain":    ArcaneDrain,
    "mirrorimage":  MirrorImage,
    "arcaneweakness": ArcaneWeakness,
    "recall": Recall,
    "cataclysm": Cataclysm,
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