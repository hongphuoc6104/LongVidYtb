#!/usr/bin/env python3
"""Rebuild English channels from scratch by studying 1-FPS full frames of real competitor videos.

Workflow per channel:
1. `extract-competitor`: Downloads a real competitor YouTube video (via yt-dlp native HTTP download)
   and extracts 20 consecutive full frames at 1 FPS (`frame_01s.jpg` .. `frame_20s.jpg`) from a
   core 20-second narrative segment (e.g., 00:00:15 to 00:00:35, skipping channel intros).
2. Subagent inspects all 20 frames via `read_file` with ZERO hardcoded style assumptions, analyzes
   the exact visual style, lighting, textures, composition, and second-by-second motion/cuts (1s..20s),
   and writes `<channel>_rebuilt_spec.json`.
3. `build-pilot`: Generates the 8-10 full-frame keyframes via Google Flow CDP (`PersistentWorkerPool`
   with automatic multi-account failover), synthesizes narration (`edge-tts` + `-11.0 LUFS` / `-1.0 dBTP`
   normalization), builds `.srt` cues, and renders both `9:16` (burned-in Vietnamese-standard White
   Arial Bold subtitles at `MarginV=400` + `100x100` rounded watermark at `W-w-24:H-h-50`) and `16:9`
   (sidecar `.srt` + `100x100` rounded watermark at `W-w-36:H-h-36`) 12-20s pilot videos with
   second-by-second camera motion & transitions learned from the competitor video.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image, ImageChops, ImageDraw, ImageFont

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
BRAIN_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")
COMP_FRAMES_DIR = BRAIN_DIR / "competitor_frames"
REBUILT_PILOTS_DIR = BRAIN_DIR / "rebuilt_pilots"

for _p in (str(SYS_DIR), str(SYS_DIR / "tools"), str(ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flow_cdp.cdp_direct_client import PROFILES
from flow_cdp.credit_ledger import CreditLedger
from flow_cdp.multi_profile_manager import MultiProfileManager
from flow_cdp.persistent_pool import PersistentWorkerPool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rebuild_en_competitor")

# Curated real competitor search queries & target timestamps (skipping 0-10s sponsor/logo intros)
COMPETITOR_VIDEO_TARGETS: Dict[str, Dict[str, Any]] = {
    "en-first-principles": {
        "niche": "Mental Models & Physics Paradoxes",
        "competitor_name": "Veritasium",
        "search_query": "ytsearch1:Veritasium physics paradox experiment",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-US-ChristopherNeural",
    },
    "en-scale-and-bone": {
        "niche": "Zoology & Animal Life-Cycle Evolution",
        "competitor_name": "BBC Earth / PBS Eons",
        "search_query": "ytsearch1:BBC Earth animal life cycle documentary",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-GB-RyanNeural",
    },
    "en-pocket-cosmos": {
        "niche": "Astrophysics & Deep Space Exploration",
        "competitor_name": "Melodysheep / Astrum",
        "search_query": "ytsearch1:melodysheep space planets cinematic",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "en-US-GuyNeural",
    },
    "en-deep-time-strata": {
        "niche": "Geology & Deep Earth History",
        "competitor_name": "History of the Earth",
        "search_query": "ytsearch1:History of the Earth geology ancient earth",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "en-GB-RyanNeural",
    },
    "en-inside-vessel": {
        "niche": "Human Physiology & Medical 3D",
        "competitor_name": "Nucleus Medical Media / Institute of Human Anatomy",
        "search_query": "ytsearch1:Nucleus Medical Media 3D human body animation",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-US-EricNeural",
    },
    "en-macro-gears": {
        "niche": "Macroeconomics, Infrastructure & Industrial Engineering",
        "competitor_name": "Practical Engineering / Wendover Productions",
        "search_query": "ytsearch1:Practical Engineering infrastructure how it works",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "en-US-ChristopherNeural",
    },
    "en-fine-print": {
        "niche": "Consumer Law & Hidden Contracts",
        "competitor_name": "LegalEagle / CNBC Make It",
        "search_query": "ytsearch1:CNBC Make It hidden fees contracts explained",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-US-RogerNeural",
    },
    "en-crowd-strings": {
        "niche": "Mass Psychology & Investigative Documentary",
        "competitor_name": "Fern / Academy of Ideas",
        "search_query": "ytsearch1:Fern TV documentary 3D animation",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-US-SteffanNeural",
    },
    "en-cold-case-ink": {
        "niche": "Forensic Mysteries & Unsolved Archives",
        "competitor_name": "LEMMiNO",
        "search_query": "ytsearch1:LEMMiNO mystery documentary",
        "start_sec": 25,
        "duration_sec": 20,
        "voice": "en-GB-RyanNeural",
    },
    "en-choke-point": {
        "niche": "Maritime Geopolitics & Satellite Maps",
        "competitor_name": "RealLifeLore / Johnny Harris",
        "search_query": "ytsearch1:RealLifeLore strait canal map geopolitics",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-US-ChristopherNeural",
    },
    "en-root-and-canopy": {
        "niche": "Botany & Forest Ecology",
        "competitor_name": "BBC Earth / Mossy Earth",
        "search_query": "ytsearch1:BBC Earth Green Planet plants time lapse",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-GB-RyanNeural",
    },
    "en-spawn-to-apex": {
        "niche": "Micro-Biology & Chronological Insect Life-Cycle",
        "competitor_name": "Deep Look PBS",
        "search_query": "ytsearch1:Deep Look PBS insect life cycle macro",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-US-AndrewNeural",
    },
    "en-second-arrow": {
        "niche": "Stoicism & Classical Philosophy",
        "competitor_name": "Einzelgänger / Daily Stoic",
        "search_query": "ytsearch1:Einzelganger stoicism Marcus Aurelius",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "en-GB-RyanNeural",
    },
    "en-bamboo-marble": {
        "niche": "Eastern Philosophy & Contemplative Essays",
        "competitor_name": "Aperture / Pursuit of Wonder",
        "search_query": "ytsearch1:Pursuit of Wonder eastern philosophy",
        "start_sec": 20,
        "duration_sec": 20,
        "voice": "en-US-BrianNeural",
    },
    "en-kindred-sketch": {
        "niche": "Relationships, Empathy & Attachment Psychology",
        "competitor_name": "The School of Life / Cinema Therapy",
        "search_query": "ytsearch1:The School of Life relationships attachment",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-GB-SoniaNeural",
    },
    "en-lazy-brain": {
        "niche": "Neuroscience of Dopamine, Focus & Habits",
        "competitor_name": "Andrew Huberman / Kurzgesagt Habit Science",
        "search_query": "ytsearch1:Kurzgesagt brain habits dopamine",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-US-AndrewNeural",
    },
    "en-career-leverage": {
        "niche": "Workplace Strategy, Economics of Careers & Leverage",
        "competitor_name": "Wall Street Journal / Harvard Business Review",
        "search_query": "ytsearch1:Wall Street Journal career salary negotiation explained",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-US-EricNeural",
    },
    "en-wallet-anatomy": {
        "niche": "Behavioral Pricing & Consumer Finance",
        "competitor_name": "Two Cents PBS / WSJ Consumer Economics",
        "search_query": "ytsearch1:Two Cents PBS behavioral economics pricing",
        "start_sec": 15,
        "duration_sec": 20,
        "voice": "en-US-AndrewNeural",
    },
}


def extract_competitor_frames(
    channel_slug: str,
    custom_query: Optional[str] = None,
    start_sec: Optional[int] = None,
    duration_sec: int = 20,
) -> Dict[str, Any]:
    """Download real competitor video and extract 1-FPS frames (frame_01s.jpg .. frame_20s.jpg)."""
    target = COMPETITOR_VIDEO_TARGETS.get(channel_slug)
    if not target and not custom_query:
        raise ValueError(f"Unknown channel slug '{channel_slug}' and no --query provided.")

    query = custom_query or target["search_query"]
    s_sec = start_sec if start_sec is not None else int(target.get("start_sec", 15))
    d_sec = duration_sec or int(target.get("duration_sec", 20))

    out_dir = COMP_FRAMES_DIR / channel_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_mp4 = out_dir / "competitor_source.mp4"
    clip_mp4 = out_dir / "competitor_segment_20s.mp4"

    # Fetch metadata + download video via yt-dlp native downloader (avoiding ffmpeg HTTPS segfault)
    if not raw_mp4.is_file() or raw_mp4.stat().st_size < 50_000:
        logger.info(f"[{channel_slug}] Downloading competitor reference via '{query}'...")
        cmd_dl = [
            "yt-dlp",
            "--no-playlist",
            "-f", "18/best[ext=mp4][height<=720]/best[ext=mp4]",
            "--write-info-json",
            "-o", str(raw_mp4),
            query,
        ]
        subprocess.run(cmd_dl, check=True, timeout=180)

    # Extract 20-second reference clip locally
    cmd_clip = [
        "ffmpeg", "-y",
        "-ss", str(s_sec),
        "-t", str(d_sec),
        "-i", str(raw_mp4),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        str(clip_mp4),
    ]
    subprocess.run(cmd_clip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Extract 1-FPS full frames: frame_01s.jpg .. frame_20s.jpg
    for old_f in out_dir.glob("frame_*s.jpg"):
        old_f.unlink()

    cmd_frames = [
        "ffmpeg", "-y",
        "-ss", str(s_sec),
        "-t", str(d_sec),
        "-i", str(raw_mp4),
        "-vf", "fps=1",
        "-q:v", "2",
        str(out_dir / "frame_%02ds.jpg"),
    ]
    subprocess.run(cmd_frames, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    frames = sorted(out_dir.glob("frame_*s.jpg"))
    info_json = out_dir / "competitor_source.info.json"
    video_meta = {}
    if info_json.is_file():
        try:
            raw_info = json.loads(info_json.read_text(encoding="utf-8"))
            video_meta = {
                "id": raw_info.get("id"),
                "title": raw_info.get("title"),
                "uploader": raw_info.get("uploader") or raw_info.get("channel"),
                "webpage_url": raw_info.get("webpage_url"),
                "view_count": raw_info.get("view_count"),
                "duration": raw_info.get("duration"),
            }
        except Exception:
            pass

    manifest = {
        "channel_slug": channel_slug,
        "niche": target.get("niche", "") if target else "",
        "competitor_name": target.get("competitor_name", "") if target else "",
        "query": query,
        "segment_start_sec": s_sec,
        "segment_duration_sec": d_sec,
        "video_meta": video_meta,
        "clip_mp4": str(clip_mp4),
        "frames_count": len(frames),
        "frames": [str(f) for f in frames],
    }
    (out_dir / "extraction_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info(f"[✓] [{channel_slug}] Extracted {len(frames)} 1-FPS frames into {out_dir}")
    return manifest


def make_channel_watermark(channel_slug: str, out_png: Path, size: int = 100) -> Path:
    """Create a 100x100 rounded-corner watermark badge matching Vietnamese channel frame spec."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    # Check if an existing brand logo exists
    existing_logo = ROOT_DIR / "sys/assets/brand_logo.png"
    if existing_logo.is_file():
        img = Image.open(existing_logo).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    else:
        img = Image.new("RGBA", (size, size), (24, 28, 36, 235))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((2, 2, size - 3, size - 3), radius=15, outline=(255, 255, 255, 180), width=2)
        initials = "".join(w[0].upper() for w in channel_slug.replace("en-", "").split("-")[:2])
        font = None
        for fc in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ):
            if Path(fc).is_file():
                font = ImageFont.truetype(fc, 36)
                break
        if font:
            bbox = draw.textbbox((0, 0), initials, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((size - tw) // 2, (size - th) // 2 - 4), initials, font=font, fill=(255, 255, 255, 240))

    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle((0, 0, size - 1, size - 1), radius=15, fill=int(round(255 * 0.92)))
    _, _, _, a = img.split()
    img.putalpha(ImageChops.multiply(a, mask))
    img.save(out_png, format="PNG")
    return out_png


async def _synthesize_edge_tts(text: str, voice: str, out_mp3: Path) -> None:
    cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(out_mp3)]
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"edge-tts failed: {stderr.decode()}")


