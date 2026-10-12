import hashlib
import json
import subprocess
import wave
from pathlib import Path
from PIL import Image

PROJ_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_DIR = PROJ_ROOT / "sys" / "exports" / "ancient_humans_bundle"
VIDEO_DIR = PROJ_ROOT / "video"

EXPECTED_CHAPTER_SHOTS = {
    1: 43,
    2: 52,
    3: 46,
    4: 38,
    5: 56,
    6: 50,
    7: 64,
    8: 33,
}

SCENE_START_CUE_INDEX = {
    "SC01": 1, "SC02": 6, "SC03": 10, "SC04": 15,
    "SC05": 1, "SC06": 5, "SC07": 9, "SC08": 17,
    "SC09": 1, "SC10": 4, "SC11": 7, "SC12": 11,
    "SC13": 1, "SC14": 6, "SC15": 13,
    "SC16": 1, "SC17": 5, "SC18": 11, "SC19": 15,
    "SC20": 1, "SC21": 5, "SC22": 8, "SC23": 13,
    "SC24": 1, "SC25": 5, "SC26": 11, "SC27": 15,
    "SC28": 1, "SC29": 6, "SC30": 10,
}


def _collect_chapter_timeline(ch: int) -> list[dict]:
    tpl_path = BUNDLE_DIR / "templates" / f"ch{ch}_props_template.json"
    tpl = json.loads(tpl_path.read_text(encoding="utf-8"))
    scenes = tpl["tracks"]["vi"]["scenesByAspect"]["16:9"]
    timeline = []
    for sc in scenes:
        sc_start = float(sc["start"])
        sc_end = float(sc["end"])
        sc_dur = round(sc_end - sc_start, 3)
        imgs = sc["images"]
        for i, im in enumerate(imgs):
            t0 = float(im["at"])
            t1 = float(imgs[i + 1]["at"]) if i + 1 < len(imgs) else sc_dur
            abs_start = round(sc_start + t0, 3)
            abs_end = round(sc_start + t1, 3)
            timeline.append(
                {
                    "scene_id": sc["id"],
                    "src": im["src"],
                    "abs_start": abs_start,
                    "abs_end": abs_end,
                    "hold": round(t1 - t0, 3),
                }
            )
    return timeline


def test_option_b_templates_and_pacing_invariant():
    """Verify all 8 chapter templates enforce subtitles=false, cue-anchored scenes, and max_hold <= 4.0s across 382 shots."""
    manifest_path = BUNDLE_DIR / "manifest" / "manifest_option_b_full.json"
    assert manifest_path.is_file(), f"Missing manifest {manifest_path}"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(manifest.get("shots", [])) == 382, "Expected 382 shots in manifest_option_b_full.json"

    total_shots = 0
    for ch in range(1, 9):
        tpl_path = BUNDLE_DIR / "templates" / f"ch{ch}_props_template.json"
        wav_path = BUNDLE_DIR / "audio" / f"ch{ch}_narration_spoken.wav"
        cues_path = BUNDLE_DIR / "audio" / f"ch{ch}_spoken_cues.json"
        assert tpl_path.is_file(), f"Missing template {tpl_path}"
        tpl = json.loads(tpl_path.read_text(encoding="utf-8"))
        cues = json.loads(cues_path.read_text(encoding="utf-8"))
        cue_start_by_idx = {int(c["index"]): float(c["start"]) for c in cues if "index" in c}

        with wave.open(str(wav_path), "rb") as wf:
            wav_dur = round(wf.getnframes() / float(wf.getframerate()), 2)
        assert abs(tpl["duration"] - wav_dur) <= 0.05, (
            f"Ch{ch} template duration {tpl['duration']} != spoken WAV duration {wav_dur}"
        )

        for out in tpl.get("outputs", []):
            assert out.get("subtitles") is False, f"Ch{ch} subtitles must be False"

        scenes = tpl["tracks"]["vi"]["scenesByAspect"]["16:9"]
        assert len(scenes) >= 3, f"Ch{ch} expected >=3 scenes"

        ch_shots = 0
        for sc in scenes:
            cue_idx = SCENE_START_CUE_INDEX[sc["id"]]
            expected_start = 0.0 if cue_idx == 1 else round(cue_start_by_idx[cue_idx], 3)
            assert abs(sc["start"] - expected_start) <= 0.01, (
                f"Ch{ch} {sc['id']} start {sc['start']}s != cue {cue_idx} start {expected_start}s"
            )
            sc_dur = round(sc["end"] - sc["start"], 3)
            imgs = sc["images"]
            assert len(imgs) >= 1
            for i, im in enumerate(imgs):
                t0 = im["at"]
                t1 = imgs[i + 1]["at"] if i + 1 < len(imgs) else sc_dur
                hold = round(t1 - t0, 3)
                assert 0.6 <= hold <= 4.0, (
                    f"Ch{ch} scene {sc['id']} shot {im['src']} violates hold invariant: {hold}s"
                )
                ch_shots += 1
                total_shots += 1

        assert ch_shots == EXPECTED_CHAPTER_SHOTS[ch], (
            f"Ch{ch} expected {EXPECTED_CHAPTER_SHOTS[ch]} shots, got {ch_shots}"
        )

    assert total_shots == 382, f"Expected 382 total rendered shots across Ch1-8, got {total_shots}"


