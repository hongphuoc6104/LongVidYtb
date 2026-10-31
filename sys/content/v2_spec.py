"""V2 Spec parser, validator, and ResearchedTopic converter for Video Pilot.

Implements the V2 CTA, Pacing, and Multi-Visual Beat contracts defined in
v2_contract.md §3.1 / §3.2.
"""

from __future__ import annotations

import re
from dataclasses import asdict
from typing import Any, Dict, List, Tuple

from channels.registry import channel_cast, get_channel

from content.research_story_architect import (
    DEFAULT_CHANNEL_PILLAR,
    PackagingSpec,
    ResearchedScene,
    ResearchedTopic,
    build_scenes_from_story_rows,
)

ALLOWED_TEMPOS: Tuple[str, ...] = ("fast", "normal", "slow", "hold")
ALLOWED_SHOT_TYPES: Tuple[str, ...] = (
    "macro_prop",
    "full_scene",
    "variation",
    "white_card",
    "white_isolated",
    "still_life",
    "environment",
    "concept_metaphor",
    "visual_diagram",
    "cutaway_detail",
    "screen_capture",
)
ALLOWED_FUNNEL_TIERS: Tuple[str, ...] = ("tier_1_broad", "tier_2_mid", "tier_3_conversion")


def count_vietnamese_syllables(text: str) -> int:
    """Count syllables by whitespace tokens per contract §3.4."""
    if not text:
        return 0
    clean = re.sub(r"\[pause:[^\]]+\]", "", text).strip()
    return len([t for t in clean.split() if t])


def visual_has_primary_character(visual: Dict[str, Any]) -> bool:
    """Determine whether a visual specification features the primary character (CH01)."""
    if not visual or not isinstance(visual, dict):
        return False
    if visual.get("character_free") is True or visual.get("has_character") is False:
        return False

    spec_str = str(visual.get("spec", ""))
    shot_part = spec_str.partition("|")[0].strip()

    # Explicit exclusion tags
    if any(k in shot_part for k in (":none", ":no_char", ":character_free", ":empty")):
        return False

    # Explicit CH01 indicator
    if ":CH01" in shot_part or ":CH01" in spec_str:
        return True
    char_ids = visual.get("character_ids")
    if isinstance(char_ids, (list, tuple)) and "CH01" in char_ids:
        return True

    # Check for stickman or character keywords in description or action
    lower_spec = spec_str.lower()
    if any(k in lower_spec for k in ("stickman", "người que", "ch01")):
        return True

    # Standard explainer full_scene or variation defaults to the primary character
    shot_type = shot_part.partition(":")[0].strip()
    if shot_type in ("full_scene", "variation"):
        return True

    return False


def resolve_crop_base_visual(vid: str, visual_map: Dict[str, Dict[str, Any]], max_depth: int = 5) -> Dict[str, Any]:
    """Resolve a crop visual reference back to its originating base visual."""
    curr = visual_map.get(vid)
    depth = 0
    while curr and depth < max_depth:
        s = str(curr.get("spec", ""))
        if s.startswith("crop:"):
            next_id = s.partition(":")[2].strip()
            curr = visual_map.get(next_id)
            depth += 1
        else:
            break
    return curr or {}


