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
from flow_video.motion_library import (
    apply_positive_framing,
    build_timecoded_video_prompt,
    get_channel_lens_spec,
    get_channel_motion_policy,
)
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


def test_serialized_scene_map_safe_zone_depth_cast_and_channel_lens(tmp_path: Path) -> None:
    entries = [
        SceneMapEntry(
            scene_id="SC01", time_range="0-6s", vo_snippet="Đêm mùng 3 tại Hà Hồi.",
            location="Hanoi bamboo rampart", hero_subject="lacquered palisade gate",
            cast_spec="none", camera_move="push_in", exit_seam="dark_opening",
            lighting_key="torchlit", person_count=0,
        ),
        SceneMapEntry(
            scene_id="SC02", time_range="6-12s", vo_snippet="Tướng quân quan sát từ xa.",
            location="Hanoi bamboo rampart", hero_subject="bamboo speaker horn",
            cast_spec="NEW: red-wrapped Tay Son commander in vermilion tunic",
            reference_scene_ids=["SC01"], camera_move="truck_lateral", exit_seam="edge_pass",
            lighting_key="torchlit", person_count=1,
        ),
        SceneMapEntry(
            scene_id="SC03", time_range="12-18s", vo_snippet="Hàng vạn quân lặng lẽ siết vòng vây.",
            location="Muddy outer trench", hero_subject="Tay Son army ranks with bamboo shields",
            cast_spec="SAME as SC02: Tay Son commander alongside calm formed army rows",
            reference_scene_ids=["SC02"], camera_move="crane_up", exit_seam="final_hold",
            lighting_key="torchlit", person_count=0,
        ),
    ]
    smap = SceneMap(
        job_id="ep06_test",
        channel_id="su_ke_lai",
        format_profile="short_9x16",
        clip_duration_sec=6,
        approved=True,
        series_meta={"series_id": "ky_dau_1789", "part_number": 1, "total_parts": 3},
        scenes=entries,
    )
    out_json = tmp_path / "scene_map.json"
    smap.to_json_file(out_json)
    reloaded = SceneMap.from_json_file(out_json)
    assert reloaded.series_meta["part_number"] == 1
    assert reloaded.series_meta["total_parts"] == 3

    assert get_channel_lens_spec("su_ke_lai") == "35mm anamorphic film lens"
    assert get_channel_lens_spec("ho_so_ky_la") == "wide 28mm lens"

    img_prompts = compile_scene_image_prompts(reloaded)
    assert "20% and 65%" in img_prompts[0]["image_prompt"]
    assert "foreground, midground, and background" in img_prompts[0]["image_prompt"]
    assert "Block A Uninhabited Frame" in img_prompts[0]["image_prompt"]
    assert "Block B Single Subject Framing" in img_prompts[1]["image_prompt"]
    assert "Block B Ensemble Formation" in img_prompts[2]["image_prompt"]

    vid_prompts = compile_scene_video_prompts(reloaded)
    assert "35mm anamorphic film lens" in vid_prompts[0]["video_prompt"]


def test_visual_pacing_serialized_detail_short_keeps_short_9x16_strict() -> None:
    from visual_pacing import check_see_say_beat_density

    # 12 animated Flow video beats across 52.8s (~4.4s each)
    scenes = []
    t = 0.0
    for idx in range(12):
        dur = 3.6 if idx == 0 else (5.2 if idx == 11 else 4.4)
        scenes.append({
            "id": f"SC{idx + 1:02d}",
            "start": round(t, 3),
            "end": round(t + dur, 3),
            "images": [{"id": f"B{idx:02d}", "at": 0.0}],
        })
        t += dur

    assert check_see_say_beat_density(scenes, format_profile="serialized_detail_short") == []
    # Strict static short_9x16 must continue rejecting sparse >3.0s/beat timelines
    strict_errors = check_see_say_beat_density(scenes, format_profile="short_9x16")
    assert strict_errors and any("LOW_VISUAL_BEAT_DENSITY" in e for e in strict_errors)


