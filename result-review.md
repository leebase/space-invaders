# space-invaders Result Review

> **Running log of completed work.** Newest entries at the top.

---

## 2026-03-07 — Sprint 11: Accuracy Pass + Release Ready

**What was done:** Comprehensive accuracy audit against reference documentation. One critical fix applied.

### Critical Fix: UFO Score Cycle

**Before:** `[50, 50, 100, 150, 100, 100, 50, 300, 100, 100, 100, 50, 150, 100, 100]` (15 values, starts with 50)
**After:** `[100, 50, 50, 100, 150, 100, 100, 50, 300, 100, 100, 100, 50, 150, 100, 50]` (16 values, starts with 100)

**Source:** Space Invaders Wiki, Digital Press Easter Eggs — verified against arcade hardware

### Audit Results

| Category | Status |
|----------|--------|
| Timing constants | ✅ All verified against design.md |
| Scoring rules | ✅ All verified |
| Deluxe features | ✅ 4/4 implemented correctly |
| Sound system | ✅ 7/7 effects verified |
| UNVERIFIED comments | ✅ None remaining |
| product-definition.md | ✅ 39/39 items checked |

### Documented Deviations

| ID | Description | Rationale |
|----|-------------|-----------|
| D001 | Procedural sprites as fallback | Ensures game runs without assets |
| D002 | Procedural beeps as fallback | Ensures game runs without assets |
| D003 | Fixed 40% scanline opacity | Aesthetic choice — authentic enough |

### Files Modified

- `src/space_invaders/constants.py` — UFO_SCORE_CYCLE corrected
- `code-reviews/accuracy-audit-2026-03-07.md` — Created
- `WHERE_AM_I.md` — Updated to reflect project complete
- `README.md` — Updated with full project description

**Result:** 203/203 tests pass, `ruff check` clean, **PROJECT COMPLETE**

---

## 2026-03-07 — Sprint 10: Game States + Polish

**What was built:** Complete game shell — title screen, initials entry, CRT scanline overlay, pause.

### Created / Modified

| File | Change |
|------|--------|
| `src/space_invaders/scenes/title.py` | Full TitleScene: animated invader parade (3 rows), blinking prompt, hi-score display |
| `src/space_invaders/scenes/gameover.py` | Complete rewrite: initials entry with 3 positions, cursor blink, UP/DOWN/LEFT/RIGHT/ENTER controls |
| `src/space_invaders/renderer.py` | CRT scanline overlay: pre-computed 672×768 surface with 40% alpha every 2nd row |
| `src/space_invaders/scenes/game.py` | Pause toggle (P/Esc), PAUSED state with overlay, UFO drone stop on pause |
| `src/space_invaders/main.py` | Start with TitleScene, Esc handling for pause vs quit |
| `tests/test_sprint10.py` | 21 new tests for TitleScene, GameOverScene, pause, CRT overlay, hi-score cap |

### Key Mechanics

- **TitleScene**: 6-invader parade per row (squid/crab/octopus), 20px/s march, 0.5s frame advance, 1Hz prompt blink
- **Initials entry**: A-Z + 0-9 character set, wrap-around navigation, underline cursor at 2Hz blink
- **CRT overlay**: Pre-computed in Renderer.__init__(), zero per-frame allocation
- **Pause**: Freezes all game logic, stops UFO drone, semi-transparent overlay with "PAUSED" text
- **High score**: Session persistence via `hi_score` passed to new GameScene instances

**Result:** 203/203 tests pass, `ruff check` clean.

---

## 2026-03-07 — Sprint 9 Code Review Remediation

**What was fixed:** 3 findings from `code-reviews/review-2026-03-07-sprint9.md` resolved.

### Findings Fixed

| Finding | Severity | Fix |
|---------|----------|-----|
| R001 | Med | Cutscene timer guard — `if self.next_scene is None:` prevents overwriting user keypress |
| R002 | Med | Bunker surface lock safety — try/finally in `apply_damage()` and `is_destroyed()` |
| R003 | Low | Removed duplicate `ROUND_CLEAR_DELAY` definition |

