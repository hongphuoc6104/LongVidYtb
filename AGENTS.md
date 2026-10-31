# Video Pilot Invariants & Governance

## 1. Dual-Format SSOT & Niche Pillar
- **Dual-Format (`sys/format_profiles.py`)**: `long_16x9` (13m Explainer Blueprint ref; dynamic duration via `content_depth_estimate`) & `short_9x16` (`subtitles: true`, `speed: 1.0`, `VietNarrator`). Measured WAV duration.
- **Philosophy (`sys/pillars.py`)**: `ContentPhilosophy` (`cognition` default, `research_guide`); adaptive flow, no forced paradox; T3 `screen_capture` -> ask source. No shallow tips.
- **Directory**: `sys/` (tools), `sys/runs/<job>/` (assets), `video/<job>/` (MP4/SRT). Root clean.

## 2. Technical Ethos & 6 Stations (`./pipeline run`)
- **Standards**: Modular, typed code. No monkey-patches, fake test passes, manual DB edits.
- **Conveyor**: St1 Critique -> St2 AST & `pytest` -> St3 `PLAYBOOK.md` -> St4 `ruff` -> St5 PR (`gh-axi`) -> St6 Green CI.

## 3. Pipelines & Role Separation
- **Production (`vp-production`)**: `vp-research-architect` (Schema 3.0 `brief.json`/`content.json`, Packaging, `build_scenes_from_story_rows`) -> `vp-scriptwriting` (Feynman sentences, cadence, `vn_text_normalizer.py`) -> `vp-full-frame-quality` (`kind: "scene"`, `shot_type`, `based_on`, camera) -> `vp-omni-platform` (`sys/omni_platform.py`) -> Multi-T4 (`ColabPoolDispatcher` / `pilot.py` outline -> dialogue -> audio -> images -> video).
- **Remote GPU (`vp-colab-bridge`)**: Run via `pilot.py` or `sys/colab_bridge/` + `sys/renderer/render.mjs` (no local ffmpeg render).
- **Flow CDP (`vp-flow-cdp`)**: 20 Chrome profiles (`sys/flow_cdp/`), adaptive 1–10 tabs, strict teardown. Valid AI image + `.json` sidecar (no PIL mocks).

## 4. Headless Colab GPU & Multi-T4 Pool (`vp-colab-bridge`)
- **Headless EGL + NVENC**: `chrome-wrapper.sh` (`VP_CHROME_PATH`, `DISABLE_FROM_SURFACE=true`, `gl-egl`), `<Img decoding="sync">`, `videoBitrate: '6M'` (`h264_nvenc`). No `xvfb-run` or `--use-angle=gl`.
- **Multi-T4 Pool**: Parallel TTS/renders via `ColabPoolManager` / `ColabPoolDispatcher` with teardown & `pkill -9`.

## 5. Execution Modes & Bug Discipline
- **Modes**: Auto (E2E), Review (pause at stages), Stop & Handoff (halt preserving assets).
- **Bug Protocol**: Reproduction -> Root Cause -> Fix -> `PLAYBOOK.md` (6 fields, `<= 200` lines; overflow to `.agents/skills/`).

## 6. Quality, Doodle Style, Voice & V2 Pacing/CTA Guards
- **Anti-Flop**: `youtube_title <= 55` chars, Flow CDP `thumbnail_spec` (2–4 uppercase words; zero overlays), relatable hook (no `vi-đê-ô`), simple declarative sentences, constructive guidance (`script_diversity_linter.py`, `script_cadence_checker.py`).
- **V2 CTA & Phễu (`cta_tone_linter.py`)**: Short binds `parent_long_id`. 1 close CTA (<=24 syl) + 1 bridge (<=22 syl) in final 15% runtime (never opening 3s hook); long <=1 mid_cta at 35-45%. Banned: `đừng quên like`, `nhấn chuông`, `like share`, `subscribe`...
- **V2 Pacing (`sys/visual_pacing.py`)**: Hold: `fast` (0.9-1.8s / 2.0-4.0s), `normal` (2.0-3.5s / 4.0-7.0s), `slow` (3.5-5.5s / 7.0-10.0s, >=1 key insight), `hold` (1.5-3.0s / 5.0-20.0s endcard). Short avg hold 2.0-3.0s; long avg 5.0-7.0s (70-90 beats). Max 3 consecutive beats of same tempo (fast <=5).
- **Hand-Lettering**: Upper third, <=10% frame height, 1-4 uppercase VN words in Flow image (zero overlays), <=35% beats, no subtitle collision (bottom 400px).
- **Voice (`VietNarrator` `1.0x`, `-11.0 LUFS` / `-1.0 dBTP`)**: Strip hyphens before OmniVoice BPE, strip bleed bursts, keep nasal codas, retry stalls (`batch_size=1`), listen WAV.
- **2D Doodle (`1.7.0` `handdrawn_2d_explainer`)**: Lock to `Nguệch Ngoạc / Vẽ Vời` (`sys/visual_style.py`: wobbly `#000000` marker, flat hex `#F8F0DC`, `#F2B88B`, `#93A88C`, `#CBE0E0`, `#2E4361`, `#FFFFFF`, bald circle stickman, `#3B82C4` shirt, wire arms, circle hands, 2D); Feynman: 1 stickman + 1 focal metaphor on flat canvas, >=60% negative space; zero room walls, oval shadows, 3/4 isometric, vignette. Verify MP4 via `ffprobe` + frame check.

## 7. Language Standards
- **User**: Concise **Vietnamese**. **Code/Commits/Prompts**: **English** (preserve exact `I`).
