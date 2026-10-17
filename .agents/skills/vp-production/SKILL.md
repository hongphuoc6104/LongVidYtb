---
name: vp-production
description: "Create, continue, or repair Video Pilot videos (both long_16x9 13m explainers and short_9x16 45-60s spin-offs) through auto/review job contracts."
---

# Production

Use production scope and sys/docs/workflow.md. One task/role; current brief and saved bank sense define the product. Auto plans and executes without a reviewer; review waits at outline, dialogue, audio, image set and video checkpoints. Do not use legacy v3 auto to impersonate the new mode.

## Read guidance by step

- New topic architecture, Packaging & SEO Contract (`youtube_title <= 55` chars, `thumbnail_spec`, `channel_pillar` locked to *"Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật"*), Vietnamese 60s localization, and Short-Form Spin-off Blueprints (`brief.json` & `content.json` Schema 3.0): [vp-research-architect](../vp-research-architect/SKILL.md); vocabulary bank entry (`vocab/bank.py start`): [vocabulary](references/vocabulary.md).
- Outline/narration/cadence (Counter-Intuitive Hook `<= 18` syl, Zero Pause in `SC01`, 4.2–4.4 syl/s opening pace): [script](references/script.md), [narration](references/narration-style.md), and [vp-scriptwriting](../vp-scriptwriting/SKILL.md) (`vn_text_normalizer.py` + `script_cadence_checker.py`).
- Shot grammar & renderer limits (mandatory reading before creating beat/image plans — after dialogue is finalized, before writing prompts): [cinematography](references/cinematography.md) then [render-capabilities](../../../sys/docs/render-capabilities.md).
- Image/beat planning and generation: [storyboard and visuals](references/visuals.md) and [vp-flow-cdp](../vp-flow-cdp/SKILL.md). Generate a complete full-frame `kind: "scene"` image for each narration-anchored visual beat; use `based_on` with explicit `preserve` and `change` when a shot stays in the same place. Do not generate background/sticker cutouts or run `matte_sticker.py`.
- Request/WAV: [audio](references/audio.md) and [vp-colab-bridge](../vp-colab-bridge/SKILL.md).
- Timeline/captions/MP4: [editing](references/editing.md) and [vp-colab-bridge](../vp-colab-bridge/SKILL.md).
- Errors: [recovery](references/recovery.md) and [Colab error matrix](../vp-colab-bridge/references/error-recovery-matrix.md).

Channel brief specs follow sys/format_profiles.py across both official formats: `long_16x9` (13m Explainer Blueprint, 8 chapters / 48 scenes for YouTube) and `short_9x16` (45–60s, 5 standalone scenes `SC01..SC05`, `subtitles: true`, `speed: 1.0` with `VietNarrator` for TikTok/Shorts Spin-offs); freeze its relevant fields in the brief. Never raw-cut middle chapters (`CH02..CH08`) of a 16:9 video for TikTok. Never leak internal IDs/instructions into visible text.

Start with the total execution plan; author draft directly with version/anchors, not an implicit external generator. Send every real artifact to web/chat with job/version/path and verified measures. Do not represent a prompt/hash/metadata as visual or auditory inspection.

Old video repair is normal production work in the authorized scope. Change current content/artifacts through version/impact operations, preserve useful unaffected assets and request history. Do not ask permission per image/WAV when already covered. An engine/Rules change is out of scope: prepare a micro-plan/diff before requesting development authority.

Audio/media/timeline/render processing is remote Colab; Flow generates images. Production manages and auto-ensures required Colab T4 and Flow sessions on configured accounts to keep execution smooth without interrupting the workflow. Do not silently fallback locally or recreate an unknown request. Recover same owner/account/session first. Completion means actual required files collected under the relevant mode, never a fabricated quality decision.
