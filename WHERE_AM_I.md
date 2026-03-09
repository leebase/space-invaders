# WHERE_AM_I — space-invaders

> **Product-level orientation.** Where does this project stand against its goals?
>
> This file tracks progress toward the product vision. For session-level context (what was I working on?), see `context.md`.

---

## Project Health

| Attribute | Value |
|-----------|-------|
| **Project** | space-invaders |
| **Profile** | Python Package |
| **Current Phase** | Phase 5 — Avatar Mode Complete |
| **Overall Status** | 🟡 Level 2 bugs fixed (UFO drone, cutscene scale, march boundary) — 277 tests pass |
| **Last Updated** | 2026-03-09 |

---

## Progress Against Product Goals

> Reference: `product-definition.md` for full success criteria.

### MVP Criteria — ALL COMPLETE

| Criterion | Status | Notes |
|-----------|--------|-------|
| Invader grid marching | ✅ Done | Sprint 3 |
| Player movement + bullet | ✅ Done | Sprint 4 |
| Collision detection + scoring | ✅ Done | Sprint 4 |
| Lives, round advance, game over | ✅ Done | Sprint 5 |
| Enemy fire + bunkers | ✅ Done | Sprint 6 |
| UFO — spawn, traverse, score cycle | ✅ Done | Sprint 7 |
| Sound | ✅ Done | Sprint 8 — 4-note march, all effects, UFO drone, mute |
| Deluxe-specific features (split, rainbow, cutscenes) | ✅ Done | Sprint 9 |
| Title screen, pause, initials entry | ✅ Done | Sprint 10 |
| CRT scanline overlay | ✅ Done | Sprint 10 |
| Basic documentation | ✅ Done | product-definition.md + design.md |

### Current Phase Goals

| Goal | Status | Notes |
|------|--------|-------|
| All features implemented | ✅ Done | 203 tests pass |
| All product-definition items checked | ✅ Done | 39/39 items complete |
| Final accuracy pass | ✅ Done | Sprint 11 — UFO cycle fixed, all constants verified |

---

## Sprint Position

| Sprint | Focus | Status |
|--------|-------|--------|
| Sprints 1–7 | Foundation through UFO | ✅ Done |
| Sprint 8 | Sound | ✅ Done |
| Sprint 9 | Deluxe features | ✅ Done + code reviewed |
| Sprint 10 | Game states + polish | ✅ Done |
| Sprint 11 | Accuracy pass | ✅ Done |
| Sprint 12 | Mode System & Config | ✅ Done |
| Sprint 13 | Procedural Generator | ✅ Done |
| Sprint 14 | Rendering Pipeline | ✅ Done |
| Sprint 15 | External Tooling | ✅ Done |
| Sprint 16 | Avatar Coordinate Fix + Level 2 bug fixes | ✅ Done |

---

## Product Risks & Blockers

| Risk/Blocker | Impact | Status |
|-------------|--------|--------|
| 12 test failures from external avatar PNGs | `test_avatar_config` / `test_avatar_generator` tests expect default characters but `assets/avatars/config.json` overrides them | 🟡 Pre-existing; tests were written before external PNG support was added |
| Level 2 playtest not in prior protocol | Bugs only found when human played level 1→2; added mandatory round-advance check to skills | ✅ Fixed |

---

## Key Decisions Made

Decisions that affect product direction (for technical decisions, see `architecture.md`):

| Decision | Rationale | Date |
|----------|-----------|------|
| Python Package profile selected | Best fit for project goals | 2026-03-07 |
| All Deluxe features implemented | Split alien, rainbow bonus, cutscene, descent color | 2026-03-07 |
| Session-only high scores | Per product definition scope | 2026-03-07 |

---

## What "Done" Looks Like

> See `product-definition.md` for full acceptance checklist.

### Arcade Mode
- [x] All items in `product-definition.md` checked off (39/39)
- [x] Player can complete multiple rounds with authentic Deluxe behavior
- [x] All Deluxe-specific features working (split aliens, rainbow bonus, cutscenes, color descent)
- [x] Sounds match original arcade recordings (procedural fallbacks available)
- [x] CRT scanline overlay applied
- [x] Title screen, pause, initials entry complete
- [x] Final accuracy pass (Sprint 11) — verified against reference documentation

### Avatar Mode (New)
- [x] Dual-mode system (Arcade vs Avatar selection)
- [x] 448×512 resolution with smooth scaling (2× coordinate scale throughout)
- [x] 5 procedural Memoji-style characters (generated at 128px, supersampled to 32px)
- [x] Configurable via JSON
- [x] External PNG support (Nano Banana2 ready)
- [x] Bounce animation, expression variation
- [x] All 11 columns reachable by player bullet
- [x] March boundaries correct (no premature descent)
- [x] Renderer survives round advance (round 2+)
- [x] All entities (player, bunkers, UFO, split alien) at 2× coordinates

---

*Update this file when project milestones are reached or product direction changes. This is your compass — `context.md` is your GPS.*
