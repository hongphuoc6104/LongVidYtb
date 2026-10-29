#!/usr/bin/env python3
"""Generate 3 clean prototype images testing the Clean Minimalist & Functional Metaphor approach.

Guarantees:
1. Pure clean solid #F8F0DC background.
2. Zero frames, cards, tape, banners, borders.
3. Zero decorative noise: no stars, squiggles, confetti, sparkles, dots.
4. Single focal concept with 70%+ negative space.
"""
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
logger = logging.getLogger("generate_clean_prototypes")

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
OUT_DIR = SYS_DIR / "runs/willpower-paradox-16x9/prototypes"
ARTIFACT_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/c82f5636-79cd-49ed-9743-67cc15d1f3a9")

PROTOTYPE_SPECS = [
    {
        "id": "PROTOTYPE_01_EGO_DEPLETION",
        "title": "Mẫu 1: Cạn kiệt bản ngã (Thay thế thẻ chữ có băng dính và sao rác)",
        "shot_type": "full_scene",
        "has_character": True,
        "description": (
            "100% solid flat untextured #F8F0DC warm cream canvas filling the entire frame. "
            "In the center, stickman sits slumped forward on the ground with head resting low on knees, "
            "limp arms draped down, completely drained of energy. "
            "75% completely empty negative cream space surrounding the figure. "
            "Strictly zero cards, zero frames, zero borders, zero banners, zero text, "
            "zero floating stars, zero sparkles, zero squiggles, zero confetti, zero floor lines, zero drop shadows."
        ),
    },
    {
        "id": "PROTOTYPE_02_ENERGY_DRAIN",
        "title": "Mẫu 2: Nguồn năng lượng cạn kiệt (Thay thế nồi lẩu 7 icon lộn xộn)",
        "shot_type": "concept_metaphor",
        "has_character": False,
        "description": (
            "100% solid flat untextured #F8F0DC warm cream canvas edge to edge. "
            "A single clean minimalist vertical battery gauge outlined in bold wobbly black marker (#000000) "
            "standing alone in the center, showing an almost completely empty level with only a tiny red bar at the very bottom. "
            "80% completely empty negative cream space around the battery. "
            "Strictly zero extra icons, zero food items, zero gamepads, zero phones, zero arrows, "
            "zero floating stars, zero sparkles, zero squiggles, zero confetti, zero decorative frames, zero shadows."
        ),
    },
    {
        "id": "PROTOTYPE_03_THIRTY_SECOND_DELAY",
        "title": "Mẫu 3: Khoảng trễ 30 giây (Thay thế chiếc đồng hồ bưu thiếp ruy băng)",
        "shot_type": "concept_metaphor",
        "has_character": False,
        "description": (
            "100% solid flat untextured #F8F0DC warm cream canvas filling the entire widescreen frame. "
            "A single clean minimalist circular analog stopwatch outlined in bold hand-drawn black marker (#000000), "
            "minimal clean dial with tick marks, a single indicator hand pointing straight down at the 30-second mark. "
            "75% completely empty negative cream space across the canvas. "
            "Strictly zero postcard frames, zero double borders, zero banners, zero ribbons, zero corner tape, "
            "zero floating stars, zero sparkles, zero squiggles, zero confetti, zero floor lines, zero drop shadows."
        ),
    },
]


def prepare_items() -> list[dict]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for spec in PROTOTYPE_SPECS:
        req_id = spec["id"]
        target_jpg = OUT_DIR / f"{req_id}.jpg"
        target_json = OUT_DIR / f"{req_id}.json"

        compiled = compile_flow_prompt(
            "NanoBanana2Lite",
            "scene",
            {
                "description": spec["description"],
                "aspect_ratio": "16:9",
                "allowed_text": [],
                "shot_type": spec["shot_type"],
                "has_character": spec["has_character"],
                "character_free": not spec["has_character"],
            },
            version="1.7.0",
        )
        items.append({
            "id": req_id,
            "title": spec["title"],
            "prompt": compiled["prompt"],
            "target_jpg": target_jpg,
            "target_json": target_json,
            "description": spec["description"],
        })
    return items


async def generate_item(sess: DirectCDPProfileSession, prof_name: str, item: dict) -> None:
    logger.info(f"Generating {item['id']} on {prof_name}...")
    res = await sess.generate_image(prompt=item["prompt"], aspect="16:9", model="BELUGA")
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
        "jobId": item["id"],
        "type": "image",
        "prompt": item["prompt"],
        "ratio": "16:9",
        "source": "google-flow-browser",
        "status": "downloaded",
        "forgeId": media_id,
        "profile_id": prof_name,
    }
    item["target_json"].write_text(json.dumps(sidecar, indent=2, ensure_ascii=False), encoding="utf-8")

    # Also copy to artifacts dir for immediate user viewing
    artifact_jpg = ARTIFACT_DIR / f"{item['id']}.jpg"
    shutil.copy2(item["target_jpg"], artifact_jpg)
    logger.info(f"SUCCESS {item['id']} on {prof_name} ({len(data)} bytes). Copied to {artifact_jpg}")


async def main():
    items = prepare_items()
    logger.info(f"Prepared {len(items)} prototype items.")

    # Find first healthy profile
    prof_cfg = next(p for p in PROFILES if p["name"] == "profile_1")
    logger.info(f"Selected profile {prof_cfg['name']} for prototype generation.")

    sess = None
    try:
        ensure_chrome_profiles_launched([prof_cfg], headless=True)
        await asyncio.sleep(2.0)
        sess = DirectCDPProfileSession(prof_cfg)
        await sess.connect()
        await sess._wait_for_flow_ready(timeout=25.0)

        for item in items:
            await generate_item(sess, prof_cfg["name"], item)
            await asyncio.sleep(3.0)
        logger.info("All 3 prototype images successfully generated and verified!")
    finally:
        if sess and sess.ws:
            try:
                await sess.ws.close()
            except Exception:
                pass
        with ProfileLifecycleManager(auto_teardown=True) as mgr:
            mgr.teardown_all()


if __name__ == "__main__":
    asyncio.run(main())
