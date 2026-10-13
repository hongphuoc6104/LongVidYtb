---
name: vp-production
description: "Create, continue, or repair Video Pilot videos through auto/review job contracts."
---

# Production

Use production scope and sys/docs/workflow.md. One task/role; current brief and saved bank sense define the product. Auto plans and executes without a reviewer; review waits at outline, dialogue, audio, image set and video checkpoints. Do not use legacy v3 auto to impersonate the new mode.

## Read guidance by step

- New topic architecture (`brief.json` & `content.json` Schema 3.0): [vp-research-architect](../vp-research-architect/SKILL.md); vocabulary bank entry (`vocab/bank.py start`): [vocabulary](references/vocabulary.md).
- Outline/narration/cadence: [script](references/script.md), [narration](references/narration-style.md), and [vp-scriptwriting](../vp-scriptwriting/SKILL.md) (`vn_text_normalizer.py` + `script_cadence_checker.py`).
- Shot grammar & renderer limits (mandatory reading before creating beat/image plans — after dialogue is finalized, before writing prompts): [cinematography](references/cinematography.md) then [render-capabilities](../../../sys/docs/render-capabilities.md).
- Image/beat planning and generation: [storyboard and visuals](references/visuals.md) and [vp-flow-cdp](../vp-flow-cdp/SKILL.md); layered cut-out video (background + timed stickers): also follow [vp-layered-motion](../vp-layered-motion/SKILL.md).
- Request/WAV: [audio](references/audio.md) and [vp-colab-bridge](../vp-colab-bridge/SKILL.md).
- Timeline/captions/MP4: [editing](references/editing.md) and [vp-colab-bridge](../vp-colab-bridge/SKILL.md).
- Errors: [recovery](references/recovery.md) and [Colab error matrix](../vp-colab-bridge/references/error-recovery-matrix.md).

Channel brief specs follow sys/format_profiles.py (13m Explainer Blueprint); freeze its relevant fields in the brief. No fixed joke arc, image quota, learner-repeat count, provider, voice or aspect-to-language mapping from this skill. Never leak internal IDs/instructions into visible text.

Start with the total execution plan; author draft directly with version/anchors, not an implicit external generator. Send every real artifact to web/chat with job/version/path and verified measures. Do not represent a prompt/hash/metadata as visual or auditory inspection.

Old video repair is normal production work in the authorized scope. Change current content/artifacts through version/impact operations, preserve useful unaffected assets and request history. Do not ask permission per image/WAV when already covered. An engine/Rules change is out of scope: prepare a micro-plan/diff before requesting development authority.

Audio/media/timeline/render processing is remote Colab; Flow generates images. Production manages and auto-ensures required Colab T4 and Flow sessions on configured accounts to keep execution smooth without interrupting the workflow. Do not silently fallback locally or recreate an unknown request. Recover same owner/account/session first. Completion means actual required files collected under the relevant mode, never a fabricated quality decision.
