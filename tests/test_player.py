"""Tests for Player movement, firing, and one-bullet constraint."""

from __future__ import annotations

import pygame
import pytest

from space_invaders import constants
from space_invaders.assets import ensure_assets
from space_invaders.entities.bullet import Bullet
from space_invaders.entities.player import Player


@pytest.fixture(scope="module")
def asset_mgr():
    return ensure_assets()


@pytest.fixture
def player(asset_mgr):
    return Player(asset_mgr)


def _keys(left: bool = False, right: bool = False):
    """Build a minimal keys object usable with player.update()."""

    class FakeKeys:
        def __getitem__(self, key):
            if key in (pygame.K_LEFT, pygame.K_a):
                return left
            if key in (pygame.K_RIGHT, pygame.K_d):
                return right
            return False

    return FakeKeys()


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def test_player_starts_at_player_y(player):
    assert player.rect.top == constants.PLAYER_Y


def test_player_starts_centered(player):
    assert abs(player.rect.centerx - constants.SCREEN_W // 2) <= 1


def test_player_starts_with_no_bullet(player):
    assert player.bullet is None


def test_player_starts_with_correct_lives(player):
    assert player.lives == constants.LIVES


# ---------------------------------------------------------------------------
# Movement
# ---------------------------------------------------------------------------


def test_player_moves_right(player):
    x_before = player.rect.x
    player.update(0.1, _keys(right=True))
    assert player.rect.x > x_before


def test_player_moves_left(asset_mgr):
    p = Player(asset_mgr)
    # Shift to the right first so there is room to move left
    p._x = float(constants.SCREEN_W // 2)
    p.rect.x = int(p._x)
    x_before = p.rect.x
    p.update(0.1, _keys(left=True))
    assert p.rect.x < x_before


def test_player_clamps_left(asset_mgr):
    p = Player(asset_mgr)
    p._x = float(constants.LEFT_LIMIT)
    p.rect.x = int(p._x)
    p.update(1.0, _keys(left=True))
    assert p.rect.x >= constants.LEFT_LIMIT


def test_player_clamps_right(asset_mgr):
    p = Player(asset_mgr)
    p._x = float(constants.RIGHT_LIMIT - p.rect.width)
    p.rect.x = int(p._x)
    p.update(1.0, _keys(right=True))
    assert p.rect.right <= constants.RIGHT_LIMIT


def test_player_stationary_no_keys(player):
    x_before = player.rect.x
    player.update(0.1, _keys())
    assert player.rect.x == x_before


# ---------------------------------------------------------------------------
# Firing
# ---------------------------------------------------------------------------


def test_fire_creates_bullet(player):
    assert player.bullet is None
    b = player.fire()
    assert b is not None
    assert isinstance(b, Bullet)
    assert player.bullet is b


def test_fire_returns_none_when_active(player):
    player.fire()  # first shot
    assert player.bullet is not None
    result = player.fire()  # second attempt
    assert result is None


def test_bullet_spawns_above_player(player):
    player.fire()
    assert player.bullet is not None
    assert player.bullet.rect.bottom <= player.rect.top


def test_bullet_travels_upward(asset_mgr):
    p = Player(asset_mgr)
    p.fire()
    y_before = p.bullet.rect.y
    p.update(0.1, _keys())
    assert p.bullet.rect.y < y_before


def test_bullet_cleared_on_offscreen(asset_mgr):
    p = Player(asset_mgr)
    p.fire()
    # Force bullet off the top of the screen
    p.bullet._y = -20.0
    p.bullet.rect.y = -20
    p.bullet.alive = False  # simulate expiry
    p.update(0.0, _keys())  # update with zero dt so player syncs
    assert p.bullet is None


# ---------------------------------------------------------------------------
# One-bullet constraint
# ---------------------------------------------------------------------------


def test_one_bullet_at_a_time(asset_mgr):
    p = Player(asset_mgr)
    b1 = p.fire()
    b2 = p.fire()
    assert b1 is not None
    assert b2 is None
    assert p.bullet is b1
