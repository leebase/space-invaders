# Project Recap — Space Invaders Deluxe

> **What we built, why it matters, and how to use it.**

---

## Executive Summary

A complete, pixel-perfect recreation of the 1980 Taito Space Invaders Deluxe arcade game. Eleven sprints, 203 tests, 100% product requirement coverage. Built with Python 3.12+ and pygame-ce.

**Status:** ✅ **COMPLETE AND RELEASED**

---

## What Was Built

### Core Game (Sprints 1-7)

| Sprint | Feature | Key Technical Achievement |
|--------|---------|---------------------------|
| 1-3 | Project skeleton + Invader grid | Native 224×256 rendering, nearest-neighbor 3× scaling |
| 4 | Player + shooting + collision | Float-position accumulators, pixel-perfect collision |
| 5 | Lives + round advance + game over | State machine (PLAYING/PLAYER_DEAD/ROUND_CLEAR) |
| 6 | Enemy fire + bunkers | Pixel-destructible surfarray shields, numpy erosion |
| 7 | UFO | Deterministic score cycle, spawn timer, 80px/s traversal |

### Polish Layer (Sprint 8)

- 4-note march sequencer locked to visual march tempo
- 6 sound categories: march, shoot, kill, death, UFO drone, UFO hit
- M-key mute toggle

### Deluxe Exclusives (Sprint 9)

| Feature | Implementation |
|---------|---------------|
| Splitting aliens | `SplitAlien` zigzag path, spawns 2 `SplitPiece` entities (100/50 pts) |
| Rainbow bonus | 500 pts last invader bottom rows, 1000 pts bottom-left cell |
| Cutscenes | 3-second inter-round animation with marching parade |
| Color descent | 5-band system (white→cyan→green→yellow→orange) via `DESCENT_COLOR_BANDS` |

### Game Shell (Sprint 10)

- **TitleScene:** Animated invader parade, blinking prompt, hi-score display
- **GameOverScene:** 3-initials entry (A-Z, 0-9), cursor navigation, confirm
- **Pause:** P/Esc toggle, freezes logic, stops UFO drone
- **CRT overlay:** Pre-computed scanlines, 40% alpha, zero per-frame allocation

### Accuracy Verification (Sprint 11)

- Code-based audit against reference documentation
- **Critical fix:** UFO score cycle corrected (now starts with 100, 16 values)
- 3 acceptable deviations documented (asset fallbacks, scanline intensity)

---

## Technical Architecture

```
space_invaders/
├── main.py              # Entry point, scene switching
├── assets.py            # AssetManager with procedural fallbacks
├── constants.py         # All arcade-accurate timing values
├── renderer.py          # Native 224×256 → 672×768 + CRT overlay
├── sound.py             # March sequencer, effects, UFO drone
├── hud.py               # Score/lives display
├── scenes/
│   ├── base.py          # Scene abstract base
│   ├── title.py         # Attract screen
│   ├── game.py          # Main gameplay (900+ lines)
│   ├── cutscene.py      # Inter-round animation
│   └── gameover.py      # Final score + initials entry
└── entities/
    ├── grid.py          # 55-invader march logic
    ├── player.py        # Cannon + bullet management
    ├── bullet.py        # Projectile entity
    ├── bunker.py        # Pixel-destructible shields
    ├── ufo.py           # Mystery ship
    └── split_alien.py   # Deluxe exclusive entity
```

### Key Design Decisions

1. **Procedural fallbacks** — Game always runs, even without asset files
2. **Scene-based architecture** — Clean state transitions via `next_scene`
3. **Float accumulators** — Sub-pixel precision for movement (Player `_x`, Bullet `_y`)
4. **Pre-computed overlays** — CRT scanlines built once in `Renderer.__init__`
5. **Tint caching** — Descent color surfaces cached to avoid per-frame creation

---

## Quality Metrics

| Metric | Value |
|--------|-------|
| Tests | 203 passing |
| Test coverage | Core mechanics + edge cases |
| Linter | `ruff check` clean |
| Type hints | Full coverage on public APIs |
| Documentation | README, AGENTS.md, design.md, skill files |
| Code reviews | 2 formal reviews, 11 findings addressed |

---

## How to Run

### Prerequisites

- Python 3.12+
- Linux (tested), macOS, or Windows

### Installation

```bash
cd /home/lee/projects/space-invaders
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Launch

```bash
space-invaders
```

Or:

```bash
python -m space_invaders
```

### For Remote/Headless Systems

If running via NoMachine NX, VNC, or SSH with X forwarding:

```bash
# Ensure DISPLAY is set
export DISPLAY=:0

# Force X11 driver if needed
export SDL_VIDEODRIVER=x1
space-invaders
```

---

## How to Play

### Controls

| Key | Action |
|-----|--------|
| ← / A | Move left |
| → / D | Move right |
| Space | Fire (one bullet at a time) |
| P | Pause / Resume |
| Esc | Pause (in game) / Quit (at title) |
| M | Mute / Unmute |

### Scoring

| Target | Points |
|--------|--------|
| Squid (top row) | 30 |
| Crab (rows 2-3) | 20 |
| Octopus (rows 4-5) | 10 |
| UFO | 50-300 (cycles deterministically) |
| Split Alien | 100 |
| Split Piece | 50 |
| Rainbow Bonus (last alien, bottom rows) | 500 |
| Rainbow Bonus (last alien, bottom-left) | 1000 |

### Strategy Tips

- **UFO exploit:** The 9th shot in the cycle awards 300 points. Count your shots!
- **Rainbow bonus:** Leave one invader from bottom rows for maximum points
- **Bunker conservation:** Let invaders erode the top; shoot through the bottom
- **Split alien:** Hit it quickly — the pieces are worth 50 pts each

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=space_invaders

# Run specific test file
pytest tests/test_deluxe.py -v
```

---

## Known Issues / Acceptable Deviations

| ID | Description | Reason |
|----|-------------|--------|
| D001 | Procedural sprites when disk assets unavailable | Ensures game always runs |
| D002 | Procedural square-wave beeps when WAVs unavailable | Ensures game always runs |
| D003 | Fixed 40% scanline opacity | Aesthetic choice — authentic enough |

---

## File Reference

| File | Purpose |
|------|---------|
| `README.md` | Quick start guide |
| `AGENTS.md` | AI agent conventions and guardrails |
| `context.md` | Session working memory (updated each session) |
| `WHERE_AM_I.md` | Product-level orientation |
| `result-review.md` | Running log of completed work |
| `sprint-plan.md` | Tactical execution tracker |
| `product-definition.md` | Acceptance checklist (39/39 ✅) |
| `design.md` | Technical blueprint |
| `code-reviews/` | Formal review findings |
| `skills/` | Reusable capability modules |

---

## Credits

- **Original game:** Taito Corporation (1980)
- **This implementation:** Lee Harrington
- **Built with:** Python 3.12, pygame-ce, numpy

---

*Project completed 2026-03-07 — 11 sprints, 203 tests, 100% requirements coverage.*
