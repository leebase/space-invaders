---

## Sprint 16 — Avatar Mode: Coordinate System Fix

**Goal:** Fix the critical coordinate mismatch in Avatar mode so that all gameplay
elements (player, bullets, invader grid, bunkers, UFO, split alien, HUD, ground line)
operate in a coherent 2× coordinate space that matches the 448×512 native surface.

**Root cause (from post-sprint-15 analysis):**
`ModeConfig` correctly doubled the native surface and invader cell size, but every
entity continued reading positions and speeds from `constants.py` (arcade values).
This caused:
- March limits hit immediately → grid descends every step
- Player moves in x-range 0–224 while invaders span 26–378 → right columns unreachable
- Grid overlaps player and bunkers at startup
- Renderer lost on round 2+ (`_next_round` never calls `set_renderer`)

**Done when:**
- Player can shoot invaders in all 11 columns in Avatar mode
- March stays within screen bounds; no premature descent
- Grid, player, bunkers, UFO all correctly positioned at 2× coordinates
- Avatar renderer survives round advance (round 2+)
- Arcade mode is completely unaffected
- All pre-existing tests pass; new avatar regression tests added

---

### Tasks

#### 16.1 — Extend `ModeConfig` with all coordinate properties

**File:** `src/space_invaders/mode.py`

Add `coord_scale` and derive all position/speed values from it. `ModeConfig` becomes the
single source of truth for both display AND gameplay coordinates.

