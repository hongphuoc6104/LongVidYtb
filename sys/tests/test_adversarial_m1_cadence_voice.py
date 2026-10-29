#!/usr/bin/env python3
"""Adversarial stress harness for Milestone M1-2:
1. SC01 hook boundary: exactly 18 syllables (PASS) vs 19 syllables (OPENING_HOOK_TOO_LONG).
2. SC01 opening pause: SC01 [pause:800ms] (OPENING_SCENE_PAUSE_FORBIDDEN) vs SC02 [pause:800ms] (PASS).
3. Clause length limit: clause with 18 syllables (PASS) vs 19 syllables (BREATHLESS_CLAUSE).
4. Audio pipeline pause preservation: raw script with [pause:800ms] produces 0.80s gap and clean text without leading commas.
5. Spinoff hook boundary: 2.99s (PASS) vs 3.01s (REJECTED by gate).
6. VietNarrator SHA-256 and duration contract integrity.
"""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import adapters
from audio_pipeline import AudioPipeline, AudioPipelineError
from colab_bridge.protocol import (
    TONE_SPEED_MULTIPLIERS,
    resolve_tone_speed,
    validate_result,
)
from script_cadence_checker import (
    SceneCadenceReport,
    ScriptCadenceChecker,
    count_syllables,
)
from tools.vn_text_normalizer import normalize_for_tts

from pilot import read


class TestSC01OpeningHookBoundary(unittest.TestCase):
    """Adversarially tests SC01 opening hook syllable boundary (<= 18 vs 19)."""

    def setUp(self):
        self.checker = ScriptCadenceChecker()
        # 18 syllables: 18 words, Vietnamese monosyllabic
        self.hook_18_syl = "Đây là một câu mở đầu có đúng mười tám âm tiết tiếng Việt rất chuẩn này nhé."
        # 19 syllables: 19 words
        self.hook_19_syl = "Đây là một câu mở đầu có đúng mười chín âm tiết tiếng Việt rất chuẩn này nhé anh."

    def test_syllable_counter_accuracy(self):
        self.assertEqual(count_syllables(self.hook_18_syl), 18)
        self.assertEqual(count_syllables(self.hook_19_syl), 19)

    def test_hook_boundary_18_syllables_passes(self):
        scenes = [{"id": "SC01", "duration": 5.2, "narration": self.hook_18_syl}]
        res = self.checker.check_scenes(scenes)
        warnings = [w for sc in res["scenes"] for w in sc["warnings"]]
        hook_warnings = [w for w in warnings if "OPENING_HOOK_TOO_LONG" in w]
        self.assertEqual(hook_warnings, [], "18-syllable opening hook must NOT trigger OPENING_HOOK_TOO_LONG")
        self.assertEqual(res["scenes"][0]["status"], "PASS")

    def test_hook_boundary_19_syllables_triggers_warning(self):
        scenes = [{"id": "SC01", "duration": 5.45, "narration": self.hook_19_syl}]
        res = self.checker.check_scenes(scenes)
        warnings = [w for sc in res["scenes"] for w in sc["warnings"]]
        hook_warnings = [w for w in warnings if "OPENING_HOOK_TOO_LONG" in w]
        self.assertEqual(len(hook_warnings), 1, "19-syllable opening hook MUST trigger OPENING_HOOK_TOO_LONG")
        self.assertIn("OPENING_HOOK_TOO_LONG", hook_warnings[0])
        self.assertIn("19 syllables", hook_warnings[0])
        self.assertIn("<= 18", hook_warnings[0])

    def test_hook_boundary_19_syllables_with_comma_still_triggers_hook_warning(self):
        # 19 syllables split by comma: each clause <= 18 syl, but hook sentence is 19 syl
        hook_19_with_comma = "Đây là một câu mở đầu có đúng, mười chín âm tiết tiếng Việt rất chuẩn này nhé anh."
        self.assertEqual(count_syllables(hook_19_with_comma), 19)
        scenes = [{"id": "SC01", "duration": 5.45, "narration": hook_19_with_comma}]
        res = self.checker.check_scenes(scenes)
        warnings = [w for sc in res["scenes"] for w in sc["warnings"]]
        hook_warnings = [w for w in warnings if "OPENING_HOOK_TOO_LONG" in w]
        clause_warnings = [w for w in warnings if "BREATHLESS_CLAUSE" in w]
        self.assertEqual(len(hook_warnings), 1, "Sentence-level hook limit must trigger even if clause is split")
        self.assertEqual(clause_warnings, [], "Clauses separated by comma must NOT trigger BREATHLESS_CLAUSE")

    def test_hook_boundary_isolated_to_opening_scene(self):
        # SC02 has 19 syllables; must NOT trigger OPENING_HOOK_TOO_LONG
        scenes = [
            {"id": "SC01", "duration": 5.2, "narration": self.hook_18_syl},
            {"id": "SC02", "duration": 5.5, "narration": "Đây là một câu tiếp theo có đúng, mười chín âm tiết tiếng Việt rất chuẩn này nhé anh."},
        ]
        res = self.checker.check_scenes(scenes)
        sc02_warnings = res["scenes"][1]["warnings"]
        hook_warnings = [w for w in sc02_warnings if "OPENING_HOOK_TOO_LONG" in w]
        self.assertEqual(hook_warnings, [], "SC02 must NOT trigger OPENING_HOOK_TOO_LONG")

    def test_opening_scene_identifier_variants(self):
        # Various opening scene IDs must all trigger OPENING_HOOK_TOO_LONG
        for sc_id in ("SC01", "Scene 1", "Phân cảnh 01"):
            report = SceneCadenceReport(scene_id=sc_id, duration=6.0, narration=self.hook_19_syl, is_last=False)
            hook_warnings = [w for w in report.warnings if "OPENING_HOOK_TOO_LONG" in w]
            self.assertEqual(len(hook_warnings), 1, f"Identifier {sc_id} must be recognized as opening scene")


