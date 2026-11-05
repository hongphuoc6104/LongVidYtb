#!/usr/bin/env python3
"""Master pipeline script to properly regenerate all 18 test shorts using Google Flow images."""
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
from typing import Any, Dict, List

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
BRAIN_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")

for _p in (str(SYS_DIR), str(SYS_DIR / "tools"), str(ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flow_cdp.cdp_direct_client import PROFILES
from flow_cdp.credit_ledger import CreditLedger
from flow_cdp.multi_profile_manager import MultiProfileManager
from flow_cdp.persistent_pool import PersistentWorkerPool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_all_flow_pilot_redo")

CHANNELS = [
    "en-first-principles-test-20s-9x16",
    "en-scale-and-bone-test-20s-9x16",
    "en-pocket-cosmos-test-20s-9x16",
    "en-deep-time-strata-test-20s-9x16",
    "en-inside-vessel-test-20s-9x16",
    "en-macro-gears-test-20s-9x16",
    "en-fine-print-test-20s-9x16",
    "en-crowd-strings-test-20s-9x16",
    "en-cold-case-ink-test-20s-9x16",
    "en-choke-point-test-20s-9x16",
    "en-root-and-canopy-test-20s-9x16",
    "en-spawn-to-apex-test-20s-9x16",
    "en-second-arrow-test-20s-9x16",
    "en-bamboo-marble-test-20s-9x16",
    "en-kindred-sketch-test-20s-9x16",
    "en-lazy-brain-test-20s-9x16",
    "en-career-leverage-test-20s-9x16",
    "en-wallet-anatomy-test-20s-9x16",
]


def render_short_with_burned_subs(
    job_slug: str,
    frames: List[Path],
    audio_path: Path,
    srt_path: Path,
    out_mp4: Path,
    video_chain_mp4: Path | None = None,
) -> None:
    """Render 1080x1920 MP4 with audio and burned yellow subtitles."""
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    rev_dir = out_mp4.parent / "revisions"
    rev_dir.mkdir(parents=True, exist_ok=True)

    # Backup old MP4 if present
    if out_mp4.is_file():
        backup = rev_dir / f"{job_slug}_crop_ref.mp4"
        if not backup.exists():
            shutil.move(out_mp4, backup)
            logger.info(f"  Moved old cropped-ref MP4 to {backup}")
        else:
            out_mp4.unlink()

    dur_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    total_dur = float(subprocess.check_output(dur_cmd).decode().strip())

    srt_escaped = str(srt_path.resolve()).replace("\\", "/").replace(":", "\\:")
    sub_style = (
        "FontName=Arial,FontSize=18,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,"
        "BorderStyle=1,Outline=2,Shadow=2,Alignment=2,MarginV=120"
    )

    if video_chain_mp4 and video_chain_mp4.is_file() and video_chain_mp4.stat().st_size > 100000:
        # Use synthesized video chain
        logger.info(f"  Rendering with synthesized video chain: {video_chain_mp4}")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_chain_mp4.resolve()),
            "-vf", f"subtitles={srt_escaped}:force_style='{sub_style}'",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            "-t", f"{total_dur:.2f}",
            str(out_mp4.resolve()),
        ]
    else:
        # Images only fallback with subtle pan/zoom on Flow images
        logger.info(f"  Rendering with images_only fallback across {len(frames)} Flow images")
        beat_dur = total_dur / len(frames)
        filter_inputs = []
        filter_chains = []

        for i, frame in enumerate(frames):
            filter_inputs.extend(["-loop", "1", "-t", f"{beat_dur + 0.5:.2f}", "-i", str(frame.resolve())])
            filter_chains.append(
                f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,setsar=1,fps=30[v{i}]"
            )

        concat_inputs = "".join(f"[v{i}]" for i in range(len(frames)))
        concat_filter = f"{concat_inputs}concat=n={len(frames)}:v=1:a=0[vconcat]"
        sub_filter = f"[vconcat]subtitles={srt_escaped}:force_style='{sub_style}'[vfinal]"
        full_filter = ";".join(filter_chains) + ";" + concat_filter + ";" + sub_filter

        cmd = [
            "ffmpeg", "-y",
            *filter_inputs,
            "-i", str(audio_path.resolve()),
            "-filter_complex", full_filter,
            "-map", "[vfinal]",
            "-map", f"{len(frames)}:a",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", f"{total_dur:.2f}",
            str(out_mp4.resolve()),
        ]

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    logger.info(f"  [✓] Master MP4 rendered: {out_mp4} ({out_mp4.stat().st_size / 1024 / 1024:.2f} MB)")


