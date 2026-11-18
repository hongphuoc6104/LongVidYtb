# Bipolar Chronicle Playbook — Chánh Niệm Kể (`chanh_niem_ke_bipolar_chronicle_v4` / V4.2 Topic-Agnostic Hybrid Line)

Complete technical, visual, acoustic, and narrative playbook implementing the `@SuDehieukhongphainho` documentary formula ([01..05_*.md](../../../../sys/runs/su_de_hieu_study/), [HYBRID_GIS_MAP_PLAN.md](../../../../sys/runs/chanh_niem_ke_chronicle_demo/HYBRID_GIS_MAP_PLAN.md), [HYBRID_FLOW_CODE_PLAN.md](../../../../sys/runs/chanh_niem_ke_chronicle_demo/HYBRID_FLOW_CODE_PLAN.md)) for **Chánh Niệm Kể** (`@ChanhNiemKeVN`) in its non-overlapping niche: **Giải Phẫu Thảm Họa Kỹ Thuật, Đại Dịch & Những Cú Sập Thay Đổi Nhân Loại Trên Bản Đồ** (*"Hiểu Đến Tận Gốc, Không Phải Nhớ Số Liệu"*).

---

## 0. V4.2 Topic-Agnostic Hybrid Production Line (One-Shot New Episode Blueprint)

Every module (`gis_map_baker.py`, `flow_hybrid_matting.py`, `bipolar_map_paper_engine.py`, `chronicle_audio_mixer.py`, `produce_chanh_niem_ke_chronicle.py`) is **100% topic-agnostic** (`0%` hardcoded disaster entities). To launch any new episode (e.g., **Ep02 Titanic 1912**, **Ep03 Bhopal 1984**, **Ep04 Fukushima 2011**, **Ep05 Đập Bản Kiều 1975**), an agent only creates `sys/runs/<job_id>/episode_manifest.json` + Long/Short scripts and executes `produce_chanh_niem_ke_chronicle.py`:

| Step | Owner Module / Shared Skill (`ref`) | Deterministic Input → Output Contract |
|---|---|---|
| **Bước 1: Manifest & Script** | `ref` `vp-research-architect` + `ref` `vp-scriptwriting` → `sys/runs/<job_id>/episode_manifest.json` | Defines `regions` (`region_aliases`, `definitions`, `local_zoom_overrides`), `country_aliases` (mapped to **Natural Earth 10m** `ISO_A3` / groups), `pin_coordinates`, `flow_assets` / asset maps (`2` thumbnails, `3–4` `cutaways_map` with `callouts` + `anchor_xy`, `4–6` `portraits_map`, `5–6` `plates_map`, `sprites_map`), `pronunciation_glossary`, `script_long_16x9.json`, `script_short_9x16.json`. |
| **Bước 2: GIS Map Baker** | `sys/fx_warehouse/gis_map_baker.py` | Downloads & caches **ESRI World Imagery + World Hillshade** tiles (`sys/assets/gis_cache/tiles/`) in **Web Mercator `EPSG:3857`**, merges **Natural Earth 10m** GeoJSON + `vietnam_sovereignty_override.geojson` (locking `HOÀNG SA` & `TRƯỜNG SA` to `VNM`), and pre-bakes `.npz` plates into `sys/assets/gis_cache/prebaked/` + 14 `#FFFFFF` SVG icons in `sys/assets/map_icons/*.svg` (`resvg_py`). |
| **Bước 3: Flow CDP + AI Matting** | `ref` `vp-flow-cdp` + `sys/fx_warehouse/flow_hybrid_matting.py` | Generates lean Flow pack (`0 credits` `BELUGA`; optionally `2–4` `Omni 1.2 Flash` I2V clips for climactic Living Polaroids). Runs `clean_and_crop_flow_image()` (sparkle removal + `1.045x` overscan), `matte_portrait_or_sprite()` (`rembg` `birefnet-portrait`/`birefnet-general`/`u2net` or border-seeded GrabCut + `scipy.ndimage.distance_transform_edt` `6.0px` `#FFFFFF` outline + drop shadow), and `prepare_cutaway_illustration()` (`#F4F3EE`). |
| **Bước 4: Voice & Foley Mix** | `ref` `vp-colab-bridge` + `sys/fx_warehouse/chronicle_audio_mixer.py` | Synthesizes `VietNarrator_chanh_niem_ke` (`KTTV Studio V3`, `226–232 syl/min` Hook/Body, `248–256 syl/min` Outro), variable `pause_after_s`, `10–14` Sparse Realistic Foley SFX cues, and BGM (`-20 dB` ducked / `+10 dB` pause swell), mastered to **`-11.0 LUFS / -1.0 dBTP`**. |
| **Bước 5: V4.2 GPU Render** | `ref` `vp-colab-bridge` + `ref` `vp-production` + `sys/fx_warehouse/bipolar_map_paper_engine.py` | Packages bundle to Colab T4 `h264_nvenc` (`30fps`), executes `blend_map_gpu()` (keeping Alps/mountain snow `#E49696`), `BeatOverlayCache` (~8x speedup), 6 Center-Stage & Split layouts, Zero-Halo Two-Pass Sweep, Metallic Double-Border Stamp, `audit_layout_boxes()`, watermark `W-w-36:H-h-36`, and mandatory `colab stop`. |

