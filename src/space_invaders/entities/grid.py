"""Invader grid — 5×11 march, animation, and (later) fire logic.

Sprint 3: march + animation, visual only.
Sprint 4: per-invader hit detection, scoring.
Sprint 6: enemy fire.
Sprint 9: splitting aliens, rainbow bonus, color-on-descent.
"""

from __future__ import annotations

import random

import pygame

from .. import constants
from ..assets import AssetManager
from .bullet import Bullet


def march_interval_ms(remaining: int) -> float:
    """Return the milliseconds between march steps for the given invader count.

    Linear interpolation: 55 invaders → MARCH_MAX_MS, 1 invader → MARCH_MIN_MS.
    """
    if remaining <= 1:
        return constants.MARCH_MIN_MS
    t = (remaining - 1) / (constants.GRID_ROWS * constants.GRID_COLS - 1)
    return constants.MARCH_MIN_MS + t * (
        constants.MARCH_MAX_MS - constants.MARCH_MIN_MS
    )


def _fire_interval_ms(remaining: int) -> float:
    """Return the ms between enemy fire attempts for the given invader count."""
    if remaining <= 1:
        return constants.ENEMY_FIRE_MIN_MS
    t = (remaining - 1) / (constants.GRID_ROWS * constants.GRID_COLS - 1)
    return constants.ENEMY_FIRE_MIN_MS + t * (
        constants.ENEMY_FIRE_MAX_MS - constants.ENEMY_FIRE_MIN_MS
    )


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
        self._fire_timer_ms: float = 0.0
        # New bullets produced this tick; GameScene drains and adopts them.
        self.pending_bullets: list[Bullet] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        self.march_timer_ms += dt * 1000.0
        interval = march_interval_ms(self.total_alive)
        while self.march_timer_ms >= interval:
            self.march_timer_ms -= interval
            self._march_step()
            interval = march_interval_ms(self.total_alive)  # recompute after each step

        # Enemy fire
        self._fire_timer_ms += dt * 1000.0
        fire_interval = _fire_interval_ms(self.total_alive)
        if self._fire_timer_ms >= fire_interval:
            self._fire_timer_ms = 0.0
            b = self._try_fire()
            if b is not None:
                self.pending_bullets.append(b)

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
        """Y position (bottom edge) of the lowest living invader.

        Used for game-over check.
        """
        for row in range(constants.GRID_ROWS - 1, -1, -1):
            if any(self.alive[row]):
                return self.grid_y + row * constants.CELL_H + constants.SPRITE_H
        return 0

    def invader_at(self, px: int, py: int) -> tuple[int, int] | None:
        """Return (row, col) of the invader whose sprite contains pixel (px, py).

        Returns None if no invader occupies that point.
        """
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
    # Internal fire mechanics
    # ------------------------------------------------------------------

    def _try_fire(self) -> Bullet | None:
        """Select a random column and fire from its lowest alive invader."""
        alive_cols = [
            col for col in range(constants.GRID_COLS)
            if any(self.alive[row][col] for row in range(constants.GRID_ROWS))
        ]
        if not alive_cols:
            return None
        col = random.choice(alive_cols)
        row = None
        for r in range(constants.GRID_ROWS - 1, -1, -1):
            if self.alive[r][col]:
                row = r
                break
        if row is None:
            return None
        sprite_key = constants.ROW_TYPES[row]
        sw = self._frames[sprite_key][0].get_width()
        cw = constants.CELL_W
        cell_x = self.grid_x + col * cw
        cell_y = self.grid_y + row * constants.CELL_H
        blit_x = cell_x + (cw - sw) // 2
        blit_y = cell_y + (constants.CELL_H - constants.SPRITE_H) // 2
        bx = blit_x + sw // 2 - Bullet.WIDTH // 2
        by = blit_y + constants.SPRITE_H
        return Bullet(bx, by, constants.ENEMY_BULLET_SPEED)

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

        sprite_w_left = self._max_sprite_w_in_col(left_col)
        sprite_w_right = self._max_sprite_w_in_col(right_col)

        # Account for centering: blit_x = cell_x + (CELL_W - sw) // 2
        cw = constants.CELL_W
        left_edge = self.grid_x + left_col * cw + (cw - sprite_w_left) // 2
        right_edge = self.grid_x + right_col * cw + (cw + sprite_w_right) // 2

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

    def _max_sprite_w_in_col(self, col: int) -> int:
        """Return the widest sprite width among all alive rows in this column."""
        w = 0
        for row in range(constants.GRID_ROWS):
            if self.alive[row][col]:
                key = constants.ROW_TYPES[row]
                w = max(w, self._frames[key][0].get_width())
        return w if w else constants.MAX_SPRITE_W

    # ------------------------------------------------------------------
    # Sprite loading
    # ------------------------------------------------------------------

    def _load_sprites(self, asset_mgr: AssetManager) -> None:
        self._frames: dict[str, list[pygame.Surface]] = {
            "squid":   asset_mgr.get_sprite_frames("squid"),
            "crab":    asset_mgr.get_sprite_frames("crab"),
            "octopus": asset_mgr.get_sprite_frames("octopus"),
        }
