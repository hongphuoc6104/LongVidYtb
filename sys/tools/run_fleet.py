#!/usr/bin/env python3
"""Video Pilot — Fleet Runner for Multi-Channel Wave Production.

Coordinates batch export and production across all 8 channel worktrees
under /home/hongphuoc6104/Desktop/vp-channels/channel-<slug> according to
the resource partition table in contract §1:

1. Step 1: Export bundle via sys/tools/export_v2_bundle.py
2. Step 2: Full production via sys/tools/produce_channel_short_e2e.py (short_9x16)
   or sys/tools/produce_channel_long_e2e.py (long_16x9)

Logs per-channel runs under each worktree's sys/logs/fleet/ directory.
Supports --dry-run and parallel execution (--parallel N).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SYS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SYS_DIR.parent
DEFAULT_WORKTREES_ROOT = Path("/home/hongphuoc6104/Desktop/vp-channels")

# Strict Resource Partition Table from Contract §1
CHANNEL_FLEET_CONFIG: Dict[str, Dict[str, Any]] = {
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

logger = logging.getLogger("run_fleet")


def resolve_channel_targets(channels_arg: Optional[str]) -> List[str]:
    """Parse --channels argument (e.g. 'nao_luoi,tui_tien' or 'all')."""
    if not channels_arg or channels_arg.strip().lower() in ("all", "*"):
        return list(CHANNEL_FLEET_CONFIG.keys())

    selected: List[str] = []
    tokens = [t.strip() for t in channels_arg.split(",") if t.strip()]
    for token in tokens:
        # Check direct channel_id match
        if token in CHANNEL_FLEET_CONFIG:
            selected.append(token)
            continue
        # Check slug match
        matched = False
        for ch_id, cfg in CHANNEL_FLEET_CONFIG.items():
            if cfg["slug"] == token or cfg["slug"].replace("-", "_") == token:
                selected.append(ch_id)
                matched = True
                break
        if not matched:
            raise ValueError(
                f"Unknown channel '{token}'. Valid channels: {list(CHANNEL_FLEET_CONFIG.keys())}"
            )
    return selected


def get_job_id(slug: str, format_profile: str) -> str:
    """Return locked job ID according to Contract §1."""
    if format_profile == "short_9x16":
        return f"{slug}-week1-9x16-v2"
    return f"{slug}-week1-16x9"


def build_channel_plan(
    channel_id: str,
    format_profile: str,
    worktrees_root: Path = DEFAULT_WORKTREES_ROOT,
    skip_export: bool = False,
    skip_produce: bool = False,
) -> Dict[str, Any]:
    """Build planned commands and paths for a single channel run."""
    cfg = CHANNEL_FLEET_CONFIG[channel_id]
    slug = cfg["slug"]
    worktree = worktrees_root / f"channel-{slug}"
    job_id = get_job_id(slug, format_profile)

    # Commands to run
    commands: List[Dict[str, Any]] = []

    if not skip_export:
        export_cmd = [
            sys.executable,
            "sys/tools/export_v2_bundle.py",
            "--channel",
            channel_id,
            "--format",
            format_profile,
            "--root",
            str(worktree),
        ]
        commands.append({
            "step": "export",
            "cmd": export_cmd,
            "cwd": str(worktree),
        })

    if not skip_produce:
        if format_profile == "short_9x16":
            producer = "sys/tools/produce_channel_short_e2e.py"
        else:
            producer = "sys/tools/produce_channel_long_e2e.py"

        produce_cmd = [
            sys.executable,
            producer,
            "--channel",
            channel_id,
            "--job",
            job_id,
            "--colab-account",
            cfg["colab_accounts"],
            "--flow-profiles",
            cfg["flow_profiles"],
            "--session",
            cfg["colab_session"],
        ]
        commands.append({
            "step": "produce",
            "cmd": produce_cmd,
            "cwd": str(worktree),
        })

    return {
        "channel_id": channel_id,
        "slug": slug,
        "format": format_profile,
        "job_id": job_id,
        "worktree": str(worktree),
        "flow_profiles": cfg["flow_profiles"],
        "colab_accounts": cfg["colab_accounts"],
        "colab_session": cfg["colab_session"],
        "commands": commands,
    }


def execute_channel(
    plan: Dict[str, Any],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Execute all planned steps for a single channel, writing to per-channel log file."""
    channel_id = plan["channel_id"]
    worktree = Path(plan["worktree"])
    format_profile = plan["format"]
    job_id = plan["job_id"]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_dir = worktree / "sys" / "logs" / "fleet"
    log_file = log_dir / f"{channel_id}_{format_profile}_{timestamp}.log"

    if dry_run:
        return {
            "channel_id": channel_id,
            "status": "DRY_RUN",
            "job_id": job_id,
            "worktree": str(worktree),
            "log_file": str(log_file),
            "flow_profiles": plan["flow_profiles"],
            "colab_accounts": plan["colab_accounts"],
            "colab_session": plan["colab_session"],
            "commands": plan["commands"],
            "duration": 0.0,
        }

    log_dir.mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    steps_executed: List[str] = []

    with open(log_file, "w", encoding="utf-8") as log_fp:
        log_fp.write(f"=== FLEET RUN START: {channel_id} ({job_id}) at {timestamp} ===\n")
        log_fp.write(f"Worktree: {worktree}\n")
        log_fp.write(f"Flow profiles: {plan['flow_profiles']}\n")
        log_fp.write(f"Colab accounts: {plan['colab_accounts']}\n")
        log_fp.write(f"Colab session: {plan['colab_session']}\n\n")
        log_fp.flush()

        for item in plan["commands"]:
            step_name = item["step"]
            cmd = item["cmd"]
            cwd = item["cwd"]

            log_fp.write(f"\n--- STEP: {step_name} ---\n")
            log_fp.write(f"Command: {' '.join(cmd)}\n")
            log_fp.write(f"CWD: {cwd}\n\n")
            log_fp.flush()

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=cwd,
                    stdout=log_fp,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False,
                )
                if proc.returncode != 0:
                    log_fp.write(f"\n[FAILED] Step {step_name} exited with code {proc.returncode}\n")
                    elapsed = time.time() - start_time
                    return {
                        "channel_id": channel_id,
                        "status": "FAILED",
                        "failed_step": step_name,
                        "exit_code": proc.returncode,
                        "job_id": job_id,
                        "worktree": str(worktree),
                        "log_file": str(log_file),
                        "duration": round(elapsed, 2),
                    }
                steps_executed.append(step_name)
            except Exception as exc:
                log_fp.write(f"\n[EXCEPTION] Step {step_name} encountered: {exc}\n")
                elapsed = time.time() - start_time
                return {
                    "channel_id": channel_id,
                    "status": "ERROR",
                    "failed_step": step_name,
                    "error": str(exc),
                    "job_id": job_id,
                    "worktree": str(worktree),
                    "log_file": str(log_file),
                    "duration": round(elapsed, 2),
                }

        log_fp.write(f"\n=== FLEET RUN COMPLETED SUCCESSFULLY in {time.time() - start_time:.2f}s ===\n")

    elapsed = time.time() - start_time
    return {
        "channel_id": channel_id,
        "status": "SUCCESS",
        "job_id": job_id,
        "worktree": str(worktree),
        "log_file": str(log_file),
        "steps_executed": steps_executed,
        "duration": round(elapsed, 2),
    }


