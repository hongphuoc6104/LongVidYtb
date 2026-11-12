#!/usr/bin/env python3
"""Resolve Shorts Duplicates and Missing Thumbnails for Video Pilot.

1. Identifies duplicate short video uploads on a given channel.
2. Checks views of each upload.
3. Permanently deletes duplicate uploads with lower view counts via YouTube Studio CDP.
4. Uploads / updates the custom 16:9 / 9:16 thumbnail on the retained video.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for p in (str(REPO_ROOT), str(SYS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from flow_cdp.process_manager import get_process_manager, is_port_listening
from flow_cdp.resource_locks import ProfilePortLock, is_port_locked_by_another_process
from tools.dashboard_catalog_engine import scrape_channel_tabs_bulk
from tools.publish_youtube_cdp import YouTubeCDPClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("resolve_shorts")

MAP_FILE = SYS_DIR / "channels" / "youtube_channel_map.json"


def get_channel_config(slug: str) -> dict:
    if not MAP_FILE.exists():
        raise FileNotFoundError(f"Channel map not found: {MAP_FILE}")
    data = json.loads(MAP_FILE.read_text(encoding="utf-8"))
    ch = data.get("channels", {}).get(slug)
    if not ch:
        raise ValueError(f"Channel slug '{slug}' not found in channel map")
    return ch


def get_spec_data(slug: str) -> dict:
    spec_path = REPO_ROOT / "video" / f"vn_pilot_{slug}_short_fullchain" / f"{slug}_short_aligned_spec.json"
    data = {}
    if spec_path.exists():
        data = json.loads(spec_path.read_text(encoding="utf-8"))
    if slug == "tui_tien" and not data.get("title") and not data.get("youtube_title"):
        data["title"] = "Bẫy Giá Mồi: Vì Sao Bạn Luôn Chọn Cỡ Lớn?"
    return data


def get_thumbnail_path(slug: str) -> Path:
    return REPO_ROOT / "video" / f"vn_pilot_{slug}_short_fullchain" / f"vn_pilot_{slug}_short_fullchain_thumbnail_9x16.png"


async def delete_video_by_id(client: YouTubeCDPClient, video_id: str) -> bool:
    """Navigate to video edit page in Studio and delete it permanently."""
    edit_url = f"https://studio.youtube.com/video/{video_id}/edit"
    logger.info("Navigating to %s to delete video %s...", edit_url, video_id)
    await client.call("Page.navigate", {"url": edit_url})
    await asyncio.sleep(6.0)
    await client.dismiss_studio_interstitials()

    # 1. Click overflow menu button
    logger.info("Clicking overflow menu button on edit page...")
    click_res = await client.evaluate("""
        (() => {
            const btn = document.querySelector('ytcp-video-overflow-menu #overflow-menu-button, #overflow-menu-button');
            if (!btn) return { found: false };
            const inner = btn.querySelector('button') || btn;
            inner.click();
            return { found: true };
        })()
    """)
    if not click_res or not click_res.get("found"):
        logger.error("Could not find overflow menu button on %s", edit_url)
        return False
    await asyncio.sleep(1.5)

    # 2. Click 'Xóa' / 'Delete' menu item
    logger.info("Clicking 'Xóa' menu item...")
    del_click = await client.evaluate("""
        (() => {
            const items = Array.from(document.querySelectorAll('tp-yt-paper-item'));
            const delItem = items.find(it => (it.innerText || '').includes('Xóa') || (it.innerText || '').includes('Delete'));
            if (!delItem) return { found: false };
            delItem.click();
            return { found: true };
        })()
    """)
    if not del_click or not del_click.get("found"):
        logger.error("Could not find 'Xóa' item in popup menu")
        return False
    await asyncio.sleep(2.0)

    # 3. Check confirmation checkbox
    logger.info("Checking confirmation checkbox...")
    cb_status = await client.evaluate("""
        (() => {
            const cb = document.querySelector('#confirm-checkbox, ytcp-checkbox-lit#confirm-checkbox, #dialog-checkbox');
            if (!cb) return { ok: false, error: 'no_cb' };
            const box = cb.querySelector('#checkbox') || cb;
            box.click();
            return { ok: true };
        })()
    """)
    if not cb_status or not cb_status.get("ok"):
        logger.error("Could not check delete confirmation checkbox: %s", cb_status)
        return False
    await asyncio.sleep(1.5)

    # 4. Click confirm button
    logger.info("Clicking confirm permanent delete button...")
    confirm_res = await client.evaluate("""
        (() => {
            const btn = document.querySelector('ytcp-button#confirm-button, #confirm-button');
            if (!btn) return { ok: false, error: 'no_btn' };
            const inner = btn.querySelector('button') || btn;
            const isDisabled = inner.disabled || btn.getAttribute('aria-disabled') === 'true';
            if (isDisabled) return { ok: false, disabled: true };
            inner.click();
            return { ok: true };
        })()
    """)
    if not confirm_res or not confirm_res.get("ok"):
        logger.error("Could not click confirm button: %s", confirm_res)
        return False

    logger.info("Confirm delete clicked. Waiting for deletion redirect...")
    await asyncio.sleep(6.0)
    current_url = await client.evaluate("window.location.href")
    logger.info("Current URL after deletion: %s", current_url)
    return True


async def process_channel(slug: str) -> dict:
    """Analyze shorts, delete duplicate with lower view count, and update thumbnail."""
    ch_info = get_channel_config(slug)
    cid = ch_info.get("youtube_channel_id", "")
    handle = ch_info.get("handle", "")
    port = int(ch_info.get("cdp_port", 9234))

    spec = get_spec_data(slug)
    target_title = spec.get("title") or spec.get("youtube_title") or ""
    thumb_path = get_thumbnail_path(slug)

    logger.info("=== Processing Channel: %s (%s) ===", slug, ch_info.get("channel_name"))
    logger.info("Target title: %s", target_title)
    logger.info("Thumbnail path: %s (exists=%s)", thumb_path, thumb_path.exists())

    # 1. Fetch current public shorts (try handle first, then cid)
    tabs = scrape_channel_tabs_bulk(handle, "")
    if not tabs and cid:
        tabs = scrape_channel_tabs_bulk(handle, cid)
    all_shorts = [v for v in tabs.values() if v.get("is_short")]
    logger.info("Found %d total shorts on channel.", len(all_shorts))

    # Match target title
    matching = []
    for s in all_shorts:
        stitle = s.get("title", "")
        if target_title and (target_title.lower() in stitle.lower() or stitle.lower() in target_title.lower()):
            matching.append(s)

    logger.info("Matching recent shorts count: %d", len(matching))
    for m in matching:
        logger.info("  Candidate: %s | views=%s | title=%s", m.get("video_id"), m.get("view_count"), m.get("title"))

    # Determine kept video and videos to delete
    to_delete = []
    kept_video = None

    if len(matching) > 1:
        # Sort by view count descending
        matching.sort(key=lambda x: (x.get("view_count") or 0), reverse=True)
        kept_video = matching[0]
        to_delete = matching[1:]
        logger.info("Selecting %s (views=%s) to KEEP", kept_video.get("video_id"), kept_video.get("view_count"))
        logger.info("Selecting %d duplicate(s) to DELETE: %s", len(to_delete), [d.get("video_id") for d in to_delete])
    elif len(matching) == 1:
        kept_video = matching[0]
        logger.info("Single matching video found: %s (views=%s). No duplicates to delete.", kept_video.get("video_id"), kept_video.get("view_count"))
    else:
        logger.warning("No matching videos found for target title '%s' on %s!", target_title, slug)
        return {"slug": slug, "status": "NO_MATCHING_VIDEO"}

    profile_cfg = {
        "id": ch_info.get("profile_id"),
        "port": port,
        "directory": ch_info.get("directory"),
        "user_data_dir": ch_info.get("user_data_dir"),
        "email": ch_info.get("email"),
        "handle": handle,
        "youtube_channel_id": cid,
    }

    # Ensure port is clean
    pm = get_process_manager()
    if is_port_listening(port):
        logger.warning("Port %d is already listening. Terminating existing process...", port)
        pm.terminate_by_port(port)
        time.sleep(1.0)

    client = YouTubeCDPClient(profile_cfg, headless=True)
    if not client.ensure_browser():
        logger.error("Could not ensure browser for %s on port %d", slug, port)
        return {"slug": slug, "status": "BROWSER_LAUNCH_FAILED"}

    deleted_ids = []
    thumb_result = None

    try:
        await client.connect()

        # 2. Delete duplicates
        for d in to_delete:
            vid = d.get("video_id")
            logger.info("Deleting duplicate %s (views=%s)...", vid, d.get("view_count"))
            success = await delete_video_by_id(client, vid)
            if success:
                deleted_ids.append(vid)
                logger.info("Successfully deleted duplicate video %s", vid)
            else:
                logger.error("Failed to delete duplicate video %s", vid)

        # 3. Update thumbnail for kept video
        if kept_video and thumb_path.exists():
            k_id = kept_video.get("video_id")
            logger.info("Updating thumbnail for kept video %s using %s...", k_id, thumb_path.name)
            thumb_result = await client.update_video_thumbnail_post_publish(k_id, thumb_path)
            logger.info("Thumbnail update result for %s: %s", k_id, thumb_result)

    finally:
        await client.close()
        pm.terminate_by_port(port)

    return {
        "slug": slug,
        "status": "SUCCESS",
        "kept_video_id": kept_video.get("video_id") if kept_video else None,
        "kept_video_views": kept_video.get("view_count") if kept_video else None,
        "deleted_video_ids": deleted_ids,
        "thumbnail_updated": thumb_result.get("success") if thumb_result else False,
    }


def main():
    parser = argparse.ArgumentParser(description="Resolve Shorts duplicates and missing thumbnails.")
    parser.add_argument("--channel", help="Specific channel slug to process")
    parser.add_argument("--all", action="store_true", help="Process all channels with duplicates or missing thumbnails")
    args = parser.parse_args()

    channels_to_run = []
    if args.channel:
        channels_to_run = [args.channel]
    elif args.all:
        channels_to_run = [
            "ban_do_quyen_luc",
            "banh_rang",
            "chanh_niem_ke",
            "dia_com",
            "ho_so_ky_la",
            "la_ban_hoc_thuat",
            "loi_sang_soi",
            "luat_doi_thuong",
            "luat_ngam",
            "minh_triet_song",
            "su_ke_lai",
            "tui_tien",
            "ua_sao_vay",
            "vu_tru_ti_hon",
            "ai_binh_dan",
            "nao_luoi",
            "nghe_song_sot",
            "thuong_cho_kheo",
        ]
    else:
        parser.error("Must specify --channel <slug> or --all")

    results = {}
    for slug in channels_to_run:
        logger.info("\n" + "="*60 + f"\nSTARTING CHANNEL: {slug}\n" + "="*60)
        try:
            res = asyncio.run(process_channel(slug))
            results[slug] = res
            logger.info("Channel %s result: %s", slug, res)
        except Exception as e:
            logger.error("Channel %s encountered error: %s", slug, e, exc_info=True)
            results[slug] = {"slug": slug, "status": "ERROR", "error": str(e)}
        time.sleep(2.0)

    print("\n" + "="*60 + "\nFINAL EXECUTION REPORT\n" + "="*60)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
