"""Test suite verifying Channel: Cơ Thể Kể (co_the_ke) V3 2K production readiness.

Covers:
- Channel profile registration with 3D Endoscopic Biomedical V3 grammar & VietNarrator_co_the_ke (1.12x)
- V3 skill (.agents/skills/vp-channel-co-the-ke), routing index, and non-interference with shared skills
- V3 production lock manifest (channel_v3_production_lock.json), HARDCODED_CHANNEL_VOICE_LOCKS, and formulas sync
- Builder topic generation for short_9x16 & long_16x9 with Schema 3.0 compliance & zero kawaii/stickman slop
- Regression guards for visual_pacing Short-as-Long fix and cta_tone_linter Long/Outro enforcement
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.co_the_ke.builder import (  # noqa: E402
    build_characters,
    build_co_the_ke_bundle,
    build_week1_long_topic,
    build_week1_short_topic,
    export_package,
)
from channels.registry import get_channel  # noqa: E402
from content.research_story_architect import validate_production_bundle  # noqa: E402
from content_contract import validate_brief, validate_content  # noqa: E402
from omni_platform import short_plans  # noqa: E402
from tools.cta_tone_linter import lint_cta  # noqa: E402
from tools.script_cadence_checker import count_syllables  # noqa: E402
from tools.script_hook_scorer import score_script  # noqa: E402
from visual_pacing import check_see_say_beat_density  # noqa: E402


def test_channel_profile_registration_and_plan() -> None:
    """Verify co_the_ke V3 registration uses 3D biomedical grammar and zero #learnontiktok."""
    ch = get_channel("co_the_ke")
    assert ch.id == "co_the_ke"
    assert ch.name == "Cơ Thể Kể"
    assert ch.niche == "Sức khỏe và cơ thể được nhân hóa"
    assert ch.visual.profile_id == "ch_co_the_ke_biomedical_v3"
    assert ch.voice == "VietNarrator_co_the_ke"
    assert ch.speed == 1.12
    assert "#learnontiktok" not in ch.hashtags
    assert ch.short_spec.duration_seconds == (48, 60)
    assert ch.long_spec.duration_seconds == (510, 780)

    assert ch.speed_optimization is not None
    assert ch.speed_optimization.render_mode == "flow_full_frame"
    assert ch.speed_optimization.fast_short_max_images <= 8

    plan_path = SYS_DIR / "channels" / "co_the_ke" / "PLAN.md"
    assert plan_path.is_file()
    plan_text = plan_path.read_text(encoding="utf-8")
    assert "co_the_ke_3d_biomedical_v3" in plan_text
    assert "VietNarrator_co_the_ke" in plan_text

    chars = build_characters()
    assert len(chars) == 5
    for c in chars:
        assert "kawaii" not in c["appearance"].lower()
        assert "stickman" not in c["appearance"].lower()


