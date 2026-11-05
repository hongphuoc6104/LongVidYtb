#!/usr/bin/env python3
"""Pilot image regeneration for en-first-principles-batch1-9x16.

SSOT Requirements:
- Regenerate images ONLY for en-first-principles-batch1-9x16 via normal Flow CDP image path (stage_a_images).
- Strict teardown after generation.
- Evaluate with visual_clutter_gate.py.
- Retry failing images up to 2 times.
- Do NOT render video, do NOT touch other packages' images.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pilot_en_first_principles")

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from tools.channel_production_common import stage_a_images
from tools.visual_clutter_gate import scan_run_directory


def teardown_flow_pool() -> None:
    """Ensure strict teardown of any spawned Chrome CDP processes."""
    logger.info("[*] Executing strict Flow CDP teardown...")
    try:
        from flow_cdp.multi_profile_manager import MultiProfileManager

        mgr = MultiProfileManager()
        mgr.stop()
        logger.info("[✓] MultiProfileManager stopped successfully.")
    except Exception as exc:
        logger.warning(f"Teardown exception: {exc}")


def run_pilot(max_retries: int = 2) -> Dict[str, Any]:
    job_dir = SYS_DIR / "runs/en-first-principles-batch1-9x16"
    channel_id = "en_first_principles"
    format_profile = "short_9x16"

    brief_file = job_dir / "brief.json"
    content_file = job_dir / "content.json"

    brief = json.loads(brief_file.read_text(encoding="utf-8"))
    content = json.loads(content_file.read_text(encoding="utf-8"))

    logger.info(f"[*] Starting pilot generation for {job_dir.name}...")

    # Initial generation of all pending images
    try:
        stage_a_images(
            sys_dir=SYS_DIR,
            job_dir=job_dir,
            channel_id=channel_id,
            brief=brief,
            content=content,
            format_profile=format_profile,
        )
    finally:
        teardown_flow_pool()

    # Visual clutter gate evaluation
    logger.info("[*] Running visual clutter gate scan...")
    report = scan_run_directory(job_dir, threshold=0.60)
    logger.info(
        f"Gate initial pass rate: {report['passing_count']}/{report['total_images']} "
        f"({report['passing_count']/max(1, report['total_images'])*100:.1f}%)"
    )

    # Retry failures up to max_retries
    retry_count = 0
    while report["failing_count"] > 0 and retry_count < max_retries:
        retry_count += 1
        logger.warning(
            f"[!] Retry round {retry_count}/{max_retries}: {report['failing_count']} images failed gate."
        )

        for failed in report["failing_images"]:
            fpath = Path(failed["path"])
            logger.info(f"  Removing failed image to trigger re-generation: {fpath.name}")
            if fpath.exists():
                fpath.unlink()
            sidecar = fpath.with_suffix(".json")
            if sidecar.exists():
                sidecar.unlink()

        try:
            stage_a_images(
                sys_dir=SYS_DIR,
                job_dir=job_dir,
                channel_id=channel_id,
                brief=brief,
                content=content,
                format_profile=format_profile,
            )
        finally:
            teardown_flow_pool()

        report = scan_run_directory(job_dir, threshold=0.60)
        logger.info(
            f"Gate pass rate after retry {retry_count}: {report['passing_count']}/{report['total_images']} "
            f"({report['passing_count']/max(1, report['total_images'])*100:.1f}%)"
        )

    # Sample 4 images
    rev_img_dir = job_dir / "revisions/images/1"
    sample_images = sorted([
        str(p.resolve())
        for p in rev_img_dir.glob("*.jpg")
        if not p.name.startswith("_") and p.name != "thumbnail_9x16.jpg"
    ])[:4]

    summary = {
        "job_dir": str(job_dir),
        "total_images": report["total_images"],
        "passing_count": report["passing_count"],
        "failing_count": report["failing_count"],
        "pass_rate": round(report["passing_count"] / max(1, report["total_images"]), 4),
        "retries_used": retry_count,
        "sample_images": sample_images,
        "report": report,
    }

    # Save pilot summary
    summary_path = job_dir / "pilot_clutter_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info(f"[✓] Pilot completed. Summary saved to {summary_path}")
    return summary


if __name__ == "__main__":
    res = run_pilot()
    print("\n================ PILOT RESULT ================")
    print(f"Pass Rate: {res['passing_count']}/{res['total_images']} ({res['pass_rate']*100:.1f}%)")
    print("Sample Images:")
    for img in res["sample_images"]:
        print(f"  - {img}")
    sys.exit(0 if res["failing_count"] == 0 else 1)
