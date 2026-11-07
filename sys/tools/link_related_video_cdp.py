#!/usr/bin/env python3
"""Link published Short (9:16) videos to their corresponding Long (16:9) explainer videos via CDP.

Features:
- Reads channels from sys/channels/youtube_channel_map.json.
- Acquires /tmp/vp_youtube_studio_cdp.lock so only 1 YouTube Studio instance runs at a time.
- Uses YouTubeCDPClient.link_related_video_post_publish to attach related video in YouTube Studio.
- Updates related_video_url in sys/channels/youtube_channel_map.json upon success.
"""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.tools.publish_youtube_cdp import YouTubeCDPClient, verify_short_live

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("link_related_video_cdp")

MAP_PATH = SYS_DIR / "channels" / "youtube_channel_map.json"
STUDIO_LOCK_PATH = Path("/tmp/vp_youtube_studio_cdp.lock")


def get_channel_videos(ch_data: Dict[str, Any]) -> tuple[Dict[str, Any] | None, Dict[str, Any] | None]:
    vids = ch_data.get("published_videos", [])
    shorts = [v for v in vids if v.get("format") == "short_9x16" and v.get("video_url")]
    longs = [v for v in vids if v.get("format") == "long_16x9" and v.get("video_url")]
    short_entry = shorts[-1] if shorts else None
    long_entry = longs[-1] if longs else None
    return short_entry, long_entry


async def link_channel_related_video(ch_id: str, headless: bool = True) -> Dict[str, Any]:
    if not MAP_PATH.exists():
        raise FileNotFoundError(f"{MAP_PATH} not found")

    ch_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    ch_entry = ch_map.get("channels", {}).get(ch_id)
    if not ch_entry:
        raise ValueError(f"Channel '{ch_id}' not found in map")

    short_entry, long_entry = get_channel_videos(ch_entry)
    if not short_entry:
        logger.info("[%s] No published Short found. Skipping.", ch_id)
        return {"channel_id": ch_id, "status": "NO_SHORT"}
    if not long_entry:
        logger.info("[%s] No published Long video found. Skipping.", ch_id)
        return {"channel_id": ch_id, "status": "NO_LONG"}

    short_url = short_entry["video_url"]
    long_url = long_entry["video_url"]
    long_title = long_entry.get("title", "")
    short_id = short_url.rstrip("/").split("/")[-1].split("?")[0]

    # Pre-check live status
    live_status = verify_short_live(short_id)
    if live_status.get("has_pill") and short_entry.get("related_video_url") == long_url:
        logger.info("[%s] Short %s already linked to %s and verified live.", ch_id, short_url, long_url)
        return {"channel_id": ch_id, "status": "ALREADY_LINKED", "short_url": short_url, "long_url": long_url}

    profile_cfg = {
        "id": ch_entry["profile_id"],
        "port": ch_entry.get("cdp_port", 9234),
        "directory": ch_entry["directory"],
        "user_data_dir": ch_entry["user_data_dir"],
        "email": ch_entry["email"],
        "handle": ch_entry.get("handle"),
        "youtube_channel_id": ch_entry.get("youtube_channel_id"),
    }

    STUDIO_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STUDIO_LOCK_PATH, "w", encoding="utf-8") as studio_lk:
        logger.info("[%s] Waiting for global YouTube Studio lock...", ch_id)
        fcntl.flock(studio_lk.fileno(), fcntl.LOCK_EX)
        try:
            logger.info("[%s] Linking Short %s -> Long %s (%s)...", ch_id, short_url, long_url, long_title)
            client = YouTubeCDPClient(profile_cfg, headless=headless)
            client.ensure_browser()
            await client.connect()
            try:
                res = await client.link_related_video_post_publish(
                    short_url_or_id=short_url,
                    related_url_or_id=long_url,
                    target_title=long_title,
                    handle=ch_entry.get("handle"),
                )
            finally:
                await client.close()
                client.terminate_browser()

            if res.get("linked_via_cdp"):
                logger.info("[%s] Link SUCCESS via CDP. Updating channel map...", ch_id)
                lock_path = MAP_PATH.with_suffix(".lock")
                with open(lock_path, "w", encoding="utf-8") as lock_fh:
                    fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
                    try:
                        latest_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
                        target_ch = latest_map.get("channels", {}).get(ch_id, {})
                        for v in target_ch.get("published_videos", []):
                            if v.get("video_url") == short_url:
                                v["related_video_url"] = long_url
                                break
                        MAP_PATH.write_text(json.dumps(latest_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                    finally:
                        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
                return {"channel_id": ch_id, "status": "LINKED", "short_url": short_url, "long_url": long_url, "details": res}
            else:
                logger.warning("[%s] Link finished with status: %s", ch_id, res)
                return {"channel_id": ch_id, "status": "FAILED_OR_FALLBACK", "details": res}
        finally:
            fcntl.flock(studio_lk.fileno(), fcntl.LOCK_UN)


def main():
    parser = argparse.ArgumentParser(description="Link published Shorts to Long videos via CDP")
    parser.add_argument("--channels", required=True, help="Comma-separated channel IDs, or 'all'")
    parser.add_argument("--no-headless", action="store_true", help="Run headed Chrome")
    args = parser.parse_args()

    if args.channels.strip().lower() == "all":
        ch_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        targets = list(ch_map.get("channels", {}).keys())
    else:
        targets = [c.strip().replace("-", "_") for c in args.channels.split(",") if c.strip()]

    results = []
    for ch_id in targets:
        try:
            res = asyncio.run(link_channel_related_video(ch_id, headless=not args.no_headless))
            results.append(res)
        except Exception as e:
            logger.error("[%s] Linking error: %s", ch_id, e)
            results.append({"channel_id": ch_id, "status": "ERROR", "error": str(e)})

    print("\n=== LINKING REPORT ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
