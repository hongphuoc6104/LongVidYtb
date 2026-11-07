"""Unit tests for Flow Video chain planning, models, stitcher, and orchestrator."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from sys.flow_cdp.credit_ledger import CreditLedger
from sys.flow_video.chain_planner import (
    apply_prompt_guard,
    build_chain_plan,
    build_daisy_chain_tasks,
    build_flipbook_tasks,
    build_scene_pair_tasks,
    export_remotion_beats,
    select_clip_duration_and_credits,
)
from sys.flow_video.models import (
    ChainMode,
    KeyframeSpec,
    ScenePairSpec,
    VideoChainSpec,
    VideoClipTask,
)
from sys.flow_video.orchestrator import FlowVideoChainOrchestrator
from sys.flow_video.stitcher import (
    probe_video_clip,
    render_flipbook_segment,
    stitch_video_chain,
)
from typing import Any
from unittest.mock import patch

import pytest
from PIL import Image


def _generate_synthetic_clip(
    path: Path,
    duration: float = 1.0,
    width: int = 320,
    height: int = 180,
    fps: int = 30,
    with_audio: bool = False,
    audio_freq: int = 440,
) -> Path:
    """Helper to generate a lightweight synthetic video clip using ffmpeg."""
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"testsrc=duration={duration}:size={width}x{height}:rate={fps}",
    ]
    if with_audio:
        cmd.extend([
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency={audio_freq}:duration={duration}:sample_rate=48000",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "ultrafast",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
        ])
    else:
        cmd.extend([
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "ultrafast",
        ])
    cmd.append(str(path.resolve()))
    subprocess.run(cmd, check=True, capture_output=True)
    return path


def _generate_synthetic_wav(path: Path, duration: float = 2.0, sample_rate: int = 48000) -> Path:
    """Helper to generate a synthetic WAV audio file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency=440:duration={duration}:sample_rate={sample_rate}",
        "-c:a",
        "pcm_s16le",
        str(path.resolve()),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return path


def test_video_chain_spec_to_and_from_dict() -> None:
    """Verify VideoChainSpec serialization to dict and deserialization from dict."""
    kf = KeyframeSpec(
        id="kf_01",
        image_path="/path/to/frame1.png",
        image_prompt="Prompt 1",
        motion_prompt="Camera zooms in",
        based_on="base_01",
    )
    sp = ScenePairSpec(
        id="sp_01",
        start_image_path="/path/to/start.png",
        end_image_path="/path/to/end.png",
        start_image_prompt="Start prompt",
        end_image_prompt="End prompt",
        motion_prompt="Smooth morph",
        target_duration=3.5,
    )
    spec = VideoChainSpec(
        job_id="custom_job",
        mode=ChainMode.SCENE_PAIRS,
        aspect="9:16",
        video_model="veo_3_1_fast",
        duration_seconds=6,
        keyframes=[kf],
        scene_pairs=[sp],
        audio_path="/path/to/audio.wav",
        no_talking_prompt_guard=False,
        keep_veo_audio=True,
        veo_audio_mix_weight=0.45,
        target_fps=24,
        normalize_audio_lufs=False,
    )

    data = spec.to_dict()
    assert data["job_id"] == "custom_job"
    assert data["mode"] == "scene_pairs"
    assert data["aspect"] == "9:16"
    assert data["target_fps"] == 24
    assert data["keep_veo_audio"] is True
    assert data["veo_audio_mix_weight"] == 0.45
    assert len(data["keyframes"]) == 1
    assert len(data["scene_pairs"]) == 1
    assert data["scene_pairs"][0]["target_duration"] == 3.5

    # Reconstruct from dict
    reconstructed = VideoChainSpec.from_dict(data)
    assert reconstructed.job_id == spec.job_id
    assert reconstructed.mode == ChainMode.SCENE_PAIRS
    assert reconstructed.aspect == "9:16"
    assert reconstructed.video_model == "veo_3_1_fast"
    assert reconstructed.duration_seconds == 6
    assert reconstructed.target_fps == 24
    assert reconstructed.no_talking_prompt_guard is False
    assert reconstructed.keep_veo_audio is True
    assert reconstructed.veo_audio_mix_weight == 0.45
    assert reconstructed.normalize_audio_lufs is False
    assert len(reconstructed.keyframes) == 1
    assert reconstructed.keyframes[0].id == "kf_01"
    assert reconstructed.keyframes[0].based_on == "base_01"
    assert len(reconstructed.scene_pairs) == 1
    assert reconstructed.scene_pairs[0].target_duration == 3.5

    # Test defaults
    default_spec = VideoChainSpec()
    assert default_spec.keep_veo_audio is False
    assert default_spec.veo_audio_mix_weight == 0.45

    # Test invalid mode fallback to DAISY_CHAIN
    invalid_data = {"mode": "unknown_mode_string"}
    fallback_spec = VideoChainSpec.from_dict(invalid_data)
    assert fallback_spec.mode == ChainMode.DAISY_CHAIN


def test_video_chain_spec_to_and_from_json_file(tmp_path: Path) -> None:
    """Verify VideoChainSpec persistence to and from JSON files."""
    json_path = tmp_path / "spec_test.json"
    kf = KeyframeSpec(id="kf_001", image_path=str(tmp_path / "frame.png"), motion_prompt="Pan left")
    spec = VideoChainSpec(job_id="json_job", keyframes=[kf])

    spec.to_json_file(json_path)
    assert json_path.is_file()

    loaded = VideoChainSpec.from_json_file(json_path)
    assert loaded.job_id == "json_job"
    assert len(loaded.keyframes) == 1
    assert loaded.keyframes[0].id == "kf_001"
    assert loaded.keyframes[0].motion_prompt == "Pan left"


