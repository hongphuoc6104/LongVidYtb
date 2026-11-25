# Sub-Warehouse Catalog Reference (`sys/fx_warehouse/`)

Complete indexed reference of the shared functional sub-warehouses (`v1` base shards, `v2` forensic HUD & suspense audio shards, and selector/pipeline bridge).

---

## 1. Camera & VFX Shard (`sys/fx_warehouse/camera_vfx.py`)

### 1.1 Sub-Pixel 2.5D Camera Moves (`CAMERA_MOTION_CATALOG` — 8 Presets)
All camera moves operate in continuous `float32` sub-pixel coordinates with overscan (`z >= 1.0`) to eliminate integer-pixel jitter and recursive `zoompan` drift.

| Camera ID | `z0 -> z1` | `x0 -> x1` | `y0 -> y1` | `parallax_amp` | Narrative Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `parallax_push_in` | `1.045 -> 1.120` | `-0.008 -> 0.008` | `0.004 -> -0.004` | `0.024` | Smooth 2.5D foreground/background separation; builds tension or focus. |
| `parallax_pull_out` | `1.110 -> 1.042` | `0.010 -> -0.010` | `-0.004 -> 0.004` | `0.022` | Reveals broader context, aftermath, or systemic scale. |
| `anamorphic_pan_lr` | `1.060 -> 1.090` | `-0.020 -> 0.020` | `0.0 -> 0.0` | `0.020` | Cinematic left-to-right anamorphic sweep across wide scenes/timelines. |
| `anamorphic_pan_rl` | `1.085 -> 1.055` | `0.018 -> -0.018` | `0.002 -> -0.002` | `0.018` | Right-to-left counter-sweep for contrast, flashback, or rebuttal. |
| `orbital_tilt_up` | `1.045 -> 1.100` | `-0.006 -> 0.006` | `0.010 -> -0.010` | `0.020` | Upward tilt emphasizing monumentality, architecture, or power. |
| `orbital_tilt_down` | `1.045 -> 1.092` | `0.0 -> 0.0` | `-0.010 -> 0.008` | `0.016` | Overhead satellite/dossier-table downward inspection. |
| `breathing_drift` | `1.020 -> 1.045` | `-0.004 -> 0.004` | `-0.002 -> 0.002` | `0.008` | Ultra-gentle organic drift preserving clean 2D doodle or calm scenes. |
| `static_clean` | `1.000 -> 1.000` | `0.0 -> 0.0` | `0.0 -> 0.0` | `0.000` | Locked frame for split-screen comparisons or dense diagrams. |

### 1.2 GPU Frame Shaders (`VFX_SHADER_CATALOG` — 7 Shaders)

| Shader ID | Intensity | Description | Comfort Guardrail Notes |
| :--- | :--- | :--- | :--- |
| `camera_shake_impulse` | `high` | Exponentially decaying impact shake synced to slams/collisions. | **Disallowed** on Group 4 (Doodle) & Group 5 (Mindful). |
| `kodak_35mm_grain` | `low` | Subtle 35mm film grain for documentary/archival realism. | Safe for Groups 1–3; avoid on pure flat 2D Doodle (`#FFFFFF`). |
| `crimson_strobe_alert` | `high` | 2200K crimson emergency warning strobe. | **Disallowed** on Group 4 (Doodle) & Group 5 (Mindful). |
| `chromatic_glitch_pulse` | `medium` | RGB channel-split micro-glitch for signal interference/confusion. | **Disallowed** on Group 5 (Mindful). |
| `hypoxic_vignette` | `medium` | Progressive edge-darkening constriction simulating blackout/hypoxia. | **Disallowed** on Group 4 (Doodle) & Group 5 (Mindful). |
| `warm_dust_motes` | `low` | Slow drifting warm-gold dust motes, gentle on the eyes. | Default for Group 5 (Mindful); safe across calm beats. |
| `clean_daylight_none` | `none` | 100% clean frame with zero shader overlay or grain. | Default for Group 4 (2D Doodle Explainer). |

### 1.3 Bespoke Camera & VFX Registration API
- `register_bespoke_camera_motion(motion_id, spec)` — Registers a per-video custom camera curve (`z0`, `z1`, `x0`, `x1`, `y0`, `y1`, `parallax_amp`, `description`) into the active catalog.
- `register_bespoke_vfx_shader(shader_id, spec)` — Registers a per-video custom GPU shader preset (`intensity`, `description`, optional shader parameters).

