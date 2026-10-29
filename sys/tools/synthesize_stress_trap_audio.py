#!/usr/bin/env python3
"""Synthesize audio for Stress Trap Paradox packages (16:9 or 9:16) via remote Colab T4 OmniVoice at -11.0 LUFS / -1.0 dBTP."""
import argparse
import hashlib
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from adapters import config
from colab_bridge.client import Client
from colab_bridge.protocol import build_request
from format_profiles import audio_mastering_for_format, resolve_format_profile
from narration_pauses import plan_tracks

from pilot import Pilot, write

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("synthesize_stress_trap_audio")


def synthesize_job(job_name: str, target_account: str = "account-01", target_session: str = "video-pilot-tts") -> dict:
    run_dir = SYS_DIR / "runs" / job_name
    out_dir = run_dir / "revisions/audio/1"
    cache_dir = run_dir / "cache/colab-tts"
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading package files for {job_name}...")
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((run_dir / "content.json").read_text(encoding="utf-8"))

    p = Pilot(str(SYS_DIR))
    cfg = config(p, job_name)
    cfg.update(audio_mastering_for_format(resolve_format_profile(brief)))
    cfg["audio_lufs"] = -11.0
    cfg["audio_peak_db"] = -1.0
    cfg["tts_voice"] = "VietNarrator"
    cfg["tts_speed"] = 1.0
    cfg.setdefault("colab_tts", {})["job_id"] = job_name
    cfg["colab_tts"]["account"] = target_account
    cfg["colab_tts"]["session"] = target_session
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["timeout_seconds"] = 1800
    cfg["colab_tts"]["audio_estimate_seconds"] = 600

    logger.info(f"Planning narration tracks with format_v1 pauses ({len(content['scenes'])} scenes)...")
    scenes, secondary_segments, pause_plan = plan_tracks(brief, content, {}, "vi")

    logger.info("Building canonical Colab TTS request...")
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
    logger.info(f"Built request {request['request_id']} with {len(request.get('items', []))} items and {len(request.get('segments', []))} segments")

    logger.info(f"Connecting to Colab T4 on {target_account}:{target_session}...")
    client = Client(p.root, cfg)
    client.account = target_account
    client.session = target_session

    logger.info("Submitting audio synthesis & remote assembly...")
    client.synthesize(request, out_dir, cache_dir)
    logger.info("Colab TTS synthesis completed successfully!")

    res_file = out_dir / "audio-result.json"
    if not res_file.is_file():
        raise RuntimeError(f"Missing {res_file}")

    data = json.loads(res_file.read_text(encoding="utf-8"))
    payload = data.get("payload", data)
    dur = payload.get("duration", 0)
    logger.info(f"Audio synthesized successfully! Measured Duration: {dur:.2f}s")

    # Measure LUFS with ffmpeg
    wav_file = out_dir / "narration.wav"
    cmd = [
        "ffmpeg", "-i", str(wav_file),
        "-af", "ebur128=framelog=verbose",
        "-f", "null", "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    measured_lufs = None
    measured_peak = None
    for line in res.stderr.split("\n"):
        if "I:" in line and "LUFS" in line:
            logger.info(f"Loudness: {line.strip()}")
            try:
                parts = line.strip().split()
                measured_lufs = float(parts[1])
            except Exception:
                pass
        if "Peak:" in line and "dBFS" in line:
            logger.info(f"True Peak: {line.strip()}")
            try:
                parts = line.strip().split()
                measured_peak = float(parts[1])
            except Exception:
                pass

    def asset(name):
        return f"revisions/audio/1/{name}"

    payload["wav"] = asset("narration.wav")
    payload["srt"] = asset("subtitles.srt")
    payload["generation_report"] = asset("tts-result.json")

    for track in payload.get("tracks", {}).values():
        track["wav"] = asset("narration.wav")
        track["srt"] = asset("subtitles.srt")
        track["generation_report"] = asset("tts-result.json")
        for seg in track.get("segments", []):
            if "path" in seg:
                seg["path"] = asset(Path(seg["path"]).name)

    for seg in payload.get("segments", []):
        if "path" in seg:
            seg["path"] = asset(Path(seg["path"]).name)

    # Write output.json in revisions/audio/1
    out_json = out_dir / "output.json"
    content_hash = hashlib.sha256((run_dir / "content.json").read_bytes()).hexdigest()
    output_contract = {
        "schema_version": "1.0",
        "job_id": job_name,
        "module": "audio",
        "revision": 1,
        "input_versions": {
            "content": content_hash,
        },
        "files": [
            asset("narration.wav"),
            asset("subtitles.srt"),
            asset("tts-result.json"),
            asset("audio-result.json"),
        ],
        "payload": payload,
    }
    out_json.write_text(json.dumps(output_contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Wrote output.json for audio revision 1 with duration {dur:.2f}s")

    # Sync main artifacts to run_dir root for convenience
    shutil.copy2(out_dir / "narration.wav", run_dir / "narration.wav")
    shutil.copy2(out_dir / "subtitles.srt", run_dir / "subtitles.srt")
    shutil.copy2(out_dir / "output.json", run_dir / "output.json")
    logger.info(f"Synced narration.wav, subtitles.srt, output.json to {run_dir}")

    return {
        "job": job_name,
        "duration": dur,
        "measured_lufs": measured_lufs,
        "measured_peak_db": measured_peak,
        "wav": str(out_dir / "narration.wav"),
        "srt": str(out_dir / "subtitles.srt"),
        "output_json": str(out_json),
    }


def main():
    parser = argparse.ArgumentParser(description="Synthesize Stress Trap Paradox OmniVoice TTS Audio on Colab T4")
    parser.add_argument("job", nargs="?", default="both", choices=["stress-trap-paradox-16x9", "stress-trap-paradox-9x16", "both"], help="Job identifier")
    parser.add_argument("--job", dest="job_opt", choices=["stress-trap-paradox-16x9", "stress-trap-paradox-9x16", "both"], help="Job identifier")
    parser.add_argument("--account", default="account-01", help="Target Colab account")
    parser.add_argument("--session", default="video-pilot-tts", help="Colab session name")
    args = parser.parse_args()

    job_choice = args.job_opt or args.job
    jobs = ["stress-trap-paradox-9x16", "stress-trap-paradox-16x9"] if job_choice == "both" else [job_choice]

    for j in jobs:
        print("\n" + "=" * 60)
        print(f"[*] BẮT ĐẦU TỔNG HỢP ÂM THANH CHO: {j}")
        print("=" * 60)
        res = synthesize_job(j, target_account=args.account, target_session=args.session)
        print("\n" + "=" * 60)
        print(f"[SUCCESS] Audio synthesis for {j} completed!")
        print(f"  - Duration: {res['duration']:.2f}s")
        print(f"  - LUFS: {res['measured_lufs']}")
        print(f"  - Peak: {res['measured_peak_db']} dB")
        print(f"  - WAV: {res['wav']}")
        print(f"  - SRT: {res['srt']}")
        print("=" * 60)


if __name__ == "__main__":
    main()
