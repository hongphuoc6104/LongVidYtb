"""Group runner for Style v2 generation across disjoint Flow CDP profiles.
"""
import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_cdp.cdp_direct_client import PROFILES
from flow_cdp.credit_ledger import get_credit_ledger
from flow_cdp.persistent_pool import PersistentWorkerPool
from tools.generate_style_v2_90 import CHANNELS_DATA

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("style_v2_subrunner")

BRAIN_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/style_v2")

GROUP_CONFIGS = {
    1: {
        "channels": ["en-macro-gears", "en-fine-print", "en-crowd-strings"],
        "profiles": ["profile_7", "profile_8", "profile_9", "profile_10"]
    },
    2: {
        "channels": ["en-cold-case-ink", "en-choke-point", "en-root-and-canopy"],
        "profiles": ["profile_11", "profile_12", "profile_14", "profile_15", "profile_en06", "profile_en07", "profile_en08", "profile_en09"]
    },
    3: {
        "channels": ["en-spawn-to-apex", "en-second-arrow", "en-bamboo-marble"],
        "profiles": ["profile_16", "profile_18", "profile_19", "profile_20", "profile_en10", "profile_en11", "profile_en12", "profile_en13"]
    },
    4: {
        "channels": ["en-kindred-sketch", "en-lazy-brain", "en-career-leverage", "en-wallet-anatomy"],
        "profiles": ["profile_en01", "profile_en02", "profile_en03", "profile_en05", "profile_en14", "profile_en15", "profile_en16", "profile_en17"]
    }
}

def process_completed_image(task: dict, res: dict | None, err: Exception | None):
    if err or not res:
        logger.error("Task %s failed: %s", task.get("id"), err)
        return

    png_path = Path(res.get("path", ""))
    if not png_path.exists():
        logger.error("Generated file not found: %s", png_path)
        return

    try:
        with Image.open(png_path) as im:
            im.load()
            w, h = im.size
            BRAIN_DIR.mkdir(parents=True, exist_ok=True)
            ch = task["_channel"]
            beat = task["_beat"]
            thumb_path = BRAIN_DIR / f"{ch}_0{beat}.jpg"
            
            target_w = 540
            target_h = int(round(540 * h / w))
            resized = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
            if resized.mode != "RGB":
                resized = resized.convert("RGB")
            resized.save(thumb_path, format="JPEG", quality=90, optimize=True)
            logger.info("Saved 540px thumbnail: %s (%dx%d)", thumb_path.name, target_w, target_h)
    except Exception as ex:
        logger.warning("Error processing thumbnail for %s: %s", png_path, ex)