class TestSC01OpeningPauseForbidden(unittest.TestCase):
    """Adversarially tests zero pause policy in SC01 vs allowed pause in SC02."""

    def setUp(self):
        self.checker = ScriptCadenceChecker()

    def test_sc01_with_pause_800ms_triggers_warning(self):
        scenes = [
            {"id": "SC01", "duration": 5.15, "narration": "Đây là câu mở đầu có đúng mười sáu âm tiết tiếng Việt nhé. [pause:800ms]"},
        ]
        res = self.checker.check_scenes(scenes)
        warnings = res["scenes"][0]["warnings"]
        pause_warnings = [w for w in warnings if "OPENING_SCENE_PAUSE_FORBIDDEN" in w]
        self.assertEqual(len(pause_warnings), 1, "SC01 with [pause:800ms] MUST trigger OPENING_SCENE_PAUSE_FORBIDDEN")
        self.assertIn("zero [pause:...]", pause_warnings[0])

    def test_sc01_with_various_pause_formats_triggers_warning(self):
        for pause_tag in ("[pause:500ms]", "[pause:0.5s]", "[pause:1.2s]"):
            report = SceneCadenceReport(
                scene_id="SC01",
                duration=6.0,
                narration=f"Câu mở đầu một hai ba bốn. {pause_tag} Câu tiếp theo năm sáu bảy tám.",
                is_last=False,
            )
            pause_warnings = [w for w in report.warnings if "OPENING_SCENE_PAUSE_FORBIDDEN" in w]
            self.assertEqual(len(pause_warnings), 1, f"SC01 with {pause_tag} must trigger OPENING_SCENE_PAUSE_FORBIDDEN")

    def test_sc02_with_pause_800ms_passes(self):
        scenes = [
            {"id": "SC01", "duration": 5.2, "narration": "Đây là một câu mở đầu có đúng mười tám âm tiết tiếng Việt rất chuẩn này nhé."},
            {"id": "SC02", "duration": 7.0, "narration": "Phân cảnh thứ hai này có mười âm tiết rất hay. [pause:800ms] Và câu kết thúc cũng có mười âm tiết nữa."},
            {"id": "SC03", "duration": 5.0, "narration": "Đây là phân cảnh kết thúc của toàn bộ video mẫu này."},
        ]
        res = self.checker.check_scenes(scenes)
        sc01_warnings = res["scenes"][0]["warnings"]
        sc02_warnings = res["scenes"][1]["warnings"]
        self.assertEqual(sc01_warnings, [], "SC01 without pause must pass with zero warnings")
        pause_warnings_sc02 = [w for w in sc02_warnings if "OPENING_SCENE_PAUSE_FORBIDDEN" in w]
        self.assertEqual(pause_warnings_sc02, [], "SC02 with [pause:800ms] must NOT trigger OPENING_SCENE_PAUSE_FORBIDDEN")
        self.assertEqual(sc02_warnings, [], "SC02 with valid cadence must have zero warnings")

    def test_forbid_opening_pause_disabled_override(self):
        report = SceneCadenceReport(
            scene_id="SC01",
            duration=6.0,
            narration="Câu mở đầu. [pause:800ms] Câu tiếp theo.",
            is_last=False,
            forbid_opening_pause=False,
        )
        pause_warnings = [w for w in report.warnings if "OPENING_SCENE_PAUSE_FORBIDDEN" in w]
        self.assertEqual(pause_warnings, [], "When forbid_opening_pause=False, pause warning must NOT be raised")


