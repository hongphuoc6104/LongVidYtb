#!/usr/bin/env python3
"""Unit and integration test suite for the 8-chapter / 48-scene Academic Research & Knowledge Decoding 13m blueprint."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

from build_academic_research_paradox_13m import (  # noqa: E402
    CHAPTER_METADATA,
    RAW_SCENES_DATA,
    build_multi_chapter_bundle,
    create_academic_research_13m_topic,
    get_academic_sources,
    get_required_points,
)
from content_contract import validate_brief, validate_content  # noqa: E402
from research_story_architect import (  # noqa: E402
    DEFAULT_CHANNEL_PILLAR,
    build_brief_v3,
    build_content_v3,
    build_short_spinoff_topics,
    check_packaging_and_localization,
    compute_brief_hash,
    generate_script_json,
    write_production_package,
)
from script_cadence_checker import ScriptCadenceChecker, count_syllables  # noqa: E402
from script_diversity_linter import lint_script  # noqa: E402


class TestAcademicResearchParadox13m(unittest.TestCase):
    """Verify the 8-chapter / 48-scene Academic Research & Knowledge Decoding blueprint and 3-Tier Spin-offs."""

    def setUp(self):
        self.topic = create_academic_research_13m_topic()
        self.brief = build_brief_v3(self.topic)
        self.brief_hash = compute_brief_hash(self.brief)
        self.content = build_content_v3(self.topic, self.brief, self.brief_hash)

    def test_chapter_scene_and_spoken_facts_invariants(self):
        self.assertEqual(len(CHAPTER_METADATA), 8)
        self.assertEqual(len(RAW_SCENES_DATA), 48)
        self.assertEqual(len(self.topic.scenes), 48)
        self.assertEqual(len(get_required_points()), 8)

        sources = get_academic_sources()
        self.assertEqual(len(sources), 8)
        total_facts = 0
        for src in sources:
            for f in src["facts"]:
                total_facts += 1
                self.assertLessEqual(count_syllables(f, lang="vi"), 20)
        self.assertEqual(total_facts, 16)

    def test_schema_3_packaging_and_localization_compliance(self):
        validate_brief(SYS_DIR, self.brief)
        validate_content(SYS_DIR, self.brief, 1, self.brief_hash, self.content)

        self.assertEqual(self.brief["channel_pillar"], DEFAULT_CHANNEL_PILLAR)
        self.assertLessEqual(len(self.brief["youtube_title"]), 55)
        self.assertEqual(self.brief["thumbnail_spec"]["text_overlay"], "BIẾT TÍNH ≠ HIỂU!")
        warns = check_packaging_and_localization(self.brief, scenes=self.topic.scenes, check_opening_hook=True)
        self.assertEqual(warns, [])

    def test_strict_cadence_and_diversity_linter_across_48_scenes(self):
        checker = ScriptCadenceChecker(
            forbid_opening_pause=True,
            max_opening_hook_syllables=18,
            max_sentence_syllables=25,
            max_clause_syllables=18,
            max_dramatic_pauses=4,
        )
        rep = checker.check_scenes(generate_script_json(self.topic))
        self.assertEqual(rep["status"], "PASS", f"Cadence warnings: {rep}")
        self.assertEqual(rep["warnings_count"], 0)
        self.assertLessEqual(rep["max_drift"], 0.25)
        self.assertGreaterEqual(rep["total_duration"], 660.0)
        self.assertLessEqual(rep["total_duration"], 840.0)

        lint_res = lint_script(
            [{"scene_id": s.scene_id, "chapter": (i // 6) + 1, "narration": s.narration} for i, s in enumerate(self.topic.scenes)],
            enforce_rhythm_variance=True,
        )
        self.assertEqual(lint_res["status"], "PASS", f"Linter violations: {lint_res}")
        self.assertEqual(lint_res["total_violations"], 0)

    def test_dual_zone_cue_window_allocation_and_3_tier_spinoffs(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            pkg_res = write_production_package(tmp_path / "run", self.topic, system_root=SYS_DIR, include_spinoffs=True)
            self.assertTrue(pkg_res["valid_contracts"])
            self.assertEqual(len(pkg_res["spinoff_packages"]), 3)

            bundle_res = build_multi_chapter_bundle(tmp_path / "bundle", self.topic)
            self.assertGreaterEqual(bundle_res["total_shots"], 250)

            manifest = json.loads(Path(bundle_res["manifest_json"]).read_text(encoding="utf-8"))
            for shot in manifest["shots"]:
                if shot["pacing_zone"] == "danger_zone_15s":
                    self.assertLessEqual(shot["hold_duration"], 1.80)
                else:
                    self.assertLessEqual(shot["hold_duration"], 3.75)

            spinoffs = build_short_spinoff_topics(self.topic, max_spinoffs=3)
            tiers = [sp.packaging.funnel_tier for sp in spinoffs]
            self.assertEqual(tiers, ["tier_1_broad", "tier_2_mid", "tier_3_conversion"])


if __name__ == "__main__":
    unittest.main()
