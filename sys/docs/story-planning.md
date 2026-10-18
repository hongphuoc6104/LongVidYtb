# Script, Storyboard and Planning Specs (`full_frame_v1`)

## 1. Scope & Workflow
- **Contract source:** Read job contract/profile (`sys/format_profiles.py`) and references: [script](../../.agents/skills/vp-production/references/script.md), [narration](../../.agents/skills/vp-production/references/narration-style.md), [visuals](../../.agents/skills/vp-production/references/visuals.md), and [full-frame quality](../../.agents/skills/vp-full-frame-quality/SKILL.md).
- **Workflow modes:** Review mode stops at `outline` and `dialogue` checkpoints; Auto mode proceeds without human review.
- **Scene counts & Flash-Friendly Authoring:** Dynamic scene counts based on causal progression (`local experience -> experimental evidence -> mechanism/metaphor -> practical return`). Prefer authoring via `(sentence, "shot_type|visual_action")` pairs (`build_scenes_from_story_rows` in `sys/tools/research_story_architect.py`) so code automatically computes exact anchors, durations, and `based_on` continuity without manual math or coordinate guessing.

## 2. Script & Narration
- **Language:** Write primary narration in natural, conversational **Vietnamese** (`vi`) for the channel's core audience (with optional `en` track only when `outputs` explicitly requests English).
- **Natural Cadence (No Rule-Stuffing):** Alternate short punchy sentences (`3–8` words) with longer explanatory sentences (`15–24` words). Never insert unnatural commas between subject and verb just to game clause counters.
- **Automated TTS Normalization:** `sys/remote_audio.py`, `sys/adapters.py`, and `sys/colab_bridge/worker.py` automatically strip `[pause:...]` tags into exact acoustic gaps and transliterate numbers/loanwords via `vn_text_normalizer.py` before synthesis while preserving clean caption text.
- **Revisions:** Narration edits must go through versioned rejections/new revisions (`reject` / new revision); never modify snapshots in-place.

## 3. Visuals & Storyboard (`full_frame_v1`)
- **Zero Layering / Zero Coordinate Guessing:** All beats use complete `kind: "scene"` full-frame images (`full_scene`, `macro_prop`, `variation`, `white_card`, `white_isolated`) with `caption_clearance: null` on landscape `16:9`. Never generate cutout stickers, `layers[]`, or guess manual `x, y, w` coordinates.
- **Visual Cast (Anonymous Stick Figures):**
  - Prompt registry `1.4.0`: All people are **anonymous stick figures** (large round white head with fine-to-medium charcoal outline, solid-black dot/oval eyes, stick limbs, simplified four-finger cartoon hands, exactly one torso) integrated physically into the environment.
  - **No main character, recurring protagonist, or presenter inside scenes.**
- **Continuity (`based_on`):** Within the same room/setting, `apply_room_continuity()` automatically links returning full-scene shots via `based_on` and enforces an `Expression lock` in `preserve`.

## 4. Audio, Subtitles & Timing
- **Timing:** Drive timeline cuts using measured WAV audio length and acoustic `word_timestamps` (`_extract_word_timestamps_acoustic()`).
- **Sound Design:** `full_frame_v1` and `omni_platform` jobs automatically include sidechain-ducked BGM (`ambient_focus_loop.wav`) and Foley micro-SFX on Colab.
- **Camera Effects:** `story_plan.timeline()` automatically resolves `cut`/`fade`/`auto` into non-repeating semantic camera movements (`zoom_in`, `zoom_out`, `punch_in`, `pan_left`, `pan_right`, `hold`) according to [render-capabilities](render-capabilities.md).

## 5. Execution Commands
- **Submit outline/dialogue:**
  `python3 sys/pilot.py author <JOB> outline|dialogue --data <PATH> --source <TEXT>`
- **Run/Resume pipeline:**
  `python3 sys/pilot.py run <JOB>` or `python3 sys/pilot.py resume <JOB>`

