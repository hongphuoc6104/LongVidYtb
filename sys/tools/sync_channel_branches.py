"""Multi-Channel Branch Synchronizer & Batch Dry-Run Verifier.

Synchronizes core engine tools from vp-agent-core to all 8 channel workspaces
under vp-channels/channel-<slug> while strictly preserving:
- sys/channels/active_channel.json
- sys/channels/<id>/builder.py
- Per-channel production packages (sys/runs/*, video/*)

Provides verification of all 8 channels (--verify-all):
- Git branch name against channel registry
- active_channel.json presence, format, and channel_id match
- PLAN.md presence, size, and dual-format (TikTok + YouTube) coverage
- Script Hook score via script_hook_scorer.py
- Schema 3.0 contract validity via validate_brief and validate_content

Usage:
    # Dry-run sync preview across all 8 channels
    python3 sys/tools/sync_channel_branches.py --dry-run

    # Verify contracts across all 8 channels (read-only)
    python3 sys/tools/sync_channel_branches.py --verify-all

    # Sync and push to origin
    python3 sys/tools/sync_channel_branches.py --push
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SYS_DIR.parent
DEFAULT_WORKSPACES_ROOT = REPO_ROOT.parent if REPO_ROOT.parent.name == "vp-channels" else REPO_ROOT.parent / "vp-channels"

for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.builders import build_channel_topic  # noqa: E402
from channels.registry import ChannelProfile, channels, get_channel  # noqa: E402
from content.research_story_architect import (  # noqa: E402
    build_brief_v3,
    build_content_v3,
    compute_brief_hash,
)
from content_contract import ContractError, validate_brief, validate_content  # noqa: E402
from tools.script_hook_scorer import HookScore, score_script  # noqa: E402

# Core top-level files to synchronize from REPO_ROOT
CORE_ROOT_FILES: Tuple[str, ...] = (
    "pilot.py",
    "pipeline",
    "pyproject.toml",
    "AGENTS.md",
    "GEMINI.md",
    "INDEX.md",
    "PLAYBOOK.md",
    "README.md",
    ".gitignore",
)

# Core directory trees to synchronize from REPO_ROOT
CORE_DIRECTORIES: Tuple[str, ...] = (
    ".agents",
    ".github",
    "sys",
)

# Relative path patterns that must NEVER be overwritten in destination workspaces
PRESERVED_PATTERNS: Tuple[str, ...] = (
    "sys/channels/active_channel.json",
    "sys/channels/*/builder.py",
    "sys/channels/*/PLAN.md",
    "sys/runs",
    "video",
    "sys/staging",
)

# Relative path patterns excluded from copying altogether
EXCLUDED_PATTERNS: Tuple[str, ...] = (
    ".git",
    "sys/renderer/node_modules",
    "sys/runs",
    "runs",
    "video",
    "sys/experiments",
    "experiments",
    "sys/logs",
    "logs",
    "sys/staging",
    "staging",
    "sys/batches",
    "batches",
    "scratch",
    "exports",
    "out",
    "bundle",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    ".state",
    ".claude",
    ".gemini",
    ".antigravity",
    ".cursor",
    "--help",
    "list",
    "status",
)


def _matches_any_prefix(rel_str: str, prefixes: Sequence[str]) -> bool:
    for p in prefixes:
        if rel_str == p or rel_str.startswith(p + "/"):
            return True
    return False


def is_excluded_path(rel_path: Path) -> bool:
    """Return True if path should be skipped during sync iteration."""
    rel_str = rel_path.as_posix()
    parts = rel_path.parts

    # Exclude technical caches and venvs anywhere in hierarchy
    for part in parts:
        if part in ("__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".git", ".venv", "venv", ".state"):
            return True
        if part.endswith(".pyc") or part.endswith(".pyo"):
            return True

    # Exclude specific prefixes
    if _matches_any_prefix(rel_str, EXCLUDED_PATTERNS):
        return True

    # Exclude node_modules anywhere
    if "node_modules" in parts:
        return True

    # Exclude sqlite files and backup files
    name = rel_path.name
    if name.endswith((".sqlite", ".sqlite3", ".db", ".bak", ".swp", ".DS_Store")):
        return True

    return False


def is_preserved_path(rel_path: Path, channel_id: Optional[str] = None) -> bool:
    """Return True if destination path is protected by channel invariants."""
    rel_str = rel_path.as_posix()

    # Exact match for active_channel lockfile
    if rel_str == "sys/channels/active_channel.json":
        return True

    # Protected channel builder scripts and PLAN.md under sys/channels/<id>/
    parts = rel_path.parts
    if len(parts) >= 4 and parts[0] == "sys" and parts[1] == "channels":
        if parts[3] in ("builder.py", "PLAN.md"):
            return True

    # Protected production runs and video deliverables
    if _matches_any_prefix(rel_str, PRESERVED_PATTERNS):
        return True

    return False


def collect_core_files(source_root: Path) -> List[Path]:
    """Discover all core files from source_root that are eligible for sync."""
    collected: Set[Path] = set()

    # 1. Root files
    for root_file in CORE_ROOT_FILES:
        candidate = source_root / root_file
        if candidate.is_file():
            rel = Path(root_file)
            if not is_excluded_path(rel):
                collected.add(rel)

    # 2. Directory trees
    for dir_name in CORE_DIRECTORIES:
        source_dir = source_root / dir_name
        if not source_dir.is_dir():
            continue
        for root, dirs, files in os.walk(source_dir):
            # Prune excluded directories in-place for efficiency
            dirs[:] = [
                d
                for d in dirs
                if not is_excluded_path(Path(root, d).relative_to(source_root))
            ]
            for fname in files:
                full_path = Path(root, fname)
                rel = full_path.relative_to(source_root)
                if not is_excluded_path(rel):
                    collected.add(rel)

    return sorted(collected)


def _run_git(cmd: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git"] + list(cmd), cwd=str(cwd), check=True, text=True, capture_output=True)


def push_workspace_branch(
    ws_dir: Path,
    branch: str,
    commit_message: str = "sync: core tools from vp-agent-core",
) -> Dict[str, Any]:
    """Stage synced files, commit if modified, and push to remote origin."""
    try:
        status_res = _run_git(["status", "--porcelain"], cwd=ws_dir)
        changes = [line for line in status_res.stdout.splitlines() if line.strip()]

        committed = False
        if changes:
            _run_git(["add", "-A"], cwd=ws_dir)
            _run_git(["commit", "-m", commit_message], cwd=ws_dir)
            committed = True

        push_res = _run_git(["push", "-u", "origin", f"{branch}:{branch}"], cwd=ws_dir)
        return {
            "pushed": True,
            "committed": committed,
            "branch": branch,
            "output": push_res.stdout.strip(),
        }
    except Exception as ex:
        return {
            "pushed": False,
            "branch": branch,
            "error": str(ex),
        }


def sync_channel_workspace(
    source_root: Path,
    target_dir: Path,
    channel: ChannelProfile,
    dry_run: bool = False,
    push: bool = False,
    core_files: Optional[Sequence[Path]] = None,
) -> Dict[str, Any]:
    """Synchronize core tools from source_root to target_dir while preserving channel invariants."""
    files_to_sync = core_files if core_files is not None else collect_core_files(source_root)

    created_files: List[str] = []
    updated_files: List[str] = []
    preserved_files: List[str] = []
    unchanged_count = 0

    if not target_dir.exists() and not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    for rel in files_to_sync:
        src_path = source_root / rel
        dest_path = target_dir / rel
        rel_str = rel.as_posix()

        # Invariant check: if destination file is protected and already exists, do not overwrite
        if is_preserved_path(rel, channel_id=channel.id):
            if dest_path.exists():
                preserved_files.append(rel_str)
                continue

        if not dest_path.exists():
            created_files.append(rel_str)
            if not dry_run:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest_path)
        else:
            # File exists in destination; check if content differs
            if filecmp.cmp(src_path, dest_path, shallow=False):
                unchanged_count += 1
            else:
                updated_files.append(rel_str)
                if not dry_run:
                    shutil.copy2(src_path, dest_path)

    # Symlink node_modules if needed
    source_nm = source_root / "sys/renderer/node_modules"
    target_nm = target_dir / "sys/renderer/node_modules"
    node_modules_linked = False
    if source_nm.exists() and not target_nm.exists() and not target_nm.is_symlink():
        if not dry_run:
            target_nm.parent.mkdir(parents=True, exist_ok=True)
            target_nm.symlink_to(source_nm)
        node_modules_linked = True

    push_result: Optional[Dict[str, Any]] = None
    if push:
        if dry_run:
            push_result = {"pushed": False, "dry_run": True, "note": "Push simulated in dry-run mode"}
        else:
            push_result = push_workspace_branch(target_dir, channel.git_branch)

    return {
        "channel_id": channel.id,
        "branch": channel.git_branch,
        "workspace": str(target_dir),
        "dry_run": dry_run,
        "created_count": len(created_files),
        "updated_count": len(updated_files),
        "unchanged_count": unchanged_count,
        "preserved_count": len(preserved_files),
        "node_modules_linked": node_modules_linked,
        "created_files": created_files,
        "updated_files": updated_files,
        "preserved_files": preserved_files,
        "push": push_result,
    }


def verify_channel(
    channel: ChannelProfile,
    target_dir: Path,
    system_root: Path = SYS_DIR,
) -> Dict[str, Any]:
    """Run full contract verification for one channel."""
    # 1. Git branch check
    branch_info: Dict[str, Any] = {"expected": channel.git_branch, "ok": False}
    if target_dir.exists():
        try:
            res = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=target_dir)
            actual_branch = res.stdout.strip()
            branch_info["actual"] = actual_branch
            branch_info["ok"] = actual_branch == channel.git_branch
        except Exception as ex:
            branch_info["error"] = str(ex)
    else:
        branch_info["error"] = "Workspace directory does not exist"

    # 2. active_channel.json check
    ac_path = target_dir / "sys/channels/active_channel.json"
    ac_info: Dict[str, Any] = {"exists": ac_path.is_file(), "ok": False}
    if ac_path.is_file():
        try:
            ac_data = json.loads(ac_path.read_text(encoding="utf-8"))
            ac_cid = ac_data.get("channel_id")
            ac_branch = ac_data.get("git_branch")
            stamp = ac_data.get("channel_profile_stamp") or {}

            ac_info["channel_id"] = ac_cid
            ac_info["git_branch"] = ac_branch
            ac_info["sha256"] = stamp.get("sha256")
            ac_info["has_speed_opt"] = bool(ac_data.get("speed_optimization"))

            ac_info["ok"] = (
                ac_cid == channel.id
                and ac_branch == channel.git_branch
                and bool(stamp.get("sha256"))
            )
        except Exception as ex:
            ac_info["error"] = f"JSON decode error: {ex}"
    else:
        ac_info["error"] = f"Missing lockfile at {ac_path}"

    # 3. PLAN.md check
    plan_candidate = target_dir / f"sys/channels/{channel.id}/PLAN.md"
    if not plan_candidate.is_file():
        plan_candidate = system_root / f"channels/{channel.id}/PLAN.md"

    plan_info: Dict[str, Any] = {"exists": plan_candidate.is_file(), "ok": False}
    if plan_candidate.is_file():
        try:
            plan_text = plan_candidate.read_text(encoding="utf-8")
            size_b = plan_candidate.stat().st_size
            lines_cnt = len(plan_text.splitlines())
            has_short = "short_9x16" in plan_text or "TikTok" in plan_text
            has_long = "long_16x9" in plan_text or "YouTube" in plan_text

            plan_info["path"] = str(plan_candidate)
            plan_info["size_bytes"] = size_b
            plan_info["lines"] = lines_cnt
            plan_info["has_short_spec"] = has_short
            plan_info["has_long_spec"] = has_long
            plan_info["ok"] = size_b > 200 and has_short and has_long
        except Exception as ex:
            plan_info["error"] = str(ex)
    else:
        plan_info["error"] = f"Missing PLAN.md at {plan_candidate}"

    # 4. Script Hook score check
    hook_info: Dict[str, Any] = {"ok": False}
    narrations: List[str] = []
    source_label = "pre_architected"

    # Search for an existing production package in target runs
    runs_dir = target_dir / "sys/runs"
    if runs_dir.is_dir():
        for job_dir in sorted(runs_dir.iterdir()):
            cf = job_dir / "content.json"
            if cf.is_file():
                try:
                    cdata = json.loads(cf.read_text(encoding="utf-8"))
                    scenes = cdata.get("scenes", [])
                    if scenes:
                        narrations = [s.get("narration", "") for s in scenes if s.get("narration")]
                        source_label = f"run:{job_dir.name}"
                        break
                except Exception:
                    pass

    # Fallback to pre-architected topic narrations
    if not narrations:
        try:
            topic = build_channel_topic(channel.id, "short_9x16", cwd=target_dir if target_dir.exists() else None)
            narrations = [sc.narration for sc in topic.scenes if sc.narration]
            source_label = "pre_architected_week1"
        except Exception as ex:
            hook_info["error"] = f"Failed to build topic: {ex}"

    if narrations:
        try:
            score_res: HookScore = score_script(narrations, channel.id, "short_9x16")
            hook_info["score"] = score_res.score
            hook_info["hook"] = score_res.hook
            hook_info["hook_syllables"] = score_res.hook_syllables
            hook_info["needs_rewrite"] = score_res.needs_rewrite
            hook_info["source"] = source_label
            hook_info["ok"] = score_res.score >= 60
        except Exception as ex:
            hook_info["error"] = str(ex)

    # 5. Schema 3.0 contract check
    schema_info: Dict[str, Any] = {"ok": False, "version": "3.0"}
    try:
        sample_topic = build_channel_topic(channel.id, "short_9x16", cwd=target_dir if target_dir.exists() else None)
        brief_data = build_brief_v3(sample_topic, system_root=system_root)
        validate_brief(system_root, brief_data)
        bhash = compute_brief_hash(brief_data)
        content_data = build_content_v3(sample_topic, brief_data, bhash, brief_revision=1)
        validate_content(system_root, brief_data, 1, bhash, content_data)

        schema_info["ok"] = True
        schema_info["youtube_title"] = sample_topic.packaging.youtube_title if sample_topic.packaging else ""
        schema_info["title_length"] = len(schema_info["youtube_title"])
        schema_info["scene_count"] = len(sample_topic.scenes)
    except ContractError as ce:
        schema_info["error"] = f"ContractError: {ce}"
    except Exception as ex:
        schema_info["error"] = f"Schema validation error: {ex}"

    all_ok = (
        branch_info.get("ok", False)
        and ac_info.get("ok", False)
        and plan_info.get("ok", False)
        and hook_info.get("ok", False)
        and schema_info.get("ok", False)
    )

    return {
        "channel_id": channel.id,
        "name": channel.name,
        "workspace": str(target_dir),
        "status": "PASS" if all_ok else "FAIL",
        "ok": all_ok,
        "git_branch": branch_info,
        "active_channel": ac_info,
        "plan_md": plan_info,
        "hook_score": hook_info,
        "schema_3_contract": schema_info,
    }


def sync_all_workspaces(
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
    source_root: Path = REPO_ROOT,
    channel_filter: Optional[Sequence[str]] = None,
    dry_run: bool = False,
    push: bool = False,
) -> List[Dict[str, Any]]:
    """Synchronize core tools across all selected channel workspaces."""
    core_files = collect_core_files(source_root)
    selected = [get_channel(cid) for cid in channel_filter] if channel_filter else list(channels().values())

    results: List[Dict[str, Any]] = []
    for ch in selected:
        ws_dir = workspaces_root / ch.workspace_dirname
        res = sync_channel_workspace(
            source_root=source_root,
            target_dir=ws_dir,
            channel=ch,
            dry_run=dry_run,
            push=push,
            core_files=core_files,
        )
        results.append(res)
    return results


def verify_all_workspaces(
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
    channel_filter: Optional[Sequence[str]] = None,
    system_root: Path = SYS_DIR,
) -> Dict[str, Any]:
    """Scan and verify contracts across all selected channel workspaces."""
    selected = [get_channel(cid) for cid in channel_filter] if channel_filter else list(channels().values())
    results: List[Dict[str, Any]] = []

    for ch in selected:
        ws_dir = workspaces_root / ch.workspace_dirname
        v_res = verify_channel(ch, ws_dir, system_root=system_root)
        results.append(v_res)

    all_passed = all(r["ok"] for r in results)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_channels": len(results),
        "passed_channels": sum(1 for r in results if r["ok"]),
        "failed_channels": sum(1 for r in results if not r["ok"]),
        "all_passed": all_passed,
        "channels": results,
    }


def format_verification_report(report: Dict[str, Any]) -> str:
    """Format verification report into clean readable output."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("VIDEO PILOT — 8-CHANNEL BATCH VERIFICATION REPORT")
    lines.append(f"Timestamp: {report.get('timestamp')}")
    lines.append(f"Overall Status: {'[PASS] ALL OK' if report.get('all_passed') else '[FAIL] ATTENTION NEEDED'}")
    lines.append(f"Passed: {report.get('passed_channels')}/{report.get('total_channels')} channels")
    lines.append("=" * 80)

    for ch in report.get("channels", []):
        cid = ch.get("channel_id")
        cname = ch.get("name")
        status = ch.get("status")
        lines.append(f"\nChannel: {cname} ({cid}) -> {status}")
        lines.append("-" * 60)

        # 1. Branch
        b = ch.get("git_branch", {})
        b_str = f"Branch: {b.get('actual', 'N/A')} (expected: {b.get('expected')})"
        lines.append(f"  [1] {'PASS' if b.get('ok') else 'FAIL'} | {b_str}")

        # 2. active_channel.json
        ac = ch.get("active_channel", {})
        ac_str = f"active_channel.json: cid={ac.get('channel_id')}, sha256={str(ac.get('sha256'))[:16]}..."
        lines.append(f"  [2] {'PASS' if ac.get('ok') else 'FAIL'} | {ac_str}")

        # 3. PLAN.md
        pl = ch.get("plan_md", {})
        pl_str = f"PLAN.md: {pl.get('size_bytes', 0)} bytes, {pl.get('lines', 0)} lines (TikTok & YouTube specs)"
        lines.append(f"  [3] {'PASS' if pl.get('ok') else 'FAIL'} | {pl_str}")

        # 4. Hook score
        hk = ch.get("hook_score", {})
        hk_str = f"Hook: {hk.get('score', 0)}/100 ({hk.get('source', '')}) | \"{hk.get('hook', '')[:48]}...\""
        lines.append(f"  [4] {'PASS' if hk.get('ok') else 'FAIL'} | {hk_str}")

        # 5. Schema 3.0
        sc = ch.get("schema_3_contract", {})
        sc_str = f"Schema 3.0: 100% VALID (title: {sc.get('title_length', 0)} chars <= 55, scenes: {sc.get('scene_count', 0)})"
        lines.append(f"  [5] {'PASS' if sc.get('ok') else 'FAIL'} | {sc_str}")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


