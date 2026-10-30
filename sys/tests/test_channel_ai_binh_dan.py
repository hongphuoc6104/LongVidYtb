"""Verification and regression tests for channel 'ai_binh_dan' (AI Bình Dân)."""

from __future__ import annotations

import json
from pathlib import Path

from channels.ai_binh_dan.builder import (
    build_long_topic,
    build_short_topic,
    build_week1_long_topic,
    build_week1_short_topic,
    export_package,
)
from channels.registry import get_channel
from content.research_story_architect import validate_production_bundle
from tools.script_cadence_checker import ScriptCadenceChecker
from tools.script_hook_scorer import score_script

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
WEEK1_RUN_DIR = SYS_DIR / "runs" / "ai-binh-dan-week1-9x16"


def test_channel_registry_and_active_config() -> None:
    ch = get_channel("ai_binh_dan")
    assert ch.id == "ai_binh_dan"
    assert ch.name == "AI Bình Dân"
    assert ch.niche == "Mẹo dùng AI và công nghệ cho người thường"
    assert ch.promise == "Một mẹo AI làm được ngay trong 1 phút, không cần biết code."
    assert ch.audience == "Người đi làm văn phòng, sinh viên, chủ shop nhỏ"
    assert ch.persona == "Đồng nghiệp rành công nghệ, chỉ từng bước 'làm theo liền'"
    assert ch.tone == "Thực chiến, nhanh, hào hứng, chỉ từng bước"
    assert ch.voice == "VietNarrator"
    assert ch.speed == 1.0
    assert ch.visual.profile_id == "ch_tech_doodle"
    assert ch.platform_routing == {"tiktok": "short_9x16", "youtube": "long_16x9"}

    so = ch.speed_optimization
    assert so is not None
    assert so.render_mode == "screen_capture_hybrid"
    assert so.fast_short_max_images == 4
    assert so.spinoff_shorts_per_long == 5
    assert so.remotion_motion_ratio == 0.60
    assert so.estimated_short_minutes == (5, 8)

    active_cfg_path = SYS_DIR / "channels" / "active_channel.json"
    if active_cfg_path.is_file():
        active = json.loads(active_cfg_path.read_text(encoding="utf-8"))
        assert active["channel_id"] == "ai_binh_dan"
        assert active["visual_profile_id"] == "ch_tech_doodle"
        assert active["speed_optimization"]["fast_short_max_images"] == 4
        assert active["speed_optimization"]["spinoff_shorts_per_long"] == 5


def test_builder_week1_short_contracts_and_cadence() -> None:
    topic = build_week1_short_topic()
    assert topic.format_profile == "short_9x16"
    assert topic.aspect_ratio == "9:16"
    assert topic.channel_id == "ai_binh_dan"
    assert len(topic.scenes) == 4

    total_images = sum(len(sc.visual_beats) for sc in topic.scenes)
    assert total_images <= 4, f"Fast-short exceeds 4 Flow images: {total_images}"

    pkg = topic.packaging
    assert pkg is not None
    assert len(pkg.youtube_title) <= 55
    assert 2 <= len(pkg.text_overlay.split()) <= 4
    assert pkg.text_overlay.isupper()

    narrations = [sc.narration for sc in topic.scenes]
    hook_res = score_script(narrations, "ai_binh_dan", "short_9x16")
    assert hook_res.score >= 70, f"Hook score below threshold: {hook_res.score}"
    assert hook_res.checks.get("hook_short") is True
    assert hook_res.checks.get("hook_curiosity") is True
    assert hook_res.checks.get("hook_direct") is True
    assert hook_res.checks.get("closing_cta") is True

    checker = ScriptCadenceChecker(nominal_rate=4.0)
    cad_report = checker.check_scenes(
        [{"id": s.scene_id, "title": s.title, "duration": s.duration, "narration": s.narration} for s in topic.scenes]
    )
    assert cad_report["status"] == "PASS"
    assert cad_report["warnings_count"] == 0
    assert cad_report["max_drift"] <= 0.05


