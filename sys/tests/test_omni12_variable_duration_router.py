"""Tests for Omni 1.2 Flash (`macaron_cookie`) 4s/6s/8s/10s Variable Gearbox & Active Choreography."""
from __future__ import annotations

from pathlib import Path

import pytest
from flow_video.models import ChainMode, ScenePairSpec, VideoChainSpec
from flow_video.motion_library import (
    _timecodes_for_clip,
    build_timecoded_video_prompt,
    is_omni12_model,
)
from flow_video.scene_map_planner import (
    SceneMap,
    SceneMapEntry,
    apply_auto_routing,
    compile_scene_image_prompts,
    compile_scene_video_prompts,
    plan_omni12_variable_gearbox,
    validate_scene_map,
)

_WAX_STATUE_PHRASES = (
    "remains still",
    "almost still",
    "hands resting naturally",
    "only the camera travels",
    "only the camera moves",
)


def test_is_omni12_model_classifier() -> None:
    for omni_alias in (
        "omni_flash",
        "OMNI_1_2_FLASH",
        "omni",
        "macaron_cookie",
        "macaron_cookie_i2v_4s",
        "macaron_cookie_i2v_fl_10s",
    ):
        assert is_omni12_model(omni_alias) is True

    for non_omni in ("veo_3_1_lite", "veo_3_1_i2v_s_lite_portrait", "veo_3_1_fast", ""):
        assert is_omni12_model(non_omni) is False


def test_omni12_timecodes_for_all_four_durations_and_veo_lite_compat() -> None:
    assert _timecodes_for_clip(4, False, model="omni_flash") == ("0-2.6s", "2.6-4.0s")
    assert _timecodes_for_clip(6, False, model="omni_flash") == ("0-4.0s", "4.0-6.0s")
    assert _timecodes_for_clip(8, False, model="omni_flash") == ("0-5.4s", "5.4-8.0s")
    assert _timecodes_for_clip(10, False, model="omni_flash") == ("0-3.4s", "3.4-7.0s", "7.0-10.0s")

    # Default model in _timecodes_for_clip also supports 4/6/8/10s cleanly
    assert _timecodes_for_clip(4) == ("0-2.6s", "2.6-4.0s")
    assert _timecodes_for_clip(6) == ("0-4.0s", "4.0-6.0s")
    assert _timecodes_for_clip(8) == ("0-5.4s", "5.4-8.0s")
    assert _timecodes_for_clip(10) == ("0-3.4s", "3.4-7.0s", "7.0-10.0s")

    # Veo 3.1 Lite legacy & V7 timecodes stay untouched
    assert _timecodes_for_clip(8, False, model="veo_3_1_lite") == ("0-6.5s", "6.5-8s")
    assert _timecodes_for_clip(8, False, viral_v7=True, model="veo_3_1_lite") == ("0-5.2s", "5.2-6.5s")