def test_video_chain_spec_from_directory_natural_sorting_and_modes(tmp_path: Path) -> None:
    """Verify from_directory performs natural sorting on filenames and handles modes."""
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()

    # Create dummy image files in non-lexicographical order
    # Natural sort order must be: frame_1, frame_2, frame_10
    (frames_dir / "frame_10.png").write_bytes(b"img10")
    (frames_dir / "frame_2.png").write_bytes(b"img2")
    (frames_dir / "frame_1.png").write_bytes(b"img1")
    (frames_dir / "notes.txt").write_bytes(b"not an image")
    (frames_dir / ".hidden.png").write_bytes(b"hidden")

    # DAISY_CHAIN mode
    spec_daisy = VideoChainSpec.from_directory(
        frames_dir,
        motion_prompt="camera moves forward",
        mode=ChainMode.DAISY_CHAIN,
        duration_seconds=5,
    )
    assert spec_daisy.mode == ChainMode.DAISY_CHAIN
    assert len(spec_daisy.keyframes) == 3
    # Check natural sorting
    assert "frame_1.png" in str(spec_daisy.keyframes[0].image_path)
    assert "frame_2.png" in str(spec_daisy.keyframes[1].image_path)
    assert "frame_10.png" in str(spec_daisy.keyframes[2].image_path)

    # SCENE_PAIRS mode
    spec_pairs = VideoChainSpec.from_directory(
        frames_dir,
        motion_prompt="transition",
        mode=ChainMode.SCENE_PAIRS,
        duration_seconds=4,
    )
    assert spec_pairs.mode == ChainMode.SCENE_PAIRS
    assert len(spec_pairs.scene_pairs) == 2
    assert "frame_1.png" in str(spec_pairs.scene_pairs[0].start_image_path)
    assert "frame_2.png" in str(spec_pairs.scene_pairs[0].end_image_path)
    assert "frame_2.png" in str(spec_pairs.scene_pairs[1].start_image_path)
    assert "frame_10.png" in str(spec_pairs.scene_pairs[1].end_image_path)
    assert spec_pairs.scene_pairs[0].target_duration == 4.0

    # Error cases
    with pytest.raises(FileNotFoundError):
        VideoChainSpec.from_directory(tmp_path / "non_existent_dir")

    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    (empty_dir / "single.png").write_bytes(b"only_one")
    with pytest.raises(ValueError):
        VideoChainSpec.from_directory(empty_dir)


def test_apply_prompt_guard() -> None:
    """Verify prompt guard appends anti-lip-movement directives and is idempotent."""
    # When enabled and missing directives
    res1 = apply_prompt_guard("cinematic drone shot", guard_enabled=True)
    assert "cinematic drone shot" in res1
    assert "no talking, no lip movement" in res1

    # When disabled
    res2 = apply_prompt_guard("cinematic drone shot", guard_enabled=False)
    assert res2 == "cinematic drone shot"

    # When already containing talking keywords
    res3 = apply_prompt_guard("character standing, no talking allowed", guard_enabled=True)
    assert res3 == "character standing, no talking allowed"

    # Empty prompt with guard enabled
    res4 = apply_prompt_guard("", guard_enabled=True)
    assert "no talking" in res4
    assert not res4.startswith(",")


def test_build_daisy_chain_tasks(tmp_path: Path) -> None:
    """Verify build_daisy_chain_tasks sets trim_first_frame=False on clip 0 and True on >= 1."""
    kfs = [
        KeyframeSpec(id="f0", image_path="/path/0.png", motion_prompt="first move"),
        KeyframeSpec(id="f1", image_path="/path/1.png", motion_prompt="second move"),
        KeyframeSpec(id="f2", image_path="/path/2.png", motion_prompt="third move"),
    ]

    tasks = build_daisy_chain_tasks(
        keyframes=kfs,
        work_dir=tmp_path,
        aspect="16:9",
        duration_seconds=5,
        no_talking_prompt_guard=True,
    )
    assert len(tasks) == 2

    # Clip 0 preserves first frame
    assert tasks[0].index == 0
    assert tasks[0].trim_first_frame is False
    assert "no talking" in tasks[0].motion_prompt
    assert tasks[0].start_frame_path == "/path/0.png"
    assert tasks[0].end_frame_path == "/path/1.png"

    # Clip 1 trims first frame to avoid duplication at boundary
    assert tasks[1].index == 1
    assert tasks[1].trim_first_frame is True
    assert tasks[1].start_frame_path == "/path/1.png"
    assert tasks[1].end_frame_path == "/path/2.png"

    # Error case with fewer than 2 keyframes
    with pytest.raises(ValueError):
        build_daisy_chain_tasks(keyframes=[kfs[0]], work_dir=tmp_path)


def test_build_scene_pair_tasks_and_validation(tmp_path: Path) -> None:
    """Verify build_scene_pair_tasks sets trim_first_frame=False and retains target_duration."""
    sps = [
        ScenePairSpec(id="p1", start_image_path="/a.png", end_image_path="/b.png", target_duration=4.2),
        ScenePairSpec(id="p2", start_image_path="/b.png", end_image_path="/c.png", target_duration=2.8),
    ]

    tasks = build_scene_pair_tasks(
        scene_pairs=sps,
        work_dir=tmp_path,
        duration_seconds=5,
        no_talking_prompt_guard=False,
    )
    assert len(tasks) == 2
    assert tasks[0].trim_first_frame is False
    assert tasks[0].target_duration == 4.2
    assert tasks[1].trim_first_frame is False
    assert tasks[1].target_duration == 2.8

    # Error case with empty list
    with pytest.raises(ValueError):
        build_scene_pair_tasks(scene_pairs=[], work_dir=tmp_path)