### Canonical `episode_manifest.json` Schema (Required Keys for New Topics)

```json
{
  "schema_version": "1.0",
  "channel_id": "chanh_niem_ke",
  "episode_id": "ep02_titanic",
  "topic": "Thảm họa tàu Titanic từ đầu đến cuối, dễ hiểu nhớ lâu",
  "job_id_long": "vn_chanh_niem_ke_ep02_titanic_long",
  "job_id_short": "vn_chanh_niem_ke_ep02_titanic_short",
  "long_script": "script_long_16x9.json",
  "short_script": "script_short_9x16.json",
  "thumbnails": {
    "long_16x9": "assets/thumbnail_long_16x9.png",
    "short_9x16": "assets/thumbnail_short_9x16.png"
  },
  "regions": {
    "region_aliases": {"north_atlantic_dem": "north_atlantic", "asia_vietnam": "east_asia_vietnam"},
    "definitions": {
      "north_atlantic": {"lon_min": -75.0, "lon_max": 5.0, "lat_min": 25.0, "lat_max": 62.0, "zoom_tile": 5, "force_vn_islands": false}
    },
    "local_zoom_overrides": {}
  },
  "country_aliases": {"uk": ["GBR"], "usa": ["USA"], "vietnam": ["VNM"]},
  "default_epicenter_lonlat": [-49.95, 41.73],
  "pin_coordinates": {"ĐIỂM VA CHẠM": [-49.95, 41.73], "SOUTHAMPTON": [-1.40, 50.90], "NEW YORK": [-74.00, 40.71]},
  "cutaways_map": {
    "presets": {
      "titanic_hull_bulkheads": {
        "image_path": "assets/cutaway_titanic_hull.png",
        "title": "MẶT CẮT THÂN TÀU TITANIC · VÁCH NGĂN CHỐNG NƯỚC",
        "callouts": [
          {"label": "VÁCH NGĂN KÍN NƯỚC", "side": "left", "label_xy": [0.03, 0.30], "anchor_xy": [0.38, 0.42]}
        ]
      }
    },
    "asset_ref_to_preset": {"hull_breach_schematic": "titanic_hull_bulkheads"}
  },
  "portraits_map": {"default": "assets/portrait_smith.png", "keywords": {"smith": "assets/portrait_smith.png"}},
  "plates_map": {"default": {"image_path": "assets/plate_shipyard.png", "caption": "XƯỞNG ĐÓNG TÀU HARLAND & WOLFF"}, "items": {}},
  "sprites_map": {"ocean_liner": {"image_path": "assets/sprite_ocean_liner.png", "label": "RMS TITANIC · 1912"}, "keywords": {}}
}
```

