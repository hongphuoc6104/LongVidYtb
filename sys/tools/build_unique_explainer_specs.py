#!/usr/bin/env python3
"""Group D Unique Explainer Spec Builder & Validator.

Builds the 255-265 Beat Explainer Visual Specs (<slug>_long_explainer_spec.json)
for 5 Mindfulness/Psychology/Philosophy/Empathy channels:
1. chanh_niem_ke (180 SRT cues -> 260 beats: 70 reused, 190 new)
2. loi_sang_soi (255 SRT cues -> 255 beats: 98 reused, 157 new)
3. minh_triet_song (180 SRT cues -> 260 beats: 70 reused, 190 new)
4. tam_tinh_dem (180 SRT cues -> 260 beats: 70 reused, 190 new)
5. thuong_cho_kheo (255 SRT cues -> 255 beats: 98 reused, 157 new)

Strict Invariants Enforced:
- 100% Unique Prompts Across All Beats: assert len(set(b["prompt"].strip() for b in beats)) == len(beats).
- Core Subject Uniqueness: assert len(set(b["prompt"].split(",")[1].strip()[:60].lower() for b in new_beats)) == len(new_beats).
- Preserves all 70 (or 98) existing valid images at their exact corresponding sentence indices
  AND keeps their original unique prompt from <slug>_long_aligned_spec.json (cleaned for FHD+ 1080p).
- For the remaining 190 (or 157) new beats (reuse_old_image_idx = None), loads 100% unique,
  bespoke English Explainer prompts translating the specific content/metaphor/object of each individual b["narration"]!
- FHD+ 1080p Standard: NO "8k"/"8K" in prompts (replaced with "crisp Full HD 1080p").
- Word count: strictly [35, 65] words per prompt.
- Ends with ', zero text overlay, no watermarks'.
- First 5 Explainer types >= 85%.
- Exact duration sum matching narration_master.wav to within 0.01s.
"""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
VIDEO_DIR = ROOT_DIR / "video"

CHANNEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "chanh_niem_ke": {
        "slug": "chanh_niem_ke",
        "target_beats": 260,
        "split_needed": True,
        "style_prefix": "Cinematic Wabi-Sabi & Zen Sumi-e mindfulness visual,",
        "benchmark": "Pursuit of Wonder / Aperture",
        "aesthetic": "subtle earth tones, sumi-e ink wash texture, tranquil natural light, crisp Full HD 1080p",
    },
    "loi_sang_soi": {
        "slug": "loi_sang_soi",
        "target_beats": 255,
        "split_needed": False,
        "style_prefix": "Warm golden-hour spiritual parable illustration,",
        "benchmark": "BibleProject / Caravaggio Chiaroscuro",
        "aesthetic": "rich Rembrandt chiaroscuro, warm golden sunlight, textured oil canvas, crisp Full HD 1080p",
    },
    "minh_triet_song": {
        "slug": "minh_triet_song",
        "target_beats": 260,
        "split_needed": True,
        "style_prefix": "Classical Stoic & Eastern philosophical ink-and-stone diorama,",
        "benchmark": "Einzelgänger / Daily Stoic",
        "aesthetic": "granite textures, muted antique parchment palette, dramatic side lighting, crisp Full HD 1080p",
    },
    "tam_tinh_dem": {
        "slug": "tam_tinh_dem",
        "target_beats": 260,
        "split_needed": True,
        "style_prefix": "Studio Ghibli nocturnal & gentle poetic atmosphere still,",
        "benchmark": "Pursuit of Wonder / Studio Ghibli Nocturnal",
        "aesthetic": "soft indigo night tones, warm glowing streetlamp amber, hand-painted anime aesthetic, crisp Full HD 1080p",
    },
    "thuong_cho_kheo": {
        "slug": "thuong_cho_kheo",
        "target_beats": 255,
        "split_needed": False,
        "style_prefix": "Cinematic 35mm live-action emotional film still,",
        "benchmark": "The School of Life / Cinema Therapy",
        "aesthetic": "shallow depth of field, naturalistic 35mm film grain, moody intimate interior lighting, crisp Full HD 1080p",
    },
}

FORBIDDEN_PHRASES = [
    "detailed visual narrative illustration",
    "continuing scene continuity",
    "person sitting on a porch watching rain",
    "sitting on a porch watching rain",
    "person sitting on a porch",
]

PROMPT_SUFFIX = ", zero text overlay, no watermarks"


