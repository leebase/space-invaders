# Space Invaders Deluxe 🕹️

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A pixel-perfect recreation of the 1980 Taito Space Invaders Deluxe arcade game.

![Space Invaders Deluxe Screenshot](assets/screenshot.png)

## Features

- ✅ **Authentic arcade resolution:** 224×256 native, scaled 3× with nearest-neighbor filtering
- ✅ **CRT scanline overlay:** Pre-computed for that retro feel
- ✅ **All Deluxe exclusives:** Splitting aliens, rainbow bonus, inter-round cutscenes, color-changing invaders
- ✅ **Arcade-accurate timing:** March tempo, fire rates, UFO intervals all verified
- ✅ **Full sound suite:** 4-note march synchronized to visuals, all effects, UFO drone
- ✅ **Complete game shell:** Title screen, pause, high score initials entry

## Quick Start

### Prerequisites

- Python 3.12 or higher
- Linux, macOS, or Windows

### Installation

```bash
git clone <repository-url>
cd space-invaders
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Run the Game

```bash
space-invaders
```

Or using Python directly:

```bash
python -m space_invaders
```

## How to Play

### Controls

| Key | Action |
|-----|--------|
| **←** or **A** | Move cannon left |
| **→** or **D** | Move cannon right |
| **Space** | Fire (one bullet at a time) |
| **P** | Pause / Resume |
| **Esc** | Pause (during game) / Quit (at title screen) |
| **M** | Mute / Unmute sound |
| **Q** | Quit (when at title screen) |

### Objective

Destroy all 55 invaders before they reach the bottom of the screen. You have 3 lives. Protect the 4 bunkers — they absorb shots from both sides and erode pixel by pixel.

### Scoring

| Target | Points | Notes |
|--------|--------|-------|
| Squid (top row) | 30 | Fastest, smallest |
| Crab (middle 2 rows) | 20 | Medium size |
| Octopus (bottom 2 rows) | 10 | Largest, slowest |
| UFO | 50-300 | Cycles deterministically; 9th shot = 300 pts |
| Split Alien | 100 | Yellow zigzag ship; splits when hit |
| Split Piece | 50 | Two spawned from split alien |
| Rainbow Bonus | 500-1000 | Last alien from bottom rows |

### Game Flow

1. **Title Screen** — Watch the invader parade, press any key to start
2. **Gameplay** — Shoot invaders, dodge enemy fire, use bunkers for cover
3. **Cutscene** — Brief animation between rounds showing "ROUND N"
4. **Game Over** — Enter your initials if you achieved a high score!

### Pro Tips

- **UFO Exploit:** Count your shots! The score cycles through `[100, 50, 50, 100, 150, 100, 100, 50, 300, ...]` — hitting the UFO on your 9th shot (and every 15th after that) gives maximum points.
- **Rainbow Bonus:** Leave one invader from the bottom 2 rows as your final kill for 500 points. If it's in the bottom-left cell, you get 1000 points!
- **Split Alien:** The yellow zigzag ship appears every 20 seconds. Shoot it before it splits — the pieces are worth 50 points each but harder to hit.
- **Bunker Strategy:** Let the invaders erode the top of the bunkers while you shoot through the bottom.

## Development

### Run Tests

```bash
pytest                    # Run all tests
pytest -v                # Verbose output
pytest tests/test_grid.py -v   # Specific test file
```

### Code Quality

```bash
ruff check src/ tests/    # Lint check
ruff check --fix src/     # Auto-fix issues
```

### Project Structure

```
space-invaders/
├── src/space_invaders/     # Main source code
│   ├── main.py            # Entry point
│   ├── assets.py          # Asset management
│   ├── constants.py       # All game constants
│   ├── renderer.py        # Display + CRT overlay
│   ├── sound.py           # Audio management
│   ├── scenes/            # Game states
│   │   ├── title.py       # Attract screen
│   │   ├── game.py        # Main gameplay
│   │   ├── cutscene.py    # Inter-round
│   │   └── gameover.py    # Score entry
│   └── entities/          # Game objects
│       ├── grid.py        # 55-invader march
│       ├── player.py      # Cannon
│       ├── bunker.py      # Shields
│       ├── ufo.py         # Mystery ship
│       └── split_alien.py # Deluxe exclusive
├── tests/                 # Test suite (203 tests)
├── assets/                # Downloaded/generated assets
├── README.md              # This file
├── project-recap.md       # Full project documentation
└── product-definition.md  # Requirements checklist
```

## Remote / Headless Systems

If running via SSH, NoMachine NX, or VNC:

```bash
# Ensure DISPLAY is set
export DISPLAY=:0

# Force X11 video driver if needed
export SDL_VIDEODRIVER=x11

# Run the game
space-invaders
```

For pure headless testing (no display):

```bash
export SDL_VIDEODRIVER=dummy
export SDL_AUDIODRIVER=dummy
pytest
```

## Accuracy Notes

All timing values derived from:
- Original arcade hardware analysis
- MAME source code documentation
- Contemporary service manuals

Key verified constants:
- March interval: 800ms (55 invaders) → 50ms (1 invader)
- UFO spawn: ~25 second intervals
- UFO score cycle: 16-value deterministic sequence
- Player speed: 80 px/s | Bullet speed: 300 px/s

See `code-reviews/accuracy-audit-2026-03-07.md` for full verification details.

## License

MIT License — See LICENSE file for details.

## Credits

- **Original game:** © 1980 Taito Corporation
- **This implementation:** Built with Python 3.12 + pygame-ce
- **Author:** Lee Harrington

---

*Project completed March 2026 — 11 sprints, 203 tests, 100% requirements coverage.*
