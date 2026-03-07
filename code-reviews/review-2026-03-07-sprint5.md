# Code Review — Sprint 5 (2026-03-07)

## Architecture Summary

Space Invaders Deluxe clone in Python/pygame-ce. Game renders to a 224×256 `pygame.Surface`, scaled 3× to the window each frame. A single `main.py` loop dispatches events, calls `scene.update(dt)`, and checks `scene.next_scene` for transitions. Sprint 5 added a three-state machine (`PLAYING` / `PLAYER_DEAD` / `ROUND_CLEAR`) in `GameScene`, a functional `GameOverScene`, and the `next_scene` mechanism on the `Scene` base class. No network access in the game loop; no user-provided file paths; no subprocess calls. Security risk is negligible.

## Checks Run

| Command | Result |
|---------|--------|
| `.venv/bin/ruff check src/ tests/` | ✅ Pass |
| `.venv/bin/pytest -q` | ✅ Pass — 92/92 |

## Findings

| ID | Severity | Category | Location | Problem | Proposed Fix |
|----|----------|----------|----------|---------|--------------|
| R001 | Med | Correctness | `scenes/gameover.py:43` | `hi_score` not passed to new `GameScene` on restart — resets to 0 every game | Add `hi_score: int = 0` to `GameScene.__init__`; pass `self.hi_score` in `GameOverScene.handle_event` |
| R002 | Low | Code Quality | `scenes/game.py:133–136` | `_respawn_player()` directly mutates `player._x` (private attribute) — coupling risk if `Player` internals change | Add `Player.reset_position()` method; call it from `GameScene` |
| R003 | Low | Tests | `tests/test_game_loop.py:52` | Misleading comment: *"lives is already 2 from above"* — fixture is function-scoped, so `scene` is fresh with `lives=3` at that test | Fix comment to say "fresh scene, lives=3" |
| R004 | Low | Tests | `tests/test_game_loop.py` | No test that hi_score carries over to the new `GameScene` after pressing any key on the game over screen | Add `test_hi_score_persists_on_restart` (see Test Additions) |
| R005 | Low | Docs | `WHERE_AM_I.md` | Status table still shows Sprint 3 as current; MVP criteria (player movement, collision, scoring) still marked "Not started" despite Sprints 4 and 5 completing them | Update milestone table |

## Remediation Roadmap

### Fix Now (Blockers)
_None._ All findings are Low or Med; no crash or data-loss risk.

### Fix Soon (High ROI)
- **R001** — Every player who achieves a hi-score and restarts will watch it disappear. One-line fix, high user-visible impact. Add before Sprint 6 so the loop is testable end-to-end.

### Fix Later (Refactors)
- **R002** — `Player.reset_position()` is the right interface; can be done as a tidy-up alongside Sprint 6 when player death is fully wired.
- **R003** — Comment-only fix; zero risk to skip until next pass.
- **R004** — Add the test after R001 is fixed (test should fail before fix, pass after).
- **R005** — `WHERE_AM_I.md` update; pure docs, no code risk.

## Patch Suggestions

### R001 — hi_score persistence across restarts

```python
# scenes/game.py — BEFORE
class GameScene(Scene):
    def __init__(self, asset_mgr: AssetManager):
        ...
        self.hi_score = 0

# AFTER
class GameScene(Scene):
    def __init__(self, asset_mgr: AssetManager, hi_score: int = 0):
        ...
        self.hi_score = hi_score
```

```python
# scenes/gameover.py — BEFORE
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            from .game import GameScene
            self.next_scene = GameScene(self._assets)

# AFTER
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            from .game import GameScene
            self.next_scene = GameScene(self._assets, hi_score=self.hi_score)
```

### R002 — Player.reset_position()

```python
# entities/player.py — add method:
def reset_position(self) -> None:
    """Re-centre the player cannon. Called on respawn."""
    self._x = float((constants.SCREEN_W - self.rect.width) // 2)
    self.rect.x = int(self._x)
    self.bullet = None
```

```python
# scenes/game.py _respawn_player() — BEFORE
def _respawn_player(self) -> None:
    self.player._x = float(
        (constants.SCREEN_W - self.player.rect.width) // 2
    )
    self.player.rect.x = int(self.player._x)
    self.player.bullet = None
    self._state = _State.PLAYING
    self._state_timer = 0.0

# AFTER
def _respawn_player(self) -> None:
    self.player.reset_position()
    self._state = _State.PLAYING
    self._state_timer = 0.0
```

## Test Additions Recommended

- [ ] `test_hi_score_persists_on_restart` — create `GameOverScene(asset_mgr, final_score=500, hi_score=1000)`, fire KEYDOWN, assert `go.next_scene.hi_score == 1000`
- [ ] `test_kill_player_when_already_at_zero_lives` — call `kill_player()` when `lives=0`, confirm `lives=-1` does not cause `update()` to crash before R002 is addressed (documents current over-decrement behaviour)
