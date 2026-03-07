"""Asset management: load sprites and sounds from disk, or generate procedurally.

Call `AssetManager.ensure_assets()` once at startup (after pygame.init).
All other code accesses assets via `get_sprite_frames(name)` and `get_sound(name)`.
The game never crashes due to missing assets — procedural fallbacks cover everything.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pygame

from . import constants

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Procedural sprite pixel patterns (fallback when real sprites unavailable)
# Each pattern is a list of rows; 1 = opaque pixel, 0 = transparent.
# ---------------------------------------------------------------------------

_SQUID_0 = [
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 0, 1, 1, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 0, 1, 0],
]

_SQUID_1 = [
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 0, 1, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 0, 0, 0, 0, 1, 1],
]

_CRAB_0 = [
    [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0],
]

_CRAB_1 = [
    [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0],
]

_OCTOPUS_0 = [
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0],
]

_OCTOPUS_1 = [
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
]

_PLAYER_SPRITE = [
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

_UFO_SPRITE = [
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
]

_SPLIT_ALIEN_SPRITE = [
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 0, 1, 1, 0, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 1, 1, 1, 0, 1],
    [0, 0, 1, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 1, 0, 1, 0],
]

_SPLIT_PIECE_SPRITE = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0],
]

_EXPLOSION_SPRITE = [
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
]

# Bunker is handled separately (pixel destruction), but provide a base sprite
_BUNKER_SPRITE = [
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pattern_to_surface(
    pattern: list[list[int]], color: tuple[int, int, int]
) -> pygame.Surface:
    h = len(pattern)
    w = len(pattern[0])
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    rgba = (*color, 255)
    for y, row in enumerate(pattern):
        for x, on in enumerate(row):
            if on:
                surf.set_at((x, y), rgba)
    return surf


def _make_beep(
    frequency: float, duration: float = 0.08, volume: float = 0.4
) -> pygame.mixer.Sound:
    """Generate a simple square-wave beep as a pygame Sound."""
    sample_rate = 44100
    n = int(sample_rate * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    wave = np.sign(np.sin(2 * np.pi * frequency * t))
    wave = (wave * 32767 * volume).astype(np.int16)
    stereo = np.column_stack([wave, wave])
    return pygame.sndarray.make_sound(stereo)


# ---------------------------------------------------------------------------
# AssetManager
# ---------------------------------------------------------------------------

class AssetManager:
    """Central registry for all game sprites and sounds.

    Usage:
        mgr = AssetManager()
        mgr.ensure_assets()            # call once after pygame.init()
        frames = mgr.get_sprite_frames("squid")   # list[pygame.Surface]
        sound  = mgr.get_sound("shoot")           # pygame.mixer.Sound | None
    """

    ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets"

    def __init__(self):
        self._sprites: dict[str, list[pygame.Surface]] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ensure_assets(self) -> None:
        """Load or generate all required assets. Never raises."""
        self.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        (self.ASSETS_DIR / "sprites").mkdir(exist_ok=True)
        (self.ASSETS_DIR / "sounds").mkdir(exist_ok=True)

        self._load_sprites()
        self._load_sounds()
        n_s, n_snd = len(self._sprites), len(self._sounds)
        log.info("Assets ready (%d sprites, %d sounds)", n_s, n_snd)

    def get_sprite_frames(self, name: str) -> list[pygame.Surface]:
        if name not in self._sprites:
            log.warning("Unknown sprite '%s', using fallback", name)
            return self._fallback_frames(name)
        return self._sprites[name]

    def get_sound(self, name: str) -> pygame.mixer.Sound | None:
        return self._sounds.get(name)

    # ------------------------------------------------------------------
    # Sprite loading (disk → procedural fallback)
    # ------------------------------------------------------------------

    def _load_sprites(self) -> None:
        defs: dict[str, tuple[list[list[list[int]]], tuple[int, int, int]]] = {
            "squid":   ([_SQUID_0, _SQUID_1],       constants.INVADER_COLORS["squid"]),
            "crab":    ([_CRAB_0, _CRAB_1],          constants.INVADER_COLORS["crab"]),
            "octopus": ([_OCTOPUS_0, _OCTOPUS_1], constants.INVADER_COLORS["octopus"]),
            "player":  ([_PLAYER_SPRITE],            constants.COLOR_GREEN),
            "ufo":     ([_UFO_SPRITE],               constants.COLOR_RED),
            "explosion":   ([_EXPLOSION_SPRITE],     constants.COLOR_WHITE),
            "split_alien": ([_SPLIT_ALIEN_SPRITE],   constants.COLOR_YELLOW),
            "split_piece": ([_SPLIT_PIECE_SPRITE],   constants.COLOR_YELLOW),
            "bunker":  ([_BUNKER_SPRITE],            constants.COLOR_GREEN),
        }
        for name, (patterns, color) in defs.items():
            path = self.ASSETS_DIR / "sprites" / f"{name}.png"
            frames = self._try_load_spritesheet(path, name, patterns, color)
            self._sprites[name] = frames

    def _try_load_spritesheet(
        self,
        path: Path,
        name: str,
        fallback_patterns: list[list[list[int]]],
        fallback_color: tuple[int, int, int],
    ) -> list[pygame.Surface]:
        if path.exists():
            try:
                sheet = pygame.image.load(str(path)).convert_alpha()
                # Horizontal strip: each frame has width = sheet.width / frame_count
                n = len(fallback_patterns)
                fw = sheet.get_width() // n
                fh = sheet.get_height()
                expected_w = len(fallback_patterns[0][0])
                expected_h = len(fallback_patterns[0])
                if fw != expected_w or fh != expected_h:
                    log.warning(
                        "Sprite '%s' dimensions %dx%d don't match expected %dx%d"
                        " — using procedural fallback",
                        name, fw, fh, expected_w, expected_h,
                    )
                    raise ValueError("dimension mismatch")
                frames = [
                    sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh)) for i in range(n)
                ]
                log.info("Loaded sprite '%s' from disk (%d frames)", name, n)
                return frames
            except Exception as exc:
                log.warning(
                    "Failed to load sprite '%s': %s — using procedural fallback",
                    name, exc,
                )

        return [_pattern_to_surface(p, fallback_color) for p in fallback_patterns]

    def _fallback_frames(self, name: str) -> list[pygame.Surface]:
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        surf.fill(constants.COLOR_WHITE)
        return [surf]

    # ------------------------------------------------------------------
    # Sound loading (disk → procedural beep fallback)
    # ------------------------------------------------------------------

    # Procedural march: four descending pitches matching arcade feel
    _MARCH_FREQS = [160.0, 130.0, 100.0, 80.0]

    def _load_sounds(self) -> None:
        sound_defs = {
            "march_0": ("march_0.wav", self._MARCH_FREQS[0], 0.10),
            "march_1": ("march_1.wav", self._MARCH_FREQS[1], 0.10),
            "march_2": ("march_2.wav", self._MARCH_FREQS[2], 0.10),
            "march_3": ("march_3.wav", self._MARCH_FREQS[3], 0.10),
            "shoot":         ("shoot.wav",         800.0, 0.05),
            "invader_killed": ("invader_killed.wav", 300.0, 0.08),
            "player_death":  ("player_death.wav",  200.0, 0.20),
            "ufo_hit":       ("ufo_hit.wav",        600.0, 0.08),
        }
        for name, (filename, freq, dur) in sound_defs.items():
            path = self.ASSETS_DIR / "sounds" / filename
            self._sounds[name] = self._try_load_sound(path, name, freq, dur)

        # UFO drone loaded separately (longer)
        drone_path = self.ASSETS_DIR / "sounds" / "ufo_drone.wav"
        self._sounds["ufo_drone"] = self._try_load_sound(
            drone_path, "ufo_drone", 120.0, 0.5
        )

    def _try_load_sound(
        self, path: Path, name: str, fallback_freq: float, fallback_dur: float
    ) -> pygame.mixer.Sound:
        if path.exists():
            try:
                sound = pygame.mixer.Sound(str(path))
                log.info("Loaded sound '%s' from disk", name)
                return sound
            except Exception as exc:
                log.warning(
                    "Failed to load sound '%s': %s — using beep fallback", name, exc
                )
        return _make_beep(fallback_freq, fallback_dur)


def ensure_assets() -> AssetManager:
    """Convenience: create and initialise an AssetManager, return it."""
    mgr = AssetManager()
    mgr.ensure_assets()
    return mgr
