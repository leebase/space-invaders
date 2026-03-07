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
| **Current Phase** | Phase 2 — Playable Core |
| **Overall Status** | 🟢 Sprints 1–7 done + reviewed — UFO complete, next: sound |
| **Last Updated** | 2026-03-07 |

---

## Progress Against Product Goals

> Reference: `product-definition.md` for full success criteria.

### MVP Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| Invader grid marching | ✅ Done | Sprint 3 |
| Player movement + bullet | ✅ Done | Sprint 4 |
| Collision detection + scoring | ✅ Done | Sprint 4 |
| Lives, round advance, game over | ✅ Done | Sprint 5 |
| Enemy fire + bunkers | ✅ Done | Sprint 6 |
| UFO — spawn, traverse, score cycle | ✅ Done | Sprint 7 |
| Sound | ⬜ Not started | Sprint 8 |
| Deluxe-specific features (split, rainbow, cutscenes) | ⬜ Not started | Sprint 9 |
| Basic documentation | ✅ Done | product-definition.md + design.md |

### Current Phase Goals

| Goal | Status | Notes |
|------|--------|-------|
| Establish project structure | ✅ Done | |
| Define product vision | ✅ Done | `product-definition.md` written |
| Define technical design | ✅ Done | `design.md` written |
| Add dependencies to pyproject.toml | ✅ Done | |
| Invader grid marching + animation | ✅ Done | Sprints 1-3 complete |
| Player movement + bullet | ✅ Done | Sprint 4 |

---

## Sprint Position

| Sprint | Focus | Status |
|--------|-------|--------|
| Sprints 1–7 | Foundation through UFO | ✅ Done |
| Sprint 8 | Sound | ⬜ Next |
| Sprint 9 | Deluxe features | ⬜ Planned |
| Sprint 10 | Game states + polish | ⬜ Planned |
| Sprint 11 | Accuracy pass | ⬜ Planned |

---

## Product Risks & Blockers

| Risk/Blocker | Impact | Status |
|-------------|--------|--------|
| Deluxe sprite rips may need manual sourcing | Asset bootstrap may need URL updates | 🟡 Monitor |
| Deluxe-specific mechanics (split, rainbow) need reference footage | Risk of inaccuracy | 🟡 Review before implementing |

---

## Key Decisions Made

Decisions that affect product direction (for technical decisions, see `architecture.md`):

| Decision | Rationale | Date |
|----------|-----------|------|
| Python Package profile selected | Best fit for project goals | 2026-03-07 |

---

## What "Done" Looks Like

> See `product-definition.md` for full acceptance checklist.

- [ ] All items in `product-definition.md` checked off
- [ ] Player can complete at least 3 rounds with authentic Deluxe behavior
- [ ] All Deluxe-specific features working (split aliens, rainbow bonus, cutscenes, color descent)
- [ ] Sounds match original arcade recordings

---

*Update this file when project milestones are reached or product direction changes. This is your compass — `context.md` is your GPS.*