def test_resolve_video_model_want_lite_catalog_fallbacks() -> None:
    catalog_no_lite = [
        {
            "id": "veo_3_1_quality",
            "display_name": "Veo 3.1 - Quality",
            "usages": [
                {"key": "veo_3_1_i2v_s_portrait", "duration": 8, "aspects": [1], "capabilities": [[1, 5]]},
                {"key": "veo_3_1_i2v_s_quality_6s", "duration": 6, "aspects": [2, 1], "capabilities": [[1, 5]]},
            ],
        },
        {
            "id": "macaron_cookie",
            "display_name": "Omni 1.2 Flash",
            "usages": [
                {"key": "macaron_cookie_i2v_6s_360p", "duration": 6, "aspects": [2, 1], "capabilities": [[1, 5]]},
                {"key": "macaron_cookie_i2v_6s", "duration": 6, "aspects": [2, 1], "capabilities": [[1, 5]]},
            ],
        },
    ]
    resolved = flow_rpc.resolve_video_model(
        "veo_3_1_lite",
        aspect="9:16",
        has_start_frame=True,
        has_end_frame=False,
        catalog=catalog_no_lite,
        duration_seconds=6,
    )
    assert resolved == "macaron_cookie_i2v_6s"

    catalog_low_prio_only = [
        {
            "id": "veo_3_1_quality",
            "display_name": "Veo 3.1 - Quality",
            "usages": [
                {"key": "veo_3_1_i2v_s_quality_6s", "duration": 6, "aspects": [2, 1], "capabilities": [[1, 5]]},
            ],
        },
        {
            "id": "veo_3_1_lite_low_priority",
            "display_name": "Veo 3.1 - Lite [Lower Priority]",
            "usages": [
                {"key": "veo_3_1_i2v_s_lite_6s_low_priority", "duration": 6, "aspects": [2, 1], "capabilities": [[1, 5]]},
            ],
        },
    ]
    resolved_lp = flow_rpc.resolve_video_model(
        "veo_3_1_lite",
        aspect="9:16",
        has_start_frame=True,
        has_end_frame=False,
        catalog=catalog_low_prio_only,
        duration_seconds=6,
    )
    assert resolved_lp == "veo_3_1_i2v_s_lite_6s_low_priority"


def _make_dummy_ledger():
    import time

    class _DummyLedger:
        def __init__(self) -> None:
            self.cooldowns: dict[str, float] = {}

        def get_balance(self, pid: str) -> int:
            return 200

        def is_eligible(self, pid: str, min_credits: int = 7) -> bool:
            return True

        def is_on_cooldown(self, pid: str) -> bool:
            return self.cooldowns.get(pid, 0.0) > time.time()

        def mark_cooldown(self, pid: str, seconds: float = 60.0, reason: str = "") -> None:
            self.cooldowns[pid] = time.time() + seconds

        def clear_cooldown(self, pid: str) -> None:
            self.cooldowns.pop(pid, None)

        def select_eligible_profiles(self, profiles, min_credits: int = 7):
            return list(profiles)

        def pick_and_reserve(self, **kwargs):
            return None

        def rollback(self, *args, **kwargs):
            pass

    return _DummyLedger()


