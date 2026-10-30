"""Unit and regression tests for channel ua_sao_vay (Ủa Sao Vậy?)."""

from __future__ import annotations

import json
from pathlib import Path

from channels.registry import (
    apply_channel,
    channel_cast,
    channel_profile_stamp,
    get_channel,
)
from channels.ua_sao_vay.builder import (
    CHANNEL_ID,
    build_channel_bundle,
    build_long_bundle,
    build_short_bundle,
)
from content.research_story_architect import validate_production_bundle
from omni_platform import short_plans
from script_cadence_checker import ScriptCadenceChecker, count_syllables
from script_hook_scorer import score_content_file


def test_channel_ua_sao_vay_registration_and_config() -> None:
    """Verify channel profile, persona Bé Ủa, and active configuration."""
    ch = get_channel(CHANNEL_ID)
    assert ch.id == "ua_sao_vay"
    assert ch.name == "Ủa Sao Vậy?"
    assert ch.visual.profile_id == "ch_sticker_pop"
    assert "Bé Ủa" in ch.persona
    assert ch.voice == "VietNarrator"
    assert ch.speed == 1.0
    assert ch.short_spec.format_profile == "short_9x16"
    assert ch.long_spec.format_profile == "long_16x9"
    assert ch.short_spec.duration_seconds == (20, 35)

    assert ch.speed_optimization is not None
    assert ch.speed_optimization.render_mode == "hybrid_motion"
    assert ch.speed_optimization.fast_short_max_images == 5
    assert ch.speed_optimization.spinoff_shorts_per_long == 6

    # Verify active_channel.json matches when inside worktree
    active_path = Path(__file__).resolve().parents[1] / "channels" / "active_channel.json"
    if active_path.is_file():
        active_data = json.loads(active_path.read_text(encoding="utf-8"))
        assert active_data["channel_id"] == "ua_sao_vay"
        assert active_data["visual_profile_id"] == "ch_sticker_pop"
        assert active_data["voice"] == "VietNarrator"


def test_channel_provenance_and_cast() -> None:
    """Verify channel cast generation and provenance stamps."""
    cast = channel_cast(CHANNEL_ID, "CH01")
    assert cast["id"] == "CH01"
    assert "Bé Ủa" in cast["name"]
    assert "lemon-yellow" in cast["appearance"]

    stamp = channel_profile_stamp(CHANNEL_ID)
    assert stamp["id"] == "ua_sao_vay"
    assert len(stamp["sha256"]) == 64

    base_brief = {
        "schema_version": "3.0",
        "topic": "Test topic",
        "outputs": [{"aspect_ratio": "9:16", "language": "vi", "subtitles": True}],
    }
    applied = apply_channel(base_brief, CHANNEL_ID)
    assert applied["channel_profile"] == stamp
    assert applied["style"] == get_channel(CHANNEL_ID).visual.style_description
    assert applied["tone"] == get_channel(CHANNEL_ID).tone
    assert any("uasaovay" in kw for kw in applied["seo_keywords"])


def test_builder_short_9x16_contract_and_acoustics(tmp_path: Path) -> None:
    """Verify TikTok Fast-Short (short_9x16) satisfies Schema 3.0, <= 5 Flow images, and acoustics."""
    out_dir = tmp_path / "test_short_9x16"
    result = build_short_bundle(output_dir=out_dir)

    assert result["valid_contracts"] is True
    assert result["contract_errors"] == []
    assert result["format_profile"] == "short_9x16"
    assert result["image_count"] <= 5
    assert result["image_count"] == 4
    assert result["scene_count"] == 4
    assert result["cadence_status"] == "PASS"
    assert result["cadence_warnings"] == 0
    assert result["hook_score"] >= 70
    assert result["hook_score"] == 100

    # Verify generated files
    brief_data = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    content_data = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))
    script_data = json.loads((out_dir / "script.json").read_text(encoding="utf-8"))
    cadence_data = json.loads((out_dir / "cadence_report.json").read_text(encoding="utf-8"))

    assert brief_data["aspect_ratio"] == "9:16"
    assert brief_data["format_profile"] == "short_9x16"
    assert brief_data["channel_profile"]["id"] == "ua_sao_vay"
    assert 20.0 <= brief_data["duration"]["min_seconds"] <= 35.0

    assert len(content_data["scenes"]) == 4
    assert content_data["characters"][0]["id"] == "CH01"
    assert "Bé Ủa" in content_data["characters"][0]["name"]

    checker = ScriptCadenceChecker(nominal_rate=4.0)
    rep = checker.check_scenes(script_data)
    assert rep["status"] == "PASS"
    assert rep["warnings_count"] == 0
    assert cadence_data["status"] == "PASS"

    score_res = score_content_file(out_dir / "content.json", CHANNEL_ID)
    assert score_res.score >= 70
    assert score_res.score == 100
    assert not score_res.needs_rewrite


