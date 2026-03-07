# Skill: Arcade Accuracy

**Trigger:** Before marking any mechanic, timing value, or scoring rule as done.

> This skill exists because "close enough" is not the goal. The goal is pixel-perfect, frame-accurate Deluxe behavior. Every deviation must be a conscious decision, not an accident.

---

## Step 1 — Identify the Reference

For the feature you just implemented, locate at least one of:

| Source type | Examples |
|-------------|---------|
| Primary: original hardware recording | YouTube longplays of Taito Space Invaders Deluxe (1980 upright) |
| Primary: disassembly / reverse engineering docs | Emulation wiki, MAME source, Colin Dooley's SI analysis |
| Secondary: documented specs | `design.md` constants table, `product-definition.md` acceptance criteria |
| Tertiary: contemporaneous reviews/manuals | Taito service manual scans (archive.org) |

If you cannot find a primary or secondary source for the specific behavior, **flag it** in the implementation as `# UNVERIFIED — assumed from [source]`.

---

## Step 2 — Verify Each Measurable Value

For the mechanic in question, run through this checklist:

### Timing
- [ ] March interval formula matches `design.md` (`MARCH_MAX_MS=800` at 55, `MARCH_MIN_MS=50` at 1)
- [ ] UFO spawn interval ~25 seconds from wave start
- [ ] UFO score cycle matches `CYCLE` constant in `design.md`
- [ ] Bullet travel speed feels correct against reference footage

### Scoring
- [ ] Squid = 30 pts, Crab = 20 pts, Octopus = 10 pts
- [ ] Split alien sub-entities = half parent value
- [ ] Rainbow bonus: 500 pts last alien bottom rows, 1000 pts last alien bottom-left
- [ ] High score cap = 99,990

### Visual
- [ ] Sprite matches reference (correct pixel art, not a console port variant)
- [ ] Animation frame count and timing match (2 frames per type, alternating on march step)
- [ ] Color-descent: invaders change color as they advance through rows
- [ ] Bunker damage shape matches original (not a circle; original has irregular erosion)

### Sound
- [ ] March note sequence is the correct 4-note loop
- [ ] March audio tempo stays locked to visual march speed
- [ ] Sounds match original arcade recordings (not console port sounds)

---

## Step 3 — Document Any Deviation

If you intentionally deviate from the original (e.g., slightly adjusted timing for playability, or a missing asset), record it:

```markdown
<!-- In the relevant source file, above the deviation -->
# DEVIATION: [brief description]
# Reason: [why]
# Original behavior: [what the arcade does]
# Restore when: [condition that would allow fixing this]
```

And add a backlog item using `skills/backlog.md`.

---

## Step 4 — Update the Acceptance Checklist

In `product-definition.md`, check off the completed item:

```markdown
- [x] March tempo accelerates as invaders are destroyed (speed tied to remaining count)
```

Only check it off after steps 1–3 are complete.

---

## Reference: Known Deluxe Differentiators

These are the things most likely to be accidentally implemented as "base Space Invaders" instead of Deluxe. Double-check each one when relevant:

| Feature | Base SI (1978) | Deluxe (1980) |
|---------|---------------|---------------|
| Splitting aliens | No | Yes — selected aliens split on hit |
| Rainbow bonus | No | Yes — last alien bonuses |
| Inter-round cutscenes | No | Yes |
| Invader color change on descent | No | Yes |
| High score cap | 9,990 | 99,990 |
| Score cycle for UFO | Fixed | Deterministic cycle (50/100/150/300) |
