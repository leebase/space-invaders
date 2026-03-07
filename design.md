# Design — Space Invaders Deluxe

> **How we build it.** Technical blueprint. Every component here traces back to a requirement in `product-definition.md`.

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Language | Python 3.10+ | Project baseline |
| Game engine | `pygame-ce` ≥ 2.4.0 | Drop-in pygame replacement; better perf, OpenGL access |
| Pixel ops | `numpy` ≥ 1.24.0 | Bunker erosion, scanline overlay as pixel arrays |
| Asset fetching | `requests` ≥ 2.28.0 + `Pillow` ≥ 10.0.0 | Download and validate assets at first run |
| Build/package | existing `pyproject.toml` | Add dependencies there |

---

## Asset Strategy

Assets are downloaded at first run into `assets/` (gitignored). If download fails, procedurally generated fallbacks are used so the game always runs.

### Sprites (sourced at runtime)

- **Primary:** The Spriters Resource — original arcade sprite rips (most accurate to Deluxe)
- **Fallback:** OpenGameArt `assets-for-a-space-invader-like-game` (CC-BY 4.0)
- Loaded as PNG, scaled with nearest-neighbor to maintain pixel art fidelity

### Sounds (sourced at runtime)

- **Primary:** `classicgaming.cc/classics/space-invaders/sounds` — original arcade sound ZIP
- **Fallback:** Freesound CC-0 collection
- Format: WAV preferred; OGG acceptable
- Loaded via `pygame.mixer`

### Asset bootstrap module: `src/space-invaders/assets.py`

- `ensure_assets()` called at startup; downloads missing files, verifies checksums
- All asset paths resolved through a single `AssetManager` class
- No asset fetch = no crash; fallback procedural generation covers every asset type

---

## Architecture

```
GameLoop (60 fps fixed timestep)
├── InputHandler       — keyboard polling
├── GameState (enum)   — TITLE | PLAYING | PAUSED | GAME_OVER | CUTSCENE
├── Scene (abstract)
│   ├── TitleScene
│   ├── GameScene      — main gameplay
│   │   ├── InvaderGrid    — 5×11 grid, march logic, fire logic
│   │   ├── Player         — movement, bullet, lives
│   │   ├── UFO            — spawn timer, score cycle
│   │   ├── BunkerGroup    — 4 pixel-destructible bunkers
│   │   ├── BulletManager  — player + enemy bullets, collision
│   │   └── HUD            — score, lives, high score display
│   ├── CutsceneScene
│   └── GameOverScene  — high score + initials entry
├── Renderer
│   ├── Surface (224×256) — game renders here
│   ├── CRTOverlay         — scanline numpy pass
│   └── ScaledBlit (3×)   — to actual window
└── SoundManager       — sound effects + march tempo control
```

---

## Key Technical Decisions

### Pixel-perfect rendering

Game renders into a `pygame.Surface` of exactly 224×256. Each frame, this surface is scaled 3× (672×768) using `pygame.transform.scale` with no smoothing (`pygame.transform.scale`, not `smoothscale`), then blitted to the window.

### CRT scanline effect

After scaling, a pre-computed numpy alpha mask (every other horizontal row set to 40% opacity black) is applied as a surface overlay. Computed once at startup; zero per-frame allocation cost.

### Bunker pixel destruction

Each bunker stored as a `pygame.surfarray` numpy array. Bullet hits zero out pixels in a small radius around impact point. Efficient and authentic to original behavior. Damage persists across rounds.

### March timing

Each march "tick" moves the entire grid one step. Tick interval starts at ~800 ms (55 invaders) and decreases linearly to ~50 ms (1 invader remaining). Interval recalculated after each kill.

```python
def march_interval_ms(remaining: int) -> int:
    # Linear interpolation: 55 invaders -> 800ms, 1 invader -> 50ms
    return int(50 + (remaining - 1) * (800 - 50) / (55 - 1))
```

### UFO score cycle

Deterministic, matching original Deluxe behavior:

```python
CYCLE = [50, 50, 100, 150, 100, 100, 50, 300, 100, 100, 100, 50, 150, 100, 100]
score = CYCLE[shot_count % len(CYCLE)]
```

### Sound march tempo

4 sound channels playing the 4 march notes in sequence. Interval between notes matches march tick interval, so audio and visuals stay locked in sync.

### Splitting aliens (Deluxe feature)

When a qualifying alien is shot, it is replaced by two smaller sub-entities at offset positions. Sub-entities are worth half the original point value and use distinct sprites. Logic lives in `InvaderGrid.handle_hit()`.

---

## File Structure

```
src/space-invaders/
├── main.py          — entry point, window init, game loop
├── assets.py        — AssetManager, ensure_assets()
├── constants.py     — SCREEN_W=224, SCREEN_H=256, SCALE=3, FPS=60, etc.
├── renderer.py      — Renderer, CRTOverlay
├── sound.py         — SoundManager, march tempo control
├── hud.py           — HUD rendering (score, lives, high score)
├── scenes/
│   ├── __init__.py
│   ├── base.py      — Scene abstract class
│   ├── title.py     — TitleScene / attract loop
│   ├── game.py      — GameScene (main gameplay)
│   ├── cutscene.py  — CutsceneScene (inter-round)
│   └── gameover.py  — GameOverScene + initials entry
└── entities/
    ├── __init__.py
    ├── grid.py      — InvaderGrid (march, fire, split logic)
    ├── player.py    — Player (movement, bullet, lives)
    ├── ufo.py       — UFO (spawn timer, score cycle)
    ├── bunker.py    — Bunker (pixel-destructible surfarray)
    └── bullet.py    — Bullet (player + enemy variants)

assets/              — gitignored, populated by ensure_assets()
├── sprites/
└── sounds/
```

---

## Dependencies to add to pyproject.toml

```toml
[project]
dependencies = [
    "pygame-ce>=2.4.0",
    "numpy>=1.24.0",
    "requests>=2.28.0",
    "Pillow>=10.0.0",
]
```

---

## Constants (canonical values)

| Constant | Value | Source |
|----------|-------|--------|
| `SCREEN_W` | 224 | Original arcade resolution |
| `SCREEN_H` | 256 | Original arcade resolution |
| `SCALE` | 3 | 224×3=672, 256×3=768 |
| `FPS` | 60 | Fixed timestep |
| `GRID_COLS` | 11 | Original grid |
| `GRID_ROWS` | 5 | Original grid |
| `BUNKER_COUNT` | 4 | Original |
| `BUNKER_W` | 22 | px at native res |
| `BUNKER_H` | 16 | px at native res |
| `LIVES` | 3 | Per game |
| `HIGH_SCORE_MAX` | 99990 | Deluxe cap |
| `UFO_INTERVAL_MS` | 25000 | ~25 sec |
| `MARCH_MAX_MS` | 800 | 55 invaders |
| `MARCH_MIN_MS` | 50 | 1 invader |
| `SCANLINE_ALPHA` | 102 | 40% of 255 |
