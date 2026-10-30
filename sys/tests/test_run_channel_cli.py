"""Unit tests for the Unified One-Command Channel Production Runner (sys/tools/run_channel.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from channels.registry import channel_ids, get_channel
from tools.run_channel import main, resolve_channel, run_channel

ALL_8_CHANNELS = [
    "nao_luoi",
    "tui_tien",
    "ua_sao_vay",
    "su_ke_lai",
    "thuong_cho_kheo",
    "ho_so_ky_la",
    "co_the_ke",
    "ai_binh_dan",
]


def test_channel_ids_match_expected() -> None:
    assert channel_ids() == ALL_8_CHANNELS


@pytest.mark.parametrize("cid", ALL_8_CHANNELS)
def test_run_channel_package_only_all_eight_channels(tmp_path: Path, cid: str) -> None:
    """Validate package-only mode across all 8 channels."""
    out_dir = tmp_path / f"job-{cid}"
    ch = get_channel(cid)
    max_images = ch.speed_optimization.fast_short_max_images if ch.speed_optimization else 8

    res = run_channel(
        channel=cid,
        format="short_9x16",
        mode="package-only",
        output_dir=out_dir,
        allow_active=True,
    )

    # 1. Pipeline Status & Contracts
    assert res["status"] == "SUCCESS", f"Channel {cid} failed: {res.get('contract_errors')}"
    assert res["valid_contracts"] is True, f"Contracts invalid in {cid}: {res.get('contract_errors')}"
    assert res["contract_errors"] == []
    assert res["channel_id"] == cid
    assert res["format"] == "short_9x16"
    assert res["mode"] == "package-only"

    # 2. ChannelProfile Provenance & Fast Short Budget Enforcement
    assert res["channel_profile"]["id"] == cid
    assert res["fast_short_max_images"] == max_images
    assert res["images_count"] <= max_images, f"{cid} exceeded fast_short_max_images: {res['images_count']} > {max_images}"

    # 3. Hook Scorer
    hook_data = res["hook_score"]
    assert hook_data["score"] >= 75, f"{cid} hook score too low: {hook_data['score']}"
    assert hook_data["needs_rewrite"] is False
    assert hook_data["hook_syllables"] <= 18

    # 4. Verified Files on Disk
    brief_file = out_dir / "brief.json"
    content_file = out_dir / "content.json"
    script_file = out_dir / "script.json"
    cadence_file = out_dir / "cadence_report.json"
    outline_file = out_dir / "draft" / "outline.json"
    draft_content_file = out_dir / "draft" / "content.json"

    assert brief_file.is_file()
    assert content_file.is_file()
    assert script_file.is_file()
    assert cadence_file.is_file()
    assert outline_file.is_file()
    assert draft_content_file.is_file()

    # 5. Brief & Content Schema 3.0 Bindings
    brief_data = json.loads(brief_file.read_text(encoding="utf-8"))
    content_data = json.loads(content_file.read_text(encoding="utf-8"))

    assert brief_data["schema_version"] == "3.0"
    assert brief_data["channel_profile"]["id"] == cid
    assert brief_data["tone"] == ch.tone
    assert brief_data["style"] == ch.visual.style_description
    assert brief_data["aspect_ratio"] == "9:16"
    assert brief_data["outputs"][0]["subtitles"] is True
    assert brief_data["outputs"][0]["speed"] == 1.0

    assert content_data["schema_version"] == "3.0"
    assert content_data["style"] == ch.visual.style_description
    assert len(content_data["characters"]) >= 1
    assert content_data["characters"][0]["id"] == "CH01"
    assert content_data["characters"][0]["outfit"] == ch.visual.outfit


def test_run_channel_cli_main_invocation(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test CLI entrypoint main() for standard execution."""
    out_dir = tmp_path / "cli-tui-tien"
    code = main([
        "--channel", "tui_tien",
        "--format", "short_9x16",
        "--mode", "package-only",
        "--output-dir", str(out_dir),
    ])
    assert code == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["status"] == "SUCCESS"
    assert payload["channel_id"] == "tui_tien"
    assert payload["valid_contracts"] is True
    assert (out_dir / "brief.json").is_file()


def test_run_channel_active_channel_fallback(tmp_path: Path) -> None:
    """Test automatic channel detection from sys/channels/active_channel.json."""
    active_cfg = tmp_path / "sys" / "channels" / "active_channel.json"
    active_cfg.parent.mkdir(parents=True, exist_ok=True)
    active_cfg.write_text(json.dumps({"channel_id": "ua_sao_vay"}, indent=2), encoding="utf-8")

    ch = resolve_channel(channel_arg=None, cwd=tmp_path)
    assert ch.id == "ua_sao_vay"

    out_dir = tmp_path / "auto-run"
    res = run_channel(
        channel=None,
        format="short_9x16",
        mode="package-only",
        output_dir=out_dir,
        cwd=tmp_path,
        allow_active=True,
    )
    assert res["status"] == "SUCCESS"
    assert res["channel_id"] == "ua_sao_vay"


