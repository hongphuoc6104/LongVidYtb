"""Production verification tests for Reality Interface Paradox packages (16:9 and 9:16)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from content.builders.build_reality_interface_jobs import (
    build_topic_9x16,
    build_topic_16x9,
    export_package,
)
from content.research_story_architect import (
    DEFAULT_CHANNEL_PILLAR,
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


class RealityInterfaceParadoxProductionTests(unittest.TestCase):
    def setUp(self):
        self.run_16x9 = SYS_DIR / "runs/reality-interface-paradox-16x9"
        self.run_9x16 = SYS_DIR / "runs/reality-interface-paradox-9x16"
        self.bp_16x9 = SYS_DIR / "content/blueprints/reality-interface-paradox-16x9"
        self.bp_9x16 = SYS_DIR / "content/blueprints/reality-interface-paradox-9x16"
        self.all_pkgs = (self.run_16x9, self.run_9x16, self.bp_16x9, self.bp_9x16)
        self.checker = ScriptCadenceChecker(nominal_rate=4.0)

    def test_package_files_exist(self):
        """Assert all required Schema 3.0 package artifacts and draft files exist with non-zero size in runs and blueprints."""
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
        """Assert packaging adheres to channel pillar, title length, uppercase 4-word thumbnail spec, and VN localization."""
        for pkg in self.all_pkgs:
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            self.assertIn("packaging", b)
            pkg_data = b["packaging"]
            self.assertLessEqual(len(pkg_data["youtube_title"]), 55)
            self.assertEqual(pkg_data["channel_pillar"], DEFAULT_CHANNEL_PILLAR)
            self.assertEqual(pkg_data["funnel_tier"], "tier_1_broad")
            self.assertIn("thumbnail_spec", pkg_data)
            thumb = pkg_data["thumbnail_spec"]
            self.assertEqual(thumb["text_overlay"], "SỰ THẬT LÀ GIẢ")
            self.assertEqual(len(thumb["text_overlay"].split()), 4)
            self.assertTrue(thumb["text_overlay"].isupper())

            # Full audit with scenes and opening hook inspection
            warnings = check_packaging_and_localization(b, scenes=c["scenes"], check_opening_hook=True)
            self.assertEqual(len(warnings), 0, f"Packaging & localization warnings in {pkg}: {warnings}")

    def test_cadence_and_dead_air_16x9(self):
        """Verify 16:9 cadence, zero dead air, zero cadence warnings, and SC01 hook invariants across runs and blueprints."""
        for pkg in (self.run_16x9, self.bp_16x9):
            script = json.loads((pkg / "script.json").read_text(encoding="utf-8"))
            res = self.checker.check_scenes(script)
            self.assertEqual(res["status"], "PASS")
            self.assertEqual(res["warnings_count"], 0)
            self.assertLessEqual(res["max_drift"], 0.3)
            self.assertEqual(len(script), 18)

            # SC01 hook invariant: zero [pause:...] and hook <= 18 syl
            self.assertNotIn("[pause:", script[0]["narration"])
            first_sentence = SENTENCE_RE.split(script[0]["narration"])[0].strip()
            hook_syl = count_syllables(first_sentence, lang="vi")
            self.assertLessEqual(hook_syl, 18, f"SC01 hook has {hook_syl} syl > 18: {first_sentence}")

    def test_cadence_and_dead_air_9x16(self):
        """Verify 9:16 cadence, zero dead air, zero cadence warnings, and SC01 hook invariants across runs and blueprints."""
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

    def test_script_diversity_and_chronology(self):
        """Verify scripts pass script_diversity_linter with 0 violations across runs and blueprints."""
        for pkg in self.all_pkgs:
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            claim_facts = {clean_sentence(f) for src in b.get("sources", []) for f in src.get("facts", [])}
            claim_facts.update(clean_sentence(cl.get("fact", "")) for cl in c.get("claims", []) if cl.get("fact"))
            claim_facts.update(clean_sentence(cl.get("quote", "")) for cl in c.get("claims", []) if cl.get("quote"))

            res = lint_script(c["scenes"], claim_facts=claim_facts, topic_title=b.get("topic", ""))
            self.assertEqual(len(res["violations"]), 0, f"Diversity violations in {pkg}: {res['violations']}")

    def test_visual_contracts_and_breathing_room(self):
        """Verify settings verbosity <= 8 words, character breathing room, abstract card clustering <= 2, and clean flat canvas."""
        banned_room_words = ("room", "interior", "bedroom", "coffee corner", "desktop workspace", "office")
        for pkg in self.all_pkgs:
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            scenes = c["scenes"]

            # 1. Setting brevity <= 8 words (hard ceiling 10)
            verbosity_errs = check_setting_description_verbosity(scenes, max_words=10)
            self.assertEqual(len(verbosity_errs), 0, f"Setting verbosity in {pkg}: {verbosity_errs}")
            for sc in scenes:
                word_count = len(sc["setting"].split())
                self.assertLessEqual(word_count, 8, f"Setting > 8 words in {sc['id']}: {sc['setting']}")
                # Clean Minimalist Contract: Flat canvas (#FFFFFF or #F8F0DC), zero room interiors
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
            self.assertEqual(len(continuity_errs), 0, f"Variation continuity errors in {pkg}: {continuity_errs}")

    def test_duration_bounds_and_narrative_floor(self):
        """Assert actual narration duration is strictly inside brief bounds and 16x9 meets 1800 syl floor."""
        for pkg in (self.run_16x9, self.bp_16x9):
            b_16 = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            cad_16 = json.loads((pkg / "cadence_report.json").read_text(encoding="utf-8"))
            dur_16 = cad_16["total_duration"]
            self.assertGreaterEqual(dur_16, b_16["duration"]["min_seconds"])
            self.assertLessEqual(dur_16, b_16["duration"]["max_seconds"])
            self.assertGreaterEqual(cad_16["total_actual_syllables"], 1800, "16x9 floor >= 1,800 syllables not met")

        for pkg in (self.run_9x16, self.bp_9x16):
            b_9 = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            cad_9 = json.loads((pkg / "cadence_report.json").read_text(encoding="utf-8"))
            dur_9 = cad_9["total_duration"]
            self.assertGreaterEqual(dur_9, b_9["duration"]["min_seconds"])
            self.assertLessEqual(dur_9, b_9["duration"]["max_seconds"])

    def test_spoken_sentence_length_limits(self):
        """Verify spoken sentences in both 16x9 explainer and 9x16 short do not exceed 20 syllables."""
        for pkg in self.all_pkgs:
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            for sc in c["scenes"]:
                raw_text = PAUSE_RE.sub(" ", sc["narration"]).strip()
                sentences = [s.strip() for s in SENTENCE_RE.split(raw_text) if s.strip()]
                for s in sentences:
                    syl = count_syllables(s, lang="vi")
                    self.assertLessEqual(syl, 20, f"Spoken sentence in {sc['id']} ({pkg.name}) exceeds 20 syl ({syl}): {s!r}")

    def test_tts_phonetic_normalization_gate(self):
        """Ensure all scene narrations across runs and blueprints pass enforce_tts_normalization_gate cleanly."""
        for pkg in self.all_pkgs:
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            for sc in c["scenes"]:
                normalized = enforce_tts_normalization_gate(sc["narration"])
                self.assertTrue(len(normalized) > 0, f"Empty normalized narration in {sc['id']} ({pkg.name})")

    def test_sources_and_claim_facts_integrity(self):
        """Verify sources and claim facts match scientific literature across runs and blueprints."""
        for pkg in self.all_pkgs:
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            source_ids = {s["id"] for s in b["sources"]}
            self.assertEqual(source_ids, {"SRC01", "SRC02", "SRC03"}, f"Source IDs mismatch in {pkg}")

            all_source_facts = {f for s in b["sources"] for f in s["facts"]}
            scene_map = {sc["id"]: sc for sc in c["scenes"]}

            claims = c.get("claims", [])
            self.assertGreater(len(claims), 0, f"No claims found in {pkg}")
            for claim in claims:
                self.assertIn(claim["source_id"], source_ids, f"Invalid source_id {claim['source_id']} in {pkg}")
                self.assertIn(claim["scene_id"], scene_map, f"Invalid scene_id {claim['scene_id']} in {pkg}")
                sc = scene_map[claim["scene_id"]]
                self.assertIn(claim["quote"], sc["narration"], f"Quote {claim['quote']!r} not in scene {sc['id']} narration in {pkg}")
                self.assertIn(claim["fact"], all_source_facts, f"Claim fact {claim['fact']!r} not in sources in {pkg}")

    def test_export_package_roundtrip_tempdir(self):
        """Verify export_package works end-to-end in isolated temporary directories with valid outline drafts."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_16 = Path(tmp_dir) / "test-16x9"
            out_9 = Path(tmp_dir) / "test-9x16"
            res_16 = export_package(build_topic_16x9(), out_16)
            res_9 = export_package(build_topic_9x16(), out_9)

            self.assertTrue(res_16["valid_contracts"], res_16.get("contract_errors"))
            self.assertTrue(res_9["valid_contracts"], res_9.get("contract_errors"))

            self.assertTrue((out_16 / "draft/outline.json").is_file())
            self.assertTrue((out_16 / "draft/content.json").is_file())
            self.assertTrue((out_9 / "draft/outline.json").is_file())
            self.assertTrue((out_9 / "draft/content.json").is_file())

            outline_16 = json.loads((out_16 / "draft/outline.json").read_text(encoding="utf-8"))
            outline_9 = json.loads((out_9 / "draft/outline.json").read_text(encoding="utf-8"))
            self.assertEqual(len(outline_16["outline"]), 18)
            self.assertEqual(len(outline_9["outline"]), 6)

            # Ensure draft/content.json matches content.json
            self.assertEqual(
                (out_16 / "draft/content.json").read_text(encoding="utf-8"),
                (out_16 / "content.json").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                (out_9 / "draft/content.json").read_text(encoding="utf-8"),
                (out_9 / "content.json").read_text(encoding="utf-8"),
            )

    def test_visual_prompts_cliche_free_contract(self):
        """Verify that all visual descriptions, settings, and actions across both formats contain zero banned clichés."""
        for pkg in self.all_pkgs:
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            for sc in c["scenes"]:
                for field in ("setting", "action"):
                    val = sc.get(field, "")
                    cliche = find_visual_cliche(val)
                    self.assertIsNone(cliche, f"Found banned cliché {cliche} in {sc['id']} {field}: {val}")
                    lazy = find_laziness_pattern(val, version="1.7.0")
                    self.assertIsNone(lazy, f"Found banned laziness pattern {lazy} in {sc['id']} {field}: {val}")

                for im in sc.get("images", []):
                    desc = im.get("description", "")
                    cliche = find_visual_cliche(desc)
                    self.assertIsNone(cliche, f"Found banned cliché {cliche} in {im['id']} description: {desc}")
                    lazy = find_laziness_pattern(desc, version="1.7.0")
                    self.assertIsNone(lazy, f"Found banned laziness pattern {lazy} in {im['id']} description: {desc}")


if __name__ == "__main__":
    unittest.main()
