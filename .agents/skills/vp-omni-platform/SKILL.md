---
name: vp-omni-platform
description: "Manage dual-format production, repackaging verified 16:9 long-form narration segments into 9:16 standalone shorts."
---

# VP Omni Platform — Dual-Format & Short Spinoff Production

`vp-omni-platform` manages the dual-format publishing pipeline across YouTube long-form (`long_16x9`) and vertical short-form platforms (`short_9x16` for TikTok, YouTube Shorts, and Reels). It enforces standalone short narrative integrity and orchestrates zero-cost audio repurposing (`sys/omni_render.py`) from verified master audio tracks.

---

## 1. Dual-Format Mission & Architectural Invariants (`sys/format_profiles.py`)
- **`long_16x9` (Master Video)**:
  - Format: 1920x1080, 11–13 minutes (8 chapters / 48 scenes) or 5–8 minutes `full_frame_v1` acceptance explainers.
  - Subtitles: Disabled on canvas (`subtitles: false`) with full-bleed imagery and separate `.srt` output.
- **`short_9x16` (Omni Spinoffs)**:
  - Format: 1080x1920, 45–60 seconds, exactly 5 standalone scenes (`SC01..SC05`).
  - Speed: 1.26x acceleration with dynamic burn-in karaoke subtitles (`subtitles: true`, `karaokeTokens`).
  - Standalone Integrity: **Never raw-cut middle chapters (`CH02..CH08`)** of a 16:9 video directly for TikTok. Every Short must have its own dedicated Hook (`SC01`), body progression (`SC02..SC04`), and practical payoff (`SC05`).

---

## 2. Audio Repurposing Engine (`sys/omni_render.py`)
- **Zero Re-synthesis Cost**: Spinoff shorts reuse verified speech segments directly from the master 16:9 narration track (`audio['tracks']['vi']`).
- **Acoustic Word Re-anchoring**: Speech chunks and acoustic word timestamps are re-scaled (`timestamp / factor`) and mapped seamlessly onto the 5 standalone scenes.
- **Dedicated Spinoff Hooks**: Only the opening hook scene (`SC01`) synthesizes a fresh hook voice clip (`spinoff_hooks[]`), ensuring strong 3-second viewer retention.

---

## 3. Aspect-Aware Camera & Optical Staging
- **Narrow Viewport Adaptation**: Narrow 9:16 portrait screens tighten horizontal camera swing to `0.68x` (`computeCinematicCameraVector(..., isPortrait=True)`) to ensure characters remain centered.
- **Karaoke Subtitle Clearance**: Camera optical focus is clamped to `Y = 40%` (safe maximum `48%`), reserving the bottom 18% of the frame exclusively for dynamic captions.
- **Reframe Mode**: Master 16:9 full-bleed illustrations can be reframed into 9:16 with rounded corners (`borderRadius: 24`), drop shadows, and top hook title typography (`editorial` mode).