def test_builder_long_16x9_contract_and_spinoffs(tmp_path: Path) -> None:
    """Verify YouTube Long (long_16x9) with 8 chapters and omni_platform spinoff shorts."""
    out_dir = tmp_path / "test_long_16x9"
    result = build_long_bundle(output_dir=out_dir)

    assert result["valid_contracts"] is True
    assert result["contract_errors"] == []
    assert result["format_profile"] == "long_16x9"
    assert result["scene_count"] == 8
    assert result["spinoff_shorts_count"] >= 2
    assert result["cadence_status"] == "PASS"
    assert result["cadence_warnings"] == 0
    assert result["hook_score"] >= 70

    brief_data = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    content_data = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))

    assert brief_data["aspect_ratio"] == "16:9"
    assert brief_data["format_profile"] == "long_16x9"
    assert brief_data["omni_platform"] is True
    assert brief_data["reframe_mode"] is True

    # Validate omni_platform spinoff shorts contract
    plans = short_plans(brief_data, content_data)
    assert len(plans) == 2
    for p in plans:
        assert len(p["body"]) == 4
        assert count_syllables(p["opening_hook"]) <= 18
        assert "[pause:" not in p["opening_hook"]


def test_builder_custom_topic(tmp_path: Path) -> None:
    """Verify builder produces compliant bundle for arbitrary custom topics."""
    out_dir = tmp_path / "test_custom_short"
    custom_topic = "Ủa, sao dưa hấu ngâm nước lại nổi bồng bềnh?"
    result = build_channel_bundle(format_profile="short_9x16", output_dir=out_dir, topic_str=custom_topic)

    assert result["valid_contracts"] is True
    assert result["contract_errors"] == []
    assert result["image_count"] <= 5
    assert result["cadence_status"] == "PASS"
    assert result["hook_score"] >= 70


def test_sample_production_run_committed_assets() -> None:
    """Verify that the official sample production bundle at sys/runs/ua-sao-vay-week1-9x16 is valid."""
    sys_dir = Path(__file__).resolve().parents[1]
    run_dir = sys_dir / "runs" / "ua-sao-vay-week1-9x16"

    assert run_dir.is_dir()
    brief_file = run_dir / "brief.json"
    content_file = run_dir / "content.json"
    script_file = run_dir / "script.json"
    cadence_file = run_dir / "cadence_report.json"
    outline_file = run_dir / "outline.json"
    hook_file = run_dir / "hook_score.json"

    for f in (brief_file, content_file, script_file, cadence_file, outline_file, hook_file):
        assert f.is_file(), f"Missing expected asset: {f}"

    brief_data = json.loads(brief_file.read_text(encoding="utf-8"))
    content_data = json.loads(content_file.read_text(encoding="utf-8"))
    script_data = json.loads(script_file.read_text(encoding="utf-8"))

    # Contract verification
    valid, errors = validate_production_bundle(sys_dir, brief_data, content_data)
    assert valid is True
    assert len(errors) == 0

    # Acoustic cadence check
    checker = ScriptCadenceChecker(nominal_rate=4.0)
    rep = checker.check_scenes(script_data)
    assert rep["status"] == "PASS"
    assert rep["warnings_count"] == 0
    assert rep["max_drift"] <= 0.3

    # Hook score check
    hook_res = score_content_file(content_file, CHANNEL_ID)
    assert hook_res.score >= 70
    assert not hook_res.needs_rewrite

    # Fast short image budget check
    flow_images = sum(len(sc["images"]) for sc in content_data["scenes"])
    assert flow_images <= 5

    # Check subtitles.srt and images.json
    assert (run_dir / "subtitles.srt").is_file()
    assert (run_dir / "images.json").is_file()
    images_data = json.loads((run_dir / "images.json").read_text(encoding="utf-8"))
    assert images_data["checkpoint"] == "compiled"
    assert images_data["total_images"] == flow_images