def test_builder_week1_long_contracts_and_spinoffs() -> None:
    topic = build_week1_long_topic()
    assert topic.format_profile == "long_16x9"
    assert topic.aspect_ratio == "16:9"
    assert topic.channel_id == "ai_binh_dan"
    assert len(topic.scenes) >= 14

    assert topic.spinoff_shorts is not None
    assert len(topic.spinoff_shorts) == 5
    for sp in topic.spinoff_shorts:
        assert sp["format_profile"] == "short_9x16"
        assert len(sp["opening_hook"].split()) <= 18
        assert sp["scene_count"] >= 1

    pkg = topic.packaging
    assert pkg is not None
    assert len(pkg.youtube_title) <= 55
    assert 2 <= len(pkg.text_overlay.split()) <= 4
    assert pkg.text_overlay.isupper()

    editorial = topic.human_editorial
    assert editorial is not None
    assert len(editorial.get("topic_dilemmas", [])) >= 3
    assert len(editorial.get("dynamic_questions", [])) >= 3
    assert len(editorial.get("expanded_content_ideas", [])) >= 3

    narrations = [sc.narration for sc in topic.scenes]
    hook_res = score_script(narrations, "ai_binh_dan", "long_16x9")
    assert hook_res.score >= 70, f"Long hook score below threshold: {hook_res.score}"

    checker = ScriptCadenceChecker(nominal_rate=4.0)
    cad_report = checker.check_scenes(
        [{"id": s.scene_id, "title": s.title, "duration": s.duration, "narration": s.narration} for s in topic.scenes]
    )
    assert cad_report["status"] == "PASS"
    assert cad_report["warnings_count"] == 0


def test_builder_custom_topic_short() -> None:
    custom_title = "Dùng AI Tóm Tắt Tài Liệu Năm Mươi Trang"
    topic = build_short_topic(custom_title)
    assert topic.format_profile == "short_9x16"
    assert len(topic.scenes) == 4
    total_images = sum(len(sc.visual_beats) for sc in topic.scenes)
    assert total_images <= 4

    narrations = [sc.narration for sc in topic.scenes]
    hook_res = score_script(narrations, "ai_binh_dan", "short_9x16")
    assert hook_res.score >= 70


def test_builder_custom_topic_long() -> None:
    custom_title = "5 Quy Trình Tự Động Hóa AI Cho Người Thường"
    topic = build_long_topic(custom_title)
    assert topic.format_profile == "long_16x9"
    assert topic.topic == custom_title
    assert len(topic.scenes) >= 14
    assert topic.spinoff_shorts is not None
    assert len(topic.spinoff_shorts) == 5



def test_export_package_e2e(tmp_path: Path) -> None:
    short_topic = build_week1_short_topic()
    out_dir = tmp_path / "test_short"
    res = export_package(short_topic, out_dir, system_root=SYS_DIR)

    assert res["valid_contracts"] is True
    assert len(res["contract_errors"]) == 0
    assert res["hook_score"] >= 70
    assert res["cadence_status"] == "PASS"
    assert res["scene_count"] == 4
    assert res["total_images"] <= 4

    assert (out_dir / "brief.json").is_file()
    assert (out_dir / "content.json").is_file()
    assert (out_dir / "script.json").is_file()
    assert (out_dir / "cadence_report.json").is_file()
    assert (out_dir / "draft" / "outline.json").is_file()
    assert (out_dir / "draft" / "content.json").is_file()

    b = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    c = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))
    valid, errors = validate_production_bundle(SYS_DIR, b, c)
    assert valid is True
    assert len(errors) == 0


def test_runs_week1_sample_package_integrity() -> None:
    if not WEEK1_RUN_DIR.is_dir():
        export_package(build_week1_short_topic(), WEEK1_RUN_DIR, system_root=SYS_DIR)
    assert WEEK1_RUN_DIR.is_dir(), f"Missing runs bundle: {WEEK1_RUN_DIR}"
    assert (WEEK1_RUN_DIR / "brief.json").is_file()
    assert (WEEK1_RUN_DIR / "content.json").is_file()
    assert (WEEK1_RUN_DIR / "script.json").is_file()
    assert (WEEK1_RUN_DIR / "cadence_report.json").is_file()

    b = json.loads((WEEK1_RUN_DIR / "brief.json").read_text(encoding="utf-8"))
    c = json.loads((WEEK1_RUN_DIR / "content.json").read_text(encoding="utf-8"))
    valid, errors = validate_production_bundle(SYS_DIR, b, c)
    assert valid is True, f"Contract errors: {errors}"
    assert len(errors) == 0

    assert b["channel_profile"]["id"] == "ai_binh_dan"
    assert b["format_profile"] == "short_9x16"
    assert len(c["scenes"]) == 4

    total_images = sum(len(sc.get("images", [])) for sc in c["scenes"])
    assert total_images <= 4

    hook_res = score_script([sc["narration"] for sc in c["scenes"]], "ai_binh_dan", "short_9x16")
    assert hook_res.score >= 70

    cadence = json.loads((WEEK1_RUN_DIR / "cadence_report.json").read_text(encoding="utf-8"))
    assert cadence["status"] == "PASS"
    assert cadence["warnings_count"] == 0
    assert cadence["max_drift"] <= 0.05
