#!/usr/bin/env python3
"""Generate authentic 2D Indie Doodle Thumbnail options for Quy Trình Đề Tài Lớn (9:16) via Flow CDP."""
from __future__ import annotations

import asyncio
import json
import logging
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
logger = logging.getLogger("generate_quy_trinh_de_tai_lon_thumbnails")

THUMBNAIL_SPECS = [
    # Option 1: AI ĐỨNG RA LÀM?
    {
        "id": "cover_option1_ai_dung_ra_lam",
        "job": "quy-trinh-de-tai-lon-9x16",
        "ratio": "9:16",
        "title": "Tùy chọn 1: Người que sinh viên vs Cỗ máy nghiên cứu (AI ĐỨNG RA LÀM?)",
        "allowed_text": ["AI ĐỨNG RA LÀM?"],
        "description": (
            "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. Raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream canvas (#F8F0DC) with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "In the upper center: Big bold hand-drawn vibrant golden-yellow (#FFE600) uppercase lettering 'AI ĐỨNG RA LÀM?' with thick pitch-black (#000000) marker outline. "
            "In the center: Iconic bald white circle-head doodle stickman in solid cerulean-blue T-shirt (#3B82C4) shrugging in perplexity with sweat drops, looking at a giant conveyor belt pipeline labeled with '43.000 NGƯỜI' and a tall doctor stickman holding a legal clipboard. "
            "Over 65% open cream negative space, zero 3D perspective, zero drop shadows, zero room interiors, clean flat 2D paper cutout staging."
        ),
        "target_file": ROOT / "video/quy-trinh-de-tai-lon-9x16/cover_option1_ai_dung_ra_lam.jpg",
    },
    # Option 2: 10 TỶ ĐÔ
    {
        "id": "cover_option2_10_ty_do",
        "job": "quy-trinh-de-tai-lon-9x16",
        "ratio": "9:16",
        "title": "Tùy chọn 2: Nghịch lý 10 Tỷ Đô vs Ống nghiệm nhỏ (10 TỶ ĐÔ)",
        "allowed_text": ["10 TỶ ĐÔ"],
        "description": (
            "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. Raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream canvas (#F8F0DC) with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "In the upper center: Big bold hand-drawn golden-yellow (#FFE600) uppercase lettering '10 TỶ ĐÔ' with thick black marker outline. "
            "In the center: A minimalist white circle-head stickman in a solid cerulean-blue T-shirt (#3B82C4) with a bewildered sweating expression, holding a tiny glass test tube with one blue droplet in his left hand. "
            "On the right: An enormous towering industrial metal vault stamped with a giant '$10B' and a thick legal contract folder stamped with a red seal. "
            "Over 60% open cream negative space, zero 3D perspective, zero drop shadows, zero room background, clean flat paper aesthetic."
        ),
        "target_file": ROOT / "video/quy-trinh-de-tai-lon-9x16/cover_option2_10_ty_do.jpg",
    },
    # Option 3: TẠI SAO KHÔNG THỂ?
    {
        "id": "cover_option3_tai_sao_khong_the",
        "job": "quy-trinh-de-tai-lon-9x16",
        "ratio": "9:16",
        "title": "Tùy chọn 3: Sinh viên xuất sắc vs Rào cản đề tài (TẠI SAO KHÔNG THỂ?)",
        "allowed_text": ["TẠI SAO KHÔNG THỂ?"],
        "description": (
            "Orthographic 2D hand-drawn doodle poster in 9:16 vertical ratio. Raw freehand 2D Vietnamese indie doodle style on a clean solid warm paper-cream canvas (#F8F0DC) with bold pitch-black (#000000) marker contours and 100% flat MS-Paint hex fills. "
            "In the upper center: Big bold hand-drawn golden-yellow (#FFE600) uppercase lettering 'TẠI SAO KHÔNG THỂ?' with thick black marker outline. "
            "In the center: A young student stickman wearing a graduation cap holding a diploma, staring in astonishment at 3 simple barrier signs labeled 'TIỀN', 'LUẬT', '30 NĂM'. "
            "Over 60% open cream negative space, zero 3D gradients, zero floor lines, zero drop shadows, zero room background."
        ),
        "target_file": ROOT / "video/quy-trinh-de-tai-lon-9x16/cover_option3_tai_sao_khong_the.jpg",
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

        # Standardize size to 1080x1920
        target_size = (1080, 1920)
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
    logger.info("--- Generating Flow-Native 2D Indie Doodle Thumbnails for Quy Trình Đề Tài Lớn ---")
    prof = next(p for p in PROFILES if p["name"] == "profile_1")

    with ProfileLifecycleManager(auto_teardown=True):
        for spec in THUMBNAIL_SPECS:
            out_path = spec["target_file"]
            sidecar_path = out_path.with_suffix(".json")
            if out_path.is_file() and out_path.stat().st_size > 5000 and sidecar_path.is_file():
                logger.info(f"Skipping {spec['id']} (already exists)")
                continue

            ensure_chrome_profiles_launched([prof], headless=True)
            await asyncio.sleep(2.0)

            success = await generate_item(prof, spec)
            if not success:
                logger.warning(f"Retrying {spec['id']} once...")
                ensure_chrome_profiles_launched([prof], headless=True)
                await asyncio.sleep(3.0)
                await generate_item(prof, spec)

            await asyncio.sleep(2.0)

    # Automatically set the best default cover/thumbnail (clean without text card overlays)
    v9 = ROOT / "video/quy-trinh-de-tai-lon-9x16"
    runs_dir = ROOT / "sys/runs/quy-trinh-de-tai-lon-9x16"
    selected_option = v9 / "cover_option1_ai_dung_ra_lam.jpg"
    if not selected_option.is_file():
        selected_option = v9 / "cover_option2_10_ty_do.jpg"
    if not selected_option.is_file():
        selected_option = v9 / "cover_option3_tai_sao_khong_the.jpg"

    if selected_option.is_file():
        shutil.copy2(selected_option, v9 / "cover.jpg")
        shutil.copy2(selected_option, v9 / "thumbnail_9x16.jpg")
        shutil.copy2(selected_option, v9 / "quy-trinh-de-tai-lon-9x16.jpg")
        # Also create PNG version for TikTok/Reels without overlay
        with Image.open(selected_option) as im:
            im.save(v9 / "cover_tiktok_reels_9x16.png", format="PNG")
        # Sync to sys/runs
        shutil.copy2(selected_option, runs_dir / "thumbnail_9x16.jpg")
        logger.info(f"[SUCCESS] Updated official deliverables with clean Flow thumbnail from {selected_option.name}")


if __name__ == "__main__":
    asyncio.run(main())