class TestClauseLengthLimit(unittest.TestCase):
    """Adversarially tests breathless clause syllable limit (<= 18 vs 19 without comma)."""

    def setUp(self):
        self.clause_18 = "Đây là một câu mở đầu có đúng mười tám âm tiết tiếng Việt rất chuẩn này nhé."
        self.clause_19 = "Đây là một câu mở đầu có đúng mười chín âm tiết tiếng Việt rất chuẩn này nhé anh."

    def test_clause_18_syllables_passes(self):
        report = SceneCadenceReport(scene_id="SC02", duration=6.0, narration=self.clause_18, is_last=False)
        clause_warnings = [w for w in report.warnings if "BREATHLESS_CLAUSE" in w]
        self.assertEqual(clause_warnings, [], "18-syllable clause must NOT trigger BREATHLESS_CLAUSE")

    def test_clause_19_syllables_triggers_breathless_clause(self):
        report = SceneCadenceReport(scene_id="SC02", duration=6.0, narration=self.clause_19, is_last=False)
        clause_warnings = [w for w in report.warnings if "BREATHLESS_CLAUSE" in w]
        self.assertEqual(len(clause_warnings), 1, "19-syllable clause without comma MUST trigger BREATHLESS_CLAUSE")
        self.assertIn("Clause #1 in sentence #1 has 19 syllables", clause_warnings[0])
        self.assertIn("exceeds 18 syl", clause_warnings[0])

    def test_sentence_with_two_18_syllable_clauses_passes(self):
        # 18 syl + comma + 18 syl = 36 syl sentence with comma breathing break
        two_clauses = (
            "Đây là một câu mở đầu có đúng mười tám âm tiết tiếng Việt rất chuẩn này nhé, "
            "và đây là một câu tiếp theo có đúng mười tám âm tiết tiếng Việt rất chuẩn này."
        )
        report = SceneCadenceReport(scene_id="SC02", duration=10.0, narration=two_clauses, is_last=False)
        clause_warnings = [w for w in report.warnings if "BREATHLESS_CLAUSE" in w]
        self.assertEqual(clause_warnings, [], "Two 18-syllable clauses separated by comma must pass without warning")

    def test_clause_delimiters_semicolon_and_dashes(self):
        # Semicolon
        s_semi = "Đây là một câu mở đầu có đúng mười tám âm tiết tiếng; tiếp theo là một câu ngắn."
        rep_semi = SceneCadenceReport(scene_id="SC02", duration=8.0, narration=s_semi, is_last=False)
        self.assertEqual([w for w in rep_semi.warnings if "BREATHLESS_CLAUSE" in w], [])

        # Em-dash
        s_dash = "Đây là một câu mở đầu có đúng mười tám âm tiết tiếng — tiếp theo là một câu ngắn."
        rep_dash = SceneCadenceReport(scene_id="SC02", duration=8.0, narration=s_dash, is_last=False)
        self.assertEqual([w for w in rep_dash.warnings if "BREATHLESS_CLAUSE" in w], [])

        # En-dash
        s_endash = "Đây là một câu mở đầu có đúng mười tám âm tiết tiếng – tiếp theo là một câu ngắn."
        rep_endash = SceneCadenceReport(scene_id="SC02", duration=8.0, narration=s_endash, is_last=False)
        self.assertEqual([w for w in rep_endash.warnings if "BREATHLESS_CLAUSE" in w], [])

    def test_clause_limit_disabled_with_none_or_zero(self):
        for val in (None, 0):
            report = SceneCadenceReport(
                scene_id="SC02",
                duration=8.0,
                narration=self.clause_19,
                is_last=False,
                max_clause_syllables=val,
            )
            clause_warnings = [w for w in report.warnings if "BREATHLESS_CLAUSE" in w]
            self.assertEqual(clause_warnings, [], f"max_clause_syllables={val} must disable breathless clause checks")


