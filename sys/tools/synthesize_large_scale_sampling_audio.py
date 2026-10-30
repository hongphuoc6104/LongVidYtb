#!/usr/bin/env python3
"""Synthesize audio for large-scale-sampling-16x9 and 9x16 packages via Colab T4 OmniVoice.

Calibrates to -11.0 LUFS / -1.0 dBTP with clean VietNarrator 1.0x narration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from adapters import config
from colab_bridge.parallel_audio import synthesize
from colab_bridge.protocol import build_request
from format_profiles import audio_mastering_for_format, resolve_format_profile
from narration_pauses import plan_tracks
from pilot import Pilot, write

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("synthesize_large_scale_sampling_audio")


def synthesize_for_job(job_name: str, target_account: str = "account-01", target_session: str = "video-pilot-tts"):
    run_dir = SYS_DIR / "runs" / job_name
    out_dir = run_dir / "revisions/audio/1_master"
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"--- Synthesizing Audio for {job_name} on {target_account}:{target_session} ---")
    p = Pilot(str(SYS_DIR))

    brief_path = run_dir / "brief.json"
    content_path = run_dir / "content.json"
    if not brief_path.is_file() or not content_path.is_file():
        raise FileNotFoundError(f"Missing brief or content for {job_name}")

    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    content = json.loads(content_path.read_text(encoding="utf-8"))
    logger.info(f"Loaded Brief & Content: {len(content['scenes'])} scenes")

    cfg = config(p, job_name)
    mastering = audio_mastering_for_format(resolve_format_profile(brief))
    cfg.update(mastering)
    cfg["audio_lufs"] = -11.0
    cfg["audio_peak_db"] = -1.0
    cfg.setdefault("colab_tts", {})["job_id"] = job_name

    cfg["colab_tts"]["account"] = target_account
    cfg["colab_tts"]["session"] = target_session
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["parallel"] = False
    cfg["colab_tts"]["timeout_seconds"] = 1200
    cfg["colab_tts"]["audio_estimate_seconds"] = int(content.get("duration", {}).get("max_seconds", 540))

    scenes, secondary_segments, pause_plan = plan_tracks(brief, content, {}, "vi")
    logger.info(f"Planned tracks: {len(scenes)} scenes with pause plan")

    request = build_request(
        p.root,
        cfg,
        scenes,
        [],
        primary_language="vi",
        assemble=True,
        secondary_scenes=secondary_segments,
        pause_plan=pause_plan,
    )

    req_path = out_dir / "request-colab.json"
    write(req_path, request)
    logger.info(f"Built request with {len(request.get('items', []))} items and {len(request.get('segments', []))} segments")

    cache_dir = run_dir / "cache/colab-tts"
    cache_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Submitting audio synthesis to Colab T4 pool on {target_account}...")
    synthesize(p.root, cfg, request, out_dir, cache_dir)
    logger.info("Colab TTS synthesis completed!")

    res_file = out_dir / "audio-result.json"
    if not res_file.is_file():
        raise RuntimeError(f"Missing {res_file}")

    data = json.loads(res_file.read_text(encoding="utf-8"))
    payload = data.get("payload", data)
    dur = payload.get("duration", 0)
    logger.info(f"Audio synthesized successfully for {job_name}! Measured duration: {dur:.2f}s")

    # Measure LUFS
    wav_file = out_dir / "narration.wav"
    if wav_file.is_file():
        cmd = [
            "ffmpeg", "-i", str(wav_file),
            "-af", "ebur128=framelog=verbose",
            "-f", "null", "-",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        for line in res.stderr.split("\n"):
            if "Integrated loudness" in line or "I:" in line or "LRA:" in line or "Peak" in line:
                logger.info(f"[Loudness] {line}")

    def asset(name):
        return f"revisions/audio/1_master/{name}"

    payload["wav"] = asset("narration.wav")
    payload["srt"] = asset("subtitles.srt")
    payload["generation_report"] = asset("tts-result.json")

    for track in payload.get("tracks", {}).values():
        track["wav"] = asset("narration.wav")
        track["srt"] = asset("subtitles.srt")
        track["generation_report"] = asset("tts-result.json")

    for seg in payload.get("segments", []):
        if "path" in seg:
            seg["path"] = asset(Path(seg["path"]).name)

    output_payload = {
        "schema_version": "1.0",
        "job_id": job_name,
        "module": "audio",
        "revision": 1,
        "input_versions": {
            "content": hashlib.sha256(content_path.read_bytes()).hexdigest(),
        },
        "payload": payload,
    }

    out_json = out_dir / "output.json"
    out_json.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Wrote output.json for {job_name} audio rev 1")

    rev_dir = run_dir / "revisions/audio/1"
    if rev_dir.is_symlink() or rev_dir.exists():
        rev_dir.unlink()
    rev_dir.symlink_to("1_master")
    logger.info("Symlinked revisions/audio/1 -> 1_master")


def main():
    parser = argparse.ArgumentParser(description="Synthesize audio for large-scale sampling jobs")
    parser.add_argument("--ratio", choices=["16:9", "9:16", "dual"], default="9:16", help="Ratio to synthesize")
    parser.add_argument("--account", default="account-01", help="Target Google account")
    parser.add_argument("--session", default="video-pilot-tts", help="Target Colab session")
    args = parser.parse_args()

    jobs = []
    if args.ratio in ("9:16", "dual"):
        jobs.append("large-scale-sampling-9x16")
    if args.ratio in ("16:9", "dual"):
        jobs.append("large-scale-sampling-16x9")

    for j in jobs:
        synthesize_for_job(j, target_account=args.account, target_session=args.session)


if __name__ == "__main__":
    main()
