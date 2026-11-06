"""Unit tests for V3 English Channel Logos, Per-Channel Flow Video Formulas,
1.05x Overscan Sparkle Removal, Dynamic CreditLedger Priority, and Hybrid Scene-Group Sync.
"""

from __future__ import annotations

import asyncio
import subprocess
import time
from pathlib import Path
from sys.flow_video.models import (
    ChainMode,
    KeyframeSpec,
    ScenePairSpec,
    VideoChainSpec,
    VideoClipTask,
)
from sys.flow_video.orchestrator import FlowVideoChainOrchestrator
from sys.flow_video.stitcher import stitch_video_chain
from typing import Any
from unittest.mock import patch

from channels.en_flow_video_formulas import (
    EN_CHANNEL_LOGO_PROMPTS,
    EN_FLOW_VIDEO_FORMULAS,
    FLOW_FRAME_CONTROL_MODES,
    RETENTION_SHOT_BLUEPRINTS,
    build_channel_motion_prompt,
    build_reference_keyframe_prompt,
)
from flow_cdp.credit_ledger import CreditLedger
from PIL import Image
from tools.produce_en_flow_dynamic_demo import build_scene_pairs_from_shots

EXPECTED_18_EN_CHANNELS = {
    "en-first-principles",
    "en-scale-and-bone",
    "en-pocket-cosmos",
    "en-deep-time-strata",
    "en-inside-vessel",
    "en-macro-gears",
    "en-fine-print",
    "en-crowd-strings",
    "en-cold-case-ink",
    "en-choke-point",
    "en-root-and-canopy",
    "en-spawn-to-apex",
    "en-second-arrow",
    "en-bamboo-marble",
    "en-kindred-sketch",
    "en-lazy-brain",
    "en-career-leverage",
    "en-wallet-anatomy",
}


def test_all_18_channels_have_flow_video_formulas_and_zero_text_logo_prompts() -> None:
    """Verify every English channel has complete V3 Flow motion physics and clean zero-text logo prompts."""
    assert set(EN_FLOW_VIDEO_FORMULAS.keys()) == EXPECTED_18_EN_CHANNELS
    assert set(EN_CHANNEL_LOGO_PROMPTS.keys()) == EXPECTED_18_EN_CHANNELS
    assert "reference_start_end" in FLOW_FRAME_CONTROL_MODES
    assert "boundary_extend" in FLOW_FRAME_CONTROL_MODES
    assert "single_frame_physics" in FLOW_FRAME_CONTROL_MODES
    assert "short_9x16_demo" in RETENTION_SHOT_BLUEPRINTS
    assert "long_16x9_demo" in RETENTION_SHOT_BLUEPRINTS

    for slug in EXPECTED_18_EN_CHANNELS:
        formula = EN_FLOW_VIDEO_FORMULAS[slug]
        assert formula["subject_physics"]
        assert len(formula["camera_grammar"]) >= 2
        assert formula["continuity_anchor"]
        assert len(formula["forbidden_artifacts"]) >= 2

        mp = build_channel_motion_prompt(slug, "gear wheel rotates clockwise")
        assert "gear wheel rotates clockwise" in mp
        assert "zero text" in mp.lower()

        kp = build_reference_keyframe_prompt(slug, "camera pulls back to reveal full mechanism")
        assert "what happens next" in kp.lower()
        assert "zero words" in kp.lower()

        logo_prompt = EN_CHANNEL_LOGO_PROMPTS[slug]
        assert "no text" in logo_prompt.lower()
        assert "25% empty margin" in logo_prompt.lower()


