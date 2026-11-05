#!/usr/bin/env python3
"""Modular proof image generator for competitor style benchmarking per channel.

Usage:
    python sys/tools/channel_style_proof_worker.py \
        --channel en-root-and-canopy \
        --profiles 0,1,2,3 \
        --spec-file /path/to/spec.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

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
logger = logging.getLogger("channel_style_proof_worker")

TARGET_SIZE = (1080, 1920)
BASE_PROOF_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/style_proofs")


def heal_watermark(image_path: Path) -> None:
    """Heal bottom-right watermark and apply 1.2% overscan trim."""
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


def run_channel_proofs(channel_slug: str, profile_indices: List[int], spec_file: Path) -> Dict[str, Any]:
    with open(spec_file, "r", encoding="utf-8") as f:
        specs_data = json.load(f)

    styles = specs_data.get("styles", {})
    if len(styles) < 4:
        raise ValueError(f"Expected at least 4 styles in spec, got {len(styles)}")

    channel_dir = BASE_PROOF_DIR / channel_slug
    channel_dir.mkdir(parents=True, exist_ok=True)

    # Dynamic healthy profiles: exclude only those with 0 credits or known auth issues
    blocked_names = {"profile_1", "profile_13", "profile_17", "profile_21"}
    assigned_profiles = sorted(
        [PROFILES[i] for i in profile_indices if i < len(PROFILES)],
        key=lambda p: 1 if p.get("name") in blocked_names else 0
    )
    logger.info(f"[*] Running proofs for {channel_slug} using profiles: {[p['name'] for p in assigned_profiles]}")

    results_summary: Dict[str, Any] = {
        "channel": channel_slug,
        "niche": specs_data.get("niche", ""),
        "scene_description": specs_data.get("scene_description", ""),
        "competitors": specs_data.get("competitors", []),
        "styles": {},
    }

    try:
        pool = PersistentWorkerPool(
            target_workers=1,
            profiles=assigned_profiles,
            cooldown_seconds=45.0,
            pacing_seconds=6.0,
            stagger_seconds=1.0,
            headless=True,
            default_out_dir=channel_dir,
            min_credits_required=1,
        )

        with pool:
            submitted_any = False
            for style_key, spec in styles.items():
                dest_filename = f"proof_{style_key}.jpg"
                dest_path = channel_dir / dest_filename
                if dest_path.is_file() and dest_path.stat().st_size > 1000:
                    logger.info(f"[-] Style task {style_key} already exists at {dest_path}, skipping generation")
                    continue
                task_spec = {
                    "id": f"{channel_slug}_{style_key}",
                    "prompt": spec["prompt"],
                    "ratio": "9:16",
                    "filename": dest_filename,
                    "out_dir": str(channel_dir),
                    "editorial_overlay": {"enabled": False},
                    "shot_type": "full_scene",
                    "model": "BELUGA",
                    "max_retries": 3,
                }
                logger.info(f"[+] Submitting {channel_slug} style task: {style_key}")
                pool.submit_task(task_spec)
                submitted_any = True

            if submitted_any:
                logger.info(f"[*] Waiting for {channel_slug} pool tasks completion...")
                completed = pool.wait_completion(timeout=450.0)
                if not completed:
                    logger.warning(f"Flow pool timed out or partial completion: {pool.get_status()}")

        for style_key, spec in styles.items():
            dest_jpg = channel_dir / f"proof_{style_key}.jpg"
            if not dest_jpg.is_file():
                logger.error(f"Missing image: {dest_jpg}")
                continue

            needs_heal = False
            with Image.open(dest_jpg) as im:
                if im.size != TARGET_SIZE:
                    im_resized = im.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                    im_resized.save(dest_jpg, format="JPEG", quality=95)
                    needs_heal = True

            if needs_heal:
                heal_watermark(dest_jpg)
            neg_space = score_negative_space(dest_jpg)

            results_summary["styles"][style_key] = {
                "competitor": spec.get("competitor", ""),
                "style_name": spec.get("style_name", style_key),
                "path": str(dest_jpg.resolve()),
                "negative_space": round(neg_space, 4),
                "resolution": TARGET_SIZE,
                "prompt": spec["prompt"],
            }

    finally:
        pass

    summary_file = channel_dir / "proof_report.json"
    summary_file.write_text(json.dumps(results_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"[✓] Completed {channel_slug}. Report saved to {summary_file}")
    return results_summary


def main():
    parser = argparse.ArgumentParser(description="Generate competitor style proof images for a channel.")
    parser.add_argument("--channel", required=True, help="Channel slug, e.g. en-root-and-canopy")
    parser.add_argument("--profiles", required=True, help="Comma-separated profile indices, e.g. 0,1,2,3")
    parser.add_argument("--spec-file", required=True, type=Path, help="Path to JSON spec file")
    args = parser.parse_args()

    prof_indices = [int(x.strip()) for x in args.profiles.split(",") if x.strip()]
    res = run_channel_proofs(args.channel, prof_indices, args.spec_file)
    print(f"DONE: {args.channel} generated {len(res['styles'])} proofs")


if __name__ == "__main__":
    main()
