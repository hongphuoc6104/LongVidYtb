# Video Pilot — Agent Rules (SSOT)

Read `PLAYBOOK.md` and the domain `SKILL.md` before acting. Precedence: `AGENTS.md` > `.agents/rules/*` > `PLAYBOOK.md` > `SKILL.md` > `references/`.

## 1. Products & Pipeline (`sys/format_profiles.py`, `vp-production`)
- Dual-mode (`sys/tools/produce_vn_dual_mode.py`): `short_9x16` (48–60s, Omni 1.2 Flash full-chain) & `long_16x9` (8m30s–13m, 13m Explainer Blueprint, 240–350 BELUGA images, static Lanczos frame + `xfade=fade` only).
- Credit priority: P1 `full_chain` while any Flow profile has credit; P2 `images_only` only when 100% of pool is at 0 credits (cooldown ≠ 0 credits).
- Chain: `vp-research-architect` → `vp-scriptwriting` → `vp-full-frame-quality` → `vp-omni-platform` → `vp-flow-cdp` → `vp-colab-bridge` → `vp-production`.
- Philosophy: `sys/pillars.py` `ContentPhilosophy` (`cognition` default); tier-3 `screen_capture` requires user source.

## 2. Render, Audio & Chrome (`vp-colab-bridge`, `vp-flow-cdp`)
- Colab T4 `FFmpeg h264_nvenc` only (`ColabPoolDispatcher`); no Remotion/Chromium/TPU/local fallback; always `colab stop`.
- Audio `-11.0 LUFS` / `-1.0 dBTP`; per-channel voice `VietNarrator_<channel_id>` on OmniVoice (never `vi-VN-NamMinhNeural`).
- Logo pinned bottom-right `W-w-36:H-h-36` on both formats. All Chrome/CDP obeys `.agents/rules/gpu-headless-chrome.md`.

## 3. Content & Visual (`vp-scriptwriting`, `vp-full-frame-quality`)
- Packaging: `youtube_title <= 55` chars; Flow-native thumbnail with 2–4 uppercase words drawn in (zero PIL/HTML overlay).
- Script & CTA: simple spoken sentences (`script_cadence_checker.py`, `script_diversity_linter.py`, `cta_tone_linter.py`); short has `parent_long_id` + close CTA + channel bridge in last 15%; never "like/share/subscribe".
- Visual `1.7.0 handdrawn_2d_explainer`: 1 stickman + 1 metaphor, ≥60% negative space, hand-lettering ≤10% height on ≤35% beats; gate: `sys/visual_pacing.py`. Verify real MP4 (`ffprobe` + frames) & WAV.

## 4. Execution, Code & Git (`vp-development`)
- Modes: Auto · Review (`outline -> dialogue -> audio -> images -> video`) · Stop & Handoff.
- Jobs >30s: worker arms `schedule(DurationSeconds=45, TimerCondition="any")`; stop failover after 2 `COLAB_EXEC_UNCONFIRMED`.
- Bugs: reproduce → root cause → fix → verify E2E → `PLAYBOOK.md` (6 fields, ≤200 lines). Gate: `./pipeline run`.
- Layout: engine `sys/`, runs `sys/runs/<job>/`, output `video/<job>/`, one-off scripts `sys/scratch/`. Stage explicit files; obey `.githooks/pre-commit`. Reply in concise Vietnamese; code/commits in English.
