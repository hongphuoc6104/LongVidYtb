"""Unit and integration tests for Channel 1: Não Lười (nao_luoi).

Validates:
1. Registration & Channel Profile SSOT: registry, active_channel.json, PLAN.md.
2. Fast-Short (short_9x16): Schema 3.0 contracts, <= 7 Flow images, camera beats, Hook score >= 70.
3. Long Explainer (long_16x9): Schema 3.0 contracts, spinoff_shorts extraction, Hook score >= 70.
4. Sample Run: verification of sys/runs/nao-luoi-week1-9x16 bundle.
5. Acoustic Cadence: speech rate 4.0 syl/s, zero drift, SC01 hook <= 18 syllables.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from channels.nao_luoi.builder import (
    CHANNEL_ID,
    export_fast_short,
    export_long_explainer,
    validate_bundle,
)
from channels.registry import (
    channel_cast,
    channel_profile_stamp,
    get_channel,
)
from content.research_story_architect import (
    compute_brief_hash,
    validate_production_bundle,
)
from content_contract import validate_brief, validate_content
from tools.script_cadence_checker import ScriptCadenceChecker
from tools.script_hook_scorer import score_script

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"


def test_nao_luoi_registry_and_active_channel_consistency() -> None:
    """Verify channel profile registry and active_channel.json SSOT."""
    channel = get_channel(CHANNEL_ID)
    assert channel.id == "nao_luoi"
    assert channel.name == "Não Lười"
    assert channel.git_branch == "channel/nao-luoi"
    assert channel.workspace_dirname == "channel-nao-luoi"
    assert channel.platform_routing == {"tiktok": "short_9x16", "youtube": "long_16x9"}
    assert channel.visual.profile_id == "handdrawn_2d_explainer"
    assert channel.voice == "VietNarrator"
    assert channel.speed == 1.0
    assert channel.speed_optimization.fast_short_max_images == 7
    assert channel.speed_optimization.spinoff_shorts_per_long == 4

    # active_channel.json check (present inside channel worktree)
    active_path = SYS_DIR / "channels" / "active_channel.json"
    if active_path.is_file():
        active_data = json.loads(active_path.read_text(encoding="utf-8"))
        assert active_data["channel_id"] == "nao_luoi"
        assert active_data["git_branch"] == "channel/nao-luoi"
        assert active_data["speed_optimization"]["fast_short_max_images"] == 7

    # PLAN.md check
    plan_path = SYS_DIR / "channels" / "nao_luoi" / "PLAN.md"
    assert plan_path.is_file()
    plan_text = plan_path.read_text(encoding="utf-8")
    assert "NÃO LƯỜI" in plan_text
    assert "fast_short" in plan_text or "Fast-Short" in plan_text
    assert "spinoff_shorts" in plan_text or "Spin-off" in plan_text

    # Provenance stamp
    stamp = channel_profile_stamp("nao_luoi")
    assert stamp["id"] == "nao_luoi"
    assert len(stamp["sha256"]) == 64

    # Primary cast entry
    cast = channel_cast("nao_luoi", "CH01")
    assert cast["id"] == "CH01"
    assert "indie webcomic doodle stickman" in cast["appearance"].lower()


def test_builder_exports_fast_short_bundle(tmp_path: Path) -> None:
    """Verify builder exports valid Schema 3.0 short_9x16 bundle (fast_short <= 7 Flow images)."""
    out_dir = tmp_path / "test-fast-short"
    export_fast_short(output_dir=out_dir)

    # Required bundle artifacts
    required_files = (
        "brief.json",
        "content.json",
        "script.json",
        "cadence_report.json",
        "draft/outline.json",
        "draft/content.json",
    )
    for fname in required_files:
        p = out_dir / fname
        assert p.is_file(), f"Missing {fname}"
        assert p.stat().st_size > 0, f"Empty {fname}"

    brief = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))

    # Schema 3.0 Contract validation
    assert brief.get("schema_version") == "3.0"
    assert content.get("schema_version") == "3.0"
    assert brief["format_profile"] == "short_9x16"
    assert brief["aspect_ratio"] == "9:16"
    assert brief["channel_profile"]["id"] == "nao_luoi"

    expected_hash = compute_brief_hash(brief)
    assert content["brief_hash"] == expected_hash

    validate_brief(SYS_DIR, brief)
    validate_content(SYS_DIR, brief, 1, content["brief_hash"], content)

    valid, errors = validate_production_bundle(SYS_DIR, brief, content)
    assert valid, f"validate_production_bundle failed: {errors}"
    assert len(errors) == 0

    # Flow image cap check (<= 7 Flow images)
    total_images = sum(len(sc["images"]) for sc in content["scenes"])
    assert total_images <= 7
    assert total_images == 6

    # Camera beats presence
    for sc in content["scenes"]:
        assert len(sc["beats"]) >= 1
        for bt in sc["beats"]:
            assert bt.get("effect") in (
                "zoom_in",
                "zoom_out",
                "pan_right",
                "pan_left",
                "macro_push_in",
                "wide_slow_pull",
                "hold",
                "cut",
                "fast_pan_reveal",
            )

    # Hook score check (must be >= 70)
    narrations = [sc["narration"] for sc in content["scenes"]]
    hook_res = score_script(narrations, CHANNEL_ID, format_profile="short_9x16")
    assert hook_res.score >= 70
    assert hook_res.score == 100
    assert not hook_res.needs_rewrite

    # Cadence checker verification
    checker = ScriptCadenceChecker(nominal_rate=4.0)
    script_data = json.loads((out_dir / "script.json").read_text(encoding="utf-8"))
    cadence_res = checker.check_scenes(script_data)
    assert cadence_res["max_drift"] <= 0.3
    assert cadence_res["total_scenes"] == 5

    # SC01 opening hook syllable check
    sc01_first = narrations[0].split(".")[0].split("?")[0].strip()
    from tools.script_cadence_checker import count_syllables

    assert count_syllables(sc01_first, lang="vi") <= 18


def test_builder_exports_long_explainer_with_spinoffs(tmp_path: Path) -> None:
    """Verify builder exports valid Schema 3.0 long_16x9 bundle with 4 spinoff shorts."""
    out_dir = tmp_path / "test-long-explainer"
    export_long_explainer(output_dir=out_dir, spinoffs=True)

    brief = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))

    # Schema 3.0 Contract validation
    assert brief.get("schema_version") == "3.0"
    assert content.get("schema_version") == "3.0"
    assert brief["format_profile"] == "long_16x9"
    assert brief["aspect_ratio"] == "16:9"
    assert brief["channel_profile"]["id"] == "nao_luoi"

    valid, errors = validate_production_bundle(SYS_DIR, brief, content)
    assert valid, f"Long bundle validation failed: {errors}"
    assert len(errors) == 0

    # Spinoff shorts attached in brief
    spinoffs = brief.get("spinoff_shorts", [])
    assert len(spinoffs) == 4
    for sp in spinoffs:
        assert sp["format_profile"] == "short_9x16"
        assert sp["id"].startswith("SPINOFF_")
        assert len(sp["hook_title"]) > 0
        assert len(sp["opening_hook"]) > 0

    # Hook score check
    narrations = [sc["narration"] for sc in content["scenes"]]
    hook_res = score_script(narrations, CHANNEL_ID, format_profile="long_16x9")
    assert hook_res.score >= 70


def test_sample_run_week1_9x16_artifact() -> None:
    """Verify that sample run sys/runs/nao-luoi-week1-9x16 exists and passes all gates."""
    run_dir = SYS_DIR / "runs" / "nao-luoi-week1-9x16"
    if not run_dir.exists():
        export_fast_short(output_dir=run_dir)
    assert run_dir.is_dir(), f"Sample run directory {run_dir} does not exist"

    summary = validate_bundle(run_dir)
    assert summary["valid_contracts"] is True
    assert summary["contract_errors"] == []
    assert summary["hook_passed"] is True
    assert summary["hook_score"] >= 70
    assert summary["fast_short_image_cap_passed"] is True
    assert summary["total_images"] <= 7


def test_builder_cli_execution() -> None:
    """Verify CLI interface of builder.py returns exit code 0."""
    builder_script = SYS_DIR / "channels" / "nao_luoi" / "builder.py"
    res = subprocess.run(
        [sys.executable, str(builder_script), "--help"],
        capture_output=True,
        text=True,
        cwd=str(ROOT_DIR),
    )
    assert res.returncode == 0
    assert "Builder for Channel 'nao_luoi'" in res.stdout

    # Validate-only mode on the sample run
    res2 = subprocess.run(
        [
            sys.executable,
            str(builder_script),
            "--out",
            str(SYS_DIR / "runs" / "nao-luoi-week1-9x16"),
            "--validate-only",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT_DIR),
    )
    assert res2.returncode == 0
    assert '"valid_contracts": true' in res2.stdout
    assert '"hook_passed": true' in res2.stdout
