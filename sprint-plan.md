# Sprint Plan — Space Invaders Deluxe

> **Tactical execution.** Active sprint is detailed; future sprints are scoped but not detailed until active.
> For product goals, see `product-definition.md`. For architecture, see `design.md`.

---

## Roadmap Overview

| Sprint | Focus | Status |
|--------|-------|--------|
| 1 | Project skeleton — window, game loop, renderer | ✅ Done |
| 2 | Asset pipeline — download, verify, fallback | ✅ Done |
| 3 | Invader grid — visual only, march animation | ✅ Done |
| 4.5 | Code review remediation — bugs, tests, lint | ✅ Done |
| 4 | Player + shooting + invader collision | ✅ Done |
| 5 | Game loop — lives, win/lose, round advance | ✅ Done |
| 6 | Enemy fire + pixel-destructible bunkers | ✅ Done |
| 7 | UFO — spawn, traverse, score cycle | ✅ Done |
| 8 | Sound — march tempo, all effects | ⬜ Planned |
| 9 | Deluxe features — split, rainbow, cutscenes, color | ⬜ Planned |
| 10 | Game states — title, game over, high score, pause | ⬜ Planned |
| 11 | Accuracy pass — playtest, fix deviations, ship | ⬜ Planned |

---

## Sprint 1 — Project Skeleton ✅

**Done:** Window opens at 672×768, 60 fps game loop, exits on Esc/Q.

**Note:** Package directory renamed to `src/space_invaders/` (underscore required for Python import). Venv at `.venv/`.

### Tasks

- [x] **1.1** Dependencies added to `pyproject.toml`
- [x] **1.2** `src/space_invaders/constants.py` — all canonical values
- [x] **1.3** `src/space_invaders/renderer.py` — 224×256 surface, 3× nearest-neighbor scale
- [x] **1.4** `src/space_invaders/main.py` — 60 fps game loop, Esc/Q exits
- [x] **1.5** All module stubs created (scenes/, entities/, sound, hud)
- [x] **1.6** `.venv/bin/pip install -e ".[dev]"` succeeds; headless smoke test passes

---

## Sprint 2 — Asset Pipeline ✅

**Done:** `ensure_assets()` runs at startup; all sprites and sounds available via `AssetManager`. Procedural pixel-art fallbacks for all types; beep fallbacks for all sounds.

### Tasks

- [x] **2.1** `src/space_invaders/assets.py` — `AssetManager`, `ensure_assets()`
- [x] **2.2** Sprite disk-load attempt (PNG spritesheet from `assets/sprites/`)
- [x] **2.3** Procedural pixel-art sprite fallback for all invader types + player/UFO/bunker/explosion
- [x] **2.4** Sound disk-load attempt (`assets/sounds/`)
- [x] **2.5** Procedural square-wave beep fallback for all sounds
- [x] **2.6** `.gitignore` created; `assets/sprites/` and `assets/sounds/` excluded
- [x] **2.7** `ensure_assets()` called in `main()` before game loop

---

## Sprint 3 — Invader Grid (Visual) ✅

**Done:** 55 invaders marching with correct tempo, 2-frame animation alternating per step, drop on direction change. March interval formula verified (800ms@55 → 50ms@1).

### Tasks

- [x] **3.1** `src/space_invaders/entities/grid.py` — `InvaderGrid`, `march_interval_ms()`
- [x] **3.2** Squid/Crab/Octopus sprites (2 frames each) loaded via `AssetManager`
- [x] **3.3** March: step 2px left/right, drop 8px on boundary hit, interval recalculates per step
- [x] **3.4** Animation: frame advances on march step, not on clock
- [x] **3.5** Wired into `GameScene`; player/UFO/bunker stubs draw without error
- [x] **3.6** Headless test: march mechanics, frame advance, boundary step verified

---

## Sprint 4.5 — Code Review Remediation

**Goal:** All findings from `code-reviews/review-2026-03-07.md` resolved. Tests pass, linter clean, correctness bugs fixed.

**Done when:** `pytest` collects ≥ 9 tests and all pass; `ruff check src/` exits 0; march boundary and HUD score are correct.

### Tasks

