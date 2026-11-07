"""Tests for Vietnamese High-Density Long (16:9) Blueprint Planner & Two-Tier Visual-State DAG Engine."""

from __future__ import annotations

import pytest
from channels.vn_long_high_density_planner import (
    VN_LONG_DENSITY_PROFILES,
    VisualEventKind,
    get_vn_long_density_profile,
    list_all_vn_long_density_profiles,
    normalize_channel_id,
    plan_long_visual_states_from_chapters,
    to_renderer_scenes,
    validate_high_density_long_plan,
)
from visual_pacing import check_see_say_beat_density, check_tempo_beats


class TestVNChannelDensityProfiles:
    """Validate SSOT registry coverage and profile contracts for all 20 Vietnamese channels."""

    def test_all_20_vn_channel_density_profiles_registered(self):
        profiles = list_all_vn_long_density_profiles()
        assert len(profiles) == 20, f"Expected exactly 20 VN channel profiles, got {len(profiles)}"

        # Verify archetype classification breakdown: 11 investigative, 6 scale/map, 3 contemplative
        investigative = [cid for cid, p in profiles.items() if p.archetype == "high_velocity_investigative"]
        scale_map = [cid for cid, p in profiles.items() if p.archetype == "scale_map_academic"]
        contemplative = [cid for cid, p in profiles.items() if p.archetype == "contemplative_sanctuary"]

        assert len(investigative) == 11
        assert len(scale_map) == 6
        assert len(contemplative) == 3

        # Target states ranges
        for cid in investigative:
            p = profiles[cid]
            assert p.target_states_range == (260, 350)
            assert p.target_avg_hold_range == (1.6, 2.3)
            assert p.tier1_anchors_range == (100, 125)
            assert p.tier2_builds_range == (160, 225)

        for cid in scale_map:
            p = profiles[cid]
            assert p.target_states_range == (220, 290)
            assert p.target_avg_hold_range == (2.1, 2.8)
            assert p.tier1_anchors_range == (90, 110)
            assert p.tier2_builds_range == (130, 180)

        for cid in contemplative:
            p = profiles[cid]
            assert p.target_states_range == (150, 210)
            assert p.target_avg_hold_range == (3.2, 4.5)
            assert p.tier1_anchors_range == (60, 80)
            assert p.tier2_builds_range == (90, 130)

    def test_channel_id_normalization_and_aliases(self):
        assert normalize_channel_id("tui-tien") == "tui_tien"
        assert normalize_channel_id("  HO-SO-KY-LA ") == "ho_so_ky_la"
        assert normalize_channel_id("Ban_Do_Quyen_Luc") == "ban_do_quyen_luc"

        # Lookup with hyphenated or mixed case string
        prof = get_vn_long_density_profile("tui-tien")
        assert prof.channel_id == "tui_tien"

        with pytest.raises(KeyError):
            get_vn_long_density_profile("non_existent_channel_xyz")


class TestPlanGenerationAndValidation:
    """Test generating full 10m30s (630s) plans and DAG compliance across all 20 channels."""

    def test_plan_and_validate_10m30s_high_velocity_tui_tien(self):
        plan = plan_long_visual_states_from_chapters("tui_tien", total_duration_sec=630.0)

        # Structure checks
        assert plan.channel_id == "tui_tien"
        assert plan.format_profile == "long_16x9_high_density"
        assert abs(plan.total_duration_sec - 630.0) < 0.1
        assert 8 <= len(plan.chapters) <= 12

        # 300 visual states target (~110 base anchors + ~190 progressive builds)
        states = plan.visual_states
        assert 260 <= len(states) <= 350
        tier1 = plan.metadata["tier1_anchors"]
        tier2 = plan.metadata["tier2_builds"]
        assert 100 <= tier1 <= 125
        assert 160 <= tier2 <= 225
        assert tier1 + tier2 == len(states)

        # Chapter durations >= 10s and contiguous
        prev_end = 0.0
        for ch in plan.chapters:
            assert ch.duration_sec >= 10.0
            assert abs(ch.start_sec - prev_end) < 0.01
            prev_end = ch.end_sec
        assert abs(prev_end - 630.0) < 0.1

        # Validation must pass cleanly with 0 errors
        errors = validate_high_density_long_plan(plan)
        assert errors == [], f"Validation failed for tui_tien: {errors}"

    @pytest.mark.parametrize("channel_id", list(VN_LONG_DENSITY_PROFILES.keys()))
    def test_plan_and_validate_all_20_vn_channels(self, channel_id: str):
        profile = VN_LONG_DENSITY_PROFILES[channel_id]
        plan = plan_long_visual_states_from_chapters(channel_id, total_duration_sec=630.0)

        # Validate DAG and pacing contracts
        errors = validate_high_density_long_plan(plan)
        assert errors == [], f"Validation failed for '{channel_id}': {errors}"

        # Target range compliance
        total_states = len(plan.visual_states)
        assert profile.target_states_range[0] <= total_states <= profile.target_states_range[1]
        assert profile.tier1_anchors_range[0] <= plan.metadata["tier1_anchors"] <= profile.tier1_anchors_range[1]
        assert profile.tier2_builds_range[0] <= plan.metadata["tier2_builds"] <= profile.tier2_builds_range[1]

        # Average hold within target
        avg_hold = plan.metadata["avg_hold"]
        assert profile.target_avg_hold_range[0] <= avg_hold <= profile.target_avg_hold_range[1]

        # Spatial cognitive holds <= 8%
        assert plan.metadata["spatial_hold_ratio"] <= 0.08


