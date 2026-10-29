#!/usr/bin/env python3
import json
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
from colab_bridge.job_protocol import bundle, extract, validate_render_result

JOB_NAME = "willpower-paradox-16x9"
RUN_DIR = SYS_DIR / "runs" / JOB_NAME
OUT_DIR = RUN_DIR / "revisions/render/1"
CACHE_DIR = RUN_DIR / "cache/colab-render"
REQ_ID = "56236c64f12614a7e7149912737906f106c0d99fea6091c02aa89803d6b5fff6"
REMOTE = f"/content/video-pilot-jobs/{REQ_ID}"
TARGET_ACCOUNT = "account-01"
TARGET_SESSION = "video-pilot-tts"
PYTHON_CLI = "/home/hongphuoc6104/.local/share/uv/tools/google-colab-cli/bin/python"
ACCOUNT_CLI = str(SYS_DIR / "colab_bridge/account_cli.py")
PROFILE_DIR = Path.home() / f".config/video-pilot/colab/profiles/{TARGET_ACCOUNT}"
CACHE_FOLDER = CACHE_DIR / REQ_ID
OUTPUT_ZIP = CACHE_FOLDER / "output.zip"

def try_download():
    # Attempt download without touching client state
    tmp_dest = CACHE_FOLDER / "output_downloading.tmp"
    cmd = [
        PYTHON_CLI,
        ACCOUNT_CLI,
        str(PROFILE_DIR),
        "download",
        "-s",
        TARGET_SESSION,
        f"{REMOTE}/output.zip",
        str(tmp_dest),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if res.returncode == 0 and tmp_dest.is_file() and tmp_dest.stat().st_size > 1000:
        tmp_dest.replace(OUTPUT_ZIP)
        return True
    if tmp_dest.exists():
        tmp_dest.unlink()
    return False

def main():
    print(f"Waiting for Colab render {REQ_ID} on {TARGET_ACCOUNT}:{TARGET_SESSION}...")
    start_wait = time.time()
    max_wait = 2400

    while time.time() - start_wait < max_wait:
        print(f"[{time.strftime('%X')}] Checking if output.zip is ready on Colab...", flush=True)
        if try_download():
            print(f"[{time.strftime('%X')}] Successfully downloaded output.zip ({OUTPUT_ZIP.stat().st_size} bytes)!", flush=True)
            break
        time.sleep(20)
    else:
        print("Timed out waiting for output.zip", flush=True)
        sys.exit(1)

    # Now that output.zip is safely in place, use Client to validate and finish!
    cfg = json.loads((SYS_DIR / "config.json").read_text(encoding="utf-8"))
    cfg["colab_tts"]["account"] = TARGET_ACCOUNT
    cfg["colab_tts"]["session"] = TARGET_SESSION
    cfg["colab_tts"]["_session_explicit"] = True

    client = Client(SYS_DIR, cfg)
    client.account = TARGET_ACCOUNT
    client.session = TARGET_SESSION

    req_file = OUT_DIR / "request-colab-render.json"
    request = json.loads(req_file.read_text(encoding="utf-8"))

    result_folder = CACHE_FOLDER / "result"
    result_folder.mkdir(parents=True, exist_ok=True)
    extract(OUTPUT_ZIP, result_folder, flat=True)
    names = validate_render_result(result_folder, request)
    for name in names:
        shutil.copy2(result_folder / name, OUT_DIR / name)

    # Copy deliverables to video/willpower-paradox-16x9/
    video_deliv_dir = ROOT / "video" / JOB_NAME
    video_deliv_dir.mkdir(parents=True, exist_ok=True)

    source_mp4 = OUT_DIR / "video_16x9.mp4"
    if not source_mp4.is_file():
        source_mp4 = OUT_DIR / "video.mp4"
    shutil.copy2(source_mp4, video_deliv_dir / "video_16x9.mp4")
    shutil.copy2(source_mp4, video_deliv_dir / f"{JOB_NAME}.mp4")

    srt_src = OUT_DIR / "subtitles_vi.srt"
    if not srt_src.is_file():
        srt_src = RUN_DIR / "subtitles.srt"
    if srt_src.is_file():
        shutil.copy2(srt_src, video_deliv_dir / "subtitles.srt")
        shutil.copy2(srt_src, video_deliv_dir / f"{JOB_NAME}.srt")

    thumb_src = RUN_DIR / "thumbnail_16x9.jpg"
    if thumb_src.is_file():
        shutil.copy2(thumb_src, video_deliv_dir / "thumbnail_16x9.jpg")
        shutil.copy2(thumb_src, video_deliv_dir / f"{JOB_NAME}.jpg")

    state_path = CACHE_FOLDER / "state.json"
    state_path.write_text(json.dumps({
        "phase": "complete",
        "account": TARGET_ACCOUNT,
        "session": TARGET_SESSION,
        "remote": REMOTE,
        "request_id": REQ_ID,
        "completed_at": time.time()
    }, indent=2) + "\n", encoding="utf-8")

    client._settle(REQ_ID)

    # Stop session to save Colab compute units
    try:
        client.stop()
        print("Colab session stopped successfully.", flush=True)
    except Exception as ex:
        print(f"Warning: could not stop Colab session: {ex}", flush=True)

    print("ALL DELIVERABLES SUCCESSFULLY DELIVERED AND VERIFIED!", flush=True)

if __name__ == "__main__":
    main()