### Tests Added

- `test_cutscene_keypress_wins_over_timer` — R001 regression
- `test_bunker_apply_damage_releases_lock_on_exception` — R002 regression  
- `test_bunker_is_destroyed_releases_lock` — R002 regression

**Result:** 182/182 tests pass, `ruff check` clean.

---

## 2026-03-07 — Sprint 9: Deluxe Features

**What was built:** All four Space Invaders Deluxe exclusive features.

### Created / Modified

| File | Change |
|------|--------|
| `src/space_invaders/entities/split_alien.py` | `SplitAlien` with zigzag path, `SplitPiece` fragments; 100 pts alien, 50 pts pieces |
| `src/space_invaders/scenes/cutscene.py` | Inter-round animated sequence with marching aliens, "ROUND N" header, skip on keypress |
| `src/space_invaders/entities/grid.py` | `_descent_color()` bands, `_get_tinted()` cache for color-shifting sprites |
| `src/space_invaders/scenes/game.py` | Split alien + pieces wired; rainbow bonus conditions; `_to_cutscene()` transition |
| `src/space_invaders/constants.py` | `DESCENT_COLOR_BANDS`, `SPLIT_ALIEN_*`, `RAINBOW_BONUS_*`, `CUTSCENE_DURATION` |
| `tests/test_deluxe.py` | 26 new tests |

### Key Mechanics

- **Split alien**: Spawns every 20s, traverses right→left with sine-wave zigzag. Hit spawns 2 `SplitPiece` entities moving diagonally off-screen.
- **Rainbow bonus**: Killing the last invader from bottom 2 rows awards 500 pts; bottom-left cell specifically awards 1000 pts.
- **Descent color**: 5-band color system — white (start) → cyan → green → yellow → orange (deep descent).
- **Cutscene**: 3-second inter-round animation; any key skips; holds reference to already-advanced `GameScene`.

**Result:** 179/179 tests pass, `ruff check` clean.
>
> Each entry documents what was built, why it matters, and how to verify it works.

---

## 2026-03-07 — Sprint 8: Sound

**What was built:** `SoundManager` with a while-loop march sequencer locked to visual march tempo. All six sound categories wired into `GameScene`: march notes, player shoot, invader killed, player death, UFO hit, UFO drone (looping on dedicated channel, starts/stops on UFO state transitions). M-key mute toggle stops all channels immediately.

### Created / Modified

| File | Change |
|------|--------|
| `src/space_invaders/sound.py` | Full implementation: march sequencer, `play()`, drone channel, `toggle_mute()`, `reset_march()` |
| `src/space_invaders/scenes/game.py` | `SoundManager` wired in; all event hooks; UFO drone transition tracking; M-key mute |
| `src/space_invaders/main.py` | Removed dead `renderer.clear()` call (R006 follow-up) |
| `tests/test_sound.py` | 19 new tests |

### Key Decisions

- **While-loop sequencer**: march timer uses `while march_timer_ms >= interval` (same pattern as visual march) so it catches multiple steps in one frame at fast tempos
- **UFO drone tracking**: `_ufo_was_active` flag in GameScene detects IDLE→ACTIVE and ACTIVE→IDLE transitions each frame, avoids polling UFO internals from sound layer
- **`reset_march()` on round start**: ensures audio re-syncs with a fresh grid

**Result:** 153/153 tests pass, `ruff check` clean.

---

## 2026-03-07 — Sprint 7 Code Review Remediation

**What was fixed:** 6 findings from `code-reviews/review-2026-03-07-sprint7.md` resolved.

### Correctness Bugs Fixed

| Finding | Fix |
|---------|-----|
| R001 (Med) — UFO not reset in `_next_round()` | `UFO.reset()` added; called from `_next_round()`; preserves session `_shot_count` |
| R002 (Low) — enemy bullets frozen during ROUND_CLEAR | `enemy_bullets.clear()` and `player.bullet = None` called when entering ROUND_CLEAR |

