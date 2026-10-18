---
name: vp-full-frame-quality
description: Author or repair Video Pilot full-frame visual journeys, continuity and caption/camera contracts. Use with full_frame_v1 jobs, not layered-motion assets.
---

# Full-frame authoring contracts

New images use the light, moderately simplified anonymous stick-figure profile `1.4.0`. Follow [visual style](../vp-production/references/visual-style.md): keep context flexible, simplify background detail and use light-value colors with restrained contours. Existing pinned jobs retain their original style.

- New full-frame jobs declare `visual_pacing_profile: full_frame_v1`. Older snapshots remain readable; do not edit saved revisions or journals to migrate them.
- Landscape defaults to external SRT (`subtitles: false`); portrait keeps burn-in subtitles and its renderer safe area. Full-frame image prompts reserve no caption band in either aspect. Keep backgrounds continuous to the canvas edges.
- Canonical `VietNarrator` uses `speed: 1.0` across both long videos (`long_16x9`) and short spin-offs (`short_9x16`). The contract permits `[0.90, 1.15]`; scene-level `tone` modulation (`0.98`, `1.02`, `0.92` via `resolve_tone_speed`) is validated against `allowed_speeds`. A speed multiplier is not a measured syllable rate.
- A sentence is a TTS boundary. Keep bilingual parts and gaps aligned with sentence chunks. SRT cues never append the opening words of the next sentence.
- Author distinct visual settings: no more than two consecutive scenes in one setting; for ten or more scenes no setting exceeds 30%. Progress across the 4 functional cognitive phases (`narrative_phase`: `lived_friction` → `empirical_conflict` → `structural_model` → `actionable_resolution`) without requiring hardcoded school-room nouns.
- Reserve roughly the final 15–20% for practical instructions. Do not repeat the same pair of operations in more than three scenes. Cite actual experiments; never invent retention percentages or brain localization to populate a visual zone.
- Within one authored setting, returning full-scene shots reuse the established base via `based_on`. Preserve room geometry, windows, furniture and props. Include an expression lock in `preserve`, or declare emotional shifts explicitly in `change` / set `allow_expression_shift: true`. Independent locations need independent compositions.
- Close-up hands keep simplified white four-finger cartoon anatomy and restrained charcoal outlines. Empty `allowed_text` means abstract wavy ink lines only on papers/books, without words, titles or equations.
- `transition: cut` describes the edit; `camera_motion` describes movement inside the frame. Use 4-direction semantic zoom/pan/punch motions (`push_in`, `pan_right`, `pull_back`, `pan_left`) without consecutive duplicates (`entropy >= 1.5` bits). Diagram/white-card comparison beats may use intentional `hold`.
- The direction diversity above describes authored intent, not mandatory visible motion on every image. Calm playback in `renderer/camera.mjs` takes priority: hold independent shots shorter than 2.4s and all macro/diagram shots; map pans, slides and shake to steady framing; turn punch into a restrained push. Use at most 1.5% zoom with peak scale velocity <= 0.004/s (including overscan), and allow at least 4s of camera rest before another moving composition. Consecutive variations/reused images share one camera clock, focal origin and portrait framing mode. Preserve the outgoing shot's own camera during dissolves. Full-frame playback never enables line-boil displacement.
- Overscan `1.045` crops about 2.15% from each edge at rest. It provides a framing margin, not a guarantee that provider marks disappear. Inspect real edge pixels over the entire motion range before claiming removal.

# Verification

Run `sys/tests/test_full_frame_pipeline.py`, `sys/tests/test_full_frame_upgrade.py`, and `sys/tests/test_anti_formulaic_storytelling.py` plus the existing format, story, remote-render and cadence checks through `./pipeline run`. Inspect real Flow outputs and a remotely rendered WAV/MP4 before claiming emotional continuity, text cleanliness, acoustic sync or visual acceptance. Fixtures and estimated timelines prove contracts only.