def run_fleet(
    channels: Optional[str] = None,
    format_profile: str = "short_9x16",
    dry_run: bool = False,
    parallel: int = 1,
    worktrees_root: Path = DEFAULT_WORKTREES_ROOT,
    skip_export: bool = False,
    skip_produce: bool = False,
) -> Dict[str, Any]:
    """Coordinate fleet execution across selected channels."""
    target_channels = resolve_channel_targets(channels)
    plans = [
        build_channel_plan(
            ch_id,
            format_profile=format_profile,
            worktrees_root=worktrees_root,
            skip_export=skip_export,
            skip_produce=skip_produce,
        )
        for ch_id in target_channels
    ]

    results: List[Dict[str, Any]] = []
    max_workers = max(1, min(parallel, len(plans)))

    if dry_run or max_workers == 1:
        for plan in plans:
            results.append(execute_channel(plan, dry_run=dry_run))
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(execute_channel, plan, dry_run): plan["channel_id"] for plan in plans}
            for fut in concurrent.futures.as_completed(futures):
                results.append(fut.result())

    # Sort results to match target order
    order_map = {ch: idx for idx, ch in enumerate(target_channels)}
    results.sort(key=lambda r: order_map.get(r["channel_id"], 999))

    summary = {
        "format": format_profile,
        "dry_run": dry_run,
        "parallel": parallel,
        "total_channels": len(results),
        "successful": sum(1 for r in results if r["status"] in ("SUCCESS", "DRY_RUN")),
        "failed": sum(1 for r in results if r["status"] in ("FAILED", "ERROR")),
        "channels": results,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Video Pilot Fleet Production Runner")
    parser.add_argument(
        "--channels",
        default="all",
        help="Comma-separated channel IDs (e.g. nao_luoi,tui_tien) or 'all'",
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=["short_9x16", "long_16x9"],
        help="Format profile to run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned operations and configurations without executing",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of channels to process concurrently (default: 1)",
    )
    parser.add_argument(
        "--worktrees-root",
        type=Path,
        default=DEFAULT_WORKTREES_ROOT,
        help=f"Worktrees parent directory (default: {DEFAULT_WORKTREES_ROOT})",
    )
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Skip export_v2_bundle.py step",
    )
    parser.add_argument(
        "--skip-produce",
        action="store_true",
        help="Skip production step",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    summary = run_fleet(
        channels=args.channels,
        format_profile=args.format,
        dry_run=args.dry_run,
        parallel=args.parallel,
        worktrees_root=args.worktrees_root,
        skip_export=args.skip_export,
        skip_produce=args.skip_produce,
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
