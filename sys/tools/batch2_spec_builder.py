"""Batch 2 Spec Builder and Validator.

Provides utilities to compile, assemble, and strictly validate the 16:9 Long aligned specs
for the 9 channels in Batch 2:
1. luat_ngam
2. minh_triet_song
3. nao_luoi
4. nghe_song_sot
5. su_ke_lai
6. tam_tinh_dem
7. thuong_cho_kheo
8. ua_sao_vay
9. vu_tru_ti_hon
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from sys.tools.story_driven_prompt_builder import CHANNEL_ALIASES, CHANNEL_STYLE_PROFILES
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
VIDEO_DIR = ROOT_DIR / "video"

BUZZWORDS_REGEX = re.compile(
    r"\b(8k|4k|uhd|ultra\s*hd|hyper-detailed|hyperrealistic|photorealistic|masterpiece)\b",
    re.IGNORECASE,
)

FRAMING_OPTIONS = [
    "Establishing wide diorama:",
    "Detailed scene showing:",
    "Macro close-up cutaway burst focusing on:",
    "Dynamic perspective cutaway showing:",
    "Visual mechanism cutaway demonstrating:",
]


def clean_ascii(text: str) -> str:
    """Enforce pure ASCII text with zero diacritics and clean spaces."""
    cleaned = re.sub(r"[^\x00-\x7F]+", "", text)
    cleaned = BUZZWORDS_REGEX.sub("detailed", cleaned)
    cleaned = re.sub(r"\bdetailed\s+detailed\b", "detailed", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def assemble_prompt(
    slug: str,
    scene_description: str,
    beat_index: int,
    is_anchor: bool = True,
) -> str:
    """Assemble a rich story-driven prompt using the channel profile."""
    clean_slug = CHANNEL_ALIASES.get(slug, slug.replace("_", "-"))
    prof = CHANNEL_STYLE_PROFILES.get(clean_slug)
    if not prof:
        raise ValueError(f"Unknown channel profile for {slug}")

    scene_clean = clean_ascii(scene_description).strip().rstrip(".")
    if is_anchor:
        framing = "Establishing wide diorama:"
    else:
        framing = FRAMING_OPTIONS[beat_index % len(FRAMING_OPTIONS)]

    parts = [
        prof.style_prefix.strip(),
        f"{framing} {scene_clean}.",
        prof.aesthetic_traits.strip(),
        prof.negative_rules.strip(),
    ]
    prompt = " ".join(parts)
    prompt = clean_ascii(prompt)
    return prompt


def generate_base_clusters(slug: str) -> List[Dict[str, Any]]:
    """Extract and merge anchor clusters for a given channel."""
    channel_dir = VIDEO_DIR / f"vn_pilot_{slug}_long"
    spec_path = channel_dir / f"{slug}_long_aligned_spec.json"
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    raw_beats = spec.get("beats", spec.get("visual_beats", []))
    clusters: List[tuple[str, List[Dict[str, Any]]]] = []
    curr_anchor = None
    curr_children = []
    for b in raw_beats:
        bid = b["beat_id"]
        m = re.match(r"^(CH\d+_A\d+)(?:_B\d+)?$", bid)
        base = m.group(1) if m else bid
        if base != curr_anchor:
            if curr_anchor is not None:
                clusters.append((curr_anchor, curr_children))
            curr_anchor = base
            curr_children = [b]
        else:
            curr_children.append(b)
    if curr_anchor is not None:
        clusters.append((curr_anchor, curr_children))

    result = []
    curr_at = 0.0
    for _idx, (anchor_id, children) in enumerate(clusters):
        dur = sum(float(c["duration"]) for c in children)
        narr = " ".join((c.get("narration") or c.get("text") or "").strip() for c in children)
        narr = re.sub(r"\s+", " ", narr).strip()
        ch_idx = children[0].get("chapter_index")
        if not ch_idx:
            m = re.match(r"^CH(\d+)", anchor_id)
            ch_idx = int(m.group(1)) if m else 1

        result.append({
            "beat_id": anchor_id,
            "chapter_index": ch_idx,
            "chapter_title": children[0].get("chapter_title", f"Hoi {ch_idx:02d}"),
            "at": round(curr_at, 4),
            "duration": round(dur, 4),
            "narration": narr,
        })
        curr_at += dur

    return result


def compile_and_save_spec(
    slug: str,
    beat_scenes: Dict[str, str],
) -> Dict[str, Any]:
    """Merge anchor clusters, apply story-aligned scenes, save spec and return verification report."""
    channel_dir = VIDEO_DIR / f"vn_pilot_{slug}_long"
    spec_path = channel_dir / f"{slug}_long_aligned_spec.json"
    tts_path = channel_dir / "_work_long/tts_metadata.json"

    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")
    if not tts_path.exists():
        raise FileNotFoundError(f"TTS metadata file not found: {tts_path}")

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    with open(tts_path, "r", encoding="utf-8") as f:
        tts = json.load(f)

    raw_beats = spec.get("beats", spec.get("visual_beats", []))
    tts_dur = float(tts["total_duration"])

    clusters: List[tuple[str, List[Dict[str, Any]]]] = []
    curr_anchor = None
    curr_children = []
    for b in raw_beats:
        bid = b["beat_id"]
        m = re.match(r"^(CH\d+_A\d+)(?:_B\d+)?$", bid)
        base = m.group(1) if m else bid
        if base != curr_anchor:
            if curr_anchor is not None:
                clusters.append((curr_anchor, curr_children))
            curr_anchor = base
            curr_children = [b]
        else:
            curr_children.append(b)
    if curr_anchor is not None:
        clusters.append((curr_anchor, curr_children))

    motions = ["push_in", "zoom_in", "pan_right", "pan_left"]
    merged_beats: List[Dict[str, Any]] = []
    curr_at = 0.0

    for idx, (anchor_id, children) in enumerate(clusters):
        dur = sum(float(c["duration"]) for c in children)
        narr = " ".join((c.get("narration") or c.get("text") or "").strip() for c in children)
        narr = re.sub(r"\s+", " ", narr).strip()
        ch_idx = children[0].get("chapter_index")
        if not ch_idx:
            m = re.match(r"^CH(\d+)", anchor_id)
            ch_idx = int(m.group(1)) if m else 1

        cam = motions[idx % len(motions)]

        scene_desc = beat_scenes.get(anchor_id)
        if not scene_desc:
            raise ValueError(f"Missing scene description for beat {anchor_id} in {slug}")

        prompt = assemble_prompt(slug, scene_desc, idx, is_anchor=(idx == 0))

        beat_dict = {
            "beat_id": anchor_id,
            "id": anchor_id,
            "based_on": None,
            "chapter_index": ch_idx,
            "chapter_title": children[0].get("chapter_title", f"Hoi {ch_idx:02d}"),
            "at": round(curr_at, 4),
            "duration": round(dur, 4),
            "hold": round(dur, 4),
            "narration": narr,
            "camera_motion": cam,
            "camera_move": cam,
            "transition": "fade",
            "xfade": "fade",
            "event_kind": "ANCHOR_ESTABLISH",
            "shot_type": "full_scene",
            "tempo": "normal",
            "prompt": prompt,
            "prompt_spec": prompt,
        }
        merged_beats.append(beat_dict)
        curr_at += dur

    # Align duration to exact tts_dur
    total_dur = sum(b["duration"] for b in merged_beats)
    diff = tts_dur - total_dur
    merged_beats[-1]["duration"] = round(merged_beats[-1]["duration"] + diff, 4)
    merged_beats[-1]["hold"] = merged_beats[-1]["duration"]

    # Recompute 'at' timestamps strictly
    acc = 0.0
    for b in merged_beats:
        b["at"] = round(acc, 4)
        acc += b["duration"]

    # Update spec
    spec["beats"] = merged_beats
    spec["visual_states"] = merged_beats
    spec["total_duration_sec"] = tts_dur

    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    # Remove stale 305 spec
    stale_305 = channel_dir / f"{slug}_long_305_aligned_spec.json"
    if stale_305.exists():
        stale_305.unlink()

    # Verification report
    final_dur = sum(b["duration"] for b in merged_beats)
    prompts = [b["prompt"] for b in merged_beats]
    unique_prompts = set(prompts)
    non_ascii_count = sum(1 for p in prompts if any(ord(c) >= 128 for c in p))
    boilerplate_matches = [p for p in prompts if "clearly demonstrating the cause-and-effect explanatory mechanism" in p]

    report = {
        "slug": slug,
        "beat_count": len(merged_beats),
        "unique_prompts": len(unique_prompts),
        "is_100_unique": len(unique_prompts) == len(merged_beats),
        "total_duration": round(final_dur, 4),
        "tts_duration": round(tts_dur, 4),
        "duration_diff": round(abs(final_dur - tts_dur), 6),
        "non_ascii_count": non_ascii_count,
        "boilerplate_count": len(boilerplate_matches),
        "is_valid": (
            70 <= len(merged_beats) <= 117
            and len(unique_prompts) == len(merged_beats)
            and abs(final_dur - tts_dur) < 0.05
            and non_ascii_count == 0
            and len(boilerplate_matches) == 0
        ),
    }
    return report
