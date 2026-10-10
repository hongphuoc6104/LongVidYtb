# Cinematography and Shot Grammar for Explainer Videos

Visual standards, shot framing grammar, and cutting pace for explainer videos, adapting composition to target aspect ratios (e.g. 9:16, 16:9) specified in the job brief. Read before planning visual beats and prompt authoring.

## 1. Mandatory Three-Step Process
1. **Analyze dialogue pacing**: Identify target vocabulary anchors, vocal emphasis, and emotional tone.
2. **Select framing grammar & effects**: Determine shot size, camera angle, focal eye-trace, and transitions compatible with the renderer.
3. **Author prompts for Flow**: Generate static illustrations adhering strictly to chosen framing and anonymous stick-figure standards (bright background, bold outlines, dedicated caption safe zone).

---

## 2. Frame Composition & Safe Margins
Composition adapts dynamically to the target aspect ratio configured in the job brief:
- **Vertical Framing (e.g., 9:16 portrait)**:
  - **Top 30% (Upper Tier)**: Character head, facial expressions, speech bubbles, question/emotion icons.
  - **Middle 40% (Golden Zone)**: Primary action, crucial props, character interactions. Viewers' eyes rest here most often.
  - **Bottom 30% (Lower Tier - Safe Zone)**: Reserved strictly for dynamic captions and platform UI overlays. **Forbidden** to place key illustrative details or lesson text in this zone.
- **Horizontal Framing (e.g., 16:9 landscape)**:
  - Rule-of-thirds composition with focal action centered; lower area cleared for subtitle overlay.
- **Safe Margins**: Maintain adequate margins on lateral edges (at least 80px). Preserve eye-trace continuity between consecutive scenes.

---

## 3. Standard Shot Grammar Table
| Shot Framing / Camera Angle | Purpose & Screen Placement | Practical Production Application |
|---|---|---|
| **Establishing shot** | Wide establishing view; stacked scenery according to target aspect ratio. | Scene transitions, establishing character environment. |
| **Medium / OTS** | Medium shot or over-the-shoulder conversation; foreground figure in lower corner, speaking partner in upper/opposite half. | Dialogue, explanation, interaction between two characters. |
| **Close-up / Extreme close-up** | Close-up / extreme close-up; center character face/mouth at focal screen area. | Shock/joy/sorrow expressions, pronunciation of target vocabulary. |
| **POV shot** | First-person point of view; stick hands or held prop extending from screen edge into center. | Immersion, hands-on manipulation of objects. |
| **High / Low / Dutch angle** | High angle (looking down), low angle (looking up), or 15–25° tilted horizon. | Convey feeling small/pressured (high), massive (low), or disoriented/quirky (Dutch). |

---

## 4. Transitions & Renderer-Compatible Effects
Refer to detailed parameters in [render-capabilities](../../../../sys/docs/render-capabilities.md).

| Scene Effect | Operating Mechanism | Recommended Use Case |
|---|---|---|
| `cut` / `hold` | Hard cut to new image immediately. `hold` keeps camera completely motionless. | Match cut, Jump cut, Smash cut, fast pacing, or preserving diagrams. |
| `fade` | Dissolve opacity transition up to 0.3s overlaying previous image. | Passage of time, flashbacks, softening scene transitions. |
| `slide_left` | Slides new image horizontally right-to-left within 0.3s. | Page turns, advancing to a new topic or narrative section. |
| `zoom_in` / `zoom_out` | Smoothly scales 1.0 $\to$ 1.08 or scales down 1.08 $\to$ 1.0. | Push-in (focusing on vocabulary) or Pull-out (revealing context). |
| `punch_in` | Sudden snap zoom 1.25x in 0.35s with subtle vibration. | Emphasizes sudden discovery, shock, or eureka moments. |
| `pan_left` / `pan_right` | Subtle 3% horizontal shift at 1.06 scale. | Sweeping across wide landscapes or reviewing multiple horizontal elements. |
| Auto Ken Burns | Cycles zoom in $\to$ pan $\to$ zoom out when effect is unset. | Prevents dead or static frames (Never a static frame). |
| `focus: {x, y}` | Normalized focal center coordinates (default `{x: 0.5, y: 0.42}`). | Directs zoom/pan motions accurately onto character faces or focal props. |
| `shake` | 55Hz screen shake decaying over 0.28s. | Impact, sudden fright, explosion, or forceful knock. |

- **L-cut / J-cut**: Narration runs continuously; offset image beat timestamps (`at`) by 0.2s - 0.5s relative to dialogue start.
- **Hand-drawn call-outs**: Request "red hand-drawn circle/arrow" directly in prompt adhering to brand tolerance.
- **Highlighted vocabulary**: Captions automatically highlight target words (`target_word`) in vibrant yellow `#FACC15`; do not draw static text on images.
- **Renderer boundaries**: **Do not select multi-layer 3D parallax (Parallax 3D đa lớp)** because standard single-frame rendering expects a single 2D bitmap per beat (unless using `scene.layers`). Whip pan is natively supported via `slide_left` with dynamic motion blur and inertia.
