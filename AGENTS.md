# Video Pilot Invariants & Governance

## 1. Dual-Format SSOT & Niche Pillar
- **Dual-Format (`sys/format_profiles.py`)**: `long_16x9` (13m Explainer Blueprint ref; dynamic duration via `content_depth_estimate`) & `short_9x16` (`subtitles: true`, `speed: 1.0`, `VietNarrator`). Measured WAV duration.
- **Philosophy (`sys/pillars.py`)**: `ContentPhilosophy` (`cognition` default); adaptive flow, no forced paradox; T3 `screen_capture` -> ask source. No shallow tips.
- **Directory**: `sys/` (tools), `sys/runs/<job>/` (assets), `video/<job>/` (MP4/SRT). Root clean.

## 2. Technical Ethos & 6 Stations (`./pipeline run`)
- **Standards**: Modular, typed code. No monkey-patches, fake test passes, manual DB edits.
- **Conveyor**: St1 Critique -> St2 AST & `pytest` -> St3 `PLAYBOOK.md` -> St4 `ruff` -> St5 PR (`gh-axi`) -> St6 Green CI.

## 3. Pipelines & Role Separation
- **Production (`vp-production`)**: Priority: P1 `full_chain` (`Omni 1.1 Flash`); P2 `images_only`. Chain: `vp-research-architect` -> `vp-scriptwriting` -> `vp-full-frame-quality` -> `vp-omni-platform` -> Multi-T4 (`ColabPoolDispatcher` / `pilot.py` outline -> dialogue -> audio -> images -> video).
- **Remote GPU (`vp-colab-bridge`)**: Run via `pilot.py` or `sys/colab_bridge/` + `sys/renderer/render.mjs` (no local ffmpeg render).
- **Flow CDP (`vp-flow-cdp`)**: 39 profiles (`sys/flow_cdp/`), adaptive 1–16 workers, CreditLedger tracking, strict teardown. Valid AI image + `.json` sidecar.

## 4. Headless Colab GPU & Multi-T4 Pool (`vp-colab-bridge`)
- **Headless EGL + NVENC**: `chrome-wrapper.sh` (`VP_CHROME_PATH`, `DISABLE_FROM_SURFACE=true`, `gl-egl`), `<Img decoding="sync">`, `videoBitrate: '6M'` (`h264_nvenc`). No `xvfb-run` or `--use-angle=gl`.
- **Multi-T4 Pool**: Parallel TTS/renders via `ColabPoolManager` / `ColabPoolDispatcher` with teardown & `pkill -9`.

## 5. Execution Modes, 45s Watchdog & Bug Discipline
- **Modes**: Auto (E2E), Review (pause at stages), Stop & Handoff (halt preserving assets).
- **Mandatory 45s Watchdog & Fail-Fast**: Background tasks (`Colab`, `Flow CDP`, `E2E >30s`) MUST pair with `schedule(DurationSeconds=45, TimerCondition="any")` checking logs/PIDs/state.json every 45s. Abort multi-account failover after 2 consecutive `COLAB_EXEC_UNCONFIRMED` errors.
- **Bug Protocol**: Reproduction -> Root Cause -> Fix -> `PLAYBOOK.md` (6 fields, `<= 200` lines; overflow to `.agents/skills/`).

## 6. Quality, Doodle Style, Voice & V2 Pacing/CTA Guards
- **Anti-Flop**: `youtube_title <= 55` chars, Flow CDP `thumbnail_spec` (2–4 uppercase words; zero overlays), relatable hook (no `vi-đê-ô`), simple declarative sentences, constructive guidance (`script_diversity_linter.py`, `script_cadence_checker.py`).
- **V2 CTA & Phễu (`cta_tone_linter.py`)**: Short binds `parent_long_id`. 1 close CTA (<=24 syl) + 1 bridge (<=22 syl) in final 15% runtime (no 3s hook); long <=1 mid_cta at 35-45%. Banned: `đừng quên like`, `nhấn chuông`, `like share`, `subscribe`...
- **V2 Pacing (`sys/visual_pacing.py`)**: Hold: `fast` (0.9-1.8s/2-4s), `normal` (2-3.5s/4-7s), `slow` (3.5-5.5s/7-10s), `hold` (1.5-3s/5-20s). Short avg hold 2-3s; long avg 5-7s (70-90 beats). Max 3 consecutive beats same tempo (fast <=5).
- **Hand-Lettering**: Upper third, <=10% height, 1-4 uppercase VN words in Flow image (zero overlays), <=35% beats, no sub collision.
- **Voice (`VietNarrator` `1.0x`, `-11.0 LUFS` / `-1.0 dBTP`)**: Strip hyphens before OmniVoice BPE, strip bleed bursts, keep nasal codas, retry stalls, listen WAV.
- **2D Doodle (`1.7.0` `handdrawn_2d_explainer`)**: Lock `Nguệch Ngoạc / Vẽ Vời` (`sys/visual_style.py`: wobbly `#000000` marker, hex `#F8F0DC`, `#F2B88B`, `#93A88C`, `#CBE0E0`, `#2E4361`, `#FFFFFF`, bald stickman, `#3B82C4` shirt, wire arms, circle hands, 2D); Feynman: 1 stickman + 1 metaphor, >=60% negative space; zero walls, oval shadows, 3/4 isometric, vignette. Verify MP4 via `ffprobe` + frame check.

## 7. Language Standards
- **User**: Concise **Vietnamese**. **Code/Commits/Prompts**: **English** (preserve exact `I`).