```python
cs = 2 if mode == GameMode.AVATAR else 1
self.coord_scale        = cs
self.screen_w           = 224 * cs
self.screen_h           = 256 * cs
self.scale              = 3 if cs == 1 else 2
self.cell_w             = 16 * cs
self.cell_h             = 16 * cs
self.crt_enabled        = (cs == 1)
self.smooth_scale       = (cs == 2)
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

Bunker dimensions added to `ModeConfig` (previously only on old `AVATAR_BUNKER_*` constants).

- [ ] **16.1** Add `coord_scale` and all derived properties to `ModeConfig`

---

#### 16.2 — Refactor `InvaderGrid` to use `ModeConfig`

**File:** `src/space_invaders/entities/grid.py`

`InvaderGrid.__init__` currently uses `constants.GRID_START_X/Y` and `constants.LEFT/RIGHT_LIMIT`
and `constants.MARCH_STEP_X/Y`. Replace with values from a `ModeConfig` parameter.

Key changes:
- Accept `mode_config: ModeConfig` in `__init__`
- Use `mode_config.grid_start_x/y` for initial position
- Use `mode_config.left_limit / right_limit` for march boundary checks
- Use `mode_config.march_step_x/y` for horizontal/vertical movement
- Fix `_next_round` bug: store `mode_config`; re-apply renderer in `GameScene._next_round`
  (renderer fix is in task 16.7)

Also fix `lowest_row_y` which uses `constants.SPRITE_H` — use `mode_config.cell_h` instead
(or a sprite height derived from cell size).

Also fix `_try_fire`: bullet spawn Y uses `constants.CELL_H` — use `mode_config.cell_h`.

- [ ] **16.2** `InvaderGrid.__init__` accepts `ModeConfig`; uses mode-aware start, limits, steps
- [ ] **16.3** `InvaderGrid._march_step` uses `mode_config.march_step_x/y` and limits
- [ ] **16.4** `InvaderGrid.lowest_row_y` uses `mode_config.cell_h` instead of `constants.SPRITE_H`
- [ ] **16.5** `InvaderGrid._try_fire` uses `mode_config.cell_h` for bullet spawn Y

---

#### 16.3 — Refactor `Player` to use `ModeConfig`

**File:** `src/space_invaders/entities/player.py`

Player currently reads `constants.PLAYER_Y`, `constants.PLAYER_SPEED`, `constants.BULLET_SPEED`,
and `constants.SCREEN_W` for movement bounds.

- [ ] **16.6** `Player.__init__` accepts `ModeConfig`; uses `mode_config.player_y`, `player_speed`, `bullet_speed`
- [ ] **16.7** Player horizontal movement bounded by `mode_config.screen_w` (not `constants.SCREEN_W`)

---

#### 16.4 — Refactor `BunkerGroup` and `Bunker` to use `ModeConfig`

**File:** `src/space_invaders/entities/bunker.py`

Bunkers use `constants.BUNKER_Y`, `BUNKER_W`, `BUNKER_H`, `BUNKER_COUNT`, and
`constants.SCREEN_W` to space them evenly.

- [ ] **16.8** `BunkerGroup.__init__` accepts `ModeConfig`; positions bunkers using `mode_config.bunker_y`, `bunker_w`, `bunker_h`, `screen_w`
- [ ] **16.9** Each `Bunker` sized from `ModeConfig` values

---

#### 16.5 — Refactor `UFO` to use `ModeConfig`

**File:** `src/space_invaders/entities/ufo.py`

UFO uses `constants.UFO_Y`, `constants.UFO_SPEED`, and `constants.SCREEN_W` for traversal.

- [ ] **16.10** `UFO.__init__` accepts `ModeConfig`; uses `mode_config.ufo_y`, `ufo_speed`, `screen_w`

---

#### 16.6 — Refactor `SplitAlien` and `SplitPiece` to use `ModeConfig`

**File:** `src/space_invaders/entities/split_alien.py`

SplitAlien uses `constants.SPLIT_ALIEN_Y/SPEED/ZIGZAG_AMP/INTERVAL_MS`,
`constants.SCREEN_W`, and `constants.SPLIT_PIECE_SPEED`.

- [ ] **16.11** `SplitAlien.__init__` accepts `ModeConfig`; uses mode-aware position and speed constants
- [ ] **16.12** `SplitPiece` uses `mode_config.split_piece_speed`

---

#### 16.7 — Fix `GameScene` — coordinate usage and `_next_round` renderer bug

**File:** `src/space_invaders/scenes/game.py`

Multiple fixes required:

1. **Pass `ModeConfig` to all entities on construction:**
   - `InvaderGrid(asset_mgr, mode_config)`
   - `Player(asset_mgr, mode_config)`
   - `BunkerGroup(asset_mgr, mode_config)`
   - `UFO(asset_mgr, mode_config)`
   - `SplitAlien(asset_mgr, mode_config)`

2. **Fix `_next_round()`** — re-apply renderer after creating fresh grid:
   ```python
   def _next_round(self):
       self._round += 1
       self.grid = InvaderGrid(self._assets, self.mode_config)
       if self.mode_config.mode == GameMode.AVATAR:
           self.grid.set_renderer(AvatarRenderer(self._assets))
       else:
           self.grid.set_renderer(PixelRenderer(self._assets))
       ...
   ```

3. **Fix `_draw_ground_line`** — use `self.mode_config.screen_w` and `mode_config.player_y`
   instead of `constants.SCREEN_W` and `constants.PLAYER_Y`.

4. **Fix `_draw_pause_overlay`** — use `mode_config.screen_w/screen_h`.

5. **Fix invader kill-line check** — use `mode_config.invader_kill_line` instead of
   `constants.INVADER_KILL_LINE`.

- [ ] **16.13** GameScene passes `ModeConfig` to all entities
- [ ] **16.14** `_next_round` re-applies renderer to new grid
- [ ] **16.15** `_draw_ground_line` uses `mode_config` screen width and player Y
- [ ] **16.16** `_draw_pause_overlay` uses `mode_config` screen dimensions
- [ ] **16.17** Kill-line check uses `mode_config.invader_kill_line`

---

#### 16.8 — Fix `HUD` for variable screen dimensions

**File:** `src/space_invaders/hud.py`

HUD score/lives text is positioned relative to `constants.SCREEN_W`. In Avatar mode the
native surface is 448px wide — HUD elements must reposition accordingly.

- [ ] **16.18** `HUD.draw` accepts screen width/height (or `ModeConfig`) and positions elements correctly

---

#### 16.9 — Improve `AvatarRenderer` generation quality

**File:** `src/space_invaders/entities/invader_renderer.py`

Avatar cells are now confirmed at 32×32 (matching 2× coord scale). Raise generation
resolution from 64px to 128px for better supersampling (4× instead of 2×).

Also update `get_cell_size()` to return `(32, 32)` — already correct, no change needed there.

- [ ] **16.19** Raise `AVATAR_GENERATE_SIZE` from 64 to 128 for 4× supersampling quality

---

#### 16.10 — Update and extend tests

**File:** `tests/test_deluxe.py` and new `tests/test_avatar_mode.py`

Existing tests that construct `InvaderGrid`, `Player`, `BunkerGroup`, `UFO`, or `SplitAlien`
must pass a `ModeConfig(GameMode.ARCADE)` to maintain arcade behaviour.

New Avatar mode regression tests:

- [ ] **16.20** Update existing entity tests to pass `ModeConfig(GameMode.ARCADE)` explicitly
- [ ] **16.21** Avatar: grid starts at correct 2× position (52, 128)
- [ ] **16.22** Avatar: march boundary uses 2× limits (8, 440); no premature descent on first step
- [ ] **16.23** Avatar: player position is at 2× Y (432)
- [ ] **16.24** Avatar: bullet from player center can reach column 10 invader (x=~346)
- [ ] **16.25** Avatar: `invader_at()` returns correct cell for 2× coordinates
- [ ] **16.26** Avatar: round 2 grid has renderer attached (not None)
- [ ] **16.27** Avatar: bunkers positioned at 2× Y (384), sized 44×32
- [ ] **16.28** Arcade mode: all 251 pre-existing tests still pass (regression guard)

---

#### 16.11 — Playtest and acceptance

- [ ] **16.29** Launch in Avatar mode; verify march moves correctly left and right
- [ ] **16.30** Verify player can shoot invaders in column 0 and column 10
- [ ] **16.31** Verify advancing to round 2 shows avatars (renderer intact)
- [ ] **16.32** Launch in Arcade mode; verify visually unchanged
- [ ] **16.33** Run full test suite; all tests pass

---

### Acceptance Checklist

Before marking Sprint 16 done, all of the following must be true:

- [ ] Avatar mode: march never triggers premature descent on startup
- [ ] Avatar mode: player bullet reaches rightmost column (col 10)
- [ ] Avatar mode: round 2 invaders are visible with avatar faces
- [ ] Avatar mode: player, bunkers, ground line at correct 2× positions
- [ ] Avatar mode: UFO traverses at 2× Y coordinate
- [ ] Arcade mode: visually identical to pre-sprint behaviour
- [ ] All tests pass (target: 260+ tests)

---

## Completed Sprints

| Sprint | Focus | Status |
|--------|-------|--------|
| 1-11 | Core arcade game | ✅ Done |
| 12 | Mode System & Config | ✅ Done |
| 13 | Procedural Generator | ✅ Done |
| 14 | Rendering Pipeline | ✅ Done |
| 15 | External Tooling | ✅ Done |
| 16 | Avatar Coordinate Fix | 🔄 Active |

---

*Update this file when sprints complete or plans change. For current status, see `context.md`.*
