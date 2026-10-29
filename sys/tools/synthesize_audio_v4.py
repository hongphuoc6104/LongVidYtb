#!/usr/bin/env python3
"""Synthesize audio for survivorship-bias-16x9 revision 3 using Colab T4 pool."""
from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from adapters import DEFAULT_PAUSE
from colab_bridge.protocol import build_request
from colab_bridge.parallel_audio import synthesize
from format_profiles import audio_mastering_for_format, resolve_format_profile
from pilot import Pilot
from remote_audio import primary_scene_request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("synthesize_audio_v4")

RUN_DIR = SYS_DIR / "runs/survivorship-bias-16x9"
OUT_DIR = RUN_DIR / "revisions/audio/3_v4_master"
CACHE_DIR = RUN_DIR / "cache/colab-tts"
CONTENT_FILE = RUN_DIR / "revisions/content/3/content.json"
BRIEF_FILE = RUN_DIR / "briefs/3.json"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    pilot = Pilot()
    brief = json.loads(BRIEF_FILE.read_text(encoding="utf-8"))
    content = json.loads(CONTENT_FILE.read_text(encoding="utf-8"))
    cfg = json.loads((SYS_DIR / "config.json").read_text(encoding="utf-8"))

    cfg.update(audio_mastering_for_format(resolve_format_profile(brief)))
    cfg["audio_lufs"] = -11.0
    cfg["audio_peak_db"] = -1.0
    cfg.setdefault("colab_tts", {})["job_id"] = "survivorship-bias-16x9"
    cfg["colab_tts"]["max_workers"] = 2
    cfg["colab_tts"]["management_session"] = {"pool": ["colab:account-01", "colab:account-03"]}
    cfg["tts_voice"] = "VietNarrator"
    cfg["tts_speed"] = 1.0

    scenes = []
    for i, scene in enumerate(content["scenes"]):
        text = scene["narration"]
        item = primary_scene_request(scene, text, "vi", DEFAULT_PAUSE, 0, i == len(content["scenes"]) - 1)
        scenes.append(item)

    logger.info(f"Building request for {len(scenes)} scenes...")
    request = build_request(pilot.root, cfg, scenes, [], primary_language="vi", assemble=True)
    request["assembly_settings"] = {"audio_lufs": -11.0, "audio_peak_db": -1.0}

    req_file = OUT_DIR / "request-colab.json"
    req_file.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Built request {request['request_id']} with {len(request['items'])} items")

    logger.info("Executing parallel synthesis on Colab T4 pool...")
    synthesize(pilot.root, cfg, request, OUT_DIR, CACHE_DIR)
    logger.info("Synthesis and assembly completed!")

    report_file = OUT_DIR / "audio-result.json"
    if not report_file.is_file():
        raise RuntimeError("audio-result.json not found in output directory")

    report = json.loads(report_file.read_text(encoding="utf-8"))
    payload = report["payload"]

    def asset(name):
        return f"revisions/audio/3_v4_master/{name}"

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

    output_payload = {
        "schema_version": "1.0",
        "job_id": "survivorship-bias-16x9",
        "module": "audio",
        "revision": 3,
        "input_versions": {
            "content": hashlib.sha256(CONTENT_FILE.read_bytes()).hexdigest(),
        },
        "payload": payload,
    }

    (OUT_DIR / "output.json").write_text(json.dumps(output_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Wrote output.json for revision 3 with duration {payload.get('duration')}s")


if __name__ == "__main__":
    main()