---

## 1. Visual Grammar: `chanh_niem_ke_bipolar_chronicle_v4` (V4.2 Hybrid Engine)

All visuals render at `30fps` via [bipolar_map_paper_engine.py](../../../../sys/fx_warehouse/bipolar_map_paper_engine.py) on **Colab T4 `h264_nvenc`** (never local CPU rendering), alternating deliberately between two high-contrast worlds (`0%` Static Hold). `BeatOverlayCache` pre-renders static overlay layers once per beat (~8x render acceleration).

### 1.1 World A — Real GIS Shaded-Relief Web Mercator Map (`map` / `map_mode`)
Used for geographic causality, dispersion plumes, pandemic corridors, maritime tracks, evacuation zones, and regional/global scale comparisons.

- **Real GIS Data & Projection (`gis_map_baker.py`):**
  - Web Mercator (`EPSG:3857`) isotropic `3840x2160` plates pre-baked from **ESRI World Imagery + ESRI World Hillshade** + **Natural Earth 10m** (`ne_10m_land.geojson`, `ne_10m_admin_0_countries.geojson`, `ne_10m_admin_0_boundary_lines_land.geojson`) + `vietnam_sovereignty_override.geojson`.
  - **3-Stop Luminance-Preserving Shader (`blend_map_gpu()` / `blend_map_cpu()`):** Maps valley (`L=0.15`), mid-plain (`L=0.45`), and mountain snow peaks (`L=0.95`) + high-pass detail injection (`(l_base - box_blur) * 0.45`) over deep ocean `#080B0E`:
    - Danger / Red (`#3A1214 -> #7B3638 -> #E49696`, glowing border `#FF6B6B` `2.5px`) — preserves bright coral-pink Alps/Caucasus/Himalaya snow ridges (`#E49696`).
    - Safe / Blue (`#162C3D -> #3A6788 -> #8CC2EB`, glowing border `#73B8FF` `2.5px`).
    - Warning / Amber (`#4A330E -> #9E7227 -> #EBD08A`, glowing border `#E5B51C` `2.5px`).
    - Neutral (`#3B3E3C -> #8A8D8A -> #F2F2EE`, border `#FFFFFF`).
- **Mandatory Sovereignty Rule (100% Hard-Lock):** Every frame showing Vietnam, the East Sea (Biển Đông), Southeast Asia, Asia, or World maps draws bold uppercase white labels **`HOÀNG SA`** (7 red cluster dots) and **`TRƯỜNG SA`** **exactly once** in screen-space (`render_gis_vector_overlays` / screen-space overlay), colored identically to Vietnam (`VNM`).
- **Clamped Continuous S-Curve Camera Rig (`clamp_camera_center()` + `3p^2 - 2p^3`):**
  - Consecutive `map` beats inherit `(cx, cy, zoom)` (`0.00s` seamless cut).
  - `clamp_camera_center()` clamps `(cx, cy)` inside `[half_w, 1 - half_w] x [half_h, 1 - half_h]` before GPU `grid_sample` crop — eliminating edge-smear artifacts.
  - 4 Presets: `push_in` (`+4%..+16%/s`), `pull_out` (`-3%..-15%/s`), `regional_pan` (`15–150 px/s @ 1080p`), `whip_pan` (`200–380 px/s @ 1080p`).
- **30fps GIS Vector Overlays & Hybrid Polaroid/Cutout on Map:**
  - Arc-length dotted Bezier trails (`o o o`, uniform `20px` spacing) led by upright `44x44px` rounded **Map Pin Badge** (`2.2px` white rim, bottom caret pointer, `#FFFFFF` SVG icon from `sys/assets/map_icons/*.svg` rendered via `resvg_py`).
  - **Bullseye Ripple** (red center, white rim, expanding ripple rings) + centered white pointer label box (`#FFFFFF` fill, `#111111` text, bottom pointer arrow directly above epicenter).
  - **3-Phase Shockwave Blast (`nuclear_shockwave_blast`)** & additive fireball/plume overlays, plus Hybrid Polaroid/Cutout overlays composited directly over moving terrain.

