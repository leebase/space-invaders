"""Player cannon entity. Implemented in Sprint 4."""

from __future__ import annotations

import pygame
from ..assets import AssetManager
from .. import constants


class Player:
    """Horizontal cannon at the bottom of the screen.

    Implemented in Sprint 4. For now this is a stub so GameScene can
    instantiate it without errors.
    """

    def __init__(self, asset_mgr: AssetManager):
        frames = asset_mgr.get_sprite_frames("player")
        self._sprite = frames[0]
        w = self._sprite.get_width()
        h = self._sprite.get_height()
        start_x = (constants.SCREEN_W - w) // 2
        self.rect = pygame.Rect(start_x, constants.PLAYER_Y, w, h)
        self.lives = constants.LIVES
        self.score = 0
        self.bullet: object | None = None  # Sprint 4

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        pass  # Sprint 4

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._sprite, self.rect.topleft)
