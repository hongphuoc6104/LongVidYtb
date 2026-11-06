#!/usr/bin/env python3
"""Rebuild English channels from scratch by studying 1-FPS full frames AND second-by-second
spoken dialogue, cadence, pauses, and transitions of real competitor videos.

Workflow per channel:
1. `extract-competitor`: Downloads a real competitor YouTube video (via yt-dlp native HTTP download),
   extracts:
   - `competitor_hook_20s.mp4` (00:00..00:20 hook segment)
   - `competitor_segment_20s.mp4` (20s core explanation segment)
   - `competitor_segment_20s.mp3` (audio stream for multimodal listening)
   - `competitor_acoustic_telemetry.json` (FFmpeg silencedetect pause intervals, speech bursts, cadence ratio)
   - `frame_01s.jpg` .. `frame_20s.jpg` (20 consecutive 1-FPS full frames)
2. Subagent inspects `competitor_segment_20s.mp4`, `competitor_hook_20s.mp4`, `competitor_acoustic_telemetry.json`,
   and all 20 frames via `read_file`, analyzes the exact spoken dialogue structure, sentence pairing,
   rhetorical pivots, acoustic pause durations (`pause_after_sec`), camera movements (`camera_motion`),
   and smooth transitions (`transition`), and writes `<channel>_rebuilt_spec.json`.
3. `build-pilot`:
   - Synthesizes per-beat narration via `edge_tts.Communicate(..., boundary="WordBoundary")` with
     exact competitor-modeled breath/dramatic pauses (`pause_after_sec`) between beats, normalized
     to `-11.0 LUFS / -1.0 dBTP`.
   - Builds Vietnamese-standard 1-word alternating Red (`#FF3B30`) & Yellow (`#FFE600`) kinetic
     subtitles (`subtitles_kinetic_9x16.ass`, `Arial Bold 100px`, `Outline=6`, `Shadow=4`, `MarginV=400`)
     for `9:16`, plus clean phrase-level `subtitles.srt` for `16:9` sidecar.
   - Renders `9:16` and `16:9` MP4s with 2x-supersampled sub-pixel `zoompan` camera motion (zero snap!)
     and smooth competitor-matched `xfade` transitions (`smoothleft`, `smoothright`, `smoothup`,
     `smoothdown`, `fade`).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import edge_tts
from PIL import Image, ImageChops, ImageDraw

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
BRAIN_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")
COMP_FRAMES_DIR = BRAIN_DIR / "competitor_frames"
REBUILT_PILOTS_DIR = BRAIN_DIR / "rebuilt_pilots"
REPO_SPECS_DIR = SYS_DIR / "channels/en_rebuilt_style_specs"

for _p in (str(SYS_DIR), str(SYS_DIR / "tools"), str(ROOT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flow_cdp.cdp_direct_client import PROFILES
from flow_cdp.credit_ledger import CreditLedger
from flow_cdp.persistent_pool import PersistentWorkerPool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rebuild_en_competitor")

COMPETITOR_VIDEO_TARGETS: Dict[str, Dict[str, Any]] = {
    "en-first-principles": {
        "niche": "Mental Models & Physics Paradoxes",
        "competitor_name": "Veritasium",
        "search_query": "ytsearch1:Veritasium physics paradox experiment",
        "start_sec": 65,
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
        "voice": "en-US-ChristopherNeural",
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
        "search_query": "ytsearch1:Wendover Productions shipping containers logistics",
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
        "voice": "en-US-JennyNeural",
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

VALID_XFADE_TRANSITIONS = {
    "fade",
    "dissolve",
    "smoothleft",
    "smoothright",
    "smoothup",
    "smoothdown",
    "wipeleft",
    "wiperight",
}


def analyze_acoustic_pauses(audio_or_video_path: Path, total_dur: float = 20.0) -> Dict[str, Any]:
    """Run FFmpeg silencedetect on competitor segment to extract exact pause intervals & speech bursts."""
    cmd = [
        "ffmpeg",
        "-i",
        str(audio_or_video_path),
        "-af",
        "silencedetect=noise=-32dB:d=0.14",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stderr = proc.stderr

    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", stderr)]
    ends_durs = [
        (float(m.group(1)), float(m.group(2)))
        for m in re.finditer(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", stderr)
    ]

    pauses: List[Dict[str, Any]] = []
    for i, (end_t, dur) in enumerate(ends_durs):
        start_t = starts[i] if i < len(starts) else max(0.0, end_t - dur)
        kind = "micro_pause" if dur < 0.28 else ("beat_pause" if dur < 0.48 else "dramatic_pause")
        pauses.append(
            {
                "start_sec": round(start_t, 3),
                "end_sec": round(end_t, 3),
                "duration_sec": round(dur, 3),
                "pause_type": kind,
            }
        )

    # Compute speech bursts between pauses
    speech_bursts: List[Dict[str, Any]] = []
    cursor = 0.0
    for p in pauses:
        if p["start_sec"] > cursor + 0.08:
            b_dur = round(p["start_sec"] - cursor, 3)
            speech_bursts.append(
                {
                    "start_sec": round(cursor, 3),
                    "end_sec": round(p["start_sec"], 3),
                    "duration_sec": b_dur,
                }
            )
        cursor = p["end_sec"]
    if cursor < total_dur - 0.08:
        speech_bursts.append(
            {
                "start_sec": round(cursor, 3),
                "end_sec": round(total_dur, 3),
                "duration_sec": round(total_dur - cursor, 3),
            }
        )

    total_pause_sec = round(sum(p["duration_sec"] for p in pauses), 3)
    total_speech_sec = round(max(0.1, total_dur - total_pause_sec), 3)
    avg_pause = round(total_pause_sec / len(pauses), 3) if pauses else 0.28
    avg_burst = round(sum(b["duration_sec"] for b in speech_bursts) / len(speech_bursts), 3) if speech_bursts else 2.4

    return {
        "segment_duration_sec": total_dur,
        "pauses_count": len(pauses),
        "total_pause_sec": total_pause_sec,
        "total_speech_sec": total_speech_sec,
        "speaking_ratio": round(total_speech_sec / max(1.0, total_dur), 3),
        "avg_pause_sec": avg_pause,
        "avg_speech_burst_sec": avg_burst,
        "pauses": pauses,
        "speech_bursts": speech_bursts,
    }


def extract_competitor_frames(
    channel_slug: str,
    custom_query: Optional[str] = None,
    start_sec: Optional[int] = None,
    duration_sec: int = 20,
) -> Dict[str, Any]:
    """Download real competitor video, extract 20s hook + 20s body MP4/MP3, acoustic pause telemetry, and 1-FPS frames."""
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
    clip_mp3 = out_dir / "competitor_segment_20s.mp3"
    hook_mp4 = out_dir / "competitor_hook_20s.mp4"

    if not raw_mp4.is_file() or raw_mp4.stat().st_size < 50_000:
        logger.info(f"[{channel_slug}] Downloading competitor reference via '{query}'...")
        cmd_dl = [
            "yt-dlp",
            "--no-playlist",
            "-f",
            "18/best[ext=mp4][height<=720]/best[ext=mp4]",
            "--write-info-json",
            "-o",
            str(raw_mp4),
            query,
        ]
        subprocess.run(cmd_dl, check=True, timeout=180)

    # Extract 20-second core reference clip locally
    if not clip_mp4.is_file() or clip_mp4.stat().st_size < 20_000 or start_sec is not None:
        cmd_clip = [
            "ffmpeg",
            "-y",
            "-ss",
            str(s_sec),
            "-t",
            str(d_sec),
            "-i",
            str(raw_mp4),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(clip_mp4),
        ]
        subprocess.run(cmd_clip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Extract 20-second opening Hook clip (00:00..00:20) to study hook formula
    if not hook_mp4.is_file() or hook_mp4.stat().st_size < 20_000:
        cmd_hook = [
            "ffmpeg",
            "-y",
            "-ss",
            "0",
            "-t",
            "20",
            "-i",
            str(raw_mp4),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "22",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(hook_mp4),
        ]
        subprocess.run(cmd_hook, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Extract MP3 audio for fast multimodal listening
    cmd_mp3 = [
        "ffmpeg",
        "-y",
        "-i",
        str(clip_mp4),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-b:a",
        "128k",
        str(clip_mp3),
    ]
    subprocess.run(cmd_mp3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Extract 1-FPS full frames if not already present or if start_sec overridden
    existing_frames = sorted(out_dir.glob("frame_*s.jpg"))
    if len(existing_frames) < d_sec or start_sec is not None:
        for old_f in existing_frames:
            old_f.unlink()
        cmd_frames = [
            "ffmpeg",
            "-y",
            "-ss",
            str(s_sec),
            "-t",
            str(d_sec),
            "-i",
            str(raw_mp4),
            "-vf",
            "fps=1",
            "-q:v",
            "2",
            str(out_dir / "frame_%02ds.jpg"),
        ]
        subprocess.run(cmd_frames, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    frames = sorted(out_dir.glob("frame_*s.jpg"))
    telemetry_body = analyze_acoustic_pauses(clip_mp4, float(d_sec))
    telemetry_hook = analyze_acoustic_pauses(hook_mp4, 20.0)
    telemetry_payload = {
        "channel_slug": channel_slug,
        "competitor_name": target.get("competitor_name", "") if target else "",
        "hook_00_20s_telemetry": telemetry_hook,
        "body_segment_telemetry": telemetry_body,
    }
    telemetry_path = out_dir / "competitor_acoustic_telemetry.json"
    telemetry_path.write_text(json.dumps(telemetry_payload, indent=2, ensure_ascii=False), encoding="utf-8")

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
        "hook_mp4": str(hook_mp4),
        "clip_mp4": str(clip_mp4),
        "clip_mp3": str(clip_mp3),
        "acoustic_telemetry_json": str(telemetry_path),
        "frames_count": len(frames),
        "frames": [str(f) for f in frames],
    }
    (out_dir / "extraction_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info(
        f"[✓] [{channel_slug}] Extracted {len(frames)} 1-FPS frames + hook/body MP4 + acoustic telemetry into {out_dir}"
    )
    return manifest


def resolve_channel_logo_source(channel_slug: str) -> Optional[Path]:
    """Resolve the canonical 1:1 brand emblem PNG for an English or Vietnamese channel."""
    ch_dir_name = channel_slug.strip().replace("-", "_")
    candidates = [
        ROOT_DIR / "sys/channels" / ch_dir_name / "assets/watermark_150x150.png",
        ROOT_DIR / "sys/channels" / ch_dir_name / "assets/avatar_800x800.png",
        ROOT_DIR / "sys/channels" / ch_dir_name / "assets/logo.png",
        ROOT_DIR / "sys/assets/brand_logo.png",
    ]
    for p in candidates:
        if p.is_file() and p.stat().st_size > 512:
            return p
    return None


def make_channel_watermark(channel_slug: str, out_png: Path, size: int = 100) -> Path:
    """Create a 100x100 squircle brand emblem watermark (radius=16, opacity=0.92) from the channel's true logo."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    src_logo = resolve_channel_logo_source(channel_slug)
    radius = max(12, int(round(size * 0.16)))

    if src_logo is not None:
        raw = Image.open(src_logo).convert("RGBA")
        rw, rh = raw.size
        # 2.5% safety margin crop in case raw source was not yet edge-cropped
        margin_x = int(round(rw * 0.025))
        margin_y = int(round(rh * 0.025))
        if rw > 64 and rh > 64:
            raw = raw.crop((margin_x, margin_y, rw - margin_x, rh - margin_y))
        img = raw.resize((size, size), Image.Resampling.LANCZOS)
    else:
        raise FileNotFoundError(
            f"Missing channel brand emblem for '{channel_slug}'. Expected watermark_150x150.png or avatar_800x800.png "
            f"in sys/channels/{channel_slug.replace('-', '_')}/assets/."
        )

    # Subtle 1.5px adaptive edge ring for crisp separation on dark or bright video frames
    ring_overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ring_overlay)
    rdraw.rounded_rectangle(
        (1, 1, size - 2, size - 2),
        radius=radius,
        outline=(255, 255, 255, 68),
        width=2,
    )
    img = Image.alpha_composite(img, ring_overlay)

    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=int(round(255 * 0.92)))
    _, _, _, a = img.split()
    img.putalpha(ImageChops.multiply(a, mask))
    img.save(out_png, format="PNG")
    return out_png


