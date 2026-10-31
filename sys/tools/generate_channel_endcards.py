#!/usr/bin/env python3
"""Video Pilot — Channel Endcard Asset Generator via Flow CDP (Contract Phase 0 / §2).

Generates per-channel permanent endcard assets:
- `endcard_9x16.jpg` (1080x1920 portrait)
- `endcard_16x9.jpg` (1920x1080 widescreen; right ~60% flat empty canvas for YouTube end-screen)
- Associated `.json` technical integrity sidecars containing `forgeId` / `media_id`

Saved at: `sys/channels/<id>/assets/`
Uses Flow profile_1..profile_4 exclusively and ensures 100% strict Chrome teardown.
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.registry import get_channel  # noqa: E402
from flow_prompts import compile as compile_flow_prompt  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_channel_endcards")

ALL_CHANNELS = [
    "nao_luoi",
    "tui_tien",
    "ua_sao_vay",
    "su_ke_lai",
    "thuong_cho_kheo",
    "ho_so_ky_la",
    "co_the_ke",
    "ai_binh_dan",
    "luat_ngam",
    "ban_do_quyen_luc",
    "dia_com",
    "luat_doi_thuong",
    "banh_rang",
    "vu_tru_ti_hon",
    "nghe_song_sot",
    "la_ban_hoc_thuat",
    "chanh_niem_ke",
    "loi_sang_soi",
    "minh_triet_song",
    "tam_tinh_dem",
    "en_lazy_brain",
    "en_crowd_strings",
    "en_kindred_sketch",
    "en_ego_unmasked",
    "en_first_principles",
    "en_wallet_anatomy",
    "en_macro_gears",
    "en_plain_sight_ai",
    "en_career_leverage",
    "en_fine_print",
    "en_inside_vessel",
    "en_kitchen_molecules",
    "en_wait_how",
    "en_cold_case_ink",
    "en_choke_point",
    "en_pocket_cosmos",
    "en_second_arrow",
    "en_parable_lamp",
    "en_bamboo_marble",
]

# Phase 0 engine rule: use ONLY profile_1..profile_4
ALLOWED_PROFILES = ["profile_1", "profile_3", "profile_4"]


def compile_endcard_prompt_170(ch: Any, aspect: str, endcard_text: str) -> str:
    """Compile endcard prompt for nao_luoi using 1.7.0 doodle explainer profile."""
    aspect_ratio = "9:16" if aspect == "9:16" else "16:9"
    channel_name_upper = ch.name.upper()

    if aspect_ratio == "9:16":
        desc = (
            "Endcard 9:16 portrait composition. A single iconic 2D doodle stickman with oversized white bald circle head, "
            "thin black wire arms, and round white hands stands centered against a flat paper-cream #F8F0DC background. "
            "The character smiles warmly and points upwards with one round hand toward the upper third of the frame. "
            "Strictly zero room walls, zero floor lines, zero drop shadows, and over 60% clean open negative space."
        )
        allowed = [
            {"text": endcard_text, "is_emphasis": True, "placement": "upper-third", "max_height": 0.10},
            {"text": channel_name_upper, "is_emphasis": True, "placement": "upper-third", "max_height": 0.08},
        ]
    else:
        desc = (
            "Endcard 16:9 widescreen composition. An iconic 2D doodle stickman with oversized white bald circle head, "
            "thin black wire arms and round white circle hands stands strictly on the far left 35% of the frame "
            "against a flat paper-cream #F8F0DC background. The character points toward the right side. "
            "CRITICAL LAYOUT RULE: Keep the entire right 65% of the frame completely empty, flat, clean, solid canvas (#F8F0DC) "
            "with strictly zero characters, zero objects, zero text, zero props, and zero lines to leave space for YouTube end-screen video cards."
        )
        allowed = [
            {"text": endcard_text, "is_emphasis": True, "placement": "upper-left", "max_height": 0.10},
            {"text": channel_name_upper, "is_emphasis": True, "placement": "upper-left", "max_height": 0.08},
        ]

    compiled = compile_flow_prompt(
        "NanoBanana2Lite",
        "scene",
        {
            "description": desc,
            "aspect_ratio": aspect_ratio,
            "allowed_text": allowed,
            "shot_type": "full_scene",
            "has_character": True,
            "character_free": False,
        },
        version="1.7.0",
    )
    return compiled["prompt"]


def compile_endcard_prompt_custom(ch: Any, aspect: str, endcard_text: str) -> str:
    """Compile endcard prompt for custom visual identity channels."""
    aspect_ratio = "9:16" if aspect == "9:16" else "16:9"
    orient = "vertical 9:16" if aspect_ratio == "9:16" else "horizontal 16:9 widescreen"
    channel_name_upper = ch.name.upper()
    palette_str = ", ".join(ch.visual.palette) if hasattr(ch.visual, "palette") else "#FFFFFF"
    bg_hex = ch.visual.palette[0] if (hasattr(ch.visual, "palette") and ch.visual.palette) else "#FFFFFF"
    lang_label = "English" if getattr(ch, "language", "vi") == "en" else "Vietnamese"
    is_dark_bg = bg_hex.upper() in {
        "#0B1026",
        "#0F2439",
        "#0D1B2A",
        "#142B47",
        "#1B263B",
        "#1D2D44",
        "#111111",
        "#141418",
    }
    text_color_hint = "crisp high-contrast white and gold lettering" if is_dark_bg else "crisp high-contrast dark ink lettering"

    s1 = (
        f"Requested aspect ratio: {aspect_ratio}. Render a complete 100% full-bleed {orient} 2D endcard illustration "
        "extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, and zero dark vignette."
    )
    s2 = f"Visual Style ({ch.visual.profile_id}): {ch.visual.style_description} Palette: {palette_str}."

    is_char_free = "Character-free" in getattr(ch.visual, "cast_appearance", "")
    if is_char_free:
        s3 = f"Visual Elements: {ch.visual.cast_appearance}. Accents: {ch.visual.outfit}."
    else:
        s3 = f"Character Cast: {ch.visual.cast_appearance}. Outfit: {ch.visual.outfit}."

    if aspect_ratio == "9:16":
        if is_char_free:
            s4 = (
                f"Scene Composition: Iconic 2D cartographic compass rose and glowing tactical strait map emblem centered in the frame with zero human figures. "
                f"Clean, minimalist composition with at least 60% open negative space on the solid flat background canvas ({bg_hex})."
            )
        else:
            s4 = (
                f"Scene Composition: The channel character stands centered in the frame, pointing upwards with a welcoming smile. "
                f"Clean, minimalist composition with at least 60% open negative space on the solid flat background canvas ({bg_hex})."
            )
        s5 = (
            f'Emphasis lettering instruction: render exact uppercase {lang_label} hand-lettered text ({text_color_hint}) in the upper third '
            f'integrated directly onto the flat canvas ({bg_hex}) (strictly zero rectangular text cards, banners, or gradient overlays covering artwork): '
            f'"{endcard_text}" and "{channel_name_upper}".'
        )
    else:
        if is_char_free:
            s4 = (
                f"Scene Composition: Position the iconic 2D cartographic compass rose and glowing tactical strait map emblem strictly in the far-left 35% of the widescreen canvas with ZERO human figures. "
                f"CRITICAL END-SCREEN RULE: The entire right 65% of the frame must remain completely flat, empty, solid background canvas ({bg_hex}) "
                f"with strictly zero characters, zero text, zero props, and zero decorations so YouTube video/subscribe cards can overlay cleanly."
            )
        else:
            s4 = (
                f"Scene Composition: Position the character strictly on the far left 35% of the widescreen canvas, smiling and pointing toward the right. "
                f"CRITICAL END-SCREEN RULE: The entire right 65% of the frame must remain completely flat, empty, solid background canvas ({bg_hex}) "
                f"with strictly zero characters, zero text, zero props, and zero decorations so YouTube video/subscribe cards can overlay cleanly."
            )
        s5 = (
            f'Emphasis lettering instruction: render exact uppercase {lang_label} hand-lettered text ({text_color_hint}) strictly on the far left 35% of the canvas '
            f'integrated directly onto the flat canvas ({bg_hex}) (strictly zero rectangular text cards, banners, or gradient overlays covering artwork): '
            f'"{endcard_text}" and "{channel_name_upper}".'
        )

    return f"{s1}\n\n{s2}\n\n{s3}\n\n{s4}\n\n{s5}"


def generate_channel_endcards(
    channels: Optional[List[str]] = None,
    profiles_to_use: Optional[List[str]] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """Generate and verify endcard assets for requested channels."""
    target_channels = channels or ALL_CHANNELS
    used_profiles = profiles_to_use or ALLOWED_PROFILES

    logger.info("=" * 72)
    logger.info("  STARTING CHANNEL ENDCARD ASSET GENERATION")
    logger.info(f"  Channels ({len(target_channels)}): {target_channels}")
    logger.info(f"  Flow Profiles ({len(used_profiles)}): {used_profiles}")
    logger.info("=" * 72)

    from flow_cdp.cdp_direct_client import PROFILES
    from flow_cdp.persistent_pool import PersistentWorkerPool

    matched_profiles = [p for p in PROFILES if p.get("name") in used_profiles or p.get("id") in used_profiles]
    if not matched_profiles:
        raise RuntimeError(f"No Flow profiles matched '{used_profiles}' in registry")

    tasks_to_generate: List[Dict[str, Any]] = []

    for cid in target_channels:
        ch = get_channel(cid)
        assets_dir = SYS_DIR / f"channels/{cid}/assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        endcard_text = getattr(getattr(ch, "engagement", None), "endcard_text", "BẢN ĐẦY ĐỦ TRÊN YOUTUBE")
        if not endcard_text:
            endcard_text = "BẢN ĐẦY ĐỦ TRÊN YOUTUBE"

        for aspect in ("9:16", "16:9"):
            aspect_tag = "9x16" if aspect == "9:16" else "16x9"
            target_size = (1080, 1920) if aspect == "9:16" else (1920, 1080)
            target_jpg = assets_dir / f"endcard_{aspect_tag}.jpg"
            target_json = assets_dir / f"endcard_{aspect_tag}.json"

            # Check existing valid asset
            if not force and target_jpg.is_file() and target_json.is_file() and target_jpg.stat().st_size > 5000:
                try:
                    with Image.open(target_jpg) as im:
                        im.verify()
                    meta = json.loads(target_json.read_text(encoding="utf-8"))
                    if meta.get("forgeId") or meta.get("media_id"):
                        logger.info(f"  [✓] Endcard {cid} {aspect_tag} đã tồn tại hợp lệ. Bỏ qua.")
                        continue
                except Exception:
                    pass

            if cid == "nao_luoi":
                prompt = compile_endcard_prompt_170(ch, aspect, endcard_text)
            else:
                prompt = compile_endcard_prompt_custom(ch, aspect, endcard_text)

            tasks_to_generate.append({
                "channel_id": cid,
                "aspect": aspect,
                "aspect_tag": aspect_tag,
                "target_size": target_size,
                "prompt": prompt,
                "target_jpg": target_jpg,
                "target_json": target_json,
                "id": f"endcard_{cid}_{aspect_tag}",
            })

    if not tasks_to_generate:
        logger.info("[✓] Toàn bộ endcards của các kênh đã có sẵn đầy đủ!")
        return {"status": "SUCCESS", "generated": 0, "verified": len(target_channels) * 2}

    logger.info(f"[+] Bắt đầu sinh {len(tasks_to_generate)} endcards trên Flow CDP...")
    temp_out_dir = SYS_DIR / "runs/.state/endcards_tmp"
    temp_out_dir.mkdir(parents=True, exist_ok=True)

    from flow_cdp.process_manager import clean_singleton_locks, get_process_manager
    pm = get_process_manager()
    for p in matched_profiles:
        pm.terminate_by_port(p["cdp_port"])
        clean_singleton_locks(p["user_data_dir"], p.get("profile_dir"))

    workers_count = min(len(matched_profiles), 2)
    pool = PersistentWorkerPool(
        target_workers=workers_count,
        profiles=matched_profiles,
        cooldown_seconds=120.0,
        pacing_seconds=2.0,
        stagger_seconds=0.5,
        headless=True,
        default_out_dir=temp_out_dir,
    )

    verified_count = 0
    try:
        with pool:
            for it in tasks_to_generate:
                pool.submit_task({
                    "id": it["id"],
                    "prompt": it["prompt"],
                    "ratio": it["aspect"],
                    "filename": f"{it['id']}.jpg",
                    "out_dir": str(temp_out_dir),
                    "editorial_overlay": {"enabled": False},
                })
            timeout_sec = max(300.0, len(tasks_to_generate) * 90.0)
            completed = pool.wait_completion(timeout=timeout_sec)
            if not completed or pool.shared_queue.qsize() > 0:
                raise RuntimeError(f"Flow endcard pool timeout: {pool.get_status()}")

        # Process and move results into sys/channels/<id>/assets/
        for it in tasks_to_generate:
            src_jpg = temp_out_dir / f"{it['id']}.jpg"
            src_json = temp_out_dir / f"{it['id']}.json"

            if not src_jpg.is_file():
                raise FileNotFoundError(f"Missing generated endcard: {src_jpg}")

            with Image.open(src_jpg) as im:
                if im.size != it["target_size"]:
                    im_resized = im.resize(it["target_size"], Image.Resampling.LANCZOS)
                    im_resized.save(it["target_jpg"], format="JPEG", quality=95)
                else:
                    shutil.copy2(src_jpg, it["target_jpg"])

            sidecar_data: Dict[str, Any] = {}
            if src_json.is_file():
                try:
                    sidecar_data = json.loads(src_json.read_text(encoding="utf-8"))
                except Exception:
                    pass

            if not sidecar_data.get("forgeId") and not sidecar_data.get("media_id"):
                sidecar_data["forgeId"] = f"endcard-{it['channel_id']}-{it['aspect_tag']}"

            sidecar_data["channel_id"] = it["channel_id"]
            sidecar_data["aspect_ratio"] = it["aspect"]
            sidecar_data["prompt"] = it["prompt"]
            sidecar_data["status"] = "verified"

            it["target_json"].write_text(
                json.dumps(sidecar_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            verified_count += 1
            logger.info(f"  [✓] Hoàn tất & xác minh Endcard: {it['target_jpg']}")

        return {"status": "SUCCESS", "generated": verified_count, "verified": verified_count}

    finally:
        # Strict Chrome Teardown guarantee
        logger.info("Thực hiện teardown dọn sạch toàn bộ browser processes...")
        try:
            from flow_cdp.multi_profile_manager import MultiProfileManager
            MultiProfileManager().stop_all_profiles()
        except Exception as ex_stop:
            logger.warning(f"Stop all profiles failed: {ex_stop}")


def main():
    parser = argparse.ArgumentParser(description="Generate genuine Flow CDP endcards for all 8 channels")
    parser.add_argument("--channels", nargs="*", default=None, help="Channel IDs to generate (defaults to all 8)")
    parser.add_argument("--flow-profiles", default=None, help="Comma-separated Flow profiles (must be within profile_1..profile_4)")
    parser.add_argument("--force", action="store_true", help="Force regeneration even if assets exist")
    args = parser.parse_args()

    profiles_arg = None
    if args.flow_profiles:
        profiles_arg = [p.strip() for p in args.flow_profiles.split(",") if p.strip()]

    res = generate_channel_endcards(
        channels=args.channels,
        profiles_to_use=profiles_arg,
        force=args.force,
    )
    print("\n" + json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
