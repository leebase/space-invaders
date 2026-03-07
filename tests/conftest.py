"""Shared pytest fixtures — headless pygame init for all tests."""

import os

import pygame
import pytest


@pytest.fixture(scope="session", autouse=True)
def headless_pygame():
    """Initialise pygame with dummy video/audio drivers for all tests."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))  # required for convert_alpha()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    yield
    pygame.quit()
