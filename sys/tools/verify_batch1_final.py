"""Final Comprehensive Verification Script for Batch 1 (9 Channels)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

BATCH_1_CHANNELS = [
    "ai_binh_dan",
    "ban_do_quyen_luc",
    "banh_rang",
    "chanh_niem_ke",
    "co_the_ke",
    "dia_com",
    "la_ban_hoc_thuat",
    "loi_sang_soi",
    "luat_doi_thuong",
]

BOILERPLATE_PATTERN = re.compile(
    r"clearly demonstrating the cause-and-effect explanatory mechanism|detailed visual narrative illustration of",
    re.IGNORECASE,
)
BUZZWORD_PATTERN = re.compile(
    r"\b(8k|4k|uhd|ultra\s*hd|hyper-detailed|hyperrealistic|photorealistic|masterpiece)\b",
    re.IGNORECASE,
)


def verify_all():
    results = []
    all_passed = True

    for slug in BATCH_1_CHANNELS:
        channel_dir = Path(f"video/vn_pilot_{slug}_long")
        spec_path = channel_dir / f"{slug}_long_aligned_spec.json"
        stale_spec = channel_dir / f"{slug}_long_305_aligned_spec.json"
        tts_path = channel_dir / "_work_long/tts_metadata.json"
        images_dir = channel_dir / "_work_long/images"

        assert spec_path.exists(), f"Spec missing: {spec_path}"
        assert not stale_spec.exists(), f"Stale 305 spec still exists: {stale_spec}"
        assert tts_path.exists(), f"TTS missing: {tts_path}"

        with open(spec_path, encoding="utf-8") as f:
            spec = json.load(f)
        with open(tts_path, encoding="utf-8") as f:
            tts = json.load(f)

        beats = spec.get("beats", [])
        vstates = spec.get("visual_states", [])
        tts_dur = float(tts["total_duration"])

        # 1. Beat count (70 to 117)
        count = len(beats)
        count_ok = 70 <= count <= 117 and len(vstates) == count

        # 2. 100% Unique Prompts
        prompts = [b.get("prompt", "") for b in beats]
        unique_prompts = len(set(prompts))
        unique_ok = unique_prompts == count

        # 3. 0% Non-ASCII characters
        non_ascii_count = sum(1 for p in prompts if any(ord(c) >= 128 for c in p))
        non_ascii_ok = non_ascii_count == 0

        # 4. 0% Boilerplate & Buzzwords
        boilerplate_count = sum(1 for p in prompts if BOILERPLATE_PATTERN.search(p))
        buzzword_count = sum(1 for p in prompts if BUZZWORD_PATTERN.search(p))
        clean_prompts_ok = boilerplate_count == 0 and buzzword_count == 0

        # 5. Audio Duration Alignment (<0.05s)
        total_dur = sum(float(b["duration"]) for b in beats)
        dur_diff = abs(total_dur - tts_dur)
        dur_ok = dur_diff < 0.05

        # Check timestamp monotonicity
        at_ok = True
        curr_t = 0.0
        for b in beats:
            if abs(b["at"] - curr_t) > 0.01:
                at_ok = False
                break
            curr_t += b["duration"]

        # 6. Transitions & Camera Motion
        transitions = set(b.get("transition") for b in beats)
        trans_ok = transitions == {"fade"}
        motions = set(b.get("camera_motion") for b in beats)
        motions_valid = all(
            m in ["push_in", "zoom_in", "pan_right", "pan_left"] for m in motions
        )

        # 7. Images directory empty (cleaned for clean regeneration)
        img_count = len(os.listdir(images_dir)) if images_dir.exists() else 0
        img_ok = img_count == 0

        # 8. All based_on are None
        based_on_none = all(b.get("based_on") is None for b in beats)

        ch_ok = (
            count_ok
            and unique_ok
            and non_ascii_ok
            and clean_prompts_ok
            and dur_ok
            and at_ok
            and trans_ok
            and motions_valid
            and img_ok
            and based_on_none
        )
        if not ch_ok:
            all_passed = False
            print(
                f"FAILED {slug}: count={count_ok}, unique={unique_ok}, non_ascii={non_ascii_ok}, "
                f"clean={clean_prompts_ok}, dur={dur_ok}, at={at_ok}, trans={trans_ok}, "
                f"motions={motions_valid}, img={img_ok}, based_on={based_on_none}"
            )

        results.append(
            {
                "slug": slug,
                "count": count,
                "unique": unique_prompts,
                "total_dur": round(total_dur, 4),
                "tts_dur": round(tts_dur, 4),
                "dur_diff": round(dur_diff, 6),
                "non_ascii": non_ascii_count,
                "boilerplate": boilerplate_count,
                "buzzwords": buzzword_count,
                "img_count": img_count,
                "status": "PASS" if ch_ok else "FAIL",
            }
        )

    col_fmt = "{:<18} | {:<5} | {:<9} | {:<10} | {:<10} | {:<8} | {:<7} | {:<6} | {:<6}"
    header = col_fmt.format(
        "Channel Slug",
        "Beats",
        "Unique",
        "Spec Dur",
        "TTS Dur",
        "Diff(s)",
        "NonAsc",
        "Images",
        "Status",
    )
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            col_fmt.format(
                r["slug"],
                r["count"],
                f"{r['unique']}/{r['count']}",
                f"{r['total_dur']:.2f}",
                f"{r['tts_dur']:.2f}",
                f"{r['dur_diff']:.6f}",
                r["non_ascii"],
                r["img_count"],
                r["status"],
            )
        )

    print("=" * len(header))
    print(f"OVERALL BATCH 1 STATUS: ALL PASSED = {all_passed}")
    print("=" * len(header))
    return all_passed


if __name__ == "__main__":
    verify_all()
