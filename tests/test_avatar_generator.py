"""Tests for procedural avatar generator."""

import pygame
import pytest

from space_invaders.avatar_config import AvatarConfig, CharacterDef
from space_invaders.avatar_generator import AvatarGenerator


@pytest.fixture
def generator():
    return AvatarGenerator()


@pytest.fixture
def config():
    return AvatarConfig()


class TestAvatarGeneratorBasics:
    """Tests for basic avatar generation."""

    def test_generator_creates_surface(self, generator, config):
        char = config.get_character(0)
        surface = generator.generate(char, size=32)
        
        assert isinstance(surface, pygame.Surface)
        assert surface.get_width() == 32
        assert surface.get_height() == 32

    def test_surface_has_alpha(self, generator, config):
        char = config.get_character(0)
        surface = generator.generate(char, size=32)
        
        # Check surface has alpha channel
        assert surface.get_flags() & pygame.SRCALPHA

    def test_different_sizes(self, generator, config):
        char = config.get_character(0)
        
        surf_32 = generator.generate(char, size=32)
        surf_64 = generator.generate(char, size=64)
        
        assert surf_32.get_size() == (32, 32)
        assert surf_64.get_size() == (64, 64)

    def test_different_characters_produce_different_surfaces(self, generator, config):
        char0 = config.get_character(0)
        char4 = config.get_character(4)
        
        surf0 = generator.generate(char0, size=32)
        surf4 = generator.generate(char4, size=32)
        
        # Different colors should produce different pixel data
        # Convert to bytes for comparison
        bytes0 = pygame.image.tostring(surf0, "RGBA")
        bytes4 = pygame.image.tostring(surf4, "RGBA")
        
        assert bytes0 != bytes4


class TestAvatarComponents:
    """Tests for individual avatar components."""

    def test_face_is_drawn(self, generator, config):
        char = CharacterDef(
            name="Test",
            row=0,
            skin=(255, 0, 0),  # Bright red for visibility
            hair=(0, 0, 0),
            hair_style="bald",  # No hair to obscure face
            shirt=(0, 0, 0),
            expression="serious",
        )
        
        surface = generator.generate(char, size=32)
        # Check that center has red pixels (the face)
        center_color = surface.get_at((16, 16))
        assert center_color.r > 200  # Should be mostly red

    def test_shirt_is_drawn(self, generator, config):
        char = CharacterDef(
            name="Test",
            row=0,
            skin=(100, 100, 100),
            hair=(0, 0, 0),
            hair_style="bald",
            shirt=(0, 255, 0),  # Bright green shirt
            expression="serious",
        )

        surface = generator.generate(char, size=32)
        # Check bottom area has green pixels (the shirt)
        # Shirt is drawn with the exact color, but darker line may be on top
        # Check multiple points to find the shirt color
        has_green = False
        for y in range(24, 31):  # Bottom area
            for x in range(8, 24):  # Center horizontal
                color = surface.get_at((x, y))
                if color.g > 100 and color.r < 50 and color.b < 50:
                    has_green = True
                    break
            if has_green:
                break
        assert has_green, "Should find green shirt pixels in bottom area"

    def test_hair_styles(self, generator):
        """Test that different hair styles produce different results."""
        base_char = CharacterDef(
            name="Test",
            row=0,
            skin=(200, 150, 100),
            hair=(50, 50, 50),
            hair_style="bald",
            shirt=(100, 100, 100),
            expression="neutral",
        )
        
        styles = ["bald", "messy", "slick", "formal", "spiky", "casual"]
        surfaces = {}
        
        for style in styles:
            char = CharacterDef(
                name="Test",
                row=0,
                skin=(200, 150, 100),
                hair=(50, 50, 50),
                hair_style=style,
                shirt=(100, 100, 100),
                expression="neutral",
            )
            surfaces[style] = pygame.image.tostring(
                generator.generate(char, size=32), "RGBA"
            )
        
        # Bald should be different from all others (no hair drawn)
        for style in ["messy", "slick", "formal", "spiky", "casual"]:
            assert surfaces["bald"] != surfaces[style], f"{style} should differ from bald"

    def test_expressions(self, generator):
        """Test that different expressions produce different results."""
        expressions = ["serious", "smirk", "neutral", "worried", "panic"]
        surfaces = {}
        
        for expr in expressions:
            char = CharacterDef(
                name="Test",
                row=0,
                skin=(200, 150, 100),
                hair=(50, 50, 50),
                hair_style="bald",
                shirt=(100, 100, 100),
                expression=expr,
            )
            surfaces[expr] = pygame.image.tostring(
                generator.generate(char, size=32), "RGBA"
            )
        
        # All expressions should produce different results
        # (At minimum, panic with open mouth should differ from serious)
        assert surfaces["serious"] != surfaces["panic"]
        assert surfaces["worried"] != surfaces["smirk"]


class TestAvatarEdgeCases:
    """Tests for edge cases."""

    def test_very_small_size(self, generator, config):
        """Generator should handle small sizes gracefully."""
        char = config.get_character(0)
        surface = generator.generate(char, size=16)
        assert surface.get_size() == (16, 16)

    def test_large_size(self, generator, config):
        """Generator should handle large sizes."""
        char = config.get_character(0)
        surface = generator.generate(char, size=128)
        assert surface.get_size() == (128, 128)

    def test_all_default_characters_generate(self, generator, config):
        """All 5 default characters should generate without error."""
        for row in range(5):
            char = config.get_character(row)
            surface = generator.generate(char, size=32)
            assert surface is not None
            assert surface.get_size() == (32, 32)
