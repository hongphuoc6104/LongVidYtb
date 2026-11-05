#!/usr/bin/env python3
"""Generate pilot competitor-matched images for en-first-principles and en-scale-and-bone.

Directly inspired by real competitor thumbnails and frames.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict

from PIL import Image, ImageDraw, ImageFilter

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from flow_cdp.cdp_direct_client import PROFILES
from flow_cdp.credit_ledger import CreditLedger
from flow_cdp.multi_profile_manager import MultiProfileManager
from flow_cdp.persistent_pool import PersistentWorkerPool
from tools.visual_clutter_gate import score_negative_space

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_pilot_competitor_matching")

OUTPUT_BASE = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/pilot_competitor_matched")
TARGET_SIZE = (1080, 1920)

PILOT_SPECS: Dict[str, Dict[str, Dict[str, str]]] = {
    "en-first-principles": {
        "veritasium": {
            "competitor_name": "Veritasium (~16.5M subs)",
            "style_title": "Cinematic High-Contrast Sci-Fi Mystery",
            "prompt": (
                "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 cinematic sci-fi thought experiment in the signature visual style of Veritasium.\n\n"
                "Atmospheric cinematic lighting, deep dark environment with dramatic blue volumetric mist and deep backlight. "
                "A lone stylized sleek car paused at a fork in an asphalt road. One path is an ordinary dark highway; the other branch is a glowing neon electric-blue and white plasma trail illuminating the surrounding atmospheric dark fog.\n\n"
                "Cinematic depth of field, metallic car reflections, high contrast, cinematic documentary frame. Zero text, zero watermarks, zero UI letters."
            ),
        },
        "polymatter": {
            "competitor_name": "PolyMatter (~2.2M subs)",
            "style_title": "Sleek Editorial Documentary Collage & Laser Scan",
            "prompt": (
                "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 modern high-contrast documentary editorial collage in the signature visual style of PolyMatter.\n\n"
                "Clean dark slate-gray background. An overhead three-quarters perspective of a sharp realistic asphalt highway road splitting into two branches. "
                "A crisp horizontal red laser scanning beam sweeps across the right road branch with glowing circular inspection callout rings highlighting the new route.\n\n"
                "Sleek corporate editorial documentary graphic, rich textures, sharp dramatic lighting, zero text typography, zero watermarks."
            ),
        },
        "primer": {
            "competitor_name": "Primer (~1.2M subs)",
            "style_title": "Charming Stylized 3D Miniature Diorama Simulation",
            "prompt": (
                "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 charming soft 3D stylized simulation aesthetic in the signature visual style of Primer.\n\n"
                "A cute miniature diorama world on a soft dark gray background. A cute simple rounded blue blob character driving a tiny toy car approaching a miniature wooden road fork. "
                "Soft clay-like textures, warm diffused ambient lighting, gentle soft shadows, clean miniature environment with tiny rounded pebbles.\n\n"
                "Engaging, friendly, clean scientific simulation aesthetic. Zero text, zero letters, zero watermarks."
            ),
        },
        "3blue1brown": {
            "competitor_name": "3Blue1Brown (~6.5M subs)",
            "style_title": "Elegant Dark-Mode Mathematical Vector Space",
            "prompt": (
                "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 elegant mathematical vector space in the signature aesthetic of 3Blue1Brown.\n\n"
                "Deep dark obsidian canvas (#0D1117). A glowing mathematical vector coordinate grid curved in 3D spacetime showing a bifurcation fork. "
                "A sleek glowing particle car glides along a brilliant cyan and electric yellow parametric curve path.\n\n"
                "Clean glowing geometric lines, mathematical elegance, dark-mode educational visual, high aesthetic clarity. Zero text, zero watermarks."
            ),
        },
    },
    "en-scale-and-bone": {
        "tierzoo": {
            "competitor_name": "TierZoo (~3.4M subs)",
            "style_title": "Retro RPG Game HUD & 3D Creature Review",
            "prompt": (
                "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 video game RPG interface aesthetic in the signature style of TierZoo.\n\n"
                "A vibrant deep tropical jungle background with sunlight rays. A stylized 3D game-model baby Komodo dragon climbing a mossy tree trunk with sharp claws. "
                "Floating beside the reptile is a glowing retro video game HUD stat chart with colorful glowing stat bars in bright pixelated green and yellow.\n\n"
                "Clean game-review explainer graphic, vibrant lighting, rich 3D character, zero text typography, zero watermarks."
            ),
        },
        "pbs_eons": {
            "competitor_name": "PBS Eons (~2.8M subs)",
            "style_title": "Cinematic Paleo-Wildlife Sunset Documentary",
            "prompt": (
                "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 cinematic prehistoric wildlife documentary art in the signature style of PBS Eons.\n\n"
                "Warm golden-hour sunset lighting with a rich orange and dusty violet sky. A realistic detailed prehistoric baby monitor lizard with sharp claws climbing rough volcanic tree bark. "
                "Atmospheric smoke and dust motes in the air, rich prehistoric island jungle foliage in the background, cinematic natural history documentary frame.\n\n"
                "Rich cinematic depth, realistic creature anatomy, zero text, zero watermarks."
            ),
        },
        "bbc_earth": {
            "competitor_name": "BBC Earth (~14M subs)",
            "style_title": "Photorealistic Macro Wildlife Documentary",
            "prompt": (
                "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 high-end BBC Earth macro wildlife photography aesthetic.\n\n"
                "Ultra-sharp natural daylight filtering through a lush canopy. A tiny real baby Komodo dragon with detailed beaded scales and curious golden eyes clinging to coarse tree bark. "
                "Rich shallow depth of field, natural dew drops on bark, authentic photorealistic wildlife documentary excellence.\n\n"
                "Natural color grading, crisp wildlife focus, zero CGI artifacts, zero text, zero watermarks."
            ),
        },
        "moth_light_media": {
            "competitor_name": "Moth Light Media (~350K subs)",
            "style_title": "Natural History Museum Scientific Gouache",
            "prompt": (
                "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 natural history museum scientific illustration in the visual style of Moth Light Media.\n\n"
                "Warm textured cream vellum background. An authentic detailed naturalist gouache painting of a young Komodo dragon climbing a weathered tree trunk. "
                "Earthy natural pigment tones (umber, sage, terracotta, ochre), delicate brushwork, scientific anatomical accuracy, timeless museum exhibit feel.\n\n"
                "Rich organic texture, refined naturalist art, zero text, zero watermarks."
            ),
        },
    },
}


def heal_watermark(image_path: Path) -> None:
    with Image.open(image_path) as im:
        im.load()
        orig_w, orig_h = im.size
        rgb = im.convert("RGB")

    base_w = 768.0 if orig_h > orig_w else 1376.0
    base_h = 1376.0 if orig_h > orig_w else 768.0
    sx = orig_w / base_w
    sy = orig_h / base_h

    wm_x1 = max(8, orig_w - int(round(120 * sx)))
    wm_x2 = min(orig_w - 4, orig_w - int(round(20 * sx)))
    wm_y1 = max(8, orig_h - int(round(120 * sy)))
    wm_y2 = min(orig_h - 4, orig_h - int(round(20 * sy)))

    if wm_x2 > wm_x1 and wm_y2 > wm_y1:
        wm_w = wm_x2 - wm_x1
        wm_h = wm_y2 - wm_y1
        patch = Image.new("RGB", (wm_w, wm_h))
        for dy in range(wm_h):
            y = wm_y1 + dy
            l_rgb = rgb.getpixel((max(0, wm_x1 - 4), y))
            r_rgb = rgb.getpixel((min(orig_w - 1, wm_x2 + 2), y))
            for dx in range(wm_w):
                t = dx / max(1, wm_w - 1)
                c = (
                    int(round(l_rgb[0] * (1.0 - t) + r_rgb[0] * t)),
                    int(round(l_rgb[1] * (1.0 - t) + r_rgb[1] * t)),
                    int(round(l_rgb[2] * (1.0 - t) + r_rgb[2] * t)),
                )
                patch.putpixel((dx, dy), c)

        mask = Image.new("L", (wm_w, wm_h), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.rounded_rectangle([3, 3, wm_w - 4, wm_h - 4], radius=max(4, int(round(8 * sx))), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=max(2, int(round(3 * sx)))))
        rgb.paste(patch, (wm_x1, wm_y1), mask)

    crop_frac = 0.012
    dx = int(round(orig_w * crop_frac))
    dy = int(round(orig_h * crop_frac))
    cropped = rgb.crop((dx, dy, orig_w - dx, orig_h - dy))
    rgb = cropped.resize((orig_w, orig_h), Image.Resampling.LANCZOS)
    rgb.save(image_path, format="JPEG", quality=95, optimize=True)


def generate_all() -> Dict[str, Any]:
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    assigned_profiles = [PROFILES[21], PROFILES[22]]  # profile_en01 and profile_en02 (clean dedicated EN pool)
    logger.info(f"[*] Starting pilot generator using profiles: {[p['name'] for p in assigned_profiles]}")

    results: Dict[str, Any] = {}

    try:
        pool = PersistentWorkerPool(
            target_workers=2,
            profiles=assigned_profiles,
            cooldown_seconds=45.0,
            pacing_seconds=2.0,
            stagger_seconds=1.0,
            headless=True,
            default_out_dir=OUTPUT_BASE,
            min_credits_required=1,
        )

        with pool:
            for channel_slug, styles in PILOT_SPECS.items():
                chan_dir = OUTPUT_BASE / channel_slug
                chan_dir.mkdir(parents=True, exist_ok=True)
                results[channel_slug] = {}

                for style_key, spec in styles.items():
                    dest_file = f"{style_key}.jpg"
                    task = {
                        "id": f"{channel_slug}_{style_key}",
                        "prompt": spec["prompt"],
                        "ratio": "9:16",
                        "filename": dest_file,
                        "out_dir": str(chan_dir),
                        "editorial_overlay": {"enabled": False},
                        "shot_type": "full_scene",
                        "model": "BELUGA",
                        "max_retries": 3,
                    }
                    logger.info(f"[+] Submitting {channel_slug} -> {style_key}")
                    pool.submit_task(task)

            logger.info("[*] Waiting for pilot generation pool completion...")
            completed = pool.wait_completion(timeout=450.0)
            if not completed:
                logger.warning(f"Flow pool generation timed out or partial: {pool.get_status()}")

        for channel_slug, styles in PILOT_SPECS.items():
            chan_dir = OUTPUT_BASE / channel_slug
            for style_key, spec in styles.items():
                dest_jpg = chan_dir / f"{style_key}.jpg"
                if not dest_jpg.is_file():
                    logger.error(f"Missing image: {dest_jpg}")
                    continue

                with Image.open(dest_jpg) as im:
                    if im.size != TARGET_SIZE:
                        im = im.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                        im.save(dest_jpg, format="JPEG", quality=95)

                heal_watermark(dest_jpg)
                results[channel_slug][style_key] = {
                    "competitor": spec["competitor_name"],
                    "style_title": spec["style_title"],
                    "path": str(dest_jpg.resolve()),
                    "prompt": spec["prompt"],
                }

    finally:
        try:
            for p in assigned_profiles:
                p_name = p.get("name")
                if p_name:
                    MultiProfileManager().stop_profile(p_name)
        except Exception as exc:
            logger.warning(f"Teardown exc: {exc}")

    summary_file = OUTPUT_BASE / "pilot_results.json"
    summary_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"[✓] Pilot completed! Summary saved to {summary_file}")
    return results


if __name__ == "__main__":
    generate_all()
