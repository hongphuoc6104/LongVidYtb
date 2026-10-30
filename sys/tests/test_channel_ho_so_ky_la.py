"""Test suite verifying Channel 6: Hồ Sơ Kỳ Lạ (ho_so_ky_la) production readiness.

Covers:
- Channel profile registration and active channel alignment
- Builder topic generation for TikTok short_9x16 (<= 8 Flow images) and YouTube long_16x9
- Schema 3.0 contract validation via validate_production_bundle
- Omni-platform 4-part spinoff shorts compliance
- Acoustic cadence calibration (drift <= 0.3s) and hook retention score (>= 70)
- Sample run artifacts integrity at sys/runs/ho-so-ky-la-week1-9x16
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.ho_so_ky_la.builder import (  # noqa: E402
    FAST_SHORT_MAX_IMAGES,
    SPINOFF_SHORTS_COUNT,
    build_production_bundle,
    build_topic_9x16,
    build_topic_16x9,
    export_package,
)
from channels.registry import get_channel  # noqa: E402
from content.research_story_architect import (  # noqa: E402
    compute_brief_hash,
    validate_production_bundle,
)
from omni_platform import short_plans  # noqa: E402
from tools.script_cadence_checker import ScriptCadenceChecker, count_syllables  # noqa: E402
from tools.script_hook_scorer import score_script  # noqa: E402


def test_channel_profile_registration_and_plan():
    """Verify channel ho_so_ky_la is registered with noir profile and matches active config."""
    ch = get_channel("ho_so_ky_la")
    assert ch.id == "ho_so_ky_la"
    assert ch.name == "Hồ Sơ Kỳ Lạ"
    assert ch.visual.profile_id == "ch_noir_dossier"
    assert ch.voice == "VietNarrator"
    assert ch.speed == 1.0

    # Verify active_channel.json matches channel when running in the channel worktree
    active_path = SYS_DIR / "channels" / "active_channel.json"
    if active_path.is_file():
        active_data = json.loads(active_path.read_text(encoding="utf-8"))
        assert active_data["channel_id"] == "ho_so_ky_la"
        assert active_data["visual_profile_id"] == "ch_noir_dossier"
        assert active_data["speed_optimization"]["fast_short_max_images"] == FAST_SHORT_MAX_IMAGES
        assert active_data["speed_optimization"]["spinoff_shorts_per_long"] == SPINOFF_SHORTS_COUNT

    # Verify PLAN.md exists and is documented
    plan_path = SYS_DIR / "channels" / "ho_so_ky_la" / "PLAN.md"
    assert plan_path.is_file()
    assert plan_path.stat().st_size > 1000


def test_builder_builds_valid_9x16_topic():
    """Verify build_topic_9x16 produces <= 8 Flow images, valid hook, and Schema 3.0 compatibility."""
    topic = build_topic_9x16()
    assert topic.format_profile == "short_9x16"
    assert topic.aspect_ratio == "9:16"
    assert topic.subtitles is True
    assert topic.voice == "VietNarrator"
    assert topic.speed == 1.0

    # Verify image count constraint: <= 8 images for fast-short
    total_images = sum(len(sc.visual_beats or []) for sc in topic.scenes)
    assert total_images <= FAST_SHORT_MAX_IMAGES, f"Expected <= {FAST_SHORT_MAX_IMAGES} images, got {total_images}"
    assert total_images == 8

    # Verify hook constraint: first sentence <= 18 syllables and no pauses
    first_sentence = topic.scenes[0].narration.split("?")[0] + "?"
    hook_syl = count_syllables(first_sentence, lang="vi")
    assert hook_syl <= 18, f"Opening hook too long: {hook_syl} syllables"
    assert "[pause:" not in first_sentence

    # Verify character is detective
    assert len(topic.characters) == 1
    assert topic.characters[0]["id"] == "CH01"


def test_builder_builds_valid_16x9_topic_with_spinoffs():
    """Verify build_topic_16x9 produces 14 scenes and 4 compliant spinoff short plans."""
    topic = build_topic_16x9()
    assert topic.format_profile == "long_16x9"
    assert topic.aspect_ratio == "16:9"
    assert len(topic.scenes) == 14

    # Verify spinoff shorts count matches speed optimization specification
    assert topic.spinoff_shorts is not None
    assert len(topic.spinoff_shorts) == SPINOFF_SHORTS_COUNT

    # Verify each spinoff conforms to omni-platform specifications
    for plan in topic.spinoff_shorts:
        assert plan["format_profile"] == "short_9x16"
        assert plan["scene_count"] == 4
        assert len(plan["body"]) == 4
        hook_syl = count_syllables(plan["opening_hook"], lang="vi")
        assert hook_syl <= 18
        assert "[pause:" not in plan["opening_hook"]

    # Verify omni_platform short_plans validation
    mock_brief = {
        "omni_platform": True,
        "aspect_ratio": "16:9",
        "reframe_mode": True,
        "spinoff_shorts": topic.spinoff_shorts,
    }
    mock_content = {
        "scenes": [
            {
                "id": sc.scene_id,
                "narration": sc.narration,
                "images": [{"id": beat.image_id} for beat in (sc.visual_beats or [])],
            }
            for sc in topic.scenes
        ]
    }
    validated_plans = short_plans(mock_brief, mock_content)
    assert len(validated_plans) == SPINOFF_SHORTS_COUNT


def test_sample_production_run_artifacts_and_contracts():
    """Verify sample package at sys/runs/ho-so-ky-la-week1-9x16 conforms 100% to Schema 3.0."""
    pkg_dir = SYS_DIR / "runs" / "ho-so-ky-la-week1-9x16"
    if not (pkg_dir / "brief.json").exists():
        build_production_bundle("short_9x16", output_dir=pkg_dir)
    assert pkg_dir.is_dir(), f"Sample package directory {pkg_dir} must exist"

    required_files = [
        "brief.json",
        "content.json",
        "script.json",
        "cadence_report.json",
        "draft/outline.json",
        "draft/content.json",
    ]
    for rel_path in required_files:
        f = pkg_dir / rel_path
        assert f.is_file(), f"Missing required file: {rel_path}"
        assert f.stat().st_size > 0, f"File {rel_path} is empty"

    brief_data: Dict[str, Any] = json.loads((pkg_dir / "brief.json").read_text(encoding="utf-8"))
    content_data: Dict[str, Any] = json.loads((pkg_dir / "content.json").read_text(encoding="utf-8"))

    # Schema version
    assert brief_data.get("schema_version") == "3.0"
    assert content_data.get("schema_version") == "3.0"

    # Brief hash integrity
    expected_hash = compute_brief_hash(brief_data)
    assert content_data.get("brief_hash") == expected_hash

    # Validate production bundle
    valid, errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=1,
    )
    assert valid is True, f"validate_production_bundle failed: {errors}"
    assert len(errors) == 0

    # Image count <= 8
    total_images = sum(len(sc.get("images", [])) for sc in content_data["scenes"])
    assert total_images <= FAST_SHORT_MAX_IMAGES
    assert total_images == 8


def test_sample_production_run_cadence_and_hook_score():
    """Verify sample package achieves >= 70 Hook score and acoustic cadence drift <= 0.3s."""
    pkg_dir = SYS_DIR / "runs" / "ho-so-ky-la-week1-9x16"
    content_data = json.loads((pkg_dir / "content.json").read_text(encoding="utf-8"))
    script_data = json.loads((pkg_dir / "script.json").read_text(encoding="utf-8"))

    # Check Hook score >= 70
    narrations = [sc["narration"] for sc in content_data["scenes"]]
    hook_result = score_script(narrations, "ho_so_ky_la", "short_9x16")
    assert hook_result.score >= 70, f"Hook score {hook_result.score} < 70"
    assert hook_result.score == 100
    assert hook_result.needs_rewrite is False
    assert hook_result.checks["hook_short"] is True
    assert hook_result.checks["hook_curiosity"] is True
    assert hook_result.checks["hook_direct"] is True

    # Check Acoustic cadence
    checker = ScriptCadenceChecker(nominal_rate=4.0)
    report = checker.check_scenes(script_data)
    assert report["max_drift"] <= 0.30, f"Drift {report['max_drift']} > 0.3s"
    assert report["max_drift"] == 0.0
    assert report["total_actual_syllables"] == report["total_target_syllables"]


def test_export_package_dual_pipeline():
    """Verify export_package executes cleanly in isolated directories for both profiles."""
    with tempfile.TemporaryDirectory() as td:
        root_temp = Path(td)

        # 1. Test 9x16 export
        topic_9x16 = build_topic_9x16()
        out_9x16 = root_temp / "test-short-9x16"
        res_9x16 = export_package(topic_9x16, out_9x16)
        assert res_9x16["valid_contracts"] is True
        assert res_9x16["contract_errors"] == []
        assert res_9x16["hook_score"] >= 70
        assert res_9x16["total_images"] == 8

        # 2. Test 16x9 export
        topic_16x9 = build_topic_16x9()
        out_16x9 = root_temp / "test-long-16x9"
        res_16x9 = export_package(topic_16x9, out_16x9)
        assert res_16x9["valid_contracts"] is True
        assert res_16x9["contract_errors"] == []
        assert res_16x9["hook_score"] >= 70
        assert res_16x9["total_images"] == 28
