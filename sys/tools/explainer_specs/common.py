"""Common utilities and validators for Group B Explainer Specs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FORBIDDEN_PHRASES = [
    "detailed visual narrative illustration",
    "continuing scene continuity",
    "sitting at a desk staring at a monitor",
    "staring at a computer monitor",
    "staring at a monitor",
]

SUFFIX = ", zero text overlay, no watermarks"


def parse_srt(path: str | Path) -> List[Dict[str, Any]]:
    """Parse SRT into cues with exact timing and text."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(
        r"(\d+)\s*\n(\d{2}):(\d{2}):(\d{2})[,\.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,\.](\d{3})\s*\n(.*?)(?=\n\s*\n|\Z)",
        re.DOTALL,
    )
    cues = []
    for m in pattern.finditer(content.strip()):
        s_h, s_m, s_s, s_ms = int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
        e_h, e_m, e_s, e_ms = int(m.group(6)), int(m.group(7)), int(m.group(8)), int(m.group(9))
        start_sec = s_h * 3600 + s_m * 60 + s_s + s_ms / 1000.0
        end_sec = e_h * 3600 + e_m * 60 + e_s + e_ms / 1000.0
        cues.append({
            "idx": int(m.group(1)) - 1,
            "start_sec": start_sec,
            "end_sec": end_sec,
            "duration": round(end_sec - start_sec, 4),
            "text": m.group(10).strip(),
        })
    return cues


def clean_scene_text(scene_text: str, style_prefix: str) -> str:
    """Clean text by stripping duplicate prefixes, forbidden phrases, and old negative rules."""
    s = scene_text.strip().rstrip(",")
    p_clean = style_prefix.strip().rstrip(",")
    if s.lower().startswith(p_clean.lower()):
        s = s[len(p_clean):].strip().lstrip(",")

    for pat in [
        r"strictly zero text overlays.*",
        r"zero text overlays.*",
        r"zero text overlay.*",
        r"no watermarks?.*",
        r"no cartoons?.*",
        r"no stickmen?.*",
        r"no clutter.*",
        r"detailed visual narrative illustration,?",
        r"continuing scene continuity,?",
        r"continuing from [a-z0-9_]+,?",
    ]:
        s = re.sub(pat, "", s, flags=re.I)

    s = re.sub(
        r"sitting at a desk staring at a monitor",
        "inspecting the digital interface with focused posture",
        s,
        flags=re.I,
    )
    s = re.sub(r"\b8[kK]\b", "crisp Full HD 1080p", s)
    return re.sub(r"\s+", " ", s).strip().strip(",")


def format_prompt(
    style_prefix: str,
    scene_text: str,
    aesthetic_traits: str,
    min_words: int = 35,
    max_words: int = 65,
) -> str:
    """Format and pad/trim prompt by assembling complete clauses within [35, 65] words."""
    scene = clean_scene_text(scene_text, style_prefix)
    aesthetic = clean_scene_text(aesthetic_traits, style_prefix)
    suffix_len = len(SUFFIX.strip(", ").split())

    core = f"{style_prefix} {scene}"

    # Try adding complete comma-separated clauses from aesthetic
    clauses = [c.strip() for c in aesthetic.split(",") if c.strip()]
    assembled = core
    for c in clauses:
        test_assembled = f"{assembled}, {c}"
        if len(test_assembled.split()) + suffix_len <= max_words:
            assembled = test_assembled
        else:
            break

    prompt = f"{assembled}{SUFFIX}"
    words = prompt.split()

    # If core itself was too long (> max_words)
    if len(words) > max_words:
        budget = max_words - suffix_len
        core_words = core.split()
        sub = " ".join(core_words[:budget])
        if "," in sub:
            sub = sub.rsplit(",", 1)[0].strip()
        prompt = f"{sub}{SUFFIX}"
        words = prompt.split()

    # If too short
    if len(words) < min_words:
        pad = "standard clear composition with ample negative space"
        prompt = f"{assembled}, {pad}{SUFFIX}"
        words = prompt.split()

    if len(words) < min_words:
        pad2 = "balanced visual hierarchy, authentic lighting"
        prompt = f"{assembled}, {pad2}, standard clear composition with ample negative space{SUFFIX}"

    return prompt


