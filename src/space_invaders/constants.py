# Display
SCREEN_W = 224
SCREEN_H = 256
SCALE = 3
FPS = 60

# Grid layout
GRID_COLS = 11
GRID_ROWS = 5
CELL_W = 16   # horizontal distance between column left-edges
CELL_H = 16   # vertical distance between row top-edges

# Grid starting position (left-edge of col 0, top of row 0)
GRID_START_X = 26
GRID_START_Y = 64

# March mechanics
MARCH_STEP_X = 2    # pixels moved per horizontal march step
MARCH_STEP_Y = 8    # pixels dropped per direction reversal
MARCH_MAX_MS = 800  # step interval at 55 invaders
MARCH_MIN_MS = 50   # step interval at 1 invader remaining

# March boundary: leftmost/rightmost living invader edge must stay within these
LEFT_LIMIT = 4
RIGHT_LIMIT = 220

# Sprite dimensions (native pixels)
SPRITE_W_SQUID = 8
SPRITE_W_CRAB = 11
SPRITE_W_OCTOPUS = 12
SPRITE_H = 8
MAX_SPRITE_W = SPRITE_W_OCTOPUS  # used for boundary calculations

# Player
PLAYER_Y = 216          # y position (top edge) of player cannon
PLAYER_SPEED = 80       # pixels per second
BULLET_SPEED = 300      # pixels per second (upward)
LIVES = 3
RESPAWN_DELAY = 2.0     # seconds before player respawns after death
ROUND_CLEAR_DELAY = 1.5  # seconds to pause before advancing to next round

# Game-over line: invaders reaching this y (bottom edge) trigger game over
INVADER_KILL_LINE = PLAYER_Y

# Enemy fire
ENEMY_BULLET_SPEED = 96      # pixels per second downward
ENEMY_FIRE_MAX_MS = 1100     # fire interval at 55 invaders (ms)
ENEMY_FIRE_MIN_MS = 200      # fire interval at 1 invader (ms)
ENEMY_BULLET_MAX = 3         # max simultaneous enemy bullets on screen

# UFO
UFO_Y = 32
UFO_INTERVAL_MS = 25000
UFO_SCORE_CYCLE = [
    50, 50, 100, 150, 100, 100, 50, 300, 100, 100, 100, 50, 150, 100, 100
]

# Bunkers
BUNKER_COUNT = 4
BUNKER_W = 22
BUNKER_H = 16
BUNKER_Y = 192

# Scoring
HIGH_SCORE_MAX = 99990
SCORE_SQUID = 30
SCORE_CRAB = 20
SCORE_OCTOPUS = 10

# CRT overlay
SCANLINE_ALPHA = 102  # 40% of 255

# Row → invader type
ROW_TYPES = {0: "squid", 1: "crab", 2: "crab", 3: "octopus", 4: "octopus"}
ROW_SCORES = {
    0: SCORE_SQUID, 1: SCORE_CRAB, 2: SCORE_CRAB, 3: SCORE_OCTOPUS, 4: SCORE_OCTOPUS
}

# Colors (native palette)
COLOR_BG = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_RED = (255, 50, 50)
COLOR_YELLOW = (255, 255, 0)

# Invader type → display color
INVADER_COLORS = {
    "squid": COLOR_WHITE,
    "crab": COLOR_CYAN,
    "octopus": COLOR_GREEN,
}
