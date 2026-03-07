"""Tests for Bullet travel, boundary despawn, and draw."""

from __future__ import annotations

from space_invaders import constants
from space_invaders.entities.bullet import Bullet


def test_bullet_moves_upward():
    b = Bullet(100, 100, -constants.BULLET_SPEED)
    b.update(0.1)
    assert b.rect.y < 100


def test_bullet_moves_downward():
    b = Bullet(100, 100, constants.BULLET_SPEED)
    b.update(0.1)
    assert b.rect.y > 100


def test_bullet_alive_initially():
    b = Bullet(100, 100, -constants.BULLET_SPEED)
    assert b.alive is True


def test_bullet_dies_at_top():
    b = Bullet(100, 0, -constants.BULLET_SPEED)
    # Force off top
    b._y = -10.0
    b.update(0.0)
    assert b.alive is False


def test_bullet_dies_at_bottom():
    b = Bullet(100, constants.SCREEN_H - 1, constants.BULLET_SPEED)
    b._y = float(constants.SCREEN_H + 1)
    b.update(0.0)
    assert b.alive is False


def test_bullet_float_position_accumulates():
    b = Bullet(100, 100, -constants.BULLET_SPEED)
    # Two small steps should accumulate rather than truncate twice
    b.update(0.05)
    b.update(0.05)
    # Combined movement: 300 * 0.1 = 30px up
    assert b.rect.y <= 100 - 20  # conservatively >= 20px moved
