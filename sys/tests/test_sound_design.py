"""Unit tests for procedural micro-SFX synthesis, sidechain BGM ducking, and sound design mixer."""

import math
import struct
import wave
from pathlib import Path

import pytest
from audio_processing import Blocked, frames_of, mix_sound_design, synthesize_micro_sfx

SR = 48000


def make_wav(
    path: Path,
    n_frames: int,
    sr: int = SR,
    channels: int = 1,
    sampwidth: int = 2,
    level: int = 8000,
    tone_hz: float = 220.0,
) -> None:
    """Helper to synthesize a test WAV file with specified channel, width, and sine tone."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sr)
        if sampwidth == 2:
            frames = []
            for i in range(n_frames):
                val = int(level * math.sin(2.0 * math.pi * tone_hz * i / sr))
                clamped = max(-32767, min(32767, val))
                frames.extend([clamped] * channels)
            wf.writeframes(struct.pack(f"<{len(frames)}h", *frames))
        elif sampwidth == 4:
            # 32-bit float or 32-bit int PCM
            frames = []
            for i in range(n_frames):
                val = int(level * 65536 * math.sin(2.0 * math.pi * tone_hz * i / sr))
                frames.extend([val] * channels)
            wf.writeframes(struct.pack(f"<{len(frames)}i", *frames))
        elif sampwidth == 1:
            # 8-bit unsigned PCM
            u_frames = [min(255, max(0, int(128 + 50 * math.sin(2.0 * math.pi * tone_hz * i / sr)))) for i in range(n_frames)]
            wf.writeframes(bytes(u_frames))


def read_samples(path: Path) -> list[int]:
    """Reads mono 16-bit PCM samples from a WAV file."""
    with wave.open(str(path), "rb") as wf:
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
        return list(struct.unpack(f"<{nframes}h", raw))


# ---------------------------------------------------------------------------
# Functional Group 1: Deterministic Micro-SFX Synthesis (synthesize_micro_sfx)
# ---------------------------------------------------------------------------


class TestSynthesizeMicroSfx:
    """Tests procedural deterministic waveform synthesis for pop, whoosh, pencil_stroke, soft_riser."""

    @pytest.mark.parametrize("kind", ["pop", "whoosh", "pencil_stroke", "soft_riser"])
    def test_waveform_determinism(self, kind: str):
        """Calling synthesize_micro_sfx twice with identical parameters yields bit-identical samples."""
        s1 = synthesize_micro_sfx(kind, duration_sec=0.22, sr=SR, amplitude=0.14)
        s2 = synthesize_micro_sfx(kind, duration_sec=0.22, sr=SR, amplitude=0.14)
        assert len(s1) == 10560
        assert s1 == s2

    @pytest.mark.parametrize(
        ("duration_sec", "expected_samples"),
        [
            (0.22, 10560),
            (0.10, 4800),
            (0.50, 24000),
            (0.00, 1),
            (-0.05, 1),
        ],
    )
    def test_sample_count_and_duration_scaling(self, duration_sec: float, expected_samples: int):
        """Sample count equals max(1, round(duration_sec * sr)) for all durations."""
        samples = synthesize_micro_sfx("pop", duration_sec=duration_sec, sr=SR, amplitude=0.14)
        assert len(samples) == expected_samples

    def test_amplitude_bounds_and_clamping(self):
        """Every generated sample is within [-32767, 32767], and zero amplitude produces pure zeros."""
        zero_samples = synthesize_micro_sfx("pop", duration_sec=0.1, sr=SR, amplitude=0.0)
        assert all(s == 0 for s in zero_samples)

        # High amplitude (e.g. 2.5) must clamp to int16 bounds without overflow wrap-around
        clipped = synthesize_micro_sfx("pop", duration_sec=0.1, sr=SR, amplitude=2.5)
        assert all(-32767 <= s <= 32767 for s in clipped)
        assert max(clipped) == 32767
        assert min(clipped) == -32767

        # Default amplitude 0.14 peak sample is strictly bounded
        default_samples = synthesize_micro_sfx("whoosh", duration_sec=0.22, sr=SR, amplitude=0.14)
        max_abs = max(abs(s) for s in default_samples)
        assert max_abs <= round(0.14 * 32767)

    def test_pop_characteristics(self):
        """'pop' exhibits exponential frequency drop (240Hz -> 85Hz), zero onset, and decay."""
        samples = synthesize_micro_sfx("pop", duration_sec=0.22, sr=SR, amplitude=0.14)
        assert samples[0] == 0
        # Peak absolute sample occurs in the first quarter (fast attack envelope)
        peak_idx = max(range(len(samples)), key=lambda i: abs(samples[i]))
        assert peak_idx < len(samples) // 4
        # Tail sample decays near 0
        assert abs(samples[-1]) <= 50

    def test_whoosh_characteristics(self):
        """'whoosh' has bell envelope: zero amplitude at endpoints, peak centered in middle."""
        samples = synthesize_micro_sfx("whoosh", duration_sec=0.22, sr=SR, amplitude=0.14)
        assert samples[0] == 0
        assert samples[-1] == 0
        # Peak absolute amplitude in central region
        peak_idx = max(range(len(samples)), key=lambda i: abs(samples[i]))
        assert len(samples) * 0.25 <= peak_idx <= len(samples) * 0.75

    def test_pencil_stroke_characteristics(self):
        """'pencil_stroke' produces texture with zero endpoints and zero-crossings."""
        samples = synthesize_micro_sfx("pencil_stroke", duration_sec=0.22, sr=SR, amplitude=0.14)
        assert samples[0] == 0
        assert samples[-1] == 0
        # Check that it produces high-frequency texture (many sign changes)
        zero_crossings = sum(
            1 for i in range(1, len(samples)) if (samples[i] >= 0 > samples[i - 1]) or (samples[i] < 0 <= samples[i - 1])
        )
        assert zero_crossings > 1000

    def test_soft_riser_characteristics(self):
        """'soft_riser' asymmetric swell envelope peaks in the second half of duration."""
        samples = synthesize_micro_sfx("soft_riser", duration_sec=0.22, sr=SR, amplitude=0.14)
        assert samples[0] == 0
        assert samples[-1] == 0
        peak_idx = max(range(len(samples)), key=lambda i: abs(samples[i]))
        assert peak_idx > len(samples) * 0.45

    def test_unknown_kind_defaults_to_soft_riser(self):
        """Unrecognized kind safely executes the soft_riser branch without exception."""
        unknown = synthesize_micro_sfx("futuristic_laser", duration_sec=0.22, sr=SR, amplitude=0.14)
        riser = synthesize_micro_sfx("soft_riser", duration_sec=0.22, sr=SR, amplitude=0.14)
        assert unknown == riser


# ---------------------------------------------------------------------------
# Functional Group 2: Voice-Only Mix Transparency (mix_sound_design)
# ---------------------------------------------------------------------------


class TestMixSoundDesignVoiceOnlyTransparency:
    """Verifies bit-exact sample passthrough and metadata when BGM and SFX are omitted."""

    def test_voice_only_produces_identical_samples(self, tmp_path: Path):
        narration_wav = tmp_path / "narration.wav"
        output_wav = tmp_path / "mixed.wav"
        n_frames = 48000 * 2  # 2.0s
        make_wav(narration_wav, n_frames=n_frames, level=12000, tone_hz=330.0)

        meta = mix_sound_design(narration_wav, output_wav, cfg={}, bgm_wav=None, sfx_events=None)

        assert meta["frames"] == n_frames
        assert meta["sample_rate"] == SR
        assert meta["sfx_events_applied"] == 0
        assert meta["bgm_mixed"] is False

        assert frames_of(output_wav) == n_frames
        assert read_samples(output_wav) == read_samples(narration_wav)

    def test_empty_sfx_events_and_missing_bgm_file(self, tmp_path: Path):
        """Missing BGM path does not crash and passes voice through untouched."""
        narration_wav = tmp_path / "narration.wav"
        output_wav = tmp_path / "mixed.wav"
        make_wav(narration_wav, n_frames=24000, level=9000, tone_hz=440.0)

        missing_bgm = tmp_path / "non_existent_bgm.wav"
        meta = mix_sound_design(narration_wav, output_wav, cfg={}, bgm_wav=missing_bgm, sfx_events=[])

        assert meta["bgm_mixed"] is False
        assert meta["sfx_events_applied"] == 0
        assert read_samples(output_wav) == read_samples(narration_wav)


# ---------------------------------------------------------------------------
# Functional Group 3: Sidechain BGM Ducking Envelope (mix_sound_design)
# ---------------------------------------------------------------------------


class TestMixSoundDesignSidechainDucking:
    """Verifies envelope-guided sidechain ducking, attack/release dynamics, and BGM looping."""

    def test_ducking_during_speech_and_swelling_during_pause(self, tmp_path: Path):
        """BGM ducks during speech (peak >= 450) and swells during narrative silence."""
        narration_wav = tmp_path / "speech_pause.wav"
        bgm_wav = tmp_path / "bgm.wav"
        output_wav = tmp_path / "mixed.wav"

        # 1.0s active speech (amplitude 10000) followed by 1.0s silence (total 2.0s = 96000 frames)
        speech_frames = 48000
        pause_frames = 48000
        total_frames = speech_frames + pause_frames

        # Create speech + pause narration
        voice_pcm = []
        for i in range(speech_frames):
            voice_pcm.append(int(10000 * math.sin(2.0 * math.pi * 300.0 * i / SR)))
        voice_pcm.extend([0] * pause_frames)

        with wave.open(str(narration_wav), "wb") as wf:
            wf.setparams((1, 2, SR, total_frames, "NONE", "not compressed"))
            wf.writeframes(struct.pack(f"<{total_frames}h", *voice_pcm))

        # Create continuous DC-offset-free BGM with constant amplitude 10000
        bgm_pcm = [int(10000 * math.sin(2.0 * math.pi * 100.0 * i / SR)) for i in range(total_frames)]
        with wave.open(str(bgm_wav), "wb") as bf:
            bf.setparams((1, 2, SR, total_frames, "NONE", "not compressed"))
            bf.writeframes(struct.pack(f"<{total_frames}h", *bgm_pcm))

        cfg = {"bgm_duck_gain": 0.07, "bgm_swell_gain": 0.20, "sidechain_threshold_pcm": 450}
        meta = mix_sound_design(narration_wav, output_wav, cfg=cfg, bgm_wav=bgm_wav)

        assert meta["bgm_mixed"] is True
        assert meta["frames"] == total_frames

        mixed_samples = read_samples(output_wav)

        # In pause region (e.g. t in [1.5s, 1.9s]), voice is 0, so mixed sample is purely bgm * gain
        # Measure RMS of mixed signal during pause
        pause_start_frame = int(1.5 * SR)
        pause_end_frame = int(1.9 * SR)
        pause_slice = mixed_samples[pause_start_frame:pause_end_frame]
        bgm_pause_slice = bgm_pcm[pause_start_frame:pause_end_frame]

        # Effective gain in pause should be close to swell_gain (0.20)
        rms_mixed = math.sqrt(sum(s * s for s in pause_slice) / len(pause_slice))
        rms_bgm = math.sqrt(sum(s * s for s in bgm_pause_slice) / len(bgm_pause_slice))
        effective_swell_gain = rms_mixed / rms_bgm
        assert abs(effective_swell_gain - 0.20) < 0.03

        # In sustained speech region (e.g. t in [0.3s, 0.9s]), isolate BGM by subtracting voice
        speech_sub_start = int(0.3 * SR)
        speech_sub_end = int(0.9 * SR)
        bgm_extracted = [
            mixed_samples[i] - voice_pcm[i] for i in range(speech_sub_start, speech_sub_end)
        ]
        bgm_original = bgm_pcm[speech_sub_start:speech_sub_end]
        rms_extracted = math.sqrt(sum(s * s for s in bgm_extracted) / len(bgm_extracted))
        rms_orig = math.sqrt(sum(s * s for s in bgm_original) / len(bgm_original))
        effective_duck_gain = rms_extracted / rms_orig
        assert abs(effective_duck_gain - 0.07) < 0.02

    def test_attack_and_release_time_constants(self, tmp_path: Path):
        """Attack drops rapidly within ~45ms (2-3 blocks), release recovers over ~380ms (15-20 blocks)."""
        # Create 0.5s pause, then 0.5s speech, then 1.0s pause (total 2.0s)
        nframes = 2 * SR
        voice_pcm = [0] * int(0.5 * SR)
        voice_pcm.extend([int(8000 * math.sin(2.0 * math.pi * 350.0 * i / SR)) for i in range(int(0.5 * SR))])
        voice_pcm.extend([0] * int(1.0 * SR))

        narration_wav = tmp_path / "n.wav"
        bgm_wav = tmp_path / "bgm.wav"
        output_wav = tmp_path / "out.wav"

        with wave.open(str(narration_wav), "wb") as wf:
            wf.setparams((1, 2, SR, nframes, "NONE", "not compressed"))
            wf.writeframes(struct.pack(f"<{nframes}h", *voice_pcm))

        # Constant amplitude BGM (10000)
        bgm_pcm = [10000] * nframes
        with wave.open(str(bgm_wav), "wb") as bf:
            bf.setparams((1, 2, SR, nframes, "NONE", "not compressed"))
            bf.writeframes(struct.pack(f"<{nframes}h", *bgm_pcm))

        cfg = {"bgm_duck_gain": 0.07, "bgm_swell_gain": 0.20, "sidechain_threshold_pcm": 450}
        mix_sound_design(narration_wav, output_wav, cfg=cfg, bgm_wav=bgm_wav)

        mixed = read_samples(output_wav)
        block_size = SR // 50  # 960 samples = 20ms

        # Inspect block gains from mixed samples during pause (where voice == 0):
        # Initial pause (t in [0, 0.4s]): gain is 0.20 -> bgm sample is 2000
        assert mixed[int(0.2 * SR)] == 2000

        # Speech onset is at 0.5s (block index 25).
        # At block 27 (40ms into speech), gain should already have dropped by more than 65% towards 0.07
        # Theoretical: g25 = 0.20, g26 = 0.20 + 0.45*(0.07 - 0.20) = 0.1415, g27 = 0.1415 + 0.45*(0.07 - 0.1415) = 0.109
        # Isolate BGM at block 27:
        b27_start = 27 * block_size
        b27_voice = voice_pcm[b27_start]
        b27_mixed = mixed[b27_start]
        b27_bgm_val = b27_mixed - b27_voice
        assert b27_bgm_val < 1300  # < 0.13 * 10000, fast attack!

        # Speech ceases at 1.0s (block 50). Release is slow (coeff 0.06):
        # 1 block after speech cessation (block 51): gain is still close to duck_gain (0.07)
        b51_start = 51 * block_size
        assert mixed[b51_start] < 900  # voice is 0, mixed is purely bgm

        # 18 blocks (~360ms) after speech cessation (block 68): gain recovers towards 0.20
        b68_start = 68 * block_size
        assert mixed[b68_start] > 1400  # > 0.14 * 10000

    def test_stereo_bgm_downmixing(self, tmp_path: Path):
        """2-channel stereo BGM is automatically downmixed to mono via channel 0 without crashing."""
        narration_wav = tmp_path / "narration.wav"
        output_wav = tmp_path / "mixed.wav"
        bgm_stereo_wav = tmp_path / "stereo_bgm.wav"

        nframes = 48000
        make_wav(narration_wav, n_frames=nframes, channels=1, level=5000)
        make_wav(bgm_stereo_wav, n_frames=nframes, channels=2, level=3000)

        meta = mix_sound_design(narration_wav, output_wav, cfg={}, bgm_wav=bgm_stereo_wav)
        assert meta["bgm_mixed"] is True
        assert frames_of(output_wav) == nframes

    def test_bgm_cyclic_looping(self, tmp_path: Path):
        """BGM shorter than narration loops cyclically without clicking or frame count deviation."""
        narration_wav = tmp_path / "narration.wav"
        output_wav = tmp_path / "mixed.wav"
        short_bgm_wav = tmp_path / "short_bgm.wav"

        # 4.0s narration, 0.5s BGM (loops 8 times)
        make_wav(narration_wav, n_frames=4 * SR, level=6000)
        make_wav(short_bgm_wav, n_frames=round(0.5 * SR), level=3000)

        meta = mix_sound_design(narration_wav, output_wav, cfg={}, bgm_wav=short_bgm_wav)
        assert meta["frames"] == 4 * SR
        assert frames_of(output_wav) == 4 * SR


# ---------------------------------------------------------------------------
# Functional Group 4: Timed Micro-SFX Overlay (mix_sound_design)
# ---------------------------------------------------------------------------


class TestMixSoundDesignSfxOverlay:
    """Verifies timed micro-SFX placement, soft-clipping protection, and boundary handling."""

    def test_exact_timestamp_placement(self, tmp_path: Path):
        """SFX placed at at_sec=1.0 starts exactly at frame sr (48000)."""
        narration_wav = tmp_path / "silence.wav"
        output_wav = tmp_path / "sfx_out.wav"
        nframes = 3 * SR  # 3.0s silence

        # Pure silence narration
        with wave.open(str(narration_wav), "wb") as wf:
            wf.setparams((1, 2, SR, nframes, "NONE", "not compressed"))
            wf.writeframes(b"\x00\x00" * nframes)

        sfx_event = {"kind": "pop", "at": 1.0, "duration": 0.22, "amplitude": 0.14}
        meta = mix_sound_design(narration_wav, output_wav, cfg={}, sfx_events=[sfx_event])

        assert meta["sfx_events_applied"] == 1
        mixed = read_samples(output_wav)

        # Before 1.0s (frame < 48000), all samples are 0
        assert all(s == 0 for s in mixed[:48000])

        # Exactly at frame 48000 to 48000 + 10560 - 1, matches synthesize_micro_sfx
        expected_sfx = synthesize_micro_sfx("pop", duration_sec=0.22, sr=SR, amplitude=0.14)
        assert mixed[48000 : 48000 + len(expected_sfx)] == expected_sfx

        # After the SFX ends, samples return to 0
        assert all(s == 0 for s in mixed[48000 + len(expected_sfx) :])

    def test_clipping_prevention_and_soft_ceiling(self, tmp_path: Path):
        """High voice + high SFX saturates cleanly at +/-32767 without int16 overflow wrap."""
        narration_wav = tmp_path / "loud_voice.wav"
        output_wav = tmp_path / "loud_out.wav"
        nframes = SR  # 1.0s

        # Voice at +30000 amplitude
        with wave.open(str(narration_wav), "wb") as wf:
            wf.setparams((1, 2, SR, nframes, "NONE", "not compressed"))
            wf.writeframes(struct.pack(f"<{nframes}h", *([30000] * nframes)))

        # SFX with high amplitude that would cause 30000 + 10000 = 40000 (> 32767)
        sfx_event = {"kind": "pop", "at": 0.1, "duration": 0.1, "amplitude": 1.0}
        mix_sound_design(narration_wav, output_wav, cfg={}, sfx_events=[sfx_event])

        mixed = read_samples(output_wav)
        assert all(-32767 <= s <= 32767 for s in mixed)
        # Peak sample is clamped to exactly 32767
        assert max(mixed) == 32767

    def test_multiple_overlapping_sfx_events(self, tmp_path: Path):
        """Multiple overlapping SFX events are all applied and counted."""
        narration_wav = tmp_path / "n.wav"
        output_wav = tmp_path / "out.wav"
        make_wav(narration_wav, n_frames=2 * SR, level=1000)

        events = [
            {"kind": "whoosh", "at": 0.2, "duration": 0.2, "amplitude": 0.1},
            {"kind": "pop", "at": 0.3, "duration": 0.1, "amplitude": 0.15},
            {"kind": "pencil_stroke", "at": 0.8, "duration": 0.2, "amplitude": 0.1},
        ]
        meta = mix_sound_design(narration_wav, output_wav, cfg={}, sfx_events=events)
        assert meta["sfx_events_applied"] == 3
        assert frames_of(output_wav) == 2 * SR

    def test_sfx_boundary_truncation(self, tmp_path: Path):
        """SFX placed near or spanning past the end truncates cleanly at nframes without padding or crash."""
        narration_wav = tmp_path / "n.wav"
        output_wav = tmp_path / "out.wav"
        nframes = round(1.0 * SR)  # 48000 frames
        make_wav(narration_wav, n_frames=nframes, level=1000)

        # SFX placed at 0.95s (frame 45600) with 0.22s duration (10560 frames, ending at 56160 > 48000)
        sfx_event = {"kind": "whoosh", "at": 0.95, "duration": 0.22, "amplitude": 0.14}
        meta = mix_sound_design(narration_wav, output_wav, cfg={}, sfx_events=[sfx_event])

        assert meta["sfx_events_applied"] == 1
        assert frames_of(output_wav) == nframes

        # SFX placed beyond end entirely (at=1.5s on 1.0s audio)
        sfx_beyond = {"kind": "pop", "at": 1.5, "duration": 0.1, "amplitude": 0.14}
        meta2 = mix_sound_design(narration_wav, output_wav, cfg={}, sfx_events=[sfx_beyond])
        assert meta2["sfx_events_applied"] == 1
        assert frames_of(output_wav) == nframes


# ---------------------------------------------------------------------------
# Functional Group 5: Strict Frame Invariance & Error Invariants
# ---------------------------------------------------------------------------


class TestMixSoundDesignInvariantsAndErrors:
    """Verifies strict sample count preservation and input format validation."""

    @pytest.mark.parametrize("dur_sec", [0.5, 1.37, 3.0, 7.5])
    def test_strict_frame_count_invariance_across_durations(self, tmp_path: Path, dur_sec: float):
        """frames_of(output_wav) == frames_of(narration_wav) for all durations."""
        narration_wav = tmp_path / f"n_{dur_sec}.wav"
        output_wav = tmp_path / f"out_{dur_sec}.wav"
        bgm_wav = tmp_path / f"bgm_{dur_sec}.wav"

        nframes = round(dur_sec * SR)
        make_wav(narration_wav, n_frames=nframes, level=4000)
        make_wav(bgm_wav, n_frames=SR, level=2000)

        sfx_events = [{"kind": "pop", "at": 0.1 * dur_sec, "duration": 0.1, "amplitude": 0.1}]
        meta = mix_sound_design(narration_wav, output_wav, cfg={}, bgm_wav=bgm_wav, sfx_events=sfx_events)

        assert meta["frames"] == nframes
        assert frames_of(output_wav) == nframes

    def test_non_mono_narration_raises_blocked(self, tmp_path: Path):
        """Stereo narration WAV raises Blocked exception."""
        narration_stereo = tmp_path / "stereo_narration.wav"
        output_wav = tmp_path / "out.wav"
        make_wav(narration_stereo, n_frames=48000, channels=2, level=5000)

        with pytest.raises(Blocked, match="mix_sound_design expects mono 16-bit PCM narration WAV"):
            mix_sound_design(narration_stereo, output_wav)

    def test_non_16bit_narration_raises_blocked(self, tmp_path: Path):
        """32-bit int PCM narration WAV raises Blocked exception."""
        narration_32bit = tmp_path / "32bit_narration.wav"
        output_wav = tmp_path / "out.wav"
        make_wav(narration_32bit, n_frames=48000, channels=1, sampwidth=4, level=5000)

        with pytest.raises(Blocked, match="mix_sound_design expects mono 16-bit PCM narration WAV"):
            mix_sound_design(narration_32bit, output_wav)

    def test_zero_length_narration_raises_blocked(self, tmp_path: Path):
        """Zero-length (0 frames) narration WAV strictly raises Blocked exception."""
        zero_wav = tmp_path / "zero_narration.wav"
        output_wav = tmp_path / "out.wav"
        with wave.open(str(zero_wav), "wb") as wf:
            wf.setparams((1, 2, SR, 0, "NONE", "not compressed"))

        with pytest.raises(Blocked, match="mix_sound_design expects non-empty narration audio"):
            mix_sound_design(zero_wav, output_wav)
