#!/usr/bin/env python3
"""Sanitize visual scene descriptions and image prompts for 6 English packages (12 directories).

Target packages:
1. en-fine-print (16x9, 9x16)
2. en-first-principles (16x9, 9x16)
3. en-inside-vessel (16x9, 9x16)
4. en-kindred-sketch (16x9, 9x16)
5. en-lazy-brain (16x9, 9x16)
6. en-macro-gears (16x9, 9x16)

SSOT Invariants:
- Exactly ONE focal subject doing ONE action
- Flat, quiet, solid background with >=75% negative space (style refs: Kurzgesagt, Vox, Primer, TierZoo)
- Removed: grids, graph paper, schematics, flowcharts, arrows everywhere, dominoes,
  logic trees, calipers, notations, cross-hatching, multiple diagrams, crowded scenes, text overlays
- Allowed: 1-4 uppercase hand-lettered words in upper third if visible_text was present
- Narration, dialogue, timings, anchors, beats, IDs kept 100% untouched
- Back up originals as content.json.bak_cluttered / images.json.bak_cluttered
- Validate JSON loads after edit
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sys.tools.sanitization_data import (
    fine_print,
    first_principles,
    inside_vessel,
    kindred_sketch,
    lazy_brain,
    macro_gears,
)

PACKAGE_MAP = {
    "en-fine-print": {
        "mod": fine_print,
        "profile_id": "ch_en_risograph_law",
    },
    "en-first-principles": {
        "mod": first_principles,
        "profile_id": "ch_en_blueprint_logic",
    },
    "en-inside-vessel": {
        "mod": inside_vessel,
        "profile_id": "ch_en_organ_buddies",
    },
    "en-kindred-sketch": {
        "mod": kindred_sketch,
        "profile_id": "ch_en_pastel_duo",
    },
    "en-lazy-brain": {
        "mod": lazy_brain,
        "profile_id": "ch_en_lazy_brain_doodle",
    },
    "en-macro-gears": {
        "mod": macro_gears,
        "profile_id": "ch_en_swiss_macro",
    },
}


def sanitize_directory(pkg_name: str, ratio: str) -> Dict[str, Any]:
    pkg_info = PACKAGE_MAP[pkg_name]
    mod = pkg_info["mod"]
    profile_id = pkg_info["profile_id"]

    dir_path = Path(f"sys/runs/{pkg_name}-batch1-{ratio}")
    content_file = dir_path / "content.json"
    images_file = dir_path / "images.json"
    rev_images_file = dir_path / "revisions/images/1/images.json"

    # 1. Backups
    content_bak = dir_path / "content.json.bak_cluttered"
    images_bak = dir_path / "images.json.bak_cluttered"
    if not content_bak.exists():
        shutil.copy2(content_file, content_bak)
    if not images_bak.exists():
        shutil.copy2(images_file, images_bak)

    # 2. Load JSON
    with open(content_file, "r", encoding="utf-8") as f:
        content = json.load(f)
    with open(images_file, "r", encoding="utf-8") as f:
        images_manifest = json.load(f)
    with open(images_bak, "r", encoding="utf-8") as f:
        images_bak_manifest = json.load(f)
    bak_items_map = {it["image_id"]: it for it in images_bak_manifest.get("items", [])}

    # Pick appropriate dictionary mappings
    is_16x9 = (ratio == "16x9")
    scene_settings = mod.SCENE_SETTINGS_16X9 if is_16x9 else mod.SCENE_SETTINGS_9X16
    scene_actions = mod.SCENE_ACTIONS_16X9 if is_16x9 else mod.SCENE_ACTIONS_9X16
    descriptions = mod.DESCRIPTIONS_16X9 if is_16x9 else mod.DESCRIPTIONS_9X16

    clean_style = mod.STYLE
    clean_character = mod.CHARACTER

    # 3. Sanitize content.json
    content["style"] = clean_style

    for sc in content.get("scenes", []):
        sid = sc["id"]
        if sid in scene_settings:
            sc["setting"] = scene_settings[sid]
        if sid in scene_actions:
            sc["action"] = scene_actions[sid]

        for im in sc.get("images", []):
            iid = im["id"]
            if iid in descriptions:
                new_desc = descriptions[iid]
                im["description"] = new_desc

                # Clean motion prompt
                im["motion_prompt"] = f"Smooth subtle camera movement focusing on {new_desc[:120]}, silent storytelling, no talking"

                # If variation shot
                if im.get("based_on"):
                    im["preserve"] = "Flat quiet solid background, palette, character silhouette"
                    im["change"] = f"Clean visible focus on {new_desc[:120]}"

    # 4. Sanitize images.json
    orient = "horizontal widescreen" if is_16x9 else "vertical"
    ratio_str = "16:9" if is_16x9 else "9:16"
    s1 = (
        f"Requested aspect ratio: {ratio_str}. Render a complete 100% full-bleed {orient} {ratio_str} "
        "2D illustration extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, "
        "zero UI chrome, and zero dark vignette."
    )
    s2 = f"Visual Style ({profile_id}): {clean_style}"
    s3 = clean_character

    # Build image map from content.json for fast lookup
    content_img_map = {}
    for sc in content.get("scenes", []):
        for im in sc.get("images", []):
            content_img_map[im["id"]] = im

    rewritten_items = 0
    sample_diffs = []

    for item in images_manifest.get("items", []):
        iid = item["image_id"]
        bak_item = bak_items_map.get(iid, {})
        old_prompt = bak_item.get("prompt", item.get("prompt", ""))
        old_motion = bak_item.get("motion_prompt", item.get("motion_prompt", ""))

        c_img = content_img_map.get(iid)
        if not c_img:
            continue

        new_desc = c_img["description"]

        # Variation vs new scene
        if c_img.get("based_on"):
            based_on = c_img["based_on"]
            preserve_txt = c_img.get("preserve", "Flat quiet solid background, palette, character silhouette")
            change_txt = c_img.get("change", f"Clean visible focus on {new_desc[:120]}")
            s4 = (
                f"Variation Shot (based on {based_on}): Maintain continuous visual continuity with the established scene. "
                f"Preserve strictly: {preserve_txt}. Visible change: {change_txt}."
            )
        else:
            s4 = f"Scene Composition & Action: {new_desc}"

        # Text policy
        visible_text = c_img.get("visible_text") or []
        emphasis_text = c_img.get("emphasis_text")
        if emphasis_text:
            s5 = (
                f"Emphasis lettering instruction: render exact uppercase English hand-lettered text in the upper third "
                f"of the frame (strictly <= 10% frame height, 1-4 uppercase words, native hand-lettering integrated directly "
                f"onto the flat canvas, strictly zero rectangular text cards, banners, or gradient overlays covering artwork): \"{emphasis_text}\"."
            )
        elif visible_text:
            text_labels = ", ".join(
                f'"{t}"' if isinstance(t, str) else f'"{t.get("text", "")}"' for t in visible_text
            )
            s5 = f"Render concise uppercase English hand-lettered labels (< 5% frame height) for exact text: {text_labels}."
        else:
            s5 = "Strict zero-text policy: render zero words, letters, numbers, speech bubbles, or watermarks anywhere in the frame."

        new_prompt = f"{s1}\n\n{s2}\n\n{s3}\n\n{s4}\n\n{s5}"
        new_motion = f"Smooth subtle camera movement focusing on {new_desc[:120]}, silent storytelling, no talking"

        item["prompt"] = new_prompt
        item["motion_prompt"] = new_motion
        rewritten_items += 1

        if len(sample_diffs) < 2 and old_prompt != new_prompt:
            sample_diffs.append({
                "image_id": iid,
                "old_prompt": old_prompt,
                "new_prompt": new_prompt,
                "old_desc": c_img.get("description"),
            })

    # 5. Write back to disk
    with open(content_file, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(images_file, "w", encoding="utf-8") as f:
        json.dump(images_manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    if rev_images_file.exists():
        with open(rev_images_file, "w", encoding="utf-8") as f:
            json.dump(images_manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")

    # 6. Validate JSON loads
    with open(content_file, "r", encoding="utf-8") as f:
        json.load(f)
    with open(images_file, "r", encoding="utf-8") as f:
        json.load(f)
    if rev_images_file.exists():
        with open(rev_images_file, "r", encoding="utf-8") as f:
            json.load(f)

    # 7. Invariant verification: Narration and IDs must match backup
    with open(content_bak, "r", encoding="utf-8") as f:
        bak_c = json.load(f)

    assert len(content["scenes"]) == len(bak_c["scenes"])
    for sc_new, sc_bak in zip(content["scenes"], bak_c["scenes"]):
        assert sc_new["id"] == sc_bak["id"]
        assert sc_new["narration"] == sc_bak["narration"]
        assert len(sc_new["images"]) == len(sc_bak["images"])
        assert len(sc_new["beats"]) == len(sc_bak["beats"])
        for b_new, b_bak in zip(sc_new["beats"], sc_bak["beats"]):
            assert b_new["anchor"] == b_bak["anchor"]
            assert b_new["id"] == b_bak["id"]

    return {
        "pkg_name": pkg_name,
        "ratio": ratio,
        "dir": str(dir_path),
        "rewritten_prompts": rewritten_items,
        "sample_diffs": sample_diffs,
    }


def main():
    packages = [
        "en-fine-print",
        "en-first-principles",
        "en-inside-vessel",
        "en-kindred-sketch",
        "en-lazy-brain",
        "en-macro-gears",
    ]

    total_rewritten = 0
    package_reports = {}

    for pkg in packages:
        pkg_rewritten = 0
        samples = []
        for ratio in ["16x9", "9x16"]:
            res = sanitize_directory(pkg, ratio)
            pkg_rewritten += res["rewritten_prompts"]
            if len(samples) < 2 and res["sample_diffs"]:
                samples.extend(res["sample_diffs"][:2 - len(samples)])
        total_rewritten += pkg_rewritten
        package_reports[pkg] = {
            "rewritten_count": pkg_rewritten,
            "samples": samples[:2],
        }

    print("=" * 60)
    print(f"SANITIZATION COMPLETE: {total_rewritten} total prompts rewritten across 12 packages")
    print("=" * 60)

    for pkg, rep in package_reports.items():
        print(f"\nPackage: {pkg}")
        print(f"Total visual prompts rewritten: {rep['rewritten_count']}")
        for idx, s in enumerate(rep["samples"]):
            print(f"\n  --- Example {idx + 1} ({s['image_id']}) ---")
            print(f"  [BEFORE]:\n  {s['old_prompt'][:250]}...")
            print(f"\n  [AFTER]:\n  {s['new_prompt'][:250]}...")


if __name__ == "__main__":
    main()
