#!/usr/bin/env python3
"""Generate alternative 2D Indie Doodle thumbnails for Survivorship Bias 16x9 explainer via Flow CDP."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import sys
import urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
sys.path.insert(0, str(SYS_DIR))

from flow_prompts import compile as compile_flow_prompt
from flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession, ensure_chrome_profiles_launched
from flow_cdp.lifecycle import ProfileLifecycleManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_thumbnails")

DELIV_DIR = ROOT / "video/survivorship-bias-16x9"
DELIV_DIR.mkdir(parents=True, exist_ok=True)

THUMBNAIL_SPECS = [
    {
        "id": "thumbnail_option1_plane_bias",
        "title": "Tùy chọn 1: Máy bay Abraham Wald & Bẫy Người Sống Sót (Kinh điển, chuẩn học thuật đại chúng)",
        "allowed_text": ["BẪY NGƯỜI SỐNG SÓT"],
        "description": (
            "16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream (#F8F0DC) stage with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "In the center: A large iconic 2D doodle WW2 propeller bomber airplane seen from directly above. "
            "Both wings and the tail are covered in distinct red marker bullet holes (#EF4444). "
            "The central engine area is completely pristine with zero bullet holes, protected by a glowing hand-drawn golden shield (#FACC15). "
            "On the left: The iconic white circle-head doodle stickman in blue shirt (#3B82C4) with wide shocked spiral eyes points with a wire stick arm directly at the clean engine. "
            "Clean minimalist staging with over 60% open negative space, zero 3D, zero shadows, zero walls. "
            "Top-center bold hand-drawn golden-yellow (#FACC15) uppercase Vietnamese lettering 'BẪY NGƯỜI SỐNG SÓT' with thick pitch-black (#000000) marker outline."
        ),
    },
    {
        "id": "thumbnail_option2_cang_cay_cang_ngheo",
        "title": "Tùy chọn 2: Nghịch lý cày cuốc 16h vs Kẻ thắng cuộc (Đánh trúng nỗi đau, CTR cao)",
        "allowed_text": ["CÀNG CÀY CÀNG NGHÈO"],
        "description": (
            "16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream (#F8F0DC) stage with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "On the left: The iconic white circle-head doodle stickman in blue shirt (#3B82C4) collapses completely face-down on a simple crooked wooden desk, dizzy spiral eyes, sweat drops flying, beside an alarm clock ringing at 16H. "
            "On the right: A giant flashy billboard where another smiling doodle stickman in a tuxedo steps out of a luxury car holding a golden trophy. "
            "Clean minimalist composition with 60% open cream negative space, zero 3D, zero drop shadows. "
            "Top-center bold hand-drawn vibrant red-orange (#EF4444) uppercase Vietnamese lettering 'CÀNG CÀY CÀNG NGHÈO' with thick pitch-black (#000000) marker outline."
        ),
    },
    {
        "id": "thumbnail_option3_plane_cu_lua",
        "title": "Tùy chọn 3: Cú Lừa 80 Năm (Kích thích tò mò cực đại)",
        "allowed_text": ["CÚ LỪA 80 NĂM"],
        "description": (
            "16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream (#F8F0DC) stage with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "In the center: A large iconic 2D doodle WW2 propeller bomber airplane seen from directly above. "
            "Both wings and tail are covered with red marker bullet holes (#EF4444). "
            "The central engine is clean, marked with a hand-drawn question mark (?) in a bright yellow circle (#FACC15). "
            "On the left: A military general stickman in army cap foolishly hammers armor onto the wing with bullet holes. "
            "On the right: The blue-shirt stickman screams and points urgently at the clean engine. "
            "Clean minimalist stage with 60% open cream negative space, zero 3D gradients. "
            "Top-center bold hand-drawn golden-yellow (#FACC15) uppercase Vietnamese lettering 'CÚ LỪA 80 NĂM' with thick pitch-black outline."
        ),
    },
]


async def generate_single_thumbnail(sess: DirectCDPProfileSession, prof_name: str, spec: dict) -> Path:
    item_id = spec["id"]
    target_jpg = DELIV_DIR / f"{item_id}.jpg"
    target_json = DELIV_DIR / f"{item_id}.json"

    logger.info(f"Compiling Flow prompt for {item_id}...")
    compiled = compile_flow_prompt(
        "NanoBanana2Lite",
        "scene",
        {
            "description": spec["description"],
            "aspect_ratio": "16:9",
            "allowed_text": spec["allowed_text"],
            "shot_type": "full_scene",
            "has_character": True,
            "character_free": False,
        },
        version="1.7.0",
    )

    logger.info(f"Generating {item_id} via Flow CDP on {prof_name}...")
    res = await sess.generate_image(prompt=compiled["prompt"], aspect="16:9", model="BELUGA")
    media_id = res.get("media_id", "")
    url = res.get("url", "")
    if not url:
        raise RuntimeError(f"No image URL returned from Flow for {item_id}")

    logger.info(f"Downloading image from {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()

    if len(data) < 5000:
        raise RuntimeError(f"Image data too small: {len(data)} bytes")

    target_jpg.write_bytes(data)
    with Image.open(target_jpg) as im:
        im.verify()

    sidecar = {
        "jobId": item_id,
        "type": "image",
        "prompt": compiled["prompt"],
        "ratio": "16:9",
        "source": "google-flow-browser",
        "status": "downloaded",
        "forgeId": media_id,
        "profile_id": prof_name,
        "spec": spec,
    }
    target_json.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Successfully saved {target_jpg} ({len(data)} bytes, media_id: {media_id})")
    return target_jpg


async def main():
    # Pick healthy profile 1 or profile 4
    prof_cfg = PROFILES[0]  # profile_1 port 9225
    prof_name = prof_cfg["name"]

    logger.info(f"Launching session on {prof_name}...")
    ensure_chrome_profiles_launched([prof_cfg], headless=True)
    await asyncio.sleep(2.0)

    sess = DirectCDPProfileSession(prof_cfg)
    await sess.connect()
    await sess._wait_for_flow_ready(timeout=25.0)

    generated_paths = []
    for spec in THUMBNAIL_SPECS:
        try:
            p = await generate_single_thumbnail(sess, prof_name, spec)
            generated_paths.append((spec, p))
            await asyncio.sleep(3.0)
        except Exception as e:
            logger.error(f"Failed to generate {spec['id']}: {e}")

    await sess.close()

    if generated_paths:
        # Default the first one as master thumbnail_16x9.jpg
        default_thumb = generated_paths[0][1]
        shutil.copy2(default_thumb, DELIV_DIR / "thumbnail_16x9.jpg")
        shutil.copy2(default_thumb, DELIV_DIR / "THUMBNAIL_16x9.jpg")
        logger.info(f"Updated default master thumbnail: {DELIV_DIR / 'thumbnail_16x9.jpg'}")


if __name__ == "__main__":
    asyncio.run(main())
