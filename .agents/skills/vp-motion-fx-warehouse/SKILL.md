---
name: vp-motion-fx-warehouse
description: Modular Motion, 30fps HUD, GPU VFX & Procedural Audio Warehouse plus the Bespoke-Per-Video Creation Protocol across all 5 Niche Archetypes (20 Vietnamese channels).
---

# Video Pilot Motion, HUD, VFX & Audio Warehouse (`vp-motion-fx-warehouse`)

This skill governs how Video Pilot agents and pipelines query, compose, and dynamically extend the shared **Motion, 30fps HUD, GPU VFX & Procedural Audio Warehouse** (`sys/fx_warehouse/`).

Instead of isolating effects inside channel silos or loading a giant monolith, all 20 Vietnamese channels (grouped into 5 Niche Archetypes) share a sharded warehouse package while obeying strict viewing-comfort guardrails and the **Golden Rule of Non-Forced Selection**.

---

## 1. Sharded Warehouse Architecture (`sys/fx_warehouse/`)

Skills, channel specs, and production scripts MUST reference only the specific sub-warehouse shard they need rather than loading a monolithic catalog:

| Shard Module | Responsibility | Primary Exports |
| :--- | :--- | :--- |
| `sys/fx_warehouse/archetypes.py` | 5 Niche Archetypes, 20-channel mapping, palettes, defaults, comfort guardrails & bespoke synthesis policies | `ARCHETYPE_PROFILES`, `CHANNEL_ARCHETYPE_MAP`, `resolve_niche_fx_blueprint` |
| `sys/fx_warehouse/camera_vfx.py` | 8 sub-pixel 2.5D camera motion curves (`float32` parallax) + 7 GPU frame shaders + bespoke registration | `CAMERA_MOTION_CATALOG`, `VFX_SHADER_CATALOG`, `register_bespoke_camera_motion`, `register_bespoke_vfx_shader` |
| `sys/fx_warehouse/hud_widgets.py` | 14 30fps PIL RGBA HUD/layout widgets + font/easing helpers + dynamic topic HUD patch builder | `HUD_WIDGET_CATALOG`, `render_hud_widget_patch`, `register_bespoke_hud_widget`, `build_bespoke_topic_hud_patch` |
| `sys/fx_warehouse/audio_sfx_bgm.py` | 25 stereo 48kHz SFX stems (`sys/assets/sfx/`) + 5 Niche BGM loops (`sys/assets/audio/bgm/`) + procedural bespoke SFX synthesizer | `SFX_CATALOG`, `BGM_CATALOG`, `SFX_DIR`, `BGM_DIR`, `TARGET_SR`, `ensure_warehouse_audio_assets`, `synthesize_bespoke_topic_sfx` |
| `sys/fx_warehouse/selector.py` | Content-aware beat FX router, static-camera pin locks (`STATIC_CAMERA_HUDS`), `T0..T3` pause-tier hints, `hud_v2_hint` routing, comfort guardrails & bespoke trigger detection | `auto_select_beat_fx`, `STATIC_CAMERA_HUDS`, `PAUSE_TIER_DURATIONS` |
| `sys/fx_warehouse/hud_forensic_v2.py` | 9 high-precision forensic/3D dossier 30fps RGBA HUD widgets + 2K verified map anchors (`VERIFIED_MAP_ANCHORS_2K`) across variants `A`/`B`/`C` | `FORENSIC_HUD_V2_CATALOG`, `VERIFIED_MAP_ANCHORS_2K`, `render_forensic_hud_v2`, `set_font_dir` |
| `sys/fx_warehouse/audio_suspense_v2.py` | 48kHz stereo suspense audio engine: 4-act dynamic tension BGM, aviation/forensic SFX synthesizers, VHF cockpit bed, 2-pass `-11.0 LUFS / -1.0 dBTP` WAV/AAC mastering | `VARIANT_PROFILES`, `compose_4act_tension_bgm`, `synth_boeing_737_warning_horn`, `build_suspense_audio_mix`, `encode_calibrated_m4a_stereo` |
| `sys/fx_warehouse/pipeline_bridge.py` | Unified dual-mode `--fx-mode` router (`static`, `auto_niche`, `full_fx`, `forensic_v2`) & universal prompt trigger keywords | `FX_MODE_CHOICES`, `TRIGGER_KEYWORD_TABLE`, `plan_and_prepare_dual_mode_fx`, `resolve_fx_intent_from_text` |
| `sys/fx_warehouse/__init__.py` | Backward-compatible package facade re-exporting all shared v1/v2/bridge symbols | All public symbols above |

