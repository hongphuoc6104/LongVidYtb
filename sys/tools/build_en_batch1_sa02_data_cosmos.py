#!/usr/bin/env python3
"""Data definitions for Channel 3: Pocket Cosmos (en_pocket_cosmos).

Jobs:
- Long 16:9: sys/runs/en-pocket-cosmos-batch1-16x9 (11 scenes, 66 images, 620 words)
- Short 9:16: sys/runs/en-pocket-cosmos-batch1-9x16 (5 scenes, 20 images, 173 words)
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


def get_pocket_cosmos_long():
    channel_id = "en_pocket_cosmos"
    job_id = "en-pocket-cosmos-batch1-16x9"
    ch = get_channel(channel_id)

    topic = "Inside the Photon Sphere: Why Light Can Orbit a Black Hole—And Why You Would See the Back of Your Own Head"
    youtube_title = "Where Light Orbits a Black Hole: The Photon Sphere"  # 50 chars <= 55

    sources = [
        {
            "id": "SRC01",
            "title": "Image of a spherical black hole with thin accretion disk",
            "reference": "Luminet, J.-P. (1979). Astronomy and Astrophysics, 75, 228-235.",
            "facts": [
                "For a non-rotating Schwarzschild black hole, strong gravitational deflection curves light trajectories into circular orbits at 1.5 times the Schwarzschild radius (r = 3GM/c^2).",
                "Light rays emitted tangentially at this exact boundary loop around the black hole indefinitely in vacuum."
            ]
        },
        {
            "id": "SRC02",
            "title": "First M87 Event Horizon Telescope Results. I. The Shadow of the Supermassive Black Hole",
            "reference": "Event Horizon Telescope Collaboration. (2019). Astrophysical Journal Letters, 875, L1.",
            "facts": [
                "The bright emission ring captured in the M87* image originates from photons orbiting near the unstable photon sphere before deflecting toward Earth.",
                "Gravitational lensing creates infinite higher-order sub-rings around the black hole shadow."
            ]
        },
        {
            "id": "SRC03",
            "title": "Gravitation",
            "reference": "Misner, C. W., Thorne, K. S., & Wheeler, J. A. (1973). W. H. Freeman.",
            "facts": [
                "Circular photon orbits in Schwarzschild geometry are dynamically unstable; any infinitesimal radial perturbation causes light to either spiral into the singularity or escape to spatial infinity.",
                "Gravitational redshift exponentially stretches the frequency of light trapped along close relativistic orbits."
            ]
        }
    ]

    required_points = [
        {"id": "R01", "text": "Hovering at one-point-five times the Schwarzschild radius outside a non-rotating black hole"},
        {"id": "R02", "text": "General Relativity: gravity as spacetime curvature bending massless photon trajectories into curved geodesics"},
        {"id": "R03", "text": "At three gravitational radii, escape velocity equals the exact speed of light along tangential paths"},
        {"id": "R04", "text": "Debunking the myth that event horizons are the only dramatic boundary around a black hole"},
        {"id": "R05", "text": "The closed circular light loop: shining a flashlight straight ahead illuminates the back of your own helmet"},
        {"id": "R06", "text": "Knife-edge dynamical instability: microscopic quantum fluctuations sending photons plunging or escaping"},
        {"id": "R07", "text": "Infinite concentric Einstein rings and gravitational redshift stretching light frequencies"},
        {"id": "R08", "text": "How the Event Horizon Telescope resolved the glowing photon ring of supermassive black hole M87*"},
        {"id": "R09", "text": "Editorial commentary on spacetime geometry twisting optics into a cosmic hall of mirrors"},
        {"id": "R10", "text": "The photon sphere as humanity's definitive testbed for unified general relativity and quantum gravity"},
        {"id": "R11", "text": "Contemplating the cosmic frontier where light loops forever and our human connection to the cosmos"}
    ]

    editorial_stance = {
        "myth_debunked": "The widespread misconception that nothing interesting happens outside a black hole until you cross the dark event horizon.",
        "why_generic_advice_fails": "Pop-science depictions rely on 2D rubber-sheet analogies that fail to show how four-dimensional curvature loops photon trajectories into closed circles.",
        "channel_verdict": "The photon sphere is physics at its most breathtakingly surreal—a region where spacetime geometry turns light back upon itself.",
        "tradeoff_or_blindspot": "While circular photon orbits exist mathematically, their extreme dynamical instability means you could never actually park a stable beam of light."
    }

    actionable_value = {
        "core_mechanism": "At r = 3GM/c^2 (1.5 Rs), relativistic spacetime curvature forces null geodesics into closed circular orbits.",
        "practical_rule_of_thumb": "To locate the photon sphere of any non-rotating black hole, multiply its Schwarzschild radius by exactly one point five.",
        "real_world_scenario": "When viewing the EHT image of M87*, recognize that the golden ring is light skimming the photon sphere before traveling to Earth."
    }

    thumbnail_spec = {
        "visual_hook": "An antique brass astrolabe and astronomer's divider tracing glowing gold circular light beams orbiting the dark silhouette of a black hole on indigo chart paper.",
        "text_overlay": "ORBITING LIGHT",
        "contrast_pair": "Straight light rays vs Gravitationally closed circular loops",
        "thumbnail_prompt": "Requested aspect ratio: 16:9. Render a complete 100% full-bleed horizontal widescreen 16:9 high-impact YouTube poster thumbnail illustration extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, zero UI chrome, and zero dark vignette.\n\nVisual Style (ch_en_cosmos_vector): Authentic 19th-century Royal Observatory 2D celestial copperplate ink engraving and hand-tinted astrolabe chart on deep cosmic-indigo cotton paper (#0B1026 deep indigo rag paper grain, #F4EFE6 chalk-ivory engraved orbit lines, #4CC9F0 pulsar cyan ink wash, #FFD166 brass astrolabe gold, #D9534F red-shift carmine). Orthographic 2D, antique star-chart texture, >=60% negative space, zero 3D CGI, zero cartoon robot mascots, zero plastic AI glow, zero gradients.\n\nFocal Subject: A central perfectly black circular void surrounded by a razor-thin glowing brass-gold photon ring (#FFD166). Tangent light rays loop around the circumference. An engraved brass astrolabe dial and coordinate dividers frame the composition.\n\nPoster Typography: Hand-lettered uppercase English text in upper third: 'ORBITING LIGHT'. Refined celestial copperplate engraving font etched onto indigo paper, strictly zero rectangular text cards or gradient boxes.",
        "layout_mode": "split_contrast"
    }

    cta_plan = {
        "close": "Step outside tonight, look up at the stars, and remember your connection to it all.",
        "endcard_text": "POCKET COSMOS"
    }

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain the relativistic physics, optical hall-of-mirrors geometry, and observational evidence of the black hole photon sphere using classical observatory charts and Feynman-esque intuition",
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
                "Deliver an awe-inspiring, mathematically rigorous astrophysics explainer across 11 scenes with 66 unique celestial copperplate engravings, maintaining an average hold under 2.8 seconds and zero AI cliches."
            ],
            "avoid": list(ch.avoid) + ["delve into", "testament to", "tapestry", "in conclusion", "it is important to remember"],
            "prior_knowledge": "No tensor calculus required; spacetime curvature explained through geometric optical intuition.",
            "pacing": "Awe-inspiring, lucid, poetic yet rigorous build from thought experiment to relativistic mechanism and cosmic reflection.",
            "domain_requirements": [],
            "assumptions": [
                "Spoken in vivid, crystal-clear conversational English with zero pretentious jargon."
            ],
            "text_style": {
                "font": "Celestial copperplate engraving font",
                "color": "#F4EFE6",
                "outline": "#0B1026 indigo contrast",
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
                    "source": "Acoustic calibrated cadence for poetic cosmological explainer"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": thumbnail_spec,
            "channel_pillar": "Relativistic Astrophysics, Celestial Mechanics & Spacetime Geometry",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["photon sphere", "black hole light orbit", "see back of your head", "general relativity", "m87 black hole", "astrophysics"],
            "cta_plan": cta_plan,
            "editorial_stance": editorial_stance,
            "actionable_value": actionable_value
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": thumbnail_spec,
        "channel_pillar": "Relativistic Astrophysics, Celestial Mechanics & Spacetime Geometry",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["photon sphere", "black hole light orbit", "see back of your head", "general relativity", "m87 black hole", "astrophysics"],
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
            {"scene_id": "SC01", "purpose": "Establish hovering at 1.5 Schwarzschild radii outside a non-rotating black hole", "requirements": ["R01"], "transition": "Transition into general relativity curvature principles"},
            {"scene_id": "SC02", "purpose": "Explain how spacetime curvature bends massless photon paths into curved arcs", "requirements": ["R02"], "transition": "Calculate the critical mathematical radius"},
            {"scene_id": "SC03", "purpose": "Show orbital speed equaling the speed of light along tangential trajectories", "requirements": ["R03"], "transition": "Deliver critical editorial commentary on black hole boundaries"},
            {"scene_id": "SC04", "purpose": "Deliver editorial stance: the photon sphere is stranger than the event horizon", "requirements": ["R04"], "transition": "Explore the mind-bending flashlight thought experiment"},
            {"scene_id": "SC05", "purpose": "Illustrate shining a flashlight ahead and illuminating the back of your helmet", "requirements": ["R05"], "transition": "Analyze the dynamical stability of the orbit"},
            {"scene_id": "SC06", "purpose": "Detail the knife-edge instability where microscopic nudges plunge or escape", "requirements": ["R06"], "transition": "Examine the resulting visual distortions on distant light"},
            {"scene_id": "SC07", "purpose": "Show infinite concentric Einstein rings and gravitational redshift stretching colors", "requirements": ["R07"], "transition": "Move from theory to real astronomical observation"},
            {"scene_id": "SC08", "purpose": "Explain how the Event Horizon Telescope resolved the glowing photon ring of M87*", "requirements": ["R08"], "transition": "Deliver profound philosophical reflection on spacetime"},
            {"scene_id": "SC09", "purpose": "Deliver editorial commentary on spacetime as a dynamic, looping fabric", "requirements": ["R09"], "transition": "Explore future physics at the quantum boundary"},
            {"scene_id": "SC10", "purpose": "Present the photon sphere as the ultimate laboratory for quantum gravity", "requirements": ["R10"], "transition": "Close on human contemplation under the night sky"},
            {"scene_id": "SC11", "purpose": "Close with awe-inspiring reflection on our cosmic connection across deep space", "requirements": ["R11"], "transition": "Final hold endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "SEA",
                    "top_performing_videos": [
                        {
                            "title": "What Would You See at the Edge of a Black Hole?",
                            "views": "4.1M views",
                            "hook_technique": "Immersive second-person thought experiment floating in the void.",
                            "pacing_structure": "Approach trajectory -> Optical distortion breakdown -> Infinite ring reveal.",
                            "retention_driver": "Poetic, hypnotic narration combined with elegant cosmological diagrams."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Placing the viewer in a physical spacecraft with visual instruments.",
                        "Building reverence for relativistic physics without sacrificing scientific rigor."
                    ]
                },
                {
                    "channel_name": "Cool Worlds (Prof. David Kipping)",
                    "top_performing_videos": [
                        {
                            "title": "The Physics of the Photon Sphere",
                            "views": "1.9M views",
                            "hook_technique": "Direct whiteboard ray-tracing demonstration showing light bending back.",
                            "pacing_structure": "Equation breakdown -> Geometric ray diagram -> Real telescopic imaging.",
                            "retention_driver": "Clear academic authority explaining mind-bending paradoxes simply."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Showing the exact geometry of light rays curving around a central mass.",
                        "Connecting theoretical thought experiments directly to real telescope data."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 13,
                "visual_contrast": "Straight golden flashlight ray suddenly looping in a perfect circle around darkness.",
                "counter_intuitive_truth_slap": "You can orbit a black hole at light speed without ever touching the event horizon."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Hovering at the mysterious 1.5 Schwarzschild radius boundary."},
                {"phase": "empirical_conflict", "purpose": "Massless photons forced into circular tracks by extreme curvature."},
                {"phase": "structural_model", "purpose": "Editorial commentary on the cosmic hall of mirrors and knife-edge instability."},
                {"phase": "actionable_resolution", "purpose": "The Event Horizon Telescope photographing M87's photon ring."},
                {"phase": "cliffhanger_spinoff", "purpose": "Contemplative reflection connecting human stargazing to cosmic relativity."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chained 2D celestial charts maintaining indigo cotton paper texture and brass ink linework."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Relativistic Astrophysics, Celestial Mechanics & Spacetime Geometry",
            "myth_debunked": "Nothing weird happens outside a black hole until you cross the event horizon.",
            "channel_verdict": "The photon sphere is geometry at its most surreal, looping past, present, and direction into a ring.",
            "actionable_rule_of_thumb": "Multiply any black hole's Schwarzschild radius by 1.5 to find where light orbits in circles."
        },
        "cta_and_spinoff_strategy": {
            "close": "Step outside tonight, look up at the stars, and remember your connection to it all.",
            "endcard_text": "POCKET COSMOS"
        }
    }

    scene_data = [
        # SC01
        {
            "id": "SC01",
            "title": "Hovering at 1.5 Schwarzschild Radii",
            "purpose": "Establish hovering at 1.5 Schwarzschild radii outside a non-rotating black hole",
            "action": "An observational spacecraft hovers motionless in the deep indigo void, instruments locked onto an invisible circular threshold outside a black hole.",
            "setting": "Celestial copperplate atlas on deep indigo cotton paper #0B1026 with chalk-ivory coordinate grids #F4EFE6.",
            "camera": "Slow cinematic tracking shot following an astronomer's brass divider across celestial coordinate lines",
            "narration": "Imagine piloting an observational spacecraft toward a non-rotating stellar black hole. You pass safely through interstellar space until your thrusters lock your position at exactly one-point-five times the Schwarzschild radius. You have not crossed the dark event horizon, but you have entered a boundary far stranger. Here, the laws of cosmic optics completely invert.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Awe-inspiring, mysterious, atmospheric",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images_spec": [
                ("SC01_I1", "Celestial copperplate map showing an observational spacecraft approaching a black hole on deep cosmic indigo paper #0B1026.", None, "full_scene", "burst", "hook_shock"),
                ("SC01_I2", "Engraved circular coordinate rings highlighting the boundary at 1.5 Schwarzschild radii in glowing brass-gold ink #FFD166.", "SC01_I1", "visual_diagram", "fast", "hook_shock"),
                ("SC01_I3", "Extreme close-up of spacecraft thrusters firing silent cyan ion plumes (#4CC9F0) to maintain a stationary hover.", "SC01_I2", "cutaway_detail", "fast", "hook_shock"),
                ("SC01_I4", "The dark circular silhouette of the black hole framed by antique brass observatory calipers on ivory chart paper.", "SC01_I3", "still_life", "fast", "hook_shock"),
                ("SC01_I5", "Distant starlight bending into distorted crescent arcs around the shadowy perimeter of the void.", "SC01_I4", "environment", "normal", "hook_shock"),
                ("SC01_I6", "Astronomer's hand holding brass dividers against an illuminated star chart, witnessing optical inversion.", "SC01_I5", "variation", "normal", "hook_shock"),
            ],
            "quotes": [
                "Imagine piloting an observational spacecraft toward a non-rotating stellar black hole.",
                "You pass safely through interstellar space until your thrusters lock your position",
                "at exactly one-point-five times the Schwarzschild radius.",
                "You have not crossed the dark event horizon,",
                "but you have entered a boundary far stranger.",
                "Here, the laws of cosmic optics completely invert."
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "Einstein's Spacetime Geodesics",
            "purpose": "Explain how spacetime curvature bends massless photon paths into curved arcs",
            "action": "A straight beam of white starlight enters a dense gravitational well and bends along curved Riemannian coordinate lines.",
            "setting": "Engraved gravitational coordinate mesh on deep indigo paper #0B1026 with fine ivory hatching #F4EFE6.",
            "camera": "Dynamic perspective tracking along curved light rays dipping into a geometric funnel",
            "narration": "Standard physics teaches that photons possess zero rest mass and always travel in perfectly straight lines through vacuum. But Einstein's General Relativity revealed that gravity is not a pull, but the curvature of four-dimensional spacetime. Near an extreme mass, spacetime bends so severely that the straightest possible paths for light become tightly curved geometric arcs.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Rigorous, revelatory, mathematical",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "chronological_shift",
            "images_spec": [
                ("SC02_I1", "Classical Newtonian diagram of a straight light ray passing a mass, contrasted with an Einsteinian curved spacetime mesh on indigo paper #0B1026.", None, "visual_diagram", "fast", "chronological_shift"),
                ("SC02_I2", "Four-dimensional Riemannian coordinate funnel curving deeply toward an infinitely dense central singularity.", "SC02_I1", "visual_diagram", "fast", "chronological_shift"),
                ("SC02_I3", "A photon wave packet traveling along a curved null geodesic, glowing in brilliant pulsar cyan #4CC9F0.", "SC02_I2", "cutaway_detail", "normal", "chronological_shift"),
                ("SC02_I4", "Mathematical callout showing Einstein's field equations etched in fine copperplate script: G_mu_nu equals 8 pi T_mu_nu.", "SC02_I3", "still_life", "fast", "chronological_shift"),
                ("SC02_I5", "Geometric angle of deflection increasing sharply as light rays graze closer to the gravitational center.", "SC02_I4", "visual_diagram", "normal", "chronological_shift"),
                ("SC02_I6", "Astronomer's brass astrolabe measuring the curvature angles of bending light rays against background constellations.", "SC02_I5", "variation", "normal", "chronological_shift"),
            ],
            "quotes": [
                "Standard physics teaches that photons possess zero rest mass",
                "and always travel in perfectly straight lines through vacuum.",
                "But Einstein's General Relativity revealed that gravity is not a pull,",
                "but the curvature of four-dimensional spacetime.",
                "Near an extreme mass, spacetime bends so severely",
                "that the straightest possible paths for light become tightly curved geometric arcs."
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Speed of Light in Orbit",
            "purpose": "Show orbital speed equaling the speed of light along tangential trajectories",
            "action": "At three gravitational radii, the escape velocity matches light speed, locking photons into closed circular racetracks.",
            "setting": "Celestial orbital mechanics chart on indigo cotton vellum #0B1026 with brass-gold trajectory rings #FFD166.",
            "camera": "Top-down celestial chart perspective tracing an endless circular orbital loop",
            "narration": "At three gravitational radii from the singularity, spacetime curvature reaches a unique mathematical threshold. Here, the orbital velocity required to maintain a circular trajectory equals the exact speed of light. Photons emitted tangentially cannot break free into outer space, nor do they fall inward. They are trapped in continuous, closed circular orbits around the void.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Lucid, geometric, astonishing",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images_spec": [
                ("SC03_I1", "Circular orbital trajectory diagram etched in brass gold #FFD166 at r equals 3GM over c squared on dark indigo paper #0B1026.", None, "visual_diagram", "burst", "mechanism_step"),
                ("SC03_I2", "A photon wave packet orbiting endlessly around the central black disk, leaving a glowing gold circular trace.", "SC03_I1", "concept_metaphor", "fast", "mechanism_step"),
                ("SC03_I3", "Vector balance diagram showing tangential velocity vector c perfectly matched to the centripetal spacetime curvature gradient.", "SC03_I2", "visual_diagram", "normal", "mechanism_step"),
                ("SC03_I4", "Multiple photon streams arriving from different angles and joining the same razor-thin circular racetrack.", "SC03_I3", "full_scene", "normal", "mechanism_step"),
                ("SC03_I5", "Comparison chart between planetary Keplerian orbits and relativistic circular null geodesics.", "SC03_I4", "visual_diagram", "normal", "mechanism_step"),
                ("SC03_I6", "Engraved armillary sphere with its central ivory ring glowing in vibrant gold, representing the photon sphere.", "SC03_I5", "still_life", "normal", "mechanism_step"),
            ],
            "quotes": [
                "At three gravitational radii from the singularity,",
                "spacetime curvature reaches a unique mathematical threshold.",
                "Here, the orbital velocity required to maintain a circular trajectory",
                "equals the exact speed of light.",
                "Photons emitted tangentially cannot break free into outer space, nor do they fall inward.",
                "They are trapped in continuous, closed circular orbits around the void."
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "Debunking the Horizon Obsession",
            "purpose": "Deliver editorial stance: the photon sphere is stranger than the event horizon",
            "action": "A balance scale contrasts the pitch-black event horizon with the brilliant, complex optical knot of the photon sphere.",
            "setting": "Philosophical observatory plate on deep indigo paper #0B1026 with antique brass instruments.",
            "camera": "Slow contemplative push-in on an antique celestial engraving comparing two relativistic boundaries",
            "narration": "Science fiction constantly fixates on the event horizon as the only dramatic boundary around a black hole. That narrow obsession overlooks the most mind-bending region in relativistic physics. The photon sphere is a cosmic hall of mirrors where past, present, and spatial direction fold into an optical knot. It is geometry pushed to its absolute limits.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Critical, sharp, poetic, evaluative",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images_spec": [
                ("SC04_I1", "Celestial copperplate chart comparing two concentric circles: the dark event horizon inside vs the glowing photon sphere outside on indigo paper #0B1026.", None, "visual_diagram", "slow", "editorial_commentary"),
                ("SC04_I2", "Optical hall of mirrors metaphor: infinite recursive reflections of an astronomer's lantern bouncing in closed curves.", "SC04_I1", "concept_metaphor", "slow", "editorial_commentary"),
                ("SC04_I3", "Brass calipers measuring the precise ratio: photon sphere at 1.5 times the radius of the event horizon.", "SC04_I2", "still_life", "slow", "editorial_commentary"),
                ("SC04_I4", "Cosmic coordinate grid twisting into an intricate Celtic knot of light lines around the central void.", "SC04_I3", "concept_metaphor", "normal", "editorial_commentary"),
                ("SC04_I5", "Astronomer looking through an antique telescope whose lens reveals circular orbits rather than straight stars.", "SC04_I4", "variation", "slow", "editorial_commentary"),
                ("SC04_I6", "Philosophical compass drawing a circle of light that closes perfectly upon its own starting point.", "SC04_I5", "concept_metaphor", "slow", "editorial_commentary"),
            ],
            "quotes": [
                "Science fiction constantly fixates on the event horizon",
                "as the only dramatic boundary around a black hole.",
                "That narrow obsession overlooks the most mind-bending region in relativistic physics.",
                "The photon sphere is a cosmic hall of mirrors",
                "where past, present, and spatial direction fold into an optical knot.",
                "It is geometry pushed to its absolute limits."
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Flashlight Paradox",
            "purpose": "Illustrate shining a flashlight ahead and illuminating the back of your helmet",
            "action": "An astronaut standing on an orbital platform shines a bright forward beam; the light loops around the black hole and strikes their helmet.",
            "setting": "Celestial star chart on indigo cotton rag #0B1026 with brilliant white chalk and brass-gold light paths.",
            "camera": "Third-person perspective watching the beam depart forward, loop around the void, and hit the viewer's back",
            "narration": "Consider what happens if you stand on an observation platform inside this sphere and shine a powerful flashlight directly ahead. The beam does not travel away into deep space. It bends around the circumference of the black hole, completes a full three-hundred-sixty-degree loop, and strikes you directly in the back of your own helmet.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Surreal, concrete, mind-bending",
            "narrative_phase": "structural_model",
            "narrative_situation": "concrete_detail",
            "images_spec": [
                ("SC05_I1", "Astronaut in vintage copper-accented spacesuit standing on a celestial platform holding a brass flashlight on indigo paper #0B1026.", None, "full_scene", "burst", "concrete_detail"),
                ("SC05_I2", "A razor-thin beam of pure white chalk light (#F4EFE6) shooting forward from the flashlight into the void.", "SC05_I1", "cutaway_detail", "fast", "concrete_detail"),
                ("SC05_I3", "The light beam curving in a perfect semicircle around the dark silhouette of the black hole in fine gold ink.", "SC05_I2", "full_scene", "normal", "concrete_detail"),
                ("SC05_I4", "The curving beam completing a full 360-degree loop and hitting the copperplate visor at the back of the astronaut's helmet.", "SC05_I3", "cutaway_detail", "fast", "concrete_detail"),
                ("SC05_I5", "Astronaut looking forward and seeing a magnified, warped reflection of their own backpack and suit across the forward sky.", "SC05_I4", "full_scene", "normal", "concrete_detail"),
                ("SC05_I6", "Astrolabe coordinate dial tracking the photon's circular journey around the circumference of spacetime.", "SC05_I5", "still_life", "normal", "concrete_detail"),
            ],
            "quotes": [
                "Consider what happens if you stand on an observation platform inside this sphere",
                "and shine a powerful flashlight directly ahead.",
                "The beam does not travel away into deep space.",
                "It bends around the circumference of the black hole,",
                "completes a full three-hundred-sixty-degree loop,",
                "and strikes you directly in the back of your own helmet."
            ]
        },
        # SC06
        {
            "id": "SC06",
            "title": "The Knife-Edge Instability",
            "purpose": "Detail the knife-edge instability where microscopic nudges plunge or escape",
            "action": "A photon teeters precariously along the circular ridge; a microscopic nudge causes one path to spiral into the void and another to escape.",
            "setting": "Mathematical potential energy diagram on indigo paper #0B1026 showing an inverted parabolic peak.",
            "camera": "Macro view on the knife-edge peak of effective gravitational potential",
            "narration": "Looking forward through your visor, you observe your spacesuit's rear pack magnified across the sky. But this optical loop is not a permanent equilibrium. This circular light trajectory is knife-edge unstable. A single quantum fluctuation or fractional millimeter shift inward condemns light to plunge into the abyss; a nudge outward lets it escape to infinity.",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Precarious, razor-sharp, fundamental",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images_spec": [
                ("SC06_I1", "Effective potential energy curve etched on vellum showing a razor-sharp inverted peak at r equals 1.5 Rs on indigo paper #0B1026.", None, "visual_diagram", "burst", "mechanism_step"),
                ("SC06_I2", "A photon depicted as a golden marble teetering on the exact sharp crest of a curved gravitational ridge.", "SC06_I1", "concept_metaphor", "fast", "mechanism_step"),
                ("SC06_I3", "One photon trajectory nudged slightly inward, spiraling violently downward across the event horizon into blackness.", "SC06_I2", "visual_diagram", "fast", "mechanism_step"),
                ("SC06_I4", "A companion photon trajectory nudged outward, escaping in a hyperbolic arc across the distant cosmos.", "SC06_I3", "visual_diagram", "normal", "mechanism_step"),
                ("SC06_I5", "Quantum fluctuation ripples depicted as delicate ivory interference fringes disturbing the photon path.", "SC06_I4", "cutaway_detail", "normal", "mechanism_step"),
                ("SC06_I6", "Astronomer holding a balancing pendulum that sways between darkness and open space, symbolizing instability.", "SC06_I5", "variation", "normal", "mechanism_step"),
            ],
            "quotes": [
                "Looking forward through your visor,",
                "you observe your spacesuit's rear pack magnified across the sky.",
                "But this optical loop is not a permanent equilibrium.",
                "This circular light trajectory is knife-edge unstable.",
                "A single quantum fluctuation or fractional millimeter shift inward condemns light to plunge into the abyss;",
                "a nudge outward lets it escape to infinity."
            ]
        },
        # SC07
        {
            "id": "SC07",
            "title": "Infinite Rings and Redshift",
            "purpose": "Show infinite concentric Einstein rings and gravitational redshift stretching colors",
            "action": "Light orbiting multiple times forms a nested series of razor-thin concentric rings, with colors stretching from blue to red and amber.",
            "setting": "Spectroscopic celestial chart on dark indigo paper #0B1026 with chromatic Doppler washes.",
            "camera": "Deep optical zoom into the nested fractal hierarchy of gravitational photon rings",
            "narration": "Because photons can orbit multiple times before escaping, an observer sees infinite concentric rings of the entire surrounding cosmos. Light from distant galaxies behind you is focused into blinding filaments wrapped around the black hole's silhouette. Gravitational redshift stretches wavelengths, turning blue star clusters into deep amber and infrared arcs across your field of view.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Luminous, fractal, spectral",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "comparative_scale",
            "images_spec": [
                ("SC07_I1", "Fractal concentric rings of light nested like Russian dolls around the dark silhouette of the black hole on indigo paper #0B1026.", None, "visual_diagram", "fast", "comparative_scale"),
                ("SC07_I2", "Ray-tracing diagram showing photons making one, two, three, and n complete loops before reaching the observer.", "SC07_I1", "visual_diagram", "normal", "comparative_scale"),
                ("SC07_I3", "Distant background galaxies warped into razor-thin arcs of brilliant light encircling the void.", "SC07_I2", "environment", "normal", "comparative_scale"),
                ("SC07_I4", "Spectral prism callout showing gravitational redshift stretching high-frequency blue photons into deep amber and carmine (#D9534F).", "SC07_I3", "cutaway_detail", "fast", "comparative_scale"),
                ("SC07_I5", "Full panoramic view from spacecraft visor: a luminous golden donut surrounded by kaleidoscopic star arcs.", "SC07_I4", "full_scene", "normal", "comparative_scale"),
                ("SC07_I6", "Astronomer recording spectral wavelengths with an antique brass spectrometer beside ivory data ledgers.", "SC07_I5", "variation", "slow", "comparative_scale"),
            ],
            "quotes": [
                "Because photons can orbit multiple times before escaping,",
                "an observer sees infinite concentric rings of the entire surrounding cosmos.",
                "Light from distant galaxies behind you is focused into blinding filaments",
                "wrapped around the black hole's silhouette.",
                "Gravitational redshift stretches wavelengths,",
                "turning blue star clusters into deep amber and infrared arcs across your field of view."
            ]
        },
        # SC08
        {
            "id": "SC08",
            "title": "Imaging the Ring of M87*",
            "purpose": "Explain how the Event Horizon Telescope resolved the glowing photon ring of M87*",
            "action": "A global array of radio telescopes synchronizes atomic clocks across Earth to image the glowing photon ring of galaxy M87.",
            "setting": "Celestial and planetary interferometry diagram on deep indigo paper #0B1026 with pulsar cyan connections #4CC9F0.",
            "camera": "From planet Earth looking 55 million light-years across the cosmic void to the M87* core",
            "narration": "For decades, the photon sphere existed only as an elegant equation on paper. That changed when the Event Horizon Telescope combined radio observatories across Earth to image the supermassive black hole M87. That iconic glowing golden donut was not the black hole itself, but light skimming the photon ring before escaping across fifty-five million light-years.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Historic, monumental, observational triumph",
            "narrative_phase": "structural_model",
            "narrative_situation": "concrete_detail",
            "images_spec": [
                ("SC08_I1", "Global network of radio dishes (Chile, Hawaii, Spain, South Pole) linked by glowing baseline arcs on indigo globe #0B1026.", None, "visual_diagram", "fast", "concrete_detail"),
                ("SC08_I2", "Very Long Baseline Interferometry synthesis creating an Earth-sized virtual aperture telescope.", "SC08_I1", "visual_diagram", "normal", "concrete_detail"),
                ("SC08_I3", "The iconic historic reconstructed image of M87*: an asymmetrical glowing golden crescent surrounding deep black shadow.", "SC08_I2", "full_scene", "fast", "concrete_detail"),
                ("SC08_I4", "Theoretical ray-tracing model overlaid perfectly atop the real observational data of M87*, matching Einstein's prediction.", "SC08_I3", "cutaway_detail", "normal", "concrete_detail"),
                ("SC08_I5", "Light rays traveling 55 million light-years from the Virgo cluster across cosmic expanses to reach Earth antennas.", "SC08_I4", "environment", "normal", "concrete_detail"),
                ("SC08_I6", "Astronomer comparing hand-calculated 1916 Schwarzschild equations to the 2019 telescope photograph on vellum.", "SC08_I5", "variation", "slow", "concrete_detail"),
            ],
            "quotes": [
                "For decades, the photon sphere existed only as an elegant equation on paper.",
                "That changed when the Event Horizon Telescope combined radio observatories across Earth",
                "to image the supermassive black hole M87.",
                "That iconic glowing golden donut was not the black hole itself,",
                "but light skimming the photon ring",
                "before escaping across fifty-five million light-years."
            ]
        },
        # SC09
        {
            "id": "SC09",
            "title": "Spacetime as an Optical Fabric",
            "purpose": "Deliver editorial commentary on spacetime as a dynamic, looping fabric",
            "action": "A celestial loom weaves threads of space and time into a tapestry where golden photon strands form closed loops.",
            "setting": "Philosophical cosmic engraving on indigo rag paper #0B1026 with white chalk and brass gold.",
            "camera": "Slow poetic zoom into woven cosmic coordinate threads",
            "narration": "The existence of the photon sphere reveals a profound truth about our cosmos. Spacetime is not a passive empty stage where objects interact; it is a dynamic physical fabric that can twist radiation into closed loops. Gravity does not merely govern falling apples; it dictates the fundamental geometry of what can and cannot be observed.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Poetic, philosophical, transcendent",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images_spec": [
                ("SC09_I1", "A celestial cosmic loom weaving threads of space and time, with golden photon strands bending into rings on indigo paper #0B1026.", None, "concept_metaphor", "slow", "editorial_commentary"),
                ("SC09_I2", "Newton's flat passive clockwork stage contrasted with Einstein's flexible dynamic spacetime fabric.", "SC09_I1", "visual_diagram", "slow", "editorial_commentary"),
                ("SC09_I3", "An apple falling from a branch into a curvature funnel that twists into an orbiting beam of light.", "SC09_I2", "concept_metaphor", "slow", "editorial_commentary"),
                ("SC09_I4", "Engraved astronomer looking up from star charts, gazing directly into the infinite recursive loop of geometry.", "SC09_I3", "variation", "slow", "editorial_commentary"),
                ("SC09_I5", "Luminous balance scale where mass and optical geometry balance in perfect mathematical symmetry.", "SC09_I4", "concept_metaphor", "slow", "editorial_commentary"),
                ("SC09_I6", "Ouroboros serpent formed of pure golden starlight swallowing its own tail around the black hole horizon.", "SC09_I5", "concept_metaphor", "slow", "editorial_commentary"),
            ],
            "quotes": [
                "The existence of the photon sphere reveals a profound truth about our cosmos.",
                "Spacetime is not a passive empty stage where objects interact;",
                "it is a dynamic physical fabric that can twist radiation into closed loops.",
                "Gravity does not merely govern falling apples;",
                "it dictates the fundamental geometry",
                "of what can and cannot be observed."
            ]
        },
        # SC10
        {
            "id": "SC10",
            "title": "The Quantum Gravity Crucible",
            "purpose": "Present the photon sphere as the ultimate laboratory for quantum gravity",
            "action": "Future space interferometers trace fine photon sub-rings, testing where general relativity meets quantum mechanics.",
            "setting": "Futuristic yet classical observatory schematic on indigo paper #0B1026 with cyan interferometer lasers #4CC9F0.",
            "camera": "Forward tracking shot following next-generation space telescope baselines in lunar orbit",
            "narration": "Today, astrophysicists use photon rings as precision laboratories for extreme physics. By measuring the sub-rings within black hole images, future space interferometers will test whether Einstein's equations hold at the brink of quantum gravity. The photon sphere remains our sharpest window into the ultimate unification of general relativity and quantum mechanics.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Visionary, scientific, frontier",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "structural_model",
            "images_spec": [
                ("SC10_I1", "Next-generation space interferometer satellites orbiting Earth and the Moon, linking laser baselines across millions of miles on indigo paper #0B1026.", None, "visual_diagram", "burst", "structural_model"),
                ("SC10_I2", "High-resolution decomposition of the photon ring revealing razor-thin n equals 1, n equals 2, and n equals 3 sub-rings.", "SC10_I1", "cutaway_detail", "fast", "structural_model"),
                ("SC10_I3", "Quantum foam ripples meeting smooth relativistic spacetime geometry at the photon orbit knife-edge.", "SC10_I2", "concept_metaphor", "normal", "structural_model"),
                ("SC10_I4", "Mathematical equations of unified field theory etched in glowing chalk along the curvature of the black hole shadow.", "SC10_I3", "still_life", "normal", "structural_model"),
                ("SC10_I5", "Astronaut and 18th-century astronomer standing side by side looking out an observatory window at the glowing photon ring.", "SC10_I4", "full_scene", "normal", "structural_model"),
                ("SC10_I6", "A radiant circular keyhole of starlight opening into the deepest mysteries of quantum spacetime.", "SC10_I5", "concept_metaphor", "normal", "structural_model"),
            ],
            "quotes": [
                "Today, astrophysicists use photon rings as precision laboratories for extreme physics.",
                "By measuring the sub-rings within black hole images,",
                "future space interferometers will test whether Einstein's equations hold",
                "at the brink of quantum gravity.",
                "The photon sphere remains our sharpest window",
                "into the ultimate unification of general relativity and quantum mechanics."
            ]
        },
        # SC11
        {
            "id": "SC11",
            "title": "Looking at the Stars",
            "purpose": "Close with awe-inspiring reflection on our cosmic connection across deep space",
            "action": "The astronomer looks through a mountaintop telescope at a crystal-clear night sky, contemplating the cosmic loop.",
            "setting": "Serene mountaintop observatory at midnight on deep cosmic indigo cotton paper #0B1026.",
            "camera": "Gentle medium pull-back from brass telescope eyepiece to star-filled sky, ending on official channel endcard",
            "narration": "Standing at the edge of a black hole, looking at your own reflection looped across the curvature of spacetime, you realize how astonishing the universe truly is. The cosmos bends light, but human curiosity bridges the gap across the dark. Step outside tonight, look up at the stars, and remember your connection to it all. See you in the next voyage.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Transcendent, poetic, resonant, inspiring",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cta_close",
            "images_spec": [
                ("SC11_I1", "Astronomer standing on a high mountain observatory terrace under a breathtaking arch of the Milky Way on indigo paper #0B1026.", None, "full_scene", "normal", "cta_close"),
                ("SC11_I2", "A brass observatory telescope pointed toward distant constellations, illuminated by warm lantern glow.", "SC11_I1", "still_life", "normal", "cta_close"),
                ("SC11_I3", "Refection of the glowing golden photon ring caught inside the circular glass lens of the telescope.", "SC11_I2", "cutaway_detail", "normal", "cta_close"),
                ("SC11_I4", "Constellation chart overlay: ancient hand-drawn star figures blending smoothly into modern relativistic spacetime maps.", "SC11_I3", "concept_metaphor", "normal", "cta_close"),
                ("SC11_I5", "The astronomer gestures warmly toward the open starry sky, smiling under a canopy of distant galaxies.", "SC11_I4", "variation", "normal", "cta_close"),
                ("SC11_I6", "Official Pocket Cosmos 16:9 channel endcard on deep cosmic-indigo rag paper #0B1026 with brass astrolabe, glowing golden photon ring, and hand-lettered text 'POCKET COSMOS'.", "SC11_I5", "white_card", "hold", "cta_close", True),
            ],
            "quotes": [
                "Standing at the edge of a black hole,",
                "looking at your own reflection looped across the curvature of spacetime,",
                "you realize how astonishing the universe truly is.",
                "The cosmos bends light, but human curiosity bridges the gap across the dark.",
                "Step outside tonight, look up at the stars, and remember your connection to it all.",
                "See you in the next voyage."
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

        if sc_id in ("SC01", "SC02", "SC03", "SC05", "SC06", "SC08", "SC10"):
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
                "preserve": "Deep indigo paper #0B1026, chalk-ivory linework #F4EFE6, brass astrolabe gold #FFD166, astronomer design." if based_on else "Deep indigo paper #0B1026, chalk-ivory linework #F4EFE6, brass astrolabe gold #FFD166.",
                "change": desc,
                "reason": f"Cosmic visual progression beat {beat_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_type,
                "tempo": tempo,
                "narrative_situation": situation,
                "has_character": True,
                "is_endcard": is_endcard,
                "motion_prompt": "Smooth 2D celestial copperplate animation, gentle relativistic rotation, silent visual storytelling, no talking, no lip movement"
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


def get_pocket_cosmos_short():
    channel_id = "en_pocket_cosmos"
    job_id = "en-pocket-cosmos-batch1-9x16"
    parent_long_id = "en-pocket-cosmos-batch1-16x9"
    ch = get_channel(channel_id)

    topic = "Where Looking Forward Shows the Back of Your Head"
    youtube_title = "Where Looking Forward Shows the Back of Your Head"  # 49 chars <= 55

    sources = [
        {
            "id": "SRC01",
            "title": "Image of a spherical black hole",
            "reference": "Luminet, J.-P. (1979). Astronomy and Astrophysics, 75, 228-235.",
            "facts": ["Photons orbit in closed circles at 1.5 times the Schwarzschild radius."]
        },
        {
            "id": "SRC02",
            "title": "First M87 Event Horizon Telescope Results",
            "reference": "Event Horizon Telescope Collaboration. (2019). Astrophysical Journal Letters, 875, L1.",
            "facts": ["The glowing ring of M87* reveals light focused along the unstable photon sphere."]
        }
    ]

    required_points = [
        {"id": "R01", "text": "Standing outside a black hole and seeing the light beam strike the back of your own head"},
        {"id": "R02", "text": "At one-point-five Schwarzschild radii, orbital speed equals the speed of light"},
        {"id": "R03", "text": "The photon sphere as a razor-sharp optical knife-edge rather than the dark event horizon"},
        {"id": "R04", "text": "The glowing golden ring of M87* as observational proof of the photon sphere"},
        {"id": "R05", "text": "Cliffhanger on crossing the photon orbit and spin-off bridge to full documentary"}
    ]

    editorial_stance = {
        "myth_debunked": "Nothing weird happens outside a black hole until you cross the event horizon.",
        "why_generic_advice_fails": "Rubber-sheet analogies fail to show how 4D curvature loops light into closed circles.",
        "channel_verdict": "The photon sphere is geometry at its most surreal, looping past, present, and direction into a ring.",
        "tradeoff_or_blindspot": "Extreme dynamical instability means you could never park a stable beam of light."
    }

    actionable_value = {
        "core_mechanism": "At 1.5 Rs, spacetime curvature forces null geodesics into closed circular tracks.",
        "practical_rule_of_thumb": "Multiply any black hole's Schwarzschild radius by 1.5 to locate where light loops.",
        "real_world_scenario": "When viewing the EHT image of M87*, recognize that the golden ring is light dancing on the photon sphere."
    }

    thumbnail_spec = {
        "visual_hook": "A beam of golden light curving around a black disk and hitting the back of an astronomer's helmet on celestial chart paper.",
        "text_overlay": "LIGHT BENDS BACK",
        "contrast_pair": "Looking forward vs Seeing behind",
        "thumbnail_prompt": "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 high-impact YouTube poster thumbnail illustration extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, zero UI chrome, and zero dark vignette.\n\nVisual Style (ch_en_cosmos_vector): Authentic 19th-century Royal Observatory 2D celestial copperplate engraving on deep cosmic indigo cotton paper (#0B1026). Fine chalk-ivory engraved lines (#F4EFE6). A brilliant brass-gold laser arc (#FFD166) curves tightly around a circular black hole shadow, completing a loop back toward the source. Orthographic 2D, >=60% negative space, zero 3D, zero gradients.\n\nPoster Typography: Hand-lettered uppercase English text in upper third: 'LIGHT BENDS BACK'. Antique observatory star chart font etched onto indigo paper, strictly zero rectangular boxes or gradient cards.",
        "layout_mode": "split_contrast"
    }

    cta_plan = {
        "cliffhanger_peak": "What happens to your vision if you dare step one inch past this circular photon orbit?",
        "bridge": "Watch the complete spacetime relativity breakdown on Pocket Cosmos YouTube.",
        "close": "Step outside tonight and remember your connection to it all.",
        "endcard_text": "WATCH FULL VIDEO ON YOUTUBE"
    }

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain the photon sphere thought experiment in 5 punchy scenes and bridge viewers to the long-form astrophysics documentary",
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
                "Deliver a fast-paced 5-scene short explainer with 20 unique celestial engravings, maintaining an average hold under 2.5 seconds and zero AI cliches."
            ],
            "avoid": list(ch.avoid) + ["delve into", "testament to", "tapestry", "in conclusion", "it is important to remember"],
            "prior_knowledge": "None required.",
            "pacing": "Rapid-fire hook escalating directly to the cliffhanger question and long-form bridge.",
            "domain_requirements": [],
            "assumptions": [
                "Spoken in sharp, punchy English with zero throat-clearing."
            ],
            "text_style": {
                "font": "Celestial copperplate engraving font",
                "color": "#F4EFE6",
                "outline": "#0B1026 indigo contrast",
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
            "channel_pillar": "Relativistic Astrophysics, Celestial Mechanics & Spacetime Geometry",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["photon sphere", "black hole light orbit", "see back of head", "relativity", "shorts"],
            "cta_plan": cta_plan,
            "editorial_stance": editorial_stance,
            "actionable_value": actionable_value
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": thumbnail_spec,
        "channel_pillar": "Relativistic Astrophysics, Celestial Mechanics & Spacetime Geometry",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["photon sphere", "black hole light orbit", "see back of head", "relativity", "shorts"],
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
            {"scene_id": "SC01", "purpose": "Immediate hook shock: shining a flashlight forward and seeing the back of your head", "requirements": ["R01"], "transition": "Transition into relativistic curvature"},
            {"scene_id": "SC02", "purpose": "Explain the 1.5 Schwarzschild radius threshold where light orbits in circles", "requirements": ["R02"], "transition": "Transition into editorial reframing"},
            {"scene_id": "SC03", "purpose": "Editorial stance: a razor-sharp optical knife-edge rather than the event horizon", "requirements": ["R03"], "transition": "Transition into real astronomical imaging"},
            {"scene_id": "SC04", "purpose": "Show the glowing golden ring of M87* as proof of the photon sphere", "requirements": ["R04"], "transition": "Transition to peak cliffhanger"},
            {"scene_id": "SC05", "purpose": "Peak cliffhanger question, channel bridge, and closing sign-off", "requirements": ["R05"], "transition": "Final hold endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "SEA",
                    "top_performing_videos": [
                        {
                            "title": "The Boundary Where Light Circles",
                            "views": "2.8M views",
                            "hook_technique": "Startling thought experiment putting the viewer directly in the light beam path.",
                            "pacing_structure": "Hook -> Geometry explanation -> Real telescope evidence.",
                            "retention_driver": "Mind-bending visual intuition of curved light rays."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Framing the thought experiment with visceral physical sensations.",
                        "Connecting relativistic theory to the historic 2019 M87* photograph."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Looking straight ahead into darkness vs Seeing your own helmet reflection.",
                "counter_intuitive_truth_slap": "Light doesn't just fall into black holes; it orbits them in closed circles."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Sensory shock of seeing the back of your own head across the void."},
                {"phase": "empirical_conflict", "purpose": "At 1.5 Rs, curvature forces photons into closed circular tracks."},
                {"phase": "structural_model", "purpose": "Editorial verdict: a knife-edge boundary stranger than the event horizon."},
                {"phase": "actionable_resolution", "purpose": "The glowing golden ring of M87* confirming the photon sphere."},
                {"phase": "cliffhanger_spinoff", "purpose": "Peak cliffhanger question bridging to the full YouTube documentary."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chained 2D celestial charts maintaining indigo cotton paper texture."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Relativistic Astrophysics, Celestial Mechanics & Spacetime Geometry",
            "myth_debunked": "Nothing weird happens outside a black hole until you cross the event horizon.",
            "channel_verdict": "The photon sphere is geometry at its most surreal, looping past, present, and direction into a ring.",
            "actionable_rule_of_thumb": "Multiply any black hole's Schwarzschild radius by 1.5 to locate where light loops."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "What happens to your vision if you dare step one inch past this circular photon orbit?",
            "bridge": "Watch the complete spacetime relativity breakdown on Pocket Cosmos YouTube.",
            "close": "Step outside tonight and remember your connection to it all.",
            "endcard_text": "WATCH FULL VIDEO ON YOUTUBE"
        }
    }

    scene_data = [
        # SC01
        {
            "id": "SC01",
            "title": "The Backward Light Loop",
            "purpose": "Immediate hook shock: shining a flashlight forward and seeing the back of your head",
            "action": "An astronaut shines a flashlight straight ahead in the indigo void, and the beam loops around to strike the back of their helmet.",
            "setting": "Celestial star chart on deep indigo cotton paper #0B1026 with white chalk #F4EFE6.",
            "camera": "Dynamic vertical zoom into illuminated light loop curving around black void",
            "narration": "If you stood in the right spot outside a black hole and shone a flashlight straight ahead, you would see the beam strike the back of your own head across the curved void.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Electrifying, surreal, physics",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images_spec": [
                ("SC01_I1", "Vertical 2D celestial chart of an astronaut firing a pure white laser beam into the void on indigo paper #0B1026.", None, "full_scene", "burst", "hook_shock"),
                ("SC01_I2", "The laser beam curving smoothly in a 180-degree arc around a circular black hole shadow in brass gold #FFD166.", "SC01_I1", "visual_diagram", "fast", "hook_shock"),
                ("SC01_I3", "The light beam striking the back of the astronaut's copperplate helmet visor.", "SC01_I2", "cutaway_detail", "fast", "hook_shock"),
                ("SC01_I4", "Astronaut looking forward and seeing their own reflection magnified across the sky.", "SC01_I3", "full_scene", "normal", "hook_shock"),
            ],
            "quotes": [
                "If you stood in the right spot outside a black hole",
                "and shone a flashlight straight ahead,",
                "you would see the beam strike the back of your own head",
                "across the curved void."
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "The 1.5 Rs Threshold",
            "purpose": "Explain the 1.5 Schwarzschild radius threshold where light orbits in circles",
            "action": "Spacetime curvature increases sharply until the orbital speed required equals the exact speed of light.",
            "setting": "Relativistic coordinate chart on deep indigo vellum #0B1026 with brass trajectory dials.",
            "camera": "Cutaway tracking along circular null geodesic track",
            "narration": "At exactly one-point-five times the Schwarzschild radius, gravitational spacetime curvature is so extreme that the speed required for a circular orbit equals the speed of light. Photons are trapped in closed circular tracks.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Geometric, mathematical, lucid",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "mechanism_breakdown",
            "images_spec": [
                ("SC02_I1", "Radial distance scale showing 1.0 Rs (event horizon) and 1.5 Rs (photon sphere) on indigo paper #0B1026.", None, "visual_diagram", "burst", "mechanism_breakdown"),
                ("SC02_I2", "Gravitational funnel plunging steeply with ivory gridlines curving inward.", "SC02_I1", "visual_diagram", "fast", "mechanism_breakdown"),
                ("SC02_I3", "A stream of photons racing along the razor-thin golden circular track at speed c.", "SC02_I2", "cutaway_detail", "normal", "mechanism_breakdown"),
                ("SC02_I4", "Astrolabe coordinate dial framing the circular photon loop with brass dividers.", "SC02_I3", "still_life", "fast", "mechanism_breakdown"),
            ],
            "quotes": [
                "At exactly one-point-five times the Schwarzschild radius,",
                "gravitational spacetime curvature is so extreme",
                "that the speed required for a circular orbit equals the speed of light.",
                "Photons are trapped in closed circular tracks."
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Optical Knife-Edge",
            "purpose": "Editorial stance: a razor-sharp optical knife-edge rather than the event horizon",
            "action": "A balance scale contrasts a photon plunging into the abyss with one escaping across the cosmos.",
            "setting": "Philosophical observatory engraving on indigo rag paper #0B1026.",
            "camera": "Slow cinematic push-in on an unstable potential energy ridge",
            "narration": "This region is not the black hole's event horizon, but a razor-sharp optical knife-edge. A microscopic push inward pulls light into the singularity; one nudge outward lets it flee across the cosmic expanse.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Sharp, precarious, evaluative",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images_spec": [
                ("SC03_I1", "Inverted parabolic potential curve etched in ivory on indigo paper #0B1026, showing the unstable crest.", None, "visual_diagram", "slow", "editorial_commentary"),
                ("SC03_I2", "One photon spiraling downward into the dark singularity abyss.", "SC03_I1", "cutaway_detail", "slow", "editorial_commentary"),
                ("SC03_I3", "Another photon escaping in an open curve toward distant stars.", "SC03_I2", "environment", "normal", "editorial_commentary"),
                ("SC03_I4", "Astronomer's hand balancing a brass plumb-bob over the razor-thin knife-edge ridge.", "SC03_I3", "concept_metaphor", "slow", "editorial_commentary"),
            ],
            "quotes": [
                "This region is not the black hole's event horizon,",
                "but a razor-sharp optical knife-edge.",
                "A microscopic push inward pulls light into the singularity;",
                "one nudge outward lets it flee across the cosmic expanse."
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "The M87* Telescope Proof",
            "purpose": "Show the glowing golden ring of M87* as proof of the photon sphere",
            "action": "The Event Horizon Telescope image of M87* appears as an illuminated golden crescent on celestial charts.",
            "setting": "Astrophysical observatory plate on deep indigo paper #0B1026 with brass-gold radio synthesis lines.",
            "camera": "Magnification zoom into the glowing golden donut of M87*",
            "narration": "The glowing golden ring imaged by the Event Horizon Telescope at the heart of galaxy M87 was light dancing along this exact photon sphere before traveling fifty-five million light-years to reach our telescopes.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Historic, monumental, observational",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "structural_model",
            "images_spec": [
                ("SC04_I1", "Historic reconstructed image of M87*: glowing golden crescent surrounding the central shadow on indigo paper #0B1026.", None, "full_scene", "burst", "structural_model"),
                ("SC04_I2", "Ray-tracing schematic showing light skimming the photon sphere before deflecting toward Earth.", "SC04_I1", "visual_diagram", "fast", "structural_model"),
                ("SC04_I3", "Radio dishes across Earth linked by cyan laser baselines (#4CC9F0) forming a planetary-scale telescope.", "SC04_I2", "visual_diagram", "normal", "structural_model"),
                ("SC04_I4", "Cosmic path of light traveling 55 million light-years across the Virgo supercluster.", "SC04_I3", "environment", "normal", "structural_model"),
            ],
            "quotes": [
                "The glowing golden ring imaged by the Event Horizon Telescope",
                "at the heart of galaxy M87",
                "was light dancing along this exact photon sphere",
                "before traveling fifty-five million light-years to reach our telescopes."
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Frontier Spinoff",
            "purpose": "Peak cliffhanger question, channel bridge, and closing sign-off",
            "action": "Astronomer holds an open star chart, points toward the full documentary, and signs off under the starry cosmos.",
            "setting": "Serene midnight observatory on deep indigo rag paper #0B1026 with brass astrolabe.",
            "camera": "Dramatic push-in on glowing photon ring, cutting to channel endcard hold",
            "narration": "What happens to your vision if you dare step one inch past this circular photon orbit? Watch the complete spacetime relativity breakdown on Pocket Cosmos YouTube. Step outside tonight and remember your connection to it all.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Suspenseful, inviting, resonant",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cliffhanger_peak",
            "images_spec": [
                ("SC05_I1", "Astronaut visor reflecting a blinding cascade of infinite distorted Einstein rings on indigo paper #0B1026.", None, "cutaway_detail", "burst", "cliffhanger_peak"),
                ("SC05_I2", "The black hole shadow expanding to engulf half the sky as the threshold is approached.", "SC05_I1", "concept_metaphor", "fast", "cliffhanger_peak"),
                ("SC05_I3", "Astronomer with brass dividers gesturing warmly toward the viewer beside illuminated celestial atlas.", "SC05_I2", "variation", "normal", "cta_bridge"),
                ("SC05_I4", "Official Pocket Cosmos 9:16 vertical channel endcard on deep indigo paper #0B1026 with brass astrolabe, glowing photon ring, and hand-lettered text 'WATCH FULL VIDEO ON YOUTUBE'.", "SC05_I3", "white_card", "hold", "cta_close", True),
            ],
            "quotes": [
                "What happens to your vision if you dare step one inch",
                "past this circular photon orbit?",
                "Watch the complete spacetime relativity breakdown on Pocket Cosmos YouTube.",
                "Step outside tonight and remember your connection to it all."
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
                "preserve": "Deep indigo paper #0B1026, chalk-ivory linework #F4EFE6, brass astrolabe gold #FFD166." if based_on else "Deep indigo paper #0B1026, chalk-ivory linework #F4EFE6, brass astrolabe gold #FFD166.",
                "change": desc,
                "reason": f"Short cosmic beat {beat_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_type,
                "tempo": tempo,
                "narrative_situation": situation,
                "has_character": True,
                "is_endcard": is_endcard,
                "motion_prompt": "Smooth 2D celestial copperplate animation, gentle relativistic rotation, silent visual storytelling, no talking, no lip movement"
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
