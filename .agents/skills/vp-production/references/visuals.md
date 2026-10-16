# Storyboard and Full-frame Visual Beats

## Beat & Image Planning Checklist (mandatory before prompt authoring)
- Does the cold open use enough narration-anchored full-frame images to show each important object or action? As a starting target, use about 8–9 images in the first 12–12.5 seconds and about 4 in the first 5 seconds when the narration supports it.
- Are all chosen effects supported in [render-capabilities](../../../../sys/docs/render-capabilities.md)? Keep body holds within `0.83s–3.80s`; inspect actual cut timing against the WAV.
- Captions must not obscure key image focal points (reserve the bottom `18%` safe zone on `short_9x16` when `subtitles: true`; full-bleed `None` clearance on unsubtitled `long_16x9`).
- Author image prompts only after the beat plan is finalized.

Before choosing framing/beats, review [cinematography](cinematography.md) to apply framing grammar and [render-capabilities](../../../../sys/docs/render-capabilities.md) to check available effects.

Give each image a clear cognitive function: **Academic Pyramid (9 research sources)**, **Original Theory vs. Mechanical Copying Scale**, **Q1 Decision Flowchart (`Question → Gap → Method → Evidence → Paper`)**, **Research Gap Matrix**, direct contrast, or loop payoff. Prohibit mechanical clichés (`ERR-20261011-03`: no brain cutaways, abacuses, pipe-valves, iron anchors, or raw split-screens).

Use a palette of complete `kind: "scene"` images: macro prop close-ups, wide scenes with figures physically grounded in the setting, in-place variations, and white concept cards. The figure, furniture, props, and environment belong to the same composition. Do not create separate background/sticker assets or add a sticker halo.

Character/style reference is optional and only guides drawing style. Use Base reference for shot continuity and set `based_on`, `preserve`, and `change` for a variation that stays in the same place. Use an independent image for a scene cut or a substantial camera change. Do not force a fixed rotation of shot types. Flow CDP (`sys/flow_cdp/`) is the sole image provider (never draw mocks with PIL).
