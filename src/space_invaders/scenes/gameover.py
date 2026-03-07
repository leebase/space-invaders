"""Game over screen. Implemented in Sprint 5 (basic). Sprint 10 adds initials."""

from __future__ import annotations

from typing import Callable

import pygame

from .. import constants
from ..assets import AssetManager
from .base import Scene


class GameOverScene(Scene):
    """Game over scene with high score initials entry.

    State machine:
    - ENTERING_INITIALS (if new high score) -> PRESS_KEY -> restart
    - PRESS_KEY (if not high score) -> restart
    """

    # Valid characters for initials: A-Z, 0-9
    _CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def __init__(
        self,
        asset_mgr: AssetManager,
        final_score: int = 0,
        hi_score: int = 0,
        on_restart: Callable[[], Scene] | None = None,
    ):
        self._assets = asset_mgr
        self._font = pygame.font.Font(None, 16)
        self._font_large = pygame.font.Font(None, 24)
        self.final_score = final_score
        self.hi_score = hi_score
        self._on_restart = on_restart

        # State tracking
        self._is_new_high_score = final_score >= hi_score and final_score > 0
        self._state: str = (
            "ENTERING_INITIALS" if self._is_new_high_score else "PRESS_KEY"
        )

        # Initials entry state (only used if _is_new_high_score)
        self.initials = ["A", "A", "A"]  # 3 characters
        self._cursor_pos = 0  # 0, 1, or 2
        self._cursor_visible = True
        self._cursor_blink_timer = 0.0
        self._cursor_blink_interval = 0.25  # 2 Hz = toggle every 0.25s (half period)

    def update(self, dt: float) -> None:
        """Update cursor blink animation."""
        if self._state == "ENTERING_INITIALS":
            self._cursor_blink_timer += dt
            if self._cursor_blink_timer >= self._cursor_blink_interval:
                self._cursor_blink_timer = 0.0
                self._cursor_visible = not self._cursor_visible

    def draw(self, surface: pygame.Surface) -> None:
        """Render the game over screen."""
        surface.fill(constants.COLOR_BG)

        # Determine which score is the best to display
        best_score = max(self.final_score, self.hi_score)

        # Main "GAME OVER" title (large font)
        title_surf = self._font_large.render("GAME OVER", False, constants.COLOR_RED)
        title_x = (constants.SCREEN_W - title_surf.get_width()) // 2
        surface.blit(title_surf, (title_x, 80))

        # Score display
        score_surf = self._font.render(
            f"SCORE  {self.final_score:05d}", False, constants.COLOR_GREEN
        )
        score_x = (constants.SCREEN_W - score_surf.get_width()) // 2
        surface.blit(score_surf, (score_x, 110))

        # Best score display
        best_surf = self._font.render(
            f"BEST   {best_score:05d}", False, constants.COLOR_CYAN
        )
        best_x = (constants.SCREEN_W - best_surf.get_width()) // 2
        surface.blit(best_surf, (best_x, 126))

        if self._state == "ENTERING_INITIALS":
            self._draw_initials_entry(surface)
        elif self._state == "PRESS_KEY":
            # Show "PRESS ANY KEY TO RESTART"
            prompt_surf = self._font.render(
                "PRESS ANY KEY TO RESTART", False, constants.COLOR_WHITE
            )
            prompt_x = (constants.SCREEN_W - prompt_surf.get_width()) // 2
            surface.blit(prompt_surf, (prompt_x, 170))

    def _draw_initials_entry(self, surface: pygame.Surface) -> None:
        """Draw the initials entry UI with blinking cursor."""
        # "NEW HIGH SCORE!" message
        new_hs_surf = self._font.render(
            "NEW HIGH SCORE!", False, constants.COLOR_YELLOW
        )
        new_hs_x = (constants.SCREEN_W - new_hs_surf.get_width()) // 2
        surface.blit(new_hs_surf, (new_hs_x, 150))

        # Build initials display with cursor underline
        # Format: "A_B_C" where _ is the cursor position (blinking)
        char_spacing = 20  # Pixels between character centers
        start_x = (constants.SCREEN_W - (2 * char_spacing)) // 2  # Center the 3 chars
        base_y = 175

        for i, char in enumerate(self.initials):
            x = start_x + i * char_spacing

            # Draw the character
            char_surf = self._font.render(char, False, constants.COLOR_WHITE)
            char_x = x - char_surf.get_width() // 2
            surface.blit(char_surf, (char_x, base_y))

            # Draw cursor underline if this is the current position and visible
            if i == self._cursor_pos and self._cursor_visible:
                # Draw underline (a short horizontal line)
                line_y = base_y + char_surf.get_height() + 2
                pygame.draw.line(
                    surface,
                    constants.COLOR_WHITE,
                    (x - 6, line_y),
                    (x + 6, line_y),
                    2,
                )

        # Instructions
        instr_surf = self._font.render(
            "UP/DOWN: CHANGE  LEFT/RIGHT: MOVE", False, constants.COLOR_WHITE
        )
        instr_x = (constants.SCREEN_W - instr_surf.get_width()) // 2
        surface.blit(instr_surf, (instr_x, 205))

        confirm_surf = self._font.render(
            "ENTER/SPACE: CONFIRM", False, constants.COLOR_WHITE
        )
        confirm_x = (constants.SCREEN_W - confirm_surf.get_width()) // 2
        surface.blit(confirm_surf, (confirm_x, 220))

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input for initials entry or restart."""
        if event.type != pygame.KEYDOWN:
            return

        if self._state == "ENTERING_INITIALS":
            self._handle_initials_input(event.key)
        elif self._state == "PRESS_KEY":
            # Any key restarts the game
            self._restart_game()

    def _handle_initials_input(self, key: int) -> None:
        """Handle input during initials entry state."""
        if key == pygame.K_RETURN or key == pygame.K_SPACE:
            # Confirm initials and move to PRESS_KEY state
            self._state = "PRESS_KEY"
            return

        if key == pygame.K_LEFT:
            # Move cursor left
            self._cursor_pos = max(0, self._cursor_pos - 1)
            self._cursor_visible = True
            self._cursor_blink_timer = 0.0
            return

        if key == pygame.K_RIGHT:
            # Move cursor right
            self._cursor_pos = min(2, self._cursor_pos + 1)
            self._cursor_visible = True
            self._cursor_blink_timer = 0.0
            return

        if key == pygame.K_UP:
            # Change character at cursor position (next character)
            self._cycle_char(self._cursor_pos, 1)
            return

        if key == pygame.K_DOWN:
            # Change character at cursor position (previous character)
            self._cycle_char(self._cursor_pos, -1)
            return

    def _cycle_char(self, position: int, direction: int) -> None:
        """Cycle the character at the given position up or down."""
        current_char = self.initials[position]
        current_index = self._CHARS.index(current_char)
        new_index = (current_index + direction) % len(self._CHARS)
        self.initials[position] = self._CHARS[new_index]

    def _restart_game(self) -> None:
        """Transition to the game scene."""
        if self._on_restart:
            self.next_scene = self._on_restart()
        else:
            from .game import GameScene

            self.next_scene = GameScene(self._assets, hi_score=self.hi_score)
