---
name: vp-production
description: "Create, continue, or repair Video Pilot videos (both long_16x9 explainers and short_9x16 spin-offs) through auto/review job contracts with dynamic duration."
---

# Production

Use production scope and sys/docs/workflow.md. One task/role; current brief and saved bank sense define the product. Auto plans and executes without a reviewer; review waits at outline, dialogue, audio, image set and video checkpoints. Do not use legacy v3 auto to impersonate the new mode.

## Read guidance by step

- New topic architecture, Packaging & SEO Contract (`youtube_title <= 55` chars, `thumbnail_spec`, `channel_philosophy` in `sys/pillars.py`), relatable opening context, and Short-Form Spin-off Blueprints (`brief.json` & `content.json` Schema 3.0): [vp-research-architect](../vp-research-architect/SKILL.md); vocabulary bank entry (`vocab/bank.py start`): [vocabulary](references/vocabulary.md).
- Outline/narration/cadence (Feynman simple sentences, natural cadence, soft advisory checks): [script](references/script.md), [narration](references/narration-style.md), and [vp-scriptwriting](../vp-scriptwriting/SKILL.md) (`vn_text_normalizer.py` + `script_cadence_checker.py`).
- Shot grammar & renderer limits (mandatory reading before creating beat/image plans — after dialogue is finalized, before writing prompts): [cinematography](references/cinematography.md) then [render-capabilities](../../../sys/docs/render-capabilities.md).
- Image/beat planning and generation: [storyboard and visuals](references/visuals.md) and [vp-flow-cdp](../vp-flow-cdp/SKILL.md). Generate a complete full-frame `kind: "scene"` image for each narration-anchored visual beat; use `based_on` with explicit `preserve` and `change` when a shot stays in the same place. Do not generate background/sticker cutouts or run `matte_sticker.py`.
- Request/WAV: [audio](references/audio.md) and [vp-colab-bridge](../vp-colab-bridge/SKILL.md).
- Timeline/captions/MP4: [editing](references/editing.md) and [vp-colab-bridge](../vp-colab-bridge/SKILL.md).
- Errors: [recovery](references/recovery.md) and [Colab error matrix](../vp-colab-bridge/references/error-recovery-matrix.md).

Channel brief specs follow sys/format_profiles.py across both official formats: `long_16x9` (landscape widescreen explainers for YouTube; dynamic duration & scenes via `content_depth_estimate`) and `short_9x16` (vertical standalone spin-offs, `subtitles: true`, `speed: 1.0` with `VietNarrator` for TikTok/Shorts Spin-offs); freeze its relevant fields in the brief. Zero fixed duration constraints — video duration and scene counts are determined strictly by narrative depth (`content_depth_estimate`) and measured WAV narration. Never raw-cut middle chapters of a 16:9 video for TikTok without standalone restructuring. Never leak internal IDs/instructions into visible text.

Start with the total execution plan; author draft directly with version/anchors, not an implicit external generator. Send every real artifact to web/chat with job/version/path and verified measures. Do not represent a prompt/hash/metadata as visual or auditory inspection.

Old video repair is normal production work in the authorized scope. Change current content/artifacts through version/impact operations, preserve useful unaffected assets and request history. Do not ask permission per image/WAV when already covered. An engine/Rules change is out of scope: prepare a micro-plan/diff before requesting development authority.

Audio/media/timeline/render processing is remote Colab via Native Tesla T4 `FFmpeg h264_nvenc` (`flow_video_worker.py` via `job_worker.py`); Flow generates images. Production manages and auto-ensures required Colab T4 and Flow sessions on configured accounts to keep execution smooth without interrupting the workflow. Do not silently fallback locally or recreate an unknown request. Recover same owner/account/session first. Completion means actual required files collected under the relevant mode, never a fabricated quality decision.

## Canonical Motion Mode Hierarchy & Credit Fallback
- **Sole Canonical Renderer**: Colab Tesla T4 Native `FFmpeg h264_nvenc` (`flow_video_worker.py` via `job_worker.py`, `-c:v h264_nvenc -preset p4 -b:v 6M`, `0s` setup; zero Remotion/Chromium/TPU/local CPU render overhead).
- **Priority 1 (Default while ANY Flow pool profile has credit)**: `100% Full-Chain` (`Omni 1.1 Flash` continuous keyframe-to-keyframe video chain across parallel GPU Chrome workers + Native Tesla T4 `FFmpeg h264_nvenc` burned-in VietSub/watermark/loudnorm render). This is the canonical priority mode whenever video credits remain on ANY profile in the 39+ Flow pool.
- **Priority 2 (Automatic Fallback ONLY when 100% of Flow pool profiles have 0 video credits left)**: Dense Multi-Image mode (`images_only` with high-density Flow keyframes: 10–14 images for `9:16` Short, 28–70+ images for `16:9` Long + Native Tesla T4 `FFmpeg h264_nvenc` camera motion/VietSub/loudnorm render). The pipeline automatically falls back to dense multi-image rendering ONLY when 100% of Flow pool profiles hit 0 credits (before Stage C starts or mid-chain), guaranteeing the video renders cleanly without failure.

**Mandatory 45s Background Watchdog & Fail-Fast Default (`WATCHDOG-45S`)**: Worker subagents executing background tasks (`Colab TTS/render`, `Flow CDP`, `E2E >30s`) MUST arm `schedule(DurationSeconds=45, TimerCondition="any")` and re-arm every 45s until completion, inspecting task logs, active PIDs, and `state.json`. The Orchestrator does NOT poll, waiting reactively for subagent completion reports. Abort multi-account failover after `2` consecutive `COLAB_EXEC_UNCONFIRMED` errors and inspect remote stderr via `Client.exec`.
