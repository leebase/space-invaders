"""UFO / Mystery Ship entity."""

from __future__ import annotations

import enum

import pygame

from .. import constants
from ..assets import AssetManager


class _State(enum.Enum):
    IDLE = "idle"
    ACTIVE = "active"
    HIT = "hit"      # score displayed briefly before returning to IDLE


class UFO:
    """Mystery ship that traverses the top of the screen left → right.

    Score is deterministic: CYCLE[shot_count % len(CYCLE)] where CYCLE is
    UFO_SCORE_CYCLE from constants.
    """

    def __init__(self, asset_mgr: AssetManager):
        frames = asset_mgr.get_sprite_frames("ufo")
        self._sprite = frames[0]
        self._font = pygame.font.Font(None, 8)
        w = self._sprite.get_width()
        h = self._sprite.get_height()
        self.rect = pygame.Rect(-w, constants.UFO_Y, w, h)
        self._x = float(-w)
        self._state = _State.IDLE
        self._spawn_timer_ms: float = 0.0
        self._hit_timer: float = 0.0
        self._shot_count: int = 0
        self._last_score: int = 0
        self._score_x: int = 0  # x position where score text is drawn

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def active(self) -> bool:
        """True while UFO is visible and hittable."""
        return self._state == _State.ACTIVE

    def update(self, dt: float) -> None:
        if self._state == _State.IDLE:
            self._spawn_timer_ms += dt * 1000.0
            if self._spawn_timer_ms >= constants.UFO_INTERVAL_MS:
                self._spawn()

        elif self._state == _State.ACTIVE:
            self._x += constants.UFO_SPEED * dt
            self.rect.x = int(self._x)
            if self.rect.left >= constants.SCREEN_W:
                self._deactivate()

        elif self._state == _State.HIT:
            self._hit_timer += dt
            if self._hit_timer >= constants.UFO_HIT_DISPLAY_S:
                self._deactivate()

    def hit(self) -> int:
        """Call when player bullet collides with the UFO.

        Returns the score value for this hit and enters the HIT display state.
        """
        cycle = constants.UFO_SCORE_CYCLE
        score = cycle[self._shot_count % len(cycle)]
        self._last_score = score
        self._score_x = self.rect.x
        self._shot_count += 1
        self._state = _State.HIT
        self._hit_timer = 0.0
        return score

    def draw(self, surface: pygame.Surface) -> None:
        if self._state == _State.ACTIVE:
            surface.blit(self._sprite, self.rect.topleft)
        elif self._state == _State.HIT:
            text = self._font.render(
                str(self._last_score), False, constants.COLOR_RED
            )
            x = max(0, min(self._score_x, constants.SCREEN_W - text.get_width()))
            surface.blit(text, (x, constants.UFO_Y))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _spawn(self) -> None:
        self._x = float(-self.rect.width)
        self.rect.x = int(self._x)
        self._state = _State.ACTIVE
        self._spawn_timer_ms = 0.0

    def _deactivate(self) -> None:
        self._state = _State.IDLE
        self._spawn_timer_ms = 0.0
