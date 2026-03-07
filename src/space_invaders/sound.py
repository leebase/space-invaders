"""SoundManager — stub, implemented in Sprint 8."""

from __future__ import annotations

from .assets import AssetManager


class SoundManager:
    """Plays march notes, effects, and UFO drone.

    All methods are no-ops until Sprint 8.
    """

    def __init__(self, asset_mgr: AssetManager):
        self._assets = asset_mgr
        self._march_index = 0

    def play_march_note(self) -> None:
        """Play the next note in the 4-note march sequence."""
        pass  # Sprint 8

    def play(self, name: str) -> None:
        """Play a one-shot sound effect by name."""
        pass  # Sprint 8

    def start_ufo_drone(self) -> None:
        pass  # Sprint 8

    def stop_ufo_drone(self) -> None:
        pass  # Sprint 8

    def update(self, dt: float) -> None:
        pass  # Sprint 8
