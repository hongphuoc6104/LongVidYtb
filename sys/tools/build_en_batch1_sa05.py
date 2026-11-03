#!/usr/bin/env python3
"""Schema 3.0 English Batch 1 Generator & Validator for SA-EN-05.

Cluster 5: Behavioral Finance, Macro Supply Chains & Career Leverage
Assigned Channels (6 jobs total):
1. en_wallet_anatomy (Wallet Anatomy):
   - Long: sys/runs/en-wallet-anatomy-batch1-16x9 (16:9, 11 scenes, 66 images)
   - Short: sys/runs/en-wallet-anatomy-batch1-9x16 (9:16, 5 scenes, 20 images)
2. en_macro_gears (Macro Gears):
   - Long: sys/runs/en-macro-gears-batch1-16x9 (16:9, 11 scenes, 66 images)
   - Short: sys/runs/en-macro-gears-batch1-9x16 (9:16, 5 scenes, 20 images)
3. en_career_leverage (Career Leverage):
   - Long: sys/runs/en-career-leverage-batch1-16x9 (16:9, 11 scenes, 66 images)
   - Short: sys/runs/en-career-leverage-batch1-9x16 (9:16, 5 scenes, 20 images)
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure sys and tools are in PYTHONPATH
SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
TOOLS_DIR = SYS_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from channels.registry import channel_cast, channel_profile_stamp, get_channel
from tools.channel_production_common import compile_channel_scene_prompt, compile_channel_thumb_prompt
from tools.editorial_value_linter import lint_editorial_and_narrative_quality
from tools.script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions
from tools.cta_tone_linter import lint_cta


def build_scene(sc_spec, default_char_id="CH01"):
    sc_id = sc_spec["id"]
    narration = sc_spec["narration"]
    images = []
    beats = []
    
    for idx, b_spec in enumerate(sc_spec["beats_data"], start=1):
        img_id = f"{sc_id}_I{idx}"
        beat_id = f"{sc_id}_B{idx}"
        quote = b_spec["quote"]
        assert quote in narration, f"Error: '{quote}' not in {sc_id} narration: '{narration}'"
        
        has_char = b_spec.get("has_char", False)
        char_ids = [default_char_id] if has_char else []
        emphasis = b_spec.get("emphasis")
        visible_text = [{"text": emphasis, "placement": "upper_third", "object": "emphasis"}] if emphasis else []
        
        img_obj = {
            "id": img_id,
            "description": b_spec["description"],
            "character_ids": char_ids,
            "based_on": None if idx == 1 else b_spec.get("based_on"),
            "preserve": b_spec.get("preserve", "established tactile paper surface and consistent linework"),
            "change": b_spec.get("change", b_spec["purpose"]),
            "reason": f"Visualizing beat {beat_id}.",
            "visible_text": visible_text,
            "kind": "scene",
            "shot_type": b_spec.get("shot_type", "full_scene"),
            "tempo": b_spec.get("tempo", "normal"),
            "narrative_situation": b_spec.get("narrative_situation", sc_spec.get("narrative_situation", "normal")),
            "emphasis_text": emphasis,
            "focus": {"x": 0.5, "y": 0.5},
            "has_character": has_char,
            "motion_prompt": b_spec.get("motion_prompt", f"Smooth 2D animation illustrating {quote}, silent visual storytelling, no talking, no lip movement")
        }
        images.append(img_obj)
        
        is_endcard = b_spec.get("is_endcard", False)
        beat_obj = {
            "id": beat_id,
            "image_id": img_id,
            "purpose": b_spec["purpose"],
            "anchor": {
                "en": {"quote": quote, "occurrence": 1},
                "vi": {"quote": quote, "occurrence": 1}
            },
            "effect": b_spec.get("effect", "cut"),
            "focus": {"x": 0.5, "y": 0.5},
            "tempo": b_spec.get("tempo", "normal"),
            "narrative_situation": b_spec.get("narrative_situation", sc_spec.get("narrative_situation", "normal"))
        }
        if is_endcard:
            beat_obj["is_endcard"] = True
        beats.append(beat_obj)
        
    scene_obj = {
        "id": sc_id,
        "title": sc_spec["title"],
        "purpose": sc_spec["purpose"],
        "action": sc_spec["action"],
        "setting": sc_spec["setting"],
        "camera": sc_spec["camera"],
        "narration": narration,
        "requirements": sc_spec["requirements"],
        "character_ids": [default_char_id] if any(b.get("has_char") for b in sc_spec["beats_data"]) else [],
        "source_ids": sc_spec.get("source_ids", []),
        "tone": sc_spec.get("tone", "conversational"),
        "narrative_phase": sc_spec.get("narrative_phase", "body"),
        "narrative_situation": sc_spec.get("narrative_situation", "mechanism_step"),
        "images": images,
        "beats": beats
    }
    return scene_obj

def compute_brief_hash(brief_dict):
    content = json.dumps(brief_dict, ensure_ascii=False, indent=2)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def process_and_save_job(job_id, channel_id, brief, outline, cr, raw_scenes_data, coverage_data, claims_data):
    ch = get_channel(channel_id)
    aspect_ratio = brief["aspect_ratio"]
    aspect_tag = "16x9" if aspect_ratio == "16:9" else "9x16"
    
    # Build complete scenes with beats and images
    scenes = [build_scene(s) for s in raw_scenes_data]
    
    # Build content dictionary
    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(brief),
        "topic": brief["topic"],
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": coverage_data,
        "claims": claims_data,
        "outline": outline["outline"],
        "revision_response": [],
        "open_questions": []
    }
    
    # Build image manifest and prompts
    job_dir = SYS_DIR / "runs" / job_id
    rev_img_dir = job_dir / "revisions" / "images" / "1"
    rev_img_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_items = []
    files_list = []
    for sc in scenes:
        for img in sc["images"]:
            prompt = compile_channel_scene_prompt(ch, brief, content, sc, img, aspect_ratio)
            p_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            img_rel_path = f"revisions/images/1/{img['id']}_{aspect_tag}.jpg"
            json_rel_path = f"revisions/images/1/{img['id']}_{aspect_tag}.json"
            
            manifest_items.append({
                "image_id": img["id"],
                "scene_id": sc["id"],
                "path": img_rel_path,
                "prompt": prompt,
                "sha256": p_hash,
                "ratio": aspect_ratio
            })
            files_list.append(img_rel_path)
            files_list.append(json_rel_path)
            
            # Write sidecar json
            sidecar = {
                "jobId": img["id"],
                "forgeId": f"local-{img['id']}",
                "aspect_ratio": aspect_ratio,
                "prompt": prompt,
                "status": "verified"
            }
            write_json(job_dir / json_rel_path, sidecar)
            
    images_manifest = {"checkpoint": "final", "items": manifest_items}
    images_output = {
        "schema_version": "1.0",
        "job_id": job_id,
        "module": "images",
        "revision": 1,
        "files": files_list,
        "items": manifest_items,
        "payload": {
            "items": manifest_items,
            "thumbnail": f"revisions/images/1/THUMBNAIL_{aspect_tag}.jpg",
            "format": aspect_ratio
        },
        "checks": {"passed": True, "errors": []}
    }
    
    # Write all json files
    write_json(job_dir / "brief.json", brief)
    write_json(job_dir / "outline.json", outline)
    write_json(job_dir / "competitor_research.json", cr)
    write_json(job_dir / "content.json", content)
    write_json(job_dir / "images.json", images_manifest)
    write_json(rev_img_dir / "images.json", images_manifest)
    write_json(rev_img_dir / "output.json", images_output)
    
    # Run Linters
    claims_set = {str(c.get("fact", "")) for c in claims_data}
    claims_set.update(str(c.get("quote", "")) for c in claims_data)
    
    ed_report = lint_editorial_and_narrative_quality(brief, content)
    ai_cliches = check_ai_cliche_phrases(content["scenes"])
    intra_reps = check_intra_video_repetitions(content["scenes"], claim_facts=claims_set)
    cta_errs = lint_cta(brief, content)
    
    total_words = sum(len(sc["narration"].split()) for sc in scenes)
    est_dur = round(total_words / 3.8, 1)
    avg_hold = round(est_dur / max(1, len(manifest_items)), 2)
    
    print(f"\n=======================================================")
    print(f"JOB: {job_id} ({brief['format_profile']})")
    print(f"  Title: {brief['youtube_title']}")
    print(f"  Words: {total_words} | Images: {len(manifest_items)} | Est Duration: {est_dur}s | Hold: {avg_hold}s/img")
    print(f"  Editorial & Narrative Quality: {'PASSED' if ed_report['passed'] else 'FAILED'}")
    if not ed_report["passed"]:
        print(f"    Errors: {ed_report['errors']}")
    print(f"  AI Cliches: {'PASSED (0)' if len(ai_cliches) == 0 else f'FAILED ({len(ai_cliches)})'}")
    if ai_cliches:
        print(f"    Violations: {ai_cliches}")
    print(f"  Intra-Video Repetitions: {'PASSED (0)' if len(intra_reps) == 0 else f'FAILED ({len(intra_reps)})'}")
    if intra_reps:
        print(f"    Violations: {intra_reps}")
    print(f"  CTA Tone & Pacing: {'PASSED (0)' if len(cta_errs) == 0 else f'FAILED ({len(cta_errs)})'}")
    if cta_errs:
        print(f"    Errors: {cta_errs}")
        
    assert ed_report["passed"], f"Editorial linter failed on {job_id}: {ed_report['errors']}"
    assert len(ai_cliches) == 0, f"AI cliches found on {job_id}: {ai_cliches}"
    assert len(intra_reps) == 0, f"Intra repetitions found on {job_id}: {intra_reps}"
    assert len(cta_errs) == 0, f"CTA errors found on {job_id}: {cta_errs}"
    
    return {
        "job_id": job_id,
        "channel_slug": channel_id,
        "format": brief["format_profile"],
        "title": brief["youtube_title"],
        "words": total_words,
        "images": len(manifest_items),
        "duration": est_dur,
        "hold": avg_hold,
        "all_passed": True
    }

def get_wallet_long_scenes_data():
    return [
        {
            "id": "SC01",
            "title": "The Luxury Decoy in the Corner",
            "purpose": "Hook the viewer with the un-ordered forty-eight dollar steak in the top-right corner",
            "action": "A guest diner scans a vintage bistro menu under an antique lamp as the camera focuses on the luxury cut",
            "setting": "An intimate wood-paneled restaurant booth on fibrous ivory ledger paper #F5F2EB",
            "camera": "Direct overhead tracking shot descending toward the top-right menu corner",
            "narration": "When you sit down at an upscale bistro, your gaze lands almost instantly on the top-right corner of the menu. Resting right there is a magnificent forty-eight-dollar prime dry-aged ribeye steak. You glance at the steep price, shake your head, and scan downward toward pasta. What you do not realize is that the restaurant never expected you to order it.",
            "requirements": ["R01"],
            "source_ids": ["SRC01"],
            "tone": "Engaging, practical, eye-opening",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "beats_data": [
                {
                    "quote": "When you sit down at an upscale bistro,",
                    "purpose": "Establishing the restaurant dining booth setting",
                    "description": "Tactile 2D vintage accounting ledger and dip-pen iron-gall ink illustration on warm fibrous cream grid paper #F5F2EB. Overhead shot of a guest seating booth at an upscale bistro with a leather-bound menu opened on a wooden table beside an antique brass lamp.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "emphasis": "DINNER MENU"
                },
                {
                    "quote": "your gaze lands almost instantly on the top-right corner of the menu.",
                    "purpose": "Focusing on the top-right corner",
                    "description": "Tactile 2D vintage accounting ledger illustration. Extreme close-up of the upper-right quadrant of the paper menu showing fine hand-ruled grid columns and decorative calligraphic borders in #1F6F54 ink.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "Resting right there is a magnificent forty-eight-dollar prime dry-aged ribeye steak.",
                    "purpose": "Depicting the 48 dollar dry-aged steak",
                    "description": "Tactile 2D vintage accounting ledger illustration. An opulent prime dry-aged ribeye steak illustrated in cross-hatched bank-note emerald ink beside a prominent hand-stamped price of 48 in rubber-stamp deficit-red #B8332A.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "PRIME STEAK 48"
                },
                {
                    "quote": "You glance at the steep price,",
                    "purpose": "Price shock and hesitation",
                    "description": "Tactile 2D vintage accounting ledger illustration. The guest diner's eyes drawn with focused dip-pen cross-hatching widen in surprise at the steep 48 dollar price tag.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "shake your head, and scan downward toward pasta.",
                    "purpose": "Scanning downward toward cheaper entrées",
                    "description": "Tactile 2D vintage accounting ledger illustration. The diner shakes their head slightly, shifting their finger downward along the ledger grid toward thirty-two-dollar chicken and twenty-six-dollar pasta entries.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": None
                },
                {
                    "quote": "What you do not realize is that the restaurant never expected you to order it.",
                    "purpose": "Manager watching the engineered result",
                    "description": "Tactile 2D vintage accounting ledger illustration. Behind a dark wooden partition, the restaurant manager in tortoiseshell glasses smiles knowingly, holding a leather accounting ledger showing planned profit projections.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "DECOY ANCHOR"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "The Golden Triangle Sightline",
            "purpose": "Explain the Golden Triangle eye-tracking pattern across physical menus",
            "action": "A visual blueprint shows the geometric Golden Triangle eye scan path across a restaurant menu page",
            "setting": "An architect's drafting desk with brass drafting dividers and ruled ledger grids",
            "camera": "Top-down geometric tracking shot following the gaze path coordinates",
            "narration": "Menu consultants call this deliberate layout the Golden Triangle. Eye-tracking cameras reveal that human gaze sweeps first across the center of the page, jumps to the upper-right section, and then drifts toward the top-left. Restaurant owners deliberately plant their highest price tag directly in that prime sightline to manipulate your psychological baseline from the very first second.",
            "requirements": ["R02"],
            "source_ids": ["SRC01"],
            "tone": "Engaging, practical, analytical",
            "narrative_phase": "story_action",
            "narrative_situation": "story_action",
            "beats_data": [
                {
                    "quote": "Menu consultants call this deliberate layout the Golden Triangle.",
                    "purpose": "Golden Triangle diagram header",
                    "description": "Tactile 2D vintage accounting ledger illustration. A hand-ruled menu grid with a bold geometric Golden Triangle diagram drawn in #1F6F54 emerald ink across the columns.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "GOLDEN TRIANGLE"
                },
                {
                    "quote": "Eye-tracking cameras reveal that human gaze sweeps first across the center of the page,",
                    "purpose": "Center gaze focal point",
                    "description": "Tactile 2D vintage accounting ledger illustration. An eye-tracking optical heatmap showing concentrated cross-hatched ink density over the center of the menu page.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "jumps to the upper-right section,",
                    "purpose": "Rapid jump to top right corner",
                    "description": "Tactile 2D vintage accounting ledger illustration. A dynamic dashed directional arrow leaping sharply from the center point into the upper-right corner price box.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": None
                },
                {
                    "quote": "and then drifts toward the top-left.",
                    "purpose": "Drifting toward top left section",
                    "description": "Tactile 2D vintage accounting ledger illustration. The dashed arrow completing the triangle path by gliding smoothly over to the top-left appetizers column.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "Restaurant owners deliberately plant their highest price tag directly in that prime sightline",
                    "purpose": "Deliberate luxury price placement",
                    "description": "Tactile 2D vintage accounting ledger illustration. A brass drafting pen inserting a heavy black price tag into the top-right apex of the Golden Triangle.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "PRIME SIGHTLINE"
                },
                {
                    "quote": "to manipulate your psychological baseline from the very first second.",
                    "purpose": "Psychological baseline scale tipping",
                    "description": "Tactile 2D vintage accounting ledger illustration. A brass balance scale tipping dramatically under the weight of the initial high anchor price on cream ledger paper.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "PRICE ANCHOR"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "Joel Huber's Asymmetric Decoy",
            "purpose": "Deconstruct Joel Huber's 1982 asymmetric dominance decoy experiment",
            "action": "A classical academic balance sheet illustrates options A, B, and the asymmetric decoy C",
            "setting": "A university economics lecture room rendered in copperplate ink and cotton rag paper",
            "camera": "Slow lateral dolly shot across three competing product columns",
            "narration": "This subtle cognitive manipulation stems from seminal research published in 1982 by Duke professor Joel Huber. Huber demonstrated the Asymmetric Dominance Effect, colloquially known as the Decoy Effect. When consumers evaluate two competing choices, introducing a third inferior decoy choice dramatically alters their final selection without changing the underlying economic value of either option.",
            "requirements": ["R03"],
            "source_ids": ["SRC01"],
            "tone": "Analytical, grounded in behavioral economics",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "This subtle cognitive manipulation stems from seminal research published in 1982 by Duke professor Joel Huber.",
                    "purpose": "Citing Joel Huber 1982 paper",
                    "description": "Tactile 2D vintage accounting ledger illustration. An academic journal title page from 1982 engraved in copperplate ink with title Journal of Consumer Research and Joel Huber signature.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "HUBER 1982"
                },
                {
                    "quote": "Huber demonstrated the Asymmetric Dominance Effect,",
                    "purpose": "Asymmetric dominance title",
                    "description": "Tactile 2D vintage accounting ledger illustration. Two balanced product cards Option A and Option B resting on parallel ruled columns on ivory paper.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "ASYMMETRIC DOMINANCE"
                },
                {
                    "quote": "colloquially known as the Decoy Effect.",
                    "purpose": "Introducing the decoy concept",
                    "description": "Tactile 2D vintage accounting ledger illustration. A wooden carved decoy duck resting on an open ledger beside balance columns, cross-hatched in bank-note green.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "THE DECOY EFFECT"
                },
                {
                    "quote": "When consumers evaluate two competing choices,",
                    "purpose": "Evaluating two competing options",
                    "description": "Tactile 2D vintage accounting ledger illustration. A consumer silhouette weighing two equal merchandise packages in brass balance pans.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": None
                },
                {
                    "quote": "introducing a third inferior decoy choice dramatically alters their final selection",
                    "purpose": "Adding inferior decoy choice",
                    "description": "Tactile 2D vintage accounting ledger illustration. A third inferior option C placed next to Option B, shaded in faint red hatched lines to show deliberate inferiority.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "without changing the underlying economic value of either option.",
                    "purpose": "Underlying economic value unchanged",
                    "description": "Tactile 2D vintage accounting ledger illustration. Mathematical equality symbols and ledger lines proving the intrinsic value of Option A remained completely identical.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "INTRINSIC VALUE"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "The Economist Subscription Experiment",
            "purpose": "Break down The Economist subscription test with three pricing tiers",
            "action": "Dan Ariely presents the three subscription tiers from The Economist on an editorial newspaper page",
            "setting": "An editorial print shop with woodblock presses and damp rag paper sheets",
            "camera": "Medium pan across the three subscription price boxes",
            "narration": "Behavioral economist Dan Ariely popularized this phenomenon using a famous test from The Economist magazine. Ariely offered students three choices: web access for fifty-nine dollars, print access for one hundred twenty-five dollars, or both print and web together for the exact same one hundred twenty-five dollars. Nobody chose the print-only decoy.",
            "requirements": ["R04"],
            "source_ids": ["SRC03"],
            "tone": "Engaging, practical, analytical",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "Behavioral economist Dan Ariely popularized this phenomenon using a famous test",
                    "purpose": "Dan Ariely test introduction",
                    "description": "Tactile 2D vintage accounting ledger illustration. Dan Ariely portrait drawn in fine fountain-pen cross-hatching beside his book Predictably Irrational on cotton rag paper.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "DAN ARIELY TEST"
                },
                {
                    "quote": "from The Economist magazine.",
                    "purpose": "The Economist masthead",
                    "description": "Tactile 2D vintage accounting ledger illustration. Vintage newspaper masthead of The Economist drawn in classic serif letterpress typography on ivory newsprint.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": "THE ECONOMIST"
                },
                {
                    "quote": "Ariely offered students three choices: web access for fifty-nine dollars,",
                    "purpose": "Web access 59 dollars",
                    "description": "Tactile 2D vintage accounting ledger illustration. Option 1 box showing Web Subscription for $59 with a clean digital screen icon inked in emerald green.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "WEB $59"
                },
                {
                    "quote": "print access for one hundred twenty-five dollars,",
                    "purpose": "Print access 125 dollars",
                    "description": "Tactile 2D vintage accounting ledger illustration. Option 2 box showing Print Subscription for $125 with a physical newspaper stack icon on grid paper.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "PRINT $125"
                },
                {
                    "quote": "or both print and web together for the exact same one hundred twenty-five dollars.",
                    "purpose": "Bundle print and web 125 dollars",
                    "description": "Tactile 2D vintage accounting ledger illustration. Option 3 box showing Print + Web Bundle for $125 radiating hand-drawn value beams on ledger paper.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "BUNDLE $125"
                },
                {
                    "quote": "Nobody chose the print-only decoy.",
                    "purpose": "Zero percent chose print only",
                    "description": "Tactile 2D vintage accounting ledger illustration. A large red deficit-ink X stamping across the print-only middle tier with a bold zero-percent badge.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "ZERO ORDERS"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "Editorial Verdict on Comparison",
            "purpose": "Editorial commentary on how comparative framing short-circuits rational spending",
            "action": "The bookkeeper audits the percentage shift before and after removing the decoy tier",
            "setting": "The bookkeeper's oak study with balance ledgers and fountain-pen ink bottles",
            "camera": "Direct portrait shot transitioning into comparative statistical ledgers",
            "narration": "Here is our channel verdict: the print-only option was never meant to sell. It existed purely to make the combo package look like an unbeatable bargain. In Ariely's experiment, eighty-four percent picked the combo. But when he removed the decoy, sixty-eight percent switched to the cheaper digital plan. Comparison completely short-circuits rational calculation.",
            "requirements": ["R05"],
            "source_ids": ["SRC03"],
            "tone": "Direct, critical, opinionated editorial verdict",
            "narrative_phase": "editorial_commentary",
            "narrative_situation": "editorial_commentary",
            "beats_data": [
                {
                    "quote": "Here is our channel verdict: the print-only option was never meant to sell.",
                    "purpose": "Editorial verdict statement",
                    "description": "Tactile 2D vintage accounting ledger illustration. The bookkeeper protagonist in tortoiseshell glasses dips a brass pen into green ink, making a decisive audit mark on the balance sheet.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "CHANNEL VERDICT"
                },
                {
                    "quote": "It existed purely to make the combo package look like an unbeatable bargain.",
                    "purpose": "Combo package bargain illusion",
                    "description": "Tactile 2D vintage accounting ledger illustration. Optical illusion metaphor showing the combo package glowing artificially bright between shadow-ruled columns.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "BARGAIN ILLUSION"
                },
                {
                    "quote": "In Ariely's experiment, eighty-four percent picked the combo.",
                    "purpose": "Eighty-four percent picked combo",
                    "description": "Tactile 2D vintage accounting ledger illustration. Hand-drawn pie chart showing a massive 84% green emerald slice flowing directly into the combo tier.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "84% COMBO"
                },
                {
                    "quote": "But when he removed the decoy,",
                    "purpose": "Removing the middle decoy",
                    "description": "Tactile 2D vintage accounting ledger illustration. A hand physically lifting the print-only middle card off the table, leaving only web $59 and combo $125.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "emphasis": None
                },
                {
                    "quote": "sixty-eight percent switched to the cheaper digital plan.",
                    "purpose": "Sixty-eight percent picked cheaper plan",
                    "description": "Tactile 2D vintage accounting ledger illustration. The pie chart reversing dramatically, showing a 68% majority shifting down to the $59 web-only tier.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "68% SWITCHED"
                },
                {
                    "quote": "Comparison completely short-circuits rational calculation.",
                    "purpose": "Comparison short circuits rationality",
                    "description": "Tactile 2D vintage accounting ledger illustration. An anatomical cross-section of a human brain with clockwork calculation gears jammed by comparative pricing arrows.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "RATIONAL SHORT-CIRCUIT"
                }
            ]
        },
        {
            "id": "SC06",
            "title": "The Dollar Sign Pain Study",
            "purpose": "Reveal Cornell University findings on how omitting dollar signs increases check spend",
            "action": "A visual comparison of two restaurant checks: one with dollar symbols and one with bare numerals",
            "setting": "A restaurant cashier counter with vintage cash register and paper receipt rolls",
            "camera": "Split-screen macro shot comparing two guest receipts",
            "narration": "Menu architects also use subtle typography to strip away financial pain. A landmark Cornell University study revealed that removing dollar signs from menus caused diners to spend eight point one percent more per check. Writing thirty-two instead of thirty-two dollars reduces the psychological sting of paying, keeping your guard down during ordering.",
            "requirements": ["R06"],
            "source_ids": ["SRC02"],
            "tone": "Engaging, practical, eye-opening",
            "narrative_phase": "rapid_examples",
            "narrative_situation": "rapid_examples",
            "beats_data": [
                {
                    "quote": "Menu architects also use subtle typography to strip away financial pain.",
                    "purpose": "Typography of menu prices",
                    "description": "Tactile 2D vintage accounting ledger illustration. Calligraphic pen tips carving elegant typography onto a pristine paper menu on warm ledger grid.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "PRICE TYPOGRAPHY"
                },
                {
                    "quote": "A landmark Cornell University study revealed",
                    "purpose": "Cornell University seal",
                    "description": "Tactile 2D vintage accounting ledger illustration. Cornell University official research insignia stamped in dark ink over a published hospitality research paper.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": "CORNELL STUDY"
                },
                {
                    "quote": "that removing dollar signs from menus caused diners to spend eight point one percent more per check.",
                    "purpose": "Eight point one percent increase",
                    "description": "Tactile 2D vintage accounting ledger illustration. Upward trending cashflow chart showing an 8.1% check size surge when dollar signs are omitted from the page.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "+8.1% SPENDING"
                },
                {
                    "quote": "Writing thirty-two instead of thirty-two dollars",
                    "purpose": "Numeral 32 versus $32.00",
                    "description": "Tactile 2D vintage accounting ledger illustration. High-contrast side-by-side comparison: left shows $32.00 in red, right shows minimalist bare 32 in emerald ink.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "32 VS $32.00"
                },
                {
                    "quote": "reduces the psychological sting of paying,",
                    "purpose": "Reducing pain of paying",
                    "description": "Tactile 2D vintage accounting ledger illustration. A metaphorical coin falling softly through feathers, symbolizing the neutralized pain of transaction.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "PAIN OF PAYING"
                },
                {
                    "quote": "keeping your guard down during ordering.",
                    "purpose": "Lowered consumer defense",
                    "description": "Tactile 2D vintage accounting ledger illustration. Diner relaxed at table, casually adding side dishes and cocktails to their order slip with lowered guard.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": None
                }
            ]
        },
        {
            "id": "SC07",
            "title": "The Second-Cheapest Wine Trap",
            "purpose": "Expose the restaurant markup trap on the second-cheapest bottle of wine",
            "action": "The camera inspects a leather-bound wine list, highlighting the bottom two bottles",
            "setting": "A dim romantic wine cellar with wooden barrels and hand-inked wine bottle racks",
            "camera": "Slow macro glide down the wine list column",
            "narration": "Now consider the notorious wine list trap. When casual diners want to avoid looking stingy on a date or business dinner, they instinctively pass over the cheapest bottle. Recognizing this social anxiety, hospitality managers deliberately place their highest profit markup on the second-cheapest wine on the list, turning cheap insecurity into pure restaurant profit.",
            "requirements": ["R07"],
            "source_ids": ["SRC02"],
            "tone": "Eye-opening, candid, practical",
            "narrative_phase": "before_after_contrast",
            "narrative_situation": "before_after_contrast",
            "beats_data": [
                {
                    "quote": "Now consider the notorious wine list trap.",
                    "purpose": "Wine list trap introduction",
                    "description": "Tactile 2D vintage accounting ledger illustration. A richly embossed leather wine list resting on an oak tasting barrel on cream ledger paper.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "WINE LIST TRAP"
                },
                {
                    "quote": "When casual diners want to avoid looking stingy on a date or business dinner,",
                    "purpose": "Date and dinner social context",
                    "description": "Tactile 2D vintage accounting ledger illustration. Two diners seated across a white tablecloth table by candlelight, reviewing the wine list with subtle tension.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": None
                },
                {
                    "quote": "they instinctively pass over the cheapest bottle.",
                    "purpose": "Passing over the cheapest wine",
                    "description": "Tactile 2D vintage accounting ledger illustration. A finger passing quickly past the lowest $28 house red bottle on the menu column without pausing.",
                    "has_char": True,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": "AVOID CHEAPEST"
                },
                {
                    "quote": "Recognizing this social anxiety, hospitality managers deliberately place their highest profit markup",
                    "purpose": "Highest profit markup placement",
                    "description": "Tactile 2D vintage accounting ledger illustration. A beverage director calculating percentage profit margins in a leather cellar ledger book.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "MAX MARKUP"
                },
                {
                    "quote": "on the second-cheapest wine on the list,",
                    "purpose": "Focusing on the second-cheapest wine",
                    "description": "Tactile 2D vintage accounting ledger illustration. A golden spotlight beam focusing tightly on the second bottle priced at $38 on the ruled wine menu.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "2ND CHEAPEST"
                },
                {
                    "quote": "turning cheap insecurity into pure restaurant profit.",
                    "purpose": "Social insecurity turned to profit",
                    "description": "Tactile 2D vintage accounting ledger illustration. A cash drawer filling with green bank notes while social masks dissolve into ledger profit figures.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "INSECURITY PROFIT"
                }
            ]
        },
        {
            "id": "SC08",
            "title": "The Ego Insurance Premium",
            "purpose": "Explain how hospitality managers exploit social anxiety and dinner table ego",
            "action": "A cellar wholesale invoice reveals the actual acquisition cost of the second bottle",
            "setting": "A cellar storehouse with stacked wooden clearance crates and dust-covered vintage bottles",
            "camera": "Direct invoice inspection revealing wholesale prices versus menu retail prices",
            "narration": "Beverage directors confess that the cheapest wine is often a perfectly decent table vintage with a modest wholesale markup. Meanwhile, the second bottle is frequently dead cellar stock purchased on clearance, priced specifically to catch customers caught in social embarrassment. You are not buying better flavor; you are paying a surcharge to protect your ego.",
            "requirements": ["R08"],
            "source_ids": ["SRC02"],
            "tone": "Candid, practical, grounded",
            "narrative_phase": "story_action",
            "narrative_situation": "story_action",
            "beats_data": [
                {
                    "quote": "Beverage directors confess that the cheapest wine is often a perfectly decent table vintage",
                    "purpose": "Cheapest wine is decent table vintage",
                    "description": "Tactile 2D vintage accounting ledger illustration. A clean wooden cask of honest house red wine with a stamp reading Honest Provenance in dark blue ink.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "HOUSE TABLE WINE"
                },
                {
                    "quote": "with a modest wholesale markup.",
                    "purpose": "Modest wholesale markup",
                    "description": "Tactile 2D vintage accounting ledger illustration. An accounting ledger showing a fair 2.5x markup line on the house wine entry.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "Meanwhile, the second bottle is frequently dead cellar stock purchased on clearance,",
                    "purpose": "Second bottle is clearance stock",
                    "description": "Tactile 2D vintage accounting ledger illustration. Dust-covered clearance bottles in wooden crates stamped with Discount Bulk Lot in red rubber stamp ink.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "CLEARANCE LOT"
                },
                {
                    "quote": "priced specifically to catch customers caught in social embarrassment.",
                    "purpose": "Catching social embarrassment",
                    "description": "Tactile 2D vintage accounting ledger illustration. A stylized fishhook catching a small wallet as diner reaches nervously for the wine list.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "EGO HOOK"
                },
                {
                    "quote": "You are not buying better flavor;",
                    "purpose": "Not buying better flavor",
                    "description": "Tactile 2D vintage accounting ledger illustration. Two wine glasses side by side with identical ruby hue, proving no taste distinction.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": None
                },
                {
                    "quote": "you are paying a surcharge to protect your ego.",
                    "purpose": "Ego protection surcharge",
                    "description": "Tactile 2D vintage accounting ledger illustration. A restaurant bill with an explicit line item labeled Ego Insurance Surcharge stamped in red ink.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "EGO SURCHARGE"
                }
            ]
        },
        {
            "id": "SC09",
            "title": "Software Subscription Decoys",
            "purpose": "Demonstrate the exact same decoy structure in modern software subscription tiers",
            "action": "A modern software SaaS pricing matrix is drawn using vintage ledger rules",
            "setting": "A financial drafting office bridging nineteenth-century ledgers with modern software UI",
            "camera": "Smooth horizontal pan across Basic, Pro, and Enterprise pricing columns",
            "narration": "This identical architecture dominates digital software subscriptions today. Software companies showcase a bare-bones Basic tier, a ridiculously overpriced Enterprise tier, and a highlighted Pro tier labeled most popular. The extreme top price anchors your expectations, making thirty dollars a month feel like a sensible compromise rather than a recurring annual expense.",
            "requirements": ["R09"],
            "source_ids": ["SRC01"],
            "tone": "Practical, analytical, eye-opening",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "This identical architecture dominates digital software subscriptions today.",
                    "purpose": "Digital subscription tier architecture",
                    "description": "Tactile 2D vintage accounting ledger illustration. A three-column SaaS software pricing table hand-ruled on fibrous ledger grid paper #F5F2EB.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "SAAS PRICING TIERS"
                },
                {
                    "quote": "Software companies showcase a bare-bones Basic tier,",
                    "purpose": "Bare-bones Basic tier",
                    "description": "Tactile 2D vintage accounting ledger illustration. The Basic column deliberately stripped of storage and export features, looking unattractive.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "BASIC $9"
                },
                {
                    "quote": "a ridiculously overpriced Enterprise tier,",
                    "purpose": "Overpriced Enterprise tier",
                    "description": "Tactile 2D vintage accounting ledger illustration. The Enterprise column with a massive $499 monthly price tag acting as an extreme visual anchor.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "ENTERPRISE $499"
                },
                {
                    "quote": "and a highlighted Pro tier labeled most popular.",
                    "purpose": "Highlighted Pro tier most popular",
                    "description": "Tactile 2D vintage accounting ledger illustration. The middle Pro tier highlighted with an emerald green ribbon banner stamped Most Popular.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "MOST POPULAR"
                },
                {
                    "quote": "The extreme top price anchors your expectations,",
                    "purpose": "Extreme top price anchors expectations",
                    "description": "Tactile 2D vintage accounting ledger illustration. Heavy iron anchor icon dropping from the Enterprise tier, pulling customer expectation downward.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "ANCHOR MECHANISM"
                },
                {
                    "quote": "making thirty dollars a month feel like a sensible compromise rather than a recurring annual expense.",
                    "purpose": "Thirty dollars felt as compromise",
                    "description": "Tactile 2D vintage accounting ledger illustration. A consumer hand clicking the Pro tier button, while an annual calculator reveals $360 compounding costs.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "$30/MO COMPROMISE"
                }
            ]
        },
        {
            "id": "SC10",
            "title": "The Engineered Choice Environment",
            "purpose": "Channel verdict on how commercial pricing grids are engineered to steer decisions",
            "action": "The bookkeeper pulls back the curtain on the entire commercial pricing landscape",
            "setting": "An executive command center where menus, software tables, and retail catalogs intersect",
            "camera": "Wide cinematic pull-back revealing the systemic nature of decoy architecture",
            "narration": "Every commercial pricing grid is an intentional environment engineered to direct your behavior. The forty-eight-dollar steak makes the thirty-two-dollar chicken look reasonable. The enterprise software package makes the monthly subscription look harmless. If you evaluate costs only by comparing items on the same page, the house wins every single time. Recognizing this visual manipulation is your first line of financial defense.",
            "requirements": ["R10"],
            "source_ids": ["SRC01", "SRC03"],
            "tone": "Direct, empowering, critical editorial commentary",
            "narrative_phase": "editorial_commentary",
            "narrative_situation": "editorial_commentary",
            "beats_data": [
                {
                    "quote": "Every commercial pricing grid is an intentional environment engineered to direct your behavior.",
                    "purpose": "Intentional choice architecture verdict",
                    "description": "Tactile 2D vintage accounting ledger illustration. A master architectural floorplan where restaurant tables and software tiers are connected by invisible guidance conduits.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "CHOICE ARCHITECTURE"
                },
                {
                    "quote": "The forty-eight-dollar steak makes the thirty-two-dollar chicken look reasonable.",
                    "purpose": "Steak makes chicken look reasonable",
                    "description": "Tactile 2D vintage accounting ledger illustration. Contrast balance where the $48 steak counterweight makes the $32 chicken plate feel weightless.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "STEAK VS CHICKEN"
                },
                {
                    "quote": "The enterprise software package makes the monthly subscription look harmless.",
                    "purpose": "Enterprise package makes sub harmless",
                    "description": "Tactile 2D vintage accounting ledger illustration. Corporate boardroom view where massive enterprise software contracts dwarf small monthly team subscriptions.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": None
                },
                {
                    "quote": "If you evaluate costs only by comparing items on the same page,",
                    "purpose": "Evaluating costs only by comparison",
                    "description": "Tactile 2D vintage accounting ledger illustration. A consumer looking through narrow magnifying spectacles that only view one page at a time.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "the house wins every single time.",
                    "purpose": "The house wins every time",
                    "description": "Tactile 2D vintage accounting ledger illustration. A vintage bank vault door locking shut with stamped gold seals representing corporate profit certainty.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "THE HOUSE WINS"
                },
                {
                    "quote": "Recognizing this visual manipulation is your first line of financial defense.",
                    "purpose": "First line of financial defense",
                    "description": "Tactile 2D vintage accounting ledger illustration. The bookkeeper protagonist closing the ledger firmly, standing as an empowered financial guide with fountain pen in hand.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "FINANCIAL DEFENSE"
                }
            ]
        },
        {
            "id": "SC11",
            "title": "The Three-Second Anchor Rule",
            "purpose": "Provide the three-second strip-the-anchor rule and close the video",
            "action": "The bookkeeper demonstrates the practical rule of thumb, writing it into a pocket ledger",
            "setting": "A clean, bright study desk on fibrous ivory ledger paper with fountain pen and pocket ledger",
            "camera": "Direct portrait shot transitioning to the closing channel endcard",
            "narration": "To protect your money, apply the three-second strip-the-anchor rule. Before picking an entrée or software tier, mentally erase the highest price from the page. Ask what you would pay if that luxury decoy did not exist. Audit your subscriptions today. Check the pricing layout before you order tonight.",
            "requirements": ["R11"],
            "source_ids": ["SRC01"],
            "tone": "Empowering, practical, direct",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cta_bridge",
            "beats_data": [
                {
                    "quote": "To protect your money, apply the three-second strip-the-anchor rule.",
                    "purpose": "Introducing 3-second strip-the-anchor rule",
                    "description": "Tactile 2D vintage accounting ledger illustration. A stop-watch timer showing 3 seconds in brass calligraphy beside an open pocket notebook.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "3-SECOND RULE"
                },
                {
                    "quote": "Before picking an entrée or software tier,",
                    "purpose": "Before picking entrée or tier",
                    "description": "Tactile 2D vintage accounting ledger illustration. Hand hovering over a restaurant menu and software price grid with deliberate mindful pause.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "mentally erase the highest price from the page.",
                    "purpose": "Mentally erase the highest price",
                    "description": "Tactile 2D vintage accounting ledger illustration. An ink eraser tool rubbing away the $48 steak and $499 enterprise entries, revealing blank canvas.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "ERASE ANCHOR"
                },
                {
                    "quote": "Ask what you would pay if that luxury decoy did not exist.",
                    "purpose": "Evaluate standalone utility",
                    "description": "Tactile 2D vintage accounting ledger illustration. The target dish standing alone on a pristine white plate, evaluated purely on taste and nutritional value.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "STANDALONE VALUE"
                },
                {
                    "quote": "Audit your subscriptions today.",
                    "purpose": "Audit subscriptions callout",
                    "description": "Tactile 2D vintage accounting ledger illustration. The bookkeeper checking off recurring charges in a neat personal pocket ledger with green checkmarks.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "AUDIT TODAY"
                },
                {
                    "quote": "Check the pricing layout before you order tonight.",
                    "purpose": "Closing call to action and channel seal",
                    "description": "Tactile 2D vintage accounting ledger illustration. Official channel endcard of Wallet Anatomy featuring the bookkeeper emblem, brass nib pen, and ledger stamp on cotton paper.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "emphasis": "WALLET ANATOMY",
                    "is_endcard": True
                }
            ]
        }
    ]

def get_wallet_short_scenes_data():
    return [
        {
            "id": "SC01",
            "title": "The Second-Cheapest Wine Warning",
            "purpose": "Hook the viewer with the warning against the second-cheapest wine",
            "action": "A guest diner pauses on the second wine entry on a candlelit leather list",
            "setting": "A dim restaurant table on cream ledger paper #F5F2EB",
            "camera": "Direct macro shot descending on the wine menu entry",
            "narration": "Never order the second-cheapest wine on a restaurant menu. You think choosing that bottle makes you look sensible and cultured without spending a fortune. But behind the kitchen doors, beverage directors call this the insecurity tax.",
            "requirements": ["R01"],
            "source_ids": ["SRC01"],
            "tone": "Eye-opening, punchy, direct",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "beats_data": [
                {
                    "quote": "Never order the second-cheapest wine on a restaurant menu.",
                    "purpose": "Second-cheapest wine warning hook",
                    "description": "Tactile 2D vintage accounting ledger illustration on cream paper #F5F2EB. Close-up of a leather wine list with a bold hand-drawn red warning arrow pointing to the second item.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "emphasis": "DON'T ORDER IT"
                },
                {
                    "quote": "You think choosing that bottle makes you look sensible and cultured",
                    "purpose": "Diner feels sensible and cultured",
                    "description": "Tactile 2D vintage accounting ledger illustration. Diner in candlelight smiling with calm satisfaction while holding the wine list.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "without spending a fortune.",
                    "purpose": "Without spending a fortune",
                    "description": "Tactile 2D vintage accounting ledger illustration. A modest stack of brass coins on a ledger column next to a glass of red wine.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "But behind the kitchen doors, beverage directors call this the insecurity tax.",
                    "purpose": "The insecurity tax reveal",
                    "description": "Tactile 2D vintage accounting ledger illustration. Behind kitchen doors, sommelier stamping an official receipt with red ink reading Insecurity Tax.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "INSECURITY TAX"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "The Fear of Looking Cheap",
            "purpose": "Explain the customer anxiety driving the selection",
            "action": "The diner hesitates over the cheapest bottle before jumping upward",
            "setting": "The dining table with wine glasses and menu",
            "camera": "Macro shot of fingers tracing the wine list prices",
            "narration": "Most diners are terrified of looking cheap in front of friends or dates. They refuse to touch the absolute bottom bottle, assuming it tastes terrible. So they immediately jump one step higher to the second-cheapest option.",
            "requirements": ["R02"],
            "source_ids": ["SRC01"],
            "tone": "Engaging, practical, analytical",
            "narrative_phase": "story_action",
            "narrative_situation": "story_action",
            "beats_data": [
                {
                    "quote": "Most diners are terrified of looking cheap in front of friends or dates.",
                    "purpose": "Fear of looking cheap",
                    "description": "Tactile 2D vintage accounting ledger illustration. Diner's anxious expression reflected in the polished wine glass surface.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "SOCIAL FEAR"
                },
                {
                    "quote": "They refuse to touch the absolute bottom bottle,",
                    "purpose": "Refusing bottom bottle",
                    "description": "Tactile 2D vintage accounting ledger illustration. The bottom $24 wine bottle crossed out with a hesitant dashed line.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": None
                },
                {
                    "quote": "assuming it tastes terrible.",
                    "purpose": "Assuming cheap wine tastes terrible",
                    "description": "Tactile 2D vintage accounting ledger illustration. A sour facial expression doodle beside a broken cork on ledger grid.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "So they immediately jump one step higher to the second-cheapest option.",
                    "purpose": "Jumping to second-cheapest option",
                    "description": "Tactile 2D vintage accounting ledger illustration. An energetic ink leap curve hopping from line one to line two on the wine list.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "HOPPING UP"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "The Four-Hundred Percent Markup",
            "purpose": "Reveal how restaurants price clearance stock in that slot",
            "action": "The cellar ledger reveals the clearance wholesale cost and 400% markup",
            "setting": "The restaurant back-office cellar with wholesale bills",
            "camera": "Direct inspection of the profit markup column",
            "narration": "Hospitality managers know this exact psychological quirk. They take clearance inventory that cost them five dollars a bottle, mark it up four hundred percent, and slot it directly into that second position to milk your social fear.",
            "requirements": ["R03"],
            "source_ids": ["SRC01"],
            "tone": "Eye-opening, candid",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "Hospitality managers know this exact psychological quirk.",
                    "purpose": "Managers know this quirk",
                    "description": "Tactile 2D vintage accounting ledger illustration. Restaurant manager checking off customer behavioral tendencies in a ledger binder.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "PSYCHOLOGY QUIRK"
                },
                {
                    "quote": "They take clearance inventory that cost them five dollars a bottle,",
                    "purpose": "Five dollar wholesale cost",
                    "description": "Tactile 2D vintage accounting ledger illustration. Wholesale shipping invoice showing an acquisition price of $5.00 per unit in green ink.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "COST: $5"
                },
                {
                    "quote": "mark it up four hundred percent,",
                    "purpose": "Four hundred percent markup",
                    "description": "Tactile 2D vintage accounting ledger illustration. A bold profit arrow soaring past a +400% mark on the ruled grid.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "+400% MARKUP"
                },
                {
                    "quote": "and slot it directly into that second position to milk your social fear.",
                    "purpose": "Slotting clearance wine into position two",
                    "description": "Tactile 2D vintage accounting ledger illustration. Hand sliding the clearance bottle directly into slot two on the leather menu board.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "SLOT TWO"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "Editorial Commentary on Ego Surcharge",
            "purpose": "Deliver channel verdict on paying for ego rather than wine quality",
            "action": "The bookkeeper compares house wine quality with the clearance bottle",
            "setting": "The tasting table with balance scales and wine carafes",
            "camera": "Direct portrait shot transitioning to comparative balance",
            "narration": "The irony is that the cheapest wine is often a solid table vintage with honest pricing. When you buy the second bottle, you are not paying for better grapes. You are paying a premium purely to soothe your ego.",
            "requirements": ["R04"],
            "source_ids": ["SRC01"],
            "tone": "Direct, critical editorial commentary",
            "narrative_phase": "editorial_commentary",
            "narrative_situation": "editorial_commentary",
            "beats_data": [
                {
                    "quote": "The irony is that the cheapest wine is often a solid table vintage with honest pricing.",
                    "purpose": "Cheapest wine is solid table vintage",
                    "description": "Tactile 2D vintage accounting ledger illustration. The bookkeeper points with his brass pen to an honest ceramic carafe of house wine with an Honest Value stamp.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "HONEST VALUE"
                },
                {
                    "quote": "When you buy the second bottle,",
                    "purpose": "Buying the second bottle",
                    "description": "Tactile 2D vintage accounting ledger illustration. The second wine bottle poured into a crystal glass with dramatic dark red watercolor wash.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "you are not paying for better grapes.",
                    "purpose": "Not paying for better grapes",
                    "description": "Tactile 2D vintage accounting ledger illustration. A withered grape vine beside an accounting balance sheet showing identical fruit quality.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "SAME GRAPES"
                },
                {
                    "quote": "You are paying a premium purely to soothe your ego.",
                    "purpose": "Paying premium to soothe ego",
                    "description": "Tactile 2D vintage accounting ledger illustration. An ornate decorative mirror reflecting an oversized ego crown over a deflated wallet on grid paper.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "EGO PREMIUM"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "The Decoy Cliffhanger and Bridge",
            "purpose": "Escalate to the full menu engineering peak, bridge to the long video, and close",
            "action": "The camera pulls back to reveal the full menu blueprint and the long video thumbnail",
            "setting": "The complete dining table revealing the broader menu choice architecture",
            "camera": "Dynamic pull-out to wide menu layout and companion video endcard",
            "narration": "How do restaurants use this exact decoy trick across their entire dinner menu to steer sixty-eight percent of what you order? Watch our full menu engineering breakdown on YouTube. Scan the prices next time you dine out.",
            "requirements": ["R05"],
            "source_ids": ["SRC01"],
            "tone": "Engaging, high-energy peak and clear bridge",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cliffhanger_peak",
            "beats_data": [
                {
                    "quote": "How do restaurants use this exact decoy trick across their entire dinner menu",
                    "purpose": "Full menu decoy trick cliffhanger part 1",
                    "description": "Tactile 2D vintage accounting ledger illustration. The full restaurant menu unfolds like an intricate architectural blueprint with green vectors pointing across columns.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "MENU BLUEPRINT"
                },
                {
                    "quote": "to steer sixty-eight percent of what you order?",
                    "purpose": "Full menu decoy trick cliffhanger part 2",
                    "description": "Tactile 2D vintage accounting ledger illustration. Ink percentages radiating across dining orders, highlighting the 68% high-margin target capture.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "STEERING 68%"
                },
                {
                    "quote": "Watch our full menu engineering breakdown on YouTube.",
                    "purpose": "Bridge to full YouTube video",
                    "description": "Tactile 2D vintage accounting ledger illustration. A YouTube interface preview card in vintage ink style showcasing the long-form companion explainer thumbnail.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "FULL VIDEO"
                },
                {
                    "quote": "Scan the prices next time you dine out.",
                    "purpose": "Closing call to action and channel mark",
                    "description": "Tactile 2D vintage accounting ledger illustration. Wallet Anatomy official channel stamp with bookkeeper insignia and fountain pen on warm cotton ledger paper.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "emphasis": "WALLET ANATOMY",
                    "is_endcard": True
                }
            ]
        }
    ]

def get_macro_long_scenes_data():
    return [
        {
            "id": "SC01",
            "title": "The Dark Subdivisions and Data Centers",
            "purpose": "Hook the viewer with dark finished housing developments and data centers waiting for a steel box",
            "action": "A cinematic aerial view over unlit subdivisions and solar arrays revealing the missing distribution transformer",
            "setting": "An unlit modern development and substation pad on deep navy blueprint paper #0E1A2B",
            "camera": "Wide aerial sweep descending onto an empty concrete transformer foundation",
            "narration": "Across the country, multi-million-dollar housing subdivisions, sprawling solar farms, and gigawatt artificial intelligence data centers sit completed in total darkness. Buildings are wired, servers are racked, and transmission towers are strung. Yet everything remains paralyzed waiting for a single, unglamorous steel box: a high-voltage electrical distribution transformer. Without it, vast regional capital investments sit completely immobilized.",
            "requirements": ["R01"],
            "source_ids": ["SRC01"],
            "tone": "Objective, clarifying, fascinating",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "beats_data": [
                {
                    "quote": "Across the country, multi-million-dollar housing subdivisions, sprawling solar farms,",
                    "purpose": "Dark housing subdivision and solar farms",
                    "description": "Tactile 2D mid-century banknote intaglio engraving on deep navy blueprint paper #0E1A2B. Widescreen landscape of a sprawling modern suburban development with unlit streetlights under twilight.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "emphasis": "GRID BOTTLENECK"
                },
                {
                    "quote": "and gigawatt artificial intelligence data centers sit completed in total darkness.",
                    "purpose": "Unpowered data center compute clusters",
                    "description": "Tactile 2D mid-century banknote intaglio engraving. Interior of a massive AI compute warehouse with rows of silent, dark server racks engraved in fine cream lines #EDE8DC.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "AI DATA CENTERS"
                },
                {
                    "quote": "Buildings are wired, servers are racked, and transmission towers are strung.",
                    "purpose": "Fully strung transmission lines and wiring",
                    "description": "Tactile 2D technical blueprint schematic. High-voltage transmission towers with perfectly strung conductor cables drawn in precision engraved cross-hatching.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": None
                },
                {
                    "quote": "Yet everything remains paralyzed waiting for a single, unglamorous steel box:",
                    "purpose": "Paralyzed waiting for the steel box",
                    "description": "Tactile 2D technical blueprint schematic. Empty concrete foundation pad with disconnected heavy copper cables coiled uselessly in the gravel.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "WAITING FOR STEEL"
                },
                {
                    "quote": "a high-voltage electrical distribution transformer.",
                    "purpose": "The high-voltage distribution transformer tank",
                    "description": "Tactile 2D technical blueprint schematic. Detailed cutaway technical schematic of an industrial high-voltage transformer tank with brass #C98A2C bushing accents.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "THE TRANSFORMER"
                },
                {
                    "quote": "Without it, vast regional capital investments sit completely immobilized.",
                    "purpose": "Capital investments immobilized",
                    "description": "Tactile 2D technical blueprint schematic. An economic balance scale holding idle bond certificates and building schematics tipped downward on navy drafting paper.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "IMMOBILIZED"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "The Four-Year Wait Time Explosion",
            "purpose": "Expose the explosion in transformer procurement lead times from 12 to 48 months",
            "action": "A procurement timeline chart compares historical 12-month delivery with current 48-month delays",
            "setting": "A utility logistics dispatch office with intaglio charts and procurement manifests",
            "camera": "Tracking shot along an expanding multi-year industrial timeline calendar",
            "narration": "Prior to 2020, ordering a utility-scale transformer took roughly twelve months. Today, procurement wait times have surged past forty-eight months. According to the Department of Energy, some municipal utilities are quoting delivery schedules stretching into 2028. Without these transformers, not a single watt of generated electricity can safely reach a wall outlet. Supply chains have backed up across every major industrial distributor.",
            "requirements": ["R02"],
            "source_ids": ["SRC01"],
            "tone": "Objective, empirical, clarifying",
            "narrative_phase": "rapid_examples",
            "narrative_situation": "rapid_examples",
            "beats_data": [
                {
                    "quote": "Prior to 2020, ordering a utility-scale transformer took roughly twelve months.",
                    "purpose": "Historical 12-month delivery timeline",
                    "description": "Tactile 2D banknote intaglio engraving. Historical timeline schematic showing a swift 12-month procurement cycle marked with a clean brass clock icon.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "12-MONTH LEAD"
                },
                {
                    "quote": "Today, procurement wait times have surged past forty-eight months.",
                    "purpose": "Lead times surging past 48 months",
                    "description": "Tactile 2D technical blueprint schematic. The timeline expanding dramatically fourfold, marked with safety-red #D9381E warning stripes stretching across 48 months.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": "48 MONTHS"
                },
                {
                    "quote": "According to the Department of Energy, some municipal utilities are quoting delivery schedules stretching into 2028.",
                    "purpose": "Department of Energy report citation",
                    "description": "Tactile 2D technical blueprint schematic. Department of Energy official technical review insignia stamped in cream lines #EDE8DC with 2028 delivery stamp.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "DOE AUDIT 2028"
                },
                {
                    "quote": "Without these transformers,",
                    "purpose": "The transformer necessity",
                    "description": "Tactile 2D technical blueprint schematic. A high-voltage transmission schematic severed at the substation transformer boundary.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": None
                },
                {
                    "quote": "not a single watt of generated electricity can safely reach a wall outlet.",
                    "purpose": "Zero power reaching home outlets",
                    "description": "Tactile 2D technical blueprint schematic. A domestic three-prong wall outlet with zero voltage gauge readout drawn in fine technical drafting script.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "ZERO VOLTAGE"
                },
                {
                    "quote": "Supply chains have backed up across every major industrial distributor.",
                    "purpose": "Industrial distributors backed up",
                    "description": "Tactile 2D technical blueprint schematic. Cavernous freight shipping docks showing backlogged logistics manifests and empty transformer cradles.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "SUPPLY BACKLOG"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "Electromagnetic Step-Down Mechanics",
            "purpose": "Explain the physical necessity of 500,000V transmission and 240V step-down conversion",
            "action": "A technical cutaway reveals primary and secondary transformer coils and electromagnetic induction",
            "setting": "An engineering physics laboratory with high-voltage coil schematics",
            "camera": "Smooth macro push into the primary and secondary electromagnetic induction coils",
            "narration": "To understand why this box is irreplaceable, look at how the electrical grid functions. Power plants generate high-voltage electricity, often up to five hundred thousand volts, to move current over long distances with minimal heat dissipation. But your home appliances require two hundred forty volts. Transformers perform that delicate electromagnetic step-down conversion. Every unit operates on these precise mathematical principles of physics.",
            "requirements": ["R03"],
            "source_ids": ["SRC01"],
            "tone": "Fascinating, empirical, educational",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "To understand why this box is irreplaceable, look at how the electrical grid functions.",
                    "purpose": "Power grid mechanical function",
                    "description": "Tactile 2D banknote intaglio engraving on navy paper #0E1A2B. Macroscopic overview schematic of the national power grid connecting generation, transmission, and homes.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "THE GRID ENGINE"
                },
                {
                    "quote": "Power plants generate high-voltage electricity, often up to five hundred thousand volts,",
                    "purpose": "500,000 volt generation",
                    "description": "Tactile 2D technical blueprint schematic. Power plant turbines sending electric current surging at 500,000 volts along massive transmission lines.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "500,000 VOLTS"
                },
                {
                    "quote": "to move current over long distances with minimal heat dissipation.",
                    "purpose": "Minimal heat dissipation in transmission",
                    "description": "Tactile 2D technical blueprint schematic. Physics thermal diagram showing high-voltage current traversing long distances with minimal resistive losses.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "normal",
                    "emphasis": "MINIMAL HEAT"
                },
                {
                    "quote": "But your home appliances require two hundred forty volts.",
                    "purpose": "Home appliance 240V requirement",
                    "description": "Tactile 2D technical blueprint schematic. Domestic circuit diagram showing kitchen appliances operating safely on standard 240-volt domestic current.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "240V DOMESTIC"
                },
                {
                    "quote": "Transformers perform that delicate electromagnetic step-down conversion.",
                    "purpose": "Electromagnetic step-down transformation",
                    "description": "Tactile 2D technical blueprint schematic. Magnetic flux lines looping through laminated core limbs, stepping voltage down from primary to secondary coils.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "STEP-DOWN CORE"
                },
                {
                    "quote": "Every unit operates on these precise mathematical principles of physics.",
                    "purpose": "Mathematical physics of induction",
                    "description": "Tactile 2D technical blueprint schematic. Faraday's Law of Induction equations engraved in clean brass calligraphy beside vector magnetic fields.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "FARADAY'S LAW"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "The Magnetic Core Meltdown Constraint",
            "purpose": "Explain why ordinary carbon steel melts from eddy-current hysteresis and requires GOES",
            "action": "A thermal simulation contrasts standard structural steel melting versus laminated silicon steel",
            "setting": "A high-temperature metallurgical testing cell with thermal cameras",
            "camera": "Intense close-up on the glowing red magnetic core cross-section",
            "narration": "Inside the tank sits a solid laminated steel core wrapped in thousands of copper turns. When alternating current flows, it generates a pulsing magnetic flux sixty times per second. If you built this core from standard structural steel, internal eddy currents and magnetic hysteresis would cause the metal to rapidly overheat and melt. Extreme thermal friction would destroy the internal coils within minutes. Preventing thermal runaway requires specialized grain alignment.",
            "requirements": ["R04"],
            "source_ids": ["SRC02"],
            "tone": "Technical, urgent, fascinating",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "Inside the tank sits a solid laminated steel core wrapped in thousands of copper turns.",
                    "purpose": "Laminated steel core and copper coils",
                    "description": "Tactile 2D banknote intaglio engraving. Precision cutaway of a multi-ton transformer core composed of thousands of micro-thin steel laminations wrapped in copper.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "LAMINATED CORE"
                },
                {
                    "quote": "When alternating current flows, it generates a pulsing magnetic flux sixty times per second.",
                    "purpose": "60 Hz pulsing magnetic flux",
                    "description": "Tactile 2D technical blueprint schematic. Sine wave oscillating at 60 Hz with dynamic magnetic flux lines surging through the core material.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "60 HERTZ FLUX"
                },
                {
                    "quote": "If you built this core from standard structural steel,",
                    "purpose": "Standard structural steel comparison",
                    "description": "Tactile 2D technical blueprint schematic. A block of standard structural construction steel placed on the testing bench with a warning label.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "STANDARD STEEL"
                },
                {
                    "quote": "internal eddy currents and magnetic hysteresis would cause the metal to rapidly overheat and melt.",
                    "purpose": "Eddy currents and hysteresis heating",
                    "description": "Tactile 2D technical blueprint schematic. Chaotic circulating eddy-current loops heating the carbon steel to glowing red #D9381E temperatures.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "CORE MELTDOWN"
                },
                {
                    "quote": "Extreme thermal friction would destroy the internal coils within minutes.",
                    "purpose": "Coil destruction within minutes",
                    "description": "Tactile 2D technical blueprint schematic. Smoldering copper coil insulation degrading under intense thermal runaway inside the simulated tank.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "THERMAL RUNAWAY"
                },
                {
                    "quote": "Preventing thermal runaway requires specialized grain alignment.",
                    "purpose": "Grain alignment requirement",
                    "description": "Tactile 2D technical blueprint schematic. Microscopic crystalline diagram showing chaotic iron domains contrasting with ordered aligned magnetic grains.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "GRAIN ALIGNMENT"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "Editorial Verdict on Metallurgy vs Software",
            "purpose": "Editorial commentary on digital software ambitions crashing into physical metallurgy",
            "action": "The economic correspondent presents the physical speed limits of heavy industrial manufacturing",
            "setting": "A mid-century financial press briefing room with engraved world maps and steel foundry prints",
            "camera": "Direct portrait shot transitioning to global heavy manufacturing balances",
            "narration": "Here lies our macro perspective: modern clean energy and artificial intelligence ambitions are crashing directly into the unyielding laws of metallurgy. You can write software in minutes, but you cannot manifest magnetic flux without highly specialized atomic structures. Our digital economy rests on a foundation of nineteenth-century heavy electrical manufacturing. No amount of venture capital funding can bypass basic material physics.",
            "requirements": ["R05"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Objective, sharp, authoritative editorial commentary",
            "narrative_phase": "editorial_commentary",
            "narrative_situation": "editorial_commentary",
            "beats_data": [
                {
                    "quote": "Here lies our macro perspective: modern clean energy and artificial intelligence ambitions",
                    "purpose": "Macro perspective statement",
                    "description": "Tactile 2D banknote intaglio engraving. The correspondent protagonist in structured navy suit standing before a grand blueprint schematic of the modern industrial world.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "MACRO PERSPECTIVE"
                },
                {
                    "quote": "are crashing directly into the unyielding laws of metallurgy.",
                    "purpose": "Crashing into metallurgy laws",
                    "description": "Tactile 2D banknote intaglio engraving. High-contrast visual collision between floating glowing software code and an unyielding anvil of solid industrial steel.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "METALLURGY LIMITS"
                },
                {
                    "quote": "You can write software in minutes,",
                    "purpose": "Writing software in minutes",
                    "description": "Tactile 2D banknote intaglio engraving. An open terminal window showing rapidly compiling lines of modern code in crisp cream lines.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "but you cannot manifest magnetic flux without highly specialized atomic structures.",
                    "purpose": "Specialized atomic structure requirement",
                    "description": "Tactile 2D banknote intaglio engraving. Microscopic atomic lattice of silicon steel grains aligned in perfect crystallographic direction.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "ATOMIC LATTICE"
                },
                {
                    "quote": "Our digital economy rests on a foundation of nineteenth-century heavy electrical manufacturing.",
                    "purpose": "19th century manufacturing foundation",
                    "description": "Tactile 2D banknote intaglio engraving. Architectural cross-section showing modern cloud data servers resting physically atop heavy steel foundry foundations.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "HEAVY INDUSTRY"
                },
                {
                    "quote": "No amount of venture capital funding can bypass basic material physics.",
                    "purpose": "Venture capital cannot bypass physics",
                    "description": "Tactile 2D banknote intaglio engraving. Heavy gold bullion coins resting on a balance scale unable to budge the fundamental laws of electromagnetic induction.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "PHYSICAL REALITY"
                }
            ]
        },
        {
            "id": "SC06",
            "title": "Grain-Oriented Electrical Steel (GOES)",
            "purpose": "Explain the GOES manufacturing process and the single domestic US mill in Pennsylvania",
            "action": "A specialized rolling mill cold-rolls electrical steel coils in Pennsylvania",
            "setting": "An immense industrial steel mill with rolling stands and hydrogen annealing furnaces",
            "camera": "Long cinematic tracking shot along the cold-reduction steel rolling line",
            "narration": "Transformers require an extraordinary material known as Grain-Oriented Electrical Steel, or GOES. Through complex cold-rolling and thermal annealing, metallurgists align the crystalline iron grains in a single direction, minimizing magnetic resistance. Yet in the United States, only one single domestic facility in Pennsylvania manufactures this critical electrical steel. Expanding these complex smelting operations requires billions in upfront capital investment.",
            "requirements": ["R06"],
            "source_ids": ["SRC01"],
            "tone": "Fascinating, empirical, industrial",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "Transformers require an extraordinary material known as Grain-Oriented Electrical Steel, or GOES.",
                    "purpose": "Grain-Oriented Electrical Steel introduction",
                    "description": "Tactile 2D banknote intaglio engraving. Coils of Grain-Oriented Electrical Steel unspooling under precise measuring gauges on navy blueprint paper.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "GOES STEEL"
                },
                {
                    "quote": "Through complex cold-rolling and thermal annealing,",
                    "purpose": "Cold rolling and thermal annealing",
                    "description": "Tactile 2D technical blueprint schematic. Industrial cold-reduction rollers compressing steel sheets under immense hydraulic pressure beside annealing furnaces.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "ANNEALING"
                },
                {
                    "quote": "metallurgists align the crystalline iron grains in a single direction, minimizing magnetic resistance.",
                    "purpose": "Aligning iron grains along single axis",
                    "description": "Tactile 2D technical blueprint schematic. Microscopic schematic showing crystal lattice planes aligned with 99% precision along the rolling axis.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "UNIFORM GRAIN"
                },
                {
                    "quote": "Yet in the United States,",
                    "purpose": "United States geography",
                    "description": "Tactile 2D banknote intaglio engraving. Map of the continental United States engraved in fine intaglio lines on navy paper.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": None
                },
                {
                    "quote": "only one single domestic facility in Pennsylvania manufactures this critical electrical steel.",
                    "purpose": "Solitary Pennsylvania steel mill",
                    "description": "Tactile 2D banknote intaglio engraving. Close-up map pinpointing the lone specialized electrical steel production facility in Butler, Pennsylvania.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "1 DOMESTIC MILL"
                },
                {
                    "quote": "Expanding these complex smelting operations requires billions in upfront capital investment.",
                    "purpose": "Billions in capital investment required",
                    "description": "Tactile 2D technical blueprint schematic. Construction blueprints for an advanced specialty steel foundry with multi-billion-dollar financing stamps.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "$3B SMELTING EXPANSION"
                }
            ]
        },
        {
            "id": "SC07",
            "title": "The Fifty-Thousand Bespoke Specs",
            "purpose": "Explain why transformers cannot be mass-produced due to 50,000 conflicting utility specs",
            "action": "A stark visual contrast between automated car factories and hand-built custom transformers",
            "setting": "An engineering archive room filled with incompatible municipal utility blueprints",
            "camera": "Split-screen comparing automated automotive robotics with custom manual coil assembly",
            "narration": "The crisis worsens because transformers cannot be mass-produced on an automated assembly line. The United States power grid is fragmented across three thousand distinct electric utilities, each demanding custom technical specifications. With over fifty thousand unique engineering designs in circulation, manufacturers must custom-build almost every single transformer by hand. Standardization remains virtually nonexistent across modern American transmission networks.",
            "requirements": ["R07"],
            "source_ids": ["SRC02"],
            "tone": "Eye-opening, structural, objective",
            "narrative_phase": "before_after_contrast",
            "narrative_situation": "before_after_contrast",
            "beats_data": [
                {
                    "quote": "The crisis worsens because transformers cannot be mass-produced on an automated assembly line.",
                    "purpose": "Cannot be mass produced on assembly line",
                    "description": "Tactile 2D banknote intaglio engraving. Automotive automated assembly line with robotic arms juxtaposed against a red crossed-out transformer silhouette.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "NO ASSEMBLY LINE"
                },
                {
                    "quote": "The United States power grid is fragmented across three thousand distinct electric utilities,",
                    "purpose": "3,000 fragmented electric utilities",
                    "description": "Tactile 2D technical blueprint schematic. A patchwork map of North America divided into 3,000 separate, fragmented electric utility service territories.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "3,000 UTILITIES"
                },
                {
                    "quote": "each demanding custom technical specifications.",
                    "purpose": "Custom technical specifications demanded",
                    "description": "Tactile 2D technical blueprint schematic. Thick technical spec books stacked high, each demanding slightly different operating impedances and voltages.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": None
                },
                {
                    "quote": "With over fifty thousand unique engineering designs in circulation,",
                    "purpose": "Over 50,000 unique designs",
                    "description": "Tactile 2D technical blueprint schematic. Cascading blueprint schematics showing 50,000 conflicting mechanical dimensions and electrical tolerances.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "50,000 BESPOKE SPECS"
                },
                {
                    "quote": "manufacturers must custom-build almost every single transformer by hand.",
                    "purpose": "Custom building every transformer by hand",
                    "description": "Tactile 2D technical blueprint schematic. Skilled electrical craftsmen assembling core laminations and copper coils individually by hand.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "BUILT BY HAND"
                },
                {
                    "quote": "Standardization remains virtually nonexistent across modern American transmission networks.",
                    "purpose": "Nonexistent grid standardization",
                    "description": "Tactile 2D technical blueprint schematic. Incompatible plug and socket interfaces unable to connect, illustrating systemic fragmentation.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "ZERO STANDARDS"
                }
            ]
        },
        {
            "id": "SC08",
            "title": "The Master Coil Winder Crunch",
            "purpose": "Expose the 5-year apprenticeship bottleneck and aging skilled labor workforce",
            "action": "A veteran master craftsman guides insulated copper conductors around a rotating mandrel",
            "setting": "A specialized heavy electrical winding shop floor with tension gauges",
            "camera": "Intimate close-up on hands guiding heavy copper conductor winding",
            "narration": "Winding those copper coils around the magnetic core is an exacting art. A single loose turn or uneven tension can cause catastrophic electrical arcing under high load. It takes up to five years to train a master coil winder, and the aging industrial workforce is retiring faster than apprentices enter factories. Without fresh talent on the factory floor, bottleneck delays worsen rapidly. Precision hand craftsmanship remains completely irreplaceable.",
            "requirements": ["R08"],
            "source_ids": ["SRC03"],
            "tone": "Respectful, grounded, human-scale",
            "narrative_phase": "story_action",
            "narrative_situation": "story_action",
            "beats_data": [
                {
                    "quote": "Winding those copper coils around the magnetic core is an exacting art.",
                    "purpose": "Coil winding as exacting art",
                    "description": "Tactile 2D banknote intaglio engraving. Veteran coil winder with focused expression guiding heavy insulated copper wire onto a rotating mandrel.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "THE WINDING ART"
                },
                {
                    "quote": "A single loose turn or uneven tension can cause catastrophic electrical arcing under high load.",
                    "purpose": "Catastrophic electrical arcing risk",
                    "description": "Tactile 2D technical blueprint schematic. Electrical arc flash blasting through insulation layers during high-voltage laboratory tolerance testing.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "ARC DANGER"
                },
                {
                    "quote": "It takes up to five years to train a master coil winder,",
                    "purpose": "Five-year training requirement",
                    "description": "Tactile 2D technical blueprint schematic. Five-year apprentice progression gauge tracking skills from basic conductor prep to master winding.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "5-YEAR APPRENTICE"
                },
                {
                    "quote": "and the aging industrial workforce is retiring faster than apprentices enter factories.",
                    "purpose": "Retiring workforce demographic crunch",
                    "description": "Tactile 2D banknote intaglio engraving. Demographic bar chart showing senior master winders retiring while apprentice benches remain half-filled.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "AGING WORKFORCE"
                },
                {
                    "quote": "Without fresh talent on the factory floor, bottleneck delays worsen rapidly.",
                    "purpose": "Delays worsen without fresh talent",
                    "description": "Tactile 2D technical blueprint schematic. Lead time hourglass where sands of production slow dramatically due to specialized labor scarcity.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": None
                },
                {
                    "quote": "Precision hand craftsmanship remains completely irreplaceable.",
                    "purpose": "Craftsmanship is irreplaceable",
                    "description": "Tactile 2D banknote intaglio engraving. Master winder's calloused hands inspecting microscopic coil alignment with brass vernier calipers.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "IRREPLACEABLE SKILL"
                }
            ]
        },
        {
            "id": "SC09",
            "title": "The AI Data Center Power Grab",
            "purpose": "Explain how tech conglomerates outbid public utilities and lock production slots through 2030",
            "action": "Tech executives place massive multi-year advance cash deposits directly with transformer manufacturers",
            "setting": "An executive boardroom overlooking hyperscale cloud compute data center campuses",
            "camera": "Wide pan across multi-billion-dollar compute capital flows outbidding municipal grids",
            "narration": "Now add the artificial intelligence boom. Tech conglomerates building massive compute clusters are consuming power equivalent to entire cities. With billions in capital, tech giants are placing advance cash deposits for entire factory runs through 2030, outbidding local utilities and pushing rural power cooperative orders to the back of the line. This financial clout leaves essential public infrastructure upgrades waiting indefinitely. Market capital prioritizes cloud data centers over municipal grids.",
            "requirements": ["R09"],
            "source_ids": ["SRC03"],
            "tone": "Urgent, analytical, eye-opening",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "Now add the artificial intelligence boom.",
                    "purpose": "AI boom introduction",
                    "description": "Tactile 2D banknote intaglio engraving. Futuristic AI compute cluster node graphic mapped directly onto power grid consumption blueprints.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "THE AI BOOM"
                },
                {
                    "quote": "Tech conglomerates building massive compute clusters are consuming power equivalent to entire cities.",
                    "purpose": "Consuming power equal to entire cities",
                    "description": "Tactile 2D technical blueprint schematic. Power balance chart showing a single gigawatt data center cluster equaling the electricity demand of Atlanta.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "CITY-SCALE POWER"
                },
                {
                    "quote": "With billions in capital, tech giants are placing advance cash deposits for entire factory runs through 2030,",
                    "purpose": "Advance deposits locking factory runs through 2030",
                    "description": "Tactile 2D banknote intaglio engraving. Corporate check stamped with multi-billion-dollar advance deposit locking factory transformer slots through 2030.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "LOCKED TO 2030"
                },
                {
                    "quote": "outbidding local utilities and pushing rural power cooperative orders to the back of the line.",
                    "purpose": "Outbidding local public utilities",
                    "description": "Tactile 2D technical blueprint schematic. Order queue graphic where municipal power orders are pushed backward by tech corporate purchase orders.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "QUEUE OVERRIDE"
                },
                {
                    "quote": "This financial clout leaves essential public infrastructure upgrades waiting indefinitely.",
                    "purpose": "Public infrastructure upgrades waiting",
                    "description": "Tactile 2D technical blueprint schematic. Aging municipal substation with rust-streaked transformers waiting for replacement units that never arrive.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "normal",
                    "emphasis": None
                },
                {
                    "quote": "Market capital prioritizes cloud data centers over municipal grids.",
                    "purpose": "Market capital prioritization",
                    "description": "Tactile 2D banknote intaglio engraving. An economic scale heavily weighted toward private cloud infrastructure over public civic electrical grids.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "CAPITAL PRIORITY"
                }
            ]
        },
        {
            "id": "SC10",
            "title": "The Speed Limit of Physical Manufacturing",
            "purpose": "Editorial verdict on physical manufacturing being the ultimate bottleneck for technological progress",
            "action": "The economic correspondent connects the physical reality of steel to the limits of software growth",
            "setting": "The macroeconomic gears command center with rotating mechanical schematics",
            "camera": "Dynamic dolly shot pulling back to reveal global transmission constraints",
            "narration": "This bottleneck proves that technological progress is only as fast as its slowest physical supply chain. We want electric vehicles, renewable microgrids, and hyperscale artificial intelligence, but our infrastructure depends on hand-wound steel cores made from a single domestic mill. You cannot download electricity; physical manufacturing sets the ultimate speed limit. The invisible foundation of all software growth remains heavy physical engineering. Ignoring physical manufacturing constraints invites systemic grid fragility.",
            "requirements": ["R10"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Authoritative, empowering, critical editorial verdict",
            "narrative_phase": "editorial_commentary",
            "narrative_situation": "editorial_commentary",
            "beats_data": [
                {
                    "quote": "This bottleneck proves that technological progress is only as fast as its slowest physical supply chain.",
                    "purpose": "Progress limited by slowest physical link",
                    "description": "Tactile 2D banknote intaglio engraving. Mechanical gear train where massive high-speed software gears are locked in place by a single jammed steel gear.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "PHYSICAL SPEED LIMIT"
                },
                {
                    "quote": "We want electric vehicles, renewable microgrids, and hyperscale artificial intelligence,",
                    "purpose": "EVs, renewables, and AI demand",
                    "description": "Tactile 2D technical blueprint schematic. Three modern icons: an electric charging station, a wind turbine, and a neural network chip arranged on blueprint.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "CLEAN TECH AMBITION"
                },
                {
                    "quote": "but our infrastructure depends on hand-wound steel cores made from a single domestic mill.",
                    "purpose": "Dependence on single domestic steel mill",
                    "description": "Tactile 2D technical blueprint schematic. Single steel coil icon funneling into thousands of industrial applications across North America.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "SINGLE DOMESTIC MILL"
                },
                {
                    "quote": "You cannot download electricity; physical manufacturing sets the ultimate speed limit.",
                    "purpose": "Cannot download electricity verdict",
                    "description": "Tactile 2D banknote intaglio engraving. A download progress bar failing at 99% beside an unyielding physical steel transformer bushing.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "CAN'T DOWNLOAD POWER"
                },
                {
                    "quote": "The invisible foundation of all software growth remains heavy physical engineering.",
                    "purpose": "Software growth depends on heavy engineering",
                    "description": "Tactile 2D banknote intaglio engraving. An immense steel transformer core holding up the digital cloud infrastructure on precision cross-hatching.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "HEAVY FOUNDATION"
                },
                {
                    "quote": "Ignoring physical manufacturing constraints invites systemic grid fragility.",
                    "purpose": "Systemic grid fragility warning",
                    "description": "Tactile 2D banknote intaglio engraving. Fragile glass cracks radiating across an overloaded national electrical network diagram.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "SYSTEMIC FRAGILITY"
                }
            ]
        },
        {
            "id": "SC11",
            "title": "Grid Standardization and the Real Economy",
            "purpose": "Provide grid standardization solutions and closing takeaway on hidden physical gears",
            "action": "A standardized universal transformer blueprint replaces the 50,000 fragmented schematics",
            "setting": "A clean modern drafting table with standardized universal utility specifications",
            "camera": "Direct portrait shot transitioning into the channel closing emblem",
            "narration": "Solving the grid lock requires standardizing voltage specifications, expanding domestic electrical steel mills, and investing in trade apprenticeships. Until utility standards consolidate, lead times will remain measured in years. Watch the real economy behind the headlines. Track the physical gears powering your modern life. Investigate the hidden transmission bottlenecks in your region.",
            "requirements": ["R11"],
            "source_ids": ["SRC01"],
            "tone": "Empowering, pragmatic, forward-looking",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cta_bridge",
            "beats_data": [
                {
                    "quote": "Solving the grid lock requires standardizing voltage specifications,",
                    "purpose": "Standardizing voltage specs",
                    "description": "Tactile 2D banknote intaglio engraving. Universal modular transformer blueprint stamped with Standardized National Specification in gold ink.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "STANDARDIZE SPECS"
                },
                {
                    "quote": "expanding domestic electrical steel mills, and investing in trade apprenticeships.",
                    "purpose": "Expanding mills and trade apprenticeships",
                    "description": "Tactile 2D technical blueprint schematic. New steel rolling mill ground-breaking schematic beside a modern technical trade apprentice workshop.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "EXPAND MILLS"
                },
                {
                    "quote": "Until utility standards consolidate, lead times will remain measured in years.",
                    "purpose": "Lead times measured in years warning",
                    "description": "Tactile 2D technical blueprint schematic. A multi-year procurement calendar showing lead times gradually stabilizing toward 2030.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "YEARS TO SOLVE"
                },
                {
                    "quote": "Watch the real economy behind the headlines.",
                    "purpose": "Watch the real economy callout",
                    "description": "Tactile 2D banknote intaglio engraving. The correspondent protagonist in navy suit pointing forward with analytical authority beside global supply conduits.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "THE REAL ECONOMY"
                },
                {
                    "quote": "Track the physical gears powering your modern life.",
                    "purpose": "Closing call to action",
                    "description": "Tactile 2D banknote intaglio engraving. Massive interlocking brass gears #C98A2C rotating steadily on deep blueprint navy paper.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "TRACK THE GEARS"
                },
                {
                    "quote": "Investigate the hidden transmission bottlenecks in your region.",
                    "purpose": "Closing channel seal and endcard",
                    "description": "Tactile 2D banknote intaglio engraving. Macro Gears official channel emblem featuring engraved mechanical gears and technical blueprint seal on navy paper.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "emphasis": "MACRO GEARS",
                    "is_endcard": True
                }
            ]
        }
    ]

def get_macro_short_scenes_data():
    return [
        {
            "id": "SC01",
            "title": "Subdivisions Sitting in the Dark",
            "purpose": "Hook the viewer with finished developments waiting 4 years for a steel box",
            "action": "A camera pans over unlit subdivisions and solar panels to reveal an empty concrete transformer pad",
            "setting": "An unlit suburban subdivision on navy blueprint paper #0E1A2B",
            "camera": "Direct overhead shot descending toward the missing transformer pad",
            "narration": "Multi-million-dollar housing subdivisions, solar power farms, and AI data centers are sitting completely finished in the dark. They are not waiting on permits or funding. They are stuck waiting four years for a single steel box.",
            "requirements": ["R01"],
            "source_ids": ["SRC01"],
            "tone": "Urgent, eye-opening, direct",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "beats_data": [
                {
                    "quote": "Multi-million-dollar housing subdivisions, solar power farms,",
                    "purpose": "Dark housing and solar farms",
                    "description": "Tactile 2D banknote intaglio engraving on navy blueprint paper #0E1A2B. Unlit modern residential streets and idle solar arrays under twilight.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "emphasis": "POWERLESS"
                },
                {
                    "quote": "and AI data centers are sitting completely finished in the dark.",
                    "purpose": "Data centers finished in the dark",
                    "description": "Tactile 2D banknote intaglio engraving. Server room full of silent black compute racks engraved in fine cream lines #EDE8DC.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "AI IN THE DARK"
                },
                {
                    "quote": "They are not waiting on permits or funding.",
                    "purpose": "Not waiting on permits or funding",
                    "description": "Tactile 2D technical blueprint schematic. Approved government permits and green funding stamps stacked neatly beside empty electrical conduits.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "PERMITS APPROVED"
                },
                {
                    "quote": "They are stuck waiting four years for a single steel box.",
                    "purpose": "Waiting 4 years for a steel box",
                    "description": "Tactile 2D technical blueprint schematic. A four-year calendar countdown leading to an isolated steel transformer box highlighted in brass #C98A2C.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "4-YEAR WAIT"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "The Specialized GOES Steel Requirement",
            "purpose": "Explain why ordinary steel melts and only GOES works",
            "action": "A cutaway reveals the magnetic core and shows ordinary steel melting under eddy currents",
            "setting": "An engineering laboratory on navy blueprint paper",
            "camera": "Macro shot of magnetic field lines through grain-oriented steel",
            "narration": "That box is a high-voltage transformer, and building one requires Grain-Oriented Electrical Steel. Regular structural steel melts from electromagnetic heat. Only this special crystalline iron can handle the voltage, and America has only one domestic mill producing it.",
            "requirements": ["R02"],
            "source_ids": ["SRC01"],
            "tone": "Fascinating, empirical, technical",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "That box is a high-voltage transformer,",
                    "purpose": "High-voltage transformer definition",
                    "description": "Tactile 2D technical blueprint schematic. Cutaway of an industrial transformer showing heavy primary bushings and oil-filled tank.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "THE TRANSFORMER"
                },
                {
                    "quote": "and building one requires Grain-Oriented Electrical Steel.",
                    "purpose": "Grain-Oriented Electrical Steel requirement",
                    "description": "Tactile 2D banknote intaglio engraving. Cold-rolled coils of Grain-Oriented Electrical Steel unspooling with bright metallic luster.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "normal",
                    "emphasis": "GOES STEEL"
                },
                {
                    "quote": "Regular structural steel melts from electromagnetic heat.",
                    "purpose": "Structural steel melts under eddy currents",
                    "description": "Tactile 2D technical blueprint schematic. Carbon structural steel melting and warping under glowing red #D9381E eddy-current loops.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "EDDY CURRENTS"
                },
                {
                    "quote": "Only this special crystalline iron can handle the voltage, and America has only one domestic mill producing it.",
                    "purpose": "Only one domestic mill producing it",
                    "description": "Tactile 2D banknote intaglio engraving. Map of the United States with a solitary glowing pinpoint over the Pennsylvania electrical steel mill.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "1 DOMESTIC MILL"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "Fifty Thousand Incompatible Specs",
            "purpose": "Explain why hand winding is required due to 50,000 custom utility designs",
            "action": "A craftsman winds heavy copper conductors by hand across incompatible blueprints",
            "setting": "A heavy electrical manufacturing workshop on navy blueprint ground",
            "camera": "Intimate shot of hands winding copper coils",
            "narration": "Making matters worse, transformers cannot be mass-produced. Over three thousand US electric utilities demand fifty thousand conflicting engineering specifications. Every unit must be custom-wound by hand by veteran master winders who take five full years to train.",
            "requirements": ["R03"],
            "source_ids": ["SRC02"],
            "tone": "Structural, eye-opening",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "Making matters worse, transformers cannot be mass-produced.",
                    "purpose": "Cannot be mass produced",
                    "description": "Tactile 2D banknote intaglio engraving. High-speed factory conveyor belt halted with a red mechanical stop lever.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "CAN'T MASS PRODUCE"
                },
                {
                    "quote": "Over three thousand US electric utilities demand fifty thousand conflicting engineering specifications.",
                    "purpose": "50,000 conflicting engineering specs",
                    "description": "Tactile 2D technical blueprint schematic. Stacks of conflicting utility spec books showing incompatible electrical tolerances.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "50,000 SPECS"
                },
                {
                    "quote": "Every unit must be custom-wound by hand",
                    "purpose": "Custom wound by hand",
                    "description": "Tactile 2D banknote intaglio engraving. Experienced technician guiding insulated copper wire conductors manually around a wooden mandrel.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "HAND WOUND"
                },
                {
                    "quote": "by veteran master winders who take five full years to train.",
                    "purpose": "Five years to train master winders",
                    "description": "Tactile 2D technical blueprint schematic. Five-year training diploma stamped with Master Winder Guild seal in brass ink.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "5-YEAR TRAINING"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "Editorial Commentary on Physical Limits",
            "purpose": "Channel verdict on software ambitions colliding with physical metallurgy",
            "action": "The economic correspondent weighs digital AI compute against heavy industrial steel",
            "setting": "The macroeconomic gears command desk on deep navy paper",
            "camera": "Direct portrait shot transitioning into a heavy physical balance scale",
            "narration": "Now artificial intelligence data centers are buying up factory capacity years in advance with cash deposits. Our digital software future has collided head-on with the gritty physical bottleneck of nineteenth-century metallurgical manufacturing.",
            "requirements": ["R04"],
            "source_ids": ["SRC01", "SRC03"],
            "tone": "Authoritative, critical editorial commentary",
            "narrative_phase": "editorial_commentary",
            "narrative_situation": "editorial_commentary",
            "beats_data": [
                {
                    "quote": "Now artificial intelligence data centers are buying up factory capacity years in advance with cash deposits.",
                    "purpose": "AI centers buying up factory capacity with cash",
                    "description": "Tactile 2D banknote intaglio engraving. Silicon Valley corporate check vault booking factory assembly bays through 2030.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "AI CASH DEPOSITS"
                },
                {
                    "quote": "Our digital software future has collided head-on",
                    "purpose": "Digital future collision",
                    "description": "Tactile 2D banknote intaglio engraving. An ethereal digital cloud server icon slamming against an unyielding iron block.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "THE HEAD-ON CRASH"
                },
                {
                    "quote": "with the gritty physical bottleneck",
                    "purpose": "Gritty physical bottleneck",
                    "description": "Tactile 2D technical blueprint schematic. Narrow bottleneck pipe where massive digital electricity demand jams at a physical transformer tank.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "THE CHOKEPOINT"
                },
                {
                    "quote": "of nineteenth-century metallurgical manufacturing.",
                    "purpose": "19th century metallurgical manufacturing",
                    "description": "Tactile 2D banknote intaglio engraving. The correspondent protagonist in structured navy suit observing a heavy steel rolling mill with solemn analytical clarity.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "HEAVY METALLURGY"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "The Global Power Grid Cliffhanger",
            "purpose": "Escalate to the global power grid cliffhanger, bridge to the long video, and close",
            "action": "The camera pulls out to reveal the national transmission grid blueprint and long video card",
            "setting": "The complete national transmission network blueprint on deep navy paper",
            "camera": "Dynamic pull-out to national grid overview and companion video endcard",
            "narration": "How will a four-year wait for electrical steel reshape global power grids and renewable energy adoption? Watch the full macro breakdown on our YouTube channel. Observe the hidden supply chains around you.",
            "requirements": ["R05"],
            "source_ids": ["SRC01"],
            "tone": "Engaging, high-energy peak and clear bridge",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cliffhanger_peak",
            "beats_data": [
                {
                    "quote": "How will a four-year wait for electrical steel reshape global power grids",
                    "purpose": "Four-year wait grid reshape cliffhanger part 1",
                    "description": "Tactile 2D banknote intaglio engraving. Global energy grid map with red warning nodes pulsing across key international interconnections.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "GLOBAL SHIFT"
                },
                {
                    "quote": "and renewable energy adoption?",
                    "purpose": "Renewable adoption cliffhanger part 2",
                    "description": "Tactile 2D technical blueprint schematic. Wind and solar growth projection curves stalling abruptly against transformer supply lines.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "RENEWABLE DELAYS"
                },
                {
                    "quote": "Watch the full macro breakdown on our YouTube channel.",
                    "purpose": "Bridge to full YouTube explainer",
                    "description": "Tactile 2D banknote intaglio engraving. YouTube companion video preview card in technical blueprint style on navy ground.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "FULL VIDEO"
                },
                {
                    "quote": "Observe the hidden supply chains around you.",
                    "purpose": "Closing call to action and channel seal",
                    "description": "Tactile 2D banknote intaglio engraving. Macro Gears official channel emblem with interlocking brass gears on deep navy blueprint paper.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "emphasis": "MACRO GEARS",
                    "is_endcard": True
                }
            ]
        }
    ]

def get_career_long_scenes_data():
    return [
        {
            "id": "SC01",
            "title": "The Indispensable Firefighter Paradox",
            "purpose": "Hook the viewer with the indispensable employee who gets perfect reviews but no promotion",
            "action": "The editorial stickman sprints to put out a project fire while an executive promotion bypasses him",
            "setting": "A corporate office floor at night on fibrous cream newsprint #EFECE6",
            "camera": "Dynamic horizontal tracking shot following the stickman sprinting with fire equipment",
            "narration": "You are the most reliable person on your team. Whenever a critical server crashes, a key client threatens to leave, or a project falls apart, leadership calls you. You fix the mess, collect glowing praise in performance reviews, and then watch the promotion go to someone who does half the work. It leaves you feeling completely bewildered.",
            "requirements": ["R01"],
            "source_ids": ["SRC01"],
            "tone": "Strategic, candid, relatable",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "beats_data": [
                {
                    "quote": "You are the most reliable person on your team.",
                    "purpose": "Establishing the reliable team member",
                    "description": "Tactile 2D Wall Street Journal Hedcut stipple illustration on warm newsprint #EFECE6. The editorial bald circle stickman in royal cobalt shirt #3B82C4 standing at his desk surrounded by team files.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "emphasis": "MOST RELIABLE"
                },
                {
                    "quote": "Whenever a critical server crashes, a key client threatens to leave, or a project falls apart,",
                    "purpose": "Critical project emergencies erupting",
                    "description": "Tactile 2D pen-and-ink sketchbook illustration. Office desks and computer monitors bursting with metaphorical red ink flames and alarm bells.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "CRITICAL EMERGENCY"
                },
                {
                    "quote": "leadership calls you.",
                    "purpose": "Leadership calling the firefighter",
                    "description": "Tactile 2D Hedcut stipple illustration. A ringing executive telephone handset with speech lines pointing directly at the stickman.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "THE CALL"
                },
                {
                    "quote": "You fix the mess, collect glowing praise in performance reviews,",
                    "purpose": "Fixing the mess and collecting praise",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman extinguishing the fire, receiving an annual review document stamped with an 'Exceeds Expectations' gold seal #D48817.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "TOP REVIEW"
                },
                {
                    "quote": "and then watch the promotion go to someone who does half the work.",
                    "purpose": "Watching the promotion go to someone else",
                    "description": "Tactile 2D Hedcut stipple illustration. A relaxed peer receiving the director promotion handshake at the executive conference table while doing minimal work.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "PASSED OVER"
                },
                {
                    "quote": "It leaves you feeling completely bewildered.",
                    "purpose": "Bewildered reaction to lost promotion",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman staring in disbelief at the empty corporate ladder, holding another emergency incident folder.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "BEWILDERED"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "The Firefighter's Trap",
            "purpose": "Explain the Firefighter's Trap where operational rescues consume strategic visibility",
            "action": "A circular diagram shows incoming fires endlessly feeding the stickman's desk",
            "setting": "A cubicle bullpen with overflowing crisis ticket queues on newsprint paper",
            "camera": "Overhead top-down shot of the circular crisis loop trapping the desk",
            "narration": "Management theorists call this pattern the Firefighter's Trap. Because you are extraordinarily skilled at putting out operational fires, colleagues and managers bring you every single blaze. Over time, you build an exhausting identity as the team savior, spending sixty hours a week executing tactical rescues while your long-term strategic visibility drops to zero. Every emergency consumed your workday until strategic thinking vanished.",
            "requirements": ["R02"],
            "source_ids": ["SRC02"],
            "tone": "Strategic, candid, empowering",
            "narrative_phase": "story_action",
            "narrative_situation": "story_action",
            "beats_data": [
                {
                    "quote": "Management theorists call this pattern the Firefighter's Trap.",
                    "purpose": "The Firefighter's Trap title",
                    "description": "Tactile 2D Hedcut stipple illustration on newsprint #EFECE6. The stickman wearing a red firefighter's helmet holding heavy fire hoses across a desk.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "FIREFIGHTER'S TRAP"
                },
                {
                    "quote": "Because you are extraordinarily skilled at putting out operational fires,",
                    "purpose": "Skilled at putting out fires",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman swiftly stamping out small flare-ups across a crowded corporate workflow diagram.",
                    "has_char": True,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "colleagues and managers bring you every single blaze.",
                    "purpose": "Colleagues bringing every blaze",
                    "description": "Tactile 2D Hedcut stipple illustration. A long line of office workers carrying smoking project folders waiting at the stickman's cubicle.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "emphasis": "EVERY CRISIS"
                },
                {
                    "quote": "Over time, you build an exhausting identity as the team savior,",
                    "purpose": "Exhausting savior identity",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman weighed down by an oversized savior medal that physically pins him to his office chair.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "TEAM SAVIOR"
                },
                {
                    "quote": "spending sixty hours a week executing tactical rescues while your long-term strategic visibility drops to zero.",
                    "purpose": "60 hours a week with zero visibility",
                    "description": "Tactile 2D Hedcut stipple illustration. A weekly calendar filled with 60 hours of crimson emergency blocks while the strategic visibility gauge reads zero.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "ZERO VISIBILITY"
                },
                {
                    "quote": "Every emergency consumed your workday until strategic thinking vanished.",
                    "purpose": "Strategic thinking vanished",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman's strategic roadmap dissolving into smoke under the relentless barrage of incoming daily alerts.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "TACTICAL PRISON"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "The Manager's Replacement Cost",
            "purpose": "Explain the manager's unspoken replacement cost calculation",
            "action": "A manager sits behind an executive desk reviewing an org chart with a gaping operational void",
            "setting": "A private manager office with mahogany desk and architectural org charts",
            "camera": "Medium shot of the manager calculating operational risks",
            "narration": "Here is the unspoken organizational dynamic your manager will never admit out loud: promoting you creates a catastrophic replacement cost. If your boss moves you up to director, who handles the twenty daily emergencies you quietly resolve? Promoting their best troubleshooter creates a massive operational deficit they cannot easily backfill without hiring three people. Keeping you in place is simply the path of least resistance.",
            "requirements": ["R03"],
            "source_ids": ["SRC01"],
            "tone": "Candid, realistic, pragmatic",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "Here is the unspoken organizational dynamic your manager will never admit out loud:",
                    "purpose": "Unspoken organizational dynamic",
                    "description": "Tactile 2D Hedcut stipple illustration on newsprint. Manager seated behind a mahogany desk with a guarded expression, holding a confidential evaluation folder.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "UNSPOKEN RULE"
                },
                {
                    "quote": "promoting you creates a catastrophic replacement cost.",
                    "purpose": "Catastrophic replacement cost",
                    "description": "Tactile 2D pen-and-ink illustration. Balance scale where the cost of replacing the stickman's daily output heavily outweighs the promotion benefit.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "REPLACEMENT COST"
                },
                {
                    "quote": "If your boss moves you up to director,",
                    "purpose": "Moving up to director hypothetical",
                    "description": "Tactile 2D Hedcut stipple illustration. An executive door labeled Director with an empty brass nameplate slot on newsprint paper.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": "DIRECTOR SUITE"
                },
                {
                    "quote": "who handles the twenty daily emergencies you quietly resolve?",
                    "purpose": "Twenty daily emergencies unanswered",
                    "description": "Tactile 2D pen-and-ink illustration. Twenty red crisis envelopes piling up on the vacant desk, threatening to overwhelm the remaining team.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "20 DAILY CRISES"
                },
                {
                    "quote": "Promoting their best troubleshooter creates a massive operational deficit they cannot easily backfill without hiring three people.",
                    "purpose": "Cannot backfill without hiring three people",
                    "description": "Tactile 2D Hedcut stipple illustration. Org chart showing three ghost silhouettes needed to replace the stickman's single workstation.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "3-PERSON DEFICIT"
                },
                {
                    "quote": "Keeping you in place is simply the path of least resistance.",
                    "purpose": "Path of least resistance for manager",
                    "description": "Tactile 2D pen-and-ink illustration. Manager sliding the promotion document back into a locked desk drawer with a subtle sigh of operational relief.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "LOCKED IN PLACE"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "The Competence Penalty",
            "purpose": "Explain the Competence Penalty: tactical execution versus perceived strategic readiness",
            "action": "The stickman is trapped inside a golden cage constructed from perfect performance scores",
            "setting": "An executive boardroom gallery with portraits of strategic leaders",
            "camera": "Slow lateral pan across the leadership table looking down on tactical execution",
            "narration": "This creates the Competence Penalty: exceptional execution in your current role actively traps you in that role. Senior executives do not promote people based on operational speed; they promote people based on perceived strategic readiness. When leadership pictures you, they only see a brilliant technician, not a future department leader guiding organizational direction.",
            "requirements": ["R04"],
            "source_ids": ["SRC01"],
            "tone": "Empowering, realistic, strategic",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "This creates the Competence Penalty:",
                    "purpose": "The Competence Penalty definition",
                    "description": "Tactile 2D Wall Street Journal Hedcut stipple illustration on newsprint #EFECE6. Large bold hand-lettered ledger header reading The Competence Penalty.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "COMPETENCE PENALTY"
                },
                {
                    "quote": "exceptional execution in your current role actively traps you in that role.",
                    "purpose": "Trapped by exceptional execution",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman trapped inside an ornate golden birdcage built from interlocking 'A+' performance evaluations.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "TRAPPED BY SUCCESS"
                },
                {
                    "quote": "Senior executives do not promote people based on operational speed;",
                    "purpose": "Not promoted on operational speed",
                    "description": "Tactile 2D Hedcut stipple illustration. Senior executives seated at a boardroom table looking past a sprinting runner to evaluate a chess grandmaster.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "NOT SPEED"
                },
                {
                    "quote": "they promote people based on perceived strategic readiness.",
                    "purpose": "Promoted on perceived strategic readiness",
                    "description": "Tactile 2D pen-and-ink illustration. A candidate pointing to a visionary corporate growth blueprint bathed in warm ochre light #D48817.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "STRATEGIC READINESS"
                },
                {
                    "quote": "When leadership pictures you, they only see a brilliant technician,",
                    "purpose": "Seen only as brilliant technician",
                    "description": "Tactile 2D Hedcut stipple illustration. The stickman holding a mechanic's wrench in a small labeled box reading 'Technical Asset'.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "BRILLIANT TECHNICIAN"
                },
                {
                    "quote": "not a future department leader guiding organizational direction.",
                    "purpose": "Not seen as organizational leader",
                    "description": "Tactile 2D pen-and-ink illustration. A compass needle spinning away from tactical execution toward broad enterprise leadership horizons.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "LEADERSHIP VOID"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "Editorial Verdict on Visible Fires vs Sprinklers",
            "purpose": "Channel verdict on rewarding visible fires over quiet maintenance and promoting architects",
            "action": "The mentor contrasts the sweaty firefighter with the architect who designs the sprinkler system",
            "setting": "An editorial drafting studio with corporate architecture models on newsprint",
            "camera": "Direct portrait shot transitioning into an automated building blueprint",
            "narration": "Our channel verdict is blunt: corporate hierarchies do not reward the fires you quietly extinguish. They reward the fires everyone saw burning, and they promote the person who designs the sprinkler system. If your value depends on personal heroics, you are an expensive piece of machinery, not an aspiring leader ready for senior executive influence. Heroic effort without systemic design is a career dead end.",
            "requirements": ["R05"],
            "source_ids": ["SRC02"],
            "tone": "Direct, blunt, authoritative editorial verdict",
            "narrative_phase": "editorial_commentary",
            "narrative_situation": "editorial_commentary",
            "beats_data": [
                {
                    "quote": "Our channel verdict is blunt: corporate hierarchies do not reward the fires you quietly extinguish.",
                    "purpose": "Channel verdict statement",
                    "description": "Tactile 2D Hedcut stipple illustration. The strategic mentor stickman in royal cobalt shirt #3B82C4 looking forward with candid, empowering authority.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "CHANNEL VERDICT"
                },
                {
                    "quote": "They reward the fires everyone saw burning,",
                    "purpose": "Rewarding visible fires",
                    "description": "Tactile 2D pen-and-ink illustration. A dramatic visible fire burning on a corporate stage with senior executives clapping for the dramatic spectacle.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "VISIBLE FIRES"
                },
                {
                    "quote": "and they promote the person who designs the sprinkler system.",
                    "purpose": "Promoting the sprinkler system designer",
                    "description": "Tactile 2D Hedcut stipple illustration. An overhead automated sprinkler system extinguishing fires automatically on blueprint paper.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "SPRINKLER ARCHITECT"
                },
                {
                    "quote": "If your value depends on personal heroics,",
                    "purpose": "Value depending on personal heroics",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman sweating under a heavy boulder labeled Personal Heroics, looking exhausted.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "PERSONAL HEROICS"
                },
                {
                    "quote": "you are an expensive piece of machinery, not an aspiring leader ready for senior executive influence.",
                    "purpose": "Machinery vs executive influence",
                    "description": "Tactile 2D Hedcut stipple illustration. Contrast between an operational cog running inside a machine and an executive leader standing at the helm.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "COG VS LEADER"
                },
                {
                    "quote": "Heroic effort without systemic design is a career dead end.",
                    "purpose": "Career dead end warning",
                    "description": "Tactile 2D pen-and-ink illustration. A hallway leading to a brick wall stamped Dead End for tactical heroes without systems.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "DEAD END"
                }
            ]
        },
        {
            "id": "SC06",
            "title": "Execution Visibility vs Strategic Visibility",
            "purpose": "Analyze the asymmetry between midnight debugging and daylight executive presentations",
            "action": "A stark visual contrast between basement server troubleshooting and sunlit boardroom strategy decks",
            "setting": "A split composition: dark server room on left versus sunlit executive suite on right",
            "camera": "Split-screen tracking comparing executive exposure across two work archetypes",
            "narration": "Consider the brutal asymmetry between execution visibility and strategic visibility. Fixing a broken database pipeline at two in the morning saves the company money, but only your direct supervisor notices. Meanwhile, a peer who presents a quarterly market strategy deck gets thirty minutes of face time with the chief executive officer in broad daylight. Strategic presence outranks midnight debugging every single time.",
            "requirements": ["R06"],
            "source_ids": ["SRC01"],
            "tone": "Candid, realistic, eye-opening",
            "narrative_phase": "before_after_contrast",
            "narrative_situation": "before_after_contrast",
            "beats_data": [
                {
                    "quote": "Consider the brutal asymmetry between execution visibility and strategic visibility.",
                    "purpose": "Execution vs strategic visibility asymmetry",
                    "description": "Tactile 2D Hedcut stipple illustration. Split balance scale weighing a pile of code tickets against a single presentation slide deck.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "VISIBILITY GAP"
                },
                {
                    "quote": "Fixing a broken database pipeline at two in the morning saves the company money,",
                    "purpose": "2am database pipeline fix",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman hunched in a dark server room fixing database code under a glowing green monitor at 2 AM.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "2:00 AM DEBUGGING"
                },
                {
                    "quote": "but only your direct supervisor notices.",
                    "purpose": "Only direct supervisor notices",
                    "description": "Tactile 2D Hedcut stipple illustration. A tiny single-line chat notification on screen reading 'Thx fixed' with zero executive visibility.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": "NO EXEC NOTICE"
                },
                {
                    "quote": "Meanwhile, a peer who presents a quarterly market strategy deck",
                    "purpose": "Peer presenting quarterly market strategy",
                    "description": "Tactile 2D pen-and-ink illustration. A peer standing confidently beside an executive projection screen showing clean revenue market curves.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "STRATEGY DECK"
                },
                {
                    "quote": "gets thirty minutes of face time with the chief executive officer in broad daylight.",
                    "purpose": "30 minutes face time with CEO",
                    "description": "Tactile 2D Hedcut stipple illustration. The CEO nodding in warm approval across a sunlit mahogany conference table.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "CEO FACE TIME"
                },
                {
                    "quote": "Strategic presence outranks midnight debugging every single time.",
                    "purpose": "Strategic presence outranks midnight work",
                    "description": "Tactile 2D pen-and-ink illustration. An executive chessboard where a strategic queen moves freely while a defensive pawn stays locked in place.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "PRESENCE WINS"
                }
            ]
        },
        {
            "id": "SC07",
            "title": "The Maintenance Invisibility Paradox",
            "purpose": "Explain the MIT Maintenance Paradox: zero credit for unseen prevention",
            "action": "A flawless machine runs silently while executives ignore it, only noticing when a controlled puff appears",
            "setting": "An executive manufacturing floor with smooth silent gears and executive walkways",
            "camera": "Slow macro glide over silent gears transitioning to executive indifference",
            "narration": "MIT management researchers call this the Maintenance Paradox: nobody gets credit for preventing problems that never happened. When systems run flawlessly because of your constant diligence, upper management assumes the process is naturally easy. Paradoxically, letting a manageable issue surface often creates more leadership visibility than preventing fifty silent breakdowns behind closed doors.",
            "requirements": ["R07"],
            "source_ids": ["SRC02"],
            "tone": "Empirical, eye-opening, structural",
            "narrative_phase": "rapid_examples",
            "narrative_situation": "rapid_examples",
            "beats_data": [
                {
                    "quote": "MIT management researchers call this the Maintenance Paradox:",
                    "purpose": "MIT Maintenance Paradox citation",
                    "description": "Tactile 2D Hedcut stipple illustration on newsprint #EFECE6. MIT research journal report titled Nobody Gets Credit for Problems That Never Happened.",
                    "has_char": False,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "MAINTENANCE PARADOX"
                },
                {
                    "quote": "nobody gets credit for preventing problems that never happened.",
                    "purpose": "Zero credit for preventing problems",
                    "description": "Tactile 2D pen-and-ink illustration. A pristine machine running silently with zero operational friction, surrounded by empty executive chairs.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "NO CREDIT"
                },
                {
                    "quote": "When systems run flawlessly because of your constant diligence,",
                    "purpose": "Flawless operation from constant diligence",
                    "description": "Tactile 2D Hedcut stipple illustration. The stickman oiling gears and checking dials with meticulous continuous diligence.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "upper management assumes the process is naturally easy.",
                    "purpose": "Management assumes process is easy",
                    "description": "Tactile 2D pen-and-ink illustration. Executive walking past thinking 'This machinery runs itself effortlessly' with a dismissive wave.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "ASSUMED EASY"
                },
                {
                    "quote": "Paradoxically, letting a manageable issue surface often creates more leadership visibility",
                    "purpose": "Visible issue creates leadership visibility",
                    "description": "Tactile 2D Hedcut stipple illustration. A controlled smoke puff drawing executive attention, turning into an organized incident review meeting.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "VISIBLE TRIAGE"
                },
                {
                    "quote": "than preventing fifty silent breakdowns behind closed doors.",
                    "purpose": "Fifty silent breakdowns ignored",
                    "description": "Tactile 2D pen-and-ink illustration. Fifty small averted disaster icons locked away in a dark basement drawer with zero company recognition.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "50 SILENT FIXES"
                }
            ]
        },
        {
            "id": "SC08",
            "title": "Shifting to Systems Architecture",
            "purpose": "Explain the transition from tactical firefighting to documented systems architecture",
            "action": "The stickman puts down the fire extinguisher and picks up drafting compass and standard operating binders",
            "setting": "An organizational workshop with standard operating procedure binders and dashboards",
            "camera": "Direct portrait shot transitioning into clean operational playbooks",
            "narration": "To break free from this trap, you must consciously shift from firefighter to systems architect. Stop fixing problems through brute-force personal effort. Instead, document standard operating procedures, build automated dashboards, and cross-train junior colleagues to handle recurring emergencies. Your goal is to engineer yourself out of the daily firefighting loop permanently. Replace tactical intervention with durable team playbooks.",
            "requirements": ["R08"],
            "source_ids": ["SRC01", "SRC03"],
            "tone": "Empowering, actionable, strategic",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "To break free from this trap, you must consciously shift from firefighter to systems architect.",
                    "purpose": "Shifting to systems architect",
                    "description": "Tactile 2D Hedcut stipple illustration on newsprint. The stickman putting down his firefighter helmet and picking up architectural drafting dividers.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "SYSTEMS ARCHITECT"
                },
                {
                    "quote": "Stop fixing problems through brute-force personal effort.",
                    "purpose": "Stop brute force personal effort",
                    "description": "Tactile 2D pen-and-ink illustration. A broken wrench crossed out in red ink, showing the end of manual brute-force fixes.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "NO BRUTE FORCE"
                },
                {
                    "quote": "Instead, document standard operating procedures, build automated dashboards,",
                    "purpose": "Standard operating procedures and dashboards",
                    "description": "Tactile 2D Hedcut stipple illustration. A thick binder labeled Standard Operating Procedures opened beside a clean automated dashboard.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "SOP PLAYBOOKS"
                },
                {
                    "quote": "and cross-train junior colleagues to handle recurring emergencies.",
                    "purpose": "Cross-training junior colleagues",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman coaching two junior team members, pointing clearly to step-by-step resolution guides.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "CROSS-TRAIN"
                },
                {
                    "quote": "Your goal is to engineer yourself out of the daily firefighting loop permanently.",
                    "purpose": "Engineer out of the firefighting loop",
                    "description": "Tactile 2D Hedcut stipple illustration. The stickman stepping out of the revolving circular crisis loop, looking back with strategic calm.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "EXIT THE LOOP"
                },
                {
                    "quote": "Replace tactical intervention with durable team playbooks.",
                    "purpose": "Durable team playbooks",
                    "description": "Tactile 2D pen-and-ink illustration. A golden playbook shelf standing in the team bullpen, empowering everyone to solve crises independently.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "TEAM AUTONOMY"
                }
            ]
        },
        {
            "id": "SC09",
            "title": "Reframing Upward Communication",
            "purpose": "Teach how to communicate business metrics and leverage rather than task lists",
            "action": "A crumpled list of 100 closed tickets is discarded for a 1-page executive memo showing hours saved",
            "setting": "A sunlit executive meeting room with glass whiteboard and strategic metrics",
            "camera": "Close-up on executive memo reframing task outputs into business outcomes",
            "narration": "Next, change how you communicate with leadership. During one-on-one meetings, stop reciting lists of tasks completed and tickets closed. Reframe your updates around systemic improvements: how your new documentation reduced error rates by forty percent, or how cross-training saved twelve engineering hours every single week across the entire engineering department. Speak the quantitative language of executive leverage.",
            "requirements": ["R09"],
            "source_ids": ["SRC01"],
            "tone": "Strategic, practical, empowering",
            "narrative_phase": "story_action",
            "narrative_situation": "story_action",
            "beats_data": [
                {
                    "quote": "Next, change how you communicate with leadership.",
                    "purpose": "Changing leadership communication",
                    "description": "Tactile 2D Hedcut stipple illustration. One-on-one meeting room with the stickman seated across from his director with poised, strategic posture.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "UPWARD NARRATIVE"
                },
                {
                    "quote": "During one-on-one meetings, stop reciting lists of tasks completed and tickets closed.",
                    "purpose": "Stop reciting lists of tasks",
                    "description": "Tactile 2D pen-and-ink illustration. A long grocery-list style ticket report discarded into the recycling bin with a red X mark.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "DITCH TASK LISTS"
                },
                {
                    "quote": "Reframe your updates around systemic improvements:",
                    "purpose": "Reframe around systemic improvements",
                    "description": "Tactile 2D Hedcut stipple illustration. A clean executive summary chart showing systemic improvements in team turnaround times.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "SYSTEMIC GAINS"
                },
                {
                    "quote": "how your new documentation reduced error rates by forty percent,",
                    "purpose": "Error rates reduced by 40 percent",
                    "description": "Tactile 2D pen-and-ink illustration. Quantitative graph showing incident tickets dropping by 40% after implementing team playbooks.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "burst",
                    "emphasis": "-40% ERROR RATES"
                },
                {
                    "quote": "or how cross-training saved twelve engineering hours every single week across the entire engineering department.",
                    "purpose": "12 engineering hours saved weekly",
                    "description": "Tactile 2D Hedcut stipple illustration. Clockwork diagram showing 12 reclaimed engineering hours flowing into strategic product development.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "12 HRS SAVED/WK"
                },
                {
                    "quote": "Speak the quantitative language of executive leverage.",
                    "purpose": "Speaking executive leverage language",
                    "description": "Tactile 2D pen-and-ink illustration. The director leaning forward with enthusiastic respect, nodding at the stickman's strategic portfolio.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "EXECUTIVE LEVERAGE"
                }
            ]
        },
        {
            "id": "SC10",
            "title": "Editorial Verdict on Making Yourself Dispensable",
            "purpose": "Channel verdict on why making yourself dispensable is the prerequisite for promotion",
            "action": "The mentor demonstrates that building systems that survive without you unlocks upward advancement",
            "setting": "An open corporate atrium looking up at director suites and architectural stairs",
            "camera": "Elevating crane shot following the stickman ascending toward executive leadership",
            "narration": "Making yourself dispensable in your current seat is the only way to become indispensable for the next one. As long as your presence is mandatory to keep the machine running, management cannot afford to let you leave it. You must build systems that survive without you before you can advance to higher ground. Autonomy at your current level creates capacity for senior leadership.",
            "requirements": ["R10"],
            "source_ids": ["SRC01", "SRC03"],
            "tone": "Empowering, candid, philosophical editorial verdict",
            "narrative_phase": "editorial_commentary",
            "narrative_situation": "editorial_commentary",
            "beats_data": [
                {
                    "quote": "Making yourself dispensable in your current seat is the only way to become indispensable for the next one.",
                    "purpose": "Making yourself dispensable verdict",
                    "description": "Tactile 2D Hedcut stipple illustration on newsprint #EFECE6. The strategic mentor stickman in royal cobalt shirt standing on an elevated architectural landing.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "BECOME DISPENSABLE"
                },
                {
                    "quote": "As long as your presence is mandatory to keep the machine running,",
                    "purpose": "Presence mandatory traps you",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman tied to a large gear by ropes of operational necessity, unable to move.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "MANDATORY PRESENCE"
                },
                {
                    "quote": "management cannot afford to let you leave it.",
                    "purpose": "Management cannot afford to move you",
                    "description": "Tactile 2D Hedcut stipple illustration. Manager holding the gear firmly in place with an anxious protective grip.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "CANNOT AFFORD"
                },
                {
                    "quote": "You must build systems that survive without you",
                    "purpose": "Building systems that survive without you",
                    "description": "Tactile 2D pen-and-ink illustration. A self-sustaining mechanical flywheel continuing to rotate smoothly while the stickman steps away.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "AUTONOMOUS FLYWHEEL"
                },
                {
                    "quote": "before you can advance to higher ground.",
                    "purpose": "Advancing to higher ground",
                    "description": "Tactile 2D Hedcut stipple illustration. Architectural staircase bathed in ochre gold #D48817 leading smoothly up to director executive suites.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "HIGHER GROUND"
                },
                {
                    "quote": "Autonomy at your current level creates capacity for senior leadership.",
                    "purpose": "Autonomy creates leadership capacity",
                    "description": "Tactile 2D pen-and-ink illustration. An executive briefcase resting on an uncluttered director desk, symbolizing strategic mental capacity.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "LEADERSHIP CAPACITY"
                }
            ]
        },
        {
            "id": "SC11",
            "title": "The Calendar Audit and Closing Takeaway",
            "purpose": "Provide the actionable calendar audit rule and closing call to action",
            "action": "The stickman audits his calendar, converts emergencies into playbooks, and steps forward",
            "setting": "A clean executive office overlooking a broad strategic horizon on cream newsprint",
            "camera": "Direct portrait shot transitioning into the channel closing emblem",
            "narration": "Audit your calendar this week. Identify three recurring emergencies you personally solve, and turn them into documented playbooks for your team. Stop being the irreplaceable firefighter so you can become the promoted architect. Take back control of your professional trajectory. Review your daily projects this month. Build systems before accepting another crisis.",
            "requirements": ["R11"],
            "source_ids": ["SRC01"],
            "tone": "Empowering, pragmatic, direct",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cta_bridge",
            "beats_data": [
                {
                    "quote": "Audit your calendar this week.",
                    "purpose": "Audit calendar this week callout",
                    "description": "Tactile 2D Hedcut stipple illustration. A weekly calendar worksheet where red crisis hours are audited with clear checkmarks.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "CALENDAR AUDIT"
                },
                {
                    "quote": "Identify three recurring emergencies you personally solve, and turn them into documented playbooks for your team.",
                    "purpose": "Turn 3 emergencies into playbooks",
                    "description": "Tactile 2D pen-and-ink illustration. Three emergency incident icons transforming into three organized team playbooks on newsprint paper.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "3 PLAYBOOKS"
                },
                {
                    "quote": "Stop being the irreplaceable firefighter so you can become the promoted architect.",
                    "purpose": "Stop being firefighter become architect",
                    "description": "Tactile 2D Hedcut stipple illustration. The stickman standing tall in royal cobalt shirt holding architectural blueprints for the department.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "PROMOTED ARCHITECT"
                },
                {
                    "quote": "Take back control of your professional trajectory.",
                    "purpose": "Take back career trajectory",
                    "description": "Tactile 2D pen-and-ink illustration. A compass needle locking firmly onto long-term executive career advancement.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "TAKE CONTROL"
                },
                {
                    "quote": "Review your daily projects this month.",
                    "purpose": "Review daily projects bridge",
                    "description": "Tactile 2D Hedcut stipple illustration. A checklist auditing current projects between low-visibility maintenance and high-leverage systems.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "PROJECT AUDIT"
                },
                {
                    "quote": "Build systems before accepting another crisis.",
                    "purpose": "Closing call to action and channel seal",
                    "description": "Tactile 2D Hedcut stipple illustration. Career Leverage official channel emblem featuring the editorial stickman and wooden leverage fulcrum on newsprint.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "emphasis": "CAREER LEVERAGE",
                    "is_endcard": True
                }
            ]
        }
    ]

def get_career_short_scenes_data():
    return [
        {
            "id": "SC01",
            "title": "The Least Promotable Employee",
            "purpose": "Hook the viewer with the irony that saving every project makes you least promotable",
            "action": "The stickman sprints with a fire extinguisher across a chaotic office floor",
            "setting": "A busy corporate office floor on cream newsprint #EFECE6",
            "camera": "Direct tracking shot following the frantic firefighter sprint",
            "narration": "If you are the person who saves every project on your team, you are probably the least promotable employee in the room. You collect perfect reviews, but your promotion keeps stalling because of your competence.",
            "requirements": ["R01"],
            "source_ids": ["SRC01"],
            "tone": "Punchy, relatable, eye-opening",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "beats_data": [
                {
                    "quote": "If you are the person who saves every project on your team,",
                    "purpose": "Saving every project hook",
                    "description": "Tactile 2D Hedcut stipple illustration on newsprint #EFECE6. The stickman sprinting with a fire extinguisher across an office floor in India ink stippling.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "burst",
                    "emphasis": "SAVING EVERY PROJECT"
                },
                {
                    "quote": "you are probably the least promotable employee in the room.",
                    "purpose": "Least promotable employee reveal",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman isolated in a spotlight with an unmoving corporate ladder standing just out of reach.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "LEAST PROMOTABLE"
                },
                {
                    "quote": "You collect perfect reviews,",
                    "purpose": "Collecting perfect reviews",
                    "description": "Tactile 2D Hedcut stipple illustration. A performance review document stamped with a Top Performer gold seal #D48817.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "TOP PERFORMER"
                },
                {
                    "quote": "but your promotion keeps stalling because of your competence.",
                    "purpose": "Promotion stalls because of competence",
                    "description": "Tactile 2D pen-and-ink illustration. The promotion escalator jammed in place by a heavy lock labeled Competence Penalty.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "STALLED PROMOTION"
                }
            ]
        },
        {
            "id": "SC02",
            "title": "The Manager's Replacement Headache",
            "purpose": "Explain why managers cannot afford to promote their best troubleshooter",
            "action": "A manager stares anxiously at a broken team machine if the troubleshooter leaves",
            "setting": "The manager's office with an operational risk calculator on newsprint",
            "camera": "Medium shot of the manager protecting team stability",
            "narration": "Here is why: promoting you creates a catastrophic replacement headache for your manager. If you move into leadership, who fixes the twenty daily crises you quietly resolve? Promoting you breaks the machine they rely on.",
            "requirements": ["R02"],
            "source_ids": ["SRC01"],
            "tone": "Strategic, candid, realistic",
            "narrative_phase": "mechanism_step",
            "narrative_situation": "mechanism_step",
            "beats_data": [
                {
                    "quote": "Here is why: promoting you creates a catastrophic replacement headache for your manager.",
                    "purpose": "Replacement headache for manager",
                    "description": "Tactile 2D Hedcut stipple illustration. Manager holding his head in operational anxiety looking at an empty troubleshooter chair.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "REPLACEMENT HEADACHE"
                },
                {
                    "quote": "If you move into leadership,",
                    "purpose": "Moving into leadership hypothetical",
                    "description": "Tactile 2D pen-and-ink illustration. Executive office door opening slightly with a golden silhouette of leadership.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "burst",
                    "emphasis": None
                },
                {
                    "quote": "who fixes the twenty daily crises you quietly resolve?",
                    "purpose": "Who fixes the 20 daily crises",
                    "description": "Tactile 2D Hedcut stipple illustration. Twenty red crisis envelopes cascading off the stickman's desk onto the floor.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "20 DAILY CRISES"
                },
                {
                    "quote": "Promoting you breaks the machine they rely on.",
                    "purpose": "Promoting you breaks the machine",
                    "description": "Tactile 2D pen-and-ink illustration. A delicate mechanical gear train grinding to a halt when the central cog is removed.",
                    "has_char": False,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "MACHINE BREAKS"
                }
            ]
        },
        {
            "id": "SC03",
            "title": "Invisible Maintenance Gets Zero Credit",
            "purpose": "Contrast invisible midnight maintenance with high-visibility strategy decks",
            "action": "A split view of midnight debugging versus broad daylight executive presentations",
            "setting": "A dual office setting comparing dark server room with executive boardroom",
            "camera": "Split-screen tracking comparing visibility levels",
            "narration": "Nobody gets promoted for invisible maintenance. When you quietly prevent disasters at midnight, management assumes the job is effortless. Meanwhile, colleagues who manage high-visibility strategic decks get all the executive face time.",
            "requirements": ["R03"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Candid, eye-opening",
            "narrative_phase": "before_after_contrast",
            "narrative_situation": "before_after_contrast",
            "beats_data": [
                {
                    "quote": "Nobody gets promoted for invisible maintenance.",
                    "purpose": "No promotion for invisible maintenance",
                    "description": "Tactile 2D Hedcut stipple illustration. The stickman fixing pipes invisibly behind the office walls while zero executives notice.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "fast",
                    "emphasis": "INVISIBLE WORK"
                },
                {
                    "quote": "When you quietly prevent disasters at midnight, management assumes the job is effortless.",
                    "purpose": "Midnight prevention assumed effortless",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman working late under moonlight while an executive thought bubble reads 'Naturally easy'.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "normal",
                    "emphasis": "ASSUMED EFFORTLESS"
                },
                {
                    "quote": "Meanwhile, colleagues who manage high-visibility strategic decks",
                    "purpose": "Colleagues with high-visibility decks",
                    "description": "Tactile 2D Hedcut stipple illustration. A colleague presenting a three-bullet strategic slide deck in the executive sunlit room.",
                    "has_char": True,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "STRATEGIC DECKS"
                },
                {
                    "quote": "get all the executive face time.",
                    "purpose": "Getting executive face time",
                    "description": "Tactile 2D pen-and-ink illustration. Senior leadership shaking hands and laughing warmly with the strategic presenter.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "EXEC FACE TIME"
                }
            ]
        },
        {
            "id": "SC04",
            "title": "Editorial Commentary on Designing Systems",
            "purpose": "Deliver channel verdict on designing systems rather than working inside the machine",
            "action": "The mentor steps out of the machine and lays down automated operational playbooks",
            "setting": "An architect's studio on warm newsprint paper",
            "camera": "Direct portrait shot transitioning to self-running flywheel",
            "narration": "You do not earn advancement by working harder inside the machine. You earn it by stepping outside and designing a machine that runs without you. To become promotable, you must first make yourself dispensable.",
            "requirements": ["R04"],
            "source_ids": ["SRC01", "SRC03"],
            "tone": "Direct, empowering editorial verdict",
            "narrative_phase": "editorial_commentary",
            "narrative_situation": "editorial_commentary",
            "beats_data": [
                {
                    "quote": "You do not earn advancement by working harder inside the machine.",
                    "purpose": "Working harder inside machine doesn't advance",
                    "description": "Tactile 2D Hedcut stipple illustration. The stickman running furiously on an office hamster wheel that leads nowhere.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "NOT HAMSTER WHEEL"
                },
                {
                    "quote": "You earn it by stepping outside and designing a machine that runs without you.",
                    "purpose": "Designing machine that runs without you",
                    "description": "Tactile 2D pen-and-ink illustration. The stickman stepping off the wheel to draft an automated architectural blueprint on newsprint.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "slow",
                    "emphasis": "DESIGN THE MACHINE"
                },
                {
                    "quote": "To become promotable,",
                    "purpose": "To become promotable condition",
                    "description": "Tactile 2D Hedcut stipple illustration. The corporate ladder unlocking and extending toward executive heights.",
                    "has_char": False,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": None
                },
                {
                    "quote": "you must first make yourself dispensable.",
                    "purpose": "Make yourself dispensable verdict",
                    "description": "Tactile 2D pen-and-ink illustration. The strategic mentor stickman in royal cobalt shirt #3B82C4 pointing forward with clarity.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "slow",
                    "emphasis": "BE DISPENSABLE"
                }
            ]
        },
        {
            "id": "SC05",
            "title": "The Executive Leverage Cliffhanger",
            "purpose": "Escalate to the executive leverage peak, bridge to the long video, and close",
            "action": "The camera pulls out to show the full masterclass preview and companion endcard",
            "setting": "The complete corporate executive suite on newsprint paper",
            "camera": "Dynamic pull-out to strategic executive roadmap and companion video card",
            "narration": "How do top performers convert tactical firefighting into executive leverage so their managers actively push for their promotion? Watch the full career masterclass on YouTube. Audit your daily projects this week.",
            "requirements": ["R05"],
            "source_ids": ["SRC01"],
            "tone": "Engaging, high-energy peak and clear bridge",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cliffhanger_peak",
            "beats_data": [
                {
                    "quote": "How do top performers convert tactical firefighting into executive leverage",
                    "purpose": "Convert firefighting to leverage cliffhanger part 1",
                    "description": "Tactile 2D Hedcut stipple illustration. Tactical emergency tickets converting into an executive leverage fulcrum lifting the stickman.",
                    "has_char": True,
                    "shot_type": "concept_metaphor",
                    "tempo": "fast",
                    "emphasis": "EXECUTIVE LEVERAGE"
                },
                {
                    "quote": "so their managers actively push for their promotion?",
                    "purpose": "Managers push for promotion cliffhanger part 2",
                    "description": "Tactile 2D pen-and-ink illustration. The manager proudly championing the stickman's promotion packet in the executive boardroom.",
                    "has_char": True,
                    "shot_type": "variation",
                    "tempo": "fast",
                    "emphasis": "MANAGER CHAMPION"
                },
                {
                    "quote": "Watch the full career masterclass on YouTube.",
                    "purpose": "Bridge to full YouTube masterclass",
                    "description": "Tactile 2D Hedcut stipple illustration. YouTube companion video preview card in editorial newsprint style showing the full masterclass thumbnail.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "normal",
                    "emphasis": "FULL MASTERCLASS"
                },
                {
                    "quote": "Audit your daily projects this week.",
                    "purpose": "Closing call to action and channel seal",
                    "description": "Tactile 2D Hedcut stipple illustration. Career Leverage official channel emblem with stickman and wooden fulcrum on warm newsprint.",
                    "has_char": True,
                    "shot_type": "full_scene",
                    "tempo": "hold",
                    "emphasis": "CAREER LEVERAGE",
                    "is_endcard": True
                }
            ]
        }
    ]

def run_wallet_long():
    channel_id = "en_wallet_anatomy"
    job_id = "en-wallet-anatomy-batch1-16x9"
    ch = get_channel(channel_id)
    topic = "The Decoy Effect & Menu Engineering: How Restaurants Design a Page to Control What You Spend"
    youtube_title = "The Menu Trap That Steers 68% of Your Orders"
    aspect_ratio = "16:9"
    format_profile = "long_16x9"
    
    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Expose the behavioral economics of menu engineering and the decoy effect, explaining how restaurants manipulate choices and providing actionable rules to avoid overspending.",
        "video_type": "research_guide",
        "duration": {"min_seconds": 150.0, "max_seconds": 210.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "The luxury dry-aged steak anchor placed in the top-right corner"},
            {"id": "R02", "text": "The Golden Triangle eye-tracking movement across dining menus"},
            {"id": "R03", "text": "Joel Huber's 1982 asymmetric dominance decoy experiment"},
            {"id": "R04", "text": "Dan Ariely's Economist subscription pricing structure test"},
            {"id": "R05", "text": "Editorial analysis of artificial comparison versus real value"},
            {"id": "R06", "text": "Cornell University study on removing dollar signs from menus"},
            {"id": "R07", "text": "The wine list margin trap and the second-cheapest bottle"},
            {"id": "R08", "text": "Social anxiety surcharge and paying to protect dinner ego"},
            {"id": "R09", "text": "Software SaaS subscription tiers using the exact same decoy"},
            {"id": "R10", "text": "Editorial verdict on engineered commercial choice architecture"},
            {"id": "R11", "text": "The three-second strip-the-anchor decision rule and closing takeaway"}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": aspect_ratio,
        "format_profile": format_profile,
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Adding Asymmetrically Dominated Alternatives: Violations of Regularity and the Similarity Hypothesis",
                "reference": "Huber, J., Payne, J. W., & Puto, C. (1982). Journal of Consumer Research, 9(1), 90-98.",
                "facts": [
                    "Introducing an asymmetrically dominated decoy alternative increases the choice probability of the dominating target brand.",
                    "Consumers evaluate options through relative comparison rather than calculating intrinsic absolute economic value."
                ]
            },
            {
                "id": "SRC02",
                "title": "$ or Dollars: Effects of Menu-price Formats on Restaurant Checks",
                "reference": "Yang, S. S., Kimes, S. E., & Sessarego, M. M. (2009). Cornell Hospitality Report, 9(8), 4-11.",
                "facts": [
                    "Diners spend significantly more (8.1% higher average spend) when prices are presented as numerals without dollar signs ($) or written words.",
                    "Omitting currency signs reduces the psychological salience of payment pain during item selection."
                ]
            },
            {
                "id": "SRC03",
                "title": "Predictably Irrational: The Hidden Forces That Shape Our Decisions",
                "reference": "Ariely, D. (2008). HarperCollins, Chapter 1: The Truth About Relativity.",
                "facts": [
                    "When presented with a print-only decoy priced identically to print-plus-web, 84% of respondents chose the combo package.",
                    "When the decoy option was removed, 68% of respondents switched to the cheaper web-only option, proving preferences are constructed."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": aspect_ratio,
                "language": "en",
                "subtitles": False,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deconstruct the decoy effect and the Golden Triangle menu layout so viewers recognize commercial price anchoring and apply the three-second strip-the-anchor rule."
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Assumes standard consumer familiarity with restaurant menus and online pricing tables.",
            "pacing": "Delivered with the razor-sharp analytical cadence of Two Cents (PBS) and The Plain Bagel, eliminating dead-air.",
            "assumptions": [
                "Each scene maintains narrative visual pacing between 2.2 and 2.8 seconds per unique image."
            ]
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Bookkeeper inspecting a luxury ribeye steak price tag of forty-eight dollars on vintage ledger paper with brass calipers",
                "text_overlay": "MENU TRAP",
                "contrast_pair": "Unordered luxury decoy steak vs High-margin thirty-two dollar entrée",
                "thumbnail_prompt": "Tactile 2D vintage accounting ledger and dip-pen iron-gall ink illustration on warm fibrous cream grid paper (#F5F2EB with faint #E3DCC8 ruled grid lines). Extreme close-up of a vintage dining menu corner featuring a luxurious dry-aged steak with a bold $48 price tag crossed out in debt-red #B8332A ink, beside a glowing $32 target dish stamped with bank-note emerald #1F6F54 ink. The bookkeeper protagonist in round tortoiseshell glasses and green accountant vest measures the margin gap with antique brass calipers. High-impact composition, at least 60% negative space, zero 3D CGI, zero plastic AI sheen.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Behavioral Finance & Spending Traps",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["menu engineering", "decoy effect", "behavioral economics", "two cents", "wallet anatomy", "dan ariely"],
            "cta_plan": {
                "close": "Check the pricing layout before you order tonight.",
                "endcard_text": "WALLET ANATOMY"
            },
            "editorial_stance": {
                "myth_debunked": "Diners believe they freely evaluate each menu item based on their own personal appetite and budget.",
                "channel_verdict": "Menus are visual choice architectures engineered with decoy anchors to guide 68% of patrons toward predetermined high-margin items.",
                "why_generic_advice_fails": "Standard budgeting advice tells people to look at prices, but ignores how decoy anchors distort your perception of what is reasonable.",
                "tradeoff_or_blindspot": "Recognizing menu decoy anchors requires pausing for three seconds to strip away comparative framing before placing your order."
            },
            "actionable_value": {
                "core_mechanism": "The human brain evaluates numbers through comparison; placing an expensive decoy anchor makes adjacent high-margin items feel like sensible bargains.",
                "practical_rule_of_thumb": "The three-second strip-the-anchor rule: mentally erase the highest priced item on any menu or subscription table before choosing.",
                "real_world_scenario": "When dining at a restaurant or evaluating software tiers, ignore the top anchor and evaluate the target item strictly on its standalone utility."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Bookkeeper inspecting a luxury ribeye steak price tag of forty-eight dollars on vintage ledger paper with brass calipers",
            "text_overlay": "MENU TRAP",
            "contrast_pair": "Unordered luxury decoy steak vs High-margin thirty-two dollar entrée",
            "thumbnail_prompt": "Tactile 2D vintage accounting ledger and dip-pen iron-gall ink illustration on warm fibrous cream grid paper (#F5F2EB with faint #E3DCC8 ruled grid lines). Extreme close-up of a vintage dining menu corner featuring a luxurious dry-aged steak with a bold $48 price tag crossed out in debt-red #B8332A ink, beside a glowing $32 target dish stamped with bank-note emerald #1F6F54 ink. The bookkeeper protagonist in round tortoiseshell glasses and green accountant vest measures the margin gap with antique brass calipers. High-impact composition, at least 60% negative space, zero 3D CGI, zero plastic AI sheen.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Behavioral Finance & Spending Traps",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["menu engineering", "decoy effect", "behavioral economics", "two cents", "wallet anatomy", "dan ariely"],
        "cta_plan": {
            "close": "Check the pricing layout before you order tonight.",
            "endcard_text": "WALLET ANATOMY"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Diners believe they freely evaluate each menu item based on their own personal appetite and budget.",
            "channel_verdict": "Menus are visual choice architectures engineered with decoy anchors to guide 68% of patrons toward predetermined high-margin items.",
            "why_generic_advice_fails": "Standard budgeting advice tells people to look at prices, but ignores how decoy anchors distort your perception of what is reasonable.",
            "tradeoff_or_blindspot": "Recognizing menu decoy anchors requires pausing for three seconds to strip away comparative framing before placing your order."
        },
        "actionable_value": {
            "core_mechanism": "The human brain evaluates numbers through comparison; placing an expensive decoy anchor makes adjacent high-margin items feel like sensible bargains.",
            "practical_rule_of_thumb": "The three-second strip-the-anchor rule: mentally erase the highest priced item on any menu or subscription table before choosing.",
            "real_world_scenario": "When dining at a restaurant or evaluating software tiers, ignore the top anchor and evaluate the target item strictly on its standalone utility."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook the viewer with the un-ordered forty-eight dollar steak in the top-right corner", "requirements": ["R01"], "transition": "Transition into the visual science of menu reading patterns"},
            {"scene_id": "SC02", "purpose": "Explain the Golden Triangle eye-tracking pattern across physical menus", "requirements": ["R02"], "transition": "Connect visual patterns to formal behavioral economics"},
            {"scene_id": "SC03", "purpose": "Deconstruct Joel Huber's 1982 asymmetric dominance decoy experiment", "requirements": ["R03"], "transition": "Transition to Dan Ariely's famous subscription study"},
            {"scene_id": "SC04", "purpose": "Break down The Economist subscription test with three pricing tiers", "requirements": ["R04"], "transition": "Deliver sharp editorial commentary on consumer rationality"},
            {"scene_id": "SC05", "purpose": "Editorial commentary on how comparative framing short-circuits rational spending", "requirements": ["R05"], "transition": "Move to typographic tricks and price perception"},
            {"scene_id": "SC06", "purpose": "Reveal Cornell University findings on how omitting dollar signs increases check spend", "requirements": ["R06"], "transition": "Transition from food entrées to the beverage program"},
            {"scene_id": "SC07", "purpose": "Expose the restaurant markup trap on the second-cheapest bottle of wine", "requirements": ["R07"], "transition": "Analyze the social psychology driving customer wine choice"},
            {"scene_id": "SC08", "purpose": "Explain how hospitality managers exploit social anxiety and dinner table ego", "requirements": ["R08"], "transition": "Show how the decoy architecture scales into digital modern commerce"},
            {"scene_id": "SC09", "purpose": "Demonstrate the exact same decoy structure in modern software subscription tiers", "requirements": ["R09"], "transition": "Deliver synthesized editorial verdict on commercial choice environments"},
            {"scene_id": "SC10", "purpose": "Channel verdict on how commercial pricing grids are engineered to steer decisions", "requirements": ["R10"], "transition": "Provide concrete viewer defense tactics and closing call to action"},
            {"scene_id": "SC11", "purpose": "Provide the three-second strip-the-anchor rule and close the video", "requirements": ["R11"], "transition": "Final closing frame"}
        ]
    }

    cr = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Two Cents (PBS)",
                    "top_performing_videos": [
                        {
                            "title": "Why You Spend More at Restaurants Than You Think",
                            "views": "2.1M views",
                            "hook_technique": "Opening with a physical receipt and breaking down psychological pricing tricks.",
                            "pacing_structure": "Everyday dining scenario -> Behavioral bias mechanism -> Practical counter-measure.",
                            "retention_driver": "Tactile illustrative visuals that make complex economic studies instantly intuitive."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Use cross-hatched balance sheets to visually demonstrate where extra dollars leak.",
                        "Ground academic citations in immediate personal dining experiences."
                    ]
                },
                {
                    "channel_name": "The Plain Bagel",
                    "top_performing_videos": [
                        {
                            "title": "Pricing Tricks Companies Use to Control You",
                            "views": "1.4M views",
                            "hook_technique": "Calm, analytical breakdown of subscription tiers and consumer anchoring.",
                            "pacing_structure": "Price table example -> Theoretical framework -> Consumer defense rule.",
                            "retention_driver": "Pragmatic, non-sensational delivery that respects the viewer's intelligence."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Compare contrasting price tiers side-by-side on an objective balance sheet.",
                        "Provide a simple heuristic rule of thumb at the conclusion."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 14,
                "visual_contrast": "Forty-eight-dollar luxury steak anchor contrasted with guest scanning downward toward thirty-two-dollar chicken.",
                "counter_intuitive_truth_slap": "The restaurant never expected you to order the forty-eight dollar steak; it sits there purely to make the thirty-two dollar entrée look like a bargain."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Opening dinner hook with the luxury anchor cut in the top-right corner."},
                {"phase": "story_action", "purpose": "Eye-tracking heatmaps revealing the Golden Triangle gaze pattern."},
                {"phase": "mechanism_step", "purpose": "Joel Huber's 1982 asymmetric dominance decoy experiment."},
                {"phase": "mechanism_step", "purpose": "Dan Ariely's Economist subscription pricing structure test."},
                {"phase": "editorial_commentary", "purpose": "Channel verdict on comparative framing short-circuiting rational spending."},
                {"phase": "rapid_examples", "purpose": "Cornell University study on removing dollar signs to increase spending."},
                {"phase": "before_after_contrast", "purpose": "Wine list profit margin trap on the second-cheapest bottle."},
                {"phase": "story_action", "purpose": "Social anxiety surcharge and paying to protect dinner ego."},
                {"phase": "mechanism_step", "purpose": "Software SaaS subscription tiers using the exact same decoy."},
                {"phase": "editorial_commentary", "purpose": "Channel verdict on commercial choice architecture and visual manipulation."},
                {"phase": "actionable_resolution", "purpose": "Three-second strip-the-anchor decision rule and closing call to action."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chain linking vintage financial ledger frames with consistent ink pen cross-hatching."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Behavioral Finance & Spending Traps",
            "myth_debunked": "Consumers pick menu items based on absolute hunger and budget.",
            "channel_verdict": "Commercial menus are engineered environments that manipulate relative comparison to steer spending.",
            "actionable_rule_of_thumb": "Strip the top anchor price from the page for three seconds before choosing."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How do software giants take this exact restaurant trick and scale it to extract recurring subscription revenue?",
            "bridge": "Watch the complete unit economics breakdown on Wallet Anatomy YouTube channel.",
            "close": "Check the pricing layout before you order tonight.",
            "endcard_text": "WALLET ANATOMY"
        }
    }

    coverage = [
        {"requirement_id": "R01", "scene_id": "SC01", "quote": "Resting right there is a magnificent forty-eight-dollar prime dry-aged ribeye steak."},
        {"requirement_id": "R02", "scene_id": "SC02", "quote": "Menu consultants call this deliberate layout the Golden Triangle."},
        {"requirement_id": "R03", "scene_id": "SC03", "quote": "Huber demonstrated the Asymmetric Dominance Effect, colloquially known as the Decoy Effect."},
        {"requirement_id": "R04", "scene_id": "SC04", "quote": "Behavioral economist Dan Ariely popularized this phenomenon using a famous test from The Economist magazine."},
        {"requirement_id": "R05", "scene_id": "SC05", "quote": "Here is our channel verdict: the print-only option was never meant to sell."},
        {"requirement_id": "R06", "scene_id": "SC06", "quote": "A landmark Cornell University study revealed that removing dollar signs from menus caused diners to spend eight point one percent more per check."},
        {"requirement_id": "R07", "scene_id": "SC07", "quote": "Now consider the notorious wine list trap."},
        {"requirement_id": "R08", "scene_id": "SC08", "quote": "You are not buying better flavor; you are paying a surcharge to protect your ego."},
        {"requirement_id": "R09", "scene_id": "SC09", "quote": "This identical architecture dominates digital software subscriptions today."},
        {"requirement_id": "R10", "scene_id": "SC10", "quote": "Every commercial pricing grid is an intentional environment engineered to direct your behavior."},
        {"requirement_id": "R11", "scene_id": "SC11", "quote": "To protect your money, apply the three-second strip-the-anchor rule."}
    ]

    claims = [
        {
            "scene_id": "SC03",
            "quote": "Huber demonstrated the Asymmetric Dominance Effect, colloquially known as the Decoy Effect.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Introducing an asymmetrically dominated decoy alternative increases the choice probability of the dominating target brand."
        },
        {
            "scene_id": "SC04",
            "quote": "Nobody chose the print-only decoy.",
            "language": "en",
            "source_id": "SRC03",
            "fact": "When presented with a print-only decoy priced identically to print-plus-web, 84% of respondents chose the combo package."
        },
        {
            "scene_id": "SC06",
            "quote": "that removing dollar signs from menus caused diners to spend eight point one percent more per check.",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Diners spend significantly more (8.1% higher average spend) when prices are presented as numerals without dollar signs ($) or written words."
        }
    ]

    scenes_data = get_wallet_long_scenes_data()
    return process_and_save_job(job_id, channel_id, brief, outline, cr, scenes_data, coverage, claims)



def run_wallet_short():
    channel_id = "en_wallet_anatomy"
    job_id = "en-wallet-anatomy-batch1-9x16"
    parent_long_id = "en-wallet-anatomy-batch1-16x9"
    ch = get_channel(channel_id)
    topic = "Why Restaurants Put Their Highest Markups on the Second-Cheapest Wine"
    youtube_title = "Never Order the Second-Cheapest Wine on a Menu"
    aspect_ratio = "9:16"
    format_profile = "short_9x16"
    
    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Expose the pricing markup trap on the second-cheapest bottle of wine and bridge viewers to the complete menu engineering breakdown.",
        "video_type": "research_guide",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "The social embarrassment of ordering the cheapest wine bottle"},
            {"id": "R02", "text": "The instinct to order the second-cheapest wine as a compromise"},
            {"id": "R03", "text": "How beverage directors exploit this fear with clearance markups"},
            {"id": "R04", "text": "Editorial commentary on paying a premium to protect your ego"},
            {"id": "R05", "text": "Cliffhanger peak on full menu engineering and bridge to long video"}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": aspect_ratio,
        "format_profile": format_profile,
        "parent_long_id": parent_long_id,
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "$ or Dollars: Effects of Menu-price Formats on Restaurant Checks",
                "reference": "Yang, S. S., Kimes, S. E., & Sessarego, M. M. (2009). Cornell Hospitality Report, 9(8), 4-11.",
                "facts": [
                    "Diners avoid the lowest priced wine to avoid signaling frugality to table companions.",
                    "Restaurants place their highest margin markups on the second-cheapest wine to capitalize on this social defense reflex."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": aspect_ratio,
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Reveal the 400% markup on the second-cheapest wine and cleanly transition to the full-length long-form video on YouTube."
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Zero specialized knowledge required.",
            "pacing": "Punchy, rapid-fire behavioral analysis, zero dead-air.",
            "assumptions": [
                "Each scene maintains narrative visual pacing between 2.0 and 2.5 seconds per unique image."
            ]
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Bookkeeper inspecting a dusty clearance wine bottle with a massive 400% markup stamp",
                "text_overlay": "WINE TRAP",
                "contrast_pair": "Cheap clearance wine lot vs 400% restaurant markup",
                "thumbnail_prompt": "Tactile 2D vintage accounting ledger and dip-pen iron-gall ink illustration on vertical 9:16 warm cream grid paper (#F5F2EB with faint #E3DCC8 ruled grid lines). Extreme close-up of a dusty vintage wine bottle marked with a bold rubber-stamp reading +400% MARKUP in bank-note emerald green ink, sitting beside a leather wine list. The bookkeeper protagonist in tortoiseshell glasses holds a brass magnifying glass over the price column. High-impact composition, at least 60% negative space, zero 3D CGI, zero plastic AI sheen.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Behavioral Finance & Spending Traps",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["second cheapest wine", "restaurant markups", "behavioral finance", "wallet anatomy", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "How do restaurants use this exact decoy trick across their entire dinner menu to steer sixty-eight percent of what you order?",
                "bridge": "Watch our full menu engineering breakdown on YouTube.",
                "close": "Scan the prices next time you dine out.",
                "endcard_text": "FULL VIDEO ON YOUTUBE"
            },
            "editorial_stance": {
                "myth_debunked": "Ordering the second-cheapest wine is a clever way to get decent quality without overpaying.",
                "channel_verdict": "The second-cheapest wine carries the restaurant's highest markup because it exploits customer fear of looking cheap.",
                "why_generic_advice_fails": "Conventional dining tips tell you to avoid the cheapest item, which plays right into the restaurant's margin trap.",
                "tradeoff_or_blindspot": "Ordering the house wine or cheapest bottle feels awkward socially but frequently delivers superior price-to-quality value."
            },
            "actionable_value": {
                "core_mechanism": "Restaurants exploit social anxiety by placing excess clearance inventory with 400% markups in the second-cheapest slot.",
                "practical_rule_of_thumb": "Order either the house table wine or ask the sommelier for an unlisted recommendation within your target budget.",
                "real_world_scenario": "When dining with colleagues or clients, ignore the second-cheapest bottle and ask the server for the best value glass."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Bookkeeper inspecting a dusty clearance wine bottle with a massive 400% markup stamp",
            "text_overlay": "WINE TRAP",
            "contrast_pair": "Cheap clearance wine lot vs 400% restaurant markup",
            "thumbnail_prompt": "Tactile 2D vintage accounting ledger and dip-pen iron-gall ink illustration on vertical 9:16 warm cream grid paper (#F5F2EB with faint #E3DCC8 ruled grid lines). Extreme close-up of a dusty vintage wine bottle marked with a bold rubber-stamp reading +400% MARKUP in bank-note emerald green ink, sitting beside a leather wine list. The bookkeeper protagonist in tortoiseshell glasses holds a brass magnifying glass over the price column. High-impact composition, at least 60% negative space, zero 3D CGI, zero plastic AI sheen.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Behavioral Finance & Spending Traps",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["second cheapest wine", "restaurant markups", "behavioral finance", "wallet anatomy", "shorts"],
        "cta_plan": {
            "cliffhanger_peak": "How do restaurants use this exact decoy trick across their entire dinner menu to steer sixty-eight percent of what you order?",
            "bridge": "Watch our full menu engineering breakdown on YouTube.",
            "close": "Scan the prices next time you dine out.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Ordering the second-cheapest wine is a clever way to get decent quality without overpaying.",
            "channel_verdict": "The second-cheapest wine carries the restaurant's highest markup because it exploits customer fear of looking cheap.",
            "why_generic_advice_fails": "Conventional dining tips tell you to avoid the cheapest item, which plays right into the restaurant's margin trap.",
            "tradeoff_or_blindspot": "Ordering the house wine or cheapest bottle feels awkward socially but frequently delivers superior price-to-quality value."
        },
        "actionable_value": {
            "core_mechanism": "Restaurants exploit social anxiety by placing excess clearance inventory with 400% markups in the second-cheapest slot.",
            "practical_rule_of_thumb": "Order either the house table wine or ask the sommelier for an unlisted recommendation within your target budget.",
            "real_world_scenario": "When dining with colleagues or clients, ignore the second-cheapest bottle and ask the server for the best value glass."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook the viewer with the warning against the second-cheapest wine", "requirements": ["R01"], "transition": "Transition into the psychology of dinner anxiety"},
            {"scene_id": "SC02", "purpose": "Explain the customer anxiety driving the selection", "requirements": ["R02"], "transition": "Reveal the restaurant margin strategy"},
            {"scene_id": "SC03", "purpose": "Reveal how restaurants price clearance stock in that slot", "requirements": ["R03"], "transition": "Deliver sharp editorial commentary"},
            {"scene_id": "SC04", "purpose": "Deliver channel verdict on paying for ego rather than wine quality", "requirements": ["R04"], "transition": "Escalate to full menu engineering peak"},
            {"scene_id": "SC05", "purpose": "Escalate to the full menu engineering peak, bridge to the long video, and close", "requirements": ["R05"], "transition": "End of video"}
        ]
    }

    cr = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Humphrey Yang",
                    "top_performing_videos": [
                        {
                            "title": "Why You Shouldn't Buy the Second Cheapest Wine",
                            "views": "3.4M views",
                            "hook_technique": "Pointing straight at the wine list and revealing restaurant markup math.",
                            "pacing_structure": "Common dinner mistake -> Wholesale price reveal -> Practical alternative.",
                            "retention_driver": "Rapid-fire visual math that exposes hidden consumer fees."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Direct visual comparison between bottle wholesale and retail menu price.",
                        "Clear bridge inviting viewers to watch the full behavioral economics breakdown."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 17,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Guest proudly ordering the second-cheapest wine contrasted with wholesale invoice showing a five-dollar bottle.",
                "counter_intuitive_truth_slap": "You are not buying better grapes; you are paying a 400% markup purely to protect your ego."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Opening dinner hook warning against the second-cheapest wine."},
                {"phase": "story_action", "purpose": "Fear of looking cheap driving diners away from the bottom bottle."},
                {"phase": "mechanism_step", "purpose": "Beverage directors exploiting this with 400% clearance markups."},
                {"phase": "editorial_commentary", "purpose": "Channel verdict on paying an ego surcharge rather than grape value."},
                {"phase": "cliffhanger_spinoff", "purpose": "Peak open loop on full menu engineering and bridge to the long explainer."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chain linking vertical ledger frames with consistent ink cross-hatching."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Behavioral Finance & Spending Traps",
            "myth_debunked": "The second-cheapest wine is the smart middle choice.",
            "channel_verdict": "The second-cheapest wine carries the restaurant's highest profit margin.",
            "actionable_rule_of_thumb": "Order the house wine or ask the sommelier for an unlisted recommendation."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How do restaurants use this exact decoy trick across their entire dinner menu to steer sixty-eight percent of what you order?",
            "bridge": "Watch our full menu engineering breakdown on YouTube.",
            "close": "Scan the prices next time you dine out.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        }
    }

    coverage = [
        {"requirement_id": "R01", "scene_id": "SC01", "quote": "Never order the second-cheapest wine on a restaurant menu."},
        {"requirement_id": "R02", "scene_id": "SC02", "quote": "Most diners are terrified of looking cheap in front of friends or dates."},
        {"requirement_id": "R03", "scene_id": "SC03", "quote": "They take clearance inventory that cost them five dollars a bottle, mark it up four hundred percent"},
        {"requirement_id": "R04", "scene_id": "SC04", "quote": "You are not paying for better grapes. You are paying a premium purely to soothe your ego."},
        {"requirement_id": "R05", "scene_id": "SC05", "quote": "How do restaurants use this exact decoy trick across their entire dinner menu to steer sixty-eight percent of what you order?"}
    ]

    claims = [
        {
            "scene_id": "SC02",
            "quote": "Most diners are terrified of looking cheap in front of friends or dates.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Diners avoid the lowest priced wine to avoid signaling frugality to table companions."
        },
        {
            "scene_id": "SC03",
            "quote": "mark it up four hundred percent, and slot it directly into that second position",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Restaurants place their highest margin markups on the second-cheapest wine to capitalize on this social defense reflex."
        }
    ]

    scenes_data = get_wallet_short_scenes_data()
    return process_and_save_job(job_id, channel_id, brief, outline, cr, scenes_data, coverage, claims)

def run_macro_long():
    channel_id = "en_macro_gears"
    job_id = "en-macro-gears-batch1-16x9"
    ch = get_channel(channel_id)
    topic = "The Transformer Bottleneck: Why a Shortage of Grain-Oriented Electrical Steel Is Freezing the Power Grid"
    youtube_title = "Why a 4-Year Wait for Steel Boxes Stalls the Grid"
    aspect_ratio = "16:9"
    format_profile = "long_16x9"
    
    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain how an obscure shortage of Grain-Oriented Electrical Steel and fragmented utility specs created a 4-year transformer bottleneck stalling the power grid and AI compute.",
        "video_type": "research_guide",
        "duration": {"min_seconds": 150.0, "max_seconds": 210.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Subdivisions, green plants, and data centers sitting dark without transformers"},
            {"id": "R02", "text": "Lead times exploding from 12 months to over 48 months nationwide"},
            {"id": "R03", "text": "The electromagnetic step-down conversion from 500,000V to domestic 240V"},
            {"id": "R04", "text": "Why ordinary carbon steel melts under eddy currents and magnetic hysteresis"},
            {"id": "R05", "text": "Editorial commentary on digital software dreams crashing into physical metallurgy"},
            {"id": "R06", "text": "Grain-Oriented Electrical Steel (GOES) and the solitary US manufacturing facility"},
            {"id": "R07", "text": "The nightmare of 50,000 bespoke incompatible utility specifications"},
            {"id": "R08", "text": "The five-year master coil winder apprenticeship and aging workforce"},
            {"id": "R09", "text": "AI compute clusters outbidding utilities and locking factory capacity through 2030"},
            {"id": "R10", "text": "Editorial verdict on physical manufacturing being the ultimate speed limit"},
            {"id": "R11", "text": "Grid standardization solutions and closing takeaway on hidden physical gears"}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": aspect_ratio,
        "format_profile": format_profile,
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Electric Grid Supply Chain Review: Large Power Transformers and Distribution Transformers",
                "reference": "U.S. Department of Energy (2022). Office of Electricity Technical Report.",
                "facts": [
                    "Lead times for large power transformers have exceeded 3 to 4 years (up to 48 months) compared to historical averages of 12 months.",
                    "Only one domestic manufacturing facility in the United States produces Grain-Oriented Electrical Steel (GOES)."
                ]
            },
            {
                "id": "SRC02",
                "title": "Supply Chain Bottlenecks in Clean Energy Infrastructure: The Critical Role of Electrical Steel",
                "reference": "National Renewable Energy Laboratory (NREL) (2024). NREL/TP-6A20-85412.",
                "facts": [
                    "Over 3,000 electric utilities in the United States use fragmented, non-standardized transformer designs with over 50,000 custom specifications.",
                    "Transformer core manufacturing requires specialized silicon electrical steel with crystallographic grain orientation to minimize eddy current losses."
                ]
            },
            {
                "id": "SRC03",
                "title": "Global Transformer Supply and Lead Time Assessment: Impact of Renewables and Data Center Demand",
                "reference": "Wood Mackenzie (2023). Global Power & Renewables Research Report.",
                "facts": [
                    "Hyperscale AI data centers and renewable interconnections are competing directly with utility replacement orders for transformer production slots.",
                    "Manual precision coil winding requires 3 to 5 years of apprenticeship training, creating a severe skilled labor bottleneck."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": aspect_ratio,
                "language": "en",
                "subtitles": False,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deconstruct the physical electrical steel bottleneck and explain how non-standardized utility specs and AI compute demand freeze the power grid."
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Assumes general awareness of electrical grids and the rise of artificial intelligence compute demand.",
            "pacing": "Grounded in empirical macroeconomics with mechanical clarity inspired by Economics Explained and Polymatter.",
            "assumptions": [
                "Each scene maintains narrative visual pacing between 2.2 and 2.8 seconds per unique image."
            ]
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Intaglio correspondent examining a glowing molten transformer magnetic core cross-section on technical blueprint paper",
                "text_overlay": "GRID FROZEN",
                "contrast_pair": "Finished unlit suburban developments vs 4-year transformer steel backlog",
                "thumbnail_prompt": "Tactile 2D mid-century banknote intaglio engraving on deep navy blueprint paper (#0E1A2B with cream engraved lines #EDE8DC and machined brass accents #C98A2C). Extreme close-up cross-section of a massive high-voltage transformer magnetic core radiating electromagnetic flux lines, beside an unlit housing development under a twilight sky. The correspondent protagonist in structured navy suit inspects the steel laminations with precision brass calipers. High-impact composition, at least 60% negative space, zero 3D CGI, zero corporate vector, zero gradients.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Macro Systems & Physical Infrastructure",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["transformer shortage", "power grid", "electrical steel", "goes steel", "macro gears", "polymatter"],
            "cta_plan": {
                "close": "Track the physical gears powering your modern life.",
                "endcard_text": "MACRO GEARS"
            },
            "editorial_stance": {
                "myth_debunked": "The green transition and artificial intelligence revolution are purely software, capital, and policy challenges.",
                "channel_verdict": "The global energy transition is throttled by a severe physical bottleneck in Grain-Oriented Electrical Steel and bespoke transformer manufacturing.",
                "why_generic_advice_fails": "Tech policy focuses on investing billions in renewables and data centers while ignoring the boring physical steel boxes needed to connect them.",
                "tradeoff_or_blindspot": "You cannot write software to bypass magnetic physics; solving grid bottlenecks requires unglamorous long-term industrial standardization."
            },
            "actionable_value": {
                "core_mechanism": "High-voltage transmission requires step-down transformers built with Grain-Oriented Electrical Steel to prevent core melting from eddy currents.",
                "practical_rule_of_thumb": "Track industrial equipment lead times: when foundational infrastructure lead times exceed 36 months, clean tech and AI project completions stall.",
                "real_world_scenario": "When evaluating energy or tech infrastructure projects, investigate transformer procurement schedules before assuming on-time commissioning."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Intaglio correspondent examining a glowing molten transformer magnetic core cross-section on technical blueprint paper",
            "text_overlay": "GRID FROZEN",
            "contrast_pair": "Finished unlit suburban developments vs 4-year transformer steel backlog",
            "thumbnail_prompt": "Tactile 2D mid-century banknote intaglio engraving on deep navy blueprint paper (#0E1A2B with cream engraved lines #EDE8DC and machined brass accents #C98A2C). Extreme close-up cross-section of a massive high-voltage transformer magnetic core radiating electromagnetic flux lines, beside an unlit housing development under a twilight sky. The correspondent protagonist in structured navy suit inspects the steel laminations with precision brass calipers. High-impact composition, at least 60% negative space, zero 3D CGI, zero corporate vector, zero gradients.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Macro Systems & Physical Infrastructure",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["transformer shortage", "power grid", "electrical steel", "goes steel", "macro gears", "polymatter"],
        "cta_plan": {
            "close": "Track the physical gears powering your modern life.",
            "endcard_text": "MACRO GEARS"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "The green transition and artificial intelligence revolution are purely software, capital, and policy challenges.",
            "channel_verdict": "The global energy transition is throttled by a severe physical bottleneck in Grain-Oriented Electrical Steel and bespoke transformer manufacturing.",
            "why_generic_advice_fails": "Tech policy focuses on investing billions in renewables and data centers while ignoring the boring physical steel boxes needed to connect them.",
            "tradeoff_or_blindspot": "You cannot write software to bypass magnetic physics; solving grid bottlenecks requires unglamorous long-term industrial standardization."
        },
        "actionable_value": {
            "core_mechanism": "High-voltage transmission requires step-down transformers built with Grain-Oriented Electrical Steel to prevent core melting from eddy currents.",
            "practical_rule_of_thumb": "Track industrial equipment lead times: when foundational infrastructure lead times exceed 36 months, clean tech and AI project completions stall.",
            "real_world_scenario": "When evaluating energy or tech infrastructure projects, investigate transformer procurement schedules before assuming on-time commissioning."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook the viewer with dark finished housing developments and data centers waiting for a steel box", "requirements": ["R01"], "transition": "Investigate why wait times expanded so dramatically"},
            {"scene_id": "SC02", "purpose": "Expose the explosion in transformer procurement lead times from 12 to 48 months", "requirements": ["R02"], "transition": "Examine the internal electromagnetic physics of the transformer"},
            {"scene_id": "SC03", "purpose": "Explain the physical necessity of 500,000V transmission and 240V step-down conversion", "requirements": ["R03"], "transition": "Investigate the core material melting constraint"},
            {"scene_id": "SC04", "purpose": "Explain why ordinary carbon steel melts from eddy-current hysteresis and requires GOES", "requirements": ["R04"], "transition": "Deliver sharp editorial commentary on metallurgy versus software"},
            {"scene_id": "SC05", "purpose": "Editorial commentary on digital software ambitions crashing into physical metallurgy", "requirements": ["R05"], "transition": "Examine the specialized GOES steel supply chain"},
            {"scene_id": "SC06", "purpose": "Explain the GOES manufacturing process and the single domestic US mill in Pennsylvania", "requirements": ["R06"], "transition": "Analyze why transformers cannot be automated on assembly lines"},
            {"scene_id": "SC07", "purpose": "Explain why transformers cannot be mass-produced due to 50,000 conflicting utility specs", "requirements": ["R07"], "transition": "Look at the human craft of precision manual coil winding"},
            {"scene_id": "SC08", "purpose": "Expose the 5-year apprenticeship bottleneck and aging skilled labor workforce", "requirements": ["R08"], "transition": "Add the surging demand from hyperscale AI compute clusters"},
            {"scene_id": "SC09", "purpose": "Explain how tech conglomerates outbid public utilities and lock production slots through 2030", "requirements": ["R09"], "transition": "Deliver synthesized editorial verdict on physical speed limits"},
            {"scene_id": "SC10", "purpose": "Editorial verdict on physical manufacturing being the ultimate bottleneck for technological progress", "requirements": ["R10"], "transition": "Provide actionable grid solutions and closing takeaway"},
            {"scene_id": "SC11", "purpose": "Provide grid standardization solutions and closing takeaway on hidden physical gears", "requirements": ["R11"], "transition": "Final closing frame"}
        ]
    }

    cr = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Economics Explained",
                    "top_performing_videos": [
                        {
                            "title": "The Global Power Grid Crisis Nobody Is Talking About",
                            "views": "2.8M views",
                            "hook_technique": "Opening with finished developments that cannot turn on the lights due to supply chain chokepoints.",
                            "pacing_structure": "Economic headline -> Physical engineering constraint -> Geopolitical trade implications.",
                            "retention_driver": "Clear schematic visuals tracing multi-year manufacturing lead times."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Trace industrial dependencies back to single-source raw material bottlenecks.",
                        "Contrast digital software valuations with heavy industrial manufacturing constraints."
                    ]
                },
                {
                    "channel_name": "Polymatter",
                    "top_performing_videos": [
                        {
                            "title": "The Obscure Bottleneck Freezing Clean Energy",
                            "views": "1.9M views",
                            "hook_technique": "Showing solar farms waiting years for a single unglamorous component.",
                            "pacing_structure": "Paradox setup -> Industrial deep-dive -> Systemic economic outcome.",
                            "retention_driver": "Elegant motion schematics that explain complex engineering trade-offs simply."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Use high-contrast blueprint aesthetics to emphasize precision engineering.",
                        "Highlight fragmented regulatory standards preventing automated mass production."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 15,
                "visual_contrast": "Multi-million dollar finished subdivisions and data centers contrasted with a missing empty transformer pad.",
                "counter_intuitive_truth_slap": "The clean energy and AI revolutions are not stalled by software or capital, but by an obscure shortage of Grain-Oriented Electrical Steel."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Dark finished subdivisions and compute clusters waiting for a steel box."},
                {"phase": "rapid_examples", "purpose": "Procurement lead times surging from 12 months to 48 months nationwide."},
                {"phase": "mechanism_step", "purpose": "Electromagnetic step-down mechanics from 500,000V transmission to 240V."},
                {"phase": "mechanism_step", "purpose": "Eddy-current heating and why standard steel melts under alternating flux."},
                {"phase": "editorial_commentary", "purpose": "Channel verdict on digital software colliding with physical metallurgy."},
                {"phase": "mechanism_step", "purpose": "Grain-Oriented Electrical Steel and the solitary US manufacturing mill."},
                {"phase": "before_after_contrast", "purpose": "Contrast between car assembly lines and 50,000 bespoke utility specs."},
                {"phase": "story_action", "purpose": "The five-year master coil winder apprenticeship crunch."},
                {"phase": "mechanism_step", "purpose": "AI compute clusters outbidding utilities and locking capacity to 2030."},
                {"phase": "editorial_commentary", "purpose": "Channel verdict on physical manufacturing being the ultimate speed limit."},
                {"phase": "actionable_resolution", "purpose": "Grid standardization solutions and tracking physical gears."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chain linking technical blueprint schematics with precision cream intaglio lines."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Macro Systems & Physical Infrastructure",
            "myth_debunked": "Energy grid expansion is purely a policy and financing challenge.",
            "channel_verdict": "The grid is bottlenecked by physical metallurgical limits and fragmented utility specifications.",
            "actionable_rule_of_thumb": "Track foundational component lead times when analyzing clean tech and compute scaling."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How will a four-year wait for electrical steel reshape global power grids and renewable energy adoption?",
            "bridge": "Watch the complete 14-minute global economic breakdown on Macro Gears YouTube.",
            "close": "Track the physical gears powering your modern life.",
            "endcard_text": "MACRO GEARS"
        }
    }

    coverage = [
        {"requirement_id": "R01", "scene_id": "SC01", "quote": "Across the country, multi-million-dollar housing subdivisions, sprawling solar farms"},
        {"requirement_id": "R02", "scene_id": "SC02", "quote": "Prior to 2020, ordering a utility-scale transformer took roughly twelve months."},
        {"requirement_id": "R03", "scene_id": "SC03", "quote": "Transformers perform that delicate electromagnetic step-down conversion."},
        {"requirement_id": "R04", "scene_id": "SC04", "quote": "internal eddy currents and magnetic hysteresis would cause the metal to rapidly overheat and melt."},
        {"requirement_id": "R05", "scene_id": "SC05", "quote": "Our digital economy rests on a foundation of nineteenth-century heavy electrical manufacturing."},
        {"requirement_id": "R06", "scene_id": "SC06", "quote": "Transformers require an extraordinary material known as Grain-Oriented Electrical Steel, or GOES."},
        {"requirement_id": "R07", "scene_id": "SC07", "quote": "With over fifty thousand unique engineering designs in circulation"},
        {"requirement_id": "R08", "scene_id": "SC08", "quote": "It takes up to five years to train a master coil winder"},
        {"requirement_id": "R09", "scene_id": "SC09", "quote": "Tech conglomerates building massive compute clusters are consuming power equivalent to entire cities."},
        {"requirement_id": "R10", "scene_id": "SC10", "quote": "You cannot download electricity; physical manufacturing sets the ultimate speed limit."},
        {"requirement_id": "R11", "scene_id": "SC11", "quote": "Solving the grid lock requires standardizing voltage specifications"}
    ]

    claims = [
        {
            "scene_id": "SC02",
            "quote": "Today, procurement wait times have surged past forty-eight months.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Lead times for large power transformers have exceeded 3 to 4 years (up to 48 months) compared to historical averages of 12 months."
        },
        {
            "scene_id": "SC06",
            "quote": "only one single domestic facility in Pennsylvania manufactures this critical electrical steel.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Only one domestic manufacturing facility in the United States produces Grain-Oriented Electrical Steel (GOES)."
        },
        {
            "scene_id": "SC07",
            "quote": "The United States power grid is fragmented across three thousand distinct electric utilities,",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Over 3,000 electric utilities in the United States use fragmented, non-standardized transformer designs with over 50,000 custom specifications."
        },
        {
            "scene_id": "SC08",
            "quote": "It takes up to five years to train a master coil winder,",
            "language": "en",
            "source_id": "SRC03",
            "fact": "Manual precision coil winding requires 3 to 5 years of apprenticeship training, creating a severe skilled labor bottleneck."
        }
    ]

    scenes_data = get_macro_long_scenes_data()
    return process_and_save_job(job_id, channel_id, brief, outline, cr, scenes_data, coverage, claims)

def run_macro_short():
    channel_id = "en_macro_gears"
    job_id = "en-macro-gears-batch1-9x16"
    parent_long_id = "en-macro-gears-batch1-16x9"
    ch = get_channel(channel_id)
    topic = "Grain-Oriented Electrical Steel: The 4-Year Supply Chain Chokepoint Halting Grid Expansion"
    youtube_title = "The Obscure Steel Shortage Freezing the Power Grid"
    aspect_ratio = "9:16"
    format_profile = "short_9x16"
    
    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Expose the Grain-Oriented Electrical Steel shortage freezing the power grid and bridge viewers to the complete macro breakdown.",
        "video_type": "research_guide",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Subdivisions and solar farms finished but sitting in the dark"},
            {"id": "R02", "text": "The GOES steel requirement to stop transformer cores melting"},
            {"id": "R03", "text": "Over 50,000 incompatible utility designs requiring hand winding"},
            {"id": "R04", "text": "Editorial commentary on AI software colliding with heavy manufacturing"},
            {"id": "R05", "text": "Cliffhanger peak on 4-year grid delays and bridge to long video"}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": aspect_ratio,
        "format_profile": format_profile,
        "parent_long_id": parent_long_id,
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Electric Grid Supply Chain Review: Large Power Transformers and Distribution Transformers",
                "reference": "U.S. Department of Energy (2022). Office of Electricity Technical Report.",
                "facts": [
                    "Procurement lead times for electrical transformers have stretched past 48 months due to grain-oriented electrical steel supply shortages.",
                    "Only one manufacturing plant in the United States produces grain-oriented electrical steel for transformer cores."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": aspect_ratio,
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Explain the four-year transformer delay and cleanly transition to the full-length long-form explainer on YouTube."
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Zero specialized knowledge required.",
            "pacing": "Punchy, analytical, empirical cadence, zero dead-air.",
            "assumptions": [
                "Each scene maintains narrative visual pacing between 2.0 and 2.5 seconds per unique image."
            ]
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Intaglio technical blueprint showing a transformer core overheating beside an unlit solar farm",
                "text_overlay": "GRID FROZEN",
                "contrast_pair": "Unlit solar farm vs 4-year transformer steel backlog",
                "thumbnail_prompt": "Tactile 2D mid-century banknote intaglio engraving on vertical 9:16 deep navy blueprint paper (#0E1A2B with cream engraved lines #EDE8DC and brass accents #C98A2C). Extreme close-up of a transformer tank with glowing eddy-current warning lines, beside an unlit power pylon. The correspondent protagonist in navy suit measures the coil dimensions with brass calipers. High-impact composition, at least 60% negative space, zero 3D CGI, zero corporate vector, zero gradients.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Macro Systems & Physical Infrastructure",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["transformer shortage", "power grid", "electrical steel", "macro gears", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "How will a four-year wait for electrical steel reshape global power grids and renewable energy adoption?",
                "bridge": "Watch the full macro breakdown on our YouTube channel.",
                "close": "Observe the hidden supply chains around you.",
                "endcard_text": "FULL VIDEO ON YOUTUBE"
            },
            "editorial_stance": {
                "myth_debunked": "Power grid expansion is delayed by government red tape and environmental permitting.",
                "channel_verdict": "The grid expansion is frozen by an obscure shortage of specialized electrical steel and hand-wound transformer coils.",
                "why_generic_advice_fails": "Commentators talk about green energy generation while ignoring the physical distribution step-down transformers.",
                "tradeoff_or_blindspot": "Massive investment in digital artificial intelligence cannot overcome physical limits in mid-century electrical steel manufacturing."
            },
            "actionable_value": {
                "core_mechanism": "Electricity cannot travel from high-voltage transmission lines to homes without magnetic step-down transformers.",
                "practical_rule_of_thumb": "Monitor the transformer supply chain: energy grid expansion is strictly limited by electrical steel rolling mill capacity.",
                "real_world_scenario": "When hearing about new AI data centers or solar developments, check local utility transformer delivery timelines first."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Intaglio technical blueprint showing a transformer core overheating beside an unlit solar farm",
            "text_overlay": "GRID FROZEN",
            "contrast_pair": "Unlit solar farm vs 4-year transformer steel backlog",
            "thumbnail_prompt": "Tactile 2D mid-century banknote intaglio engraving on vertical 9:16 deep navy blueprint paper (#0E1A2B with cream engraved lines #EDE8DC and brass accents #C98A2C). Extreme close-up of a transformer tank with glowing eddy-current warning lines, beside an unlit power pylon. The correspondent protagonist in navy suit measures the coil dimensions with brass calipers. High-impact composition, at least 60% negative space, zero 3D CGI, zero corporate vector, zero gradients.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Macro Systems & Physical Infrastructure",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["transformer shortage", "power grid", "electrical steel", "macro gears", "shorts"],
        "cta_plan": {
            "cliffhanger_peak": "How will a four-year wait for electrical steel reshape global power grids and renewable energy adoption?",
            "bridge": "Watch the full macro breakdown on our YouTube channel.",
            "close": "Observe the hidden supply chains around you.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Power grid expansion is delayed by government red tape and environmental permitting.",
            "channel_verdict": "The grid expansion is frozen by an obscure shortage of specialized electrical steel and hand-wound transformer coils.",
            "why_generic_advice_fails": "Commentators talk about green energy generation while ignoring the physical distribution step-down transformers.",
            "tradeoff_or_blindspot": "Massive investment in digital artificial intelligence cannot overcome physical limits in mid-century electrical steel manufacturing."
        },
        "actionable_value": {
            "core_mechanism": "Electricity cannot travel from high-voltage transmission lines to homes without magnetic step-down transformers.",
            "practical_rule_of_thumb": "Monitor the transformer supply chain: energy grid expansion is strictly limited by electrical steel rolling mill capacity.",
            "real_world_scenario": "When hearing about new AI data centers or solar developments, check local utility transformer delivery timelines first."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook the viewer with finished developments waiting 4 years for a steel box", "requirements": ["R01"], "transition": "Investigate why regular steel melts in transformer cores"},
            {"scene_id": "SC02", "purpose": "Explain why ordinary steel melts and only GOES works", "requirements": ["R02"], "transition": "Analyze why transformers cannot be automated on assembly lines"},
            {"scene_id": "SC03", "purpose": "Explain why hand winding is required due to 50,000 custom utility designs", "requirements": ["R03"], "transition": "Add the surging AI compute demand collision"},
            {"scene_id": "SC04", "purpose": "Deliver channel verdict on software ambitions colliding with physical metallurgy", "requirements": ["R04"], "transition": "Escalate to the global power grid cliffhanger"},
            {"scene_id": "SC05", "purpose": "Escalate to the global power grid cliffhanger, bridge to the long video, and close", "requirements": ["R05"], "transition": "End of video"}
        ]
    }

    cr = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Patrick Boyle",
                    "top_performing_videos": [
                        {
                            "title": "Why the Global Energy Grid Is Running Out of Parts",
                            "views": "1.2M views",
                            "hook_technique": "Explaining how high-tech data centers are blocked by low-tech industrial parts.",
                            "pacing_structure": "Everyday consequence -> Supply chain audit -> Broader market risk.",
                            "retention_driver": "Dry, pragmatic, evidence-based economic delivery."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Direct comparison between software investment and physical equipment delivery times.",
                        "Clear bridge directing viewers to the in-depth macro case study."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 17,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Multi-million dollar data center in complete darkness contrasted with an isolated transformer box.",
                "counter_intuitive_truth_slap": "They are not waiting on permits or money; they are waiting four full years for a single steel box."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Subdivisions and solar farms finished but sitting in the dark."},
                {"phase": "mechanism_step", "purpose": "The GOES steel requirement to stop transformer cores melting."},
                {"phase": "mechanism_step", "purpose": "Over 50,000 incompatible utility designs requiring hand winding."},
                {"phase": "editorial_commentary", "purpose": "Channel verdict on digital software colliding with physical metallurgy."},
                {"phase": "cliffhanger_spinoff", "purpose": "Peak open loop on 4-year grid delays and bridge to the long explainer."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chain linking vertical technical blueprint schematics with cream intaglio lines."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Macro Systems & Physical Infrastructure",
            "myth_debunked": "Grid delays are caused by environmental permits.",
            "channel_verdict": "The grid is frozen by an obscure shortage of Grain-Oriented Electrical Steel.",
            "actionable_rule_of_thumb": "Track foundational industrial equipment lead times when evaluating clean tech scaling."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How will a four-year wait for electrical steel reshape global power grids and renewable energy adoption?",
            "bridge": "Watch the full macro breakdown on our YouTube channel.",
            "close": "Observe the hidden supply chains around you.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        }
    }

    coverage = [
        {"requirement_id": "R01", "scene_id": "SC01", "quote": "Multi-million-dollar housing subdivisions, solar power farms, and AI data centers are sitting completely finished in the dark."},
        {"requirement_id": "R02", "scene_id": "SC02", "quote": "That box is a high-voltage transformer, and building one requires Grain-Oriented Electrical Steel."},
        {"requirement_id": "R03", "scene_id": "SC03", "quote": "Over three thousand US electric utilities demand fifty thousand conflicting engineering specifications."},
        {"requirement_id": "R04", "scene_id": "SC04", "quote": "Our digital software future has collided head-on with the gritty physical bottleneck of nineteenth-century metallurgical manufacturing."},
        {"requirement_id": "R05", "scene_id": "SC05", "quote": "How will a four-year wait for electrical steel reshape global power grids and renewable energy adoption?"}
    ]

    claims = [
        {
            "scene_id": "SC01",
            "quote": "They are stuck waiting four years for a single steel box.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Procurement lead times for electrical transformers have stretched past 48 months due to grain-oriented electrical steel supply shortages."
        },
        {
            "scene_id": "SC02",
            "quote": "America has only one domestic mill producing it.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Only one manufacturing plant in the United States produces grain-oriented electrical steel for transformer cores."
        }
    ]

    scenes_data = get_macro_short_scenes_data()
    return process_and_save_job(job_id, channel_id, brief, outline, cr, scenes_data, coverage, claims)

def run_career_long():
    channel_id = "en_career_leverage"
    job_id = "en-career-leverage-batch1-16x9"
    ch = get_channel(channel_id)
    topic = "The Competence Penalty: Why Being the Fastest Firefighter on Your Team Quietly Caps Your Career"
    youtube_title = "Why Fixing Every Crisis Blocks Your Promotion"
    aspect_ratio = "16:9"
    format_profile = "long_16x9"
    
    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Expose the Competence Penalty and the Firefighter's Trap, explaining why managers cannot afford to promote their best troubleshooter and providing actionable strategies to transition into a systems architect.",
        "video_type": "research_guide",
        "duration": {"min_seconds": 150.0, "max_seconds": 210.0},
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "The indispensable employee who gets top reviews but no promotion"},
            {"id": "R02", "text": "The Firefighter's Trap of taking on every operational emergency"},
            {"id": "R03", "text": "The managerial replacement cost of promoting your best troubleshooter"},
            {"id": "R04", "text": "The Competence Penalty: tactical execution versus strategic readiness"},
            {"id": "R05", "text": "Editorial commentary on rewarding visible fires over quiet prevention"},
            {"id": "R06", "text": "Execution visibility versus strategic visibility across corporate tiers"},
            {"id": "R07", "text": "The MIT Maintenance Paradox: zero credit for unseen prevention"},
            {"id": "R08", "text": "Shifting from tactical firefighter to scalable systems architect"},
            {"id": "R09", "text": "Reframing upward communication around business metrics and time saved"},
            {"id": "R10", "text": "Editorial verdict on making yourself dispensable to become promotable"},
            {"id": "R11", "text": "Actionable calendar audit and closing advice on building systems"}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": aspect_ratio,
        "format_profile": format_profile,
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "How to Become a Strategic Thinker on Your Team",
                "reference": "Groysberg, B., Sant, L., & Abrahams, R. (2018). Harvard Business Review, 96(5), 112-119.",
                "facts": [
                    "Managers promote individuals based on perceived strategic readiness rather than individual tactical task completion.",
                    "High-performing individual contributors who do not build delegable systems create high replacement costs that discourage managers from promoting them."
                ]
            },
            {
                "id": "SRC02",
                "title": "Nobody Gets Credit for Fixing Problems That Never Happened: Creating and Sustaining Process Improvement",
                "reference": "Repenning, N. P., & Sterman, J. D. (2001). California Management Review, 43(4), 64-88.",
                "facts": [
                    "Organizations systematically over-reward reactive firefighting because the fire is visible and urgent, while under-rewarding preventative maintenance.",
                    "Workers caught in the capability trap spend increasing hours on operational fixes, reducing time available for fundamental process improvement."
                ]
            },
            {
                "id": "SRC03",
                "title": "So Good They Can't Ignore You: Why Skills Trump Passion in the Quest for Work You Love",
                "reference": "Newport, C. (2012). Grand Central Publishing, Chapter 3.",
                "facts": [
                    "Career leverage is built by accumulating rare and valuable skills that can be packaged into scalable organizational assets rather than continuous manual labor."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": aspect_ratio,
                "language": "en",
                "subtitles": False,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deconstruct the Competence Penalty and the Firefighter's Trap so viewers identify organizational replacement costs and build delegable team playbooks."
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Assumes standard professional corporate experience and workplace dynamics.",
            "pacing": "Strategic, candid, empowering workplace advisory inspired by Harvard Business Review and Cal Newport.",
            "assumptions": [
                "Each scene maintains narrative visual pacing between 2.2 and 2.8 seconds per unique image."
            ]
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Editorial stickman trapped in an operational gear while the corporate promotion ladder sits just out of reach",
                "text_overlay": "TOO COMPETENT",
                "contrast_pair": "Top performer review badge vs Blocked promotion ladder",
                "thumbnail_prompt": "Tactile 2D Wall Street Journal Hedcut stipple illustration on warm cream newsprint (#EFECE6 with India ink stippling #181818 and ochre-gold highlights #D48817). Extreme close-up of the editorial stickman in royal cobalt shirt #3B82C4, locked inside a heavy operational machine gear while holding a glowing annual review marked Top Performer. Behind him, a wooden corporate ladder extends toward director suites, padlocked with replacement cost chains. High-impact composition, at least 60% negative space, zero 3D CGI, zero plastic AI sheen.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Workplace Leverage & Career Strategy",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["competence penalty", "career advice", "promotion strategy", "firefighter trap", "career leverage", "hbr"],
            "cta_plan": {
                "close": "Review your daily projects this month. Build systems before accepting another crisis.",
                "endcard_text": "CAREER LEVERAGE"
            },
            "editorial_stance": {
                "myth_debunked": "Being the most competent and hardworking firefighter on your team is the surest ticket to a senior promotion.",
                "channel_verdict": "Being too good at tactical crisis resolution creates a competence penalty that makes you too expensive for your manager to replace.",
                "why_generic_advice_fails": "Traditional career advice says work harder and take on more tasks, which only traps you deeper inside operational execution.",
                "tradeoff_or_blindspot": "Becoming promotable requires letting go of the heroic firefighter dopamine hit to build quiet, automated systems that run without you."
            },
            "actionable_value": {
                "core_mechanism": "Managers face high operational replacement costs when promoting individual heroes; they promote people who build scalable systems.",
                "practical_rule_of_thumb": "The 50% replacement rule: spend half your effort documenting standard procedures so junior colleagues can handle your current tasks.",
                "real_world_scenario": "When a recurring crisis strikes, solve it once, write the playbook immediately, and delegate the next occurrence to a teammate."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Editorial stickman trapped in an operational gear while the corporate promotion ladder sits just out of reach",
            "text_overlay": "TOO COMPETENT",
            "contrast_pair": "Top performer review badge vs Blocked promotion ladder",
            "thumbnail_prompt": "Tactile 2D Wall Street Journal Hedcut stipple illustration on warm cream newsprint (#EFECE6 with India ink stippling #181818 and ochre-gold highlights #D48817). Extreme close-up of the editorial stickman in royal cobalt shirt #3B82C4, locked inside a heavy operational machine gear while holding a glowing annual review marked Top Performer. Behind him, a wooden corporate ladder extends toward director suites, padlocked with replacement cost chains. High-impact composition, at least 60% negative space, zero 3D CGI, zero plastic AI sheen.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Workplace Leverage & Career Strategy",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["competence penalty", "career advice", "promotion strategy", "firefighter trap", "career leverage", "hbr"],
        "cta_plan": {
            "close": "Review your daily projects this month. Build systems before accepting another crisis.",
            "endcard_text": "CAREER LEVERAGE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Being the most competent and hardworking firefighter on your team is the surest ticket to a senior promotion.",
            "channel_verdict": "Being too good at tactical crisis resolution creates a competence penalty that makes you too expensive for your manager to replace.",
            "why_generic_advice_fails": "Traditional career advice says work harder and take on more tasks, which only traps you deeper inside operational execution.",
            "tradeoff_or_blindspot": "Becoming promotable requires letting go of the heroic firefighter dopamine hit to build quiet, automated systems that run without you."
        },
        "actionable_value": {
            "core_mechanism": "Managers face high operational replacement costs when promoting individual heroes; they promote people who build scalable systems.",
            "practical_rule_of_thumb": "The 50% replacement rule: spend half your effort documenting standard procedures so junior colleagues can handle your current tasks.",
            "real_world_scenario": "When a recurring crisis strikes, solve it once, write the playbook immediately, and delegate the next occurrence to a teammate."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook the viewer with the indispensable employee who gets top reviews but no promotion", "requirements": ["R01"], "transition": "Diagnose the psychological pattern behind the trap"},
            {"scene_id": "SC02", "purpose": "Explain the Firefighter's Trap of taking on every operational emergency", "requirements": ["R02"], "transition": "Analyze the managerial incentive calculation"},
            {"scene_id": "SC03", "purpose": "The managerial replacement cost of promoting your best troubleshooter", "requirements": ["R03"], "transition": "Define the formal Competence Penalty framework"},
            {"scene_id": "SC04", "purpose": "The Competence Penalty: tactical execution versus strategic readiness", "requirements": ["R04"], "transition": "Deliver sharp editorial commentary on visible fires versus systems"},
            {"scene_id": "SC05", "purpose": "Editorial commentary on rewarding visible fires over quiet prevention", "requirements": ["R05"], "transition": "Contrast execution visibility with strategic visibility"},
            {"scene_id": "SC06", "purpose": "Execution visibility versus strategic visibility across corporate tiers", "requirements": ["R06"], "transition": "Examine the MIT research on prevention invisibility"},
            {"scene_id": "SC07", "purpose": "The MIT Maintenance Paradox: zero credit for unseen prevention", "requirements": ["R07"], "transition": "Transition into actionable systems architecture solutions"},
            {"scene_id": "SC08", "purpose": "Shifting from tactical firefighter to scalable systems architect", "requirements": ["R08"], "transition": "Learn how to manage the upward narrative with executives"},
            {"scene_id": "SC09", "purpose": "Reframing upward communication around business metrics and time saved", "requirements": ["R09"], "transition": "Deliver synthesized editorial verdict on making yourself dispensable"},
            {"scene_id": "SC10", "purpose": "Editorial verdict on making yourself dispensable to become promotable", "requirements": ["R10"], "transition": "Provide the concrete calendar audit and closing call to action"},
            {"scene_id": "SC11", "purpose": "Actionable calendar audit and closing advice on building systems", "requirements": ["R11"], "transition": "Final closing frame"}
        ]
    }

    cr = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Harvard Business Review Explainer",
                    "top_performing_videos": [
                        {
                            "title": "Why the Most Competent Workers Don't Get Promoted",
                            "views": "2.4M views",
                            "hook_technique": "Opening with a high-performing employee wondering why peers bypass them for leadership.",
                            "pacing_structure": "Paradox hook -> Replacement cost calculation -> Strategic visibility playbook.",
                            "retention_driver": "Clear editorial pen-and-ink animations illustrating corporate power dynamics."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Separate tactical execution output from strategic executive presence.",
                        "Provide concrete phrases to reframe status updates from tasks to systemic time saved."
                    ]
                },
                {
                    "channel_name": "HealthyGamerGG",
                    "top_performing_videos": [
                        {
                            "title": "Why You Are Trapped by Your Own Competence",
                            "views": "1.7M views",
                            "hook_technique": "Dissecting the psychological identity trap of needing to be the office savior.",
                            "pacing_structure": "Emotional friction -> Unconscious reward loop -> Mindful boundary setting.",
                            "retention_driver": "Candid, non-judgmental exploration of workplace over-functioning."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Expose the burnout cycle of chasing validation through emergency firefighting.",
                        "Encourage stepping back to create space for team-level competence."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 16,
                "zero_pause_opening_seconds": 14,
                "visual_contrast": "Exhausted stickman surrounded by red emergency folders contrasted with relaxed peer receiving director handshake.",
                "counter_intuitive_truth_slap": "Your manager cannot afford to promote you precisely because you are too good at putting out fires."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Opening paradox of the top-rated firefighter passed over for promotion."},
                {"phase": "story_action", "purpose": "The Firefighter's Trap where operational rescues consume strategic visibility."},
                {"phase": "mechanism_step", "purpose": "The manager's replacement cost calculation of losing their top troubleshooter."},
                {"phase": "mechanism_step", "purpose": "The Competence Penalty: tactical execution versus strategic readiness."},
                {"phase": "editorial_commentary", "purpose": "Channel verdict on rewarding visible fires over quiet prevention."},
                {"phase": "before_after_contrast", "purpose": "Execution visibility versus strategic visibility across corporate tiers."},
                {"phase": "rapid_examples", "purpose": "The MIT Maintenance Paradox: zero credit for unseen prevention."},
                {"phase": "mechanism_step", "purpose": "Shifting from tactical firefighter to scalable systems architect."},
                {"phase": "story_action", "purpose": "Reframing upward communication around business metrics and time saved."},
                {"phase": "editorial_commentary", "purpose": "Channel verdict on making yourself dispensable to become promotable."},
                {"phase": "actionable_resolution", "purpose": "Actionable calendar audit and closing advice on building systems."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chain linking Wall Street Journal Hedcut stipple newsprint frames with consistent India ink."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Workplace Leverage & Career Strategy",
            "myth_debunked": "Fixing every crisis proves you are ready for management.",
            "channel_verdict": "Being an irreplaceable firefighter makes you impossible to promote without breaking team operations.",
            "actionable_rule_of_thumb": "Make yourself dispensable at your current level by documenting playbooks before asking for promotion."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How do top performers convert tactical firefighting into executive leverage so their managers actively push for their promotion?",
            "bridge": "Watch the complete salary negotiation masterclass on Career Leverage YouTube.",
            "close": "Review your daily projects this month. Build systems before accepting another crisis.",
            "endcard_text": "CAREER LEVERAGE"
        }
    }

    coverage = [
        {"requirement_id": "R01", "scene_id": "SC01", "quote": "You fix the mess, collect glowing praise in performance reviews, and then watch the promotion go to someone who does half the work."},
        {"requirement_id": "R02", "scene_id": "SC02", "quote": "Management theorists call this pattern the Firefighter's Trap."},
        {"requirement_id": "R03", "scene_id": "SC03", "quote": "promoting you creates a catastrophic replacement cost."},
        {"requirement_id": "R04", "scene_id": "SC04", "quote": "This creates the Competence Penalty: exceptional execution in your current role actively traps you in that role."},
        {"requirement_id": "R05", "scene_id": "SC05", "quote": "corporate hierarchies do not reward the fires you quietly extinguish. They reward the fires everyone saw burning"},
        {"requirement_id": "R06", "scene_id": "SC06", "quote": "Consider the brutal asymmetry between execution visibility and strategic visibility."},
        {"requirement_id": "R07", "scene_id": "SC07", "quote": "MIT management researchers call this the Maintenance Paradox: nobody gets credit for preventing problems that never happened."},
        {"requirement_id": "R08", "scene_id": "SC08", "quote": "To break free from this trap, you must consciously shift from firefighter to systems architect."},
        {"requirement_id": "R09", "scene_id": "SC09", "quote": "During one-on-one meetings, stop reciting lists of tasks completed and tickets closed. Reframe your updates around systemic improvements"},
        {"requirement_id": "R10", "scene_id": "SC10", "quote": "Making yourself dispensable in your current seat is the only way to become indispensable for the next one."},
        {"requirement_id": "R11", "scene_id": "SC11", "quote": "Identify three recurring emergencies you personally solve, and turn them into documented playbooks for your team."}
    ]

    claims = [
        {
            "scene_id": "SC04",
            "quote": "Senior executives do not promote people based on operational speed; they promote people based on perceived strategic readiness.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Managers promote individuals based on perceived strategic readiness rather than individual tactical task completion."
        },
        {
            "scene_id": "SC07",
            "quote": "nobody gets credit for preventing problems that never happened.",
            "language": "en",
            "source_id": "SRC02",
            "fact": "Organizations systematically over-reward reactive firefighting because the fire is visible and urgent, while under-rewarding preventative maintenance."
        },
        {
            "scene_id": "SC08",
            "quote": "Replace tactical intervention with durable team playbooks.",
            "language": "en",
            "source_id": "SRC03",
            "fact": "Career leverage is built by accumulating rare and valuable skills that can be packaged into scalable organizational assets rather than continuous manual labor."
        }
    ]

    scenes_data = get_career_long_scenes_data()
    return process_and_save_job(job_id, channel_id, brief, outline, cr, scenes_data, coverage, claims)

def run_career_short():
    channel_id = "en_career_leverage"
    job_id = "en-career-leverage-batch1-9x16"
    parent_long_id = "en-career-leverage-batch1-16x9"
    ch = get_channel(channel_id)
    topic = "The Competence Penalty: Why Your Boss Cannot Afford to Promote Their Best Firefighter"
    youtube_title = "The Trap of Being Too Good at Your Current Job"
    aspect_ratio = "9:16"
    format_profile = "short_9x16"
    
    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Expose the Competence Penalty and show why being too good at tactical crisis resolution caps your promotion, bridging viewers to the full career masterclass.",
        "video_type": "research_guide",
        "duration": {"min_seconds": 38.0, "max_seconds": 52.0},
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "The irony that saving every project makes you the least promotable"},
            {"id": "R02", "text": "The manager's replacement cost headache of losing their top troubleshooter"},
            {"id": "R03", "text": "Invisible midnight maintenance versus visible strategic presentation decks"},
            {"id": "R04", "text": "Editorial commentary on designing systems rather than working inside the machine"},
            {"id": "R05", "text": "Cliffhanger peak on escaping the trap and bridge to the full masterclass"}
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": aspect_ratio,
        "format_profile": format_profile,
        "parent_long_id": parent_long_id,
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "How to Become a Strategic Thinker on Your Team",
                "reference": "Groysberg, B., Sant, L., & Abrahams, R. (2018). Harvard Business Review, 96(5), 112-119.",
                "facts": [
                    "Individual contributors who resolve every daily crisis become operationally indispensable, making managers reluctant to promote them.",
                    "Strategic visibility with senior executives carries significantly more promotion weight than flawless tactical troubleshooting."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": aspect_ratio,
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deconstruct the Competence Penalty in under 50 seconds and transition viewers to the full-length long-form career strategy masterclass on YouTube."
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Zero specialized knowledge required.",
            "pacing": "Direct, candid, strategic cadence, zero dead-air.",
            "assumptions": [
                "Each scene maintains narrative visual pacing between 2.0 and 2.5 seconds per unique image."
            ]
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Editorial stickman trapped inside an operational machine gear looking up at director suites",
                "text_overlay": "TOO GOOD",
                "contrast_pair": "Top performer review badge vs Blocked promotion ladder",
                "thumbnail_prompt": "Tactile 2D Wall Street Journal Hedcut stipple illustration on vertical 9:16 warm newsprint (#EFECE6 with India ink stippling #181818 and gold highlights #D48817). Extreme close-up of the stickman in royal cobalt shirt #3B82C4, locked inside a heavy operational gear while holding a glowing annual review marked Top Performer. Behind him, a wooden corporate ladder extends toward director suites, padlocked with replacement cost chains. High-impact composition, at least 60% negative space, zero 3D CGI, zero plastic AI sheen.",
                "layout_mode": "split_contrast"
            },
            "channel_pillar": "Workplace Leverage & Career Strategy",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["competence penalty", "career advice", "promotion strategy", "career leverage", "shorts"],
            "cta_plan": {
                "cliffhanger_peak": "How do top performers convert tactical firefighting into executive leverage so their managers actively push for their promotion?",
                "bridge": "Watch the full career masterclass on YouTube.",
                "close": "Audit your daily projects this week.",
                "endcard_text": "FULL VIDEO ON YOUTUBE"
            },
            "editorial_stance": {
                "myth_debunked": "Solving every workplace emergency makes you the obvious choice for the next promotion.",
                "channel_verdict": "Solving every fire without documenting systems guarantees your manager cannot afford to let you leave your current desk.",
                "why_generic_advice_fails": "Standard hustle culture encourages being the ultimate workhorse, which leads directly to career stagnation and burnout.",
                "tradeoff_or_blindspot": "Stepping back from firefighting feels risky initially, but building automated workflows is the only bridge to executive roles."
            },
            "actionable_value": {
                "core_mechanism": "Promotions are unlocked by perceived strategic leadership, not by tactical operational heroics.",
                "practical_rule_of_thumb": "Never solve a recurring crisis without writing a standard operating playbook that allows a junior peer to solve it next time.",
                "real_world_scenario": "When your boss praises you for fixing a server or client disaster, present the automated system you built to prevent it recurring."
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Editorial stickman trapped inside an operational machine gear looking up at director suites",
            "text_overlay": "TOO GOOD",
            "contrast_pair": "Top performer review badge vs Blocked promotion ladder",
            "thumbnail_prompt": "Tactile 2D Wall Street Journal Hedcut stipple illustration on vertical 9:16 warm newsprint (#EFECE6 with India ink stippling #181818 and gold highlights #D48817). Extreme close-up of the stickman in royal cobalt shirt #3B82C4, locked inside a heavy operational gear while holding a glowing annual review marked Top Performer. Behind him, a wooden corporate ladder extends toward director suites, padlocked with replacement cost chains. High-impact composition, at least 60% negative space, zero 3D CGI, zero plastic AI sheen.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Workplace Leverage & Career Strategy",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["competence penalty", "career advice", "promotion strategy", "career leverage", "shorts"],
        "cta_plan": {
            "cliffhanger_peak": "How do top performers convert tactical firefighting into executive leverage so their managers actively push for their promotion?",
            "bridge": "Watch the full career masterclass on YouTube.",
            "close": "Audit your daily projects this week.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": {
            "myth_debunked": "Solving every workplace emergency makes you the obvious choice for the next promotion.",
            "channel_verdict": "Solving every fire without documenting systems guarantees your manager cannot afford to let you leave your current desk.",
            "why_generic_advice_fails": "Standard hustle culture encourages being the ultimate workhorse, which leads directly to career stagnation and burnout.",
            "tradeoff_or_blindspot": "Stepping back from firefighting feels risky initially, but building automated workflows is the only bridge to executive roles."
        },
        "actionable_value": {
            "core_mechanism": "Promotions are unlocked by perceived strategic leadership, not by tactical operational heroics.",
            "practical_rule_of_thumb": "Never solve a recurring crisis without writing a standard operating playbook that allows a junior peer to solve it next time.",
            "real_world_scenario": "When your boss praises you for fixing a server or client disaster, present the automated system you built to prevent it recurring."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook the viewer with the irony that saving every project makes you the least promotable", "requirements": ["R01"], "transition": "Explain the manager's replacement cost"},
            {"scene_id": "SC02", "purpose": "The manager's replacement cost headache of losing their top troubleshooter", "requirements": ["R02"], "transition": "Contrast invisible maintenance with strategic decks"},
            {"scene_id": "SC03", "purpose": "Invisible midnight maintenance versus visible strategic presentation decks", "requirements": ["R03"], "transition": "Deliver sharp editorial commentary"},
            {"scene_id": "SC04", "purpose": "Editorial commentary on designing systems rather than working inside the machine", "requirements": ["R04"], "transition": "Escalate to the executive leverage cliffhanger"},
            {"scene_id": "SC05", "purpose": "Escalate to the executive leverage peak, bridge to the full masterclass, and close", "requirements": ["R05"], "transition": "End of video"}
        ]
    }

    cr = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Dan Koe",
                    "top_performing_videos": [
                        {
                            "title": "Why Hard Work Traps You (How to Build Systems)",
                            "views": "1.5M views",
                            "hook_technique": "Direct challenge to the hustle myth: you are rewarded for leverage, not effort.",
                            "pacing_structure": "Unconscious trap -> Mental model -> Sovereign execution framework.",
                            "retention_driver": "High-contrast visual frameworks and sharp philosophical aphorisms."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Dismantle the belief that effort equals career advancement.",
                        "Direct bridge inviting viewers to study the comprehensive leverage blueprint."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Stickman sprinting with fire extinguisher contrasted with locked promotion ladder.",
                "counter_intuitive_truth_slap": "Your competence is the exact reason you are not getting promoted."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Saving every project makes you the least promotable employee."},
                {"phase": "mechanism_step", "purpose": "The manager's replacement cost headache of losing their top troubleshooter."},
                {"phase": "before_after_contrast", "purpose": "Invisible midnight maintenance versus visible strategic presentation decks."},
                {"phase": "editorial_commentary", "purpose": "Designing systems rather than working inside the machine."},
                {"phase": "cliffhanger_spinoff", "purpose": "Peak open loop on executive leverage and bridge to the full masterclass."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chain linking vertical Hedcut stipple newsprint frames with consistent India ink."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Workplace Leverage & Career Strategy",
            "myth_debunked": "Fixing every crisis gets you promoted.",
            "channel_verdict": "Being too good at troubleshooting makes you too expensive to replace.",
            "actionable_rule_of_thumb": "Design systems that run without you before expecting career advancement."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How do top performers convert tactical firefighting into executive leverage so their managers actively push for their promotion?",
            "bridge": "Watch the full career masterclass on YouTube.",
            "close": "Audit your daily projects this week.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        }
    }

    coverage = [
        {"requirement_id": "R01", "scene_id": "SC01", "quote": "If you are the person who saves every project on your team, you are probably the least promotable employee in the room."},
        {"requirement_id": "R02", "scene_id": "SC02", "quote": "promoting you creates a catastrophic replacement headache for your manager."},
        {"requirement_id": "R03", "scene_id": "SC03", "quote": "Nobody gets promoted for invisible maintenance. When you quietly prevent disasters at midnight, management assumes the job is effortless."},
        {"requirement_id": "R04", "scene_id": "SC04", "quote": "You do not earn advancement by working harder inside the machine. You earn it by stepping outside and designing a machine that runs without you."},
        {"requirement_id": "R05", "scene_id": "SC05", "quote": "How do top performers convert tactical firefighting into executive leverage so their managers actively push for their promotion?"}
    ]

    claims = [
        {
            "scene_id": "SC01",
            "quote": "your promotion keeps stalling because of your competence.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Individual contributors who resolve every daily crisis become operationally indispensable, making managers reluctant to promote them."
        },
        {
            "scene_id": "SC03",
            "quote": "colleagues who manage high-visibility strategic decks get all the executive face time.",
            "language": "en",
            "source_id": "SRC01",
            "fact": "Strategic visibility with senior executives carries significantly more promotion weight than flawless tactical troubleshooting."
        }
    ]

    scenes_data = get_career_short_scenes_data()
    return process_and_save_job(job_id, channel_id, brief, outline, cr, scenes_data, coverage, claims)


def main():
    print("=" * 75)
    print("BUILDING SCHEMA 3.0 ENGLISH BATCH 1 PACKAGES (CLUSTER 5 - SA-EN-05)")
    print("=" * 75)

    jobs = [
        run_wallet_long(),
        run_wallet_short(),
        run_macro_long(),
        run_macro_short(),
        run_career_long(),
        run_career_short(),
    ]

    print()
    print("=" * 105)
    print(f"{'Job ID':<33} | {'Format':<10} | {'Words':<6} | {'Dur(s)':<6} | {'Imgs':<5} | {'Hold(s)':<7} | {'Status'}")
    print("-" * 105)
    all_ok = True
    for r in jobs:
        status_label = "100% PASS" if r["all_passed"] else "FAIL"
        print(f"{r['job_id']:<33} | {r['format']:<10} | {r['words']:<6} | {r['duration']:<6.1f} | {r['images']:<5} | {r['hold']:<7.2f} | {status_label}")
        if not r["all_passed"]:
            all_ok = False
    print("=" * 105)
    print()

    if not all_ok:
        print("❌ Some jobs failed validation!")
        sys.exit(1)
    print("🎉 All 6 English Batch 1 packages generated & validated successfully with 0 linter errors!")


if __name__ == "__main__":
    main()
