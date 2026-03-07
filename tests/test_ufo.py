"""Tests for Sprint 7: UFO spawn, traverse, score cycle, collision."""

from __future__ import annotations

import pytest

from space_invaders import constants
from space_invaders.assets import ensure_assets
from space_invaders.entities.bullet import Bullet
from space_invaders.entities.ufo import UFO, _State
from space_invaders.scenes.game import GameScene


@pytest.fixture(scope="module")
def asset_mgr():
    return ensure_assets()


@pytest.fixture
def ufo(asset_mgr):
    return UFO(asset_mgr)


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def test_ufo_starts_idle(ufo):
    assert not ufo.active
    assert ufo._state == _State.IDLE


def test_ufo_starts_off_screen_left(ufo):
    assert ufo.rect.right <= 0


# ---------------------------------------------------------------------------
# Spawn timer
# ---------------------------------------------------------------------------


def test_ufo_does_not_spawn_before_interval(ufo):
    ufo.update(0.1)
    assert not ufo.active


def test_ufo_spawns_after_interval(asset_mgr):
    u = UFO(asset_mgr)
    u.update(constants.UFO_INTERVAL_MS / 1000.0 + 0.01)
    assert u.active


def test_ufo_spawn_resets_timer(asset_mgr):
    u = UFO(asset_mgr)
    u.update(constants.UFO_INTERVAL_MS / 1000.0 + 0.01)
    assert u._spawn_timer_ms == 0.0


def test_ufo_starts_at_left_edge_on_spawn(asset_mgr):
    u = UFO(asset_mgr)
    u.update(constants.UFO_INTERVAL_MS / 1000.0 + 0.01)
    assert u.rect.right <= 4  # just off or at left edge


# ---------------------------------------------------------------------------
# Traversal
# ---------------------------------------------------------------------------


def test_ufo_moves_right_when_active(asset_mgr):
    u = UFO(asset_mgr)
    u._spawn()
    x_before = u.rect.x
    u.update(0.1)
    assert u.rect.x > x_before


def test_ufo_deactivates_at_right_edge(asset_mgr):
    u = UFO(asset_mgr)
    u._spawn()
    # Place UFO just before the right edge
    u._x = float(constants.SCREEN_W - 1)
    u.rect.x = int(u._x)
    u.update(0.1)
    assert not u.active
    assert u._state == _State.IDLE


def test_ufo_y_stays_constant(asset_mgr):
    u = UFO(asset_mgr)
    u._spawn()
    u.update(0.5)
    assert u.rect.top == constants.UFO_Y


# ---------------------------------------------------------------------------
# Score cycle
# ---------------------------------------------------------------------------


def test_hit_returns_first_cycle_value(ufo):
    ufo._spawn()
    score = ufo.hit()
    assert score == constants.UFO_SCORE_CYCLE[0]


def test_hit_increments_shot_count(asset_mgr):
    u = UFO(asset_mgr)
    u._spawn()
    u.hit()
    assert u._shot_count == 1


def test_hit_cycles_through_values(asset_mgr):
    u = UFO(asset_mgr)
    cycle = constants.UFO_SCORE_CYCLE
    for expected in cycle:
        u._spawn()
        assert u.hit() == expected
        u._deactivate()


def test_hit_wraps_cycle(asset_mgr):
    u = UFO(asset_mgr)
    cycle = constants.UFO_SCORE_CYCLE
    n = len(cycle)
    # exhaust one full cycle
    for _ in range(n):
        u._spawn()
        u.hit()
        u._deactivate()
    # next hit should wrap to index 0
    u._spawn()
    assert u.hit() == cycle[0]


# ---------------------------------------------------------------------------
# HIT state: score display, then return to IDLE
# ---------------------------------------------------------------------------


def test_hit_enters_hit_state(asset_mgr):
    u = UFO(asset_mgr)
    u._spawn()
    u.hit()
    assert u._state == _State.HIT


def test_ufo_not_active_during_hit_state(asset_mgr):
    u = UFO(asset_mgr)
    u._spawn()
    u.hit()
    assert not u.active


def test_ufo_returns_to_idle_after_display(asset_mgr):
    u = UFO(asset_mgr)
    u._spawn()
    u.hit()
    u.update(constants.UFO_HIT_DISPLAY_S + 0.01)
    assert u._state == _State.IDLE


# ---------------------------------------------------------------------------
# GameScene: player bullet vs. UFO collision
# ---------------------------------------------------------------------------


def test_player_bullet_hits_ufo(asset_mgr):
    s = GameScene(asset_mgr)
    s.ufo._spawn()
    # Place bullet on UFO
    b = Bullet(
        s.ufo.rect.centerx, s.ufo.rect.centery, -constants.BULLET_SPEED
    )
    s.player.bullet = b
    s.update(0.001)
    assert s.player.bullet is None
    assert not s.ufo.active  # entered HIT state


def test_player_bullet_ufo_awards_score(asset_mgr):
    s = GameScene(asset_mgr)
    s.ufo._spawn()
    b = Bullet(
        s.ufo.rect.centerx, s.ufo.rect.centery, -constants.BULLET_SPEED
    )
    s.player.bullet = b
    s.update(0.001)
    expected = constants.UFO_SCORE_CYCLE[0]
    assert s.score == expected


def test_inactive_ufo_not_hittable(asset_mgr):
    s = GameScene(asset_mgr)
    assert not s.ufo.active
    # Place bullet at UFO_Y — should pass through without triggering hit
    b = Bullet(s.ufo.rect.centerx, constants.UFO_Y, -constants.BULLET_SPEED)
    s.player.bullet = b
    score_before = s.score
    s.update(0.001)
    assert s.score == score_before