- [x] **4.5.1** R003 — `while` loop in `InvaderGrid.update()`
- [x] **4.5.2** R002 + R007 — Boundary centering + `_max_sprite_w_in_col()` replaces topmost-row lookup
- [x] **4.5.3** R004 — HUD score `{v:05d}` capped at `HIGH_SCORE_MAX`
- [x] **4.5.4** R006 — Spritesheet dimension validation warning added
- [x] **4.5.5** R005 — `ASSETS_DIR` editable-install limitation documented in `CLAUDE.md`
- [x] **4.5.6** R008 — ruff config migrated to `[tool.ruff.lint]`
- [x] **4.5.7** R009 — All 27 lint violations resolved (10 auto-fixed I001, 17 manual E501 wraps)
- [x] **4.5.8** R010 — Stale `--help` removed from `main.py` docstring
- [x] **4.5.9** R001 — `tests/conftest.py`, `tests/test_grid.py`, `tests/test_assets.py` added (53 tests)
- [x] **4.5.10** 53/53 tests pass; `ruff check src/` clean; headless smoke test passes

---

## Sprint 4 — Player + Shooting + Invader Collision

**Goal:** Player can move and shoot. Hitting an invader removes it and increments score. HUD shows live score.

**Done when:** Player moves, fires one bullet at a time, invaders die on hit, score increments correctly (Squid 30, Crab 20, Octopus 10).

**Done:** Player moves (A/D or arrow keys), fires one bullet at a time (Space), invaders die on hit with correct score values, march tempo recalculates each kill. 74/74 tests pass.

### Tasks

- [x] **4.1** `player.py` — horizontal movement, screen-constrained, float-position accumulator
- [x] **4.2** `bullet.py` — upward travel, float-position accumulator, off-screen despawn
- [x] **4.3** `hud.py` — score display (already done in Sprint 4.5)
- [x] **4.4** Collision: player bullet vs. invader grid, score increment, high score tracking
- [x] **4.5** March tempo recalculates after each kill (handled by while loop + total_alive)
- [x] **4.6** Point values verified: Squid=30, Crab=20, Octopus=10
- [x] `constants.py` — BULLET_SPEED=300 added
- [x] `tests/test_player.py` — 15 tests: movement, clamping, fire, one-bullet constraint
- [x] `tests/test_bullet.py` — 6 tests: travel, boundary despawn, float accumulation

---

## Sprint 5 — Game Loop (Lives, Win/Lose, Round Advance)

**Goal:** The game has a complete loop. Player has 3 lives. Dying costs a life. All invaders cleared = next round. Invaders reach bottom = game over.

**Done when:** Can play multiple rounds; game over triggers correctly; round advance works.

**Done:** State machine in `GameScene` handles lives, round advance, and both game-over conditions. `GameOverScene` shows score and restarts on any key. 92/92 tests pass.

### Tasks

- [x] **5.1** Lives system — `kill_player()`, `PLAYER_DEAD` state, `RESPAWN_DELAY` countdown
- [x] **5.2** Round advance — `ROUND_CLEAR` state → `_next_round()` resets grid, preserves score
- [x] **5.3** Game over — invaders reach `INVADER_KILL_LINE` or lives reach 0
- [x] **5.4** `GameOverScene` — score display, `PRESS ANY KEY` restart
- [x] **5.5** Scene switching via `next_scene` attribute; `main.py` checks each frame
- [x] `tests/conftest.py` — `display.set_mode(1,1)` added for `convert_alpha()` compat
- [x] `tests/test_game_loop.py` — 18 tests: state transitions, round advance, game over, restart

---

## Sprint 6 — Enemy Fire + Bunkers

**Goal:** Invaders shoot downward. 4 pixel-destructible bunkers absorb shots from above and below.

**Done when:** Multiple enemy bullets active simultaneously; bunkers erode pixel-by-pixel on hit from either direction; damage persists between rounds.

**Done:** Invaders fire downward. Multiple simultaneous bullets (max 3). Bunkers erode via numpy surfarray on hit from either direction. Enemy bullet hitting player triggers kill_player(). 112/112 tests pass.

### Tasks

