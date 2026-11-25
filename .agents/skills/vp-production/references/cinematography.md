# Cinematography and Shot Grammar for Full-Frame Explainer Videos (`full_frame_v1`)

Visual standards, shot framing grammar, and cutting pace for full-frame explainer videos (`flow_prompts 1.7.0`), adapting composition to target aspect ratios (`9:16`, `16:9`) specified in `sys/format_profiles.py`. Read before planning visual beats and prompt authoring.

## 1. Mandatory Process & Style Lock (`1.7.0 Nguệch Ngoạc`)
1. **Author natural sentence-beat pairs**: Pair each spoken sentence with one concrete visual action (`shot_type|visual_action`), alternating short punchy sentences (`3–8` words) with explanatory sentences (`15–24` words).
2. **Lock 2D Doodle Style (`1.7.0 Nguệch Ngoạc`)**: Pure-white (`#FFFFFF`) bald circle head, bold pitch-black outline, solid black dot eyes low on the face, single-stroke eyebrows/mouth, no nose/ears, thin single-stroke solid-black wire arms ending in round white circle hands, and flat cerulean-blue (`#3B82C4`) shirt.
3. **Select from 10 standard shot types**: Choose from all 10 supported shot types without guessing manual coordinates. Camera moves and cuts are executed natively via Colab Tesla T4 `FFmpeg h264_nvenc`.

---

## 2. Frame Composition & Visual Pacing (`sys/format_profiles.py`)
Composition adapts dynamically to the target `format_profile` configured in the job brief:
- **Horizontal Framing (`long_16x9` — `1920x1080`)**:
  - **100% Full-Bleed Canvas (`caption_clearance = null`)**: Landscape videos use external sidecar `.srt`.
  - **4 Pacing Modes**: Rapid (`1.2–2.0s`), Normal (`2.2–3.2s`), Slow (`3.5–4.8s`), Hold (`5.0–6.5s`). Max 3 consecutive same tempo (fast <=5).
  - **Setting Brevity Invariant**: Setting descriptions must be strictly $\le 8$ words specifying only physical space and ambient lighting. Prop enumeration is forbidden in `setting`.
  - **Visual Breathing Room**: At least 30% of beats in every 10-beat sliding window must be character-free rest shots (`still_life`, `environment`, `white_card`). Never exceed 4 consecutive beats containing human figures.
- **Vertical Framing (`short_9x16` — `1080x1920`)**:
  - **100% Full-Chain Video**: Continuous video clips generated from 11–15 `BELUGA` keyframes.
  - **Top & Middle Zone (Top 82%)**: Character posture, actions and focal props.
  - **Bottom 18% (`caption_clearance = 0.18`)**: Reserved for 1-word Red `#FF3B30` / Yellow `#FFE600` kinetic `.ass` subtitles.

---

## 3. Standard 10 Shot Types (`flow_prompts 1.7.0`)
| Shot Type | Purpose & Composition Rule | Practical Production Application |
|---|---|---|
| **`full_scene`** | Integrated physical environment with anonymous stick figure(s), furniture, and props drawn together. | Establishing rooms, experiments, lecture halls, cafes, or metaphorical landscapes. |
| **`variation`** | Attached to prior `based_on` image; preserves exact room geometry and camera (`Expression lock`), changing only the declared action/prop. | Flipbook-style character pose changes within the same room. |
| **`macro_prop`** | Close-up on a concrete object or hand action (round white circle hands, thin black wire arms). | Highlighting a book, correcting an error with a red pen, inspecting a gauge. |
| **`white_card`** | Clean pure white `#FFFFFF` field with icon/diagram and `allowed_text` (zero card border, zero tape, zero banners). | Isolating a core paradox or minimal conceptual diagram. |
| **`white_isolated`** | Clean pure white `#FFFFFF` field with figure or object integrated into complete frame without background clutter. | Single-subject conceptual emphasis without distractions. |
| **`still_life`** | Character-free close-up or medium focus on physical objects, documents, books, or instruments without human figures. | Resting between character beats; open highlighted textbook, ticking desk clock. |
| **`environment`** | Character-free wide establishing shot of a landscape, room architecture, or outdoor space devoid of figures. | Visual rest and contemplative pacing; wide empty classroom, morning horizon. |
| **`concept_metaphor`** | Pure conceptual visual metaphor embodying a cognitive paradox or cognitive framework. | Visualizing cognitive bias, feedback loops, or invisible market mechanisms. |
| **`visual_diagram`** | Clean hand-drawn flowchart, comparison axis, or matrix diagram on flat canvas. | 3-Tier academic funnel, gap matrices, decision trees, or hypothesis models. |
| **`cutaway_detail`** | Targeted cutaway revealing an unexpected mechanism or overlooked detail. | Zooming in on a crucial hidden footnote, broken instrument wire, or subtle reaction. |

