# Renderer Capabilities

This document records the actual technical capabilities of the Remotion renderer (`sys/renderer/index.tsx`, `render.mjs`) in the Video Pilot system.

Unlike the long-term stable cinematic grammar in `.agents/skills/vp-production/references/cinematography.md`, this document evolves with engine and renderer upgrades.

---

## 1. Directly Supported Features in Renderer Source Code (Remotion Engine)

These effects are implemented in `sys/renderer/index.tsx` and triggered via the `effect` and `focus` fields of each beat in `scene.images`:

| Effect / Technique | Status in Code | Mechanism & Parameters | Usage Guidance |
|---|---|---|---|
| **Hard cut (`cut` / `hold`)** | Supported | Immediately switches to new image at beat `at`. If `hold`, camera remains static without triggering Ken Burns motion. | Ideal for fast-paced narration, logical explanations, or keeping data charts steady. |
| **Cross-fade (`fade` / Dissolve)** | Supported | New image layer transitions opacity from 0 to 1 over up to 0.3s (or half beat duration), overlaying previous frame. | Suitable for time passage, flashbacks, or softening scene cuts. |
| **Slide / Whip Pan (`slide_left`)** | Supported | Smoothly moves `translateX` from 100% to 0% with easing, combined with velocity-dependent dynamic motion blur (`blur(Xpx, 0px)`) over up to 0.3s. | Page turns, introducing new topics, creating cinematic camera whip transitions. |
| **Smooth Zoom In (`zoom_in`)** | Supported | Scales from 1.0 to 1.08 using non-linear Bezier easing. | Smoothly directs visual focus to vocabulary keywords or core focal points. |
| **Smooth Zoom Out (`zoom_out`)** | Supported | Scales down from 1.08 to 1.0 using non-linear Bezier easing. | Gently reveals wider environmental context (pull-out). |
| **Punch Zoom (`punch_in`)** | Supported | Rapidly snaps to 1.25x scale within first 0.35s via spring dynamics before easing to 1.08x, accompanied by subtle shake. | Emphasizes moments of surprise, realization, shock, or discovery. |
| **Horizontal Pan (`pan_left` / `pan_right`)** | Supported | Fixed at `scale = 1.06`, smoothly moves `translateX` across frame with eased acceleration. | Panning across wide scenery or scanning multiple chore/activity items. |
| **Auto Ken Burns** | Supported | When `effect` is unset and not `hold`: automatically cycles through 4 phases with smooth easing: (1) zoom in $\to$ (2) pan right $\to$ (3) zoom out $\to$ (4) pan left. | Prevents dead or static frames (Never a static frame). |
| **Focal Center (`focus`)** | Supported | Accepts normalized coordinates `focus: {x, y}` (0.0 to 1.0) mapped to `transformOrigin: x% y%`. Default center is `{x: 0.5, y: 0.42}` (adaptable based on framing and target aspect ratio). | Directs zoom and pan motions precisely onto character faces or focal props. |
| **Camera Shake (`shake`)** | Supported | Random camera jitter using Perlin/Simplex noise simulating handheld camera shake, decaying over 0.28s. | Naturally conveys impacts, shocks, explosions, or strong knocks. |
| **Line Boil Effect (`line_boil`)** | Supported | Procedural SVG Displacement Map filter (`<feTurbulence>` + `<feDisplacementMap>`) with 4 rotating seeds at 10 fps. Triggered via `line_boil: true` or `effect: 'line_boil'`. | Animates static stick-figure black lines like *MinutePhysics*, making figures naturally "breathe" with zero AI cost. |
| **Draw-on Transition (`draw_on`)** | Supported | Soft transition mask `maskImage: linear-gradient(135deg, ...)` sweeping diagonally from top-left to bottom-right across `draw_duration` (default 1.3s), accompanied by leading pencil icon `✏️`. Triggered via `draw_on: true` or `effect: 'draw_on'`. | Eye-catching scene openings, drawing sketches in real time with opening narrator lines. |
| **Cinematic Overlays** | Supported | Subtle 4-corner vignette shading and film grain across the frame. | Blends 2D sketches into visual space, eliminating raw digital image feel. |
| **Kinetic Keyword Typography** | Supported | Tokenizes captions, automatically highlighting target vocabulary (`target_word`) or uppercase English words in glowing yellow `#FACC15` with black drop shadows. | Highlights key terms without requiring static text drawn into illustrations. |
| **Interactive Practice Counter** | Supported | Floating countdown bubble "3... 2... 1... 🎙️" automatically shown when cue has `practice` flag or contains repeat prompts. | Engages learners without manual per-frame compositing. |
| **Layered Motion Animation (`scene.layers`)** | Supported | Multi-layer rendering (1 Background + N independent Stickers). Automatically triggers Spring dynamics (`pop`, `pop_wobble`, `bounce`, `drop`, `slide_left`, `spin_grow`), organic `line_boil`, `suck` vortex, `bg_flash`, and `shakeAt` jitter. | Turns static scenes into lively 2.5D animation where figures and props bounce naturally on word beats. Content declared via `scenes[].layers` + `images[].kind` (schema content-v3), prompt registry 1.2.0; stickers matted on Colab via `tools/matte_sticker.py`. See skill `vp-layered-motion`. |

---

## 2. Techniques Handled at Script, Storyboard, and Timeline Level (No Custom Shaders Needed)

These techniques do not require dedicated renderer code changes; they depend on how the director sequences content and timing:

- **Match cut, Jump cut, Smash cut**: Create visual similarity or stark contrast via image content and appropriate beat timing (`at`).
- **L-cut / J-cut**: Narration audio (`narration.wav`) runs continuously on its own audio track; visual scene transitions (`scene.start`) and beat switches (`beat.at`) are deliberately offset 0.2s - 0.5s before or after dialogue to create seamless visual flow.
- **Visual beats & Pacing**: Distribute `images` array in each scene with `at` values aligning with spoken emphasis.
- **B-roll**: Insert cutaway beats or short video clips (both `.mp4` and `.webm` supported via `RemotionVideo`).

---

## 3. Techniques Handled at Prompt and Image Generation Level (Flow Generation)

Camera angles and framing are established in the static image prompt for Flow, not via 3D transformations in the renderer:

- **Shot Framing**: `Establishing shot`, `Close-up`, `Extreme close-up`, `Over-the-shoulder`, `POV shot`.
- **Camera Angles**: `High angle`, `Low angle`, `Dutch angle` (request tilted horizon line in prompt).
- **Hand-drawn Call-outs / Annotations**: Prompt directly for "red hand-drawn circle / arrow pointing at the focal object" in accordance with brand tolerance (avoids artificial mechanical graphic overlays).

---

## 4. Unsupported Techniques

| Technique | Status | Current Recommended Alternative |
|---|---|---|
| **True 3D Spatial Parallax / 3D Mesh Warping** | **Unsupported (Chưa hỗ trợ)**. The renderer supports 2.5D layered animation via `scene.layers`, but does not support true 3D spatial camera simulation or 3D mesh warping. | Use 2.5D layered animation via `scene.layers` (see `vp-layered-motion` skill) or illustrate compositions with deep 2D perspective. |
