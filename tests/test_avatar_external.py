"""Tests for external avatar image loading."""

import pygame
import pytest

from space_invaders.avatar_config import AvatarConfig
from space_invaders.avatar_generator import AvatarGenerator


class TestExternalAvatarLoading:
    """Tests for loading external PNG avatars."""

    @pytest.fixture
    def generator(self):
        return AvatarGenerator()

    @pytest.fixture
    def config(self):
        return AvatarConfig()

    def test_uses_procedural_when_no_external_file(self, generator, config, tmp_path, monkeypatch):
        """When external file doesn't exist, use procedural generation."""
        monkeypatch.setattr(generator, "EXTERNAL_DIR", tmp_path)
        
        char = config.get_character(0)
        surf = generator.generate(char, size=32)
        
        assert surf is not None
        assert surf.get_size() == (32, 32)

    def test_loads_external_file_when_present(
        self, generator, config, tmp_path, monkeypatch
    ):
        """When external file exists, load it instead of procedural."""
        # Create a test external image
        external_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        external_surf.fill((255, 0, 0, 255))  # Red
        
        # Save to temp directory
        avatar_path = tmp_path / "avatar_0.png"
        pygame.image.save(external_surf, str(avatar_path))
        
        monkeypatch.setattr(generator, "EXTERNAL_DIR", tmp_path)
        
        char = config.get_character(0)
        result = generator.generate(char, size=32)
        
        # Should be red (external), not skin tone (procedural)
        assert result.get_at((16, 16)).r == 255
        assert result.get_at((16, 16)).g == 0

    def test_scales_external_image_to_size(
        self, generator, config, tmp_path, monkeypatch
    ):
        """External images with wrong size are scaled."""
        # Create a test external image with wrong size
        external_surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        external_surf.fill((0, 255, 0, 255))  # Green
        
        avatar_path = tmp_path / "avatar_0.png"
        pygame.image.save(external_surf, str(avatar_path))
        
        monkeypatch.setattr(generator, "EXTERNAL_DIR", tmp_path)
        
        char = config.get_character(0)
        result = generator.generate(char, size=32)
        
        # Should be scaled to 32x32
        assert result.get_size() == (32, 32)

    def test_fallback_on_corrupt_image(
        self, generator, config, tmp_path, monkeypatch, caplog
    ):
        """When external file is corrupt, fall back to procedural."""
        # Create a corrupt "image" file
        avatar_path = tmp_path / "avatar_0.png"
        avatar_path.write_text("not a valid image")
        
        monkeypatch.setattr(generator, "EXTERNAL_DIR", tmp_path)
        
        char = config.get_character(0)
        result = generator.generate(char, size=32)
        
        # Should still get a valid surface (procedural fallback)
        assert result is not None
        assert result.get_size() == (32, 32)

    def test_different_rows_load_different_files(
        self, generator, config, tmp_path, monkeypatch
    ):
        """Different rows load different external files."""
        # Create different colored images for rows 0 and 1
        red_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        red_surf.fill((255, 0, 0, 255))
        pygame.image.save(red_surf, str(tmp_path / "avatar_0.png"))
        
        blue_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        blue_surf.fill((0, 0, 255, 255))
        pygame.image.save(blue_surf, str(tmp_path / "avatar_1.png"))
        
        monkeypatch.setattr(generator, "EXTERNAL_DIR", tmp_path)
        
        char0 = config.get_character(0)
        char1 = config.get_character(1)
        
        result0 = generator.generate(char0, size=32)
        result1 = generator.generate(char1, size=32)
        
        # Row 0 should be red, Row 1 should be blue
        assert result0.get_at((16, 16)).r == 255
        assert result1.get_at((16, 16)).b == 255