@pytest.mark.parametrize(
    ("dur", "expected_brackets", "expected_cue"),
    [
        (4, ("[0-2.6s]", "[2.6-4.0s]"), "Measured tactile micro-motion and crisp optical focus"),
        (6, ("[0-4.0s]", "[4.0-6.0s]"), "Medium OTS and grounded physical blocking"),
        (8, ("[0-5.4s]", "[5.4-8.0s]"), "Two-stage spatial choreography"),
        (
            10,
            ("[0-3.4s]", "[3.4-7.0s]", "[7.0-10.0s]"),
            "One unbroken 10-second continuous long take",
        ),
    ],
)
def test_build_timecoded_video_prompt_omni12_eliminates_wax_statue_across_modes(
    dur: int,
    expected_brackets: tuple[str, ...],
    expected_cue: str,
) -> None:
    for model_name in ("omni_flash", "macaron_cookie_i2v_fl_8s"):
        for transition_mode in ("seam", "frame_link", "soft_fade"):
            prompt = build_timecoded_video_prompt(
                camera_move="tracking_alongside",
                hero_subject="blacksmith hammering red-hot iron spearhead",
                setting="rain-slicked Lam Son forge",
                model=model_name,
                clip_duration_sec=dur,
                transition_mode=transition_mode,
                exit_seam="edge_pass",
                seam_prop="charred timber post",
                has_person=True,
                next_subject="quenched steel blade steaming in barrel",
                next_location="rain-slicked Lam Son forge",
                lens_spec="35mm anamorphic film lens",
            )
            for bracket in expected_brackets:
                assert bracket in prompt, f"Missing {bracket} in {dur}s {transition_mode} prompt: {prompt}"
            assert expected_cue in prompt

            low = prompt.lower()
            for banned in _WAX_STATUE_PHRASES:
                assert banned not in low, f"Found wax-statue phrase {banned!r} in Omni 1.2 prompt: {prompt}"

            assert "closed mouths" in low
            assert "zero lip-flap" in low
            assert "no talking" in low
            assert "no lip movement" in low
            assert "one continuous unbroken camera take with zero internal cuts" in low
            assert "zero mid-clip prop morphing" in low
            assert "tactile prop impact" not in low
            assert "forge, write, or grip weapons" not in low

    # 10s must specifically carry 3-phase opening -> continuous Steadicam/crane/Frame-Link -> dramatic arrival
    p10_fl = build_timecoded_video_prompt(
        camera_move="push_in",
        hero_subject="Tay Son vanguard marching through ankle-deep mud",
        setting="Tam Diep mountain pass",
        model="macaron_cookie_i2v_fl_10s",
        clip_duration_sec=10,
        transition_mode="frame_link",
        has_person=True,
        next_subject="forward torchlit timber barricade",
        next_location="Ngoc Hoi approach",
    )
    assert "[0-3.4s] Opening physical action and foreground pass" in p10_fl
    assert "[3.4-7.0s] Continuous Steadicam and Frame-Link evolution" in p10_fl
    assert "[7.0-10.0s] Dramatic arrival and shallow-DoF optical settle" in p10_fl


def test_models_and_scene_map_optional_fields_backward_compatible_serialization(tmp_path: Path) -> None:
    # Defaults remain None without breaking legacy callers
    sp_default = ScenePairSpec(id="B00", start_image_path="/tmp/a.png")
    assert sp_default.clip_duration_sec is None
    assert sp_default.oner_group_id is None
    assert ScenePairSpec.from_dict({"id": "B00"}).clip_duration_sec is None
    assert ScenePairSpec.from_dict({"id": "B00"}).oner_group_id is None

    sp_v12 = ScenePairSpec(
        id="B04",
        start_image_path="/tmp/b04.png",
        end_image_path="/tmp/b05.png",
        video_model="omni_flash",
        transition_mode="frame_link",
        target_duration=9.4,
        clip_duration_sec=10,
        oner_group_id="oner_tam_diep_01",
    )
    chain = VideoChainSpec(job_id="v12_roundtrip", mode=ChainMode.SCENE_PAIRS, scene_pairs=[sp_default, sp_v12])
    chain_json = tmp_path / "chain.json"
    chain.to_json_file(chain_json)
    reloaded_chain = VideoChainSpec.from_json_file(chain_json)
    assert reloaded_chain.scene_pairs[0].clip_duration_sec is None
    assert reloaded_chain.scene_pairs[0].oner_group_id is None
    assert reloaded_chain.scene_pairs[1].clip_duration_sec == 10
    assert reloaded_chain.scene_pairs[1].oner_group_id == "oner_tam_diep_01"

    entry_legacy = SceneMapEntry.from_dict({
        "scene_id": "SC01",
        "time_range": "0-4s",
        "vo_snippet": "Mở màn.",
        "location": "Chi Lang gorge",
        "hero_subject": "limestone cliff",
    })
    assert entry_legacy.clip_duration_sec is None
    assert entry_legacy.oner_group_id is None

    entry_v12 = SceneMapEntry(
        scene_id="SC02",
        time_range="4-13.5s",
        vo_snippet="Đội kỵ binh lao qua khe núi.",
        location="Chi Lang gorge",
        hero_subject="cavalry ambush trap",
        clip_duration_sec=10,
        oner_group_id="oner_chi_lang_ambush",
    )
    smap = SceneMap(job_id="v12_smap", channel_id="su_ke_lai", scenes=[entry_legacy, entry_v12])
    smap_json = tmp_path / "scene_map.json"
    smap.to_json_file(smap_json)
    reloaded_smap = SceneMap.from_json_file(smap_json)
    assert reloaded_smap.scenes[0].clip_duration_sec is None
    assert reloaded_smap.scenes[0].oner_group_id is None
    assert reloaded_smap.scenes[1].clip_duration_sec == 10
    assert reloaded_smap.scenes[1].oner_group_id == "oner_chi_lang_ambush"