### Code Quality

| Finding | Fix |
|---------|-----|
| R003 — redundant `_State.PLAYING` guard in `_check_enemy_bullet_collisions` | Guard removed (method only called from PLAYING block) |
| R004 — score update duplicated 3× | `_award(pts)` helper extracted |
| R005 — unreachable guard in `_try_fire()` | `if row is None: return None` replaced with `assert` |
| R006 — unused `Renderer.clear()` | Removed |

**Result:** 134/134 tests pass, `ruff check` clean.

---

## 2026-03-07 — Sprint 7: UFO

**What was built:** Mystery ship spawns every 25 seconds and traverses left→right at 80px/s. Shooting it awards a deterministic score from `UFO_SCORE_CYCLE` based on total shot count. Score text displays at the hit position for 1 second, then UFO returns to IDLE.

### Created / Modified

| File | Change |
|------|--------|
| `src/space_invaders/constants.py` | `UFO_SPEED = 80`, `UFO_HIT_DISPLAY_S = 1.0` |
| `src/space_invaders/entities/ufo.py` | Full implementation: `_State` enum, float-x accumulator, spawn timer, `hit()`, draw |
| `src/space_invaders/scenes/game.py` | `ufo.update(dt)` wired in; UFO collision in `_check_player_bullet_collisions()` |
| `tests/test_ufo.py` | 19 new tests |

**Result:** 131/131 tests pass, `ruff check` clean.

---

## 2026-03-07 — Sprint 6: Enemy Fire + Pixel-Destructible Bunkers

**What was built:** Invaders fire downward at random intervals (rate scales with remaining count). Up to 3 simultaneous enemy bullets. Bunkers erode pixel-by-pixel via numpy surfarray when hit from either direction. Enemy bullets that reach the player trigger `kill_player()` and clear the field.

### Created / Modified

| File | Change |
|------|--------|
| `src/space_invaders/constants.py` | `ENEMY_BULLET_SPEED`, `ENEMY_FIRE_MAX/MIN_MS`, `ENEMY_BULLET_MAX` |
| `src/space_invaders/entities/grid.py` | `_fire_interval_ms()`, fire timer, `pending_bullets`, `_try_fire()` |
| `src/space_invaders/entities/bunker.py` | `apply_damage()` via surfarray, `is_destroyed()` |
| `src/space_invaders/scenes/game.py` | `enemy_bullets` list, all collision paths, filter-after-collision fix |
| `tests/test_enemy_fire.py` | 19 new tests |

### Key Decisions

- **Reuse `Bullet`**: enemy bullets use `Bullet(dy=+ENEMY_BULLET_SPEED)` — no separate class needed
- **`pending_bullets` drain**: grid accumulates, GameScene adopts (cap enforced at ENEMY_BULLET_MAX)
- **Filter-after-collision**: bullet filter now runs after all collision checks in a frame, not before
- **Player bullet checks bunkers before invaders** (correct upward path order)

**Result:** 112/112 tests pass, `ruff check` clean.

---

## 2026-03-07 — Sprint 5: Game Loop (Lives, Win/Lose, Round Advance)

**What was built:** Full game loop. Player has 3 lives with 2-second respawn. All invaders cleared = brief pause then next round. Invaders reaching `PLAYER_Y` or lives exhausted = game over. `GameOverScene` shows score and restarts on any key.

### Created / Modified

| File | Change |
|------|--------|
| `src/space_invaders/constants.py` | `RESPAWN_DELAY`, `ROUND_CLEAR_DELAY`, `INVADER_KILL_LINE` added |
| `src/space_invaders/scenes/base.py` | `next_scene = None` class attribute added |
| `src/space_invaders/scenes/game.py` | `_State` enum, state machine, `kill_player()`, round advance, game-over trigger |
| `src/space_invaders/scenes/gameover.py` | Score + best display, any-key restart |
| `src/space_invaders/main.py` | Scene switching via `scene.next_scene` |
| `tests/conftest.py` | `display.set_mode(1,1)` added for `convert_alpha()` compat |
| `tests/test_game_loop.py` | 18 new tests |

