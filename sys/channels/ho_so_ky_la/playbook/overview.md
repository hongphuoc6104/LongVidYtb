---
name: vp-channel-ho-so-ky-la
description: "Dedicated channel specifications for Hồ Sơ Kỳ Lạ (ho_so_ky_la). Holds all channel-specific identity, 3D Noir Forensic Diorama & 4-style visual options (ho_so_ky_la_3d_noir_forensic_v3), 260-beat 10-chapter Long & 18-beat Short investigative pacing, VietNarrator_ho_so_ky_la 1.10x voice profile, and 2K brand parameters to pair with shared workflow skills without overriding them."
---

# Hồ Sơ Kỳ Lạ (`ho_so_ky_la`) — Dedicated Channel Specifications (v3)

Channel-specific specification module for **Hồ Sơ Kỳ Lạ** (`@HoSoKyLaVN`, YouTube Channel ID `UCEWZEZJTFpNCbURgtNLHA1A`, `profile_3`, port `9224`). Shared workflow skills ([vp-content-studio](../../../../.agents/skills/vp-content-studio/SKILL.md), [vp-content-studio](../../../../.agents/skills/vp-content-studio/SKILL.md), [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md), [vp-flow-cdp](../../../../.agents/skills/vp-flow-cdp/SKILL.md), [vp-colab-bridge](../../../../.agents/skills/vp-colab-bridge/SKILL.md), [vp-production](../../../../.agents/skills/vp-production/SKILL.md), [vp-production](../../../../.agents/skills/vp-production/SKILL.md)) remain **100% shared and unmodified**; this skill supplies only the parameters unique to `ho_so_ky_la`. Read [visual-grammar-noir-forensic.md](visual.md) for the 3-pillar 3D Noir Forensic Diorama + 4-mode investigative grammar and [pacing-and-script-rules.md](pacing.md) for beat density and script rules.

## Bảng Ghép Nối Quy Trình Dùng Chung ↔ Đặc Thù Riêng Kênh `ho_so_ky_la` (Shared Workflow ↔ Channel-Specific Matrix)

| Shared Workflow Step (Unmodified) | `ho_so_ky_la` Channel-Specific Parameters (Plug-in Only) |
|---|---|
| **1. Research & Packaging** ([vp-content-studio](../../../../.agents/skills/vp-content-studio/SKILL.md)) | Niche: Real-world unsolved mysteries, aviation/maritime engineering disasters, and forensic case files (`ho_so_ky_la`, `@HoSoKyLaVN`, `profile_3`, port `9224`, playlist `"Hồ Sơ Kỳ Lạ — Giải Mã Bí Ẩn Có Thật"`, `parent_long_id` Short-to-Long funnel). |
| **2. Script & Beat Density** ([vp-content-studio](../../../../.agents/skills/vp-content-studio/SKILL.md)) | Per [pacing-and-script-rules.md](pacing.md): Long = `10 chapters`, `260` visual beats, `~10–14m`, `<= 30s/sentence`, `<= 24` syllables Cold Open, Open Loop in `sents[1:4]`, hypothesis elimination; Short = `18` beats, `~52–90s`, `<= 5.0s/sentence`, `<= 18` syllables hook, close CTA + channel bridge in the last 15%. |
| **3. Channel Visual Style** *(selected instead of 2D Doodle [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md))* | Per [visual-grammar-noir-forensic.md](visual.md): **`ho_so_ky_la_3d_noir_forensic_v3`** — 3-pillar 3D Noir Forensic Diorama (`#0A0B0E`, `#181B22`, `#E8DFC8`, `#C0392B`, `#C9A24D`) + 4 investigative visual modes (`MODE_1_EVIDENCE_STAMP`, `MODE_2_HYPOTHESIS_CONTRAST`, `MODE_3_DOSSIER_CHECKLIST`, `MODE_4_NOIR_CINEMATIC_PACING`), `allowed_text=None` on raw Flow frames, bottom-right `delogo` + `1.045x` overscan, zero gore/stickman. |
| **3b. Modular FX & Audio Warehouse** ([vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md)) | Plugs into sharded `sys/fx_warehouse/` (`archetypes`, `camera_vfx`, `hud_widgets`, `audio_sfx_bgm`, `selector`). Pulls 4 investigative styles: Style 1 (IMAX 35mm + Stamp), Style 2 (3D X-Ray + Dual Oscilloscope), Style 3 (LEMMiNO Chiaroscuro + CVR Waveform), Style 4 (Vox Radar + Laser Split + 3-Column Triptych). **Bespoke-Per-Video Rule**: When a case file involves non-aviation mechanics (e.g., maritime hull/sonar, poisoning toxicology, ballistics/ciphers), MUST create bespoke `bespoke_hud_spec` (`build_bespoke_topic_hud_patch`) and procedural 48kHz `bespoke_sfx_spec` (`synthesize_bespoke_topic_sfx`) instead of forcing aviation HUDs onto unrelated mysteries. |
| **4. Flow Asset Generation** ([vp-flow-cdp](../../../../.agents/skills/vp-flow-cdp/SKILL.md)) | Long: `260` `16:9` BELUGA frames. Short: `18` `9:16` frames/clips (`omni_flash` `single_frame_i2v` / `reference_start_end`). Thumbnails: Flow-native 3D Noir forensic close-up with `2–4` uppercase Vietnamese words drawn directly (`< 2MB`, zero PIL/HTML overlay cards). |
| **5. Voice & 2K Render Specs** ([vp-colab-bridge](../../../../.agents/skills/vp-colab-bridge/SKILL.md)) | Voice: `VietNarrator_ho_so_ky_la` (`recommended_speed=1.10`, `base_omnivoice_speed=1.00`, `atempo_factor=1.10` V3.1 TTS baseline; local `1.05 -> 1.10` WSOLA retime uses `atempo=1.047619`, `inter_beat_gap_sec=0.10`, `default_tone="forensic_investigative_crisp"`, `-11.0 LUFS / -1.0 dBTP` master). Render: Long `2560x1440@30fps` (`xfade=fade:duration=0.24`), Short `1440x2560@30fps`; bottom-right `delogo` before `sys/channels/ho_so_ky_la/assets/watermark_150x150.png` pinned at `W-w-48:H-h-48` (2K) / `W-w-36:H-h-36` (HD). |
| **6. Multi-Platform Publish** ([vp-production](../../../../.agents/skills/vp-production/SKILL.md) + [vp-production](../../../../.agents/skills/vp-production/SKILL.md)) | Target `--channel ho_so_ky_la` (`profile_3`, port `9224`): publish Long first, capture live URL, publish Short with `Related Video` (`Video có liên quan`) linked to Long, configure End Screen, assign playlist `"Hồ Sơ Kỳ Lạ — Giải Mã Bí Ẩn Có Thật"`, and pin Debate-Trigger comment (`@HoSoKyLaVN`). |

