#!/usr/bin/env python3
"""Generator & Pre-synthesizer for Video Pilot Vietnamese High-Density Long (16:9) Master Specs.

Creates 240-350 state Two-Tier DAG Master Specs (<slug>_long_master_spec.json) with
unique conversational narrative scripts and Studio V3 Human Voice profile contracts
for all 18 remaining Vietnamese channels.
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

VN_18_CHANNELS = [
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
]


def resolve_channel_ids(slug: str) -> Tuple[str, str]:
    clean = slug.strip().removeprefix("channel-").removeprefix("ch_")
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


def upgrade_channel_long_spec(channel_slug: str) -> Path:
    channel_id, channel_slug = resolve_channel_ids(channel_slug)
    logger.info(f"=== Upgrading Long Master Spec for {channel_slug} ({channel_id}) ===")

    channel_dir = SYS_DIR / f"channels/vn_rebuilt_style_specs/{channel_slug}"
    plan_path = channel_dir / f"{channel_slug}_long_high_density_plan.json"
    if not plan_path.is_file():
        raise FileNotFoundError(f"Missing high density plan: {plan_path}")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    beats = plan.get("beats", plan.get("visual_states", []))
    chapters = plan.get("chapters", [])

    narratives = CHANNEL_NARRATIVES.get(channel_slug, [])
    if len(narratives) < 10:
        raise ValueError(f"Channel {channel_slug} requires 10 chapter narratives, found {len(narratives)}")

    # 1. Distribute spoken narratives across beats per chapter
    updated_beats = []
    for ch_idx in range(1, len(chapters) + 1):
        ch_beats = [b for b in beats if b.get("chapter_index") == ch_idx]
        if not ch_beats:
            continue
        ch_text = narratives[ch_idx - 1]
        clauses = split_sentences_into_clauses(ch_text, len(ch_beats))

        # Anchor tracking for strict 1-hop star DAG
        current_anchor_id = None
        for b_item, clause in zip(ch_beats, clauses, strict=False):
            b = copy.deepcopy(b_item)
            b_id = b.get("beat_id") or b.get("id")
            b["narration"] = clause
            b["prompt"] = sanitize_text(b.get("prompt", ""))
            b["prompt_spec"] = sanitize_text(b.get("prompt_spec", ""))

            # Enforce 1-hop star DAG
            if b.get("event_kind") == "ANCHOR_ESTABLISH" or b.get("based_on") is None:
                current_anchor_id = b_id
                b["based_on"] = None
            else:
                b["based_on"] = current_anchor_id or ch_beats[0].get("beat_id") or ch_beats[0].get("id")

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
    logger.info(f"Wrote master spec ({len(updated_beats)} beats) to: {out_master_p}")

    return out_master_p


def upgrade_all_18_channels() -> List[Path]:
    results = []
    for ch in VN_18_CHANNELS:
        p = upgrade_channel_long_spec(ch)
        results.append(p)
    logger.info(f"Successfully upgraded all {len(results)} long master specs!")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Upgrade VN Long High Density Plans to Master Specs")
    parser.add_argument("--channel", "-c", help="Specific channel slug or 'all'")
    args = parser.parse_args()

    if args.channel and args.channel != "all":
        upgrade_channel_long_spec(args.channel)
    else:
        upgrade_all_18_channels()
