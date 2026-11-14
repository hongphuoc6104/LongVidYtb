# Active documentation index

Root INDEX remains the entry point. Every agent MUST observe the Priority Document Gate ([AGENTS.md](../../AGENTS.md) -> [PLAYBOOK.md](../../PLAYBOOK.md) -> [Domain SKILL.md](../../.agents/skills/vp-production/SKILL.md)).

| Current source | Purpose |
|---|---|
| [getting-started](getting-started.md), [session-start](session-start.md) | New-machine bootstrap, per-machine profiles and grant/checkpoint/request handoff |
| [workflow](workflow.md), [contracts](contracts.md) | Dual-mode production, auto/review, five outputs, scope/version/impact/ownership |
| [format profiles](../format_profiles.py) | Dual-Format SSOT: `short_9x16` Full-Chain (`Omni 1.2 Flash`) & `long_16x9` High-Density Multi-Image |
| [story-planning](story-planning.md), [narration-length](narration-length-guidance.md), [director-system](director-system.md) | Craft/storyboard/anchors and vp-production references |
| [colab-tts](colab-tts.md), [image-repair-loops](image-repair-loops.md) | Remote heavy processing, voice provenance, request/session and progressing image repair |
| [render-capabilities](render-capabilities.md) | Native Colab Tesla T4 `FFmpeg h264_nvenc` rendering capabilities, `/dev/shm` parallel chunk encoding, and lossless stream-copy |
| [Flow model prompts](flow-prompts.md) | Versioned model/purpose instructions (1.7.0 Nguệch Ngoạc lock), exact learner text and reference provenance |
| [maintenance](maintenance.md) | Reproducibility manifests, verified archive, scoped Git history/branch/remote |
| [AGY adapter](AGY-SETUP.md) | Compatibility entry point without duplicate Rules/reviewer |
| [Rules](../../AGENTS.md), [14 Skills](../../.agents/skills) | Authority/execution/accounts/brand; one skill per workflow, plus channel SSOT routing via [vp-channel-ban-do-quyen-luc](../../.agents/skills/vp-channel-ban-do-quyen-luc/SKILL.md) and [vp-channel-su-ke-lai](../../.agents/skills/vp-channel-su-ke-lai/SKILL.md) |

Outdated historical planning documents and pre-normalization `legacy/` guides have been cleaned up and consolidated into the current documentation or archived in `sys/docs/archive/`.
