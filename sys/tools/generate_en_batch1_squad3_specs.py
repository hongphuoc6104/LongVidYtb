#!/usr/bin/env python3
"""Batch 1 Spec Generator for Squad 3 (Channels 07–09).

Channels:
7. en-fine-print (LegalEagle / CNBC Make It | en-US-RogerNeural)
   - en-fine-print_long_16x9.json, en-fine-print_short_9x16.json
8. en-crowd-strings (Fern / Academy of Ideas | en-US-SteffanNeural)
   - en-crowd-strings_long_16x9.json, en-crowd-strings_short_9x16.json
9. en-cold-case-ink (LEMMiNO | en-GB-RyanNeural)
   - en-cold-case-ink_long_16x9.json, en-cold-case-ink_short_9x16.json

Enforces:
- 64 shots per 16:9 Long video organized into 8 chapters (ch1_hook .. ch8_resolution)
- 20 to 23 words per shot for 16:9 (~1,290 - 1,420 total words)
- pause_after_sec 0.32-0.48 (0.55 at chapter boundaries)
- 7 shots per 9:16 Short video (13 to 15 words per shot, ~95-102 total words)
- parent_long_id linkage and bridge CTA
- Concrete, tactile, non-repetitive visual prompts matching channel StyleDNA
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from sys.tools.squad3_data_fine_print import build_fine_print_long, build_fine_print_short
from sys.tools.squad3_data_crowd_strings import build_crowd_strings_long, build_crowd_strings_short
from sys.tools.squad3_data_cold_case_ink import build_cold_case_ink_long, build_cold_case_ink_short


def count_words(text: str) -> int:
    return len(text.strip().split())


def validate_shots(shots: List[Dict[str, Any]], is_long: bool, channel_slug: str):
    if is_long:
        assert len(shots) == 64, f"[{channel_slug}] Expected 64 shots, got {len(shots)}"
        total_w = sum(count_words(s["narration"]) for s in shots)
        for i, s in enumerate(shots):
            w = count_words(s["narration"])
            assert 20 <= w <= 23, f"[{channel_slug}] Shot S{i+1:02d} has {w} words (must be 20-23): '{s['narration']}'"
            assert "start_visual" in s and s["start_visual"], f"[{channel_slug}] S{i+1:02d} missing start_visual"
            assert "end_visual" in s and s["end_visual"], f"[{channel_slug}] S{i+1:02d} missing end_visual"
            assert "subject_motion" in s and s["subject_motion"], f"[{channel_slug}] S{i+1:02d} missing subject_motion"
            assert "camera_verb" in s and s["camera_verb"], f"[{channel_slug}] S{i+1:02d} missing camera_verb"
            assert "scene_anchor" in s and s["scene_anchor"], f"[{channel_slug}] S{i+1:02d} missing scene_anchor"
            # check continues_prev
            if i % 4 == 0:
                assert s["continues_prev"] is False, f"[{channel_slug}] Shot S{i+1:02d} should have continues_prev=False"
            else:
                assert s["continues_prev"] is True, f"[{channel_slug}] Shot S{i+1:02d} should have continues_prev=True"
            # check pause_after_sec
            if i % 8 == 7:
                assert s["pause_after_sec"] == 0.55, f"[{channel_slug}] Shot S{i+1:02d} chapter end should have pause_after_sec=0.55"
            else:
                assert 0.32 <= s["pause_after_sec"] <= 0.48, f"[{channel_slug}] Shot S{i+1:02d} pause_after_sec {s['pause_after_sec']} out of range"
        print(f"[✓] [{channel_slug} Long 16:9] 64 shots validated! Total words: {total_w}")
    else:
        assert len(shots) == 7, f"[{channel_slug}] Expected 7 shots, got {len(shots)}"
        total_w = sum(count_words(s["narration"]) for s in shots)
        for i, s in enumerate(shots):
            w = count_words(s["narration"])
            assert 13 <= w <= 15, f"[{channel_slug}] Shot S{i+1:02d} has {w} words (must be 13-15): '{s['narration']}'"
            assert "start_visual" in s and s["start_visual"], f"[{channel_slug}] S{i+1:02d} missing start_visual"
            assert "end_visual" in s and s["end_visual"], f"[{channel_slug}] S{i+1:02d} missing end_visual"
            assert "subject_motion" in s and s["subject_motion"], f"[{channel_slug}] S{i+1:02d} missing subject_motion"
            assert "camera_verb" in s and s["camera_verb"], f"[{channel_slug}] S{i+1:02d} missing camera_verb"
            assert "scene_anchor" in s and s["scene_anchor"], f"[{channel_slug}] S{i+1:02d} missing scene_anchor"
        print(f"[✓] [{channel_slug} Short 9:16] 7 shots validated! Total words: {total_w}")


def main():
    specs_dir = SYS_DIR / "channels" / "en_batch1_specs"
    specs_dir.mkdir(parents=True, exist_ok=True)

    items = [
        ("en-fine-print_long_16x9.json", build_fine_print_long(), True),
        ("en-fine-print_short_9x16.json", build_fine_print_short(), False),
        ("en-crowd-strings_long_16x9.json", build_crowd_strings_long(), True),
        ("en-crowd-strings_short_9x16.json", build_crowd_strings_short(), False),
        ("en-cold-case-ink_long_16x9.json", build_cold_case_ink_long(), True),
        ("en-cold-case-ink_short_9x16.json", build_cold_case_ink_short(), False),
    ]

    for filename, data, is_long in items:
        ch_slug = data["channel_slug"]
        yt_title = data.get("youtube_title", "")
        assert len(yt_title) <= 55, f"[{ch_slug}] youtube_title too long ({len(yt_title)} chars): '{yt_title}'"
        validate_shots(data["shots"], is_long=is_long, channel_slug=ch_slug)
        out_path = specs_dir / filename
        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[✓] Written: {out_path} ({len(data['shots'])} shots)")


if __name__ == "__main__":
    main()
