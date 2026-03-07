"""Title / attract screen. Implemented in Sprint 10."""

from __future__ import annotations

import pygame

from .. import constants
from ..assets import AssetManager
from .base import Scene


class TitleScene(Scene):
    def __init__(self, asset_mgr: AssetManager):
        self._font = pygame.font.Font(None, 16)

    def update(self, dt: float) -> None:
        pass  # Sprint 10

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(constants.COLOR_BG)
        text = self._font.render("SPACE INVADERS DELUXE", False, constants.COLOR_WHITE)
        x = (constants.SCREEN_W - text.get_width()) // 2
        surface.blit(text, (x, 100))

    def handle_event(self, event: pygame.event.Event) -> None:
        pass  # Sprint 10
