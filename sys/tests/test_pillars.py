"""Tests for ContentPhilosophy registry and dynamic depth estimation."""

import pytest
from pillars import (
    COGNITION,
    DEFAULT_PHILOSOPHY_ID,
    DEFAULT_PILLAR_ID,
    RESEARCH_GUIDE,
    ContentPhilosophy,
    DepthEstimate,
    check_screen_capture,
    content_depth_estimate,
    depth_floor_for,
    get_philosophy,
    get_pillar,
    philosophy_for_brief,
    pillar_for_brief,
)


def _scene(shot: str) -> dict:
    return {"id": "SC05", "images": [{"shot_type": shot}]}


def test_philosophy_dataclass_and_defaults():
    assert isinstance(COGNITION, ContentPhilosophy)
    assert COGNITION.id == "cognition"
    assert len(COGNITION.principles) >= 3
    assert len(COGNITION.exemplar_hooks) >= 2
    assert "2D indie doodle" in COGNITION.visual_guidance
    assert COGNITION.academic_props is False
    assert len(COGNITION.screen_capture_tiers) == 0

    assert isinstance(RESEARCH_GUIDE, ContentPhilosophy)
    assert RESEARCH_GUIDE.id == "research_guide"
    assert len(RESEARCH_GUIDE.principles) >= 3
    assert len(RESEARCH_GUIDE.exemplar_hooks) >= 2
    assert RESEARCH_GUIDE.academic_props is True
    assert "tier_3_conversion" in RESEARCH_GUIDE.screen_capture_tiers

    assert DEFAULT_PHILOSOPHY_ID == "cognition"
    assert DEFAULT_PILLAR_ID == DEFAULT_PHILOSOPHY_ID


def test_removed_hard_constraints_not_present():
    # Verify clean-break removal of obsolete constraints
    assert not hasattr(COGNITION, "require_paradox")
    assert not hasattr(COGNITION, "require_vn_1960s_opening")
    assert not hasattr(COGNITION, "hook_style")

    assert not hasattr(RESEARCH_GUIDE, "require_paradox")
    assert not hasattr(RESEARCH_GUIDE, "require_vn_1960s_opening")
    assert not hasattr(RESEARCH_GUIDE, "hook_style")


def test_philosophy_and_pillar_lookup():
    assert get_philosophy(None).id == DEFAULT_PHILOSOPHY_ID
    assert get_philosophy("research_guide") is RESEARCH_GUIDE
    assert get_philosophy(RESEARCH_GUIDE.name) is RESEARCH_GUIDE
    assert get_philosophy(COGNITION.name) is COGNITION

    # Backward-compatible get_pillar
    assert get_pillar(None).id == DEFAULT_PILLAR_ID
    assert get_pillar("research_guide") is RESEARCH_GUIDE
    assert get_pillar(RESEARCH_GUIDE.name) is RESEARCH_GUIDE

    # Resolution from brief
    assert philosophy_for_brief({"packaging": {"channel_philosophy": "research_guide"}}) is RESEARCH_GUIDE
    assert philosophy_for_brief({"channel_philosophy": "cognition"}) is COGNITION
    assert pillar_for_brief({"packaging": {"channel_pillar": "research_guide"}}) is RESEARCH_GUIDE
    assert pillar_for_brief({"channel_pillar": "cognition"}) is COGNITION

    with pytest.raises(ValueError):
        get_philosophy("unknown_philosophy")

    with pytest.raises(ValueError):
        get_pillar("cooking")


def test_content_depth_estimate_dynamic_flow():
    # 1. Estimation from topic string alone
    est_topic = content_depth_estimate("Hiệu Ứng Dunning-Kruger")
    assert isinstance(est_topic, DepthEstimate)
    assert est_topic.recommended_scenes[0] >= 10
    assert est_topic.recommended_scenes[1] >= est_topic.recommended_scenes[0]
    assert est_topic.recommended_minutes[0] > 0
    assert est_topic.target_syllables > 0
    assert "Dunning-Kruger" in est_topic.rationale

    # 2. Scaling with required points depth
    est_brief_short = content_depth_estimate({
        "topic": "Tư duy phản biện",
        "required_points": [{"id": "pt1", "text": "Khái niệm"}],
    })
    est_brief_mid = content_depth_estimate({
        "topic": "Tư duy phản biện",
        "required_points": [
            {"id": "pt1", "text": "Khái niệm"},
            {"id": "pt2", "text": "Mô hình"},
            {"id": "pt3", "text": "Ứng dụng"},
        ],
    })
    est_brief_deep = content_depth_estimate({
        "topic": "Tư duy phản biện",
        "required_points": [
            {"id": "pt1", "text": "Khái niệm"},
            {"id": "pt2", "text": "Mô hình"},
            {"id": "pt3", "text": "Ứng dụng"},
            {"id": "pt4", "text": "Phản biện"},
            {"id": "pt5", "text": "Thực hành"},
        ],
    })
    assert est_brief_mid.recommended_scenes[0] >= est_brief_short.recommended_scenes[0]
    assert est_brief_deep.recommended_scenes[0] > est_brief_short.recommended_scenes[0]
    assert est_brief_deep.target_syllables > est_brief_short.target_syllables

    # 3. Short format (9:16) dynamic adaptation
    est_short_form = content_depth_estimate({
        "topic": "Thói quen nhỏ",
        "format_profile": "short_9x16",
    })
    assert est_short_form.recommended_minutes[1] <= 2.0
    assert est_short_form.recommended_scenes[1] <= 8
    assert est_short_form.target_syllables <= 400


def test_depth_estimate_property_compatibility():
    est = DepthEstimate(
        recommended_scenes=(14, 18),
        recommended_minutes=(6.0, 8.5),
        target_syllables=1600,
        rationale="Test estimate",
    )
    assert est.min_scenes == 14
    assert est.min_syllables == 1600
    assert est.target_minutes == (6.0, 8.5)


def test_tier3_depth_override():
    floor = depth_floor_for({"channel_pillar": "research_guide", "funnel_tier": "tier_3_conversion"})
    assert floor is not None
    assert floor.target_minutes == (10, 15)
    assert floor.min_scenes == 24
    assert floor.min_syllables == 2700

    # Non-overridden tiers return None (falling back to dynamic format profile)
    assert depth_floor_for({"channel_pillar": "research_guide", "funnel_tier": "tier_1_broad"}) is None
    assert depth_floor_for({"funnel_tier": "tier_3_conversion"}) is None


def test_screen_capture_rules():
    t3 = {"channel_pillar": "research_guide", "funnel_tier": "tier_3_conversion"}
    assert check_screen_capture(t3, [_scene("full_scene")]) == []

    errs = check_screen_capture(t3, [_scene("screen_capture")])
    assert len(errs) == 1
    assert errs[0].startswith("SCREEN_CAPTURE_SOURCE_REQUIRED")

    assert check_screen_capture({**t3, "screen_capture_source": "cdp_auto"}, [_scene("screen_capture")]) == []

    errs = check_screen_capture(
        {"funnel_tier": "tier_3_conversion", "screen_capture_source": "cdp_auto"},
        [_scene("screen_capture")],
    )
    assert len(errs) > 0
    assert errs[0].startswith("SCREEN_CAPTURE_NOT_ALLOWED")