def test_every_spoken_cue_has_exact_shot_boundary():
    """Verify all 149 spoken cues across Ch1..8 have an exact shot boundary at cue['start'] (drift <= 0.05s)."""
    cue_map_path = BUNDLE_DIR / "manifest" / "cue_shot_mapping_8ch.json"
    assert cue_map_path.is_file(), f"Missing {cue_map_path}"
    cue_map = json.loads(cue_map_path.read_text(encoding="utf-8"))
    assert cue_map["total_cues"] == 149
    assert cue_map["total_shots"] == 382

    total_cues_checked = 0
    for ch in range(1, 9):
        cues_path = BUNDLE_DIR / "audio" / f"ch{ch}_spoken_cues.json"
        cues = json.loads(cues_path.read_text(encoding="utf-8"))
        timeline = _collect_chapter_timeline(ch)
        shot_starts = [item["abs_start"] for item in timeline]

        for pos, cue in enumerate(cues):
            expected_start = 0.0 if pos == 0 else round(float(cue["start"]), 3)
            min_drift = min(abs(st - expected_start) for st in shot_starts)
            assert min_drift <= 0.05, (
                f"Ch{ch} Cue {cue['index']} at {expected_start}s has no matching shot boundary "
                f"(min_drift={min_drift:.3f}s)"
            )
            total_cues_checked += 1

    assert total_cues_checked == 149


