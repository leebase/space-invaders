"""SoundManager — march sequencer, one-shot effects, UFO drone.

Sprint 8 implementation.

March sequencer keeps its own timer and fires notes at the same interval as
the visual march, so audio and visuals stay locked at all tempos.
"""

from __future__ import annotations

import pygame

from .assets import AssetManager
from .entities.grid import march_interval_ms

_MARCH_NOTES = 4
_UFO_CHANNEL_ID = 0


class SoundManager:
    """Plays march notes, effects, and UFO drone.

    Call `update(dt, invaders_remaining)` once per frame while PLAYING.
    Call `reset_march()` on round start to re-sync timing.
    """

    def __init__(self, asset_mgr: AssetManager):
        self._assets = asset_mgr
        self._march_index: int = 0
        self._march_timer_ms: float = 0.0
        self._muted: bool = False
        self._ufo_channel = pygame.mixer.Channel(_UFO_CHANNEL_ID)

    # ------------------------------------------------------------------
    # Per-frame update (march sequencer)
    # ------------------------------------------------------------------

    def update(self, dt: float, invaders_remaining: int) -> None:
        """Advance march sequencer; fire next note when interval elapsed."""
        if self._muted or invaders_remaining == 0:
            return
        self._march_timer_ms += dt * 1000.0
        interval = march_interval_ms(invaders_remaining)
        while self._march_timer_ms >= interval:
            self._march_timer_ms -= interval
            self._play_march_note()
            interval = march_interval_ms(invaders_remaining)

    # ------------------------------------------------------------------
    # One-shot effects
    # ------------------------------------------------------------------

    def play(self, name: str) -> None:
        """Play a sound effect by name. Silent when muted or sound missing."""
        if self._muted:
            return
        sound = self._assets.get_sound(name)
        if sound is not None:
            sound.play()

    # ------------------------------------------------------------------
    # UFO drone (looping, dedicated channel)
    # ------------------------------------------------------------------

    def start_ufo_drone(self) -> None:
        if self._muted:
            return
        sound = self._assets.get_sound("ufo_drone")
        if sound is not None:
            self._ufo_channel.play(sound, loops=-1)

    def stop_ufo_drone(self) -> None:
        self._ufo_channel.stop()

    # ------------------------------------------------------------------
    # Mute toggle
    # ------------------------------------------------------------------

    def toggle_mute(self) -> None:
        self._muted = not self._muted
        if self._muted:
            pygame.mixer.stop()

    # ------------------------------------------------------------------
    # Round reset
    # ------------------------------------------------------------------

    def reset_march(self) -> None:
        """Reset sequencer timing for a fresh round."""
        self._march_timer_ms = 0.0
        self._march_index = 0

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _play_march_note(self) -> None:
        key = f"march_{self._march_index}"
        sound = self._assets.get_sound(key)
        if sound is not None:
            sound.play()
        self._march_index = (self._march_index + 1) % _MARCH_NOTES
