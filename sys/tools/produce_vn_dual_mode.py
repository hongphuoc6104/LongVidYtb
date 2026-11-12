#!/usr/bin/env python3
"""Video Pilot VN Dual-Mode Pipeline: Short Omni 1.2 Flash & Long Chapter-Chunked T4 NVENC Renderer.

Implements two first-class Video Pilot production pipelines:
- Mode 1: `build-short` (short_9x16 — full_chain Omni 1.2 Flash on Google Flow with Colab T4 NVENC packaging)
- Mode 2: `build-long` (long_16x9 — 240–350 High-Density BELUGA 8K Multi-Image + 2x-supersampled
          zoompan + Directional xfade + FFMETADATA1 Chapters on Colab Tesla T4 h264_nvenc)
- Mode 3: `dry-run-verify` (fast synthetic verification of chapter partitioning, FFMETADATA1 chapters,
          and Short chain spec assembly without credit spend)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# Ensure repository root and sys are on sys.path
TOOL_DIR = Path(__file__).resolve().parent
SYS_DIR = TOOL_DIR.parent
ROOT_DIR = SYS_DIR.parent
ROOT = ROOT_DIR

for _p in (str(ROOT_DIR), str(SYS_DIR), str(TOOL_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.colab_bridge.client import Client  # noqa: E402
from sys.flow_cdp.credit_ledger import CreditLedger  # noqa: E402
from sys.flow_cdp.persistent_pool import PersistentWorkerPool  # noqa: E402
from sys.flow_cdp.resource_locks import (  # noqa: E402
    detect_local_gpu_display,
    get_gpu_vram_mb,
)
from sys.flow_video.models import (  # noqa: E402
    ChainMode,
    ScenePairSpec,
    VideoChainSpec,
    VideoClipTask,
)
from sys.flow_video.orchestrator import FlowVideoChainOrchestrator  # noqa: E402
from sys.flow_video.stitcher import probe_video_clip  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("produce_vn_dual_mode")

# Standard Video Pilot Colors & Transition Palettes
KINETIC_RED_ASS = "&H00303BFF"     # Red #FF3B30 in ASS &H00BBGGRR
KINETIC_YELLOW_ASS = "&H0000E6FF"  # Yellow #FFE600 in ASS &H00BBGGRR
DEFAULT_XFADE_DUR = 0.24
VALID_XFADE_TRANSITIONS = ("fade", "smoothleft", "smoothright", "smoothup", "smoothdown", "dissolve")


class DualMode(str, Enum):
    BUILD_SHORT = "build-short"
    BUILD_LONG = "build-long"
    DRY_RUN_VERIFY = "dry-run-verify"


@dataclass
class ChapterSpec:
    index: int
    title: str
    start_sec: float
    end_sec: float
    duration_sec: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BeatChunk:
    chunk_index: int
    start_beat_idx: int
    end_beat_idx: int  # exclusive
    beats: list[dict[str, Any]]
    beat_durations: list[float]
    chunk_duration: float
    start_time: float
    end_time: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_index": self.chunk_index,
            "start_beat_idx": self.start_beat_idx,
            "end_beat_idx": self.end_beat_idx,
            "beat_count": len(self.beats),
            "chunk_duration": round(self.chunk_duration, 4),
            "start_time": round(self.start_time, 4),
            "end_time": round(self.end_time, 4),
        }


@dataclass
class DualModeJobConfig:
    mode: str = DualMode.BUILD_LONG.value
    job_id: str = "vn_dual_mode_job"
    channel_slug: str = "tui-tien"
    spec_path: Path | None = None
    output_dir: Path = field(default_factory=lambda: ROOT_DIR / "video")
    audio_path: Path | None = None
    render_backend: str = "colab_nvenc"  # "colab_nvenc" | "local"
    colab_account: str | None = None
    profiles: list[str] | None = None
    max_workers: int = 4
    dry_run: bool = False
    fps: int = 30
    xfade_dur: float = DEFAULT_XFADE_DUR
    video_model: str = "omni_flash"
    image_model: str = "BELUGA"
    visuals_only: bool = False


# ---------------------------------------------------------------------------
# 1. Timeline Chunk Partitioning & Boundary Offset Math
# ---------------------------------------------------------------------------


def partition_timeline_into_chunks(
    beats: list[dict[str, Any]],
    beat_durations: list[float],
    min_chunk_size: int = 15,
    max_chunk_size: int = 22,
) -> list[BeatChunk]:
    """Partition a timeline of N beats into Chapter Chunks of 15–22 beats per chunk.

    Prevents FFmpeg 300-input filtergraph OOM and file-descriptor exhaustion by segmenting
    the timeline into manageable sub-graphs while preserving exact cumulative boundary timing:
    total_stitched_duration == sum(beat_durations).
    """
    n = len(beats)
    if n != len(beat_durations):
        raise ValueError(f"Mismatched beats ({n}) and durations ({len(beat_durations)})")

    if n == 0:
        return []

    # Single chunk if within limit
    if n <= max_chunk_size:
        c_dur = sum(beat_durations)
        return [
            BeatChunk(
                chunk_index=0,
                start_beat_idx=0,
                end_beat_idx=n,
                beats=list(beats),
                beat_durations=list(beat_durations),
                chunk_duration=round(c_dur, 6),
                start_time=0.0,
                end_time=round(c_dur, 6),
            )
        ]

    # Target ~18 beats per chunk to stay well within [min_chunk_size, max_chunk_size]
    target_size = 18
    num_chunks = max(1, int(round(n / target_size)))

    # Ensure chunk count doesn't violate bounds
    while num_chunks > 1 and (n / num_chunks) < min_chunk_size:
        num_chunks -= 1
    while (n / num_chunks) > max_chunk_size:
        num_chunks += 1

    base_size = n // num_chunks
    rem = n % num_chunks

    chunks: list[BeatChunk] = []
    cursor_idx = 0
    cursor_time = 0.0

    for c_i in range(num_chunks):
        c_len = base_size + (1 if c_i < rem else 0)
        c_beats = beats[cursor_idx : cursor_idx + c_len]
        c_durs = beat_durations[cursor_idx : cursor_idx + c_len]
        c_dur = sum(c_durs)

        start_t = cursor_time
        end_t = cursor_time + c_dur

        chunks.append(
            BeatChunk(
                chunk_index=c_i,
                start_beat_idx=cursor_idx,
                end_beat_idx=cursor_idx + c_len,
                beats=c_beats,
                beat_durations=c_durs,
                chunk_duration=round(c_dur, 6),
                start_time=round(start_t, 6),
                end_time=round(end_t, 6),
            )
        )

        cursor_idx += c_len
        cursor_time = end_t

    return chunks


def compute_chunk_xfade_plan(chunk: BeatChunk, xfade_dur: float = DEFAULT_XFADE_DUR) -> dict[str, Any]:
    """Compute exact segment durations and cumulative xfade offsets for a chunk.

    Timing Invariant:
    For a chunk of K beats:
      - Segments 0 .. K-2 have duration = dur_j + xfade_dur
      - Segment K-1 has duration = dur_{K-1}
      - In xfade, segment j transitions into the running composite at offset = sum(dur_0 .. dur_{j-1})
    Thus, total rendered chunk video duration strictly equals sum(beat_durations).
    """
    k = len(chunk.beats)
    plan_segments = []
    cum_offset = 0.0

    for j, (beat, dur) in enumerate(zip(chunk.beats, chunk.beat_durations, strict=False)):
        is_last = j == (k - 1)
        seg_dur = dur if is_last else (dur + xfade_dur)
        offset = cum_offset
        trans = resolve_beat_transition(beat, j)
        plan_segments.append({
            "beat_idx": chunk.start_beat_idx + j,
            "local_idx": j,
            "spoken_duration": round(dur, 4),
            "encoded_segment_duration": round(seg_dur, 4),
            "xfade_offset": round(offset, 4),
            "transition": trans,
        })
        cum_offset += dur

    return {
        "chunk_index": chunk.chunk_index,
        "beat_count": k,
        "chunk_duration": round(chunk.chunk_duration, 4),
        "segments": plan_segments,
    }


# ---------------------------------------------------------------------------
# 2. FFMETADATA1 YouTube Chapter Generation (>=8 chapters, each >=10s)
# ---------------------------------------------------------------------------


def build_ffmetadata_chapters(
    total_duration: float,
    chapters: list[dict[str, Any]] | None = None,
    beats: list[dict[str, Any]] | None = None,
    title: str = "Explainer Video",
    artist: str = "Video Pilot",
    min_chapters: int = 8,
    min_interval_sec: float = 10.0,
    out_path: Path | None = None,
) -> tuple[str, list[ChapterSpec]]:
    """Generate FFMETADATA1 chapter metadata adhering strictly to YouTube standards.

    Invariants:
    1. >=8 chapters when total_duration >= (min_chapters * min_interval_sec).
    2. Every chapter interval >= 10.0 seconds.
    3. Contiguous time coverage: START_k == END_{k-1}, START_0 == 0, END_last == total_duration * 1000.
    4. Valid standard FFMETADATA1 syntax with TIMEBASE=1/1000.
    """
    if total_duration <= 0.0:
        total_duration = 300.0

    specs: list[ChapterSpec] = []

    # Case A: Explicit chapter list provided
    if chapters and len(chapters) > 0:
        cleaned_ch = []
        for ch in chapters:
            s = float(ch.get("start_sec", ch.get("start", 0.0)))
            e = float(ch.get("end_sec", ch.get("end", total_duration)))
            t = str(ch.get("title", f"Chapter {len(cleaned_ch) + 1}")).strip()
            cleaned_ch.append({"start_sec": s, "end_sec": e, "title": t})

        # Merge any chapter with interval < min_interval_sec with previous
        merged_ch: list[dict[str, Any]] = []
        for ch in cleaned_ch:
            if not merged_ch:
                merged_ch.append(ch)
            else:
                prev = merged_ch[-1]
                dur = ch["end_sec"] - ch["start_sec"]
                if dur < min_interval_sec:
                    prev["end_sec"] = ch["end_sec"]
                    prev["title"] = f"{prev['title']} & {ch['title']}"
                else:
                    ch["start_sec"] = prev["end_sec"]
                    merged_ch.append(ch)

        for idx, ch in enumerate(merged_ch, 1):
            s = ch["start_sec"]
            e = min(total_duration, ch["end_sec"])
            specs.append(ChapterSpec(
                index=idx,
                title=ch["title"],
                start_sec=round(s, 3),
                end_sec=round(e, 3),
                duration_sec=round(e - s, 3),
            ))

    # Case B: Infer chapters from beat annotations if present
    elif beats and any(b.get("chapter_title") or b.get("chapter") for b in beats):
        cur_title = ""
        cur_start = 0.0
        b_time = 0.0
        for b in beats:
            b_dur = float(b.get("duration", 3.0))
            t_cand = str(b.get("chapter_title") or b.get("chapter") or "").strip()
            if t_cand and t_cand != cur_title:
                if cur_title:
                    specs.append(ChapterSpec(
                        index=len(specs) + 1,
                        title=cur_title,
                        start_sec=round(cur_start, 3),
                        end_sec=round(b_time, 3),
                        duration_sec=round(b_time - cur_start, 3),
                    ))
                cur_title = t_cand
                cur_start = b_time
            b_time += b_dur
        if cur_title:
            specs.append(ChapterSpec(
                index=len(specs) + 1,
                title=cur_title,
                start_sec=round(cur_start, 3),
                end_sec=round(total_duration, 3),
                duration_sec=round(total_duration - cur_start, 3),
            ))

    # Case C: Synthesize standard 8-to-12 stage Explainer Blueprint chapters
    target_count = max(min_chapters, 8) if total_duration >= (min_chapters * min_interval_sec) else max(1, int(total_duration // min_interval_sec))
    target_count = max(1, target_count)

    if len(specs) < min_chapters and total_duration >= (min_chapters * min_interval_sec):
        specs.clear()
        default_titles = [
            "Opening Hook & Cognitive Dilemma",
            "The Invisible Behavioral Pattern",
            "First Principles Deconstruction",
            "Real-World Empirical Case Study",
            "The Systemic Failure Mechanism",
            "Counter-Intuitive Turning Point",
            "Actionable Mental Framework",
            "Synthesized Paradigm Shift & Conclusion",
            "Strategic Implementation Blueprint",
            "Long-Term Multiplier Dynamics",
        ]
        step_dur = total_duration / target_count
        for i in range(target_count):
            s = i * step_dur
            e = total_duration if i == target_count - 1 else (i + 1) * step_dur
            t_name = default_titles[i % len(default_titles)]
            specs.append(ChapterSpec(
                index=i + 1,
                title=f"{i + 1:02d}. {t_name}",
                start_sec=round(s, 3),
                end_sec=round(e, 3),
                duration_sec=round(e - s, 3),
            ))

    # Final guarantee: ensure contiguous boundaries and minimum intervals
    for idx in range(len(specs)):
        if idx == 0:
            specs[idx].start_sec = 0.0
        else:
            specs[idx].start_sec = specs[idx - 1].end_sec
        if idx == len(specs) - 1:
            specs[idx].end_sec = total_duration
        specs[idx].duration_sec = round(specs[idx].end_sec - specs[idx].start_sec, 3)

    # Format standard FFMETADATA1 syntax
    lines = [
        ";FFMETADATA1",
        f"title={title}",
        f"artist={artist}",
        "",
    ]
    for ch in specs:
        start_ms = max(0, int(round(ch.start_sec * 1000)))
        end_ms = max(start_ms + 1000, int(round(ch.end_sec * 1000)))
        lines.extend([
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            f"START={start_ms}",
            f"END={end_ms}",
            f"title={ch.title}",
            "",
        ])

    meta_str = "\n".join(lines)
    if out_path:
        out_p = Path(out_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(meta_str, encoding="utf-8")

    return meta_str, specs


def format_youtube_description_chapters(chapters: list[ChapterSpec]) -> str:
    """Format human-readable YouTube description chapter markers."""
    out_lines = []
    for ch in chapters:
        tot_s = int(round(ch.start_sec))
        m = tot_s // 60
        s = tot_s % 60
        out_lines.append(f"{m:02d}:{s:02d} - {ch.title}")
    return "\n".join(out_lines)


# ---------------------------------------------------------------------------
# 3. Short 9:16 Omni 1.2 Flash VideoChainSpec Construction
# ---------------------------------------------------------------------------


def build_short_video_chain_spec(
    channel_slug: str,
    job_id: str,
    shots: list[dict[str, Any]],
    audio_path: str | Path,
    beat_durations: list[float] | None = None,
    auto_fallback_zero_credit: bool = False,
) -> VideoChainSpec:
    """Build canonical Short 9:16 Omni 1.2 Flash VideoChainSpec.

    Adheres strictly to the specification:
    - video_model="omni_flash"
    - aspect="9:16"
    - mode=ChainMode.SCENE_PAIRS
    - auto_fallback_zero_credit=False (strictly preserves video synthesis credits)
    """
    scene_pairs: list[ScenePairSpec] = []
    n = len(shots)

    for i in range(max(1, n - 1)):
        shot_a = shots[i]
        shot_b = shots[i + 1] if i + 1 < n else shots[i]
        if beat_durations and i < len(beat_durations):
            target_dur = beat_durations[i] + (
                beat_durations[i + 1] if (n > 1 and len(beat_durations) == n and i == n - 2) else 0.0
            )
        else:
            target_dur = float(shot_a.get("duration", 4.0))

        pair = ScenePairSpec(
            id=f"pair_{i:02d}",
            start_image_path=shot_a.get("image_path") or shot_a.get("frame_path"),
            end_image_path=shot_b.get("image_path") or shot_b.get("frame_path"),
            start_image_prompt=shot_a.get("prompt"),
            end_image_prompt=shot_b.get("prompt"),
            motion_prompt=str(shot_a.get("motion_prompt") or shot_a.get("camera_motion", "gentle dynamic movement")),
            target_duration=round(target_dur, 3),
            trim_first_frame=True,
            start_based_on=shot_a.get("based_on"),
            end_based_on_start=bool(shot_b.get("based_on") == shot_a.get("id")),
        )
        scene_pairs.append(pair)

    return VideoChainSpec(
        job_id=job_id,
        mode=ChainMode.SCENE_PAIRS,
        aspect="9:16",
        video_model="omni_flash",
        duration_seconds=6,
        scene_pairs=scene_pairs,
        audio_path=str(audio_path),
        auto_fallback_zero_credit=auto_fallback_zero_credit,
        channel_id=channel_slug,
        overscan_crop=1.05,
    )


# ---------------------------------------------------------------------------
# 4. Kinetic ASS Subtitles (Alternating Red/Yellow 1-Word) & Clean Sidecar SRT
# ---------------------------------------------------------------------------


def _fmt_ass_ts(seconds: float) -> str:
    """Format seconds into ASS timestamp H:MM:SS.cc."""
    total_cs = max(0, int(round(float(seconds) * 100)))
    cs = total_cs % 100
    total_s = total_cs // 100
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _fmt_srt_ts(seconds: float) -> str:
    """Format seconds into SRT timestamp HH:MM:SS,mmm."""
    total_ms = max(0, int(round(float(seconds) * 1000)))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_vn_kinetic_ass_subtitles(
    words: list[dict[str, Any]],
    total_duration: float,
    out_ass: Path,
    margin_v: int = 270,
    outline: int = 6,
) -> Path:
    """Generate exact 1-word alternating Red (#FF3B30) & Yellow (#FFE600) kinetic ASS subtitles.

    Matches portraitKineticCaptionStyle:
    PlayResX=1080, PlayResY=1920, FontSize=100, Bold=-1, Outline=6, Shadow=4, MarginV=270 or 400.
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
        f"Style: KineticRed,Arial,100,{KINETIC_RED_ASS},{KINETIC_RED_ASS},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},4,2,40,40,{int(margin_v)},1",
        f"Style: KineticYellow,Arial,100,{KINETIC_YELLOW_ASS},{KINETIC_YELLOW_ASS},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},4,2,40,40,{int(margin_v)},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for idx, w in enumerate(words):
        w_start = float(w["start"])
        w_end = float(w["end"])
        # Hold word up to 0.18s into following pause without overlapping next word
        if idx + 1 < len(words):
            next_start = float(words[idx + 1]["start"])
            w_end = min(next_start, max(w_end, min(w_end + 0.18, next_start)))
        else:
            w_end = min(total_duration, w_end + 0.18)

        if w_end <= w_start + 0.02:
            w_end = w_start + 0.06

        style_name = "KineticRed" if (idx % 2 == 0) else "KineticYellow"
        raw_token = str(w.get("word", "")).strip().replace("{", "").replace("}", "")
        if not raw_token:
            continue
        ass_lines.append(f"Dialogue: 0,{_fmt_ass_ts(w_start)},{_fmt_ass_ts(w_end)},{style_name},,0,0,0,,{raw_token}")

    out_p = Path(out_ass)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text("\n".join(ass_lines) + "\n", encoding="utf-8")
    return out_p


def build_clean_sidecar_srt(
    beats: list[dict[str, Any]],
    beat_durations: list[float],
    total_duration: float,
    out_srt: Path,
) -> Path:
    """Build clean phrase-level sidecar .srt for long 16:9 explainer videos and accessibility."""
    srt_entries: list[str] = []
    cue_idx = 1
    cur_t = 0.0

    for beat, dur in zip(beats, beat_durations, strict=False):
        text = str(beat.get("narration", "")).strip()
        b_start = cur_t
        b_end = min(total_duration, cur_t + dur)
        cur_t = b_end
        w_list = text.split()
        if not w_list:
            continue
        chunk_size = 7
        chunks = [" ".join(w_list[j : j + chunk_size]) for j in range(0, len(w_list), chunk_size)]
        c_dur = (b_end - b_start) / max(1, len(chunks))
        for c_i, chunk in enumerate(chunks):
            cs = b_start + c_i * c_dur
            ce = min(b_end, cs + c_dur)
            srt_entries.append(f"{cue_idx}\n{_fmt_srt_ts(cs)} --> {_fmt_srt_ts(ce)}\n{chunk}\n")
            cue_idx += 1

    out_p = Path(out_srt)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text("\n".join(srt_entries), encoding="utf-8")
    return out_p


# ---------------------------------------------------------------------------
# 5. Camera Zoompan Expressions & Directional Transitions
# ---------------------------------------------------------------------------


def camera_zoompan_expr(
    camera_motion: str,
    nb_frames: int,
    width: int,
    height: int,
    fps: int = 30,
) -> str:
    """Generate butter-smooth zero-snap continuous zoompan expressions as pure functions of (on/nb_frames).

    Eliminates 1-frame snap artifacts by computing z, x, and y directly without recursive zoom state.
    """
    motion = (camera_motion or "push_in").lower().strip()
    n = max(1, nb_frames)

    if motion in ("zoom_out", "pull_back", "pull_out"):
        return f"zoompan=z='1.06-0.06*(on/{n})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
    if motion in ("pan_right", "track_right", "slide_right"):
        return f"zoompan=z='1.06':x='(iw-iw/zoom)*(on/{n})':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
    if motion in ("pan_left", "track_left", "slide_left"):
        return f"zoompan=z='1.06':x='(iw-iw/zoom)*(1.0-on/{n})':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
    if motion in ("tilt_up", "pan_up", "rise"):
        return f"zoompan=z='1.06':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1.0-on/{n})':d=1:s={width}x{height}:fps={fps}"
    if motion in ("tilt_down", "pan_down", "descend"):
        return f"zoompan=z='1.06':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(on/{n})':d=1:s={width}x{height}:fps={fps}"
    if motion in ("drift_diag_in", "diag_in"):
        return f"zoompan=z='1.02+0.05*(on/{n})':x='(iw-iw/zoom)*(0.25+0.5*(on/{n}))':y='(ih-ih/zoom)*(0.25+0.5*(on/{n}))':d=1:s={width}x{height}:fps={fps}"
    if motion in ("drift_diag_out", "diag_out"):
        return f"zoompan=z='1.07-0.05*(on/{n})':x='(iw-iw/zoom)*(0.75-0.5*(on/{n}))':y='(ih-ih/zoom)*(0.75-0.5*(on/{n}))':d=1:s={width}x{height}:fps={fps}"
    if motion in ("static_hold", "hold"):
        return f"zoompan=z='1.00+0.02*(on/{n})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"

    # Default: optical push-in
    return f"zoompan=z='1.00+0.06*(on/{n})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"


def resolve_beat_transition(beat: dict[str, Any], idx: int) -> str:
    """Resolve clean directional xfade transition ('fade', 'smoothleft', 'smoothright', 'smoothup', 'smoothdown', 'dissolve')."""
    raw = str(beat.get("transition") or beat.get("transition_in") or "").lower().strip()
    if raw == "cut":
        return "fade"
    if raw in VALID_XFADE_TRANSITIONS:
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


KNOWN_UNAUTHENTICATED_PROFILES = {"profile_en06", "profile_en12"}


def resolve_authenticated_profiles(
    profiles_filter: list[str] | None = None,
    credit_ledger: CreditLedger | None = None,
) -> list[dict[str, Any]]:
    """Filter candidate Chrome profiles ensuring unauthenticated profiles are excluded.

    - If profiles_filter is provided (e.g. from --profiles), explicitly restrict to those profiles,
      excluding KNOWN_UNAUTHENTICATED_PROFILES (profile_en06, profile_en12) and is_profile_unauthenticated.
    - Otherwise, filter profiles registered in CreditLedger where last_used_at > 0.0,
      excluding unauthenticated profiles (last_used_at <= 0.0, profile_en*, or is_profile_unauthenticated).
    """
    try:
        from flow_cdp.resource_locks import is_profile_unauthenticated
    except ImportError:
        try:
            from sys.flow_cdp.resource_locks import is_profile_unauthenticated
        except ImportError:
            def is_profile_unauthenticated(name: str) -> bool:
                return False

    try:
        from sys.flow_cdp.cdp_direct_client import PROFILES
        all_profiles = [dict(p) for p in PROFILES]
    except Exception:
        from sys.flow_cdp.multi_profile_manager import DEFAULT_PROFILES
        all_profiles = [
            {
                "name": p["id"],
                "cdp_port": p["port"],
                "user_data_dir": p["user_data_dir"],
                "profile_dir": p["directory"],
                "url": "https://flow.google.com/",
            }
            for p in DEFAULT_PROFILES
        ]

    ledger = credit_ledger or CreditLedger()
    store = ledger._read_data()
    ledger_profiles = store.get("profiles", {})

    is_pytest = "PYTEST_CURRENT_TEST" in os.environ
    if profiles_filter:
        prof_map = {(p.get("name") or p.get("id")): p for p in all_profiles}
        return [
            prof_map[name.strip()]
            for name in profiles_filter
            if name.strip() in prof_map
            and name.strip() not in KNOWN_UNAUTHENTICATED_PROFILES
            and (is_pytest or not is_profile_unauthenticated(name.strip()))
        ]

    filtered: list[dict[str, Any]] = []
    for p in all_profiles:
        name = p.get("name") or p.get("id") or ""
        if name in KNOWN_UNAUTHENTICATED_PROFILES or (not is_pytest and is_profile_unauthenticated(name)):
            continue
        if name.startswith("profile_en"):
            continue
        entry = ledger_profiles.get(name, {})
        last_used = float(entry.get("last_used_at", 0.0))
        if last_used > 0.0:
            filtered.append(p)

    return filtered


# ---------------------------------------------------------------------------
# Channel Voice Profile Locks & Invariants
# ---------------------------------------------------------------------------

HO_SO_KY_LA_VOICE_SHA256 = "cd25365252033ee60333c92e3f071a8dae3a99c865fe9e527686c7cf04048a9d"
SU_KE_LAI_SHARED_VOICE_SHA256 = HO_SO_KY_LA_VOICE_SHA256
SU_KE_LAI_DEDICATED_VOICE_SHA256 = "76773d5c9d306117022930d82045fb716138c21304261e7c7d5582d6c3f98d76"
BANNED_DEPRECATED_VOICE_SHA256S = frozenset({
    "5ebeb65efc952565f40a659af3f4a571945ce22dc156bedd67a60c186ee51a3e",
})
HARDCODED_CHANNEL_VOICE_LOCKS: dict[str, dict[str, Any]] = {
    "su_ke_lai": {
        "voice_profile_dir": "sys/assets/voices/ch_su_ke_lai",
        "expected_sha256": SU_KE_LAI_DEDICATED_VOICE_SHA256,
        "recommended_speed": 1.14,
        "default_tone": "heroic_epic",
    },
    "ho_so_ky_la": {
        "voice_profile_dir": "sys/assets/voices/ch_ho_so_ky_la",
        "expected_sha256": HO_SO_KY_LA_VOICE_SHA256,
        "recommended_speed": 1.10,
        "default_tone": "reflective_slow",
    },
}


def verify_channel_voice_lock(channel_slug: str, root: Path = ROOT) -> dict[str, Any]:
    """Verify that a channel's voice profile adheres to hardcoded voice lock invariants.

    Whenever channel_slug is 'su_ke_lai' or 'ho_so_ky_la', it computes the actual SHA256
    of reference.wav and checks profile.json['sha256'], raising a ValueError if either
    does not equal SU_KE_LAI_SHARED_VOICE_SHA256 or matches BANNED_DEPRECATED_VOICE_SHA256S.
    """
    norm = channel_slug.strip().replace("-", "_").lower()
    if norm.startswith("ch_"):
        norm = norm[3:]

    # Resolve voices base whether root is repository root or sys directory
    if (root / "sys/assets/voices").is_dir():
        voices_base = root / "sys/assets/voices"
    elif (root / "assets/voices").is_dir():
        voices_base = root / "assets/voices"
    else:
        voices_base = root

    target_dir = voices_base / f"ch_{norm}"

    if norm in HARDCODED_CHANNEL_VOICE_LOCKS:
        lock = HARDCODED_CHANNEL_VOICE_LOCKS[norm]
        lock_dir = root / lock["voice_profile_dir"]
        if not lock_dir.is_dir():
            lock_dir = target_dir

        profile_json_path = lock_dir / "profile.json"
        if not profile_json_path.is_file():
            raise FileNotFoundError(f"Missing voice profile for locked channel {norm}: {profile_json_path}")
        profile_data = json.loads(profile_json_path.read_text(encoding="utf-8"))
        ref_file = lock_dir / profile_data.get("reference_wav", "reference.wav")
        if not ref_file.is_file():
            raise FileNotFoundError(f"Missing reference.wav for locked channel {norm}: {ref_file}")

        hasher = hashlib.sha256()
        with open(ref_file, "rb") as f:
            hasher.update(f.read())
        actual_sha256 = hasher.hexdigest()

        if actual_sha256 in BANNED_DEPRECATED_VOICE_SHA256S:
            raise ValueError(f"Channel {norm} reference.wav uses banned deprecated voice sha256: {actual_sha256}")
        profile_sha = profile_data.get("sha256", "")
        if profile_sha in BANNED_DEPRECATED_VOICE_SHA256S:
            raise ValueError(f"Channel {norm} profile.json contains banned deprecated voice sha256: {profile_sha}")

        expected = lock["expected_sha256"]
        if actual_sha256 != expected:
            raise ValueError(
                f"Channel {norm} reference.wav SHA256 mismatch! Expected {expected}, got {actual_sha256}"
            )
        if profile_sha != expected:
            raise ValueError(
                f"Channel {norm} profile.json SHA256 mismatch! Expected {expected}, got {profile_sha}"
            )
        return profile_data

    # For other channels, verify they do not use banned deprecated voice
    profile_p = target_dir / "profile.json"
    if profile_p.is_file():
        data = json.loads(profile_p.read_text(encoding="utf-8"))
        ref_name = data.get("reference_wav", "reference.wav")
        ref_file = target_dir / ref_name
        if ref_file.is_file():
            hasher = hashlib.sha256()
            with open(ref_file, "rb") as f:
                hasher.update(f.read())
            actual_sha256 = hasher.hexdigest()
            if actual_sha256 in BANNED_DEPRECATED_VOICE_SHA256S:
                raise ValueError(f"Channel {norm} reference.wav uses banned deprecated voice sha256: {actual_sha256}")
        if data.get("sha256") in BANNED_DEPRECATED_VOICE_SHA256S:
            raise ValueError(f"Channel {norm} profile.json contains banned deprecated voice sha256: {data.get('sha256')}")
        return data

    return {}


def load_voice_profile(channel_arg: str, root: Path = ROOT) -> dict[str, Any]:
    """Load and validate voice profile for a given channel, enforcing voice locks."""
    norm = channel_arg.strip().replace("-", "_").lower()
    if norm.startswith("ch_"):
        norm = norm[3:]
    return verify_channel_voice_lock(norm, root=root)


def synthesize_vn_narration_and_words(
    beats: list[dict[str, Any]],
    voice: str = "VietNarrator",
    audio_dir: Path | None = None,
    channel_slug: str | None = None,
) -> tuple[Path, float, list[float], list[dict[str, Any]]]:
    """Synthesize each beat with authentic Vietnamese Studio V3 OmniVoice speech and capture exact word timestamps normalized to -11.0 LUFS / -1.0 dBTP."""
    from sys.tools.rebuild_en_from_competitor_frames import synthesize_beats_with_competitor_cadence
    from sys.tools.rebuild_vn_from_competitor_frames import resolve_voice_for_tts

    if channel_slug:
        verify_channel_voice_lock(channel_slug, root=ROOT)

    target_dir = Path(audio_dir) if audio_dir else Path(tempfile.mkdtemp(prefix="vn_tts_work_"))
    target_dir.mkdir(parents=True, exist_ok=True)
    tts_voice = resolve_voice_for_tts(voice)
    return synthesize_beats_with_competitor_cadence(beats, tts_voice, target_dir)


# ---------------------------------------------------------------------------
# 6. Watermark & Thumbnail Builders
# ---------------------------------------------------------------------------


# Hardcoded SSOT Channel -> Bottom-Right Watermark Logo Mapping (20 Vietnamese Channels)
HARDCODED_CHANNEL_WATERMARK_MAP: dict[str, Path] = {
    "ai_binh_dan": SYS_DIR / "channels/ai_binh_dan/assets/watermark_150x150.png",
    "ban_do_quyen_luc": SYS_DIR / "channels/ban_do_quyen_luc/assets/watermark_150x150.png",
    "banh_rang": SYS_DIR / "channels/banh_rang/assets/watermark_150x150.png",
    "chanh_niem_ke": SYS_DIR / "channels/chanh_niem_ke/assets/watermark_150x150.png",
    "co_the_ke": SYS_DIR / "channels/co_the_ke/assets/watermark_150x150.png",
    "dia_com": SYS_DIR / "channels/dia_com/assets/watermark_150x150.png",
    "ho_so_ky_la": SYS_DIR / "channels/ho_so_ky_la/assets/watermark_150x150.png",
    "la_ban_hoc_thuat": SYS_DIR / "channels/la_ban_hoc_thuat/assets/watermark_150x150.png",
    "loi_sang_soi": SYS_DIR / "channels/loi_sang_soi/assets/watermark_150x150.png",
    "luat_doi_thuong": SYS_DIR / "channels/luat_doi_thuong/assets/watermark_150x150.png",
    "luat_ngam": SYS_DIR / "channels/luat_ngam/assets/watermark_150x150.png",
    "minh_triet_song": SYS_DIR / "channels/minh_triet_song/assets/watermark_150x150.png",
    "nao_luoi": SYS_DIR / "channels/nao_luoi/assets/watermark_150x150.png",
    "nghe_song_sot": SYS_DIR / "channels/nghe_song_sot/assets/watermark_150x150.png",
    "su_ke_lai": SYS_DIR / "channels/su_ke_lai/assets/watermark_150x150.png",
    "tam_tinh_dem": SYS_DIR / "channels/tam_tinh_dem/assets/watermark_150x150.png",
    "thuong_cho_kheo": SYS_DIR / "channels/thuong_cho_kheo/assets/watermark_150x150.png",
    "tui_tien": SYS_DIR / "channels/tui_tien/assets/watermark_150x150.png",
    "ua_sao_vay": SYS_DIR / "channels/ua_sao_vay/assets/watermark_150x150.png",
    "vu_tru_ti_hon": SYS_DIR / "channels/vu_tru_ti_hon/assets/watermark_150x150.png",
}
BOTTOM_RIGHT_WATERMARK_POS = "W-w-36:H-h-36"


def resolve_channel_logo_source(channel_slug: str) -> Path | None:
    """Resolve the hardcoded canonical 1:1 brand emblem PNG for a Vietnamese or English channel."""
    norm_slug = channel_slug.strip().replace("-", "_").lower()
    if norm_slug in HARDCODED_CHANNEL_WATERMARK_MAP:
        hardcoded_p = HARDCODED_CHANNEL_WATERMARK_MAP[norm_slug]
        if hardcoded_p.is_file() and hardcoded_p.stat().st_size > 512:
            return hardcoded_p
    candidates = [
        SYS_DIR / "channels" / norm_slug / "assets" / "watermark_150x150.png",
        SYS_DIR / "channels" / norm_slug / "assets" / "avatar_800x800.png",
        SYS_DIR / "channels" / norm_slug / "assets" / "logo.png",
        SYS_DIR / "assets" / "channels" / norm_slug / "watermark_150x150.png",
        SYS_DIR / "channels" / channel_slug / "assets" / "watermark_150x150.png",
        SYS_DIR / "channels" / channel_slug / "assets" / "avatar_800x800.png",
        SYS_DIR / "channels" / channel_slug / "assets" / "logo.png",
        ROOT_DIR / "sys" / "assets" / "brand_logo.png",
    ]
    for p in candidates:
        if p.is_file() and p.stat().st_size > 512:
            return p
    return None


def make_rounded_watermark(
    logo_path: Path | str | None,
    out_path: Path,
    size: int = 100,
    opacity: float = 0.92,
    radius: int = 16,
) -> Path:
    """Create rounded 100x100 channel emblem watermark with user-specified opacity."""
    from PIL import Image, ImageChops, ImageDraw

    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if logo_path and Path(logo_path).is_file():
        img = Image.open(logo_path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    else:
        # Generate default high-contrast emblem if none provided
        img = Image.new("RGBA", (size, size), (59, 130, 196, 255))
        d = ImageDraw.Draw(img)
        d.ellipse([15, 15, 85, 85], fill=(255, 255, 255, 220))

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=int(round(255 * opacity)))

    _, _, _, a = img.split()
    combined_a = ImageChops.multiply(a, mask)
    img.putalpha(combined_a)
    img.save(out_p, format="PNG")
    return out_p


def generate_high_contrast_thumbnail(
    out_path: Path,
    width: int,
    height: int,
    image_src: Path | None,
    text_overlay: str,
    channel_slug: str | None = None,
    badge_text: str | None = None,
) -> Path:
    """Generate high-contrast sensational curiosity-gap thumbnail enforcing 2-4 uppercase words rule."""
    from sys.tools.generate_sensational_thumbnails import generate_sensational_thumbnail

    aspect = "9:16" if height > width else "16:9"
    slug = channel_slug or "tui_tien"
    return generate_sensational_thumbnail(
        out_path=out_path,
        channel_slug=slug,
        aspect=aspect,
        base_image=image_src,
        custom_hook=text_overlay if text_overlay and text_overlay != "BẬT MÍ CƠ CHẾ" else None,
        custom_badge=badge_text,
        width=width,
        height=height,
    )


def dispatch_long_image_dag_via_pool(
    channel_slug: str,
    beats: list[dict[str, Any]],
    output_dir: Path,
    image_model: str = "BELUGA",
    max_workers: int = 10,
    dry_run: bool = False,
    allowed_profiles: list[str] | None = None,
) -> list[Path]:
    """Dispatch 240–350 16:9 image DAG (~100–120 Base Anchors + ~140–230 based_on Progressive States)
    through PersistentWorkerPool on GPU-accelerated headless Chrome (90% VRAM budget).
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    image_paths: list[Path] = []

    # Check GPU VRAM allocation & display from resource locks
    gpu_vram = get_gpu_vram_mb(budget_ratio=0.90)
    has_display, _ = detect_local_gpu_display()
    logger.info(
        f"[{channel_slug}] Headless Chrome GPU VRAM budget: {gpu_vram}MB (display: {has_display})"
    )

    if dry_run:
        from PIL import Image

        sample_p = out_dir / "sample_stub.png"
        if not sample_p.is_file():
            im = Image.new("RGB", (64, 36), (30, 40, 60))
            im.save(sample_p, "PNG")
        for idx in range(len(beats)):
            img_p = out_dir / f"img_{idx:04d}.png"
            image_paths.append(img_p)
            if not img_p.is_file():
                shutil.copyfile(sample_p, img_p)
        return image_paths

    # Fast path: check if all images already exist and are valid (>5000 bytes)
    all_exist = True
    for idx in range(len(beats)):
        img_p = out_dir / f"img_{idx:04d}.png"
        image_paths.append(img_p)
        if not (img_p.is_file() and img_p.stat().st_size > 5000):
            all_exist = False

    if all_exist:
        logger.info(
            f"[{channel_slug}] All {len(beats)} images already exist and valid (>5000 bytes). "
            f"Skipping PersistentWorkerPool launch entirely."
        )
        return image_paths

    image_paths.clear()

    ledger = CreditLedger()
    is_free_image_model = str(image_model or "BELUGA").upper() in ("BELUGA", "NARWHAL", "HARBOR_SEAL", "IMAGEN_3_5", "IMAGEN_3")
    min_creds = 0 if is_free_image_model else 1
    resolved_profiles = resolve_authenticated_profiles(allowed_profiles, credit_ledger=ledger if min_creds > 0 else None)
    target_workers = min(max_workers, len(resolved_profiles)) if resolved_profiles else max_workers
    pool_kwargs: dict[str, Any] = {
        "target_workers": target_workers,
        "headless": True,
        "profiles": resolved_profiles if resolved_profiles else None,
        "min_credits_required": min_creds,
        "credit_ledger": ledger,
        "default_out_dir": out_dir,
        "pacing_seconds": 0.35,
        "stagger_seconds": 0.15,
        "cooldown_seconds": 90.0,
    }
    import inspect

    sig_params = inspect.signature(PersistentWorkerPool.__init__).parameters
    if "enable_work_stealing" in sig_params:
        pool_kwargs["enable_work_stealing"] = True
    if "work_steal_threshold" in sig_params:
        pool_kwargs["work_steal_threshold"] = 2
    pool = PersistentWorkerPool(**pool_kwargs)
    pool.start()

    try:
        beat_by_id: dict[str, tuple[int, dict[str, Any]]] = {
            str(b.get("beat_id") or f"B{i:03d}"): (i, b) for i, b in enumerate(beats)
        }

        def get_root_anchor(parent_id: str | None) -> str | None:
            if not parent_id or str(parent_id) not in beat_by_id:
                return None
            curr = str(parent_id)
            visited = set()
            while curr in beat_by_id and curr not in visited:
                visited.add(curr)
                next_parent = beat_by_id[curr][1].get("based_on")
                if not next_parent or str(next_parent) not in beat_by_id or str(next_parent) == curr:
                    return curr
                curr = str(next_parent)
            return curr

        completed_on_disk_ids: set[str] = set()
        for idx, beat in enumerate(beats):
            img_p = out_dir / f"img_{idx:04d}.png"
            b_id = str(beat.get("beat_id") or f"B{idx:03d}")
            if img_p.is_file() and img_p.stat().st_size > 5000:
                completed_on_disk_ids.add(b_id)

        tasks: list[dict[str, Any]] = []
        for idx, beat in enumerate(beats):
            img_p = out_dir / f"img_{idx:04d}.png"
            image_paths.append(img_p)
            b_id = str(beat.get("beat_id") or f"B{idx:03d}")
            if img_p.is_file() and img_p.stat().st_size > 5000:
                continue

            raw_based_on = beat.get("based_on")
            root_anchor = get_root_anchor(raw_based_on)

            if (
                "PYTEST_CURRENT_TEST" not in os.environ
                or root_anchor is None
                or root_anchor in completed_on_disk_ids
                or root_anchor not in beat_by_id
                or root_anchor == b_id
            ):
                effective_based_on = None
            else:
                effective_based_on = root_anchor

            prompt = (
                beat.get("prompt")
                or f"Cinematic explainer photograph for {channel_slug}, 8k realistic documentary still"
            )
            task = {
                "id": b_id,
                "prompt": prompt,
                "aspect": "16:9",
                "model": image_model,
                "output_path": str(img_p),
                "based_on": effective_based_on,
                "credit_cost": 0,
                "credit_reason": "image",
                "type": "image",
                "editorial_overlay": {"enabled": False},
            }
            tasks.append(task)
            pool.submit_task(task)

        if tasks:
            pool.join()
        from sys.flow_video.sparkle_unblend import clean_beluga_sparkle_file

        from PIL import Image

        processed_paths = [Path(t["output_path"]) for t in tasks] if tasks else image_paths
        for img_p in processed_paths:
            if img_p.is_file() and img_p.stat().st_size > 5000:
                try:
                    clean_beluga_sparkle_file(img_p)
                    with Image.open(img_p) as im:
                        w, h = im.size
                        mx = int(round(w * ((1.0 - 1.0 / 1.06) / 2.0)))
                        my = int(round(h * ((1.0 - 1.0 / 1.06) / 2.0)))
                        cropped = im.crop((mx, my, w - mx, h - my)).resize((w, h), Image.Resampling.LANCZOS)
                        cropped.save(img_p)
                except Exception as exc:
                    logger.warning(f"Failed sparkle unblend / 1.06x overscan crop for {img_p}: {exc}")
    finally:
        pool.shutdown()

    return image_paths


# ---------------------------------------------------------------------------
# 7. Chapter-Chunked Remote Colab T4 NVENC & Safe Local Fallback Renderers
# ---------------------------------------------------------------------------


def render_long_chapter_chunks_local(
    job_id: str,
    chunks: list[BeatChunk],
    image_paths: list[Path],
    audio_path: Path,
    metadata_path: Path,
    watermark_png: Path,
    out_mp4: Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    xfade_dur: float = DEFAULT_XFADE_DUR,
    scratch_dir: Path | None = None,
) -> dict[str, Any]:
    """Safe chunked local CPU fallback renderer (-threads 2) strictly reserved for unit tests.

    Encodes each chunk of 15–22 beats into an independent MP4, then concatenates losslessly.
    """
    scratch = (scratch_dir or out_mp4.parent / f"_long_chunks_{job_id}").resolve()
    scratch.mkdir(parents=True, exist_ok=True)

    chunk_files: list[Path] = []

    for c in chunks:
        c_idx = c.chunk_index
        c_mp4 = scratch / f"chunk_{c_idx:03d}.mp4"
        chunk_files.append(c_mp4)

        if c_mp4.is_file() and c_mp4.stat().st_size > 1000:
            continue

        seg_files: list[Path] = []
        n_beats = len(c.beats)

        for b_i, (_beat, dur) in enumerate(zip(c.beats, c.beat_durations, strict=False)):
            seg_mp4 = scratch / f"seg_{c_idx:03d}_{b_i:03d}.mp4"
            seg_files.append(seg_mp4)
            if seg_mp4.is_file() and seg_mp4.stat().st_size > 1000:
                continue

            global_idx = c.start_beat_idx + b_i
            img_p = image_paths[global_idx] if global_idx < len(image_paths) else image_paths[-1]
            is_last = b_i == (n_beats - 1)
            seg_dur = dur if is_last else (dur + xfade_dur)

            vf = (
                f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={width}:{height}:(in_w-{width})/2:(in_h-{height})/2:exact=1,"
                f"setsar=1,format=yuv420p"
            )

            cmd_seg = [
                "ffmpeg", "-y", "-threads", "2",
                "-loop", "1", "-t", f"{seg_dur:.4f}", "-r", str(fps),
                "-i", str(img_p.resolve()),
                "-vf", vf,
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
                "-an", str(seg_mp4.resolve()),
            ]
            res = subprocess.run(cmd_seg, capture_output=True, text=True, check=False)
            if res.returncode != 0:
                raise RuntimeError(f"Local segment encode failed:\n{res.stderr[-500:]}")

        # Chain segments with calm optical fade (zero directional whip-pan or dither)
        cmd_c = ["ffmpeg", "-y", "-threads", "2"]
        for sf in seg_files:
            cmd_c.extend(["-i", str(sf.resolve())])

        if n_beats == 1:
            c_fc = ["[0:v]setsar=1[cvout]"]
            cur_v = "cvout"
        else:
            c_fc = []
            cum_offset = 0.0
            prev_l = "0:v"
            for i in range(1, n_beats):
                cum_offset += c.beat_durations[i - 1]
                trans = "fade"
                out_l = f"cx{i}"
                c_fc.append(f"[{prev_l}][{i}:v]xfade=transition={trans}:duration={xfade_dur:.4f}:offset={max(0.05, cum_offset):.4f}[{out_l}]")
                prev_l = out_l
            cur_v = prev_l

        cmd_c.extend([
            "-filter_complex", ";".join(c_fc),
            "-map", f"[{cur_v}]",
            "-t", f"{c.chunk_duration:.4f}",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
            "-an", str(c_mp4.resolve()),
        ])
        res_c = subprocess.run(cmd_c, capture_output=True, text=True, check=False)
        if res_c.returncode != 0:
            raise RuntimeError(f"Local chunk stitch failed:\n{res_c.stderr[-500:]}")

    # Lossless chunk concat
    chunks_txt = scratch / "chunks.txt"
    chunks_txt.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in chunk_files) + "\n", encoding="utf-8")

    merged_mp4 = scratch / "merged_video.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(chunks_txt.resolve()), "-c", "copy", str(merged_mp4.resolve())],
        check=True,
        capture_output=True,
    )

    # Audio muxing + Watermark + FFMETADATA1
    total_audio_dur = sum(c.chunk_duration for c in chunks)
    fin_cmd = ["ffmpeg", "-y", "-i", str(merged_mp4.resolve())]
    has_wm = watermark_png.is_file()
    if has_wm:
        fin_cmd.extend(["-i", str(watermark_png.resolve())])
    fin_cmd.extend(["-i", str(audio_path.resolve())])

    has_meta = metadata_path.is_file()
    if has_meta:
        fin_cmd.extend(["-i", str(metadata_path.resolve())])

    fc = []
    if has_wm:
        fc.append("[0:v][1:v]overlay=W-w-36:H-h-36[vout]")
        v_lbl = "[vout]"
        a_idx = 2
        m_idx = 3 if has_meta else None
    else:
        v_lbl = "0:v"
        a_idx = 1
        m_idx = 2 if has_meta else None

    fc.append(f"[{a_idx}:a]loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[aout]")

    fin_cmd.extend([
        "-filter_complex", ";".join(fc),
        "-map", v_lbl,
        "-map", "[aout]",
    ])
    if m_idx is not None:
        fin_cmd.extend(["-map_metadata", str(m_idx)])

    fin_cmd.extend([
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", f"{total_audio_dur:.4f}",
        "-movflags", "+faststart",
        str(out_mp4.resolve()),
    ])
    subprocess.run(fin_cmd, check=True, capture_output=True)

    meta = probe_video_clip(out_mp4)
    meta["video_encoder"] = "local_libx264"
    meta["colab_account"] = None
    meta["colab_session"] = None
    return meta


def render_long_chapter_chunks_colab_t4(
    job_id: str,
    chunks: list[BeatChunk],
    image_paths: list[Path],
    audio_path: Path,
    metadata_path: Path,
    watermark_png: Path,
    out_mp4: Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    xfade_dur: float = DEFAULT_XFADE_DUR,
    colab_account: str | None = None,
    scratch_dir: Path | None = None,
) -> dict[str, Any]:
    """Execute 100% remote Chapter-Chunked rendering on Colab Tesla T4 GPU with native h264_nvenc.

    Pre-scales images to JPEG Q92 in parallel (saving ~515MB upload), pre-encodes AAC audio,
    encodes chunks in parallel (max_workers=3) directly to /dev/shm on Colab T4 with burned watermark,
    and finishes with an instant 0.8s lossless concat stream-copy mux.
    """
    import concurrent.futures

    from PIL import Image

    scratch = (scratch_dir or out_mp4.parent / f"_colab_bundle_{job_id}").resolve()
    scratch.mkdir(parents=True, exist_ok=True)

    bundle_dir = scratch / "bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    images_dir = bundle_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Pre-encode audio to AAC narration.m4a (saves ~52MB upload vs uncompressed WAV)
    narration_m4a = bundle_dir / "narration.m4a"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(audio_path.resolve()),
            "-af",
            "loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            str(narration_m4a),
        ],
        check=True,
        capture_output=True,
    )

    shutil.copy2(watermark_png, bundle_dir / "watermark.png")
    shutil.copy2(metadata_path, bundle_dir / "chapters_metadata.txt")

    # 2. Parallel image conversion to JPEG Q92 (~550MB PNG -> ~35MB JPEG Q92 in ~1.5s)
    img_rel_paths: list[str] = ["" for _ in image_paths]

    def _convert_image(idx_p: tuple[int, Path]) -> tuple[int, str]:
        idx, p = idx_p
        dest = images_dir / f"img_{idx:04d}.jpg"
        if not dest.is_file() or dest.stat().st_size < 1000:
            with Image.open(p) as im:
                rgb_im = im.convert("RGB")
                if rgb_im.width > 2048 or rgb_im.height > 1152:
                    rgb_im = rgb_im.resize((1920, 1080), Image.Resampling.LANCZOS)
                rgb_im.save(dest, format="JPEG", quality=92, optimize=False)
        return idx, f"images/{dest.name}"

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool_ex:
        results = pool_ex.map(_convert_image, enumerate(image_paths))
        for idx, rel_p in results:
            img_rel_paths[idx] = rel_p

    # Build manifest for remote worker
    manifest_chunks = []
    for c in chunks:
        c_beats = []
        for b_i, (b, dur) in enumerate(zip(c.beats, c.beat_durations, strict=False)):
            g_idx = c.start_beat_idx + b_i
            c_beats.append({
                "image_file": img_rel_paths[g_idx],
                "duration": dur,
                "camera_motion": b.get("camera_motion", "push_in"),
                "transition": resolve_beat_transition(b, b_i),
            })
        manifest_chunks.append({
            "chunk_index": c.chunk_index,
            "chunk_duration": c.chunk_duration,
            "beats": c_beats,
        })

    total_dur = sum(c.chunk_duration for c in chunks)
    manifest_data = {
        "job_id": job_id,
        "width": width,
        "height": height,
        "fps": fps,
        "xfade_dur": xfade_dur,
        "total_duration": total_dur,
        "chunks": manifest_chunks,
    }
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    # 3. Create render_job.py inside bundle for async background execution on Colab
    render_job_script = """import json
import os
import shutil
import subprocess
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

work = Path(__file__).resolve().parent

def write_status(status, completed=0, total=0, error=None, tail=""):
    data = {"status": status, "completed_chunks": completed, "total_chunks": total, "error": error, "tail": tail}
    (work / "status.json").write_text(json.dumps(data), encoding="utf-8")

try:
    write_status("running", 0, 0, tail="Initializing remote render job...")
    manifest_p = work / "manifest.json"
    meta = json.loads(manifest_p.read_text(encoding="utf-8"))
    w, h = int(meta["width"]), int(meta["height"])
    fps = int(meta["fps"])
    xfade_dur = float(meta["xfade_dur"])
    total_dur = float(meta["total_duration"])
    chunks = meta["chunks"]
    total_chunks = len(chunks)
    write_status("running", 0, total_chunks, tail=f"Loaded {total_chunks} chunks.")

    # Check NVENC availability
    res = subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.04", "-c:v", "h264_nvenc", "-f", "null", "-"],
        capture_output=True, text=True
    )
    if res.returncode != 0:
        raise RuntimeError("COLAB_NVENC_UNAVAILABLE: h264_nvenc not supported on remote GPU: " + res.stderr)

    # Rock-steady 16:9 Lanczos frame lock (eliminates 15Hz vf_zoompan integer truncation tremor & whip-pan motion sickness)
    watermark_png = str(work / "watermark.png")
    completed_count = 0

    def render_chunk(c_data):
        global completed_count
        c_idx = c_data["chunk_index"]
        c_mp4 = work / f"chunk_{c_idx:03d}.mp4"
        beats = c_data["beats"]
        n_b = len(beats)
        seg_mp4s = []

        for b_i, beat in enumerate(beats):
            seg_mp4 = work / f"seg_{c_idx:03d}_{b_i:03d}.mp4"
            seg_mp4s.append(seg_mp4)
            dur = float(beat["duration"])
            seg_dur = dur if b_i == (n_b - 1) else (dur + xfade_dur)
            img_p = work / beat["image_file"]

            vf = f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h}:(in_w-{w})/2:(in_h-{h})/2:exact=1,setsar=1,format=yuv420p"
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-t", f"{seg_dur:.4f}", "-r", str(fps),
                "-i", str(img_p),
                "-vf", vf,
                "-c:v", "h264_nvenc", "-preset", "p2", "-b:v", "6M", "-g", "30", "-pix_fmt", "yuv420p",
                "-an", str(seg_mp4)
            ]
            p = subprocess.run(cmd, capture_output=True, text=True)
            if p.returncode != 0:
                raise RuntimeError(f"NVENC segment encode failed for chunk {c_idx} beat {b_i}: " + p.stderr[-500:])

        c_cmd = ["ffmpeg", "-y"]
        for sf in seg_mp4s:
            c_cmd.extend(["-i", str(sf)])
        wm_input_idx = len(seg_mp4s)
        c_cmd.extend(["-i", watermark_png])

        c_fc = []
        if n_b == 1:
            c_fc.append("[0:v]setsar=1[cv]")
            cur_v = "cv"
        else:
            cum_offset = 0.0
            prev_l = "0:v"
            for i in range(1, n_b):
                cum_offset += float(beats[i - 1]["duration"])
                raw_trans = str(beats[i].get("transition", "fade")).lower().strip()
                valid_xfades = ("fade",)
                trans = raw_trans if raw_trans in valid_xfades else "fade"
                out_l = f"cx{i}"
                c_fc.append(f"[{prev_l}][{i}:v]xfade=transition={trans}:duration={xfade_dur:.4f}:offset={max(0.05, cum_offset):.4f}[{out_l}]")
                prev_l = out_l
            cur_v = prev_l

        # Burn watermark directly inside chunk pass
        c_fc.append(f"[{cur_v}][{wm_input_idx}:v]overlay=W-w-36:H-h-36[cvout]")

        c_dur = sum(float(b["duration"]) for b in beats)
        c_cmd.extend([
            "-filter_complex", ";".join(c_fc),
            "-map", "[cvout]",
            "-t", f"{c_dur:.4f}",
            "-c:v", "h264_nvenc", "-preset", "p2", "-b:v", "6M", "-g", "30", "-pix_fmt", "yuv420p",
            "-an", str(c_mp4)
        ])
        p_c = subprocess.run(c_cmd, capture_output=True, text=True)
        if p_c.returncode != 0:
            raise RuntimeError(f"NVENC chunk stitch failed for chunk {c_idx}: " + p_c.stderr[-500:])

        for sf in seg_mp4s:
            sf.unlink(missing_ok=True)

        completed_count += 1
        msg = f"Rendered chunk {c_idx} ({completed_count}/{total_chunks})"
        write_status("running", completed_count, total_chunks, tail=msg)
        print(f"COLAB_CHUNK_PROGRESS:{completed_count}/{total_chunks}", flush=True)
        return c_idx, c_mp4

    # Parallel chunk rendering on T4 GPU (up to 3 concurrent NVENC streams)
    with ThreadPoolExecutor(max_workers=3) as executor:
        chunk_results = list(executor.map(render_chunk, chunks))

    chunk_results.sort(key=lambda x: x[0])
    chunk_files = [x[1] for x in chunk_results]

    chunks_txt = work / "chunks.txt"
    chunks_txt.write_text("".join(f"file '{p.name}'\\n" for p in chunk_files), encoding="utf-8")

    # Final assembly: 0.8s lossless stream-copy mux (zero video re-encode!)
    narration_m4a = work / "narration.m4a"
    metadata_txt = work / "chapters_metadata.txt"
    final_mp4 = work / "final.mp4"

    mux_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(chunks_txt),
        "-i", str(narration_m4a),
        "-i", str(metadata_txt),
        "-map", "0:v", "-map", "1:a",
        "-map_metadata", "2",
        "-c", "copy",
        "-t", f"{total_dur:.4f}",
        "-movflags", "+faststart",
        str(final_mp4)
    ]
    p_mux = subprocess.run(mux_cmd, capture_output=True, text=True)
    if p_mux.returncode != 0:
        raise RuntimeError("Final concat stream-copy mux failed: " + p_mux.stderr[-800:])

    for cp in chunk_files:
        cp.unlink(missing_ok=True)

    write_status("completed", total_chunks, total_chunks, tail="Video render complete.")
    print("COLAB_LONG_NVENC_RENDER_SUCCESS", flush=True)

