"""Shared authoring defaults for new light, moderately simplified 2D scenes.

Historical job snapshots and versioned registries are never rewritten here.
The registry is the single source for both authored style and compiled prompts.
"""
from __future__ import annotations

import json
from pathlib import Path

STYLE_VERSION = "1.5.0"
STYLE_ID = "earth_toned_2d"

_REGISTRY_150 = json.loads(
    (Path(__file__).parent / "flow_prompts/versions/1.5.0/registry.json").read_text(encoding="utf-8")
)
_REGISTRY_140 = json.loads(
    (Path(__file__).parent / "flow_prompts/versions/1.4.0/registry.json").read_text(encoding="utf-8")
)

STYLE_DESCRIPTION: str = _REGISTRY_150["style"]
PASTEL_STYLE_DESCRIPTION: str = _REGISTRY_140["style"]

CAST_APPEARANCE: str = (
    "Anonymous round white head, expressive dot eyes, thin stick limbs, "
    "simplified cartoon hands and fine-to-medium charcoal contours."
)
DEFAULT_OUTFIT: str = (
    "Simple earth-toned or neutral clothing (ochre, sage green, warm gray, sky blue) "
    "appropriate to the scene and role; preserve the costume in returning shots without imposing a recurring color."
)


def render_style(brief: dict, images: dict | None = None) -> str | None:
    """Identify explicitly authored style profiles without adopting unstyled legacy jobs."""
    b_style = brief.get("style")
    if b_style == STYLE_DESCRIPTION:
        return STYLE_ID
    if b_style == PASTEL_STYLE_DESCRIPTION:
        return "soft_pastel_2d"
    items = (images or {}).get("items", [])
    if items:
        if all(STYLE_DESCRIPTION in item.get("actual_prompt", "") for item in items):
            return STYLE_ID
        if all(PASTEL_STYLE_DESCRIPTION in item.get("actual_prompt", "") for item in items):
            return "soft_pastel_2d"
    return None