---

## 2. HUD & Layout Shard (`sys/fx_warehouse/hud_widgets.py`)

### 2.1 Shared 30fps HUD & Layout Widgets (`HUD_WIDGET_CATALOG` — 14 Widgets)
Rendered as compact RGBA PIL patches via `render_hud_widget_patch(widget_id, spec, t_beat, dur, amp=0.3, width=2560, height=1440)`.

| Widget ID | Kind | Position / Footprint | Key `spec` Fields |
| :--- | :--- | :--- | :--- |
| `typewriter_telemetry_tag` | `corner_hud` | Top-right (`width - 64 - w, 48`) | `tag`, `accent_rgba` |
| `altitude_stat_counter` | `data_hud` | Bottom-left (`680x175`) | `target_value`, `unit`, `kicker`, `accent_rgba` |
| `kinetic_stamp_slam` | `impact_hud` | Bottom-left (`840x178`, scale `1.42->1.00`) | `kicker`, `headline`, `subline` |
| `xray_mode_switch_particles` | `tech_hud` | Bottom-left (`780x190`) | `kicker`, `left_label`, `right_label` |
| `dual_oscilloscope_compare` | `tech_hud` | Bottom-left (`880x210`) | `kicker`, `badge`, `wave1_label`, `wave2_label` |
| `countdown_cvr_waveform` | `forensic_hud` | Bottom-left (`860x210`) | `kicker`, `countdown_from`, `metric_prefix` |
| `lemmino_dossier_card` | `editorial_hud` | Left slide-in (`840x168`) | `kicker`, `headline`, `subline` |
| `radar_bezier_trajectory` | `map_layout` | Full-width (`width x 920` @ `y=160`) | Animated Bezier dashed arc + pulsing targets |
| `laser_split_screen` | `split_layout` | Top dual badges (`width x 160` @ `y=160`) | `left_kicker`, `left_title`, `right_kicker`, `right_title` |
| `triptych_3col_evidence` | `triptych_layout` | 3-column header bar (`width x 130` @ `y=140`) | `headers` (list of 3 strings) |
| `verdict_lower_third` | `editorial_hud` | Bottom-left (`1480x136` @ `y=960`) | `kicker`, `headline` |
| `doodle_spring_pop_badge` | `doodle_hud` | Bottom-left (`620x136`, spring pop) | `kicker`, `headline`, `accent_rgba` |
| `highlighter_stroke_bar` | `doodle_hud` | Bottom-left (`820x128`, yellow sweep) | `kicker`, `headline` |
| `calligraphy_quote_dissolve` | `mindful_hud` | Bottom-left (`920x150`, warm fade) | `kicker`, `headline` |

### 2.2 Bespoke HUD Patch Builder API
- `build_bespoke_topic_hud_patch(bespoke_hud_spec, t_beat, dur, amp=0.3, width=2560, height=1440)` — Dynamically renders a custom topic-specific HUD card, multi-row metric table, progress meter, or domain diagram directly from a `bespoke_hud_spec` dict without forcing any of the 14 preset widgets.
- `register_bespoke_hud_widget(widget_id, spec, renderer=None)` — Registers a custom HUD widget into `HUD_WIDGET_CATALOG` for reuse across beats in a video or promotion to the shared shard.

---

## 3. Audio SFX & BGM Shard (`sys/fx_warehouse/audio_sfx_bgm.py`)

All warehouse audio assets are **48kHz stereo 16-bit PCM WAV** (`TARGET_SR = 48000`) stored in `sys/assets/sfx/` and `sys/assets/audio/bgm/`, generated deterministically via `ensure_warehouse_audio_assets(force=False)` when missing.

### 3.1 Base 2D SFX (`EXISTING_SFX_FILES` — 7 Stems)
Preserved untouched for all channels (`archetypes: ["all"]`):
- `ambient_focus_loop.wav` (`ambient`)
- `clock_tick.wav` (`timing`)
- `ding_insight.wav` (`insight`)
- `page_flip.wav` (`paper`)
- `pen_highlight.wav` (`marker`)
- `pop_clean.wav` (`pop`)
- `whoosh_soft.wav` (`transition`)

### 3.2 Expanded Warehouse Stereo SFX (`SFX_CATALOG` — 18 Additional Stems = 25 Total)

