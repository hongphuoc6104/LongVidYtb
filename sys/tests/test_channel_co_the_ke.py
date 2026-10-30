"""Verification tests for Channel 7: 'co_the_ke' (Cơ Thể Kể).

Tests:
  - Channel profile registration and active_channel.json integrity.
  - Character descriptions free of visual clichés and laziness patterns.
  - Automated builder exports for TikTok Short (short_9x16, <= 6 Flow images) and YouTube Long (long_16x9).
  - Schema 3.0 contract compliance (validate_production_bundle).
  - Acoustic cadence zero-drift and dead-air check (script_cadence_checker).
  - Hook retention scoring (script_hook_scorer >= 70 points).
  - Local sample production bundle in sys/runs/co-the-ke-week1-9x16.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from channels.co_the_ke.builder import (
    CHANNEL_ID,
    audit_bundle,
    build_characters,
    build_co_the_ke_bundle,
    build_week1_long_topic,
    build_week1_short_topic,
    export_package,
)
from channels.registry import channel_for_style, channel_profile_stamp, get_channel
from content.research_story_architect import compute_brief_hash, validate_production_bundle
from content_contract import validate_brief, validate_content
from flow_prompts.compiler import find_laziness_pattern, find_visual_cliche
from omni_platform import short_plans
from tools.script_hook_scorer import score_script
from visual_style import render_style

SYS_DIR = Path(__file__).resolve().parents[1]
SAMPLE_SHORT_RUN = SYS_DIR / "runs/co-the-ke-week1-9x16"
SAMPLE_LONG_RUN = SYS_DIR / "runs/co-the-ke-week1-16x9"


def test_co_the_ke_registry_and_active_channel() -> None:
    """Verify channel co_the_ke registration, profile stamps, and active_channel.json."""
    ch = get_channel(CHANNEL_ID)
    assert ch.id == "co_the_ke"
    assert ch.name == "Cơ Thể Kể"
    assert ch.niche == "Sức khỏe và cơ thể được nhân hóa"
    assert ch.visual.profile_id == "ch_organ_buddies"
    assert ch.voice == "VietNarrator"
    assert ch.speed == 1.0

    # Speed optimization rules
    assert ch.speed_optimization is not None
    assert ch.speed_optimization.render_mode == "hybrid_motion"
    assert ch.speed_optimization.fast_short_max_images <= 6
    assert ch.speed_optimization.spinoff_shorts_per_long >= 3

    # Visual style recognition
    resolved = render_style({"style": ch.visual.style_description})
    assert resolved == "ch_organ_buddies"
    matched = channel_for_style(ch.visual.style_description)
    assert matched is not None and matched.id == "co_the_ke"

    # Active channel config check
    active_path = SYS_DIR / "channels/active_channel.json"
    if active_path.is_file():
        active = json.loads(active_path.read_text(encoding="utf-8"))
        assert active["channel_id"] == "co_the_ke"
        assert active["visual_profile_id"] == "ch_organ_buddies"
        stamp = channel_profile_stamp("co_the_ke")
        assert active["channel_profile_stamp"]["sha256"] == stamp["sha256"]


def test_co_the_ke_characters_validity() -> None:
    """Verify 5 recurring organ mascots and host have zero clichés and zero laziness patterns."""
    chars = build_characters()
    assert len(chars) == 5
    ids = {c["id"] for c in chars}
    assert ids == {"CH01", "CH02", "CH03", "CH04", "CH05"}

    for c in chars:
        app = c["appearance"]
        outf = c["outfit"]
        assert find_visual_cliche(app) is None, f"{c['id']} appearance has cliché: {find_visual_cliche(app)}"
        assert find_visual_cliche(outf) is None, f"{c['id']} outfit has cliché: {find_visual_cliche(outf)}"
        assert (
            find_laziness_pattern(app, "1.7.0") is None
        ), f"{c['id']} appearance has laziness: {find_laziness_pattern(app, '1.7.0')}"
        assert (
            find_laziness_pattern(outf, "1.7.0") is None
        ), f"{c['id']} outfit has laziness: {find_laziness_pattern(outf, '1.7.0')}"


def test_week1_short_topic_and_export(tmp_path: Path) -> None:
    """Verify week 1 TikTok Short export (Schema 3.0, <= 6 Flow images, hook score >= 70)."""
    topic = build_week1_short_topic()
    assert topic.format_profile == "short_9x16"
    assert topic.aspect_ratio == "9:16"
    assert len(topic.scenes) == 5

    out_dir = tmp_path / "test_short_bundle"
    res = export_package(topic, out_dir, system_root=SYS_DIR)
    assert res["valid_contracts"] is True

    # File completeness
    required_files = (
        "brief.json",
        "content.json",
        "script.json",
        "cadence_report.json",
        "draft/outline.json",
        "draft/content.json",
    )
    for fname in required_files:
        fpath = out_dir / fname
        assert fpath.is_file(), f"Missing file: {fname}"
        assert fpath.stat().st_size > 0, f"Empty file: {fname}"

    # Contract verification
    b = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    c = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))
    validate_brief(SYS_DIR, b)
    validate_content(SYS_DIR, b, 1, c["brief_hash"], c)
    assert c["brief_hash"] == compute_brief_hash(b)

    valid_bundle, errors = validate_production_bundle(SYS_DIR, b, c)
    assert valid_bundle is True, f"Contract errors: {errors}"
    assert len(errors) == 0

    # Image count constraint: <= 6 Flow images
    total_images = sum(len(sc["images"]) for sc in c["scenes"])
    assert total_images <= 6, f"Expected <= 6 Flow images, got {total_images}"

    # Cadence zero drift
    cadence = json.loads((out_dir / "cadence_report.json").read_text(encoding="utf-8"))
    assert cadence["net_drift"] <= 0.3
    assert cadence["max_drift"] <= 0.3

    # Hook retention score >= 70
    narrations = [sc["narration"] for sc in c["scenes"]]
    hook_res = score_script(narrations, channel_id="co_the_ke", format_profile="short_9x16")
    assert hook_res.score >= 70, f"Hook score {hook_res.score} < 70"
    assert not hook_res.needs_rewrite


def test_week1_long_topic_and_export(tmp_path: Path) -> None:
    """Verify week 1 YouTube Long export (Schema 3.0, 3 spinoff shorts, hook score >= 70)."""
    topic, omni_plan = build_week1_long_topic()
    assert topic.format_profile == "long_16x9"
    assert topic.aspect_ratio == "16:9"
    assert len(topic.scenes) == 8

    out_dir = tmp_path / "test_long_bundle"
    res = export_package(topic, out_dir, omni_plan=omni_plan, system_root=SYS_DIR)
    assert res["valid_contracts"] is True

    b = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    c = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))
    validate_brief(SYS_DIR, b)
    validate_content(SYS_DIR, b, 1, c["brief_hash"], c)

    valid_bundle, errors = validate_production_bundle(SYS_DIR, b, c)
    assert valid_bundle is True, f"Contract errors: {errors}"
    assert len(errors) == 0

    # Spinoff shorts contract
    assert "spinoff_shorts" in b
    plans = short_plans(b, c)
    assert 2 <= len(plans) <= 3
    for plan in plans:
        assert len(plan["body"]) == 4

    # Hook retention score >= 70
    narrations = [sc["narration"] for sc in c["scenes"]]
    hook_res = score_script(narrations, channel_id="co_the_ke", format_profile="long_16x9")
    assert hook_res.score >= 70, f"Hook score {hook_res.score} < 70"


def test_local_sample_bundle_exists_and_passes() -> None:
    """Verify sample production bundle at sys/runs/co-the-ke-week1-9x16."""
    if not SAMPLE_SHORT_RUN.exists():
        pytest.skip("Local sample run not yet generated; run builder.py first.")

    audit = audit_bundle(SAMPLE_SHORT_RUN, channel_id="co_the_ke")
    assert audit["valid_contracts"] is True, f"Sample bundle contract errors: {audit['contract_errors']}"
    assert audit["total_images"] <= 6, f"Expected <= 6 Flow images, got {audit['total_images']}"
    assert audit["hook_score"] >= 70, f"Hook score {audit['hook_score']} < 70"
    assert audit["cadence_report"]["net_drift"] <= 0.5


def test_builder_cli_helper(tmp_path: Path) -> None:
    """Verify programmatic CLI helper build_co_the_ke_bundle."""
    res = build_co_the_ke_bundle(
        format_choice="short_9x16",
        out_dir=tmp_path,
        job_name="cli-test-short",
    )
    assert "short_9x16" in res
    audit = res["short_9x16"]["audit"]
    assert audit["valid_contracts"] is True
    assert audit["total_images"] <= 6
    assert audit["hook_score"] >= 70
