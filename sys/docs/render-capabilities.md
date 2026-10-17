# Renderer Capabilities

This document records the actual technical capabilities of the Remotion renderer (`sys/renderer/index.tsx`, `render.mjs`) in the Video Pilot system.

Unlike the long-term stable cinematic grammar in `.agents/skills/vp-production/references/cinematography.md`, this document evolves with engine and renderer upgrades.

---

## 1. Directly Supported Features in Renderer Source Code (Remotion Engine)

Playback uses the calm composition plan in `sys/renderer/camera.mjs` and the image layers in `sys/renderer/index.tsx`. Existing `effect`, `camera_motion` and `focus` fields remain readable; authored direction diversity does not force visible movement on each beat. The initial comfort thresholds below are engineering defaults pending remote MP4 visual acceptance. Paths are evaluated from `useCurrentFrame()` with clamped progress, following [Remotion animation guidance](https://www.remotion.dev/docs/animating-properties).

| Effect / Technique | Status in Code | Mechanism & Parameters | Usage Guidance |
|---|---|---|---|
| **Hard cut (`cut` / `hold`)** | Supported | Switches images at beat `at`; variations use an 85ms micro-dissolve while sharing camera time and origin. `hold` locks the composition. | Fast image edits do not require fast camera movement. |
| **Cross-fade (`fade` / Dissolve)** | Supported | New image layer transitions opacity from 0 to 1 over up to 0.3s (or half beat duration), overlaying previous frame. | Suitable for time passage, flashbacks, or softening scene cuts. |
| **Slide / Whip Pan (`slide_left`)** | Steady in calm playback | Legacy intent remains readable; the full-frame renderer switches images without lateral travel or blur. | Use clean cuts for topic changes. |
| **Smooth Zoom In (`zoom_in` / `push_in`)** | Supported, budgeted | One composition-level smoothstep path, at most 1.5% zoom; peak scale velocity <= 0.004/s including overscan. | Compositions >= 2.4s only, with at least 4s rest before another moving composition. |
| **Smooth Zoom Out (`zoom_out` / `pull_back`)** | Supported, budgeted | Same speed budget and smooth endpoint velocities as push-in. | Reveal context gently; never reset the path on a variation cut. |
| **Punch Zoom (`punch_in`)** | Restrained push | Uses the calm zoom path, without spring, size snap or impact shake. | Let narration and depicted action carry emphasis. |
| **Horizontal Pan (`pan_left` / `pan_right`)** | Steady in calm playback | Authored intent is preserved; no lateral image translation. | Use composition and cuts to compare subjects. |
| **Auto Ken Burns** | Replaced by calm playback | Unknown/no-intent shots hold steady; independent shots shorter than 2.4s, macro shots and white cards hold. | Camera movement is optional. Image beat timing stays unchanged. |
| **Focal Center (`focus`)** | Supported | Safely clamps existing normalized focus; variations/reused images retain the base composition origin and portrait framing mode. | Do not invent manual coordinates. Outgoing dissolves keep their own framing. |
| **Camera Shake (`shake`)** | Steady in full-frame playback | Legacy Perlin helpers remain available, but are not applied to full-frame images. | Avoid whole-frame vibration. |
| **Line Boil Effect (`line_boil`)** | Disabled for full-frame playback | Global and per-beat flags cannot enable displacement on full-frame imagery; dormant layered assets retain legacy handling. | Do not distort the entire illustration to simulate character animation. |
| **Draw-on Transition (`draw_on`)** | Supported | Soft transition mask `maskImage: linear-gradient(135deg, ...)` sweeping diagonally from top-left to bottom-right across `draw_duration` (default 1.3s), accompanied by leading pencil icon `✏️`. Triggered via `draw_on: true` or `effect: 'draw_on'`. | Eye-catching scene openings, drawing sketches in real time with opening narrator lines. |
| **Cinematic Overlays** | Supported | Subtle 4-corner vignette shading and film grain across the frame. | Blends 2D sketches into visual space, eliminating raw digital image feel. |
| **Kinetic Keyword Typography** | Supported | Tokenizes captions, automatically highlighting target vocabulary (`target_word`) or uppercase English words in glowing yellow `#FACC15` with black drop shadows. | Highlights key terms without requiring static text drawn into illustrations. |
| **Interactive Practice Counter** | Supported | Floating countdown bubble "3... 2... 1... 🎙️" automatically shown when cue has `practice` flag or contains repeat prompts. | Engages learners without manual per-frame compositing. |
| **Layered Cut-out Motion (`scene.layers`)** | **Deprecated for new jobs** | Standard authoring and render validation accept full-frame `kind: "scene"` images with narration-anchored `beats[]`; `kind: "background"`, `kind: "sticker"`, and non-empty `layers[]` are rejected. `matte_sticker.py` is not bundled or invoked. | Use multi-beat full-frame scene images and `based_on` variations for continuity. Existing renderer code is retained only as dormant legacy code. |

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
| **True 3D Spatial Parallax / 3D Mesh Warping** | **Unsupported (Chưa hỗ trợ)**. The renderer does not support true 3D spatial camera simulation or 3D mesh warping. | Use semantic camera movement between full-frame images or illustrate compositions with deep 2D perspective. |