def test_plan_omni12_variable_gearbox_all_durations_rpc_keys_and_credits() -> None:
    # 4s (<= 4.2s)
    g4_sf = plan_omni12_variable_gearbox(3.8, shot_class="MACRO_PROP", has_end_frame=False)
    assert g4_sf["video_model"] == "omni_flash"
    assert g4_sf["resolved_rpc_key"] == "macaron_cookie_i2v_4s"
    assert g4_sf["clip_duration_sec"] == 4
    assert g4_sf["credit_cost"] == 12
    assert g4_sf["timecode_phases"] == ("0-2.6s", "2.6-4.0s")

    g4_fl = plan_omni12_variable_gearbox(4.2, shot_class="REACTION_MICRO", has_end_frame=True)
    assert g4_fl["resolved_rpc_key"] == "macaron_cookie_i2v_fl_4s"
    assert g4_fl["clip_duration_sec"] == 4
    assert g4_fl["credit_cost"] == 12

    # 6s (<= 6.2s)
    g6_sf = plan_omni12_variable_gearbox(5.4, shot_class="OTS_DIRTY", has_end_frame=False)
    assert g6_sf["resolved_rpc_key"] == "macaron_cookie_i2v_6s"
    assert g6_sf["clip_duration_sec"] == 6
    assert g6_sf["credit_cost"] == 18
    assert g6_sf["timecode_phases"] == ("0-4.0s", "4.0-6.0s")

    g6_fl = plan_omni12_variable_gearbox(6.2, has_end_frame=True)
    assert g6_fl["resolved_rpc_key"] == "macaron_cookie_i2v_fl_6s"
    assert g6_fl["clip_duration_sec"] == 6
    assert g6_fl["credit_cost"] == 18

    # 8s (<= 8.2s)
    g8_sf = plan_omni12_variable_gearbox(7.5, shot_class="GROUND_MUD", has_end_frame=False)
    assert g8_sf["resolved_rpc_key"] == "macaron_cookie_i2v_8s"
    assert g8_sf["clip_duration_sec"] == 8
    assert g8_sf["credit_cost"] == 24
    assert g8_sf["timecode_phases"] == ("0-5.4s", "5.4-8.0s")

    g8_fl = plan_omni12_variable_gearbox(8.2, has_end_frame=True)
    assert g8_fl["resolved_rpc_key"] == "macaron_cookie_i2v_fl_8s"
    assert g8_fl["clip_duration_sec"] == 8
    assert g8_fl["credit_cost"] == 24

    # 10s (> 8.2s OR is_multi_beat_oner=True)
    g10_sf = plan_omni12_variable_gearbox(9.1, shot_class="GODS_EYE", has_end_frame=False)
    assert g10_sf["resolved_rpc_key"] == "macaron_cookie_i2v_10s"
    assert g10_sf["clip_duration_sec"] == 10
    assert g10_sf["credit_cost"] == 30
    assert g10_sf["timecode_phases"] == ("0-3.4s", "3.4-7.0s", "7.0-10.0s")

    g10_oner = plan_omni12_variable_gearbox(
        4.6,
        shot_class="ENV_SENSORY",
        has_end_frame=True,
        is_multi_beat_oner=True,
    )
    assert g10_oner["video_model"] == "omni_flash"
    assert g10_oner["resolved_rpc_key"] == "macaron_cookie_i2v_fl_10s"
    assert g10_oner["clip_duration_sec"] == 10
    assert g10_oner["credit_cost"] == 30
    assert g10_oner["timecode_phases"] == ("0-3.4s", "3.4-7.0s", "7.0-10.0s")

    # Optional prefer_omni12=False uses veo_3_1_lite for <=8.2s start-frame only
    g_lite = plan_omni12_variable_gearbox(5.0, has_end_frame=False, prefer_omni12=False)
    assert g_lite["video_model"] == "veo_3_1_lite"
    assert g_lite["clip_duration_sec"] == 6
    assert g_lite["credit_cost"] == 10