def synthesize_and_normalize_audio(text: str, voice: str, audio_dir: Path) -> tuple[Path, float]:
    audio_dir.mkdir(parents=True, exist_ok=True)
    raw_mp3 = audio_dir / "narration_raw.mp3"
    norm_wav = audio_dir / "narration.wav"
    asyncio.run(_synthesize_edge_tts(text, voice, raw_mp3))
    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_mp3),
        "-af", "loudnorm=I=-11.0:TP=-1.0:LRA=7.0",
        "-ar", "48000", "-ac", "2",
        str(norm_wav),
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    dur_out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(norm_wav),
    ]).decode().strip()
    return norm_wav, float(dur_out)


def build_vietnamese_standard_srt(beats: List[Dict[str, Any]], total_dur: float, srt_path: Path) -> List[float]:
    """Build clean SRT cues (no HTML tags so libass renders pure White Arial Bold with Black Outline)
    and return exact per-beat durations synced to the narration audio."""
    texts = [str(b.get("narration", "")).strip() for b in beats]
    word_counts = [max(1, len(t.split())) for t in texts]
    total_words = sum(word_counts)

    beat_durations: List[float] = []
    srt_entries: List[str] = []
    cue_idx = 1
    cur_t = 0.0

    for i, (words, text) in enumerate(zip(word_counts, texts)):
        dur = round((words / total_words) * total_dur, 3) if i < len(beats) - 1 else max(0.4, round(total_dur - cur_t, 3))
        beat_durations.append(dur)
        b_start = cur_t
        b_end = min(total_dur, cur_t + dur)
        cur_t = b_end

        w_list = text.split()
        if not w_list:
            continue
        # 5-7 words per subtitle cue (2 short lines max, matching VN standard)
        chunk_size = 6
        chunks = [" ".join(w_list[j:j + chunk_size]) for j in range(0, len(w_list), chunk_size)]
        c_dur = (b_end - b_start) / len(chunks)
        for c_i, chunk in enumerate(chunks):
            cs = b_start + c_i * c_dur
            ce = min(b_end, cs + c_dur)

            def _fmt(sec: float) -> str:
                ms = max(0, int(round(sec * 1000)))
                s, ms = divmod(ms, 1000)
                m, s = divmod(s, 60)
                h, m = divmod(m, 60)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            srt_entries.append(f"{cue_idx}\n{_fmt(cs)} --> {_fmt(ce)}\n{chunk}\n")
            cue_idx += 1

    srt_path.parent.mkdir(parents=True, exist_ok=True)
    srt_path.write_text("\n".join(srt_entries), encoding="utf-8")
    return beat_durations


