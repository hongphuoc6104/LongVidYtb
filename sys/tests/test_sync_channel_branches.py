"""Unit tests for Multi-Channel Branch Synchronizer & Batch Verifier."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SYS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.registry import get_channel  # noqa: E402
from tools.sync_channel_branches import (  # noqa: E402
    collect_core_files,
    format_sync_report,
    format_verification_report,
    is_excluded_path,
    is_preserved_path,
    main,
    push_workspace_branch,
    sync_channel_workspace,
    verify_all_workspaces,
    verify_channel,
)


def _init_git_repo(repo_dir: Path, initial_branch: str = "main") -> None:
    repo_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", initial_branch], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test Runner"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@videopilot.local"], cwd=str(repo_dir), check=True, capture_output=True)
    dummy = repo_dir / "README.md"
    dummy.write_text("# Test Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo_dir), check=True, capture_output=True)


def test_collect_core_files_filters_runs_and_caches() -> None:
    core_files = collect_core_files(REPO_ROOT)
    assert len(core_files) > 100

    posix_paths = [p.as_posix() for p in core_files]
    # Core tools must be present
    assert "pilot.py" in posix_paths
    assert "pipeline" in posix_paths
    assert "sys/channels/registry.py" in posix_paths
    assert "sys/tools/sync_channel_branches.py" in posix_paths
    assert "sys/content_contract.py" in posix_paths

    # Runs, logs, caches and venvs must strictly NEVER be collected
    for p in posix_paths:
        assert not p.startswith("sys/runs/"), f"sys/runs was collected: {p}"
        assert not p.startswith("sys/experiments/"), f"sys/experiments was collected: {p}"
        assert not p.startswith("sys/logs/"), f"sys/logs was collected: {p}"
        assert not p.startswith(".git/"), f".git was collected: {p}"
        assert "__pycache__" not in p, f"__pycache__ was collected: {p}"
        assert not p.endswith(".pyc"), f".pyc was collected: {p}"


def test_is_excluded_and_preserved_rules() -> None:
    # Excluded rules
    assert is_excluded_path(Path("sys/runs/my-job/content.json"))
    assert is_excluded_path(Path("sys/experiments/exp1/brief.json"))
    assert is_excluded_path(Path("sys/logs/render.log"))
    assert is_excluded_path(Path(".git/config"))
    assert is_excluded_path(Path("sys/tools/__pycache__/something.cpython-312.pyc"))
    assert is_excluded_path(Path("video/my-video.mp4"))
    assert is_excluded_path(Path("sys/renderer/node_modules/remotion/package.json"))

    # Preserved rules
    assert is_preserved_path(Path("sys/channels/active_channel.json"))
    assert is_preserved_path(Path("sys/channels/nao_luoi/builder.py"))
    assert is_preserved_path(Path("sys/channels/tui_tien/builder.py"))
    assert is_preserved_path(Path("sys/channels/nao_luoi/PLAN.md"))
    assert is_preserved_path(Path("sys/runs/job-001/content.json"))
    assert is_preserved_path(Path("video/export.mp4"))

    # Core files must NOT be preserved or excluded
    assert not is_preserved_path(Path("sys/tools/script_hook_scorer.py"))
    assert not is_excluded_path(Path("sys/tools/script_hook_scorer.py"))
    assert not is_preserved_path(Path("pilot.py"))
    assert not is_excluded_path(Path("pilot.py"))


def test_preserves_active_channel_json_and_channel_builder(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_root.mkdir()
    target_dir.mkdir()

    # Create dummy core file
    (source_root / "sys/tools").mkdir(parents=True)
    (source_root / "sys/tools/my_tool.py").write_text("# Core Tool v1\n", encoding="utf-8")

    # In target, create active_channel.json with distinct content
    target_channels = target_dir / "sys/channels"
    target_channels.mkdir(parents=True)
    custom_active_channel = {
        "channel_id": "nao_luoi",
        "name": "Custom Channel Workspace",
        "custom_marker": 12345,
    }
    (target_channels / "active_channel.json").write_text(
        json.dumps(custom_active_channel, indent=2), encoding="utf-8"
    )

    # In target, create custom channel builder.py
    custom_builder = target_channels / "nao_luoi"
    custom_builder.mkdir(parents=True)
    (custom_builder / "builder.py").write_text("# Custom subagent builder logic\n", encoding="utf-8")

    # In target, create channel production package in sys/runs/
    run_dir = target_dir / "sys/runs/channel-nao-luoi-001"
    run_dir.mkdir(parents=True)
    (run_dir / "content.json").write_text('{"scenes": []}', encoding="utf-8")

    # In source, put conflicting active_channel.json and builder.py
    (source_root / "sys/channels/nao_luoi").mkdir(parents=True)
    (source_root / "sys/channels/active_channel.json").write_text('{"channel_id": "CONFLICT"}', encoding="utf-8")
    (source_root / "sys/channels/nao_luoi/builder.py").write_text("# OVERWRITE ATTEMPT", encoding="utf-8")

    ch = get_channel("nao_luoi")
    summary = sync_channel_workspace(
        source_root=source_root,
        target_dir=target_dir,
        channel=ch,
        dry_run=False,
    )

    # Core tool copied
    assert (target_dir / "sys/tools/my_tool.py").read_text(encoding="utf-8") == "# Core Tool v1\n"

    # Protected files remain untouched
    ac_content = json.loads((target_channels / "active_channel.json").read_text(encoding="utf-8"))
    assert ac_content["custom_marker"] == 12345
    assert ac_content["name"] == "Custom Channel Workspace"

    builder_content = (custom_builder / "builder.py").read_text(encoding="utf-8")
    assert builder_content == "# Custom subagent builder logic\n"

    assert (run_dir / "content.json").read_text(encoding="utf-8") == '{"scenes": []}'
    assert "sys/channels/active_channel.json" in summary["preserved_files"]
    assert "sys/channels/nao_luoi/builder.py" in summary["preserved_files"]


def test_dry_run_creates_no_files_on_disk(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_root.mkdir()
    target_dir.mkdir()

    (source_root / "pilot.py").write_text("# pilot\n", encoding="utf-8")
    (source_root / "sys/tools").mkdir(parents=True)
    (source_root / "sys/tools/sample.py").write_text("# sample\n", encoding="utf-8")

    ch = get_channel("nao_luoi")
    summary = sync_channel_workspace(
        source_root=source_root,
        target_dir=target_dir,
        channel=ch,
        dry_run=True,
    )

    assert summary["dry_run"] is True
    assert summary["created_count"] == 2
    assert not (target_dir / "pilot.py").exists()
    assert not (target_dir / "sys/tools/sample.py").exists()


def test_real_sync_detects_updated_and_unchanged_files(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_root.mkdir()
    target_dir.mkdir()

    file_a = source_root / "sys/file_a.py"
    file_b = source_root / "sys/file_b.py"
    source_root.joinpath("sys").mkdir(parents=True)
    file_a.write_text("print('A1')\n", encoding="utf-8")
    file_b.write_text("print('B1')\n", encoding="utf-8")

    ch = get_channel("tui_tien")

    # First sync: created
    res1 = sync_channel_workspace(source_root, target_dir, ch, dry_run=False)
    assert res1["created_count"] == 2
    assert res1["updated_count"] == 0

    # Second sync: unchanged
    res2 = sync_channel_workspace(source_root, target_dir, ch, dry_run=False)
    assert res2["created_count"] == 0
    assert res2["updated_count"] == 0
    assert res2["unchanged_count"] == 2

    # Modify file_a in source: updated
    file_a.write_text("print('A2')\n", encoding="utf-8")
    res3 = sync_channel_workspace(source_root, target_dir, ch, dry_run=False)
    assert res3["created_count"] == 0
    assert res3["updated_count"] == 1
    assert res3["unchanged_count"] == 1
    assert (target_dir / "sys/file_a.py").read_text(encoding="utf-8") == "print('A2')\n"


def test_verify_channel_detects_all_five_contracts(tmp_path: Path) -> None:
    ws_dir = tmp_path / "channel-nao-luoi"
    _init_git_repo(ws_dir, initial_branch="channel/nao-luoi")

    ch = get_channel("nao_luoi")

    # 1. Without active_channel.json -> FAIL
    v1 = verify_channel(ch, ws_dir, system_root=SYS_DIR)
    assert v1["ok"] is False
    assert v1["active_channel"]["ok"] is False
    assert v1["git_branch"]["ok"] is True

    # 2. Add valid active_channel.json
    ac_file = ws_dir / "sys/channels/active_channel.json"
    ac_file.parent.mkdir(parents=True)
    ac_file.write_text(
        json.dumps(
            {
                "channel_id": "nao_luoi",
                "git_branch": "channel/nao-luoi",
                "channel_profile_stamp": {"sha256": "1234567890abcdef" * 4},
                "speed_optimization": {"render_mode": "hybrid_motion"},
            }
        ),
        encoding="utf-8",
    )

    # 3. Add valid PLAN.md
    plan_file = ws_dir / "sys/channels/nao_luoi/PLAN.md"
    plan_file.parent.mkdir(parents=True)
    plan_file.write_text(
        "# Kế Hoạch Não Lười\n\n"
        "## TikTok Short (`short_9x16`)\n- 35s retention structure.\n\n"
        "## YouTube Long (`long_16x9`)\n- 10m deep dive.\n" + ("x" * 300),
        encoding="utf-8",
    )

    # 4. Now verification should pass
    v2 = verify_channel(ch, ws_dir, system_root=SYS_DIR)
    assert v2["ok"] is True
    assert v2["status"] == "PASS"
    assert v2["active_channel"]["ok"] is True
    assert v2["plan_md"]["ok"] is True
    assert v2["hook_score"]["ok"] is True
    assert v2["schema_3_contract"]["ok"] is True


def test_verify_all_workspaces_on_real_environment() -> None:
    """Verify that all 8 production workspaces under vp-channels satisfy 100% of contracts."""
    workspaces_root = Path("/home/hongphuoc6104/Desktop/vp-channels")
    if not workspaces_root.exists():
        pytest.skip("vp-channels directory not present in environment")

    report = verify_all_workspaces(workspaces_root=workspaces_root, system_root=SYS_DIR)
    assert report["total_channels"] == 8
    assert report["passed_channels"] == 8
    assert report["failed_channels"] == 0
    assert report["all_passed"] is True

    for ch_report in report["channels"]:
        assert ch_report["ok"] is True
        assert ch_report["status"] == "PASS"
        assert ch_report["hook_score"]["score"] >= 75
        assert ch_report["schema_3_contract"]["title_length"] <= 55


def test_cli_interface_dry_run_and_verify_all() -> None:
    # Test --verify-all JSON output
    old_stdout = sys.stdout
    import io

    sys.stdout = io.StringIO()
    try:
        ret = main(["--verify-all", "--json", "--channel", "nao_luoi"])
        out = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert ret == 0
    data = json.loads(out)
    assert data["total_channels"] == 1
    assert data["all_passed"] is True

    # Test --dry-run
    sys.stdout = io.StringIO()
    try:
        ret_dry = main(["--dry-run", "--channel", "tui_tien", "--json"])
        out_dry = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert ret_dry == 0
    dry_data = json.loads(out_dry)
    assert len(dry_data) == 1
    assert dry_data[0]["dry_run"] is True


def test_format_reports_output_readability() -> None:
    mock_verify_report = {
        "timestamp": "2026-10-30T00:00:00Z",
        "total_channels": 1,
        "passed_channels": 1,
        "all_passed": True,
        "channels": [
            {
                "channel_id": "nao_luoi",
                "name": "Não Lười",
                "status": "PASS",
                "git_branch": {"actual": "channel/nao-luoi", "expected": "channel/nao-luoi", "ok": True},
                "active_channel": {"channel_id": "nao_luoi", "sha256": "abc12345", "ok": True},
                "plan_md": {"size_bytes": 8000, "lines": 90, "ok": True},
                "hook_score": {"score": 100, "source": "test", "hook": "Vì sao lại thế?", "ok": True},
                "schema_3_contract": {"title_length": 45, "scene_count": 8, "ok": True},
            }
        ],
    }
    rendered_verify = format_verification_report(mock_verify_report)
    assert "Não Lười" in rendered_verify
    assert "[PASS] ALL OK" in rendered_verify
    assert "Hook: 100/100" in rendered_verify

    mock_sync_result = [
        {
            "channel_id": "nao_luoi",
            "workspace": "/tmp/mock",
            "created_count": 10,
            "updated_count": 2,
            "unchanged_count": 50,
            "preserved_count": 3,
            "dry_run": True,
            "push": {"pushed": False, "note": "Push simulated in dry-run mode"},
        }
    ]
    rendered_sync = format_sync_report(mock_sync_result)
    assert "Created files:    10" in rendered_sync
    assert "Preserved files:  3" in rendered_sync


def test_push_workspace_branch_with_local_git_remote(tmp_path: Path) -> None:
    origin_dir = tmp_path / "origin.git"
    origin_dir.mkdir()
    subprocess.run(["git", "init", "--bare", "-b", "channel/nao-luoi"], cwd=str(origin_dir), check=True, capture_output=True)

    ws_dir = tmp_path / "channel-nao-luoi"
    _init_git_repo(ws_dir, initial_branch="channel/nao-luoi")
    subprocess.run(["git", "remote", "add", "origin", str(origin_dir)], cwd=str(ws_dir), check=True, capture_output=True)

    # Clean push
    res_clean = push_workspace_branch(ws_dir, "channel/nao-luoi")
    assert res_clean["pushed"] is True
    assert res_clean["committed"] is False

    # Modify and push
    (ws_dir / "new_file.txt").write_text("Hello Git", encoding="utf-8")
    res_changed = push_workspace_branch(ws_dir, "channel/nao-luoi", commit_message="test: add file")
    assert res_changed["pushed"] is True
    assert res_changed["committed"] is True

    log_out = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"], cwd=str(origin_dir), check=True, text=True, capture_output=True
    ).stdout.strip()
    assert "test: add file" in log_out


def test_verify_channel_detects_corruptions_and_mismatches(tmp_path: Path) -> None:
    ws_dir = tmp_path / "channel-tui-tien"
    _init_git_repo(ws_dir, initial_branch="wrong-branch")
    ch = get_channel("tui_tien")

    # Wrong branch
    res_b = verify_channel(ch, ws_dir, system_root=SYS_DIR)
    assert res_b["git_branch"]["ok"] is False
    assert res_b["git_branch"]["actual"] == "wrong-branch"

    # Switch to correct branch
    subprocess.run(["git", "checkout", "-b", "channel/tui-tien"], cwd=str(ws_dir), check=True, capture_output=True)

    # Corrupt active_channel.json
    ac_file = ws_dir / "sys/channels/active_channel.json"
    ac_file.parent.mkdir(parents=True)
    ac_file.write_text("{corrupt-json", encoding="utf-8")

    res_c = verify_channel(ch, ws_dir, system_root=SYS_DIR)
    assert res_c["active_channel"]["ok"] is False
    assert "JSON decode error" in res_c["active_channel"]["error"]

    # Mismatched channel_id
    ac_file.write_text(json.dumps({"channel_id": "WRONG_ID", "git_branch": "channel/tui-tien"}), encoding="utf-8")
    res_m = verify_channel(ch, ws_dir, system_root=SYS_DIR)
    assert res_m["active_channel"]["ok"] is False
    assert res_m["active_channel"]["channel_id"] == "WRONG_ID"


def test_symlink_node_modules(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    target_dir = tmp_path / "target"
    (source_root / "sys/renderer/node_modules").mkdir(parents=True)
    (target_dir / "sys/renderer").mkdir(parents=True)

    ch = get_channel("nao_luoi")
    res = sync_channel_workspace(source_root, target_dir, ch, dry_run=False)
    assert res["node_modules_linked"] is True
    target_nm = target_dir / "sys/renderer/node_modules"
    assert target_nm.is_symlink()
    assert target_nm.resolve() == (source_root / "sys/renderer/node_modules").resolve()

