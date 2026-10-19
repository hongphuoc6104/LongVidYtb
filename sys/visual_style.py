"""Shared authoring defaults for new light, moderately simplified 2D scenes.

Historical job snapshots and versioned registries are never rewritten here.
The registry is the single source for both authored style and compiled prompts.
"""
from __future__ import annotations

import json
from pathlib import Path

STYLE_VERSION = "1.7.0"
STYLE_ID = "handdrawn_2d_explainer"

_REGISTRY_170 = json.loads(
    (Path(__file__).parent / "flow_prompts/versions/1.7.0/registry.json").read_text(encoding="utf-8")
)
_REGISTRY_160 = json.loads(
    (Path(__file__).parent / "flow_prompts/versions/1.6.0/registry.json").read_text(encoding="utf-8")
)
_REGISTRY_150 = json.loads(
    (Path(__file__).parent / "flow_prompts/versions/1.5.0/registry.json").read_text(encoding="utf-8")
)
_REGISTRY_140 = json.loads(
    (Path(__file__).parent / "flow_prompts/versions/1.4.0/registry.json").read_text(encoding="utf-8")
)

STYLE_DESCRIPTION: str = _REGISTRY_170["style"]
LEGACY_HANDDRAWN_STYLE_DESCRIPTION: str = _REGISTRY_160["style"]
EARTH_TONED_STYLE_DESCRIPTION: str = _REGISTRY_150["style"]
PASTEL_STYLE_DESCRIPTION: str = _REGISTRY_140["style"]

CAST_APPEARANCE: str = (
    "Anonymous round white head, expressive dot eyes, thin stick limbs, "
    "simplified cartoon hands and fine-to-medium charcoal contours."
)
DEFAULT_OUTFIT: str = (
    "Simple earth-toned clothing (terracotta, warm ochre, sage green, navy, warm gray) "
    "appropriate to the scene and role; preserve the costume in returning shots without imposing a recurring color."
)


def render_style(brief: dict, images: dict | None = None) -> str | None:
    """Identify explicitly authored style profiles without adopting unstyled legacy jobs."""
    b_style = brief.get("style")
    if b_style == STYLE_DESCRIPTION:
        return STYLE_ID
    if b_style == LEGACY_HANDDRAWN_STYLE_DESCRIPTION:
        return STYLE_ID
    if b_style == EARTH_TONED_STYLE_DESCRIPTION:
        return "earth_toned_2d"
    if b_style == PASTEL_STYLE_DESCRIPTION:
        return "soft_pastel_2d"
    items = (images or {}).get("items", [])
    if items:
        if all(STYLE_DESCRIPTION in item.get("actual_prompt", "") for item in items):
            return STYLE_ID
        if all(LEGACY_HANDDRAWN_STYLE_DESCRIPTION in item.get("actual_prompt", "") for item in items):
            return STYLE_ID
        if all(EARTH_TONED_STYLE_DESCRIPTION in item.get("actual_prompt", "") for item in items):
            return "earth_toned_2d"
        if all(PASTEL_STYLE_DESCRIPTION in item.get("actual_prompt", "") for item in items):
            return "soft_pastel_2d"
    return None