> [!IMPORTANT]
> **Render & Audio Invariants**:
> - Video rendering runs exclusively on **Colab Tesla T4 (`FFmpeg h264_nvenc`)**; zero Remotion/Chromium/TPU/local fallback.
> - High-density `long_16x9` 2D Doodle videos (240–350 `based_on` states) lock to static Lanczos + `xfade=fade` unless GPU `float32` 2.5D parallax warehouse mode is explicitly enabled.
> - Audio mixes normalize to **`-11.0 LUFS` / `-1.0 dBTP`** using `VietNarrator_<channel_id>` on OmniVoice (never `vi-VN-NamMinhNeural`).

---

## 2. Golden Rule of Non-Forced Selection ("Không Cố Ép Dùng Cái Cũ")

Shared presets exist to accelerate common beats—**never** to force an ill-fitting visual or sound onto a specialized video topic. For example, do not force an aviation black-box CVR countdown onto a maritime submarine mystery, do not force modern radar onto a medieval dynasty battle, and do not force a glowing cyan X-ray switch onto a calm mindfulness story.

Follow this mandatory 3-step protocol for every beat and video brief:

### Step 1: Query Shared Sub-Warehouses
Call `auto_select_beat_fx(beat_text, channel_id, beat_index=..., total_beats=..., overrides=..., video_topic=..., allow_bespoke=True)` from `sys/fx_warehouse/selector.py`.
- The selector inspects `beat_text` and `video_topic`, applies `CHANNEL_ARCHETYPE_MAP[channel_id]` defaults, checks cross-niche pull rules, and enforces `disallowed_vfx` comfort guardrails.

### Step 2: Check Semantic Fit
Evaluate the selected `camera`, `hud`, `vfx`, and `sfx` against three axes:
1. **Video Topic (`video_topic`)**: Does the widget's domain metaphor match the subject (e.g., aviation vs. maritime vs. ancient history vs. semiconductor supply chain vs. personal income tax)?
2. **Beat Metaphor**: Does the motion/HUD clarify the exact point of the narration without distracting or contradicting it?
3. **Niche Archetype**: Does the tone respect the channel's aesthetic and comfort boundaries (e.g., zero strobes/shakes/glitches on Group 4 Doodle or Group 5 Mindful)?

### Step 3: Author or Synthesize Bespoke Per-Video Assets When Needed
If **no** existing HUD widget, camera curve, VFX shader, or SFX stem matches the topic naturally:
1. **Bespoke HUD**: Pass a `bespoke_hud_spec` dict in `overrides` or call `build_bespoke_topic_hud_patch(bespoke_hud_spec, t_beat, dur, ...)` (from `sys/fx_warehouse/hud_widgets.py`) to render a topic-specific diagram, meter, ledger, or telemetry card on the fly (`is_bespoke: True`).
2. **Bespoke SFX**: Call `synthesize_bespoke_topic_sfx(spec_or_name, ...)` (from `sys/fx_warehouse/audio_sfx_bgm.py`) to procedurally synthesize a clean 48kHz stereo WAV tailored to the scene's physical soundscape (e.g., sonar ping at custom depth frequency, ancient bronze bell, Geiger click, mechanical loom).
3. **Bespoke Camera / VFX**: Register custom per-video motion curves or frame shaders via `register_bespoke_camera_motion(...)` or `register_bespoke_vfx_shader(...)` (from `sys/fx_warehouse/camera_vfx.py`).
4. **Optional Promotion**: If a bespoke asset proves broadly reusable across future episodes or channels, promote it cleanly into the appropriate `sys/fx_warehouse/` shard with a descriptive ID and comfort metadata.

---

## 3. Detailed Reference Files