### 1.2 World B — Toroidally Seamless 3D Ridged Paper Collage (`paper` / `paper_mode`)
Used as a high-contrast pattern interrupt (`L1 > 120`) for engineering cutaways, quantitative proof, archival evidence, and human decision-makers.

- **3D Ridged-Crease Seamless Canvas (`build_seamless_paper_tile()`):** `#DCDCD7` base, `#E4E4E0` lit fold slopes, `#CBCBC6` shade slopes, `-7.6%` radial vignette, fine paper fiber grain, and continuous ambient drift (zero mirror seams; `70–82%` negative space).
- **6 Mandatory Center-Stage & Split Layout Archetypes (Zero Empty-Corner Frames):**
  1. `center_stack_typewriter`: Large centered vertical stack (`44–56pt` Typewriter pill + `72–82pt` Display Title + bullets/alert pill/counter/stamp across `Y: 22%–78%`).
  2. `staggered_numbered_thesis`: Yellow numbered thesis block (`#F5C518`) + staggered horizontal indentation for multi-tier thesis statements.
  3. `two_col_waffle_comparison`: Left column animated waffle pictogram grid (`1/4`..`1/100`, `#C5C7C2` inactive) + ratio badge; right column animated checklist (`[✓]` `#348B36` / `[✗]`) + red pill + stamp.
  4. `polaroid_split_right_stack`: Left/right tilted Washi-tape Polaroid (`±2–4°`, `#EAE8E1`, `#C8C3B2 @ 65%`, internal Ken Burns or I2V Living Polaroid clip) paired with a centered multi-tier typography stack (`date_pill` -> `title` -> `black_pill` -> `red_pill` -> `stamp`) filling the opposite column.
  5. `cutout_split_right_stack`: `6.0px` white-outlined B&W character/sprite cutout (`0.35s` `easeOutBack` slide-in) paired with a full opposite-column typography stack.
  6. `cutaway_annotated_stage` *(+ `paper_vector_schematic_map`)*: Central 2D Technical Cutaway image (`spec["image_path"]`, prepared at `#F4F3EE` with `0%` AI text) or crisp anti-aliased vector nodes/flows, flanked by left/right collision-free bent leader-line Vietnamese callouts (`label_xy` -> `anchor_xy`).

### 1.3 5-Tier Typography, Vietnamese Glyph Gate & Collision Guard (Both Worlds)
- **Vietnamese Glyph Gate (`verify_font_vietnamese_coverage()` via `TTFont`):** Every primary font (`BarlowCondensed-ExtraBold.ttf`, `Oswald-Bold.ttf`, `RobotoCondensed-Bold.ttf`, `IBMPlexMono-Bold.ttf`, `RobotoSlab-Bold.ttf`, `RobotoMono-Bold.ttf`) must cover 100% of all **134 Vietnamese accented characters**. Special symbols (`→ · × ✓ ✗ %`) automatically split-run fall back to `DejaVuSans-Bold.ttf` (`_split_runs_with_fallback()`), guaranteeing **`0` tofu `▯`**.
- **5 Tiers:**
  1. **Tier 1 — Two-Pass Mutually Exclusive Inverted Yellow Highlighter Sweep (`render_tier1_display_title()`):** Renders `base_layer` (`#FFFFFF` + drop shadow on Map, `#141414` on Paper) and `highlight_layer` (`#F5C518` solid bar + `#111111` **zero-shadow** text) separately; masks `x < sweep_x(t)` strictly from `highlight_layer` and `x >= sweep_x(t)` strictly from `base_layer` (`0.40s` sweep, **`0%` white/grey halo**).
  2. **Tier 2 — Yellow Date Pill (`#F5C518`):** `#111111` bold condensed timestamp/location anchor.
  3. **Tier 3 — Typewriter Black Pill (`#141414`, ~92% alpha):** `#FFFFFF` crisp `IBMPlexMono-Bold` context pill.
  4. **Tier 4 — Red Alert Pill (`#C83228`):** `#FFFFFF` uppercase pill for fatal thresholds, casualties, or system failures.
  5. **Tier 5 — Double-Border Metallic Grunge Stamp (`render_tier5_grunge_stamp()`):** SSAA 2x rendered on `rgba(12,12,12,0.68)` rounded backing (`radius=10px`) + outer `4.5px` / inner `2.0px` concentric double border + vertical metallic gradient **`#E87A3E -> #C84B20 -> #9E3414`** + subtle horizontal brushed streaks (`scale 1.25 -> 1.0` in `0.15s`, auto-censoring sensitive terms).
