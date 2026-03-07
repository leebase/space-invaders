"""Pixel-destructible bunker entity."""

from __future__ import annotations

import numpy as np
import pygame

from .. import constants
from ..assets import AssetManager


class Bunker:
    """A single pixel-destructible bunker.

    Damage is applied by zeroing the alpha channel of pixels in a small
    rectangular region around the hit point, making them transparent.
    """

    def __init__(self, x: int, asset_mgr: AssetManager):
        base = asset_mgr.get_sprite_frames("bunker")[0]
        self.surface = base.copy().convert_alpha()
        self.rect = pygame.Rect(
            x, constants.BUNKER_Y, constants.BUNKER_W, constants.BUNKER_H
        )

    def apply_damage(self, hit_x: int, hit_y: int, radius: int = 3) -> None:
        """Erase pixels within *radius* of (hit_x, hit_y) in surface coords."""
        lx = hit_x - self.rect.x
        ly = hit_y - self.rect.y
        w, h = self.surface.get_size()
        x1 = max(0, lx - radius)
        x2 = min(w, lx + radius + 1)
        y1 = max(0, ly - radius)
        y2 = min(h, ly + radius + 1)
        if x2 <= x1 or y2 <= y1:
            return
        # pixels_alpha returns a (w, h) array — column-major (x, y)
        arr = pygame.surfarray.pixels_alpha(self.surface)
        arr[x1:x2, y1:y2] = 0
        del arr  # release surface lock

    def is_destroyed(self) -> bool:
        """True if no opaque pixels remain."""
        arr = pygame.surfarray.pixels_alpha(self.surface)
        result = bool(np.any(arr > 0))
        del arr
        return not result

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect.topleft)


class BunkerGroup:
    """Four bunkers evenly spaced across the screen."""

    def __init__(self, asset_mgr: AssetManager):
        spacing = constants.SCREEN_W // (constants.BUNKER_COUNT + 1)
        self.bunkers = [
            Bunker(spacing * (i + 1) - constants.BUNKER_W // 2, asset_mgr)
            for i in range(constants.BUNKER_COUNT)
        ]

    def update(self, dt: float) -> None:
        pass  # bunkers are purely reactive — damage applied by collision logic

    def draw(self, surface: pygame.Surface) -> None:
        for b in self.bunkers:
            b.draw(surface)