- **[Sub-Warehouse Catalog](references/sub-warehouse-catalog.md)**: Complete indexed reference of all 8 camera moves, 7 GPU shaders, 14 30fps HUD widgets, 25 stereo 48kHz SFX stems, 5 BGM loops, and the `auto_select_beat_fx` + bespoke registration/synthesis APIs.
- **[Niche & Bespoke Synthesis Rules](references/niche-bespoke-synthesis-rules.md)**: Complete visual/audio signatures, cross-warehouse pull permissions, forbidden jarring effects, and concrete bespoke-per-video creation playbooks for all **5 Niche Archetypes** and all **20 Vietnamese channels**.
- **Pipeline Bridge & v2 Forensic/Suspense Shards**: [pipeline_bridge.py](../../../sys/fx_warehouse/pipeline_bridge.py) (dual-mode `--fx-mode` integration & keyword router), [hud_forensic_v2.py](../../../sys/fx_warehouse/hud_forensic_v2.py) (`FORENSIC_HUD_V2_CATALOG` 9 widgets), [audio_suspense_v2.py](../../../sys/fx_warehouse/audio_suspense_v2.py) (`A`/`B`/`C` 48kHz stereo suspense mixes).

---

## 4. Universal Trigger Keywords & Prompt Protocol (Dùng Cho Mọi Kênh)

Whenever requesting a new video on **any** of the 20 channels (`--channel <slug>`), include one or more canonical trigger keywords below in your prompt or `--video-topic`, or pass `--fx-mode` to [`produce_vn_dual_mode.py`](../../../sys/tools/produce_vn_dual_mode.py):

### A. Master Pipeline Intent Keywords (Dùng Cho Mọi Kênh)

| User Keyword / Alias | Resolved `--fx-mode` | Behavior & Branching |
|---|---|---|
| `[PRO_FX]`, `pro_fx`, `auto_niche`, `motion_fx`, `2.5D parallax`, `dựng chuyên nghiệp`, `hiệu ứng chuyên nghiệp` | `auto_niche` | Giữ Shared Spine, tự rẽ nhánh đúng **5 Niche Archetypes** (`CHANNEL_ARCHETYPE_MAP[channel_id]`), kéo 2.5D camera/HUD/SFX/BGM hợp ngữ cảnh, bật bespoke khi topic có trigger. |
| `[FULL_FX]`, `full_fx`, `hud_30fps`, `hud 30fps`, `motion_graphic`, `telemetry_hud`, `sound_design_pro` | `full_fx` | Kích hoạt full Motion 2.5D + tầng HUD 30fps + GPU shader hint + lớp SFX/BGM 48kHz stereo theo ngách cho mọi beat phù hợp. |
| `[BESPOKE_FX]`, `bespoke_fx`, `bespoke_hud`, `bespoke_sfx`, `hiệu ứng riêng`, `chủ đề riêng` | `full_fx` (`force_bespoke=True`) | **Không ép dùng preset cũ**: ép tổng hợp `bespoke_hud_spec` & `bespoke_sfx_spec` (`synthesize_bespoke_topic_sfx`) riêng cho chủ đề video. |
| `[FORENSIC_V2]`, `forensic_v2`, `suspense_v2`, `noir_diorama`, `hồ sơ trinh thám`, `âm thanh căng thẳng` | `forensic_v2` | Kích hoạt `FORENSIC_HUD_V2_CATALOG` (9 widget) + `audio_suspense_v2` (`A`/`B`/`C`). Tự hạ về `auto_niche` nếu kênh thuộc Group 5 Chánh Niệm (`comfort_downgraded=True`). |
| `[STATIC_CLEAN]`, `static_clean`, `2d_minimal`, `khung tĩnh` | `static` | Khóa khung tĩnh `Lanczos + fade` thuần 2D (tắt shader/HUD động). |

### B. Beat-Level Semantic Keywords (`sys/fx_warehouse/selector.py`)

