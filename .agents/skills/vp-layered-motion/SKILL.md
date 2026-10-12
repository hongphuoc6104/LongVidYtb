---
name: vp-layered-motion
description: "Plan and render layered cut-out videos with stick-figure stickers on background plates."
---

# Layered motion (cut-out stickers)

Use with **vp-production** scope. This skill only changes how content is authored; generation, audio, matting and render still run through `pilot.py` (Flow for images, Colab T4 for audio/matte/render). Never run the old scratch scripts, local matting or local render for a real job.

## When a scene is layered
A scene is layered when it declares `layers`. Then its `images` contain exactly one `kind: "background"` image and up to 4 new `kind: "sticker"` images; `beats` has exactly one beat (the background). Flat scenes (`kind` omitted = `scene`) keep the old behaviour, and both kinds may coexist in one job.

## Authoring steps (after dialogue is final)
1. Split each sentence into visual beats → decide which sticker appears on which word ([layer-breakdown](references/layer-breakdown.md)).
2. Write background description: the place only, no figures. Write sticker descriptions: one figure or one prop, pose/costume/props explicit. Follow **Editorial Graphic Visuals** (`ERR-20261011-03`): use clean architectural geometry, expressive posture, and single focal props instead of literal mechanical clichés (strictly avoid repeated brain cutaways, abacuses, pipe-valves, iron anchors, or generic split-screen comparisons).
3. Reuse stickers from earlier scenes (`layers[].image_id` may point to any earlier sticker) — cheaper Flow quota and natural continuity.
4. For each layer set `anchor` (exact narration quote + occurrence), `fx`, `x/y/w` (0–1, centre of sticker — place single or dual stickers on **Rule-of-Thirds** horizontal coordinates `x ∈ [0.34, 0.38]` or `x ∈ [0.62, 0.66]`, default `RULE_OF_THIRDS_X = (0.35, 0.64)`, rather than dead-center `0.50`), optional `exit_anchor`/`exit_fx`, `shake_anchor`, `z` ([animation-presets](references/animation-presets.md)).
5. Keep the bottom 18% for captions on `9:16` (`sticker y + height/2` stays above ~0.80); on `16:9` flat/multi-shot scenes, pair **Semantic Camera Motion** (`select_semantic_camera_effect` / `assign_scene_camera_effects`: wide/establishing → `zoom_out`, focus/detail → `zoom_in` or `punch_in`, lateral action → `pan_right` / `pan_left`) with zero consecutive duplicates — never use mechanical modulo-5 cycling (`(idx - 1) % 5`).
6. `pilot.py author JOB dialogue --data …` then `run`. Validation codes `LAYER_*` explain every rejection.

## What the engine does
- Registry **1.2.0** compiles `layer_background` / `layer_sticker` prompts (no Base/Character reference, no preserve/change).
- Colab render worker mattes each sticker by border flood-fill and adds the white sticker halo ([sticker-matting](references/sticker-matting.md)), writes `layers-report.json`, then Remotion renders `scene.layers` with spring physics, line-boil jitter and caption highlight.
- Timing comes from narration anchors interpolated inside actual audio chunks (not word-forced alignment).

## Limits
- Flow quota: ≤4 new stickers per scene, prefer reuse ([flow-quota](references/flow-quota.md)).
- A sticker whose outline is open lets the flood-fill leak into white interiors; repair by image reject with a correction ("continuous closed black outline").
- Technical checks do not prove look/feel; inspect real frames before claiming quality.
