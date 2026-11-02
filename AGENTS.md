# Video Pilot Invariants & Governance

## 1. Dual-Format SSOT & Niche Pillar
- **Dual-Format (`sys/format_profiles.py`)**: `long_16x9` (13m Explainer Blueprint ref; dynamic duration via `content_depth_estimate`) & `short_9x16` (`subtitles: true`, `speed: 1.0`, `VietNarrator`). Measured WAV duration.
- **Philosophy (`sys/pillars.py`)**: `ContentPhilosophy` (`cognition` default); adaptive flow; T3 `screen_capture` -> ask source. No shallow tips.
- **Directory**: `sys/` (tools), `sys/runs/<job>/` (assets), `video/<job>/` (MP4/SRT). Root clean.

## 2. Technical Ethos & 6 Stations (`./pipeline run`)
- **Standards**: Modular, typed code. No monkey-patches, fake test passes, manual DB edits.
- **Conveyor**: St1 Critique -> St2 AST & `pytest` -> St3 `PLAYBOOK.md` -> St4 `ruff` -> St5 PR (`gh-axi`) -> St6 Green CI.

## 3. Pipelines & Role Separation
- **Production (`vp-production`)**: Priority: P1 `full_chain` (`Omni 1.1 Flash` continuous `.mp4` clips while any Flow pool profile has credits); P2 `images_only` (dense fallback when 100% of Flow pool hits 0 credits). Chain: `vp-research-architect` -> `vp-scriptwriting` -> `vp-full-frame-quality` -> `vp-omni-platform` -> Multi-T4 (`ColabPoolDispatcher` / `pilot.py` outline -> dialogue -> audio -> images -> video).
- **Remote GPU (`vp-colab-bridge`)**: Native Tesla T4 `FFmpeg h264_nvenc` (`sys/colab_bridge/flow_video_worker.py` via `job_worker.py` / `pilot.py`, `-c:v h264_nvenc -preset p4 -b:v 6M`, `0s` setup; no Remotion/Chromium/TPU/local render).
- **Flow CDP (`vp-flow-cdp`)**: 39 profiles (`sys/flow_cdp/`), adaptive 1–16 workers, CreditLedger tracking, strict teardown. Valid AI image + `.json` sidecar.

## 4. Colab GPU NVENC & Multi-T4 Pool (`vp-colab-bridge`)
- **Native GPU `FFmpeg h264_nvenc`**: `-c:v h264_nvenc -preset p4 -b:v 6M`, burned-in `.srt` (`9:16`), sidecar `.srt` (`16:9`), rounded watermark on endcard, `-11.0 LUFS` / `-1.0 dBTP` audio.
- **Multi-T4 Pool**: Parallel TTS/renders via `ColabPoolManager` / `ColabPoolDispatcher` with strict `colab stop` teardown.

## 5. Execution Modes, 45s Watchdog & Bug Discipline
- **Modes**: Auto (E2E), Review (pause), Stop & Handoff (halt, keep assets).
- **Mandatory 45s Watchdog & Fail-Fast**: Worker subagents running background jobs (>30s) MUST pair with `schedule(DurationSeconds=45, TimerCondition="any")` checking logs/PIDs/state.json every 45s; Orchestrator waits reactively for subagent reports without polling. Abort failover after 2 consecutive `COLAB_EXEC_UNCONFIRMED`.
- **Bug Protocol**: Reproduction -> Root Cause -> Fix -> `PLAYBOOK.md` (6 fields, `<= 200` lines; overflow to skills).

## 6. Quality, Doodle Style, Voice & V2 Pacing/CTA Guards
- **Anti-Flop**: `youtube_title <= 55` chars, Flow CDP `thumbnail_spec` (2–4 uppercase words; zero overlays), relatable hook (no `vi-đê-ô`), simple declarative sentences (`script_diversity_linter.py`, `script_cadence_checker.py`).
- **V2 CTA & Phễu (`cta_tone_linter.py`)**: Short binds `parent_long_id`. 1 close CTA (<=24 syl) + 1 bridge (<=22 syl) in last 15% (no 3s hook); long <=1 mid_cta at 35-45%. Banned: like, share, subscribe...
- **V2 Pacing (`sys/visual_pacing.py`)**: Hold: fast (0.9-1.8s/2-4s), normal (2-3.5s/4-7s), slow (3.5-5.5s/7-10s), hold (1.5-3s/5-20s). Short avg 2-3s; long avg 5-7s (70-90 beats). Max 3 consecutive same tempo (fast <=5).
- **Hand-Lettering**: Upper third, <=10% height, 1-4 uppercase words in Flow image (zero overlays), <=35% beats, no sub collision.
- **Voice (`VietNarrator` `1.0x`, `-11.0 LUFS` / `-1.0 dBTP`)**: Strip hyphens before OmniVoice BPE, strip bleed bursts, keep nasal codas, retry stalls, listen WAV.
- **2D Doodle (`1.7.0` `handdrawn_2d_explainer`)**: Lock `Nguệch Ngoạc` (`sys/visual_style.py`: 7-color palette, bald stickman, `#3B82C4` shirt, wire arms, circle hands); Feynman: 1 stickman + 1 metaphor, >=60% negative space; zero walls/shadows/vignette. Check MP4 via `ffprobe` + frame.

## 7. Language Standards
- **User**: Concise **Vietnamese**. **Code/Commits/Prompts**: **English** (preserve exact `I`).