def generate_flow_images_for_spec(
    channel_slug: str,
    beats: List[Dict[str, Any]],
    img_dir: Path,
    profile_names: Optional[List[str]] = None,
    max_workers: int = 4,
    both_native: bool = False,
) -> Dict[str, List[Path]]:
    """Generate 9:16 (and 16:9) images on Google Flow CDP using PersistentWorkerPool with full-pool failover."""
    img_dir.mkdir(parents=True, exist_ok=True)
    ledger = CreditLedger()

    all_healthy = [
        p for p in PROFILES
        if ledger.get_balance(p["name"]) >= 10 and p["name"] not in ("profile_1", "profile_13")
    ]
    if profile_names:
        preferred = [p for p in all_healthy if p["name"] in profile_names]
        fallback = [p for p in all_healthy if p["name"] not in profile_names]
        candidate_profiles = preferred + fallback
    else:
        candidate_profiles = all_healthy

    if not candidate_profiles:
        candidate_profiles = [p for p in PROFILES if p["name"] not in ("profile_1", "profile_13")]

    tasks = []
    for idx, beat in enumerate(beats, 1):
        beat_id = beat.get("beat_id") or f"B{idx:02d}"
        out_png_9x16 = img_dir / f"{beat_id}_9x16.png"
        out_jpg_9x16 = img_dir / f"{beat_id}_9x16.jpg"
        out_png_16x9 = img_dir / f"{beat_id}_16x9.png"
        out_jpg_16x9 = img_dir / f"{beat_id}_16x9.jpg"

        if not (out_jpg_9x16.is_file() and out_jpg_9x16.stat().st_size > 10_000):
            tasks.append({
                "id": f"{channel_slug}_{beat_id}_9x16",
                "jobId": f"{beat_id}_9x16",
                "prompt": beat["prompt"],
                "ratio": "9:16",
                "aspect": "9:16",
                "model": "BELUGA",
                "filename": out_png_9x16.name,
                "out_dir": str(img_dir),
                "credit_cost": 1,
                "credit_reason": "image",
                "editorial_overlay": {"enabled": False},
            })
        if both_native and not (out_jpg_16x9.is_file() and out_jpg_16x9.stat().st_size > 10_000):
            tasks.append({
                "id": f"{channel_slug}_{beat_id}_16x9",
                "jobId": f"{beat_id}_16x9",
                "prompt": beat["prompt"],
                "ratio": "16:9",
                "aspect": "16:9",
                "model": "BELUGA",
                "filename": out_png_16x9.name,
                "out_dir": str(img_dir),
                "credit_cost": 1,
                "credit_reason": "image",
                "editorial_overlay": {"enabled": False},
            })

    if tasks:
        logger.info(
            f"[{channel_slug}] Submitting {len(tasks)} Flow CDP image tasks across "
            f"{len(candidate_profiles)} profiles (workers={max_workers}, OS-lock failover enabled)..."
        )
        pool = PersistentWorkerPool(
            target_workers=min(max_workers, len(candidate_profiles)),
            profiles=candidate_profiles,
            cooldown_seconds=30.0,
            pacing_seconds=2.5,
            stagger_seconds=1.0,
            headless=True,
            min_credits_required=1,
        )
        try:
            pool.start()
            for t in tasks:
                pool.submit_task(t)
            pool.wait_completion(timeout=900.0)
        finally:
            pool.shutdown()

    paths_9x16: List[Path] = []
    paths_16x9: List[Path] = []

    for idx, beat in enumerate(beats, 1):
        beat_id = beat.get("beat_id") or f"B{idx:02d}"
        png_9x16 = img_dir / f"{beat_id}_9x16.png"
        jpg_9x16 = img_dir / f"{beat_id}_9x16.jpg"
        png_16x9 = img_dir / f"{beat_id}_16x9.png"
        jpg_16x9 = img_dir / f"{beat_id}_16x9.jpg"

        if png_9x16.is_file() and not jpg_9x16.is_file():
            with Image.open(png_9x16) as im:
                im.convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS).save(jpg_9x16, "JPEG", quality=95)
        if png_16x9.is_file() and not jpg_16x9.is_file():
            with Image.open(png_16x9) as im:
                im.convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS).save(jpg_16x9, "JPEG", quality=95)

        # Cross-aspect fallback if one aspect finished and the other timed out
        if jpg_16x9.is_file() and not jpg_9x16.is_file():
            with Image.open(jpg_16x9) as im:
                w, h = im.size
                nw = int(round(h * 9.0 / 16.0))
                left = (w - nw) // 2
                im.crop((left, 0, left + nw, h)).resize((1080, 1920), Image.Resampling.LANCZOS).save(jpg_9x16, "JPEG", quality=95)
        if jpg_9x16.is_file() and not jpg_16x9.is_file():
            with Image.open(jpg_9x16) as im:
                w, h = im.size
                nh = int(round(w * 9.0 / 16.0))
                top = (h - nh) // 2
                im.crop((0, top, w, top + nh)).resize((1920, 1080), Image.Resampling.LANCZOS).save(jpg_16x9, "JPEG", quality=95)

        if jpg_9x16.is_file():
            paths_9x16.append(jpg_9x16)
        if jpg_16x9.is_file():
            paths_16x9.append(jpg_16x9)

    return {"9x16": paths_9x16, "16x9": paths_16x9}


