#!/usr/bin/env python3
"""Main Pipeline Script to Build and Validate Group B Explainer Specs.

Channels:
1. ai_binh_dan (305 beats)
2. la_ban_hoc_thuat (255 beats)
3. luat_doi_thuong (305 beats)
4. nghe_song_sot (305 beats)
5. tui_tien (305 beats)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "sys"))

from tools.explainer_specs.ai_binh_dan import build_ai_binh_dan_spec
from tools.explainer_specs.common import validate_spec
from tools.explainer_specs.la_ban_hoc_thuat import build_la_ban_hoc_thuat_spec
from tools.explainer_specs.luat_doi_thuong import build_luat_doi_thuong_spec
from tools.explainer_specs.nghe_song_sot import build_nghe_song_sot_spec
from tools.explainer_specs.tui_tien import build_tui_tien_spec

CHANNELS = [
    ("ai_binh_dan", build_ai_binh_dan_spec, 305, "video/vn_pilot_ai_binh_dan_long/ai_binh_dan_long_explainer_spec.json"),
    ("la_ban_hoc_thuat", build_la_ban_hoc_thuat_spec, 255, "video/vn_pilot_la_ban_hoc_thuat_long/la_ban_hoc_thuat_long_explainer_spec.json"),
    ("luat_doi_thuong", build_luat_doi_thuong_spec, 305, "video/vn_pilot_luat_doi_thuong_long/luat_doi_thuong_long_explainer_spec.json"),
    ("nghe_song_sot", build_nghe_song_sot_spec, 305, "video/vn_pilot_nghe_song_sot_long/nghe_song_sot_long_explainer_spec.json"),
    ("tui_tien", build_tui_tien_spec, 305, "video/vn_pilot_tui_tien_long/tui_tien_long_explainer_spec.json"),
]


def main():
    print("=" * 80)
    print("BUILDING AND VALIDATING EXPLAINER VISUAL SPECS (GROUP B)")
    print("=" * 80)

    summary_records = []

    for slug, builder_fn, expected_beats, out_rel_path in CHANNELS:
        print(f"\n>>> Processing channel: {slug} (expected {expected_beats} beats)...")
        spec = builder_fn()

        # Validate
        stats = validate_spec(spec, expected_beats)
        print(f"    Validation passed! First 5 types: {stats['first_5_types_ratio']:.1%}, Situational: {stats['situational_ratio']:.1%}")
        print(f"    Reused images: {stats['reused_count']} ({stats['reuse_ratio']:.1%}), New to generate: {stats['new_generation_count']}")
        print(f"    Prompt word counts: min={stats['min_word_count']}, max={stats['max_word_count']}, avg={stats['avg_word_count']}")

        # Save to disk
        out_path = ROOT_DIR / out_rel_path
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        print(f"    Saved: {out_path} ({out_path.stat().st_size:,} bytes)")

        # Record summary
        summary_records.append({
            "slug": slug,
            "total_beats": stats["total_beats"],
            "first_5_ratio": stats["first_5_types_ratio"],
            "situational_ratio": stats["situational_ratio"],
            "reused_count": stats["reused_count"],
            "new_count": stats["new_generation_count"],
            "reuse_ratio": stats["reuse_ratio"],
            "type_distribution": stats["explainer_type_distribution"],
            "sample_beats": spec["beats"][:5],
        })

    print("\n" + "=" * 80)
    print("ALL 5 EXPLAINER SPECS SUCCESSFULLY GENERATED AND VALIDATED!")
    print("=" * 80)

    return summary_records


if __name__ == "__main__":
    main()
