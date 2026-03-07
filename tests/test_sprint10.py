"""Tests for Sprint 10: Title scene, CRT overlay, pause, initials entry."""

import pygame
import pytest

from space_invaders import constants
from space_invaders.assets import AssetManager
from space_invaders.renderer import Renderer
from space_invaders.scenes.game import GameScene
from space_invaders.scenes.gameover import GameOverScene
from space_invaders.scenes.title import TitleScene


@pytest.fixture
def asset_mgr():
    """Provide a fresh AssetManager with procedural assets."""
    mgr = AssetManager()
    mgr.ensure_assets()
    return mgr

# -----------------------------------------------------------------------------
# TitleScene
# -----------------------------------------------------------------------------


def test_titlescene_shows_title(asset_mgr):
    ts = TitleScene(asset_mgr)
    # Should not crash on draw
    surf = pygame.Surface((constants.SCREEN_W, constants.SCREEN_H))
    ts.draw(surf)


def test_titlescene_transitions_on_keypress(asset_mgr):
    ts = TitleScene(asset_mgr, hi_score=5000)
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
    ts.handle_event(event)
    assert ts.next_scene is not None
    assert isinstance(ts.next_scene, GameScene)


def test_titlescene_preserves_hi_score(asset_mgr):
    ts = TitleScene(asset_mgr, hi_score=9990)
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
    ts.handle_event(event)
    assert ts.next_scene.hi_score == 9990


def test_titlescene_animates_march(asset_mgr):
    ts = TitleScene(asset_mgr)
    # Initial state
    ts.update(0.0)
    # After some time, animation should advance
    ts.update(0.6)  # > 0.5s frame interval
    # Just verify no crash; visual test confirms animation


# -----------------------------------------------------------------------------
# GameOverScene - High Score Entry
# -----------------------------------------------------------------------------


def test_gameoverscene_shows_game_over(asset_mgr):
    gs = GameOverScene(asset_mgr, final_score=1000, hi_score=5000)
    surf = pygame.Surface((constants.SCREEN_W, constants.SCREEN_H))
    gs.draw(surf)
    assert gs._state == "PRESS_KEY"  # Not a new high score


def test_gameoverscene_new_high_score_state(asset_mgr):
    gs = GameOverScene(asset_mgr, final_score=5000, hi_score=4000)
    assert gs._is_new_high_score is True
    assert gs._state == "ENTERING_INITIALS"
    assert gs.initials == ["A", "A", "A"]


def test_gameoverscene_initials_navigation(asset_mgr):
    gs = GameOverScene(asset_mgr, final_score=5000, hi_score=4000)
    # Move right
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT}))
    assert gs._cursor_pos == 1
    # Move right again
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT}))
    assert gs._cursor_pos == 2
    # Clamp at 2
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT}))
    assert gs._cursor_pos == 2
    # Move left
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT}))
    assert gs._cursor_pos == 1


def test_gameoverscene_initials_change_character(asset_mgr):
    gs = GameOverScene(asset_mgr, final_score=5000, hi_score=4000)
    # Start at 'A', go up to 'B'
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP}))
    assert gs.initials[0] == "B"
    # Go down back to 'A'
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN}))
    assert gs.initials[0] == "A"


def test_gameoverscene_initials_wrap_around(asset_mgr):
    gs = GameOverScene(asset_mgr, final_score=5000, hi_score=4000)
    # Character order: A-Z (0-25), then 0-9 (26-35)
    # K_DOWN (direction=-1): A -> 9 (wraps backward from 0 to 35)
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN}))
    assert gs.initials[0] == "9"
    # Continue down: 9 (35) -> 8 (34)
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN}))
    assert gs.initials[0] == "8"
    # K_UP (direction=1): 8 (34) -> 9 (35)
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP}))
    assert gs.initials[0] == "9"
    # 9 (35) -> A (0) via UP (wraps)
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP}))
    assert gs.initials[0] == "A"
    # A (0) -> B (1) via UP
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP}))
    assert gs.initials[0] == "B"


