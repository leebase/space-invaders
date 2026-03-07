"""Title / attract screen. Implemented in Sprint 10."""

from __future__ import annotations

import math

import pygame

from .. import constants
from ..assets import AssetManager
from .base import Scene


class TitleScene(Scene):
    """Attract screen with animated invader parade and high score display.

    Transitions to GameScene on any key press.
    """

    def __init__(self, asset_mgr: AssetManager, hi_score: int = 0):
        self._assets = asset_mgr
        self._hi_score = hi_score
        self._timer: float = 0.0

        # Fonts for different text elements
        self._font_title = pygame.font.Font(None, 24)
        self._font_prompt = pygame.font.Font(None, 16)
        self._font_score = pygame.font.Font(None, 14)

        # Marching alien animation (3 rows: squid, crab, octopus)
        self._frames = [
            asset_mgr.get_sprite_frames("squid"),
            asset_mgr.get_sprite_frames("crab"),
            asset_mgr.get_sprite_frames("octopus"),
        ]
        self._frame_idx: int = 0
        self._frame_timer: float = 0.0

        # Marching parade state
        self._march_x: float = 0.0
        self._march_dir: int = 1

    # ------------------------------------------------------------------
    # Scene interface
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self._timer += dt

        # Animate marching aliens slowly (20px/s)
        self._march_x += 20.0 * self._march_dir * dt
        if self._march_x > constants.SCREEN_W - 100 or self._march_x < 0:
            self._march_dir *= -1

        # Advance animation frame every 0.5s
        self._frame_timer += dt
        if self._frame_timer >= 0.5:
            self._frame_timer = 0.0
            self._frame_idx = (self._frame_idx + 1) % 2

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(constants.COLOR_BG)

        # "SPACE INVADERS DELUXE" title at top
        title = self._font_title.render(
            "SPACE INVADERS DELUXE", False, constants.COLOR_WHITE
        )
        title_x = (constants.SCREEN_W - title.get_width()) // 2
        surface.blit(title, (title_x, 40))

        # Separator line under title
        pygame.draw.line(
            surface,
            constants.COLOR_GREEN,
            (20, 70),
            (constants.SCREEN_W - 20, 70),
        )

        # High score display
        hi_score_text = self._font_score.render(
            f"HI-SCORE  {self._hi_score:05d}", False, constants.COLOR_CYAN
        )
        hi_score_x = (constants.SCREEN_W - hi_score_text.get_width()) // 2
        surface.blit(hi_score_text, (hi_score_x, 85))

        # Three rows of marching aliens (animated parade)
        x = int(self._march_x)
        for row_idx, frames in enumerate(self._frames):
            y = 110 + row_idx * 22
            sprite = frames[self._frame_idx]
            # Draw a parade of 6 aliens per row across the screen
            for i in range(6):
                sx = (x + i * 25) % (constants.SCREEN_W - 20)
                surface.blit(sprite, (sx + 10, y))

        # Blinking "PRESS ANY KEY TO START" prompt (1 Hz pulse)
        # Use sin wave for smooth pulsing: period = 2π, so 1 Hz = sin(timer * 2π)
        pulse = 0.5 + 0.5 * math.sin(self._timer * 2 * math.pi)
        alpha = int(100 + 155 * pulse)  # Range from 100 to 255

        prompt = self._font_prompt.render(
            "PRESS ANY KEY TO START", False, constants.COLOR_YELLOW
        )
        prompt_x = (constants.SCREEN_W - prompt.get_width()) // 2
        prompt_y = 200

        # Create a copy with alpha for blinking effect
        prompt_alpha = prompt.copy()
        prompt_alpha.set_alpha(alpha)
        surface.blit(prompt_alpha, (prompt_x, prompt_y))

    def handle_event(self, event: pygame.event.Event) -> None:
        # Any key transitions to GameScene
        if event.type == pygame.KEYDOWN:
            from .game import GameScene
            self.next_scene = GameScene(self._assets, hi_score=self._hi_score)
