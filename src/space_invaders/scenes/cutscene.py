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
        screen_w: int = constants.SCREEN_W,
        screen_h: int = constants.SCREEN_H,
    ):
        self._assets = asset_mgr
        self._game_scene = game_scene
        self._round_num = round_num
        self._screen_w = screen_w
        self._screen_h = screen_h
        self._timer: float = 0.0

        # Scale font sizes proportionally to screen size
        w_scale = screen_w // constants.SCREEN_W
        self._font_large = pygame.font.Font(None, 24 * w_scale)
        self._font_small = pygame.font.Font(None, 14 * w_scale)

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
        if self._march_x > self._screen_w - 30 or self._march_x < 0:
            self._march_dir *= -1

        self._frame_timer += dt
        if self._frame_timer >= 0.3:
            self._frame_timer = 0.0
            self._frame_idx = (self._frame_idx + 1) % 2

        if self._timer >= constants.CUTSCENE_DURATION:
            if self.next_scene is None:  # Only if not already skipped
                self.next_scene = self._game_scene

    def draw(self, surface: pygame.Surface) -> None:
        sw = self._screen_w
        sh = self._screen_h
        surface.fill(constants.COLOR_BG)

        # "ROUND N" header
        header = self._font_large.render(
            f"ROUND  {self._round_num}", False, constants.COLOR_GREEN
        )
        header_y = sh * 50 // 256
        surface.blit(header, ((sw - header.get_width()) // 2, header_y))

        # Separator line
        sep_y = sh * 70 // 256
        pygame.draw.line(
            surface,
            constants.COLOR_GREEN,
            (sw * 10 // 224, sep_y),
            (sw - sw * 10 // 224, sep_y),
        )

        # Three rows of marching aliens (one per type)
        x = int(self._march_x)
        for row_idx, frames in enumerate(self._frames):
            y = sh * (90 + row_idx * 22) // 256
            sprite = frames[self._frame_idx]
            # Scale sprite for non-arcade screens
            if sw != constants.SCREEN_W:
                sprite_scale = sw // constants.SCREEN_W
                sprite = pygame.transform.scale(
                    sprite,
                    (sprite.get_width() * sprite_scale, sprite.get_height() * sprite_scale),
                )
            spacing = sw * 20 // 224
            modulo = sw - sw * 10 // 224
            for i in range(5):
                sx = (x + i * spacing) % modulo
                surface.blit(sprite, (sx, y))

        # Pulsing "PREPARING..." text
        pulse = 0.5 + 0.5 * math.sin(self._timer * 4)
        alpha = int(180 + 75 * pulse)
        txt = self._font_small.render("PREPARING ROUND...", False, constants.COLOR_CYAN)
        txt_a = txt.copy()
        txt_a.set_alpha(alpha)
        txt_y = sh * 175 // 256
        surface.blit(txt_a, ((sw - txt.get_width()) // 2, txt_y))

    def handle_event(self, event: pygame.event.Event) -> None:
        # Any key skips to the end of the cutscene
        if event.type == pygame.KEYDOWN:
            self.next_scene = self._game_scene