def test_overscan_crop_removes_bottom_right_corner_sparkle(tmp_path: Path) -> None:
    """Verify overscan_crop=1.05 removes raw corner artifacts at (96..100% W, 96..100% H)."""
    frame_png = tmp_path / "raw_with_corner_mark.png"
    img = Image.new("RGB", (640, 360), color=(20, 40, 120))
    # Paint bright white corner artifact in bottom-right 2.2% zone (x=626..639, y=352..359)
    for x in range(626, 640):
        for y in range(352, 360):
            img.putpixel((x, y), (255, 255, 255))
    img.save(frame_png)

    raw_clip = tmp_path / "raw_clip.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-t",
            "0.5",
            "-r",
            "30",
            "-i",
            str(frame_png),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "ultrafast",
            str(raw_clip),
        ],
        check=True,
        capture_output=True,
    )

    stitched_mp4 = tmp_path / "stitched_clean.mp4"
    stitch_video_chain(
        clips=[str(raw_clip)],
        output_mp4_path=stitched_mp4,
        aspect="16:9",
        fps=30,
        overscan_crop=1.05,
    )

    check_png = tmp_path / "check_frame.png"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(stitched_mp4), "-frames:v", "1", str(check_png)],
        check=True,
        capture_output=True,
    )
    with Image.open(check_png) as out_im:
        rgb = out_im.convert("RGB")
        assert rgb.size == (1920, 1080)
        r, g, b = rgb.getpixel((1915, 1075))
        # White corner artifact (255,255,255) must be completely cropped out, leaving deep blue
        assert r < 60 and g < 80 and b > 90


def test_dynamic_credit_ledger_ordering_unlocks_high_credit_profiles(tmp_path: Path) -> None:
    """Verify _get_channel_profiles prioritizes live high-credit accounts and pushes 0-credit accounts last."""
    mock_profiles = [
        {"name": f"profile_{i}", "cdp_port": 9220 + i}
        for i in range(1, 8)
    ]
    spec = VideoChainSpec(job_id="dynamic_order_test")
    orch = FlowVideoChainOrchestrator(spec=spec, work_dir=tmp_path / "w", dry_run=True)
    ledger = CreditLedger(path=tmp_path / "credits.json")
    # Set profile_1 and profile_3 to 0/2 credits, and profile_2 (previously statically blocked!) to 1050 credits
    ledger.sync_balance("profile_1", 0)
    ledger.sync_balance("profile_2", 1050)
    ledger.sync_balance("profile_3", 2)
    ledger.sync_balance("profile_4", 900)
    ledger.sync_balance("profile_5", 850)
    ledger.sync_balance("profile_6", 1800)
    ledger.sync_balance("profile_7", 4)
    orch.credit_ledger = ledger

    with patch("sys.flow_video.orchestrator.get_all_configured_profiles", return_value=mock_profiles):
        ordered = orch._get_channel_profiles()

    names = [p["name"] for p in ordered]
    # First 4 MUST be the 4 video-eligible accounts (>= 7 credits), including profile_2!
    assert set(names[:4]) == {"profile_2", "profile_4", "profile_5", "profile_6"}
    # Last 3 MUST be the < 7 credit accounts
    assert set(names[4:]) == {"profile_1", "profile_3", "profile_7"}


