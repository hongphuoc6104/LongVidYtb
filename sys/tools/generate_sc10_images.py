#!/usr/bin/env python3
"""Generate the 3 SC10 Outro images via Flow CDP and build Revision 8 images."""
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

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
sys.path.insert(0, str(SYS_DIR))

from flow_prompts import compile as compile_flow_prompt
from flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession, ensure_chrome_profiles_launched

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_sc10")

RUN_DIR = SYS_DIR / "runs/survivorship-bias-16x9"
SRC_IMAGES_DIR = RUN_DIR / "revisions/images/7_new_doodle"
OUT_DIR = RUN_DIR / "revisions/images/8_with_outro"
CONTENT_PATH = RUN_DIR / "revisions/content/5/content.json"

OUT_DIR.mkdir(parents=True, exist_ok=True)


async def generate_item(sess, prof_name, item):
    logger.info(f"Generating {item['id']} on {prof_name}...")
    res = await sess.generate_image(prompt=item["prompt"], aspect="16:9", model="BELUGA")
    media_id = res["media_id"]
    url = res["url"]

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if len(data) < 5000:
        raise RuntimeError(f"Image data too small: {len(data)} bytes")

    target_jpg = OUT_DIR / f"{item['id']}_16x9.jpg"
    target_json = OUT_DIR / f"{item['id']}_16x9.json"

    target_jpg.write_bytes(data)
    with Image.open(target_jpg) as im:
        im.verify()

    sidecar = {
        "jobId": item["id"],
        "type": "image",
        "prompt": item["prompt"],
        "ratio": "16:9",
        "source": "google-flow-browser",
        "status": "downloaded",
        "forgeId": media_id,
        "profile_id": prof_name,
    }
    target_json.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"SUCCESS: {item['id']} ({len(data)} bytes, media_id: {media_id[:8]}...)")


async def main():
    # Step 1: Copy existing 34 images from 7_new_doodle to 8_with_outro
    logger.info("Copying existing images from 7_new_doodle -> 8_with_outro...")
    for f in SRC_IMAGES_DIR.iterdir():
        if f.name.endswith(".jpg") or f.name.endswith(".json") and f.name != "images.json":
            dest = OUT_DIR / f.name
            if not dest.is_file() or dest.stat().st_size != f.stat().st_size:
                shutil.copy2(f, dest)

    # Step 2: Load content.json and get SC10 beats
    with open(CONTENT_PATH, encoding="utf-8") as f:
        content = json.load(f)

    sc10 = next(s for s in content["scenes"] if s["id"] == "SC10")
    items_to_gen = []

    for img in sc10["images"]:
        target_jpg = OUT_DIR / f"{img['id']}_16x9.jpg"
        target_json = OUT_DIR / f"{img['id']}_16x9.json"
        if target_jpg.is_file() and target_jpg.stat().st_size > 5000 and target_json.is_file():
            logger.info(f"Already exists: {img['id']}")
            continue

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
        items_to_gen.append({
            "id": img["id"],
            "scene_id": "SC10",
            "prompt": compiled["prompt"],
            "description": img["description"]
        })

    if items_to_gen:
        logger.info(f"Generating {len(items_to_gen)} SC10 images with Flow CDP...")
        prof_cfg = PROFILES[0]  # profile_1
        ensure_chrome_profiles_launched([prof_cfg], headless=True)
        await asyncio.sleep(2.0)
        sess = DirectCDPProfileSession(prof_cfg)
        await sess.connect()
        ready = await sess._wait_for_flow_ready(timeout=25.0)
        logger.info(f"Flow ready on {prof_cfg['name']}: {bool(ready)}")

        try:
            for item in items_to_gen:
                await generate_item(sess, prof_cfg["name"], item)
                await asyncio.sleep(3.0)
        finally:
            await sess.close()

    # Step 3: Build master images.json for revision 8
    logger.info("Building images.json for revision 8...")
    manifest_items = []
    for sc in content["scenes"]:
        for img in sc["images"]:
            img_id = img["id"]
            jpg_path = OUT_DIR / f"{img_id}_16x9.jpg"
            json_path = OUT_DIR / f"{img_id}_16x9.json"
            if not jpg_path.is_file() or not json_path.is_file():
                raise FileNotFoundError(f"Missing {jpg_path} or {json_path}")

            sidecar = json.loads(json_path.read_text(encoding="utf-8"))
            sha = hashlib.sha256(jpg_path.read_bytes()).hexdigest()
            manifest_items.append({
                "scene_id": sc["id"],
                "path": f"revisions/images/8_with_outro/{img_id}_16x9.jpg",
                "prompt": img["description"],
                "source": "google-flow-browser",
                "actual_prompt": sidecar.get("prompt", ""),
                "sha256": sha,
                "image_id": img_id,
                "ratio": "16:9",
                "forge_id": sidecar.get("forgeId", ""),
                "profile_id": sidecar.get("profile_id", "profile_1"),
            })

    # Add thumbnail if exists
    thumb_jpg = OUT_DIR / "THUMBNAIL_16x9.jpg"
    thumb_json = OUT_DIR / "THUMBNAIL_16x9.json"
    if thumb_jpg.is_file() and thumb_json.is_file():
        sidecar = json.loads(thumb_json.read_text(encoding="utf-8"))
        sha = hashlib.sha256(thumb_jpg.read_bytes()).hexdigest()
        manifest_items.append({
            "scene_id": "THUMBNAIL",
            "path": "revisions/images/8_with_outro/THUMBNAIL_16x9.jpg",
            "prompt": sidecar.get("prompt", ""),
            "source": "google-flow-browser",
            "actual_prompt": sidecar.get("prompt", ""),
            "sha256": sha,
            "image_id": "THUMBNAIL",
            "ratio": "16:9",
            "forge_id": sidecar.get("forgeId", ""),
            "profile_id": sidecar.get("profile_id", "profile_1"),
        })

    content_hash = hashlib.sha256(Path(CONTENT_PATH).read_bytes()).hexdigest()
    images_manifest = {
        "schema_version": "2.0",
        "checkpoint": "final",
        "content_hash": content_hash,
        "signature": hashlib.sha256(f"rev8_{len(manifest_items)}".encode()).hexdigest(),
        "items": manifest_items,
    }

    images_json_path = OUT_DIR / "images.json"
    images_json_path.write_text(json.dumps(images_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Done! Saved {images_json_path} with {len(manifest_items)} items.")


if __name__ == "__main__":
    asyncio.run(main())
