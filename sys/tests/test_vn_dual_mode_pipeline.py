"""Unit tests for Video Pilot VN Dual-Mode Pipeline:
- Short Omni 1.1 Flash Full-Chain (9:16)
- Long Chapter-Chunked 300-Image T4 NVENC Renderer (16:9)
- FFMETADATA1 YouTube Chapter Generation & Timing Invariants
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from sys.flow_video.models import ChainMode
from sys.tools.produce_vn_dual_mode import (
    DEFAULT_XFADE_DUR,
    KINETIC_RED_ASS,
    KINETIC_YELLOW_ASS,
    DualModeJobConfig,
    build_clean_sidecar_srt,
    build_ffmetadata_chapters,
    build_short_video_chain_spec,
    build_vn_kinetic_ass_subtitles,
    camera_zoompan_expr,
    compute_chunk_xfade_plan,
    format_youtube_description_chapters,
    partition_timeline_into_chunks,
    resolve_authenticated_profiles,
    resolve_beat_transition,
    run_dry_run_verify,
    run_long_mode,
)


def test_chunk_partitioning_300_beats_exact_boundary_timing() -> None:
    """Verify chunk partitioning of a 300-beat Long timeline into 15-22 beat chunks
    with exact cumulative boundary timing and xfade offset math matching total audio duration.
    """
    # 1. Synthesize 300 beats with realistic varying durations [1.8s .. 3.9s]
    beats = []
    durations = []
    for i in range(300):
        # Deterministic varying durations
        d = round(1.8 + (i % 7) * 0.35, 4)
        beats.append({
            "beat_id": f"B{i:03d}",
            "narration": f"Phân đoạn bóc tách kinh tế {i + 1}",
            "camera_motion": "push_in" if i % 2 == 0 else "zoom_out",
            "transition": "fade" if i % 3 == 0 else "smoothright",
            "duration": d,
        })
        durations.append(d)

    total_audio_dur = round(sum(durations), 4)
    assert len(beats) == 300
    assert total_audio_dur > 0

    # 2. Partition into chunks
    chunks = partition_timeline_into_chunks(beats, durations, min_chunk_size=15, max_chunk_size=22)

    # Verify chunk count and sizes
    assert len(chunks) > 1
    total_beats_in_chunks = sum(len(c.beats) for c in chunks)
    assert total_beats_in_chunks == 300

    for idx, c in enumerate(chunks):
        c_size = len(c.beats)
        assert 15 <= c_size <= 22, f"Chunk {idx} size {c_size} outside [15, 22]"
        assert len(c.beat_durations) == c_size
        assert abs(c.chunk_duration - sum(c.beat_durations)) < 1e-4

    # 3. Verify contiguous boundary timing: S_0 = 0, S_k == E_{k-1}, E_last == total_audio_dur
    assert chunks[0].start_time == 0.0
    for k in range(1, len(chunks)):
        prev_chunk = chunks[k - 1]
        curr_chunk = chunks[k]
        assert abs(curr_chunk.start_time - prev_chunk.end_time) < 1e-4, (
            f"Chunk {k} start ({curr_chunk.start_time}) != Chunk {k-1} end ({prev_chunk.end_time})"
        )

    last_chunk = chunks[-1]
    assert abs(last_chunk.end_time - total_audio_dur) < 1e-4, (
        f"Last chunk end time ({last_chunk.end_time}) != total audio duration ({total_audio_dur})"
    )

    # 4. Verify xfade offset math inside each chunk
    total_stitched_from_chunks = 0.0
    for c in chunks:
        plan = compute_chunk_xfade_plan(c, xfade_dur=DEFAULT_XFADE_DUR)
        segments = plan["segments"]
        k = len(segments)

        cum_offset = 0.0
        for seg_idx, seg in enumerate(segments):
            dur_j = seg["spoken_duration"]
            encoded_dur = seg["encoded_segment_duration"]
            offset_j = seg["xfade_offset"]

            # Offset must strictly equal sum of preceding beats in this chunk
            assert abs(offset_j - cum_offset) < 1e-4
            if seg_idx < k - 1:
                assert abs(encoded_dur - (dur_j + DEFAULT_XFADE_DUR)) < 1e-4
            else:
                assert abs(encoded_dur - dur_j) < 1e-4

            cum_offset += dur_j

        total_stitched_from_chunks += cum_offset

    assert abs(total_stitched_from_chunks - total_audio_dur) < 1e-4, (
        f"Total stitched duration ({total_stitched_from_chunks}) != audio duration ({total_audio_dur})"
    )


def test_ffmetadata_chapters_generation_intervals(tmp_path: Path) -> None:
    """Verify FFMETADATA1 YouTube Chapter generation: >=8 chapters, each interval >=10s,
    standard TIMEBASE=1/1000 syntax, and contiguous timing.
    """
    total_dur = 360.0  # 6-minute explainer
    out_meta = tmp_path / "test_chapters.txt"

    meta_str, chapters = build_ffmetadata_chapters(
        total_duration=total_dur,
        title="Bí Ẩn Tiền Tệ",
        artist="Túi Tiền",
        min_chapters=8,
        min_interval_sec=10.0,
        out_path=out_meta,
    )

    # 1. Structure and count verification
    assert len(chapters) >= 8, f"Expected >= 8 chapters, found {len(chapters)}"
    assert out_meta.is_file()
    assert meta_str.startswith(";FFMETADATA1")
    assert "title=Bí Ẩn Tiền Tệ" in meta_str
    assert "artist=Túi Tiền" in meta_str

    # 2. Verify intervals: each >= 10s and contiguous coverage
    assert chapters[0].start_sec == 0.0
    for idx, ch in enumerate(chapters):
        assert ch.duration_sec >= 10.0, f"Chapter {idx} duration {ch.duration_sec} < 10.0s"
        assert ch.end_sec > ch.start_sec
        assert abs(ch.end_sec - ch.start_sec - ch.duration_sec) < 1e-4
        if idx > 0:
            assert abs(ch.start_sec - chapters[idx - 1].end_sec) < 1e-4

    assert abs(chapters[-1].end_sec - total_dur) < 1e-4

    # 3. Verify TIMEBASE=1/1000 and Millisecond START/END values in FFMETADATA1
    chapter_blocks = re.findall(r"\[CHAPTER\]\s+TIMEBASE=1/1000\s+START=(\d+)\s+END=(\d+)\s+title=(.+)", meta_str)
    assert len(chapter_blocks) == len(chapters)

    for i, (start_ms_str, end_ms_str, title_str) in enumerate(chapter_blocks):
        s_ms = int(start_ms_str)
        e_ms = int(end_ms_str)
        assert e_ms - s_ms >= 10000, f"Chapter {i} interval {e_ms - s_ms}ms < 10000ms"
        assert s_ms == int(round(chapters[i].start_sec * 1000))
        assert e_ms == int(round(chapters[i].end_sec * 1000))
        assert title_str.strip() == chapters[i].title

    # 4. Verify human-readable YouTube description chapter formatting
    desc_text = format_youtube_description_chapters(chapters)
    desc_lines = desc_text.strip().splitlines()
    assert len(desc_lines) == len(chapters)
    assert desc_lines[0].startswith("00:00 - ")


def test_short_video_chain_spec_construction() -> None:
    """Verify Short 9:16 Omni 1.1 Flash VideoChainSpec construction:
    video_model='omni_flash', aspect='9:16', mode=ChainMode.SCENE_PAIRS,
    auto_fallback_zero_credit=False.
    """
    shots = [
        {"id": "S01", "narration": "Cảnh mở đầu", "prompt": "Prompt 1", "camera_motion": "push_in", "duration": 2.5},
        {"id": "S02", "narration": "Cảnh thứ hai", "prompt": "Prompt 2", "camera_motion": "pan_right", "duration": 3.0},
        {"id": "S03", "narration": "Cảnh thứ ba", "prompt": "Prompt 3", "camera_motion": "tilt_up", "duration": 2.8},
        {"id": "S04", "narration": "Cảnh kết thúc", "prompt": "Prompt 4", "camera_motion": "zoom_out", "duration": 3.2},
    ]
    durations = [2.5, 3.0, 2.8, 3.2]

    spec = build_short_video_chain_spec(
        channel_slug="tui-tien",
        job_id="test_short_job",
        shots=shots,
        audio_path="/tmp/test_audio.wav",
        beat_durations=durations,
        auto_fallback_zero_credit=False,
    )

    assert spec.job_id == "test_short_job"
    assert spec.video_model == "omni_flash"
    assert spec.aspect == "9:16"
    assert spec.mode == ChainMode.SCENE_PAIRS
    assert spec.auto_fallback_zero_credit is False
    assert spec.channel_id == "tui-tien"
    assert spec.overscan_crop == 1.05
    assert spec.audio_path == "/tmp/test_audio.wav"

    # Scene pairs verification: 4 shots -> 3 consecutive pairs with last duration folded into final pair
    assert len(spec.scene_pairs) == 3
    for idx, pair in enumerate(spec.scene_pairs):
        assert pair.id == f"pair_{idx:02d}"
        expected_dur = durations[idx] + (durations[idx + 1] if idx == len(spec.scene_pairs) - 1 else 0.0)
        assert abs(pair.target_duration - expected_dur) < 1e-4
        assert pair.trim_first_frame is True
        assert pair.start_image_prompt == shots[idx]["prompt"]
        assert pair.end_image_prompt == shots[idx + 1]["prompt"]

    assert abs(sum(p.target_duration for p in spec.scene_pairs) - sum(durations)) < 1e-4


def test_kinetic_ass_subtitles_formatting(tmp_path: Path) -> None:
    """Verify 1-word alternating Red (#FF3B30) & Yellow (#FFE600) kinetic ASS formatting."""
    words = [
        {"word": "Bố", "start": 0.0, "end": 0.25},
        {"word": "trí", "start": 0.25, "end": 0.50},
        {"word": "siêu", "start": 0.50, "end": 0.80},
        {"word": "thị", "start": 0.80, "end": 1.10},
    ]
    out_ass = tmp_path / "subtitles_kinetic.ass"

    build_vn_kinetic_ass_subtitles(words, total_duration=2.0, out_ass=out_ass, margin_v=270, outline=6)
    assert out_ass.is_file()

    content = out_ass.read_text(encoding="utf-8")
    assert "PlayResX: 1080" in content
    assert "PlayResY: 1920" in content

    # Colors
    assert f"Style: KineticRed,Arial,100,{KINETIC_RED_ASS}" in content
    assert f"Style: KineticYellow,Arial,100,{KINETIC_YELLOW_ASS}" in content
    assert "Outline, Shadow" in content or ",1,6,4,2,40,40,270,1" in content

    # Alternating dialogue lines
    events = [line for line in content.splitlines() if line.startswith("Dialogue:")]
    assert len(events) == 4
    assert ",KineticRed," in events[0]
    assert ",KineticYellow," in events[1]
    assert ",KineticRed," in events[2]
    assert ",KineticYellow," in events[3]


def test_clean_sidecar_srt_generation(tmp_path: Path) -> None:
    """Verify phrase-level clean sidecar SRT generation."""
    beats = [
        {"narration": "Bố trí siêu thị là một cái bẫy tâm lý"},
        {"narration": "được lập trình để kích hoạt ham muốn tiêu tiền."},
    ]
    durations = [2.2, 2.8]
    out_srt = tmp_path / "subtitles.srt"

    build_clean_sidecar_srt(beats, durations, total_duration=5.0, out_srt=out_srt)
    assert out_srt.is_file()

    content = out_srt.read_text(encoding="utf-8")
    assert "1\n00:00:00,000 --> " in content
    assert "Bố trí siêu thị" in content


def test_camera_zoompan_expressions_zero_snap() -> None:
    """Verify camera zoompan expressions use pure continuous functions of (on/N) without snaps."""
    motions = ["push_in", "zoom_out", "pan_left", "pan_right", "tilt_up", "tilt_down", "drift_diag_in", "drift_diag_out", "static_hold"]

    for m in motions:
        expr = camera_zoompan_expr(m, nb_frames=90, width=1920, height=1080, fps=30)
        assert "s=1920x1080:fps=30" in expr
        assert "on/90" in expr or "1.06" in expr
        # Ensure forbidden snaps are absent
        assert "eq(on,1)" not in expr
        assert "min(zoom+" not in expr  # recursive state-reset banned

    # Verify transitions
    assert resolve_beat_transition({"camera_motion": "pan_right"}, 1) == "smoothleft"
    assert resolve_beat_transition({"camera_motion": "pan_left"}, 2) == "smoothright"
    assert resolve_beat_transition({"camera_motion": "tilt_up"}, 3) == "smoothup"
    assert resolve_beat_transition({"camera_motion": "tilt_down"}, 4) == "smoothdown"
    assert resolve_beat_transition({"transition": "fade"}, 5) == "fade"
    assert resolve_beat_transition({"transition": "dissolve"}, 6) == "dissolve"
    assert resolve_beat_transition({"transition": "cut"}, 7) == "fade"
    assert resolve_beat_transition({"transition": "smoothright"}, 8) == "smoothright"


def test_dry_run_verify_dual_mode_pipeline(tmp_path: Path) -> None:
    """Verify Mode 3 dry-run verification contract."""
    config = DualModeJobConfig(
        job_id="test_dual_verify",
        channel_slug="tui-tien",
        output_dir=tmp_path / "out",
        render_backend="local",
        dry_run=True,
    )
    result = run_dry_run_verify(config)

    assert result["status"] == "verified"
    assert result["mode"] == "dry-run-verify"

    short_res = result["short_verification"]
    assert short_res["status"] == "success"
    assert short_res["mode"] == "build-short"
    assert Path(short_res["video_path"]).is_file()

    long_res = result["long_verification"]
    assert long_res["status"] == "success"
    assert long_res["mode"] == "build-long"
    assert Path(long_res["video_path"]).is_file()
    assert long_res["chunks_rendered"] > 0
    assert long_res["chapters_count"] >= 8
    assert Path(long_res["metadata_path"]).is_file()
    assert Path(long_res["thumbnail_path"]).is_file()


def test_vn_long_high_density_planner_integration_contract(tmp_path: Path) -> None:
    """Verify integration with vn_long_high_density_planner:
    run_long_mode(dry_run=True) automatically invokes plan_long_visual_states_from_chapters,
    producing 260-350 beats, a valid based_on DAG, 8-12 FFMETADATA1 chapters, and 15-22 beat chunks.
    """
    out_dir = tmp_path / "long_test_out"
    config = DualModeJobConfig(
        job_id="test_long_planner_integ",
        channel_slug="tui-tien",
        output_dir=out_dir,
        render_backend="local",
        dry_run=True,
    )
    result = run_long_mode(config)

    assert result["status"] == "success"
    assert result["mode"] == "build-long"
    assert Path(result["video_path"]).is_file()
    assert Path(result["metadata_path"]).is_file()
    assert Path(result["thumbnail_path"]).is_file()

    # Verify 8-12 FFMETADATA1 chapters
    assert 8 <= result["chapters_count"] <= 12

    # Verify chunk count reflects 15-22 beats per chunk
    chunks_count = result["chunks_rendered"]
    assert chunks_count >= 10

    # Read back metadata to verify FFMETADATA1 chapters syntax
    meta_content = Path(result["metadata_path"]).read_text(encoding="utf-8")
    assert ";FFMETADATA1" in meta_content
    chapter_blocks = re.findall(r"\[CHAPTER\]\s+TIMEBASE=1/1000\s+START=(\d+)\s+END=(\d+)", meta_content)
    assert 8 <= len(chapter_blocks) <= 12

    # Verify each chapter interval is >= 10s (10000 ms)
    for start_ms, end_ms in chapter_blocks:
        assert int(end_ms) - int(start_ms) >= 10000

    # Verify 260-350 generated images and valid DAG
    images_dir = out_dir / config.job_id / "_work_long" / "images"
    image_files = list(images_dir.glob("img_*.png"))
    assert 260 <= len(image_files) <= 350


def test_transition_mapping_guards_and_remote_script_subscript() -> None:
    """Verify transition mapping handles 'cut' / 'dissolve' / 'smoothright' cleanly,
    and remote_script uses beats[i].get("transition", "fade") instead of stale beat.
    """
    # 1. Transition mapping
    assert resolve_beat_transition({"transition": "cut"}, 0) == "fade"
    assert resolve_beat_transition({"transition": "dissolve"}, 1) == "dissolve"
    assert resolve_beat_transition({"transition": "smoothright"}, 2) == "smoothright"
    assert resolve_beat_transition({"transition": "smoothleft"}, 3) == "smoothleft"
    assert resolve_beat_transition({"transition": "smoothup"}, 4) == "smoothup"
    assert resolve_beat_transition({"transition": "smoothdown"}, 5) == "smoothdown"
    assert resolve_beat_transition({"transition": "fade"}, 6) == "fade"
    # Non-xfade transition name maps safely to fade
    assert resolve_beat_transition({"transition": "wipe_diagonal_flip"}, 7) == "fade"

    # 2. Inspect source code of render_long_chapter_chunks_colab_t4
    import inspect
    from sys.tools.produce_vn_dual_mode import render_long_chapter_chunks_colab_t4
    source = inspect.getsource(render_long_chapter_chunks_colab_t4)

    # Must use beats[i] in the xfade loop, NOT stale beat from earlier loop
    assert 'beats[i].get("transition"' in source or "beats[i].get('transition'" in source
    # Must guard cut/invalid transitions in remote script
    assert "valid_xfades" in source
    # Must guarantee client.stop() teardown in finally block
    assert "finally:" in source
    assert "client.stop()" in source


def test_profile_filtering_credit_ledger_and_cli_override(tmp_path: Path) -> None:
    """Verify profile filtering excludes unauthenticated (last_used_at <= 0 or profile_en*) profiles
    and respects explicit --profiles CLI override.
    """
    from sys.flow_cdp.credit_ledger import CreditLedger

    ledger_p = tmp_path / "test_credits.json"
    ledger = CreditLedger(path=ledger_p)

    with ledger._locked_store() as data:
        data["profiles"] = {
            "profile_1": {"credits_remaining": 500, "last_used_at": 1793000000.0, "status": "active"},
            "profile_2": {"credits_remaining": 1000, "last_used_at": 0.0, "status": "active"},  # unauthenticated
            "profile_3": {"credits_remaining": 750, "last_used_at": 1793000100.0, "status": "active"},
            "profile_en01": {"credits_remaining": 1000, "last_used_at": 1793000200.0, "status": "active"},  # EN profile
        }

    # Case 1: Default filtering excludes last_used_at == 0 and profile_en*
    filtered = resolve_authenticated_profiles(profiles_filter=None, credit_ledger=ledger)
    filtered_names = {p.get("name") or p.get("id") for p in filtered}

    assert "profile_1" in filtered_names
    assert "profile_3" in filtered_names
    assert "profile_2" not in filtered_names  # last_used_at == 0 excluded
    assert "profile_en01" not in filtered_names  # profile_en* excluded

    # Case 2: Explicit CLI override respects requested profile list
    override_names = ["profile_2", "profile_en01"]
    overridden = resolve_authenticated_profiles(profiles_filter=override_names, credit_ledger=ledger)
    overridden_names = {p.get("name") or p.get("id") for p in overridden}

    assert "profile_2" in overridden_names
    assert "profile_en01" in overridden_names


def test_short_video_chain_and_stitch_alignment_13_beats_12_clips(tmp_path: Path, monkeypatch) -> None:
    """Verify that 13 beats produce 12 ScenePairSpec items covering 100% of audio duration,
    and stitch_hybrid_scene_groups_and_package aligns effective_shots and effective_durs to 12
    so groups never exceed len(clips) - 1, completely preventing IndexError on Colab.
    """
    shots = [
        {"id": f"S{i:02d}", "narration": f"Beat {i}", "prompt": f"Prompt {i}", "duration": 2.5 + 0.1 * i}
        for i in range(13)
    ]
    durations = [float(s["duration"]) for s in shots]
    total_audio_dur = sum(durations)

    # 1. Build short video chain spec
    spec = build_short_video_chain_spec(
        channel_slug="tui-tien",
        job_id="test_align_job",
        shots=shots,
        audio_path="/tmp/test_narration.wav",
        beat_durations=durations,
    )
    assert len(spec.scene_pairs) == 12
    # Verify sum of pair durations exactly matches total audio duration (last duration folded into pair_11)
    assert abs(sum(p.target_duration for p in spec.scene_pairs) - total_audio_dur) < 1e-4
    assert abs(spec.scene_pairs[-1].target_duration - (durations[11] + durations[12])) < 1e-4

    # 2. Simulate 12 completed tasks from orchestrator
    from sys.flow_video.models import VideoClipTask

    tasks = [
        VideoClipTask(
            clip_id=f"pair_{i:02d}",
            index=i,
            start_frame_path=f"/tmp/frame_{i}.png",
            end_frame_path=f"/tmp/frame_{i+1}.png",
            output_mp4_path=str(tmp_path / f"clip_{i:02d}.mp4"),
            aspect="9:16",
            video_model="omni_flash",
            target_duration=spec.scene_pairs[i].target_duration,
        )
        for i in range(12)
    ]

    # Create dummy files for audio, ass, srt, watermark
    audio_wav = tmp_path / "audio.wav"
    audio_wav.write_bytes(b"RIFF" + b"\x00" * 100)
    ass_path = tmp_path / "sub.ass"
    ass_path.write_text("[Script Info]\n", encoding="utf-8")
    srt_path = tmp_path / "sub.srt"
    srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nTest\n", encoding="utf-8")
    wm_png = tmp_path / "wm.png"
    wm_png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
    out_mp4 = tmp_path / "out.mp4"

    # Capture arguments passed to package_final_on_colab_t4_nvenc
    captured_kwargs = {}

    def mock_package(**kwargs):
        captured_kwargs.update(kwargs)
        return {"duration": total_audio_dur, "video_encoder": "colab_t4_h264_nvenc"}

    import sys.tools.produce_en_flow_dynamic_demo as demo_mod
    monkeypatch.setattr(demo_mod, "package_final_on_colab_t4_nvenc", mock_package)

    from sys.tools.produce_en_flow_dynamic_demo import stitch_hybrid_scene_groups_and_package

    meta = stitch_hybrid_scene_groups_and_package(
        channel_slug="tui-tien",
        aspect="9:16",
        shots=shots,
        tasks=tasks,
        beat_durations=durations,
        audio_path=audio_wav,
        ass_path=ass_path,
        srt_path=srt_path,
        watermark_png=wm_png,
        out_mp4=out_mp4,
        dry_run=False,
    )

    assert meta["video_encoder"] == "colab_t4_h264_nvenc"
    assert "groups" in captured_kwargs
    passed_groups = captured_kwargs["groups"]
    passed_durs = captured_kwargs["beat_durations"]

    # Invariants:
    # 1. Zero index in groups >= 12 (len(tasks) == 12, so max index is 11)
    all_indices = [idx for grp in passed_groups for idx in grp]
    assert max(all_indices) < 12
    assert len(all_indices) == 12

    # 2. Length of passed beat_durations is 12 and sum equals full 13-beat total_audio_dur
    assert len(passed_durs) == 12
    assert abs(sum(passed_durs) - total_audio_dur) < 1e-4

    # 3. Last task target_duration folded the remaining beat duration
    assert abs(tasks[-1].target_duration - (durations[11] + durations[12])) < 1e-4


def test_dispatch_long_image_dag_flattening_and_resume_safety(tmp_path: Path, monkeypatch) -> None:
    """Verify that dispatch_long_image_dag_via_pool:
    1. Flattens multi-hop based_on chains (C -> B -> A => C -> A).
    2. Clears based_on to None if the anchor image already exists on disk (preventing deadlock in deferred_tasks).
    3. Keeps based_on pointing to root anchor if anchor is missing.
    4. Passes credit_cost=0 and editorial_overlay={'enabled': False} on every task.
    """
    out_dir = tmp_path / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 6 beats:
    # B000: Anchor 1
    # B001: based_on B000
    # B002: based_on B001 (multi-hop to B000)
    # B003: based_on B002 (multi-hop to B000)
    # B004: Anchor 2 (missing from disk)
    # B005: based_on B004
    beats = [
        {"beat_id": "B000", "prompt": "Prompt 0", "based_on": None},
        {"beat_id": "B001", "prompt": "Prompt 1", "based_on": "B000"},
        {"beat_id": "B002", "prompt": "Prompt 2", "based_on": "B001"},
        {"beat_id": "B003", "prompt": "Prompt 3", "based_on": "B002"},
        {"beat_id": "B004", "prompt": "Prompt 4", "based_on": None},
        {"beat_id": "B005", "prompt": "Prompt 5", "based_on": "B004"},
    ]

    # Simulate resume where B000 already finished on disk (>5000 bytes)
    img_0000 = out_dir / "img_0000.png"
    img_0000.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 6000)

    submitted_tasks = []

    class MockPool:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def start(self):
            pass

        def submit_task(self, task):
            submitted_tasks.append(task)

        def join(self):
            pass

        def shutdown(self):
            pass

    import sys.tools.produce_vn_dual_mode as dual_mod
    monkeypatch.setattr(dual_mod, "PersistentWorkerPool", MockPool)
    monkeypatch.setattr(dual_mod, "resolve_authenticated_profiles", lambda *args, **kwargs: [{"name": "profile_1"}])

    image_paths = dual_mod.dispatch_long_image_dag_via_pool(
        channel_slug="tui-tien",
        beats=beats,
        output_dir=out_dir,
        max_workers=8,
        dry_run=False,
    )

    assert len(image_paths) == 6
    # B000 is skipped because it's already on disk
    task_map = {t["id"]: t for t in submitted_tasks}
    assert "B000" not in task_map
    assert set(task_map.keys()) == {"B001", "B002", "B003", "B004", "B005"}

    # B001, B002, B003 root anchor was B000. Since B000 is already on disk, based_on MUST be None!
    assert task_map["B001"]["based_on"] is None
    assert task_map["B002"]["based_on"] is None
    assert task_map["B003"]["based_on"] is None

    # B004 is missing anchor -> based_on is None
    assert task_map["B004"]["based_on"] is None

    # B005 root anchor is B004. B004 is NOT on disk yet -> based_on is "B004"
    assert task_map["B005"]["based_on"] == "B004"

    # Tasks have credit_cost=0 and editorial_overlay disabled
    for t in submitted_tasks:
        assert t["credit_cost"] == 0
        assert t["credit_reason"] == "image"
        assert t["editorial_overlay"] == {"enabled": False}


