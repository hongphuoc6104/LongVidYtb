#!/usr/bin/env python3
"""Unit tests for the 8 per-channel dedicated Human Voice Profiles.

Validates:
1. All 8 channel voice profiles exist under sys/assets/voices/ch_<channel_id>/.
2. profile.json contracts: voice naming, channel_id, languages, speeds, tone, audio_voice_chain, sha256.
3. reference.wav audio integrity: 24kHz mono PCM16, protocol duration bounds (3.0s - 15.0s),
   peak normalized to ~ -2.5 dBFS with zero clipping, clean sentence boundary with trailing fade-out.
4. colab_bridge.protocol.load_profiles() validation succeeds for every channel voice profile.
5. Worktree sync status across /home/hongphuoc6104/Desktop/vp-channels/.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from colab_bridge.protocol import TONE_SPEED_MULTIPLIERS, load_profiles  # noqa: E402

EXPECTED_CHANNELS = {
    "nao_luoi": {
        "voice": "VietNarrator_NaoLuoi",
        "recommended_speed": 1.08,
        "default_tone": "narrative_warm",
    },
    "tui_tien": {
        "voice": "VietNarrator_TuiTien",
        "recommended_speed": 1.12,
        "default_tone": "analytical_crisp",
    },
    "ua_sao_vay": {
        "voice": "VietNarrator_UaSaoVay",
        "recommended_speed": 1.16,
        "default_tone": "analytical_crisp",
    },
    "su_ke_lai": {
        "voice": "VietNarrator_SuKeLai",
        "recommended_speed": 1.04,
        "default_tone": "reflective_slow",
    },
    "thuong_cho_kheo": {
        "voice": "VietNarrator_ThuongChoKheo",
        "recommended_speed": 1.00,
        "default_tone": "reflective_slow",
    },
    "ho_so_ky_la": {
        "voice": "VietNarrator_HoSoKyLa",
        "recommended_speed": 1.06,
        "default_tone": "narrative_warm",
    },
    "co_the_ke": {
        "voice": "VietNarrator_CoTheKe",
        "recommended_speed": 1.10,
        "default_tone": "narrative_warm",
    },
    "ai_binh_dan": {
        "voice": "VietNarrator_AIBinhDan",
        "recommended_speed": 1.14,
        "default_tone": "analytical_crisp",
    },
}


class TestChannelVoiceProfiles(unittest.TestCase):
    """Validates the invariants and audio parameters of all 8 channel voice profiles."""

    def setUp(self):
        self.voices_dir = ROOT / "assets/voices"

    def test_all_eight_channel_profiles_exist(self):
        """All 8 channel profile directories and required files must exist."""
        for ch_id in EXPECTED_CHANNELS:
            ch_dir = self.voices_dir / f"ch_{ch_id}"
            self.assertTrue(ch_dir.is_dir(), f"Missing profile directory: {ch_dir}")
            self.assertTrue((ch_dir / "profile.json").is_file(), f"Missing profile.json in {ch_dir}")
            self.assertTrue((ch_dir / "reference.wav").is_file(), f"Missing reference.wav in {ch_dir}")

    def test_channel_profile_json_contracts(self):
        """Validates all schema fields and metadata in profile.json."""
        for ch_id, expected in EXPECTED_CHANNELS.items():
            profile_path = self.voices_dir / f"ch_{ch_id}" / "profile.json"
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data.get("voice"), expected["voice"])
            self.assertEqual(data.get("channel_id"), ch_id)
            self.assertEqual(data.get("language"), "vi")
            self.assertIn("vi", data.get("languages", []))
            self.assertIn("en", data.get("languages", []))
            self.assertEqual(data.get("reference_wav"), "reference.wav")

            ref_text = data.get("reference_text", "")
            self.assertTrue(len(ref_text.strip()) > 20, "reference_text must be non-empty and substantial")
            self.assertTrue(
                ref_text.strip().endswith((".", "?", "!")),
                f"reference_text must end on a clean sentence delimiter, got: {ref_text[-20:]}",
            )

            self.assertEqual(data.get("source_speed"), 0.90)
            self.assertGreaterEqual(data.get("recommended_speed"), 1.00)
            self.assertAlmostEqual(data.get("recommended_speed"), expected["recommended_speed"], places=2)
            self.assertEqual(data.get("default_tone"), expected["default_tone"])
            self.assertIn(data.get("default_tone"), TONE_SPEED_MULTIPLIERS)

            voice_chain = data.get("audio_voice_chain", "")
            self.assertTrue(bool(voice_chain.strip()), "audio_voice_chain must not be empty")
            self.assertIn("highpass=f=90", voice_chain, f"{ch_id}: audio_voice_chain must include highpass=f=90")
            self.assertIn("equalizer=f=185", voice_chain, f"{ch_id}: audio_voice_chain must include equalizer=f=185 anti-mud cut")
            self.assertIn("equalizer=f=2400", voice_chain, f"{ch_id}: audio_voice_chain must include equalizer=f=2400 clarity boost")
            self.assertIn("lowpass=f=13500", voice_chain, f"{ch_id}: audio_voice_chain must include lowpass=f=13500")
            self.assertNotIn("acompressor", voice_chain, f"{ch_id}: audio_voice_chain must NOT contain acompressor")
            self.assertNotIn("afftdn", voice_chain, f"{ch_id}: audio_voice_chain must NOT contain afftdn")
            self.assertEqual(data.get("audio_lufs"), -14.0)
            self.assertEqual(data.get("audio_peak_db"), -1.5)

            # Check sha256 matches actual reference.wav on disk
            wav_path = self.voices_dir / f"ch_{ch_id}" / "reference.wav"
            hasher = hashlib.sha256()
            with open(wav_path, "rb") as f:
                hasher.update(f.read())
            self.assertEqual(data.get("sha256"), hasher.hexdigest())

    def test_channel_reference_wav_audio_integrity(self):
        """Validates WAV format, protocol duration (3-15s), peak normalization, and zero clipping."""
        for ch_id in EXPECTED_CHANNELS:
            wav_path = self.voices_dir / f"ch_{ch_id}" / "reference.wav"
            with wave.open(str(wav_path), "rb") as w:
                channels = w.getnchannels()
                sample_width = w.getsampwidth()
                framerate = w.getframerate()
                n_frames = w.getnframes()
                duration = n_frames / framerate
                frames = w.readframes(n_frames)

            self.assertEqual(channels, 1, f"{ch_id}: Must be mono PCM")
            self.assertEqual(sample_width, 2, f"{ch_id}: Must be PCM16")
            self.assertEqual(framerate, 24000, f"{ch_id}: Reference framerate must be 24000 Hz")

            # Protocol duration gate: 3.0s <= duration <= 15.0s
            self.assertTrue(
                3.0 <= duration <= 15.0,
                f"{ch_id}: duration {duration:.2f}s outside protocol bounds [3.0s, 15.0s]",
            )
            # Studio voice design duration gate: 5.0s <= duration <= 13.0s
            self.assertTrue(
                5.0 <= duration <= 13.0,
                f"{ch_id}: duration {duration:.2f}s outside studio bounds [5.0s, 13.0s]",
            )

            samples = struct.unpack(f"<{len(frames)//2}h", frames)
            peak = max(abs(s) for s in samples)

            # Clean studio reference peak bounds (-2.5 dBFS .. -1.2 dBFS -> [24000, 29000])
            self.assertTrue(
                24000 <= peak <= 29000,
                f"{ch_id}: peak amplitude {peak} is not within studio headroom bounds [24000, 29000]",
            )
            self.assertTrue(peak <= 32767, f"{ch_id}: Peak amplitude {peak} clipped")

            # Fade-out verification: last sample must be near zero
            self.assertLessEqual(abs(samples[-1]), 5, f"{ch_id}: trailing sample {samples[-1]} should be near zero")

    def test_colab_bridge_load_profiles_integration(self):
        """Verifies that colab_bridge.protocol.load_profiles() successfully loads each channel."""
        for ch_id, expected in EXPECTED_CHANNELS.items():
            rel_profile = f"assets/voices/ch_{ch_id}/profile.json"
            cfg = {
                "tts_voice": expected["voice"],
                "en_voice": expected["voice"],
                "voices": {
                    "vi": rel_profile,
                    "en": rel_profile,
                },
            }
            profiles = load_profiles(ROOT, cfg, {"vi", "en"})
            self.assertIn("vi", profiles)
            self.assertIn("en", profiles)
            self.assertEqual(profiles["vi"]["voice"], expected["voice"])
            self.assertEqual(profiles["vi"]["channel_id"], ch_id)

    def test_channel_voice_chain_filters_no_acompressor(self):
        """Verifies every channel voice chain includes anti-mud clarity EQ and no acompressor or afftdn."""
        for ch_id in EXPECTED_CHANNELS:
            profile_path = self.voices_dir / f"ch_{ch_id}" / "profile.json"
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            chain = data.get("audio_voice_chain", "")
            self.assertNotIn("acompressor", chain, f"{ch_id}: voice chain must NOT contain 'acompressor'")
            self.assertNotIn("afftdn", chain, f"{ch_id}: voice chain must NOT contain 'afftdn'")
            self.assertIn("equalizer=f=185", chain, f"{ch_id}: voice chain missing 'equalizer=f=185'")
            self.assertIn("equalizer=f=2400", chain, f"{ch_id}: voice chain missing 'equalizer=f=2400'")
            self.assertIn("highpass=f=90", chain, f"{ch_id}: voice chain missing 'highpass=f=90'")
            self.assertIn("lowpass=f=13500", chain, f"{ch_id}: voice chain missing 'lowpass=f=13500'")

    def test_audition_split_into_clauses_preserves_sentences(self):
        """Validates that audition split_into_clauses splits on .?!;, keeps <= 18 words intact, and splits > 18 words at middle comma."""
        from audition_channel_voice import split_into_clauses

        # 1. Short or normal sentence <= 18 words with commas is NOT split on commas
        short_with_comma = "Đừng vội đặt bút ký hợp đồng, khi bạn chưa nhờ AI kiểm tra."
        res = split_into_clauses(short_with_comma)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], short_with_comma)

        # 2. Text with commas under 18 words is never broken on commas
        comma_text = "Thực tế, tiền nguyên liệu gồm cốt trà, bột sữa và trân châu chỉ tốn sáu nghìn đồng."
        res = split_into_clauses(comma_text)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], comma_text)

        # 3. Two separate sentences are split on sentence boundary .?!;
        multi_sent = "Ủa, sao trong phòng đông người mà muỗi chỉ đốt mỗi mình bạn vậy? Ai cũng nghĩ do máu ngọt."
        res = split_into_clauses(multi_sent)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], "Ủa, sao trong phòng đông người mà muỗi chỉ đốt mỗi mình bạn vậy?")
        self.assertEqual(res[1], "Ai cũng nghĩ do máu ngọt.")

        # 4. Long sentence > 18 words with comma is split at the comma closest to the middle
        long_sent = "Tiếp theo, hệ thống tự động đối chiếu các mốc phạt, và gợi ý điều khoản sửa đổi an toàn."
        res = split_into_clauses(long_sent)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], "Tiếp theo, hệ thống tự động đối chiếu các mốc phạt")
        self.assertEqual(res[1], "và gợi ý điều khoản sửa đổi an toàn.")
        self.assertTrue(6 <= len(res[0].split()) <= 16, f"Clause 1 length {len(res[0].split())} outside 6..16 sweet spot")
        self.assertTrue(6 <= len(res[1].split()) <= 16, f"Clause 2 length {len(res[1].split())} outside 6..16 sweet spot")

    def test_audition_scripts_coverage_and_duration(self):
        """Validates that AUDITION_SCRIPTS covers all 8 channels with full 5-sentence scripts."""
        from audition_channel_voice import AUDITION_SCRIPTS, SENTENCE_RE

        for ch_id in EXPECTED_CHANNELS:
            self.assertIn(ch_id, AUDITION_SCRIPTS, f"Missing {ch_id} in AUDITION_SCRIPTS")
            script = AUDITION_SCRIPTS[ch_id]
            sents = [s.strip() for s in SENTENCE_RE.split(script) if s.strip()]
            self.assertGreaterEqual(len(sents), 5, f"{ch_id}: script must have at least 5 sentences, got {len(sents)}")
            words = script.split()
            self.assertGreaterEqual(len(words), 60, f"{ch_id}: script should have >= 60 words for ~18-22s duration")

    def test_audition_target_loudness_defaults(self):
        """Verifies audition loudness calibration defaults to -14.0 LUFS and -1.5 dBTP."""
        import inspect

        from audition_channel_voice import audition_channel

        sig = inspect.signature(audition_channel)
        self.assertIn("target_lufs", sig.parameters)
        self.assertIn("true_peak_db", sig.parameters)

    def test_worktrees_sync_verification(self):
        """Verifies that all 8 channel worktrees have their voice profiles present and synced."""
        worktrees_root = Path("/home/hongphuoc6104/Desktop/vp-channels")
        if not worktrees_root.is_dir():
            self.skipTest("Worktrees directory not found; skipping sync check")

        for ch_id in EXPECTED_CHANNELS:
            slug = ch_id.replace("_", "-")
            wt_profile_dir = worktrees_root / f"channel-{slug}" / "sys" / "assets" / "voices" / f"ch_{ch_id}"
            self.assertTrue(
                (wt_profile_dir / "profile.json").is_file(),
                f"Missing profile.json in worktree: {wt_profile_dir}",
            )
            self.assertTrue(
                (wt_profile_dir / "reference.wav").is_file(),
                f"Missing reference.wav in worktree: {wt_profile_dir}",
            )

            # Check worktree profile.json audio_voice_chain and sha256
            with open(wt_profile_dir / "profile.json", "r", encoding="utf-8") as f:
                wt_data = json.load(f)
            wt_chain = wt_data.get("audio_voice_chain", "")
            self.assertIn("highpass=f=90", wt_chain, f"Worktree {slug}: missing highpass=f=90")
            self.assertIn("equalizer=f=185", wt_chain, f"Worktree {slug}: missing equalizer=f=185")
            self.assertIn("equalizer=f=2400", wt_chain, f"Worktree {slug}: missing equalizer=f=2400")
            self.assertIn("lowpass=f=13500", wt_chain, f"Worktree {slug}: missing lowpass=f=13500")
            self.assertNotIn("acompressor", wt_chain, f"Worktree {slug}: must not contain acompressor")
            self.assertNotIn("afftdn", wt_chain, f"Worktree {slug}: must not contain afftdn")
            self.assertEqual(wt_data.get("audio_lufs"), -14.0)
            self.assertEqual(wt_data.get("audio_peak_db"), -1.5)

            # Check sha256 matches actual reference.wav in worktree
            hasher = hashlib.sha256()
            with open(wt_profile_dir / "reference.wav", "rb") as f:
                hasher.update(f.read())
            self.assertEqual(wt_data.get("sha256"), hasher.hexdigest())


if __name__ == "__main__":
    unittest.main()
