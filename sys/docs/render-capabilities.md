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
| **Smooth Zoom In (`zoom_in`)** | Supported | Scene-continuous 3-DOF dolly (`~3.4%–5.2%` adaptive zoom + 2D diagonal drift via Weyl golden-ratio sequence `computeCinematicCameraVector`) with sine ease-in-out. | Smoothly directs visual focus across the entire scene without resetting on in-scene beat cuts. |
| **Smooth Zoom Out (`zoom_out`)** | Supported | Scene-continuous pull-out (`1.045 -> 1.0` adaptive scale + diagonal drift) with sine ease-in-out. | Gently reveals wider environmental context (pull-out). |
| **Punch Zoom (`punch_in`)** | Supported | Critically damped (`damping: 28`) forward push-in accent (`+1.6%` on top of scene dolly, zero backward bounce, zero screen shake). | Emphasizes opening hook (`SC01`) or key realization without jarring screen shake. |
| **Horizontal Pan (`pan_left` / `pan_right`)** | Supported | Coupled horizontal tracking (`~1.05%–1.60%`) + subtle micro-dolly (`1.4%–2.6%`) across the scene duration. | Panning across wide scenery, timelines, or two-group comparisons. |
| **Weyl Non-Repeating Camera (`auto`)** | Supported | Combines semantic framing selection (`selectSemanticCameraEffect`) with irrational golden-ratio/plastic sequences (`PHI_1, PHI_2, PHI_3`), duration scaling $\sqrt{T/12}$, and `scene.tone` modulation. | Guarantees 100% unique, non-repeating documentary camera trajectories across all scenes. |
| **Focal Center (`focus`)** | Supported | Normalized coordinates `focus: {x, y}` automatically clamped to the safe central viewport (`x: 0.35..0.65`, `y: 0.35..0.58`) with `microRot = 0` (locked horizon). | Prevents model coordinate guesses from zooming into blank corners or tilting 2D architectural lines. |
| **Camera Shake (`shake`)** | Supported | Bounded camera jitter (`<= 5px`) using multi-harmonic Perlin/Simplex noise (`organicNoise`), decaying over 0.28s. | Conveys physical impacts only; normal scenes use subtle `0.9px` tripod breathing. |
| **Line Boil Effect (`line_boil`)** | Supported | Opt-in procedural SVG Displacement Map filter (`<feTurbulence>` + `<feDisplacementMap>`) with 4 rotating seeds at 10 fps (disabled by default on 1080p full-frame scenes). | Optional effect for isolated sketch assets without overloading CPU on full-bleed frames. |
| **Draw-on Transition (`draw_on`)** | Supported | Soft diagonal reveal mask (`maskImage: linear-gradient(135deg, ...)`) restricted strictly to `shot_type === 'white_card'` with zero floating pencil icon overlay. | Clean conceptual card reveals without blind coordinate icons. |
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