class TestDAGContractViolations:
    """Verify that validate_high_density_long_plan rejects invalid DAGs, camera entropy, and xfade conflicts."""

    def test_tier2_missing_dag_parent_rejected(self):
        plan = plan_long_visual_states_from_chapters("tui_tien", total_duration_sec=630.0)
        # Corrupt a Tier-2 state by removing based_on
        plan.visual_states[1].based_on = None
        errors = validate_high_density_long_plan(plan)
        assert any("MISSING_DAG_PARENT" in err for err in errors)

    def test_dag_parent_not_found_rejected(self):
        plan = plan_long_visual_states_from_chapters("tui_tien", total_duration_sec=630.0)
        # Point to a future or nonexistent state
        plan.visual_states[2].based_on = "NON_EXISTENT_PARENT_ID"
        errors = validate_high_density_long_plan(plan)
        assert any("DAG_PARENT_NOT_FOUND" in err for err in errors)

    def test_anchor_with_parent_rejected(self):
        plan = plan_long_visual_states_from_chapters("tui_tien", total_duration_sec=630.0)
        # An anchor must establish a new diorama and have based_on=None
        plan.visual_states[0].based_on = "INVALID_PARENT"
        errors = validate_high_density_long_plan(plan)
        assert any("INVALID_DAG_ANCHOR" in err for err in errors)

    def test_camera_entropy_exceeded_rejected(self):
        plan = plan_long_visual_states_from_chapters("tui_tien", total_duration_sec=630.0)
        # Force 3 consecutive identical camera moves
        plan.visual_states[3].camera_move = "pan_right"
        plan.visual_states[4].camera_move = "pan_right"
        plan.visual_states[5].camera_move = "pan_right"
        errors = validate_high_density_long_plan(plan)
        assert any("CAMERA_ENTROPY_VIOLATION" in err for err in errors)

    def test_directional_xfade_conflict_rejected(self):
        plan = plan_long_visual_states_from_chapters("tui_tien", total_duration_sec=630.0)
        # Pair pan_right with smoothleft (directional conflict)
        plan.visual_states[3].camera_move = "pan_right"
        plan.visual_states[3].xfade = "smoothleft"
        errors = validate_high_density_long_plan(plan)
        assert any("DIRECTIONAL_XFADE_CONFLICT" in err for err in errors)

    def test_spatial_hold_ratio_exceeded_rejected(self):
        plan = plan_long_visual_states_from_chapters("tui_tien", total_duration_sec=630.0)
        # Corrupt many states to be spatial holds (> 8%)
        for s in plan.visual_states[:40]:
            s.event_kind = VisualEventKind.SPATIAL_COGNITIVE_HOLD
        errors = validate_high_density_long_plan(plan)
        assert any("SPATIAL_HOLD_RATIO_EXCEEDED" in err for err in errors)


class TestVisualPacingEngineIntegration:
    """Verify direct integration with sys/visual_pacing.py functions."""

    def test_to_renderer_scenes_passes_see_say_density_and_tempo(self):
        plan = plan_long_visual_states_from_chapters("tui_tien", total_duration_sec=630.0)
        scenes = to_renderer_scenes(plan)

        # Validate directly using visual_pacing engine
        density_errors = check_see_say_beat_density(scenes, format_profile="long_16x9_high_density")
        assert density_errors == [], f"Direct density check failed: {density_errors}"

        beats = [
            {"id": s.id, "tempo": s.tempo, "hold": s.hold, "at": s.at, "emphasis_text": s.emphasis_text}
            for s in plan.visual_states
        ]
        tempo_errors = check_tempo_beats(beats, format_profile="long_16x9_high_density")
        assert tempo_errors == [], f"Direct tempo check failed: {tempo_errors}"

    def test_high_density_opening_windows_support_rapid_cuts(self):
        """High-density long format allows up to 7 starts in [0, 5) and up to 14 in [0, 12.5)."""
        # Create a rapid 6-cut opening in first 5s (total 200 beats across 600s)
        sc1_images = [{"id": f"I{i}", "at": round(i * 0.8, 2)} for i in range(6)]  # 6 starts < 5s
        sc1_images.extend([{"id": f"I{i}", "at": round(5.0 + (i - 6) * 1.0, 2)} for i in range(6, 12)])  # 12 starts < 12.5s
        sc1_images.extend([{"id": f"I{i}", "at": round(12.0 + (i - 12) * 2.0, 2)} for i in range(12, 36)])

        scenes = [
            {"id": "SC01", "start": 0.0, "end": 60.0, "images": sc1_images},
            {"id": "SC02", "start": 60.0, "end": 600.0, "images": [{"id": f"S2_I{i}", "at": round(i * 3.0, 2)} for i in range(180)]},
        ]
        # Under high density, 6 starts in [0, 5) is accepted (allowed 2-7)
        errors = check_see_say_beat_density(scenes, format_profile="long_16x9_high_density")
        assert errors == [], f"Expected clean pass under high density, got: {errors}"
