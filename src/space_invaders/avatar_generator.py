"""Procedural avatar generator for Avatar Mode — enhanced edition.

Generates Memoji-style faces with:
  - Layered eyes (iris, pupil, highlight) or large almond alien eyes
  - Styled eyebrows (arched/flat/bushy/raised) with colour override
  - Nose shadow dots
  - Lip-coloured expressions (serious/smirk/neutral/worried/panic/smile/open_smile/grin/determined)
  - Optional blush circles (semi-transparent)
  - 9 hair styles: bald/slick/formal/messy/spiky/casual/wild/bob/long/wavy/updo
  - 5 accessory types: glasses/aviators/antenna/dual_antenna/crown
  - Background fill and full shirt with V-neck detail

Back-to-front z-order:
  1. bg_color fill
  2. hair back panels  (long/wavy only)
  3. shirt
  4. ears
  5. face ellipse with shadow
  6. eyebrows
  7. eyes
  8. nose
  9. mouth / expression
  10. blush
  11. hair cap (front)
  12. accessory
"""

from __future__ import annotations

import logging
import math
from pathlib import Path

import pygame

from .avatar_config import CharacterDef

log = logging.getLogger(__name__)

_RGB = tuple[int, int, int]


def _darken(color: _RGB, factor: float = 0.65) -> _RGB:
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor),
    )


def _lighten(color: _RGB, factor: float = 1.4) -> _RGB:
    return (
        min(255, int(color[0] * factor)),
        min(255, int(color[1] * factor)),
        min(255, int(color[2] * factor)),
    )


