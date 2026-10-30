"""Tests for Channel 5: Thương Cho Khéo (thuong_cho_kheo).

Verifies:
  - Channel profile registration and dual characters (Tũn & Mây)
  - Schema 3.0 production bundle generation for TikTok (short_9x16) and YouTube (long_16x9)
  - Fast-Short Flow image count <= 6 with based_on dialogue variations
  - Acoustic cadence compliance (P_tail, zero-pause in SC01, max drift <= 0.5s)
  - Script hook scoring >= 70 points
  - Saved sample run artifact in sys/runs/thuong-cho-kheo-week1-9x16
"""

from __future__ import annotations

import json
from pathlib import Path

from channels.registry import get_channel
from channels.thuong_cho_kheo.builder import (
    CHANNEL_ID,
    build_characters,
    build_production_bundle,
    build_sources,
    build_spinoff_shorts,
    build_topic_9x16,
    build_topic_16x9,
)
from content.research_story_architect import validate_production_bundle
from script_cadence_checker import ScriptCadenceChecker
from tools.script_hook_scorer import score_content_file, score_script

SYS_DIR = Path(__file__).resolve().parents[1]


def test_channel_registration_and_profile() -> None:
    ch = get_channel(CHANNEL_ID)
    assert ch.id == CHANNEL_ID
    assert ch.name == "Thương Cho Khéo"
    assert ch.visual.profile_id == "ch_pastel_duo"
    assert ch.speed_optimization is not None
    assert ch.speed_optimization.render_mode == "hybrid_motion"
    assert ch.speed_optimization.fast_short_max_images <= 6
    assert ch.speed_optimization.spinoff_shorts_per_long == 4
    assert "Tũn" in ch.visual.cast_appearance
    assert "Mây" in ch.visual.cast_appearance


def test_build_characters_and_sources() -> None:
    chars = build_characters()
    assert len(chars) == 2
    ids = {c["id"] for c in chars}
    names = {c["name"] for c in chars}
    assert ids == {"CH01", "CH02"}
    assert names == {"Tũn", "Mây"}
    for c in chars:
        assert c["appearance"]
        assert c["outfit"]

    sources = build_sources()
    assert len(sources) >= 2
    for s in sources:
        assert s["id"]
        assert s["title"]
        assert len(s["facts"]) >= 2


def test_build_topic_9x16_flow_image_budget_and_variations() -> None:
    topic = build_topic_9x16()
    assert topic.format_profile == "short_9x16"
    assert topic.aspect_ratio == "9:16"
    assert topic.subtitles is True
    assert topic.speed == 1.0

    # Total Flow images budget <= 6
    total_flow_images = sum(len(sc.visual_beats) for sc in topic.scenes)
    assert total_flow_images <= 6

    # Verify based_on dialogue pair variations
    variations = [beat for sc in topic.scenes for beat in sc.visual_beats if beat.shot_type == "variation"]
    assert len(variations) >= 2
    for v in variations:
        assert v.based_on is not None
        assert v.based_on != v.image_id
        assert v.preserve.strip()
        assert v.change.strip()


def test_build_topic_16x9_and_spinoff_shorts() -> None:
    topic = build_topic_16x9()
    assert topic.format_profile == "long_16x9"
    assert topic.aspect_ratio == "16:9"
    assert len(topic.scenes) == 16
    assert topic.spinoff_shorts is not None
    assert len(topic.spinoff_shorts) == 4

    spinoffs = build_spinoff_shorts()
    assert len(spinoffs) == 4
    for sp in spinoffs:
        assert sp["format_profile"] == "short_9x16"
        assert sp["scene_count"] >= 1
        assert len(sp["opening_hook"]) > 0


def test_bundle_schema_validation_and_cadence(tmp_path: Path) -> None:
    topic = build_topic_9x16()
    out_dir = tmp_path / "test_9x16_bundle"
    res = build_production_bundle(topic, out_dir)

    assert res["valid_contracts"] is True, f"Contract errors: {res.get('contract_errors')}"
    assert len(res["contract_errors"]) == 0

    brief_file = Path(res["brief_file"])
    content_file = Path(res["content_file"])
    script_file = Path(res["script_file"])
    cadence_file = Path(res["cadence_file"])

    assert brief_file.is_file()
    assert content_file.is_file()
    assert script_file.is_file()
    assert cadence_file.is_file()

    # Re-validate bundle
    brief_data = json.loads(brief_file.read_text(encoding="utf-8"))
    content_data = json.loads(content_file.read_text(encoding="utf-8"))
    valid, errors = validate_production_bundle(SYS_DIR, brief_data, content_data)
    assert valid is True
    assert len(errors) == 0

    # Hook score test
    narrations = [sc.narration for sc in topic.scenes]
    h_score = score_script(narrations, CHANNEL_ID, "short_9x16")
    assert h_score.score >= 70, f"Hook score {h_score.score} < 70"
    assert not h_score.needs_rewrite

    # Cadence checker verification
    checker = ScriptCadenceChecker()
    report = checker.check_file(script_file)
    assert report["status"] == "PASS"
    assert report["max_drift"] <= 0.5
    assert report["warnings_count"] == 0


def test_week1_production_run_artifact() -> None:
    run_dir = SYS_DIR / "runs" / "thuong-cho-kheo-week1-9x16"
    assert run_dir.is_dir(), f"Run artifact dir missing: {run_dir}"

    brief_file = run_dir / "brief.json"
    content_file = run_dir / "content.json"
    script_file = run_dir / "script.json"
    cadence_file = run_dir / "cadence_report.json"

    assert brief_file.is_file()
    assert content_file.is_file()
    assert script_file.is_file()
    assert cadence_file.is_file()

    brief_data = json.loads(brief_file.read_text(encoding="utf-8"))
    content_data = json.loads(content_file.read_text(encoding="utf-8"))

    valid, errors = validate_production_bundle(SYS_DIR, brief_data, content_data)
    assert valid is True, f"Artifact validation failed: {errors}"
    assert len(errors) == 0

    # Verify hook score on artifact
    hook_score = score_content_file(content_file, CHANNEL_ID)
    assert hook_score.score >= 70, f"Artifact hook score {hook_score.score} < 70"
    assert not hook_score.needs_rewrite

    # Verify cadence on artifact
    checker = ScriptCadenceChecker()
    cad_report = checker.check_file(script_file)
    assert cad_report["status"] == "PASS"
    assert cad_report["max_drift"] <= 0.5
    assert cad_report["warnings_count"] == 0


def test_custom_topic_support(tmp_path: Path) -> None:
    custom_title = "Vì sao bạn hay thích người không thích mình"
    topic = build_topic_9x16(topic=custom_title)
    assert topic.topic == custom_title

    out_dir = tmp_path / "custom_bundle"
    res = build_production_bundle(topic, out_dir)
    assert res["valid_contracts"] is True
    brief_data = json.loads(Path(res["brief_file"]).read_text(encoding="utf-8"))
    assert brief_data["topic"] == custom_title