def test_gameoverscene_confirm_initials(asset_mgr):
    gs = GameOverScene(asset_mgr, final_score=5000, hi_score=4000)
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN}))
    assert gs._state == "PRESS_KEY"


def test_gameoverscene_restart_after_initials(asset_mgr):
    gs = GameOverScene(asset_mgr, final_score=5000, hi_score=4000)
    # Confirm initials
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE}))
    # Now in PRESS_KEY state, any key restarts
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_a}))
    assert gs.next_scene is not None


def test_gameoverscene_restart_no_high_score(asset_mgr):
    gs = GameOverScene(asset_mgr, final_score=100, hi_score=5000)
    # Not a high score, any key immediately restarts
    gs.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE}))
    assert gs.next_scene is not None


def test_gameoverscene_cursor_blink(asset_mgr):
    gs = GameOverScene(asset_mgr, final_score=5000, hi_score=4000)
    assert gs._cursor_visible is True
    gs.update(0.3)  # > 0.25s blink interval
    assert gs._cursor_visible is False
    gs.update(0.3)
    assert gs._cursor_visible is True


# -----------------------------------------------------------------------------
# Pause
# -----------------------------------------------------------------------------


def test_pause_toggles_with_p_key(asset_mgr):
    s = GameScene(asset_mgr)
    assert s._state.name == "PLAYING"
    # Press P to pause
    s.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p}))
    assert s._state.name == "PAUSED"
    # Press P again to resume
    s.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p}))
    assert s._state.name == "PLAYING"


def test_pause_toggles_with_escape(asset_mgr):
    s = GameScene(asset_mgr)
    assert s._state.name == "PLAYING"
    s.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE}))
    assert s._state.name == "PAUSED"
    s.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE}))
    assert s._state.name == "PLAYING"


def test_pause_stops_game_updates(asset_mgr):
    s = GameScene(asset_mgr)
    initial_x = s.grid.grid_x
    # Pause
    s.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p}))
    # Update while paused
    s.update(1.0)  # 1 second
    # Grid should not have moved
    assert s.grid.grid_x == initial_x


def test_pause_only_during_playing(asset_mgr):
    s = GameScene(asset_mgr)
    # Kill player to enter PLAYER_DEAD state
    s.kill_player()
    assert s._state.name == "PLAYER_DEAD"
    # Try to pause - should not work
    s.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_p}))
    assert s._state.name == "PLAYER_DEAD"  # Still dead, not paused


# -----------------------------------------------------------------------------
# CRT Scanline Overlay (Renderer)
# -----------------------------------------------------------------------------


def test_renderer_creates_scanline_overlay():
    r = Renderer()
    assert hasattr(r, "_scanline_overlay")
    assert r._scanline_overlay is not None
    assert r._scanline_overlay.get_size() == (
        constants.SCREEN_W * constants.SCALE,
        constants.SCREEN_H * constants.SCALE,
    )


def test_scanline_overlay_has_alpha():
    r = Renderer()
    overlay = r._scanline_overlay
    # Check that overlay has alpha channel
    assert overlay.get_flags() & pygame.SRCALPHA


# -----------------------------------------------------------------------------
# High Score Cap
# -----------------------------------------------------------------------------


def test_high_score_cap_enforced(asset_mgr):
    s = GameScene(asset_mgr)
    # Award points that would exceed cap
    s._award(constants.HIGH_SCORE_MAX + 1000)
    assert s.score == constants.HIGH_SCORE_MAX


def test_hi_score_tracks_max(asset_mgr):
    s = GameScene(asset_mgr)
    s._award(500)
    s._award(300)
    assert s.hi_score == 800
    # Score decreases (shouldn't happen normally), hi_score stays
    s.score = 200
    s._award(0)  # Trigger hi_score update with 0 points
    assert s.hi_score == 800  # Still max