def test_co_the_ke_v3_skill_and_routing_index() -> None:
    """Verify co_the_ke 3-pillar data playbook and zero legacy per-channel skill isolation."""
    registry_skill = ROOT_DIR / ".agents" / "skills" / "vp-channel-registry" / "SKILL.md"
    legacy_skill_dir = ROOT_DIR / ".agents" / "skills" / "vp-channel-co-the-ke"
    pb_dir = ROOT_DIR / "sys" / "channels" / "co_the_ke" / "playbook"
    skill_md = pb_dir / "overview.md"
    content_ref = pb_dir / "content.md"
    visual_ref = pb_dir / "visual.md"
    pacing_ref = pb_dir / "pacing.md"

    assert registry_skill.is_file(), f"Missing consolidated registry skill: {registry_skill}"
    assert not legacy_skill_dir.exists(), f"Per-channel skill should be retired: {legacy_skill_dir}"
    for p in (skill_md, content_ref, visual_ref, pacing_ref):
        assert p.is_file(), f"Missing playbook file: {p}"

    skill_text = skill_md.read_text(encoding="utf-8")
    assert "co_the_ke_3d_biomedical_v3" in skill_text
    assert "VietNarrator_co_the_ke" in skill_text
    for mode in (
        "MODE_1_BIOMETRIC_STAMP",
        "MODE_2_NORMAL_VS_STRESS_SPLIT",
        "MODE_3_CASCADE_CHECKLIST",
        "MODE_4_ENDOSCOPIC_PACING",
    ):
        assert mode in skill_text

    visual_text = visual_ref.read_text(encoding="utf-8")
    assert "co_the_ke_3d_biomedical_v3" in visual_text
    assert "allowed_text=None" in visual_text
    for color in ("#0A192F", "#06B6D4", "#EF4444"):
        assert color in visual_text

    pacing_text = pacing_ref.read_text(encoding="utf-8")
    assert "1.12" in pacing_text
    assert "240" in pacing_text
    assert "18" in pacing_text

    root_index = (ROOT_DIR / "INDEX.md").read_text(encoding="utf-8")
    docs_index = (SYS_DIR / "docs" / "INDEX.md").read_text(encoding="utf-8")
    prod_skill = (ROOT_DIR / ".agents" / "skills" / "vp-production" / "SKILL.md").read_text(encoding="utf-8")
    plan_text = (SYS_DIR / "channels" / "co_the_ke" / "PLAN.md").read_text(encoding="utf-8")
    assert "vp-channel-registry" in root_index
    assert "co_the_ke/playbook/overview.md" in root_index
    assert "vp-channel-registry" in docs_index
    assert "co_the_ke/playbook/overview.md" in docs_index
    assert "vp-channel-co-the-ke" not in prod_skill
    assert "co_the_ke" not in prod_skill
    assert "playbook/overview.md" in plan_text


def _load_dual_mode_locks() -> dict[str, Any]:
    """Load co_the_ke constants and verify_channel_voice_lock safely under any PYTHONPATH."""
    try:
        from tools.produce_vn_dual_mode import (
            CO_THE_KE_PRODUCTION_LOCK,
            CO_THE_KE_VOICE_SHA256,
            HARDCODED_CHANNEL_VOICE_LOCKS,
            verify_channel_voice_lock,
        )
        return {
            "CO_THE_KE_PRODUCTION_LOCK": CO_THE_KE_PRODUCTION_LOCK,
            "CO_THE_KE_VOICE_SHA256": CO_THE_KE_VOICE_SHA256,
            "HARDCODED_CHANNEL_VOICE_LOCKS": HARDCODED_CHANNEL_VOICE_LOCKS,
            "verify_channel_voice_lock": verify_channel_voice_lock,
        }
    except ModuleNotFoundError:
        src_path = SYS_DIR / "tools" / "produce_vn_dual_mode.py"
        tree = ast.parse(src_path.read_text(encoding="utf-8"))
        wanted = {
            "HO_SO_KY_LA_VOICE_SHA256",
            "CO_THE_KE_VOICE_SHA256",
            "SU_KE_LAI_SHARED_VOICE_SHA256",
            "SU_KE_LAI_DEDICATED_VOICE_SHA256",
            "BANNED_DEPRECATED_VOICE_SHA256S",
            "HARDCODED_CHANNEL_VOICE_LOCKS",
            "BOTTOM_RIGHT_WATERMARK_POS",
            "CO_THE_KE_PRODUCTION_LOCK",
        }
        ns: dict[str, Any] = {"Any": Any, "Path": Path, "hashlib": hashlib, "json": json, "ROOT": ROOT_DIR}
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in wanted for t in node.targets
            ):
                exec(compile(ast.Module([node], type_ignores=[]), str(src_path), "exec"), ns)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in wanted:
                exec(compile(ast.Module([node], type_ignores=[]), str(src_path), "exec"), ns)
            elif isinstance(node, ast.FunctionDef) and node.name == "verify_channel_voice_lock":
                exec(compile(ast.Module([node], type_ignores=[]), str(src_path), "exec"), ns)
        return ns