def _camera_zoompan_expr(camera_motion: str, nb_frames: int, width: int, height: int, fps: int = 30) -> str:
    """Return FFmpeg zoompan filter string replicating the competitor's second-by-second camera movement."""
    motion = (camera_motion or "push_in").lower().strip()
    step = 0.08 / max(1, nb_frames)
    if motion in ("zoom_out", "pull_back", "pull_out"):
        return (
            f"zoompan=z='if(eq(on,1),1.08,max(1.0,zoom-{step:.6f}))':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
        )
    if motion in ("pan_right", "track_right"):
        return (
            f"zoompan=z='1.06':"
            f"x='(iw-iw/zoom)*(on/{max(1, nb_frames)})':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
        )
    if motion in ("pan_left", "track_left"):
        return (
            f"zoompan=z='1.06':"
            f"x='(iw-iw/zoom)*(1-on/{max(1, nb_frames)})':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
        )
    if motion in ("tilt_up", "pan_up", "rise"):
        return (
            f"zoompan=z='1.06':"
            f"x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{max(1, nb_frames)})':d=1:s={width}x{height}:fps={fps}"
        )
    if motion in ("tilt_down", "pan_down", "descend"):
        return (
            f"zoompan=z='1.06':"
            f"x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(on/{max(1, nb_frames)})':d=1:s={width}x{height}:fps={fps}"
        )
    # Default: smooth optical push-in (zoom_in / push_in)
    return (
        f"zoompan=z='min(zoom+{step:.6f},1.08)':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
    )


