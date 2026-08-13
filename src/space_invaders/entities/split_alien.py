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
from ..mode import GameMode, ModeConfig


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
        screen_w: int | None = None,
        screen_h: int | None = None,
    ):
        self._x = float(x)
        self._y = float(y)
        self.dx = dx
        self.dy = dy
        self._sprite = sprite
        w, h = sprite.get_size()
        self.rect = pygame.Rect(x, y, w, h)
        self.alive = True
        self._screen_w = screen_w if screen_w is not None else constants.SCREEN_W
        self._screen_h = screen_h if screen_h is not None else constants.SCREEN_H

    def update(self, dt: float) -> None:
        self._x += self.dx * dt
        self._y += self.dy * dt
        self.rect.x = int(self._x)
        self.rect.y = int(self._y)
        if (
            self.rect.right < 0
            or self.rect.left > self._screen_w
            or self.rect.bottom < 0
            or self.rect.top > self._screen_h
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

    def __init__(self, asset_mgr: AssetManager, mode_config: ModeConfig | None = None):
        self._cfg = mode_config or ModeConfig(GameMode.ARCADE)
        frames = asset_mgr.get_sprite_frames("split_alien")
        self._sprite = frames[0]
        self._piece_sprite = asset_mgr.get_sprite_frames("split_piece")[0]
        w, h = self._sprite.get_size()
        self.rect = pygame.Rect(self._cfg.screen_w, self._cfg.split_alien_y, w, h)
        self._x = float(self._cfg.screen_w)
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
            self._x -= self._cfg.split_alien_speed * dt
            dy = self._cfg.split_alien_zigzag_amp * math.sin(
                2 * math.pi * constants.SPLIT_ALIEN_ZIGZAG_FREQ * self._t
            )
            self.rect.x = int(self._x)
            self.rect.y = self._cfg.split_alien_y + int(dy)
            if self.rect.right < 0:
                self._deactivate()

    def hit(self) -> list[SplitPiece]:
        """Call when player bullet collides. Returns two SplitPiece entities."""
        cx = self.rect.centerx
        cy = self.rect.centery
        speed = self._cfg.split_piece_speed
        pieces = [
            SplitPiece(
                cx, cy, -speed * 0.7, -speed * 0.7, self._piece_sprite,
                self._cfg.screen_w, self._cfg.screen_h,
            ),
            SplitPiece(
                cx, cy, -speed * 0.7,  speed * 0.7, self._piece_sprite,
                self._cfg.screen_w, self._cfg.screen_h,
            ),
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
        self._x = float(self._cfg.screen_w)
        self.rect.x = int(self._x)
        self.rect.y = self._cfg.split_alien_y
        self._t = 0.0
        self._state = _State.ACTIVE
        self._spawn_timer_ms = 0.0

    def _deactivate(self) -> None:
        self._state = _State.IDLE
        self._spawn_timer_ms = 0.0
