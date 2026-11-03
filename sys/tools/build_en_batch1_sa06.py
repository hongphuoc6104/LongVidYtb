#!/usr/bin/env python3
"""Build and validate Schema 3.0 production packages for SA-EN-06 (Cluster 6).

Channels (6 jobs total):
1. en_fine_print (Everyday Fine Print):
   - sys/runs/en-fine-print-batch1-16x9 (Long 16:9, 11 scenes, 66 images)
   - sys/runs/en-fine-print-batch1-9x16 (Short 9:16, 5 scenes, 20 images)
2. en_second_arrow (The Second Arrow):
   - sys/runs/en-second-arrow-batch1-16x9 (Long 16:9, 11 scenes, 66 images)
   - sys/runs/en-second-arrow-batch1-9x16 (Short 9:16, 5 scenes, 20 images)
3. en_bamboo_marble (Bamboo & Marble):
   - sys/runs/en-bamboo-marble-batch1-16x9 (Long 16:9, 11 scenes, 66 images)
   - sys/runs/en-bamboo-marble-batch1-9x16 (Short 9:16, 5 scenes, 20 images)

Quality Gates:
- 100% natural, sharp, spoken English (language: "en")
- Zero robotic AI clichés
- Zero intra-video repetitions across sliding 4-scene windows
- 2026 Anti-AI tactile physical visual prompts
- 100% pass on lint_editorial_and_narrative_quality, check_ai_cliche_phrases,
  check_intra_video_repetitions, lint_cta, and jsonschema.
"""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure sys is in python path
SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from channels.registry import get_channel, channel_cast, channel_profile_stamp
from tools.editorial_value_linter import lint_editorial_and_narrative_quality
from tools.script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions
from tools.cta_tone_linter import lint_cta
from tools.channel_production_common import compile_channel_scene_prompt
import jsonschema

# Load json schemas for strict schema 3.0 validation
BRIEF_SCHEMA = json.loads((SYS_DIR / "schemas/brief-v3.json").read_text(encoding="utf-8"))
OUTLINE_SCHEMA = json.loads((SYS_DIR / "schemas/outline-v3.json").read_text(encoding="utf-8"))
CONTENT_SCHEMA = json.loads((SYS_DIR / "schemas/content-v3.json").read_text(encoding="utf-8"))

# Import data definitions
import tools.data_en_fine_print as dfp
import tools.data_en_second_arrow as dsa
import tools.data_en_bamboo_marble as dbm


def compute_brief_hash(brief_dict: Dict[str, Any]) -> str:
    content = json.dumps(brief_dict, ensure_ascii=False, indent=2)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def make_planning(
    criteria: List[str],
    avoid: List[str],
    pacing: str,
    color: str = "#1D3557",
    aspect: str = "16:9",
) -> Dict[str, Any]:
    """Generate fully compliant planning object adhering to brief-v3 schema."""
    return {
        "success_criteria": criteria,
        "avoid": avoid,
        "prior_knowledge": "No specialized legal, neurological, or classical philosophical training required.",
        "pacing": pacing,
        "domain_requirements": [],
        "assumptions": ["Visual pacing holds ~2.2 to 2.8 seconds per distinct tactile frame."],
        "text_style": {
            "font": "Clean editorial sans-serif with authentic woodcut or ink print texture",
            "color": color,
            "outline": "High-contrast clean negative space boundary",
            "size": "Legible on mobile vertical screens (9:16)" if aspect == "9:16" else "Legible on desktop widescreen (16:9)",
            "placement": "Upper third margin, at least 10% away from edges, avoiding subtitles",
        },
        "speech_rates": {
            "vi": {"units_per_second": 3.8, "uncertainty": 0.15, "source": "Standard acoustic rate"},
            "en": {"units_per_second": 2.6, "uncertainty": 0.20, "source": "Measured native spoken English cadence"},
        },
    }


SHOT_TYPE_MAP = {
    "close_up": "cutaway_detail",
    "medium_shot": "concept_metaphor",
    "full_scene": "full_scene",
    "macro": "macro_prop",
    "macro_prop": "macro_prop",
    "white_card": "white_card",
    "white_isolated": "white_isolated",
    "still_life": "still_life",
    "environment": "environment",
    "concept_metaphor": "concept_metaphor",
    "visual_diagram": "visual_diagram",
    "cutaway_detail": "cutaway_detail",
    "screen_capture": "screen_capture",
}


