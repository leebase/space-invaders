"""Inter-round cutscene — Space Invaders Deluxe.

Plays a brief animated sequence between rounds.  Holds a reference to the
already-advanced GameScene and restores it as next_scene when finished.
"""

from __future__ import annotations

import math

import pygame

from .. import constants
from ..assets import AssetManager
from .base import Scene


class CutsceneScene(Scene):
    """Animated inter-round sequence.

    `game_scene` is the GameScene that has already called `_next_round()`.
    When the cutscene finishes it sets `next_scene = game_scene`.

    `round_num` is the NEW round number (displayed as "ROUND N").
    """

    def __init__(
        self,
        asset_mgr: AssetManager,
        game_scene: Scene,
        round_num: int,
    ):
        self._assets = asset_mgr
        self._game_scene = game_scene
        self._round_num = round_num
        self._timer: float = 0.0

        self._font_large = pygame.font.Font(None, 24)
        self._font_small = pygame.font.Font(None, 14)

        # Marching alien animation
        self._frames = [
            asset_mgr.get_sprite_frames("squid"),
            asset_mgr.get_sprite_frames("crab"),
            asset_mgr.get_sprite_frames("octopus"),
        ]
        self._frame_idx: int = 0
        self._frame_timer: float = 0.0
        self._march_x: float = 0.0
        self._march_dir: int = 1

    # ------------------------------------------------------------------
    # Scene interface
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self._timer += dt

        # Animate marching aliens
        self._march_x += 40.0 * self._march_dir * dt
        if self._march_x > constants.SCREEN_W - 30 or self._march_x < 0:
            self._march_dir *= -1

        self._frame_timer += dt
        if self._frame_timer >= 0.3:
            self._frame_timer = 0.0
            self._frame_idx = (self._frame_idx + 1) % 2

        if self._timer >= constants.CUTSCENE_DURATION:
            if self.next_scene is None:  # Only if not already skipped
                self.next_scene = self._game_scene

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(constants.COLOR_BG)

        # "ROUND N" header
        header = self._font_large.render(
            f"ROUND  {self._round_num}", False, constants.COLOR_GREEN
        )
        surface.blit(header, ((constants.SCREEN_W - header.get_width()) // 2, 50))

        # Separator line
        pygame.draw.line(
            surface,
            constants.COLOR_GREEN,
            (10, 70),
            (constants.SCREEN_W - 10, 70),
        )

        # Three rows of marching aliens (one per type)
        x = int(self._march_x)
        for row_idx, frames in enumerate(self._frames):
            y = 90 + row_idx * 22
            sprite = frames[self._frame_idx]
            # Draw a small parade across a partial screen width
            for i in range(5):
                sx = (x + i * 20) % (constants.SCREEN_W - 10)
                surface.blit(sprite, (sx, y))

        # Pulsing "PREPARING..." text
        pulse = 0.5 + 0.5 * math.sin(self._timer * 4)
        alpha = int(180 + 75 * pulse)
        txt = self._font_small.render("PREPARING ROUND...", False, constants.COLOR_CYAN)
        txt_a = txt.copy()
        txt_a.set_alpha(alpha)
        surface.blit(txt_a, ((constants.SCREEN_W - txt.get_width()) // 2, 175))

    def handle_event(self, event: pygame.event.Event) -> None:
        # Any key skips to the end of the cutscene
        if event.type == pygame.KEYDOWN:
            self.next_scene = self._game_scene