def test_co_the_ke_v3_production_lock_and_formulas() -> None:
    """Verify channel_v3_production_lock.json, produce_vn_dual_mode, and formula registries align."""
    from channels.vn_competitor_script_formulas import VN_COMPETITOR_SCRIPT_FORMULAS
    from channels.vn_flow_video_formulas import VN_FLOW_VIDEO_FORMULAS

    dm = _load_dual_mode_locks()
    CO_THE_KE_PRODUCTION_LOCK = dm["CO_THE_KE_PRODUCTION_LOCK"]
    CO_THE_KE_VOICE_SHA256 = dm["CO_THE_KE_VOICE_SHA256"]
    HARDCODED_CHANNEL_VOICE_LOCKS = dm["HARDCODED_CHANNEL_VOICE_LOCKS"]
    verify_channel_voice_lock = dm["verify_channel_voice_lock"]

    lock_path = SYS_DIR / "channels" / "co_the_ke" / "channel_v3_production_lock.json"
    assert lock_path.is_file()
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert lock["schema_version"] == "3.0"
    assert lock["channel_id"] == "co_the_ke"
    assert lock["handle"] == "@CoTheKeVN"
    assert lock["recommended_speed"] == 1.12
    assert lock["visual_lock"]["long_resolution"] == "2560x1440"
    assert lock["visual_lock"]["short_resolution"] == "1440x2560"

    assert CO_THE_KE_PRODUCTION_LOCK["voice"] == "VietNarrator_co_the_ke"
    assert CO_THE_KE_PRODUCTION_LOCK["recommended_speed"] == 1.12
    assert CO_THE_KE_PRODUCTION_LOCK["visual_style_id"] == "co_the_ke_3d_biomedical_v3"
    assert HARDCODED_CHANNEL_VOICE_LOCKS["co_the_ke"]["expected_sha256"] == CO_THE_KE_VOICE_SHA256

    verified = verify_channel_voice_lock("co_the_ke", root=ROOT_DIR)
    assert verified["sha256"] == CO_THE_KE_VOICE_SHA256
    assert verified["recommended_speed"] == 1.12

    flow_f = VN_FLOW_VIDEO_FORMULAS["co_the_ke"]
    assert flow_f["visual_style_id"] == "co_the_ke_3d_biomedical_v3"
    assert flow_f["voice_profile_id"] == "VietNarrator_co_the_ke"
    assert flow_f["recommended_speed"] == 1.12

    script_f = VN_COMPETITOR_SCRIPT_FORMULAS["co_the_ke"]
    assert script_f["voice_id"] == "VietNarrator_co_the_ke"
    assert script_f["recommended_speed"] == 1.12
    assert script_f["visual_4modes_biomedical_rule"]["version"] == "co_the_ke_3d_biomedical_v3"

    setup_spec = json.loads((SYS_DIR / "channels/co_the_ke/assets/channel_setup_spec.json").read_text(encoding="utf-8"))
    assert "learnontiktok" not in json.dumps(setup_spec, ensure_ascii=False).lower()


def test_short_9x16_contract_and_export(tmp_path: Path) -> None:
    """Verify V3 9:16 builder generates Schema 3.0 compliant package with clean 3D biomedical prompts."""
    topic = build_week1_short_topic()
    assert topic.format_profile == "short_9x16"
    assert topic.voice == "VietNarrator_co_the_ke"
    assert topic.speed == 1.12

    first_sentence = topic.scenes[0].narration.split(".")[0]
    assert count_syllables(first_sentence, lang="vi") <= 18
    assert "[pause:" not in first_sentence

    for sc in topic.scenes:
        for beat in sc.visual_beats or []:
            low = f"{beat.description} {beat.preserve} {beat.change}".lower()
            assert "kawaii" not in low
            assert "doodle" not in low
            assert "stickman" not in low

    out_dir = tmp_path / "test_short_v3"
    res = export_package(topic, out_dir, system_root=SYS_DIR)
    assert res["valid_contracts"] is True

    b = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    c = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))
    validate_brief(SYS_DIR, b)
    validate_content(SYS_DIR, b, 1, c["brief_hash"], c)
    ok, errs = validate_production_bundle(SYS_DIR, b, c)
    assert ok is True, errs

    hook_res = score_script([sc["narration"] for sc in c["scenes"]], channel_id="co_the_ke", format_profile="short_9x16")
    assert hook_res.score >= 70


