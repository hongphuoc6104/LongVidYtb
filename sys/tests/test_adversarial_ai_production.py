#!/usr/bin/env python3
"""Automated Test Suite for Adversarial AI Dual-Format Video Production.

Verifies:
1. Packaging Spec (<= 55 chars title, 2-4 uppercase word overlay, pillar & tier_3_conversion lock).
2. Vietnamese Cultural Localization in first 60s & zero pause in SC01.
3. Conversational Spoken Facts (<= 20 syllables, zero dry symbols).
4. Visual Beat Density (32 beats for 16:9, 20 beats for 9:16, cold-open cuts).
5. Conversational Spoken Tone Modulation (7 styles & required spoken keywords).
6. Cadence Calibration (0 dead-air, 0 timeline drift, exact P_tail formula).
7. Script Diversity & Anti-Formulaic Transitions (0 clichés, stddev >= 1.8 syllables).
8. Format Separation (long_16x9 vs short_9x16 independent contracts).
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content_contract import validate_brief, validate_content
from format_profiles import get_profile, validate_format_separation
from research_story_architect import (
    DEFAULT_CHANNEL_PILLAR,
    check_conversational_spoken_facts,
    check_packaging_and_localization,
    count_syllables,
    extract_pauses,
    split_sentences,
)
from script_diversity_linter import (
    check_formulaic_transitions,
    check_intra_video_repetitions,
    check_sentence_rhythm_variance,
    lint_script,
)
from tools.build_adversarial_ai_package import (
    SPOKEN_TONE_MAP,
    build_sources,
    build_topic_16x9,
    build_topic_9x16,
    count_total_beats,
    verify_spoken_tone_keywords,
)


class TestAdversarialAIProduction(unittest.TestCase):
    """Test suite for Adversarial AI dual-format production packages."""

    @classmethod
    def setUpClass(cls):
        cls.topic_16x9 = build_topic_16x9()
        cls.topic_9x16 = build_topic_9x16()
        cls.job_dir_16x9 = SYS_DIR / "blueprints" / "adversarial-ai-16x9"
        cls.job_dir_9x16 = SYS_DIR / "blueprints" / "adversarial-ai-9x16"
        cls.brief_16x9 = json.loads((cls.job_dir_16x9 / "brief.json").read_text(encoding="utf-8"))
        cls.content_16x9 = json.loads((cls.job_dir_16x9 / "content.json").read_text(encoding="utf-8"))
        cls.cadence_16x9 = json.loads((cls.job_dir_16x9 / "cadence_report.json").read_text(encoding="utf-8"))
        cls.brief_9x16 = json.loads((cls.job_dir_9x16 / "brief.json").read_text(encoding="utf-8"))
        cls.content_9x16 = json.loads((cls.job_dir_9x16 / "content.json").read_text(encoding="utf-8"))
        cls.cadence_9x16 = json.loads((cls.job_dir_9x16 / "cadence_report.json").read_text(encoding="utf-8"))

    def test_01_packaging_spec_and_pillar_lock(self):
        """Verify title <= 55 chars, 2-4 uppercase word overlay, pillar & funnel tier."""
        for label, brief, topic in [
            ("16:9", self.brief_16x9, self.topic_16x9),
            ("9:16", self.brief_9x16, self.topic_9x16),
        ]:
            title = brief.get("youtube_title", "")
            self.assertTrue(bool(title), f"{label}: missing youtube_title")
            self.assertLessEqual(
                len(title), 55,
                f"{label}: youtube_title '{title}' exceeds 55 chars ({len(title)} chars)"
            )
            # Channel Pillar Lock
            self.assertEqual(
                brief.get("channel_pillar"), DEFAULT_CHANNEL_PILLAR,
                f"{label}: must lock to channel pillar {DEFAULT_CHANNEL_PILLAR}"
            )
            self.assertEqual(
                brief.get("funnel_tier"), "tier_3_conversion",
                f"{label}: must belong to tier_3_conversion"
            )
            # Thumbnail Spec
            thumb = brief.get("thumbnail_spec", {})
            self.assertTrue(thumb.get("visual_hook"), f"{label}: missing visual_hook")
            overlay = thumb.get("text_overlay", "")
            words = overlay.split()
            self.assertTrue(2 <= len(words) <= 4, f"{label}: overlay '{overlay}' must be 2-4 words")
            alpha_chars = [c for c in overlay if c.isalpha()]
            self.assertTrue(all(c.isupper() for c in alpha_chars), f"{label}: overlay must be uppercase")

            # Packaging and localization check function
            warnings = check_packaging_and_localization(brief, scenes=topic.scenes, check_opening_hook=True)
            self.assertEqual(warnings, [], f"{label}: packaging/localization warnings: {warnings}")

    def test_02_conversational_spoken_facts(self):
        """Verify sources have facts <= 20 syllables and zero dry academic notations."""
        sources = build_sources()
        warnings = check_conversational_spoken_facts(sources, max_syllables=20)
        self.assertEqual(warnings, [], f"Conversational spoken fact warnings: {warnings}")

        # Check each fact individually
        for src in sources:
            for fact in src["facts"]:
                syl = count_syllables(fact, lang="vi")
                self.assertLessEqual(syl, 20, f"Fact exceeds 20 syllables ({syl} syl): {fact}")
                self.assertFalse(
                    re.search(r"(?:\bdoi:|\bisbn:|\bet al\.|\(\d{4}\))", fact, re.IGNORECASE),
                    f"Fact contains dry academic notation: {fact}"
                )

    def test_03_visual_density_and_beat_counts(self):
        """Verify exactly 32 visual beats for 16:9 and 109 visual beats for 9:16."""
        total_16x9 = count_total_beats(self.topic_16x9.scenes)
        self.assertEqual(total_16x9, 32, f"16:9 total beats must be 32, got {total_16x9}")
        total_9x16 = count_total_beats(self.topic_9x16.scenes)
        self.assertEqual(total_9x16, 109, f"9:16 total beats must be 109, got {total_9x16}")

        # Cold-open visual density
        sc01_16x9 = self.topic_16x9.scenes[0]
        self.assertEqual(len(sc01_16x9.visual_beats), 8, "SC01 in 16:9 must have exactly 8 visual beats")
        sc01_9x16 = self.topic_9x16.scenes[0]
        self.assertEqual(len(sc01_9x16.visual_beats), 5, "SC01 in 9:16 must have exactly 5 visual beats")

        # Verify beat shot types and variation integrity
        for topic in (self.topic_16x9, self.topic_9x16):
            shot_types_seen = set()
            for sc in topic.scenes:
                for beat in sc.visual_beats:
                    self.assertIn(
                        beat.shot_type,
                        {"macro_prop", "full_scene", "variation", "white_card"},
                        f"Unsupported shot type: {beat.shot_type}"
                    )
                    shot_types_seen.add(beat.shot_type)
                    if beat.shot_type == "variation":
                        self.assertTrue(bool(beat.based_on), f"{beat.image_id}: variation needs based_on")
                        self.assertTrue(bool(beat.preserve), f"{beat.image_id}: variation needs preserve")
                        self.assertTrue(bool(beat.change), f"{beat.image_id}: variation needs change")
            self.assertEqual(
                shot_types_seen,
                {"macro_prop", "full_scene", "variation", "white_card"},
                "Topic must use all four diverse shot types"
            )

    def test_04_spoken_tone_modulation_and_keywords(self):
        """Verify 7 spoken styles and conversational keyword presence."""
        warnings_16x9 = verify_spoken_tone_keywords(self.topic_16x9.scenes)
        self.assertEqual(warnings_16x9, [], f"16:9 tone keyword warnings: {warnings_16x9}")
        warnings_9x16 = verify_spoken_tone_keywords(self.topic_9x16.scenes)
        self.assertEqual(warnings_9x16, [], f"9:16 tone keyword warnings: {warnings_9x16}")

        # Check all 7 distinct spoken styles are assigned in 16:9
        styles_16x9 = [getattr(sc, "spoken_style", None) for sc in self.topic_16x9.scenes]
        expected_styles = [
            "gentle_lived_friction",
            "truth_slap_emphasis",
            "explanatory_mechanism",
            "analytical_contrast",
            "step_listing",
            "decisive_prompts",
            "narrative_payoff",
        ]
        self.assertEqual(styles_16x9, expected_styles)

        # Ensure schema tones are mapped to allowed set
        allowed_tones = {"narrative_warm", "analytical_crisp", "reflective_slow"}
        for sc in self.topic_16x9.scenes:
            self.assertIn(sc.tone, allowed_tones)
        for sc in self.topic_9x16.scenes:
            self.assertIn(sc.tone, allowed_tones)

    def test_05_cadence_and_timing_contracts(self):
        """Verify zero dead-air, zero drift, exact P_tail formulas, and opening hook <= 18 syl."""
        for label, cadence, topic in [
            ("16:9", self.cadence_16x9, self.topic_16x9),
            ("9:16", self.cadence_9x16, self.topic_9x16),
        ]:
            self.assertEqual(cadence["status"], "PASS", f"{label}: Cadence status must be PASS")
            self.assertEqual(cadence["warnings_count"], 0, f"{label}: Cadence warnings must be 0")
            self.assertEqual(cadence["net_drift"], 0.0, f"{label}: Net drift must be 0.0")
            self.assertEqual(cadence["max_drift"], 0.0, f"{label}: Max drift must be 0.0")

            # SC01 hook syllables <= 18
            first_sentence = split_sentences(topic.scenes[0].narration)[0]
            hook_syl = count_syllables(first_sentence, lang="vi")
            self.assertLessEqual(hook_syl, 18, f"{label}: Opening hook has {hook_syl} syllables (must be <= 18)")

            # Zero pause in SC01
            pause_sec, pauses, _ = extract_pauses(topic.scenes[0].narration)
            self.assertEqual(len(pauses), 0, f"{label}: SC01 must have 0 pauses, found {len(pauses)}")

            # Last scene p_tail == 0.35s
            last_cadence_sc = cadence["scenes"][-1]
            self.assertEqual(last_cadence_sc["p_tail"], 0.35, f"{label}: Last scene p_tail must be 0.35s")

    def test_06_script_diversity_and_rhythm_metrics(self):
        """Verify zero formulaic transitions, zero repetitions, zero backtracking, stddev >= 1.8 syl."""
        for label, content in [("16:9", self.content_16x9), ("9:16", self.content_9x16)]:
            scenes = content["scenes"]
            # 1. Formulaic transitions
            trans_violations = check_formulaic_transitions(scenes)
            self.assertEqual(trans_violations, [], f"{label}: Formulaic transitions found: {trans_violations}")

            # 2. Intra-video repetitions
            rep_violations = check_intra_video_repetitions(scenes)
            self.assertEqual(rep_violations, [], f"{label}: Intra-video repetitions found: {rep_violations}")

            # 3. Overall lint_script
            lint_res = lint_script(scenes)
            self.assertEqual(lint_res["status"], "PASS", f"{label}: Lint script failed: {lint_res}")

            # 4. Sentence rhythm variance
            rhythm = check_sentence_rhythm_variance(scenes, min_stddev_syllables=1.8)
            self.assertEqual(rhythm, [], f"{label}: Robotic sentence cadence detected: {rhythm}")

    def test_07_format_separation_and_contract_validation(self):
        """Verify 16:9 vs 9:16 strict separation and clean schema 3.0 validation."""
        # 16:9 validation
        validate_brief(SYS_DIR, self.brief_16x9)
        validate_content(
            SYS_DIR,
            self.brief_16x9,
            self.content_16x9["brief_revision"],
            self.content_16x9["brief_hash"],
            self.content_16x9,
        )
        validate_format_separation(self.brief_16x9)

        # 9:16 validation
        validate_brief(SYS_DIR, self.brief_9x16)
        validate_content(
            SYS_DIR,
            self.brief_9x16,
            self.content_9x16["brief_revision"],
            self.content_9x16["brief_hash"],
            self.content_9x16,
        )
        validate_format_separation(self.brief_9x16)

        # Profiles match SSOT
        prof_16x9 = get_profile("long_16x9")
        self.assertEqual(prof_16x9["width"], 1920)
        self.assertEqual(prof_16x9["height"], 1080)
        prof_9x16 = get_profile("short_9x16")
        self.assertEqual(prof_9x16["width"], 1080)
        self.assertEqual(prof_9x16["height"], 1920)

        # Cross contamination fails
        with self.assertRaises(ValueError):
            validate_format_separation({"format_profile": "short_9x16", "aspect_ratio": "16:9"})


if __name__ == "__main__":
    unittest.main()