---

## 4. Transitions & Colab Tesla T4 NVENC Rendering
Refer to detailed parameters in [render-capabilities](../../../../sys/docs/render-capabilities.md).

| Scene Effect | Operating Mechanism | Recommended Use Case |
|---|---|---|
| `cut` / `hold` | Switches beats cleanly; `hold` keeps camera motionless for dense diagrams. | Standard beat cuts and diagram inspection. |
| `zoom_in` / `zoom_out` | Continuous zero-snap `zoompan`: continuous smooth function `z='1.06-0.06*(on/N)'` on 1.25x supersampled canvas *(low-density/EN fallback only; high-density `long_16x9` 240–350 states uses static Lanczos frame lock with zero `zoompan`, ERR-20261109-01, unless GPU sub-pixel `float32` 2.5D parallax warehouse mode is explicitly enabled)*. | Reveal context gently without frame jumps. |
| `punch_in` | Restrained push with smooth endpoint velocities; no spring or shake. | Convey surprise through image and narration emphasis. |
| `pan_left` / `pan_right` | Smooth horizontal sweep via analytical coordinates *(disabled on high-density `long_16x9` unless 2.5D parallax warehouse mode is enabled)*. | Contrast through authored composition and edits. |
| `fade` / `xfade` | High-density `long_16x9` locks strictly to optical `xfade=transition=fade` (`0.24s`; zero slide transitions `smoothleft/right/up/down`, ERR-20261109-01). | Soft scene transitions and chapter changes. |

- **Hand-drawn call-outs inside AI art**: Request `"red hand-drawn circle or arrow pointing at..."` directly inside the image description when needed; never add HTML/Remotion floating overlays. When 30fps HUD/diagram overlays are needed for a beat, composite them natively via `sys/fx_warehouse/hud_widgets.py` on Colab Tesla T4 `FFmpeg h264_nvenc`.
- **Clean papers & books**: When `allowed_text` is empty, books and sheets must contain only abstract wavy ink lines—never invented words, titles, or equations.
- **Sole Canonical Engine**: All rendering is performed via Native Colab Tesla T4 `FFmpeg h264_nvenc` with `/dev/shm` parallel chunk processing (zero Remotion/Chromium overhead), `-11.0 LUFS / -1.0 dBTP` audio normalization, `VietNarrator_<channel_id>` on OmniVoice, and bottom-right watermark `W-w-36:H-h-36`.

---

## 5. Modular FX & Audio Warehouse (`sys/fx_warehouse/`)
Refer to [vp-visual-fx](../../vp-visual-fx/SKILL.md) for beat-level camera, VFX, 30fps HUD, and procedural SFX/BGM selection across `sys/fx_warehouse/` (`archetypes.py`, `camera_vfx.py`, `hud_widgets.py`, `audio_sfx_bgm.py`, `selector.py`):
- **5 Niche Archetypes (20 Channels)**: `CHANNEL_ARCHETYPE_MAP` groups all 20 channels into 5 archetypes (`archetype_1_forensic_noir`, `archetype_2_geopolitics_history`, `archetype_3_science_xray`, `archetype_4_doodle_explainer`, `archetype_5_mindful_healing`), pulling dynamically from the shared sub-warehouses per beat via `auto_select_beat_fx(...)` while obeying viewing-comfort guardrails.
- **Non-Forced Bespoke Rule**: If a video's topic or niche requires a visual effect, HUD overlay, or sound stem not yet in the shared catalog, create a bespoke per-video/per-topic spec (`bespoke_hud_spec`, `bespoke_sfx_spec`) instead of forcing an incompatible existing preset, and shard new reusable catalogs into `sys/fx_warehouse/` submodules as the warehouse grows.
