#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Video Pilot V3 Batch 2 Production Package Generator & Multi-Linter Validator.

Generates schema-compliant, high-density V3 brief.json and content.json for Batch 2:
- Long explainer (long_16x9, ~85-110 unique Flow images, hold <= 3.5s, editorial_stance, actionable_value)
- Short spin-off (short_9x16, ~18-24 unique Flow images, hold <= 2.5s, cliffhanger funnel, cta bridge)

Runs and asserts all 3 linters PASS (exit code 0):
1. editorial_value_linter.py
2. cta_tone_linter.py
3. script_diversity_linter.py
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
if str(SYS_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(SYS_DIR / "tools"))

from content.research_story_architect import (  # noqa: E402
    PackagingSpec,
    ResearchedTopic,
    build_brief_v3,
    build_content_v3,
    build_scenes_from_story_rows,
    compute_brief_hash,
)
from channels.registry import channel_cast, get_channel  # noqa: E402
from tools.cta_tone_linter import lint_cta  # noqa: E402
from tools.editorial_value_linter import lint_editorial_and_narrative_quality  # noqa: E402
from tools.script_diversity_linter import lint_script  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("batch2_generator")


def _get_cast(channel_id: str) -> Dict[str, Any]:
    ch = get_channel(channel_id)
    cast = channel_cast(channel_id, "CH01")
    if hasattr(ch.visual, "outfit") and ch.visual.outfit:
        cast["outfit"] = ch.visual.outfit
    return cast


def build_channel_long_topic(mod: Any) -> ResearchedTopic:
    ch = get_channel(mod.CHANNEL_ID)
    cast = _get_cast(mod.CHANNEL_ID)

    scenes = build_scenes_from_story_rows(mod.LONG_STORY_ROWS, character_id="CH01")
    for i, sc in enumerate(scenes, 1):
        sc.requirements = [f"R{i:02d}"]
        if i <= len(mod.LONG_SOURCES[0]["facts"]):
            sc.source_ids = ["SRC01"]

    pkg = PackagingSpec(
        youtube_title=mod.LONG_PACKAGING["youtube_title"],
        visual_hook=mod.LONG_PACKAGING["visual_hook"],
        text_overlay=mod.LONG_PACKAGING["text_overlay"],
        contrast_pair=mod.LONG_PACKAGING["contrast_pair"],
        channel_pillar=mod.LONG_PACKAGING["channel_pillar"],
        funnel_tier=mod.LONG_PACKAGING["funnel_tier"],
        seo_keywords=mod.LONG_PACKAGING["seo_keywords"],
        cta_plan=mod.LONG_PACKAGING["cta_plan"],
    )

    req_points = [{"id": f"R{i:02d}", "text": sc.title} for i, sc in enumerate(scenes, 1)]

    return ResearchedTopic(
        topic=mod.LONG_TOPIC,
        audience=mod.LONG_AUDIENCE,
        goal=mod.LONG_GOAL,
        video_type="explainer",
        min_duration=240.0,
        max_duration=360.0,
        style=ch.visual.style_description,
        aspect_ratio="16:9",
        format_profile="long_16x9",
        sources=mod.LONG_SOURCES,
        required_points=req_points,
        characters=[cast],
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=False,
        voice=ch.voice,
        speed=ch.speed,
        packaging=pkg,
        channel_id=mod.CHANNEL_ID,
        cta_plan=mod.LONG_PACKAGING["cta_plan"],
    )


