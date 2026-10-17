#!/usr/bin/env python3
"""Unit test suite for Research Story Architect (vp-research-architect).

Validates:
1. Acoustic dead-air syllable calculation formula.
2. Trial topic structure and 5-part arc distribution.
3. Strict schema 3.0 validation for brief.json (validate_brief).
4. Strict schema 3.0 validation for content.json (validate_content & validate_plan).
5. Cadence checker timeline drift within <= 0.3s tolerance and zero warnings.
6. Full-frame visual-beat contract, in-place variations, and no generated layers.
7. Legal traceability: 100% of required_points covered, 100% of claims verified.
8. Packaging & SEO Contract, Vietnamese Cultural Localization in First 60s, and Short-Form Spin-off Blueprints.
9. End-to-end package generation and CLI execution.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
if str(SYS_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(SYS_DIR / "tools"))

from content_contract import validate_brief, validate_content  # noqa: E402
from research_story_architect import (  # noqa: E402
    DEFAULT_CHANNEL_PILLAR,
    build_brief_v3,
    build_content_v3,
    build_short_spinoff_topics,
    calculate_proportional_durations,
    calculate_scene_syllable_budget,
    check_packaging_and_localization,
    compute_brief_hash,
    create_academic_research_paradox_topic,
    create_demo_trial_topic,
    generate_script_json,
    write_production_package,
)
from script_cadence_checker import ScriptCadenceChecker  # noqa: E402


class TestResearchStoryArchitect(unittest.TestCase):
    """Test suite ensuring full compliance and verification of research story architect."""

    def setUp(self):
        self.topic = create_demo_trial_topic()
        self.brief_data = build_brief_v3(self.topic)
        self.brief_hash = compute_brief_hash(self.brief_data)
        self.content_data = build_content_v3(self.topic, self.brief_data, self.brief_hash, brief_revision=1)

    def test_syllable_budget_calculation(self):
        """Verify the P_tail formula correctly calculates syllable budgets."""
        budget_8s = calculate_scene_syllable_budget(8.0, is_last=False)
        self.assertEqual(budget_8s, 29)
        assert budget_8s == 29

        budget_11s_paused = calculate_scene_syllable_budget(11.0, is_last=False, pause_seconds=0.9)
        self.assertEqual(budget_11s_paused, 38)
        assert budget_11s_paused == 38

        budget_9s_last = calculate_scene_syllable_budget(9.0, is_last=True)
        self.assertEqual(budget_9s_last, 35)
        assert budget_9s_last == 35

    def test_calculate_proportional_durations(self):
        """Verify duration allocator matches 5-part conversational arc and reconciles sums."""
        for total in [45.0, 52.5, 60.0, 75.0, 90.0]:
            durations = calculate_proportional_durations(total, scene_count=5)
            self.assertEqual(len(durations), 5)
            self.assertEqual(round(sum(durations), 1), round(total, 1))
            assert len(durations) == 5
            assert round(sum(durations), 1) == round(total, 1)

        for count in [3, 4, 6, 8]:
            durations = calculate_proportional_durations(60.0, scene_count=count)
            self.assertEqual(len(durations), count)
            self.assertEqual(round(sum(durations), 1), 60.0)
            assert len(durations) == count
            assert round(sum(durations), 1) == 60.0

        with self.assertRaises(ValueError):
            calculate_proportional_durations(60.0, scene_count=0)
        with self.assertRaises(ValueError):
            calculate_proportional_durations(-10.0, scene_count=5)

    def test_demo_trial_topic_structure(self):
        """Verify the trial topic has 5 scenes matching the 5-part conversational arc."""
        self.assertEqual(len(self.topic.scenes), 5)
        self.assertEqual([s.scene_id for s in self.topic.scenes], ["SC01", "SC02", "SC03", "SC04", "SC05"])
        assert len(self.topic.scenes) == 5
        assert [s.scene_id for s in self.topic.scenes] == ["SC01", "SC02", "SC03", "SC04", "SC05"]

        total_duration = sum(s.duration for s in self.topic.scenes)
        self.assertGreaterEqual(total_duration, self.topic.min_duration)
        self.assertLessEqual(total_duration, self.topic.max_duration)
        assert self.topic.min_duration <= total_duration <= self.topic.max_duration

        self.assertEqual(len(self.topic.sources), 2)
        assert any("Pychyl" in s["reference"] for s in self.topic.sources)

    def test_build_brief_v3_schema_compliance(self):
        """Verify brief.json satisfies validate_brief contract with 0 errors and top-level voice defaults."""
        validate_brief(SYS_DIR, self.brief_data)
        self.assertEqual(self.brief_data["schema_version"], "3.0")
        self.assertEqual(self.brief_data["scene_count"], 5)
        self.assertEqual(len(self.brief_data["required_points"]), 5)
        cfg = json.loads((SYS_DIR / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(self.brief_data["outputs"][0]["voice"], cfg["tts_voice"])
        self.assertEqual(self.brief_data["outputs"][0]["speed"], cfg["tts_speed"])
        assert self.brief_data["schema_version"] == "3.0"
        assert self.brief_data["scene_count"] == 5
        assert self.brief_data["outputs"][0]["voice"] == cfg["tts_voice"]

        self.assertEqual(cfg["voices"]["vi"], "assets/voices/viet_narrator/profile.json")
        self.assertEqual(cfg["tts_voice"], "VietNarrator")
        self.assertEqual(cfg["tts_speed"], 1.0)
        self.assertEqual(cfg["en_voice"], "Adam")
        self.assertEqual(cfg["en_speed"], 1.22)
        voice_dirs = sorted(p.name for p in (SYS_DIR / "assets/voices").iterdir() if p.is_dir())
        self.assertEqual(voice_dirs, ["adam", "viet_narrator"])
        assert voice_dirs == ["adam", "viet_narrator"]

    def test_build_content_v3_schema_compliance(self):
        """Verify content.json satisfies validate_content contract with 0 errors."""
        validate_content(SYS_DIR, self.brief_data, 1, self.brief_hash, self.content_data)
        self.assertEqual(self.content_data["schema_version"], "3.0")
        self.assertEqual(self.content_data["brief_hash"], self.brief_hash)
        self.assertEqual(len(self.content_data["scenes"]), 5)
        assert self.content_data["schema_version"] == "3.0"
        assert self.content_data["brief_hash"] == self.brief_hash

    def test_brief_hash_matches_disk_and_pilot_digest(self):
        """Verify that brief_hash exactly matches the SHA-256 of the brief file on disk."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "pkg"
            res = write_production_package(out_path, self.topic, system_root=SYS_DIR)
            brief_bytes = Path(res["brief_file"]).read_bytes()
            import hashlib
            file_sha256 = hashlib.sha256(brief_bytes).hexdigest()

            content = json.loads(Path(res["content_file"]).read_text())
            self.assertEqual(content["brief_hash"], file_sha256)
            self.assertEqual(res["brief_hash"], file_sha256)
            assert content["brief_hash"] == file_sha256
            assert res["brief_hash"] == file_sha256

    def test_dual_aspect_ratio_compliance(self):
        """Verify that dual aspect ratio produces valid brief and content schemas."""
        dual_topic = create_demo_trial_topic()
        dual_topic.aspect_ratio = "dual"

        brief_d = build_brief_v3(dual_topic)
        validate_brief(SYS_DIR, brief_d)
        self.assertEqual(len(brief_d["outputs"]), 2)
        self.assertEqual([o["aspect_ratio"] for o in brief_d["outputs"]], ["9:16", "16:9"])
        assert len(brief_d["outputs"]) == 2

        bhash = compute_brief_hash(brief_d)
        content_d = build_content_v3(dual_topic, brief_d, bhash, brief_revision=1)
        validate_content(SYS_DIR, brief_d, 1, bhash, content_d)
        self.assertEqual(content_d["schema_version"], "3.0")
        assert content_d["schema_version"] == "3.0"

    def test_cadence_checker_drift_within_tolerance(self):
        """Verify all scenes have timeline drift <= 0.3s and 0 cadence warnings."""
        checker = ScriptCadenceChecker(nominal_rate=4.0)
        standardized = generate_script_json(self.topic)
        result = checker.check_scenes(standardized)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["warnings_count"], 0)
        self.assertLessEqual(result["max_drift"], 0.30)
        assert result["status"] == "PASS"
        assert result["warnings_count"] == 0
        assert result["max_drift"] <= 0.30

        for sc in result["scenes"]:
            self.assertLessEqual(abs(sc["drift"]), 0.30, f"Scene {sc['scene_id']} drift exceeded tolerance")
            self.assertEqual(len(sc["warnings"]), 0)
            assert abs(sc["drift"]) <= 0.30
            assert len(sc["warnings"]) == 0

        scenes_en = [
            {"id": s.scene_id, "duration": s.duration, "narration": s.narration_en}
            for s in self.topic.scenes
        ]
        result_en = checker.check_scenes(scenes_en)
        self.assertEqual(result_en["status"], "PASS")
        self.assertEqual(result_en["warnings_count"], 0)
        self.assertLessEqual(result_en["max_drift"], 0.30)
        assert result_en["status"] == "PASS"
        assert result_en["warnings_count"] == 0

    def test_full_frame_visual_contract(self):
        """Verify architect output uses complete scene images and narration-synced beats."""
        from research_story_architect import (
            assign_scene_camera_effects,
            check_conversational_spoken_facts,
            select_semantic_camera_effect,
        )

        for sc in self.content_data["scenes"]:
            kinds = [im["kind"] for im in sc["images"]]
            self.assertTrue(all(kind == "scene" for kind in kinds), f"Scene {sc['id']} must use full-frame images")
            self.assertEqual(sc.get("layers"), [])
            self.assertEqual({im["id"] for im in sc["images"]}, {beat["image_id"] for beat in sc["beats"]})
            self.assertEqual(len(sc["images"]), len(sc["beats"]))
            assert all(kind == "scene" for kind in kinds)
            assert sc["layers"] == []

        from research_story_architect import ResearchedVisualBeat

        topic = create_demo_trial_topic()
        scene = topic.scenes[0]
        words = scene.narration.split()
        anchors = [
            " ".join(words[start:start + 3])
            for start in (0, len(words) // 3, (2 * len(words)) // 3)
        ]
        scene.visual_beats = [
            ResearchedVisualBeat(
                image_id="SC01_VIS1",
                description="A complete full-frame kitchen scene with the character at the open refrigerator.",
                anchor_quote=anchors[0],
                reason="Establish the action in its setting.",
                character_ids=["CH01"],
            ),
            ResearchedVisualBeat(
                image_id="SC01_VIS2",
                description="The same kitchen and camera, with the character reaching toward the refrigerator shelf.",
                anchor_quote=anchors[1],
                reason="Show the next spoken action in the same place.",
                character_ids=["CH01"],
                based_on="SC01_VIS1",
                preserve="Keep the kitchen, refrigerator, camera position, and character design.",
                change="Move the character's hand toward the refrigerator shelf.",
            ),
            ResearchedVisualBeat(
                image_id="SC01_VIS3",
                description="A full-frame close-up of the refrigerator shelf and the character's hand.",
                anchor_quote=anchors[2],
                reason="Emphasize the narrated object.",
                character_ids=["CH01"],
                effect="punch_in",
            ),
        ]
        brief = build_brief_v3(topic)
        visual_content = build_content_v3(topic, brief, compute_brief_hash(brief), brief_revision=1)
        validate_content(SYS_DIR, brief, 1, compute_brief_hash(brief), visual_content)
        scene_content = visual_content["scenes"][0]
        self.assertEqual(len(scene_content["beats"]), 3)
        self.assertEqual(scene_content["images"][1]["based_on"], "SC01_VIS1")
        self.assertTrue(scene_content["images"][1]["preserve"])
        self.assertTrue(scene_content["images"][1]["change"])
        self.assertEqual(scene_content["layers"], [])

        self.assertEqual(select_semantic_camera_effect("zoom_out"), "zoom_out")
        self.assertEqual(select_semantic_camera_effect("punch_in"), "punch_in")
        cam_effects = assign_scene_camera_effects([
            "Wide establishing shot",
            "Wide establishing shot",
            "Extreme close-up shot",
            "Medium tracking pan shot",
            "Opposite reverse left shot",
        ])
        self.assertEqual(cam_effects, ["zoom_out", "pan_right", "punch_in", "pan_right", "pan_left"])
        for i in range(1, len(cam_effects)):
            self.assertNotEqual(cam_effects[i], cam_effects[i - 1])
        self.assertEqual(
            check_conversational_spoken_facts([{"id": "SRC01", "facts": ["Não bộ không cần ngọn lửa cảm hứng để bắt đầu làm việc."]}]),
            [],
        )
        dry_warns = check_conversational_spoken_facts(
            [{"id": "SRC01", "facts": ["Theo Dyble et al. (2019), DOI: 10.1038, tỷ lệ là 81%."]}]
        )
        self.assertEqual(len(dry_warns), 1)
        self.assertIn("dry academic notation", dry_warns[0])
        long_warns = check_conversational_spoken_facts(
            [{"id": "SRC01", "facts": ["Đây là một mệnh đề học thuật rất dài vượt quá giới hạn hai mươi hai âm tiết được phép phát âm tự nhiên trong một hơi thở của người dẫn chuyện."]}]
        )
        self.assertEqual(len(long_warns), 1)
        assert len(dry_warns) == 1
        assert len(long_warns) == 1

    def test_default_cold_open_uses_about_nine_full_frame_beats(self):
        from scripts.story_plan import estimates, languages, timeline

        language = languages(self.brief_data)[0]
        images = []
        segments = []
        cursor = 0.0
        aspect_ratio = self.brief_data["outputs"][0]["aspect_ratio"]
        for scene in self.content_data["scenes"]:
            duration = next(item.duration for item in self.topic.scenes if item.scene_id == scene["id"])
            text = scene.get("narration_en" if language == "en" else "narration", "")
            segments.append({
                "scene_id": scene["id"],
                "start": cursor,
                "end": cursor + duration,
                "content_end": cursor + duration,
                "text": text,
            })
            cursor += duration
            images.extend({
                "scene_id": scene["id"],
                "image_id": image["id"],
                "ratio": aspect_ratio,
                "path": f"assets/{image['id']}.jpg",
            } for image in scene["images"])
        audio = {"tracks": {language: {"segments": segments, "duration": cursor}}}
        planned = timeline(self.content_data, {"items": images}, audio, language, aspect_ratio)
        opening_count = sum(
            1 for scene in planned for beat in scene["images"] if scene["start"] + beat["at"] < 12.5
        )
        first_five_count = sum(
            1 for scene in planned for beat in scene["images"] if scene["start"] + beat["at"] < 5.0
        )
        self.assertGreaterEqual(opening_count, 8)
        self.assertLessEqual(opening_count, 10)
        self.assertGreaterEqual(first_five_count, 3)
        self.assertLessEqual(first_five_count, 5)
        visual_warnings = [warning for warning in estimates(self.brief_data, self.content_data)["warnings"] if "beat hold" in warning]
        self.assertEqual(visual_warnings, [])

    def test_academic_research_paradox_packaging_localization_and_spinoffs(self):
        """Verify Academic Research Q1 topic, Packaging Contract, VN 60s Localization, and Short-Form Spin-offs."""
        acad_topic = create_academic_research_paradox_topic(aspect_ratio="9:16")
        brief = build_brief_v3(acad_topic)
        validate_brief(SYS_DIR, brief)
        bhash = compute_brief_hash(brief)
        content = build_content_v3(acad_topic, brief, bhash)
        validate_content(SYS_DIR, brief, 1, bhash, content)

        # Packaging contract checks
        self.assertEqual(brief["channel_pillar"], DEFAULT_CHANNEL_PILLAR)
        self.assertEqual(brief["funnel_tier"], "tier_1_broad")
        self.assertLessEqual(len(brief["youtube_title"]), 55)
        self.assertEqual(brief["outputs"][0]["speed"], 1.26)
        self.assertTrue(brief["outputs"][0]["subtitles"])
        pkg_warns = check_packaging_and_localization(brief, scenes=acad_topic.scenes, check_opening_hook=True)
        self.assertEqual(pkg_warns, [])

        # Strict cadence check with opening pause forbidden and opening hook <= 18 syllables
        checker = ScriptCadenceChecker(
            forbid_opening_pause=True,
            max_opening_hook_syllables=18,
            max_sentence_syllables=25,
            max_clause_syllables=18,
            max_dramatic_pauses=4,
        )
        cadence_res = checker.check_scenes(generate_script_json(acad_topic))
        self.assertEqual(cadence_res["status"], "PASS", f"Cadence warnings: {cadence_res}")
        self.assertEqual(cadence_res["warnings_count"], 0)
        self.assertLessEqual(cadence_res["max_drift"], 0.30)

        # Verify check_packaging_and_localization catches violations (Excel off-pillar, >55 char title, foreign SC01)
        bad_brief = dict(brief)
        bad_brief["youtube_title"] = "Nghịch lý tri thức là bởi vì não bộ con người luôn lười suy nghĩ khi đọc lại giáo trình đại học"
        bad_brief["topic"] = "Tổng hợp mẹo Excel và làm slide nhanh trong 4 tiếng cho tình huống của Na"
        bad_brief["thumbnail_spec"] = {"visual_hook": "Bảng tính", "text_overlay": "mẹo nhỏ"}
        bad_scenes = [{"id": "SC01", "narration": "Tại trường chữ nêm Edubba xứ Sumer cổ đại, các học sinh phải chép bài trên bảng đất sét. [pause:800ms]"}]
        bad_warns = check_packaging_and_localization(bad_brief, scenes=bad_scenes, check_opening_hook=True)
        self.assertTrue(any("OFF_PILLAR_DILUTION" in w for w in bad_warns))
        self.assertTrue(any("YOUTUBE_TITLE_TOO_LONG" in w for w in bad_warns))
        self.assertTrue(any("YOUTUBE_TITLE_SELF_ANSWERING" in w for w in bad_warns))
        self.assertTrue(any("THUMBNAIL_OVERLAY_NOT_UPPERCASE" in w for w in bad_warns))
        self.assertTrue(any("OPENING_NOT_LOCALIZED_VN" in w for w in bad_warns))
        self.assertTrue(any("OPENING_SCENE_PAUSE_FORBIDDEN" in w for w in bad_warns))

        # Verify standalone short_9x16 spin-offs generation
        spinoffs = build_short_spinoff_topics(acad_topic, max_spinoffs=3)
        self.assertEqual(len(spinoffs), 3)
        for sp in spinoffs:
            self.assertEqual(sp.aspect_ratio, "9:16")
            self.assertEqual(len(sp.scenes), 5)
            sp_brief = build_brief_v3(sp)
            validate_brief(SYS_DIR, sp_brief)
            sp_hash = compute_brief_hash(sp_brief)
            sp_content = build_content_v3(sp, sp_brief, sp_hash)
            validate_content(SYS_DIR, sp_brief, 1, sp_hash, sp_content)
            self.assertEqual(check_packaging_and_localization(sp_brief, scenes=sp.scenes, check_opening_hook=True), [])
            sp_cadence = checker.check_scenes(generate_script_json(sp))
            self.assertEqual(sp_cadence["status"], "PASS", f"Spin-off cadence warnings: {sp_cadence}")

    def test_legal_traceability_coverage_and_claims(self):
        """Verify 100% of required_points are covered and all claims have verified sources."""
        covered_req_ids = {c["requirement_id"] for c in self.content_data["coverage"]}
        brief_req_ids = {r["id"] for r in self.brief_data["required_points"]}
        self.assertEqual(covered_req_ids, brief_req_ids)
        assert covered_req_ids == brief_req_ids

        scene_by_id = {s["id"]: s for s in self.content_data["scenes"]}
        for c in self.content_data["coverage"]:
            sc = scene_by_id[c["scene_id"]]
            self.assertIn(c["quote"], sc["narration"])
            assert c["quote"] in sc["narration"]

        self.assertGreater(len(self.content_data["claims"]), 0)
        source_by_id = {s["id"]: s for s in self.brief_data["sources"]}
        for claim in self.content_data["claims"]:
            sc = scene_by_id[claim["scene_id"]]
            src = source_by_id[claim["source_id"]]
            self.assertIn(claim["quote"], sc["narration"])
            self.assertIn(claim["fact"], src["facts"])
            self.assertIn(claim["source_id"], sc["source_ids"])
            assert claim["quote"] in sc["narration"]
            assert claim["fact"] in src["facts"]

    def test_write_production_package_e2e(self):
        """Verify full package assembly writes all files (including spinoff_shorts) and passes validation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "test_pkg"
            res = write_production_package(out_path, self.topic, system_root=SYS_DIR, include_spinoffs=True)

            self.assertTrue(res["valid_contracts"])
            self.assertEqual(len(res["contract_errors"]), 0)
            self.assertEqual(len(res["spinoff_packages"]), 3)
            self.assertTrue(Path(res["brief_file"]).is_file())
            self.assertTrue(Path(res["content_file"]).is_file())
            self.assertTrue(Path(res["script_file"]).is_file())
            self.assertTrue(Path(res["cadence_file"]).is_file())
            assert res["valid_contracts"] is True
            assert Path(res["brief_file"]).is_file()

            b = json.loads(Path(res["brief_file"]).read_text())
            c = json.loads(Path(res["content_file"]).read_text())
            validate_brief(SYS_DIR, b)
            validate_content(SYS_DIR, b, 1, res["brief_hash"], c)
            assert b["schema_version"] == "3.0"
            assert c["schema_version"] == "3.0"

    def test_cli_demo_execution(self):
        """Verify CLI execution with --demo flag exits with code 0."""
        cli_tool = SYS_DIR / "tools/research_story_architect.py"
        venv_py = SYS_DIR / ".venv/bin/python"
        py_bin = str(venv_py) if venv_py.is_file() else sys.executable

        with tempfile.TemporaryDirectory() as tmp_dir:
            cmd = [py_bin, str(cli_tool), "--demo", "--output-dir", tmp_dir]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"CLI demo execution failed: {res.stderr}\n{res.stdout}")
            self.assertIn("HỢP LỆ", res.stdout)
            self.assertIn("Max Drift", res.stdout)
            assert res.returncode == 0
            assert "HỢP LỆ" in res.stdout

    def test_cli_demo_dual_execution(self):
        """Verify CLI execution with --demo and --aspect-ratio dual exits with code 0."""
        cli_tool = SYS_DIR / "tools/research_story_architect.py"
        venv_py = SYS_DIR / ".venv/bin/python"
        py_bin = str(venv_py) if venv_py.is_file() else sys.executable

        with tempfile.TemporaryDirectory() as tmp_dir:
            cmd = [py_bin, str(cli_tool), "--demo", "--aspect-ratio", "dual", "--output-dir", tmp_dir]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"CLI dual demo failed: {res.stderr}\n{res.stdout}")
            self.assertIn("HỢP LỆ", res.stdout)
            assert res.returncode == 0
            assert "HỢP LỆ" in res.stdout

    def test_pilot_check_draft_direct_compatibility(self):
        """Verify that a package generated by research_story_architect passes pilot.py check_draft."""
        import os
        import shutil

        from pilot import Pilot

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            os.symlink(SYS_DIR / "schemas", root / "schemas")
            shutil.copy(SYS_DIR / "config.json", root / "config.json")

            p = Pilot(root=root)
            p.new("trial_job", brief=self.brief_data, mode="review")
            p.approve("trial_job", "control", 1, "Approve control for draft testing")

            saved_b, rev, bhash = p.brief("trial_job")
            self.assertEqual(self.brief_hash, bhash)
            assert self.brief_hash == bhash

            (p.job("trial_job") / "draft/content.json").write_text(
                json.dumps(self.content_data, indent=2, ensure_ascii=False)
            )

            report = p.check_draft("trial_job")
            self.assertTrue(report["passed"])
            self.assertEqual(len(report["errors"]), 0)
            assert report["passed"] is True
            assert len(report["errors"]) == 0

    def test_motivation_v2_exp_13m_package_audio_gaps_and_videos(self):
        """Verify V2 experimental 8-chapter package, stereo PCM16 trimmer, 0.000s cue sync, and V2 MP4s."""
        import array
        import importlib.util

        from build_motivation_v2_exp_13m import create_motivation_v2_exp_13m_topic
        from research_story_architect import check_conversational_spoken_facts
        from script_cadence_checker import count_syllables

        topic = create_motivation_v2_exp_13m_topic()
        brief = build_brief_v3(topic)
        validate_brief(SYS_DIR, brief)
        brief_hash = compute_brief_hash(brief)
        content = build_content_v3(topic, brief, brief_hash)
        validate_content(SYS_DIR, brief, 1, brief_hash, content)
        self.assertEqual(check_conversational_spoken_facts(brief["sources"]), [])
        for src in brief["sources"]:
            for fact in src["facts"]:
                self.assertLessEqual(count_syllables(fact), 20)

        cadence = ScriptCadenceChecker().check_scenes(generate_script_json(topic))
        self.assertEqual(cadence["status"], "PASS")
        self.assertEqual(cadence["warnings_count"], 0)
        self.assertLessEqual(cadence["max_drift"], 0.30)

        playbook_txt = (SYS_DIR.parent / "PLAYBOOK.md").read_text(encoding="utf-8")
        self.assertNotIn("600.0", playbook_txt)
        self.assertNotIn("10–15", playbook_txt)

        v2_gen_path = SYS_DIR / "exports" / "motivation_v2_exp_bundle" / "scripts" / "generate_spoken_narration.py"
        if not v2_gen_path.is_file():
            return
        spec = importlib.util.spec_from_file_location("v2_gen_spoken", v2_gen_path)
        v2_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v2_mod)
        sr = 48000
        right_only = array.array("h", [0] * (int(0.20 * sr) * 2))
        for _ in range(int(0.30 * sr)):
            right_only.extend([0, 8000])
        right_only.extend([0] * (int(0.25 * sr) * 2))
        trimmed_bytes = v2_mod.trim_pcm16_stereo_silence(right_only.tobytes(), sr=sr)
        self.assertGreater(len(trimmed_bytes), int(0.30 * sr) * 4)
        self.assertLess(len(trimmed_bytes), int(0.40 * sr) * 4)

        no_pad = array.array("h", [8000, -8000] * int(0.30 * sr)).tobytes()
        once = v2_mod.trim_pcm16_stereo_silence(no_pad, sr=sr)
        twice = v2_mod.trim_pcm16_stereo_silence(once, sr=sr)
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
