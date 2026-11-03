#!/usr/bin/env python3
"""Schema 3.0 English Batch 1 Generator & Validator for SA-EN-04.

Cluster 4: Neuroscience, Attachment Science & First-Principles Thinking
Assigned Channels (6 jobs total):
1. en_lazy_brain (Lazy Brain Lab):
   - Long: sys/runs/en-lazy-brain-batch1-16x9
   - Short: sys/runs/en-lazy-brain-batch1-9x16
2. en_kindred_sketch (Kindred Sketch):
   - Long: sys/runs/en-kindred-sketch-batch1-16x9
   - Short: sys/runs/en-kindred-sketch-batch1-9x16
3. en_first_principles (First Principles Ink):
   - Long: sys/runs/en-first-principles-batch1-16x9
   - Short: sys/runs/en-first-principles-batch1-9x16
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure sys is in PYTHONPATH
SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

TOOLS_DIR = SYS_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from channels.registry import get_channel
from tools.build_en_batch1_first_principles import (
    build_first_principles_long,
    build_first_principles_short,
)
from tools.build_en_batch1_kindred_sketch import (
    build_kindred_sketch_long,
    build_kindred_sketch_short,
)
from tools.build_en_batch1_lazy_brain import (
    build_lazy_brain_long,
    build_lazy_brain_short,
)
from tools.channel_production_common import compile_channel_scene_prompt
from tools.cta_tone_linter import lint_cta
from tools.editorial_value_linter import lint_editorial_and_narrative_quality
from tools.script_diversity_linter import (
    check_ai_cliche_phrases,
    check_intra_video_repetitions,
)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def generate_and_validate_all() -> List[Dict[str, Any]]:
    builders = [
        ("en-lazy-brain-batch1-16x9", build_lazy_brain_long),
        ("en-lazy-brain-batch1-9x16", build_lazy_brain_short),
        ("en-kindred-sketch-batch1-16x9", build_kindred_sketch_long),
        ("en-kindred-sketch-batch1-9x16", build_kindred_sketch_short),
        ("en-first-principles-batch1-16x9", build_first_principles_long),
        ("en-first-principles-batch1-9x16", build_first_principles_short),
    ]

    results = []

    print("=" * 80)
    print("STARTING SA-EN-04 BATCH 1 GENERATION & QUALITY AUDIT (6 JOBS)")
    print("=" * 80)

    for expected_job_id, builder_func in builders:
        print(f"\n[+] Processing: {expected_job_id}...")
        job_id, brief, outline, cr, content = builder_func()
        assert job_id == expected_job_id, f"Mismatched job_id: {job_id} != {expected_job_id}"

        job_dir = SYS_DIR / "runs" / job_id
        aspect = brief.get("aspect_ratio", "16:9")
        aspect_tag = aspect.replace(":", "x")
        channel_id = brief.get("channel_profile", {}).get("id", "")
        ch = get_channel(channel_id) if channel_id else None

        # 1. Compile images.json manifest
        compiled_items = []
        for sc in content.get("scenes", []):
            for img in sc.get("images", []):
                if ch:
                    final_prompt = compile_channel_scene_prompt(
                        ch, brief, content, sc, img, aspect_ratio=aspect
                    )
                else:
                    final_prompt = img.get("description", "")

                sha = hashlib.sha256(final_prompt.encode("utf-8")).hexdigest()
                compiled_items.append({
                    "image_id": img.get("id"),
                    "scene_id": sc.get("id"),
                    "path": f"revisions/images/1/{img.get('id')}_{aspect_tag}.jpg",
                    "prompt": final_prompt,
                    "motion_prompt": img.get("motion_prompt", ""),
                    "sha256": sha,
                    "ratio": aspect,
                })

        images_manifest = {
            "checkpoint": "compiled",
            "total_images": len(compiled_items),
            "items": compiled_items,
        }

        # 2. Write all 5 JSON package files to sys/runs/<job_id>/
        write_json(job_dir / "brief.json", brief)
        write_json(job_dir / "outline.json", outline)
        write_json(job_dir / "competitor_research.json", cr)
        write_json(job_dir / "content.json", content)
        write_json(job_dir / "images.json", images_manifest)

        # 3. Execute quality gates
        ed_report = lint_editorial_and_narrative_quality(brief, content)
        cliche_violations = check_ai_cliche_phrases(content.get("scenes", []))
        repeat_violations = check_intra_video_repetitions(content.get("scenes", []))
        cta_violations = lint_cta(brief, content)

        # Assert strict quality gates
        assert ed_report["passed"], f"[{job_id}] Editorial Linter Failed: {ed_report['errors']}"
        assert len(cliche_violations) == 0, f"[{job_id}] AI Cliche Violations Found: {cliche_violations}"
        assert len(repeat_violations) == 0, f"[{job_id}] Intra-video Repetition Violations: {repeat_violations}"
        assert len(cta_violations) == 0, f"[{job_id}] CTA Linter Violations: {cta_violations}"

        # Calculate metrics
        scenes = content.get("scenes", [])
        total_words = sum(len((sc.get("narration") or "").split()) for sc in scenes)
        est_duration = round(total_words / 3.8, 1)
        num_images = len(compiled_items)
        avg_hold = round(est_duration / max(1, num_images), 2)
        youtube_title = brief.get("packaging", {}).get("youtube_title", brief.get("youtube_title", ""))

        benchmarks = [b["channel_name"] for b in cr.get("competitor_analysis", {}).get("benchmark_channels", [])]

        res = {
            "job_id": job_id,
            "channel_id": channel_id,
            "format_profile": brief.get("format_profile"),
            "aspect_ratio": aspect,
            "youtube_title": youtube_title,
            "title_len": len(youtube_title),
            "scenes_count": len(scenes),
            "total_words": total_words,
            "est_duration_sec": est_duration,
            "images_count": num_images,
            "avg_image_hold_sec": avg_hold,
            "benchmarks": ", ".join(benchmarks),
            "ed_passed": ed_report["passed"],
            "cliches_count": len(cliche_violations),
            "repeats_count": len(repeat_violations),
            "cta_errors_count": len(cta_violations),
        }
        results.append(res)
        print(f"  [✓] Verified: {job_id} | Title: '{youtube_title}' ({len(youtube_title)}c) | {total_words}w, {est_duration}s | {num_images} imgs ({avg_hold}s/img) | LINTERS: ALL GREEN")

    print("\n" + "=" * 80)
    print("ALL 6 SCHEMA 3.0 ENGLISH PACKAGES SUCCESSFULLY BUILT AND VALIDATED!")
    print("=" * 80)

    # Print summary table
    print("\n| Job ID | Title (<=55 chars) | Format | Words | Est. Dur | Images | Avg Hold | Benchmarks | Linters |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in results:
        print(
            f"| `{r['job_id']}` | \"{r['youtube_title']}\" ({r['title_len']}c) | `{r['format_profile']}` | "
            f"{r['total_words']}w | {r['est_duration_sec']}s | {r['images_count']} | {r['avg_image_hold_sec']}s | "
            f"{r['benchmarks']} | ✅ PASS |"
        )
    print("\n")
    return results


if __name__ == "__main__":
    generate_and_validate_all()