def test_run_channel_long_16x9_format(tmp_path: Path) -> None:
    """Test running long_16x9 YouTube explainer format."""
    out_dir = tmp_path / "long-nao-luoi"
    res = run_channel(
        channel="nao_luoi",
        format="long_16x9",
        mode="package-only",
        output_dir=out_dir,
        allow_active=True,
    )
    assert res["status"] == "SUCCESS"
    assert res["valid_contracts"] is True
    assert res["format"] == "long_16x9"

    brief_data = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    assert brief_data["aspect_ratio"] == "16:9"
    assert brief_data["format_profile"] == "long_16x9"


def test_run_channel_bundle_format_with_spinoffs(tmp_path: Path) -> None:
    """Test running bundle format generating 1 long explainer + spinoff shorts."""
    out_dir = tmp_path / "bundle-nao-luoi"
    res = run_channel(
        channel="nao_luoi",
        format="bundle",
        mode="package-only",
        output_dir=out_dir,
        allow_active=True,
    )
    assert res["status"] == "SUCCESS"
    assert res["valid_contracts"] is True
    assert res["format"] == "bundle"
    assert res["spinoff_count"] >= 2
    assert (out_dir / "spinoff_shorts").is_dir()


def test_run_channel_custom_topic_and_hook(tmp_path: Path) -> None:
    """Test running with user-provided --topic-title and --hook."""
    out_dir = tmp_path / "custom-co-the-ke"
    custom_title = "Vì sao cúi đầu nhìn điện thoại làm cổ bạn gánh nặng 27 kg?"
    custom_hook = "Vì sao cúi đầu nhìn điện thoại làm cổ bạn gánh nặng hai mươi bảy ký?"

    res = run_channel(
        channel="co_the_ke",
        format="short_9x16",
        topic_title=custom_title,
        hook=custom_hook,
        mode="package-only",
        output_dir=out_dir,
        allow_active=True,
    )
    assert res["status"] == "SUCCESS"
    assert res["valid_contracts"] is True
    assert res["hook_score"]["hook"] == custom_hook
    assert res["hook_score"]["score"] >= 80


def test_run_channel_input_json_spec(tmp_path: Path) -> None:
    """Test running with --input-json supplying a custom topic spec."""
    spec_file = tmp_path / "input_topic.json"
    spec_file.write_text(
        json.dumps({
            "topic_title": "Mẹo dùng trí tuệ nhân tạo rà soát hợp đồng cực nhanh",
            "hook": "Mẹo dùng trí tuệ nhân tạo rà soát lỗi hợp đồng trong ba mươi giây?",
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    out_dir = tmp_path / "json-ai-binh-dan"
    res = run_channel(
        channel="ai_binh_dan",
        format="short_9x16",
        input_json=spec_file,
        mode="package-only",
        output_dir=out_dir,
        allow_active=True,
    )
    assert res["status"] == "SUCCESS"
    assert res["valid_contracts"] is True
    assert res["hook_score"]["score"] >= 80


def test_run_channel_full_e2e_dry_run(tmp_path: Path) -> None:
    """Test full-e2e mode with --dry-run verifying downstream pipeline wiring."""
    out_dir = tmp_path / "e2e-dry-run"
    res = run_channel(
        channel="nao_luoi",
        format="short_9x16",
        mode="full-e2e",
        output_dir=out_dir,
        dry_run=True,
        allow_active=True,
    )
    assert res["status"] == "SUCCESS"
    assert res["mode"] == "full-e2e"
    assert "downstream" in res
    downstream = res["downstream"]
    assert downstream["audio_tts"]["status"] == "DRY_RUN_PASS"
    assert downstream["flow_images"]["status"] == "DRY_RUN_PASS"
    assert downstream["colab_render"]["status"] == "DRY_RUN_PASS"


def test_run_channel_missing_channel_and_active_file_raises(tmp_path: Path) -> None:
    """Test missing channel raises ValueError when active_channel.json does not exist."""
    empty_dir = tmp_path / "empty_workspace"
    empty_dir.mkdir()
    with pytest.raises(ValueError, match="No --channel provided"):
        resolve_channel(channel_arg=None, cwd=empty_dir, system_root=empty_dir / "sys")