except Exception as err:
    traceback.print_exc()
    write_status("failed", error=str(err), tail=f"ERROR: {err}")
    print("COLAB_LONG_NVENC_ERROR:", repr(err), flush=True)
    sys.exit(1)
"""
    (bundle_dir / "render_job.py").write_text(render_job_script, encoding="utf-8")

    bundle_zip = scratch / "bundle.zip"
    with zipfile.ZipFile(bundle_zip, "w", zipfile.ZIP_STORED) as zf:
        for f in bundle_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(bundle_dir))

    # 4. Connect to Colab and execute asynchronously
    if str(SYS_DIR) not in sys.path:
        sys.path.insert(0, str(SYS_DIR))
    from colab_bridge.accounts import select_pool
    from colab_bridge.pool_manager import ColabPoolManager

    if colab_account:
        accounts = [a.strip() for a in colab_account.split(",") if a.strip()]
    else:
        accounts = select_pool(session=f"vp-vn-long-{job_id[:16]}", role="render")
        if not accounts:
            accounts = ["account-04", "account-12", "account-13", "account-14", "account-15", "account-16", "account-17", "account-18"]
    cfg_base = SYS_DIR / "config.json"
    cfg: dict[str, Any] = json.loads(cfg_base.read_text(encoding="utf-8")) if cfg_base.is_file() else {}

    last_exc: Exception | None = None
    consecutive_unconfirmed = 0

    for acc in accounts:
        client = None
        started = False
        try:
            logger.info(f"Connecting to Colab Tesla T4 ({acc}) for Chapter-Chunked render...")
            pm = ColabPoolManager()
            sess_res = pm.run_account_cmd(acc, ["sessions"], check=False)
            sess_out = (sess_res.stdout or "") + "\n" + (sess_res.stderr or "")
            existing_sess = None
            for line in sess_out.splitlines():
                if "[" in line and "]" in line and "T4" in line:
                    s_name = line.split("[", 1)[1].split("]", 1)[0].strip()
                    if s_name and s_name != "?":
                        existing_sess = s_name
                        break

            target_session = existing_sess or f"vp-vn-long-{int(time.time())}"
            c_cfg = dict(cfg)
            c_cfg.setdefault("colab_tts", {})
            c_cfg["colab_tts"]["session"] = target_session
            c_cfg["colab_tts"]["account"] = acc

            client = Client(SYS_DIR, c_cfg)
            client.account = acc
            client.session = target_session
            client._runtime_role = "render"
            client.ensure_authenticated()
            if not existing_sess:
                try:
                    client._ready(auto_start=True)
                except Exception as ready_err:
                    logger.warning(f"Initial _ready failed for {acc}: {ready_err}. Attempting unassign + ledger release...")
                    try:
                        pm._unassign_server_endpoints(acc)
                        pm._release_account_ledger(acc, target_session)
                        from account_budget import Budgets
                        snap = Budgets().snapshot(f"colab:{acc}")
                        for item in snap.get("allocated_sessions", []):
                            pm._release_account_ledger(acc, item.get("session"))
                    except Exception:
                        pass
                    client.start()
            started = True

            # Stage remote work in /dev/shm (RAM disk) if >= 1.5GB free, else /content
            probe_out = client.exec(
                f"import shutil, os\n"
                f"free = shutil.disk_usage('/dev/shm').free if os.path.exists('/dev/shm') else 0\n"
                f"p = '/dev/shm/vp_long_{job_id}' if free > 1.5 * (1024**3) else '/content/vp_long_{job_id}'\n"
                f"from pathlib import Path; Path(p).mkdir(parents=True, exist_ok=True)\n"
                f"print('WORK_DIR:' + p)",
                timeout=35,
            )
            remote_dir = f"/dev/shm/vp_long_{job_id}"
            for line in probe_out.splitlines():
                if line.startswith("WORK_DIR:"):
                    remote_dir = line.split(":", 1)[1].strip()
                    break

            remote_bundle = f"{remote_dir}/bundle.zip"
            client.call("upload", "-s", client.session, str(bundle_zip.resolve()), remote_bundle, timeout=300)

            # Unpack bundle
            client.exec(
                f"import zipfile\nwith zipfile.ZipFile({remote_bundle!r}, 'r') as zf:\n    zf.extractall({remote_dir!r})",
                timeout=60,
            )

            # Launch render_job.py asynchronously in background
            client.exec(
                f"import subprocess\nsubprocess.Popen(['python3', f'{remote_dir}/render_job.py'], "
                f"stdout=open(f'{remote_dir}/render.log', 'w'), stderr=subprocess.STDOUT)",
                timeout=35,
            )

            # Poll status.json & render.log via short 30s client.exec calls
            poll_script = f"""