class TestAudioPipelinePausePreservationAndCadenceRejection(unittest.TestCase):
    """Adversarially tests audio_pipeline pause preservation, chunking, and cadence rejection."""

    def test_audio_pipeline_preserves_pause_in_narration_normalized(self):
        raw = "Câu thứ nhất của cảnh. [pause:800ms] Câu thứ hai của cảnh."
        normalized = normalize_for_tts(raw, preserve_pauses=True)
        self.assertIn("[pause:800ms]", normalized, "Explicit pause tag must be preserved in normalized output")

    def test_audio_pipeline_chunk_gap_and_clean_text(self):
        raw = "Câu thứ nhất của cảnh. [pause:800ms] Câu thứ hai của cảnh."
        normalized = normalize_for_tts(raw, preserve_pauses=True)
        chunks, gaps = adapters.chunks_with_gaps(normalized, adapters.DEFAULT_PAUSE)
        self.assertEqual(chunks, ["Câu thứ nhất của cảnh.", "Câu thứ hai của cảnh."])
        self.assertEqual(gaps, [0.8], "Explicit pause [pause:800ms] must produce gap of exactly 0.80s")

        # Simulate audio_pipeline.py segment planning
        segments = []
        for c_idx, chunk_text in enumerate(chunks):
            clean_chunk = chunk_text.lstrip(", ").strip()
            pause_sec = gaps[c_idx] if c_idx < len(gaps) else adapters.DEFAULT_PAUSE["minor"]
            segments.append({"text": clean_chunk, "pause": pause_sec})

        self.assertEqual(segments[0]["pause"], 0.8)
        self.assertFalse(segments[1]["text"].startswith(","))
        self.assertEqual(segments[1]["text"], "Câu thứ hai của cảnh.")

    def test_audio_pipeline_strips_commas_surrounding_pause_tag(self):
        raw = "Câu thứ nhất của cảnh, [pause:800ms], câu thứ hai của cảnh."
        normalized = normalize_for_tts(raw, preserve_pauses=True)
        chunks, gaps = adapters.chunks_with_gaps(normalized, adapters.DEFAULT_PAUSE)
        clean_chunks = [c.lstrip(", ").strip() for c in chunks]
        self.assertEqual(clean_chunks, ["Câu thứ nhất của cảnh", "câu thứ hai của cảnh."])
        self.assertEqual(gaps, [0.8])

    def test_audio_pipeline_rejects_sc01_pause(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            job_dir = Path(tmp_dir)
            content = {
                "scenes": [
                    {"id": "SC01", "duration": 5.15, "narration": "Đây là câu mở đầu có đúng mười sáu âm tiết tiếng Việt nhé. [pause:800ms]"}
                ]
            }
            brief = {"voice": "VietNarrator", "speed": 1.0}
            (job_dir / "content.json").write_text(json.dumps(content, ensure_ascii=False))
            (job_dir / "brief.json").write_text(json.dumps(brief, ensure_ascii=False))

            # Default strict_cadence=False logs advisory without raising fatal exception
            pipeline_advisory = AudioPipeline(job_dir / "content.json", job_dir / "brief.json", job_dir / "out", mock=True)
            res = pipeline_advisory.run()
            self.assertIn("total_duration", res)

            # strict_cadence=True raises AudioPipelineError
            pipeline_strict = AudioPipeline(
                job_dir / "content.json", job_dir / "brief.json", job_dir / "out", mock=True, strict_cadence=True
            )
            with self.assertRaises(AudioPipelineError) as ctx:
                pipeline_strict.run()
            self.assertIn("Cadence rejection", str(ctx.exception))
            self.assertIn("OPENING_SCENE_PAUSE_FORBIDDEN", str(ctx.exception))

    def test_audio_pipeline_rejects_sc01_19_syl_hook(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            job_dir = Path(tmp_dir)
            content = {
                "scenes": [
                    {"id": "SC01", "duration": 5.45, "narration": "Đây là một câu mở đầu có đúng mười chín âm tiết tiếng Việt rất chuẩn này nhé anh."}
                ]
            }
            brief = {"voice": "VietNarrator", "speed": 1.0}
            (job_dir / "content.json").write_text(json.dumps(content, ensure_ascii=False))
            (job_dir / "brief.json").write_text(json.dumps(brief, ensure_ascii=False))

            # Default strict_cadence=False logs advisory without raising fatal exception
            pipeline_advisory = AudioPipeline(job_dir / "content.json", job_dir / "brief.json", job_dir / "out", mock=True)
            res = pipeline_advisory.run()
            self.assertIn("total_duration", res)

            # strict_cadence=True raises AudioPipelineError
            pipeline_strict = AudioPipeline(
                job_dir / "content.json", job_dir / "brief.json", job_dir / "out", mock=True, strict_cadence=True
            )
            with self.assertRaises(AudioPipelineError) as ctx:
                pipeline_strict.run()
            self.assertIn("Cadence rejection", str(ctx.exception))
            self.assertIn("OPENING_HOOK_TOO_LONG", str(ctx.exception))

    def test_audio_pipeline_accepts_valid_sc01_and_sc02_pause(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            job_dir = Path(tmp_dir)
            content = {
                "scenes": [
                    {"id": "SC01", "duration": 5.2, "narration": "Đây là một câu mở đầu có đúng mười tám âm tiết tiếng Việt rất chuẩn này nhé."},
                    {"id": "SC02", "duration": 6.65, "narration": "Phân cảnh thứ hai này có mười âm tiết rất hay. [pause:800ms] Và câu kết thúc cũng có mười âm tiết nữa."}
                ]
            }
            brief = {"voice": "VietNarrator", "speed": 1.0}
            (job_dir / "content.json").write_text(json.dumps(content, ensure_ascii=False))
            (job_dir / "brief.json").write_text(json.dumps(brief, ensure_ascii=False))

            pipeline = AudioPipeline(job_dir / "content.json", job_dir / "brief.json", job_dir / "out", mock=True)
            res = pipeline.run()
            self.assertIn("total_duration", res)
            self.assertEqual(len(res.get("segments", [])), 3)


class TestSpinoffHookBoundary(unittest.TestCase):
    """Adversarially tests standalone spinoff hook duration gate (2.99s, 3.00s vs 3.01s)
    against real production colab_bridge.protocol.validate_result.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        self.models = {"vi": {"revision": "a" * 40}}
        self.req_hook = {"id": "hook_01", "text": "Nghịch lý nhận thức", "item": 0}
        self.req = {
            "request_id": "req_adv_spinoff",
            "primary_language": "vi",
            "profiles": {"vi": {"voice": "VietNarrator"}},
            "models": self.models,
            "segments": [],
            "english": [],
            "spinoff_hooks": [self.req_hook],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def _write_result(self, dur: float):
        wav_path = self.folder / "hook_01.wav"
        with wave.open(str(wav_path), "wb") as w:
            w.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
            w.writeframes(b"\x00\x20" * round(max(0.0, dur) * 48000))
        payload = {
            "request_id": "req_adv_spinoff",
            "voice": "VietNarrator",
            "engine": {"backend": "colab-omnivoice", "models": self.models, "device": "Tesla T4"},
            "segments": [],
            "spinoff_hooks": [{"id": "hook_01", "text": "Nghịch lý nhận thức", "path": "hook_01.wav", "duration": dur}],
        }
        (self.folder / "tts-result.json").write_text(json.dumps(payload, ensure_ascii=False))

    def test_spinoff_hook_2_99s_passes_gate(self):
        self._write_result(2.99)
        names = validate_result(self.folder, self.req)
        self.assertIn("hook_01.wav", names)

    def test_spinoff_hook_3_00s_exact_boundary_passes(self):
        self._write_result(3.00)
        names = validate_result(self.folder, self.req)
        self.assertIn("hook_01.wav", names)

    def test_spinoff_hook_3_01s_rejected_by_gate(self):
        self._write_result(3.01)
        with self.assertRaises(ValueError) as ctx:
            validate_result(self.folder, self.req)
        self.assertEqual(str(ctx.exception), "Standalone hook identity/duration mismatch")

    def test_spinoff_hook_zero_and_negative_rejected(self):
        for invalid_d in (0.0, -0.01, -2.5):
            self._write_result(invalid_d)
            with self.assertRaises(ValueError) as ctx:
                validate_result(self.folder, self.req)
            self.assertEqual(str(ctx.exception), "Standalone hook identity/duration mismatch")


class TestVietNarratorContractIntegrity(unittest.TestCase):
    """Adversarially tests VietNarrator profile integrity, reference WAV, and pinned HF hashes."""

    def setUp(self):
        self.profile_dir = ROOT / "assets/voices/viet_narrator"
        self.profile_path = self.profile_dir / "profile.json"
        self.reference_wav = self.profile_dir / "reference.wav"

    def test_profile_json_canonical_sha256_and_settings(self):
        self.assertTrue(self.profile_path.is_file())
        with open(self.profile_path, "r", encoding="utf-8") as f:
            prof = json.load(f)
        self.assertEqual(prof.get("voice"), "VietNarrator")
        self.assertEqual(prof.get("source_speed"), 1.0)
        self.assertEqual(prof.get("language"), "vi")
        self.assertEqual(prof.get("sha256"), "ec54c744434ab5569f3d7a3c542607ddbfd3bd02023a1d0232a17523fce32681")

    def test_reference_wav_file_hash_and_audio_invariants(self):
        self.assertTrue(self.reference_wav.is_file())
        hasher = hashlib.sha256()
        with open(self.reference_wav, "rb") as f:
            hasher.update(f.read())
        self.assertEqual(hasher.hexdigest(), "ec54c744434ab5569f3d7a3c542607ddbfd3bd02023a1d0232a17523fce32681")

        with wave.open(str(self.reference_wav), "rb") as w:
            self.assertEqual(w.getnchannels(), 1, "Must be mono")
            self.assertEqual(w.getsampwidth(), 2, "Must be PCM16")
            self.assertEqual(w.getframerate(), 24000, "24kHz sample rate")
            self.assertEqual(w.getnframes(), 288000, "288,000 frames = 12.0s")
            self.assertAlmostEqual(w.getnframes() / w.getframerate(), 12.0, places=3)

    def test_pinned_40_char_hex_huggingface_revisions(self):
        cfg = read(ROOT / "config.json")
        models = cfg.get("colab_tts", {}).get("models", {})
        hex_re = re.compile(r"^[0-9a-f]{40}$")
        for lang in ("vi", "en"):
            rev = models.get(lang, {}).get("revision", "")
            self.assertTrue(bool(hex_re.match(rev)), f"Model revision for {lang} must be 40-char hex hash: {rev}")

    def test_tone_speed_multipliers_and_base_speed_preservation(self):
        self.assertEqual(TONE_SPEED_MULTIPLIERS.get("narrative_warm"), 0.98)
        self.assertEqual(TONE_SPEED_MULTIPLIERS.get("analytical_crisp"), 1.02)
        self.assertEqual(TONE_SPEED_MULTIPLIERS.get("reflective_slow"), 0.92)
        # Base speed 1.0 preservation
        self.assertEqual(resolve_tone_speed(1.0, "narrative_warm"), 0.98)
        self.assertEqual(resolve_tone_speed(1.0, "analytical_crisp"), 1.02)
        self.assertEqual(resolve_tone_speed(1.0, "reflective_slow"), 0.92)
        self.assertEqual(resolve_tone_speed(1.0, None), 1.00)


if __name__ == "__main__":
    unittest.main()
