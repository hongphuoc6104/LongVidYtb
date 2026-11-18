# Visual Grammar — `ho_so_ky_la_3d_noir_forensic_v3`

Reference specification for generating 3D Noir Forensic Diorama photography paired with the 4-mode investigative visual storytelling system (`MODE_1`..`MODE_4`) on **Hồ Sơ Kỳ Lạ (`ho_so_ky_la`)**.

## 1. Base 3D Noir Forensic Realism (3 Pillars) & Hygiene Constraints

Raw Flow (`BELUGA`) generation MUST strictly enforce `allowed_text=None` (`strictly zero text`, zero newspaper gibberish headlines, zero random telemetry digits, zero AI corner watermarks) and depict tactile forensic investigation aligned directly with the spoken beat:

1. **Pillar 1 — 3D Noir Crime-Scene & Incident Diorama**: Miniature architectural scale models, cutaway cabins/compartments, terrain elevation reconstructions, and foggy exterior crime-scene dioramas lit by a single 45-degree directional volumetric spotlight against deep night shadows.
2. **Pillar 2 — 100mm Forensic Macro & Mechanical Telemetry**: Close-up physical examination of critical engineering failures, brushed brass pressure gauges, black-box switches (`MAN`/`AUTO`), torn oxygen valves, taut red evidence threads, parchment flight/maritime charts, and metallurgical fractures captured at shallow depth of field (`f/2.0–f/2.8`).
3. **Pillar 3 — Atmospheric Archival Field Reconstruction**: Cold rainy asphalt, shadowy runways, derelict hulls, high-altitude cockpit interiors bathed in eerie instrument glow, and misty alpine/oceanic search environments rendered with intellectual gravitas.

### Locked Color Palette & Anti-Repetition Guardrails
- **Midnight Investigation Obsidian**: `#0A0B0E`
- **Dark Slate Dossier Desk / Concrete**: `#181B22`
- **Aged Parchment / Forensic Files**: `#E8DFC8`
- **Evidence Laser / Crimson Investigation Thread**: `#C0392B`
- **Brushed Brass / Black-Box Hardware**: `#C9A24D`
- **Zero Gore & Zero Cartoon Slop**: Strictly zero graphic blood, zero screaming/distorted human faces, zero 2D flat stick figures (`stickman`), zero neon cyberpunk clutter.
- **Anti-Repetition**: Vary diorama scale, camera angle, and mechanical focus across consecutive beats; never lock the same corkboard prop across unrelated narrative scenes.
- **Clean Corner Pipeline**: Apply `1.045x` overscan crop and run FFmpeg bottom-right `delogo` (`_compute_bottom_right_delogo_filter`) **before** overlaying `watermark_150x150.png` at `W-w-48:H-h-48` (2K) or `W-w-36:H-h-36` (HD).

## 2. Four Investigative Visual Modes (`Long 16:9` at `2560x1440`)

Combine all 4 modes across each `260`-beat episode to sustain tension and make complex technical reconstructions immediately scannable:

| Mode Code | Target Share | Trigger in Narration | 2K (`2560x1440`) Composition & Overlay Spec |
|---|---|---|---|
| **`MODE_1_EVIDENCE_STAMP`** | **~15% beats** | Crucial timestamps, altitude/pressure thresholds, black-box anomalies, or decisive forensic pivots (e.g., `12.040 FT`, `MAN MODE`, `121 NGƯỜI`) | Dark vignette scrim (`#0A0B0E` @ 60–75% opacity) over 3D Noir scene + bold evidence metric in brass gold `#C9A24D` / forensic crimson `#C0392B` and crisp clean white `#E8DFC8` subhead (`<= 6` words), clear of watermark safe zone. |
| **`MODE_2_HYPOTHESIS_CONTRAST`** | **~12% beats** | Comparing competing theories, expected vs actual instrument state (`AUTO` vs `MAN`), or pilot belief vs forensic reality | Clean vertical glowing `#C0392B` / `#C9A24D` split framing two contrasting 3D Noir scenes with concise top/bottom forensic tags (`<= 4` words per side). |
| **`MODE_3_DOSSIER_CHECKLIST`** | **~15% beats** | Sequential failure chains, 3-step official investigation findings (e.g., AAIASB root causes), or physical clue eliminations | Left-weighted 3D Noir scene clearance + right-docked dark archival dossier card (`#181B22` @ 88% opacity, `#C9A24D` / `#C0392B` border) displaying up to 3 sequential clues (`[01]`, `[02]`, `[03]`). |
| **`MODE_4_NOIR_CINEMATIC_PACING`** | **~58% beats** | Atmospheric transitions, flight/voyage progression, suspense builds, and field reconstructions | Uncluttered clean full-bleed 3D Noir frame with smooth `2560x1440@30fps` static Lanczos pacing (`xfade=fade:duration=0.24`) and optional key-beat `omni_flash` I2V clips. |

## 3. Four Creative Visual Style Options (`Long 16:9` Breakthrough Catalog)

Instead of repetitive miniature tabletop props or strings, `ho_so_ky_la` supports **4 creative visual style directions** (2 sub-beats/sentence at `~2.2s–2.5s/frame`, strictly forbidding `scale model`, `miniature`, `toy`, `strings`, `pedestal` on live-action/3D X-ray/minimalist beats):

