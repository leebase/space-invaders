"""Tests for GameMode and ModeConfig."""

import pytest

from space_invaders.mode import GameMode, ModeConfig


class TestGameMode:
    """Tests for GameMode enum."""

    def test_arcade_mode_exists(self):
        assert GameMode.ARCADE is not None

    def test_avatar_mode_exists(self):
        assert GameMode.AVATAR is not None

    def test_modes_are_distinct(self):
        assert GameMode.ARCADE != GameMode.AVATAR


class TestModeConfigArcade:
    """Tests for ModeConfig in ARCADE mode."""

    @pytest.fixture
    def config(self):
        return ModeConfig(GameMode.ARCADE)

    def test_arcade_screen_dimensions(self, config):
        assert config.screen_w == 224
        assert config.screen_h == 256

    def test_arcade_scale(self, config):
        assert config.scale == 3

    def test_arcade_cell_size(self, config):
        assert config.cell_w == 16
        assert config.cell_h == 16

    def test_arcade_crt_enabled(self, config):
        assert config.crt_enabled is True

    def test_arcade_nearest_neighbor_scaling(self, config):
        assert config.smooth_scale is False

    def test_arcade_bunker_dimensions(self, config):
        assert config.bunker_w == 22
        assert config.bunker_h == 16

    def test_arcade_mode_attribute(self, config):
        assert config.mode == GameMode.ARCADE


class TestModeConfigAvatar:
    """Tests for ModeConfig in AVATAR mode."""

    @pytest.fixture
    def config(self):
        return ModeConfig(GameMode.AVATAR)

    def test_avatar_screen_dimensions(self, config):
        assert config.screen_w == 448
        assert config.screen_h == 512

    def test_avatar_scale(self, config):
        assert config.scale == 2

    def test_avatar_cell_size(self, config):
        assert config.cell_w == 32
        assert config.cell_h == 32

    def test_avatar_crt_disabled(self, config):
        assert config.crt_enabled is False

    def test_avatar_smooth_scaling(self, config):
        assert config.smooth_scale is True

    def test_avatar_bunker_dimensions(self, config):
        assert config.bunker_w == 44
        assert config.bunker_h == 32

    def test_avatar_mode_attribute(self, config):
        assert config.mode == GameMode.AVATAR


class TestModeConfigDefaults:
    """Tests for ModeConfig default behavior."""

    def test_none_defaults_to_arcade(self):
        """Passing None should default to ARCADE mode."""
        config = ModeConfig(None)  # type: ignore
        assert config.mode == GameMode.ARCADE
        assert config.screen_w == 224
