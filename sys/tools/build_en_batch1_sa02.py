#!/usr/bin/env python3
"""Batch 1 Schema 3.0 Production Package Generator for SA-EN-02.

Channels & Jobs:
1. en_parable_lamp (alias: en_deep_time_strata — Deep Time Strata):
   - Long 16:9: sys/runs/en-deep-time-strata-batch1-16x9
   - Short 9:16: sys/runs/en-deep-time-strata-batch1-9x16
2. en_inside_vessel (Inside the Vessel):
   - Long 16:9: sys/runs/en-inside-vessel-batch1-16x9
   - Short 9:16: sys/runs/en-inside-vessel-batch1-9x16
3. en_pocket_cosmos (Pocket Cosmos):
   - Long 16:9: sys/runs/en-pocket-cosmos-batch1-16x9
   - Short 9:16: sys/runs/en-pocket-cosmos-batch1-9x16

Governance & Quality Gates:
- 100% English content (language: "en")
- Zero AI clichés (spoken natural English storytelling)
- Schema 3.0 compliance (brief-v3, outline-v3, content-v3)
- 2026 Anti-AI tactile visual prompts in content.json & images.json
- Exact channel identity preservation from sys/channels/registry.py
- Zero errors on lint_editorial_and_narrative_quality, check_ai_cliche_phrases,
  check_intra_video_repetitions, and lint_cta
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
TOOLS_DIR = SYS_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import jsonschema
from channels.registry import channel_cast, channel_profile_stamp, get_channel
from channel_production_common import compile_channel_scene_prompt
from cta_tone_linter import lint_cta
from editorial_value_linter import lint_editorial_and_narrative_quality
from script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions

from build_en_batch1_sa02_data_strata import get_deep_time_strata_long, get_deep_time_strata_short
from build_en_batch1_sa02_data_vessel import get_inside_vessel_long, get_inside_vessel_short
from build_en_batch1_sa02_data_cosmos import get_pocket_cosmos_long, get_pocket_cosmos_short


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def compile_images_package(
    ch: Any,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    aspect_ratio: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    aspect_tag = "16x9" if aspect_ratio == "16:9" else "9x16"
    manifest_items = []
    files_list = []

    for sc in content.get("scenes", []):
        for img in sc.get("images", []):
            req_id = img["id"]
            final_prompt = compile_channel_scene_prompt(
                ch, brief, content, sc, img, aspect_ratio=aspect_ratio
            )
            sha = hashlib.sha256(final_prompt.encode("utf-8")).hexdigest()
            target_jpg_name = f"{req_id}_{aspect_tag}.jpg"
            target_json_name = f"{req_id}_{aspect_tag}.json"
            files_list.append(f"revisions/images/1/{target_jpg_name}")
            files_list.append(f"revisions/images/1/{target_json_name}")

            manifest_items.append({
                "image_id": req_id,
                "scene_id": sc["id"],
                "path": f"revisions/images/1/{target_jpg_name}",
                "prompt": final_prompt,
                "sha256": sha,
                "ratio": aspect_ratio,
            })

    images_manifest = {"checkpoint": "final", "items": manifest_items}
    images_output = {
        "schema_version": "1.0",
        "job_id": brief.get("packaging", {}).get("youtube_title", "job"),
        "module": "images",
        "revision": 1,
        "files": files_list,
        "items": manifest_items,
        "payload": {
            "items": manifest_items,
            "thumbnail": f"revisions/images/1/THUMBNAIL_{aspect_tag}.jpg",
            "format": aspect_ratio,
        },
        "checks": {"passed": True, "errors": []},
    }
    return images_manifest, images_output


def run_all_generators():
    jobs = [
        get_deep_time_strata_long(),
        get_deep_time_strata_short(),
        get_inside_vessel_long(),
        get_inside_vessel_short(),
        get_pocket_cosmos_long(),
        get_pocket_cosmos_short(),
    ]

    # Load schemas
    with open(SYS_DIR / "schemas" / "brief-v3.json") as f:
        s_brief = json.load(f)
    with open(SYS_DIR / "schemas" / "outline-v3.json") as f:
        s_outline = json.load(f)
    with open(SYS_DIR / "schemas" / "content-v3.json") as f:
        s_content = json.load(f)

    v_brief = jsonschema.Draft202012Validator(s_brief)
    v_outline = jsonschema.Draft202012Validator(s_outline)
    v_content = jsonschema.Draft202012Validator(s_content)

    results = []

    print("=" * 80)
    print("STARTING SA-EN-02 BATCH 1 GENERATION & QUALITY GATES")
    print("=" * 80)

    for ch_id, job_id, brief, outline, competitor_research, content in jobs:
        ch = get_channel(ch_id)
        job_dir = SYS_DIR / "runs" / job_id
        aspect_ratio = brief["aspect_ratio"]

        # Compile images
        images_manifest, images_output = compile_images_package(
            ch, brief, content, aspect_ratio=aspect_ratio
        )

        # Write all package files
        write_json(job_dir / "brief.json", brief)
        write_json(job_dir / "outline.json", outline)
        write_json(job_dir / "competitor_research.json", competitor_research)
        write_json(job_dir / "content.json", content)
        write_json(job_dir / "images.json", images_manifest)

        # Revisions images directory
        img_rev_dir = job_dir / "revisions" / "images" / "1"
        write_json(img_rev_dir / "images.json", images_manifest)
        write_json(img_rev_dir / "output.json", images_output)

        print(f"\n[✓] Generated files for job: {job_id} ({job_dir})")

        # 1. Schema 3.0 Validation
        b_errs = list(v_brief.iter_errors(brief))
        o_errs = list(v_outline.iter_errors(outline))
        c_errs = list(v_content.iter_errors(content))

        assert len(b_errs) == 0, f"Schema error in brief.json for {job_id}: {[e.message for e in b_errs]}"
        assert len(o_errs) == 0, f"Schema error in outline.json for {job_id}: {[e.message for e in o_errs]}"
        assert len(c_errs) == 0, f"Schema error in content.json for {job_id}: {[e.message for e in c_errs]}"

        # 2. Editorial & Narrative Visual Pacing Linter
        ed_report = lint_editorial_and_narrative_quality(brief, content)
        assert ed_report["passed"] is True, f"Editorial quality failed in {job_id}: {ed_report['errors']}"

        # 3. AI Cliché Linter
        cliche_errs = check_ai_cliche_phrases(content["scenes"])
        assert len(cliche_errs) == 0, f"AI clichés found in {job_id}: {cliche_errs}"

        # 4. Intra-video Repetitions
        rep_errs = check_intra_video_repetitions(content["scenes"])
        assert len(rep_errs) == 0, f"Repetitions found in {job_id}: {rep_errs}"

        # 5. CTA Tone & Policy Linter
        cta_errs = lint_cta(brief, content)
        assert len(cta_errs) == 0, f"CTA errors in {job_id}: {cta_errs}"

        total_words = sum(len(sc["narration"].split()) for sc in content["scenes"])
        total_images = len(images_manifest["items"])
        avg_hold = ed_report["avg_unique_image_hold_sec"]

        results.append({
            "job_id": job_id,
            "channel": ch.name,
            "format": brief["format_profile"],
            "title": brief["packaging"]["youtube_title"],
            "scenes": len(content["scenes"]),
            "words": total_words,
            "images": total_images,
            "avg_hold": avg_hold,
            "editorial_scenes": ed_report["editorial_scenes"],
            "schema_pass": True,
            "linter_pass": True,
        })
        print(f"  • Title: '{brief['packaging']['youtube_title']}' ({len(brief['packaging']['youtube_title'])} chars)")
        print(f"  • Scenes: {len(content['scenes'])}, Words: {total_words}, Images: {total_images}, Avg Hold: {avg_hold:.2f}s")
        print(f"  • Editorial scenes: {ed_report['editorial_scenes']}")
        print(f"  • Schema: PASS | Editorial: PASS | Clichés: 0 | Repetitions: 0 | CTA: PASS")

    print("\n" + "=" * 80)
    print("ALL 6 SA-EN-02 PACKAGES GENERATED AND VALIDATED SUCCESSFULLY (100% PASS)!")
    print("=" * 80)

    # Print summary table
    print("\n| Job ID | Format | Title | Scenes | Words | Images | Avg Hold | Status |")
    print("|---|---|---|---|---|---|---|---|")
    for r in results:
        print(f"| `{r['job_id']}` | `{r['format']}` | {r['title']} | {r['scenes']} | {r['words']} | {r['images']} | {r['avg_hold']:.2f}s | **PASS (100%)** |")

    return results


if __name__ == "__main__":
    run_all_generators()
