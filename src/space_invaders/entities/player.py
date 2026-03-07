"""Player cannon entity."""

from __future__ import annotations

import pygame

from .. import constants
from ..assets import AssetManager
from .bullet import Bullet


class Player:
    """Horizontal cannon at the bottom of the screen.

    Movement: left/right arrow keys or A/D.
    Firing: SPACE — one bullet active at a time.
    """

    def __init__(self, asset_mgr: AssetManager):
        frames = asset_mgr.get_sprite_frames("player")
        self._sprite = frames[0]
        w = self._sprite.get_width()
        h = self._sprite.get_height()
        start_x = (constants.SCREEN_W - w) // 2
        self.rect = pygame.Rect(start_x, constants.PLAYER_Y, w, h)
        self._x = float(self.rect.x)
        self.lives = constants.LIVES
        self.score = 0
        self.bullet: Bullet | None = None

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1

        self._x += dx * constants.PLAYER_SPEED * dt
        self._x = max(
            float(constants.LEFT_LIMIT),
            min(self._x, float(constants.RIGHT_LIMIT - self.rect.width)),
        )
        self.rect.x = int(self._x)

        if self.bullet is not None:
            self.bullet.update(dt)
            if not self.bullet.alive:
                self.bullet = None

    def reset_position(self) -> None:
        """Re-centre the cannon and clear any in-flight bullet. Called on respawn."""
        self._x = float((constants.SCREEN_W - self.rect.width) // 2)
        self.rect.x = int(self._x)
        self.bullet = None

    def fire(self) -> Bullet | None:
        """Attempt to fire. Returns new Bullet or None if already active."""
        if self.bullet is not None:
            return None
        bx = self.rect.centerx - Bullet.WIDTH // 2
        by = self.rect.top - Bullet.HEIGHT
        self.bullet = Bullet(bx, by, -constants.BULLET_SPEED)
        return self.bullet

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._sprite, self.rect.topleft)
        if self.bullet is not None:
            self.bullet.draw(surface)
