"""Avatar configuration loading and management."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CharacterDef:
    """Definition for a single avatar character.

    Required fields (core identity):
        name, row, skin, hair, hair_style, shirt, expression

    Optional enhanced fields (all have defaults so old configs still work):
        eye_color:      RGB for iris — default dark blue
        eye_style:      "round" (default) or "almond" (alien large eyes)
        eyebrow_style:  "arched" | "flat" | "bushy" | "raised"
        eyebrow_color:  RGB override — None means use hair color
        lip_color:      RGB for mouth detail
        blush:          draw soft cheek circles if True
        blush_color:    RGB for blush circles
        accessory:      "none" | "glasses" | "aviators" | "antenna" |
                        "dual_antenna" | "crown"
        accessory_color: RGB for accessory
        bg_color:       RGB background fill — None = transparent / black
    """
    # --- required ---
    name: str
    row: int
    skin: tuple[int, int, int]
    hair: tuple[int, int, int]
    hair_style: str
    shirt: tuple[int, int, int]
    expression: str

    # --- optional enhanced ---
    eye_color: tuple[int, int, int] = (50, 50, 100)
    eye_style: str = "round"
    eyebrow_style: str = "arched"
    eyebrow_color: tuple[int, int, int] | None = None   # None → use hair
    lip_color: tuple[int, int, int] = (130, 55, 55)
    blush: bool = False
    blush_color: tuple[int, int, int] = (255, 170, 170)
    accessory: str = "none"
    accessory_color: tuple[int, int, int] = (200, 200, 200)
    bg_color: tuple[int, int, int] | None = None


class AvatarConfig:
    """Loads and provides access to avatar character configuration."""

    CONFIG_PATH = Path("assets/avatars/config.json")

    def __init__(self) -> None:
        self._characters: list[CharacterDef] = self._load()

    def _load(self) -> list[CharacterDef]:
        if self.CONFIG_PATH.exists():
            try:
                with open(self.CONFIG_PATH) as f:
                    data = json.load(f)
                return self._parse_config(data)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Warning: Failed to load avatar config: {e}")
                return self._default_characters()
        return self._default_characters()

    def _parse_config(self, data: dict[str, Any]) -> list[CharacterDef]:
        characters = []
        for char_data in data.get("characters", []):
            p = char_data.get("procedural", {})

            # Optional colour fields that may be null in JSON
            def _col(key: str, default: list[int]) -> tuple[int, int, int]:
                v = p.get(key, default)
                return tuple(v) if v is not None else tuple(default)  # type: ignore[return-value]

            eyebrow_color_raw = p.get("eyebrow_color")
            bg_color_raw = p.get("bg_color")

            characters.append(CharacterDef(
                name=char_data.get("name", "Unknown"),
                row=char_data.get("row", 0),
                skin=_col("skin", [255, 220, 177]),
                hair=_col("hair", [80, 60, 40]),
                hair_style=p.get("hair_style", "slick"),
                shirt=_col("shirt", [0, 100, 200]),
                expression=p.get("expression", "serious"),
                eye_color=_col("eye_color", [50, 50, 100]),
                eye_style=p.get("eye_style", "round"),
                eyebrow_style=p.get("eyebrow_style", "arched"),
                eyebrow_color=(
                    tuple(eyebrow_color_raw)  # type: ignore[arg-type]
                    if eyebrow_color_raw is not None else None
                ),
                lip_color=_col("lip_color", [130, 55, 55]),
                blush=p.get("blush", False),
                blush_color=_col("blush_color", [255, 170, 170]),
                accessory=p.get("accessory", "none"),
                accessory_color=_col("accessory_color", [200, 200, 200]),
                bg_color=(
                    tuple(bg_color_raw)  # type: ignore[arg-type]
                    if bg_color_raw is not None else None
                ),
            ))
        return characters

    def _default_characters(self) -> list[CharacterDef]:
        return [
            CharacterDef(
                name="The Executive",
                row=0,
                skin=(255, 220, 177),
                hair=(80, 60, 40),
                hair_style="slick",
                shirt=(0, 100, 200),
                expression="serious",
                eyebrow_style="arched",
            ),
            CharacterDef(
                name="The Politician",
                row=1,
                skin=(240, 200, 150),
                hair=(200, 150, 80),
                hair_style="formal",
                shirt=(200, 50, 50),
                expression="smirk",
                eyebrow_style="arched",
                lip_color=(160, 80, 80),
            ),
            CharacterDef(
                name="The Pundit",
                row=2,
                skin=(200, 150, 100),
                hair=(30, 30, 30),
                hair_style="messy",
                shirt=(50, 150, 50),
                expression="neutral",
                eyebrow_style="flat",
            ),
            CharacterDef(
                name="The Analyst",
                row=3,
                skin=(255, 200, 160),
                hair=(150, 80, 50),
                hair_style="casual",
                shirt=(150, 50, 150),
                expression="worried",
                eyebrow_style="raised",
                blush=True,
                blush_color=(255, 200, 180),
            ),
            CharacterDef(
                name="The Intern",
                row=4,
                skin=(220, 180, 140),
                hair=(100, 100, 100),
                hair_style="wild",
                shirt=(200, 150, 0),
                expression="panic",
                eyebrow_style="raised",
            ),
        ]

    def get_character(self, row: int) -> CharacterDef:
        for char in self._characters:
            if char.row == row:
                return char
        return self._characters[0]

    @property
    def characters(self) -> list[CharacterDef]:
        return self._characters.copy()