def validate_spec(spec: Dict[str, Any], expected_beats: int, max_situational_ratio: float = 0.15) -> Dict[str, Any]:
    """Validate all hard invariants on an explainer spec."""
    beats = spec.get("beats", [])
    assert len(beats) == expected_beats, f"Expected {expected_beats} beats, got {len(beats)}"

    type_counts = {}
    word_counts = []
    reused_count = 0

    for i, b in enumerate(beats):
        bid = b.get("beat_id")
        narr = b.get("narration")
        dur = b.get("duration")
        etype = b.get("explainer_type")
        prompt = b.get("prompt")
        reuse_idx = b.get("reuse_old_image_idx")

        assert bid == f"B{i:03d}", f"Beat {i} has invalid id {bid}"
        assert narr, f"Beat {i} missing narration"
        assert dur > 0, f"Beat {i} duration <= 0: {dur}"
        assert etype in [
            "SPLIT_COMPARISON",
            "OBJECT_MACRO",
            "STEP_ENUMERATION",
            "MECHANISM_CUTAWAY",
            "CAUSE_EFFECT_DIAGRAM",
            "SITUATIONAL_ACTION",
        ], f"Beat {i} invalid explainer_type {etype}"

        type_counts[etype] = type_counts.get(etype, 0) + 1

        if reuse_idx is not None:
            reused_count += 1

        # Check prompt
        assert prompt.endswith(SUFFIX), f"Beat {i} prompt does not end with SUFFIX: {prompt[-40:]}"
        assert not re.search(r"\b8[kK]\b", prompt), f"Beat {i} contains forbidden 8K keyword: {prompt}"
        for fb in FORBIDDEN_PHRASES:
            assert fb not in prompt.lower(), f"Beat {i} contains forbidden phrase '{fb}': {prompt}"

        wc = len(prompt.split())
        assert 35 <= wc <= 65, f"Beat {i} prompt word count {wc} out of bounds [35, 65]: {prompt}"
        word_counts.append(wc)

    first_5_count = sum(type_counts.get(t, 0) for t in [
        "SPLIT_COMPARISON",
        "OBJECT_MACRO",
        "STEP_ENUMERATION",
        "MECHANISM_CUTAWAY",
        "CAUSE_EFFECT_DIAGRAM",
    ])
    situational_count = type_counts.get("SITUATIONAL_ACTION", 0)

    first_5_ratio = first_5_count / len(beats)
    situational_ratio = situational_count / len(beats)
    reuse_ratio = reused_count / len(beats)

    unique_prompts = set(b["prompt"].strip() for b in beats)
    assert len(unique_prompts) == len(beats), (
        f"Duplicate prompts found! {len(unique_prompts)} unique out of {len(beats)} beats"
    )

    assert first_5_ratio >= 0.85, f"First 5 explainer types {first_5_ratio:.2%} < 85%"
    assert situational_ratio <= max_situational_ratio, f"Situational ratio {situational_ratio:.2%} > {max_situational_ratio:.2%}"

    # Return stats summary
    return {
        "total_beats": len(beats),
        "explainer_type_distribution": type_counts,
        "first_5_types_ratio": round(first_5_ratio, 4),
        "situational_ratio": round(situational_ratio, 4),
        "reused_count": reused_count,
        "new_generation_count": len(beats) - reused_count,
        "reuse_ratio": round(reuse_ratio, 4),
        "min_word_count": min(word_counts),
        "max_word_count": max(word_counts),
        "avg_word_count": round(sum(word_counts) / len(word_counts), 1),
    }
