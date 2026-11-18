"""Tests for Motion Library, 2-Stage Scene Map, Dual-Model Router, Seam Stitcher & 4 Fleet Drift Fixes."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from channels.registry import CHANNEL_ALIASES, channel_ids
from channels.vn_competitor_script_formulas import VN_COMPETITOR_SCRIPT_FORMULAS
from channels.vn_flow_video_formulas import VN_CHANNEL_LOGO_PROMPTS, VN_FLOW_VIDEO_FORMULAS
from flow_cdp import flow_rpc
from flow_video.chain_planner import build_dual_model_chain_spec, build_scene_pair_tasks, select_clip_duration_and_credits
from flow_video.motion_library import apply_positive_framing, build_timecoded_video_prompt, get_channel_motion_policy
from flow_video.scene_map_planner import (
    SceneMap,
    SceneMapEntry,
    apply_auto_routing,
    compile_scene_image_prompts,
    compile_scene_video_prompts,
    validate_scene_map,
)
from flow_video.stitcher import stitch_video_chain
from fx_warehouse.archetypes import (
    ARCHETYPE_PROFILES,
    CHANNEL_BESPOKE_RULES,
    EN_CHANNEL_ARCHETYPE_MAP,
    get_channel_archetype,
    resolve_niche_fx_blueprint,
)
from tools.produce_vn_dual_mode import V3_2K_CHANNEL_LOCKS, build_short_video_chain_spec
from tools.story_driven_prompt_builder import build_positive_scene_prompt


def test_motion_library_timecodes_positive_framing_and_comfort_policies() -> None:
    cleaned = apply_positive_framing("clean bench, no text, no cars, no talking")
    assert "plain unmarked surfaces" in cleaned
    assert "empty open ground" in cleaned

    veo_prompt = build_timecoded_video_prompt(
        camera_move="push_in",
        hero_subject="steel reactor valve",
        setting="dim turbine hall",
        model="veo_3_1_lite",
        clip_duration_sec=8,
        transition_mode="seam",
        exit_seam="dark_opening",
        seam_prop="steel bulkhead hatch",
        has_person=True,
    )
    assert "[0-6.5s]" in veo_prompt
    assert "[6.5-8s]" in veo_prompt
    assert "closed mouth" in veo_prompt
    assert "zero flags" in veo_prompt

    mindful_policy = get_channel_motion_policy("minh_triet_song")
    assert mindful_policy["allow_exit_seams"] is False
    assert mindful_policy["default_transition_mode"] == "soft_fade"
    assert mindful_policy["default_dissolve_sec"] == 0.24

    doodle_policy = get_channel_motion_policy("nao_luoi")
    assert doodle_policy["allow_exit_seams"] is False

    forensic_policy = get_channel_motion_policy("ho_so_ky_la")
    assert forensic_policy["allow_exit_seams"] is True
    assert forensic_policy["default_dissolve_sec"] == 0.18


def test_two_stage_scene_map_anti_morph_routing_and_credit_savings(tmp_path: Path) -> None:
    entries = [
        SceneMapEntry(
            scene_id="SC01", time_range="0-8s", vo_snippet="Bãi ga Stanley trống vắng.",
            location="Stanley rail yard", hero_subject="locomotive 8888",
            cast_spec="NEW: lone engineer in dark vest", camera_move="push_in",
            exit_seam="dark_opening", lighting_key="dusk", person_count=1,
        ),
        SceneMapEntry(
            scene_id="SC02", time_range="8-16s", vo_snippet="Anh ta bước xuống đường ray.",
            location="Stanley rail track", hero_subject="track switch lever",
            cast_spec="SAME as SC01: lone engineer in dark vest", reference_scene_ids=["SC01"],
            camera_move="truck_lateral", exit_seam="edge_pass", lighting_key="dusk",
            person_count=1, same_world_continuous=True,
        ),
        SceneMapEntry(
            scene_id="SC03", time_range="16-24s", vo_snippet="Bảng điều khiển báo động đỏ.",
            location="Ohio dispatch room", hero_subject="telemetry board",
            cast_spec="NEW: dispatcher in white shirt", camera_move="orbit",
            exit_seam="dust_smoke_cloud", lighting_key="indoor_cool", person_count=1,
        ),
        SceneMapEntry(
            scene_id="SC04", time_range="24-32s", vo_snippet="Đoàn tàu lao đi không phanh.",
            location="Countryside rail bridge", hero_subject="freight train",
            cast_spec="none", camera_move="pull_back",
            exit_seam="final_hold", seam_color="none", lighting_key="dusk",
        ),
    ]
    smap = SceneMap(job_id="test_dual_job", channel_id="ho_so_ky_la", format_profile="short_9x16", scenes=entries)
    apply_auto_routing(smap, prefer_credit_saving=True)

    # SC01->SC02 has same cast + same_world_continuous -> Omni Flash Frame-Link
    assert smap.scenes[0].transition_mode == "frame_link"
    assert smap.scenes[0].video_model == "omni_flash"
    # SC02->SC03 changes cast & lighting -> Veo 3.1 Lite Seam Mode (10c, zero morphing)
    assert smap.scenes[1].transition_mode == "seam"
    assert smap.scenes[1].video_model == "veo_3_1_lite"

    val = validate_scene_map(smap)
    assert val["valid"] is True, val["errors"]
    assert val["credit_summary"]["credits_saved"] > 0

    img_prompts = compile_scene_image_prompts(smap)
    vid_prompts = compile_scene_video_prompts(smap)
    assert len(img_prompts) == 4 and len(vid_prompts) == 4
    assert "Using the attached reference image(s) (SC01)" in img_prompts[1]["image_prompt"]

    # Positive scene prompt helper delegates cleanly without EP01 hardcoding
    pos_prompt = build_positive_scene_prompt(entries[2], "co-the-ke")
    assert "Endoscopic" in pos_prompt or "biomedical" in pos_prompt.lower() or "Biomedical" in pos_prompt

    # Heterogeneous chain planner keeps Veo Lite Seam free of end_frame_path & reduces credits
    spec = build_dual_model_chain_spec(smap, work_dir=tmp_path)
    tasks = build_scene_pair_tasks(spec.scene_pairs, work_dir=tmp_path, video_model=spec.video_model)
    assert tasks[0].video_model == "omni_flash"
    assert tasks[1].video_model == "veo_3_1_lite"
    assert tasks[1].end_frame_path is None
    assert tasks[1].credit_cost == 10


def test_produce_vn_dual_mode_short_routing_modes(tmp_path: Path) -> None:
    shots = [
        {"id": "S1", "image_path": "s1.png", "prompt": "p1", "cast": "engineer", "duration": 6.0},
        {"id": "S2", "image_path": "s2.png", "prompt": "p2", "cast": "engineer", "based_on": "S1", "duration": 6.0},
        {"id": "S3", "image_path": "s3.png", "prompt": "p3", "cast": "dispatcher", "duration": 6.0},
    ]
    audio = tmp_path / "dummy.wav"
    audio.write_bytes(b"RIFF")

    omni_spec = build_short_video_chain_spec("ho_so_ky_la", "j1", shots, audio, routing_mode="omni_only")
    assert all(sp.video_model == "omni_flash" for sp in omni_spec.scene_pairs)

    lite_spec = build_short_video_chain_spec("ho_so_ky_la", "j2", shots, audio, routing_mode="veo_lite_seam")
    assert all(sp.video_model == "veo_3_1_lite" and sp.end_image_path is None for sp in lite_spec.scene_pairs)
    assert lite_spec.seam_dissolve_sec == 0.18

    dual_spec = build_short_video_chain_spec("ho_so_ky_la", "j3", shots, audio, routing_mode="dual_model_seam")
    assert dual_spec.scene_pairs[0].video_model == "omni_flash"
    assert dual_spec.scene_pairs[1].video_model == "veo_3_1_lite"
    assert dual_spec.scene_pairs[1].end_image_path is None


def test_flow_rpc_deprecation_and_veo_lite_resolution() -> None:
    assert flow_rpc.VIDEO_MODEL == "macaron_cookie_i2v_fl_8s"
    dep, msg = flow_rpc.is_video_model_deprecated("veo_3_1_i2v_s_fast_fl")
    assert dep is True and "2026-12-05" in msg
    assert flow_rpc.resolve_video_model("veo_3_1_lite", aspect="9:16", has_start_frame=True, has_end_frame=False) == "veo_3_1_i2v_s_lite_portrait"
    assert select_clip_duration_and_credits(6.0, "veo_3_1_lite", has_end_frame=False, default_duration_sec=6, auto_duration=False) == (6, 10)


def test_real_ffmpeg_seam_dissolve_stitcher(tmp_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    assert ffmpeg is not None
    c1 = tmp_path / "clip1.mp4"
    c2 = tmp_path / "clip2.mp4"
    for clip_path, color in ((c1, "navy"), (c2, "crimson")):
        subprocess.run(
            [
                ffmpeg, "-y", "-f", "lavfi", "-i", f"color=c={color}:s=360x640:r=30:d=1.0",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip_path),
            ],
            check=True, capture_output=True,
        )

    out_mp4 = tmp_path / "stitched_seam.mp4"
    res = stitch_video_chain(
        clips=[
            {"output_mp4_path": str(c1), "trim_first_frame": False, "target_duration": 1.0},
            {"output_mp4_path": str(c2), "trim_first_frame": False, "target_duration": 1.0},
        ],
        output_mp4_path=out_mp4,
        aspect="9:16",
        fps=30,
        keep_veo_audio=False,
        seam_dissolve_sec=0.18,
    )
    assert out_mp4.is_file()
    assert res["width"] == 1080 and res["height"] == 1920
    assert 1.70 <= res["duration"] <= 1.90
    assert res["nb_frames"] >= 50


def test_all_four_fleet_drift_fixes() -> None:
    # 1. su_ke_lai included in V3_2K_CHANNEL_LOCKS
    assert "su_ke_lai" in V3_2K_CHANNEL_LOCKS
    assert V3_2K_CHANNEL_LOCKS["su_ke_lai"]["short_resolution"] == "1440x2560"

    # 2. dia_com and nghe_song_sot bespoke rules match true niches
    assert "ẩm thực" in CHANNEL_BESPOKE_RULES["dia_com"]["focus"].lower()
    assert "maillard" in CHANNEL_BESPOKE_RULES["dia_com"]["topic_bespoke_triggers"]
    assert "công sở" in CHANNEL_BESPOKE_RULES["nghe_song_sot"]["focus"].lower()
    assert "đàm phán" in CHANNEL_BESPOKE_RULES["nghe_song_sot"]["topic_bespoke_triggers"]

    # 3. chanh_niem_ke formulas updated to Hiểu Tận Gốc V5.0
    cnk_flow = VN_FLOW_VIDEO_FORMULAS["chanh_niem_ke"]
    assert "Hiểu Tận Gốc" in cnk_flow["niche"]
    assert "GIS" in cnk_flow["new_visual_label"]
    assert "Kyoto" not in cnk_flow["style_description"]
    assert "Option W1" in VN_CHANNEL_LOGO_PROMPTS["chanh_niem_ke"]
    assert "AZ-5" in VN_COMPETITOR_SCRIPT_FORMULAS["chanh_niem_ke"]["competitor_dialogue_formula"]["competitor_verbatim_transcript_20s"]

    # 4. All 18 EN channels + 4 aliases mapped across archetypes
    en_ids = [cid for cid in channel_ids() if cid.startswith("en_")]
    assert len(en_ids) == 18
    for cid in en_ids + list(CHANNEL_ALIASES.keys()):
        resolved = get_channel_archetype(cid)
        assert resolved in ARCHETYPE_PROFILES, f"Unmapped EN channel: {cid}"
        if not "-" in cid:
            assert EN_CHANNEL_ARCHETYPE_MAP.get(cid) == resolved
        bp = resolve_niche_fx_blueprint(cid, video_topic="test")
        assert bp["archetype_id"] == resolved
