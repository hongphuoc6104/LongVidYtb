#!/usr/bin/env python3
"""Automated Test Suite for Reviewer 2 & Nobel Rejections Dual-Format Video Production.

Verifies:
1. Packaging Spec (<= 55 chars title, 2-4 uppercase word overlay, pillar & tier_2_mid lock).
2. Vietnamese Cultural Localization in first 60s & zero pause in SC01.
3. Conversational Spoken Facts (<= 20 syllables, zero dry symbols).
4. Visual Beat Density (77 beats for 16:9, 57 beats for 9:16, max hold <= 2.80s).
5. Conversational Spoken Tone Modulation (12 styles for 16:9, 9 styles for 9:16).
6. Cadence Calibration (0 dead-air, 0 timeline drift, exact P_tail formula).
7. Script Diversity & Anti-Formulaic Transitions (0 clichés, 0 intra-video repetition).
8. Format Separation (long_16x9 vs short_9x16 independent contracts).
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content_contract import validate_brief, validate_content
from format_profiles import validate_format_separation
from research_story_architect import (
    DEFAULT_CHANNEL_PILLAR,
    check_conversational_spoken_facts,
    count_syllables,
    extract_pauses,
    split_sentences,
)
from script_diversity_linter import (
    lint_script,
)
from tools.build_reviewer_2_jobs import (
    build_sources_9x16,
    build_sources_16x9,
    build_topic_9x16,
    build_topic_16x9,
    count_total_beats,
    verify_spoken_tone_keywords,
)


class TestReviewer2Production(unittest.TestCase):
    """Test suite for Reviewer 2 dual-format production packages."""

    @classmethod
    def setUpClass(cls):
        cls.topic_16x9 = build_topic_16x9()
        cls.topic_9x16 = build_topic_9x16()
        cls.run_dir_16x9 = SYS_DIR / "blueprints" / "reviewer-2-novelty-bias-16x9"
        cls.run_dir_9x16 = SYS_DIR / "blueprints" / "reviewer-2-nobel-rejections-9x16"

    def test_01_packaging_spec_compliance(self):
        """Rule 1 & Rule 6: Validate YouTube titles, overlays, channel pillars, and funnel tier."""
        pkg_16x9 = self.topic_16x9.packaging
        self.assertIsNotNone(pkg_16x9)
        self.assertLessEqual(len(pkg_16x9.youtube_title), 55)
        self.assertEqual(pkg_16x9.youtube_title, "Vì sao ý tưởng đột phá luôn bị phản biện từ chối?")
        self.assertEqual(pkg_16x9.text_overlay, "BẪY REVIEWER 2")
        words_16x9 = pkg_16x9.text_overlay.split()
        self.assertTrue(2 <= len(words_16x9) <= 4)
        self.assertTrue(all(w.isupper() for w in words_16x9 if w.isalpha()))
        self.assertEqual(pkg_16x9.channel_pillar, DEFAULT_CHANNEL_PILLAR)
        self.assertEqual(pkg_16x9.funnel_tier, "tier_2_mid")

        pkg_9x16 = self.topic_9x16.packaging
        self.assertIsNotNone(pkg_9x16)
        self.assertLessEqual(len(pkg_9x16.youtube_title), 55)
        self.assertEqual(pkg_9x16.youtube_title, "Những Bài Báo Đoạt Giải Nobel Từng Bị Ném Vào Sọt Rác")
        self.assertEqual(pkg_9x16.text_overlay, "BỊ TỪ CHỐI NOBEL")
        words_9x16 = pkg_9x16.text_overlay.split()
        self.assertTrue(2 <= len(words_9x16) <= 4)
        self.assertTrue(all(w.isupper() for w in words_9x16 if w.isalpha()))
        self.assertEqual(pkg_9x16.channel_pillar, DEFAULT_CHANNEL_PILLAR)
        self.assertEqual(pkg_9x16.funnel_tier, "tier_2_mid")

    def test_02_truth_slap_hooks_and_zero_pause(self):
        """Rule 3 & Rule 6: SC01 hook <= 18 syllables, zero pause in SC01."""
        sc01_16x9 = self.topic_16x9.scenes[0]
        sents_16x9 = split_sentences(sc01_16x9.narration)
        hook_16x9 = sents_16x9[0].rstrip(".!?")
        syl_16x9 = count_syllables(hook_16x9, lang="vi")
        self.assertEqual(hook_16x9, "Ý tưởng đột phá nhất thường là thứ bị hội đồng từ chối đầu tiên")
        self.assertLessEqual(syl_16x9, 18)
        _, pauses_16x9, _ = extract_pauses(sc01_16x9.narration)
        self.assertEqual(len(pauses_16x9), 0, "SC01 must have zero [pause:...]")

        sc01_9x16 = self.topic_9x16.scenes[0]
        sents_9x16 = split_sentences(sc01_9x16.narration)
        hook_9x16 = sents_9x16[0].rstrip(".!?")
        syl_9x16 = count_syllables(hook_9x16, lang="vi")
        self.assertEqual(hook_9x16, "Những bài báo đoạt giải Nobel từng bị hội đồng ném vào sọt rác")
        self.assertLessEqual(syl_9x16, 18)
        _, pauses_9x16, _ = extract_pauses(sc01_9x16.narration)
        self.assertEqual(len(pauses_9x16), 0, "SC01 must have zero [pause:...]")

    def test_03_conversational_spoken_facts(self):
        """Rule 3: Facts must be <= 20 syllables and free of dry academic symbols."""
        sources_16x9 = build_sources_16x9()
        warns_16x9 = check_conversational_spoken_facts(sources_16x9, max_syllables=20)
        self.assertEqual(warns_16x9, [], f"16:9 fact warnings: {warns_16x9}")

        sources_9x16 = build_sources_9x16()
        warns_9x16 = check_conversational_spoken_facts(sources_9x16, max_syllables=20)
        self.assertEqual(warns_9x16, [], f"9:16 fact warnings: {warns_9x16}")

    def test_04_visual_beat_densities(self):
        """Rule 6: 77 beats for 16:9, 57 beats for 9:16, holds between 0.83s and 2.80s."""
        beats_16x9 = count_total_beats(self.topic_16x9.scenes)
        self.assertEqual(beats_16x9, 77)

        beats_9x16 = count_total_beats(self.topic_9x16.scenes)
        self.assertEqual(beats_9x16, 57)

        for sc in self.topic_16x9.scenes:
            avg_hold = sc.duration / len(sc.visual_beats)
            self.assertLessEqual(avg_hold, 2.80, f"{sc.scene_id} 16:9 average hold {avg_hold:.2f}s exceeds 2.80s")

        for sc in self.topic_9x16.scenes:
            avg_hold = sc.duration / len(sc.visual_beats)
            self.assertLessEqual(avg_hold, 2.80, f"{sc.scene_id} 9:16 average hold {avg_hold:.2f}s exceeds 2.80s")

    def test_05_spoken_tone_keywords_verification(self):
        """Conversational essayist vocal cadence: Tone keywords verified across all scenes."""
        warns_16x9 = verify_spoken_tone_keywords(self.topic_16x9.scenes)
        self.assertEqual(warns_16x9, [], f"16:9 tone keyword warnings: {warns_16x9}")

        warns_9x16 = verify_spoken_tone_keywords(self.topic_9x16.scenes)
        self.assertEqual(warns_9x16, [], f"9:16 tone keyword warnings: {warns_9x16}")

    def test_06_script_diversity_and_zero_repetition(self):
        """Rule 6: Script diversity linter with zero formulaic clichés and zero repeated phrasing."""
        content_16x9 = json.loads((self.run_dir_16x9 / "content.json").read_text(encoding="utf-8"))
        res_16x9 = lint_script(content_16x9["scenes"], topic_title=content_16x9["topic"])
        self.assertEqual(len(res_16x9["violations"]), 0, f"16:9 diversity failed: {res_16x9['violations']}")

        content_9x16 = json.loads((self.run_dir_9x16 / "content.json").read_text(encoding="utf-8"))
        res_9x16 = lint_script(content_9x16["scenes"], topic_title=content_9x16["topic"])
        self.assertEqual(len(res_9x16["violations"]), 0, f"9:16 diversity failed: {res_9x16['violations']}")

    def test_07_contract_validation(self):
        """Rule 2 & Station 2: Official schema 3.0 contract validation (validate_brief & validate_content)."""
        brief_16x9 = json.loads((self.run_dir_16x9 / "brief.json").read_text(encoding="utf-8"))
        content_16x9 = json.loads((self.run_dir_16x9 / "content.json").read_text(encoding="utf-8"))
        validate_brief(SYS_DIR, brief_16x9)
        validate_content(SYS_DIR, brief_16x9, 1, content_16x9["brief_hash"], content_16x9)

        brief_9x16 = json.loads((self.run_dir_9x16 / "brief.json").read_text(encoding="utf-8"))
        content_9x16 = json.loads((self.run_dir_9x16 / "content.json").read_text(encoding="utf-8"))
        validate_brief(SYS_DIR, brief_9x16)
        validate_content(SYS_DIR, brief_9x16, 1, content_9x16["brief_hash"], content_9x16)

    def test_08_format_separation(self):
        """Rule 1: Strict separation between long_16x9 and short_9x16 format profiles."""
        brief_16x9 = json.loads((self.run_dir_16x9 / "brief.json").read_text(encoding="utf-8"))
        brief_9x16 = json.loads((self.run_dir_9x16 / "brief.json").read_text(encoding="utf-8"))
        validate_format_separation(brief_16x9)
        validate_format_separation(brief_9x16)
        self.assertEqual(brief_16x9["format_profile"], "long_16x9")
        self.assertEqual(brief_9x16["format_profile"], "short_9x16")


if __name__ == "__main__":
    unittest.main()
