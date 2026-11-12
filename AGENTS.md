# Video Pilot Invariants & Governance

## 0. Mandatory Pre-Task Reading Protocol (Priority Document Gate)
Every agent session MUST read the required documents below before taking any planning, coding, production, or debugging action:
- **Tier 1 (Mandatory for ALL tasks)**:
  - `AGENTS.md`: System-wide SSOT Architecture, Governance, & Hard Invariants.
  - `PLAYBOOK.md`: Operational Post-Mortems, Anti-Regression Rules, & Root Cause Fixes.
  - `.agents/rules/gpu-headless-chrome.md`: Mandatory Rule for Hidden GPU Chrome (`--headless=new` + `90%` VRAM via `build_optimized_chrome_launch`).
- **Tier 2 (Mandatory Domain Skill SSOT — read the exact domain `SKILL.md` before acting)**:
  - Video Production / Spin-offs / Dual-Mode E2E: `.agents/skills/vp-production/SKILL.md`
  - Flow CDP Image & Video Chain Engine: `.agents/skills/vp-flow-cdp/SKILL.md`
  - Colab Tesla T4 GPU TTS & NVENC Render: `.agents/skills/vp-colab-bridge/SKILL.md`
  - Conversational Scriptwriting & Cadence: `.agents/skills/vp-scriptwriting/SKILL.md`
  - Research Architecture & 3-Tier Funnel Packaging: `.agents/skills/vp-research-architect/SKILL.md`
  - 2D Doodle `1.7.0` (`Nguệch Ngoạc`) Visual Quality: `.agents/skills/vp-full-frame-quality/SKILL.md`
  - Multi-Platform Publishing & Funnel Linking: `.agents/skills/vp-omni-platform/SKILL.md`
  - Troubleshooting & Recovery: `.agents/skills/vp-troubleshooting/SKILL.md`
  - Engine Development & 6-Station Conveyor: `.agents/skills/vp-development/SKILL.md`
- **Tier 3 (Deep Reference — read specific references when matching an error code or sub-workflow)**:
  - Open target `.agents/skills/<skill>/references/*.md` as indexed in each skill.

## 1. Dual-Format SSOT & Production Architecture (`produce_vn_dual_mode.py` & `format_profiles.py`)
- **Dual-Format Delivery**:
  - **`short_9x16` (Bản Short 48–60s)**: `100% Full-Chain` (`Omni 1.2 Flash` / `macaron_cookie_i2v_fl_4s/6s/8s/10s` continuous video clips from `11–15` `BELUGA` keyframes, `trim=start_frame=1` zero-stutter stitching, 1-word Red `#FF3B30` / Yellow `#FFE600` kinetic `.ass` subtitles, Colab Tesla T4 `h264_nvenc`).
  - **`long_16x9` (Bản Long 8m30s–13m)**: `240–350` High-Density `BELUGA` 8K Multi-Image (`~100–120` Base Anchors + `~140–230` 1-hop `based_on` Progressive States across 4 pacing modes: Rapid `1.2–2.0s`, Normal `2.2–3.2s`, Slow `3.5–4.8s`, Hold `5.0–6.5s`) + `1.25x` supersampled zero-snap `zoompan` + directional `xfade` (`0.24s`) + sidecar `.srt` + `8–12` `FFMETADATA1` YouTube Chapters rendered in 3-worker parallel `/dev/shm` chunks + `<1s` lossless `stream-copy` concat on Colab Tesla T4 `h264_nvenc`.
- **Philosophy (`sys/pillars.py`)**: `ContentPhilosophy` (`cognition` default); adaptive flow; T3 `screen_capture` -> ask source. No shallow tips.
- **Directory**: `sys/` (tools), `sys/runs/<job>/` (assets), `video/<job>/` (MP4/SRT). Root clean.

## 2. Technical Ethos & 6 Stations (`./pipeline run`)
- **Standards**: Modular, typed code. No monkey-patches, fake test passes, manual DB edits.
- **Conveyor**: St1 Critique -> St2 AST & `pytest` -> St3 `PLAYBOOK.md` -> St4 `ruff` -> St5 PR (`gh-axi`) -> St6 Green CI.

## 3. Pipelines & Flow CDP GPU / Anti-IP-Ban Invariants (`vp-flow-cdp`)
- **Production Hierarchy**: P1 `full_chain` (`Omni 1.2 Flash` continuous `.mp4` clips while any Flow pool profile has credits); P2 `images_only` (dense fallback when 100% of Flow pool hits 0 credits). Chain: `vp-research-architect` -> `vp-scriptwriting` -> `vp-full-frame-quality` -> `vp-omni-platform` -> Multi-T4 (`ColabPoolDispatcher` / `pilot.py` outline -> dialogue -> audio -> images -> video).
- **GPU Headless Chrome (`90%` VRAM)**: Headless Chrome on Linux MUST run on local GPU within 90% VRAM (`--headless=new --ozone-platform=x11 --disable-software-rasterizer --force-gpu-mem-available-mb=1843`). Zero CPU SwiftShader fallback.
- **Cross-Process Staggered Launch**: Cross-process staggered Chrome launch (`>= 3.2s + 0.6s` gap via `stagger_cross_process_action("chrome_launch")`) — NEVER launch all Chrome windows simultaneously into `flow.google.com`.
- **Global Jittered RPC Pacer**: Cross-process pacer (`1.55s + 0..0.35s` via `stagger_cross_process_action("flow_rpc_submit")`) capped at `~34–38 RPCs/min` host-wide + opportunistic 2–4 prompt batching (`generate_images_batch` on `ogiZ0b`).
- **Warm Session Preservation (`ERR-20261010-07`)**: On Error 7/8 (`PUBLIC_ERROR_UNUSUAL_ACTIVITY` / `TOO_MUCH_TRAFFIC`), NEVER kill/relaunch Chrome or reload the tab; refresh reCAPTCHA in-place (`_refresh_recaptcha_session`), keep the warm Chrome instance alive during profile cooldown, and quarantine `NO_AT_TOKEN` profiles automatically.

## 4. Colab GPU NVENC & Multi-T4 Pool (`vp-colab-bridge`)
- **Native GPU `FFmpeg h264_nvenc`**: `-c:v h264_nvenc -preset p4 -b:v 6M`, burned-in `.ass`/`.srt` (`9:16`), sidecar `.srt` (`16:9`), rounded watermark on endcard, `-11.0 LUFS` / `-1.0 dBTP` audio. No Remotion/Chromium/TPU/local render.
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
