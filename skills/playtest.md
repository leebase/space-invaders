# Skill: Playtest Loop

**Trigger:** After implementing any gameplay mechanic, or when behavior "feels wrong" but passes tests.

> Unit tests verify logic. Playtesting verifies feel and arcade accuracy. Both are required.

---

## Step 1 — Launch

```bash
# From project root
pip install -e ".[dev]"
space-invaders
```

If the game crashes on launch, that is a blocker — fix it before playtesting.

---

## Step 2 — Structured observation

Do not just "play the game." Observe specific behaviors against this checklist. Note any deviation.

### March behavior
- [ ] Grid starts slow (~800ms between steps with 55 invaders)
- [ ] Speed increases noticeably as invaders are killed
- [ ] With 1–5 invaders remaining, march is visibly very fast (~50–100ms)
- [ ] Grid drops exactly one row on direction change (not more, not less)
- [ ] March audio stays locked to visual march steps

### Player
- [ ] Cannon movement feels correct — not too fast, not sluggish
- [ ] Only one bullet on screen at a time (firing while bullet is active has no effect)
- [ ] Bullet travels straight up at consistent speed
- [ ] Death animation plays on hit before respawning

### Invader fire
- [ ] Multiple enemy bullets visible simultaneously
- [ ] Fire rate increases as invader count drops

### UFO
- [ ] UFO appears from left or right edge (alternating or random — verify against reference)
- [ ] UFO score displays briefly on hit, then disappears
- [ ] UFO drone sound plays while on screen, stops on exit or hit

### Bunkers
- [ ] Player bullets erode bunkers from below
- [ ] Invader bullets erode bunkers from above
- [ ] Erosion is pixel-level and persistent through the round

### Deluxe-specific
- [ ] Split behavior: shooting a qualifying invader produces two smaller ones
- [ ] Rainbow bonus triggers on last invader (correct rows)
- [ ] Invaders visibly change color as they descend

### HUD
- [ ] Score increments correctly for each kill
- [ ] High score updates when current score exceeds it
- [ ] Lives display decrements on death

---

## Step 3 — Compare to reference footage

Open a reference playthrough of **Taito Space Invaders Deluxe (1980 upright)** alongside the running game.

Suggested search: `"space invaders deluxe" arcade longplay 1980`

For each observation above that felt off, pause both at the same game state and compare directly:
- Timing
- Sprite appearance
- Color
- Sound

---

## Step 4 — Log deviations

For each deviation found, create a backlog item using `skills/backlog.md`. Classify as:

| Class | Meaning |
|-------|---------|
| `accuracy-bug` | Behavior differs from Deluxe; must fix |
| `feel-issue` | Behavior is accurate but something feels wrong — investigate before changing |
| `unverified` | Can't confirm against reference; needs more research |

Do not fix deviations mid-playtest. Finish the full observation first, then triage.

---

## Step 5 — After playtesting

- Update `result-review.md` with what was tested and what was found
- If deviations were found: update `context.md` next actions queue
- If behavior is confirmed accurate: run `skills/arcade-accuracy.md` Step 4 (check off acceptance criteria)