def summarize_v2_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate visual beat metrics across all scenes in a v2 spec."""
    total_visuals = 0
    new_flow_images = 0
    variations = 0
    reused_v1 = 0
    crops = 0
    endcards = 0
    emphasis_count = 0
    tempos: Dict[str, int] = {"fast": 0, "normal": 0, "slow": 0, "hold": 0}

    for sc in spec.get("scenes", []):
        for row in sc.get("rows", []):
            visuals = row.get("visuals", [])
            for v in visuals:
                total_visuals += 1
                tempo = v.get("tempo")
                if tempo in tempos:
                    tempos[tempo] += 1
                if v.get("emphasis_text"):
                    emphasis_count += 1
                spec_str = str(v.get("spec", ""))
                if spec_str == "endcard" or v.get("is_endcard"):
                    endcards += 1
                elif spec_str.startswith("crop:"):
                    crops += 1
                elif v.get("reuse_image"):
                    reused_v1 += 1
                elif v.get("based_on") or spec_str.partition("|")[0].partition(":")[0].strip() == "variation":
                    variations += 1
                else:
                    new_flow_images += 1

    ratio = round(emphasis_count / total_visuals, 3) if total_visuals else 0.0
    return {
        "total_visuals": total_visuals,
        "new_flow_images": new_flow_images,
        "variations": variations,
        "reused_v1": reused_v1,
        "crops": crops,
        "endcards": endcards,
        "emphasis_count": emphasis_count,
        "emphasis_ratio": ratio,
        "tempo_counts": tempos,
    }


def validate_v2_spec(spec: Dict[str, Any], channel_id: str) -> List[str]:
    """Validate a v2 spec dict against contract §3.1/§3.2/§3.4 rules.

    Returns a list of error strings. Empty list indicates full validity.
    """
    errors: List[str] = []

    # 1. Channel check
    try:
        get_channel(channel_id)
    except Exception as ex:
        errors.append(f"UNKNOWN_CHANNEL: Channel '{channel_id}' not found: {ex}")
        return errors

    # 2. Top-level metadata
    job_id = spec.get("job_id", "")
    if not job_id or not isinstance(job_id, str):
        errors.append("MISSING_JOB_ID: spec must contain a non-empty string 'job_id'")

    format_profile = spec.get("format_profile", "")
    if format_profile not in ("short_9x16", "long_16x9"):
        errors.append(f"INVALID_FORMAT_PROFILE: '{format_profile}' must be 'short_9x16' or 'long_16x9'")

    if format_profile == "short_9x16":
        parent_long_id = spec.get("parent_long_id")
        if not parent_long_id or not isinstance(parent_long_id, str):
            errors.append("MISSING_PARENT_LONG_ID: short_9x16 spec must declare 'parent_long_id'")

    if not spec.get("topic") or not isinstance(spec.get("topic"), str):
        errors.append("MISSING_TOPIC: spec must contain a non-empty string 'topic'")
    if not spec.get("goal") or not isinstance(spec.get("goal"), str):
        errors.append("MISSING_GOAL: spec must contain a non-empty string 'goal'")

    min_dur = spec.get("min_duration")
    max_dur = spec.get("max_duration")
    if min_dur is not None and max_dur is not None:
        if not (isinstance(min_dur, (int, float)) and isinstance(max_dur, (int, float)) and 0 < min_dur <= max_dur):
            errors.append(f"INVALID_DURATION_RANGE: min_duration ({min_dur}) must be <= max_duration ({max_dur})")

    # 3. Packaging
    pkg = spec.get("packaging")
    if not isinstance(pkg, dict):
        errors.append("MISSING_PACKAGING: spec must contain a 'packaging' dictionary")
    else:
        yt_title = str(pkg.get("youtube_title", "")).strip()
        if not yt_title:
            errors.append("PACKAGING_MISSING_TITLE: youtube_title must not be empty")
        elif len(yt_title) > 55:
            errors.append(f"PACKAGING_TITLE_TOO_LONG: youtube_title is {len(yt_title)} chars (must be <= 55)")

        v_hook = str(pkg.get("visual_hook", "")).strip()
        if not v_hook:
            errors.append("PACKAGING_MISSING_HOOK: visual_hook must not be empty")

        overlay = str(pkg.get("text_overlay", "")).strip()
        if not overlay:
            errors.append("PACKAGING_MISSING_OVERLAY: text_overlay must not be empty")
        else:
            words = [w for w in re.split(r"\s+", overlay) if w]
            if not (2 <= len(words) <= 5):
                errors.append(f"PACKAGING_OVERLAY_WORD_COUNT: text_overlay '{overlay}' must be 2-4 words")
            alpha = [c for c in overlay if c.isalpha()]
            if alpha and not all(c.isupper() for c in alpha):
                errors.append(f"PACKAGING_OVERLAY_NOT_UPPERCASE: text_overlay '{overlay}' must be uppercase")

        funnel_tier = pkg.get("funnel_tier")
        if funnel_tier and funnel_tier not in ALLOWED_FUNNEL_TIERS:
            errors.append(f"INVALID_FUNNEL_TIER: '{funnel_tier}' must be one of {ALLOWED_FUNNEL_TIERS}")

    # 4. Sources
    sources = spec.get("sources", [])
    if not isinstance(sources, list) or not sources:
        errors.append("MISSING_SOURCES: spec must declare at least one academic/researched source")
    else:
        for s in sources:
            if not s.get("id") or not s.get("title") or not s.get("facts"):
                errors.append(f"INVALID_SOURCE: source {s} missing id, title, or facts")

    # 5. CTA Plan
    cta = spec.get("cta_plan")
    if not isinstance(cta, dict):
        errors.append("MISSING_CTA_PLAN: spec must declare 'cta_plan' dictionary")
    else:
        close_text = str(cta.get("close", "")).strip()
        if not close_text:
            errors.append("CTA_MISSING_CLOSE: cta_plan must declare 'close'")
        else:
            close_syl = count_vietnamese_syllables(close_text)
            if close_syl > 24:
                errors.append(f"CTA_CLOSE_TOO_LONG: close is {close_syl} syllables (max 24)")

        endcard_text = str(cta.get("endcard_text", "")).strip()
        if not endcard_text:
            errors.append("CTA_MISSING_ENDCARD_TEXT: cta_plan must declare 'endcard_text'")
        else:
            words = [w for w in endcard_text.split() if w]
            if len(words) > 6:
                errors.append(f"CTA_ENDCARD_TEXT_TOO_LONG: endcard_text '{endcard_text}' has {len(words)} words (max 6)")
            alpha = [c for c in endcard_text if c.isalpha()]
            if alpha and not all(c.isupper() for c in alpha):
                errors.append(f"CTA_ENDCARD_NOT_UPPERCASE: endcard_text '{endcard_text}' must be UPPERCASE")

        if format_profile == "short_9x16":
            bridge_text = str(cta.get("bridge", "")).strip()
            if not bridge_text:
                errors.append("CTA_MISSING_BRIDGE: short_9x16 cta_plan must declare 'bridge'")
            else:
                bridge_syl = count_vietnamese_syllables(bridge_text)
                if bridge_syl > 22:
                    errors.append(f"CTA_BRIDGE_TOO_LONG: bridge is {bridge_syl} syllables (max 22)")
            if cta.get("mid_cta") is not None:
                errors.append("CTA_SHORT_NO_MID_CTA: short_9x16 must have mid_cta: null")

    # 6. Scenes and Visuals
    scenes = spec.get("scenes", [])
    if not isinstance(scenes, list) or not scenes:
        errors.append("MISSING_SCENES: spec must declare a non-empty 'scenes' list")
        return errors

    seen_vids: Dict[str, Tuple[int, int]] = {}
    ordered_vids: List[str] = []
    total_beats = 0
    emphasis_beats = 0

    for sc_idx, sc in enumerate(scenes, 1):
        sc_title = sc.get("title", f"SC{sc_idx:02d}")
        sc_setting = sc.get("setting", "")
        if not sc_setting:
            errors.append(f"SCENE_MISSING_SETTING: {sc_title} must declare 'setting'")

        rows = sc.get("rows", [])
        if not isinstance(rows, list) or not rows:
            errors.append(f"SCENE_MISSING_ROWS: {sc_title} must declare non-empty 'rows'")
            continue

        for r_idx, row in enumerate(rows, 1):
            narration = row.get("narration", "") if isinstance(row, dict) else (row[0] if isinstance(row, (tuple, list)) else "")
            if not narration or not str(narration).strip():
                errors.append(f"ROW_EMPTY_NARRATION: {sc_title} row {r_idx} narration is empty")

            visuals = row.get("visuals", []) if isinstance(row, dict) else (row[1] if isinstance(row, (tuple, list)) and len(row) > 1 else [])
            if not isinstance(visuals, list) or not visuals:
                errors.append(f"ROW_EMPTY_VISUALS: {sc_title} row {r_idx} visuals list is empty")
                continue

            last_pos = -1
            seen_row_anchors = set()
            for v_idx, v in enumerate(visuals, 1):
                total_beats += 1
                v_id = v.get("id") if isinstance(v, dict) else None
                if not v_id or not isinstance(v_id, str):
                    errors.append(f"VISUAL_MISSING_ID: {sc_title} row {r_idx} visual {v_idx} missing stable 'id'")
                else:
                    if v_id in seen_vids:
                        errors.append(f"DUPLICATE_VISUAL_ID: visual id '{v_id}' duplicated (seen in {seen_vids[v_id]})")
                    seen_vids[v_id] = (sc_idx, r_idx)
                    ordered_vids.append(v_id)

                v_anchor = str(v.get("anchor", "")).strip() if isinstance(v, dict) else ""
                if not v_anchor:
                    errors.append(f"VISUAL_MISSING_ANCHOR: {sc_title} row {r_idx} visual {v_idx} missing anchor")
                else:
                    if v_anchor in seen_row_anchors:
                        errors.append(f"DUPLICATE_ROW_ANCHOR: {sc_title} row {r_idx} anchor '{v_anchor}' duplicated in same row")
                    seen_row_anchors.add(v_anchor)

                    pos = narration.find(v_anchor)
                    if pos == -1:
                        errors.append(f"ANCHOR_NOT_IN_NARRATION: {sc_title} row {r_idx} anchor '{v_anchor}' not found in narration")
                    else:
                        if v_idx == 1 and pos != 0:
                            # First visual should start at beginning of row narration
                            if not narration[:pos].strip() == "":
                                errors.append(f"FIRST_ANCHOR_NOT_START: {sc_title} row {r_idx} first visual anchor must start at beginning of narration")
                        if pos < last_pos:
                            errors.append(f"ANCHORS_OUT_OF_ORDER: {sc_title} row {r_idx} anchor '{v_anchor}' occurs before previous anchor")
                        last_pos = pos

                tempo = v.get("tempo") if isinstance(v, dict) else None
                if tempo not in ALLOWED_TEMPOS:
                    errors.append(f"INVALID_TEMPO: {sc_title} visual {v_id or v_idx} tempo '{tempo}' must be in {ALLOWED_TEMPOS}")

                emp = v.get("emphasis_text") if isinstance(v, dict) else None
                if emp:
                    emphasis_beats += 1
                    emp_words = [w for w in str(emp).split() if w]
                    if not (1 <= len(emp_words) <= 4):
                        errors.append(f"EMPHASIS_TEXT_LENGTH: visual {v_id or v_idx} emphasis '{emp}' must be 1-4 words")
                    alpha = [c for c in str(emp) if c.isalpha()]
                    if alpha and not all(c.isupper() for c in alpha):
                        errors.append(f"EMPHASIS_NOT_UPPERCASE: visual {v_id or v_idx} emphasis '{emp}' must be UPPERCASE")

                spec_str = str(v.get("spec", "")) if isinstance(v, dict) else ""
                based_on = v.get("based_on") if isinstance(v, dict) else None
                focus = v.get("focus") if isinstance(v, dict) else None

                if spec_str.startswith("crop:"):
                    target_vid = spec_str.partition(":")[2].strip()
                    if target_vid not in seen_vids or target_vid == v_id:
                        errors.append(f"CROP_TARGET_NOT_PRIOR: crop beat {v_id} references '{target_vid}' which does not precede it")
                    if not focus or not isinstance(focus, dict) or "x" not in focus or "y" not in focus:
                        errors.append(f"CROP_MISSING_FOCUS: crop beat {v_id} requires focus dict with x and y")
                    elif "scale" in focus:
                        scale_val = float(focus["scale"])
                        if not (1.1 <= scale_val <= 3.0):
                            errors.append(f"CROP_SCALE_OUT_OF_RANGE: crop beat {v_id} scale {scale_val} outside [1.1, 3.0]")

                if based_on:
                    if based_on not in seen_vids or based_on == v_id:
                        errors.append(f"BASED_ON_NOT_PRIOR: visual {v_id} based_on '{based_on}' does not precede it")

    # 7. Final visual must be endcard
    if scenes and scenes[-1].get("rows"):
        last_row = scenes[-1]["rows"][-1]
        last_visuals = last_row.get("visuals", []) if isinstance(last_row, dict) else (last_row[1] if isinstance(last_row, (tuple, list)) else [])
        if last_visuals:
            final_v = last_visuals[-1]
            f_spec = final_v.get("spec") if isinstance(final_v, dict) else ""
            if f_spec != "endcard" and not final_v.get("is_endcard"):
                errors.append("FINAL_VISUAL_NOT_ENDCARD: final visual of last scene must have spec 'endcard'")
            elif final_v.get("tempo") != "hold":
                errors.append(f"ENDCARD_TEMPO_NOT_HOLD: endcard visual must have tempo 'hold', got '{final_v.get('tempo')}'")

    # 8. Verbatim bridge & close check in last scene narration
    if format_profile == "short_9x16" and isinstance(cta, dict) and scenes:
        last_sc_narr = " ".join(
            (r.get("narration", "") if isinstance(r, dict) else r[0])
            for r in scenes[-1].get("rows", [])
        )
        bridge_line = cta.get("bridge", "").strip()
        if bridge_line and bridge_line not in last_sc_narr:
            errors.append(f"CTA_BRIDGE_NOT_IN_LAST_SCENE: cta_plan.bridge '{bridge_line}' must appear verbatim in last scene narration")
        close_line = cta.get("close", "").strip()
        if close_line and close_line not in last_sc_narr:
            errors.append(f"CTA_CLOSE_NOT_IN_LAST_SCENE: cta_plan.close '{close_line}' must appear verbatim in last scene narration")

    # 9. Emphasis text density check (<= 35%)
    if total_beats > 0:
        emp_ratio = emphasis_beats / total_beats
        if emp_ratio > 0.35:
            errors.append(
                f"EMPHASIS_RATIO_EXCEEDED: {emphasis_beats}/{total_beats} ({emp_ratio:.1%}) beats have emphasis_text (max allowed 35%)"
            )

    return errors


def topic_from_v2_spec(spec: Dict[str, Any], channel_id: str) -> ResearchedTopic:
    """Convert a validated V2 spec dict into a production-ready ResearchedTopic."""
    ch = get_channel(channel_id)
    slug = ch.slug
    format_profile = spec.get("format_profile", "short_9x16")
    aspect_ratio = "9:16" if format_profile == "short_9x16" else "16:9"
    suffix = "9x16" if format_profile == "short_9x16" else "16x9"

    # Build story rows per scene
    story_row_scenes = []
    scene_claims_map: Dict[str, List[Any]] = {}
    scene_sources_map: Dict[str, List[str]] = {}

    for idx, sc in enumerate(spec["scenes"], 1):
        sc_id = f"SC{idx:02d}"
        title = sc.get("title", f"Phân cảnh {idx}")
        setting = sc.get("setting", "")
        tone = sc.get("tone") or ch.tone
        phase = sc.get("phase")

        if sc.get("claim_facts"):
            scene_claims_map[sc_id] = list(sc["claim_facts"])
        if sc.get("source_ids"):
            scene_sources_map[sc_id] = list(sc["source_ids"])

        row_tuples = []
        for row in sc.get("rows", []):
            if isinstance(row, dict):
                narration = row.get("narration", "")
                raw_visuals = row.get("visuals", [])
            else:
                narration = row[0]
                raw_visuals = row[1] if len(row) > 1 else []

            processed_visuals = []
            for v in raw_visuals:
                v_copy = dict(v) if isinstance(v, dict) else {"spec": str(v), "anchor": narration}
                spec_str = str(v_copy.get("spec", ""))
                reuse_img = v_copy.get("reuse_image")

                if reuse_img:
                    v_copy["reuse_from"] = f"runs/{slug}-week1-9x16/revisions/images/1/{reuse_img}_{suffix}.jpg"
                elif spec_str == "endcard" or v_copy.get("is_endcard"):
                    v_copy["is_endcard"] = True
                    v_copy["reuse_from"] = f"channels/{ch.id}/assets/endcard_{suffix}.jpg"
                processed_visuals.append(v_copy)

            row_tuples.append((narration, processed_visuals))

        story_row_scenes.append((title, setting, tone, phase, row_tuples))

    built_scenes: List[ResearchedScene] = build_scenes_from_story_rows(
        story_row_scenes,
        character_id="CH01",
        visual_contract="1.7.0",
    )

    # Attach claim_facts, source_ids, and requirements to built scenes
    for sc_i, sc_obj in enumerate(built_scenes, 1):
        if not sc_obj.requirements:
            sc_obj.requirements = [f"R{sc_i:02d}"]
        if sc_obj.scene_id in scene_claims_map:
            sc_obj.claim_facts = scene_claims_map[sc_obj.scene_id]
        if sc_obj.scene_id in scene_sources_map:
            sc_obj.source_ids = scene_sources_map[sc_obj.scene_id]

    pkg_data = spec.get("packaging", {})
    cta_plan = spec.get("cta_plan")
    packaging = PackagingSpec(
        youtube_title=pkg_data.get("youtube_title", spec["topic"][:55]),
        visual_hook=pkg_data.get("visual_hook", spec["topic"][:55]),
        text_overlay=pkg_data.get("text_overlay", "XEM NGAY"),
        contrast_pair=pkg_data.get("contrast_pair", "Học vẹt cơ học vs. Tư duy bản chất Q1"),
        channel_pillar=pkg_data.get("channel_pillar") or DEFAULT_CHANNEL_PILLAR,
        funnel_tier=pkg_data.get("funnel_tier", "tier_1_broad"),
        seo_keywords=pkg_data.get("seo_keywords", list(ch.hashtags)),
        cta_plan=cta_plan,
    )

    required_points = spec.get("required_points") or [
        {"id": f"R{i:02d}", "text": sc.title} for i, sc in enumerate(built_scenes, 1)
    ]

    return ResearchedTopic(
        topic=spec["topic"],
        audience=spec.get("audience") or ch.audience,
        goal=spec["goal"],
        video_type="explainer",
        min_duration=spec.get("min_duration"),
        max_duration=spec.get("max_duration"),
        style=ch.visual.style_description,
        aspect_ratio=aspect_ratio,
        sources=spec.get("sources", []),
        required_points=required_points,
        characters=[channel_cast(ch.id, "CH01")],
        scenes=built_scenes,
        tone=spec.get("tone") or ch.tone,
        voice=ch.voice,
        speed=ch.speed,
        format_profile=format_profile,
        packaging=packaging,
        channel_id=ch.id,
        parent_long_id=spec.get("parent_long_id"),
        cta_plan=cta_plan,
        engagement={
            k: list(v) if isinstance(v, (list, tuple)) else v
            for k, v in asdict(ch.engagement).items()
        } if ch.engagement else None,
        visual_pacing_profile="full_frame_v1",
    )
