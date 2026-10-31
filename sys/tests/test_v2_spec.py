"""Tests for V2 Spec parser, validator, and ResearchedTopic conversion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from content.research_story_architect import (
    validate_production_bundle,
    write_production_package,
)
from content.v2_spec import (
    summarize_v2_spec,
    topic_from_v2_spec,
    validate_v2_spec,
)

SYS_DIR = Path(__file__).resolve().parents[1]


def create_realistic_v2_short_spec() -> Dict[str, Any]:
    """Realistic fixture spec with Vietnamese narration, 2 scenes, multi-visual rows, and endcard."""
    return {
        "job_id": "nao-luoi-week1-9x16-v2",
        "format_profile": "short_9x16",
        "parent_long_id": "nao-luoi-week1-16x9",
        "topic": "Vì sao bạn lướt điện thoại tới 2 giờ sáng",
        "goal": "Giải thích hiện tượng trả thù giờ ngủ bằng tâm lý học đời thường.",
        "audience": "Gen Z và người trẻ đi làm 18-30 tuổi",
        "min_duration": 25.0,
        "max_duration": 50.0,
        "packaging": {
            "youtube_title": "Vì sao bạn thức tới 2 giờ sáng dù rất buồn ngủ?",
            "visual_hook": "Nhân vật người que nằm bấm điện thoại sáng rực trong phòng tối",
            "text_overlay": "TRẢ THÙ GIỜ NGỦ",
            "contrast_pair": "Lười biếng vô kỷ luật vs. Cơ chế tâm lý đòi lại thời gian",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["tamlyhoc", "genz", "thuckhuya", "naoluoi"],
        },
        "sources": [
            {
                "id": "SRC01",
                "title": "Bedtime Procrastination: A Self-Regulation Problem",
                "reference": "Floor M. Kroese et al. (2014). Frontiers in Psychology. DOI: 10.3389/fpsyg.2014.00611",
                "facts": [
                    "Hiện tượng thức khuya trả thù giờ ngủ xuất phát từ việc thiếu tự chủ ban ngày.",
                    "Não bộ cố gắng giành lại cảm giác kiểm soát thời gian cá nhân vào ban đêm.",
                ],
            }
        ],
        "cta_plan": {
            "bridge": "Vì sao não lại đòi lại thời gian kiểu này? Bản dài mình mổ xẻ trên YouTube Não Lười.",
            "close": "Gửi cho đứa bạn hay thức khuya chung với bạn đi.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
            "mid_cta": None,
        },
        "scenes": [
            {
                "title": "Khoảnh khắc lướt màn hình lúc nửa đêm",
                "setting": "Phòng ngủ tối mịt với ánh sáng xanh từ màn hình điện thoại chiếu lên mặt",
                "tone": "narrative_warm",
                "phase": "lived_friction",
                "source_ids": ["SRC01"],
                "claim_facts": [
                    ("Hai giờ sáng, mắt bạn đã díp lại vì mỏi", "SRC01", "Hiện tượng thức khuya trả thù giờ ngủ xuất phát từ việc thiếu tự chủ ban ngày.")
                ],
                "rows": [
                    {
                        "narration": "Hai giờ sáng, mắt bạn đã díp lại vì mỏi. Nhưng ngón tay vẫn vô thức lướt màn hình không chịu dừng.",
                        "visuals": [
                            {
                                "id": "V01",
                                "anchor": "Hai giờ sáng",
                                "spec": "full_scene:CH01|Stickman lying in dark room staring at glowing phone screen",
                                "tempo": "fast",
                                "emphasis_text": "2 GIỜ SÁNG",
                                "reuse_image": None,
                                "based_on": None,
                                "focus": None,
                            },
                            {
                                "id": "V02",
                                "anchor": "Nhưng ngón tay",
                                "spec": "macro_prop:CH01|Close up on thumb endlessly scrolling social feed",
                                "tempo": "normal",
                                "emphasis_text": None,
                                "reuse_image": None,
                                "based_on": None,
                                "focus": None,
                            },
                        ],
                    }
                ],
            },
            {
                "title": "Cơ chế trả thù giờ ngủ và lời kết",
                "setting": "Phòng ngủ tối giản trên nền phẳng sáng sủa",
                "tone": "reflective_slow",
                "phase": "actionable_resolution",
                "source_ids": ["SRC01"],
                "claim_facts": [],
                "rows": [
                    {
                        "narration": "Bạn không hề lười. Não bộ chỉ đang cố giành lại vài giờ tự do sau một ngày bị công việc chi phối.",
                        "visuals": [
                            {
                                "id": "V03",
                                "anchor": "Bạn không hề lười.",
                                "spec": "concept_metaphor:CH01|Stickman brain wearing small superhero cape fighting a clock",
                                "tempo": "slow",
                                "emphasis_text": None,
                                "reuse_image": None,
                                "based_on": None,
                                "focus": None,
                            },
                            {
                                "id": "V04",
                                "anchor": "Não bộ chỉ đang",
                                "spec": "crop:V03",
                                "tempo": "fast",
                                "emphasis_text": None,
                                "reuse_image": None,
                                "based_on": None,
                                "focus": {"x": 0.5, "y": 0.45, "scale": 1.35},
                            },
                        ],
                    },
                    {
                        "narration": "Vì sao não lại đòi lại thời gian kiểu này? Bản dài mình mổ xẻ trên YouTube Não Lười. Gửi cho đứa bạn hay thức khuya chung với bạn đi.",
                        "visuals": [
                            {
                                "id": "V05",
                                "anchor": "Vì sao não lại",
                                "spec": "variation:CH01|Stickman smiling and pointing forward to long video title",
                                "tempo": "normal",
                                "emphasis_text": None,
                                "reuse_image": None,
                                "based_on": "V03",
                                "focus": None,
                            },
                            {
                                "id": "V06",
                                "anchor": "Gửi cho đứa bạn",
                                "spec": "endcard",
                                "tempo": "hold",
                                "emphasis_text": None,
                                "reuse_image": None,
                                "based_on": None,
                                "focus": None,
                            },
                        ],
                    },
                ],
            },
        ],
    }


def test_validate_realistic_v2_spec_passes():
    spec = create_realistic_v2_short_spec()
    errors = validate_v2_spec(spec, "nao_luoi")
    assert errors == [], f"Expected valid spec, got errors: {errors}"


def test_summarize_v2_spec_metrics():
    spec = create_realistic_v2_short_spec()
    metrics = summarize_v2_spec(spec)
    assert metrics["total_visuals"] == 6
    assert metrics["new_flow_images"] == 3  # V01, V02, V03
    assert metrics["crops"] == 1  # V04 (crop:V03)
    assert metrics["variations"] == 1  # V05 (based_on: V03)
    assert metrics["endcards"] == 1  # V06 (endcard)
    assert metrics["emphasis_count"] == 1  # "2 GIỜ SÁNG"
    assert metrics["emphasis_ratio"] <= 0.35


def test_validate_v2_spec_catches_missing_parent_long_id():
    spec = create_realistic_v2_short_spec()
    spec["parent_long_id"] = None
    errors = validate_v2_spec(spec, "nao_luoi")
    assert any("MISSING_PARENT_LONG_ID" in err for err in errors)


def test_validate_v2_spec_catches_duplicate_visual_id():
    spec = create_realistic_v2_short_spec()
    spec["scenes"][1]["rows"][0]["visuals"][1]["id"] = "V01"  # Duplicate of V01
    errors = validate_v2_spec(spec, "nao_luoi")
    assert any("DUPLICATE_VISUAL_ID" in err for err in errors)


def test_validate_v2_spec_catches_anchor_not_in_narration():
    spec = create_realistic_v2_short_spec()
    spec["scenes"][0]["rows"][0]["visuals"][1]["anchor"] = "Câu này không hề có"
    errors = validate_v2_spec(spec, "nao_luoi")
    assert any("ANCHOR_NOT_IN_NARRATION" in err for err in errors)


def test_validate_v2_spec_catches_final_visual_not_endcard():
    spec = create_realistic_v2_short_spec()
    spec["scenes"][1]["rows"][1]["visuals"][1]["spec"] = "full_scene:CH01|Something else"
    errors = validate_v2_spec(spec, "nao_luoi")
    assert any("FINAL_VISUAL_NOT_ENDCARD" in err for err in errors)


def test_validate_v2_spec_catches_cta_bridge_not_in_last_scene():
    spec = create_realistic_v2_short_spec()
    spec["cta_plan"]["bridge"] = "Câu cầu nối hoàn toàn khác không xuất hiện trong bài."
    errors = validate_v2_spec(spec, "nao_luoi")
    assert any("CTA_BRIDGE_NOT_IN_LAST_SCENE" in err for err in errors)


def test_topic_from_v2_spec_and_bundle_validation(tmp_path: Path):
    spec = create_realistic_v2_short_spec()
    topic = topic_from_v2_spec(spec, "nao_luoi")

    assert topic.topic == spec["topic"]
    assert topic.format_profile == "short_9x16"
    assert topic.aspect_ratio == "9:16"
    assert topic.parent_long_id == "nao-luoi-week1-16x9"
    assert topic.packaging is not None
    assert topic.packaging.cta_plan is not None
    assert len(topic.scenes) == 2

    # Check beats in scenes
    sc1 = topic.scenes[0]
    assert len(sc1.visual_beats) == 2
    b1 = sc1.visual_beats[0]
    assert b1.image_id == "SC01_V01"
    assert b1.tempo == "fast"
    assert b1.emphasis_text == "2 GIỜ SÁNG"

    sc2 = topic.scenes[1]
    assert len(sc2.visual_beats) == 4
    # Check crop beat: points to SC02_V03 image
    crop_beat = sc2.visual_beats[1]
    assert crop_beat.image_id == "SC02_V03"
    assert crop_beat.focus is not None
    assert crop_beat.focus.get("scale") == 1.35

    # Check endcard beat
    endcard_beat = sc2.visual_beats[3]
    assert endcard_beat.is_endcard is True
    assert "endcard_9x16.jpg" in str(endcard_beat.reuse_from)

    # Write production package and validate schema compliance
    out_dir = tmp_path / "test_v2_bundle"
    write_production_package(out_dir, topic)
    assert (out_dir / "brief.json").is_file()
    assert (out_dir / "content.json").is_file()

    brief_data = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    content_data = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))

    # Check new fields serialized into brief.json
    assert brief_data.get("parent_long_id") == "nao-luoi-week1-16x9"
    assert brief_data.get("packaging", {}).get("cta_plan") is not None
    assert brief_data.get("engagement") is not None

    # Check new fields serialized into content.json
    images = content_data["scenes"][0]["images"]
    assert images[0]["tempo"] == "fast"
    assert images[0]["emphasis_text"] == "2 GIỜ SÁNG"
    assert any(vt.get("text") == "2 GIỜ SÁNG" for vt in images[0]["visible_text"])

    # Validate bundle passes official contract without error
    is_valid, validation_errors = validate_production_bundle(SYS_DIR, brief_data, content_data)
    assert is_valid, f"validate_production_bundle failed: {validation_errors}"
