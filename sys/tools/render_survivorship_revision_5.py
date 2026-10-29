#!/usr/bin/env python3
"""Execute remote Colab T4 render for survivorship-bias-16x9 revision 5_final."""
import hashlib
import json
import logging
import os
import shutil
import subprocess
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
logger = logging.getLogger("render_revision_5")

RUN_DIR = SYS_DIR / "runs/survivorship-bias-16x9"
OUT_DIR = RUN_DIR / "revisions/render/5_final"
CACHE_DIR = RUN_DIR / "cache/colab-render"
VIDEO_DELIV_DIR = ROOT / "video/survivorship-bias-16x9"

OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DELIV_DIR.mkdir(parents=True, exist_ok=True)


def main():
    logger.info("Loading inputs for revision 5 render...")
    brief = json.loads((RUN_DIR / "briefs/4.json").read_text(encoding="utf-8"))
    content = json.loads((RUN_DIR / "revisions/content/4/content.json").read_text(encoding="utf-8"))
    images = json.loads((RUN_DIR / "revisions/images/7_new_doodle/images.json").read_text(encoding="utf-8"))
    audio_out = json.loads((RUN_DIR / "revisions/audio/4_final_audio/output.json").read_text(encoding="utf-8"))
    audio = audio_out.get("payload", audio_out)

    def resolve_path(rel_path):
        p = RUN_DIR / rel_path
        if p.exists():
            return p
        p2 = RUN_DIR / "revisions" / rel_path
        if p2.exists():
            return p2
        return p

    logger.info("Building render request for revision 5...")
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
    final_mp4 = VIDEO_DELIV_DIR / "survivorship-bias-16x9_v5_final.mp4"
    final_srt = VIDEO_DELIV_DIR / "survivorship-bias-16x9_v5_final.srt"
    std_mp4 = VIDEO_DELIV_DIR / "video_16x9.mp4"
    std_srt = VIDEO_DELIV_DIR / "subtitles.srt"

    if video_mp4.is_file():
        shutil.copy2(video_mp4, final_mp4)
        shutil.copy2(video_mp4, std_mp4)
        logger.info(f"Exported deliverable MP4: {final_mp4} and {std_mp4}")

    srt_src = RUN_DIR / "revisions/audio/4_final_audio/subtitles.srt"
    if srt_src.is_file():
        shutil.copy2(srt_src, final_srt)
        shutil.copy2(srt_src, std_srt)
        logger.info(f"Exported deliverable SRT: {final_srt} and {std_srt}")

    # Export thumbnail
    thumb_src = RUN_DIR / "revisions/images/7_new_doodle/THUMBNAIL_16x9.jpg"
    if thumb_src.is_file():
        shutil.copy2(thumb_src, VIDEO_DELIV_DIR / "THUMBNAIL_16x9.jpg")
        shutil.copy2(thumb_src, VIDEO_DELIV_DIR / "thumbnail_16x9.jpg")
        logger.info("Exported thumbnail deliverable.")

    files = [
        f"revisions/render/5_final/{p.name}"
        for p in OUT_DIR.iterdir()
        if p.is_file()
    ]

    stills = [
        f"revisions/render/5_final/{p.name}"
        for p in (OUT_DIR / "stills").iterdir()
        if (OUT_DIR / "stills").is_dir() and p.is_file()
    ]

    output_manifest = {
        "schema_version": "1.0",
        "job_id": "survivorship-bias-16x9",
        "module": "render",
        "revision": 5,
        "input_versions": {
            "content": hashlib.sha256((RUN_DIR / "revisions/content/4/content.json").read_bytes()).hexdigest(),
            "images": hashlib.sha256((RUN_DIR / "revisions/images/7_new_doodle/images.json").read_bytes()).hexdigest(),
            "audio": hashlib.sha256((RUN_DIR / "revisions/audio/4_final_audio/output.json").read_bytes()).hexdigest(),
        },
        "files": files + stills,
        "payload": {
            "schema_version": "2.0",
            "checkpoint": "final",
            "video": "revisions/render/5_final/video.mp4",
            "video_16x9": "revisions/render/5_final/video_16x9.mp4",
            "generation_report": "revisions/render/5_final/render-result.json",
            "stills": stills,
        },
    }

    (OUT_DIR / "output.json").write_text(json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Symlink 5 -> 5_final
    symlink_path = RUN_DIR / "revisions/render/5"
    if symlink_path.is_symlink() or symlink_path.exists():
        symlink_path.unlink()
    symlink_path.symlink_to("5_final")
    logger.info("Symlinked revisions/render/5 -> 5_final")


if __name__ == "__main__":
    main()
