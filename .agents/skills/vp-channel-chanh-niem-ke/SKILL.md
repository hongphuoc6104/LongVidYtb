---
name: vp-channel-chanh-niem-ke
description: "Dedicated channel specifications for Hiểu Tận Gốc (internal slug chanh_niem_ke, @HieuTanGocVN). Permanent V5.0 Topic-Agnostic Hybrid Production Line for Causal Disaster, Pandemic & Engineering Collapse Chronicles ('Hiểu Đến Tận Gốc, Không Phải Nhớ Số Liệu') combining Real GIS Web Mercator Maps (ESRI + Natural Earth 10m + HOÀNG SA/TRƯỜNG SA), Flow CDP + AI Matting, KTTV Studio V3 voice + Sparse Foley (-11.0 LUFS), Bipolar 30fps GPU Engine V5.0, Option W1 Dark-Slate Circular Watermark, and explicit branching refs to shared Video Pilot skills."
---

# Hiểu Tận Gốc (`chanh_niem_ke` / `@HieuTanGocVN`) — Dedicated Channel Specifications (V5.0 Topic-Agnostic Hybrid Production Line)

Channel-specific specification module for **Hiểu Tận Gốc** (`@HieuTanGocVN`, internal repo slug `chanh_niem_ke` retained for codebase continuity, YouTube Channel ID `UCXEFl4mz5LYr84ym7t1eI4A`, Chrome `profile_7`, CDP port `9228`, `Profile 11`, email `phuocnguyenne01@gmail.com`). Legacy mindfulness videos (`FMupcF80q4k`, `Yn42xhCRCUY`, `FHjg3LM1SWc`, etc.) are quarantined as **`PRIVATE`** on YouTube Studio.

- **Niche (0% Portfolio Overlap):** *Giải Phẫu Thảm Họa Kỹ Thuật, Đại Dịch & Những Cú Sập Thay Đổi Nhân Loại Trên Bản Đồ* (*Causal Disaster, Pandemic & Engineering Collapse Chronicles — "Hiểu Đến Tận Gốc, Không Phải Nhớ Số Liệu"*). Strictly non-overlapping with `ban_do_quyen_luc` (contemporary geopolitics/chokepoints), `su_ke_lai` (military wars), `ho_so_ky_la` (unsolved 3D noir mysteries), `co_the_ke` (organ-level physiology), and `minh_triet_song` / `tam_tinh_dem` / `loi_sang_soi` (philosophy/mindfulness/parables).
- **Topic-Agnostic Guarantee:** All visual, GIS, matting, and audio modules (`gis_map_baker.py`, `flow_hybrid_matting.py`, `bipolar_map_paper_engine.py`, `chronicle_audio_mixer.py`, `produce_chanh_niem_ke_chronicle.py`) are 100% **manifest-driven** (`sys/runs/<job_id>/episode_manifest.json`) with **0% hardcoded episode content**. Producing any new episode (e.g., *Ep02 Titanic 1912*, *Ep03 Bhopal 1984*, *Ep04 Fukushima 2011*, *Ep05 Đập Bản Kiều 1975*) only requires authoring `episode_manifest.json` + Long/Short scripts and running the pipeline once.
- **Benchmark Formula Source:** Calibrated from [01_channel_and_packaging_report.md](../../../sys/runs/su_de_hieu_study/01_channel_and_packaging_report.md), [02_video1_visual_motion_fx.md](../../../sys/runs/su_de_hieu_study/02_video1_visual_motion_fx.md), [03_video2_visual_motion_fx.md](../../../sys/runs/su_de_hieu_study/03_video2_visual_motion_fx.md), [04_script_voice_sfx_formula.md](../../../sys/runs/su_de_hieu_study/04_script_voice_sfx_formula.md), and [05_vp_channel_fit_and_tech_gap.md](../../../sys/runs/su_de_hieu_study/05_vp_channel_fit_and_tech_gap.md).
- **Read Together With:** [references/bipolar_chronicle_playbook.md](references/bipolar_chronicle_playbook.md) for the complete 5-Step V4.2 Hybrid Production Line, `episode_manifest.json` schema, 6 Center-Stage & Split layouts, Two-Pass Zero-Halo Highlighter Sweep, Metallic Double-Border Stamp, GIS shader math, and 5-Act domino script rules.

