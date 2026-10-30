#!/usr/bin/env python3
"""Video Pilot — Unified One-Command Channel Production Runner.

Executes unified, one-command production across all 8 Video Pilot channels:
- Auto-detects channel from --channel <id>, sys/channels/active_channel.json, or current git branch.
- Supports formats: short_9x16 (TikTok), long_16x9 (YouTube explainer), and bundle (1 long + spinoff shorts).
- Accepts --topic-title, --hook, or --input-json; defaults to Week 1 topic/hook from WEEK1_BUNDLES.
- Defaults --job-id to <channel-slug>-auto-<format>.
- Supports --mode package-only and full-e2e.
- Automatically applies ChannelProfile: style, tone, channel_profile stamp, channel_cast,
  and fast_short_max_images budget enforcement for TikTok short_9x16.
- Validates production bundle via validate_production_bundle.
- Scores hook retention via score_content_file (script_hook_scorer.py).
- Outputs clear, machine-readable JSON reports.
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.builders import (  # noqa: E402
    WEEK1_LONG_STORIES,
    WEEK1_SHORT_STORIES,
    generate_synthetic_story_for_channel,
)
from channels.registry import (  # noqa: E402
    ChannelProfile,
    channel_cast,
    channel_ids,
    channel_profile_stamp,
    channels,
    get_channel,
)
from content.research_story_architect import (  # noqa: E402
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedTopic,
    build_scenes_from_story_rows,
    compute_brief_hash,
    serialize_brief_json,
    validate_production_bundle,
    write_production_package,
)
from tools.generate_channel_plans import WEEK1_BUNDLES  # noqa: E402
from tools.script_hook_scorer import score_content_file  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_channel")


def resolve_channel(
    channel_arg: Optional[str] = None,
    cwd: Optional[Path] = None,
    system_root: Path = SYS_DIR,
) -> ChannelProfile:
    """Resolve ChannelProfile from explicit parameter, active_channel.json, or current git branch."""
    if channel_arg and channel_arg.strip():
        clean = (
            channel_arg.strip()
            .replace("channel-", "")
            .replace("channel/", "")
            .replace("-", "_")
        )
        return get_channel(clean)

    base = cwd or Path.cwd()
    candidates = [
        base / "sys/channels/active_channel.json",
        base / "channels/active_channel.json",
        base / "active_channel.json",
        system_root / "channels/active_channel.json",
        base.parent / "sys/channels/active_channel.json",
    ]
    for cand in candidates:
        if cand.is_file():
            try:
                data = json.loads(cand.read_text(encoding="utf-8"))
                cid = data.get("channel_id") or data.get("id")
                if cid:
                    clean_cid = str(cid).strip().replace("channel-", "").replace("channel/", "").replace("-", "_")
                    return get_channel(clean_cid)
            except Exception as ex:
                logger.debug(f"Failed to read {cand}: {ex}")

    # Check git branch
    try:
        res = subprocess.run(
            ["git", "-C", str(base), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            branch = res.stdout.strip()
            if branch.startswith("channel/"):
                slug = branch.partition("channel/")[2].replace("-", "_")
                if slug in channels():
                    return get_channel(slug)
    except Exception as ex:
        logger.debug(f"Git branch check failed: {ex}")

    raise ValueError(
        "No --channel provided and sys/channels/active_channel.json was not found. "
        f"Available channels: {channel_ids()}"
    )


def condense_rows_to_budget(
    rows: List[Tuple[str, str]],
    max_images: int,
    fact_text: str = "",
) -> List[Tuple[str, str]]:
    """Condense story rows to fit within fast_short_max_images while preserving hook, claim, and closing."""
    if len(rows) <= max_images:
        return list(rows)

    fact_idx = 1
    if fact_text:
        for i, (sent, _) in enumerate(rows[1:-1], 1):
            if any(w in sent.lower() for w in fact_text.lower().split() if len(w) > 4):
                fact_idx = i
                break

    indices = {0, fact_idx, len(rows) - 1}
    step = max(1, (len(rows) - 2) // max(1, max_images - 2))
    curr = 1
    while len(indices) < max_images and curr < len(rows) - 1:
        indices.add(curr)
        curr += step

    sorted_indices = sorted(indices)
    while len(sorted_indices) > max_images:
        for idx in sorted_indices:
            if idx not in (0, fact_idx, len(rows) - 1):
                sorted_indices.remove(idx)
                break

    return [rows[i] for i in sorted_indices]


def build_channel_topic_bundle(
    ch: ChannelProfile,
    format_profile: str = "short_9x16",
    topic_title: Optional[str] = None,
    hook: Optional[str] = None,
    input_json_data: Optional[Dict[str, Any]] = None,
) -> ResearchedTopic:
    """Build a calibrated ResearchedTopic object strictly adhering to ChannelProfile & contracts."""
    is_short = format_profile == "short_9x16"
    spec = ch.short_spec if is_short else ch.long_spec
    max_images = ch.speed_optimization.fast_short_max_images if ch.speed_optimization else 8

    # 1. Resolve Story Blueprint Source
    story_data: Optional[Dict[str, Any]] = None
    if input_json_data:
        topic_title = topic_title or input_json_data.get("topic_title") or input_json_data.get("topic")
        hook = hook or input_json_data.get("hook")

    if not topic_title:
        if is_short and ch.id in WEEK1_SHORT_STORIES:
            story_data = copy.deepcopy(WEEK1_SHORT_STORIES[ch.id])
        elif not is_short and ch.id in WEEK1_LONG_STORIES:
            story_data = copy.deepcopy(WEEK1_LONG_STORIES[ch.id])

    if story_data:
        chosen_title = story_data["title"]
        yt_title = story_data["youtube_title"]
        text_overlay = story_data["text_overlay"]
        visual_hook = story_data["visual_hook"]
        contrast_pair = story_data["contrast_pair"]
        sources = story_data["sources"]
        rows = list(story_data["rows"])
    else:
        # Fallback to WEEK1_BUNDLES or synthetic generator
        week1_info = WEEK1_BUNDLES.get(ch.id, {})
        if not topic_title:
            if is_short:
                shorts_list = week1_info.get("tiktok_shorts", [])
                chosen_title = str(shorts_list[0][1]) if shorts_list else ch.seed_topics[0]
            else:
                yt_info = week1_info.get("youtube_long", {})
                chosen_title = str(yt_info.get("title", ch.seed_topics[0]))
        else:
            chosen_title = topic_title.strip()

        yt_title = chosen_title if len(chosen_title) <= 55 else chosen_title[:52] + "..."
        text_overlay = ch.name.upper()[:16]
        visual_hook = f"Nhân vật chính của kênh {ch.name} tương tác với chủ đề {chosen_title}"
        contrast_pair = "Nhận thức phổ thông vs. Sự thật khoa học"
        sources, rows = generate_synthetic_story_for_channel(ch, "short_9x16" if is_short else "long_16x9", chosen_title)

    # 2. Apply Custom Hook if supplied
    if hook and hook.strip() and rows:
        rows[0] = (hook.strip(), rows[0][1])

    # 3. Apply fast_short_max_images budget for TikTok short_9x16
    if is_short:
        fact_ref = sources[0]["facts"][0] if sources and sources[0].get("facts") else ""
        rows = condense_rows_to_budget(rows, max_images, fact_text=fact_ref)

    # 4. Build Scenes via build_scenes_from_story_rows
    char_id = "CH01"
    story_tuples = [(chosen_title, f"Flat 2D {ch.visual.label} stage.", rows)]
    scenes = build_scenes_from_story_rows(story_tuples, character_id=char_id)

    # Distribute requirements and claims
    reqs = [{"id": f"R{i:02d}", "text": chosen_title} for i in range(1, len(scenes) + 1)]
    for i, sc in enumerate(scenes):
        sc.requirements = [f"R{i+1:02d}"]
        if sources:
            sc.source_ids = [sources[0]["id"]]
            if sources[0].get("facts"):
                # Claim must quote a sentence present in this scene's narration
                fact_text = sources[0]["facts"][0]
                matching_quote = None
                for row_sent, _ in rows:
                    if row_sent in sc.narration:
                        matching_quote = row_sent
                        break
                if matching_quote:
                    sc.claim_facts = [(matching_quote, sources[0]["id"], fact_text)]

    # Ensure at least one scene carries the claim
    if sources and sources[0].get("facts") and not any(sc.claim_facts for sc in scenes):
        scenes[0].claim_facts = [(rows[0][0], sources[0]["id"], sources[0]["facts"][0])]

    # 5. Build Cast
    characters = [channel_cast(ch.id, char_id)]
    if ch.id == "thuong_cho_kheo":
        characters.append(
            {
                "id": "CH02",
                "name": "Mây",
                "appearance": "Young woman with a round face, shoulder-length black hair with a small clip and dot eyes in simple chibi proportions.",
                "outfit": "Flat blush (#F7C6C7) cardigan, no folds, no shading.",
            }
        )

    # 6. Packaging Specification
    tags = [t.lstrip("#") for t in ch.hashtags]
    seo_kws = tags + [ch.slug, "videopilot", "kienthuc"]

    packaging = PackagingSpec(
        youtube_title=yt_title[:55],
        visual_hook=visual_hook,
        text_overlay=text_overlay,
        contrast_pair=contrast_pair,
        channel_pillar=DEFAULT_CHANNEL_PILLAR,
        funnel_tier="tier_1_broad",
        seo_keywords=seo_kws,
    )

    lo, hi = spec.duration_seconds
    return ResearchedTopic(
        topic=chosen_title,
        audience=ch.audience,
        goal=ch.promise,
        video_type="research_explainer",
        min_duration=float(lo),
        max_duration=float(hi),
        style=ch.visual.style_description,
        aspect_ratio="9:16" if is_short else "16:9",
        format_profile="short_9x16" if is_short else "long_16x9",
        sources=sources,
        required_points=reqs,
        characters=characters,
        scenes=scenes,
        tone=ch.tone,
        language="vi",
        subtitles=True if is_short else False,
        voice=ch.voice,
        speed=1.0 if is_short else ch.speed,
        channel_id=ch.id,
        conversational_facts=True,
        visual_pacing_profile="full_frame_v1",
        packaging=packaging,
    )


def execute_full_e2e_stages(
    output_dir: Path,
    dry_run: bool = False,
    account: str = "account-01",
    session: str = "video-pilot-tts",
) -> Dict[str, Any]:
    """Execute downstream Colab TTS Audio -> Flow CDP Images + Thumbnail -> Colab Remotion MP4 Render."""
    brief_file = output_dir / "brief.json"
    content_file = output_dir / "content.json"
    if not brief_file.is_file() or not content_file.is_file():
        raise FileNotFoundError(f"Missing brief.json or content.json in {output_dir}")

    brief_data = json.loads(brief_file.read_text(encoding="utf-8"))
    content_data = json.loads(content_file.read_text(encoding="utf-8"))

    results: Dict[str, Any] = {
        "audio_tts": {"status": "SKIPPED"},
        "flow_images": {"status": "SKIPPED"},
        "colab_render": {"status": "SKIPPED"},
    }

    # 1. Audio Colab TTS
    if dry_run:
        results["audio_tts"] = {
            "status": "DRY_RUN_PASS",
            "voice": brief_data.get("outputs", [{}])[0].get("voice", "VietNarrator"),
            "scenes": len(content_data.get("scenes", [])),
            "target_lufs": -11.0,
        }
    else:
        try:
            from adapters import config
            from colab_bridge.client import Client
            from colab_bridge.protocol import build_request
            from format_profiles import audio_mastering_for_format, resolve_format_profile
            from narration_pauses import plan_tracks

            from pilot import Pilot

            job_name = output_dir.name
            p = Pilot(str(SYS_DIR))
            scenes, secondary, pause_plan = plan_tracks(brief_data, content_data, {}, "vi")
            cfg = config(p, job_name)
            cfg.update(audio_mastering_for_format(resolve_format_profile(brief_data)))
            cfg["audio_lufs"] = -11.0
            cfg["audio_peak_db"] = -1.0
            cfg["tts_voice"] = brief_data.get("outputs", [{}])[0].get("voice", "VietNarrator")
            cfg["tts_speed"] = brief_data.get("outputs", [{}])[0].get("speed", 1.0)
            cfg.setdefault("colab_tts", {})["job_id"] = job_name
            cfg["colab_tts"]["account"] = account
            cfg["colab_tts"]["session"] = session

            client = Client(SYS_DIR, cfg)
            client.account = account
            client.session = session
            request = build_request(p.root, cfg, scenes, secondary_scenes=secondary, pause_plan=pause_plan, assemble=True)
            audio_out = output_dir / "revisions/audio/1_master"
            audio_out.mkdir(parents=True, exist_ok=True)
            audio_cache = output_dir / "cache/colab-tts"
            audio_cache.mkdir(parents=True, exist_ok=True)
            synth_res = client.synthesize(request, audio_out, audio_cache)
            results["audio_tts"] = {"status": "SUCCESS", "detail": synth_res}
        except Exception as ex:
            results["audio_tts"] = {
                "status": "BLOCKED",
                "error": str(ex),
                "remediation": "Start Colab T4 OmniVoice TTS notebook and ensure Colab accounts.py is configured.",
            }

    # 2. Flow CDP Images & Native Thumbnail
    total_images = sum(len(sc.get("images", [])) for sc in content_data.get("scenes", []))
    if dry_run:
        results["flow_images"] = {
            "status": "DRY_RUN_PASS",
            "images_budget": total_images,
            "native_thumbnail": True,
            "overlay_card": False,
        }
    else:
        try:
            from flow_prompts import compile as compile_flow_prompt

            aspect_ratio = brief_data.get("outputs", [{}])[0].get("aspect_ratio", "9:16")
            compiled_prompts = []
            for sc in content_data.get("scenes", []):
                for img in sc.get("images", []):
                    c = compile_flow_prompt(
                        "NanoBanana2Lite",
                        "scene",
                        {
                            "description": img["description"],
                            "aspect_ratio": aspect_ratio,
                            "allowed_text": img.get("visible_text", []),
                            "shot_type": img.get("shot_type", "full_scene"),
                            "has_character": img.get("has_character", True),
                            "character_free": not img.get("has_character", True),
                        },
                        version="1.7.0",
                    )
                    compiled_prompts.append(c["prompt"])
            results["flow_images"] = {
                "status": "PROMPTS_COMPILED",
                "count": len(compiled_prompts),
                "pool_dispatched": False,
                "remediation": "Launch Google Chrome CDP profiles (ports 9222-9241) to execute image batch.",
            }
        except Exception as ex:
            results["flow_images"] = {"status": "BLOCKED", "error": str(ex)}

    # 3. Colab Remotion MP4 Render
    if dry_run:
        results["colab_render"] = {
            "status": "DRY_RUN_PASS",
            "format": brief_data.get("outputs", [{}])[0].get("aspect_ratio", "9:16"),
            "target": f"video/{output_dir.name}/{output_dir.name}.mp4",
        }
    else:
        results["colab_render"] = {
            "status": "BLOCKED",
            "remediation": "Requires audio WAV artifacts and Flow images before Colab Remotion render.",
        }

    return results


def run_channel(
    channel: Optional[str] = None,
    format: str = "short_9x16",
    topic_title: Optional[str] = None,
    hook: Optional[str] = None,
    input_json: Optional[Path] = None,
    job_id: Optional[str] = None,
    mode: str = "package-only",
    output_dir: Optional[Path] = None,
    allow_active: bool = False,
    dry_run: bool = False,
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute Unified One-Command Channel Production Runner."""
    ch = resolve_channel(channel, cwd=cwd, system_root=SYS_DIR)
    format_profile = format.strip()
    if format_profile not in ("short_9x16", "long_16x9", "bundle"):
        raise ValueError(f"Invalid format '{format_profile}'. Allowed: ['short_9x16', 'long_16x9', 'bundle']")

    actual_format = "long_16x9" if format_profile == "bundle" else format_profile
    include_spinoffs = format_profile == "bundle"

    # Default job_id: <channel-slug>-auto-<format>
    resolved_job_id = job_id or f"{ch.slug}-auto-{format_profile}"
    dest_dir = output_dir or (SYS_DIR / "runs" / resolved_job_id)
    dest_dir.mkdir(parents=True, exist_ok=True)

    input_json_data: Optional[Dict[str, Any]] = None
    if input_json:
        p = Path(input_json)
        if not p.is_file():
            raise FileNotFoundError(f"Input JSON not found: {p}")
        input_json_data = json.loads(p.read_text(encoding="utf-8"))

    # If input_json directly provides an existing brief and content:
    if input_json_data and "brief" in input_json_data and "content" in input_json_data:
        from channels.registry import apply_channel

        brief_dict = apply_channel(input_json_data["brief"], ch.id)
        content_dict = copy.deepcopy(input_json_data["content"])
        content_dict["style"] = brief_dict["style"]
        content_dict["characters"] = [channel_cast(ch.id, "CH01")]
        brief_hash = compute_brief_hash(brief_dict)
        content_dict["brief_hash"] = brief_hash
        content_dict["brief_revision"] = 1

        (dest_dir / "brief.json").write_text(serialize_brief_json(brief_dict), encoding="utf-8")
        (dest_dir / "content.json").write_text(json.dumps(content_dict, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        valid_contracts, contract_errors = validate_production_bundle(
            system_root=SYS_DIR,
            brief_data=brief_dict,
            content_data=content_dict,
        )
        package_res = {
            "valid_contracts": valid_contracts,
            "contract_errors": contract_errors,
            "output_dir": str(dest_dir),
            "brief_hash": brief_hash,
        }
        topic_scenes_count = len(content_dict.get("scenes", []))
        topic_images_count = sum(len(sc.get("images", [])) for sc in content_dict.get("scenes", []))
    else:
        topic = build_channel_topic_bundle(
            ch=ch,
            format_profile=actual_format,
            topic_title=topic_title,
            hook=hook,
            input_json_data=input_json_data,
        )

        package_res = write_production_package(
            output_dir=dest_dir,
            topic=topic,
            system_root=SYS_DIR,
            include_spinoffs=include_spinoffs,
            allow_active=allow_active or True,
        )
        topic_scenes_count = len(topic.scenes)
        topic_images_count = sum(len(sc.visual_beats) for sc in topic.scenes)

    content_path = dest_dir / "content.json"
    hook_score = score_content_file(content_path, ch.id, actual_format)

    report: Dict[str, Any] = {
        "channel_id": ch.id,
        "channel_name": ch.name,
        "job_id": resolved_job_id,
        "format": format_profile,
        "mode": mode,
        "channel_profile": channel_profile_stamp(ch.id),
        "output_dir": str(dest_dir),
        "valid_contracts": package_res.get("valid_contracts", False),
        "contract_errors": package_res.get("contract_errors", []),
        "hook_score": {
            "score": hook_score.score,
            "hook": hook_score.hook,
            "hook_syllables": hook_score.hook_syllables,
            "estimated_seconds": hook_score.estimated_seconds,
            "seconds_per_sentence": hook_score.seconds_per_sentence,
            "checks": hook_score.checks,
            "needs_rewrite": hook_score.needs_rewrite,
            "suggestions": hook_score.suggestions,
        },
        "fast_short_max_images": ch.speed_optimization.fast_short_max_images if ch.speed_optimization else 6,
        "scenes_count": topic_scenes_count,
        "images_count": topic_images_count,
        "spinoff_count": len(package_res.get("spinoff_packages") or []),
        "status": "SUCCESS" if package_res.get("valid_contracts") else "FAILED",
    }

    if mode == "full-e2e":
        downstream = execute_full_e2e_stages(
            output_dir=dest_dir,
            dry_run=dry_run,
        )
        report["downstream"] = downstream

    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Video Pilot — Unified One-Command Channel Production Runner"
    )
    parser.add_argument(
        "--channel",
        choices=channel_ids() + [f"channel-{c}" for c in channel_ids()],
        default=None,
        help="Channel ID (defaults to active_channel.json or current git branch)",
    )
    parser.add_argument(
        "--format",
        choices=["short_9x16", "long_16x9", "bundle"],
        default="short_9x16",
        help="Format profile: short_9x16, long_16x9, or bundle (default: short_9x16)",
    )
    parser.add_argument(
        "--topic-title",
        default=None,
        help="Custom topic title (defaults to Week 1 bundle topic)",
    )
    parser.add_argument(
        "--hook",
        default=None,
        help="Custom opening hook (defaults to Week 1 hook formula)",
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        default=None,
        help="Path to pre-constructed input JSON package or spec",
    )
    parser.add_argument(
        "--job-id",
        default=None,
        help="Job ID (defaults to <channel-slug>-auto-<format>)",
    )
    parser.add_argument(
        "--mode",
        choices=["package-only", "full-e2e"],
        default="package-only",
        help="Execution mode: package-only (default) or full-e2e",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Destination directory for output artifacts",
    )
    parser.add_argument(
        "--allow-active",
        action="store_true",
        default=True,
        help="Allow active job destination directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run for full-e2e downstream stages",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="Output structured JSON report (default: True)",
    )

    args = parser.parse_args(argv)

    try:
        start_time = time.time()
        result = run_channel(
            channel=args.channel,
            format=args.format,
            topic_title=args.topic_title,
            hook=args.hook,
            input_json=args.input_json,
            job_id=args.job_id,
            mode=args.mode,
            output_dir=args.output_dir,
            allow_active=args.allow_active,
            dry_run=args.dry_run,
        )
        result["elapsed_seconds"] = round(time.time() - start_time, 2)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "SUCCESS" else 1
    except Exception as ex:
        err_res = {
            "status": "ERROR",
            "error": str(ex),
        }
        print(json.dumps(err_res, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
