# Start here — Video Pilot

## Mandatory Pre-Task Reading Protocol (Priority Document Gate)
Before initiating any task, every agent MUST follow the 3-tier reading protocol:
1. **Tier 1 (Mandatory for ALL tasks)**: [AGENTS.md](AGENTS.md) and [PLAYBOOK.md](PLAYBOOK.md).
2. **Tier 2 (Domain Skill SSOT)**: Read the specific `SKILL.md` matching your current task domain below.
3. **Tier 3 (Deep Reference)**: Read specific reference guides in `.agents/skills/<skill>/references/` when diagnosing errors.

---

## Task Routing Table

| Task | Guide | Skill |
|---|---|---|
| Download/clone or configure a machine | [Getting started](sys/docs/getting-started.md) | [vp-setup](.agents/skills/vp-setup/SKILL.md) |
| New chat or continuing unfinished work | [Session handoff](sys/docs/session-start.md) | Skill for the ongoing task |
| Architect research narrative, 3-Tier Funnel Packaging & Spin-offs | [Research architect](.agents/skills/vp-research-architect/SKILL.md) | [vp-research-architect](.agents/skills/vp-research-architect/SKILL.md) |
| Author conversational narration, Truth-Slap Hooks & verify acoustic cadence | [Scriptwriting guide](.agents/skills/vp-scriptwriting/SKILL.md) | [vp-scriptwriting](.agents/skills/vp-scriptwriting/SKILL.md) |
| Dual-Format Production (`short_9x16` Full-Chain or `long_16x9` High-Density) | [Workflow](sys/docs/workflow.md) | [vp-production](.agents/skills/vp-production/SKILL.md) |
| Bản Đồ Quyền Lực (`ban_do_quyen_luc`) v3 4-Style Photorealistic Geopolitical Channel SSOT | [Channel PLAN](sys/channels/ban_do_quyen_luc/PLAN.md) | [vp-channel-ban-do-quyen-luc](.agents/skills/vp-channel-ban-do-quyen-luc/SKILL.md) |
| Sử Kể Lại (`su_ke_lai`) v3 Option 1 35mm Live-Action Channel SSOT | [Channel PLAN](sys/channels/su_ke_lai/PLAN.md) | [vp-channel-su-ke-lai](.agents/skills/vp-channel-su-ke-lai/SKILL.md) |
| 2D Minimalist Doodle (`1.7.0 Nguệch Ngoạc`) Visual Quality & Continuity | [Full-frame quality guide](.agents/skills/vp-full-frame-quality/SKILL.md) | [vp-full-frame-quality](.agents/skills/vp-full-frame-quality/SKILL.md) |
| Package shared-image YouTube, Facebook & standalone Reels/TikTok deliverables | [Omni-platform guide](.agents/skills/vp-omni-platform/SKILL.md) | [vp-omni-platform](.agents/skills/vp-omni-platform/SKILL.md) |
| Automated image & video generation via Flow CDP pool | [Flow CDP Guide](.agents/skills/vp-flow-cdp/SKILL.md) | [vp-flow-cdp](.agents/skills/vp-flow-cdp/SKILL.md) |
| Remote Colab T4 TTS synthesis & native FFmpeg h264_nvenc render | [Colab Bridge Guide](.agents/skills/vp-colab-bridge/SKILL.md) | [vp-colab-bridge](.agents/skills/vp-colab-bridge/SKILL.md) |
| Troubleshooting technical issues & proven remedies | [Troubleshooting handbook](.agents/skills/vp-troubleshooting/SKILL.md) | [vp-troubleshooting](.agents/skills/vp-troubleshooting/SKILL.md) |
| Analyze a reference channel and derive an original production playbook | [Reference-video analysis](.agents/skills/vp-channel-patterns/SKILL.md) | [vp-channel-patterns](.agents/skills/vp-channel-patterns/SKILL.md) |
| Upgrade the engine, rules, skills, tests, and conveyor | [Implementation progress (archived)](sys/docs/archive/normalization-progress.md) | [vp-development](.agents/skills/vp-development/SKILL.md) |
| Cleanup/archive/Git synchronization | [Maintenance](sys/docs/maintenance.md) | [vp-maintenance](.agents/skills/vp-maintenance/SKILL.md) |

## Channel-to-Skill Routing & Composition Matrix (Mục Lục Điều Phối Quy Trình Chung & Skill Riêng Từng Kênh)

Shared workflow skills (`vp-research-architect`, `vp-scriptwriting`, `vp-flow-cdp`, `vp-colab-bridge`, `vp-omni-platform`, `vp-production`) are **generic and never overridden**. Channel-specific parameters and visual styles are isolated in dedicated channel skills:

| Channel Scope | Shared Workflow Skills (Unmodified) | Channel-Specific Style & Parameter Skill | Channel-Specific Scope |
|---|---|---|---|
| **`ban_do_quyen_luc` (Bản Đồ Quyền Lực)** | `vp-research-architect`, `vp-scriptwriting`, `vp-flow-cdp`, `vp-colab-bridge`, `vp-omni-platform`, `vp-production` | [vp-channel-ban-do-quyen-luc](.agents/skills/vp-channel-ban-do-quyen-luc/SKILL.md) | Supplies `ban_do_quyen_luc_4styles_photoreal_v3` (3-pillar photorealistic base + 4-mode storytelling combination), `VietNarrator_ban_do_quyen_luc` (`1.15x`), `240`-beat 9-chapter Long / `12–14`-beat Short pacing, and 2K brand specs. |
| **`su_ke_lai` (Sử Kể Lại)** | `vp-research-architect`, `vp-scriptwriting`, `vp-flow-cdp`, `vp-colab-bridge`, `vp-omni-platform`, `vp-production` | [vp-channel-su-ke-lai](.agents/skills/vp-channel-su-ke-lai/SKILL.md) | Supplies Option 1 `su_ke_lai_35mm_live_action_v3` visual grammar, `VietNarrator_su_ke_lai` (`1.30x`), 2-clause `240`-beat Long / `12`-beat `omni_flash` Short pacing, and 2K brand specs. |
| **Standard 2D Doodle Channels** | `vp-research-architect`, `vp-scriptwriting`, `vp-flow-cdp`, `vp-colab-bridge`, `vp-omni-platform`, `vp-production` | [vp-full-frame-quality](.agents/skills/vp-full-frame-quality/SKILL.md) | Supplies `1.7.0 handdrawn_2d_explainer` visual grammar and default `sys/format_profiles.py` settings. |

## System Layout & SSOT

- `sys/`: code, docs, schemas, configuration and operational data.
- `sys/format_profiles.py`: single source of truth for Dual-Format video profiles:
  - `short_9x16`: 100% Full-Chain continuous video (`Omni 1.2 Flash`, 11–15 keyframes, kinetic 1-word `.ass` subtitles, Colab T4 NVENC).
  - `long_16x9`: 240–350 high-density `BELUGA` 8K multi-image visual journey, 1.25x supersampled zero-snap `zoompan`, directional optical `xfade` (0.24s), sidecar `.srt`, and 8–12 chapters.
- `sys/runs/<job>/`: content, versions, requests and artifacts.
- `sys/assets/`: visual and voice references (`VietNarrator` 1.0x).
- `video/<job>/`: collected deliverables (MP4 / SRT / ASS).
- `.agents/skills/`: discoverable skills and canonical references.
- `PLAYBOOK.md`: operational lessons and root-cause fixes (mandatory reading).

[Active documentation index](sys/docs/INDEX.md).
