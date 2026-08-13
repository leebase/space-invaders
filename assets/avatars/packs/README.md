# Avatar Packs

Avatar packs replace the default procedural characters in Avatar Mode.

## How to activate a pack

Copy the pack's `config.json` to `assets/avatars/config.json`:

```bash
# Sexy Aliens
cp assets/avatars/packs/sexy-aliens/config.json assets/avatars/config.json

# US Democrats
cp assets/avatars/packs/us-democrats/config.json assets/avatars/config.json

# Restore defaults (delete the active config)
rm assets/avatars/config.json
```

Then start Avatar Mode from the title screen. Changes take effect on the next game launch.

## Packs

### sexy-aliens
Five glamorous extra-terrestrials with almond eyes, exotic skin tones, antennas, and attitude.

| Row | Name | Key traits |
|-----|------|-----------|
| 0 | ZARA | Emerald green, silver slick hair, dual magenta antennas, violet almond eyes, smirk |
| 1 | LYRA | Deep violet, flowing platinum long hair, lavender antenna, electric blue almond eyes |
| 2 | NOVA | Ice cyan, silver bob, steel glasses, cyan almond eyes, cool neutral expression |
| 3 | VEGA | Rose pink, golden wavy hair, gold crown, amber round eyes, wide open smile |
| 4 | XENA | Bronze amber, jet black spikes, fiery orange almond eyes, determined jaw |

### us-democrats
Caricature portraits of prominent US Democratic Party figures. Parody/satire.

| Row | Name | Key traits |
|-----|------|-----------|
| 0 | JOE | Fair skin, silver slick hair, signature gold aviators, blue suit, serious |
| 1 | KAMALA | Warm medium skin, dark formal hair, navy suit, berry lips, sly smirk |
| 2 | BERNIE | Fair skin, white wild hair, tortoiseshell glasses, bushy brows, grey shirt |
| 3 | BARACK | Medium-dark skin, black slick hair, navy suit, confident open smile |
| 4 | AOC | Warm medium skin, long black hair, red shirt, bold red lips, determined |

## Creating your own pack

1. Create a folder under `assets/avatars/packs/your-pack-name/`
2. Add a `config.json` following the schema below
3. Activate with `cp assets/avatars/packs/your-pack-name/config.json assets/avatars/config.json`

### config.json schema

```json
{
  "version": 1,
  "characters": [
    {
      "name": "Display Name",
      "row": 0,
      "procedural": {
        "skin":             [R, G, B],
        "hair":             [R, G, B],
        "hair_style":       "slick | formal | messy | spiky | casual | wild | bob | long | wavy | updo | bald",
        "shirt":            [R, G, B],
        "expression":       "serious | smirk | neutral | worried | panic | smile | open_smile | grin | determined",
        "eye_color":        [R, G, B],
        "eye_style":        "round | almond",
        "eyebrow_style":    "arched | flat | bushy | raised",
        "eyebrow_color":    [R, G, B] or null,
        "lip_color":        [R, G, B],
        "blush":            true | false,
        "blush_color":      [R, G, B],
        "accessory":        "none | glasses | aviators | antenna | dual_antenna | crown",
        "accessory_color":  [R, G, B],
        "bg_color":         [R, G, B] or null
      }
    }
  ]
}
```

- `eyebrow_color: null` — inherits hair colour
- `bg_color: null` — transparent background
- Rows 0–4 map to the 5 grid rows (0 = top/squid row, 4 = bottom/octopus row)
- Missing optional fields fall back to sensible defaults
- External PNG overrides still work: place `avatar_0.png` … `avatar_4.png` in `assets/avatars/`
