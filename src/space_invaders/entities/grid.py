"""Invader grid — 5×11 march, animation, and (later) fire logic.

Sprint 3: march + animation, visual only.
Sprint 4: per-invader hit detection, scoring.
Sprint 6: enemy fire.
Sprint 9: splitting aliens, rainbow bonus, color-on-descent.
"""

from __future__ import annotations

import pygame
from ..assets import AssetManager
from .. import constants


def march_interval_ms(remaining: int) -> float:
    """Return the milliseconds between march steps for the given invader count.

    Linear interpolation: 55 invaders → MARCH_MAX_MS, 1 invader → MARCH_MIN_MS.
    """
    if remaining <= 1:
        return constants.MARCH_MIN_MS
    t = (remaining - 1) / (constants.GRID_ROWS * constants.GRID_COLS - 1)
    return constants.MARCH_MIN_MS + t * (constants.MARCH_MAX_MS - constants.MARCH_MIN_MS)


class InvaderGrid:
    """The 5×11 grid of invaders.

    State
    -----
    alive[row][col] : bool — whether that invader is still alive
    grid_x          : int  — x of left edge of column 0 (native pixels)
    grid_y          : int  — y of top edge of row 0 (native pixels)
    direction       : int  — +1 = moving right, -1 = moving left
    frame           : int  — animation frame index (0 or 1), advances each march step
    march_timer_ms  : float — accumulated time since last step (milliseconds)
    """

    def __init__(self, asset_mgr: AssetManager):
        self._load_sprites(asset_mgr)

        self.alive: list[list[bool]] = [
            [True] * constants.GRID_COLS for _ in range(constants.GRID_ROWS)
        ]
        self.grid_x: int = constants.GRID_START_X
        self.grid_y: int = constants.GRID_START_Y
        self.direction: int = 1          # start moving right
        self.frame: int = 0
        self.march_timer_ms: float = 0.0
        self.total_alive: int = constants.GRID_ROWS * constants.GRID_COLS

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self.march_timer_ms += dt * 1000.0
        interval = march_interval_ms(self.total_alive)
        if self.march_timer_ms >= interval:
            self.march_timer_ms -= interval
            self._march_step()

    def draw(self, surface: pygame.Surface) -> None:
        for row in range(constants.GRID_ROWS):
            sprite_key = constants.ROW_TYPES[row]
            sprite = self._frames[sprite_key][self.frame]
            sw = sprite.get_width()
            sh = sprite.get_height()
            for col in range(constants.GRID_COLS):
                if not self.alive[row][col]:
                    continue
                # Centre sprite within its CELL_W × CELL_H slot
                cell_x = self.grid_x + col * constants.CELL_W
                cell_y = self.grid_y + row * constants.CELL_H
                blit_x = cell_x + (constants.CELL_W - sw) // 2
                blit_y = cell_y + (constants.CELL_H - sh) // 2
                surface.blit(sprite, (blit_x, blit_y))

    def kill(self, row: int, col: int) -> int:
        """Mark an invader dead. Returns its point value.

        Called by Sprint 4 collision logic.
        """
        if not self.alive[row][col]:
            return 0
        self.alive[row][col] = False
        self.total_alive -= 1
        return constants.ROW_SCORES[row]

    def is_cleared(self) -> bool:
        return self.total_alive == 0

    def lowest_row_y(self) -> int:
        """Y position (bottom edge) of the lowest living invader. Used for game-over check."""
        for row in range(constants.GRID_ROWS - 1, -1, -1):
            if any(self.alive[row]):
                return self.grid_y + row * constants.CELL_H + constants.SPRITE_H
        return 0

    def invader_at(self, px: int, py: int) -> tuple[int, int] | None:
        """Return (row, col) of the invader whose sprite contains pixel (px, py), or None."""
        for row in range(constants.GRID_ROWS):
            sprite_key = constants.ROW_TYPES[row]
            sw = self._frames[sprite_key][0].get_width()
            sh = constants.SPRITE_H
            for col in range(constants.GRID_COLS):
                if not self.alive[row][col]:
                    continue
                cell_x = self.grid_x + col * constants.CELL_W
                cell_y = self.grid_y + row * constants.CELL_H
                blit_x = cell_x + (constants.CELL_W - sw) // 2
                blit_y = cell_y + (constants.CELL_H - sh) // 2
                if blit_x <= px < blit_x + sw and blit_y <= py < blit_y + sh:
                    return (row, col)
        return None

    # ------------------------------------------------------------------
    # Internal march mechanics
    # ------------------------------------------------------------------

    def _march_step(self) -> None:
        # Advance animation frame
        self.frame = (self.frame + 1) % 2

        # Move horizontally
        self.grid_x += self.direction * constants.MARCH_STEP_X

        # Check boundary using the leftmost and rightmost living columns
        left_col = self._leftmost_alive_col()
        right_col = self._rightmost_alive_col()

        if left_col is None:
            return  # no living invaders

        sprite_w_right = self._frames[constants.ROW_TYPES[self._topmost_alive_row_in_col(right_col)]][0].get_width()

        left_edge = self.grid_x + left_col * constants.CELL_W
        right_edge = self.grid_x + right_col * constants.CELL_W + sprite_w_right

        if self.direction == 1 and right_edge >= constants.RIGHT_LIMIT:
            self.direction = -1
            self.grid_y += constants.MARCH_STEP_Y
        elif self.direction == -1 and left_edge <= constants.LEFT_LIMIT:
            self.direction = 1
            self.grid_y += constants.MARCH_STEP_Y

    def _leftmost_alive_col(self) -> int | None:
        for col in range(constants.GRID_COLS):
            if any(self.alive[row][col] for row in range(constants.GRID_ROWS)):
                return col
        return None

    def _rightmost_alive_col(self) -> int | None:
        for col in range(constants.GRID_COLS - 1, -1, -1):
            if any(self.alive[row][col] for row in range(constants.GRID_ROWS)):
                return col
        return None

    def _topmost_alive_row_in_col(self, col: int) -> int:
        for row in range(constants.GRID_ROWS):
            if self.alive[row][col]:
                return row
        return 0

    # ------------------------------------------------------------------
    # Sprite loading
    # ------------------------------------------------------------------

    def _load_sprites(self, asset_mgr: AssetManager) -> None:
        self._frames: dict[str, list[pygame.Surface]] = {
            "squid":   asset_mgr.get_sprite_frames("squid"),
            "crab":    asset_mgr.get_sprite_frames("crab"),
            "octopus": asset_mgr.get_sprite_frames("octopus"),
        }
