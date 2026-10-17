# Timing, captions, dual-zone pacing and output

Build timelines from real language-track WAVs and acoustic `word_timestamps` (`_extract_word_timestamps_acoustic()`). Each cut/hold/diagram/reveal needs a semantic purpose; never use mechanical modulo cycling (`% 5` or `% 4`).

Language, aspect ratio, subtitles and track selection are governed by `sys/format_profiles.py`:
- **`long_16x9` (`1920x1080`):** 8 chapters / 48 scenes (11–13m) for YouTube, `subtitles: false` by default (`max_line_chars: 42`, `max_cue_chars: 84` for SRT), `voice: "VietNarrator"`, `speed: 1.0`.
- **`short_9x16` (`1080x1920`):** 5 standalone scenes (`SC01..SC05`, 45–60s) for TikTok/Shorts Spin-offs, `subtitles: true` (`max_line_chars: 28`, `max_cue_chars: 54`, `18%` bottom clearance), `voice: "VietNarrator"`, `speed: 1.0`. Never raw-cut middle chapters (`CH02..CH08`) of a `16:9` video to post on TikTok.

Use supported camera/transition effects (`cut`, `hold`, `fade`, `slide_left`, `zoom_in`, `zoom_out`, `punch_in`, `pan_left`, `pan_right`, `shake`) according to render-capabilities.md; preserve diagram labels and visual action under crop/zoom.

Prepare, render and encode on Colab T4 (NVIDIA Headless EGL `gl-egl` + `h264_nvenc` `videoBitrate: '6M'`). Inspect actual playback when available without treating that craft activity as a machine-review gate.

Each visual beat uses a complete full-frame `kind: "scene"` image. For a same-location action change, attach the previous image with `based_on` and specify what to preserve and what to change. Scene cuts and substantial camera changes use independent full-frame images.

For multi-cue scenes and multi-chapter explainers, enforce **Dual-Zone Cue-Window Allocation** (`[cue_i.start, cue_{i+1}.start)`):
- Anchor the first visual shot of every spoken cue to `cue_i.start` with `0.00s` drift.
- **Cold open (`0:00–0:12.5`):** When the narration supports it, target 8–9 full-frame cuts (about 4 in the first 5 seconds). Anchor each image to the spoken object or action; review timing against the actual WAV rather than enforcing a fixed image quota.
- **Body & Payoff Zone (`after 0:15` / `SC03+`):** Subdivide cue windows longer than `3.80s` into semantic sub-beats so image holds stay within **`0.83s–3.80s`** (`<= 4.0s` hard ceiling), and verify rendered freshness (`mp4_mtime >= template_mtime`).
