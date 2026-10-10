---
name: vp-troubleshooting
description: Rapid lookup for known issues and proven remedies ("What worked to fix bugs") in Video Pilot: Colab T4 headless display, Chromium tile drops, Flow Kit timeouts, and Audio alignment.
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
| **COLAB-HEADLESS** | Rendering error on Colab T4: Chrome crash, blank white screen, missing X11 display, or expired `video-pilot-tts` session | Colab GPU lacks a physical display; requires compositor sync flags, shell wrapper script, and session/runtime bootstrap check. | [colab-headless.md](references/colab-headless.md) |
| **RENDER-TILES** | Rendered MP4 shows white rectangular tiles, dashed black border teeth, or 10x render slowdown (>10m per minute of video) | Missing compositor flags, or blanket full-frame `1920x1080` SVG `line_boil: true` running in CPU software under `--disable-gpu-rasterization`. | [renderer-tiles.md](references/renderer-tiles.md) |
| **FLOWKIT-GEN** | Flow Kit generation error: timeout > 120s, `PUBLIC_ERROR_UNUSUAL_ACTIVITY`, cross-profile `based_on` failure, or `NANO_BANANA_2_1` model mismatch | Port 8100 daemon/tab issue, destructive tab reload breaking `Object.assign` neuter, ungrouped `based_on` chains across profiles, or missing `"BELUGA"` wire code. | [flowkit-generation.md](references/flowkit-generation.md) |
| **AUDIO-ALIGN** | Captions lead/lag spoken audio, audio duration mismatches scene budget, TTS mispronunciation | Speech rate uncalibrated, missing silence padding between script beats. | [audio-alignment.md](references/audio-alignment.md) |
| **NEW-ISSUE** | Novel issue encountered and resolved after successful bugfix | Document the new issue and solution in `sys/logs/issues/`. | [issue-template.md](references/issue-template.md) |

---

## Standard Bug Handling Workflow for Agents
1. **Verify on live execution pipeline**: Reproduce the error on command line or actual execution logs; do not rely on mock unit tests.
2. **Match against issue table**: Identify the matching category code in the index table above.
3. **Apply proven remedies**: Open the corresponding file in `references/` and execute the verified "Proven Remedies" steps.
4. **Update issue logbook**: If encountering a new variant or bug, document in `sys/logs/issues/<timestamp>-<job>-<module>.md` using the standard template.
