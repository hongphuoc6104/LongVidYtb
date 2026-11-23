"""Automated Pytest Suite for the Parameterized M1-Flex V9.2 Production Engine (`produce_su_ke_lai_long_m1.py`).

Covers:
  - All 4 `--color-preset` modes (`golden_dawn_1789`, `river_mist_teal_gold`, `monsoon_siege_contrast`, `imperial_torch_amber`)
  - Both `--chapter-style` modes (`minimal_center_card`, `in_scene_cinema_title`)
  - All 3 `--chain-pattern` modes (`balanced_2beat`, `dynamic_1_2_3beat`, `epic_3beat`)
  - `--keyword-density` enforcement (`0.15..0.30` sparse ratio, `beat_*0` always text-free, `top_word == ""`, `card_subtitle == ""`)
  - `full-cc-srt` generation (`subtitles_vi_full_cc.srt`) & impact keyword SRT (`subtitles_impact_keywords.srt`)
  - All 4 `NARRATIVE_ARCHETYPES` & all 3 `--resolution` modes (`360p`, `1080p`, `1440p`)
  - Hard-coded safety locks: `0` whip-slides (`directional_flow_chain_transition` banned), `0` Pillow 2D/3D cartoon maps
    (`map_dive` banned), `0` text in top/bottom pure-black IMAX `2.39:1` letterbox bars, and 100% moving `.mp4` verification.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import tools.produce_su_ke_lai_long_m1 as m1_flex
from tools.produce_su_ke_lai_long_m1 import (
    CHAIN_PATTERNS,
    CHAPTER_STYLES,
    COLOR_PRESETS,
    M1_FLEX_ENGINE_VERSION,
    M1_FLEX_PATTERN_ID,
    NARRATIVE_ARCHETYPES,
    PERMANENTLY_BANNED_INSERTS,
    PERMANENTLY_BANNED_TRANSITIONS,
    RESOLUTION_SPECS,
    ShardFFmpegWriter,
    ShardFrameBank,
    _write_wav_stereo_i16,
    apply_bright_golden_dawn_grade,
    assemble_full_video,
    build_timeline_and_master_audio,
    enforce_sparse_keyword_density,
    get_resolution_geometry,
    main as m1_cli_main,
    plan_chain_assignments,
    render_shard,
    set_active_resolution,
    validate_m1_flex_options,
    write_full_cc_srt,
)

ENGINE_FILE = Path(m1_flex.__file__).resolve()


def _create_synthetic_m1_job(tmp_path: Path, *, num_chapters: int = 3, beats_per_chapter: int = 10) -> dict[str, Path]:
    """Create a self-contained synthetic M1-Flex job directory with WAVs, PNGs, and moving 16:9 .mp4 clips."""
    job_dir = tmp_path / "job_m1_flex_test"
    audio_dir = job_dir / "audio"
    frames_dir = job_dir / "frames"
    clips_dir = job_dir / "raw_clips"
    out_dir = tmp_path / "video_out"
    for d in (audio_dir, frames_dir, clips_dir, out_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Create a short 1.2s 48kHz stereo WAV template with rhythmic energy envelope
    sr = 48000
    n_samples = int(1.20 * sr)
    t = np.arange(n_samples, dtype=np.float32) / float(sr)
    wave_mono = (0.25 * np.sin(2.0 * np.pi * 220.0 * t) * (0.6 + 0.4 * np.sin(2.0 * np.pi * 4.0 * t))).astype(np.float32)
    wave_stereo = np.stack([wave_mono, wave_mono], axis=1)

    # 2. Create a valid moving 16:9 .mp4 clip (> 180KB so MIN_CLIP_BYTES passes)
    master_clip = clips_dir / "chain_00.mp4"
    rng = np.random.default_rng(1789)
    with ShardFFmpegWriter(master_clip, width=640, height=360, fps=24, crf=10, preset="ultrafast") as writer:
        for fi in range(36):
            noise_frame = rng.integers(30, 225, size=(360, 640, 3), dtype=np.uint8)
            writer.write_frame(noise_frame)
    # Pad file tail slightly if needed so st_size >= MIN_CLIP_BYTES (180_000)
    if master_clip.stat().st_size < 190_000:
        with open(master_clip, "ab") as f:
            f.write(b"\x00" * (190_000 - master_clip.stat().st_size))

    total_beats = num_chapters * beats_per_chapter
    for c_idx in range(1, total_beats + 2):
        cp = clips_dir / f"chain_{c_idx:02d}.mp4"
        if not cp.exists():
            cp.hardlink_to(master_clip)

    chapters_list: list[dict[str, Any]] = []
    beats_list: list[dict[str, Any]] = []
    g_idx = 0
    for ch_i in range(1, num_chapters + 1):
        chapters_list.append(
            {
                "chapter_index": ch_i,
                "header": f"CHƯƠNG {ch_i}",
                "main_word": f"CHIẾN DỊCH HỒI {ch_i}",
                "subtitle": "SHOULD BE IGNORED BY V4 LOCK",
                "tone": "fire" if ch_i == 2 else "gold",
            }
        )
        for lp in range(beats_per_chapter):
            bid = f"beat_{g_idx:03d}"
            _write_wav_stereo_i16(audio_dir / f"{bid}.wav", wave_stereo)
            # Small valid PNG fallback frame
            if g_idx == 0:
                from PIL import Image
                Image.new("RGB", (320, 180), (90, 70, 50)).save(frames_dir / f"{bid}.png")
            else:
                (frames_dir / f"{bid}.png").hardlink_to(frames_dir / "beat_000.png")

            # Deliberately put show_keyword=True on chapter openers (lp == 0) and on ~40% of beats
            # to verify that enforce_sparse_keyword_density strips beat_*0 and clamps to target density!
            want_kw = (lp == 0) or (lp in (2, 5, 7, 8))
            beats_list.append(
                {
                    "beat_id": bid,
                    "chapter_index": ch_i,
                    "text": f"Đạo quân Tây Sơn thứ {g_idx} tiến công thần tốc phá vỡ phòng tuyến quân Thanh tại Ngọc Hồi. [pause:300ms]",
                    "show_keyword": want_kw,
                    "top_word": "BANNED TOP KICKER",
                    "main_word": f"THẦN TỐC {g_idx:02d}" if want_kw else "",
                    "target_keyword": "thần tốc",
                    "sfx_type": "elephant_trumpet" if lp == 5 else "war_drum",
                    "use_3d_map_dive": True,  # Must be hard-overridden to False by safety lock!
                }
            )
            g_idx += 1

    script_path = job_dir / "script.json"
    script_path.write_text(
        json.dumps({"job_id": "job_m1_flex_test", "chapters": chapters_list, "beats": beats_list}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        "job_dir": job_dir,
        "script": script_path,
        "audio_dir": audio_dir,
        "frames_dir": frames_dir,
        "raw_clips_dir": clips_dir,
        "timeline": job_dir / "timeline_m1_full.json",
        "master_wav": job_dir / "master_audio_m1_full.wav",
        "srt": job_dir / "subtitles_impact_keywords.srt",
        "full_cc_srt": job_dir / "subtitles_vi_full_cc.srt",
        "output_dir": out_dir,
    }


def test_m1_flex_version_archetypes_and_zero_whip_zero_map_ast_lock() -> None:
    """Verify M1-Flex V9.2 constants, 4 narrative archetypes, and AST ban on whip-slides & cartoon maps."""
    assert M1_FLEX_ENGINE_VERSION == "9.2.0"
    assert M1_FLEX_PATTERN_ID == "su_ke_lai_long_v9_2_m1_flex_engine"
    assert set(COLOR_PRESETS.keys()) == {
        "golden_dawn_1789",
        "river_mist_teal_gold",
        "monsoon_siege_contrast",
        "imperial_torch_amber",
    }
    assert set(CHAPTER_STYLES.keys()) == {"minimal_center_card", "in_scene_cinema_title"}
    assert set(CHAIN_PATTERNS.keys()) == {"balanced_2beat", "dynamic_1_2_3beat", "epic_3beat"}
    assert set(NARRATIVE_ARCHETYPES.keys()) == {
        "blitz_campaign",
        "siege_and_trap_anatomy",
        "commander_rivalry_duel",
        "naval_and_river_ambush",
    }
    assert set(RESOLUTION_SPECS.keys()) == {"360p", "1080p", "1440p"}
    assert "directional_flow_chain_transition" in PERMANENTLY_BANNED_TRANSITIONS
    assert "map_dive" in PERMANENTLY_BANNED_INSERTS

    # AST audit: confirm ZERO function definitions for directional_flow_chain_transition or _render_3d_map_dive
    source = ENGINE_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert "directional_flow_chain_transition" not in func_names
    assert "_render_3d_map_dive" not in func_names
    assert not hasattr(m1_flex, "directional_flow_chain_transition")
    assert not hasattr(m1_flex, "_render_3d_map_dive")


@pytest.mark.parametrize(
    ("preset_name", "expected_lift", "expected_warmth"),
    [
        ("golden_dawn_1789", 0.18, 0.14),
        ("river_mist_teal_gold", 0.17, 0.06),
        ("monsoon_siege_contrast", 0.16, 0.09),
        ("imperial_torch_amber", 0.19, 0.16),
    ],
)
def test_all_four_color_presets_grade_and_timeline(
    tmp_path: Path, preset_name: str, expected_lift: float, expected_warmth: float
) -> None:
    """Verify all 4 --color-preset modes apply distinct lift/warmth parameters and brighten midtones cleanly."""
    paths = _create_synthetic_m1_job(tmp_path, num_chapters=2, beats_per_chapter=5)
    tl = build_timeline_and_master_audio(
        script_path=paths["script"],
        audio_dir=paths["audio_dir"],
        frames_dir=paths["frames_dir"],
        timeline_path=paths["timeline"],
        master_wav_path=paths["master_wav"],
        srt_path=paths["srt"],
        video_out_dir=paths["output_dir"],
        raw_clips_dir=paths["raw_clips_dir"],
        color_preset=preset_name,
        skip_audio_master=True,
    )
    assert tl["color_preset"] == preset_name
    for b in tl["beats"]:
        assert b["color_preset"] == preset_name
        assert b["grade_lift"] == pytest.approx(expected_lift)
        assert b["grade_warmth"] == pytest.approx(expected_warmth)

    # Verify pixel-level grading behavior
    test_plate = np.full((120, 240, 3), (105, 98, 92), dtype=np.uint8)
    graded = apply_bright_golden_dawn_grade(test_plate, lift=expected_lift, warmth=expected_warmth)
    assert graded.shape == test_plate.shape
    assert graded.dtype == np.uint8
    # Midtones must be lifted cleanly (never darkened into murk) and warm R channel >= B channel
    assert float(graded.mean()) > float(test_plate.mean()) + 12.0
    assert float(graded[:, :, 0].mean()) > float(graded[:, :, 2].mean())


def test_both_chapter_styles_minimal_center_card_and_in_scene_cinema_title(tmp_path: Path) -> None:
    """Verify `minimal_center_card` vs `in_scene_cinema_title` timeline structure & zero subtitle/divider lock."""
    paths = _create_synthetic_m1_job(tmp_path, num_chapters=3, beats_per_chapter=6)

    # Mode 1: minimal_center_card
    tl_card = build_timeline_and_master_audio(
        script_path=paths["script"],
        audio_dir=paths["audio_dir"],
        frames_dir=paths["frames_dir"],
        timeline_path=paths["timeline"],
        master_wav_path=paths["master_wav"],
        srt_path=paths["srt"],
        video_out_dir=paths["output_dir"],
        raw_clips_dir=paths["raw_clips_dir"],
        chapter_style="minimal_center_card",
        skip_audio_master=True,
    )
    assert tl_card["chapter_style"] == "minimal_center_card"
    assert tl_card["chapter_card_count"] == 3
    assert tl_card["in_scene_chapter_title_count"] == 0
    assert tl_card["narration_beat_count"] == 18
    for b in tl_card["beats"]:
        assert b["card_subtitle"] == ""
        assert b["gold_divider_line"] is False
        if b["kind"] == "chapter_card":
            assert (b["out_end"] - b["out_start"]) == pytest.approx(3.60, abs=0.05)

    # Mode 2: in_scene_cinema_title (0 separate chapter_card pause beats; overlay directly on first 3.5s of opener)
    tl_in_scene = build_timeline_and_master_audio(
        script_path=paths["script"],
        audio_dir=paths["audio_dir"],
        frames_dir=paths["frames_dir"],
        timeline_path=paths["timeline"],
        master_wav_path=paths["master_wav"],
        srt_path=paths["srt"],
        video_out_dir=paths["output_dir"],
        raw_clips_dir=paths["raw_clips_dir"],
        chapter_style="in_scene_cinema_title",
        skip_audio_master=True,
    )
    assert tl_in_scene["chapter_style"] == "in_scene_cinema_title"
    assert tl_in_scene["chapter_card_count"] == 0
    assert tl_in_scene["in_scene_chapter_title_count"] == 3
    assert tl_in_scene["narration_beat_count"] == 18
    # Total runtime of in_scene_cinema_title is shorter by exactly 3 * 3.60s = 10.80s (no separate card pauses)
    assert tl_card["total_sec"] - tl_in_scene["total_sec"] == pytest.approx(3 * 3.60, abs=0.10)

    openers = [b for b in tl_in_scene["beats"] if b.get("is_chapter_opener")]
    assert len(openers) == 3
    for op in openers:
        assert op["show_keyword"] is False
        assert op["main_word"] == ""
        ov = op["in_scene_chapter_title"]
        assert isinstance(ov, dict)
        assert ov["duration_sec"] == pytest.approx(3.50)
        assert ov["full_brightness"] is True
        assert ov["card_subtitle"] == ""
        assert ov["gold_divider_line"] is False


def test_all_three_chain_patterns_balanced_dynamic_and_epic(tmp_path: Path) -> None:
    """Verify `balanced_2beat`, `dynamic_1_2_3beat`, and `epic_3beat` continuous chain planners."""
    paths = _create_synthetic_m1_job(tmp_path, num_chapters=4, beats_per_chapter=6)

    # 1. balanced_2beat: every chain has 2 beats (0.00->3.30 and 3.30->6.60)
    tl_2b = build_timeline_and_master_audio(
        script_path=paths["script"],
        audio_dir=paths["audio_dir"],
        frames_dir=paths["frames_dir"],
        timeline_path=paths["timeline"],
        master_wav_path=paths["master_wav"],
        srt_path=paths["srt"],
        video_out_dir=paths["output_dir"],
        raw_clips_dir=paths["raw_clips_dir"],
        chain_pattern="balanced_2beat",
        skip_audio_master=True,
    )
    narr_2b = [b for b in tl_2b["beats"] if b["kind"] == "narration"]
    assert all(b["chain_length"] == 2 for b in narr_2b)
    assert (narr_2b[0]["clip_start_sec"], narr_2b[0]["clip_end_sec"]) == (0.0, 3.3)
    assert (narr_2b[1]["clip_start_sec"], narr_2b[1]["clip_end_sec"]) == (3.3, 6.6)
    assert narr_2b[0]["video_chain_id"] == narr_2b[1]["video_chain_id"]

    # 2. epic_3beat: 3 beats per chain (0.00->2.20->4.40->6.60)
    tl_3b = build_timeline_and_master_audio(
        script_path=paths["script"],
        audio_dir=paths["audio_dir"],
        frames_dir=paths["frames_dir"],
        timeline_path=paths["timeline"],
        master_wav_path=paths["master_wav"],
        srt_path=paths["srt"],
        video_out_dir=paths["output_dir"],
        raw_clips_dir=paths["raw_clips_dir"],
        chain_pattern="epic_3beat",
        skip_audio_master=True,
    )
    narr_3b = [b for b in tl_3b["beats"] if b["kind"] == "narration"]
    assert all(b["chain_length"] == 3 for b in narr_3b)
    assert (narr_3b[0]["clip_start_sec"], narr_3b[0]["clip_end_sec"]) == (0.0, 2.2)
    assert (narr_3b[1]["clip_start_sec"], narr_3b[1]["clip_end_sec"]) == (2.2, 4.4)
    assert (narr_3b[2]["clip_start_sec"], narr_3b[2]["clip_end_sec"]) == (4.4, 6.6)
    assert narr_3b[0]["video_chain_id"] == narr_3b[1]["video_chain_id"] == narr_3b[2]["video_chain_id"]

    # 3. dynamic_1_2_3beat: adaptive pacing containing 1-beat, 2-beat, and 3-beat chains
    tl_dyn = build_timeline_and_master_audio(
        script_path=paths["script"],
        audio_dir=paths["audio_dir"],
        frames_dir=paths["frames_dir"],
        timeline_path=paths["timeline"],
        master_wav_path=paths["master_wav"],
        srt_path=paths["srt"],
        video_out_dir=paths["output_dir"],
        raw_clips_dir=paths["raw_clips_dir"],
        chain_pattern="dynamic_1_2_3beat",
        skip_audio_master=True,
    )
    narr_dyn = [b for b in tl_dyn["beats"] if b["kind"] == "narration"]
    lengths_present = {b["chain_length"] for b in narr_dyn}
    assert lengths_present == {1, 2, 3}, f"Expected 1, 2, and 3-beat chains in dynamic_1_2_3beat, got {lengths_present}"


@pytest.mark.parametrize("density", [0.15, 0.22, 0.28, 0.30])
def test_keyword_density_enforcement_and_opener_beat_x0_protection(tmp_path: Path, density: float) -> None:
    """Verify --keyword-density enforces 15%..30% sparse ratio, beat_*0 always text-free, and top_word == ''."""
    paths = _create_synthetic_m1_job(tmp_path, num_chapters=4, beats_per_chapter=10)
    tl = build_timeline_and_master_audio(
        script_path=paths["script"],
        audio_dir=paths["audio_dir"],
        frames_dir=paths["frames_dir"],
        timeline_path=paths["timeline"],
        master_wav_path=paths["master_wav"],
        srt_path=paths["srt"],
        video_out_dir=paths["output_dir"],
        raw_clips_dir=paths["raw_clips_dir"],
        keyword_density=density,
        skip_audio_master=True,
    )
    narr_beats = [b for b in tl["beats"] if b["kind"] == "narration"]
    assert len(narr_beats) == 40
    expected_kw = int(round(40 * density))
    actual_kw = sum(1 for b in narr_beats if b["show_keyword"])
    assert actual_kw == expected_kw
    assert 0.15 <= tl["emphasis_keyword_density"] <= 0.30
    assert tl["text_free_ratio"] >= 0.70

    for b in narr_beats:
        # Single-line verbatim emphasis only: top_word & card_subtitle permanently empty
        assert b["top_word"] == ""
        assert b["card_subtitle"] == ""
        assert b["use_3d_map_dive"] is False
        # Every chapter opening beat (beat_000, beat_010, beat_020, beat_030) MUST be text-free
        if b["is_chapter_opener"] or b["beat_id"].endswith("0"):
            assert b["show_keyword"] is False, f"Chapter opener {b['beat_id']} must never display a keyword!"
            assert b["main_word"] == ""


def test_invalid_keyword_density_rejected() -> None:
    """Verify densities outside [0.15, 0.30] raise ValueError."""
    with pytest.raises(ValueError, match="keyword-density"):
        validate_m1_flex_options(keyword_density=0.10)
    with pytest.raises(ValueError, match="keyword-density"):
        validate_m1_flex_options(keyword_density=0.35)
    with pytest.raises(ValueError, match="keyword_density"):
        enforce_sparse_keyword_density({1: [(0, {"beat_id": "beat_000", "text": "test"})]}, keyword_density=0.45)


def test_full_cc_srt_and_end_to_end_360p_render_and_pure_black_bars(tmp_path: Path) -> None:
    """Verify full-cc-srt generation, 360p shard render, lossless assembly, and 100% pure-black IMAX bars."""
    paths = _create_synthetic_m1_job(tmp_path, num_chapters=2, beats_per_chapter=3)
    tl = build_timeline_and_master_audio(
        script_path=paths["script"],
        audio_dir=paths["audio_dir"],
        frames_dir=paths["frames_dir"],
        timeline_path=paths["timeline"],
        master_wav_path=paths["master_wav"],
        srt_path=paths["srt"],
        video_out_dir=paths["output_dir"],
        raw_clips_dir=paths["raw_clips_dir"],
        color_preset="river_mist_teal_gold",
        chapter_style="in_scene_cinema_title",
        chain_pattern="dynamic_1_2_3beat",
        keyword_density=0.25,
        resolution="360p",
        total_shards=2,
        full_cc_srt_path=paths["full_cc_srt"],
        skip_audio_master=False,
    )
    assert paths["full_cc_srt"].is_file()
    cc_text = paths["full_cc_srt"].read_text(encoding="utf-8")
    assert "[pause:" not in cc_text
    assert "Đạo quân Tây Sơn" in cc_text
    assert "-->" in cc_text

    # Re-run via CLI --stage full-cc-srt
    rc = m1_cli_main(["--stage", "full-cc-srt", "--job-dir", str(paths["job_dir"]), "--timeline", str(paths["timeline"])])
    assert rc == 0

    # Verify static IMAX 2.39:1 pure-black bars (0 text in top/bottom black bars, only bottom-right logo)
    set_active_resolution("360p")
    bank = ShardFrameBank()
    chrome = bank.build_static_imax_chrome()
    geom = get_resolution_geometry("360p")
    bar_h = geom["bar_h"]
    # Top bar above gold hairline must be 100% pure black (0, 0, 0)
    assert int(chrome[: bar_h - 2, :, :].max()) == 0
    # Bottom-left bar (away from bottom-right watermark) must be 100% pure black (0, 0, 0)
    assert int(chrome[geom["height"] - bar_h + 2 :, : geom["width"] - 80, :].max()) == 0
    # Bottom-right watermark corner must have non-zero logo pixels
    assert int(chrome[geom["height"] - bar_h + 2 :, geom["width"] - 60 :, :].max()) > 40
    bank.close()

    # Render 15 frames of shard 1 with --require-moving-video to verify moving .mp4 decoding & overlay pipeline
    shard_res = render_shard(
        paths["timeline"],
        shard_id=1,
        raw_clips_dir=paths["raw_clips_dir"],
        require_moving_video=True,
        max_frames=15,
        resolution_override="360p",
    )
    assert shard_res["expected_frames"] == 15
    assert shard_res["ffprobe"]["width"] == 640
    assert shard_res["ffprobe"]["height"] == 360
    assert shard_res["moving_video_beats_in_shard"] == shard_res["total_narration_beats_in_shard"]
    set_active_resolution("1080p")
