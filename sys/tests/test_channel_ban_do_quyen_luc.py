"""Production verification tests for Bản Đồ Quyền Lực (ban_do_quyen_luc) dedicated skill and v3 lock."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))


def test_ban_do_quyen_luc_v3_skill_and_routing_index() -> None:
    """Verify ban_do_quyen_luc 3-pillar data playbook and consolidated registry isolation."""
    registry_skill = ROOT_DIR / ".agents" / "skills" / "vp-channel-registry" / "SKILL.md"
    legacy_skill_dir = ROOT_DIR / ".agents" / "skills" / "vp-channel-ban-do-quyen-luc"
    pb_dir = SYS_DIR / "channels" / "ban_do_quyen_luc" / "playbook"
    skill_md = pb_dir / "overview.md"
    content_ref = pb_dir / "content.md"
    visual_ref = pb_dir / "visual.md"
    pacing_ref = pb_dir / "pacing.md"

    assert registry_skill.is_file(), f"Missing consolidated registry skill: {registry_skill}"
    assert not legacy_skill_dir.exists(), f"Per-channel skill should be retired: {legacy_skill_dir}"
    for path in (skill_md, content_ref, visual_ref, pacing_ref):
        assert path.is_file(), f"Missing playbook file: {path}"

    skill_text = skill_md.read_text(encoding="utf-8")
    assert "ban_do_quyen_luc_4styles_photoreal_v3" in skill_text
    assert "VietNarrator_ban_do_quyen_luc" in skill_text
    assert "Bảng Ghép Nối Quy Trình Dùng Chung" in skill_text
    assert "100% shared and unmodified" in skill_text
    assert "CACH_1_HERO_STAMP" in skill_text
    assert "CACH_2_SPLIT_COMPARE" in skill_text
    assert "CACH_3_DOSSIER_LIST" in skill_text
    assert "CACH_4_CINEMATIC_PACING" in skill_text
    assert "(visual.md)" in skill_text
    assert "(pacing.md)" in skill_text

    visual_text = visual_ref.read_text(encoding="utf-8")
    assert "ban_do_quyen_luc_4styles_photoreal_v3" in visual_text
    assert "allowed_text=None" in visual_text
    for mode in ("CACH_1_HERO_STAMP", "CACH_2_SPLIT_COMPARE", "CACH_3_DOSSIER_LIST", "CACH_4_CINEMATIC_PACING"):
        assert mode in visual_text

    pacing_text = pacing_ref.read_text(encoding="utf-8")
    assert "VietNarrator_ban_do_quyen_luc" in pacing_text
    assert "240" in pacing_text

    root_index = (ROOT_DIR / "INDEX.md").read_text(encoding="utf-8")
    docs_index = (SYS_DIR / "docs" / "INDEX.md").read_text(encoding="utf-8")
    prod_skill = (ROOT_DIR / ".agents" / "skills" / "vp-production" / "SKILL.md").read_text(encoding="utf-8")
    plan_text = (SYS_DIR / "channels" / "ban_do_quyen_luc" / "PLAN.md").read_text(encoding="utf-8")

    assert "vp-channel-registry" in root_index
    assert "ban_do_quyen_luc/playbook/overview.md" in root_index
    assert "vp-channel-registry" in docs_index
    assert "ban_do_quyen_luc/playbook/overview.md" in docs_index
    assert "vp-channel-ban-do-quyen-luc" not in prod_skill
    assert "ban_do_quyen_luc" not in prod_skill
    assert "playbook/overview.md" in plan_text


def test_ban_do_quyen_luc_v3_production_lock_and_formulas() -> None:
    """Verify channel_v3_production_lock.json and V3 formula entries stay synchronized."""
    from channels.vn_competitor_script_formulas import VN_COMPETITOR_SCRIPT_FORMULAS
    from channels.vn_flow_video_formulas import VN_FLOW_VIDEO_FORMULAS

    lock_path = SYS_DIR / "channels" / "ban_do_quyen_luc" / "channel_v3_production_lock.json"
    assert lock_path.is_file(), f"Missing {lock_path}"

    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert lock["schema_version"] == "3.0"
    assert lock["channel_id"] == "ban_do_quyen_luc"
    assert lock["status"] == "LOCKED_PRODUCTION_V3"
    assert lock["voice_id"] == "VietNarrator_ban_do_quyen_luc"
    assert lock["recommended_speed"] == 1.15

    vg = lock["visual_grammar"]
    assert vg["version"] == "ban_do_quyen_luc_4styles_photoreal_v3"
    assert len(vg["three_pillars"]) == 3
    assert set(vg["four_visual_modes"].keys()) == {
        "CACH_1_HERO_STAMP",
        "CACH_2_SPLIT_COMPARE",
        "CACH_3_DOSSIER_LIST",
        "CACH_4_CINEMATIC_PACING",
    }

    ep = lock["benchmark_episode"]
    assert ep["job_id"] == "vn_ban_do_quyen_luc_ep05_ban_do_dat_hiem_long"
    assert ep["video_id"] == "HLmYROh1YfA"
    assert ep["beats_count"] == 240
    assert ep["chapters_count"] == 9
    assert ep["short_benchmark"]["video_id"] == "AMWZ3v30SJ4"

    flow = VN_FLOW_VIDEO_FORMULAS["ban_do_quyen_luc"]
    assert flow["visual_style_id"] == "ban_do_quyen_luc_4styles_photoreal_v3"
    assert flow["voice_profile_id"] == "VietNarrator_ban_do_quyen_luc"
    assert flow["recommended_speed"] == 1.15
    assert "strictly zero text" in flow["continuity_anchor"].lower()

    script_f = VN_COMPETITOR_SCRIPT_FORMULAS["ban_do_quyen_luc"]
    assert script_f["voice_id"] == "VietNarrator_ban_do_quyen_luc"
    assert script_f["visual_4styles_combination_rule"]["version"] == "ban_do_quyen_luc_4styles_photoreal_v3"