def test_export_remotion_beats() -> None:
    """Verify export_remotion_beats produces valid Remotion scene metadata."""
    t0 = VideoClipTask(
        clip_id="c0",
        index=0,
        start_frame_path="/f0.png",
        output_mp4_path="/out0.mp4",
        duration_seconds=5,
        target_duration=4.5,
        trim_first_frame=False,
    )
    t1 = VideoClipTask(
        clip_id="c1",
        index=1,
        start_frame_path="/f1.png",
        output_mp4_path="/out1.mp4",
        duration_seconds=5,
        target_duration=5.0,
        trim_first_frame=True,
    )

    beats = export_remotion_beats([t0, t1], mode=ChainMode.DAISY_CHAIN, fps=30)
    assert len(beats) == 2

    # Check kind contract
    assert beats[0]["kind"] == "scene"
    assert beats[1]["kind"] == "scene"

    # Check trim_before contract
    assert beats[0]["trim_before"] == 0
    assert beats[1]["trim_before"] == 1

    # Check playback_rate calculation (t0: raw 5.0 / target 4.5 = 1.111, within 0.7-1.35)
    assert beats[0]["playback_rate"] == 1.111
    assert beats[0]["duration_seconds"] == 4.5
    assert beats[0]["duration_frames"] == int(round(4.5 * 30))

    # Check clip 1 playback rate
    assert beats[1]["duration_seconds"] == 5.0


def test_probe_video_clip_valid_and_invalid(tmp_path: Path) -> None:
    """Verify probe_video_clip extracts video stream metadata and raises on bad files."""
    valid_mp4 = _generate_synthetic_clip(tmp_path / "valid.mp4", duration=1.0, width=320, height=180, fps=30)
    meta = probe_video_clip(valid_mp4)

    assert meta["width"] == 320
    assert meta["height"] == 180
    assert meta["fps"] == 30.0
    assert meta["nb_frames"] == 30
    assert meta["duration"] >= 0.9
    assert meta["codec_name"] == "h264"
    assert meta["has_audio"] is False

    # Non-existent file
    with pytest.raises(ValueError, match="does not exist"):
        probe_video_clip(tmp_path / "does_not_exist.mp4")

    # Empty 0-byte file
    empty_file = tmp_path / "empty.mp4"
    empty_file.touch()
    with pytest.raises(ValueError, match="empty"):
        probe_video_clip(empty_file)


def test_stitch_video_chain_daisy_chain_trims_boundary_frames(tmp_path: Path) -> None:
    """Verify DAISY_CHAIN stitching trims 1 frame per join (3 clips x 30 frames -> 88 frames)."""
    clip_paths = [
        _generate_synthetic_clip(tmp_path / f"clip_{i}.mp4", duration=1.0, width=320, height=180, fps=30)
        for i in range(3)
    ]
    tasks = [
        VideoClipTask(
            clip_id=f"clip_{i}",
            index=i,
            start_frame_path="",
            output_mp4_path=str(clip_paths[i]),
            duration_seconds=1,
            trim_first_frame=(i > 0),
        )
        for i in range(3)
    ]

    out_mp4 = tmp_path / "daisy_stitched.mp4"
    res = stitch_video_chain(
        clips=tasks,
        output_mp4_path=out_mp4,
        mode=ChainMode.DAISY_CHAIN,
        aspect="16:9",
        fps=30,
    )

    assert Path(res["output_path"]).is_file()
    assert res["nb_clips"] == 3
    assert res["width"] == 1920
    assert res["height"] == 1080

    probe = probe_video_clip(out_mp4)
    # 30 frames on clip 0 + 29 on clip 1 + 29 on clip 2 = 88 frames
    assert probe["nb_frames"] == 88


def test_stitch_video_chain_scene_pairs_pacing(tmp_path: Path) -> None:
    """Verify SCENE_PAIRS mode applies tpad freeze for hold and setpts for stretch."""
    c0 = _generate_synthetic_clip(tmp_path / "p_hold.mp4", duration=1.0, width=320, height=180, fps=30)
    c1 = _generate_synthetic_clip(tmp_path / "p_stretch.mp4", duration=1.0, width=320, height=180, fps=30)

    # c0 has raw 1.0s, target 2.0s -> target > raw * 1.35 -> tpad freeze
    # c1 has raw 1.0s, target 1.1s -> 0.7 <= ratio <= 1.35 -> setpts time-stretch
    clips = [
        {"src": str(c0), "target_duration": 2.0, "trim_first_frame": False},
        {"src": str(c1), "target_duration": 1.1, "trim_first_frame": False},
    ]

    out_mp4 = tmp_path / "scene_pairs_stitched.mp4"
    res = stitch_video_chain(
        clips=clips,
        output_mp4_path=out_mp4,
        mode=ChainMode.SCENE_PAIRS,
        aspect="16:9",
        fps=30,
    )

    probe = probe_video_clip(out_mp4)
    assert probe["width"] == 1920
    assert probe["height"] == 1080
    # Expected total duration: ~2.0 + 1.1 = ~3.1 seconds
    assert probe["duration"] >= 3.0
    assert res["nb_clips"] == 2


def test_stitch_video_chain_external_audio_muxing(tmp_path: Path) -> None:
    """Verify external WAV voiceover muxing produces valid h264 + aac output."""
    clip = _generate_synthetic_clip(tmp_path / "vid.mp4", duration=2.0, width=320, height=180, fps=30)
    audio = _generate_synthetic_wav(tmp_path / "narration.wav", duration=2.0)

    out_mp4 = tmp_path / "muxed_output.mp4"
    res = stitch_video_chain(
        clips=[str(clip)],
        output_mp4_path=out_mp4,
        audio_path=audio,
        normalize_audio_lufs=True,
        aspect="16:9",
        fps=30,
    )

    probe = probe_video_clip(out_mp4)
    assert probe["has_audio"] is True
    assert probe["audio_codec"] == "aac"
    assert probe["codec_name"] == "h264"
    assert res["has_audio"] is True


def test_stitch_video_chain_pads_video_when_audio_longer(tmp_path: Path) -> None:
    """Verify that if total video is shorter than external audio, stitch_video_chain pads final frame instead of cutting audio."""
    clip = _generate_synthetic_clip(tmp_path / "short_vid.mp4", duration=1.0, width=320, height=180, fps=30)
    audio = _generate_synthetic_wav(tmp_path / "long_audio.wav", duration=2.5)

    out_mp4 = tmp_path / "padded_output.mp4"
    res = stitch_video_chain(
        clips=[str(clip)],
        output_mp4_path=out_mp4,
        audio_path=audio,
        normalize_audio_lufs=True,
        aspect="16:9",
        fps=30,
    )

    probe = probe_video_clip(out_mp4)
    assert probe["has_audio"] is True
    assert probe["duration"] >= 2.4
    assert res["duration"] >= 2.4


