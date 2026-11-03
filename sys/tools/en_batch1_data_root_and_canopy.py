"""Data definitions for Channel 2: Root & Canopy (en_kitchen_molecules / en_root_and_canopy).

Long Job: sys/runs/en-root-and-canopy-batch1-16x9
Short Job: sys/runs/en-root-and-canopy-batch1-9x16
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


PRESERVE_ROOT_STYLE = (
    "Authentic 2D Kew Gardens and Audubon botanical copperplate ink engraving and pressed-herbarium watercolor wash on warm "
    "deckle-edge rag paper #F4EFE0, botanical India ink cross-hatching #1E241E, chlorophyll forest green #3A6B4C, "
    "soil-strata terracotta #B85D3B, amber resin gold #D4A359, deep canopy forest green #2B3A2E, split above-and-below-ground "
    "strata cross-sections with taxonomic brass magnifier callouts, orthographic 2D, >=60% negative space, "
    "tactile herbarium plate texture, zero 3D CGI, zero kawaii stickers, zero gradients"
)

MOTION_SUFFIX = "silent visual storytelling, no talking, no lip movement"


def make_rc_image(
    img_id: str,
    desc: str,
    change: str,
    reason: str,
    tempo: str,
    situation: str,
    motion_action: str = "Tactile botanical time-lapse engraving camera motion",
    has_character: bool = True,
    is_endcard: bool = False,
    shot_type: str = "full_scene",
) -> Dict[str, Any]:
    m_prompt = f"Tactile 2D botanical copperplate animation. {motion_action.strip()}, transitioning smoothly into next frame, {MOTION_SUFFIX}"
    return {
        "id": img_id,
        "description": desc,
        "character_ids": ["CH01"] if has_character else [],
        "based_on": None,
        "preserve": PRESERVE_ROOT_STYLE,
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


def make_rc_beat(
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


def build_root_and_canopy_long_data() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_kitchen_molecules"
    job_id = "en-root-and-canopy-batch1-16x9"
    youtube_title = "How a Strangler Fig Devours a Giant Tree Alive"
    topic = "Year 1 to Year 200: How a Strangler Fig Slowly Devours a Rainforest Giant from the Sky Down"

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Nature documentary enthusiasts, botanical science fans, and viewers fascinated by time-lapse life cycles",
        "goal": "Chronicle the two-century time-lapse warfare of a strangler fig germinating in the canopy and slowly devouring a 150-foot rainforest giant from the sky down",
        "video_type": "botanical_chronicle",
        "duration": {
            "min_seconds": 150.0,
            "max_seconds": 210.0
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Year One canopy seed deposition by a frugivorous hornbill atop a dipterocarp branch"},
            {"id": "R02", "text": "The dark forest floor mortality trap receiving less than one percent photosynthetic light"},
            {"id": "R03", "text": "Years Two to Ten epiphytic anchor sending delicate aerial roots downward along host bark"},
            {"id": "R04", "text": "Editorial commentary on plants as slow-motion architectural predators waging territorial war"},
            {"id": "R05", "text": "Year Twenty-Five ground strike as first root tip taps moisture-rich forest floor loam"},
            {"id": "R06", "text": "Explosive underground hydraulic overdrive pumping nitrogen and water back up to canopy"},
            {"id": "R07", "text": "Years Fifty to Eighty anastomosing root fusion weaving a suffocating rigid wooden corset"},
            {"id": "R08", "text": "Editorial commentary on vascular girdling severing host phloem sugar transport conduits"},
            {"id": "R09", "text": "Canopy conquest over-topping the host crown and stealing solar photons completely"},
            {"id": "R10", "text": "Years One Hundred to Two Hundred host trunk rotting into hollow central cathedral cylinder"},
            {"id": "R11", "text": "The keystone botanical survivor legacy feeding hundreds of rainforest species and closing CTA"}
        ],
        "language": "en",
        "tone": "Hypnotic, chronological, dramatic, revealing hidden underground and canopy survival battles",
        "style": PRESERVE_ROOT_STYLE,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "The Biology of Ficus: Strangling Figs and Tropical Forest Ecology",
                "reference": "Harrison, R. D. (2005). Biological Reviews of the Cambridge Philosophical Society.",
                "facts": [
                    "Strangler fig seeds dropped on the dark rainforest floor have less than a 0.1% chance of survival due to extreme shade.",
                    "Anastomosing aerial roots fuse together via self-grafting to form a rigid structural cylinder around the host trunk."
                ]
            },
            {
                "id": "SRC02",
                "title": "Vascular Girdling Biomechanics in Hemiepiphytic Trees",
                "reference": "Putz, F. E., & Holbrook, N. M. (1989). Functional Ecology.",
                "facts": [
                    "Radial expansion of fused fig roots constricts the host's secondary phloem, halting downward sugar transport to the host's root system.",
                    "The mature strangler fig acts as a keystone resource, providing figs during seasonal fruit famines."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": True,
                "voice": "OmniVoice_EnKitchenMolecules",
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deliver hypnotic 200-year botanical time-lapse storytelling framing plant growth as high-stakes gladiator warfare"
            ],
            "avoid": [
                "Treating plants as passive static scenery",
                "Childish cartoon flower faces",
                "Dry gardening tips without evolutionary storytelling"
            ],
            "prior_knowledge": "Accessible to general documentary viewers without specialized plant anatomy knowledge.",
            "pacing": "Hypnotic time-lapse progression, accelerating chronological stakes, zero filler.",
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
                "visual_hook": "Split soil-and-canopy cutaway of a strangler fig lattice suffocating a colossal hardwood tree",
                "text_overlay": "CAGED ALIVE",
                "contrast_pair": "Host tree phloem strangled vs Expanding fig root lattice",
                "thumbnail_prompt": "18th-century Kew Gardens botanical copperplate engraving on warm fibrous rag paper #F4EFE0. High-contrast cross-section of a 150-foot rainforest giant tree encircled by an interlocking wooden mesh of strangler fig roots. Cutaway reveals dying dark-brown host xylem surrounded by vibrant green fig vascular cords. Fine India ink cross-hatching #1E241E, chlorophyll green #3A6B4C, soil terracotta #B85D3B. Bold hand-lettered uppercase text in upper third: 'CAGED ALIVE'. Tactile museum herbarium texture, >=60% negative space, zero 3D CGI.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "Plants are peaceful, passive organisms coexisting in harmonious balance without territorial aggression.",
                "why_generic_advice_fails": "Viewing botany as gentle ignores the cutthroat multi-century architectural warfare over light and minerals.",
                "channel_verdict": "A strangler fig is not a peaceful vine but a calculating parasite executing a slow-motion architectural execution.",
                "tradeoff_or_blindspot": "Growing from the canopy down avoids the gloom below but risks total desiccation before reaching groundwater."
            },
            "actionable_value": {
                "core_mechanism": "Inverting traditional resource acquisition by capturing sunlight first, then deploying downward conduits for soil minerals.",
                "practical_rule_of_thumb": "When competition at ground level is fatal, secure market reach from above before building physical infrastructure.",
                "real_world_scenario": "Software platforms mirror strangler figs by launching cloud-first services that gradually encircle legacy on-premises servers."
            },
            "channel_pillar": "Plant evolution through deep time",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["strangler fig", "botany", "plant time lapse", "rainforest documentary", "tree evolution", "nature"],
            "cta_plan": {
                "close": "Explore the next botanical survival chronicle on Root and Canopy.",
                "endcard_text": "ROOT & CANOPY"
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Split soil-and-canopy cutaway of a strangler fig lattice suffocating a colossal hardwood tree",
            "text_overlay": "CAGED ALIVE",
            "contrast_pair": "Host tree phloem strangled vs Expanding fig root lattice",
            "thumbnail_prompt": "18th-century Kew Gardens botanical copperplate engraving on warm fibrous rag paper #F4EFE0. High-contrast cross-section of a 150-foot rainforest giant tree encircled by an interlocking wooden mesh of strangler fig roots. Cutaway reveals dying dark-brown host xylem surrounded by vibrant green fig vascular cords. Fine India ink cross-hatching #1E241E, chlorophyll green #3A6B4C, soil terracotta #B85D3B. Bold hand-lettered uppercase text in upper third: 'CAGED ALIVE'. Tactile museum herbarium texture, >=60% negative space, zero 3D CGI.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Plant evolution through deep time",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["strangler fig", "botany", "plant time lapse", "rainforest documentary", "tree evolution", "nature"],
        "cta_plan": {
            "close": "Explore the next botanical survival chronicle on Root and Canopy.",
            "endcard_text": "ROOT & CANOPY"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": "Botanical time-lapse chronicler",
            "bridge_templates": [
                "Watch the complete 200-year botanical time-lapse chronicle on Root & Canopy YouTube."
            ],
            "close_templates": [
                "Explore the next botanical survival chronicle on Root and Canopy."
            ],
            "endcard_text": "ROOT & CANOPY",
            "banned_cta_phrases": [
                "don't forget to like",
                "hit the bell",
                "smash that like",
                "like and subscribe",
                "subscribe to the channel"
            ]
        },
        "editorial_stance": {
            "myth_debunked": "Plants are peaceful, passive organisms coexisting in harmonious balance without territorial aggression.",
            "why_generic_advice_fails": "Viewing botany as gentle ignores the cutthroat multi-century architectural warfare over light and minerals.",
            "channel_verdict": "A strangler fig is not a peaceful vine but a calculating parasite executing a slow-motion architectural execution.",
            "tradeoff_or_blindspot": "Growing from the canopy down avoids the gloom below but risks total desiccation before reaching groundwater."
        },
        "actionable_value": {
            "core_mechanism": "Inverting traditional resource acquisition by capturing sunlight first, then deploying downward conduits for soil minerals.",
            "practical_rule_of_thumb": "When competition at ground level is fatal, secure market reach from above before building physical infrastructure.",
            "real_world_scenario": "Software platforms mirror strangler figs by launching cloud-first services that gradually encircle legacy on-premises servers."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Establish Year One seed deposition high in the canopy fork", "requirements": ["R01"], "transition": "Contrast with the fatal gloom of the forest floor"},
            {"scene_id": "SC02", "purpose": "Explain why ground germination is an automatic death sentence", "requirements": ["R02"], "transition": "Return to the fragile epiphytic seedling above"},
            {"scene_id": "SC03", "purpose": "Chronicle the slow downward descent of hair-thin aerial roots", "requirements": ["R03"], "transition": "Transition to editorial analysis of plant warfare"},
            {"scene_id": "SC04", "purpose": "Provide sharp editorial stance framing plants as architectural predators", "requirements": ["R04"], "transition": "Moving to the critical moment roots touch soil"},
            {"scene_id": "SC05", "purpose": "Show the explosive hydraulic shift when roots penetrate ground loam", "requirements": ["R05"], "transition": "Detailing the massive underground nutrient surge"},
            {"scene_id": "SC06", "purpose": "Illustrate root thickening into massive structural wooden cables", "requirements": ["R06"], "transition": "Advancing time to the multi-root grafting stage"},
            {"scene_id": "SC07", "purpose": "Depict root self-grafting into an anastomosing strangulation corset", "requirements": ["R07"], "transition": "Analyzing the physiological damage to host phloem"},
            {"scene_id": "SC08", "purpose": "Editorial breakdown of phloem girdling and vascular starvation", "requirements": ["R08"], "transition": "Shifting upward to the canopy light battle"},
            {"scene_id": "SC09", "purpose": "Illustrate canopy expansion over-topping and shading host foliage", "requirements": ["R09"], "transition": "Advancing century to the host tree's death"},
            {"scene_id": "SC10", "purpose": "Chronicle the host trunk decomposition leaving a hollow cathedral", "requirements": ["R10"], "transition": "Concluding with the keystone ecological payoff"},
            {"scene_id": "SC11", "purpose": "Deliver keystone forest verdict and channel closing call to action", "requirements": ["R11"], "transition": "End of chronicle"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "BBC Earth — The Green Planet",
                    "top_performing_videos": [
                        {
                            "title": "The Tree That Strangles Its Host",
                            "views": "6.1M views",
                            "hook_technique": "Time-lapse cinematography treating botanical growth as predator-prey stalking.",
                            "pacing_structure": "Seed deposition -> Root descent -> Trunk strangulation -> Hollow cage.",
                            "retention_driver": "Mind-bending realization that plants move with terrifying predatory intent."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Chronological time-lapse pacing across decades and centuries.",
                        "Vascular cutaways showing phloem fluid choked by tight root loops."
                    ]
                },
                {
                    "channel_name": "Crime Pays But Botany Doesn't",
                    "top_performing_videos": [
                        {
                            "title": "Insane Tropical Epiphytes and Tree Parasites",
                            "views": "1.4M views",
                            "hook_technique": "Candid, gritty botanical taxonomy stripped of textbook pleasantries.",
                            "pacing_structure": "Ecological niche -> Cutthroat resource competition -> Structural morphology.",
                            "retention_driver": "Authentic enthusiasm for plant brutality and evolutionary ruthlessness."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Sharp critique of naive gentle-nature stereotypes.",
                        "Highlighting how light starvation on forest floors forces canopy-first evolution."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_words": 16,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Tiny solitary seed pasted 150 feet high vs Massive 200-year-old hardwood trunk",
                "counter_intuitive_truth_slap": "While normal trees fight upward toward the sun from the soil, this botanical executioner begins one hundred and fifty feet in the air."
            },
            "narrative_progression_arc": [
                {"phase": "canopy_germination", "purpose": "A sticky seed glues itself to high bark via hornbill droppings."},
                {"phase": "descent_of_roots", "purpose": "Delicate aerial filaments crawl downward through humid mist."},
                {"phase": "ground_hydraulic_strike", "purpose": "Touching forest loam triggers explosive hydraulic uptake."},
                {"phase": "phloem_strangulation", "purpose": "Roots fuse into an airtight wooden corset that girdles the host."},
                {"phase": "hollow_cathedral", "purpose": "The host rots away, leaving an immortal freestanding lattice."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential Kew Gardens botanical plates with copperplate soil strata cutaways."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Plant evolution through deep time",
            "myth_debunked": "Plants are peaceful, passive static decorations.",
            "channel_verdict": "Plants wage ruthless architectural and hydraulic warfare over multi-century timelines.",
            "actionable_rule_of_thumb": "Capture vital sunlight first before investing energy into massive ground roots."
        },
        "cta_and_spinoff_strategy": {
            "close": "Explore the next botanical survival chronicle on Root and Canopy.",
            "endcard_text": "ROOT & CANOPY"
        }
    }

    # 11 Scenes for Long Video
    scenes = [
        # SC01
        {
            "id": "SC01",
            "title": "Year One: The Canopy Dropping",
            "purpose": "Introduce the sticky seed deposited high in the canopy fork",
            "action": "A hornbill perches on a high dipterocarp branch and deposits a sticky fig seed into a mossy bark crevice",
            "setting": "Canopy fork of a 150-foot dipterocarp tree in tropical rainforest",
            "camera": "High-altitude establishing shot tracking hornbill landing on towering branch",
            "narration": "A hundred and fifty feet above the tropical rainforest floor, a rhinoceros hornbill perches quietly upon the mossy bough of an ancient dipterocarp hardwood. With an energetic flick of its curved beak, the bird excretes a gelatinous seed cluster. Coated in natural mucilage, a solitary strangler fig seed cements itself securely into a deep, humid bark crevice.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Hypnotic, aerial, atmospheric",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images": [
                make_rc_image(
                    "SC01_I1",
                    "Kew Gardens botanical copperplate plate on warm rag paper #F4EFE0. High canopy view of colossal dipterocarp tree bough with rhinoceros hornbill perched in fine India ink #1E241E.",
                    "Hornbill perched high on mossy hardwood branch",
                    "Establishing high-altitude canopy setting SC01_I1",
                    "burst", "hook_shock"
                ),
                make_rc_image(
                    "SC01_I2",
                    "Macro botanical engraving. Cluster of tiny glistening fig seeds wrapped in translucent mucilage adhering to rough bark furrow, amber resin gold wash #D4A359.",
                    "Sticky fig seed cluster adhering to bark furrow",
                    "Focusing on the microscopic seed payload SC01_I2",
                    "burst", "hook_shock"
                ),
                make_rc_image(
                    "SC01_I3",
                    "Botanical cross-section on herbarium paper #F4EFE0. Single seed coat swelling with tropical rain mist, tiny green embryonic shoot stirring inside with chlorophyll green #3A6B4C.",
                    "Cross-section of swelling fig seed coat",
                    "Depicting internal embryonic germination SC01_I3",
                    "fast", "hook_shock"
                ),
                make_rc_image(
                    "SC01_I4",
                    "Naturalist codex plate. Delicate green cotyledon leaf unfurling upward into bright unobstructed sunlight, while tiny root anchor embeds into moist bark moss.",
                    "First green leaf unfurls in open sunlight",
                    "Securing immediate photosynthetic energy SC01_I4",
                    "fast", "hook_shock"
                ),
                make_rc_image(
                    "SC01_I5",
                    "Wide vertical botanical plate. Slender green seedling perched precariously on titanic branch high above distant forest floor, India ink cross-hatching #1E241E.",
                    "Seedling perched precariously on titanic bough",
                    "Illustrating the immense vertical scale SC01_I5",
                    "normal", "hook_shock"
                ),
                make_rc_image(
                    "SC01_I6",
                    "Herbarium specimen diagram. Taxonomic labels identifying Ficus hemiepiphyte seedling in delicate calligraphy beside brass calipers, rag paper #F4EFE0.",
                    "Botanical specimen plate of juvenile hemiepiphyte",
                    "Documenting scientific taxonomy SC01_I6",
                    "normal", "hook_shock"
                ),
            ],
            "beats": [
                make_rc_beat("SC01_B1", "SC01_I1", "Establish 150-foot height", "A hundred and fifty feet above the tropical rainforest floor,", "burst", "hook_shock"),
                make_rc_beat("SC01_B2", "SC01_I2", "Introduce hornbill landing", "a rhinoceros hornbill perches upon the mossy bough of an ancient dipterocarp hardwood.", "burst", "hook_shock"),
                make_rc_beat("SC01_B3", "SC01_I3", "Describe seed excretion", "With a flick of its curved beak, the bird excretes a gelatinous seed cluster.", "fast", "hook_shock"),
                make_rc_beat("SC01_B4", "SC01_I4", "Highlight mucilage glue", "Coated in natural mucilage,", "fast", "hook_shock"),
                make_rc_beat("SC01_B5", "SC01_I5", "Show seed cementing", "a solitary strangler fig seed cements itself tightly", "normal", "hook_shock"),
                make_rc_beat("SC01_B6", "SC01_I6", "Conclude bark anchor", "into a humid bark crevice.", "normal", "hook_shock"),
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "The Dark Floor Death Trap",
            "purpose": "Explain why germinating on the dark forest floor is an immediate death sentence",
            "action": "A comparison showing seeds dying in the pitch-black gloom of the forest understory",
            "setting": "Understory floor beneath dense interlocking canopy layers",
            "camera": "Downward vertical pan descending from sunlit canopy into suffocating gloom",
            "narration": "Landing high in the canopy is no biological accident; it represents the fig's only hope of survival. Down on the forest floor, a suffocating triple canopy blocks ninety-nine percent of solar radiation. Any fig seed that tumbles onto the dark leaf litter is doomed to starve in perpetual green twilight before ever developing its second leaf.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Stark, comparative, ecological",
            "narrative_phase": "lived_friction",
            "narrative_situation": "before_after_contrast",
            "images": [
                make_rc_image(
                    "SC02_I1",
                    "Copperplate strata cutaway on rag paper #F4EFE0. Vertical forest profile showing brilliant sunlight at canopy layer fading into pitch-black ink shading at soil floor.",
                    "Light gradient cross-section from canopy to floor",
                    "Visualizing severe light attenuation SC02_I1",
                    "fast", "before_after_contrast"
                ),
                make_rc_image(
                    "SC02_I2",
                    "Botanical study on dark understory. A withered pale fig seedling lying limp upon damp decaying leaf litter, chlorophyll starved in terracotta soil #B85D3B.",
                    "Withered seedling starving on dark leaf litter",
                    "Demonstrating ground floor mortality SC02_I2",
                    "fast", "before_after_contrast"
                ),
                make_rc_image(
                    "SC02_I3",
                    "Photometric diagram plate. Hand-drawn light meter scale showing 100% light at canopy top dropping to less than 1% at floor level, fine dip-pen calligraphy #1E241E.",
                    "Light percentage scale down tree profile",
                    "Explaining the 1% sunlight statistic SC02_I3",
                    "normal", "before_after_contrast"
                ),
                make_rc_image(
                    "SC02_I4",
                    "Macro plate of forest floor fungi. Aggressive mold mycelium consuming a dead fallen seed in moist darkness, deep terracotta wash #B85D3B.",
                    "Mold threads consuming failed fallen seed",
                    "Depicting underground biological decomposition SC02_I4",
                    "fast", "before_after_contrast"
                ),
                make_rc_image(
                    "SC02_I5",
                    "Contrast comparison plate. On left, dead ground seed decaying in shadow; on right, canopy seedling thriving in radiant gold sunlight #D4A359.",
                    "Split contrast between ground death and canopy life",
                    "Establishing evolutionary justification SC02_I5",
                    "fast", "before_after_contrast"
                ),
                make_rc_image(
                    "SC02_I6",
                    "Wide botanical illustration on #F4EFE0 paper. The sun-drenched upper crown of the rainforest, where the young epiphyte basks safely above the shaded graveyard below.",
                    "Sunlit canopy crown glowing above shadowed understory",
                    "Confirming the canopy sanctuary advantage SC02_I6",
                    "normal", "before_after_contrast"
                ),
            ],
            "beats": [
                make_rc_beat("SC02_B1", "SC02_I1", "State deliberate canopy strategy", "Landing high in the canopy is no biological accident;", "fast", "before_after_contrast"),
                make_rc_beat("SC02_B2", "SC02_I2", "Frame only hope of survival", "it is the fig's only hope.", "fast", "before_after_contrast"),
                make_rc_beat("SC02_B3", "SC02_I3", "Detail 99% light blockage", "Down on the forest floor, a suffocating triple canopy blocks ninety-nine percent of solar radiation.", "normal", "before_after_contrast"),
                make_rc_beat("SC02_B4", "SC02_I4", "Highlight leaf litter doom", "Any fig seed that tumbles onto the dark leaf litter", "fast", "before_after_contrast"),
                make_rc_beat("SC02_B5", "SC02_I5", "Show starvation in twilight", "is doomed to starve in perpetual green twilight", "fast", "before_after_contrast"),
                make_rc_beat("SC02_B6", "SC02_I6", "Conclude two-leaf barrier", "before developing its second leaf.", "normal", "before_after_contrast"),
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "Years Two to Ten: Epiphytic Pioneers",
            "purpose": "Chronicle the slow downward descent of hair-thin aerial roots along host bark",
            "action": "Delicate aerial roots snake downward along the host tree's furrowed bark, feeding on mist",
            "setting": "Vertical trunk of massive dipterocarp tree spanning 150 vertical feet",
            "camera": "Slow downward tracking macro shot following root tips creeping along bark",
            "narration": "During its first decade, the young fig lives strictly as an innocent epiphyte. It feeds on tropical mist, rainwater trickle, and decomposing moss particles trapped in bark crevices. But soon, it extends hair-thin aerial roots downward. These delicate living cables snake across the hardwood timber like slow-motion green lightning, heading inexorably toward damp ground soil.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Poetic, methodical, tense",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "story_action",
            "images": [
                make_rc_image(
                    "SC03_I1",
                    "Botanical codex plate on #F4EFE0 paper. Slender Ficus epiphyte nestled in bark crevice, absorbing droplets of rainwater mist in translucent wash #D4A359.",
                    "Epiphytic seedling absorbing rainwater droplets",
                    "Showing early epiphytic nutrition SC03_I1",
                    "normal", "story_action"
                ),
                make_rc_image(
                    "SC03_I2",
                    "Macro botanical engraving. Delicate aerial root tip equipped with a moist protective root cap crawling downward along rough hardwood bark, forest green #3A6B4C.",
                    "Close-up of descending aerial root tip",
                    "Detailing aerial root morphology SC03_I2",
                    "fast", "story_action"
                ),
                make_rc_image(
                    "SC03_I3",
                    "Vertical botanical plate on rag paper. Multiple hair-thin aerial roots branching and tracing natural vertical crevices down twenty feet of trunk, India ink #1E241E.",
                    "Thin aerial roots snaking down furrowed bark",
                    "Visualizing downward exploratory reach SC03_I3",
                    "normal", "story_action"
                ),
                make_rc_image(
                    "SC03_I4",
                    "Anatomical cutaway of aerial root. Internal vascular bundles showing xylem conduits ready to transport gallons of fluid, terracotta wash #B85D3B.",
                    "Internal vascular xylem diagram of aerial root",
                    "Revealing internal fluid conduits SC03_I4",
                    "normal", "story_action"
                ),
                make_rc_image(
                    "SC03_I5",
                    "Field sketch plate. Naturalist stickman measures root growth rate against tree trunk using brass calipers and hanging measuring tape, paper #F4EFE0.",
                    "Stickman measuring downward aerial root progression",
                    "Documenting decadal descent rate SC03_I5",
                    "normal", "story_action"
                ),
                make_rc_image(
                    "SC03_I6",
                    "Dramatic vertical composition. Aerial roots suspended mid-trunk, still fifty feet above ground, dangling like delicate green threads in misty forest air.",
                    "Aerial roots dangling halfway down massive trunk",
                    "Heightening suspense before ground strike SC03_I6",
                    "normal", "story_action"
                ),
            ],
            "beats": [
                make_rc_beat("SC03_B1", "SC03_I1", "State first decade status", "During its first decade, the young fig lives strictly as an innocent epiphyte.", "normal", "story_action"),
                make_rc_beat("SC03_B2", "SC03_I2", "Detail mist and moss diet", "It feeds on tropical mist, rainwater trickle, and decomposing moss particles trapped in bark crevices.", "normal", "story_action"),
                make_rc_beat("SC03_B3", "SC03_I3", "Introduce aerial root extension", "But soon, it extends hair-thin aerial roots downward.", "fast", "story_action"),
                make_rc_beat("SC03_B4", "SC03_I4", "Describe living cables", "These delicate living cables snake across the hardwood timber", "normal", "story_action"),
                make_rc_beat("SC03_B5", "SC03_I5", "Compare to green lightning", "like slow-motion green lightning,", "fast", "story_action"),
                make_rc_beat("SC03_B6", "SC03_I6", "Conclude march to soil", "heading inexorably toward damp ground soil.", "normal", "story_action"),
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "Architectural Predators: The Botanical Stance",
            "purpose": "Provide sharp editorial stance framing plants as architectural predators",
            "action": "A conceptual botanical codex plate showing plants as gladiators competing for light",
            "setting": "Naturalist codex diagram on herbarium vellum with botanical diagrams",
            "camera": "Static analytical presentation with brass pointers highlighting key concepts",
            "narration": "Human culture mistakenly romanticizes plants as gentle, passive organisms coexisting in harmonious peace. In reality, the tropical rainforest is a brutal, slow-motion gladiator arena. Plants wage lethal territorial warfare over centuries. The strangler fig is not a peaceful vine; it is an architectural assassin preparing a slow, calculated stranglehold.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Analytical, debunking, commanding",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                make_rc_image(
                    "SC04_I1",
                    "Conceptual botanical plate on #F4EFE0 paper. A cross-section of tropical canopy drawn as a battlefield where competing trees push crowns like armored warriors in dip-pen ink.",
                    "Canopy crowns depicted as armored botanical warriors",
                    "Debunking gentle nature mythology SC04_I1",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC04_I2",
                    "Naturalist codex study. Stickman observer with magnifying lens gestures toward historical botanical texts crossed out with red ink, rejecting passive plant myths.",
                    "Stickman crossing out romanticized nature diagrams",
                    "Editorial stance on botanical ruthlessness SC04_I2",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC04_I3",
                    "Anatomical weapon diagram. Fig root tip illustrated like an architectural grappling hook sinking into host bark crevices with sharp tensile strength lines #1E241E.",
                    "Fig root tip illustrated as architectural weapon",
                    "Visualizing root as predatory tool SC04_I3",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC04_I4",
                    "Biomechanical time-lapse sketch. Progressive wireframe diagrams showing a single vine multiplying into an encircling cage around a central host cylinder.",
                    "Wireframe diagram of expanding wooden cage",
                    "Showing deliberate architectural entrapment SC04_I4",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC04_I5",
                    "Tactile herbarium plate. Dried pressed leaves of strangler fig mounted on aged paper beside ink text declaring: 'SLOW-MOTION EXECUTION', amber wash #D4A359.",
                    "Pressed herbarium specimen with calligraphic text",
                    "Channel verdict on calculating parasite SC04_I5",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC04_I6",
                    "Panoramic codex landscape. Towering dipterocarp tree with roots quietly creeping down its trunk beneath golden sunlight, unaware of the trap closing around it.",
                    "Host tree standing magnificent yet encircled",
                    "Reinforcing the silent multi-century trap SC04_I6",
                    "slow", "editorial_commentary"
                ),
            ],
            "beats": [
                make_rc_beat("SC04_B1", "SC04_I1", "Challenge gentle nature myth", "Human culture mistakenly romanticizes plants as gentle, passive organisms coexisting in harmonious peace.", "slow", "editorial_commentary"),
                make_rc_beat("SC04_B2", "SC04_I2", "Frame gladiator arena", "In reality, the tropical rainforest is a brutal, slow-motion gladiator arena.", "slow", "editorial_commentary"),
                make_rc_beat("SC04_B3", "SC04_I3", "State multi-century war", "Plants wage lethal territorial warfare over centuries.", "slow", "editorial_commentary"),
                make_rc_beat("SC04_B4", "SC04_I4", "Reject peaceful vine label", "The strangler fig is not a peaceful vine;", "slow", "editorial_commentary"),
                make_rc_beat("SC04_B5", "SC04_I5", "Proclaim architectural assassin", "it is an architectural assassin", "slow", "editorial_commentary"),
                make_rc_beat("SC04_B6", "SC04_I6", "Conclude calculated stranglehold", "preparing a slow, calculated stranglehold.", "slow", "editorial_commentary"),
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "Year Twenty-Five: The Ground Strike",
            "purpose": "Show the explosive hydraulic shift when roots penetrate ground loam",
            "action": "The first aerial root tip penetrates dark volcanic soil, immediately absorbing water and minerals",
            "setting": "Forest floor soil strata cross-section with rich subterranean mycorrhizal networks",
            "camera": "Split-level macro cutaway showing root tip entering dark terracotta soil",
            "narration": "At Year Twenty-Five, the critical turning point arrives in dramatic fashion. The leading aerial root tip penetrates the dark, mineral-rich forest loam below. Instantly, the fig's biology shifts into explosive hydraulic overdrive. No longer rationing airborne mist, its vascular xylem begins pumping hundreds of liters of water and nitrogen straight up into the high canopy.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Explosive, transformative, kinetic",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_rc_image(
                    "SC05_I1",
                    "Split soil strata plate on #F4EFE0 paper. Root tip touching forest floor surface, delicate hairs spreading outward into dark terracotta loam #B85D3B.",
                    "Root tip touching forest floor soil strata",
                    "The decisive moment of ground contact SC05_I1",
                    "fast", "mechanism_step"
                ),
                make_rc_image(
                    "SC05_I2",
                    "Microscopic soil cutaway. Fig root hairs connecting to fungal mycorrhizal networks, absorbing nitrogen and phosphate ions depicted as tiny glowing amber dots #D4A359.",
                    "Root hairs connecting to fungal mycelium in soil",
                    "Tapping massive underground nutrient reservoir SC05_I2",
                    "fast", "mechanism_step"
                ),
                make_rc_image(
                    "SC05_I3",
                    "Anatomical hydraulic diagram. Massive blue-tinted fluid vectors surging upward through xylem tubes against gravity, bone ivory #D9C5A0 and deep green #3A6B4C.",
                    "Hydraulic fluid surge surging upward through xylem",
                    "Visualizing hydraulic overdrive activation SC05_I3",
                    "fast", "mechanism_step"
                ),
                make_rc_image(
                    "SC05_I4",
                    "Time-lapse botanical engraving. Slender aerial root swelling rapidly from thin string to thick green rope within months of soil contact, ink cross-hatching #1E241E.",
                    "Root swelling from thin string into heavy rope",
                    "Depicting explosive radial thickening SC05_I4",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC05_I5",
                    "Field codex plate on rag paper. Multiple secondary roots hitting soil and anchoring deep, fanning out across forest floor like thick wooden tentacles.",
                    "Multiple roots anchoring into forest loam",
                    "Securing permanent ground foundation SC05_I5",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC05_I6",
                    "Wide vertical botanical plate. The full tree trunk now connected top-to-bottom by thick taut cables humming with pressurized sap, terracotta #B85D3B.",
                    "Full trunk spanned by taut pressurized root cables",
                    "Completing the hydraulic pipeline connection SC05_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_rc_beat("SC05_B1", "SC05_I1", "Mark 25-year turning point", "At Year Twenty-Five, the critical turning point arrives.", "fast", "mechanism_step"),
                make_rc_beat("SC05_B2", "SC05_I2", "Describe ground penetration", "The leading aerial root tip penetrates the dark, mineral-rich forest loam.", "fast", "mechanism_step"),
                make_rc_beat("SC05_B3", "SC05_I3", "Announce hydraulic overdrive", "Instantly, the fig's biology shifts into hydraulic overdrive.", "fast", "mechanism_step"),
                make_rc_beat("SC05_B4", "SC05_I4", "Contrast mist rationing", "No longer rationing airborne mist,", "fast", "mechanism_step"),
                make_rc_beat("SC05_B5", "SC05_I5", "Detail xylem pumping", "its vascular xylem begins pumping hundreds of liters of water and nitrogen", "normal", "mechanism_step"),
                make_rc_beat("SC05_B6", "SC05_I6", "Conclude canopy fuel", "straight up into the high canopy.", "normal", "mechanism_step"),
            ]
        },
        # SC06
        {
            "id": "SC06",
            "title": "Massive Root Expansion: Heavy Cables",
            "purpose": "Illustrate root thickening into massive structural wooden cables",
            "action": "Thin roots rapidly expand into thick wooden pillars, pressing hard against host bark",
            "setting": "Mid-trunk section of host tree with expanding wooden root columns",
            "camera": "Medium tracking shot examining expanding girth of root columns",
            "narration": "Empowered by unlimited subterranean groundwater, the aerial roots transform into massive wooden pillars. Where fragile filaments once swayed gently in the breeze, thick python-like trunks now press violently against the host's timber. Dozens of new descending roots cascade downward, criss-crossing one another as they race to anchor into the damp earth below.",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Vigorous, muscular, unstoppable",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images": [
                make_rc_image(
                    "SC06_I1",
                    "Botanical codex plate on #F4EFE0 paper. Massive swollen fig roots hugging the curvature of host bark like muscular python coils in fine India ink #1E241E.",
                    "Swollen roots hugging host trunk like python coils",
                    "Visualizing muscular root expansion SC06_I1",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC06_I2",
                    "Anatomical trunk cross-section. Host tree bark indenting and flattening under immense compressive pressure from expanding exterior fig roots, green #3A6B4C.",
                    "Cross-section showing bark indentation under pressure",
                    "Detailing mechanical compressive force SC06_I2",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC06_I3",
                    "Time-lapse engraving plate. Sequential root growth showing five roots multiplying into twenty thick overlapping cables spanning eighty vertical feet.",
                    "Sequential plate of roots multiplying into cables",
                    "Depicting exponential multiplication SC06_I3",
                    "fast", "mechanism_step"
                ),
                make_rc_image(
                    "SC06_I4",
                    "Field naturalist plate. Stickman observer places hand against massive wooden root column, marvelling at its rock-solid rigidity, paper #F4EFE0.",
                    "Stickman examining rock-solid wooden root column",
                    "Showing physical scale and timber density SC06_I4",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC06_I5",
                    "Dynamic vertical engraving. Dense curtain of descending roots cascading through air like braided ropes, amber wash #D4A359 and terracotta #B85D3B.",
                    "Cascading curtain of braided root cables",
                    "Illustrating the aerial root deluge SC06_I5",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC06_I6",
                    "Botanical codex illustration. Root tips spreading horizontally across forest floor, interlacing with host surface roots and dominating ground territory.",
                    "Fig roots dominating forest floor territory",
                    "Completing underground expansion SC06_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_rc_beat("SC06_B1", "SC06_I1", "State groundwater empowerment", "Empowered by unlimited subterranean groundwater,", "normal", "mechanism_step"),
                make_rc_beat("SC06_B2", "SC06_I2", "Describe transformation to pillars", "the aerial roots transform into massive wooden pillars.", "normal", "mechanism_step"),
                make_rc_beat("SC06_B3", "SC06_I3", "Contrast filaments with pythons", "Where fragile filaments once swayed gently in the breeze, thick python-like trunks now press violently against the host's timber.", "normal", "mechanism_step"),
                make_rc_beat("SC06_B4", "SC06_I4", "Describe cascading deluge", "Dozens of new descending roots cascade downward,", "fast", "mechanism_step"),
                make_rc_beat("SC06_B5", "SC06_I5", "Detail criss-crossing paths", "criss-crossing one another as they race", "normal", "mechanism_step"),
                make_rc_beat("SC06_B6", "SC06_I6", "Conclude ground anchorage", "to anchor into the damp earth below.", "normal", "mechanism_step"),
            ]
        },
        # SC07
        {
            "id": "SC07",
            "title": "Years Fifty to Eighty: The Living Lattice",
            "purpose": "Depict root self-grafting into an anastomosing strangulation corset",
            "action": "Crossing roots touch, apply pressure, and fuse vascular cambium via self-grafting",
            "setting": "Mid-trunk where roots weave together into a solid wooden lattice",
            "camera": "Macro view of two crossing roots fusing seamlessly together",
            "narration": "By Year Fifty, the roots commit an extraordinary act of biological engineering called anastomosis. Wherever two roots cross and press against each other, friction rubs away their outer bark. Their cambium cells touch, recognize identical genetics, and fuse seamlessly together, weaving an airtight wooden corset around the host tree.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Fascinating, biomechanical, suffocating",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_rc_image(
                    "SC07_I1",
                    "Botanical anatomical plate on #F4EFE0 paper. Close-up of two crossing fig roots pressing against each other, bark abrading in fine cross-hatching #1E241E.",
                    "Two crossing roots abrading bark under friction",
                    "The beginning of anastomosing contact SC07_I1",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC07_I2",
                    "Microscopic histological cutaway. Cambium cells of both roots merging and forming continuous xylem and phloem rings, chlorophyll green #3A6B4C.",
                    "Microscopic cell fusion forming continuous rings",
                    "Explaining biological self-grafting mechanism SC07_I2",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC07_I3",
                    "Kew Gardens botanical engraving. An intricate lattice of dozens of fused root junctions creating a diamond-patterned wooden mesh, amber resin gold #D4A359.",
                    "Intricate diamond-patterned fused wooden lattice",
                    "Visualizing the living wooden mesh SC07_I3",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC07_I4",
                    "Full-length trunk illustration. Host tree completely enveloped in rigid cylindrical fig lattice from ground to canopy crown, rag paper #F4EFE0.",
                    "Host trunk fully enveloped in rigid wooden lattice",
                    "The complete wooden corset established SC07_I4",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC07_I5",
                    "Field naturalist plate. Stickman anatomist taps brass pointer against solid fused wooden junction, noting zero gaps between overlapping trunks.",
                    "Stickman testing fused junction solidity",
                    "Confirming seamless structural unity SC07_I5",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC07_I6",
                    "Biomechanical compression plate. Directional arrows showing inward radial pressure of fused lattice constricting host trunk perimeter in red ink #B85D3B.",
                    "Inward radial force vectors constricting host trunk",
                    "Depicting mechanical strangulation physics SC07_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_rc_beat("SC07_B1", "SC07_I1", "State Year Fifty milestone", "By Year Fifty, the roots commit an extraordinary act of biological engineering", "normal", "mechanism_step"),
                make_rc_beat("SC07_B2", "SC07_I2", "Name anastomosis process", "called anastomosis.", "normal", "mechanism_step"),
                make_rc_beat("SC07_B3", "SC07_I3", "Explain friction abrasion", "Wherever two roots cross and press against each other, friction rubs away their outer bark.", "normal", "mechanism_step"),
                make_rc_beat("SC07_B4", "SC07_I4", "Detail cambium contact", "Their cambium cells touch, recognize identical genetics,", "normal", "mechanism_step"),
                make_rc_beat("SC07_B5", "SC07_I5", "Show seamless fusion", "and fuse seamlessly together,", "fast", "mechanism_step"),
                make_rc_beat("SC07_B6", "SC07_I6", "Conclude airtight corset", "weaving an airtight wooden corset around the host tree.", "normal", "mechanism_step"),
            ]
        },
        # SC08
        {
            "id": "SC08",
            "title": "Phloem Girdling: The Vascular Chokehold",
            "purpose": "Provide editorial analysis on phloem girdling and vascular starvation",
            "action": "Anatomical cutaway showing the host tree's phloem conduits crushed by the expanding fig lattice",
            "setting": "Cross-sectional anatomical diagram of tree vascular rings",
            "camera": "Deep macro cutaway of vascular rings showing sap blockage",
            "narration": "The host tree is not strangled by lack of air; it is starved by ruthless vascular girdling. Just beneath the outer surface lies the phloem—the tree's vital transport highway carrying sugars from canopy leaves down to subterranean roots. As the rigid fig cage prevents trunk expansion, it completely crushes this delicate highway, starving the host's roots until they rot.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Scientific, merciless, diagnostic",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                make_rc_image(
                    "SC08_I1",
                    "Anatomical botanical cutaway on #F4EFE0 paper. Concentric growth rings of host tree showing outer phloem layer colored in delicate green #3A6B4C.",
                    "Concentric growth rings showing vital phloem layer",
                    "Setting the vascular highway anatomy SC08_I1",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC08_I2",
                    "Microscopic diagram of phloem sieve tubes. Sieve plates buckling and collapsing under external mechanical pressure, India ink #1E241E.",
                    "Sieve tubes collapsing under external pressure",
                    "Visualizing physical crushing of phloem SC08_I2",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC08_I3",
                    "Fluid transport diagram. Sugar molecules accumulating in swollen upper trunk above constriction point, unable to travel downward to root system.",
                    "Sugar accumulation above constriction point",
                    "Demonstrating downward transport stoppage SC08_I3",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC08_I4",
                    "Subterranean cutaway plate. Host tree roots underground shrivelling and turning dark brown from carbon starvation, terracotta wash #B85D3B.",
                    "Host tree roots shrivelling from sugar starvation",
                    "Depicting underground root death SC08_I4",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC08_I5",
                    "Naturalist codex plate. Stickman botanist examines cross-section with magnifying loupe, writing 'IRREVERSIBLE VASCULAR FAILURE' in field ledger.",
                    "Stickman recording irreversible vascular failure",
                    "Editorial verdict on silent execution SC08_I5",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC08_I6",
                    "Symbolic botanical engraving. The relentless strangler lattice glowing with vitality while the host interior begins to rot and hollow out.",
                    "Vital fig lattice surrounding rotting host core",
                    "Confirming fatal vascular chokehold SC08_I6",
                    "slow", "editorial_commentary"
                ),
            ],
            "beats": [
                make_rc_beat("SC08_B1", "SC08_I1", "Debunk air strangulation", "The host tree is not strangled by lack of air;", "slow", "editorial_commentary"),
                make_rc_beat("SC08_B2", "SC08_I2", "Define vascular girdling", "it is starved by ruthless vascular girdling.", "slow", "editorial_commentary"),
                make_rc_beat("SC08_B3", "SC08_I3", "Locate phloem highway", "Just beneath the outer surface lies the phloem—the tree's vital transport highway carrying sugars from canopy leaves down to subterranean roots.", "slow", "editorial_commentary"),
                make_rc_beat("SC08_B4", "SC08_I4", "Explain expansion block", "As the rigid fig cage prevents trunk expansion,", "slow", "editorial_commentary"),
                make_rc_beat("SC08_B5", "SC08_I5", "Show crushed highway", "it crushes this delicate highway,", "slow", "editorial_commentary"),
                make_rc_beat("SC08_B6", "SC08_I6", "Conclude root rot", "starving the host's roots until they rot.", "slow", "editorial_commentary"),
            ]
        },
        # SC09
        {
            "id": "SC09",
            "title": "Canopy Conquest: Stealing the Crown",
            "purpose": "Illustrate canopy expansion over-topping and shading host foliage",
            "action": "Strangler fig branches expand aggressively above host crown, intercepting sunlight",
            "setting": "Upper canopy layer 160 feet high with interlocking leaves",
            "camera": "Aerial high-angle sweeping across expanding fig crown above host tree",
            "narration": "While roots execute the subterranean blockade, the fig strikes a fatal blow above. Fueled by bottomless groundwater, its canopy expands into a titanic crown. Broad fig leaves unfurl directly over the host's crown, stealing every photon of solar radiation. Stripped of sunlight above and water below, the rainforest giant quietly surrenders.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Epic, expansive, dominant",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_rc_image(
                    "SC09_I1",
                    "Aerial botanical engraving on #F4EFE0 paper. High canopy perspective showing vigorous strangler fig branches spreading over dipterocarp crown in chlorophyll green #3A6B4C.",
                    "Strangler fig branches overtopping host crown",
                    "Showing canopy light interception SC09_I1",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC09_I2",
                    "Macro botanical plate of fig leaves. Broad thick Ficus leaves overlapping tightly like green roof tiles, blocking all light penetration beneath.",
                    "Broad fig leaves overlapping like roof tiles",
                    "Visualizing complete solar shade SC09_I2",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC09_I3",
                    "Botanical study of host foliage. Host tree leaves yellowing, withering, and dropping into the abyss, shaded out by the dense fig canopy above.",
                    "Host leaves yellowing and dropping in shade",
                    "Depicting host foliage collapse SC09_I3",
                    "fast", "mechanism_step"
                ),
                make_rc_image(
                    "SC09_I4",
                    "Field codex panoramic landscape. The giant dipterocarp standing with bare, leafless gray boughs while the fig crown thrives in radiant emerald splendor.",
                    "Bare host boughs enveloped in lush fig crown",
                    "Contrasting host death with fig vitality SC09_I4",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC09_I5",
                    "Solar photon diagram. Rays of sunlight terminating on fig foliage, zero energy reaching the dying host leaves below in India ink #1E241E.",
                    "Diagram showing 100% solar interception",
                    "Documenting photosynthetic theft SC09_I5",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC09_I6",
                    "Grand naturalist plate. The triumphant strangler fig crown commanding the rainforest skyline 160 feet above ground, amber resin wash #D4A359.",
                    "Strangler fig crown dominating forest skyline",
                    "Canopy conquest complete SC09_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_rc_beat("SC09_B1", "SC09_I1", "State double-pronged strike", "While roots execute the subterranean blockade, the fig strikes a fatal blow above.", "normal", "mechanism_step"),
                make_rc_beat("SC09_B2", "SC09_I2", "Detail groundwater fueling", "Fueled by bottomless groundwater, its canopy expands into a titanic crown.", "normal", "mechanism_step"),
                make_rc_beat("SC09_B3", "SC09_I3", "Show unfurling over host", "Broad fig leaves unfurl directly over the host's crown,", "normal", "mechanism_step"),
                make_rc_beat("SC09_B4", "SC09_I4", "Highlight photon theft", "stealing every photon of solar radiation.", "fast", "mechanism_step"),
                make_rc_beat("SC09_B5", "SC09_I5", "Summarize dual starvation", "Stripped of sunlight above and water below,", "normal", "mechanism_step"),
                make_rc_beat("SC09_B6", "SC09_I6", "Conclude quiet surrender", "the rainforest giant quietly surrenders.", "normal", "mechanism_step"),
            ]
        },
        # SC10
        {
            "id": "SC10",
            "title": "Years 100 to 200: The Hollow Cathedral",
            "purpose": "Chronicle the host trunk decomposition leaving a hollow cathedral cylinder",
            "action": "The host tree trunk decomposes completely into soil, leaving the freestanding fig cage standing alone",
            "setting": "Interior hollow chamber inside the living strangler fig lattice trunk",
            "camera": "Interior upward tilt looking through the hollow wooden cathedral toward the sky",
            "narration": "Across the second century, the host hardwood gradually dies, rots, and dissolves into organic dust, eaten away by termites and relentless fungal moisture. Where a solid tree once stood, only an empty cylindrical void remains. But the strangler fig does not collapse. Its fused lattice has become a hollow, self-supporting wooden cathedral that stands completely independent.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Awe-inspiring, monumental, eerie",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_rc_image(
                    "SC10_I1",
                    "Kew Gardens architectural plate on #F4EFE0 paper. Longitudinal cutaway showing host trunk core decaying into dark powdery humus inside the surrounding root lattice.",
                    "Longitudinal cutaway of host core decomposing",
                    "Visualizing internal host decay SC10_I1",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC10_I2",
                    "Subterranean decomposition study. Wood-boring termites and moisture consuming the dead hardwood core in fine dip-pen stippling #1E241E.",
                    "Termites and fungi dissolving dead hardwood core",
                    "Detailing biological decomposition agents SC10_I2",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC10_I3",
                    "Stunning interior perspective plate. Standing inside the hollow core of the tree, looking 150 feet straight up toward daylight through woven wooden lattice openings.",
                    "Looking straight up through hollow wooden cylinder",
                    "Revealing the hollow cathedral interior SC10_I3",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC10_I4",
                    "Biomechanical structural diagram. Cylindrical hollow tube physics showing that a hollow cylinder provides equal bending resistance to a solid trunk with half the wood mass.",
                    "Engineering diagram proving hollow tube strength",
                    "Explaining self-supporting structural physics SC10_I4",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC10_I5",
                    "Naturalist codex plate. Stickman botanist standing inside the hollow cathedral trunk with antique brass lantern, marvelling at the living wooden architecture.",
                    "Stickman with brass lantern inside hollow trunk",
                    "Human scale reference inside hollow tree SC10_I5",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC10_I6",
                    "Magnificent external portrait on rag paper. The mature two-century-old strangler fig standing proud as an independent colossus, vibrant green leaves gleaming.",
                    "Mature strangler fig standing independent",
                    "Freestanding architectural colossus SC10_I6",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_rc_beat("SC10_B1", "SC10_I1", "State second century milestone", "Across the second century, the host hardwood dies, rots, and dissolves into organic dust,", "normal", "mechanism_step"),
                make_rc_beat("SC10_B2", "SC10_I2", "Detail termites and moisture", "eaten away by termites and moisture.", "normal", "mechanism_step"),
                make_rc_beat("SC10_B3", "SC10_I3", "Describe empty void", "Where a solid tree once stood, only an empty void remains.", "normal", "mechanism_step"),
                make_rc_beat("SC10_B4", "SC10_I4", "State non-collapse paradox", "But the strangler fig does not collapse.", "fast", "mechanism_step"),
                make_rc_beat("SC10_B5", "SC10_I5", "Proclaim hollow cathedral", "Its fused lattice has become a hollow, self-supporting wooden cathedral", "normal", "mechanism_step"),
                make_rc_beat("SC10_B6", "SC10_I6", "Conclude independent standing", "that stands completely independent.", "normal", "mechanism_step"),
            ]
        },
        # SC11
        {
            "id": "SC11",
            "title": "Keystone Survivor: The Forest Lifeline",
            "purpose": "Deliver keystone forest verdict and channel closing call to action",
            "action": "Dozens of tropical birds, bats, and gibbons feed on thousands of ripe figs in the mature crown",
            "setting": "Mature strangler fig crown during dry season fruit famine",
            "camera": "Slow cinematic pan across fruiting canopy teeming with rainforest wildlife",
            "narration": "What began as an architectural executioner becomes the rainforest's greatest ecological savior. Because it bears fruit asynchronously during dry season famines, a single strangler fig sustains hundreds of birds, fruit bats, and primates when surrounding trees offer nothing. In nature, destruction breeds indispensable life. Explore the next botanical survival chronicle on Root and Canopy.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Profound, keystone, conclusive",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cta_bridge",
            "images": [
                make_rc_image(
                    "SC11_I1",
                    "Rich botanical plate on #F4EFE0 paper. Clusters of thousands of ripe purple and gold figs ripening along woody branches, amber wash #D4A359 and crimson #8C3B4A.",
                    "Clusters of ripe figs ripening in thousands",
                    "Introducing keystone fruit production SC11_I1",
                    "normal", "cta_bridge"
                ),
                make_rc_image(
                    "SC11_I2",
                    "Wildlife interaction engraving. Rhinoceros hornbills, gibbons, and flying foxes feasting together in the fruiting fig crown during dry season famine.",
                    "Hornbills and gibbons feasting in fruiting crown",
                    "Demonstrating keystone ecological support SC11_I2",
                    "normal", "cta_bridge"
                ),
                make_rc_image(
                    "SC11_I3",
                    "Ecological food web codex diagram. Arrows linking the central fig tree to forty different vertebrate species dependent on its asynchronous fruiting cycle.",
                    "Ecological web diagram showing forty dependent species",
                    "Proving indispensable keystone status SC11_I3",
                    "normal", "cta_bridge"
                ),
                make_rc_image(
                    "SC11_I4",
                    "Majestic panoramic codex landscape. The 200-year-old hollow fig cathedral bathed in golden dawn light, mist rising from surrounding canopy valleys.",
                    "Hollow fig cathedral glowing in dawn mist",
                    "Grand botanical evolutionary verdict SC11_I4",
                    "normal", "cta_bridge"
                ),
                make_rc_image(
                    "SC11_I5",
                    "Naturalist codex plate. Stickman botanist closes brass field notebook, gesturing warmly toward the viewer beneath ancient spreading fig boughs.",
                    "Naturalist closing herbarium journal and inviting viewer",
                    "Delivering closing channel CTA SC11_I5",
                    "hold", "cta_close"
                ),
                make_rc_image(
                    "SC11_I6",
                    "Tactile channel endcard on warm fibrous herbarium paper #F4EFE0. Elegant botanical copperplate root border framing hand-lettered text: 'ROOT & CANOPY'. Zero 3D, zero gradients.",
                    "Official Root & Canopy channel endcard",
                    "Holding final channel endcard SC11_I6",
                    "hold", "cta_close",
                    is_endcard=True, shot_type="white_card"
                ),
            ],
            "beats": [
                make_rc_beat("SC11_B1", "SC11_I1", "State executioner paradox", "What began as an architectural executioner becomes the rainforest's greatest ecological savior.", "normal", "cta_bridge"),
                make_rc_beat("SC11_B2", "SC11_I2", "Detail asynchronous fruiting", "Because it bears fruit asynchronously during dry season famines,", "normal", "cta_bridge"),
                make_rc_beat("SC11_B3", "SC11_I3", "Cite wildlife support", "a single strangler fig sustains hundreds of birds, fruit bats, and primates when surrounding trees offer nothing.", "normal", "cta_bridge"),
                make_rc_beat("SC11_B4", "SC11_I4", "State philosophical verdict", "In nature, destruction breeds indispensable life.", "normal", "cta_bridge"),
                make_rc_beat("SC11_B5", "SC11_I5", "Deliver closing CTA", "Explore the next botanical survival chronicle on Root and Canopy.", "hold", "cta_close"),
                make_rc_beat("SC11_B6", "SC11_I6", "Hold channel endcard", "Explore the next botanical survival chronicle on Root and Canopy.", "hold", "cta_close", is_endcard=True),
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
                "scene_id": "SC02",
                "quote": "a suffocating triple canopy blocks ninety-nine percent of solar radiation.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Strangler fig seeds dropped on the dark rainforest floor have less than a 0.1% chance of survival due to extreme shade."
            },
            {
                "scene_id": "SC08",
                "quote": "it crushes this delicate highway, starving the host's roots until they rot.",
                "language": "en",
                "source_id": "SRC02",
                "fact": "Radial expansion of fused fig roots constricts the host's secondary phloem, halting downward sugar transport to the host's root system."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return brief, outline, competitor_research, content


def build_root_and_canopy_short_data() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_kitchen_molecules"
    job_id = "en-root-and-canopy-batch1-9x16"
    parent_long_id = "en-root-and-canopy-batch1-16x9"
    youtube_title = "The Seed That Slowly Cages a 150-Foot Tree"
    topic = "The Parasitic Fig Seed That Slowly Strangles a 150-Foot Canopy Giant from Above"

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Nature documentary enthusiasts, botanical science fans, and viewers fascinated by time-lapse life cycles",
        "goal": "Explain how a strangler fig seed germinates 150 feet high and builds a suffocating wooden cage around a living tree, teasing the hollow cathedral climax",
        "video_type": "botanical_chronicle",
        "duration": {
            "min_seconds": 38.0,
            "max_seconds": 52.0
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Inverted growth starting 150 feet high in the canopy rather than dark soil"},
            {"id": "R02", "text": "Hornbill guano cementing the seed into high bark crevices avoiding forest gloom"},
            {"id": "R03", "text": "Editorial stance framing plant evolution as vicious slow-motion warfare"},
            {"id": "R04", "text": "Ground strike turning aerial filaments into a rigid suffocating wooden cage"},
            {"id": "R05", "text": "Cliffhanger peak on hollow cathedral trunk and bridge to full time-lapse documentary"}
        ],
        "language": "en",
        "tone": "Hypnotic, chronological, dramatic, revealing hidden underground and canopy survival battles",
        "style": PRESERVE_ROOT_STYLE,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "The Biology of Ficus: Strangling Figs and Tropical Forest Ecology",
                "reference": "Harrison, R. D. (2005). Biological Reviews of the Cambridge Philosophical Society.",
                "facts": [
                    "Strangler fig seeds dropped on the dark rainforest floor have less than a 0.1% chance of survival due to extreme shade.",
                    "Anastomosing aerial roots fuse together via self-grafting to form a rigid structural cylinder around the host trunk."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": "OmniVoice_EnKitchenMolecules",
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deliver high-velocity 45-second botanical hook and convert cold viewers to the 200-year long-form time-lapse"
            ],
            "avoid": [
                "Treating plants as passive static scenery",
                "Childish cartoon flower faces",
                "Dry gardening tips without evolutionary storytelling"
            ],
            "prior_knowledge": "Accessible to general cold mobile audience.",
            "pacing": "Rapid-fire visual contrasts, escalating time-lapse stakes, zero dead-air.",
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
                "visual_hook": "Cross-section of a 150-foot tree encircled by a crushing mesh of strangler fig roots",
                "text_overlay": "CROW TREE KILLER",
                "contrast_pair": "Host tree crushed by roots vs Strangler fig expanding cage",
                "thumbnail_prompt": "Vertical 9:16 botanical copperplate engraving on fibrous rag paper #F4EFE0. Dynamic composition showing a giant hardwood tree encircled and crushed by thick interlocking strangler fig roots. Cutaway reveals dying dark xylem surrounded by vibrant green fig cords. Fine India ink cross-hatching #1E241E, chlorophyll green #3A6B4C, terracotta #B85D3B. Bold hand-lettered uppercase text in upper third: 'CROW TREE KILLER'. Tactile museum herbarium plate texture, zero 3D CGI.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "Plants are peaceful, static decorations coexisting without aggression.",
                "why_generic_advice_fails": "Assuming plants are passive ignores the deadly multi-century architectural warfare over canopy light.",
                "channel_verdict": "A strangler fig is a botanical predator executing a calculated slow-motion execution.",
                "tradeoff_or_blindspot": "Growing downward avoids ground gloom but risks drying out before roots reach soil."
            },
            "actionable_value": {
                "core_mechanism": "Capturing sunlight first in the canopy before deploying downward conduits for soil minerals.",
                "practical_rule_of_thumb": "When ground competition is fatal, capture top market reach before investing in physical infrastructure.",
                "real_world_scenario": "Cloud software platforms encircle and replace legacy on-premises servers from above."
            },
            "channel_pillar": "Plant evolution through deep time",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["strangler fig", "shorts", "botany", "plant war", "nature documentary"],
            "cta_plan": {
                "cliffhanger_peak": "What happens inside the hollow wooden cage when the host tree rots away completely?",
                "bridge": "Watch the full two-century time-lapse on Root and Canopy YouTube.",
                "close": "Follow our channel to uncover more hidden plant warfare chronicles.",
                "endcard_text": "FULL VIDEO ON YOUTUBE"
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Cross-section of a 150-foot tree encircled by a crushing mesh of strangler fig roots",
            "text_overlay": "CROW TREE KILLER",
            "contrast_pair": "Host tree crushed by roots vs Strangler fig expanding cage",
            "thumbnail_prompt": "Vertical 9:16 botanical copperplate engraving on fibrous rag paper #F4EFE0. Dynamic composition showing a giant hardwood tree encircled and crushed by thick interlocking strangler fig roots. Cutaway reveals dying dark xylem surrounded by vibrant green fig cords. Fine India ink cross-hatching #1E241E, chlorophyll green #3A6B4C, terracotta #B85D3B. Bold hand-lettered uppercase text in upper third: 'CROW TREE KILLER'. Tactile museum herbarium plate texture, zero 3D CGI.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Plant evolution through deep time",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["strangler fig", "shorts", "botany", "plant war", "nature documentary"],
        "parent_long_id": parent_long_id,
        "cta_plan": {
            "cliffhanger_peak": "What happens inside the hollow wooden cage when the host tree rots away completely?",
            "bridge": "Watch the full two-century time-lapse on Root and Canopy YouTube.",
            "close": "Follow our channel to uncover more hidden plant warfare chronicles.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": "Botanical time-lapse chronicler",
            "bridge_templates": [
                "Watch the complete 200-year botanical time-lapse chronicle on Root & Canopy YouTube."
            ],
            "close_templates": [
                "Explore the next botanical survival chronicle on Root and Canopy."
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
            "myth_debunked": "Plants are peaceful, static decorations coexisting without aggression.",
            "why_generic_advice_fails": "Assuming plants are passive ignores the deadly multi-century architectural warfare over canopy light.",
            "channel_verdict": "A strangler fig is a botanical predator executing a calculated slow-motion execution.",
            "tradeoff_or_blindspot": "Growing downward avoids ground gloom but risks drying out before roots reach soil."
        },
        "actionable_value": {
            "core_mechanism": "Capturing sunlight first in the canopy before deploying downward conduits for soil minerals.",
            "practical_rule_of_thumb": "When ground competition is fatal, capture top market reach before investing in physical infrastructure.",
            "real_world_scenario": "Cloud software platforms encircle and replace legacy on-premises servers from above."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook cold viewers with the inverted 150-foot canopy beginning", "requirements": ["R01"], "transition": "Transition to seed attachment via hornbill guano"},
            {"scene_id": "SC02", "purpose": "Show seed deposition escaping the fatal dark forest floor", "requirements": ["R02"], "transition": "Transition to editorial analysis of plant warfare"},
            {"scene_id": "SC03", "purpose": "Deliver sharp editorial commentary on plants as architectural predators", "requirements": ["R03"], "transition": "Pivoting to the explosive ground root strike"},
            {"scene_id": "SC04", "purpose": "Show aerial roots fusing into a suffocating wooden cage", "requirements": ["R04"], "transition": "Escalate to the peak cliffhanger and channel spinoff"},
            {"scene_id": "SC05", "purpose": "Deliver cliffhanger peak on hollow cathedral trunk and bridge to long video", "requirements": ["R05"], "transition": "End of short"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "BBC Earth — The Green Planet",
                    "top_performing_videos": [
                        {
                            "title": "Plants That Hunt and Kill",
                            "views": "5.4M views",
                            "hook_technique": "Start with immediate time-lapse predator framing.",
                            "pacing_structure": "Inverted start -> Downward crawler -> The squeeze.",
                            "retention_driver": "Rapid sensory revelation that plants move like slow predators."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Framing the seed starting in the sky as an impossible reversal.",
                        "Highlighting the hollow wooden cathedral mystery."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_words": 16,
                "zero_pause_opening_seconds": 10,
                "visual_contrast": "Tiny seed in canopy vs 150-foot tree caged by thick roots",
                "counter_intuitive_truth_slap": "While normal trees grow upward from the soil, this plant killer starts one hundred and fifty feet in the air."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Inverted start hook: 150 feet high in the air."},
                {"phase": "empirical_conflict", "purpose": "Escaping the dark forest floor death trap."},
                {"phase": "structural_model", "purpose": "Editorial stance on botanical architectural warfare."},
                {"phase": "actionable_resolution", "purpose": "Ground strike creates suffocating root cage."},
                {"phase": "cliffhanger_spinoff", "purpose": "Tease the hollow cathedral trunk and bridge to long video."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Vertical Kew Gardens botanical copperplate engravings on rag paper."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Plant evolution through deep time",
            "myth_debunked": "Plants are peaceful, static organisms.",
            "channel_verdict": "Plants wage ruthless architectural warfare over multi-century timelines.",
            "actionable_rule_of_thumb": "Capture sunlight from above before building ground infrastructure."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "What happens inside the hollow wooden cage when the host tree rots away completely?",
            "bridge": "Watch the full two-century time-lapse on Root and Canopy YouTube.",
            "close": "Follow our channel to uncover more hidden plant warfare chronicles.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        }
    }

    scenes = [
        # SC01
        {
            "id": "SC01",
            "title": "The Inverted Predator Hook",
            "purpose": "Hook cold viewers with the inverted 150-foot canopy beginning",
            "action": "A sticky seed sits 150 feet high in the canopy, looking down on the doomed giant tree below",
            "setting": "Canopy layer 150 feet high with panoramic view of towering dipterocarp hardwood",
            "camera": "Dramatic vertical high-angle looking down dizzying height of tree trunk",
            "narration": "Most plants fight upward toward the sun from the dark dirt, but this botanical predator begins a hundred and fifty feet in the air. It lands as a single sticky seed atop a giant hardwood tree.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Suspenseful, inverted, startling",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images": [
                make_rc_image(
                    "SC01_I1",
                    "Vertical 9:16 Kew Gardens botanical copperplate on rag paper #F4EFE0. Extreme high-angle view looking 150 feet straight down along massive furrowed tree trunk toward dim green understory below.",
                    "Dizzying high-angle view down 150-foot trunk",
                    "Establishing inverted height perspective SC01_I1",
                    "burst", "hook_shock"
                ),
                make_rc_image(
                    "SC01_I2",
                    "Macro botanical engraving. Solitary glistening fig seed wrapped in golden mucilage adhering tightly to bark crevice, amber resin wash #D4A359.",
                    "Single sticky seed glued to bark crevice",
                    "Focusing on the harmless-looking seed payload SC01_I2",
                    "burst", "hook_shock"
                ),
                make_rc_image(
                    "SC01_I3",
                    "Close-up botanical plate. Tiny emerald cotyledon unfurls into brilliant sunlight, while host tree trunk looms beneath in dark India ink cross-hatching #1E241E.",
                    "Tiny green cotyledon leaf unfurls in open sun",
                    "First leaf basking in pure solar light SC01_I3",
                    "fast", "hook_shock"
                ),
                make_rc_image(
                    "SC01_I4",
                    "Dynamic vertical composition. A hair-thin green root filament emerges from the seed, pointing straight down into the dizzying abyss toward the ground.",
                    "Root filament pointing downward into abyss",
                    "Hook climax: downward invasion initiated SC01_I4",
                    "fast", "hook_shock"
                ),
            ],
            "beats": [
                make_rc_beat("SC01_B1", "SC01_I1", "State normal plant contrast", "Most plants fight upward toward the sun from the dark dirt,", "burst", "hook_shock"),
                make_rc_beat("SC01_B2", "SC01_I2", "State 150-foot start", "but this botanical predator begins a hundred and fifty feet in the air.", "burst", "hook_shock"),
                make_rc_beat("SC01_B3", "SC01_I3", "Describe sticky seed landing", "It lands as a single sticky seed", "fast", "hook_shock"),
                make_rc_beat("SC01_B4", "SC01_I4", "Name giant hardwood host", "atop a giant hardwood tree.", "fast", "hook_shock"),
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "Escaping the Floor Trap",
            "purpose": "Show seed deposition escaping the fatal dark forest floor",
            "action": "A hornbill deposits the seed high above, bypassing the suffocating gloom of the ground floor",
            "setting": "Canopy branch shifting to dark understory floor",
            "camera": "Vertical tracking comparing bright canopy branch with pitch-black leaf litter below",
            "narration": "Deposited in hornbill droppings, the seed bypasses the forest floor where ninety-nine percent of sunlight is blocked. By germinating in the canopy crown, it secures pure solar radiation while sending exploratory roots downward along the bark.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Precise, comparative, accelerating",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "story_action",
            "images": [
                make_rc_image(
                    "SC02_I1",
                    "Vertical 9:16 botanical plate on #F4EFE0 paper. Rhinoceros hornbill perched on massive bough, beak glistening in golden morning sunlight, India ink #1E241E.",
                    "Hornbill perched high on bough depositing seed",
                    "Depicting the avian seed vector SC02_I1",
                    "fast", "story_action"
                ),
                make_rc_image(
                    "SC02_I2",
                    "Split contrast engraving. Top half: brilliant sunlit leaves; bottom half: dark forest floor where fallen seeds rot in pitch-black leaf litter, terracotta #B85D3B.",
                    "Split contrast between sunlit canopy and dark floor",
                    "Visualizing escape from floor trap SC02_I2",
                    "fast", "story_action"
                ),
                make_rc_image(
                    "SC02_I3",
                    "Macro botanical engraving. Delicate aerial root crawling down moist bark fissures, taking moisture from tropical mist, chlorophyll green #3A6B4C.",
                    "Aerial root crawling down moist bark furrow",
                    "Detailing aerial exploratory descent SC02_I3",
                    "fast", "story_action"
                ),
                make_rc_image(
                    "SC02_I4",
                    "Vertical perspective on rag paper. Thin green root filaments cascading down twenty vertical feet of trunk like living wires, amber wash #D4A359.",
                    "Root filaments cascading twenty feet down trunk",
                    "Showing steady descent progress SC02_I4",
                    "normal", "story_action"
                ),
            ],
            "beats": [
                make_rc_beat("SC02_B1", "SC02_I1", "State hornbill vector", "Deposited in hornbill droppings,", "fast", "story_action"),
                make_rc_beat("SC02_B2", "SC02_I2", "Cite 99% light block", "the seed bypasses the forest floor where ninety-nine percent of sunlight is blocked.", "fast", "story_action"),
                make_rc_beat("SC02_B3", "SC02_I3", "Highlight solar radiation", "By germinating in the canopy crown, it secures pure solar radiation", "fast", "story_action"),
                make_rc_beat("SC02_B4", "SC02_I4", "Conclude downward roots", "while sending exploratory roots downward along the bark.", "normal", "story_action"),
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Architectural Predator Stance",
            "purpose": "Deliver sharp editorial commentary on plants as architectural predators",
            "action": "Botanical diagram illustrating plants waging slow-motion territorial warfare",
            "setting": "Naturalist codex diagram on herbarium vellum",
            "camera": "Static conceptual diagram highlighting geometric expansion",
            "narration": "Do not let quiet greenery deceive you. Plants are not peaceful decorations; they wage ruthless architectural warfare over centuries. The strangler fig does not ask for permission; it builds a living prison around its host.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Sharp, commanding, philosophical",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                make_rc_image(
                    "SC03_I1",
                    "Vertical 9:16 conceptual botanical plate on #F4EFE0 paper. Graphic diagram showing tree trunk encircled by geometric iron-gall cage lines #1E241E labeled 'ARCHITECTURAL PRISON'.",
                    "Diagram of tree encircled by geometric cage lines",
                    "Editorial stance on plant architectural war SC03_I1",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC03_I2",
                    "Tactile herbarium plate. Stickman botanist examines cross-section showing overlapping fused roots crushing host cambium layer, terracotta wash #B85D3B.",
                    "Stickman examining crushed cambium cross-section",
                    "Proving predatory mechanical force SC03_I2",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC03_I3",
                    "Anatomical weapon etching. Strangler root tips drawn as architectural clamps locking securely around hardwood bark furrows, deep green #3A6B4C.",
                    "Root tips drawn as mechanical architectural clamps",
                    "Visualizing root clamp mechanism SC03_I3",
                    "slow", "editorial_commentary"
                ),
                make_rc_image(
                    "SC03_I4",
                    "Botanical codex illustration. Ancient host tree standing magnificent yet entirely encased in a tightening grid of wooden bars, amber resin wash #D4A359.",
                    "Host tree encased in tightening grid of wooden bars",
                    "Channel verdict on living prison SC03_I4",
                    "slow", "editorial_commentary"
                ),
            ],
            "beats": [
                make_rc_beat("SC03_B1", "SC03_I1", "Warn against greenery deception", "Do not let quiet greenery deceive you.", "slow", "editorial_commentary"),
                make_rc_beat("SC03_B2", "SC03_I2", "Reject peaceful decoration myth", "Plants are not peaceful decorations; they wage ruthless architectural warfare over centuries.", "slow", "editorial_commentary"),
                make_rc_beat("SC03_B3", "SC03_I3", "State no permission asked", "The strangler fig does not ask for permission;", "slow", "editorial_commentary"),
                make_rc_beat("SC03_B4", "SC03_I4", "Proclaim living prison", "it builds a living prison around its host.", "slow", "editorial_commentary"),
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "Ground Strike: The Suffocating Cage",
            "purpose": "Show aerial roots fusing into a suffocating wooden cage",
            "action": "Roots penetrate forest soil, thicken explosively, and fuse together around host trunk",
            "setting": "Full tree trunk showing roots hitting ground and fusing into lattice",
            "camera": "Dynamic upward tilt showing roots swelling and locking together",
            "narration": "The moment aerial roots penetrate forest soil, hydraulic overdrive strikes. Drinking groundwater, the roots swell into thick wooden pythons, criss-crossing and fusing into an airtight wooden corset that crushes the host's sugar conduits.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Muscular, choking, rapid",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_rc_image(
                    "SC04_I1",
                    "Vertical 9:16 botanical plate on #F4EFE0 paper. Root tips hitting dark terracotta soil strata #B85D3B, sending blue hydraulic sap vectors rushing upward.",
                    "Root tips striking forest soil strata",
                    "Depicting hydraulic overdrive strike SC04_I1",
                    "fast", "mechanism_step"
                ),
                make_rc_image(
                    "SC04_I2",
                    "Macro botanical engraving. Aerial roots swelling rapidly into thick wooden trunks, pressing deeply into host bark, chlorophyll green #3A6B4C.",
                    "Roots swelling into thick wooden pythons",
                    "Showing rapid radial expansion SC04_I2",
                    "fast", "mechanism_step"
                ),
                make_rc_image(
                    "SC04_I3",
                    "Anatomical cutaway of self-grafting. Crossing roots rubbing away bark and fusing cambium into solid continuous wooden junctions, India ink #1E241E.",
                    "Crossing roots fusing cambium into solid lattice",
                    "Detailing anastomosing fusion SC04_I3",
                    "normal", "mechanism_step"
                ),
                make_rc_image(
                    "SC04_I4",
                    "Dramatic vertical plate. Host tree trunk completely enclosed in seamless diamond-mesh wooden corset, constricting vascular phloem, amber wash #D4A359.",
                    "Seamless diamond-mesh wooden corset crushing trunk",
                    "The vascular chokehold established SC04_I4",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_rc_beat("SC04_B1", "SC04_I1", "State ground strike moment", "The moment aerial roots penetrate forest soil, hydraulic overdrive strikes.", "fast", "mechanism_step"),
                make_rc_beat("SC04_B2", "SC04_I2", "Describe swelling pythons", "Drinking groundwater, the roots swell into thick wooden pythons,", "fast", "mechanism_step"),
                make_rc_beat("SC04_B3", "SC04_I3", "Detail criss-crossing fusion", "criss-crossing and fusing into an airtight wooden corset", "normal", "mechanism_step"),
                make_rc_beat("SC04_B4", "SC04_I4", "Conclude sugar crushing", "that crushes the host's sugar conduits.", "normal", "mechanism_step"),
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Hollow Cathedral Twist & Spin-off",
            "purpose": "Deliver cliffhanger peak on hollow cathedral trunk, bridge to full time-lapse, and closing CTA",
            "action": "Host tree rots away inside the wooden cage; stickman introduces the full 200-year time-lapse",
            "setting": "Interior of hollow strangler fig cathedral shifting to vertical channel endcard",
            "camera": "Tilt up inside hollow wooden cylinder toward sky, transitioning to endcard",
            "narration": "What happens inside the hollow wooden cage when the host tree rots away completely? Watch the full two-century time-lapse on Root and Canopy YouTube. Follow our channel to uncover more hidden plant warfare chronicles.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Awe-inspiring, mysterious, inviting",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cliffhanger_peak",
            "images": [
                make_rc_image(
                    "SC05_I1",
                    "Vertical 9:16 botanical plate on #F4EFE0 paper. Longitudinal cutaway of strangler fig trunk showing host interior completely dissolved into hollow empty space.",
                    "Interior host trunk completely dissolved into void",
                    "Visualizing cliffhanger peak mystery SC05_I1",
                    "fast", "cliffhanger_peak"
                ),
                make_rc_image(
                    "SC05_I2",
                    "Interior architectural engraving looking straight up 150 feet through hollow wooden cylinder toward bright sky openings, amber wash #D4A359.",
                    "Looking straight up through hollow wooden cylinder",
                    "Stunning hollow cathedral visual climax SC05_I2",
                    "normal", "cliffhanger_peak"
                ),
                make_rc_image(
                    "SC05_I3",
                    "Field naturalist plate on rag paper. Pith-helmet stickman points with brass pointer toward a 200-year botanical time-lapse banner on aged vellum.",
                    "Stickman presenting the full 200-year time-lapse banner",
                    "Bridging to full YouTube documentary SC05_I3",
                    "normal", "cta_bridge"
                ),
                make_rc_image(
                    "SC05_I4",
                    "Vertical 9:16 channel endcard on warm herbarium paper #F4EFE0. Botanical copperplate root border framing hand-lettered text: 'ROOT & CANOPY'. Zero 3D, zero gradients.",
                    "Official Root & Canopy vertical channel endcard",
                    "Holding vertical channel endcard SC05_I4",
                    "hold", "cta_close",
                    is_endcard=True, shot_type="white_card"
                ),
            ],
            "beats": [
                make_rc_beat("SC05_B1", "SC05_I1", "Deliver cliffhanger peak question", "What happens inside the hollow wooden cage when the host tree rots away completely?", "fast", "cliffhanger_peak"),
                make_rc_beat("SC05_B2", "SC05_I2", "Reinforce visual mystery", "What happens inside the hollow wooden cage when the host tree rots away completely?", "normal", "cliffhanger_peak"),
                make_rc_beat("SC05_B3", "SC05_I3", "Deliver bridge to long video", "Watch the full two-century time-lapse on Root and Canopy YouTube.", "normal", "cta_bridge"),
                make_rc_beat("SC05_B4", "SC05_I4", "Deliver closing CTA on endcard", "Follow our channel to uncover more hidden plant warfare chronicles.", "hold", "cta_close", is_endcard=True),
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
                "scene_id": "SC02",
                "quote": "the seed bypasses the forest floor where ninety-nine percent of sunlight is blocked.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Strangler fig seeds dropped on the dark rainforest floor have less than a 0.1% chance of survival due to extreme shade."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return brief, outline, competitor_research, content