def render_vn_frame_video(
    frames: List[Path],
    beats: List[Dict[str, Any]],
    beat_durations: List[float],
    audio_path: Path,
    srt_path: Path,
    watermark_png: Path,
    out_mp4: Path,
    aspect: str = "9:16",
) -> Path:
    """Render MP4 adhering strictly to Vietnamese 9:16 / 16:9 frame layout & competitor motion grammar."""
    is_short = aspect == "9:16"
    width, height = (1080, 1920) if is_short else (1920, 1080)
    fps = 30
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    scratch = out_mp4.parent / f"_work_{aspect.replace(':', 'x')}"
    scratch.mkdir(parents=True, exist_ok=True)

    seg_files: List[Path] = []
    for idx, (frame_p, beat, dur) in enumerate(zip(frames, beats, beat_durations)):
        seg_mp4 = scratch / f"seg_{idx:02d}.mp4"
        nb_frames = max(1, int(round(dur * fps)))
        cam_motion = str(beat.get("camera_motion", "push_in"))
        zp = _camera_zoompan_expr(cam_motion, nb_frames, width, height, fps=fps)
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1,{zp},format=yuv420p"
        )
        cmd_seg = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", f"{dur:.4f}", "-r", str(fps),
            "-i", str(frame_p.resolve()),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-an",
            str(seg_mp4.resolve()),
        ]
        subprocess.run(cmd_seg, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        seg_files.append(seg_mp4)

    concat_txt = scratch / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in seg_files) + "\n", encoding="utf-8")

    # Vietnamese Frame Standard:
    # - 9:16: Burned-in White Arial Bold (FontSize=48, MarginV=400, Outline=3, Shadow=1) + 100x100 rounded logo at W-w-24:H-h-50
    # - 16:9: Sidecar .srt + 100x100 rounded logo at W-w-36:H-h-36
    escaped_srt = str(srt_path.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    filter_chains: List[str] = []
    cur_v = "0:v"

    if is_short:
        sub_filter = (
            f"subtitles=filename={escaped_srt}:"
            f"force_style='FontName=Arial,FontSize=48,Bold=1,PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,MarginV=400,Alignment=2,PlayResY={height},PlayResX={width}'"
        )
        filter_chains.append(f"[{cur_v}]{sub_filter}[vsub]")
        cur_v = "vsub"

    wm_pos = "W-w-24:H-h-50" if is_short else "W-w-36:H-h-36"
    filter_chains.append(f"[{cur_v}][1:v]overlay={wm_pos}[vout]")
    filter_chains.append(
        "[2:a]loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[aout]"
    )

    total_dur = sum(beat_durations)
    cmd_final = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt.resolve()),
        "-i", str(watermark_png.resolve()),
        "-i", str(audio_path.resolve()),
        "-filter_complex", ";".join(filter_chains),
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", f"{total_dur:.3f}",
        "-movflags", "+faststart",
        str(out_mp4.resolve()),
    ]
    subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    shutil.copy2(srt_path, out_mp4.with_suffix(".srt"))
    shutil.rmtree(scratch, ignore_errors=True)
    return out_mp4


