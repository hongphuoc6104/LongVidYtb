#!/usr/bin/env python3
"""Synthesize audio for survivorship-bias-16x9 Revision 9 (Ultra-Punchy Analytical Explainer v10) at -11.0 LUFS."""
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

import execution
from adapters import config
from colab_bridge.parallel_audio import synthesize
from colab_bridge.protocol import build_request
from format_profiles import audio_mastering_for_format, resolve_format_profile
from narration_pauses import plan_tracks
from pilot import Pilot, write

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("synthesize_ultra_punchy_v10")

RUN_DIR = SYS_DIR / "runs/survivorship-bias-16x9"
OUT_DIR = RUN_DIR / "revisions/audio/9_ultra_punchy_master"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    target_account = sys.argv[1] if len(sys.argv) > 1 else "account-02"
    target_session = sys.argv[2] if len(sys.argv) > 2 else "video-pilot-tts"

    logger.info(f"Initializing Pilot for audio synthesis on {target_account}:{target_session}...")
    p = Pilot(str(SYS_DIR))

    brief = json.loads((RUN_DIR / "briefs/8.json").read_text(encoding="utf-8"))
    content = json.loads((RUN_DIR / "revisions/content/9/content.json").read_text(encoding="utf-8"))
    logger.info(f"Loaded Brief 8 & Content 9: {len(content['scenes'])} scenes")

    cfg = config(p, "survivorship-bias-16x9")
    mastering = audio_mastering_for_format(resolve_format_profile(brief))
    logger.info(f"Mastering profile: {mastering}")
    cfg.update(mastering)
    cfg["audio_lufs"] = -11.0
    cfg["audio_peak_db"] = -1.0
    cfg.setdefault("colab_tts", {})["job_id"] = "survivorship-bias-16x9"

    selection = execution.settings(p, "survivorship-bias-16x9").get("management_session", {})
    from remote_audio import configure_accounts
    configure_accounts(cfg, selection)
    cfg["colab_tts"]["account"] = target_account
    cfg["colab_tts"]["session"] = target_session
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["parallel"] = False
    cfg["colab_tts"]["timeout_seconds"] = 900
    cfg["colab_tts"]["audio_estimate_seconds"] = 300

    # Use format_v1 pause policy
    scenes, secondary_segments, pause_plan = plan_tracks(brief, content, {}, "vi")
    logger.info(f"Planned tracks: {len(scenes)} scenes with format_v1 pauses")

    request = build_request(
        p.root,
        cfg,
        scenes,
        [],
        primary_language="vi",
        assemble=True,
        secondary_scenes=secondary_segments,
        pause_plan=pause_plan
    )

    req_path = OUT_DIR / "request-colab.json"
    write(req_path, request)
    logger.info(f"Built audio request with {len(request.get('items', []))} items and {len(request.get('segments', []))} segments")

    cache_dir = RUN_DIR / "cache/colab-tts"
    cache_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Submitting audio synthesis to Colab T4 pool on {target_account}...")
    synthesize(p.root, cfg, request, OUT_DIR, cache_dir)
    logger.info("Colab TTS synthesis completed!")

    res_file = OUT_DIR / "audio-result.json"
    if not res_file.is_file():
        raise RuntimeError(f"Missing {res_file}")

    data = json.loads(res_file.read_text(encoding="utf-8"))
    payload = data.get("payload", data)
    dur = payload.get("duration", 0)
    logger.info(f"Audio synthesized successfully! Duration: {dur:.2f}s")

    # Measure LUFS
    wav_file = OUT_DIR / "narration.wav"
    cmd = [
        "ffmpeg", "-i", str(wav_file),
        "-af", "ebur128=framelog=verbose",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    for line in res.stderr.split("\n"):
        if "Integrated loudness" in line or "I:" in line or "LRA:" in line or "Peak" in line:
            logger.info(f"[Loudness] {line}")

    def asset(name):
        return f"revisions/audio/9_ultra_punchy_master/{name}"

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

    content_file = RUN_DIR / "revisions/content/9/content.json"
    output_payload = {
        "schema_version": "1.0",
        "job_id": "survivorship-bias-16x9",
        "module": "audio",
        "revision": 9,
        "input_versions": {
            "content": hashlib.sha256(content_file.read_bytes()).hexdigest(),
        },
        "payload": payload,
    }

    out_json = OUT_DIR / "output.json"
    out_json.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Wrote output.json for audio revision 9 with duration {payload.get('duration')}s")

    symlink_path = RUN_DIR / "revisions/audio/9"
    if symlink_path.is_symlink() or symlink_path.exists():
        symlink_path.unlink()
    symlink_path.symlink_to("9_ultra_punchy_master")
    logger.info("Symlinked revisions/audio/9 -> 9_ultra_punchy_master")


if __name__ == "__main__":
    main()