---

## V4.2 Topic-Agnostic Hybrid Production Line (5 Permanent Steps)

Any agent producing a new `chanh_niem_ke` episode executes these 5 deterministic steps in order:

1. **Bước 1 — `episode_manifest.json` + Kịch bản Long/Short:**
   - Author `sys/runs/<job_id>/episode_manifest.json` defining all topic parameters cleanly:
     - `regions` (`region_aliases`, `definitions` with `lon_min/lon_max/lat_min/lat_max/zoom_tile/force_vn_islands`, `local_zoom_overrides`),
     - `country_aliases` & `country_groups` mapped to canonical **Natural Earth 10m** `ISO_A3` codes (including historical blocs such as `USSR`, `INDOCHINA`, `SCANDINAVIA`),
     - `pin_coordinates` (`[lon, lat]` anchors for city/site bullseyes and trajectories),
     - `flow_assets` / asset registries: `thumbnails` (`2`: `long_16x9` `1280x720`, `short_9x16` `1080x1920`), `cutaways_map` (`3–4` 2D technical cutaway presets with `image_path`, `title`, and `callouts` containing `label`, `side`, `label_xy`, `anchor_xy` + `asset_ref_to_preset`), `portraits_map` (`4–6` key historical/catalyst figures), `plates_map` (`5–6` archival photo plates), and `sprites_map` (vehicles/ships/helicopters/equipment),
     - `pronunciation_glossary` + `script_long_16x9.json` (`5-Act Causal Domino`) + `script_short_9x16.json` (`48–56s`, `parent_long_id`).
2. **Bước 2 — GIS Terrain Pre-Baking (`sys/fx_warehouse/gis_map_baker.py`):**
   - Automatically fetches & caches `ESRI World Imagery` + `ESRI World Hillshade` XYZ tiles (`sys/assets/gis_cache/tiles/`) under **Web Mercator `EPSG:3857`**.
   - Loads **Natural Earth 10m** GeoJSON (`ne_10m_land.geojson`, `ne_10m_admin_0_countries.geojson`, `ne_10m_admin_0_boundary_lines_land.geojson`) merged with `vietnam_sovereignty_override.geojson` (hard-locking `HOÀNG SA` & `TRƯỜNG SA` to `VNM`).
   - Pre-bakes isotropic `3840x2160` `.npz` region plates (`l_base`, `land_mask`, `country_id_map`, `country_records_json`, `border_lines_json`, `country_borders_json`, `meta_json`) into `sys/assets/gis_cache/prebaked/`, paired with 14 `#FFFFFF` SVG map pin icons (`sys/assets/map_icons/*.svg` rendered via `resvg_py`).
3. **Bước 3 — Lean Flow CDP + 3D Cutaways + Omni 1.2 Flash Mechanism Clips (`vp-flow-cdp` + `sys/fx_warehouse/flow_hybrid_matting.py`):**
   - Generate photorealistic **3D Studio Cutaways** (`0` credits `BELUGA`, Unreal Engine 5 / Octane isometric cross-sections on clean solid `#141619` dark charcoal studio background, strictly `0%` embedded text), warm muted **1986 Svema Documentary Color Plates** (`archival_warm`, `0.74–0.82` saturation), flat-background portraits/sprites, 2 Flow-native 5-layer thumbnails (`0` credits `BELUGA`), plus **`Omni 1.2 Flash` `6s` `16:9` 3D mechanism video clips** (`flow_videos` in `episode_manifest.json` via `FlowVideoChainOrchestrator(ChainMode.SCENE_PAIRS)`) chained directly to the 3D BELUGA keyframes so complex physics principles play live inside schematic viewports at `30fps`.
   - Never ask Flow AI to generate maps, Vietnamese typography overlays, bar charts, or waffle grids. Every consecutive schematic or Polaroid beat in both Long and Short MUST map to a distinct `(image_path, video_path, focus_xy)` / plate view (`0` consecutive repetitions).
   - Post-process deterministically via `flow_hybrid_matting.py` & `produce_chanh_niem_ke_chronicle.py`: `clean_and_crop_flow_image()`, `matte_portrait_or_sprite()` (`rembg`/GrabCut + `distance_transform_edt` `6.0px` `#FFFFFF` sticker outline), `process_archival_plate()` (natural `0.82` documentary color contrast), and dark-studio viewport framing in `bipolar_map_paper_engine.py`.
