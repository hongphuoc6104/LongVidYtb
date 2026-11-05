#!/usr/bin/env python3
"""Master Batch 3 Script & Storyboard Architect Builder.

Builds and validates complete Batch 3 packages for:
1. nao-luoi-batch3-9x16
2. nao-luoi-batch3-16x9
3. tui-tien-batch3-9x16
4. tui-tien-batch3-16x9
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "sys"))

from tools.build_nao_luoi_batch3 import build_nao_luoi_9x16
from tools.build_nao_luoi_16x9 import build_nao_luoi_16x9
from tools.build_tui_tien_batch3 import build_tui_tien_9x16
from tools.build_tui_tien_16x9 import build_tui_tien_16x9
from tools.cta_tone_linter import lint_cta
from tools.editorial_value_linter import lint_editorial_and_narrative_quality
from tools.script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions


def build_and_validate():
    print("=== Generating Batch 3 Packages ===")
    build_nao_luoi_9x16()
    build_nao_luoi_16x9()
    build_tui_tien_9x16()
    build_tui_tien_16x9()

    print("\n=== Validating All 4 Jobs ===")
    jobs = [
        "nao-luoi-batch3-9x16",
        "nao-luoi-batch3-16x9",
        "tui-tien-batch3-9x16",
        "tui-tien-batch3-16x9",
    ]
    summary = {}
    for j in jobs:
        d = ROOT / "sys" / "runs" / j
        b = json.loads((d / "brief.json").read_text())
        c = json.loads((d / "content.json").read_text())
        r1 = lint_editorial_and_narrative_quality(b, c)
        r2 = check_ai_cliche_phrases(c.get("scenes", []))
        r3 = check_intra_video_repetitions(c.get("scenes", []))
        r4 = lint_cta(b, c)

        total_words = sum(len((sc.get("narration") or "").split()) for sc in c.get("scenes", []))
        num_beats = sum(len(sc.get("beats", [])) for sc in c.get("scenes", []))
        num_images = sum(len(sc.get("images", [])) for sc in c.get("scenes", []))

        summary[j] = {
            "editorial_passed": r1["passed"],
            "errors": r1["errors"],
            "cliche_count": len(r2),
            "repetition_count": len(r3),
            "cta_errors": r4,
            "scenes": len(c.get("scenes", [])),
            "beats": num_beats,
            "unique_images": num_images,
            "total_words": total_words,
            "est_duration_sec": r1.get("estimated_duration_sec"),
            "avg_hold_sec": r1.get("avg_unique_image_hold_sec"),
            "youtube_title": b.get("youtube_title"),
            "youtube_title_len": len(b.get("youtube_title", "")),
        }
        print(f"[{j}] editorial={r1['passed']}, errors={r1['errors']}, cliches={len(r2)}, rep={len(r3)}, cta={r4}")
        assert r1["passed"] and not r2 and not r3 and not r4

    print("\nAll 4 Batch 3 packages validated with 100% compliance!")
    return summary


if __name__ == "__main__":
    res = build_and_validate()
    print("\nSummary metrics:")
    for k, v in res.items():
        print(f"--- {k} ---")
        for sk, sv in v.items():
            print(f"  {sk}: {sv}")
