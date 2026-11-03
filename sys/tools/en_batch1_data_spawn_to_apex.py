"""Data definitions for Channel 3: Spawn to Apex (en_wait_how / en_spawn_to_apex).

Long Job: sys/runs/en-spawn-to-apex-batch1-16x9
Short Job: sys/runs/en-spawn-to-apex-batch1-9x16
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


PRESERVE_SPAWN_STYLE = (
    "Authentic 2D Maria Sibylla Merian and natural-history museum metamorphosis lithograph and dip-pen watercolor plate on warm "
    "specimen vellum #F6F0DD, fine lithographic dip-pen ink #1A1D24, deep bioluminescent teal wash #2E6F65, "
    "chrysalis amber #D97941, cellular carmine #8C3B4A, nocturnal indigo #1D3557, chronological metamorphosis stages "
    "(Egg -> Larval Instar -> Translucent Chrysalis Cutaway -> Adult Moth) with brass magnifying-lens callouts, "
    "orthographic 2D, >=60% negative space, tactile scientific vellum plate texture, zero 3D CGI, zero cartoon stickers, zero gradients"
)

MOTION_SUFFIX = "silent visual storytelling, no talking, no lip movement"


def make_sta_image(
    img_id: str,
    desc: str,
    change: str,
    reason: str,
    tempo: str,
    situation: str,
    motion_action: str = "Tactile natural-history metamorphosis plate camera movement",
    has_character: bool = True,
    is_endcard: bool = False,
    shot_type: str = "full_scene",
) -> Dict[str, Any]:
    m_prompt = f"Tactile 2D scientific metamorphosis animation. {motion_action.strip()}, transitioning smoothly into next frame, {MOTION_SUFFIX}"
    return {
        "id": img_id,
        "description": desc,
        "character_ids": ["CH01"] if has_character else [],
        "based_on": None,
        "preserve": PRESERVE_SPAWN_STYLE,
        "change": change,
        "reason": reason,
        "visible_text": [],
        "kind": "scene",
        "shot_type": shot_type,
        "tempo": tempo,
        "narrative_situation": situation,
        "has_character": has_character,
        "is_endcard": is_endcard,
        "motion_prompt": m_prompt,
    }


def make_sta_beat(
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
        "focus": {"x": 0.5, "y": 0.5 if is_endcard else 0.0},
        "tempo": tempo,
        "narrative_situation": situation,
    }
    if is_endcard:
        b["is_endcard"] = True
    return b


def build_spawn_to_apex_long_data() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_wait_how"
    job_id = "en-spawn-to-apex-batch1-16x9"
    youtube_title = "Why a Caterpillar Dissolves Yet Keeps Its Memory"
    topic = "Inside the Chrysalis: Why a Caterpillar Completely Dissolves Into Genetic Soup—Yet Remembers Its Past Life"

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Curious adults, biology lovers, and viewers hooked on bizarre chronological life-cycle transformations",
        "goal": "Explain the biochemical reality of caterpillar liquefaction inside the chrysalis, how imaginal discs rebuild adult anatomy, and the neuroanatomical preservation of larval memories",
        "video_type": "metamorphosis_chronicle",
        "duration": {
            "min_seconds": 150.0,
            "max_seconds": 210.0
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Day One inside chrysalis debunking the myth of a sleeping caterpillar peacefully sprouting wings"},
            {"id": "R02", "text": "Cellular autolysis as caspases and digestive enzymes liquefy muscles, gut, and fat into nutrient soup"},
            {"id": "R03", "text": "The microscopic survivors: imaginal discs dormant since the embryonic egg stage"},
            {"id": "R04", "text": "Editorial commentary on complete metamorphosis as nature's most radical body rebuild"},
            {"id": "R05", "text": "Imaginal disc proliferation drinking protein broth to assemble compound eyes, antennae, and wings"},
            {"id": "R06", "text": "The neurological paradox: how memories persist if brain tissue dissolves into liquid broth"},
            {"id": "R07", "text": "The Georgetown University conditioning experiment training hornworms to fear ethyl acetate vapor"},
            {"id": "R08", "text": "Editorial commentary on the shocking test result where adult moths retain larval odor aversion"},
            {"id": "R09", "text": "Synaptic preservation revealing mushroom-body neural circuits surviving liquefaction intact"},
            {"id": "R10", "text": "Day Fourteen emergence: pumping hemolymph into wings, drying chitin, and taking flight"},
            {"id": "R11", "text": "Holometabolous evolutionary triumph dividing life cycles into feeding and reproduction, and closing CTA"}
        ],
        "language": "en",
        "tone": "Riveting, chronological, wonder-filled, lucid, documentary-grade biological storytelling",
        "style": PRESERVE_SPAWN_STYLE,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Retention of Memory Through Metamorphosis in Manduca sexta",
                "reference": "Blackiston, D. J., Casey, E. S., & Weiss, M. R. (2008). PLOS ONE.",
                "facts": [
                    "Tobacco hornworm larvae trained with mild electrical shocks to avoid ethyl acetate odor retained that aversion as adult moths after complete metamorphosis.",
                    "Memory retention is specific to training during late larval instars when adult mushroom-body neuroblasts mature."
                ]
            },
            {
                "id": "SRC02",
                "title": "Cellular Autolysis and Imaginal Disc Development in Holometabolous Insects",
                "reference": "Gilbert, L. I. (2012). Insect Molecular Biology and Biochemistry. Academic Press.",
                "facts": [
                    "Caspase-mediated programmed cell death dissolves the majority of larval tissues into an amino acid-rich soup inside the pupal casing.",
                    "Imaginal discs remain biochemically isolated from autolytic digestive enzymes during pupation."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": True,
                "voice": "OmniVoice_EnWaitHow",
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deliver mind-bending scientific revelation on how memories survive cellular liquefaction inside the chrysalis"
            ],
            "avoid": [
                "Childish cartoon mascots",
                "Clickbait fake biology",
                "Skipping stages of the chronological life cycle"
            ],
            "prior_knowledge": "Accessible to curious adults without biochemistry prerequisites.",
            "pacing": "Chronological Day-1 to Day-14 timeline, lucid mechanistic progression, zero filler.",
            "speech_rates": {
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.1,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Translucent chrysalis cutaway showing liquefied golden soup with glowing neural discs inside",
                "text_overlay": "MEMORY IN SOUP",
                "contrast_pair": "Dissolving caterpillar tissue vs Preserved synaptic memory circuits",
                "thumbnail_prompt": "18th-century Maria Sibylla Merian metamorphosis plate on warm specimen vellum #F6F0DD. Translucent cutaway of a monarch chrysalis showing internal golden organic fluid #D97941 with suspended cellular discs. Glowing microscopic neural brain circuits highlighted in bioluminescent teal #2E6F65 survive intact amid dissolving tissue. Fine lithographic dip-pen ink #1A1D24, carmine wash #8C3B4A. Bold hand-lettered uppercase text in upper third: 'MEMORY IN SOUP'. Tactile vellum texture, >=60% negative space, zero 3D CGI.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "A caterpillar simply rests asleep inside the chrysalis while slowly growing wings and adult legs.",
                "why_generic_advice_fails": "Assuming gradual transformation misses the brutal biochemical reality of total self-liquefaction.",
                "channel_verdict": "Metamorphosis is not a peaceful nap but controlled biological suicide followed by cellular resurrection.",
                "tradeoff_or_blindspot": "Liquefying the entire body eliminates larval maintenance costs but requires an impossible memory vault."
            },
            "actionable_value": {
                "core_mechanism": "Preserving core synaptic circuits while completely rebuilding all peripheral biological hardware from raw amino acids.",
                "practical_rule_of_thumb": "During massive systemic redesign, identify and insulate core memory structures while liquefying obsolete legacy systems.",
                "real_world_scenario": "Software architects mirror imaginal discs when refactoring legacy codebases, preserving core database schemas while rewriting frontends."
            },
            "channel_pillar": "Extreme metamorphosis & life cycles",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["caterpillar metamorphosis", "chrysalis", "biology", "insect memory", "science documentary", "nature"],
            "cta_plan": {
                "close": "Follow our next extreme metamorphosis chronicle on Spawn to Apex.",
                "endcard_text": "SPAWN TO APEX"
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Translucent chrysalis cutaway showing liquefied golden soup with glowing neural discs inside",
            "text_overlay": "MEMORY IN SOUP",
            "contrast_pair": "Dissolving caterpillar tissue vs Preserved synaptic memory circuits",
            "thumbnail_prompt": "18th-century Maria Sibylla Merian metamorphosis plate on warm specimen vellum #F6F0DD. Translucent cutaway of a monarch chrysalis showing internal golden organic fluid #D97941 with suspended cellular discs. Glowing microscopic neural brain circuits highlighted in bioluminescent teal #2E6F65 survive intact amid dissolving tissue. Fine lithographic dip-pen ink #1A1D24, carmine wash #8C3B4A. Bold hand-lettered uppercase text in upper third: 'MEMORY IN SOUP'. Tactile vellum texture, >=60% negative space, zero 3D CGI.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Extreme metamorphosis & life cycles",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["caterpillar metamorphosis", "chrysalis", "biology", "insect memory", "science documentary", "nature"],
        "cta_plan": {
            "close": "Follow our next extreme metamorphosis chronicle on Spawn to Apex.",
            "endcard_text": "SPAWN TO APEX"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": "Natural history metamorphosis chronicler",
            "bridge_templates": [
                "Watch the complete Egg-to-Apex metamorphosis chronicle on Spawn to Apex YouTube."
            ],
            "close_templates": [
                "Follow our next extreme metamorphosis chronicle on Spawn to Apex."
            ],
            "endcard_text": "SPAWN TO APEX",
            "banned_cta_phrases": [
                "don't forget to like",
                "hit the bell",
                "smash that like",
                "like and subscribe",
                "subscribe to the channel"
            ]
        },
        "editorial_stance": {
            "myth_debunked": "A caterpillar simply rests asleep inside the chrysalis while slowly growing wings and adult legs.",
            "why_generic_advice_fails": "Assuming gradual transformation misses the brutal biochemical reality of total self-liquefaction.",
            "channel_verdict": "Metamorphosis is not a peaceful nap but controlled biological suicide followed by cellular resurrection.",
            "tradeoff_or_blindspot": "Liquefying the entire body eliminates larval maintenance costs but requires an impossible memory vault."
        },
        "actionable_value": {
            "core_mechanism": "Preserving core synaptic circuits while completely rebuilding all peripheral biological hardware from raw amino acids.",
            "practical_rule_of_thumb": "During massive systemic redesign, identify and insulate core memory structures while liquefying obsolete legacy systems.",
            "real_world_scenario": "Software architects mirror imaginal discs when refactoring legacy codebases, preserving core database schemas while rewriting frontends."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Debunk the peaceful sleep myth on Day One of pupation", "requirements": ["R01"], "transition": "Reveal the internal enzymatic dissolution"},
            {"scene_id": "SC02", "purpose": "Explain caspase enzymatic autolysis melting muscles and gut", "requirements": ["R02"], "transition": "Introduce the microscopic blueprint survivors"},
            {"scene_id": "SC03", "purpose": "Show imaginal discs present since the egg stage surviving the melt", "requirements": ["R03"], "transition": "Transition to editorial stance on radical transformation"},
            {"scene_id": "SC04", "purpose": "Provide sharp editorial stance on metamorphosis as controlled suicide", "requirements": ["R04"], "transition": "Pivoting to the assembly of adult structures"},
            {"scene_id": "SC05", "purpose": "Show imaginal discs proliferating by drinking the nutrient broth", "requirements": ["R05"], "transition": "Transition to the central neurological paradox"},
            {"scene_id": "SC06", "purpose": "Pose the riddle of how memories survive brain liquefaction", "requirements": ["R06"], "transition": "Introducing the Georgetown University experiment"},
            {"scene_id": "SC07", "purpose": "Detail the ethyl acetate shock conditioning on hornworm caterpillars", "requirements": ["R07"], "transition": "Revealing the adult moth avoidance results"},
            {"scene_id": "SC08", "purpose": "Editorial analysis of memory retention across complete metamorphosis", "requirements": ["R08"], "transition": "Uncovering the neuroanatomical survival mechanism"},
            {"scene_id": "SC09", "purpose": "Illustrate mushroom-body synaptic preservation during brain remodeling", "requirements": ["R09"], "transition": "Advancing timeline to Day Fourteen emergence"},
            {"scene_id": "SC10", "purpose": "Depict adult moth emerging, pumping hemolymph, and drying wings", "requirements": ["R10"], "transition": "Concluding with deep evolutionary triumph"},
            {"scene_id": "SC11", "purpose": "Deliver holometabolous evolutionary verdict and channel closing call to action", "requirements": ["R11"], "transition": "End of chronicle"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Deep Look (KQED)",
                    "top_performing_videos": [
                        {
                            "title": "What's Really Inside a Pupa?",
                            "views": "4.9M views",
                            "hook_technique": "Macro-cinematography puncturing common cartoon misconceptions.",
                            "pacing_structure": "Myth busting -> Cellular autolysis -> Imaginal discs -> Emergence.",
                            "retention_driver": "Visceral sensory cutaways of the golden liquid broth inside pupal shell."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Framing the chrysalis as a vat of digestive enzyme soup.",
                        "Clear anatomical diagrams showing imaginal discs as blueprint seeds."
                    ]
                },
                {
                    "channel_name": "Ze Frank",
                    "top_performing_videos": [
                        {
                            "title": "True Facts: Insect Metamorphosis",
                            "views": "7.2M views",
                            "hook_technique": "Hilarious yet deeply factual biological narrative delivery.",
                            "pacing_structure": "Bizarre premise -> Experimental proof -> Astonished philosophical takeaway.",
                            "retention_driver": "The genuine wonder that an adult remembers what terrified it as a larva."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Highlighting the absurdity of liquefying your brain yet keeping your memories.",
                        "Focus on the Georgetown University shock-odor conditioning experiment."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_words": 16,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Plump crawling caterpillar vs Translucent pupa containing liquefied golden soup",
                "counter_intuitive_truth_slap": "If you slice open a chrysalis on Day four, you will not find a developing butterfly—you will find an enzyme-dissolved genetic soup."
            },
            "narrative_progression_arc": [
                {"phase": "myth_puncture", "purpose": "Debunking the peaceful sleeping caterpillar myth on Day One."},
                {"phase": "cellular_autolysis", "purpose": "Digestive enzymes melt muscles, gut, and fat reserves into soup."},
                {"phase": "imaginal_resurrection", "purpose": "Dormant imaginal blueprint discs awaken and drink the broth."},
                {"phase": "georgetown_proof", "purpose": "Odor-shock experiments prove memories survive total liquefaction."},
                {"phase": "synaptic_vault", "purpose": "Mushroom body synaptic pathways persist intact into the adult moth."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential Maria Sibylla Merian metamorphosis lithograph plates on vellum."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Extreme metamorphosis & life cycles",
            "myth_debunked": "A caterpillar simply sprouts wings while taking a peaceful nap.",
            "channel_verdict": "Metamorphosis requires complete biological suicide while insulating core synaptic memory circuits.",
            "actionable_rule_of_thumb": "During massive architectural redesign, isolate core memory data while rebuilding peripheral systems."
        },
        "cta_and_spinoff_strategy": {
            "close": "Follow our next extreme metamorphosis chronicle on Spawn to Apex.",
            "endcard_text": "SPAWN TO APEX"
        }
    }

    # 11 Scenes for Long Video
    scenes = [
        # SC01
        {
            "id": "SC01",
            "title": "Day One: Shattering the Metamorphosis Myth",
            "purpose": "Debunk the peaceful sleep myth on Day One of pupation",
            "action": "A caterpillar anchors itself to a twig and forms a chrysalis, cutaway reveals internal enzymes activating",
            "setting": "Natural history specimen vellum with antique brass naturalist loupe",
            "camera": "Macro cutaway through translucent green chrysalis wall",
            "narration": "Children are taught a comforting fairytale: a caterpillar enters its chrysalis, takes a peaceful nap, and gently sprouts colorful wings. The biochemical truth is infinitely more brutal. If you slice open a chrysalis on Day Four, you will not find a half-formed insect; you will discover a bubbling vat of self-digesting genetic soup.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Provocative, revelatory, cinematic",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images": [
                make_sta_image(
                    "SC01_I1",
                    "Maria Sibylla Merian style metamorphosis plate on warm specimen vellum #F6F0DD. Plump green caterpillar suspended beneath a twig spinning its silk button in fine dip-pen ink #1A1D24.",
                    "Plump caterpillar spinning silk button beneath twig",
                    "Establishing opening caterpillar pupation SC01_I1",
                    "burst", "hook_shock"
                ),
                make_sta_image(
                    "SC01_I2",
                    "Naturalist lithograph plate. Caterpillar skin splitting along dorsal midline to reveal gleaming jade-green chrysalis shell, amber resin accents #D97941.",
                    "Caterpillar skin splitting to reveal chrysalis",
                    "The dramatic skin shed revealing pupa SC01_I2",
                    "burst", "hook_shock"
                ),
                make_sta_image(
                    "SC01_I3",
                    "Anatomical cutaway plate on vellum #F6F0DD. Fully sealed chrysalis with translucent cutaway window showing internal caterpillar anatomy bathed in teal wash #2E6F65.",
                    "Cutaway window into newly sealed chrysalis",
                    "Initial internal baseline before melt SC01_I3",
                    "fast", "hook_shock"
                ),
                make_sta_image(
                    "SC01_I4",
                    "Microscopic chemical etching. Tiny enzyme droplet symbols multiplying rapidly inside tissues, labeled 'AUTOLYTIC CASPASES' in delicate cursive calligraphy.",
                    "Enzyme symbols multiplying inside tissues",
                    "Revealing internal biochemical activation SC01_I4",
                    "fast", "hook_shock"
                ),
                make_sta_image(
                    "SC01_I5",
                    "Macro plate of internal liquefaction. Caterpillar muscle fibers dissolving into amorphous golden broth #D97941 with floating cellular debris in dip-pen detail.",
                    "Muscle fibers dissolving into golden broth",
                    "Visualizing the start of body melt SC01_I5",
                    "normal", "hook_shock"
                ),
                make_sta_image(
                    "SC01_I6",
                    "Field naturalist codex plate. Stickman anatomist peers through brass microscope at sealed pupa, gesturing in astonishment at the fluid state inside.",
                    "Stickman examining fluid state inside pupa",
                    "Hook climax: genetic soup reality confirmed SC01_I6",
                    "normal", "hook_shock"
                ),
            ],
            "beats": [
                make_sta_beat("SC01_B1", "SC01_I1", "Cite comforting fairytale", "Children are taught a comforting fairytale:", "burst", "hook_shock"),
                make_sta_beat("SC01_B2", "SC01_I2", "Describe peaceful nap myth", "a caterpillar enters its chrysalis, takes a peaceful nap, and gently sprouts colorful wings.", "burst", "hook_shock"),
                make_sta_beat("SC01_B3", "SC01_I3", "State brutal biochemical truth", "The biochemical truth is infinitely more brutal.", "fast", "hook_shock"),
                make_sta_beat("SC01_B4", "SC01_I4", "Challenge Day Four expectation", "If you slice open a chrysalis on Day Four,", "fast", "hook_shock"),
                make_sta_beat("SC01_B5", "SC01_I5", "Deny half-formed insect", "you will not find a half-formed insect;", "normal", "hook_shock"),
                make_sta_beat("SC01_B6", "SC01_I6", "Proclaim self-digesting soup", "you will discover a bubbling vat of self-digesting genetic soup.", "normal", "hook_shock"),
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "Cellular Autolysis: Melting from Within",
            "purpose": "Explain caspase enzymatic autolysis melting muscles, gut, and fat into soup",
            "action": "Digestive enzymes flood the caterpillar's body, dissolving organs into nutrient soup",
            "setting": "Microscopic histological cutaway on aged specimen vellum",
            "camera": "Deep microscopic zoom tracking cellular lysis and tissue breakdown",
            "narration": "Within forty-eight hours of pupation, the caterpillar initiates a violent, controlled cascade of biological self-destruction. Specialized programmed death enzymes called caspases flood every single tissue layer. The massive chewing mouthparts, sixteen crawling prolegs, and sprawling internal digestive tract are completely autolyzed from the inside out, turning into a rich amino-acid organic slurry.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Precise, biochemical, visceral",
            "narrative_phase": "lived_friction",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sta_image(
                    "SC02_I1",
                    "Histological vellum plate on #F6F0DD paper. Cross-section of caterpillar digestive gut surrounded by cascading enzyme droplets in deep cellular carmine #8C3B4A.",
                    "Digestive gut surrounded by cascading enzymes",
                    "Setting the autolytic dissolution scene SC02_I1",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC02_I2",
                    "Microscopic cellular diagram. Chewing jaw muscle bundles breaking apart into individual cell membranes under enzymatic digestion, fine dip-pen stippling #1A1D24.",
                    "Jaw muscle bundles breaking apart into cells",
                    "Showing physical muscle disintegration SC02_I2",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC02_I3",
                    "Anatomical plate of larval leg resorption. The sixteen fleshy prolegs with microscopic crochet hooks melting into smooth translucent fluid #D97941.",
                    "Prolegs melting into translucent fluid",
                    "Visualizing limb autolysis SC02_I3",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC02_I4",
                    "Biochemical slurry diagram. Golden amino acid molecules and peptide chains floating densely in suspension inside pupal shell, teal accents #2E6F65.",
                    "Suspension of golden amino acids and peptide chains",
                    "Depicting the nutrient slurry soup SC02_I4",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC02_I5",
                    "Naturalist codex plate. Stickman anatomist uses glass pipette to sample translucent golden broth, recording protein density in specimen ledger.",
                    "Stickman sampling golden broth with pipette",
                    "Confirming protein density of broth SC02_I5",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC02_I6",
                    "Full pupal cutaway on specimen vellum. The entire caterpillar interior now completely fluid, enclosed safely within tough outer chitin shell, paper #F6F0DD.",
                    "Entire pupa interior completely liquefied",
                    "Total cellular autolysis achieved SC02_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sta_beat("SC02_B1", "SC02_I1", "State 48-hour timeline", "Within forty-eight hours of pupation,", "fast", "mechanism_step"),
                make_sta_beat("SC02_B2", "SC02_I2", "Name self-destruction process", "the caterpillar initiates a violent, controlled cascade of biological self-destruction.", "fast", "mechanism_step"),
                make_sta_beat("SC02_B3", "SC02_I3", "Identify caspase enzymes", "Specialized programmed death enzymes called caspases flood every single tissue layer.", "normal", "mechanism_step"),
                make_sta_beat("SC02_B4", "SC02_I4", "List dissolving organs", "The massive chewing mouthparts, sixteen crawling prolegs, and sprawling internal digestive tract", "normal", "mechanism_step"),
                make_sta_beat("SC02_B5", "SC02_I5", "Describe internal autolysis", "are completely autolyzed from the inside out,", "fast", "mechanism_step"),
                make_sta_beat("SC02_B6", "SC02_I6", "Conclude amino-acid slurry", "turning into a rich amino-acid organic slurry.", "normal", "mechanism_step"),
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Blueprint Survivors: Imaginal Discs",
            "purpose": "Show imaginal discs present since the egg stage surviving the melt",
            "action": "Microscopic imaginal discs remain untouched by digestive enzymes, floating in the broth",
            "setting": "Microscopic view inside golden pupal broth on specimen vellum",
            "camera": "High-magnification lens isolating glowing cellular discs floating in liquid",
            "narration": "Amid this catastrophic cellular massacre, tiny clusters of dormant cells steadfastly refuse to dissolve. Known as imaginal discs, these microscopic blueprint clusters were embedded inside the caterpillar since the day it hatched from its egg. Shielded by unique chemical barriers, each disc holds the complete dormant instructions to assemble one specific adult organ.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Wonder-filled, architectural, precise",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sta_image(
                    "SC03_I1",
                    "Microscopic anatomical plate on vellum #F6F0DD. Multiple flat disk-shaped cellular clusters floating untouched in amber broth, glowing in bioluminescent teal #2E6F65.",
                    "Flat cellular discs floating untouched in broth",
                    "Introducing the resilient imaginal discs SC03_I1",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC03_I2",
                    "Timeline codex diagram. Tracing imaginal discs from tiny dots inside microscopic egg, through larval instars, into the pupa with fine dip-pen calligraphy #1A1D24.",
                    "Timeline tracing discs from egg through larva",
                    "Proving presence since embryonic origin SC03_I2",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC03_I3",
                    "Histological membrane study. Chemical barrier surrounding imaginal disc repelling surrounding caspase digestive enzymes, cellular carmine accents #8C3B4A.",
                    "Protective chemical barrier repelling enzymes",
                    "Explaining biochemical disc insulation SC03_I3",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC03_I4",
                    "Anatomical blueprint plate. Separate labelled imaginal discs for compound eyes, segmented antennae, long nectar proboscis, and six jointed adult legs.",
                    "Labelled discs for eyes, antennae, and legs",
                    "Cataloging organ blueprint assignments SC03_I4",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC03_I5",
                    "Macro plate of wing discs. Paired flat wing discs unfolding microscopic vascular folds within the amber soup, nocturnal indigo wash #1D3557.",
                    "Paired wing discs unfolding vascular folds",
                    "Focusing on wing disc preparation SC03_I5",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC03_I6",
                    "Naturalist codex plate. Stickman observer sketches the constellation of imaginal discs floating inside pupa, labeling them 'EMBRYONIC ARCHITECTS' in ledger.",
                    "Stickman cataloging disc constellation in pupa",
                    "Synthesizing dormant blueprint concept SC03_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sta_beat("SC03_B1", "SC03_I1", "Frame cellular massacre", "Amid this catastrophic cellular massacre,", "normal", "mechanism_step"),
                make_sta_beat("SC03_B2", "SC03_I2", "Introduce surviving clusters", "tiny clusters of dormant cells steadfastly refuse to dissolve.", "normal", "mechanism_step"),
                make_sta_beat("SC03_B3", "SC03_I3", "Name imaginal discs", "Known as imaginal discs, these microscopic blueprint clusters", "normal", "mechanism_step"),
                make_sta_beat("SC03_B4", "SC03_I4", "State presence since egg", "were embedded inside the caterpillar since the day it hatched from its egg.", "normal", "mechanism_step"),
                make_sta_beat("SC03_B5", "SC03_I5", "Highlight chemical shield", "Shielded by unique chemical barriers,", "fast", "mechanism_step"),
                make_sta_beat("SC03_B6", "SC03_I6", "Conclude organ instructions", "each disc holds the dormant instructions to assemble one specific adult organ.", "normal", "mechanism_step"),
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "Editorial Stance: Controlled Resurrection",
            "purpose": "Provide sharp editorial stance on metamorphosis as controlled biological suicide",
            "action": "A philosophical codex plate examining metamorphosis as radical biological deconstruction",
            "setting": "Natural history philosophical codex plate on aged specimen vellum",
            "camera": "Static reflective presentation with brass calipers pointing to life-cycle wheel",
            "narration": "Metamorphosis is often trivialized as gentle decorative magic, but it represents nature's most radical evolutionary engineering sacrifice. To transition from an earthbound crawling machine into an agile airborne flyer, the organism systematically disassembles its physical identity. It commits controlled biological suicide so its dormant blueprint discs can execute a miraculous bodily resurrection.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Philosophical, profound, sharp",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                make_sta_image(
                    "SC04_I1",
                    "Philosophical metamorphosis codex plate on #F6F0DD paper. An Ouroboros ring of caterpillar transforming into chrysalis soup and emerging as winged moth in India ink #1A1D24.",
                    "Ouroboros metamorphosis life-cycle wheel",
                    "Framing radical transformation cycle SC04_I1",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC04_I2",
                    "Naturalist codex study. Stickman observer in pith helmet examines life-cycle wheel with brass divider, crossing out trivial 'magic' labels with dark red ink #8C3B4A.",
                    "Stickman rejecting trivial magic explanations",
                    "Editorial stance on engineering sacrifice SC04_I2",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC04_I3",
                    "Contrast plate comparing heavy crawling machinery with ultra-light winged aerodynamics, teal wash #2E6F65 and chrysalis amber #D97941.",
                    "Mechanical comparison: crawling vs winged flight",
                    "Illustrating why deconstruction is needed SC04_I3",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC04_I4",
                    "Conceptual dissection plate. Dissolving caterpillar silhouette overlaid with blueprint schematic of adult moth, fine dip-pen hatching on vellum.",
                    "Dissolving caterpillar overlaid with moth blueprint",
                    "Visualizing total physical identity shift SC04_I4",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC04_I5",
                    "Lithographic plate with calligraphic motto: 'CONTROLLED BIOLOGICAL SUICIDE, CELLULAR RESURRECTION', framed by botanical specimen borders.",
                    "Calligraphic banner defining biological suicide",
                    "Channel verdict on controlled rebirth SC04_I5",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC04_I6",
                    "Quiet specimen plate. The sealed chrysalis hanging suspended in solitude, completely quiet on outside while violent recreation unfolds within.",
                    "Chrysalis suspended quietly on specimen branch",
                    "Contrasting outer peace with inner storm SC04_I6",
                    "slow", "editorial_commentary"
                ),
            ],
            "beats": [
                make_sta_beat("SC04_B1", "SC04_I1", "Reject decorative magic", "Metamorphosis is often trivialized as gentle decorative magic,", "slow", "editorial_commentary"),
                make_sta_beat("SC04_B2", "SC04_I2", "Frame radical engineering sacrifice", "but it represents nature's most radical evolutionary engineering sacrifice.", "slow", "editorial_commentary"),
                make_sta_beat("SC04_B3", "SC04_I3", "State locomotive transition", "To transition from an earthbound crawling machine into an agile airborne flyer,", "slow", "editorial_commentary"),
                make_sta_beat("SC04_B4", "SC04_I4", "Describe identity disassembly", "the organism systematically disassembles its physical identity.", "slow", "editorial_commentary"),
                make_sta_beat("SC04_B5", "SC04_I5", "Name controlled biological suicide", "It commits controlled biological suicide", "slow", "editorial_commentary"),
                make_sta_beat("SC04_B6", "SC04_I6", "Conclude total resurrection", "so its dormant blueprint discs can execute a miraculous bodily resurrection.", "slow", "editorial_commentary"),
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "Proliferation: Drinking the Broth",
            "purpose": "Show imaginal discs proliferating by drinking the nutrient broth",
            "action": "Imaginal discs absorb dissolved proteins, rapidly multiplying and folding into adult organs",
            "setting": "Internal chrysalis cavity bustling with rapid cellular growth",
            "camera": "Time-lapse sequence showing rapid cell multiplication and organ formation",
            "narration": "By Day Six, the imaginal discs awaken into hyperactive cellular proliferation. Using the dissolved amino acid soup as free raw building material, the discs consume the nutrient broth to divide and multiply at breakneck speed. Within days, flat discs fold and expand into faceted compound eyes, delicate feathery antennae, and multi-jointed walking legs.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Kinetic, rapid, miraculous",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sta_image(
                    "SC05_I1",
                    "Microscopic time-lapse plate on #F6F0DD paper. Imaginal disc cells actively dividing via mitosis, absorbing surrounding amber broth droplets #D97941.",
                    "Imaginal disc cells dividing and absorbing broth",
                    "Showing cellular proliferation beginning SC05_I1",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC05_I2",
                    "Anatomical cutaway of developing head. Eye discs curving and assembling thousands of hexagonal ommatidia lenses in bioluminescent teal wash #2E6F65.",
                    "Eye discs assembling hexagonal ommatidia lenses",
                    "Detailing compound eye construction SC05_I2",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC05_I3",
                    "Macro plate of antennae formation. Feathery sensory branches unfurling like tiny fern fronds within the liquid broth, fine dip-pen linework #1A1D24.",
                    "Feathery antennae unfurling within liquid broth",
                    "Visualizing sensory organ morphogenesis SC05_I3",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC05_I4",
                    "Anatomical study of adult legs. Slender jointed legs extending from thoracic discs, equipped with delicate tarsal claws, cellular carmine accents #8C3B4A.",
                    "Slender jointed adult legs extending from discs",
                    "Showing adult locomotive structure emergence SC05_I4",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC05_I5",
                    "Wing expansion plate on specimen vellum. Folded embryonic wing pads inflating and vascularizing with branching veins, nocturnal indigo wash #1D3557.",
                    "Embryonic wing pads inflating with branching veins",
                    "Illustrating wing organogenesis SC05_I5",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC05_I6",
                    "Full chrysalis internal plate. The golden soup now mostly consumed and converted into the fully formed anatomical structures of an adult moth inside the shell.",
                    "Internal soup converted into adult moth anatomy",
                    "Completing the structural transformation SC05_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sta_beat("SC05_B1", "SC05_I1", "State Day Six awakening", "By Day Six, the imaginal discs awaken into hyperactive proliferation.", "fast", "mechanism_step"),
                make_sta_beat("SC05_B2", "SC05_I2", "Explain broth consumption", "Using the dissolved amino acid soup as free raw building material,", "normal", "mechanism_step"),
                make_sta_beat("SC05_B3", "SC05_I3", "Describe cell division", "the discs consume the nutrient broth to divide and multiply at breakneck speed.", "normal", "mechanism_step"),
                make_sta_beat("SC05_B4", "SC05_I4", "Detail compound eye formation", "Within days, flat discs fold and expand into faceted compound eyes,", "normal", "mechanism_step"),
                make_sta_beat("SC05_B5", "SC05_I5", "Detail feathery antennae", "delicate feathery antennae,", "fast", "mechanism_step"),
                make_sta_beat("SC05_B6", "SC05_I6", "Conclude jointed legs", "and multi-jointed walking legs.", "normal", "mechanism_step"),
            ]
        },
        # SC06
        {
            "id": "SC06",
            "title": "The Neurological Paradox: Melting the Brain",
            "purpose": "Pose the riddle of how memories survive brain liquefaction",
            "action": "Anatomical cutaway of caterpillar brain dissolving, posing the central memory riddle",
            "setting": "Cranial neuroanatomical plate on aged specimen vellum",
            "camera": "Macro zoom on insect brain and nervous system",
            "narration": "Yet this complete cellular melt poses an impossible neurological paradox that baffled science for centuries. Memory in living creatures is stored in delicate physical synaptic connections between neurons. If the caterpillar's brain dissolves into liquid broth alongside its digestive tract, how could any memory of its past life survive into the adult moth?",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Intriguing, paradoxical, mysterious",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sta_image(
                    "SC06_I1",
                    "Neuroanatomical plate on #F6F0DD paper. Detailed sketch of caterpillar central nervous system with subesophageal ganglion in fine India ink #1A1D24.",
                    "Caterpillar central nervous system anatomy",
                    "Establishing larval neurological baseline SC06_I1",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC06_I2",
                    "Microscopic synaptic diagram. Dendrites and synaptic clefts transmitting chemical neurotransmitters, highlighted in glowing teal #2E6F65.",
                    "Microscopic synaptic connections storing memory",
                    "Explaining physical memory storage basis SC06_I2",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC06_I3",
                    "Dramatic dissolution etching. Neural fibers uncoupling and breaking apart amid golden autolytic fluid, amber wash #D97941.",
                    "Neural fibers breaking apart in autolytic fluid",
                    "Visualizing brain tissue liquefaction SC06_I3",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC06_I4",
                    "Philosophical question plate. A question mark formed from dissolving neural filaments floating inside chrysalis, cellular carmine accents #8C3B4A.",
                    "Question mark formed from dissolving neural threads",
                    "Posing the central memory paradox SC06_I4",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC06_I5",
                    "Field naturalist codex plate. Stickman neuroscientist holds magnifying glass over brain model, pointing toward the seeming impossibility of memory retention.",
                    "Stickman pondering memory retention riddle",
                    "Framing scientific skepticism SC06_I5",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC06_I6",
                    "Split contrast plate. On left, crawling caterpillar eating leaf; on right, flying moth, separated by liquid chrysalis void on specimen vellum #F6F0DD.",
                    "Split view linking caterpillar memory to flying moth",
                    "Setting up empirical laboratory test SC06_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sta_beat("SC06_B1", "SC06_I1", "State neurological paradox", "Yet this complete cellular melt poses an impossible neurological paradox that baffled science for centuries.", "normal", "mechanism_step"),
                make_sta_beat("SC06_B2", "SC06_I2", "Explain physical memory storage", "Memory in living creatures is stored in delicate physical synaptic connections between neurons.", "normal", "mechanism_step"),
                make_sta_beat("SC06_B3", "SC06_I3", "Describe brain liquefaction", "If the caterpillar's brain dissolves into liquid broth", "normal", "mechanism_step"),
                make_sta_beat("SC06_B4", "SC06_I4", "Compare with digestive tract", "alongside its digestive tract,", "fast", "mechanism_step"),
                make_sta_beat("SC06_B5", "SC06_I5", "Ask how memory survives", "how could any memory of its past life", "normal", "mechanism_step"),
                make_sta_beat("SC06_B6", "SC06_I6", "Conclude adult survival riddle", "survive into the adult moth?", "normal", "mechanism_step"),
            ]
        },
        # SC07
        {
            "id": "SC07",
            "title": "The Georgetown Shock Experiment",
            "purpose": "Detail the ethyl acetate shock conditioning on hornworm caterpillars",
            "action": "Scientists at Georgetown University condition caterpillars with ethyl acetate odor and mild electrical pulses",
            "setting": "Laboratory apparatus plate with glass Y-maze and electrical electrodes",
            "camera": "Overhead technical presentation of the scientific conditioning apparatus",
            "narration": "To answer this perplexing biological riddle, pioneering researchers at Georgetown University conducted a landmark conditioning experiment with tobacco hornworm caterpillars. They exposed fifth-instar larvae to the pungent chemical scent of ethyl acetate, pairing the odor with harmless but unpleasant electrical pulses. The crawling caterpillars rapidly learned to associate the sharp chemical smell with immediate danger.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Empirical, methodical, scientific",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sta_image(
                    "SC07_I1",
                    "Scientific laboratory codex plate on #F6F0DD paper. Georgetown University apparatus showing glass conditioning chamber and chemical vials in fine dip-pen linework #1A1D24.",
                    "Georgetown laboratory apparatus and chemical vials",
                    "Introducing historic conditioning experiment SC07_I1",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC07_I2",
                    "Technical drawing of ethyl acetate molecule with chemical formula CH3COOCH2CH3, emitting vapor wisps tinted in pale amber wash #D97941.",
                    "Ethyl acetate molecular formula and vapor wisps",
                    "Specifying the chemical odor trigger SC07_I2",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC07_I3",
                    "Experimental conditioning plate. Fifth-instar tobacco hornworm crawling across wired grid, mild electrical pulses indicated by fine blue zig-zag lines #2E6F65.",
                    "Caterpillar on wired grid receiving mild shock",
                    "Depicting associative shock conditioning SC07_I3",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC07_I4",
                    "Behavioral response diagram. Caterpillar rearing back and turning away from ethyl acetate vapor dispenser, demonstrating learned aversion behavior.",
                    "Caterpillar flinching away from odor dispenser",
                    "Confirming successful larval memory formation SC07_I4",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC07_I5",
                    "Naturalist codex plate. Stickman researcher in lab coat logs conditioning trials with clipboard, checking off successful avoidance responses.",
                    "Stickman researcher recording conditioning trials",
                    "Documenting empirical experimental rigor SC07_I5",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC07_I6",
                    "Transition plate on vellum. The conditioned caterpillars entering pupation, sealing into brown chrysalises inside incubation rack, nocturnal indigo #1D3557.",
                    "Conditioned caterpillars pupating in incubation rack",
                    "Setting the stage for metamorphosis test SC07_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sta_beat("SC07_B1", "SC07_I1", "Introduce Georgetown researchers", "To answer this perplexing biological riddle,", "normal", "mechanism_step"),
                make_sta_beat("SC07_B2", "SC07_I2", "Name hornworm caterpillars", "pioneering researchers at Georgetown University conducted a landmark conditioning experiment with tobacco hornworm caterpillars.", "normal", "mechanism_step"),
                make_sta_beat("SC07_B3", "SC07_I3", "Detail ethyl acetate exposure", "They exposed fifth-instar larvae to the pungent chemical scent of ethyl acetate,", "normal", "mechanism_step"),
                make_sta_beat("SC07_B4", "SC07_I4", "Describe electrical pairing", "pairing the odor with harmless but unpleasant electrical pulses.", "fast", "mechanism_step"),
                make_sta_beat("SC07_B5", "SC07_I5", "Show learned association", "The crawling caterpillars rapidly learned to associate", "normal", "mechanism_step"),
                make_sta_beat("SC07_B6", "SC07_I6", "Conclude danger memory", "the sharp chemical smell with immediate danger.", "normal", "mechanism_step"),
            ]
        },
        # SC08
        {
            "id": "SC08",
            "title": "Editorial Stance: The Impossible Proof",
            "purpose": "Provide editorial analysis of the shocking proof that adult moths remember",
            "action": "Adult moths placed in a Y-maze overwhelmingly avoid the trained odor weeks later",
            "setting": "Glass Y-maze olfactory choice arena on specimen vellum",
            "camera": "Overhead view of Y-maze tracking moth flight choice",
            "narration": "Weeks later, after the caterpillars had completely liquefied and rebuilt themselves into winged adults, scientists tested them inside an olfactory Y-maze arena. The resulting data stunned the entire scientific community. Over seventy-five percent of the adult moths vigorously avoided the ethyl acetate chamber. Learned memory had survived the complete cellular death of the larval body.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Astonished, authoritative, triumphant",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                make_sta_image(
                    "SC08_I1",
                    "Technical glass Y-maze diagram on #F6F0DD paper. Moths released at base, left arm emitting ethyl acetate, right arm emitting clean air, India ink #1A1D24.",
                    "Glass Y-maze olfactory choice arena diagram",
                    "Establishing empirical choice test setup SC08_I1",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC08_I2",
                    "Flight trajectory plate. Adult Manduca sexta moth fluttering up the maze, sharply veering away from the chemical scent arm into clean air, teal wash #2E6F65.",
                    "Adult moth veering sharply away from odor arm",
                    "Visualizing active adult avoidance flight SC08_I2",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC08_I3",
                    "Statistical codex chart on specimen vellum. Bar graph showing 78% avoidance in trained group versus 50% random choice in control group with dip-pen calligraphy.",
                    "Statistical bar graph proving 78% avoidance",
                    "Documenting statistically robust proof SC08_I3",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC08_I4",
                    "Field naturalist plate. Stickman scientist raises hands in astonishment beside Y-maze results, noting validation of larval memory persistence.",
                    "Stickman scientist celebrating unexpected breakthrough",
                    "Editorial stance on scientific astonishment SC08_I4",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC08_I5",
                    "Conceptual engraving. Ghostly silhouette of caterpillar mind glowing within the brain of a soaring winged moth, chrysalis amber #D97941.",
                    "Caterpillar mind silhouette glowing inside moth brain",
                    "Visualizing unbroken mental identity SC08_I5",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC08_I6",
                    "Specimen plate on rag paper. Beautiful mounted adult tobacco hornworm moth with outstretched wings, labeled 'SURVIVOR OF THE BROTH' in ledger.",
                    "Mounted adult moth with outstretched wings",
                    "Channel verdict on memory surviving liquefaction SC08_I6",
                    "slow", "editorial_commentary"
                ),
            ],
            "beats": [
                make_sta_beat("SC08_B1", "SC08_I1", "State weeks-later testing", "Weeks later, after the caterpillars had completely liquefied and rebuilt themselves into winged adults,", "slow", "editorial_commentary"),
                make_sta_beat("SC08_B2", "SC08_I2", "Introduce Y-maze test", "scientists tested them inside an olfactory Y-maze arena.", "slow", "editorial_commentary"),
                make_sta_beat("SC08_B3", "SC08_I3", "State scientific stun", "The resulting data stunned the entire scientific community.", "slow", "editorial_commentary"),
                make_sta_beat("SC08_B4", "SC08_I4", "Cite 75% avoidance", "Over seventy-five percent of the adult moths vigorously avoided the ethyl acetate chamber.", "slow", "editorial_commentary"),
                make_sta_beat("SC08_B5", "SC08_I5", "Highlight memory survival", "Learned memory had survived", "slow", "editorial_commentary"),
                make_sta_beat("SC08_B6", "SC08_I6", "Conclude cellular death triumph", "the complete cellular death of the larval body.", "slow", "editorial_commentary"),
            ]
        },
        # SC09
        {
            "id": "SC09",
            "title": "Synaptic Vault: The Mushroom Bodies",
            "purpose": "Illustrate mushroom-body synaptic preservation during brain remodeling",
            "action": "Neuroanatomical cross-section reveals mushroom body synaptic circuits insulated from liquefaction",
            "setting": "Microscopic neuroanatomical diagram on aged specimen vellum",
            "camera": "Deep microscopic zoom into brain mushroom body neuropil",
            "narration": "Neuroanatomists soon discovered the physical secret behind this miracle. While the vast majority of larval brain neurons are digested, specific neural circuits in specialized structures called mushroom bodies remain protected. These ancient memory-processing centers are insulated from autolysis, carrying learned synaptic connections intact across the pupal melt into the adult brain.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Revelatory, neuroanatomical, lucid",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sta_image(
                    "SC09_I1",
                    "Cranial neuroanatomical cutaway on #F6F0DD paper. Adult moth head dissection showing brain lobes with prominent twin mushroom body structures highlighted in teal #2E6F65.",
                    "Adult moth brain showing twin mushroom bodies",
                    "Isolating the memory mushroom bodies SC09_I1",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC09_I2",
                    "Microscopic mushroom body diagram. Kenyon cells and dense calyx neuropil outlined in fine iron-gall dip-pen cross-hatching #1A1D24.",
                    "Microscopic Kenyon cells and calyx neuropil",
                    "Detailing the physical synaptic memory architecture SC09_I2",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC09_I3",
                    "Biochemical insulation study. Protective glial sheath surrounding mushroom body neurons, preventing caspase enzymes from entering, cellular carmine #8C3B4A.",
                    "Protective glial sheath shielding memory neurons",
                    "Explaining neuroprotection during autolysis SC09_I3",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC09_I4",
                    "Synaptic continuity diagram. Synapses formed during caterpillar stage persisting unbroken as new adult optic nerves connect alongside them, nocturnal indigo #1D3557.",
                    "Larval synapses persisting as adult nerves connect",
                    "Demonstrating bridge between past and future SC09_I4",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC09_I5",
                    "Field naturalist plate. Stickman anatomist gestures toward illuminated memory pathway, marvelling at nature's biological data-preservation protocol.",
                    "Stickman tracing illuminated memory pathway",
                    "Synthesizing the synaptic vault discovery SC09_I5",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC09_I6",
                    "Full brain reconstruction plate on specimen vellum. The fully remodeled adult brain gleaming with integrated larval memory centers, amber resin accents #D97941.",
                    "Fully remodeled adult brain with memory centers",
                    "Neural metamorphosis successfully completed SC09_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sta_beat("SC09_B1", "SC09_I1", "Announce physical secret", "Neuroanatomists soon discovered the physical secret behind this miracle.", "normal", "mechanism_step"),
                make_sta_beat("SC09_B2", "SC09_I2", "Contrast digested neurons", "While the vast majority of larval brain neurons are digested,", "normal", "mechanism_step"),
                make_sta_beat("SC09_B3", "SC09_I3", "Name mushroom bodies", "specific neural circuits in specialized structures called mushroom bodies remain protected.", "normal", "mechanism_step"),
                make_sta_beat("SC09_B4", "SC09_I4", "Define memory centers", "These ancient memory-processing centers are insulated from autolysis,", "fast", "mechanism_step"),
                make_sta_beat("SC09_B5", "SC09_I5", "State intact synaptic carryover", "carrying learned synaptic connections intact", "normal", "mechanism_step"),
                make_sta_beat("SC09_B6", "SC09_I6", "Conclude adult brain integration", "across the pupal melt into the adult brain.", "normal", "mechanism_step"),
            ]
        },
        # SC10
        {
            "id": "SC10",
            "title": "Day Fourteen: Flight and Resurrected Wings",
            "purpose": "Depict adult moth emerging, pumping hemolymph, and drying wings",
            "action": "Chrysalis splits open, adult moth crawls out, pumps wings with hemolymph, and flies",
            "setting": "Specimen branch bathed in warm golden twilight",
            "camera": "Slow macro tracking following the emergence and wing inflation",
            "narration": "On Day Fourteen, the chrysalis splits along its dorsal seam. An adult hawkmoth crawls out into evening twilight, its shrivelled wings expanding as hydraulic pressure pumps hemolymph through intricate branching veins. As chitin hardens beneath the evening breeze, the resurrected creature takes flight, bearing vivid memories forged inside a crawling body it no longer possesses.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Triumphant, majestic, poetic",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sta_image(
                    "SC10_I1",
                    "Maria Sibylla Merian style plate on #F6F0DD paper. Chrysalis splitting along dorsal suture, damp adult moth head and antennae protruding into twilight air.",
                    "Chrysalis splitting as adult moth head emerges",
                    "The dramatic moment of physical emergence SC10_I1",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC10_I2",
                    "Macro plate of moth clinging to empty pupal husk. Soft wrinkled wing pads hanging limp while abdominal muscles contract to generate fluid pressure.",
                    "Moth clinging to empty husk with wrinkled wings",
                    "Preparing for hydraulic wing inflation SC10_I2",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC10_I3",
                    "Hydraulic wing inflation sequence. Hemolymph fluid surging through delicate wing veins, unrolling flat wings like vibrant silk sails, teal wash #2E6F65.",
                    "Hemolymph pumping through wing veins unrolling wings",
                    "Visualizing hydraulic wing expansion SC10_I3",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC10_I4",
                    "Detailed anatomical plate. Chitin cuticle drying and hardening in evening air, intricate scale patterns shimmering in nocturnal indigo #1D3557 and amber #D97941.",
                    "Chitin cuticle drying and scales shimmering",
                    "Hardening into flight-ready aerodynamic structure SC10_I4",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC10_I5",
                    "Dynamic action etching on vellum. The adult hawkmoth takes flight, powerful wings beating at forty strokes per second in misty evening air.",
                    "Adult hawkmoth taking flight with rapid wing beats",
                    "Achieving majestic aerial mastery SC10_I5",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC10_I6",
                    "Naturalist codex plate. Stickman observer watches the flying moth navigate twilight flowers, amazed that a dissolved caterpillar now navigates the sky.",
                    "Stickman watching moth navigate twilight flowers",
                    "The complete physical resurrection realized SC10_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sta_beat("SC10_B1", "SC10_I1", "State Day Fourteen seam split", "On Day Fourteen, the chrysalis splits along its dorsal seam.", "normal", "mechanism_step"),
                make_sta_beat("SC10_B2", "SC10_I2", "Describe emergence into twilight", "An adult hawkmoth crawls out into evening twilight,", "normal", "mechanism_step"),
                make_sta_beat("SC10_B3", "SC10_I3", "Detail hydraulic hemolymph pump", "its shrivelled wings expanding as hydraulic pressure pumps hemolymph through intricate branching veins.", "normal", "mechanism_step"),
                make_sta_beat("SC10_B4", "SC10_I4", "Describe chitin hardening", "As chitin hardens beneath the evening breeze,", "fast", "mechanism_step"),
                make_sta_beat("SC10_B5", "SC10_I5", "Show flight takeoff", "the resurrected creature takes flight,", "normal", "mechanism_step"),
                make_sta_beat("SC10_B6", "SC10_I6", "Conclude memory carryover", "bearing vivid memories forged inside a crawling body it no longer possesses.", "normal", "mechanism_step"),
            ]
        },
        # SC11
        {
            "id": "SC11",
            "title": "Holometabolous Triumph: Life-Cycle Division",
            "purpose": "Deliver holometabolous evolutionary verdict and channel closing call to action",
            "action": "Wide evolutionary view showing how dividing the life cycle into feeding and flying conquered Earth",
            "setting": "Naturalist museum archive with antique specimen cases and twilight landscape",
            "camera": "Slow cinematic pull-back revealing evolutionary diversity of holometabolous insects",
            "narration": "This radical division of life into two separate lives explains why complete metamorphosis accounts for eighty percent of all insect species on Earth. The larva does nothing but feed; the adult does nothing but navigate and reproduce. In nature, destruction is merely the price of evolutionary perfection. Follow our next extreme metamorphosis chronicle on Spawn to Apex.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Grand, evolutionary, authoritative",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cta_bridge",
            "images": [
                make_sta_image(
                    "SC11_I1",
                    "Grand evolutionary plate on #F6F0DD paper. Tree of life diagram showing holometabolous insects dominating eighty percent of terrestrial biodiversity in dip-pen ink.",
                    "Tree of life diagram showing insect dominance",
                    "Establishing eighty percent biodiversity dominance SC11_I1",
                    "normal", "cta_bridge"
                ),
                make_sta_image(
                    "SC11_I2",
                    "Dual-stage efficiency study. Plump caterpillar eating leaf on bottom; sleek adult moth pollinating orchid on top, teal #2E6F65 and amber #D97941.",
                    "Dual-stage efficiency: feeding larva vs flying adult",
                    "Explaining evolutionary life-cycle specialization SC11_I2",
                    "normal", "cta_bridge"
                ),
                make_sta_image(
                    "SC11_I3",
                    "Ecological victory engraving. Moths, butterflies, beetles, and bees thriving across continental ecosystems, illuminated by golden evening light.",
                    "Diverse holometabolous insects thriving across continents",
                    "Celebrating evolutionary triumph SC11_I3",
                    "normal", "cta_bridge"
                ),
                make_sta_image(
                    "SC11_I4",
                    "Philosophical summary plate. Maria Sibylla Merian style vignette of empty chrysalis beside soaring moth with calligraphic script: 'PERFECTION THROUGH DISSOLUTION'.",
                    "Vignette of empty chrysalis beside soaring moth",
                    "Final philosophical synthesis SC11_I4",
                    "normal", "cta_bridge"
                ),
                make_sta_image(
                    "SC11_I5",
                    "Naturalist codex plate. Stickman chronicler closes antique leather folio, gesturing warmly toward the viewer beneath fluttering specimen cases.",
                    "Naturalist closing leather folio and inviting viewer",
                    "Delivering closing channel CTA SC11_I5",
                    "hold", "cta_close"
                ),
                make_sta_image(
                    "SC11_I6",
                    "Tactile channel endcard on warm specimen vellum #F6F0DD. Merian lithographic metamorphosis border framing hand-lettered text: 'SPAWN TO APEX'. Zero 3D, zero gradients.",
                    "Official Spawn to Apex channel endcard",
                    "Holding final channel endcard SC11_I6",
                    "hold", "cta_close",
                    is_endcard=True, shot_type="white_card"
                ),
            ],
            "beats": [
                make_sta_beat("SC11_B1", "SC11_I1", "State life-cycle division", "This radical division of life into two separate lives", "normal", "cta_bridge"),
                make_sta_beat("SC11_B2", "SC11_I2", "Cite 80% insect dominance", "explains why complete metamorphosis accounts for eighty percent of all insect species on Earth.", "normal", "cta_bridge"),
                make_sta_beat("SC11_B3", "SC11_I3", "Detail larval feeding role", "The larva does nothing but feed;", "normal", "cta_bridge"),
                make_sta_beat("SC11_B4", "SC11_I4", "Detail adult reproduction role", "the adult does nothing but navigate and reproduce. In nature, destruction is merely the price of evolutionary perfection.", "normal", "cta_bridge"),
                make_sta_beat("SC11_B5", "SC11_I5", "Deliver closing CTA", "Follow our next extreme metamorphosis chronicle on Spawn to Apex.", "hold", "cta_close"),
                make_sta_beat("SC11_B6", "SC11_I6", "Hold channel endcard", "Follow our next extreme metamorphosis chronicle on Spawn to Apex.", "hold", "cta_close", is_endcard=True),
            ]
        }
    ]

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
            {"requirement_id": f"R{i+1:02d}", "scene_id": f"SC{i+1:02d}", "quote": sc["narration"][:60]}
            for i, sc in enumerate(scenes)
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC07",
                "quote": "pairing the odor with harmless but unpleasant electrical pulses.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Tobacco hornworm larvae trained with mild electrical shocks to avoid ethyl acetate odor retained that aversion as adult moths after complete metamorphosis."
            },
            {
                "scene_id": "SC02",
                "quote": "Specialized death enzymes called caspases flood every tissue layer.",
                "language": "en",
                "source_id": "SRC02",
                "fact": "Caspase-mediated programmed cell death dissolves the majority of larval tissues into an amino acid-rich soup inside the pupal casing."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return brief, outline, competitor_research, content


def build_spawn_to_apex_short_data() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_wait_how"
    job_id = "en-spawn-to-apex-batch1-9x16"
    parent_long_id = "en-spawn-to-apex-batch1-16x9"
    youtube_title = "A Moth Remembers What Scared It as a Caterpillar"
    topic = "How a Caterpillar Completely Dissolves into Soup Inside the Chrysalis Yet Remembers What It Feared"

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Curious adults, biology lovers, and viewers hooked on bizarre chronological life-cycle transformations",
        "goal": "Explain how a caterpillar completely liquefies inside the chrysalis yet retains conditioned memories as an adult moth, teasing the mushroom-body synaptic vault",
        "video_type": "metamorphosis_chronicle",
        "duration": {
            "min_seconds": 38.0,
            "max_seconds": 52.0
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Slicing open a chrysalis reveals liquid genetic soup rather than a developing butterfly"},
            {"id": "R02", "text": "Caspase enzymes dissolve muscles while imaginal discs rebuild the adult body"},
            {"id": "R03", "text": "Editorial commentary on the impossibility of preserving memories through total liquefaction"},
            {"id": "R04", "text": "The Georgetown shock proof showing adult moths avoiding odor learned as caterpillars"},
            {"id": "R05", "text": "Cliffhanger peak on surviving mushroom-body circuits and bridge to full documentary"}
        ],
        "language": "en",
        "tone": "Riveting, chronological, wonder-filled, lucid, documentary-grade biological storytelling",
        "style": PRESERVE_SPAWN_STYLE,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "Retention of Memory Through Metamorphosis in Manduca sexta",
                "reference": "Blackiston, D. J., Casey, E. S., & Weiss, M. R. (2008). PLOS ONE.",
                "facts": [
                    "Tobacco hornworm larvae trained with mild electrical shocks to avoid ethyl acetate odor retained that aversion as adult moths after complete metamorphosis."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": "OmniVoice_EnWaitHow",
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deliver intense 45-second scientific shock hook and convert viewers to the long-form metamorphosis breakdown"
            ],
            "avoid": [
                "Childish cartoon mascots",
                "Clickbait fake biology",
                "Skipping stages of the chronological life cycle"
            ],
            "prior_knowledge": "Accessible to general cold mobile audience.",
            "pacing": "Rapid-fire visual hooks, high contrast, zero dead-air.",
            "speech_rates": {
                "en": {
                    "units_per_second": 3.8,
                    "uncertainty": 0.1,
                    "source": "Acoustic calibrated cadence"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Translucent chrysalis cutaway showing golden dissolved liquid with glowing caterpillar brain memory nodes inside",
                "text_overlay": "BRAIN IN SOUP",
                "contrast_pair": "Liquefied caterpillar soup vs Intact memory brain nodes",
                "thumbnail_prompt": "Vertical 9:16 Maria Sibylla Merian metamorphosis plate on warm specimen vellum #F6F0DD. High-impact cutaway of a chrysalis: interior filled with glowing amber organic liquid #D97941. Inside the broth, an intricate network of glowing bioluminescent teal brain nodes #2E6F65 remains completely intact. Fine dip-pen lithograph ink #1A1D24, cellular carmine accents #8C3B4A. Bold hand-lettered uppercase text in upper third: 'BRAIN IN SOUP'. Tactile vellum texture, zero 3D CGI.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "A caterpillar simply rests asleep while growing wings.",
                "why_generic_advice_fails": "Assuming gradual transformation ignores the brutal reality of total cellular autolysis.",
                "channel_verdict": "Metamorphosis requires complete biological suicide while insulating core memory circuits.",
                "tradeoff_or_blindspot": "Liquefying everything eliminates caterpillar upkeep but requires a miraculous neural vault."
            },
            "actionable_value": {
                "core_mechanism": "Preserving core synaptic circuits while completely rebuilding all peripheral body hardware.",
                "practical_rule_of_thumb": "During massive redesign, insulate core memory data while liquefying obsolete systems.",
                "real_world_scenario": "Software architects preserve core database schemas while completely rewriting obsolete frontends."
            },
            "channel_pillar": "Extreme metamorphosis & life cycles",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["caterpillar memory", "moth", "shorts", "metamorphosis", "science"],
            "cta_plan": {
                "cliffhanger_peak": "Which specific brain circuits survive total liquefaction to preserve larval memories into adulthood?",
                "bridge": "Watch the complete metamorphosis breakdown on Spawn to Apex YouTube.",
                "close": "Follow our channel for more extreme life-cycle revelations.",
                "endcard_text": "FULL VIDEO ON YOUTUBE"
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Translucent chrysalis cutaway showing golden dissolved liquid with glowing caterpillar brain memory nodes inside",
            "text_overlay": "BRAIN IN SOUP",
            "contrast_pair": "Liquefied caterpillar soup vs Intact memory brain nodes",
            "thumbnail_prompt": "Vertical 9:16 Maria Sibylla Merian metamorphosis plate on warm specimen vellum #F6F0DD. High-impact cutaway of a chrysalis: interior filled with glowing amber organic liquid #D97941. Inside the broth, an intricate network of glowing bioluminescent teal brain nodes #2E6F65 remains completely intact. Fine dip-pen lithograph ink #1A1D24, cellular carmine accents #8C3B4A. Bold hand-lettered uppercase text in upper third: 'BRAIN IN SOUP'. Tactile vellum texture, zero 3D CGI.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Extreme metamorphosis & life cycles",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["caterpillar memory", "moth", "shorts", "metamorphosis", "science"],
        "parent_long_id": parent_long_id,
        "cta_plan": {
            "cliffhanger_peak": "Which specific brain circuits survive total liquefaction to preserve larval memories into adulthood?",
            "bridge": "Watch the complete metamorphosis breakdown on Spawn to Apex YouTube.",
            "close": "Follow our channel for more extreme life-cycle revelations.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": "Natural history metamorphosis chronicler",
            "bridge_templates": [
                "Watch the complete Egg-to-Apex metamorphosis chronicle on Spawn to Apex YouTube."
            ],
            "close_templates": [
                "Follow our next evolutionary survival chronicle on Spawn to Apex."
            ],
            "endcard_text": "FULL VIDEO ON YOUTUBE",
            "banned_cta_phrases": [
                "don't forget to like",
                "hit the bell",
                "smash that like",
                "like and subscribe",
                "subscribe to the channel"
            ]
        },
        "editorial_stance": {
            "myth_debunked": "A caterpillar simply rests asleep while growing wings.",
            "why_generic_advice_fails": "Assuming gradual transformation ignores the brutal reality of total cellular autolysis.",
            "channel_verdict": "Metamorphosis requires complete biological suicide while insulating core memory circuits.",
            "tradeoff_or_blindspot": "Liquefying everything eliminates caterpillar upkeep but requires a miraculous neural vault."
        },
        "actionable_value": {
            "core_mechanism": "Preserving core synaptic circuits while completely rebuilding all peripheral body hardware.",
            "practical_rule_of_thumb": "During massive redesign, insulate core memory data while liquefying obsolete systems.",
            "real_world_scenario": "Software architects preserve core database schemas while completely rewriting obsolete frontends."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook cold viewers with the liquid soup reality inside the chrysalis", "requirements": ["R01"], "transition": "Transition to caspase enzymatic autolysis"},
            {"scene_id": "SC02", "purpose": "Show digestive enzymes melting tissues while imaginal discs rebuild", "requirements": ["R02"], "transition": "Transition to editorial analysis of memory impossibility"},
            {"scene_id": "SC03", "purpose": "Deliver sharp editorial commentary on the memory survival paradox", "requirements": ["R03"], "transition": "Pivoting to the Georgetown University shock experiment"},
            {"scene_id": "SC04", "purpose": "Present the empirical shock proof of odor avoidance in adult moths", "requirements": ["R04"], "transition": "Escalate to the peak cliffhanger and channel spinoff"},
            {"scene_id": "SC05", "purpose": "Deliver cliffhanger peak on mushroom bodies and bridge to long video", "requirements": ["R05"], "transition": "End of short"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Deep Look (KQED)",
                    "top_performing_videos": [
                        {
                            "title": "Inside the Chrysalis",
                            "views": "5.8M views",
                            "hook_technique": "Start with immediate high-retention macro cutaway.",
                            "pacing_structure": "Myth burst -> Liquid soup -> Memory proof.",
                            "retention_driver": "Rapid-fire visual delivery with zero filler."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Exposing the brutal fact of complete cellular liquefaction.",
                        "Using the Georgetown shock experiment as absolute empirical proof."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_words": 16,
                "zero_pause_opening_seconds": 10,
                "visual_contrast": "Crawling caterpillar vs Chrysalis filled with golden soup",
                "counter_intuitive_truth_slap": "Inside the chrysalis, a caterpillar completely melts into soup, yet somehow remembers what terrified it as a larva."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Shocking cold open on liquid soup inside the chrysalis."},
                {"phase": "empirical_conflict", "purpose": "Caspase enzymes dissolve tissues while imaginal discs rebuild."},
                {"phase": "structural_model", "purpose": "Editorial stance on the memory paradox."},
                {"phase": "actionable_resolution", "purpose": "Georgetown shock test proves memory survived."},
                {"phase": "cliffhanger_spinoff", "purpose": "Tease the mushroom body synaptic vault and bridge."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Vertical Maria Sibylla Merian metamorphosis lithograph plates on vellum."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Extreme metamorphosis & life cycles",
            "myth_debunked": "Caterpillars sleep while sprouting wings.",
            "channel_verdict": "Metamorphosis requires complete biological suicide while insulating core memory circuits.",
            "actionable_rule_of_thumb": "Isolate core memory data while liquefying obsolete hardware."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "Which specific brain circuits survive total liquefaction to preserve larval memories into adulthood?",
            "bridge": "Watch the complete metamorphosis breakdown on Spawn to Apex YouTube.",
            "close": "Follow our channel for more extreme life-cycle revelations.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        }
    }

    scenes = [
        # SC01
        {
            "id": "SC01",
            "title": "The Genetic Soup Hook",
            "purpose": "Hook cold viewers with the liquid soup reality inside the chrysalis",
            "action": "A chrysalis is cut open on Day 4 revealing liquid organic broth rather than an insect",
            "setting": "Natural history specimen vellum with antique brass naturalist loupe",
            "camera": "Dramatic vertical cutaway showing golden soup inside chrysalis",
            "narration": "If you slice open a chrysalis on Day Four, you will not find a developing insect—you will find an enzyme-dissolved genetic soup. The caterpillar completely destroys its physical body from the inside out.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Shocking, revelatory, visceral",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images": [
                make_sta_image(
                    "SC01_I1",
                    "Vertical 9:16 Maria Sibylla Merian plate on specimen vellum #F6F0DD. Cutaway of jade-green chrysalis revealing swirling golden organic liquid inside, dip-pen ink #1A1D24 and amber wash #D97941.",
                    "Cutaway of chrysalis revealing golden liquid soup",
                    "Establishing the liquid soup reality SC01_I1",
                    "burst", "hook_shock"
                ),
                make_sta_image(
                    "SC01_I2",
                    "Macro plate of liquid broth. Floating dissolved muscle strands and cell fragments in golden amber suspension, cellular carmine accents #8C3B4A.",
                    "Floating dissolved muscle strands in broth",
                    "Visualizing dissolved internal tissues SC01_I2",
                    "burst", "hook_shock"
                ),
                make_sta_image(
                    "SC01_I3",
                    "Lithographic dissection plate. Brass scalpel slicing through chrysalis wall, droplet of clear golden fluid weeping outward, bioluminescent teal #2E6F65.",
                    "Scalpel slicing chrysalis wall with fluid droplet",
                    "Emphasizing the physical fluid state SC01_I3",
                    "fast", "hook_shock"
                ),
                make_sta_image(
                    "SC01_I4",
                    "Field naturalist plate. Stickman anatomist gestures in astonishment at the fluid state, shaking head at the peaceful cartoon myth.",
                    "Stickman marvelling at fluid inside pupa",
                    "Hook climax: debunking cartoon myth SC01_I4",
                    "fast", "hook_shock"
                ),
            ],
            "beats": [
                make_sta_beat("SC01_B1", "SC01_I1", "Hook opening challenge", "If you slice open a chrysalis on Day Four,", "burst", "hook_shock"),
                make_sta_beat("SC01_B2", "SC01_I2", "Deny developing insect", "you will not find a developing insect—", "burst", "hook_shock"),
                make_sta_beat("SC01_B3", "SC01_I3", "Proclaim genetic soup", "you will find an enzyme-dissolved genetic soup.", "fast", "hook_shock"),
                make_sta_beat("SC01_B4", "SC01_I4", "State physical body destruction", "The caterpillar completely destroys its physical body from the inside out.", "fast", "hook_shock"),
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "Autolysis and Disc Resurrection",
            "purpose": "Show digestive enzymes melting tissues while imaginal discs rebuild",
            "action": "Enzymes dissolve muscles and gut while imaginal discs drink broth to assemble wings",
            "setting": "Microscopic histological cutaway on specimen vellum",
            "camera": "Deep microscopic zoom tracking cellular autolysis and disc division",
            "narration": "Caspase enzymes dissolve muscles, gut, and fat reserves into a nutrient broth. Yet tiny clusters called imaginal discs survive. Present since the egg, these dormant blueprint disks drink the protein soup to rapidly assemble eyes, antennae, and wings.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Precise, biochemical, rapid",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sta_image(
                    "SC02_I1",
                    "Vertical 9:16 histological plate on #F6F0DD paper. Muscle fibers dissolving under caspase enzyme attack, cellular carmine wash #8C3B4A and amber #D97941.",
                    "Muscle fibers dissolving under caspase attack",
                    "Depicting enzymatic autolysis SC02_I1",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC02_I2",
                    "Microscopic cellular plate. Glowing imaginal discs floating untouched within the golden broth, bioluminescent teal wash #2E6F65 and India ink #1A1D24.",
                    "Glowing imaginal discs surviving in broth",
                    "Showing resilient blueprint discs SC02_I2",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC02_I3",
                    "Mitosis diagram. Disc cells actively dividing and drinking amino acid broth, multiplying rapidly, nocturnal indigo wash #1D3557.",
                    "Disc cells actively dividing and multiplying",
                    "Visualizing rapid cell proliferation SC02_I3",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC02_I4",
                    "Organogenesis plate. Wing discs folding into miniature wings and compound eyes taking shape inside pupal shell, specimen vellum #F6F0DD.",
                    "Wing discs and compound eyes taking shape",
                    "Demonstrating organ assembly from soup SC02_I4",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sta_beat("SC02_B1", "SC02_I1", "Describe caspase dissolution", "Caspase enzymes dissolve muscles, gut, and fat reserves into a nutrient broth.", "fast", "mechanism_step"),
                make_sta_beat("SC02_B2", "SC02_I2", "Introduce surviving imaginal discs", "Yet tiny clusters called imaginal discs survive.", "fast", "mechanism_step"),
                make_sta_beat("SC02_B3", "SC02_I3", "State presence since egg", "Present since the egg, these dormant blueprint disks", "normal", "mechanism_step"),
                make_sta_beat("SC02_B4", "SC02_I4", "Detail organ assembly", "drink the protein soup to rapidly assemble eyes, antennae, and wings.", "normal", "mechanism_step"),
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Memory Paradox Stance",
            "purpose": "Deliver sharp editorial commentary on the memory survival paradox",
            "action": "Conceptual diagram examining memory storage in synaptic networks versus liquid dissolution",
            "setting": "Naturalist neuroanatomical codex plate on aged specimen vellum",
            "camera": "Static conceptual diagram highlighting broken synapses",
            "narration": "Science once assumed every memory was destroyed when the brain dissolved. Physical memories require physical neural connections. How could an organism liquefy its entire nervous system, yet preserve what it learned as a caterpillar?",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Provocative, commanding, analytical",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                make_sta_image(
                    "SC03_I1",
                    "Vertical 9:16 neuroanatomical codex on #F6F0DD paper. Caterpillar brain diagram with synaptic network dissolving into fluid droplets, India ink #1A1D24 and amber #D97941.",
                    "Caterpillar brain diagram dissolving into fluid",
                    "Editorial stance on the memory paradox SC03_I1",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC03_I2",
                    "Microscopic synaptic diagram. Broken dendrites floating apart in liquid broth, highlighted with red question marks in cellular carmine #8C3B4A.",
                    "Broken dendrites floating in liquid broth",
                    "Showing physical breakdown of memory circuits SC03_I2",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC03_I3",
                    "Naturalist codex plate. Stickman neuroscientist holds magnifying glass over brain model, pointing toward the seeming impossibility of memory retention.",
                    "Stickman pondering the memory survival riddle",
                    "Framing scientific skepticism SC03_I3",
                    "slow", "editorial_commentary"
                ),
                make_sta_image(
                    "SC03_I4",
                    "Conceptual lithograph plate. Question mark formed from glowing synaptic threads glowing inside translucent chrysalis, teal wash #2E6F65.",
                    "Glowing question mark formed from synaptic threads",
                    "Channel verdict on memory riddle SC03_I4",
                    "slow", "editorial_commentary"
                ),
            ],
            "beats": [
                make_sta_beat("SC03_B1", "SC03_I1", "State past scientific assumption", "Science once assumed every memory was destroyed when the brain dissolved.", "slow", "editorial_commentary"),
                make_sta_beat("SC03_B2", "SC03_I2", "State physical synapse requirement", "Physical memories require physical neural connections.", "slow", "editorial_commentary"),
                make_sta_beat("SC03_B3", "SC03_I3", "Ask nervous system liquefaction question", "How could an organism liquefy its entire nervous system,", "slow", "editorial_commentary"),
                make_sta_beat("SC03_B4", "SC03_I4", "Conclude larval learning riddle", "yet preserve what it learned as a caterpillar?", "slow", "editorial_commentary"),
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "The Georgetown Shock Proof",
            "purpose": "Present the empirical shock proof of odor avoidance in adult moths",
            "action": "Georgetown University researchers shock caterpillars with odor; adult moths avoid that smell",
            "setting": "Laboratory conditioning apparatus and Y-maze arena",
            "camera": "Dynamic comparison showing caterpillar shock training and adult moth flight choice",
            "narration": "Researchers at Georgetown University delivered definitive proof. They conditioned caterpillars to fear an odor using mild electrical shocks. Weeks later, after complete liquefaction, the adult moths still remembered, fleeing from that exact smell in a flight maze.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Empirical, astonished, triumphant",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sta_image(
                    "SC04_I1",
                    "Vertical 9:16 laboratory plate on #F6F0DD paper. Caterpillar on wired grid flinching from chemical odor dispenser, blue electrical sparks in teal #2E6F65.",
                    "Caterpillar on wired grid learning odor aversion",
                    "Depicting the Georgetown shock training SC04_I1",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC04_I2",
                    "Laboratory Y-maze plate. Adult hawkmoth flying up glass maze, sharply turning away from the odor chamber into clean air, India ink #1A1D24.",
                    "Adult hawkmoth turning away from odor chamber",
                    "Proving adult moth avoidance behavior SC04_I2",
                    "fast", "mechanism_step"
                ),
                make_sta_image(
                    "SC04_I3",
                    "Statistical bar graph on specimen vellum showing 78% avoidance in trained moths versus random choice, amber resin accents #D97941.",
                    "Bar graph proving 78% avoidance in adult moths",
                    "Documenting empirical verification SC04_I3",
                    "normal", "mechanism_step"
                ),
                make_sta_image(
                    "SC04_I4",
                    "Conceptual zoological plate. Glowing memory connection linking caterpillar silhouette to soaring adult hawkmoth, nocturnal indigo #1D3557.",
                    "Memory connection linking caterpillar to moth",
                    "The empirical proof established SC04_I4",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sta_beat("SC04_B1", "SC04_I1", "Introduce Georgetown proof", "Researchers at Georgetown University delivered definitive proof.", "fast", "mechanism_step"),
                make_sta_beat("SC04_B2", "SC04_I2", "Detail odor shock conditioning", "They conditioned caterpillars to fear an odor using mild electrical shocks.", "fast", "mechanism_step"),
                make_sta_beat("SC04_B3", "SC04_I3", "State weeks-later retention", "Weeks later, after complete liquefaction, the adult moths still remembered,", "normal", "mechanism_step"),
                make_sta_beat("SC04_B4", "SC04_I4", "Conclude flight maze avoidance", "fleeing from that exact smell in a flight maze.", "normal", "mechanism_step"),
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Synaptic Vault Twist & Spin-off",
            "purpose": "Deliver cliffhanger peak on mushroom bodies, bridge to long video, and closing CTA",
            "action": "Brain cutaway reveals mushroom body circuits; stickman introduces full metamorphosis breakdown",
            "setting": "Cranial neuroanatomical plate shifting to vertical channel endcard",
            "camera": "Deep microscopic zoom on glowing mushroom body circuits, transitioning to endcard",
            "narration": "Which specific brain circuits survive total liquefaction to preserve larval memories into adulthood? Watch the complete metamorphosis breakdown on Spawn to Apex YouTube. Follow our channel for more extreme life-cycle revelations.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Mysterious, wonder-filled, inviting",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cliffhanger_peak",
            "images": [
                make_sta_image(
                    "SC05_I1",
                    "Vertical 9:16 cranial cutaway on #F6F0DD paper. Adult moth head with brain glowing, highlighting protected twin mushroom body circuits in bioluminescent teal #2E6F65.",
                    "Adult moth brain highlighting mushroom bodies",
                    "Visualizing cliffhanger peak mystery SC05_I1",
                    "fast", "cliffhanger_peak"
                ),
                make_sta_image(
                    "SC05_I2",
                    "Microscopic synaptic diagram showing dense insulated Kenyon cell circuits surviving intact amid surrounding autolytic soup, amber wash #D97941.",
                    "Insulated Kenyon cell circuits surviving in soup",
                    "Demonstrating the synaptic vault SC05_I2",
                    "normal", "cliffhanger_peak"
                ),
                make_sta_image(
                    "SC05_I3",
                    "Field naturalist plate on vellum. Stickman researcher points with brass pointer toward a full 14-day metamorphosis timeline banner.",
                    "Stickman presenting the full 14-day timeline banner",
                    "Bridging to full YouTube documentary SC05_I3",
                    "normal", "cta_bridge"
                ),
                make_sta_image(
                    "SC05_I4",
                    "Vertical 9:16 channel endcard on warm specimen vellum #F6F0DD. Merian lithographic metamorphosis border framing hand-lettered text: 'SPAWN TO APEX'. Zero 3D, zero gradients.",
                    "Official Spawn to Apex vertical channel endcard",
                    "Holding vertical channel endcard SC05_I4",
                    "hold", "cta_close",
                    is_endcard=True, shot_type="white_card"
                ),
            ],
            "beats": [
                make_sta_beat("SC05_B1", "SC05_I1", "Deliver cliffhanger peak question", "Which specific brain circuits survive total liquefaction to preserve larval memories into adulthood?", "fast", "cliffhanger_peak"),
                make_sta_beat("SC05_B2", "SC05_I2", "Reinforce visual mystery", "Which specific brain circuits survive total liquefaction to preserve larval memories into adulthood?", "normal", "cliffhanger_peak"),
                make_sta_beat("SC05_B3", "SC05_I3", "Deliver bridge to long video", "Watch the complete metamorphosis breakdown on Spawn to Apex YouTube.", "normal", "cta_bridge"),
                make_sta_beat("SC05_B4", "SC05_I4", "Deliver closing CTA on endcard", "Follow our channel for more extreme life-cycle revelations.", "hold", "cta_close", is_endcard=True),
            ]
        }
    ]

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
            {"requirement_id": f"R{i+1:02d}", "scene_id": f"SC{i+1:02d}", "quote": sc["narration"][:60]}
            for i, sc in enumerate(scenes)
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC04",
                "quote": "fleeing from that exact smell in a flight maze.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Tobacco hornworm larvae trained with mild electrical shocks to avoid ethyl acetate odor retained that aversion as adult moths after complete metamorphosis."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return brief, outline, competitor_research, content
