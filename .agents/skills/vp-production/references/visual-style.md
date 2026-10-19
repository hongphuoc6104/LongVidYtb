# Light, moderately simplified 2D stick-figure images

Approved user direction, 2026-10-19. New jobs use prompt registry `1.5.0`; do not rewrite historical pins or image revisions.

- Keep anonymous round-white-headed stick figures, expressive simple faces, thin limbs and simplified four-finger cartoon hands. Fine-to-medium charcoal contours replace heavy black marker borders.
- Show a clear focal action. Keep only the background cues needed to recognize the requested place; reduce small interior lines, repeated shelves, cables, charts and decorative props. Background contours are finer, lighter and lower-contrast than the focal subject.
- Use natural earth-toned foundations (`ochre`, `sage green`, `warm gray`, `sky blue`) replacing pastel descriptors, with warm-cool temperature contrast (warm highlights, cool blue-gray shadows), a 60-30-10 color distribution ratio, and explicit negative space (at least 25–35% calm open canvas). Avoid large near-black fills in walls, clothes and furniture; retain small dark facial features and readable focal edges.
- Choose palette, role costume, time of day and setting naturally for the story. No fixed room, recurring outfit color or universal beige/teal palette. Keep night cues with soft ambient fill; do not turn every scene into daytime.
- Setting descriptions must be strictly $\le 8$ words specifying only physical space and lighting (strictly no prop or furniture enumeration).
- Incorporate visual breathing room to prevent character fatigue: interleave character-free rest shots (`still_life` on objects/books/instruments without figures or hands; `environment` on wide landscapes/rooms without figures). Enforce at least 30% character-free beats per 10-beat sequence and at most 4 consecutive character beats.
- Create interest through gestures, expressions, composition and selective emphasis rather than extra objects, neon glow or hard spotlights.
- New style references must demonstrate this lighter treatment. Do not reuse a heavy-line dark-clothing reference as the default for new jobs. Base variations preserve declared geometry, costumes, props and expression; generate the new light Base before its variations.
- Keep full-bleed artwork, exact allowed lettering and the existing caption/render contracts. The remote renderer preserves this profile's image colors without vignette/film-grain overlays; subtitle contrast remains independent.

Author English scene prose about who does what, with only necessary environmental cues. Import authoring defaults from `sys/visual_style.py`, which reads the versioned registry. Prompt text and unit tests prove contracts; inspect real Flow outputs before claiming the style has succeeded.
