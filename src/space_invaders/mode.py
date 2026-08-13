"""Game mode configuration for Space Invaders.

Both modes share gameplay rules (scoring, timing, lives). All pixel positions
and speeds scale by coord_scale (1 for ARCADE, 2 for AVATAR), keeping geometry
proportionally identical across resolutions.
"""

from enum import Enum, auto


class GameMode(Enum):
    """Enumeration of available game modes.

    - ARCADE: Original arcade-style gameplay with pixel art and CRT effects
    - AVATAR: Enhanced mode with Memoji-style avatars at 2x resolution
    """
    ARCADE = auto()
    AVATAR = auto()


class ModeConfig:
    """Mode-dependent display and gameplay configuration.

    ModeConfig is the single source of truth for all pixel positions and speeds.
    Game entities must read position/speed values from here, not from constants.py.

    Timing values (march intervals, fire rate, etc.) are NOT scaled — they are
    expressed in milliseconds/seconds and are mode-independent.
    """

    def __init__(self, mode: GameMode | None = None) -> None:
        self.mode = mode if mode is not None else GameMode.ARCADE
        cs = 2 if self.mode == GameMode.AVATAR else 1

        # --- Display ---
        self.coord_scale  = cs
        self.screen_w     = 224 * cs
        self.screen_h     = 256 * cs
        self.scale        = 3 if cs == 1 else 2   # window scale factor
        self.cell_w       = 16 * cs
        self.cell_h       = 16 * cs
        self.crt_enabled  = (cs == 1)
        self.smooth_scale = (cs == 2)

        # --- Grid march coordinates ---
        self.grid_start_x = 26  * cs
        self.grid_start_y = 64  * cs
        self.left_limit   = 4   * cs
        self.right_limit  = 220 * cs
        self.march_step_x = 2   * cs
        self.march_step_y = 8   * cs

        # --- Player ---
        self.player_y           = 216 * cs   # top edge of player sprite
        self.player_speed       = 80  * cs   # px/s; proportional feel at any res
        self.bullet_speed       = 300 * cs   # px/s upward
        self.enemy_bullet_speed = 96  * cs   # px/s downward

        # --- Bunkers ---
        self.bunker_y = 192 * cs
        self.bunker_w = 22  * cs
        self.bunker_h = 16  * cs

        # --- UFO ---
        self.ufo_y     = 32 * cs
        self.ufo_speed = 80 * cs

        # --- Game-over kill line ---
        self.invader_kill_line = 216 * cs

        # --- Split alien (Deluxe feature) ---
        self.split_alien_y          = 100 * cs
        self.split_alien_speed      = 60  * cs
        self.split_alien_zigzag_amp = 12  * cs
        self.split_piece_speed      = 70  * cs
