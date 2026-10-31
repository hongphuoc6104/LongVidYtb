#!/usr/bin/env python3
"""Video Pilot — V2 Crop-Safety Fleet Auditor.

Audits all 16 V2 production jobs (8 short 9:16 + 8 long 16:9) across channel worktrees:
- Lettering bounds safety (no partial cuts of hand-lettering).
- Primary-subject head safety (no slicing through stickman / character heads).
- Motion visible rect containment at both start and end of camera moves.

Usage:
    python3 sys/tools/audit_crop_safety.py [--all] [--fix]
    python3 sys/tools/audit_crop_safety.py --channel tui_tien [--fix]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SYS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SYS_DIR.parent
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from crop_safety import (
    enforce_scenes_crop_safety,
    validate_scenes_crop_safety,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("audit_crop_safety")

CHANNELS = [
    "nao_luoi",
    "tui_tien",
    "ua_sao_vay",
    "su_ke_lai",
    "thuong_cho_kheo",
    "ho_so_ky_la",
    "co_the_ke",
    "ai_binh_dan",
]

DEFAULT_WORKTREES_DIR = Path("/home/hongphuoc6104/Desktop/vp-channels")


def audit_job(
    job_dir: Path,
    fix: bool = False,
) -> Dict[str, Any]:
    """Audit a single job directory for crop safety violations."""
    content_file = job_dir / "content.json"
    if not content_file.is_file():
        return {
            "job_id": job_dir.name,
            "status": "MISSING_CONTENT",
            "crop_beats": 0,
            "violations": [],
            "repaired": 0,
        }

    try:
        content = json.loads(content_file.read_text(encoding="utf-8"))
    except Exception as ex:
        return {
            "job_id": job_dir.name,
            "status": "CORRUPT_JSON",
            "error": str(ex),
            "crop_beats": 0,
            "violations": [],
            "repaired": 0,
        }

    scenes = content.get("scenes", [])
    images_dir = job_dir / "revisions/images/1"

    # Count crop beats
    crop_beats = 0
    for sc in scenes:
        beats = sc.get("beats") or sc.get("images") or []
        for b in beats:
            if isinstance(b, dict) and b.get("focus") and float(b["focus"].get("scale", 1.0)) > 1.0:
                crop_beats += 1

    violations = validate_scenes_crop_safety(scenes, images_dir=images_dir, raise_on_error=False)

    repaired_count = 0
    if fix and violations:
        repaired_scenes, repaired_count = enforce_scenes_crop_safety(scenes, images_dir=images_dir)
        content["scenes"] = repaired_scenes
        content_file.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        # Re-validate
        remaining = validate_scenes_crop_safety(repaired_scenes, images_dir=images_dir, raise_on_error=False)
        violations = remaining

    return {
        "job_id": job_dir.name,
        "path": str(job_dir),
        "status": "PASS" if not violations else "FAIL",
        "crop_beats": crop_beats,
        "violations": [
            {
                "rule": v.rule,
                "scene": v.scene_id,
                "beat": v.beat_id,
                "image": v.image_id,
                "message": v.message,
                "target_bbox": v.target_bbox.to_list(),
                "visible_start": v.visible_rect_start.to_list(),
                "visible_end": v.visible_rect_end.to_list(),
                "focus": v.focus,
            }
            for v in violations
        ],
        "repaired": repaired_count,
    }


def find_job_dir(channel_slug: str, job_id: str, worktrees_dir: Path) -> Optional[Path]:
    candidates = [
        worktrees_dir / f"channel-{channel_slug}" / "sys/runs" / job_id,
        SYS_DIR / "runs" / job_id,
        REPO_ROOT / "sys/runs" / job_id,
    ]
    for c in candidates:
        if c.is_dir() and (c / "content.json").is_file():
            return c
    return candidates[0] if candidates[0].is_dir() else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Video Pilot — V2 Crop-Safety Fleet Auditor")
    parser.add_argument("--channel", type=str, default=None, help="Specific channel slug or ID")
    parser.add_argument("--all", action="store_true", default=True, help="Audit all 16 V2 jobs")
    parser.add_argument("--fix", action="store_true", help="Auto-repair violating crop beats in content.json")
    parser.add_argument("--worktrees", type=Path, default=DEFAULT_WORKTREES_DIR, help="Path to vp-channels root")
    args = parser.parse_args()

    channels_to_audit = [args.channel.replace("-", "_")] if args.channel else CHANNELS

    results: List[Dict[str, Any]] = []
    total_crop_beats = 0
    total_violations = 0
    total_repaired = 0

    print("\n" + "=" * 80)
    print("VIDEO PILOT V2 — CROP-SAFETY FLEET AUDIT REPORT")
    print(f"Action: {'AUTO-REPAIR (--fix)' if args.fix else 'VERIFICATION ONLY'}")
    print("=" * 80)

    for ch in channels_to_audit:
        slug = ch.replace("_", "-")
        for fmt in ("9x16-v2", "16x9"):
            job_id = f"{slug}-week1-{fmt}"
            job_dir = find_job_dir(slug, job_id, args.worktrees)
            if not job_dir or not job_dir.is_dir():
                logger.warning(f"Job directory not found for {job_id}")
                results.append({"job_id": job_id, "status": "NOT_FOUND", "violations": []})
                continue

            report = audit_job(job_dir, fix=args.fix)
            results.append(report)
            v_count = len(report["violations"])
            c_count = report["crop_beats"]
            r_count = report["repaired"]

            total_crop_beats += c_count
            total_violations += v_count
            total_repaired += r_count

            status_icon = "✓ PASS" if v_count == 0 else f"✗ FAIL ({v_count} violations)"
            if args.fix and r_count > 0:
                status_icon += f" [REPAIRED {r_count}]"

            print(f"[{status_icon:22s}] {job_id:28s} ({c_count:2d} crops)")
            if v_count > 0:
                for v in report["violations"]:
                    print(f"    - [{v['rule']}] {v['scene']} {v['beat']}: {v['message']}")

    print("-" * 80)
    print(f"TOTAL AUDITED JOBS : {len(results)}")
    print(f"TOTAL CROP BEATS   : {total_crop_beats}")
    print(f"TOTAL VIOLATIONS   : {total_violations}")
    if args.fix:
        print(f"TOTAL REPAIRED     : {total_repaired}")
    print("=" * 80 + "\n")

    summary_file = SYS_DIR / "runs/crop_safety_audit.json"
    try:
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        summary_file.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except Exception:
        pass

    return 1 if total_violations > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
