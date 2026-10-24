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
                 speed: float | None = None, mock: bool = False,
                 parallel: bool = True, max_workers: int = 3, batch_size: int = 4,
                 auto_teardown: bool = True, pool_manager: Any | None = None):
        self.content_path = Path(content_path)
        self.brief_path = Path(brief_path)
        self.out_dir = Path(out_dir)
        self.bgm_path = Path(bgm_path) if bgm_path else None
        self.mock = mock
        self.parallel = parallel
        self.max_workers = max(1, int(max_workers))
        self.batch_size = max(1, int(batch_size))
        self.auto_teardown = auto_teardown
        self.pool_manager = pool_manager
        self.last_teardown_report: dict[str, Any] | None = None
        self.used_accounts: list[str] = []

        self.content = read_json(self.content_path)
        self.brief = read_json(self.brief_path)
        self.voice = voice or self.brief.get("voice", "VietNarrator")
        self.speed = float(speed or self.brief.get("speed", 1.0))
        self.aspect_ratio = self.brief.get("aspect_ratio", "16:9")

    def _mastering_cfg(self) -> dict[str, float]:
        """Format-aware audio mastering config."""
        from format_profiles import audio_mastering_for_format, resolve_format_profile
        try:
            return audio_mastering_for_format(resolve_format_profile(self.brief))
        except Exception:
            cfg = read_json(SYS_ROOT / "config.json")
            return {
                "audio_lufs": float(cfg.get("audio_lufs", -11.0)),
                "audio_peak_db": float(cfg.get("audio_peak_db", -1.0)),
            }

    def _synthesize_segments_parallel(
        self,
        segments_plan: list[dict[str, Any]],
        seg_dir: Path,
    ) -> None:
        """Synthesize segments using multi-threaded parallel batch dispatch by default."""
        import concurrent.futures
        import copy
        import threading

        if self.mock:
            def _mock_one(seg: dict[str, Any]) -> str:
                wav_file = seg_dir / seg["wav_name"]
                words = len(seg["text"].split())
                dur = max(1.2, round(words * 0.35 + seg["pause"], 3))
                generate_mock_tone(wav_file, dur, freq=180.0 + (seg["index"] % 5) * 20.0)
                return seg["wav_name"]

            worker_threads = self.max_workers if self.parallel else 1
            with concurrent.futures.ThreadPoolExecutor(max_workers=worker_threads) as executor:
                list(executor.map(_mock_one, segments_plan))
            return

        from colab_bridge.client import Client
        from colab_bridge.pool_manager import ColabAccountWorker, ColabPoolDispatcher, ColabPoolManager
        from colab_bridge.protocol import build_request

        base_cfg = read_json(SYS_ROOT / "config.json")
        base_cfg["tts_voice"] = self.voice
        base_cfg["tts_speed"] = self.speed
        base_cfg["en_voice"] = self.voice
        base_cfg["en_speed"] = self.speed
        base_cfg.setdefault("colab_tts", {})["account"] = "auto-idle"
        base_cfg["colab_tts"]["batch_size"] = min(8, max(1, self.batch_size))

        batches: list[list[dict[str, Any]]] = [
            segments_plan[i : i + self.batch_size]
            for i in range(0, len(segments_plan), self.batch_size)
        ]
        tasks = [
            {
                "id": f"tts-batch-{b_idx:03d}",
                "batch_index": b_idx,
                "segments": batch,
            }
            for b_idx, batch in enumerate(batches)
        ]

        used_accounts: set[str] = set()
        used_lock = threading.Lock()

        def _exec_batch_on_worker(worker: ColabAccountWorker | None, task: dict[str, Any]) -> list[str]:
            batch_idx = int(task["batch_index"])
            batch_segs = task["segments"]
            batch_tmp = self.out_dir / "tmp_tts" / f"batch-{batch_idx:03d}"
            batch_cache = self.out_dir / "cache" / f"batch-{batch_idx:03d}"
            batch_tmp.mkdir(parents=True, exist_ok=True)
            batch_cache.mkdir(parents=True, exist_ok=True)

            cfg_copy = copy.deepcopy(base_cfg)
            if worker is not None:
                cfg_copy.setdefault("colab_tts", {})["account"] = worker.account_id
                cfg_copy["colab_tts"]["session"] = worker.session_name
                with used_lock:
                    used_accounts.add(worker.account_id)

            scene_specs = [
                {
                    "scene_id": f"{seg['scene_id']}_{seg['index']:03d}",
                    "narration": seg["text"],
                    "texts": [seg["text"]],
                    "gaps": [],
                    "tail": float(seg["pause"]),
                    "tone": seg.get("tone"),
                    "retake": 0,
                }
                for seg in batch_segs
            ]
            try:
                req = build_request(
                    SYS_ROOT,
                    cfg_copy,
                    scene_specs,
                    primary_language=self.brief.get("primary_language", "vi"),
                    assemble=False,
                )
            except Exception:
                req = {
                    "request_id": str(uuid.uuid4()),
                    "voice": self.voice,
                    "speed": self.speed,
                    "segments": batch_segs,
                }

            client = Client(SYS_ROOT, cfg_copy)
            client.synthesize(req, batch_tmp, batch_cache)

            tts_res_file = batch_tmp / "tts-result.json"
            tts_segments = read_json(tts_res_file).get("segments", []) if tts_res_file.is_file() else []
            moved: list[str] = []
            for local_idx, seg in enumerate(batch_segs):
                target_wav = seg_dir / seg["wav_name"]
                candidates = [
                    batch_tmp / seg["wav_name"],
                    batch_tmp / f"segment-{local_idx:04d}.wav",
                    batch_tmp / f"segment-{local_idx:03d}.wav",
                    batch_tmp / f"segment-{local_idx}.wav",
                ]
                if local_idx < len(tts_segments) and tts_segments[local_idx].get("path"):
                    candidates.insert(0, batch_tmp / tts_segments[local_idx]["path"])
                src_wav = next((c for c in candidates if c.is_file()), None)
                if src_wav is None:
                    raise AudioPipelineError(
                        f"Missing synthesized WAV for segment {seg['wav_name']} in {batch_tmp}"
                    )
                shutil.move(str(src_wav), str(target_wav))
                moved.append(seg["wav_name"])
            return moved

        pool_mgr = self.pool_manager or ColabPoolManager()
        concurrency = self.max_workers if self.parallel else 1
        try:
            if pool_mgr.workers and self.parallel:
                dispatcher = ColabPoolDispatcher(pool_mgr)
                dispatcher.dispatch_all(
                    tasks,
                    _exec_batch_on_worker,
                    max_concurrency=concurrency,
                    role="tts",
                )
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
                    futures = [pool.submit(_exec_batch_on_worker, None, t) for t in tasks]
                    for fut in futures:
                        fut.result()
        finally:
            self.used_accounts = sorted(used_accounts)
            shutil.rmtree(self.out_dir / "tmp_tts", ignore_errors=True)
            if self.auto_teardown and used_accounts:
                self.last_teardown_report = pool_mgr.teardown_job_resources(
                    account_ids=sorted(used_accounts),
                    close_chrome=False,
                )

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
                scene["narration_normalized"] = normalize_for_tts(raw_text, preserve_pauses=True)
            if "narration_en" in scene:
                scene["narration_en_normalized"] = scene["narration_en"]

        # 2. Cadence and syllable auditing
        checker = ScriptCadenceChecker(
            forbid_opening_pause=True,
            max_opening_hook_syllables=18,
            max_clause_syllables=18,
        )
        cadence_res = checker.check_scenes(scenes)
        cadence_log = self.out_dir / "cadence_audit.json"
        write_json(cadence_log, cadence_res)
        all_warnings: list[str] = []
        for sc in cadence_res.get("scenes", []):
            all_warnings.extend(sc.get("warnings", []))
        critical_cadence_tags = (
            "OPENING_SCENE_PAUSE_FORBIDDEN",
            "OPENING_HOOK_TOO_LONG",
            "RATE_TOO_FAST",
            "RATE_TOO_SLOW",
            "DEAD_AIR",
        )
        for w in all_warnings:
            if any(tag in w for tag in critical_cadence_tags):
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
                clean_chunk = chunk_text.lstrip(", ").strip()
                if not clean_chunk:
                    continue
                pause_sec = gaps[c_idx] if c_idx < len(gaps) else cfg["tts_pause"]["minor"]
                segments_plan.append({
                    "index": global_idx,
                    "scene_id": scene_id,
                    "text": clean_chunk,
                    "pause": pause_sec,
                    "tone": tone,
                    "wav_name": f"segment-{global_idx:03d}.wav",
                })
                global_idx += 1

        # 4. Voice Synthesis (Default Multi-Threaded Parallel Dispatch across Colab T4 Pool or Mock)
        seg_dir = self.out_dir / "segments"
        seg_dir.mkdir(exist_ok=True)

        self._synthesize_segments_parallel(segments_plan, seg_dir)

        cursor = 0.0
        final_segments: list[dict[str, Any]] = []

        for seg in segments_plan:
            wav_file = seg_dir / seg["wav_name"]

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
            except Exception:
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
    run_parser.add_argument("--max-workers", type=int, default=3, help="Max concurrent T4 account workers (default: 3)")
    run_parser.add_argument("--batch-size", type=int, default=4, help="Segments per remote batch (default: 4)")
    run_parser.add_argument("--no-parallel", action="store_true", help="Disable default multi-threaded parallel dispatch")

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
            parallel=not args.no_parallel,
            max_workers=args.max_workers,
            batch_size=args.batch_size,
        )
        result = pipeline.run()
        print("✅ Audio pipeline completed successfully!")
        print(f"Duration: {result['total_duration']:.2f}s | Segments: {len(result['segments'])}")
        print(f"Master: {result['master_wav']} | SRT: {result['subtitles']}")


if __name__ == "__main__":
    main()
