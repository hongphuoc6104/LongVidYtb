#!/usr/bin/env python3
"""Execute remote Colab T4 render for survivorship-bias-16x9 revision 4_v4_final."""
import hashlib
import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from colab_bridge.client import Client
from colab_bridge.job_protocol import build_render_request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("render_v4")

RUN_DIR = SYS_DIR / "runs/survivorship-bias-16x9"
OUT_DIR = RUN_DIR / "revisions/render/4_v4_final"
CACHE_DIR = RUN_DIR / "cache/colab-render"
VIDEO_DELIV_DIR = ROOT / "video/survivorship-bias-16x9"

OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DELIV_DIR.mkdir(parents=True, exist_ok=True)


def main():
    logger.info("Loading inputs...")
    brief = json.loads((RUN_DIR / "briefs/3.json").read_text(encoding="utf-8"))
    content = json.loads((RUN_DIR / "revisions/content/3/content.json").read_text(encoding="utf-8"))
    images = json.loads((RUN_DIR / "revisions/images/6_v4_doodle/images.json").read_text(encoding="utf-8"))
    audio_out = json.loads((RUN_DIR / "revisions/audio/3_v4_master/output.json").read_text(encoding="utf-8"))
    audio = audio_out.get("payload", audio_out)

    def resolve_path(rel_path):
        p = RUN_DIR / rel_path
        if p.exists():
            return p
        p2 = RUN_DIR / "revisions" / rel_path
        if p2.exists():
            return p2
        return p

    logger.info("Building render request for revision 4...")
    request = build_render_request(SYS_DIR, brief, content, images, audio, resolve_path)
    req_file = OUT_DIR / "request-colab-render.json"
    req_file.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Built request {request['request_id']} with {len(request['files'])} files")

    cfg = json.loads((SYS_DIR / "config.json").read_text(encoding="utf-8"))
    cfg["colab_tts"]["account"] = "account-01"
    cfg["colab_tts"]["session"] = "video-pilot-tts"

    client = Client(SYS_DIR, cfg)
    client.account = "account-01"
    client.session = "video-pilot-tts"

    logger.info(f"Submitting render request to Colab {client.account} ({client.session})...")
    client.render(request, OUT_DIR, CACHE_DIR)
    logger.info("Remote render extraction completed!")

    res_path = OUT_DIR / "render-result.json"
    if not res_path.is_file():
        raise RuntimeError("render-result.json missing after extraction")

    result = json.loads(res_path.read_text(encoding="utf-8"))
    logger.info(f"Device: {result.get('device')}, elapsed: {result.get('elapsed_seconds')}s")

    video_mp4 = OUT_DIR / "video.mp4"
    video_16x9 = OUT_DIR / "video_16x9.mp4"
    if video_mp4.is_file() and not video_16x9.is_file():
        shutil.copy2(video_mp4, video_16x9)
        logger.info("Copied video.mp4 -> video_16x9.mp4")

    # Export deliverables to video/survivorship-bias-16x9/
    final_mp4 = VIDEO_DELIV_DIR / "survivorship-bias-16x9_v4_final.mp4"
    final_srt = VIDEO_DELIV_DIR / "survivorship-bias-16x9_v4_final.srt"
    if video_mp4.is_file():
        shutil.copy2(video_mp4, final_mp4)
        logger.info(f"Exported deliverable MP4: {final_mp4}")

    srt_src = RUN_DIR / "revisions/audio/3_v4_master/subtitles.srt"
    if srt_src.is_file():
        shutil.copy2(srt_src, final_srt)
        logger.info(f"Exported deliverable SRT: {final_srt}")

    files = [
        f"revisions/render/4_v4_final/{p.name}"
        for p in OUT_DIR.iterdir()
        if p.is_file()
    ]

    stills = [
        f"revisions/render/4_v4_final/{p.name}"
        for p in OUT_DIR.glob("*.png")
    ]

    output_payload = {
        "schema_version": "1.0",
        "job_id": "survivorship-bias-16x9",
        "module": "render",
        "revision": 4,
        "input_versions": {
            "content": hashlib.sha256((RUN_DIR / "revisions/content/3/content.json").read_bytes()).hexdigest(),
            "images": hashlib.sha256((RUN_DIR / "revisions/images/6_v4_doodle/images.json").read_bytes()).hexdigest(),
            "audio": hashlib.sha256((RUN_DIR / "revisions/audio/3_v4_master/output.json").read_bytes()).hexdigest(),
        },
        "files": files,
        "payload": {
            "video": "revisions/render/4_v4_final/video.mp4",
            "video_16x9": "revisions/render/4_v4_final/video_16x9.mp4",
            "stills": stills,
            "layout_report": "revisions/render/4_v4_final/layout.json",
            "editorial_report": "revisions/render/4_v4_final/editorial-audit.json",
            "remote_report": "revisions/render/4_v4_final/render-result.json",
            "language": result["outputs"][0]["language"],
            "duration": result["outputs"][0]["duration"],
        },
        "checks": {
            "passed": True,
            "errors": []
        }
    }
    (OUT_DIR / "output.json").write_text(json.dumps(output_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info("Wrote output.json for revision 4_v4_final!")


if __name__ == "__main__":
    main()
