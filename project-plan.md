# Project Plan — Space Invaders Deluxe

> **Strategic roadmap** — stable, long-term planning document.
> For tactical execution, see `sprint-plan.md`. For acceptance criteria, see `product-definition.md`.

---

## Project Overview

A pixel-perfect, authentic recreation of the 1979/1980 Taito Space Invaders Deluxe arcade experience, running as a native desktop Python application.

The philosophy is **TinyClaw**: build the smallest visible slice first, get it on screen, verify it's correct, then layer in the next slice.

---

## Objectives

### Primary Objective
Ship a playable Space Invaders Deluxe clone that is indistinguishable from the original arcade cabinet in gameplay feel, timing, and visual behavior.

### Secondary Objectives
- Implement all four Deluxe-exclusive features (split aliens, rainbow bonus, cutscenes, color descent)
- Source original arcade assets (sprites, sounds) rather than generating approximations
- Produce a clean, maintainable Python codebase others could learn from
- **NEW:** Avatar Mode — modern visual reinterpretation with configurable characters

---

## Non-Negotiable Constraints

- No blurring or interpolation — nearest-neighbor scaling only (Arcade mode)
- Render target is always 224×256; never draw directly to the scaled window (Arcade mode)
- All timing values must be derived from arcade reference, not guessed
- No external runtime dependencies added without explicit human approval
- Every Deluxe-specific feature must be verified against reference footage before marking done
- **NEW:** Avatar Mode must be toggleable without code changes
- **NEW:** Avatar configuration must support external tooling (drop-in PNG replacement)

---

## Development Phases

### Phase 0 — Bootstrap

**Status:** ✅ Complete

**Goals:**
- Scaffold project structure
- Define product vision and technical design

**Deliverables:**
- ✅ `product-definition.md` — acceptance checklist
- ✅ `design.md` — technical blueprint
- ✅ `sprint-plan.md` — 11-sprint roadmap
- ✅ Skills: `arcade-accuracy.md`, `pygame-entity.md`, `playtest.md`

---

### Phase 1 — Core Engine (Sprints 1–3)

**Status:** ✅ Complete

**Goal:** A window with a live, animated invader grid. Nothing interactive yet — just proof that the rendering pipeline and asset system work.

**Core components:**
1. Window, game loop, renderer (Sprint 1)
2. Asset pipeline with fallbacks (Sprint 2)
3. Invader grid — visual only, correct march (Sprint 3)

**Success Criteria:**
- Window opens at 672×768, holds 60 fps
- All 55 invaders visible, animating, marching at correct starting tempo
- Assets load from disk or fallback procedurally — no crash on cold start

---

### Phase 2 — Playable Core (Sprints 4–6)

**Status:** ✅ Complete

**Goal:** A playable game loop — shoot invaders, die, advance rounds. Enemy fire and bunkers make it dangerous.

**Components:**
- Player movement and shooting (Sprint 4)
- Lives, round advance, game over (Sprint 5)
- Enemy fire and pixel-destructible bunkers (Sprint 6)

**Success Criteria:**
- Player can complete a full round (kill all invaders)
- Dying costs a life; game over on 0 lives or invaders reaching bottom
- Bunker erosion is pixel-level and persistent

---

### Phase 3 — Full Feature Set (Sprints 7–9)

**Status:** ✅ Complete

**Goal:** UFO, sound, and all four Deluxe-exclusive features. The game is now recognizably Space Invaders Deluxe.

**Components:**
- UFO with correct score cycle (Sprint 7)
- Sound — march tempo locked to visuals (Sprint 8)
- Split aliens, rainbow bonus, cutscenes, color descent (Sprint 9)

**Success Criteria:**
- UFO score cycle matches Deluxe `CYCLE` constant
- March audio and visual are in sync at all tempos
- All four Deluxe features work and verified against reference footage

---

### Phase 4 — Shell + Accuracy (Sprints 10–11)

**Status:** ✅ Complete

**Goal:** Complete, shippable game. Full game flow, CRT overlay, high score entry, and an accuracy pass against reference footage.

**Components:**
- Title screen, game over + initials entry, pause, CRT overlay (Sprint 10)
- Structured playtest and deviation resolution (Sprint 11)

**Success Criteria:**
- All items in `product-definition.md` checked off
- No `accuracy-bug` deviations remaining
- Game navigable end-to-end without touching code

---

### Phase 5 — Avatar Mode (Sprints 12–15)

**Status:** ⚠️ Structurally complete but has a critical coordinate bug

