"""Tests for Sprint 8: SoundManager march sequencer, mute, and GameScene wiring."""

from __future__ import annotations

import pytest

from space_invaders.assets import ensure_assets
from space_invaders.entities.grid import march_interval_ms
from space_invaders.scenes.game import GameScene
from space_invaders.sound import SoundManager


@pytest.fixture(scope="module")
def asset_mgr():
    return ensure_assets()


@pytest.fixture
def sm(asset_mgr):
    return SoundManager(asset_mgr)


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def test_sound_manager_starts_unmuted(sm):
    assert not sm._muted


def test_march_index_starts_at_zero(sm):
    assert sm._march_index == 0


def test_march_timer_starts_at_zero(sm):
    assert sm._march_timer_ms == 0.0


# ---------------------------------------------------------------------------
# March sequencer timing
# ---------------------------------------------------------------------------


def test_march_does_not_fire_before_interval(sm):
    remaining = 55
    interval_s = march_interval_ms(remaining) / 1000.0
    sm.update(interval_s * 0.5, remaining)
    assert sm._march_index == 0


def test_march_fires_at_interval(sm):
    remaining = 55
    interval_s = march_interval_ms(remaining) / 1000.0
    sm.update(interval_s + 0.001, remaining)
    assert sm._march_index == 1


def test_march_fires_multiple_steps(sm):
    sm.reset_march()
    remaining = 1  # fastest interval
    interval_s = march_interval_ms(remaining) / 1000.0
    sm.update(interval_s * 2 + 0.001, remaining)
    assert sm._march_index == 2


def test_march_wraps_to_zero_after_four(asset_mgr):
    s = SoundManager(asset_mgr)
    remaining = 1
    interval_s = march_interval_ms(remaining) / 1000.0
    s.update(interval_s * 4 + 0.001, remaining)
    assert s._march_index == 0


def test_march_silent_when_no_invaders(asset_mgr):
    s = SoundManager(asset_mgr)
    s.update(10.0, 0)   # no invaders — sequencer must not advance
    assert s._march_index == 0


# ---------------------------------------------------------------------------
# Mute
# ---------------------------------------------------------------------------


def test_toggle_mute_mutes(sm):
    sm._muted = False
    sm.toggle_mute()
    assert sm._muted


def test_toggle_mute_unmutes(sm):
    sm._muted = True
    sm.toggle_mute()
    assert not sm._muted


def test_muted_march_does_not_advance(asset_mgr):
    s = SoundManager(asset_mgr)
    s.toggle_mute()
    interval_s = march_interval_ms(55) / 1000.0
    s.update(interval_s * 10, 55)
    assert s._march_index == 0


def test_play_does_not_raise_when_muted(sm):
    sm._muted = True
    sm.play("shoot")   # must not raise
    sm._muted = False


def test_play_does_not_raise_for_unknown_name(sm):
    sm.play("nonexistent_sound")  # must not raise


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def test_reset_march_clears_timer(asset_mgr):
    s = SoundManager(asset_mgr)
    s._march_timer_ms = 500.0
    s.reset_march()
    assert s._march_timer_ms == 0.0


def test_reset_march_clears_index(asset_mgr):
    s = SoundManager(asset_mgr)
    s._march_index = 3
    s.reset_march()
    assert s._march_index == 0


# ---------------------------------------------------------------------------
# GameScene integration
# ---------------------------------------------------------------------------


def test_gamescene_has_sound_manager(asset_mgr):
    s = GameScene(asset_mgr)
    assert isinstance(s.sound, SoundManager)


def test_mute_toggle_in_gamescene(asset_mgr):
    import pygame

    s = GameScene(asset_mgr)
    assert not s.sound._muted
    event = pygame.event.Event(
        pygame.KEYDOWN,
        {"key": pygame.K_m, "mod": 0, "unicode": "m", "scancode": 0},
    )
    s.handle_event(event)
    assert s.sound._muted
    s.handle_event(event)
    assert not s.sound._muted


def test_shoot_sound_fires_on_bullet_created(asset_mgr):
    """Firing a bullet when none is active should not raise."""
    import pygame

    s = GameScene(asset_mgr)
    assert s.player.bullet is None
    event = pygame.event.Event(
        pygame.KEYDOWN,
        {"key": pygame.K_SPACE, "mod": 0, "unicode": " ", "scancode": 0},
    )
    s.handle_event(event)  # must not raise; bullet is created, sound plays


def test_sound_reset_on_round_advance(asset_mgr):
    """March timer and index reset when a new round starts."""
    s = GameScene(asset_mgr)
    s.sound._march_index = 3
    s.sound._march_timer_ms = 750.0
    # Manually trigger round advance
    s._next_round()
    assert s.sound._march_index == 0
    assert s.sound._march_timer_ms == 0.0
