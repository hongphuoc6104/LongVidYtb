#!/usr/bin/env python3
"""Generate authentic 2D Indie Doodle Thumbnail options for Research Topic Size jobs via Flow CDP."""
from __future__ import annotations

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
logger = logging.getLogger("generate_research_topic_thumbnails")

THUMBNAIL_SPECS = [
    # 16:9 Option 1: Classic Metaphor - Boulder vs Blue Brick (BỚT THAM LẠI)
    {
        "id": "thumbnail_option1_tang_da_vien_gach",
        "job": "research-topic-size-16x9",
        "ratio": "16:9",
        "title": "Tùy chọn 1: Tảng Đá Vĩ Mô vs Viên Gạch Nhỏ (Chuẩn học thuật đại chúng)",
        "allowed_text": ["BỚT THAM LẠI"],
        "description": (
            "16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream (#F8F0DC) stage with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "On the left: An iconic crude 2D white circle-head stickman in a cerulean-blue shirt (#3B82C4) staggering and sweating under an enormous oversized grey rock prop that is crushing him. "
            "On the right: Another calm smiling blue-shirt stickman holding a tiny neat cerulean-blue brick (#3B82C4) that fits perfectly into an empty slot in a sturdy brick wall, stamped with a bright green checkmark. "
            "Clean minimalist composition with over 60% open cream negative space, zero 3D gradients, zero floor lines, zero drop shadows. "
            "Top-center bold hand-drawn golden-yellow (#FFE600) uppercase Vietnamese lettering 'BỚT THAM LẠI' with thick pitch-black (#000000) marker outline."
        ),
        "target_file": ROOT / "video/research-topic-size-16x9/thumbnail_option1_tang_da_vien_gach.jpg",
    },
    # 16:9 Option 2: The Nationwide Trap vs Dormitory Reality (CÚ LỪA TOÀN QUỐC)
    {
        "id": "thumbnail_option2_cu_lua_toan_quoc",
        "job": "research-topic-size-16x9",
        "ratio": "16:9",
        "title": "Tùy chọn 2: Cú Lừa Toàn Quốc vs Ký Túc Xá (Đánh trúng nỗi đau sinh viên)",
        "allowed_text": ["CÚ LỪA TOÀN QUỐC"],
        "description": (
            "16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream (#F8F0DC) stage with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "Comparison between two research paths. "
            "On the left: A giant outline map of Vietnam covered with red question marks and an empty flat wallet outline showing zero coins, stickman collapsing with dizzy spiral eyes. "
            "On the right: A simple doodle dormitory door labeled 'KÝ TÚC XÁ', where a happy stickman holds a neat clipboard checklist with 100 verified survey checkmarks and a big grade 'A+'. "
            "Over 60% open cream negative space, zero 3D perspective, zero drop shadows. "
            "Top-center bold hand-drawn golden-yellow (#FFE600) uppercase Vietnamese lettering 'CÚ LỪA TOÀN QUỐC' with thick pitch-black (#000000) marker outline."
        ),
        "target_file": ROOT / "video/research-topic-size-16x9/thumbnail_option2_cu_lua_toan_quoc.jpg",
    },
    # 16:9 Option 3: Onion Peeling Technique (GỌT CỦ HÀNH)
    {
        "id": "thumbnail_option3_got_cu_hanh",
        "job": "research-topic-size-16x9",
        "ratio": "16:9",
        "title": "Tùy chọn 3: Kỹ Thuật Gọt Củ Hành (Bóc tách biến số)",
        "allowed_text": ["GỌT CỦ HÀNH"],
        "description": (
            "16:9 YouTube thumbnail poster in raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream (#F8F0DC) stage with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "In the center: A large iconic 2D hand-drawn doodle onion with three concentric peeled layers clearly visible. "
            "The outer layer is large and crossed out, the middle layer is focused, and the tiny glowing core in the center radiates clean energy. "
            "On the left: The iconic white circle-head stickman in blue shirt (#3B82C4) holds a small peeling knife with enlightened cheerful expression, pointing right at the glowing core. "
            "Clean staging with over 60% open cream negative space, zero 3D, zero room interiors. "
            "Top-center bold hand-drawn vibrant golden-yellow (#FFE600) uppercase Vietnamese lettering 'GỌT CỦ HÀNH' with thick pitch-black (#000000) marker outline."
        ),
        "target_file": ROOT / "video/research-topic-size-16x9/thumbnail_option3_got_cu_hanh.jpg",
    },
    # 9:16 Option 1: Vertical Boulder vs Brick (BỚT THAM LẠI)
    {
        "id": "cover_option1_bot_tham_lai_9x16",
        "job": "research-topic-size-9x16",
        "ratio": "9:16",
        "title": "Tùy chọn 1 (9:16): Tảng Đá vs Viên Gạch Nhỏ",
        "allowed_text": ["BỚT THAM LẠI"],
        "description": (
            "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. Raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream canvas (#F8F0DC) with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "In the upper center: Big bold hand-drawn golden-yellow (#FFE600) uppercase lettering 'BỚT THAM LẠI' with thick black marker outline. "
            "In the center: A white circle-head doodle stickman in blue shirt (#3B82C4) dropping a giant heavy grey rock onto the floor and happily picking up a small glowing blue brick (#3B82C4). "
            "Clean vertical composition with over 60% open cream negative space, zero 3D perspective, zero drop shadows, zero room background."
        ),
        "target_file": ROOT / "video/research-topic-size-9x16/cover_option1_bot_tham_lai.jpg",
    },
    # 9:16 Option 2: Vertical The Nationwide Trap (CÚ LỪA TOÀN QUỐC)
    {
        "id": "cover_option2_cu_lua_toan_quoc_9x16",
        "job": "research-topic-size-9x16",
        "ratio": "9:16",
        "title": "Tùy chọn 2 (9:16): Cú Lừa Toàn Quốc",
        "allowed_text": ["CÚ LỪA TOÀN QUỐC"],
        "description": (
            "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. Raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream canvas (#F8F0DC) with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "In the upper center: Big bold hand-drawn golden-yellow (#FFE600) uppercase lettering 'CÚ LỪA TOÀN QUỐC' with thick black marker outline. "
            "In the center: Stickman in blue shirt (#3B82C4) stands bewildered between a giant map outline with red question marks and a simple neat dormitory door icon labeled 'KÝ TÚC XÁ' with green checkmarks. "
            "Clean vertical staging with 60% open negative space, zero 3D, zero shadows."
        ),
        "target_file": ROOT / "video/research-topic-size-9x16/cover_option2_cu_lua_toan_quoc.jpg",
    },
]


async def generate_item(prof_cfg: dict, spec: dict) -> bool:
    out_path = spec["target_file"]
    sidecar_path = out_path.with_suffix(".json")
    if out_path.is_file() and out_path.stat().st_size > 5000 and sidecar_path.is_file():
        logger.info(f"Skipping {spec['id']} (already exists on disk)")
        return True

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

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)

        # Upscale / standardize size to 1920x1080 or 1080x1920
        target_size = (1920, 1080) if spec["ratio"] == "16:9" else (1080, 1920)
        with Image.open(out_path) as im:
            im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
            im_resized.save(out_path, format="JPEG", quality=95)

        # Write sidecar JSON
        sidecar = {
            "jobId": spec["id"],
            "type": "image",
            "prompt": prompt,
            "ratio": spec["ratio"],
            "source": "google-flow-browser",
            "status": "downloaded",
            "forgeId": res.get("media_id", ""),
            "profile_id": prof_name,
            "spec": {k: str(v) if isinstance(v, Path) else v for k, v in spec.items()},
        }
        sidecar_path.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
        logger.info(f"Saved {out_path} ({target_size}) and sidecar")
        return True
    except Exception as ex:
        logger.warning(f"Error on {prof_name} for {spec['id']}: {ex}")
        return False
    finally:
        if sess and sess.ws:
            try:
                await sess.ws.close()
            except Exception:
                pass


async def main():
    logger.info("--- Generating High-Impact Authentic 2D Indie Doodle Thumbnails via Flow CDP ---")
    prof = next(p for p in PROFILES if p["name"] == "profile_1")

    with ProfileLifecycleManager(auto_teardown=True):
        for spec in THUMBNAIL_SPECS:
            out_path = spec["target_file"]
            sidecar_path = out_path.with_suffix(".json")
            if out_path.is_file() and out_path.stat().st_size > 5000 and sidecar_path.is_file():
                logger.info(f"Skipping {spec['id']} (already exists)")
                continue

            ensure_chrome_profiles_launched([prof], headless=True)
            await asyncio.sleep(3.0)

            success = await generate_item(prof, spec)
            if not success:
                logger.warning(f"Retrying {spec['id']} once after restart...")
                ensure_chrome_profiles_launched([prof], headless=True)
                await asyncio.sleep(4.0)
                await generate_item(prof, spec)

            await asyncio.sleep(3.0)

    # Set default thumbnail.jpg / cover.jpg
    v16 = ROOT / "video/research-topic-size-16x9"
    v9 = ROOT / "video/research-topic-size-9x16"
    if (v16 / "thumbnail_option1_tang_da_vien_gach.jpg").is_file():
        import shutil
        shutil.copy2(v16 / "thumbnail_option1_tang_da_vien_gach.jpg", v16 / "thumbnail.jpg")
    if (v9 / "cover_option1_bot_tham_lai.jpg").is_file():
        import shutil
        shutil.copy2(v9 / "cover_option1_bot_tham_lai.jpg", v9 / "cover.jpg")
    elif (v9 / "cover_option2_cu_lua_toan_quoc.jpg").is_file():
        import shutil
        shutil.copy2(v9 / "cover_option2_cu_lua_toan_quoc.jpg", v9 / "cover.jpg")

    logger.info("[SUCCESS] All thumbnail options successfully processed!")


if __name__ == "__main__":
    asyncio.run(main())
