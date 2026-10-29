#!/usr/bin/env python3
"""Generate all 33 images and thumbnail for revision 7 of survivorship-bias-16x9.

Strict requirements:
- 100% brand-new assets, zero reuse of old video images
- 2D Indie Doodle contract (1.7.0 handdrawn_2d_explainer / NanoBanana2Lite)
- Distributed across healthy Flow CDP profiles with ProfileLifecycleManager(auto_teardown=True)
- Verified sidecars, sha256 manifests, and output.json
"""
import asyncio
import hashlib
import json
import logging
import os
import shutil
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
logger = logging.getLogger("generate_images_revision_7")

ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "sys/runs/survivorship-bias-16x9"
OUT_DIR = RUN_DIR / "revisions/images/7_new_doodle"
CONTENT_PATH = RUN_DIR / "revisions/content/4/content.json"
BRIEF_PATH = RUN_DIR / "briefs/4.json"

HEALTHY_PROFILE_NAMES = [
    "profile_1", "profile_4", "profile_5", "profile_6", "profile_8",
    "profile_9", "profile_10", "profile_13", "profile_14", "profile_15",
    "profile_16", "profile_17", "profile_18", "profile_19", "profile_20"
]


def build_all_items():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONTENT_PATH, encoding="utf-8") as f:
        content = json.load(f)

    with open(BRIEF_PATH, encoding="utf-8") as f:
        brief = json.load(f)

    items = []
    for sc in content["scenes"]:
        for img in sc["images"]:
            req_id = img["id"]
            target_jpg = OUT_DIR / f"{req_id}_16x9.jpg"
            target_json = OUT_DIR / f"{req_id}_16x9.json"

            compiled = compile_flow_prompt(
                "NanoBanana2Lite",
                "scene",
                {
                    "description": img["description"],
                    "aspect_ratio": "16:9",
                    "allowed_text": img.get("visible_text", []),
                    "shot_type": img.get("shot_type", "full_scene"),
                    "has_character": True,
                    "character_free": False,
                },
                version="1.7.0",
            )
            items.append({
                "id": req_id,
                "job_id": req_id,
                "prompt": compiled["prompt"],
                "target_jpg": target_jpg,
                "target_json": target_json,
                "is_thumb": False,
            })

    # Add Thumbnail item
    thumb_jpg = OUT_DIR / "THUMBNAIL_16x9.jpg"
    thumb_json = OUT_DIR / "THUMBNAIL_16x9.json"
    thumb_spec = brief["packaging"]["thumbnail_spec"]
    thumb_compiled = compile_flow_prompt(
        "NanoBanana2Lite",
        "scene",
        {
            "description": thumb_spec["thumbnail_prompt"],
            "aspect_ratio": "16:9",
            "allowed_text": ["BẪY NGƯỜI SỐNG SÓT"],
            "shot_type": "full_scene",
            "has_character": True,
            "character_free": False,
        },
        version="1.7.0",
    )
    items.append({
        "id": "THUMBNAIL_16x9",
        "job_id": "THUMBNAIL_16x9",
        "prompt": thumb_compiled["prompt"],
        "target_jpg": thumb_jpg,
        "target_json": thumb_json,
        "is_thumb": True,
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
            # Skip if already generated successfully
            if item["target_jpg"].is_file() and item["target_jpg"].stat().st_size > 5000 and item["target_json"].is_file():
                continue

            if idx > 0:
                await asyncio.sleep(4.0)
            try:
                await process_item_on_session(sess, prof_name, item)
            except Exception as ex:
                logger.warning(f"Error on {prof_name} for {item['id']}: {ex}")
                failed_queue.append(item)
                if "BLOCKED" in str(ex) or "CAPTCHA" in str(ex) or "UNUSUAL_ACTIVITY" in str(ex):
                    logger.error(f"Quarantining {prof_name} due to block/captcha")
                    for rem in items_to_process[idx+1:]:
                        failed_queue.append(rem)
                    break
    except Exception as ex:
        logger.warning(f"Worker {prof_name} connection failed: {ex}")
        for rem in items_to_process:
            if not rem["target_jpg"].is_file() or rem["target_jpg"].stat().st_size < 5000:
                failed_queue.append(rem)
    finally:
        if sess and sess.ws:
            try:
                await sess.ws.close()
            except Exception:
                pass


def build_final_output_manifest():
    logger.info("Building images.json and output.json for revision 7...")
    with open(CONTENT_PATH, encoding="utf-8") as f:
        content = json.load(f)

    content_hash = hashlib.sha256(CONTENT_PATH.read_bytes()).hexdigest()
    manifest_items = []
    files_list = []

    for sc in content["scenes"]:
        sc_id = sc["id"]
        for img in sc["images"]:
            img_id = img["id"]
            jpg_file = OUT_DIR / f"{img_id}_16x9.jpg"
            json_file = OUT_DIR / f"{img_id}_16x9.json"

            if not jpg_file.is_file():
                raise FileNotFoundError(f"Missing {jpg_file}")
            if not json_file.is_file():
                raise FileNotFoundError(f"Missing {json_file}")

            sidecar = json.loads(json_file.read_text(encoding="utf-8"))
            jpg_sha = hashlib.sha256(jpg_file.read_bytes()).hexdigest()
            rel_jpg = f"revisions/images/7_new_doodle/{img_id}_16x9.jpg"
            rel_json = f"revisions/images/7_new_doodle/{img_id}_16x9.json"

            files_list.append(rel_jpg)
            files_list.append(rel_json)

            manifest_items.append({
                "scene_id": sc_id,
                "path": rel_jpg,
                "prompt": img["description"],
                "source": "google-flow-browser",
                "actual_prompt": sidecar.get("prompt", ""),
                "sha256": jpg_sha,
                "image_id": img_id,
                "ratio": "16:9",
                "forge_id": sidecar.get("forgeId", ""),
                "profile_id": sidecar.get("profile_id", "profile_1"),
            })

    # Add thumbnail files
    thumb_jpg = OUT_DIR / "THUMBNAIL_16x9.jpg"
    thumb_json = OUT_DIR / "THUMBNAIL_16x9.json"
    if thumb_jpg.is_file():
        files_list.append("revisions/images/7_new_doodle/THUMBNAIL_16x9.jpg")
    if thumb_json.is_file():
        files_list.append("revisions/images/7_new_doodle/THUMBNAIL_16x9.json")

    payload = {
        "schema_version": "2.0",
        "checkpoint": "final",
        "content_hash": content_hash,
        "signature": hashlib.sha256(json.dumps([m["sha256"] for m in manifest_items]).encode()).hexdigest(),
        "items": manifest_items,
    }

    images_manifest_file = OUT_DIR / "images.json"
    images_manifest_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    output_manifest = {
        "schema_version": "1.0",
        "job_id": "survivorship-bias-16x9",
        "module": "images",
        "revision": 7,
        "input_versions": {
            "content": content_hash,
        },
        "files": files_list,
        "payload": payload,
    }

    output_file = OUT_DIR / "output.json"
    output_file.write_text(json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Symlink 7 -> 7_new_doodle
    symlink_path = RUN_DIR / "revisions/images/7"
    if symlink_path.is_symlink() or symlink_path.exists():
        symlink_path.unlink()
    symlink_path.symlink_to("7_new_doodle")

    logger.info(f"Successfully generated revision 7 manifest with {len(manifest_items)} images and symlink 7 -> 7_new_doodle")


async def main_async():
    all_items = build_all_items()
    needed = [
        item for item in all_items
        if not (item["target_jpg"].is_file() and item["target_jpg"].stat().st_size > 5000 and item["target_json"].is_file())
    ]
    logger.info(f"Total items to generate: {len(needed)} / {len(all_items)}")

    if needed:
        healthy_cfgs = [p for p in PROFILES if p["name"] in HEALTHY_PROFILE_NAMES]
        logger.info(f"Using {len(healthy_cfgs)} healthy profiles")

        # Distribute items evenly among profiles
        prof_assignments = {p["name"]: [] for p in healthy_cfgs}
        for idx, item in enumerate(needed):
            p_name = healthy_cfgs[idx % len(healthy_cfgs)]["name"]
            prof_assignments[p_name].append(item)

        failed_queue = []
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

            if failed_queue:
                logger.warning(f"Retrying {len(failed_queue)} failed items...")
                retry_profs = [p for p in healthy_cfgs if p["name"] in ["profile_1", "profile_4", "profile_5", "profile_8", "profile_9", "profile_10"]]
                for item in failed_queue:
                    if item["target_jpg"].is_file() and item["target_jpg"].stat().st_size > 5000:
                        continue
                    for rp in retry_profs:
                        sub_failed = []
                        await run_worker(rp, [item], sub_failed)
                        if item["target_jpg"].is_file() and item["target_jpg"].stat().st_size > 5000:
                            break

    rem = [
        item for item in all_items
        if not (item["target_jpg"].is_file() and item["target_jpg"].stat().st_size > 5000 and item["target_json"].is_file())
    ]
    if rem:
        logger.error(f"Still missing {len(rem)} items after run: {[r['id'] for r in rem]}")
        return 1

    build_final_output_manifest()
    return 0


if __name__ == "__main__":
    ret = asyncio.run(main_async())
    sys.exit(ret)
