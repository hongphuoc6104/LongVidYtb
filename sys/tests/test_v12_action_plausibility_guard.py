"""Unit tests for V12 Action Plausibility Guard & Motion Library Integration."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
from flow_video.motion_library import build_timecoded_video_prompt
from fx_warehouse.v12_action_plausibility_guard import (
    COMPOSED_FACIAL_EXPRESSION_LOCK,
    DIGNIFIED_HAND_LOCK,
    MOTION_STRIP_SAMPLE_RATIOS,
    VIDEO_PHYSICAL_PLAUSIBILITY_ANCHOR,
    audit_clip_motion_plausibility,
    render_clip_8frame_motion_strip,
    sanitize_action_and_gesture_prompt,
)
from PIL import Image


def _nice_ffmpeg_cmd(args: list[str]) -> list[str]:
    ffmpeg_bin = shutil.which("ffmpeg")
    assert ffmpeg_bin is not None
    nice_bin = shutil.which("nice")
    base = [nice_bin, "-n", "15", ffmpeg_bin] if nice_bin else [ffmpeg_bin]
    return [*base, "-y", "-v", "error", "-threads", "1", *args]


def test_sanitize_eating_and_drinking_into_mouth() -> None:
    risky = (
        "Palace attendant drinking from a celadon teacup and raising wine cup to his lips "
        "while soldier is eating rice balls in torchlight"
    )
    res = sanitize_action_and_gesture_prompt(risky, mode="image")
    out_low = res["sanitized_prompt"].lower()

    assert res["changed"] is True
    assert "eating_drinking" in res["triggered_categories"]
    assert "drinking from" not in out_low
    assert "to his lips" not in out_low
    assert "eating rice" not in out_low
    assert "holding vessel steady" in out_low or "resting vessel" in out_low
    assert "wooden table" in out_low

    # Stationary teacup prop on floor/tray must NOT be falsely rewritten
    clean_prop = (
        "Extreme macro close-up of a cracked celadon porcelain teacup tipped sideways "
        "on a dark oiled ironwood floor mat"
    )
    clean_res = sanitize_action_and_gesture_prompt(clean_prop, mode="image")
    assert clean_res["is_clean_input"] is True
    assert clean_res["changed"] is False
    assert clean_res["sanitized_prompt"] == clean_prop


@pytest.mark.parametrize(
    "gesture_phrase",
    [
        "court official pointing finger toward bamboo scroll",
        "royal eunuch pressing finger on lips in dark corridor",
        "quartermaster counting on fingers beside wooden crates",
        "scholar sitting with intertwined fingers over lacquer desk",
    ],
)
def test_sanitize_complex_multi_finger_gestures(gesture_phrase: str) -> None:
    res = sanitize_action_and_gesture_prompt(gesture_phrase, mode="image")
    out_low = res["sanitized_prompt"].lower()

    assert res["changed"] is True
    assert "complex_finger_gesture" in res["triggered_categories"]
    assert DIGNIFIED_HAND_LOCK.lower() in out_low
    assert "calm open palm resting on" in out_low
    for banned in ("pointing finger", "finger on lips", "counting on fingers", "intertwined fingers"):
        assert banned not in out_low


@pytest.mark.parametrize(
    "chaotic_phrase",
    [
        "soldiers locked in tangled multi-body melee in muddy trench",
        "warrior performing acrobatics and backflips over palisade",
        "spearman spinning rapidly across stone courtyard",
        "infantryman backwards walking up steep mountain pass",
        "messenger walking backwards through wooden gate",
    ],
)
def test_sanitize_tangled_melee_acrobatics_spinning_and_backwards_walking(
    chaotic_phrase: str,
) -> None:
    res = sanitize_action_and_gesture_prompt(chaotic_phrase, mode="image")
    out_low = res["sanitized_prompt"].lower()

    assert res["changed"] is True
    assert "chaotic_multi_body_or_acrobatics" in res["triggered_categories"]
    assert (
        "structured unidirectional formation movement" in out_low
        or "crisp single-subject framing" in out_low
    )

    # Craft noun 'wooden spinning wheel' must remain untouched
    loom_res = sanitize_action_and_gesture_prompt(
        "Quiet village hearth with an antique wooden spinning wheel beside hemp baskets",
        mode="image",
    )
    assert loom_res["is_clean_input"] is True
    assert "wooden spinning wheel" in loom_res["sanitized_prompt"]


def test_sanitize_exaggerated_grimacing_shouting_crying_and_open_mouth() -> None:
    noisy = (
        "General with exaggerated grimacing, shouting orders and crying hysterically "
        "with mouth opening wide in rainstorm"
    )
    res = sanitize_action_and_gesture_prompt(noisy, mode="image")
    out = res["sanitized_prompt"]
    out_low = out.lower()

    assert res["changed"] is True
    assert res["enforced_facial_lock"] is True
    assert "exaggerated_facial_or_open_mouth" in res["triggered_categories"]
    assert COMPOSED_FACIAL_EXPRESSION_LOCK.lower() in out_low
    for banned in ("grimacing", "shouting", "crying", "mouth opening"):
        assert banned not in out_low
    # Adjacent duplicate facial locks must collapse cleanly into a single occurrence
    assert out_low.count("composed, historically dignified facial expression") == 1


@pytest.mark.parametrize(
    ("modern_item", "expected_period_anchor"),
    [
        ("eyeglasses", "unadorned natural eyes"),
        ("wristwatch", "silk bracer"),
        ("metal buttons", "cloth-knotted ties"),
        ("zippers", "silk sash fastening"),
        ("modern salute", "clasped-fist bow"),
        ("handshake", "clasped-hand greeting"),
        ("modern book spine", "bamboo-slip scroll"),
        ("ballpoint pen", "bamboo calligraphy brush"),
        ("glass window panes", "wooden lattice shutters"),
    ],
)
def test_sanitize_all_nine_modern_anachronisms(
    modern_item: str,
    expected_period_anchor: str,
) -> None:
    raw = f"15th-century Đại Việt envoy with {modern_item} inside wooden hall"
    res = sanitize_action_and_gesture_prompt(raw, mode="image")
    out_low = res["sanitized_prompt"].lower()

    assert res["changed"] is True
    assert "modern_anachronism" in res["triggered_categories"]
    assert modern_item not in out_low
    assert expected_period_anchor.lower() in out_low


def test_video_physical_anchor_idempotency_and_env_sensory_hygiene() -> None:
    base = "Commander standing beside lacquered wooden command table"
    vid_res = sanitize_action_and_gesture_prompt(base, mode="video")
    assert vid_res["appended_anchor"] is True
    assert vid_res["sanitized_prompt"].endswith(VIDEO_PHYSICAL_PLAUSIBILITY_ANCHOR)

    # Second pass on already-sanitized video prompt must be strictly idempotent
    second_res = sanitize_action_and_gesture_prompt(vid_res["sanitized_prompt"], mode="video")
    assert second_res["changed"] is False
    assert second_res["appended_anchor"] is False
    assert second_res["is_clean_input"] is True
    assert second_res["sanitized_prompt"] == vid_res["sanitized_prompt"]
    assert second_res["sanitized_prompt"].count("Grounded real-world physics") == 1

    # ENV_SENSORY zero-human hygiene: never inject human hand/face clauses
    env_res = sanitize_action_and_gesture_prompt(
        "Sealed pavilion interior with pointing finger shadow, NO human figures anywhere",
        mode="image",
        shot_class="ENV_SENSORY",
    )
    assert "five-fingered hands" not in env_res["sanitized_prompt"].lower()
    assert "no human figures anywhere" in env_res["sanitized_prompt"].lower()

    with pytest.raises(ValueError, match="Unsupported mode"):
        sanitize_action_and_gesture_prompt("test", mode="invalid_mode")


def test_motion_library_wires_action_plausibility_guard_cleanly() -> None:
    for model_name, dur in (("veo_3_1_lite", 6), ("omni_flash", 6), ("macaron_cookie_i2v_fl_10s", 10)):
        prompt = build_timecoded_video_prompt(
            camera_move="push_in",
            hero_subject="attendant pressing finger on lips while drinking teacup with wristwatch",
            setting="candlelit wooden chamber with glass window panes",
            model=model_name,
            clip_duration_sec=dur,
            transition_mode="seam",
            secondary_motion="guards shouting in tangled multi-body melee",
            has_person=True,
            lens_spec="35mm anamorphic film lens",
        )
        low = prompt.lower()
        assert VIDEO_PHYSICAL_PLAUSIBILITY_ANCHOR in prompt
        assert "finger on lips" not in low
        assert "drinking teacup" not in low
        assert "wristwatch" not in low
        assert "glass window panes" not in low
        assert "tangled multi-body melee" not in low
        assert "shouting" not in low
        assert DIGNIFIED_HAND_LOCK.lower() in low
        assert COMPOSED_FACIAL_EXPRESSION_LOCK.lower() in low
        assert "tactile prop impact" not in low
        assert "forge, write, or grip weapons" not in low

    # Verify 4s Omni 1.2 quiet court prompt emits Measured tactile micro-motion with zero weapon/impact leak
    quiet_4s = build_timecoded_video_prompt(
        camera_move="push_in",
        hero_subject="cracked celadon porcelain teacup on dark oiled ironwood floor",
        setting="sealed Le Chi Vien wooden pavilion",
        model="omni_flash",
        clip_duration_sec=4,
        transition_mode="seam",
        has_person=True,
        shot_class="MACRO_PROP",
    )
    assert "Measured tactile micro-motion and crisp optical focus (macro_prop)" in quiet_4s
    assert "impact" not in quiet_4s.lower()
    assert "weapons" not in quiet_4s.lower()
    assert "mud" not in quiet_4s.lower()
    assert (
        "Natural, grounded single-action physical motion with closed mouths (zero lip-flap, zero speech), "
        "anatomically natural five-fingered hands, real gravity and weight, "
        "one continuous unbroken camera take with zero internal cuts, and zero mid-clip prop morphing."
    ) in quiet_4s

    # Legacy pre-authored impact/weapon boilerplate is also healed by sanitize_action_and_gesture_prompt
    legacy_buggy = (
        "[0-2.6s] Snappy 100mm kinetic micro-action captures immediate physical impact on celadon cup "
        "as hands forge, write, or grip weapons and tools, bodies move through mud or terrain with real weight."
    )
    healed = sanitize_action_and_gesture_prompt(legacy_buggy, mode="video")
    assert "Measured tactile micro-motion and crisp optical focus" in healed["sanitized_prompt"]
    assert "impact" not in healed["sanitized_prompt"].lower()
    assert "grip weapons" not in healed["sanitized_prompt"].lower()


def test_audit_clip_motion_plausibility_and_8frame_strip(tmp_path: Path) -> None:
    # 1. Missing file check
    missing_res = audit_clip_motion_plausibility(tmp_path / "does_not_exist.mp4")
    assert missing_res["passed"] is False
    assert "missing_or_empty_video" in missing_res["anomalies"]

    # 2. Clean smooth continuous motion clip -> PASS
    clean_mp4 = tmp_path / "clean_motion.mp4"
    subprocess.run(
        _nice_ffmpeg_cmd(
            [
                "-f",
                "lavfi",
                "-i",
                "color=c=#1e2430:s=256x192:r=24:d=2.0",
                "-f",
                "lavfi",
                "-i",
                "color=c=#d89b3c:s=64x80:r=24:d=2.0",
                "-filter_complex",
                "[0:v][1:v]overlay=x='16+t*75':y=56:shortest=1[outv]",
                "-filter_threads",
                "1",
                "-map",
                "[outv]",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-threads",
                "1",
                str(clean_mp4),
            ]
        ),
        check=True,
        capture_output=True,
    )
    clean_audit = audit_clip_motion_plausibility(clean_mp4)
    assert clean_audit["passed"] is True, clean_audit
    assert clean_audit["status"] == "PASS"
    assert clean_audit["anomalies"] == []
    assert clean_audit["ffmpeg_threads"] == 1
    assert clean_audit["ffmpeg_nice_level"] == 15
    assert clean_audit["scan_resolution"] == "256x192"

    # 3. Mid-clip AI flash / morph spike clip -> catches frame_jump_spike (> 4.2x median)
    spike_mp4 = tmp_path / "morph_spike.mp4"
    subprocess.run(
        _nice_ffmpeg_cmd(
            [
                "-f",
                "lavfi",
                "-i",
                "color=c=#1e2430:s=256x192:r=24:d=2.0",
                "-f",
                "lavfi",
                "-i",
                "color=c=#c88a32:s=60x80:r=24:d=2.0",
                "-filter_complex",
                (
                    "[0:v][1:v]overlay=x='16+t*65':y=56:shortest=1,"
                    "drawbox=enable='eq(n,24)':x=0:y=0:w=iw:h=ih:color=white@1.0:t=fill[outv]"
                ),
                "-filter_threads",
                "1",
                "-map",
                "[outv]",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-threads",
                "1",
                str(spike_mp4),
            ]
        ),
        check=True,
        capture_output=True,
    )
    spike_audit = audit_clip_motion_plausibility(spike_mp4)
    assert spike_audit["passed"] is False, spike_audit
    assert "frame_jump_spike" in spike_audit["anomalies"]
    assert spike_audit["metrics"]["max_spike_ratio"] > 4.2
    assert len(spike_audit["metrics"]["spike_frame_indices"]) >= 1

    # 4. Severe border oscillation / edge flicker warping clip -> catches edge_flicker_warping
    flicker_mp4 = tmp_path / "edge_flicker.mp4"
    subprocess.run(
        _nice_ffmpeg_cmd(
            [
                "-f",
                "lavfi",
                "-i",
                "color=c=#222834:s=256x192:r=24:d=1.5",
                "-f",
                "lavfi",
                "-i",
                "color=c=#b87d2e:s=56x72:r=24:d=1.5",
                "-filter_complex",
                (
                    "[0:v][1:v]overlay=x='20+t*60':y=60:shortest=1,"
                    "drawbox=enable='mod(n,2)':x=0:y=0:w=iw:h=ih:color=#f5f5f5@1.0:t=24[outv]"
                ),
                "-filter_threads",
                "1",
                "-map",
                "[outv]",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-threads",
                "1",
                str(flicker_mp4),
            ]
        ),
        check=True,
        capture_output=True,
    )
    flicker_audit = audit_clip_motion_plausibility(flicker_mp4)
    assert flicker_audit["passed"] is False, flicker_audit
    assert "edge_flicker_warping" in flicker_audit["anomalies"]
    assert flicker_audit["metrics"]["edge_flicker_score"] > 3.0

    # 5. Dead frozen stretch clip -> catches dead_frozen_stretch
    frozen_mp4 = tmp_path / "dead_frozen.mp4"
    subprocess.run(
        _nice_ffmpeg_cmd(
            [
                "-f",
                "lavfi",
                "-i",
                "color=c=#1c222d:s=256x192:r=24:d=0.6",
                "-f",
                "lavfi",
                "-i",
                "color=c=#cfa044:s=60x80:r=24:d=0.6",
                "-filter_complex",
                (
                    "[0:v][1:v]overlay=x='10+t*80':y=50:shortest=1,"
                    "tpad=stop_mode=clone:stop_duration=1.6[outv]"
                ),
                "-filter_threads",
                "1",
                "-map",
                "[outv]",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-threads",
                "1",
                str(frozen_mp4),
            ]
        ),
        check=True,
        capture_output=True,
    )
    frozen_audit = audit_clip_motion_plausibility(frozen_mp4)
    assert frozen_audit["passed"] is False, frozen_audit
    assert "dead_frozen_stretch" in frozen_audit["anomalies"]
    assert frozen_audit["metrics"]["max_frozen_stretch_sec"] >= 1.1

    # 6. Render 8-frame horizontal motion strip (`t=2%, 16%, 30%, 44%, 58%, 72%, 86%, 97%`)
    strip_png = tmp_path / "clean_8frame_strip.png"
    strip_info = render_clip_8frame_motion_strip(clean_mp4, strip_png, tile_height=192)
    assert strip_png.is_file()
    assert strip_png.stat().st_size > 500
    assert strip_info["sample_ratios"] == list(MOTION_STRIP_SAMPLE_RATIOS)
    assert strip_info["sample_ratios"] == [0.02, 0.16, 0.30, 0.44, 0.58, 0.72, 0.86, 0.97]
    assert len(strip_info["sampled_frame_indices"]) == 8
    assert strip_info["sampled_frame_indices"] == sorted(strip_info["sampled_frame_indices"])
    assert len(set(strip_info["sampled_frame_indices"])) == 8

    with Image.open(strip_png) as im:
        assert im.size == (strip_info["strip_width"], strip_info["strip_height"])
        assert im.size[0] == 8 * strip_info["tile_width"]
        arr = np.asarray(im.convert("RGB"), dtype=np.float32)

    tw = strip_info["tile_width"]
    first_tile = arr[:, :tw, :]
    last_tile = arr[:, 7 * tw : 8 * tw, :]
    # Moving golden box shifts horizontally from left to right across the 8 chronological tiles
    assert float(np.mean(np.abs(last_tile - first_tile))) > 5.0
