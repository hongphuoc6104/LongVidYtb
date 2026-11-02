---
name: vp-troubleshooting
description: "Quick remedies for Colab headless display, tile drops, Flow CDP timeouts, and audio sync."
---

# Video Pilot — Troubleshooting Handbook & Technical Remedies

This skill provides **Progressive Disclosure** lookup for operational issues in Video Pilot.
**Rules for Agents**:
1. Review the symptom summary table below first.
2. Only open the detailed reference file in `references/` when the actual observed symptom matches the issue category.
3. Never load all detailed reference files into context unless needed, avoiding context window bloat.

---

## Issue Summary Index

| Category Code | Triggering Symptoms | Root Cause Summary | Detailed Reference File |
|---|---|---|---|
| **COLAB-HEADLESS** | Rendering error on Colab T4: Chrome crash, blank white screen, missing X11 display, or expired `video-pilot-tts` session | Colab GPU lacks a physical display; requires compositor sync flags, shell wrapper script, and session/runtime bootstrap check. | [colab-headless.md](references/colab-headless.md) / [vp-colab-bridge](../vp-colab-bridge/SKILL.md) |
| **COLAB-RENDER** | Video render failure on Colab T4, NVENC encoder initialization error, audio loudness desync, or sub burn-in failure | Retired slow Remotion/Chromium/TPU rendering in favor of Native Tesla T4 `FFmpeg h264_nvenc` (`flow_video_worker.py` via `job_worker.py`, `-c:v h264_nvenc -preset p4 -b:v 6M`, `loudnorm=I=-11.0:TP=-1.0`). | [remote-ffmpeg-nvenc-render.md](../vp-colab-bridge/references/remote-ffmpeg-nvenc-render.md) / [vp-colab-bridge](../vp-colab-bridge/SKILL.md) |
| **FLOW-CDP-GEN** | Flow CDP generation error: timeout > 120s, `PUBLIC_ERROR_UNUSUAL_ACTIVITY`, cross-profile `based_on` failure, or model mismatch | CDP port/tab issue, destructive tab reload breaking `Object.assign` neuter, ungrouped `based_on` chains across profiles, or missing `"BELUGA"` wire code. | [flow-cdp-generation.md](references/flow-cdp-generation.md) |
| **AUDIO-ALIGN** | Captions or visual shots lead/lag spoken audio, mid-scene image desync, audio duration mismatches scene budget, TTS mispronunciation | Coarse scene-level scaling instead of Cue-Window Allocation (`[cue_i.start, cue_{i+1}.start)`), inverted semantic shot order, uncalibrated speech rate, or missing silence padding. | [audio-alignment.md](references/audio-alignment.md) |
| **CHROME-TMP-BLOAT** | Host SSD `/` fills suddenly during multi-channel CDP runs with multi-GB `/tmp/url_fetcher_*` folders | Chromium Component Updater / OptimizationGuide model fetcher downloading CRX/models per profile into `/tmp` and leaving orphans on teardown; mitigated by `--component-updater=url-source=http://127.0.0.1:1` in `sys/flow_cdp/resource_locks.py` and `clean_stale_chrome_tmp_artifacts()` in `sys/flow_cdp/process_manager.py`. | [vp-flow-cdp](../vp-flow-cdp/SKILL.md) |
| **NEW-ISSUE** | Novel issue encountered and resolved after successful bugfix | Document the new issue and solution in `PLAYBOOK.md` conforming to the 6 mandatory fields. | [issue-template.md](references/issue-template.md) |

---

## Standard Bug Handling Workflow for Agents
Adhere strictly to the **4-Step Bug Resolution Protocol** and Playbook governance defined in [PLAYBOOK.md](../../../PLAYBOOK.md):
1. **E2E Reproduction**: Reproduce on the live pipeline, never synthetic unit mocks.
2. **Root Cause Analysis**: Pinpoint the physical failure mechanism.
3. **Architectural Fix**: Implement modular, resilient code at the source.
4. **E2E Verification & Playbook Entry**: Verify output via technical inspection (`ffprobe`) and log the entry with all 6 mandatory fields.
