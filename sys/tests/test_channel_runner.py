"""Unit tests for the 8-channel automated runner, builders, and Schema 3.0 production packages."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.builders import (  # noqa: E402
    build_and_export_channel_package,
    build_channel_topic,
    get_channel_or_active,
)
from channels.registry import channel_ids, get_channel  # noqa: E402
from flow_prompts.compiler import find_laziness_pattern, find_visual_cliche  # noqa: E402
from tools.run_channel_video import execute_channel_video  # noqa: E402

ALL_CHANNELS = channel_ids()


@pytest.mark.parametrize("cid", ALL_CHANNELS)
def test_all_eight_channels_short_package_generation(tmp_path: Path, cid: str) -> None:
    """Every channel must generate a valid Schema 3.0 TikTok short_9x16 package."""
    out_dir = tmp_path / f"{cid}_short"
    res = build_and_export_channel_package(cid, "short_9x16", output_dir=out_dir)

    assert res["valid_contracts"] is True, f"Errors for {cid}: {res['contract_errors']}"
    assert len(res["contract_errors"]) == 0
    assert len(res["packaging_warnings"]) == 0

    # Verify generated files
    assert (out_dir / "brief.json").is_file()
    assert (out_dir / "content.json").is_file()
    assert (out_dir / "script.json").is_file()
    assert (out_dir / "cadence_report.json").is_file()
    assert (out_dir / "draft/outline.json").is_file()

    # Verify brief packaging & hook
    brief = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    assert len(brief["packaging"]["youtube_title"]) <= 55
    assert len(brief["packaging"]["thumbnail_spec"]["text_overlay"].split()) in (2, 3, 4)

    # Verify Hook score >= 75
    hook_score = res["hook_score"]
    assert hook_score["score"] >= 75, f"Low hook score {hook_score['score']} for {cid}: {hook_score['suggestions']}"
    assert hook_score["hook_syllables"] <= 18

    # Verify Cadence
    cadence = res["cadence_report"]
    assert cadence["max_drift"] <= 0.30


@pytest.mark.parametrize("cid", ALL_CHANNELS)
def test_all_eight_channels_long_package_generation(tmp_path: Path, cid: str) -> None:
    """Every channel must generate a valid Schema 3.0 YouTube long_16x9 package."""
    out_dir = tmp_path / f"{cid}_long"
    res = build_and_export_channel_package(cid, "long_16x9", output_dir=out_dir)

    assert res["valid_contracts"] is True, f"Errors for {cid}: {res['contract_errors']}"
    assert len(res["contract_errors"]) == 0
    assert len(res["packaging_warnings"]) == 0

    brief = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    assert len(brief["packaging"]["youtube_title"]) <= 55

    hook_score = res["hook_score"]
    assert hook_score["score"] >= 75
    assert hook_score["hook_syllables"] <= 24


def test_long_spinoff_shorts_generation(tmp_path: Path) -> None:
    """Long explainer with spinoff shorts flag must create standalone short packages."""
    out_dir = tmp_path / "nao_luoi_spinoffs"
    res = build_and_export_channel_package(
        "nao_luoi",
        "long_16x9",
        output_dir=out_dir,
        spinoff_shorts=True,
    )
    assert res["valid_contracts"] is True
    spinoffs = res.get("spinoff_packages") or []
    assert len(spinoffs) >= 1

    sp_root = out_dir / "spinoff_shorts"
    assert sp_root.is_dir()
    sp_dirs = list(sp_root.glob("spinoff_*"))
    assert len(sp_dirs) >= 1
    for sp in sp_dirs:
        assert (sp / "brief.json").is_file()
        assert (sp / "content.json").is_file()


def test_custom_topic_and_seed_indices(tmp_path: Path) -> None:
    """Builder can formulate packages from custom topics and seed indices."""
    out_seed = tmp_path / "seed_3"
    res_seed = build_and_export_channel_package(
        "tui_tien",
        "short_9x16",
        output_dir=out_seed,
        seed_index=3,
    )
    assert res_seed["valid_contracts"] is True

    out_custom = tmp_path / "custom"
    res_custom = build_and_export_channel_package(
        "ua_sao_vay",
        "short_9x16",
        output_dir=out_custom,
        topic_title="Vì sao khi đi máy bay tai lại bị ù?",
    )
    assert res_custom["valid_contracts"] is True


def test_channel_runner_cli_dry_run(tmp_path: Path) -> None:
    """CLI runner executes clean dry-run end-to-end for all stages."""
    out_dir = tmp_path / "cli_run"
    res = execute_channel_video(
        channel_id="ai_binh_dan",
        format_profile="short_9x16",
        stage="all",
        dry_run=True,
        output_dir=out_dir,
    )
    assert res["success"] is True
    assert "package" in res["stages"]
    assert "audio" in res["stages"]
    assert "images" in res["stages"]
    assert "render" in res["stages"]
    assert res["stages"]["images"]["overlay_card"] is False


def test_channel_auto_detection_from_active_channel(tmp_path: Path) -> None:
    """get_channel_or_active resolves correctly from active_channel.json."""
    active_file = tmp_path / "active_channel.json"
    active_file.write_text(json.dumps({"channel_id": "ho_so_ky_la"}), encoding="utf-8")
    ch = get_channel_or_active(cwd=tmp_path)
    assert ch.id == "ho_so_ky_la"
    assert ch.name == "Hồ Sơ Kỳ Lạ"


def test_clean_visual_prompts_free_of_banned_cliches() -> None:
    """All prompts generated across all 8 channels must be 100% free of banned clichés."""
    for cid in ALL_CHANNELS:
        topic_short = build_channel_topic(cid, "short_9x16")
        for sc in topic_short.scenes:
            for b in sc.visual_beats:
                assert find_visual_cliche(b.description) is None, f"Cliché in {cid} short: {b.description}"
                assert find_laziness_pattern(b.description, version="1.7.0") is None, f"Laziness in {cid} short: {b.description}"

        topic_long = build_channel_topic(cid, "long_16x9")
        for sc in topic_long.scenes:
            for b in sc.visual_beats:
                assert find_visual_cliche(b.description) is None, f"Cliché in {cid} long: {b.description}"
                assert find_laziness_pattern(b.description, version="1.7.0") is None, f"Laziness in {cid} long: {b.description}"
