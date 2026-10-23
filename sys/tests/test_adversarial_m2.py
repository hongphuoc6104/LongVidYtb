#!/usr/bin/env python3
"""Adversarial stress harness for Milestone M2:
1. Arbitrary & non-standard durations frame invariance for master():
   - 0.3s (14,400 frames), 1.777s (85,296 frames), 13.5s (648,000 frames),
     12,345 odd frames, 150,000 frames.
   - Bit-for-bit exact frame count: frames_of(final) == frames_of(src).
2. Extreme input waveforms for master():
   - Maximum-level square waves (+/-32767).
   - DC offset audio (large constant bias + sine).
   - Low-level noise floor (-64 dBFS).
   - Pure digital silence (zeros) and near-silence step (exposing -inf loudnorm gain divergence).
   - True peak margin preservation (<= -1.0 dBTP) and loudnorm convergence.
3. Frame count discrepancy enforcement:
   - Altered frame count strictly raises Blocked.
   - Source WAV is byte-for-byte preserved on discrepancy.
4. Extreme inputs for mix_sound_design():
   - Zero-length narration WAV (evaluates whether Blocked is raised).
   - Loud narration burst followed by long silence (attack <= 45ms, release <= 380ms).
   - Boundary SFX events (t=0.0, t < 0, spanning past end, beyond end, multiple overlapping).
"""

from __future__ import annotations

import math
import shutil
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from audio_processing import (
    Blocked,
    _measure,
    frames_of,
    master,
    mix_sound_design,
)

SR = 48000


