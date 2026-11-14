---
name: vp-channel-ban-do-quyen-luc
description: "Dedicated channel specifications for Bản Đồ Quyền Lực (ban_do_quyen_luc). Holds all channel-specific identity, 3-pillar photorealistic + 4-mode visual grammar (ban_do_quyen_luc_4styles_photoreal_v3), 240-beat 9-chapter pacing, VietNarrator_ban_do_quyen_luc voice profile, and 2K brand parameters to pair with shared workflow skills without overriding them."
---

# Bản Đồ Quyền Lực (`ban_do_quyen_luc`) — Dedicated Channel Specifications (v3)

Channel-specific specification module for **Bản Đồ Quyền Lực** (`@BanDoQuyenLucVN`, YouTube Channel ID `UCkL2Lj5dSea1zh7CcBtXG8w`, `profile_19`, port `9240`). Shared workflow skills ([vp-research-architect](../vp-research-architect/SKILL.md), [vp-scriptwriting](../vp-scriptwriting/SKILL.md), [vp-flow-cdp](../vp-flow-cdp/SKILL.md), [vp-colab-bridge](../vp-colab-bridge/SKILL.md), [vp-omni-platform](../vp-omni-platform/SKILL.md), [vp-production](../vp-production/SKILL.md)) remain **100% shared and unmodified**; this skill supplies only the parameters unique to `ban_do_quyen_luc`. Read [visual-grammar-4styles.md](references/visual-grammar-4styles.md) for the 3-pillar photorealistic + 4-mode composite grammar and [pacing-and-script-rules.md](references/pacing-and-script-rules.md) for beat density and narrative structure.

## Bảng Ghép Nối Quy Trình Dùng Chung ↔ Đặc Thù Riêng Kênh `ban_do_quyen_luc` (Shared Workflow ↔ Channel-Specific Matrix)

| Shared Workflow Step (Unmodified) | `ban_do_quyen_luc` Channel-Specific Parameters (Plug-in Only) |
|---|---|
| **1. Research & Packaging** ([vp-research-architect](../vp-research-architect/SKILL.md)) | Niche: Geopolitics, strategic maritime chokepoints, and critical resource supply chains (`ban_do_quyen_luc`, `@BanDoQuyenLucVN`, `profile_19`, port `9240`, playlist `"Bản Đồ Quyền Lực — Địa Chính Trị Thế Giới"`, `parent_long_id` Short-to-Long funnel). |
| **2. Script & Beat Density** ([vp-scriptwriting](../vp-scriptwriting/SKILL.md)) | Per [pacing-and-script-rules.md](references/pacing-and-script-rules.md): Long = `9–10 chapters` (`240` visual beats, `~9m30s–10m00s`, `~2.42s/image` avg, zero-filler sentences); Short = `12–14` beats (`~48–58s`) with natural close CTA + channel bridge in the last 15%. |
| **3. Channel Visual Style** *(selected instead of 2D Doodle [vp-full-frame-quality](../vp-full-frame-quality/SKILL.md))* | Per [visual-grammar-4styles.md](references/visual-grammar-4styles.md): **`ban_do_quyen_luc_4styles_photoreal_v3`** — 3-pillar photorealistic base (orbital satellite relief, 100mm macro engineering, on-site documentary journalism; strictly diverse per beat, no repetitive walnut tabletop or crimson clamp props) combined with 4 narrative visual modes (`CACH_1_HERO_STAMP`, `CACH_2_SPLIT_COMPARE`, `CACH_3_DOSSIER_LIST`, `CACH_4_CINEMATIC_PACING`), `allowed_text=None` on raw Flow frames, `clean_beluga_sparkle_pil` + `1.045x` overscan. |
| **4. Flow Asset Generation** ([vp-flow-cdp](../vp-flow-cdp/SKILL.md)) | Long: `240` `16:9` BELUGA frames (+ optional key-beat I2V clips). Short: `12–14` `9:16` frames + `omni_flash` `reference_start_end` / `single_frame_i2v` clips. Thumbnails: Flow-native high-CTR geopolitical conflict/chokepoint photography with `2–4` bold uppercase Vietnamese words (`< 2MB`, zero tabletop clamp props). |
| **5. Voice & 2K Render Specs** ([vp-colab-bridge](../vp-colab-bridge/SKILL.md)) | Voice: `VietNarrator_ban_do_quyen_luc` (`recommended_speed=1.15`, `default_tone="authoritative_clear"`, `-11.0 LUFS / -1.0 dBTP` master). Render: Long `2560x1440@30fps` (`xfade=fade:duration=0.18`, `9–10` `FFMETADATA1` chapters); Short `1440x2560@30fps`. Watermark `sys/channels/ban_do_quyen_luc/assets/watermark_150x150.png` pinned at `W-w-36:H-h-36`. |
| **6. Multi-Platform Publish** ([vp-omni-platform](../vp-omni-platform/SKILL.md) + [vp-production](../vp-production/SKILL.md)) | Target `--channel ban_do_quyen_luc` (`profile_19`, port `9240`): publish Long first, capture live URL, publish Short with native Related Video (`Video có liên quan`) linked to Long, configure End Screen (`1 video, 1 đăng ký`), Info Card, `.srt` subtitles, and pin debate-trigger comment. |

## Channel SSOT Code & Asset Paths

- **Production Lock Manifest**: `sys/channels/ban_do_quyen_luc/channel_v3_production_lock.json`
- **Channel Blueprint**: `sys/channels/ban_do_quyen_luc/PLAN.md`
- **Video & Visual Formulas**: `sys/channels/vn_flow_video_formulas.py`
- **Script & Hook Formulas**: `sys/channels/vn_competitor_script_formulas.py`
- **Voice Profile**: `sys/assets/voices/ch_ban_do_quyen_luc/profile.json` (`VietNarrator_ban_do_quyen_luc`)
- **Channel Watermark**: `sys/channels/ban_do_quyen_luc/assets/watermark_150x150.png` (`W-w-36:H-h-36`)
- **Release Registry**: `sys/channels/ban_do_quyen_luc/release_links.json`

## Mandatory Verification Commands

```bash
PYTHONPATH=sys pytest sys/tests/test_channel_ban_do_quyen_luc.py sys/tests/test_vn_flow_v3_pipeline.py sys/tests/test_channels_system.py -q
python3 sys/tools/script_cadence_checker.py --help
python3 sys/tools/cta_tone_linter.py --help
```

1. **Audio & Video Container**: Verify master WAV (`48000Hz` stereo, `-11.0 LUFS / -1.0 dBTP`) and rendered MP4 via `ffprobe` (`2560x1440` Long or `1440x2560` Short, `30fps`, `h264_nvenc`).
2. **Visual & 4-Style Frame Audit**: Extract representative frames from `CACH_1_HERO_STAMP`, `CACH_2_SPLIT_COMPARE`, `CACH_3_DOSSIER_LIST`, and `CACH_4_CINEMATIC_PACING` beats, verifying crisp Vietnamese 2K typography legibility, clean `watermark_150x150.png` placement (`W-w-36:H-h-36`), environment diversity across beats, and zero AI-drawn text inside raw Flow photography.
