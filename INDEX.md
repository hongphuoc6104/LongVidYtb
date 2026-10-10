# Start here — Video Pilot

Read [AGENTS.md](AGENTS.md), identify the task and authority, then select the route:

| Task | Guide | Skill |
|---|---|---|
| Download/clone or configure a machine | [Getting started](sys/docs/getting-started.md) | vp-setup |
| New chat or continuing unfinished work | [Session handoff](sys/docs/session-start.md) | Skill for the ongoing task |
| Create or repair a video | [Workflow](sys/docs/workflow.md) | vp-production |
| Automated image generation via Flow CDP | [Flow CDP Guide](.agents/skills/vp-flow-cdp/SKILL.md) | vp-flow-cdp |
| Troubleshooting technical issues & proven remedies | [Troubleshooting handbook](.agents/skills/vp-troubleshooting/SKILL.md) | vp-troubleshooting |
| Analyze a reference channel and derive an original production playbook | [Reference-video analysis](.agents/skills/vp-channel-patterns/SKILL.md) | vp-channel-patterns |
| Upgrade the system | [Implementation progress (archived)](sys/docs/archive/normalization-progress.md) | vp-development |
| Cleanup/archive/Git synchronization | [Maintenance](sys/docs/maintenance.md) | vp-maintenance |

## Layout

- `sys/`: code, docs, schemas, configuration and operational data.
- `sys/vocab/`: one sense per bank entry; [channel profile](sys/vocab/channel.json).
- `sys/runs/<job>/`: content, versions, requests and artifacts.
- `sys/.state/`: local state; `sys/.gflow/`: browser profiles, excluded from Git.
- `sys/assets/`: visual/voice references; `video/<job>/`: collected products.
- `sys/logs/issues/`: issue logbook and proven recovery remedies ("What worked to fix bugs").
- `.agents/`: Rules and discoverable skills; corresponding links in `sys/` point here.

The root launcher is `python3 pilot.py`; operational examples use `sys/` as their working directory. Do not infer job/revision from MP4 filenames.

## Upgrade status

Authority/modes/Colab and English portrait direction are being normalized; [progress and evidence](sys/docs/archive/normalization-progress.md) identify verified capabilities. Do not use v3 auto for the new no-reviewer auto task. Existing jobs migrate only through compatibility-checked tools, never direct state/baseline edits.

[Active documentation index](sys/docs/INDEX.md). [Layout migration](sys/docs/archive/layout-migration.md) and [branch synchronization](sys/docs/archive/branch-sync.md) are historical records; their old measurements/tests are not current acceptance evidence.
