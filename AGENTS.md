# Video Pilot — Agent Invariants & Governance

## 1. Architecture, Dual-Format SSOT & Niche Pillar
- **Dual-Format Mission (`sys/format_profiles.py`)**: Automate both **`long_16x9`** (11–13m, 8 chapters / 48 scenes for YouTube per 13m Explainer Blueprint) and **`short_9x16`** (45–60s, 5 standalone scenes `SC01..SC05`, `subtitles: true`, `speed: 1.26` for TikTok/Shorts & Spin-offs). Never raw-cut middle chapters (`CH02..CH08`) of a 16:9 video for TikTok.
- **Channel Pillar Lock**: Lock content to **"Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật"** across the 3-Tier Funnel (`tier_1_broad` Illusion of Competence, `tier_2_mid` Q1 Process & 120s Defense Psychology, `tier_3_conversion` AI for Deep Research / Gap Matrix). Prohibit office tips (Excel, slides, Na's English).
- **Directory Invariant**: `sys/` (engine/tools), `sys/runs/<job>/` (assets), `video/<job>/` (final MP4/SRT). Keep root clean.

## 2. Technical Ethos & 6-Station Conveyor (`./pipeline run`)
- **Code Standards**: Modular, type-hinted code only. No monkey-patches, fake test passes, or manual DB/state edits.
- **Conveyor**: St1 Critique (`critique_review.html` / `lavish-axi`) -> St2 AST Proof & `pytest` -> St3 `PLAYBOOK.md` Sync -> St4 `ruff` Lint -> St5 PR (`treehouse` / `gh-axi`) -> St6 Green CI.

## 3. Pipelines & Role Separation
- **Topic-to-Video Chain (`vp-production`)**: `vp-research-architect` (Schema 3.0 `brief.json`/`content.json`, Packaging Contract, VN 60s Localization, 8-chapter 48-scene `long_16x9` + 5-scene `short_9x16` Spin-offs) -> `vp-scriptwriting` (Truth-Slap Hook `<= 18` syl, Zero Pause in `SC01`, `vn_text_normalizer.py` + `script_cadence_checker.py`) -> full-frame visual beat planning (`kind: "scene"`, semantic anchors, `based_on` for in-place variations) -> Multi-T4 Orchestrator (`ColabPoolDispatcher` / `pilot.py` outline -> dialogue -> audio -> images -> video).
- **Remote GPU TTS & Video (`vp-colab-bridge`)**: Execute via `pilot.py` or `sys/colab_bridge/` + `sys/renderer/render.mjs` (no ad-hoc ffmpeg/local render).
- **AI Image Generation (`vp-flow-cdp`)**: 3 Chrome profiles pool (`sys/flow_cdp/`) with patch failover. Valid AI image + `.json` sidecar required (no PIL mocks).

## 4. Headless Colab GPU & Multi-T4 Pool (`vp-colab-bridge`)
- **Headless EGL + NVENC (Rule 4)**: Run Chromium via `chrome-wrapper.sh` (`VP_CHROME_PATH`, `DISABLE_FROM_SURFACE=true`) with NVIDIA Headless EGL (`10_nvidia.json` + `gl-egl`, fallback `--disable-gpu-rasterization`), 4-layer sync tile locks (`<Img decoding="sync">`), and `videoBitrate: '6M'` (`h264_nvenc`). Prohibit `xvfb-run` and `--use-angle=gl`.
- **Multi-T4 Pool**: Dispatch multi-chapter renders in parallel across Colab T4 accounts (`ColabPoolManager` / `ColabPoolDispatcher`) with orphan cleanup (`pkill -9`).

## 5. Execution Modes & Bug Discipline
- **Modes**: Auto (E2E without reviewer), Review (pause at outline/dialogue/audio/images/video), Stop & Handoff (halt preserving assets).
- **Bug Protocol**: Reproduction -> Root Cause -> Fix -> `PLAYBOOK.md` (6 mandatory fields). Extract to `.agents/skills/` if `PLAYBOOK.md` > 200 lines.

## 6. Quality & Verification Guards
- **Fidelity, Packaging & Direct Pacing**: Enforce `youtube_title <= 55` chars + `thumbnail_spec` (2–4 uppercase words), VN 60s localization (defer Sumer/Edubba/Kalahari to Ch3+), `SC01` hook `<= 18` syl with zero `[pause:...]` (`OPENING_SCENE_PAUSE_FORBIDDEN`), 4.2–4.4 syl/s opening pace, spoken facts `<= 20` syl, forward chronology; pass `script_diversity_linter.py`.
- **Visuals & Verification**: Use complete `kind: "scene"` images with narration-anchored beats; use `based_on` + `preserve`/`change` for in-place variations. Cold open target: 8–9 images/12.5s (~4/5s); body holds `0.83s–3.80s`. No background/sticker assets, layers, or `matte_sticker.py`. Verify MP4 with `ffprobe`.

## 7. Language Standards
- **User**: Concise, natural **Vietnamese**. **Code/Commits/Prompts**: **English** (preserve exact English spelling including `I`).
