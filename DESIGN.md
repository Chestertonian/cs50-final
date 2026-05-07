# Design Document

## Overview
Wayfarer is an old-school text-based adventure game, a bit like [Zork](https://en.wikipedia.org/wiki/Zork), based on the classic tropes of fantasy: dragons, fireballs, caves, wizards, goblins. The basic final goal of the project was to create a playable game -- one without a defined outcome, but hopefully with a lot of adventure to be had. 

## Motivation
I wanted to build a project that I would enjoy working on, and definitely succeeded in that! I also wanted to have a project that would be very easy to add features to if I wanted to -- there wasn't a single defined outcome. Also, it didn't involve doing a lot of frontend work, which I wasn't excited about doing.

## Architecture
High-level structure of the system.

- Major components (e.g., client, server, database, engine)
- How they interact
- Any important design patterns

(Optional diagram)

## Data Model / Schema
Explain your database or data structures.

- Tables / models
- Key fields
- Relationships
- Why this structure was chosen

## Core Features
Break down major functionality.

### Feature 1 (e.g., Authentication System)
- How it works
- Key files/functions involved

### Feature 2 (e.g., Combat System)
- Mechanics
- Flow of execution

(Repeat as needed)

## Game / Application Flow
Describe how a user interacts step-by-step.

Example:
1. User logs in
2. Enters world
3. Moves / interacts
4. System processes ticks/combat/events

## Key Design Decisions
Important tradeoffs or architecture choices.

- Why you used X instead of Y
- What you optimized for (simplicity, extensibility, performance, etc.)

## Algorithms and Systems
Explain any non-trivial logic.

- Combat resolution
- Movement system
- Tick system
- Procedural generation (if applicable)

## File Structure
Brief explanation of important files.

- `models.py` – core game logic
- `engine.py` – command processing
- etc.

## Challenges
What was difficult and how you solved it.

## Future Improvements
What you would add or improve with more time.


## Outcomes Reached
I met all of my good outcomes. 
In terms of better outcomes, I decided that having doors which you could "open" and "close" wasn't my priority. I decided the same thing about stores -- useful, but not key.
In terms of best outcomes, I created health/movement points and combat. I actually decided that switching to PostgreSQL was definitely overkill, so that was dropped from my goals. I even hit one of my "very ideal" goals: creating levels. The game has an entire class, with a progression from level 1-level 20 (although a few spells don't quite work yet.)

Overall, I achieved all of the goals that I wanted to.

- New systems
- Refactoring ideas
- Scalability improvements

## Acknowledgments
Any resources, libraries, or inspiration.

## Project Structure

<details>
<summary>Click to expand full directory tree</summary>

```text
cs50-final
│   .gitignore
│   DESIGN.md
│   LICENSE
│   plan.md
│   README.md
│   __main__.py
│
├── creative-information
│       monastery_idea.txt
│       world_info.txt
│
├── db
│       game.db
│       schema.sql
│
├── game
│   │   .gitignore
│   │   character_creation.py
│   │   engine.py
│   │   helpers.py
│   │   login.py
│   │   models.py
│   │   move.py
│   │   spawner.py
│   │   stats.py
│   │   tick.py
│   │   ui.py
│   │   wealth.py
│   │   __init__.py
│   │
│   ├── combat
│   │       combat_loop.py
│   │       combat_state.py
│   │       flee.py
│   │
│   ├── commands
│   │       ask.py
│   │       base.py
│   │       DevAddHealth.py
│   │       DevAddMove.py
│   │       DevAddSP.py
│   │       DevClearCombat.py
│   │       DevDeathCommand.py
│   │       drop.py
│   │       equip.py
│   │       flee.py
│   │       get.py
│   │       health.py
│   │       help.py
│   │       inventory.py
│   │       kill.py
│   │       listen.py
│   │       look.py
│   │       powers.py
│   │       remove.py
│   │       save.py
│   │       say.py
│   │       score.py
│   │       smell.py
│   │       time.py
│   │       wealth.py
│   │       __init__.py
│   │
│   ├── helpfiles
│   │       arcane_drain.txt
│   │       arcane_pulse.txt
│   │       arcane_weakness.txt
│   │       ask.txt
│   │       cataclysm.txt
│   │       changelog.txt
│   │       combat.txt
│   │       drop.txt
│   │       earthen_fist.txt
│   │       equip.txt
│   │       fireball.txt
│   │       fire_bolt.txt
│   │       flameshield.txt
│   │       get.txt
│   │       greater_fireball.txt
│   │       greater_magic_missile.txt
│   │       guild.txt
│   │       help.txt
│   │       inventory.txt
│   │       invisibility.txt
│   │       jab.txt
│   │       level.txt
│   │       light.txt
│   │       lighting.txt
│   │       lightning_bolt.txt
│   │       look.txt
│   │       lore.txt
│   │       mage_armor.txt
│   │       magic_missile.txt
│   │       mass_slow.txt
│   │       meteor_storm.txt
│   │       minor_heal.txt
│   │       mirror_image.txt
│   │       movement.txt
│   │       npc.txt
│   │       race.txt
│   │       recall.txt
│   │       regeneration.txt
│   │       remove.txt
│   │       save.txt
│   │       score.txt
│   │       senses.txt
│   │       shield.txt
│   │       shock.txt
│   │       slash.txt
│   │       sp.txt
│   │       spells.txt
│   │       stoneskin.txt
│   │       strike.txt
│   │       swift_feet.txt
│   │       time.txt
│   │       true_sight.txt
│   │       web.txt
│   │       world.txt
│   │       xp.txt
│   │
│   ├── skills
│   │   │   base.py
│   │   │   registry.py
│   │   │   __init__.py
│   │   │
│   │   ├── active
│   │   │       arcane_blast.py
│   │   │       arcane_drain.py
│   │   │       arcane_pulse.py
│   │   │       arcane_weakness.py
│   │   │       cataclysm.py
│   │   │       earthen_fist.py
│   │   │       fireball.py
│   │   │       fire_bolt.py
│   │   │       flame_shield.py
│   │   │       greater_fireball.py
│   │   │       greater_magic_missile.py
│   │   │       invisibility.py
│   │   │       jab.py
│   │   │       lightning_bolt.py
│   │   │       mage_armor.py
│   │   │       magic_missile.py
│   │   │       mass_slow.py
│   │   │       meteor_storm.py
│   │   │       minor_heal.py
│   │   │       mirror_image.py
│   │   │       recall.py
│   │   │       shield.py
│   │   │       slash.py
│   │   │       slow.py
│   │   │       stoneskin.py
│   │   │       strike.py
│   │   │       swift_feet.py
│   │   │       true_sight.py
│   │   │       web.py
│   │   │       __init__.py
│   │
│   ├── text_files
│   │       ascii_art.txt
│   │       guilds_screen.txt
│   │       races_screen.txt
│   │
│   └── __init__.py
│
└── __main__.py
```
</details>