def test_orchestrator_closes_warm_session_and_escalates_on_unusual_activity(tmp_path: Path, monkeypatch) -> None:
    import asyncio
    import time
    from types import SimpleNamespace
    from flow_video.models import ChainMode, ScenePairSpec, VideoChainSpec, VideoClipTask
    from flow_video.orchestrator import FlowVideoChainOrchestrator

    f0 = tmp_path / "f0.png"
    f0.write_bytes(b"fake")
    spec = VideoChainSpec(
        job_id="test_warm_evict",
        mode=ChainMode.SCENE_PAIRS,
        channel_id="su_ke_lai",
        aspect="9:16",
        video_model="veo_3_1_lite",
        duration_seconds=6,
        auto_fallback_zero_credit=False,
        scene_pairs=[
            ScenePairSpec(
                id="B00",
                start_image_prompt="s",
                start_image_path=str(f0),
                video_model="veo_3_1_lite",
                transition_mode="seam",
            )
        ],
    )
    orch = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work",
        output_mp4_path=tmp_path / "out.mp4",
        max_workers=1,
        resume=False,
        max_retries_per_clip=4,
        reuse_warm_sessions=True,
    )
    orch.credit_ledger = _make_dummy_ledger()  # type: ignore[assignment]
    p1 = {"name": "prof_1", "cdp_port": 9901}
    p2 = {"name": "prof_2", "cdp_port": 9902}
    monkeypatch.setattr(orch, "_get_channel_profiles", lambda: [p1, p2])
    monkeypatch.setattr("flow_video.orchestrator.get_process_manager", lambda: SimpleNamespace(terminate_by_port=lambda port: True))

    released = {"port": False, "slot": False, "closed": False}

    class _FakeSession:
        profile_cfg = p1

        async def generate_video_from_frames(self, **kwargs):
            raise RuntimeError("FLOW_PROVIDER_BLOCKED: PUBLIC_ERROR_UNUSUAL_ACTIVITY")

        async def close(self):
            released["closed"] = True

    class _FakeLock:
        def release(self):
            released["port"] = True

    class _FakeSlot:
        def release(self):
            released["slot"] = True

    orch._warm_sessions[9901] = {
        "profile_cfg": p1,
        "session": _FakeSession(),
        "port_lock": _FakeLock(),
        "browser_slot": _FakeSlot(),
        "credits_synced": True,
    }
    task = VideoClipTask(
        clip_id="B00",
        index=0,
        start_frame_path=str(f0),
        end_frame_path=None,
        motion_prompt="slow push",
        duration_seconds=6,
        target_duration=5.0,
        output_mp4_path=str(tmp_path / "clip_00.mp4"),
        video_model="veo_3_1_lite",
        transition_mode="seam",
        credit_cost=10,
    )

    try:
        asyncio.run(orch._generate_single_clip(task, profile_cfg=p1))
        raise AssertionError("Expected RuntimeError from fake session")
    except RuntimeError:
        pass
    assert 9901 not in orch._warm_sessions
    assert released == {"port": True, "slot": True, "closed": True}

    # Now test _generate_clips_parallel deprioritizes blocked p1 and applies >=120s backoff
    orch._profile_cooldowns.clear()
    orch.credit_ledger.cooldowns.clear()
    tried: list[str] = []

    async def _fake_single(clip: VideoClipTask, profile_cfg: dict | None = None) -> None:
        pname = str((profile_cfg or {}).get("name"))
        tried.append(pname)
        if pname == "prof_1":
            raise RuntimeError("FLOW_PROVIDER_BLOCKED: PUBLIC_ERROR_UNUSUAL_ACTIVITY")
        Path(clip.output_mp4_path).write_bytes(b"mp4")

    monkeypatch.setattr(orch, "_generate_single_clip", _fake_single)
    # Seed prof_1 warm session with streak=1 so warm_cand must skip it when streak>0
    orch._warm_sessions[9901] = {"profile_cfg": p1}
    asyncio.run(orch._generate_clips_parallel([task]))
    assert tried == ["prof_1", "prof_2"]
    assert orch._profile_block_streaks["prof_1"] == 1
    assert orch._profile_cooldowns["prof_1"] - time.time() >= 115.0


