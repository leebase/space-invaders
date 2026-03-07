"""Splitting alien — Space Invaders Deluxe exclusive entity.

A special alien that traverses right→left in a zigzag pattern.
When the player bullet hits it, it splits into two SplitPiece entities
that move diagonally off-screen.
"""

from __future__ import annotations

import enum
import math

import pygame

from .. import constants
from ..assets import AssetManager


class _State(enum.Enum):
    IDLE = "idle"
    ACTIVE = "active"


class SplitPiece:
    """A small fragment spawned when a SplitAlien is hit."""

    def __init__(
        self,
        x: int,
        y: int,
        dx: float,
        dy: float,
        sprite: pygame.Surface,
    ):
        self._x = float(x)
        self._y = float(y)
        self.dx = dx
        self.dy = dy
        self._sprite = sprite
        w, h = sprite.get_size()
        self.rect = pygame.Rect(x, y, w, h)
        self.alive = True

    def update(self, dt: float) -> None:
        self._x += self.dx * dt
        self._y += self.dy * dt
        self.rect.x = int(self._x)
        self.rect.y = int(self._y)
        if (
            self.rect.right < 0
            or self.rect.left > constants.SCREEN_W
            or self.rect.bottom < 0
            or self.rect.top > constants.SCREEN_H
        ):
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.alive:
            surface.blit(self._sprite, self.rect.topleft)


class SplitAlien:
    """Mystery alien that traverses right→left in a zigzag path.

    Spawns every SPLIT_ALIEN_INTERVAL_MS.  On bullet hit, splits into
    two SplitPiece entities moving in opposite diagonal directions.
    """

    def __init__(self, asset_mgr: AssetManager):
        frames = asset_mgr.get_sprite_frames("split_alien")
        self._sprite = frames[0]
        self._piece_sprite = asset_mgr.get_sprite_frames("split_piece")[0]
        w, h = self._sprite.get_size()
        self.rect = pygame.Rect(constants.SCREEN_W, constants.SPLIT_ALIEN_Y, w, h)
        self._x = float(constants.SCREEN_W)
        self._t: float = 0.0          # time accumulator for zigzag phase
        self._state = _State.IDLE
        self._spawn_timer_ms: float = 0.0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def active(self) -> bool:
        return self._state == _State.ACTIVE

    def update(self, dt: float) -> None:
        if self._state == _State.IDLE:
            self._spawn_timer_ms += dt * 1000.0
            if self._spawn_timer_ms >= constants.SPLIT_ALIEN_INTERVAL_MS:
                self._spawn()

        elif self._state == _State.ACTIVE:
            self._t += dt
            self._x -= constants.SPLIT_ALIEN_SPEED * dt
            dy = constants.SPLIT_ALIEN_ZIGZAG_AMP * math.sin(
                2 * math.pi * constants.SPLIT_ALIEN_ZIGZAG_FREQ * self._t
            )
            self.rect.x = int(self._x)
            self.rect.y = constants.SPLIT_ALIEN_Y + int(dy)
            if self.rect.right < 0:
                self._deactivate()

    def hit(self) -> list[SplitPiece]:
        """Call when player bullet collides. Returns two SplitPiece entities."""
        cx = self.rect.centerx
        cy = self.rect.centery
        speed = constants.SPLIT_PIECE_SPEED
        pieces = [
            SplitPiece(cx, cy, -speed * 0.7, -speed * 0.7, self._piece_sprite),
            SplitPiece(cx, cy, -speed * 0.7,  speed * 0.7, self._piece_sprite),
        ]
        self._deactivate()
        return pieces

    def reset(self) -> None:
        """Return to IDLE without preserving timer (called on round advance)."""
        self._state = _State.IDLE
        self._spawn_timer_ms = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        if self._state == _State.ACTIVE:
            surface.blit(self._sprite, self.rect.topleft)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _spawn(self) -> None:
        self._x = float(constants.SCREEN_W)
        self.rect.x = int(self._x)
        self.rect.y = constants.SPLIT_ALIEN_Y
        self._t = 0.0
        self._state = _State.ACTIVE
        self._spawn_timer_ms = 0.0

    def _deactivate(self) -> None:
        self._state = _State.IDLE
        self._spawn_timer_ms = 0.0
