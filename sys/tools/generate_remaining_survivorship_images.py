#!/usr/bin/env python3
"""Generate the remaining 35 images for survivorship-bias-16x9 revision 5 using healthy Flow CDP profiles."""
import asyncio
import json
import logging
import os
import sys
import time
import urllib.request
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_prompts import compile as compile_flow_prompt
from flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession, ensure_chrome_profiles_launched
from flow_cdp.lifecycle import ProfileLifecycleManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_remaining")

HEALTHY_PROFILE_NAMES = [
    "profile_1", "profile_4", "profile_5", "profile_6", "profile_8",
    "profile_9", "profile_10", "profile_13", "profile_14", "profile_15",
    "profile_16", "profile_17", "profile_18", "profile_19", "profile_20"
]

OUT_DIR = Path("sys/runs/survivorship-bias-16x9/revisions/images/5_full_doodle")
CONTENT_PATH = Path("sys/runs/survivorship-bias-16x9/revisions/content/2/content.json")

def build_missing_items():
    with open(CONTENT_PATH, encoding="utf-8") as f:
        content = json.load(f)

    img_map = {}
    for sc in content["scenes"]:
        for img in sc["images"]:
            img_map[img["id"]] = img

    all_reqs = [
        "SC04_I11", "SC05_I1", "SC05_I2", "SC07_I2", "SC07_I3", "SC07_I4",
        "SC09_I3", "SC09_I4", "SC09_I5", "SC10_I2", "SC10_I3", "SC10_I4",
        "SC10_I5", "SC10_I6", "SC10_I7", "SC10_I8", "SC11_I1", "SC11_I2",
        "SC11_I3", "SC11_I4", "SC11_I5", "SC11_I6", "SC11_I7", "SC11_I8",
        "SC11_I9", "SC11_I10", "SC12_I1", "SC12_I2", "SC12_I3", "SC12_I4",
        "SC12_I5", "SC12_I6", "SC12_I7", "SC12_I8", "SC12_I9", "THUMB"
    ]

    items = []
    for req_id in all_reqs:
        target_jpg = OUT_DIR / ("THUMBNAIL_16x9.jpg" if req_id == "THUMB" else f"{req_id}_16x9.jpg")
        target_json = OUT_DIR / ("THUMBNAIL_16x9.json" if req_id == "THUMB" else f"{req_id}_16x9.json")
        if target_jpg.is_file() and target_jpg.stat().st_size > 5000 and target_json.is_file():
            continue  # Already downloaded & valid

        if req_id == "THUMB":
            visual_data = {
                "description": "Raw freehand 2D Vietnamese indie doodle on a flat slate-navy (#2E4361) stage: a white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) looks up at one golden trophy inside a bright yellow spotlight cone while standing above a deep ocean trench filled with sunken propeller bomber planes",
                "aspect_ratio": "16:9",
                "allowed_text": [{"text": "BẪY NGƯỜI SỐNG SÓT", "placement": "top center bold banner", "object": "banner"}],
                "shot_type": "cutaway_detail",
                "has_character": True,
                "character_free": False,
                "change": ["Raw freehand 2D Vietnamese indie doodle on a flat slate-navy (#2E4361) stage: a white-head doodle stickman in a casual cerulean blue shirt (#3B82C4) looks up at one golden trophy inside a bright yellow spotlight cone while standing above a deep ocean trench filled with sunken propeller bomber planes"],
                "preserve": [],
            }
            compiled = compile_flow_prompt("NanoBanana2Lite", "scene", visual_data, version="1.7.0")
            prompt_text = compiled["prompt"]
            job_id = "THUMBNAIL"
        else:
            img = img_map[req_id]
            compiled = compile_flow_prompt(
                "NanoBanana2Lite",
                "scene",
                {
                    "description": img["description"],
                    "aspect_ratio": "16:9",
                    "allowed_text": img.get("visible_text", []),
                    "shot_type": img["shot_type"],
                    "has_character": bool(img.get("has_character", False)),
                    "character_free": not bool(img.get("has_character", False)),
                },
                version="1.7.0",
            )
            prompt_text = compiled["prompt"]
            job_id = req_id

        items.append({
            "id": req_id,
            "job_id": job_id,
            "prompt": prompt_text,
            "target_jpg": target_jpg,
            "target_json": target_json,
        })
    return items


