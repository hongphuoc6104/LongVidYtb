#!/usr/bin/env python3
"""Batch YouTube Publisher for Approved Video Pilot Channels.

Iterates over channels approved in sys/channels/video_review_queue.json,
publishes Long 16:9 video first, then Short 9:16 with related-video linking,
updates review queue to PUBLISHED, and archives published deliverables to HDD.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.tools.review_queue_manager import load_review_queue, set_review_decision
from sys.tools.build_review_dashboard import build_review_dashboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("publish_approved_batch")

HDD_ARCHIVE_DIR = Path("/media/hongphuoc6104/DATA_HDD/PipelineFlow_Videos/Archive_Batch2_And_Published_20261103/published")


def publish_job(
    channel_id: str,
    job_id: str,
    format_type: str,
    related_long_url: str | None = None,
    headless: bool = True,
) -> dict[str, Any]:
    """Invoke publish_youtube_cdp.py for a single job."""
    video_dir = REPO_ROOT / "video" / job_id
    mp4_file = video_dir / f"{job_id}.mp4"
    if not mp4_file.exists():
        logger.error("MP4 file not found: %s", mp4_file)
        return {"status": "FAILED", "error": f"MP4 not found: {mp4_file}"}

    publish_dir = video_dir / "publish"
    is_short = (format_type == "short_9x16")
    meta_file = publish_dir / ("youtube_shorts.md" if is_short else "youtube_long.md")
    thumb_file = video_dir / "thumbnail_16x9.jpg"
    srt_file = video_dir / f"{job_id}.srt"
    screenshot_dir = REPO_ROOT / "sys" / "runs" / job_id / "qa"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_file = screenshot_dir / f"publish_{job_id}.png"

    cmd = [
        sys.executable,
        str(SYS_DIR / "tools" / "publish_youtube_cdp.py"),
        "--channel", channel_id,
        "--job-id", job_id,
        "--video", str(mp4_file),
        "--metadata", str(meta_file),
        "--screenshot", str(screenshot_file),
        "--visibility", "PUBLIC",
    ]

    if not is_short and thumb_file.exists():
        cmd.extend(["--thumbnail", str(thumb_file)])
    if srt_file.exists():
        cmd.extend(["--subtitles", str(srt_file)])
    if is_short:
        cmd.append("--short")
        if related_long_url:
            cmd.extend(["--related-video", related_long_url])
    if headless:
        cmd.append("--headless")
    else:
        cmd.append("--no-headless")

    logger.info("Executing: %s", " ".join(cmd[:8]) + " ...")
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        logger.error("Publishing %s failed with code %d:\n%s", job_id, proc.returncode, proc.stderr)
        return {"status": "FAILED", "job_id": job_id, "error": proc.stderr, "stdout": proc.stdout}

    # Extract JSON report from stdout
    output = proc.stdout
    result = {"status": "UNKNOWN", "job_id": job_id}
    if "=== PUBLISH REPORT ===" in output:
        try:
            report_text = output.split("=== PUBLISH REPORT ===")[-1].strip()
            result = json.loads(report_text)
        except Exception as e:
            logger.warning("Could not parse publish report JSON: %s", e)

    logger.info("Publish result for %s: %s (URL: %s)", job_id, result.get("status"), result.get("video_url"))
    return result


def archive_published_job(job_id: str) -> None:
    """Move published video folder to HDD archive if accessible."""
    if not HDD_ARCHIVE_DIR.parent.exists():
        logger.warning("HDD storage not mounted at %s; skipping move.", HDD_ARCHIVE_DIR)
        return

    HDD_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    src_video = REPO_ROOT / "video" / job_id
    dst_video = HDD_ARCHIVE_DIR / job_id

    if src_video.exists():
        logger.info("Archiving published %s to %s...", job_id, dst_video)
        shutil.copytree(str(src_video), str(dst_video), dirs_exist_ok=True)
        # Leave a small marker or symlink
        marker_file = src_video / "ARCHIVED_TO_HDD.txt"
        marker_file.write_text(f"Archived to {dst_video} on {time.ctime()}\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish approved Batch 3 videos to YouTube")
    parser.add_argument("--channel", help="Limit to specific channel")
    parser.add_argument("--max-channels", type=int, default=12, help="Max channels to publish in this run")
    parser.add_argument("--archive-to-hdd", action="store_true", default=True, help="Archive to HDD after publishing")
    args = parser.parse_args()

    queue = load_review_queue()
    items = queue.get("items", {})

    channels_to_publish: dict[str, dict[str, str]] = {}
    for k, v in items.items():
        if v.get("status") == "APPROVED" and v.get("allowed"):
            ch = v.get("channel_id")
            fmt = v.get("format_profile", "long_16x9")
            if args.channel and ch != args.channel:
                continue
            channels_to_publish.setdefault(ch, {})[fmt] = k

    logger.info("Found %d channels ready for publishing: %s", len(channels_to_publish), list(channels_to_publish.keys()))

    count = 0
    for ch, jobs in sorted(channels_to_publish.items()):
        if count >= args.max_channels:
            break
        count += 1
        logger.info("\n=======================================================")
        logger.info("[*] Publishing Channel (%d/%d): %s", count, min(len(channels_to_publish), args.max_channels), ch)
        logger.info("=======================================================")

        long_job = jobs.get("long_16x9")
        short_job = jobs.get("short_9x16")
        long_url = None

        if long_job:
            logger.info("--- Step 1: Publishing Long Video (%s) ---", long_job)
            res_long = publish_job(ch, long_job, "long_16x9")
            if res_long.get("status") == "PUBLISHED":
                long_url = res_long.get("video_url")
                if args.archive_to_hdd:
                    archive_published_job(long_job)

        if short_job:
            logger.info("--- Step 2: Publishing Short Video (%s) with Related Video: %s ---", short_job, long_url)
            res_short = publish_job(ch, short_job, "short_9x16", related_long_url=long_url)
            if res_short.get("status") == "PUBLISHED":
                if args.archive_to_hdd:
                    archive_published_job(short_job)

        time.sleep(2.0)

    # Rebuild review dashboard
    logger.info("Rebuilding Review Dashboard...")
    build_review_dashboard()
    logger.info("All publishing tasks complete!")


if __name__ == "__main__":
    main()
