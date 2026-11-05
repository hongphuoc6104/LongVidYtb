"""Production Runner for Style v2 90-Image Generation.
Executes 18 channels x 5 images = 90 images across 4 parallel Flow CDP profiles
with CreditLedger tracking, automatic failover/quarantine, and 540px thumbnail export.
"""
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_cdp.persistent_pool import PersistentWorkerPool
from flow_cdp.credit_ledger import get_credit_ledger
from tools.generate_style_v2_90 import CHANNELS_DATA

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("style_v2_runner")

BRAIN_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/style_v2")
PROGRESS_FILE = Path("sys/runs/style_v2_progress.json")

def process_completed_image(task: dict, res: dict | None, err: Exception | None):
    """Callback executed immediately when an image task finishes."""
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
            
            # Export 540px-wide JPEG to brain directory
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
    """Inspect image for corruptions, dimensions, or unintended blue/navy tints."""
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
            
            # Check aspect ratio (~9:16)
            ratio = w / h
            if not (0.50 <= ratio <= 0.65):
                return False, f"Non-9:16 aspect ratio {ratio:.2f} ({w}x{h})"
            
            # Color histogram check: detect heavy blue/navy background
            rgb = im.convert("RGB")
            # Sample background pixels: top 20% corners
            sample_top_left = rgb.crop((0, 0, int(w * 0.25), int(h * 0.25)))
            stat = sample_top_left.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
            r, g, b = stat[0], stat[1], stat[2]
            
            # If blue is significantly dominant over red and green (navy/teal background)
            if b > r + 30 and b > g + 25 and b > 50:
                return False, f"Blue/navy background detected (R={r}, G={g}, B={b})"
            
            return True, "OK"
    except Exception as ex:
        return False, f"Image read error: {ex}"

def main():
    logger.info("Initializing Style v2 Runner for 18 channels = 90 images...")
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)
    
    ledger = get_credit_ledger()
    initial_credits = ledger.get_pool_summary().get("total_available_credits", 0)
    logger.info("Starting total credits in ledger: %d", initial_credits)

    pool = PersistentWorkerPool(
        target_workers=4,
        cooldown_seconds=300.0,
        pacing_seconds=2.5,
        stagger_seconds=0.5,
        headless=True,
    )

    tasks_to_run = []
    task_map = {}

    for ch_data in CHANNELS_DATA:
        ch = ch_data["channel"]
        run_dir = Path("sys/runs") / f"{ch}-style-v2"
        images_dir = run_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        for b in ch_data["beats"]:
            beat_num = b["beat"]
            task_id = f"{ch}_beat_0{beat_num}"
            png_dest = images_dir / f"beat_0{beat_num}.png"
            
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
                "_channel": ch,
                "_beat": beat_num,
                "_png_path": png_dest,
            }
            tasks_to_run.append(task)
            task_map[task_id] = task

    logger.info("Total tasks prepared: %d", len(tasks_to_run))

    pool.start()
    t_start = time.time()

    for task in tasks_to_run:
        pool.submit_task(task, priority=10)

    # Monitor progress
    completed_prev = 0
    while True:
        status = pool.get_status()
        pending = status["pending_tasks"]
        completed = len(pool.results)
        incidents = status["incidents_count"]
        workers_alive = status["active_worker_threads"]
        
        elapsed = round(time.time() - t_start, 1)
        progress_pct = round((completed / len(tasks_to_run)) * 100, 1)
        
        progress_data = {
            "total": len(tasks_to_run),
            "completed": completed,
            "pending": pending,
            "progress_percent": progress_pct,
            "elapsed_seconds": elapsed,
            "incidents": incidents,
            "workers_alive": workers_alive,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        PROGRESS_FILE.write_text(json.dumps(progress_data, indent=2))
        
        if completed != completed_prev or pending == 0:
            logger.info(
                "[Progress %s%%] %d/%d completed | Pending: %d | Incidents: %d | Workers: %d | Time: %ss",
                progress_pct, completed, len(tasks_to_run), pending, incidents, workers_alive, elapsed
            )
            completed_prev = completed

        if pending == 0:
            break
        time.sleep(5.0)

    logger.info("All queued tasks finished processing! Running QA audit...")
    
    # QA Check & Retries
    qa_failures = []
    for task in tasks_to_run:
        png_p = task["_png_path"]
        ok, reason = check_image_qa(png_p)
        if not ok:
            logger.warning("QA check failed for %s: %s", png_p.name, reason)
            qa_failures.append((task, reason))

    if qa_failures:
        logger.info("Found %d images needing QA retry. Executing retries (max 2)...", len(qa_failures))
        for task, reason in qa_failures:
            task["retries"] = 0
            task["max_retries"] = 2
            pool.submit_task(task, priority=0)
        
        # Wait for QA retries
        while pool.get_status()["pending_tasks"] > 0:
            time.sleep(3.0)
            
        # Re-verify
        remaining_failures = []
        for task, _ in qa_failures:
            png_p = task["_png_path"]
            ok, reason = check_image_qa(png_p)
            if not ok:
                remaining_failures.append((task["id"], reason))
            else:
                # Update thumbnail
                process_completed_image(task, {"path": str(png_p)}, None)
        
        if remaining_failures:
            logger.error("Remaining failures after QA retries: %s", remaining_failures)
        else:
            logger.info("All QA retries succeeded!")

    pool.shutdown()
    
    final_credits = ledger.get_pool_summary().get("total_available_credits", 0)
    credits_used = initial_credits - final_credits
    logger.info("Finished! Total credits used: %d (Remaining: %d)", credits_used, final_credits)

    # Save summary manifest
    summary = {
        "total_images_requested": 90,
        "completed_images": len(list(BRAIN_DIR.glob("*.jpg"))),
        "credits_used": credits_used,
        "total_elapsed_seconds": round(time.time() - t_start, 1),
        "status": "complete"
    }
    (Path("sys/runs/style_v2_summary.json")).write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
