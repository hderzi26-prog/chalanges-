# Dragon Quest - 20% Project

A collection of fun dragon-themed games built for my 20% project time. Features both a Pygame desktop version and an HTML5 Canvas web version.

## 🎮 Games Included

### 1. Dragon Quest (Pygame) - Desktop Version
A lightweight top-down free-roam dragon game built with Pygame. Explore the overworld, breathe fire, defeat roaming enemies, collect treasure, and survive.

**Quick Start:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python dragon_game/main.py
```

### 2. Dragon Quest (Web) - Browser Version
An enhanced HTML5 Canvas version with levels, bosses, XP system, abilities, and minimap. Play directly in your browser!

**Quick Start:**
```bash
# Option 1: Open directly
open dragon_web/index.html

# Option 2: Run local server (recommended)
cd dragon_web && python3 -m http.server 8000
# Then visit http://localhost:8000
```

## 🎯 Features

### Core Gameplay
- **Free-roam exploration** with camera following your dragon
- **Fire breath combat** with cone-shaped projectiles
- **Enemy AI** that patrols and chases when you get close
- **Pickups**: gold (score) and hearts (health)
- **Dash ability** with stamina management

### Web Version Extras
- **Level system** with waves and boss fights
- **XP and leveling** with ability unlocks
- **Two special abilities**:
  - Roar (1): Stuns nearby enemies
  - Nova (2): Radial fire attack (unlocks at level 3)
- **Minimap** showing player, enemies, boss, and pickups
- **Scaling difficulty** - enemies and bosses get stronger each level

## 🕹️ Controls

### Desktop (Pygame)
- WASD / Arrow Keys: Move the dragon
- Shift: Dash (short speed burst, stamina-limited)
- Space: Breathe fire (cooldown)
- P: Pause / Resume
- H or ?: Toggle help overlay
- Esc or Q: Quit

### Web (HTML5)
- WASD / Arrow Keys: Move the dragon
- Shift: Dash
- Space: Breathe fire
- 1: Roar (stun enemies)
- 2: Nova (radial fire - unlocks at level 3)
- P: Pause
- H or ?: Toggle help
- Esc: Quit tab

## 🛠️ Technical Details

- **No external assets** - all visuals generated programmatically
- **Responsive design** - works on different screen sizes
- **Performance optimized** - efficient collision detection and rendering
- **Cross-platform** - Pygame version works on Windows/Mac/Linux, web version works in any modern browser

## 📁 Project Structure

```
fun/
├── dragon_game/           # Pygame desktop version
│   └── main.py
├── dragon_web/           # HTML5 Canvas web version
│   ├── index.html
│   └── game.js
├── requirements.txt      # Python dependencies
└── README.md           # This file
```

## 🎨 Game Design

This project explores different approaches to game development:
- **Pygame**: Traditional desktop game development with Python
- **HTML5 Canvas**: Modern web-based game development with JavaScript
- **Procedural generation**: Dynamic world creation and enemy spawning
- **Game mechanics**: Combat, progression, and player feedback systems

## 🚀 Future Enhancements

Potential additions for future 20% time:
- Multiplayer support
- More enemy types and boss patterns
- Tile-based level system
- Sound effects and music
- Save/load system
- Mobile touch controls

---

*Built with ❤️ during 20% project time*


