# space-invaders Session Context

> **Purpose**: Working memory for session continuity. If power drops, a new AI takes over, or we return after a break—read this first.

---

## Snapshot

| Attribute | Value |
|-----------|-------|
| **Phase** | Sprint 6 — Enemy Fire + Pixel-Destructible Bunkers |
| **Mode** | 2 (Implementation with approval) |
| **Last Updated** | 2026-03-07 |

### Sprint Status
| Sprint | Status | Completion |
|--------|--------|------------|
| Sprint 1 — Foundation | ⬜ Planned | 0% |

---

## What's Happening Now

### Current Work Stream
Setting up the project structure and initial implementation.

### Recently Completed
- ✅ Sprints 1-3 — skeleton, assets, invader grid
- ✅ Sprint 4.5 — code review remediation: 3 correctness bugs fixed, 53 tests added, linter clean
- ✅ Sprint 4 — Player movement, bullet, invader collision, scoring (74 tests pass)
- ✅ Sprint 5 — Lives system, round advance, game over, scene switching (92 tests pass)

### In Progress
- ⏳ Sprint 6 — Enemy fire, pixel-destructible bunkers

---

## Decisions Locked

| Decision | Rationale | Date |
|----------|-----------|------|
| TinyClaw methodology | Build from scratch with small primitives; validate before scale | 2026-03-07 |
| Package dir `space_invaders` (underscore) | Python identifiers can't have hyphens; CLI stays `space-invaders` | 2026-03-07 |
| Venv at `.venv/` | System Python is externally managed (Debian); never use system pip | 2026-03-07 |
| Procedural sprite fallback over download | Asset sites block programmatic access; pixel-art fallbacks cover cold start | 2026-03-07 |

---

## Document Inventory

### Planning (Stable)
| File | Purpose | Status |
|------|---------|--------|
| `product-definition.md` | Product vision, constraints | ✅ Created |
| `project-plan.md` | Strategic roadmap, phases, success metrics | ⬜ To create |
| `sprint-plan.md` | Tactical execution | ✅ Created |
| `AGENTS.md` | AI agent guide, conventions, operational modes | ✅ Created |

### Session Memory (Dynamic)
| File | Purpose | Status |
|------|---------|--------|
| `context.md` | Working state, current focus, next actions | 🔄 Active |
| `result-review.md` | Running log of completed work | 🔄 Active |

### Backlog System
| File | Purpose | Status |
|------|---------|--------|
| `backlog/schema.md` | Unified backlog item schema | ⬜ To create |
| `backlog/template.md` | Copy-paste template for new backlog items | ⬜ To create |

---

## Open Questions (keep short)

1. First feature to implement?
2. What's the definition of MVP?

---

## Next Actions Queue (ranked)

| Rank | Action | Owner | Done When |
|------|--------|-------|----------|
| 1 | Sprint 6: Enemy bullet downward travel | AI | Enemy bullets fire and travel |
| 2 | Sprint 6: Invader fire logic (rate tied to count) | AI | Invaders shoot at player |
| 3 | Sprint 6: Bunker pixel destruction via surfarray | AI | Bunkers erode on hit |
| 4 | Sprint 6: Player hit detection (enemy bullet → kill_player) | AI | Player can die |

---

## Working Conventions

### Start of session
1. Read `product-definition.md` (if exists)
2. Read this file
3. Execute the top-ranked item only
4. Update **Last Updated** if you changed any state here

### End of work unit
1. Move completed items into "Recently Completed"
2. Update "Next Actions Queue"
3. Add any new "Decisions Locked"
4. Keep "Open Questions" ≤ 5

---

## Environment Notes

- **Working Directory**: ./space-invaders
- **Project Name**: space-invaders
- **Profile**: Python Package
- **Author**: Lee Harrington

---

*This file is a living document—update it frequently.*