def test_apply_auto_routing_omni12_variable_mode_and_legacy_compat() -> None:
    scenes = [
        SceneMapEntry(
            scene_id="SC01",
            time_range="0-3.6s",
            vo_snippet="Chén trà đồng bốc khói lạnh.",
            location="Le Chi Vien pavilion",
            hero_subject="bronze teacup on lacquer tray",
            cast_spec="none",
            camera_move="push_in",
            exit_seam="dark_opening",
            lighting_key="candlelit",
        ),
        SceneMapEntry(
            scene_id="SC02",
            time_range="3.6-9.0s",
            vo_snippet="Ngón tay chấm chu sa đỏ thẫm.",
            location="Le Chi Vien desk",
            hero_subject="wet cinnabar brush over silk scroll",
            cast_spec="NEW: court scribe hands in dark silk sleeves",
            camera_move="truck_lateral",
            exit_seam="edge_pass",
            lighting_key="candlelit",
            person_count=1,
        ),
        SceneMapEntry(
            scene_id="SC03",
            time_range="9.0-16.4s",
            vo_snippet="Ánh đuốc hắt qua hành lang gỗ.",
            location="Le Chi Vien corridor",
            hero_subject="imperial wooden seal box",
            cast_spec="SAME as SC02: court scribe hands in dark silk sleeves",
            reference_scene_ids=["SC02"],
            camera_move="orbit",
            exit_seam="dust_smoke_cloud",
            lighting_key="candlelit",
            person_count=1,
            same_world_continuous=True,
        ),
        SceneMapEntry(
            scene_id="SC04",
            time_range="16.4-21.0s",
            vo_snippet="Bước chân dồn dập ngoài sân gạch.",
            location="Rainy courtyard",
            hero_subject="iron lantern swinging in monsoon rain",
            cast_spec="none",
            camera_move="tracking_alongside",
            exit_seam="edge_pass",
            lighting_key="rain_night",
            oner_group_id="oner_courtyard_01",
        ),
        SceneMapEntry(
            scene_id="SC05",
            time_range="21.0-25.8s",
            vo_snippet="Cánh cổng gỗ khép sập trong đêm mưa.",
            location="Rainy courtyard gate",
            hero_subject="heavy iron-studded gate",
            cast_spec="none",
            camera_move="pull_back",
            exit_seam="final_hold",
            seam_color="none",
            lighting_key="rain_night",
            oner_group_id="oner_courtyard_01",
        ),
    ]
    smap = SceneMap(job_id="v12_autopsy", channel_id="su_ke_lai", format_profile="short_9x16", scenes=scenes)
    apply_auto_routing(smap, prefer_credit_saving=True, omni12_variable_mode=True)

    assert [sc.video_model for sc in smap.scenes] == ["omni_flash"] * 5
    # Durations: 3.6s -> 4s, 5.4s -> 6s, 7.4s -> 8s, shared oner_group_id -> 10s & 10s
    assert [sc.clip_duration_sec for sc in smap.scenes] == [4, 6, 8, 10, 10]
    # SC01->SC02 changes cast (none -> NEW) -> seam; SC04->SC05 shares oner_group_id + compatible cast + lighting -> frame_link
    assert smap.scenes[0].transition_mode == "seam"
    assert smap.scenes[3].transition_mode == "frame_link"
    assert smap.scenes[4].exit_seam == "final_hold"

    val = validate_scene_map(smap)
    assert val["valid"] is True, val["errors"]
    assert val["credit_summary"]["omni_clips"] == 5
    assert val["credit_summary"]["total_credits"] == (12 + 18 + 24 + 30 + 30)

    img_prompts = compile_scene_image_prompts(smap)
    assert "only the camera moves" not in img_prompts[1]["image_prompt"].lower()

    vid_prompts = compile_scene_video_prompts(smap)
    assert vid_prompts[0]["clip_duration_sec"] == 4 and "[0-2.6s]" in vid_prompts[0]["video_prompt"]
    assert vid_prompts[1]["clip_duration_sec"] == 6 and "[0-4.0s]" in vid_prompts[1]["video_prompt"]
    assert vid_prompts[2]["clip_duration_sec"] == 8 and "[0-5.4s]" in vid_prompts[2]["video_prompt"]
    assert vid_prompts[3]["clip_duration_sec"] == 10 and "[0-3.4s]" in vid_prompts[3]["video_prompt"]
    assert "[3.4-7.0s]" in vid_prompts[3]["video_prompt"] and "[7.0-10.0s]" in vid_prompts[3]["video_prompt"]
    for item in vid_prompts:
        low_vp = item["video_prompt"].lower()
        for banned in _WAX_STATUE_PHRASES:
            assert banned not in low_vp
