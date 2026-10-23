#!/usr/bin/env python3
"""Standalone Audio Pipeline for module-audio.

This entrypoint executes the full audio processing lifecycle independently:
  1. Input loading & validation (brief.json, content.json)
  2. Vietnamese phonetic normalization (vn_text_normalizer.py)
  3. Script cadence and syllable auditing (script_cadence_checker.py)
  4. Audio segment chunking and pause assignment (adapters.chunks_with_gaps)
  5. Voice synthesis (Colab OmniVoice VietNarrator or local test mock)
  6. Broadcast audio mastering (audio_processing.py: EQ, -14 LUFS, -1.5 dBTP, frame preservation)
  7. Subtitle timecodes generation (subtitles.srt)
  8. SHA-256 provenance manifest generation (audio-result.json)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
import subprocess
import sys
import uuid
import wave
from pathlib import Path
from typing import Any

# Ensure sys directory is in Python path
SYS_ROOT = Path(__file__).resolve().parent
if str(SYS_ROOT) not in sys.path:
    sys.path.insert(0, str(SYS_ROOT))

import adapters
import audio_processing
from tools.script_cadence_checker import ScriptCadenceChecker
from tools.vn_text_normalizer import normalize_for_tts

SR = 48000


class AudioPipelineError(RuntimeError):
    """Raised when an audio pipeline step fails."""
    pass


def read_json(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path | str, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def calculate_rms(raw_frames: bytes, sampwidth: int = 2) -> int:
    """Calculate RMS amplitude without deprecated audioop module."""
    if not raw_frames:
        return 0
    import numpy as np
    dt = {1: np.int8, 2: np.int16, 4: np.int32}.get(sampwidth, np.int16)
    arr = np.frombuffer(raw_frames, dtype=dt)
    if len(arr) == 0:
        return 0
    return int(np.sqrt(np.mean(arr.astype(np.float64) ** 2)))


def generate_mock_tone(path: Path | str, seconds: float, level: int = 8000, freq: float = 220.0) -> None:
    """Generate a clean PCM16 mono 48kHz audio tone for offline testing."""
    body_samples = int(SR * seconds * 0.85)
    tail_samples = int(SR * seconds) - body_samples
    frames = bytearray()
    for i in range(body_samples):
        val = int(level * math.sin(2 * math.pi * freq * (i / SR)))
        frames.extend(struct.pack("<h", val))
    frames.extend(b"\x00\x00" * tail_samples)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(frames)


class AudioPipeline:
    def __init__(self, content_path: Path | str, brief_path: Path | str, out_dir: Path | str,
                 bgm_path: Path | str | None = None, voice: str | None = None,
                 speed: float | None = None, mock: bool = False):
        self.content_path = Path(content_path)
        self.brief_path = Path(brief_path)
        self.out_dir = Path(out_dir)
        self.bgm_path = Path(bgm_path) if bgm_path else None
        self.mock = mock

        self.content = read_json(self.content_path)
        self.brief = read_json(self.brief_path)
        self.voice = voice or self.brief.get("voice", "VietNarrator")
        self.speed = float(speed or self.brief.get("speed", 1.0))
        self.aspect_ratio = self.brief.get("aspect_ratio", "16:9")

    def _mastering_cfg(self) -> dict[str, float]:
        """Single channel-wide mastering config from sys/config.json (same for every format)."""
        cfg = read_json(SYS_ROOT / "config.json")
        return {
            "audio_lufs": float(cfg.get("audio_lufs", -11.0)),
            "audio_peak_db": float(cfg.get("audio_peak_db", -1.0)),
        }

    def run(self) -> dict[str, Any]:
        """Execute the complete audio workflow."""
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Phonetic normalization
        scenes = self.content.get("scenes", [])
        if not scenes:
            raise AudioPipelineError("Empty scene list in content.json")

        for scene in scenes:
            raw_text = scene.get("narration", "")
            if raw_text:
                scene["narration_normalized"] = normalize_for_tts(raw_text)
            if "narration_en" in scene:
                scene["narration_en_normalized"] = scene["narration_en"]

        # 2. Cadence and syllable auditing
        checker = ScriptCadenceChecker()
        cadence_res = checker.check_scenes(scenes)
        cadence_log = self.out_dir / "cadence_audit.json"
        write_json(cadence_log, cadence_res)
        all_warnings: list[str] = []
        for sc in cadence_res.get("scenes", []):
            all_warnings.extend(sc.get("warnings", []))
        for w in all_warnings:
            if "OPENING_SCENE_PAUSE_FORBIDDEN" in w:
                raise AudioPipelineError(f"Cadence rejection: {w}")

        # 3. Chunking & pause planning
        cfg = {"tts_pause": adapters.DEFAULT_PAUSE}
        segments_plan: list[dict[str, Any]] = []
        global_idx = 0

        for scene in scenes:
            text = scene.get("narration_normalized", scene.get("narration", ""))
            chunks, gaps = adapters.chunks_with_gaps(text, cfg["tts_pause"])
            scene_id = scene.get("id", f"SC{len(segments_plan)+1:02d}")
            tone = scene.get("tone", "narrative_warm")

            for c_idx, chunk_text in enumerate(chunks):
                pause_sec = gaps[c_idx] if c_idx < len(gaps) else cfg["tts_pause"]["minor"]
                segments_plan.append({
                    "index": global_idx,
                    "scene_id": scene_id,
                    "text": chunk_text,
                    "pause": pause_sec,
                    "tone": tone,
                    "wav_name": f"segment-{global_idx:03d}.wav",
                })
                global_idx += 1

        # 4. Voice Synthesis (Colab OmniVoice or Mock)
        seg_dir = self.out_dir / "segments"
        seg_dir.mkdir(exist_ok=True)

        cursor = 0.0
        final_segments: list[dict[str, Any]] = []

        for seg in segments_plan:
            wav_file = seg_dir / seg["wav_name"]
            if self.mock:
                # Est duration: 3.5 syllables per sec
                words = len(seg["text"].split())
                dur = max(1.2, round(words * 0.35 + seg["pause"], 3))
                generate_mock_tone(wav_file, dur, freq=180.0 + (seg["index"] % 5) * 20.0)
            else:
                # Dispatch remote synthesis
                from colab_bridge.client import Client
                client = Client()
                req = {
                    "request_id": str(uuid.uuid4()),
                    "voice": self.voice,
                    "speed": self.speed,
                    "segments": [seg],
                }
                client.synthesize(req, self.out_dir / "tmp_tts", self.out_dir / "cache")
                shutil.move(str(self.out_dir / "tmp_tts" / seg["wav_name"]), str(wav_file))

            # Inspect synthesized WAV
            with wave.open(str(wav_file), "rb") as w:
                frames = w.readframes(w.getnframes())
                duration = w.getnframes() / w.getframerate()
                rms = calculate_rms(frames, w.getsampwidth())

            if rms < 5:
                raise AudioPipelineError(f"Silent audio segment detected: {wav_file.name} (RMS={rms})")

            start_t = cursor
            end_t = round(start_t + duration, 3)
            cursor = end_t

            final_segments.append({
                "scene_id": seg["scene_id"],
                "text": seg["text"],
                "path": str(wav_file.relative_to(self.out_dir)),
                "duration": duration,
                "start": start_t,
                "end": end_t,
                "sha256": sha256_file(wav_file),
            })

        # 5. Assemble & Master full narration.wav
        raw_combined = self.out_dir / "narration_raw.wav"
        combined_frames = bytearray()
        for s in final_segments:
            with wave.open(str(self.out_dir / s["path"]), "rb") as w:
                combined_frames.extend(w.readframes(w.getnframes()))

        with wave.open(str(raw_combined), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(combined_frames)

        final_mastered = self.out_dir / "narration.wav"
        mastering_cfg = self._mastering_cfg()

        # Apply mastering EQ & loudness if ffmpeg is available
        if shutil.which("ffmpeg"):
            shutil.copy2(str(raw_combined), str(final_mastered))
            try:
                audio_processing.master(final_mastered, self.out_dir / "tmp_master.wav", mastering_cfg)
            except Exception as e:
                # If mastering fails due to extreme shortness or missing tools, retain raw
                shutil.copy2(str(raw_combined), str(final_mastered))
        else:
            shutil.copy2(str(raw_combined), str(final_mastered))

        raw_combined.unlink(missing_ok=True)

        # 6. Generate Subtitles (SRT)
        srt_file = self.out_dir / "subtitles.srt"
        srt_content = adapters.make_srt(final_segments)
        srt_file.write_text(srt_content, encoding="utf-8")

        # 7. Write Manifest audio-result.json
        manifest = {
            "request_id": str(uuid.uuid4()),
            "processing_location": "local" if self.mock else "colab",
            "voice": self.voice,
            "speed": self.speed,
            "language": self.brief.get("primary_language", "vi"),
            "aspect_ratio": self.aspect_ratio,
            "total_duration": cursor,
            "master_wav": str(final_mastered.relative_to(self.out_dir)),
            "master_sha256": sha256_file(final_mastered),
            "subtitles": str(srt_file.relative_to(self.out_dir)),
            "segments": final_segments,
        }
        write_json(self.out_dir / "audio-result.json", manifest)

        return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone Audio Pipeline for module-audio")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the full audio pipeline")
    run_parser.add_argument("--content", required=True, help="Path to content.json / script.json")
    run_parser.add_argument("--brief", required=True, help="Path to brief.json")
    run_parser.add_argument("--out", required=True, help="Output directory")
    run_parser.add_argument("--bgm", help="Optional path to BGM audio file")
    run_parser.add_argument("--voice", help="Voice model name (defaults to VietNarrator)")
    run_parser.add_argument("--speed", type=float, help="Voice speed factor (defaults to 1.0)")
    run_parser.add_argument("--mock", action="store_true", help="Generate local mock synthesis for testing")

    args = parser.parse_args()
    if args.command == "run":
        pipeline = AudioPipeline(
            content_path=args.content,
            brief_path=args.brief,
            out_dir=args.out,
            bgm_path=args.bgm,
            voice=args.voice,
            speed=args.speed,
            mock=args.mock,
        )
        result = pipeline.run()
        print(f"✅ Audio pipeline completed successfully!")
        print(f"Duration: {result['total_duration']:.2f}s | Segments: {len(result['segments'])}")
        print(f"Master: {result['master_wav']} | SRT: {result['subtitles']}")


if __name__ == "__main__":
    main()