def test_long_16x9_contract_and_spinoff_shorts(tmp_path: Path) -> None:
    """Verify V3 16:9 builder generates valid package and omni_plan."""
    topic, omni_plan = build_week1_long_topic()
    assert topic.format_profile == "long_16x9"
    assert topic.voice == "VietNarrator_co_the_ke"
    assert topic.speed == 1.12

    out_dir = tmp_path / "test_long_v3"
    res = export_package(topic, out_dir, omni_plan=omni_plan, system_root=SYS_DIR)
    assert res["valid_contracts"] is True

    b = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    c = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))
    ok, errs = validate_production_bundle(SYS_DIR, b, c)
    assert ok is True, errs

    plans = short_plans(b, c)
    assert 2 <= len(plans) <= 3
    for plan in plans:
        assert len(plan["body"]) == 4

    hook_res = score_script([sc["narration"] for sc in c["scenes"]], channel_id="co_the_ke", format_profile="long_16x9")
    assert hook_res.score >= 70


def test_builder_cli_helper(tmp_path: Path) -> None:
    """Verify build_co_the_ke_bundle helper builds valid V3 short_9x16 audit."""
    res = build_co_the_ke_bundle(
        format_choice="short_9x16",
        out_dir=tmp_path,
        job_name="cli-test-short-v3",
    )
    audit = res["short_9x16"]["audit"]
    assert audit["valid_contracts"] is True
    assert audit["hook_score"] >= 70


def test_visual_pacing_short_not_misclassified_as_long() -> None:
    """Regression: sparse short_9x16 (>2.8s/beat average, <=120s) must fail Short thresholds, not pass as Long."""
    # 12 beats spread evenly across 42s -> avg 3.5s/beat (>2.8s), only 2 beats in 0..5s
    sparse_short_scenes = [
        {
            "id": "SC01",
            "start": 0.0,
            "end": 21.0,
            "images": [{"id": f"I{i}", "at": round(i * 3.5, 2)} for i in range(6)],
        },
        {
            "id": "SC02",
            "start": 21.0,
            "end": 42.0,
            "images": [{"id": f"J{i}", "at": round(i * 3.5, 2)} for i in range(6)],
        },
    ]
    errors = check_see_say_beat_density(sparse_short_scenes, format_profile="short_9x16")
    assert errors, "Sparse short_9x16 must not be misclassified as long_16x9"
    assert any("LOW_VISUAL_BEAT_DENSITY" in e or "OPENING_VISUAL_DENSITY" in e for e in errors)


def test_cta_tone_linter_long_spoken_and_short_outro_budget() -> None:
    """Regression: lint_cta rejects Long with unspoken declared CTAs and Short with oversized combined outro."""
    long_brief = {
        "format_profile": "long_16x9",
        "cta_plan": {
            "mid_cta": "Ghi nhớ nguyên tắc nhịp sinh học này.",
            "close": "Bạn thường đi ngủ lúc mấy giờ, chia sẻ cùng Cơ Thể Kể nhé.",
        },
    }
    unspoken_long_content = {
        "scenes": [
            {"id": "SC01", "narration": "Mở đầu về đồng hồ sinh học."},
            {"id": "SC02", "narration": "Cơ chế tiết melatonin ở tuyến tùng."},
            {"id": "SC03", "narration": "Kết thúc giải thích ngắn gọn."},
        ]
    }
    long_errs = lint_cta(long_brief, unspoken_long_content)
    assert any("CTA_CLOSE_NOT_IN_OUTRO" in e for e in long_errs)
    assert any("CTA_MID_NOT_IN_BODY" in e for e in long_errs)

    short_brief = {
        "format_profile": "short_9x16",
        "parent_long_id": "sgp65IoBMa8",
        "cta_plan": {
            "bridge": " ".join(["từ"] * 21),
            "close": " ".join(["chữ"] * 21),
        },
    }
    short_content = {
        "scenes": [
            {"id": "SC01", "narration": "Mở đầu ngắn."},
            {"id": "SC02", "narration": f"{short_brief['cta_plan']['bridge']} {short_brief['cta_plan']['close']}"},
        ]
    }
    short_errs = lint_cta(short_brief, short_content)
    assert any("CTA_OUTRO_SYLLABLES_EXCEEDED" in e for e in short_errs)