class AvatarGenerator:
    """Generates Memoji-style avatar surfaces procedurally.

    Checks for external PNG files in assets/avatars/ before falling back
    to procedural generation. External files should be named:
    - avatar_0.png (row 0, top)
    - avatar_1.png (row 1)
    - avatar_2.png (row 2)
    - avatar_3.png (row 3)
    - avatar_4.png (row 4, bottom)
    """

    EXTERNAL_DIR = Path("assets/avatars")

    def generate(self, char: CharacterDef, size: int = 32) -> pygame.Surface:
        """Create avatar surface from character definition or external file.

        Args:
            char: Character definition with colors and style
            size: Output size in pixels (default 32 for Avatar mode cells)

        Returns:
            pygame.Surface with the rendered avatar (RGBA)
        """
        external = self._try_load_external(char.row, size)
        if external is not None:
            return external
        return self._generate_procedural(char, size)

    def _try_load_external(self, row: int, size: int) -> pygame.Surface | None:
        path = self.EXTERNAL_DIR / f"avatar_{row}.png"
        if not path.exists():
            return None
        try:
            surf = pygame.image.load(str(path)).convert_alpha()
            if surf.get_size() != (size, size):
                log.warning(
                    "External avatar %s has wrong size %s, expected %dx%d",
                    path, surf.get_size(), size, size,
                )
                surf = pygame.transform.smoothscale(surf, (size, size))
            return surf
        except pygame.error as e:
            log.warning("Failed to load external avatar %s: %s", path, e)
            return None

    def _generate_procedural(self, char: CharacterDef, size: int) -> pygame.Surface:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        # 1. Background fill
        if char.bg_color is not None:
            surf.fill((*char.bg_color, 255))

        # 2. Hair back panels (behind face for long/wavy)
        self._draw_hair_back(surf, char, size)

        # 3. Shirt
        self._draw_shirt(surf, char, size)

        # 4. Ears
        self._draw_ears(surf, char, size)

        # 5. Face ellipse
        self._draw_face(surf, char, size)

        # 6. Eyebrows
        self._draw_eyebrows(surf, char, size)

        # 7. Eyes
        self._draw_eyes(surf, char, size)

        # 8. Nose
        self._draw_nose(surf, char, size)

        # 9. Expression / mouth
        self._draw_expression(surf, char, size)

        # 10. Blush
        if char.blush:
            self._draw_blush(surf, char, size)

        # 11. Hair cap (front)
        self._draw_hair(surf, char, size)

        # 12. Accessory
        if char.accessory != "none":
            self._draw_accessory(surf, char, size)

        return surf

    # ------------------------------------------------------------------
    # Face
    # ------------------------------------------------------------------

    def _draw_face(self, surf: pygame.Surface, char: CharacterDef, size: int) -> None:
        s = size
        # Shadow (slightly offset)
        shadow = _darken(char.skin, 0.78)
        shadow_rect = pygame.Rect(
            s * 11 // 100 + 1, s * 8 // 100 + 2,
            s * 78 // 100, s * 72 // 100,
        )
        pygame.draw.ellipse(surf, shadow, shadow_rect)
        # Main face
        face_rect = pygame.Rect(
            s * 11 // 100, s * 6 // 100,
            s * 78 // 100, s * 72 // 100,
        )
        pygame.draw.ellipse(surf, char.skin, face_rect)

    def _draw_ears(self, surf: pygame.Surface, char: CharacterDef, size: int) -> None:
        s = size
        ear_y = s * 44 // 100
        ear_r = max(2, s * 7 // 100)
        inner_r = max(1, s * 4 // 100)
        inner_color = _darken(char.skin, 0.82)
        pygame.draw.circle(surf, char.skin, (s * 10 // 100, ear_y), ear_r)
        pygame.draw.circle(surf, inner_color, (s * 10 // 100, ear_y), inner_r)
        pygame.draw.circle(surf, char.skin, (s * 90 // 100, ear_y), ear_r)
        pygame.draw.circle(surf, inner_color, (s * 90 // 100, ear_y), inner_r)

    # ------------------------------------------------------------------
    # Eyebrows
    # ------------------------------------------------------------------

    def _draw_eyebrows(
        self, surf: pygame.Surface, char: CharacterDef, size: int
    ) -> None:
        s = size
        brow_color = char.eyebrow_color if char.eyebrow_color is not None else char.hair
        brow_y = s * 36 // 100
        lx = s * 31 // 100
        rx = s * 69 // 100
        hw = s * 11 // 100
        thick = max(1, s // 20)
        thick_bushy = max(2, s // 12)

        if char.eyebrow_style == "flat":
            pygame.draw.line(
                surf, brow_color, (lx - hw, brow_y), (lx + hw, brow_y), thick
            )
            pygame.draw.line(
                surf, brow_color, (rx - hw, brow_y), (rx + hw, brow_y), thick
            )
        elif char.eyebrow_style == "bushy":
            pygame.draw.line(
                surf, brow_color, (lx - hw, brow_y), (lx + hw, brow_y), thick_bushy
            )
            pygame.draw.line(
                surf, brow_color, (rx - hw, brow_y), (rx + hw, brow_y), thick_bushy
            )
        elif char.eyebrow_style == "raised":
            pts_l = [
                (lx - hw, brow_y + s * 3 // 100),
                (lx, brow_y - s * 4 // 100),
                (lx + hw, brow_y + s * 2 // 100),
            ]
            pts_r = [
                (rx - hw, brow_y + s * 3 // 100),
                (rx, brow_y - s * 4 // 100),
                (rx + hw, brow_y + s * 2 // 100),
            ]
            pygame.draw.lines(surf, brow_color, False, pts_l, thick)
            pygame.draw.lines(surf, brow_color, False, pts_r, thick)
        else:  # arched (default)
            pts_l = [
                (lx - hw, brow_y + s * 2 // 100),
                (lx, brow_y - s * 2 // 100),
                (lx + hw, brow_y + s * 1 // 100),
            ]
            pts_r = [
                (rx - hw, brow_y + s * 2 // 100),
                (rx, brow_y - s * 2 // 100),
                (rx + hw, brow_y + s * 1 // 100),
            ]
            pygame.draw.lines(surf, brow_color, False, pts_l, thick)
            pygame.draw.lines(surf, brow_color, False, pts_r, thick)

    # ------------------------------------------------------------------
    # Eyes
    # ------------------------------------------------------------------

    def _draw_eyes(self, surf: pygame.Surface, char: CharacterDef, size: int) -> None:
        s = size
        eye_y = s * 46 // 100
        lx = s * 32 // 100
        rx = s * 68 // 100
        if char.eye_style == "almond":
            self._draw_almond_eye(surf, char, s, lx, eye_y)
            self._draw_almond_eye(surf, char, s, rx, eye_y)
        else:
            self._draw_round_eye(surf, char, s, lx, eye_y)
            self._draw_round_eye(surf, char, s, rx, eye_y)

    def _draw_round_eye(
        self,
        surf: pygame.Surface,
        char: CharacterDef,
        s: int,
        cx: int,
        cy: int,
    ) -> None:
        r_white = max(2, s * 8 // 100)
        r_iris = max(1, s * 5 // 100)
        r_pupil = max(1, s * 3 // 100)
        r_hi = max(1, s * 2 // 100)
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), r_white)
        pygame.draw.circle(surf, char.eye_color, (cx, cy), r_iris)
        pygame.draw.circle(surf, (10, 10, 10), (cx, cy), r_pupil)
        hx = cx + r_iris // 3
        hy = cy - r_iris // 3
        pygame.draw.circle(surf, (255, 255, 255), (hx, hy), r_hi)

    def _draw_almond_eye(
        self,
        surf: pygame.Surface,
        char: CharacterDef,
        s: int,
        cx: int,
        cy: int,
    ) -> None:
        ew = max(4, s * 22 // 100)
        eh = max(3, s * 14 // 100)
        # White of eye
        eye_surf = pygame.Surface((ew, eh), pygame.SRCALPHA)
        pygame.draw.ellipse(eye_surf, (215, 240, 255, 255), (0, 0, ew, eh))
        surf.blit(eye_surf, (cx - ew // 2, cy - eh // 2))
        # Iris
        ir = max(2, s * 5 // 100)
        pygame.draw.circle(surf, char.eye_color, (cx, cy), ir)
        # Vertical slit pupil (alien look)
        pr_w = max(1, s * 2 // 100)
        pr_h = max(2, ir - 1)
        pupil_rect = pygame.Rect(cx - pr_w // 2, cy - pr_h, pr_w, pr_h * 2)
        pygame.draw.ellipse(surf, (5, 5, 5), pupil_rect)
        # Highlight
        hx = cx + ir // 3
        hy = cy - ir // 2
        pygame.draw.circle(surf, (255, 255, 255), (hx, hy), max(1, s * 2 // 100))
        # Outline
        outline = _darken(char.eye_color, 0.5)
        pygame.draw.ellipse(
            surf, outline,
            pygame.Rect(cx - ew // 2, cy - eh // 2, ew, eh),
            max(1, s // 64),
        )

    # ------------------------------------------------------------------
    # Nose
    # ------------------------------------------------------------------

    def _draw_nose(self, surf: pygame.Surface, char: CharacterDef, size: int) -> None:
        s = size
        nose_y = s * 57 // 100
        shadow = _darken(char.skin, 0.82)
        r = max(1, s * 2 // 100)
        pygame.draw.circle(surf, shadow, (s * 45 // 100, nose_y), r)
        pygame.draw.circle(surf, shadow, (s * 55 // 100, nose_y), r)

    # ------------------------------------------------------------------
    # Expression / Mouth
    # ------------------------------------------------------------------

    def _draw_expression(
        self, surf: pygame.Surface, char: CharacterDef, size: int
    ) -> None:
        s = size
        mouth_y = s * 68 // 100
        lc = char.lip_color
        w = max(1, s // 28)

        if char.expression == "serious":
            pygame.draw.line(
                surf, lc, (s * 36 // 100, mouth_y), (s * 64 // 100, mouth_y), w
            )
        elif char.expression == "smirk":
            pts = [
                (s * 36 // 100, mouth_y),
                (s * 50 // 100, mouth_y - s * 2 // 100),
                (s * 64 // 100, mouth_y - s * 1 // 100),
            ]
            pygame.draw.lines(surf, lc, False, pts, w)
        elif char.expression == "neutral":
            pygame.draw.line(
                surf, lc, (s * 41 // 100, mouth_y), (s * 59 // 100, mouth_y), w
            )
        elif char.expression == "worried":
            rect = pygame.Rect(
                s * 36 // 100, mouth_y - s * 4 // 100,
                s * 28 // 100, s * 8 // 100,
            )
            pygame.draw.arc(surf, lc, rect, math.pi, 2 * math.pi, w)
        elif char.expression == "panic":
            mouth_rect = pygame.Rect(
                s * 37 // 100, mouth_y - s * 3 // 100,
                s * 26 // 100, s * 9 // 100,
            )
            pygame.draw.ellipse(surf, lc, mouth_rect)
            inner = mouth_rect.inflate(-(s // 10), -(s // 10))
            pygame.draw.ellipse(surf, (235, 235, 235), inner)
        elif char.expression == "open_smile":
            rect = pygame.Rect(
                s * 33 // 100, mouth_y - s * 7 // 100,
                s * 34 // 100, s * 13 // 100,
            )
            pygame.draw.arc(surf, lc, rect, math.pi, 2 * math.pi, w)
            teeth = pygame.Rect(
                s * 35 // 100, mouth_y - s * 2 // 100,
                s * 30 // 100, s * 5 // 100,
            )
            pygame.draw.rect(surf, (235, 235, 235), teeth, border_radius=2)
        elif char.expression == "grin":
            rect = pygame.Rect(
                s * 30 // 100, mouth_y - s * 9 // 100,
                s * 40 // 100, s * 14 // 100,
            )
            pygame.draw.arc(surf, lc, rect, math.pi, 2 * math.pi, w)
            teeth = pygame.Rect(
                s * 33 // 100, mouth_y - s * 3 // 100,
                s * 34 // 100, s * 5 // 100,
            )
            pygame.draw.rect(surf, (235, 235, 235), teeth, border_radius=2)
        elif char.expression == "smile":
            rect = pygame.Rect(
                s * 34 // 100, mouth_y - s * 6 // 100,
                s * 32 // 100, s * 11 // 100,
            )
            pygame.draw.arc(surf, lc, rect, math.pi, 2 * math.pi, w)
        elif char.expression == "determined":
            pts = [
                (s * 34 // 100, mouth_y - s * 1 // 100),
                (s * 50 // 100, mouth_y),
                (s * 66 // 100, mouth_y - s * 1 // 100),
            ]
            pygame.draw.lines(surf, lc, False, pts, w)
        else:
            # Default: gentle smile arc
            rect = pygame.Rect(
                s * 34 // 100, mouth_y - s * 5 // 100,
                s * 32 // 100, s * 10 // 100,
            )
            pygame.draw.arc(surf, lc, rect, math.pi, 2 * math.pi, w)

    # ------------------------------------------------------------------
    # Blush
    # ------------------------------------------------------------------

    def _draw_blush(self, surf: pygame.Surface, char: CharacterDef, size: int) -> None:
        s = size
        r = max(2, s * 10 // 100)
        blush_y = s * 56 // 100
        blush_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(blush_surf, (*char.blush_color, 75), (r, r), r)
        surf.blit(blush_surf, (s * 16 // 100, blush_y - r))
        surf.blit(blush_surf, (s * 74 // 100, blush_y - r))

    # ------------------------------------------------------------------
    # Hair
    # ------------------------------------------------------------------

    def _draw_hair_back(
        self, surf: pygame.Surface, char: CharacterDef, size: int
    ) -> None:
        """Side panels behind the face for long/wavy styles."""
        s = size
        if char.hair_style not in ("long", "wavy"):
            return
        panel_w = s * 18 // 100
        panel_h = s * 58 // 100
        panel_y = s * 18 // 100
        h = char.hair
        radius = max(1, s // 10)
        pygame.draw.rect(
            surf, h,
            pygame.Rect(s * 6 // 100, panel_y, panel_w, panel_h),
            border_radius=radius,
        )
        pygame.draw.rect(
            surf, h,
            pygame.Rect(s * 76 // 100, panel_y, panel_w, panel_h),
            border_radius=radius,
        )
        if char.hair_style == "wavy":
            wave = _darken(h, 0.8)
            step = max(2, s // 8)
            for dy in range(0, panel_h, step):
                y = panel_y + dy
                pygame.draw.line(
                    surf, wave,
                    (s * 6 // 100, y),
                    (s * 24 // 100, y + step // 2), 1,
                )
                pygame.draw.line(
                    surf, wave,
                    (s * 76 // 100, y),
                    (s * 94 // 100, y + step // 2), 1,
                )

    def _draw_hair(self, surf: pygame.Surface, char: CharacterDef, size: int) -> None:
        """Draw the front hair cap."""
        s = size
        h = char.hair

        if char.hair_style == "bald":
            return

        elif char.hair_style == "slick":
            rect = pygame.Rect(s * 9 // 100, s * 2 // 100, s * 82 // 100, s * 36 // 100)
            pygame.draw.ellipse(surf, h, rect)
            hi = _lighten(h, 1.35)
            pygame.draw.line(
                surf, hi,
                (s * 34 // 100, s * 7 // 100),
                (s * 62 // 100, s * 13 // 100),
                max(1, s // 30),
            )

        elif char.hair_style == "formal":
            rect = pygame.Rect(s * 11 // 100, s * 3 // 100, s * 78 // 100, s * 34 // 100)
            pygame.draw.ellipse(surf, h, rect)
            pygame.draw.line(
                surf, char.skin,
                (s // 2, s * 5 // 100),
                (s // 2, s * 27 // 100),
                max(1, s // 32),
            )

        elif char.hair_style == "messy":
            blobs = [
                (9, 1, 22, 22), (22, 0, 22, 21), (37, 1, 26, 22),
                (54, 0, 22, 21), (65, 2, 22, 22),
            ]
            for ox, oy, rw, rh in blobs:
                pygame.draw.ellipse(
                    surf, h,
                    pygame.Rect(
                        s * ox // 100, s * oy // 100,
                        s * rw // 100, s * rh // 100,
                    ),
                )

        elif char.hair_style == "spiky":
            for i in range(5):
                bx = s * (10 + i * 17) // 100
                tip_y = s * (14 - i % 2 * 9) // 100
                base_y = s * 30 // 100
                pts = [
                    (bx, base_y),
                    (bx + s * 8 // 100, tip_y),
                    (bx + s * 17 // 100, base_y),
                ]
                pygame.draw.polygon(surf, h, pts)
            pygame.draw.rect(
                surf, h,
                pygame.Rect(s * 9 // 100, s * 23 // 100, s * 82 // 100, s * 12 // 100),
            )

        elif char.hair_style == "wild":
            cx = s // 2
            cy = s * 18 // 100
            core_r = s * 18 // 100
            pygame.draw.circle(surf, h, (cx, cy), core_r)
            for deg in range(0, 360, 28):
                angle = math.radians(deg)
                length = s * (20 + (deg % 56) * 4 // 56) // 100
                ex = int(cx + math.cos(angle) * length)
                ey = int(cy + math.sin(angle) * length * 0.75)
                pygame.draw.line(surf, h, (cx, cy), (ex, ey), max(1, s // 16))

        elif char.hair_style == "bob":
            rect = pygame.Rect(s * 7 // 100, s * 2 // 100, s * 86 // 100, s * 46 // 100)
            pygame.draw.ellipse(surf, h, rect)
            # Blunt straight bottom
            pygame.draw.rect(
                surf, h,
                pygame.Rect(s * 7 // 100, s * 27 // 100, s * 86 // 100, s * 15 // 100),
            )
            # Clear corners below bob line (show neck skin)
            pygame.draw.rect(
                surf, (0, 0, 0, 0),
                pygame.Rect(0, s * 43 // 100, s * 7 // 100, s * 20 // 100),
            )
            pygame.draw.rect(
                surf, (0, 0, 0, 0),
                pygame.Rect(s * 93 // 100, s * 43 // 100, s * 7 // 100, s * 20 // 100),
            )

        elif char.hair_style in ("long", "wavy"):
            # Front cap only — panels drawn in _draw_hair_back
            rect = pygame.Rect(s * 9 // 100, s * 1 // 100, s * 82 // 100, s * 34 // 100)
            pygame.draw.ellipse(surf, h, rect)

        elif char.hair_style == "updo":
            # Side base
            rect = pygame.Rect(s * 11 // 100, s * 10 // 100, s * 78 // 100, s * 28 // 100)
            pygame.draw.ellipse(surf, h, rect)
            # Bun on top
            bun_cx = s // 2
            bun_cy = s * 8 // 100
            bun_r = s * 16 // 100
            pygame.draw.circle(surf, h, (bun_cx, bun_cy), bun_r)
            # Hair-pin highlight
            hi = _lighten(h, 1.45)
            pygame.draw.line(
                surf, hi,
                (s * 37 // 100, s * 5 // 100),
                (s * 63 // 100, s * 9 // 100),
                max(1, s // 40),
            )

        else:  # casual / default
            rect = pygame.Rect(s * 10 // 100, s * 3 // 100, s * 80 // 100, s * 34 // 100)
            pygame.draw.ellipse(surf, h, rect)

    # ------------------------------------------------------------------
    # Shirt
    # ------------------------------------------------------------------

    def _draw_shirt(self, surf: pygame.Surface, char: CharacterDef, size: int) -> None:
        s = size
        shirt_top = s * 76 // 100
        pygame.draw.rect(surf, char.shirt, pygame.Rect(0, shirt_top, s, s - shirt_top))
        # V-neck collar (skin-coloured triangle)
        collar_pts = [
            (s * 34 // 100, shirt_top),
            (s // 2, shirt_top + s * 10 // 100),
            (s * 66 // 100, shirt_top),
        ]
        pygame.draw.polygon(surf, char.skin, collar_pts)
        # Centre-seam shadow
        dark = _darken(char.shirt, 0.72)
        pygame.draw.line(
            surf, dark,
            (s // 2, shirt_top + s * 10 // 100),
            (s // 2, s - 1),
            max(1, s // 64),
        )

    # ------------------------------------------------------------------
    # Accessories
    # ------------------------------------------------------------------

    def _draw_accessory(
        self, surf: pygame.Surface, char: CharacterDef, size: int
    ) -> None:
        s = size
        ac = char.accessory_color
        if char.accessory == "glasses":
            self._draw_glasses(surf, s, ac, tinted=False)
        elif char.accessory == "aviators":
            self._draw_glasses(surf, s, ac, tinted=True)
        elif char.accessory == "antenna":
            self._draw_antenna(surf, s, ac, dual=False)
        elif char.accessory == "dual_antenna":
            self._draw_antenna(surf, s, ac, dual=True)
        elif char.accessory == "crown":
            self._draw_crown(surf, s, ac)

    def _draw_glasses(
        self, surf: pygame.Surface, s: int, color: _RGB, tinted: bool
    ) -> None:
        eye_y = s * 46 // 100
        lx = s * 32 // 100
        rx = s * 68 // 100
        r = s * 11 // 100
        frame_w = max(1, s // 32)

        if tinted:
            for cx in (lx, rx):
                lens_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(lens_surf, (*color, 90), (r, r), r)
                surf.blit(lens_surf, (cx - r, eye_y - r))

        pygame.draw.circle(surf, color, (lx, eye_y), r, frame_w)
        pygame.draw.circle(surf, color, (rx, eye_y), r, frame_w)
        # Bridge
        pygame.draw.line(surf, color, (lx + r, eye_y), (rx - r, eye_y), frame_w)
        # Temples
        pygame.draw.line(
            surf, color, (lx - r, eye_y), (s * 5 // 100, eye_y - s * 2 // 100), frame_w
        )
        pygame.draw.line(
            surf, color, (rx + r, eye_y), (s * 95 // 100, eye_y - s * 2 // 100), frame_w
        )

    def _draw_antenna(
        self, surf: pygame.Surface, s: int, color: _RGB, dual: bool
    ) -> None:
        glow = _lighten(color, 1.55)
        stem_base_y = s * 10 // 100
        ball_y = max(2, s * 3 // 100)
        ball_r = max(2, s * 5 // 100)
        stem_w = max(1, s // 40)

        def _one(cx: int) -> None:
            pygame.draw.line(surf, color, (cx, stem_base_y), (cx, ball_y), stem_w)
            pygame.draw.circle(surf, glow, (cx, ball_y), ball_r)
            pygame.draw.circle(surf, color, (cx, ball_y), ball_r, max(1, s // 48))

        if dual:
            _one(s * 34 // 100)
            _one(s * 66 // 100)
        else:
            _one(s // 2)

    def _draw_crown(self, surf: pygame.Surface, s: int, color: _RGB) -> None:
        base_y = s * 12 // 100
        pts = [
            (s * 14 // 100, base_y),
            (s * 14 // 100, base_y - s * 7 // 100),
            (s * 30 // 100, base_y - s * 4 // 100),
            (s // 2, base_y - s * 10 // 100),
            (s * 70 // 100, base_y - s * 4 // 100),
            (s * 86 // 100, base_y - s * 7 // 100),
            (s * 86 // 100, base_y),
        ]
        pygame.draw.polygon(surf, color, pts)
        jewel = _lighten(color, 1.65)
        jewel_r = max(1, s * 2 // 100)
        for jx in (s * 26 // 100, s // 2, s * 74 // 100):
            pygame.draw.circle(surf, jewel, (jx, base_y - s * 3 // 100), jewel_r)
