"""Unit tests for Fleet Runner (run_fleet.py)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SYS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.run_fleet import (  # noqa: E402
    CHANNEL_FLEET_CONFIG,
    build_channel_plan,
    get_job_id,
    resolve_channel_targets,
    run_fleet,
)

EXPECTED_PARTITIONS = {
    "nao_luoi": {
        "slug": "nao-luoi",
        "flow_profiles": "profile_1,profile_2",
        "colab_accounts": "account-01,account-02",
        "colab_session": "vp-nao-luoi",
    },
    "tui_tien": {
        "slug": "tui-tien",
        "flow_profiles": "profile_3,profile_4,profile_5",
        "colab_accounts": "account-03,account-04,account-05",
        "colab_session": "vp-tui-tien",
    },
    "ua_sao_vay": {
        "slug": "ua-sao-vay",
        "flow_profiles": "profile_6,profile_7",
        "colab_accounts": "account-06,account-07",
        "colab_session": "vp-ua-sao-vay",
    },
    "su_ke_lai": {
        "slug": "su-ke-lai",
        "flow_profiles": "profile_8,profile_9,profile_10",
        "colab_accounts": "account-08,account-09,account-10",
        "colab_session": "vp-su-ke-lai",
    },
    "thuong_cho_kheo": {
        "slug": "thuong-cho-kheo",
        "flow_profiles": "profile_11,profile_12",
        "colab_accounts": "account-11,account-12",
        "colab_session": "vp-thuong-cho-kheo",
    },
    "ho_so_ky_la": {
        "slug": "ho-so-ky-la",
        "flow_profiles": "profile_13,profile_14,profile_15",
        "colab_accounts": "account-13,account-14,account-15",
        "colab_session": "vp-ho-so-ky-la",
    },
    "co_the_ke": {
        "slug": "co-the-ke",
        "flow_profiles": "profile_16,profile_17",
        "colab_accounts": "account-16,account-17",
        "colab_session": "vp-co-the-ke",
    },
    "ai_binh_dan": {
        "slug": "ai-binh-dan",
        "flow_profiles": "profile_18,profile_19,profile_20",
        "colab_accounts": "account-18,account-19,account-20",
        "colab_session": "vp-ai-binh-dan",
    },
}


def test_channel_resource_partitions_match_contract() -> None:
    """Verify CHANNEL_FLEET_CONFIG strictly matches Contract §1."""
    assert len(CHANNEL_FLEET_CONFIG) == 8
    for ch_id, expected in EXPECTED_PARTITIONS.items():
        assert ch_id in CHANNEL_FLEET_CONFIG
        actual = CHANNEL_FLEET_CONFIG[ch_id]
        assert actual["slug"] == expected["slug"]
        assert actual["flow_profiles"] == expected["flow_profiles"]
        assert actual["colab_accounts"] == expected["colab_accounts"]
        assert actual["colab_session"] == expected["colab_session"]


def test_resolve_channel_targets() -> None:
    # All channels
    assert len(resolve_channel_targets("all")) == 8
    assert len(resolve_channel_targets(None)) == 8

    # Specific channel_ids
    targets = resolve_channel_targets("nao_luoi,tui_tien")
    assert targets == ["nao_luoi", "tui_tien"]

    # Slug names
    targets2 = resolve_channel_targets("nao-luoi,su-ke-lai")
    assert targets2 == ["nao_luoi", "su_ke_lai"]

    # Invalid channel raises ValueError
    with pytest.raises(ValueError, match="Unknown channel 'invalid_channel'"):
        resolve_channel_targets("invalid_channel")


def test_job_id_naming_convention() -> None:
    assert get_job_id("nao-luoi", "short_9x16") == "nao-luoi-week1-9x16-v2"
    assert get_job_id("nao-luoi", "long_16x9") == "nao-luoi-week1-16x9"


def test_build_channel_plan_short_and_long(tmp_path: Path) -> None:
    # Short 9:16 plan
    short_plan = build_channel_plan("nao_luoi", "short_9x16", worktrees_root=tmp_path)
    assert short_plan["job_id"] == "nao-luoi-week1-9x16-v2"
    assert len(short_plan["commands"]) == 2
    assert short_plan["commands"][0]["step"] == "export"
    assert "export_v2_bundle.py" in short_plan["commands"][0]["cmd"][1]
    assert short_plan["commands"][1]["step"] == "produce"
    assert "produce_channel_short_e2e.py" in short_plan["commands"][1]["cmd"][1]

    # Long 16:9 plan
    long_plan = build_channel_plan("nao_luoi", "long_16x9", worktrees_root=tmp_path)
    assert long_plan["job_id"] == "nao-luoi-week1-16x9"
    assert len(long_plan["commands"]) == 2
    assert long_plan["commands"][1]["step"] == "produce"
    assert "produce_channel_long_e2e.py" in long_plan["commands"][1]["cmd"][1]


def test_run_fleet_dry_run_all_channels(tmp_path: Path) -> None:
    summary = run_fleet(
        channels="all",
        format_profile="short_9x16",
        dry_run=True,
        parallel=2,
        worktrees_root=tmp_path,
    )

    assert summary["format"] == "short_9x16"
    assert summary["dry_run"] is True
    assert summary["total_channels"] == 8
    assert summary["successful"] == 8
    assert summary["failed"] == 0

    channel_results = summary["channels"]
    assert len(channel_results) == 8

    for res in channel_results:
        ch_id = res["channel_id"]
        assert res["status"] == "DRY_RUN"
        assert res["job_id"] == f"{EXPECTED_PARTITIONS[ch_id]['slug']}-week1-9x16-v2"
        assert res["flow_profiles"] == EXPECTED_PARTITIONS[ch_id]["flow_profiles"]
        assert res["colab_accounts"] == EXPECTED_PARTITIONS[ch_id]["colab_accounts"]
        assert res["colab_session"] == EXPECTED_PARTITIONS[ch_id]["colab_session"]
        assert "sys/logs/fleet" in res["log_file"]
        assert len(res["commands"]) == 2


def test_run_fleet_dry_run_subset(tmp_path: Path) -> None:
    summary = run_fleet(
        channels="tui_tien,ho_so_ky_la",
        format_profile="long_16x9",
        dry_run=True,
        worktrees_root=tmp_path,
    )

    assert summary["total_channels"] == 2
    assert [c["channel_id"] for c in summary["channels"]] == ["tui_tien", "ho_so_ky_la"]
    assert summary["channels"][0]["job_id"] == "tui-tien-week1-16x9"
    assert summary["channels"][1]["job_id"] == "ho-so-ky-la-week1-16x9"
