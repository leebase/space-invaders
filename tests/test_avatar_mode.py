"""Avatar mode regression tests — Sprint 16.

Verifies that coordinate scaling works correctly in Avatar mode:
- Grid starts at 2x arcade position
- March boundaries are 2x arcade limits (no premature descent)
- Player positioned at 2x Y
- Player bullet can reach all 11 columns of the invader grid
- invader_at() resolves hits correctly in 2x coordinate space
- Round 2 grid has renderer attached (not None)
- Bunkers positioned at 2x Y, sized 44x32
- Arcade mode is unchanged (regression guard)
"""

from __future__ import annotations

import pytest

from space_invaders import constants
from space_invaders.assets import ensure_assets
from space_invaders.entities.bunker import BunkerGroup
from space_invaders.entities.grid import InvaderGrid
from space_invaders.entities.invader_renderer import AvatarRenderer, PixelRenderer
from space_invaders.entities.player import Player
from space_invaders.mode import GameMode, ModeConfig
from space_invaders.scenes.game import GameScene


@pytest.fixture(scope="module")
def asset_mgr():
    return ensure_assets()


@pytest.fixture
def arcade_cfg():
    return ModeConfig(GameMode.ARCADE)


@pytest.fixture
def avatar_cfg():
    return ModeConfig(GameMode.AVATAR)


# ---------------------------------------------------------------------------
# ModeConfig coordinate scaling
# ---------------------------------------------------------------------------


class TestModeConfigCoordinateScaling:
    def test_arcade_coord_scale(self, arcade_cfg):
        assert arcade_cfg.coord_scale == 1

    def test_avatar_coord_scale(self, avatar_cfg):
        assert avatar_cfg.coord_scale == 2

    def test_avatar_grid_start_x(self, avatar_cfg):
        assert avatar_cfg.grid_start_x == 52   # 26 * 2

    def test_avatar_grid_start_y(self, avatar_cfg):
        assert avatar_cfg.grid_start_y == 128  # 64 * 2

    def test_avatar_left_limit(self, avatar_cfg):
        assert avatar_cfg.left_limit == 8      # 4 * 2

    def test_avatar_right_limit(self, avatar_cfg):
        assert avatar_cfg.right_limit == 440   # 220 * 2

    def test_avatar_march_step_x(self, avatar_cfg):
        assert avatar_cfg.march_step_x == 4    # 2 * 2

    def test_avatar_march_step_y(self, avatar_cfg):
        assert avatar_cfg.march_step_y == 16   # 8 * 2

    def test_avatar_player_y(self, avatar_cfg):
        assert avatar_cfg.player_y == 432      # 216 * 2

    def test_avatar_player_speed(self, avatar_cfg):
        assert avatar_cfg.player_speed == 160  # 80 * 2

    def test_avatar_bullet_speed(self, avatar_cfg):
        assert avatar_cfg.bullet_speed == 600  # 300 * 2

    def test_avatar_bunker_y(self, avatar_cfg):
        assert avatar_cfg.bunker_y == 384      # 192 * 2

    def test_avatar_bunker_w(self, avatar_cfg):
        assert avatar_cfg.bunker_w == 44       # 22 * 2

    def test_avatar_bunker_h(self, avatar_cfg):
        assert avatar_cfg.bunker_h == 32       # 16 * 2

    def test_avatar_ufo_y(self, avatar_cfg):
        assert avatar_cfg.ufo_y == 64          # 32 * 2

    def test_avatar_invader_kill_line(self, avatar_cfg):
        assert avatar_cfg.invader_kill_line == 432  # 216 * 2

    def test_arcade_values_unchanged(self, arcade_cfg):
        assert arcade_cfg.grid_start_x == 26
        assert arcade_cfg.grid_start_y == 64
        assert arcade_cfg.left_limit == 4
        assert arcade_cfg.right_limit == 220
        assert arcade_cfg.player_y == 216
        assert arcade_cfg.bunker_y == 192
        assert arcade_cfg.bunker_w == 22
        assert arcade_cfg.bunker_h == 16


# ---------------------------------------------------------------------------
# InvaderGrid — avatar mode coordinates
# ---------------------------------------------------------------------------


