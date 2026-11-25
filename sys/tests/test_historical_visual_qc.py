"""Unit & Integration Tests for `sys/fx_warehouse/historical_visual_qc.py`.

Validates:
1. `audit_and_sanitize_historical_prompt`:
   - 60+ anti-anachronism, anti-fog, story-frame zero-text, and `PROMINENT_PEOPLE` rules.
   - Era-aware gating (`musket`/`cannon` before 1400 vs allowed in 1400+ Hồ & 1789 Tây Sơn).
   - Faction + era gating (`qing queue` / `manchu robe` strictly restricted to 1788-1789 Qing forces).
   - Period-accurate positive armor/weapon + clear-air optical anchor injection & idempotency.
2. `audit_sub_cut_crop_geometry`:
   - Exact `[x0, y0, x1, y1]` visible crop math across `1.25x..1.40x` sub-cuts.
   - Auto-correction of `focus_cx, focus_cy` preventing upper head (`0.18..0.46`) severance
     and `MarginV=660` subtitle collision.
3. `audit_rendered_2k_frame`:
   - Resolution, `< 2MB` strict thumbnail gate, dynamic range (`p95 - p5 >= 85`),
     black-crush/overexposure clipping %, Laplacian sharpness, and `W-w-36:H-h-36` /
     `MarginV=660` readability contrast.
4. `audit_full_episode_visual_readiness`:
   - End-to-end Short `9:16` and Long `16:9` episode directory readiness checks (clean & failing)
     plus read-only verification on `video/vn_su_ke_lai_v7_bach_dang_1288_short` when present.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from fx_warehouse.historical_visual_qc import (
    HISTORICAL_ANACHRONISM_CATALOG,
    MAX_THUMBNAIL_BYTES,
    audit_and_sanitize_historical_prompt,
    audit_full_episode_visual_readiness,
    audit_rendered_2k_frame,
    audit_sub_cut_crop_geometry,
)
from PIL import Image


def _make_crisp_cinema_image(
    width: int = 1440,
    height: int = 2560,
    *,
    seed: int = 42,
) -> Image.Image:
    """Synthesize a crisp chiaroscuro 2K test frame with strong edges and rich dynamic range."""
    rng = np.random.default_rng(seed)
    yy = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]
    xx = np.linspace(0.0, 1.0, width, dtype=np.float32)[None, :]

    # Caravaggio directional gradient + sharp architectural / spear grid detail
    base = 24.0 + 165.0 * (1.0 - yy) * (0.35 + 0.65 * xx)
    # Keep subtitle zone (0.63..0.75) richly textured dark-earth tone for high caption contrast
    sub_mask = (yy >= 0.60) & (yy <= 0.80)
    base = np.where(sub_mask, base * 0.55 + 18.0, base)

    # Crisp high-frequency edge bars (simulating lamellar scales / wooden stakes)
    stripes = (((np.floor(xx * 96.0) + np.floor(yy * 96.0)) % 2) * 42.0).astype(np.float32)
    grain = rng.normal(0.0, 6.0, size=(height, width)).astype(np.float32)
    luma = np.clip(base + stripes + grain, 6.0, 244.0)

    rgb = np.stack(
        [
            np.clip(luma * 1.06, 0, 255),
            np.clip(luma * 0.96, 0, 255),
            np.clip(luma * 0.84, 0, 255),
        ],
        axis=2,
    ).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB")


# ---------------------------------------------------------------------------
# 1. Prompt Anachronism Sanitizer & Anchor Injection Tests
# ---------------------------------------------------------------------------


def test_catalog_contains_over_40_distinct_anachronism_rules() -> None:
    assert len(HISTORICAL_ANACHRONISM_CATALOG) >= 60
    unique_ids = {r.token_id for r in HISTORICAL_ANACHRONISM_CATALOG}
    assert len(unique_ids) == len(HISTORICAL_ANACHRONISM_CATALOG)


def test_prompt_strips_samurai_viking_european_plate_and_injects_anchors() -> None:
    dirty_prompt = (
        "Epic wide shot of a samurai general wearing a kabuto and European plate armor "
        "fighting a Viking warrior in a horned helmet and medieval knight wielding a katana "
        "and claymore beside a gothic castle."
    )
    res = audit_and_sanitize_historical_prompt(dirty_prompt, dynasty_era="ly_1077", faction="dai_viet")

    assert res["passed"] is False
    assert res["is_clean"] is False
    for banned in ("katana", "kabuto", "samurai", "viking", "horned_helmet", "european_plate", "knight", "claymore"):
        assert banned in res["stripped_tokens"]

    san_low = res["sanitized_prompt"].lower()
    for word in ("katana", "kabuto", "samurai", "viking", "horned helmet", "european plate", "knight", "claymore"):
        assert word not in san_low

    # Positive 11th-century Lý Dynasty armor/weapon + clear-air + no-text anchors injected
    assert len(res["injected_anchors"]) >= 1
    assert "lamellar" in san_low
    assert "no text" in san_low

    # Idempotence: re-auditing sanitized prompt passes with 0 violations and 0 re-injections
    res2 = audit_and_sanitize_historical_prompt(res["sanitized_prompt"], dynasty_era="ly_1077", faction="dai_viet")
    assert res2["passed"] is True
    assert res2["violations"] == []
    assert res2["stripped_tokens"] == []
    assert res2["injected_anchors"] == []


def test_prompt_era_gated_musket_and_cannon_rules() -> None:
    # Pre-1400 (1288 Trần Dynasty): both musket and cannon are anachronistic
    p_1288 = "Soldiers firing muskets and bronze cannons from river wooden galleys."
    r_1288 = audit_and_sanitize_historical_prompt(p_1288, dynasty_era="tran_1288", faction="dai_viet")
    assert r_1288["passed"] is False
    assert "musket" in r_1288["stripped_tokens"]
    assert "cannon_pre1400" in r_1288["stripped_tokens"]
    assert "musket" not in r_1288["sanitized_prompt"].lower()

    # 1402 Hồ Dynasty (Hồ Nguyên Trừng Súng Thần Cơ): bronze cannon is historically accurate!
    p_1402 = (
        "Hồ Nguyên Trừng inspecting heavy cast bronze cannons and iron lamellar armor "
        "atop Đa Bang citadel, Shot on 35mm Kodak Vision3 500T film, crisp optical clarity, no text."
    )
    r_1402 = audit_and_sanitize_historical_prompt(p_1402, dynasty_era="ho_1402", faction="dai_viet")
    assert r_1402["passed"] is True
    assert "cannon_pre1400" not in r_1402["stripped_tokens"]

    # 1789 Tây Sơn: muskets & bronze cannons are historically accurate
    p_1789 = (
        "Tây Sơn troops with lacquered leather cuirass, wet straw shields, muskets, and bronze cannons "
        "charging at dawn, Shot on 35mm Kodak Vision3 500T film, crisp optical clarity, no text."
    )
    r_1789 = audit_and_sanitize_historical_prompt(p_1789, dynasty_era="tay_son_1789", faction="dai_viet")
    assert r_1789["passed"] is True
    assert r_1789["stripped_tokens"] == []


def test_prompt_qing_queue_allowed_only_for_1789_qing_faction() -> None:
    base_qing_desc = (
        "Soldiers with shaved-forehead Qing queue and Manchu robes in iron lamellar armor, "
        "Shot on 35mm Kodak Vision3 500T film, crisp optical clarity, no text."
    )
    # 1. Stripped for Đại Việt troops even in 1789
    r_dv_1789 = audit_and_sanitize_historical_prompt(base_qing_desc, dynasty_era="1789", faction="dai_viet")
    assert r_dv_1789["passed"] is False
    assert "qing_queue" in r_dv_1789["stripped_tokens"]
    assert "manchu_robe" in r_dv_1789["stripped_tokens"]

    # 2. Stripped in 1077 Northern Song even if caller mistakenly passes qing tokens
    r_song_1077 = audit_and_sanitize_historical_prompt(base_qing_desc, dynasty_era="1077", faction="northern_song")
    assert r_song_1077["passed"] is False
    assert "qing_queue" in r_song_1077["stripped_tokens"]

    # 3. Allowed ONLY when era is Qing/1789 AND faction is Qing
    r_qing_1789 = audit_and_sanitize_historical_prompt(base_qing_desc, dynasty_era="1789", faction="qing")
    assert r_qing_1789["passed"] is True
    assert r_qing_1789["stripped_tokens"] == []


def test_prompt_strips_fog_story_text_and_prominent_people_while_allowing_thumbnail_text() -> None:
    polluted = (
        "Commander played by Donnie Yen alongside Jet Li and Chân Tử Đan in lacquered lamellar armor "
        "marching through river mist, dense battlefield mist, and drifting gunsmoke fog with "
        "bold uppercase title lettering reading 'ĐẠI THẮNG BẠCH ĐẰNG', Shot on 35mm film."
    )
    res_story = audit_and_sanitize_historical_prompt(
        polluted, dynasty_era="tran_1288", faction="dai_viet", is_thumbnail=False
    )
    assert res_story["passed"] is False
    assert len(res_story["fog_tokens_stripped"]) == 3
    assert len(res_story["prominent_people_flagged"]) >= 3
    assert res_story["text_request_stripped"] is True

    san = res_story["sanitized_prompt"].lower()
    assert "donnie yen" not in san
    assert "jet li" not in san
    assert "river mist" not in san
    assert "dense battlefield mist" not in san
    assert "drifting gunsmoke fog" not in san
    assert "đại thắng bạch đằng" not in san

    # Thumbnail mode MUST allow 2-4 uppercase word Flow-native poster lettering
    thumb_prompt = (
        "Full-frame 9:16 35mm cinema poster, bold antique-gold title lettering reading exactly "
        "\"BẪY TRIỀU BẠCH ĐẰNG\" in upper sky, Trần Hưng Đạo in iron lamellar armor below, crisp optical clarity."
    )
    res_thumb = audit_and_sanitize_historical_prompt(
        thumb_prompt, dynasty_era="tran_1288", faction="dai_viet", is_thumbnail=True
    )
    assert res_thumb["passed"] is True
    assert res_thumb["text_request_stripped"] is False
    assert "BẪY TRIỀU BẠCH ĐẰNG" in res_thumb["sanitized_prompt"]


def test_prompt_preserves_explicit_negative_locks_and_disambiguates_duration_years() -> None:
    clean_with_negations = (
        "28mm anamorphic shot over Như Nguyệt river in 1077, Lý Dynasty troops in iron lamellar armor, "
        "Shot on 35mm Kodak Vision3 500T film, crisp optical clarity, zero blanket river mist, "
        "no neon/cyberpunk HUD, no samurai katana, no text."
    )
    res_clean = audit_and_sanitize_historical_prompt(
        clean_with_negations, dynasty_era="1000_nam_ly_1077", faction="dai_viet"
    )
    assert res_clean["passed"] is True
    assert res_clean["resolved_year"] == 1077
    assert res_clean["stripped_tokens"] == []
    assert "no samurai katana" in res_clean["sanitized_prompt"]

    # Non-negated katana after an unrelated 'no fear' phrase MUST still be caught!
    tricky = "Fierce warrior with no fear wielding a katana in river mist."
    res_tricky = audit_and_sanitize_historical_prompt(tricky, dynasty_era="tran_1288", faction="dai_viet")
    assert res_tricky["passed"] is False
    assert "katana" in res_tricky["stripped_tokens"]
    assert "river_mist" in res_tricky["stripped_tokens"]

    # Historical monarch 'Tran Thanh Tong' must NEVER false-match celebrity 'Trấn Thành'
    monarch_prompt = (
        "Emperor Tran Thanh Tong and Emperor Tran Nhan Tong in silk ao giao linh robes "
        "inside Thang Long palace, Shot on 35mm Kodak Vision3 500T film, crisp optical clarity, no text."
    )
    res_monarch = audit_and_sanitize_historical_prompt(monarch_prompt, dynasty_era="tran_1288")
    assert res_monarch["passed"] is True
    assert res_monarch["prominent_people_flagged"] == []
    assert "Tran Thanh Tong" in res_monarch["sanitized_prompt"]


# ---------------------------------------------------------------------------
# 2. Sub-Cut Crop Geometry & Auto-Correction Tests
# ---------------------------------------------------------------------------


def test_sub_cut_crop_geometry_valid_v7_framing() -> None:
    res = audit_sub_cut_crop_geometry(
        width=1440,
        height=2560,
        focus_zoom=1.32,
        focus_cx=0.50,
        focus_cy=0.34,
        subtitle_margin_v=660,
    )
    assert res["passed"] is True
    assert res["was_corrected"] is False
    assert res["head_severed"] is False
    assert res["subtitle_collision"] is False

    x0, y0, x1, y1 = res["crop_rect"]
    assert 0 < x0 < x1 < 1440
    assert 0 < y0 < y1 < 2560
    assert (x1 - x0) == round(1440 / 1.32)
    assert (y1 - y0) == round(2560 / 1.32)
    # Upper head zone [0.18..0.46] is completely inside normalized crop rect
    assert res["crop_rect_norm"][1] <= 0.18
    assert res["crop_rect_norm"][3] >= 0.46


def test_sub_cut_crop_auto_repairs_severed_head_and_subtitle_collision() -> None:
    # Case A: focus_cy=0.85 at 1.38x decapitates upper head zone (0.18..0.46)
    severed = audit_sub_cut_crop_geometry(
        width=1440,
        height=2560,
        focus_zoom=1.38,
        focus_cx=0.92,
        focus_cy=0.85,
        subtitle_margin_v=660,
    )
    assert severed["passed"] is False
    assert severed["head_severed"] is True
    assert "UPPER_HEAD_ZONE_SEVERED" in severed["issues"]
    assert "HORIZONTAL_SAFE_ZONE_CLIPPED" in severed["issues"]
    assert severed["was_corrected"] is True

    # Re-auditing the auto-corrected coordinates passes 100%
    recheck_a = audit_sub_cut_crop_geometry(
        width=1440,
        height=2560,
        focus_zoom=severed["corrected_focus_zoom"],
        focus_cx=severed["corrected_focus_cx"],
        focus_cy=severed["corrected_focus_cy"],
        subtitle_margin_v=660,
    )
    assert recheck_a["passed"] is True
    assert recheck_a["corrected_crop_rect_norm"][1] <= 0.18
    assert recheck_a["corrected_crop_rect_norm"][3] >= 0.46

    # Case B: focus_cy=0.02 + out-of-bounds zoom=1.60 pushes face down into subtitle zone
    sub_hit = audit_sub_cut_crop_geometry(
        width=1080,
        height=1920,
        focus_zoom=1.60,
        focus_cx=0.50,
        focus_cy=0.02,
        subtitle_margin_v=660,
    )
    assert sub_hit["passed"] is False
    assert sub_hit["subtitle_collision"] is True
    assert "ZOOM_OUT_OF_SUBCUT_RANGE" in sub_hit["issues"]
    assert "SUBTITLE_COLLISION_RISK" in sub_hit["issues"]
    assert sub_hit["corrected_focus_zoom"] == 1.40

    recheck_b = audit_sub_cut_crop_geometry(
        width=1080,
        height=1920,
        focus_zoom=sub_hit["corrected_focus_zoom"],
        focus_cx=sub_hit["corrected_focus_cx"],
        focus_cy=sub_hit["corrected_focus_cy"],
        subtitle_margin_v=660,
    )
    assert recheck_b["passed"] is True
    assert recheck_b["head_screen_y_span_after_fix"][1] <= recheck_b["subtitle_top_screen_norm"] + 1e-4


# ---------------------------------------------------------------------------
# 3. Rendered 2K Frame & Thumbnail Quality Gate Tests
# ---------------------------------------------------------------------------


def test_rendered_2k_frame_passes_crisp_cinema_and_catches_fog_blur_crush_and_2mb(tmp_path: Path) -> None:
    good_frame = tmp_path / "beat_00.jpg"
    _make_crisp_cinema_image(1440, 2560).save(good_frame, format="JPEG", quality=92)
    r_good = audit_rendered_2k_frame(good_frame, is_thumbnail=False)
    assert r_good["passed"] is True
    assert r_good["dynamic_range"] >= 85.0
    assert r_good["laplacian_variance"] >= 25.0
    assert r_good["watermark_zone"]["position_spec"] == "W-w-36:H-h-36"
    assert r_good["subtitle_zone"]["outlined_effective_contrast"] >= 4.5

    # Washed-out murky fog frame (low dynamic range < 85 & low sharpness)
    fog_arr = np.full((1920, 1080, 3), 165, dtype=np.uint8)
    fog_arr[:400, :, :] = 185  # p95 - p5 = 20 << 85
    fog_path = tmp_path / "fog_whiteout.png"
    Image.fromarray(fog_arr, mode="RGB").save(fog_path)
    r_fog = audit_rendered_2k_frame(fog_path, is_thumbnail=False)
    assert r_fog["passed"] is False
    assert "WASHED_OUT_LOW_DYNAMIC_RANGE" in r_fog["issues"]
    assert "BLURRY_LOW_LAPLACIAN_SHARPNESS" in r_fog["issues"]

    # Severe black crush (> 45% near-black pixels)
    crush_arr = np.zeros((1080, 1920, 3), dtype=np.uint8)
    crush_arr[:120, :, :] = 220
    crush_path = tmp_path / "black_crush.png"
    Image.fromarray(crush_arr, mode="RGB").save(crush_path)
    r_crush = audit_rendered_2k_frame(crush_path, is_thumbnail=False)
    assert r_crush["passed"] is False
    assert "SEVERE_BLACK_CRUSH" in r_crush["issues"]

    # Severe overexposure + subtitle glare
    over_arr = np.full((1920, 1080, 3), 254, dtype=np.uint8)
    over_arr[:180, :, :] = 20
    over_path = tmp_path / "overexposed.png"
    Image.fromarray(over_arr, mode="RGB").save(over_path)
    r_over = audit_rendered_2k_frame(over_path, is_thumbnail=False)
    assert r_over["passed"] is False
    assert "SEVERE_OVEREXPOSURE_CLIPPING" in r_over["issues"]
    assert "SUBTITLE_ZONE_BLOWN_GLARE" in r_over["issues"]

    # Thumbnail strict < 2MB gate: noise PNG > 2MB fails as thumbnail, passes as story frame
    rng = np.random.default_rng(7)
    heavy_arr = rng.integers(5, 250, size=(1440, 1080, 3), dtype=np.uint8)
    heavy_png = tmp_path / "heavy_poster.png"
    Image.fromarray(heavy_arr, mode="RGB").save(heavy_png, format="PNG", compress_level=0)
    assert heavy_png.stat().st_size >= MAX_THUMBNAIL_BYTES

    r_thumb_fail = audit_rendered_2k_frame(heavy_png, is_thumbnail=True)
    assert r_thumb_fail["passed"] is False
    assert "THUMBNAIL_EXCEEDS_2MB" in r_thumb_fail["issues"]

    r_story_ok = audit_rendered_2k_frame(heavy_png, is_thumbnail=False)
    assert "THUMBNAIL_EXCEEDS_2MB" not in r_story_ok["issues"]

    # Missing file
    r_missing = audit_rendered_2k_frame(tmp_path / "does_not_exist.png", is_thumbnail=False)
    assert r_missing["passed"] is False
    assert r_missing["issues"] == ["FILE_NOT_FOUND"]


# ---------------------------------------------------------------------------
# 4. Full-Episode Readiness Gate Tests (Short 9:16, Long 16:9 & Live V7 Spec)
# ---------------------------------------------------------------------------


def test_full_episode_readiness_short_and_long_specs(tmp_path: Path) -> None:
    # 1. Clean Short 9:16 Episode Directory
    short_dir = tmp_path / "vn_su_ke_lai_test_1288_short"
    frames_dir = short_dir / "frames"
    frames_dir.mkdir(parents=True)

    _make_crisp_cinema_image(1080, 1920, seed=1).save(frames_dir / "beat_00.jpg", quality=90)
    _make_crisp_cinema_image(1080, 1920, seed=2).save(short_dir / "thumbnail_9x16.jpg", quality=88)

    clean_short_spec = {
        "job_id": "vn_su_ke_lai_test_1288_short",
        "format_profile": "v7_model_twin_short",
        "resolution": "1440x2560",
        "subtitle_margin_v": 660,
        "thumbnail_spec": {
            "prompt": (
                "Full-frame 9:16 35mm cinema poster, bold gold title lettering reading exactly "
                "\"BẪY CỌC 1288\" in upper sky, Trần commander in lacquered iron lamellar armor below, "
                "crisp optical clarity."
            )
        },
        "beats": [
            {
                "beat_id": "B00",
                "prompt": (
                    "Trần Dynasty vanguard commander in dark lacquered lamellar armor gripping an "
                    "iron-tipped spear on a wooden river galley, Shot on 35mm Kodak Vision3 500T film, "
                    "crisp optical clarity, no text, no watermarks."
                ),
                "sub_cut_ratio": 0.48,
                "focus_zoom": 1.32,
                "focus_cx": 0.50,
                "focus_cy": 0.34,
            }
        ],
    }
    (short_dir / "short_spec.json").write_text(json.dumps(clean_short_spec), encoding="utf-8")

    rep_clean = audit_full_episode_visual_readiness(short_dir)
    assert rep_clean["passed"] is True
    assert rep_clean["format_profile"] == "short_9x16"
    assert rep_clean["summary"]["frames_audited"] == 1
    assert rep_clean["summary"]["thumbnails_audited"] == 1
    assert rep_clean["blocking_issues"] == []

    # 2. Clean Long 16:9 Episode Directory with Cold Open + Chapters + 1789 Qing Faction Beat
    long_dir = tmp_path / "vn_su_ke_lai_v10_1789_long"
    long_dir.mkdir(parents=True)
    _make_crisp_cinema_image(1920, 1080, seed=3).save(long_dir / "thumbnail_16x9.jpg", quality=88)

    clean_long_spec = {
        "job_id": "vn_su_ke_lai_v10_1789_long",
        "format_profile": "long_16x9",
        "resolution": "1920x1080",
        "cold_open": {
            "beats": [
                {
                    "beat_id": "CO_01",
                    "prompt": (
                        "Emperor Quang Trung in crimson cloth war tunic and lacquered leather cuirass "
                        "atop an armored war elephant, bronze cannons gleaming, Shot on 35mm Kodak Vision3 "
                        "500T film, crisp optical clarity, no text."
                    ),
                }
            ]
        },
        "chapters": [
            {
                "chapter_id": "ch_01",
                "beats": [
                    {
                        "beat_id": "B_QING_01",
                        "hero_subject": "Qing commander Tôn Sĩ Nghị and Manchu bannermen",
                        "prompt": (
                            "Qing general Tôn Sĩ Nghị and Eight Banners troops with shaved-forehead Qing queue "
                            "in iron-studded dingjia brigandine armor inside Thăng Long camp, Shot on 35mm film, "
                            "crisp optical clarity, no text."
                        ),
                    }
                ],
            }
        ],
    }
    (long_dir / "long_spec.json").write_text(json.dumps(clean_long_spec), encoding="utf-8")

    rep_long = audit_full_episode_visual_readiness(long_dir / "long_spec.json")
    assert rep_long["passed"] is True
    assert rep_long["format_profile"] == "long_16x9"
    assert rep_long["summary"]["total_beats"] == 2

    # 3. Failing Episode Directory catching prompt, crop, and fog-frame defects simultaneously
    bad_dir = tmp_path / "vn_su_ke_lai_bad_1077_short"
    (bad_dir / "frames").mkdir(parents=True)
    fog_img = np.full((1920, 1080, 3), 170, dtype=np.uint8)
    Image.fromarray(fog_img, mode="RGB").save(bad_dir / "frames" / "beat_00.png")
    bad_spec = {
        "job_id": "vn_su_ke_lai_bad_1077_short",
        "beats": [
            {
                "beat_id": "B00",
                "prompt": "Samurai with katana in dense battlefield mist played by Donnie Yen",
                "sub_cut_ratio": 0.5,
                "focus_zoom": 1.38,
                "focus_cx": 0.5,
                "focus_cy": 0.88,
            }
        ],
    }
    (bad_dir / "short_spec.json").write_text(json.dumps(bad_spec), encoding="utf-8")

    rep_bad = audit_full_episode_visual_readiness(bad_dir)
    assert rep_bad["passed"] is False
    assert rep_bad["summary"]["prompt_violations_count"] == 1
    assert rep_bad["summary"]["crop_violations_count"] == 1
    assert rep_bad["summary"]["frame_failures_count"] == 1
    assert len(rep_bad["blocking_issues"]) >= 3


def test_real_v7_bach_dang_1288_episode_passes_readiness_if_present() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    v7_dir = repo_root / "video" / "vn_su_ke_lai_v7_bach_dang_1288_short"
    if not (v7_dir / "short_spec.json").is_file():
        assert not v7_dir.is_file()
        return

    report = audit_full_episode_visual_readiness(v7_dir)
    assert report["passed"] is True, f"Unexpected blocking issues: {report['blocking_issues']}"
    assert report["summary"]["total_beats"] == 20
    assert report["summary"]["prompt_violations_count"] == 0
    assert report["summary"]["crop_violations_count"] == 0
    assert report["summary"]["frame_failures_count"] == 0
    assert report["summary"]["thumbnail_failures_count"] == 0
