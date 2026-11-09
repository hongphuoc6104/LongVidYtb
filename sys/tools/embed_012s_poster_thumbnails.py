#!/usr/bin/env python3
"""Embed 0.12s Poster Thumbnail into the first 3 frames of all 15 Short videos.

Ensures the YouTube Shorts shelf automatically displays the Flow Native poster
as the video cover frame, while attaching the image as a cover stream.
"""

from __future__ import annotations

import concurrent.futures
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("embed_posters")

SLUGS = [
    "ban_do_quyen_luc",
    "banh_rang",
    "chanh_niem_ke",
    "co_the_ke",
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
]


def embed_poster_for_channel(slug: str) -> dict:
    folder = REPO_ROOT / "video" / f"vn_pilot_{slug}_short_fullchain"
    mp4 = folder / f"vn_pilot_{slug}_short_fullchain_9x16.mp4"
    thumb = folder / f"vn_pilot_{slug}_short_fullchain_thumbnail_9x16.png"
    marker = folder / "_poster_012s_embedded.txt"

    if marker.exists():
        logger.info("[%s] Already has 0.12s poster embedded. Skipping.", slug)
        return {"slug": slug, "status": "ALREADY_DONE"}

    if not mp4.exists() or not thumb.exists():
        logger.error("[%s] Missing mp4 or thumbnail! mp4=%s, thumb=%s", slug, mp4.exists(), thumb.exists())
        return {"slug": slug, "status": "MISSING_FILES"}

    tmp_out = Path(f"/tmp/embed_{slug}.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(mp4),
        "-i", str(thumb),
        "-filter_complex", "[0:v][1:v]overlay=0:0:enable='between(t,0,0.12)'[vout]",
        "-map", "[vout]",
        "-map", "0:a",
        "-map", "1:v",
        "-c:v:0", "libx264",
        "-preset", "veryfast",
        "-b:v", "6M",
        "-c:a", "copy",
        "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic",
        str(tmp_out),
    ]

    logger.info("[%s] Embedding 0.12s poster thumbnail...", slug)
    start_t = time.time()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if res.returncode != 0 or not tmp_out.exists() or tmp_out.stat().st_size < 1000:
        logger.error("[%s] FFmpeg failed: %s", slug, res.stderr[-400:])
        return {"slug": slug, "status": "FAILED", "error": res.stderr[-400:]}

    # Backup original and replace
    backup_path = folder / f"vn_pilot_{slug}_short_fullchain_9x16.mp4.bak_pre_poster"
    if not backup_path.exists():
        shutil.copy2(mp4, backup_path)

    shutil.move(str(tmp_out), str(mp4))
    marker.write_text(f"Embedded 0.12s poster at {time.strftime('%Y-%m-%d %H:%M:%S')}\n", encoding="utf-8")
    dur = round(time.time() - start_t, 2)
    logger.info("[%s] Successfully embedded poster in %ss! Size: %d bytes", slug, dur, mp4.stat().st_size)
    return {"slug": slug, "status": "SUCCESS", "duration_sec": dur}


def main():
    logger.info("==================================================")
    logger.info("Embedding 0.12s Poster Thumbnails into 15 Shorts")
    logger.info("==================================================")

    results = []
    # 2 concurrent workers to respect CPU
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_map = {executor.submit(embed_poster_for_channel, s): s for s in SLUGS}
        for future in concurrent.futures.as_completed(future_map):
            slug = future_map[future]
            try:
                res = future.result()
                results.append(res)
            except Exception as e:
                logger.error("Exception in %s: %s", slug, e)
                results.append({"slug": slug, "status": "EXCEPTION", "error": str(e)})

    logger.info("Embed run complete! Results: %s", results)


if __name__ == "__main__":
    main()