def test_mid_flight_credit_exhaustion_falls_back_cleanly(tmp_path: Path) -> None:
    """Verify that if credits run out mid-run after clip 0, clip 1 falls back to zero-credit slide cleanly."""
    f0 = tmp_path / "f0.png"
    f1 = tmp_path / "f1.png"
    f2 = tmp_path / "f2.png"
    for p, col in ((f0, (30, 60, 90)), (f1, (60, 90, 120)), (f2, (90, 120, 150))):
        Image.new("RGB", (320, 180), color=col).save(p)

    spec = VideoChainSpec(
        job_id="mid_flight_fb",
        mode=ChainMode.DAISY_CHAIN,
        video_model="omni_flash",
        duration_seconds=4,
        auto_duration=False,
        auto_fallback_zero_credit=True,
        keyframes=[
            KeyframeSpec(id="k0", image_path=str(f0)),
            KeyframeSpec(id="k1", image_path=str(f1)),
            KeyframeSpec(id="k2", image_path=str(f2)),
        ],
    )
    out_mp4 = tmp_path / "mid_flight_out.mp4"
    orch = FlowVideoChainOrchestrator(spec=spec, work_dir=tmp_path / "work", output_mp4_path=out_mp4, max_workers=1)
    ledger = CreditLedger(path=tmp_path / "mid_credits.json")
    # Exactly 7 credits -> enough for clip 0 (7 credits), 0 left for clip 1!
    ledger.sync_balance("solo_profile", 7)
    orch.credit_ledger = ledger

    class OneClipSession:
        def __init__(self, profile_cfg: dict) -> None:
            self.name = profile_cfg["name"]

        async def connect(self) -> None:
            pass

        async def close(self) -> None:
            pass

        async def query_credits(self) -> dict:
            return {"remaining": ledger.get_balance(self.name)}

        async def generate_video_from_frames(self, **kwargs) -> None:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=1:size=320x180:rate=30",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                    str(kwargs["output_mp4_path"]),
                ],
                check=True,
                capture_output=True,
            )

    with (
        patch("sys.flow_video.orchestrator.get_all_configured_profiles", return_value=[{"name": "solo_profile", "cdp_port": 9222}]),
        patch("sys.flow_video.orchestrator.DirectCDPProfileSession", side_effect=OneClipSession),
        patch("sys.flow_video.orchestrator.ProfilePortLock") as mock_pl,
        patch("sys.flow_video.orchestrator.GlobalBrowserSlot") as mock_bs,
        patch("sys.flow_video.orchestrator.get_process_manager") as mock_pm,
    ):
        mock_pl.return_value.acquire.return_value = True
        mock_bs.return_value.acquire.return_value = True
        mock_pm.return_value.launch.return_value = True
        report = orch.run()

    assert report["success"] is True
    assert Path(report["output_path"]).is_file()
    assert report["tasks"][0]["profile_used"] == "solo_profile"
    assert report["tasks"][1]["profile_used"] == "local_zero_credit_flipbook"
    assert report["tasks"][1]["credit_cost"] == 0


def test_build_scene_pairs_from_shots_continuity_and_pivot_math(tmp_path: Path) -> None:
    """Verify continuous shots share boundary frames (trim_first_frame=True) and scene pivots add 0.24s overlap."""
    shots = [
        {"shot_id": "S01", "continues_prev": False, "start_visual": "Scene A start", "end_visual": "Scene A mid", "subject_motion": "move 1"},
        {"shot_id": "S02", "continues_prev": True, "end_visual": "Scene A end", "subject_motion": "move 2"},
        {"shot_id": "S03", "continues_prev": False, "start_visual": "Scene B start", "end_visual": "Scene B end", "subject_motion": "move 3"},
    ]
    beats = [4.0, 5.0, 4.5]
    pairs = build_scene_pairs_from_shots("en-first-principles", shots, beats, tmp_path / "frames", xfade_pivot_sec=0.24)

    assert len(pairs) == 3
    # S01 -> S02 is continuous: S01 gets exact 4.0s (no xfade), S02 reuses S01_end.png and trims first frame
    assert pairs[0].target_duration == 4.0
    assert pairs[0].trim_first_frame is False
    assert pairs[0].end_based_on_start is True

    # S02 precedes new scene S03 -> gets 5.0 + 0.24 = 5.24s overlap budget!
    assert pairs[1].start_image_path == str((tmp_path / "frames/S01_end.png").resolve())
    assert pairs[1].trim_first_frame is True
    assert pairs[1].end_based_on_start is True
    assert pairs[1].target_duration == 5.24

    # S03 is final shot in new scene -> exact 4.5s, trim_first_frame=False
    assert pairs[2].trim_first_frame is False
    assert pairs[2].target_duration == 4.5


