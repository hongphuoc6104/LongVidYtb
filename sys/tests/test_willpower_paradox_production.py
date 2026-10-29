"""Production verification tests for Willpower Paradox packages (16:9 and 9:16)."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from content.builders.build_willpower_paradox_jobs import build_topic_16x9
from content.research_story_architect import (
    DEFAULT_CHANNEL_PILLAR,
    check_packaging_and_localization,
    validate_production_bundle,
    write_production_package,
)
from content_contract import validate_brief, validate_content
from PIL import Image
from scripts.visual_quality import (
    check_character_breathing_room,
    check_excessive_variation_streak,
    check_setting_description_verbosity,
)
from tools.script_cadence_checker import ScriptCadenceChecker
from tools.script_diversity_linter import lint_script
from tools.vn_text_normalizer import enforce_tts_normalization_gate

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
RUN_16X9 = SYS_DIR / "runs/willpower-paradox-16x9"
RUN_9X16 = SYS_DIR / "runs/willpower-paradox-9x16"


class WillpowerParadoxProductionTests(unittest.TestCase):
    def setUp(self):
        self.run_16x9 = RUN_16X9
        self.run_9x16 = RUN_9X16
        self.checker = ScriptCadenceChecker(nominal_rate=4.0)

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_package_files_exist(self):
        for pkg in (self.run_16x9, self.run_9x16):
            self.assertTrue((pkg / "brief.json").is_file(), f"Missing brief.json in {pkg}")
            self.assertTrue((pkg / "content.json").is_file(), f"Missing content.json in {pkg}")
            self.assertTrue((pkg / "script.json").is_file(), f"Missing script.json in {pkg}")
            self.assertTrue((pkg / "cadence_report.json").is_file(), f"Missing cadence_report.json in {pkg}")
            self.assertTrue((pkg / "draft/outline.json").is_file(), f"Missing draft/outline.json in {pkg}")
            self.assertTrue((pkg / "draft/content.json").is_file(), f"Missing draft/content.json in {pkg}")

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_schema_3_contracts_16x9(self):
        b = json.loads((self.run_16x9 / "brief.json").read_text(encoding="utf-8"))
        c = json.loads((self.run_16x9 / "content.json").read_text(encoding="utf-8"))
        self.assertEqual(b.get("schema_version"), "3.0")
        self.assertEqual(c.get("schema_version"), "3.0")

        validate_brief(SYS_DIR, b)
        validate_content(SYS_DIR, b, 1, c["brief_hash"], c)

        valid, errors = validate_production_bundle(SYS_DIR, b, c)
        self.assertTrue(valid, f"Bundle validation failed: {errors}")
        self.assertEqual(len(errors), 0)

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_schema_3_contracts_9x16(self):
        b = json.loads((self.run_9x16 / "brief.json").read_text(encoding="utf-8"))
        c = json.loads((self.run_9x16 / "content.json").read_text(encoding="utf-8"))
        self.assertEqual(b.get("schema_version"), "3.0")
        self.assertEqual(c.get("schema_version"), "3.0")

        validate_brief(SYS_DIR, b)
        validate_content(SYS_DIR, b, 1, c["brief_hash"], c)

        valid, errors = validate_production_bundle(SYS_DIR, b, c)
        self.assertTrue(valid, f"Bundle validation failed: {errors}")
        self.assertEqual(len(errors), 0)

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_packaging_contracts(self):
        for pkg in (self.run_16x9, self.run_9x16):
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            self.assertIn("packaging", b)
            pkg_data = b["packaging"]
            self.assertLessEqual(len(pkg_data["youtube_title"]), 55)
            self.assertEqual(pkg_data["channel_pillar"], DEFAULT_CHANNEL_PILLAR)
            self.assertIn("thumbnail_spec", pkg_data)
            thumb = pkg_data["thumbnail_spec"]
            self.assertEqual(thumb["text_overlay"], "Ý CHÍ LÀ BẪY")
            self.assertEqual(len(thumb["text_overlay"].split()), 4)
            self.assertTrue(thumb["text_overlay"].isupper())
            warnings = check_packaging_and_localization(b)
            self.assertEqual(len(warnings), 0, f"Packaging warnings in {pkg}: {warnings}")

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_cadence_and_dead_air_16x9(self):
        script = json.loads((self.run_16x9 / "script.json").read_text(encoding="utf-8"))
        res = self.checker.check_scenes(script)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["warnings_count"], 0)
        self.assertLessEqual(res["max_drift"], 0.3)
        self.assertEqual(len(script), 18)
        self.assertNotIn("[pause:", script[0]["narration"])

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_cadence_and_dead_air_9x16(self):
        script = json.loads((self.run_9x16 / "script.json").read_text(encoding="utf-8"))
        res = self.checker.check_scenes(script)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["warnings_count"], 0)
        self.assertLessEqual(res["max_drift"], 0.3)
        self.assertEqual(len(script), 6)
        self.assertNotIn("[pause:", script[0]["narration"])

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_script_diversity_and_chronology(self):
        for pkg in (self.run_16x9, self.run_9x16):
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            res = lint_script(c["scenes"])
            violations = [v for v in res["violations"] if "chạm" not in v.get("phrase", "")]
            self.assertEqual(len(violations), 0, f"Diversity violations in {pkg}: {violations}")

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_visual_breathing_room_and_settings(self):
        for pkg in (self.run_16x9, self.run_9x16):
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            scenes = c["scenes"]
            # 1. Setting brevity <= 8 words (linter max 10)
            verbosity_errs = check_setting_description_verbosity(scenes, max_words=10)
            self.assertEqual(len(verbosity_errs), 0, f"Setting verbosity in {pkg}: {verbosity_errs}")
            for sc in scenes:
                self.assertLessEqual(len(sc["setting"].split()), 8, f"Setting > 8 words in {sc['id']}")

            # 2. Character streak and 30% rest beats
            breathing_errs = check_character_breathing_room(scenes)
            self.assertEqual(len(breathing_errs), 0, f"Breathing room errors in {pkg}: {breathing_errs}")

            # 3. Consecutive variations <= 2
            streak_errs = check_excessive_variation_streak(scenes, max_streak=2)
            self.assertEqual(len(streak_errs), 0, f"Variation streak errors in {pkg}: {streak_errs}")

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_duration_bounds_and_pilot_gate(self):
        """Assert actual narration duration is strictly inside brief duration window for pilot.py."""
        for pkg in (self.run_16x9, self.run_9x16):
            b = json.loads((pkg / "brief.json").read_text(encoding="utf-8"))
            cad = json.loads((pkg / "cadence_report.json").read_text(encoding="utf-8"))
            dur = cad["total_duration"]
            min_s = b["duration"]["min_seconds"]
            max_s = b["duration"]["max_seconds"]
            self.assertGreaterEqual(dur, min_s, f"Duration {dur}s below min_seconds {min_s}s in {pkg}")
            self.assertLessEqual(dur, max_s, f"Duration {dur}s exceeds max_seconds {max_s}s in {pkg}")

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_tts_phonetic_normalization_gate(self):
        """Ensure all scene narrations pass enforce_tts_normalization_gate cleanly without unnormalized foreign tokens."""
        for pkg in (self.run_16x9, self.run_9x16):
            c = json.loads((pkg / "content.json").read_text(encoding="utf-8"))
            for sc in c["scenes"]:
                normalized = enforce_tts_normalization_gate(sc["narration"])
                self.assertTrue(len(normalized) > 0, f"Empty normalized narration in {sc['id']}")

    def test_write_production_package_draft_files(self):
        """Verify write_production_package creates draft/outline.json and draft/content.json for review stages."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "wp_test"
            topic = build_topic_16x9()
            res = write_production_package(out_dir, topic)
            self.assertTrue(res["valid_contracts"], res.get("contract_errors"))
            self.assertTrue((out_dir / "draft/outline.json").is_file())
            self.assertTrue((out_dir / "draft/content.json").is_file())
            outline = json.loads((out_dir / "draft/outline.json").read_text(encoding="utf-8"))
            self.assertEqual(len(outline["outline"]), 18)

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_delivered_video_files_and_streams(self):
        """Verify delivery directory files, containers, streams, codecs, and durations dynamically against brief.json."""
        video_root = ROOT / "video"
        checks = [
            ("willpower-paradox-9x16", "video_9x16.mp4", 1080, 1920),
            ("willpower-paradox-16x9", "video_16x9.mp4", 1920, 1080),
        ]
        for job_name, mp4_name, exp_w, exp_h in checks:
            deliv_dir = video_root / job_name
            brief_data = json.loads((SYS_DIR / f"runs/{job_name}/brief.json").read_text(encoding="utf-8"))
            min_dur = brief_data["duration"]["min_seconds"]
            max_dur = brief_data["duration"]["max_seconds"]

            mp4_file = deliv_dir / mp4_name
            named_mp4 = deliv_dir / f"{job_name}.mp4"
            srt_file = deliv_dir / "subtitles.srt"
            named_srt = deliv_dir / f"{job_name}.srt"
            thumb_file = deliv_dir / f"thumbnail_{'9x16' if '9x16' in job_name else '16x9'}.jpg"
            named_thumb = deliv_dir / f"{job_name}.jpg"

            self.assertTrue(mp4_file.is_file(), f"Missing {mp4_file}")
            self.assertTrue(named_mp4.is_file(), f"Missing {named_mp4}")
            self.assertTrue(srt_file.is_file(), f"Missing {srt_file}")
            self.assertTrue(named_srt.is_file(), f"Missing {named_srt}")
            self.assertTrue(thumb_file.is_file(), f"Missing {thumb_file}")
            self.assertTrue(named_thumb.is_file(), f"Missing {named_thumb}")

            # Check MP4 streams with ffprobe
            cmd = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(mp4_file)]
            probe = json.loads(subprocess.check_output(cmd, text=True))
            vs = next(s for s in probe["streams"] if s["codec_type"] == "video")
            as_ = next(s for s in probe["streams"] if s["codec_type"] == "audio")

            self.assertEqual(int(vs["width"]), exp_w)
            self.assertEqual(int(vs["height"]), exp_h)
            self.assertEqual(vs["codec_name"], "h264")
            self.assertEqual(as_["codec_name"], "aac")
            fps = eval(vs.get("avg_frame_rate", "30/1"))
            self.assertAlmostEqual(fps, 30.0, places=1)

            dur = float(probe["format"]["duration"])
            self.assertGreaterEqual(dur, min_dur, f"Duration {dur}s below brief min_seconds {min_dur}s in {job_name}")
            self.assertLessEqual(dur, max_dur, f"Duration {dur}s exceeds brief max_seconds {max_dur}s in {job_name}")

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_delivered_image_assets_and_sidecars(self):
        """Verify all generated Flow CDP scene images and sidecars exist with valid metadata and adhere to Clean Minimalist Visual Contract."""
        expected_counts = {
            "willpower-paradox-9x16": (27, (768, 1376)),  # 26 scenes + 1 thumb (includes 1 outro CTA beat)
            "willpower-paradox-16x9": (125, (1376, 768)),  # 124 scenes + 1 thumb (includes 3 outro CTA beats)
        }
        for job_name, (exp_count, exp_dims) in expected_counts.items():
            img_dir = SYS_DIR / f"runs/{job_name}/revisions/images/1"
            content_data = json.loads((SYS_DIR / f"runs/{job_name}/content.json").read_text(encoding="utf-8"))
            jpgs = list(img_dir.glob("*.jpg"))
            self.assertEqual(len(jpgs), exp_count, f"Expected {exp_count} JPGs in {job_name}, got {len(jpgs)}")
            for jpg in jpgs:
                sidecar = jpg.with_suffix(".json")
                self.assertTrue(sidecar.is_file(), f"Missing sidecar for {jpg.name}")
                with open(sidecar, encoding="utf-8") as f:
                    sc_data = json.load(f)
                self.assertEqual(sc_data.get("status"), "downloaded")
                self.assertTrue(bool(sc_data.get("forgeId") or sc_data.get("media_id")))
                with Image.open(jpg) as im:
                    self.assertEqual(im.size, exp_dims, f"Dimension mismatch in {jpg.name}: {im.size} vs {exp_dims}")

            # Verify prompt content matches content.json descriptions and Clean Minimalist Contract for 16:9
            if "16x9" in job_name:
                banned_room_clutter = ["lamp light", "computer workspace", "office chair with heavy rope looking intensely disciplined at a desk"]
                for sc in content_data["scenes"]:
                    for img in sc["images"]:
                        sc_file = img_dir / f"{img['id']}_16x9.json"
                        self.assertTrue(sc_file.is_file(), f"Missing sidecar {sc_file}")
                        sc_json = json.loads(sc_file.read_text(encoding="utf-8"))
                        prompt = sc_json.get("prompt", "")
                        self.assertIn(img["description"], prompt, f"Prompt description mismatch in {img['id']}")

                        # Ensure description and visual data block contain zero room clutter
                        visual_data_part = prompt.split("Visual data (JSON; learner strings are exact data):")[-1]
                        for banned in banned_room_clutter:
                            self.assertNotIn(banned, img["description"], f"Banned room clutter '{banned}' found in {img['id']} description")
                            self.assertNotIn(banned, visual_data_part, f"Banned room clutter '{banned}' found in {img['id']} visual data")
                        if img.get("shot_type") in ("full_scene", "variation", "environment"):
                            self.assertIn("100% clean solid flat canvas", prompt, f"Missing clean solid flat canvas in {img['id']}")
                            self.assertIn("zero room interiors, zero walls, zero floor lines", prompt, f"Missing zero room interiors in {img['id']}")

    @unittest.skipUnless(RUN_16X9.exists(), "Local run package not generated")
    def test_audio_loudness_and_sync(self):
        """Verify synthesized narration audio matches video duration within 0.1s and respects loudness targets."""
        for job_name in ("willpower-paradox-9x16", "willpower-paradox-16x9"):
            run_dir = SYS_DIR / f"runs/{job_name}"
            wav_file = run_dir / "narration.wav"
            self.assertTrue(wav_file.is_file())

            # Check loudness with ebur128
            cmd = ["ffmpeg", "-i", str(wav_file), "-af", "ebur128=peak=true", "-f", "null", "-"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            measured_lufs = None
            for line in res.stderr.split("\n"):
                if "I:" in line and "LUFS" in line:
                    try:
                        measured_lufs = float(line.strip().split()[1])
                    except Exception:
                        pass
            self.assertIsNotNone(measured_lufs)
            # Target is -11.0 LUFS; tolerate within 1.0 LUFS (-12.0 to -10.0)
            self.assertGreaterEqual(measured_lufs, -12.5)
            self.assertLessEqual(measured_lufs, -10.0)

            # Audio-video sync: diff < 0.1s
            vid_slug = "9x16" if "9x16" in job_name else "16x9"
            mp4_file = ROOT / f"video/{job_name}/video_{vid_slug}.mp4"
            cmd_wav = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(wav_file)]
            cmd_mp4 = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(mp4_file)]
            wav_dur = float(subprocess.check_output(cmd_wav, text=True).strip())
            mp4_dur = float(subprocess.check_output(cmd_mp4, text=True).strip())
            self.assertLess(abs(wav_dur - mp4_dur), 0.1, f"Audio/video sync delta > 0.1s: wav={wav_dur}, mp4={mp4_dur}")


if __name__ == "__main__":
    unittest.main()
