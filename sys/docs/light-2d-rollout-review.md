# Light, moderately simplified 2D stick-figure images

Approved and implemented on 2026-10-18. New jobs use prompt registry 1.4.0.

## Approved direction

Keep anonymous round-white-headed stick figures, expressive simple faces and cartoon hands. Make backgrounds easier to read by drawing only the contextual cues needed for the action. Use light-value pastel fills, restrained charcoal contours and finer, lower-contrast background linework. Maintain enough context to recognize the place.

Settings, time of day, costumes and palettes stay specific to each story. Night remains night with readable ambient illumination. Useful metaphors remain allowed. There is no fixed room, universal palette or arbitrary object/person quota.

Visual interest comes from gesture, expression, composition and selective accents. Avoid large near-black fills, heavy marker borders, exhaustive furniture and architectural details, muddy grading and decorative visual noise.

## Implementation

- [Registry 1.4.0](../flow_prompts/versions/1.4.0/registry.json) supplies the prompt treatment.
- [Shared authoring defaults](../visual_style.py) read the same registry.
- [Prompt compilation](../flow_prompts/compiler.py) and [image requests](../image_pipeline.py) preserve explicit model/version pins, exact lettering, optional style references, Base variations, shot types and full-bleed framing.
- [Remote request packaging](../colab_bridge/job_protocol.py) hashes the selected treatment and packages its dependencies; the worker passes it to main and standalone-short props.
- [Renderer treatment](../renderer/visual-style.mjs) preserves the new image colors without vignette or grain. Legacy grading is retained for historical profiles.
- [Production guidance](../../.agents/skills/vp-production/references/visual-style.md) separates focal detail from background detail.

Historical registry bytes, request identities and downloaded assets are retained. Existing pinned jobs do not silently inherit a different prompt version.

## Review and verification

The review covered the 30-file engine, authoring guidance, regression-test and CI change set in [PR #2](https://github.com/hongphuoc6104/LongVidYtb/pull/2). No unresolved defect was found in that scoped change set.

Two defects found during implementation were repaired and documented in PLAYBOOK:
- Capability imports must be available with and without attached style references.
- Integration fixtures must close both socket and direct-CDP transport boundaries, retaining real before-send checks while preventing real provider calls.

The CI evidence reader also uses an explicit machine-readable envelope because gh-axi renders nonempty arrays as TOON tables. Exact-commit and all-runs-success checks remain enforced.

Verification before this documentation checkpoint: 246 tests and 8 subtests passed in the main workspace and clean feature checkout. All six conveyor stations passed for code commit 45a9a1464aedafab698b01ff6a3ec381d777161a, with two successful GitHub Actions runs.

Six genuine Flow images were recreated from Collector's Fallacy, Adversarial AI and Feynman videos: night study, daylight reading, a committee, a prediction diagram, a forest scene and a portrait phone close-up. Each collected image has a provider media identifier, hash, compiled prompt and sidecar; historical source hashes were unchanged. The images and local comparison report remain outside the source-code checkpoint.

These are still-image previews. No new MP4 has been rendered, and automated contract tests do not certify aesthetic acceptance. The night sample intentionally remains darker than the daylight examples.

## Checkpoint scope

Publish the reviewed visual-style engine, guidance and this approved plan through the existing feature PR. The later repository checkpoint includes reviewed production packages and runtime code as well. Credentials, live job state and generated media stay local.
