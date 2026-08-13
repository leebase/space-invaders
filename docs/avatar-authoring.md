# Avatar Authoring Guide

> For external tool creators (e.g., Nano Banana2) and manual avatar customization.

---

## Overview

Space Invaders Deluxe supports a modern **Avatar Mode** where the pixel-art aliens are replaced with Memoji-style human characters. This guide explains how to create and integrate custom avatars.

---

## Quick Start

1. Create 5 PNG images (one per grid row)
2. Name them `avatar_0.png` through `avatar_4.png`
3. Place them in `assets/avatars/`
4. Launch the game in Avatar Mode

```
assets/
└── avatars/
    ├── avatar_0.png  # Top row (was Squid)
    ├── avatar_1.png  # Second row (was Crab)
    ├── avatar_2.png  # Third row (was Crab)
    ├── avatar_3.png  # Fourth row (was Octopus)
    └── avatar_4.png  # Bottom row (was Octopus)
```

---

## Image Specifications

| Property | Recommended | Minimum | Maximum |
|----------|-------------|---------|---------|
| **Dimensions** | 128×128 px | 32×32 px | 256×256 px |
| **Format** | PNG | PNG | PNG |
| **Color depth** | 24-bit RGB + 8-bit alpha | RGBA | RGBA |
| **Background** | Transparent | Transparent | Transparent |

### Why 128×128?

The game displays avatars at 32×32 pixels but uses smooth scaling. A larger source image gives better quality when scaled down. 128×128 provides good detail without excessive file size.

---

## Character Design Guidelines

### Row Mapping

| File | Grid Row | Personality | Expression |
|------|----------|-------------|------------|
| `avatar_0.png` | Top | Leader, confident | Serious, focused |
| `avatar_1.png` | Upper-middle | Enthusiastic | Smirk, self-assured |
| `avatar_2.png` | Middle | Professional | Neutral, composed |
| `avatar_3.png` | Lower-middle | Concerned | Worried, uncertain |
| `avatar_4.png` | Bottom | Panicked | Fearful, desperate |

The expressions should escalate — row 4 should look more worried than row 0. This reinforces the "descending = danger" theme.

### Style Recommendations

**Memoji-inspired approach:**
- Oversized heads relative to bodies (or head-only)
- Simple, clean features
- Recognizable at small sizes
- Distinctive silhouettes

**Color palette:**
- Skin tones: natural human range
- Hair: distinct per character
- Clothing: avoid black (blends with background)
- Avoid neon/oversaturated colors

**What to avoid:**
- Fine details (lost at 32×32)
- Text or logos (illegible)
- Complex backgrounds (must be transparent)
- Photorealistic textures (looks muddy when scaled)

---

## Configuration File

For advanced customization, create `assets/avatars/config.json`:

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
      "procedural": {
        "skin": [240, 200, 150],
        "hair": [200, 150, 80],
        "hair_style": "formal",
        "shirt": [200, 50, 50],
        "expression": "smirk"
      }
    },
    {
      "name": "The Pundit",
      "row": 2,
      "procedural": {
        "skin": [200, 150, 100],
        "hair": [30, 30, 30],
        "hair_style": "messy",
        "shirt": [50, 150, 50],
        "expression": "neutral"
      }
    },
    {
      "name": "The Analyst",
      "row": 3,
      "procedural": {
        "skin": [255, 200, 160],
        "hair": [150, 80, 50],
        "hair_style": "neat",
        "shirt": [150, 50, 150],
        "expression": "worried"
      }
    },
    {
      "name": "The Intern",
      "row": 4,
      "procedural": {
        "skin": [220, 180, 140],
        "hair": [100, 100, 100],
        "hair_style": "casual",
        "shirt": [200, 150, 0],
        "expression": "panic"
      }
    }
  ]
}
```

### Configuration Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Display name (future: for UI) |
| `row` | integer | 0-4, maps to grid row |
| `procedural.skin` | [R,G,B] | Skin tone (0-255 each) |
| `procedural.hair` | [R,G,B] | Hair color |
| `procedural.hair_style` | string | `"slick"`, `"messy"`, `"bald"`, `"formal"`, `"spiky"`, `"casual"` |
| `procedural.shirt` | [R,G,B] | Shirt/collar color |
| `procedural.expression` | string | `"serious"`, `"smirk"`, `"neutral"`, `"worried"`, `"panic"` |

**Priority:** If a PNG file exists for a row, it overrides the procedural configuration.

---

## Tool Integration (Nano Banana2)

### Export Workflow

```python
# Pseudo-code for tool integration
config = generate_avatar_config()  # Your tool defines the characters
save_json("assets/avatars/config.json", config)

for row in range(5):
    character = config["characters"][row]
    image = your_generator.create_avatar(character)
    image.save(f"assets/avatars/avatar_{row}.png")
```

### Validation Checklist

Before submitting avatars:

- [ ] All 5 PNG files present
- [ ] All images have transparent backgrounds
- [ ] Dimensions are square (128×128 recommended)
- [ ] File sizes reasonable (< 500KB each)
- [ ] Expressions escalate appropriately (row 4 most worried)
- [ ] Distinctive silhouettes at thumbnail size

---

## Testing Your Avatars

1. Place files in `assets/avatars/`
2. Launch game: `space-invaders`
3. Select "AVATAR MODE" from title screen
4. Verify all 55 characters appear correctly
5. Play through a round — avatars should march, bounce, and disappear on hit

### Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Avatars not showing | Files in wrong location | Check `assets/avatars/` (not `assets/sprites/`) |
| Black squares instead | Missing alpha channel | Re-export with transparency |
| Wrong avatars | Naming mismatch | Verify `avatar_0.png` through `avatar_4.png` |
| Game crashes on load | Corrupt PNG | Re-export or use procedural fallback (delete PNG) |
| Blurry avatars | Wrong scaling | Ensure source is larger than 32×32, let game scale down |

---

## Procedural Fallback

If no external files are provided, the game generates Memoji-style avatars procedurally. This ensures the game always runs, even without custom assets.

To force procedural mode: delete or rename the `assets/avatars/` folder.

---

## License & Attribution

Custom avatars you create are your own. If distributing:

- Include a `LICENSE` or `CREDITS` file in `assets/avatars/`
- The game will ignore it; it's for human reference only

Example `assets/avatars/CREDITS`:
```
Avatars generated by Nano Banana2
https://example.com/nano-banana2

Characters designed by: [Your Name]
License: CC-BY 4.0
```

---

## Examples

### Minimal (Procedural Only)
No files needed — game generates defaults automatically.

### Simple (Config Only)
```
assets/avatars/
└── config.json
```
Procedural avatars use your color/style choices.

### Full Custom (PNG Override)
```
assets/avatars/
├── config.json
├── avatar_0.png
├── avatar_1.png
├── avatar_2.png
├── avatar_3.png
└── avatar_4.png
```
PNG files displayed; config used if any PNG missing.

---

## Future Extensions

Potential future features (not yet implemented):

- Animation frames (e.g., `avatar_0_0.png`, `avatar_0_1.png`)
- Hit/death expressions (e.g., `avatar_0_hit.png`)
- Per-character sound effects
- Real-time avatar editor UI

---

*For questions or issues, see the project repository or contact the maintainer.*
