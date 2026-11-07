"""Unit tests for V3.3 Vietnamese Competitor-Rebuilt Pipeline, Per-Channel Formulas,
Registry Competitor Bridges, Builders Integration, and Spec Validation Suite.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools"), str(ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.builders import (  # noqa: E402
    build_channel_topic,
    build_rebuilt_channel_brief,
)
from channels.registry import (  # noqa: E402
    apply_rebuilt_channel,
    get_rebuilt_competitor_formula,
    get_rebuilt_visual_identity,
)
from channels.vn_competitor_script_formulas import (  # noqa: E402
    VN_COMPETITOR_SCRIPT_FORMULAS,
    get_vn_competitor_script_formula,
)
from channels.vn_flow_video_formulas import (  # noqa: E402
    FLOW_FRAME_CONTROL_MODES,
    RETENTION_SHOT_BLUEPRINTS,
    VN_CHANNEL_LOGO_PROMPTS,
    VN_FLOW_VIDEO_FORMULAS,
    build_vn_channel_motion_prompt,
    build_vn_reference_keyframe_prompt,
)
from tools.rebuild_vn_from_competitor_frames import (  # noqa: E402
    VALID_CAMERAS,
    count_vietnamese_syllables,
    validate_all_vn_specs,
)

EXPECTED_20_VN_SLUGS = [
    "tui-tien",
    "banh-rang",
    "luat-doi-thuong",
    "la-ban-hoc-thuat",
    "luat-ngam",
    "ua-sao-vay",
    "dia-com",
    "vu-tru-ti-hon",
    "chanh-niem-ke",
    "minh-triet-song",
    "co-the-ke",
    "su-ke-lai",
    "ho-so-ky-la",
    "ban-do-quyen-luc",
    "loi-sang-soi",
    "nao-luoi",
    "thuong-cho-kheo",
    "nghe-song-sot",
    "ai-binh-dan",
    "tam-tinh-dem",
]

EXPECTED_18_EN_SLUGS = [
    "en-first-principles",
    "en-scale-and-bone",
    "en-pocket-cosmos",
    "en-deep-time-strata",
    "en-inside-vessel",
    "en-macro-gears",
    "en-fine-print",
    "en-crowd-strings",
    "en-cold-case-ink",
    "en-choke-point",
    "en-root-and-canopy",
    "en-spawn-to-apex",
    "en-second-arrow",
    "en-bamboo-marble",
    "en-kindred-sketch",
    "en-lazy-brain",
    "en-career-leverage",
    "en-wallet-anatomy",
]

RENAMED_EN_ALIASES = [
    "en_plain_sight_ai",
    "en-plain-sight-ai",
    "en_scale_and_bone",
    "en-scale-and-bone",
    "en_kitchen_molecules",
    "en-kitchen-molecules",
    "en_root_and_canopy",
    "en-root-and-canopy",
    "en_wait_how",
    "en-wait-how",
    "en_spawn_to_apex",
    "en-spawn-to-apex",
    "en_parable_lamp",
    "en-parable-lamp",
    "en_deep_time_strata",
    "en-deep-time-strata",
]


def test_all_20_vn_channels_have_flow_video_formulas_and_clean_logo_prompts() -> None:
    """Verify all 20 Vietnamese channels have complete V3 Flow physics and zero-text logo prompts."""
    expected_underscored = {s.replace("-", "_") for s in EXPECTED_20_VN_SLUGS}
    assert set(VN_FLOW_VIDEO_FORMULAS.keys()) == expected_underscored
    assert set(VN_CHANNEL_LOGO_PROMPTS.keys()) == expected_underscored
    assert len(VN_FLOW_VIDEO_FORMULAS) == 20
    assert len(VN_CHANNEL_LOGO_PROMPTS) == 20

    assert "reference_start_end" in FLOW_FRAME_CONTROL_MODES
    assert "boundary_extend" in FLOW_FRAME_CONTROL_MODES
    assert "single_frame_physics" in FLOW_FRAME_CONTROL_MODES
    assert "short_9x16_demo" in RETENTION_SHOT_BLUEPRINTS
    assert "long_16x9_demo" in RETENTION_SHOT_BLUEPRINTS

    for ch_id in expected_underscored:
        formula = VN_FLOW_VIDEO_FORMULAS[ch_id]
        assert formula["subject_physics"], f"{ch_id} missing subject_physics"
        assert len(formula["camera_grammar"]) >= 3, f"{ch_id} camera_grammar must have at least 3 moves"
        assert formula["continuity_anchor"], f"{ch_id} missing continuity_anchor"
        assert len(formula["forbidden_artifacts"]) >= 3, f"{ch_id} forbidden_artifacts must have at least 3 items"
        assert formula["new_visual_label"], f"{ch_id} missing new_visual_label"
        assert formula["style_description"], f"{ch_id} missing style_description"
        assert formula["thumbnail_rule"], f"{ch_id} missing thumbnail_rule"

        # Motion prompt builder
        mp = build_vn_channel_motion_prompt(ch_id, "camera tracking motion through space")
        assert "camera tracking motion through space" in mp
        assert "zero text" in mp.lower()

        # Reference keyframe prompt builder
        kp = build_vn_reference_keyframe_prompt(ch_id, "subject evolves into next state")
        assert "what happens next" in kp.lower()
        assert "zero words" in kp.lower()

        # Channel logo prompt: zero text, 25% empty margin
        logo = VN_CHANNEL_LOGO_PROMPTS[ch_id]
        assert "strictly no text" in logo.lower()
        assert "25% empty margin" in logo.lower()


def test_all_20_vn_channels_have_competitor_script_formulas() -> None:
    """Verify all 20 Vietnamese channels have 5-stage competitor dialogue formulas and cadence models."""
    expected_underscored = {s.replace("-", "_") for s in EXPECTED_20_VN_SLUGS}
    assert set(VN_COMPETITOR_SCRIPT_FORMULAS.keys()) == expected_underscored

    for ch_id in expected_underscored:
        formula_entry = VN_COMPETITOR_SCRIPT_FORMULAS[ch_id]
        assert formula_entry.get("competitor_name"), f"{ch_id} missing competitor_name"
        assert formula_entry.get("voice") == "VietNarrator", f"{ch_id} voice must be VietNarrator"

        dialogue = formula_entry.get("competitor_dialogue_formula", {})
        assert dialogue.get("competitor_verbatim_transcript_20s"), f"{ch_id} missing transcript"
        struct_formula = dialogue.get("sentence_structure_formula_vi", "")
        assert struct_formula, f"{ch_id} missing sentence structure formula"

        # Verify 5-step / 5-stage pattern presence
        for step_num in ("(1)", "(2)", "(3)", "(4)", "(5)"):
            assert step_num in struct_formula, f"{ch_id} sentence structure formula missing step {step_num}"

        assert dialogue.get("pause_and_cadence_formula_vi"), f"{ch_id} missing pause cadence formula"
        assert dialogue.get("transition_and_camera_formula_vi"), f"{ch_id} missing transition formula"

        # Test lookup helper with both underscore and hyphen
        assert get_vn_competitor_script_formula(ch_id) == formula_entry
        assert get_vn_competitor_script_formula(ch_id.replace("_", "-")) == formula_entry


def test_all_20_vn_rebuilt_style_specs_validity() -> None:
    """Validate all 20 Vietnamese rebuilt style specs files against syllable caps, pause bounds, and guardrails."""
    is_valid, violations = validate_all_vn_specs()
    assert is_valid, f"Spec validation failed with {len(violations)} violations: {violations}"
    assert len(violations) == 0

    # Explicit file-by-file assertion
    specs_dir = SYS_DIR / "channels/vn_rebuilt_style_specs"
    for slug in EXPECTED_20_VN_SLUGS:
        spec_file = specs_dir / slug / f"{slug}_rebuilt_spec.json"
        assert spec_file.is_file(), f"Missing spec file for {slug}"

        data = json.loads(spec_file.read_text(encoding="utf-8"))
        assert data["channel_slug"] == slug
        assert len(data["beats"]) == 8, f"{slug} must have exactly 8 beats"

        # Beat B01 Hook <= 18 syllables
        b01_narr = data["beats"][0]["narration"]
        b01_syl = count_vietnamese_syllables(b01_narr)
        assert b01_syl <= 18, f"{slug} B01 hook has {b01_syl} syllables > 18: '{b01_narr}'"

        # Check beat pauses and camera motions
        for b in data["beats"]:
            p = float(b["pause_after_sec"])
            assert 0.10 <= p <= 0.85, f"{slug} {b['beat_id']} invalid pause {p}"
            assert b["camera_motion"] in VALID_CAMERAS, f"{slug} {b['beat_id']} invalid camera {b['camera_motion']}"


def test_rebuilt_registry_bridge_all_38_channels_and_aliases() -> None:
    """Verify registry rebuilt bridges work seamlessly across all 38 channels and 4 renamed aliases."""
    mock_brief: Dict[str, Any] = {
        "topic": "Test Topic",
        "format_profile": "short_9x16",
        "outputs": [{"format_profile": "short_9x16"}],
    }

    # 1. All 20 VN channels (both underscore and hyphen)
    for slug in EXPECTED_20_VN_SLUGS:
        for cid in (slug, slug.replace("-", "_")):
            vis = get_rebuilt_visual_identity(cid)
            norm_id = slug.replace("-", "_")
            assert vis.profile_id == f"ch_rebuilt_{norm_id}"
            assert vis.label
            assert len(vis.style_description) > 20
            assert vis.thumbnail_rule

            formula = get_rebuilt_competitor_formula(cid)
            assert "subject_physics" in formula
            assert "competitor_dialogue_formula" in formula
            assert formula.get("voice") == "VietNarrator"

            applied = apply_rebuilt_channel(mock_brief, cid)
            assert applied["style"] == vis.style_description
            assert applied["rebuilt_competitor_benchmark"]
            assert applied["outputs"][0]["voice"] == "VietNarrator"

    # 2. All 18 EN channels (both hyphen and underscore)
    for slug in EXPECTED_18_EN_SLUGS:
        for cid in (slug, slug.replace("-", "_")):
            vis = get_rebuilt_visual_identity(cid)
            norm_id = slug.replace("-", "_")
            assert vis.profile_id == f"ch_rebuilt_{norm_id}"
            assert vis.label
            assert len(vis.style_description) > 20

            formula = get_rebuilt_competitor_formula(cid)
            assert "subject_physics" in formula
            assert "competitor_dialogue_formula" in formula

            applied = apply_rebuilt_channel(mock_brief, cid)
            assert applied["style"] == vis.style_description
            assert applied["rebuilt_competitor_benchmark"]

    # 3. All renamed EN aliases
    for alias in RENAMED_EN_ALIASES:
        vis = get_rebuilt_visual_identity(alias)
        assert vis.profile_id.startswith("ch_rebuilt_")
        assert len(vis.style_description) > 20

        formula = get_rebuilt_competitor_formula(alias)
        assert "subject_physics" in formula
        assert "competitor_dialogue_formula" in formula

        applied = apply_rebuilt_channel(mock_brief, alias)
        assert applied["style"] == vis.style_description
        assert applied["rebuilt_competitor_benchmark"]


def test_rebuilt_builders_integration() -> None:
    """Verify builders.py wires rebuilt style and formulas cleanly without altering legacy behavior."""
    # Test build_rebuilt_channel_brief for VN and EN
    brief_vn = build_rebuilt_channel_brief("tui_tien", "Cơ chế bẫy giá", "short_9x16")
    assert "rebuilt_competitor_formula" in brief_vn
    assert "Two Cents" in brief_vn["rebuilt_competitor_benchmark"]
    assert "35mm tabletop commercial" in brief_vn["style"].lower()

    brief_en = build_rebuilt_channel_brief("en-first-principles", "The Torque Paradox", "short_9x16")
    assert "rebuilt_competitor_formula" in brief_en
    assert "Veritasium" in brief_en["rebuilt_competitor_benchmark"]
    assert "veritasium scientific cinematography" in brief_en["style"].lower()

    # Test build_channel_topic with rebuilt_style flag
    legacy_topic = build_channel_topic("tui_tien", "short_9x16", rebuilt_style=False)
    rebuilt_topic = build_channel_topic("tui_tien", "short_9x16", rebuilt_style=True)
    assert legacy_topic.style != rebuilt_topic.style
    assert "35mm tabletop" in rebuilt_topic.style.lower()
    assert "notebook-ledger" in legacy_topic.style.lower()


def test_rebuild_vn_tool_cli_validate_specs() -> None:
    """Verify `rebuild_vn_from_competitor_frames.py validate-specs` executes and returns exit code 0."""
    tool_path = SYS_DIR / "tools/rebuild_vn_from_competitor_frames.py"
    proc = subprocess.run(
        [sys.executable, str(tool_path), "validate-specs"],
        capture_output=True,
        text=True,
        cwd=SYS_DIR,
    )
    assert proc.returncode == 0, f"validate-specs failed: {proc.stderr}\n{proc.stdout}"
    assert "Specification validation PASSED" in proc.stdout
    assert "0 violations" in proc.stdout


def test_rebuild_vn_tool_cli_list() -> None:
    """Verify `rebuild_vn_from_competitor_frames.py list` lists all 20 channels with exit code 0."""
    tool_path = SYS_DIR / "tools/rebuild_vn_from_competitor_frames.py"
    proc = subprocess.run(
        [sys.executable, str(tool_path), "list"],
        capture_output=True,
        text=True,
        cwd=SYS_DIR,
    )
    assert proc.returncode == 0, f"list failed: {proc.stderr}\n{proc.stdout}"
    for slug in EXPECTED_20_VN_SLUGS:
        assert slug in proc.stdout, f"Slug {slug} missing from CLI list output"
