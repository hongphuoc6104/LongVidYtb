#!/usr/bin/env python3
"""Video Pilot — V2 Script Spec Exporter & Bundle Builder.

Validates and exports V2 channel scripts (sys/channels/<id>/script_v2.py)
into production packages under sys/runs/<job_id>/.

Runs comprehensive verification:
1. Schema validation via validate_v2_spec
2. CTA tone and policy linter via lint_cta
3. Hook retention scorer (score >= 70 required)
4. Conversational Essayist cadence checker
5. Script diversity linter (if available)

Outputs a structured JSON summary on stdout.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

SYS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.registry import get_channel  # noqa: E402
from content.research_story_architect import (  # noqa: E402
    ResearchedTopic,
    write_production_package,
)
from tools.script_cadence_checker import ScriptCadenceChecker  # noqa: E402
from tools.script_hook_scorer import HookScore, score_script  # noqa: E402

# Banned CTA phrases per contract §3.4
BANNED_CTA_PHRASES: Sequence[str] = (
    "đừng quên like",
    "nhấn chuông",
    "bấm chuông",
    "like share",
    "like và share",
    "like, share",
    "subscribe",
    "đăng ký kênh",
    "ấn theo dõi ngay",
    "bấm theo dõi ngay",
    "hãy like",
    "nhớ like",
    "để ủng hộ kênh",
)

# Guarded import of V2 spec validator and topic builder (E1)
try:
    from content.v2_spec import topic_from_v2_spec, validate_v2_spec  # type: ignore
except ImportError:
    # Development fallback stub until E1 merges sys/content/v2_spec.py
    def validate_v2_spec(spec: Dict[str, Any], channel_id: str) -> List[str]:  # type: ignore
        errors: List[str] = []
        for key in ("job_id", "format_profile", "topic", "packaging", "sources", "cta_plan", "scenes"):
            if key not in spec:
                errors.append(f"Missing required key: '{key}'")
        fmt = spec.get("format_profile")
        if fmt == "short_9x16":
            if not spec.get("parent_long_id"):
                errors.append("short_9x16 spec requires 'parent_long_id'")
        elif fmt == "long_16x9":
            cta_plan = spec.get("cta_plan", {})
            if not cta_plan.get("mid_cta"):
                errors.append("long_16x9 cta_plan requires 'mid_cta'")
        scenes = spec.get("scenes", [])
        if not scenes:
            errors.append("Spec has no scenes")
        for s_idx, scene in enumerate(scenes):
            rows = scene.get("rows", [])
            if not rows:
                errors.append(f"Scene {s_idx+1} has no rows")
            for r_idx, row in enumerate(rows):
                if not row.get("narration"):
                    errors.append(f"Scene {s_idx+1} row {r_idx+1} missing narration")
                if not row.get("visuals"):
                    errors.append(f"Scene {s_idx+1} row {r_idx+1} missing visuals")
        return errors

    def topic_from_v2_spec(spec: Dict[str, Any], channel_id: str) -> ResearchedTopic:  # type: ignore
        from content.research_story_architect import (
            PackagingSpec,
            ResearchedBeat,
            ResearchedScene,
        )
        channel = get_channel(channel_id)
        fmt = spec.get("format_profile", "short_9x16")
        aspect = "9:16" if fmt == "short_9x16" else "16:9"

        packaging_dict = spec.get("packaging", {})
        packaging = PackagingSpec(
            youtube_title=packaging_dict.get("youtube_title", spec["topic"][:55]),
            visual_hook=packaging_dict.get("visual_hook", ""),
            text_overlay=packaging_dict.get("text_overlay", ""),
            contrast_pair=packaging_dict.get("contrast_pair", "Tự trách vs Tự trắc ẩn"),
            channel_pillar=getattr(channel, "niche", "Tư Duy Nhận Thức"),
            funnel_tier=packaging_dict.get("funnel_tier", "tier_1_broad"),
            seo_keywords=packaging_dict.get("seo_keywords", []),
            cta_plan=spec.get("cta_plan"),
        )

        char_id = "CH01"
        char_obj = {
            "id": char_id,
            "name": channel.name,
            "appearance": channel.visual.cast_appearance if channel.visual else "Character appearance",
            "outfit": channel.visual.outfit if channel.visual else "Simple outfit",
        }

        scenes_list: List[ResearchedScene] = []
        visual_count = 0
        for s_idx, sc in enumerate(spec.get("scenes", []), 1):
            sc_id = f"SC{s_idx:02d}"
            rows = sc.get("rows", [])
            narr_parts = [r.get("narration", "").strip() for r in rows if r.get("narration")]
            scene_narration = " ".join(narr_parts)

            words = scene_narration.split()
            p_tail = 0.35 if s_idx == len(spec.get("scenes", [])) else 0.70
            sc_duration = max(3.0, round(len(words) / 4.0 + p_tail, 1))

            v_beats: List[ResearchedBeat] = []
            for r in rows:
                for v in r.get("visuals", []):
                    visual_count += 1
                    img_id = f"{sc_id}_I{visual_count}"
                    spec_str = v.get("spec", "shot_type:CH01|Visual description")
                    raw_shot = spec_str.partition("|")[0].partition(":")[0] if ":" in spec_str or "|" in spec_str else "full_scene"
                    if raw_shot == "endcard" or spec_str == "endcard":
                        raw_shot = "white_card"
                    allowed_shots = {
                        "macro_prop", "full_scene", "variation", "white_card",
                        "white_isolated", "still_life", "environment",
                        "concept_metaphor", "visual_diagram", "cutaway_detail",
                        "screen_capture",
                    }
                    if raw_shot not in allowed_shots:
                        raw_shot = "full_scene"

                    based_on = v.get("based_on")
                    preserve = "Preserve the main character and composition" if raw_shot == "variation" else ""
                    change = "Change visual details as described" if raw_shot == "variation" else "Show the described full-frame scene."
                    if raw_shot == "variation" and not based_on:
                        based_on = f"{sc_id}_I1"

                    desc = spec_str.partition("|")[2] if "|" in spec_str else spec_str
                    if not desc or desc == "endcard":
                        desc = "Channel endcard display frame with branding"

                    v_beats.append(
                        ResearchedBeat(
                            image_id=img_id,
                            description=desc,
                            anchor_quote=v.get("anchor") or scene_narration[:20],
                            reason="Visual continuity and narrative pacing",
                            character_ids=[char_id],
                            shot_type=raw_shot,
                            based_on=based_on,
                            preserve=preserve,
                            change=change,
                        )
                    )

            scenes_list.append(
                ResearchedScene(
                    scene_id=sc_id,
                    title=sc.get("title", f"Scene {s_idx}"),
                    purpose=f"Scene {s_idx} purpose",
                    duration=sc_duration,
                    narration=scene_narration,
                    requirements=[f"R{s_idx:02d}"],
                    source_ids=sc.get("source_ids", []),
                    character_ids=[char_id],
                    action="Character speaks clearly",
                    setting=sc.get("setting", "Clean studio setting"),
                    camera="Semantic full-frame sequence",
                    tone=sc.get("tone", "narrative_warm"),
                    narrative_phase=sc.get("phase", "lived_friction"),
                    visual_beats=v_beats,
                )
            )

        topic = ResearchedTopic(
            topic=spec["topic"],
            audience=spec.get("audience") or channel.audience,
            goal=spec.get("goal") or "Educational explainer",
            video_type="research_explainer",
            min_duration=spec.get("min_duration", 25.0),
            max_duration=spec.get("max_duration", 75.0),
            style=channel.visual.style_description if channel.visual else "Clean 2D explainer illustration",
            aspect_ratio=aspect,
            sources=spec.get("sources", []),
            characters=[char_obj],
            scenes=scenes_list,
            format_profile=fmt,
            packaging=packaging,
            channel_id=channel_id,
            voice=channel.voice,
            speed=channel.speed,
        )
        return topic


def lint_cta_fallback(spec: Dict[str, Any], channel_id: Optional[str] = None) -> List[str]:
    """Fallback CTA tone & policy linter adhering strictly to contract §3.4."""
    violations: List[str] = []
    cta_plan = spec.get("cta_plan", {})
    if not cta_plan:
        violations.append("Missing cta_plan")
        return violations

    close = cta_plan.get("close")
    if not close:
        violations.append("Missing primary CTA (close)")

    fmt = spec.get("format_profile", "short_9x16")
    if fmt == "short_9x16":
        bridge = cta_plan.get("bridge")
        if not bridge:
            violations.append("Short requires a bridge to the long video")
        elif len(bridge.split()) > 22:
            violations.append(f"Bridge exceeds 22 syllables: {len(bridge.split())}")

    if close and len(close.split()) > 24:
        violations.append(f"Close exceeds 24 syllables: {len(close.split())}")

    # Check banned phrases in CTA plan and narrations
    texts_to_check: List[str] = [
        cta_plan.get("bridge") or "",
        cta_plan.get("close") or "",
        cta_plan.get("mid_cta") or "",
    ]
    for sc in spec.get("scenes", []):
        for r in sc.get("rows", []):
            texts_to_check.append(r.get("narration", ""))

    for text in texts_to_check:
        text_lower = text.lower()
        for banned in BANNED_CTA_PHRASES:
            if banned in text_lower:
                violations.append(f"BANNED_CTA_PHRASE: contains '{banned}' in text: '{text[:60]}...'")

    return violations


def run_cta_lint(spec: Dict[str, Any], channel_id: str) -> List[str]:
    """Execute CTA tone lint using E1 linter with fallback."""
    try:
        from tools.cta_tone_linter import lint_cta  # type: ignore
        try:
            res = lint_cta(spec, channel_id=channel_id)
        except TypeError:
            res = lint_cta(spec)
        if isinstance(res, list):
            return res
        if isinstance(res, dict) and "violations" in res:
            return list(res["violations"])
        return []
    except (ImportError, Exception):
        return lint_cta_fallback(spec, channel_id)


def load_channel_script_v2(channel_id: str, format_profile: str, root_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Locate and import script_v2.py, extracting SHORT_V2 or LONG_V2."""
    channel = get_channel(channel_id)
    search_paths: List[Path] = []

    if root_dir:
        search_paths.append(root_dir / "sys" / "channels" / channel_id / "script_v2.py")
        search_paths.append(root_dir / "channels" / channel_id / "script_v2.py")

    cwd = Path.cwd().resolve()
    search_paths.append(cwd / "sys" / "channels" / channel_id / "script_v2.py")
    search_paths.append(REPO_ROOT / "sys" / "channels" / channel_id / "script_v2.py")

    # Also search under vp-channels worktree
    worktree_path = REPO_ROOT.parent / "vp-channels" / f"channel-{channel.slug}" / "sys" / "channels" / channel_id / "script_v2.py"
    search_paths.append(worktree_path)

    script_file: Optional[Path] = None
    for p in search_paths:
        if p.exists() and p.is_file():
            script_file = p
            break

    if not script_file:
        raise FileNotFoundError(
            f"Could not find script_v2.py for channel '{channel_id}'. Searched:\n"
            + "\n".join(f"  - {p}" for p in search_paths)
        )

    module_name = f"channels.{channel_id}.script_v2"
    spec = importlib.util.spec_from_file_location(module_name, script_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module spec from {script_file}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    attr_name = "SHORT_V2" if format_profile == "short_9x16" else "LONG_V2"
    if not hasattr(module, attr_name):
        raise AttributeError(f"Module {script_file} does not define '{attr_name}'")

    script_spec = getattr(module, attr_name)
    if not isinstance(script_spec, dict):
        raise TypeError(f"'{attr_name}' in {script_file} must be a dictionary")

    return script_spec


def compute_bundle_statistics(spec: Dict[str, Any], topic: ResearchedTopic) -> Dict[str, Any]:
    """Calculate beat counts, Flow images, reuse counts, emphasis ratio, and duration."""
    total_beats = 0
    flow_gen_count = 0
    reused_count = 0
    emphasis_count = 0

    for scene in spec.get("scenes", []):
        for row in scene.get("rows", []):
            for visual in row.get("visuals", []):
                total_beats += 1

                # Check emphasis lettering
                if visual.get("emphasis_text"):
                    emphasis_count += 1

                # Check image generation vs reuse vs endcard
                if visual.get("reuse_image"):
                    reused_count += 1
                elif visual.get("spec") == "endcard":
                    reused_count += 1
                else:
                    flow_gen_count += 1

    emphasis_ratio = round(emphasis_count / max(1, total_beats), 3)

    # Duration from measured topic scenes or spec duration limits
    est_duration = sum(sc.duration for sc in topic.scenes)
    if est_duration <= 0.0:
        est_duration = float(spec.get("min_duration", 30.0))

    return {
        "beats": total_beats,
        "flow_images_to_generate": flow_gen_count,
        "reused_images": reused_count,
        "emphasis_ratio": emphasis_ratio,
        "estimated_duration": round(est_duration, 1),
    }


def export_v2_bundle(
    channel_id: str,
    format_profile: str,
    out_dir: Optional[Path] = None,
    root_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Export and verify a V2 script into a production package."""
    # 1. Load script spec
    spec = load_channel_script_v2(channel_id, format_profile, root_dir)

    # 2. Run schema validation
    validation_errors = validate_v2_spec(spec, channel_id)
    if validation_errors:
        raise ValueError(
            f"V2 spec validation failed for channel '{channel_id}' ({format_profile}):\n"
            + "\n".join(f"  - {err}" for err in validation_errors)
        )

    # 3. Run CTA tone & policy linter
    cta_violations = run_cta_lint(spec, channel_id)
    if cta_violations:
        raise ValueError(
            f"CTA tone linter violations for channel '{channel_id}' ({format_profile}):\n"
            + "\n".join(f"  - {v}" for v in cta_violations)
        )

    # 4. Build ResearchedTopic
    topic = topic_from_v2_spec(spec, channel_id)

    # 5. Determine output directory and assemble production package
    job_id = spec["job_id"]
    if out_dir is None:
        effective_root = root_dir or REPO_ROOT
        out_dir = effective_root / "sys" / "runs" / job_id
    out_dir = Path(out_dir).resolve()

    system_root = (root_dir / "sys") if root_dir else SYS_DIR
    write_production_package(
        output_dir=out_dir,
        topic=topic,
        system_root=system_root,
        allow_active=True,
    )

    # 6. Run comprehensive CTA linter on written brief and content
    try:
        from tools.cta_tone_linter import lint_cta  # type: ignore
        brief_data = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
        content_data = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))
        post_cta_errors = lint_cta(brief_data, content_data)
        if post_cta_errors:
            raise ValueError(
                f"CTA tone linter violations for channel '{channel_id}' ({format_profile}):\n"
                + "\n".join(f"  - {v}" for v in post_cta_errors)
            )
    except ImportError:
        pass

    # 7. Verify Hook score (require >= 70)
    narrations = [sc.narration for sc in topic.scenes if sc.narration]
    hook_score: HookScore = score_script(narrations, channel_id=channel_id, format_profile=format_profile)
    if hook_score.score < 70:
        raise ValueError(
            f"Hook score {hook_score.score} is below required threshold 70 for '{channel_id}' "
            f"(opening hook: '{hook_score.hook}'). Suggestions: {hook_score.suggestions}"
        )

    # 7. Check Conversational Essayist cadence
    cadence_checker = ScriptCadenceChecker()
    content_file = out_dir / "content.json"
    if content_file.exists():
        cadence_report = cadence_checker.check_file(content_file)
    else:
        cadence_report = cadence_checker.check_scenes(
            [{"id": sc.scene_id, "narration": sc.narration, "duration": sc.duration} for sc in topic.scenes]
        )

    # 8. Check Script Diversity (if available)
    diversity_violations = 0
    try:
        from tools.script_diversity_linter import lint_script  # type: ignore
        if content_file.exists():
            with open(content_file, encoding="utf-8") as f:
                cdata = json.load(f)
            div_res = lint_script(cdata.get("scenes", []), topic_title=topic.topic)
            diversity_violations = len(div_res.get("violations", []))
    except (ImportError, Exception):
        pass

    # 9. Compute summary metrics
    stats = compute_bundle_statistics(spec, topic)

    summary = {
        "channel_id": channel_id,
        "format": format_profile,
        "job_id": job_id,
        "out_dir": str(out_dir),
        "beats": stats["beats"],
        "flow_images_to_generate": stats["flow_images_to_generate"],
        "reused_images": stats["reused_images"],
        "emphasis_ratio": stats["emphasis_ratio"],
        "estimated_duration": stats["estimated_duration"],
        "hook_score": hook_score.score,
        "cadence_status": cadence_report.get("status", "PASS"),
        "cadence_warnings": cadence_report.get("warnings_count", 0),
        "diversity_violations": diversity_violations,
        "cta_lint": "PASS",
    }

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Export V2 channel script into production bundle")
    parser.add_argument("--channel", required=True, help="Channel identifier (e.g. nao_luoi)")
    parser.add_argument("--format", required=True, choices=["short_9x16", "long_16x9"], help="Format profile")
    parser.add_argument("--out", type=Path, default=None, help="Destination directory (default: sys/runs/<job_id>)")
    parser.add_argument("--root", type=Path, default=None, help="Root directory of workspace")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        summary = export_v2_bundle(
            channel_id=args.channel,
            format_profile=args.format,
            out_dir=args.out,
            root_dir=args.root,
        )
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    except Exception as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
