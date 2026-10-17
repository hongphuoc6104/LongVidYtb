# Video Pilot — Agent Invariants & Governance

## 1. Architecture, Dual-Format SSOT & Niche Pillar
- **Dual-Format Mission (`sys/format_profiles.py`)**: Automate **`long_16x9`** (11–13m, 8ch/48sc for YouTube per 13m Explainer Blueprint, or 5–8m `full_frame_v1` explainers) and **`short_9x16`** (45–60s, 5 standalone scenes `SC01..SC05`, `subtitles: true`, `speed: 1.26` for TikTok/Shorts Spin-offs). Never cut middle chapters (`CH02..CH08`) of 16:9 for TikTok.
- **Channel Pillar Lock**: Lock content to **"Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật"** across 3-Tier Funnel (`tier_1_broad` Illusion of Competence, `tier_2_mid` Q1 Process & 120s Defense Psychology, `tier_3_conversion` AI for Deep Research / Gap Matrix). No office tips (Excel, slides, Na's English).
- **Directory Invariant**: `sys/` (engine/tools), `sys/runs/<job>/` (assets), `video/<job>/` (final MP4/SRT). Keep root clean.

## 2. Technical Ethos & 6-Station Conveyor (`./pipeline run`)
- **Code Standards**: Modular, type-hinted code only. No monkey-patches, fake test passes, or manual DB/state edits.
- **Conveyor**: St1 Critique (`critique_review.html`) -> St2 AST Proof & `pytest` -> St3 `PLAYBOOK.md` Sync -> St4 `ruff` Lint -> St5 PR (`gh-axi`) -> St6 Green CI.

## 3. Pipelines & Role Separation (Flash-Agent Simplified)
- **Topic-to-Video Chain (`vp-production`)**: `vp-research-architect` (Schema 3.0 `brief.json`/`content.json`, Packaging Contract, VN 60s Localization, `build_scenes_from_story_rows`) -> `vp-scriptwriting` (Truth-Slap Hook `<= 18` syl, Zero Pause in `SC01`, mix 3–8 & 15–24 word sentences; `vn_text_normalizer.py` & `chunks_with_gaps`) -> `vp-full-frame-quality` (`kind: "scene"`, `shot_type` in `full_scene|macro_prop|variation|white_card`, `based_on`, `narrative_phase`, camera assignment) -> `vp-omni-platform` (`sys/omni_platform.py`) -> Multi-T4 Orchestrator (`ColabPoolDispatcher` / `pilot.py` outline -> dialogue -> audio -> images -> video).
- **Remote GPU TTS & Video (`vp-colab-bridge`)**: Execute via `pilot.py` or `sys/colab_bridge/` + `sys/renderer/render.mjs` (no ad-hoc ffmpeg/local render).
- **AI Image Generation (`vp-flow-cdp`)**: 3 Chrome profiles pool (`sys/flow_cdp/`) with patch failover. Valid AI image + `.json` sidecar required (no PIL mocks).

## 4. Headless Colab GPU & Multi-T4 Pool (`vp-colab-bridge`)
- **Headless EGL + NVENC (Rule 4)**: Run Chromium via `chrome-wrapper.sh` (`VP_CHROME_PATH`, `DISABLE_FROM_SURFACE=true`) with NVIDIA Headless EGL (`10_nvidia.json` + `gl-egl`, fallback `--disable-gpu-rasterization`), 4-layer sync tile locks (`<Img decoding="sync">`), and `videoBitrate: '6M'` (`h264_nvenc`). No `xvfb-run` or `--use-angle=gl`.
- **Multi-T4 Pool**: Dispatch multi-chapter renders in parallel across Colab T4 accounts (`ColabPoolManager` / `ColabPoolDispatcher`) with orphan cleanup (`pkill -9`).

## 5. Execution Modes & Bug Discipline
- **Modes**: Auto (E2E without reviewer), Review (pause at outline/dialogue/audio/images/video), Stop & Handoff (halt preserving assets).
- **Bug Protocol**: Reproduction -> Root Cause -> Fix -> `PLAYBOOK.md` (6 mandatory fields). Extract to `.agents/skills/` if `PLAYBOOK.md` > 200 lines.

## 6. Quality, Anti-Flop & Verification Guards
- **Fidelity, Packaging & Anti-Flop Gate**: 1 core paradox/video (no Frankenstein cramming or clone topics), `youtube_title <= 55` chars + `thumbnail_spec` (2–4 uppercase words), VN 60s localization, `SC01` hook `<= 18` syl, zero `[pause:...]` (`OPENING_SCENE_PAUSE_FORBIDDEN`), spoken facts `<= 20` syl; pass `script_diversity_linter.py`.
- **Visuals & Verification (`full_frame_v1`)**: Complete `kind: "scene"` images (`caption_clearance: null` on 16:9) with visual counterpoint; no manual `(x, y)` coordinates, cutout stickers, `layers[]`, or `matte_sticker.py`. Cold open: 6–10 images/12.5s (3–5/5s); body holds `0.83s–3.80s`. Verify MP4 with `ffprobe`.

## 7. Language Standards
- **User**: Concise **Vietnamese**. **Code/Commits/Prompts**: **English** (preserve exact English spelling including `I`).
