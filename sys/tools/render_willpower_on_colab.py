#!/usr/bin/env python3
"""Execute remote Colab T4 render for Willpower Paradox packages (9:16 or 16:9)."""
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
logger = logging.getLogger("render_willpower_on_colab")


def render_job(job_name: str, target_account: str = "account-01", target_session: str = "video-pilot-tts") -> dict:
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
    cfg["colab_tts"]["account"] = target_account
    cfg["colab_tts"]["session"] = target_session
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["render_timeout_seconds"] = 5400

    client = Client(SYS_DIR, cfg)
    client.account = target_account
    client.session = target_session

    logger.info(f"Submitting render request to Colab {client.account} ({client.session})...")
    client.render(request, out_dir, cache_dir)
    logger.info("Remote render extraction completed!")

    res_path = out_dir / "render-result.json"
    if not res_path.is_file():
        raise RuntimeError("render-result.json missing after extraction")

    result = json.loads(res_path.read_text(encoding="utf-8"))
    logger.info(f"Render completed on device: {result.get('device')}, elapsed: {result.get('elapsed_seconds')}s")

    is_9x16 = "9x16" in job_name
    video_mp4 = out_dir / "video.mp4"
    named_mp4 = out_dir / ("video_9x16.mp4" if is_9x16 else "video_16x9.mp4")

    source_mp4 = named_mp4 if named_mp4.is_file() else video_mp4
    if not source_mp4.is_file():
        raise RuntimeError(f"No rendered video file found in {out_dir}")

    # Copy to delivery directory
    deliv_mp4 = video_deliv_dir / ("video_9x16.mp4" if is_9x16 else "video_16x9.mp4")
    deliv_named_mp4 = video_deliv_dir / f"{job_name}.mp4"
    shutil.copy2(source_mp4, deliv_mp4)
    shutil.copy2(source_mp4, deliv_named_mp4)

    # Deliver SRT
    srt_src = run_dir / "revisions/audio/1/subtitles.srt"
    if not srt_src.is_file():
        srt_src = run_dir / "subtitles.srt"
    if srt_src.is_file():
        shutil.copy2(srt_src, video_deliv_dir / "subtitles.srt")
        shutil.copy2(srt_src, video_deliv_dir / f"{job_name}.srt")

    # Deliver Thumbnail
    thumb_src = run_dir / f"thumbnail_{'9x16' if is_9x16 else '16x9'}.jpg"
    if not thumb_src.is_file():
        thumb_src = run_dir / f"revisions/images/1/THUMBNAIL_{'9x16' if is_9x16 else '16x9'}.jpg"
    if thumb_src.is_file():
        shutil.copy2(thumb_src, video_deliv_dir / f"thumbnail_{'9x16' if is_9x16 else '16x9'}.jpg")
        shutil.copy2(thumb_src, video_deliv_dir / f"{job_name}.jpg")

    # Run ffprobe validation
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_streams", "-show_format",
        "-of", "json",
        str(deliv_mp4),
    ]
    probe_data = json.loads(subprocess.check_output(probe_cmd, text=True))
    video_stream = next(s for s in probe_data["streams"] if s["codec_type"] == "video")
    audio_stream = next(s for s in probe_data["streams"] if s["codec_type"] == "audio")

    width = int(video_stream["width"])
    height = int(video_stream["height"])
    v_codec = video_stream["codec_name"]
    a_codec = audio_stream["codec_name"]
    duration = float(probe_data["format"]["duration"])
    fps_eval = eval(video_stream.get("avg_frame_rate", "30/1"))
    size_mb = deliv_mp4.stat().st_size / (1024 * 1024)

    logger.info("================ FFPROBE VALIDATION ================")
    logger.info(f"File: {deliv_mp4}")
    logger.info(f"Resolution: {width}x{height} (expected {'1080x1920' if is_9x16 else '1920x1080'})")
    logger.info(f"FPS: {fps_eval:.2f} (expected 30.00)")
    logger.info(f"Video Codec: {v_codec}, Audio Codec: {a_codec}")
    logger.info(f"Duration: {duration:.2f}s, File Size: {size_mb:.2f} MB")
    logger.info("====================================================")

    # Write output.json for render revision
    output_manifest = {
        "schema_version": "1.0",
        "job_id": job_name,
        "module": "render",
        "revision": 1,
        "input_versions": {
            "content": hashlib.sha256((run_dir / "content.json").read_bytes()).hexdigest(),
            "images": hashlib.sha256((run_dir / "revisions/images/1/output.json").read_bytes()).hexdigest(),
            "audio": hashlib.sha256((run_dir / "revisions/audio/1/output.json").read_bytes()).hexdigest(),
        },
        "payload": {
            "video": f"video/{job_name}/video_{'9x16' if is_9x16 else '16x9'}.mp4",
            "duration": duration,
            "resolution": f"{width}x{height}",
            "fps": fps_eval,
            "video_codec": v_codec,
            "audio_codec": a_codec,
            "size_mb": size_mb,
            "remote_report": str(res_path.relative_to(run_dir)),
        },
    }
    (out_dir / "output.json").write_text(json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "job": job_name,
        "video_path": str(deliv_mp4),
        "duration": duration,
        "resolution": f"{width}x{height}",
        "fps": fps_eval,
        "v_codec": v_codec,
        "a_codec": a_codec,
        "size_mb": size_mb,
    }


def main():
    parser = argparse.ArgumentParser(description="Render Willpower Paradox Video on Colab T4")
    parser.add_argument("job", nargs="?", default=None, choices=["willpower-paradox-9x16", "willpower-paradox-16x9"], help="Job identifier")
    parser.add_argument("--job", dest="job_opt", choices=["willpower-paradox-9x16", "willpower-paradox-16x9"], help="Job identifier")
    parser.add_argument("--account", default="account-01", help="Target Colab account")
    parser.add_argument("--session", default="video-pilot-tts", help="Colab session name")
    args = parser.parse_args()

    job_name = args.job_opt or args.job
    if not job_name:
        parser.error("Job identifier is required (either positional or via --job)")

    res = render_job(job_name, target_account=args.account, target_session=args.session)
    print("\n" + "=" * 60)
    print(f"[SUCCESS] Remote Colab T4 render for {job_name} completed!")
    print(f"  - Output Video: {res['video_path']}")
    print(f"  - Resolution:   {res['resolution']}")
    print(f"  - Duration:     {res['duration']:.2f}s")
    print(f"  - FPS:          {res['fps']:.2f}")
    print(f"  - Codecs:       {res['v_codec']} / {res['a_codec']}")
    print(f"  - Size:         {res['size_mb']:.2f} MB")
    print("=" * 60)


if __name__ == "__main__":
    main()
