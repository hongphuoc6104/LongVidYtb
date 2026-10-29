#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import shutil
import sys
import urllib.request
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_prompts import compile as compile_flow_prompt
from flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession, ensure_chrome_profiles_launched
from flow_cdp.lifecycle import ProfileLifecycleManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_clean_text")

OUT_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/c82f5636-79cd-49ed-9743-67cc15d1f3a9")

ITEMS = [
    {
        "id": "PROTOTYPE_CLEAN_TEXT_01_EGO",
        "shot_type": "full_scene",
        "has_character": True,
        "allowed_text": ["CẠN KIỆT BẢN NGÃ"],
        "description": (
            "100% solid flat untextured #F8F0DC warm cream canvas edge to edge. "
            "In the lower center, stickman sits slumped forward exhausted with head on knees. "
            "Directly above the stickman, clean bold unadorned black hand-lettered text reading 'CẠN KIỆT BẢN NGÃ' "
            "floats freely on the bare cream field. "
            "Strictly zero card borders, zero boxes, zero banners, zero corner tape, "
            "zero floating stars, zero sparkles, zero squiggles, zero confetti, zero ribbons, zero floor lines. "
            "70% completely empty negative space."
        ),
    },
    {
        "id": "PROTOTYPE_CLEAN_TEXT_02_DELAY",
        "shot_type": "concept_metaphor",
        "has_character": False,
        "allowed_text": ["KHOẢNG TRỄ 30 GIÂY"],
        "description": (
            "100% solid flat untextured #F8F0DC warm cream canvas filling the widescreen frame. "
            "On the left, a clean minimalist analog stopwatch outlined in black marker (#000000) with needle at 30 seconds. "
            "On the right, clean bold unadorned black hand-lettered text reading 'KHOẢNG TRỄ 30 GIÂY' "
            "floats freely on the empty cream field. "
            "Strictly zero postcard frames, zero boxes, zero double borders, zero banners, zero ribbons, zero corner tape, "
            "zero floating stars, zero sparkles, zero squiggles, zero confetti, zero drop shadows. "
            "70% completely empty negative cream space."
        ),
    }
]

async def main():
    prof_cfg = next(p for p in PROFILES if p["name"] == "profile_1")
    ensure_chrome_profiles_launched([prof_cfg], headless=True)
    await asyncio.sleep(2.0)
    sess = DirectCDPProfileSession(prof_cfg)
    await sess.connect()
    await sess._wait_for_flow_ready(timeout=25.0)

    try:
        for item in ITEMS:
            compiled = compile_flow_prompt(
                "NanoBanana2Lite",
                "scene",
                {
                    "description": item["description"],
                    "aspect_ratio": "16:9",
                    "allowed_text": item["allowed_text"],
                    "shot_type": item["shot_type"],
                    "has_character": item["has_character"],
                    "character_free": not item["has_character"],
                },
                version="1.7.0",
            )
            logger.info(f"Generating {item['id']}...")
            res = await sess.generate_image(prompt=compiled["prompt"], aspect="16:9", model="BELUGA")
            url = res.get("url", "")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            target = OUT_DIR / f"{item['id']}.jpg"
            target.write_bytes(data)
            logger.info(f"SUCCESS {item['id']} saved to {target} ({len(data)} bytes)")
            await asyncio.sleep(3.0)
    finally:
        if sess and sess.ws:
            await sess.ws.close()
        # cleanup profile
        from flow_cdp.cdp_direct_client import kill_chrome_processes_on_ports
        kill_chrome_processes_on_ports([prof_cfg["cdp_port"]])

if __name__ == "__main__":
    asyncio.run(main())