| Filename | Role | Duration | Primary Trigger / Use Case |
| :--- | :--- | :--- | :--- |
| `jet_flyby_doppler.wav` | `flyby` | `1.45s` | Aviation / supersonic / rapid overhead pass |
| `typewriter_burst.wav` | `telemetry` | `0.65s` | Telemetry tag / archival typing |
| `cold_wind_gust.wav` | `atmosphere` | `1.10s` | High-altitude, wasteland, or tense isolation |
| `sub_bass_boom.wav` | `impact` | `0.90s` | Stat reveal, verdict, or heavy structural drop |
| `stamp_slam_hit.wav` | `impact` | `0.60s` | `kinetic_stamp_slam` / classified seal |
| `rotary_switch_click.wav` | `mechanical` | `0.45s` | `xray_mode_switch_particles` / valve or breaker flip |
| `air_pressure_hiss.wav` | `hiss` | `1.50s` | Cabin depressurization, steam, or pneumatic release |
| `caution_chime_double.wav` | `alarm` | `0.85s` | `dual_oscilloscope_compare` / instrument warning |
| `heartbeat_lub_dub.wav` | `biometric` | `0.95s` | `countdown_cvr_waveform` / survival tension |
| `stopwatch_urgent_tick.wav` | `timing` | `0.50s` | Rapid countdown or deadline pressure |
| `dossier_slide_whoosh.wav` | `transition` | `0.42s` | `lemmino_dossier_card` / document slide |
| `radar_sonar_ping.wav` | `telemetry` | `0.70s` | `radar_bezier_trajectory` / tracking lock |
| `laser_split_whoosh.wav` | `transition` | `0.52s` | `laser_split_screen` / A-vs-B comparison |
| `card_lock_thud.wav` | `impact` | `0.55s` | `triptych_3col_evidence` / sequential panel lock |
| `taiko_war_drum.wav` | `epic` | `1.00s` | Historical battle, dynasty clash, or turning point |
| `braaam_horn_low.wav` | `epic` | `1.40s` | Geopolitical shockwave or macro-scale reveal |
| `singing_bowl_zen.wav` | `mindful` | `2.40s` | `calligraphy_quote_dissolve` / mindful transition |
| `night_rain_soft.wav` | `ambient` | `2.50s` | Late-night reflection / calm atmospheric bed |

### 3.3 Niche BGM Loops (`BGM_CATALOG` — 5 Loops, `12.0s` Seamless)

| Filename | Mood | Default Archetype |
| :--- | :--- | :--- |
| `bgm_forensic_noir_drone.wav` | `dark_forensic` | Group 1 (`archetype_1_forensic_noir`) |
| `bgm_geopolitics_pulse.wav` | `tense_pulse` | Group 2 (`archetype_2_geopolitics_history`) |
| `bgm_scifi_biotech_pad.wav` | `cyan_telemetry` | Group 3 (`archetype_3_science_xray`) |
| `bgm_curious_acoustic_loop.wav` | `light_curious` | Group 4 (`archetype_4_doodle_explainer`) |
| `bgm_zen_night_healing.wav` | `calm_warm` | Group 5 (`archetype_5_mindful_healing`) |

### 3.4 Procedural Bespoke SFX Synthesizer API
- `synthesize_bespoke_topic_sfx(spec_or_name, output_path=None, seed=42)` — Procedurally synthesizes a custom 48kHz stereo WAV SFX/ambience on the fly for a specific video topic (using bandpass/lowpass noise shaping, harmonic synthesis, envelope ADSR, and stereo panning) whenever no existing stem in `SFX_CATALOG` fits naturally.

---

## 4. Selector & Guardrail Shard (`sys/fx_warehouse/selector.py`)

### 4.1 `auto_select_beat_fx(...)`
```python
auto_select_beat_fx(
    beat_text: str,
    channel_id: str,
    beat_index: int = 0,
    total_beats: int = 1,
    overrides: dict[str, Any] | None = None,
    video_topic: str | None = None,
    allow_bespoke: bool = True,
) -> dict[str, Any]
```

