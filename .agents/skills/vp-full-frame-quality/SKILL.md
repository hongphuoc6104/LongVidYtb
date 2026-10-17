---
name: vp-full-frame-quality
description: "Enforce full-frame visual standards, pacing holds, shot types, and setting diversity for full_frame_v1 production."
---

# VP Full-Frame Quality — Visual Standards & Pacing Guards

`vp-full-frame-quality` defines the visual composition, shot grammar, and pacing standards for Video Pilot under the `full_frame_v1` profile. It deprecates manual `(x, y)` coordinate guessing and cutout sticker layers (`layers[]`, `matte_sticker.py`), standardizing all visual production on complete, narrative-bound full-frame scene compositions (`kind: "scene"`).

---

## 1. Core Principles & Deprecation of Cut-Out Layers
- **No Cut-Out Stickers**: Legacy sticker matting (`kind: "sticker"`, `matte_sticker.py`, `layers[]`) is deprecated for new jobs. Every generated visual asset is a complete, full-bleed physical or conceptual composition (`kind: "scene"`).
- **Zero Coordinate Guessing**: Agents never guess arbitrary `(x, y)` sticker coordinates or place floating HTML/SVG callouts over frames. All visual actions, character poses, and focal props are authored directly into the image prompt or integrated organically via Remotion camera vectors.
- **Aspect-Aware Clearance**:
  - Horizontal (`long_16x9`): `caption_clearance: null` (100% full-bleed canvas when burn-in subtitles are disabled).
  - Vertical (`short_9x16`): Bottom 18% reserved for dynamic burn-in subtitles (`max_line_chars = 28`). Camera optical center is clamped to `Y = 40%` (safe maximum `48%`).

---

## 2. Standard Shot Types (`flow_prompts 1.3.0`)
Every visual beat must declare a valid `shot_type`:
1. **`full_scene`**: Integrated physical environment featuring anonymous stick figure(s), furniture, and key props together in the same room. Used for establishing settings, lab experiments, lectures, or emotional moments.
2. **`variation`**: In-place variation attached to an earlier `based_on` scene image. Preserves exact room architecture and facial expression (`Expression lock`), shifting only the declared character pose or held prop.
3. **`macro_prop`**: Optical close-up on a concrete object, tool, book page, or hand action (white cartoon four-finger hands with black outlines).
4. **`white_card`**: Clean, pure white `#FFFFFF` conceptual card with no room or floor scenery. Displays only the isolated paradox diagram, formula, or comparison icon with declared `allowed_text`.
5. **`white_isolated`**: Clean pure white background with a single character or prop integrated cleanly without sticker borders.

---

## 3. Visual Pacing & Duration Holds
- **Cold Open (First 15s)**: Target 8–9 distinct visual beats within the first 12.5s (~0.8s–1.5s per beat, average ~4/5s hold) to maximize initial viewer retention.
- **Body Scene Holds**: Every visual beat hold duration must be strictly between **`0.83s` and `3.80s`** (`OMNI_VISUAL_PACING`). No image may linger static for longer than 3.8s.
- **Optical Crossfade**: In-room variation cuts within the same camera anchor group use a subtle 75ms (2-frame) optical crossfade to prevent jarring pose pops. Standalone cuts to `macro_prop` or `white_card` use clean hard cuts with zero crossfade ghosting.

---

## 4. Deterministic Authoring & Quality Guards (`sys/scripts/visual_quality.py`)
- **Visual Setting Diversity (`check_visual_setting_diversity`)**:
  - `SETTING_MONOTONY_STREAK`: No single physical setting (`study_desk`, `laboratory`, `lecture_hall`, `cafe`) may continue for more than 2 consecutive scenes.
  - `LOW_VISUAL_SETTING_VARIETY`: For scripts with $\ge 10$ scenes, no single setting may account for more than 30% of total scenes.
- **Anti-Manual Repetition (`check_instructional_manual_loop`)**:
  - Prohibits repetitive manual checklist actions (e.g., repeatedly closing textbooks, picking up blank paper, drawing circles on paper) more than 3 times per video.
- **Expression Lock**:
  - Every `based_on` variation beat must declare `"Expression lock: preserve eyebrow tension, mouth shape and facial expression unless change explicitly requests a shift."`
