"""Regenerate QA-flagged defect images for en-first-principles (02) and en-scale-and-bone (05).
"""
import json
import logging
import sys
import time
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_cdp.persistent_pool import PersistentWorkerPool
from flow_cdp.cdp_direct_client import PROFILES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("qa_regen")

BRAIN_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/style_v2")

REGEN_TASKS = [
    {
        "id": "en-first-principles_beat_02_retry",
        "jobId": "en-first-principles_beat_02_retry",
        # Cleaned prompt eliminating technical drafting/dimension lines/HUD
        "prompt": "Vertical 9:16 full-bleed minimalist ink line art on warm cream paper #F4EFE4. A clean simple cutaway silhouette of an empty cylindrical rocket fuel tank drawn with single dark lines #2B2B2B. One subtle terracotta downward arrow #E07A3F indicating empty dead weight, with sage #9BA88D accent. Over 75% calm empty negative space, lower 30% completely empty, zero text, zero dimension lines, zero ticks, zero HUD.",
        "ratio": "9:16",
        "aspect": "9:16",
        "model": "BELUGA",
        "filename": "beat_02.png",
        "out_dir": "sys/runs/en-first-principles-style-v2/images",
        "credit_cost": 1,
        "credit_reason": "image",
        "editorial_overlay": {"enabled": False},
        "_channel": "en-first-principles",
        "_beat": 2,
    },
    {
        "id": "en-scale-and-bone_beat_05_retry",
        "jobId": "en-scale-and-bone_beat_05_retry",
        # Explicitly prohibiting birds/nests and enforcing reptile lizard hatchling
        "prompt": "Vertical 9:16 full-bleed naturalist gouache illustration on warm cream #F2EBDD. High in the forest canopy, a single tiny Komodo dragon reptile hatchling with mottled terracotta scales #C86D51 rests safely on a mossy tree branch #4A6B53 with deep bark #3A2E25. Over 70% calm negative space, lower 30% clean, zero birds, zero bird nests, zero feathers, zero text, zero hands.",
        "ratio": "9:16",
        "aspect": "9:16",
        "model": "BELUGA",
        "filename": "beat_05.png",
        "out_dir": "sys/runs/en-scale-and-bone-style-v2/images",
        "credit_cost": 1,
        "credit_reason": "image",
        "editorial_overlay": {"enabled": False},
        "_channel": "en-scale-and-bone",
        "_beat": 5,
    }
]

def main():
    logger.info("Regenerating 2 QA defect images...")
    # Use profile_6 (cdp_port 9227) which is healthy and free
    p6 = [p for p in PROFILES if p["name"] == "profile_6"]
    
    pool = PersistentWorkerPool(
        target_workers=1,
        cooldown_seconds=300.0,
        pacing_seconds=2.5,
        headless=True,
        profiles=p6
    )
    
    pool.start()
    for t in REGEN_TASKS:
        pool.submit_task(t, priority=0)
        
    pool.wait_completion(timeout=120.0)
    pool.shutdown()
    
    for t in REGEN_TASKS:
        png_p = Path(t["out_dir"]) / t["filename"]
        if png_p.exists():
            with Image.open(png_p) as im:
                w, h = im.size
                thumb_p = BRAIN_DIR / f"{t['_channel']}_0{t['_beat']}.jpg"
                resized = im.resize((540, int(round(540 * h / w))), Image.Resampling.LANCZOS)
                if resized.mode != "RGB":
                    resized = resized.convert("RGB")
                resized.save(thumb_p, format="JPEG", quality=90, optimize=True)
                logger.info("Successfully updated thumbnail: %s", thumb_p)
        else:
            logger.error("Failed regenerating %s", t["id"])

if __name__ == "__main__":
    main()
