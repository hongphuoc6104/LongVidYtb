# Video Pilot — Agent Invariants & Governance

## 1. Architecture, Dual-Format SSOT & Niche Pillar
- **Dual-Format Mission (`sys/format_profiles.py`)**: Automate **`long_16x9`** (landscape YouTube explainers, 13m Explainer Blueprint reference) and **`short_9x16`** (standalone scenes, `subtitles: true`, `speed: 1.0` with `VietNarrator` for TikTok/Shorts). Zero fixed duration constraints: duration is dynamic, driven by narrative depth and measured WAV audio.
- **Channel Pillar Lock**: Lock content to **"Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"** across 3-Tier Funnel (`tier_1_broad` Cognitive Biases & Mental Models; `tier_2_mid` Methodological Inquiry & First-Principles; `tier_3_conversion` Deep Intellectual Tooling). Focus on cognitive mechanisms without rigid sample topics. No shallow office tips (Excel, slides).
- **Directory Invariant**: `sys/` (engine/tools), `sys/runs/<job>/` (assets), `video/<job>/` (final MP4/SRT). Keep root clean.

## 2. Technical Ethos & 6-Station Conveyor (`./pipeline run`)
- **Code Standards**: Modular, type-hinted code. No monkey-patches, fake test passes, or manual DB/state edits.
- **Conveyor**: St1 Critique (`critique_review.html`) -> St2 AST Proof & `pytest` -> St3 `PLAYBOOK.md` Sync -> St4 `ruff` Lint -> St5 PR (`gh-axi`) -> St6 Green CI.

## 3. Pipelines & Role Separation (Flash-Agent Simplified)
- **Topic-to-Video Chain (`vp-production`)**: `vp-research-architect` (Schema 3.0 `brief.json`/`content.json`, `human_editorial` dynamic questions, Packaging Contract, VN 60s, `build_scenes_from_story_rows`) -> `vp-scriptwriting` (Truth-Slap Hook `<= 18` syl, Zero Pause in `SC01`, mix 3–8 & 15–24 word sentences; `vn_text_normalizer.py`) -> `vp-full-frame-quality` (`kind: "scene"`, `shot_type` in `full_scene|macro_prop|variation|white_card`, `based_on`, camera) -> `vp-omni-platform` (`sys/omni_platform.py`) -> Multi-T4 Orchestrator (`ColabPoolDispatcher` / `pilot.py` outline -> dialogue -> audio -> images -> video).
- **Remote GPU TTS & Video (`vp-colab-bridge`)**: Execute via `pilot.py` or `sys/colab_bridge/` + `sys/renderer/render.mjs` (no ad-hoc ffmpeg/local render).
- **AI Image Generation (`vp-flow-cdp`)**: Dynamic 20 Chrome profiles pool (`sys/flow_cdp/`) with adaptive sizing (1–10 tabs) and strict lifecycle teardown (open N, close N). Valid AI image + `.json` sidecar required (no PIL mocks).

## 4. Headless Colab GPU & Multi-T4 Pool (`vp-colab-bridge`)
- **Headless EGL + NVENC (Rule 4)**: Run Chromium via `chrome-wrapper.sh` (`VP_CHROME_PATH`, `DISABLE_FROM_SURFACE=true`) with Headless EGL (`10_nvidia.json` + `gl-egl`, fallback `--disable-gpu-rasterization`), 4-layer sync tile locks (`<Img decoding="sync">`), and `videoBitrate: '6M'` (`h264_nvenc`). No `xvfb-run` or `--use-angle=gl`.
- **Multi-T4 Pool**: Dispatch parallel renders across Colab T4 accounts (`ColabPoolManager` / `ColabPoolDispatcher`) with orphan cleanup (`pkill -9`).

## 5. Execution Modes & Bug Discipline
- **Modes**: Auto (E2E without reviewer), Review (pause at outline/dialogue/audio/images/video), Stop & Handoff (halt preserving assets).
- **Bug Protocol**: Reproduction -> Root Cause -> Fix -> `PLAYBOOK.md` (6 fields). Extract to `.agents/skills/` if `PLAYBOOK.md` > 200 lines.

## 6. Quality, Anti-Flop & Verification Guards
- **Fidelity, Packaging & Anti-Flop Gate**: 1 paradox/video (no cramming/clone), `youtube_title <= 55` chars + `thumbnail_spec` (2–4 uppercase words), VN 60s localization, `SC01` hook `<= 18` syl, zero `[pause:...]` (`OPENING_SCENE_PAUSE_FORBIDDEN`), spoken facts `<= 20` syl; pass `script_diversity_linter.py`.
- **Visuals & Verification (`full_frame_v1`)**: Complete `kind: "scene"` images (`caption_clearance: null` on 16:9) with visual counterpoint; no manual `(x, y)` coords, cutout stickers, `layers[]`, or `matte_sticker.py`. Dynamic pacing on narrative beats + measured audio (no clamps). Verify MP4 via `ffprobe`.

## 7. Language Standards
- **User**: Concise **Vietnamese**. **Code/Commits/Prompts**: **English** (preserve exact English spelling including `I`).
