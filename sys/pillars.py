"""Channel pillar registry (SSOT for multi-pillar production).

Each job selects a pillar through ``brief.channel_pillar`` (pillar id or display
name). Missing values resolve to the default cognition pillar so legacy jobs keep
their behaviour. Pillars may override hook rules, visual add-ons and long-form
narrative-depth floors per funnel tier.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Mapping, Optional, Tuple

TIER_1 = "tier_1_broad"
TIER_2 = "tier_2_mid"
TIER_3 = "tier_3_conversion"

SCREEN_CAPTURE_SHOT = "screen_capture"
SCREEN_CAPTURE_SOURCES: Tuple[str, str] = ("user_recorded", "cdp_auto")


@dataclass(frozen=True)
class DepthFloor:
    min_syllables: int
    min_scenes: int
    target_minutes: Tuple[int, int]


@dataclass(frozen=True)
class Pillar:
    id: str
    name: str
    funnel: Mapping[str, str]
    hook_style: str  # "paradox" | "tutorial_promise"
    require_paradox: bool
    require_vn_1960s_opening: bool
    academic_props: bool = False
    screen_capture_tiers: FrozenSet[str] = frozenset()
    depth_overrides: Mapping[str, DepthFloor] = field(default_factory=dict)


COGNITION = Pillar(
    id="cognition",
    name="Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
    funnel={
        TIER_1: "Cognitive biases and everyday paradoxes",
        TIER_2: "First-principles reasoning",
        TIER_3: "Deep thinking tooling",
    },
    hook_style="paradox",
    require_paradox=True,
    require_vn_1960s_opening=True,
)

RESEARCH_GUIDE = Pillar(
    id="research_guide",
    name="Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới",
    funnel={
        TIER_1: "Common beginner mistakes and misconceptions in research",
        TIER_2: "The essence of each step: question, literature review, design, data, writing, submission/peer review",
        TIER_3: "Deep tooling: Zotero, Google Scholar, SPSS/R, LaTeX, journal selection",
    },
    hook_style="tutorial_promise",
    require_paradox=False,
    require_vn_1960s_opening=False,
    academic_props=True,
    screen_capture_tiers=frozenset({TIER_3}),
    depth_overrides={TIER_3: DepthFloor(min_syllables=2700, min_scenes=24, target_minutes=(10, 15))},
)

PILLARS: Dict[str, Pillar] = {p.id: p for p in (COGNITION, RESEARCH_GUIDE)}
DEFAULT_PILLAR_ID = COGNITION.id


def get_pillar(key: Optional[str]) -> Pillar:
    """Resolve a pillar by id or display name; empty -> default. Unknown raises ValueError."""
    raw = (key or "").strip()
    if not raw:
        return PILLARS[DEFAULT_PILLAR_ID]
    if raw in PILLARS:
        return PILLARS[raw]
    for p in PILLARS.values():
        if p.name.casefold() == raw.casefold():
            return p
    raise ValueError(f"Unknown channel_pillar '{raw}'. Allowed ids: {sorted(PILLARS)}")


def _brief_field(brief: Mapping[str, Any], name: str) -> Any:
    pkg = brief.get("packaging") or {}
    return brief.get(name) or (pkg.get(name) if isinstance(pkg, Mapping) else None)


def pillar_for_brief(brief: Mapping[str, Any]) -> Pillar:
    return get_pillar(_brief_field(brief, "channel_pillar"))


def depth_floor_for(brief: Mapping[str, Any]) -> Optional[DepthFloor]:
    """Return a pillar/tier-specific long-form depth floor, or None to use the format profile."""
    pillar = pillar_for_brief(brief)
    return pillar.depth_overrides.get(_brief_field(brief, "funnel_tier") or "")


def check_screen_capture(brief: Mapping[str, Any], scenes: List[Mapping[str, Any]]) -> List[str]:
    """Validate screen_capture shots against pillar/tier policy and the recorded source decision.

    The source (user_recorded vs cdp_auto) is asked from the user only when a video
    actually contains screen_capture shots; until then the job must stop here.
    """
    errors: List[str] = []
    capture_ids = [
        str(sc.get("id", "SC??"))
        for sc in scenes
        for v in (sc.get("images") or [])
        if isinstance(v, Mapping) and v.get("shot_type") == SCREEN_CAPTURE_SHOT
    ]
    if not capture_ids:
        return errors
    pillar = pillar_for_brief(brief)
    tier = _brief_field(brief, "funnel_tier")
    if tier not in pillar.screen_capture_tiers:
        errors.append(
            f"SCREEN_CAPTURE_NOT_ALLOWED: pillar '{pillar.id}' tier '{tier}' forbids screen_capture shots ({', '.join(capture_ids)})"
        )
    source = brief.get("screen_capture_source")
    if source not in SCREEN_CAPTURE_SOURCES:
        errors.append(
            "SCREEN_CAPTURE_SOURCE_REQUIRED: ask the user whether the recordings are "
            f"user_recorded or cdp_auto before continuing (scenes: {', '.join(capture_ids)})"
        )
    return errors
