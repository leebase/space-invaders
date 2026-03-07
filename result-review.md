# space-invaders Result Review

> **Running log of completed work.** Newest entries at the top.
>
> Each entry documents what was built, why it matters, and how to verify it works.

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
