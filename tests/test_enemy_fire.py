"""Tests for Sprint 6: enemy fire, bunker destruction, player hit detection."""

from __future__ import annotations

import pygame
import pytest

from space_invaders import constants
from space_invaders.assets import ensure_assets
from space_invaders.entities.bullet import Bullet
from space_invaders.entities.bunker import Bunker
from space_invaders.entities.grid import InvaderGrid, _fire_interval_ms
from space_invaders.scenes.game import GameScene, _State


@pytest.fixture(scope="module")
def asset_mgr():
    return ensure_assets()


@pytest.fixture
def grid(asset_mgr):
    return InvaderGrid(asset_mgr)


@pytest.fixture
def scene(asset_mgr):
    return GameScene(asset_mgr)


# ---------------------------------------------------------------------------
# _fire_interval_ms
# ---------------------------------------------------------------------------


def test_fire_interval_full_grid():
    assert _fire_interval_ms(55) == constants.ENEMY_FIRE_MAX_MS


def test_fire_interval_single_invader():
    assert _fire_interval_ms(1) == constants.ENEMY_FIRE_MIN_MS


def test_fire_interval_zero_clamps_to_min():
    assert _fire_interval_ms(0) == constants.ENEMY_FIRE_MIN_MS


def test_fire_interval_decreases_with_fewer_invaders():
    assert _fire_interval_ms(10) < _fire_interval_ms(40)


# ---------------------------------------------------------------------------
# InvaderGrid fire timer → pending_bullets
# ---------------------------------------------------------------------------


def test_no_bullets_before_interval(grid):
    grid.update(0.01)  # very short dt
    assert len(grid.pending_bullets) == 0


def test_bullet_produced_after_interval(grid):
    interval_s = constants.ENEMY_FIRE_MAX_MS / 1000.0
    grid.update(interval_s + 0.01)
    assert len(grid.pending_bullets) >= 1


def test_pending_bullet_travels_downward(grid):
    interval_s = constants.ENEMY_FIRE_MAX_MS / 1000.0
    grid.update(interval_s + 0.01)
    for b in grid.pending_bullets:
        assert b.dy > 0, "Enemy bullet must travel downward (positive dy)"


def test_pending_bullet_is_bullet_instance(grid):
    interval_s = constants.ENEMY_FIRE_MAX_MS / 1000.0
    grid.update(interval_s + 0.01)
    for b in grid.pending_bullets:
        assert isinstance(b, Bullet)


def test_fire_timer_resets_after_shot(asset_mgr):
    g = InvaderGrid(asset_mgr)
    interval_s = constants.ENEMY_FIRE_MAX_MS / 1000.0
    g.update(interval_s + 0.01)
    g.pending_bullets.clear()
    g.update(0.01)  # short dt — should not fire again yet
    assert len(g.pending_bullets) == 0


def test_no_fire_when_grid_cleared(asset_mgr):
    g = InvaderGrid(asset_mgr)
    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            g.kill(row, col)
    interval_s = constants.ENEMY_FIRE_MAX_MS / 1000.0
    g.update(interval_s + 0.01)
    assert len(g.pending_bullets) == 0


# ---------------------------------------------------------------------------
# GameScene: enemy bullet cap and lifecycle
# ---------------------------------------------------------------------------


def test_enemy_bullets_capped_at_max(asset_mgr):
    s = GameScene(asset_mgr)
    # Inject more pending bullets than the cap
    for _ in range(constants.ENEMY_BULLET_MAX + 5):
        s.grid.pending_bullets.append(
            Bullet(100, 100, constants.ENEMY_BULLET_SPEED)
        )
    s.update(0.001)
    assert len(s.enemy_bullets) <= constants.ENEMY_BULLET_MAX


def test_enemy_bullets_cleared_on_player_death(scene):
    scene.enemy_bullets = [
        Bullet(100, 200, constants.ENEMY_BULLET_SPEED) for _ in range(3)
    ]
    scene.kill_player()
    assert len(scene.enemy_bullets) == 0


def test_enemy_bullets_cleared_on_round_advance(asset_mgr):
    s = GameScene(asset_mgr)
    s.enemy_bullets = [Bullet(100, 100, constants.ENEMY_BULLET_SPEED)]
    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            s.grid.kill(row, col)
    s.update(0.01)  # → ROUND_CLEAR
    s.update(constants.ROUND_CLEAR_DELAY + 0.01)  # → _next_round
    assert len(s.enemy_bullets) == 0


# ---------------------------------------------------------------------------
# Player hit by enemy bullet → kill_player()
# ---------------------------------------------------------------------------


def test_enemy_bullet_kills_player(asset_mgr):
    s = GameScene(asset_mgr)
    # Place a bullet directly on the player
    b = Bullet(
        s.player.rect.centerx, s.player.rect.centery,
        constants.ENEMY_BULLET_SPEED,
    )
    s.enemy_bullets = [b]
    s.update(0.001)
    assert s._state == _State.PLAYER_DEAD
    assert s.player.lives == constants.LIVES - 1


def test_enemy_bullet_marked_dead_on_hit(asset_mgr):
    s = GameScene(asset_mgr)
    b = Bullet(
        s.player.rect.centerx, s.player.rect.centery,
        constants.ENEMY_BULLET_SPEED,
    )
    s.enemy_bullets = [b]
    s.update(0.001)
    # bullet is removed from list (filtered out because alive=False)
    assert b not in s.enemy_bullets


# ---------------------------------------------------------------------------
# Bunker.apply_damage() — pixel destruction via surfarray
# ---------------------------------------------------------------------------


def test_apply_damage_removes_pixels(asset_mgr):
    b = Bunker(50, asset_mgr)
    cx = b.surface.get_width() // 2
    cy = b.surface.get_height() // 2
    b.apply_damage(b.rect.x + cx, b.rect.y + cy, radius=2)
    arr_after = pygame.surfarray.array_alpha(b.surface)
    # Pixels within radius 2 of centre should now be transparent
    assert arr_after[cx, cy] == 0


def test_apply_damage_out_of_bounds_does_not_crash(asset_mgr):
    b = Bunker(50, asset_mgr)
    # Hit at the very edge/outside — should not raise
    b.apply_damage(b.rect.x - 10, b.rect.y - 10, radius=3)
    b.apply_damage(b.rect.right + 10, b.rect.bottom + 10, radius=3)


# ---------------------------------------------------------------------------
# Bunker stops player bullet
# ---------------------------------------------------------------------------


def test_player_bullet_stopped_by_bunker(asset_mgr):
    s = GameScene(asset_mgr)
    bunker = s.bunkers.bunkers[0]
    # Place a player bullet colliding with the bunker
    bx = bunker.rect.centerx
    by = bunker.rect.top
    s.player.bullet = Bullet(bx, by, -constants.BULLET_SPEED)
    s.update(0.001)
    assert s.player.bullet is None


# ---------------------------------------------------------------------------
# Bunker stops enemy bullet
# ---------------------------------------------------------------------------


def test_enemy_bullet_stopped_by_bunker(asset_mgr):
    s = GameScene(asset_mgr)
    bunker = s.bunkers.bunkers[0]
    b = Bullet(
        bunker.rect.centerx, bunker.rect.top,
        constants.ENEMY_BULLET_SPEED,
    )
    s.enemy_bullets = [b]
    s.update(0.001)
    assert b not in s.enemy_bullets
