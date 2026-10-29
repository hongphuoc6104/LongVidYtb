#!/usr/bin/env python3
"""Generate alternative thumbnail options for Reality Interface Paradox (16:9 and 9:16) via Flow CDP."""
import asyncio
import json
import logging
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
logger = logging.getLogger("generate_reality_thumbnails")

THUMBNAIL_SPECS = [
    {
        "id": "thumbnail_option2_coffee_16x9",
        "job": "reality-interface-paradox-16x9",
        "ratio": "16:9",
        "allowed_text": ["SỰ THẬT LÀ GIẢ"],
        "description": (
            "Orthographic 2D hand-drawn doodle poster. A white circle-head stickman in a blue shirt (#3B82C4) "
            "holds a large magnifying glass examining a steaming ceramic coffee cup on a warm paper-cream canvas (#F8F0DC). "
            "Inside the magnifying glass lens, green binary matrix code and computer circuits are clearly revealed. "
            "Wobbly raw black marker contours (#000000), 50% clean open negative space on top with massive bold yellow hand-lettered text 'SỰ THẬT LÀ GIẢ' with thick black outline. "
            "Zero room interiors, zero 3D perspective, zero drop shadows."
        ),
        "target_file": ROOT / "video/reality-interface-paradox-16x9/thumbnail_option2_coffee.jpg",
    },
    {
        "id": "thumbnail_option2_scissors_9x16",
        "job": "reality-interface-paradox-9x16",
        "ratio": "9:16",
        "allowed_text": ["SỰ THẬT LÀ GIẢ"],
        "description": (
            "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. A white circle-head stickman in a blue shirt (#3B82C4) "
            "uses oversized black scissors to cut through the paper canvas sky, tearing open a portal that reveals a glowing matrix of green binary code and computer bus lines beneath the fabric. "
            "Flat solid warm paper-cream canvas (#F8F0DC), wobbly raw black marker contours (#000000). "
            "Clean negative space at the top holding large bold yellow hand-lettered text 'SỰ THẬT LÀ GIẢ' with thick black outline. "
            "Zero room interiors, zero 3D perspective, zero drop shadows."
        ),
        "target_file": ROOT / "video/reality-interface-paradox-9x16/thumbnail_option2_scissors.jpg",
    },
]


async def generate_item(prof_cfg: dict, spec: dict) -> None:
    prof_name = prof_cfg["name"]
    logger.info(f"Generating {spec['id']} on {prof_name}...")
    compiled = compile_flow_prompt(
        "NanoBanana2Lite",
        "scene",
        {
            "description": spec["description"],
            "aspect_ratio": spec["ratio"],
            "allowed_text": spec["allowed_text"],
            "shot_type": "full_scene",
            "has_character": True,
            "character_free": False,
        },
        version="1.7.0",
    )
    prompt = compiled["prompt"]

    ensure_chrome_profiles_launched([prof_cfg], headless=True)
    # Poll for CDP port ready
    cdp_url = f"http://127.0.0.1:{prof_cfg['cdp_port']}/json/version"
    for attempt in range(15):
        try:
            with urllib.request.urlopen(cdp_url, timeout=1) as resp:
                if resp.status == 200:
                    break
        except Exception:
            await asyncio.sleep(1.0)

    sess = DirectCDPProfileSession(prof_cfg)
    try:
        await sess.connect()
        await sess._wait_for_flow_ready(timeout=30.0)
        res = await sess.generate_image(prompt=prompt, aspect=spec["ratio"], model="BELUGA")
        url = res.get("url", "")
        if not url:
            raise RuntimeError(f"No URL returned for {spec['id']}")

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()

        out_path = spec["target_file"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)

        # Upscale/format to standard resolution
        target_size = (1920, 1080) if spec["ratio"] == "16:9" else (1080, 1920)
        with Image.open(out_path) as im:
            im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
            im_resized.save(out_path, format="JPEG", quality=95)

        logger.info(f"Saved {out_path} ({target_size})")
    finally:
        if sess and sess.ws:
            try:
                await sess.ws.close()
            except Exception:
                pass


async def main():
    # 1. Format and copy primary Option 1 thumbnails
    v16_dir = ROOT / "video/reality-interface-paradox-16x9"
    v9_dir = ROOT / "video/reality-interface-paradox-9x16"
    v16_dir.mkdir(parents=True, exist_ok=True)
    v9_dir.mkdir(parents=True, exist_ok=True)

    src_16 = SYS_DIR / "runs/reality-interface-paradox-16x9/thumbnail_16x9.jpg"
    src_9 = SYS_DIR / "runs/reality-interface-paradox-9x16/thumbnail_9x16.jpg"

    if src_16.is_file():
        with Image.open(src_16) as im:
            im_1080 = im.resize((1920, 1080), Image.Resampling.LANCZOS)
            im_1080.save(v16_dir / "thumbnail.jpg", format="JPEG", quality=95)
            im_1080.save(v16_dir / "thumbnail_option1_scissors.jpg", format="JPEG", quality=95)
            logger.info("Saved 16:9 Option 1 primary thumbnail (1920x1080)")

    if src_9.is_file():
        with Image.open(src_9) as im:
            im_1080 = im.resize((1080, 1920), Image.Resampling.LANCZOS)
            im_1080.save(v9_dir / "thumbnail.jpg", format="JPEG", quality=95)
            im_1080.save(v9_dir / "thumbnail_option1_coffee.jpg", format="JPEG", quality=95)
            logger.info("Saved 9:16 Option 1 primary thumbnail (1080x1920)")

    # 2. Generate alternative Option 2 thumbnails via Flow CDP
    healthy_profs = [p for p in PROFILES if p["name"] in ["profile_1", "profile_4"]]
    with ProfileLifecycleManager(auto_teardown=True):
        tasks = [
            generate_item(healthy_profs[0], THUMBNAIL_SPECS[0]),
            generate_item(healthy_profs[1], THUMBNAIL_SPECS[1]),
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