def test_stitch_video_chain_mixes_native_audio_and_voiceover(tmp_path: Path) -> None:
    """Verify that when clips contain native audio and external voiceover is passed with keep_veo_audio=True,
    stitch_video_chain mixes both native audio and external voiceover into the final MP4.
    """
    clip1 = _generate_synthetic_clip(
        tmp_path / "clip1.mp4", duration=1.5, width=320, height=180, fps=30, with_audio=True, audio_freq=440
    )
    clip2 = _generate_synthetic_clip(
        tmp_path / "clip2.mp4", duration=1.5, width=320, height=180, fps=30, with_audio=True, audio_freq=880
    )
    voiceover = _generate_synthetic_wav(tmp_path / "voiceover.wav", duration=3.0)

    out_mp4 = tmp_path / "mixed_final.mp4"
    res = stitch_video_chain(
        clips=[str(clip1), str(clip2)],
        output_mp4_path=out_mp4,
        audio_path=voiceover,
        keep_veo_audio=True,
        veo_audio_mix_weight=0.45,
        normalize_audio_lufs=True,
        aspect="16:9",
        fps=30,
    )

    probe = probe_video_clip(out_mp4)
    assert probe["has_audio"] is True
    assert probe["audio_codec"] == "aac"
    assert probe["codec_name"] == "h264"
    assert probe["duration"] > 2.5
    assert res["has_audio"] is True
    assert res["nb_clips"] == 2


def test_orchestrator_dry_run_execution(tmp_path: Path) -> None:
    """Verify FlowVideoChainOrchestrator in dry_run mode generates mock pipeline artifacts."""
    kf0 = KeyframeSpec(id="dry_kf0", image_prompt="stickman walking")
    kf1 = KeyframeSpec(id="dry_kf1", image_prompt="stickman stopping")
    spec = VideoChainSpec(job_id="test_dry_job", keyframes=[kf0, kf1], duration_seconds=1)

    work_dir = tmp_path / "dry_run_work"
    out_mp4 = tmp_path / "dry_final.mp4"

    orchestrator = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=work_dir,
        output_mp4_path=out_mp4,
        dry_run=True,
    )
    # Ensure test credit ledger points to isolated tmp path
    orchestrator.credit_ledger = CreditLedger(path=tmp_path / "dry_credits.json")

    report = orchestrator.run()
    assert report["success"] is True
    assert report["dry_run"] is True
    assert Path(report["output_path"]).is_file()
    assert Path(report["manifest_file"]).is_file()
    assert Path(report["remotion_beats_file"]).is_file()

    # Verify manifest
    manifest_data = json.loads(Path(report["manifest_file"]).read_text(encoding="utf-8"))
    assert manifest_data["job_id"] == "test_dry_job"
    assert len(manifest_data["tasks"]) == 1
    assert manifest_data["tasks"][0]["status"] == "completed"


class FakeDirectCDPSession:
    """Isolated CDP session mock for unit tests that does NOT open Chrome."""

    def __init__(self, profile_cfg: dict[str, Any]):
        self.profile_cfg = profile_cfg
        self.name = profile_cfg.get("name", "mock_profile")

    async def connect(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def query_credits(self) -> dict[str, Any]:
        # Return 5 for profile_poor to trigger credit rotation
        if "poor" in self.name:
            return {"remaining": 5}
        return {"remaining": 100}

    async def generate_video_from_frames(self, **kwargs: Any) -> None:
        out_path = Path(kwargs["output_mp4_path"])
        _generate_synthetic_clip(out_path, duration=1.0, width=320, height=180, fps=30)


def test_orchestrator_credit_rotation_and_isolated_execution(tmp_path: Path) -> None:
    """Verify orchestrator rotates away from profile with < 10 credits and uses eligible profile."""
    # Create two dummy keyframe images
    f0 = tmp_path / "kf0.png"
    f1 = tmp_path / "kf1.png"
    f0.write_bytes(b"\x89PNG\r\n\x1a\nfake1")
    f1.write_bytes(b"\x89PNG\r\n\x1a\nfake2")

    kf0 = KeyframeSpec(id="kf0", image_path=str(f0), motion_prompt="zoom")
    kf1 = KeyframeSpec(id="kf1", image_path=str(f1), motion_prompt="pan")
    spec = VideoChainSpec(job_id="test_credit_rot", keyframes=[kf0, kf1], duration_seconds=6)

    work_dir = tmp_path / "rot_work"
    out_mp4 = tmp_path / "rot_final.mp4"

    mock_profiles = [
        {"name": "mock_profile_poor", "cdp_port": 9222},
        {"name": "mock_profile_rich", "cdp_port": 9223},
    ]

    orchestrator = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=work_dir,
        output_mp4_path=out_mp4,
        dry_run=False,
    )
    test_ledger = CreditLedger(path=tmp_path / "rot_credits.json")
    orchestrator.credit_ledger = test_ledger

    # Mock locks, process manager, and profile session
    with (
        patch("sys.flow_video.orchestrator.get_all_configured_profiles", return_value=mock_profiles),
        patch("sys.flow_video.orchestrator.DirectCDPProfileSession", side_effect=FakeDirectCDPSession),
        patch("sys.flow_video.orchestrator.ProfilePortLock") as mock_port_lock,
        patch("sys.flow_video.orchestrator.GlobalBrowserSlot") as mock_slot,
        patch("sys.flow_video.orchestrator.get_process_manager") as mock_pm,
    ):
        mock_port_lock.return_value.acquire.return_value = True
        mock_slot.return_value.acquire.return_value = True
        mock_pm.return_value.launch.return_value = True

        report = orchestrator.run()

    assert report["success"] is True
    # mock_profile_poor should be marked exhausted due to 5 < 18 credits
    assert test_ledger.is_eligible("mock_profile_poor", min_credits=18) is False
    poor_summary = test_ledger.summary(["mock_profile_poor"])["profiles"]["mock_profile_poor"]
    assert poor_summary["status"] == "exhausted"

    # mock_profile_rich should be used and had 18 credits deducted (Omni 1.2 Flash 6s)
    assert "mock_profile_rich" in report["profiles_used"]
    assert report["credits_deducted"]["mock_profile_rich"] == 18
    rich_summary = test_ledger.summary(["mock_profile_rich"])["profiles"]["mock_profile_rich"]
    assert rich_summary["credits_remaining"] == 82


