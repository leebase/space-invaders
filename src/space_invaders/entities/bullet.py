"""Bullet entity — player and enemy variants. Implemented in Sprint 4."""

from __future__ import annotations

import pygame


class Bullet:
    """A single bullet travelling in one direction.

    Args:
        x, y: initial top-left position (native pixels)
        dy: pixels per second; negative = up (player), positive = down (enemy)
    """

    WIDTH = 1
    HEIGHT = 6

    def __init__(self, x: int, y: int, dy: float):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.dy = dy
        self.alive = True

    def update(self, dt: float) -> None:
        self.rect.y += int(self.dy * dt)
        if self.rect.bottom < 0 or self.rect.top > 256:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.alive:
            pygame.draw.rect(surface, (255, 255, 255), self.rect)