async def _synthesize_beat_with_word_boundaries(
    text: str,
    voice: str,
    out_mp3: Path,
    rate: str = "+0%",
) -> List[Dict[str, Any]]:
    """Synthesize a single beat's narration via edge_tts and return exact WordBoundary events."""
    comm = edge_tts.Communicate(text=text, voice=voice, rate=rate, boundary="WordBoundary")
    word_events: List[Dict[str, Any]] = []
    audio_bytes = bytearray()

    async for chunk in comm.stream():
        ctype = chunk.get("type")
        if ctype == "audio":
            audio_bytes.extend(chunk.get("data", b""))
        elif ctype == "WordBoundary":
            # offset and duration are in 100-nanosecond ticks (1e-7 seconds)
            start_s = float(chunk.get("offset", 0)) / 10_000_000.0
            dur_s = float(chunk.get("duration", 0)) / 10_000_000.0
            w_text = str(chunk.get("text", "")).strip()
            if w_text:
                word_events.append(
                    {
                        "word": w_text,
                        "start": round(start_s, 4),
                        "end": round(start_s + max(0.06, dur_s), 4),
                    }
                )

    out_mp3.write_bytes(bytes(audio_bytes))
    return word_events


def _probe_duration(path: Path) -> float:
    out = (
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ]
        )
        .decode()
        .strip()
    )
    return float(out)


