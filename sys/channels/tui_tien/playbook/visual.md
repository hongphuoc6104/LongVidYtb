# Visual Grammar & FX Lock — Túi Tiền Biết Nói (`tui_tien`)

## 1. Visual Style Bible & Flow Prompt Lock
- **Archetype Track:** `archetype_4_doodle_explainer` (consult [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md) and [vp-channel-registry](../../../../.agents/skills/vp-channel-registry/SKILL.md))
- **Master Style Lock:** Hand-drawn 2D notebook-ledger explainer illustration: wobbly black marker outlines (#1F1F1F) on a flat warm grid-paper canvas (#FAF6E9 with faint #E3DCC8 square grid), flat unshaded fills in money green (#2F9E5B), coin gold (#F2C14E), loss red (#D64545) and ink navy (#24364F); hand-drawn bar charts, price tags and VND banknotes drawn as simple flat shapes; orthographic 2D, generous empty grid space, no gradients, no photorealism, no 3D., crisp optical clarity, deep-focus lens depth, dramatic directional key lighting, clean focal subject with >=60% negative space, zero text in frame.
- **Palette & Thumbnail Rule:** #FAF6E9, #2F9E5B, #F2C14E, #D64545, #24364F | Thumbnail: One big VND number or price tag + shocked stickman, hand-lettered on grid paper.
- **Subject Physics:** Tactile real-world consumer product, crisp polymer banknote, leather, glass, and checkout hardware physics, smooth commercial studio lighting specular reflections, realistic weight transfer and clean f/2.0 optical rack-focus
- **Wardrobe / Outfit Cue:** Flat coin-gold (#F2C14E) T-shirt and navy (#24364F) trousers, no folds, no shading
- **Continuity Anchor:** WSJ Consumer Economics & Two Cents realistic 35mm tabletop cinematography with crisp commercial keylight, f/2.0 optical depth-of-field, and tactile anti-morph physical dynamics across diverse consumer environments, strictly zero readable text, words, or price digits
- **Forbidden Visual Artifacts:** ['flat 2D cartoon paper cutouts', 'off-topic grocery items in non-grocery scenes', 'gibberish printed letters', 'warping credit card logos', 'cartoon money bags']

## 2. Short V4 Render & Banner Specifications (`1440x2560@30fps`)
- **Dual-Model Video Router:** Route character/lighting jumps via `veo_3_1_lite` Seam Mode (`10c`) and continuous same-cast transitions via `omni_flash` (`macaron_cookie` Frame-Link).
- **Heroic Banner Palette (`>= 132px`, `anchor_y=150`, `<= 4` UPPERCASE words):**
  - Fill Bar RGBA: `(42, 108, 184, 245)`
  - Accent RGBA: `(245, 158, 11, 255)`
- **Camera Grammar:** ['smooth 35mm commercial dolly push-in', 'eye-level lateral tabletop tracking pass', 'clean macro product rack-focus']
- **Watermark SSOT:** `watermark_150x150.png` pinned bottom-right at `W-w-36:H-h-36` (`delogo` enabled only when Flow corner mark detected).
