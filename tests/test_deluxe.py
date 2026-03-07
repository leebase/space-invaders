"""Tests for Sprint 9 Deluxe features:
- Splitting aliens
- Rainbow bonus
- Invader color on descent
- Inter-round cutscene
"""

from __future__ import annotations

import pytest

from space_invaders import constants
from space_invaders.assets import ensure_assets
from space_invaders.entities.grid import InvaderGrid
from space_invaders.entities.split_alien import SplitAlien, SplitPiece
from space_invaders.scenes.cutscene import CutsceneScene
from space_invaders.scenes.game import GameScene, _State


@pytest.fixture(scope="module")
def asset_mgr():
    return ensure_assets()


@pytest.fixture
def scene(asset_mgr):
    return GameScene(asset_mgr)


def _kill_all(s: GameScene) -> None:
    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            s.grid.kill(row, col)


# ---------------------------------------------------------------------------
# Splitting alien — SplitAlien entity
# ---------------------------------------------------------------------------


def test_split_alien_starts_idle(asset_mgr):
    sa = SplitAlien(asset_mgr)
    assert not sa.active


def test_split_alien_spawns_after_interval(asset_mgr):
    sa = SplitAlien(asset_mgr)
    sa.update(constants.SPLIT_ALIEN_INTERVAL_MS / 1000.0 + 0.01)
    assert sa.active


def test_split_alien_moves_left(asset_mgr):
    sa = SplitAlien(asset_mgr)
    sa._spawn()
    x_before = sa.rect.x
    sa.update(0.5)
    assert sa.rect.x < x_before


def test_split_alien_deactivates_at_left_edge(asset_mgr):
    sa = SplitAlien(asset_mgr)
    sa._spawn()
    sa._x = float(-sa.rect.width - 1)
    sa.rect.x = int(sa._x)
    sa.update(0.001)
    assert not sa.active


def test_split_alien_hit_returns_two_pieces(asset_mgr):
    sa = SplitAlien(asset_mgr)
    sa._spawn()
    pieces = sa.hit()
    assert len(pieces) == 2
    assert all(isinstance(p, SplitPiece) for p in pieces)


def test_split_alien_deactivates_on_hit(asset_mgr):
    sa = SplitAlien(asset_mgr)
    sa._spawn()
    sa.hit()
    assert not sa.active


def test_split_piece_moves(asset_mgr):
    sa = SplitAlien(asset_mgr)
    sa._spawn()
    pieces = sa.hit()
    x0 = [p.rect.x for p in pieces]
    for p in pieces:
        p.update(0.1)
    for i, p in enumerate(pieces):
        assert p.rect.x != x0[i] or p.rect.y != pieces[i].rect.y


def test_split_piece_goes_offscreen(asset_mgr):
    sa = SplitAlien(asset_mgr)
    sa._spawn()
    pieces = sa.hit()
    # Drive pieces off-screen
    for p in pieces:
        p.update(100.0)
    assert all(not p.alive for p in pieces)


def test_split_alien_reset_returns_to_idle(asset_mgr):
    sa = SplitAlien(asset_mgr)
    sa._spawn()
    sa.reset()
    assert not sa.active


# ---------------------------------------------------------------------------
# Splitting alien — GameScene integration
# ---------------------------------------------------------------------------


def test_gamescene_has_split_alien(scene):
    assert isinstance(scene.split_alien, SplitAlien)


def test_player_bullet_hits_split_alien(asset_mgr):
    from space_invaders.entities.bullet import Bullet

    s = GameScene(asset_mgr)
    s.split_alien._spawn()
    b = Bullet(
        s.split_alien.rect.centerx, s.split_alien.rect.centery,
        -constants.BULLET_SPEED
    )
    s.player.bullet = b
    s.update(0.001)
    assert not s.split_alien.active
    assert s.score == constants.SPLIT_ALIEN_SCORE


