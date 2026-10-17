# Cinematography and Shot Grammar for Full-Frame Explainer Videos (`full_frame_v1`)

Visual standards, shot framing grammar, and cutting pace for full-frame explainer videos (`flow_prompts 1.3.0`), adapting composition to target aspect ratios (`9:16`, `16:9`) specified in `sys/format_profiles.py`. Read before planning visual beats and prompt authoring.

## 1. Mandatory Three-Step Process (Flash-Agent Simplified)
1. **Author natural sentence-beat pairs**: Pair each spoken sentence with one concrete visual action (`shot_type|visual_action`), alternating short punchy sentences (`3–8` words) with explanatory sentences (`15–24` words).
2. **Select full-frame `shot_type`**: Choose from `full_scene`, `macro_prop`, `variation`, `white_card`, or `white_isolated`. Never guess manual `(x, y)` coordinates—code automatically centers `focus` safely and assigns non-repeating semantic camera movements (`select_semantic_camera_effect`).
3. **Author full-bleed prompts for Flow**: Generate one integrated 2D illustration per beat where anonymous stick figures, furniture, and props belong naturally to the same physical environment (no detached stickers, no white cutout borders).

---

## 2. Frame Composition & Safe Margins (`sys/format_profiles.py`)
Composition adapts dynamically to the target `format_profile` configured in the job brief:
- **Horizontal Framing (`long_16x9` — `1920x1080`, `full_frame_v1`)**:
  - **100% Full-Bleed Canvas (`caption_clearance = null`)**: Landscape videos use external `.srt` (`subtitles: false` by default). Never instruct the AI to leave a blank bottom band.
  - **Setting Diversity & Continuity**: Use at most 2 consecutive scenes in the same physical room; across $\ge 10$ scenes no single setting may exceed 30%. Within one room, use `variation` (`based_on`) with `Expression lock` to animate character posture changes smoothly.
- **Vertical Framing (`short_9x16` — `1080x1920`)**:
  - **Top & Middle Zone (Top 82%)**: Compose character posture, expressions, action and focal props together in the physical scene, or use `reframe_mode: true` from a `16:9` master.
  - **Bottom 18% (`caption_clearance = 0.18`)**: Reserved for burn-in dynamic captions (`max_line_chars = 28`).

---

## 3. Standard Full-Frame Shot Types (`flow_prompts 1.3.0`)
| Shot Type | Purpose & Composition Rule | Practical Production Application |
|---|---|---|
| **`full_scene`** | Integrated physical environment with anonymous stick figure(s), furniture, and props drawn together. | Establishing rooms, experiments, lecture halls, cafes, or metaphorical landscapes. |
| **`variation`** | Attached to prior `based_on` image; preserves exact room geometry, camera, and facial expression (`Expression lock`), changing only the declared action/prop. | Flipbook-style character pose changes (e.g., closing a book, lifting a pen) within the same room. |
| **`macro_prop`** | Close-up on a concrete object, hand action, or diagram detail (simplified white four-finger cartoon hands with black outlines). | Highlighting a textbook, correcting an error with a red pen, inspecting a clock or gauge. |
| **`white_card`** | Clean pure white `#FFFFFF` concept card with no room, floor, or scenery; renders only the requested icon/diagram and `allowed_text`. | Isolating a core paradox, comparison icon, or minimal conceptual diagram. |
| **`white_isolated`** | Clean pure white `#FFFFFF` field with the requested figure or object integrated into a complete frame (no sticker border). | Single-subject conceptual emphasis without environmental distractions. |

---

## 4. Transitions & Renderer-Compatible Effects
Refer to detailed parameters in [render-capabilities](../../../../sys/docs/render-capabilities.md).

| Scene Effect | Operating Mechanism (`computeCinematicCameraVector` in `camera.mjs`) | Recommended Use Case & Flash Agent Rule |
|---|---|---|
| `auto` / `cut` / `hold` | Resolves `auto`/`cut` into a **Scene-Continuous Weyl Camera Glide** (with 75ms optical soft-cut between in-scene beats); `hold` keeps camera still for dense diagrams. | **Default for Gemini Flash**: leave `effect: "auto"` (or `"cut"`) and let code compute non-repeating vectors. |
| `zoom_in` / `zoom_out` | Continuous scene-level dolly (`~3.4%–5.2%` adaptive scale + 2D diagonal parallax drift via Weyl golden-ratio sequence $\phi_1, \phi_2, \phi_3$) with ease-in-out inertia. | Focusing on action/detail (`zoom_in`) or revealing context (`zoom_out`). Never repeats identical numbers across scenes. |
| `punch_in` | Critically damped (`damping: 28`) forward push-in accent (`+1.6%` on top of scene dolly, zero backward bounce, zero screen shake). | **Max 1 per scene**: reserve strictly for Opening Hook (`SC01`) or a single eureka/climax beat (`!`). |
| `pan_left` / `pan_right` | Coupled horizontal tracking (`~1.05%–1.60%`) + subtle micro-dolly (`1.4%–2.6%`) across the full scene duration. | Contrasting two groups, timeline progression, or wide environments. |
| `slide_left` | Bezier horizontal slide with directional motion blur (Whip pan). | Fast topic transitions (use sparingly, max 1–2 per chapter). |
| `shake` | Subtle Perlin camera vibration decaying over 0.28s (`<= 5px`). | Physical impact only; never attach `shake` to ordinary numbers or speech beats. |

- **Hand-drawn call-outs inside the AI art**: Request `"red hand-drawn circle or arrow pointing at..."` directly inside the image description when needed; **never** add external React/SVG floating callouts or coordinate overlays on top of the video.
- **Clean papers & books**: When `allowed_text` is empty, books and sheets must contain only abstract wavy ink lines—never invented words, titles, or equations.
- **Renderer boundaries**: **Do not select multi-layer 3D parallax (Parallax 3D đa lớp)** or cutout sticker layers (`layers[]`) because standard rendering uses one complete 2D full-frame bitmap per beat. Whip pan is natively supported via `slide_left` with dynamic motion blur and inertia.
