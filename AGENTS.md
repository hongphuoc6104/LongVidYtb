# Video Pilot — Agent Invariants & Governance

## 1. Architecture, Dual-Format SSOT & Niche Pillar
- **Dual-Format (`sys/format_profiles.py`)**: Automate **`long_16x9`** (13m Explainer Blueprint reference) and **`short_9x16`** (`subtitles: true`, `speed: 1.0`, `VietNarrator`). Dynamic duration driven by narrative depth and measured WAV.
- **Channel Pillar**: Lock to **"Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"** across 3-Tier Funnel (`tier_1_broad` Biases/Mental Models; `tier_2_mid` First-Principles; `tier_3_conversion` Deep Tooling). No shallow office tips.
- **Directory**: `sys/` (engine/tools), `sys/runs/<job>/` (assets), `video/<job>/` (final MP4/SRT). Keep root clean.

## 2. Technical Ethos & 6-Station Conveyor (`./pipeline run`)
- **Standards**: Modular, type-hinted code. No monkey-patches, fake test passes, or manual DB/state edits.
- **Conveyor**: St1 Critique (`critique_review.html`) -> St2 AST & `pytest` -> St3 `PLAYBOOK.md` -> St4 `ruff` -> St5 PR (`gh-axi`) -> St6 Green CI.

## 3. Pipelines & Role Separation
- **Topic-to-Video (`vp-production`)**: `vp-research-architect` (Schema 3.0 `brief.json`/`content.json`, `human_editorial`, Packaging, VN 60s, `build_scenes_from_story_rows`) -> `vp-scriptwriting` (Hook `<= 18` syl, Zero Pause in `SC01`, mix 3–8 & 15–24 word sentences; `vn_text_normalizer.py`) -> `vp-full-frame-quality` (`kind: "scene"`, `shot_type`, `based_on`, camera) -> `vp-omni-platform` (`sys/omni_platform.py`) -> Multi-T4 (`ColabPoolDispatcher` / `pilot.py` outline -> dialogue -> audio -> images -> video).
- **Remote GPU (`vp-colab-bridge`)**: Execute via `pilot.py` or `sys/colab_bridge/` + `sys/renderer/render.mjs` (no local ffmpeg render).
- **Flow CDP (`vp-flow-cdp`)**: 20 Chrome profiles (`sys/flow_cdp/`), adaptive 1–10 tabs, strict teardown. Valid AI image + `.json` sidecar (no PIL mocks).

## 4. Headless Colab GPU & Multi-T4 Pool (`vp-colab-bridge`)
- **Headless EGL + NVENC**: `chrome-wrapper.sh` (`VP_CHROME_PATH`, `DISABLE_FROM_SURFACE=true`, `10_nvidia.json` + `gl-egl`, fallback `--disable-gpu-rasterization`), `<Img decoding="sync">`, `videoBitrate: '6M'` (`h264_nvenc`). No `xvfb-run` or `--use-angle=gl`.
- **Multi-T4 Pool**: Dispatch parallel TTS/renders via `ColabPoolManager` / `ColabPoolDispatcher` with post-job teardown and `pkill -9` cleanup.

## 5. Execution Modes & Bug Discipline
- **Modes**: Auto (E2E without reviewer), Review (pause at outline/dialogue/audio/images/video), Stop & Handoff (halt preserving assets).
- **Bug Protocol**: Reproduction -> Root Cause -> Fix -> `PLAYBOOK.md` (6 fields, `<= 200` lines; archive overflow to `.agents/skills/`).

## 6. Quality, Doodle Style & Voice Guards
- **Grounded Script & Anti-Flop**: 1 paradox/video, `youtube_title <= 55` chars + `thumbnail_spec` (2–4 uppercase words), VN 60s lived-reality slice-of-life + plain-spoken paradox reveal in `SC01–SC02` (no clichés; prefer pure VN words over loanwords like `vi-đê-ô`), `SC01` hook `<= 18` syl, zero `[pause:...]` in `SC01`, spoken facts `<= 20` syl; pass `script_diversity_linter.py`.
- **Voice & Prosody (`VietNarrator` `1.0x`, `-11.0 LUFS` / `-1.0 dBTP`)**: Strip inter-letter hyphens before `OmniVoice` BPE, strip leading prompt-bleed bursts, preserve soft nasal codas, auto-retry acoustic stalls (`batch_size=1`), and verify WAV by direct listening.
- **2D Indie Doodle (`full_frame_v1` / `1.7.0` `handdrawn_2d_explainer`)**: Lock to `Nguệch Ngoạc / Vẽ Vời` (`sys/visual_style.py`): wobbly `#000000` marker contours, flat MS-Paint hex fills (`#F8F0DC`, `#F2B88B`, `#93A88C`, `#CBE0E0`, `#2E4361`, `#FFFFFF`), white bald circle-head stickman (`#3B82C4` shirt, wire arms, white circle hands), orthographic 2D; no oval shadows, 3/4 isometric, rounded AI icons, `layers[]`, or dark vignette. Verify MP4 via `ffprobe` + frame check.

## 7. Language Standards
- **User**: Concise **Vietnamese**. **Code/Commits/Prompts**: **English** (preserve exact `I`).
