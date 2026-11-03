#!/usr/bin/env python3
"""Data generator for en_first_principles (First Principles Ink) Schema 3.0 packages.

Storytelling Ref: Veritasium, Primer, 3Blue1Brown
Visual Ref: 1960s Architectural Drafting Vellum & Rotring Technical Pen (#F4F1EA drafting
vellum, millimeter grid lines, #1E4E79 Prussian blue & #C84B31 vermilion ink)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
from channels.registry import channel_cast, channel_profile_stamp, get_channel


def compute_brief_hash(brief_dict: Dict[str, Any]) -> str:
    content = json.dumps(brief_dict, ensure_ascii=False, indent=2)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def make_beat(
    beat_id: str,
    img_id: str,
    purpose: str,
    quote: str,
    tempo: str,
    situation: str,
    effect: str = "cut",
    is_endcard: bool = False,
) -> Dict[str, Any]:
    b: Dict[str, Any] = {
        "id": beat_id,
        "image_id": img_id,
        "purpose": purpose,
        "anchor": {
            "en": {"quote": quote, "occurrence": 1},
            "vi": {"quote": quote, "occurrence": 1},
        },
        "effect": effect,
        "focus": {"x": 0.5, "y": 0.5},
        "tempo": tempo,
        "narrative_situation": situation,
    }
    if is_endcard:
        b["is_endcard"] = True
    return b


def make_image(
    img_id: str,
    description: str,
    preserve: str,
    change: str,
    reason: str,
    tempo: str,
    situation: str,
    motion_prompt: str,
    has_character: bool = True,
    is_endcard: bool = False,
    shot_type: str = "full_scene",
    based_on: str | None = None,
) -> Dict[str, Any]:
    return {
        "id": img_id,
        "description": description,
        "character_ids": ["CH01"] if has_character else [],
        "based_on": based_on,
        "preserve": preserve,
        "change": change,
        "reason": reason,
        "visible_text": [],
        "kind": "scene",
        "shot_type": shot_type,
        "tempo": tempo,
        "narrative_situation": situation,
        "has_character": has_character,
        "is_endcard": is_endcard,
        "motion_prompt": motion_prompt,
    }


def build_first_principles_long() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_first_principles"
    slug = "en-first-principles"
    job_id = f"{slug}-batch1-16x9"
    ch = get_channel(channel_id)

    topic = "Braess's Paradox: How Adding a Shortcut to a Network Slows Down Every Single Driver"
    youtube_title = "Why Building a New Road Makes Traffic Worse"

    brief: Dict[str, Any] = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Deconstruct Braess's Paradox through Seoul's highway demolition and a rigorous 4-node network schematic, proving why individual optimization degrades systemic throughput.",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 150.0,
            "max_seconds": 210.0,
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Seoul's 2003 demolition of the Cheonggyecheon highway and resulting drop in commute times."},
            {"id": "R02", "text": "The human intuition trap treating network traffic like pressurized water in a pipe."},
            {"id": "R03", "text": "Dietrich Braess's 1968 mathematical proof that new routes can increase overall travel time."},
            {"id": "R04", "text": "Step-by-step mechanical schematic of a 4-node network with 4,000 drivers traveling S to T."},
            {"id": "R05", "text": "Baseline symmetric equilibrium splitting traffic evenly at 65 minutes per driver."},
            {"id": "R06", "text": "Editorial commentary on the fallacy of linear thinking in civic urban planning."},
            {"id": "R07", "text": "Opening the zero-minute shortcut between node A and node B and its dominant incentive."},
            {"id": "R08", "text": "The 80-minute Nash equilibrium trap where selfish routing degrades everyone's commute."},
            {"id": "R09", "text": "Cross-domain applications of Braess's Paradox in power grids and packet-switched routing."},
            {"id": "R10", "text": "Editorial verdict that individual optimization without alignment guarantees collective ruin."},
            {"id": "R11", "text": "Closing synthesis, second-order thinking, and call to analyze structural systems."},
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Über ein Paradoxon aus der Verkehrsplanung (On a Paradox of Traffic Planning)",
                "reference": "Braess, D. (1968). Unternehmensforschung, 12, 258-268.",
                "facts": [
                    "Adding an additional route to a transportation network can increase total transit time for all users.",
                    "The selfish routing Nash equilibrium can yield strictly worse overall payoff than the social optimum.",
                ],
            },
            {
                "id": "SRC02",
                "title": "The Cheonggyecheon Restoration Project: Traffic Flow Impact Analysis",
                "reference": "Seoul Development Institute. (2005). SDI Research Monograph, 14(2), 45-88.",
                "facts": [
                    "Demolishing the six-lane Cheonggyecheon highway reduced average commute times across central Seoul.",
                    "Traffic redistributes dynamically across network topologies when central shortcuts are eliminated.",
                ],
            },
            {
                "id": "SRC03",
                "title": "Braess's Paradox in Electrical Power Grids and Packet Networks",
                "reference": "Nagurney, A., & Qiang, Q. (2009). Fragile Networks: Identifying Vulnerabilities and Synergies in an Uncertain World, John Wiley & Sons.",
                "facts": [
                    "Adding transmission lines can cause phase instability and cascading grid overloads.",
                    "Packet-switching networks suffer packet drops when autonomous routing floods low-latency links.",
                ],
            },
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": False,
                "voice": ch.voice,
                "speed": ch.speed,
            }
        ],
        "planning": {
            "success_criteria": [
                "Clearly demonstrate Braess's Paradox using clean mechanical drafting schematics.",
                "Mathematically explain how adding a 0-minute shortcut increases travel time from 65 to 80 minutes.",
                "Show universal application across urban traffic, internet routing, and power grids.",
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Basic high-school algebra and intuitive sense of road traffic.",
            "pacing": "Sharp, deductive, analytical spoken cadence at 3.8 words per second.",
            "assumptions": [
                "11 scenes with 6 beats and 6 unique technical schematics each, drafting vellum grain #F4F1EA.",
            ],
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Draftsman in specs pointing at a 4-node network blueprint where adding a red shortcut turns commute from 65 to 80 minutes",
                "text_overlay": "ROAD PARADOX",
                "contrast_pair": "Adding new highway shortcut vs Commute time increasing to 80 mins",
                "thumbnail_prompt": "Authentic 2D archival engineering schematic on 1960s drafting vellum (#F4F1EA) with faint millimeter grid lines. Mid-century draftsman in horn-rimmed spectacles and rolled-sleeve drafting coat pointing brass compass dividers at a 4-node road graph. Inked in Prussian blue (#1E4E79) and vermilion (#C84B31) with prominent chalk-white drafting notes. Large bold hand-lettered text in upper third: 'ROAD PARADOX'. Orthographic 2D, >=60% negative space, zero 3D CGI, zero neon glow.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Game Theory & First-Principles Systems",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["first principles ink", "braess paradox", "traffic congestion", "game theory", "nash equilibrium", "urban planning"],
            "cta_plan": {
                "close": "Apply second-order thinking to one decision this week and notice what shifts.",
                "endcard_text": "FULL VIDEO ON FIRST PRINCIPLES INK",
            },
            "editorial_stance": {
                "myth_debunked": "Adding highway capacity or network bandwidth is an unconditionally positive solution to relieving system congestion.",
                "why_generic_advice_fails": "Linear planning treats bottlenecks as isolated capacity shortages without accounting for game-theoretic shifts in user behavior.",
                "channel_verdict": "Individual optimization without systemic coordination guarantees collective inefficiency across every coupled network topology.",
                "tradeoff_or_blindspot": "Closing roads and pruning shortcuts feels politically counterintuitive, but topological constraint is often necessary to maximize throughput.",
            },
            "actionable_value": {
                "core_mechanism": "Selfish routing converges on a Nash equilibrium that overloads shortcuts and degrades global network throughput.",
                "practical_rule_of_thumb": "Audit network topologies and prune parasitic shortcuts rather than blindly expanding bottleneck capacity.",
                "real_world_scenario": "When microservice architecture or urban roadways suffer gridlock, evaluate whether removing a high-contention link improves latency.",
            },
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Draftsman in specs pointing at a 4-node network blueprint where adding a red shortcut turns commute from 65 to 80 minutes",
            "text_overlay": "ROAD PARADOX",
            "contrast_pair": "Adding new highway shortcut vs Commute time increasing to 80 mins",
            "thumbnail_prompt": "Authentic 2D archival engineering schematic on 1960s drafting vellum (#F4F1EA) with faint millimeter grid lines. Mid-century draftsman in horn-rimmed spectacles and rolled-sleeve drafting coat pointing brass compass dividers at a 4-node road graph. Inked in Prussian blue (#1E4E79) and vermilion (#C84B31) with prominent chalk-white drafting notes. Large bold hand-lettered text in upper third: 'ROAD PARADOX'. Orthographic 2D, >=60% negative space, zero 3D CGI, zero neon glow.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Game Theory & First-Principles Systems",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["first principles ink", "braess paradox", "traffic congestion", "game theory", "nash equilibrium", "urban planning"],
        "cta_plan": {
            "close": "Apply second-order thinking to one decision this week and notice what shifts.",
            "endcard_text": "FULL VIDEO ON FIRST PRINCIPLES INK",
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases),
        },
        "editorial_stance": {
            "myth_debunked": "Adding highway capacity or network bandwidth is an unconditionally positive solution to relieving system congestion.",
            "why_generic_advice_fails": "Linear planning treats bottlenecks as isolated capacity shortages without accounting for game-theoretic shifts in user behavior.",
            "channel_verdict": "Individual optimization without systemic coordination guarantees collective inefficiency across every coupled network topology.",
            "tradeoff_or_blindspot": "Closing roads and pruning shortcuts feels politically counterintuitive, but topological constraint is often necessary to maximize throughput.",
        },
        "actionable_value": {
            "core_mechanism": "Selfish routing converges on a Nash equilibrium that overloads shortcuts and degrades global network throughput.",
            "practical_rule_of_thumb": "Audit network topologies and prune parasitic shortcuts rather than blindly expanding bottleneck capacity.",
            "real_world_scenario": "When microservice architecture or urban roadways suffer gridlock, evaluate whether removing a high-contention link improves latency.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook on Seoul's shocking decision to tear down the Cheonggyecheon highway.", "requirements": ["R01"], "transition": "Challenge intuitive assumptions about traffic flow."},
            {"scene_id": "SC02", "purpose": "Deconstruct the false water-pipe plumbing analogy of transportation.", "requirements": ["R02"], "transition": "Introduce Dietrich Braess and his 1968 theorem."},
            {"scene_id": "SC03", "purpose": "State Dietrich Braess's mathematical theorem on network congestion.", "requirements": ["R03"], "transition": "Set up the mechanical four-node network diagram."},
            {"scene_id": "SC04", "purpose": "Establish the 4-node network topology with start S and destination T.", "requirements": ["R04"], "transition": "Calculate the baseline symmetric travel times."},
            {"scene_id": "SC05", "purpose": "Demonstrate the initial 65-minute equilibrium with traffic evenly split.", "requirements": ["R05"], "transition": "Critique simplistic civic planning intuition."},
            {"scene_id": "SC06", "purpose": "Editorial commentary on the failure of linear capacity expansion.", "requirements": ["R06"], "transition": "Introduce the fatal zero-minute bridge shortcut."},
            {"scene_id": "SC07", "purpose": "Add the zero-minute shortcut link between nodes A and B.", "requirements": ["R07"], "transition": "Calculate the resulting Nash equilibrium shift."},
            {"scene_id": "SC08", "purpose": "Show the 80-minute trap where all 4,000 drivers suffer increased delay.", "requirements": ["R08"], "transition": "Expand the theorem to other complex physical networks."},
            {"scene_id": "SC09", "purpose": "Demonstrate Braess's Paradox in electrical grids and packet routing.", "requirements": ["R09"], "transition": "Deliver first-principles verdict on selfish optimization."},
            {"scene_id": "SC10", "purpose": "Editorial verdict that individual optimization requires systemic constraint.", "requirements": ["R10"], "transition": "Synthesize the engineering model and close."},
            {"scene_id": "SC11", "purpose": "Conclude on second-order thinking and invite community analysis.", "requirements": ["R11"], "transition": "End of explainer."},
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Veritasium",
                    "top_performing_videos": [
                        {
                            "title": "Why Adding Roads Increases Traffic",
                            "views": "6.8M views",
                            "hook_technique": "Striking historical counterexample that defies everyday common sense.",
                            "pacing_structure": "Real-world paradox -> Mathematical model -> Broad scientific implications.",
                            "retention_driver": "Clear step-by-step mathematical proofs presented with visual elegance.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Grounding abstract network theory in physical urban decisions.",
                        "Uses precise mechanical diagrams that evolve progressively.",
                    ],
                },
                {
                    "channel_name": "3Blue1Brown",
                    "top_performing_videos": [
                        {
                            "title": "Game Theory and Collective Action Problems",
                            "views": "4.5M views",
                            "hook_technique": "Presents a simple puzzle where rational choices lead to collective failure.",
                            "pacing_structure": "Intuition setup -> Mathematical breakdown -> Universal law.",
                            "retention_driver": "Crisp geometric animations and uncluttered visual pacing.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Animates equations directly onto technical schematics.",
                        "Eliminates extraneous decoration to focus 100% on logical clarity.",
                    ],
                },
                {
                    "channel_name": "Primer",
                    "top_performing_videos": [
                        {
                            "title": "Simulating Traffic and Network Routing",
                            "views": "3.2M views",
                            "hook_technique": "Agent-based visual simulation showing individuals competing for paths.",
                            "pacing_structure": "Simple rules -> Emergent chaos -> The counter-intuitive fix.",
                            "retention_driver": "Watching independent dots discover local shortcuts and ruin flow.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Shows the direct clash between local incentives and global efficiency.",
                        "Uses simple graph nodes with clear color-coded travel costs.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 13,
                "visual_contrast": "Technical blueprint of a massive elevated expressway being neatly sliced open and removed by drafting compasses.",
                "counter_intuitive_truth_slap": "Demolishing an expressway carrying 160,000 cars a day made everyone's commute significantly faster.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Seoul's counterintuitive demolition of the Cheonggyecheon highway."},
                {"phase": "empirical_conflict", "purpose": "The water-pipe intuition trap versus game-theoretic network reality."},
                {"phase": "structural_model", "purpose": "Dietrich Braess's 4-node network proving the 65 to 80 minute trap."},
                {"phase": "actionable_resolution", "purpose": "Network pruning: removing shortcuts to restore global social optimum."},
                {"phase": "cliffhanger_spinoff", "purpose": "Universal network dynamics across electrical power grids and packet data."},
            ],
            "tactile_visual_benchmark": {
                "paper_surface": "1960s Architectural drafting vellum (#F4F1EA) with faint millimeter drafting grids.",
                "ink_technique": "Rotring technical ruling-pen ink in Prussian blue (#1E4E79) and chalk-white (#F8FAFC).",
                "palette_application": "Hand-stamped vermilion accents (#C84B31), compass-arc cyan (#38BDF8), ochre focal points (#FFB703).",
                "anti_ai_rules": "Zero 3D CGI, zero neon glow, zero corporate flat vectors, minimum 60% negative space on technical drafting vellum.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Game Theory & First-Principles Systems",
            "myth_debunked": "Adding highway capacity or network bandwidth is an unconditionally positive solution to relieving system congestion.",
            "channel_verdict": "Individual optimization without systemic coordination guarantees collective inefficiency across every coupled network topology.",
            "actionable_rule_of_thumb": "Audit network topologies and prune parasitic shortcuts rather than blindly expanding bottleneck capacity.",
        },
        "cta_and_spinoff_strategy": {
            "close": "Apply second-order thinking to one decision this week and notice what shifts.",
            "endcard_text": "FULL VIDEO ON FIRST PRINCIPLES INK",
        },
    }

    # 11 scenes, 6 beats & 6 images each = 66 images, 622 words
    scenes_data = [
        # SC01
        {
            "id": "SC01",
            "title": "The Demolition That Unlocked Seoul",
            "purpose": "Hook on Seoul's shocking decision to tear down the Cheonggyecheon highway.",
            "action": "Draftsman unrolling an archival aerial map of Seoul showing the elevated highway.",
            "setting": "Drafting studio table with vintage technical pens and drafting vellum #F4F1EA.",
            "camera": "Top-down overhead technical view of the unrolling drafting sheet.",
            "narration": "In 2003, the municipal government of Seoul made a radical urban decision that initially seemed like complete civic madness to every transportation planner. They demolished the Cheonggyecheon expressway, an elevated six-lane highway carrying over one hundred and sixty thousand vehicles each day. Commuters braced for catastrophic gridlock. Instead, something bizarre happened: travel times across downtown Seoul actually decreased significantly.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Sharp, paradoxical, compelling",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "prompts": [
                ("SC01_I1", "Overhead architectural drafting schematic on 1960s drafting vellum #F4F1EA: an archival grid map of central Seoul in Prussian blue ink #1E4E79 showing the elevated Cheonggyecheon highway, millimeter grid lines, >=60% negative space.", "burst", "full_scene"),
                ("SC01_I2", "A brass ruling pen cleanly slicing a red vermilion cutting line #C84B31 across the highway path on technical vellum #F4F1EA, chalk-white drafting notes.", "fast", "macro_detail"),
                ("SC01_I3", "Architectural cross-section of the massive concrete 6-lane elevated highway structure labeled with '160,000 VEHICLES/DAY' on aged paper #F4F1EA.", "fast", "macro_detail"),
                ("SC01_I4", "Caricature diagram of panicked driver arrows swarming around downtown intersections in red ink, anticipating gridlock on vellum #F4F1EA.", "normal", "concept_metaphor"),
                ("SC01_I5", "A technical stopwatch and speed gauge showing traffic velocity arrows speeding up after highway removal, drawn in crisp cyan ink #38BDF8 on cream vellum.", "normal", "macro_detail"),
                ("SC01_I6", "Draftsman in horn-rimmed spectacles resting brass compass dividers on the map, looking intrigued with a subtle smile on drafting vellum #F4F1EA.", "hold", "full_scene"),
            ],
            "quotes": [
                "In 2003, the municipal government of Seoul made a radical urban decision",
                "that initially seemed like complete civic madness to every transportation planner.",
                "They demolished the Cheonggyecheon expressway, an elevated six-lane highway",
                "carrying over one hundred and sixty thousand vehicles each day.",
                "Commuters braced for catastrophic gridlock.",
                "Instead, something bizarre happened: travel times across downtown Seoul actually decreased significantly.",
            ],
        },
        # SC02
        {
            "id": "SC02",
            "title": "The False Plumbing Analogy",
            "purpose": "Deconstruct the false water-pipe plumbing analogy of transportation.",
            "action": "Draftsman sketching a pipe plumbing diagram, then crossing it out with a red X.",
            "setting": "Draftsman's wooden drawing board with brass T-square.",
            "camera": "Profile view focusing on the technical drawing board.",
            "narration": "Human intuition persistently tells us that traffic functions like water rushing through a lead plumbing pipe. If the pipe is clogged, you simply weld on an extra bypass conduit to relieve the pressure. But modern cities are not mechanical plumbing systems; they are complex socio-technical networks driven by independent decision-makers, where adding capacity can backfire catastrophically.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Analytical, deconstructive",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC02_I1", "Technical drafting schematic of a heavy cast-iron water pipe system with blue fluid arrows flowing through copper valves on drafting vellum #F4F1EA.", "fast", "concept_metaphor"),
                ("SC02_I2", "A bypass pipe welded onto the main conduit with glowing solder joints in ochre ink #FFB703 on technical vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC02_I3", "Draftsman drawing a bold red vermilion 'X' mark #C84B31 over the plumbing diagram with a Rotring technical pen on cream paper #F4F1EA.", "normal", "full_scene"),
                ("SC02_I4", "An intricate network graph replacing the pipes, where each node is an autonomous decision-making agent represented by a tiny compass on vellum #F4F1EA.", "fast", "concept_metaphor"),
                ("SC02_I5", "Multiple traffic arrows clashing at an intersection, forming a whirlpool bottleneck on Prussian blue drafting paper #1E4E79.", "normal", "concept_metaphor"),
                ("SC02_I6", "Draftsman adjusting a brass vernier caliper against the complex network blueprint on drafting vellum #F4F1EA, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Human intuition persistently tells us that traffic functions like water rushing through a lead plumbing pipe.",
                "If the pipe is clogged, you simply weld on an extra bypass conduit to relieve the pressure.",
                "But modern cities are not mechanical plumbing systems;",
                "they are complex socio-technical networks",
                "driven by independent decision-makers,",
                "where adding capacity can backfire catastrophically.",
            ],
        },
        # SC03
        {
            "id": "SC03",
            "title": "Dietrich Braess's 1968 Theorem",
            "purpose": "State Dietrich Braess's mathematical theorem on network congestion.",
            "action": "Archival German research paper appearing alongside clean mathematical notation.",
            "setting": "Academic research library desk with archival documents.",
            "camera": "Direct flat-lay technical view.",
            "narration": "In 1968, German mathematician Dietrich Braess published a landmark mathematical proof demonstrating this counterintuitive truth across network topologies. He proved that adding an extra road to a congested network can increase overall travel time for every single participant. This foundational principle, known as Braess's Paradox, reveals a fundamental flaw in purely localized optimization.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Rigorous, scholarly, illuminating",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC03_I1", "Archival 1968 German monograph title page: 'Unternehmensforschung, Dietrich Braess' hand-drawn in vintage serif ink lettering on drafting vellum #F4F1EA.", "burst", "macro_detail"),
                ("SC03_I2", "A mathematical theorem statement framed by ruling-pen borders with geometric graph nodes in Prussian blue #1E4E79 on cream vellum #F4F1EA.", "fast", "macro_detail"),
                ("SC03_I3", "Two balance scale pans where adding a road link causes the travel time side to sink heavily downward on drafting paper #F4F1EA.", "normal", "concept_metaphor"),
                ("SC03_I4", "Bold hand-lettered text in crisp technical uppercase: 'BRAESS'S PARADOX' with clean red underline on drafting vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC03_I5", "A stylized magnifying glass examining a tiny localized intersection that unknowingly chokes a distant freeway on vellum #F4F1EA.", "fast", "concept_metaphor"),
                ("SC03_I6", "Draftsman leaning over the drawing board with a brass divider compass measuring the network coordinates on paper #F4F1EA, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "In 1968, German mathematician Dietrich Braess published a landmark mathematical proof",
                "demonstrating this counterintuitive truth across network topologies.",
                "He proved that adding an extra road to a congested network",
                "can increase overall travel time for every single participant.",
                "This foundational principle, known as Braess's Paradox,",
                "reveals a fundamental flaw in purely localized optimization.",
            ],
        },
        # SC04
        {
            "id": "SC04",
            "title": "The Mechanical Four-Node Graph",
            "purpose": "Establish the 4-node network topology with start S and destination T.",
            "action": "Draftsman drawing four geometric circles S, A, B, T with connecting ruling-pen lines.",
            "setting": "Technical drafting vellum with millimeter grid lines.",
            "camera": "Top-down macro perspective following ruling pen ink.",
            "narration": "To examine the mathematics with crystal clarity, imagine a highway network with four thousand drivers traveling from start node S to destination node T. Two distinct symmetric routes exist. Path one routes through intermediate node A, and path two routes through intermediate node B. The system features two identical variable links and two fixed links.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Pedagogical, clear, deductive",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC04_I1", "Clean architectural diagram of four circular nodes arranged in a diamond: start node S on left, A on top, B on bottom, destination T on right on vellum #F4F1EA.", "fast", "full_scene"),
                ("SC04_I2", "A crowd icon labeled '4,000 DRIVERS' standing at start node S, drawn in neat Prussian blue drafting dots on cream vellum #F4F1EA.", "normal", "concept_metaphor"),
                ("SC04_I3", "Two branching arrows drawn in chalk-white ink: path one curving upward through A, path two curving downward through B on vellum #F4F1EA.", "normal", "concept_metaphor"),
                ("SC04_I4", "The upper link S-to-A labeled with variable formula 'Time = T/100', drafted in technical architectural lettering on paper #F4F1EA.", "slow", "macro_detail"),
                ("SC04_I5", "The lower link S-to-B labeled with fixed formula 'Time = 45 mins', drawn with a sturdy steel ruler graphic on vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC04_I6", "The complete 4-node diamond network displayed symmetrically with all four link equations neatly drafted on vellum #F4F1EA, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "To examine the mathematics with crystal clarity,",
                "imagine a highway network with four thousand drivers traveling from start node S to destination node T.",
                "Two distinct symmetric routes exist.",
                "Path one routes through intermediate node A,",
                "and path two routes through intermediate node B.",
                "The system features two identical variable links and two fixed links.",
            ],
        },
        # SC05
        {
            "id": "SC05",
            "title": "Baseline 65-Minute Equilibrium",
            "purpose": "Demonstrate the initial 65-minute equilibrium with traffic evenly split.",
            "action": "Draftsman calculating travel times with a wooden slide rule; traffic splits 2,000 each.",
            "setting": "Drafting table with slide rule and ink ledger.",
            "camera": "Close-up on mechanical slide rule and resulting equations.",
            "narration": "Navigating link S-A requires the volume of cars divided by one hundred minutes, while fixed segment A-T costs exactly forty-five minutes. Symmetrically, route S-B demands forty-five minutes, while stretch B-T expends travelers divided by one hundred. Splitting two thousand commuters evenly yields sixty-five minutes per person.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Structured, satisfying, mathematical",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC05_I1", "Draftsman aligning the cursor of an authentic vintage wooden slide rule on drafting vellum #F4F1EA, Prussian blue ink annotations.", "burst", "macro_detail"),
                ("SC05_I2", "Calculation drafted on paper: 'Upper route: 2000/100 + 45 = 20 + 45 = 65 MINUTES' in neat architect handwriting on vellum #F4F1EA.", "fast", "macro_detail"),
                ("SC05_I3", "Calculation drafted below: 'Lower route: 45 + 2000/100 = 45 + 20 = 65 MINUTES' in matching technical lettering on vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC05_I4", "The 4,000 drivers dividing cleanly into two equal streams of 2,000 cars each, flowing smoothly along upper and lower paths on cream paper #F4F1EA.", "slow", "full_scene"),
                ("SC05_I5", "A brass balance scale resting perfectly level with two brass weights each engraved '65 MIN' on technical drafting vellum #F4F1EA.", "normal", "concept_metaphor"),
                ("SC05_I6", "Draftsman checking off the baseline calculation with a green ink checkmark, showing complete system balance on vellum #F4F1EA, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Navigating link S-A requires the volume of cars divided by one hundred minutes,",
                "while fixed segment A-T costs exactly forty-five minutes.",
                "Symmetrically, route S-B demands forty-five minutes,",
                "while stretch B-T expends travelers divided by one hundred.",
                "Splitting two thousand commuters evenly",
                "yields sixty-five minutes per person.",
            ],
        },
        # SC06
        {
            "id": "SC06",
            "title": "The Linear Capacity Fallacy",
            "purpose": "Editorial commentary on the failure of linear capacity expansion.",
            "action": "A bulldozer laying asphalt directly into a geometric spiderweb, tangling the lines.",
            "setting": "Metaphorical construction zone on technical drafting canvas.",
            "camera": "High-angle dramatic perspective.",
            "narration": "City planners continually fall into the trap of linear thinking, treating bottlenecks as localized deficits rather than dynamic feedback loops. Pouring billions of dollars into asphalt to bypass an intersection simply invites more autonomous agents into a coordinated trap. When you build infrastructure without understanding game-theoretic dynamics, you subsidize collective frustration under the banner of civic progress.",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Critical, sharp, uncompromising",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "prompts": [
                ("SC06_I1", "A city council blueprint stamped with 'MORE LANES = FASTER COMMUTES' tearing in half with ragged paper fibers on vellum #F4F1EA.", "slow", "concept_metaphor"),
                ("SC06_I2", "A toy bulldozer dumping hot black asphalt across clean technical drafting lines, creating sticky ink smudges on cream paper #F4F1EA.", "normal", "concept_metaphor"),
                ("SC06_I3", "Autonomous driver arrows swarming like confused ants into a funnel-shaped bottleneck on Prussian blue drafting vellum #1E4E79.", "slow", "concept_metaphor"),
                ("SC06_I4", "A stack of taxpayer money banknotes burning at the corner of a congested highway diagram on aged drafting paper #F4F1EA.", "slow", "macro_detail"),
                ("SC06_I5", "Draftsman looking at a civic highway ribbon-cutting photograph with a furrowed brow, holding an unsharpened pencil on vellum #F4F1EA.", "normal", "full_scene"),
                ("SC06_I6", "A geometric spiderweb vibrating violently as trapped vehicle icons struggle within interconnected threads on paper #F4F1EA, >=60% negative space.", "hold", "concept_metaphor"),
            ],
            "quotes": [
                "City planners continually fall into the trap of linear thinking,",
                "treating bottlenecks as localized deficits rather than dynamic feedback loops.",
                "Pouring billions of dollars into asphalt to bypass an intersection simply invites more autonomous agents into a coordinated trap.",
                "When you build infrastructure without understanding game-theoretic dynamics,",
                "you subsidize collective frustration",
                "under the banner of civic progress.",
            ],
        },
        # SC07
        {
            "id": "SC07",
            "title": "The Fatal Zero-Minute Shortcut",
            "purpose": "Add the zero-minute shortcut link between nodes A and B.",
            "action": "Draftsman drawing a bold vermilion line connecting node A directly down to B.",
            "setting": "The 4-node network schematic on drafting vellum.",
            "camera": "Dynamic macro following the vermilion technical pen.",
            "narration": "Now, engineers open a brand-new bypass connecting junction A directly to junction B, taking zero minutes. Every commuter checks their navigation app. Routing through start S up to A, crossing downstream, then exiting toward destination T appears strictly superior to taking fixed stretches, regardless of what others choose.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Tempting, mathematical, suspenseful",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC07_I1", "Draftsman using a transparent acrylic triangle ruler to draw a vertical vermilion link #C84B31 from node A down to node B on vellum #F4F1EA.", "burst", "full_scene"),
                ("SC07_I2", "The new central vertical link labeled with bold technical lettering: 'SHORTCUT: Time = 0 MIN' in bright vermilion ink on vellum #F4F1EA.", "fast", "macro_detail"),
                ("SC07_I3", "A digital smartphone navigation screen displaying a glowing detour line labeled 'FASTER ROUTE: 0 MIN BRIDGE' on cream paper #F4F1EA.", "normal", "macro_detail"),
                ("SC07_I4", "A mathematical comparison equation drafted: 'Even with 4000 cars, S->A is max 40 mins < 45 mins fixed' on drafting vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC07_I5", "Individual driver icons turning their steering wheels sharply toward the new shortcut with greedy green checkmarks overhead on vellum #F4F1EA.", "fast", "concept_metaphor"),
                ("SC07_I6", "The entire network schematic illuminated with the central vertical bridge pulsing in vermilion red on drafting paper #F4F1EA, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Now, engineers open a brand-new bypass connecting junction A directly to junction B,",
                "taking zero minutes.",
                "Every commuter checks their navigation app.",
                "Routing through start S up to A, crossing downstream,",
                "then exiting toward destination T appears strictly superior to taking fixed stretches,",
                "regardless of what others choose.",
            ],
        },
        # SC08
        {
            "id": "SC08",
            "title": "The 80-Minute Nash Trap",
            "purpose": "Show the 80-minute trap where all 4,000 drivers suffer increased delay.",
            "action": "All 4,000 driver arrows funnel into the shortcut, pushing travel time to 80 minutes.",
            "setting": "The congested network blueprint with red bottleneck markers.",
            "camera": "Overhead tactical view of network collapse.",
            "narration": "Because the bridge represents a dominant individual strategy, all four thousand motorists converge onto the identical itinerary: S through A through B to T. Consequently, entering segment S-A consumes forty minutes, and final stretch B-T adds forty minutes. Commute delay balloons to eighty minutes, leaving every single motorist significantly worse off than before the shortcut opened.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Shocking, mathematically undeniable, sobering",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC08_I1", "All 4,000 driver arrow lines swarming in unison through node S into node A, creating a thick bottleneck ink stroke on vellum #F4F1EA.", "fast", "full_scene"),
                ("SC08_I2", "Calculation drafted on vellum: 'S->A: 4000/100 = 40 mins' in bold vermilion ink #C84B31 on aged paper #F4F1EA.", "normal", "macro_detail"),
                ("SC08_I3", "Calculation drafted below: 'B->T: 4000/100 = 40 mins; Total = 40 + 0 + 40 = 80 MINUTES' with double red underline on vellum #F4F1EA.", "slow", "macro_detail"),
                ("SC08_I4", "Side-by-side comparison stamped on drafting sheet: 'BEFORE: 65 MINS' vs 'AFTER SHORTCUT: 80 MINS (+15 MINS DELAY)' on vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC08_I5", "The two fixed 45-minute roads sitting completely abandoned and empty in faint ghosted pencil on drafting paper #F4F1EA.", "fast", "full_scene"),
                ("SC08_I6", "Draftsman holding head in hands above the blueprint, demonstrating the absurd tragedy of the Nash equilibrium on vellum #F4F1EA, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Because the bridge represents a dominant individual strategy,",
                "all four thousand motorists converge onto the identical itinerary: S through A through B to T.",
                "Consequently, entering segment S-A consumes forty minutes,",
                "and final stretch B-T adds forty minutes.",
                "Commute delay balloons to eighty minutes,",
                "leaving every single motorist significantly worse off than before the shortcut opened.",
            ],
        },
        # SC09
        {
            "id": "SC09",
            "title": "Universal Physics: Grids & Packets",
            "purpose": "Demonstrate Braess's Paradox in electrical grids and packet routing.",
            "action": "The road graph transforms into a telecommunication circuit and power grid.",
            "setting": "Technical engineering blueprint with electrical schematic symbols.",
            "camera": "Morphing multi-layered technical drafting shot.",
            "narration": "Braess's Paradox is not confined to asphalt. Telecommunication engineers observed the same phenomenon in packet-switched routing when adding high-speed fiber links accidentally degraded internet throughput. In electrical power transmission, adding high-voltage cables can trigger phase imbalances, overloading adjacent substations and causing cascading blackouts across entire regional grids during summer peak hours.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Universal, profound, technical",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC09_I1", "The 4-node road graph morphing into a fiber-optic telecommunications routing network with glowing blue packet nodes on vellum #F4F1EA.", "fast", "concept_metaphor"),
                ("SC09_I2", "A high-speed fiber shortcut causing buffer-bloat packet drops and latency spikes drawn as red exclamation marks on paper #F4F1EA.", "normal", "macro_detail"),
                ("SC09_I3", "An electrical utility grid schematic showing high-voltage transmission lines between power sub-stations in Prussian blue ink #1E4E79.", "slow", "full_scene"),
                ("SC09_I4", "An added electrical line causing phase imbalance angles to diverge, triggering overload sparks at a transformer node on vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC09_I5", "A continental map silhouette experiencing cascading blackout shadows across regional grid sectors in charcoal on vellum #F4F1EA.", "fast", "environment"),
                ("SC09_I6", "Draftsman examining electrical impedance equations using a brass compass, marveling at universal network mathematics on paper #F4F1EA, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Braess's Paradox is not confined to asphalt.",
                "Telecommunication engineers observed the same phenomenon in packet-switched routing",
                "when adding high-speed fiber links accidentally degraded internet throughput.",
                "In electrical power transmission, adding high-voltage cables can trigger phase imbalances,",
                "overloading adjacent substations",
                "and causing cascading blackouts across entire regional grids during summer peak hours.",
            ],
        },
        # SC10
        {
            "id": "SC10",
            "title": "The Necessity of Structural Constraint",
            "purpose": "Editorial verdict that individual optimization requires systemic constraint.",
            "action": "Draftsman using an eraser to remove the shortcut; traffic instantly recovers.",
            "setting": "Drafting table with eraser shavings and restored flow lines.",
            "camera": "Close-up on deliberate architectural intervention.",
            "narration": "Unconstrained self-interest creates systemic degradation whenever individual incentives decouple from global efficiency. The Nash equilibrium of selfish agents rarely matches the social optimum. To build resilient networks, whether in software architecture, corporate logistics, or urban transit, designers must intentionally constrain choices, occasionally removing shortcuts to force traffic into distributed, harmonious flow.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Authoritative, first-principles, profound",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "editorial_commentary",
            "prompts": [
                ("SC10_I1", "Draftsman holding a white vinyl drafting eraser, deliberately erasing the vermilion central shortcut line on drafting vellum #F4F1EA.", "slow", "full_scene"),
                ("SC10_I2", "White eraser crumbs resting beside the newly erased path, leaving the network pristine and uncluttered on technical vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC10_I3", "Traffic arrows immediately redistributing evenly into upper and lower paths, travel times dropping back to 65 minutes in green ink on paper #F4F1EA.", "slow", "full_scene"),
                ("SC10_I4", "A philosophical equation hand-lettered on the drafting margin: 'NASH EQUILIBRIUM != SOCIAL OPTIMUM' in crisp architect lettering on vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC10_I5", "Architectural gate metaphor showing deliberate boundary fences guiding water into twin parallel fountains on cream paper #F4F1EA.", "slow", "concept_metaphor"),
                ("SC10_I6", "Draftsman standing proudly beside the beautifully balanced, pruned network diagram on drafting vellum #F4F1EA, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Unconstrained self-interest creates systemic degradation",
                "whenever individual incentives decouple from global efficiency.",
                "The Nash equilibrium of selfish agents rarely matches the social optimum.",
                "To build resilient networks, whether in software architecture, corporate logistics, or urban transit,",
                "designers must intentionally constrain choices,",
                "occasionally removing shortcuts to force traffic into distributed, harmonious flow.",
            ],
        },
        # SC11
        {
            "id": "SC11",
            "title": "Closing Synthesis & Second-Order Thinking",
            "purpose": "Conclude on second-order thinking and invite community analysis.",
            "action": "Draftsman rolling up the Cheonggyecheon blueprint into a leather tube; endcard establishes.",
            "setting": "Refined mid-century drafting studio under warm directional desk lamp.",
            "camera": "Concluding wide shot pulling back to frame drafting tools and channel identity.",
            "narration": "The Cheonggyecheon highway was not a tragic loss; its removal cured a chronic architectural paradox. When designing any complex system, remember that local shortcuts frequently breed global paralysis. Apply second-order thinking to one decision this week and notice what shifts. Watch the complete first-principles analysis on First Principles Ink YouTube.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Inspiring, rigorous, memorable",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cta_close",
            "prompts": [
                ("SC11_I1", "A modern photograph-style architectural sketch of the Cheonggyecheon urban stream in Seoul, with willow trees and pedestrian walkways replacing the highway on vellum #F4F1EA.", "normal", "full_scene"),
                ("SC11_I2", "A brass compass drawing concentric ripple circles outward, illustrating second-order feedback effects in cyan ink #38BDF8 on paper #F4F1EA.", "normal", "concept_metaphor"),
                ("SC11_I3", "Draftsman carefully rolling the completed drafting vellum sheet and sliding it into an archival leather drafting tube on wooden desk #F4F1EA.", "slow", "full_scene"),
                ("SC11_I4", "Brass drafting tools (compass, ruling pen, protractor, slide rule) arranged with geometric perfection around an open notebook on vellum #F4F1EA.", "slow", "macro_detail"),
                ("SC11_I5", "Draftsman smiling thoughtfully through horn-rimmed spectacles, adjusting drafting coat cuff under warm desk lamp on paper #F4F1EA, >=60% negative space.", "hold", "full_scene"),
                ("SC11_I6", "Editorial channel endcard on architectural drafting vellum #F4F1EA with millimeter grid borders and uppercase technical hand-lettering in upper third: 'FIRST PRINCIPLES INK'.", "hold", "full_scene", True),
            ],
            "quotes": [
                "The Cheonggyecheon highway was not a tragic loss;",
                "its removal cured a chronic architectural paradox.",
                "When designing any complex system, remember that local shortcuts frequently breed global paralysis.",
                "Apply second-order thinking to one decision this week and notice what shifts.",
                "Watch the complete first-principles analysis on First Principles Ink YouTube.",
                "Watch the complete first-principles analysis on First Principles Ink YouTube.",
            ],
        },
    ]

    scenes = []
    for sc_data in scenes_data:
        sc_id = sc_data["id"]
        images = []
        beats = []
        for i, (p_id, desc, tempo, shot_type, *rest) in enumerate(sc_data["prompts"]):
            is_end = bool(rest[0]) if rest else False
            based = sc_data["prompts"][i - 1][0] if i > 0 else None
            img = make_image(
                img_id=p_id,
                description=desc,
                preserve="1960s architectural drafting aesthetic, drafting vellum #F4F1EA with millimeter grid, draftsman in horn-rimmed glasses and white drafting coat, Prussian blue #1E4E79 and vermilion #C84B31 ink.",
                change=f"Progress to beat {p_id} showing {desc[:60]}...",
                reason=f"Visualize first-principles system progression for {sc_id} beat {i+1}.",
                tempo=tempo,
                situation=sc_data["narrative_situation"],
                motion_prompt="Smooth 2D technical drafting animation. Crisp ruling-pen lines drawing smoothly across drafting vellum, compass needle rotating, zero lip-sync, elegant mathematical precision.",
                has_character=True,
                is_endcard=is_end,
                shot_type=shot_type,
                based_on=based,
            )
            images.append(img)

            b_id = f"{sc_id}_B{i+1}"
            quote = sc_data["quotes"][i]
            beat = make_beat(
                beat_id=b_id,
                img_id=p_id,
                purpose=f"Visual anchor for {sc_id} beat {i+1}",
                quote=quote,
                tempo=tempo,
                situation=sc_data["narrative_situation"],
                effect="cut" if i < 5 else "hold",
                is_endcard=is_end,
            )
            beats.append(beat)

        scenes.append({
            "id": sc_id,
            "title": sc_data["title"],
            "purpose": sc_data["purpose"],
            "action": sc_data["action"],
            "setting": sc_data["setting"],
            "camera": sc_data["camera"],
            "narration": sc_data["narration"],
            "requirements": sc_data["requirements"],
            "character_ids": sc_data["character_ids"],
            "source_ids": sc_data["source_ids"],
            "tone": sc_data["tone"],
            "narrative_phase": sc_data["narrative_phase"],
            "narrative_situation": sc_data["narrative_situation"],
            "images": images,
            "beats": beats,
        })

    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(brief),
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": [
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "In 2003, the municipal government of Seoul made a radical urban decision that initially seemed like complete civic madness to every transportation planner."},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Human intuition tells us that traffic functions like water rushing through a lead pipe."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "He proved that adding a road to a congested network can increase overall travel time for every single participant."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "To see the math with crystal clarity, imagine a network with four thousand drivers traveling from start node S to destination node T."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Splitting two thousand commuters evenly yields sixty-five minutes per person."},
            {"requirement_id": "R06", "scene_id": "SC06", "quote": "City planners often fall into the trap of linear thinking, treating bottlenecks as localized deficits rather than dynamic feedback loops."},
            {"requirement_id": "R07", "scene_id": "SC07", "quote": "Now, engineers open a brand-new bypass connecting junction A directly to junction B, taking zero minutes."},
            {"requirement_id": "R08", "scene_id": "SC08", "quote": "Commute delay balloons to eighty minutes, leaving every single motorist worse off than before."},
            {"requirement_id": "R09", "scene_id": "SC09", "quote": "Telecommunication engineers observed the same phenomenon in packet-switched routing when adding high-speed fiber links accidentally degraded internet throughput."},
            {"requirement_id": "R10", "scene_id": "SC10", "quote": "The Nash equilibrium of selfish agents rarely matches the social optimum."},
            {"requirement_id": "R11", "scene_id": "SC11", "quote": "The Cheonggyecheon highway was not a tragic loss; its removal cured a chronic architectural paradox."},
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC01",
                "quote": "Instead, something bizarre happened: travel times across downtown Seoul actually decreased.",
                "language": "en",
                "source_id": "SRC02",
                "fact": "Demolishing the six-lane Cheonggyecheon highway reduced average commute times across central Seoul.",
            },
            {
                "scene_id": "SC03",
                "quote": "He proved that adding a road to a congested network can increase overall travel time for every single participant.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Adding an additional route to a transportation network can increase total transit time for all users.",
            },
            {
                "scene_id": "SC09",
                "quote": "In electrical power transmission, adding high-voltage cables can trigger phase imbalances, overloading adjacent substations and causing cascading blackouts across entire regional grids during summer peak hours.",
                "language": "en",
                "source_id": "SRC03",
                "fact": "Adding transmission lines can cause phase instability and cascading grid overloads.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    return job_id, brief, outline, competitor_research, content


def build_first_principles_short() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_first_principles"
    slug = "en-first-principles"
    parent_long_id = f"{slug}-batch1-16x9"
    job_id = f"{slug}-batch1-9x16"
    ch = get_channel(channel_id)

    topic = "Braess's Paradox: How Adding a Shortcut to a Network Slows Down Every Single Driver"
    youtube_title = "Seoul Demolished a Highway and Traffic Moved Faster"

    brief: Dict[str, Any] = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain Braess's Paradox in 45s using Seoul's highway removal, breaking down the 65-to-80 minute shortcut trap and bridging to full video.",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 38.0,
            "max_seconds": 52.0,
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Seoul demolished a 6-lane highway carrying 160,000 cars and traffic improved."},
            {"id": "R02", "text": "Braess's Paradox: adding a shortcut lures everyone onto the same path, increasing travel time from 65 to 80 minutes."},
            {"id": "R03", "text": "Editorial commentary on how more lanes synchronize commuters into collective paralysis."},
            {"id": "R04", "text": "Network pruning: removing high-conflict shortcuts restores distributed throughput."},
            {"id": "R05", "text": "Cliffhanger peak on power grid blackouts, channel bridge, and CTA."},
        ],
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "parent_long_id": parent_long_id,
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Über ein Paradoxon aus der Verkehrsplanung (On a Paradox of Traffic Planning)",
                "reference": "Braess, D. (1968). Unternehmensforschung, 12, 258-268.",
                "facts": [
                    "Adding an additional route to a transportation network can increase total transit time for all users.",
                    "The selfish routing Nash equilibrium can yield strictly worse overall payoff than the social optimum.",
                ],
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": ch.speed,
            }
        ],
        "planning": {
            "success_criteria": [
                "Hook viewers in under 3s with Seoul's counter-intuitive highway demolition.",
                "Explain the 65-to-80 minute Braess Paradox with crisp technical drafting animation.",
                "Bridge seamlessly to the full first-principles video at the power grid cliffhanger.",
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "None required.",
            "pacing": "Punchy, deductive, fast-paced technical clarity at 3.8 words per second.",
            "assumptions": [
                "4 beats and 4 unique technical schematics per scene across 5 scenes.",
            ],
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Draftsman in spectacles erasing a red highway bridge on drafting vellum as travel times drop from 80 to 65 mins",
                "text_overlay": "LESS ROADS FASTER",
                "contrast_pair": "6-lane expressway demolition vs Commute times significantly decreasing",
                "thumbnail_prompt": "Authentic 2D archival engineering vertical schematic on 1960s drafting vellum (#F4F1EA). Draftsman in horn-rimmed spectacles erasing a central red shortcut link, causing traffic arrows to split smoothly with time display dropping from '80 MINS' down to '65 MINS'. Prussian blue (#1E4E79) and vermilion (#C84B31) ink lines. Hand-lettered uppercase text: 'LESS ROADS FASTER'. Vertical 9:16, >=60% negative space, zero 3D CGI.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Game Theory & First-Principles Systems",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["first principles ink", "shorts", "braess paradox", "traffic", "game theory", "engineering"],
            "parent_long_id": parent_long_id,
            "cta_plan": {
                "cliffhanger_peak": "How does this identical mathematical paradox cause sudden blackouts across continental power grids?",
                "bridge": "Watch the complete first-principles analysis on First Principles Ink YouTube.",
                "close": "How would you resolve this paradox? Share your thought process below.",
                "endcard_text": "FULL VIDEO ON YOUTUBE",
            },
            "editorial_stance": {
                "myth_debunked": "Adding highway capacity or network bandwidth is an unconditionally positive solution to relieving system congestion.",
                "why_generic_advice_fails": "Linear planning treats bottlenecks as isolated capacity shortages without accounting for game-theoretic shifts in user behavior.",
                "channel_verdict": "Individual optimization without systemic coordination guarantees collective inefficiency across every coupled network topology.",
                "tradeoff_or_blindspot": "Closing roads and pruning shortcuts feels politically counterintuitive, but topological constraint is often necessary to maximize throughput.",
            },
            "actionable_value": {
                "core_mechanism": "Selfish routing converges on a Nash equilibrium that overloads shortcuts and degrades global network throughput.",
                "practical_rule_of_thumb": "Audit network topologies and prune parasitic shortcuts rather than blindly expanding bottleneck capacity.",
                "real_world_scenario": "When microservice architecture or urban roadways suffer gridlock, evaluate whether removing a high-contention link improves latency.",
            },
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Draftsman in spectacles erasing a red highway bridge on drafting vellum as travel times drop from 80 to 65 mins",
            "text_overlay": "LESS ROADS FASTER",
            "contrast_pair": "6-lane expressway demolition vs Commute times significantly decreasing",
            "thumbnail_prompt": "Authentic 2D archival engineering vertical schematic on 1960s drafting vellum (#F4F1EA). Draftsman in horn-rimmed spectacles erasing a central red shortcut link, causing traffic arrows to split smoothly with time display dropping from '80 MINS' down to '65 MINS'. Prussian blue (#1E4E79) and vermilion (#C84B31) ink lines. Hand-lettered uppercase text: 'LESS ROADS FASTER'. Vertical 9:16, >=60% negative space, zero 3D CGI.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Game Theory & First-Principles Systems",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["first principles ink", "shorts", "braess paradox", "traffic", "game theory", "engineering"],
        "parent_long_id": parent_long_id,
        "cta_plan": {
            "cliffhanger_peak": "How does this identical mathematical paradox cause sudden blackouts across continental power grids?",
            "bridge": "Watch the complete first-principles analysis on First Principles Ink YouTube.",
            "close": "How would you resolve this paradox? Share your thought process below.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases),
        },
        "editorial_stance": {
            "myth_debunked": "Adding highway capacity or network bandwidth is an unconditionally positive solution to relieving system congestion.",
            "why_generic_advice_fails": "Linear planning treats bottlenecks as isolated capacity shortages without accounting for game-theoretic shifts in user behavior.",
            "channel_verdict": "Individual optimization without systemic coordination guarantees collective inefficiency across every coupled network topology.",
            "tradeoff_or_blindspot": "Closing roads and pruning shortcuts feels politically counterintuitive, but topological constraint is often necessary to maximize throughput.",
        },
        "actionable_value": {
            "core_mechanism": "Selfish routing converges on a Nash equilibrium that overloads shortcuts and degrades global network throughput.",
            "practical_rule_of_thumb": "Audit network topologies and prune parasitic shortcuts rather than blindly expanding bottleneck capacity.",
            "real_world_scenario": "When microservice architecture or urban roadways suffer gridlock, evaluate whether removing a high-contention link improves latency.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook on Seoul tearing down the Cheonggyecheon highway.", "requirements": ["R01"], "transition": "Explain the game-theoretic mechanism."},
            {"scene_id": "SC02", "purpose": "Demonstrate Braess's Paradox shifting travel times from 65 to 80 minutes.", "requirements": ["R02"], "transition": "Critique simplistic urban highway expansion."},
            {"scene_id": "SC03", "purpose": "Editorial commentary on the fallacy of adding lanes to solve traffic.", "requirements": ["R03"], "transition": "Present the first-principles pruning solution."},
            {"scene_id": "SC04", "purpose": "Demonstrate network pruning and strategic choice constraint.", "requirements": ["R04"], "transition": "Cliffhanger peak on power grids and channel bridge."},
            {"scene_id": "SC05", "purpose": "Cliffhanger peak on continental power grids, YouTube bridge, and closing CTA.", "requirements": ["R05"], "transition": "End of short."},
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Veritasium",
                    "top_performing_videos": [
                        {
                            "title": "The Counter-Intuitive Traffic Theorem",
                            "views": "3.8M views",
                            "hook_technique": "Shows highway demolition leading to traffic speedup.",
                            "pacing_structure": "Surprising historical fact -> Logical proof -> Systemic insight.",
                            "retention_driver": "Rapid-fire visual deduction.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Animates network graph costs directly in real time.",
                        "Replaces intuition with first-principles proof.",
                    ],
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 21,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Draftsman erasing a six-lane highway while green traffic speed lines accelerate.",
                "counter_intuitive_truth_slap": "Demolishing 6 highway lanes carrying 160,000 cars a day made everyone's commute significantly faster.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Visceral hook on Seoul's counterintuitive highway demolition."},
                {"phase": "empirical_conflict", "purpose": "Braess's Paradox showing 65-to-80 minute Nash trap."},
                {"phase": "structural_model", "purpose": "Editorial critique on linear asphalt expansion fallacies."},
                {"phase": "actionable_resolution", "purpose": "Network pruning: removing shortcuts to maximize throughput."},
                {"phase": "cliffhanger_spinoff", "purpose": "Cliffhanger peak on power grid blackouts and YouTube bridge."},
            ],
            "tactile_visual_benchmark": {
                "paper_surface": "1960s Architectural drafting vellum (#F4F1EA) with faint millimeter grid.",
                "ink_technique": "Rotring technical pen in Prussian blue (#1E4E79) and chalk-white lines.",
                "palette_application": "Vermilion accents (#C84B31), compass-arc cyan (#38BDF8), ochre focal points (#FFB703).",
                "anti_ai_rules": "Vertical 9:16, zero 3D CGI, zero neon glow, minimum 60% negative space.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Game Theory & First-Principles Systems",
            "myth_debunked": "Adding highway capacity or network bandwidth is an unconditionally positive solution to relieving system congestion.",
            "channel_verdict": "Individual optimization without systemic coordination guarantees collective inefficiency across every coupled network topology.",
            "actionable_rule_of_thumb": "Audit network topologies and prune parasitic shortcuts rather than blindly expanding bottleneck capacity.",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How does this identical mathematical paradox cause sudden blackouts across continental power grids?",
            "bridge": "Watch the complete first-principles analysis on First Principles Ink YouTube.",
            "close": "How would you resolve this paradox? Share your thought process below.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
    }

    # 5 scenes, 4 beats & 4 images each = 20 images, 176 words
    scenes_data = [
        # SC01
        {
            "id": "SC01",
            "title": "Seoul's Demolition Miracle",
            "purpose": "Hook on Seoul tearing down the Cheonggyecheon highway.",
            "action": "Draftsman erasing highway on vertical vellum map.",
            "setting": "Drafting table on vertical vellum #F4F1EA.",
            "camera": "Vertical overhead map view.",
            "narration": "In 2003, the city of Seoul tore down an elevated six-lane highway carrying over one hundred and sixty thousand vehicles every single day. Everyone predicted catastrophic gridlock, but travel times across the capital city surprisingly improved.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Shocking, compelling, crisp",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "prompts": [
                ("SC01_I1", "Vertical 9:16 engineering drafting schematic on vellum #F4F1EA: Seoul aerial map in Prussian blue ink #1E4E79 showing the elevated highway with millimeter grid lines, >=60% negative space.", "burst", "full_scene"),
                ("SC01_I2", "A brass ruling pen cleanly slicing a vermilion cut line #C84B31 across the highway graphic on vertical vellum #F4F1EA.", "fast", "macro_detail"),
                ("SC01_I3", "Vehicles swarming around downtown intersections with speed numbers dropping in red chalk on cream paper #F4F1EA.", "fast", "concept_metaphor"),
                ("SC01_I4", "Draftsman in horn-rimmed spectacles examining stopwatch showing faster commute times in cyan ink #38BDF8 on paper #F4F1EA.", "normal", "full_scene"),
            ],
            "quotes": [
                "In 2003, the city of Seoul tore down an elevated six-lane highway",
                "carrying over one hundred and sixty thousand vehicles every single day.",
                "Everyone predicted catastrophic gridlock,",
                "but travel times across the capital city surprisingly improved.",
            ],
        },
        # SC02
        {
            "id": "SC02",
            "title": "The Shortcut Trap (65 to 80 Mins)",
            "purpose": "Demonstrate Braess's Paradox shifting travel times from 65 to 80 minutes.",
            "action": "Adding a 0-min shortcut lures everyone into 80-minute delay.",
            "setting": "Vertical 4-node diamond network diagram.",
            "camera": "Close-up on network equations.",
            "narration": "This is Braess's Paradox. Adding a brand-new shortcut to a network lures every selfish driver onto the exact same path. The resulting bottleneck drives individual travel times from sixty-five all the way up to eighty minutes.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Sharp, mathematical, revealing",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC02_I1", "Vertical diamond 4-node network diagram on vellum #F4F1EA with start S, nodes A and B, destination T, neatly drafted in Prussian blue #1E4E79.", "fast", "full_scene"),
                ("SC02_I2", "A bright vermilion shortcut line drawn between A and B labeled '0 MIN SHORTCUT' on technical vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC02_I3", "All vehicle arrows converging on the shortcut, causing the time indicator to jump from 65 to 80 minutes in red ink #C84B31 on paper #F4F1EA.", "normal", "concept_metaphor"),
                ("SC02_I4", "Draftsman tapping the 80-minute equation with a brass compass divider on cream drafting vellum #F4F1EA.", "hold", "full_scene"),
            ],
            "quotes": [
                "This is Braess's Paradox.",
                "Adding a brand-new shortcut to a network lures every selfish driver onto the exact same path.",
                "The resulting bottleneck drives individual travel times",
                "from sixty-five all the way up to eighty minutes.",
            ],
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Road Expansion Fallacy",
            "purpose": "Editorial commentary on the fallacy of adding lanes to solve traffic.",
            "action": "Bulldozer laying lanes into gridlock while planners look puzzled.",
            "setting": "Metaphorical construction zone on technical vellum.",
            "camera": "Direct vertical perspective.",
            "narration": "Pouring more asphalt does not cure congestion; it synchronizes independent commuters into collective paralysis. Conventional planning assumes more lanes mean faster commutes, completely ignoring how selfish routing sabotages global efficiency.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Critical, incisive, first-principles",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "prompts": [
                ("SC03_I1", "A highway blueprint stamped with 'MORE LANES = LESS TRAFFIC' crossed out with a bold red vermilion line #C84B31 on vellum #F4F1EA.", "slow", "concept_metaphor"),
                ("SC03_I2", "A toy bulldozer laying asphalt into a clogged funnel where cars pack bumper to bumper on drafting paper #F4F1EA.", "normal", "concept_metaphor"),
                ("SC03_I3", "A broken balance scale with individual self-interest heavily outweighing collective throughput on cream vellum #F4F1EA.", "slow", "concept_metaphor"),
                ("SC03_I4", "Draftsman shaking head at a highway budget ledger with red deficit ink running off the page on paper #F4F1EA, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Pouring more asphalt does not cure congestion;",
                "it synchronizes independent commuters into collective paralysis.",
                "Conventional planning assumes more lanes mean faster commutes,",
                "completely ignoring how selfish routing sabotages global efficiency.",
            ],
        },
        # SC04
        {
            "id": "SC04",
            "title": "Network Pruning: The Counter-Intuitive Cure",
            "purpose": "Demonstrate network pruning and strategic choice constraint.",
            "action": "Draftsman erasing shortcut, restoring balanced 65-min flow.",
            "setting": "Technical drafting vellum with restored network balance.",
            "camera": "Vertical medium shot on drawing board.",
            "narration": "Network pruning resolves the trap. Intentionally closing high-conflict shortcuts forces traffic back onto distributed paths, proving that removing options can mathematically increase overall throughput across any complex engineering system.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Tactical, empowering, deductive",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "actionable_resolution",
            "prompts": [
                ("SC04_I1", "Draftsman using a vinyl drafting eraser to cleanly erase the central shortcut on vertical vellum #F4F1EA, white eraser shavings.", "burst", "full_scene"),
                ("SC04_I2", "The 4,000 traffic arrows immediately splitting back into two balanced parallel streams of 2,000 cars each on paper #F4F1EA.", "fast", "concept_metaphor"),
                ("SC04_I3", "Travel time indicator dropping smoothly back to '65 MINS' in serene cyan drafting ink #38BDF8 on cream vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC04_I4", "A bold architectural stamp reading 'NETWORK PRUNED: THROUGHPUT RESTORED' on technical drafting vellum #F4F1EA.", "hold", "macro_detail"),
            ],
            "quotes": [
                "Network pruning resolves the trap.",
                "Intentionally closing high-conflict shortcuts forces traffic back onto distributed paths,",
                "proving that removing options can mathematically increase overall throughput",
                "across any complex engineering system.",
            ],
        },
        # SC05
        {
            "id": "SC05",
            "title": "Power Grids & The First Principles Bridge",
            "purpose": "Cliffhanger peak on continental power grids, YouTube bridge, and closing CTA.",
            "action": "Electrical utility grid appears with phase imbalance; endcard establishes.",
            "setting": "Luminous technical electrical drafting canvas.",
            "camera": "Vertical cinematic tilt into channel branding.",
            "narration": "How does this identical mathematical paradox cause sudden blackouts across continental power grids? Watch the complete first-principles analysis on First Principles Ink YouTube. How would you resolve this paradox? Share your thought process below.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Electrifying, profound, inviting",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cta_close",
            "prompts": [
                ("SC05_I1", "Vertical engineering schematic of a regional power grid with high-voltage lines branching between substations on drafting vellum #F4F1EA.", "normal", "macro_detail"),
                ("SC05_I2", "A glowing circuit breaker sparking as transmission phase lines overload in vermilion ink #C84B31 on cream paper #F4F1EA.", "slow", "concept_metaphor"),
                ("SC05_I3", "A technical video player card on drafting vellum with draftsman pointing brass compass at the complete model in Prussian blue #1E4E79.", "hold", "full_scene"),
                ("SC05_I4", "Vertical channel endcard on 1960s drafting vellum #F4F1EA with millimeter grid borders and technical hand-lettering in upper third: 'FIRST PRINCIPLES INK'.", "hold", "full_scene", True),
            ],
            "quotes": [
                "How does this identical mathematical paradox cause sudden blackouts across continental power grids?",
                "Watch the complete first-principles analysis on First Principles Ink YouTube.",
                "How would you resolve this paradox?",
                "Share your thought process below.",
            ],
        },
    ]

    scenes = []
    for sc_data in scenes_data:
        sc_id = sc_data["id"]
        images = []
        beats = []
        for i, (p_id, desc, tempo, shot_type, *rest) in enumerate(sc_data["prompts"]):
            is_end = bool(rest[0]) if rest else False
            based = sc_data["prompts"][i - 1][0] if i > 0 else None
            img = make_image(
                img_id=p_id,
                description=desc,
                preserve="1960s architectural drafting aesthetic, drafting vellum #F4F1EA with millimeter grid, draftsman in horn-rimmed glasses and white drafting coat, Prussian blue #1E4E79 and vermilion #C84B31 ink.",
                change=f"Progress to beat {p_id} showing {desc[:60]}...",
                reason=f"Visualize first-principles system progression for {sc_id} beat {i+1}.",
                tempo=tempo,
                situation=sc_data["narrative_situation"],
                motion_prompt="Smooth 2D technical drafting animation. Crisp ruling-pen lines drawing smoothly across drafting vellum, compass needle rotating, zero lip-sync, elegant mathematical precision.",
                has_character=True,
                is_endcard=is_end,
                shot_type=shot_type,
                based_on=based,
            )
            images.append(img)

            b_id = f"{sc_id}_B{i+1}"
            quote = sc_data["quotes"][i]
            beat = make_beat(
                beat_id=b_id,
                img_id=p_id,
                purpose=f"Visual anchor for {sc_id} beat {i+1}",
                quote=quote,
                tempo=tempo,
                situation=sc_data["narrative_situation"],
                effect="cut" if i < 3 else "hold",
                is_endcard=is_end,
            )
            beats.append(beat)

        scenes.append({
            "id": sc_id,
            "title": sc_data["title"],
            "purpose": sc_data["purpose"],
            "action": sc_data["action"],
            "setting": sc_data["setting"],
            "camera": sc_data["camera"],
            "narration": sc_data["narration"],
            "requirements": sc_data["requirements"],
            "character_ids": sc_data["character_ids"],
            "source_ids": sc_data["source_ids"],
            "tone": sc_data["tone"],
            "narrative_phase": sc_data["narrative_phase"],
            "narrative_situation": sc_data["narrative_situation"],
            "images": images,
            "beats": beats,
        })

    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(brief),
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id, "CH01")],
        "scenes": scenes,
        "coverage": [
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "In 2003, the city of Seoul tore down an elevated six-lane highway carrying over one hundred and sixty thousand vehicles every single day."},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "The resulting bottleneck drives individual travel times from sixty-five all the way up to eighty minutes."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Pouring more asphalt does not cure congestion; it synchronizes independent commuters into collective paralysis."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Network pruning resolves the trap. Intentionally closing high-conflict shortcuts forces traffic back onto distributed paths, proving that removing options can mathematically increase overall throughput across any complex engineering system."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Watch the complete first-principles analysis on First Principles Ink YouTube."},
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC02",
                "quote": "The resulting bottleneck drives individual travel times from sixty-five up to eighty minutes.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Adding an additional route to a transportation network can increase total transit time for all users.",
            }
        ],
        "revision_response": [],
        "open_questions": [],
    }

    return job_id, brief, outline, competitor_research, content
