# Visual Grammar — `ban_do_quyen_luc_4styles_photoreal_v3`

Reference specification for generating 3-pillar photorealistic documentary photography paired with the 4-mode visual storytelling combination (`CACH_1`..`CACH_4`) on **Bản Đồ Quyền Lực (`ban_do_quyen_luc`)**.

## 1. Base Photorealism (3 Pillars) & Anti-Repetition Diversity Rules

Raw Flow (`BELUGA`) generation MUST strictly obey `allowed_text=None` (`zero text, zero labels, zero map letters, zero watermarks`) and depict authentic physical reality matched directly to the spoken beat:

1. **Pillar 1 — Orbital Satellite Relief & Geological Geography**: True-color 3D satellite topography, high-altitude strait/pass views, continental shelves, open-pit mining terraces, hydrological basins, and shipping corridors seen from space or high altitude.
2. **Pillar 2 — 100mm Macro Engineering & Physical Supply-Chain Mechanisms**: Real physical machinery, high-purity wafers, industrial centrifuges, rare-earth magnets, optical mirrors, turbine blades, deep-sea pipelines, or cargo container locks shot with authentic shallow depth of field (`f/2.0–f/2.8`).
3. **Pillar 3 — On-Site Industrial, Maritime & Geopolitical Field Documentary**: Real cargo vessels queuing in narrow straits, smelter furnaces, port gantry cranes, border logistics hubs, power grids, and industrial cleanrooms under realistic atmospheric lighting.

### Strict Anti-Repetition Constraints (Cross-Beat & Cross-Episode Diversity)
- **Never Lock a Single Prop or Surface**: Strictly forbidden from recycling the same dark walnut tabletop, wooden desk, brass caliper, leather portfolio, or crimson steel C-clamp across unrelated beats or episodes.
- **Subject-to-Environment Coherence**: Every foreground object must inhabit its authentic real-world industrial, geographical, or engineering environment (e.g., semiconductor wafers inside a cleanroom lithography chamber, ore rocks inside an open-pit quarry, container ships in oceanic fog).
- **Zero Sci-Fi / Flat Vector Slop**: Zero glowing neon HUDs, zero hologram radar circles, zero flat 2D clip-art cartoons, zero AI gibberish typography inside generated images.
- **Clean Margin Preprocessing**: Apply `clean_beluga_sparkle_pil` and `1.045x` overscan crop before compositing so edge artifacts and Flow watermarks never enter the 2K frame.

## 2. Four-Mode Visual Storytelling Combination (`4 Cách Kết Hợp`)

To eliminate visual fatigue in `9–10m` long explainers and amplify comprehension of complex numbers, contrasts, and causal chains, every `long_16x9` episode combines 4 storytelling visual modes rendered natively at `2560x1440`:

| Mode Code | Target Share | Trigger in Narration | 2K (`2560x1440`) Composition & Typography Geometry |
|---|---|---|---|
| **`CACH_1_HERO_STAMP`** | **~15% beats** | Shocking figures, percentages, bottleneck thresholds, or decisive chapter hooks (e.g., `92%`, `2.000 TẤN`, `KHÓA VAN`) | Full-bleed dark gradient scrim (`#060A12` @ 55–75% opacity over dramatic photoreal base) + centered or lower-third giant kinetic hero metric (`156px` Bold gold `#FFD60A` or amber `#FFB703` with subtle dark drop shadow) + concise `68px` uppercase/clean sans-serif white `#FFFFFF` subhead (`<= 6` words). Zero clutter inside watermark safe zone. |
| **`CACH_2_SPLIT_COMPARE`** | **~12% beats** | Explicit geopolitical asymmetries, before/after shifts, raw export vs high-value monopoly, or rival chokepoints | Clean vertical/diagonal `2px` glowing divider splitting two complementary photorealistic frames (`Left / Red #FF3B30` pressure badge vs `Right / Cyan-Teal #00F5D4` leverage badge). Top/bottom pill labels (`40px` Bold, `<= 4` words per side) keeping >=70% unobstructed imagery per half. |
| **`CACH_3_DOSSIER_LIST`** | **~15% beats** | Multi-tier enumerations, 3-step dependency chains, sequential chokepoint causes, or industrial processing stages | Subject photo positioned with focal clearance on the left 58% + right-docked dark glassmorphic intelligence dossier card (`#0B1220` @ 86% opacity, `1px` `#38BDF8`/`#FFB703` border) displaying `3` numbered checklist items (`[01]`, `[02]`, `[03]`) with status tags (`#FFB703` amber / `#FF3B30` red). Progressive reveal or clean consolidated view. |
| **`CACH_4_CINEMATIC_PACING`** | **~58% beats + transitions** | Continuous narrative flow, geographic transitions, and atmospheric scene changes | Uncluttered clean full-bleed photorealistic frame with smooth 2K camera pacing (`zoom_in_center`, `zoom_out_reveal`, `pan_left_to_right`, `pan_right_to_left` using `1.12x` overscan crop; optional `omni_flash` I2V clips on flagship climax beats) bridged by `xfade=fade:duration=0.18`. |

## 3. High-CTR Flow-Native Thumbnail Contract

- **Resolution & Size**: `16:9` (`1280x720`, `< 2MB`), `9:16` (`1080x1920`, `< 2MB`).
- **Composition**: Flow-native dramatic conflict or bottleneck photography showing the real geopolitical/resource subject in high contrast with `2–4` bold Vietnamese uppercase words (gold `#FFD60A` / cream `#FFFFFF` with crisp dark stroke) placed in clean upper/corner negative space away from YouTube timestamp (`bottom-right`).
- **Prohibition**: Strictly zero fake PIL gradient overlay cards appended offline on top of raw images, zero repetitive tabletop props or steel clamps, and zero clickbait arrows covering faces/subjects.