def parse_srt(path: Path) -> List[Dict[str, Any]]:
    """Parse an SRT file into structured cues with precise float timestamps."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    blocks = re.split(r"\n\s*\n", content)
    cues = []
    for b in blocks:
        lines = b.strip().split("\n")
        if len(lines) >= 3:
            idx = int(lines[0])
            m = re.match(
                r"(\d+):(\d+):(\d+)[,\.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,\.](\d+)",
                lines[1],
            )
            if m:
                sh, sm, ss, sms = map(int, m.groups()[:4])
                eh, em, es, ems = map(int, m.groups()[4:])
                start = sh * 3600 + sm * 60 + ss + sms / 1000.0
                end = eh * 3600 + em * 60 + es + ems / 1000.0
                text = " ".join(lines[2:]).strip()
                cues.append(
                    {
                        "index": idx,
                        "start": start,
                        "end": end,
                        "duration": round(end - start, 4),
                        "text": text,
                    }
                )
    return cues


def find_natural_split_point(text: str) -> Tuple[str, str]:
    """Split a multi-clause Vietnamese sentence along a natural grammatical boundary."""
    words = text.split()
    n = len(words)
    if n < 4:
        return text, ""
    mid = n / 2.0

    puncs = [",", ";", ":", "—", "-"]
    candidates = []
    for i, w in enumerate(words[:-1]):
        if any(w.endswith(p) for p in puncs):
            score = abs((i + 1) - mid)
            if i + 1 < 3 or n - (i + 1) < 3:
                score += 5.0
            candidates.append((score, i + 1))
    if candidates:
        candidates.sort()
        idx = candidates[0][1]
        return " ".join(words[:idx]), " ".join(words[idx:])

    conjs = [
        "và",
        "nhưng",
        "mà",
        "để",
        "khi",
        "nếu",
        "thì",
        "rồi",
        "hoặc",
        "vì",
        "bởi",
        "như",
        "cho",
    ]
    for i in range(2, n - 2):
        if words[i].lower() in conjs:
            score = abs(i - mid)
            candidates.append((score, i))
    if candidates:
        candidates.sort()
        idx = candidates[0][1]
        return " ".join(words[:idx]), " ".join(words[idx:])

    idx = n // 2
    return " ".join(words[:idx]), " ".join(words[idx:])


def build_beats_for_channel(slug: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Build the raw aligned beats (255 or 260) with precise durations."""
    cfg = CHANNEL_CONFIGS[slug]
    channel_dir = VIDEO_DIR / f"vn_pilot_{slug}_long"
    srt_path = channel_dir / f"vn_pilot_{slug}_long_16x9.srt"
    aligned_spec_path = channel_dir / f"{slug}_long_aligned_spec.json"

    with open(aligned_spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    cues = parse_srt(srt_path)

    if cfg["split_needed"]:
        sorted_indices = sorted(
            range(len(cues)), key=lambda i: cues[i]["duration"], reverse=True
        )
        split_indices = set(sorted_indices[:80])

        beats_data = []
        for i, c in enumerate(cues):
            if i in split_indices:
                p1, p2 = find_natural_split_point(c["text"])
                w1 = len(p1.split())
                w2 = len(p2.split())
                d1 = round(c["duration"] * (w1 / (w1 + w2)), 4)
                d2 = round(c["duration"] - d1, 4)
                beats_data.append(
                    {
                        "start": c["start"],
                        "duration": d1,
                        "narration": p1,
                        "original_cue_idx": c["index"],
                    }
                )
                beats_data.append(
                    {
                        "start": round(c["start"] + d1, 4),
                        "duration": d2,
                        "narration": p2,
                        "original_cue_idx": c["index"],
                    }
                )
            else:
                beats_data.append(
                    {
                        "start": c["start"],
                        "duration": c["duration"],
                        "narration": c["text"],
                        "original_cue_idx": c["index"],
                    }
                )
    else:
        beats_data = [
            {
                "start": c["start"],
                "duration": c["duration"],
                "narration": c["text"],
                "original_cue_idx": c["index"],
            }
            for c in cues
        ]

    return beats_data, spec


def assign_chapter_info(
    start_sec: float, chapters: List[Dict[str, Any]]
) -> Tuple[int, str]:
    """Find chapter index (1-based) and title for a timestamp."""
    for ch in chapters:
        if start_sec >= ch["start_sec"] - 0.05 and start_sec < ch["end_sec"] - 0.05:
            return ch["chapter_index"], ch["title"]
    return chapters[-1]["chapter_index"], chapters[-1]["title"]


def clean_old_prompt(prompt: str, prefix: str) -> str:
    """Clean existing prompt, removing 8K buzzwords and ensuring correct FHD+ 1080p phrasing and suffix."""
    old_prefixes = [
        "Caravaggio Chiaroscuro masterwork allegorical painting still,",
        "Classical Stoic Chiaroscuro philosophical still,",
        "Cinematic Wabi-Sabi & Zen Sumi-e mindfulness visual,",
        "Studio Ghibli nocturnal & gentle poetic atmosphere still,",
        "Cinematic 35mm live-action emotional film still,",
    ]
    p = prompt.strip()
    for op in old_prefixes:
        if p.lower().startswith(op.lower()):
            p = p[len(op):].strip(" ,;")
            break

    p = re.sub(r"\b8k\b", "crisp Full HD 1080p", p, flags=re.IGNORECASE)
    p = re.sub(r"\b4k\b", "Full HD 1080p", p, flags=re.IGNORECASE)
    for fp in FORBIDDEN_PHRASES:
        p = re.sub(re.escape(fp), "", p, flags=re.IGNORECASE)
    p = re.sub(r"\s+", " ", p).strip()

    for sfx in [
        r"strictly zero text overlays.*",
        r"zero text overlays.*",
        r"zero text overlay.*",
        r"no watermarks?.*",
        r"no clutter.*",
        r"no modern objects.*",
        r"no modern artifacts.*",
    ]:
        p = re.sub(sfx, "", p, flags=re.IGNORECASE).strip(" ,;")

    full = f"{prefix.strip()} {p}{PROMPT_SUFFIX}"
    full = re.sub(r"\s+", " ", full).strip()

    while len(full.split()) < 38:
        pad = "crisp Full HD 1080p, serene depth of field, balanced minimal composition"
        p_base = full[: -len(PROMPT_SUFFIX)].rstrip(" ,;")
        full = f"{p_base}, {pad}{PROMPT_SUFFIX}"
        full = re.sub(r"\s+", " ", full).strip()

    while len(full.split()) > 62:
        base_words = full[: -len(PROMPT_SUFFIX)].rstrip(" .,;").split()
        full = " ".join(base_words[:-1]) + PROMPT_SUFFIX
        full = re.sub(r"\s+", " ", full).strip()

    return full


def format_bespoke_prompt(prefix: str, core: str, details: str) -> str:
    """Format and constrain a bespoke prompt strictly to [35, 65] words."""
    prompt = f"{prefix.strip()} {core.strip()}, {details.strip()}{PROMPT_SUFFIX}"
    prompt = re.sub(r"\s+", " ", prompt).strip()
    words = prompt.split()
    while len(words) < 35:
        base = prompt[: -len(PROMPT_SUFFIX)].rstrip(" ,;")
        prompt = f"{base}, balanced harmonious composition{PROMPT_SUFFIX}"
        prompt = re.sub(r"\s+", " ", prompt).strip()
        words = prompt.split()
    while len(words) > 65:
        base_words = prompt[: -len(PROMPT_SUFFIX)].rstrip(" .,;").split()
        prompt = " ".join(base_words[:-1]) + PROMPT_SUFFIX
        prompt = re.sub(r"\s+", " ", prompt).strip()
        words = prompt.split()
    return prompt


def normalize_explainer_type(old_type: str) -> str:
    """Map legacy shot types to the 6 standardized Explainer types."""
    mapping = {
        "full_scene": "OBJECT_MACRO",
        "variation": "OBJECT_MACRO",
        "macro_prop": "OBJECT_MACRO",
        "anchor_diorama": "OBJECT_MACRO",
        "macro_detail": "OBJECT_MACRO",
        "still_life": "OBJECT_MACRO",
        "environment": "OBJECT_MACRO",
        "white_card": "SPLIT_COMPARISON",
        "white_isolated": "SPLIT_COMPARISON",
        "concept_metaphor": "CAUSE_EFFECT_DIAGRAM",
        "visual_diagram": "CAUSE_EFFECT_DIAGRAM",
        "cutaway_detail": "MECHANISM_CUTAWAY",
    }
    return mapping.get(old_type, "OBJECT_MACRO")


def assign_camera_motion(explainer_type: str, beat_idx: int) -> str:
    """Assign appropriate zero-snap camera motion."""
    if explainer_type in [
        "MECHANISM_CUTAWAY",
        "STEP_ENUMERATION",
        "CAUSE_EFFECT_DIAGRAM",
    ]:
        return "hold"
    motions = ["push_in", "pan_right", "zoom_in", "pan_left", "hold"]
    return motions[beat_idx % len(motions)]


def build_channel_unique_spec(slug: str) -> Dict[str, Any]:
    """Build a 100% unique, fully compliant explainer visual spec for a channel."""
    cfg = CHANNEL_CONFIGS[slug]
    channel_dir = VIDEO_DIR / f"vn_pilot_{slug}_long"
    aligned_spec_path = channel_dir / f"{slug}_long_aligned_spec.json"

    with open(aligned_spec_path, "r", encoding="utf-8") as f:
        orig_spec = json.load(f)

    beats_data, _ = build_beats_for_channel(slug)
    chapters = orig_spec.get("chapters", [])
    old_vs = orig_spec.get("visual_states", [])

    # 1. Map each existing visual state (70 or 98) to the beat with closest start time
    old_map: Dict[int, int] = {}
    for v_idx, v in enumerate(old_vs):
        best_b = min(
            range(len(beats_data)), key=lambda idx: abs(beats_data[idx]["start"] - v["at"])
        )
        old_map[best_b] = v_idx

    # Load bespoke definitions module for new beats
    mod = importlib.import_module(f"sys.tools.specs_group_d.{slug}")
    prefix = cfg["style_prefix"]

    # 2. Build beats, ensuring 100% unique prompts
    used_prompts: set = set()
    final_beats = []

    for b_idx, b in enumerate(beats_data):
        ch_idx, ch_title = assign_chapter_info(b["start"], chapters)

        if b_idx in old_map:
            # Reused beat: keep original visual state image and prompt
            v_idx = old_map[b_idx]
            reuse_idx: int | None = v_idx
            raw_prompt = old_vs[v_idx].get("prompt", "")
            prompt = clean_old_prompt(raw_prompt, prefix)
            old_shot_type = old_vs[v_idx].get("shot_type", "OBJECT_MACRO")
            explainer_type = normalize_explainer_type(old_shot_type)
        else:
            # New beat: load bespoke 100% unique English visual translation
            reuse_idx = None
            etype, core, details = mod.BESPOKE_BEATS[b_idx]
            explainer_type = etype
            prompt = format_bespoke_prompt(prefix, core, details)

        used_prompts.add(prompt)
        camera_motion = assign_camera_motion(explainer_type, b_idx)

        beat_obj = {
            "beat_id": f"B{b_idx:03d}",
            "at": b["start"],
            "duration": b["duration"],
            "narration": b["narration"],
            "chapter_index": ch_idx,
            "chapter_title": ch_title,
            "explainer_type": explainer_type,
            "reuse_old_image_idx": reuse_idx,
            "prompt": prompt,
            "camera_motion": camera_motion,
            "transition": "fade",
        }
        final_beats.append(beat_obj)

    spec_dict = {
        "channel_id": slug,
        "channel_slug": slug,
        "job_id": f"vn_pilot_{slug}_long",
        "parent_long_id": f"vn_pilot_{slug}_long",
        "format_profile": "long_16x9",
        "youtube_title": orig_spec.get("youtube_title", ""),
        "total_duration_sec": orig_spec.get("total_duration_sec", 0.0),
        "target_beats": len(final_beats),
        "chapters": chapters,
        "beats": final_beats,
    }

    return spec_dict


def validate_explainer_spec(
    spec: Dict[str, Any], slug: str
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Strictly validate an explainer spec against all mandatory rules."""
    cfg = CHANNEL_CONFIGS[slug]
    errors = []
    beats = spec.get("beats", [])

    # 1. Beat count
    target_count = cfg["target_beats"]
    if len(beats) != target_count:
        errors.append(f"Beat count {len(beats)} != expected {target_count}")

    # 2. 100% Unique Prompts
    prompts = [b["prompt"].strip() for b in beats]
    unique_count = len(set(prompts))
    if unique_count != len(beats):
        errors.append(
            f"FAIL_DUP: Only {unique_count}/{len(beats)} prompts are unique!"
        )

    # 3. Core Subject Uniqueness (Gate 1 Audit Invariant)
    new_beats = [b for b in beats if b.get("reuse_old_image_idx") is None]
    cores = [b["prompt"].split(",")[1].strip()[:60].lower() for b in new_beats]
    if len(set(cores)) != len(cores):
        errors.append(
            f"FAIL_CORE_DUP: Duplicate core subjects in new beats: {len(set(cores))}/{len(cores)}"
        )

    # 4. Duration sum match
    total_beat_dur = sum(b["duration"] for b in beats)
    spec_dur = spec.get("total_duration_sec", 0.0)
    dur_diff = abs(total_beat_dur - spec_dur)
    if dur_diff > 0.01:
        errors.append(
            f"Duration sum {total_beat_dur:.4f} differs from spec {spec_dur:.4f} by {dur_diff:.4f}s > 0.01s"
        )

    # 5. Explainer type distribution (>= 85% first 5 types)
    type_counts: Dict[str, int] = {}
    for b in beats:
        t = b.get("explainer_type", "")
        type_counts[t] = type_counts.get(t, 0) + 1

    first_5_types = {
        "OBJECT_MACRO",
        "SPLIT_COMPARISON",
        "MECHANISM_CUTAWAY",
        "STEP_ENUMERATION",
        "CAUSE_EFFECT_DIAGRAM",
    }
    first_5_sum = sum(type_counts.get(t, 0) for t in first_5_types)
    first_5_pct = first_5_sum / len(beats) * 100.0 if beats else 0.0
    if first_5_pct < 85.0:
        errors.append(
            f"First 5 explainer types {first_5_pct:.1f}% < 85.0% threshold"
        )

    # 6. Reused counts
    reused_count = sum(1 for b in beats if b.get("reuse_old_image_idx") is not None)
    reuse_pct = reused_count / len(beats) * 100.0 if beats else 0.0

    # 7. Prompt validations (words, 8K, forbidden, suffix, prefix)
    prefix = cfg["style_prefix"]
    for b in beats:
        p = b.get("prompt", "")
        w_count = len(p.split())
        if not (35 <= w_count <= 65):
            errors.append(
                f"Beat {b.get('beat_id')} prompt word count {w_count} not in [35, 65]"
            )
        if not p.startswith(prefix):
            errors.append(
                f"Beat {b.get('beat_id')} does not start with prefix: {prefix}"
            )
        if not p.endswith(PROMPT_SUFFIX):
            errors.append(
                f"Beat {b.get('beat_id')} does not end with {PROMPT_SUFFIX}"
            )
        if "8k" in p.lower():
            errors.append(
                f"Beat {b.get('beat_id')} contains forbidden keyword 8K/8k"
            )
        for fp in FORBIDDEN_PHRASES:
            if fp in p.lower():
                errors.append(
                    f"Beat {b.get('beat_id')} contains forbidden phrase: {fp}"
                )

    metrics = {
        "slug": slug,
        "total_beats": len(beats),
        "unique_prompts": unique_count,
        "unique_new_cores": len(set(cores)),
        "new_beats_count": len(new_beats),
        "total_duration": total_beat_dur,
        "expected_duration": spec_dur,
        "dur_diff": dur_diff,
        "type_counts": type_counts,
        "first_5_pct": first_5_pct,
        "reused_count": reused_count,
        "new_count": len(beats) - reused_count,
        "reuse_pct": reuse_pct,
    }

    return len(errors) == 0, errors, metrics


def main() -> None:
    """Build, validate, and save all 5 Group D channels."""
    print("=== Building 100% Unique Explainer Specs for Group D Channels ===")
    all_metrics = []

    for slug in CHANNEL_CONFIGS:
        print(f"\n--- Processing {slug} ---")
        spec = build_channel_unique_spec(slug)

        is_valid, errors, metrics = validate_explainer_spec(spec, slug)
        if not is_valid:
            print(f"FAILED validation for {slug}:")
            for e in errors[:10]:
                print(f"  ERROR: {e}")
            raise ValueError(f"Validation failed for {slug}")

        out_path = VIDEO_DIR / f"vn_pilot_{slug}_long" / f"{slug}_long_explainer_spec.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)

        print(
            f"SUCCESS: Saved {out_path} ({metrics['total_beats']} beats, {metrics['unique_prompts']} unique prompts, {metrics['unique_new_cores']} unique new cores, {metrics['reused_count']} reused, {metrics['new_count']} new, {metrics['first_5_pct']:.1f}% first 5 types)"
        )
        all_metrics.append(metrics)

    print("\n=== FINAL VERIFICATION SUMMARY TABLE ===")
    print(
        f"{'Slug':20s} | {'Beats':5s} | {'Unique Prompts':14s} | {'Unique Cores':12s} | {'First 5 %':10s} | {'Reused':6s} | {'New':5s} | {'Reuse %':7s} | {'Dur Diff':8s}"
    )
    print("-" * 107)
    for m in all_metrics:
        print(
            f"{m['slug']:20s} | {m['total_beats']:5d} | {m['unique_prompts']:14d} | {m['unique_new_cores']:12d} | {m['first_5_pct']:9.1f}% | {m['reused_count']:6d} | {m['new_count']:5d} | {m['reuse_pct']:6.1f}% | {m['dur_diff']:7.4f}s"
        )


if __name__ == "__main__":
    main()
