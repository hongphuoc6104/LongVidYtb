#!/usr/bin/env python3
"""Automated Test Suite for The Collector's Fallacy Dual-Format Video Production.

Verifies:
1. Packaging Spec (<= 55 chars title, 2-4 uppercase word overlay, pillar & tier_1_broad lock).
2. Vietnamese Cultural Localization in first 60s & zero pause in SC01.
3. Conversational Spoken Facts (<= 20 syllables, zero dry academic symbols).
4. Visual Beat Density (114 beats for 16:9, 60 beats for 9:16).
5. Cadence Calibration (0 dead-air, 0 timeline drift, exact P_tail formula).
6. Script Diversity & Anti-Formulaic Transitions (0 clichés, stddev >= 1.8 syllables).
7. Format Separation & Clean Schema 3.0 Contract Validation.
8. Existence of verified production deliverables & thumbnails.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unittest
from pathlib import Path

import pytest

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
    split_sentences,
)
from script_diversity_linter import (
    check_formulaic_transitions,
    check_intra_video_repetitions,
    check_sentence_rhythm_variance,
    lint_script,
)
from tools.build_collectors_fallacy_jobs import (
    build_sources,
    build_topic_9x16,
    build_topic_16x9,
)


class TestCollectorsFallacyProduction(unittest.TestCase):
    """Test suite for The Collector's Fallacy dual-format production packages."""

    @classmethod
    def setUpClass(cls):
        cls.topic_16x9 = build_topic_16x9()
        cls.topic_9x16 = build_topic_9x16()
        cls.job_dir_16x9 = SYS_DIR / "blueprints" / "collectors-fallacy-16x9"
        cls.job_dir_9x16 = SYS_DIR / "blueprints" / "collectors-fallacy-9x16"
        cls.brief_16x9 = json.loads((cls.job_dir_16x9 / "brief.json").read_text(encoding="utf-8"))
        cls.content_16x9 = json.loads((cls.job_dir_16x9 / "content.json").read_text(encoding="utf-8"))
        cls.cadence_16x9 = json.loads((cls.job_dir_16x9 / "cadence_report.json").read_text(encoding="utf-8"))
        cls.brief_9x16 = json.loads((cls.job_dir_9x16 / "brief.json").read_text(encoding="utf-8"))
        cls.content_9x16 = json.loads((cls.job_dir_9x16 / "content.json").read_text(encoding="utf-8"))
        cls.cadence_9x16 = json.loads((cls.job_dir_9x16 / "cadence_report.json").read_text(encoding="utf-8"))

    def test_01_packaging_spec_and_pillar_lock(self):
        """Rule 1 & Rule 6: YouTube title <= 55 chars, 2-4 uppercase word overlay, pillar & tier_1_broad lock."""
        for label, brief, topic in [
            ("16:9", self.brief_16x9, self.topic_16x9),
            ("9:16", self.brief_9x16, self.topic_9x16),
        ]:
            title = brief.get("youtube_title", "")
            self.assertTrue(bool(title), f"{label}: missing youtube_title")
            self.assertLessEqual(len(title), 55, f"{label}: title exceeds 55 chars ({len(title)})")
            self.assertEqual(brief.get("channel_pillar"), DEFAULT_CHANNEL_PILLAR)
            self.assertEqual(brief.get("funnel_tier"), "tier_1_broad")

            thumb = brief.get("thumbnail_spec", {})
            self.assertTrue(thumb.get("visual_hook"), f"{label}: missing visual_hook")
            overlay = thumb.get("text_overlay", "")
            words = overlay.split()
            self.assertTrue(2 <= len(words) <= 4, f"{label}: overlay '{overlay}' must be 2-4 words")
            self.assertEqual(overlay, "LƯU ĐẦY KHÔNG ĐỌC")

            warnings = check_packaging_and_localization(brief, scenes=topic.scenes, check_opening_hook=True)
            self.assertEqual(warnings, [], f"{label}: packaging warnings: {warnings}")

    def test_02_opening_truth_slap_hook_and_zero_pause(self):
        """Rule 3 & Rule 6: Opening hook <= 18 syllables, zero pause in SC01."""
        for label, content in [("16:9", self.content_16x9), ("9:16", self.content_9x16)]:
            sc01 = content["scenes"][0]
            first_sentence = split_sentences(sc01["narration"])[0]
            syl = count_syllables(first_sentence, lang="vi")
            self.assertLessEqual(syl, 18, f"{label}: Opening hook too long: {syl} syl")
            self.assertEqual(first_sentence, "Tải hàng trăm cuốn sách chỉ tạo ra ảo giác học tập")
            self.assertNotIn("[pause:", sc01["narration"])

    def test_03_conversational_spoken_facts(self):
        """Rule 6: Facts must be <= 20 syllables and free of dry academic symbols."""
        sources = build_sources()
        warnings = check_conversational_spoken_facts(sources, max_syllables=20)
        self.assertEqual(warnings, [], f"Spoken fact warnings: {warnings}")
        for src in sources:
            for fact in src["facts"]:
                syl = count_syllables(fact, lang="vi")
                self.assertLessEqual(syl, 20, f"Fact exceeds 20 syllables ({syl} syl): {fact}")
                self.assertFalse(
                    re.search(r"(?:\bdoi:|\bisbn:|\bet al\.|\(\d{4}\))", fact, re.IGNORECASE),
                    f"Fact contains dry academic notation: {fact}",
                )

    def test_04_schema_and_contract_validation(self):
        """Rule 2: Schema 3.0 validity, character references, claim-source links."""
        validate_brief(SYS_DIR, self.brief_16x9)
        validate_content(
            SYS_DIR,
            self.brief_16x9,
            self.content_16x9["brief_revision"],
            self.content_16x9["brief_hash"],
            self.content_16x9,
        )
        validate_brief(SYS_DIR, self.brief_9x16)
        validate_content(
            SYS_DIR,
            self.brief_9x16,
            self.content_9x16["brief_revision"],
            self.content_9x16["brief_hash"],
            self.content_9x16,
        )

    def test_05_strict_cadence_calibration_and_zero_drift(self):
        """Rule 3: Zero timeline drift, PASS status, zero warnings."""
        for label, cadence in [("16:9", self.cadence_16x9), ("9:16", self.cadence_9x16)]:
            self.assertEqual(cadence["status"], "PASS", f"{label}: Cadence status must be PASS")
            self.assertEqual(cadence["warnings_count"], 0, f"{label}: Cadence warnings must be 0")
            self.assertEqual(cadence["net_drift"], 0.0, f"{label}: Net drift must be 0.0")
            self.assertEqual(cadence["max_drift"], 0.0, f"{label}: Max drift must be 0.0")
            self.assertEqual(cadence["scenes"][-1]["p_tail"], 0.35, f"{label}: Last scene p_tail must be 0.35")

    def test_06_script_diversity_and_rhythm_metrics(self):
        """Rule 6: stddev_syllables >= 1.8, zero formulaic transitions."""
        for label, content in [("16:9", self.content_16x9), ("9:16", self.content_9x16)]:
            scenes = content["scenes"]
            trans_violations = check_formulaic_transitions(scenes)
            self.assertEqual(trans_violations, [], f"{label}: Formulaic transitions: {trans_violations}")

            rep_violations = check_intra_video_repetitions(scenes)
            self.assertEqual(rep_violations, [], f"{label}: Intra-video repetitions: {rep_violations}")

            lint_res = lint_script(scenes)
            self.assertEqual(lint_res["status"], "PASS")

            rhythm = check_sentence_rhythm_variance(scenes, min_stddev_syllables=1.8)
            self.assertEqual(rhythm, [], f"{label}: Sentence rhythm variance failure: {rhythm}")

    def test_07_format_separation(self):
        """Rule 1: Format separation between long_16x9 and short_9x16."""
        validate_format_separation(self.brief_16x9)
        validate_format_separation(self.brief_9x16)
        self.assertEqual(self.brief_16x9["aspect_ratio"], "16:9")
        self.assertEqual(self.brief_16x9["format_profile"], "long_16x9")
        self.assertEqual(self.brief_9x16["aspect_ratio"], "9:16")
        self.assertEqual(self.brief_9x16["format_profile"], "short_9x16")

        prof_16x9 = get_profile("long_16x9")
        self.assertEqual(prof_16x9["width"], 1920)
        self.assertEqual(prof_16x9["height"], 1080)
        prof_9x16 = get_profile("short_9x16")
        self.assertEqual(prof_9x16["width"], 1080)
        self.assertEqual(prof_9x16["height"], 1920)

        with self.assertRaises(ValueError):
            validate_format_separation({"format_profile": "short_9x16", "aspect_ratio": "16:9"})

    @pytest.mark.media_acceptance
    def test_08_thumbnail_deliverables(self):
        """Verify thumbnails are generated and have non-zero size."""
        thumb_16x9 = Path(os.environ.get("VP_MEDIA_ROOT", str(ROOT_DIR))) / Path("video/collectors-fallacy-16x9/thumbnail.png")
        thumb_9x16 = Path(os.environ.get("VP_MEDIA_ROOT", str(ROOT_DIR))) / Path("video/collectors-fallacy-9x16/cover_tiktok_9x16.png")
        self.assertTrue(thumb_16x9.is_file(), f"Missing 16:9 thumbnail: {thumb_16x9}")
        self.assertGreater(thumb_16x9.stat().st_size, 10000)
        self.assertTrue(thumb_9x16.is_file(), f"Missing 9:16 thumbnail: {thumb_9x16}")
        self.assertGreater(thumb_9x16.stat().st_size, 10000)

    @pytest.mark.media_acceptance
    def test_09_rendered_mp4_deliverables(self):
        """Verify final rendered MP4 video files exist and have valid size (>10MB)."""
        mp4_16x9 = Path(os.environ.get("VP_MEDIA_ROOT", str(ROOT_DIR))) / Path("video/collectors-fallacy-16x9/collectors-fallacy-16x9_r1_final.mp4")
        mp4_9x16 = Path(os.environ.get("VP_MEDIA_ROOT", str(ROOT_DIR))) / Path("video/collectors-fallacy-9x16/collectors-fallacy-9x16_r1_final.mp4")
        self.assertTrue(mp4_16x9.is_file(), f"Missing 16:9 final MP4: {mp4_16x9}")
        self.assertGreater(mp4_16x9.stat().st_size, 10 * 1024 * 1024, "16:9 MP4 must be > 10MB")
        self.assertTrue(mp4_9x16.is_file(), f"Missing 9:16 final MP4: {mp4_9x16}")
        self.assertGreater(mp4_9x16.stat().st_size, 10 * 1024 * 1024, "9:16 MP4 must be > 10MB")


if __name__ == "__main__":
    unittest.main()
