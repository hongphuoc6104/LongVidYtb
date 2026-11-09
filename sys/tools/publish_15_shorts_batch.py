#!/usr/bin/env python3
"""Batch YouTube Shorts Publisher for Video Pilot (15 Channels).

Publishes 15 finalized and verified short_9x16 videos sequentially
to their respective channels via publish_youtube_cdp.py with clean
resource teardown between uploads.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for p in (str(REPO_ROOT), str(SYS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from channels.registry import get_channel
from flow_cdp.process_manager import get_process_manager, is_port_listening

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("batch_publish_15_shorts")

REPORT_FILE = REPO_ROOT / "video" / "published_15_shorts_report.json"
STATE_FILE = REPO_ROOT / "video" / "published_15_shorts_state.json"
LOG_FILE = REPO_ROOT / "video" / "published_15_shorts.log"

CHANNELS_LIST = [
    "ban_do_quyen_luc",
    "banh_rang",
    "chanh_niem_ke",
    "co_the_ke",
    "dia_com",
    "ho_so_ky_la",
    "la_ban_hoc_thuat",
    "loi_sang_soi",
    "luat_doi_thuong",
    "luat_ngam",
    "minh_triet_song",
    "su_ke_lai",
    "tui_tien",
    "ua_sao_vay",
    "vu_tru_ti_hon",
]


def load_report() -> dict:
    if REPORT_FILE.exists():
        try:
            return json.loads(REPORT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "status": "IN_PROGRESS",
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_at": None,
        "total_channels": len(CHANNELS_LIST),
        "published_count": 0,
        "failed_count": 0,
        "videos": {},
    }


def save_report(report: dict) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_state(current_channel: str, status: str, detail: str = "") -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "timestamp": time.time(),
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "current_channel": current_channel,
        "status": status,
        "detail": detail,
        "pid": os.getpid(),
    }
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def get_channel_payload(slug: str) -> dict:
    map_file = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"
    channel_map = json.loads(map_file.read_text(encoding="utf-8")).get("channels", {})
    ch_info = channel_map.get(slug, {})

    base = REPO_ROOT / "video" / f"vn_pilot_{slug}_short_fullchain"
    mp4 = base / f"vn_pilot_{slug}_short_fullchain_9x16.mp4"
    thumb = base / f"vn_pilot_{slug}_short_fullchain_thumbnail_9x16.png"
    spec_path = base / f"{slug}_short_aligned_spec.json"

    spec = json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else {}
    ch_profile = get_channel(slug)

    title = spec.get("title") or spec.get("youtube_title") or ""
    if not title and slug == "tui_tien":
        title = "Bẫy Giá Mồi: Vì Sao Bạn Luôn Chọn Cỡ Lớn?"

    long_url = ch_info.get("long_video_url", "")
    beats = spec.get("beats", [])
    hook_narration = beats[0].get("narration", "") if beats else ""
    cta_plan = spec.get("cta_plan", {})
    bridge = cta_plan.get("bridge_to_long") or cta_plan.get("bridge") or ""

    tags = ["#Shorts"] + list(ch_profile.hashtags[:4])
    tag_str = " ".join(tags)

    lines = [
        title,
        "",
        hook_narration,
        "",
        f"👉 Xem trọn bộ video bản dài giải mã chi tiết tại: {long_url}",
        f"{bridge}",
        "",
        f"Đăng ký kênh {ch_profile.name} để theo dõi thêm nhiều nội dung bổ ích!",
        "",
        tag_str,
    ]
    description = "\n".join(lines).strip()

    return {
        "slug": slug,
        "video_path": str(mp4),
        "thumbnail_path": str(thumb),
        "title": title,
        "description": description,
        "related_video_url": long_url,
        "cdp_port": ch_info.get("cdp_port"),
    }


def publish_channel(slug: str) -> dict:
    payload = get_channel_payload(slug)
    port = payload.get("cdp_port")

    pm = get_process_manager()
    # Safety: ensure port is clean before starting
    if port and is_port_listening(port):
        logger.warning("Port %d is already in use before publishing %s. Terminating existing process...", port, slug)
        pm.terminate_by_port(port)
        time.sleep(1.0)

    cmd = [
        sys.executable,
        str(REPO_ROOT / "sys" / "tools" / "publish_youtube_cdp.py"),
        "--channel", slug,
        "--video", payload["video_path"],
        "--title", payload["title"],
        "--description", payload["description"],
        "--thumbnail", payload["thumbnail_path"],
        "--short",
        "--visibility", "PUBLIC",
        "--bypass-review-gate",
        "--headless",
    ]
    if payload["related_video_url"]:
        cmd.extend(["--related-video", payload["related_video_url"]])

    logger.info("Starting publish for %s...", slug)
    logger.info("Title: %s", payload["title"])
    logger.info("Video: %s", payload["video_path"])

    start_time = time.time()
    result_json = None
    captured_stdout = ""

    with open(LOG_FILE, "a", encoding="utf-8") as log_fh:
        log_fh.write(f"\n\n{'='*70}\n")
        log_fh.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] START CHANNEL: {slug}\n")
        log_fh.write(f"COMMAND: {' '.join(cmd)}\n")
        log_fh.flush()

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(REPO_ROOT),
        )

        lines = []
        try:
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                log_fh.write(line)
                log_fh.flush()
                lines.append(line)
            proc.wait(timeout=360.0)
        except subprocess.TimeoutExpired:
            logger.error("Channel %s timed out after 360s! Killing process...", slug)
            proc.kill()
            proc.wait()
            log_fh.write(f"\n[ERROR] Channel {slug} TIMED OUT after 360s!\n")
        except Exception as e:
            logger.error("Error reading output from %s: %s", slug, e)
            proc.kill()
            proc.wait()

        captured_stdout = "".join(lines)
        log_fh.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] FINISH CHANNEL: {slug} (Exit Code: {proc.returncode})\n")

    duration = time.time() - start_time

    # Cleanup browser port strictly
    if port:
        logger.info("Cleaning up browser on port %d...", port)
        pm.terminate_by_port(port)

    # Parse publish report from output
    if "=== PUBLISH REPORT ===" in captured_stdout:
        try:
            report_block = captured_stdout.split("=== PUBLISH REPORT ===")[-1].strip()
            # If there is extra output after JSON, extract valid JSON
            brace_start = report_block.find("{")
            brace_end = report_block.rfind("}")
            if brace_start != -1 and brace_end != -1:
                json_str = report_block[brace_start:brace_end + 1]
                result_json = json.loads(json_str)
        except Exception as e:
            logger.warning("Could not parse publish report JSON: %s", e)

    video_url = ""
    short_url = ""
    if result_json:
        video_url = result_json.get("video_url", "")
    elif proc.returncode == 0:
        # Fallback parse from stdout
        for line in captured_stdout.splitlines():
            if "Assigned video URL in dialog:" in line:
                video_url = line.split("dialog:")[-1].strip()
            elif "Published video URL:" in line:
                video_url = line.split("URL:")[-1].strip()

    if video_url:
        vid_id = video_url.strip().rstrip("/").split("/")[-1].split("?")[0]
        short_url = f"https://youtube.com/shorts/{vid_id}"

    success = bool(short_url and (proc.returncode == 0 or (result_json and result_json.get("status") == "PUBLISHED")))

    return {
        "slug": slug,
        "success": success,
        "video_url": video_url,
        "short_url": short_url,
        "duration_sec": round(duration, 2),
        "return_code": proc.returncode,
        "title": payload["title"],
        "related_video_url": payload["related_video_url"],
        "result_detail": result_json or {},
    }


def main():
    logger.info("==================================================")
    logger.info("Video Pilot: Publishing 15 Shorts to 15 Channels")
    logger.info("==================================================")

    report = load_report()

    for idx, slug in enumerate(CHANNELS_LIST, start=1):
        # Check if already published successfully
        existing = report.get("videos", {}).get(slug)
        if existing and existing.get("success") and existing.get("short_url"):
            logger.info("[%d/15] Channel %s ALREADY PUBLISHED: %s. Skipping.", idx, slug, existing["short_url"])
            continue

        logger.info("[%d/15] >>> Processing Channel: %s <<<", idx, slug)
        update_state(slug, "UPLOADING", f"Channel {idx}/{len(CHANNELS_LIST)}")

        ch_res = publish_channel(slug)

        report["videos"][slug] = ch_res
        if ch_res["success"]:
            logger.info(">>> SUCCESS [%d/15] %s: %s <<<", idx, slug, ch_res["short_url"])
        else:
            logger.error(">>> FAILED [%d/15] %s (return_code=%s) <<<", idx, slug, ch_res["return_code"])

        # Update summary counts
        report["published_count"] = sum(1 for v in report["videos"].values() if v.get("success"))
        report["failed_count"] = sum(1 for v in report["videos"].values() if not v.get("success"))
        save_report(report)

        update_state(slug, "FINISHED_CHANNEL", f"Success={ch_res['success']}")

        # Stagger gap between channels: 4.5s to let OS reclaim memory and sockets
        logger.info("Cooling down 4.5s before next channel...")
        time.sleep(4.5)

    report["status"] = "COMPLETED" if report["published_count"] == len(CHANNELS_LIST) else "PARTIAL"
    report["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_report(report)
    update_state("ALL", report["status"], f"Published {report['published_count']}/{len(CHANNELS_LIST)}")

    logger.info("==================================================")
    logger.info("Batch Publishing Complete: %d/%d published successfully", report["published_count"], len(CHANNELS_LIST))
    logger.info("Report saved to: %s", REPORT_FILE)
    logger.info("==================================================")


if __name__ == "__main__":
    main()