def test_sample_production_run_committed_assets_long() -> None:
    """Verify that the official sample production bundle at sys/runs/ua-sao-vay-week1-16x9 is valid."""
    sys_dir = Path(__file__).resolve().parents[1]
    run_dir = sys_dir / "runs" / "ua-sao-vay-week1-16x9"

    assert run_dir.is_dir()
    brief_file = run_dir / "brief.json"
    content_file = run_dir / "content.json"
    script_file = run_dir / "script.json"
    cadence_file = run_dir / "cadence_report.json"
    outline_file = run_dir / "outline.json"
    hook_file = run_dir / "hook_score.json"
    subtitles_file = run_dir / "subtitles.srt"
    images_file = run_dir / "images.json"

    for f in (brief_file, content_file, script_file, cadence_file, outline_file, hook_file, subtitles_file, images_file):
        assert f.is_file(), f"Missing expected asset: {f}"

    brief_data = json.loads(brief_file.read_text(encoding="utf-8"))
    content_data = json.loads(content_file.read_text(encoding="utf-8"))
    script_data = json.loads(script_file.read_text(encoding="utf-8"))

    # Contract verification
    valid, errors = validate_production_bundle(sys_dir, brief_data, content_data)
    assert valid is True
    assert len(errors) == 0

    # Acoustic cadence check
    checker = ScriptCadenceChecker(nominal_rate=4.0)
    rep = checker.check_scenes(script_data)
    assert rep["status"] == "PASS"
    assert rep["warnings_count"] == 0

    # Hook score check
    hook_res = score_content_file(content_file, CHANNEL_ID)
    assert hook_res.score >= 70

    # Spinoff shorts directory check
    spinoffs_dir = run_dir / "spinoff_shorts"
    assert spinoffs_dir.is_dir()
    sp1_dir = spinoffs_dir / "spinoff_01_short_9x16"
    sp2_dir = spinoffs_dir / "spinoff_02_short_9x16"
    assert sp1_dir.is_dir()
    assert sp2_dir.is_dir()

    for sp in (sp1_dir, sp2_dir):
        for f in ("brief.json", "content.json", "script.json", "cadence_report.json", "images.json", "subtitles.srt"):
            assert (sp / f).is_file(), f"Missing spinoff asset {f} in {sp}"


def test_video_delivery_assets() -> None:
    """Verify that export subtitles in video/ are properly generated for both jobs."""
    root_dir = Path(__file__).resolve().parents[2]
    video_dir = root_dir / "video"

    assert video_dir.is_dir()
    vid_short = video_dir / "ua-sao-vay-week1-9x16"
    vid_long = video_dir / "ua-sao-vay-week1-16x9"

    assert vid_short.is_dir()
    assert vid_long.is_dir()

    assert (vid_short / "subtitles.srt").is_file()
    assert (vid_short / "ua-sao-vay-week1-9x16.srt").is_file()
    assert (vid_long / "subtitles.srt").is_file()
    assert (vid_long / "ua-sao-vay-week1-16x9.srt").is_file()

    short_srt = (vid_short / "subtitles.srt").read_text(encoding="utf-8")
    assert "-->" in short_srt
    assert "Ủa, sao trong phòng" in short_srt

