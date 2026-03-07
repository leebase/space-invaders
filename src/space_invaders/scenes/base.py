"""Abstract Scene base class."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class Scene(ABC):
    # Set to a new Scene instance to trigger a scene transition in main.py.
    next_scene: "Scene | None" = None

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance game logic. dt is elapsed seconds since last frame."""

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw to the 224×256 native surface."""

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event. Override as needed."""