def test_flow_model_resolution_and_catalog_durations() -> None:
    """Verify flow_rpc model catalogs, nicknames, aspect ratios, and exact durations."""
    from sys.flow_cdp import flow_rpc

    # 1. Nickname resolution for Veo 3.1 Fast
    assert (
        flow_rpc.resolve_video_model("veo_3_1_fast", aspect="16:9", has_start_frame=True, has_end_frame=True)
        == "veo_3_1_i2v_s_fast_fl"
    )
    assert (
        flow_rpc.resolve_video_model("veo_3_1_fast", aspect="9:16", has_start_frame=True, has_end_frame=True)
        == "veo_3_1_i2v_s_fast_portrait_fl"
    )
    assert (
        flow_rpc.resolve_video_model("veo_3_1_fast", aspect="16:9", has_start_frame=True, has_end_frame=False)
        == "veo_3_1_i2v_s_fast"
    )

    # 2. Duration-specific resolution (4s, 6s)
    assert (
        flow_rpc.resolve_video_model("veo_3_1_fast", duration_seconds=4, has_start_frame=True, has_end_frame=True)
        == "veo_3_1_i2v_s_fast_4s_fl"
    )
    assert (
        flow_rpc.resolve_video_model("veo_3_1_fast", duration_seconds=6, has_start_frame=True, has_end_frame=True)
        == "veo_3_1_i2v_s_fast_6s_fl"
    )

    # 3. Veo 3.1 Lite and Omni Flash resolution
    assert (
        flow_rpc.resolve_video_model("veo_3_1_lite", has_start_frame=True, has_end_frame=True)
        == "veo_3_1_interpolation_lite"
    )
    assert (
        flow_rpc.resolve_video_model("omni_flash", has_start_frame=True, has_end_frame=True)
        == "macaron_cookie_i2v_fl_8s"
    )
    assert (
        flow_rpc.resolve_video_model("omni_flash", duration_seconds=10, has_start_frame=True, has_end_frame=False)
        == "macaron_cookie_i2v_10s"
    )
    assert (
        flow_rpc.resolve_video_model("omni_1_1_flash", has_start_frame=True, has_end_frame=True)
        == "omni_flash_i2v_8s_first_last"
    )
    assert (
        flow_rpc.resolve_video_model("abra", duration_seconds=10, has_start_frame=True, has_end_frame=False)
        == "abra_i2v_10s"
    )

    # 4. Image model nicknames
    assert flow_rpc.IMAGE_MODEL_BY_NICKNAME["NANO_BANANA_PRO"] == "GEM_PIX_2"
    assert flow_rpc.IMAGE_MODEL_BY_NICKNAME["NANO_BANANA_2_1"] == "BELUGA"
    assert flow_rpc.IMAGE_MODEL_BY_NICKNAME["HARBOR_SEAL"] == "HARBOR_SEAL"

    # 5. Catalog parsing and duration extraction
    mock_payload = [
        [
            None,
            None,
            None,
            None,
            # Field 5 (index 4) = Video families
            [
                [
                    "Veo 3.1 - Fast",
                    [
                        [
                            "veo_3_1_i2v_s_fast_fl",
                            None,
                            None,
                            None,
                            [[1, [[None, 20]]], [2, [[None, 20]]]],
                            None,
                            None,
                            [[[[1, 5, 7]]]],
                            None,
                            None,
                            None,
                            None,
                            [[2, 1]],
                            None,
                            None,
                            None,
                            8,
                        ],
                        [
                            "veo_3_1_i2v_s_fast_4s_fl",
                            None,
                            None,
                            None,
                            [[3, [[None, 10]]]],
                            None,
                            None,
                            [[[[1, 5, 7]]]],
                            None,
                            None,
                            None,
                            None,
                            [[2, 1]],
                            None,
                            None,
                            None,
                            4,
                        ],
                    ],
                    None,
                    "veo_3_1_fast",
                ]
            ],
            # Field 6 (index 5) = Image families
            [
                [
                    "🍌 Nano Banana Pro",
                    [["GEM_PIX_2", None, None, None, [[1, [[None, 0]]]]]],
                    None,
                    "nano_banana_pro",
                ]
            ],
        ]
    ]

    video_cat = flow_rpc.read_model_catalog(mock_payload)
    assert len(video_cat) == 1
    assert video_cat[0]["id"] == "veo_3_1_fast"
    assert len(video_cat[0]["usages"]) == 2
    assert video_cat[0]["usages"][0]["duration"] == 8
    assert video_cat[0]["usages"][0]["credits"] == {1: 20, 2: 20}
    assert video_cat[0]["usages"][1]["duration"] == 4
    assert video_cat[0]["usages"][1]["credits"] == {3: 10}

    # Resolution using catalog
    res_8s = flow_rpc.resolve_video_model(
        "veo_3_1_fast", aspect="16:9", has_start_frame=True, has_end_frame=True, catalog=video_cat, duration_seconds=8
    )
    assert res_8s == "veo_3_1_i2v_s_fast_fl"

    res_4s = flow_rpc.resolve_video_model(
        "veo_3_1_fast", aspect="16:9", has_start_frame=True, has_end_frame=True, catalog=video_cat, duration_seconds=4
    )
    assert res_4s == "veo_3_1_i2v_s_fast_4s_fl"

    image_cat = flow_rpc.read_image_model_catalog(mock_payload)
    assert len(image_cat) == 1
    assert image_cat[0]["id"] == "nano_banana_pro"
    assert image_cat[0]["usages"][0]["key"] == "GEM_PIX_2"
    assert image_cat[0]["usages"][0]["credits"] == {1: 0}


