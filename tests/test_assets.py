"""Tests for AssetManager: procedural fallbacks always return valid surfaces/sounds."""

import pygame
import pytest

from space_invaders.assets import ensure_assets


@pytest.fixture(scope="module")
def mgr():
    return ensure_assets()


SPRITE_NAMES = ["squid", "crab", "octopus", "player", "ufo", "explosion", "bunker"]
SOUND_NAMES = [
    "march_0", "march_1", "march_2", "march_3",
    "shoot", "invader_killed", "player_death", "ufo_hit", "ufo_drone",
]


@pytest.mark.parametrize("name", SPRITE_NAMES)
def test_sprite_returns_non_empty_list(mgr, name):
    frames = mgr.get_sprite_frames(name)
    assert len(frames) >= 1


@pytest.mark.parametrize("name", SPRITE_NAMES)
def test_sprite_frames_are_surfaces(mgr, name):
    frames = mgr.get_sprite_frames(name)
    assert all(isinstance(f, pygame.Surface) for f in frames)


@pytest.mark.parametrize("name", SPRITE_NAMES)
def test_sprite_frames_have_positive_dimensions(mgr, name):
    frames = mgr.get_sprite_frames(name)
    for f in frames:
        assert f.get_width() > 0
        assert f.get_height() > 0


def test_unknown_sprite_returns_fallback(mgr):
    frames = mgr.get_sprite_frames("nonexistent_sprite")
    assert len(frames) >= 1
    assert isinstance(frames[0], pygame.Surface)


@pytest.mark.parametrize("name", SOUND_NAMES)
def test_sound_returns_sound_object(mgr, name):
    sound = mgr.get_sound(name)
    assert sound is not None
    assert isinstance(sound, pygame.mixer.Sound)


def test_unknown_sound_returns_none(mgr):
    assert mgr.get_sound("nonexistent_sound") is None


def test_invader_sprites_have_two_frames(mgr):
    for name in ("squid", "crab", "octopus"):
        assert len(mgr.get_sprite_frames(name)) == 2, (
            f"{name} should have 2 animation frames"
        )
