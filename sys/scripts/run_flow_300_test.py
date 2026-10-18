#!/usr/bin/env python3
"""Execute 300 real Flow image generations across a Dynamic Profile Pool with auto-failover.

Architectural Guarantees:
1. Dynamic Profile Pool (up to 20 Chrome profiles, 8-10 active workers, standby rotation).
2. Two-Phase Commit (atomic staging in `.staging/` -> verified `.jpg` + `.json` in `images/`).
3. Priority Re-Queue: Failed/interrupted tasks return to HEAD of queue for immediate worker pickup.
4. Auto-Remediation & Cooldown Quarantine: When Error 7 (PUBLIC_ERROR_UNUSUAL_ACTIVITY) occurs,
   the offending profile clears storage/cookies, enters a 10-minute cooldown, and is swapped
   with a healthy standby profile without stopping other concurrent workers.
5. Pacing gap (>= 4.0s per profile) and staggered launches (0.5s) to eliminate burst flags.
6. Resumable & Idempotent: Automatically verifies existing images and skips completed ones.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import queue
import shutil
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from flow_cdp import accounts
from flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


PROMPT_TEMPLATES = [
    "A clean 2D hand-drawn stick figure researcher with a large round white head and simple dot eyes standing in front of a chalkboard covered in mathematical equations, minimalist marker-pen explainer style, full frame 16:9, soft muted colors, pure white background #FFFFFF.",
    "A 2D stick figure student reading an ancient leather-bound academic journal at a wooden desk with a single brass lamp, marker illustration style, clean black contours, no realistic hair, no text, wide angle 16:9.",
    "A behavioral psychology laboratory with two stick figures observing a rat navigating a transparent maze on a checkered table, marker-pen 2D explainer style, soft pastel palette, uncluttered composition 16:9.",
    "A scientific debate in a lecture hall: one stick figure professor gesturing passionately at a podium while stick figure audience members take notes, flat fills, expressive stick postures, 16:9 widescreen.",
    "A researcher looking through a brass microscope in a brightly lit modern genetics laboratory, simple test tubes and glassware on the table, clean 2D marker style, edge-to-edge illustration 16:9.",
    "A scholar holding a single glowing lightbulb idea above their head while sitting on a massive stack of academic textbooks, expressive stick figure posture, cheerful mood, marker art 16:9.",
    "Two researchers standing before a large comparison board with red arrows pointing between two conflicting scientific hypotheses, clean marker illustration, minimal details, 16:9 aspect ratio.",
    "An astronomical observatory interior at dusk: a stick figure astronomer looking through a large vintage telescope towards a starry window, deep navy and warm amber lighting, 2D explainer 16:9.",
    "A solitary stick figure walking down a long minimalist corridor lined with archive filing cabinets and quiet doors, perspective view, contemplative mood, 2D marker explainer 16:9.",
    "A cognitive neuroscience experiment: a stick figure wearing an EEG sensor cap with simple colorful wires sitting peacefully in an armchair, clean laboratory background, 16:9.",
    "A stick figure statistician reviewing a massive printed scatter plot chart rolling across a conference table, marker pen line art, soft muted tones, 16:9 composition.",
    "An archaeology field station tent: a stick figure brushing sand from an ancient fossil fragment on an examination table, warm earthy tones, simple 2D stick figure, 16:9.",
    "A quiet university library aisle with floor-to-ceiling wooden bookshelves, a stick figure holding a magnifying glass examining a manuscript, peaceful lighting, 16:9.",
    "A medical research briefing room: three stick figure doctors in simple teal coats analyzing an abstract anatomical diagram, clear visual hierarchy, marker-pen aesthetic 16:9.",
    "A computer science server room: a stick figure technician holding a digital tablet next to glowing server racks with subtle cable lines, high-contrast clean 2D illustration 16:9."
]


def generate_300_prompts() -> list[dict[str, Any]]:
    """Generate 300 structured prompt tasks with scene continuity markers."""
    items = []
    num_templates = len(PROMPT_TEMPLATES)
    for i in range(1, 301):
        tmpl = PROMPT_TEMPLATES[(i - 1) % num_templates]
        variant_idx = ((i - 1) // num_templates) + 1
        prompt = f"{tmpl} (Scientific Study Phase {variant_idx}, Scene Variant {i:03d})"
        items.append({
            "index": i,
            "id": f"flow_300_shot_{i:03d}",
            "prompt": prompt,
            "ratio": "16:9",
            "retries": 0,
        })
    return items


def launch_profile_if_needed(prof_cfg: dict[str, Any]) -> bool:
    """Ensure Chrome is running and listening on the designated port."""
    port = int(prof_cfg["cdp_port"])
    if accounts.is_port_listening(port):
        return True
    entry = {
        "port": port,
        "user_data_dir": prof_cfg["user_data_dir"],
        "directory": prof_cfg["profile_dir"],
    }
    return accounts.launch_profile(entry, url="https://flow.google.com/")


async def remediate_profile_session(sess: DirectCDPProfileSession) -> None:
    """Clean origin cache, indexeddb, and bot detection tracking cookies."""
    try:
        await sess.call(
            "Storage.clearDataForOrigin",
            {
                "origin": "https://flow.google.com",
                "storageTypes": "appcache,cache_storage,file_systems,indexeddb,local_storage,service_workers,shader_cache,websql",
            },
            timeout=6.0,
        )
        await sess.call("Network.clearBrowserCache", timeout=6.0)
        res = await sess.call("Network.getAllCookies", timeout=6.0)
        cookies = res.get("cookies", [])
        for c in cookies:
            if "GRECAPTCHA" in c["name"] or c["name"].startswith("_ga"):
                await sess.call(
                    "Network.deleteCookies",
                    {"name": c["name"], "domain": c["domain"], "path": c.get("path", "/")},
                    timeout=4.0,
                )
        await sess.call("Page.navigate", {"url": "https://flow.google.com/"}, timeout=6.0)
    except Exception:
        pass


class DynamicProfilePool:
    """Thread-safe pool managing active and standby Chrome profiles with cooldown quarantine."""

    def __init__(self, profiles: list[dict[str, Any]], cooldown_seconds: float = 600.0):
        self.lock = threading.Lock()
        self.all_profiles = list(profiles)
        self.in_use: set[str] = set()
        self.cooldowns: dict[str, float] = {}
        self.cooldown_seconds = cooldown_seconds

    def acquire(self, current_name: Optional[str] = None) -> Optional[dict[str, Any]]:
        with self.lock:
            now = time.time()
            for p in self.all_profiles:
                name = p["name"]
                if name == current_name or name in self.in_use:
                    continue
                # Check cooldown status
                if name in self.cooldowns:
                    if self.cooldowns[name] > now:
                        continue
                    else:
                        del self.cooldowns[name]
                # Found candidate profile
                self.in_use.add(name)
                return p
            return None

    def release(self, profile_cfg: dict[str, Any], quarantine_reason: Optional[str] = None):
        with self.lock:
            name = profile_cfg["name"]
            self.in_use.discard(name)
            if quarantine_reason:
                self.cooldowns[name] = time.time() + self.cooldown_seconds


def worker_loop(
    worker_id: int,
    initial_profile: dict[str, Any],
    pool: DynamicProfilePool,
    task_queue: queue.PriorityQueue,
    out_dir: Path,
    staging_dir: Path,
    incidents_file: Path,
    abort_event: threading.Event,
    pacing_seconds: float,
    progress_lock: threading.Lock,
    progress_tracker: dict[str, Any],
):
    current_profile = initial_profile
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    sess = None

    def connect_session(p_cfg: dict[str, Any]) -> DirectCDPProfileSession:
        launch_profile_if_needed(p_cfg)
        s = DirectCDPProfileSession(p_cfg)
        loop.run_until_complete(s.connect())
        return s

    try:
        sess = connect_session(current_profile)
    except Exception as exc:
        print(f"\033[93m[Worker-{worker_id}] Lỗi kết nối khởi động {current_profile['name']}: {exc}. Đang đổi profile khác...\033[0m")
        pool.release(current_profile, quarantine_reason="init_connect_failed")
        current_profile = pool.acquire()
        if not current_profile:
            print(f"\033[91m[Worker-{worker_id}] Không còn profile nào khả dụng trong pool. Luồng kết thúc.\033[0m")
            return
        try:
            sess = connect_session(current_profile)
        except Exception as exc2:
            print(f"\033[91m[Worker-{worker_id}] Lỗi kết nối profile thay thế {current_profile['name']}: {exc2}. Luồng kết thúc.\033[0m")
            pool.release(current_profile, quarantine_reason="replace_connect_failed")
            return

    try:
        while not abort_event.is_set():
            try:
                # PriorityQueue items: (priority, index, task_dict)
                priority, idx, task = task_queue.get_nowait()
            except queue.Empty:
                break

            shot_id = task["id"]
            img_dest = out_dir / f"image_{idx:03d}.jpg"
            meta_dest = out_dir / f"image_{idx:03d}.json"
            staging_path = staging_dir / f"temp_{idx:03d}_{current_profile['name']}.jpg"

            # 1. Idempotent check: skip if valid file exists
            if img_dest.is_file() and meta_dest.is_file():
                try:
                    with Image.open(img_dest) as im:
                        im.verify()
                    with progress_lock:
                        progress_tracker["completed"] += 1
                        c = progress_tracker["completed"]
                        t = progress_tracker["total"]
                        print(f"[{c:03d}/{t:03d}] [{current_profile['name']}] Image #{idx:03d} ALREADY EXISTS & VALID (Skipped).")
                    task_queue.task_done()
                    continue
                except Exception:
                    pass

            t0 = time.time()
            try:
                # 2. Execute RPC generation inside browser tab
                res = loop.run_until_complete(
                    sess.generate_image(
                        prompt=task["prompt"],
                        aspect=task.get("ratio", "16:9"),
                        model="BELUGA",
                    )
                )
                media_url = res.get("url")
                media_id = res.get("media_id")
                if not media_url:
                    raise RuntimeError(f"No media URL returned: {res}")

                # 3. Download binary to Staging directory with 3 retries
                img_data = b""
                for dl_attempt in range(3):
                    try:
                        req = urllib.request.Request(media_url, headers={"User-Agent": "video-pilot"})
                        with urllib.request.urlopen(req, timeout=45) as resp:
                            img_data = resp.read()
                        if len(img_data) >= 5000:
                            break
                    except Exception as dl_err:
                        if dl_attempt == 2:
                            raise RuntimeError(f"Download failed after 3 attempts: {dl_err}") from dl_err
                        time.sleep(2.0)

                if len(img_data) < 5000:
                    raise RuntimeError(f"Downloaded image too small ({len(img_data)} bytes)")

                # Write to staging first
                staging_path.write_bytes(img_data)

                # 4. Verify PIL integrity on staging image
                with Image.open(staging_path) as im:
                    im.verify()

                # 5. Atomic Commit: Move staging -> images/
                shutil.move(str(staging_path), str(img_dest))

                latency = round(time.time() - t0, 2)
                f_hash = sha256_file(img_dest)

                # Write sidecar metadata
                metadata = {
                    "index": idx,
                    "id": shot_id,
                    "media_id": media_id,
                    "url": media_url,
                    "prompt": task["prompt"],
                    "ratio": task.get("ratio", "16:9"),
                    "profile": current_profile["name"],
                    "port": current_profile["cdp_port"],
                    "latency": latency,
                    "sha256": f_hash,
                    "bytes": len(img_data),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                meta_dest.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

                with progress_lock:
                    progress_tracker["completed"] += 1
                    c = progress_tracker["completed"]
                    t = progress_tracker["total"]
                    print(f"[{c:03d}/{t:03d}] [{current_profile['name']}:{current_profile['cdp_port']}] Image #{idx:03d} SUCCESS in {latency}s ({len(img_data)}B, ID={media_id[:8]}..) [Pacing {pacing_seconds}s]")

                task_queue.task_done()

                # Pacing gap per profile
                if not abort_event.is_set():
                    time.sleep(pacing_seconds)

            except Exception as exc:
                staging_path.unlink(missing_ok=True)
                err_str = str(exc)
                is_rate_limit = "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in err_str or "FLOW_PROVIDER_BLOCKED" in err_str

                incident = {
                    "index": idx,
                    "id": shot_id,
                    "profile": current_profile["name"],
                    "port": current_profile["cdp_port"],
                    "error": err_str,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                with progress_lock:
                    with open(incidents_file, "a", encoding="utf-8") as f_inc:
                        f_inc.write(json.dumps(incident, ensure_ascii=False) + "\n")

                if is_rate_limit:
                    print(f"\n\033[93m[FAILOVER] {current_profile['name']} gặp Rate Limit / Bot Block tại ảnh #{idx:03d}!\033[0m")
                    print(f"\033[93m  - Đang chạy Remediation (Xóa Storage/Cache & reload tab) trên {current_profile['name']}...\033[0m")
                    loop.run_until_complete(remediate_profile_session(sess))

                    # Quarantine for 10 minutes
                    old_prof_name = current_profile["name"]
                    pool.release(current_profile, quarantine_reason="rate_limit_code_7")

                    # Re-queue task at HEAD of PriorityQueue (priority=0)
                    task["retries"] = task.get("retries", 0) + 1
                    if task["retries"] <= 3:
                        task_queue.put((0, idx, task))
                        print(f"\033[92m  - Đã đẩy lại ảnh #{idx:03d} vào ĐẦU HÀNG ĐỢI (Retry {task['retries']}/3).\033[0m")
                    else:
                        print(f"\033[91m  - [!] Ảnh #{idx:03d} đã thử lại quá 3 lần. Cách ly vào sổ sự cố.\033[0m")
                    task_queue.task_done()

                    # Acquire a fresh healthy standby profile from the pool
                    try:
                        loop.run_until_complete(sess.close())
                    except Exception:
                        pass

                    new_profile = pool.acquire(current_name=old_prof_name)
                    if not new_profile:
                        print(f"\033[93m[!] Tất cả profile khác đang bận/cooldown. Worker-{worker_id} chờ 30s trước khi thử lại...\033[0m")
                        time.sleep(30)
                        current_profile = pool.acquire()
                        if not current_profile:
                            print(f"\033[91m[!] Hết profile khả dụng. Worker-{worker_id} kết thúc.\033[0m")
                            break
                    else:
                        current_profile = new_profile

                    print(f"\033[96m[✓] Worker-{worker_id} đã đổi sang Profile mới: {current_profile['name']} (Port {current_profile['cdp_port']}). Tiếp tục tạo ảnh ngay!\033[0m\n")
                    try:
                        sess = connect_session(current_profile)
                    except Exception as switch_err:
                        print(f"\033[91m[!] Lỗi kết nối profile mới {current_profile['name']}: {switch_err}\033[0m")
                        pool.release(current_profile, quarantine_reason="switch_connect_failed")
                        break
                    continue
                else:
                    # Non-rate-limit exception
                    task["retries"] = task.get("retries", 0) + 1
                    if task["retries"] <= 5:
                        task_queue.put((0, idx, task))
                        print(f"\033[93m[!] Lỗi tạm thời ({exc}) tại ảnh #{idx:03d}. Đã đưa lại đầu hàng đợi (Retry {task['retries']}/5).\033[0m")
                    else:
                        print(f"\033[91m[X] Ảnh #{idx:03d} đã thử lại quá 5 lần. Bỏ qua.\033[0m")
                    task_queue.task_done()
                    time.sleep(2.0)
    finally:
        if sess:
            try:
                loop.run_until_complete(sess.close())
            except Exception:
                pass
        pool.release(current_profile)
        loop.close()


def main():
    parser = argparse.ArgumentParser(description="Run 300 Flow image generations with Dynamic Pool Failover")
    parser.add_argument("--total", type=int, default=300, help="Total images to generate")
    parser.add_argument("--workers", type=int, default=9, help="Number of concurrent active worker threads")
    parser.add_argument("--pacing", type=float, default=4.0, help="Pacing gap in seconds per profile")
    parser.add_argument("--stagger", type=float, default=0.5, help="Staggered start delay in seconds")
    parser.add_argument("--cooldown", type=float, default=600.0, help="Quarantine duration for blocked profiles")
    parser.add_argument("--out-dir", type=str, default="sys/runs/flow-300-experiment/images", help="Output directory")
    args = parser.parse_args()

    out_dir = (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    staging_dir = out_dir.parent / ".staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    incidents_file = out_dir.parent / "incidents.jsonl"
    summary_file = out_dir.parent / "summary.json"

    prompts = generate_300_prompts()[:args.total]

    task_q = queue.PriorityQueue()
    for item in prompts:
        # Initial priority = 10, idx = item["index"], data = item
        task_q.put((10, item["index"], item))

    # Initialize pool with all 20 profiles
    pool = DynamicProfilePool(PROFILES, cooldown_seconds=args.cooldown)

    # Put profile_7 into initial cooldown since it's currently flagged
    pool.cooldowns["profile_7"] = time.time() + args.cooldown

    abort_event = threading.Event()
    progress_lock = threading.Lock()
    progress_tracker = {"completed": 0, "total": len(prompts)}

    print("=" * 80)
    print(f"  TIẾN TRÌNH THỰC NGHIỆM: TẠO {len(prompts)} ẢNH VỚI DYNAMIC PROFILE POOL")
    print(f"  - Thư mục lưu ảnh: {out_dir}")
    print(f"  - Thư mục Staging: {staging_dir}")
    print(f"  - Tổng số Profile trong Pool: {len(PROFILES)} Profiles")
    print(f"  - Số luồng chạy đồng thời (Active Workers): {args.workers}")
    print(f"  - Giãn cách mỗi Profile (Pacing Gap): {args.pacing}s")
    print(f"  - Thời gian cách ly Cooldown khi gặp Lỗi 7: {args.cooldown}s (10 phút)")
    print(f"  - Cơ chế bảo toàn: Two-Phase Commit + Priority Re-Queue + Standby Failover")
    print("=" * 80 + "\n")

    start_time = time.time()
    threads = []
    num_workers = min(args.workers, len(PROFILES))

    for w_id in range(1, num_workers + 1):
        prof = pool.acquire()
        if not prof:
            print(f"[!] Không đủ profile khả dụng cho Worker-{w_id}.")
            break

        t = threading.Thread(
            target=worker_loop,
            args=(
                w_id,
                prof,
                pool,
                task_q,
                out_dir,
                staging_dir,
                incidents_file,
                abort_event,
                args.pacing,
                progress_lock,
                progress_tracker,
            ),
            name=f"Worker-{w_id}",
        )
        threads.append(t)
        t.start()
        time.sleep(args.stagger)

    for t in threads:
        t.join()

    total_time = round(time.time() - start_time, 2)
    completed_count = progress_tracker["completed"]

    summary_data = {
        "total_images": completed_count,
        "target": len(prompts),
        "total_time_seconds": total_time,
        "average_time_per_image": round(total_time / max(1, completed_count), 2),
        "out_dir": str(out_dir),
        "status": "SUCCESS" if completed_count >= len(prompts) else "PARTIAL",
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    summary_file.write_text(json.dumps(summary_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("\n" + "=" * 80)
    print(f"\033[92m[✓] BÁO CÁO KẾT THÚC: {completed_count}/{len(prompts)} ảnh hoàn thành ({total_time}s ~ {total_time/60:.1f} phút).\033[0m")
    print(f"Báo cáo tổng kết: {summary_file}")
    print(f"Sổ nhật ký sự cố: {incidents_file}")
    print(f"Thư mục ảnh: {out_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