- **Mandatory Collision Guard (`audit_layout_boxes()`):** Enforces `safe_margin_top >= 95px`, `min_gap_y >= 20px` between all boxes, `left_safe_margin >= 51px`, and clear bottom-right `W-w-36:H-h-36` (`48px` @ 2K) watermark zone.
- **Asset Sourcing Guard:** NEVER prompt Flow `BELUGA` to draw maps, Vietnamese text overlays, bar charts, waffle grids, or text inside cutaways. Use `BELUGA` (`0` credits) solely for flat-bg portraits/sprites, archival Polaroid plates, `0%`-text 2D cutaways, and 5-layer Thumbnails (plus optional `2–4` `Omni 1.2 Flash` I2V clips for climaxes), processed through `flow_hybrid_matting.py`.

---

## 2. Audio, Voice & Sparse Foley Formula

Managed by [sys/assets/voices/ch_chanh_niem_ke/profile.json](../../../../sys/assets/voices/ch_chanh_niem_ke/profile.json) and [chronicle_audio_mixer.py](../../../../sys/fx_warehouse/chronicle_audio_mixer.py):

- **Voice Profile (`VietNarrator_chanh_niem_ke`):** KTTV Studio V3 calm northern Vietnamese male documentary voice (`F0 median ~148 Hz`), **`226–232 syllables/min`** (Hook/Body) and **`248–256 syllables/min`** (final 60s Outro).
- **Pre-TTS Pronunciation Normalizer:** Protects Hán-Việt compound words from mid-word pauses and maps foreign technical/place names from `episode_manifest.json["pronunciation_glossary"]` to smooth Vietnamese phonetics, plus `"khoảng"` softening on large numbers.
- **Variable Sentence Pauses (`pause_after_s`):** `0.48–0.75s` normal breath, `0.90–1.35s` emphasis/pivot, **`2.50–4.80s` every `~45–55s`** for **10–14 Sparse Realistic Foley SFX** (`geiger_counter_burst`, `steam_reactor_explosion`, `control_room_siren`, `sub_bass_chapter_boom`, `stamp_slam_thud`, `fire_crackle`, `telegraph_ticker`) — zero UI `pop`/`ding` spam.
- **BGM & Master Contract:** Continuous `>99%` coverage — *Documentary Tension Strings/Pulse* (Hook + Body) shifting to *Emotional Piano + Strings* (Outro), ducked **`-20 dB`** under speech (`+10 dB` swell in chapter pauses), mastered to **`-11.0 LUFS / -1.0 dBTP`**.

---

## 3. Storytelling & Script Formula ("Hiểu Đến Tận Gốc, Không Phải Nhớ Số Liệu")

