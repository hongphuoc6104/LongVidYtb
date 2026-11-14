"""Production verification tests for Sử Kể Lại (su_ke_lai) channel."""

from __future__ import annotations

import json
from pathlib import Path

from channels.registry import get_channel
from channels.su_ke_lai.builder import (
    DEFAULT_TOPIC_LONG,
    DEFAULT_TOPIC_SHORT,
    build_su_ke_lai_long,
    build_su_ke_lai_package,
    build_su_ke_lai_short,
    build_topic_long_16x9,
    build_topic_short_9x16,
)
from content.research_story_architect import (
    check_packaging_and_localization,
    compute_brief_hash,
    validate_production_bundle,
)
from content_contract import validate_brief, validate_content
from omni_platform import short_plans
from tools.script_cadence_checker import ScriptCadenceChecker, count_syllables
from tools.script_hook_scorer import score_content_file

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
SAMPLE_RUN_DIR = SYS_DIR / "runs" / "su-ke-lai-week1-9x16"


def test_channel_su_ke_lai_registration() -> None:
    """Assert channel metadata, visual profile, voice, and speed optimizations match PLAN.md."""
    ch = get_channel("su_ke_lai")
    assert ch.id == "su_ke_lai"
    assert ch.name == "Sử Kể Lại"
    assert ch.git_branch == "channel/su-ke-lai"
    assert ch.workspace_dirname == "channel-su-ke-lai"
    assert ch.platform_routing == {"tiktok": "short_9x16", "youtube": "long_16x9"}
    assert ch.voice == "VietNarrator"
    assert ch.speed == 1.0

    # Visual style profile: ch_dong_ho_folk
    assert ch.visual.profile_id == "ch_dong_ho_folk"
    assert len(ch.visual.palette) == 6
    assert "#EFE4C8" in ch.visual.palette
    assert "#B5332E" in ch.visual.palette
    assert "#D9A520" in ch.visual.palette
    assert "#2C4A6E" in ch.visual.palette
    assert "#5E7D3A" in ch.visual.palette
    assert "#1E1E1E" in ch.visual.palette

    # Speed & Hybrid specifications
    assert ch.speed_optimization is not None
    assert ch.speed_optimization.render_mode == "flow_full_frame"
    assert ch.speed_optimization.fast_short_max_images <= 8
    assert ch.speed_optimization.spinoff_shorts_per_long >= 4