def test_clean_beluga_sparkle_unblends_corner_star_without_blur() -> None:
    """Verify exact inverse-alpha unblending removes a simulated BELUGA star on 9:16 and 16:9 frames."""
    from sys.flow_video.sparkle_unblend import (
        _ALPHA_9X16_16X9_B64,
        _decode_alpha_68,
        clean_beluga_sparkle_pil,
    )

    import numpy as np

    rng = np.random.default_rng(42)
    true_img = rng.integers(30, 180, size=(1376, 768, 3), dtype=np.uint8)
    alpha = _decode_alpha_68(_ALPHA_9X16_16X9_B64)
    stamped = true_img.astype(np.float64)
    y0, y1, x0, x1 = 1376 - 132, 1376 - 64, 768 - 132, 768 - 64
    stamped[y0:y1, x0:x1] = np.round((1.0 - alpha) * stamped[y0:y1, x0:x1] + 255.0 * alpha)
    obs_pil = Image.fromarray(np.clip(stamped, 0, 255).astype(np.uint8), mode="RGB")

    cleaned_pil = clean_beluga_sparkle_pil(obs_pil)
    cleaned_arr = np.array(cleaned_pil, dtype=np.float64)
    mae = float(np.abs(cleaned_arr - true_img.astype(np.float64)).mean())
    star_mae = float(np.abs(cleaned_arr[y0:y1, x0:x1] - true_img[y0:y1, x0:x1].astype(np.float64)).mean())
    assert mae < 0.05
    assert star_mae < 1.0


def test_clean_omni_video_sparkle_mp4_idempotent(tmp_path: Path) -> None:
    """Verify 720x1280 MP4 corner star unblending removes the video stamp and records idempotency."""
    import json
    from sys.flow_video.sparkle_unblend import (
        _decode_alpha_vid_56,
        clean_omni_video_sparkle_mp4,
    )

    import numpy as np

    frame = np.full((1280, 720, 3), 40, dtype=np.float64)
    alpha = _decode_alpha_vid_56()
    y0, y1, x0, x1 = 1280 - 148, 1280 - 92, 720 - 148, 720 - 92
    frame[y0:y1, x0:x1] = np.round((1.0 - alpha) * frame[y0:y1, x0:x1] + 255.0 * alpha)
    stamped_png = tmp_path / "stamped_720x1280.png"
    Image.fromarray(frame.astype(np.uint8)).save(stamped_png)

    clip_mp4 = tmp_path / "omni_clip.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-t", "0.25", "-r", "24",
            "-i", str(stamped_png), "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p",
            str(clip_mp4),
        ],
        check=True,
        capture_output=True,
    )

    assert clean_omni_video_sparkle_mp4(clip_mp4) is True
    # Second call must be a fast no-op due to sidecar idempotency flag
    assert clean_omni_video_sparkle_mp4(clip_mp4) is False
    sidecar = json.loads(clip_mp4.with_suffix(".json").read_text(encoding="utf-8"))
    assert sidecar["sparkle_unblended"] is True

    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(clip_mp4), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    )
    out_f = np.frombuffer(raw, dtype=np.uint8).reshape(1280, 720, 3)
    # Peak inside star zone was ~110 before unblending; must return close to 40 background
    assert int(out_f[y0:y1, x0:x1].max()) < 55


def test_v3_1_purges_hardcoded_props_and_honors_scene_anchor(tmp_path: Path) -> None:
    """Verify V3.1 formulas contain zero off-topic episodic props, honor scene_anchor, and use MarginV=270."""
    from tools.rebuild_en_from_competitor_frames import build_vn_kinetic_1word_ass_and_srt

    banned_props = (
        "olive-oil",
        "gyroscope",
        "green chalkboard",
        "banker's lamp",
        "tea bowl",
        "container vessel",
        "cobblestones",
    )
    for slug in EXPECTED_18_EN_CHANNELS:
        formula = EN_FLOW_VIDEO_FORMULAS[slug]
        combined = f"{formula['subject_physics']} {formula['continuity_anchor']}".lower()
        for prop in banned_props:
            assert prop not in combined, f"Found banned episodic prop '{prop}' in {slug}"

    mp = build_channel_motion_prompt(
        "en-first-principles",
        "skeletal wind craft races across salt flat",
        scene_anchor="vast twilight desert salt flat",
    )
    assert "vast twilight desert salt flat" in mp
    assert "gyroscope" not in mp.lower()

    kp = build_reference_keyframe_prompt(
        "en-wallet-anatomy",
        "black leather bill folder opens on walnut table",
        scene_anchor="candlelit walnut dining table",
    )
    assert "candlelit walnut dining table" in kp
    assert "olive-oil" not in kp.lower()

    ass_p = tmp_path / "test.ass"
    srt_p = tmp_path / "test.srt"
    build_vn_kinetic_1word_ass_and_srt(
        beats=[{"narration": "Hello world."}],
        beat_durations=[1.2],
        global_words=[
            {"word": "Hello", "start": 0.0, "end": 0.5, "beat_index": 0},
            {"word": "world.", "start": 0.55, "end": 1.0, "beat_index": 0},
        ],
        total_dur=1.2,
        ass_path=ass_p,
        srt_path=srt_p,
    )
    ass_txt = ass_p.read_text(encoding="utf-8")
    assert ",40,40,270,1" in ass_txt