| Style ID | Reference Benchmark | Core Visual Grammar & Graphic Layer |
|---|---|---|
| **`STYLE_1_IMAX_35MM_LIVE_ACTION`** | Netflix *Mayday* / Fincher / *Sử Kể Lại* Option 1 | Full-scale 35mm Kodak Vision3 500T thriller docudrama (`5600K` cold altitude mist vs `2200K` red cockpit glow; strict OTS & 100mm hardware macros, zero AI close-up faces) + lightweight `.ass` subtitles & thin typewriter timestamp tag |
| **`STYLE_2_FERN_3D_XRAY_CUTAWAY`** | *Fern* / *Hoog* / *Jared Owen* | Unreal Engine 5 / Octane translucent X-ray fuselage & cockpit cutaway in full flight environment showing glowing airflow/circuit pathways & faceless translucent 3D pilot silhouettes + clean telemetry HUD tag & `.ass` subtitles |
| **`STYLE_3_LEMMINO_CHIAROSCURO_ARCHIVE`** | *LEMMiNO* / *Barely Sociable* | Stark chiaroscuro monochrome minimalism (`>= 65%` `#07080C` obsidian negative space, silver/crimson volumetric rim-light, single hanging oxygen mask, red CVR black-box waveform, backlit silhouette) + minimalist archival stamp & `.ass` subtitles |
| **`STYLE_4_VOX_INVESTIGATIVE_SPLIT_RADAR`** | *Johnny Harris* / *Vox Dark-Mode* | Multi-frame investigative storytelling combining dark aerial satellite radar reticle (`FL340`, dashed flight path), 2-panel split-screen contrast (`AUTO` vs `MAN`), and 3-column vertical triptych progression (`01`, `02`, `03`) + `.ass` subtitles |

### Combined 4-Style Allocation Contract (`Long 16:9` 10 Chapters / `Short 9:16` 18 Beats)
- **Long `16:9` (`260` beats)**: Chapters 1, 2, 9 -> `STYLE_1_IMAX_35MM_LIVE_ACTION` (`78` beats); Chapters 3, 5, 7 -> `STYLE_2_FERN_3D_XRAY_CUTAWAY` (`78` beats); Chapters 4, 6, 8 -> `STYLE_3_LEMMINO_CHIAROSCURO_ARCHIVE` (`78` beats); Chapter 10 + chapter-end synthesis pivots -> `STYLE_4_VOX_INVESTIGATIVE_SPLIT_RADAR` (`26+` beats).
- **Short `9:16` (`18` beats)**: Beats 00–03 -> `STYLE_1`; Beats 04–08 -> `STYLE_2`; Beats 09–13 -> `STYLE_3`; Beats 14–17 -> `STYLE_4`.

## 4. High-CTR Flow-Native Thumbnail Contract

- **Resolution & Size**: `16:9` (`1280x720`, `< 2MB`), `9:16` (`1080x1920`, `< 2MB`).
- **Composition**: Flow-native dramatic 3D Noir close-up of the single core forensic anomaly (e.g., cockpit pressurization switch turned to red `MAN` with an F-16 wingtip silhouette in misty night clouds) plus `2–4` bold uppercase Vietnamese words (`CHUYẾN BAY MA`, cream `#E8DFC8` / crimson `#C0392B`) drawn directly into clean upper corner negative space.
- **Prohibition**: Zero offline PIL/HTML gradient overlay cards pasted over raw images; keep bottom-right clear for YouTube duration badge.

## 5. Modular FX Warehouse Integration & Bespoke-Per-Case Rule

`ho_so_ky_la` plugs directly into [vp-motion-fx-warehouse](../../vp-motion-fx-warehouse/SKILL.md) and the sharded `sys/fx_warehouse/` sub-modules (`archetypes`, `camera_vfx`, `hud_widgets`, `audio_sfx_bgm`, `selector`) via `selector.auto_select_beat_fx(..., channel_id="ho_so_ky_la", video_topic=...)`:

- **Shared Warehouse Mapping (4 Styles)**:
  - `STYLE_1_IMAX_35MM_LIVE_ACTION`: pulls subtle sub-pixel `camera_vfx` + `MODE_1_EVIDENCE_STAMP` typewriter/evidence stamp widgets (`hud_widgets`) + tense noir foley (`audio_sfx_bgm`).
  - `STYLE_2_FERN_3D_XRAY_CUTAWAY`: pulls 3D X-ray HUD overlays and Dual Oscilloscope telemetry widgets (`hud_widgets`) + mechanical/electrical diagnostics SFX.
  - `STYLE_3_LEMMINO_CHIAROSCURO_ARCHIVE`: pulls chiaroscuro archival stamps and CVR black-box waveform widgets + minimalist low-end drone/tape-hiss stems.
  - `STYLE_4_VOX_INVESTIGATIVE_SPLIT_RADAR`: pulls radar reticle, 2-panel laser split, and 3-column vertical triptych (`01`, `02`, `03`) layouts from `hud_widgets`.
- **Non-Forced Bespoke Rule**: Aviation-specific HUDs (`FL340`, altimeter/pressurization gauges, cockpit CVR waveforms) are **only** for aviation cases. Whenever a case file involves a maritime sinking, chemical/poisoning toxicology, cold-case ballistics, or cipher mystery where the shared catalog lacks an exact thematic fit, the pipeline MUST synthesize a bespoke per-video/per-topic HUD (`bespoke_hud_spec` via `build_bespoke_topic_hud_patch`) and procedural 48kHz stereo SFX (`bespoke_sfx_spec` via `synthesize_bespoke_topic_sfx`)—never forcing aviation HUDs onto unrelated mysteries.