def test_builder_short_9x16_contract_and_structure(tmp_path: Path) -> None:
    """Verify builder produces Schema 3.0 short_9x16 bundle with <= 8 images and passes all contracts."""
    pkg_dir = tmp_path / "custom_short"
    res = build_su_ke_lai_short(out_dir=pkg_dir)
    assert res["valid_contracts"] is True
    assert len(res["contract_errors"]) == 0
    assert len(res["packaging_warnings"]) == 0

    required_files = (
        "brief.json",
        "content.json",
        "script.json",
        "cadence_report.json",
        "thumbnail_9x16.jpg",
        "draft/outline.json",
        "draft/content.json",
    )
    for fname in required_files:
        fpath = pkg_dir / fname
        assert fpath.is_file(), f"Missing {fname} in {pkg_dir}"
        assert fpath.stat().st_size > 0, f"Empty file {fname} in {pkg_dir}"

    brief = json.loads((pkg_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((pkg_dir / "content.json").read_text(encoding="utf-8"))

    assert brief.get("schema_version") == "3.0"
    assert content.get("schema_version") == "3.0"
    assert brief.get("format_profile") == "short_9x16"
    assert brief.get("aspect_ratio") == "9:16"
    assert brief.get("channel_profile", {}).get("id") == "su_ke_lai"

    # Fast-Short Flow image count constraint (<= 8 images)
    scenes = content.get("scenes", [])
    assert len(scenes) <= 8
    total_beats = sum(len(sc.get("images", [])) for sc in scenes)
    assert total_beats <= 8

    # Contract validations
    validate_brief(SYS_DIR, brief)
    expected_hash = compute_brief_hash(brief)
    assert content["brief_hash"] == expected_hash
    validate_content(SYS_DIR, brief, 1, expected_hash, content)

    valid, errors = validate_production_bundle(SYS_DIR, brief, content)
    assert valid is True, f"Validation errors: {errors}"
    assert len(errors) == 0

    warnings = check_packaging_and_localization(brief, scenes=scenes, check_opening_hook=True)
    assert len(warnings) == 0, f"Packaging warnings: {warnings}"


def test_builder_long_16x9_contract_and_spinoffs(tmp_path: Path) -> None:
    """Verify builder produces Schema 3.0 long_16x9 bundle with valid omni-platform spinoff shorts."""
    pkg_dir = tmp_path / "custom_long"
    res = build_su_ke_lai_long(out_dir=pkg_dir)
    assert res["valid_contracts"] is True
    assert len(res["contract_errors"]) == 0

    brief = json.loads((pkg_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((pkg_dir / "content.json").read_text(encoding="utf-8"))

    assert brief.get("format_profile") == "long_16x9"
    assert brief.get("aspect_ratio") == "16:9"
    assert brief.get("omni_platform") is True
    assert brief.get("reframe_mode") is True
    assert (pkg_dir / "thumbnail_16x9.jpg").is_file()

    # Verify 16 scenes across narrative acts
    scenes = content.get("scenes", [])
    assert len(scenes) == 16

    # Verify spinoff shorts conformance
    spinoffs = brief.get("spinoff_shorts", [])
    assert 2 <= len(spinoffs) <= 3
    plans = short_plans(brief, content)
    assert len(plans) == len(spinoffs)

    validate_brief(SYS_DIR, brief)
    validate_content(SYS_DIR, brief, 1, content["brief_hash"], content)
    valid, errors = validate_production_bundle(SYS_DIR, brief, content)
    assert valid is True, f"Validation errors: {errors}"


def test_sample_production_run_artifacts() -> None:
    """Verify the canonical sample production run at sys/runs/su-ke-lai-week1-9x16."""
    if not SAMPLE_RUN_DIR.is_dir():
        build_su_ke_lai_short(out_dir=SAMPLE_RUN_DIR)

    assert SAMPLE_RUN_DIR.is_dir(), f"Sample run directory {SAMPLE_RUN_DIR} must exist"

    required_files = (
        "brief.json",
        "content.json",
        "script.json",
        "cadence_report.json",
        "thumbnail_9x16.jpg",
        "draft/outline.json",
        "draft/content.json",
    )
    for fname in required_files:
        fpath = SAMPLE_RUN_DIR / fname
        assert fpath.is_file(), f"Missing artifact: {fname}"
        assert fpath.stat().st_size > 0, f"Artifact {fname} is empty"

    brief = json.loads((SAMPLE_RUN_DIR / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((SAMPLE_RUN_DIR / "content.json").read_text(encoding="utf-8"))
    script = json.loads((SAMPLE_RUN_DIR / "script.json").read_text(encoding="utf-8"))

    valid, errors = validate_production_bundle(SYS_DIR, brief, content)
    assert valid is True, f"Errors in sample run: {errors}"

    # Acoustic cadence check
    checker = ScriptCadenceChecker(nominal_rate=4.0, max_beat_hold_seconds=15.0)
    report = checker.check_scenes(script)
    assert report["status"] == "PASS"
    assert report["warnings_count"] == 0
    assert report["max_drift"] == 0.0
    assert 60.0 <= report["total_duration"] <= 90.0

    # Hook syllables <= 18 in opening scene SC01
    first_sentence = script[0]["narration"].split("?")[0].strip()
    syl = count_syllables(first_sentence, lang="vi")
    assert syl <= 18


def test_script_hook_scorer_reaches_target() -> None:
    """Verify script hook scorer achieves >= 70 score (100/100) on su_ke_lai script."""
    content_file = SAMPLE_RUN_DIR / "content.json"
    result = score_content_file(content_file, "su_ke_lai")
    assert result.score >= 70
    assert result.score == 100
    assert result.needs_rewrite is False
    assert result.checks["hook_short"] is True
    assert result.checks["hook_curiosity"] is True
    assert result.checks["hook_direct"] is True
    assert result.checks["open_loop"] is True
    assert result.checks["beat_density"] is True
    assert result.checks["duration_fit"] is True
    assert result.checks["closing_cta"] is True


def test_builder_package_dispatcher_and_custom_topic(tmp_path: Path) -> None:
    """Verify package dispatcher supports dual formats and custom topic titles."""
    custom_title = "Vì sao Lý Công Uẩn dời đô về Thăng Long"
    topic = build_topic_short_9x16(topic_title=custom_title)
    assert topic.topic == custom_title

    topic_long = build_topic_long_16x9(topic_title=custom_title)
    assert topic_long.topic == custom_title

    # Test dual generation
    out_custom = tmp_path / "dual_test"
    res = build_su_ke_lai_package(format_profile="short_9x16", out_dir=out_custom, topic_title=custom_title)
    assert res["valid_contracts"] is True
    brief = json.loads((out_custom / "brief.json").read_text(encoding="utf-8"))
    assert brief["topic"] == custom_title
    assert DEFAULT_TOPIC_SHORT != DEFAULT_TOPIC_LONG


def test_su_ke_lai_v2_production_lock_invariants() -> None:
    """Verify V2 production lock manifest, worktree parity, formulas, and PLAN.md section 8."""
    from channels.vn_flow_video_formulas import VN_FLOW_VIDEO_FORMULAS
    from tools.produce_vn_dual_mode import SU_KE_LAI_PRODUCTION_LOCK

    lock_path = SYS_DIR / "channels" / "su_ke_lai" / "channel_v2_production_lock.json"
    worktree_lock_path = Path(
        "/home/hongphuoc6104/Desktop/vp-channels/channel-su-ke-lai/sys/channels/su_ke_lai/channel_v2_production_lock.json"
    )
    assert lock_path.is_file(), f"Missing {lock_path}"
    assert worktree_lock_path.is_file(), f"Missing worktree copy {worktree_lock_path}"
    assert lock_path.read_bytes() == worktree_lock_path.read_bytes(), "Worktree lock manifest parity mismatch"

    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert lock["schema_version"] == "2.0"
    assert lock["channel_id"] == "su_ke_lai"
    assert lock["channel_name"] == "Sử Kể Lại"
    assert lock["status"] == "LOCKED_PRODUCTION_V2"

    v_lock = lock["voice_lock"]
    assert v_lock["voice"] == "VietNarrator_su_ke_lai"
    assert v_lock["reference_sha256"] == "7bf3594d89a04c8ac3615ae50f192c3bf5bd904c4a5bb890816f4ca977d43808"
    assert v_lock["recommended_speed"] == 1.30
    assert v_lock["base_omnivoice_speed"] == 1.12
    assert v_lock["atempo_factor"] == 1.161
    assert v_lock["inter_beat_gap_sec"] == 0.12
    assert v_lock["default_tone"] == "heroic_epic"
    assert v_lock["studio_eq_filter"] == (
        "highpass=f=80,equalizer=f=180:t=q:w=1.1:g=1.2,"
        "equalizer=f=3200:t=q:w=1.0:g=2.2,equalizer=f=6500:t=q:w=1.2:g=1.5,lowpass=f=15000"
    )
    assert v_lock["master_lufs"] == -11.0
    assert v_lock["master_true_peak_dbtp"] == -1.0

    vis_lock = lock["visual_lock"]
    assert vis_lock["visual_style_id"] == "su_ke_lai_3tier_epic_v2"
    assert vis_lock["tier_distribution"] == {
        "TIER_1_WARROOM_MAP": 0.25,
        "TIER_2_TACTICAL_CUTAWAY": 0.25,
        "TIER_3_EPIC_BATTLE_PAINTING": 0.50,
    }
    assert vis_lock["long_resolution"] == "2560x1440"
    assert vis_lock["short_resolution"] == "1080x1920"
    assert vis_lock["fps"] == 30
    assert vis_lock["xfade_transition"] == "fade"
    assert vis_lock["xfade_duration_sec"] == 0.24
    assert vis_lock["watermark_pos_2k"] == "W-w-48:H-h-48"
    assert vis_lock["watermark_pos_hd"] == "W-w-36:H-h-36"

    ep = lock["benchmark_episode"]
    assert ep["job_id"] == "vn_su_ke_lai_ep04_nhu_nguyet_1077_long"
    assert ep["duration_sec"] == 582.875
    assert ep["nb_frames"] == 17486
    assert ep["beats_count"] == 240
    assert ep["chapters_count"] == 10
    assert ep["mp4_relpath"] == "video/vn_su_ke_lai_ep04_nhu_nguyet_1077_long/final_long_2k.mp4"
    assert ep["mp4_bytes"] == 551657507
    assert len(ep["mp4_sha256"]) == 64

    assert VN_FLOW_VIDEO_FORMULAS["su_ke_lai"]["recommended_speed"] == 1.30
    assert SU_KE_LAI_PRODUCTION_LOCK["recommended_speed"] == 1.30

    plan_text = (SYS_DIR / "channels" / "su_ke_lai" / "PLAN.md").read_text(encoding="utf-8")
    assert "## 8. Chuẩn Sản Xuất V2 Đã Chốt (Voice 1.30x & 3-Tier Epic Historical Visuals)" in plan_text
    assert "VietNarrator_su_ke_lai" in plan_text
    assert "su_ke_lai_3tier_epic_v2" in plan_text
    assert "xfade=fade" in plan_text


def test_su_ke_lai_v3_skill_and_routing_index() -> None:
    """Verify vp-channel-su-ke-lai skill, routing index links, and worktree parity."""
    skill_dir = ROOT_DIR / ".agents" / "skills" / "vp-channel-su-ke-lai"
    skill_md = skill_dir / "SKILL.md"
    visual_ref = skill_dir / "references" / "visual-grammar-option1.md"
    pacing_ref = skill_dir / "references" / "pacing-and-script-rules.md"

    for path in (skill_md, visual_ref, pacing_ref):
        assert path.is_file(), f"Missing skill file: {path}"

    skill_text = skill_md.read_text(encoding="utf-8")
    assert "name: vp-channel-su-ke-lai" in skill_text
    assert "su_ke_lai_35mm_live_action_v3" in skill_text
    assert "VietNarrator_su_ke_lai" in skill_text
    assert "Bảng Ghép Nối Quy Trình Dùng Chung" in skill_text
    assert "FULLY OVERRIDES" not in skill_text
    assert "vp-full-frame-quality" in skill_text
    assert "references/visual-grammar-option1.md" in skill_text
    assert "references/pacing-and-script-rules.md" in skill_text

    visual_text = visual_ref.read_text(encoding="utf-8")
    assert "su_ke_lai_35mm_live_action_v3" in visual_text
    assert "allowed_text=None" in visual_text

    pacing_text = pacing_ref.read_text(encoding="utf-8")
    assert "VietNarrator_su_ke_lai" in pacing_text
    assert "240" in pacing_text

    root_index = (ROOT_DIR / "INDEX.md").read_text(encoding="utf-8")
    docs_index = (SYS_DIR / "docs" / "INDEX.md").read_text(encoding="utf-8")
    prod_skill = (ROOT_DIR / ".agents" / "skills" / "vp-production" / "SKILL.md").read_text(encoding="utf-8")
    plan_text = (SYS_DIR / "channels" / "su_ke_lai" / "PLAN.md").read_text(encoding="utf-8")

    assert "vp-channel-su-ke-lai" in root_index
    assert "Channel-to-Skill Routing & Composition Matrix" in root_index
    assert "vp-channel-su-ke-lai" in docs_index
    assert "14 Skills" in docs_index
    assert "vp-channel-su-ke-lai" not in prod_skill
    assert "su_ke_lai" not in prod_skill
    assert ".agents/skills/vp-channel-su-ke-lai/SKILL.md" in plan_text

    worktree_root = Path("/home/hongphuoc6104/Desktop/vp-channels/channel-su-ke-lai")
    parity_relpaths = (
        ".agents/skills/vp-channel-su-ke-lai/SKILL.md",
        ".agents/skills/vp-channel-su-ke-lai/references/visual-grammar-option1.md",
        ".agents/skills/vp-channel-su-ke-lai/references/pacing-and-script-rules.md",
        ".agents/skills/vp-production/SKILL.md",
        "INDEX.md",
        "sys/docs/INDEX.md",
        "sys/channels/su_ke_lai/PLAN.md",
        "sys/tests/test_channel_su_ke_lai.py",
    )
    for rel in parity_relpaths:
        src = ROOT_DIR / rel
        dst = worktree_root / rel
        assert dst.is_file(), f"Missing worktree mirror file: {dst}"
        assert src.read_bytes() == dst.read_bytes(), f"Worktree parity mismatch for {rel}"

