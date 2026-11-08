# Storyboard and Full-frame Visual Beats

For every new image, use [the light 2D visual contract](visual-style.md) locked to `1.7.0 Nguệch Ngoạc` (`sys/visual_style.py`: 7-color palette, pure-white bald stickman, `#3B82C4` shirt, thin black wire arms ending in round white circle hands, >=60% negative space).

## Beat & Image Planning Checklist (mandatory before prompt authoring)
- Does the cold open use enough narration-anchored full-frame images to establish the narrative conflict?
- Are all visual holds aligned with `sys/visual_pacing.py`?
  - For `long_16x9`: 4 pacing modes (Rapid `1.2–2.0s`, Normal `2.2–3.2s`, Slow `3.5–4.8s`, Hold `5.0–6.5s`).
  - For `short_9x16`: Rapid cuts (`0.9–1.8s`), normal (`2–3.5s`), average `2–3s`.
- Captions must not obscure key image focal points (reserve the bottom `18%` safe zone on `short_9x16` for kinetic 1-word subtitles; full-bleed `None` clearance on unsubtitled `long_16x9`).
- Setting descriptions must be strictly $\le 8$ words (space + lighting only; strictly no prop or furniture enumeration).
- Visual breathing room: verify that at least 30% of beats in every 10-beat sequence are character-free rest frames (`still_life`, `environment`, character-free `white_card`), and human figures appear in at most 4 consecutive beats.
- Author image prompts only after the beat plan is finalized.

Before choosing framing/beats, review [cinematography](cinematography.md) to apply framing grammar and [render-capabilities](../../../../sys/docs/render-capabilities.md) to check available effects.

Give each image a clear cognitive function: **Academic Pyramid (9 research sources)**, **Original Theory vs. Mechanical Copying Scale**, **Q1 Decision Flowchart (`Question → Gap → Method → Evidence → Paper`)**, **Research Gap Matrix**, direct contrast, or loop payoff. Prohibit mechanical clichés (`ERR-20261011-03`: no brain cutaways, abacuses, pipe-valves, iron anchors, or raw split-screens).

Use a palette of complete `kind: "scene"` images across all 10 shot types:
- `full_scene`
- `variation`
- `macro_prop`
- `white_card`
- `white_isolated`
- `still_life`
- `environment`
- `concept_metaphor`
- `visual_diagram`
- `cutaway_detail`

The figure, furniture, props, and environment belong to the same composition. Do not create separate background/sticker assets or add a sticker halo.

Character/style reference is optional and only guides drawing style. Use Base reference for shot continuity and set `based_on`, `preserve`, and `change` for a variation that stays in the same place. Use an independent image for a scene cut or a substantial camera change. Flow CDP (`sys/flow_cdp/`) is the sole image provider (never draw mocks with PIL).