### 3.1 Long `16:9` 5-Act Causal Domino Architecture
1. **Act 1 — Cold Open *In Medias Res* + Counter-Intuitive Paradox Hook:** Drop straight into the exact minute/location of failure (zero channel intro) and pose a paradox question.
2. **Act 2 — Root Design/System Flaw:** Explain *why* the system was fragile before the disaster using everyday mechanical analogies.
3. **Act 3 — The Domino Chain:** Trace each human/procedural delay where Step A forced Step B until safety margins vanished.
4. **Act 4 — The Collapse & Map Spread:** Track the explosion/spill/outbreak across the real GIS map, cover-up delays, and frontline human response.
5. **Act 5 — Scale Translation, Vietnam Micro-Bridges, Payoff & Soft CTA:** Translate abstract magnitudes into Vietnamese spatial/daily comparisons, show Asia/World map with `HOÀNG SA` & `TRƯỜNG SA`, close the opening loop, and end with **`"Các bạn thấy thế nào? Cùng chia sẻ cảm nhận của các bạn nha."`** (`0%` like/share/subscribe begging).

### 3.2 Six "Dịch Sang Đời Thường" Techniques & 4 Colloquial Connectors
1. **Physical Scale Translation:** Never leave raw figures isolated (`2,000 tons` -> *"nặng ngang khoảng 1.000 chiếc ô tô con"*; `1/30` or `1/100` waffle ratios).
2. **Social/Everyday Analogies:** Explain engineering & epidemiology as familiar human habits/workplace shortcuts rather than textbook jargon.
3. **4 Colloquial Connectors:** Anchor flow with **`Thế nhưng mà`**, **`Thế nên là`**, **`Tức là`**, and **`khoảng`** (avoid stiff `"Tuy nhiên"`, `"Do đó"`).
4. **One-Touch Transitions & Open Loops/Callbacks:** `"Rồi, giờ chúng ta sẽ đến với..."`, `"Trong lúc A đang..., thì ở B..."`, planting early details that pay off in Act 4/5.
5. **Vietnam Micro-Bridges:** Compare radii/distances/impacts to familiar Vietnamese geography (e.g., Hanoi–Hai Phong corridor) and national monitoring context.
6. **Deadpan Irony:** Highlight the tragic absurdity of bureaucratic cover-ups and flawed incentives in calm, understated documentary phrasing.

### 3.3 Spin-Off Short `9:16` Contract (`48–56s`, `18–22` Beats)
- Linked via `parent_long_id` to the Long episode; `youtube_title <= 55` chars.
- **First sentence `<= 18` syllables** with counter-intuitive hook and **zero pauses in the first 15s**.
- Alternates World A GIS DEM Map + World B Wrinkled Paper in `1080x1920` / `1440x2560`.
- **Final 15% (`<= 38` syllables combined):** Natural close CTA + explicit channel bridge inviting viewers to tap **`@ChanhNiemKeVN`** (*Chánh Niệm Kể*) for the full Long breakdown (zero banned CTA phrases).

---

## 4. Packaging: Title & 5-Layer Thumbnail Blueprint

- **Title Formula:** `"[Chủ đề thảm họa] từ đầu đến cuối, dễ hiểu nhớ lâu"` (`<= 55` chars; Pilot Ep01 Long = `"Thảm họa Chernobyl từ đầu đến cuối, dễ hiểu nhớ lâu"`, 51 chars; Short = `"Vì sao nút dừng khẩn cấp lại làm nổ lò Chernobyl?"`, 49 chars).
- **5-Layer Flow-Native Thumbnail (`1280x720` Long & `1080x1920` Short, `< 2MB`):**
  1. Double dark document border frame.
  2. Weathered vintage/dark geopolitical map (dark sea `#2E2521`, terracotta hazard `#7B3638`).
  3. Glowing orange flashpoint ring at the disaster epicenter + `3` bold vector arrows radiating outward.
  4. Top-left cream double-border card (`#EFE8D5`) with bold dark condensed title (`2–4` words per line) + bottom-left date stamp.
  5. Bottom-right high-contrast B&W/sepia cutout portrait of the key catalyst figure looking straight into the lens.