4. **Bước 4 — Voice, Variable Pauses & Sparse Foley Mix (`sys/fx_warehouse/chronicle_audio_mixer.py`):**
   - Synthesize via remote Colab T4 OmniVoice (`vp-colab-bridge`) using `VietNarrator_chanh_niem_ke` (`KTTV Studio V3`, `F0 ~148 Hz`, `226–232 syl/min` Hook/Body, `248–256 syl/min` Outro) with Pre-TTS Pronunciation Normalization.
   - Assemble with context-variable `pause_after_s` (`0.48–0.75s` normal breath, `0.90–1.35s` emphasis, `2.50–4.80s` every `~45–55s` for `10–14` Sparse Realistic Foley SFX cues such as `geiger_counter_burst`, `steam_reactor_explosion`, `control_room_siren`, `sub_bass_chapter_boom`, `stamp_slam_thud`, `fire_crackle`, `telegraph_ticker`).
   - Mix Documentary Tension Strings/Pulse + Emotional Piano Outro BGM (`-20 dB` ducked under voice, `+10 dB` swell in chapter pauses) and 2-pass master to **`-11.0 LUFS / -1.0 dBTP`**.
5. **Bước 5 — Bipolar V4.3 30fps GPU Render & Audit (`sys/fx_warehouse/bipolar_map_paper_engine.py` + Colab T4 `h264_nvenc`):**
   - Orchestrate via `sys/tools/produce_chanh_niem_ke_chronicle.py` (`--manifest .../episode_manifest.json`), bundling fonts, prebaked `.npz`, `map_icons/*.svg`, and all `assets/*.png` + `assets/*.mp4` mechanism clips to Colab T4 (`h264_nvenc`).
   - Render `30fps` using `blend_map_gpu()` (3-stop luminance-preserving territory shader), `clamp_camera_center()`, `BeatOverlayCache` (with live `cv2.VideoCapture` decoding for `schematic_video_cap` + `focus_xy` smooth push-in zooms), 6 Center-Stage & Split layouts (`9:16` symmetric margins `safe_left = safe_right = 44*scale`, device-agnostic centered stacks, enlarged `78–84px` titles / `40–48px` pills / `780x580` Polaroids, and **Bottom Callout Dock** `<=3` numbered rows @ `25px` bold under a `96–100%` safe-width 3D/video viewport; `16:9` side columns `<=4` callouts @ `25px` bold), Tight Cap-Height `#FAD01A` Highlighter Sweep, 90-degree Courier Tape Strips, Transparent Crimson Grunge Stamp, `verify_font_vietnamese_coverage()`, `audit_layout_boxes()` (`0` collisions), and watermark `W-w-36:H-h-36`. Always `colab teardown` after render.

---

## Shared Workflow ↔ Dedicated `chanh_niem_ke` Branching Matrix (`ref`)

Shared workflow skills remain **100% unmodified** for all other 19 channels. `chanh_niem_ke` plugs into shared Video Pilot skills via explicit `ref` handoffs:

