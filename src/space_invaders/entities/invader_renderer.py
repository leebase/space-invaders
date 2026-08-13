"""Invader rendering strategies.

This module implements the Strategy pattern for rendering invaders/avatars.
Two renderers are provided:
- PixelRenderer: Original arcade pixel sprites with color tinting
- AvatarRenderer: Memoji-style procedural avatars with smooth scaling
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

from .. import constants
from ..assets import AssetManager
from ..avatar_config import AvatarConfig
from ..avatar_generator import AvatarGenerator

if TYPE_CHECKING:
    from .grid import InvaderGrid


class InvaderRenderer(ABC):
    """Abstract base class for invader/avatar rendering strategies."""

    @abstractmethod
    def render(self, surface: pygame.Surface, grid: InvaderGrid) -> None:
        """Render the invaders/avatars to the given surface.

        Args:
            surface: The surface to render to (native resolution)
            grid: The invader grid containing positions and state
        """

    @abstractmethod
    def get_cell_size(self) -> tuple[int, int]:
        """Return the cell size (width, height) used by this renderer."""


class PixelRenderer(InvaderRenderer):
    """Original arcade sprite renderer with color tinting.

    Renders pixel-art sprites at 16×16 cell size with color tinting
    based on descent depth.
    """

    def __init__(self, asset_mgr: AssetManager):
        """Initialize with asset manager for sprite access.

        Args:
            asset_mgr: Asset manager for loading sprites
        """
        self._assets = asset_mgr
        self._frames: dict[str, list[pygame.Surface]] = {
            "squid": asset_mgr.get_sprite_frames("squid"),
            "crab": asset_mgr.get_sprite_frames("crab"),
            "octopus": asset_mgr.get_sprite_frames("octopus"),
        }
        # Cache for tinted sprites
        self._tint_cache: dict[tuple, pygame.Surface] = {}

    def render(self, surface: pygame.Surface, grid: InvaderGrid) -> None:
        """Render pixel sprites with color tinting."""

        # Calculate color based on descent
        color = self._descent_color(grid.grid_y)

        for row in range(constants.GRID_ROWS):
            sprite_key = constants.ROW_TYPES[row]
            raw_sprite = self._frames[sprite_key][grid.frame]
            sprite = self._get_tinted(raw_sprite, color)
            sw = sprite.get_width()
            sh = sprite.get_height()

            for col in range(constants.GRID_COLS):
                if not grid.alive[row][col]:
                    continue

                # Centre sprite within its CELL_W × CELL_H slot
                cell_x = grid.grid_x + col * constants.CELL_W
                cell_y = grid.grid_y + row * constants.CELL_H
                blit_x = cell_x + (constants.CELL_W - sw) // 2
                blit_y = cell_y + (constants.CELL_H - sh) // 2
                surface.blit(sprite, (blit_x, blit_y))

    def get_cell_size(self) -> tuple[int, int]:
        """Return arcade mode cell size."""
        return (constants.CELL_W, constants.CELL_H)

    def _descent_color(self, grid_y: int) -> tuple[int, int, int]:
        """Return the band color for the current grid Y position."""
        for min_y, color in constants.DESCENT_COLOR_BANDS:
            if grid_y >= min_y:
                return color
        return constants.COLOR_WHITE

    def _get_tinted(
        self, sprite: pygame.Surface, color: tuple[int, int, int]
    ) -> pygame.Surface:
        """Return a cached copy of sprite with all opaque pixels set to color."""
        import numpy as np

        key = (id(sprite), color)
        if key not in self._tint_cache:
            tinted = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            tinted.fill((*color, 255))
            alpha = np.array(pygame.surfarray.pixels_alpha(sprite))
            pygame.surfarray.pixels_alpha(tinted)[:] = alpha
            self._tint_cache[key] = tinted
        return self._tint_cache[key]


class AvatarRenderer(InvaderRenderer):
    """Memoji-style avatar renderer.

    Renders procedurally generated avatars at 32×32 cell size
    with smooth scaling and bounce animation.
    """

    # Avatar cells are 2x arcade cells
    AVATAR_CELL_W = 32
    AVATAR_CELL_H = 32
    # Generate at 4x cell size for high-quality supersampling, then scale down
    AVATAR_GENERATE_SIZE = 128

    def __init__(self, asset_mgr: AssetManager):
        """Initialize with asset manager and create avatar generator.

        Args:
            asset_mgr: Asset manager (for API compatibility)
        """
        self._config = AvatarConfig()
        self._generator = AvatarGenerator()
        # Generate avatars for all 5 rows at high resolution
        self._avatars: list[pygame.Surface] = []
        for row in range(constants.GRID_ROWS):
            char = self._config.get_character(row)
            # Generate at high res, then scale to cell size
            high_res = self._generator.generate(char, size=self.AVATAR_GENERATE_SIZE)
            avatar = pygame.transform.smoothscale(
                high_res, (self.AVATAR_CELL_W, self.AVATAR_CELL_H)
            )
            self._avatars.append(avatar)
        # Animation phase
        self._bounce_phase: float = 0.0

    def render(self, surface: pygame.Surface, grid: InvaderGrid) -> None:
        """Render avatars with bounce animation."""
        # Update animation phase based on march frame
        self._bounce_phase = grid.frame * 0.5

        for row in range(constants.GRID_ROWS):
            avatar = self._avatars[row]

            for col in range(constants.GRID_COLS):
                if not grid.alive[row][col]:
                    continue

                # Calculate position using Avatar mode cell size
                cell_x = grid.grid_x + col * self.AVATAR_CELL_W
                cell_y = grid.grid_y + row * self.AVATAR_CELL_H

                # Apply bounce animation
                bounce = int(3 * math.sin(self._bounce_phase + col * 0.5))

                # Center avatar in cell (avatar is same size as cell)
                blit_x = cell_x
                blit_y = cell_y + bounce

                surface.blit(avatar, (blit_x, blit_y))

    def get_cell_size(self) -> tuple[int, int]:
        """Return avatar mode cell size (32×32)."""
        return (self.AVATAR_CELL_W, self.AVATAR_CELL_H)
