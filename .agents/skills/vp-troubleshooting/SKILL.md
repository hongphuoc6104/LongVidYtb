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
| **RENDER-TILES** | Rendered MP4 shows white rectangular tiles, dashed black border teeth, or 10x render slowdown (>10m per minute of video) | Missing 4-layer sync tile locks (`--disable-checker-imaging`, `<Img decoding="sync">`), uncalibrated GPU EGL backend, or full-frame SVG `line_boil`. | [renderer-tiles.md](references/renderer-tiles.md) / [remote-remotion-render.md](../vp-colab-bridge/references/remote-remotion-render.md) |
| **FLOW-CDP-GEN** | Flow CDP generation error: timeout > 120s, `PUBLIC_ERROR_UNUSUAL_ACTIVITY`, cross-profile `based_on` failure, or model mismatch | CDP port/tab issue, destructive tab reload breaking `Object.assign` neuter, ungrouped `based_on` chains across profiles, or missing `"BELUGA"` wire code. | [flow-cdp-generation.md](references/flow-cdp-generation.md) |
| **AUDIO-ALIGN** | Captions or visual shots lead/lag spoken audio, mid-scene image desync, audio duration mismatches scene budget, TTS mispronunciation | Coarse scene-level scaling instead of Cue-Window Allocation (`[cue_i.start, cue_{i+1}.start)`), inverted semantic shot order, uncalibrated speech rate, or missing silence padding. | [audio-alignment.md](references/audio-alignment.md) |
| **NEW-ISSUE** | Novel issue encountered and resolved after successful bugfix | Document the new issue and solution in `PLAYBOOK.md` conforming to the 6 mandatory fields. | [issue-template.md](references/issue-template.md) |

---

## Standard Bug Handling Workflow for Agents
Adhere strictly to the **4-Step Bug Resolution Protocol** and Playbook governance defined in [PLAYBOOK.md](../../../PLAYBOOK.md):
1. **E2E Reproduction**: Reproduce on the live pipeline, never synthetic unit mocks.
2. **Root Cause Analysis**: Pinpoint the physical failure mechanism.
3. **Architectural Fix**: Implement modular, resilient code at the source.
4. **E2E Verification & Playbook Entry**: Verify output via technical inspection (`ffprobe`) and log the entry with all 6 mandatory fields.