def test_ensure_keyframes_parallel_dag_waves_and_dependencies(tmp_path: Path) -> None:
    """Verify _ensure_keyframes executes independent frames concurrently in DAG waves
    and strictly respects based_on and shared {prev}_end.png continuity dependencies.
    """
    frames_dir = tmp_path / "work/frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    sp1 = ScenePairSpec(
        id="S01",
        start_image_prompt="scene 1 start visual",
        end_image_prompt="scene 1 end visual",
        end_based_on_start=True,
    )
    sp2 = ScenePairSpec(
        id="S02",
        start_image_path=str((frames_dir / "S01_end.png").resolve()),
        start_image_prompt=None,
        end_image_prompt="scene 2 end visual",
        end_based_on_start=True,
        trim_first_frame=True,
    )
    sp3 = ScenePairSpec(
        id="S03",
        start_image_prompt="independent scene 3 start visual",
        end_image_prompt="independent scene 3 end visual",
        end_based_on_start=True,
    )

    spec = VideoChainSpec(
        job_id="test_dag_waves",
        mode=ChainMode.SCENE_PAIRS,
        scene_pairs=[sp1, sp2, sp3],
        duration_seconds=4,
    )

    orch = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work",
        max_workers=4,
        dry_run=False,
    )

    call_log: list[dict[str, Any]] = []

    async def fake_generate_image(
        prompt: str,
        dest_file: Path,
        reference_image_paths: list[str] | None = None,
        preferred_profile: Any = None,
    ) -> None:
        start_t = time.monotonic()
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        item_stem = dest_file.stem
        entry = {
            "item": item_stem,
            "start": start_t,
            "ref_paths": list(reference_image_paths or []),
            "prompt": prompt,
        }
        call_log.append(entry)
        await asyncio.sleep(0.08)
        dest_file.write_bytes(b"\x89PNG\r\n\x1a\nfake_image")
        dest_file.with_suffix(".json").write_text("{}", encoding="utf-8")
        entry["end"] = time.monotonic()

    with patch.object(orch, "_generate_single_image", side_effect=fake_generate_image):
        asyncio.run(orch._ensure_keyframes())

    generated_items = [c["item"] for c in call_log]
    assert len(generated_items) == 5
    assert "S02_start" not in generated_items
    assert set(generated_items) == {"S01_start", "S01_end", "S02_end", "S03_start", "S03_end"}

    assert Path(sp2.start_image_path).is_file()
    assert Path(sp2.start_image_path).name == "S01_end.png"

    log_by_item = {c["item"]: c for c in call_log}

    # Dependency check 1: S01_start must complete before S01_end starts
    assert log_by_item["S01_start"]["end"] <= log_by_item["S01_end"]["start"] + 0.05

    # Dependency check 2: S03_start must complete before S03_end starts
    assert log_by_item["S03_start"]["end"] <= log_by_item["S03_end"]["start"] + 0.05

    # Dependency check 3: S01_end must complete before S02_end starts
    assert log_by_item["S01_end"]["end"] <= log_by_item["S02_end"]["start"] + 0.05

    # Dependency check 4: S02_end must reference S01_end.png
    assert any("S01_end.png" in p for p in log_by_item["S02_end"]["ref_paths"])

    # Concurrency check: S01_start and S03_start ran concurrently in Wave 1
    assert abs(log_by_item["S01_start"]["start"] - log_by_item["S03_start"]["start"]) < 0.08

    # Wave execution is faster than sequential (3 waves * ~0.08s < 0.35s vs sequential 5 * 0.08s = 0.40s)
    span_dur = max(c["end"] for c in call_log) - min(c["start"] for c in call_log)
    sum_dur = sum(c["end"] - c["start"] for c in call_log)
    assert span_dur < sum_dur * 0.80


