---
name: vp-channel-co-the-ke
description: Dedicated channel specifications for Cơ Thể Kể (co_the_ke). Holds all channel-specific identity, 3D Endoscopic Biomedical Cinematography & 4-mode visual grammar (co_the_ke_3d_biomedical_v3), 240-beat 10-chapter Long & 18-beat Short physiological pacing, VietNarrator_co_the_ke 1.12x voice profile, and 2K brand parameters to pair with shared workflow skills without overriding them.
---

# Cơ Thể Kể (`co_the_ke`) — Dedicated Channel SSOT v3.0

Use this channel skill alongside the shared workflow skills (`vp-content-studio`, `vp-content-studio`, `vp-visual-fx`, `vp-visual-fx`, `vp-flow-cdp`, `vp-colab-bridge`, `vp-production`, `vp-production`). Channel rules here isolate `co_the_ke` identity and V3 biomedical specs without overriding shared pipeline invariants.

| Pipeline Stage | Shared Workflow Skill | Channel-Specific Lock (`co_the_ke` V3.0) |
|---|---|---|
| **1. Channel Identity & Audience** | — | Channel `Cơ Thể Kể` (`@CoTheKeVN`, ID `UCgehIaP3nZ5jdcZfI3eI7RQ`, Chrome `profile_1`, port `9225`, email `phuocnguyen010204@gmail.com`). Core VN demographic: Vietnam `95.87%`, ages 25–44 (`78.12%` combined), TV `40.79%` + Mobile `50.4%`. |
| **2. Research & Strategy** | [vp-content-studio](../../../../.agents/skills/vp-content-studio/SKILL.md) | 3-Tier Funnel grounded in peer-reviewed biomedical sources (NIH, WHO, AHA, CDC, Nature, Harvard Health, Walker 2017): everyday physiological shocks -> deep cellular cascade `long_16x9` -> linked `short_9x16` spin-off (`parent_long_id`). Zero cure/treatment claims or supplement promotion. |
| **3. Scriptwriting & Pacing** | [vp-content-studio](../../../../.agents/skills/vp-content-studio/SKILL.md) + [pacing-and-script-rules.md](pacing.md) | See [pacing-and-script-rules.md](pacing.md). Cold Open (`<= 18` syl Short / `<= 24` syl Long, zero `[pause:...]`) -> Open Loop (`sents[1:4]`) -> `10` chapters / `240` beats Long (`8.5–13m`, `510–780s`), `18` beats (`48–60s`) Short; Debate/Action CTA + `"Cơ Thể Kể"` bridge; strictly zero "like/share/subscribe" or `#learnontiktok`. |
| **4. Visual Grammar & FX** | [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md) + [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md) | See [visual-grammar-biomedical-v3.md](visual.md). 3-Pillar 3D Endoscopic Biomedical Cinematography (`#0A192F`, `#0F172A`, `#06B6D4`, `#EF4444`, `#F8FAFC`, `#F59E0B`) + 4 Modes (`MODE_1_BIOMETRIC_STAMP`, `MODE_2_NORMAL_VS_STRESS_SPLIT`, `MODE_3_CASCADE_CHECKLIST`, `MODE_4_ENDOSCOPIC_PACING`), `archetype_3_science_xray`, `allowed_text=None` on raw Flow frames, bottom-right `delogo` + `1.045x` overscan, zero gore/stickman/kawaii on V3. |
| **5. Voice & 2K Render Specs** | [vp-colab-bridge](../../../../.agents/skills/vp-colab-bridge/SKILL.md) | Voice: `VietNarrator_co_the_ke` (`recommended_speed=1.12`, `default_tone="authoritative_calm"`, EQ `highpass=f=85,equalizer=f=190:t=q:w=1.2:g=-2.0,equalizer=f=3000:t=q:w=1.2:g=1.4,lowpass=f=13500`, `-11.0 LUFS / -1.0 dBTP` master). Render: Long `2560x1440@30fps` (`xfade=fade:duration=0.20`), Short `1440x2560@30fps`; bottom-right `delogo` before `sys/channels/co_the_ke/assets/watermark_150x150.png` at `W-w-48:H-h-48` (2K) / `W-w-36:H-h-36` (HD). |
| **6. Multi-Platform Publish** | [vp-production](../../../../.agents/skills/vp-production/SKILL.md) + [vp-production](../../../../.agents/skills/vp-production/SKILL.md) | Target `--channel co_the_ke` (`profile_1`, port `9225`, **NEVER delete existing videos or personal playlists**): `Science & Technology`, Language `Vietnamese`, Flow-native thumbnail `<2MB` (`2–4` uppercase VN words, zero `✦`, zero PIL card overlay), `.vi.srt` Published, Long `End Screens` + `Info Cards`, Short `Related Video` linked to Long, and pinned biomedical comment (`@CoTheKeVN`). |

## Channel Assets & Entrypoints (SSOT)
- **Production Lock Manifest**: `sys/channels/co_the_ke/channel_v3_production_lock.json`
- **Channel Blueprint**: `sys/channels/co_the_ke/PLAN.md`
- **Bundle Builder & Registry**: `sys/channels/co_the_ke/builder.py`, `sys/channels/registry.py`, `sys/channels/vn_flow_video_formulas.py`, `sys/channels/vn_competitor_script_formulas.py`
- **FX Archetype & Warehouse**: `sys/fx_warehouse/archetypes.py` (`archetype_3_science_xray`), `sys/fx_warehouse/selector.py`
- **Voice Profile & Audition**: `sys/assets/voices/ch_co_the_ke/profile.json` (`VietNarrator_co_the_ke`), `sys/assets/voices/ch_co_the_ke/audition-report.json`
- **Channel Watermark & Brand Assets**: `sys/channels/co_the_ke/assets/{avatar_800x800.png,banner_2048x1152.png,watermark_150x150.png,endcard_16x9.jpg,endcard_9x16.jpg}` & `sys/assets/logos/co_the_ke.png`
- **Release Registry**: `sys/channels/co_the_ke/release_links.json`

## Mandatory Verification Commands
```bash
PYTHONPATH=sys sys/.venv/bin/python -m pytest sys/tests/test_channel_co_the_ke.py sys/tests/test_channel_voice_profiles.py sys/tests/test_vn_dual_mode_pipeline.py sys/tests/test_fx_warehouse.py -q
PYTHONPATH=sys sys/.venv/bin/python sys/tools/script_hook_scorer.py --content <content.json> --channel co_the_ke --format short_9x16
PYTHONPATH=sys sys/.venv/bin/python sys/tools/script_cadence_checker.py --content <content.json> --format short_9x16
PYTHONPATH=sys sys/.venv/bin/python sys/tools/cta_tone_linter.py --content <content.json> --format short_9x16 --channel co_the_ke
./pipeline run
```
