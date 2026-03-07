"""HUD rendering — score, hi-score, lives.

Full implementation in Sprint 4+. For Sprint 3 this provides a minimal
text overlay so the native surface has something in the top bar.
"""

from __future__ import annotations

import pygame
from . import constants


class HUD:
    def __init__(self):
        # Small font that fits the 224×256 native surface
        self._font = pygame.font.Font(None, 8)

    def draw(self, surface: pygame.Surface, score: int = 0, hi_score: int = 0, lives: int = 3) -> None:
        self._text(surface, "SCORE", 8, 2)
        self._text(surface, "HI-SCORE", 88, 2)
        self._val(surface, score, 8, 10)
        self._val(surface, hi_score, 88, 10)
        # Lives at bottom
        self._text(surface, f"{lives}", 8, 246)

    def _text(self, surface: pygame.Surface, s: str, x: int, y: int) -> None:
        rendered = self._font.render(s, False, constants.COLOR_WHITE)
        surface.blit(rendered, (x, y))

    def _val(self, surface: pygame.Surface, v: int, x: int, y: int) -> None:
        rendered = self._font.render(f"{v:04d}", False, constants.COLOR_WHITE)
        surface.blit(rendered, (x, y))
