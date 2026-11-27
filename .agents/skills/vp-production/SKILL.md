---
name: vp-production
description: "Create, publish, or repair dual-format videos (long_16x9 and short_9x16), omni-platform deliverables, and full episode lifecycles via ./vp."
---

# VP Production & Episode Lifecycle (`vp-production`)

Executes dual-format video creation, publishing, and multi-platform packaging (`outline -> dialogue -> audio -> images -> video`) using the shared `./vp` CLI, `sys/format_profiles.py`, and channel data playbooks (`[vp-channel-registry](../vp-channel-registry/SKILL.md)`). Auto plans and executes end-to-end; review waits at explicit human checkpoints.

## 1. Unified CLI & Workflow Routing
Run `./vp status` before starting a batch, `./vp playbook <channel_id>` to read the target channel's 3-pillar contract, `./vp scaffold-short` / `./vp clone-en` to prepare V4 specs, `./vp short`, `./vp long-reborn`, or `./vp long-m1` to build, `./vp publish` to upload, and `./vp studio` for Web Dashboard inspection.

- **Channel Selection & Playbooks:** [vp-channel-registry](../vp-channel-registry/SKILL.md)
- **Research, Packaging (`youtube_title <= 55` chars, `vocab/bank.py start`), Script & 4 Linters:** [vp-content-studio](../vp-content-studio/SKILL.md) · [script.md](references/script.md) · [narration-style.md](references/narration-style.md)
- **Visual Style, Cinematography, 2.5D/30fps FX (`--fx-mode auto_niche`, `[PRO_FX]`/`[BESPOKE_FX]`) & Non-Forced Selection:** [vp-visual-fx](../vp-visual-fx/SKILL.md) · [cinematography.md](references/cinematography.md) · [visuals.md](references/visuals.md) · [render-capabilities](../../../sys/docs/render-capabilities.md)
- **Flow CDP Image/Video Harvest & Teardown:** [vp-flow-cdp](../vp-flow-cdp/SKILL.md)
- **Colab T4 OmniVoice Audio (`-11.0 LUFS`) & `h264_nvenc` Render:** [vp-colab-bridge](../vp-colab-bridge/SKILL.md) · [audio.md](references/audio.md) · [editing.md](references/editing.md)
- **End-to-End Episode Checklist & Multi-Platform Spin-Offs:** [new-episode-checklist.md](references/new-episode-checklist.md) · [omni-platform-deliverables.md](references/omni-platform-deliverables.md)
- **Error Recovery:** [recovery.md](references/recovery.md) · [Colab error matrix](../vp-colab-bridge/references/error-recovery-matrix.md)

## 2. Format Contracts (`sys/format_profiles.py`) & Motion Hierarchy
- **Sole Canonical Renderer:** Remote Colab Tesla T4 Native `FFmpeg h264_nvenc` (`flow_video_worker.py` / `job_worker.py`, `-bf 0 -g 30 -b:v 10M -preset p4` or `-b:v 6M`). Zero Remotion, Chromium, TPU, or local CPU render fallbacks. Bottom-right channel watermark pinned at `W-w-36:H-h-36`.
- **`short_9x16` & `serialized_detail_short`:** `48–60s` (`11–15` beats) or V4 `15–16` / `20` beats (`4 chunks × 5 beats`, `--render-mode single_pass` `1440x2560` on 4 T4 GPUs via `sys/tools/produce_serialized_short.py` + `sys/short_engine/`), Dual-Model Flow Router (`veo_3_1_lite` Seam Mode + `macaron_cookie` Omni 1.2 Flash Frame-Link).
- **`long_16x9`:** Flagship **Reborn V11.5 Anti-AI Long-Form Omni Cinema** (`./vp long-reborn` -> `sys/tools/produce_reborn_long_pilot.py`, `8m30s–11m30s`, `6` Acts, `~85–95` beats): Stage A0 `character_roster` turnaround anchors (`--stage anchors`, `reference_media_ids` per Flow profile), `1.0x` native `macaron_cookie_i2v[_fl]_{4s|6s|8s|10s}` Hero-POV + Flow Aerial/Split-Waterline seekbar-safe `y <= 0.72*H` RGBA overlays + Zero-Box optical spotlight forensic reveals, fluent `omni_speed=1.12` + `atempo=1.14..1.16` voice lock banning `< 1.08`, hard `ANTI_AI_QA_RULES` / `audit_color_continuity` (`--strict-anti-ai`) + 6-frame `motion-police` audit, and 6-GPU parallel Colab T4 `/dev/shm` `h264_nvenc` render (`--colab-render-workers 6 --color-grade kodak_2383_anti_ai` Lab harmony + 35mm grain + lossless `concat` + `colab stop`); OR `M1-Flex V9.2` `16:9` IMAX moving cinema (`./vp long-m1`); OR `240–350` `BELUGA` frames + static Lanczos + `xfade=fade` (`--fx-mode auto_niche`), with external `.srt` & chapter markers.
- **Credit Fallback Hierarchy:** P1 `full_chain` while ANY Flow profile holds credits; P2 `images_only` ONLY when 100% of pool profiles hit `0` credits (`cooldown != 0 credits`).
- **45s Watchdog (`WATCHDOG-45S`):** Subagents running jobs >30s arm `schedule(DurationSeconds=45, TimerCondition="any")`; stop multi-account Colab failover after `2` consecutive `COLAB_EXEC_UNCONFIRMED` errors.

