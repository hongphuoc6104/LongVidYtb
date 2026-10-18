"""Shared authoring defaults for new light, moderately simplified 2D scenes.

Historical job snapshots and versioned registries are never rewritten here.
The registry is the single source for both authored style and compiled prompts.
"""
from __future__ import annotations

import json
from pathlib import Path

STYLE_VERSION = "1.4.0"
STYLE_ID = "soft_pastel_2d"
_REGISTRY = json.loads(
    (Path(__file__).parent / "flow_prompts/versions" / STYLE_VERSION / "registry.json").read_text(encoding="utf-8")
)
STYLE_DESCRIPTION: str = _REGISTRY["style"]
CAST_APPEARANCE: str = (
    "Anonymous round white head, expressive dot eyes, thin stick limbs, "
    "simplified cartoon hands and fine-to-medium charcoal contours."
)
DEFAULT_OUTFIT: str = (
    "Simple light-value clothing appropriate to the scene and role; "
    "preserve the costume in returning shots without imposing a recurring color."
)


def render_style(brief: dict, images: dict | None = None) -> str | None:
    """Identify an explicitly authored new style without adopting older jobs."""
    if brief.get("style") == STYLE_DESCRIPTION:
        return STYLE_ID
    items = (images or {}).get("items", [])
    if items and all(STYLE_DESCRIPTION in item.get("actual_prompt", "") for item in items):
        return STYLE_ID
    return None
