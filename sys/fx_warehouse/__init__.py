"""Unified Shared Motion, HUD, VFX, SFX & BGM Warehouse Package for All 20 Vietnamese Channels.

Sharded into modular sub-warehouses:
- `archetypes`: 5 Niche Archetypes, 20-channel map, & per-topic bespoke synthesis policies
- `camera_vfx`: 8 sub-pixel 2.5D camera moves, 7 GPU shaders, & bespoke registration
- `hud_widgets`: 14 30fps HUD/layout widgets & dynamic `build_bespoke_topic_hud_patch`
- `audio_sfx_bgm`: 25 stereo 48kHz SFX stems, 5 Niche BGM loops, & `synthesize_bespoke_topic_sfx`
- `selector`: `auto_select_beat_fx` with comfort guardrails & automatic bespoke routing
- `hud_forensic_v2`: 9 high-precision forensic/3D dossier 30fps HUD widgets
- `audio_suspense_v2`: 48kHz stereo suspense audio mixer (`A`/`B`/`C` variants)
- `pipeline_bridge`: Unified `plan_and_prepare_dual_mode_fx` & `resolve_fx_intent_from_text`
"""
from __future__ import annotations

from .archetypes import (
    ARCHETYPE_PROFILES,
    CHANNEL_ARCHETYPE_MAP,
    CHANNEL_BESPOKE_RULES,
    resolve_niche_fx_blueprint,
)
from .audio_sfx_bgm import (
    BGM_CATALOG,
    BGM_DIR,
    EXISTING_SFX_FILES,
    SFX_CATALOG,
    SFX_DIR,
    SYS_DIR,
    TARGET_SR,
    ensure_warehouse_audio_assets,
    synthesize_bespoke_topic_sfx,
)
from .audio_suspense_v2 import (
    FPS,
    VARIANT_PROFILES,
    add_vhf_cockpit_bed,
    apply_stereo_pan,
    apply_vhf_radio_texture,
    build_suspense_audio_mix,
    compose_4act_tension_bgm,
    compute_voice_envelope_30fps,
    encode_calibrated_m4a_stereo,
    master_2pass_wav_stereo,
    measure_ebur128,
    place_stereo_sfx,
    synth_air_leak_turbulence,
    synth_boeing_737_warning_horn,
    synth_chapter_stinger,
    synth_master_caution_chime,
    synth_riser_to_subdrop,
)
from .camera_vfx import (
    BESPOKE_CAMERA_MOTIONS,
    BESPOKE_VFX_SHADERS,
    CAMERA_MOTION_CATALOG,
    VFX_SHADER_CATALOG,
    get_camera_motion,
    get_vfx_shader,
    register_bespoke_camera_motion,
    register_bespoke_vfx_shader,
)
from .fx_compositor import (
    build_ffmpeg_vfx_filter,
    mix_fx_warehouse_audio,
    prepare_fx_hud_assets,
)
from .hud_forensic_v2 import (
    FORENSIC_HUD_V2_CATALOG,
    VERIFIED_MAP_ANCHORS_2K,
    render_alt_pressure_divergence,
    render_calibrated_radar_overlay,
    render_chapter_title_bumper,
    render_classic_vs_ng_compare,
    render_dual_horn_pulse,
    render_forensic_hud_v2,
    render_fuel_avoidance_vector,
    render_hypoxia_tuc_meter,
    render_lemmino_hairline_hud,
    render_swiss_cheese_align,
    set_font_dir,
)
from .hud_widgets import (
    BESPOKE_HUD_WIDGETS,
    HUD_WIDGET_CATALOG,
    build_bespoke_topic_hud_patch,
    register_bespoke_hud_widget,
    render_hud_widget_patch,
)
from .pipeline_bridge import (
    FX_MODE_CHOICES,
    TRIGGER_KEYWORD_TABLE,
    plan_and_prepare_dual_mode_fx,
    resolve_fx_intent_from_text,
)
from .selector import PAUSE_TIER_DURATIONS, STATIC_CAMERA_HUDS, auto_select_beat_fx

__all__ = [
    "ARCHETYPE_PROFILES",
    "BESPOKE_CAMERA_MOTIONS",
    "BESPOKE_HUD_WIDGETS",
    "BESPOKE_VFX_SHADERS",
    "BGM_CATALOG",
    "BGM_DIR",
    "CAMERA_MOTION_CATALOG",
    "CHANNEL_ARCHETYPE_MAP",
    "CHANNEL_BESPOKE_RULES",
    "EXISTING_SFX_FILES",
    "FORENSIC_HUD_V2_CATALOG",
    "FPS",
    "FX_MODE_CHOICES",
    "HUD_WIDGET_CATALOG",
    "PAUSE_TIER_DURATIONS",
    "SFX_CATALOG",
    "SFX_DIR",
    "STATIC_CAMERA_HUDS",
    "SYS_DIR",
    "TARGET_SR",
    "TRIGGER_KEYWORD_TABLE",
    "VARIANT_PROFILES",
    "VERIFIED_MAP_ANCHORS_2K",
    "VFX_SHADER_CATALOG",
    "add_vhf_cockpit_bed",
    "apply_stereo_pan",
    "apply_vhf_radio_texture",
    "auto_select_beat_fx",
    "build_bespoke_topic_hud_patch",
    "build_ffmpeg_vfx_filter",
    "build_suspense_audio_mix",
    "compose_4act_tension_bgm",
    "compute_voice_envelope_30fps",
    "encode_calibrated_m4a_stereo",
    "ensure_warehouse_audio_assets",
    "get_camera_motion",
    "get_vfx_shader",
    "master_2pass_wav_stereo",
    "measure_ebur128",
    "mix_fx_warehouse_audio",
    "place_stereo_sfx",
    "plan_and_prepare_dual_mode_fx",
    "prepare_fx_hud_assets",
    "register_bespoke_camera_motion",
    "register_bespoke_hud_widget",
    "register_bespoke_vfx_shader",
    "render_alt_pressure_divergence",
    "render_calibrated_radar_overlay",
    "render_chapter_title_bumper",
    "render_classic_vs_ng_compare",
    "render_dual_horn_pulse",
    "render_forensic_hud_v2",
    "render_fuel_avoidance_vector",
    "render_hud_widget_patch",
    "render_hypoxia_tuc_meter",
    "render_lemmino_hairline_hud",
    "render_swiss_cheese_align",
    "resolve_fx_intent_from_text",
    "resolve_niche_fx_blueprint",
    "set_font_dir",
    "synth_air_leak_turbulence",
    "synth_boeing_737_warning_horn",
    "synth_chapter_stinger",
    "synth_master_caution_chime",
    "synth_riser_to_subdrop",
    "synthesize_bespoke_topic_sfx",
]