def test_warm_session_reuse_across_tasks_and_clean_teardown(tmp_path: Path) -> None:
    """Verify warm CDP session pooling reuses live sessions across multiple images/clips
    (launching Chrome only once per port) and performs clean teardown with 0 leaked processes/locks.
    """
    f0 = tmp_path / "frame0.png"
    f1 = tmp_path / "frame1.png"
    f2 = tmp_path / "frame2.png"
    for p in (f0, f1, f2):
        Image.new("RGB", (320, 180), color=(10, 50, 100)).save(p)

    kf0 = KeyframeSpec(id="k0", image_path=str(f0))
    kf1 = KeyframeSpec(id="k1", image_path=str(f1))
    kf2 = KeyframeSpec(id="k2", image_path=str(f2))

    spec = VideoChainSpec(
        job_id="test_warm_reuse",
        mode=ChainMode.DAISY_CHAIN,
        video_model="omni_flash",
        duration_seconds=4,
        auto_duration=False,
        keyframes=[kf0, kf1, kf2],
    )

    mock_profile = {"name": "warm_profile_1", "cdp_port": 9222}
    orch = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work",
        output_mp4_path=tmp_path / "out.mp4",
        max_workers=1,
        reuse_warm_sessions=True,
    )
    orch.credit_ledger = CreditLedger(path=tmp_path / "warm_credits.json")
    orch.credit_ledger.sync_balance("warm_profile_1", 200)

    connect_calls = 0
    close_calls = 0
    query_credit_calls = 0

    class TrackingSession:
        def __init__(self, profile_cfg: dict) -> None:
            self.profile_cfg = profile_cfg
            self.name = profile_cfg["name"]

        async def connect(self) -> None:
            nonlocal connect_calls
            connect_calls += 1

        async def close(self) -> None:
            nonlocal close_calls
            close_calls += 1

        async def query_credits(self) -> dict:
            nonlocal query_credit_calls
            query_credit_calls += 1
            return {"remaining": 200}

        async def generate_video_from_frames(self, **kwargs) -> None:
            out_p = Path(kwargs["output_mp4_path"])
            out_p.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "testsrc=duration=1:size=320x180:rate=30",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-preset",
                    "ultrafast",
                    str(out_p),
                ],
                check=True,
                capture_output=True,
            )

    with (
        patch("sys.flow_video.orchestrator.get_all_configured_profiles", return_value=[mock_profile]),
        patch("sys.flow_video.orchestrator.DirectCDPProfileSession", side_effect=TrackingSession),
        patch("sys.flow_video.orchestrator.ProfilePortLock") as mock_pl,
        patch("sys.flow_video.orchestrator.GlobalBrowserSlot") as mock_bs,
        patch("sys.flow_video.orchestrator.get_process_manager") as mock_pm,
    ):
        mock_pl.return_value.acquire.return_value = True
        mock_bs.return_value.acquire.return_value = True
        mock_pm.return_value.launch.return_value = True

        report = orch.run()

    assert report["success"] is True
    assert len(report["tasks"]) == 2

    assert mock_pm.return_value.launch.call_count == 1
    assert connect_calls == 1
    assert query_credit_calls == 1

    assert close_calls == 1
    assert mock_pm.return_value.terminate_by_port.call_count == 1
    assert len(orch._warm_sessions) == 0
    assert len(orch._launched_ports) == 0


