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

import enum

import pygame

from .. import constants
from ..assets import AssetManager
from ..entities.bunker import BunkerGroup
from ..entities.grid import InvaderGrid
from ..entities.player import Player
from ..entities.ufo import UFO
from ..hud import HUD
from .base import Scene


class _State(enum.Enum):
    PLAYING = "playing"
    PLAYER_DEAD = "player_dead"   # respawn countdown active
    ROUND_CLEAR = "round_clear"   # brief pause before next round


class GameScene(Scene):
    def __init__(self, asset_mgr: AssetManager, hi_score: int = 0):
        self._assets = asset_mgr
        self.grid = InvaderGrid(asset_mgr)
        self.player = Player(asset_mgr)
        self.ufo = UFO(asset_mgr)
        self.bunkers = BunkerGroup(asset_mgr)
        self.hud = HUD()
        self.score = 0
        self.hi_score = hi_score
        self._round = 1
        self._state = _State.PLAYING
        self._state_timer = 0.0

    # ------------------------------------------------------------------
    # Scene interface
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        # Invaders reaching the player row = immediate game over
        if self.grid.lowest_row_y() >= constants.INVADER_KILL_LINE:
            self._trigger_game_over()
            return

        if self._state == _State.PLAYING:
            self.grid.update(dt)
            self.player.update(dt, pygame.key.get_pressed())
            self._check_bullet_collision()
            if self.grid.is_cleared():
                self._state = _State.ROUND_CLEAR
                self._state_timer = 0.0

        elif self._state == _State.ROUND_CLEAR:
            self._state_timer += dt
            if self._state_timer >= constants.ROUND_CLEAR_DELAY:
                self._next_round()

        elif self._state == _State.PLAYER_DEAD:
            self._state_timer += dt
            if self._state_timer >= constants.RESPAWN_DELAY:
                if self.player.lives <= 0:
                    self._trigger_game_over()
                else:
                    self._respawn_player()

        # Sprint 7: self.ufo.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(constants.COLOR_BG)
        self._draw_ground_line(surface)
        # Z-order: bunkers → grid → ufo → player (+ bullet) → HUD
        self.bunkers.draw(surface)
        self.grid.draw(surface)
        self.ufo.draw(surface)
        if self._state != _State.PLAYER_DEAD:
            self.player.draw(surface)
        self.hud.draw(surface, self.score, self.hi_score, self.player.lives)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._state == _State.PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.fire()

    # ------------------------------------------------------------------
    # Public: called by collision systems (Sprint 6 enemy fire → here)
    # ------------------------------------------------------------------

    def kill_player(self) -> None:
        """Decrement a life and enter the respawn countdown."""
        self.player.lives -= 1
        self.player.bullet = None
        self._state = _State.PLAYER_DEAD
        self._state_timer = 0.0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_bullet_collision(self) -> None:
        b = self.player.bullet
        if b is None or not b.alive:
            return
        hit = self.grid.invader_at(b.rect.centerx, b.rect.top)
        if hit is not None:
            row, col = hit
            pts = self.grid.kill(row, col)
            self.score = min(self.score + pts, constants.HIGH_SCORE_MAX)
            self.hi_score = max(self.hi_score, self.score)
            b.alive = False
            self.player.bullet = None

    def _next_round(self) -> None:
        self._round += 1
        self.grid = InvaderGrid(self._assets)
        self.player.bullet = None
        self._state = _State.PLAYING
        self._state_timer = 0.0

    def _respawn_player(self) -> None:
        self.player.reset_position()
        self._state = _State.PLAYING
        self._state_timer = 0.0

    def _trigger_game_over(self) -> None:
        from .gameover import GameOverScene
        self.next_scene = GameOverScene(
            self._assets, self.score, self.hi_score
        )

    def _draw_ground_line(self, surface: pygame.Surface) -> None:
        """Horizontal line separating play area from player lane."""
        pygame.draw.line(
            surface,
            constants.COLOR_GREEN,
            (0, constants.PLAYER_Y + 12),
            (constants.SCREEN_W, constants.PLAYER_Y + 12),
        )
