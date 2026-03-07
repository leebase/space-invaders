"""Entry point — window init, asset bootstrap, game loop.

Usage:
    space-invaders
"""

import sys

import pygame

from . import constants
from .assets import ensure_assets
from .renderer import Renderer
from .scenes.title import TitleScene


def main() -> None:
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    renderer = Renderer()
    asset_mgr = ensure_assets()

    scene = TitleScene(asset_mgr)

    clock = pygame.time.Clock()
    running = True

    while running:
        # dt capped at 100 ms to avoid spiral-of-death on tab-switch
        dt = min(clock.tick(constants.FPS) / 1000.0, 0.1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_ESCAPE:
                    # Allow scenes to handle Esc first (e.g., pause)
                    scene.handle_event(event)
                    # If not handled by scene, quit only if not in gameplay
                    if hasattr(scene, '_state') and scene._state.name == 'PAUSED':
                        pass  # Esc unpauses, don't quit
                    elif isinstance(scene, TitleScene):
                        running = False
                else:
                    scene.handle_event(event)
            else:
                scene.handle_event(event)

        scene.update(dt)

        # Scene transition requested by current scene
        if scene.next_scene is not None:
            scene = scene.next_scene

        scene.draw(renderer.surface)
        renderer.present()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