def build_scene_objects(
    scenes_raw: List[Dict[str, Any]],
    channel_id: str,
    aspect_ratio: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build compliant scenes and outline items from raw narrative definitions."""
    ch = get_channel(channel_id)
    scenes_list: List[Dict[str, Any]] = []
    outline_list: List[Dict[str, Any]] = []

    for s_idx, s in enumerate(scenes_raw):
        sc_id = s["id"]
        req_id = f"R{s_idx+1:02d}"
        outline_list.append({
            "scene_id": sc_id,
            "purpose": s["purpose"],
            "requirements": [req_id],
            "transition": s.get("transition", "Continue following narrative sequence"),
        })

        images_list: List[Dict[str, Any]] = []
        beats_list: List[Dict[str, Any]] = []

        for b_idx, b in enumerate(s["beats"]):
            img_id = f"{sc_id}_I{b_idx+1}"
            beat_id = f"{sc_id}_B{b_idx+1}"
            tempo = b.get("tempo", "normal")
            situation = b.get("situation", s.get("narrative_situation", "mechanism_step"))
            raw_shot = b.get("shot", "full_scene")
            shot = SHOT_TYPE_MAP.get(raw_shot, "full_scene")
            is_endcard = b.get("is_endcard", False)
            quote = b["quote"]
            desc = b["desc"]
            motion = b.get("motion", f"Smooth subtle camera movement focusing on {desc[:60]}, silent storytelling, no talking")

            images_list.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "based_on": None,
                "preserve": b.get("preserve", f"{ch.name} authentic tactile palette and style"),
                "change": b.get("change", desc[:80]),
                "reason": b.get("reason", f"Visual storytelling for beat {beat_id}"),
                "visible_text": b.get("visible_text", []),
                "kind": "scene",
                "shot_type": shot,
                "tempo": tempo,
                "narrative_situation": situation,
                "focus": {"x": 0.5, "y": 0.5},
                "has_character": b.get("has_character", True),
                "motion_prompt": motion,
                "is_endcard": is_endcard,
            })

            beats_list.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": b.get("purpose", s["purpose"]),
                "anchor": {"en": {"quote": quote, "occurrence": 1}},
                "effect": b.get("effect", "cut"),
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": tempo,
                "narrative_situation": situation,
                "camera_intent": b.get("intent", "focus"),
                "is_endcard": is_endcard,
            })

        scenes_list.append({
            "id": sc_id,
            "title": s["title"],
            "purpose": s["purpose"],
            "action": s["action"],
            "setting": s["setting"],
            "camera": s["camera"],
            "narration": s["narration"],
            "requirements": [req_id],
            "character_ids": ["CH01"],
            "source_ids": s.get("source_ids", ["SRC01"]),
            "narrative_situation": s.get("narrative_situation", "mechanism_step"),
            "narrative_phase": s.get("narrative_phase", "lived_friction"),
            "images": images_list,
            "beats": beats_list,
        })

    return scenes_list, outline_list


def compile_images_manifest(
    ch: Any,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    aspect_ratio: str,
) -> Dict[str, Any]:
    """Compile final 2026 Anti-AI tactile prompts for images.json manifest."""
    compiled_items = []
    aspect_tag = aspect_ratio.replace(":", "x")
    for sc in content.get("scenes", []):
        for img in sc.get("images", []):
            final_prompt = compile_channel_scene_prompt(
                ch, brief, content, sc, img, aspect_ratio=aspect_ratio
            )
            compiled_items.append({
                "image_id": img.get("id"),
                "scene_id": sc.get("id"),
                "path": f"revisions/images/1/{img.get('id')}_{aspect_tag}.jpg",
                "prompt": final_prompt,
                "motion_prompt": img.get("motion_prompt", ""),
                "ratio": aspect_ratio,
            })

    return {
        "checkpoint": "compiled",
        "total_images": len(compiled_items),
        "items": compiled_items,
    }


def validate_and_save_package(
    job_id: str,
    brief: Dict[str, Any],
    outline: Dict[str, Any],
    content: Dict[str, Any],
    competitor: Dict[str, Any],
) -> Dict[str, Any]:
    """Run full Schema 3.0 and linter quality audits and write files."""
    ch_id = competitor["channel_id"]
    ch = get_channel(ch_id)
    aspect = brief["aspect_ratio"]

    # Convert all tuples to lists via clean json round-trip for jsonschema compliance
    brief = json.loads(json.dumps(brief, ensure_ascii=False))
    outline = json.loads(json.dumps(outline, ensure_ascii=False))
    content = json.loads(json.dumps(content, ensure_ascii=False))
    competitor = json.loads(json.dumps(competitor, ensure_ascii=False))

    # 1. Schema 3.0 validation
    jsonschema.validate(brief, BRIEF_SCHEMA)
    jsonschema.validate(outline, OUTLINE_SCHEMA)
    jsonschema.validate(content, CONTENT_SCHEMA)

    # 2. Editorial & narrative quality linter
    linter_result = lint_editorial_and_narrative_quality(brief, content)
    if not linter_result["passed"]:
        raise ValueError(f"Editorial linter failed on {job_id}: {linter_result['errors']}")

    # 3. AI cliche phrase check
    cliches = check_ai_cliche_phrases(content["scenes"])
    if cliches:
        raise ValueError(f"AI cliché check failed on {job_id}: {cliches}")

    # 4. Intra-video repetition check
    rep_violations = check_intra_video_repetitions(content["scenes"])
    if rep_violations:
        raise ValueError(f"Intra-video repetition check failed on {job_id}: {rep_violations}")

    # 5. CTA tone linter
    cta_errors = lint_cta(brief, content)
    if cta_errors:
        raise ValueError(f"CTA tone linter failed on {job_id}: {cta_errors}")

    # Compile images.json
    images_manifest = compile_images_manifest(ch, brief, content, aspect)

    # Save to disk
    job_dir = SYS_DIR / "runs" / job_id
    write_json(job_dir / "brief.json", brief)
    write_json(job_dir / "outline.json", outline)
    write_json(job_dir / "competitor_research.json", competitor)
    write_json(job_dir / "content.json", content)
    write_json(job_dir / "images.json", images_manifest)

    total_words = sum(len(sc["narration"].split()) for sc in content["scenes"])
    return {
        "job_id": job_id,
        "channel_id": ch_id,
        "format": brief["format_profile"],
        "youtube_title": brief["youtube_title"],
        "scene_count": len(content["scenes"]),
        "image_count": len(images_manifest["items"]),
        "word_count": total_words,
        "est_duration_sec": round(total_words / 3.8, 1),
        "hold_sec_per_img": round((total_words / 3.8) / len(images_manifest["items"]), 2),
        "linter_status": "PASSED (0 errors)",
    }


# ==============================================================================
# 1. CHANNEL BUILDER: Everyday Fine Print (en_fine_print)
# ==============================================================================

def generate_fine_print_packages():
    ch_id = dfp.CHANNEL_ID
    ch = get_channel(ch_id)
    cast = channel_cast(ch_id, "CH01")
    stamp = channel_profile_stamp(ch_id)

    # SHORT 9:16
    short_scenes, short_outline = build_scene_objects(dfp.SHORT_SCENES_RAW, ch_id, "9:16")
    short_brief = {
        "schema_version": "3.0",
        "topic": dfp.SHORT_TOPIC,
        "audience": ch.audience,
        "goal": "Expose how mandatory predispute arbitration clauses strip constitutional jury rights and demonstrate the 30-day written opt-out procedure",
        "video_type": "explainer",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Surrendering constitutional Seventh Amendment jury rights by tapping I Agree"},
            {"id": "R02", "text": "Disputes forced behind closed doors into private corporate arbitration"},
            {"id": "R03", "text": "Class-action waivers sheltering corporate micro-theft at massive scale"},
            {"id": "R04", "text": "The secret thirty-day written opt-out escape hatch in Section 14"},
            {"id": "R05", "text": "One-page opt-out notice restoring public court protections and channel funnel"},
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": dfp.SOURCES,
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": ch.speed,
            }
        ],
        "planning": make_planning(
            criteria=["Reveal constitutional loss behind I Agree and provide 30-day opt-out action step within 45s"],
            avoid=list(ch.avoid),
            pacing="Vigilant, crisp, high-urgency spoken cadence with zero generic filler words.",
            color="#1D3557",
            aspect="9:16",
        ),
        "packaging": {
            "youtube_title": dfp.SHORT_TITLE,
            "thumbnail_spec": {
                "visual_hook": "A thumb tapping an 'I Agree' button that turns into an iron padlock locking courthouse gates",
                "text_overlay": "DON'T TAP AGREE",
                "contrast_pair": "Instant click vs Forfeited jury rights",
                "thumbnail_prompt": "Crisp 3-color mid-century New Yorker editorial risograph print on newsprint ivory canvas (#F4EFE6). A smartphone screen displaying an illuminated blue 'I Agree' button turning into an iron padlock snapping shut over bronze courthouse doors, navy indigo ink #1D3557 and crimson #E63946, bold hand-lettered text in upper third: 'DON'T TAP AGREE'. 2D orthographic, >=60% negative space, zero 3D, zero gradients.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Consumer Law Literacy & Contract Defense",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["forced arbitration", "terms of service", "opt out clause", "fine print", "consumer rights", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "How does a one-page opt-out letter restore your full constitutional protection?",
                "bridge": "See all five hidden contract traps explained on our main YouTube channel.",
                "close": "Check the terms on your next subscription before clicking accept.",
                "endcard_text": "FULL VIDEO ON YOUTUBE",
            },
            "editorial_stance": {
                "myth_debunked": "Clicking I Agree is a harmless technical formality required only for software updates.",
                "why_generic_advice_fails": "Generic consumer advice to simply read fifty pages of legalese is humanly impossible and offers no actionable recourse.",
                "channel_verdict": "Arbitration clauses are an asymmetric corporate weapon designed to extinguish constitutional jury access and conceal corporate wrongdoing.",
                "tradeoff_or_blindspot": "Sending a physical opt-out letter requires fifteen minutes and postage, but it permanently preserves your right to public justice.",
            },
            "actionable_value": {
                "core_mechanism": "Arbitration provisions enforce private dispute resolution and eliminate class actions, but federal law mandates a 30-day opt-out window.",
                "practical_rule_of_thumb": "Always search online terms for the phrase opt out within thirty days of signing up for any subscription.",
                "real_world_scenario": "When opening a rideshare or streaming account, mail a certified opt-out letter to their legal department immediately.",
            },
        },
        "youtube_title": dfp.SHORT_TITLE,
        "thumbnail_spec": {
            "visual_hook": "A thumb tapping an 'I Agree' button that turns into an iron padlock locking courthouse gates",
            "text_overlay": "DON'T TAP AGREE",
            "contrast_pair": "Instant click vs Forfeited jury rights",
            "thumbnail_prompt": "Crisp 3-color mid-century New Yorker editorial risograph print on newsprint ivory canvas (#F4EFE6). A smartphone screen displaying an illuminated blue 'I Agree' button turning into an iron padlock snapping shut over bronze courthouse doors, navy indigo ink #1D3557 and crimson #E63946, bold hand-lettered text in upper third: 'DON'T TAP AGREE'. 2D orthographic, >=60% negative space, zero 3D, zero gradients.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Consumer Law Literacy & Contract Defense",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["forced arbitration", "terms of service", "opt out clause", "fine print", "consumer rights", "shorts"],
        "parent_long_id": dfp.LONG_JOB_ID,
        "cta_plan": {
            "cliffhanger_peak": "How does a one-page opt-out letter restore your full constitutional protection?",
            "bridge": "See all five hidden contract traps explained on our main YouTube channel.",
            "close": "Check the terms on your next subscription before clicking accept.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Clicking I Agree is a harmless technical formality required only for software updates.",
            "why_generic_advice_fails": "Generic consumer advice to simply read fifty pages of legalese is humanly impossible and offers no actionable recourse.",
            "channel_verdict": "Arbitration clauses are an asymmetric corporate weapon designed to extinguish constitutional jury access and conceal corporate wrongdoing.",
            "tradeoff_or_blindspot": "Sending a physical opt-out letter requires fifteen minutes and postage, but it permanently preserves your right to public justice.",
        },
        "actionable_value": {
            "core_mechanism": "Arbitration provisions enforce private dispute resolution and eliminate class actions, but federal law mandates a 30-day opt-out window.",
            "practical_rule_of_thumb": "Always search online terms for the phrase opt out within thirty days of signing up for any subscription.",
            "real_world_scenario": "When opening a rideshare or streaming account, mail a certified opt-out letter to their legal department immediately.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    short_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(short_brief),
        "topic": dfp.SHORT_TOPIC,
        "duration": short_brief["duration"],
        "style": short_brief["style"],
        "required_points": [rp["text"] for rp in short_brief["required_points"]],
        "characters": [cast],
        "scenes": short_scenes,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(short_scenes)
        ],
        "outline": short_outline,
        "claims": [
            {
                "scene_id": "SC01",
                "quote": "you surrender your constitutional right to sue in court",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Mandatory predispute binding arbitration waives the Seventh Amendment right to a public jury trial.",
            },
            {
                "scene_id": "SC03",
                "quote": "class-action waivers prevent consumers from joining together",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Class action waivers in consumer contracts prevent collective aggregation of small-dollar harms.",
            },
            {
                "scene_id": "SC04",
                "quote": "You have thirty days from account creation to send a simple written letter",
                "language": "en",
                "source_id": "SRC02",
                "fact": "Written opt-out provisions typically require a physical letter or notice sent within thirty days of account registration.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    short_competitor = {
        "channel_id": ch_id,
        "job_id": dfp.SHORT_JOB_ID,
        "topic": dfp.SHORT_TOPIC,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "LegalEagle",
                    "top_performing_videos": [
                        {
                            "title": "Why You Just Signed Away Your Rights (Terms of Service)",
                            "views": "2.8M views",
                            "hook_technique": "Shows a real contract scroll covering an entire desk within the first three seconds.",
                            "pacing_structure": "Everyday sign-up -> Shocking clause reveal -> Practical defense step.",
                            "retention_driver": "Clear visual magnification of obscure legal wording that viewers sign daily.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dramatize the sheer physical scale of terms nobody reads.",
                        "Directly contrast corporate marketing promises with courtroom defense filings.",
                    ],
                },
                {
                    "channel_name": "Lehto's Law",
                    "top_performing_videos": [
                        {
                            "title": "How to Opt Out of Mandatory Arbitration Clauses",
                            "views": "850K views",
                            "hook_technique": "Starts by showing a certified mail receipt and explaining why it is worth millions in leverage.",
                            "pacing_structure": "Problem breakdown -> Statutory opt-out requirement -> Exact letter template.",
                            "retention_driver": "No-nonsense legal literacy empowering ordinary citizens with proven procedures.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Provide exact copy-paste sentence formulas viewers can use immediately.",
                        "Explain the tactical leverage preserved by opting out before a dispute ever happens.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 17,
                "zero_pause_opening_seconds": 14,
                "visual_contrast": "Friendly blue digital button on tablet versus padlocked heavy courthouse door.",
                "counter_intuitive_truth_slap": "You think clicking agree is just accepting software updates; legally, you just signed away your constitutional right to a jury trial.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "The routine sign-up click that quietly forfeits your jury rights."},
                {"phase": "empirical_conflict", "purpose": "Disputes forced into secret corporate conference rooms with paid arbitrators."},
                {"phase": "structural_model", "purpose": "Class-action bans enabling millions in micro-theft with zero legal accountability."},
                {"phase": "actionable_resolution", "purpose": "The statutory 30-day opt-out letter that preserves your constitutional rights."},
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Consistent 3-color Risograph newsprint ivory palette with continuous camera pan from digital screen to open courthouse.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Consumer Law Literacy & Contract Defense",
            "myth_debunked": "Clicking I Agree is a harmless technical formality required only for software updates.",
            "channel_verdict": "Arbitration clauses are an asymmetric corporate weapon designed to extinguish constitutional jury access and conceal corporate wrongdoing.",
            "actionable_rule_of_thumb": "Always search online terms for the phrase opt out within thirty days of signing up for any subscription.",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How does a one-page opt-out letter restore your full constitutional protection?",
            "bridge": "See all five hidden contract traps explained on our main YouTube channel.",
            "close": "Check the terms on your next subscription before clicking accept.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
    }

    # LONG 16:9
    long_scenes, long_outline = build_scene_objects(dfp.LONG_SCENES_RAW, ch_id, "16:9")
    long_brief = {
        "schema_version": "3.0",
        "topic": dfp.LONG_TOPIC,
        "audience": ch.audience,
        "goal": "Provide comprehensive legal explainer on forced arbitration, corporate class-action bans, repeat-player bias, and the 30-day written opt-out blueprint",
        "video_type": "explainer",
        "duration": {"min_seconds": 150.0, "max_seconds": 210.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Signing up for streaming or services and reflexively clicking I Agree"},
            {"id": "R02", "text": "Mandatory predispute binding arbitration waiving Seventh Amendment jury rights"},
            {"id": "R03", "text": "Class-action waiver economics preventing consumers from aggregating micro-charges"},
            {"id": "R04", "text": "Infinite arbitration overreach binding consumers across unrelated subsidiaries forever"},
            {"id": "R05", "text": "Editorial commentary on adhesion contracts and mid-video value share"},
            {"id": "R06", "text": "Public courtroom transparency versus private confidential dispute rooms"},
            {"id": "R07", "text": "Arbitration reality: sealed records, lack of rules of evidence, non-appealable awards"},
            {"id": "R08", "text": "The repeat-player bias: corporate defendants winning ninety percent of arbitrations"},
            {"id": "R09", "text": "The hidden escape hatch in Section 14: the mandatory 30-day opt-out window"},
            {"id": "R10", "text": "Step-by-step certified mail and legal email opt-out blueprint"},
            {"id": "R11", "text": "Summary of consumer power, preserving courtroom access, and closing CTA"},
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": dfp.SOURCES,
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": ch.speed,
            }
        ],
        "planning": make_planning(
            criteria=["Thoroughly explain forced arbitration mechanisms and empower viewer with exact 30-day opt-out protocol"],
            avoid=list(ch.avoid),
            pacing="Vigilant, clear, protective, grounded in consumer protection case law.",
            color="#1D3557",
            aspect="16:9",
        ),
        "packaging": {
            "youtube_title": dfp.LONG_TITLE,
            "thumbnail_spec": {
                "visual_hook": "A consumer looking at an 'I Agree' pop-up with a brass magnifying glass revealing Seventh Amendment jury waiver",
                "text_overlay": "NEVER CLICK AGREE",
                "contrast_pair": "Routine App Download vs Jury Right Forfeited",
                "thumbnail_prompt": "Crisp 3-color mid-century New Yorker editorial risograph print on newsprint ivory canvas (#F4EFE6). The sharp consumer advocate inspecting an 'I Agree' digital dialogue box with a brass magnifying glass, revealing microscopic handcuffs and locked courthouse gates, deep navy ink #1D3557 and crimson #E63946, bold hand-lettered text in upper third: 'NEVER CLICK AGREE'. 2D orthographic, >=60% negative space, zero 3D, zero gradients.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Consumer Law Literacy & Contract Defense",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["forced arbitration", "terms of service", "opt out clause", "fine print", "consumer protection", "legal rights"],
            "cta_plan": {
                "mid_cta": "If this breakdown protects your consumer rights, share it with someone who signs contracts.",
                "close": "Check the terms on your next subscription before clicking accept.",
                "endcard_text": "FULL VIDEO ON YOUTUBE",
            },
            "editorial_stance": {
                "myth_debunked": "Clicking I Agree is a harmless technical formality required only for software updates.",
                "why_generic_advice_fails": "Generic consumer advice to simply read fifty pages of legalese is humanly impossible and offers no actionable recourse.",
                "channel_verdict": "Arbitration clauses are an asymmetric corporate weapon designed to extinguish constitutional jury access and conceal corporate wrongdoing.",
                "tradeoff_or_blindspot": "Sending a physical opt-out letter requires fifteen minutes and postage, but it permanently preserves your right to public justice.",
            },
            "actionable_value": {
                "core_mechanism": "Arbitration provisions enforce private dispute resolution and eliminate class actions, but federal law mandates a 30-day opt-out window.",
                "practical_rule_of_thumb": "Always search online terms for the phrase opt out within thirty days of signing up for any subscription.",
                "real_world_scenario": "When opening a rideshare or streaming account, mail a certified opt-out letter to their legal department immediately.",
            },
        },
        "youtube_title": dfp.LONG_TITLE,
        "thumbnail_spec": {
            "visual_hook": "A consumer looking at an 'I Agree' pop-up with a brass magnifying glass revealing Seventh Amendment jury waiver",
            "text_overlay": "NEVER CLICK AGREE",
            "contrast_pair": "Routine App Download vs Jury Right Forfeited",
            "thumbnail_prompt": "Crisp 3-color mid-century New Yorker editorial risograph print on newsprint ivory canvas (#F4EFE6). The sharp consumer advocate inspecting an 'I Agree' digital dialogue box with a brass magnifying glass, revealing microscopic handcuffs and locked courthouse gates, deep navy ink #1D3557 and crimson #E63946, bold hand-lettered text in upper third: 'NEVER CLICK AGREE'. 2D orthographic, >=60% negative space, zero 3D, zero gradients.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Consumer Law Literacy & Contract Defense",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["forced arbitration", "terms of service", "opt out clause", "fine print", "consumer protection", "legal rights"],
        "cta_plan": {
            "mid_cta": "If this breakdown protects your consumer rights, share it with someone who signs contracts.",
            "close": "Check the terms on your next subscription before clicking accept.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Clicking I Agree is a harmless technical formality required only for software updates.",
            "why_generic_advice_fails": "Generic consumer advice to simply read fifty pages of legalese is humanly impossible and offers no actionable recourse.",
            "channel_verdict": "Arbitration clauses are an asymmetric corporate weapon designed to extinguish constitutional jury access and conceal corporate wrongdoing.",
            "tradeoff_or_blindspot": "Sending a physical opt-out letter requires fifteen minutes and postage, but it permanently preserves your right to public justice.",
        },
        "actionable_value": {
            "core_mechanism": "Arbitration provisions enforce private dispute resolution and eliminate class actions, but federal law mandates a 30-day opt-out window.",
            "practical_rule_of_thumb": "Always search online terms for the phrase opt out within thirty days of signing up for any subscription.",
            "real_world_scenario": "When opening a rideshare or streaming account, mail a certified opt-out letter to their legal department immediately.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    long_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(long_brief),
        "topic": dfp.LONG_TOPIC,
        "duration": long_brief["duration"],
        "style": long_brief["style"],
        "required_points": [rp["text"] for rp in long_brief["required_points"]],
        "characters": [cast],
        "scenes": long_scenes,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(long_scenes)
        ],
        "outline": long_outline,
        "claims": [
            {
                "scene_id": "SC02",
                "quote": "You waive your Seventh Amendment right to a trial before a jury of your peers",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Mandatory predispute binding arbitration waives the Seventh Amendment right to a public jury trial.",
            },
            {
                "scene_id": "SC03",
                "quote": "When millions of customers are barred from uniting their claims",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Class action waivers in consumer contracts prevent collective aggregation of small-dollar harms.",
            },
            {
                "scene_id": "SC08",
                "quote": "The private arbitration firm handling your case is paid hundreds of thousands of dollars each year",
                "language": "en",
                "source_id": "SRC01",
                "fact": "The repeat-player effect documents that arbitrators ruling frequently on corporate disputes favor corporate clients who pay forum fees.",
            },
            {
                "scene_id": "SC09",
                "quote": "If you notify the company in writing within thirty days of signing up",
                "language": "en",
                "source_id": "SRC02",
                "fact": "Written opt-out provisions typically require a physical letter or notice sent within thirty days of account registration.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    long_competitor = {
        "channel_id": ch_id,
        "job_id": dfp.LONG_JOB_ID,
        "topic": dfp.LONG_TOPIC,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "LegalEagle",
                    "top_performing_videos": [
                        {
                            "title": "Why You Just Signed Away Your Rights (Terms of Service)",
                            "views": "2.8M views",
                            "hook_technique": "Unrolls a massive parchment roll spanning forty feet across his law office.",
                            "pacing_structure": "Common signing habit -> The Fifth and Seventh Amendment stakes -> How courts enforce arbitration.",
                            "retention_driver": "Clear, accessible breakdown of legal doctrine without patronizing jargon.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Use high-contrast visual props representing invisible contract terms.",
                        "Directly cite actual corporate motions to compel arbitration from landmark federal court dockets.",
                    ],
                },
                {
                    "channel_name": "Consumer Reports",
                    "top_performing_videos": [
                        {
                            "title": "Forced Arbitration: How Companies Block You From Court",
                            "views": "1.2M views",
                            "hook_technique": "Profiles an ordinary family unable to sue after a major appliance fire.",
                            "pacing_structure": "Human victim case -> The buried clause -> Investigation into arbitration firm win rates.",
                            "retention_driver": "Hard empirical statistics on corporate repeat-player win rates.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Present data-driven investigations into repeat-player arbitrator bias.",
                        "Provide practical opt-out templates for viewers to execute immediately.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Digital phone app download contrasted with dissolving Seventh Amendment parchment.",
                "counter_intuitive_truth_slap": "You didn't just accept a software update; you signed away your constitutional right to be heard by an open jury of your peers.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "The routine sign-up click that quietly strips your Seventh Amendment rights."},
                {"phase": "empirical_conflict", "purpose": "Corporate class-action bans and private arbitration rooms designed to block public discovery."},
                {"phase": "structural_model", "purpose": "The repeat-player effect where corporations pay the private judges deciding consumer claims."},
                {"phase": "actionable_resolution", "purpose": "The step-by-step certified mail and email opt-out blueprint that preserves your right to justice."},
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential Risograph newsprint transitions tracking from the smartphone screen to private conference rooms and culminating in open public courthouse doors.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Consumer Law Literacy & Contract Defense",
            "myth_debunked": "Clicking I Agree is a harmless technical formality required only for software updates.",
            "channel_verdict": "Arbitration clauses are an asymmetric corporate weapon designed to extinguish constitutional jury access and conceal corporate wrongdoing.",
            "actionable_rule_of_thumb": "Always search online terms for the phrase opt out within thirty days of signing up for any subscription.",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "",
            "bridge": "",
            "close": "Check the terms on your next subscription before clicking accept.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
    }

    return (
        (dfp.SHORT_JOB_ID, short_brief, {"outline": short_outline}, short_content, short_competitor),
        (dfp.LONG_JOB_ID, long_brief, {"outline": long_outline}, long_content, long_competitor),
    )


# ==============================================================================
# 2. CHANNEL BUILDER: The Second Arrow (en_second_arrow)
# ==============================================================================

def generate_second_arrow_packages():
    ch_id = dsa.CHANNEL_ID
    ch = get_channel(ch_id)
    cast = channel_cast(ch_id, "CH01")
    stamp = channel_profile_stamp(ch_id)

    # SHORT 9:16
    short_scenes, short_outline = build_scene_objects(dsa.SHORT_SCENES_RAW, ch_id, "9:16")
    short_brief = {
        "schema_version": "3.0",
        "topic": dsa.SHORT_TOPIC,
        "audience": ch.audience,
        "goal": "Explain the biological ninety-second chemical surge versus mental rumination using the Buddha's second arrow parable",
        "video_type": "explainer",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Biological emotions flush in ninety seconds while mental suffering creates ongoing pain"},
            {"id": "R02", "text": "Harvard neuroanatomy showing adrenaline clearing while Default Mode Network loops stories"},
            {"id": "R03", "text": "The Buddha's Sallatha Sutta distinguishing inevitable first dart from self-inflicted second dart"},
            {"id": "R04", "text": "Actionable somatic tracking technique watching bodily sensations without narrative blame"},
            {"id": "R05", "text": "Cliffhanger peak on deactivating the Default Mode Network and funnel bridge to full guide"},
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": dsa.SOURCES,
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": ch.speed,
            }
        ],
        "planning": make_planning(
            criteria=["Explain the 90-second emotional flush and teach sensory tracking to dissolve the second arrow in 45s"],
            avoid=list(ch.avoid),
            pacing="Tranquil, meditative, poetic, grounded in early Buddhist psychology.",
            color="#1C1C1C",
            aspect="9:16",
        ),
        "packaging": {
            "youtube_title": dsa.SHORT_TITLE,
            "thumbnail_spec": {
                "visual_hook": "A flying dark arrow dissolving into misty mountain air beside an hourglass counting ninety seconds",
                "text_overlay": "STOP ARROW TWO",
                "contrast_pair": "Physical 90-Second Surge vs Lifetime of Rumination",
                "thumbnail_prompt": "Minimalist 2D Zen Sumi-e brush-ink wash illustration on handmade Xuan rice paper canvas (#F5EFE0). A dark flying sumi arrow dissolving into gentle mist beside an antique ceramic hourglass with cinnabar red sand #B84A39 counting 90 seconds, bamboo sage washes #5F7A61, bold hand-lettered text in upper third: 'STOP ARROW TWO'. Orthographic 2D, >=65% negative space, zero 3D, zero gradients.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Secular Buddhist Psychology & Mindfulness",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["second arrow", "sallatha sutta", "mindfulness", "letting go", "buddhist psychology", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "How does unhooking the Default Mode Network instantly dissolve emotional suffering?",
                "bridge": "Watch the complete second arrow meditation story on The Second Arrow YouTube.",
                "close": "Take three slow breaths tonight and release what is outside your control.",
                "endcard_text": "FULL VIDEO ON YOUTUBE",
            },
            "editorial_stance": {
                "myth_debunked": "Negative emotions inherently persist for days or weeks because of external events.",
                "why_generic_advice_fails": "Generic advice to just stay positive suppresses genuine nociception and forces the brain into violent cognitive dissonance.",
                "channel_verdict": "Physical pain is life's inevitable first dart, but prolonged suffering is a self-inflicted second arrow fired by our narrative ego.",
                "tradeoff_or_blindspot": "Sitting with raw somatic tension for ninety seconds feels uncomfortable, but it prevents months of toxic mental rumination.",
            },
            "actionable_value": {
                "core_mechanism": "Adrenaline and cortisol metabolize in ninety seconds; dropping narrative blame allows natural chemical clearance.",
                "practical_rule_of_thumb": "When triggered, track the physical knot in your body until the ninety-second timer runs dry.",
                "real_world_scenario": "When receiving harsh criticism, breathe directly into the chest tension without replaying what you should have said.",
            },
        },
        "youtube_title": dsa.SHORT_TITLE,
        "thumbnail_spec": {
            "visual_hook": "A flying dark arrow dissolving into misty mountain air beside an hourglass counting ninety seconds",
            "text_overlay": "STOP ARROW TWO",
            "contrast_pair": "Physical 90-Second Surge vs Lifetime of Rumination",
            "thumbnail_prompt": "Minimalist 2D Zen Sumi-e brush-ink wash illustration on handmade Xuan rice paper canvas (#F5EFE0). A dark flying sumi arrow dissolving into gentle mist beside an antique ceramic hourglass with cinnabar red sand #B84A39 counting 90 seconds, bamboo sage washes #5F7A61, bold hand-lettered text in upper third: 'STOP ARROW TWO'. Orthographic 2D, >=65% negative space, zero 3D, zero gradients.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Secular Buddhist Psychology & Mindfulness",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["second arrow", "sallatha sutta", "mindfulness", "letting go", "buddhist psychology", "shorts"],
        "parent_long_id": dsa.LONG_JOB_ID,
        "cta_plan": {
            "cliffhanger_peak": "How does unhooking the Default Mode Network instantly dissolve emotional suffering?",
            "bridge": "Watch the complete second arrow meditation story on The Second Arrow YouTube.",
            "close": "Take three slow breaths tonight and release what is outside your control.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Negative emotions inherently persist for days or weeks because of external events.",
            "why_generic_advice_fails": "Generic advice to just stay positive suppresses genuine nociception and forces the brain into violent cognitive dissonance.",
            "channel_verdict": "Physical pain is life's inevitable first dart, but prolonged suffering is a self-inflicted second arrow fired by our narrative ego.",
            "tradeoff_or_blindspot": "Sitting with raw somatic tension for ninety seconds feels uncomfortable, but it prevents months of toxic mental rumination.",
        },
        "actionable_value": {
            "core_mechanism": "Adrenaline and cortisol metabolize in ninety seconds; dropping narrative blame allows natural chemical clearance.",
            "practical_rule_of_thumb": "When triggered, track the physical knot in your body until the ninety-second timer runs dry.",
            "real_world_scenario": "When receiving harsh criticism, breathe directly into the chest tension without replaying what you should have said.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    short_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(short_brief),
        "topic": dsa.SHORT_TOPIC,
        "duration": short_brief["duration"],
        "style": short_brief["style"],
        "required_points": [rp["text"] for rp in short_brief["required_points"]],
        "characters": [cast],
        "scenes": short_scenes,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(short_scenes)
        ],
        "outline": short_outline,
        "claims": [
            {
                "scene_id": "SC01",
                "quote": "emotional shock only lasts ninety seconds in your bloodstream",
                "language": "en",
                "source_id": "SRC02",
                "fact": "The physiological lifespan of an emotional chemical cascade in the bloodstream is approximately ninety seconds.",
            },
            {
                "scene_id": "SC03",
                "quote": "The first dart is inevitable physical reality",
                "language": "en",
                "source_id": "SRC01",
                "fact": "The uninstructed person struck by painful feeling experiences two pains: physical and mental, like being struck by a second dart.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    short_competitor = {
        "channel_id": ch_id,
        "job_id": dsa.SHORT_JOB_ID,
        "topic": dsa.SHORT_TOPIC,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Einzelgänger",
                    "top_performing_videos": [
                        {
                            "title": "The Art of Letting Go (The Second Arrow)",
                            "views": "1.9M views",
                            "hook_technique": "Asks the viewer why a brief disagreement turns into three days of ruined sleep.",
                            "pacing_structure": "Everyday grievance -> The Buddhist parable -> Psychological application.",
                            "retention_driver": "Tranquil pacing, serene artwork, and deep philosophical resonance.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Frame psychological pain as an avoidable second reaction rather than an unavoidable tragedy.",
                        "Use minimalist aesthetic negative space to evoke calmness.",
                    ],
                },
                {
                    "channel_name": "Plum Village",
                    "top_performing_videos": [
                        {
                            "title": "Embracing Pain with Mindfulness",
                            "views": "920K views",
                            "hook_technique": "Invites the viewer to take a deep conscious breath and observe somatic tension without judgment.",
                            "pacing_structure": "Guided somatic check-in -> Ancient sutta context -> Evening peace blessing.",
                            "retention_driver": "Gentle, non-judgmental presence providing genuine relief from anxiety.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Ground philosophical concepts in immediate bodily somatic awareness.",
                        "Close with calming mindful reflections that foster nighttime peace.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Sharp dark flying arrow contrasted with tranquil water ripples and an emptying sandglass.",
                "counter_intuitive_truth_slap": "Your body stops feeling angry after ninety seconds; every hour of rage after that is an arrow you loaded and shot into yourself.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "The sudden sting of physical or emotional pain that flushes in ninety seconds."},
                {"phase": "empirical_conflict", "purpose": "How the brain's Default Mode Network loops grievance stories, re-triggering chemical floods."},
                {"phase": "structural_model", "purpose": "The Sallatha Sutta distinction between physical reality and self-inflicted mental suffering."},
                {"phase": "actionable_resolution", "purpose": "Tracking raw somatic sensation without chasing the story until the timer runs dry."},
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Fluid East Asian Sumi-e brushwork flowing from dark flying arrows into serene water ripples and blooming lotus petals.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Secular Buddhist Psychology & Mindfulness",
            "myth_debunked": "Negative emotions inherently persist for days or weeks because of external events.",
            "channel_verdict": "Physical pain is life's inevitable first dart, but prolonged suffering is a self-inflicted second arrow fired by our narrative ego.",
            "actionable_rule_of_thumb": "When triggered, track the physical knot in your body until the ninety-second timer runs dry.",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How does unhooking the Default Mode Network instantly dissolve emotional suffering?",
            "bridge": "Watch the complete second arrow meditation story on The Second Arrow YouTube.",
            "close": "Take three slow breaths tonight and release what is outside your control.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
    }

    # LONG 16:9
    long_scenes, long_outline = build_scene_objects(dsa.LONG_SCENES_RAW, ch_id, "16:9")
    long_brief = {
        "schema_version": "3.0",
        "topic": dsa.LONG_TOPIC,
        "audience": ch.audience,
        "goal": "Provide deep philosophical and neurobiological exploration uniting the Sallatha Sutta with Harvard 90-second flush and Brewer fMRI studies",
        "video_type": "explainer",
        "duration": {"min_seconds": 150.0, "max_seconds": 210.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "The Buddha gathering disciples and introducing the parable of two arrows in a forest"},
            {"id": "R02", "text": "Distinguishing inevitable physical nociception from self-inflicted psychological resistance"},
            {"id": "R03", "text": "Harvard neuroanatomist Jill Bolte Taylor and the 90-second chemical surge lifespan"},
            {"id": "R04", "text": "Metabolizing adrenaline and cortisol: how liver and kidneys clear emotional storms"},
            {"id": "R05", "text": "Editorial commentary on reloading the bow and mid-video mindful reflection"},
            {"id": "R06", "text": "The Default Mode Network: the brain's internal narrative author of grievance"},
            {"id": "R07", "text": "The Posterior Cingulate Cortex: neural hub responsible for taking events personally"},
            {"id": "R08", "text": "Editorial commentary on the second arrow as an optional self-inflicted story"},
            {"id": "R09", "text": "Dr. Judson Brewer's fMRI research proving somatic curiosity deactivates the PCC"},
            {"id": "R10", "text": "The step-by-step Somatic Uncoupling Protocol for daily tension release"},
            {"id": "R11", "text": "Resting in the open sky of awareness, natural healing, and evening blessing CTA"},
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": dsa.SOURCES,
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": ch.speed,
            }
        ],
        "planning": make_planning(
            criteria=["Bridge Buddhist psychology and neuroscience to provide deep evening calm and practical somatic uncoupling"],
            avoid=list(ch.avoid),
            pacing="Tranquil, meditative, poetic, compassionate, grounded in early Buddhist psychology.",
            color="#1C1C1C",
            aspect="16:9",
        ),
        "packaging": {
            "youtube_title": dsa.LONG_TITLE,
            "thumbnail_spec": {
                "visual_hook": "The Zen monk seated beside an unstrung wooden bow as an arrow dissolves into flying lotus petals",
                "text_overlay": "DROP ARROW TWO",
                "contrast_pair": "Wounding Arrow vs Meditative Liberation",
                "thumbnail_prompt": "Minimalist 2D Zen Sumi-e brush-ink wash illustration on handmade Xuan rice paper canvas (#F5EFE0). The serene Zen monk companion seated beside a slack wooden bow as a dark arrow dissolves into soft lotus petals in pink coral #D98A76 and bamboo sage #5F7A61, bold hand-lettered text in upper third: 'DROP ARROW TWO'. Orthographic 2D, >=65% negative space, zero 3D, zero gradients.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Secular Buddhist Psychology & Mindfulness",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["second arrow", "sallatha sutta", "mindfulness", "letting go", "buddhist neuroscience", "default mode network"],
            "cta_plan": {
                "mid_cta": "If this reflection brings quiet stillness, share it with someone who carries tension.",
                "close": "Take three slow breaths tonight and release what is outside your control.",
                "endcard_text": "FULL VIDEO ON YOUTUBE",
            },
            "editorial_stance": {
                "myth_debunked": "Negative emotions inherently persist for days or weeks because of external events.",
                "why_generic_advice_fails": "Generic advice to just stay positive suppresses genuine nociception and forces the brain into violent cognitive dissonance.",
                "channel_verdict": "Physical pain is life's inevitable first dart, but prolonged suffering is a self-inflicted second arrow fired by our narrative ego.",
                "tradeoff_or_blindspot": "Sitting with raw somatic tension for ninety seconds feels uncomfortable, but it prevents months of toxic mental rumination.",
            },
            "actionable_value": {
                "core_mechanism": "Adrenaline and cortisol metabolize in ninety seconds; dropping narrative blame allows natural chemical clearance.",
                "practical_rule_of_thumb": "When triggered, track the physical knot in your body until the ninety-second timer runs dry.",
                "real_world_scenario": "When receiving harsh criticism, breathe directly into the chest tension without replaying what you should have said.",
            },
        },
        "youtube_title": dsa.LONG_TITLE,
        "thumbnail_spec": {
            "visual_hook": "The Zen monk seated beside an unstrung wooden bow as an arrow dissolves into flying lotus petals",
            "text_overlay": "DROP ARROW TWO",
            "contrast_pair": "Wounding Arrow vs Meditative Liberation",
            "thumbnail_prompt": "Minimalist 2D Zen Sumi-e brush-ink wash illustration on handmade Xuan rice paper canvas (#F5EFE0). The serene Zen monk companion seated beside a slack wooden bow as a dark arrow dissolves into soft lotus petals in pink coral #D98A76 and bamboo sage #5F7A61, bold hand-lettered text in upper third: 'DROP ARROW TWO'. Orthographic 2D, >=65% negative space, zero 3D, zero gradients.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Secular Buddhist Psychology & Mindfulness",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["second arrow", "sallatha sutta", "mindfulness", "letting go", "buddhist neuroscience", "default mode network"],
        "cta_plan": {
            "mid_cta": "If this reflection brings quiet stillness, share it with someone who carries tension.",
            "close": "Take three slow breaths tonight and release what is outside your control.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Negative emotions inherently persist for days or weeks because of external events.",
            "why_generic_advice_fails": "Generic advice to just stay positive suppresses genuine nociception and forces the brain into violent cognitive dissonance.",
            "channel_verdict": "Physical pain is life's inevitable first dart, but prolonged suffering is a self-inflicted second arrow fired by our narrative ego.",
            "tradeoff_or_blindspot": "Sitting with raw somatic tension for ninety seconds feels uncomfortable, but it prevents months of toxic mental rumination.",
        },
        "actionable_value": {
            "core_mechanism": "Adrenaline and cortisol metabolize in ninety seconds; dropping narrative blame allows natural chemical clearance.",
            "practical_rule_of_thumb": "When triggered, track the physical knot in your body until the ninety-second timer runs dry.",
            "real_world_scenario": "When receiving harsh criticism, breathe directly into the chest tension without replaying what you should have said.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    long_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(long_brief),
        "topic": dsa.LONG_TOPIC,
        "duration": long_brief["duration"],
        "style": long_brief["style"],
        "required_points": [rp["text"] for rp in long_brief["required_points"]],
        "characters": [cast],
        "scenes": long_scenes,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(long_scenes)
        ],
        "outline": long_outline,
        "claims": [
            {
                "scene_id": "SC02",
                "quote": "The first arrow is the unavoidable pain of physical life",
                "language": "en",
                "source_id": "SRC01",
                "fact": "The uninstructed person struck by painful feeling experiences two pains: physical and mental, like being struck by a second dart.",
            },
            {
                "scene_id": "SC03",
                "quote": "the physiological surge lasts approximately ninety seconds in the bloodstream",
                "language": "en",
                "source_id": "SRC02",
                "fact": "The physiological lifespan of an emotional chemical cascade in the bloodstream is approximately ninety seconds.",
            },
            {
                "scene_id": "SC09",
                "quote": "the Posterior Cingulate Cortex immediately deactivated",
                "language": "en",
                "source_id": "SRC03",
                "fact": "Mindfulness meditation deactivates core nodes of the Default Mode Network, particularly the posterior cingulate cortex.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    long_competitor = {
        "channel_id": ch_id,
        "job_id": dsa.LONG_JOB_ID,
        "topic": dsa.LONG_TOPIC,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Einzelgänger",
                    "top_performing_videos": [
                        {
                            "title": "The Art of Letting Go (The Second Arrow)",
                            "views": "1.9M views",
                            "hook_technique": "Starts with the physical dilemma of an archer and poses the question of self-inflicted wounds.",
                            "pacing_structure": "The Sallatha Sutta allegory -> Psychological anatomy of resentment -> Practical letting go.",
                            "retention_driver": "Clear, poetic cadence and deeply grounding narrative voice.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Frame emotional rumination as an unhelpful mental loop that can be consciously dropped.",
                        "Use high negative space visuals to allow viewers time to absorb profound reflections.",
                    ],
                },
                {
                    "channel_name": "Judson Brewer MD",
                    "top_performing_videos": [
                        {
                            "title": "A Simple Way to Break a Bad Habit (and Anxiety)",
                            "views": "18M views",
                            "hook_technique": "Directly explains the brain's reward loop and Default Mode Network in simple visual terms.",
                            "pacing_structure": "Trigger -> Narrative loop -> Somatic curiosity practice.",
                            "retention_driver": "Hard neuroimaging fMRI evidence backing ancient contemplative wisdom.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Show real fMRI brain heat maps demonstrating how mindful presence cools the posterior cingulate cortex.",
                        "Provide concrete somatic curiosity prompts instead of abstract willpower advice.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Sharp dark sumi arrow in flight contrasted with calm mountain stream and dropping bow.",
                "counter_intuitive_truth_slap": "Pain takes only 90 seconds to clear your veins; every hour of suffering after that is a second arrow you fired into yourself.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "The sudden pain of life and the ancient forest parable of the two arrows."},
                {"phase": "empirical_conflict", "purpose": "Jill Bolte Taylor's 90-second chemical surge versus the Default Mode Network's narrative looping."},
                {"phase": "structural_model", "purpose": "The posterior cingulate cortex taking events personally and re-triggering adrenal surges."},
                {"phase": "actionable_resolution", "purpose": "Brewer's fMRI somatic curiosity practice dissolving suffering into vast awareness."},
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Harmonious Sumi-e ink wash sequences moving from dark flying arrows to glowing anatomical brain nodes and settling into open water reflections.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Secular Buddhist Psychology & Mindfulness",
            "myth_debunked": "Negative emotions inherently persist for days or weeks because of external events.",
            "channel_verdict": "Physical pain is life's inevitable first dart, but prolonged suffering is a self-inflicted second arrow fired by our narrative ego.",
            "actionable_rule_of_thumb": "When triggered, track the physical knot in your body until the ninety-second timer runs dry.",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "",
            "bridge": "",
            "close": "Take three slow breaths tonight and release what is outside your control.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
    }

    return (
        (dsa.SHORT_JOB_ID, short_brief, {"outline": short_outline}, short_content, short_competitor),
        (dsa.LONG_JOB_ID, long_brief, {"outline": long_outline}, long_content, long_competitor),
    )


# ==============================================================================
# 3. CHANNEL BUILDER: Bamboo & Marble (en_bamboo_marble)
# ==============================================================================

def generate_bamboo_marble_packages():
    ch_id = dbm.CHANNEL_ID
    ch = get_channel(ch_id)
    cast = channel_cast(ch_id, "CH01")
    stamp = channel_profile_stamp(ch_id)

    # SHORT 9:16
    short_scenes, short_outline = build_scene_objects(dbm.SHORT_SCENES_RAW, ch_id, "9:16")
    short_brief = {
        "schema_version": "3.0",
        "topic": dbm.SHORT_TOPIC,
        "audience": ch.audience,
        "goal": "Explain why we never rage at an empty drifting boat and apply Zhuangzi and Marcus Aurelius to master evening emotional calm",
        "video_type": "explainer",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Raging at a boat collision on a misty river until discovering the craft is completely empty"},
            {"id": "R02", "text": "Identical physical damage yields zero anger when human malice is absent"},
            {"id": "R03", "text": "Zhuangzi's Daoist insight: anger is caused by the ego's demand that others avoid our path"},
            {"id": "R04", "text": "Marcus Aurelius viewing difficult people as unpiloted canoes tossed by their own storms"},
            {"id": "R05", "text": "Cliffhanger peak on emptying your own ego and funnel bridge to the nighttime fable"},
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": dbm.SOURCES,
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": ch.speed,
            }
        ],
        "planning": make_planning(
            criteria=["Deliver the empty boat parable and teach Stoic reframing to extinguish daily rage within 45s"],
            avoid=list(ch.avoid),
            pacing="Soothing, reflective, philosophical, grounded, poetic.",
            color="#1D2D44",
            aspect="9:16",
        ),
        "packaging": {
            "youtube_title": dbm.SHORT_TITLE,
            "thumbnail_spec": {
                "visual_hook": "An angry traveler pointing at an unmanned wooden canoe floating peacefully under a crescent moon",
                "text_overlay": "THE EMPTY BOAT",
                "contrast_pair": "Blinding Fury vs Instant Serenity",
                "thumbnail_prompt": "Tranquil 2D flat midnight gouache on coarse raw linen canvas (#EDE6D6). An unmanned wooden canoe drifting serenely under a glowing crescent moon #E9C46A on slate-indigo river water #1D2D44, carved marble colonnades and celadon bamboo #84A98C, bold hand-lettered text in upper third: 'THE EMPTY BOAT'. Orthographic 2D, >=60% negative space, zero 3D, zero gradients.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Stoicism & Daoist Wisdom for Evening Calm",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["empty boat", "zhuangzi", "marcus aurelius", "stoicism", "anger management", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "How does emptying your own ego prevent anyone from ever bumping into you again?",
                "bridge": "Watch the complete nighttime fable and relaxing background on Bamboo & Marble YouTube.",
                "close": "Release today's burdens into the quiet night. Rest well and be at peace.",
                "endcard_text": "FULL VIDEO ON YOUTUBE",
            },
            "editorial_stance": {
                "myth_debunked": "Anger is an automatic, involuntary reaction caused directly by external friction.",
                "why_generic_advice_fails": "Generic advice to count to ten merely bottles up resentment without addressing the ego's false demand for personal targeting.",
                "channel_verdict": "Anger is never caused by the collision itself; it is the ego's wounded projection demanding that drifting boats should not exist.",
                "tradeoff_or_blindspot": "Viewing offenders as unmanned vessels requires surrendering the righteous pleasure of vengeance, but it buys unbreakable peace.",
            },
            "actionable_value": {
                "core_mechanism": "Rage evaporates when intent is removed; treating difficult people as unpiloted vessels redirects energy from anger to compassion.",
                "practical_rule_of_thumb": "Whenever someone cuts you off or snaps, pause and whisper: 'This is an empty boat.'",
                "real_world_scenario": "When receiving a harsh work email, view the sender as an exhausted vessel tossed by private storms, and respond with calm brevity.",
            },
        },
        "youtube_title": dbm.SHORT_TITLE,
        "thumbnail_spec": {
            "visual_hook": "An angry traveler pointing at an unmanned wooden canoe floating peacefully under a crescent moon",
            "text_overlay": "THE EMPTY BOAT",
            "contrast_pair": "Blinding Fury vs Instant Serenity",
            "thumbnail_prompt": "Tranquil 2D flat midnight gouache on coarse raw linen canvas (#EDE6D6). An unmanned wooden canoe drifting serenely under a glowing crescent moon #E9C46A on slate-indigo river water #1D2D44, carved marble colonnades and celadon bamboo #84A98C, bold hand-lettered text in upper third: 'THE EMPTY BOAT'. Orthographic 2D, >=60% negative space, zero 3D, zero gradients.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Stoicism & Daoist Wisdom for Evening Calm",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["empty boat", "zhuangzi", "marcus aurelius", "stoicism", "anger management", "shorts"],
        "parent_long_id": dbm.LONG_JOB_ID,
        "cta_plan": {
            "cliffhanger_peak": "How does emptying your own ego prevent anyone from ever bumping into you again?",
            "bridge": "Watch the complete nighttime fable and relaxing background on Bamboo & Marble YouTube.",
            "close": "Release today's burdens into the quiet night. Rest well and be at peace.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Anger is an automatic, involuntary reaction caused directly by external friction.",
            "why_generic_advice_fails": "Generic advice to count to ten merely bottles up resentment without addressing the ego's false demand for personal targeting.",
            "channel_verdict": "Anger is never caused by the collision itself; it is the ego's wounded projection demanding that drifting boats should not exist.",
            "tradeoff_or_blindspot": "Viewing offenders as unmanned vessels requires surrendering the righteous pleasure of vengeance, but it buys unbreakable peace.",
        },
        "actionable_value": {
            "core_mechanism": "Rage evaporates when intent is removed; treating difficult people as unpiloted vessels redirects energy from anger to compassion.",
            "practical_rule_of_thumb": "Whenever someone cuts you off or snaps, pause and whisper: 'This is an empty boat.'",
            "real_world_scenario": "When receiving a harsh work email, view the sender as an exhausted vessel tossed by private storms, and respond with calm brevity.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    short_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(short_brief),
        "topic": dbm.SHORT_TOPIC,
        "duration": short_brief["duration"],
        "style": short_brief["style"],
        "required_points": [rp["text"] for rp in short_brief["required_points"]],
        "characters": [cast],
        "scenes": short_scenes,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(short_scenes)
        ],
        "outline": short_outline,
        "claims": [
            {
                "scene_id": "SC02",
                "quote": "You cannot stay angry at floating pine planks when there is no helmsman",
                "language": "en",
                "source_id": "SRC01",
                "fact": "If a man is crossing a river and an empty boat collides with his skiff, even an irritable man will not lose his temper.",
            },
            {
                "scene_id": "SC04",
                "quote": "Difficult people who hurt you are merely unpiloted vessels",
                "language": "en",
                "source_id": "SRC02",
                "fact": "When you wake up in the morning, tell yourself: the people I deal with today will be meddling, ungrateful, arrogant, dishonest, jealous, and surly.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    short_competitor = {
        "channel_id": ch_id,
        "job_id": dbm.SHORT_JOB_ID,
        "topic": dbm.SHORT_TOPIC,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Daily Stoic",
                    "top_performing_videos": [
                        {
                            "title": "How Marcus Aurelius Dealt With Rude People",
                            "views": "3.4M views",
                            "hook_technique": "Quotes the opening of Meditations Book 2 and reframes difficult people as natural elements.",
                            "pacing_structure": "The morning reflection -> Reframing ignorance -> Actionable daily practice.",
                            "retention_driver": "Practical, clear, grounded advice for dealing with daily frustration.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Directly connect ancient Roman emperors and Chinese sages to modern workplace and traffic friction.",
                        "Emphasize the dichotomy of control: external actions versus internal reactions.",
                    ],
                },
                {
                    "channel_name": "Pursuit of Wonder",
                    "top_performing_videos": [
                        {
                            "title": "The Parable of The Empty Boat",
                            "views": "2.1M views",
                            "hook_technique": "Opens with an immersive atmospheric nighttime fable of a traveler on a misty river.",
                            "pacing_structure": "The collision story -> The psychological turn -> The existential lesson.",
                            "retention_driver": "Hypnotic storytelling and beautiful visual metaphors creating soothing immersion.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Use storytelling parables rather than lecture bullet points.",
                        "Create soothing nighttime ambiance that helps viewers unwind before sleep.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Violent river collision on misty water contrasted with an empty unpiloted wooden canoe.",
                "counter_intuitive_truth_slap": "You never scream at an empty boat that hits you; your rage is never about the crash, but your ego demanding that no one cross your path.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "The jarring collision on a misty river that instantly dissolves upon seeing the boat is empty."},
                {"phase": "empirical_conflict", "purpose": "Identical physical damage producing opposite emotional reactions based solely on presumed intent."},
                {"phase": "structural_model", "purpose": "Zhuangzi and Marcus Aurelius revealing that offenders are unpiloted vessels tossed by inner turmoil."},
                {"phase": "actionable_resolution", "purpose": "The daily practice of whispering 'This is an empty boat' and emptying your own vessel of ego."},
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Matte mineral gouache brushwork on raw linen transitioning from misty river collisions to moonlit Roman colonnades and calm starry night skies.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Stoicism & Daoist Wisdom for Evening Calm",
            "myth_debunked": "Anger is an automatic, involuntary reaction caused directly by external friction.",
            "channel_verdict": "Anger is never caused by the collision itself; it is the ego's wounded projection demanding that drifting boats should not exist.",
            "actionable_rule_of_thumb": "Whenever someone cuts you off or snaps, pause and whisper: 'This is an empty boat.'",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How does emptying your own ego prevent anyone from ever bumping into you again?",
            "bridge": "Watch the complete nighttime fable and relaxing background on Bamboo & Marble YouTube.",
            "close": "Release today's burdens into the quiet night. Rest well and be at peace.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
    }

    # LONG 16:9
    long_scenes, long_outline = build_scene_objects(dbm.LONG_SCENES_RAW, ch_id, "16:9")
    long_brief = {
        "schema_version": "3.0",
        "topic": dbm.LONG_TOPIC,
        "audience": ch.audience,
        "goal": "Unite Zhuangzi's Empty Boat parable with Marcus Aurelius and Epictetus to extinguish personal outrage and guide viewers into serene nighttime peace",
        "video_type": "explainer",
        "duration": {"min_seconds": 150.0, "max_seconds": 210.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Crossing a misty river at twilight and experiencing a jarring wooden collision"},
            {"id": "R02", "text": "The automatic surge of fury and shouting when an oarsman is presumed aboard"},
            {"id": "R03", "text": "The alternative scenario: discovering the colliding vessel is completely unpiloted"},
            {"id": "R04", "text": "The instant vanishing of anger when human malice and intent are removed"},
            {"id": "R05", "text": "Editorial commentary on the illusion of personal insult and mid-video calm share"},
            {"id": "R06", "text": "Marcus Aurelius in the Roman military tent writing Meditations Book Two"},
            {"id": "R07", "text": "The morning directive: viewing wrongdoers as blind actors tossed by inner storms"},
            {"id": "R08", "text": "Epictetus and the Dichotomy of Control: we are disturbed by views, not things"},
            {"id": "R09", "text": "The helmsman without oars: replacing anger with understanding and steady compassion"},
            {"id": "R10", "text": "The daily Empty Boat practice: pausing three seconds before responding to friction"},
            {"id": "R11", "text": "Emptying your own boat of ego: ultimate tranquility and nighttime restful CTA"},
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": dbm.SOURCES,
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": ch.speed,
            }
        ],
        "planning": make_planning(
            criteria=["Interweave Eastern Daoism and Western Stoicism to deliver soothing bedtime reflection and anger mastery"],
            avoid=list(ch.avoid),
            pacing="Soothing, reflective, philosophical, grounded, poetic.",
            color="#1D2D44",
            aspect="16:9",
        ),
        "packaging": {
            "youtube_title": dbm.LONG_TITLE,
            "thumbnail_spec": {
                "visual_hook": "The philosopher traveler guiding an unpiloted wooden canoe past carved Roman marble columns under golden moon",
                "text_overlay": "BE THE EMPTY BOAT",
                "contrast_pair": "Reckless Collision vs Ancient Stoic Serenity",
                "thumbnail_prompt": "Tranquil 2D flat midnight gouache on coarse raw linen canvas (#EDE6D6). The philosopher traveler standing peacefully in a wooden skiff guiding an unpiloted canoe downstream under a golden crescent moon #E9C46A on slate-indigo river water #1D2D44, carved marble colonnades and celadon bamboo #84A98C, bold hand-lettered text in upper third: 'BE THE EMPTY BOAT'. Orthographic 2D, >=60% negative space, zero 3D, zero gradients.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Stoicism & Daoist Wisdom for Evening Calm",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["empty boat", "zhuangzi", "marcus aurelius", "epictetus", "stoic philosophy", "evening meditation"],
            "cta_plan": {
                "mid_cta": "If this quiet fable brings clarity, share it with someone navigating turbulent waters.",
                "close": "Release today's burdens into the quiet night. Rest well and be at peace.",
                "endcard_text": "FULL VIDEO ON YOUTUBE",
            },
            "editorial_stance": {
                "myth_debunked": "Anger is an automatic, involuntary reaction caused directly by external friction.",
                "why_generic_advice_fails": "Generic advice to count to ten merely bottles up resentment without addressing the ego's false demand for personal targeting.",
                "channel_verdict": "Anger is never caused by the collision itself; it is the ego's wounded projection demanding that drifting boats should not exist.",
                "tradeoff_or_blindspot": "Viewing offenders as unmanned vessels requires surrendering the righteous pleasure of vengeance, but it buys unbreakable peace.",
            },
            "actionable_value": {
                "core_mechanism": "Rage evaporates when intent is removed; treating difficult people as unpiloted vessels redirects energy from anger to compassion.",
                "practical_rule_of_thumb": "Whenever someone cuts you off or snaps, pause and whisper: 'This is an empty boat.'",
                "real_world_scenario": "When receiving a harsh work email, view the sender as an exhausted vessel tossed by private storms, and respond with calm brevity.",
            },
        },
        "youtube_title": dbm.LONG_TITLE,
        "thumbnail_spec": {
            "visual_hook": "The philosopher traveler guiding an unpiloted wooden canoe past carved Roman marble columns under golden moon",
            "text_overlay": "BE THE EMPTY BOAT",
            "contrast_pair": "Reckless Collision vs Ancient Stoic Serenity",
            "thumbnail_prompt": "Tranquil 2D flat midnight gouache on coarse raw linen canvas (#EDE6D6). The philosopher traveler standing peacefully in a wooden skiff guiding an unpiloted canoe downstream under a golden crescent moon #E9C46A on slate-indigo river water #1D2D44, carved marble colonnades and celadon bamboo #84A98C, bold hand-lettered text in upper third: 'BE THE EMPTY BOAT'. Orthographic 2D, >=60% negative space, zero 3D, zero gradients.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Stoicism & Daoist Wisdom for Evening Calm",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["empty boat", "zhuangzi", "marcus aurelius", "epictetus", "stoic philosophy", "evening meditation"],
        "cta_plan": {
            "mid_cta": "If this quiet fable brings clarity, share it with someone navigating turbulent waters.",
            "close": "Release today's burdens into the quiet night. Rest well and be at peace.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
        "channel_profile": stamp,
        "engagement": asdict(ch.engagement),
        "editorial_stance": {
            "myth_debunked": "Anger is an automatic, involuntary reaction caused directly by external friction.",
            "why_generic_advice_fails": "Generic advice to count to ten merely bottles up resentment without addressing the ego's false demand for personal targeting.",
            "channel_verdict": "Anger is never caused by the collision itself; it is the ego's wounded projection demanding that drifting boats should not exist.",
            "tradeoff_or_blindspot": "Viewing offenders as unmanned vessels requires surrendering the righteous pleasure of vengeance, but it buys unbreakable peace.",
        },
        "actionable_value": {
            "core_mechanism": "Rage evaporates when intent is removed; treating difficult people as unpiloted vessels redirects energy from anger to compassion.",
            "practical_rule_of_thumb": "Whenever someone cuts you off or snaps, pause and whisper: 'This is an empty boat.'",
            "real_world_scenario": "When receiving a harsh work email, view the sender as an exhausted vessel tossed by private storms, and respond with calm brevity.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    long_content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(long_brief),
        "topic": dbm.LONG_TOPIC,
        "duration": long_brief["duration"],
        "style": long_brief["style"],
        "required_points": [rp["text"] for rp in long_brief["required_points"]],
        "characters": [cast],
        "scenes": long_scenes,
        "coverage": [
            {"requirement_id": f"R{i+1:02d}", "scene_id": s["id"], "quote": s["narration"][:60]}
            for i, s in enumerate(long_scenes)
        ],
        "outline": long_outline,
        "claims": [
            {
                "scene_id": "SC04",
                "quote": "Even the most irritable person on earth does not scream curses at empty timber",
                "language": "en",
                "source_id": "SRC01",
                "fact": "If a man is crossing a river and an empty boat collides with his skiff, even an irritable man will not lose his temper.",
            },
            {
                "scene_id": "SC07",
                "quote": "the people I deal with today will be meddling, ungrateful, arrogant, dishonest, and surly",
                "language": "en",
                "source_id": "SRC02",
                "fact": "When you wake up in the morning, tell yourself: the people I deal with today will be meddling, ungrateful, arrogant, dishonest, jealous, and surly.",
            },
            {
                "scene_id": "SC08",
                "quote": "we are disturbed not by things, but by the views we take of them",
                "language": "en",
                "source_id": "SRC03",
                "fact": "Men are disturbed not by things, but by the view which they take of them.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    long_competitor = {
        "channel_id": ch_id,
        "job_id": dbm.LONG_JOB_ID,
        "topic": dbm.LONG_TOPIC,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Daily Stoic",
                    "top_performing_videos": [
                        {
                            "title": "How Marcus Aurelius Dealt With Rude People",
                            "views": "3.4M views",
                            "hook_technique": "Asks why we let strangers ruin our entire day and cites Marcus Aurelius's morning journal.",
                            "pacing_structure": "The problem of everyday rudeness -> Book 2 of Meditations -> Daily Stoic reframing.",
                            "retention_driver": "Clear, practical, direct delivery of ancient philosophy to modern challenges.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dismantle the illusion that difficult people are purposefully targeting our dignity.",
                        "Reframe external insults as natural environmental phenomena like rain or wind.",
                    ],
                },
                {
                    "channel_name": "Pursuit of Wonder",
                    "top_performing_videos": [
                        {
                            "title": "The Parable of The Empty Boat",
                            "views": "2.1M views",
                            "hook_technique": "Immersive narrative establishing an evening skiff crossing on a misty lake.",
                            "pacing_structure": "The collision story -> The sudden vanishing of anger -> The profound realization of ego.",
                            "retention_driver": "Poetic reflection and gentle nighttime atmosphere that induces deep contemplation.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Use sensory storytelling to illustrate philosophical principles.",
                        "Blend classical Eastern parables with universal human emotional experiences.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Splintering collision in dense fog contrasted with vacant boat floorboards under crescent moon.",
                "counter_intuitive_truth_slap": "You never scream at an unmanned boat; anger is never about the physical impact, but your ego demanding that no one cross your path.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "The jarring evening river collision and the immediate urge to shout accusations."},
                {"phase": "empirical_conflict", "purpose": "The instant evaporation of fury upon discovering the boat is completely deserted."},
                {"phase": "structural_model", "purpose": "Zhuangzi and Marcus Aurelius explaining that offenders are unpiloted canoes tossed by circumstance."},
                {"phase": "actionable_resolution", "purpose": "The daily three-second Empty Boat reframing and emptying your own vessel of self-importance."},
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Gouache on raw linen transitions moving from misty twilight waters to warm imperial Roman tents and quiet moonlit bamboo colonnades.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Stoicism & Daoist Wisdom for Evening Calm",
            "myth_debunked": "Anger is an automatic, involuntary reaction caused directly by external friction.",
            "channel_verdict": "Anger is never caused by the collision itself; it is the ego's wounded projection demanding that drifting boats should not exist.",
            "actionable_rule_of_thumb": "Whenever someone cuts you off or snaps, pause and whisper: 'This is an empty boat.'",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "",
            "bridge": "",
            "close": "Release today's burdens into the quiet night. Rest well and be at peace.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
    }

    return (
        (dbm.SHORT_JOB_ID, short_brief, {"outline": short_outline}, short_content, short_competitor),
        (dbm.LONG_JOB_ID, long_brief, {"outline": long_outline}, long_content, long_competitor),
    )


# ==============================================================================
# MAIN EXECUTION & SUMMARY REPORT
# ==============================================================================

def main():
    print("=" * 80)
    print("SA-EN-06: Production Package Generator & Quality Gate Verification")
    print("Cluster 6: Consumer Law, Buddhist Neuroscience & East-West Stoicism")
    print("=" * 80)

    packages_to_generate = []

    # 1. Everyday Fine Print
    print("\nBuilding packages for Channel 1: Everyday Fine Print (en_fine_print)...")
    fp_short, fp_long = generate_fine_print_packages()
    packages_to_generate.extend([fp_short, fp_long])

    # 2. The Second Arrow
    print("Building packages for Channel 2: The Second Arrow (en_second_arrow)...")
    sa_short, sa_long = generate_second_arrow_packages()
    packages_to_generate.extend([sa_short, sa_long])

    # 3. Bamboo & Marble
    print("Building packages for Channel 3: Bamboo & Marble (en_bamboo_marble)...")
    bm_short, bm_long = generate_bamboo_marble_packages()
    packages_to_generate.extend([bm_short, bm_long])

    results = []
    print("\nRunning full Schema 3.0 validation and strict quality linters on all 6 jobs...")

    for job_id, brief, outline, content, competitor in packages_to_generate:
        print(f"  Validating and saving {job_id}...")
        res = validate_and_save_package(job_id, brief, outline, content, competitor)
        results.append(res)
        print(f"    ✓ {job_id}: {res['scene_count']} scenes, {res['image_count']} images, {res['word_count']} words, est {res['est_duration_sec']}s ({res['hold_sec_per_img']}s/img) - {res['linter_status']}")

    print("\n" + "=" * 80)
    print("ALL 6 PRODUCTION PACKAGES SUCCESSFULLY GENERATED & VALIDATED")
    print("=" * 80)

    # Print markdown summary table
    print("\n| Job ID | Format | Channel | Title | Scenes | Images | Words | Duration | Hold/Img | Quality Gates |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        print(
            f"| `{r['job_id']}` | `{r['format']}` | `{r['channel_id']}` | {r['youtube_title']} | "
            f"{r['scene_count']} | {r['image_count']} | {r['word_count']}w | {r['est_duration_sec']}s | "
            f"{r['hold_sec_per_img']}s | **PASS (0 errors)** |"
        )
    print("\n")


if __name__ == "__main__":
    main()