### State Machine

```
PLAYING → (grid cleared)     → ROUND_CLEAR → (1.5s) → PLAYING (next round)
PLAYING → (invaders at Y)    → [GameOverScene]
PLAYING → kill_player()      → PLAYER_DEAD → (2s, lives>0) → PLAYING
                                           → (2s, lives≤0) → [GameOverScene]
```

**Result:** 92/92 tests pass, `ruff check` clean.

### How to Verify

```bash
.venv/bin/pytest -q          # 92 passed
.venv/bin/space-invaders     # play, die, watch game over; press key to restart
```

---

## 2026-03-07 — Sprint 4: Player + Shooting + Invader Collision

**What was built:** Player cannon moves, fires one bullet at a time, invaders die on hit with correct score values. March tempo auto-adjusts as invaders are killed.

### Created / Modified

| File | Change |
|------|--------|
| `src/space_invaders/constants.py` | `BULLET_SPEED = 300` added |
| `src/space_invaders/entities/player.py` | Full implementation: movement (A/D/arrows), `fire()`, bullet lifecycle, float-position accumulator |
| `src/space_invaders/entities/bullet.py` | Float-position accumulator, `constants.SCREEN_H` boundary, imports cleaned |
| `src/space_invaders/scenes/game.py` | Player update wired, SPACE fires bullet, bullet-vs-grid collision with scoring |
| `tests/test_player.py` | 15 new tests: position, movement, clamping, fire, one-bullet constraint |
| `tests/test_bullet.py` | 6 new tests: travel, despawn, float accumulation |

### Mechanics

- **One-bullet constraint**: `player.fire()` returns `None` if `player.bullet` is not `None`
- **Float positions**: both Player (`_x`) and Bullet (`_y`) accumulate float sub-pixel movement; `rect` is synced as `int()` each frame
- **Collision**: `GameScene._check_bullet_collision()` calls `grid.invader_at(bx, by)` then `grid.kill(row, col)` for score
- **Score cap**: `min(score + pts, HIGH_SCORE_MAX)` enforced in GameScene

**Result:** 74/74 tests pass, `ruff check` clean.

### How to Verify

```bash
.venv/bin/pytest -q          # 74 passed
.venv/bin/ruff check src/ tests/
.venv/bin/space-invaders     # move with arrows/AD, fire with space
```

---

## 2026-03-07 — Sprint 4.5: Code Review Remediation

**What was fixed:** All 10 findings from `code-reviews/review-2026-03-07.md` resolved.

### Correctness Bugs Fixed

| Finding | Fix |
|---------|-----|
| R003 — single step per frame | `if` → `while` in `InvaderGrid.update()`; interval recomputed each iteration |
| R002 — boundary ignored centering offset | `left/right_edge` now accounts for `(CELL_W ± sprite_w) // 2` |
| R007 — boundary used topmost row width | `_topmost_alive_row_in_col` replaced by `_max_sprite_w_in_col` |
| R004 — HUD score 4 digits max | `{v:04d}` → `{v:05d}` capped at `HIGH_SCORE_MAX` |
| R006 — no spritesheet validation | Dimension check added; mismatch logs warning and falls back |

### Tests Added

- `tests/conftest.py` — headless pygame session fixture
- `tests/test_grid.py` — 22 tests: `march_interval_ms`, animation, multi-step, boundary reversal, kill/score, `invader_at`
- `tests/test_assets.py` — 31 tests: all sprite names, all sound names, fallback behaviour

**Result:** 53/53 tests pass.

### Tooling
- ruff config migrated from deprecated `[tool.ruff]` to `[tool.ruff.lint]`
- All 27 lint violations resolved (10 I001 auto-fixed, 17 E501 manually wrapped)
- Stale `--help` removed from `main.py` docstring
- `ASSETS_DIR` editable-install limitation documented in `CLAUDE.md`