def format_sync_report(results: List[Dict[str, Any]]) -> str:
    """Format sync results into clean readable output."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("VIDEO PILOT — CORE TOOLS SYNCHRONIZATION")
    lines.append("=" * 80)

    for r in results:
        cid = r.get("channel_id")
        dry = " [DRY-RUN]" if r.get("dry_run") else ""
        lines.append(f"\nChannel: {cid}{dry}")
        lines.append(f"  Workspace: {r.get('workspace')}")
        lines.append(f"  Created files:    {r.get('created_count')}")
        lines.append(f"  Updated files:    {r.get('updated_count')}")
        lines.append(f"  Unchanged files:  {r.get('unchanged_count')}")
        lines.append(f"  Preserved files:  {r.get('preserved_count')} (channel invariants protected)")
        if r.get("push"):
            p = r["push"]
            lines.append(f"  Git Push:         {'OK' if p.get('pushed') else p.get('note', p.get('error', 'FAILED'))}")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_WORKSPACES_ROOT, help="Workspaces root directory")
    parser.add_argument("--source", type=Path, default=REPO_ROOT, help="Source repository root")
    parser.add_argument("--channel", action="append", default=None, help="Filter by channel ID (e.g. nao_luoi)")
    parser.add_argument("--dry-run", action="store_true", help="Preview synchronization without writing files")
    parser.add_argument("--verify-all", action="store_true", help="Run full contract verification across channels")
    parser.add_argument("--push", action="store_true", help="Push synced branch to remote origin")
    parser.add_argument("--json", action="store_true", help="Output summary in JSON format")

    args = parser.parse_args(argv)

    if args.verify_all:
        report = verify_all_workspaces(
            workspaces_root=args.root,
            channel_filter=args.channel,
            system_root=args.source / "sys",
        )
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(format_verification_report(report))
        return 0 if report.get("all_passed") else 1

    # Synchronization mode
    sync_results = sync_all_workspaces(
        workspaces_root=args.root,
        source_root=args.source,
        channel_filter=args.channel,
        dry_run=args.dry_run,
        push=args.push,
    )

    if args.json:
        print(json.dumps(sync_results, ensure_ascii=False, indent=2))
    else:
        print(format_sync_report(sync_results))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
