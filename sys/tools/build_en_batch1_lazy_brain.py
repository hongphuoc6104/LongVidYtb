#!/usr/bin/env python3
"""Data generator for en_lazy_brain (Lazy Brain Lab) Schema 3.0 packages.

Storytelling Ref: Andrew Huberman, After Skool, Better Ideas
Visual Ref: Raw Indie Editorial Sketchbook (#F6F1E3 cream Moleskine paper,
2B graphite construction lines, Sumi-e brush ink, #E88D2A dopamine-amber highlights)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
from channels.registry import channel_cast, channel_profile_stamp, get_channel
from tools.channel_production_common import compile_channel_scene_prompt


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


def build_lazy_brain_long() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_lazy_brain"
    slug = "en-lazy-brain"
    job_id = f"{slug}-batch1-16x9"
    ch = get_channel(channel_id)

    topic = "Task Paralysis Is Not Laziness: How Open Loops and Amygdala Threat Tagging Drain Your Prefrontal Cortex"
    youtube_title = "Why a 5-Minute Email Drains Your Brain All Day"

    brief: Dict[str, Any] = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain the neuroscience of task paralysis, debunk moral laziness through amygdala threat evaluation and open loops, and provide the 90-second ugly draft protocol.",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 150.0,
            "max_seconds": 210.0,
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "Staring at an unfinished three-sentence email for four hours and the resulting exhaustion."},
            {"id": "R02", "text": "The illusion of physical fatigue caused by cognitive freeze mode rather than bodily exertion."},
            {"id": "R03", "text": "The amygdala's ancient threat radar misidentifying ambiguous work tasks as physical predators."},
            {"id": "R04", "text": "How ambiguity triggers adrenaline and cortisol, locking prefrontal rational circuits."},
            {"id": "R05", "text": "The Zeigarnik Effect keeping unclosed tasks burning background working memory RAM."},
            {"id": "R06", "text": "Editorial commentary on why conventional hustle culture advice worsens biological panic."},
            {"id": "R07", "text": "Prefrontal cortex metabolic energy depletion from continuous internal resistance."},
            {"id": "R08", "text": "The anterior mid-cingulate cortex (aMCC) growing only through friction-heavy micro-actions."},
            {"id": "R09", "text": "The ninety-second ugly draft protocol that mechanically shuts off amygdala threat tagging."},
            {"id": "R10", "text": "Editorial verdict that action precedes emotional readiness, not the other way around."},
            {"id": "R11", "text": "Closing synthesis, habit rule, and community discussion on neuroplastic tenacity."},
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
                "title": "Neural Mechanisms of Procrastination and Amygdala Threat Evaluation",
                "reference": "Zhang, S. et al. (2021). Journal of Cognitive Neuroscience, 33(5), 890-904.",
                "facts": [
                    "The amygdala tags ambiguous social evaluation as an acute survival threat.",
                    "Threat-tagging inhibits dorsolateral prefrontal cortex executive functioning.",
                ],
            },
            {
                "id": "SRC02",
                "title": "On Finished and Unfinished Tasks: Cognitive Load and the Zeigarnik Effect",
                "reference": "Zeigarnik, B. (1927). Psychologische Forschung, 9, 1-85.",
                "facts": [
                    "Uncompleted tasks remain active in working memory, consuming continuous cognitive bandwidth.",
                    "Interrupting an activity leaves intrusive cognitive tension until closure occurs.",
                ],
            },
            {
                "id": "SRC03",
                "title": "The Anterior Mid-Cingulate Cortex and Human Tenacity",
                "reference": "Touroutoglou, A. et al. (2020). Trends in Cognitive Sciences, 24(9), 704-714.",
                "facts": [
                    "The anterior mid-cingulate cortex increases in volume through voluntary effort against friction.",
                    "Micro-actions facing resistance stimulate neuroplasticity and strengthen self-regulation.",
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
                "Demystify task paralysis through amygdala threat evaluation without academic guilt.",
                "Demonstrate the Zeigarnik Effect background cognitive drain with clear sketchbook metaphors.",
                "Equip viewers with the 90-second ugly draft protocol to lower executive friction immediately.",
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Basic familiarity with procrastination and everyday workday fatigue.",
            "pacing": "Empathetic, punchy, conversational spoken cadence calibrated at 3.8 words per second.",
            "assumptions": [
                "Each scene averages 6 unique hand-inked visual beats with high tactile paper texture.",
            ],
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Blue-shirt stickman paralyzed at desk staring at a massive ominous email envelope with glowing amber threat teeth",
                "text_overlay": "EMAIL BRAIN DRAIN",
                "contrast_pair": "Five-minute short email vs All-day total mental exhaustion",
                "thumbnail_prompt": "Hand-inked 2D indie neuroscience sketchbook illustration on warm textured cotton rag paper (#F8F0DC deckle-edge paper grain). Iconic bald circle stickman in matte cobalt-blue (#3B82C4) t-shirt sitting frozen in wooden chair, staring terrified at a giant floating white mail envelope with sharp ink teeth and dopamine-amber (#E88D2A) alarm sparks. Visible 2B graphite pencil construction marks, dip-pen pitch-black (#000000) ink hatch lines. Bold uppercase hand-lettered text in upper third: 'EMAIL BRAIN DRAIN'. Orthographic 2D, >=60% negative space, zero 3D CGI, zero plastic sheen.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Neuroscience of Focus & Behavioral Friction",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["lazy brain lab", "procrastination", "task paralysis", "neuroscience", "amygdala", "zeigarnik effect"],
            "cta_plan": {
                "close": "Try the ninety-second protocol today, and tell us below what shifted for your focus.",
                "endcard_text": "FULL VIDEO ON LAZY BRAIN LAB",
            },
            "editorial_stance": {
                "myth_debunked": "Procrastination on critical tasks stems from moral laziness, defective willpower, or poor time management.",
                "why_generic_advice_fails": "Telling people to push through or shame themselves triggers additional amygdala panic, worsening the physiological freeze response.",
                "channel_verdict": "Task paralysis is an involuntary biological defense mechanism against perceived social ambiguity, not a character flaw.",
                "tradeoff_or_blindspot": "Lowering your standards to write an intentionally terrible first draft feels counterintuitive, but it is the only way to disarm threat tagging.",
            },
            "actionable_value": {
                "core_mechanism": "Ambiguity triggers amygdala threat-tagging, locking the prefrontal cortex until an open cognitive loop is mechanically closed.",
                "practical_rule_of_thumb": "Lower the threshold to zero with a ninety-second ugly draft on scrap paper.",
                "real_world_scenario": "When frozen by an intimidating email from your boss, write the worst possible three-sentence draft immediately.",
            },
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Blue-shirt stickman paralyzed at desk staring at a massive ominous email envelope with glowing amber threat teeth",
            "text_overlay": "EMAIL BRAIN DRAIN",
            "contrast_pair": "Five-minute short email vs All-day total mental exhaustion",
            "thumbnail_prompt": "Hand-inked 2D indie neuroscience sketchbook illustration on warm textured cotton rag paper (#F8F0DC deckle-edge paper grain). Iconic bald circle stickman in matte cobalt-blue (#3B82C4) t-shirt sitting frozen in wooden chair, staring terrified at a giant floating white mail envelope with sharp ink teeth and dopamine-amber (#E88D2A) alarm sparks. Visible 2B graphite pencil construction marks, dip-pen pitch-black (#000000) ink hatch lines. Bold uppercase hand-lettered text in upper third: 'EMAIL BRAIN DRAIN'. Orthographic 2D, >=60% negative space, zero 3D CGI, zero plastic sheen.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Neuroscience of Focus & Behavioral Friction",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["lazy brain lab", "procrastination", "task paralysis", "neuroscience", "amygdala", "zeigarnik effect"],
        "cta_plan": {
            "close": "Try the ninety-second protocol today, and tell us below what shifted for your focus.",
            "endcard_text": "FULL VIDEO ON LAZY BRAIN LAB",
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
            "myth_debunked": "Procrastination on critical tasks stems from moral laziness, defective willpower, or poor time management.",
            "why_generic_advice_fails": "Telling people to push through or shame themselves triggers additional amygdala panic, worsening the physiological freeze response.",
            "channel_verdict": "Task paralysis is an involuntary biological defense mechanism against perceived social ambiguity, not a character flaw.",
            "tradeoff_or_blindspot": "Lowering your standards to write an intentionally terrible first draft feels counterintuitive, but it is the only way to disarm threat tagging.",
        },
        "actionable_value": {
            "core_mechanism": "Ambiguity triggers amygdala threat-tagging, locking the prefrontal cortex until an open cognitive loop is mechanically closed.",
            "practical_rule_of_thumb": "Lower the threshold to zero with a ninety-second ugly draft on scrap paper.",
            "real_world_scenario": "When frozen by an intimidating email from your boss, write the worst possible three-sentence draft immediately.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook the viewer with the visceral torture of staring at a 3-sentence email.", "requirements": ["R01"], "transition": "Transition into the false perception of physical tiredness."},
            {"scene_id": "SC02", "purpose": "Deconstruct why cognitive freeze mimics heavy physical labor.", "requirements": ["R02"], "transition": "Introduce the temporal lobe threat radar."},
            {"scene_id": "SC03", "purpose": "Explain the amygdala's evolutionary threat detection role.", "requirements": ["R03"], "transition": "Showcase how ambiguity triggers chemical alarms."},
            {"scene_id": "SC04", "purpose": "Demonstrate the neurological lockdown caused by ambiguous social tasks.", "requirements": ["R04"], "transition": "Connect lingering tasks to cognitive working memory."},
            {"scene_id": "SC05", "purpose": "Illustrate the Zeigarnik Effect burning background mental RAM.", "requirements": ["R05"], "transition": "Deliver sharp critique on hustle culture productivity advice."},
            {"scene_id": "SC06", "purpose": "Editorial commentary on why willpower shaming worsens task freeze.", "requirements": ["R06"], "transition": "Examine the metabolic energy toll on the prefrontal cortex."},
            {"scene_id": "SC07", "purpose": "Show the prefrontal cortex glucose depletion under open loops.", "requirements": ["R07"], "transition": "Introduce the neurobiological seat of human willpower."},
            {"scene_id": "SC08", "purpose": "Explain how the anterior mid-cingulate cortex (aMCC) builds tenacity.", "requirements": ["R08"], "transition": "Present the counter-intuitive behavioral antidote."},
            {"scene_id": "SC09", "purpose": "Walk through the 90-second ugly draft protocol step-by-step.", "requirements": ["R09"], "transition": "Provide philosophical verdict on motivation versus momentum."},
            {"scene_id": "SC10", "purpose": "Editorial verdict that action must precede emotional readiness.", "requirements": ["R10"], "transition": "Synthesize key neuroplastic takeaways and close."},
            {"scene_id": "SC11", "purpose": "Consolidate daily habit rule and invite thoughtful community engagement.", "requirements": ["R11"], "transition": "End of explainer."},
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Andrew Huberman (Huberman Lab)",
                    "top_performing_videos": [
                        {
                            "title": "How to Optimize Your Brain-Body Function & Overcome Procrastination",
                            "views": "4.2M views",
                            "hook_technique": "Grounding everyday distraction in precise neural circuitry without moral blame.",
                            "pacing_structure": "Everyday symptom -> Neurochemical mechanism -> Friction-lowering behavioural protocol.",
                            "retention_driver": "Validating the biological reality of dopamine depletion and stress alarms.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Translates neurobiology into physical mechanisms like alarm switches and fuel meters.",
                        "Replaces guilt with curiosity by analyzing brain circuits as evolutionary artifacts.",
                    ],
                },
                {
                    "channel_name": "After Skool",
                    "top_performing_videos": [
                        {
                            "title": "Why You Can't Get Anything Done",
                            "views": "3.1M views",
                            "hook_technique": "Hand-drawn chalkboard metaphor showing a tiny person overwhelmed by gigantic tasks.",
                            "pacing_structure": "Visual struggle -> Deep psychological theory -> Tangible mindset shift.",
                            "retention_driver": "Tactile drawing strokes unfolding in sync with narration.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Visualizes internal psychological friction through physical metaphors.",
                        "Uses sparse, impactful color accents to highlight neural pathways.",
                    ],
                },
                {
                    "channel_name": "Better Ideas",
                    "top_performing_videos": [
                        {
                            "title": "Why you can't focus on anything anymore",
                            "views": "2.8M views",
                            "hook_technique": "Relatable comedic self-awareness about staring at a blank screen while organizing pencils.",
                            "pacing_structure": "Embarrassing lived anecdote -> The trap explained -> The micro-step unlock.",
                            "retention_driver": "Conversational vulnerability combined with sharp analytical insight.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Normalizes the absurd lengths people go to avoid answering a simple message.",
                        "Focuses on immediate tactile experiments rather than grand life overhauls.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 21,
                "zero_pause_opening_seconds": 14,
                "visual_contrast": "Tiny stickman at wooden desk dwarfed by a blinking cursor against an expansive cream sketchbook canvas.",
                "counter_intuitive_truth_slap": "You are not avoiding work because you lack willpower; your nervous system is treating an ambiguous inbox like a predatory tiger.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Visceral relatable depiction of email paralysis at the desktop."},
                {"phase": "empirical_conflict", "purpose": "Brain threat evaluation misidentifying ambiguous text as physical danger."},
                {"phase": "structural_model", "purpose": "The Zeigarnik open loop burning background working memory capacity."},
                {"phase": "actionable_resolution", "purpose": "The 90-second ugly draft lowering executive stakes to zero."},
                {"phase": "cliffhanger_spinoff", "purpose": "The anterior mid-cingulate cortex growing tenacity through micro-friction."},
            ],
            "tactile_visual_benchmark": {
                "paper_surface": "Textured warm cotton rag paper (#F8F0DC deckle-edge paper grain) with visible 2B pencil construction marks.",
                "ink_technique": "Dip-pen Sumi-e black ink outlines (#000000) with hand-drawn analog cross-hatching.",
                "palette_application": "Matte mineral watercolor washes in cobalt blue (#3B82C4), dopamine-amber (#E88D2A), and sage green (#93A88C).",
                "anti_ai_rules": "Zero 3D CGI, zero neon glows, zero smooth vector gradients, minimum 60% negative space on raw paper grain.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Neuroscience of Focus & Behavioral Friction",
            "myth_debunked": "Procrastination on critical tasks stems from moral laziness, defective willpower, or poor time management.",
            "channel_verdict": "Task paralysis is an involuntary biological defense mechanism against perceived social ambiguity, not a character flaw.",
            "actionable_rule_of_thumb": "Lower the threshold to zero with a ninety-second ugly draft on scrap paper.",
        },
        "cta_and_spinoff_strategy": {
            "close": "Try the ninety-second protocol today, and tell us below what shifted for your focus.",
            "endcard_text": "FULL VIDEO ON LAZY BRAIN LAB",
        },
    }

    # 11 scenes, 6 beats & 6 images each = 66 unique images, 623 words
    scenes_data = [
        # SC01
        {
            "id": "SC01",
            "title": "The Blinking Cursor Trap",
            "purpose": "Hook the viewer with the visceral torture of staring at a 3-sentence email.",
            "action": "Stickman in cobalt t-shirt sitting at a wooden desk with head in hands before an empty laptop screen.",
            "setting": "Raw sketchbook study desk on warm cotton rag paper #F8F0DC.",
            "camera": "Eye-level medium shot centering on the blinking cursor.",
            "narration": "You have been staring at an unfinished three-sentence email for four hours. The cursor blinks against a blank white window like a tiny interrogation light. You could type the entire reply in ninety seconds. Yet opening that draft makes your chest tighten up, so you clean your desk and reorganize your bookmarks instead.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Empathetic, sharp, relatable",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "prompts": [
                ("SC01_I1", "Hand-inked 2D indie sketchbook stickman in cobalt-blue shirt sitting at a wooden desk staring paralyzed at an open laptop screen on warm cotton rag paper #F8F0DC, visible graphite pencil layout marks, dip-pen ink hatch lines, >=60% negative space.", "burst", "full_scene"),
                ("SC01_I2", "Close-up macro detail of an antique mechanical clock on the wall ticking past four hours while the stickman remains frozen at the desk on textured rag paper #F8F0DC, charcoal linework with subtle amber ink wash #E88D2A.", "fast", "macro_detail"),
                ("SC01_I3", "Conceptual indie illustration of a tiny glowing red vertical cursor pulsing like an intense interrogation spotlight over the stickman on textured cream paper #F8F0DC, minimal dip-pen lines.", "fast", "concept_metaphor"),
                ("SC01_I4", "Doodle illustration of a small 90-second mechanical sand hourglass next to a blank sheet of paper, demonstrating simplicity on textured cotton rag paper #F8F0DC, cobalt ink highlights.", "normal", "concept_metaphor"),
                ("SC01_I5", "Stickman clutching chest with spiral graphite lines radiating around the heart, showing physical tension while leaning away from the monitor on cream paper #F8F0DC.", "normal", "variation"),
                ("SC01_I6", "Stickman frantically wiping a tidy desk with a feather duster and lining up colorful fountain pens in extreme procrastination on textured paper #F8F0DC, sage green #93A88C watercolor wash.", "hold", "full_scene"),
            ],
            "quotes": [
                "You have been staring at an unfinished three-sentence email",
                "for four hours.",
                "The cursor blinks against a blank white window like a tiny interrogation light.",
                "You could type the entire reply in ninety seconds.",
                "Yet opening that draft makes your chest tighten up,",
                "so you clean your desk and reorganize your bookmarks instead.",
            ],
        },
        # SC02
        {
            "id": "SC02",
            "title": "The False Fatigue of Freeze Mode",
            "purpose": "Deconstruct why cognitive freeze mimics heavy physical labor.",
            "action": "Stickman collapsed horizontally over the desk looking drained despite zero physical exertion.",
            "setting": "Minimalist sketchbook bedroom office under dim lamp.",
            "camera": "Slow tilt downwards emphasizing physical heaviness.",
            "narration": "By evening, you feel completely exhausted, as if you carried heavy cinderblocks up three flights of concrete stairs. Naturally, you tell yourself you are lazy or undisciplined. But modern neurobiology shows something entirely different. Your body did not expend physical energy today; your prefrontal cortex was quietly hijacked by a false biological alarm.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Analytical, deconstructive",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC02_I1", "Stickman in cobalt t-shirt slumped completely flat across a wooden desk like a deflated balloon under an inked hanging lamp on textured cotton rag paper #F8F0DC, delicate cross-hatching.", "fast", "full_scene"),
                ("SC02_I2", "Metaphorical sketch of the stickman struggling to carry three heavy textured stone cinderblocks up a spiral graphite staircase on warm cream paper #F8F0DC.", "normal", "concept_metaphor"),
                ("SC02_I3", "Stickman looking into a small vanity mirror with a harsh thought bubble labeled with shame symbols on textured rag paper #F8F0DC, charcoal linework.", "normal", "full_scene"),
                ("SC02_I4", "Anatomical cross-section sketch of the human brain drawn in fine technical dip-pen ink on cotton vellum #F8F0DC, glowing cobalt blue accents #3B82C4 outlining frontal lobes.", "fast", "concept_metaphor"),
                ("SC02_I5", "Stickman sitting motionless on a stool with an empty battery meter floating overhead showing zero calories burned on textured paper #F8F0DC, dry sage wash #93A88C.", "normal", "full_scene"),
                ("SC02_I6", "The prefrontal cortex highlighted in red ink with an alarm bell clapper ringing erratically above the frontal bone on textured rag paper #F8F0DC, amber watercolor burst #E88D2A.", "hold", "macro_detail"),
            ],
            "quotes": [
                "By evening, you feel completely exhausted,",
                "as if you carried heavy cinderblocks up three flights of concrete stairs.",
                "Naturally, you tell yourself you are lazy or undisciplined.",
                "But modern neurobiology shows something entirely different.",
                "Your body did not expend physical energy today;",
                "your prefrontal cortex was quietly hijacked by a false biological alarm.",
            ],
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Savanna Threat Radar",
            "purpose": "Explain the amygdala's evolutionary threat detection role.",
            "action": "Split illustration showing primitive savanna danger versus a modern email notification.",
            "setting": "Evolutionary landscape transitioning into modern workspace.",
            "camera": "Panoramic comparative split framing.",
            "narration": "Hidden deep inside your temporal lobe sits the amygdala, your brain's ancient threat radar. It evolved to spot rustling tall grass and apex predators on the savanna. The trouble is, your amygdala cannot tell the difference between a hungry saber-toothed cat and an ambiguous email from your supervisor asking to speak tomorrow morning.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Fascinating, visual, evolutionary",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC03_I1", "Hand-drawn anatomical sketch of the deep temporal lobe pinpointing the almond-shaped amygdala in rich dark brown ink on textured rag paper #F8F0DC, graphite margin notes.", "burst", "macro_detail"),
                ("SC03_I2", "Vintage radar scanner metaphor drawn as brass nautical rings with a sweeping needle detecting blips on textured vellum #F8F0DC, cobalt accents #3B82C4.", "fast", "concept_metaphor"),
                ("SC03_I3", "Prehistoric hunter stickman crouching in wind-blown savanna grass watching the glowing silhouette of a saber-toothed tiger on cream cotton paper #F8F0DC, charcoal shading.", "normal", "environment"),
                ("SC03_I4", "Split comparative diagram on textured rag paper: on left a ferocious prehistoric predator, on right an unread white email envelope on a desk, both outlined in identical red ink lines.", "normal", "concept_metaphor"),
                ("SC03_I5", "Stickman staring wide-eyed at a glowing pop-up window notification with jagged sharp edges on textured paper #F8F0DC, dopamine-amber wash #E88D2A.", "fast", "full_scene"),
                ("SC03_I6", "Close-up of the stickman's dilated pupils reflecting both the saber-toothed predator and an unread email subject line on warm paper #F8F0DC, dip-pen ink lines.", "hold", "macro_detail"),
            ],
            "quotes": [
                "Hidden deep inside your temporal lobe sits the amygdala,",
                "your brain's ancient threat radar.",
                "It evolved to spot rustling tall grass and apex predators on the savanna.",
                "The trouble is, your amygdala cannot tell the difference",
                "between a hungry saber-toothed cat and an ambiguous email",
                "from your supervisor asking to speak tomorrow morning.",
            ],
        },
        # SC04
        {
            "id": "SC04",
            "title": "The Neurobiology of Ambiguity",
            "purpose": "Demonstrate the neurological lockdown caused by ambiguous social tasks.",
            "action": "Stickman enveloped by shadowy question marks as chemical vials pour into synapses.",
            "setting": "Abstract cognitive space rendered in sketchbook watercolor wash.",
            "camera": "Macro zoom into stylized neural pathways.",
            "narration": "When an incoming task lacks immediate clarity, your nervous system automatically tags it as high-stakes danger. Ambiguity triggers an involuntary micro-dose of adrenaline and cortisol. Your rational prefrontal circuits lock up in freeze mode. You are not avoiding work because you lack willpower; you are freezing because your biology treats that inbox like a physical ambush.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Scientific, liberating, intense",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC04_I1", "Stickman surrounded by towering hand-drawn question marks resembling menacing granite statues on textured rag paper #F8F0DC, graphite shading.", "fast", "full_scene"),
                ("SC04_I2", "A giant stamped red wax seal reading 'DANGER' slamming down onto an innocent paper memo on textured cream paper #F8F0DC, vermilion ink droplets.", "normal", "concept_metaphor"),
                ("SC04_I3", "Two vintage chemical apothecary dropper bottles labeled adrenaline and cortisol dropping ink droplets onto neural dendrites on paper #F8F0DC, amber wash #E88D2A.", "normal", "concept_metaphor"),
                ("SC04_I4", "Stylized prefrontal neural circuits freezing over with intricate crystalline ice patterns drawn in dip-pen white ink on slate-gray background #F8F0DC.", "slow", "concept_metaphor"),
                ("SC04_I5", "Stickman pulling backward against a heavy steel anchor chain labeled 'willpower myth' on textured rag paper #F8F0DC, charcoal hatching.", "normal", "full_scene"),
                ("SC04_I6", "Stickman taking cover behind a wooden desk while ink-splattered paper airplane arrows fly overhead like a medieval ambush on textured cotton paper #F8F0DC.", "hold", "environment"),
            ],
            "quotes": [
                "When an incoming task lacks immediate clarity,",
                "your nervous system automatically tags it as high-stakes danger.",
                "Ambiguity triggers an involuntary micro-dose of adrenaline and cortisol.",
                "Your rational prefrontal circuits lock up in freeze mode.",
                "You are not avoiding work because you lack willpower;",
                "you are freezing because your biology treats that inbox like a physical ambush.",
            ],
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Zeigarnik Background Drain",
            "purpose": "Illustrate the Zeigarnik Effect burning background mental RAM.",
            "action": "A spinning loading wheel hovering over stickman while doing other daily activities.",
            "setting": "Everyday vignettes overlaid with semi-transparent cognitive load wheels.",
            "camera": "Multi-panel comic style layout on sketchbook paper.",
            "narration": "Leaving the email unwritten creates what cognitive psychologists call an open cognitive loop. Bluma Zeigarnik discovered a century ago that uncompleted tasks refuse to leave working memory. Even while scrolling social videos or eating lunch, that open loop quietly burns valuable neural bandwidth in the background, draining your metabolic battery all afternoon.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Illuminating, relatable, eye-opening",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC05_I1", "Stylized diagram of a glowing circular arrow loop that never closes, spinning endlessly above stickman's head on textured rag paper #F8F0DC, cobalt ink #3B82C4.", "burst", "concept_metaphor"),
                ("SC05_I2", "Vintage 1920s European café vignette with psychologist Bluma Zeigarnik observing busy waiters remembering unpaid orders, sketched in sepia ink on cream paper #F8F0DC.", "fast", "environment"),
                ("SC05_I3", "An open mechanical filing cabinet in the brain with documents spilling out uncontrollably onto the floor on textured rag paper #F8F0DC, fine dip-pen lines.", "normal", "concept_metaphor"),
                ("SC05_I4", "Stickman eating a sandwich at lunch while a ghostly translucent email window hovers persistently right before their eyes on textured paper #F8F0DC, sage green wash #93A88C.", "slow", "full_scene"),
                ("SC05_I5", "Computer motherboard schematic drawn in pencil with a single glowing RAM slot overheating and smoking in amber ink on textured cotton vellum #F8F0DC.", "normal", "macro_detail"),
                ("SC05_I6", "Stickman's body drawn as a transparent glass battery meter with green liquid steadily leaking through a cracked seam at the base on cream paper #F8F0DC.", "hold", "concept_metaphor"),
            ],
            "quotes": [
                "Leaving the email unwritten creates what cognitive psychologists call an open cognitive loop.",
                "Bluma Zeigarnik discovered a century ago",
                "that uncompleted tasks refuse to leave working memory.",
                "Even while scrolling social videos or eating lunch,",
                "that open loop quietly burns valuable neural bandwidth in the background,",
                "draining your metabolic battery all afternoon.",
            ],
        },
        # SC06
        {
            "id": "SC06",
            "title": "The Failure of Hustle Shaming",
            "purpose": "Editorial commentary on why willpower shaming worsens task freeze.",
            "action": "Aggressive motivational slogans tearing apart while stickman curls defensively.",
            "setting": "Harsh spotlight on empty sketchbook page with ripped paper texture.",
            "camera": "Direct front-facing confrontational perspective.",
            "narration": "This is why conventional productivity advice completely fails. Yelling at yourself to just sit down and focus only validates the amygdala's panic signal. Hustle culture treats task paralysis like a moral defect requiring brutal shame. In reality, demanding flawless perfection on an ambiguous task guarantees your nervous system will slam on the emergency brake every single time.",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Sharp, defiant, compassionate",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "prompts": [
                ("SC06_I1", "A generic self-help book cover with bold aggressive fonts crumbling into ash and graphite dust on textured cotton rag paper #F8F0DC, dip-pen ink hatching.", "slow", "concept_metaphor"),
                ("SC06_I2", "A giant megaphone shouting jagged spiky sound waves at the cowering stickman, magnifying red threat sparks around the amygdala on cream paper #F8F0DC.", "normal", "full_scene"),
                ("SC06_I3", "Stickman wearing a medieval pillory labeled 'guilt' while standing before an empty easel on textured paper #F8F0DC, dark charcoal shading.", "slow", "concept_metaphor"),
                ("SC06_I4", "An ink-drawn judge's gavel slamming down onto an unfinished diary page, scattering papers into the margins on textured rag paper #F8F0DC.", "slow", "concept_metaphor"),
                ("SC06_I5", "A fragile porcelain vase representing perfectionism cracking under the immense weight of an ambiguous deadline on cream cotton paper #F8F0DC, amber accents #E88D2A.", "normal", "macro_detail"),
                ("SC06_I6", "A massive cast-iron mechanical brake shoe clamping hard onto a spinning railroad wheel with sparks flying on textured rag paper #F8F0DC, deep black ink.", "hold", "concept_metaphor"),
            ],
            "quotes": [
                "This is why conventional productivity advice completely fails.",
                "Yelling at yourself to just sit down and focus only validates the amygdala's panic signal.",
                "Hustle culture treats task paralysis like a moral defect",
                "requiring brutal shame.",
                "In reality, demanding flawless perfection on an ambiguous task",
                "guarantees your nervous system will slam on the emergency brake every single time.",
            ],
        },
        # SC07
        {
            "id": "SC07",
            "title": "Prefrontal Energy Starvation",
            "purpose": "Show the prefrontal cortex glucose depletion under open loops.",
            "action": "A glowing brain fuel gauge dipping into the red empty zone.",
            "setting": "Technical laboratory schematic drawn on Moleskine paper.",
            "camera": "Intimate diagrammatic exploration of brain metabolism.",
            "narration": "Your prefrontal cortex consumes roughly twenty percent of total resting energy despite accounting for only two percent of your body mass. Wrestling an open loop forces your brain to juggle competing threat signals against executive commands. After four hours of internal resistance, your glucose stores drop, leaving you mentally paralyzed before typing a single sentence.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Quantitative, rigorous, scientific",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC07_I1", "An inked pie chart comparing a tiny 2% body mass slice to a glowing 20% metabolic furnace consuming glucose in vibrant cobalt blue #3B82C4 on textured paper #F8F0DC.", "burst", "concept_metaphor"),
                ("SC07_I2", "Stickman holding two heavy scale pans balancing a tiny brain against a giant pile of sugar cubes on textured rag paper #F8F0DC, 2B pencil hatching.", "fast", "concept_metaphor"),
                ("SC07_I3", "Two stickmen inside the skull engaged in an exhausting tug-of-war over a fraying nerve cable on textured paper #F8F0DC, amber ink accents #E88D2A.", "normal", "concept_metaphor"),
                ("SC07_I4", "Complex circuit diagram of executive command signals crashing into red roadblock barriers on textured cotton vellum #F8F0DC, dip-pen drafting lines.", "normal", "macro_detail"),
                ("SC07_I5", "An antique glass beaker with glucose liquid dripping steadily to the very bottom line marked 'CRITICAL DEPLETION' on cream paper #F8F0DC.", "fast", "macro_detail"),
                ("SC07_I6", "Stickman seated before a typewriter with hands frozen above keys as if coated in solid hardening plaster on textured rag paper #F8F0DC, charcoal outlines.", "hold", "full_scene"),
            ],
            "quotes": [
                "Your prefrontal cortex consumes roughly twenty percent of total resting energy",
                "despite accounting for only two percent of your body mass.",
                "Wrestling an open loop forces your brain",
                "to juggle competing threat signals against executive commands.",
                "After four hours of internal resistance, your glucose stores drop,",
                "leaving you mentally paralyzed before typing a single sentence.",
            ],
        },
        # SC08
        {
            "id": "SC08",
            "title": "The Tenacity Engine (aMCC)",
            "purpose": "Explain how the anterior mid-cingulate cortex (aMCC) builds tenacity.",
            "action": "A hidden neural muscle expanding with glowing golden linework as effort is applied.",
            "setting": "Deep cerebral architecture schematic on warm vellum.",
            "camera": "Dramatic focus on the midline frontal brain structure.",
            "narration": "Breaking this paralysis requires understanding the anterior mid-cingulate cortex, or aMCC. Neuroscientists consider this brain region the central engine of human tenacity. Research shows the aMCC expands in volume only when you engage in effortful resistance, choosing to push through friction on tasks you genuinely do not feel like doing in the moment.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Empowering, rigorous, neuroplastic",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC08_I1", "Detailed anatomical drawing of the human brain with the anterior mid-cingulate cortex (aMCC) illuminated in bright gold ink #E88D2A on textured paper #F8F0DC.", "fast", "macro_detail"),
                ("SC08_I2", "The aMCC depicted as a sturdy brass steam engine piston turning a heavy iron flywheel inside the forehead on textured cream paper #F8F0DC, technical drafting style.", "normal", "concept_metaphor"),
                ("SC08_I3", "Side-by-side growth comparison of a neural structure before and after effortful resistance, with dendrites branching out like spring tree buds on rag paper #F8F0DC.", "slow", "concept_metaphor"),
                ("SC08_I4", "Stickman in cobalt t-shirt leaning their shoulder against a heavy boulder labeled 'reluctant friction' on textured paper #F8F0DC, 2B pencil lines.", "normal", "full_scene"),
                ("SC08_I5", "Close-up of stickman's determined eye with subtle golden sparks igniting in the iris as effort begins on textured cotton paper #F8F0DC, dip-pen ink.", "fast", "macro_detail"),
                ("SC08_I6", "Stickman standing tall atop a small conquered hill of crumpled draft papers with a glowing halo around their prefrontal cortex on cream paper #F8F0DC.", "hold", "full_scene"),
            ],
            "quotes": [
                "Breaking this paralysis requires understanding the anterior mid-cingulate cortex, or aMCC.",
                "Neuroscientists consider this brain region the central engine of human tenacity.",
                "Research shows the aMCC expands in volume",
                "only when you engage in effortful resistance,",
                "choosing to push through friction",
                "on tasks you genuinely do not feel like doing in the moment.",
            ],
        },
        # SC09
        {
            "id": "SC09",
            "title": "The 90-Second Ugly Draft",
            "purpose": "Walk through the 90-second ugly draft protocol step-by-step.",
            "action": "Stickman scribbling intentionally messy words on rough scratch paper.",
            "setting": "Cluttered artist's worktable with scrap sheets and fountain pens.",
            "camera": "Over-the-shoulder close shot following the pen nib.",
            "narration": "To disarm the threat tag, apply the ninety-second ugly draft protocol. Give yourself permission to write the worst, most embarrassing response possible on scrap paper. By explicitly lowering the stakes to zero, you bypass the amygdala's alarm bells. Once three terrible sentences exist on the page, the task shifts from abstract danger to mechanical editing.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Practical, liberating, tactical",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "actionable_resolution",
            "prompts": [
                ("SC09_I1", "Stickman gleefully pulling out a scrap piece of torn brown butcher paper with a fountain pen on textured rag paper #F8F0DC, cobalt and amber accents.", "burst", "full_scene"),
                ("SC09_I2", "Extreme close-up of a fountain pen scratching messy, misspelled, unpolished words onto lined yellow paper on textured vellum #F8F0DC, visible ink splatters.", "fast", "macro_detail"),
                ("SC09_I3", "The red threat alarm bell over the amygdala shutting down with a satisfying mechanical click and tiny puff of smoke on cream paper #F8F0DC.", "normal", "concept_metaphor"),
                ("SC09_I4", "The saber-toothed tiger from earlier deflating into a tiny, harmless purring kitten on the corner of the desk on textured paper #F8F0DC, sage wash #93A88C.", "normal", "concept_metaphor"),
                ("SC09_I5", "Three rough handwritten sentences sitting on paper, surrounded by calm blue pencil correction marks #3B82C4 on textured cotton paper #F8F0DC.", "fast", "macro_detail"),
                ("SC09_I6", "Stickman calmly holding a red editor's pencil, comfortably reshaping the sentences with a relaxed smile on textured rag paper #F8F0DC, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "To disarm the threat tag, apply the ninety-second ugly draft protocol.",
                "Give yourself permission to write the worst, most embarrassing response possible on scrap paper.",
                "By explicitly lowering the stakes to zero,",
                "you bypass the amygdala's alarm bells.",
                "Once three terrible sentences exist on the page,",
                "the task shifts from abstract danger to mechanical editing.",
            ],
        },
        # SC10
        {
            "id": "SC10",
            "title": "Action Precedes Motivation",
            "purpose": "Editorial verdict that action must precede emotional readiness.",
            "action": "Stickman stepping forward into fog, which instantly dissolves into clarity.",
            "setting": "Minimalist misty landscape transforming into clear sunlight.",
            "camera": "Expansive cinematic wide shot on cream Moleskine canvas.",
            "narration": "Stop waiting to feel inspired before you open the draft. Action precedes emotional readiness, never the other way around. Waiting for calm motivation simply surrenders your afternoon to primitive fear circuits. When you lean into the friction for ninety seconds, your brain realizes the threat was imaginary, and the heavy mental fog lifts almost immediately.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Decisive, philosophical, motivating",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "editorial_commentary",
            "prompts": [
                ("SC10_I1", "Stickman sitting patiently on a park bench watching calendar pages blow away in autumn wind on textured rag paper #F8F0DC, muted sepia wash.", "slow", "full_scene"),
                ("SC10_I2", "A bold equation hand-lettered in black dip-pen ink across the page: 'ACTION -> EMOTION (NOT EMOTION -> ACTION)' on textured cream paper #F8F0DC.", "normal", "concept_metaphor"),
                ("SC10_I3", "Primitive stone monster representing ancient fear circuits crumbling as a small wooden stickman calmly walks straight past it on rag paper #F8F0DC.", "slow", "full_scene"),
                ("SC10_I4", "Stickman taking a single deliberate step forward into a dense gray graphite fog on textured paper #F8F0DC, cobalt t-shirt #3B82C4 standing out sharply.", "normal", "full_scene"),
                ("SC10_I5", "The gray pencil fog evaporating into radiant clear space as warm amber watercolor wash #E88D2A illuminates the horizon on cream paper #F8F0DC.", "slow", "environment"),
                ("SC10_I6", "Stickman standing tall with chest open and relaxed posture at an organized clean desk, breathing easily on textured cotton paper #F8F0DC, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Stop waiting to feel inspired before you open the draft.",
                "Action precedes emotional readiness, never the other way around.",
                "Waiting for calm motivation simply surrenders your afternoon to primitive fear circuits.",
                "When you lean into the friction for ninety seconds,",
                "your brain realizes the threat was imaginary,",
                "and the heavy mental fog lifts almost immediately.",
            ],
        },
        # SC11
        {
            "id": "SC11",
            "title": "Closing Synthesis & The Tenacity Muscle",
            "purpose": "Consolidate daily habit rule and invite thoughtful community engagement.",
            "action": "Stickman closing notebook with satisfied nod as channel endcard visual establishes.",
            "setting": "Clean, bright studio desk with morning light.",
            "camera": "Warm concluding medium shot pulling back to reveal sketchbook borders.",
            "narration": "Every time you execute a tiny friction-heavy action, you physically reinforce your brain's tenacity engine. The next time an unwritten message freezes your day, remember your biology is merely running an outdated survival script. Disarm the loop with an intentionally ugly draft. Try the ninety-second protocol today, and tell us below what shifted for your focus.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Warm, inspiring, grounded",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cta_close",
            "prompts": [
                ("SC11_I1", "Stickman gently touching forehead with one finger as a small golden neuron star pulses with healthy neural branches on textured cotton rag paper #F8F0DC.", "normal", "macro_detail"),
                ("SC11_I2", "Vintage blueprint drawing of the brain showing reinforced structural beams strengthening the frontal cortex on cream paper #F8F0DC, technical blue ink #3B82C4.", "normal", "concept_metaphor"),
                ("SC11_I3", "An old computer monitor displaying an 'OVERRIDE SURVIVAL SCRIPT' command with a green checkmark on textured rag paper #F8F0DC, dry sage wash #93A88C.", "slow", "concept_metaphor"),
                ("SC11_I4", "Stickman smiling comfortably while dropping a stamped envelope into a vintage mailbox on the street on cream paper #F8F0DC, crisp dip-pen outlines.", "slow", "full_scene"),
                ("SC11_I5", "Stickman closing a leather-bound sketchbook with a gentle satisfied smile under soft warm lamp light on textured paper #F8F0DC, >=60% negative space.", "hold", "full_scene"),
                ("SC11_I6", "Editorial channel endcard on textured cream rag paper #F8F0DC with stickman waving friendly from the corner and hand-lettered text in upper third: 'LAZY BRAIN LAB'.", "hold", "full_scene", True),
            ],
            "quotes": [
                "Every time you execute a tiny friction-heavy action,",
                "you physically reinforce your brain's tenacity engine.",
                "The next time an unwritten message freezes your day,",
                "remember your biology is merely running an outdated survival script.",
                "Disarm the loop with an intentionally ugly draft.",
                "Try the ninety-second protocol today, and tell us below what shifted for your focus.",
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
                preserve="Hand-inked 2D indie sketchbook aesthetic, textured warm cotton rag paper #F8F0DC, cobalt-blue t-shirt stickman #3B82C4, dip-pen black ink outlines #000000.",
                change=f"Progress to beat {p_id} showing {desc[:60]}...",
                reason=f"Visualize narrative progression for {sc_id} beat {i+1}.",
                tempo=tempo,
                situation=sc_data["narrative_situation"],
                motion_prompt="Smooth 2D indie animation. Hand-drawn ink lines shift gently on textured cotton paper, subtle micro-movement in characters, zero lip-sync, calm organic visual transitions.",
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
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "You have been staring at an unfinished three-sentence email for four hours."},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Your body did not expend physical energy today; your prefrontal cortex was hijacked by a false biological alarm."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Hidden deep inside your temporal lobe sits the amygdala, your brain's ancient threat radar."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Ambiguity triggers a micro-dose of adrenaline and cortisol. Your rational prefrontal circuits lock up in freeze mode."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Leaving the email unwritten creates what cognitive psychologists call an open cognitive loop."},
            {"requirement_id": "R06", "scene_id": "SC06", "quote": "This is why conventional productivity advice completely fails."},
            {"requirement_id": "R07", "scene_id": "SC07", "quote": "Your prefrontal cortex consumes roughly twenty percent of total resting energy despite accounting for only two percent of your body mass."},
            {"requirement_id": "R08", "scene_id": "SC08", "quote": "Breaking this paralysis requires understanding the anterior mid-cingulate cortex, or aMCC."},
            {"requirement_id": "R09", "scene_id": "SC09", "quote": "To disarm the threat tag, apply the ninety-second ugly draft protocol."},
            {"requirement_id": "R10", "scene_id": "SC10", "quote": "Stop waiting to feel inspired before you open the draft. Action precedes emotional readiness, never the other way around."},
            {"requirement_id": "R11", "scene_id": "SC11", "quote": "Every time you execute a tiny friction-heavy action, you physically reinforce your brain's tenacity engine."},
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC03",
                "quote": "The trouble is, your amygdala cannot tell the difference between a hungry saber-toothed cat and an ambiguous email from your supervisor asking to speak tomorrow morning.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "The amygdala tags ambiguous social evaluation as an acute survival threat.",
            },
            {
                "scene_id": "SC05",
                "quote": "Bluma Zeigarnik discovered a century ago that uncompleted tasks refuse to leave working memory.",
                "language": "en",
                "source_id": "SRC02",
                "fact": "Uncompleted tasks remain active in working memory, consuming continuous cognitive bandwidth.",
            },
            {
                "scene_id": "SC08",
                "quote": "Research shows the aMCC expands in volume only when you engage in effortful resistance, choosing to push through friction on tasks you genuinely do not feel like doing in the moment.",
                "language": "en",
                "source_id": "SRC03",
                "fact": "The anterior mid-cingulate cortex increases in volume through voluntary effort against friction.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    return job_id, brief, outline, competitor_research, content


def build_lazy_brain_short() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_lazy_brain"
    slug = "en-lazy-brain"
    parent_long_id = f"{slug}-batch1-16x9"
    job_id = f"{slug}-batch1-9x16"
    ch = get_channel(channel_id)

    topic = "Task Paralysis Is Not Laziness: How Open Loops and Amygdala Threat Tagging Drain Your Prefrontal Cortex"
    youtube_title = "Why Answering One Email Exhausts Your Brain"

    brief: Dict[str, Any] = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Deliver a fast-paced 45s deconstruction of task paralysis, explaining amygdala threat tagging and the 90-second ugly draft antidote.",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 38.0,
            "max_seconds": 52.0,
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Staring at a short email for hours is physiological freeze, not moral laziness."},
            {"id": "R02", "text": "The amygdala treats ambiguous social evaluation as an apex predator threat."},
            {"id": "R03", "text": "Uncompleted tasks lock working memory in an open loop that burns mental battery."},
            {"id": "R04", "text": "The 90-second ugly draft protocol disarms threat evaluation by dropping stakes to zero."},
            {"id": "R05", "text": "Cliffhanger peak on the anterior mid-cingulate cortex and channel bridge."},
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
                "title": "Neural Mechanisms of Procrastination and Amygdala Threat Evaluation",
                "reference": "Zhang, S. et al. (2021). Journal of Cognitive Neuroscience, 33(5), 890-904.",
                "facts": [
                    "The amygdala tags ambiguous social evaluation as an acute survival threat.",
                    "Threat-tagging inhibits dorsolateral prefrontal cortex executive functioning.",
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
                "Hook audience in under 3 seconds with the relatable agony of email avoidance.",
                "Debunk willpower guilt and demonstrate the 90-second ugly draft mechanism.",
                "Bridge smoothly to the long video right at the peak cliffhanger.",
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "None required.",
            "pacing": "Rapid-fire, punchy spoken rhythm with zero hesitation.",
            "assumptions": [
                "Each beat changes image every 2.0 to 2.4 seconds.",
            ],
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Stickman staring paralyzed at giant email icon with glowing amber teeth on cream vertical paper",
                "text_overlay": "EMAIL FREEZE",
                "contrast_pair": "Lazy mindset myth vs Amygdala freeze reality",
                "thumbnail_prompt": "Hand-inked 2D indie vertical sketchbook illustration on textured warm cotton rag paper (#F8F0DC). Cobalt-shirt (#3B82C4) stickman frozen in shock as a gigantic white email envelope grows sharp ink jaws and amber (#E88D2A) alarm sparks. Dip-pen pitch-black outline (#000000), visible 2B pencil marks. Bold hand-lettered text in upper third: 'EMAIL FREEZE'. Vertical 9:16, >=60% negative space, zero 3D CGI.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Neuroscience of Focus & Behavioral Friction",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["lazy brain lab", "shorts", "neuroscience", "procrastination", "brain hacks"],
            "parent_long_id": parent_long_id,
            "cta_plan": {
                "cliffhanger_peak": "How does micro-friction physically rewire your anterior mid-cingulate cortex to stop future paralysis?",
                "bridge": "Watch the complete neuroscience breakdown on Lazy Brain Lab YouTube.",
                "close": "Try the ninety-second ugly draft today and notice what shifts.",
                "endcard_text": "FULL VIDEO ON YOUTUBE",
            },
            "editorial_stance": {
                "myth_debunked": "Procrastination on critical tasks stems from moral laziness, defective willpower, or poor time management.",
                "why_generic_advice_fails": "Telling people to push through or shame themselves triggers additional amygdala panic, worsening the physiological freeze response.",
                "channel_verdict": "Task paralysis is an involuntary biological defense mechanism against perceived social ambiguity, not a character flaw.",
                "tradeoff_or_blindspot": "Lowering your standards to write an intentionally terrible first draft feels counterintuitive, but it is the only way to disarm threat tagging.",
            },
            "actionable_value": {
                "core_mechanism": "Ambiguity triggers amygdala threat-tagging, locking the prefrontal cortex until an open cognitive loop is mechanically closed.",
                "practical_rule_of_thumb": "Lower the threshold to zero with a ninety-second ugly draft on scrap paper.",
                "real_world_scenario": "When frozen by an intimidating email from your boss, write the worst possible three-sentence draft immediately.",
            },
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Stickman staring paralyzed at giant email icon with glowing amber teeth on cream vertical paper",
            "text_overlay": "EMAIL FREEZE",
            "contrast_pair": "Lazy mindset myth vs Amygdala freeze reality",
            "thumbnail_prompt": "Hand-inked 2D indie vertical sketchbook illustration on textured warm cotton rag paper (#F8F0DC). Cobalt-shirt (#3B82C4) stickman frozen in shock as a gigantic white email envelope grows sharp ink jaws and amber (#E88D2A) alarm sparks. Dip-pen pitch-black outline (#000000), visible 2B pencil marks. Bold hand-lettered text in upper third: 'EMAIL FREEZE'. Vertical 9:16, >=60% negative space, zero 3D CGI.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Neuroscience of Focus & Behavioral Friction",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["lazy brain lab", "shorts", "neuroscience", "procrastination", "brain hacks"],
        "parent_long_id": parent_long_id,
        "cta_plan": {
            "cliffhanger_peak": "How does micro-friction physically rewire your anterior mid-cingulate cortex to stop future paralysis?",
            "bridge": "Watch the complete neuroscience breakdown on Lazy Brain Lab YouTube.",
            "close": "Try the ninety-second ugly draft today and notice what shifts.",
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
            "myth_debunked": "Procrastination on critical tasks stems from moral laziness, defective willpower, or poor time management.",
            "why_generic_advice_fails": "Telling people to push through or shame themselves triggers additional amygdala panic, worsening the physiological freeze response.",
            "channel_verdict": "Task paralysis is an involuntary biological defense mechanism against perceived social ambiguity, not a character flaw.",
            "tradeoff_or_blindspot": "Lowering your standards to write an intentionally terrible first draft feels counterintuitive, but it is the only way to disarm threat tagging.",
        },
        "actionable_value": {
            "core_mechanism": "Ambiguity triggers amygdala threat-tagging, locking the prefrontal cortex until an open cognitive loop is mechanically closed.",
            "practical_rule_of_thumb": "Lower the threshold to zero with a ninety-second ugly draft on scrap paper.",
            "real_world_scenario": "When frozen by an intimidating email from your boss, write the worst possible three-sentence draft immediately.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook on the 4-hour paralysis over a 3-sentence reply.", "requirements": ["R01"], "transition": "Reveal the biological root in the amygdala."},
            {"scene_id": "SC02", "purpose": "Explain amygdala threat evaluation treating emails as physical predators.", "requirements": ["R02"], "transition": "Deconstruct open loops and mental RAM."},
            {"scene_id": "SC03", "purpose": "Editorial commentary on the futility of willpower shaming.", "requirements": ["R03"], "transition": "Provide the 90-second unlock."},
            {"scene_id": "SC04", "purpose": "Deliver the 90-second ugly draft protocol.", "requirements": ["R04"], "transition": "Peak twist on brain neuroplasticity and bridge."},
            {"scene_id": "SC05", "purpose": "Climax on the aMCC, channel bridge, and closing CTA.", "requirements": ["R05"], "transition": "End of short."},
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "Psych2Go Shorts",
                    "top_performing_videos": [
                        {
                            "title": "Why You Freeze When You Have Too Much To Do",
                            "views": "2.4M views",
                            "hook_technique": "Direct relatable question confronting viewers' secret avoidance habits.",
                            "pacing_structure": "Callout -> Psychological mechanism -> Calming reframe.",
                            "retention_driver": "High empathy combined with minimalist visual doodles.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Validates the viewer's hidden shame immediately in the opening 2 seconds.",
                        "Uses simple stickman visual cues to illustrate emotional overwhelm.",
                    ],
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 19,
                "zero_pause_opening_seconds": 11,
                "visual_contrast": "Stickman cowering before an intimidating glowing email envelope.",
                "counter_intuitive_truth_slap": "You are not lazy; your prefrontal cortex is frozen by an ancient predator alert system.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Opening hook confronting the 4-hour email paralysis."},
                {"phase": "empirical_conflict", "purpose": "Amygdala threat tagging mistaking text for an apex predator."},
                {"phase": "structural_model", "purpose": "Working memory open loop draining mental stamina."},
                {"phase": "actionable_resolution", "purpose": "The 90-second ugly draft protocol disarming alarm circuits."},
                {"phase": "cliffhanger_spinoff", "purpose": "Peak twist on the aMCC tenacity muscle and channel bridge."},
            ],
            "tactile_visual_benchmark": {
                "paper_surface": "Textured warm cotton rag paper (#F8F0DC deckle-edge paper grain).",
                "ink_technique": "Dip-pen Sumi-e black ink outlines (#000000) with visible graphite pencil marks.",
                "palette_application": "Matte mineral washes: cobalt blue (#3B82C4), dopamine-amber (#E88D2A), dry sage (#93A88C).",
                "anti_ai_rules": "Vertical 9:16, zero 3D CGI, zero neon glow, minimum 60% negative space.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Neuroscience of Focus & Behavioral Friction",
            "myth_debunked": "Procrastination on critical tasks stems from moral laziness, defective willpower, or poor time management.",
            "channel_verdict": "Task paralysis is an involuntary biological defense mechanism against perceived social ambiguity, not a character flaw.",
            "actionable_rule_of_thumb": "Lower the threshold to zero with a ninety-second ugly draft on scrap paper.",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "How does micro-friction physically rewire your anterior mid-cingulate cortex to stop future paralysis?",
            "bridge": "Watch the complete neuroscience breakdown on Lazy Brain Lab YouTube.",
            "close": "Try the ninety-second ugly draft today and notice what shifts.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
    }

    # 5 scenes, 4 beats & 4 images each = 20 images, 176 words
    scenes_data = [
        # SC01
        {
            "id": "SC01",
            "title": "The Four-Hour Stare",
            "purpose": "Hook on the 4-hour paralysis over a 3-sentence reply.",
            "action": "Stickman in cobalt t-shirt staring in shock at blinking cursor.",
            "setting": "Raw sketchbook study desk on vertical cream paper.",
            "camera": "Vertical medium close-up.",
            "narration": "Staring at a three-sentence email for four long hours is not laziness. The blinking cursor triggers actual physical panic in your chest, draining your daily stamina before you even type the opening greeting.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Electrifying, relatable, validating",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "prompts": [
                ("SC01_I1", "Vertical 9:16 indie sketchbook illustration on warm rag paper #F8F0DC: stickman in cobalt t-shirt #3B82C4 paralyzed before an empty laptop screen, visible 2B graphite marks, dip-pen ink.", "burst", "full_scene"),
                ("SC01_I2", "Vertical close-up of a wall clock spinning crazily past four hours while stickman sits motionless, warm cotton paper #F8F0DC, charcoal linework.", "fast", "macro_detail"),
                ("SC01_I3", "Stickman clutching chest as radiating graphite tension waves pulse outward against an oversized red blinking cursor, textured paper #F8F0DC.", "fast", "concept_metaphor"),
                ("SC01_I4", "Stickman slumping down into desk chair as energy visibly evaporates like smoke plumes, cream cotton paper #F8F0DC, >=60% negative space.", "normal", "full_scene"),
            ],
            "quotes": [
                "Staring at a three-sentence email for four long hours",
                "is not laziness.",
                "The blinking cursor triggers actual physical panic in your chest,",
                "draining your daily stamina before you even type the opening greeting.",
            ],
        },
        # SC02
        {
            "id": "SC02",
            "title": "The Predator in the Inbox",
            "purpose": "Explain amygdala threat evaluation treating emails as physical predators.",
            "action": "The amygdala lighting up as email icon transforms into a tiger silhouette.",
            "setting": "Abstract anatomical and savanna sketch on vertical paper.",
            "camera": "Vertical split comparative angle.",
            "narration": "Your ancient amygdala cannot distinguish between an ambiguous email and a predator in the bushes. It flags the social uncertainty as life-threatening danger, locking your prefrontal cortex into complete biological freeze mode.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Eye-opening, neuroscientific",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC02_I1", "Vertical anatomical sketch of brain with the almond-shaped amygdala pulsing with red dip-pen ink on warm cotton paper #F8F0DC, technical margin annotations.", "fast", "macro_detail"),
                ("SC02_I2", "A shadowy ink-wash saber-toothed tiger silhouette emerging directly out of a glowing desktop inbox window on textured vellum #F8F0DC.", "normal", "concept_metaphor"),
                ("SC02_I3", "Red exclamation hazard signs stamped across neural axons as adrenaline droplets fall on cream paper #F8F0DC, amber wash #E88D2A.", "normal", "concept_metaphor"),
                ("SC02_I4", "Stickman frozen in a solid block of ice resembling a glass specimen jar while staring forward on textured rag paper #F8F0DC.", "hold", "full_scene"),
            ],
            "quotes": [
                "Your ancient amygdala cannot distinguish between an ambiguous email",
                "and a predator in the bushes.",
                "It flags the social uncertainty as life-threatening danger,",
                "locking your prefrontal cortex into complete biological freeze mode.",
            ],
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Working Memory Leak",
            "purpose": "Editorial commentary on the futility of willpower shaming.",
            "action": "A battery leaking fluid while self-help books crumble.",
            "setting": "Minimalist sketchbook canvas with dark ink accents.",
            "camera": "Direct vertical perspective.",
            "narration": "Unwritten tasks linger as open loops, burning your brain's precious working memory all day. Shaming yourself for lack of willpower fails because you are fighting a primitive biological alarm system, not bad personal discipline.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Sharp, compassionate, liberating",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "prompts": [
                ("SC03_I1", "Vertical sketch of an endless spinning loading loop hovering above stickman's head, glowing in cobalt blue #3B82C4 on warm cotton rag paper #F8F0DC.", "slow", "concept_metaphor"),
                ("SC03_I2", "A transparent human silhouette showing a glowing prefrontal battery draining rapidly into empty red levels on cream paper #F8F0DC.", "normal", "concept_metaphor"),
                ("SC03_I3", "Motivational hustle posters cracking and tearing into dust as stickman brushes them aside on textured paper #F8F0DC, charcoal hatching.", "slow", "full_scene"),
                ("SC03_I4", "An ancient biological alarm bell clapper ringing wildly inside a glass jar, demonstrating involuntary survival reflex on rag paper #F8F0DC.", "hold", "macro_detail"),
            ],
            "quotes": [
                "Unwritten tasks linger as open loops,",
                "burning your brain's precious working memory all day.",
                "Shaming yourself for lack of willpower fails",
                "because you are fighting a primitive biological alarm system, not bad personal discipline.",
            ],
        },
        # SC04
        {
            "id": "SC04",
            "title": "The 90-Second Antidote",
            "purpose": "Deliver the 90-second ugly draft protocol.",
            "action": "Stickman hurriedly writing scribbles on scrap paper with a smile.",
            "setting": "Art studio desk with rough paper scraps.",
            "camera": "Vertical over-the-table macro shot.",
            "narration": "Shut off the threat tag with a rapid ninety-second rough scribble on scrap paper. Give yourself permission to write the worst possible response on purpose. Zero stakes disarm the amygdala, turning impossible paralysis into simple editing.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Empowering, tactical, actionable",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "actionable_resolution",
            "prompts": [
                ("SC04_I1", "Stickman eagerly grabbing a piece of torn brown scrap paper with a fountain pen on vertical cream paper #F8F0DC, energetic dip-pen lines.", "burst", "full_scene"),
                ("SC04_I2", "Macro vertical shot of messy, crooked ink words crossing the page under a handwritten label reading 'UGLY DRAFT' on textured rag paper #F8F0DC.", "fast", "macro_detail"),
                ("SC04_I3", "The red threat alarm over the amygdala dissolving into serene blue water droplets on textured cotton vellum #F8F0DC, cobalt wash #3B82C4.", "normal", "concept_metaphor"),
                ("SC04_I4", "Stickman holding a blue editing pencil, casually crossing out a messy word with a relaxed confident smile on warm paper #F8F0DC, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Shut off the threat tag with a rapid ninety-second rough scribble on scrap paper.",
                "Give yourself permission to write the worst possible response on purpose.",
                "Zero stakes disarm the amygdala,",
                "turning impossible paralysis into simple editing.",
            ],
        },
        # SC05
        {
            "id": "SC05",
            "title": "Tenacity & The Bridge",
            "purpose": "Climax on the aMCC, channel bridge, and closing CTA.",
            "action": "Golden neuron expanding, leading into channel endcard.",
            "setting": "Luminous clean vertical sketchbook canvas.",
            "camera": "Vertical upward tilt into final visual bridge.",
            "narration": "How does micro-friction physically rewire your anterior mid-cingulate cortex to stop future paralysis? Watch the complete neuroscience breakdown on Lazy Brain Lab YouTube. Try the ninety-second ugly draft today and notice what shifts.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Magnetic, curious, inviting",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cta_close",
            "prompts": [
                ("SC05_I1", "Vertical anatomical sketch of anterior mid-cingulate cortex (aMCC) glowing like a radiant golden star #E88D2A inside the midline frontal cortex on textured rag paper #F8F0DC.", "normal", "macro_detail"),
                ("SC05_I2", "Stickman stepping confidently over a tiny obstacle labeled '90-second resistance' as golden light beams radiate from within on cream paper #F8F0DC.", "slow", "full_scene"),
                ("SC05_I3", "A clean hand-drawn video player card pointing toward the full explainer with stickman holding an ink pen on textured paper #F8F0DC, cobalt blue wash #3B82C4.", "hold", "full_scene"),
                ("SC05_I4", "Vertical channel endcard on textured cream cotton rag paper #F8F0DC with stickman waving happily and hand-lettered uppercase text in upper third: 'LAZY BRAIN LAB'.", "hold", "full_scene", True),
            ],
            "quotes": [
                "How does micro-friction physically rewire your anterior mid-cingulate cortex",
                "to stop future paralysis?",
                "Watch the complete neuroscience breakdown on Lazy Brain Lab YouTube.",
                "Try the ninety-second ugly draft today and notice what shifts.",
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
                preserve="Hand-inked 2D indie sketchbook aesthetic, textured warm cotton rag paper #F8F0DC, cobalt-blue t-shirt stickman #3B82C4, dip-pen black ink outlines #000000.",
                change=f"Progress to beat {p_id} showing {desc[:60]}...",
                reason=f"Visualize narrative progression for {sc_id} beat {i+1}.",
                tempo=tempo,
                situation=sc_data["narrative_situation"],
                motion_prompt="Smooth 2D indie animation. Hand-drawn ink lines shift gently on textured cotton paper, subtle micro-movement in characters, zero lip-sync, calm organic visual transitions.",
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
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "Staring at a three-sentence email for four long hours is not laziness."},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Your ancient amygdala cannot distinguish between an ambiguous email and a predator in the bushes."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Unwritten tasks linger as open loops, burning your brain's precious working memory all day."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Shut off the threat tag with a rapid ninety-second rough scribble on scrap paper."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Watch the complete neuroscience breakdown on Lazy Brain Lab YouTube."},
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC02",
                "quote": "It flags the social uncertainty as life-threatening danger, locking your prefrontal cortex in complete freeze mode.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "The amygdala tags ambiguous social evaluation as an acute survival threat.",
            }
        ],
        "revision_response": [],
        "open_questions": [],
    }

    return job_id, brief, outline, competitor_research, content
