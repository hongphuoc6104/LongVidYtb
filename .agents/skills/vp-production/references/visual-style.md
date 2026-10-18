# Light, moderately simplified 2D stick-figure images

Approved user direction, 2026-10-18. New jobs use prompt registry `1.4.0`; do not rewrite historical pins or image revisions.

- Keep anonymous round-white-headed stick figures, expressive simple faces, thin limbs and simplified four-finger cartoon hands. Fine-to-medium charcoal contours replace heavy black marker borders.
- Show a clear focal action. Keep only the background cues needed to recognize the requested place; reduce small interior lines, repeated shelves, cables, charts and decorative props. Background contours are finer, lighter and lower-contrast than the focal subject.
- Use light-value, gently muted colors and small selective accents. Muted colors alone can still be dark or muddy. Avoid large near-black fills in walls, clothes and furniture; retain small dark facial features and readable focal edges.
- Choose palette, role costume, time of day and setting naturally for the story. No fixed room, recurring outfit color or universal beige/teal palette. Keep night cues with soft ambient fill; do not turn every scene into daytime.
- Aim for recognizable context and visual breathing room, without empty backgrounds, washed-out subjects or arbitrary object/person quotas. Useful metaphors remain allowed when their main relationship reads clearly.
- Create interest through gestures, expressions, composition and selective emphasis rather than extra objects, neon glow or hard spotlights.
- New style references must demonstrate this lighter treatment. Do not reuse a heavy-line dark-clothing reference as the default for new jobs. Base variations preserve declared geometry, costumes, props and expression; generate the new light Base before its variations.
- Keep full-bleed artwork, exact allowed lettering and the existing caption/render contracts. The remote renderer preserves this profile's image colors without vignette/film-grain overlays; subtitle contrast remains independent.

Author English scene prose about who does what, with only necessary environmental cues. Import authoring defaults from `sys/visual_style.py`, which reads the versioned registry. Prompt text and unit tests prove contracts; inspect real Flow outputs before claiming the style has succeeded.
