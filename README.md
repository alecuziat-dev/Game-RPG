# Mini-RPG Project - Le Donjon de Naheulbeuk

Welcome to the repository of my very first video game project! This is a text-based mini-RPG with a graphical user interface (GUI), developed in Python and inspired by the crazy and humorous universe of the famous French audio saga *Le Donjon de Naheulbeuk*.

This project is part of my self-taught learning journey into programming, Python development, and Graphical User Interface (GUI) management.

---

## Current Features

- **Complete Character Creation:** Customize or randomly generate your character's gender, race (Human, Elf, Dark Elf, Ogre, Dwarf, Therianthrope, Orc), and class (Warrior, Mage, Bishop, Assassin, Paladin, Ranger, Minstrel).
- **Dynamic Stats System:** Core attributes (Courage, Strength, Intelligence, Agility) are influenced by your race, your class, and your equipped gear.
- **Procedural Exploration:** Progress through **30** randomly generated rooms across three branching paths (each with its own risk/reward balance), featuring traps, treasure chests, wandering merchants, and magical fountains.
- **Visual Dungeon Map:** A real-time map tracks your progress through all 30 rooms, highlighting the mid-boss and final boss locations.
- **Difficulty Levels:** Choose Easy, Normal, or Hard before starting — it directly scales monster strength throughout the run.
- **Turn-Based Combat:** Fight a diverse bestiary leading up to a mid-dungeon boss (**Reivax**, Zangdar's sneaky second-in-command) and the final showdown against **Zangdar** himself — both with unique attack patterns and an enrage phase below 40% HP.
- **Unique Skills & Spells:** Two special abilities per class, including a devastating ultimate skill that unlocks automatically upon reaching Level 2.
- **Equipment & Inventory:** Weapons, armor, helmets, and boots (Common, Rare, Legendary) with real stat impact, managed through a full inventory screen.
- **Consumables:** Healing potions, mana potions, and food rations, usable both in and out of combat.
- **Wandering Merchant:** Buy gear and consumables, or sell items from your inventory for gold.
- **Multi-Slot Save System:** Save and load your progress across three independent save slots.
- **Visual HP/Mana/XP Bars:** Color-coded progress bars replace plain numbers for a clearer read of your state — including a live monster health bar during combat.
- **Character Portraits:** Illustrated portraits matching your character's race and gender (falls back to a generated icon if no image is provided).
- **Dynamic Music:** Separate ambient and combat music tracks that switch automatically based on game context.
- **End-of-Run Summary:** A recap screen (monsters defeated, gold earned, rooms cleared, time played) on both victory and game over.
- **Text-Based RP Events:** Integrated humor and situational choices when encountering patrols, tavern visits, and more.

---

## Visuals & Media

The game features dynamic image and audio displays throughout a playthrough:

- **`victoire.png`**: Displayed when you defeat Zangdar and recover the twelfth Statuette of Gladeulfeurha.
- **`gameover.png`**: Displayed to honor the tragic demise of your party if your HP drops to zero.
- **`musique_ambiance.mp3`**: Background music during exploration, menus, the tavern, and the merchant.
- **`musique_combat.mp3`**: Music that takes over automatically as soon as a fight starts.
- **`<Race>_h.png` / `<Race>_f.png`**: Character portraits (one male and one female version per race).

> **Important:** All image and audio assets must sit in the exact same directory as the main Python script. File names are matched case-insensitively and tolerate a few common extensions (`.png`/`.jpg` for images, `.mp3`/`.ogg`/`.wav` for music) — but a missing or misnamed file simply falls back gracefully (a generated portrait, silent audio, or an in-game message telling you exactly what went wrong).

---

## Tech Stack

- **Language:** Python 3
- **Standard Libraries:** `tkinter` (GUI), `random`, `os`, `json` (save system), `time`
- **Third-Party Libraries:**
  - `Pillow` (PIL) — image loading, resizing, and processing
  - `pygame` — audio playback (ambient and combat music)
- **Tools:** Git & GitHub for version control

---

## How to Run the Project

To test the game on your local machine, follow these steps:

### 1. Clone the repository

```bash
git clone https://github.com/alecuziat-dev/Game-RPG.git
cd Game-RPG
```

### 2. Install dependencies

```bash
pip install Pillow pygame
```

### 3. Run the game

```bash
python naheulbeuk_rpg.py
```

The game will still launch without `pygame` installed — it just runs silently, without music.

---

## Project Status

This project started as a simple calculator idea and grew into a full mini-RPG. It's now considered feature-complete and stable. Ongoing work is limited to bug fixes and polish rather than major new systems.