def test_package_final_on_colab_t4_nvenc_purges_local_cpu(tmp_path: Path) -> None:
    """Verify live stitch_hybrid_scene_groups_and_package rejects local_cpu and dispatches strictly to Colab T4 NVENC."""
    import shutil
    from sys.tools.produce_en_flow_dynamic_demo import stitch_hybrid_scene_groups_and_package

    import pytest

    g0 = tmp_path / "sg0.mp4"
    g1 = tmp_path / "sg1.mp4"
    for g in (g0, g1):
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "testsrc=duration=1:size=320x180:rate=30",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                "ultrafast",
                str(g),
            ],
            check=True,
            capture_output=True,
        )

    audio_wav = tmp_path / "narration.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2:sample_rate=48000",
            "-c:a",
            "pcm_s16le",
            str(audio_wav),
        ],
        check=True,
        capture_output=True,
    )
    wm_png = tmp_path / "wm.png"
    Image.new("RGBA", (100, 100), color=(255, 0, 0, 200)).save(wm_png)
    ass_path = tmp_path / "sub.ass"
    ass_path.write_text("[Script Info]\nTitle: Test\n", encoding="utf-8")
    srt_path = tmp_path / "sub.srt"
    srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")

    out_nvenc = tmp_path / "final_nvenc.mp4"
    shots = [
        {"continues_prev": False, "narration": "a"},
        {"continues_prev": False, "narration": "b"},
    ]
    tasks = [
        VideoClipTask(clip_id="c0", index=0, start_frame_path="", output_mp4_path=str(g0), duration_seconds=1),
        VideoClipTask(clip_id="c1", index=1, start_frame_path="", output_mp4_path=str(g1), duration_seconds=1),
    ]

    # 1. Deviated local_cpu backend must be strictly rejected in live mode
    with pytest.raises(ValueError, match="local CPU rendering has been purged"):
        stitch_hybrid_scene_groups_and_package(
            channel_slug="en-test",
            aspect="16:9",
            shots=shots,
            tasks=tasks,
            beat_durations=[1.0, 1.0],
            audio_path=audio_wav,
            ass_path=ass_path,
            srt_path=srt_path,
            watermark_png=wm_png,
            out_mp4=out_nvenc,
            render_backend="local_cpu",
            dry_run=False,
        )

    # 2. Live mode dispatches strictly to package_final_on_colab_t4_nvenc
    def fake_colab_nvenc(**kwargs: Any) -> dict[str, Any]:
        shutil.copy2(g0, kwargs["out_mp4"])
        return {
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "duration": 2.0,
            "video_encoder": "colab_t4_h264_nvenc",
            "colab_account": "account-01",
            "colab_session": "vp-en-test",
        }

    with patch("sys.tools.produce_en_flow_dynamic_demo.package_final_on_colab_t4_nvenc", side_effect=fake_colab_nvenc) as mock_nv:
        meta = stitch_hybrid_scene_groups_and_package(
            channel_slug="en-test",
            aspect="16:9",
            shots=shots,
            tasks=tasks,
            beat_durations=[1.0, 1.0],
            audio_path=audio_wav,
            ass_path=ass_path,
            srt_path=srt_path,
            watermark_png=wm_png,
            out_mp4=out_nvenc,
            render_backend="colab_nvenc",
            dry_run=False,
        )
        assert mock_nv.call_count == 1
        assert meta["video_encoder"] == "colab_t4_h264_nvenc"
        assert out_nvenc.is_file()
        assert out_nvenc.with_suffix(".srt").is_file()


