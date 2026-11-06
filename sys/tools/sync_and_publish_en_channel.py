#!/usr/bin/env python3
"""Synchronize YouTube Channel Branding (Name, Handle, Description, Avatar, Banner)
and Publish Completed Batch-1 Videos (Short 9:16 & Long 16:9) via CDP.

Features:
- Acquires cross-process lock (/tmp/vp_youtube_studio_cdp.lock) so at most 1 YouTube
  Studio Chrome instance runs at a time on the 4C/8T Xeon host.
- Verifies and updates Channel Name, @Handle, Description, Avatar (800x800), and
  Banner (2048x1152) from sys/channels/<channel_id>/assets/channel_setup_spec.json.
- Publishes completed Short (9:16) and/or Long (16:9) MP4s from video/<job_id>/<job_id>.mp4
  and records live URLs in sys/channels/youtube_channel_map.json.
"""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sync_and_publish_en_channel")

MAP_PATH = SYS_DIR / "channels" / "youtube_channel_map.json"
STUDIO_LOCK_PATH = Path("/tmp/vp_youtube_studio_cdp.lock")

PIVOT_ALIAS_MAP = {
    "en_scale_and_bone": "en_scale_and_bone",
    "en-scale-and-bone": "en_scale_and_bone",
    "en_plain_sight_ai": "en_scale_and_bone",
    "en_root_and_canopy": "en_root_and_canopy",
    "en-root-and-canopy": "en_root_and_canopy",
    "en_kitchen_molecules": "en_root_and_canopy",
    "en_spawn_to_apex": "en_spawn_to_apex",
    "en-spawn-to-apex": "en_spawn_to_apex",
    "en_wait_how": "en_spawn_to_apex",
    "en_deep_time_strata": "en_deep_time_strata",
    "en-deep-time-strata": "en_deep_time_strata",
    "en_parable_lamp": "en_deep_time_strata",
}


def resolve_canonical_channel_id(raw: str) -> str:
    clean = raw.strip()
    if clean in PIVOT_ALIAS_MAP:
        return PIVOT_ALIAS_MAP[clean]
    return clean.replace("-", "_")


def build_short_description(spec_data: Dict[str, Any], ch_spec: Dict[str, Any]) -> str:
    full_title = spec_data.get("title") or spec_data.get("youtube_title") or ""
    shots = spec_data.get("shots", [])
    narration_lines = [s.get("narration", "").strip() for s in shots if s.get("narration")]
    summary_text = " ".join(narration_lines[:3])
    ch_desc = ch_spec.get("description", "")
    hashtags = [f"#{k}" for k in ch_spec.get("keywords", [])[:5] if " " not in k]
    tags_line = " ".join(["#shorts", "#explained", "#science"] + hashtags)
    return (
        f"{full_title}\n\n"
        f"{summary_text}\n\n"
        f"---\n"
        f"{ch_desc}\n\n"
        f"{tags_line}"
    ).strip()


def build_long_description(spec_data: Dict[str, Any], ch_spec: Dict[str, Any]) -> str:
    full_title = spec_data.get("title") or spec_data.get("youtube_title") or ""
    shots = spec_data.get("shots", [])
    narration_lines = [s.get("narration", "").strip() for s in shots if s.get("narration")]
    summary_text = " ".join(narration_lines[:4])
    chapters = spec_data.get("chapters", [])
    chapter_lines = []
    if chapters:
        for ch in chapters:
            ts = ch.get("timestamp", "00:00")
            ctitle = ch.get("title", "Chapter")
            chapter_lines.append(f"{ts} {ctitle}")
    else:
        chapter_lines = [
            "00:00 Introduction & Core Mystery",
            "02:05 The Hidden Mechanism",
            "04:20 Real-World Chain Reaction",
            "06:35 The Deeper System Truth",
        ]
    ch_desc = ch_spec.get("description", "")
    hashtags = [f"#{k}" for k in ch_spec.get("keywords", [])[:6] if " " not in k]
    tags_line = " ".join(["#explainer", "#documentary", "#deepdive"] + hashtags)
    chapters_block = "\n".join(chapter_lines)
    return (
        f"{full_title}\n\n"
        f"{summary_text}\n\n"
        f"Chapters:\n{chapters_block}\n\n"
        f"---\n"
        f"{ch_desc}\n\n"
        f"{tags_line}"
    ).strip()


