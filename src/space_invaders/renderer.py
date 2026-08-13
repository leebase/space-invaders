import pygame

from . import constants
from .mode import GameMode, ModeConfig


class Renderer:
    """Owns the native surface and the scaled display window.

    Game code draws to `self.surface` at native resolution. Each call to
    `present()` scales to the window. The scaling method and effects depend
    on the game mode:

    - ARCADE: 224×256, nearest-neighbor scaling, CRT scanline overlay
    - AVATAR: 448×512, smooth scaling, no CRT overlay
    """

    def __init__(self, mode_config: ModeConfig | None = None):
        """Initialize renderer with mode-specific configuration.

        Args:
            mode_config: Display configuration for the selected game mode.
                        If None, defaults to ARCADE mode.
        """
        self.config = mode_config or ModeConfig(GameMode.ARCADE)

        # Create native surface at mode-specific resolution
        self.surface = pygame.Surface((self.config.screen_w, self.config.screen_h))

        # Create window at scaled size
        window_w = self.config.screen_w * self.config.scale
        window_h = self.config.screen_h * self.config.scale
        self.window = pygame.display.set_mode((window_w, window_h))

        mode_name = "Arcade" if self.config.mode == GameMode.ARCADE else "Avatar"
        pygame.display.set_caption(f"Space Invaders Deluxe — {mode_name} Mode")

        # Pre-compute CRT scanline overlay (only for arcade mode)
        self._scanline_overlay = None
        if self.config.crt_enabled:
            self._scanline_overlay = self._create_scanline_overlay()

    def _create_scanline_overlay(self) -> pygame.Surface:
        """Create a pre-computed scanline overlay surface.

        Every other horizontal row has a semi-transparent black line
        to simulate CRT scanline effect.

        Returns:
            Surface with per-pixel alpha, sized to scaled display dimensions.
        """
        width = self.config.screen_w * self.config.scale
        height = self.config.screen_h * self.config.scale

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
        """Scale the native surface and present to the window."""
        sc = self.config.scale
        target_size = (self.config.screen_w * sc, self.config.screen_h * sc)

        # Choose scaling method based on mode
        if self.config.smooth_scale:
            scaled = pygame.transform.smoothscale(self.surface, target_size)
        else:
            scaled = pygame.transform.scale(self.surface, target_size)

        self.window.blit(scaled, (0, 0))

        # Apply CRT scanline overlay (only for arcade mode)
        if self._scanline_overlay is not None:
            self.window.blit(self._scanline_overlay, (0, 0))

        pygame.display.flip()
