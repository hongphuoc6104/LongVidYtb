"""Unit tests for the Reborn Long Cinema engine.

Run:
    PYTHONPATH=sys sys/.venv/bin/pytest sys/tests/test_reborn_long_cinema.py -q
"""

from __future__ import annotations

import json

import numpy as np
import pytest
from fx_warehouse.reborn_long_cinema import (
    BANNED_TRANSITIONS,
    COLD_OPEN_SFX_LEAD_IN_RANGE,
    DIEGETIC_SFX_CATALOG,
    ENGINE_ID,
    ENGINE_VERSION,
    FPS,
    HEIGHT,
    J_CUT_PRELAP_SEC,
    MACRO_PARALLAX_MAX_HOLD_SEC,
    MIX_STEM_COUNT,
    POST_HOOK_SILENCE_DROP_RANGE,
    SPATIAL_TERRAIN_MAX_CONSECUTIVE_SEC,
    TARGET_LRA_RANGE,
    TARGET_SR,
    WATERMARK_POS,
    WIDTH,
    WPM_MODULATION_RANGE,
    BeatSpec,
    ChapterSpec,
    CinemaMixStem,
    ForensicRevealSpec,
    MacroParallaxSpec,
    MovingCinemaSpec,
    PilotSpec,
    SpatialTerrainSpec,
    TransitionRules,
    VisualMode,
    build_5stem_cinema_mix,
    build_forensic_reveal_layout,
    build_nvenc_render_cmd,
    compute_beat_timing,
    compute_parallax_camera_keyframes,
    compute_terrain_camera_keyframes,
    export_pilot_spec_json,
    parse_pilot_spec,
    resolve_transition,
    synthesize_diegetic_sfx,
    validate_visual_choreography,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _make_beat(
    beat_id: str = "beat_001",
    visual_mode: str = "moving_cinema",
    tts_text: str = "Đây là câu thuyết minh mẫu.",
    is_silence_drop: bool = False,
    sfx_solo_id: str | None = None,
    pre_silence_sec: float = 0.0,
    post_sfx_hold_sec: float = 0.0,
    **kwargs: object,
) -> BeatSpec:
    defaults: dict = {
        "beat_id": beat_id,
        "visual_mode": visual_mode,
        "tts_text": tts_text,
        "is_silence_drop": is_silence_drop,
        "sfx_solo_id": sfx_solo_id,
        "pre_silence_sec": pre_silence_sec,
        "post_sfx_hold_sec": post_sfx_hold_sec,
    }
    defaults.update(kwargs)
    return BeatSpec(**defaults)


def _make_moving_cinema_beat(beat_id: str = "beat_mc_001", **kwargs: object) -> BeatSpec:
    return _make_beat(
        beat_id=beat_id,
        visual_mode="moving_cinema",
        moving_cinema=MovingCinemaSpec(
            prompt="A vast battlefield at dawn, smoke rising, 16:9 cinematic",
            model="veo_3_1_lite",
        ),
        **kwargs,
    )


def _make_terrain_beat(beat_id: str = "beat_st_001") -> BeatSpec:
    return _make_beat(
        beat_id=beat_id,
        visual_mode="spatial_terrain_ops",
        spatial_terrain_ops=SpatialTerrainSpec(
            region_key="east_asia_vietnam",
            camera_start_zoom=1.0,
            camera_end_zoom=3.5,
            camera_fly_duration_sec=4.0,
            sovereignty_markers=True,
        ),
    )


def _make_forensic_beat(beat_id: str = "beat_fr_001") -> BeatSpec:
    return _make_beat(
        beat_id=beat_id,
        visual_mode="forensic_evidence_reveal",
        forensic_evidence_reveal=ForensicRevealSpec(
            layout="countdown_clock",
            timestamp_text="02:15 RẠNG SÁNG — CÒN 45 PHÚT",
        ),
    )


def _make_parallax_beat(beat_id: str = "beat_mp_001") -> BeatSpec:
    return _make_beat(
        beat_id=beat_id,
        visual_mode="macro_parallax_still",
        macro_parallax_still=MacroParallaxSpec(
            prompt="Ancient fortress walls at sunset, 16:9",
            max_hold_sec=3.0,
            camera_motion="parallax_push_in",
        ),
    )


def _make_silence_beat(beat_id: str = "beat_sil_001") -> BeatSpec:
    return _make_beat(
        beat_id=beat_id,
        visual_mode="moving_cinema",
        tts_text="",
        is_silence_drop=True,
        sfx_solo_id="cannon_thunder",
        pre_silence_sec=0.5,
        post_sfx_hold_sec=1.0,
        moving_cinema=MovingCinemaSpec(
            prompt="Cannon fire illuminating night sky, 16:9",
            model="veo_3_1_lite",
        ),
    )


def _make_pilot_spec(beats: list[BeatSpec] | None = None) -> PilotSpec:
    if beats is None:
        beats = [
            _make_moving_cinema_beat("beat_001"),
            _make_terrain_beat("beat_002"),
            _make_forensic_beat("beat_003"),
            _make_silence_beat("beat_004"),
            _make_parallax_beat("beat_005"),
            _make_moving_cinema_beat("beat_006"),
        ]
    return PilotSpec(
        chapters=[
            ChapterSpec(
                chapter_idx=1,
                chapter_header="CHƯƠNG I",
                chapter_title="TRẬN MỞ MÀN",
                beats=beats,
            ),
        ],
    )


# ===========================================================================
# TEST: Constants & Enums
# ===========================================================================
class TestConstants:
    def test_engine_id(self) -> None:
        assert ENGINE_ID == "reborn_long_cinema"

    def test_engine_version(self) -> None:
        assert ENGINE_VERSION == "1.0.0"

    def test_resolution(self) -> None:
        assert WIDTH == 1920
        assert HEIGHT == 1080
        assert FPS == 30

    def test_audio_specs(self) -> None:
        assert TARGET_SR == 48000
        assert J_CUT_PRELAP_SEC == -0.24

    def test_watermark_position(self) -> None:
        assert WATERMARK_POS == "W-w-36:H-h-36"

    def test_mix_stem_count(self) -> None:
        assert MIX_STEM_COUNT == 5

    def test_visual_modes(self) -> None:
        modes = {m.value for m in VisualMode}
        assert modes == {
            "moving_cinema",
            "spatial_terrain_ops",
            "forensic_evidence_reveal",
            "macro_parallax_still",
        }

    def test_banned_transitions(self) -> None:
        """Must include all harmful transitions from PLAYBOOK.md."""
        assert "dust_smoke_cloud" in BANNED_TRANSITIONS
        assert "river_mist_map_dive" in BANNED_TRANSITIONS
        assert "directional_flow_chain_transition" in BANNED_TRANSITIONS
        assert "smoothleft" in BANNED_TRANSITIONS

    def test_diegetic_sfx_catalog(self) -> None:
        assert len(DIEGETIC_SFX_CATALOG) >= 6
        for _sfx_id, spec in DIEGETIC_SFX_CATALOG.items():
            assert "duration_sec" in spec
            assert "stereo_width" in spec
            assert spec["duration_sec"] > 0.0

    def test_radar_benchmark_cold_open_sfx_range(self) -> None:
        """Foreign documentary benchmark: 2.5–4.0s SFX before Beat 0."""
        assert COLD_OPEN_SFX_LEAD_IN_RANGE == (2.5, 4.0)

    def test_radar_benchmark_lra_range(self) -> None:
        """LRA 5.5–10.5 LU breaks flat ~2 LU TTS monotony."""
        assert TARGET_LRA_RANGE == (5.5, 10.5)

    def test_radar_benchmark_wpm_modulation(self) -> None:
        """Non-uniform cadence swings: 75–165 WPM."""
        assert WPM_MODULATION_RANGE == (75, 165)

    def test_radar_benchmark_post_hook_silence(self) -> None:
        """1.5–3.0s silence after the central paradox question."""
        assert POST_HOOK_SILENCE_DROP_RANGE == (1.5, 3.0)


# ===========================================================================
# TEST: BeatSpec Validation
# ===========================================================================
class TestBeatSpecValidation:
    def test_valid_moving_cinema(self) -> None:
        beat = _make_moving_cinema_beat()
        assert beat.validate() == []

    def test_valid_terrain(self) -> None:
        beat = _make_terrain_beat()
        assert beat.validate() == []

    def test_valid_forensic(self) -> None:
        beat = _make_forensic_beat()
        assert beat.validate() == []

    def test_valid_parallax(self) -> None:
        beat = _make_parallax_beat()
        assert beat.validate() == []

    def test_valid_silence_drop(self) -> None:
        beat = _make_silence_beat()
        assert beat.validate() == []

    def test_empty_beat_id_fails(self) -> None:
        beat = _make_beat(beat_id="")
        errors = beat.validate()
        assert any("beat_id" in e for e in errors)

    def test_non_silence_empty_tts_fails(self) -> None:
        beat = _make_beat(tts_text="", is_silence_drop=False)
        errors = beat.validate()
        assert any("tts_text" in e for e in errors)

    def test_invalid_visual_mode_fails(self) -> None:
        beat = _make_beat(visual_mode="slideshow")
        errors = beat.validate()
        assert any("visual_mode" in e for e in errors)

    def test_pre_silence_exceeds_max_fails(self) -> None:
        beat = _make_beat(pre_silence_sec=5.0)
        errors = beat.validate()
        assert any("pre_silence_sec" in e for e in errors)

    def test_invalid_sfx_solo_id_fails(self) -> None:
        beat = _make_beat(
            is_silence_drop=True,
            tts_text="",
            sfx_solo_id="nonexistent_sfx",
        )
        errors = beat.validate()
        assert any("sfx_solo_id" in e for e in errors)

    def test_parallax_exceeds_max_hold_fails(self) -> None:
        beat = _make_beat(
            visual_mode="macro_parallax_still",
            macro_parallax_still=MacroParallaxSpec(
                prompt="Test scene",
                max_hold_sec=5.0,
            ),
        )
        errors = beat.validate()
        assert any("max_hold_sec" in e for e in errors)

    def test_moving_cinema_invalid_model_fails(self) -> None:
        beat = _make_beat(
            visual_mode="moving_cinema",
            moving_cinema=MovingCinemaSpec(
                prompt="Test scene",
                model="veo_3_1_fast",  # Retired model!
            ),
        )
        errors = beat.validate()
        assert any("model" in e for e in errors)

    def test_forensic_non_zero_rectangles_fails(self) -> None:
        beat = _make_beat(
            visual_mode="forensic_evidence_reveal",
            forensic_evidence_reveal=ForensicRevealSpec(
                layout="countdown_clock",
                zero_rectangles=False,
            ),
        )
        errors = beat.validate()
        assert any("zero_rectangles" in e for e in errors)


# ===========================================================================
# TEST: PilotSpec Validation
# ===========================================================================
class TestPilotSpecValidation:
    def test_valid_spec(self) -> None:
        spec = _make_pilot_spec()
        errors = spec.validate()
        assert errors == [], f"Unexpected errors: {errors}"

    def test_nam_minh_neural_blocked(self) -> None:
        """ERR-20261108-03: vi-VN-NamMinhNeural is permanently banned."""
        spec = _make_pilot_spec()
        spec.voice_id = "vi-VN-NamMinhNeural"
        errors = spec.validate()
        assert any("NamMinh" in e for e in errors)

    def test_wrong_engine_fails(self) -> None:
        spec = _make_pilot_spec()
        spec.engine = "old_slideshow"
        errors = spec.validate()
        assert any("engine" in e for e in errors)

    def test_positive_j_cut_fails(self) -> None:
        spec = _make_pilot_spec()
        spec.j_cut_prelap_sec = 0.5
        errors = spec.validate()
        assert any("j_cut" in e for e in errors)

    def test_wrong_stem_count_fails(self) -> None:
        spec = _make_pilot_spec()
        spec.mix_stems = ["narration", "bgm"]
        errors = spec.validate()
        assert any("stem" in e.lower() for e in errors)

    def test_wrong_watermark_position_fails(self) -> None:
        spec = _make_pilot_spec()
        spec.watermark_position = "top-left"
        errors = spec.validate()
        assert any("watermark" in e.lower() for e in errors)

    def test_banned_transition_fails(self) -> None:
        spec = _make_pilot_spec()
        spec.transitions.scene_boundary = "dust_smoke_cloud"
        errors = spec.validate()
        assert any("BANNED" in e for e in errors)

    def test_no_chapters_fails(self) -> None:
        spec = PilotSpec(chapters=[])
        errors = spec.validate()
        assert any("chapter" in e.lower() for e in errors)

    def test_cold_open_too_short_fails(self) -> None:
        """Radar: 0/10 breakout channels start TTS at 0.0s."""
        spec = _make_pilot_spec()
        spec.cold_open_sfx_lead_in_sec = 1.0
        errors = spec.validate()
        assert any("cold_open" in e for e in errors)

    def test_cold_open_valid(self) -> None:
        spec = _make_pilot_spec()
        spec.cold_open_sfx_lead_in_sec = 3.2
        errors = spec.validate()
        assert not any("cold_open" in e for e in errors)


# ===========================================================================
# TEST: Visual Choreography Validator
# ===========================================================================
class TestVisualChoreography:
    def test_mixed_modes_pass(self) -> None:
        spec = _make_pilot_spec()
        errors = validate_visual_choreography(spec)
        assert errors == []

    def test_single_mode_fails(self) -> None:
        """Must use at least 2 visual modes."""
        beats = [_make_moving_cinema_beat(f"b_{i}") for i in range(6)]
        spec = _make_pilot_spec(beats)
        errors = validate_visual_choreography(spec)
        assert any("at least 2" in e for e in errors)

    def test_four_consecutive_same_mode_warns(self) -> None:
        beats = [
            _make_moving_cinema_beat("b_1"),
            _make_moving_cinema_beat("b_2"),
            _make_moving_cinema_beat("b_3"),
            _make_moving_cinema_beat("b_4"),
            _make_terrain_beat("b_5"),
        ]
        spec = _make_pilot_spec(beats)
        errors = validate_visual_choreography(spec)
        assert any("4+ consecutive" in e for e in errors)

    def test_moving_cinema_cap_70pct(self) -> None:
        # 8 moving cinema + 2 terrain = 80% MC -> should warn
        beats = [_make_moving_cinema_beat(f"mc_{i}") for i in range(8)]
        beats.extend([_make_terrain_beat(f"st_{i}") for i in range(2)])
        spec = _make_pilot_spec(beats)
        errors = validate_visual_choreography(spec)
        assert any("70%" in e for e in errors)

    def test_spatial_terrain_max_consecutive_constant(self) -> None:
        """radar-user4: never pure map >14s."""
        assert SPATIAL_TERRAIN_MAX_CONSECUTIVE_SEC == 14.0


# ===========================================================================
# TEST: Beat Timing Computation
# ===========================================================================
class TestBeatTiming:
    def test_basic_timing(self) -> None:
        spec = _make_pilot_spec()
        durations = {
            "beat_001": 4.0,
            "beat_002": 5.0,
            "beat_003": 3.5,
            "beat_004": 0.0,  # silence drop
            "beat_005": 3.0,
            "beat_006": 4.5,
        }
        timeline = compute_beat_timing(spec, durations)
        assert len(timeline) == 6
        assert timeline[0]["out_start"] == 0.0
        # All out_starts should be monotonically increasing
        for i in range(1, len(timeline)):
            assert timeline[i]["out_start"] >= timeline[i - 1]["out_start"]

    def test_silence_drop_has_sfx_duration(self) -> None:
        spec = _make_pilot_spec()
        durations = {"beat_004": 0.0}
        for b in spec.all_beats():
            if b.beat_id not in durations:
                durations[b.beat_id] = 3.0
        timeline = compute_beat_timing(spec, durations)
        sil_beat = [t for t in timeline if t["beat_id"] == "beat_004"][0]
        assert sil_beat["is_silence_drop"] is True
        assert sil_beat["narration_duration_sec"] == 0.0
        assert sil_beat["duration_sec"] > 0.0

    def test_pre_silence_adds_to_duration(self) -> None:
        beat = _make_beat(
            beat_id="b1",
            pre_silence_sec=1.0,
            post_sfx_hold_sec=0.5,
        )
        spec = PilotSpec(
            chapters=[ChapterSpec(chapter_title="TEST", beats=[beat])],
        )
        durations = {"b1": 3.0}
        timeline = compute_beat_timing(spec, durations)
        assert len(timeline) == 1
        expected = 1.0 + 3.0 + 0.5  # pre + narration + post
        assert abs(timeline[0]["duration_sec"] - expected) < 0.01

    def test_j_cut_offset(self) -> None:
        beats = [_make_beat(beat_id=f"b{i}") for i in range(3)]
        spec = PilotSpec(
            chapters=[ChapterSpec(chapter_title="TEST", beats=beats)],
        )
        durations = {f"b{i}": 2.0 for i in range(3)}
        timeline = compute_beat_timing(spec, durations)
        # First beat has no j-cut
        assert timeline[0]["j_cut_offset"] == 0.0
        # Subsequent beats have j-cut
        assert timeline[1]["j_cut_offset"] == J_CUT_PRELAP_SEC


# ===========================================================================
# TEST: Transition Resolution
# ===========================================================================
class TestTransitions:
    def test_no_prev_beat(self) -> None:
        beat = _make_moving_cinema_beat()
        result = resolve_transition(None, beat, TransitionRules())
        assert result["type"] == "none"

    def test_intra_chain_moving_cinema(self) -> None:
        a = _make_moving_cinema_beat("a")
        b = _make_moving_cinema_beat("b")
        result = resolve_transition(a, b, TransitionRules())
        assert result["type"] == "continuous_cut"
        assert result["duration_sec"] == 0.0

    def test_map_entry_transition(self) -> None:
        a = _make_moving_cinema_beat("a")
        b = _make_terrain_beat("b")
        result = resolve_transition(a, b, TransitionRules())
        assert result["type"] == "map_camera_zoom_match"
        assert result["duration_sec"] == 0.55

    def test_cross_mode_scene_boundary(self) -> None:
        a = _make_moving_cinema_beat("a")
        b = _make_forensic_beat("b")
        result = resolve_transition(a, b, TransitionRules())
        assert result["type"] == "optical_anamorphic_dissolve"
        assert result["duration_sec"] == 0.45


# ===========================================================================
# TEST: Diegetic SFX Synthesizer
# ===========================================================================
class TestDiegeticSFX:
    @pytest.mark.parametrize("sfx_id", list(DIEGETIC_SFX_CATALOG.keys()))
    def test_synthesize_all_sfx(self, sfx_id: str) -> None:
        wav = synthesize_diegetic_sfx(sfx_id)
        assert wav.ndim == 2
        assert wav.shape[1] == 2  # stereo
        assert wav.dtype == np.float32
        assert len(wav) > 0
        # Check no NaN/Inf
        assert np.isfinite(wav).all()
        # Check peak normalized
        assert float(np.max(np.abs(wav))) <= 1.0

    def test_unknown_sfx_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown diegetic SFX"):
            synthesize_diegetic_sfx("nonexistent_sfx")

    def test_custom_duration(self) -> None:
        wav = synthesize_diegetic_sfx("cannon_thunder", duration_sec=1.0)
        expected_samples = int(1.0 * TARGET_SR)
        assert abs(len(wav) - expected_samples) < 10


# ===========================================================================
# TEST: 5-Stem Cinema Mix
# ===========================================================================
class TestCinemaMix:
    def test_valid_5stem_mix(self) -> None:
        n = TARGET_SR * 2  # 2 seconds
        stems = [
            CinemaMixStem("narration", np.random.randn(n, 2).astype(np.float32) * 0.3),
            CinemaMixStem("diegetic_sfx", np.zeros((n, 2), dtype=np.float32)),
            CinemaMixStem("silence_bed", np.zeros((n, 2), dtype=np.float32)),
            CinemaMixStem("bgm_tension", np.random.randn(n, 2).astype(np.float32) * 0.1, gain_db=-6.0),
            CinemaMixStem("room_tone", np.random.randn(n, 2).astype(np.float32) * 0.02),
        ]
        result = build_5stem_cinema_mix(stems, n)
        assert "master" in result
        assert result["master"].shape == (n, 2)
        assert result["master"].dtype == np.float32
        assert np.isfinite(result["master"]).all()
        assert len(result["stem_peaks"]) == 5

    def test_wrong_stem_count_raises(self) -> None:
        n = TARGET_SR
        stems = [
            CinemaMixStem("narration", np.zeros((n, 2), dtype=np.float32)),
            CinemaMixStem("bgm", np.zeros((n, 2), dtype=np.float32)),
        ]
        with pytest.raises(ValueError, match="Expected 5 stems"):
            build_5stem_cinema_mix(stems, n)


# ===========================================================================
# TEST: Camera Keyframes (Terrain & Parallax)
# ===========================================================================
class TestCameraKeyframes:
    def test_terrain_keyframes(self) -> None:
        terrain = SpatialTerrainSpec(
            camera_start_zoom=1.0,
            camera_end_zoom=4.0,
            camera_fly_duration_sec=3.0,
        )
        kf = compute_terrain_camera_keyframes(terrain)
        assert len(kf) == 3 * FPS  # 3 seconds * 30fps
        # First frame at start zoom, last at end zoom
        assert abs(kf[0]["zoom"] - 1.0) < 0.01
        assert abs(kf[-1]["zoom"] - 4.0) < 0.01
        # All zoom values are float (sub-pixel precision)
        for k in kf:
            assert isinstance(k["zoom"], float)

    def test_parallax_keyframes(self) -> None:
        parallax = MacroParallaxSpec(
            prompt="Test",
            max_hold_sec=2.0,
            camera_motion="parallax_push_in",
        )
        kf = compute_parallax_camera_keyframes(parallax)
        assert len(kf) == 2 * FPS  # 2 seconds
        # Zoom should increase (push in)
        assert kf[-1]["zoom"] >= kf[0]["zoom"]
        # Sub-pixel float precision
        for k in kf:
            assert isinstance(k["cx"], float)
            assert isinstance(k["cy"], float)

    def test_parallax_max_hold_clamped(self) -> None:
        """Max hold at 3.5s per ERR-20261109-01."""
        parallax = MacroParallaxSpec(prompt="Test", max_hold_sec=5.0)
        kf = compute_parallax_camera_keyframes(parallax)
        dur = len(kf) / FPS
        assert dur <= MACRO_PARALLAX_MAX_HOLD_SEC + 0.1


# ===========================================================================
# TEST: Forensic Reveal Layout
# ===========================================================================
class TestForensicRevealLayout:
    def test_countdown_clock(self) -> None:
        spec = ForensicRevealSpec(
            layout="countdown_clock",
            timestamp_text="02:15 RẠNG SÁNG",
        )
        layout = build_forensic_reveal_layout(spec)
        assert layout["type"] == "countdown_clock"
        assert layout["constraints"]["zero_rectangular_boxes"] is True
        assert "clock" in layout

    def test_force_comparison(self) -> None:
        spec = ForensicRevealSpec(layout="force_comparison")
        layout = build_forensic_reveal_layout(spec)
        assert layout["type"] == "force_comparison"
        assert "split" in layout

    def test_non_zero_rectangles_raises(self) -> None:
        spec = ForensicRevealSpec(zero_rectangles=False)
        with pytest.raises(ValueError, match="zero_rectangles"):
            build_forensic_reveal_layout(spec)


# ===========================================================================
# TEST: FFmpeg Render Command Builder
# ===========================================================================
class TestNvencRenderCmd:
    def test_basic_cmd(self) -> None:
        cmd = build_nvenc_render_cmd(
            "frames/%04d.png",
            "audio/master.wav",
            "out.mp4",
        )
        assert "ffmpeg" in cmd
        assert "h264_nvenc" in cmd
        assert "-preset" in cmd
        assert "p4" in cmd[cmd.index("-preset") + 1]
        assert "-b:v" in cmd
        assert "10M" in cmd[cmd.index("-b:v") + 1]

    def test_watermark_overlay(self) -> None:
        cmd = build_nvenc_render_cmd(
            "frames/%04d.png",
            "audio/master.wav",
            "out.mp4",
            watermark_path="logo.png",
        )
        assert "logo.png" in cmd
        assert "W-w-36:H-h-36" in " ".join(cmd)

    def test_delogo_in_cmd(self) -> None:
        cmd = build_nvenc_render_cmd(
            "frames/%04d.png",
            "audio/master.wav",
            "out.mp4",
            delogo=True,
        )
        assert "delogo" in " ".join(cmd)

    def test_48khz_audio(self) -> None:
        cmd = build_nvenc_render_cmd("f.png", "a.wav", "o.mp4")
        ar_idx = cmd.index("-ar")
        assert cmd[ar_idx + 1] == str(TARGET_SR)


# ===========================================================================
# TEST: Spec Serialization Round-Trip
# ===========================================================================
class TestSpecSerialization:
    def test_export_roundtrip(self) -> None:
        spec = _make_pilot_spec()
        exported = export_pilot_spec_json(spec)
        # Verify it's JSON-serializable
        json_str = json.dumps(exported, ensure_ascii=False)
        # Parse it back
        parsed = parse_pilot_spec(json.loads(json_str))
        assert parsed.engine == ENGINE_ID
        assert parsed.channel_id == "su_ke_lai"
        assert parsed.beat_count() == spec.beat_count()
        assert parsed.voice_id == spec.voice_id

    def test_export_contains_banned_transitions(self) -> None:
        spec = _make_pilot_spec()
        exported = export_pilot_spec_json(spec)
        assert "banned" in exported["transitions"]
        assert "dust_smoke_cloud" in exported["transitions"]["banned"]

    def test_export_all_visual_modes_present(self) -> None:
        spec = _make_pilot_spec()
        exported = export_pilot_spec_json(spec)
        all_modes = set()
        for ch in exported["chapters"]:
            for b in ch["beats"]:
                all_modes.add(b["visual_mode"])
        assert len(all_modes) >= 3  # moving_cinema, spatial, forensic, parallax


# ===========================================================================
# TEST: Integration — Full Pipeline Validation
# ===========================================================================
class TestFullPipelineValidation:
    def test_pilot_spec_validates_fully(self) -> None:
        """The standard pilot spec must pass all validation gates."""
        spec = _make_pilot_spec()
        errors = spec.validate()
        assert errors == [], f"Validation errors: {errors}"
        choreo_errors = validate_visual_choreography(spec)
        assert choreo_errors == [], f"Choreography errors: {choreo_errors}"

    def test_timing_total_non_zero(self) -> None:
        spec = _make_pilot_spec()
        durations = {b.beat_id: 3.0 for b in spec.all_beats()}
        durations["beat_004"] = 0.0  # silence drop
        timeline = compute_beat_timing(spec, durations)
        total_dur = timeline[-1]["out_end"]
        assert total_dur > 0.0

    def test_all_diegetic_sfx_synthesize(self) -> None:
        """Every SFX in the catalog must synthesize without error."""
        for sfx_id in DIEGETIC_SFX_CATALOG:
            wav = synthesize_diegetic_sfx(sfx_id)
            assert wav.shape[1] == 2
            assert np.isfinite(wav).all()
