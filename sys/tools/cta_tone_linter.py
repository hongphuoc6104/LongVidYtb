#!/usr/bin/env python3
"""CTA Tone and Placement Linter for Video Pilot.

Enforces Video Pilot V2 CTA and Pacing Governance per contract §3.4:
  - Exactly one primary CTA per video (close).
  - Short: exactly one bridge to parent long-form video; parent_long_id required.
  - Long: <= 1 mid_cta (sitting at 35-45% of runtime).
  - Banned phrase detection (diacritic- and case-insensitive).
  - Syllable budget (whitespace tokens): bridge <= 22 syllables, close <= 24 syllables.
  - Placement: final 15% (short) / final 25s (long); never inside the first 3s hook.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

DEFAULT_BANNED_CTA_PHRASES: tuple[str, ...] = (
    "đừng quên like",
    "nhấn chuông",
    "bấm chuông",
    "like share",
    "like và share",
    "like, share",
    "subscribe",
    "đăng ký kênh",
    "ấn theo dõi ngay",
    "bấm theo dõi ngay",
    "hãy like",
    "nhớ like",
    "để ủng hộ kênh",
)

MAX_BRIDGE_SYLLABLES = 22
MAX_CLOSE_SYLLABLES = 24


def strip_diacritics(text: str) -> str:
    """Normalize and strip Vietnamese diacritics for insensitive matching."""
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "D")
    nfd = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return stripped.lower()


def count_syllables_whitespace(text: str) -> int:
    """Count syllables by whitespace tokens per contract §3.4."""
    if not text:
        return 0
    clean = re.sub(r"\[pause:[^\]]+\]", "", text).strip()
    return len([w for w in clean.split() if w])


def _find_phrase_insensitive(phrase: str, text: str) -> bool:
    """Diacritic- and punctuation-flexible check whether phrase appears in text."""
    norm_phrase = strip_diacritics(phrase)
    norm_text = strip_diacritics(text)

    # Normalize whitespace and punctuation
    clean_p = re.sub(r"[^\w\s]", " ", norm_phrase)
    clean_p = " ".join(clean_p.split())
    clean_t = re.sub(r"[^\w\s]", " ", norm_text)
    clean_t = " ".join(clean_t.split())

    if not clean_p or not clean_t:
        return False
    return clean_p in clean_t


def lint_cta(
    brief: Dict[str, Any],
    content: Dict[str, Any],
    timings: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
) -> List[str]:
    """Validate CTA plan, tone, syllable budgets, and placement.

    Args:
        brief: brief.json dictionary
        content: content.json dictionary
        timings: optional measured timing data (dict with timestamps or list of scenes)

    Returns:
        List of error strings. Empty list indicates full compliance.
    """
    errors: List[str] = []

    format_profile = brief.get("format_profile") or "short_9x16"
    is_short = format_profile == "short_9x16"
    is_long = format_profile == "long_16x9"

    # 1. Short requires parent_long_id
    if is_short:
        parent_long_id = brief.get("parent_long_id")
        if not parent_long_id:
            errors.append("CTA_MISSING_PARENT_LONG_ID: short_9x16 video must declare 'parent_long_id'")

    # Extract CTA plan
    cta_plan = brief.get("cta_plan")
    if not cta_plan and isinstance(brief.get("packaging"), dict):
        cta_plan = brief["packaging"].get("cta_plan")

    if not cta_plan or not isinstance(cta_plan, dict):
        errors.append("CTA_MISSING_PLAN: brief must declare a valid 'cta_plan' dictionary")
        cta_plan = {}

    bridge = str(cta_plan.get("bridge") or "").strip()
    close = str(cta_plan.get("close") or "").strip()
    mid_cta = cta_plan.get("mid_cta")

    # 2. Exactly one close per video
    if not close:
        errors.append("CTA_MISSING_CLOSE: video must declare exactly one primary closing CTA")
    else:
        close_syl = count_syllables_whitespace(close)
        if close_syl > MAX_CLOSE_SYLLABLES:
            errors.append(
                f"CTA_CLOSE_SYLLABLES_EXCEEDED: close CTA has {close_syl} syllables (max {MAX_CLOSE_SYLLABLES}): '{close}'"
            )

    # 3. Short requires bridge
    if is_short:
        if not bridge:
            errors.append("CTA_MISSING_BRIDGE: short_9x16 must declare exactly one bridge to the long video")
        else:
            bridge_syl = count_syllables_whitespace(bridge)
            if bridge_syl > MAX_BRIDGE_SYLLABLES:
                errors.append(
                    f"CTA_BRIDGE_SYLLABLES_EXCEEDED: bridge CTA has {bridge_syl} syllables (max {MAX_BRIDGE_SYLLABLES}): '{bridge}'"
                )
        if mid_cta is not None:
            errors.append("CTA_SHORT_NO_MID_CTA: short_9x16 video cannot have a mid_cta")

    # 4. Long may have <= 1 mid_cta
    if is_long and mid_cta is not None:
        mid_text = str(mid_cta).strip()
        if not mid_text:
            errors.append("CTA_EMPTY_MID_CTA: mid_cta is declared but empty")

    # 5. Banned phrases detection across all narrations and CTA text
    banned_phrases = list(DEFAULT_BANNED_CTA_PHRASES)
    engagement = brief.get("engagement")
    if isinstance(engagement, dict) and engagement.get("banned_cta_phrases"):
        for bp in engagement["banned_cta_phrases"]:
            if bp not in banned_phrases:
                banned_phrases.append(bp)

    # Collect all script texts
    scenes = content.get("scenes", [])
    script_texts = []
    for sc in scenes:
        narr = sc.get("narration", "")
        if narr:
            script_texts.append((sc.get("id", "SC??"), narr))

    all_cta_strings = [bridge, close]
    if mid_cta:
        all_cta_strings.append(str(mid_cta))

    for phrase in banned_phrases:
        for cta_str in all_cta_strings:
            if cta_str and _find_phrase_insensitive(phrase, cta_str):
                errors.append(
                    f"CTA_BANNED_PHRASE: CTA text contains banned phrase '{phrase}': '{cta_str}'"
                )
        for sc_id, narr in script_texts:
            if _find_phrase_insensitive(phrase, narr):
                errors.append(
                    f"CTA_BANNED_PHRASE: {sc_id} narration contains banned phrase '{phrase}'"
                )

    # 6. Placement rules
    # Never inside the first 3s hook (SC01 opening)
    if scenes:
        sc01_narr = scenes[0].get("narration", "")
        if close and _find_phrase_insensitive(close, sc01_narr):
            errors.append("CTA_INSIDE_HOOK: close CTA cannot appear in opening scene hook (SC01)")
        if bridge and _find_phrase_insensitive(bridge, sc01_narr):
            errors.append("CTA_INSIDE_HOOK: bridge CTA cannot appear in opening scene hook (SC01)")

        # In short, bridge and close must be in the final scene
        if is_short and len(scenes) > 1:
            last_narr = scenes[-1].get("narration", "")
            if close and not _find_phrase_insensitive(close, last_narr):
                errors.append("CTA_CLOSE_NOT_IN_OUTRO: short_9x16 close CTA must be in the final scene narration")
            if bridge and not _find_phrase_insensitive(bridge, last_narr):
                errors.append("CTA_BRIDGE_NOT_IN_OUTRO: short_9x16 bridge CTA must be in the final scene narration")

    # 7. Measured timings placement checks
    if timings is not None:
        if isinstance(timings, dict):
            tot_dur = float(timings.get("total_duration", 0.0))
            bridge_at = timings.get("bridge_start")
            close_at = timings.get("close_start")
            mid_at = timings.get("mid_cta_start")

            if tot_dur > 0:
                if bridge_at is not None:
                    b_sec = float(bridge_at)
                    if b_sec < 3.0:
                        errors.append(f"CTA_INSIDE_HOOK: bridge CTA starts at {b_sec:.2f}s (< 3.0s)")
                    if is_short and b_sec < tot_dur * 0.85:
                        errors.append(
                            f"CTA_NOT_IN_FINAL_WINDOW: bridge CTA starts at {b_sec:.2f}s (must be in final 15% >= {tot_dur * 0.85:.2f}s)"
                        )

                if close_at is not None:
                    c_sec = float(close_at)
                    if c_sec < 3.0:
                        errors.append(f"CTA_INSIDE_HOOK: close CTA starts at {c_sec:.2f}s (< 3.0s)")
                    if is_short and c_sec < tot_dur * 0.85:
                        errors.append(
                            f"CTA_NOT_IN_FINAL_WINDOW: close CTA starts at {c_sec:.2f}s (must be in final 15% >= {tot_dur * 0.85:.2f}s)"
                        )
                    if is_long and c_sec < tot_dur - 25.0:
                        errors.append(
                            f"CTA_NOT_IN_FINAL_WINDOW: long close CTA starts at {c_sec:.2f}s (must be in final 25s >= {tot_dur - 25.0:.2f}s)"
                        )

                if is_long and mid_at is not None:
                    m_sec = float(mid_at)
                    min_mid = tot_dur * 0.35
                    max_mid = tot_dur * 0.45
                    if not (min_mid <= m_sec <= max_mid):
                        errors.append(
                            f"CTA_MID_NOT_IN_WINDOW: long mid_cta starts at {m_sec:.2f}s (expected 35-45% runtime [{min_mid:.2f}, {max_mid:.2f}]s)"
                        )

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint CTA tone, placements, and constraints.")
    parser.add_argument("target", help="Job directory or brief.json path")
    parser.add_argument("--content", help="Optional explicit path to content.json")
    parser.add_argument("--timings", help="Optional explicit path to timings.json")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    if target_path.is_dir():
        brief_file = target_path / "brief.json"
        content_file = target_path / "content.json"
        timing_file = target_path / "timings.json"
    else:
        brief_file = target_path
        content_file = Path(args.content).resolve() if args.content else target_path.parent / "content.json"
        timing_file = Path(args.timings).resolve() if args.timings else target_path.parent / "timings.json"

    if not brief_file.is_file():
        print(f"Error: Brief file not found at {brief_file}", file=sys.stderr)
        sys.exit(2)
    if not content_file.is_file():
        print(f"Error: Content file not found at {content_file}", file=sys.stderr)
        sys.exit(2)

    brief_data = json.loads(brief_file.read_text(encoding="utf-8"))
    content_data = json.loads(content_file.read_text(encoding="utf-8"))
    timings_data = json.loads(timing_file.read_text(encoding="utf-8")) if timing_file.is_file() else None

    lint_errors = lint_cta(brief_data, content_data, timings=timings_data)
    if lint_errors:
        print(f"FAILED: {len(lint_errors)} CTA tone violation(s) found:")
        for err in lint_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("PASS: CTA tone and placement conform strictly to Video Pilot V2 contracts.")
        sys.exit(0)


if __name__ == "__main__":
    main()