def test_orchestrator_downgrades_veo_lite_on_model_access_denied(tmp_path: Path, monkeypatch) -> None:
    import asyncio
    from flow_video.models import ChainMode, ScenePairSpec, VideoChainSpec, VideoClipTask
    from flow_video.orchestrator import FlowVideoChainOrchestrator

    f0 = tmp_path / "f0.png"
    f0.write_bytes(b"fake")
    spec = VideoChainSpec(
        job_id="test_access_denied",
        mode=ChainMode.SCENE_PAIRS,
        channel_id="su_ke_lai",
        aspect="9:16",
        video_model="veo_3_1_lite",
        duration_seconds=6,
        auto_fallback_zero_credit=False,
        scene_pairs=[
            ScenePairSpec(
                id="B00",
                start_image_prompt="s",
                start_image_path=str(f0),
                video_model="veo_3_1_lite",
                transition_mode="seam",
            )
        ],
    )
    orch = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work",
        output_mp4_path=tmp_path / "out.mp4",
        max_workers=1,
        resume=False,
        max_retries_per_clip=4,
        reuse_warm_sessions=False,
    )
    orch.credit_ledger = _make_dummy_ledger()  # type: ignore[assignment]
    monkeypatch.setattr(orch, "_get_channel_profiles", lambda: [{"name": "prof_ok", "cdp_port": 9903}])

    seen_calls: list[tuple[str, object, int]] = []

    async def _fake_single(clip: VideoClipTask, profile_cfg: dict | None = None) -> None:
        seen_calls.append((clip.video_model, clip.end_frame_path, clip.credit_cost))
        if clip.video_model == "veo_3_1_lite":
            raise RuntimeError("eb1hJf failed: PUBLIC_ERROR_MODEL_ACCESS_DENIED")
        Path(clip.output_mp4_path).write_bytes(b"mp4")

    monkeypatch.setattr(orch, "_generate_single_clip", _fake_single)
    task = VideoClipTask(
        clip_id="B00",
        index=0,
        start_frame_path=str(f0),
        end_frame_path=None,
        motion_prompt="slow push",
        duration_seconds=6,
        target_duration=5.0,
        output_mp4_path=str(tmp_path / "clip_00.mp4"),
        video_model="veo_3_1_lite",
        transition_mode="seam",
        credit_cost=10,
    )
    asyncio.run(orch._generate_clips_parallel([task]))
    assert seen_calls == [("veo_3_1_lite", None, 10), ("omni_flash", None, 18)]
    assert task.status == "completed"
    assert not orch._is_profile_cooled_down("prof_ok")