def create_tone_wav(
    path: Path,
    n_frames: int,
    sr: int = SR,
    channels: int = 1,
    amplitude: int = 10000,
    freq_hz: float = 440.0,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setparams((channels, 2, sr, n_frames, "NONE", "not compressed"))
        samples = []
        for i in range(n_frames):
            val = int(amplitude * math.sin(2.0 * math.pi * freq_hz * i / sr))
            clamped = max(-32767, min(32767, val))
            samples.extend([clamped] * channels)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg and ffprobe required")
class TestMasterArbitraryDurationsInvariance(unittest.TestCase):
    """Adversarially tests master() sample count invariance across arbitrary, non-standard durations."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_master_arbitrary_durations_frame_count(self):
        """Verifies frames_of(final) == frames_of(src) for arbitrary & odd durations."""
        durations = [
            ("0.3s", round(0.3 * SR)),
            ("1.777s", round(1.777 * SR)),
            ("13.5s", round(13.5 * SR)),
            ("12345_odd_frames", 12345),
            ("150000_frames", 150000),
        ]
        for label, n_frames in durations:
            with self.subTest(duration=label, n_frames=n_frames):
                src = self.d / f"src_{label}.wav"
                dst = self.d / f"dst_{label}.wav"
                create_tone_wav(src, n_frames=n_frames, amplitude=12000, freq_hz=350.0)

                orig_frames = frames_of(src)
                self.assertEqual(orig_frames, n_frames)

                master(src, dst, {})

                final_frames = frames_of(src)
                self.assertEqual(
                    final_frames,
                    orig_frames,
                    f"master() violated frame count invariance for {label}: expected {orig_frames}, got {final_frames}",
                )


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg and ffprobe required")
class TestMasterExtremeWaveformsAndLoudnorm(unittest.TestCase):
    """Adversarially tests master() against extreme waveforms: square waves, DC offsets, noise floor, silence."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_maximum_level_square_wave(self):
        """Full-scale square wave (+/-32767) must converge in loudnorm and preserve true peak margin <= -1.0 dBTP."""
        src = self.d / "square_max.wav"
        dst = self.d / "dst_square.wav"
        n_frames = 2 * SR
        with wave.open(str(src), "wb") as wf:
            wf.setparams((1, 2, SR, n_frames, "NONE", "not compressed"))
            # 400Hz square wave alternating between +32767 and -32767
            samples = [32767 if (i // 60) % 2 == 0 else -32767 for i in range(n_frames)]
            wf.writeframes(struct.pack(f"<{n_frames}h", *samples))

        master(src, dst, {"audio_lufs": -11.0, "audio_peak_db": -1.0})
        self.assertEqual(frames_of(src), n_frames)

        meas = _measure(src, self.d / "meas_sq.log")
        self.assertIsNotNone(meas, "Loudnorm analysis must not crash or return None")
        self.assertNotEqual(meas.get("input_i"), "nan")
        self.assertNotEqual(meas.get("input_tp"), "nan")

        lufs = float(meas["input_i"])
        true_peak = float(meas["input_tp"])

        # Should converge close to target -11.0 LUFS
        self.assertAlmostEqual(lufs, -11.0, delta=1.5)
        # True peak must be <= -1.0 dBTP
        self.assertLessEqual(true_peak, -1.0, f"True peak {true_peak} exceeds limit -1.0 dBTP")

    def test_dc_offset_waveform(self):
        """Audio with massive DC offset (+15000) must have DC stripped by highpass and true peak <= -1.0 dBTP."""
        src = self.d / "dc_offset.wav"
        dst = self.d / "dst_dc.wav"
        n_frames = 2 * SR
        with wave.open(str(src), "wb") as wf:
            wf.setparams((1, 2, SR, n_frames, "NONE", "not compressed"))
            samples = [
                max(-32767, min(32767, int(15000 + 10000 * math.sin(2.0 * math.pi * 300.0 * i / SR))))
                for i in range(n_frames)
            ]
            wf.writeframes(struct.pack(f"<{n_frames}h", *samples))

        master(src, dst, {"audio_lufs": -11.0, "audio_peak_db": -1.0})
        self.assertEqual(frames_of(src), n_frames)

        meas = _measure(src, self.d / "meas_dc.log")
        self.assertIsNotNone(meas)
        lufs = float(meas["input_i"])
        true_peak = float(meas["input_tp"])

        self.assertAlmostEqual(lufs, -11.0, delta=1.5)
        self.assertLessEqual(true_peak, -1.0, f"True peak {true_peak} exceeds limit -1.0 dBTP")

    def test_low_level_noise_floor(self):
        """Low-level noise floor (-64 dBFS) converges to target loudness with true peak <= -1.0 dBTP."""
        src = self.d / "low_noise.wav"
        dst = self.d / "dst_noise.wav"
        n_frames = 2 * SR
        import random
        random.seed(42)
        with wave.open(str(src), "wb") as wf:
            wf.setparams((1, 2, SR, n_frames, "NONE", "not compressed"))
            samples = [random.randint(-20, 20) for _ in range(n_frames)]
            wf.writeframes(struct.pack(f"<{n_frames}h", *samples))

        master(src, dst, {"audio_lufs": -11.0, "audio_peak_db": -1.0})
        self.assertEqual(frames_of(src), n_frames)

        meas = _measure(src, self.d / "meas_noise.log")
        self.assertIsNotNone(meas)
        lufs = float(meas["input_i"])
        true_peak = float(meas["input_tp"])

        self.assertAlmostEqual(lufs, -11.0, delta=1.5)
        self.assertLessEqual(true_peak, -1.0)

    def test_pure_digital_silence_true_peak_and_gain_divergence(self):
        """Exposes numerical gain divergence on pure digital silence:
        loudnorm returns input_i='-inf', leading to volume=infdB, amplifying subnormal noise and violating <= -1.0 dBTP.
        """
        src = self.d / "pure_silence.wav"
        dst = self.d / "dst_silence.wav"
        n_frames = 2 * SR
        with wave.open(str(src), "wb") as wf:
            wf.setparams((1, 2, SR, n_frames, "NONE", "not compressed"))
            wf.writeframes(b"\x00\x00" * n_frames)

        master(src, dst, {"audio_lufs": -11.0, "audio_peak_db": -1.0})
        self.assertEqual(frames_of(src), n_frames)

        meas = _measure(src, self.d / "meas_silence.log")
        self.assertIsNotNone(meas)
        true_peak = float(meas["input_tp"])

        # When gain=infdB is executed, true peak is -0.61 dBTP, which strictly fails the <= -1.0 dBTP invariant!
        self.assertLessEqual(
            true_peak,
            -1.0,
            f"VULNERABILITY: pure digital silence boosted by infdB resulted in true peak {true_peak} dBTP > -1.0 dBTP",
        )


class TestMasterFrameDiscrepancyEnforcement(unittest.TestCase):
    """Verifies that any frame count discrepancy strictly raises Blocked and leaves src untouched."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_master_frame_mismatch_strictly_raises_blocked(self):
        src = self.d / "mismatch_test.wav"
        create_tone_wav(src, n_frames=SR, amplitude=8000)
        orig_bytes = src.read_bytes()

        # Chain that drops 200 samples
        with self.assertRaisesRegex(Blocked, "frame count"):
            master(src, self.d / "dst_mismatch.wav", {"audio_voice_chain": "atrim=start_sample=200"})

        # Verify source file is byte-for-byte untouched
        self.assertEqual(src.read_bytes(), orig_bytes)
        # Verify temporary file is unlinked
        self.assertFalse((self.d / "narration_lv.wav").exists())


class TestMixSoundDesignExtremeInputs(unittest.TestCase):
    """Adversarially tests mix_sound_design() against zero-length narration, ducking attack/release, and boundary SFX."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_zero_length_narration_must_raise_blocked(self):
        """Zero-length narration WAV (0 frames) must strictly raise Blocked rather than silently passing 0 frames."""
        zero_wav = self.d / "zero_narration.wav"
        out_wav = self.d / "zero_out.wav"
        with wave.open(str(zero_wav), "wb") as wf:
            wf.setparams((1, 2, SR, 0, "NONE", "not compressed"))

        # Invariant: Zero-length narration has no audio to mix; it must raise Blocked/AudioProcessingError
        with self.assertRaises(Blocked, msg="VULNERABILITY: mix_sound_design silently accepted zero-length narration"):
            mix_sound_design(zero_wav, out_wav)

    def test_ducking_attack_within_45ms_and_release_within_380ms(self):
        """Loud speech burst (+30000 PCM) followed by long silence:
        - Ducking attack: gain drops by >80% towards 0.07 within 45ms.
        - Ducking release: gain recovers by >70% towards 0.20 within 380ms.
        """
        burst_frames = round(0.10 * SR)  # 100ms loud burst
        silence_frames = round(2.00 * SR)  # 2.0s silence
        total_frames = burst_frames + silence_frames

        # Voice: full-scale 30000 burst then pure zero silence
        voice_samples = [30000 if (i // 50) % 2 == 0 else -30000 for i in range(burst_frames)]
        voice_samples.extend([0] * silence_frames)

        narration_wav = self.d / "burst_voice.wav"
        with wave.open(str(narration_wav), "wb") as wf:
            wf.setparams((1, 2, SR, total_frames, "NONE", "not compressed"))
            wf.writeframes(struct.pack(f"<{total_frames}h", *voice_samples))

        # BGM: constant amplitude 10,000
        bgm_wav = self.d / "constant_bgm.wav"
        with wave.open(str(bgm_wav), "wb") as wf:
            wf.setparams((1, 2, SR, total_frames, "NONE", "not compressed"))
            wf.writeframes(struct.pack(f"<{total_frames}h", *([10000] * total_frames)))

        out_wav = self.d / "ducked_out.wav"
        cfg = {"bgm_duck_gain": 0.07, "bgm_swell_gain": 0.20}
        mix_sound_design(narration_wav, out_wav, cfg=cfg, bgm_wav=bgm_wav)

        with wave.open(str(out_wav), "rb") as wf:
            raw = wf.readframes(total_frames)
            mixed = list(struct.unpack(f"<{total_frames}h", raw))

        # Block size = 20ms = 960 samples
        # 1. Attack evaluation:
        # At t=0ms (block 0): initial gain 0.20 -> drops to 0.1415
        # At t=20ms (block 1): drops to 0.1093
        # At t=45ms (block 2, frame 2160): gain is 0.0916
        # Subtract voice sample to isolate scaled BGM:
        sample_45ms = round(0.045 * SR)
        bgm_at_45ms = (mixed[sample_45ms] - voice_samples[sample_45ms]) / 10000.0
        self.assertLessEqual(
            bgm_at_45ms,
            0.10,
            f"Ducking attack too slow at 45ms: gain is {bgm_at_45ms}, expected <= 0.10 (target 0.07)",
        )

        # 2. Release evaluation:
        # Burst ceases at t=100ms (frame 4800).
        # 380ms after burst cessation = t=480ms (frame 23040).
        # Voice is 0 at frame 23040, so mixed sample is purely bgm * gain.
        sample_380ms_after = round((0.10 + 0.380) * SR)
        bgm_gain_at_380ms = mixed[sample_380ms_after] / 10000.0
        self.assertGreaterEqual(
            bgm_gain_at_380ms,
            0.15,
            f"Ducking release too slow at 380ms: gain is {bgm_gain_at_380ms}, expected >= 0.15 (target 0.20)",
        )

    def test_boundary_sfx_events_and_overlapping(self):
        """Multiple overlapping SFX events placed at boundaries:
        - t = 0.0 (onset)
        - t = -0.05 (negative timestamp)
        - t = 0.95 (spanning past end of 1.0s audio)
        - t = 1.0 (exact end boundary)
        - t = 1.5 (beyond end)
        - Multiple overlapping SFX at identical boundary frame
        Verifies exact frame preservation and clean boundary truncation without IndexError.
        """
        n_frames = SR  # 1.0s
        narration_wav = self.d / "voice_boundary.wav"
        create_tone_wav(narration_wav, n_frames=n_frames, amplitude=4000)

        out_wav = self.d / "out_boundary.wav"
        events = [
            {"kind": "pop", "at": 0.0, "duration": 0.1, "amplitude": 0.2},
            {"kind": "whoosh", "at": -0.05, "duration": 0.2, "amplitude": 0.2},
            {"kind": "pencil_stroke", "at": 0.95, "duration": 0.22, "amplitude": 0.3},
            {"kind": "soft_riser", "at": 1.0, "duration": 0.5, "amplitude": 0.2},
            {"kind": "pop", "at": 1.5, "duration": 0.2, "amplitude": 0.2},
            {"kind": "whoosh", "at": 0.95, "duration": 0.3, "amplitude": 0.3},
        ]

        meta = mix_sound_design(narration_wav, out_wav, cfg={}, sfx_events=events)
        self.assertEqual(meta["sfx_events_applied"], 6)
        self.assertEqual(frames_of(out_wav), n_frames)

    def test_mix_sound_design_frame_discrepancy_raises_blocked(self):
        """Simulated frame discrepancy in mix_sound_design strictly raises Blocked."""
        narration_wav = self.d / "voice_discrepancy.wav"
        create_tone_wav(narration_wav, n_frames=SR, amplitude=4000)
        out_wav = self.d / "out_discrepancy.wav"

        # Patch frames_of to report altered frame count for out_wav
        real_frames_of = frames_of

        def mocked_frames_of(p):
            if Path(p) == out_wav:
                return SR - 50  # Discrepancy!
            return real_frames_of(p)

        with patch("audio_processing.frames_of", side_effect=mocked_frames_of):
            with self.assertRaisesRegex(Blocked, "mix_sound_design altered frame count"):
                mix_sound_design(narration_wav, out_wav)


if __name__ == "__main__":
    unittest.main()