def build_pilot_from_spec(
    spec_path: Path,
    profile_names: Optional[List[str]] = None,
    max_workers: int = 3,
) -> Dict[str, Any]:
    """Execute full pilot build (Flow images + Audio + 9:16 & 16:9 VN-frame MP4s + 1-FPS proof frames)."""
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    channel_slug = spec["channel_slug"]
    target_cfg = COMPETITOR_VIDEO_TARGETS.get(channel_slug, {})
    voice = spec.get("voice") or target_cfg.get("voice", "en-US-ChristopherNeural")
    beats = spec["beats"]

    pilot_dir = REBUILT_PILOTS_DIR / channel_slug
    pilot_dir.mkdir(parents=True, exist_ok=True)
    img_dir = pilot_dir / "images"
    audio_dir = pilot_dir / "audio"

    # 1. Audio synthesis & LUFS normalization
    full_narration = " ".join(str(b.get("narration", "")).strip() for b in beats if b.get("narration"))
    norm_wav, total_dur = synthesize_and_normalize_audio(full_narration, voice, audio_dir)
    srt_path = audio_dir / "subtitles.srt"
    beat_durations = build_vietnamese_standard_srt(beats, total_dur, srt_path)

    # 2. Flow CDP image generation (9:16 and 16:9)
    images_map = generate_flow_images_for_spec(
        channel_slug=channel_slug,
        beats=beats,
        img_dir=img_dir,
        profile_names=profile_names,
        max_workers=max_workers,
    )

    if len(images_map["9x16"]) < len(beats) or len(images_map["16x9"]) < len(beats):
        raise RuntimeError(
            f"[{channel_slug}] Incomplete Flow image generation: "
            f"9x16={len(images_map['9x16'])}/{len(beats)}, 16x9={len(images_map['16x9'])}/{len(beats)}"
        )

    # 3. Watermark preparation
    wm_png = pilot_dir / "watermark_100x100.png"
    make_channel_watermark(channel_slug, wm_png, size=100)

    # 4. Render 9:16 and 16:9 deliverables in both pilot_dir and video/
    mp4_9x16 = pilot_dir / f"{channel_slug}-pilot-9x16.mp4"
    mp4_16x9 = pilot_dir / f"{channel_slug}-pilot-16x9.mp4"

    render_vn_frame_video(
        frames=images_map["9x16"],
        beats=beats,
        beat_durations=beat_durations,
        audio_path=norm_wav,
        srt_path=srt_path,
        watermark_png=wm_png,
        out_mp4=mp4_9x16,
        aspect="9:16",
    )
    render_vn_frame_video(
        frames=images_map["16x9"],
        beats=beats,
        beat_durations=beat_durations,
        audio_path=norm_wav,
        srt_path=srt_path,
        watermark_png=wm_png,
        out_mp4=mp4_16x9,
        aspect="16:9",
    )

    # Copy to canonical video/<channel>-test-20s-9x16/ and video/<channel>-pilot-16x9/
    vid_short_dir = ROOT_DIR / f"video/{channel_slug}-test-20s-9x16"
    vid_short_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mp4_9x16, vid_short_dir / f"{channel_slug}-test-20s-9x16.mp4")
    shutil.copy2(srt_path, vid_short_dir / "subtitles.srt")

    vid_long_dir = ROOT_DIR / f"video/{channel_slug}-pilot-16x9"
    vid_long_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mp4_16x9, vid_long_dir / f"{channel_slug}-pilot-16x9.mp4")
    shutil.copy2(srt_path, vid_long_dir / "subtitles.srt")

    # 5. Extract 1-FPS verification frames from the rendered 9:16 pilot
    verify_dir = pilot_dir / "rendered_frames_9x16"
    verify_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", str(mp4_9x16), "-vf", "fps=1", "-q:v", "2",
        str(verify_dir / "pilot_frame_%02ds.jpg"),
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    report = {
        "channel_slug": channel_slug,
        "status": "SUCCESS",
        "duration_sec": round(total_dur, 2),
        "beats_count": len(beats),
        "mp4_9x16": str(mp4_9x16),
        "mp4_16x9": str(mp4_16x9),
        "canonical_short_mp4": str(vid_short_dir / f"{channel_slug}-test-20s-9x16.mp4"),
        "canonical_long_mp4": str(vid_long_dir / f"{channel_slug}-pilot-16x9.mp4"),
        "rendered_frames_dir": str(verify_dir),
    }
    (pilot_dir / "pilot_build_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info(f"[✓] [{channel_slug}] Built 9:16 & 16:9 Pilot Videos ({total_dur:.2f}s) -> {mp4_9x16}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Competitor 1-FPS frame extractor & VN-frame pilot rebuilder.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ext = sub.add_parser("extract-competitor", help="Download competitor video & extract 20 1-FPS frames")
    p_ext.add_argument("--channel", required=True, help="Channel slug, e.g. en-first-principles")
    p_ext.add_argument("--query", default=None, help="Optional custom yt-dlp search query or URL")
    p_ext.add_argument("--start-sec", type=int, default=None, help="Start second in competitor video")
    p_ext.add_argument("--duration-sec", type=int, default=20, help="Duration in seconds (default: 20)")

    p_bld = sub.add_parser("build-pilot", help="Build 9:16 & 16:9 pilot videos from rebuilt spec JSON")
    p_bld.add_argument("--spec", required=True, help="Path to <channel>_rebuilt_spec.json")
    p_bld.add_argument("--profiles", default=None, help="Comma-separated Flow profile names")
    p_bld.add_argument("--workers", type=int, default=3, help="Max concurrent Flow workers")

    args = parser.parse_args()
    if args.cmd == "extract-competitor":
        res = extract_competitor_frames(
            channel_slug=args.channel,
            custom_query=args.query,
            start_sec=args.start_sec,
            duration_sec=args.duration_sec,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "build-pilot":
        profs = [x.strip() for x in args.profiles.split(",") if x.strip()] if args.profiles else None
        res = build_pilot_from_spec(
            spec_path=Path(args.spec),
            profile_names=profs,
            max_workers=args.workers,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
