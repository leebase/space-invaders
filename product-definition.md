# Product Definition — Space Invaders Deluxe

> **What done looks like.** This is the acceptance checklist. No feature ships without a corresponding item here, and no item here is optional unless marked Out of Scope.

---

## Vision

A pixel-perfect, authentic recreation of the 1979/1980 Taito Space Invaders Deluxe arcade experience, running as a native desktop application.

**Target hardware reference:** Taito Space Invaders Deluxe (1980 upright cabinet)
**NOT:** Space Invaders (1978), Space Invaders Part II (1979 Japan-only), or any console port.

---

## Done = All of the following are true

### Display

- [x] Renders at 224×256 (original arcade resolution), scaled 3× to 672×768 for modern screens
- [x] No interpolation/blurring on scaling (nearest-neighbor only)
- [x] CRT scanline overlay applied at runtime
- [x] Black background with color elements matching Deluxe color scheme

### Invader Grid

- [x] 5 rows × 11 columns = 55 invaders at game start
- [x] Three invader types: Squid (top row, 30 pts), Crab (middle 2 rows, 20 pts), Octopus (bottom 2 rows, 10 pts)
- [x] Each type has 2 animation frames, alternating on each march step
- [x] Grid marches left/right, drops one row on direction change
- [x] March tempo accelerates as invaders are destroyed (speed tied to remaining count)
- [x] Invaders that reach the bottom of the screen = game over

### Player Cannon

- [x] Horizontal movement only, constrained to bottom of screen
- [x] One active bullet on screen at a time
- [x] 3 lives per game
- [x] Bullet travels upward; collision detection with invaders, bunkers, UFO

### UFO / Mystery Ship

- [x] Appears at ~25-second intervals, traverses top of screen
- [x] Score cycles deterministically: 50/100/150/300 based on shot count
- [x] Score value displayed briefly on hit

### Shields / Bunkers

- [x] 4 bunkers, each 22×16 px, pixel-destructible
- [x] Damaged by both invader fire (from above) and player fire (from below)
- [x] Damage is persistent per level

### Invader Fire

- [x] Invaders fire downward at player; multiple enemy bullets active simultaneously
- [x] Fire rate increases as invader count decreases

### Scoring

- [x] Live score display; high score tracked per session
- [x] High score limit: 99,990 pts (Deluxe cap)
- [x] High score initials entry on game over

### Space Invaders Deluxe-Specific Features

These features distinguish Deluxe from the original. All are required.

- [x] **Splitting aliens:** Selected aliens split into two smaller ones when shot
- [x] **Rainbow bonus:** 500 pts for last alien from bottom rows; 1,000 pts for last alien bottom-left
- [x] **Stage cutscenes** between rounds (as in the original Deluxe attract/inter-round sequences)
- [x] **Invaders change color** as they descend through rows

### Sound

- [x] 4-note march loop (tempo increases with speed)
- [x] Player shoot sound
- [x] Invader killed sound
- [x] Player death explosion sound
- [x] UFO drone (looping while on screen)
- [x] UFO hit sound

### Game States

- [x] Title/attract screen
- [x] Gameplay loop (advance rounds, track lives)
- [x] Game over screen with high score entry
- [x] Pause support

---

## Avatar Mode (Post-Arcade Feature)

A modern visual reinterpretation with Memoji-style human characters instead of pixel aliens.
All gameplay mechanics (timing, scoring, collision, rules) are identical to Arcade mode.
Only the coordinate scale and visual rendering differ.

### Display (Avatar Mode)

- [x] Renders at 448×512 (2× arcade resolution), scaled 2× to 896×1024
- [x] Smooth scaling (interpolation enabled for photo-style avatars)
- [x] No CRT scanline overlay (clean modern look)
- [ ] Black background with subtle gradient (deferred — low priority)

### Avatar Grid

- [x] 5 rows × 11 columns = 55 avatars at game start
- [x] Configurable avatar set: 5 distinct Memoji-style characters
- [x] Characters procedurally generated (skin tones, hair, expressions)
- [x] Subtle bounce animation instead of pixel frame swap
- [x] Characters show "concern" expression as they descend lower rows
- [x] March mechanics correct in Avatar mode — march boundaries, step size, and descent all 2× arcade values
- [x] All 11 columns reachable by player bullet
- [x] Invaders respond to being shot in all columns
- [x] Grid correct after round advance (renderer reapplied on new round)

### Configurable Characters

- [x] JSON configuration file for avatar definitions
- [x] Per-character attributes: skin color, hair color, hair style, shirt color, expression set
- [x] 5 default characters provided as placeholders
- [x] Characters map to grid rows (row 0 = top character, row 4 = bottom character)
- [ ] Hot-reload: configuration changes detected at round start (deferred)

### Avatar Assets

- [x] Procedural generation as fallback/default
- [x] External image support: `assets/avatars/` folder
- [x] Naming convention: `avatar_{row}.png`
- [x] Images scaled to fit 32×32 cell size
- [x] Alpha channel support for transparent backgrounds

### Mode Selection

- [x] Title screen menu: "ARCADE MODE" vs "AVATAR MODE"
- [ ] Keyboard navigation (up/down/enter)
- [ ] Mode persisted per session (default to Arcade)
- [ ] Both modes share high score table

### Avatar Mode Acceptance Tests

- [x] Player can shoot invaders in all 11 columns
- [x] March stays within screen bounds and never triggers premature descent
- [x] Grid survives to round 2 with avatar renderer intact
- [x] Player, bunkers, UFO, and ground line all correctly positioned at 2× coordinates
- [x] Arcade mode is unaffected by all Avatar mode changes

---

## Out of Scope (for initial release)

- Multiplayer / 2-player alternating mode
- Cabinet/MAME hardware emulation
- Network high scores
- Mobile/touch controls
- Console port accuracy (Atari 2600, etc.)
- Space Invaders (1978) or Part II (1979 JP) feature parity
- Real-time avatar customization UI (config file only)
- Avatar animation beyond bounce/expression

---

## Asset Pipeline for Avatar Mode

```
assets/
├── avatars/
│   ├── config.json          # Character definitions (or use defaults)
│   ├── avatar_0.png         # Optional: external image overrides
│   ├── avatar_1.png
│   ├── avatar_2.png
│   ├── avatar_3.png
│   └── avatar_4.png
└── (existing sprites/ folder for Arcade mode)
```

### Configuration Schema (config.json)

```json
{
  "version": 1,
  "characters": [
    {
      "name": "The Executive",
      "row": 0,
      "procedural": {
        "skin": [255, 220, 177],
        "hair": [80, 60, 40],
        "hair_style": "slick",
        "shirt": [0, 100, 200],
        "expression": "serious"
      }
    },
    {
      "name": "The Politician",
      "row": 1,
      "procedural": { ... }
    }
  ]
}
```

*Note: If `config.json` is missing or invalid, fallback to hardcoded procedural defaults.*