def test_split_pieces_spawned_in_gamescene(asset_mgr):
    from space_invaders.entities.bullet import Bullet

    s = GameScene(asset_mgr)
    s.split_alien._spawn()
    b = Bullet(
        s.split_alien.rect.centerx, s.split_alien.rect.centery,
        -constants.BULLET_SPEED
    )
    s.player.bullet = b
    s.update(0.001)
    assert len(s.split_pieces) == 2


def test_player_bullet_hits_split_piece(asset_mgr):
    from space_invaders.entities.bullet import Bullet
    from space_invaders.entities.split_alien import SplitPiece

    s = GameScene(asset_mgr)
    # Inject a stationary split piece at a known position (no velocity)
    sprite = asset_mgr.get_sprite_frames("split_piece")[0]
    piece = SplitPiece(100, 100, 0.0, 0.0, sprite)
    s.split_pieces.append(piece)

    b = Bullet(piece.rect.centerx, piece.rect.centery, -constants.BULLET_SPEED)
    s.player.bullet = b
    prev_score = s.score
    s.update(0.001)
    assert s.score == prev_score + constants.SPLIT_PIECE_SCORE


# ---------------------------------------------------------------------------
# Rainbow bonus
# ---------------------------------------------------------------------------


def test_rainbow_bonus_bottom_row(asset_mgr):
    from space_invaders.entities.bullet import Bullet

    s = GameScene(asset_mgr)
    # Kill all except last invader in bottom row, col 1 (not col 0)
    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            if not (row == constants.GRID_ROWS - 1 and col == 1):
                s.grid.kill(row, col)
    assert s.grid.total_alive == 1
    # Place bullet on the last invader
    hit = s.grid.invader_at.__func__(s.grid, *_find_alive_center(s.grid))
    row, col = hit
    inv_x, inv_y = _find_alive_center(s.grid)
    b = Bullet(inv_x, inv_y, -constants.BULLET_SPEED)
    s.player.bullet = b
    s.update(0.001)
    assert s.score == constants.RAINBOW_BONUS_BOTTOM


def test_rainbow_bonus_bottom_left(asset_mgr):
    from space_invaders.entities.bullet import Bullet

    s = GameScene(asset_mgr)
    # Kill all except bottom-left invader (row 4, col 0)
    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            if not (row == constants.GRID_ROWS - 1 and col == 0):
                s.grid.kill(row, col)
    assert s.grid.total_alive == 1
    inv_x, inv_y = _find_alive_center(s.grid)
    b = Bullet(inv_x, inv_y, -constants.BULLET_SPEED)
    s.player.bullet = b
    s.update(0.001)
    assert s.score == constants.RAINBOW_BONUS_BOTTOM_LEFT


def test_no_rainbow_bonus_for_non_bottom_row(asset_mgr):
    from space_invaders.entities.bullet import Bullet

    s = GameScene(asset_mgr)
    # Kill all except top-row invader (row 0, col 5)
    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            if not (row == 0 and col == 5):
                s.grid.kill(row, col)
    inv_x, inv_y = _find_alive_center(s.grid)
    b = Bullet(inv_x, inv_y, -constants.BULLET_SPEED)
    s.player.bullet = b
    s.update(0.001)
    # Should get normal squid score, NOT rainbow bonus
    assert s.score == constants.SCORE_SQUID


def _find_alive_center(grid: InvaderGrid) -> tuple[int, int]:
    """Return screen-center (x, y) of the first alive invader."""
    from space_invaders import constants as c
    for row in range(c.GRID_ROWS):
        key = c.ROW_TYPES[row]
        for col in range(c.GRID_COLS):
            if grid.alive[row][col]:
                sw = grid._frames[key][0].get_width()
                cw = c.CELL_W
                cell_x = grid.grid_x + col * cw
                cell_y = grid.grid_y + row * c.CELL_H
                blit_x = cell_x + (cw - sw) // 2
                blit_y = cell_y + (c.CELL_H - c.SPRITE_H) // 2
                return blit_x + sw // 2, blit_y + c.SPRITE_H // 2
    return 0, 0


# ---------------------------------------------------------------------------
# Invader color on descent
# ---------------------------------------------------------------------------


