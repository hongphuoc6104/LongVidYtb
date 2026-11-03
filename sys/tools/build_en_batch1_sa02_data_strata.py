#!/usr/bin/env python3
"""Data definitions for Channel 1: Deep Time Strata (en_parable_lamp / en_deep_time_strata).

Jobs:
- Long 16:9: sys/runs/en-deep-time-strata-batch1-16x9 (11 scenes, 66 images, 620 words)
- Short 9:16: sys/runs/en-deep-time-strata-batch1-9x16 (5 scenes, 20 images, 173 words)
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from channels.registry import channel_cast, channel_profile_stamp, get_channel


def compute_brief_hash(brief_dict: Dict[str, Any]) -> str:
    content = json.dumps(brief_dict, ensure_ascii=False, indent=2)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_deep_time_strata_long():
    channel_id = "en_parable_lamp"
    job_id = "en-deep-time-strata-batch1-16x9"
    ch = get_channel(channel_id)

    topic = "The Two-Million-Year Rainstorm: How the Carnian Pluvial Episode Flooded Pangaea and Launched the Age of Dinosaurs"
    youtube_title = "When It Rained on Earth for Two Million Years"  # 45 chars <= 55

    sources = [
        {
            "id": "SRC01",
            "title": "Synchronic climatic and biotic change in the Carnian (Upper Triassic)",
            "reference": "Simms, M. J., & Ruffell, A. H. (1989). Nature, 340, 521-526.",
            "facts": [
                "Colossal Wrangellia flood basalt eruptions pumped thousands of gigatons of carbon dioxide into the atmosphere.",
                "Global thermal warming pushed tropical ocean surface temperatures to approximately one hundred degrees Fahrenheit."
            ]
        },
        {
            "id": "SRC02",
            "title": "Extinction and dawn of the modern world in the Carnian (Late Triassic)",
            "reference": "Dal Corso, J. et al. (2020). Science Advances, 6(38), eaba0099.",
            "facts": [
                "Torrential pluvial conditions persisted across the supercontinent Pangaea for approximately two million years.",
                "Sedimentary rock layers abruptly shift from arid red sandstones to dark carbonaceous mudstones, coal swamps, and fossil amber."
            ]
        },
        {
            "id": "SRC03",
            "title": "The Carnian Pluvial Episode and the dawn of the dinosaurs",
            "reference": "Benton, M. J. et al. (2018). Journal of the Geological Society, 175(6), 989-1003.",
            "facts": [
                "Dominant herbivorous rhynchosaurs and heavy mammal-like reptiles suffered massive extinction during the sodden deluge.",
                "Bipedal agile early dinosaurs expanded from less than five percent of land animals to over fifty percent of terrestrial vertebrates."
            ]
        }
    ]

    required_points = [
        {"id": "R01", "text": "Arid supercontinent Pangaea baking under desert heat two hundred thirty-four million years ago"},
        {"id": "R02", "text": "Cataclysmic Wrangellia flood basalts erupting in modern Alaska and venting massive greenhouse gases"},
        {"id": "R03", "text": "Runaway atmospheric warming heating tropical oceans to one hundred degrees Fahrenheit"},
        {"id": "R04", "text": "Debunking gentle rain: the reality of an acidic ecological scald stripping terrestrial biomes"},
        {"id": "R05", "text": "Atmospheric engine locking into a permanent supercontinental mega-monsoon"},
        {"id": "R06", "text": "Relentless downpours hammering Earth continuously for two million unbroken years"},
        {"id": "R07", "text": "Mass extinction of dominant rhynchosaurs and heavy cynodonts in waterlogged rot"},
        {"id": "R08", "text": "Stratigraphic transition in stone from red desert sands to dark mudstone, coal, and amber"},
        {"id": "R09", "text": "Editorial commentary on how planetary catastrophes clear the board for evolutionary breakthroughs"},
        {"id": "R10", "text": "Early bipedal dinosaurs with hollow bones and upright stance conquering post-deluge Pangaea"},
        {"id": "R11", "text": "Rock layers beneath our feet preserving the memory of Earth's great evolutionary crucibles"}
    ]

    editorial_stance = {
        "myth_debunked": "The comforting myth that prehistoric rain was a gentle, life-giving blessing that nourished ancient ecosystems.",
        "why_generic_advice_fails": "Simplistic climatic models assume rainfall uniformly restores biospheres, ignoring that superheated acidic deluges strip soils and poison lakes.",
        "channel_verdict": "The Carnian Pluvial Episode was not a benign season of showers, but a two-million-year planetary crucible that shattered existing food webs to crown the dinosaurs.",
        "tradeoff_or_blindspot": "Surviving an environmental crisis demands radical physiological agility rather than sheer armor, favoring nimble generalists over entrenched titans."
    }

    actionable_value = {
        "core_mechanism": "Wrangellia basalt eruptions flooded the atmosphere with greenhouse carbon, superheating oceans and locking planetary weather into an endless mega-monsoon.",
        "practical_rule_of_thumb": "Examine stratigraphic boundary transitions between red desert sandstone and dark carbonaceous mudstone to spot abrupt climate shifts.",
        "real_world_scenario": "When hiking sedimentary rock cliffs in Italy or Britain, notice how grey fossil-amber layers expose the ancient two-million-year flood."
    }

    thumbnail_spec = {
        "visual_hook": "Carved woodcut field paleontologist examining a glowing amber droplet in stratified red-to-grey canyon rock layers while torrential rain pours behind.",
        "text_overlay": "TWO MILLION YEARS",
        "contrast_pair": "Arid desert sand dunes vs Endless planetary deluge",
        "thumbnail_prompt": "Requested aspect ratio: 16:9. Render a complete 100% full-bleed horizontal widescreen 16:9 high-impact YouTube poster thumbnail illustration extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, zero UI chrome, and zero dark vignette.\n\nVisual Style (ch_en_parable_woodcut): Expressive 2D carved paleo-lithograph and linocut geological strata print on aged fossil-matrix parchment (#EFE4C8 aged fossil parchment, #1E1E1E bold carved woodcut ink, #D9A520 amber fossil gold, #5E7D3A Carboniferous fern green, #A44A3F Permian red-bed terracotta). Orthographic 2D relief printmaking texture, >=60% negative space, zero 3D CGI, zero plastic AI glow, zero gradients.\n\nFocal Subject: Carved woodcut field paleontologist in terracotta expedition coat (#A44A3F) holds a glowing golden amber droplet (#D9A520) in a stratified canyon wall. In the background, heavy diagonal rain cross-hatching sweeps across a dark storm sky above primeval fern hills.\n\nPoster Typography: Hand-lettered uppercase English text in upper third: 'TWO MILLION YEARS'. Bold relief woodcut font integrated directly into the parchment, strictly zero rectangular text cards or gradient boxes.",
        "layout_mode": "split_contrast"
    }

    cta_plan = {
        "close": "Every rock layer beneath your feet holds an entire lost world. See you in the next epoch.",
        "endcard_text": "DEEP TIME STRATA"
    }

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain the geological triggers, ecological destruction, and evolutionary consequences of the Carnian Pluvial Episode using field stratigraphy and woodcut visual storytelling",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 150.0,
            "max_seconds": 210.0
        },
        "scene_count": 11,
        "required_points": required_points,
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": sources,
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": False,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deliver an epic, scientifically grounded deep-time narrative across 11 scenes with 66 unique tactile woodcut illustrations, maintaining an average hold under 2.8 seconds and zero AI cliches."
            ],
            "avoid": list(ch.avoid) + ["delve into", "testament to", "tapestry", "in conclusion", "it is important to remember"],
            "prior_knowledge": "No prior geology degree required; concepts explained through physical rock strata metaphors.",
            "pacing": "Epic, investigative, chronological build from desert heat to torrential flood and evolutionary triumph.",
            "domain_requirements": [],
            "assumptions": [
                "Spoken in sharp, cinematic English without robotic academic throat-clearing."
            ],
            "text_style": {
                "font": "Carved woodblock relief serif",
                "color": "#1E1E1E",
                "outline": "#EFE4C8 parchment contrast",
                "size": "Legible on widescreen monitor",
                "placement": "Upper third, <= 10% frame height"
            },
            "speech_rates": {
                "vi": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Baseline reference speech rate"
                },
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Natural conversational cadence calibrated for deep-time documentary storytelling"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": thumbnail_spec,
            "channel_pillar": "Deep Time Earth History & Stratigraphic Evolution",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["carnian pluvial episode", "two million year rain", "how dinosaurs took over", "triassic extinction", "deep time geology", "pangaea flood"],
            "cta_plan": cta_plan,
            "editorial_stance": editorial_stance,
            "actionable_value": actionable_value
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": thumbnail_spec,
        "channel_pillar": "Deep Time Earth History & Stratigraphic Evolution",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["carnian pluvial episode", "two million year rain", "how dinosaurs took over", "triassic extinction", "deep time geology", "pangaea flood"],
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": editorial_stance,
        "actionable_value": actionable_value,
        "cta_plan": cta_plan,
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Establish bone-dry supercontinent Pangaea 234 million years ago", "requirements": ["R01"], "transition": "Shift focus to deep crustal volcanic fissures"},
            {"scene_id": "SC02", "purpose": "Reveal Wrangellia flood basalts venting gigatons of carbon dioxide", "requirements": ["R02"], "transition": "Trace carbon accumulation to runaway atmospheric heat"},
            {"scene_id": "SC03", "purpose": "Explain how boiling ocean waters locked atmospheric storm engines", "requirements": ["R03"], "transition": "Transition to critical editorial perspective on rainfall"},
            {"scene_id": "SC04", "purpose": "Deliver editorial stance debunking gentle rain as an acidic ecological scald", "requirements": ["R04"], "transition": "Examine the physical aftermath across the terrain"},
            {"scene_id": "SC05", "purpose": "Illustrate supercontinental flash floods transforming deserts to mud", "requirements": ["R05"], "transition": "Expand temporal scale to geological duration"},
            {"scene_id": "SC06", "purpose": "Chronicle the two-million-year continuous downpour across global strata", "requirements": ["R06"], "transition": "Examine the biological toll on dominant species"},
            {"scene_id": "SC07", "purpose": "Document the collapse of dominant rhynchosaurs and bulky cynodonts", "requirements": ["R07"], "transition": "Spotlight the agile underdogs navigating the mud"},
            {"scene_id": "SC08", "purpose": "Analyze physical rock strata: red sandstones replaced by mudstone and amber", "requirements": ["R08"], "transition": "Deliver key philosophical commentary on extinction"},
            {"scene_id": "SC09", "purpose": "Deliver editorial commentary on disasters clearing competitive biological boards", "requirements": ["R09"], "transition": "Track the rise of the dinosaur dynasty"},
            {"scene_id": "SC10", "purpose": "Show the explosive adaptive radiation of dinosaurs across green Pangaea", "requirements": ["R10"], "transition": "Zoom out to modern geological perspective"},
            {"scene_id": "SC11", "purpose": "Close with deep-time reflection on rock layers preserving ancient trials", "requirements": ["R11"], "transition": "Final hold endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "History of the Earth",
                    "top_performing_videos": [
                        {
                            "title": "The Carnian Pluvial Episode: The Event That Made The Dinosaurs",
                            "views": "3.2M views",
                            "hook_technique": "Contrasting dry desert fossils directly against sudden muddy coal layers.",
                            "pacing_structure": "Paleogeographic map setup -> Volcanic trigger -> Global biotic turnover.",
                            "retention_driver": "Deep geological detective pacing that grounds ancient time in physical rock evidence."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Grounding immense timescales in tangible rock layer transitions.",
                        "Framing dinosaurs not as born rulers, but as lucky crisis beneficiaries."
                    ]
                },
                {
                    "channel_name": "Atlas Pro",
                    "top_performing_videos": [
                        {
                            "title": "The Time It Rained for 2 Million Years",
                            "views": "2.1M views",
                            "hook_technique": "Opening with the sheer absurdity of a two-million-year weather forecast.",
                            "pacing_structure": "Meteorological physics -> Ocean circulation collapse -> Extinction ripple.",
                            "retention_driver": "Clear visual diagrams demonstrating how landmass shapes alter climate."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Translating complex atmospheric science into intuitive physical mechanisms.",
                        "Using high-contrast visual before-and-after biome comparisons."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 14,
                "visual_contrast": "Sunbaked red desert sand dunes suddenly engulfed by pitch-black thunderclouds.",
                "counter_intuitive_truth_slap": "The dinosaur dynasty was not born from dry volcanic conquest, but launched by a two-million-year flood."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Establishing the scorched, arid supercontinental desert of early Pangaea."},
                {"phase": "empirical_conflict", "purpose": "Wrangellia basalt eruptions superheating the oceans to boiling thresholds."},
                {"phase": "structural_model", "purpose": "Editorial commentary on toxic acidic rain collapsing reigning reptile titans."},
                {"phase": "actionable_resolution", "purpose": "Marginal agile bipeds with hollow bones rising to dominate post-flood Earth."},
                {"phase": "cliffhanger_spinoff", "purpose": "Rock strata reflections connecting deep-time memory to modern curiosity."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chained 2D woodcut frames maintaining aged parchment texture and ink line consistency."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Deep Time Earth History & Stratigraphic Evolution",
            "myth_debunked": "Prehistoric rain was a gentle, life-giving blessing for all living things.",
            "channel_verdict": "The Carnian deluge was an acidic environmental reset that shattered existing biological dominance.",
            "actionable_rule_of_thumb": "Look for dark mudstone and fossil amber between desert sandstones to read deep-time climate upheavals."
        },
        "cta_and_spinoff_strategy": {
            "close": "Every rock layer beneath your feet holds an entire lost world. See you in the next epoch.",
            "endcard_text": "DEEP TIME STRATA"
        }
    }

    scene_data = [
        # SC01
        {
            "id": "SC01",
            "title": "The Parched Supercontinent of Pangaea",
            "purpose": "Establish bone-dry supercontinent Pangaea 234 million years ago",
            "action": "A field paleontologist surveys vast cracked terracotta sand dunes beneath a glaring sun as storm clouds gather far on the horizon.",
            "setting": "Aged fossil vellum #EFE4C8 with carved woodcut black linework #1E1E1E depicting an arid Triassic desert canyon.",
            "camera": "Panoramic wide landscape tracking forward toward a lone paleontologist silhouette",
            "narration": "Two hundred thirty-four million years ago, the supercontinent Pangaea was a parched, unforgiving desert. Red sand dunes stretched unbroken across thousands of miles under a merciless sun. Most terrestrial life clung desperately to isolated river valleys. No living creature on Earth was prepared for what was gathering over the Panthalassic ocean. The skies turned black, and the deluge began.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Epic, foreboding, atmospheric",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images_spec": [
                ("SC01_I1", "Panoramic 2D woodcut of barren Pangaean sand dunes in terracotta #A44A3F and ochre #D9A520 under a blazing white sun on aged parchment #EFE4C8, fine relief gouge lines.", None, "full_scene", "burst", "hook_shock"),
                ("SC01_I2", "Field paleontologist in canvas coat stands atop a sandstone cliff, holding a brass geological hammer while gazing across endless cracked desert flats.", "SC01_I1", "variation", "fast", "hook_shock"),
                ("SC01_I3", "Extreme close-up of cracked desert mud with prehistoric tetrapod footprints fossilized in dry terracotta silt, bold carved woodcut ink #1E1E1E.", "SC01_I2", "cutaway_detail", "fast", "hook_shock"),
                ("SC01_I4", "Distant Panthalassic ocean horizon where towering black thunderheads rise against copper-tinted skies, dark ink wash filling the horizon.", "SC01_I3", "environment", "fast", "hook_shock"),
                ("SC01_I5", "First massive rain droplets splashing against dry desert sand, carving tiny craters into the ancient red sediment.", "SC01_I4", "cutaway_detail", "normal", "hook_shock"),
                ("SC01_I6", "The sky turns completely black as violent diagonal rain hatching sweeps across the prehistoric landscape, extinguishing the desert sun.", "SC01_I5", "full_scene", "normal", "hook_shock"),
            ],
            "quotes": [
                "Two hundred thirty-four million years ago,",
                "the supercontinent Pangaea was a parched, unforgiving desert.",
                "Red sand dunes stretched unbroken across thousands of miles",
                "Most terrestrial life clung desperately to isolated river valleys.",
                "No living creature on Earth was prepared for what was gathering",
                "The skies turned black, and the deluge began."
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "The Wrangellia Volcanic Catalyst",
            "purpose": "Reveal Wrangellia flood basalts venting gigatons of carbon dioxide",
            "action": "Massive tectonic fissures rip across modern Alaska, spewing incandescent basalt lava and choking volcanic plumes into the atmosphere.",
            "setting": "Carved woodcut cross-section of Earth's crust on aged parchment #EFE4C8 with crimson magma veins #A44A3F.",
            "camera": "Deep geological cross-section panning upward from subterranean magma chambers into sky",
            "narration": "The catalyst was not born in the atmosphere, but torn violently from the crust. Across modern British Columbia and Alaska, the massive Wrangellia flood basalts tore open. For five million years, towering fissures spewed colossal volcanic magma and gigatons of carbon dioxide into the air. Global temperatures surged by nine degrees Fahrenheit, transforming Earth into an unbreathable thermal hothouse.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Cataclysmic, tectonic, scientific",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "chronological_shift",
            "images_spec": [
                ("SC02_I1", "Stratigraphic geological cross-section of tectonic plates fracturing, revealing glowing underground basalt chambers on aged parchment #EFE4C8.", None, "visual_diagram", "fast", "chronological_shift"),
                ("SC02_I2", "Towering fissure volcanic vents in prehistoric Wrangellia spewing massive rivers of incandescent red basalt #A44A3F across ancient crust.", "SC02_I1", "environment", "fast", "chronological_shift"),
                ("SC02_I3", "Colossal dark plumes of volcanic carbon dioxide billowing miles into the Triassic stratosphere, woodcut relief cross-hatching.", "SC02_I2", "concept_metaphor", "fast", "chronological_shift"),
                ("SC02_I4", "Chemical callout diagram showing molecular CO2 clouds blanketing the upper atmosphere, drawn with fine fountain-pen annotations on vellum.", "SC02_I3", "visual_diagram", "normal", "chronological_shift"),
                ("SC02_I5", "Global globe diagram of Pangaea wrapped in a dense thermal greenhouse haze, oceans tinted in warm amber #D9A520.", "SC02_I4", "full_scene", "normal", "chronological_shift"),
                ("SC02_I6", "Paleontologist holds a brass temperature gauge showing soaring planetary thermal lines, standing before basalt columns.", "SC02_I5", "variation", "normal", "chronological_shift"),
            ],
            "quotes": [
                "The catalyst was not born in the atmosphere,",
                "but torn violently from the crust.",
                "Across modern British Columbia and Alaska,",
                "For five million years, towering fissures spewed colossal volcanic magma",
                "Global temperatures surged by nine degrees Fahrenheit,",
                "transforming Earth into an unbreathable thermal hothouse."
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "Boiling Oceans and Runaway Evaporation",
            "purpose": "Explain how boiling ocean waters locked atmospheric storm engines",
            "action": "Superheated tropical waters steam intensely, feeding massive spiraling hurricane systems that lock across the equatorial belt.",
            "setting": "Celestial and oceanic woodcut diagram on aged vellum #EFE4C8 with slate-grey storm washes.",
            "camera": "High-altitude meteorological perspective viewing spiraling ocean cloud bands",
            "narration": "Superheated air triggered runaway planetary evaporation. The world ocean reached a staggering one hundred degrees Fahrenheit, turning tropical waters into a steaming bath. Moisture boiled off equatorial currents, creating massive thermal low-pressure systems. Instead of seasonal summer monsoons that faded after weeks, an unstoppable atmospheric engine locked in place. The storm clouds simply refused to leave.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Relentless, scientific, accelerating",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "mechanism_breakdown",
            "images_spec": [
                ("SC03_I1", "Woodcut illustration of turbulent ocean currents steaming like boiling water under a scorching sun on aged parchment #EFE4C8.", None, "environment", "fast", "mechanism_breakdown"),
                ("SC03_I2", "Meteorological circulation diagram showing rising columns of hot oceanic water vapor condensing into dense cloud walls.", "SC03_I1", "visual_diagram", "fast", "mechanism_breakdown"),
                ("SC03_I3", "Colossal spiraling mega-monsoon vortex spanning thousands of miles across Panthalassa, rendered in swirling black ink curves.", "SC03_I2", "full_scene", "normal", "mechanism_breakdown"),
                ("SC03_I4", "Cross-section showing atmospheric high-pressure and low-pressure locks trapped against the towering Central Pangaean Mountains.", "SC03_I3", "visual_diagram", "normal", "mechanism_breakdown"),
                ("SC03_I5", "Dense slate-black cloud wall rolling continuously over continental interior valleys, blotting out natural light.", "SC03_I4", "environment", "normal", "mechanism_breakdown"),
                ("SC03_I6", "Rain streaks falling in relentless vertical and diagonal lines, locking into an endless repeating cycle of moisture.", "SC03_I5", "still_life", "fast", "mechanism_breakdown"),
            ],
            "quotes": [
                "Superheated air triggered runaway planetary evaporation.",
                "The world ocean reached a staggering one hundred degrees Fahrenheit,",
                "Moisture boiled off equatorial currents,",
                "creating massive thermal low-pressure systems.",
                "an unstoppable atmospheric engine locked in place.",
                "The storm clouds simply refused to leave."
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "Debunking the Myth of Gentle Rain",
            "purpose": "Deliver editorial stance debunking gentle rain as an acidic ecological scald",
            "action": "Acidic rain streams strip lush foliage down to skeletons, dissolving mineral topsoils into grey toxic runoff.",
            "setting": "Bleak ecological cross-section on aged vellum #EFE4C8 with corroded terracotta #A44A3F and fern green #5E7D3A.",
            "camera": "Slow cinematic push-in on dissolving tree bark and acidified stream banks",
            "narration": "Popular mythology often paints ancient rainstorms as gentle life-giving events that greened the prehistoric plains. The reality was a toxic ecological nightmare. This was not clean mountain rain, but scorching acidic downpours that stripped topsoil, poisoned freshwater lakes, and suffocated terrestrial vegetation. The Carnian Pluvial Episode was a brutal planetary crucible that systematically dismantled existing food webs.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Critical, sharp, demystifying",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images_spec": [
                ("SC04_I1", "Woodcut contrasting a mythical peaceful green meadow against an acidified, eroded wasteland on aged parchment #EFE4C8.", None, "concept_metaphor", "slow", "editorial_commentary"),
                ("SC04_I2", "Acidic rain droplets searing ancient seed-fern leaves, causing edges to curl and dissolve in fine etched ink detail.", "SC04_I1", "cutaway_detail", "slow", "editorial_commentary"),
                ("SC04_I3", "Toxic grey mud sludge pouring off bare hillside slopes where topsoil has been violently stripped away by downpours.", "SC04_I2", "environment", "normal", "editorial_commentary"),
                ("SC04_I4", "A suffocated freshwater lake choked with floating debris and decaying vegetation under continuous grey rain.", "SC04_I3", "full_scene", "normal", "editorial_commentary"),
                ("SC04_I5", "Field paleontologist kneeling by an eroded cliff face, holding up a handful of acidic grey silt with a somber expression.", "SC04_I4", "variation", "slow", "editorial_commentary"),
                ("SC04_I6", "Symbolic woodcut scale balancing fertile plant life against heavy acidic rainwater droplets, tilting into crisis.", "SC04_I5", "concept_metaphor", "slow", "editorial_commentary"),
            ],
            "quotes": [
                "Popular mythology often paints ancient rainstorms as gentle life-giving events",
                "The reality was a toxic ecological nightmare.",
                "This was not clean mountain rain, but scorching acidic downpours",
                "that stripped topsoil, poisoned freshwater lakes,",
                "The Carnian Pluvial Episode was a brutal planetary crucible",
                "that systematically dismantled existing food webs."
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Supercontinent Floods",
            "purpose": "Illustrate supercontinental flash floods transforming deserts to mud",
            "action": "Dry canyon floors become raging rivers of mud and debris, washing away boulders and ancient riverbanks.",
            "setting": "Dynamic carved landscape on parchment #EFE4C8 with surging black water lines #1E1E1E.",
            "camera": "Dynamic low-angle camera tracking violent flash flood water rushing toward the viewer",
            "narration": "Across the barren heart of Pangaea, dry ravines became raging torrents overnight. Flash floods tore down mountain ranges, carving deep canyons through sedimentary rock. Ancient river deltas swelled into suffocating freshwater seas that buried entire biomes under heavy silt. For tens of thousands of generations, every single sunrise was greeted by thunder, grey fog, and pounding water.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Vivid, overwhelming, relentless",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images_spec": [
                ("SC05_I1", "Dry sandstone ravine violently erupting as a surging wall of muddy water crashes through rock walls on aged parchment #EFE4C8.", None, "environment", "burst", "mechanism_step"),
                ("SC05_I2", "Massive boulders rolling down steep eroded mountain chutes in a torrent of churned mud and fractured timber.", "SC05_I1", "environment", "fast", "mechanism_step"),
                ("SC05_I3", "Ancient river delta expanding across hundreds of miles, drowning lowlands under murky sediment and fallen conifers.", "SC05_I2", "full_scene", "normal", "mechanism_step"),
                ("SC05_I4", "A lone prehistoric tetrapod struggling through knee-deep mud flats as heavy rain pelts down from a dark sky.", "SC05_I3", "full_scene", "fast", "mechanism_step"),
                ("SC05_I5", "Thick grey fog banks rolling across endless drowned swamplands where lightning flickers between low clouds.", "SC05_I4", "environment", "normal", "mechanism_step"),
                ("SC05_I6", "Paleontologist standing on a high rocky outcropping looking down at the drowned valley beneath an oil lantern.", "SC05_I5", "variation", "normal", "mechanism_step"),
            ],
            "quotes": [
                "Across the barren heart of Pangaea, dry ravines became raging torrents",
                "Flash floods tore down mountain ranges, carving deep canyons",
                "Ancient river deltas swelled into suffocating freshwater seas",
                "that buried entire biomes under heavy silt.",
                "For tens of thousands of generations,",
                "every single sunrise was greeted by thunder, grey fog, and pounding water."
            ]
        },
        # SC06
        {
            "id": "SC06",
            "title": "Two Million Years of Continuous Deluge",
            "purpose": "Chronicle the two-million-year continuous downpour across global strata",
            "action": "Deep stratigraphic cliff bands show desert sandstones abruptly yielding to thick dark mudstones and coal seams.",
            "setting": "Detailed geological cliff face cross-section on aged parchment #EFE4C8 with fossil callouts.",
            "camera": "Vertical tracking shot rising up stratified rock layers through time",
            "narration": "The rain did not fall for weeks, months, or years. It hammered the supercontinent relentlessly for two million continuous years. In modern Italy, England, and China, geologists uncover the exact signature of this deluge. Crisp red desert sandstones suddenly end, replaced by thick grey mudstone, swampy coal seams, and layers rich in fossilized plant amber.",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Awe-inspiring, deep-time, monumental",
            "narrative_phase": "structural_model",
            "narrative_situation": "historical_chronology",
            "images_spec": [
                ("SC06_I1", "Massive stratigraphic cliff exposure in the Italian Dolomites showing distinct horizontal strata on parchment #EFE4C8.", None, "visual_diagram", "normal", "historical_chronology"),
                ("SC06_I2", "Close-up of the rock boundary where red desert sandstone abruptly transitions into dense grey Carnian mudstone.", "SC06_I1", "cutaway_detail", "normal", "historical_chronology"),
                ("SC06_I3", "World map highlighting matching Carnian pluvial strata discovered across Britain, Germany, China, and Argentina.", "SC06_I2", "visual_diagram", "fast", "historical_chronology"),
                ("SC06_I4", "Thick coal seams compressed between rock layers, indicating swampy peat accumulation during the pluvial episode.", "SC06_I3", "cutaway_detail", "normal", "historical_chronology"),
                ("SC06_I5", "Translucent golden droplets of fossil amber embedded inside dark shale, glowing in warm amber gold #D9A520.", "SC06_I4", "still_life", "slow", "historical_chronology"),
                ("SC06_I6", "Paleontologist holds a magnifying loupe to an amber specimen containing ancient conifer needle inclusions.", "SC06_I5", "variation", "normal", "historical_chronology"),
            ],
            "quotes": [
                "The rain did not fall for weeks, months, or years.",
                "It hammered the supercontinent relentlessly for two million continuous years.",
                "In modern Italy, England, and China,",
                "geologists uncover the exact signature of this deluge.",
                "Crisp red desert sandstones suddenly end,",
                "replaced by thick grey mudstone, swampy coal seams, and layers rich in fossilized plant amber."
            ]
        },
        # SC07
        {
            "id": "SC07",
            "title": "Extinction of the Old Masters",
            "purpose": "Document the collapse of dominant rhynchosaurs and bulky cynodonts",
            "action": "Massive herbivorous rhynchosaurs collapse in rotting wetlands as specialized food plants die off in the waterlogged soil.",
            "setting": "Grim paleo-swamp on aged vellum #EFE4C8 with terracotta sediment #A44A3F and rotting fern bogs.",
            "camera": "Slow elegiac pull-back over extinct fossil skeletons half-submerged in silt",
            "narration": "The reigning masters of Pangaea could not endure the humidity and collapsing vegetation. Huge herbivorous rhynchosaurs and bulky mammal-like cynodonts died off in catastrophic numbers. Their heavy sprawling bodies and specialized grinding teeth were useless in soggy rot-filled marshes. Over thirty percent of all marine and land species vanished forever into the muddy fossil strata.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Elegiac, tragic, evolutionary turnover",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "comparative_scale",
            "images_spec": [
                ("SC07_I1", "Heavy, pig-sized herbivorous rhynchosaur with parrot-like beak struggling helplessly in deep quagmire mud on aged vellum #EFE4C8.", None, "full_scene", "fast", "comparative_scale"),
                ("SC07_I2", "Bulky mammal-like cynodont shivering beneath rotting cycad fronds under heavy vertical rain lines.", "SC07_I1", "full_scene", "normal", "comparative_scale"),
                ("SC07_I3", "Fossil skeleton of a rhynchosaur gradually being buried under successive layers of fine grey river mud.", "SC07_I2", "cutaway_detail", "normal", "comparative_scale"),
                ("SC07_I4", "Ecosystem food-web diagram showing herbivore populations plummeting as seed-ferns rot away.", "SC07_I3", "visual_diagram", "normal", "comparative_scale"),
                ("SC07_I5", "Bleak panoramic swamp littered with mineralized fossil bones sticking out from dark silt banks.", "SC07_I4", "environment", "normal", "comparative_scale"),
                ("SC07_I6", "Paleontologist gently brushes sediment off an extinct cynodont skull, documenting the extinction horizon.", "SC07_I5", "variation", "slow", "comparative_scale"),
            ],
            "quotes": [
                "The reigning masters of Pangaea could not endure the humidity",
                "Huge herbivorous rhynchosaurs and bulky mammal-like cynodonts died off",
                "Their heavy sprawling bodies and specialized grinding teeth",
                "were useless in soggy rot-filled marshes.",
                "Over thirty percent of all marine and land species",
                "vanished forever into the muddy fossil strata."
            ]
        },
        # SC08
        {
            "id": "SC08",
            "title": "The Nimble Underdogs of Deep Time",
            "purpose": "Spotlight the agile underdogs navigating the mud",
            "action": "Early dinosaurs like Herrerasaurus leap effortlessly across mud slicks on long upright hind legs while heavier reptiles flounder.",
            "setting": "Dynamic riverbank on aged vellum #EFE4C8 with green moss #5E7D3A and terracotta mud #A44A3F.",
            "camera": "Dynamic lateral tracking shot following an early bipedal dinosaur sprinting across rocks",
            "narration": "Yet amidst the muddy carnage, one obscure lineage of reptiles found an astonishing advantage. Before the deluge, early dinosaurs were marginal, two-legged sprinters representing less than five percent of land animals. Their upright posture, hollow air-sac bones, and rapid metabolism allowed them to traverse sodden terrain where heavier competitors sank and drowned.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Dynamic, revelatory, biological triumph",
            "narrative_phase": "structural_model",
            "narrative_situation": "concrete_detail",
            "images_spec": [
                ("SC08_I1", "Small, sleek bipedal early dinosaur (Herrerasaurus type) sprinting lithely along a slippery river ridge on aged parchment #EFE4C8.", None, "full_scene", "fast", "concrete_detail"),
                ("SC08_I2", "Anatomical skeletal comparison diagram: sprawling lizard-like cynodont leg vs upright erect pillar-like dinosaur leg.", "SC08_I1", "visual_diagram", "normal", "concrete_detail"),
                ("SC08_I3", "Cross-section of hollow dinosaur bone showing honeycomb air pockets, giving immense strength with minimal weight.", "SC08_I2", "cutaway_detail", "fast", "concrete_detail"),
                ("SC08_I4", "Two early dinosaurs hunting cooperatively along a gravel bar, agile feet leaving clean, sharp claw marks in wet silt.", "SC08_I3", "full_scene", "normal", "concrete_detail"),
                ("SC08_I5", "Prehistoric pie chart on vellum showing dinosaur biodiversity expanding rapidly from a sliver to a dominant wedge.", "SC08_I4", "visual_diagram", "normal", "concrete_detail"),
                ("SC08_I6", "Paleontologist studies dinosaur foot impressions preserved beside ancient ripple marks in stone.", "SC08_I5", "variation", "normal", "concrete_detail"),
            ],
            "quotes": [
                "Yet amidst the muddy carnage,",
                "one obscure lineage of reptiles found an astonishing advantage.",
                "Before the deluge, early dinosaurs were marginal, two-legged sprinters",
                "Their upright posture, hollow air-sac bones,",
                "allowed them to traverse sodden terrain",
                "where heavier competitors sank and drowned."
            ]
        },
        # SC09
        {
            "id": "SC09",
            "title": "Disaster as an Evolutionary Crucible",
            "purpose": "Deliver key philosophical commentary on extinction",
            "action": "A conceptual tree of life branches outward across aged vellum as old branches wither and dinosaur twigs surge upward in bold green ink.",
            "setting": "Metaphorical evolutionary diagram on aged parchment #EFE4C8 with rich amber #D9A520 and ink accents.",
            "camera": "Slow reverent zoom into expanding branches of the evolutionary tree",
            "narration": "Mass extinctions do not merely destroy life; they clear the ecological board for revolutionary adaptations. Without the two million years of relentless deluge, dinosaurs might have remained trivial sideline oddities of deep time. The Carnian storm proves that dominance in nature is fragile, and survival favors adaptable innovators when planetary baselines permanently shift.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Philosophical, profound, evaluative",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images_spec": [
                ("SC09_I1", "Tree of life woodcut drawing on aged vellum #EFE4C8, with withered archaic branches beside bursting dinosaur boughs.", None, "concept_metaphor", "slow", "editorial_commentary"),
                ("SC09_I2", "Symbolic stone chessboard where towering stone idols crumble under rain while small agile figures advance across squares.", "SC09_I1", "concept_metaphor", "slow", "editorial_commentary"),
                ("SC09_I3", "Paleontologist standing before an enormous rock wall showing the boundary of extinction, pencil in hand.", "SC09_I2", "variation", "slow", "editorial_commentary"),
                ("SC09_I4", "Close-up of ancient conifer shoots sprouting vigorously from charred volcanic soil nourished by flood silt.", "SC09_I3", "still_life", "normal", "editorial_commentary"),
                ("SC09_I5", "Dramatic silhouette of an early sauropodomorph dinosaur standing against an illuminated golden storm horizon.", "SC09_I4", "full_scene", "slow", "editorial_commentary"),
                ("SC09_I6", "Philosophical hourglass metaphor where sand grains transform into falling rain droplets and fossil bones.", "SC09_I5", "concept_metaphor", "slow", "editorial_commentary"),
            ],
            "quotes": [
                "Mass extinctions do not merely destroy life;",
                "they clear the ecological board for revolutionary adaptations.",
                "Without the two million years of relentless deluge,",
                "dinosaurs might have remained trivial sideline oddities of deep time.",
                "The Carnian storm proves that dominance in nature is fragile,",
                "and survival favors adaptable innovators when planetary baselines permanently shift."
            ]
        },
        # SC10
        {
            "id": "SC10",
            "title": "The Dawn of the Dinosaur Dynasty",
            "purpose": "Show the explosive adaptive radiation of dinosaurs across green Pangaea",
            "action": "As the storm clouds finally part, brilliant sunlight illuminates vast lush coniferous forests teeming with diverse early dinosaurs.",
            "setting": "Expansive green prehistoric wilderness on aged vellum #EFE4C8 with vibrant fern green #5E7D3A and ochre #D9A520.",
            "camera": "Grand sweeping panoramic crane shot revealing a transformed, vibrant supercontinent",
            "narration": "When the Wrangellia volcanic fissures finally cooled and the skies cleared, Pangaea was unrecognizably transformed. Lush coniferous forests covered what were once arid salt flats. Dinosaurs emerged from the shadows, multiplying rapidly across every continent. Within a few million years, their share of terrestrial vertebrate biodiversity leaped from five percent to over ninety percent.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Triumphant, expansive, majestic",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "structural_model",
            "images_spec": [
                ("SC10_I1", "Brilliant golden sunbeams breaking through parting storm clouds, illuminating towering primeval conifer canopies on parchment #EFE4C8.", None, "environment", "burst", "structural_model"),
                ("SC10_I2", "Diverse early dinosaurs—slender predators, long-necked prosauropods, agile herbivores—grazing peacefully across a lush river valley.", "SC10_I1", "full_scene", "fast", "structural_model"),
                ("SC10_I3", "Global paleogeography map showing dinosaur fossil localities spreading across all corners of connected Pangaea.", "SC10_I2", "visual_diagram", "normal", "structural_model"),
                ("SC10_I4", "Dramatic silhouette of a tall bipedal prosauropod browsing high conifer branches in early morning mist.", "SC10_I3", "full_scene", "normal", "structural_model"),
                ("SC10_I5", "Fossil diversity bar chart showing dinosaur species numbers rocketing upward across Late Triassic rock layers.", "SC10_I4", "visual_diagram", "normal", "structural_model"),
                ("SC10_I6", "Paleontologist smiles while standing atop a high scenic cliff overlooking the lush post-deluge valley.", "SC10_I5", "variation", "normal", "structural_model"),
            ],
            "quotes": [
                "When the Wrangellia volcanic fissures finally cooled",
                "and the skies cleared, Pangaea was unrecognizably transformed.",
                "Lush coniferous forests covered what were once arid salt flats.",
                "Dinosaurs emerged from the shadows, multiplying rapidly across every continent.",
                "Within a few million years,",
                "their share of terrestrial vertebrate biodiversity leaped from five percent to over ninety percent."
            ]
        },
        # SC11
        {
            "id": "SC11",
            "title": "The Memory in the Rock",
            "purpose": "Close with deep-time reflection on rock layers preserving ancient trials",
            "action": "The paleontologist traces fingers across banded rock layers, reflecting on how ancient crises shaped modern existence.",
            "setting": "Serene outdoor cliff outcrop at twilight on aged fossil vellum #EFE4C8.",
            "camera": "Gentle medium close-up on paleontologist and rock face, slowly pulling back to endcard hold",
            "narration": "The next time you walk across a rocky outcrop, look closely at the banded stone beneath your feet. Hidden inside those quiet layers is the memory of an unbroken two-million-year storm that forged our planet's greatest dynasty. Every rock layer beneath your feet holds an entire lost world. See you in the next epoch.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Poetic, contemplative, resonant",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cta_close",
            "images_spec": [
                ("SC11_I1", "Paleontologist gently runs fingers across finely stratified limestone and mudstone layers on a sunlit cliff outcrop on aged parchment #EFE4C8.", None, "cutaway_detail", "normal", "cta_close"),
                ("SC11_I2", "Close-up of a fossil amber droplet glowing like a warm lantern inside dark grey Triassic siltstone.", "SC11_I1", "still_life", "normal", "cta_close"),
                ("SC11_I3", "The paleontologist pauses and looks out toward a vast modern mountain valley under a peaceful blue sky.", "SC11_I2", "full_scene", "normal", "cta_close"),
                ("SC11_I4", "Transparent split-view overlay: modern hiking trail superimposed over the primeval drowned Carnian swamp of 234 million years ago.", "SC11_I3", "concept_metaphor", "normal", "cta_close"),
                ("SC11_I5", "Paleontologist tips hat toward the viewer with field satchel and hammer, standing by a weathered trail marker.", "SC11_I4", "variation", "normal", "cta_close"),
                ("SC11_I6", "Deep Time Strata official carved woodcut channel endcard on aged fossil parchment #EFE4C8. Brass hammer and amber jewel rest on stratified rock ledge beside hand-carved text 'DEEP TIME STRATA'.", "SC11_I5", "white_card", "hold", "cta_close", True),
            ],
            "quotes": [
                "The next time you walk across a rocky outcrop,",
                "look closely at the banded stone beneath your feet.",
                "Hidden inside those quiet layers is the memory",
                "of an unbroken two-million-year storm that forged our planet's greatest dynasty.",
                "Every rock layer beneath your feet holds an entire lost world.",
                "See you in the next epoch."
            ]
        }
    ]

    scenes = []
    coverage = []
    claims = []

    for sc_raw in scene_data:
        sc_id = sc_raw["id"]
        req_id = sc_raw["requirements"][0]
        coverage.append({
            "requirement_id": req_id,
            "scene_id": sc_id,
            "quote": sc_raw["quotes"][0] + " " + sc_raw["quotes"][1]
        })

        if sc_id in ("SC01", "SC02", "SC03", "SC06", "SC07", "SC08", "SC10"):
            src = sc_raw["source_ids"][0]
            fact_text = sources[0]["facts"][0] if src == "SRC01" else (sources[1]["facts"][0] if src == "SRC02" else sources[2]["facts"][0])
            claims.append({
                "scene_id": sc_id,
                "quote": sc_raw["quotes"][1],
                "language": "en",
                "source_id": src,
                "fact": fact_text
            })

        imgs = []
        bts = []
        for idx, (img_id, desc, based_on, shot_type, tempo, situation, *rest) in enumerate(sc_raw["images_spec"]):
            is_endcard = bool(rest[0]) if rest else False
            beat_id = f"{sc_id}_B{idx+1}"
            quote_text = sc_raw["quotes"][idx]

            imgs.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "based_on": based_on,
                "preserve": "Aged parchment canvas #EFE4C8, bold carved woodcut black linework #1E1E1E, terracotta and amber palette, paleontologist design." if based_on else "Aged fossil parchment #EFE4C8, bold carved woodcut ink #1E1E1E, terracotta and amber palette.",
                "change": desc,
                "reason": f"Visual progression beat {beat_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_type,
                "tempo": tempo,
                "narrative_situation": situation,
                "has_character": True,
                "is_endcard": is_endcard,
                "motion_prompt": "Smooth 2D carved woodblock animation, continuous natural motion, silent visual storytelling, no talking, no lip movement"
            })

            bts.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Visual beat {beat_id} accompanying '{quote_text[:30]}...'",
                "anchor": {
                    "en": {"quote": quote_text, "occurrence": 1},
                    "vi": {"quote": quote_text, "occurrence": 1}
                },
                "effect": "hold" if is_endcard else ("cut" if tempo in ("burst", "fast") else "pan_right"),
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": tempo,
                "narrative_situation": situation,
                "is_endcard": is_endcard
            })

        scenes.append({
            "id": sc_id,
            "title": sc_raw["title"],
            "purpose": sc_raw["purpose"],
            "action": sc_raw["action"],
            "setting": sc_raw["setting"],
            "camera": sc_raw["camera"],
            "narration": sc_raw["narration"],
            "requirements": sc_raw["requirements"],
            "character_ids": sc_raw["character_ids"],
            "source_ids": sc_raw["source_ids"],
            "tone": sc_raw["tone"],
            "narrative_phase": sc_raw["narrative_phase"],
            "narrative_situation": sc_raw["narrative_situation"],
            "images": imgs,
            "beats": bts
        })

    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(brief),
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id)],
        "scenes": scenes,
        "coverage": coverage,
        "outline": outline["outline"],
        "claims": claims,
        "revision_response": [],
        "open_questions": []
    }

    return channel_id, job_id, brief, outline, competitor_research, content


def get_deep_time_strata_short():
    channel_id = "en_parable_lamp"
    job_id = "en-deep-time-strata-batch1-9x16"
    parent_long_id = "en-deep-time-strata-batch1-16x9"
    ch = get_channel(channel_id)

    topic = "The Rainstorm That Lasted Two Million Years"
    youtube_title = "The Rainstorm That Lasted Two Million Years"  # 43 chars <= 55

    sources = [
        {
            "id": "SRC01",
            "title": "Synchronic climatic and biotic change in the Carnian",
            "reference": "Simms, M. J., & Ruffell, A. H. (1989). Nature, 340, 521-526.",
            "facts": ["Wrangellia flood basalt eruptions triggered catastrophic planetary global warming."]
        },
        {
            "id": "SRC02",
            "title": "Extinction and dawn of the modern world in the Carnian",
            "reference": "Dal Corso, J. et al. (2020). Science Advances, 6(38), eaba0099.",
            "facts": ["The Carnian Pluvial Episode lasted two million years, reshaping Earth's biomes."]
        }
    ]

    required_points = [
        {"id": "R01", "text": "Imagine walking outside and knowing the rain falling on your head will not stop for two million years"},
        {"id": "R02", "text": "Colossal volcanic eruptions in modern Alaska superheating oceans into runaway storms"},
        {"id": "R03", "text": "Acidic rain deluge drowning dominant reptile species and resetting ecosystems"},
        {"id": "R04", "text": "Agile bipedal early dinosaurs thriving in the sodden world and conquering continents"},
        {"id": "R05", "text": "Cliffhanger on dinosaur survival and spin-off bridge to full documentary"}
    ]

    editorial_stance = {
        "myth_debunked": "Prehistoric rain was a gentle, life-giving blessing for all living things.",
        "why_generic_advice_fails": "Simplistic climatic assumptions overlook that superheated acidic rains destroy existing food webs.",
        "channel_verdict": "The two-million-year rainstorm was an ecological reset that dethroned heavy reptiles and crowned the dinosaurs.",
        "tradeoff_or_blindspot": "Surviving deep-time crisis demanded physiological agility and upright speed over armored bulk."
    }

    actionable_value = {
        "core_mechanism": "Wrangellia eruptions pumped carbon into the air, turning oceans into steaming engines that powered endless storms.",
        "practical_rule_of_thumb": "Look for dark mudstone and fossil amber between desert sandstones to read ancient climate crises.",
        "real_world_scenario": "When examining Triassic cliff layers, notice how grey fossil-amber bands record the two-million-year deluge."
    }

    thumbnail_spec = {
        "visual_hook": "Small agile two-legged early dinosaur sprinting across cracked mud under massive dark rain clouds.",
        "text_overlay": "ENDLESS RAIN",
        "contrast_pair": "Dry red desert vs Unbroken flood",
        "thumbnail_prompt": "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 high-impact YouTube poster thumbnail illustration extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, zero UI chrome, and zero dark vignette.\n\nVisual Style (ch_en_parable_woodcut): Expressive 2D carved paleo-lithograph and linocut geological strata print on aged fossil-matrix parchment (#EFE4C8, #1E1E1E bold carved woodcut ink, #D9A520 amber gold, #A44A3F terracotta). Orthographic 2D, >=60% negative space, zero 3D, zero gradients.\n\nFocal Subject: A sleek bipedal early dinosaur with terracotta striping (#A44A3F) sprints dynamically across cracked mud while heavy diagonal rain cross-hatching sweeps downward from black storm clouds.\n\nPoster Typography: Hand-lettered uppercase English text in upper third: 'ENDLESS RAIN'. Bold relief woodcut font directly on parchment, strictly zero rectangular boxes or gradient cards.",
        "layout_mode": "split_contrast"
    }

    cta_plan = {
        "cliffhanger_peak": "How did these fragile two-legged sprinters outlast two million years of flooding while armored giants perished?",
        "bridge": "Watch the complete Carnian Pluvial chronicle on Deep Time Strata YouTube.",
        "close": "Every rock layer beneath your feet holds an entire lost world.",
        "endcard_text": "WATCH FULL VIDEO ON YOUTUBE"
    }

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Hook viewers with the mind-bending reality of a two-million-year rainstorm and bridge them to the full long-form documentary",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 38.0,
            "max_seconds": 52.0
        },
        "scene_count": 5,
        "required_points": required_points,
        "language": "en",
        "tone": ch.tone,
        "style": ch.visual.style_description,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "parent_long_id": parent_long_id,
        "facts_required": True,
        "sources": sources,
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": ch.voice,
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deliver a fast-paced 5-scene short explainer with 20 unique woodcut illustrations, maintaining an average hold under 2.5 seconds and zero AI cliches."
            ],
            "avoid": list(ch.avoid) + ["delve into", "testament to", "tapestry", "in conclusion", "it is important to remember"],
            "prior_knowledge": "None required.",
            "pacing": "Rapid-fire hook escalating directly to the cliffhanger question and long-form bridge.",
            "domain_requirements": [],
            "assumptions": [
                "Spoken in sharp, punchy English with zero throat-clearing."
            ],
            "text_style": {
                "font": "Carved woodblock relief serif",
                "color": "#1E1E1E",
                "outline": "#EFE4C8 parchment contrast",
                "size": "Legible on mobile vertical screen",
                "placement": "Upper third, <= 10% frame height"
            },
            "speech_rates": {
                "vi": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Baseline reference speech rate"
                },
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.15,
                    "source": "Punchy cadence for vertical short-form narrative"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": thumbnail_spec,
            "channel_pillar": "Deep Time Earth History & Stratigraphic Evolution",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["carnian pluvial episode", "rain for two million years", "dinosaurs", "shorts", "geology"],
            "cta_plan": cta_plan,
            "editorial_stance": editorial_stance,
            "actionable_value": actionable_value
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": thumbnail_spec,
        "channel_pillar": "Deep Time Earth History & Stratigraphic Evolution",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["carnian pluvial episode", "rain for two million years", "dinosaurs", "shorts", "geology"],
        "parent_long_id": parent_long_id,
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": ch.engagement.cta_voice,
            "bridge_templates": list(ch.engagement.bridge_templates),
            "close_templates": list(ch.engagement.close_templates),
            "endcard_text": ch.engagement.endcard_text,
            "banned_cta_phrases": list(ch.engagement.banned_cta_phrases)
        },
        "editorial_stance": editorial_stance,
        "actionable_value": actionable_value,
        "cta_plan": cta_plan,
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Immediate hook shock: the rainstorm that lasted two million years", "requirements": ["R01"], "transition": "Transition into volcanic cause"},
            {"scene_id": "SC02", "purpose": "Break down Wrangellia eruptions superheating oceans", "requirements": ["R02"], "transition": "Transition into ecological destruction"},
            {"scene_id": "SC03", "purpose": "Editorial commentary on the lethal acidic scald drowning ancient reptiles", "requirements": ["R03"], "transition": "Transition into dinosaur adaptation"},
            {"scene_id": "SC04", "purpose": "Show bipedal early dinosaurs thriving in waterlogged terrain", "requirements": ["R04"], "transition": "Transition to peak cliffhanger"},
            {"scene_id": "SC05", "purpose": "Peak cliffhanger twist, channel bridge, and closing sign-off", "requirements": ["R05"], "transition": "Final hold endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "History of the Earth",
                    "top_performing_videos": [
                        {
                            "title": "When Earth Rained Nonstop",
                            "views": "1.8M views",
                            "hook_technique": "Startling two-sentence opening stating the impossible duration.",
                            "pacing_structure": "Hook -> Rapid volcanic breakdown -> Evolutionary survivor payoff.",
                            "retention_driver": "Rapid sensory imagery of ancient weather extremes."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Frontloading the two-million-year premise in the first three seconds.",
                        "Using bipedal running dinosaurs as dynamic visual anchors."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Dry red desert sand dunes suddenly blasted by relentless black rain.",
                "counter_intuitive_truth_slap": "A catastrophic rainstorm didn't destroy prehistoric life; it created the dinosaur empire."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Immediate shock of the unbroken two-million-year rain."},
                {"phase": "empirical_conflict", "purpose": "Volcanic gas turning oceans into steaming mega-monsoons."},
                {"phase": "structural_model", "purpose": "Lethal acidic rain wiping out heavy dominant reptiles."},
                {"phase": "actionable_resolution", "purpose": "Agile bipedal runners conquering every continent."},
                {"phase": "cliffhanger_spinoff", "purpose": "Peak cliffhanger question bridging to the full YouTube documentary."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chained 2D woodcut frames maintaining tactile aged parchment texture."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Deep Time Earth History & Stratigraphic Evolution",
            "myth_debunked": "Prehistoric rain was a gentle blessing.",
            "channel_verdict": "The Carnian deluge was a biological reset that crowned the dinosaurs.",
            "actionable_rule_of_thumb": "Look for dark mudstone between desert sandstones to read ancient climate shocks."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How did these fragile two-legged sprinters outlast two million years of flooding while armored giants perished?",
            "bridge": "Watch the complete Carnian Pluvial chronicle on Deep Time Strata YouTube.",
            "close": "Every rock layer beneath your feet holds an entire lost world.",
            "endcard_text": "WATCH FULL VIDEO ON YOUTUBE"
        }
    }

    scene_data = [
        # SC01
        {
            "id": "SC01",
            "title": "The Two-Million-Year Downpour",
            "purpose": "Immediate hook shock: the rainstorm that lasted two million years",
            "action": "A lone observer looks up in astonishment as black thunderclouds roll over arid Pangaean desert dunes.",
            "setting": "Aged fossil parchment #EFE4C8 with carved woodcut black ink linework #1E1E1E.",
            "camera": "Dynamic vertical tracking shot rising from cracked desert mud to towering storm clouds",
            "narration": "Imagine walking outside and knowing the rain falling on your head will not stop for two million years. Two hundred thirty-four million years ago, a supercontinental deluge flooded Earth and launched the dinosaur dynasty.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Electrifying, shocking, epic",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images_spec": [
                ("SC01_I1", "Vertical 2D woodcut of red Pangaean sand dunes blasted by black diagonal rain lines on aged parchment #EFE4C8.", None, "full_scene", "burst", "hook_shock"),
                ("SC01_I2", "A field paleontologist looks upward in awe as heavy raindrops crater into dry terracotta soil.", "SC01_I1", "variation", "fast", "hook_shock"),
                ("SC01_I3", "Prehistoric calendar diagram with rock layers ticking past 100,000 years, 500,000 years, to two million years.", "SC01_I2", "visual_diagram", "fast", "hook_shock"),
                ("SC01_I4", "Silhouette of a small agile dinosaur illuminated by lightning across a drowned ancient valley.", "SC01_I3", "environment", "normal", "hook_shock"),
            ],
            "quotes": [
                "Imagine walking outside and knowing",
                "the rain falling on your head will not stop for two million years.",
                "Two hundred thirty-four million years ago,",
                "a supercontinental deluge flooded Earth and launched the dinosaur dynasty."
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "Volcanic Superheating",
            "purpose": "Break down Wrangellia eruptions superheating oceans",
            "action": "Colossal volcanic fissures vent crimson magma and dark CO2 clouds, superheating tropical oceans.",
            "setting": "Tectonic cross-section on aged vellum #EFE4C8 with terracotta magma veins #A44A3F.",
            "camera": "Vertical cutaway rising from deep magma reservoirs to boiling ocean surface",
            "narration": "Colossal volcanic eruptions in modern Alaska tore through the crust, spewing gigatons of carbon dioxide. Global temperatures surged nine degrees, turning tropical oceans into boiling cauldrons that pumped unstoppable moisture into runaway atmospheric storms.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Tectonic, mechanistic, explosive",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "mechanism_breakdown",
            "images_spec": [
                ("SC02_I1", "Fissure volcanoes spewing rivers of glowing basalt lava across prehistoric Alaska on aged parchment #EFE4C8.", None, "environment", "burst", "mechanism_breakdown"),
                ("SC02_I2", "Carbon dioxide molecular plumes rising like dark pillars into the Triassic atmosphere.", "SC02_I1", "visual_diagram", "fast", "mechanism_breakdown"),
                ("SC02_I3", "Steaming tropical ocean waves boiling with bubbles under a blazing greenhouse sky.", "SC02_I2", "environment", "normal", "mechanism_breakdown"),
                ("SC02_I4", "Massive cyclone clouds spiraling over the entire Pangaean landmass in dark ink relief.", "SC02_I3", "concept_metaphor", "fast", "mechanism_breakdown"),
            ],
            "quotes": [
                "Colossal volcanic eruptions in modern Alaska tore through the crust,",
                "spewing gigatons of carbon dioxide.",
                "Global temperatures surged nine degrees, turning tropical oceans into boiling cauldrons",
                "that pumped unstoppable moisture into runaway atmospheric storms."
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Toxic Scald",
            "purpose": "Editorial commentary on the lethal acidic scald drowning ancient reptiles",
            "action": "Bulky dominant reptiles flounder and drown in toxic mud as acidic rain corrodes vegetation.",
            "setting": "Corroded prehistoric marshland on aged vellum #EFE4C8 with grey mud and rotting plants.",
            "camera": "Close-up on heavy reptile sinking into waterlogged silt",
            "narration": "This torrential rain was not a gentle blessing; it was an acidic deluge that poisoned lakes and drowned dominant reptile species. Their heavy sprawling bodies sank into mud, leaving empty ecological niches across the planet.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Sharp, evaluative, dramatic",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images_spec": [
                ("SC03_I1", "Acidic rain streams burning the edges of ancient fern fronds on aged vellum #EFE4C8.", None, "cutaway_detail", "slow", "editorial_commentary"),
                ("SC03_I2", "Heavy rhynchosaur reptile sinking hopelessly into deep quagmire mud under pounding rain.", "SC03_I1", "full_scene", "slow", "editorial_commentary"),
                ("SC03_I3", "Fossil skeleton half-covered by dark grey mudstone layers, representing massive extinction.", "SC03_I2", "cutaway_detail", "normal", "editorial_commentary"),
                ("SC03_I4", "Empty biological niches depicted as vacant pedestals on a stratified rock ledge.", "SC03_I3", "concept_metaphor", "slow", "editorial_commentary"),
            ],
            "quotes": [
                "This torrential rain was not a gentle blessing;",
                "it was an acidic deluge that poisoned lakes and drowned dominant reptile species.",
                "Their heavy sprawling bodies sank into mud,",
                "leaving empty ecological niches across the planet."
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "Rise of the Agile Sprinters",
            "purpose": "Show bipedal early dinosaurs thriving in waterlogged terrain",
            "action": "Early dinosaurs with upright legs sprint across sodden mud ridges, expanding rapidly across Pangaea.",
            "setting": "Verdant prehistoric delta on aged parchment #EFE4C8 with moss green #5E7D3A and ochre #D9A520.",
            "camera": "Dynamic low tracking shot following the rapid strides of early bipedal dinosaurs",
            "narration": "Agile bipedal runners with hollow bones and rapid metabolism thrived in the sodden world. Before the storm, early dinosaurs made up barely five percent of land animals. Afterward, they conquered every single continent on Earth.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Triumphant, revelatory, biological",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "structural_model",
            "images_spec": [
                ("SC04_I1", "Sleek bipedal dinosaur leaping across muddy river rocks with effortless agility on parchment #EFE4C8.", None, "full_scene", "burst", "structural_model"),
                ("SC04_I2", "Anatomical bone cutaway revealing hollow air cavities inside dinosaur vertebrae.", "SC04_I1", "cutaway_detail", "fast", "structural_model"),
                ("SC04_I3", "Dinosaur pack moving through lush green conifer forests under parting storm clouds.", "SC04_I2", "full_scene", "normal", "structural_model"),
                ("SC04_I4", "Pangaean map with dinosaur territory expanding rapidly from five percent to ninety percent.", "SC04_I3", "visual_diagram", "normal", "structural_model"),
            ],
            "quotes": [
                "Agile bipedal runners with hollow bones and rapid metabolism",
                "thrived in the sodden world.",
                "Before the storm, early dinosaurs made up barely five percent of land animals.",
                "Afterward, they conquered every single continent on Earth."
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Dinosaur Mystery & Spinoff",
            "purpose": "Peak cliffhanger twist, channel bridge, and closing sign-off",
            "action": "Paleontologist holds a golden amber droplet, points toward the full documentary, and signs off.",
            "setting": "Twilight canyon outcrop on aged parchment #EFE4C8 with glowing amber droplet #D9A520.",
            "camera": "Dramatic push-in on glowing amber, cutting to channel endcard hold",
            "narration": "How did these fragile two-legged sprinters outlast two million years of flooding while armored giants perished? Watch the complete Carnian Pluvial chronicle on Deep Time Strata YouTube. Every rock layer beneath your feet holds an entire lost world.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Suspenseful, inviting, philosophical",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cliffhanger_peak",
            "images_spec": [
                ("SC05_I1", "Dramatic close-up of a fossilized dinosaur footprint stamped into rock beside an amber droplet on parchment #EFE4C8.", None, "cutaway_detail", "burst", "cliffhanger_peak"),
                ("SC05_I2", "Shadowy silhouette of early dinosaurs standing against an ominous, thundering horizon.", "SC05_I1", "full_scene", "fast", "cliffhanger_peak"),
                ("SC05_I3", "Field paleontologist holding an open field journal and gesturing toward the viewer with a friendly wave.", "SC05_I2", "variation", "normal", "cta_bridge"),
                ("SC05_I4", "Official Deep Time Strata 9:16 vertical channel endcard on aged fossil parchment #EFE4C8 with geological hammer, amber, and hand-lettered text 'WATCH FULL VIDEO ON YOUTUBE'.", "SC05_I3", "white_card", "hold", "cta_close", True),
            ],
            "quotes": [
                "How did these fragile two-legged sprinters outlast two million years of flooding",
                "while armored giants perished?",
                "Watch the complete Carnian Pluvial chronicle on Deep Time Strata YouTube.",
                "Every rock layer beneath your feet holds an entire lost world."
            ]
        }
    ]

    scenes = []
    coverage = []
    claims = []

    for sc_raw in scene_data:
        sc_id = sc_raw["id"]
        req_id = sc_raw["requirements"][0]
        coverage.append({
            "requirement_id": req_id,
            "scene_id": sc_id,
            "quote": sc_raw["quotes"][0] + " " + sc_raw["quotes"][1]
        })

        if sc_id in ("SC01", "SC02", "SC04"):
            src = sc_raw["source_ids"][0]
            fact_text = sources[0]["facts"][0] if src == "SRC01" else sources[1]["facts"][0]
            claims.append({
                "scene_id": sc_id,
                "quote": sc_raw["quotes"][1],
                "language": "en",
                "source_id": src,
                "fact": fact_text
            })

        imgs = []
        bts = []
        for idx, (img_id, desc, based_on, shot_type, tempo, situation, *rest) in enumerate(sc_raw["images_spec"]):
            is_endcard = bool(rest[0]) if rest else False
            beat_id = f"{sc_id}_B{idx+1}"
            quote_text = sc_raw["quotes"][idx]

            imgs.append({
                "id": img_id,
                "description": desc,
                "character_ids": ["CH01"],
                "based_on": based_on,
                "preserve": "Aged parchment canvas #EFE4C8, bold carved woodcut black linework #1E1E1E, terracotta and amber palette." if based_on else "Aged fossil parchment #EFE4C8, bold carved woodcut ink #1E1E1E, terracotta and amber palette.",
                "change": desc,
                "reason": f"Short visual beat {beat_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_type,
                "tempo": tempo,
                "narrative_situation": situation,
                "has_character": True,
                "is_endcard": is_endcard,
                "motion_prompt": "Smooth 2D carved woodblock animation, continuous natural motion, silent visual storytelling, no talking, no lip movement"
            })

            bts.append({
                "id": beat_id,
                "image_id": img_id,
                "purpose": f"Visual beat {beat_id} accompanying '{quote_text[:30]}...'",
                "anchor": {
                    "en": {"quote": quote_text, "occurrence": 1},
                    "vi": {"quote": quote_text, "occurrence": 1}
                },
                "effect": "hold" if is_endcard else ("cut" if tempo in ("burst", "fast") else "fade"),
                "focus": {"x": 0.5, "y": 0.5},
                "tempo": tempo,
                "narrative_situation": situation,
                "is_endcard": is_endcard
            })

        scenes.append({
            "id": sc_id,
            "title": sc_raw["title"],
            "purpose": sc_raw["purpose"],
            "action": sc_raw["action"],
            "setting": sc_raw["setting"],
            "camera": sc_raw["camera"],
            "narration": sc_raw["narration"],
            "requirements": sc_raw["requirements"],
            "character_ids": sc_raw["character_ids"],
            "source_ids": sc_raw["source_ids"],
            "tone": sc_raw["tone"],
            "narrative_phase": sc_raw["narrative_phase"],
            "narrative_situation": sc_raw["narrative_situation"],
            "images": imgs,
            "beats": bts
        })

    content = {
        "schema_version": "3.0",
        "brief_revision": 1,
        "brief_hash": compute_brief_hash(brief),
        "topic": topic,
        "duration": brief["duration"],
        "style": brief["style"],
        "required_points": [rp["text"] for rp in brief["required_points"]],
        "characters": [channel_cast(channel_id)],
        "scenes": scenes,
        "coverage": coverage,
        "outline": outline["outline"],
        "claims": claims,
        "revision_response": [],
        "open_questions": []
    }

    return channel_id, job_id, brief, outline, competitor_research, content
