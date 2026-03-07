"""Game over screen with high score / initials entry. Implemented in Sprint 10."""

from __future__ import annotations

import pygame
from .base import Scene
from ..assets import AssetManager
from .. import constants


class GameOverScene(Scene):
    def __init__(self, asset_mgr: AssetManager, final_score: int = 0):
        self._font = pygame.font.Font(None, 16)
        self.final_score = final_score

    def update(self, dt: float) -> None:
        pass  # Sprint 10

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(constants.COLOR_BG)
        text = self._font.render("GAME OVER", False, constants.COLOR_WHITE)
        x = (constants.SCREEN_W - text.get_width()) // 2
        surface.blit(text, (x, 110))
