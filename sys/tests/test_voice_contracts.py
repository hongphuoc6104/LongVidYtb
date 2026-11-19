#!/usr/bin/env python3
"""Unit and integration tests for VietNarrator voice profile contracts,
tone speed modulation, inline English spans, and spinoff hooks.

Validates:
1. VietNarrator profile contract: canonical SHA-256, 12.0s duration, pinned 40-char HF revision.
2. Tone speed modulation: narrative_warm (0.98), analytical_crisp (1.02), reflective_slow (0.92),
   preserving base_speeds (1.0).
3. Inline English spans: 0.18s acoustic gap insertion between alternating language segments.
4. Spinoff hooks gate: strict duration limit (0 < duration <= 3.0s).
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import adapters
from colab_bridge.protocol import (
    TONE_SPEED_MULTIPLIERS,
    build_request,
    resolve_tone_speed,
    validate_result,
)

from pilot import read


class TestVietNarratorProfileContract(unittest.TestCase):
    """Validates the canonical VietNarrator voice profile invariants."""

    def setUp(self):
        self.profile_dir = ROOT / "assets/voices/viet_narrator"
        self.profile_path = self.profile_dir / "profile.json"
        self.reference_wav = self.profile_dir / "reference.wav"

    def test_canonical_profile_json_fields(self):
        self.assertTrue(self.profile_path.is_file(), "profile.json must exist")
        with open(self.profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)

        self.assertEqual(profile.get("voice"), "VietNarrator")
        self.assertEqual(profile.get("language"), "vi")
        self.assertIn("vi", profile.get("languages", []))
        self.assertEqual(profile.get("source_speed"), 1.0)
        self.assertEqual(
            profile.get("sha256"),
            "ec54c744434ab5569f3d7a3c542607ddbfd3bd02023a1d0232a17523fce32681",
        )

    def test_reference_wav_duration_and_checksum(self):
        self.assertTrue(self.reference_wav.is_file(), "reference.wav must exist")
        # Verify SHA-256
        hasher = hashlib.sha256()
        with open(self.reference_wav, "rb") as f:
            hasher.update(f.read())
        self.assertEqual(
            hasher.hexdigest(),
            "ec54c744434ab5569f3d7a3c542607ddbfd3bd02023a1d0232a17523fce32681",
        )

        # Verify WAV audio parameters & exact 12.0s duration
        with wave.open(str(self.reference_wav), "rb") as w:
            channels = w.getnchannels()
            sample_width = w.getsampwidth()
            framerate = w.getframerate()
            frames = w.getnframes()
            duration = frames / framerate

            self.assertEqual(channels, 1, "Must be mono PCM")
            self.assertEqual(sample_width, 2, "Must be PCM16 (2 bytes per sample)")
            self.assertEqual(framerate, 24000, "Reference WAV recorded at 24kHz")
            self.assertEqual(frames, 288000, "288,000 frames at 24kHz = exactly 12.0s")
            self.assertAlmostEqual(duration, 12.0, places=3)
            # Must satisfy protocol duration bound: 3.0s <= duration <= 15.0s
            self.assertTrue(3.0 <= duration <= 15.0)

    def test_pinned_huggingface_model_revisions(self):
        cfg = read(ROOT / "config.json")
        models = cfg.get("colab_tts", {}).get("models", {})

        hex_40_re = re.compile(r"^[a-f0-9]{40}$")
        for lang in ("vi", "en"):
            revision = models.get(lang, {}).get("revision", "")
            self.assertTrue(
                bool(hex_40_re.match(revision)),
                f"Model revision for {lang} must be a 40-character hex commit hash, got: {revision}",
            )


class TestToneSpeedModulation(unittest.TestCase):
    """Validates tone speed modulation rules and base_speeds preservation."""

    def test_tone_speed_multipliers(self):
        self.assertEqual(TONE_SPEED_MULTIPLIERS.get("narrative_warm"), 1.00)
        self.assertEqual(TONE_SPEED_MULTIPLIERS.get("analytical_crisp"), 1.02)
        self.assertEqual(TONE_SPEED_MULTIPLIERS.get("reflective_slow"), 0.98)

    def test_resolve_tone_speed(self):
        # Base speed 1.0
        self.assertEqual(resolve_tone_speed(1.0, "narrative_warm"), 1.00)
        self.assertEqual(resolve_tone_speed(1.0, "analytical_crisp"), 1.02)
        self.assertEqual(resolve_tone_speed(1.0, "reflective_slow"), 0.98)
        self.assertEqual(resolve_tone_speed(1.0, None), 1.00)

        # Base speed scaling
        self.assertEqual(resolve_tone_speed(1.1, "narrative_warm"), 1.1)
        self.assertEqual(resolve_tone_speed(1.05, "analytical_crisp"), 1.071)
        self.assertEqual(resolve_tone_speed(0.95, "reflective_slow"), 0.931)

    def test_build_request_preserves_base_speeds_and_modulates_items(self):
        tmp = tempfile.TemporaryDirectory()
        try:
            root = Path(tmp.name)
            shutil.copytree(ROOT / "assets/voices", root / "assets/voices")
            cfg = read(ROOT / "config.json")
            cfg["colab_tts"]["enabled"] = True

            scenes = [
                {"scene_id": "SC01", "texts": ["Câu ấm áp."], "tone": "narrative_warm", "gaps": [], "tail": 0.4},
                {"scene_id": "SC02", "texts": ["Câu sắc sảo."], "tone": "analytical_crisp", "gaps": [], "tail": 0.4},
                {"scene_id": "SC03", "texts": ["Câu trầm ngâm."], "tone": "reflective_slow", "gaps": [], "tail": 0.4},
            ]

            req = build_request(root, cfg, scenes)
            self.assertEqual(req.get("base_speeds", {}).get("vi"), 1.0)
            item_speeds = [it["speed"] for it in req["items"]]
            self.assertEqual(item_speeds, [1.0, 1.02, 0.98])
        finally:
            tmp.cleanup()


class TestInlineEnglishSpansAndAcousticGap(unittest.TestCase):
    """Validates inline English spans extraction and the 0.18s acoustic gap."""

    def test_english_parts_extraction_with_vocabulary(self):
        text = 'Thói quen "deep work" giúp tăng năng suất vượt trội.'
        parts = adapters.english_parts(text, words=["deep work"])
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0]["lang"], "vi")
        self.assertEqual(parts[1]["lang"], "en")
        self.assertEqual(parts[1]["text"], "deep work")
        self.assertEqual(parts[2]["lang"], "vi")

    def test_audio_english_spans_gap_configuration(self):
        cfg = read(ROOT / "config.json")
        span_gap = cfg.get("audio_english_spans_gap", 0.18)
        self.assertEqual(span_gap, 0.18, "Default acoustic span gap must be 0.18s (180ms)")


class TestStandaloneSpinoffHooksGate(unittest.TestCase):
    """Validates the strict duration limit and identity contracts on spinoff hooks
    (0 < duration <= 3.0s) against production colab_bridge.protocol.validate_result.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        self.models = {"vi": {"revision": "a" * 40}}
        self.req_hook = {"id": "hook_01", "text": "Nghịch lý nhận thức", "item": 0}
        self.req = {
            "request_id": "req_test_spinoff_hooks",
            "primary_language": "vi",
            "profiles": {"vi": {"voice": "VietNarrator"}},
            "models": self.models,
            "segments": [],
            "english": [],
            "spinoff_hooks": [self.req_hook],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def _write_spinoff_result(
        self,
        hook_duration: float,
        hook_id: str = "hook_01",
        hook_text: str = "Nghịch lý nhận thức",
        wav_frames_duration: float | None = None,
        include_hook: bool = True,
    ):
        result = {
            "request_id": "req_test_spinoff_hooks",
            "voice": "VietNarrator",
            "engine": {"backend": "colab-omnivoice", "models": self.models, "device": "Tesla T4"},
            "segments": [],
            "spinoff_hooks": [],
        }
        if include_hook:
            wav_name = f"{hook_id}.wav"
            result["spinoff_hooks"].append({
                "id": hook_id,
                "text": hook_text,
                "path": wav_name,
                "duration": hook_duration,
            })
            actual_wav_dur = wav_frames_duration if wav_frames_duration is not None else max(0.0, hook_duration)
            wav_path = self.folder / wav_name
            with wave.open(str(wav_path), "wb") as w:
                w.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
                w.writeframes(b"\x00\x20" * round(actual_wav_dur * 48000))

        (self.folder / "tts-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))

    def test_spinoff_hook_valid_durations_accepted(self):
        """Durations in (0.0, 3.0] pass production validate_result."""
        for d in [0.5, 1.2, 2.8, 3.0]:
            self._write_spinoff_result(hook_duration=d)
            names = validate_result(self.folder, self.req)
            self.assertIn("hook_01.wav", names)
            self.assertIn("tts-result.json", names)

    def test_spinoff_hook_exceeded_duration_rejected(self):
        """Durations > 3.0s raise ValueError('Standalone hook identity/duration mismatch')."""
        for d in [3.01, 3.05, 3.5, 5.0]:
            self._write_spinoff_result(hook_duration=d)
            with self.assertRaises(ValueError) as ctx:
                validate_result(self.folder, self.req)
            self.assertEqual(str(ctx.exception), "Standalone hook identity/duration mismatch")

    def test_spinoff_hook_zero_or_negative_duration_rejected(self):
        """Durations <= 0.0s raise ValueError('Standalone hook identity/duration mismatch')."""
        for d in [0.0, -0.01, -0.5, -2.0]:
            self._write_spinoff_result(hook_duration=d)
            with self.assertRaises(ValueError) as ctx:
                validate_result(self.folder, self.req)
            self.assertEqual(str(ctx.exception), "Standalone hook identity/duration mismatch")

    def test_spinoff_hook_missing_audio_rejected(self):
        """Missing spinoff hooks raise ValueError('Missing standalone hook audio')."""
        self._write_spinoff_result(hook_duration=2.0, include_hook=False)
        with self.assertRaises(ValueError) as ctx:
            validate_result(self.folder, self.req)
        self.assertEqual(str(ctx.exception), "Missing standalone hook audio")

    def test_spinoff_hook_identity_mismatch_rejected(self):
        """Mismatched hook ID or text raises ValueError('Standalone hook identity/duration mismatch')."""
        self._write_spinoff_result(hook_duration=2.0, hook_id="wrong_hook_id")
        with self.assertRaises(ValueError) as ctx:
            validate_result(self.folder, self.req)
        self.assertEqual(str(ctx.exception), "Standalone hook identity/duration mismatch")

        self._write_spinoff_result(hook_duration=2.0, hook_text="Sai nội dung hook")
        with self.assertRaises(ValueError) as ctx:
            validate_result(self.folder, self.req)
        self.assertEqual(str(ctx.exception), "Standalone hook identity/duration mismatch")

    def test_spinoff_hook_wav_duration_mismatch_rejected(self):
        """Mismatch between metadata duration and actual WAV audio frames raises error."""
        # Claims 2.5s duration in JSON, but WAV file only contains 1.0s of audio frames
        self._write_spinoff_result(hook_duration=2.5, wav_frames_duration=1.0)
        with self.assertRaises(ValueError) as ctx:
            validate_result(self.folder, self.req)
        self.assertEqual(str(ctx.exception), "Remote duration/learner pause mismatch")


class TestVoiceProsodyAndCinemaDeliveryModes(unittest.TestCase):
    """Validates Wave 1A cinema prosody director and synchronized 6 cinema tone multipliers."""

    EXPECTED_CINEMA_KEYS = (
        "tense_whisper",
        "narrative_cinema",
        "tactical_breakdown",
        "urgent_escalation",
        "climax_heroic",
        "reflective_lesson",
    )

    def test_delivery_profiles_exact_specs_and_speed_ordering(self):
        from voice_prosody import (
            BASELINE_LUFS,
            VOICE_DELIVERY_PROFILES,
            resolve_delivery_profile,
        )

        self.assertEqual(BASELINE_LUFS, -14.0)
        self.assertEqual(set(VOICE_DELIVERY_PROFILES.keys()), set(self.EXPECTED_CINEMA_KEYS))

        for mode, prof in VOICE_DELIVERY_PROFILES.items():
            self.assertEqual(prof["mode"], mode)
            self.assertEqual(
                prof["effective_rate"],
                round(prof["omni_speed"] * prof["atempo"], 3),
            )
            self.assertIn("highpass=", prof["eq_chain"])
            self.assertIn("lowpass=", prof["eq_chain"])

        # Exact numeric spot checks
        self.assertEqual(VOICE_DELIVERY_PROFILES["tense_whisper"]["omni_speed"], 0.98)
        self.assertEqual(VOICE_DELIVERY_PROFILES["tense_whisper"]["atempo"], 1.10)
        self.assertEqual(VOICE_DELIVERY_PROFILES["tense_whisper"]["micro_gain_db"], -1.8)
        self.assertEqual(VOICE_DELIVERY_PROFILES["urgent_escalation"]["omni_speed"], 1.16)
        self.assertEqual(VOICE_DELIVERY_PROFILES["urgent_escalation"]["gap_after_sec"], 0.05)
        self.assertEqual(VOICE_DELIVERY_PROFILES["climax_heroic"]["micro_gain_db"], 1.5)
        self.assertEqual(VOICE_DELIVERY_PROFILES["reflective_lesson"]["gap_after_sec"], 0.32)

        # Speed ordering: tense_whisper < reflective_lesson < narrative_cinema/tactical_breakdown < climax_heroic < urgent_escalation
        eff = {k: VOICE_DELIVERY_PROFILES[k]["effective_rate"] for k in self.EXPECTED_CINEMA_KEYS}
        self.assertLess(eff["tense_whisper"], eff["reflective_lesson"])
        self.assertLess(eff["reflective_lesson"], eff["tactical_breakdown"])
        self.assertLess(eff["reflective_lesson"], eff["narrative_cinema"])
        self.assertLess(eff["tactical_breakdown"], eff["climax_heroic"])
        self.assertLess(eff["narrative_cinema"], eff["climax_heroic"])
        self.assertLess(eff["climax_heroic"], eff["urgent_escalation"])

        # resolve_delivery_profile returns defensive copy and defaults unknown/None to narrative_cinema
        resolved = resolve_delivery_profile("tactical_breakdown")
        self.assertEqual(resolved["mode"], "tactical_breakdown")
        resolved["omni_speed"] = 9.99
        self.assertEqual(VOICE_DELIVERY_PROFILES["tactical_breakdown"]["omni_speed"], 1.06)

        self.assertEqual(resolve_delivery_profile(None)["mode"], "narrative_cinema")
        self.assertEqual(resolve_delivery_profile("nonexistent_mode")["mode"], "narrative_cinema")

    def test_split_text_with_pauses_edge_cases(self):
        from voice_prosody import split_text_with_pauses

        self.assertEqual(split_text_with_pauses(""), [])
        self.assertEqual(split_text_with_pauses("   \n\t  "), [])

        # Plain text without pauses
        self.assertEqual(
            split_text_with_pauses("  Đêm mùng ba tại Hà Hồi.  "),
            [{"type": "speech", "text": "Đêm mùng ba tại Hà Hồi."}],
        )

        # Mixed ms, s, and bare >10 ms values
        parsed = split_text_with_pauses(
            "Khoan đã. [pause:550ms] Nghe rõ tiếng trống? [pause:0.5s] Rút lui ngay. [pause:600]"
        )
        self.assertEqual(
            parsed,
            [
                {"type": "speech", "text": "Khoan đã."},
                {"type": "pause", "seconds": 0.55},
                {"type": "speech", "text": "Nghe rõ tiếng trống?"},
                {"type": "pause", "seconds": 0.5},
                {"type": "speech", "text": "Rút lui ngay."},
                {"type": "pause", "seconds": 0.6},
            ],
        )

        # Leading/trailing pauses and consecutive whitespace-separated pauses merged cleanly
        consec = split_text_with_pauses("  [pause:300ms] [pause:0.4s] Bắt đầu. [pause:0ms]  ")
        self.assertEqual(
            consec,
            [
                {"type": "pause", "seconds": 0.7},
                {"type": "speech", "text": "Bắt đầu."},
            ],
        )

    def test_protocol_and_output_contract_tone_multipliers_sync(self):
        from output_contract import TONE_SPEED_MULTIPLIERS as CONTRACT_TONES
        from output_contract import resolve_tone_speed as contract_resolve_tone_speed

        expected_all = {
            "narrative_warm": 1.00,
            "analytical_crisp": 1.02,
            "reflective_slow": 0.98,
            "tense_whisper": 0.86,
            "narrative_cinema": 0.95,
            "tactical_breakdown": 0.96,
            "urgent_escalation": 1.07,
            "climax_heroic": 1.02,
            "reflective_lesson": 0.88,
        }
        self.assertEqual(TONE_SPEED_MULTIPLIERS, expected_all)
        self.assertEqual(CONTRACT_TONES, expected_all)

        for key, mult in expected_all.items():
            self.assertEqual(resolve_tone_speed(1.0, key), mult)
            self.assertEqual(contract_resolve_tone_speed(1.0, key), mult)


if __name__ == "__main__":
    unittest.main()
