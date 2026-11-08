# Video Pilot

Video Pilot is an autonomous AI explainer video production system engineered for dual-format intellectual storytelling:
- **`short_9x16` (Vertical Spin-off, 48–60s)**: 100% Full-Chain continuous video clips (`Omni 1.2 Flash` / `macaron_cookie_i2v_fl_4s/6s/8s/10s` stitched from 11–15 `BELUGA` keyframes with zero-stutter blending and kinetic 1-word Red/Yellow `.ass` subtitles).
- **`long_16x9` (Landscape Explainer, 8m30s–13m)**: High-density multi-image visual journey (`240–350` `BELUGA` 8K frames, 1-hop progressive state transitions across 4 visual pacing modes, supersampled zero-snap `zoompan`, directional optical `xfade`, sidecar `.srt`, and 8–12 `FFMETADATA1` YouTube chapters).

All audio synthesis (`VietNarrator` 1.0x, -11.0 LUFS) and final video rendering (`-c:v h264_nvenc -preset p4 -b:v 6M`) run on remote Tesla T4 GPUs via Google Colab. Visual generation runs via local headless Chrome GPU on Google Flow CDP across a 39-profile pool.

## Mandatory Pre-Task Reading Protocol (Priority Document Gate)

Every agent session MUST read the required documents before taking any action:
1. **Tier 1 (Mandatory for ALL tasks)**: [AGENTS.md](AGENTS.md) (SSOT Architecture & Governance) and [PLAYBOOK.md](PLAYBOOK.md) (Operational Post-Mortems & Anti-Regression Rules).
2. **Tier 2 (Domain Skill SSOT)**: Read the exact domain `SKILL.md` (e.g. [.agents/skills/vp-production/SKILL.md](.agents/skills/vp-production/SKILL.md)) for the task before writing code or running production.
3. **Tier 3 (Deep Reference)**: Inspect targeted references in `.agents/skills/<skill>/references/` when encountering specific error codes.

## Getting Started

1. Read [INDEX](INDEX.md) to select the task route.
2. New machine setup: [getting-started](sys/docs/getting-started.md). New chat session: [session-start](sys/docs/session-start.md).
3. Production workflows: [workflow](sys/docs/workflow.md); Dual-mode production: `sys/tools/produce_vn_dual_mode.py`.
4. Quality and Invariants: [AGENTS.md](AGENTS.md) and [PLAYBOOK.md](PLAYBOOK.md).

## Architecture & Infrastructure

- **Local Machine**: Lightweight dashboard, session management, and GPU Headless Chrome Flow CDP (`--ozone-platform=x11 --force-gpu-mem-available-mb=1843`).
- **Remote Colab Tesla T4**: Multi-T4 pool for OmniVoice TTS synthesis and native FFmpeg NVENC video encoding with `/dev/shm` parallel chunk processing.
- **Visual Style**: 2D Minimalist Doodle (`1.7.0 Nguệch Ngoạc` lock in `sys/visual_style.py`: 7-color palette, pure-white bald stickman, `#3B82C4` cerulean-blue shirt, round white circle hands, >=60% negative space).
