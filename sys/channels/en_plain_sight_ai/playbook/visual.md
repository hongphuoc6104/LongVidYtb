# Visual Grammar & FX Lock — Scale & Bone (`en_plain_sight_ai`)

## 1. Visual Style Bible & Flow Prompt Lock
- **Archetype Track:** `archetype_3_science_xray` (consult [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md) and [vp-channel-registry](../../../../.agents/skills/vp-channel-registry/SKILL.md))
- **Master Style Lock:** Minimalist flat-vector evolutionary biology explainer in TierZoo and BBC Earth aesthetic on solid flat warm ivory canvas (#F5F2EB). Exactly ONE single hero creature or anatomical adaptation metaphor per frame, rendered with clean flat shapes and smooth organic contours in deep moss green (#2D5A3A) with a vivid terracotta rust (#C85A32) vital accent. Flat 2D orthographic composition, strictly >=75% open negative space, zero textures, zero clutter., crisp optical clarity, deep-focus lens depth, dramatic directional key lighting, clean focal subject with >=60% negative space, zero text in frame.
- **Palette & Thumbnail Rule:** #F5F2EB, #2D5A3A, #C85A32 | Thumbnail: Extreme close-up of single hatching reptile egg or predator silhouette on flat ivory canvas + 2-4 uppercase bold words.
- **Subject Physics:** Iconic 2D minimalist naturalist stickman with clean white (#FFFFFF) circle head, field hat, wire arms, and round circle hands
- **Wardrobe / Outfit Cue:** Flat olive safari vest in deep moss green (#2D5A3A) over simple trousers, zero shading, zero gradients
- **Continuity Anchor:** Preserve camera horizon, lighting key, and hero prop geometry via reference_scene_ids.
- **Forbidden Visual Artifacts:** No overlaid AI text, no watermarks, no cluttered visual slop.

## 2. Short V4 Render & Banner Specifications (`1440x2560@30fps`)
- **Dual-Model Video Router:** Route character/lighting jumps via `veo_3_1_lite` Seam Mode (`10c`) and continuous same-cast transitions via `omni_flash` (`macaron_cookie` Frame-Link).
- **Heroic Banner Palette (`>= 132px`, `anchor_y=150`, `<= 4` UPPERCASE words):**
  - Fill Bar RGBA: `(18, 152, 190, 245)`
  - Accent RGBA: `(255, 216, 102, 255)`
- **Camera Grammar:** Smooth push_in / pull_back / truck_lateral rotation; zero consecutive duplicate moves.
- **Watermark SSOT:** `watermark_150x150.png` pinned bottom-right at `W-w-36:H-h-36` (`delogo` enabled only when Flow corner mark detected).
