---
name: vp-full-frame-quality
description: Author or repair Video Pilot full-frame visual journeys, continuity and caption/camera contracts. Use with full_frame_v1 jobs, not layered-motion assets.
---

# Full-frame authoring contracts

- New full-frame jobs declare `visual_pacing_profile: full_frame_v1`. Older snapshots remain readable; do not edit saved revisions or journals to migrate them.
- Landscape defaults to external SRT (`subtitles: false`); portrait keeps burn-in subtitles and its renderer safe area. Full-frame image prompts reserve no caption band in either aspect. Keep backgrounds continuous to the canvas edges.
- Vietnamese Adam uses canonical `speed: 1.22` for long videos, `1.26` for short spin-offs. The contract permits `[1.12, 1.38]`; tone modulation is separate. A speed multiplier is not a measured syllable rate.
- A sentence is a TTS boundary. Keep bilingual parts and gaps aligned with sentence chunks. SRT cues never append the opening words of the next sentence.
- Author distinct visual settings: no more than two consecutive scenes in one setting; for ten or more scenes no setting exceeds 30%. Use a causal journey through local experience, empirical evidence, mechanism/metaphor and practical return. These are planning heuristics, not semantic certification.
- Reserve roughly the final 15–20% for practical instructions. Do not repeat the same pair of operations in more than three scenes. Cite actual experiments; never invent retention percentages or brain localization to populate a visual zone.
- Within one authored setting, returning full-scene shots reuse the established base via `based_on`. Preserve room geometry, windows, furniture and props. Include an expression lock in `preserve`; declare emotional shifts explicitly in `change`. Independent locations need independent compositions.
- Close-up hands keep simplified white four-finger cartoon anatomy and black ink outlines. Empty `allowed_text` means abstract wavy ink lines only on papers/books, without words, titles or equations.
- `transition: cut` describes the edit; `camera_motion` describes movement inside the frame. Use semantic zoom/pan/punch motions without consecutive duplicates. Explicit holds require deliberate authoring, not accidental `cut` fallback.
- Overscan `1.045` crops about 2.15% from each edge at rest. It provides a framing margin, not a guarantee that provider marks disappear. Inspect real edge pixels over the entire motion range before claiming removal.

# Verification

Run `sys/tests/test_full_frame_pipeline.py` plus the existing format, story, remote-render and cadence checks through `./pipeline run`. Inspect real Flow outputs and a remotely rendered WAV/MP4 before claiming emotional continuity, text cleanliness, acoustic sync or visual acceptance. Fixtures and estimated timelines prove contracts only.