def test_scene_map_tactical_sand_table_serialization_and_positive_prompt(tmp_path: Path) -> None:
    import re

    legacy_dict = {
        "scene_id": "SC01",
        "time_range": "0-6s",
        "vo_snippet": "Đêm trước trận đánh.",
        "location": "Ngọc Hồi road",
        "hero_subject": "earthen palisade",
    }
    legacy_entry = SceneMapEntry.from_dict(legacy_dict)
    assert legacy_entry.scene_type == "live_action"
    assert legacy_entry.delivery_mode == "narrative_cinema"

    sand_entry = SceneMapEntry(
        scene_id="SC02",
        time_range="6-12s",
        vo_snippet="Ba mũi giáp công khép kín vòng vây.",
        location="dark timber war tent",
        hero_subject="clay terrain relief with wooden troop blocks",
        camera_move="push_in",
        exit_seam="final_hold",
        seam_color="none",
        lighting_key="warm_oil_lamp",
        time_of_day="night",
        scene_type="tactical_sand_table",
        delivery_mode="tactical_breakdown",
    )
    smap = SceneMap(
        job_id="sand_table_test",
        channel_id="su_ke_lai",
        format_profile="short_9x16",
        scenes=[legacy_entry, sand_entry],
    )
    json_path = tmp_path / "sand_scene_map.json"
    smap.to_json_file(json_path)
    reloaded = SceneMap.from_json_file(json_path)
    assert reloaded.scenes[0].scene_type == "live_action"
    assert reloaded.scenes[1].scene_type == "tactical_sand_table"
    assert reloaded.scenes[1].delivery_mode == "tactical_breakdown"

    compiled = compile_scene_image_prompts(reloaded)
    sand_prompt = compiled[1]["image_prompt"]
    assert compiled[1]["scene_type"] == "tactical_sand_table"
    assert compiled[1]["delivery_mode"] == "tactical_breakdown"

    low = sand_prompt.lower()
    assert "2200k oil-lamp" in low
    assert "vermilion" in low
    assert "dark-indigo" in low
    assert "weathered hand" in low
    assert "35mm cinema depth of field" in low
    assert "raw wet clay" in low
    assert "unmarked hand-carved wooden blocks" in low
    for forbidden_noun in ("inscribed symbols", "printed maps", "modern displays", "plastic pieces", "no text", "zero text"):
        assert forbidden_noun not in low
    assert not re.search(r"\bno\s+(?:text|cars|vehicles|people|talking|speech|logos?|watermarks?)\b", low)

    # Also verify compile_scene_video_prompts for su_ke_lai inland vs sand table vs river scenes
    river_entry = SceneMapEntry(
        scene_id="SC03",
        time_range="12-18s",
        vo_snippet="Đoàn thuyền tiến ra cửa sông.",
        location="Bạch Đằng estuary",
        hero_subject="wooden river barge",
        camera_move="tracking_alongside",
        exit_seam="final_hold",
        seam_color="none",
    )
    sand_with_cast = SceneMapEntry(
        scene_id="SC04",
        time_range="18-24s",
        vo_snippet="Bàn tay đặt khối gỗ lên gò đất.",
        location="dark timber war tent",
        hero_subject="wooden troop block",
        cast_spec="NEW: commander hand",
        person_count=1,
        camera_move="orbit",
        exit_seam="final_hold",
        seam_color="none",
        scene_type="tactical_sand_table",
        delivery_mode="tactical_breakdown",
    )
    vid_smap = SceneMap(
        job_id="vid_prompt_check",
        channel_id="su_ke_lai",
        format_profile="short_9x16",
        scenes=[legacy_entry, sand_entry, river_entry, sand_with_cast],
    )
    vid_prompts = compile_scene_video_prompts(vid_smap)
    inland_vid = vid_prompts[0]["video_prompt"]
    sand_vid = vid_prompts[1]["video_prompt"]
    river_vid = vid_prompts[2]["video_prompt"]
    sand_cast_vid = vid_prompts[3]["video_prompt"]

    assert "timber fortifications, walls, banners, shields, and plain tunics" in inland_vid
    assert "masts, hulls" not in inland_vid
    assert "masts, hulls, buildings, walls, and uniforms" in river_vid

    assert "wooden command table, sculpted clay relief, and carved wooden blocks" in sand_vid
    assert "over the tabletop at a high 45-degree angle" in sand_vid
    assert "at chest height" not in sand_vid
    assert "hands resting naturally" not in sand_cast_vid
    assert "from a high 45-degree overhead angle in" in sand_cast_vid
    assert "at head height" not in sand_cast_vid

    for move_name in ("push_in", "pull_back", "truck_lateral", "tracking_alongside", "orbit", "crane_up"):
        p_table = build_timecoded_video_prompt(
            camera_move=move_name,
            hero_subject="wooden troop blocks",
            setting="dark timber war tent",
            model="veo_3_1_lite",
            clip_duration_sec=6,
            scene_type="tactical_sand_table",
            lens_spec="35mm anamorphic film lens",
        )
        assert "45-degree" in p_table
        for human_h in ("at chest height", "at hip height", "at head height", "from low ground level"):
            assert human_h not in p_table


