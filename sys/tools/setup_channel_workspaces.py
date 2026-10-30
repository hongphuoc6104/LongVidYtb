"""Create, sync, and push the 8 per-channel Git branches and local workspaces.

Each channel in ``sys/channels/registry.py`` gets:
1. A dedicated Git branch ``channel/<slug>`` pushed to ``origin/channel/<slug>``.
2. A local workspace directory ``/home/hongphuoc6104/Desktop/vp-channels/channel-<slug>``
   checked out on ``channel/<slug>`` via ``git worktree`` (sharing git objects with
   ``vp-agent-core`` for instant checkout and zero disk bloat).
3. A symlinked ``sys/renderer/node_modules`` so Remotion renders work immediately.
4. A channel lockfile ``sys/channels/active_channel.json`` inside the workspace.

Usage:
    python3 sys/tools/setup_channel_workspaces.py --push
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from channels.registry import ChannelProfile, channel_profile_stamp, channels, get_channel  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKSPACES_ROOT = REPO_ROOT.parent / "vp-channels"


def build_channel_config(ch: ChannelProfile) -> Dict[str, Any]:
    so = ch.speed_optimization
    return {
        "channel_id": ch.id,
        "name": ch.name,
        "git_branch": ch.git_branch,
        "workspace_dirname": ch.workspace_dirname,
        "niche": ch.niche,
        "promise": ch.promise,
        "platform_routing": ch.platform_routing,
        "visual_profile_id": ch.visual.profile_id,
        "voice": ch.voice,
        "speed": ch.speed,
        "wave": ch.wave,
        "channel_profile_stamp": channel_profile_stamp(ch.id),
        "speed_optimization": {
            "render_mode": so.render_mode if so else "hybrid_motion",
            "fast_short_max_images": so.fast_short_max_images if so else 6,
            "spinoff_shorts_per_long": so.spinoff_shorts_per_long if so else 4,
            "remotion_motion_ratio": so.remotion_motion_ratio if so else 0.35,
            "estimated_short_minutes": list(so.estimated_short_minutes) if so else [8, 12],
            "estimated_bundle_minutes": list(so.estimated_bundle_minutes) if so else [35, 45],
        },
        "plan_file": f"sys/channels/{ch.id}/PLAN.md",
    }


def _run(cmd: Sequence[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), check=True, text=True, capture_output=True)


def setup_workspaces(
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
    channel_filter: Optional[Sequence[str]] = None,
    push: bool = False,
) -> List[Dict[str, Any]]:
    workspaces_root.mkdir(parents=True, exist_ok=True)
    selected = [get_channel(cid) for cid in channel_filter] if channel_filter else list(channels().values())
    results: List[Dict[str, Any]] = []

    wt_out = _run(["git", "worktree", "list", "--porcelain"]).stdout
    existing_worktrees = {
        line.split(" ", 1)[1].strip()
        for line in wt_out.splitlines()
        if line.startswith("worktree ")
    }

    for ch in selected:
        branch = ch.git_branch
        ws_dir = workspaces_root / ch.workspace_dirname

        _run(["git", "branch", "-f", branch, "HEAD"])

        if str(ws_dir) in existing_worktrees and ws_dir.exists():
            _run(["git", "checkout", "-B", branch, "HEAD"], cwd=ws_dir)
            _run(["git", "reset", "--hard", branch], cwd=ws_dir)
        else:
            if ws_dir.exists():
                _run(["git", "worktree", "remove", "--force", str(ws_dir)])
            _run(["git", "worktree", "add", "-B", branch, str(ws_dir), branch])

        cfg_path = ws_dir / "sys/channels/active_channel.json"
        cfg_path.write_text(
            json.dumps(build_channel_config(ch), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        for nm_rel in ("sys/node_modules", "sys/renderer/node_modules"):
            src_nm = REPO_ROOT / nm_rel
            dst_nm = ws_dir / nm_rel
            if src_nm.exists() and not dst_nm.exists():
                dst_nm.symlink_to(src_nm)

        if push:
            _run(["git", "push", "-u", "origin", f"{branch}:{branch}", "--force-with-lease"])

        results.append(
            {
                "channel_id": ch.id,
                "branch": branch,
                "workspace": str(ws_dir),
                "pushed": push,
            }
        )
    return results


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_WORKSPACES_ROOT)
    parser.add_argument("--channel", action="append", default=None)
    parser.add_argument("--push", action="store_true", help="Push all channel/<slug> branches to origin")
    args = parser.parse_args(argv)
    summary = setup_workspaces(args.root, args.channel, push=args.push)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