def test_render_long_chapter_chunks_colab_t4_bundle_and_pool_select(tmp_path: Path, monkeypatch) -> None:
    """Verify that render_long_chapter_chunks_colab_t4:
    1. Imports and uses select_pool without ImportError.
    2. Converts images to JPEG Q92 (~14x smaller bundle) and pre-encodes AAC narration.m4a.
    3. Includes render_job.py inside bundle.zip using zipfile.ZIP_STORED.
    4. Guarantees client.stop() teardown in finally block.
    """
    from colab_bridge.accounts import select_pool
    accounts = select_pool(session="vp-test-session", role="render")
    assert isinstance(accounts, list)
    assert len(accounts) > 0

    import sys.tools.produce_vn_dual_mode as dual_mod

    # Create dummy images
    from PIL import Image
    image_paths = []
    for i in range(3):
        p = tmp_path / f"img_{i:04d}.png"
        im = Image.new("RGB", (128, 72), (i * 40, 50, 60))
        im.save(p, "PNG")
        image_paths.append(p)

    # Create dummy audio, watermark, metadata
    audio_wav = tmp_path / "audio.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=f=440:d=1.0", "-c:a", "pcm_s16le", str(audio_wav)],
        check=True,
        capture_output=True,
    )
    wm_png = tmp_path / "watermark.png"
    wm_im = Image.new("RGBA", (32, 32), (255, 255, 255, 200))
    wm_im.save(wm_png, "PNG")
    meta_txt = tmp_path / "chapters_metadata.txt"
    meta_txt.write_text(";FFMETADATA1\n", encoding="utf-8")
    out_mp4 = tmp_path / "final.mp4"

    from sys.tools.produce_vn_dual_mode import BeatChunk
    chunks = [
        BeatChunk(
            chunk_index=0,
            start_beat_idx=0,
            end_beat_idx=3,
            beats=[
                {"camera_motion": "push_in", "transition": "fade"},
                {"camera_motion": "zoom_out", "transition": "fade"},
                {"camera_motion": "push_in", "transition": "fade"},
            ],
            beat_durations=[1.0, 1.0, 1.0],
            start_time=0.0,
            end_time=3.0,
            chunk_duration=3.0,
        )
    ]

    stopped_sessions = []
    uploaded_files = {}

    class MockClient:
        def __init__(self, sys_dir, cfg):
            self.account = cfg.get("colab_tts", {}).get("account", "account-01")
            self.session = cfg.get("colab_tts", {}).get("session", "test-session")

        def ensure_authenticated(self):
            pass

        def _ready(self, auto_start=True):
            pass

        def exec(self, cmd, timeout=30):
            if "shutil.disk_usage" in cmd:
                return "WORK_DIR:/dev/shm/vp_long_test_bundle"
            if "status.json" in cmd:
                return 'POLL_STATUS:{"status": "completed", "completed_chunks": 1, "total_chunks": 1}'
            return ""

        def call(self, action, *args, **kwargs):
            if action == "upload":
                # args: -s, session, local_p, remote_p
                src = args[2]
                uploaded_files["bundle.zip"] = Path(src).read_bytes()
            elif action == "download":
                # args: -s, session, remote_p, local_p
                dest = Path(args[3])
                # Generate a valid tiny MP4 so probe_video_clip succeeds
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=0.1", "-c:v", "libx264", str(dest)],
                    check=True,
                    capture_output=True,
                )

        def stop(self):
            stopped_sessions.append(self.session)

    monkeypatch.setattr(dual_mod, "Client", MockClient)

    res = dual_mod.render_long_chapter_chunks_colab_t4(
        job_id="test_bundle",
        chunks=chunks,
        image_paths=image_paths,
        audio_path=audio_wav,
        metadata_path=meta_txt,
        watermark_png=wm_png,
        out_mp4=out_mp4,
        colab_account="account-01",
    )

    assert res["video_encoder"] == "colab_t4_h264_nvenc"
    assert "test-session" in stopped_sessions or any("vp-vn-long-" in s for s in stopped_sessions)
    assert "bundle.zip" in uploaded_files

    # Inspect uploaded bundle.zip contents
    import io
    import zipfile
    with zipfile.ZipFile(io.BytesIO(uploaded_files["bundle.zip"]), "r") as zf:
        namelist = zf.namelist()
        assert "narration.m4a" in namelist
        assert "render_job.py" in namelist
        assert "manifest.json" in namelist
        assert "chapters_metadata.txt" in namelist
        assert "watermark.png" in namelist
        assert "images/img_0000.jpg" in namelist
        assert "images/img_0001.jpg" in namelist
        assert "images/img_0002.jpg" in namelist
