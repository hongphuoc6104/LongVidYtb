---
name: vp-channel-su-ke-lai
description: "Dedicated channel specifications for Sử Kể Lại (su_ke_lai). Holds all channel-specific identity, Option 1 35mm live-action visual grammar, 2-clause 240-beat pacing, VietNarrator_su_ke_lai 1.30x voice profile, and 2K brand parameters to pair with shared workflow skills without overriding them."
---

# Sử Kể Lại (`su_ke_lai`) — Dedicated Channel Specifications (v3)

Channel-specific specification module for **Sử Kể Lại** (`@SuKeLaiVN`, `profile_5`, port `9226`). Shared workflow skills ([vp-research-architect](../vp-research-architect/SKILL.md), [vp-scriptwriting](../vp-scriptwriting/SKILL.md), [vp-flow-cdp](../vp-flow-cdp/SKILL.md), [vp-colab-bridge](../vp-colab-bridge/SKILL.md), [vp-omni-platform](../vp-omni-platform/SKILL.md), [vp-production](../vp-production/SKILL.md)) remain **100% shared and unmodified**; this skill supplies only the parameters unique to `su_ke_lai`. Read [visual-grammar-option1.md](references/visual-grammar-option1.md) for visual prompts and [pacing-and-script-rules.md](references/pacing-and-script-rules.md) for beat structure.

## Bảng Ghép Nối Quy Trình Dùng Chung ↔ Đặc Thù Riêng Kênh `su_ke_lai` (Shared Workflow ↔ Channel-Specific Matrix)

| Shared Workflow Step (Unmodified) | `su_ke_lai` Channel-Specific Parameters (Plug-in Only) |
|---|---|
| **1. Research & Packaging** ([vp-research-architect](../vp-research-architect/SKILL.md)) | Niche: Vietnamese military & dynasty history (`su_ke_lai`, playlist `"Sử Kể Lại — Lịch Sử Việt Nam Kể Như Phim"`, `parent_long_id` Short-to-Long funnel). |
| **2. Script & Beat Density** ([vp-scriptwriting](../vp-scriptwriting/SKILL.md)) | Per [pacing-and-script-rules.md](references/pacing-and-script-rules.md): Long = `10 chapters × 12 zero-filler sentences = 120 sentences` (`~9m15s–9m45s`), split into `2` clause sub-beats/sentence (`240` visual beats, `~2.35s/image`). Short = `12` beats (`~48–58s`). |
| **3. Channel Visual Style** *(selected instead of 2D Doodle [vp-full-frame-quality](../vp-full-frame-quality/SKILL.md))* | Per [visual-grammar-option1.md](references/visual-grammar-option1.md): **Option 1 (`su_ke_lai_35mm_live_action_v3`)** — `35mm Kodak Vision3 500T` live-action historical cinema, 5-block prompt formula, 5-shot camera rotation, `allowed_text=None` on 100% story frames, `clean_beluga_sparkle_pil` + `1.045x` overscan. |
| **4. Flow Asset Generation** ([vp-flow-cdp](../vp-flow-cdp/SKILL.md)) | Long: `240` `16:9` BELUGA frames. Short: `12` `9:16` frames + `12` `omni_flash` `single_frame_i2v` clips (`end_image_path=None`). Thumbnails: Flow-native 35mm live-action with `2–4` uppercase Vietnamese words (`< 2MB`). |
| **5. Voice & 2K Render Specs** ([vp-colab-bridge](../vp-colab-bridge/SKILL.md)) | Voice: `VietNarrator_su_ke_lai` (`speaking_rate=1.30`, `inter_beat_gap=0.06s`, `chapter_gap=0.18s`, `heroic_epic` EQ). Render: Long `2560x1440@30fps` (`xfade=fade:duration=0.18`, `10` `FFMETADATA1` chapters); Short `1440x2560@30fps` (`cas=0.55`, bundled `DejaVuSans` fonts for `libass`, `omni_flash` corner `delogo` check). Watermark `watermark_150x150.png` at `W-w-36:H-h-36`. |
| **6. Multi-Platform Publish** ([vp-omni-platform](../vp-omni-platform/SKILL.md) + [vp-production](../vp-production/SKILL.md)) | Target `--channel su_ke_lai`: publish Long first, capture live URL, publish Short with `--related-video <LONG_URL>`, pin `@SuKeLaiVN` funnel comment. |

## Channel SSOT Code & Asset Paths

- **Production Lock Manifest**: `sys/channels/su_ke_lai/channel_v2_production_lock.json`
- **Video & Visual Formulas**: `sys/channels/vn_flow_video_formulas.py`
- **Script & Hook Formulas**: `sys/channels/vn_competitor_script_formulas.py`
- **Voice Profile**: `sys/assets/voices/ch_su_ke_lai/profile.json` (`VietNarrator_su_ke_lai`)
- **Channel Watermark**: `sys/channels/su_ke_lai/assets/watermark_150x150.png` (`W-w-36:H-h-36`)

## Mandatory Verification Commands

```bash
PYTHONPATH=sys pytest sys/tests/test_channel_su_ke_lai.py sys/tests/test_vn_flow_v3_pipeline.py -q
python3 sys/tools/script_cadence_checker.py --help
python3 sys/tools/cta_tone_linter.py --help
python3 sys/visual_pacing.py --help
```

1. **Audio & Video Container**: Verify master WAV (`48000Hz` stereo, `-11.0 LUFS / -1.0 dBTP`) and rendered MP4 via `ffprobe` (`2560x1440` or `1440x2560`, `30fps`, `h264_nvenc`).
2. **Visual Frame Audit**: Extract representative frames from the rendered MP4 and inspect `watermark_150x150.png` placement (`W-w-36:H-h-36`), `libass` Vietnamese diacritics/stamps, `delogo` cleanliness on `omni_flash` clips, and zero AI-drawn text.