def extract_sample_frame(out_mp4: Path, sample_jpg: Path) -> None:
    """Extract visual frame at second 4.0 for proof catalog."""
    sample_jpg.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", "4.0",
        "-i", str(out_mp4.resolve()),
        "-vframes", "1",
        "-q:v", "2",
        str(sample_jpg.resolve()),
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    logger.info(f"  [✓] Extracted sample frame: {sample_jpg}")


def run_stage_images(target_channels: List[str], max_workers: int = 3) -> Dict[str, Any]:
    """Generate all missing or non-Flow images for target channels using PersistentWorkerPool."""
    ledger = CreditLedger()
    assigned_profiles = sorted(
        PROFILES,
        key=lambda p: ledger.get_balance(str(p.get("name") or p.get("id") or "")),
        reverse=True,
    )
    healthy = [p for p in assigned_profiles if ledger.get_balance(str(p.get("name") or p.get("id") or "")) >= 20]
    logger.info(f"[*] PersistentWorkerPool initialized with {len(healthy)} healthy profiles. Target workers: {max_workers}")

    tasks_submitted = 0
    channel_tasks: Dict[str, List[Dict[str, Any]]] = {}

    pool = PersistentWorkerPool(
        target_workers=max_workers,
        profiles=healthy,
        cooldown_seconds=300.0,
        pacing_seconds=2.5,
        stagger_seconds=0.8,
        headless=True,
        min_credits_required=1,
    )

    t0 = time.time()
    try:
        with pool:
            for job_slug in target_channels:
                job_dir = SYS_DIR / f"runs/{job_slug}"
                img_dir = job_dir / "revisions/images/1"
                img_dir.mkdir(parents=True, exist_ok=True)

                images_json_path = job_dir / "images.json"
                if not images_json_path.is_file():
                    logger.warning(f"Skipping {job_slug}: images.json not found")
                    continue

                images_data = json.loads(images_json_path.read_text(encoding="utf-8"))
                items = images_data.get("items", [])
                channel_tasks[job_slug] = items

                for it in items:
                    task_id = it.get("image_id")
                    target_jpg = img_dir / f"{task_id}_9x16.jpg"
                    target_json = img_dir / f"{task_id}_9x16.json"

                    # Check if already generated with real forgeId
                    if target_jpg.is_file() and target_json.is_file():
                        try:
                            s_data = json.loads(target_json.read_text(encoding="utf-8"))
                            if s_data.get("status") == "downloaded" and s_data.get("forgeId"):
                                logger.info(f"  [cached] {job_slug} {task_id} already valid Flow image")
                                continue
                        except Exception:
                            pass

                    filename = f"{task_id}_9x16.jpg"
                    task_spec = {
                        "id": f"{job_slug}_{task_id}",
                        "jobId": task_id,
                        "prompt": it.get("prompt"),
                        "ratio": "9:16",
                        "filename": filename,
                        "out_dir": str(img_dir),
                        "shot_type": "full_scene",
                        "model": "BELUGA",
                        "max_retries": 4,
                    }
                    pool.submit_task(task_spec)
                    tasks_submitted += 1

            logger.info(f"[*] Submitted {tasks_submitted} Flow image tasks to pool. Waiting for completion...")
            if tasks_submitted > 0:
                completed = pool.wait_completion(timeout=1800.0)
                logger.info(f"[*] Pool wait_completion returned: {completed}. Elapsed: {time.time()-t0:.1f}s")
    finally:
        MultiProfileManager().stop_all_profiles()

    return channel_tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="Master redo script for 18 pilot test shorts.")
    parser.add_argument("--channel", type=str, default=None, help="Specific channel to process, or None for all 18")
    parser.add_argument("--workers", type=int, default=3, help="Worker count for PersistentWorkerPool (default: 3)")
    parser.add_argument("--skip-images", action="store_true", help="Skip image generation phase")
    args = parser.parse_args()

    target_channels = [args.channel] if args.channel else CHANNELS

    if not args.skip_images:
        logger.info(f"==================== PHASE 1: FLOW CDP IMAGE GENERATION ====================")
        run_stage_images(target_channels, max_workers=args.workers)

    logger.info(f"==================== PHASE 2: VIDEO PACKAGING & RENDERING ====================")
    results = []

    for job_slug in target_channels:
        job_dir = SYS_DIR / f"runs/{job_slug}"
        img_dir = job_dir / "revisions/images/1"
        audio_path = job_dir / "revisions/audio/1/narration.wav"
        srt_path = job_dir / "revisions/audio/1/subtitles.srt"
        out_mp4 = ROOT_DIR / f"video/{job_slug}/{job_slug}.mp4"
        sample_jpg = BRAIN_DIR / f"flow_{job_slug}.jpg"

        brief_file = job_dir / "brief.json"
        style_name = "Unknown"
        if brief_file.is_file():
            try:
                b_data = json.loads(brief_file.read_text(encoding="utf-8"))
                style_name = b_data.get("style", "Unknown")
            except Exception:
                pass

        images_json_path = job_dir / "images.json"
        items = []
        if images_json_path.is_file():
            try:
                images_data = json.loads(images_json_path.read_text(encoding="utf-8"))
                items = images_data.get("items", [])
            except Exception:
                pass

        if items:
            frames = [img_dir / f"{it.get('image_id')}_9x16.jpg" for it in items]
        else:
            frames = [img_dir / f"SC01_B{i}_9x16.jpg" for i in range(1, 7)]

        valid_frames = [f for f in frames if f.is_file() and f.stat().st_size > 1000]

        logger.info(f"[*] Processing channel: {job_slug} (Style: {style_name}, Frames: {len(valid_frames)}/6)")

        # Check if flow video clips exist
        flow_video_dir = job_dir / "revisions/flow_video"
        flow_chain_mp4 = flow_video_dir / "stitched_chain.mp4"
        video_chain_to_use = flow_chain_mp4 if flow_chain_mp4.is_file() else None

        clips_count = 0
        if flow_video_dir.is_dir():
            clips_count = len(list(flow_video_dir.glob("*.mp4")))

        try:
            render_short_with_burned_subs(
                job_slug=job_slug,
                frames=valid_frames,
                audio_path=audio_path,
                srt_path=srt_path,
                out_mp4=out_mp4,
                video_chain_mp4=video_chain_to_use,
            )

            extract_sample_frame(out_mp4, sample_jpg)

            # Probe output
            dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(out_mp4)]
            final_dur = float(subprocess.check_output(dur_cmd).decode().strip())

            results.append({
                "job_slug": job_slug,
                "style": style_name,
                "images_count": len(valid_frames),
                "clips_count": clips_count,
                "credits_used": len(valid_frames) * 1 + clips_count * 10,
                "duration": round(final_dur, 1),
                "mp4_path": str(out_mp4),
                "sample_frame": str(sample_jpg),
                "status": "PASS",
                "mode": "full_chain" if video_chain_to_use else "images_only",
            })
        except Exception as exc:
            logger.error(f"[!] Failed processing {job_slug}: {exc}")
            results.append({
                "job_slug": job_slug,
                "style": style_name,
                "images_count": len(valid_frames),
                "clips_count": 0,
                "credits_used": 0,
                "duration": 0,
                "mp4_path": str(out_mp4),
                "sample_frame": "",
                "status": "FAIL",
                "error": str(exc),
            })

    # Summary print
    print("\n==================== PIPELINE EXECUTION SUMMARY ====================")
    for r in results:
        print(f"[{r['status']}] {r['job_slug']} | Style: {r['style']} | Mode: {r.get('mode')} | Flow Images: {r['images_count']} | MP4: {r['mp4_path']}")

    # Save JSON summary
    summary_path = BRAIN_DIR / "flow_pilot_redo_summary.json"
    summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"[✓] Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
