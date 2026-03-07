# Code Review — Full Project (Post-Sprint 7)

**Date:** 2026-03-07
**Reviewer:** Claude Code
**Scope:** All source files (`src/space_invaders/`) and tests (`tests/`)
**Baseline:** 131/131 tests pass, `ruff check` clean

---

## Summary

The codebase is in good shape. One medium-severity bug (UFO not reset on round advance) and several low-severity issues. All other logic, architecture, and test coverage is sound.

---

## Findings

### R001 — [MEDIUM] UFO not reset in `_next_round()` (correctness bug)

**File:** `src/space_invaders/scenes/game.py:189-195`

`_next_round()` creates a fresh `InvaderGrid` and clears bullets, but leaves `self.ufo` untouched. If the UFO is ACTIVE at the moment the last invader is killed (triggering ROUND_CLEAR), it stays ACTIVE into round 2 — visible, moving, hittable, and not on its expected spawn timer.

`_shot_count` should persist (it's session-wide per arcade rules), but state and position must reset.

**Fix:** Call `self.ufo.reset()` in `_next_round()`. Implement `UFO.reset()` to return to IDLE with position off-screen-left and spawn timer zeroed, while preserving `_shot_count`.

---

### R002 — [LOW] Enemy bullets visible/frozen during ROUND_CLEAR

**File:** `src/space_invaders/scenes/game.py:106-107`

`draw()` always renders `self.enemy_bullets`, but `update()` only advances them during `_State.PLAYING`. If the grid is cleared while enemy bullets are in flight, they freeze in place and remain drawn for the full `ROUND_CLEAR_DELAY`.

**Fix:** Clear `self.enemy_bullets` when entering ROUND_CLEAR (alongside clearing the player bullet).

---

### R003 — [LOW] Redundant state guard in `_check_enemy_bullet_collisions()`

**File:** `src/space_invaders/scenes/game.py:182-184`

```python
if (
    self._state == _State.PLAYING
    and b.rect.colliderect(self.player.rect)
):
```

`_check_enemy_bullet_collisions()` is only ever called from within the `if self._state == _State.PLAYING:` block. The guard is always true and can be removed.

**Fix:** Remove the `self._state == _State.PLAYING` condition from the player collision check inside `_check_enemy_bullet_collisions()`.

---

### R004 — [LOW] Score update pattern duplicated 3×

**File:** `src/space_invaders/scenes/game.py:150-151, 161-162`

```python
self.score = min(self.score + pts, constants.HIGH_SCORE_MAX)
self.hi_score = max(self.hi_score, self.score)
```

This two-line pattern appears three times in `_check_player_bullet_collisions()`. A small helper `_award(pts)` would eliminate the duplication.

**Fix:** Extract `_award(self, pts: int) -> None` and call it in all three places.

---

### R005 — [LOW] Unreachable guard in `_try_fire()`

**File:** `src/space_invaders/entities/grid.py`

```python
if row is None:
    return None
```

This guard follows a loop that selects the lowest alive invader in a column from `alive_cols`. The column was drawn from `alive_cols`, which only contains columns with at least one alive invader, so `row` is guaranteed to be non-None. The guard is dead code.

**Fix:** Remove the `if row is None: return None` guard, or convert it to an `assert row is not None` for documentation purposes.

---

### R006 — [LOW] `Renderer.clear()` is dead code

**File:** `src/space_invaders/renderer.py`

`Renderer.clear()` fills the native surface with `COLOR_BG`. However, every scene's `draw()` already begins with `surface.fill(constants.COLOR_BG)`. `clear()` is never called from `main.py`. It is unused.

**Fix:** Remove `Renderer.clear()`.

---

### R007 — [LOW] Missing test: UFO not reset between rounds

No test verifies that a UFO active at round clear is properly reset before round 2. Once R001 is fixed, add a regression test.

---

### R008 — [LOW] Missing test: enemy bullets cleared on round clear

No test verifies that enemy bullets in flight at round clear are cleared before round 2. Once R002 is fixed, add a regression test.

---

## Not Flagged (verified correct)

- Float-position accumulators in Player and Bullet: correct
- `pending_bullets` drain with cap: correct
- Filter-after-collision ordering: correct
- `convert_alpha()` display.set_mode in conftest: correct
- UFO `_shot_count` persists across rounds (session-wide): correct per arcade rules
- Deferred imports for circular dependency resolution: correct
- `hi_score` threaded through GameOverScene → GameScene: correct
- surfarray column-major indexing in `apply_damage()`: correct
- `invader_at()` uses `rect.top` (leading edge of bullet): correct
- March `while` loop with per-step interval recalculation: correct
- Boundary centering with `_max_sprite_w_in_col`: correct

---

## Action Plan

| ID | Severity | Action |
|----|----------|--------|
| R001 | Med | Add `UFO.reset()`, call from `_next_round()` |
| R002 | Low | Clear `enemy_bullets` when entering ROUND_CLEAR |
| R003 | Low | Remove redundant state guard |
| R004 | Low | Extract `_award()` helper |
| R005 | Low | Remove unreachable guard in `_try_fire()` |
| R006 | Low | Remove `Renderer.clear()` |
| R007 | Low | Add test: UFO reset on round advance |
| R008 | Low | Add test: enemy bullets cleared on round clear |