def test_orchestrator_tier0_pool_preroutes_after_two_lite_denials(tmp_path: Path, monkeypatch, caplog) -> None:
    import asyncio
    import logging

    from flow_cdp.credit_ledger import CreditLedger
    from flow_video.models import ChainMode, ScenePairSpec, VideoChainSpec, VideoClipTask
    from flow_video.orchestrator import FlowVideoChainOrchestrator

    f0 = tmp_path / "f0.png"
    f1 = tmp_path / "f1.png"
    f0.write_bytes(b"fake")
    f1.write_bytes(b"fake")

    def _make_seam_tasks(count: int) -> list[VideoClipTask]:
        return [
            VideoClipTask(
                clip_id=f"B{idx:02d}",
                index=idx,
                start_frame_path=str(f0),
                end_frame_path=str(f1),
                motion_prompt="slow push",
                duration_seconds=6,
                target_duration=5.0,
                output_mp4_path=str(tmp_path / f"clip_{idx:02d}.mp4"),
                video_model="veo_3_1_lite",
                transition_mode="seam",
                credit_cost=10,
            )
            for idx in range(count)
        ]

    spec = VideoChainSpec(
        job_id="test_tier0_pool_fallback",
        mode=ChainMode.SCENE_PAIRS,
        channel_id="su_ke_lai",
        aspect="9:16",
        video_model="veo_3_1_lite",
        duration_seconds=6,
        auto_fallback_zero_credit=False,
        scene_pairs=[
            ScenePairSpec(
                id="B00",
                start_image_prompt="s",
                start_image_path=str(f0),
                video_model="veo_3_1_lite",
                transition_mode="seam",
            )
        ],
    )

    # Case 1: All profiles are paygate_tier == 0 -> after 2 distinct profiles deny veo_3_1_lite,
    # B02 must pre-route directly to omni_flash (end_frame_path=None, credit_cost=18) without RPC on Lite.
    orch = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work_tier0",
        output_mp4_path=tmp_path / "out_tier0.mp4",
        max_workers=1,
        resume=False,
        max_retries_per_clip=6,
        reuse_warm_sessions=False,
    )
    ledger = CreditLedger(path=tmp_path / "credits_tier0.json")
    for pname in ("tier0_a", "tier0_b", "tier0_c"):
        ledger.sync_balance(pname, 200, paygate_tier=0)
    orch.credit_ledger = ledger
    profiles_tier0 = [
        {"name": "tier0_a", "cdp_port": 9911},
        {"name": "tier0_b", "cdp_port": 9912},
        {"name": "tier0_c", "cdp_port": 9913},
    ]
    monkeypatch.setattr(orch, "_get_channel_profiles", lambda: profiles_tier0)

    calls_tier0: list[tuple[str, str, str, object, int]] = []

    async def _fake_single_tier0(clip: VideoClipTask, profile_cfg: dict | None = None) -> None:
        pname = str((profile_cfg or {}).get("name"))
        calls_tier0.append((clip.clip_id, pname, clip.video_model, clip.end_frame_path, clip.credit_cost))
        if clip.video_model == "veo_3_1_lite":
            raise RuntimeError("eb1hJf failed: PUBLIC_ERROR_MODEL_ACCESS_DENIED")
        Path(clip.output_mp4_path).write_bytes(b"mp4")

    monkeypatch.setattr(orch, "_generate_single_clip", _fake_single_tier0)
    tasks_tier0 = _make_seam_tasks(3)
    with caplog.at_level(logging.WARNING):
        asyncio.run(orch._generate_clips_parallel(tasks_tier0))

    assert len(orch._tier0_veo_lite_denied_profiles) == 2
    assert all(t.status == "completed" for t in tasks_tier0)
    # B02 never called veo_3_1_lite RPC
    b02_calls = [c for c in calls_tier0 if c[0] == "B02"]
    assert b02_calls == [("B02", b02_calls[0][1], "omni_flash", None, 18)]
    assert any("[POOL_TIER0_MODEL_FALLBACK]" in rec.message for rec in caplog.records)

    # Case 2: If a healthy paygate_tier >= 1 profile remains, still allow veo_3_1_lite probing.
    orch_pro = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work_pro",
        output_mp4_path=tmp_path / "out_pro.mp4",
        max_workers=1,
        resume=False,
        max_retries_per_clip=6,
        reuse_warm_sessions=False,
    )
    ledger_pro = CreditLedger(path=tmp_path / "credits_pro.json")
    ledger_pro.sync_balance("tier0_a", 200, paygate_tier=0)
    ledger_pro.sync_balance("tier0_b", 200, paygate_tier=0)
    ledger_pro.sync_balance("tier1_pro", 200, paygate_tier=1)
    orch_pro.credit_ledger = ledger_pro
    profiles_pro = [
        {"name": "tier0_a", "cdp_port": 9921},
        {"name": "tier0_b", "cdp_port": 9922},
        {"name": "tier1_pro", "cdp_port": 9923},
    ]
    monkeypatch.setattr(orch_pro, "_get_channel_profiles", lambda: profiles_pro)

    calls_pro: list[tuple[str, str, str]] = []

    async def _fake_single_pro(clip: VideoClipTask, profile_cfg: dict | None = None) -> None:
        pname = str((profile_cfg or {}).get("name"))
        calls_pro.append((clip.clip_id, pname, clip.video_model))
        if clip.video_model == "veo_3_1_lite" and pname != "tier1_pro":
            raise RuntimeError("eb1hJf failed: PUBLIC_ERROR_MODEL_ACCESS_DENIED")
        Path(clip.output_mp4_path).write_bytes(b"mp4")

    monkeypatch.setattr(orch_pro, "_generate_single_clip", _fake_single_pro)
    tasks_pro = _make_seam_tasks(3)

    # Simulate 2 tier0 denials already recorded while tier1_pro remains healthy;
    # patch _reset_tier0_veo_lite_state or let B00/B01 test if pro runs directly or after reset:
    # First verify _reset_tier0_veo_lite_state resets session set cleanly, then verify probing with 2 prior denials + tier1_pro.
    orch_pro._tier0_veo_lite_denied_profiles = {"tier0_a", "tier0_b"}
    asyncio.run(orch_pro._generate_clips_parallel(tasks_pro))
    assert all(t.status == "completed" for t in tasks_pro)
    assert any(c[1] == "tier1_pro" and c[2] == "veo_3_1_lite" for c in calls_pro)

    # Also verify directly that when 2 denied profiles exist in-session AND tier1_pro is healthy,
    # _maybe_preroute_tier0_veo_lite keeps veo_3_1_lite enabled for probing.
    orch_pro._tier0_veo_lite_denied_profiles = {"tier0_a", "tier0_b"}
    probe_task = _make_seam_tasks(1)[0]
    is_lite, _, _ = orch_pro._maybe_preroute_tier0_veo_lite(probe_task, profiles_pro)
    assert is_lite is True
    assert probe_task.video_model == "veo_3_1_lite"


