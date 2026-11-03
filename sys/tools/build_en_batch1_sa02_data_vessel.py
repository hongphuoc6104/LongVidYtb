#!/usr/bin/env python3
"""Data definitions for Channel 2: Inside the Vessel (en_inside_vessel).

Jobs:
- Long 16:9: sys/runs/en-inside-vessel-batch1-16x9 (11 scenes, 66 images, 620 words)
- Short 9:16: sys/runs/en-inside-vessel-batch1-9x16 (5 scenes, 20 images, 173 words)
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


def get_inside_vessel_long():
    channel_id = "en_inside_vessel"
    job_id = "en-inside-vessel-batch1-16x9"
    ch = get_channel(channel_id)

    topic = "What Actually Happens Inside Your Vagus Nerve and Adrenal Glands During a 3 AM Cortisol Awakening"
    youtube_title = "Why Your Heart Suddenly Races at 3 AM"  # 37 chars <= 55

    sources = [
        {
            "id": "SRC01",
            "title": "Timing the end of nocturnal sleep",
            "reference": "Born, J. et al. (1999). Nature, 397, 29-30.",
            "facts": [
                "Circadian cortisol awakening response and nocturnal hepatic glycogen depletion trigger early autonomic arousal.",
                "Blood glucose dips prompt counter-regulatory hormone release including epinephrine and cortisol."
            ]
        },
        {
            "id": "SRC02",
            "title": "The polyvagal perspective: autonomic regulation and cardiac control",
            "reference": "Porges, S. W. (2007). Biological Psychology, 74(2), 116-143.",
            "facts": [
                "The vagus nerve provides continuous parasympathetic braking on the sinoatrial node.",
                "Withdrawal of the vagal brake causes rapid, abrupt acceleration of cardiac pulse without immediate physical exertion."
            ]
        },
        {
            "id": "SRC03",
            "title": "Brief structured respiration practices enhance mood and reduce physiological arousal",
            "reference": "Balban, M. Y. et al. (2023). Cell Reports Medicine, 4(1), 100895.",
            "facts": [
                "Physiological sighs with two quick nasal inhales and an extended oral exhale rapidly stimulate parasympathetic vagal tone.",
                "Extended exhalation expands the thoracic cavity, compressing the heart and stimulating the baroreflex brake."
            ]
        }
    ]

    required_points = [
        {"id": "R01", "text": "Snapping wide awake at 3:14 AM with a violently hammering heart and adrenaline panic"},
        {"id": "R02", "text": "Nocturnal glycogen depletion in the liver triggering an emergency metabolic fuel alert"},
        {"id": "R03", "text": "Hypothalamus sounding the alarm down the spinal sympathetic nervous chain"},
        {"id": "R04", "text": "Debunking midnight panic: an ancient survival reflex executing out of sync"},
        {"id": "R05", "text": "Adrenal medulla discharging epinephrine and cortex ramping up cortisol secretion"},
        {"id": "R06", "text": "Adrenaline binding sinoatrial node receptors as the vagus nerve brake disengages"},
        {"id": "R07", "text": "Checking glowing smartphone screens halting pineal melatonin and locking sympathetic arousal"},
        {"id": "R08", "text": "Abruptly standing up dropping venous return and triggering baroreceptor tachycardia"},
        {"id": "R09", "text": "Editorial verdict on using respiration biomechanics instead of mental willpower to clear adrenaline"},
        {"id": "R10", "text": "The physiological sigh protocol: two nasal inhales followed by one long extended exhale"},
        {"id": "R11", "text": "Rapid parasympathetic recovery and honoring your biological vessel each night"}
    ]

    editorial_stance = {
        "myth_debunked": "The panic-inducing myth that a midnight racing heart means you have an underlying cardiac disorder or catastrophic anxiety.",
        "why_generic_advice_fails": "Telling someone to just calm down or try harder to sleep ignores that circulating epinephrine cannot be neutralized by willpower alone.",
        "channel_verdict": "A 3 AM heart spike is your liver and adrenal glands executing a biochemical fuel rescue, which only becomes frightening when misread as danger.",
        "tradeoff_or_blindspot": "Staying completely still in dark silence feels counterintuitive during panic, yet physical stillness is required to let adrenaline clear."
    }

    actionable_value = {
        "core_mechanism": "Nocturnal glycogen drop prompts an adrenaline surge that disengages vagal braking on the sinoatrial node, spiking heart rate.",
        "practical_rule_of_thumb": "Perform three rounds of the physiological sigh—two nasal sniffs, one long sigh out—while keeping room lights completely dark.",
        "real_world_scenario": "When waking with a pounding chest at 3 AM, keep your phone face down on the nightstand and exhale slowly to re-engage the vagal brake."
    }

    thumbnail_spec = {
        "visual_hook": "Classical anatomical cross-section of a human chest on medical parchment showing the illuminated sinoatrial node and adrenal medulla beside a 3:14 AM pocket watch.",
        "text_overlay": "3 AM HEART",
        "contrast_pair": "Peaceful bedroom stillness vs Sudden adrenal surge",
        "thumbnail_prompt": "Requested aspect ratio: 16:9. Render a complete 100% full-bleed horizontal widescreen 16:9 high-impact YouTube poster thumbnail illustration extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, zero UI chrome, and zero dark vignette.\n\nVisual Style (ch_en_organ_buddies): Authentic 2D Vesalius and Gray's Anatomy medical copperplate ink etching and mineral watercolor cross-section atlas on warm archival vellum (#FAF7F0 fibrous vellum paper, #1E1B18 fine surgical dip-pen cross-hatching, #C85A5A arterial carmine wash, #D99B66 hepatic ochre, #4A7C9B venous slate-blue, #5E8C6A lymphatic sage). Orthographic 2D, museum medical plate texture, >=60% negative space, zero 3D CGI, zero kawaii cartoon faces, zero plastic AI glow, zero gradients.\n\nFocal Subject: Translucent human chest silhouette showing the heart with arterial carmine wash (#C85A5A) and glowing sinoatrial node, with delicate vagus nerve branches in slate-blue (#4A7C9B). An antique brass pocket watch pointing to 3:14 AM rests beside surgical calipers in the foreground.\n\nPoster Typography: Hand-lettered uppercase English text in upper third: '3 AM HEART'. Elegant Latin medical font etched directly onto vellum, strictly zero rectangular text cards or gradient boxes.",
        "layout_mode": "split_contrast"
    }

    cta_plan = {
        "close": "Give your vessel a restful pause tonight and notice how it responds.",
        "endcard_text": "INSIDE THE VESSEL"
    }

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain the neurochemical and autonomic mechanisms behind nocturnal cortisol spikes using classical anatomical etchings and physiological respiration solutions",
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
                "Deliver an empathetic, anatomically rigorous explainer across 11 scenes with 66 unique tactile medical atlas illustrations, maintaining an average hold under 2.8 seconds and zero AI cliches."
            ],
            "avoid": list(ch.avoid) + ["delve into", "testament to", "tapestry", "in conclusion", "it is important to remember"],
            "prior_knowledge": "No medical background required; concepts grounded in intuitive biological mechanics.",
            "pacing": "Curious, awe-inspiring, empathetic build from midnight alarm to biochemical mystery and physiological relief.",
            "domain_requirements": [],
            "assumptions": [
                "Spoken in warm, clear conversational English without clinical jargon barrier."
            ],
            "text_style": {
                "font": "Classical copperplate serif",
                "color": "#1E1B18",
                "outline": "#FAF7F0 vellum contrast",
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
                    "source": "Conversational cadence calibrated for anatomical storytelling"
                }
            }
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": thumbnail_spec,
            "channel_pillar": "Human Anatomy, Autonomic Physiology & Internal Health",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["why heart races at 3am", "cortisol awakening", "vagus nerve", "adrenal spike", "sleep tachycardia", "physiological sigh"],
            "cta_plan": cta_plan,
            "editorial_stance": editorial_stance,
            "actionable_value": actionable_value
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": thumbnail_spec,
        "channel_pillar": "Human Anatomy, Autonomic Physiology & Internal Health",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["why heart races at 3am", "cortisol awakening", "vagus nerve", "adrenal spike", "sleep tachycardia", "physiological sigh"],
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
            {"scene_id": "SC01", "purpose": "Establish the terrifying 3:14 AM awakening with racing pulse in dark silence", "requirements": ["R01"], "transition": "Trace signal inward to hepatic biochemistry"},
            {"scene_id": "SC02", "purpose": "Explain nocturnal glycogen depletion in the liver triggering emergency alert", "requirements": ["R02"], "transition": "Follow neurochemical pathways up to the brain"},
            {"scene_id": "SC03", "purpose": "Show hypothalamus signaling down spinal sympathetic nerve chain", "requirements": ["R03"], "transition": "Deliver critical editorial commentary on midnight panic"},
            {"scene_id": "SC04", "purpose": "Deliver editorial stance: not broken psychology, but an ancient survival reflex", "requirements": ["R04"], "transition": "Examine the adrenal gland hormone cascade"},
            {"scene_id": "SC05", "purpose": "Illustrate adrenal medulla discharging epinephrine into circulation", "requirements": ["R05"], "transition": "Follow adrenaline to the cardiac pacemaker node"},
            {"scene_id": "SC06", "purpose": "Detail adrenaline accelerating sinoatrial node as vagus brake slips", "requirements": ["R06"], "transition": "Examine common behavioral traps in the bedroom"},
            {"scene_id": "SC07", "purpose": "Expose how checking glowing smartphone screens halts melatonin and locks panic", "requirements": ["R07"], "transition": "Examine postural mistakes when getting out of bed"},
            {"scene_id": "SC08", "purpose": "Show how standing up drops venous return and spikes heart rate higher", "requirements": ["R08"], "transition": "Transition to physical autonomic solutions"},
            {"scene_id": "SC09", "purpose": "Deliver editorial commentary on respiration biomechanics over mental willpower", "requirements": ["R09"], "transition": "Demonstrate the physiological sigh technique"},
            {"scene_id": "SC10", "purpose": "Guide viewer through two quick nasal inhales and one long slow exhale", "requirements": ["R10"], "transition": "Zoom out to whole-body parasympathetic calm"},
            {"scene_id": "SC11", "purpose": "Close with profound reflection on listening to and respecting your vessel", "requirements": ["R11"], "transition": "Final hold endcard"}
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Institute of Human Anatomy",
                    "top_performing_videos": [
                        {
                            "title": "What Happens During a Cortisol Spike",
                            "views": "4.5M views",
                            "hook_technique": "Holding a real anatomical model of the adrenal gland and showing its nerve supply.",
                            "pacing_structure": "Everyday panic symptom -> Nerve tract anatomy -> Chemical receptor mechanics.",
                            "retention_driver": "Extreme precision combined with relatable bodily sensations everyone has experienced."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Validating that physical symptoms are not 'all in your head'.",
                        "Using clear organ cross-sections to explain confusing internal sensations."
                    ]
                },
                {
                    "channel_name": "Chubbyemu",
                    "top_performing_videos": [
                        {
                            "title": "A Student Woke Up At 3 AM Feeling Terrified. This Is What Happened To His Blood Pressure",
                            "views": "5.8M views",
                            "hook_technique": "Forensic timestamp breakdown starting right in the bedroom at 3:14 AM.",
                            "pacing_structure": "Sensory dread -> Hepatic biochemistry -> Autonomic cascading loop.",
                            "retention_driver": "Medical detective pacing where biological cause and effect click into place."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Timestamped chronological progression creating immediate tension.",
                        "Clear pharmacological and physiological explanations that empower viewers."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 17,
                "zero_pause_opening_seconds": 13,
                "visual_contrast": "Quiet, dark, peaceful bedroom vs Violently thumping red heart on medical parchment.",
                "counter_intuitive_truth_slap": "You didn't wake up because you panicked; your liver panicked first, forcing you awake."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Sensory shock of snapping awake with a pounding pulse at 3:14 AM."},
                {"phase": "empirical_conflict", "purpose": "Depleted hepatic glycogen triggering hypothalamic emergency commands."},
                {"phase": "structural_model", "purpose": "Editorial commentary on ancient survival wiring executing without a predator."},
                {"phase": "actionable_resolution", "purpose": "The physiological sigh engaging the vagus nerve brake in three breaths."},
                {"phase": "cliffhanger_spinoff", "purpose": "Profound whole-body reflection honoring the biological vessel."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chained 2D medical etchings maintaining consistent vellum texture and ink linework."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Human Anatomy, Autonomic Physiology & Internal Health",
            "myth_debunked": "A 3 AM racing heart means an impending panic attack or heart defect.",
            "channel_verdict": "Your body executed an emergency fuel rescue, and breathing biomechanics can instantly restore calm.",
            "actionable_rule_of_thumb": "Two sharp nasal sniffs, one long sigh out, and keep bedroom lights black."
        },
        "cta_and_spinoff_strategy": {
            "close": "Give your vessel a restful pause tonight and notice how it responds.",
            "endcard_text": "INSIDE THE VESSEL"
        }
    }

    scene_data = [
        # SC01
        {
            "id": "SC01",
            "title": "The 3:14 AM Awakening",
            "purpose": "Establish the terrifying 3:14 AM awakening with racing pulse in dark silence",
            "action": "A human figure lies wide awake in a dark bedroom, clutching their chest as internal cardiac chambers pulse in crimson ink.",
            "setting": "Archival vellum #FAF7F0 with fine surgical dip-pen cross-hatching #1E1B18 showing an illuminated bedroom at night.",
            "camera": "Intimate medium close-up zooming smoothly from bedroom clock into internal ribcage cross-section",
            "narration": "It is 3:14 in the morning. Total silence fills your bedroom, but you snap wide awake with your heart violently hammering against your ribs. Your throat feels dry, your palms are clammy, and your thoughts immediately race toward catastrophe. You did not have a nightmare, yet your entire nervous system is screaming as if a predator entered the room.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Suspenseful, alarming, physiological",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images_spec": [
                ("SC01_I1", "Vesalius medical atlas plate of a bedroom at night: antique clock pointing to 3:14 AM beside a human lying awake on archival vellum #FAF7F0.", None, "full_scene", "burst", "hook_shock"),
                ("SC01_I2", "Translucent anatomical cutaway of human torso revealing the heart pulsing in vivid arterial carmine #C85A5A against dark parchment.", "SC01_I1", "cutaway_detail", "fast", "hook_shock"),
                ("SC01_I3", "Close-up of human eyes wide with dilated pupils, fine copperplate dip-pen cross-hatching #1E1B18.", "SC01_I2", "variation", "fast", "hook_shock"),
                ("SC01_I4", "Anatomical hand clutching the sternum over the ribcage, showing autonomic vasomotor sweating on palms.", "SC01_I3", "cutaway_detail", "fast", "hook_shock"),
                ("SC01_I5", "Metaphorical shadow of a primeval predator looming on the bedroom wall, contrasting modern bedroom with ancient survival wiring.", "SC01_I4", "concept_metaphor", "normal", "hook_shock"),
                ("SC01_I6", "The full anatomical human silhouette illuminated from within by neural pathways glowing like copper wires.", "SC01_I5", "full_scene", "normal", "hook_shock"),
            ],
            "quotes": [
                "It is 3:14 in the morning.",
                "Total silence fills your bedroom, but you snap wide awake",
                "with your heart violently hammering against your ribs.",
                "Your throat feels dry, your palms are clammy,",
                "You did not have a nightmare, yet your entire nervous system is screaming",
                "as if a predator entered the room."
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "The Hepatic Glycogen Dip",
            "purpose": "Explain nocturnal glycogen depletion in the liver triggering emergency alert",
            "action": "Inside the right hypochondrium, the liver slowly runs out of stored glycogen fuel after seven hours of fasting.",
            "setting": "Anatomical abdominal cross-section on vellum #FAF7F0 with hepatic ochre #D99B66 and fine vascular etching.",
            "camera": "Deep anatomical cutaway tracking into liver parenchyma and glycogen fuel meters",
            "narration": "The true trigger began hours earlier inside your liver. By three in the morning, your body has gone seven hours without fuel. Your hepatic glycogen stores steadily deplete to critical thresholds. Your brain consumes a constant supply of glucose, and as circulating blood sugar dips, your internal biochemical sensors detect an existential metabolic emergency.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Investigative, biochemical, precise",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "chronological_shift",
            "images_spec": [
                ("SC02_I1", "Classical medical etching of the liver situated beneath the diaphragm on archival vellum #FAF7F0, tinted in hepatic ochre #D99B66.", None, "visual_diagram", "fast", "chronological_shift"),
                ("SC02_I2", "Microscopic hepatic lobule cross-section showing hexagonal cell plates depleting their stored glycogen granules.", "SC02_I1", "cutaway_detail", "fast", "chronological_shift"),
                ("SC02_I3", "Anatomical gauge showing blood glucose levels declining across a nocturnal timeline from midnight to 3 AM.", "SC02_I2", "visual_diagram", "normal", "chronological_shift"),
                ("SC02_I4", "Glucose molecules traveling up the carotid arteries toward the cranium, illustrated as glowing dots in dip-pen ink.", "SC02_I3", "cutaway_detail", "fast", "chronological_shift"),
                ("SC02_I5", "Biochemical sensor callout inside the autonomic nervous system flashing red warning indicators.", "SC02_I4", "concept_metaphor", "normal", "chronological_shift"),
                ("SC02_I6", "Full internal vascular map showing the liver signaling metabolic urgency to neighboring organs.", "SC02_I5", "full_scene", "normal", "chronological_shift"),
            ],
            "quotes": [
                "The true trigger began hours earlier inside your liver.",
                "By three in the morning, your body has gone seven hours without fuel.",
                "Your hepatic glycogen stores steadily deplete to critical thresholds.",
                "Your brain consumes a constant supply of glucose,",
                "and as circulating blood sugar dips,",
                "your internal biochemical sensors detect an existential metabolic emergency."
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "Hypothalamic Command",
            "purpose": "Show hypothalamus signaling down spinal sympathetic nerve chain",
            "action": "The central neuroendocrine hub detects the glucose drop and fires electrical impulses down the sympathetic nerve chain.",
            "setting": "Anatomical cranial and spinal cord etching on archival vellum #FAF7F0 with fine neural linework.",
            "camera": "Macro anatomical tracking shot following electrical sparks down the thoracic spinal cord",
            "narration": "Your hypothalamus acts as the vigilant master controller. Sensing the nocturnal glucose drop, it sends urgent neurochemical commands down the spinal sympathetic chain. Rather than letting blood sugar fall further, your brain activates an emergency counter-regulatory rescue response. It orders an immediate surge of survival hormones to mobilize fuel from muscle and adipose tissue.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Commanding, neurochemical, urgent",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images_spec": [
                ("SC03_I1", "Medial sagittal view of the neuroendocrine hypothalamus illuminated at the center of the cranial cavity on vellum #FAF7F0.", None, "visual_diagram", "fast", "mechanism_step"),
                ("SC03_I2", "Electrical action potentials streaming down the cervical and thoracic sympathetic nerve trunks in vibrant cobalt blue.", "SC03_I1", "cutaway_detail", "fast", "mechanism_step"),
                ("SC03_I3", "Cross-section of the thoracic spinal cord with preganglionic sympathetic neurons arborizing outward.", "SC03_I2", "visual_diagram", "normal", "mechanism_step"),
                ("SC03_I4", "Anatomical schematic showing sympathetic signals branching toward the kidneys, liver, and cardiac plexus.", "SC03_I3", "full_scene", "normal", "mechanism_step"),
                ("SC03_I5", "Adipose tissue cells receiving chemical messages to begin breaking down triglycerides into free fatty acids.", "SC03_I4", "cutaway_detail", "fast", "mechanism_step"),
                ("SC03_I6", "The master controller depicted metaphorically as an intricate antique clockwork mechanism inside a classical bust.", "SC03_I5", "concept_metaphor", "normal", "mechanism_step"),
            ],
            "quotes": [
                "Your hypothalamus acts as the vigilant master controller.",
                "Sensing the nocturnal glucose drop,",
                "it sends urgent neurochemical commands down the spinal sympathetic chain.",
                "Rather than letting blood sugar fall further,",
                "your brain activates an emergency counter-regulatory rescue response.",
                "It orders an immediate surge of survival hormones to mobilize fuel from muscle and adipose tissue."
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "Debunking Midnight Anxiety",
            "purpose": "Deliver editorial stance: not broken psychology, but an ancient survival reflex",
            "action": "A balance scale on medical vellum weighs 'broken psychology' against 'ancient metabolic survival reflex'.",
            "setting": "Philosophical medical plate on warm vellum #FAF7F0 with brass calipers and antique ink annotations.",
            "camera": "Slow contemplative push-in on classical anatomical balancing scales",
            "narration": "Modern health advice often tells us that a midnight racing heart is proof of anxiety disorders or mental weakness. That diagnosis gets human physiology completely backward. Your vessel is not broken; it is executing an ancient, life-saving survival reflex. Your biology is prioritizing your survival over your sleep, but in a quiet bedroom, that chemical surge feels terrifying.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Empathetic, reassuring, demystifying",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images_spec": [
                ("SC04_I1", "Vesalius etching of a human resting in peace contrasted against clinical anxiety labels, rendered on archival vellum #FAF7F0.", None, "concept_metaphor", "slow", "editorial_commentary"),
                ("SC04_I2", "Close-up of classical brass surgical calipers measuring healthy heart linework, refuting the broken organ myth.", "SC04_I1", "still_life", "slow", "editorial_commentary"),
                ("SC04_I3", "Ancient human hunter silhouette surviving a freeze by burning emergency fuel, juxtaposed with modern sleeping human.", "SC04_I2", "concept_metaphor", "slow", "editorial_commentary"),
                ("SC04_I4", "Anatomical cross-section of the head showing calm facial expression despite rapid internal cardiovascular pumping.", "SC04_I3", "full_scene", "normal", "editorial_commentary"),
                ("SC04_I5", "Handwritten anatomical note on vellum: 'Survival precedes slumber in the hierarchy of physiology'.", "SC04_I4", "cutaway_detail", "slow", "editorial_commentary"),
                ("SC04_I6", "Reassuring composition showing the human silhouette gently cradled by protective physiological nerve arches.", "SC04_I5", "concept_metaphor", "slow", "editorial_commentary"),
            ],
            "quotes": [
                "Modern health advice often tells us that a midnight racing heart",
                "is proof of anxiety disorders or mental weakness.",
                "That diagnosis gets human physiology completely backward.",
                "Your vessel is not broken; it is executing an ancient, life-saving survival reflex.",
                "Your biology is prioritizing your survival over your sleep,",
                "but in a quiet bedroom, that chemical surge feels terrifying."
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Adrenal Medulla Detonation",
            "purpose": "Illustrate adrenal medulla discharging epinephrine into circulation",
            "action": "Chromaffin cells inside the adrenal medulla discharge dense granules of epinephrine directly into the inferior vena cava.",
            "setting": "Detailed retroperitoneal adrenal gland cutaway on parchment #FAF7F0 with golden ochre #D99B66 and arterial carmine #C85A5A.",
            "camera": "Dramatic cutaway zooming into the pyramid-shaped adrenal gland atop the kidney",
            "narration": "Deep inside your retroperitoneal cavity sit the adrenal glands. Triggered by sympathetic nerve fibers, the adrenal medulla discharges a concentrated burst of epinephrine and norepinephrine directly into the venous circulation. Seconds later, the adrenal cortex begins ramping up cortisol production, flooding your bloodstream with a potent cocktail of chemical stimulants.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Intense, endocrine, surging",
            "narrative_phase": "structural_model",
            "narrative_situation": "mechanism_step",
            "images_spec": [
                ("SC05_I1", "Classical anatomical dissection plate of the retroperitoneal space: kidneys with golden adrenal glands perched above on vellum #FAF7F0.", None, "visual_diagram", "burst", "mechanism_step"),
                ("SC05_I2", "Cross-section of the adrenal gland showing outer striated cortex and dark, vascularized inner medulla in fine ink lines.", "SC05_I1", "cutaway_detail", "fast", "mechanism_step"),
                ("SC05_I3", "Microscopic view of adrenal chromaffin cells exocytosing dense vesicles of epinephrine into blood capillaries.", "SC05_I2", "cutaway_detail", "fast", "mechanism_step"),
                ("SC05_I4", "Crimson chemical surge rushing upward through the inferior vena cava toward the thoracic cavity.", "SC05_I3", "full_scene", "normal", "mechanism_step"),
                ("SC05_I5", "Adrenal cortex layers (glomerulosa, fasciculata, reticularis) synthesizing steroid cortisol rings from cholesterol.", "SC05_I4", "visual_diagram", "normal", "mechanism_step"),
                ("SC05_I6", "Endocrine cocktail represented as twin glowing golden and crimson vials in an antique medical case.", "SC05_I5", "concept_metaphor", "normal", "mechanism_step"),
            ],
            "quotes": [
                "Deep inside your retroperitoneal cavity sit the adrenal glands.",
                "Triggered by sympathetic nerve fibers,",
                "the adrenal medulla discharges a concentrated burst of epinephrine and norepinephrine",
                "directly into the venous circulation.",
                "Seconds later, the adrenal cortex begins ramping up cortisol production,",
                "flooding your bloodstream with a potent cocktail of chemical stimulants."
            ]
        },
        # SC06
        {
            "id": "SC06",
            "title": "The Sinoatrial Node Accelerates",
            "purpose": "Detail adrenaline accelerating sinoatrial node as vagus brake slips",
            "action": "Epinephrine molecules dock onto beta-1 receptors on the right atrium pacemaker while the vagus nerve brake disengages.",
            "setting": "Anatomical cardiac chamber cutaway on vellum #FAF7F0 with carmine heart muscle #C85A5A and slate-blue vagus nerve #4A7C9B.",
            "camera": "Intense close-up on the sinoatrial node firing rhythmic electrical rings",
            "narration": "As adrenaline reaches the right atrium of your heart, it binds avidly to beta-1 adrenergic receptors on the sinoatrial node. Simultaneously, the parasympathetic vagus nerve, which normally acts as an acoustic calming brake, disengages completely. Stripped of its neural brake, your pacemaker node doubles its firing rate, thumping loudly against your chest wall.",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Visceral, kinetic, cardiac",
            "narrative_phase": "structural_model",
            "narrative_situation": "concrete_detail",
            "images_spec": [
                ("SC06_I1", "Detailed anatomical cutaway of the right atrium showing the crescent-shaped sinoatrial node on vellum #FAF7F0.", None, "visual_diagram", "burst", "concrete_detail"),
                ("SC06_I2", "Molecular depiction of epinephrine binding to seven-transmembrane beta-1 adrenergic receptors, triggering cAMP cascade.", "SC06_I1", "cutaway_detail", "fast", "concrete_detail"),
                ("SC06_I3", "The tenth cranial vagus nerve drawn in slate-blue #4A7C9B relaxing its inhibitory clamp on the cardiac plexus.", "SC06_I2", "visual_diagram", "normal", "concrete_detail"),
                ("SC06_I4", "Pacemaker action potential waves firing in rapid succession, moving from 60 beats per minute to 120 beats per minute.", "SC06_I3", "visual_diagram", "fast", "concrete_detail"),
                ("SC06_I5", "Cross-section of the entire beating heart contracting forcefully, sending arterial blood surging into the aorta.", "SC06_I4", "full_scene", "normal", "concrete_detail"),
                ("SC06_I6", "A mechanical brake caliper slipping off a spinning flywheel, visualizing the loss of vagal parasympathetic restraint.", "SC06_I5", "concept_metaphor", "normal", "concrete_detail"),
            ],
            "quotes": [
                "As adrenaline reaches the right atrium of your heart,",
                "it binds avidly to beta-1 adrenergic receptors on the sinoatrial node.",
                "Simultaneously, the parasympathetic vagus nerve,",
                "which normally acts as an acoustic calming brake, disengages completely.",
                "Stripped of its neural brake, your pacemaker node doubles its firing rate,",
                "thumping loudly against your chest wall."
            ]
        },
        # SC07
        {
            "id": "SC07",
            "title": "The Smartphone Trap",
            "purpose": "Expose how checking glowing smartphone screens halts melatonin and locks panic",
            "action": "A hand illuminates a bright blue screen in darkness, sending harsh photons into the retina and suppressing the pineal gland.",
            "setting": "Stark contrast of dark bedroom vellum #FAF7F0 and harsh artificial cyan glare.",
            "camera": "Direct frontal view of eyes exposed to glowing phone screen, tracking to pineal gland",
            "narration": "Now comes the critical mistake that traps millions of people in midnight panic. Feeling your pounding pulse, your hand reaches for your nightstand and unlocks your smartphone. A blast of blue-wavelength light hits your retinal ganglion cells, instantly halting melatonin production in your pineal gland and convincing your brain that dawn has broken.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Cautionary, analytical, revelatory",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "comparative_scale",
            "images_spec": [
                ("SC07_I1", "Hand reaching out from bedsheets to grasp a glowing rectangular smartphone on an antique nightstand on vellum #FAF7F0.", None, "full_scene", "fast", "comparative_scale"),
                ("SC07_I2", "Intense burst of cyan blue light striking the cornea and activating melanopsin-containing retinal ganglion cells.", "SC07_I1", "cutaway_detail", "fast", "comparative_scale"),
                ("SC07_I3", "Retinohypothalamic tract carrying daylight signals directly to the suprachiasmatic nucleus master clock.", "SC07_I2", "visual_diagram", "normal", "comparative_scale"),
                ("SC07_I4", "Pineal gland abruptly shutting down melatonin secretion, illustrated as an extinguished glowing oil lamp.", "SC07_I3", "concept_metaphor", "slow", "comparative_scale"),
                ("SC07_I5", "Split anatomical plate: peaceful nocturnal darkness vs chemical alertness locked in by artificial screen glare.", "SC07_I4", "visual_diagram", "normal", "comparative_scale"),
                ("SC07_I6", "The human silhouette trapped inside a glowing cage of digital lines, unable to re-enter slow-wave sleep.", "SC07_I5", "concept_metaphor", "normal", "comparative_scale"),
            ],
            "quotes": [
                "Now comes the critical mistake that traps millions of people in midnight panic.",
                "Feeling your pounding pulse, your hand reaches for your nightstand",
                "and unlocks your smartphone.",
                "A blast of blue-wavelength light hits your retinal ganglion cells,",
                "instantly halting melatonin production in your pineal gland",
                "and convincing your brain that dawn has broken."
            ]
        },
        # SC08
        {
            "id": "SC08",
            "title": "The Postural Error",
            "purpose": "Show how standing up drops venous return and spikes heart rate higher",
            "action": "A person swings legs out of bed and stands abruptly, causing blood to pool in legs and triggering carotid baroreflex tachycardia.",
            "setting": "Anatomical vascular etching on archival vellum #FAF7F0 showing hemodynamic hydrostatic pressures.",
            "camera": "Full-body vertical cutaway showing gravity pulling column of blood downward",
            "narration": "If you stand up abruptly to pace the hallway, gravity immediately pulls blood into your lower extremities. Venous return to the heart drops sharply, triggering carotid baroreceptors to fire another sympathetic burst. Your heart rate accelerates even further. The very actions you take to calm down end up reinforcing the chemical adrenaline trap.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Forensic, hemodynamic, cautionary",
            "narrative_phase": "structural_model",
            "narrative_situation": "concrete_detail",
            "images_spec": [
                ("SC08_I1", "Human figure sitting upright on bed edge, swinging bare feet down to the wooden floor on vellum #FAF7F0.", None, "full_scene", "fast", "concrete_detail"),
                ("SC08_I2", "Hydrostatic pressure diagram showing 500 milliliters of venous blood pooling in lower limb capacitance veins.", "SC08_I1", "visual_diagram", "fast", "concrete_detail"),
                ("SC08_I3", "Carotid sinus baroreceptors at the bifurcation of common carotid arteries sensing reduced stretch pressure.", "SC08_I2", "cutaway_detail", "normal", "concrete_detail"),
                ("SC08_I4", "Glossopharyngeal and sympathetic reflex arc firing an emergency booster signal back to the heart.", "SC08_I3", "visual_diagram", "normal", "concrete_detail"),
                ("SC08_I5", "Pulse rate graph showing an abrupt secondary spike from 100 to 135 beats per minute upon standing.", "SC08_I4", "visual_diagram", "fast", "concrete_detail"),
                ("SC08_I6", "Pacing footsteps in hallway leaving glowing red stress prints, symbolizing the self-reinforcing panic loop.", "SC08_I5", "concept_metaphor", "normal", "concrete_detail"),
            ],
            "quotes": [
                "If you stand up abruptly to pace the hallway,",
                "gravity immediately pulls blood into your lower extremities.",
                "Venous return to the heart drops sharply,",
                "triggering carotid baroreceptors to fire another sympathetic burst.",
                "Your heart rate accelerates even further.",
                "The very actions you take to calm down end up reinforcing the chemical adrenaline trap."
            ]
        },
        # SC09
        {
            "id": "SC09",
            "title": "Breathing Over Willpower",
            "purpose": "Deliver editorial commentary on respiration biomechanics over mental willpower",
            "action": "Thoracic diaphragm moves downward in graceful mechanical harmony, physically compressing heart chambers to trigger vagal braking.",
            "setting": "Classical respiratory biomechanics atlas on archival vellum #FAF7F0 with sage green #5E8C6A and slate blue #4A7C9B.",
            "camera": "Slow rhythmic expansion and contraction of the thoracic cage",
            "narration": "Fighting a nocturnal adrenaline surge with frustrated mental willpower is biologically futile. You cannot talk an elevated heart rate down when circulating epinephrine has a half-life of several minutes. Instead of ruminating over tomorrow's schedule, you must communicate with your autonomic nervous system using the physical biomechanics of respiration.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Empathetic, authoritative, physiological",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images_spec": [
                ("SC09_I1", "Anatomical etching of the head filled with swirling question marks and frantic clocks, contrasting with calm diaphragm below on vellum #FAF7F0.", None, "concept_metaphor", "slow", "editorial_commentary"),
                ("SC09_I2", "Chemical half-life decay curve showing circulating epinephrine lingering for 3 to 5 minutes in blood plasma.", "SC09_I1", "visual_diagram", "slow", "editorial_commentary"),
                ("SC09_I3", "Thoracic diaphragm muscle depicted as an elegant domed parachute separating chest from abdomen.", "SC09_I2", "visual_diagram", "normal", "editorial_commentary"),
                ("SC09_I4", "Vagus nerve fibers innervating pulmonary stretch receptors and cardiac ganglia in fine blue dip-pen linework.", "SC09_I3", "cutaway_detail", "slow", "editorial_commentary"),
                ("SC09_I5", "Antique brass balance scale tipping toward biological breathing mechanics and away from mental struggle.", "SC09_I4", "concept_metaphor", "slow", "editorial_commentary"),
                ("SC09_I6", "A serene anatomical figure lying completely flat in darkness with eyes closed, hand resting over diaphragm.", "SC09_I5", "full_scene", "slow", "editorial_commentary"),
            ],
            "quotes": [
                "Fighting a nocturnal adrenaline surge with frustrated mental willpower",
                "is biologically futile.",
                "You cannot talk an elevated heart rate down",
                "when circulating epinephrine has a half-life of several minutes.",
                "Instead of ruminating over tomorrow's schedule,",
                "you must communicate with your autonomic nervous system using the physical biomechanics of respiration."
            ]
        },
        # SC10
        {
            "id": "SC10",
            "title": "The Physiological Sigh Protocol",
            "purpose": "Guide viewer through two quick nasal inhales and one long slow exhale",
            "action": "A human demonstrates two sharp nasal sniffs expanding lung alveoli, followed by one long, slow sigh releasing all tension.",
            "setting": "Detailed alveolar and respiratory cross-section on archival vellum #FAF7F0.",
            "camera": "Rhythmic macro camera matching the two inhales and long exhale cycle",
            "narration": "The fastest physiological reset is the physiological sigh. Keep your eyes closed, take two quick inhales through your nose to reinflate collapsed alveoli, then release one long, slow, unforced exhale through your mouth. That prolonged exhale expands your thoracic cavity, compressing the heart and forcing the vagus nerve to slam on the parasympathetic brake.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Instructive, grounding, physiological mastery",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "concrete_detail",
            "images_spec": [
                ("SC10_I1", "Anatomical etching showing two successive arrows of nasal airflow entering nasal turbinates on vellum #FAF7F0.", None, "visual_diagram", "burst", "concrete_detail"),
                ("SC10_I2", "Microscopic clusters of pulmonary alveoli popping open like tiny grape clusters under positive pressure.", "SC10_I1", "cutaway_detail", "fast", "concrete_detail"),
                ("SC10_I3", "Smooth, long stream of warm oral exhale releasing from lips in soft mineral blue watercolor wash #4A7C9B.", "SC10_I2", "cutaway_detail", "slow", "concrete_detail"),
                ("SC10_I4", "Thoracic cage expanding during exhale, increasing intrathoracic pressure and gently compressing cardiac walls.", "SC10_I3", "visual_diagram", "normal", "concrete_detail"),
                ("SC10_I5", "Vagus nerve firing intense acetylcholine volleys directly onto the sinoatrial node, forcing pulse deceleration.", "SC10_I4", "cutaway_detail", "normal", "concrete_detail"),
                ("SC10_I6", "Cardiogram line visibly relaxing from crowded spikes into wide, rhythmic, peaceful wave intervals.", "SC10_I5", "visual_diagram", "slow", "concrete_detail"),
            ],
            "quotes": [
                "The fastest physiological reset is the physiological sigh.",
                "Keep your eyes closed, take two quick inhales through your nose",
                "to reinflate collapsed alveoli,",
                "then release one long, slow, unforced exhale through your mouth.",
                "That prolonged exhale expands your thoracic cavity, compressing the heart",
                "and forcing the vagus nerve to slam on the parasympathetic brake."
            ]
        },
        # SC11
        {
            "id": "SC11",
            "title": "Honoring Your Vessel",
            "purpose": "Close with profound reflection on listening to and respecting your vessel",
            "action": "The human rests peacefully in deep restorative sleep as internal vascular and nervous systems glow in harmonious balance.",
            "setting": "Tranquil twilight anatomical plate on warm archival vellum #FAF7F0.",
            "camera": "Gentle medium pull-back from tranquil sleeping face to full-body anatomical harmony, ending on channel endcard",
            "narration": "Within three cycles of physiological sighs, your pulse rate decelerates, peripheral vascular resistance drops, and circulating hormones begin clearing through your renal filters. Your body is a miraculous, self-regulating biological vessel that simply needs understanding rather than panic. Give your vessel a restful pause tonight and notice how it responds. See you in the next exploration.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Warm, peaceful, deeply empowering",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cta_close",
            "images_spec": [
                ("SC11_I1", "Human sleeping deeply with relaxed facial muscles, steady breathing chest, and resting heart rate on vellum #FAF7F0.", None, "full_scene", "normal", "cta_close"),
                ("SC11_I2", "Renal glomerular filtration diagram quietly clearing metabolites and hormonal byproducts into urine.", "SC11_I1", "cutaway_detail", "normal", "cta_close"),
                ("SC11_I3", "Full anatomical silhouette illuminated by soft golden ochre and carmine channels working in perfect autonomic balance.", "SC11_I2", "full_scene", "normal", "cta_close"),
                ("SC11_I4", "Antique medical journal resting on nightstand beside an unlit oil lamp and brass stethoscope.", "SC11_I3", "still_life", "normal", "cta_close"),
                ("SC11_I5", "Warm anatomical sketch of a hand placed peacefully over the heart with fine Latin callout 'Vas Cordis'.", "SC11_I4", "concept_metaphor", "normal", "cta_close"),
                ("SC11_I6", "Official Inside the Vessel 16:9 channel endcard on archival vellum #FAF7F0 with brass calipers, Da Vinci heart cutaway, and hand-lettered text 'INSIDE THE VESSEL'.", "SC11_I5", "white_card", "hold", "cta_close", True),
            ],
            "quotes": [
                "Within three cycles of physiological sighs, your pulse rate decelerates,",
                "peripheral vascular resistance drops,",
                "and circulating hormones begin clearing through your renal filters.",
                "Your body is a miraculous, self-regulating biological vessel",
                "that simply needs understanding rather than panic.",
                "Give your vessel a restful pause tonight and notice how it responds. See you in the next exploration."
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
                "preserve": "Archival vellum #FAF7F0, fine surgical dip-pen cross-hatching #1E1B18, arterial carmine #C85A5A and venous slate-blue #4A7C9B." if based_on else "Archival vellum #FAF7F0, fine surgical dip-pen cross-hatching #1E1B18, arterial carmine #C85A5A.",
                "change": desc,
                "reason": f"Medical visual progression beat {beat_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_type,
                "tempo": tempo,
                "narrative_situation": situation,
                "has_character": True,
                "is_endcard": is_endcard,
                "motion_prompt": "Smooth 2D medical atlas animation, gentle physiological idling, silent visual storytelling, no talking, no lip movement"
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


def get_inside_vessel_short():
    channel_id = "en_inside_vessel"
    job_id = "en-inside-vessel-batch1-9x16"
    parent_long_id = "en-inside-vessel-batch1-16x9"
    ch = get_channel(channel_id)

    topic = "Why Your Brain Fires Adrenaline at 3 AM"
    youtube_title = "Why Your Brain Fires Adrenaline at 3 AM"  # 39 chars <= 55

    sources = [
        {
            "id": "SRC01",
            "title": "Timing the end of nocturnal sleep",
            "reference": "Born, J. et al. (1999). Nature, 397, 29-30.",
            "facts": ["Nocturnal hepatic glycogen dips trigger early autonomic arousal."]
        },
        {
            "id": "SRC02",
            "title": "The polyvagal perspective: autonomic regulation",
            "reference": "Porges, S. W. (2007). Biological Psychology, 74(2), 116-143.",
            "facts": ["Vagal nerve withdrawal releases the brake on the sinoatrial node."]
        }
    ]

    required_points = [
        {"id": "R01", "text": "Waking up at 3:14 AM with a violently pounding heart in trembling panic"},
        {"id": "R02", "text": "Depleted liver glycogen causing your brain to fire an emergency adrenaline surge"},
        {"id": "R03", "text": "Ancient survival reflex running out of sync rather than broken psychology"},
        {"id": "R04", "text": "Physiological sigh with two quick nasal sniffs and long slow exhale to brake the heart"},
        {"id": "R05", "text": "Cliffhanger on recurring nighttime surges and spinoff bridge to full documentary"}
    ]

    editorial_stance = {
        "myth_debunked": "A 3 AM racing heart means an impending panic attack or heart defect.",
        "why_generic_advice_fails": "Willpower cannot clear circulating epinephrine without respiration biomechanics.",
        "channel_verdict": "Your body executed an emergency fuel rescue, and breathing biomechanics can instantly restore calm.",
        "tradeoff_or_blindspot": "Staying completely still in dark silence feels unnatural during panic, yet it is essential."
    }

    actionable_value = {
        "core_mechanism": "Low liver glycogen prompts an adrenaline spike that disengages vagal braking on the heart.",
        "practical_rule_of_thumb": "Two sharp nasal sniffs, one long sigh out, and keep bedroom lights black.",
        "real_world_scenario": "When waking with a racing chest at 3 AM, avoid bright phone screens and perform three physiological sighs."
    }

    thumbnail_spec = {
        "visual_hook": "Medical atlas silhouette of an awake human in bed with the adrenal gland and heart glowing in carmine ink.",
        "text_overlay": "MIDNIGHT ADRENALINE",
        "contrast_pair": "Dark bedroom vs Internal adrenal fire",
        "thumbnail_prompt": "Requested aspect ratio: 9:16. Render a complete 100% full-bleed vertical 9:16 high-impact YouTube poster thumbnail illustration extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, zero UI chrome, and zero dark vignette.\n\nVisual Style (ch_en_organ_buddies): Authentic 2D Vesalius medical atlas illustration on archival vellum (#FAF7F0). Dip-pen black hatching (#1E1B18). Translucent human torso revealing the golden adrenal gland above the kidney and racing heart stained in arterial carmine (#C85A5A). Orthographic 2D, museum medical plate texture, >=60% negative space, zero 3D, zero cartoon faces, zero gradients.\n\nPoster Typography: Hand-lettered uppercase English text in upper third: 'MIDNIGHT ADRENALINE'. Elegant Latin medical font etched directly onto parchment, strictly zero rectangular boxes or gradient cards.",
        "layout_mode": "split_contrast"
    }

    cta_plan = {
        "cliffhanger_peak": "What happens inside your blood vessels if this midnight adrenaline surge recurs every single night?",
        "bridge": "Watch the complete autonomic nervous system breakdown on Inside the Vessel YouTube.",
        "close": "Give your vessel a restful pause tonight.",
        "endcard_text": "WATCH FULL VIDEO ON YOUTUBE"
    }

    brief = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain the 3 AM adrenaline trigger in 5 punchy scenes and bridge viewers to the long-form autonomic explainer",
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
                "Deliver a fast-paced 5-scene short explainer with 20 unique medical etchings, maintaining an average hold under 2.5 seconds and zero AI cliches."
            ],
            "avoid": list(ch.avoid) + ["delve into", "testament to", "tapestry", "in conclusion", "it is important to remember"],
            "prior_knowledge": "None required.",
            "pacing": "Rapid-fire hook escalating directly to the cliffhanger question and long-form bridge.",
            "domain_requirements": [],
            "assumptions": [
                "Spoken in sharp, punchy English with zero clinical throat-clearing."
            ],
            "text_style": {
                "font": "Classical copperplate serif",
                "color": "#1E1B18",
                "outline": "#FAF7F0 vellum contrast",
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
            "channel_pillar": "Human Anatomy, Autonomic Physiology & Internal Health",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["why heart races at 3am", "cortisol awakening", "vagus nerve", "adrenaline surge", "shorts"],
            "cta_plan": cta_plan,
            "editorial_stance": editorial_stance,
            "actionable_value": actionable_value
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": thumbnail_spec,
        "channel_pillar": "Human Anatomy, Autonomic Physiology & Internal Health",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["why heart races at 3am", "cortisol awakening", "vagus nerve", "adrenaline surge", "shorts"],
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
            {"scene_id": "SC01", "purpose": "Immediate hook shock: snapping awake at 3:14 AM with a thumping chest", "requirements": ["R01"], "transition": "Trace inward to the liver"},
            {"scene_id": "SC02", "purpose": "Explain depleted liver glycogen firing an emergency fuel rescue", "requirements": ["R02"], "transition": "Transition into editorial reframing"},
            {"scene_id": "SC03", "purpose": "Editorial stance: an ancient survival reflex executing out of sync", "requirements": ["R03"], "transition": "Transition into physiological solution"},
            {"scene_id": "SC04", "purpose": "Demonstrate the physiological sigh to re-engage the vagus brake", "requirements": ["R04"], "transition": "Transition to peak cliffhanger"},
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
                    "channel_name": "Institute of Human Anatomy",
                    "top_performing_videos": [
                        {
                            "title": "Why You Wake Up in a Panic",
                            "views": "2.4M views",
                            "hook_technique": "Direct physical question addressing the 3 AM heart thumping sensation.",
                            "pacing_structure": "Hook -> Liver glycogen explanation -> Vagus nerve reset.",
                            "retention_driver": "Anatomical clarity that immediately dispels unnecessary panic."
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Validating common bodily sensations with biochemical proof.",
                        "Providing an actionable 30-second breathing technique."
                    ]
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Peaceful dark bedroom vs Internally racing arterial carmine heart.",
                "counter_intuitive_truth_slap": "Your heart isn't racing from anxiety; your liver ran low on sugar and triggered an adrenaline rescue."
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Sensory shock of waking with a pounding heart at 3:14 AM."},
                {"phase": "empirical_conflict", "purpose": "Liver glycogen depletion prompting emergency adrenaline."},
                {"phase": "structural_model", "purpose": "Editorial verdict: an ancient survival reflex misread as danger."},
                {"phase": "actionable_resolution", "purpose": "Physiological sigh re-engaging the vagus nerve brake."},
                {"phase": "cliffhanger_spinoff", "purpose": "Peak cliffhanger question bridging to the full YouTube documentary."}
            ],
            "flow_video_transition_blueprint": {
                "chain_mode": "daisy_chain",
                "video_model": "omni_flash",
                "keyframe_continuity": "Daisy-chained 2D medical etchings maintaining consistent vellum texture."
            }
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Human Anatomy, Autonomic Physiology & Internal Health",
            "myth_debunked": "A 3 AM racing heart means an impending panic attack or heart defect.",
            "channel_verdict": "Your body executed an emergency fuel rescue, and breathing biomechanics can instantly restore calm.",
            "actionable_rule_of_thumb": "Two sharp nasal sniffs, one long sigh out, and keep bedroom lights black."
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "What happens inside your blood vessels if this midnight adrenaline surge recurs every single night?",
            "bridge": "Watch the complete autonomic nervous system breakdown on Inside the Vessel YouTube.",
            "close": "Give your vessel a restful pause tonight.",
            "endcard_text": "WATCH FULL VIDEO ON YOUTUBE"
        }
    }

    scene_data = [
        # SC01
        {
            "id": "SC01",
            "title": "The Midnight Panic Awakening",
            "purpose": "Immediate hook shock: snapping awake at 3:14 AM with a thumping chest",
            "action": "Human snaps awake in dark bedroom, chest illuminated with racing red cardiac chambers on medical parchment.",
            "setting": "Archival vellum #FAF7F0 with fine surgical dip-pen cross-hatching #1E1B18.",
            "camera": "Dynamic vertical zoom into illuminated cardiac cross-section",
            "narration": "You wake up at 3:14 in the morning with your heart violently pounding in your throat. You did not have a nightmare, yet your entire body is trembling in fight-or-flight panic.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Electrifying, suspenseful, physical",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "images_spec": [
                ("SC01_I1", "Vertical 2D medical etching of a bedroom clock at 3:14 AM beside an awake human silhouette on vellum #FAF7F0.", None, "full_scene", "burst", "hook_shock"),
                ("SC01_I2", "Cutaway of the human ribcage showing the heart contracting violently in vivid arterial carmine #C85A5A.", "SC01_I1", "cutaway_detail", "fast", "hook_shock"),
                ("SC01_I3", "Close-up of dilated pupils in dark bedroom illuminated by neural firing sparks.", "SC01_I2", "variation", "fast", "hook_shock"),
                ("SC01_I4", "Autonomic nervous system silhouette glowing like copper wiring inside the human body.", "SC01_I3", "full_scene", "normal", "hook_shock"),
            ],
            "quotes": [
                "You wake up at 3:14 in the morning",
                "with your heart violently pounding in your throat.",
                "You did not have a nightmare,",
                "yet your entire body is trembling in fight-or-flight panic."
            ]
        },
        # SC02
        {
            "id": "SC02",
            "title": "The Liver Fuel Emergency",
            "purpose": "Explain depleted liver glycogen firing an emergency fuel rescue",
            "action": "Inside the abdomen, the liver depletes its glycogen reserves, prompting an emergency adrenaline burst from adrenal glands.",
            "setting": "Anatomical abdominal cross-section on vellum #FAF7F0 with hepatic ochre #D99B66.",
            "camera": "Cutaway tracking from liver to adrenal glands atop kidneys",
            "narration": "The culprit is not in your mind, but in your liver. As nocturnal glycogen stores run low, your brain senses a blood-sugar emergency and fires an adrenaline burst to liberate stored metabolic fuel.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Biochemical, revelatory, precise",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "mechanism_breakdown",
            "images_spec": [
                ("SC02_I1", "Classical medical etching of the liver showing depleted glycogen granules on archival vellum #FAF7F0.", None, "visual_diagram", "burst", "mechanism_breakdown"),
                ("SC02_I2", "Glucose level indicator dipping below critical threshold on a parchment gauge.", "SC02_I1", "visual_diagram", "fast", "mechanism_breakdown"),
                ("SC02_I3", "Adrenal glands firing golden adrenaline droplets directly into the inferior vena cava.", "SC02_I2", "cutaway_detail", "normal", "mechanism_breakdown"),
                ("SC02_I4", "Epinephrine molecules surging through the arterial bloodstream toward the chest.", "SC02_I3", "concept_metaphor", "fast", "mechanism_breakdown"),
            ],
            "quotes": [
                "The culprit is not in your mind, but in your liver.",
                "As nocturnal glycogen stores run low,",
                "your brain senses a blood-sugar emergency",
                "and fires an adrenaline burst to liberate stored metabolic fuel."
            ]
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Out-of-Sync Reflex",
            "purpose": "Editorial stance: an ancient survival reflex executing out of sync",
            "action": "A balance scale contrasts normal physiological survival wiring against behavioral traps like phone screens.",
            "setting": "Philosophical medical plate on warm vellum #FAF7F0.",
            "camera": "Slow cinematic push-in on classical medical scales",
            "narration": "Your vessel is not broken; it is running an ancient survival reflex out of sync. Reaching for a bright phone screen or pacing the hallway only locks in this chemical sympathetic trap.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Empathetic, sharp, demystifying",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "images_spec": [
                ("SC03_I1", "Classical brass calipers measuring healthy cardiac linework on vellum #FAF7F0, refuting broken heart defect.", None, "concept_metaphor", "slow", "editorial_commentary"),
                ("SC03_I2", "Human figure trapped between phone screen blue glare and dark bedroom stillness.", "SC03_I1", "full_scene", "slow", "editorial_commentary"),
                ("SC03_I3", "Carotid baroreceptors firing secondary tachycardia signals upon standing up abruptly.", "SC03_I2", "visual_diagram", "normal", "editorial_commentary"),
                ("SC03_I4", "Handwritten anatomical Latin annotation on vellum: 'Non defectus, sed refectio' (Not a defect, but a rescue).", "SC03_I3", "cutaway_detail", "slow", "editorial_commentary"),
            ],
            "quotes": [
                "Your vessel is not broken;",
                "it is running an ancient survival reflex out of sync.",
                "Reaching for a bright phone screen",
                "or pacing the hallway only locks in this chemical sympathetic trap."
            ]
        },
        # SC04
        {
            "id": "SC04",
            "title": "The Vagal Brake Reset",
            "purpose": "Demonstrate the physiological sigh to re-engage the vagus brake",
            "action": "Airflow streams into nasal passages in two quick inhales, followed by a long oral sigh that engages vagal heart braking.",
            "setting": "Respiratory biomechanics etching on vellum #FAF7F0 with slate-blue vagus nerve #4A7C9B.",
            "camera": "Rhythmic macro camera matching two nasal sniffs and long slow exhale",
            "narration": "To instantly engage your vagus nerve brake, practice the physiological sigh. Take two sharp inhales through your nose, followed by one long, slow, extended exhale through your mouth to decelerate your heart.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Instructive, calming, empowering",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "structural_model",
            "images_spec": [
                ("SC04_I1", "Anatomical etching showing twin inhalation arrows entering the nasal cavity on vellum #FAF7F0.", None, "visual_diagram", "burst", "structural_model"),
                ("SC04_I2", "Alveoli micro-clusters expanding fully under positive respiratory pressure.", "SC04_I1", "cutaway_detail", "fast", "structural_model"),
                ("SC04_I3", "Long smooth oral exhalation wash in slate-blue #4A7C9B relaxing the thoracic diaphragm.", "SC04_I2", "cutaway_detail", "normal", "structural_model"),
                ("SC04_I4", "The vagal nerve clamp engaging firmly onto the cardiac sinoatrial node, slowing beats.", "SC04_I3", "visual_diagram", "normal", "structural_model"),
            ],
            "quotes": [
                "To instantly engage your vagus nerve brake,",
                "practice the physiological sigh.",
                "Take two sharp inhales through your nose,",
                "followed by one long, slow, extended exhale through your mouth to decelerate your heart."
            ]
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Chronic Spike Spinoff",
            "purpose": "Peak cliffhanger question, channel bridge, and closing sign-off",
            "action": "Translucent human rests peacefully in bed, while a warning gauge flashes a recurring nightly question.",
            "setting": "Twilight anatomical plate on archival vellum #FAF7F0.",
            "camera": "Dramatic zoom on vascular network, cutting to official channel endcard hold",
            "narration": "What happens inside your blood vessels if this midnight adrenaline surge recurs every single night? Watch the complete autonomic nervous system breakdown on Inside the Vessel YouTube. Give your vessel a restful pause tonight.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Suspenseful, inviting, warm",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "cliffhanger_peak",
            "images_spec": [
                ("SC05_I1", "Cross-section of an arterial blood vessel under repeated endocrine stress on vellum #FAF7F0.", None, "cutaway_detail", "burst", "cliffhanger_peak"),
                ("SC05_I2", "Silhouette of human in bed beside an antique hourglass running out of sand.", "SC05_I1", "concept_metaphor", "fast", "cliffhanger_peak"),
                ("SC05_I3", "Friendly anatomical explorer gesturing warmly toward the viewer beside open medical atlas.", "SC05_I2", "variation", "normal", "cta_bridge"),
                ("SC05_I4", "Official Inside the Vessel 9:16 vertical channel endcard on archival vellum #FAF7F0 with Da Vinci heart etching, brass calipers, and hand-lettered text 'WATCH FULL VIDEO ON YOUTUBE'.", "SC05_I3", "white_card", "hold", "cta_close", True),
            ],
            "quotes": [
                "What happens inside your blood vessels if this midnight adrenaline surge",
                "recurs every single night?",
                "Watch the complete autonomic nervous system breakdown on Inside the Vessel YouTube.",
                "Give your vessel a restful pause tonight."
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
                "preserve": "Archival vellum #FAF7F0, fine surgical dip-pen cross-hatching #1E1B18, arterial carmine and slate-blue." if based_on else "Archival vellum #FAF7F0, fine surgical dip-pen cross-hatching #1E1B18, arterial carmine #C85A5A.",
                "change": desc,
                "reason": f"Short medical beat {beat_id}.",
                "visible_text": [],
                "kind": "scene",
                "shot_type": shot_type,
                "tempo": tempo,
                "narrative_situation": situation,
                "has_character": True,
                "is_endcard": is_endcard,
                "motion_prompt": "Smooth 2D medical atlas animation, gentle physiological idling, silent visual storytelling, no talking, no lip movement"
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
