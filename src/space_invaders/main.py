"""Entry point — window init, asset bootstrap, game loop.

Usage:
    space-invaders
"""

import sys

import pygame

from . import constants
from .assets import ensure_assets
from .renderer import Renderer
from .scenes.game import GameScene


def main() -> None:
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    renderer = Renderer()
    asset_mgr = ensure_assets()

    scene = GameScene(asset_mgr)

    clock = pygame.time.Clock()
    running = True

    while running:
        # dt capped at 100 ms to avoid spiral-of-death on tab-switch
        dt = min(clock.tick(constants.FPS) / 1000.0, 0.1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                else:
                    scene.handle_event(event)
            else:
                scene.handle_event(event)

        scene.update(dt)

        renderer.clear()
        scene.draw(renderer.surface)
        renderer.present()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
