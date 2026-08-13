"""Title / attract screen with mode selector. Implemented in Sprint 10/12."""

from __future__ import annotations

import math

import pygame

from .. import constants
from ..assets import AssetManager
from ..mode import GameMode, ModeConfig
from .base import Scene


class TitleScene(Scene):
    """Attract screen with animated invader parade, high score display,
    and game mode selector.

    Transitions to GameScene when user selects a mode and presses START.
    """

    def __init__(self, asset_mgr: AssetManager, hi_score: int = 0):
        self._assets = asset_mgr
        self._hi_score = hi_score
        self._timer: float = 0.0

        # Fonts for different text elements
        self._font_title = pygame.font.Font(None, 24)
        self._font_prompt = pygame.font.Font(None, 16)
        self._font_score = pygame.font.Font(None, 14)
        self._font_menu = pygame.font.Font(None, 14)

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

        # Mode selection state
        self._selected_mode: int = 0  # 0 = ARCADE, 1 = AVATAR
        self._modes = [GameMode.ARCADE, GameMode.AVATAR]
        self._mode_names = ["ARCADE MODE", "AVATAR MODE"]

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
        surface.blit(title, (title_x, 30))

        # Separator line under title
        pygame.draw.line(
            surface,
            constants.COLOR_GREEN,
            (20, 55),
            (constants.SCREEN_W - 20, 55),
        )

        # High score display
        hi_score_text = self._font_score.render(
            f"HI-SCORE  {self._hi_score:05d}", False, constants.COLOR_CYAN
        )
        hi_score_x = (constants.SCREEN_W - hi_score_text.get_width()) // 2
        surface.blit(hi_score_text, (hi_score_x, 65))

        # Three rows of marching aliens (animated parade)
        x = int(self._march_x)
        for row_idx, frames in enumerate(self._frames):
            y = 90 + row_idx * 20
            sprite = frames[self._frame_idx]
            # Draw a parade of 6 aliens per row across the screen
            for i in range(6):
                sx = (x + i * 25) % (constants.SCREEN_W - 20)
                surface.blit(sprite, (sx + 10, y))

        # Mode selector menu
        menu_y = 160
        menu_spacing = 18

        for i, mode_name in enumerate(self._mode_names):
            y = menu_y + i * menu_spacing

            # Highlight selected mode with arrow and different color
            if i == self._selected_mode:
                color = constants.COLOR_YELLOW
                prefix = "> "
            else:
                color = constants.COLOR_WHITE
                prefix = "  "

            text = self._font_menu.render(prefix + mode_name, False, color)
            text_x = (constants.SCREEN_W - text.get_width()) // 2
            surface.blit(text, (text_x, y))

        # Instructions at bottom
        instr_text = self._font_prompt.render(
            "UP/DOWN: SELECT  ENTER: START", False, constants.COLOR_GREEN
        )
        instr_x = (constants.SCREEN_W - instr_text.get_width()) // 2
        surface.blit(instr_text, (instr_x, 220))

        # Blinking "PRESS ENTER TO START" prompt for selected mode
        pulse = 0.5 + 0.5 * math.sin(self._timer * 2 * math.pi)
        alpha = int(100 + 155 * pulse)

        prompt = self._font_prompt.render("PRESS ENTER", False, constants.COLOR_YELLOW)
        prompt_x = (constants.SCREEN_W - prompt.get_width()) // 2
        prompt_y = 235

        prompt_alpha = prompt.copy()
        prompt_alpha.set_alpha(alpha)
        surface.blit(prompt_alpha, (prompt_x, prompt_y))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        # Mode selection
        if event.key == pygame.K_UP:
            self._selected_mode = (self._selected_mode - 1) % len(self._modes)
        elif event.key == pygame.K_DOWN:
            self._selected_mode = (self._selected_mode + 1) % len(self._modes)

        # Start game with selected mode
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            from .game import GameScene

            selected_mode = self._modes[self._selected_mode]
            mode_config = ModeConfig(selected_mode)

            self.next_scene = GameScene(
                self._assets,
                hi_score=self._hi_score,
                mode_config=mode_config
            )
