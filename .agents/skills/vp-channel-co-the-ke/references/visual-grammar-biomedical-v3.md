# Visual Grammar — `co_the_ke_3d_biomedical_v3`

Reference specification for generating **8K 3D Endoscopic Biomedical Cinematography** paired with the 4-mode physiological visual storytelling system (`MODE_1`..`MODE_4`) on **Cơ Thể Kể (`co_the_ke`)**.

## 1. Base 3D Biomedical Realism (3 Pillars) & Hygiene Constraints

Raw Flow (`BELUGA` / `Omni 1.2 Flash`) generation MUST strictly enforce `allowed_text=None` (`strictly zero text`, zero gibberish anatomical labels, zero random EKG digits, zero AI corner watermarks) and visualize concrete biological mechanisms matching every spoken beat:

1. **Pillar 1 — 3D Endoscopic & Volumetric Organ Flythrough**: Unreal Engine 5 / Octane photorealistic internal camera flying through living arterial corridors, beating cardiac valves, synaptic clefts, renal nephrons, and pulmonary alveoli under subsurface bioluminescent cyan/crimson illumination against deep biomedical navy `#0A192F`.
2. **Pillar 2 — 100mm Macro Bio-Mechanism & Cellular Physics**: Close-up real-time physiological interactions — ATP depletion, cortisol surges, natural killer (NK) T-cell scanning, macrophage phagocytosis, and cervical disc micro-compression rendered cleanly without graphic blood/gore.
3. **Pillar 3 — Human Stimulus-to-Response Reality**: Cinematic macro bridges linking daily human triggers (midnight smartphone blue light, 60-degree neck posture, iced drink thermal shock, skipping breakfast) directly into translucent 3D X-ray skeletal/organ cutaways.

### Locked Color Palette & Anti-Repetition Guardrails
- **Deep Biomedical Navy**: `#0A192F`
- **Anatomical Slate Shadow**: `#0F172A`
- **Clinical X-Ray Cyan**: `#06B6D4` (Warehouse `archetype_3_science_xray` primary accent `(32, 212, 248, 255)`)
- **Arterial Danger / Alert Crimson**: `#EF4444` (Warehouse accent `(205, 52, 48, 255)`)
- **Clean Laboratory White**: `#F8FAFC`
- **Bio-Energy Warm Amber**: `#F59E0B`
- **Zero Gore, Zero Kawaii Flat Slop, Zero Stickmen**: Strictly zero bloody surgery gore, zero 2D flat cartoon stickers (`ch_organ_buddies` / `kawaii` deprecated for V3), zero doodle stick figures, zero sci-fi neon cyberpunk clutter unrelated to physiology.
- **Clean Corner Pipeline**: Apply `1.045x` overscan crop and run FFmpeg bottom-right `delogo` (`_compute_bottom_right_delogo_filter`) **before** overlaying `watermark_150x150.png` (`150x150` RGBA) at `W-w-48:H-h-48` (2K) or `W-w-36:H-h-36` (HD).

## 2. Four Biomedical Visual Modes (`Long 16:9` at `2560x1440`)

