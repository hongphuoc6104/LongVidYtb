"""Data definitions for Channel 1: Scale & Bone (en_plain_sight_ai / en_scale_and_bone).

Long Job: sys/runs/en-scale-and-bone-batch1-16x9
Short Job: sys/runs/en-scale-and-bone-batch1-9x16
"""
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


PRESERVE_SCALE_STYLE = (
    "Authentic 19th-century Darwin and Ernst Haeckel naturalist zoological codex on aged cotton rag paper #F2EAD7, "
    "razor-sharp iron-gall dip-pen cross-hatching #1C1917, mineral watercolor washes in olive-scale #4A6B53, "
    "venom ochre #C86D51, bone ivory #D9C5A0, 2D field-expedition stickman naturalist in olive waistcoat #4A6B53, "
    "orthographic 2D, >=60% negative space, tactile engraving grain, zero 3D CGI, zero gradients"
)

MOTION_SUFFIX = "silent visual storytelling, no talking, no lip movement"


def make_sb_image(
    img_id: str,
    desc: str,
    change: str,
    reason: str,
    tempo: str,
    situation: str,
    motion_action: str = "Naturalist lithograph plate camera movement",
    has_character: bool = True,
    is_endcard: bool = False,
    shot_type: str = "full_scene",
) -> Dict[str, Any]:
    m_prompt = f"Tactile 2D naturalist lithograph animation. {motion_action.strip()}, transitioning smoothly into next frame, {MOTION_SUFFIX}"
    return {
        "id": img_id,
        "description": desc,
        "character_ids": ["CH01"] if has_character else [],
        "based_on": None,
        "preserve": PRESERVE_SCALE_STYLE,
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


def make_sb_beat(
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


def build_scale_and_bone_long_data() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_plain_sight_ai"
    job_id = "en-scale-and-bone-batch1-16x9"
    youtube_title = "How a Baby Komodo Survives Its Cannibal Mother"
    topic = "From Buried Egg to Cannibal Forest: How a Baby Komodo Dragon Survives Its Own Mother (Day 1 to Year 5)"

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Nature documentary lovers, evolutionary biology fans, and viewers captivated by survival life-cycles",
        "goal": "Chronicle the high-stakes five-year survival journey of a newborn Komodo dragon escaping cannibalistic adults through canopy refuge and chemical camouflage",
        "video_type": "evolutionary_chronicle",
        "duration": {
            "min_seconds": 150.0,
            "max_seconds": 210.0
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Subterranean egg chamber mechanics and the deciduous keratin egg-tooth"},
            {"id": "R02", "text": "Frantic upward excavation through two feet of suffocating volcanic sand"},
            {"id": "R03", "text": "The coastal sprint as ruptured embryonic fluids alert hunting adult dragons"},
            {"id": "R04", "text": "Evolutionary rationale behind island cannibalism accounting for ten percent of adult diet"},
            {"id": "R05", "text": "Vertical canopy salvation exploiting juvenile weight-to-grip ratio against heavy adults"},
            {"id": "R06", "text": "Arboreal adaptations including prehensile tail counterbalance and recurved climbing claws"},
            {"id": "R07", "text": "The desperate chemical defense of smearing in adult dragon feces and rotting entrails"},
            {"id": "R08", "text": "Jacobson organ sensory deception blinding adult dragons to living juvenile prey"},
            {"id": "R09", "text": "Four years of canopy survival hunting geckos, insects, and tree-dwelling eggs"},
            {"id": "R10", "text": "Subcutaneous osteoderm chainmail mineralization and venom gland maturation"},
            {"id": "R11", "text": "Descent of the armored apex survivor and deep-time evolutionary triumph"}
        ],
        "language": "en",
        "tone": "Visceral, chronological, suspenseful, documentary-grade, grounded in evolutionary biomechanics",
        "style": PRESERVE_SCALE_STYLE,
        "aspect_ratio": "16:9",
        "format_profile": "long_16x9",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "The Behavioral Ecology of the Komodo Monitor",
                "reference": "Auffenberg, W. (1981). University of Florida Press.",
                "facts": [
                    "Young Komodo dragons constitute up to 10% of the total diet of adult Komodos in resource-constrained island ecosystems.",
                    "Juvenile Komodo dragons climb trees within minutes of hatching to avoid predation by conspecific adults."
                ]
            },
            {
                "id": "SRC02",
                "title": "A central role for venom in predation by Varanus komodoensis",
                "reference": "Fry, B. G. et al. (2009). Proceedings of the National Academy of Sciences.",
                "facts": [
                    "Adult Komodo dragons possess dense dermal osteoderms that act as biological chainmail armor against territorial bites.",
                    "Juveniles roll in fecal matter to deter cannibalistic adults relying on the Jacobson's olfactory organ."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "16:9",
                "language": "en",
                "subtitles": True,
                "voice": "OmniVoice_EnPlainSightAI",
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Engage cold documentary audience with visceral life-cycle pacing from subterranean egg to apex predator"
            ],
            "avoid": [
                "Plastic 3D CGI monsters",
                "Dry textbook taxonomy lists without chronological story",
                "Sensationalized fake creature myths"
            ],
            "prior_knowledge": "Accessible to general science enthusiasts without herpetological jargon.",
            "pacing": "Chronological documentary escalation, rigorous forward timeline, zero dead-air.",
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
                "visual_hook": "Cross-section of Komodo hatchling slicing out of leathery egg with adult jaws lurking in background",
                "text_overlay": "BORN TO ESCAPE",
                "contrast_pair": "Fragile 100g hatchling vs Massive 80kg cannibal adult",
                "thumbnail_prompt": "19th-century copperplate zoological codex illustration on aged cotton rag paper #F2EAD7. Close-up cross-section of a miniature Komodo hatchling slicing through a fibrous leathery eggshell with a sharp white keratin egg-tooth. In the shadowed background, the menacing silhouette of an 80kg adult Komodo dragon looms with fork tongue flicking. Fine iron-gall dip-pen cross-hatching #1C1917, olive-green scales #4A6B53, venom ochre #C86D51. Bold hand-lettered uppercase text in upper third: 'BORN TO ESCAPE'. Tactile museum engraving grain, >=60% negative space, zero 3D CGI.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "Animal mothers possess universal nurturing instincts to protect their newborn offspring from environmental threats.",
                "why_generic_advice_fails": "Assuming maternal care ignores severe island energy dynamics where eating young preserves vital breeding biomass.",
                "channel_verdict": "On isolated volcanic islands, survival is cold thermodynamic arithmetic where any unprotected protein becomes fuel.",
                "tradeoff_or_blindspot": "Spending four years exiled in tree fronds limits growth rate but guarantees escape from cannibalistic relatives."
            },
            "actionable_value": {
                "core_mechanism": "Exploiting inverse scaling physics where low juvenile mass enables vertical escape beyond adult gravitational grip.",
                "practical_rule_of_thumb": "When facing insurmountable physical strength, change dimensions entirely by fleeing vertically where weight becomes liability.",
                "real_world_scenario": "Engineers mirror biological scaling limits when lightweight climbing robots scale sheer vertical walls where heavy vehicles fail."
            },
            "channel_pillar": "Reptile & amphibian evolution",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["komodo dragon", "reptile evolution", "animal survival", "herpetology", "nature documentary", "life cycle"],
            "cta_plan": {
                "close": "Follow our next evolutionary survival chronicle on Scale and Bone.",
                "endcard_text": "SCALE & BONE"
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Cross-section of Komodo hatchling slicing out of leathery egg with adult jaws lurking in background",
            "text_overlay": "BORN TO ESCAPE",
            "contrast_pair": "Fragile 100g hatchling vs Massive 80kg cannibal adult",
            "thumbnail_prompt": "19th-century copperplate zoological codex illustration on aged cotton rag paper #F2EAD7. Close-up cross-section of a miniature Komodo hatchling slicing through a fibrous leathery eggshell with a sharp white keratin egg-tooth. In the shadowed background, the menacing silhouette of an 80kg adult Komodo dragon looms with fork tongue flicking. Fine iron-gall dip-pen cross-hatching #1C1917, olive-green scales #4A6B53, venom ochre #C86D51. Bold hand-lettered uppercase text in upper third: 'BORN TO ESCAPE'. Tactile museum engraving grain, >=60% negative space, zero 3D CGI.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Reptile & amphibian evolution",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["komodo dragon", "reptile evolution", "animal survival", "herpetology", "nature documentary", "life cycle"],
        "cta_plan": {
            "close": "Follow our next evolutionary survival chronicle on Scale and Bone.",
            "endcard_text": "SCALE & BONE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": "Field herpetologist narrator",
            "bridge_templates": [
                "Watch the complete Egg-to-Apex reptile survival chronicle on Scale & Bone YouTube."
            ],
            "close_templates": [
                "Follow our next evolutionary survival chronicle on Scale and Bone."
            ],
            "endcard_text": "SCALE & BONE",
            "banned_cta_phrases": [
                "don't forget to like",
                "hit the bell",
                "smash that like",
                "like and subscribe",
                "subscribe to the channel"
            ]
        },
        "editorial_stance": {
            "myth_debunked": "Animal mothers possess universal nurturing instincts to protect their newborn offspring from environmental threats.",
            "why_generic_advice_fails": "Assuming maternal care ignores severe island energy dynamics where eating young preserves vital breeding biomass.",
            "channel_verdict": "On isolated volcanic islands, survival is cold thermodynamic arithmetic where any unprotected protein becomes fuel.",
            "tradeoff_or_blindspot": "Spending four years exiled in tree fronds limits growth rate but guarantees escape from cannibalistic relatives."
        },
        "actionable_value": {
            "core_mechanism": "Exploiting inverse scaling physics where low juvenile mass enables vertical escape beyond adult gravitational grip.",
            "practical_rule_of_thumb": "When facing insurmountable physical strength, change dimensions entirely by fleeing vertically where weight becomes liability.",
            "real_world_scenario": "Engineers mirror biological scaling limits when lightweight climbing robots scale sheer vertical walls where heavy vehicles fail."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Establish subterranean claustrophobia and egg-tooth piercing mechanics", "requirements": ["R01"], "transition": "Shift focus to the vertical struggle through sand"},
            {"scene_id": "SC02", "purpose": "Show the perilous upward dig through dense suffocating volcanic sand", "requirements": ["R02"], "transition": "Transition directly into the open beach gauntlet"},
            {"scene_id": "SC03", "purpose": "Reveal how fluid scents alert prowling cannibalistic adults", "requirements": ["R03"], "transition": "Transition to evolutionary commentary on island predation"},
            {"scene_id": "SC04", "purpose": "Provide sharp editorial analysis on the biological necessity of cannibalism", "requirements": ["R04"], "transition": "Pivoting to the hatchling's vertical escape strategy"},
            {"scene_id": "SC05", "purpose": "Demonstrate the physics of vertical sprint up palm trunks", "requirements": ["R05"], "transition": "Exploring the biomechanics of canopy survival"},
            {"scene_id": "SC06", "purpose": "Detail the tail counterbalance and grip adaptations in treetops", "requirements": ["R06"], "transition": "Escalating to when the dragon must touch the forest floor"},
            {"scene_id": "SC07", "purpose": "Unveil the bizarre chemical disguise of rolling in adult excrement", "requirements": ["R07"], "transition": "Analyzing why the sensory bluff works on adult anatomy"},
            {"scene_id": "SC08", "purpose": "Editorial breakdown of the Jacobson organ and olfactory deception", "requirements": ["R08"], "transition": "Moving into the long multi-year juvenile growth phase"},
            {"scene_id": "SC09", "purpose": "Chronicle the four-year canopy lifestyle hunting geckos and bird nests", "requirements": ["R09"], "transition": "Examining anatomical changes preceding permanent descent"},
            {"scene_id": "SC10", "purpose": "Illustrate internal osteoderm chainmail development and venom glands", "requirements": ["R10"], "transition": "Concluding with the adult descent and evolutionary legacy"},
            {"scene_id": "SC11", "purpose": "Deliver deep-time survival verdict and channel closing call to action", "requirements": ["R11"], "transition": "End of chronicle"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "PBS Eons",
                    "top_performing_videos": [
                        {
                            "title": "When Komodo Dragons Ruled Australia",
                            "views": "2.8M views",
                            "hook_technique": "Connect ancient fossil giant body plans to modern living survivors.",
                            "pacing_structure": "Deep-time origin -> Continental isolation -> Biomechanical adaptations.",
                            "retention_driver": "Visceral evolutionary illustrations grounded in scientific fossil evidence."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Chronological survival timeline from Day 1 to adult apex maturity.",
                        "Tactile anatomical cutaways revealing internal bone and gland structures."
                    ]
                },
                {
                    "channel_name": "TierZoo",
                    "top_performing_videos": [
                        {
                            "title": "The Lizard Tier List",
                            "views": "3.4M views",
                            "hook_technique": "Frame survival traits as min-maxed evolutionary stats.",
                            "pacing_structure": "Strengths -> Matchup vulnerabilities -> Survival verdict.",
                            "retention_driver": "Humorous yet scientifically rigorous breakdown of biological trade-offs."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Highlighting the counter-intuitive absurdity of cannibalistic parents.",
                        "Sharp focus on scaling mechanics: adult weight vs juvenile climbing agility."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_words": 16,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Vulnerable miniature hatchling inside egg vs Looming 80kg cannibal mother outside",
                "counter_intuitive_truth_slap": "A mother Komodo dragon does not nurture her clutch; she treats her own emerging hatchlings as convenient morning calories."
            },
            "narrative_progression_arc": [
                {"phase": "subterranean_birth", "purpose": "Puncturing the egg-tooth barrier in total underground darkness."},
                {"phase": "cannibal_gauntlet", "purpose": "Sprinting across open sand as adult predators converge on scent."},
                {"phase": "vertical_ascent", "purpose": "Escaping adult gravitational weight into the high canopy refuge."},
                {"phase": "chemical_camouflage", "purpose": "Masking reptile scent with adult feces during emergency descents."},
                {"phase": "armored_resurrection", "purpose": "Growing dermal bone chainmail to descend as an apex predator colossus."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Sequential copperplate zoological codex plates on textured cotton rag paper."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Reptile & amphibian evolution",
            "myth_debunked": "Maternal care is a universal vertebrate trait.",
            "channel_verdict": "Survival on resource-depleted islands forces ruthless intraspecific cannibalism and vertical exile.",
            "actionable_rule_of_thumb": "When physical force is asymmetric, exploit vertical terrain where heavy predators cannot follow."
        },
        "cta_and_spinoff_strategy": {
            "close": "Follow our next evolutionary survival chronicle on Scale and Bone.",
            "endcard_text": "SCALE & BONE"
        }
    }

    # 11 Scenes for Long Video
    scenes = [
        # SC01
        {
            "id": "SC01",
            "title": "Hour Zero: The Underground Chamber",
            "purpose": "Introduce the leathery egg and the keratin egg-tooth mechanism",
            "action": "A tiny Komodo hatchling uses its keratin egg-tooth to slit the leathery shell in subterranean darkness",
            "setting": "Subterranean egg chamber two feet beneath sun-baked volcanic soil",
            "camera": "Macro cutaway focusing on snout slicing through fibrous egg membrane",
            "narration": "Two feet beneath the sun-baked volcanic soil of Komodo Island, complete darkness conceals a lethal nursery. Inside a leathery, mineral-encrusted egg, a baby monitor lizard is rapidly exhausting its embryonic oxygen supply. It tilts its snout upward, bracing a specialized keratin egg-tooth against the fibrous shell, slicing through thirty long weeks of subterranean confinement.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Suspenseful, claustrophobic, precise",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images": [
                make_sb_image(
                    "SC01_I1",
                    "Darwin zoological copperplate engraving on aged cotton rag paper #F2EAD7. Cross-section of subterranean volcanic soil chamber showing clustered leathery reptile eggs outlined in dip-pen India ink #1C1917. Naturalist stickman in pith helmet observes with brass calipers.",
                    "Subterranean egg chamber establishing shot",
                    "Establishing dark volcanic underground nest SC01_I1",
                    "burst", "hook_shock",
                    "Fine dip-pen line art gently pans across subterranean reptile egg chamber"
                ),
                make_sb_image(
                    "SC01_I2",
                    "Zoological anatomical engraving on cotton rag paper #F2EAD7. Close-up cross-section of single leathery egg with translucent albumen wash in bone ivory #D9C5A0, coiled miniature Komodo dragon embryo inside.",
                    "Embryo coiled within leathery egg",
                    "Revealing embryo oxygen crisis SC01_I2",
                    "burst", "hook_shock",
                    "Subtle watercolor wash illuminates embryo shifting within shell"
                ),
                make_sb_image(
                    "SC01_I3",
                    "Ernst Haeckel style copperplate etching. Extreme close-up of hatchling snout showing the razor-sharp white keratin egg-tooth pressed against fibrous inner shell membrane, olive-scale green #4A6B53.",
                    "Snout pressing egg-tooth against membrane",
                    "Focusing on the sharp egg-tooth tool SC01_I3",
                    "fast", "hook_shock",
                    "Macro view slowly zooms toward pointed keratin tooth"
                ),
                make_sb_image(
                    "SC01_I4",
                    "Naturalist codex plate on #F2EAD7 paper. The keratin tooth pierces the fibrous shell, viscous clear fluid weeping outward into dark porous sand with iron-gall ink cross-hatching #1C1917.",
                    "First puncture slit in leathery eggshell",
                    "Showing physical puncture of egg barrier SC01_I4",
                    "fast", "hook_shock",
                    "Delicate slit widens as fluid droplets seep through paper fibers"
                ),
                make_sb_image(
                    "SC01_I5",
                    "Zoological field sketch. Hatchling snout emerges through triangular slit, nostrils flaring as fresh subterranean air enters respiratory tract, venom ochre wash #C86D51.",
                    "Hatchling snout protruding from sliced shell",
                    "First breath of air outside egg SC01_I5",
                    "normal", "hook_shock",
                    "Hatchling snout pushes forward gently through torn shell"
                ),
                make_sb_image(
                    "SC01_I6",
                    "Engraved plate on rag paper #F2EAD7. Complete hatchling wriggles out from collapsed parchment egg, slender body covered in yellow-banded juvenile scales beside empty shell fragment.",
                    "Hatchling fully emerged on nest floor",
                    "Completing the subterranean emergence SC01_I6",
                    "normal", "hook_shock",
                    "Hatchling body uncoils onto dark sand floor in fluid motion"
                ),
            ],
            "beats": [
                make_sb_beat("SC01_B1", "SC01_I1", "Establish subterranean darkness", "Two feet beneath the sun-baked volcanic soil of Komodo Island,", "burst", "hook_shock"),
                make_sb_beat("SC01_B2", "SC01_I2", "Introduce embryonic crisis", "complete darkness conceals a lethal nursery. Inside a leathery, mineral-encrusted egg,", "burst", "hook_shock"),
                make_sb_beat("SC01_B3", "SC01_I3", "Depict oxygen exhaustion", "a baby monitor lizard is rapidly exhausting its embryonic oxygen supply.", "fast", "hook_shock"),
                make_sb_beat("SC01_B4", "SC01_I4", "Highlight snout movement", "It tilts its snout upward, bracing a specialized keratin egg-tooth", "fast", "hook_shock"),
                make_sb_beat("SC01_B5", "SC01_I5", "Execute shell slice", "against the fibrous shell, slicing through", "normal", "hook_shock"),
                make_sb_beat("SC01_B6", "SC01_I6", "Conclude 30-week confinement", "thirty long weeks of subterranean confinement.", "normal", "hook_shock"),
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "Day One: The Sand Gauntlet",
            "purpose": "Track the frantic upward excavation through heavy volcanic sand",
            "action": "Newborn Komodo uses needle claws and undulating spine to burrow vertically upward",
            "setting": "Vertical cross-section of deep volcanic sand stratum",
            "camera": "Profile cutaway tracking vertical upward movement",
            "narration": "Puncturing the eggshell is merely the opening hurdle of Day One. Above the newborn rests two vertical feet of compacted, suffocating volcanic sand, heavy enough to crush fragile rib cages. With frantic undulations and needle-sharp claws, the miniature dragon excavates upward against gravity, fighting through crushing black granules toward the scorching heat of the surface.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Strenuous, urgent, physical",
            "narrative_phase": "lived_friction",
            "narrative_situation": "story_action",
            "images": [
                make_sb_image(
                    "SC02_I1",
                    "Copperplate geological cross-section on aged paper #F2EAD7. Strata of black volcanic granules pressing down upon tiny Komodo hatchling digging upward with iron-gall ink cross-hatching #1C1917.",
                    "Hatchling beginning upward vertical dig",
                    "Visualizing suffocating sand burden SC02_I1",
                    "fast", "story_action",
                    "Cross-hatching lines indicate downward pressure of sand"
                ),
                make_sb_image(
                    "SC02_I2",
                    "Zoological plate. Miniature foreclaws with transparent sharp keratin sheaths displacing black volcanic sand grains, fine dip-pen detail in olive wash #4A6B53.",
                    "Extreme close-up of foreclaws scraping sand",
                    "Demonstrating digging biomechanics SC02_I2",
                    "fast", "story_action",
                    "Small claws rake through coarse sand grains continuously"
                ),
                make_sb_image(
                    "SC02_I3",
                    "Anatomical cutaway diagram. Slender rib cage of juvenile monitor lizard expanding slightly beneath flexible skin, resisting external soil pressure with bone ivory lines #D9C5A0.",
                    "Internal skeleton resisting soil compression",
                    "Depicting internal pressure resistance SC02_I3",
                    "normal", "story_action",
                    "Subtle skeletal line art highlights thoracic resilience"
                ),
                make_sb_image(
                    "SC02_I4",
                    "Field codex illustration. Hatchling body undulating like a swimming fish through subterranean dark earth, naturalist stickman measures excavation depth with vintage plumb line.",
                    "Sinusoidal body undulation through sand",
                    "Illustrating swimming locomotion in soil SC02_I4",
                    "fast", "story_action",
                    "Sinusoidal body ripple shifts loose substrate backward"
                ),
                make_sb_image(
                    "SC02_I5",
                    "Lithograph plate on #F2EAD7 paper. Faint sunlight filtering down through top sand layer, casting warm ochre rays #C86D51 into the dark excavation tunnel.",
                    "Sunlight piercing top layer of black sand",
                    "Approaching surface threshold SC02_I5",
                    "fast", "story_action",
                    "Warm ochre rays brighten the top of the dark burrow"
                ),
                make_sb_image(
                    "SC02_I6",
                    "Zoological codex plate. Hatchling head breaks through surface crust into blinding tropical sunlight, dark volcanic sand scattering across dry coastal savanna grasses.",
                    "Snout breaking through dry surface crust",
                    "Reaching open daylight SC02_I6",
                    "normal", "story_action",
                    "Surface sand breaks apart as hatchling head emerges in sunlight"
                ),
            ],
            "beats": [
                make_sb_beat("SC02_B1", "SC02_I1", "State opening hurdle", "Puncturing the eggshell is merely the opening hurdle of Day One.", "fast", "story_action"),
                make_sb_beat("SC02_B2", "SC02_I2", "Detail sand compression", "Above the newborn rests two vertical feet of compacted, suffocating volcanic sand,", "fast", "story_action"),
                make_sb_beat("SC02_B3", "SC02_I3", "Highlight crushing weight", "heavy enough to crush fragile rib cages.", "normal", "story_action"),
                make_sb_beat("SC02_B4", "SC02_I4", "Describe climbing motion", "With frantic undulations and needle-sharp claws,", "fast", "story_action"),
                make_sb_beat("SC02_B5", "SC02_I5", "Show upward fight", "the miniature dragon excavates upward against gravity,", "fast", "story_action"),
                make_sb_beat("SC02_B6", "SC02_I6", "Reach surface heat", "fighting through crushing black granules toward the scorching heat of the surface.", "normal", "story_action"),
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "Coastal Sprint: The Scent of Birth",
            "purpose": "Depict the predatory gauntlet as adult Komodos detect hatching fluids",
            "action": "Massive adult Komodo dragons prowl toward the nest mound, flicking yellow tongues",
            "setting": "Arid coastal scrubland and volcanic beach on Komodo Island",
            "camera": "Wide panoramic landscape contrasting miniature hatchling with titanic adult dragons",
            "narration": "Emerging into blinding daylight brings zero relief or celebration. The scent of ruptured embryonic fluids and egg protein instantly carries on coastal sea winds, alerting massive adult dragons prowling nearby scrubland. Weighed down by eighty kilograms of bone and muscle, adult Komodos actively stalk nesting mounds, ready to swallow whole any newborn that lingers on open ground.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Menacing, predatory, expansive",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "story_action",
            "images": [
                make_sb_image(
                    "SC03_I1",
                    "Expansive 19th-century zoological landscape on aged rag paper #F2EAD7. Arid coastal scrub with stunted lontar palms, tiny hatchling on foreground mound dwarfed by vast savanna.",
                    "Tiny hatchling on vast open coastal landscape",
                    "Establishing vulnerability on open ground SC03_I1",
                    "fast", "story_action",
                    "Wide lens slowly sweeps across windswept volcanic beach"
                ),
                make_sb_image(
                    "SC03_I2",
                    "Tactile dip-pen engraving. Scent vapor wisps drawn as delicate swirling lines carrying from torn eggshell across dry grass, ink cross-hatching #1C1917 and slate wash #2E4361.",
                    "Scent plume drifting across dry grass",
                    "Visualizing airborne embryonic scent SC03_I2",
                    "fast", "story_action",
                    "Delicate engraved scent tendrils drift across frame"
                ),
                make_sb_image(
                    "SC03_I3",
                    "Zoological copperplate plate. A colossal eighty-kilogram adult Komodo dragon emerges from acacia shadows, heavy muscular throat sagging with menacing power, olive scales #4A6B53.",
                    "Colossal adult Komodo emerges from shadows",
                    "Introducing the adult apex predator SC03_I3",
                    "normal", "story_action",
                    "Massive adult reptile steps forward with slow heavy gait"
                ),
                make_sb_image(
                    "SC03_I4",
                    "Macro engraving of adult dragon head. Deeply forked yellow tongue flicks outward into air currents, testing chemical particles with fine dip-pen stippling and ochre wash #C86D51.",
                    "Forked yellow tongue tasting air currents",
                    "Adult detecting chemical scent particles SC03_I4",
                    "fast", "story_action",
                    "Forked yellow tongue extends and retracts with mechanical rhythm"
                ),
                make_sb_image(
                    "SC03_I5",
                    "Split contrast composition. On left, tiny hatchling sprinting at full velocity; on right, massive adult dragon turning head toward the scent trajectory with jaw slightly ajar.",
                    "Hatchling sprinting while adult turns to track",
                    "Building predatory pursuit tension SC03_I5",
                    "fast", "story_action",
                    "Dynamic split view captures sudden directional pursuit"
                ),
                make_sb_image(
                    "SC03_I6",
                    "Dramatic field codex plate. Adult dragon lunges forward, kicking up clouds of dry volcanic dust, while tiny hatchling dashes frantically toward the tree line.",
                    "Adult dragon charges across dry volcanic dust",
                    "Climax of the ground sprint gauntlet SC03_I6",
                    "normal", "story_action",
                    "Dust billows as adult accelerates across dry earth"
                ),
            ],
            "beats": [
                make_sb_beat("SC03_B1", "SC03_I1", "Establish false relief", "Emerging into blinding daylight brings zero relief or celebration.", "fast", "story_action"),
                make_sb_beat("SC03_B2", "SC03_I2", "Introduce scent drift", "The scent of ruptured embryonic fluids and egg protein instantly carries on coastal sea winds,", "fast", "story_action"),
                make_sb_beat("SC03_B3", "SC03_I3", "Reveal lurking adults", "alerting massive adult dragons prowling nearby scrubland.", "fast", "story_action"),
                make_sb_beat("SC03_B4", "SC03_I4", "Contrast physical scale", "Weighed down by eighty kilograms of bone and muscle,", "normal", "story_action"),
                make_sb_beat("SC03_B5", "SC03_I5", "Detail nest-stalking behavior", "adult Komodos actively stalk nesting mounds,", "fast", "story_action"),
                make_sb_beat("SC03_B6", "SC03_I6", "Conclude open ground peril", "ready to swallow whole any newborn that lingers on open ground.", "normal", "story_action"),
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "Evolutionary Logic: Island Cannibalism",
            "purpose": "Provide sharp editorial analysis on why adult dragons cannibalize offspring",
            "action": "Naturalist stickman analyzes ecological food pyramid showing high cannibalism rates",
            "setting": "Naturalist codex diagram on aged cotton paper with balance scales and charts",
            "camera": "Static conceptual diagram with brass magnifier highlighting percentages",
            "narration": "Devouring one's own genetic progeny sounds like evolutionary suicide, but on a resource-starved volcanic island, cannibalism is cold thermodynamic arithmetic. Juvenile monitors represent ten percent of an adult's seasonal protein intake. Natural selection eliminates parental sentimentality when survival requires recycling every calorie back into the dominant breeding population.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Analytical, unsentimental, sharp",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                make_sb_image(
                    "SC04_I1",
                    "Naturalist codex diagram on cotton rag paper #F2EAD7. Hand-drawn ecological food web of Komodo Island showing deer, pigs, and a prominent red-ink cycle connecting adult dragons to juveniles.",
                    "Ecological food web showing cannibalistic loop",
                    "Framing cannibalism in island ecology SC04_I1",
                    "slow", "editorial_commentary",
                    "Brass calipers measure connecting cycle lines on chart"
                ),
                make_sb_image(
                    "SC04_I2",
                    "Scientific lithograph chart. A brass balance scale comparing an arid island's scarce winter prey against the caloric mass of a newborn clutch, bone ivory #D9C5A0 and slate #2E4361.",
                    "Balance scale weighing prey scarcity vs eggs",
                    "Illustrating thermodynamic calculation SC04_I2",
                    "slow", "editorial_commentary",
                    "Scale tilts as symbolic weights drop onto brass pans"
                ),
                make_sb_image(
                    "SC04_I3",
                    "Zoological anatomical cutaway. Stomach contents of an adult Komodo dragon illustrated in copperplate cross-hatching, showing juvenile monitor bones marked with taxonomic ink labels.",
                    "Adult stomach diagram showing juvenile bones",
                    "Visualizing the ten percent diet statistic SC04_I3",
                    "slow", "editorial_commentary",
                    "Magnifying lens glides over internal stomach cross-section"
                ),
                make_sb_image(
                    "SC04_I4",
                    "Field naturalist codex plate. Stickman observer in olive waistcoat stands beside Haeckel reptile skull engravings, gesturing thoughtfully toward cold mathematical calculations on margin.",
                    "Stickman examining skulls and mathematical ratios",
                    "Editorial stance on biological necessity SC04_I4",
                    "slow", "editorial_commentary",
                    "Stickman taps vintage brass pointer against margin notes"
                ),
                make_sb_image(
                    "SC04_I5",
                    "Metaphorical codex illustration. A harsh dry island sun scorching cracked earth, where parental protection is crossed out by a bold iron-gall ink quill stroke.",
                    "Scorched island landscape with crossed-out symbol",
                    "Debunking universal maternal care myth SC04_I5",
                    "slow", "editorial_commentary",
                    "Quill ink stroke settles smoothly across weathered parchment"
                ),
                make_sb_image(
                    "SC04_I6",
                    "Zoological engraving on #F2EAD7. Adult Komodo basking atop volcanic ridge, indifferent and apex, while calories cycle efficiently through the harsh island ecosystem.",
                    "Adult dragon basking atop barren ridge",
                    "Channel verdict on raw island survival SC04_I6",
                    "slow", "editorial_commentary",
                    "Quiet idle view of adult colossus against pale sky"
                ),
            ],
            "beats": [
                make_sb_beat("SC04_B1", "SC04_I1", "Challenge maternal assumption", "Devouring one's own genetic progeny sounds like evolutionary suicide,", "slow", "editorial_commentary"),
                make_sb_beat("SC04_B2", "SC04_I2", "Frame island resource math", "but on a resource-starved volcanic island, cannibalism is cold thermodynamic arithmetic.", "slow", "editorial_commentary"),
                make_sb_beat("SC04_B3", "SC04_I3", "Cite ten percent statistic", "Juvenile monitors represent ten percent of an adult's seasonal protein intake.", "slow", "editorial_commentary"),
                make_sb_beat("SC04_B4", "SC04_I4", "Explain lack of sentiment", "Natural selection eliminates parental sentimentality", "slow", "editorial_commentary"),
                make_sb_beat("SC04_B5", "SC04_I5", "Detail calorie recycling", "when survival requires recycling every calorie", "slow", "editorial_commentary"),
                make_sb_beat("SC04_B6", "SC04_I6", "Conclude on dominant population", "back into the dominant breeding population.", "slow", "editorial_commentary"),
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "Vertical Salvation: Escaping Heavy Jaws",
            "purpose": "Demonstrate how juvenile scaling allows vertical escape from heavy adults",
            "action": "Newborn Komodo scrambles up a rough palm trunk while massive adult fails to climb",
            "setting": "Lontar palm trunk rising from volcanic gravel",
            "camera": "Vertical tracking shot rising up tree trunk with hatchling",
            "narration": "The hatchling possesses one definitive biomechanical advantage: inverse scaling physics. Weighing barely one hundred grams, the agile newborn scrambles vertically up the nearest palm trunk, sinking curved claws into fibrous bark. Adult dragons, burdened by their immense eighty-kilogram mass, cannot overcome gravity; their claws shear through bark as they slide helplessly back to earth.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Dynamic, biomechanical, triumphant",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sb_image(
                    "SC05_I1",
                    "Biomechanical diagram on aged paper #F2EAD7. Weight-to-surface-area ratio comparison: 100g hatchling silhouette beside 80kg adult silhouette with physics force vectors in red ink.",
                    "Biomechanical force vector diagram comparing sizes",
                    "Explaining inverse scaling advantage SC05_I1",
                    "fast", "mechanism_step",
                    "Force arrows indicate downward gravity pull on adult body"
                ),
                make_sb_image(
                    "SC05_I2",
                    "Macro copperplate engraving. Hatchling forefoot with curved needle-claws hooking deeply into the fibrous bark ridges of a palm trunk, olive-scale green #4A6B53.",
                    "Extreme close-up of juvenile claws locking into bark",
                    "Detailing climbing mechanical grip SC05_I2",
                    "fast", "mechanism_step",
                    "Sharp claw tips flex and anchor securely into bark fibers"
                ),
                make_sb_image(
                    "SC05_I3",
                    "Dynamic zoological plate. Juvenile lizard ascends vertically with lightning speed, limbs pumping in rapid alternating gait, black dip-pen lines #1C1917.",
                    "Juvenile sprinting vertically up palm trunk",
                    "Depicting high-speed vertical ascent SC05_I3",
                    "fast", "mechanism_step",
                    "Hatchling scrambles upward in rapid continuous motion"
                ),
                make_sb_image(
                    "SC05_I4",
                    "Engraved illustration from ground level. Massive adult dragon rears onto hind legs, attempting to grip trunk, its heavy claws gouging deep slivers but failing to hold weight.",
                    "Adult dragon attempting to claw up palm trunk",
                    "Showing adult climbing failure SC05_I4",
                    "normal", "mechanism_step",
                    "Adult dragon claws slip down bark with heavy thud"
                ),
                make_sb_image(
                    "SC05_I5",
                    "Zoological codex plate. Bark tearing under massive weight as adult dragon slides back onto gravel with frustrated hiss, yellow fork tongue flicking upward.",
                    "Adult dragon sliding backward onto gravel",
                    "Adult grounded by gravitational weight SC05_I5",
                    "normal", "mechanism_step",
                    "Dust settles as massive adult rests defeated on ground"
                ),
                make_sb_image(
                    "SC05_I6",
                    "Perspective plate on #F2EAD7 paper. Looking downward from four meters high: tiny hatchling peers down safely from palm frond at prowling adult dragon far below.",
                    "View looking down from four meters at adult",
                    "Safe haven established in vertical realm SC05_I6",
                    "normal", "mechanism_step",
                    "Gentle breeze sways palm fronds high above ground"
                ),
            ],
            "beats": [
                make_sb_beat("SC05_B1", "SC05_I1", "State physical advantage", "The hatchling possesses one definitive biomechanical advantage: inverse scaling physics.", "fast", "mechanism_step"),
                make_sb_beat("SC05_B2", "SC05_I2", "Cite 100g weight", "Weighing barely one hundred grams,", "fast", "mechanism_step"),
                make_sb_beat("SC05_B3", "SC05_I3", "Show trunk scramble", "the agile newborn scrambles vertically up the nearest palm trunk, sinking curved claws into fibrous bark.", "fast", "mechanism_step"),
                make_sb_beat("SC05_B4", "SC05_I4", "Contrast adult burden", "Adult dragons, burdened by their immense eighty-kilogram mass,", "normal", "mechanism_step"),
                make_sb_beat("SC05_B5", "SC05_I5", "Explain gravity barrier", "cannot overcome gravity;", "normal", "mechanism_step"),
                make_sb_beat("SC05_B6", "SC05_I6", "Conclude adult failure", "their claws shear through bark as they slide helplessly back to earth.", "normal", "mechanism_step"),
            ]
        },
        # SC06
        {
            "id": "SC06",
            "title": "Arboreal Mastery: The Prehensile Lifeline",
            "purpose": "Explore anatomical adaptations that make treetops a safe nursery",
            "action": "Juvenile Komodo navigates thin canopy branches, using prehensile tail and camouflage",
            "setting": "Canopy layer of tropical rainforest fifteen meters above forest floor",
            "camera": "Close following shot weaving through leaves and branches",
            "narration": "Suspended fifteen meters above danger, the juvenile enters an entirely different existence. Its long, whip-like tail functions as a dynamic counterbalance while stalking along slender twigs. Vivid yellow and green chevron markings disrupt its body outline against dappled canopy foliage, rendering it invisible to passing sea eagles while adult cannibals pace blindly below.",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Lyrical, observant, adaptive",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sb_image(
                    "SC06_I1",
                    "Lush botanical and zoological plate on #F2EAD7 paper. Dense lontar and fig canopy with juvenile Komodo resting along horizontal branch, dappled sunlight washes in olive #4A6B53.",
                    "Juvenile resting among canopy foliage",
                    "Establishing arboreal sanctuary SC06_I1",
                    "normal", "mechanism_step",
                    "Leaves rustle gently as dappled sunlight shifts"
                ),
                make_sb_image(
                    "SC06_I2",
                    "Anatomical study of prehensile tail. Muscular cross-section showing tendon arrangements enabling delicate grasping and balancing along thin branches, dip-pen ink #1C1917.",
                    "Anatomical cross-section of tail tendons",
                    "Explaining tail counterbalance mechanics SC06_I2",
                    "normal", "mechanism_step",
                    "Tail tip curls smoothly around slender twig for support"
                ),
                make_sb_image(
                    "SC06_I3",
                    "Camouflage plate in Ernst Haeckel style. Juvenile skin pattern of bright yellow and emerald chevron bands blending seamlessly with lichen-covered tree bark.",
                    "Chevron scale pattern blending with bark lichen",
                    "Illustrating disruptive camouflage pattern SC06_I3",
                    "normal", "mechanism_step",
                    "Scale pattern dissolves naturally into background lichen"
                ),
                make_sb_image(
                    "SC06_I4",
                    "Field sketch on cotton rag. A Brahminy kite eagle soaring above forest canopy, its shadow gliding across leaves without detecting the motionless juvenile reptile.",
                    "Predatory bird soaring above canopy unaware",
                    "Avian predator avoidance in canopy SC06_I4",
                    "fast", "mechanism_step",
                    "Bird silhouette glides smoothly across upper frame"
                ),
                make_sb_image(
                    "SC06_I5",
                    "Naturalist codex plate. Stickman observer sketches sleeping juvenile dragon draped securely across tree fork, legs dangling relaxed fifteen meters above ground.",
                    "Stickman sketching juvenile sleeping in branch fork",
                    "Showing peaceful arboreal sleeping posture SC06_I5",
                    "normal", "mechanism_step",
                    "Juvenile breathes steadily in safe treetop perch"
                ),
                make_sb_image(
                    "SC06_I6",
                    "Vertical perspective plate. High canopy branches bathed in golden afternoon light, looking down through dense leaf layers to dim forest floor far below.",
                    "Golden canopy light contrasting dim forest floor",
                    "Reinforcing height separation from cannibals SC06_I6",
                    "normal", "mechanism_step",
                    "Warm sunlight filters down through successive green layers"
                ),
            ],
            "beats": [
                make_sb_beat("SC06_B1", "SC06_I1", "Establish fifteen-meter height", "Suspended fifteen meters above danger,", "normal", "mechanism_step"),
                make_sb_beat("SC06_B2", "SC06_I2", "Introduce new existence", "the juvenile enters an entirely different existence.", "normal", "mechanism_step"),
                make_sb_beat("SC06_B3", "SC06_I3", "Detail tail counterbalance", "Its long, whip-like tail functions as a dynamic counterbalance while stalking along slender twigs.", "normal", "mechanism_step"),
                make_sb_beat("SC06_B4", "SC06_I4", "Explain chevron camouflage", "Vivid yellow and green chevron markings disrupt its body outline against dappled canopy foliage,", "fast", "mechanism_step"),
                make_sb_beat("SC06_B5", "SC06_I5", "Highlight eagle avoidance", "rendering it invisible to passing sea eagles", "normal", "mechanism_step"),
                make_sb_beat("SC06_B6", "SC06_I6", "Contrast blind adult pacing", "while adult cannibals pace blindly below.", "normal", "mechanism_step"),
            ]
        },
        # SC07
        {
            "id": "SC07",
            "title": "Chemical Masking: The Putrid Fecal Armor",
            "purpose": "Unveil the extreme chemical disguise of smearing in adult excrement",
            "action": "Juvenile Komodo dragon caught on ground deliberately rolls in adult feces and rotting entrails",
            "setting": "Forest floor clearing with decaying buffalo carcass and dung heap",
            "camera": "Ground-level macro tracking juvenile coating itself in putrid material",
            "narration": "Canopy life is not absolute; young dragons must periodically traverse open ground to reach unharvested fruit trees. When trapped near forest clearings, they resort to one of nature's most extreme chemical defenses. They throw themselves into adult dragon excrement and rotting deer intestines, vigorously coating every millimeter of their scales in rank, putrid filth.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Visceral, shocking, remarkable",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "story_action",
            "images": [
                make_sb_image(
                    "SC07_I1",
                    "Zoological codex plate on rag paper #F2EAD7. Juvenile Komodo climbing down trunk toward forest floor, looking alertly across shadowy undergrowth with ink cross-hatching #1C1917.",
                    "Juvenile descending to ground between trees",
                    "Showing unavoidable ground transit SC07_I1",
                    "fast", "story_action",
                    "Juvenile pauses cautiously at base of tree trunk"
                ),
                make_sb_image(
                    "SC07_I2",
                    "Field sketch of forest floor. Large pile of adult dragon fecal deposits containing calcium bone shards, sketched with dark iron-gall ink and earth-toned washes.",
                    "Adult dragon dung pile with bone shards",
                    "Introducing the fecal armor resource SC07_I2",
                    "fast", "story_action",
                    "Sun flies hover lightly above organic dung deposits"
                ),
                make_sb_image(
                    "SC07_I3",
                    "Dynamic zoological etching. Juvenile dragon deliberately rolls onto its back in pungent dung, vigorously rubbing shoulders and belly across putrid material.",
                    "Juvenile rolling deliberately in dung pile",
                    "Depicting the active coating behavior SC07_I3",
                    "normal", "story_action",
                    "Juvenile twists torso to cover flanks thoroughly"
                ),
                make_sb_image(
                    "SC07_I4",
                    "Macro plate of coated scales. Glossy reptilian scales smeared with dark putrid organic matter, completely concealing vibrant green juvenile chevron patterns.",
                    "Close-up of smeared scales hiding pattern",
                    "Visualizing complete chemical coverage SC07_I4",
                    "fast", "story_action",
                    "Dark protective sludge adheres firmly to keeled scales"
                ),
                make_sb_image(
                    "SC07_I5",
                    "Dramatic field engraving. Adult Komodo lumbering directly into clearing, tongue flicking, just two meters away from the dung-encrusted motionless juvenile.",
                    "Adult dragon approaching encrusted juvenile",
                    "Immediate high-stakes encounter SC07_I5",
                    "fast", "story_action",
                    "Heavy adult dragon strides into immediate foreground"
                ),
                make_sb_image(
                    "SC07_I6",
                    "Suspenseful codex plate. Adult dragon snout sniffs directly over the coated juvenile, then turns away indifferently as juvenile remains frozen like a stone.",
                    "Adult sniffs juvenile and turns away",
                    "Successful chemical bluff payoff SC07_I6",
                    "normal", "story_action",
                    "Adult head swings aside dismissively and moves past"
                ),
            ],
            "beats": [
                make_sb_beat("SC07_B1", "SC07_I1", "Note non-absolute canopy life", "Canopy life is not absolute;", "fast", "story_action"),
                make_sb_beat("SC07_B2", "SC07_I2", "Explain ground crossings", "young dragons must periodically traverse open ground to reach unharvested fruit trees.", "fast", "story_action"),
                make_sb_beat("SC07_B3", "SC07_I3", "Introduce extreme defense", "When trapped near forest clearings, they resort to one of nature's most extreme chemical defenses.", "normal", "story_action"),
                make_sb_beat("SC07_B4", "SC07_I4", "Describe dung roll", "They throw themselves into adult dragon excrement", "fast", "story_action"),
                make_sb_beat("SC07_B5", "SC07_I5", "Detail rotten entrails", "and rotting deer intestines,", "fast", "story_action"),
                make_sb_beat("SC07_B6", "SC07_I6", "Conclude total coating", "vigorously coating every millimeter of their scales in rank, putrid filth.", "normal", "story_action"),
            ]
        },
        # SC08
        {
            "id": "SC08",
            "title": "Jacobson Sensory Bluff: Deceiving Adult Predators",
            "purpose": "Provide sharp editorial analysis on how the chemical disguise fools the Jacobson's organ",
            "action": "Anatomical cutaway of adult dragon palate and Jacobson's organ analyzing scent particles",
            "setting": "Anatomical engraving plate with brass pointer detailing reptile olfactory neuroanatomy",
            "camera": "Detailed anatomical cross-section with cutaway skull",
            "narration": "Dignity does not preserve species; pragmatic deception does. Adult dragons hunt using the vomeronasal Jacobson organ located in the roof of their mouth, capable of registering microscopic airborne lipids. The heavy coating of feces chemically overpowers the juvenile scent, tricking the adult into categorizing its own offspring as stale, repulsive excrement rather than edible living prey.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Scientific, evaluative, revelatory",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                make_sb_image(
                    "SC08_I1",
                    "Vesalius-style anatomical plate on aged paper #F2EAD7. Sagittal cross-section of adult Komodo skull showing deep iron-gall cross-hatching #1C1917 and sensory olfactory nerves.",
                    "Sagittal cross-section of adult Komodo skull",
                    "Establishing anatomical codex layout SC08_I1",
                    "slow", "editorial_commentary",
                    "Anatomical cutaway reveals cranial sensory pathways"
                ),
                make_sb_image(
                    "SC08_I2",
                    "Extreme macro anatomical engraving. Roof of mouth showing the paired pits of the Jacobson organ with olfactory sensory epithelium tinted in venom ochre #C86D51.",
                    "Paired sensory pits of the Jacobson organ",
                    "Focusing on the olfactory target organ SC08_I2",
                    "slow", "editorial_commentary",
                    "Microscopic sensory cilia receive chemical molecules"
                ),
                make_sb_image(
                    "SC08_I3",
                    "Chemical receptor diagram. Molecules of living lizard blood vs sulfurous compounds of rotting fecal matter interacting with olfactory receptor sites in dip-pen ink.",
                    "Molecular receptor comparison diagram",
                    "Explaining chemical receptor saturation SC08_I3",
                    "slow", "editorial_commentary",
                    "Sulfur molecular symbols crowd out blood lipid markers"
                ),
                make_sb_image(
                    "SC08_I4",
                    "Field naturalist plate. Stickman anatomist examines reptile palate model with brass calipers, pointing toward olfactory nerve connection to predatory brain centers.",
                    "Stickman pointing to palate sensory connections",
                    "Editorial stance on sensory bluffing SC08_I4",
                    "slow", "editorial_commentary",
                    "Stickman taps pointer against brainstem signal path"
                ),
                make_sb_image(
                    "SC08_I5",
                    "Conceptual zoological etching. Sensory illusion depicted as a mental filter: adult brain sees a worthless stone heap instead of living lizard flesh.",
                    "Visual representation of predatory mental filter",
                    "Visualizing sensory misdirection payoff SC08_I5",
                    "slow", "editorial_commentary",
                    "Predatory cognitive outline shifts from prey to inert rock"
                ),
                make_sb_image(
                    "SC08_I6",
                    "Naturalist codex plate on #F2EAD7. Young dragon shakes off sand and ascends back into low branches as adult colossus marches away in distance.",
                    "Juvenile re-climbing trunk as adult departs",
                    "Triumph of chemical misdirection SC08_I6",
                    "slow", "editorial_commentary",
                    "Juvenile climbs steadily back toward tree canopy"
                ),
            ],
            "beats": [
                make_sb_beat("SC08_B1", "SC08_I1", "State pragmatic deception thesis", "Dignity does not preserve species; pragmatic deception does.", "slow", "editorial_commentary"),
                make_sb_beat("SC08_B2", "SC08_I2", "Introduce Jacobson organ", "Adult dragons hunt using the vomeronasal Jacobson organ located in the roof of their mouth,", "slow", "editorial_commentary"),
                make_sb_beat("SC08_B3", "SC08_I3", "Explain lipid detection", "capable of registering microscopic airborne lipids.", "slow", "editorial_commentary"),
                make_sb_beat("SC08_B4", "SC08_I4", "Describe fecal overpower", "The heavy coating of feces chemically overpowers the juvenile scent,", "slow", "editorial_commentary"),
                make_sb_beat("SC08_B5", "SC08_I5", "Detail mental miscategorization", "tricking the adult into categorizing its own offspring as stale, repulsive excrement", "slow", "editorial_commentary"),
                make_sb_beat("SC08_B6", "SC08_I6", "Conclude prey avoidance", "rather than edible living prey.", "slow", "editorial_commentary"),
            ]
        },
        # SC09
        {
            "id": "SC09",
            "title": "Years One to Four: Hunting Among the Fronds",
            "purpose": "Chronicle the multi-year arboreal growth phase and predatory development",
            "action": "Juvenile Komodo dragon grows steadily, stalking Tokay geckos, insects, and bird nests",
            "setting": "Canopy canopy transition from sapling fronds to mature hardwood branches",
            "camera": "Dynamic hunting sequence following stalking predator along branches",
            "narration": "For four demanding years, the growing dragon reigns as a ruthless canopy predator. It stalks slumbering Tokay geckos, devours tropical cicadas, and plunders arboreal bird nests. With each season, its body mass expands and jaw musculature thickens. By Year Four, stretching over one meter long, the branch tips begin to groan under its increasing bulk.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Vigorous, developmental, chronological",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sb_image(
                    "SC09_I1",
                    "Zoological codex plate on #F2EAD7. Juvenile Komodo stalking a brightly spotted Tokay gecko on palm frond, fine cross-hatching in olive green #4A6B53 and slate #2E4361.",
                    "Juvenile stalking Tokay gecko on frond",
                    "Demonstrating canopy hunting skills SC09_I1",
                    "normal", "mechanism_step",
                    "Body lowers in slow deliberate stalking creep"
                ),
                make_sb_image(
                    "SC09_I2",
                    "High-speed action etching. Lightning snap of juvenile jaws capturing giant cicada in flight among canopy leaves, wings fluttering in dip-pen detail.",
                    "Lightning jaw snap capturing giant cicada",
                    "Showing lightning strike reflexes SC09_I2",
                    "fast", "mechanism_step",
                    "Jaws snap shut crisply around fluttering prey"
                ),
                make_sb_image(
                    "SC09_I3",
                    "Field codex study. Juvenile dragon raiding weaver bird nest tucked beneath palm leaf, swallowing speckled eggs whole with expanding throat pouch.",
                    "Juvenile raiding weaver bird nest",
                    "Expanding seasonal diet intake SC09_I3",
                    "normal", "mechanism_step",
                    "Throat ripples as smooth egg passes down gullet"
                ),
                make_sb_image(
                    "SC09_I4",
                    "Naturalist timeline plate showing four annual growth stages (Year 1, 2, 3, 4) with measuring rod, body lengthening from 30cm to 1.2m, bone ivory #D9C5A0.",
                    "Four-stage chronological growth comparison plate",
                    "Chronological size progression SC09_I4",
                    "normal", "mechanism_step",
                    "Naturalist stickman shifts measuring rod along silhouettes"
                ),
                make_sb_image(
                    "SC09_I5",
                    "Biomechanical weight plate. Thickened subadult Komodo resting on heavy branch, wooden limb flexing and groaning visibly beneath its seven-kilogram weight.",
                    "Heavy branch sagging under subadult weight",
                    "Signaling end of arboreal phase SC09_I5",
                    "normal", "mechanism_step",
                    "Branch dips slightly downward under increasing mass"
                ),
                make_sb_image(
                    "SC09_I6",
                    "Zoological engraving on cotton rag. Subadult dragon looking downward toward forest floor with steady golden gaze, ready for inevitable terrestrial descent.",
                    "Subadult dragon gazing down toward ground",
                    "Transitioning toward adult descent SC09_I6",
                    "normal", "mechanism_step",
                    "Dragon head turns deliberately toward ground below"
                ),
            ],
            "beats": [
                make_sb_beat("SC09_B1", "SC09_I1", "Establish four-year reign", "For four demanding years, the growing dragon reigns as a ruthless canopy predator.", "normal", "mechanism_step"),
                make_sb_beat("SC09_B2", "SC09_I2", "Detail gecko and cicada diet", "It stalks slumbering Tokay geckos, devours tropical cicadas,", "normal", "mechanism_step"),
                make_sb_beat("SC09_B3", "SC09_I3", "Highlight nest plundering", "and plunders arboreal bird nests.", "normal", "mechanism_step"),
                make_sb_beat("SC09_B4", "SC09_I4", "Describe mass expansion", "With each season, its body mass expands and jaw musculature thickens.", "normal", "mechanism_step"),
                make_sb_beat("SC09_B5", "SC09_I5", "State one-meter milestone", "By Year Four, stretching over one meter long,", "normal", "mechanism_step"),
                make_sb_beat("SC09_B6", "SC09_I6", "Conclude branch strain", "the branch tips begin to groan under its increasing bulk.", "normal", "mechanism_step"),
            ]
        },
        # SC10
        {
            "id": "SC10",
            "title": "The Armored Transformation: Mineralizing Bone Plates",
            "purpose": "Illustrate internal osteoderm chainmail development and venom gland maturation",
            "action": "Anatomical cutaway revealing thousands of osteoderm bone plates mineralizing inside the skin",
            "setting": "Anatomical laboratory plate with microscopic magnification circles",
            "camera": "Deep microscopic zoom into dermal layers revealing bone mineralization",
            "narration": "Before descending, an extraordinary anatomical transformation fortifies the subadult. Embedded within its leathery dermis, thousands of tiny bone deposits called osteoderms mineralize into an internal suit of flexible chainmail armor. Simultaneously, complex venom glands mature within the lower jaw. No longer fragile prey, the young monitor is now an armored, venomous predator.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Awe-inspiring, biomechanical, dense",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sb_image(
                    "SC10_I1",
                    "Histological codex plate on #F2EAD7 paper. Microscopic cross-section of Komodo dragon skin showing epidermis and underlying dermis in fine iron-gall linework.",
                    "Microscopic skin cross-section diagram",
                    "Setting dermal layer architecture SC10_I1",
                    "normal", "mechanism_step",
                    "Microscopic lens focus sharpens on dermal strata"
                ),
                make_sb_image(
                    "SC10_I2",
                    "Anatomical engraving of osteoderms. Rosette clusters of bone mineral deposits forming interlocking mesh inside skin, bone ivory #D9C5A0 and slate ink #1C1917.",
                    "Rosette clusters of bone osteoderms in skin",
                    "Depicting internal chainmail structure SC10_I2",
                    "normal", "mechanism_step",
                    "Mineralized bone rosettes interlock into flexible mesh"
                ),
                make_sb_image(
                    "SC10_I3",
                    "Biomechanical defense diagram. Simulated adult bite showing teeth deflecting off the dense subcutaneous osteoderm chainmail without piercing vital muscles.",
                    "Teeth deflecting off osteoderm bone armor",
                    "Proving bite-proof defense capability SC10_I3",
                    "fast", "mechanism_step",
                    "Sharp tooth point impacts bone plate and slides away"
                ),
                make_sb_image(
                    "SC10_I4",
                    "Cranial anatomical cutaway. Lower jaw dissection showing specialized multichambered venom glands resting along tooth rows, tinted in venom ochre #C86D51.",
                    "Lower jaw cutaway showing venom gland chambers",
                    "Detailing venom apparatus maturation SC10_I4",
                    "normal", "mechanism_step",
                    "Ochre venom ducts glisten inside mandibular grooves"
                ),
                make_sb_image(
                    "SC10_I5",
                    "Naturalist codex plate. Stickman anatomist examines complete articulated osteoderm suit with magnifying glass, nodding in approval at nature's armor.",
                    "Stickman examining complete osteoderm suit",
                    "Reviewing complete armored anatomy SC10_I5",
                    "normal", "mechanism_step",
                    "Stickman sketches interlocking dermal plates carefully"
                ),
                make_sb_image(
                    "SC10_I6",
                    "Powerful zoological portrait. Fully transformed four-year-old Komodo dragon perched on lowest tree branch, muscular and armored, ready for ground life.",
                    "Four-year-old dragon primed on low branch",
                    "Ready to descend as apex predator SC10_I6",
                    "normal", "mechanism_step",
                    "Muscular dragon shifts weight forward with coiled power"
                ),
            ],
            "beats": [
                make_sb_beat("SC10_B1", "SC10_I1", "Introduce pre-descent fortification", "Before descending, an extraordinary anatomical transformation fortifies the subadult.", "normal", "mechanism_step"),
                make_sb_beat("SC10_B2", "SC10_I2", "Detail osteoderm mineralization", "Embedded within its leathery dermis, thousands of tiny bone deposits called osteoderms", "normal", "mechanism_step"),
                make_sb_beat("SC10_B3", "SC10_I3", "Describe chainmail armor", "mineralize into an internal suit of flexible chainmail armor.", "normal", "mechanism_step"),
                make_sb_beat("SC10_B4", "SC10_I4", "Highlight venom gland maturation", "Simultaneously, complex venom glands mature within the lower jaw.", "normal", "mechanism_step"),
                make_sb_beat("SC10_B5", "SC10_I5", "Contrast past fragility", "No longer fragile prey,", "fast", "mechanism_step"),
                make_sb_beat("SC10_B6", "SC10_I6", "Proclaim armored predator", "the young monitor is now an armored, venomous predator.", "normal", "mechanism_step"),
            ]
        },
        # SC11
        {
            "id": "SC11",
            "title": "Descent of the Apex Colossus & Deep-Time Legacy",
            "purpose": "Deliver deep-time survival verdict and channel closing call to action",
            "action": "Four-year-old Komodo dragon steps firmly onto volcanic earth as an apex terrestrial survivor",
            "setting": "Volcanic savanna floor with adult Komodos acknowledging the new rival",
            "camera": "Slow cinematic tracking shot following heavy footsteps on volcanic earth",
            "narration": "At Year Five, claws release the canopy wood and touch volcanic earth permanently. The former hatchling now walks the forest floor as an apex colossus, immune to cannibalistic ambushes. This ruthless five-year gauntlet is how the Komodo lineage conquered three million years of island isolation. Follow our next evolutionary survival chronicle on Scale and Bone.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Majestic, triumphant, conclusive",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cta_bridge",
            "images": [
                make_sb_image(
                    "SC11_I1",
                    "Low-angle copperplate etching on #F2EAD7. Armored clawed foot steps heavily onto dry volcanic earth, dust puffing outward in fine dip-pen lines #1C1917.",
                    "Armored foot touching volcanic earth",
                    "The decisive moment of permanent descent SC11_I1",
                    "normal", "cta_bridge"
                ),
                make_sb_image(
                    "SC11_I2",
                    "Majestic zoological engraving. The five-year-old Komodo dragon strides across savanna floor with steady lateral stride, olive green scales #4A6B53.",
                    "Five-year-old dragon striding across savanna",
                    "Territorial apex swagger established SC11_I2",
                    "normal", "cta_bridge"
                ),
                make_sb_image(
                    "SC11_I3",
                    "Field codex plate. An older adult dragon crosses paths with the newcomer, exchanging deep throat hisses before passing without attacking.",
                    "Adult dragon recognizing newcomer as equal rival",
                    "Immunity from cannibalism confirmed SC11_I3",
                    "normal", "cta_bridge"
                ),
                make_sb_image(
                    "SC11_I4",
                    "Grand evolutionary landscape. Komodo dragons roaming volcanic shoreline against sunset sky, deep-time fossil skull silhouettes etched into distant clouds.",
                    "Deep-time evolutionary panorama of Komodo shoreline",
                    "Three-million-year survival verdict SC11_I4",
                    "normal", "cta_bridge"
                ),
                make_sb_image(
                    "SC11_I5",
                    "Naturalist codex plate. Field stickman naturalist in pith helmet closes leather expedition journal, gesturing warmly toward the viewer with antique brass compass.",
                    "Naturalist closing field codex and inviting viewer",
                    "Delivering closing channel CTA SC11_I5",
                    "hold", "cta_close"
                ),
                make_sb_image(
                    "SC11_I6",
                    "Tactile channel endcard on aged cotton rag paper #F2EAD7. Fine dip-pen reptile skeleton engraving framing elegant hand-lettered banner: 'SCALE & BONE'. Zero 3D, zero gradients.",
                    "Official Scale & Bone channel endcard codex",
                    "Holding final channel endcard SC11_I6",
                    "hold", "cta_close",
                    is_endcard=True, shot_type="white_card"
                ),
            ],
            "beats": [
                make_sb_beat("SC11_B1", "SC11_I1", "Describe permanent ground contact", "At Year Five, claws release the canopy wood and touch volcanic earth permanently.", "normal", "cta_bridge"),
                make_sb_beat("SC11_B2", "SC11_I2", "Proclaim apex colossus", "The former hatchling now walks the forest floor as an apex colossus,", "normal", "cta_bridge"),
                make_sb_beat("SC11_B3", "SC11_I3", "Note cannibal immunity", "immune to cannibalistic ambushes.", "normal", "cta_bridge"),
                make_sb_beat("SC11_B4", "SC11_I4", "State three-million-year legacy", "This ruthless five-year gauntlet is how the Komodo lineage conquered three million years of island isolation.", "normal", "cta_bridge"),
                make_sb_beat("SC11_B5", "SC11_I5", "Deliver closing CTA", "Follow our next evolutionary survival chronicle on Scale and Bone.", "hold", "cta_close"),
                make_sb_beat("SC11_B6", "SC11_I6", "Hold channel endcard", "Follow our next evolutionary survival chronicle on Scale and Bone.", "hold", "cta_close", is_endcard=True),
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
                "quote": "Juvenile monitors represent ten percent of an adult's seasonal protein intake.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Young Komodo dragons constitute up to 10% of the total diet of adult Komodos in resource-constrained island ecosystems."
            },
            {
                "scene_id": "SC10",
                "quote": "thousands of tiny bone deposits called osteoderms mineralize into an internal suit of flexible chainmail armor.",
                "language": "en",
                "source_id": "SRC02",
                "fact": "Adult Komodo dragons possess dense dermal osteoderms that act as biological chainmail armor against territorial bites."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return brief, outline, competitor_research, content


def build_scale_and_bone_short_data() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_plain_sight_ai"
    job_id = "en-scale-and-bone-batch1-9x16"
    parent_long_id = "en-scale-and-bone-batch1-16x9"
    youtube_title = "Why Newborn Komodos Immediately Sprint Up Trees"
    topic = "Why Newborn Komodo Dragons Must Immediately Sprint Up Trees to Escape Their Own Mothers"

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": "Nature documentary lovers, evolutionary biology fans, and viewers captivated by survival life-cycles",
        "goal": "Explain why newborn Komodo dragons must sprint up trees within minutes of hatching to escape cannibalistic adults and tease the fecal armor survival trick",
        "video_type": "evolutionary_chronicle",
        "duration": {
            "min_seconds": 38.0,
            "max_seconds": 52.0
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Shocking realization that the greatest predator outside the egg is the mother"},
            {"id": "R02", "text": "Frantic sprint across open sand toward the nearest tree trunk"},
            {"id": "R03", "text": "Evolutionary reality of island cannibalism consuming ten percent of young"},
            {"id": "R04", "text": "Vertical physics advantage where juvenile claws beat adult gravity"},
            {"id": "R05", "text": "Cliffhanger on grotesque fecal armor trick and bridge to full documentary"}
        ],
        "language": "en",
        "tone": "Visceral, chronological, suspenseful, documentary-grade, grounded in evolutionary biomechanics",
        "style": PRESERVE_SCALE_STYLE,
        "aspect_ratio": "9:16",
        "format_profile": "short_9x16",
        "facts_required": True,
        "sources": [
            {
                "id": "SRC01",
                "title": "The Behavioral Ecology of the Komodo Monitor",
                "reference": "Auffenberg, W. (1981). University of Florida Press.",
                "facts": [
                    "Young Komodo dragons constitute up to 10% of the total diet of adult Komodos in resource-constrained island ecosystems.",
                    "Juvenile Komodo dragons climb trees within minutes of hatching to avoid predation by conspecific adults."
                ]
            }
        ],
        "outputs": [
            {
                "aspect_ratio": "9:16",
                "language": "en",
                "subtitles": True,
                "voice": "OmniVoice_EnPlainSightAI",
                "speed": 1.0
            }
        ],
        "planning": {
            "success_criteria": [
                "Deliver intense 45-second high-retention survival hook and convert viewers to the long-form chronicle"
            ],
            "avoid": [
                "Plastic 3D CGI monsters",
                "Dry textbook taxonomy lists without chronological story",
                "Sensationalized fake creature myths"
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
                "visual_hook": "Newborn Komodo scrambling frantically up tree trunk while enormous adult jaws snap shut inches below",
                "text_overlay": "ESCAPE OR DIE",
                "contrast_pair": "Baby Komodo scrambling up bark vs Giant adult dragon snapping jaws below",
                "thumbnail_prompt": "Vertical 9:16 19th-century zoological copperplate engraving on aged cotton rag paper #F2EAD7. Dynamic vertical composition: tiny newborn Komodo dragon with sharp needle-claws scrambling desperately up rough palm bark. Directly below, the colossal gaping jaws of an adult Komodo dragon snap shut with dripping venom saliva in deep iron-gall cross-hatching #1C1917, olive-green #4A6B53. Bold hand-lettered uppercase text in top third: 'ESCAPE OR DIE'. Tactile museum engraving grain, zero 3D CGI.",
                "layout_mode": "split_contrast"
            },
            "editorial_stance": {
                "myth_debunked": "All animal mothers protect their newborn offspring.",
                "why_generic_advice_fails": "Assuming maternal care ignores harsh island caloric math where young are easy meals.",
                "channel_verdict": "On Komodo Island, adult dragons eat ten percent of their own species without hesitation.",
                "tradeoff_or_blindspot": "Living four years in treetops stops rapid growth but ensures survival from cannibal parents."
            },
            "actionable_value": {
                "core_mechanism": "Exploiting lightweight scaling physics to escape vertically where heavy predators cannot climb.",
                "practical_rule_of_thumb": "When facing overwhelming force, change dimensions by climbing where weight becomes a trap.",
                "real_world_scenario": "Lightweight climbing robots traverse vertical obstacles that trap heavy ground vehicles."
            },
            "channel_pillar": "Reptile & amphibian evolution",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["komodo dragon", "shorts", "reptiles", "nature documentary", "survival"],
            "cta_plan": {
                "cliffhanger_peak": "What grotesque chemical armor allows juvenile dragons to survive when trapped on the forest floor?",
                "bridge": "Watch the full five-year survival breakdown on Scale and Bone YouTube.",
                "close": "Follow our channel for more deep evolutionary survival stories.",
                "endcard_text": "FULL VIDEO ON YOUTUBE"
            }
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Newborn Komodo scrambling frantically up tree trunk while enormous adult jaws snap shut inches below",
            "text_overlay": "ESCAPE OR DIE",
            "contrast_pair": "Baby Komodo scrambling up bark vs Giant adult dragon snapping jaws below",
            "thumbnail_prompt": "Vertical 9:16 19th-century zoological copperplate engraving on aged cotton rag paper #F2EAD7. Dynamic vertical composition: tiny newborn Komodo dragon with sharp needle-claws scrambling desperately up rough palm bark. Directly below, the colossal gaping jaws of an adult Komodo dragon snap shut with dripping venom saliva in deep iron-gall cross-hatching #1C1917, olive-green #4A6B53. Bold hand-lettered uppercase text in top third: 'ESCAPE OR DIE'. Tactile museum engraving grain, zero 3D CGI.",
            "layout_mode": "split_contrast"
        },
        "channel_pillar": "Reptile & amphibian evolution",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["komodo dragon", "shorts", "reptiles", "nature documentary", "survival"],
        "parent_long_id": parent_long_id,
        "cta_plan": {
            "cliffhanger_peak": "What grotesque chemical armor allows juvenile dragons to survive when trapped on the forest floor?",
            "bridge": "Watch the full five-year survival breakdown on Scale and Bone YouTube.",
            "close": "Follow our channel for more deep evolutionary survival stories.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        },
        "channel_profile": channel_profile_stamp(channel_id),
        "engagement": {
            "cta_voice": "Field herpetologist narrator",
            "bridge_templates": [
                "Watch the complete Egg-to-Apex reptile survival chronicle on Scale & Bone YouTube."
            ],
            "close_templates": [
                "Follow our next evolutionary survival chronicle on Scale and Bone."
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
            "myth_debunked": "All animal mothers protect their newborn offspring.",
            "why_generic_advice_fails": "Assuming maternal care ignores harsh island caloric math where young are easy meals.",
            "channel_verdict": "On Komodo Island, adult dragons eat ten percent of their own species without hesitation.",
            "tradeoff_or_blindspot": "Living four years in treetops stops rapid growth but ensures survival from cannibal parents."
        },
        "actionable_value": {
            "core_mechanism": "Exploiting lightweight scaling physics to escape vertically where heavy predators cannot climb.",
            "practical_rule_of_thumb": "When facing overwhelming force, change dimensions by climbing where weight becomes a trap.",
            "real_world_scenario": "Lightweight climbing robots traverse vertical obstacles that trap heavy ground vehicles."
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain"
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook cold viewers with the shocking reality of cannibal mothers", "requirements": ["R01"], "transition": "Transition to the frantic sand breakout sprint"},
            {"scene_id": "SC02", "purpose": "Show the desperate sand sprint toward vertical safety", "requirements": ["R02"], "transition": "Transition into ecological explanation of cannibalism"},
            {"scene_id": "SC03", "purpose": "Deliver sharp editorial commentary on island cannibalism math", "requirements": ["R03"], "transition": "Pivoting to the vertical physics of claw climbing"},
            {"scene_id": "SC04", "purpose": "Explain the climbing biomechanics that defeat heavy adults", "requirements": ["R04"], "transition": "Escalate to the peak cliffhanger and channel spinoff"},
            {"scene_id": "SC05", "purpose": "Deliver cliffhanger peak on fecal armor and bridge to long video", "requirements": ["R05"], "transition": "End of short"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "TierZoo",
                    "top_performing_videos": [
                        {
                            "title": "Why Komodo Dragons Are S-Tier",
                            "views": "4.2M views",
                            "hook_technique": "Start with immediate high-lethality stat shock.",
                            "pacing_structure": "Hook -> Mechanic breakdown -> Survival twist.",
                            "retention_driver": "Rapid-fire visual delivery with zero filler."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Exposing the brutal fact that mothers actively eat their young.",
                        "Using gravity and climbing as the ultimate escape trick."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_words": 16,
                "zero_pause_opening_seconds": 10,
                "visual_contrast": "Newborn Komodo in hand-drawn codex vs Looming cannibal mother",
                "counter_intuitive_truth_slap": "The moment a baby Komodo dragon hatches, its number-one predator is its own mother."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Shocking cold open on maternal cannibalism."},
                {"phase": "empirical_conflict", "purpose": "The sprint across sand before scent gives away the nest."},
                {"phase": "structural_model", "purpose": "Editorial stance on island caloric scarcity."},
                {"phase": "actionable_resolution", "purpose": "Vertical climb exploiting adult weight limits."},
                {"phase": "cliffhanger_spinoff", "purpose": "Tease the bizarre chemical armor defense and bridge."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Vertical copperplate zoological plates on aged cotton rag paper."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Reptile & amphibian evolution",
            "myth_debunked": "Animal mothers protect their offspring.",
            "channel_verdict": "On Komodo Island, adult dragons eat ten percent of their own young.",
            "actionable_rule_of_thumb": "Climb vertically where heavy predators cannot follow."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "What grotesque chemical armor allows juvenile dragons to survive when trapped on the forest floor?",
            "bridge": "Watch the full five-year survival breakdown on Scale and Bone YouTube.",
            "close": "Follow our channel for more deep evolutionary survival stories.",
            "endcard_text": "FULL VIDEO ON YOUTUBE"
        }
    }

    scenes = [
        # SC01
        {
            "id": "SC01",
            "title": "The Cannibal Mother Shock",
            "purpose": "Shock cold viewers with maternal cannibalism hook",
            "action": "Newborn Komodo slices through egg while adult mother dragon waits outside as a predator",
            "setting": "Underground nest mound on volcanic sand beach",
            "camera": "Dramatic vertical split frame comparing egg interior with looming jaws above",
            "narration": "The moment a baby Komodo dragon slices through its leathery egg, its greatest mortal enemy is waiting right outside the nest: its own mother. Maternal affection does not exist in this volcanic forest.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Shocking, cold, urgent",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images": [
                make_sb_image(
                    "SC01_I1",
                    "Vertical 9:16 zoological copperplate plate on cotton rag paper #F2EAD7. Close-up of tiny Komodo hatchling head emerging from torn egg, white keratin egg-tooth visible in dip-pen ink #1C1917.",
                    "Hatchling head emerging from torn leathery egg",
                    "Establishing newborn vulnerability SC01_I1",
                    "burst", "hook_shock"
                ),
                make_sb_image(
                    "SC01_I2",
                    "Vertical split composition. Top half: giant adult dragon snout hovering over ground with yellow tongue flicking; bottom half: subterranean egg chamber with tiny coiled hatchling.",
                    "Split view of giant mother above and hatchling below",
                    "Visualizing immediate maternal threat SC01_I2",
                    "burst", "hook_shock"
                ),
                make_sb_image(
                    "SC01_I3",
                    "Macro copperplate engraving. Giant adult Komodo dragon eye with slit pupil dilating as it smells hatching fluids, olive-scale green #4A6B53 and venom ochre #C86D51.",
                    "Macro view of adult dragon predatory eye",
                    "Showing adult predator sensory lock SC01_I3",
                    "fast", "hook_shock"
                ),
                make_sb_image(
                    "SC01_I4",
                    "Dramatic field sketch. Adult dragon jaws snapping open directly over nesting hole, sharp serrated teeth outlined in dark iron-gall cross-hatching #1C1917.",
                    "Adult jaws opening over nesting hole",
                    "Hook climax: jaws ready to snap SC01_I4",
                    "fast", "hook_shock"
                ),
            ],
            "beats": [
                make_sb_beat("SC01_B1", "SC01_I1", "Hook opening statement", "The moment a baby Komodo dragon slices through its leathery egg,", "burst", "hook_shock"),
                make_sb_beat("SC01_B2", "SC01_I2", "Reveal mother as predator", "its greatest mortal enemy is waiting right outside the nest:", "burst", "hook_shock"),
                make_sb_beat("SC01_B3", "SC01_I3", "Deliver shock slap", "its own mother.", "fast", "hook_shock"),
                make_sb_beat("SC01_B4", "SC01_I4", "State absence of affection", "Maternal affection does not exist in this volcanic forest.", "fast", "hook_shock"),
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "The Explosive Sand Sprint",
            "purpose": "Show the desperate breakout and sprint across open volcanic sand",
            "action": "Newborn Komodo explodes from sand and dashes frantically across volcanic gravel",
            "setting": "Volcanic sand mound under tropical sun",
            "camera": "Low-angle fast tracking shot following miniature lizard feet sprinting",
            "narration": "Digging through two feet of suffocating volcanic sand, the hatchling bursts into blinding sunlight. It cannot hesitate for one single second. The smell of birth fluids alerts every hungry adult within hundreds of meters.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Frantic, breathless, physical",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "story_action",
            "images": [
                make_sb_image(
                    "SC02_I1",
                    "Vertical 9:16 zoological plate on #F2EAD7 paper. Sand explodes upward as tiny lizard snout breaks through surface crust, black granules scattering in fine dip-pen cross-hatching.",
                    "Sand explodes as hatchling breaches surface",
                    "Depicting explosive surface breach SC02_I1",
                    "fast", "story_action"
                ),
                make_sb_image(
                    "SC02_I2",
                    "Low-angle dynamic engraving. Tiny Komodo hatchling sprinting at full speed across volcanic gravel, legs moving in rapid blur, olive-scale wash #4A6B53.",
                    "Tiny hatchling sprinting across black gravel",
                    "Showing desperate ground sprint SC02_I2",
                    "fast", "story_action"
                ),
                make_sb_image(
                    "SC02_I3",
                    "Panoramic vertical view. An eighty-kilogram adult Komodo dragon charging across savanna scrub toward the fleeing hatchling in dense iron-gall linework #1C1917.",
                    "Massive adult dragon charging across savanna",
                    "Adult pursuing across open ground SC02_I3",
                    "fast", "story_action"
                ),
                make_sb_image(
                    "SC02_I4",
                    "Field sketch plate. Scent plume billowing from nest mound as multiple adult silhouettes converge in background, bone ivory #D9C5A0 and slate #2E4361.",
                    "Multiple adult dragon silhouettes converging on scent",
                    "Revealing multi-predator threat SC02_I4",
                    "normal", "story_action"
                ),
            ],
            "beats": [
                make_sb_beat("SC02_B1", "SC02_I1", "Describe sand breakout", "Digging through two feet of suffocating volcanic sand,", "fast", "story_action"),
                make_sb_beat("SC02_B2", "SC02_I2", "Show daylight emergence", "the hatchling bursts into blinding sunlight. It cannot hesitate for one single second.", "fast", "story_action"),
                make_sb_beat("SC02_B3", "SC02_I3", "Explain scent spread", "The smell of birth fluids alerts every hungry adult", "fast", "story_action"),
                make_sb_beat("SC02_B4", "SC02_I4", "State perimeter danger", "within hundreds of meters.", "normal", "story_action"),
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "Island Cannibalism Math",
            "purpose": "Deliver sharp editorial commentary on why island dragons eat their young",
            "action": "Naturalist diagram explaining island resource scarcity and ten percent cannibal diet",
            "setting": "Naturalist codex calculation board on aged cotton paper",
            "camera": "Graphic diagram with calipers highlighting statistical numbers",
            "narration": "On an isolated island with severe protein scarcity, cannibalism is cold arithmetic. Young dragons constitute ten percent of an adult's annual calories. In this ecosystem, sentimentality dies; raw calories determine who survives.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Analytical, unsentimental, stark",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images": [
                make_sb_image(
                    "SC03_I1",
                    "Vertical 9:16 naturalist codex plate on #F2EAD7. Food pyramid diagram of Komodo Island with bold hand-drawn numbers showing 10% cannibalism rate in iron-gall ink #1C1917.",
                    "Food pyramid diagram showing 10% cannibalism rate",
                    "Editorial analysis of caloric necessity SC03_I1",
                    "slow", "editorial_commentary"
                ),
                make_sb_image(
                    "SC03_I2",
                    "Engraved anatomical study. Adult Komodo jaw holding juvenile lizard silhouette, crossed out with balance scale comparing dry season famine, venom ochre #C86D51.",
                    "Balance scale comparing famine vs cannibal calories",
                    "Illustrating stark island famine math SC03_I2",
                    "slow", "editorial_commentary"
                ),
                make_sb_image(
                    "SC03_I3",
                    "Naturalist field sketch. Pith-helmet stickman points with brass calipers toward dry cracked earth, shaking head at the brutal island reality.",
                    "Stickman pointing to dry cracked island earth",
                    "Channel verdict on harsh natural laws SC03_I3",
                    "slow", "editorial_commentary"
                ),
                make_sb_image(
                    "SC03_I4",
                    "Zoological codex plate. Large adult dragon swallowing prey on barren ridge beneath blazing tropical sun, dark ink cross-hatching #1C1917.",
                    "Adult dragon swallowing food on barren ridge",
                    "Stark reality of calorie dominance SC03_I4",
                    "slow", "editorial_commentary"
                ),
            ],
            "beats": [
                make_sb_beat("SC03_B1", "SC03_I1", "State cold island arithmetic", "On an isolated island with severe protein scarcity, cannibalism is cold arithmetic.", "slow", "editorial_commentary"),
                make_sb_beat("SC03_B2", "SC03_I2", "Cite ten percent calories", "Young dragons constitute ten percent of an adult's annual calories.", "slow", "editorial_commentary"),
                make_sb_beat("SC03_B3", "SC03_I3", "Note death of sentimentality", "In this ecosystem, sentimentality dies;", "slow", "editorial_commentary"),
                make_sb_beat("SC03_B4", "SC03_I4", "Conclude on raw calories", "raw calories determine who survives.", "slow", "editorial_commentary"),
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "Climbing Against Gravity",
            "purpose": "Explain the climbing biomechanics that defeat heavy adults",
            "action": "Newborn Komodo uses sharp claws to sprint vertically up a palm trunk while adult slips",
            "setting": "Tall lontar palm trunk rising from volcanic gravel",
            "camera": "Upward tracking shot moving rapidly with the climbing hatchling",
            "narration": "The baby's only salvation is vertical. Weighing under one hundred grams, its needle claws lock into palm bark, carrying it skyward in seconds. Massive eighty-kilogram adults cannot follow; gravity pulls their heavy bodies back down.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Fast-paced, triumphant, biomechanical",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "mechanism_step",
            "images": [
                make_sb_image(
                    "SC04_I1",
                    "Vertical 9:16 zoological plate on #F2EAD7. Tiny hatchling hits palm trunk and scrambles vertically upward in a blur, needle claws hooking deep into fibrous bark.",
                    "Hatchling hitting palm trunk and sprinting up",
                    "Visualizing vertical acceleration SC04_I1",
                    "fast", "mechanism_step"
                ),
                make_sb_image(
                    "SC04_I2",
                    "Macro copperplate detail. Tiny curved claw tips embedding firmly into tree bark ridges, bone ivory lines #D9C5A0 and olive wash #4A6B53.",
                    "Extreme macro of juvenile claws locked in bark",
                    "Showing physical grip mechanism SC04_I2",
                    "fast", "mechanism_step"
                ),
                make_sb_image(
                    "SC04_I3",
                    "Low-angle dynamic plate. Adult dragon rears up against trunk, heavy claws tearing bark away as it slides backward onto gravel with heavy thud.",
                    "Massive adult sliding down trunk in frustration",
                    "Demonstrating adult gravitational failure SC04_I3",
                    "normal", "mechanism_step"
                ),
                make_sb_image(
                    "SC04_I4",
                    "Vertical composition on cotton rag. Tiny hatchling perched securely five meters up in palm fronds, looking safely down at ground predator below.",
                    "Hatchling resting safely five meters high in fronds",
                    "Reaching vertical sanctuary SC04_I4",
                    "normal", "mechanism_step"
                ),
            ],
            "beats": [
                make_sb_beat("SC04_B1", "SC04_I1", "State vertical salvation", "The baby's only salvation is vertical.", "fast", "mechanism_step"),
                make_sb_beat("SC04_B2", "SC04_I2", "Detail needle claw sprint", "Weighing under one hundred grams, its needle claws lock into palm bark, carrying it skyward in seconds.", "fast", "mechanism_step"),
                make_sb_beat("SC04_B3", "SC04_I3", "Contrast eighty-kilogram adults", "Massive eighty-kilogram adults cannot follow;", "normal", "mechanism_step"),
                make_sb_beat("SC04_B4", "SC04_I4", "State gravitational victory", "gravity pulls their heavy bodies back down.", "normal", "mechanism_step"),
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Fecal Armor Twist & Spin-off",
            "purpose": "Deliver cliffhanger peak on fecal armor trick, bridge to full documentary, and closing CTA",
            "action": "Juvenile rolls in dung when grounded; stickman introduces the full 5-year documentary",
            "setting": "Forest floor clearing shifting to official Scale & Bone vertical endcard",
            "camera": "Macro shot of smeared scales transitioning to channel endcard",
            "narration": "What grotesque chemical armor allows juvenile dragons to survive when trapped on the forest floor? Watch the full five-year survival breakdown on Scale and Bone YouTube. Follow our channel for more deep evolutionary survival stories.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01", "SRC02"],
            "tone": "Suspenseful, intriguing, inviting",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cliffhanger_peak",
            "images": [
                make_sb_image(
                    "SC05_I1",
                    "Vertical 9:16 zoological plate on #F2EAD7. Juvenile dragon on ground rolling vigorously in adult fecal matter and rotting entrails, scales dark with putrid disguise.",
                    "Juvenile rolling in fecal matter on ground",
                    "Visualizing cliffhanger peak mystery SC05_I1",
                    "fast", "cliffhanger_peak"
                ),
                make_sb_image(
                    "SC05_I2",
                    "Macro engraving of adult dragon snout sniffing smeared juvenile, eyes baffled as chemical disguise bluffs Jacobson organ, ink cross-hatching #1C1917.",
                    "Adult dragon sniffing dung-coated juvenile",
                    "Demonstrating chemical sensory bluff SC05_I2",
                    "normal", "cliffhanger_peak"
                ),
                make_sb_image(
                    "SC05_I3",
                    "Field naturalist plate on cotton rag. Pith-helmet stickman points with brass pointer toward a full five-year chronological timeline banner on aged vellum.",
                    "Stickman presenting the full five-year timeline",
                    "Bridging to full YouTube documentary SC05_I3",
                    "normal", "cta_bridge"
                ),
                make_sb_image(
                    "SC05_I4",
                    "Vertical 9:16 channel endcard on aged cotton rag paper #F2EAD7. Elegant dip-pen reptile skeleton engraving framing uppercase hand-lettered text: 'SCALE & BONE'. Zero 3D, zero gradients.",
                    "Official Scale & Bone vertical channel endcard",
                    "Holding vertical channel endcard SC05_I4",
                    "hold", "cta_close",
                    is_endcard=True, shot_type="white_card"
                ),
            ],
            "beats": [
                make_sb_beat("SC05_B1", "SC05_I1", "Deliver cliffhanger peak question", "What grotesque chemical armor allows juvenile dragons to survive when trapped on the forest floor?", "fast", "cliffhanger_peak"),
                make_sb_beat("SC05_B2", "SC05_I2", "Reinforce visual mystery", "What grotesque chemical armor allows juvenile dragons to survive when trapped on the forest floor?", "normal", "cliffhanger_peak"),
                make_sb_beat("SC05_B3", "SC05_I3", "Deliver bridge to long video", "Watch the full five-year survival breakdown on Scale and Bone YouTube.", "normal", "cta_bridge"),
                make_sb_beat("SC05_B4", "SC05_I4", "Deliver closing CTA on endcard", "Follow our channel for more deep evolutionary survival stories.", "hold", "cta_close", is_endcard=True),
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
                "scene_id": "SC03",
                "quote": "Young dragons constitute ten percent of an adult's annual calories.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Young Komodo dragons constitute up to 10% of the total diet of adult Komodos in resource-constrained island ecosystems."
            }
        ],
        "revision_response": [],
        "open_questions": []
    }

    return brief, outline, competitor_research, content