class TestAvatarGrid:
    def test_grid_starts_at_2x_position(self, asset_mgr, avatar_cfg):
        grid = InvaderGrid(asset_mgr, avatar_cfg)
        assert grid.grid_x == 52
        assert grid.grid_y == 128

    def test_grid_cell_size_is_32(self, asset_mgr, avatar_cfg):
        grid = InvaderGrid(asset_mgr, avatar_cfg)
        grid.set_renderer(AvatarRenderer(asset_mgr))
        assert grid.cell_w == 32
        assert grid.cell_h == 32

    def test_no_premature_descent_on_first_march_step(self, asset_mgr, avatar_cfg):
        """Right edge of grid at startup must be below right_limit (440).

        In the broken implementation the grid started at 368 (> 220 arcade limit),
        triggering an immediate descent on the very first march step.
        """
        grid = InvaderGrid(asset_mgr, avatar_cfg)
        grid.set_renderer(AvatarRenderer(asset_mgr))
        start_y = grid.grid_y

        # Force a single march step
        grid._march_step()

        assert grid.grid_y == start_y, (
            "Grid descended on the first march step — right_limit is wrong"
        )

    def test_grid_marches_right_first(self, asset_mgr, avatar_cfg):
        grid = InvaderGrid(asset_mgr, avatar_cfg)
        grid.set_renderer(AvatarRenderer(asset_mgr))
        start_x = grid.grid_x
        grid._march_step()
        assert grid.grid_x > start_x

    def test_invader_at_returns_hit_for_all_columns(self, asset_mgr, avatar_cfg):
        """Player bullet at each column center must register a hit."""
        grid = InvaderGrid(asset_mgr, avatar_cfg)
        grid.set_renderer(AvatarRenderer(asset_mgr))
        cell_w = grid.cell_w  # 32
        cell_h = grid.cell_h  # 32

        for col in range(constants.GRID_COLS):
            px = grid.grid_x + col * cell_w + cell_w // 2
            py = grid.grid_y + cell_h // 2  # center of row 0
            hit = grid.invader_at(px, py)
            assert hit is not None, f"No hit registered for column {col} at x={px}"
            assert hit[1] == col

    def test_invader_at_correct_coords_in_2x_space(self, asset_mgr, avatar_cfg):
        grid = InvaderGrid(asset_mgr, avatar_cfg)
        grid.set_renderer(AvatarRenderer(asset_mgr))
        # col 5, row 3 center
        col, row = 5, 3
        px = grid.grid_x + col * 32 + 16
        py = grid.grid_y + row * 32 + 16
        hit = grid.invader_at(px, py)
        assert hit == (row, col)

    def test_arcade_grid_still_at_arcade_position(self, asset_mgr, arcade_cfg):
        grid = InvaderGrid(asset_mgr, arcade_cfg)
        assert grid.grid_x == 26
        assert grid.grid_y == 64


# ---------------------------------------------------------------------------
# Player — avatar mode position and movement
# ---------------------------------------------------------------------------


class TestAvatarPlayer:
    def test_player_starts_at_2x_y(self, asset_mgr, avatar_cfg):
        player = Player(asset_mgr, avatar_cfg)
        assert player.rect.y == 432

    def test_player_centered_on_448_wide_screen(self, asset_mgr, avatar_cfg):
        player = Player(asset_mgr, avatar_cfg)
        # Centre of player should be near centre of 448-wide surface
        assert abs(player.rect.centerx - 224) < 20

    def test_player_bullet_speed_is_2x(self, asset_mgr, avatar_cfg):
        player = Player(asset_mgr, avatar_cfg)
        bullet = player.fire()
        assert bullet is not None
        # Bullet travels upward at 2x arcade speed (dy is negative = upward)
        assert bullet.dy == -600

    def test_arcade_player_y_unchanged(self, asset_mgr, arcade_cfg):
        player = Player(asset_mgr, arcade_cfg)
        assert player.rect.y == 216


# ---------------------------------------------------------------------------
# BunkerGroup — avatar mode position and size
# ---------------------------------------------------------------------------


