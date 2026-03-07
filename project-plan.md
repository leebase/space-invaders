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

---

## Non-Negotiable Constraints

- No blurring or interpolation — nearest-neighbor scaling only
- Render target is always 224×256; never draw directly to the scaled window
- All timing values must be derived from arcade reference, not guessed
- No external runtime dependencies added without explicit human approval
- Every Deluxe-specific feature must be verified against reference footage before marking done

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

**Goal:** Complete, shippable game. Full game flow, CRT overlay, high score entry, and an accuracy pass against reference footage.

**Components:**
- Title screen, game over + initials entry, pause, CRT overlay (Sprint 10)
- Structured playtest and deviation resolution (Sprint 11)

**Success Criteria:**
- All items in `product-definition.md` checked off
- No `accuracy-bug` deviations remaining
- Game navigable end-to-end without touching code

---

## Risks

| Risk | Mitigation |
|------|------------|
| Deluxe sprite rips require manual sourcing | Procedural fallback ensures game always runs; revisit URLs before Sprint 2 |
| Deluxe-specific mechanics under-documented | Load `skills/arcade-accuracy.md` before implementing Sprint 9; find reference footage early |
| March timing drift between audio and visual | Design locks them to same interval; verify in Sprint 8 with structured playtest |
| "Close enough" accuracy creep | `skills/arcade-accuracy.md` is mandatory before any mechanic is marked done |

---

## Success Metrics

- Every checkbox in `product-definition.md` is ticked
- Side-by-side comparison with reference footage shows no visible timing or scoring deviation
- `space-invaders` launches, plays, and exits without error on a clean install

---

## Current Status

**Phase:** Phase 1 — Core Engine
**Active Sprint:** Sprint 1 — Project Skeleton
**Next Milestone:** Window opens at 672×768, 60 fps, black screen, clean exit

---

*Update this file only when phases complete or strategic direction changes. For daily state, see `context.md`.*
