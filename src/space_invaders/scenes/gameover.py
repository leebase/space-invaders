"""Game over screen. Implemented in Sprint 5 (basic). Sprint 10 adds initials."""

from __future__ import annotations

import pygame

from .. import constants
from ..assets import AssetManager
from .base import Scene


class GameOverScene(Scene):
    def __init__(
        self,
        asset_mgr: AssetManager,
        final_score: int = 0,
        hi_score: int = 0,
    ):
        self._assets = asset_mgr
        self._font = pygame.font.Font(None, 16)
        self.final_score = final_score
        self.hi_score = hi_score

    def update(self, dt: float) -> None:
        pass  # Sprint 10: initials entry

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(constants.COLOR_BG)

        lines = [
            ("GAME OVER", constants.COLOR_WHITE, 96),
            (f"SCORE  {self.final_score:05d}", constants.COLOR_GREEN, 116),
            (f"BEST   {self.hi_score:05d}", constants.COLOR_CYAN, 132),
            ("PRESS ANY KEY", constants.COLOR_WHITE, 160),
        ]
        for text, color, y in lines:
            surf = self._font.render(text, False, color)
            x = (constants.SCREEN_W - surf.get_width()) // 2
            surface.blit(surf, (x, y))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            from .game import GameScene
            self.next_scene = GameScene(self._assets, hi_score=self.hi_score)
