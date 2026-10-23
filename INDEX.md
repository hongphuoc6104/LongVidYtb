# Start here — Video Pilot

Read [AGENTS.md](AGENTS.md), identify the task and authority, then select the route:

| Task | Guide | Skill |
|---|---|---|
| Download/clone or configure a machine | [Getting started](sys/docs/getting-started.md) | vp-setup |
| New chat or continuing unfinished work | [Session handoff](sys/docs/session-start.md) | Skill for the ongoing task |
| Architect a new research topic, Packaging Contract & Spin-offs (`brief.json` & `content.json` v3.0) | [Research architect](.agents/skills/vp-research-architect/SKILL.md) | vp-research-architect |
| Author conversational narration, Truth-Slap Hooks & verify acoustic cadence | [Scriptwriting guide](.agents/skills/vp-scriptwriting/SKILL.md) | vp-scriptwriting |
| Create or repair a video (`long_16x9` or `short_9x16`) | [Workflow](sys/docs/workflow.md) | vp-production |
| Author or repair full-frame visual beats, continuity & camera motion (`full_frame_v1`) | [Full-frame quality guide](.agents/skills/vp-full-frame-quality/SKILL.md) | vp-full-frame-quality |
| Package shared-image YouTube, Facebook & standalone Reels/TikTok deliverables | [Omni-platform guide](.agents/skills/vp-omni-platform/SKILL.md) | vp-omni-platform |
| Automated image generation via Flow CDP | [Flow CDP Guide](.agents/skills/vp-flow-cdp/SKILL.md) | vp-flow-cdp |
| Remote Colab T4 TTS synthesis & headless Remotion render | [Colab Bridge Guide](.agents/skills/vp-colab-bridge/SKILL.md) | vp-colab-bridge |
| Troubleshooting technical issues & proven remedies | [Troubleshooting handbook](.agents/skills/vp-troubleshooting/SKILL.md) | vp-troubleshooting |
| Analyze a reference channel and derive an original production playbook | [Reference-video analysis](.agents/skills/vp-channel-patterns/SKILL.md) | vp-channel-patterns |
| Upgrade the system | [Implementation progress (archived)](sys/docs/archive/normalization-progress.md) | vp-development |
| Cleanup/archive/Git synchronization | [Maintenance](sys/docs/maintenance.md) | vp-maintenance |

## Layout

- `sys/`: code, docs, schemas, configuration and operational data.
- `sys/format_profiles.py`: single source of truth for Dual-Format video profiles (`long_16x9` Landscape Explainer & `short_9x16` Vertical Spin-offs with dynamic duration based on narrative depth and measured audio).
- `sys/runs/<job>/`: content, versions, requests and artifacts.
- `sys/.state/`: local state; `~/.config/google-chrome`: Flow CDP browser profiles, excluded from Git.
- `sys/assets/`: visual/voice references; `video/<job>/`: collected products.
- `sys/logs/issues/`: issue logbook and proven recovery remedies ("What worked to fix bugs").
- `.agents/`: Rules and discoverable skills; corresponding links in `sys/` point here.

The root launcher is `python3 pilot.py`; operational examples use `sys/` as their working directory. Do not infer job/revision from MP4 filenames.

## Upgrade status

Engine 4 is active; [progress and evidence](sys/docs/archive/normalization-progress.md) identify verified capabilities. Existing jobs migrate only through compatibility-checked tools, never direct state/baseline edits.

[Active documentation index](sys/docs/INDEX.md). [Layout migration](sys/docs/archive/layout-migration.md) and [branch synchronization](sys/docs/archive/branch-sync.md) are historical records.