def test_omni_flash_auto_duration_and_credit_selection() -> None:
    """Verify Omni 1.2 Flash defaults, 4s/6s/8s/10s auto-duration, credits (12/18/24/30), legacy 1.1 fallback, and chain planning."""
    from sys.flow_cdp import flow_rpc
    from sys.flow_video.chain_planner import (
        build_chain_plan,
        build_daisy_chain_specs,
        build_daisy_chain_tasks,
        build_scene_pair_specs,
        build_scene_pair_tasks,
        select_clip_duration_and_credits,
    )
    from sys.flow_video.models import (
        FlowVideoChainSpec,
        KeyframeSpec,
        ScenePairSpec,
        VideoChainSpec,
        VideoClipSpec,
        VideoClipTask,
    )

    # 1. Models and Aliases
    assert FlowVideoChainSpec is VideoChainSpec
    assert VideoClipSpec is VideoClipTask
    assert build_daisy_chain_specs is build_daisy_chain_tasks
    assert build_scene_pair_specs is build_scene_pair_tasks

    # KeyframeSpec instantiation
    kf_test = KeyframeSpec(id="kf_test", image_path="/path/test.png")
    assert kf_test.id == "kf_test"

    default_spec = FlowVideoChainSpec()
    assert default_spec.video_model == "omni_flash"
    assert default_spec.auto_duration is True

    default_clip = VideoClipSpec(
        clip_id="c_test",
        index=0,
        start_frame_path="/frame0.png",
    )
    assert default_clip.credit_cost == 18
    assert default_clip.duration_sec == float(default_clip.duration_seconds)
    default_clip.duration_sec = 8.0
    assert default_clip.duration_seconds == 8

    # 2. flow_rpc resolution for Omni 1.2 Flash across 16:9 and 9:16
    for dur, expected_fl in [
        (4, "macaron_cookie_i2v_fl_4s"),
        (6, "macaron_cookie_i2v_fl_6s"),
        (8, "macaron_cookie_i2v_fl_8s"),
        (10, "macaron_cookie_i2v_fl_10s"),
    ]:
        # 16:9 Landscape
        res_fl_16x9 = flow_rpc.resolve_video_model(
            "omni_flash", aspect="16:9", duration_seconds=dur, has_start_frame=True, has_end_frame=True
        )
        assert res_fl_16x9 == expected_fl
        # 9:16 Portrait (universal aspect in Omni 1.2 Flash)
        res_fl_9x16 = flow_rpc.resolve_video_model(
            "omni_flash", aspect="9:16", duration_seconds=dur, has_start_frame=True, has_end_frame=True
        )
        assert res_fl_9x16 == expected_fl

    for dur, expected_sf in [
        (4, "macaron_cookie_i2v_4s"),
        (6, "macaron_cookie_i2v_6s"),
        (8, "macaron_cookie_i2v_8s"),
        (10, "macaron_cookie_i2v_10s"),
    ]:
        res_sf_16x9 = flow_rpc.resolve_video_model(
            "omni_flash", aspect="16:9", duration_seconds=dur, has_start_frame=True, has_end_frame=False
        )
        assert res_sf_16x9 == expected_sf
        res_sf_9x16 = flow_rpc.resolve_video_model(
            "omni_flash", aspect="9:16", duration_seconds=dur, has_start_frame=True, has_end_frame=False
        )
        assert res_sf_9x16 == expected_sf

    # Omni 1.1 Flash / Abra legacy resolution
    for dur, expected_abra in [
        (4, "abra_i2v_4s"),
        (6, "abra_i2v_6s"),
        (8, "abra_i2v_8s"),
        (10, "abra_i2v_10s"),
    ]:
        res_sf_16x9 = flow_rpc.resolve_video_model(
            "abra", aspect="16:9", duration_seconds=dur, has_start_frame=True, has_end_frame=False
        )
        assert res_sf_16x9 == expected_abra
        res_sf_9x16 = flow_rpc.resolve_video_model(
            "abra", aspect="9:16", duration_seconds=dur, has_start_frame=True, has_end_frame=False
        )
        assert res_sf_9x16 == expected_abra

    for dur, expected_11_fl in [
        (4, "omni_flash_i2v_4s_first_last"),
        (6, "omni_flash_i2v_6s_first_last"),
        (8, "omni_flash_i2v_8s_first_last"),
        (10, "omni_flash_i2v_8s_first_last"),
    ]:
        res_11_fl = flow_rpc.resolve_video_model(
            "omni_1_1_flash", aspect="16:9", duration_seconds=dur, has_start_frame=True, has_end_frame=True
        )
        assert res_11_fl == expected_11_fl

    # 3. select_clip_duration_and_credits tests
    # Omni 1.2 Flash auto-duration with start_end_frames
    assert select_clip_duration_and_credits(3.0, "omni_flash", has_end_frame=True, auto_duration=True) == (4, 12)
    assert select_clip_duration_and_credits(4.8, "omni_flash", has_end_frame=True, auto_duration=True) == (4, 12)
    assert select_clip_duration_and_credits(5.0, "omni_flash", has_end_frame=True, auto_duration=True) == (6, 18)
    assert select_clip_duration_and_credits(6.8, "omni_flash", has_end_frame=True, auto_duration=True) == (6, 18)
    assert select_clip_duration_and_credits(7.2, "omni_flash", has_end_frame=True, auto_duration=True) == (8, 24)
    assert select_clip_duration_and_credits(9.5, "omni_flash", has_end_frame=True, auto_duration=True) == (10, 30)

    # Omni 1.2 Flash auto-duration with start_frame
    assert select_clip_duration_and_credits(3.0, "omni_flash", has_end_frame=False, auto_duration=True) == (4, 12)
    assert select_clip_duration_and_credits(6.0, "omni_flash", has_end_frame=False, auto_duration=True) == (6, 18)
    assert select_clip_duration_and_credits(8.0, "omni_flash", has_end_frame=False, auto_duration=True) == (8, 24)
    assert select_clip_duration_and_credits(9.5, "omni_flash", has_end_frame=False, auto_duration=True) == (10, 30)

    # Fixed duration (auto_duration=False)
    assert select_clip_duration_and_credits(9.5, "omni_flash", has_end_frame=True, default_duration_sec=6, auto_duration=False) == (6, 18)
    assert select_clip_duration_and_credits(9.5, "omni_flash", has_end_frame=True, default_duration_sec=4, auto_duration=False) == (4, 12)
    assert select_clip_duration_and_credits(9.5, "omni_flash", has_end_frame=True, default_duration_sec=8, auto_duration=False) == (8, 24)
    assert select_clip_duration_and_credits(9.5, "omni_flash", has_end_frame=True, default_duration_sec=10, auto_duration=False) == (10, 30)
    assert select_clip_duration_and_credits(9.5, "omni_flash", has_end_frame=False, default_duration_sec=10, auto_duration=False) == (10, 30)

    # Legacy abra / omni_1_1_flash auto-duration
    assert select_clip_duration_and_credits(3.0, "abra", has_end_frame=True, auto_duration=True) == (4, 7)
    assert select_clip_duration_and_credits(5.0, "omni_1_1_flash", has_end_frame=True, auto_duration=True) == (6, 10)
    assert select_clip_duration_and_credits(7.2, "abra", has_end_frame=True, auto_duration=True) == (8, 12)
    assert select_clip_duration_and_credits(9.5, "abra", has_end_frame=False, auto_duration=True) == (10, 15)

    # Veo models
    assert select_clip_duration_and_credits(5.0, "veo_3_1_lite", has_end_frame=True) == (8, 10)
    assert select_clip_duration_and_credits(5.0, "veo_3_1_fast", has_end_frame=True) == (8, 20)
    assert select_clip_duration_and_credits(5.0, "veo_3_1_quality", has_end_frame=True) == (8, 100)

    # 4. build_chain_plan total_credit_cost calculation
    sps = [
        ScenePairSpec(id="p1", start_image_path="/a.png", end_image_path="/b.png", target_duration=3.5),  # 4s -> 12 credits
        ScenePairSpec(id="p2", start_image_path="/b.png", end_image_path="/c.png", target_duration=5.5),  # 6s -> 18 credits
        ScenePairSpec(id="p3", start_image_path="/c.png", end_image_path="/d.png", target_duration=7.5),  # 8s -> 24 credits
    ]
    spec = FlowVideoChainSpec(
        job_id="plan_test_job",
        mode=default_spec.mode.SCENE_PAIRS,
        scene_pairs=sps,
        video_model="omni_flash",
        auto_duration=True,
    )
    plan = build_chain_plan(spec)
    assert plan.total_credit_cost == 12 + 18 + 24  # 54 credits
    assert len(plan.clips) == 3
    assert plan.clips[0].duration_seconds == 4
    assert plan.clips[0].credit_cost == 12
    assert plan.clips[1].duration_seconds == 6
    assert plan.clips[1].credit_cost == 18
    assert plan.clips[2].duration_seconds == 8
    assert plan.clips[2].credit_cost == 24


