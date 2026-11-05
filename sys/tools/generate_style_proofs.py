#!/usr/bin/env python3
"""Generate 4 style proof images (9:16) for First-Principles Thinking scene.

Styles:
1. kurzgesagt
2. doodle_white
3. flat_pastel
4. ink_watercolor
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
logger = logging.getLogger("generate_style_proofs")

OUTPUT_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")
TARGET_SIZE = (1080, 1920)

STYLE_SPECS: Dict[str, Dict[str, str]] = {
    "kurzgesagt": {
        "name": "kurzgesagt",
        "description": "flat vector, vivid saturated colors, cute rounded shapes, deep dark gradient background with soft glow",
        "prompt": (
            "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 2D flat vector illustration "
            "extending continuously to all four edges with zero letterbox bars, zero UI chrome, zero text.\n\n"
            "Visual Style: Kurzgesagt in a nutshell aesthetic: flat vector art, vivid rich saturated cosmic colors (deep indigo, electric cyan, vibrant golden yellow, magenta), "
            "clean smooth rounded geometric shapes, deep dark indigo-violet radial gradient background (#0B0C1E to #1E1B4B) with a soft atmospheric radial glow behind the center subject. "
            "Flat shading, sharp edges, cute rounded minimalist geometry.\n\n"
            "Scene & Composition: Exactly ONE focal subject centered strictly in the vertical middle third of the frame: "
            "a cute small rounded minimalist vector car approaching a fork in a pathway. One road is a dull paved standard path; "
            "the other branch is a vibrant glowing cyan-yellow new path being drawn forward into open space.\n\n"
            "Negative Space: Over 75% clean empty negative space. Top third and bottom third are pure quiet dark gradient background with zero stars clutter, zero planets, zero scenery grids.\n\n"
            "Policy: Strictly zero text, zero letters, zero numbers, zero typography, zero words, zero labels, zero speech bubbles, zero watermarks anywhere."
        ),
    },
    "doodle_white": {
        "name": "doodle_white",
        "description": "pure white/cream background, simple black marker line drawing + ONE accent color (Sprouts / Minute Physics style)",
        "prompt": (
            "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 2D minimalist line-art illustration "
            "extending continuously to all four edges with zero letterbox bars, zero UI chrome, zero text.\n\n"
            "Visual Style: MinutePhysics and Sprouts educational doodle aesthetic: clean hand-drawn black marker line drawing on a solid pure flat white/cream paper canvas (#FAFAFA). "
            "Bold uniform felt-tip pen contours, clean unshaded minimalist sketch lines, strictly ONE single bright accent color (#F59E0B golden yellow) highlighting the new path. "
            "No gray shading, no 3D rendering, no gradients.\n\n"
            "Scene & Composition: Exactly ONE focal subject centered strictly in the vertical middle third of the canvas: "
            "a simple charming hand-drawn black marker outline of a tiny car reaching a fork in the road. One road is a standard faint black line, "
            "while the other branch is an energetic new path actively being drawn forward in the bright accent color.\n\n"
            "Negative Space: Over 75% pure stark clean white negative space. The upper third and lower third of the canvas are 100% completely blank empty white background. "
            "Zero clutter, zero borders, zero background scenery.\n\n"
            "Policy: Strictly zero text, zero letters, zero words, zero numbers, zero writing, zero watermarks anywhere in the image."
        ),
    },
    "flat_pastel": {
        "name": "flat_pastel",
        "description": "soft pastel palette, rounded soft geometric shapes, light background (TED-Ed / Headspace style)",
        "prompt": (
            "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 2D modern flat motion-graphic illustration "
            "extending continuously to all four edges with zero letterbox bars, zero UI chrome, zero text.\n\n"
            "Visual Style: TED-Ed and Headspace animation aesthetic: soft harmonious pastel color palette (light warm cream background #F7F5EE, dusty peach #F4A261, soft sage green #93B5A1, "
            "pastel lavender #B8B5E0, gentle terracotta), smooth rounded soft geometric shapes, clean flat matte paper cutout look, gentle ambient lighting with zero harsh drop shadows, zero gradients.\n\n"
            "Scene & Composition: Exactly ONE focal subject centered strictly in the vertical middle third of the frame: "
            "a stylized cute minimalist pastel small car pausing at a fork in a smooth pathway. One branch is a plain muted grey-beige path; "
            "the other branch is a fresh curving path made of colorful soft rounded pastel blocks being laid down forward.\n\n"
            "Negative Space: Over 75% clean quiet empty pastel background negative space. Generous open breathing room in top and bottom thirds. Zero clouds, zero trees, zero clutter.\n\n"
            "Policy: Strictly zero text, zero letters, zero words, zero numbers, zero watermarks anywhere in the frame."
        ),
    },
    "ink_watercolor": {
        "name": "ink_watercolor",
        "description": "clean ink outline with light transparent watercolor wash on cream paper (clean Oversimplified-like)",
        "prompt": (
            "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 2D editorial illustration "
            "extending continuously to all four edges with zero letterbox bars, zero UI chrome, zero text.\n\n"
            "Visual Style: Clean ink outline with light transparent watercolor wash on cream paper (clean OverSimplified storybook aesthetic): "
            "crisp elegant black dip-pen ink line contours with delicate translucent watercolor washes on warm textured antique cream paper (#FDFBF7). "
            "Light airy watercolor tints in cerulean blue and warm ochre, soft watercolor edge bleeds, matte paper grain, zero 3D, zero digital glow.\n\n"
            "Scene & Composition: Exactly ONE focal subject centered strictly in the vertical middle third of the canvas: "
            "an ink-outlined vintage minimalist small car approaching a fork in a winding country trail. One road is an ordinary sketchy dirt trail; "
            "the other road is a fresh vibrant path being painted forward with a translucent blue watercolor brush stroke.\n\n"
            "Negative Space: Over 75% clean open negative space on the textured cream paper. The top third and bottom third are completely empty quiet paper background. "
            "Zero background scenery, zero borders, zero clutter.\n\n"
            "Policy: Strictly zero text, zero letters, zero numbers, zero handwriting, zero signatures, zero watermarks."
        ),
    },
}


def teardown_flow_pool() -> None:
    """Ensure strict teardown of any spawned Chrome CDP processes."""
    logger.info("[*] Executing strict Flow CDP teardown...")
    try:
        mgr = MultiProfileManager()
        mgr.stop_all_profiles()
        logger.info("[✓] MultiProfileManager stopped all profiles successfully.")
    except Exception as exc:
        logger.warning(f"Teardown exception: {exc}")


def heal_watermark(image_path: Path) -> None:
    """Heal the bottom-right Gemini sparkle watermark if present using row-wise boundary interpolation."""
    with Image.open(image_path) as im:
        im.load()
        orig_w, orig_h = im.size
        rgb = im.convert("RGB")

    base_w = 768.0 if orig_h > orig_w else 1376.0
    base_h = 1376.0 if orig_h > orig_w else 768.0
    sx = orig_w / base_w
    sy = orig_h / base_h

    # Region where the bottom-right sparkle icon appears
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

    # Subtle 1.2% overscan crop to guarantee clean full-bleed edges
    crop_frac = 0.012
    dx = int(round(orig_w * crop_frac))
    dy = int(round(orig_h * crop_frac))
    cropped = rgb.crop((dx, dy, orig_w - dx, orig_h - dy))
    rgb = cropped.resize((orig_w, orig_h), Image.Resampling.LANCZOS)
    rgb.save(image_path, format="JPEG", quality=95, optimize=True)


def generate_proofs() -> Dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ledger = CreditLedger()
    assigned_profiles = sorted(
        PROFILES,
        key=lambda p: ledger.get_balance(str(p.get("name") or p.get("id") or "")),
        reverse=True,
    )
    # Filter only profiles with healthy quota (>= 50 credits)
    healthy_profiles = [
        p for p in assigned_profiles
        if ledger.get_balance(str(p.get("name") or p.get("id") or "")) >= 50
    ]
    logger.info(f"[*] Found {len(healthy_profiles)} healthy profiles. Top: {[p['name'] for p in healthy_profiles[:4]]}")

    results_summary: Dict[str, Any] = {}

    try:
        pool = PersistentWorkerPool(
            target_workers=2,
            profiles=healthy_profiles,
            cooldown_seconds=45.0,
            pacing_seconds=2.0,
            stagger_seconds=1.0,
            headless=True,
            default_out_dir=OUTPUT_DIR,
            min_credits_required=10,
        )

        with pool:
            for style_key, spec in STYLE_SPECS.items():
                dest_filename = f"style_proof_{style_key}.jpg"
                task_spec = {
                    "id": f"proof_{style_key}",
                    "prompt": spec["prompt"],
                    "ratio": "9:16",
                    "filename": dest_filename,
                    "out_dir": str(OUTPUT_DIR),
                    "editorial_overlay": {"enabled": False},
                    "shot_type": "full_scene",
                    "model": "BELUGA",
                    "max_retries": 3,
                }
                logger.info(f"[+] Submitting style proof task: {style_key}")
                pool.submit_task(task_spec)

            logger.info("[*] Waiting for pool tasks completion...")
            completed = pool.wait_completion(timeout=400.0)
            if not completed:
                raise RuntimeError(f"Flow pool generation timed out: {pool.get_status()}")

        logger.info("[✓] Flow pool finished generation. Processing results...")

        # Post-process generated images
        for style_key, spec in STYLE_SPECS.items():
            dest_jpg = OUTPUT_DIR / f"style_proof_{style_key}.jpg"
            if not dest_jpg.is_file():
                raise FileNotFoundError(f"Missing expected output: {dest_jpg}")

            # Verify and resize to standard 1080x1920
            with Image.open(dest_jpg) as im:
                if im.size != TARGET_SIZE:
                    im_resized = im.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                    im_resized.save(dest_jpg, format="JPEG", quality=95)

            # Heal watermark & apply subtle overscan trim
            heal_watermark(dest_jpg)

            # Measure negative space
            neg_space = score_negative_space(dest_jpg)
            logger.info(f"  [Style: {style_key}] File: {dest_jpg.name} | Negative Space: {neg_space*100:.1f}%")

            results_summary[style_key] = {
                "path": str(dest_jpg.resolve()),
                "prompt": spec["prompt"],
                "negative_space": round(neg_space, 4),
                "resolution": TARGET_SIZE,
            }

    finally:
        teardown_flow_pool()

    summary_file = OUTPUT_DIR / "style_proofs_summary.json"
    summary_file.write_text(json.dumps(results_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"[✓] Style proofs completed. Summary saved to {summary_file}")
    return results_summary


if __name__ == "__main__":
    res = generate_proofs()
    print("\n================ STYLE PROOF RESULTS ================")
    for style_key, data in res.items():
        print(f"Style: {style_key}")
        print(f"  Path: {data['path']}")
        print(f"  Negative Space: {data['negative_space']*100:.1f}%")
        print(f"  Prompt:\n{data['prompt']}\n")
