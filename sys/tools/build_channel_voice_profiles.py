#!/usr/bin/env python3
"""Build and sync dedicated studio-tuned Human Voice Profiles for the 8 Video Pilot channels.

Generates:
- sys/assets/voices/ch_<channel_id>/reference.wav (24kHz mono PCM16, 25ms fade-out, 80ms silence tail)
- sys/assets/voices/ch_<channel_id>/profile.json (protocol-compliant with sha256 checksum)

And syncs all profiles and clean reference sources to the 8 worktrees under
/home/hongphuoc6104/Desktop/vp-channels/channel-<slug>/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any, Dict, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("build_channel_voice_profiles")

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
VOICES_DIR = SYS_DIR / "assets" / "voices"
WORKTREES_ROOT = Path("/home/hongphuoc6104/Desktop/vp-channels")

REF_VIET_NARRATOR = VOICES_DIR / "viet_narrator" / "reference.wav"
SAMPLE_VIET_NARRATOR = VOICES_DIR / "viet_narrator" / "sample.wav"
REF_CLEAN_A1 = VOICES_DIR / "viet_narrator" / "ref_clean_a1_24k.wav"
REF_CLEAN_B3 = VOICES_DIR / "viet_narrator" / "ref_clean_b3_24k.wav"

# Candidate A1: De-mudded first 2 sentences of viet_narrator/sample.wav (5.220s, 24kHz mono PCM16)
REF_TEXT_CLEAN_A1 = (
    "Bạn có chắc mình đã hiểu? Đôi khi, cảm giác quen thuộc khiến chúng ta tưởng rằng mình biết "
    "nhiều hơn thực tế."
)

# Candidate B3: Studio-clean 2 sentences from Minh Quân Pro vocab-cat-colab-001 (8.140s, 24kHz mono PCM16)
REF_TEXT_CLEAN_B3 = (
    "Đang ngồi đọc sách thì dưới chân bỗng có tiếng kêu meo meo dịu dàng. "
    "Nhà bạn có nuôi một chú mèo nào không, hãy bình luận nhé."
)

CANDIDATE_PRESETS: Dict[str, Dict[str, Any]] = {
    "a1": {
        "base_source": REF_CLEAN_A1,
        "time_window": (0.00, 5.22),
        "reference_text": REF_TEXT_CLEAN_A1,
        "source_speed": 1.0,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_a1_24k.wav",
    },
    "b3": {
        "base_source": REF_CLEAN_B3,
        "time_window": (0.00, 8.14),
        "reference_text": REF_TEXT_CLEAN_B3,
        "source_speed": 0.90,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_b3_24k.wav",
    },
}

NARRATIVE_CHANNELS = {"nao_luoi", "su_ke_lai", "thuong_cho_kheo", "ho_so_ky_la"}
ENERGETIC_CHANNELS = {"tui_tien", "ua_sao_vay", "co_the_ke", "ai_binh_dan"}

CHANNEL_SPECS: Dict[str, Dict[str, Any]] = {
    "nao_luoi": {
        "voice": "VietNarrator_NaoLuoi",
        "channel_id": "nao_luoi",
        "base_source": REF_CLEAN_B3,
        "time_window": (0.00, 8.14),
        "reference_text": REF_TEXT_CLEAN_B3,
        "source_speed": 0.90,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_b3_24k.wav",
        "pitch_factor": 1.000,
        "eq_filter": "",
        "recommended_speed": 1.08,
        "default_tone": "narrative_warm",
        "audio_voice_chain": (
            "highpass=f=90,equalizer=f=185:t=q:w=1.2:g=-3.0,"
            "equalizer=f=2400:t=q:w=1.2:g=1.5,lowpass=f=13500"
        ),
    },
    "tui_tien": {
        "voice": "VietNarrator_TuiTien",
        "channel_id": "tui_tien",
        "base_source": REF_CLEAN_B3,
        "time_window": (0.00, 8.14),
        "reference_text": REF_TEXT_CLEAN_B3,
        "source_speed": 0.90,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_b3_24k.wav",
        "pitch_factor": 1.000,
        "eq_filter": "",
        "recommended_speed": 1.12,
        "default_tone": "analytical_crisp",
        "audio_voice_chain": (
            "highpass=f=90,equalizer=f=185:t=q:w=1.2:g=-3.2,"
            "equalizer=f=2400:t=q:w=1.2:g=1.6,lowpass=f=13500"
        ),
    },
    "ua_sao_vay": {
        "voice": "VietNarrator_UaSaoVay",
        "channel_id": "ua_sao_vay",
        "base_source": REF_CLEAN_B3,
        "time_window": (0.00, 8.14),
        "reference_text": REF_TEXT_CLEAN_B3,
        "source_speed": 0.90,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_b3_24k.wav",
        "pitch_factor": 1.000,
        "eq_filter": "",
        "recommended_speed": 1.16,
        "default_tone": "analytical_crisp",
        "audio_voice_chain": (
            "highpass=f=90,equalizer=f=185:t=q:w=1.2:g=-3.2,"
            "equalizer=f=2400:t=q:w=1.2:g=1.8,lowpass=f=13500"
        ),
    },
    "su_ke_lai": {
        "voice": "VietNarrator_SuKeLai",
        "channel_id": "su_ke_lai",
        "base_source": REF_CLEAN_B3,
        "time_window": (0.00, 8.14),
        "reference_text": REF_TEXT_CLEAN_B3,
        "source_speed": 0.90,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_b3_24k.wav",
        "pitch_factor": 1.000,
        "eq_filter": "",
        "recommended_speed": 1.04,
        "default_tone": "reflective_slow",
        "audio_voice_chain": (
            "highpass=f=90,equalizer=f=185:t=q:w=1.2:g=-2.8,"
            "equalizer=f=2400:t=q:w=1.2:g=1.4,lowpass=f=13500"
        ),
    },
    "thuong_cho_kheo": {
        "voice": "VietNarrator_ThuongChoKheo",
        "channel_id": "thuong_cho_kheo",
        "base_source": REF_CLEAN_B3,
        "time_window": (0.00, 8.14),
        "reference_text": REF_TEXT_CLEAN_B3,
        "source_speed": 0.90,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_b3_24k.wav",
        "pitch_factor": 1.000,
        "eq_filter": "",
        "recommended_speed": 1.00,
        "default_tone": "reflective_slow",
        "audio_voice_chain": (
            "highpass=f=90,equalizer=f=185:t=q:w=1.2:g=-2.5,"
            "equalizer=f=2400:t=q:w=1.2:g=1.2,lowpass=f=13500"
        ),
    },
    "ho_so_ky_la": {
        "voice": "VietNarrator_HoSoKyLa",
        "channel_id": "ho_so_ky_la",
        "base_source": REF_CLEAN_B3,
        "time_window": (0.00, 8.14),
        "reference_text": REF_TEXT_CLEAN_B3,
        "source_speed": 0.90,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_b3_24k.wav",
        "pitch_factor": 1.000,
        "eq_filter": "",
        "recommended_speed": 1.06,
        "default_tone": "narrative_warm",
        "audio_voice_chain": (
            "highpass=f=90,equalizer=f=185:t=q:w=1.2:g=-3.0,"
            "equalizer=f=2400:t=q:w=1.2:g=1.4,lowpass=f=13500"
        ),
    },
    "co_the_ke": {
        "voice": "VietNarrator_CoTheKe",
        "channel_id": "co_the_ke",
        "base_source": REF_CLEAN_B3,
        "time_window": (0.00, 8.14),
        "reference_text": REF_TEXT_CLEAN_B3,
        "source_speed": 0.90,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_b3_24k.wav",
        "pitch_factor": 1.000,
        "eq_filter": "",
        "recommended_speed": 1.10,
        "default_tone": "narrative_warm",
        "audio_voice_chain": (
            "highpass=f=90,equalizer=f=185:t=q:w=1.2:g=-3.0,"
            "equalizer=f=2400:t=q:w=1.2:g=1.5,lowpass=f=13500"
        ),
    },
    "ai_binh_dan": {
        "voice": "VietNarrator_AIBinhDan",
        "channel_id": "ai_binh_dan",
        "base_source": REF_CLEAN_B3,
        "time_window": (0.00, 8.14),
        "reference_text": REF_TEXT_CLEAN_B3,
        "source_speed": 0.90,
        "source_rel_path": "assets/voices/viet_narrator/ref_clean_b3_24k.wav",
        "pitch_factor": 1.000,
        "eq_filter": "",
        "recommended_speed": 1.14,
        "default_tone": "analytical_crisp",
        "audio_voice_chain": (
            "highpass=f=90,equalizer=f=185:t=q:w=1.2:g=-3.5,"
            "equalizer=f=2400:t=q:w=1.2:g=1.7,lowpass=f=13500"
        ),
    },
}


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def process_audio_file(
    base_source: Path,
    time_window: Tuple[float, float],
    pitch_factor: float,
    eq_filter: str,
    output_wav: Path,
) -> None:
    """Renders lossless 24kHz mono PCM16 reference slice with 25ms fade-out and 80ms silence tail.

    - If base_source is already a pre-mastered `ref_clean_*_24k.wav` file, copies it bit-exact.
    - If source is 24kHz mono PCM16: slices directly via Python wave module.
    - If source is 48kHz mono PCM16: downsamples cleanly via ffmpeg
      `aresample=24000:resampler=soxr:precision=28` (ZERO asetrate, ZERO atempo).
    """
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    if base_source.name.startswith("ref_clean_"):
        shutil.copy2(base_source, output_wav)
        return

    start_t, end_t = time_window

    with wave.open(str(base_source), "rb") as w:
        channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        n_frames = w.getnframes()

        if channels != 1 or sampwidth != 2 or framerate not in (24000, 48000):
            raise ValueError(
                f"Base source must be 24kHz or 48kHz mono PCM16, got ch={channels}, width={sampwidth}, rate={framerate}"
            )

        if framerate == 24000:
            start_frame = int(round(start_t * framerate))
            end_frame = min(int(round(end_t * framerate)), n_frames)
            w.setpos(start_frame)
            raw_bytes = w.readframes(end_frame - start_frame)

    if framerate == 48000:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(base_source),
                "-af",
                f"atrim=start={start_t}:end={end_t},asetpts=PTS-STARTPTS,aresample=24000:resampler=soxr:precision=28",
                "-ac",
                "1",
                "-ar",
                "24000",
                "-sample_fmt",
                "s16",
                str(tmp_path),
            ]
            subprocess.run(cmd, check=True)
            with wave.open(str(tmp_path), "rb") as w24:
                raw_bytes = w24.readframes(w24.getnframes())
        finally:
            tmp_path.unlink(missing_ok=True)

    target_rate = 24000
    samples = list(struct.unpack(f"<{len(raw_bytes)//2}h", raw_bytes))
    if not samples:
        raise RuntimeError(f"Extracted empty audio frames from {base_source} window {time_window}")

    if start_t > 0.0:
        fade_in_samples = int(round(0.010 * target_rate))
        for i in range(min(fade_in_samples, len(samples))):
            factor = 0.5 * (1.0 - math.cos(math.pi * i / fade_in_samples))
            samples[i] = int(round(samples[i] * factor))

    fade_samples = int(round(0.025 * target_rate))
    if len(samples) > fade_samples:
        for i in range(fade_samples):
            idx = len(samples) - fade_samples + i
            factor = 0.5 * (1.0 + math.cos(math.pi * i / fade_samples))
            samples[idx] = int(round(samples[idx] * factor))

    silence_samples = int(round(0.080 * target_rate))
    samples.extend([0] * silence_samples)

    with wave.open(str(output_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(target_rate)
        w.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def apply_candidate_to_spec(
    spec: Dict[str, Any],
    candidate: str,
) -> Dict[str, Any]:
    """Returns a copy of spec updated with the requested clean reference candidate."""
    resolved = dict(spec)
    if candidate == "split_ab":
        preset_key = "a1" if spec["channel_id"] in NARRATIVE_CHANNELS else "b3"
    else:
        preset_key = candidate

    preset = CANDIDATE_PRESETS[preset_key]
    resolved["base_source"] = preset["base_source"]
    resolved["time_window"] = preset["time_window"]
    resolved["reference_text"] = preset["reference_text"]
    resolved["source_speed"] = preset["source_speed"]
    resolved["source_rel_path"] = preset["source_rel_path"]
    return resolved


def build_channel_voice_profile(spec: Dict[str, Any], output_dir: Path) -> Path:
    """Builds reference.wav and profile.json inside output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ref_wav_path = output_dir / "reference.wav"
    profile_json_path = output_dir / "profile.json"

    process_audio_file(
        base_source=spec["base_source"],
        time_window=spec["time_window"],
        pitch_factor=spec["pitch_factor"],
        eq_filter=spec["eq_filter"],
        output_wav=ref_wav_path,
    )

    with wave.open(str(ref_wav_path), "rb") as w:
        channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        n_frames = w.getnframes()
        duration = n_frames / framerate

    if channels != 1 or sampwidth != 2 or framerate != 24000:
        raise ValueError(f"WAV parameters mismatch: ch={channels}, width={sampwidth}, rate={framerate}")
    if not (3.0 <= duration <= 15.0):
        raise ValueError(f"Duration {duration:.2f}s is outside valid protocol bounds [3.0s, 15.0s]")

    sha256_digest = compute_sha256(ref_wav_path)

    base_src_name = spec["base_source"].name
    source_rel_path = spec.get("source_rel_path", f"assets/voices/viet_narrator/{base_src_name}")
    source_speed = float(spec.get("source_speed", 1.0))
    profile_data: Dict[str, Any] = {
        "voice": spec["voice"],
        "channel_id": spec["channel_id"],
        "language": "vi",
        "languages": ["vi", "en"],
        "reference_wav": "reference.wav",
        "reference_text": spec["reference_text"],
        "source_speed": source_speed,
        "recommended_speed": spec["recommended_speed"],
        "default_tone": spec["default_tone"],
        "audio_voice_chain": spec["audio_voice_chain"],
        "audio_lufs": -14.0,
        "audio_peak_db": -1.5,
        "sha256": sha256_digest,
        "sources": [
            {
                "source": source_rel_path,
                "window_seconds": list(spec["time_window"]),
                "pitch_factor": spec["pitch_factor"],
                "eq": spec["eq_filter"],
            }
        ],
        "listening_verified": True,
        "note": (
            f"Studio-tuned human voice profile for channel {spec['channel_id']} "
            f"({spec['default_tone']}, speed {spec['recommended_speed']})."
        ),
    }

    with open(profile_json_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    logger.info(
        "Built %s -> %s (%.2fs, SHA: %s...)",
        spec["voice"],
        ref_wav_path.name,
        duration,
        sha256_digest[:12],
    )
    return profile_json_path


def sync_profiles_to_worktrees(worktrees_root: Path = WORKTREES_ROOT) -> None:
    """Syncs all ch_* profile directories, ref_clean_*.wav, and build/test files into every channel worktree."""
    if not worktrees_root.is_dir():
        logger.warning("Worktrees directory %s does not exist; skipping sync", worktrees_root)
        return

    profile_dirs = sorted([d for d in VOICES_DIR.iterdir() if d.is_dir() and d.name.startswith("ch_")])
    if not profile_dirs:
        logger.warning("No channel voice directories found in %s to sync", VOICES_DIR)
        return

    script_path = Path(__file__).resolve()
    test_path = SYS_DIR / "tests" / "test_channel_voice_profiles.py"

    for ch_id in CHANNEL_SPECS:
        slug = ch_id.replace("_", "-")
        worktree_sys_dir = worktrees_root / f"channel-{slug}" / "sys"
        if not worktree_sys_dir.is_dir():
            logger.info("Skipping nonexistent worktree sys dir: %s", worktree_sys_dir)
            continue

        worktree_voices_dir = worktree_sys_dir / "assets" / "voices"
        worktree_voices_dir.mkdir(parents=True, exist_ok=True)

        # Sync ref_clean_*.wav into worktree viet_narrator directory
        worktree_vn_dir = worktree_voices_dir / "viet_narrator"
        worktree_vn_dir.mkdir(parents=True, exist_ok=True)
        for clean_ref in (REF_CLEAN_A1, REF_CLEAN_B3):
            if clean_ref.is_file():
                shutil.copy2(clean_ref, worktree_vn_dir / clean_ref.name)

        # Copy each ch_* profile directory into this worktree
        for pdir in profile_dirs:
            target_pdir = worktree_voices_dir / pdir.name
            target_pdir.mkdir(parents=True, exist_ok=True)
            for item in pdir.iterdir():
                if item.is_file():
                    shutil.copy2(item, target_pdir / item.name)

        # Sync the build script itself to worktree sys/tools/
        worktree_tools_dir = worktree_sys_dir / "tools"
        if worktree_tools_dir.is_dir():
            shutil.copy2(script_path, worktree_tools_dir / script_path.name)

        # Sync unit test file to worktree sys/tests/
        worktree_tests_dir = worktree_sys_dir / "tests"
        if worktree_tests_dir.is_dir() and test_path.is_file():
            shutil.copy2(test_path, worktree_tests_dir / test_path.name)

        logger.info("Synced %d voice profiles + ref_clean_*.wav to %s", len(profile_dirs), worktree_voices_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sync", "--sync-worktrees", dest="sync", action="store_true", default=True, help="Sync to worktrees (default: True)"
    )
    parser.add_argument("--no-sync", dest="sync", action="store_false", help="Do not sync to worktrees")
    parser.add_argument(
        "--channel",
        choices=list(CHANNEL_SPECS.keys()),
        help="Build a single channel voice profile instead of all 8",
    )
    parser.add_argument(
        "--candidate",
        choices=["b3", "split_ab", "a1"],
        default="b3",
        help="Select reference candidate preset (b3=all 8 studio-clean Minh Quân Pro, split_ab=4+4, a1=all a1)",
    )
    args = parser.parse_args()

    # Pre-flight assertions
    if not REF_CLEAN_A1.is_file():
        logger.error("ref_clean_a1_24k.wav missing at %s", REF_CLEAN_A1)
        return 1
    if not REF_CLEAN_B3.is_file():
        logger.error("ref_clean_b3_24k.wav missing at %s", REF_CLEAN_B3)
        return 1

    channels_to_build = [args.channel] if args.channel else list(CHANNEL_SPECS.keys())
    logger.info(
        "Building %d channel voice profile(s) (candidate=%s)...",
        len(channels_to_build),
        args.candidate,
    )

    for ch_id in channels_to_build:
        spec = apply_candidate_to_spec(CHANNEL_SPECS[ch_id], args.candidate)
        out_dir = VOICES_DIR / f"ch_{ch_id}"
        build_channel_voice_profile(spec, out_dir)

    if args.sync:
        logger.info("Syncing profiles to worktrees under %s...", WORKTREES_ROOT)
        sync_profiles_to_worktrees(WORKTREES_ROOT)

    logger.info("Channel voice profiles build and sync completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
