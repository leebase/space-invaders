# Code Review — Sprint 9 Complete (2026-03-07)

## Architecture Summary

Space Invaders Deluxe is a Python 3.12+ / pygame-ce implementation using a scene-based architecture. The main loop (`main.py`) drives a current `Scene` object, switching via the `next_scene` attribute. Core gameplay lives in `GameScene`, which orchestrates `InvaderGrid` (55-invader march logic with descent-color tinting), `Player` (movement, one-bullet constraint), `UFO` (spawn timer, deterministic score cycle), `SplitAlien` (zigzag path, fragment spawning), `BunkerGroup` (pixel-destructible surfarray shields), and `SoundManager` (march sequencer locked to visual tempo). Assets are procedurally generated as fallbacks if disk files missing. The game renders at native 224×256, scales 3× nearest-neighbor for display. No external network calls or user-provided file paths — attack surface is minimal.

## Checks Run

| Command | Result |
|---------|--------|
| `pytest -q` | ✅ 179 passed |
| `ruff check src/ tests/` | ✅ All checks passed |

## Findings

| ID | Severity | Category | Location | Problem | Proposed Fix |
|----|----------|----------|----------|---------|--------------|
| R001 | Med | Correctness | `src/space_invaders/scenes/cutscene.py:69` | Cutscene unconditionally sets `next_scene` when timer expires, potentially overwriting a user-triggered transition | Add guard: `if self.next_scene is None:` before assignment |
| R002 | Med | Edge Case | `src/space_invaders/entities/bunker.py:38-40, 44-46` | `pixels_alpha()` surface lock released via `del arr`; exception before deletion leaves surface locked | Use try/finally: `try: arr[...]=0; finally: del arr` |
| R003 | Low | Code Quality | `src/space_invaders/constants.py:40,101` | `ROUND_CLEAR_DELAY` defined twice (1.5 then overwritten by 0.5) | Remove line 40; keep only the Sprint 9 value |
| R004 | Low | Code Quality | `src/space_invaders/assets.py:204` | `ASSETS_DIR` uses fragile `__file__.parent.parent.parent.parent` chain | Document the assumption or use `importlib.resources` for installed packages |
| R005 | Low | Code Quality | `src/space_invaders/scenes/game.py:260-262` | Local import of `CutsceneScene` inside method risks circular import on refactor | Move to top-level import or use scene factory registry |
| R006 | Low | Edge Case | `src/space_invaders/entities/ufo.py:88` | Score text clamping only handles right edge; left edge (x<0) not clamped | Add `x = max(0, x)` before the existing clamp |
| R007 | Low | Documentation | `design.md:136` | File path shows `src/space-invaders/` (hyphen) but actual is `src/space_invaders/` (underscore) | Update documentation to match actual paths |
| R008 | Low | Documentation | `product-definition.md` | CRT scanline overlay marked unchecked but constant exists (Sprint 10) | No action needed; tracked in Sprint 10 |

## Finding Details

### R001 — Cutscene Transition Race

```python
# src/space_invaders/scenes/cutscene.py:69
if self._timer >= constants.CUTSCENE_DURATION:
    self.next_scene = self._game_scene  # Overwrites user keypress!
```

If user presses a key (line 109-110 sets `next_scene`), then on the same frame the timer check fires, the user's skip is overwritten. Fix:

```python
if self._timer >= constants.CUTSCENE_DURATION:
    if self.next_scene is None:  # Only if not already skipped
        self.next_scene = self._game_scene
```

### R002 — Surface Lock Safety

```python
# src/space_invaders/entities/bunker.py:38-40
arr = pygame.surfarray.pixels_alpha(self.surface)
arr[x1:x2, y1:y2] = 0
del arr  # Never reached if exception above
```

If `MemoryError` or `KeyboardInterrupt` occurs during slice assignment, the surface stays locked. Fix:

```python
arr = pygame.surfarray.pixels_alpha(self.surface)
try:
    arr[x1:x2, y1:y2] = 0
finally:
    del arr
```

Same pattern needed in `is_destroyed()` at lines 44-46.

### R003 — Duplicate Constant Definition

`ROUND_CLEAR_DELAY = 1.5` at line 40 is immediately overwritten by `ROUND_CLEAR_DELAY = 0.5` at line 101. This is confusing — remove the first definition.

## Remediation Roadmap

### Fix Now (Blockers)
None — all tests pass, no crashes or security issues.

### Fix Soon (High ROI / Low Effort)
- **R001** — Cutscene race: 1-line guard, prevents user frustration
- **R002** — Surface lock safety: 4-line try/finally, prevents resource leak on edge cases
- **R003** — Duplicate constant: delete 1 line, reduces confusion

### Fix Later (Polish)
- **R004** — Asset path fragility: only matters if packaging for PyPI
- **R005** — Local import pattern: refactor risk, not current bug
- **R006** — UFO score text left-clamp: cosmetic edge case
- **R007** — Documentation sync: Sprint 10 documentation pass

## Test Additions Recommended

- [ ] **Test:** Cutscene keypress followed by timer expiry — verify keypress wins (catches R001)
- [ ] **Test:** Bunker damage with exception injection — verify surface not locked (catches R002)
- [ ] **Test:** UFO hit at extreme left edge (x < 0) — verify score text visible (catches R006)
- [ ] **Test:** Split alien spawn timing — verify interval is exactly SPLIT_ALIEN_INTERVAL_MS
- [ ] **Test:** Split piece scoring — verify each piece awards SPLIT_PIECE_SCORE
- [ ] **Test:** Descent color bands — verify exact Y thresholds trigger correct colors

## Coverage Notes

| Module | Lines | Status |
|--------|-------|--------|
| `entities/grid.py` | 275 | Well tested (march, fire, kill, color) |
| `entities/player.py` | 68 | Well tested (movement, fire, bullet lifecycle) |
| `entities/bunker.py` | 68 | Tested (damage, destruction) |
| `entities/ufo.py` | 111 | Well tested (spawn, cycle, HIT state) |
| `entities/split_alien.py` | 140 | Tested (26 tests in test_deluxe.py) |
| `scenes/game.py` | 286 | Well tested via integration tests |
| `scenes/cutscene.py` | 110 | Basic tests (transition, skip) — see R001 gap |
| `sound.py` | 102 | Well tested (march tempo, mute, drone) |
| `assets.py` | 343 | Tested (fallback, disk load) |

**Gap identified:** `scenes/title.py` is a stub (Sprint 10) — no tests expected yet.

## Security Assessment

**Threat model:** Local desktop game, no network, no user file paths.

- No subprocess calls with user input
- No file writes outside assets/ (which is gitignored)
- No deserialization of untrusted data
- No SQL/query languages

**Conclusion:** No security findings. Attack surface limited to pygame surface overflows (handled by SDL).

## Performance Observations

- `pixels_alpha()` allocation every bunker hit — acceptable at bullet rate
- Tint cache in `InvaderGrid._get_tinted()` prevents per-frame surface creation
- March while-loop in `SoundManager.update()` can play multiple notes per frame at high tempo — intentional design

No action needed; performance is acceptable for target hardware.

---
*Review completed: 179 tests pass, ruff clean, 8 findings (0 Critical, 0 High, 2 Med, 6 Low)*
