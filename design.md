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
| Config format | JSON | Universal, editable by hand or external tools |

---

## Asset Strategy

Assets are downloaded at first run into `assets/` (gitignored). If download fails, procedurally generated fallbacks are used so the game always runs.

### Sprites (sourced at runtime)

- **Primary:** The Spriters Resource — original arcade sprite rips (most accurate to Deluxe)
- **Fallback:** OpenGameArt `assets-for-a-space-invader-like-game` (CC-BY 4.0)
- Loaded as PNG, scaled with nearest-neighbor to maintain pixel art fidelity

### Avatar Mode Assets

- **Configuration:** `assets/avatars/config.json` defines character attributes
- **External images:** Optional PNG files in `assets/avatars/`, named `avatar_{row}.png`
- **Procedural fallback:** Memoji-style faces generated via pygame drawing primitives
- **Generator outsourcing:** Placeholder generator is functional; final art can be provided by external tools (e.g., Gemini's Nano Banana2)

### Sounds (sourced at runtime)

- **Primary:** `classicgaming.cc/classics/space-invaders/sounds` — original arcade sound ZIP
- **Fallback:** Freesound CC-0 collection
- Format: WAV preferred; OGG acceptable
- Loaded via `pygame.mixer`

### Asset bootstrap module: `src/space-invaders/assets.py`

- `ensure_assets()` called at startup; downloads missing files, verifies checksums
- All asset paths resolved through a single `AssetManager` class
- No asset fetch = no crash; fallback procedural generation covers every asset type
- **New:** Avatar generation integrated into AssetManager for Avatar Mode

---

## Architecture

```
GameLoop (60 fps fixed timestep)
├── InputHandler       — keyboard polling
├── GameMode (enum)    — ARCADE | AVATAR
├── GameState (enum)   — TITLE | PLAYING | PAUSED | GAME_OVER | CUTSCENE
├── Scene (abstract)
│   ├── TitleScene     — mode selector integrated
│   ├── GameScene      — main gameplay (mode-agnostic logic)
│   │   ├── InvaderGrid    — delegates rendering to InvaderRenderer
│   │   ├── Player         — movement, bullet, lives
│   │   ├── UFO            — spawn timer, score cycle
│   │   ├── BunkerGroup    — pixel-destructible bunkers
│   │   ├── BulletManager  — player + enemy bullets, collision
│   │   └── HUD            — score, lives, high score display
│   ├── CutsceneScene
│   └── GameOverScene  — high score + initials entry
├── Renderer
│   ├── Mode-aware config  — resolution, scaling method, effects
│   ├── Surface (224×256 or 448×512)
│   ├── CRTOverlay         — optional scanline pass
│   └── ScaledBlit         — nearest-neighbor OR smooth
├── InvaderRenderer (strategy pattern)
│   ├── PixelRenderer      — original sprites, color tint
│   └── AvatarRenderer     — Memoji faces, smooth animation
├── AvatarConfig
│   ├── config.json parser
│   ├── procedural generator
│   └── external image loader
└── SoundManager       — sound effects + march tempo control
```

---

## Dual Mode System

The game supports two distinct visual modes. Gameplay **rules** (scoring, lives, win/lose conditions,
timing intervals, sound) are identical. Gameplay **coordinates** scale with the native resolution —
every pixel position in Avatar mode is exactly 2× its arcade equivalent.

### The Coordinate Scaling Principle

Avatar mode doubles the native surface (448×512 vs 224×256). For the game to be geometrically
correct, every position constant must also double:

| What | Arcade | Avatar | Rule |
|------|--------|--------|------|
| Native surface | 224×256 | 448×512 | × coord_scale |
| Cell size | 16×16 | 32×32 | × coord_scale |
| Grid start X/Y | 26, 64 | 52, 128 | × coord_scale |
| Left/Right limits | 4, 220 | 8, 440 | × coord_scale |
| Player Y | 216 | 432 | × coord_scale |
| Player speed (px/s) | 80 | 160 | × coord_scale |
| Bullet speed (px/s) | 300 | 600 | × coord_scale |
| Enemy bullet speed | 96 | 192 | × coord_scale |
| March step X | 2 | 4 | × coord_scale |
| March step Y | 8 | 16 | × coord_scale |
| Bunker Y | 192 | 384 | × coord_scale |
| Bunker W×H | 22×16 | 44×32 | × coord_scale |
| UFO Y | 32 | 64 | × coord_scale |
| UFO speed | 80 | 160 | × coord_scale |
| Timing intervals | same | same | unchanged — timing is time, not pixels |
| Scoring | same | same | unchanged |
| Window scale factor | ×3 | ×2 | chosen so final window size is ~900px wide |

The `ModeConfig` object carries the authoritative values for the active mode. Game entities
receive `ModeConfig` at construction and use it exclusively — they do not read from `constants.py`
for anything position-related.

### Mode Configuration

```python
# src/space_invaders/mode.py
class ModeConfig:
    """Mode-dependent configuration — display AND gameplay coordinates."""

    def __init__(self, mode: GameMode) -> None:
        self.mode = mode
        cs = 2 if mode == GameMode.AVATAR else 1   # coord_scale

        # Display
        self.coord_scale   = cs
        self.screen_w      = 224 * cs
        self.screen_h      = 256 * cs
        self.scale         = 3 if cs == 1 else 2   # window scale factor
        self.cell_w        = 16 * cs
        self.cell_h        = 16 * cs
        self.crt_enabled   = (cs == 1)
        self.smooth_scale  = (cs == 2)

        # Gameplay coordinates (all arcade values × coord_scale)
        self.grid_start_x       = 26  * cs
        self.grid_start_y       = 64  * cs
        self.left_limit         = 4   * cs
        self.right_limit        = 220 * cs
        self.march_step_x       = 2   * cs
        self.march_step_y       = 8   * cs
        self.player_y           = 216 * cs
        self.player_speed       = 80  * cs
        self.bullet_speed       = 300 * cs
        self.enemy_bullet_speed = 96  * cs
        self.bunker_y           = 192 * cs
        self.bunker_w           = 22  * cs
        self.bunker_h           = 16  * cs
        self.ufo_y              = 32  * cs
        self.ufo_speed          = 80  * cs
        self.invader_kill_line  = 216 * cs
        self.split_alien_y      = 100 * cs
        self.split_alien_speed  = 60  * cs
        self.split_alien_zigzag_amp = 12 * cs
        self.split_piece_speed  = 70  * cs
```

### What Is and Is Not Mode-Dependent

**Shared (truly identical):**
- Timing intervals: `MARCH_MAX_MS`, `MARCH_MIN_MS`, `ENEMY_FIRE_*_MS`, `UFO_INTERVAL_MS`
- Scoring: `ROW_SCORES`, `UFO_SCORE_CYCLE`, `RAINBOW_BONUS_*`
- Life count, respawn delay, round clear delay
- Sound events and march audio tempo
- State machines and scene logic

**Mode-dependent (from `ModeConfig`):**
- All pixel positions and sizes
- All speeds expressed in px/s
- Screen dimensions used for boundary checks and UI layout

**Pattern:** every entity that reads a position or speed from `constants.py` today must instead
receive and read from a `ModeConfig` instance.

---

## Avatar System Design

### Configuration Layer

```python
# src/space_invaders/avatar_config.py
@dataclass
class CharacterDef:
    name: str
    row: int  # 0-4, maps to grid row
    skin: tuple[int, int, int]
    hair: tuple[int, int, int]
    hair_style: str  # "slick", "messy", "bald", etc.
    shirt: tuple[int, int, int]
    expression_base: str  # "serious", "smirk", "worried"

class AvatarConfig:
    """Loads and validates avatar configuration."""
    
    CONFIG_PATH = Path("assets/avatars/config.json")
    
    def load(self) -> list[CharacterDef]:
        if self.CONFIG_PATH.exists():
            return self._load_from_json()
        return self._default_characters()
    
    def get_character(self, row: int) -> CharacterDef:
        """Get character definition for a grid row."""
```

### Procedural Avatar Generator

```python
# src/space_invaders/avatar_generator.py
class AvatarGenerator:
    """Generates Memoji-style avatar surfaces procedurally."""
    
    def generate(self, char: CharacterDef, size: int = 32) -> pygame.Surface:
        """Create avatar surface from character definition."""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Layer 1: Face shape (ellipse)
        self._draw_face(surf, char.skin, size)
        
        # Layer 2: Hair (style-dependent)
        self._draw_hair(surf, char.hair, char.hair_style, size)
        
        # Layer 3: Eyes
        self._draw_eyes(surf, size)
        
        # Layer 4: Expression (mouth)
        self._draw_expression(surf, char.expression_base, size)
        
        # Layer 5: Shirt (bottom portion)
        self._draw_shirt(surf, char.shirt, size)
        
        return surf
```

### Avatar Renderer (Strategy)

```python
# src/space_invaders/entities/invader_renderer.py
class InvaderRenderer(ABC):
    @abstractmethod
    def render(self, surface: pygame.Surface, grid: InvaderGrid) -> None: ...

class PixelRenderer(InvaderRenderer):
    """Original arcade sprite rendering with color tinting."""
    
class AvatarRenderer(InvaderRenderer):
    """Memoji avatar rendering with bounce animation."""
    
    def __init__(self, config: AvatarConfig):
        self.avatars = self._load_avatars(config)
        self.bounce_phase = 0.0
    
    def render(self, surface, grid):
        for row, col in grid.living_invaders():
            avatar = self.avatars[row]
            # Apply subtle bounce based on phase
            y_offset = int(3 * math.sin(self.bounce_phase + col * 0.5))
            # Scale avatar to cell size smoothly
            scaled = pygame.transform.smoothscale(avatar, (grid.cell_w, grid.cell_h))
            surface.blit(scaled, (cell_x, cell_y + y_offset))
```

---

## Key Technical Decisions

### Pixel-perfect rendering (Arcade mode)

Game renders into a `pygame.Surface` of exactly 224×256. Each frame, this surface is scaled 3× (672×768) using `pygame.transform.scale` with no smoothing (`pygame.transform.scale`, not `smoothscale`), then blitted to the window.

### Smooth rendering (Avatar mode)

Game renders into 448×512 (all coordinates are 2× arcade values). Scaled 2× to 896×1024 using
`pygame.transform.smoothscale` for interpolated, photo-like quality. No CRT overlay applied.
Avatar sprites are generated at 128×128 and smooth-scaled to 32×32 in the native surface, giving
4× supersampling — equivalent visual quality to a 128×128-pixel displayed face at native resolution.

### CRT scanline effect

After scaling, a pre-computed numpy alpha mask (every other horizontal row set to 40% opacity black) is applied as a surface overlay. Computed once at startup; zero per-frame allocation cost. **Only in Arcade mode.**

### Bunker pixel destruction

Each bunker stored as a `pygame.surfarray` numpy array. Bullet hits zero out pixels in a small radius around impact point. Efficient and authentic to original behavior. Damage persists across rounds.

**Avatar mode enhancement:** Higher resolution bunkers (44×32) with same destruction mechanics but smoother appearance.

### March timing

Each march "tick" moves the entire grid one step. Tick interval starts at ~800 ms (55 invaders) and decreases linearly to ~50 ms (1 invader remaining). Interval recalculated after each kill.

**Same in both modes** — gameplay logic is mode-agnostic.

### UFO score cycle

Deterministic, matching original Deluxe behavior:

```python
CYCLE = [50, 50, 100, 150, 100, 100, 50, 300, 100, 100, 100, 50, 150, 100, 100]
score = CYCLE[shot_count % len(CYCLE)]
```

### Sound march tempo

4 sound channels playing the 4 march notes in sequence. Interval between notes matches march tick interval, so audio and visuals stay locked in sync.

**Same in both modes.**

---

## File Structure

```
src/space-invaders/
├── main.py              — entry point, window init, game loop
├── mode.py              — GameMode enum, ModeConfig
├── assets.py            — AssetManager, ensure_assets()
├── avatar_config.py     — CharacterDef, AvatarConfig loader
├── avatar_generator.py  — Procedural Memoji generator
├── constants.py         — SCREEN_W=224, SCREEN_H=256, SCALE=3, FPS=60, etc.
├── renderer.py          — Renderer (mode-aware), optional CRTOverlay
├── sound.py             — SoundManager, march tempo control
├── hud.py               — HUD rendering (score, lives, high score)
├── scenes/
│   ├── __init__.py
│   ├── base.py          — Scene abstract class
│   ├── title.py         — TitleScene with mode selector
│   ├── game.py          — GameScene (main gameplay)
│   ├── cutscene.py      — CutsceneScene (inter-round)
│   └── gameover.py      — GameOverScene + initials entry
└── entities/
    ├── __init__.py
    ├── grid.py          — InvaderGrid (logic only, delegates rendering)
    ├── invader_renderer.py — Strategy: PixelRenderer, AvatarRenderer
    ├── player.py        — Player (movement, bullet, lives)
    ├── ufo.py           — UFO (spawn timer, score cycle)
    ├── bunker.py        — Bunker (pixel-destructible surfarray)
    └── bullet.py        — Bullet (player + enemy variants)

assets/                  — gitignored, populated by ensure_assets()
├── avatars/
│   ├── config.json      — Optional: character definitions
│   ├── avatar_0.png     — Optional: external image overrides
│   ├── avatar_1.png
│   ├── avatar_2.png
│   ├── avatar_3.png
│   └── avatar_4.png
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

### Arcade Mode

| Constant | Value | Source |
|----------|-------|--------|
| `SCREEN_W` | 224 | Original arcade resolution |
| `SCREEN_H` | 256 | Original arcade resolution |
| `SCALE` | 3 | 224×3=672, 256×3=768 |
| `FPS` | 60 | Fixed timestep |
| `GRID_COLS` | 11 | Original grid |
| `GRID_ROWS` | 5 | Original grid |
| `CELL_W` | 16 | Pixels between column centers |
| `CELL_H` | 16 | Pixels between row centers |
| `BUNKER_COUNT` | 4 | Original |
| `BUNKER_W` | 22 | px at native res |
| `BUNKER_H` | 16 | px at native res |
| `LIVES` | 3 | Per game |
| `HIGH_SCORE_MAX` | 99990 | Deluxe cap |
| `UFO_INTERVAL_MS` | 25000 | ~25 sec |
| `MARCH_MAX_MS` | 800 | 55 invaders |
| `MARCH_MIN_MS` | 50 | 1 invader |
| `SCANLINE_ALPHA` | 102 | 40% of 255 |

### Avatar Mode (all from `ModeConfig`, coord_scale = 2)

| Config property | Value | Rule |
|----------------|-------|------|
| `screen_w` | 448 | 224 × 2 |
| `screen_h` | 512 | 256 × 2 |
| `scale` | 2 | window = 896×1024 |
| `cell_w` | 32 | 16 × 2 |
| `cell_h` | 32 | 16 × 2 |
| `grid_start_x` | 52 | 26 × 2 |
| `grid_start_y` | 128 | 64 × 2 |
| `left_limit` | 8 | 4 × 2 |
| `right_limit` | 440 | 220 × 2 |
| `march_step_x` | 4 | 2 × 2 |
| `march_step_y` | 16 | 8 × 2 |
| `player_y` | 432 | 216 × 2 |
| `player_speed` | 160 | 80 × 2 (same feel) |
| `bullet_speed` | 600 | 300 × 2 (same feel) |
| `enemy_bullet_speed` | 192 | 96 × 2 |
| `bunker_y` | 384 | 192 × 2 |
| `bunker_w` | 44 | 22 × 2 |
| `bunker_h` | 32 | 16 × 2 |
| `ufo_y` | 64 | 32 × 2 |
| `ufo_speed` | 160 | 80 × 2 |
| `invader_kill_line` | 432 | 216 × 2 |
| All timing constants | unchanged | time, not pixels |
| `crt_enabled` | False | clean modern look |

---

## External Tool Integration

### Nano Banana2 / External Avatar Generator

The procedural generator provides functional placeholders. For production-quality avatars:

1. **Export config:** Run game once to generate `config.json` template
2. **External generation:** Use Nano Banana2 or other tool to create 5 PNG files
3. **Drop-in replacement:** Place PNGs in `assets/avatars/`, no code changes needed
4. **Fallback safety:** If PNG missing or corrupt, procedural generator provides default

### Character Design Guidelines for External Tools

- **Canvas size:** 128×128 recommended (game scales to 32×32 native → 64×64 displayed at 2× window)
- **Format:** PNG with alpha transparency
- **Style:** Memoji-inspired, recognizable human faces, cartoony proportions
- **Naming:** `avatar_{row}.png` where row 0 = top, row 4 = bottom
- **Expression:** Row 0 serious/confident, Row 4 worried/panicked (reflects descent)
- **Quality note:** 128→32 supersampling gives 4× quality improvement over native-resolution art

---

*Generated for Avatar Mode feature — Dual-mode architecture with configurable characters*