def build_channel_short_topic(mod: Any, parent_long_id: str) -> ResearchedTopic:
    ch = get_channel(mod.CHANNEL_ID)
    cast = _get_cast(mod.CHANNEL_ID)

    scenes = build_scenes_from_story_rows(mod.SHORT_STORY_ROWS, character_id="CH01")
    for i, sc in enumerate(scenes, 1):
        sc.requirements = [f"R{i:02d}"]
        sc.source_ids = ["SRC01"]

    pkg = PackagingSpec(
        youtube_title=mod.SHORT_PACKAGING["youtube_title"],
        visual_hook=mod.SHORT_PACKAGING["visual_hook"],
        text_overlay=mod.SHORT_PACKAGING["text_overlay"],
        contrast_pair=mod.SHORT_PACKAGING["contrast_pair"],
        channel_pillar=mod.SHORT_PACKAGING["channel_pillar"],
        funnel_tier=mod.SHORT_PACKAGING["funnel_tier"],
        seo_keywords=mod.SHORT_PACKAGING["seo_keywords"],
        cta_plan=mod.SHORT_PACKAGING["cta_plan"],
    )

    req_points = [{"id": f"R{i:02d}", "text": sc.title} for i, sc in enumerate(scenes, 1)]

    return ResearchedTopic(
        topic=mod.SHORT_TOPIC,
        audience=mod.SHORT_AUDIENCE,
        goal=mod.SHORT_GOAL,
        video_type="research_guide",
        min_duration=35.0,
        max_duration=55.0,
        style=ch.visual.style_description,
        aspect_ratio="9:16",
        format_profile="short_9x16",
        sources=mod.SHORT_SOURCES,
        required_points=req_points,
        characters=[cast],
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True,
        voice=ch.voice,
        speed=ch.speed,
        packaging=pkg,
        channel_id=mod.CHANNEL_ID,
        parent_long_id=parent_long_id,
        cta_plan=mod.SHORT_PACKAGING["cta_plan"],
    )


