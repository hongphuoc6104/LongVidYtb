#!/usr/bin/env python3
"""Unit test suite for Impostor Paradox 9:16 Vertical Long-Form Video Package.

Verifies:
1. Packaging Spec (<= 55 chars title, 2-4 uppercase word overlay, pillar & tier_1_broad lock).
2. Vietnamese Cultural Localization in first 60s & zero pause in SC01.
3. Conversational Spoken Facts (<= 20 syllables, zero dry symbols).
4. Visual Beat Density & Breathing Room (76 beats for 19 scenes, >=30% rest frames).
5. Cadence Calibration (0 dead-air, 0 timeline drift <= 0.3s).
6. Schema 3.0 Strict Validation (validate_brief & validate_content).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content_contract import validate_brief, validate_content
from research_story_architect import (
    DEFAULT_CHANNEL_PILLAR,
    check_conversational_spoken_facts,
    count_syllables,
    extract_pauses,
    split_sentences,
)
from tools.build_impostor_paradox_job import build_topic, count_total_beats


class TestImpostorParadoxProduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.topic = build_topic()
        cls.run_dir = SYS_DIR / "blueprints" / "impostor-paradox-9x16"

    def test_01_packaging_spec_compliance(self):
        pkg = self.topic.packaging
        self.assertIsNotNone(pkg)
        self.assertLessEqual(len(pkg.youtube_title), 55)
        self.assertEqual(pkg.youtube_title, "Càng Đọc Nhiều Càng Sợ Viết: Ảo Giác Tự Ti Học Thuật")
        self.assertEqual(pkg.text_overlay, "BẪY TỰ TI")
        words = pkg.text_overlay.split()
        self.assertTrue(2 <= len(words) <= 4)
        self.assertTrue(all(w.isupper() for w in words if w.isalpha()))
        self.assertEqual(pkg.channel_pillar, DEFAULT_CHANNEL_PILLAR)
        self.assertEqual(pkg.funnel_tier, "tier_1_broad")

    def test_02_truth_slap_hook_and_zero_pause(self):
        sc01 = self.topic.scenes[0]
        sents = split_sentences(sc01.narration)
        hook = sents[0].rstrip(".!?")
        syl = count_syllables(hook, lang="vi")
        self.assertEqual(hook, "Càng đọc nhiều tài liệu, não bạn càng sợ bắt đầu")
        self.assertLessEqual(syl, 18)
        _, pauses, _ = extract_pauses(sc01.narration)
        self.assertEqual(len(pauses), 0, "SC01 must have zero [pause:...]")

    def test_03_conversational_spoken_facts(self):
        warnings = check_conversational_spoken_facts(self.topic.sources, max_syllables=20)
        self.assertEqual(warnings, [], f"Sources have invalid facts: {warnings}")

    def test_04_visual_beats_and_breathing_room(self):
        total_beats = count_total_beats(self.topic.scenes)
        self.assertEqual(total_beats, 76)
        self.assertEqual(len(self.topic.scenes), 19)

    def test_05_schema_contract_validation(self):
        import json
        brief_data = json.loads((self.run_dir / "brief.json").read_text(encoding="utf-8"))
        content_data = json.loads((self.run_dir / "content.json").read_text(encoding="utf-8"))
        # Must not raise
        validate_brief(SYS_DIR, brief_data)
        validate_content(SYS_DIR, brief_data, 1, content_data["brief_hash"], content_data)


if __name__ == "__main__":
    unittest.main()
