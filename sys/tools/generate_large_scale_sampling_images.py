#!/usr/bin/env python3
"""Generate 2D Indie Doodle scene images and thumbnail for Large-Scale Sampling jobs via Flow CDP.

Strict Requirements:
- 2D Indie Doodle contract (1.7.0 handdrawn_2d_explainer / NanoBanana2Lite)
- BELUGA model via DirectCDPProfileSession
- Verified sidecars (.json with forgeId/media_id), PIL verification, and output.json
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import shutil
import socket
import sys
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession, ensure_chrome_profiles_launched
from flow_prompts import compile as compile_flow_prompt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_large_scale_sampling_images")

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex(("127.0.0.1", port)) == 0


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
        return True
    except Exception:
        return False


async def generate_single_item(sess: DirectCDPProfileSession, prof_name: str, item: dict) -> None:
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

    target_size = (1080, 1920) if item["aspect"] == "9:16" else (1920, 1080)
    with Image.open(item["target_jpg"]) as im:
        if im.size != target_size:
            im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
            im_resized.save(item["target_jpg"], format="JPEG", quality=95)
        else:
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
    logger.info(f"Saved {item['target_jpg']} ({target_size}) and sidecar")


def build_manifest_and_finalize(job_name: str, ratio: str, out_dir: Path, content: dict, content_hash: str) -> None:
    ratio_slug = ratio.replace(":", "x")
    logger.info(f"Building images.json and output.json for {job_name} ({ratio})...")

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
    (run_dir / "images.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if thumb_jpg.is_file():
        shutil.copy2(thumb_jpg, run_dir / f"thumbnail_{ratio_slug}.jpg")

    logger.info(f"Successfully generated images manifest with {len(manifest_items)} scene images and thumbnail!")


async def ensure_session_ready(prof_cfg: dict, max_retries: int = 5) -> DirectCDPProfileSession:
    port = prof_cfg["cdp_port"]
    p_name = prof_cfg["name"]
    for attempt in range(max_retries):
        try:
            if not is_port_open(port):
                logger.info(f"Port {port} for {p_name} is closed. Launching Chrome profile...")
                ensure_chrome_profiles_launched([prof_cfg])
                for _ in range(30):
                    if is_port_open(port):
                        break
                    await asyncio.sleep(0.5)
                await asyncio.sleep(2.5)

            for _ in range(20):
                try:
                    get_flow_target(port)
                    break
                except Exception:
                    await asyncio.sleep(0.5)

            sess = DirectCDPProfileSession(prof_cfg)
            await sess.connect()
            ready = await sess._wait_for_flow_ready(timeout=25.0)
            if ready.get("hasAt") and (ready.get("hasPristine") or ready.get("hasExec")):
                logger.info(f"Session for {p_name} is fully ready (hasAt=True, readyState={ready.get('readyState')})")
                return sess
            logger.warning(f"Session for {p_name} not ready yet (ready={ready}), retrying...")
            await sess.close()
        except Exception as e:
            logger.warning(f"Connection attempt {attempt+1} failed: {e}")
            await asyncio.sleep(2.5)
    raise RuntimeError(f"Could not establish ready Flow session for {p_name}")


async def main_async(job_name: str, ratio: str, profile_name: str = "profile_1", force: bool = False) -> None:
    run_dir = SYS_DIR / "runs" / job_name
    content_file = run_dir / "content.json"
    content_hash = hashlib.sha256(content_file.read_bytes()).hexdigest()
    out_dir = run_dir / "revisions/images/1"

    items, brief, content = build_all_items(job_name, ratio, out_dir)
    pending_items = [it for it in items if force or not is_item_valid_on_disk(it)]
    logger.info(f"Total items: {len(items)}, Pending generation: {len(pending_items)}")

    if not pending_items:
        logger.info("All items already generated! Rebuilding manifests...")
        build_manifest_and_finalize(job_name, ratio, out_dir, content, content_hash)
        return

    prof_cfg = next((p for p in PROFILES if p["name"] == profile_name), None)
    if not prof_cfg:
        raise ValueError(f"Profile {profile_name} not found in PROFILES configuration")

    sess = await ensure_session_ready(prof_cfg)
    try:
        for idx, it in enumerate(pending_items, 1):
            logger.info(f"[{idx}/{len(pending_items)}] Processing {it['id']} on {profile_name}...")
            success = False
            for attempt in range(1, 5):
                try:
                    if sess is None or sess._is_closed():
                        if sess is not None:
                            try:
                                await sess.close()
                            except Exception:
                                pass
                        sess = await ensure_session_ready(prof_cfg)

                    await generate_single_item(sess, profile_name, it)
                    success = True
                    break
                except Exception as ex:
                    logger.warning(f"Failed {it['id']} attempt {attempt} on {profile_name}: {ex}")
                    if sess is not None:
                        try:
                            await sess.close()
                        except Exception:
                            pass
                        sess = None
                    await asyncio.sleep(3.0)
            if not success:
                raise RuntimeError(f"Failed to generate image for {it['id']}")
            # Small pace pause between requests
            await asyncio.sleep(2.0)
    finally:
        if sess is not None:
            try:
                await sess.close()
            except Exception:
                pass

    build_manifest_and_finalize(job_name, ratio, out_dir, content, content_hash)


def main():
    parser = argparse.ArgumentParser(description="Generate 2D Indie Doodle images for Large-Scale Sampling")
    parser.add_argument("--job", default="large-scale-sampling-9x16", help="Job name")
    parser.add_argument("--ratio", default="9:16", help="Aspect ratio (9:16 or 16:9)")
    parser.add_argument("--profile", default="profile_1", help="Target Chrome profile name")
    parser.add_argument("--force", action="store_true", help="Force re-generation of all images")
    args = parser.parse_args()

    asyncio.run(main_async(args.job, args.ratio, profile_name=args.profile, force=args.force))


if __name__ == "__main__":
    main()