**Goal:** Modern visual reinterpretation with Memoji-style configurable characters. Dual-mode system lets players choose Arcade (authentic) or Avatar (modern) at startup.

**Components:**
- Mode selection system and dynamic configuration (Sprint 12) ✅
- Procedural avatar generator with placeholders (Sprint 13) ✅
- Avatar rendering pipeline and animation (Sprint 14) ✅
- Configurable character system and external tooling support (Sprint 15) ✅

**Bug Found (post-sprint-15):** Avatar mode doubled the native surface and invader cell size
but left all other gameplay coordinates (player position, march limits, bullet speed, bunker
position, UFO path) at arcade values. This causes immediate incorrect march behaviour, invaders
unreachable by the player, and the grid overlapping the player row. All are traced to a single
root cause: no `coord_scale` propagation. See `design.md` — Dual Mode System for full analysis.

**Success Criteria (incomplete — awaiting Sprint 16):**
- Title screen offers mode selection (Arcade vs Avatar) ✅
- Avatar mode: 5 distinct procedural characters, configurable via JSON ✅
- External PNG avatars can replace procedural ones without code changes ✅
- All gameplay coordinates scale correctly with resolution (Sprint 16)
- Player can reach all 11 columns of invaders (Sprint 16)
- March behaves correctly; no premature descent (Sprint 16)
- All 251 existing tests pass; avatar regression suite added (Sprint 16)

---

### Phase 6 — Avatar Mode Correctness (Sprint 16)

**Status:** 🔄 Active

**Goal:** Fix the coordinate system mismatch in Avatar mode. Every pixel position scales
with `coord_scale = 2`. All game entities receive `ModeConfig` and use it as the single
source of truth for all position and speed values.

**Root cause:** `ModeConfig` provided correct display config (448×512, 32×32 cells) but
arcade constants (`constants.py`) were still used directly by Player, BunkerGroup, UFO,
SplitAlien, InvaderGrid, GameScene, and HUD for all coordinate values.

**Components:**
- `ModeConfig` extended with all coordinate properties (Sprint 16)
- All entities refactored to accept and use `ModeConfig` (Sprint 16)
- `_next_round()` renderer reapplication bug fixed (Sprint 16)
- Avatar mode acceptance test suite (Sprint 16)

**Success Criteria:**
- All items in Avatar Mode Acceptance Tests section of `product-definition.md` checked
- Arcade mode unchanged — all pre-existing tests pass
- Avatar mode playable end-to-end: title → gameplay → round 2 → game over

---

## Risks

| Risk | Mitigation |
|------|------------|
| Deluxe sprite rips require manual sourcing | Procedural fallback ensures game always runs; revisit URLs before Sprint 2 |
| Deluxe-specific mechanics under-documented | Load `skills/arcade-accuracy.md` before implementing Sprint 9; find reference footage early |
| March timing drift between audio and visual | Design locks them to same interval; verify in Sprint 8 with structured playtest |
| "Close enough" accuracy creep | `skills/arcade-accuracy.md` is mandatory before any mechanic is marked done |
| **NEW:** Avatar mode breaks arcade mode | Strict separation: ModeConfig for display, shared logic for gameplay; test both modes every sprint |
| **NEW:** External avatar images don't fit | Document requirements; provide template; procedural fallback on load failure |
| **NEW:** Procedural avatars look unprofessional | Style guide in design.md; placeholders are functional, not final art |

---

## Success Metrics

- Every checkbox in `product-definition.md` is ticked
- Side-by-side comparison with reference footage shows no visible timing or scoring deviation
- `space-invaders` launches, plays, and exits without error on a clean install
- **NEW:** Mode selection works, both modes playable
- **NEW:** Avatar configuration file can be edited without restarting game (per round)

---

## Current Status

**Phase:** Phase 6 — Avatar Mode Correctness
**Active Sprint:** Sprint 16 — Coordinate System Fix
**Next Milestone:** Avatar Mode fully playable and correct

**Game Status:** ✅ Arcade mode shippable. ⚠️ Avatar mode has critical coordinate bug (Sprint 16).

---

## Post-Release Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| 0-4 | Core arcade game | ✅ Complete |
| 5 | Avatar Mode (structure) | ✅ Complete (Sprints 12-15) |
| 6 | Avatar Mode Correctness | 🔄 Active (Sprint 16) |
| 7 | Polish & Balance | 📋 Future (difficulty curves, power-ups?) |
| 8 | Platform ports | 📋 Future (web, mobile) |

---

*Update this file only when phases complete or strategic direction changes. For daily state, see `context.md`.*
