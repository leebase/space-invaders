"""Tests for avatar configuration loading."""

import json
from pathlib import Path

import pytest

from space_invaders.avatar_config import AvatarConfig, CharacterDef


class TestCharacterDef:
    """Tests for CharacterDef dataclass."""

    def test_character_def_creation(self):
        char = CharacterDef(
            name="Test",
            row=0,
            skin=(255, 200, 150),
            hair=(50, 50, 50),
            hair_style="slick",
            shirt=(100, 100, 100),
            expression="serious",
        )
        assert char.name == "Test"
        assert char.row == 0
        assert char.skin == (255, 200, 150)


class TestAvatarConfigDefaults:
    """Tests for default character configuration."""

    @pytest.fixture
    def config(self):
        return AvatarConfig()

    def test_has_five_default_characters(self, config):
        assert len(config.characters) == 5

    def test_default_character_rows_are_sequential(self, config):
        rows = [c.row for c in config.characters]
        assert rows == [0, 1, 2, 3, 4]

    def test_get_character_by_row(self, config):
        char = config.get_character(0)
        assert char.row == 0
        assert char.name == "The Executive"

    def test_get_character_row_4(self, config):
        char = config.get_character(4)
        assert char.row == 4
        assert char.name == "The Intern"

    def test_characters_property_returns_copy(self, config):
        chars1 = config.characters
        chars2 = config.characters
        assert chars1 is not chars2
        assert chars1 == chars2


class TestAvatarConfigFileLoading:
    """Tests for loading configuration from JSON file."""

    def test_loads_from_config_json_if_exists(self, tmp_path, monkeypatch):
        # Create a temporary config
        config_data = {
            "version": 1,
            "characters": [
                {
                    "name": "Custom",
                    "row": 0,
                    "procedural": {
                        "skin": [100, 100, 100],
                        "hair": [200, 200, 200],
                        "hair_style": "bald",
                        "shirt": [50, 50, 50],
                        "expression": "neutral",
                    },
                }
            ],
        }
        
        # Create temp config file
        avatars_dir = tmp_path / "assets" / "avatars"
        avatars_dir.mkdir(parents=True)
        config_file = avatars_dir / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        # Monkeypatch the CONFIG_PATH
        monkeypatch.setattr(AvatarConfig, "CONFIG_PATH", config_file)
        
        config = AvatarConfig()
        char = config.get_character(0)
        assert char.name == "Custom"
        assert char.skin == (100, 100, 100)
        assert char.hair_style == "bald"

    def test_falls_back_to_defaults_on_invalid_json(self, tmp_path, monkeypatch, capsys):
        # Create invalid config file
        avatars_dir = tmp_path / "assets" / "avatars"
        avatars_dir.mkdir(parents=True)
        config_file = avatars_dir / "config.json"
        config_file.write_text("not valid json")
        
        monkeypatch.setattr(AvatarConfig, "CONFIG_PATH", config_file)
        
        config = AvatarConfig()
        # Should fallback to defaults
        assert len(config.characters) == 5
        
        # Should print warning
        captured = capsys.readouterr()
        assert "Failed to load avatar config" in captured.out

    def test_falls_back_to_defaults_on_missing_file(self, tmp_path, monkeypatch):
        # Point to non-existent file
        config_file = tmp_path / "nonexistent" / "config.json"
        monkeypatch.setattr(AvatarConfig, "CONFIG_PATH", config_file)
        
        config = AvatarConfig()
        # Should use defaults
        assert len(config.characters) == 5
        assert config.get_character(0).name == "The Executive"


class TestCharacterAttributes:
    """Tests for character attribute validation."""

    @pytest.fixture
    def config(self):
        return AvatarConfig()

    def test_executive_attributes(self, config):
        char = config.get_character(0)
        assert char.name == "The Executive"
        assert char.expression == "serious"
        assert char.hair_style == "slick"

    def test_politician_attributes(self, config):
        char = config.get_character(1)
        assert char.name == "The Politician"
        assert char.expression == "smirk"
        assert char.hair_style == "formal"

    def test_pundit_attributes(self, config):
        char = config.get_character(2)
        assert char.name == "The Pundit"
        assert char.expression == "neutral"
        assert char.hair_style == "messy"

    def test_analyst_attributes(self, config):
        char = config.get_character(3)
        assert char.name == "The Analyst"
        assert char.expression == "worried"

    def test_intern_attributes(self, config):
        char = config.get_character(4)
        assert char.name == "The Intern"
        assert char.expression == "panic"
