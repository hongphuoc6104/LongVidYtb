# Script, Storyboard and Planning Specs

## 1. Scope & Workflow
- **Contract source:** Read job contract/profile and references: [script](../../.agents/skills/vp-production/references/script.md), [narration](../../.agents/skills/vp-production/references/narration-style.md) and [visuals](../../.agents/skills/vp-production/references/visuals.md).
- **Workflow modes:** Review mode stops at `outline` and `dialogue` checkpoints; Auto mode proceeds without human review.
- **Scene counts:** Dynamic. Choose scene count based on meaning, causality, and payoff; no fixed image/beat quotas.

## 2. Script & Narration
- **Language:** Narration, visible coverage, and anchors must be in natural, accessible English (B1+).
- **Freezing:** Lock narration before compiling quotes, visual coverage, or timeline anchors.
- **Quotes:** Verbatim from the exact target scene.
- **Revisions:** Narration edits must go through versioned rejections/new revisions (`reject` / new revision); never modify snapshots in-place.

## 3. Visuals & Storyboard
- **Function:** Every frame must have a clear visual function (action, visible state, or diagram).
- **Visual Cast (Anonymous Stick Figures):**
  - Prompt registry `1.1.0+`, channel profile v5: All people are **anonymous stick figures** (large round white head with thick black outline, solid-black dot/oval eyes, stick limbs, exactly one torso).
  - **No main character, recurring protagonist, or presenter inside scenes.** Roles and identities arise strictly from scene-specific costume, props, hair, or educational context.
  - Style references guide drawing style only. Legacy character assets (CH01) are permanently retired.
- **Continuity:** Use `Base reference` to inherit shot/background continuity across state changes; independent shots generate independently.
- **Verification:** Actual image inspection required; prompt text and IDs do not prove visual compliance.

## 4. Audio, Subtitles & Timing
- **Timing:** Drive timeline cuts using measured WAV audio length; do not rely on character-count estimates. Anchor interpolation is not word alignment.
- **Subtitles:** At most 2 readable lines with safe margins adapted to the target aspect ratio.
- **Effects:** Use only supported camera/transition effects (`cut`, `hold`, `fade`, `slide_left`, `zoom_in`, `zoom_out`, `punch_in`, `pan_left`, `pan_right`, `shake`) according to `render-capabilities.md`.

## 5. Execution Commands
- **Submit outline/dialogue:**
  `python3 sys/pilot.py author <JOB> outline|dialogue --data <PATH> --source <TEXT>`
- **Run/Resume pipeline:**
  `python3 sys/pilot.py run <JOB>` or `python3 sys/pilot.py resume <JOB>`

*(Note: The [prior guide](legacy/story-planning-before-normalization.md) is historical, not current mode policy.)*