## 3. Turnkey `/run-workflow` Scripts (`scripts/` — Safe Parallel Spec + Sequential Render)
Run `./vp workflows` (or pick a 1-click preset in `./vp studio`) to invoke these built-in `run_workflow` scripts without creating extra workspace skills:
- **[wf_reborn_long.py](scripts/wf_reborn_long.py)**: Flagship 5-phase **V11.5 Reborn Anti-AI 10-Minute Documentary** pipeline — Phase 1 Fact Vault (`>=24` facts) + `character_roster` Bible + 6-Act spec + `--strict-anti-ai`; Phase 2 `parallel` 1.30x 5-stem OmniVoice audio + Stage A0 `reference_media_ids` Flow harvest; Phase 3 `parallel` 6-shard Anti-AI & 6-frame `motion-police` gate + bounded surgical re-roll loop (`max_reroll_rounds=3`); Phase 4 6-GPU parallel Colab T4 `h264_nvenc` render (`--color-grade kodak_2383_anti_ai`); Phase 5 `parallel` 6-Act final audit + `ffprobe`/`ebur128` + optional YouTube publish. One-call invocation:
  ```python
  run_workflow(
      ScriptPath=".agents/skills/vp-production/scripts/wf_reborn_long.py",
      Description="Produce V11.5 Reborn Long 10m Documentary",
      Args={
          "channel": "<channel_id>",
          "topic": "<episode topic>",
          "job": "",
          "target_duration_sec": 600,
          "colab_workers": 6,
          "color_grade": "kodak_2383_anti_ai",
          "render": True,
          "publish": False,
      },
  )
  ```
- **[wf_series_shorts.py](scripts/wf_series_shorts.py)**: Recommended Series-First flow — discovers/grounds one cohesive Series arc (`3–5` Shorts default, configurable up to `15`, `serialized_detail_short` 20 beats), writes all episode specs in `parallel`, stops for review (`render=False`), and optionally batch-renders sequentially (`pipeline`).
- **[wf_batch_shorts.py](scripts/wf_batch_shorts.py)**: Parallel standalone Short V4 spec authoring across channels/waves (`parallel`) + safe sequential 2K render (`pipeline` honoring Flow IP & Chrome limits).
- **[wf_clone_en_twins.py](scripts/wf_clone_en_twins.py)**: Parallel VN → EN native twin adaptation (`parallel`) + optional sequential 2K render (`pipeline`).
- **[wf_qa_and_publish.py](scripts/wf_qa_and_publish.py)**: Parallel 3-angle QA council (Fact/Script, Media `ffprobe`/`ebur128`, Packaging/Debate) + optional YouTube Studio publish.