- [x] **6.1** Enemy bullet reuses `Bullet(dy>0)` — downward travel, off-screen despawn
- [x] **6.2** `InvaderGrid` fire timer + `_try_fire()` — lowest invader in random column; rate linearly scales ENEMY_FIRE_MAX_MS→ENEMY_FIRE_MIN_MS
- [x] **6.3** `Bunker.apply_damage()` — numpy `surfarray.pixels_alpha()` zeroed in radius
- [x] **6.4** `BunkerGroup` — 4 bunkers evenly spaced (already positioned, now functional)
- [x] **6.5** Collision: enemy bullet vs. bunker; player bullet vs. bunker (checked before invaders on upward path)
- [x] **6.6** Enemy bullet vs. player rect → `kill_player()`; field cleared on death
- [x] **6.7** Enemy bullet filter moved after collision checks (bug fix: bullet wasn't removed same frame)
- [x] `tests/test_enemy_fire.py` — 19 tests: fire interval, pending bullets, cap, bunker damage, player kill

---

## Sprint 7 — UFO

**Goal:** Mystery ship appears at correct intervals, traverses top of screen, awards deterministic score on hit.

**Done when:** UFO spawns ~every 25 seconds, traverses correctly, UFO score cycle matches `CYCLE` constant, score displays on hit.

**Done:** UFO spawns every 25s, traverses left→right at 80px/s, displays score for 1s on hit, cycles through UFO_SCORE_CYCLE deterministically. 131/131 tests pass.

### Tasks

- [x] **7.1** `ufo.py` — `_State` enum (IDLE/ACTIVE/HIT), float-x accumulator, spawn timer
- [x] **7.2** Collision: player bullet vs. UFO in `_check_player_bullet_collisions()` (after bunkers, before invaders)
- [x] **7.3** Score text drawn at hit position for `UFO_HIT_DISPLAY_S = 1.0s`
- [x] **7.4** Score cycle: `UFO_SCORE_CYCLE[shot_count % len(CYCLE)]` — all 15 values verified in tests
- [x] `constants.py` — `UFO_SPEED = 80`, `UFO_HIT_DISPLAY_S = 1.0` added
- [x] `tests/test_ufo.py` — 19 tests: spawn, traverse, cycle, HIT state, collision

---

## Sprint 8 — Sound

**Goal:** All required sounds play. March loop tempo is locked to visual march speed.

**Done when:** All 6 sound categories work; march audio and visual march are perceptibly in sync at all tempos.

### Tasks (detail added when sprint becomes active)

- [ ] **8.1** Create `src/space-invaders/sound.py` — `SoundManager`, 4-channel march sequencer
- [ ] **8.2** March tempo sync — note interval matches `march_interval_ms(remaining)`
- [ ] **8.3** Shoot, kill, death, UFO drone, UFO hit sounds wired to events
- [ ] **8.4** Mute/unmute support (nice to have for dev iteration)
- [ ] **8.5** Arcade accuracy check (sound identity, tempo feel)

---

## Sprint 9 — Deluxe Features

**Goal:** All four Space Invaders Deluxe exclusive features implemented.

**Done when:** Split aliens work, rainbow bonus triggers correctly, cutscenes play between rounds, invaders change color on descent. Each verified against reference footage.

### Tasks (detail added when sprint becomes active)

- [ ] **9.1** Splitting aliens — qualifying invader hit spawns two sub-entities at half value
- [ ] **9.2** Rainbow bonus — 500 pts last alien bottom rows, 1000 pts bottom-left; verify trigger conditions against reference
- [ ] **9.3** Invader color change on descent — palette swap as rows advance downward
- [ ] **9.4** Create `src/space-invaders/scenes/cutscene.py` — inter-round cutscene matching Deluxe originals
- [ ] **9.5** Arcade accuracy check on all four features (most critical sprint for accuracy)

---

## Sprint 10 — Game States + Polish

**Goal:** Complete game shell — title screen, game over with high score entry, pause.

**Done when:** Full game flow navigable without touching the code. High score initials entry works. CRT overlay applied.

### Tasks (detail added when sprint becomes active)

- [ ] **10.1** `TitleScene` — attract screen, press-start prompt
- [ ] **10.2** `GameOverScene` — high score + initials entry (3 characters)
- [ ] **10.3** CRT scanline overlay — numpy pre-computed mask, applied post-scale each frame
- [ ] **10.4** Pause (toggle on P or Esc during gameplay)
- [ ] **10.5** High score persistence (session-only; no file persistence needed per spec)
- [ ] **10.6** High score cap enforced at 99,990

---

## Sprint 11 — Accuracy Pass

**Goal:** All `product-definition.md` acceptance criteria checked off. Game feels like the arcade original.

**Done when:** Every item in `product-definition.md` is checked. Playtested against reference footage. No `# UNVERIFIED` comments remaining (or each is consciously accepted with a backlog item).

### Tasks (detail added when sprint becomes active)

- [ ] **11.1** Run `skills/playtest.md` — full structured observation against reference footage
- [ ] **11.2** Fix all `accuracy-bug` deviations found
- [ ] **11.3** Resolve or formally accept all `# UNVERIFIED` comments
- [ ] **11.4** Check off every item in `product-definition.md`
- [ ] **11.5** Final `skills/arcade-accuracy.md` pass on all mechanics
- [ ] **11.6** Update `WHERE_AM_I.md` — project complete

---

## Completed Sprints

_(none yet)_