| Pipeline Step | Shared Video Pilot Skill (`Unmodified`) | `chanh_niem_ke` Branch & Manifest Handoff (`ref`) |
|---|---|---|
| **1. Research & Packaging** | `ref` [vp-research-architect](../vp-research-architect/SKILL.md) *(shared)* | Produce causal 5-Act domino dossier + `youtube_title <= 55` chars (`"[Thảm họa] từ đầu đến cuối, dễ hiểu nhớ lâu"`), Short `<= 55` chars linked via `parent_long_id`, and 5-Layer Flow-Native Thumbnail specs (`1280x720` & `1080x1920`, `< 2MB`). Author `episode_manifest.json` (`regions`, `country_aliases`, `pin_coordinates`, `flow_assets` / `cutaways_map`, `portraits_map`, `plates_map`, `sprites_map`). |
| **2. Script & Storytelling** | `ref` [vp-scriptwriting](../vp-scriptwriting/SKILL.md) + `script_cadence_checker.py`, `script_diversity_linter.py`, `cta_tone_linter.py` *(shared)* | Apply [bipolar_chronicle_playbook.md](references/bipolar_chronicle_playbook.md): 5-Act Causal Domino, 6 "Dịch Sang Đời Thường" techniques, 4 colloquial connectors (`Thế nhưng mà`, `Thế nên là`, `Tức là`, `khoảng`), Vietnam micro-bridges, Long Soft CTA (`"Các bạn thấy thế nào? Cùng bình luận góc nhìn của bạn nha."`), Short `<= 18` syl hook (`0s` pause first `15s`) + **Hiểu Tận Gốc** channel bridge in final 15% (`<= 38` syl, never raw `@Handle` in TTS). |
| **3. GIS Map & Asset Harvest** | `ref` [vp-flow-cdp](../vp-flow-cdp/SKILL.md) + `.agents/rules/gpu-headless-chrome.md` *(shared)* | **BRANCH `ref` → `gis_map_baker.py` + `flow_hybrid_matting.py`:** Pre-bake region `.npz` plates (`ESRI + Natural Earth 10m + vietnam_sovereignty_override.geojson`). Harvest `BELUGA` (`0` credits, optionally `2–4` single-scene `Omni 1.2 Flash` clips) ONLY for portraits, plates, and cutaways (`0%` text) -> `clean_and_crop_flow_image` -> `matte_portrait_or_sprite`. 5-Layer Thumbnails (`thumbnail_long_16x9.png` `1280x720` RGB, `thumbnail_short_9x16.png` `1080x1920` RGB `<2MB`) use deterministic GIS parchment plates + `#EFE8D5` double-bordered cards + `0px` white outline B&W portrait cutouts (`@SuDehieukhongphainho` template). |
| **4. Voice, Pauses & Audio** | `ref` [vp-colab-bridge](../vp-colab-bridge/SKILL.md) for Colab T4 OmniVoice GPU *(shared)* | **BRANCH `ref` → `sys/assets/voices/ch_chanh_niem_ke/profile.json` + `chronicle_audio_mixer.py`:** `VietNarrator_chanh_niem_ke` (`KTTV Studio V3`, `226–232 syl/min` Hook/Body, `248–256 syl/min` Outro), variable `pause_after_s`, `10–14` Sparse Realistic Foley SFX, BGM `-20 dB` ducking, `-11.0 LUFS / -1.0 dBTP`. |
| **5. Visual Engine & Render** | `ref` [vp-colab-bridge](../vp-colab-bridge/SKILL.md) & [vp-production](../vp-production/SKILL.md) *(overrides default `1.7.0 handdrawn_2d_explainer` via `produce_chanh_niem_ke_chronicle.py`)* | **BRANCH `ref` → `bipolar_map_paper_engine.py` V5.0 (`chanh_niem_ke_bipolar_chronicle_v4`):** Colab T4 `h264_nvenc` `30fps` (`blend_map_gpu()`, `BeatOverlayCache`, 3D crumpled paper relief, 2.5D depth-dimmed desk pans, Full-Stage 3D viewports, `CourierPrime-VN-Bold.ttf` pills with `2px` ink borders, `HOÀNG SA`/`TRƯỜNG SA` screen-space lock, `audit_layout_boxes()`, circular Option W1 watermark `W-w-36:H-h-36`). Always `colab stop` after render. |
| **6. Multi-Platform Publish** | `ref` [vp-omni-platform](../vp-omni-platform/SKILL.md) *(shared)* | Target `--channel chanh_niem_ke` (`profile_7`, port `9228`, public brand **Hiểu Tận Gốc** `@HieuTanGocVN`): publish Long first, capture live URL, publish Short with `Related Video` linked to Long, configure `.vi.srt`, End Screen, Info Card, pin `@HieuTanGocVN` comment. Legacy mindfulness videos remain `PRIVATE`. |

---

## Channel SSOT Code, Cache & Asset Paths

