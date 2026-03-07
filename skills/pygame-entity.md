# Skill: Pygame Entity Implementation

**Trigger:** Implementing any new game entity (invader, player, UFO, bunker, bullet, or similar).

> All entities follow the same structural contract. This skill ensures consistency, correct scene registration, and no missed integration points.

---

## Step 1 — Locate the correct file

| Entity | File |
|--------|------|
| InvaderGrid | `src/space-invaders/entities/grid.py` |
| Player | `src/space-invaders/entities/player.py` |
| UFO | `src/space-invaders/entities/ufo.py` |
| Bunker / BunkerGroup | `src/space-invaders/entities/bunker.py` |
| Bullet | `src/space-invaders/entities/bullet.py` |
| New entity | Create in `src/space-invaders/entities/`, register in `__init__.py` |

---

## Step 2 — Implement the standard interface

Every entity must implement this contract:

```python
class EntityName:
    def __init__(self, ...):
        # Load sprite(s) via AssetManager — never hardcode paths
        # Set initial position in native (224×256) coordinates
        # Set up any internal state (timers, counters, flags)
        pass

    def update(self, dt: float) -> None:
        # dt is elapsed seconds since last frame (from fixed 60fps loop)
        # All movement/timing must be dt-based, never frame-count-based
        pass

    def draw(self, surface: pygame.Surface) -> None:
        # surface is the 224×256 native surface, not the scaled window
        # All coordinates are in native pixels
        pass
```

**Never** blit to the window surface directly. Always draw to the 224×256 `surface` passed in.

---

## Step 3 — Sprite loading checklist

- [ ] Load sprite via `AssetManager`, not a raw path string
- [ ] Use `pygame.transform.scale` (not `smoothscale`) if resizing
- [ ] For animated sprites: store frames as a list, advance frame index on march step / timer
- [ ] For pixel-art sprites: confirm `convert()` or `convert_alpha()` is called after load (perf)

```python
# Correct sprite load pattern
frames = asset_manager.load_sprite_frames("invader_squid")  # returns List[pygame.Surface]
self.frame_index = 0

# Advance animation (call in update, not every frame — only on march step)
self.frame_index = (self.frame_index + 1) % len(self.frames)
```

---

## Step 4 — Scene registration checklist

After implementing the entity, verify it is wired into `GameScene`:

- [ ] Entity instantiated in `GameScene.__init__()`
- [ ] `entity.update(dt)` called in `GameScene.update(dt)`
- [ ] `entity.draw(surface)` called in `GameScene.draw(surface)` in correct Z-order
- [ ] Collision with bullets registered in `BulletManager` or handled in `GameScene.update()`
- [ ] Entity exposes a `rect` or `mask` for collision (use `pygame.Rect` at minimum)

**Z-order (back to front):**
1. Bunkers
2. Invader grid
3. UFO
4. Player
5. Bullets (player + enemy)
6. HUD (drawn last, always on top)

---

## Step 5 — Bunker special case

Bunkers use pixel-level destruction via `pygame.surfarray`. Use this pattern:

```python
import numpy as np
import pygame

class Bunker:
    def __init__(self, x: int, y: int, asset_manager):
        sprite = asset_manager.load_sprite("bunker")
        self.surface = sprite.copy().convert_alpha()
        self.pixel_array = pygame.surfarray.pixels_alpha(self.surface)
        # pixel_array is a live view — writes go directly to the surface
        self.rect = self.surface.get_rect(topleft=(x, y))

    def apply_damage(self, hit_x: int, hit_y: int, radius: int = 3) -> None:
        # Convert to local coordinates
        lx = hit_x - self.rect.x
        ly = hit_y - self.rect.y
        # Zero out pixels in radius (set alpha to 0)
        x0 = max(0, lx - radius)
        x1 = min(self.pixel_array.shape[0], lx + radius)
        y0 = max(0, ly - radius)
        y1 = min(self.pixel_array.shape[1], ly + radius)
        self.pixel_array[x0:x1, y0:y1] = 0
```

---

## Step 6 — Run arcade-accuracy check

Before marking the entity implementation done, load `skills/arcade-accuracy.md` and run through the relevant sections.
