"""Main gameplay scene.

Sprint 3: invader grid marching, basic HUD.
Sprint 4: player movement and shooting, invader collision, scoring.
Sprint 5: lives, game-over, round advance.
Sprint 6: enemy fire, bunkers.
Sprint 7: UFO.
Sprint 8: sound wired in.
Sprint 9: Deluxe features.
"""

from __future__ import annotations

import pygame

from .. import constants
from ..assets import AssetManager
from ..entities.bunker import BunkerGroup
from ..entities.grid import InvaderGrid
from ..entities.player import Player
from ..entities.ufo import UFO
from ..hud import HUD
from .base import Scene


class GameScene(Scene):
    def __init__(self, asset_mgr: AssetManager):
        self._assets = asset_mgr
        self.grid = InvaderGrid(asset_mgr)
        self.player = Player(asset_mgr)
        self.ufo = UFO(asset_mgr)
        self.bunkers = BunkerGroup(asset_mgr)
        self.hud = HUD()
        self.score = 0
        self.hi_score = 0

    def update(self, dt: float) -> None:
        self.grid.update(dt)
        # Sprint 4: self.player.update(dt, pygame.key.get_pressed())
        # Sprint 7: self.ufo.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(constants.COLOR_BG)
        self._draw_ground_line(surface)
        # Z-order: bunkers → grid → ufo → player → HUD
        self.bunkers.draw(surface)
        self.grid.draw(surface)
        self.ufo.draw(surface)
        self.player.draw(surface)
        self.hud.draw(surface, self.score, self.hi_score, self.player.lives)

    def handle_event(self, event: pygame.event.Event) -> None:
        pass  # Sprint 4: shooting on SPACE

    # ------------------------------------------------------------------

    def _draw_ground_line(self, surface: pygame.Surface) -> None:
        """Horizontal line separating play area from player lane."""
        pygame.draw.line(
            surface,
            constants.COLOR_GREEN,
            (0, constants.PLAYER_Y + 12),
            (constants.SCREEN_W, constants.PLAYER_Y + 12),
        )
