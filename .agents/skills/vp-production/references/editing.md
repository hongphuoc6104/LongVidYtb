# Timing, captions, dual-zone pacing and output

Build timelines from real language-track WAVs and acoustic `word_timestamps` (`_extract_word_timestamps_acoustic()`). Each cut/hold/diagram/reveal needs a semantic purpose; never use mechanical modulo cycling (`% 5` or `% 4`).

Language, aspect ratio, subtitles and track selection are governed by `sys/format_profiles.py` (zero fixed duration constraints — duration is dynamic, determined by narrative depth and measured WAV narration):
- **`long_16x9` (`1920x1080`):** Landscape explainers for YouTube, `subtitles: false` by default (`max_line_chars: 42`, `max_cue_chars: 84` for sidecar `.srt`), per-channel studio voice `VietNarrator_<channel_id>` (`sys/assets/voices/ch_<id>/`, `speed: 1.0`). High-density `240–350` multi-image journey across 4 pacing modes (Rapid `1.2–2.0s`, Normal `2.2–3.2s`, Slow `3.5–4.8s`, Hold `5.0–6.5s`), static Lanczos frame lock (`scale=1920:1080:flags=lanczos,crop=1920:1080:exact=1`, zero `zoompan`, ERR-20261109-01), optical `xfade=transition=fade` (`0.24s`) only, bottom-right logo `W-w-36:H-h-36`, and 8–12 `FFMETADATA1` chapters.
- **`short_9x16` (`1080x1920`):** Standalone scenes for TikTok/Shorts Spin-offs, `subtitles: true` (kinetic 1-word Red `#FF3B30` / Yellow `#FFE600` `.ass` subtitles, `18%` bottom clearance), per-channel studio voice `VietNarrator_<channel_id>` (`speed: 1.0`), bottom-right logo `W-w-36:H-h-36`. 100% Full-Chain continuous video (`Omni 1.2 Flash` from 11–15 keyframes). Never raw-cut middle chapters of a `16:9` video to post on TikTok without standalone restructuring.

Use supported camera/transition effects (`cut`, `hold`, `fade`, `xfade`, `zoom_in`, `zoom_out`, `punch_in`, `pan_left`, `pan_right`) according to [render-capabilities](../../../../sys/docs/render-capabilities.md); preserve diagram labels and visual action under crop/zoom.

Encode natively on remote Colab Tesla T4 GPU (`-c:v h264_nvenc -preset p4 -b:v 6M`, `loudnorm=I=-11.0:TP=-1.0`). Long videos encode in parallel across 3 workers on `/dev/shm` RAM disk, followed by `<1.0s` lossless `stream-copy` concatenation.

Each visual beat uses a complete full-frame `kind: "scene"` image. For a same-location action change, attach the previous image with `based_on` and specify what to preserve and what to change. Scene cuts and substantial camera changes use independent full-frame images.

Enforce **Dual-Zone Cue-Window Allocation** (`[cue_i.start, cue_{i+1}.start)`):
- Anchor the first visual shot of every spoken cue to `cue_i.start` with `0.00s` drift.
- **Cold open (`0:00–0:12.5`):** Target high visual density (3–5 beats in first 5s) to hook viewers with zero fluff.
- **Body & Payoff Zone (`after 0:15` / `SC03+`):** Pacing adheres strictly to `sys/visual_pacing.py` format profiles (Short average `1.8–3.0s`; Long high-density `240–350` beats average `1.35–6.50s`).
