"""Inter-round cutscene. Implemented in Sprint 9."""

from __future__ import annotations

import pygame
from .base import Scene
from ..assets import AssetManager


class CutsceneScene(Scene):
    def __init__(self, asset_mgr: AssetManager, on_complete: object = None):
        self._on_complete = on_complete

    def update(self, dt: float) -> None:
        pass  # Sprint 9

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))  # Sprint 9
