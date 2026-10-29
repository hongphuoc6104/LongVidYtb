"""Tests for the multi-pillar registry."""

import pytest
from pillars import (
    DEFAULT_PILLAR_ID,
    RESEARCH_GUIDE,
    check_screen_capture,
    depth_floor_for,
    get_pillar,
    pillar_for_brief,
)


def _scene(shot: str) -> dict:
    return {"id": "SC05", "images": [{"shot_type": shot}]}


def test_default_and_lookup():
    assert get_pillar(None).id == DEFAULT_PILLAR_ID
    assert get_pillar("research_guide") is RESEARCH_GUIDE
    assert get_pillar(RESEARCH_GUIDE.name) is RESEARCH_GUIDE
    assert pillar_for_brief({"packaging": {"channel_pillar": "research_guide"}}) is RESEARCH_GUIDE
    with pytest.raises(ValueError):
        get_pillar("cooking")


def test_research_pillar_relaxes_paradox():
    assert not RESEARCH_GUIDE.require_paradox
    assert not RESEARCH_GUIDE.require_vn_1960s_opening
    assert get_pillar(None).require_paradox


def test_tier3_depth_override():
    floor = depth_floor_for({"channel_pillar": "research_guide", "funnel_tier": "tier_3_conversion"})
    assert floor is not None and floor.target_minutes == (10, 15)
    assert depth_floor_for({"channel_pillar": "research_guide", "funnel_tier": "tier_1_broad"}) is None
    assert depth_floor_for({"funnel_tier": "tier_3_conversion"}) is None


def test_screen_capture_rules():
    t3 = {"channel_pillar": "research_guide", "funnel_tier": "tier_3_conversion"}
    assert check_screen_capture(t3, [_scene("full_scene")]) == []
    errs = check_screen_capture(t3, [_scene("screen_capture")])
    assert len(errs) == 1 and errs[0].startswith("SCREEN_CAPTURE_SOURCE_REQUIRED")
    assert check_screen_capture({**t3, "screen_capture_source": "cdp_auto"}, [_scene("screen_capture")]) == []
    errs = check_screen_capture({"funnel_tier": "tier_3_conversion", "screen_capture_source": "cdp_auto"}, [_scene("screen_capture")])
    assert errs and errs[0].startswith("SCREEN_CAPTURE_NOT_ALLOWED")
