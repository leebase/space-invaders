import pygame

from . import constants


class Renderer:
    """Owns the 224×256 native surface and the scaled display window.

    Game code draws to `self.surface` at native resolution. Each call to
    `present()` scales that surface 3× (nearest-neighbor, no smoothing) and
    blits it to the window. A CRT scanline overlay is applied after scaling
    for retro visual effect.
    """

    def __init__(self):
        self.surface = pygame.Surface((constants.SCREEN_W, constants.SCREEN_H))
        self.window = pygame.display.set_mode(
            (constants.SCREEN_W * constants.SCALE, constants.SCREEN_H * constants.SCALE)
        )
        pygame.display.set_caption("Space Invaders Deluxe")

        # Pre-compute CRT scanline overlay surface (zero per-frame allocation)
        self._scanline_overlay = self._create_scanline_overlay()

    def _create_scanline_overlay(self) -> pygame.Surface:
        """Create a pre-computed scanline overlay surface.

        Every other horizontal row has a semi-transparent black line
        to simulate CRT scanline effect.

        Returns:
            Surface with per-pixel alpha, sized to scaled display dimensions.
        """
        width = constants.SCREEN_W * constants.SCALE
        height = constants.SCREEN_H * constants.SCALE

        # Create surface with per-pixel alpha channel
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        # Fill with transparent (no scanlines on odd rows)
        overlay.fill((0, 0, 0, 0))

        # Draw semi-transparent black lines on every 2nd row (y % 2 == 0)
        scanline_color = (0, 0, 0, constants.SCANLINE_ALPHA)
        for y in range(0, height, 2):
            pygame.draw.line(overlay, scanline_color, (0, y), (width, y))

        return overlay

    def present(self):
        sc = constants.SCALE
        scaled = pygame.transform.scale(
            self.surface, (constants.SCREEN_W * sc, constants.SCREEN_H * sc)
        )
        self.window.blit(scaled, (0, 0))

        # Apply CRT scanline overlay (pre-computed, zero allocation)
        self.window.blit(self._scanline_overlay, (0, 0))

        pygame.display.flip()
