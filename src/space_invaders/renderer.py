import pygame
from . import constants


class Renderer:
    """Owns the 224×256 native surface and the scaled display window.

    Game code draws to `self.surface` at native resolution. Each call to
    `present()` scales that surface 3× (nearest-neighbor, no smoothing) and
    blits it to the window.
    """

    def __init__(self):
        self.surface = pygame.Surface((constants.SCREEN_W, constants.SCREEN_H))
        self.window = pygame.display.set_mode(
            (constants.SCREEN_W * constants.SCALE, constants.SCREEN_H * constants.SCALE)
        )
        pygame.display.set_caption("Space Invaders Deluxe")

    def clear(self):
        self.surface.fill(constants.COLOR_BG)

    def present(self):
        scaled = pygame.transform.scale(
            self.surface,
            (constants.SCREEN_W * constants.SCALE, constants.SCREEN_H * constants.SCALE),
        )
        self.window.blit(scaled, (0, 0))
        pygame.display.flip()