def test_descent_color_white_at_start(asset_mgr):
    grid = InvaderGrid(asset_mgr)
    assert grid._descent_color() == (255, 255, 255)


def test_descent_color_changes_with_grid_y(asset_mgr):
    grid = InvaderGrid(asset_mgr)
    grid.grid_y = 80
    assert grid._descent_color() == (0, 255, 255)  # cyan band


def test_descent_color_orange_at_deep_descent(asset_mgr):
    grid = InvaderGrid(asset_mgr)
    grid.grid_y = 145
    assert grid._descent_color() == (255, 128, 0)


def test_tint_cache_populated_on_draw(asset_mgr):
    import pygame
    grid = InvaderGrid(asset_mgr)
    surf = pygame.Surface((constants.SCREEN_W, constants.SCREEN_H))
    grid.draw(surf)
    assert len(grid._tint_cache) > 0


def test_tinted_sprite_preserves_alpha(asset_mgr):
    import numpy as np
    import pygame
    grid = InvaderGrid(asset_mgr)
    frames = grid._frames["squid"]
    color = (255, 0, 0)
    tinted = grid._get_tinted(frames[0], color)
    orig_alpha = np.array(pygame.surfarray.pixels_alpha(frames[0]))
    tint_alpha = np.array(pygame.surfarray.pixels_alpha(tinted))
    assert np.array_equal(orig_alpha, tint_alpha)


# ---------------------------------------------------------------------------
# Cutscene
# ---------------------------------------------------------------------------


def test_cutscene_transitions_to_game_after_duration(asset_mgr, scene):
    cs = CutsceneScene(asset_mgr, game_scene=scene, round_num=2)
    cs.update(constants.CUTSCENE_DURATION + 0.01)
    assert cs.next_scene is scene


def test_cutscene_skipped_on_keypress(asset_mgr, scene):
    import pygame
    cs = CutsceneScene(asset_mgr, game_scene=scene, round_num=2)
    event = pygame.event.Event(
        pygame.KEYDOWN,
        {"key": pygame.K_SPACE, "mod": 0, "unicode": " ", "scancode": 0},
    )
    cs.handle_event(event)
    assert cs.next_scene is scene


def test_cutscene_keypress_wins_over_timer(asset_mgr, scene):
    """R001: Keypress skip should not be overwritten by timer expiry."""
    import pygame
    cs = CutsceneScene(asset_mgr, game_scene=scene, round_num=2)
    # User presses key to skip
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
    cs.handle_event(event)
    assert cs.next_scene is scene
    # Timer would have expired on next update
    cs.update(constants.CUTSCENE_DURATION + 0.01)
    # next_scene should still be the same scene reference
    assert cs.next_scene is scene


def test_round_clear_transitions_to_cutscene(asset_mgr):
    s = GameScene(asset_mgr)
    _kill_all(s)
    s.update(0.01)  # → ROUND_CLEAR
    assert s._state == _State.ROUND_CLEAR
    s.update(constants.ROUND_CLEAR_DELAY + 0.01)  # → _to_cutscene()
    assert isinstance(s.next_scene, CutsceneScene)


def test_cutscene_round_num_is_new_round(asset_mgr):
    s = GameScene(asset_mgr)
    _kill_all(s)
    s.update(0.01)
    s.update(constants.ROUND_CLEAR_DELAY + 0.01)
    cs = s.next_scene
    assert cs._round_num == 2


def test_cutscene_game_scene_ref_is_advanced(asset_mgr):
    """After _to_cutscene(), the GameScene ref inside CutsceneScene
    should already have its grid reset (round advanced in-place)."""
    s = GameScene(asset_mgr)
    _kill_all(s)
    s.update(0.01)
    s.update(constants.ROUND_CLEAR_DELAY + 0.01)
    cs = s.next_scene
    # The game scene that CutsceneScene will restore is already round 2
    assert cs._game_scene._round == 2
    assert cs._game_scene.grid.total_alive == constants.GRID_ROWS * constants.GRID_COLS