def check_image_qa(img_path: Path) -> tuple[bool, str]:
    if not img_path.exists():
        return False, "File missing"
    if img_path.stat().st_size < 10000:
        return False, f"File too small ({img_path.stat().st_size} bytes)"
    
    try:
        with Image.open(img_path) as im:
            im.load()
            w, h = im.size
            if w <= 0 or h <= 0:
                return False, f"Invalid dimensions {w}x{h}"
            
            ratio = w / h
            if not (0.50 <= ratio <= 0.65):
                return False, f"Non-9:16 aspect ratio {ratio:.2f} ({w}x{h})"
            
            rgb = im.convert("RGB")
            sample_top_left = rgb.crop((0, 0, int(w * 0.25), int(h * 0.25)))
            stat = sample_top_left.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
            r, g, b = stat[0], stat[1], stat[2]
            
            # Blue/navy/teal check
            if b > r + 30 and b > g + 25 and b > 50:
                return False, f"Blue/navy background detected (R={r}, G={g}, B={b})"
            
            return True, "OK"
    except Exception as ex:
        return False, f"Image read error: {ex}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=int, required=True, choices=[1, 2, 3, 4])
    args = parser.parse_args()

    cfg = GROUP_CONFIGS[args.group]
    assigned_channels = cfg["channels"]
    assigned_prof_names = cfg["profiles"]

    logger.info("Starting Group %d Runner: Channels=%s, Profiles=%s", args.group, assigned_channels, assigned_prof_names)
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    assigned_profiles = [p for p in PROFILES if p["name"] in assigned_prof_names]
    assert len(assigned_profiles) >= 4, f"Expected at least 4 profiles, found {len(assigned_profiles)}"

    status_file = Path(f"sys/runs/style_v2_group_{args.group}_status.json")

    # Filter channel data
    ch_map = {c["channel"]: c for c in CHANNELS_DATA if c["channel"] in assigned_channels}

    tasks_to_run = []
    skipped_count = 0

    for ch_name in assigned_channels:
        ch_data = ch_map[ch_name]
        run_dir = Path("sys/runs") / f"{ch_name}-style-v2"
        images_dir = run_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        for b in ch_data["beats"]:
            beat_num = b["beat"]
            task_id = f"{ch_name}_beat_0{beat_num}"
            png_dest = images_dir / f"beat_0{beat_num}.png"
            json_dest = images_dir / f"beat_0{beat_num}.json"

            # Check if already generated
            if png_dest.exists() and json_dest.exists() and png_dest.stat().st_size > 10000:
                ok, _ = check_image_qa(png_dest)
                if ok:
                    skipped_count += 1
                    # Ensure thumb exists
                    process_completed_image({"_channel": ch_name, "_beat": beat_num}, {"path": str(png_dest)}, None)
                    continue

            task = {
                "id": task_id,
                "jobId": task_id,
                "prompt": b["prompt"],
                "ratio": "9:16",
                "aspect": "9:16",
                "model": "BELUGA",
                "filename": f"beat_0{beat_num}.png",
                "out_dir": str(images_dir),
                "credit_cost": 1,
                "credit_reason": "image",
                "editorial_overlay": {"enabled": False},
                "callback": process_completed_image,
                "_channel": ch_name,
                "_beat": beat_num,
                "_png_path": png_dest,
            }
            tasks_to_run.append(task)

    logger.info("Group %d: Total images = %d, Skipped = %d, To Generate = %d", args.group, len(assigned_channels) * 5, skipped_count, len(tasks_to_run))

    if not tasks_to_run:
        logger.info("Group %d: All images already complete!", args.group)
        status_file.write_text(json.dumps({"status": "complete", "completed": len(assigned_channels) * 5, "total": len(assigned_channels) * 5}))
        return

    pool = PersistentWorkerPool(
        target_workers=4,
        cooldown_seconds=300.0,
        pacing_seconds=2.5,
        stagger_seconds=0.5,
        headless=True,
        profiles=assigned_profiles,
    )

    pool.start()
    t_start = time.time()

    for task in tasks_to_run:
        pool.submit_task(task, priority=10)

    # Monitor
    completed_prev = 0
    while True:
        status = pool.get_status()
        pending = status["pending_tasks"]
        completed = len(pool.results)
        incidents = status["incidents_count"]
        workers_alive = status["active_worker_threads"]
        elapsed = round(time.time() - t_start, 1)

        progress_data = {
            "group": args.group,
            "total_to_generate": len(tasks_to_run),
            "completed_new": completed,
            "skipped": skipped_count,
            "total_done": completed + skipped_count,
            "pending": pending,
            "incidents": incidents,
            "workers_alive": workers_alive,
            "elapsed_seconds": elapsed,
            "status": "running" if pending > 0 else "verifying",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        status_file.write_text(json.dumps(progress_data, indent=2))

        if completed != completed_prev or pending == 0:
            logger.info(
                "[Group %d] %d/%d generated | Pending: %d | Incidents: %d | Workers: %d | Time: %ss",
                args.group, completed, len(tasks_to_run), pending, incidents, workers_alive, elapsed
            )
            completed_prev = completed

        if pending == 0:
            break
        time.sleep(4.0)

    # QA & Retries
    logger.info("[Group %d] Generation complete. Running QA check on all %d tasks...", args.group, len(tasks_to_run))
    qa_failures = []
    for task in tasks_to_run:
        png_p = task["_png_path"]
        ok, reason = check_image_qa(png_p)
        if not ok:
            logger.warning("[Group %d] QA failed for %s: %s", args.group, png_p.name, reason)
            qa_failures.append((task, reason))

    if qa_failures:
        logger.info("[Group %d] %d images failed QA. Retrying (max 2)...", args.group, len(qa_failures))
        for task, reason in qa_failures:
            task["retries"] = 0
            task["max_retries"] = 2
            pool.submit_task(task, priority=0)

        while pool.get_status()["pending_tasks"] > 0:
            time.sleep(3.0)

        # Re-check
        for task, _ in qa_failures:
            png_p = task["_png_path"]
            ok, reason = check_image_qa(png_p)
            if ok:
                process_completed_image(task, {"path": str(png_p)}, None)

    pool.shutdown()
    logger.info("[Group %d] All tasks and QA finished successfully!", args.group)
    status_file.write_text(json.dumps({
        "group": args.group,
        "status": "complete",
        "total_images": len(assigned_channels) * 5,
        "elapsed_seconds": round(time.time() - t_start, 1)
    }, indent=2))

if __name__ == "__main__":
    main()
