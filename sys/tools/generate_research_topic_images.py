#!/usr/bin/env python3
"""Generate 2D Indie Doodle scene images and thumbnail for Research Topic Size jobs via Flow CDP.

Strict Requirements:
- 2D Indie Doodle contract (1.7.0 handdrawn_2d_explainer / NanoBanana2Lite)
- Distributed across healthy Flow CDP profiles with ProfileLifecycleManager(auto_teardown=True)
- Verified sidecars (.json with forgeId/media_id), PIL verification, and output.json
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import shutil
import sys
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession, ensure_chrome_profiles_launched
from flow_cdp.lifecycle import ProfileLifecycleManager
from flow_prompts import compile as compile_flow_prompt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_research_topic_images")

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"

HEALTHY_PROFILE_NAMES = [
    "profile_1", "profile_4", "profile_5", "profile_8",
    "profile_9", "profile_10", "profile_13", "profile_14", "profile_15",
    "profile_16", "profile_17", "profile_18", "profile_19", "profile_20",
]


def build_all_items(job_name: str, ratio: str, out_dir: Path) -> tuple[list[dict], dict, dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    run_dir = SYS_DIR / "runs" / job_name
    content_path = run_dir / "content.json"
    brief_path = run_dir / "brief.json"

    with open(content_path, encoding="utf-8") as f:
        content = json.load(f)

    with open(brief_path, encoding="utf-8") as f:
        brief = json.load(f)

    ratio_slug = ratio.replace(":", "x")
    items = []
    for sc in content["scenes"]:
        for img in sc["images"]:
            req_id = img["id"]
            target_jpg = out_dir / f"{req_id}_{ratio_slug}.jpg"
            target_json = out_dir / f"{req_id}_{ratio_slug}.json"

            shot = img.get("shot_type", "full_scene")
            if shot == "variation":
                shot = "full_scene"

            compiled = compile_flow_prompt(
                "NanoBanana2Lite",
                "scene",
                {
                    "description": img["description"],
                    "aspect_ratio": ratio,
                    "allowed_text": img.get("visible_text", []),
                    "shot_type": shot,
                    "has_character": img.get("has_character", True),
                    "character_free": not img.get("has_character", True),
                },
                version="1.7.0",
            )
            items.append({
                "id": req_id,
                "scene_id": sc["id"],
                "job_id": req_id,
                "prompt": compiled["prompt"],
                "target_jpg": target_jpg,
                "target_json": target_json,
                "is_thumb": False,
                "aspect": ratio,
                "description": img["description"],
            })

    # Add Thumbnail item
    thumb_id = f"THUMBNAIL_{ratio_slug}"
    thumb_jpg = out_dir / f"{thumb_id}.jpg"
    thumb_json = out_dir / f"{thumb_id}.json"
    thumb_spec = brief["packaging"]["thumbnail_spec"]
    thumb_compiled = compile_flow_prompt(
        "NanoBanana2Lite",
        "scene",
        {
            "description": thumb_spec["thumbnail_prompt"],
            "aspect_ratio": ratio,
            "allowed_text": [thumb_spec["text_overlay"]],
            "shot_type": "full_scene",
            "has_character": True,
            "character_free": False,
        },
        version="1.7.0",
    )
    items.append({
        "id": thumb_id,
        "scene_id": "THUMBNAIL",
        "job_id": thumb_id,
        "prompt": thumb_compiled["prompt"],
        "target_jpg": thumb_jpg,
        "target_json": thumb_json,
        "is_thumb": True,
        "aspect": ratio,
        "description": thumb_spec["thumbnail_prompt"],
    })

    return items, brief, content


async def process_item_on_session(sess: DirectCDPProfileSession, prof_name: str, item: dict) -> None:
    logger.info(f"Generating {item['id']} ({item['aspect']}) on {prof_name}...")
    res = await sess.generate_image(prompt=item["prompt"], aspect=item["aspect"], model="BELUGA")
    media_id = res.get("media_id", "")
    url = res.get("url", "")
    if not url:
        raise RuntimeError(f"No image URL returned from Flow for {item['id']}")

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
        "ratio": item["aspect"],
        "source": "google-flow-browser",
        "status": "downloaded",
        "forgeId": media_id,
        "profile_id": prof_name,
    }
    item["target_json"].write_text(json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(f"Saved {item['target_jpg']} ({len(data)} bytes) and sidecar")


def is_item_valid_on_disk(item: dict) -> bool:
    jpg = item["target_jpg"]
    js = item["target_json"]
    if not jpg.is_file() or not js.is_file():
        return False
    if jpg.stat().st_size < 5000:
        return False
    try:
        with Image.open(jpg) as im:
            im.verify()
        data = json.loads(js.read_text(encoding="utf-8"))
        if not data.get("forgeId"):
            return False
        if data.get("prompt") != item["prompt"]:
            return False
        return True
    except Exception:
        return False


async def run_worker(prof_cfg: dict, items_to_process: list[dict], failed_queue: list[dict], force: bool = False) -> None:
    prof_name = prof_cfg["name"]
    logger.info(f"Starting worker {prof_name} with {len(items_to_process)} items")
    sess = None
    try:
        ensure_chrome_profiles_launched([prof_cfg], headless=True)
        await asyncio.sleep(2.0)
        sess = DirectCDPProfileSession(prof_cfg)
        await sess.connect()

        for idx, item in enumerate(items_to_process):
            if not force and is_item_valid_on_disk(item):
                logger.info(f"Item {item['id']} already valid on disk, skipping")
                continue
            if idx > 0:
                await asyncio.sleep(3.0)
            try:
                await process_item_on_session(sess, prof_name, item)
            except Exception as ex:
                logger.warning(f"Error on {prof_name} for {item['id']}: {ex}")
                failed_queue.append(item)
                if any(w in str(ex).upper() for w in ("BLOCKED", "CAPTCHA", "UNUSUAL_ACTIVITY")):
                    logger.error(f"Quarantining {prof_name} due to security trigger")
                    for rem in items_to_process[idx + 1:]:
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


def build_final_output_manifest(job_name: str, ratio: str, out_dir: Path, content: dict) -> dict:
    logger.info(f"Building images.json and output.json for {job_name} ({ratio})...")
    ratio_slug = ratio.replace(":", "x")
    content_path = SYS_DIR / "runs" / job_name / "content.json"
    content_hash = hashlib.sha256(content_path.read_bytes()).hexdigest()
    manifest_items = []
    files_list = []

    for sc in content["scenes"]:
        sc_id = sc["id"]
        for img in sc["images"]:
            img_id = img["id"]
            jpg_file = out_dir / f"{img_id}_{ratio_slug}.jpg"
            json_file = out_dir / f"{img_id}_{ratio_slug}.json"

            if not jpg_file.is_file():
                raise FileNotFoundError(f"Missing {jpg_file}")
            if not json_file.is_file():
                raise FileNotFoundError(f"Missing {json_file}")

            sidecar = json.loads(json_file.read_text(encoding="utf-8"))
            jpg_sha = hashlib.sha256(jpg_file.read_bytes()).hexdigest()
            rel_jpg = f"revisions/images/1/{img_id}_{ratio_slug}.jpg"
            rel_json = f"revisions/images/1/{img_id}_{ratio_slug}.json"

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
                "ratio": ratio,
                "forge_id": sidecar.get("forgeId", ""),
                "profile_id": sidecar.get("profile_id", "profile_1"),
            })

    thumb_id = f"THUMBNAIL_{ratio_slug}"
    thumb_jpg = out_dir / f"{thumb_id}.jpg"
    thumb_json = out_dir / f"{thumb_id}.json"
    if thumb_jpg.is_file() and thumb_json.is_file():
        files_list.append(f"revisions/images/1/{thumb_id}.jpg")
        files_list.append(f"revisions/images/1/{thumb_id}.json")

    payload = {
        "checkpoint": "final",
        "items": manifest_items,
        "references": [],
        "proofs": [],
        "thumbnail": f"revisions/images/1/{thumb_id}.jpg" if thumb_jpg.is_file() else None,
        "format": ratio,
    }

    images_manifest_file = out_dir / "images.json"
    images_manifest_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    output_manifest = {
        "schema_version": "1.0",
        "job_id": job_name,
        "module": "images",
        "revision": 1,
        "input_versions": {
            "content": content_hash,
        },
        "files": files_list,
        "payload": payload,
    }

    output_file = out_dir / "output.json"
    output_file.write_text(json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    run_dir = SYS_DIR / "runs" / job_name
    shutil.copy2(images_manifest_file, run_dir / "images.json")
    if thumb_jpg.is_file():
        shutil.copy2(thumb_jpg, run_dir / f"thumbnail_{ratio_slug}.jpg")

    logger.info(f"Successfully generated images manifest with {len(manifest_items)} scene images and thumbnail!")
    return payload


async def generate_images_for_job(job_name: str, ratio: str, max_concurrency: int = 5, force: bool = False) -> int:
    out_dir = SYS_DIR / "runs" / job_name / "revisions/images/1"
    all_items, brief, content = build_all_items(job_name, ratio, out_dir)

    needed = [
        item for item in all_items
        if force or not is_item_valid_on_disk(item)
    ]
    logger.info(f"Job: {job_name} ({ratio}) — Total items to generate: {len(needed)} / {len(all_items)}")

    if needed:
        healthy_cfgs = [p for p in PROFILES if p["name"] in HEALTHY_PROFILE_NAMES]
        logger.info(f"Using {len(healthy_cfgs)} healthy Flow profiles with max_concurrency={max_concurrency}")

        prof_assignments = {p["name"]: [] for p in healthy_cfgs}
        for idx, item in enumerate(needed):
            p_name = healthy_cfgs[idx % len(healthy_cfgs)]["name"]
            prof_assignments[p_name].append(item)

        failed_queue = []
        batch_size = min(max_concurrency, len(healthy_cfgs))

        with ProfileLifecycleManager(auto_teardown=True):
            for i in range(0, len(healthy_cfgs), batch_size):
                batch_profs = healthy_cfgs[i:i + batch_size]
                tasks = []
                for prof in batch_profs:
                    items_for_p = prof_assignments[prof["name"]]
                    if items_for_p:
                        tasks.append(run_worker(prof, items_for_p, failed_queue, force=force))
                if tasks:
                    logger.info(f"--- Running batch {i // batch_size + 1} with {len(tasks)} workers ---")
                    await asyncio.gather(*tasks)

            if failed_queue:
                logger.warning(f"Retrying {len(failed_queue)} failed items...")
                retry_profs = [p for p in healthy_cfgs if p["name"] in ["profile_1", "profile_4", "profile_5", "profile_8", "profile_9", "profile_10"]]
                for item in failed_queue:
                    if not force and is_item_valid_on_disk(item):
                        continue
                    for rp in retry_profs:
                        sub_failed = []
                        await run_worker(rp, [item], sub_failed, force=force)
                        if is_item_valid_on_disk(item):
                            break

    rem = [
        item for item in all_items
        if not is_item_valid_on_disk(item)
    ]
    if rem:
        logger.error(f"Still missing or invalid {len(rem)} items after run: {[r['id'] for r in rem]}")
        return 1

    build_final_output_manifest(job_name, ratio, out_dir, content)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Generate 2D Indie Doodle Images for Research Topic Size jobs")
    parser.add_argument("job", nargs="?", default="research-topic-size-16x9", choices=["research-topic-size-16x9", "research-topic-size-9x16"], help="Job identifier")
    parser.add_argument("--ratio", default=None, choices=["16:9", "9:16"], help="Aspect ratio")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent profile workers")
    parser.add_argument("--force", action="store_true", help="Force regenerate all images even if cached on disk")
    args = parser.parse_args()

    job_name = args.job
    ratio = args.ratio or ("9:16" if "9x16" in job_name else "16:9")
    ret = asyncio.run(generate_images_for_job(job_name, ratio, max_concurrency=args.concurrency, force=args.force))
    sys.exit(ret)


if __name__ == "__main__":
    main()
