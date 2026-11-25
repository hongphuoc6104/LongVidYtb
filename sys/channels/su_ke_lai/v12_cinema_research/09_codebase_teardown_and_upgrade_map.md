# V12 Codebase Teardown & Surgical Upgrade Map (Thread 3A)

**Auditor:** `@code-hud-auditor` | **Scope:** Read-Only Audit of V7/V8 HUDs, `tactical_battle_map_v8.py`, Short/Long Film Engines, Visual QC & Unit Tests  
**Companion JSON:** [09_codebase_teardown_and_upgrade_map.json](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/channels/su_ke_lai/v12_cinema_research/09_codebase_teardown_and_upgrade_map.json)

---

## 1. Defect Screenshot Forensics -> Exact Root Causes

| Defect Screenshot | Observed Defect | Exact Root Cause (`file:lines`) | V12 Surgical Remedy |
| :--- | :--- | :--- | :--- |
| `media_1795577556825_43560abb.png` | Dark obsidian rounded rectangle pill + left gold vertical bar + bottom gold line (`NỬA ĐÊM 06/08/1442 \| 48 GIỜ BƯNG BÍT TIN DỮ`) | [render_single_pass.py#L321-L346](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/short_engine/render_single_pass.py#L321-L346) (`render_prestige_dateline_png`, `L340–L342`) | **Abolish box/stripe/line.** Replace with bare Zero-Box Cinema Typography (optical shadow only) or pure no-overlay cinema. |
| `media_1795577569660_b4602a02.png` | Full-width dark box + gold outline + gold/red side bars + vertical divider + red `VS` badge (`ĐÚNG 10 NGÀY` vs `TRU DI 3 HỌ`) | [render_single_pass.py#L512-L599](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/short_engine/render_single_pass.py#L512-L599) (`render_v7_stat_versus_png`, `L542–L563`, `L590–L591`) | **Abolish completely.** Never draw `VS` boxes or split HUD cards; keep at most 1-line boxless floating metric or omit. |
| `media_1795577586131_ec18d5fd.png` | Dark rectangular pill bar + left gold stripe + bottom gold line over roof tiles (`THÁNG 07/1464 · QUANG THUẬN 5 \| 22 NĂM RỬA OAN`) | [render_single_pass.py#L321-L346](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/short_engine/render_single_pass.py#L321-L346) (`render_prestige_dateline_png`, `L340–L342`) | **Abolish box/stripe/line.** Render bare small-caps dateline over feathered optical scrim or fold into voiceover. |
| `media_1795577641961_154afc27.jpg` | 9:16 Chi Lăng 1427 map: tiny faded header (`14–40px`), 9 crowded multi-word labels, left `-0.8m` vertical gauge, bottom force-ratio bar colliding with captions, fast `4.8s` pacing | [tactical_battle_map_v8.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/fx_warehouse/tactical_battle_map_v8.py) (`L472–L623`, `L1462–L1540`, `L2014–L2460`, `L2498`, `L2568`) | **Upgrade to V12 Minimalist Slow Map:** font `>= 5%` height (`>= 54px` @ 1080h / `>= 96px` @ 1920h), `<= 3` words/label, max `2–3` staged callouts, abolish side gauge & bottom bar, `>= 6.0–8.0s` maneuver duration, stop premature `hud_opacity` fadeout. |

---

## 2. Line-by-Line Teardown: Boxed HUDs, Pills, Gold Borders & `VS` Badges

### A. [render_single_pass.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/short_engine/render_single_pass.py)
- **`render_prestige_dateline_png` (`L321–L346`) — ABOLISH BOX**:
  - `L340`: `draw.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=8, fill=(10, 14, 20, 178))`
  - `L341`: `draw.rectangle([0, 6, 4, ch - 7], fill=(226, 188, 96, 235))`
  - `L342`: `draw.line([(16, ch - 3), (cw - 16, ch - 3)], fill=(226, 188, 96, 140), width=2)`
  - *Upgrade:* Strip `L340–L342`; render bare uppercase dateline (`>= 44px` on `1440w`) with soft optical drop shadow only.
- **`render_v7_hook_headline_png` (`L450–L509`) — ABOLISH BOX**:
  - `L484`: `draw.rounded_rectangle([0, 0, canvas_w - 1, canvas_h - 1], radius=18, fill=(10, 14, 22, 214), outline=(232, 190, 88, 195), width=3)`
  - `L485`: `draw.rounded_rectangle([0, 14, 8, canvas_h - 15], radius=3, fill=(238, 196, 94, 245))`
  - `L505–L508`: crimson + gold underline bars (`draw.rounded_rectangle([bx0, bar_y, ...])`)
  - *Upgrade:* Replace with boxless Zero-Box Cinema Hook Title (`88–108px`, stroke + soft Gaussian shadow) or omit in `pure_no_overlay` mode.
- **`render_v7_stat_versus_png` (`L512–L599`) — ABOLISH**:
  - `L542`: full-width dark card `rounded_rectangle` with `outline=(232, 190, 88, 210), width=3`
  - `L543–L544`: gold left bar & crimson right bar
  - `L559`: gold vertical divider
  - `L560–L563`: red rounded-rectangle `"VS"` badge (`fill=(198, 44, 34, 245), outline=(255, 216, 102, 245)`)
  - `L590–L591`: single counter mode dark `rounded_rectangle` + gold stripe
  - *Upgrade:* Abolish `v7_stat_versus` from V12 specs/renderers.
- **`render_heroic_banner_png` (`L349–L424`) — REFINE**:
  - Already boxless typography (`>= 132px`, `<= 4` words), except `L412–L421` draws crimson/gold underline bars. Make `show_underline_bar=False` default in V12.
- **`render_chronicle_stamp_png` (`L275–L298`) & `render_ai_disclosure_pill_png` (`L301–L318`) — KEEP (BOXLESS)**:
  - Both already draw zero boxes (`render_ai_disclosure_pill_png` has `"pill"` in name only; no rectangle is drawn).
- **`build_hud_stamps` (`L602–L778`) & Remote Scripts (`L1208`, `L1460`)**:
  - `L661–L672` dispatches `v7_hook_headline`, `v7_stat_versus`, `prestige_dateline`; `L676–L707` dispatches boxed Short signature HUDs; `L708–L715` falls back to boxed `build_bespoke_topic_hud_patch`.
  - `L731–L735`, `L1208`, `L1460` force `pop_y` `+38px` bounce whenever `is_v7_chunk` is True. Disable `pop_y` bounce for V12 Zero-Box typography and support `overlay_mode == "pure_no_overlay"` (`return []`).

### B. [history_styles_10x10.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/fx_warehouse/history_styles_10x10.py) & [studio_director_v7.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tools/studio_director_v7.py) (Upstream Spec Generators)
- **`history_styles_10x10.py`**:
  - `L426–L966`: All 10 Short styles list `v7_hook_headline`, `v7_stat_versus`, `prestige_dateline` in `hud_preset_kinds`.
  - `L1744–L1967` (`_build_short_hud_stamps`): Emits `v7_hook_headline`, `prestige_dateline`, `v7_stat_versus`, plus `S02/S04/S05/S06/S07/S09` boxed cards.
  - `L2786–L3133` (`_render_s02_pov_survival_card` through `_render_generic_short_style_card`): Every Short renderer draws dark `rounded_rectangle` boxes + left vertical bars + inner pills. **Contrast:** `_render_long_zero_box_hud` (`L3136–L3217`) ALREADY implements 100% Zero-Box feathered optical scrim + hairline typography! Port Short HUDs to that pattern or omit.
- **`studio_director_v7.py`**:
  - `L1755–L1770`: Gate 1 requires `v7_hook_headline` or `heroic_banner` at `B00`.
  - `L4145–L4252`: Scaffolds 11 `hud_stamps` (`1` `v7_hook_headline`, `3` `prestige_dateline`, `4` `v7_stat_versus`). Update scaffold & Gate 1 for V12 Zero-Box / no-overlay cinema.
- **`neural_soundstage_v5.py`**:
  - `L1301`: `v7_hud_tick` SFX triggers on `("v7_hook_headline", "v7_stat_versus", "chronicle_stamp", "heroic_banner")`. Update whitelist or mute in pure cinema mode.

### C. [hud_widgets.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/fx_warehouse/hud_widgets.py) & [hud_forensic_v2.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/fx_warehouse/hud_forensic_v2.py)
- **`hud_widgets.py`**:
  - `build_bespoke_topic_hud_patch` (`L77–L190`): All 5 bespoke kinds (`metric_meter` `L114`, `timeline_nodes` `L133`, `comparison_matrix` `L151`, `sonar_radial` `L168`, `telemetry_card` `L184–L185`) draw `rounded_rectangle` dark boxes (plus left vertical stripe on `telemetry_card`).
  - `render_hud_widget_patch` (`L193–L438`): All 13 boxed widgets (`L233`, `L248`, `L271`, `L285`, `L302`, `L323`, `L339–L340`, `L374`, `L386`, `L395`, `L406`, `L419`, `L433`) draw `rounded_rectangle`/`rectangle` boxes. Gate `su_ke_lai` away from these via `zero_box=True` / `fx_mode="static"`.
- **`hud_forensic_v2.py`**:
  - `_draw_pill` (`L288–L306`) & `_draw_card_shell` (`L402–L430`, including Variant A left vertical bar `L429`) power 8 boxed forensic widgets (`L436–L1147`, `L1492–L1640`, plus `calibrated_radar_overlay` pill/boxes `L1234`, `L1279`). Keep isolated to `ho_so_ky_la` aviation/forensics.
  - `render_lemmino_hairline_hud` (`L1294–L1386`): Almost Zero-Box, but `L1338–L1342` draws a hard-edged `rounded_rectangle` scrim (`fill=(8,10,14,int(alpha*0.44))`). Replace with Gaussian feathered scrim.
  - `render_chapter_title_bumper` (`L1393–L1485`): Already 100% Zero-Box compliant (explicit bare eyebrow at `L1444`). Keep as Long chapter standard.

---

## 3. Line-by-Line Teardown: [tactical_battle_map_v8.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/fx_warehouse/tactical_battle_map_v8.py)

| Defect | Exact Lines & Constants | Why It Fails | V12 Upgrade Target |
| :--- | :--- | :--- | :--- |
| **Tiny Fonts** | `_ViewportProjector` (`L1532, L1538`: `ui_scale = width/1080` or `height/1080`); `_draw_moving_unit_blocks` (`L2044`: `19.0 * sc`); `_draw_callout_pins` (`L2181–L2182`: `20.5 * sc` / `15.0 * sc`); `_draw_hud_chrome` (`L2333–L2363`: date `21*sc`, title `40->22*sc`, phase `22->14*sc`; `L2414–L2415`: gauge `14.5*sc` / `21*sc`; `L2443–L2444`: force bar `20*sc` / `16*sc`) | Produces `14–24px` labels on `1080x1920` (`~0.7%–1.2%` height) — illegible on mobile & thumbnail previews. | Primary map labels `>= 5%` frame height (`>= 54px` @ 1080h, `>= 96px` @ 1920h); remove `sub` secondary lines; raise `_fit_font` floor to `>= 42px` on 9:16. |
| **Crowded Labels** | `_build_presets` (`L300–L1107`, e.g. `chi_lang_1427` `L472–L623` has 5 unit badges + 4 callouts with `sub` lines); `_draw_callout_pins` (`L2190–L2268`) keeps all `t_appear <= 0.25` callouts on screen simultaneously | 9 multi-word labels (`"1 VẠN KỴ • LIỄU THĂNG"`, `"VÁCH ĐÁ CAI KINH / NÚI ĐÁ DỰNG ĐỨNG"`) crowd the central valley. | Enforce `<= 3` words/label; remove `sub` sublines; add `t_disappear` staging so max `2–3` labels are active at any frame. |
| **Side Gauge & Bottom Bar** | `_seed_hud_exclusion_rects` (`L2014–L2025`); `_draw_hud_chrome` tide/gorge bar (`L2370–L2425`); force-ratio bar (`L2426–L2459`); compass (`L2365–L2368`) | Side `-0.8m` gauge & bottom force-ratio bar (`H - 185*sc`) shrink map canvas and collide with ASS captions / Shorts UI. | **Abolish** side gauge and bottom force-ratio bar by default (`show_side_gauge=False`, `show_force_bar=False`); keep full-bleed map + minimal top header. |
| **Fast Animation & Premature Fade** | `duration_sec = 4.8` (`L1466`, `L2498`, `L2568`); arrow/unit `t_end` `0.34–0.58` (`L386–L611`); `hud_opacity = _clamp(1.0 - u_zm * 1.45)` (`L1494`); ripple `0.42*speed_boost` (`L1658`); shockwave `1.45` / `sin(18*t)` (`L1909, L1920`); unit jitter `sin(20*t)` (`L2067`) | Arrows finish in `1.6–2.7s`, units jitter, and `hud_opacity` dims title/header to faint gray (as seen in `media_1795577641961_154afc27.jpg`). | Default `duration_sec >= 7.5` (gate `>= 6.0s`); spread unit/arrow progression across `0.05..0.90`; remove high-frequency `sin(18*t)` / `sin(20*t)` jitter; keep primary labels at full contrast until final `0.25s`. |

---

## 4. Film Engines & Visual QC ([flow_stage.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/short_engine/flow_stage.py), [produce_vn_dual_mode.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tools/produce_vn_dual_mode.py), [produce_serialized_short.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tools/produce_serialized_short.py), [historical_visual_qc.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/fx_warehouse/historical_visual_qc.py))

1. **`flow_stage.py` (`classify_hybrid_beats`, `L51–L102`)**: Currently `L89–L90` routes `scene_type == "tactical_sand_table"` to `2k_native_kenburns`, and `L91–L96` routes calm context/mechanism/payoff beats outside Act 4 to static Ken Burns. In V12, route `gis_map` / `tactical_map` beats to baked `tactical_battle_map_v8` MP4 clips (`>= 6.0s` or split cleanly across beats) and leverage Ultra credits for living `flow_video` macro/hero coverage.
2. **`produce_vn_dual_mode.py` (`L655–L688`, `L1409–L1413`, `L1906`, `L2642`, `L2992`)**: Long mode uses static Lanczos scale+crop when `fx_mode="static"`. For V12 Long first-60s cold open, enforce `<= 3.5s/beat` pacing (zero static image held `> 3.5s` in `0..60s`) via living Flow clips, continuous chains, or smooth CUDA `grid_sample` / map motion, while keeping boxed `fx_compositor.prepare_fx_hud_assets` off for `su_ke_lai`. Keep `make_rounded_watermark` (`L1128–L1157`) at `W-w-36:H-h-36`.
3. **`produce_serialized_short.py` (`L1–L223`)**: Thin CLI facade; add `--overlay-mode pure_cinema|zero_box|legacy` pass-through to `run_render_stage`.
4. **`historical_visual_qc.py` (`L45–L82`, `L829–L1000`, `L1156–L1340`)**: Add 3 hard-fail V12 gates to `audit_full_episode_visual_readiness`:
   - `NO_BOXED_HUD_OVERLAY`: reject `v7_hook_headline`, `v7_stat_versus`, `prestige_dateline` or dark rectangular HUD cards.
   - `MAP_LEGIBILITY_AND_PACING`: enforce `duration_sec >= 6.0`, map label font height `>= 5%`, `<= 3` words/label, zero side gauge / bottom bar.
   - `LONG_COLD_OPEN_FIRST_60S_PACING`: fail if any static image beat in `0..60s` exceeds `3.5s`.

---

## 5. Unit Tests Impacted (Wave-2 Update Checklist)

| Test File | Lines Asserting Old V7/V8 Boxes or V8 Map | Wave-2 Update Action |
| :--- | :--- | :--- |
| [test_su_ke_lai_short_v7_upgrade.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tests/test_su_ke_lai_short_v7_upgrade.py) | `L29–L30`, `L86–L115`, `L290–L346` (`render_v7_hook_headline_png`, `render_v7_stat_versus_png`, `v7_hook_headline`, `pop_y` bounce) | Replace with Zero-Box Cinema Typography assertions (alpha/borderless check) & zero `VS` card checks. |
| [test_tactical_battle_map_v8.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tests/test_tactical_battle_map_v8.py) | `L50` (`len(callouts) >= 3`), `L121–L131` (`duration_sec=4.8`, `hud_opacity == 0.0`), `L197–L235` (`1.2s`/`1.0s` bake) | Add V12 map assertions: font `>= 5%` height, `<= 3` words/label, zero side/bottom bars by default, `>= 6.0s` default maneuver duration, full header contrast. |
| [test_history_styles_10x10.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tests/test_history_styles_10x10.py) | `L197–L220`, `L231` (`hud_stamps >= 4`), `L320–L359` (boxed `S02/S04/S05/S06/S07/S09` cards) | Port Short signature HUD tests to Zero-Box (`high_opacity_ratio < 0.15` / zero rectangular box borders, matching `L342–L345`). |
| [test_studio_director_v7.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tests/test_studio_director_v7.py) | `L54`, `L65`, `L270`, `L281` (hardcodes `hud_count == 11` / `len(hud_stamps) == 11`) | Update expected `hud_stamps` count & Gate 1 rules when V12 scaffolding drops boxed V7 cards. |
| [test_historical_visual_qc.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tests/test_historical_visual_qc.py) | `L1–L515` (existing prompt/crop/2K frame gates) | Add tests for new V12 hard-fail gates (boxed HUD ban, map legibility/pacing, Long first-60s `<= 3.5s` static hold). |
| [test_fx_warehouse.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tests/test_fx_warehouse.py) | `L299–L366` (14 `HUD_WIDGET_CATALOG` + 5 `build_bespoke_topic_hud_patch` boxed cards) | Keep forensic channel checks; add `zero_box=True` / `su_ke_lai` Zero-Box verification test. |
| [test_produce_serialized_short.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tests/test_produce_serialized_short.py) | `L99–L112`, `L153–L162`, `L287` (`heroic_banner` `>= 132px`, `<= 4` words, `hud_stamps_count == 5`) | Keep `heroic_banner` boxless tests; add `pure_no_overlay` (`hud_stamps_count == 0`) and `show_underline_bar=False` coverage. |
| [test_su_ke_lai_short_v5_upgrade.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tests/test_su_ke_lai_short_v5_upgrade.py) | `L96–L129` (`chronicle_stamp` + `ai_disclosure_pill`) | Already boxless; add explicit zero-opaque-box check. |
| [test_short_engine_mode_aplus.py](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/tests/test_short_engine_mode_aplus.py) | `L130–L313` (15–16 beat bounds & 4-chunk timeline) | No boxed HUD dependency; optionally add `hud_stamps=[]` pure cinema regression test. |
