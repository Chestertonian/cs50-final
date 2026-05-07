# Design Document

## Overview
Wayfarer is an old-school text-based adventure game, a bit like [Zork](https://en.wikipedia.org/wiki/Zork), based on the classic tropes of fantasy: dragons, fireballs, caves, wizards, goblins. The basic final goal of the project was to create a playable game -- one without a defined outcome, but hopefully with a lot of adventure to be had. 

## Motivation
I wanted to build a project that I would enjoy working on, and definitely succeeded in that! I also wanted to have a project that would be very easy to add features to if I wanted to -- there wasn't a single defined outcome. Also, it didn't involve doing a lot of frontend work, which I wasn't excited about doing.

## Architecture
The engine (engine.py) is the heart of the game. It holds the player object, the database connection, and a dictionary mapping command strings to command objects. Each iteration it reads a line, splits off the verb, looks it up in that dictionary, and calls .execute(player, db, args).

The database is the 'world.' There's no in-memory persistent game world to speak of — rooms, items, NPCs, exits all live in SQLite and are queried as needed. This means the world persists automatically. The tradeoff to this, of course, is that almost every action touches the database. I tried to minimize this by using object-oriented programming -- Python classes with a lot of methods -- to keep raw SQL as limited as possible.

Models (models.py) are a object layer over the DB rows. They give, for example, "player.health" instead of just getting things from the rows, and methods like item.equip(slot) instead of raw SQL in the command files (except for when I forgot).

Commands (under commands/) are self-contained classes, one per every file, all inheriting from base.py (base command structure). Each implements a single 'execute' method. The engine doesn't "know"  what a command does. The engine just calls execute and prints the return value. This means adding new commands does not require touching the engine.

Combat (combat/) is split into two main pieces. CombatState is an object that tracks who the player is fighting. It's in memory, not SQL. Combat_loop.py contains the round logic: player attacks, monster counterattacks, damage is calculated, death is handled, etc.

The spawner (spawner.py) spawns from the item_spawns and npc_spawns tables in SQL, creating new instances from templates.


## Data Model / Schema
The core distinctive of the way I handled data is this: almost everything in the world is an instance of a template. For example, Threna the barkeeper, the NPC in the tavern, is actually an instance of a template. This might seem like overkill in this case, but consider the following case.

Presumably, the game will have a lot of goblins, since there's a goblin lair. If I need to create an entirely new "idea" of a goblin every time I spawn one, that ends up being a hassle -- plus it causes problems, like if I want to edit how much damage goblins in general do. If I have a template for a goblin and individual instances (think of the idea of a goblin vs individual goblins running around), this makes that entire thing much, much easier. So for NPCs (monsters like goblins), I have 
- npc_templates, containing things like the maximum health, what it looks like, if it's aggressive.
- npc_instances, containing things like the current health of an instance or its location
- and npc_spawns, containing the "rules" for where NPCs are spawned.

I have a very similar system for items, with the added wrinkle that there are different types of items (armor, weapons, food, etc), so I used the primary key idea for that.

The world is made of rooms and exits -- both of these are pretty simple.


## Core Features
The best way to experience the core features is to try playing the game! Create a character (wizard is best), find the abandoned house and its secret room, take the armor from it, wear it, and go fight deer. Or fight deer without armor. Or try to find the dragon. You'll die.

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
Yes, this is an absolutely massive folder.
Creative-information should basically be ignored. Nothing cs50 relevant here.
db has the actual game database and the schema.
Everything interesting is under game.
character_creation, login, and stats are all among the first things I wrote. They're for the initial screen of the game and creating a character.
Engine is key -- it includes the parser and game engine.
Wealth is a bunch of unrelated helpers that aren't really being used now, and are for future incorporation.
Spawner is responsible for spawning NPCs and items from SQL tables.
Models: a beast of a file! (το θηριον.) It has almost all of the "db.execute" in the project. It's where *most* interaction with the SQL occurs, and where the models are all created for things like items, NPCs, rooms, and players, each with a whole host of methods accompanying it. Worth noting that there are also things in there which aren't being used currently.
Helpers: Many things that I did not put elsewhere. Some of them should likely be elsewhere.
**/combat**
Has combat_loop, which handles most of the combat things.
Combat_state, which is responsible for starting and ending combat (all stored in memory, not to the database.)
**/commands**
All of the commands are here. There are... a lot, so I won't go over all of them.
**All of the Dev commands are, by default, commented out in engine.py, so that they can't be used. They're for testing purposes (I left them in there for graders' purposes, since they might be useful.**
**/helpfiles**
Literally just a ton of .txt files. Boring.
**/skills**
The base skill class.
Registry of all skills (if a skill isn't in there, it isn't being used).
**/active**
Why active? I anticipate there being passive skills at some point (e.g. "Enduring: You regenerate movement slightly faster.")
This contains all of the wizard powers, as well as a power for each other class excepting the cleric. If you want to test this game, play a wizard.
**/text_files**
What it says. Various textfiles that aren't helpfiles.


## Challenges
Probably *the* biggest challenge that I encountered was the instance-template problem. I couldn't figure out how to make all of those systems work until I had my eureka moment.

The other one surrounds combat: I would've loved to have it be real-time (every 3 seconds or so, weapon attacks occur.) Unfortunately, that wasn't doable without threading. If I had been aware of this earlier, I would probably have tried to add some level of threading from the beginning -- once I figured out that I'd have to do that, it was too late to go back and add something of that magnitude.

## Future Improvements
I definitely want to work on this more, and make it a more enjoyable game.
*I want to add*
- The other classes (rogue, warrior, cleric, and ranger.) I think this will be much easier to do now that I have one fully working class.
- NPCs that drop items on death.
- Working food, lighting system.
- Working economic system.
- More areas. (There's actually about 30 unreachable rooms in the game now that I just didn't have time to add exits for :( )
- Better weapons.
- Quests.
- Multiplayer. (This would be a vastly enjoyable challenge!)


## Outcomes Reached
I met all of my good outcomes. 
In terms of better outcomes, I decided that having doors which you could "open" and "close" wasn't my priority. I decided the same thing about stores -- useful, but not key.
In terms of best outcomes, I created health/movement points and combat. I actually decided that switching to PostgreSQL was definitely overkill, so that was dropped from my goals. I even hit one of my "very ideal" goals: creating levels. The game has an entire class, with a progression from level 1-level 20 (although a few spells don't quite work yet.)

Overall, I achieved all of the goals that I wanted to.

## AI Use Note
I used AI fairly extensively in my workflow, specifically Claude Sonnet 4.6. Its project prompt was "I'm working on my CS50 final project -- creating a small single player MUD-type game in Python, using sqlite3 to deal with rooms, objects, exits, etc." It also had access to my schemas and file tree. Overall, it was very helpful, although it did make some notable mistakes, and want to add some absolutely unnecessary safety checks at random points. Without it, though, I definitely would not have ended up with 4000+ lines of code!

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