def test_semantic_cue_shot_alignment_invariants():
    """Verify semantic shot placement invariants across Ch1..8 against cue_shot_mapping_8ch.json and templates."""
    cue_map_path = BUNDLE_DIR / "manifest" / "cue_shot_mapping_8ch.json"
    cue_map = json.loads(cue_map_path.read_text(encoding="utf-8"))
    by_ch_cue: dict[tuple[int, int], list[str]] = {}
    for entry in cue_map["cues"]:
        key = (int(entry["chapter_number"]), int(entry["cue_index"]))
        by_ch_cue[key] = [s["target_filename"] for s in entry["shots"]]

    # Ch1: Cue 16 has the modern appliances, Cue 17 has prehistoric vs modern & balance scale
    assert "ch1_blind_beat_30_53.82s.jpg" in by_ch_cue[(1, 16)]
    assert by_ch_cue[(1, 17)] == ["ch1_blind_beat_31_55.27s.jpg", "ch1_blind_beat_32_57.15s.jpg"]
    assert by_ch_cue[(1, 18)] == ["ch1_blind_beat_33_58.97s.jpg", "ch1_blind_beat_33b_60.32s.jpg"]
    assert by_ch_cue[(1, 19)] == ["ch1_blind_beat_34_61.67s.jpg", "ch1_blind_beat_34b_62.96s.jpg"]

    # Ch2: Cue 04 has shot_07, Cue 07 has teeth (shot_14) before spine (shot_13), Cue 11 swaps labels, Cue 13 reveals farmer (shot_35)
    assert "shot_07_79.41s.jpg" in by_ch_cue[(2, 4)]
    c2_7 = by_ch_cue[(2, 7)]
    assert c2_7.index("shot_14_93.83s.jpg") < c2_7.index("shot_13_92.43s.jpg")
    assert "shot_25_118.62s.jpg" in by_ch_cue[(2, 10)]
    assert by_ch_cue[(2, 11)] == ["shot_30_129.90s.jpg", "shot_31_132.10s.jpg"]
    assert "shot_35_147.08s.jpg" in by_ch_cue[(2, 13)]
    assert "shot_33a_135.64s.jpg" in by_ch_cue[(2, 14)]
    assert "shot_33d_141.55s.jpg" in by_ch_cue[(2, 15)]

    # Ch3: Cue 02 has embers, Cue 08-09 has spear/hide/arrow crafting, Cue 11 starts hunting
    assert by_ch_cue[(3, 2)] == ["shot_03a_164.03s.jpg", "shot_06_179.28s.jpg"]
    assert by_ch_cue[(3, 8)] == ["shot_16b_200.67s.jpg", "shot_16c_202.51s.jpg"]
    assert "shot_22_219.62s.jpg" in by_ch_cue[(3, 11)]

    # Ch4: Cue 02 has Ju/'hoansi tribe (shot_03), Cue 11 has 2.4h/day chart (shot_11b)
    assert "shot_03_247.21s.jpg" in by_ch_cue[(4, 2)]
    assert by_ch_cue[(4, 11)] == ["shot_11b_273.50s.jpg"]

    # Ch5: Cue 04 has hair combing, Cue 05 shell beads, Cue 08 Blombos shells, Cue 11 vulture bone flute, Cue 21 bank/hospital/pension
    assert "shot_09a_326.83s.jpg" in by_ch_cue[(5, 4)]
    assert "shot_05_321.09s.jpg" in by_ch_cue[(5, 5)]
    assert "shot_10_330.26s.jpg" in by_ch_cue[(5, 8)]
    assert "shot_13_338.50s.jpg" in by_ch_cue[(5, 11)]
    assert by_ch_cue[(5, 21)] == ["shot_26_384.32s.jpg", "shot_27_386.49s.jpg", "shot_28_387.89s.jpg"]

    # Ch6: Cue 04 has 75% (shot_05a), Cue 06 has 81% (shot_05b), Cue 12 has fire dying (shot_20), Cue 14 has first sleep (shot_21b..d)
    assert "shot_05a_425.83s.jpg" in by_ch_cue[(6, 4)]
    assert "shot_05b_427.65s.jpg" in by_ch_cue[(6, 6)]
    assert "shot_20_460.53s.jpg" in by_ch_cue[(6, 12)]
    assert "shot_21b_464.57s.jpg" in by_ch_cue[(6, 14)]

    # Ch7: Cue 01 has hunter-gatherer schedule only, Cue 05 has calorie yield (shot_08a/b), Cue 12 has Skeleton #2 flashback
    assert by_ch_cue[(7, 1)] == ["shot_01_509.04s.jpg", "shot_02_510.38s.jpg", "shot_25h_579.00s.jpg"]
    assert "shot_08a_525.59s.jpg" in by_ch_cue[(7, 5)]
    assert "shot_36a_607.17s.jpg" in by_ch_cue[(7, 12)]

    # Ch8: Cue 02 has Skeleton #1, Cue 03 has afternoon (shot_05), Cue 05 has agriculture door (shot_07), Cue 09 has pension (shot_10), Cue 11 has waking without alarm (shot_06e)
    assert "shot_04a_623.39s.jpg" in by_ch_cue[(8, 2)]
    assert by_ch_cue[(8, 3)] == ["shot_05_626.83s.jpg"]
    assert "shot_07_637.60s.jpg" in by_ch_cue[(8, 5)]
    assert "shot_10_644.48s.jpg" in by_ch_cue[(8, 9)]
    assert "shot_06e_635.90s.jpg" in by_ch_cue[(8, 11)]


def test_option_b_images_unique_and_genuine_flow_ai():
    """Verify all 382 rendered shots exist, are 1376x768 Flow AI images, have unique MD5s, and have non-fallback JSON sidecars."""
    seen_hashes: dict[str, str] = {}
    for ch in range(1, 9):
        tpl_path = BUNDLE_DIR / "templates" / f"ch{ch}_props_template.json"
        tpl = json.loads(tpl_path.read_text(encoding="utf-8"))
        scenes = tpl["tracks"]["vi"]["scenesByAspect"]["16:9"]
        for sc in scenes:
            for im in sc["images"]:
                img_path = BUNDLE_DIR / "generated_images" / f"ch{ch}" / im["src"]
                sidecar_path = img_path.with_suffix(".json")
                assert img_path.is_file(), f"Missing image {img_path}"
                assert sidecar_path.is_file(), f"Missing sidecar {sidecar_path}"

                with Image.open(img_path) as pil_img:
                    assert pil_img.size == (1376, 768), (
                        f"Non-Flow image dimensions {pil_img.size} at {img_path}"
                    )

                md5 = hashlib.md5(img_path.read_bytes()).hexdigest()
                assert md5 not in seen_hashes, (
                    f"Duplicate MD5 {md5} between {img_path} and {seen_hashes[md5]}"
                )
                seen_hashes[md5] = str(img_path)

                meta = json.loads(sidecar_path.read_text(encoding="utf-8"))
                assert not str(meta.get("media_id", "")).startswith("gen-"), (
                    f"Synthetic placeholder media_id detected in {sidecar_path}"
                )
                prompt = str(meta.get("prompt", ""))
                assert prompt and not prompt.startswith("Stick figure illustration for Chapter"), (
                    f"Dummy fallback prompt detected in {sidecar_path}: {prompt}"
                )

    assert len(seen_hashes) == 382


