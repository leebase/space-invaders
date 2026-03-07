"""UFO / Mystery Ship entity. Implemented in Sprint 7."""

from __future__ import annotations

import pygame
from ..assets import AssetManager
from .. import constants


class UFO:
    """Mystery ship that traverses the top of the screen. Sprint 7."""

    def __init__(self, asset_mgr: AssetManager):
        frames = asset_mgr.get_sprite_frames("ufo")
        self._sprite = frames[0]
        self.active = False
        self._timer = 0.0
        self._shot_count = 0  # for score cycle
        self.rect = pygame.Rect(-32, constants.UFO_Y, self._sprite.get_width(), self._sprite.get_height())

    def update(self, dt: float) -> None:
        pass  # Sprint 7

    def draw(self, surface: pygame.Surface) -> None:
        pass  # Sprint 7
