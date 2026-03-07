"""Pixel-destructible bunker entity. Implemented in Sprint 6."""

from __future__ import annotations

import pygame

from .. import constants
from ..assets import AssetManager


class Bunker:
    """A single pixel-destructible bunker. Sprint 6."""

    def __init__(self, x: int, asset_mgr: AssetManager):
        base = asset_mgr.get_sprite_frames("bunker")[0]
        self.surface = base.copy().convert_alpha()
        self.rect = pygame.Rect(
            x, constants.BUNKER_Y, constants.BUNKER_W, constants.BUNKER_H
        )

    def apply_damage(self, hit_x: int, hit_y: int, radius: int = 3) -> None:
        pass  # Sprint 6

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect.topleft)


class BunkerGroup:
    """Four bunkers evenly spaced across the screen. Sprint 6."""

    def __init__(self, asset_mgr: AssetManager):
        spacing = constants.SCREEN_W // (constants.BUNKER_COUNT + 1)
        self.bunkers = [
            Bunker(spacing * (i + 1) - constants.BUNKER_W // 2, asset_mgr)
            for i in range(constants.BUNKER_COUNT)
        ]

    def update(self, dt: float) -> None:
        pass  # Sprint 6

    def draw(self, surface: pygame.Surface) -> None:
        for b in self.bunkers:
            b.draw(surface)