Putting natural domain words inside `narration` or `video_topic` automatically pulls matching HUDs & SFX (subject to niche `disallowed_vfx` guardrails):
- **Split-Screen (`laser_split_screen`)**: `so sánh`, `đối chiếu`, `trái ngược`, `ngược lại`, `khác với`, `chia đôi`, `hai mặt`, `thay vì`, `một bên`, `vs`
- **3-Column Triptych (`triptych_3col_evidence`)**: `ba mắt xích`, `3 mắt xích`, `ba nguyên nhân`, `3 bước`, `ba yếu tố`, `3 quy luật`, `ba bài học`, `ba giai đoạn`, `3 lý do`
- **Verdict / Conclusion (`verdict_lower_third`)**: `phán quyết`, `kết luận`, `cải tổ`, `bài học lớn nhất`, `tóm lại`, `thay đổi vĩnh viễn`
- **Map / Radar (`radar_bezier_trajectory` + `radar_sonar_ping.wav`)**: `bản đồ`, `radar`, `tọa độ`, `quỹ đạo`, `biển đông`, `eo biển`, `tuyến đường`, `bay qua`, `lộ trình`, `thành phố`, `thủ đô`, `quốc gia`, `biên giới`
- **Emergency Countdown (`countdown_cvr_waveform` + `heartbeat_lub_dub.wav`)**: `hộp đen`, `cvr`, `đếm ngược`, `oxy não`, `90 giây`, `nhịp tim`, `sinh tồn`
- **Oscilloscope / Audio Forensic (`dual_oscilloscope_compare` + `caution_chime_double.wav`)**: `tần số`, `sóng âm`, `còi`, `âm thanh`, `báo động`, `trùng âm`, `nhầm còi`
- **X-Ray / System Mechanism (`xray_mode_switch_particles` + `rotary_switch_click.wav`)**: `cơ chế`, `x-ray`, `cấu tạo`, `bên trong`, `van điều áp`, `công tắc`, `mạch điện`, `tế bào`, `động cơ`, `chế độ`, `gạt sang`, `chỉnh tay`
- **Mindful Quote (`calligraphy_quote_dissolve` + `singing_bowl_zen.wav`)**: `chánh niệm`, `buông bỏ`, `tĩnh lặng`, `hơi thở`, `minh triết`, `đêm khuya`, `bình yên`, `thiền`, `chậm lại`, `tâm trí`, `thư thái`
- **Impact Stamp (`kinetic_stamp_slam` + `stamp_slam_hit.wav`)**: `hôn mê`, `thảm họa`, `tử vong`, `sai lầm`, `cảnh báo khẩn`, `sụp đổ`, `phá sản`, `nguy hiểm`, `mất kiểm soát`, `nghiêm trọng`
- **Archive Dossier (`lemmino_dossier_card` + `dossier_slide_whoosh.wav`)**: `hồ sơ`, `tư liệu`, `nhân chứng`, `tài liệu mật`, `bằng chứng`, `tiếp viên`, `vụ án`, `điều tra`
- **Metric Counter (`altitude_stat_counter` + `typewriter_burst.wav`)**: `số liệu + % / mét / km / tỷ / triệu / nghìn / độ c / giờ / phút / usd / đồng`
- **Knowledge Highlight (`highlighter_stroke_bar` / `doodle_spring_pop_badge`)**: `quy tắc`, `mẹo`, `bí quyết`, `nguyên lý`, `điểm mấu chốt`, `từ khóa`, `ghi nhớ`, `tư duy`, `não bộ`, `thói quen`, `lãi kép`

### C. Canonical CLI & Prompt Templates

```bash
# Tổng quát cho mọi kênh (Shared Spine + Niche Branch + Topic Bespoke)
PYTHONPATH=sys python3 sys/tools/produce_vn_dual_mode.py --mode build-long \
  --channel <channel-slug> \
  --fx-mode auto_niche \
  --video-topic "[PRO_FX] [BESPOKE_FX] <chủ đề tập video>"
```

Mẫu câu lệnh ngắn khi gọi trợ lý AI cho **bất kỳ kênh nào**:
> `Tạo video cho kênh <tên kênh/slug>, chủ đề <chủ đề>, kích hoạt [PRO_FX] [FULL_FX] [BESPOKE_FX] để tự rẽ nhánh ngách + HUD 30fps + sound design 48kHz + hiệu ứng riêng theo chủ đề.`