def test_orchestrator_skip_denied_tier0_lite_routes_direct_omni_and_preserves_pro_probe(
    tmp_path: Path, monkeypatch, caplog
) -> None:
    import asyncio
    import logging

    from flow_cdp.credit_ledger import CreditLedger
    from flow_video.models import ChainMode, ScenePairSpec, VideoChainSpec, VideoClipTask
    from flow_video.orchestrator import FlowVideoChainOrchestrator

    f0 = tmp_path / "f0.png"
    f1 = tmp_path / "f1.png"
    f0.write_bytes(b"fake")
    f1.write_bytes(b"fake")

    spec = VideoChainSpec(
        job_id="test_skip_tier0_lite",
        mode=ChainMode.SCENE_PAIRS,
        channel_id="su_ke_lai",
        aspect="9:16",
        video_model="veo_3_1_lite",
        duration_seconds=6,
        auto_fallback_zero_credit=False,
        scene_pairs=[
            ScenePairSpec(
                id="B00",
                start_image_prompt="s",
                start_image_path=str(f0),
                video_model="veo_3_1_lite",
                transition_mode="seam",
            )
        ],
    )

    def _task(idx: int) -> VideoClipTask:
        return VideoClipTask(
            clip_id=f"B{idx:02d}",
            index=idx,
            start_frame_path=str(f0),
            end_frame_path=str(f1),
            motion_prompt="slow push",
            duration_seconds=6,
            target_duration=5.0,
            output_mp4_path=str(tmp_path / f"clip_{idx:02d}.mp4"),
            video_model="veo_3_1_lite",
            transition_mode="seam",
            credit_cost=10,
        )

    # Case 1: Only tier-0 eligible -> clip #1 downgrades IMMEDIATELY to omni_flash before RPC
    orch_t0 = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work_t0",
        output_mp4_path=tmp_path / "out_t0.mp4",
        max_workers=1,
        resume=False,
        max_retries_per_clip=4,
        reuse_warm_sessions=False,
        skip_denied_tier0_lite=True,
    )
    ledger_t0 = CreditLedger(path=tmp_path / "credits_t0.json")
    ledger_t0.sync_balance("tier0_a", 200, paygate_tier=0)
    ledger_t0.sync_balance("tier0_b", 200, paygate_tier=0)
    orch_t0.credit_ledger = ledger_t0
    monkeypatch.setattr(
        orch_t0,
        "_get_channel_profiles",
        lambda: [{"name": "tier0_a", "cdp_port": 9931}, {"name": "tier0_b", "cdp_port": 9932}],
    )

    calls_t0: list[tuple[str, str, str, object, int]] = []

    async def _fake_single_t0(clip: VideoClipTask, profile_cfg: dict | None = None) -> None:
        pname = str((profile_cfg or {}).get("name"))
        calls_t0.append((clip.clip_id, pname, clip.video_model, clip.end_frame_path, clip.credit_cost))
        Path(clip.output_mp4_path).write_bytes(b"mp4")

    monkeypatch.setattr(orch_t0, "_generate_single_clip", _fake_single_t0)
    tasks_t0 = [_task(0), _task(1)]
    with caplog.at_level(logging.WARNING):
        asyncio.run(orch_t0._generate_clips_parallel(tasks_t0))

    assert all(t.status == "completed" for t in tasks_t0)
    assert [c[2] for c in calls_t0] == ["omni_flash", "omni_flash"]
    assert all(c[3] is None and c[4] == 18 for c in calls_t0)
    assert any("[POOL_TIER0_DIRECT_OMNI]" in rec.message for rec in caplog.records)

    # Case 2: At least one eligible paygate_tier >= 1 profile exists -> still probes veo_3_1_lite
    orch_pro = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work_pro_direct",
        output_mp4_path=tmp_path / "out_pro_direct.mp4",
        max_workers=1,
        resume=False,
        max_retries_per_clip=4,
        reuse_warm_sessions=False,
        skip_denied_tier0_lite=True,
    )
    ledger_pro = CreditLedger(path=tmp_path / "credits_pro_direct.json")
    ledger_pro.sync_balance("tier0_a", 200, paygate_tier=0)
    ledger_pro.sync_balance("tier1_pro", 200, paygate_tier=1)
    orch_pro.credit_ledger = ledger_pro
    monkeypatch.setattr(
        orch_pro,
        "_get_channel_profiles",
        lambda: [{"name": "tier0_a", "cdp_port": 9941}, {"name": "tier1_pro", "cdp_port": 9942}],
    )

    calls_pro: list[tuple[str, str, str]] = []

    async def _fake_single_pro(clip: VideoClipTask, profile_cfg: dict | None = None) -> None:
        pname = str((profile_cfg or {}).get("name"))
        calls_pro.append((clip.clip_id, pname, clip.video_model))
        Path(clip.output_mp4_path).write_bytes(b"mp4")

    monkeypatch.setattr(orch_pro, "_generate_single_clip", _fake_single_pro)
    tasks_pro = [_task(0)]
    asyncio.run(orch_pro._generate_clips_parallel(tasks_pro))
    assert calls_pro == [("B00", "tier1_pro", "veo_3_1_lite")]