### How to Verify

```bash
.venv/bin/pytest -v          # 53 passed
.venv/bin/ruff check src/    # All checks passed
```

---

## 2026-03-07 — Sprints 1-3 Complete: Invader Grid Marching

**What was built:** Full project skeleton, asset pipeline, and live invader grid.

### Created / Modified

| File | Purpose |
|------|---------|
| `src/space_invaders/constants.py` | All canonical game values (224×256, 60fps, march bounds, UFO cycle) |
| `src/space_invaders/renderer.py` | 224×256 native surface → nearest-neighbor 3× window blit |
| `src/space_invaders/assets.py` | AssetManager: disk-load or procedural pixel-art/beep fallback |
| `src/space_invaders/entities/grid.py` | InvaderGrid: 5×11 march, 2-frame animation, timing formula |
| `src/space_invaders/entities/player.py` | Player stub (Sprint 4) |
| `src/space_invaders/entities/ufo.py` | UFO stub (Sprint 7) |
| `src/space_invaders/entities/bunker.py` | Bunker/BunkerGroup stub (Sprint 6) |
| `src/space_invaders/entities/bullet.py` | Bullet stub (Sprint 4) |
| `src/space_invaders/scenes/game.py` | GameScene: wires grid, player, UFO, bunkers, HUD |
| `src/space_invaders/scenes/base.py` | Scene abstract class |
| `src/space_invaders/scenes/title.py` | TitleScene stub |
| `src/space_invaders/scenes/cutscene.py` | CutsceneScene stub |
| `src/space_invaders/scenes/gameover.py` | GameOverScene stub |
| `src/space_invaders/sound.py` | SoundManager stub (Sprint 8) |
| `src/space_invaders/hud.py` | Minimal HUD (score/lives text) |
| `src/space_invaders/main.py` | Entry point: init, asset load, 60fps loop, Esc/Q exit |
| `pyproject.toml` | Dependencies added: pygame-ce, numpy, requests, Pillow |
| `.gitignore` | Created; assets/sprites/ and assets/sounds/ excluded |
| `product-definition.md` | Acceptance checklist (Deluxe features) |
| `design.md` | Technical blueprint |
| `sprint-plan.md` | 11-sprint roadmap; Sprints 1-3 marked done |
| `project-plan.md` | Filled in from scaffold template |
| `skills/arcade-accuracy.md` | Pre-done-check skill |
| `skills/pygame-entity.md` | Entity implementation pattern |
| `skills/playtest.md` | Structured observation loop |
| `CLAUDE.md` | Updated commands for venv workflow |

### Key Decision

Package directory renamed `space-invaders/` → `space_invaders/` — Python identifiers cannot contain hyphens. CLI command remains `space-invaders`.

### How to Verify

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# Headless smoke test
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -c "
import pygame; pygame.init(); pygame.mixer.init()
from space_invaders.assets import ensure_assets
from space_invaders.entities.grid import InvaderGrid, march_interval_ms
mgr = ensure_assets()
grid = InvaderGrid(mgr)
grid.update(0.81)
assert grid.frame == 1
print('OK')
"

# Visual launch (requires display)
.venv/bin/space-invaders
```

---

## 2026-03-07 — Project Scaffolded

**Project initialized** with init-agent.

### Created

| File | Purpose |
|------|---------|
| `AGENTS.md` | AI agent guide and conventions |
| `WHERE_AM_I.md` | Quick orientation for agents |
| `feedback.md` | Human feedback capture |
| `README.md` | Project documentation |
| `context.md` | Session working memory |
| `result-review.md` | This file - running log |
| `sprint-plan.md` | Sprint tracking |

### How to Verify

1. Check all files exist: `ls *.md`
2. Read AGENTS.md to understand project conventions
3. Check context.md for current state

---

*Add new entries above this line. Keep the newest work at the top.*