**Selection & Guardrail Flow**:
1. **Archetype Resolution**: Maps `channel_id` via `CHANNEL_ARCHETYPE_MAP` (defaults to `archetype_1_forensic_noir` if unknown).
2. **Semantic Keyword Routing**: Matches `beat_text` against 12 narrative intent patterns (in priority order: Split -> Triptych -> Verdict -> Radar -> CVR -> Oscilloscope -> X-Ray -> Mindful -> Stamp -> Dossier -> Stat -> Highlight), then falls back to archetype defaults (`doodle_spring_pop_badge` for Group 4, `calligraphy_quote_dissolve` for Group 5, `verdict_lower_third` for the final beat when `total_beats >= 3`).
3. **Bespoke Trigger Check**: When `allow_bespoke=True`, inspects `video_topic`, `beat_text`, and `overrides` (`bespoke_hud_spec`, `bespoke_sfx_spec`). If the topic requires specialized domain mechanics not covered by the 14 HUD widgets or 25 SFX stems, returns a bespoke specification (`is_bespoke: True`) instead of force-fitting an unrelated preset.
4. **Cross-Niche Pull & Comfort Guardrails**: Any channel may pull compatible HUDs/cameras/SFX from other archetypes (e.g., Group 4 pulling `triptych_3col_evidence` or `laser_split_screen` for a structured comparison), **except** `vfx` in `arch["disallowed_vfx"]` are automatically suppressed back to `arch["default_vfx"]` unless explicitly overridden with `allow_unsafe_vfx=True`.
5. **Static Camera Pin Lock (`STATIC_CAMERA_HUDS`)**: Whenever the selected `hud` is in `{"radar_bezier_trajectory", "laser_split_screen", "triptych_3col_evidence", "calibrated_radar_overlay"}` or `hud_v2_hint == "calibrated_radar_overlay"` (and `overrides` does not explicitly supply `"camera"`), `camera` is forcibly locked to `"static_clean"` so map coordinates and split-screen boundaries never drift.
6. **Suspense Metadata (`pause_tier`, `recommended_pause_sec`, `hud_v2_hint`)**: Every `auto_select_beat_fx(...)` result includes `pause_tier` (`"T0"`: `0.14s`, `"T1"`: `0.28s`, `"T2"`: `0.45s`, `"T3"`: `0.65s` via `PAUSE_TIER_DURATIONS`), `recommended_pause_sec`, and `hud_v2_hint` (identifying a matching `FORENSIC_HUD_V2_CATALOG` widget ID or `None`).

---

## 5. Forensic HUD v2 Shard (`sys/fx_warehouse/hud_forensic_v2.py`)

High-precision 30fps RGBA overlays engineered for `ho_so_ky_la` and `[FORENSIC_V2]` workflows across three visual grammar variants (`A`: Forensic Telemetry, `B`: LEMMiNO Chiaroscuro Noir, `C`: Vox/Fincher Kinetic).

### 5.1 9 High-Precision HUD v2 Widgets (`FORENSIC_HUD_V2_CATALOG`)

| Widget ID | Primary Telemetry / Visual Grammar | Notes |
| :--- | :--- | :--- |
| `alt_pressure_divergence` | Dual curve comparing aircraft climb vs cabin pressure drop | Annotated with `3.600M` & `4.300M` hypoxia thresholds |
| `dual_horn_pulse` | Non-overlapping `2.0Hz` (`250ms ON / 250ms OFF`) pulse comparator | Contrasts Takeoff Config warning vs Cabin Altitude warning |
| `hypoxia_tuc_meter` | CO2 clearance vs SpO2 drop paradox with animated `30–90s` TUC bar | Survival countdown telemetry |
| `swiss_cheese_align` | 4 sequential defense slices sliding into alignment | Animated red laser piercing all aligned gaps |
| `classic_vs_ng_compare` | Split comparator: 1997 Boeing 737 Classic vs 2006 Post-Helios NG | 1 dim P5 lamp vs 2 separated eye-level lamps |
| `fuel_avoidance_vector` | Dual fuel bars dropping to `0%` + Athens avoidance vector | `ENG 1 11:50`, `ENG 2 12:00`, vector to Grammatiko `12:04` |
| `calibrated_radar_overlay` | Dynamic Bezier trajectory & radar sweep locked to calibrated anchors | Must run with `static_clean` camera |
| `lemmino_hairline_hud` | Ultra-clean `1px` hairline forensic typography & timeline | Built for Option B LEMMiNO Noir |
| `chapter_title_bumper` | Animated `1.3s` dossier chapter card (`CH01..CH10` / Style `01..04`) | Clean chapter transitions |

### 5.2 Verified 2K Map Anchors (`VERIFIED_MAP_ANCHORS_2K`) & Dispatch API
Calibrated directly against 2560×1440 night-imagery pixel geometry:
- `athens`: `(675, 830)`
- `grammatiko`: `(1115, 365)`
- `aegean_corridor`: `(1540, 560)`
- `aegean_entry`: `(1860, 740)`
- `radar_center`: `(895, 598)`
- `avoidance_ctrl`: `(1015, 675)`