def test_v3_3_credit_ledger_cooldown_and_cross_process_isolation(tmp_path: Path) -> None:
    """Verify CreditLedger mark_cooldown prevents reuse of rate-limited profiles across waves and processes."""
    credits_file = tmp_path / "credits_cooldown_test.json"
    ledger1 = CreditLedger(path=credits_file)

    ledger1.register_profile("prof_active", initial_credits=1000)
    ledger1.register_profile("prof_limited", initial_credits=1000)
    ledger1.register_profile("prof_expired", initial_credits=1000)

    # Mark prof_limited on cooldown for 600s
    ledger1.mark_cooldown("prof_limited", seconds=600.0, reason="rate_limit_exceeded")
    # Mark prof_expired on cooldown in the past (already expired)
    ledger1.mark_cooldown("prof_expired", seconds=-10.0, reason="old_temporary_glitch")

    assert ledger1.is_on_cooldown("prof_limited") is True
    assert ledger1.is_on_cooldown("prof_active") is False
    assert ledger1.is_on_cooldown("prof_expired") is False

    # is_eligible must strictly reject profiles currently on cooldown
    assert ledger1.is_eligible("prof_limited", min_credits=7) is False
    assert ledger1.is_eligible("prof_active", min_credits=7) is True
    assert ledger1.is_eligible("prof_expired", min_credits=7) is True

    # Cross-process check: a second CreditLedger instance accessing the same file
    ledger2 = CreditLedger(path=credits_file)
    assert ledger2.is_on_cooldown("prof_limited") is True
    assert ledger2.is_eligible("prof_limited", min_credits=7) is False

    # Clear cooldown restores eligibility immediately across all processes
    ledger1.clear_cooldown("prof_limited")
    assert ledger1.is_on_cooldown("prof_limited") is False
    assert ledger2.is_on_cooldown("prof_limited") is False
    assert ledger2.is_eligible("prof_limited", min_credits=7) is True


def test_v3_3_credit_ledger_selection_untested_penalty_and_cooldown_filtering(tmp_path: Path) -> None:
    """Verify select_eligible_profiles filters cooldowns and prefers tested (last_used > 0) profiles."""
    credits_file = tmp_path / "credits_selection_test.json"
    ledger = CreditLedger(path=credits_file)

    ledger.register_profile("p_tested_low", initial_credits=50)
    ledger.register_profile("p_tested_high", initial_credits=80)
    ledger.register_profile("p_untested", initial_credits=100)
    ledger.register_profile("p_cooldown", initial_credits=1000)

    # Mark tested profiles as actually used before
    ledger.touch_used("p_tested_low")
    time.sleep(0.01)
    ledger.touch_used("p_tested_high")

    # Mark high-credit profile on cooldown
    ledger.mark_cooldown("p_cooldown", seconds=300.0, reason="429_quota")

    profiles_input = [
        {"id": "p_tested_low", "port": 9221},
        {"id": "p_tested_high", "port": 9222},
        {"id": "p_untested", "port": 9223},
        {"id": "p_cooldown", "port": 9224},
    ]

    selected = ledger.select_eligible_profiles(profiles_input, min_credits=7)
    selected_ids = [p["id"] for p in selected]

    # 1. p_cooldown is on cooldown and must be excluded completely
    assert "p_cooldown" not in selected_ids

    # 2. Tested profiles (untested_penalty=0) come before untested (untested_penalty=1),
    #    and among tested profiles, p_tested_high (80) precedes p_tested_low (50)
    assert selected_ids == ["p_tested_high", "p_tested_low", "p_untested"]

    # 3. pick_for_video_task must skip p_cooldown (1000 credits) and pick highest non-cooldown video profile
    picked_video = ledger.pick_for_video_task(profiles_input, cost=7)
    assert picked_video is not None
    assert picked_video["id"] == "p_untested"  # 100 credits > 80 credits, neither is on cooldown

    # 4. pick_for_image_task must skip p_cooldown if marked on cooldown
    picked_img = ledger.pick_for_image_task(profiles_input)
    assert picked_img is not None
    assert picked_img["id"] != "p_cooldown"

    # 5. touch_used and deduct_credits clear expired cooldown
    ledger.mark_cooldown("p_untested", seconds=-5.0, reason="expired_rate_limit")
    assert ledger.is_on_cooldown("p_untested") is False  # already expired
    ledger.touch_used("p_untested")
    entry = ledger.summary(["p_untested"])["profiles"]["p_untested"]
    assert entry["cooldown_until"] == 0.0
    assert entry["cooldown_reason"] is None