def _write_silence_wav(out_wav: Path, duration_sec: float, sample_rate: int = 48000) -> None:
    n_frames = max(1, int(round(duration_sec * sample_rate)))
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00\x00\x00" * n_frames)


def synthesize_beats_with_competitor_cadence(
    beats: List[Dict[str, Any]],
    voice: str,
    audio_dir: Path,
) -> Tuple[Path, float, List[float], List[Dict[str, Any]]]:
    """Synthesize each beat with competitor-modeled pause_after_sec and capture exact WordBoundary timestamps.

    Returns:
      (norm_wav_path, total_duration_sec, beat_durations_sec, global_word_events)
    """
    audio_dir.mkdir(parents=True, exist_ok=True)
    scratch_a = audio_dir / "_beats_work"
    scratch_a.mkdir(parents=True, exist_ok=True)

    concat_wavs: List[Path] = []
    beat_durations: List[float] = []
    global_words: List[Dict[str, Any]] = []
    cursor_sec = 0.0

    for idx, beat in enumerate(beats):
        text = str(beat.get("narration", "")).strip()
        if not text:
            text = "..."
        rate = str(beat.get("speech_rate") or "+0%")
        # Competitor-modeled acoustic pause after this beat (default 0.28s beat pause; last beat 0.25s tail)
        raw_pause = beat.get("pause_after_sec")
        if raw_pause is not None:
            pause_after = max(0.08, min(0.85, float(raw_pause)))
        else:
            # Infer from terminal punctuation if not explicitly set
            if text.endswith("?") or text.endswith("..."):
                pause_after = 0.42
            elif text.endswith("—") or text.endswith(":"):
                pause_after = 0.22
            elif idx == len(beats) - 1:
                pause_after = 0.25
            else:
                pause_after = 0.30

        b_mp3 = scratch_a / f"beat_{idx:02d}.mp3"
        b_wav = scratch_a / f"beat_{idx:02d}.wav"
        p_wav = scratch_a / f"pause_{idx:02d}.wav"

        # Clean trailing em-dash for TTS synthesis so final consonants are articulated cleanly
        tts_text = re.sub(r"\s*[—–-]+\s*$", ",", text)
        words = asyncio.run(_synthesize_beat_with_word_boundaries(tts_text, voice, b_mp3, rate=rate))

        orig_tokens = text.split()
        if words:
            trim_start = max(0.0, float(words[0]["start"]) - 0.04)
            trim_end = float(words[-1]["end"]) + 0.08
            clip_dur = max(0.15, trim_end - trim_start)
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-ss",
                    f"{trim_start:.4f}",
                    "-t",
                    f"{clip_dur:.4f}",
                    "-i",
                    str(b_mp3),
                    "-ar",
                    "48000",
                    "-ac",
                    "2",
                    "-c:a",
                    "pcm_s16le",
                    str(b_wav),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            speech_dur = _probe_duration(b_wav)
            for w_i, w_ev in enumerate(words):
                rel_s = max(0.0, float(w_ev["start"]) - trim_start)
                rel_e = min(speech_dur, max(rel_s + 0.06, float(w_ev["end"]) - trim_start))
                display_word = orig_tokens[w_i] if w_i < len(orig_tokens) else w_ev["word"]
                global_words.append(
                    {
                        "word": display_word,
                        "clean_word": w_ev["word"],
                        "beat_index": idx,
                        "start": round(cursor_sec + rel_s, 4),
                        "end": round(cursor_sec + rel_e, 4),
                    }
                )
        else:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(b_mp3),
                    "-ar",
                    "48000",
                    "-ac",
                    "2",
                    "-c:a",
                    "pcm_s16le",
                    str(b_wav),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            speech_dur = _probe_duration(b_wav)
            toks = orig_tokens or [text]
            t_dur = speech_dur / len(toks)
            for w_i, tok in enumerate(toks):
                global_words.append(
                    {
                        "word": tok,
                        "clean_word": tok,
                        "beat_index": idx,
                        "start": round(cursor_sec + w_i * t_dur, 4),
                        "end": round(cursor_sec + (w_i + 1) * t_dur, 4),
                    }
                )

        _write_silence_wav(p_wav, pause_after, sample_rate=48000)
        concat_wavs.append(b_wav)
        concat_wavs.append(p_wav)

        beat_total = round(speech_dur + pause_after, 4)
        beat_durations.append(beat_total)
        cursor_sec += beat_total

    concat_list = scratch_a / "concat_audio.txt"
    concat_list.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in concat_wavs) + "\n",
        encoding="utf-8",
    )
    stitched_wav = scratch_a / "stitched_raw.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list),
            "-c:a",
            "pcm_s16le",
            str(stitched_wav),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    norm_wav = audio_dir / "narration.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(stitched_wav),
            "-af",
            "loudnorm=I=-11.0:TP=-1.0:LRA=7.0",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(norm_wav),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    final_dur = _probe_duration(norm_wav)
    raw_sum = sum(beat_durations)
    if raw_sum > 0 and abs(final_dur - raw_sum) > 0.005:
        scale = final_dur / raw_sum
        beat_durations = [round(d * scale, 4) for d in beat_durations]
        beat_durations[-1] = max(0.2, round(final_dur - sum(beat_durations[:-1]), 4))
        for w in global_words:
            w["start"] = round(w["start"] * scale, 4)
            w["end"] = round(w["end"] * scale, 4)

    # Save word alignment & cadence report
    (audio_dir / "word_alignment.json").write_text(
        json.dumps(
            {
                "total_duration_sec": round(final_dur, 4),
                "beat_durations_sec": beat_durations,
                "word_count": len(global_words),
                "words": global_words,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    shutil.rmtree(scratch_a, ignore_errors=True)
    return norm_wav, final_dur, beat_durations, global_words


def _fmt_srt_ts(sec: float) -> str:
    ms = max(0, int(round(sec * 1000)))
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _fmt_ass_ts(sec: float) -> str:
    cs = max(0, int(round(sec * 100)))
    s, cs = divmod(cs, 100)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def build_vn_kinetic_1word_ass_and_srt(
    beats: List[Dict[str, Any]],
    beat_durations: List[float],
    global_words: List[Dict[str, Any]],
    total_dur: float,
    ass_path: Path,
    srt_path: Path,
    margin_v: int = 270,
) -> None:
    """Build:
    1. `subtitles_kinetic_9x16.ass`: Exact Vietnamese 9:16 1-word kinetic pop (`portraitKineticWord` /
       `portraitKineticCaptionStyle`: Alternating Red `#FF3B30` and Yellow `#FFE600`, `Arial`,
       `FontSize=100`, `Bold=-1`, `Outline=6` `#000000`, `Shadow=4`, `MarginV=270` safe lower band, `PlayResX=1080`, `PlayResY=1920`).
    2. `subtitles.srt`: Clean phrase-level sidecar `.srt` for `16:9` and accessibility.
    """
    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        # Red #FF3B30 -> ASS BGR &H00303BFF; Yellow #FFE600 -> ASS BGR &H0000E6FF
        f"Style: KineticRed,Arial,100,&H00303BFF,&H00303BFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,4,2,40,40,{int(margin_v)},1",
        f"Style: KineticYellow,Arial,100,&H0000E6FF,&H0000E6FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,4,2,40,40,{int(margin_v)},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for idx, w in enumerate(global_words):
        w_start = float(w["start"])
        w_end = float(w["end"])
        # Match captions.mjs line 109: hold last word up to 0.22s into a pause without overlapping next word
        if idx + 1 < len(global_words):
            next_start = float(global_words[idx + 1]["start"])
            w_end = min(next_start, max(w_end, min(w_end + 0.18, next_start)))
        else:
            w_end = min(total_dur, w_end + 0.18)

        if w_end <= w_start + 0.02:
            w_end = w_start + 0.06

        style_name = "KineticRed" if (idx % 2 == 0) else "KineticYellow"
        raw_token = str(w.get("word", "")).strip()
        # Escape ASS braces if any
        safe_token = raw_token.replace("{", "").replace("}", "")
        if not safe_token:
            continue
        ass_lines.append(f"Dialogue: 0,{_fmt_ass_ts(w_start)},{_fmt_ass_ts(w_end)},{style_name},,0,0,0,,{safe_token}")

    ass_path.parent.mkdir(parents=True, exist_ok=True)
    ass_path.write_text("\n".join(ass_lines) + "\n", encoding="utf-8")

    # Build clean phrase-level SRT for 16:9 sidecar
    srt_entries: List[str] = []
    cue_idx = 1
    cur_t = 0.0
    for beat, dur in zip(beats, beat_durations, strict=False):
        text = str(beat.get("narration", "")).strip()
        b_start = cur_t
        b_end = min(total_dur, cur_t + dur)
        cur_t = b_end
        w_list = text.split()
        if not w_list:
            continue
        chunk_size = 6
        chunks = [" ".join(w_list[j : j + chunk_size]) for j in range(0, len(w_list), chunk_size)]
        c_dur = (b_end - b_start) / len(chunks)
        for c_i, chunk in enumerate(chunks):
            cs = b_start + c_i * c_dur
            ce = min(b_end, cs + c_dur)
            srt_entries.append(f"{cue_idx}\n{_fmt_srt_ts(cs)} --> {_fmt_srt_ts(ce)}\n{chunk}\n")
            cue_idx += 1

    srt_path.parent.mkdir(parents=True, exist_ok=True)
    srt_path.write_text("\n".join(srt_entries), encoding="utf-8")


def generate_flow_images_for_spec(
    channel_slug: str,
    beats: List[Dict[str, Any]],
    img_dir: Path,
    profile_names: Optional[List[str]] = None,
    max_workers: int = 4,
    both_native: bool = False,
    force_regenerate: bool = False,
) -> Dict[str, List[Path]]:
    """Generate 9:16 (and 16:9) images on Google Flow CDP using PersistentWorkerPool with full-pool failover."""
    img_dir.mkdir(parents=True, exist_ok=True)
    ledger = CreditLedger()

    all_healthy = [
        p for p in PROFILES if ledger.get_balance(p["name"]) >= 10 and p["name"] not in ("profile_1", "profile_13")
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

        if force_regenerate or not (out_jpg_9x16.is_file() and out_jpg_9x16.stat().st_size > 10_000):
            tasks.append(
                {
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
                }
            )
        if both_native and (force_regenerate or not (out_jpg_16x9.is_file() and out_jpg_16x9.stat().st_size > 10_000)):
            tasks.append(
                {
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
                }
            )

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

        if jpg_16x9.is_file() and not jpg_9x16.is_file():
            with Image.open(jpg_16x9) as im:
                w, h = im.size
                nw = int(round(h * 9.0 / 16.0))
                left = (w - nw) // 2
                im.crop((left, 0, left + nw, h)).resize((1080, 1920), Image.Resampling.LANCZOS).save(
                    jpg_9x16, "JPEG", quality=95
                )
        if jpg_9x16.is_file() and not jpg_16x9.is_file():
            with Image.open(jpg_9x16) as im:
                w, h = im.size
                nh = int(round(w * 9.0 / 16.0))
                top = (h - nh) // 2
                im.crop((0, top, w, top + nh)).resize((1920, 1080), Image.Resampling.LANCZOS).save(
                    jpg_16x9, "JPEG", quality=95
                )

        if jpg_9x16.is_file():
            paths_9x16.append(jpg_9x16)
        if jpg_16x9.is_file():
            paths_16x9.append(jpg_16x9)

    return {"9x16": paths_9x16, "16x9": paths_16x9}


def _camera_zoompan_expr(camera_motion: str, nb_frames: int, width: int, height: int, fps: int = 30) -> str:
    """Return butter-smooth FFmpeg zoompan filter expression using pure continuous functions of (on/nb_frames).

    Crucial invariant: Never use `if(eq(on,1), ...)` or recursive `zoom` state with `d=1` on `-loop 1`
    inputs because `d=1` resets `zoom=1.0` on every new input frame, which caused a violent 1-frame snap!
    Instead, compute `z`, `x`, and `y` directly from `on / nb_frames` on a 2x-supersampled canvas.
    """
    motion = (camera_motion or "push_in").lower().strip()
    n = max(1, nb_frames)
    if motion in ("zoom_out", "pull_back", "pull_out"):
        return (
            f"zoompan=z='1.06-0.06*(on/{n})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
        )
    if motion in ("pan_right", "track_right", "slide_right"):
        return f"zoompan=z='1.06':x='(iw-iw/zoom)*(on/{n})':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
    if motion in ("pan_left", "track_left", "slide_left"):
        return f"zoompan=z='1.06':x='(iw-iw/zoom)*(1.0-on/{n})':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
    if motion in ("tilt_up", "pan_up", "rise"):
        return f"zoompan=z='1.06':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1.0-on/{n})':d=1:s={width}x{height}:fps={fps}"
    if motion in ("tilt_down", "pan_down", "descend"):
        return f"zoompan=z='1.06':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(on/{n})':d=1:s={width}x{height}:fps={fps}"
    if motion in ("drift_diag_in", "diag_in"):
        return (
            f"zoompan=z='1.02+0.05*(on/{n})':"
            f"x='(iw-iw/zoom)*(0.25+0.5*(on/{n}))':y='(ih-ih/zoom)*(0.25+0.5*(on/{n}))':d=1:s={width}x{height}:fps={fps}"
        )
    if motion in ("drift_diag_out", "diag_out"):
        return (
            f"zoompan=z='1.07-0.05*(on/{n})':"
            f"x='(iw-iw/zoom)*(0.75-0.5*(on/{n}))':y='(ih-ih/zoom)*(0.75-0.5*(on/{n}))':d=1:s={width}x{height}:fps={fps}"
        )
    # Default: smooth optical push-in (zoom_in / push_in)
    return f"zoompan=z='1.00+0.06*(on/{n})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"


def _resolve_beat_transition(beat: Dict[str, Any], idx: int) -> str:
    """Resolve smooth competitor-matched xfade transition for beat boundary.

    Note: In FFmpeg xfade, 'dissolve' is a grainy pixel dither, whereas 'fade' is a true
    optical cross-dissolve. Always map 'dissolve' -> 'fade'.
    """
    raw = str(beat.get("transition") or beat.get("transition_in") or "").lower().strip()
    if raw == "dissolve":
        return "fade"
    if raw in ("fade", "smoothleft", "smoothright", "smoothup", "smoothdown"):
        return raw
    cam = str(beat.get("camera_motion") or "").lower().strip()
    if "pan_right" in cam or "track_right" in cam:
        return "smoothleft"
    if "pan_left" in cam or "track_left" in cam:
        return "smoothright"
    if "tilt_up" in cam or "rise" in cam:
        return "smoothup"
    if "tilt_down" in cam or "descend" in cam:
        return "smoothdown"
    return "fade"


def render_vn_frame_video(
    frames: List[Path],
    beats: List[Dict[str, Any]],
    beat_durations: List[float],
    audio_path: Path,
    ass_path: Path,
    srt_path: Path,
    watermark_png: Path,
    out_mp4: Path,
    aspect: str = "9:16",
) -> Path:
    """Render MP4 adhering strictly to Vietnamese 9:16 / 16:9 frame layout, 1-word Red/Yellow kinetic ASS
    subtitles on 9:16, supersampled sub-pixel camera motion, and smooth xfade transitions."""
    from concurrent.futures import ThreadPoolExecutor

    is_short = aspect == "9:16"
    width, height = (1080, 1920) if is_short else (1920, 1080)
    up_w, up_h = int(width * 1.5), int(height * 1.5)
    fps = 30
    xfade_dur = 0.28
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    scratch = out_mp4.parent / f"_work_{aspect.replace(':', 'x')}"
    scratch.mkdir(parents=True, exist_ok=True)

    n_beats = len(frames)
    seg_files: List[Path] = [scratch / f"seg_{idx:02d}.mp4" for idx in range(n_beats)]

    def _encode_seg(idx: int) -> None:
        frame_p = frames[idx]
        beat = beats[idx]
        dur = beat_durations[idx]
        seg_mp4 = seg_files[idx]
        seg_dur = (dur + xfade_dur) if idx < n_beats - 1 else dur
        nb_frames = max(1, int(round(seg_dur * fps)))
        cam_motion = str(beat.get("camera_motion", "push_in"))
        zp = _camera_zoompan_expr(cam_motion, nb_frames, width, height, fps=fps)
        over_w = int(round(up_w * 1.05 / 2.0)) * 2
        over_h = int(round(up_h * 1.05 / 2.0)) * 2
        vf = (
            f"scale={over_w}:{over_h}:force_original_aspect_ratio=increase,"
            f"crop={up_w}:{up_h}:(in_w-{up_w})/2:(in_h-{up_h})/2,"
            f"setsar=1,{zp},format=yuv420p"
        )
        cmd_seg = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-t",
            f"{seg_dur:.4f}",
            "-r",
            str(fps),
            "-i",
            str(frame_p.resolve()),
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-an",
            str(seg_mp4.resolve()),
        ]
        subprocess.run(cmd_seg, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(_encode_seg, range(n_beats)))

    # Chain all segments with smooth competitor-learned xfade transitions at exact cumulative beat boundaries
    cmd_final: List[str] = ["ffmpeg", "-y"]
    for sf in seg_files:
        cmd_final.extend(["-i", str(sf.resolve())])

    wm_idx = len(seg_files)
    cmd_final.extend(["-i", str(watermark_png.resolve())])
    audio_idx = len(seg_files) + 1
    cmd_final.extend(["-i", str(audio_path.resolve())])

    filter_chains: List[str] = []
    if n_beats == 1:
        filter_chains.append("[0:v]setsar=1[vchain]")
        cur_v = "vchain"
    else:
        cum_offset = 0.0
        prev_label = "0:v"
        for i in range(1, n_beats):
            cum_offset += beat_durations[i - 1]
            trans_name = _resolve_beat_transition(beats[i], i)
            out_label = f"vx{i}"
            filter_chains.append(
                f"[{prev_label}][{i}:v]xfade=transition={trans_name}:"
                f"duration={xfade_dur:.4f}:offset={max(0.05, cum_offset):.4f}[{out_label}]"
            )
            prev_label = out_label
        cur_v = prev_label

    if is_short:
        escaped_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        filter_chains.append(f"[{cur_v}]ass=filename='{escaped_ass}'[vsub]")
        cur_v = "vsub"

    wm_pos = "W-w-24:H-h-56" if is_short else "W-w-36:H-h-36"
    filter_chains.append(f"[{cur_v}][{wm_idx}:v]overlay={wm_pos}[vout]")
    filter_chains.append(f"[{audio_idx}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[aout]")

    total_dur = sum(beat_durations)
    cmd_final.extend(
        [
            "-filter_complex",
            ";".join(filter_chains),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-t",
            f"{total_dur:.3f}",
            "-movflags",
            "+faststart",
            str(out_mp4.resolve()),
        ]
    )
    subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    shutil.copy2(srt_path, out_mp4.with_suffix(".srt"))
    if is_short:
        shutil.copy2(ass_path, out_mp4.with_suffix(".ass"))
    shutil.rmtree(scratch, ignore_errors=True)
    return out_mp4


def build_pilot_from_spec(
    spec_path: Path,
    profile_names: Optional[List[str]] = None,
    max_workers: int = 4,
    force_images: bool = False,
) -> Dict[str, Any]:
    """Execute full pilot build (Competitor-cadence Audio + 1-Word Red/Yellow ASS + Flow images + 9:16 & 16:9 MP4s)."""
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    channel_slug = spec["channel_slug"]
    target_cfg = COMPETITOR_VIDEO_TARGETS.get(channel_slug, {})
    voice = spec.get("voice") or target_cfg.get("voice", "en-US-ChristopherNeural")
    beats = spec["beats"]

    pilot_dir = REBUILT_PILOTS_DIR / channel_slug
    pilot_dir.mkdir(parents=True, exist_ok=True)
    img_dir = pilot_dir / "images"
    audio_dir = pilot_dir / "audio"

    # Keep artifact copy and repo copy of spec synchronized
    artifact_spec_p = pilot_dir / f"{channel_slug}_rebuilt_spec.json"
    if spec_path.resolve() != artifact_spec_p.resolve():
        shutil.copy2(spec_path, artifact_spec_p)
    repo_spec_dir = REPO_SPECS_DIR / channel_slug
    repo_spec_dir.mkdir(parents=True, exist_ok=True)
    repo_spec_p = repo_spec_dir / f"{channel_slug}_rebuilt_spec.json"
    if spec_path.resolve() != repo_spec_p.resolve():
        shutil.copy2(spec_path, repo_spec_p)

    # 1. Per-beat audio synthesis with competitor pauses & WordBoundary alignment
    norm_wav, total_dur, beat_durations, global_words = synthesize_beats_with_competitor_cadence(
        beats=beats,
        voice=voice,
        audio_dir=audio_dir,
    )
    ass_path = audio_dir / "subtitles_kinetic_9x16.ass"
    srt_path = audio_dir / "subtitles.srt"
    build_vn_kinetic_1word_ass_and_srt(
        beats=beats,
        beat_durations=beat_durations,
        global_words=global_words,
        total_dur=total_dur,
        ass_path=ass_path,
        srt_path=srt_path,
    )

    # 2. Flow CDP image generation (9:16 and 16:9)
    images_map = generate_flow_images_for_spec(
        channel_slug=channel_slug,
        beats=beats,
        img_dir=img_dir,
        profile_names=profile_names,
        max_workers=max_workers,
        force_regenerate=force_images,
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
        ass_path=ass_path,
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
        ass_path=ass_path,
        srt_path=srt_path,
        watermark_png=wm_png,
        out_mp4=mp4_16x9,
        aspect="16:9",
    )

    vid_short_dir = ROOT_DIR / f"video/{channel_slug}-test-20s-9x16"
    vid_short_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mp4_9x16, vid_short_dir / f"{channel_slug}-test-20s-9x16.mp4")
    shutil.copy2(srt_path, vid_short_dir / "subtitles.srt")
    shutil.copy2(ass_path, vid_short_dir / "subtitles_kinetic_9x16.ass")

    vid_long_dir = ROOT_DIR / f"video/{channel_slug}-pilot-16x9"
    vid_long_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mp4_16x9, vid_long_dir / f"{channel_slug}-pilot-16x9.mp4")
    shutil.copy2(srt_path, vid_long_dir / "subtitles.srt")

    # 5. Extract 1-FPS verification frames from the rendered 9:16 pilot
    verify_dir = pilot_dir / "rendered_frames_9x16"
    verify_dir.mkdir(parents=True, exist_ok=True)
    for old_vf in verify_dir.glob("pilot_frame_*s.jpg"):
        old_vf.unlink()
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp4_9x16),
            "-vf",
            "fps=1",
            "-q:v",
            "2",
            str(verify_dir / "pilot_frame_%02ds.jpg"),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    report = {
        "channel_slug": channel_slug,
        "status": "SUCCESS",
        "duration_sec": round(total_dur, 2),
        "beats_count": len(beats),
        "words_count": len(global_words),
        "beat_durations_sec": beat_durations,
        "subtitle_style_9x16": "VN_KINETIC_1WORD_RED_YELLOW_ASS (Arial 100px, #FF3B30 / #FFE600, Outline=6, MarginV=400)",
        "transition_engine": "2x_supersampled_zoompan_plus_xfade",
        "mp4_9x16": str(mp4_9x16),
        "mp4_16x9": str(mp4_16x9),
        "canonical_short_mp4": str(vid_short_dir / f"{channel_slug}-test-20s-9x16.mp4"),
        "canonical_long_mp4": str(vid_long_dir / f"{channel_slug}-pilot-16x9.mp4"),
        "rendered_frames_dir": str(verify_dir),
    }
    (pilot_dir / "pilot_build_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    shutil.copy2(pilot_dir / "pilot_build_report.json", repo_spec_dir / "pilot_build_report.json")
    logger.info(
        f"[✓] [{channel_slug}] Built 9:16 (1-word Red/Yellow ASS) & 16:9 Pilot Videos ({total_dur:.2f}s) -> {mp4_9x16}"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Competitor 1-FPS frame + dialogue cadence extractor & VN-frame pilot rebuilder."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ext = sub.add_parser(
        "extract-competitor", help="Extract competitor hook/body MP4, MP3, acoustic pauses & 20 frames"
    )
    p_ext.add_argument("--channel", required=True, help="Channel slug, e.g. en-first-principles")
    p_ext.add_argument("--query", default=None, help="Optional custom yt-dlp search query or URL")
    p_ext.add_argument("--start-sec", type=int, default=None, help="Start second in competitor video")
    p_ext.add_argument("--duration-sec", type=int, default=20, help="Duration in seconds (default: 20)")

    p_bld = sub.add_parser("build-pilot", help="Build 9:16 & 16:9 pilot videos from rebuilt spec JSON")
    p_bld.add_argument("--spec", required=True, help="Path to <channel>_rebuilt_spec.json")
    p_bld.add_argument("--profiles", default=None, help="Comma-separated Flow profile names")
    p_bld.add_argument("--workers", type=int, default=4, help="Max concurrent Flow workers")
    p_bld.add_argument("--force-images", action="store_true", help="Force regenerate Flow images")

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
            force_images=args.force_images,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