def _generate_synthetic_image(
    path: Path,
    width: int = 320,
    height: int = 180,
    color: tuple[int, int, int] = (100, 150, 200),
) -> Path:
    """Helper to generate a lightweight PNG image."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), color=color)
    img.save(path)
    return path


def test_zero_credit_flipbook_plan_generation(tmp_path: Path) -> None:
    """Verify zero_credit_flipbook tasks and plan generation with 0 credits."""
    # 1. Test duration and credit selector for zero_credit_flipbook
    dur, cost = select_clip_duration_and_credits(
        target_sec=3.5,
        video_model="zero_credit_flipbook",
        has_end_frame=True,
        mode="zero_credit_flipbook",
    )
    assert dur == 4
    assert cost == 0

    # 2. Build multi-frame flipbook tasks
    kf0 = KeyframeSpec(id="kf0", image_path=str(tmp_path / "f0.png"), target_duration=2.5)
    kf1 = KeyframeSpec(id="kf1", image_path=str(tmp_path / "f1.png"), target_duration=4.0)
    kf2 = KeyframeSpec(id="kf2", image_path=str(tmp_path / "f2.png"), target_duration=3.2)
    spec = VideoChainSpec(
        job_id="flipbook_plan_test",
        mode=ChainMode.ZERO_CREDIT_FLIPBOOK,
        aspect="16:9",
        duration_seconds=6,
        keyframes=[kf0, kf1, kf2],
    )

    tasks = build_flipbook_tasks(spec, work_dir=tmp_path)
    assert len(tasks) == 2
    assert tasks[0].clip_id == "clip_000_kf0_to_kf1"
    assert tasks[0].credit_cost == 0
    assert tasks[0].video_model == "zero_credit_flipbook"
    assert tasks[0].target_duration_sec == 2.5
    assert tasks[0].duration_seconds == int(round(2.5))

    assert tasks[1].clip_id == "clip_001_kf1_to_kf2"
    assert tasks[1].credit_cost == 0
    assert tasks[1].target_duration_sec == 4.0
    assert tasks[1].duration_seconds == 4

    # 3. Build plan
    plan = build_chain_plan(spec, work_dir=tmp_path)
    assert plan.total_credit_cost == 0
    assert plan.mode == ChainMode.ZERO_CREDIT_FLIPBOOK
    assert len(plan.clips) == 2

    # 4. Single keyframe hold (1 frame)
    single_spec = VideoChainSpec(
        job_id="single_hold_job",
        mode=ChainMode.ZERO_CREDIT_FLIPBOOK,
        keyframes=[kf0],
    )
    single_tasks = build_flipbook_tasks(single_spec, work_dir=tmp_path)
    assert len(single_tasks) == 1
    assert single_tasks[0].clip_id == "clip_000_kf0_hold"
    assert single_tasks[0].credit_cost == 0
    assert single_tasks[0].end_frame_path is None


def test_render_flipbook_segment(tmp_path: Path) -> None:
    """Verify render_flipbook_segment creates a valid animated MP4 clip via local ffmpeg."""
    im1 = _generate_synthetic_image(tmp_path / "im1.png", width=640, height=360, color=(50, 100, 150))
    im2 = _generate_synthetic_image(tmp_path / "im2.png", width=640, height=360, color=(150, 100, 50))
    out_clip = tmp_path / "flipbook_clip.mp4"

    # Multi-frame transition with xfade
    meta = render_flipbook_segment(
        start_image=im1,
        end_image=im2,
        output_mp4=out_clip,
        duration_sec=1.5,
        width=640,
        height=360,
        fps=30,
        crossfade_sec=0.3,
    )
    assert out_clip.is_file()
    assert meta["width"] == 640
    assert meta["height"] == 360
    assert meta["fps"] == 30.0
    assert 1.4 <= meta["duration"] <= 1.6

    # Single-frame hold
    out_hold = tmp_path / "flipbook_hold.mp4"
    meta_hold = render_flipbook_segment(
        start_image=im1,
        end_image=None,
        output_mp4=out_hold,
        duration_sec=1.0,
        width=640,
        height=360,
        fps=30,
    )
    assert out_hold.is_file()
    assert meta_hold["width"] == 640
    assert meta_hold["height"] == 360
    assert 0.9 <= meta_hold["duration"] <= 1.1


def test_orchestrator_zero_credit_flipbook_mode_end_to_end(tmp_path: Path) -> None:
    """Verify FlowVideoChainOrchestrator in zero_credit_flipbook mode produces a valid stitched MP4 with audio and 0 credits."""
    im1 = _generate_synthetic_image(tmp_path / "f1.png", width=640, height=360, color=(30, 60, 90))
    im2 = _generate_synthetic_image(tmp_path / "f2.png", width=640, height=360, color=(90, 60, 30))
    im3 = _generate_synthetic_image(tmp_path / "f3.png", width=640, height=360, color=(60, 90, 30))
    audio_wav = _generate_synthetic_wav(tmp_path / "audio.wav", duration=2.0)

    spec = VideoChainSpec(
        job_id="e2e_flipbook",
        mode=ChainMode.ZERO_CREDIT_FLIPBOOK,
        aspect="16:9",
        target_fps=30,
        audio_path=str(audio_wav),
        keyframes=[
            KeyframeSpec(id="k1", image_path=str(im1), target_duration=1.0),
            KeyframeSpec(id="k2", image_path=str(im2), target_duration=1.0),
            KeyframeSpec(id="k3", image_path=str(im3), target_duration=1.0),
        ],
    )

    out_mp4 = tmp_path / "final_flipbook.mp4"
    orchestrator = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work_flipbook",
        output_mp4_path=out_mp4,
        headless=True,
    )

    report = orchestrator.run()
    assert report["success"] is True
    assert report["mode"] == "zero_credit_flipbook"
    assert report["total_credit_cost"] == 0
    assert report["nb_clips"] == 2
    assert Path(report["output_path"]).is_file()

    meta = probe_video_clip(report["output_path"])
    assert meta["width"] == 1920
    assert meta["height"] == 1080
    assert meta["has_audio"] is True
    assert meta["duration"] > 0


def test_orchestrator_auto_fallback_zero_credit(tmp_path: Path) -> None:
    """Verify orchestrator automatically falls back to zero_credit_flipbook when account pool has 0 credits."""
    im1 = _generate_synthetic_image(tmp_path / "fb_f1.png", width=640, height=360, color=(40, 80, 120))
    im2 = _generate_synthetic_image(tmp_path / "fb_f2.png", width=640, height=360, color=(120, 80, 40))

    spec = VideoChainSpec(
        job_id="auto_fallback_test",
        mode=ChainMode.DAISY_CHAIN,  # Initially requested daisy_chain (omni_flash requires 7-15 credits)
        video_model="omni_flash",
        auto_fallback_zero_credit=True,
        keyframes=[
            KeyframeSpec(id="k1", image_path=str(im1), target_duration=1.0),
            KeyframeSpec(id="k2", image_path=str(im2), target_duration=1.0),
        ],
    )

    out_mp4 = tmp_path / "final_fallback.mp4"
    orchestrator = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=tmp_path / "work_fallback",
        output_mp4_path=out_mp4,
        headless=True,
    )

    # Mock credit ledger to report 0 credits across all profiles
    mock_profiles = [{"name": "profile_1", "cdp_port": 9222}]
    with patch("sys.flow_video.orchestrator.get_all_configured_profiles", return_value=mock_profiles):
        orchestrator.credit_ledger.sync_balance("profile_1", 0)  # 0 credits available

        report = orchestrator.run()
        assert report["success"] is True
        # Mode should have automatically fallen back to zero_credit_flipbook!
        assert report["mode"] == "zero_credit_flipbook"
        assert report["total_credit_cost"] == 0
        assert Path(report["output_path"]).is_file()


def test_zero_credit_flipbook_cli_args_parsing() -> None:
    """Verify run_flow_video_chain.py CLI parses zero_credit_flipbook and channel options."""
    import sys
    from sys.tools.run_flow_video_chain import parse_args

    test_argv = [
        "run_flow_video_chain.py",
        "--frames-dir", "/tmp",
        "--mode", "zero_credit_flipbook",
        "--channel", "channel_nano_free",
        "--auto-fallback-zero-credit",
    ]
    with patch.object(sys, "argv", test_argv):
        args = parse_args()
        assert args.mode == "zero_credit_flipbook"
        assert args.channel == "channel_nano_free"
        assert args.auto_fallback_zero_credit is True


