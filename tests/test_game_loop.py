"""Tests for Sprint 5 game loop: lives, round advance, game over conditions."""

from __future__ import annotations

import pytest

from space_invaders import constants
from space_invaders.assets import ensure_assets
from space_invaders.scenes.game import GameScene, _State
from space_invaders.scenes.gameover import GameOverScene


@pytest.fixture(scope="module")
def asset_mgr():
    return ensure_assets()


@pytest.fixture
def scene(asset_mgr):
    return GameScene(asset_mgr)


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def test_scene_starts_in_playing_state(scene):
    assert scene._state == _State.PLAYING


def test_scene_starts_round_one(scene):
    assert scene._round == 1


def test_scene_starts_with_no_next_scene(scene):
    assert scene.next_scene is None


# ---------------------------------------------------------------------------
# kill_player(): decrement lives, enter PLAYER_DEAD
# ---------------------------------------------------------------------------


def test_kill_player_decrements_lives(scene):
    assert scene.player.lives == constants.LIVES
    scene.kill_player()
    assert scene.player.lives == constants.LIVES - 1


def test_kill_player_enters_dead_state(scene):
    # scene.player.lives is already 2 from above; kill once more
    scene.kill_player()
    assert scene._state == _State.PLAYER_DEAD


def test_kill_player_clears_bullet(asset_mgr):
    s = GameScene(asset_mgr)
    s.player.fire()
    assert s.player.bullet is not None
    s.kill_player()
    assert s.player.bullet is None


# ---------------------------------------------------------------------------
# PLAYER_DEAD → respawn after delay
# ---------------------------------------------------------------------------


def test_respawn_after_delay(asset_mgr):
    s = GameScene(asset_mgr)
    s.kill_player()  # lives = 2, PLAYER_DEAD
    assert s._state == _State.PLAYER_DEAD
    # Simulate enough time for respawn
    s.update(constants.RESPAWN_DELAY + 0.01)
    assert s._state == _State.PLAYING


def test_respawn_recenters_player(asset_mgr):
    s = GameScene(asset_mgr)
    # Move player to an edge
    s.player._x = float(constants.LEFT_LIMIT)
    s.player.rect.x = constants.LEFT_LIMIT
    s.kill_player()
    s.update(constants.RESPAWN_DELAY + 0.01)
    expected_x = (constants.SCREEN_W - s.player.rect.width) // 2
    assert abs(s.player.rect.x - expected_x) <= 1


# ---------------------------------------------------------------------------
# PLAYER_DEAD → game over when lives exhausted
# ---------------------------------------------------------------------------


def test_game_over_after_last_life(asset_mgr):
    s = GameScene(asset_mgr)
    s.player.lives = 1
    s.kill_player()  # lives → 0, PLAYER_DEAD
    s.update(constants.RESPAWN_DELAY + 0.01)
    assert s.next_scene is not None
    assert isinstance(s.next_scene, GameOverScene)


# ---------------------------------------------------------------------------
# Game over: invaders reach kill line
# ---------------------------------------------------------------------------


def test_game_over_invaders_reach_bottom(asset_mgr):
    s = GameScene(asset_mgr)
    # Force the grid's y so lowest_row_y() >= INVADER_KILL_LINE
    # lowest_row_y() = grid_y + 4*CELL_H + SPRITE_H for full grid
    s.grid.grid_y = (
        constants.INVADER_KILL_LINE
        - 4 * constants.CELL_H
        - constants.SPRITE_H
        + 1
    )
    s.update(0.01)
    assert s.next_scene is not None
    assert isinstance(s.next_scene, GameOverScene)


def test_game_over_carries_score(asset_mgr):
    s = GameScene(asset_mgr)
    s.score = 1234
    s.player.lives = 1
    s.kill_player()
    s.update(constants.RESPAWN_DELAY + 0.01)
    assert s.next_scene.final_score == 1234


# ---------------------------------------------------------------------------
# Round advance: grid cleared
# ---------------------------------------------------------------------------


def _kill_all(s: GameScene) -> None:
    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            s.grid.kill(row, col)


def test_round_clear_state_on_grid_cleared(asset_mgr):
    s = GameScene(asset_mgr)
    _kill_all(s)
    s.update(0.01)
    assert s._state == _State.ROUND_CLEAR


def test_round_advance_resets_grid(asset_mgr):
    s = GameScene(asset_mgr)
    _kill_all(s)
    s.update(0.01)  # → ROUND_CLEAR
    s.update(constants.ROUND_CLEAR_DELAY + 0.01)  # → _next_round()
    assert s.grid.total_alive == constants.GRID_ROWS * constants.GRID_COLS


def test_round_advance_increments_round(asset_mgr):
    s = GameScene(asset_mgr)
    _kill_all(s)
    s.update(0.01)
    s.update(constants.ROUND_CLEAR_DELAY + 0.01)
    assert s._round == 2


def test_round_advance_preserves_score(asset_mgr):
    s = GameScene(asset_mgr)
    s.score = 990
    _kill_all(s)
    s.update(0.01)
    s.update(constants.ROUND_CLEAR_DELAY + 0.01)
    assert s.score == 990


def test_round_advance_returns_to_playing(asset_mgr):
    s = GameScene(asset_mgr)
    _kill_all(s)
    s.update(0.01)
    s.update(constants.ROUND_CLEAR_DELAY + 0.01)
    assert s._state == _State.PLAYING


# ---------------------------------------------------------------------------
# Firing blocked during non-PLAYING states
# ---------------------------------------------------------------------------


def test_cannot_fire_while_dead(asset_mgr):
    import pygame

    s = GameScene(asset_mgr)
    s.kill_player()
    event = pygame.event.Event(
        pygame.KEYDOWN,
        {"key": pygame.K_SPACE, "mod": 0, "unicode": " ", "scancode": 0},
    )
    s.handle_event(event)
    assert s.player.bullet is None


# ---------------------------------------------------------------------------
# GameOverScene: restart creates new GameScene
# ---------------------------------------------------------------------------


def test_gameover_restart_on_keypress(asset_mgr):
    import pygame

    go = GameOverScene(asset_mgr, final_score=500, hi_score=1000)
    assert go.next_scene is None
    event = pygame.event.Event(
        pygame.KEYDOWN,
        {"key": pygame.K_SPACE, "mod": 0, "unicode": " ", "scancode": 0},
    )
    go.handle_event(event)
    assert go.next_scene is not None
    assert isinstance(go.next_scene, GameScene)
