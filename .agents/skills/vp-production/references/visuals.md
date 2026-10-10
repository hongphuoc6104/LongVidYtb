# Storyboard and 2D explanatory images

## Beat & Image Planning Checklist (mandatory before prompt authoring)
- How many beats is each dialogue line broken into, and what shot framing is chosen?
- Are all chosen effects supported in [render-capabilities](../../../../sys/docs/render-capabilities.md); for layered video (background + sticker), follow [vp-layered-motion](../../vp-layered-motion/SKILL.md).
- Captions must not obscure key image focal points (reserve the designated lower safe zone strictly for subtitles).
- Author image prompts only after the beat plan is finalized.

Before choosing framing/beats, review [cinematography](cinematography.md) to apply framing grammar and [render-capabilities](../../../../sys/docs/render-capabilities.md) to check available effects.

Give each image a function: situation, action/state change, diagram, contrast, explanation or payoff. Specify what must be noticed, permitted text, shot/attention, and change from the prior frame in existing images/beats fields.

Current channel: hand-drawn bold outlines, flat colors, bright uncluttered background, recognizable props/diagrams. Avoid textured photorealistic natural-history paintings or dark cinematic lighting. Investment is causal storyboard and useful state changes, not decorative detail or image count.

No main character or recurring presenter inside scenes (prompt registry 1.1.0). Cast consists of anonymous stick figures sharing one construction: large round white head with thick black outline, simple dot/oval eyes with expressive brows/mouth, thin black stick limbs, exactly one torso. Each figure's role comes only from the scene (costume, hair, skin tone, age/size, props). Allowed: exaggerated expressions, sweat drops, simple ?, red hand-drawn focus circles/arrows. Not allowed: anime eyes, realistic faces, muscular bodies, doubled torsos, recurring protagonist/narrator.

Character/style reference is optional and only guides drawing style. Use Base reference for shot/background continuity and based_on only when continuity is needed. Independent composition uses independent generation. No prompt/ref ID alone proves identity. Preserve exact allowed text and caption clearance; no forced yellow highlight/screen shake/comic effect. Historical character assets remain only for legacy 1.0.x/v3 jobs.

Flow remains the image provider. Unknown submissions must reconcile/collect on their owning session, never resend under a renamed target. Report real image IDs/version and evidence; visual sampling during development is not a new auto quality gate.

Layered scenes (`layers` declared): one `kind: background` plate without figures plus `kind: sticker` cut-outs on flat pure white; stickers are independent (no based_on) and motion comes from layers, not from new flat frames. Rules/presets: [vp-layered-motion](../../vp-layered-motion/SKILL.md).
