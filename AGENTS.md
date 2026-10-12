# Video Pilot — Agent Invariants & Governance

## 1. Architecture & Layout (SSOT)
- **Mission**: Automate short (`9:16`) and long-form (`16:9`) explainer videos per brief specs (`sys/format_profiles.py`).
- **Directory Invariant**: `sys/` (engine/tools), `sys/runs/<job>/` (assets), `video/<job>/` (final MP4/SRT). Keep root clean.

## 2. Technical Ethos & 6-Station Conveyor (`./pipeline run`)
- **Code Standards**: Modular, type-hinted code only. No monkey-patches, fake test passes, or manual DB/state edits.
- **Conveyor**: St1 Critique (`critique_review.html` / `lavish-axi`) -> St2 AST Proof & `pytest` -> St3 `PLAYBOOK.md` Sync -> St4 `ruff` Lint -> St5 PR (`treehouse` / `gh-axi`) -> St6 Green CI.

## 3. Pipelines & Role Separation
- **Topic-to-Video Chain (`vp-production`)**: `vp-research-architect` (Schema 3.0 `brief.json`/`content.json`) -> `vp-scriptwriting` (`vn_text_normalizer.py` + `script_cadence_checker.py`) -> `vp-layered-motion` (`background` + `sticker` layers) -> `pilot.py` Engine 4 (`outline -> dialogue -> audio -> images -> video`; vocab jobs start via `vocab/bank.py start`).
- **Remote GPU TTS & Video (`vp-colab-bridge`)**: Execute via `pilot.py` or `sys/colab_bridge/` + `sys/renderer/render.mjs` (no ad-hoc ffmpeg/local render).
- **AI Image Generation (`vp-flow-cdp`)**: 3 Chrome profiles pool (`sys/flow_cdp/`) with patch failover. Valid AI image + `.json` sidecar required (never draw mocks with PIL).

## 4. Headless Colab GPU & Multi-T4 Pool (`vp-colab-bridge`)
- **Headless EGL + NVENC (Rule 4)**: Run Chromium via `chrome-wrapper.sh` (`VP_CHROME_PATH`, `DISABLE_FROM_SURFACE=true`) with NVIDIA Headless EGL (`10_nvidia.json` + `gl-egl`, fallback `--disable-gpu-rasterization`), 4-layer sync tile locks (`<Img decoding="sync">`), and `videoBitrate: '6M'` (`h264_nvenc`). Strictly prohibit `xvfb-run` and `--use-angle=gl`.
- **Multi-T4 Pool**: Dispatch multi-chapter renders in parallel across Colab T4 accounts (`ColabPoolManager` / `ColabPoolDispatcher`) with orphan cleanup (`pkill -9`).

## 5. Execution Modes & Bug Discipline
- **Modes**: Auto (E2E without reviewer), Review (pause at outline/dialogue/audio/images/video), Stop & Handoff (halt immediately preserving assets).
- **Bug Protocol**: Reproduction -> Root Cause -> Fix -> `PLAYBOOK.md` (6 mandatory fields). Extract to `.agents/skills/` if `PLAYBOOK.md` > 200 lines.

## 6. Quality & Verification Guards
- **Fidelity & Direct Pacing**: Split into short scenes (`1-2` concise sentences/scene), go straight to the point (zero greetings/fillers, zero `Prof. X at Univ. Y` name-drops in narration — keep citations in `brief.json` only), spoken facts `<= 20` syllables, forward chronology, and `sys/prompt_templates.py`; pass `script_diversity_linter.py`.
- **Visuals & Verification**: Anonymous stick-figures only, Rule-of-Thirds stickers, semantic camera motion (no `% 5` cycling). Verify outputs via `ffprobe` (file existence != valid content).

## 7. Language Standards
- **User**: Concise, natural **Vietnamese**. **Code/Commits/Prompts**: **English** (preserve exact English spelling including `I`).
