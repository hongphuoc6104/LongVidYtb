---
name: vp-channel-su-ke-lai
description: "Production SSOT for the Sử Kể Lại (su_ke_lai) history channel. Use whenever planning topics, writing scripts, generating Option 1 35mm live-action visuals, synthesizing VietNarrator_su_ke_lai 1.30x audio, rendering 2K Long 16:9 or Short 9:16 videos, or publishing for su_ke_lai."
---

# Sử Kể Lại (`su_ke_lai`) — Channel Production SSOT (v3)

Authoritative v3 production contract for **Sử Kể Lại**. Read [visual-grammar-option1.md](references/visual-grammar-option1.md) before authoring image/video prompts and [pacing-and-script-rules.md](references/pacing-and-script-rules.md) before writing scripts or beat splits.

## Mục lục phối hợp & ghi đè Skill (Skill Composition & Override Matrix)

| Stage | Skill Interaction | `su_ke_lai` v3 Contract & Override |
|---|---|---|
| **1. Topic & Packaging** | Combines with [vp-research-architect](../vp-research-architect/SKILL.md) | `brief.json` / `content.json` Schema 3.0, `youtube_title <= 55` chars, `parent_long_id` linkage on spin-offs. |
| **2. Script & Pacing** | Combines with [vp-scriptwriting](../vp-scriptwriting/SKILL.md) + **overrides structure** via [pacing-and-script-rules.md](references/pacing-and-script-rules.md) | Long: `10 chapters × 12 zero-filler sentences = 120 sentences` (`~9m15s–9m45s`), split into `2` clause sub-beats/sentence (`240` beats, `~2.35s/image`). Short: `12` beats (`~48–58s`), close CTA + Long bridge in final `15%`. |
| **3. Visual System** | **FULLY OVERRIDES** [vp-full-frame-quality](../vp-full-frame-quality/SKILL.md) | **Do NOT use 2D Doodle `1.7.0`.** Locks **Option 1 (`su_ke_lai_35mm_live_action_v3`)** per [visual-grammar-option1.md](references/visual-grammar-option1.md): `allowed_text=None` on 100% story frames, `clean_beluga_sparkle_pil` + `1.045x` overscan center-crop. |
| **4. Flow Generation** | Combines with [vp-flow-cdp](../vp-flow-cdp/SKILL.md) | Long: `240` `16:9` BELUGA frames. Short: `12` `9:16` frames + `12` `omni_flash` `single_frame_i2v` clips (`end_image_path=None`). Thumbnails: Flow-native with `2–4` uppercase Vietnamese words (`< 2MB`, zero PIL/HTML overlay). |
| **5. Audio & Colab T4 Render** | Combines with [vp-colab-bridge](../vp-colab-bridge/SKILL.md) + **overrides voice/render lock** | `VietNarrator_su_ke_lai` (`speaking_rate=1.30`, `inter_beat_gap=0.06s`, `chapter_gap=0.18s`, `-11.0 LUFS / -1.0 dBTP`). Colab T4 `h264_nvenc`: Long `2560x1440@30fps` (`xfade=fade:duration=0.18`, `FFMETADATA1` 10 chapters); Short `1440x2560@30fps` (`cas=0.55`). Bundle `DejaVuSans.ttf`/`DejaVuSans-Bold.ttf` (`fontsdir='fonts' + fc-cache -f`) for `libass`; run `omni_flash` corner `delogo` check before pinning `watermark_150x150.png` at `W-w-36:H-h-36`. |
| **6. Omni-Platform & Publish** | Combines with [vp-omni-platform](../vp-omni-platform/SKILL.md) + [vp-production](../vp-production/SKILL.md) | Publish via `sys/tools/publish_youtube_cdp.py --channel su_ke_lai`: **publish Long first**, capture its live URL, then publish Short with `--related-video <LONG_URL>` and full SEO/chapters/funnel metadata. |

## SSOT Code Paths

- **Production Lock Manifest**: `sys/channels/su_ke_lai/channel_v2_production_lock.json`
- **Video & Visual Formulas**: `sys/channels/vn_flow_video_formulas.py`
- **Script & Hook Formulas**: `sys/channels/vn_competitor_script_formulas.py`
- **Voice Profile**: `sys/assets/voices/ch_su_ke_lai/profile.json` (`VietNarrator_su_ke_lai`)
- **Channel Watermark**: `sys/channels/su_ke_lai/assets/watermark_150x150.png` (pinned bottom-right `W-w-36:H-h-36`)

## Mandatory Verification Commands

```bash
PYTHONPATH=sys pytest sys/tests/test_channel_su_ke_lai.py sys/tests/test_vn_flow_v3_pipeline.py -q
python3 sys/tools/script_cadence_checker.py --help
python3 sys/tools/cta_tone_linter.py --help
python3 sys/visual_pacing.py --help
```

1. **Audio & Video Container**: Verify master WAV (`48000Hz` stereo, `-11.0 LUFS / -1.0 dBTP`) and rendered MP4 via `ffprobe` (`2560x1440` or `1440x2560`, `30fps`, `h264_nvenc`).
2. **Visual Frame Audit**: Extract representative frames from the rendered MP4 and inspect `watermark_150x150.png` placement (`W-w-36:H-h-36`), `libass` Vietnamese diacritics/stamps, `delogo` cleanliness on `omni_flash` clips, and zero AI-drawn text.
