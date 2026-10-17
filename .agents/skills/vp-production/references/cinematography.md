# Cinematography and Shot Grammar for Full-Frame Explainer Videos (`full_frame_v1`)

Visual standards, shot framing grammar, and cutting pace for full-frame explainer videos (`flow_prompts 1.3.0`), adapting composition to target aspect ratios (`9:16`, `16:9`) specified in `sys/format_profiles.py`. Read before planning visual beats and prompt authoring.

## 1. Mandatory Three-Step Process (Flash-Agent Simplified)
1. **Author natural sentence-beat pairs**: Pair each spoken sentence with one concrete visual action (`shot_type|visual_action`), alternating short punchy sentences (`3–8` words) with explanatory sentences (`15–24` words).
2. **Select full-frame `shot_type`**: Choose from `full_scene`, `macro_prop`, `variation`, `white_card`, or `white_isolated`. Never guess manual `(x, y)` coordinates—code automatically centers `focus` safely. Semantic camera intent remains diverse; calm playback decides whether visible movement is warranted.
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

| Scene Effect | Operating Mechanism | Recommended Use Case |
|---|---|---|
| `cut` / `hold` | `transition: cut` switches beats cleanly (with automatic 85ms micro-dissolve on `variation` shots); `hold` keeps camera motionless for dense diagrams. | Standard beat cuts and diagram inspection. |
| `zoom_in` / `zoom_out` | Calm playback: at most 1.5% scale change, peak velocity <= 0.004/s including overscan; smooth start/stop. | Move only on a composition held >= 2.4s, with at least 4s of camera rest between moving compositions. |
| `punch_in` | Restrained push with the same speed budget; no spring or shake. | Convey surprise through the image and narration rather than an abrupt size jump. |
| `pan_left` / `pan_right` | Intent is retained; calm playback holds the image steady. | Contrast through authored composition and edits. |
| `slide_left` | Steady image cut in calm playback; no Whip pan or slide. | Topic changes use clean cuts. |
| `shake` | Steady framing in full-frame playback; legacy Perlin helpers are not applied. | Convey impact through the depicted action. |

- **Continuity and breathing room**: Consecutive variations and repeated images share one camera clock, focal origin and portrait framing mode. Macro shots and white cards hold steady. During a dissolve the outgoing image retains its own framing. Global line-boil flags never displace full-frame images. Image beat density and narration timing remain independent of camera motion.

- **Hand-drawn call-outs inside the AI art**: Request `"red hand-drawn circle or arrow pointing at..."` directly inside the image description when needed; **never** add external React/SVG floating callouts or coordinate overlays on top of the video.
- **Clean papers & books**: When `allowed_text` is empty, books and sheets must contain only abstract wavy ink lines—never invented words, titles, or equations.
- **Renderer boundaries**: **Do not select multi-layer 3D parallax (Parallax 3D đa lớp)** or cutout sticker layers (`layers[]`) because standard rendering uses one complete 2D full-frame bitmap per beat. Whip pan is natively supported via `slide_left` with dynamic motion blur and inertia.
