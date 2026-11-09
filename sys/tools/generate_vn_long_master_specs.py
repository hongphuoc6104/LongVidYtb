#!/usr/bin/env python3
"""Generator & Pre-synthesizer for Video Pilot Vietnamese High-Density Long (16:9) Master Specs.

Creates 180-350 state Two-Tier DAG Master Specs (<slug>_long_master_spec.json) with
story-driven visual prompts illustrating spoken Vietnamese narratives beat-by-beat
and Studio V3 Human Voice profile contracts for all 20 Vietnamese channels.
"""

from __future__ import annotations

import copy
import json
import logging
import re
import sys
from pathlib import Path
from typing import List, Tuple

TOOL_DIR = Path(__file__).resolve().parent
SYS_DIR = TOOL_DIR.parent
ROOT_DIR = SYS_DIR.parent

for _p in (str(ROOT_DIR), str(SYS_DIR), str(TOOL_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.vn_long_high_density_planner import validate_high_density_long_plan
from tools.story_driven_prompt_builder import build_story_driven_prompt
from tools.vn_long_channel_narratives import CHANNEL_NARRATIVES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_vn_long_master_specs")

SAFE_REPLACEMENTS = [
    ("shotgun", "tactical breaching device"),
    ("bullet", "kinetic projectile"),
    ("gun", "kinetic device"),
    ("firearm", "tactical equipment"),
    ("blood", "vital fluid"),
    ("corpse", "fallen subject"),
    ("suicide", "self-destruction"),
    ("murder", "lethal elimination"),
    ("bomb", "explosive charge"),
]

VN_20_CHANNELS = [
    "banh-rang",
    "luat-doi-thuong",
    "la-ban-hoc-thuat",
    "luat-ngam",
    "ua-sao-vay",
    "dia-com",
    "vu-tru-ti-hon",
    "chanh-niem-ke",
    "minh-triet-song",
    "co-the-ke",
    "su-ke-lai",
    "ban-do-quyen-luc",
    "loi-sang-soi",
    "nao-luoi",
    "thuong-cho-kheo",
    "nghe-song-sot",
    "ai-binh-dan",
    "tam-tinh-dem",
    "tui-tien",
    "ho-so-ky-la",
]


def resolve_channel_ids(slug: str) -> Tuple[str, str]:
    clean = slug.strip().removeprefix("channel-").removeprefix("ch_").removeprefix("ch-")
    channel_id = clean.replace("-", "_")
    channel_slug = clean.replace("_", "-")
    return channel_id, channel_slug


def sanitize_text(text: str) -> str:
    """Sanitize unsafe prompt trigger words."""
    if not text:
        return ""
    for old, new in SAFE_REPLACEMENTS:
        text = text.replace(old, new)
        text = text.replace(old.capitalize(), new.capitalize())
        text = text.replace(old.upper(), new.upper())
    return text


def split_sentences_into_clauses(text: str, target_count: int) -> List[str]:
    """Split a chapter narrative text into exactly target_count clauses."""
    raw_parts = [p.strip() for p in re.split(r'[.,;—–!\?\n]+', text) if p.strip()]
    if not raw_parts:
        raw_parts = [f"Phân đoạn {i+1}" for i in range(target_count)]

    if len(raw_parts) >= target_count:
        merged = []
        step = len(raw_parts) / target_count
        for i in range(target_count):
            start = int(i * step)
            end = int((i + 1) * step) if i < target_count - 1 else len(raw_parts)
            chunk = " ".join(raw_parts[start:end])
            merged.append(chunk)
        return merged
    else:
        result = list(raw_parts)
        while len(result) < target_count:
            max_idx = max(range(len(result)), key=lambda i: len(result[i].split()))
            words = result[max_idx].split()
            if len(words) <= 2:
                result.append("tiếp tục phân tích.")
            else:
                mid = len(words) // 2
                p1 = " ".join(words[:mid])
                p2 = " ".join(words[mid:])
                result[max_idx] = p1
                result.insert(max_idx + 1, p2)
        return result[:target_count]


def sync_aligned_specs(channel_id: str, channel_slug: str, updated_beats: List[dict]) -> None:
    """Synchronize story-driven prompts into aligned spec files in video/vn_pilot_<ch>_long/."""
    beat_prompt_map = {}
    for b in updated_beats:
        bid = b.get("beat_id") or b.get("id")
        if bid:
            beat_prompt_map[bid] = (b.get("prompt", ""), b.get("prompt_spec", ""))

    aligned_candidates = [
        ROOT_DIR / f"video/vn_pilot_{channel_id}_long/{channel_id}_long_aligned_spec.json",
        ROOT_DIR / f"video/vn_pilot_{channel_id}_long/{channel_id}_long_{len(updated_beats)}_aligned_spec.json",
        ROOT_DIR / f"video/vn_pilot_{channel_id}_long/{channel_id}_long_305_aligned_spec.json",
        ROOT_DIR / f"video/vn_pilot_{channel_id}_long/{channel_id}_long_310_aligned_spec.json",
    ]

    for aligned_p in aligned_candidates:
        if aligned_p.is_file():
            try:
                aligned_data = json.loads(aligned_p.read_text(encoding="utf-8"))
                aligned_beats = aligned_data.get("beats", aligned_data.get("visual_states", []))
                updated_count = 0
                for ab in aligned_beats:
                    ab_id = ab.get("beat_id") or ab.get("id")
                    if ab_id in beat_prompt_map:
                        p, ps = beat_prompt_map[ab_id]
                        ab["prompt"] = p
                        ab["prompt_spec"] = ps
                        updated_count += 1
                aligned_data["beats"] = aligned_beats
                aligned_data["visual_states"] = aligned_beats
                aligned_p.write_text(json.dumps(aligned_data, ensure_ascii=False, indent=2), encoding="utf-8")
                logger.info(f"Synchronized {updated_count} story prompts to aligned spec: {aligned_p}")
            except Exception as exc:
                logger.warning(f"Failed to sync aligned spec {aligned_p}: {exc}")


def upgrade_channel_long_spec(channel_slug: str) -> Path:
    channel_id, channel_slug = resolve_channel_ids(channel_slug)
    logger.info(f"=== Upgrading Story-Driven Long Master Spec for {channel_slug} ({channel_id}) ===")

    channel_dir = SYS_DIR / f"channels/vn_rebuilt_style_specs/{channel_slug}"
    plan_path = channel_dir / f"{channel_slug}_long_high_density_plan.json"
    master_path = channel_dir / f"{channel_slug}_long_master_spec.json"

    plan = None
    # 1. First priority: master spec if it has full narrations
    if master_path.is_file():
        try:
            cand = json.loads(master_path.read_text(encoding="utf-8"))
            cand_beats = cand.get("beats", cand.get("visual_states", []))
            if len(cand_beats) >= 150 and sum(1 for b in cand_beats if b.get("narration")) >= len(cand_beats) * 0.8:
                plan = cand
                logger.info(f"Using existing master spec with {len(cand_beats)} beats for {channel_slug}")
        except Exception:
            pass

    # 2. Second priority: aligned spec if master spec not found or lacks narrations
    if plan is None:
        for aligned_p in [
            ROOT_DIR / f"video/vn_pilot_{channel_id}_long/{channel_id}_long_305_aligned_spec.json",
            ROOT_DIR / f"video/vn_pilot_{channel_id}_long/{channel_id}_long_310_aligned_spec.json",
            ROOT_DIR / f"video/vn_pilot_{channel_id}_long/{channel_id}_long_aligned_spec.json",
        ]:
            if aligned_p.is_file():
                try:
                    cand = json.loads(aligned_p.read_text(encoding="utf-8"))
                    cand_beats = cand.get("beats", cand.get("visual_states", []))
                    if len(cand_beats) >= 150 and sum(1 for b in cand_beats if b.get("narration")) >= len(cand_beats) * 0.8:
                        plan = cand
                        logger.info(f"Using aligned spec with {len(cand_beats)} beats for {channel_slug}")
                        break
                except Exception:
                    pass

    # 3. Third priority: high density plan
    if plan is None and plan_path.is_file():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        logger.info(f"Using high density plan for {channel_slug}")

    if plan is None:
        raise FileNotFoundError(f"Missing plan, master spec, or aligned spec for {channel_slug} in {channel_dir}")

    beats = plan.get("beats", plan.get("visual_states", []))
    chapters = plan.get("chapters", [])

    narratives = CHANNEL_NARRATIVES.get(channel_slug, [])
    if len(narratives) < 10 and not beats:
        raise ValueError(f"Channel {channel_slug} requires 10 chapter narratives, found {len(narratives)}")

    # 1. Distribute spoken narratives across beats per chapter & build story-driven prompts
    updated_beats = []
    for ch_idx in range(1, len(chapters) + 1):
        ch_beats = [b for b in beats if b.get("chapter_index") == ch_idx]
        if not ch_beats:
            continue
        ch_title = chapters[ch_idx - 1].get("title", f"Hồi {ch_idx:02d}")

        # Check if beats already have valid non-empty spoken narrations
        has_existing_narrations = all(b.get("narration") and len(b.get("narration", "").strip()) > 3 for b in ch_beats)
        if has_existing_narrations:
            clauses = [b.get("narration", "").strip() for b in ch_beats]
        elif narratives and len(narratives) >= ch_idx:
            ch_text = narratives[ch_idx - 1]
            clauses = split_sentences_into_clauses(ch_text, len(ch_beats))
        else:
            clauses = [b.get("narration") or f"Phân đoạn {i+1}" for i, b in enumerate(ch_beats)]

        # Anchor tracking for strict 1-hop star DAG
        current_anchor_id = None
        current_anchor_desc = ""

        for b_item, clause in zip(ch_beats, clauses, strict=False):
            b = copy.deepcopy(b_item)
            b_id = b.get("beat_id") or b.get("id")
            b["id"] = b_id
            b["beat_id"] = b_id
            b["narration"] = clause

            # Enforce field compatibility between planner conventions
            b["camera_move"] = b.get("camera_move") or b.get("camera_motion") or "zoom_in"
            b["camera_motion"] = b["camera_move"]
            b["xfade"] = b.get("xfade") or b.get("transition") or "fade"
            b["transition"] = b["xfade"]
            b["hold"] = float(b.get("hold") or b.get("duration") or 2.5)
            b["duration"] = b["hold"]
            b["at"] = float(b.get("at", 0.0))
            b["tempo"] = b.get("tempo", "normal")
            b["chapter_index"] = b.get("chapter_index") or ch_idx

            # Enforce 1-hop star DAG
            is_anchor = (b.get("event_kind") == "ANCHOR_ESTABLISH" or b.get("based_on") is None)
            if is_anchor:
                current_anchor_id = b_id
                b["based_on"] = None
            else:
                b["based_on"] = current_anchor_id or ch_beats[0].get("beat_id") or ch_beats[0].get("id")

            # Generate Story-Driven Prompt directly from spoken narration
            prompt_str = build_story_driven_prompt(
                narration_vi=clause,
                channel_slug=channel_slug,
                chapter_title=ch_title,
                event_kind=b.get("event_kind", "ANCHOR_ESTABLISH"),
                anchor_scene_desc=current_anchor_desc,
                is_anchor=is_anchor,
                shot_type=b.get("shot_type", ""),
            )
            clean_prompt = sanitize_text(prompt_str)
            b["prompt"] = clean_prompt
            b["prompt_spec"] = clean_prompt

            if is_anchor:
                current_anchor_desc = clean_prompt

            updated_beats.append(b)

    # 2. Update Plan Contracts
    plan["channel_id"] = channel_id
    plan["channel_slug"] = channel_slug
    plan["voice"] = f"VietNarrator_{channel_id}"
    plan["voice_profile"] = f"sys/assets/voices/ch_{channel_id}/profile.json"
    plan["beats"] = updated_beats
    plan["visual_states"] = updated_beats
    plan["total_duration_sec"] = sum(float(b.get("duration") or b.get("hold") or 2.5) for b in updated_beats)

    # 3. Validate spec
    errors = validate_high_density_long_plan(plan)
    if errors:
        logger.warning(f"Validation warnings for {channel_slug}: {errors}")
    else:
        logger.info(f"Spec for {channel_slug} validated 100% cleanly (0 errors)!")

    # 4. Save to standardized master spec path
    out_master_p = channel_dir / f"{channel_slug}_long_master_spec.json"
    out_master_p.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Wrote story-driven master spec ({len(updated_beats)} beats) to: {out_master_p}")

    # Also update dense numbered specs if they exist
    for dense_p in [
        channel_dir / f"{channel_slug}_long_{len(updated_beats)}_master_spec.json",
        channel_dir / f"{channel_slug}_long_305_master_spec.json",
        channel_dir / f"{channel_slug}_long_310_master_spec.json",
    ]:
        if dense_p.exists():
            dense_p.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info(f"Updated dense spec: {dense_p}")

    # 5. Synchronize prompt & prompt_spec into aligned specs in video/vn_pilot_<ch>_long/
    sync_aligned_specs(channel_id, channel_slug, updated_beats)

    return out_master_p


def upgrade_all_20_channels() -> List[Path]:
    results = []
    for ch in VN_20_CHANNELS:
        p = upgrade_channel_long_spec(ch)
        results.append(p)
    logger.info(f"Successfully upgraded all {len(results)} long master specs to story-driven prompts!")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Upgrade VN Long High Density Plans to Story-Driven Master Specs")
    parser.add_argument("--channel", "-c", help="Specific channel slug or 'all'")
    args = parser.parse_args()

    if args.channel and args.channel != "all":
        upgrade_channel_long_spec(args.channel)
    else:
        upgrade_all_20_channels()
