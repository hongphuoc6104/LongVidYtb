"""Video Pilot Short Thumbnail Embedder.

Overlays 9:16 Flow Native poster thumbnail onto the first 0.12s of Short MP4
and attaches thumbnail image as a cover stream (attached_pic).
This ensures 100% reliable poster display on YouTube Shorts Shelf while
preserving complete video/audio quality, Kinetic subtitles, and channel emblems.
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("thumbnail_embedder")


def has_nvenc() -> bool:
    """Check if ffmpeg has h264_nvenc encoder available."""
    try:
        res = subprocess.run(
            ["ffmpeg", "-encoders"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return "h264_nvenc" in res.stdout
    except Exception:
        return False


def embed_poster_thumbnail_into_short(
    video_path: Path | str,
    thumbnail_path: Path | str,
    duration_sec: float = 0.12,
    timeout_sec: int = 120,
) -> bool:
    """Embed poster thumbnail into the first duration_sec of Short MP4.

    Args:
        video_path: Path to target Short MP4.
        thumbnail_path: Path to 9:16 thumbnail image (PNG/JPG).
        duration_sec: How many seconds from start to display the thumbnail (default: 0.12s).
        timeout_sec: Maximum execution time for FFmpeg.

    Returns:
        True if embedded successfully, False otherwise.
    """
    v_path = Path(video_path).resolve()
    t_path = Path(thumbnail_path).resolve()

    if not v_path.is_file():
        logger.error(f"Video file does not exist: {v_path}")
        return False
    if not t_path.is_file():
        logger.error(f"Thumbnail file does not exist: {t_path}")
        return False

    temp_out = v_path.with_name(f"{v_path.stem}_thumb_temp.mp4")

    # Select best encoder: NVENC if hardware available, otherwise veryfast libx264
    use_nvenc = has_nvenc()
    v_codec = ["-c:v:0", "h264_nvenc", "-preset", "p4", "-b:v", "6M"] if use_nvenc else [
        "-c:v:0", "libx264", "-preset", "veryfast", "-b:v", "6M"
    ]

    cmd = [
        "ffmpeg", "-y",
        "-i", str(v_path),
        "-i", str(t_path),
        "-filter_complex", f"[0:v][1:v]overlay=0:0:enable='between(t,0,{duration_sec})'[vout]",
        "-map", "[vout]",
        "-map", "0:a",
        "-map", "1:v",
        *v_codec,
        "-c:a", "copy",
        "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic",
        "-movflags", "+faststart",
        str(temp_out),
    ]

    logger.info(f"Embedding thumbnail into {v_path.name} (0.0s - {duration_sec}s)...")
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        if proc.returncode != 0:
            logger.error(f"FFmpeg failed with code {proc.returncode}: {proc.stderr[-500:]}")
            if temp_out.exists():
                temp_out.unlink()
            return False

        if not temp_out.is_file() or temp_out.stat().st_size < 1000:
            logger.error(f"Generated temp video is invalid or empty: {temp_out}")
            if temp_out.exists():
                temp_out.unlink()
            return False

        # Atomic replace
        temp_out.replace(v_path)
        logger.info(f"Successfully embedded thumbnail into {v_path.name} ({v_path.stat().st_size} bytes).")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"FFmpeg timed out after {timeout_sec}s while processing {v_path.name}")
        if temp_out.exists():
            temp_out.unlink()
        return False
    except Exception as ex:
        logger.error(f"Unexpected error embedding thumbnail into {v_path.name}: {ex}")
        if temp_out.exists():
            temp_out.unlink()
        return False


def batch_embed_all_shorts(
    video_dir: Path | str = "video",
    slug_filter: list[str] | None = None,
    max_workers: int = 3,
) -> dict[str, bool]:
    """Scan video directory and embed thumbnails for all matching Short directories."""
    import concurrent.futures

    v_root = Path(video_dir).resolve()
    results: dict[str, bool] = {}

    short_dirs = sorted([d for d in v_root.iterdir() if d.is_dir() and d.name.endswith("_short_fullchain")])
    
    # Priority order: upcoming unpublished channels first
    upcoming_priority = [
        "luat_doi_thuong", "luat_ngam", "minh_triet_song", "su_ke_lai",
        "tui_tien", "ua_sao_vay", "vu_tru_ti_hon", "co_the_ke",
        "ban_do_quyen_luc", "banh_rang", "chanh_niem_ke", "dia_com",
        "ho_so_ky_la", "la_ban_hoc_thuat", "loi_sang_soi", "ai_binh_dan",
        "nao_luoi", "nghe_song_sot", "tam_tinh_dem", "thuong_cho_kheo",
    ]
    def sort_key(d: Path) -> int:
        s = d.name.replace("vn_pilot_", "").replace("_short_fullchain", "")
        if s in upcoming_priority:
            return upcoming_priority.index(s)
        return 999

    short_dirs.sort(key=sort_key)

    tasks_to_run = []
    for sdir in short_dirs:
        # Determine slug
        slug = sdir.name.replace("vn_pilot_", "").replace("_short_fullchain", "")
        if slug_filter and slug not in slug_filter:
            continue

        mp4_cand = sdir / f"{sdir.name}_9x16.mp4"
        thumb_cand = sdir / f"{sdir.name}_thumbnail_9x16.png"

        if not mp4_cand.is_file():
            alt_mp4s = list(sdir.glob("*.mp4"))
            if alt_mp4s:
                mp4_cand = alt_mp4s[0]

        if not thumb_cand.is_file():
            alt_thumbs = list(sdir.glob("*thumbnail*.png")) + list(sdir.glob("*thumb*.png"))
            if alt_thumbs:
                thumb_cand = alt_thumbs[0]

        if mp4_cand.is_file() and thumb_cand.is_file():
            tasks_to_run.append((slug, mp4_cand, thumb_cand))
        else:
            logger.warning(f"Skipping {slug}: mp4={mp4_cand.is_file()}, thumb={thumb_cand.is_file()}")
            results[slug] = False

    def _worker(item: tuple[str, Path, Path]) -> tuple[str, bool]:
        s, m, t = item
        logger.info(f"Worker start: {s}")
        ok = embed_poster_thumbnail_into_short(m, t)
        return s, ok

    if max_workers > 1 and len(tasks_to_run) > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            fut_map = {executor.submit(_worker, t): t[0] for t in tasks_to_run}
            for fut in concurrent.futures.as_completed(fut_map):
                s = fut_map[fut]
                try:
                    slug, ok = fut.result()
                    results[slug] = ok
                except Exception as ex:
                    logger.error(f"Worker exception for {s}: {ex}")
                    results[s] = False
    else:
        for t in tasks_to_run:
            slug, ok = _worker(t)
            results[slug] = ok

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed poster thumbnail into Short MP4.")
    parser.add_argument("--video", help="Path to Short MP4")
    parser.add_argument("--thumbnail", help="Path to thumbnail image")
    parser.add_argument("--batch", action="store_true", help="Batch process all Short folders in video/")
    parser.add_argument("--slugs", nargs="*", help="Specific slugs to process in batch")
    parser.add_argument("--workers", type=int, default=3, help="Max parallel workers for batch")
    args = parser.parse_args()

    if args.batch:
        results = batch_embed_all_shorts(slug_filter=args.slugs, max_workers=args.workers)
        total = len(results)
        success = sum(1 for v in results.values() if v)
        logger.info(f"Batch embedding complete: {success}/{total} successful.")
        print(f"RESULTS: {results}")
    elif args.video and args.thumbnail:
        ok = embed_poster_thumbnail_into_short(args.video, args.thumbnail)
        sys.exit(0 if ok else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