**Public API**:
- `render_forensic_hud_v2(hud_id, spec, t_beat, dur, width=2560, height=1440, variant="A") -> PIL.Image.Image` (full-frame RGBA overlay; accepts `FORENSIC_HUD_V2_CATALOG` keys or aliases and raises `ValueError` on unknown IDs)
- Direct widget functions: `render_alt_pressure_divergence`, `render_dual_horn_pulse`, `render_hypoxia_tuc_meter`, `render_swiss_cheese_align`, `render_classic_vs_ng_compare`, `render_fuel_avoidance_vector`, `render_calibrated_radar_overlay`, `render_lemmino_hairline_hud`, `render_chapter_title_bumper`
- `set_font_dir(font_dir)` — overrides font search directory (useful inside remote Colab workers).

---

## 6. Suspense Audio v2 Shard (`sys/fx_warehouse/audio_suspense_v2.py`)

48kHz (`TARGET_SR = 48000`, `FPS = 30`) true-stereo procedural BGM/SFX & 2-pass broadcast mastering engine.

### 6.1 Three Tuned Mix Profiles (`VARIANT_PROFILES`)

| Variant | Name | `bgm_idle_gain` | `bgm_duck_db` | `pulse_emphasis` | `cello_emphasis` | `sfx_gain` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `A` | `Forensic Telemetry` | `0.165` | `-5.5` | `1.00` | `0.85` | `1.00` |
| `B` | `LEMMiNO Chiaroscuro Noir` | `0.145` | `-6.8` | `0.42` | `1.38` | `0.86` |
| `C` | `Vox/Fincher Kinetic` | `0.185` | `-4.8` | `1.45` | `0.95` | `1.12` |

### 6.2 Procedural Synthesizers, Spatialization & EBU R128 Calibration
- **4-Act Dynamic Tension BGM**: `compose_4act_tension_bgm(n_samples, voice_stereo, beats, variant="A", sr=48000, seed=42, drop_windows=None)` — procedural low drone, pulsing motif, mournful cello bed, speech sidechain ducking, and climax silence dropouts.
- **Forensic & Aviation Synthesizers**:
  - `synth_boeing_737_warning_horn(dur_sec=2.6, sr=48000, pulsed=True, gain=0.14)`
  - `synth_master_caution_chime(dur_sec=0.85, sr=48000, gain=0.13)`
  - `synth_air_leak_turbulence(dur_sec=1.8, sr=48000, gain=0.11, seed=42)`
  - `synth_riser_to_subdrop(riser_dur=0.65, gap_dur=0.45, drop_dur=0.42, sr=48000, riser_gain=0.14, drop_gain=0.22, seed=42)`
  - `synth_chapter_stinger(sr=48000, dur_sec=1.30, gain=0.18, seed=42)`
- **VHF Radio & Stereo Placement**: `apply_vhf_radio_texture(...)`, `add_vhf_cockpit_bed(...)`, `apply_stereo_pan(...)` (sub-bass centered below cutoff), `place_stereo_sfx(...)`, `compute_voice_envelope_30fps(...)`.
- **Broadcast Mastering & Calibrated AAC Export**:
  - `measure_ebur128(audio_path)` — measures integrated LUFS, LRA, and true-peak dBTP via FFmpeg `ebur128`.
  - `master_2pass_wav_stereo(raw_stereo, out_wav, sr=48000, target_lufs=-11.0, max_tp_db=-1.0, lra=5.0)` — preserves L/R stereo width while normalizing to `-11.0 LUFS / <= -1.0 dBTP`.
  - `encode_calibrated_m4a_stereo(wav_path, out_m4a, target_lufs=-11.0, max_tp_db=-1.0, pre_aac_tp_db=-1.4, lra=4.5)` — encodes true-stereo 256k AAC (`.m4a`) with pre-AAC headroom and re-calibrates so the decoded `.m4a` stays inside `-11.0 ± 0.4 LUFS` and `<= -1.0 dBTP`.
  - `build_suspense_audio_mix(voice_wav, out_wav, out_m4a, beats, variant="A", seed=42, sr=48000, drop_windows=None)` — end-to-end orchestrator returning paths, `ebur128_wav`, `ebur128_m4a`, and `env_30fps`.