## Channel SSOT Code & Asset Paths

- **Production Lock Manifest**: `sys/channels/ho_so_ky_la/channel_v3_production_lock.json`
- **Channel Blueprint**: `sys/channels/ho_so_ky_la/PLAN.md`
- **Engine Production Lock**: `HO_SO_KY_LA_PRODUCTION_LOCK` in `sys/tools/produce_vn_dual_mode.py`
- **Modular FX & Audio Warehouse**: `sys/fx_warehouse/` (`archetypes.py`, `camera_vfx.py`, `hud_widgets.py`, `audio_sfx_bgm.py`, `selector.py`)
- **Video & Visual Formulas**: `sys/channels/vn_flow_video_formulas.py`
- **Script & Hook Formulas**: `sys/channels/vn_competitor_script_formulas.py`
- **Voice Profile**: `sys/assets/voices/ch_ho_so_ky_la/profile.json` (`VietNarrator_ho_so_ky_la`, `reference.wav`)
- **Channel Watermark & Logo**: `sys/channels/ho_so_ky_la/assets/watermark_150x150.png` & `sys/assets/logos/ho_so_ky_la.png`
- **Episode 05 Blueprint & Scripts**: `sys/channels/ho_so_ky_la/ep05_helios_522_v3_blueprint.json`, `ep05_content_short.json`, `ep05_content_long.json`
- **Release Registry**: `sys/channels/ho_so_ky_la/release_links.json`

## Mandatory Verification Commands

```bash
PYTHONPATH=sys pytest sys/tests/test_channel_ho_so_ky_la.py sys/tests/test_channel_voice_profiles.py sys/tests/test_vn_dual_mode_pipeline.py -q
python3 sys/tools/script_hook_scorer.py --content sys/channels/ho_so_ky_la/ep05_content_short.json --channel ho_so_ky_la --format short_9x16
python3 sys/tools/script_hook_scorer.py --content sys/channels/ho_so_ky_la/ep05_content_long.json --channel ho_so_ky_la --format long_16x9
python3 sys/tools/script_cadence_checker.py --help
python3 sys/tools/cta_tone_linter.py --help
```

1. **Audio & Video Container**: Verify master WAV (`48000Hz` stereo, `-11.0 LUFS / -1.0 dBTP`) and rendered MP4 via `ffprobe` (`2560x1440` Long or `1440x2560` Short, `30fps`, `h264_nvenc`).
2. **Visual & Forensic Mode Audit**: Extract representative frames across `MODE_1_EVIDENCE_STAMP`, `MODE_2_HYPOTHESIS_CONTRAST`, `MODE_3_DOSSIER_CHECKLIST`, and `MODE_4_NOIR_CINEMATIC_PACING` beats, verifying clean bottom-right `delogo`, crisp `watermark_150x150.png` placement (`W-w-48:H-h-48` 2K / `W-w-36:H-h-36` HD), and zero AI-drawn text inside raw Flow photography (`allowed_text=None`).