class TestAvatarBunkers:
    def test_bunkers_at_2x_y(self, asset_mgr, avatar_cfg):
        group = BunkerGroup(asset_mgr, avatar_cfg)
        for bunker in group.bunkers:
            assert bunker.rect.y == 384

    def test_bunkers_sized_44x32(self, asset_mgr, avatar_cfg):
        group = BunkerGroup(asset_mgr, avatar_cfg)
        for bunker in group.bunkers:
            assert bunker.rect.width == 44
            assert bunker.rect.height == 32

    def test_arcade_bunkers_unchanged(self, asset_mgr, arcade_cfg):
        group = BunkerGroup(asset_mgr, arcade_cfg)
        for bunker in group.bunkers:
            assert bunker.rect.y == 192
            assert bunker.rect.width == 22
            assert bunker.rect.height == 16


# ---------------------------------------------------------------------------
# GameScene — round advance preserves renderer
# ---------------------------------------------------------------------------


class TestAvatarGameSceneRoundAdvance:
    def test_round_2_grid_has_renderer(self, asset_mgr):
        scene = GameScene(asset_mgr, mode_config=ModeConfig(GameMode.AVATAR))
        scene._next_round()
        assert scene.grid._renderer is not None, (
            "Grid renderer was None after _next_round() — renderer not re-applied"
        )

    def test_round_2_grid_is_avatar_renderer(self, asset_mgr):
        scene = GameScene(asset_mgr, mode_config=ModeConfig(GameMode.AVATAR))
        scene._next_round()
        assert isinstance(scene.grid._renderer, AvatarRenderer)

    def test_round_2_grid_at_2x_position(self, asset_mgr):
        scene = GameScene(asset_mgr, mode_config=ModeConfig(GameMode.AVATAR))
        scene._next_round()
        assert scene.grid.grid_x == 52
        assert scene.grid.grid_y == 128

    def test_arcade_round_2_renderer_is_pixel(self, asset_mgr):
        scene = GameScene(asset_mgr, mode_config=ModeConfig(GameMode.ARCADE))
        scene._next_round()
        assert isinstance(scene.grid._renderer, PixelRenderer)

    def test_game_over_restart_preserves_mode(self, asset_mgr):
        scene = GameScene(asset_mgr, mode_config=ModeConfig(GameMode.AVATAR))
        scene._trigger_game_over()
        # next_scene should have been set; the restart callback creates the new game
        # We test that mode_config is passed into the closure by calling make_new_game
        from space_invaders.scenes.gameover import GameOverScene
        assert isinstance(scene.next_scene, GameOverScene)
        new_game = scene.next_scene._on_restart()
        assert new_game.mode_config.mode == GameMode.AVATAR


# ---------------------------------------------------------------------------
# End-to-end geometry: player bullet can hit rightmost column
# ---------------------------------------------------------------------------


class TestAvatarBulletReachability:
    def test_bullet_x_range_covers_all_columns(self, asset_mgr, avatar_cfg):
        """Player moves across the full screen width and can aim at any column."""
        grid = InvaderGrid(asset_mgr, avatar_cfg)
        grid.set_renderer(AvatarRenderer(asset_mgr))

        # Rightmost column center x
        col10_center = grid.grid_x + 10 * 32 + 16  # = 52 + 320 + 16 = 388

        # Player right movement limit
        player = Player(asset_mgr, avatar_cfg)
        # Player can move up to right_limit - width
        player_max_right = avatar_cfg.right_limit  # 440
        player_max_centerx = player_max_right - player.rect.width // 2

        assert player_max_centerx >= col10_center, (
            f"Player can't reach column 10: player max center={player_max_centerx}, "
            f"col10 center={col10_center}"
        )

    def test_bullet_from_right_hits_col10(self, asset_mgr, avatar_cfg):
        """Bullet fired from right side of screen hits column 10."""
        grid = InvaderGrid(asset_mgr, avatar_cfg)
        grid.set_renderer(AvatarRenderer(asset_mgr))

        # Bullet at column 10 center X, row 0 center Y
        bx = grid.grid_x + 10 * 32 + 16
        by = grid.grid_y + 16
        hit = grid.invader_at(bx, by)
        assert hit is not None
        assert hit[1] == 10
