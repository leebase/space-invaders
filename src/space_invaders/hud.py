"""HUD rendering — score, hi-score, lives."""

from __future__ import annotations

import pygame

from . import constants


class HUD:
    def __init__(self):
        # Small font; positions derived from surface size at draw time
        self._font = pygame.font.Font(None, 8)

    def draw(
        self, surface: pygame.Surface, score: int = 0, hi_score: int = 0, lives: int = 3
    ) -> None:
        sw = surface.get_width()
        sh = surface.get_height()
        hi_x = sw // 2 - 20
        lives_y = sh - 10
        self._text(surface, "SCORE", 8, 2)
        self._text(surface, "HI-SCORE", hi_x, 2)
        self._val(surface, score, 8, 10)
        self._val(surface, hi_score, hi_x, 10)
        self._text(surface, f"{lives}", 8, lives_y)

    def _text(self, surface: pygame.Surface, s: str, x: int, y: int) -> None:
        rendered = self._font.render(s, False, constants.COLOR_WHITE)
        surface.blit(rendered, (x, y))

    def _val(self, surface: pygame.Surface, v: int, x: int, y: int) -> None:
        capped = min(v, constants.HIGH_SCORE_MAX)
        rendered = self._font.render(f"{capped:05d}", False, constants.COLOR_WHITE)
        surface.blit(rendered, (x, y))
