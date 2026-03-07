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

- [ ] Renders at 224×256 (original arcade resolution), scaled 3× to 672×768 for modern screens
- [ ] No interpolation/blurring on scaling (nearest-neighbor only)
- [ ] CRT scanline overlay applied at runtime
- [ ] Black background with color elements matching Deluxe color scheme

### Invader Grid

- [ ] 5 rows × 11 columns = 55 invaders at game start
- [ ] Three invader types: Squid (top row, 30 pts), Crab (middle 2 rows, 20 pts), Octopus (bottom 2 rows, 10 pts)
- [ ] Each type has 2 animation frames, alternating on each march step
- [ ] Grid marches left/right, drops one row on direction change
- [ ] March tempo accelerates as invaders are destroyed (speed tied to remaining count)
- [ ] Invaders that reach the bottom of the screen = game over

### Player Cannon

- [ ] Horizontal movement only, constrained to bottom of screen
- [ ] One active bullet on screen at a time
- [ ] 3 lives per game
- [ ] Bullet travels upward; collision detection with invaders, bunkers, UFO

### UFO / Mystery Ship

- [ ] Appears at ~25-second intervals, traverses top of screen
- [ ] Score cycles deterministically: 50/100/150/300 based on shot count
- [ ] Score value displayed briefly on hit

### Shields / Bunkers

- [ ] 4 bunkers, each 22×16 px, pixel-destructible
- [ ] Damaged by both invader fire (from above) and player fire (from below)
- [ ] Damage is persistent per level

### Invader Fire

- [ ] Invaders fire downward at player; multiple enemy bullets active simultaneously
- [ ] Fire rate increases as invader count decreases

### Scoring

- [ ] Live score display; high score tracked per session
- [ ] High score limit: 99,990 pts (Deluxe cap)
- [ ] High score initials entry on game over

### Space Invaders Deluxe-Specific Features

These features distinguish Deluxe from the original. All are required.

- [ ] **Splitting aliens:** Selected aliens split into two smaller ones when shot
- [ ] **Rainbow bonus:** 500 pts for last alien from bottom rows; 1,000 pts for last alien bottom-left
- [ ] **Stage cutscenes** between rounds (as in the original Deluxe attract/inter-round sequences)
- [ ] **Invaders change color** as they descend through rows

### Sound

- [ ] 4-note march loop (tempo increases with speed)
- [ ] Player shoot sound
- [ ] Invader killed sound
- [ ] Player death explosion sound
- [ ] UFO drone (looping while on screen)
- [ ] UFO hit sound

### Game States

- [ ] Title/attract screen
- [ ] Gameplay loop (advance rounds, track lives)
- [ ] Game over screen with high score entry
- [ ] Pause support

---

## Out of Scope (for initial release)

- Multiplayer / 2-player alternating mode
- Cabinet/MAME hardware emulation
- Network high scores
- Mobile/touch controls
- Console port accuracy (Atari 2600, etc.)
- Space Invaders (1978) or Part II (1979 JP) feature parity
