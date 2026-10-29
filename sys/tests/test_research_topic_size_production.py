"""Production verification tests for Research Topic Size explainer (research-topic-size-16x9)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from content.builders.build_research_topic_size_jobs import (
    CHANNEL_PILLAR_RESEARCH_GUIDE,
)
from content.research_story_architect import (
    check_packaging_and_localization,
    compute_brief_hash,
    validate_production_bundle,
)
from content_contract import validate_brief, validate_content
from flow_prompts import find_visual_cliche
from flow_prompts.compiler import find_laziness_pattern
from narration_pauses import PAUSE_RE, SENTENCE_RE
from scripts.visual_quality import (
    check_abstract_card_clustering,
    check_atomic_variation_continuity,
    check_character_breathing_room,
    check_excessive_variation_streak,
    check_setting_description_verbosity,
    check_ungrounded_environment_scenes,
)
from tools.script_cadence_checker import ScriptCadenceChecker, count_syllables
from tools.script_diversity_linter import clean_sentence, lint_script
from tools.vn_text_normalizer import enforce_tts_normalization_gate

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"


class ResearchTopicSizeProductionTests(unittest.TestCase):
    def setUp(self):
        self.run_16x9 = SYS_DIR / "runs/research-topic-size-16x9"
        self.run_9x16 = SYS_DIR / "runs/research-topic-size-9x16"
        self.bp_16x9 = SYS_DIR / "content/blueprints/research-topic-size-16x9"
        self.bp_9x16 = SYS_DIR / "content/blueprints/research-topic-size-9x16"
        self.all_pkgs = (self.run_16x9, self.run_9x16, self.bp_16x9, self.bp_9x16)
        self.checker = ScriptCadenceChecker(nominal_rate=4.0)

    def test_package_files_exist(self):
        """Assert all required Schema 3.0 package artifacts and draft files exist with non-zero size."""
        required_files = (
            "brief.json",
            "content.json",
            "script.json",
            "cadence_report.json",
            "draft/outline.json",
            "draft/content.json",
        )
        for pkg in self.all_pkgs:
            for fname in required_files:
                fpath = pkg / fname
                self.assertTrue(fpath.is_file(), f"Missing {fname} in {pkg}")
                self.assertGreater(fpath.stat().st_size, 0, f"Empty file {fname} in {pkg}")

    def test_schema_3_contracts_16x9(self):
        """Verify 16:9 explainer conforms 100% to Schema 3.0 contracts and bundle validation."""
        for pkg in (self.run_16x9, self.bp_16x9):
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            self.assertEqual(b.get("schema_version"), "3.0")
            self.assertEqual(c.get("schema_version"), "3.0")

            expected_hash = compute_brief_hash(b)
            self.assertEqual(c["brief_hash"], expected_hash, f"Brief hash mismatch in {pkg}")

            validate_brief(SYS_DIR, b)
            validate_content(SYS_DIR, b, 1, c["brief_hash"], c)

            valid, errors = validate_production_bundle(SYS_DIR, b, c)
            self.assertTrue(valid, f"Bundle validation failed in {pkg}: {errors}")
            self.assertEqual(len(errors), 0)

    def test_schema_3_contracts_9x16(self):
        """Verify 9:16 mobile short conforms 100% to Schema 3.0 contracts and bundle validation."""
        for pkg in (self.run_9x16, self.bp_9x16):
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            self.assertEqual(b.get("schema_version"), "3.0")
            self.assertEqual(c.get("schema_version"), "3.0")

            expected_hash = compute_brief_hash(b)
            self.assertEqual(c["brief_hash"], expected_hash, f"Brief hash mismatch in {pkg}")

            validate_brief(SYS_DIR, b)
            validate_content(SYS_DIR, b, 1, c["brief_hash"], c)

            valid, errors = validate_production_bundle(SYS_DIR, b, c)
            self.assertTrue(valid, f"Bundle validation failed in {pkg}: {errors}")
            self.assertEqual(len(errors), 0)

    def test_packaging_and_localization_contracts(self):
        """Assert packaging adheres to channel pillar, title length, uppercase thumbnail spec, and VN localization."""
        for pkg in self.all_pkgs:
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            self.assertIn("packaging", b)
            pkg_data = b["packaging"]
            self.assertLessEqual(len(pkg_data["youtube_title"]), 55)
            self.assertEqual(pkg_data["youtube_title"], "Đừng Chọn Đề Tài NCKH Quá Lớn")
            self.assertEqual(pkg_data["channel_pillar"], CHANNEL_PILLAR_RESEARCH_GUIDE)
            self.assertEqual(pkg_data["funnel_tier"], "tier_1_broad")
            self.assertIn("thumbnail_spec", pkg_data)
            thumb = pkg_data["thumbnail_spec"]
            self.assertEqual(thumb["text_overlay"], "BỚT THAM LẠI")
            self.assertEqual(len(thumb["text_overlay"].split()), 3)
            self.assertTrue(thumb["text_overlay"].isupper())

            # Full audit with scenes and opening hook inspection
            warnings = check_packaging_and_localization(b, scenes=c["scenes"], check_opening_hook=True)
            self.assertEqual(len(warnings), 0, f"Packaging & localization warnings in {pkg}: {warnings}")

    def test_cadence_and_dead_air_16x9(self):
        """Verify 16:9 cadence, zero dead air, zero cadence warnings, and SC01 hook invariants."""
        for pkg in (self.run_16x9, self.bp_16x9):
            script = json.loads((pkg / "script.json").read_text(encoding="utf-8"))
            res = self.checker.check_scenes(script)
            self.assertEqual(res["status"], "PASS")
            self.assertEqual(res["warnings_count"], 0)
            self.assertLessEqual(res["max_drift"], 0.3)
            self.assertEqual(len(script), 16)

            # SC01 hook invariant: zero [pause:...] and hook <= 18 syl
            self.assertNotIn("[pause:", script[0]["narration"])
            first_sentence = SENTENCE_RE.split(script[0]["narration"])[0].strip()
            hook_syl = count_syllables(first_sentence, lang="vi")
            self.assertLessEqual(hook_syl, 18, f"SC01 hook has {hook_syl} syl > 18: {first_sentence}")
            self.assertEqual(first_sentence, "Tên đề tài nghiên cứu quá rộng sẽ bị thầy cô gạch ngay.")

            # All spoken sentences must be <= 20 syllables
            for sc in script:
                sc_id = sc["id"]
                raw_narr = sc["narration"]
                clean_narr = PAUSE_RE.sub(" ", raw_narr).strip()
                for sent in SENTENCE_RE.split(clean_narr):
                    s = sent.strip()
                    if not s:
                        continue
                    cnt = count_syllables(s, lang="vi")
                    self.assertLessEqual(cnt, 20, f"Sentence too long in {sc_id} ({cnt} syl > 20): {s!r}")

    def test_cadence_and_dead_air_9x16(self):
        """Verify 9:16 cadence, zero dead air, zero cadence warnings, and SC01 hook invariants."""
        for pkg in (self.run_9x16, self.bp_9x16):
            script = json.loads((pkg / "script.json").read_text(encoding="utf-8"))
            res = self.checker.check_scenes(script)
            self.assertEqual(res["status"], "PASS")
            self.assertEqual(res["warnings_count"], 0)
            self.assertLessEqual(res["max_drift"], 0.3)
            self.assertEqual(len(script), 6)

            # SC01 hook invariant: zero [pause:...] and hook <= 18 syl
            self.assertNotIn("[pause:", script[0]["narration"])
            first_sentence = SENTENCE_RE.split(script[0]["narration"])[0].strip()
            hook_syl = count_syllables(first_sentence, lang="vi")
            self.assertLessEqual(hook_syl, 18, f"SC01 hook has {hook_syl} syl > 18: {first_sentence}")
            self.assertEqual(first_sentence, "Tên đề tài nghiên cứu quá rộng sẽ bị thầy cô gạch ngay.")

            # All spoken sentences must be <= 20 syllables
            for sc in script:
                sc_id = sc["id"]
                raw_narr = sc["narration"]
                clean_narr = PAUSE_RE.sub(" ", raw_narr).strip()
                for sent in SENTENCE_RE.split(clean_narr):
                    s = sent.strip()
                    if not s:
                        continue
                    cnt = count_syllables(s, lang="vi")
                    self.assertLessEqual(cnt, 20, f"Sentence too long in {sc_id} ({cnt} syl > 20): {s!r}")

    def test_script_diversity_and_chronology(self):
        """Verify scripts pass script_diversity_linter with 0 violations."""
        for pkg in self.all_pkgs:
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            claim_facts = {clean_sentence(f) for src in b.get("sources", []) for f in src.get("facts", [])}
            claim_facts.update(clean_sentence(cl.get("fact", "")) for cl in c.get("claims", []) if cl.get("fact"))
            claim_facts.update(clean_sentence(cl.get("quote", "")) for cl in c.get("claims", []) if cl.get("quote"))

            res = lint_script(c["scenes"], claim_facts=claim_facts, topic_title=b.get("topic", ""))
            self.assertEqual(len(res["violations"]), 0, f"Diversity violations in {pkg}: {res['violations']}")

    def test_visual_contracts_and_breathing_room(self):
        """Verify settings verbosity <= 8 words, character breathing room, and flat canvas."""
        banned_room_words = ("room", "interior", "bedroom", "coffee corner", "desktop workspace", "office")
        for pkg in self.all_pkgs:
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            scenes = c["scenes"]

            # 1. Setting brevity <= 8 words
            verbosity_errs = check_setting_description_verbosity(scenes, max_words=10)
            self.assertEqual(len(verbosity_errs), 0, f"Setting verbosity in {pkg}: {verbosity_errs}")
            for sc in scenes:
                word_count = len(sc["setting"].split())
                self.assertLessEqual(word_count, 8, f"Setting > 8 words in {sc['id']}: {sc['setting']}")
                setting_lower = sc["setting"].casefold()
                for banned in banned_room_words:
                    self.assertNotIn(banned, setting_lower, f"Banned room interior word '{banned}' in {sc['id']} setting: {sc['setting']}")

            # 2. Character streak and 30% rest beats
            breathing_errs = check_character_breathing_room(scenes)
            self.assertEqual(len(breathing_errs), 0, f"Breathing room errors in {pkg}: {breathing_errs}")

            # 3. Consecutive variations <= 2
            streak_errs = check_excessive_variation_streak(scenes, max_streak=2)
            self.assertEqual(len(streak_errs), 0, f"Variation streak errors in {pkg}: {streak_errs}")

            # 4. Abstract card clustering <= 2
            card_errs = check_abstract_card_clustering(scenes)
            self.assertEqual(len(card_errs), 0, f"Abstract card clustering in {pkg}: {card_errs}")

            # 5. Ungrounded environment shots
            ungrounded_errs = check_ungrounded_environment_scenes(scenes)
            self.assertEqual(len(ungrounded_errs), 0, f"Ungrounded environment errors in {pkg}: {ungrounded_errs}")

            # 6. Atomic variation continuity
            continuity_errs = check_atomic_variation_continuity(scenes)
            self.assertEqual(len(continuity_errs), 0, f"Atomic variation continuity errors in {pkg}: {continuity_errs}")

    def test_full_frame_visual_prompt_hygiene(self):
        """Verify 0 visual clichés and 0 laziness patterns in compiled image descriptions."""
        for pkg in self.all_pkgs:
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            for sc in c["scenes"]:
                for img in sc.get("images", []):
                    desc = img.get("description", "")
                    cliche = find_visual_cliche(desc)
                    self.assertIsNone(cliche, f"Visual cliché '{cliche}' found in {img.get('id')}: {desc}")
                    laziness = find_laziness_pattern(desc, version="1.7.0")
                    self.assertIsNone(laziness, f"Laziness pattern '{laziness}' found in {img.get('id')}: {desc}")

    def test_tts_normalization_gate(self):
        """Assert Vietnamese TTS phonetic normalization gate passes cleanly."""
        for pkg in self.all_pkgs:
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            for sc in c["scenes"]:
                normalized = enforce_tts_normalization_gate(sc["narration"])
                self.assertIsNotNone(normalized)
                self.assertGreater(len(normalized), 0)

    def test_duration_bounds_and_narrative_floor(self):
        """Verify video duration and syllable floor invariants for both 16:9 and 9:16 packages."""
        for pkg in (self.run_16x9, self.bp_16x9):
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            cadence = json.loads((pkg / "cadence_report.json").read_text(encoding="utf-8"))

            total_sylls = cadence["total_actual_syllables"]
            self.assertGreaterEqual(total_sylls, 1800, f"Narrative floor violated in {pkg}: {total_sylls} < 1800 syl")

            total_dur = cadence["total_duration"]
            min_dur = b["duration"]["min_seconds"]
            max_dur = b["duration"]["max_seconds"]
            self.assertGreaterEqual(total_dur, min_dur, f"Duration too short in {pkg}: {total_dur} < {min_dur}")
            self.assertLessEqual(total_dur, max_dur, f"Duration too long in {pkg}: {total_dur} > {max_dur}")

        for pkg in (self.run_9x16, self.bp_9x16):
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            cadence = json.loads((pkg / "cadence_report.json").read_text(encoding="utf-8"))

            total_dur = cadence["total_duration"]
            min_dur = b["duration"]["min_seconds"]
            max_dur = b["duration"]["max_seconds"]
            self.assertGreaterEqual(total_dur, min_dur, f"Duration too short in {pkg}: {total_dur} < {min_dur}")
            self.assertLessEqual(total_dur, max_dur, f"Duration too long in {pkg}: {total_dur} > {max_dur}")


if __name__ == "__main__":
    unittest.main()
