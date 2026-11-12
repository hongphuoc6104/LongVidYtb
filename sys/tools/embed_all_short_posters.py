#!/usr/bin/env python3
"""Re-embed 0.12s Flow Native Poster Thumbnails into Shorts and update markers."""

import os
import shutil
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VIDEO_DIR = REPO_ROOT / "video"

# 6 upgraded channels
UPGRADED_6 = [
    "co_the_ke",
    "ua_sao_vay",
    "banh_rang",
    "minh_triet_song",
    "loi_sang_soi",
    "tam_tinh_dem",
]

def embed_poster(slug: str, force_reembed: bool = False) -> dict:
    folder = VIDEO_DIR / f"vn_pilot_{slug}_short_fullchain"
    mp4 = folder / f"vn_pilot_{slug}_short_fullchain_9x16.mp4"
    bak = folder / f"vn_pilot_{slug}_short_fullchain_9x16.mp4.bak_pre_poster"
    thumb = folder / f"vn_pilot_{slug}_short_fullchain_thumbnail_9x16.png"
    marker = folder / "_poster_012s_embedded.txt"

    if not mp4.exists() and not bak.exists():
        return {"slug": slug, "status": "NO_MP4", "msg": "Video not rendered yet"}

    if not thumb.exists():
        return {"slug": slug, "status": "NO_THUMBNAIL", "msg": "Thumbnail missing"}

    # Base video: use bak if available to avoid double-embedding
    if bak.exists():
        base_video = bak
    else:
        # Create bak from clean MP4
        shutil.copy2(mp4, bak)
        base_video = bak

    # If marker exists and not forcing reembed (e.g. not one of the upgraded 6), skip
    if marker.exists() and not force_reembed:
        return {"slug": slug, "status": "ALREADY_UP_TO_DATE", "msg": "Marker exists"}

    tmp_out = Path(f"/tmp/embed_{slug}_{int(time.time())}.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(base_video),
        "-i", str(thumb),
        "-filter_complex", "[0:v:0][1:v]overlay=0:0:enable='between(t,0,0.12)'[vout]",
        "-map", "[vout]",
        "-map", "0:a:0",
        "-map", "1:v",
        "-c:v:0", "libx264",
        "-preset", "veryfast",
        "-b:v", "6M",
        "-c:a", "copy",
        "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic",
        str(tmp_out),
    ]

    print(f"[{slug}] Running FFmpeg poster embed from {base_video.name}...")
    t0 = time.time()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if res.returncode != 0 or not tmp_out.exists() or tmp_out.stat().st_size < 10000:
        err = res.stderr[-400:] if res.stderr else "Unknown error"
        print(f"[{slug}] ✗ FFmpeg FAILED: {err}")
        return {"slug": slug, "status": "FAILED", "error": err}

    shutil.move(str(tmp_out), str(mp4))
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    marker.write_text(f"Embedded 0.12s poster at {now_str}\n", encoding="utf-8")
    elapsed = round(time.time() - t0, 2)
    print(f"[{slug}] ✓ Embedded poster in {elapsed}s (Size: {mp4.stat().st_size / 1024 / 1024:.2f} MB)")
    return {"slug": slug, "status": "SUCCESS", "elapsed_sec": elapsed, "size_mb": round(mp4.stat().st_size / 1024 / 1024, 2)}

def main():
    print("=== Re-embedding Upgraded 6 Channels ===")
    results_6 = {}
    for slug in UPGRADED_6:
        # force_reembed = True for the 6 upgraded channels
        res = embed_poster(slug, force_reembed=True)
        results_6[slug] = res

    print("\n=== Verifying All 20 Channels in video/ ===")
    short_dirs = sorted([d.name for d in VIDEO_DIR.iterdir() if d.name.endswith("_short_fullchain")])
    all_results = {}
    for d in short_dirs:
        slug = d.replace("vn_pilot_", "").replace("_short_fullchain", "")
        if slug in results_6 and results_6[slug]["status"] == "SUCCESS":
            all_results[slug] = results_6[slug]
        else:
            res = embed_poster(slug, force_reembed=False)
            all_results[slug] = res

    print("\n=== COMPLETE SHORT EMBED STATUS TABLE ===")
    print(f"| {'Slug':22} | {'Status':18} | {'Details':35} |")
    print("|" + "-"*24 + "|" + "-"*20 + "|" + "-"*37 + "|")
    for s, r in sorted(all_results.items()):
        status = r.get("status", "UNKNOWN")
        detail = f"Size: {r.get('size_mb')}MB ({r.get('elapsed_sec')}s)" if status == "SUCCESS" else r.get("msg", r.get("error", ""))
        print(f"| {s:22} | {status:18} | {detail:35} |")

if __name__ == "__main__":
    main()
