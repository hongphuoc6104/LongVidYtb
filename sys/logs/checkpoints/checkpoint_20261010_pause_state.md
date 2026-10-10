# Video Pilot — State Checkpoint & Context Handover
**Timestamp**: 2026-10-10 12:25:00 +07:00
**Trigger**: User requested immediate pause, context checkpointing, and 4-part roadmap reporting.

---

## 1. Current System & Assets State (Where We Stopped)

### 1.1 Running Background Processes
- All subagents have been terminated via `manage_subagents(Action='kill_all')`.
- Zero active background tasks currently running.

### 1.2 Render Outputs Inventory (`video/ancient-humans-day-ch{1..6}-16x9/`)
All 6 chapters were rendered on **Colab Tesla T4 GPU** (`video-pilot-tts`), with subtitles turned off (`subtitles: false` and `DISABLE_SUBTITLES: true`):
- **Ch1**: `ancient-humans-day-ch1-16x9_r1_final.mp4` | 1920x1080 @ 30fps | H.264/AAC | 64.32s | 18.3 MB | 34 images
- **Ch2**: `ancient-humans-day-ch2-16x9_r1_final.mp4` | 1920x1080 @ 30fps | H.264/AAC | 94.95s | 21.0 MB | 37 new pastel images
- **Ch3**: `ancient-humans-day-ch3-16x9_r1_final.mp4` | 1920x1080 @ 30fps | H.264/AAC | 81.86s | 17.8 MB | 28 images
- **Ch4**: `ancient-humans-day-ch4-16x9_r1_final.mp4` | 1920x1080 @ 30fps | H.264/AAC | 72.19s | 14.0 MB | 20 images
- **Ch5**: `ancient-humans-day-ch5-16x9_r1_final.mp4` | 1920x1080 @ 30fps | H.264/AAC | 98.03s | 20.7 MB | 34 images
- **Ch6**: `ancient-humans-day-ch6-16x9_r1_final.mp4` | 1920x1080 @ 30fps | H.264/AAC | 83.88s | 21.2 MB | 30 images

### 1.3 Images Asset Status (`sys/exports/ancient_humans_flowkit_bundle/generated_images/`)
- **Ch1**: 34 / 34 images complete.
- **Ch2**: 37 / 37 images complete (full-color pastel set).
- **Ch3**: 28 / 28 images complete.
- **Ch4**: 20 / 20 images complete.
- **Ch5**: 34 / 34 images complete.
- **Ch6**: 30 / 30 images complete.
- **Ch7**: 1 / 36 images complete (35 remaining).
- **Ch8**: 0 / 21 images complete (21 remaining).

---

## 2. Key Technical Findings & Corrective Actions

### 2.1 The "Bottom 20% White Gap" Root Cause
- **Discovery**: In `manifest_245_shots.json`, 206/245 prompts contained `"Keep the bottom 20% of the frame plain and unobstructed for subtitles."`.
- **Result**: The AI model (Google Flow Nano Banana) intentionally pushed drawings upward and left a blank 20% white space at the bottom for captions. When captions were turned off, this gap became visibly noticeable.
- **Action Taken**: Completely stripped `"Keep the bottom 20% of the frame plain and unobstructed for subtitles."` from `manifest_245_shots.json` and prompt build tools. Future image generation prompts will let AI render naturally across the full 16:9 canvas.

### 2.2 Subagent Path Misdirection Fix
- **Discovery**: A previously spawned subagent wrote ad-hoc scripts (`sys/scratch/render_ch2_colab.py`, `render_ch6_colab.py`) pointing to `sys/scratch/reference_49_Ph2q6uIM/` (which holds low-res 720p sample frames from the YouTube reference video), bypassing the AI-generated images.
- **Action Taken**: Killed the subagent, deleted the rogue scripts, and ensured all builds strictly resolve images from `sys/exports/ancient_humans_flowkit_bundle/generated_images/ch{num}/` via `sys/exports/ancient_humans_flowkit_bundle/scripts/render_all_on_colab.py`.

### 2.3 Smart Auto-Reframe (Temporary Mechanism)
- Added temporary Smart Auto-Reframe logic in `sys/renderer/index.tsx`:
  - When `isAutoReframe` is enabled (via `VP_SMART_AUTOREFRAME='true'` env var passed through `render_all_on_colab.py --auto-reframe`):
    - `scale = 1.14` (~14% zoom).
    - `translateY = +6%` (shifts image down so table rests on bottom edge).
  - Main pipeline remains untouched by default (`VP_SMART_AUTOREFRAME` defaults to `false`).

---

## 3. Road Map (Past, Present, Future & Ultimate Goal)

### 3.1 Completed Work
1. Purged old black-and-white render outputs and staging caches for Ch1 and Ch2.
2. Configured captions off (`subtitles: false` and `DISABLE_SUBTITLES: true`).
3. Rendered all 6 chapters (Ch1-Ch6) on Colab Tesla T4 GPU with full ffprobe verification.
4. Conducted deep pacing audit revealing long static beats (>2.5s and up to 6-12s in Ch3, Ch4, Ch5).
5. Identified prompt rule root cause for bottom gap and purged the rule from all manifest/prompt files.
6. Implemented isolated `--auto-reframe` option in `render_all_on_colab.py` for review tests.

### 3.2 In-Progress Work (Paused at User Request)
1. Preparing temporary re-render test for Ch6 (and Ch2) with `--auto-reframe` using actual AI generated images to present to the user.
2. Developing formal `/plan` for **Option B** (dividing long scenes >3s into 1.5s–2.0s sub-beats and generating new close-up/expression images using `vp-flow-cdp` across 3 Chrome profiles).

### 3.3 Upcoming Work
1. Execute the isolated `--auto-reframe` test render on Colab GPU T4 for Ch6/Ch2 to evaluate visual composition.
2. Finalize and review the Option B implementation plan:
   - Identify candidate shots for sub-beat breakdown (13 shots in Ch3, 13 shots in Ch4).
   - Author specific visual beat prompts (close-up expressions, reaction shots) without the bottom 20% restriction.
   - Dispatch generation across the 3 Chrome profiles via `vp-flow-cdp` with patch partitioning (2-4 shots/patch).
3. Update scene timelines in templates with the new sub-beats and re-render.
4. Complete remaining shots for Chapter 7 (35 shots) and Chapter 8 (21 shots) using the corrected prompt format.
5. Concatenate all 8 chapters into the final 11-minute full video.

### 3.4 Ultimate Objective
Produce a complete, broadcast-quality 11-minute explainer video ("A Day in the Life of Ancient Humans") in 16:9 (`1920x1080` @ 30fps):
- Seamless visual composition with no empty bottom padding.
- Engaging, fast-paced rhythm (beat changes every 1.5s - 2.0s) avoiding static stalls.
- 100% unified warm pastel stick-figure visual identity.
- Frame-accurate sync with Vietnamese narration audio.
