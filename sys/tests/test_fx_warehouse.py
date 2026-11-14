"""Unit tests for sys/fx_warehouse modular sub-warehouses, v2 shards, and bespoke synthesis."""
from __future__ import annotations

import json
import subprocess
import wave
from pathlib import Path

import numpy as np
import pytest
from fx_warehouse import (
    ARCHETYPE_PROFILES,
    BGM_CATALOG,
    BGM_DIR,
    CAMERA_MOTION_CATALOG,
    CHANNEL_ARCHETYPE_MAP,
    CHANNEL_BESPOKE_RULES,
    FORENSIC_HUD_V2_CATALOG,
    FPS,
    HUD_WIDGET_CATALOG,
    PAUSE_TIER_DURATIONS,
    SFX_CATALOG,
    SFX_DIR,
    STATIC_CAMERA_HUDS,
    TARGET_SR,
    VARIANT_PROFILES,
    VERIFIED_MAP_ANCHORS_2K,
    VFX_SHADER_CATALOG,
    add_vhf_cockpit_bed,
    apply_stereo_pan,
    apply_vhf_radio_texture,
    auto_select_beat_fx,
    build_bespoke_topic_hud_patch,
    build_suspense_audio_mix,
    compose_4act_tension_bgm,
    compute_voice_envelope_30fps,
    encode_calibrated_m4a_stereo,
    ensure_warehouse_audio_assets,
    get_camera_motion,
    get_vfx_shader,
    master_2pass_wav_stereo,
    measure_ebur128,
    place_stereo_sfx,
    register_bespoke_camera_motion,
    register_bespoke_hud_widget,
    register_bespoke_vfx_shader,
    render_forensic_hud_v2,
    render_hud_widget_patch,
    resolve_niche_fx_blueprint,
    set_font_dir,
    synth_air_leak_turbulence,
    synth_boeing_737_warning_horn,
    synth_chapter_stinger,
    synth_master_caution_chime,
    synth_riser_to_subdrop,
    synthesize_bespoke_topic_sfx,
)
from fx_warehouse.archetypes import (
    ARCHETYPE_PROFILES as SUB_ARCHETYPE_PROFILES,
)
from fx_warehouse.archetypes import (
    CHANNEL_ARCHETYPE_MAP as SUB_CHANNEL_ARCHETYPE_MAP,
)
from fx_warehouse.archetypes import (
    CHANNEL_BESPOKE_RULES as SUB_CHANNEL_BESPOKE_RULES,
)
from fx_warehouse.archetypes import (
    resolve_niche_fx_blueprint as sub_resolve_niche_fx_blueprint,
)
from fx_warehouse.audio_sfx_bgm import (
    BGM_CATALOG as SUB_BGM_CATALOG,
)
from fx_warehouse.audio_sfx_bgm import (
    SFX_CATALOG as SUB_SFX_CATALOG,
)
from fx_warehouse.audio_sfx_bgm import (
    ensure_warehouse_audio_assets as sub_ensure_warehouse_audio_assets,
)
from fx_warehouse.audio_sfx_bgm import (
    synthesize_bespoke_topic_sfx as sub_synthesize_bespoke_topic_sfx,
)
from fx_warehouse.audio_suspense_v2 import (
    FPS as SUB_FPS,
)
from fx_warehouse.audio_suspense_v2 import (
    VARIANT_PROFILES as SUB_VARIANT_PROFILES,
)
from fx_warehouse.audio_suspense_v2 import (
    build_suspense_audio_mix as sub_build_suspense_audio_mix,
)
from fx_warehouse.audio_suspense_v2 import (
    compose_4act_tension_bgm as sub_compose_4act_tension_bgm,
)
from fx_warehouse.audio_suspense_v2 import (
    encode_calibrated_m4a_stereo as sub_encode_calibrated_m4a_stereo,
)
from fx_warehouse.audio_suspense_v2 import (
    synth_boeing_737_warning_horn as sub_synth_boeing_737_warning_horn,
)
from fx_warehouse.camera_vfx import (
    CAMERA_MOTION_CATALOG as SUB_CAMERA_MOTION_CATALOG,
)
from fx_warehouse.camera_vfx import (
    VFX_SHADER_CATALOG as SUB_VFX_SHADER_CATALOG,
)
from fx_warehouse.camera_vfx import (
    register_bespoke_camera_motion as sub_register_bespoke_camera_motion,
)
from fx_warehouse.camera_vfx import (
    register_bespoke_vfx_shader as sub_register_bespoke_vfx_shader,
)
from fx_warehouse.hud_forensic_v2 import (
    FORENSIC_HUD_V2_CATALOG as SUB_FORENSIC_HUD_V2_CATALOG,
)
from fx_warehouse.hud_forensic_v2 import (
    VERIFIED_MAP_ANCHORS_2K as SUB_VERIFIED_MAP_ANCHORS_2K,
)
from fx_warehouse.hud_forensic_v2 import (
    render_forensic_hud_v2 as sub_render_forensic_hud_v2,
)
from fx_warehouse.hud_widgets import (
    HUD_WIDGET_CATALOG as SUB_HUD_WIDGET_CATALOG,
)
from fx_warehouse.hud_widgets import (
    build_bespoke_topic_hud_patch as sub_build_bespoke_topic_hud_patch,
)
from fx_warehouse.hud_widgets import (
    register_bespoke_hud_widget as sub_register_bespoke_hud_widget,
)
from fx_warehouse.hud_widgets import (
    render_hud_widget_patch as sub_render_hud_widget_patch,
)
from fx_warehouse.selector import (
    PAUSE_TIER_DURATIONS as SUB_PAUSE_TIER_DURATIONS,
)
from fx_warehouse.selector import (
    STATIC_CAMERA_HUDS as SUB_STATIC_CAMERA_HUDS,
)
from fx_warehouse.selector import (
    auto_select_beat_fx as sub_auto_select_beat_fx,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_20_CHANNELS = {
    "ai_binh_dan",
    "ban_do_quyen_luc",
    "banh_rang",
    "chanh_niem_ke",
    "co_the_ke",
    "dia_com",
    "ho_so_ky_la",
    "la_ban_hoc_thuat",
    "loi_sang_soi",
    "luat_doi_thuong",
    "luat_ngam",
    "minh_triet_song",
    "nao_luoi",
    "nghe_song_sot",
    "su_ke_lai",
    "tam_tinh_dem",
    "thuong_cho_kheo",
    "tui_tien",
    "ua_sao_vay",
    "vu_tru_ti_hon",
}


def test_sharded_subwarehouse_imports_match_top_level_facade() -> None:
    assert SUB_ARCHETYPE_PROFILES is ARCHETYPE_PROFILES
    assert SUB_CHANNEL_ARCHETYPE_MAP is CHANNEL_ARCHETYPE_MAP
    assert SUB_CHANNEL_BESPOKE_RULES is CHANNEL_BESPOKE_RULES
    assert sub_resolve_niche_fx_blueprint is resolve_niche_fx_blueprint
    assert SUB_CAMERA_MOTION_CATALOG is CAMERA_MOTION_CATALOG
    assert SUB_VFX_SHADER_CATALOG is VFX_SHADER_CATALOG
    assert sub_register_bespoke_camera_motion is register_bespoke_camera_motion
    assert sub_register_bespoke_vfx_shader is register_bespoke_vfx_shader
    assert SUB_HUD_WIDGET_CATALOG is HUD_WIDGET_CATALOG
    assert sub_render_hud_widget_patch is render_hud_widget_patch
    assert sub_build_bespoke_topic_hud_patch is build_bespoke_topic_hud_patch
    assert sub_register_bespoke_hud_widget is register_bespoke_hud_widget
    assert SUB_SFX_CATALOG is SFX_CATALOG
    assert SUB_BGM_CATALOG is BGM_CATALOG
    assert sub_ensure_warehouse_audio_assets is ensure_warehouse_audio_assets
    assert sub_synthesize_bespoke_topic_sfx is synthesize_bespoke_topic_sfx
    assert sub_auto_select_beat_fx is auto_select_beat_fx
    assert SUB_STATIC_CAMERA_HUDS is STATIC_CAMERA_HUDS
    assert SUB_PAUSE_TIER_DURATIONS is PAUSE_TIER_DURATIONS
    assert SUB_FORENSIC_HUD_V2_CATALOG is FORENSIC_HUD_V2_CATALOG
    assert SUB_VERIFIED_MAP_ANCHORS_2K is VERIFIED_MAP_ANCHORS_2K
    assert sub_render_forensic_hud_v2 is render_forensic_hud_v2
    assert SUB_FPS == FPS
    assert SUB_VARIANT_PROFILES is VARIANT_PROFILES
    assert sub_compose_4act_tension_bgm is compose_4act_tension_bgm
    assert sub_synth_boeing_737_warning_horn is synth_boeing_737_warning_horn
    assert sub_build_suspense_audio_mix is build_suspense_audio_mix
    assert sub_encode_calibrated_m4a_stereo is encode_calibrated_m4a_stereo
    for sym in (
        add_vhf_cockpit_bed,
        apply_stereo_pan,
        apply_vhf_radio_texture,
        compute_voice_envelope_30fps,
        master_2pass_wav_stereo,
        measure_ebur128,
        place_stereo_sfx,
        set_font_dir,
        synth_air_leak_turbulence,
        synth_chapter_stinger,
        synth_master_caution_chime,
        synth_riser_to_subdrop,
    ):
        assert callable(sym)


def test_all_20_channels_mapped_to_5_archetypes_with_bespoke_policy() -> None:
    assert len(ARCHETYPE_PROFILES) == 5
    for arch_id, profile in ARCHETYPE_PROFILES.items():
        policy = profile.get("bespoke_synthesis_policy", "")
        assert isinstance(policy, str) and len(policy.strip()) >= 15, (
            f"Archetype {arch_id} missing valid bespoke_synthesis_policy"
        )

    assert set(CHANNEL_ARCHETYPE_MAP.keys()) == EXPECTED_20_CHANNELS
    for ch, arch_id in CHANNEL_ARCHETYPE_MAP.items():
        assert arch_id in ARCHETYPE_PROFILES, f"{ch} mapped to invalid archetype {arch_id}"
        ch_rule = CHANNEL_BESPOKE_RULES.get(ch, {})
        assert isinstance(ch_rule.get("bespoke_synthesis_policy"), str) and len(ch_rule["bespoke_synthesis_policy"]) >= 15
        bp = resolve_niche_fx_blueprint(ch, video_topic="chủ đề đặc thù")
        assert bp["archetype_id"] == arch_id
        assert len(bp["bespoke_synthesis_policy"]) >= 15


def test_catalog_counts_and_valid_audio_wavs_on_disk() -> None:
    assert len(CAMERA_MOTION_CATALOG) == 8
    assert len(HUD_WIDGET_CATALOG) == 14
    assert len(VFX_SHADER_CATALOG) == 7
    assert len(SFX_CATALOG) == 25
    assert len(BGM_CATALOG) == 5

    for name in SFX_CATALOG:
        p = SFX_DIR / name
        assert p.is_file() and p.stat().st_size > 1024, f"Missing or tiny SFX WAV: {p}"
        with wave.open(str(p), "rb") as wf:
            assert wf.getframerate() == TARGET_SR
            assert wf.getnframes() > 1000

    for name in BGM_CATALOG:
        p = BGM_DIR / name
        assert p.is_file() and p.stat().st_size > 4096, f"Missing or tiny BGM WAV: {p}"
        with wave.open(str(p), "rb") as wf:
            assert wf.getframerate() == TARGET_SR
            assert wf.getnchannels() == 2
            assert wf.getnframes() >= TARGET_SR


def test_cross_niche_dynamic_selection_from_shared_warehouse() -> None:
    split_fx = auto_select_beat_fx("So sánh hai danh mục đầu tư trước và sau 10 năm", channel_id="tui_tien")
    assert split_fx["hud"] == "laser_split_screen"
    assert split_fx["sfx"] == "laser_split_whoosh.wav"

    route_fx = auto_select_beat_fx("Quỹ đạo tàu chở dầu đi qua eo biển trên bản đồ", channel_id="ban_do_quyen_luc")
    assert route_fx["hud"] == "radar_bezier_trajectory"
    assert route_fx["sfx"] == "radar_sonar_ping.wav"

    stat_fx = auto_select_beat_fx("Lạm phát tăng thêm 12,5% chỉ trong một năm", channel_id="banh_rang")
    assert stat_fx["hud"] == "altitude_stat_counter"
    assert stat_fx["sfx"] == "sub_bass_boom.wav"

    tri_fx = auto_select_beat_fx("Ba mắt xích sai lầm nối tiếp nhau trong hồ sơ vụ án", channel_id="ho_so_ky_la")
    assert tri_fx["hud"] == "triptych_3col_evidence"
    assert tri_fx["sfx"] == "card_lock_thud.wav"

    mind_fx = auto_select_beat_fx("Hít thở chậm lại trong tĩnh lặng đêm khuya", channel_id="chanh_niem_ke")
    assert mind_fx["camera"] == "breathing_drift"
    assert mind_fx["hud"] == "calligraphy_quote_dissolve"
    assert mind_fx["sfx"] == "singing_bowl_zen.wav"


def test_archetype_comfort_guardrail_and_override() -> None:
    calm_fx = auto_select_beat_fx("Thảm họa mất kiểm soát của tâm trí", channel_id="chanh_niem_ke")
    assert calm_fx["vfx"] not in ("camera_shake_impulse", "crimson_strobe_alert")

    forced = auto_select_beat_fx(
        "Thảm họa mất kiểm soát",
        channel_id="chanh_niem_ke",
        overrides={"vfx": "camera_shake_impulse"},
    )
    assert forced["vfx"] == "camera_shake_impulse"


def test_render_all_14_hud_widgets_produce_valid_rgba_patches() -> None:
    for widget_id in HUD_WIDGET_CATALOG:
        res = render_hud_widget_patch(widget_id, {}, t_beat=0.45, dur=2.5, amp=0.5)
        assert res is not None, f"{widget_id} returned None at t_beat=0.45"
        x0, y0, img = res
        assert isinstance(x0, int) and isinstance(y0, int)
        assert img.mode == "RGBA"
        assert img.width >= 50 and img.height >= 40


def test_bespoke_hud_patch_and_procedural_sfx_synthesis(tmp_path: Path) -> None:
    # 1. All 5 bespoke HUD kinds synthesize valid RGBA patches
    for kind in ("metric_meter", "timeline_nodes", "comparison_matrix", "sonar_radial", "telemetry_card"):
        x0, y0, img = build_bespoke_topic_hud_patch(
            {
                "kind": kind,
                "theme": "dark",
                "kicker": "BESPOKE TEST",
                "headline": "Ngộ độc thủy ngân trên tàu ngầm",
                "subline": "Phân tích độc chất chuyên biệt",
                "value": 84.5,
                "nodes": ["01. ĐỘC TỐ", "02. HẤP THU", "03. TÁC ĐỘNG"],
            },
            t_beat=0.5,
            dur=3.0,
            amp=0.4,
        )
        assert isinstance(x0, int) and isinstance(y0, int)
        assert img.mode == "RGBA"
        assert img.width >= 400 and img.height >= 120

    # 2. Bespoke procedural SFX synthesis produces valid 48kHz stereo WAVs
    for idx, profile in enumerate(("maritime_sonar", "historical_resonance", "cosmic_shimmer", "zen_bowl", "doodle_pop", "forensic_pulse")):
        out_wav = tmp_path / f"bespoke_{idx}_{profile}.wav"
        meta = synthesize_bespoke_topic_sfx(
            {"topic": f"topic_{profile}", "profile": profile, "dur": 0.6},
            output_path=out_wav,
            seed=100 + idx,
        )
        assert meta["is_bespoke"] is True
        assert meta["sample_rate"] == TARGET_SR
        assert meta["channels"] == 2
        assert out_wav.is_file() and out_wav.stat().st_size > 4096
        with wave.open(str(out_wav), "rb") as wf:
            assert wf.getframerate() == TARGET_SR
            assert wf.getnchannels() == 2
            assert wf.getnframes() >= int(0.55 * TARGET_SR)


def test_auto_select_beat_fx_bespoke_routing_and_registration(tmp_path: Path) -> None:
    # Unmapped domain topic without preset keywords routes dynamically to bespoke_topic_hud
    fx_bespoke = auto_select_beat_fx(
        "Cấu trúc cọc gỗ ngầm dưới lòng sông Bạch Đằng khi thủy triều rút",
        channel_id="su_ke_lai",
        video_topic="Trận Bạch Đằng thủy triều cọc gỗ",
        allow_bespoke=True,
    )
    assert fx_bespoke["is_bespoke"] is True
    assert fx_bespoke["hud"] == "bespoke_topic_hud"
    assert "bespoke_hud_spec" in fx_bespoke and fx_bespoke["bespoke_hud_spec"]["is_bespoke"] is True
    assert "bespoke_sfx_spec" in fx_bespoke and fx_bespoke["bespoke_sfx_spec"]["is_bespoke"] is True

    # Render the generated bespoke_hud_spec and synthesize bespoke_sfx_spec end-to-end
    x0, y0, patch = build_bespoke_topic_hud_patch(fx_bespoke["bespoke_hud_spec"], t_beat=0.4, dur=2.5)
    assert isinstance(x0, int) and isinstance(y0, int) and patch.mode == "RGBA"
    wav_info = synthesize_bespoke_topic_sfx(fx_bespoke["bespoke_sfx_spec"], output_path=tmp_path / "bach_dang.wav")
    assert Path(wav_info["path"]).is_file()

    # Disabling allow_bespoke suppresses bespoke synthesis
    fx_no_bespoke = auto_select_beat_fx(
        "Cấu trúc cọc gỗ ngầm dưới lòng sông Bạch Đằng khi thủy triều rút",
        channel_id="su_ke_lai",
        video_topic="Trận Bạch Đằng thủy triều cọc gỗ",
        allow_bespoke=False,
    )
    assert fx_no_bespoke["is_bespoke"] is False
    assert "bespoke_hud_spec" not in fx_no_bespoke

    # Custom registration helpers work for camera, VFX, and HUD
    cam_entry = register_bespoke_camera_motion("test_bespoke_cam", z0=1.02, z1=1.07, x1=0.02, promote=False)
    assert cam_entry["is_bespoke"] is True
    assert get_camera_motion("test_bespoke_cam")["z1"] == 1.07

    vfx_entry = register_bespoke_vfx_shader("test_bespoke_vfx", intensity="high", params={"vignette": 0.25}, promote=False)
    assert vfx_entry["is_bespoke"] is True
    assert get_vfx_shader("test_bespoke_vfx")["params"]["vignette"] == 0.25

    hud_entry = register_bespoke_hud_widget("test_bespoke_hud", spec={"kind": "telemetry_card"}, promote=False)
    assert hud_entry["is_bespoke"] is True


def test_vp_motion_fx_warehouse_skill_and_cross_links_exist() -> None:
    skill_dir = REPO_ROOT / ".agents" / "skills" / "vp-motion-fx-warehouse"
    skill_md = skill_dir / "SKILL.md"
    ref_catalog = skill_dir / "references" / "sub-warehouse-catalog.md"
    ref_rules = skill_dir / "references" / "niche-bespoke-synthesis-rules.md"

    assert skill_md.is_file(), f"Missing {skill_md}"
    assert ref_catalog.is_file(), f"Missing {ref_catalog}"
    assert ref_rules.is_file(), f"Missing {ref_rules}"

    linked_files = [
        REPO_ROOT / ".agents" / "skills" / "vp-channel-ho-so-ky-la" / "SKILL.md",
        REPO_ROOT / ".agents" / "skills" / "vp-channel-ban-do-quyen-luc" / "SKILL.md",
        REPO_ROOT / ".agents" / "skills" / "vp-channel-su-ke-lai" / "SKILL.md",
        REPO_ROOT / ".agents" / "skills" / "vp-full-frame-quality" / "SKILL.md",
        REPO_ROOT / ".agents" / "skills" / "vp-production" / "SKILL.md",
        REPO_ROOT / ".agents" / "skills" / "vp-production" / "references" / "cinematography.md",
        REPO_ROOT / "sys" / "docs" / "render-capabilities.md",
    ]
    for path in linked_files:
        assert path.is_file(), f"Missing linked doc: {path}"
        content = path.read_text(encoding="utf-8")
        assert "vp-motion-fx-warehouse" in content, f"{path} does not link vp-motion-fx-warehouse"


def test_selector_static_camera_locks_and_suspense_metadata() -> None:
    # Radar, split, and triptych beats lock camera strictly to static_clean
    radar_fx = auto_select_beat_fx("Quỹ đạo bay qua biển Aegean đến Athens trên radar", channel_id="ho_so_ky_la")
    assert radar_fx["hud"] == "radar_bezier_trajectory"
    assert radar_fx["camera"] == "static_clean"
    assert radar_fx["camera_params"]["z0"] == 1.0 and radar_fx["camera_params"]["z1"] == 1.0
    assert radar_fx["camera_params"]["parallax_amp"] == 0.0
    assert radar_fx["hud_v2_hint"] == "calibrated_radar_overlay"
    assert radar_fx["pause_tier"] in PAUSE_TIER_DURATIONS
    assert radar_fx["recommended_pause_sec"] == PAUSE_TIER_DURATIONS[radar_fx["pause_tier"]]

    split_fx = auto_select_beat_fx("So sánh 737 Classic và NG thế hệ mới", channel_id="ho_so_ky_la")
    assert split_fx["hud"] == "laser_split_screen"
    assert split_fx["camera"] == "static_clean"
    assert split_fx["hud_v2_hint"] == "classic_vs_ng_compare"

    triptych_fx = auto_select_beat_fx("Ba mắt xích sai lầm xuyên qua lỗ hổng", channel_id="ho_so_ky_la")
    assert triptych_fx["hud"] == "triptych_3col_evidence"
    assert triptych_fx["camera"] == "static_clean"
    assert triptych_fx["hud_v2_hint"] == "swiss_cheese_align"

    # Explicit HUD override into STATIC_CAMERA_HUDS still locks camera unless caller overrides camera
    cal_fx = auto_select_beat_fx(
        "Cập nhật trạng thái chuyến bay",
        channel_id="ho_so_ky_la",
        overrides={"hud": "calibrated_radar_overlay"},
    )
    assert cal_fx["camera"] == "static_clean"
    assert cal_fx["hud_v2_hint"] == "calibrated_radar_overlay"

    # Explicit camera override still wins if caller intentionally unlocks it
    unlocked = auto_select_beat_fx(
        "Bản đồ Athens",
        channel_id="ho_so_ky_la",
        overrides={"camera": "parallax_push_in"},
    )
    assert unlocked["camera"] == "parallax_push_in"

    # Suspense pause tiers & selective hud_v2_hint behavior
    horn_fx = auto_select_beat_fx("Còi báo động nhầm tần số vang lên trong buồng lái", channel_id="ho_so_ky_la")
    assert horn_fx["hud_v2_hint"] == "dual_horn_pulse"
    assert horn_fx["pause_tier"] == "T2"
    assert horn_fx["recommended_pause_sec"] == PAUSE_TIER_DURATIONS["T2"]

    hypoxia_fx = auto_select_beat_fx("Thiếu oxy não khiến TUC chỉ còn 60 giây trong hộp đen", channel_id="ho_so_ky_la")
    assert hypoxia_fx["hud_v2_hint"] == "hypoxia_tuc_meter"
    assert hypoxia_fx["pause_tier"] == "T3"
    assert hypoxia_fx["recommended_pause_sec"] == PAUSE_TIER_DURATIONS["T3"]

    calm_fx = auto_select_beat_fx("Hít thở chậm lại trong tĩnh lặng đêm khuya", channel_id="chanh_niem_ke")
    assert calm_fx["hud_v2_hint"] is None
    assert calm_fx["pause_tier"] == "T0"


def test_forensic_hud_v2_catalog_anchors_and_rendering() -> None:
    expected_widgets = {
        "alt_pressure_divergence",
        "dual_horn_pulse",
        "hypoxia_tuc_meter",
        "swiss_cheese_align",
        "classic_vs_ng_compare",
        "fuel_avoidance_vector",
        "calibrated_radar_overlay",
        "lemmino_hairline_hud",
        "chapter_title_bumper",
    }
    assert set(FORENSIC_HUD_V2_CATALOG.keys()) == expected_widgets
    assert len(FORENSIC_HUD_V2_CATALOG) == 9

    expected_anchors = {
        "athens": (675, 830),
        "grammatiko": (1115, 365),
        "aegean_corridor": (1540, 560),
        "aegean_entry": (1860, 740),
        "radar_center": (895, 598),
        "avoidance_ctrl": (1015, 675),
    }
    assert VERIFIED_MAP_ANCHORS_2K == expected_anchors
    for name, (ax, ay) in VERIFIED_MAP_ANCHORS_2K.items():
        assert 0 <= ax < 2560 and 0 <= ay < 1440, f"Anchor {name} out of 2K bounds: {(ax, ay)}"

    # Render all 9 widgets across variants A/B/C at scaled 720p (fast) + 2K radar anchor alignment check
    variants = ("A", "B", "C")
    for idx, hud_id in enumerate(sorted(FORENSIC_HUD_V2_CATALOG)):
        variant = variants[idx % len(variants)]
        frame = render_forensic_hud_v2(hud_id, {"kicker": "TEST"}, t_beat=0.65, dur=2.5, width=1280, height=720, variant=variant)
        assert frame.mode == "RGBA"
        assert frame.size == (1280, 720)
        alpha = np.asarray(frame, dtype=np.uint8)[:, :, 3]
        assert int(alpha.max()) > 20 and int((alpha > 0).sum()) > 100, f"{hud_id} ({variant}) rendered empty frame"

    # Calibrated radar overlay places bright non-zero pixels right on scaled Athens & Grammatiko anchors
    radar_2k = render_forensic_hud_v2("calibrated_radar_overlay", {}, t_beat=1.2, dur=2.5, width=2560, height=1440, variant="A")
    arr_2k = np.asarray(radar_2k, dtype=np.uint8)
    for key in ("athens", "grammatiko"):
        ax, ay = VERIFIED_MAP_ANCHORS_2K[key]
        patch_alpha = arr_2k[ay - 28 : ay + 28, ax - 28 : ax + 28, 3]
        assert int(patch_alpha.max()) > 120, f"Radar pin missing near verified anchor {key}={(ax, ay)}"

    # Short 9:16 portrait layout renders cleanly
    short_bumper = render_forensic_hud_v2(
        "chapter_title_bumper",
        {"ch_num": "CH01", "ch_title": "MẬT MÃ 522"},
        t_beat=0.45,
        dur=1.3,
        width=1080,
        height=1920,
        variant="B",
    )
    assert short_bumper.size == (1080, 1920)
    assert int(np.asarray(short_bumper)[:, :, 3].max()) > 20

    with pytest.raises(ValueError):
        render_forensic_hud_v2("nonexistent_hud_v2", {}, t_beat=0.2, dur=1.0)


def test_audio_suspense_v2_synthesis_stereo_and_4act_bgm() -> None:
    assert set(VARIANT_PROFILES.keys()) == {"A", "B", "C"}

    # 1. Boeing 737 pulsed warning horn: 250ms ON / 250ms OFF at 48kHz stereo
    horn = synth_boeing_737_warning_horn(dur_sec=1.0, sr=TARGET_SR, pulsed=True, gain=0.14)
    assert horn.shape == (TARGET_SR, 2) and horn.dtype == np.float32
    on_rms = float(np.sqrt(np.mean(horn[int(0.05 * TARGET_SR) : int(0.20 * TARGET_SR)] ** 2)))
    off_rms = float(np.sqrt(np.mean(horn[int(0.30 * TARGET_SR) : int(0.45 * TARGET_SR)] ** 2)))
    assert on_rms > off_rms * 5.0
    assert float(np.mean(np.abs(horn[:, 0] - horn[:, 1]))) > 1e-4  # Subtle spatial spread

    # 2. Additional aviation/forensic SFX synthesizers produce finite 48kHz stereo arrays
    for fn, kwargs in (
        (synth_master_caution_chime, {"dur_sec": 0.6, "sr": TARGET_SR}),
        (synth_air_leak_turbulence, {"dur_sec": 0.8, "sr": TARGET_SR}),
        (synth_riser_to_subdrop, {"riser_dur": 0.45, "gap_dur": 0.25, "drop_dur": 0.35, "sr": TARGET_SR}),
        (synth_chapter_stinger, {"sr": TARGET_SR, "dur_sec": 0.8}),
    ):
        sig = fn(**kwargs)
        assert sig.ndim == 2 and sig.shape[1] == 2 and sig.shape[0] > 1000
        assert np.all(np.isfinite(sig))

    # 3. Sub-bass (<120Hz crossover) stays centered while high frequencies pan cleanly
    tt = np.arange(TARGET_SR // 2, dtype=np.float32) / float(TARGET_SR)
    sub_sine = np.sin(2.0 * np.pi * 35.0 * tt).astype(np.float32)
    panned_sub = apply_stereo_pan(sub_sine, pan=0.20, sr=TARGET_SR, sub_crossover_hz=120.0)
    mid = slice(TARGET_SR // 8, (3 * TARGET_SR) // 8)
    sub_diff = float(np.max(np.abs(panned_sub[mid, 0] - panned_sub[mid, 1])))
    assert sub_diff < 5e-3

    hi_sine = np.sin(2.0 * np.pi * 1200.0 * tt).astype(np.float32)
    panned_hi = apply_stereo_pan(hi_sine, pan=0.20, sr=TARGET_SR, sub_crossover_hz=120.0)
    hi_diff = float(np.max(np.abs(panned_hi[mid, 0] - panned_hi[mid, 1])))
    assert sub_diff < hi_diff * 0.05
    assert float(np.sqrt(np.mean(panned_hi[mid, 1] ** 2))) > float(np.sqrt(np.mean(panned_hi[mid, 0] ** 2))) * 1.15

    # 4. 4-act tension BGM honors true stereo, dropout silence, and voice ducking
    n_samples = 3 * TARGET_SR
    silent_voice = np.zeros((n_samples, 2), dtype=np.float32)
    beats = [
        {"id": "S005", "start": 0.0, "end": 1.0, "text": "Radio ATC trong đêm"},
        {"id": "S053", "start": 1.0, "end": 2.0, "text": "Còi báo động độ cao cabin"},
        {"id": "S114", "start": 2.0, "end": 3.0, "text": "Hồi kết tại Grammatiko"},
    ]
    bgm = compose_4act_tension_bgm(
        n_samples=n_samples,
        voice_stereo=silent_voice,
        beats=beats,
        variant="B",
        sr=TARGET_SR,
        seed=42,
        drop_windows=[(1.40, 1.85)],
    )
    assert bgm.shape == (n_samples, 2)
    assert float(np.sqrt(np.mean((bgm[:, 0] - bgm[:, 1]) ** 2))) > 1e-4  # True stereo width
    drop_rms = float(np.sqrt(np.mean(bgm[int(1.48 * TARGET_SR) : int(1.78 * TARGET_SR)] ** 2)))
    active_rms = float(np.sqrt(np.mean(bgm[int(0.20 * TARGET_SR) : int(1.10 * TARGET_SR)] ** 2)))
    assert drop_rms < active_rms * 0.05

    loud_voice = np.column_stack([
        0.35 * np.sin(2.0 * np.pi * 240.0 * (np.arange(n_samples, dtype=np.float32) / TARGET_SR)),
        0.35 * np.sin(2.0 * np.pi * 240.0 * (np.arange(n_samples, dtype=np.float32) / TARGET_SR)),
    ])
    bgm_ducked = compose_4act_tension_bgm(
        n_samples=n_samples,
        voice_stereo=loud_voice,
        beats=beats,
        variant="B",
        sr=TARGET_SR,
        seed=42,
    )
    ducked_rms = float(np.sqrt(np.mean(bgm_ducked[int(0.20 * TARGET_SR) : int(1.10 * TARGET_SR)] ** 2)))
    assert ducked_rms < active_rms * 0.75


def test_audio_suspense_v2_calibrated_wav_and_m4a_export(tmp_path: Path) -> None:
    # Build a realistic 2.8s speech-like mono WAV (modulated multi-harmonic formants + breath gaps)
    dur_sec = 2.8
    n = int(dur_sec * TARGET_SR)
    tt = np.arange(n, dtype=np.float32) / float(TARGET_SR)
    f0 = 155.0 + 20.0 * np.sin(2.0 * np.pi * 2.3 * tt)
    ph = 2.0 * np.pi * np.cumsum(f0) / float(TARGET_SR)
    syllable_env = np.where((tt < 1.15) | ((tt > 1.35) & (tt < 2.65)), 0.5 + 0.4 * np.sin(2.0 * np.pi * 4.2 * tt), 0.0)
    speech = (
        0.18 * np.sin(ph) + 0.11 * np.sin(2.0 * ph) + 0.06 * np.sin(3.0 * ph) + 0.03 * np.sin(5.0 * ph)
    ) * syllable_env.astype(np.float32)

    voice_wav = tmp_path / "voice_dry.wav"
    pcm = np.clip(speech * 32767.0, -32767, 32767).astype("<i2")
    with wave.open(str(voice_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(TARGET_SR)
        wf.writeframes(pcm.tobytes())

    out_wav = tmp_path / "mix_suspense_A.wav"
    out_m4a = tmp_path / "mix_suspense_A.m4a"
    beats = [
        {"id": "S005", "start": 0.0, "end": 1.2, "text": "Helios 522 mất liên lạc qua VHF"},
        {"id": "S053", "start": 1.2, "end": 2.8, "text": "Còi báo động độ cao vang lên"},
    ]
    res = build_suspense_audio_mix(
        voice_wav=voice_wav,
        out_wav=out_wav,
        out_m4a=out_m4a,
        beats=beats,
        variant="A",
        seed=42,
        sr=TARGET_SR,
    )

    assert out_wav.is_file() and out_wav.stat().st_size > 10_000
    assert out_m4a.is_file() and out_m4a.stat().st_size > 4_000
    assert res["sample_rate"] == TARGET_SR and res["channels"] == 2
    assert len(res["env_30fps"]) >= int(dur_sec * FPS) - 1

    # Loudness & peak contracts verified on both WAV and calibrated M4A
    for key in ("ebur128_wav", "ebur128_m4a"):
        stats = res[key]
        assert -11.40 <= stats["integrated_lufs"] <= -10.60, f"{key} LUFS out of bounds: {stats}"
        assert stats["true_peak_dbfs"] <= -1.0, f"{key} TP > -1.0 dBTP: {stats}"

    # Verify M4A stream is real 48kHz stereo AAC and decoded L/R differ (no mono collapse)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name,sample_rate,channels", "-of", "json", str(out_m4a)],
        capture_output=True,
        text=True,
        check=True,
    )
    stream_info = json.loads(probe.stdout)["streams"][0]
    assert stream_info["codec_name"] == "aac"
    assert int(stream_info["sample_rate"]) == TARGET_SR
    assert int(stream_info["channels"]) == 2

    decoded_wav = tmp_path / "decoded_m4a.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(out_m4a), "-acodec", "pcm_s16le", str(decoded_wav)],
        capture_output=True,
        check=True,
    )
    with wave.open(str(decoded_wav), "rb") as wf:
        assert wf.getnchannels() == 2
        assert wf.getframerate() == TARGET_SR
        samples = np.frombuffer(wf.readframes(wf.getnframes()), dtype="<i2").reshape(-1, 2).astype(np.float32) / 32768.0
    stereo_diff_rms = float(np.sqrt(np.mean((samples[:, 0] - samples[:, 1]) ** 2)))
    assert stereo_diff_rms > 1e-4, "Calibrated M4A collapsed to mono!"