- **Channel Soul & Boundaries:** [sys/channels/chanh_niem_ke/soul.json](../../../sys/channels/chanh_niem_ke/soul.json)
- **Channel Strategic Plan:** [sys/channels/chanh_niem_ke/PLAN.md](../../../sys/channels/chanh_niem_ke/PLAN.md)
- **V4 Production Lock Manifest:** [sys/channels/chanh_niem_ke/channel_v4_chronicle_lock.json](../../../sys/channels/chanh_niem_ke/channel_v4_chronicle_lock.json)
- **GIS Map Baker (`branch ref`):** [sys/fx_warehouse/gis_map_baker.py](../../../sys/fx_warehouse/gis_map_baker.py)
- **Flow Hybrid Matting (`branch ref`):** [sys/fx_warehouse/flow_hybrid_matting.py](../../../sys/fx_warehouse/flow_hybrid_matting.py)
- **Bipolar 30fps Engine V4.2 (`branch ref`):** [sys/fx_warehouse/bipolar_map_paper_engine.py](../../../sys/fx_warehouse/bipolar_map_paper_engine.py)
- **Chronicle Audio Mixer (`branch ref`):** [sys/fx_warehouse/chronicle_audio_mixer.py](../../../sys/fx_warehouse/chronicle_audio_mixer.py)
- **Topic-Agnostic Chronicle Producer (`branch ref`):** [sys/tools/produce_chanh_niem_ke_chronicle.py](../../../sys/tools/produce_chanh_niem_ke_chronicle.py)
- **GIS Cache & Sovereignty:** `sys/assets/gis_cache/geojson/vietnam_sovereignty_override.geojson`, `sys/assets/gis_cache/prebaked/*.npz`, `sys/assets/map_icons/*.svg`
- **Verified Vietnamese Fonts:** `sys/assets/fonts/chanh_niem_ke/*.ttf` (`BarlowCondensed-ExtraBold.ttf`, `Oswald-Bold.ttf`, `RobotoCondensed-Bold.ttf`, `LiberationMono-Bold.ttf`, `IBMPlexMono-Bold.ttf`, `RobotoSlab-Bold.ttf`, `RobotoMono-Bold.ttf`, `DejaVuSans-Bold.ttf`)
- **Voice Profile (KTTV Studio V3):** [sys/assets/voices/ch_chanh_niem_ke/profile.json](../../../sys/assets/voices/ch_chanh_niem_ke/profile.json) (`VietNarrator_chanh_niem_ke`)
- **Channel Watermark:** [sys/channels/chanh_niem_ke/assets/watermark_150x150.png](../../../sys/channels/chanh_niem_ke/assets/watermark_150x150.png) (`W-w-36:H-h-36`)
- **Reference Pilot Manifest:** [sys/runs/chanh_niem_ke_chronicle_demo/episode_manifest.json](../../../sys/runs/chanh_niem_ke_chronicle_demo/episode_manifest.json)

## Mandatory Verification Commands

```bash
./sys/.venv/bin/pytest sys/tests/test_channels_system.py sys/tests/test_channel_voice_profiles.py sys/tests/test_fx_warehouse.py sys/tests/test_chanh_niem_ke_hybrid_v42.py
python3 sys/tools/script_cadence_checker.py --content sys/runs/<job_id>/script_long_16x9.json --format long_16x9
python3 sys/tools/script_diversity_linter.py --content sys/runs/<job_id>/script_long_16x9.json
python3 sys/tools/cta_tone_linter.py --content sys/runs/<job_id>/script_short_9x16.json --format short_9x16 --channel chanh_niem_ke
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of json <output.mp4>
ffmpeg -i <output.wav> -af ebur128=peak=true -f null -
```

1. **Automated V4.2 Engine & Anti-Hardcode Gate:** Run `test_chanh_niem_ke_hybrid_v42.py` to verify `0%` topic hardcoding, 134-char Vietnamese font coverage (`0` tofu), prebaked GIS `.npz` + `vietnam_sovereignty_override.geojson`, and synthetic multi-topic frame rendering (`audit_layout_boxes()` == `[]`).
2. **Container & Audio Gate:** Verify master WAV (`48000Hz` stereo, `-11.0 LUFS / -1.0 dBTP`) and Colab T4 `h264_nvenc` MP4s (`30fps`, `1920x1080`/`2560x1440` Long and `1080x1920`/`1440x2560` Short).
3. **Visual & Sovereignty Audit:** Extract frames across World A (`map`), World B (`paper` layouts + cutaways + Polaroids + cutouts), and watermark regions (`read_file`) to confirm `0%` edge stretching, `HOÀNG SA` & `TRƯỜNG SA` drawn cleanly once in screen-space, `0` highlighter halo, `0` bounding-box violations, and clean `watermark_150x150.png` at `W-w-36:H-h-36`.
