#!/usr/bin/env python3
"""Execute remote Colab T4 render for Research Topic Size packages (16:9 or 9:16)."""
from __future__ import annotations

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

from colab_bridge.client import Client
from colab_bridge.job_protocol import build_render_request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("render_research_topic_on_colab")


def render_job(job_name: str, target_account: str = "account-08", target_session: str = "video-pilot-tts") -> dict:
    run_dir = SYS_DIR / "runs" / job_name
    out_dir = run_dir / "revisions/render/1"
    cache_dir = run_dir / "cache/colab-render"
    video_deliv_dir = ROOT / "video" / job_name

    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    video_deliv_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading inputs for {job_name} render on {target_account}:{target_session}...")
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    content = json.loads((run_dir / "content.json").read_text(encoding="utf-8"))
    images = json.loads((run_dir / "revisions/images/1/images.json").read_text(encoding="utf-8"))
    audio_out = json.loads((run_dir / "revisions/audio/1/output.json").read_text(encoding="utf-8"))
    audio = audio_out.get("payload", audio_out)

    def resolve_path(rel_path):
        p = run_dir / rel_path
        if p.is_file():
            return p
        p2 = run_dir / "revisions" / rel_path
        if p2.is_file():
            return p2
        p3 = SYS_DIR / rel_path
        if p3.is_file():
            return p3
        raise FileNotFoundError(f"Cannot resolve path: {rel_path}")

    logger.info("Building render request...")
    request = build_render_request(SYS_DIR, brief, content, images, audio, resolve_path)
    req_file = out_dir / "request-colab-render.json"
    req_file.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Built request {request['request_id']} with {len(request['files'])} files")

    cfg = json.loads((SYS_DIR / "config.json").read_text(encoding="utf-8"))
    is_9x16 = "9x16" in job_name
    cfg["colab_tts"]["account"] = target_account
    cfg["colab_tts"]["session"] = target_session
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["render_timeout_seconds"] = 5400
    cfg["colab_tts"]["render_estimate_seconds"] = 300 if is_9x16 else 1200

    client = Client(SYS_DIR, cfg)
    client.account = target_account
    client.session = target_session

    logger.info("Submitting render to Colab T4...")
    client.render(request, out_dir, cache_dir)
    logger.info("Colab render completed successfully!")

    video_mp4 = out_dir / "video.mp4"
    named_mp4 = out_dir / ("video_9x16.mp4" if is_9x16 else "video_16x9.mp4")
    source_mp4 = named_mp4 if named_mp4.is_file() else video_mp4

    if not source_mp4.is_file():
        raise RuntimeError(f"Render completed but {source_mp4} is missing!")

    # Verify MP4 with ffprobe
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=width,height,codec_name",
        "-of", "json", str(source_mp4),
    ]
    probe = subprocess.run(cmd, capture_output=True, text=True, check=True)
    probe_data = json.loads(probe.stdout)
    logger.info(f"ffprobe verification: {probe_data}")

    # Copy deliverables to video/job_name/
    final_mp4 = video_deliv_dir / f"{job_name}.mp4"
    final_srt = video_deliv_dir / f"{job_name}.srt"
    shutil.copy2(source_mp4, final_mp4)

    srt_source = out_dir / "subtitles.srt"
    if not srt_source.is_file():
        srt_source = run_dir / "revisions/audio/1_master/subtitles.srt"
    if srt_source.is_file():
        shutil.copy2(srt_source, final_srt)

    # Save output.json
    output_manifest = {
        "schema_version": "1.0",
        "job_id": job_name,
        "module": "render",
        "revision": 1,
        "video": str(final_mp4.relative_to(ROOT)),
        "subtitles": str(final_srt.relative_to(ROOT)) if final_srt.is_file() else None,
        "ffprobe": probe_data,
    }
    (out_dir / "output.json").write_text(json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Deliverables copied to {video_deliv_dir} and output.json recorded.")
    return output_manifest


def main():
    parser = argparse.ArgumentParser(description="Render Research Topic Size packages on Colab T4")
    parser.add_argument("job", nargs="?", default="research-topic-size-9x16", choices=["research-topic-size-16x9", "research-topic-size-9x16"], help="Job to render")
    parser.add_argument("--account", default="account-08", help="Target Colab account")
    parser.add_argument("--session", default="video-pilot-tts", help="Target Colab session")
    args = parser.parse_args()

    render_job(args.job, target_account=args.account, target_session=args.session)


if __name__ == "__main__":
    main()
