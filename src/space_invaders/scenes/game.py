"""Main gameplay scene.

Sprint 3: invader grid marching, basic HUD.
Sprint 4: player movement and shooting, invader collision, scoring.
Sprint 5: lives, game-over, round advance.
Sprint 6: enemy fire, bunker pixel destruction, player hit detection.
Sprint 7: UFO.
Sprint 8: sound wired in.
Sprint 9: Deluxe features (split alien, rainbow bonus, descent color, cutscene).
"""

from __future__ import annotations

import enum

import pygame

from .. import constants
from ..assets import AssetManager
from ..entities.bullet import Bullet
from ..entities.bunker import BunkerGroup
from ..entities.grid import InvaderGrid
from ..entities.player import Player
from ..entities.split_alien import SplitAlien, SplitPiece
from ..entities.ufo import UFO
from ..hud import HUD
from ..sound import SoundManager
from .base import Scene


class _State(enum.Enum):
    PLAYING = "playing"
    PLAYER_DEAD = "player_dead"   # respawn countdown active
    ROUND_CLEAR = "round_clear"   # brief pause before cutscene
    PAUSED = "paused"             # gameplay paused


class GameScene(Scene):
    def __init__(self, asset_mgr: AssetManager, hi_score: int = 0):
        self._assets = asset_mgr
        self.grid = InvaderGrid(asset_mgr)
        self.player = Player(asset_mgr)
        self.ufo = UFO(asset_mgr)
        self.split_alien = SplitAlien(asset_mgr)
        self.bunkers = BunkerGroup(asset_mgr)
        self.hud = HUD()
        self.sound = SoundManager(asset_mgr)
        self.score = 0
        self.hi_score = hi_score
        self._round = 1
        self._state = _State.PLAYING
        self._state_timer = 0.0
        self.enemy_bullets: list[Bullet] = []
        self.split_pieces: list[SplitPiece] = []
        self._ufo_was_active: bool = False

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

            # Adopt new bullets fired by the grid (cap at ENEMY_BULLET_MAX)
            for b in self.grid.pending_bullets:
                if len(self.enemy_bullets) < constants.ENEMY_BULLET_MAX:
                    self.enemy_bullets.append(b)
            self.grid.pending_bullets.clear()

            # Advance enemy bullets
            for b in self.enemy_bullets:
                b.update(dt)

            # Advance split pieces
            for p in self.split_pieces:
                p.update(dt)
            self.split_pieces = [p for p in self.split_pieces if p.alive]

            self.player.update(dt, pygame.key.get_pressed())
            self._check_player_bullet_collisions()
            self._check_enemy_bullet_collisions()

            # Filter dead bullets after all collision checks this frame
            self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

            # UFO — track transitions for drone sound
            ufo_was_active = self._ufo_was_active
            self.ufo.update(dt)
            self._ufo_was_active = self.ufo.active
            if self.ufo.active and not ufo_was_active:
                self.sound.start_ufo_drone()
            elif not self.ufo.active and ufo_was_active:
                self.sound.stop_ufo_drone()

            self.split_alien.update(dt)

            self.sound.update(dt, self.grid.total_alive)

            if self.grid.is_cleared():
                self.enemy_bullets.clear()
                self.player.bullet = None
                self._state = _State.ROUND_CLEAR
                self._state_timer = 0.0

        elif self._state == _State.ROUND_CLEAR:
            self._state_timer += dt
            if self._state_timer >= constants.ROUND_CLEAR_DELAY:
                self._to_cutscene()

        elif self._state == _State.PLAYER_DEAD:
            self._state_timer += dt
            if self._state_timer >= constants.RESPAWN_DELAY:
                if self.player.lives <= 0:
                    self._trigger_game_over()
                else:
                    self._respawn_player()

        # PAUSED: no game logic updates (everything frozen)
        elif self._state == _State.PAUSED:
            pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(constants.COLOR_BG)
        self._draw_ground_line(surface)
        # Z-order: bunkers → grid → enemy bullets → split pieces → split alien
        #          → ufo → player (+ bullet) → HUD
        self.bunkers.draw(surface)
        self.grid.draw(surface)
        for b in self.enemy_bullets:
            b.draw(surface)
        for p in self.split_pieces:
            p.draw(surface)
        self.split_alien.draw(surface)
        self.ufo.draw(surface)
        if self._state != _State.PLAYER_DEAD:
            self.player.draw(surface)
        self.hud.draw(surface, self.score, self.hi_score, self.player.lives)

        # Draw pause overlay when paused
        if self._state == _State.PAUSED:
            self._draw_pause_overlay(surface)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self.sound.toggle_mute()

        # Pause toggle: only during PLAYING state
        if self._state == _State.PLAYING:
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_p, pygame.K_ESCAPE
            ):
                self._state = _State.PAUSED
                self.sound.stop_ufo_drone()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.player.fire() is not None:
                    self.sound.play("shoot")

        # Resume from pause
        if self._state == _State.PAUSED:
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_p, pygame.K_ESCAPE
            ):
                self._state = _State.PLAYING
                return

    # ------------------------------------------------------------------
    # Public: called by collision systems
    # ------------------------------------------------------------------

    def kill_player(self) -> None:
        """Decrement a life, clear the field, and enter the respawn countdown."""
        self.sound.play("player_death")
        self.sound.stop_ufo_drone()
        self._ufo_was_active = False
        self.player.lives -= 1
        self.player.bullet = None
        self.enemy_bullets.clear()
        self._state = _State.PLAYER_DEAD
        self._state_timer = 0.0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_player_bullet_collisions(self) -> None:
        b = self.player.bullet
        if b is None or not b.alive:
            return

        # Bunkers first (between player and invaders on the upward path)
        for bunker in self.bunkers.bunkers:
            if b.rect.colliderect(bunker.rect):
                bunker.apply_damage(b.rect.centerx, b.rect.centery)
                b.alive = False
                self.player.bullet = None
                return

        # UFO
        if self.ufo.active and b.rect.colliderect(self.ufo.rect):
            self._award(self.ufo.hit())
            self.sound.play("ufo_hit")
            b.alive = False
            self.player.bullet = None
            return

        # Split alien
        if self.split_alien.active and b.rect.colliderect(self.split_alien.rect):
            pieces = self.split_alien.hit()
            self.split_pieces.extend(pieces)
            self._award(constants.SPLIT_ALIEN_SCORE)
            self.sound.play("invader_killed")
            b.alive = False
            self.player.bullet = None
            return

        # Split pieces
        for piece in self.split_pieces:
            if piece.alive and b.rect.colliderect(piece.rect):
                piece.alive = False
                self._award(constants.SPLIT_PIECE_SCORE)
                self.sound.play("invader_killed")
                b.alive = False
                self.player.bullet = None
                return

        # Invader grid — with rainbow bonus for last kill
        hit = self.grid.invader_at(b.rect.centerx, b.rect.top)
        if hit is not None:
            row, col = hit
            pts = self.grid.kill(row, col)
            # Rainbow bonus: override points if this was the last invader
            if self.grid.total_alive == 0 and row >= constants.GRID_ROWS - 2:
                if col == 0:
                    pts = constants.RAINBOW_BONUS_BOTTOM_LEFT
                else:
                    pts = constants.RAINBOW_BONUS_BOTTOM
            self._award(pts)
            self.sound.play("invader_killed")
            b.alive = False
            self.player.bullet = None

    def _check_enemy_bullet_collisions(self) -> None:
        for b in self.enemy_bullets:
            if not b.alive:
                continue

            # Bunkers
            for bunker in self.bunkers.bunkers:
                if b.rect.colliderect(bunker.rect):
                    bunker.apply_damage(b.rect.centerx, b.rect.centery)
                    b.alive = False
                    break

            if not b.alive:
                continue

            # Player
            if b.rect.colliderect(self.player.rect):
                b.alive = False
                self.kill_player()

    def _next_round(self) -> None:
        """Reset round-local state in-place. Called by _to_cutscene() and tests."""
        self._round += 1
        self.grid = InvaderGrid(self._assets)
        self.ufo.reset()
        self.split_alien.reset()
        self.split_pieces.clear()
        self.sound.reset_march()
        self._ufo_was_active = False
        self._state = _State.PLAYING
        self._state_timer = 0.0

    def _to_cutscene(self) -> None:
        """Advance round in-place, then hand off to CutsceneScene."""
        self._next_round()  # increments _round, resets grid, returns to PLAYING
        from .cutscene import CutsceneScene
        self.next_scene = CutsceneScene(
            self._assets, game_scene=self, round_num=self._round
        )

    def _respawn_player(self) -> None:
        self.player.reset_position()
        self._state = _State.PLAYING
        self._state_timer = 0.0

    def _award(self, pts: int) -> None:
        self.score = min(self.score + pts, constants.HIGH_SCORE_MAX)
        self.hi_score = max(self.hi_score, self.score)

    def _trigger_game_over(self) -> None:
        from .gameover import GameOverScene

        def make_new_game():
            return GameScene(self._assets, hi_score=self.hi_score)

        self.next_scene = GameOverScene(
            self._assets, self.score, self.hi_score, on_restart=make_new_game
        )

    def _draw_ground_line(self, surface: pygame.Surface) -> None:
        """Horizontal line separating play area from player lane."""
        pygame.draw.line(
            surface,
            constants.COLOR_GREEN,
            (0, constants.PLAYER_Y + 12),
            (constants.SCREEN_W, constants.PLAYER_Y + 12),
        )

    def _draw_pause_overlay(self, surface: pygame.Surface) -> None:
        """Draw semi-transparent overlay and 'PAUSED' text centered on screen."""
        # Semi-transparent dark overlay
        overlay = pygame.Surface((constants.SCREEN_W, constants.SCREEN_H))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)  # 50% transparency
        surface.blit(overlay, (0, 0))

        # PAUSED text
        font = pygame.font.Font(None, 24)
        text_surf = font.render("PAUSED", False, constants.COLOR_WHITE)
        x = (constants.SCREEN_W - text_surf.get_width()) // 2
        y = (constants.SCREEN_H - text_surf.get_height()) // 2
        surface.blit(text_surf, (x, y))
