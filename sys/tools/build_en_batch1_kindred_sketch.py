#!/usr/bin/env python3
"""Data generator for en_kindred_sketch (Kindred Sketch) Schema 3.0 packages.

Storytelling Ref: The School of Life, Cinema Therapy, Esther Perel
Visual Ref: Warm Charcoal & Loose Botanical Watercolor Journal (#F7F0E4 cold-press
watercolor paper, soft charcoal lines, #D97A54 terracotta & #5D8A72 sage washes)
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


def build_kindred_sketch_long() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_kindred_sketch"
    slug = "en-kindred-sketch"
    job_id = f"{slug}-batch1-16x9"
    ch = get_channel(channel_id)

    topic = "The Anxious-Avoidant Trap: Why One Partner Pursues Harder While the Other Stonewalls—And How to Break It"
    youtube_title = "Why One Partner Pursues While the Other Shuts Down"

    brief: Dict[str, Any] = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Deconstruct the anxious-avoidant cycle through Gottman's physiological arousal research, explain stonewalling as a nervous system overload, and teach the 20-minute timed return contract.",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 150.0,
            "max_seconds": 210.0,
        },
        "scene_count": 11,
        "required_points": [
            {"id": "R01", "text": "The tense kitchen-table silence where one asks what is wrong and the other shuts down."},
            {"id": "R02", "text": "The escalation reflex: the pursuer talks faster while the distancer withdraws deeper."},
            {"id": "R03", "text": "Gottman's Love Lab finding that stonewallers experience heart rates over 100 BPM."},
            {"id": "R04", "text": "Stonewalling as an involuntary autonomic survival shutdown rather than cold malice."},
            {"id": "R05", "text": "Why withdrawal triggers primal abandonment alarms in the anxious attachment brain."},
            {"id": "R06", "text": "Editorial commentary on why conventional advice to just talk it out fails during flooding."},
            {"id": "R07", "text": "The tragic polarized dance where both partners fear the exact same outcome of losing love."},
            {"id": "R08", "text": "The 20-minute biological requirement to metabolize cortisol and clear physiological arousal."},
            {"id": "R09", "text": "The twenty-minute timed return contract with an explicit timestamp commitment."},
            {"id": "R10", "text": "Editorial verdict that true intimacy is measured by the predictable certainty of repair."},
            {"id": "R11", "text": "Closing synthesis, respectful boundaries, and compassionate community invitation."},
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
                "title": "The Physiological Correlates of Marital Conflict: Diffuse Physiological Arousal and Stonewalling",
                "reference": "Gottman, J. M., & Levenson, R. W. (1988). Journal of Personality and Social Psychology, 54(5), 890-900.",
                "facts": [
                    "Stonewalling occurs when heart rate surpasses one hundred beats per minute during marital dispute.",
                    "Diffuse physiological arousal shuts down cognitive capacity for empathy and active listening.",
                ],
            },
            {
                "id": "SRC02",
                "title": "Attachment in Adulthood: Structure, Dynamics, and Change",
                "reference": "Mikulincer, M., & Shaver, P. R. (2016). Guilford Press.",
                "facts": [
                    "Perceived emotional withdrawal triggers biological attachment panic in anxiously attached partners.",
                    "Avoidant strategies represent protective deactivating responses to emotional overwhelm.",
                ],
            },
            {
                "id": "SRC03",
                "title": "Autonomic Recovery Dynamics Following Interpersonal Conflict",
                "reference": "Levenson, R. W. et al. (2014). Emotion Review, 6(4), 312-320.",
                "facts": [
                    "The human nervous system requires at least twenty minutes of emotional safety to metabolize stress hormones.",
                    "Premature re-engagement during physiological flooding prolongs autonomic arousal.",
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
                "Remove moral condemnation from both pursuer and distancer through autonomic physiology.",
                "Visually depict Gottman's 100+ BPM discovery using warm charcoal and watercolor vignettes.",
                "Equip couples with the 20-minute timed return contract to eliminate abandonment panic.",
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "Basic experience with romantic or interpersonal conflict.",
            "pacing": "Gentle, emotionally literate, steady spoken cadence at 3.8 words per second.",
            "assumptions": [
                "11 scenes with 6 beats and 6 unique images each, cold-press rag paper grain #F7F0E4.",
            ],
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Leo turning away with arms crossed as a red heartbeat line spikes over 100 BPM while Maya reaches forward with pleading eyes",
                "text_overlay": "WHY THEY SHUT DOWN",
                "contrast_pair": "Loud desperate pursuit vs Silent internal 100 BPM flooding",
                "thumbnail_prompt": "Warm charcoal-pencil and loose botanical watercolor illustration on cold-press rag paper (#F7F0E4). Maya in terracotta (#D97A54) cardigan reaching outward with expressive charcoal eyes, while Leo in sage-green (#5D8A72) sweater turns slightly away with a spiking red pulse line reading '100+ BPM' sketched between them. Soft raw umber (#5B4636) pencil lines, visible paper bleed, >=60% negative space, uppercase hand-lettered text: 'WHY THEY SHUT DOWN'. Orthographic 2D, zero 3D CGI, zero plastic sheen.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Attachment Science & Emotional Repair",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["kindred sketch", "stonewalling", "anxious avoidant trap", "gottman method", "attachment theory", "relationships"],
            "cta_plan": {
                "close": "Share gently below what patterns you recognize in your connections.",
                "endcard_text": "FULL VIDEO ON KINDRED SKETCH",
            },
            "editorial_stance": {
                "myth_debunked": "The silent partner in a heated argument is indifferent and manipulative, while the pursuing partner is just controlling.",
                "why_generic_advice_fails": "Demanding open communication while partners are physiologically flooded forces an overwhelmed nervous system into deeper defensive survival mode.",
                "channel_verdict": "Stonewalling and pursuing are mirror-image biological survival reflexes protecting against the identical terror of relational loss.",
                "tradeoff_or_blindspot": "Walking away for twenty minutes requires immense restraint from the pursuer, but it is necessary to restore neurological empathy.",
            },
            "actionable_value": {
                "core_mechanism": "Autonomic flooding above one hundred beats per minute blinds emotional processing, turning conversation into perceived threat.",
                "practical_rule_of_thumb": "Agree on a twenty-minute timed return contract with an exact timestamp before disengaging.",
                "real_world_scenario": "When conflict escalates over dinner, state a specific twenty-minute return time rather than storming out silently.",
            },
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Leo turning away with arms crossed as a red heartbeat line spikes over 100 BPM while Maya reaches forward with pleading eyes",
            "text_overlay": "WHY THEY SHUT DOWN",
            "contrast_pair": "Loud desperate pursuit vs Silent internal 100 BPM flooding",
            "thumbnail_prompt": "Warm charcoal-pencil and loose botanical watercolor illustration on cold-press rag paper (#F7F0E4). Maya in terracotta (#D97A54) cardigan reaching outward with expressive charcoal eyes, while Leo in sage-green (#5D8A72) sweater turns slightly away with a spiking red pulse line reading '100+ BPM' sketched between them. Soft raw umber (#5B4636) pencil lines, visible paper bleed, >=60% negative space, uppercase hand-lettered text: 'WHY THEY SHUT DOWN'. Orthographic 2D, zero 3D CGI, zero plastic sheen.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Attachment Science & Emotional Repair",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["kindred sketch", "stonewalling", "anxious avoidant trap", "gottman method", "attachment theory", "relationships"],
        "cta_plan": {
            "close": "Share gently below what patterns you recognize in your connections.",
            "endcard_text": "FULL VIDEO ON KINDRED SKETCH",
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
            "myth_debunked": "The silent partner in a heated argument is indifferent and manipulative, while the pursuing partner is just controlling.",
            "why_generic_advice_fails": "Demanding open communication while partners are physiologically flooded forces an overwhelmed nervous system into deeper defensive survival mode.",
            "channel_verdict": "Stonewalling and pursuing are mirror-image biological survival reflexes protecting against the identical terror of relational loss.",
            "tradeoff_or_blindspot": "Walking away for twenty minutes requires immense restraint from the pursuer, but it is necessary to restore neurological empathy.",
        },
        "actionable_value": {
            "core_mechanism": "Autonomic flooding above one hundred beats per minute blinds emotional processing, turning conversation into perceived threat.",
            "practical_rule_of_thumb": "Agree on a twenty-minute timed return contract with an exact timestamp before disengaging.",
            "real_world_scenario": "When conflict escalates over dinner, state a specific twenty-minute return time rather than storming out silently.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Depict the painful kitchen-table shutdown over cold tea.", "requirements": ["R01"], "transition": "Transition into the escalating pursuit dynamic."},
            {"scene_id": "SC02", "purpose": "Examine the pursuer's desperation versus the distancer's wall.", "requirements": ["R02"], "transition": "Introduce Gottman's laboratory physiological findings."},
            {"scene_id": "SC03", "purpose": "Reveal Gottman's biometric finding of 100+ BPM heart rates during silence.", "requirements": ["R03"], "transition": "Explore the biological shutdown of empathy circuits."},
            {"scene_id": "SC04", "purpose": "Showcase how autonomic flooding causes involuntary shutdown.", "requirements": ["R04"], "transition": "Shift focus to the partner's primal attachment alarm."},
            {"scene_id": "SC05", "purpose": "Explain why withdrawal feels like physical abandonment to anxious attachment.", "requirements": ["R05"], "transition": "Deliver sharp critique on conventional communication advice."},
            {"scene_id": "SC06", "purpose": "Editorial commentary on why forcing dialogue during flooding explodes couples.", "requirements": ["R06"], "transition": "Analyze the polarizing feedback loop."},
            {"scene_id": "SC07", "purpose": "Illustrate the tragic mutual fear of losing love underpinning both behaviors.", "requirements": ["R07"], "transition": "Detail the biological timetable for hormonal calming."},
            {"scene_id": "SC08", "purpose": "Explain the 20-minute metabolic recovery window required for empathy.", "requirements": ["R08"], "transition": "Introduce the structured conversational antidote."},
            {"scene_id": "SC09", "purpose": "Present the 20-minute timed return contract step-by-step.", "requirements": ["R09"], "transition": "Provide philosophical verdict on repair versus harmony."},
            {"scene_id": "SC10", "purpose": "Editorial verdict that lasting safety rests on the certainty of return.", "requirements": ["R10"], "transition": "Synthesize emotional wisdom and close."},
            {"scene_id": "SC11", "purpose": "Encourage biological respect in conflicts and invite community sharing.", "requirements": ["R11"], "transition": "End of explainer."},
        ]
    }

    competitor_research = {
        "channel_id": channel_id,
        "job_id": job_id,
        "topic": topic,
        "competitor_analysis": {
            "benchmark_channels": [
                {
                    "channel_name": "The School of Life",
                    "top_performing_videos": [
                        {
                            "title": "Why We Stonewall and How to Stop",
                            "views": "2.9M views",
                            "hook_technique": "Gentle, compassionate dissection of embarrassing relationship behaviors.",
                            "pacing_structure": "Everyday marital freeze -> Psychoanalytic origin -> Tender compassionate reframing.",
                            "retention_driver": "Validates the hidden terror behind seemingly hostile emotional coldness.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Framing defensive hostility as disguised helplessness.",
                        "Uses soft, warm hand-painted watercolor textures to disarm viewer defensiveness.",
                    ],
                },
                {
                    "channel_name": "Cinema Therapy",
                    "top_performing_videos": [
                        {
                            "title": "Therapist Reacts to Anxious-Avoidant Relationships",
                            "views": "1.8M views",
                            "hook_technique": "Demonstrates fictional scenes showing the exact moment one partner runs and the other pursues.",
                            "pacing_structure": "Scene analysis -> Attachment science breakdown -> Practical couple repair rule.",
                            "retention_driver": "Clear, grounded attachment terminology explained with warmth.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Translates Gottman's 'Four Horsemen' into tangible physiological sensations.",
                        "Emphasizes that neither partner is the villain in the dance.",
                    ],
                },
                {
                    "channel_name": "Esther Perel",
                    "top_performing_videos": [
                        {
                            "title": "The Art of De-escalation: When Arguments Spiral",
                            "views": "2.2M views",
                            "hook_technique": "Poetic, piercing observation of what partners actually say versus what their nervous systems feel.",
                            "pacing_structure": "The unspoken subtext -> The somatic freeze -> The courageous micro-repair.",
                            "retention_driver": "Focus on emotional attunement and the rhythm of rupture and repair.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Highlights the asymmetry between longing for closeness and terror of engulfment.",
                        "Replaces blame with curiosity about each partner's biological threshold.",
                    ],
                },
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 18,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Leo and Maya seated opposite at wooden table, separated by a heavy watercolor wash of cold blue shadow.",
                "counter_intuitive_truth_slap": "Your partner is not shutting down out of cold indifference; their heart is racing over 100 BPM in involuntary survival panic.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Visceral kitchen-table confrontation over cold tea."},
                {"phase": "empirical_conflict", "purpose": "Gottman's discovery of hidden physiological flooding."},
                {"phase": "structural_model", "purpose": "The anxious-avoidant trap of mutual escalating terror."},
                {"phase": "actionable_resolution", "purpose": "The 20-minute timed return contract restoring safety."},
                {"phase": "cliffhanger_spinoff", "purpose": "Reframing relational intimacy as the certainty of repair."},
            ],
            "tactile_visual_benchmark": {
                "paper_surface": "Cold-press cotton rag paper (#F7F0E4 textured cotton rag grain) with organic watercolor bleed.",
                "ink_technique": "Soft raw umber charcoal pencil lines (#5B4636) with visible artist construction strokes.",
                "palette_application": "Matte botanical watercolor washes in terracotta (#D97A54), dry sage (#5D8A72), dusty iris (#CDB4DB).",
                "anti_ai_rules": "Zero 3D CGI, zero plastic AI sheen, zero harsh vector borders, minimum 60% negative space on raw paper grain.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Attachment Science & Emotional Repair",
            "myth_debunked": "The silent partner in a heated argument is indifferent and manipulative, while the pursuing partner is just controlling.",
            "channel_verdict": "Stonewalling and pursuing are mirror-image biological survival reflexes protecting against the identical terror of relational loss.",
            "actionable_rule_of_thumb": "Agree on a twenty-minute timed return contract with an exact timestamp before disengaging.",
        },
        "cta_and_spinoff_strategy": {
            "close": "Share gently below what patterns you recognize in your connections.",
            "endcard_text": "FULL VIDEO ON KINDRED SKETCH",
        },
    }

    # 11 scenes, 6 beats & 6 images each = 66 images, 623 words
    scenes_data = [
        # SC01
        {
            "id": "SC01",
            "title": "Cold Tea at the Counter",
            "purpose": "Depict the painful kitchen-table shutdown over cold tea.",
            "action": "Maya reaches across wooden table toward Leo, who tightens jaw and stares down.",
            "setting": "Intimate kitchen dining nook on warm watercolor paper #F7F0E4.",
            "camera": "Eye-level intimate two-shot capturing micro-expressions.",
            "narration": "It begins at the kitchen counter over cold tea late in the evening. One partner asks gently, What is wrong? The other looks down at the table, tightens their jaw, and mutters, Nothing, just drop it. Within seconds, the room feels freezing cold, and the conversation snaps shut like a heavy wooden door.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Intimate, tense, tender",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "prompts": [
                ("SC01_I1", "Warm charcoal-pencil and watercolor illustration on cold-press paper #F7F0E4: Leo in sage knit sweater and Maya in terracotta cardigan sitting opposite at a rustic wooden table with two ceramic tea mugs, delicate charcoal outlines #5B4636, >=60% negative space.", "burst", "full_scene"),
                ("SC01_I2", "Close-up of Maya's hand gently reaching halfway across the table surface toward Leo, fingers trembling slightly, soft muted rose watercolor wash #F7C6C7 on cotton paper.", "fast", "macro_detail"),
                ("SC01_I3", "Close-up portrait of Leo looking downward with a clenched jawline and tightened lips in soft raw umber charcoal on textured rag paper #F7F0E4.", "fast", "macro_detail"),
                ("SC01_I4", "A cold watercolor shadow wash in dusty iris #CDB4DB spreading between the two ceramic mugs like frost creeping across cold glass on cream paper.", "normal", "concept_metaphor"),
                ("SC01_I5", "Metaphorical sketch of a thick oak door with heavy iron hinges slamming shut between the couple, drawn in textured charcoal pencil on paper #F7F0E4.", "normal", "concept_metaphor"),
                ("SC01_I6", "Maya leaning back in her chair with a wounded expression as Leo turns his head toward the dark kitchen window on textured cotton paper #F7F0E4.", "hold", "full_scene"),
            ],
            "quotes": [
                "It begins at the kitchen counter over cold tea late in the evening.",
                "One partner asks gently, What is wrong?",
                "The other looks down at the table, tightens their jaw,",
                "and mutters, Nothing, just drop it.",
                "Within seconds, the room feels freezing cold,",
                "and the conversation snaps shut like a heavy wooden door.",
            ],
        },
        # SC02
        {
            "id": "SC02",
            "title": "The Escalation Reflex",
            "purpose": "Examine the pursuer's desperation versus the distancer's wall.",
            "action": "Maya leans forward speaking urgently while Leo crosses arms and shrinks back.",
            "setting": "Dimly lit dining room with expanding emotional distance.",
            "camera": "Profile comparative split angle.",
            "narration": "Instinctively, the pursuing partner leans closer, raising their voice to demand answers. Why will you not talk to me? Meanwhile, the retreating partner shrinks back, crossing their arms and staring out the window. One is desperately chasing contact, while the other is building an impenetrable fortress out of pure silence.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Somatic, urgent, tragic",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC02_I1", "Maya leaning forward with both hands on the table, eyes searching Leo's face with urgent desperation, drawn in charcoal pencil with terracotta wash #D97A54 on textured paper #F7F0E4.", "fast", "full_scene"),
                ("SC02_I2", "Speech bubbles rendered as fluttering paper birds flying frantically from Maya toward Leo on cold-press watercolor paper #F7F0E4.", "normal", "concept_metaphor"),
                ("SC02_I3", "Leo folding his arms defensively across his chest, posture stiffening as if shielding his torso on textured cotton rag paper #F7F0E4, sage wash #5D8A72.", "normal", "full_scene"),
                ("SC02_I4", "Close-up of Leo's gaze fixed blankly on raindrops running down windowpane glass, charcoal hatching on cream paper #F7F0E4.", "fast", "macro_detail"),
                ("SC02_I5", "Metaphorical illustration of Maya chasing a fleeing silhouette across a vast empty sketchbook meadow on warm paper #F7F0E4.", "normal", "concept_metaphor"),
                ("SC02_I6", "Leo surrounded by rising stone fortress battlements sketched in soft graphite and raw umber ink, completely walling himself off on paper #F7F0E4.", "hold", "concept_metaphor"),
            ],
            "quotes": [
                "Instinctively, the pursuing partner leans closer,",
                "raising their voice to demand answers. Why will you not talk to me?",
                "Meanwhile, the retreating partner shrinks back,",
                "crossing their arms and staring out the window.",
                "One is desperately chasing contact,",
                "while the other is building an impenetrable fortress out of pure silence.",
            ],
        },
        # SC03
        {
            "id": "SC03",
            "title": "Gottman's Biometric Discovery",
            "purpose": "Reveal Gottman's biometric finding of 100+ BPM heart rates during silence.",
            "action": "A heart monitor graphic showing Leo's pulse spiking despite calm exterior.",
            "setting": "University of Washington Love Lab research setting blended with emotional art.",
            "camera": "Scientific anatomical focus with delicate watercolor.",
            "narration": "Decades of research by Dr. John Gottman at the University of Washington revealed a stunning physiological reality. Observers assume the silent partner is cold, detached, or cruel. In truth, biometric monitors show their pulse skyrocketing past one hundred beats per minute, entering a state known as diffuse physiological arousal.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Revelatory, scientific, deeply validating",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC03_I1", "Vintage research lab notebook page with hand-written clinical notes and pencil drawings of heart monitors on cold-press paper #F7F0E4.", "burst", "macro_detail"),
                ("SC03_I2", "A silent observer caricature pointing an accusing finger at Leo, assuming cruelty, sketched in charcoal on textured paper #F7F0E4.", "fast", "full_scene"),
                ("SC03_I3", "Leo's external face appearing still and stony, while beneath the skin his ribcage glows with fiery vermilion watercolor heat on paper #F7F0E4.", "normal", "concept_metaphor"),
                ("SC03_I4", "An inked electrocardiogram pulse line jumping violently upward across the page with handwritten numeric annotation '105 BPM' on textured paper #F7F0E4.", "normal", "macro_detail"),
                ("SC03_I5", "Leo clutching a wooden chair armrest with knuckles turning white under strain, charcoal shading on cream rag paper #F7F0E4.", "fast", "macro_detail"),
                ("SC03_I6", "An anatomical watercolor diagram of the human sympathetic nervous system firing red electrical pulses through the spine on cold-press paper #F7F0E4.", "hold", "macro_detail"),
            ],
            "quotes": [
                "Decades of research by Dr. John Gottman at the University of Washington",
                "revealed a stunning physiological reality.",
                "Observers assume the silent partner is cold, detached, or cruel.",
                "In truth, biometric monitors show their pulse skyrocketing past one hundred beats per minute,",
                "entering a state known as",
                "diffuse physiological arousal.",
            ],
        },
        # SC04
        {
            "id": "SC04",
            "title": "The Neurological Flooding",
            "purpose": "Showcase how autonomic flooding causes involuntary shutdown.",
            "action": "Blood rushing into muscles while higher prefrontal empathy centers dim.",
            "setting": "Internal neurological landscape sketched in loose botanical watercolor.",
            "camera": "Macro zoom into cognitive centers.",
            "narration": "When the autonomic nervous system enters flooding, oxygenated blood rushes to large muscles and peripheral vision narrows into a dark tunnel. The higher executive centers responsible for empathy and nuanced conversation shut down completely. Stonewalling is not an act of arrogant indifference; it is an involuntary emergency shutdown triggered by an overwhelmed biological threat detector.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Empathetic, somatic, clarifying",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC04_I1", "Botanical watercolor cross-section of the human vascular system with arterial branches pulsing deep terracotta red on cold-press paper #F7F0E4.", "fast", "macro_detail"),
                ("SC04_I2", "Leo's point of view illustrated as heavy tunnel vision with dark vignetted charcoal charcoal edges blurring the cozy room on textured paper #F7F0E4.", "normal", "environment"),
                ("SC04_I3", "Prefrontal brain lobes drawn as glowing paper lanterns whose warm light gently flickers and dims out on cream paper #F7F0E4.", "normal", "concept_metaphor"),
                ("SC04_I4", "An antique brass electrical circuit breaker snapping down with a bright ink spark, representing cognitive shutdown on textured rag paper #F7F0E4.", "slow", "concept_metaphor"),
                ("SC04_I5", "Leo standing like a frozen stone garden statue in gentle rain, showing internal paralysis rather than hostility on cold-press paper #F7F0E4.", "normal", "full_scene"),
                ("SC04_I6", "A biological alarm bell clapper vibrating wildly against the amygdala deep inside the brain sketch on textured cotton paper #F7F0E4, amber wash #FFF1B5.", "hold", "macro_detail"),
            ],
            "quotes": [
                "When the autonomic nervous system enters flooding,",
                "oxygenated blood rushes to large muscles and peripheral vision narrows into a dark tunnel.",
                "The higher executive centers responsible for empathy and nuanced conversation shut down completely.",
                "Stonewalling is not an act of arrogant indifference;",
                "it is an involuntary emergency shutdown",
                "triggered by an overwhelmed biological threat detector.",
            ],
        },
        # SC05
        {
            "id": "SC05",
            "title": "The Anxious Attachment Alarm",
            "purpose": "Explain why withdrawal feels like physical abandonment to anxious attachment.",
            "action": "Maya feeling the ground crumble under her feet as silence sets in.",
            "setting": "Metaphorical crumbling landscape sketched in charcoal.",
            "camera": "Intense close-up on Maya's expressive face.",
            "narration": "On the opposite side of the table, that sudden withdrawal sounds like a catastrophic siren. For someone with an anxious attachment style, emotional disconnection registers neurologically as physical abandonment. Pursuing louder is not an attempt to pick a fight; it is a desperate survival reflex to verify that the bond still exists.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Heartbreaking, validating, perceptive",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC05_I1", "Maya sitting alone on an icy floe drifting away from the warm kitchen shoreline on cold-press watercolor paper #F7F0E4, dusty iris wash #CDB4DB.", "burst", "concept_metaphor"),
                ("SC05_I2", "A lighthouse beam sweeping through thick fog, searching frantically for a lost ship in dark raw umber ink on textured paper #F7F0E4.", "fast", "concept_metaphor"),
                ("SC05_I3", "Maya's hand clutching her chest where an ink outline of a fragile bird beats its wings against ribs on warm cotton rag paper #F7F0E4.", "normal", "macro_detail"),
                ("SC05_I4", "Sketch of an infant animal calling out in dark woods, visualizing primal attachment distress in delicate charcoal on cream paper #F7F0E4.", "slow", "concept_metaphor"),
                ("SC05_I5", "Maya standing with hands extended in sincere plea, not anger, with soft terracotta watercolor tones #D97A54 on textured paper #F7F0E4.", "normal", "full_scene"),
                ("SC05_I6", "A golden ribbon connecting two hearts fraying at the center under tension on cold-press paper #F7F0E4, >=60% negative space.", "hold", "concept_metaphor"),
            ],
            "quotes": [
                "On the opposite side of the table, that sudden withdrawal sounds like a catastrophic siren.",
                "For someone with an anxious attachment style,",
                "emotional disconnection registers neurologically as physical abandonment.",
                "Pursuing louder is not an attempt to pick a fight;",
                "it is a desperate survival reflex",
                "to verify that the bond still exists.",
            ],
        },
        # SC06
        {
            "id": "SC06",
            "title": "Why Talk It Out Advice Explodes",
            "purpose": "Editorial commentary on why forcing dialogue during flooding explodes couples.",
            "action": "Two flooded nervous systems clashing like stormy waves against rocks.",
            "setting": "Abstract turbulent storm on cold-press paper.",
            "camera": "Dynamic expansive perspective.",
            "narration": "Popular relationship advice tells couples to simply sit down and communicate openly when tempers flare. But trying to talk through emotional wounds while flooded is like attempting delicate brain surgery during an earthquake. Pushing an overwhelmed avoidant partner to open up only triggers deeper retreat, confirming the pursuer's worst fear that love has evaporated.",
            "requirements": ["R06"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Passionate, corrective, incisive",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "prompts": [
                ("SC06_I1", "A glossy self-help paperback with clean cheerful typography drowning in a puddle of spilled black ink on textured paper #F7F0E4.", "slow", "concept_metaphor"),
                ("SC06_I2", "Metaphorical drawing of a surgeon attempting delicate eye microsurgery while the ground splits in an earthquake on cotton rag paper #F7F0E4.", "normal", "concept_metaphor"),
                ("SC06_I3", "Maya pressing an open journal against Leo's wooden door as Leo braces both shoulders against the inside on textured cream paper #F7F0E4.", "slow", "full_scene"),
                ("SC06_I4", "Leo retreating into an underground root cellar, pulling the hatch closed in charcoal pencil shading on cold-press paper #F7F0E4.", "slow", "environment"),
                ("SC06_I5", "Maya dropping her hands to her sides, tears pooling in ink eyes as cold shadows envelop her shoulders on textured paper #F7F0E4.", "normal", "macro_detail"),
                ("SC06_I6", "Two hands reaching toward each other through dense barbed wire, highlighting painful futility of flooded communication on paper #F7F0E4.", "hold", "concept_metaphor"),
            ],
            "quotes": [
                "Popular relationship advice tells couples to simply sit down and communicate openly when tempers flare.",
                "But trying to talk through emotional wounds while flooded",
                "is like attempting delicate brain surgery during an earthquake.",
                "Pushing an overwhelmed avoidant partner to open up only triggers deeper retreat,",
                "confirming the pursuer's worst fear",
                "that love has evaporated.",
            ],
        },
        # SC07
        {
            "id": "SC07",
            "title": "The Polarized Dance",
            "purpose": "Illustrate the tragic mutual fear of losing love underpinning both behaviors.",
            "action": "Both Leo and Maya shown with mirror-image emotional pain beneath opposite facades.",
            "setting": "Split mirror composition on cold-press watercolor paper.",
            "camera": "Symmetrical diptych composition.",
            "narration": "Here lies the tragic trap of the anxious-avoidant dynamic. The harder the pursuer knocks on the door, the more terrified the distancer becomes of being swallowed alive. And the quieter the distancer grows, the more terrified the pursuer becomes of being permanently discarded. Both partners are terrified of the exact same outcome: losing love.",
            "requirements": ["R07"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC02"],
            "tone": "Profoundly moving, sympathetic, illuminating",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC07_I1", "Symmetrical diptych illustration: Maya knocking on a door on left, Leo leaning against same door on right on cold-press rag paper #F7F0E4.", "burst", "full_scene"),
                ("SC07_I2", "Leo depicted as a small bird terrified of being captured in a heavy brass cage, sketched in charcoal on warm paper #F7F0E4.", "fast", "concept_metaphor"),
                ("SC07_I3", "Maya depicted as a solitary figure standing alone on an endless dark dock at midnight on textured cotton paper #F7F0E4, dusty iris wash #CDB4DB.", "normal", "concept_metaphor"),
                ("SC07_I4", "Close-up of both their eyes in split frames, showing identical vulnerability and tears beneath different masks on paper #F7F0E4.", "normal", "macro_detail"),
                ("SC07_I5", "A fragile glass heart cradled between two trembling hands on cold-press watercolor paper #F7F0E4, soft terracotta and sage washes.", "fast", "concept_metaphor"),
                ("SC07_I6", "The two characters standing back to back, heads bowed in shared sorrow under soft ambient watercolor light on paper #F7F0E4, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "Here lies the tragic trap of the anxious-avoidant dynamic.",
                "The harder the pursuer knocks on the door, the more terrified the distancer becomes of being swallowed alive.",
                "And the quieter the distancer grows,",
                "the more terrified the pursuer becomes of being permanently discarded.",
                "Both partners are terrified of the exact same outcome:",
                "losing love.",
            ],
        },
        # SC08
        {
            "id": "SC08",
            "title": "The Twenty-Minute Biological Reset",
            "purpose": "Explain the 20-minute metabolic recovery window required for empathy.",
            "action": "A biological hourglass filtering stress hormones as heart rates drop.",
            "setting": "Gentle, calm botanical study space.",
            "camera": "Slow rhythmic pacing matching a calming pulse.",
            "narration": "Once a nervous system reaches physiological flooding, no amount of clever logic or pleading can restore calm. It takes at least twenty minutes for stress hormones like cortisol and norepinephrine to clear the bloodstream. Until the heart rate drops back below baseline, genuine emotional attunement is biologically impossible for both individuals.",
            "requirements": ["R08"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Calming, biological, reassuring",
            "narrative_phase": "structural_model",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC08_I1", "A vintage brass 20-minute sand timer with fine golden sand flowing steadily through narrow glass neck on cold-press paper #F7F0E4.", "fast", "concept_metaphor"),
                ("SC08_I2", "An anatomical watercolor depiction of stress hormones dissipating like morning mist from capillary beds into clean paper white on #F7F0E4.", "normal", "macro_detail"),
                ("SC08_I3", "A pulse line gradually calming from jagged mountain peaks into smooth, gentle ocean swells on textured cotton paper #F7F0E4.", "slow", "macro_detail"),
                ("SC08_I4", "Leo sitting quietly by himself in a garden chair, taking three deep breaths with closed eyes on cold-press paper #F7F0E4, sage wash #5D8A72.", "normal", "full_scene"),
                ("SC08_I5", "Prefrontal brain regions slowly re-igniting with warm, soft lantern light as executive empathy reactivates on paper #F7F0E4.", "fast", "macro_detail"),
                ("SC08_I6", "Maya resting her forehead on her arms at the table, breath slowing as physical tension releases from her shoulders on cream paper #F7F0E4.", "hold", "full_scene"),
            ],
            "quotes": [
                "Once a nervous system reaches physiological flooding,",
                "no amount of clever logic or pleading can restore calm.",
                "It takes at least twenty minutes for stress hormones like cortisol and norepinephrine to clear the bloodstream.",
                "Until the heart rate drops back below baseline,",
                "genuine emotional attunement is biologically impossible",
                "for both individuals.",
            ],
        },
        # SC09
        {
            "id": "SC09",
            "title": "The Timed Return Contract",
            "purpose": "Present the 20-minute timed return contract step-by-step.",
            "action": "Leo speaking reassuring words while pointing to clock; Maya feeling immediate relief.",
            "setting": "The kitchen table transformed by intentional structure.",
            "camera": "Close two-shot focusing on eye contact and clocks.",
            "narration": "To disarm the cycle, implement the twenty-minute timed return contract. The retreating partner must explicitly say, I care about this conversation, but I am flooded right now; let us take twenty minutes, and I promise to return at eight fifteen. That precise timestamp gives the anxious nervous system certainty while giving the avoidant nervous system air.",
            "requirements": ["R09"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Clear, practical, restorative",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "actionable_resolution",
            "prompts": [
                ("SC09_I1", "Leo holding Maya's hand gently, speaking with soft eye contact before stepping away on cold-press watercolor paper #F7F0E4.", "burst", "full_scene"),
                ("SC09_I2", "A handwritten card on the table sketched in ink: 'I love you. I am flooded. Back at 8:15 PM.' on textured rag paper #F7F0E4.", "fast", "macro_detail"),
                ("SC09_I3", "An analog kitchen wall clock with hands clearly pointing to a 20-minute interval, glowing in warm sienna watercolor wash #FFF1B5.", "normal", "macro_detail"),
                ("SC09_I4", "Maya's shoulders visibly dropping two inches in pure physical relief as the abandonment alarm switches off on textured paper #F7F0E4.", "normal", "full_scene"),
                ("SC09_I5", "Leo taking a walk outdoors under green maple leaves, lungs expanding with cool fresh air on cold-press paper #F7F0E4, sage wash #5D8A72.", "fast", "environment"),
                ("SC09_I6", "Two empty chairs at the table with warm light overhead, waiting peacefully for the promised reunion on paper #F7F0E4, >=60% negative space.", "hold", "environment"),
            ],
            "quotes": [
                "To disarm the cycle, implement the twenty-minute timed return contract.",
                "The retreating partner must explicitly say,",
                "I care about this conversation, but I am flooded right now;",
                "let us take twenty minutes, and I promise to return at eight fifteen.",
                "That precise timestamp gives the anxious nervous system certainty",
                "while giving the avoidant nervous system air.",
            ],
        },
        # SC10
        {
            "id": "SC10",
            "title": "Repair is the True Sanctuary",
            "purpose": "Editorial verdict that lasting safety rests on the certainty of return.",
            "action": "Leo returning to the table at the exact promised time; hands clasping.",
            "setting": "Warm glowing kitchen table in evening light.",
            "camera": "Intimate cinematic close shot on reunited hands.",
            "narration": "True relational safety is never measured by the total absence of conflict. Lasting intimacy is built on the predictable guarantee of emotional repair. When you stop treating your partner's survival reflex as a personal attack, the kitchen table stops being a battleground, transforming instead into a sanctuary where both nervous systems can finally breathe.",
            "requirements": ["R10"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Wise, moving, transformative",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "editorial_commentary",
            "prompts": [
                ("SC10_I1", "Leo opening the kitchen door right as the clock strikes 8:15 PM, smiling gently at Maya on cold-press watercolor paper #F7F0E4.", "slow", "full_scene"),
                ("SC10_I2", "A Japanese Kintsugi bowl repaired with shimmering golden lacquer, symbolizing stronger bonds after repair on textured paper #F7F0E4.", "normal", "concept_metaphor"),
                ("SC10_I3", "The heavy stone fortress walls around the kitchen table crumbling into soft green moss and wild violets on cotton rag paper #F7F0E4.", "slow", "concept_metaphor"),
                ("SC10_I4", "Maya and Leo sitting close at the table, leaning their foreheads together in deep mutual understanding on textured paper #F7F0E4.", "normal", "full_scene"),
                ("SC10_I5", "Warm golden light pooling across the tabletop, illuminating two full ceramic cups of fresh hot tea on cold-press paper #F7F0E4.", "slow", "macro_detail"),
                ("SC10_I6", "Both characters breathing in unison as soft watercolor wash blends terracotta and sage in harmonious balance on paper #F7F0E4, >=60% negative space.", "hold", "full_scene"),
            ],
            "quotes": [
                "True relational safety is never measured by the total absence of conflict.",
                "Lasting intimacy is built on the predictable guarantee of emotional repair.",
                "When you stop treating your partner's survival reflex as a personal attack,",
                "the kitchen table stops being a battleground,",
                "transforming instead into a sanctuary",
                "where both nervous systems can finally breathe.",
            ],
        },
        # SC11
        {
            "id": "SC11",
            "title": "Closing Synthesis & The Timed Return",
            "purpose": "Encourage biological respect in conflicts and invite community sharing.",
            "action": "Leo and Maya walking together down a tree-lined path; endcard establishes.",
            "setting": "Peaceful autumn neighborhood trail.",
            "camera": "Gentle retreating wide shot into soft watercolor wash.",
            "narration": "Breaking the anxious-avoidant loop does not require changing who you are; it requires respecting biological limits of the human heart. The next time the silence settles between you, pause the interrogation and agree on a timed return. Watch the complete guide to healthy attachment on Kindred Sketch YouTube. Share gently below what patterns you recognize in your connections.",
            "requirements": ["R11"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC03"],
            "tone": "Warm, restorative, inviting",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cta_close",
            "prompts": [
                ("SC11_I1", "Leo and Maya holding hands while walking side by side down a quiet tree-lined path in soft morning watercolor on cold-press paper #F7F0E4.", "normal", "full_scene"),
                ("SC11_I2", "A blooming olive branch sketched in raw umber charcoal with delicate sage watercolor wash #5D8A72 on textured cotton rag paper #F7F0E4.", "normal", "concept_metaphor"),
                ("SC11_I3", "Two nervous systems depicted as twin blossoming trees whose roots intertwine safely underground on textured paper #F7F0E4.", "slow", "concept_metaphor"),
                ("SC11_I4", "Close-up of their intertwined fingers resting gently on a wooden park bench in soft natural light on cold-press paper #F7F0E4.", "slow", "macro_detail"),
                ("SC11_I5", "Leo and Maya looking toward the golden horizon together with calm, grounded posture on textured cream paper #F7F0E4, >=60% negative space.", "hold", "full_scene"),
                ("SC11_I6", "Editorial channel endcard on cold-press watercolor paper #F7F0E4 with botanical leafy border and uppercase hand-lettered text in upper third: 'KINDRED SKETCH'.", "hold", "full_scene", True),
            ],
            "quotes": [
                "Breaking the anxious-avoidant loop does not require changing who you are;",
                "it requires respecting biological limits of the human heart.",
                "The next time the silence settles between you, pause the interrogation and agree on a timed return.",
                "Watch the complete guide to healthy attachment on Kindred Sketch YouTube.",
                "Share gently below",
                "what patterns you recognize in your connections.",
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
                preserve="Warm charcoal-pencil and botanical watercolor aesthetic, cold-press rag paper #F7F0E4, Leo in sage sweater and Maya in terracotta cardigan, raw umber outlines #5B4636.",
                change=f"Progress to beat {p_id} showing {desc[:60]}...",
                reason=f"Visualize relationship dynamic progression for {sc_id} beat {i+1}.",
                tempo=tempo,
                situation=sc_data["narrative_situation"],
                motion_prompt="Smooth 2D watercolor animation. Subtle charcoal sketch line shifts, organic watercolor bleeding gently across cold-press paper, zero lip-sync, intimate tender character micro-movements.",
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
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "It begins at the kitchen counter over cold tea late in the evening."},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Instinctively, the pursuing partner leans closer, raising their voice to demand answers."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "In truth, biometric monitors show their pulse skyrocketing past one hundred beats per minute, entering a state known as diffuse physiological arousal."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Stonewalling is not an act of arrogant indifference; it is an involuntary emergency shutdown triggered by an overwhelmed biological threat detector."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "For someone with an anxious attachment style, emotional disconnection registers neurologically as physical abandonment."},
            {"requirement_id": "R06", "scene_id": "SC06", "quote": "Popular relationship advice tells couples to simply sit down and communicate openly when tempers flare."},
            {"requirement_id": "R07", "scene_id": "SC07", "quote": "Both partners are terrified of the exact same outcome: losing love."},
            {"requirement_id": "R08", "scene_id": "SC08", "quote": "It takes at least twenty minutes for stress hormones like cortisol and norepinephrine to clear the bloodstream."},
            {"requirement_id": "R09", "scene_id": "SC09", "quote": "To disarm the cycle, implement the twenty-minute timed return contract."},
            {"requirement_id": "R10", "scene_id": "SC10", "quote": "True relational safety is never measured by the total absence of conflict. Lasting intimacy is built on the predictable guarantee of emotional repair."},
            {"requirement_id": "R11", "scene_id": "SC11", "quote": "Breaking the anxious-avoidant loop does not require changing who you are; it requires respecting biological limits of the human heart."},
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC03",
                "quote": "In truth, biometric monitors show their pulse skyrocketing past one hundred beats per minute, entering a state known as diffuse physiological arousal.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Stonewalling occurs when heart rate surpasses one hundred beats per minute during marital dispute.",
            },
            {
                "scene_id": "SC05",
                "quote": "For someone with an anxious attachment style, emotional disconnection registers neurologically as physical abandonment.",
                "language": "en",
                "source_id": "SRC02",
                "fact": "Perceived emotional withdrawal triggers biological attachment panic in anxiously attached partners.",
            },
            {
                "scene_id": "SC08",
                "quote": "It takes at least twenty minutes for stress hormones like cortisol and norepinephrine to clear the bloodstream.",
                "language": "en",
                "source_id": "SRC03",
                "fact": "The human nervous system requires at least twenty minutes of emotional safety to metabolize stress hormones.",
            },
        ],
        "revision_response": [],
        "open_questions": [],
    }

    return job_id, brief, outline, competitor_research, content


def build_kindred_sketch_short() -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    channel_id = "en_kindred_sketch"
    slug = "en-kindred-sketch"
    parent_long_id = f"{slug}-batch1-16x9"
    job_id = f"{slug}-batch1-9x16"
    ch = get_channel(channel_id)

    topic = "The Anxious-Avoidant Trap: Why One Partner Pursues Harder While the Other Stonewalls—And How to Break It"
    youtube_title = "Why Saying 'I'm Fine' Spikes Your Partner's Pulse"

    brief: Dict[str, Any] = {
        "schema_version": "3.0",
        "topic": topic,
        "audience": ch.audience,
        "goal": "Explain Gottman's 100+ BPM stonewalling discovery in 45s, debunk partner malice, and provide the 20-minute timed return bridge.",
        "video_type": "explainer",
        "duration": {
            "min_seconds": 38.0,
            "max_seconds": 52.0,
        },
        "scene_count": 5,
        "required_points": [
            {"id": "R01", "text": "Saying 'I'm fine' accompanies a heart rate spike above 100 BPM."},
            {"id": "R02", "text": "Stonewalling is an involuntary survival shutdown, not cold indifference."},
            {"id": "R03", "text": "Editorial commentary on how demanding answers during flooding explodes empathy."},
            {"id": "R04", "text": "The twenty-minute timed return contract calms both attachment systems."},
            {"id": "R05", "text": "Cliffhanger peak on the de-escalation phrase, channel bridge, and CTA."},
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
                "title": "The Physiological Correlates of Marital Conflict: Diffuse Physiological Arousal and Stonewalling",
                "reference": "Gottman, J. M., & Levenson, R. W. (1988). Journal of Personality and Social Psychology, 54(5), 890-900.",
                "facts": [
                    "Stonewalling occurs when heart rate surpasses one hundred beats per minute during marital dispute.",
                    "Diffuse physiological arousal shuts down cognitive capacity for empathy and active listening.",
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
                "Hook viewers in under 3s with the counter-intuitive biological reality behind 'I'm fine'.",
                "Reveal the 100+ BPM Love Lab finding with warm watercolor and charcoal animation.",
                "Bridge seamlessly to the full relational guide at the peak open loop.",
            ],
            "avoid": list(ch.avoid),
            "prior_knowledge": "None required.",
            "pacing": "Gentle yet urgent and rhythmic, spoken cadence at 3.8 words per second.",
            "assumptions": [
                "High visual density with 4 beats and 4 unique images per scene across 5 scenes.",
            ],
        },
        "packaging": {
            "youtube_title": youtube_title,
            "thumbnail_spec": {
                "visual_hook": "Leo turning away saying 'I'm fine' with heart rate monitor reading 104 BPM as Maya reaches out",
                "text_overlay": "PULSE OVER 100",
                "contrast_pair": "I'm fine cold facade vs Internal panic 100 BPM heart rate",
                "thumbnail_prompt": "Warm charcoal-pencil and botanical watercolor vertical illustration on cold-press rag paper (#F7F0E4). Leo turning head away with jaw set, speech bubble saying 'I'M FINE', while a bold red pulse monitor line spikes to '104 BPM' over his chest. Maya reaching from the edge with pleading charcoal eyes. Terracotta (#D97A54) and sage (#5D8A72) washes. Hand-lettered uppercase text: 'PULSE OVER 100'. Vertical 9:16, >=60% negative space, zero 3D CGI.",
                "layout_mode": "split_contrast",
            },
            "channel_pillar": "Attachment Science & Emotional Repair",
            "funnel_tier": "tier_1_broad",
            "seo_keywords": ["kindred sketch", "shorts", "relationships", "stonewalling", "gottman", "couples"],
            "parent_long_id": parent_long_id,
            "cta_plan": {
                "cliffhanger_peak": "What exact three-word phrase allows an avoidant partner to pause without triggering abandonment panic?",
                "bridge": "Watch the complete guide to healthy attachment on Kindred Sketch YouTube.",
                "close": "Share this with someone whose bond you cherish and want to understand better.",
                "endcard_text": "FULL VIDEO ON YOUTUBE",
            },
            "editorial_stance": {
                "myth_debunked": "The silent partner in a heated argument is indifferent and manipulative, while the pursuing partner is just controlling.",
                "why_generic_advice_fails": "Demanding open communication while partners are physiologically flooded forces an overwhelmed nervous system into deeper defensive survival mode.",
                "channel_verdict": "Stonewalling and pursuing are mirror-image biological survival reflexes protecting against the identical terror of relational loss.",
                "tradeoff_or_blindspot": "Walking away for twenty minutes requires immense restraint from the pursuer, but it is necessary to restore neurological empathy.",
            },
            "actionable_value": {
                "core_mechanism": "Autonomic flooding above one hundred beats per minute blinds emotional processing, turning conversation into perceived threat.",
                "practical_rule_of_thumb": "Agree on a twenty-minute timed return contract with an exact timestamp before disengaging.",
                "real_world_scenario": "When conflict escalates over dinner, state a specific twenty-minute return time rather than storming out silently.",
            },
        },
        "youtube_title": youtube_title,
        "thumbnail_spec": {
            "visual_hook": "Leo turning away saying 'I'm fine' with heart rate monitor reading 104 BPM as Maya reaches out",
            "text_overlay": "PULSE OVER 100",
            "contrast_pair": "I'm fine cold facade vs Internal panic 100 BPM heart rate",
            "thumbnail_prompt": "Warm charcoal-pencil and botanical watercolor vertical illustration on cold-press rag paper (#F7F0E4). Leo turning head away with jaw set, speech bubble saying 'I'M FINE', while a bold red pulse monitor line spikes to '104 BPM' over his chest. Maya reaching from the edge with pleading charcoal eyes. Terracotta (#D97A54) and sage (#5D8A72) washes. Hand-lettered uppercase text: 'PULSE OVER 100'. Vertical 9:16, >=60% negative space, zero 3D CGI.",
            "layout_mode": "split_contrast",
        },
        "channel_pillar": "Attachment Science & Emotional Repair",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["kindred sketch", "shorts", "relationships", "stonewalling", "gottman", "couples"],
        "parent_long_id": parent_long_id,
        "cta_plan": {
            "cliffhanger_peak": "What exact three-word phrase allows an avoidant partner to pause without triggering abandonment panic?",
            "bridge": "Watch the complete guide to healthy attachment on Kindred Sketch YouTube.",
            "close": "Share this with someone whose bond you cherish and want to understand better.",
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
            "myth_debunked": "The silent partner in a heated argument is indifferent and manipulative, while the pursuing partner is just controlling.",
            "why_generic_advice_fails": "Demanding open communication while partners are physiologically flooded forces an overwhelmed nervous system into deeper defensive survival mode.",
            "channel_verdict": "Stonewalling and pursuing are mirror-image biological survival reflexes protecting against the identical terror of relational loss.",
            "tradeoff_or_blindspot": "Walking away for twenty minutes requires immense restraint from the pursuer, but it is necessary to restore neurological empathy.",
        },
        "actionable_value": {
            "core_mechanism": "Autonomic flooding above one hundred beats per minute blinds emotional processing, turning conversation into perceived threat.",
            "practical_rule_of_thumb": "Agree on a twenty-minute timed return contract with an exact timestamp before disengaging.",
            "real_world_scenario": "When conflict escalates over dinner, state a specific twenty-minute return time rather than storming out silently.",
        },
        "video_engine": "flow_video",
        "chain_mode": "daisy_chain",
    }

    outline = {
        "outline": [
            {"scene_id": "SC01", "purpose": "Hook on the 100+ BPM heart rate spike behind saying 'I am fine'.", "requirements": ["R01"], "transition": "Explain the biological basis in Gottman's research."},
            {"scene_id": "SC02", "purpose": "Deconstruct stonewalling as autonomic survival overload.", "requirements": ["R02"], "transition": "Deliver editorial critique on forcing communication."},
            {"scene_id": "SC03", "purpose": "Editorial commentary on the futility of talking through flooding.", "requirements": ["R03"], "transition": "Provide the 20-minute timed contract antidote."},
            {"scene_id": "SC04", "purpose": "Demonstrate the 20-minute timed return contract in action.", "requirements": ["R04"], "transition": "Peak twist question on repair phrases and channel bridge."},
            {"scene_id": "SC05", "purpose": "Cliffhanger peak on de-escalation phrases, YouTube bridge, and closing CTA.", "requirements": ["R05"], "transition": "End of short."},
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
                            "title": "Why Avoidants Pull Away When Things Get Good",
                            "views": "2.1M views",
                            "hook_technique": "Relatable quote confronting avoidant panic directly.",
                            "pacing_structure": "The hurtful moment -> The biological cause -> The healing step.",
                            "retention_driver": "Empathy-first psychological explanations.",
                        }
                    ],
                    "viral_patterns_extracted": [
                        "Translates relational defense into biological fight-or-flight terms.",
                        "Uses soft, warm illustration to reduce viewer defensiveness.",
                    ],
                }
            ]
        },
        "viral_formula_audit": {
            "cold_audience_hook_analysis": {
                "first_sentence_syllables": 22,
                "zero_pause_opening_seconds": 12,
                "visual_contrast": "Leo saying 'I'm fine' while a red heartbeat monitor spikes violently to 104 BPM.",
                "counter_intuitive_truth_slap": "That cold silence is not arrogance or lack of love; your partner's nervous system is drowning in acute physical panic.",
            },
            "narrative_progression_arc": [
                {"phase": "lived_friction", "purpose": "Visceral hook exposing the 100+ BPM reality behind silence."},
                {"phase": "empirical_conflict", "purpose": "Gottman's research proving stonewalling is an involuntary shutdown."},
                {"phase": "structural_model", "purpose": "Editorial critique on why forced dialogue during flooding explodes."},
                {"phase": "actionable_resolution", "purpose": "The 20-minute timed return contract disarming both systems."},
                {"phase": "cliffhanger_spinoff", "purpose": "Cliffhanger peak on de-escalation scripts and YouTube bridge."},
            ],
            "tactile_visual_benchmark": {
                "paper_surface": "Cold-press cotton rag paper (#F7F0E4 textured cotton rag grain).",
                "ink_technique": "Soft charcoal pencil lines (#5B4636 raw umber) with organic watercolor wash.",
                "palette_application": "Matte botanical watercolor: terracotta (#D97A54), dry sage (#5D8A72), dusty iris (#CDB4DB).",
                "anti_ai_rules": "Vertical 9:16, zero 3D CGI, zero plastic sheen, minimum 60% negative space.",
            },
        },
        "academic_funnel_positioning": {
            "funnel_tier": "tier_1_broad",
            "channel_pillar": "Attachment Science & Emotional Repair",
            "myth_debunked": "The silent partner in a heated argument is indifferent and manipulative, while the pursuing partner is just controlling.",
            "channel_verdict": "Stonewalling and pursuing are mirror-image biological survival reflexes protecting against the identical terror of relational loss.",
            "actionable_rule_of_thumb": "Agree on a twenty-minute timed return contract with an exact timestamp before disengaging.",
        },
        "cta_and_spinoff_strategy": {
            "cliffhanger_peak": "What exact three-word phrase allows an avoidant partner to pause without triggering abandonment panic?",
            "bridge": "Watch the complete guide to healthy attachment on Kindred Sketch YouTube.",
            "close": "Share this with someone whose bond you cherish and want to understand better.",
            "endcard_text": "FULL VIDEO ON YOUTUBE",
        },
    }

    # 5 scenes, 4 beats & 4 images each = 20 images, 176 words
    scenes_data = [
        # SC01
        {
            "id": "SC01",
            "title": "The Spiking Heartbeat Behind Silence",
            "purpose": "Hook on the 100+ BPM heart rate spike behind saying 'I am fine'.",
            "action": "Leo mutters 'I am fine' while heartbeat monitor spikes violently.",
            "setting": "Warm vertical watercolor dining nook.",
            "camera": "Vertical intimate close-up.",
            "narration": "When your partner mutters I am fine and turns away, their heart rate often spikes above one hundred beats per minute. That icy silence is not cold indifference; it is acute nervous system flooding.",
            "requirements": ["R01"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Visceral, urgent, eye-opening",
            "narrative_phase": "lived_friction",
            "narrative_situation": "hook_shock",
            "prompts": [
                ("SC01_I1", "Vertical 9:16 charcoal and watercolor illustration on cold-press paper #F7F0E4: Leo in sage sweater turning head away with clenched jaw, speech bubble saying 'I'M FINE', raw umber outlines #5B4636.", "burst", "full_scene"),
                ("SC01_I2", "Vertical close-up of a spiking red biometric heart monitor line jumping above 100 BPM on textured cotton rag paper #F7F0E4, watercolor wash.", "fast", "macro_detail"),
                ("SC01_I3", "Metaphorical sketch of Leo's chest encased in a transparent cracking glass ice block on cream paper #F7F0E4, dusty iris accents #CDB4DB.", "fast", "concept_metaphor"),
                ("SC01_I4", "Maya standing on the opposite edge of the frame with hands clasped in deep concern on textured rag paper #F7F0E4, terracotta wash #D97A54.", "normal", "full_scene"),
            ],
            "quotes": [
                "When your partner mutters I am fine and turns away,",
                "their heart rate often spikes above one hundred beats per minute.",
                "That icy silence is not cold indifference;",
                "it is acute nervous system flooding.",
            ],
        },
        # SC02
        {
            "id": "SC02",
            "title": "The Involuntary Emergency Shutdown",
            "purpose": "Deconstruct stonewalling as autonomic survival overload.",
            "action": "Autonomic flooding shutting down communication while partner panics.",
            "setting": "Abstract internal physiological space.",
            "camera": "Vertical split comparative view.",
            "narration": "Gottman's research proves that stonewalling is an involuntary survival shutdown. Meanwhile, their sudden withdrawal sounds like a catastrophic abandonment siren to the anxious partner, who pursues harder out of desperate fear.",
            "requirements": ["R02"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Illuminating, somatic, balanced",
            "narrative_phase": "empirical_conflict",
            "narrative_situation": "empirical_mechanism",
            "prompts": [
                ("SC02_I1", "Vertical drawing of sympathetic neural wires glowing with red heat as blood rushes to muscles on cold-press paper #F7F0E4, botanical ink lines.", "fast", "macro_detail"),
                ("SC02_I2", "A heavy wooden portcullis dropping down between the couple, severing verbal dialogue on textured paper #F7F0E4, charcoal hatching.", "normal", "concept_metaphor"),
                ("SC02_I3", "Maya's heart illustrated as a glowing lighthouse signaling in a wild foggy storm on cream paper #F7F0E4, muted rose wash #F7C6C7.", "normal", "concept_metaphor"),
                ("SC02_I4", "Maya taking a desperate forward step while Leo braces against an invisible glass wall on textured rag paper #F7F0E4.", "hold", "full_scene"),
            ],
            "quotes": [
                "Gottman's research proves that stonewalling is an involuntary survival shutdown.",
                "Meanwhile, their sudden withdrawal sounds like a catastrophic abandonment siren",
                "to the anxious partner,",
                "who pursues harder out of desperate fear.",
            ],
        },
        # SC03
        {
            "id": "SC03",
            "title": "The Fallacy of Forced Talking",
            "purpose": "Editorial commentary on the futility of talking through flooding.",
            "action": "Words colliding like fiery arrows while empathy centers stay dark.",
            "setting": "Stormy abstract watercolor space.",
            "camera": "Direct vertical perspective.",
            "narration": "Demanding answers while flooded detonates the conversation. The pursuer chases connection while the distancer fights for survival. Conventional advice to just talk it out fails because a flooded brain cannot process empathy.",
            "requirements": ["R03"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Decisive, incisive, compassionate",
            "narrative_phase": "structural_model",
            "narrative_situation": "editorial_commentary",
            "prompts": [
                ("SC03_I1", "Two speech bubbles colliding like fragile porcelain teacups, shattering into charcoal fragments on cold-press paper #F7F0E4.", "slow", "concept_metaphor"),
                ("SC03_I2", "Diptych sketch: pursuer swimming desperately toward shore on left; distancer retreating into a deep cave on right, textured paper #F7F0E4.", "normal", "full_scene"),
                ("SC03_I3", "A torn relationship guidebook falling apart into loose watercolor leaves on warm cotton paper #F7F0E4, raw umber shading #5B4636.", "slow", "concept_metaphor"),
                ("SC03_I4", "A dimmed brain icon with a red lock symbol across prefrontal empathy lobes on cold-press paper #F7F0E4, >=60% negative space.", "hold", "macro_detail"),
            ],
            "quotes": [
                "Demanding answers while flooded detonates the conversation.",
                "The pursuer chases connection while the distancer fights for survival.",
                "Conventional advice to just talk it out fails",
                "because a flooded brain cannot process empathy.",
            ],
        },
        # SC04
        {
            "id": "SC04",
            "title": "The Timed Return Protocol",
            "purpose": "Demonstrate the 20-minute timed return contract in action.",
            "action": "Leo pointing to clock; Maya taking a calming breath; safe space opens.",
            "setting": "Restorative, calming watercolor atmosphere.",
            "camera": "Vertical medium two-shot.",
            "narration": "Break the trap with a twenty-minute timed return contract. The overwhelmed partner promises an exact timestamp to resume talking. Certainty calms the anxious alarm, while space allows avoidant heart rates to reset safely.",
            "requirements": ["R04"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Tactical, calming, restorative",
            "narrative_phase": "actionable_resolution",
            "narrative_situation": "actionable_resolution",
            "prompts": [
                ("SC04_I1", "Vertical sketch of an elegant 20-minute sand hourglass glowing with warm botanical sage wash #5D8A72 on cold-press paper #F7F0E4.", "burst", "concept_metaphor"),
                ("SC04_I2", "Leo holding up a small pocket watch, speaking gently with palm outstretched toward Maya on textured rag paper #F7F0E4.", "fast", "full_scene"),
                ("SC04_I3", "The red abandonment alarm bell above Maya dissolving into calm blue morning dew on cream paper #F7F0E4, soft charcoal lines.", "normal", "concept_metaphor"),
                ("SC04_I4", "Leo taking a slow deep breath by an open window as his pulse monitor drops back into serene green baseline on paper #F7F0E4.", "hold", "full_scene"),
            ],
            "quotes": [
                "Break the trap with a twenty-minute timed return contract.",
                "The overwhelmed partner promises an exact timestamp to resume talking.",
                "Certainty calms the anxious alarm,",
                "while space allows avoidant heart rates to reset safely.",
            ],
        },
        # SC05
        {
            "id": "SC05",
            "title": "The De-escalation Script & Bridge",
            "purpose": "Cliffhanger peak on de-escalation phrases, YouTube bridge, and closing CTA.",
            "action": "Hands meeting at table; transition to channel endcard.",
            "setting": "Warm glowing kitchen table with blooming botanical accents.",
            "camera": "Vertical cinematic tilt into channel branding.",
            "narration": "What exact three-word phrase allows an avoidant partner to pause without triggering abandonment panic? Watch the complete guide to healthy attachment on Kindred Sketch YouTube. Share this with someone whose bond you cherish and want to understand better.",
            "requirements": ["R05"],
            "character_ids": ["CH01"],
            "source_ids": ["SRC01"],
            "tone": "Enchanting, curious, deeply caring",
            "narrative_phase": "cliffhanger_spinoff",
            "narrative_situation": "cta_close",
            "prompts": [
                ("SC05_I1", "Vertical sketch of an ancient parchment letter with three glowing blank word slots surrounded by tender green vines on cold-press paper #F7F0E4.", "normal", "macro_detail"),
                ("SC05_I2", "Leo and Maya seated together in warm golden candlelight at the kitchen table, hands resting peacefully side by side on paper #F7F0E4.", "slow", "full_scene"),
                ("SC05_I3", "A hand-painted channel card showing Leo and Maya walking through an autumn park on textured cotton rag paper #F7F0E4, sage and terracotta washes.", "hold", "full_scene"),
                ("SC05_I4", "Vertical channel endcard on cold-press watercolor paper #F7F0E4 with delicate botanical leaves and hand-lettered text in upper third: 'KINDRED SKETCH'.", "hold", "full_scene", True),
            ],
            "quotes": [
                "What exact three-word phrase allows an avoidant partner to pause without triggering abandonment panic?",
                "Watch the complete guide to healthy attachment on Kindred Sketch YouTube.",
                "Share this with someone whose bond you cherish",
                "and want to understand better.",
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
                preserve="Warm charcoal-pencil and botanical watercolor aesthetic, cold-press rag paper #F7F0E4, Leo in sage sweater and Maya in terracotta cardigan, raw umber outlines #5B4636.",
                change=f"Progress to beat {p_id} showing {desc[:60]}...",
                reason=f"Visualize relationship dynamic progression for {sc_id} beat {i+1}.",
                tempo=tempo,
                situation=sc_data["narrative_situation"],
                motion_prompt="Smooth 2D watercolor animation. Subtle charcoal sketch line shifts, organic watercolor bleeding gently across cold-press paper, zero lip-sync, intimate tender character micro-movements.",
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
            {"requirement_id": "R01", "scene_id": "SC01", "quote": "When your partner mutters I am fine and turns away, their heart rate often spikes above one hundred beats per minute."},
            {"requirement_id": "R02", "scene_id": "SC02", "quote": "Gottman's research proves that stonewalling is an involuntary survival shutdown."},
            {"requirement_id": "R03", "scene_id": "SC03", "quote": "Conventional advice to just talk it out fails because a flooded brain cannot process empathy."},
            {"requirement_id": "R04", "scene_id": "SC04", "quote": "Break the trap with a twenty-minute timed return contract."},
            {"requirement_id": "R05", "scene_id": "SC05", "quote": "Watch the complete guide to healthy attachment on Kindred Sketch YouTube."},
        ],
        "outline": outline["outline"],
        "claims": [
            {
                "scene_id": "SC01",
                "quote": "When your partner mutters I am fine and turns away, their heart rate often spikes above one hundred beats per minute.",
                "language": "en",
                "source_id": "SRC01",
                "fact": "Stonewalling occurs when heart rate surpasses one hundred beats per minute during marital dispute.",
            }
        ],
        "revision_response": [],
        "open_questions": [],
    }

    return job_id, brief, outline, competitor_research, content