def test_adam_spoken_audio_and_cues_present():
    """Verify all 8 chapters have Adam spoken WAV audio and cues JSON."""
    for ch in range(1, 9):
        wav_path = BUNDLE_DIR / "audio" / f"ch{ch}_narration_spoken.wav"
        cues_path = BUNDLE_DIR / "audio" / f"ch{ch}_spoken_cues.json"
        assert wav_path.is_file() and wav_path.stat().st_size > 5_000_000, f"Invalid WAV {wav_path}"
        assert cues_path.is_file(), f"Missing cues {cues_path}"
        cues = json.loads(cues_path.read_text(encoding="utf-8"))
        assert len(cues) >= 10, f"Too few cues in {cues_path}"


def test_rendered_chapter_and_master_videos_ffprobe():
    """Verify all 8 chapter MP4s, master 12m MP4, and master SRT are newer than templates and valid via ffprobe."""
    total_ch_dur = 0.0
    for ch in range(1, 9):
        tpl_path = BUNDLE_DIR / "templates" / f"ch{ch}_props_template.json"
        mp4 = VIDEO_DIR / f"ancient-humans-day-ch{ch}-16x9" / f"ancient-humans-day-ch{ch}-16x9_r1_final.mp4"
        assert mp4.is_file() and mp4.stat().st_size > 10_000_000, f"Invalid MP4 {mp4}"
        assert mp4.stat().st_mtime >= tpl_path.stat().st_mtime, (
            f"Stale render cache detected for Ch{ch}: mp4 mtime ({mp4.stat().st_mtime:.1f}) "
            f"< template mtime ({tpl_path.stat().st_mtime:.1f})"
        )
        probe = json.loads(
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration,size:stream=codec_name,width,height,r_frame_rate",
                    "-of",
                    "json",
                    str(mp4),
                ],
                text=True,
            )
        )
        v_streams = [s for s in probe["streams"] if s.get("width")]
        a_streams = [s for s in probe["streams"] if s.get("codec_name") == "aac"]
        assert v_streams and v_streams[0]["codec_name"] == "h264"
        assert v_streams[0]["width"] == 1920 and v_streams[0]["height"] == 1080
        assert a_streams and a_streams[0]["codec_name"] == "aac"
        dur = float(probe["format"]["duration"])
        assert dur > 60.0
        total_ch_dur += dur

    master_mp4 = VIDEO_DIR / "ancient_humans_full_11m_final.mp4"
    assert master_mp4.is_file() and master_mp4.stat().st_size > 150_000_000
    newest_tpl_mtime = max(
        (BUNDLE_DIR / "templates" / f"ch{ch}_props_template.json").stat().st_mtime
        for ch in range(1, 9)
    )
    assert master_mp4.stat().st_mtime >= newest_tpl_mtime, (
        "Stale master MP4 detected: older than chapter templates"
    )
    m_probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration,size:stream=codec_name,width,height,r_frame_rate",
                "-of",
                "json",
                str(master_mp4),
            ],
            text=True,
        )
    )
    m_dur = float(m_probe["format"]["duration"])
    assert abs(m_dur - total_ch_dur) < 1.0

    srt_path = VIDEO_DIR / "ancient_humans_full_11m.srt"
    assert srt_path.is_file() and srt_path.stat().st_size > 5_000


def test_zero_legacy_bridge_terminology():
    """Verify legacy bridge directory and terminology are completely absent from the repository."""
    import re
    legacy_dir = PROJ_ROOT / "sys" / ("flow" + "kit")
    assert not legacy_dir.exists(), f"Legacy directory must not exist: {legacy_dir}"
    pat = re.compile("flow" + r"[_ -]?kit", re.IGNORECASE)
    for sub in ("sys/flow_cdp", "sys/tools", "sys/scripts", ".agents/skills"):
        target = PROJ_ROOT / sub
        for fpath in target.rglob("*"):
            if not fpath.is_file() or "__pycache__" in str(fpath):
                continue
            assert not pat.search(fpath.name), f"Legacy filename detected: {fpath}"
            txt = fpath.read_text(encoding="utf-8", errors="ignore")
            assert not pat.search(txt), f"Legacy terminology detected inside {fpath}"