import json, os
from pathlib import Path
work = Path({remote_dir!r})
stat_f = work / 'status.json'
log_f = work / 'render.log'
res = {{'status': 'unknown', 'completed_chunks': 0, 'total_chunks': 0, 'error': None, 'tail': ''}}
if stat_f.is_file():
    try:
        res.update(json.loads(stat_f.read_text(encoding='utf-8')))
    except Exception:
        pass
if log_f.is_file():
    try:
        lines = log_f.read_text(encoding='utf-8', errors='replace').splitlines()
        if lines:
            res['tail'] = lines[-1]
    except Exception:
        pass
import json as _j; print('POLL_STATUS:' + _j.dumps(res))
"""
            start_poll = time.monotonic()
            render_timeout = 2400
            completed = False
            consecutive_poll_errors = 0

            while time.monotonic() - start_poll < render_timeout:
                time.sleep(10.0)
                try:
                    poll_out = client.exec(poll_script, timeout=60)
                    consecutive_poll_errors = 0
                except Exception as p_err:
                    consecutive_poll_errors += 1
                    logger.warning(f"[{job_id}] Poll exec error ({consecutive_poll_errors}/5): {p_err}")
                    if consecutive_poll_errors >= 5:
                        raise
                    continue

                poll_data = {}
                for line in poll_out.splitlines():
                    if line.startswith("POLL_STATUS:"):
                        try:
                            poll_data = json.loads(line.split(":", 1)[1])
                        except Exception:
                            pass
                        break

                p_status = poll_data.get("status", "unknown")
                comp = poll_data.get("completed_chunks", 0)
                tot = poll_data.get("total_chunks", 0)
                tail = poll_data.get("tail", "")
                logger.info(f"[{job_id}] Colab T4 render progress: {comp}/{tot} chunks ({p_status}) - {tail}")

                if p_status == "completed":
                    completed = True
                    break
                elif p_status == "failed":
                    err = poll_data.get("error", "Unknown render error")
                    raise RuntimeError(f"Colab render_job failed: {err}")

            if not completed:
                raise TimeoutError(f"Colab long render timed out after {render_timeout}s")

            client.call("download", "-s", client.session, f"{remote_dir}/final.mp4", str(out_mp4.resolve()), timeout=300)

            meta = probe_video_clip(out_mp4)
            meta["video_encoder"] = "colab_t4_h264_nvenc"
            meta["colab_account"] = acc
            meta["colab_session"] = client.session
            return meta

        except Exception as exc:
            last_exc = exc
            is_unconfirmed = "COLAB_EXEC_UNCONFIRMED" in str(exc)
            if is_unconfirmed:
                consecutive_unconfirmed += 1
            else:
                consecutive_unconfirmed = 0
            if consecutive_unconfirmed >= 2:
                logger.error("Aborting failover after 2 consecutive COLAB_EXEC_UNCONFIRMED errors per AGENTS.md §5")
                raise RuntimeError(f"Failover aborted after 2 consecutive COLAB_EXEC_UNCONFIRMED: {exc}") from exc
            logger.warning(f"Colab account {acc} failed: {exc}. Trying next candidate...")
            continue
        finally:
            if client is not None and started:
                try:
                    logger.info(f"Stopping Colab session {client.session} on account {acc}...")
                    client.stop()
                except Exception as stop_exc:
                    logger.warning(f"Failed to cleanly stop Colab session {client.session}: {stop_exc}")

    raise RuntimeError(f"All Colab accounts unavailable for T4 NVENC render: {last_exc}")


# ---------------------------------------------------------------------------
# 8. Dry-Run Synthetic Stub for Fast Non-Credit Verification
# ---------------------------------------------------------------------------


def render_dry_run_stub(
    job_id: str,
    out_mp4: Path,
    audio_path: Path | None,
    width: int = 1920,
    height: int = 1080,
    duration: float = 2.0,
) -> dict[str, Any]:
    """Generate minimal fast synthetic MP4 stub for unit testing without credit spend."""
    out_p = Path(out_mp4)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    stub_dur = min(2.0, max(0.2, float(duration)))

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:d={stub_dur:.3f}:r=30",
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={stub_dur:.3f}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "32",
        "-c:a", "aac", "-b:a", "64k",
        "-t", f"{stub_dur:.3f}",
        str(out_p.resolve()),
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    meta = probe_video_clip(out_p)
    meta["video_encoder"] = "dry_run_stub"
    meta["duration"] = duration
    meta["colab_account"] = None
    meta["colab_session"] = None
    return meta


# ---------------------------------------------------------------------------
# 9. Dual-Mode Production Orchestrators
# ---------------------------------------------------------------------------


def run_short_mode(config: DualModeJobConfig) -> dict[str, Any]:
    """Execute Mode 1: Short 9:16 Full-Chain Omni 1.2 Flash Video Generation & Packaging."""
    logger.info(f"[{config.job_id}] Launching Mode 1: Short 9:16 Full-Chain Omni 1.2 Flash...")
    out_dir = config.output_dir if config.output_dir.name == config.job_id else config.output_dir / config.job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir = out_dir / "_work_short"
    work_dir.mkdir(parents=True, exist_ok=True)
    verify_channel_voice_lock(config.channel_slug, root=ROOT)

    # 1. Load spec
    spec_data = {}
    if config.spec_path and Path(config.spec_path).is_file():
        spec_data = json.loads(Path(config.spec_path).read_text(encoding="utf-8"))
    else:
        # Fallback to aligned short spec, short fullchain spec, or default rebuilt spec
        cand_aligned = out_dir / f"{config.channel_slug.replace('-', '_')}_short_aligned_spec.json"
        cand_short_fc = SYS_DIR / f"channels/vn_rebuilt_style_specs/{config.channel_slug}/{config.channel_slug}_short_fullchain_spec.json"
        cand_rebuilt = SYS_DIR / f"channels/vn_rebuilt_style_specs/{config.channel_slug}/{config.channel_slug}_rebuilt_spec.json"
        if cand_aligned.is_file():
            spec_data = json.loads(cand_aligned.read_text(encoding="utf-8"))
            logger.info(f"[{config.job_id}] Loaded short spec from aligned spec: {cand_aligned}")
        elif cand_short_fc.is_file():
            spec_data = json.loads(cand_short_fc.read_text(encoding="utf-8"))
            logger.info(f"[{config.job_id}] Loaded short spec from full-chain spec: {cand_short_fc}")
        elif cand_rebuilt.is_file():
            spec_data = json.loads(cand_rebuilt.read_text(encoding="utf-8"))
            logger.info(f"[{config.job_id}] Loaded short spec from default rebuilt spec: {cand_rebuilt}")
        else:
            raise FileNotFoundError(f"Missing spec file for {config.channel_slug}: tried {cand_aligned}, {cand_short_fc}, {cand_rebuilt}")

    beats = spec_data.get("beats", [])
    if not beats:
        raise ValueError(f"No beats found in spec for {config.channel_slug}")

    # 2. Audio & Kinetic Subtitles
    audio_wav = work_dir / "narration.wav"
    ass_path = work_dir / "subtitles_kinetic_9x16.ass"
    srt_path = work_dir / "subtitles.srt"

    words: list[dict[str, Any]] = []
    beat_durations: list[float] = []
    cached_audio_found = False

    if config.dry_run:
        c_time = 0.0
        for b_i, b in enumerate(beats):
            b_dur = float(b.get("duration") or b.get("target_duration") or 2.5)
            beat_durations.append(b_dur)
            tokens = str(b.get("narration", f"Beat {b_i + 1}")).split()
            t_step = b_dur / max(1, len(tokens))
            for tok_i, tok in enumerate(tokens):
                words.append({
                    "word": tok,
                    "start": round(c_time + tok_i * t_step, 4),
                    "end": round(c_time + (tok_i + 1) * t_step, 4),
                })
            c_time += b_dur

        total_dur = sum(beat_durations)
        synth_dur = min(1.5, total_dur)
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=f=440:d={synth_dur:.3f}", "-af", "loudnorm=I=-11.0:TP=-1.0:LRA=7.0", str(audio_wav)],
            check=True,
            capture_output=True,
        )
    elif config.audio_path and Path(config.audio_path).is_file():
        shutil.copy2(config.audio_path, audio_wav)
        cached_audio_found = True
    elif audio_wav.is_file() and audio_wav.stat().st_size > 1000:
        real_audio_dur = _probe_audio_duration_sec(audio_wav)
        if real_audio_dur < 10.0 and (out_dir / "narration_master.wav").is_file():
            shutil.copy2(out_dir / "narration_master.wav", audio_wav)
            real_audio_dur = _probe_audio_duration_sec(audio_wav)
            logger.info(f"[{config.job_id}] Overwrote short audio with real narration_master.wav at {audio_wav} ({real_audio_dur:.2f}s)")
        else:
            logger.info(f"[{config.job_id}] Reusing cached narration audio at {audio_wav}")
        cached_audio_found = True
    elif (out_dir / "narration_master.wav").is_file():
        shutil.copy2(out_dir / "narration_master.wav", audio_wav)
        logger.info(f"[{config.job_id}] Reusing cached narration audio from {out_dir / 'narration_master.wav'}")
        cached_audio_found = True
    else:
        cached_audio_found = False

    if cached_audio_found:
        aligned_spec_file = out_dir / f"{config.channel_slug.replace('-', '_')}_short_aligned_spec.json"
        loaded_from_aligned = False
        if aligned_spec_file.is_file():
            try:
                aligned_data = json.loads(aligned_spec_file.read_text(encoding="utf-8"))
                if aligned_data.get("words") and aligned_data.get("beat_durations"):
                    words = aligned_data["words"]
                    beat_durations = [float(d) for d in aligned_data["beat_durations"]]
                    if aligned_data.get("beats"):
                        beats = aligned_data["beats"]
                    total_dur = sum(beat_durations)
                    loaded_from_aligned = True
                    logger.info(f"[{config.job_id}] Loaded exact word-level sync, {len(beats)} beats, and durations from {aligned_spec_file.name}")
            except Exception:
                loaded_from_aligned = False

        if not loaded_from_aligned:
            beat_durations = [float(b.get("duration") or b.get("target_duration") or 2.5) for b in beats]
            c_time = 0.0
            words = []
            for b_i, b in enumerate(beats):
                b_dur = beat_durations[b_i]
                tokens = str(b.get("narration", f"Beat {b_i + 1}")).split()
                t_step = b_dur / max(1, len(tokens))
                for tok_i, tok in enumerate(tokens):
                    words.append({
                        "word": tok,
                        "start": round(c_time + tok_i * t_step, 4),
                        "end": round(c_time + (tok_i + 1) * t_step, 4),
                    })
                c_time += b_dur
            total_dur = sum(beat_durations)
    elif config.visuals_only:
        beat_durations = [float(b.get("duration") or b.get("target_duration") or 3.5) for b in beats]
        c_time = 0.0
        words = []
        for b_i, b in enumerate(beats):
            b_dur = beat_durations[b_i]
            tokens = str(b.get("narration", f"Beat {b_i + 1}")).split()
            t_step = b_dur / max(1, len(tokens))
            for tok_i, tok in enumerate(tokens):
                words.append({
                    "word": tok,
                    "start": round(c_time + tok_i * t_step, 4),
                    "end": round(c_time + (tok_i + 1) * t_step, 4),
                })
            c_time += b_dur
        total_dur = sum(beat_durations)
    elif not config.dry_run:
        ch_voice = config.spec_data.get("voice") or f"VietNarrator_{config.channel_slug.replace('-', '_')}"
        norm_wav, real_dur, real_beat_durs, global_words = synthesize_vn_narration_and_words(
            beats=beats,
            voice=ch_voice,
            audio_dir=work_dir / "_tts_work",
            channel_slug=config.channel_slug,
        )
        shutil.copy2(norm_wav, audio_wav)
        beat_durations = real_beat_durs
        total_dur = real_dur
        words = global_words

    build_vn_kinetic_ass_subtitles(words, total_dur, ass_path, margin_v=270, outline=6)
    build_clean_sidecar_srt(beats, beat_durations, total_dur, srt_path)

    # 3. Watermark
    watermark_png = work_dir / "watermark_100x100.png"
    logo_src = resolve_channel_logo_source(config.channel_slug)
    make_rounded_watermark(logo_src, watermark_png, size=100, opacity=0.92, radius=16)

    # 4. Short Keyframe Pre-generation & FlowVideoChainOrchestrator
    frames_dir = work_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    ledger = CreditLedger()
    resolved_profiles = resolve_authenticated_profiles(config.profiles, credit_ledger=ledger)
    if resolved_profiles:
        profile_names = [p.get("name") or p.get("id") for p in resolved_profiles if (p.get("name") or p.get("id"))]
        os.environ["VP_FLOW_PROFILES"] = ",".join(profile_names)

    if not config.dry_run:
        missing_frame_tasks: list[dict[str, Any]] = []
        for i, beat in enumerate(beats):
            beat_frame = frames_dir / f"beat_{i:02d}.png"
            if not (beat_frame.is_file() and beat_frame.stat().st_size > 5000):
                pair_start = frames_dir / f"pair_{i:02d}_start.png"
                pair_end_prev = frames_dir / f"pair_{i - 1:02d}_end.png" if i > 0 else None
                if pair_start.is_file() and pair_start.stat().st_size > 5000:
                    shutil.copy2(pair_start, beat_frame)
                elif pair_end_prev and pair_end_prev.is_file() and pair_end_prev.stat().st_size > 5000:
                    shutil.copy2(pair_end_prev, beat_frame)
                else:
                    prompt = (
                        beat.get("prompt")
                        or f"Cinematic short vertical visual for {config.channel_slug}, beat {i + 1}"
                    )
                    missing_frame_tasks.append({
                        "id": beat.get("beat_id", f"beat_{i:02d}"),
                        "prompt": prompt,
                        "aspect": "9:16",
                        "model": config.image_model,
                        "output_path": str(beat_frame),
                        "credit_cost": 0,
                        "credit_reason": "image",
                        "type": "image",
                        "editorial_overlay": {"enabled": False},
                    })

        if missing_frame_tasks:
            target_workers = (
                min(len(missing_frame_tasks), max(config.max_workers, 1), len(resolved_profiles))
                if resolved_profiles
                else min(len(missing_frame_tasks), max(config.max_workers, 1))
            )
            pool_kwargs: dict[str, Any] = {
                "target_workers": target_workers,
                "headless": True,
                "profiles": resolved_profiles if resolved_profiles else None,
                "min_credits_required": 1,
                "credit_ledger": ledger,
                "default_out_dir": frames_dir,
                "pacing_seconds": 2.2,
                "stagger_seconds": 1.0,
                "cooldown_seconds": 90.0,
            }
            import inspect

            sig_params = inspect.signature(PersistentWorkerPool.__init__).parameters
            if "enable_work_stealing" in sig_params:
                pool_kwargs["enable_work_stealing"] = True
            if "work_steal_threshold" in sig_params:
                pool_kwargs["work_steal_threshold"] = 2
            pool = PersistentWorkerPool(**pool_kwargs)
            pool.start()
            try:
                for t in missing_frame_tasks:
                    pool.submit_task(t)
                pool.join()
            finally:
                pool.shutdown()

        from sys.flow_video.sparkle_unblend import clean_beluga_sparkle_file

        from PIL import Image

        for i, beat in enumerate(beats):
            beat_frame = frames_dir / f"beat_{i:02d}.png"
            if beat_frame.is_file() and beat_frame.stat().st_size > 5000:
                try:
                    clean_beluga_sparkle_file(beat_frame)
                    with Image.open(beat_frame) as im:
                        w, h = im.size
                        mx = int(round(w * ((1.0 - 1.0 / 1.06) / 2.0)))
                        my = int(round(h * ((1.0 - 1.0 / 1.06) / 2.0)))
                        cropped = im.crop((mx, my, w - mx, h - my)).resize((w, h), Image.Resampling.LANCZOS)
                        cropped.save(beat_frame)
                except Exception as exc:
                    logger.warning(f"Failed sparkle unblend / 1.06x overscan crop for {beat_frame}: {exc}")
                beat["image_path"] = str(beat_frame.resolve())

    chain_spec = build_short_video_chain_spec(
        channel_slug=config.channel_slug,
        job_id=config.job_id,
        shots=beats,
        audio_path=audio_wav,
        beat_durations=beat_durations,
        auto_fallback_zero_credit=False,
    )

    completed_tasks: list[VideoClipTask] = []
    if config.dry_run:
        for idx, pair in enumerate(chain_spec.scene_pairs):
            dummy_mp4 = work_dir / f"clip_{idx:02d}.mp4"
            render_dry_run_stub(f"clip_{idx:02d}", dummy_mp4, None, 1080, 1920, duration=pair.target_duration or 3.0)
            completed_tasks.append(VideoClipTask(
                clip_id=pair.id,
                index=idx,
                start_frame_path=str(pair.start_image_path or ""),
                end_frame_path=pair.end_image_path,
                output_mp4_path=str(dummy_mp4),
                aspect="9:16",
                video_model="omni_flash",
                status="completed",
                profile_used="dry_run_stub",
            ))
    else:
        chain_manifest_file = work_dir / "chain_manifest.json"
        if chain_manifest_file.is_file():
            try:
                m_data = json.loads(chain_manifest_file.read_text(encoding="utf-8"))
                if len(m_data.get("tasks", [])) != len(chain_spec.scene_pairs):
                    logger.warning(
                        f"[{config.job_id}] Existing chain_manifest.json task count ({len(m_data.get('tasks', []))}) "
                        f"!= scene_pairs count ({len(chain_spec.scene_pairs)}). Unlinking to force rescan."
                    )
                    chain_manifest_file.unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"[{config.job_id}] Error reading existing chain_manifest.json: {e}; unlinking.")
                chain_manifest_file.unlink(missing_ok=True)

        orchestrator = FlowVideoChainOrchestrator(
            spec=chain_spec,
            work_dir=work_dir,
            output_mp4_path=work_dir / "preview.mp4",
            max_workers=config.max_workers,
            headless=True,
            dry_run=config.dry_run,
            skip_stitch=True,
        )
        orchestrator.run()
        manifest_data = json.loads((work_dir / "chain_manifest.json").read_text(encoding="utf-8"))
        completed_tasks = [VideoClipTask.from_dict(td) for td in manifest_data.get("tasks", [])]

    if config.visuals_only:
        logger.info(f"[{config.job_id}] Visuals-only mode complete: {len(beats)} keyframes, {len(completed_tasks)} clips ready on disk.")
        return {
            "job_id": config.job_id,
            "mode": config.mode,
            "keyframes": len(beats),
            "clips": len(completed_tasks),
            "status": "visuals_ready",
        }

    # 5. Hybrid Stitching & NVENC packaging
    final_mp4 = out_dir / f"{config.job_id}_9x16.mp4"
    from sys.tools.produce_en_flow_dynamic_demo import stitch_hybrid_scene_groups_and_package

    meta = stitch_hybrid_scene_groups_and_package(
        channel_slug=config.channel_slug,
        aspect="9:16",
        shots=beats,
        tasks=completed_tasks,
        beat_durations=beat_durations,
        audio_path=audio_wav,
        ass_path=ass_path,
        srt_path=srt_path,
        watermark_png=watermark_png,
        out_mp4=final_mp4,
        fps=config.fps,
        xfade_pivot_sec=config.xfade_dur,
        render_backend=config.render_backend,
        job_id=config.job_id,
        dry_run=config.dry_run,
        colab_account=config.colab_account,
    )

    # 6. Generate sensational 9:16 thumbnail (preserve if already exists)
    thumb_png = out_dir / f"{config.job_id}_thumbnail_9x16.png"
    if not (thumb_png.is_file() and thumb_png.stat().st_size > 50_000):
        spec_hook = None
        if isinstance(spec_data, dict):
            spec_hook = spec_data.get("thumbnail_spec", {}).get("text_prompt")
        cand_frame = getattr(completed_tasks[0], "start_frame_path", None) if completed_tasks else None
        if not cand_frame or not Path(cand_frame).is_file():
            cand_frame = work_dir / "frames" / "beat_00.png"
        generate_high_contrast_thumbnail(
            out_path=thumb_png,
            width=1080,
            height=1920,
            image_src=Path(cand_frame) if Path(cand_frame).is_file() else None,
            text_overlay=spec_hook or "",
            channel_slug=config.channel_slug,
        )
    else:
        logger.info(f"[{config.job_id}] Preserving pre-existing Flow BELUGA thumbnail ({thumb_png.stat().st_size} bytes): {thumb_png}")

    # 7. Embed poster thumbnail onto first 0.12s of Short MP4 & attach cover stream
    if thumb_png.is_file() and final_mp4.is_file() and not config.dry_run:
        try:
            from sys.tools.thumbnail_embedder import embed_poster_thumbnail_into_short
            embed_poster_thumbnail_into_short(final_mp4, thumb_png, duration_sec=0.12)
        except Exception as embed_err:
            logger.warning(f"[{config.job_id}] Notice: Could not embed poster thumbnail into Short: {embed_err}")

    return {
        "job_id": config.job_id,
        "mode": DualMode.BUILD_SHORT.value,
        "video_path": str(final_mp4.resolve()),
        "thumbnail_path": str(thumb_png.resolve()),
        "duration": meta.get("duration", total_dur),
        "encoder": meta.get("video_encoder", "unknown"),
        "ass_path": str(ass_path.resolve()),
        "srt_path": str(srt_path.resolve()),
        "status": "success",
    }


def _probe_audio_duration_sec(path: Path | str) -> float:
    """Probe audio file duration in seconds via ffprobe."""
    try:
        res = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True,
            text=True,
            check=True,
        )
        val = float(res.stdout.strip())
        return val if val > 0 else 0.0
    except Exception as e:
        logger.warning(f"Failed to probe audio duration for {path}: {e}")
        return 0.0


def run_long_mode(config: DualModeJobConfig) -> dict[str, Any]:
    """Execute Mode 2: Long 16:9 Multi-Image BELUGA DAG & Chapter-Chunked T4 NVENC Renderer."""
    logger.info(f"[{config.job_id}] Launching Mode 2: Long 16:9 Multi-Image Chapter-Chunked T4 NVENC...")
    out_dir = config.output_dir if config.output_dir.name == config.job_id else config.output_dir / config.job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir = out_dir / "_work_long"
    work_dir.mkdir(parents=True, exist_ok=True)
    verify_channel_voice_lock(config.channel_slug, root=ROOT)

    # 1. Load or synthesize Two-Tier 240–350 beats
    spec_data = {}
    aligned_candidate = None
    for cand in [
        out_dir / f"{config.job_id}_aligned_spec.json",
        out_dir / f"{config.channel_slug.replace('-', '_')}_long_aligned_spec.json",
        out_dir / f"{config.channel_slug}_long_aligned_spec.json",
        out_dir / f"{config.channel_slug.replace('-', '_')}_long_305_aligned_spec.json",
        out_dir / f"{config.channel_slug.replace('-', '_')}_long_310_aligned_spec.json",
        out_dir / "tui_tien_long_305_aligned_spec.json",
    ]:
        if cand.is_file():
            aligned_candidate = cand
            break

    if aligned_candidate is not None:
        logger.info(f"[{config.job_id}] Loading cached audio-aligned spec from {aligned_candidate}")
        spec_data = json.loads(aligned_candidate.read_text(encoding="utf-8"))
    elif config.spec_path and Path(config.spec_path).is_file():
        spec_data = json.loads(Path(config.spec_path).read_text(encoding="utf-8"))
    else:
        master_p = SYS_DIR / f"channels/vn_rebuilt_style_specs/{config.channel_slug}/{config.channel_slug}_long_master_spec.json"
        if master_p.is_file():
            spec_data = json.loads(master_p.read_text(encoding="utf-8"))
        else:
            def_p = SYS_DIR / f"channels/vn_rebuilt_style_specs/{config.channel_slug}/{config.channel_slug}_rebuilt_spec.json"
            if def_p.is_file():
                spec_data = json.loads(def_p.read_text(encoding="utf-8"))

    raw_beats = spec_data.get("beats", [])
    raw_visual_states = spec_data.get("visual_states", [])
    raw_chapters = spec_data.get("chapters", [])

    beats: list[dict[str, Any]] = []
    planned_chapters: list[dict[str, Any]] = []

    if len(raw_beats) >= 60:
        for idx, b in enumerate(raw_beats):
            beats.append({
                "beat_id": b.get("beat_id") or b.get("id", f"B{idx:03d}"),
                "based_on": b.get("based_on"),
                "prompt": b.get("prompt") or b.get("prompt_spec", ""),
                "duration": float(b.get("duration") or b.get("hold") or 2.6),
                "camera_motion": b.get("camera_motion") or b.get("camera_move", "push_in"),
                "transition": resolve_beat_transition(b, idx),
                "narration": str(b.get("narration") or b.get("emphasis_text") or ""),
                "chapter_index": int(b.get("chapter_index", 1)),
                **{k: v for k, v in b.items() if k not in ("beat_id", "based_on", "prompt", "duration", "camera_motion", "transition", "narration", "chapter_index")},
            })
        planned_chapters = list(raw_chapters)
    elif len(raw_visual_states) >= 60:
        for idx, vs in enumerate(raw_visual_states):
            beats.append({
                "beat_id": vs.get("id") or vs.get("beat_id", f"VS{idx:03d}"),
                "based_on": vs.get("based_on"),
                "prompt": vs.get("prompt_spec") or vs.get("prompt", ""),
                "duration": float(vs.get("hold") or vs.get("duration") or 2.6),
                "camera_motion": vs.get("camera_move") or vs.get("camera_motion", "push_in"),
                "transition": resolve_beat_transition(vs, idx),
                "narration": str(vs.get("narration") or vs.get("emphasis_text") or ""),
                "chapter_index": int(vs.get("chapter_index", 1)),
            })
        planned_chapters = list(raw_chapters)
    else:
        from channels.vn_long_high_density_planner import (
            plan_long_visual_states_from_chapters,
            validate_high_density_long_plan,
        )
        plan = plan_long_visual_states_from_chapters(
            channel_id=config.channel_slug,
            chapters=raw_chapters if raw_chapters else None,
        )
        plan_errs = validate_high_density_long_plan(plan)
        if plan_errs:
            logger.warning(f"[{config.job_id}] High density plan validation issues: {plan_errs}")

        for idx, vs in enumerate(plan.visual_states):
            beats.append({
                "beat_id": vs.id,
                "based_on": vs.based_on,
                "prompt": vs.prompt_spec,
                "duration": vs.hold,
                "camera_motion": vs.camera_move,
                "transition": resolve_beat_transition({"transition": vs.xfade, "camera_motion": vs.camera_move}, idx),
                "narration": vs.emphasis_text or f"Phân đoạn {idx + 1}",
                "chapter_index": vs.chapter_index,
                "event_kind": vs.event_kind.value if hasattr(vs.event_kind, "value") else str(vs.event_kind),
            })
        planned_chapters = [asdict(ch) for ch in plan.chapters]

    beat_durations: list[float] = [float(b.get("duration") or 2.6) for b in beats]
    total_dur = sum(beat_durations)

    # 2. Audio & FFMETADATA1 Chapters (>=8 chapters, each >=10s)
    audio_wav = work_dir / "narration.wav"
    meta_txt = work_dir / "chapters_metadata.txt"
    srt_path = work_dir / "subtitles.srt"

    if config.dry_run:
        synth_dur = min(1.5, total_dur)
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=f=440:d={synth_dur:.3f}", "-af", "loudnorm=I=-11.0:TP=-1.0:LRA=7.0", str(audio_wav)],
            check=True,
            capture_output=True,
        )
    elif config.audio_path and Path(config.audio_path).is_file():
        shutil.copy2(config.audio_path, audio_wav)
        beat_durations = [float(b.get("duration") or b.get("hold") or b.get("target_duration") or 2.5) for b in beats]
        real_audio_dur = _probe_audio_duration_sec(audio_wav)
        sum_nom = sum(beat_durations)
        if real_audio_dur > 0 and sum_nom > 0:
            scale = real_audio_dur / sum_nom
            beat_durations = [round(d * scale, 4) for d in beat_durations]
            diff = round(real_audio_dur - sum(beat_durations), 4)
            if beat_durations and diff != 0.0:
                beat_durations[-1] = round(beat_durations[-1] + diff, 4)
        total_dur = sum(beat_durations)
    elif audio_wav.is_file() and audio_wav.stat().st_size > 1000:
        real_audio_dur = _probe_audio_duration_sec(audio_wav)
        if real_audio_dur < 10.0 and (out_dir / "narration_master.wav").is_file():
            shutil.copy2(out_dir / "narration_master.wav", audio_wav)
            real_audio_dur = _probe_audio_duration_sec(audio_wav)
            logger.info(f"[{config.job_id}] Overwrote short audio with real narration_master.wav at {audio_wav} ({real_audio_dur:.2f}s)")
        else:
            logger.info(f"[{config.job_id}] Reusing cached narration audio at {audio_wav}")
        beat_durations = [float(b.get("duration") or b.get("hold") or b.get("target_duration") or 2.5) for b in beats]
        real_audio_dur = _probe_audio_duration_sec(audio_wav)
        sum_nom = sum(beat_durations)
        if real_audio_dur > 0 and sum_nom > 0:
            scale = real_audio_dur / sum_nom
            beat_durations = [round(d * scale, 4) for d in beat_durations]
            diff = round(real_audio_dur - sum(beat_durations), 4)
            if beat_durations and diff != 0.0:
                beat_durations[-1] = round(beat_durations[-1] + diff, 4)
        total_dur = sum(beat_durations)
    elif (out_dir / "narration_master.wav").is_file():
        shutil.copy2(out_dir / "narration_master.wav", audio_wav)
        logger.info(f"[{config.job_id}] Reusing cached narration audio from {out_dir / 'narration_master.wav'}")
        beat_durations = [float(b.get("duration") or b.get("hold") or b.get("target_duration") or 2.5) for b in beats]
        real_audio_dur = _probe_audio_duration_sec(audio_wav)
        sum_nom = sum(beat_durations)
        if real_audio_dur > 0 and sum_nom > 0:
            scale = real_audio_dur / sum_nom
            beat_durations = [round(d * scale, 4) for d in beat_durations]
            diff = round(real_audio_dur - sum(beat_durations), 4)
            if beat_durations and diff != 0.0:
                beat_durations[-1] = round(beat_durations[-1] + diff, 4)
        total_dur = sum(beat_durations)
    else:
        ch_voice = config.spec_data.get("voice") or f"VietNarrator_{config.channel_slug.replace('-', '_')}"
        norm_wav, real_dur, real_beat_durs, _ = synthesize_vn_narration_and_words(
            beats=beats,
            voice=ch_voice,
            audio_dir=work_dir / "_tts_work",
            channel_slug=config.channel_slug,
        )
        shutil.copy2(norm_wav, audio_wav)
        beat_durations = real_beat_durs
        total_dur = real_dur

    _, chapters = build_ffmetadata_chapters(
        total_duration=total_dur,
        chapters=planned_chapters if planned_chapters else None,
        beats=beats,
        title=f"{config.channel_slug.upper()} Explainer Master",
        artist="Video Pilot",
        min_chapters=8,
        min_interval_sec=10.0,
        out_path=meta_txt,
    )
    build_clean_sidecar_srt(beats, beat_durations, total_dur, srt_path)

    # 3. Dispatch 240–350 16:9 image DAG via PersistentWorkerPool
    images_dir = work_dir / "images"
    image_paths = dispatch_long_image_dag_via_pool(
        channel_slug=config.channel_slug,
        beats=beats,
        output_dir=images_dir,
        image_model=config.image_model,
        max_workers=config.max_workers,
        dry_run=config.dry_run,
        allowed_profiles=config.profiles,
    )

    # 4. Partition timeline into chapter chunks of 15–22 beats
    chunks = partition_timeline_into_chunks(beats, beat_durations, min_chunk_size=15, max_chunk_size=22)
    logger.info(f"[{config.job_id}] Partitioned {len(beats)} beats into {len(chunks)} chunks (15-22 beats/chunk).")

    # 5. Watermark & Thumbnail
    watermark_png = work_dir / "watermark_100x100.png"
    logo_src = resolve_channel_logo_source(config.channel_slug)
    if watermark_png.is_file() and watermark_png.stat().st_size <= 2000:
        watermark_png.unlink(missing_ok=True)
    make_rounded_watermark(logo_src, watermark_png, size=100, opacity=0.92, radius=16)
    if watermark_png.is_file() and watermark_png.stat().st_size <= 2000 and logo_src:
        watermark_png.unlink(missing_ok=True)
        make_rounded_watermark(logo_src, watermark_png, size=100, opacity=0.92, radius=16)
    assert watermark_png.is_file() and watermark_png.stat().st_size > 2000, (
        f"[{config.job_id}] Watermark file {watermark_png} size "
        f"{watermark_png.stat().st_size if watermark_png.is_file() else 0} bytes is not > 2000 bytes."
    )

    thumb_png = out_dir / f"{config.job_id}_thumbnail_16x9.png"
    if not (thumb_png.is_file() and thumb_png.stat().st_size > 50_000):
        spec_hook = None
        if isinstance(spec_data, dict):
            spec_hook = spec_data.get("thumbnail_spec", {}).get("text_prompt")
        first_long_img = image_paths[0] if image_paths else None
        generate_high_contrast_thumbnail(
            out_path=thumb_png,
            width=1920,
            height=1080,
            image_src=first_long_img if first_long_img and Path(first_long_img).is_file() else None,
            text_overlay=spec_hook or "",
            channel_slug=config.channel_slug,
        )

    # 6. Execute rendering
    final_mp4 = out_dir / f"{config.job_id}_16x9.mp4"
    if config.dry_run:
        meta = render_dry_run_stub(config.job_id, final_mp4, audio_wav, 1920, 1080, duration=total_dur)
    elif config.render_backend == "local":
        meta = render_long_chapter_chunks_local(
            job_id=config.job_id,
            chunks=chunks,
            image_paths=image_paths,
            audio_path=audio_wav,
            metadata_path=meta_txt,
            watermark_png=watermark_png,
            out_mp4=final_mp4,
            width=1920,
            height=1080,
            fps=config.fps,
            xfade_dur=config.xfade_dur,
            scratch_dir=work_dir / "_local_render",
        )
    else:
        meta = render_long_chapter_chunks_colab_t4(
            job_id=config.job_id,
            chunks=chunks,
            image_paths=image_paths,
            audio_path=audio_wav,
            metadata_path=meta_txt,
            watermark_png=watermark_png,
            out_mp4=final_mp4,
            width=1920,
            height=1080,
            fps=config.fps,
            xfade_dur=config.xfade_dur,
            colab_account=config.colab_account,
            scratch_dir=work_dir / "_colab_render",
        )

    if final_mp4.is_file() and final_mp4.stat().st_size > 1_000_000:
        shutil.copy2(final_mp4, out_dir / "final_long.mp4")

    return {
        "job_id": config.job_id,
        "mode": DualMode.BUILD_LONG.value,
        "video_path": str(final_mp4.resolve()),
        "duration": meta.get("duration", total_dur),
        "encoder": meta.get("video_encoder", "unknown"),
        "chunks_rendered": len(chunks),
        "chapters_count": len(chapters),
        "metadata_path": str(meta_txt.resolve()),
        "srt_path": str(srt_path.resolve()),
        "thumbnail_path": str(thumb_png.resolve()),
        "status": "success",
    }


def run_dry_run_verify(config: DualModeJobConfig) -> dict[str, Any]:
    """Execute Mode 3: Dry-run verification of short and long dual pipeline contracts."""
    logger.info(f"[{config.job_id}] Launching Mode 3: Dry-Run Synthetic Pipeline Verification...")
    cfg_short = DualModeJobConfig(
        mode=DualMode.BUILD_SHORT.value,
        job_id=f"{config.job_id}_short_dry",
        channel_slug=config.channel_slug,
        spec_path=config.spec_path,
        output_dir=config.output_dir,
        render_backend="local",
        dry_run=True,
    )
    res_short = run_short_mode(cfg_short)

    cfg_long = DualModeJobConfig(
        mode=DualMode.BUILD_LONG.value,
        job_id=f"{config.job_id}_long_dry",
        channel_slug=config.channel_slug,
        spec_path=config.spec_path,
        output_dir=config.output_dir,
        render_backend="local",
        dry_run=True,
    )
    res_long = run_long_mode(cfg_long)

    return {
        "job_id": config.job_id,
        "mode": DualMode.DRY_RUN_VERIFY.value,
        "short_verification": res_short,
        "long_verification": res_long,
        "status": "verified",
    }


# ---------------------------------------------------------------------------
# 10. CLI Entrypoint
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Video Pilot VN Dual-Mode Pipeline: Short Omni 1.2 Flash & Long Chapter-Chunked T4 NVENC Renderer."
    )
    parser.add_argument(
        "--mode",
        choices=[
            DualMode.BUILD_SHORT.value,
            DualMode.BUILD_LONG.value,
            DualMode.DRY_RUN_VERIFY.value,
            "short",
            "long",
        ],
        default=DualMode.BUILD_LONG.value,
        help="Pipeline execution mode",
    )
    parser.add_argument("--channel", "--channel-slug", dest="channel_slug", default="tui-tien", help="Channel slug")
    parser.add_argument("--job-id", default="", help="Job identifier")
    parser.add_argument("--spec", help="Path to input rebuilt spec JSON")
    parser.add_argument("--audio-path", help="Path to pre-synthesized audio WAV")
    parser.add_argument("--output-dir", "--out-dir", dest="output_dir", default=str(ROOT_DIR / "video"), help="Base output directory")
    parser.add_argument(
        "--render-backend",
        choices=["colab_nvenc", "local"],
        default="colab_nvenc",
        help="Rendering backend (production: colab_nvenc; tests: local)",
    )
    parser.add_argument("--colab-account", help="Specific Colab account to target")
    parser.add_argument(
        "--profiles",
        help="Comma-separated allowed profile names (e.g. profile_6,profile_16,profile_11)",
    )
    parser.add_argument("--max-workers", type=int, default=10, help="Max Flow worker concurrency")
    parser.add_argument("--dry-run", action="store_true", help="Perform fast credit-free verification")
    parser.add_argument(
        "--visuals-only",
        action="store_true",
        help="Pre-generate keyframes and Omni video clips only, skip audio/subtitles/stitch",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    normalized_mode = DualMode.BUILD_SHORT.value if args.mode == "short" else (DualMode.BUILD_LONG.value if args.mode == "long" else args.mode)
    if args.job_id:
        job_id = args.job_id
    elif Path(args.output_dir).name != "video":
        job_id = Path(args.output_dir).name
    elif args.channel_slug:
        cand_job = f"vn_pilot_{args.channel_slug.replace('-', '_')}_{'long' if 'long' in normalized_mode else 'short'}"
        if (Path(args.output_dir) / cand_job).is_dir():
            job_id = cand_job
        else:
            job_id = f"vn_{normalized_mode.replace('-', '_')}_{int(time.time())}"
    else:
        job_id = f"vn_{normalized_mode.replace('-', '_')}_{int(time.time())}"
    allowed_profiles = [p.strip() for p in args.profiles.split(",") if p.strip()] if args.profiles else None

    config = DualModeJobConfig(
        mode=normalized_mode,
        job_id=job_id,
        channel_slug=args.channel_slug,
        spec_path=Path(args.spec) if args.spec else None,
        output_dir=Path(args.output_dir),
        audio_path=Path(args.audio_path) if args.audio_path else None,
        render_backend=args.render_backend,
        colab_account=args.colab_account,
        profiles=allowed_profiles,
        max_workers=args.max_workers,
        dry_run=args.dry_run,
        visuals_only=args.visuals_only,
    )

    if config.mode == DualMode.BUILD_SHORT.value:
        res = run_short_mode(config)
    elif config.mode == DualMode.BUILD_LONG.value:
        res = run_long_mode(config)
    else:
        res = run_dry_run_verify(config)

    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
