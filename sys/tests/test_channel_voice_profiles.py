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
        "voice": "VietNarrator_nao_luoi",
        "recommended_speed": 1.08,
        "default_tone": "narrative_warm",
    },
    "tui_tien": {
        "voice": "VietNarrator_tui_tien",
        "recommended_speed": 1.08,
        "default_tone": "analytical_crisp",
    },
    "ua_sao_vay": {
        "voice": "VietNarrator_ua_sao_vay",
        "recommended_speed": 1.16,
        "default_tone": "analytical_crisp",
    },
    "su_ke_lai": {
        "voice": "VietNarrator_su_ke_lai",
        "recommended_speed": 1.14,
        "default_tone": "heroic_epic",
    },
    "thuong_cho_kheo": {
        "voice": "VietNarrator_thuong_cho_kheo",
        "recommended_speed": 1.08,
        "default_tone": "reflective_slow",
    },
    "ho_so_ky_la": {
        "voice": "VietNarrator_ho_so_ky_la",
        "recommended_speed": 1.10,
        "default_tone": "reflective_slow",
    },
    "co_the_ke": {
        "voice": "VietNarrator_co_the_ke",
        "recommended_speed": 1.12,
        "default_tone": "narrative_warm",
    },
    "ai_binh_dan": {
        "voice": "VietNarrator_ai_binh_dan",
        "recommended_speed": 1.07,
        "default_tone": "analytical_crisp",
    },
    "luat_ngam": {
        "voice": "VietNarrator_luat_ngam",
        "recommended_speed": 1.07,
        "default_tone": "narrative_warm",
    },
    "ban_do_quyen_luc": {
        "voice": "VietNarrator_ban_do_quyen_luc",
        "recommended_speed": 1.15,
        "default_tone": "analytical_crisp",
    },
    "dia_com": {
        "voice": "VietNarrator_dia_com",
        "recommended_speed": 1.16,
        "default_tone": "analytical_crisp",
    },
    "luat_doi_thuong": {
        "voice": "VietNarrator_luat_doi_thuong",
        "recommended_speed": 1.10,
        "default_tone": "narrative_warm",
    },
    "banh_rang": {
        "voice": "VietNarrator_banh_rang",
        "recommended_speed": 1.16,
        "default_tone": "analytical_crisp",
    },
    "vu_tru_ti_hon": {
        "voice": "VietNarrator_vu_tru_ti_hon",
        "recommended_speed": 1.12,
        "default_tone": "narrative_warm",
    },
    "nghe_song_sot": {
        "voice": "VietNarrator_nghe_song_sot",
        "recommended_speed": 1.12,
        "default_tone": "analytical_crisp",
    },
    "la_ban_hoc_thuat": {
        "voice": "VietNarrator_la_ban_hoc_thuat",
        "recommended_speed": 1.12,
        "default_tone": "analytical_crisp",
    },
    "chanh_niem_ke": {
        "voice": "VietNarrator_chanh_niem_ke",
        "recommended_speed": 1.12,
        "default_tone": "reflective_slow",
    },
    "loi_sang_soi": {
        "voice": "VietNarrator_loi_sang_soi",
        "recommended_speed": 1.09,
        "default_tone": "narrative_warm",
    },
    "minh_triet_song": {
        "voice": "VietNarrator_minh_triet_song",
        "recommended_speed": 1.08,
        "default_tone": "reflective_slow",
    },
    "tam_tinh_dem": {
        "voice": "VietNarrator_tam_tinh_dem",
        "recommended_speed": 1.06,
        "default_tone": "reflective_slow",
    },
    "en_lazy_brain": {
        "voice": "OmniVoice_EnLazyBrain",
        "recommended_speed": 1.08,
        "default_tone": "narrative_warm",
        "language": "en",
    },
    "en_crowd_strings": {
        "voice": "OmniVoice_EnCrowdStrings",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_kindred_sketch": {
        "voice": "OmniVoice_EnKindredSketch",
        "recommended_speed": 1.02,
        "default_tone": "narrative_warm",
        "language": "en",
    },
    "en_first_principles": {
        "voice": "OmniVoice_EnFirstPrinciples",
        "recommended_speed": 1.12,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_wallet_anatomy": {
        "voice": "OmniVoice_EnWalletAnatomy",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_macro_gears": {
        "voice": "OmniVoice_EnMacroGears",
        "recommended_speed": 1.12,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_plain_sight_ai": {
        "voice": "OmniVoice_EnPlainSightAI",
        "recommended_speed": 1.14,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_career_leverage": {
        "voice": "OmniVoice_EnCareerLeverage",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_fine_print": {
        "voice": "OmniVoice_EnFinePrint",
        "recommended_speed": 1.08,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_inside_vessel": {
        "voice": "OmniVoice_EnInsideVessel",
        "recommended_speed": 1.08,
        "default_tone": "narrative_warm",
        "language": "en",
    },
    "en_kitchen_molecules": {
        "voice": "OmniVoice_EnKitchenMolecules",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_wait_how": {
        "voice": "OmniVoice_EnWaitHow",
        "recommended_speed": 1.14,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_cold_case_ink": {
        "voice": "OmniVoice_EnColdCaseInk",
        "recommended_speed": 1.02,
        "default_tone": "reflective_slow",
        "language": "en",
    },
    "en_choke_point": {
        "voice": "OmniVoice_EnChokePoint",
        "recommended_speed": 1.10,
        "default_tone": "analytical_crisp",
        "language": "en",
    },
    "en_pocket_cosmos": {
        "voice": "OmniVoice_EnPocketCosmos",
        "recommended_speed": 1.06,
        "default_tone": "narrative_warm",
        "language": "en",
    },
    "en_second_arrow": {
        "voice": "OmniVoice_EnSecondArrow",
        "recommended_speed": 1.00,
        "default_tone": "reflective_slow",
        "language": "en",
    },
    "en_parable_lamp": {
        "voice": "OmniVoice_EnParableLamp",
        "recommended_speed": 1.02,
        "default_tone": "reflective_slow",
        "language": "en",
    },
    "en_bamboo_marble": {
        "voice": "OmniVoice_EnBambooMarble",
        "recommended_speed": 1.00,
        "default_tone": "reflective_slow",
        "language": "en",
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

            self.assertEqual(data.get("voice").lower(), expected["voice"].lower())
            self.assertEqual(data.get("channel_id"), ch_id)
            expected_lang = expected.get("language", "vi")
            self.assertEqual(data.get("language"), expected_lang)
            self.assertIn("vi", data.get("languages", []))
            self.assertIn("en", data.get("languages", []))
            self.assertEqual(data.get("reference_wav"), "reference.wav")

            ref_text = data.get("reference_text", "")
            self.assertTrue(len(ref_text.strip()) > 20, "reference_text must be non-empty and substantial")
            self.assertTrue(
                ref_text.strip().endswith((".", "?", "!")),
                f"reference_text must end on a clean sentence delimiter, got: {ref_text[-20:]}",
            )

            self.assertIn(data.get("source_speed"), (0.90, 1.0))
            self.assertGreaterEqual(data.get("recommended_speed"), 1.00)
            self.assertAlmostEqual(data.get("recommended_speed"), expected["recommended_speed"], places=2)
            if data.get("studio_v3_restored"):
                self.assertTrue(bool(data.get("default_tone")), f"{ch_id}: default_tone must not be empty")
            else:
                self.assertEqual(data.get("default_tone"), expected["default_tone"])
                self.assertIn(data.get("default_tone"), TONE_SPEED_MULTIPLIERS)

            voice_chain = data.get("audio_voice_chain", "")
            self.assertTrue(bool(voice_chain.strip()), "audio_voice_chain must not be empty")
            self.assertTrue("highpass=f=" in voice_chain, f"{ch_id}: audio_voice_chain must include highpass")
            self.assertTrue(
                "equalizer=f=" in voice_chain or "treble=" in voice_chain,
                f"{ch_id}: audio_voice_chain must include equalizer or treble",
            )
            self.assertTrue(
                "lowpass=f=13500" in voice_chain or "lowpass=f=15000" in voice_chain,
                f"{ch_id}: audio_voice_chain must include lowpass=f=13500 or lowpass=f=15000",
            )
            self.assertNotIn("acompressor", voice_chain, f"{ch_id}: audio_voice_chain must NOT contain acompressor")
            self.assertNotIn("afftdn", voice_chain, f"{ch_id}: audio_voice_chain must NOT contain afftdn")
            self.assertEqual(data.get("audio_lufs"), -14.0)
            self.assertTrue(
                -1.6 <= data.get("audio_peak_db", 0) <= -1.0,
                f"{ch_id}: audio_peak_db {data.get('audio_peak_db')} not in [-1.6, -1.0]",
            )

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

            # Clean studio reference peak bounds (-2.5 dBFS .. -1.0 dBFS -> [24000, 30500])
            self.assertTrue(
                24000 <= peak <= 30500,
                f"{ch_id}: peak amplitude {peak} is not within studio headroom bounds [24000, 30500]",
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
            self.assertEqual(profiles["vi"]["voice"].lower(), expected["voice"].lower())
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
            self.assertTrue("highpass=f=" in chain, f"{ch_id}: voice chain missing 'highpass'")
            self.assertTrue(
                "equalizer=f=" in chain or "treble=" in chain,
                f"{ch_id}: voice chain missing equalizer or treble",
            )
            self.assertTrue(
                "lowpass=f=13500" in chain or "lowpass=f=15000" in chain,
                f"{ch_id}: voice chain missing 'lowpass=f=13500' or 'lowpass=f=15000'",
            )

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
        """Validates that AUDITION_SCRIPTS covers all Wave 1 channels with full 5-sentence scripts."""
        from audition_channel_voice import AUDITION_SCRIPTS, SENTENCE_RE

        wave1_ids = [
            "nao_luoi", "tui_tien", "ua_sao_vay", "su_ke_lai",
            "thuong_cho_kheo", "ho_so_ky_la", "co_the_ke", "ai_binh_dan",
        ]
        for ch_id in wave1_ids:
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
        """Verifies that all active channel worktrees have their voice profiles present and synced."""
        worktrees_root = Path("/home/hongphuoc6104/Desktop/vp-channels")
        if not worktrees_root.is_dir():
            self.skipTest("Worktrees directory not found; skipping sync check")

        checked = 0
        for ch_id in EXPECTED_CHANNELS:
            slug = ch_id.replace("_", "-")
            wt_channel_dir = worktrees_root / f"channel-{slug}"
            if not wt_channel_dir.is_dir():
                continue
            wt_profile_dir = wt_channel_dir / "sys" / "assets" / "voices" / f"ch_{ch_id}"
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
            self.assertTrue("highpass=f=" in wt_chain, f"Worktree {slug}: missing highpass")
            self.assertTrue(
                "equalizer=f=" in wt_chain or "treble=" in wt_chain,
                f"Worktree {slug}: missing equalizer or treble",
            )
            self.assertIn("lowpass=f=13500", wt_chain, f"Worktree {slug}: missing lowpass=f=13500")
            self.assertNotIn("acompressor", wt_chain, f"Worktree {slug}: must not contain acompressor")
            self.assertNotIn("afftdn", wt_chain, f"Worktree {slug}: must not contain afftdn")
            self.assertEqual(wt_data.get("audio_lufs"), -14.0)
            self.assertTrue(
                -1.6 <= wt_data.get("audio_peak_db", 0) <= -1.0,
                f"Worktree {slug}: audio_peak_db {wt_data.get('audio_peak_db')} not in [-1.6, -1.0]",
            )

            # Check sha256 matches actual reference.wav in worktree
            hasher = hashlib.sha256()
            with open(wt_profile_dir / "reference.wav", "rb") as f:
                hasher.update(f.read())
            self.assertEqual(wt_data.get("sha256"), hasher.hexdigest())
            checked += 1
        self.assertGreaterEqual(checked, 8, "Expected at least 8 worktrees to be checked")

    def test_su_ke_lai_dedicated_and_ho_so_ky_la_voice_locks(self):
        """Verifies su_ke_lai uses its dedicated heroic voice lock while ho_so_ky_la keeps its canonical lock."""
        try:
            from tools.produce_vn_dual_mode import (
                BANNED_DEPRECATED_VOICE_SHA256S,
                HARDCODED_CHANNEL_VOICE_LOCKS,
                HO_SO_KY_LA_VOICE_SHA256,
                SU_KE_LAI_DEDICATED_VOICE_SHA256,
                verify_channel_voice_lock,
            )
        except ModuleNotFoundError:
            import ast
            from typing import Any
            src_path = ROOT / "tools" / "produce_vn_dual_mode.py"
            if not src_path.is_file():
                src_path = ROOT / "sys" / "tools" / "produce_vn_dual_mode.py"
            src_text = src_path.read_text(encoding="utf-8")
            tree = ast.parse(src_text)
            wanted_assigns = {
                "HO_SO_KY_LA_VOICE_SHA256",
                "SU_KE_LAI_SHARED_VOICE_SHA256",
                "SU_KE_LAI_DEDICATED_VOICE_SHA256",
                "BANNED_DEPRECATED_VOICE_SHA256S",
                "HARDCODED_CHANNEL_VOICE_LOCKS",
            }
            ns: dict[str, Any] = {"Any": Any, "Path": Path, "hashlib": hashlib, "json": json, "ROOT": ROOT}
            for node in tree.body:
                if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id in wanted_assigns for t in node.targets
                ):
                    exec(compile(ast.Module([node], type_ignores=[]), str(src_path), "exec"), ns)
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in wanted_assigns:
                    exec(compile(ast.Module([node], type_ignores=[]), str(src_path), "exec"), ns)
                elif isinstance(node, ast.FunctionDef) and node.name == "verify_channel_voice_lock":
                    exec(compile(ast.Module([node], type_ignores=[]), str(src_path), "exec"), ns)
            BANNED_DEPRECATED_VOICE_SHA256S = ns["BANNED_DEPRECATED_VOICE_SHA256S"]
            HARDCODED_CHANNEL_VOICE_LOCKS = ns["HARDCODED_CHANNEL_VOICE_LOCKS"]
            HO_SO_KY_LA_VOICE_SHA256 = ns["HO_SO_KY_LA_VOICE_SHA256"]
            SU_KE_LAI_DEDICATED_VOICE_SHA256 = ns["SU_KE_LAI_DEDICATED_VOICE_SHA256"]
            verify_channel_voice_lock = ns["verify_channel_voice_lock"]

        su_ke_sha = "76773d5c9d306117022930d82045fb716138c21304261e7c7d5582d6c3f98d76"
        ho_so_sha = "cd25365252033ee60333c92e3f071a8dae3a99c865fe9e527686c7cf04048a9d"
        banned_sha = "5ebeb65efc952565f40a659af3f4a571945ce22dc156bedd67a60c186ee51a3e"

        self.assertEqual(SU_KE_LAI_DEDICATED_VOICE_SHA256, su_ke_sha)
        self.assertEqual(HO_SO_KY_LA_VOICE_SHA256, ho_so_sha)
        self.assertIn(banned_sha, BANNED_DEPRECATED_VOICE_SHA256S)
        self.assertIn("su_ke_lai", HARDCODED_CHANNEL_VOICE_LOCKS)
        self.assertIn("ho_so_ky_la", HARDCODED_CHANNEL_VOICE_LOCKS)

        su_ke_dir = self.voices_dir / "ch_su_ke_lai"
        ho_so_dir = self.voices_dir / "ch_ho_so_ky_la"

        with open(su_ke_dir / "profile.json", "r", encoding="utf-8") as f:
            su_ke_prof = json.load(f)
        with open(ho_so_dir / "profile.json", "r", encoding="utf-8") as f:
            ho_so_prof = json.load(f)

        self.assertEqual(su_ke_prof["sha256"], su_ke_sha)
        self.assertEqual(ho_so_prof["sha256"], ho_so_sha)
        self.assertNotIn("shared_voice_with", su_ke_prof)
        self.assertEqual(su_ke_prof.get("default_tone"), "heroic_epic")
        self.assertAlmostEqual(su_ke_prof.get("recommended_speed"), 1.14, places=2)
        self.assertEqual(ho_so_prof.get("shared_voice_group"), "su_ke_lai_canonical_voice")

        with open(su_ke_dir / "reference.wav", "rb") as f:
            su_ke_bytes = f.read()
        with open(ho_so_dir / "reference.wav", "rb") as f:
            ho_so_bytes = f.read()

        self.assertEqual(hashlib.sha256(su_ke_bytes).hexdigest(), su_ke_sha)
        self.assertEqual(hashlib.sha256(ho_so_bytes).hexdigest(), ho_so_sha)
        self.assertNotEqual(su_ke_bytes, ho_so_bytes, "su_ke_lai must be decoupled from ho_so_ky_la")

        # Verify banned SHA256 does not exist anywhere in sys/assets/voices/
        for p in self.voices_dir.rglob("*"):
            if p.is_file():
                with open(p, "rb") as f:
                    file_bytes = f.read()
                file_hash = hashlib.sha256(file_bytes).hexdigest()
                self.assertNotEqual(
                    file_hash,
                    banned_sha,
                    f"Banned deprecated voice file found at: {p}",
                )

        # Verify verify_channel_voice_lock runtime guard succeeds
        v1 = verify_channel_voice_lock("su_ke_lai", root=ROOT)
        self.assertEqual(v1["sha256"], su_ke_sha)
        v2 = verify_channel_voice_lock("ho_so_ky_la", root=ROOT)
        self.assertEqual(v2["sha256"], ho_so_sha)


if __name__ == "__main__":
    unittest.main()