def export_and_lint_package(
    topic: ResearchedTopic,
    editorial_stance: Dict[str, str],
    actionable_value: Dict[str, str],
    target_dirs: List[Path],
    parent_long_id: Optional[str] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Export brief.json and content.json to target_dirs and enforce all 3 linters."""
    brief_data = build_brief_v3(topic)
    brief_data["editorial_stance"] = dict(editorial_stance)
    brief_data["actionable_value"] = dict(actionable_value)
    if "packaging" in brief_data and isinstance(brief_data["packaging"], dict):
        brief_data["packaging"]["editorial_stance"] = dict(editorial_stance)
        brief_data["packaging"]["actionable_value"] = dict(actionable_value)

    if parent_long_id:
        brief_data["parent_long_id"] = parent_long_id

    # Compute hash and build content
    brief_hash = compute_brief_hash(brief_data)
    content_data = build_content_v3(topic, brief_data, brief_hash)

    # 1. Run editorial_value_linter
    ed_result = lint_editorial_and_narrative_quality(brief_data, content_data)
    if not ed_result["passed"]:
        logger.error(f"Editorial Value Linter FAILED for {topic.topic}:\n" + json.dumps(ed_result["errors"], indent=2, ensure_ascii=False))
        raise ValueError(f"Editorial Value Linter FAILED: {ed_result['errors']}")

    # 2. Run cta_tone_linter
    cta_errors = lint_cta(brief_data, content_data)
    if cta_errors:
        logger.error(f"CTA Tone Linter FAILED for {topic.topic}:\n" + json.dumps(cta_errors, indent=2, ensure_ascii=False))
        raise ValueError(f"CTA Tone Linter FAILED: {cta_errors}")

    # 3. Run script_diversity_linter
    div_res = lint_script(scenes=content_data.get("scenes", []))
    if div_res.get("status") != "PASS":
        logger.error(f"Script Diversity Linter FAILED for {topic.topic}:\n" + json.dumps(div_res.get("violations", []), indent=2, ensure_ascii=False))
        raise ValueError(f"Script Diversity Linter FAILED: {div_res.get('violations')}")

    # Write files to all target directories
    for t_dir in target_dirs:
        t_dir.mkdir(parents=True, exist_ok=True)
        (t_dir / "brief.json").write_text(json.dumps(brief_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (t_dir / "content.json").write_text(json.dumps(content_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        outline_data = {"outline": content_data.get("outline", [])}
        (t_dir / "outline.json").write_text(json.dumps(outline_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    logger.info(
        f"[✓] PASSED ALL 3 LINTERS: {topic.format_profile} ({len(content_data['scenes'])} scenes, "
        f"{ed_result['unique_images_count']} Flow images, hold: {ed_result['avg_unique_image_hold_sec']}s/img)"
    )
    return brief_data, content_data


def generate_channel_batch2(channel_id: str) -> Dict[str, Any]:
    """Generate both Long and Short Batch 2 packages for a given channel."""
    logger.info(f"\n=======================================================")
    logger.info(f"  GENERATING BATCH 2 FOR CHANNEL: {channel_id}")
    logger.info(f"=======================================================")

    mod_name = f"tools.batch2_data_{channel_id}"
    try:
        mod = importlib.import_module(mod_name)
    except ModuleNotFoundError:
        mod_name = f"batch2_data_{channel_id}"
        mod = importlib.import_module(mod_name)

    ch_slug = mod.CHANNEL_SLUG
    long_job_id = f"{ch_slug}-batch2-16x9"
    short_job_id = f"{ch_slug}-batch2-9x16"

    worktree_runs = Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{ch_slug}/sys/runs")
    core_runs = SYS_DIR / "runs"

    # 1. Long Explainer
    long_dirs = [worktree_runs / long_job_id, core_runs / long_job_id]
    long_topic = build_channel_long_topic(mod)
    long_brief, long_content = export_and_lint_package(
        topic=long_topic,
        editorial_stance=mod.LONG_EDITORIAL_STANCE,
        actionable_value=mod.LONG_ACTIONABLE_VALUE,
        target_dirs=long_dirs,
    )

    # 2. Short Spin-off (linked to parent_long_id)
    short_dirs = [worktree_runs / short_job_id, core_runs / short_job_id]
    short_topic = build_channel_short_topic(mod, parent_long_id=long_job_id)
    short_brief, short_content = export_and_lint_package(
        topic=short_topic,
        editorial_stance=mod.SHORT_EDITORIAL_STANCE,
        actionable_value=mod.SHORT_ACTIONABLE_VALUE,
        target_dirs=short_dirs,
        parent_long_id=long_job_id,
    )

    return {
        "channel_id": channel_id,
        "channel_slug": ch_slug,
        "long_job_id": long_job_id,
        "short_job_id": short_job_id,
        "long_scenes": len(long_content["scenes"]),
        "long_images": sum(len(s["images"]) for s in long_content["scenes"]),
        "short_scenes": len(short_content["scenes"]),
        "short_images": sum(len(s["images"]) for s in short_content["scenes"]),
        "status": "PASS_ALL_3_LINTERS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and lint Video Pilot Batch 2 packages.")
    parser.add_argument("--channel", required=True, help="Channel identifier (e.g. ai_binh_dan, or 'all')")
    args = parser.parse_args()

    if args.channel == "all":
        channels_to_run = [
            "ai_binh_dan",
            "co_the_ke",
            "ho_so_ky_la",
            "nao_luoi",
            "su_ke_lai",
            "thuong_cho_kheo",
            "tui_tien",
            "ua_sao_vay",
        ]
    else:
        channels_to_run = [args.channel]

    results = []
    for ch_id in channels_to_run:
        res = generate_channel_batch2(ch_id)
        results.append(res)

    print("\n" + "=" * 72)
    print("  BATCH 2 SCRIPTING & LINTING AUDIT REPORT")
    print("=" * 72)
    for r in results:
        print(f"[{r['channel_id']}] Long: {r['long_job_id']} ({r['long_scenes']} sc / {r['long_images']} img) | "
              f"Short: {r['short_job_id']} ({r['short_scenes']} sc / {r['short_images']} img) -> {r['status']}")
    print("=" * 72 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
