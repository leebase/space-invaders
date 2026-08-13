"""Bullet entity — player and enemy variants."""

from __future__ import annotations

import pygame

from .. import constants


class Bullet:
    """A single bullet travelling in one direction.

    Args:
        x, y: initial top-left position (native pixels)
        dy: pixels per second; negative = up (player), positive = down (enemy)
        screen_h: native screen height for off-screen culling (defaults to arcade value)
    """

    WIDTH = 1
    HEIGHT = 6

    def __init__(self, x: int, y: int, dy: float, screen_h: int | None = None):
        self._y = float(y)
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.dy = dy
        self.alive = True
        self._screen_h = screen_h if screen_h is not None else constants.SCREEN_H

    def update(self, dt: float) -> None:
        self._y += self.dy * dt
        self.rect.y = int(self._y)
        if self.rect.bottom < 0 or self.rect.top > self._screen_h:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.alive:
            pygame.draw.rect(surface, (255, 255, 255), self.rect)