def is_already_published(ch_id: str, fmt: str) -> str | None:
    if not MAP_PATH.exists():
        return None
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    entry = data.get("channels", {}).get(ch_id, {})
    for v in entry.get("published_videos", []):
        if v.get("format") == fmt and v.get("video_url"):
            return v["video_url"]
    return None


def is_branding_verified(ch_id: str, expected_name: str) -> bool:
    if not MAP_PATH.exists():
        return False
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    entry = data.get("channels", {}).get(ch_id, {})
    return bool(
        entry.get("branding_v3_verified")
        and entry.get("channel_name") == expected_name
    )


def mark_branding_verified(ch_id: str, report: Dict[str, Any]) -> None:
    lock_path = MAP_PATH.with_suffix(".lock")
    with open(lock_path, "w", encoding="utf-8") as lock_fh:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
        try:
            data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
            if ch_id in data.get("channels", {}):
                data["channels"][ch_id]["branding_v3_verified"] = True
                data["channels"][ch_id]["branding_verified_at"] = time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                )
                if report.get("youtube_name"):
                    data["channels"][ch_id]["channel_name"] = report["youtube_name"]
                if report.get("handle"):
                    data["channels"][ch_id]["handle"] = report["handle"]
                MAP_PATH.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
        finally:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)


def process_single_channel(
    raw_channel: str,
    force_branding: bool = False,
    publish_short: bool = True,
    publish_long: bool = True,
) -> Dict[str, Any]:
    ch_id = resolve_canonical_channel_id(raw_channel)
    slug = ch_id.replace("_", "-")
    ch_spec_path = SYS_DIR / "channels" / ch_id / "assets" / "channel_setup_spec.json"
    if not ch_spec_path.exists():
        raise FileNotFoundError(f"Missing channel_setup_spec.json: {ch_spec_path}")
    ch_spec = json.loads(ch_spec_path.read_text(encoding="utf-8"))

    short_job_id = f"{slug}-batch1-9x16"
    long_job_id = f"{slug}-batch1-16x9"
    short_mp4 = REPO_ROOT / "video" / short_job_id / f"{short_job_id}.mp4"
    long_mp4 = REPO_ROOT / "video" / long_job_id / f"{long_job_id}.mp4"
    short_spec_path = SYS_DIR / "channels" / "en_batch1_specs" / f"{slug}_short_9x16.json"
    long_spec_path = SYS_DIR / "channels" / "en_batch1_specs" / f"{slug}_long_16x9.json"

    summary: Dict[str, Any] = {
        "channel_id": ch_id,
        "slug": slug,
        "expected_name": ch_spec["youtube_name"],
        "branding_status": "SKIPPED_ALREADY_VERIFIED",
        "short_url": is_already_published(ch_id, "short_9x16"),
        "long_url": is_already_published(ch_id, "long_16x9"),
    }

    STUDIO_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STUDIO_LOCK_PATH, "w", encoding="utf-8") as studio_lk:
        logger.info("[%s] Waiting for global YouTube Studio lock...", ch_id)
        fcntl.flock(studio_lk.fileno(), fcntl.LOCK_EX)
        try:
            # 1. Branding Verification & Setup
            if force_branding or not is_branding_verified(ch_id, ch_spec["youtube_name"]):
                logger.info("[%s] Running YouTube Channel Branding Setup (%s)...", ch_id, ch_spec["youtube_name"])
                from sys.tools.setup_youtube_channel_cdp import setup_youtube_channel

                rep = asyncio.run(setup_youtube_channel(channel_id=ch_id, headless=True))
                mark_branding_verified(ch_id, rep)
                summary["branding_status"] = "UPDATED_AND_VERIFIED"
                summary["branding_report"] = rep
            else:
                logger.info("[%s] Branding V3 already verified for '%s'.", ch_id, ch_spec["youtube_name"])

            # 2. Publish Short (9:16) if ready and not yet published
            if publish_short and not summary["short_url"] and short_mp4.is_file():
                short_spec = json.loads(short_spec_path.read_text(encoding="utf-8"))
                yt_title = short_spec.get("youtube_title") or short_spec.get("title")
                yt_desc = build_short_description(short_spec, ch_spec)
                shot_out = Path(f"/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/qa/publish_{short_job_id}.png")
                cmd = [
                    sys.executable,
                    str(SYS_DIR / "tools" / "publish_youtube_cdp.py"),
                    "--video",
                    str(short_mp4),
                    "--channel",
                    ch_id,
                    "--job-id",
                    short_job_id,
                    "--title",
                    yt_title,
                    "--description",
                    yt_desc,
                    "--short",
                    "--visibility",
                    "PUBLIC",
                    "--headless",
                    "--bypass-review-gate",
                    "--screenshot",
                    str(shot_out),
                ]
                if summary["long_url"]:
                    cmd.extend(["--related-video", summary["long_url"]])
                logger.info("[%s] Publishing Short MP4: %s (title=%r)...", ch_id, short_mp4.name, yt_title)
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                if proc.returncode != 0:
                    logger.error("[%s] Short publish failed:\n%s\n%s", ch_id, proc.stdout[-800:], proc.stderr[-800:])
                    summary["short_error"] = proc.stderr[-500:] or proc.stdout[-500:]
                else:
                    summary["short_url"] = is_already_published(ch_id, "short_9x16")
                    logger.info("[%s] Short published live: %s", ch_id, summary["short_url"])

            # 3. Publish Long (16:9) if ready and not yet published
            if publish_long and not summary["long_url"] and long_mp4.is_file():
                long_spec = json.loads(long_spec_path.read_text(encoding="utf-8"))
                yt_title = long_spec.get("youtube_title") or long_spec.get("title")
                yt_desc = build_long_description(long_spec, ch_spec)
                long_srt = REPO_ROOT / "video" / long_job_id / f"{long_job_id}.srt"
                shot_out = Path(f"/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/qa/publish_{long_job_id}.png")
                cmd = [
                    sys.executable,
                    str(SYS_DIR / "tools" / "publish_youtube_cdp.py"),
                    "--video",
                    str(long_mp4),
                    "--channel",
                    ch_id,
                    "--job-id",
                    long_job_id,
                    "--title",
                    yt_title,
                    "--description",
                    yt_desc,
                    "--visibility",
                    "PUBLIC",
                    "--headless",
                    "--bypass-review-gate",
                    "--screenshot",
                    str(shot_out),
                ]
                if long_srt.is_file():
                    cmd.extend(["--subtitles", str(long_srt)])
                logger.info("[%s] Publishing Long MP4: %s (title=%r)...", ch_id, long_mp4.name, yt_title)
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
                if proc.returncode != 0:
                    logger.error("[%s] Long publish failed:\n%s\n%s", ch_id, proc.stdout[-800:], proc.stderr[-800:])
                    summary["long_error"] = proc.stderr[-500:] or proc.stdout[-500:]
                else:
                    summary["long_url"] = is_already_published(ch_id, "long_16x9")
                    logger.info("[%s] Long published live: %s", ch_id, summary["long_url"])
        finally:
            fcntl.flock(studio_lk.fileno(), fcntl.LOCK_UN)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync YouTube Channel Branding & Publish Completed Videos")
    parser.add_argument("--channels", required=True, help="Comma-separated channel IDs or slugs")
    parser.add_argument("--force-branding", action="store_true", help="Force re-running channel branding setup")
    parser.add_argument("--branding-only", action="store_true", help="Only run channel branding setup")
    args = parser.parse_args()

    channels = [c.strip() for c in args.channels.split(",") if c.strip()]
    results = []
    for raw_ch in channels:
        try:
            res = process_single_channel(
                raw_ch,
                force_branding=args.force_branding,
                publish_short=not args.branding_only,
                publish_long=not args.branding_only,
            )
            results.append(res)
        except Exception as e:
            logger.exception("Error processing channel %s: %s", raw_ch, e)
            results.append({"channel": raw_ch, "error": str(e)})

    print("\n=== SYNC & PUBLISH SUMMARY ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