| Mode Code | Target Share | Trigger in Narration | 2K (`2560x1440`) Composition & Overlay Spec |
|---|---|---|---|
| **`MODE_1_BIOMETRIC_STAMP`** | **~15% beats** | Shocking numbers, biological thresholds, cell counts, pressure loads (e.g., `27 KG`, `70% TẾ BÀO NK`, `02:00 AM`, `90 PHÚT`) | Dark `#0A192F` vignette scrim over 3D biomedical frame + bold Clinical Cyan `#06B6D4` or Arterial Crimson `#EF4444` stat card + clean `#F8FAFC` subhead (`<= 6` words), clear of bottom-right watermark. |
| **`MODE_2_NORMAL_VS_STRESS_SPLIT`** | **~12% beats** | Physiological contrasts: healthy baseline vs overload (`Ngủ Đủ 8H` vs `Thức Trắng 24H`, `Cúi 0°` vs `Cúi 60°`) | Glowing vertical `#06B6D4` / `#EF4444` split separating calm homeostatic 3D view vs stressed biological response with concise `<= 4` word headers per half. |
| **`MODE_3_CASCADE_CHECKLIST`** | **~15% beats** | Sequential physiological steps, circadian timeline stages, or 3-step recovery protocol (`[01]`, `[02]`, `[03]`) | Left-weighted 3D organ X-ray + right-docked dark slate biotech dossier card (`#0F172A` @ 88% opacity, `#06B6D4` accent border) listing `[01]`, `[02]`, `[03]`. |
| **`MODE_4_ENDOSCOPIC_PACING`** | **~58% beats** | Smooth fluid/vascular flow, internal organ flythroughs, daily habit setups, and biological story progression | Uncluttered clean full-bleed 3D biomedical frame (`2560x1440@30fps`) with static Lanczos + subtle parallax zoom/pan (`xfade=fade:duration=0.20`) and key-beat `omni_flash` I2V clips. |

## 3. Four Creative Style Directions & Chapter Allocation

- **`STYLE_1_MICRO_ENDOSCOPIC_CINEMA`** (*Nucleus Medical Media / Zack D. Films* 3D internal biology): Chapters 1, 2, 9 (`Long`) / Beats 00–03 (`Short`).
- **`STYLE_2_UE5_XRAY_CUTAWAY`** (*Fern / Jared Owen* translucent skeletal & vascular 3D cutaway + clean HUD telemetry): Chapters 3, 5, 7 (`Long`) / Beats 04–08 (`Short`).
- **`STYLE_3_DARK_MRI_MINIMALISM`** (*LEMMiNO* `#070B14` stark isolation of single neuron, macrophage, or red blood cell): Chapters 4, 6, 8 (`Long`) / Beats 09–13 (`Short`).
- **`STYLE_4_VOX_CLINICAL_SPLIT_RADAR`** (*Vox* clinical comparison & 3-panel physiological timeline triptych): Chapter 10 + chapter pivots (`Long`) / Beats 14–17 (`Short`).

## 4. High-CTR Flow-Native Thumbnail Contract

- **Resolution & Size**: `16:9` (`1280x720`, `< 2MB`), `9:16` (`1080x1920`, `< 2MB`).
- **Composition**: Flow-native dramatic 3D biomedical close-up depicting the single biological shock (e.g., translucent glowing 3D spine glowing red at neck vertebrae, or immune cells dimming inside crimson bloodstream) plus `2–4` crisp bold uppercase Vietnamese words (`MẤT 70% MIỄN DỊCH`, `ÁP LỰC 27 KG`, `ĐẠI NÁO DẠ DÀY`) rendered natively in `#F8FAFC` / `#06B6D4` / `#EF4444` inside clean upper negative space.
- **Prohibition**: Zero PIL/HTML solid box overlays, zero `✦` corner sparkle (`sparkle_unblend` required if any trace appears), zero blurry anatomical gore.

## 5. Modular FX Warehouse Integration (`archetype_3_science_xray`)

Plugs directly into `sys/fx_warehouse/` via `auto_select_beat_fx(..., channel_id="co_the_ke", video_topic=...)`:
- **Warehouse Pulls**: `xray_mode_switch_particles`, `parallax_push_in`, `chromatic_glitch_pulse`, `dual_oscilloscope_compare`, `laser_split_screen`, `triptych_3col_evidence`, `heartbeat_lub_dub.wav`, `bgm_scifi_biotech_pad.wav`.
- **Forbidden Jarring FX**: Zero vintage parchment/calligraphy (`calligraphy_quote_dissolve`) and zero war drums (`taiko_war_drum.wav`) on cellular/clinical beats.
- **Bespoke-Per-Topic Protocol**: For neurotransmitter synapses, hormone cascades, renal filtration, or posture mechanics not covered by generic counters, synthesize topic-specific `bespoke_hud_spec` + 48kHz stereo SFX via `build_bespoke_topic_hud_patch` / `synthesize_bespoke_topic_sfx`.