async def process_item_on_session(sess, prof_name, item):
    logger.info(f"Generating {item['id']} on {prof_name}...")
    res = await sess.generate_image(prompt=item["prompt"], aspect="16:9", model="BELUGA")
    media_id = res["media_id"]
    url = res["url"]

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if len(data) < 5000:
        raise RuntimeError(f"Image data too small: {len(data)} bytes")

    item["target_jpg"].write_bytes(data)
    with Image.open(item["target_jpg"]) as im:
        im.verify()

    sidecar = {
        "jobId": item["job_id"],
        "type": "image",
        "prompt": item["prompt"],
        "ratio": "16:9",
        "source": "google-flow-browser",
        "status": "downloaded",
        "forgeId": media_id,
        "profile_id": prof_name,
    }
    item["target_json"].write_text(json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"SUCCESS {item['id']} on {prof_name} ({len(data)} bytes, media_id: {media_id[:8]}...)")


async def run_worker(prof_cfg, items_to_process, failed_queue):
    prof_name = prof_cfg["name"]
    logger.info(f"Starting worker {prof_name} with {len(items_to_process)} items")
    sess = None
    try:
        ensure_chrome_profiles_launched([prof_cfg], headless=True)
        await asyncio.sleep(2.0)
        sess = DirectCDPProfileSession(prof_cfg)
        await sess.connect()
        await sess._wait_for_flow_ready(timeout=25.0)

        for idx, item in enumerate(items_to_process):
            if idx > 0:
                await asyncio.sleep(4.0)
            try:
                await process_item_on_session(sess, prof_name, item)
            except Exception as ex:
                logger.warning(f"Error on {prof_name} for {item['id']}: {ex}")
                failed_queue.append(item)
                # If blocked or captcha, don't continue on this profile
                if "BLOCKED" in str(ex) or "CAPTCHA" in str(ex) or "UNUSUAL_ACTIVITY" in str(ex):
                    logger.error(f"Quarantining {prof_name} due to block/captcha")
                    # Append remaining items to failed_queue
                    for rem in items_to_process[idx+1:]:
                        failed_queue.append(rem)
                    break
    except Exception as ex:
        logger.warning(f"Worker {prof_name} connection failed: {ex}")
        for rem in items_to_process:
            if not rem["target_jpg"].is_file():
                failed_queue.append(rem)
    finally:
        if sess and sess.ws:
            try:
                await sess.ws.close()
            except Exception:
                pass


async def main_async():
    missing_items = build_missing_items()
    logger.info(f"Total missing items to generate: {len(missing_items)}")
    if not missing_items:
        logger.info("All images are already generated!")
        return 0

    healthy_cfgs = [p for p in PROFILES if p["name"] in HEALTHY_PROFILE_NAMES]
    logger.info(f"Using {len(healthy_cfgs)} healthy profiles: {[p['name'] for p in healthy_cfgs]}")

    # Distribute missing items across healthy profiles
    prof_assignments = {p["name"]: [] for p in healthy_cfgs}
    for idx, item in enumerate(missing_items):
        p_name = healthy_cfgs[idx % len(healthy_cfgs)]["name"]
        prof_assignments[p_name].append(item)

    failed_queue = []

    # Run in batches of at most 5 profiles concurrently to manage RAM
    batch_size = 5
    with ProfileLifecycleManager(auto_teardown=True):
        for i in range(0, len(healthy_cfgs), batch_size):
            batch_profs = healthy_cfgs[i:i + batch_size]
            tasks = []
            for prof in batch_profs:
                items_for_p = prof_assignments[prof["name"]]
                if items_for_p:
                    tasks.append(run_worker(prof, items_for_p, failed_queue))
            if tasks:
                logger.info(f"--- Running batch {i//batch_size + 1} with {len(tasks)} workers ---")
                await asyncio.gather(*tasks)

        # Retry failed items on healthy profiles if any failed
        if failed_queue:
            logger.warning(f"Retrying {len(failed_queue)} failed items...")
            retry_profs = [p for p in healthy_cfgs if p["name"] not in ["profile_12", "profile_2", "profile_3", "profile_7"]]
            for item in failed_queue:
                if item["target_jpg"].is_file() and item["target_jpg"].stat().st_size > 5000:
                    continue
                # Pick a retry profile
                for rp in retry_profs:
                    sub_failed = []
                    await run_worker(rp, [item], sub_failed)
                    if item["target_jpg"].is_file() and item["target_jpg"].stat().st_size > 5000:
                        break

    # Final check
    rem = build_missing_items()
    logger.info(f"Finished generation run. Remaining missing items: {len(rem)}")
    return len(rem)


if __name__ == "__main__":
    ret = asyncio.run(main_async())
    sys.exit(ret)
