#!/usr/bin/env python3
"""Batch 1 Spec Generator for Channels 01-03 (en-first-principles, en-scale-and-bone, en-pocket-cosmos).

Generates 6 canonical spec JSONs into sys/channels/en_batch1_specs/:
- 3 Long 16:9 specs (64 shots each, 8 chapters, 20-23 words/shot, >=495s target duration)
- 3 Short 9:16 specs (7 shots each, 13-15 words/shot, 35-45s target duration)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OUT_DIR = Path("sys/channels/en_batch1_specs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHAPTER_NAMES = [
    "ch1_hook",
    "ch2_paradox",
    "ch3_mechanism",
    "ch4_case_study_1",
    "ch5_escalation",
    "ch6_case_study_2",
    "ch7_systemic_shift",
    "ch8_resolution",
]


def validate_shots(shots: list[dict[str, Any]], is_long: bool) -> None:
    expected_nb = 64 if is_long else 7
    if len(shots) != expected_nb:
        raise ValueError(f"Expected {expected_nb} shots, got {len(shots)}")

    total_words = 0
    for idx, s in enumerate(shots):
        words = s["narration"].split()
        nb_w = len(words)
        total_words += nb_w
        if is_long:
            if not (20 <= nb_w <= 23):
                raise ValueError(
                    f"Shot {s['shot_id']} (idx={idx}) has {nb_w} words: '{s['narration']}' (expected 20-23)"
                )
            # Check scene group & continuation rules
            ch_idx = idx // 8
            expected_ch = CHAPTER_NAMES[ch_idx]
            if s["scene_group"] != expected_ch:
                raise ValueError(f"Shot {s['shot_id']} scene_group {s['scene_group']} != {expected_ch}")
            shot_in_group = idx % 4
            expected_cont = shot_in_group != 0
            if s["continues_prev"] != expected_cont:
                raise ValueError(f"Shot {s['shot_id']} continues_prev {s['continues_prev']} != {expected_cont}")
            # Check pause rules
            pause = float(s["pause_after_sec"])
            if (idx + 1) % 8 == 0:
                if pause != 0.55:
                    raise ValueError(f"Shot {s['shot_id']} at chapter end should have pause 0.55s, got {pause}")
            elif (idx + 1) % 4 == 0:
                if not (0.42 <= pause <= 0.48):
                    raise ValueError(f"Shot {s['shot_id']} at scene pivot should have pause 0.42-0.48s, got {pause}")
            else:
                if not (0.32 <= pause <= 0.42):
                    raise ValueError(f"Shot {s['shot_id']} should have pause 0.32-0.42s, got {pause}")
        else:
            if not (13 <= nb_w <= 15):
                raise ValueError(
                    f"Short shot {s['shot_id']} (idx={idx}) has {nb_w} words: '{s['narration']}' (expected 13-15)"
                )
        for key in ["start_visual", "end_visual", "subject_motion", "camera_verb", "scene_anchor"]:
            if not str(s.get(key, "")).strip():
                raise ValueError(f"Shot {s['shot_id']} missing required key '{key}'")

    print(f"Validation PASSED: {len(shots)} shots, total words = {total_words}")


if __name__ == "__main__":
    print("Validator module ready.")
