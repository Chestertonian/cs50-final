# Design Document

## Overview
Wayfarer is an old-school text-based adventure game, a bit like [Zork](https://en.wikipedia.org/wiki/Zork), based on the classic tropes of fantasy: dragons, fireballs, caves, wizards, goblins. The basic goal of the project was to create a playable game -- one without a defined outcome, but hopefully with a lot of adventure to be had. 

## Motivation
Why you built it. What problem it solves or what inspired it.

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
