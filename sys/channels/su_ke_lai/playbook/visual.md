# Option 1 Visual Grammar — `su_ke_lai_35mm_live_action_v3`

Reference specification for generating 35mm live-action historical battle cinema docudrama frames for **Sử Kể Lại**. Every story frame MUST enforce `allowed_text=None` (`Zero AI-Drawn Text`).

## 1. 5-Block Option 1 Prompt Formula

Construct every image prompt in this exact 5-block order:

1. **Block 1 — Camera & Shot Framing**: Shot scale, angle, lens/perspective, and subject placement from the 5-shot rotation matrix (e.g., `Wide establishing 35mm anamorphic shot, eye-level across a clear-air riverbank embankment...`).
2. **Block 2 — Primary Subject & Action**: Concrete physical action, posture, and period-accurate 10th–11th century Đại Việt or Northern Song combatants/craftspeople/commanders in motion.
3. **Block 3 — Period Costume, Armor & Props**: Explicit tactile materials (lamellar/laminar iron scales, lacquered leather, ramie/hemp tunics, ironwood stakes, bamboo shields, Song halberds) matching the faction vocabulary below.
4. **Block 4 — Environment, Lighting & Atmosphere**: 10th–11th century Red River Delta / northern frontier terrain with **Clear-Air 35mm Anamorphic Cinema Clarity** (`crisp optical clarity, deep-focus 35mm anamorphic depth, dramatic directional sunlight or warm Caravaggio torchlight chiaroscuro, rich tactile armor and terrain detail`), wet mud or rain only when story-specific. Never inject blanket `"river mist"`, `"drifting gunsmoke fog"`, or `"dense battlefield mist"` into default style locks.
5. **Block 5 — Film Stock & Clean-Frame Lock**: `Shot on 35mm Kodak Vision3 500T film, historical battle cinema docudrama, crisp optical clarity, deep-focus 35mm anamorphic depth, dramatic directional sunlight or warm Caravaggio torchlight chiaroscuro, rich tactile armor and terrain detail, natural film grain, photorealistic practical wardrobe and set, no text, no captions, no watermarks, no UI overlays.`

## 2. Period-Accurate Positive Vocabulary (10th–11th Century)

### Đại Việt Forces (Ngô / Đinh / Tiền Lê / Lý)
- **Armor & Wardrobe**: Lacquered dark-brown leather and iron lamellar cuirass (*giáp vảy*), coarse undyed hemp/ramie wrapped tunics (*áo giao lĩnh* / cross-collar short battle tunics), indigo-dyed cloth waist sashes, bare or cloth-wrapped shins (*xà cạp*) muddied from riverbanks, conical or shallow-domed lacquered iron/rattan helmets.
- **Weapons & Gear**: Iron-tipped bamboo and hardwood spears (*giáo*, *mác*), curved single-edged sabers (*đao*), wooden/bamboo crossbows (*nỏ*) with bone or iron triggers, woven rattan and lacquered-wood shields, sharpened charred ironwood river stakes (*cọc gỗ lim*), reed/bamboo fire rafts.
- **Architecture & Vessels**: Low-slung timber-and-thatch riverine watchtowers, earthen ramparts reinforced with bamboo palisades, flat-bottomed wooden war junks and oar-powered river galleys with dark pitched hulls.

### Northern Song Dynasty Forces (960–1127)
- **Armor & Wardrobe**: Iron laminar armor (*shanwenjia* / mountain-pattern and rectangular iron plates laced with leather thongs), padded crimson or slate-blue gambesons underneath, iron-rimmed round helmets with neck guards (*bảo đầu*), leather bracers, heavy boots.
- **Weapons & Gear**: Long-shafted Song halberds (*kích*) and crescent-blade polearms, composite recurve bows, iron-strapped wooden tower shields, counterweighted torsion catapults/trebuchets (*pháo*), multi-oared Song transport barges and armored river warships.
- **Banners & Camp**: Weathered crimson, ochre, and dark-indigo silk pennants frayed by wind (explicitly **blank or pure geometric/animal emblem only — zero Chinese/Vietnamese characters**).

## 3. Negative Anti-Anachronism Constraints

Never allow any of the following in prompts or accepted frames:
- **Zero AI-Drawn Text**: No Latin letters, Vietnamese diacritics, Chinese characters, dates, map labels, subtitles, logos, or UI graphics on any story frame (`allowed_text=None`).
- **No Wrong-Era Armor/Weapons**: No European plate armor, Viking horned helmets, Japanese samurai *kabuto*/*katana*, Qing Dynasty queues/Manchu robes, Ming-era muskets/cannons, or modern tactical gear.
- **No Fantasy/Video-Game Tropes**: No glowing magic weapons, neonrim lighting, exaggerated CGI superhero capes, spotless mirror-polished chrome armor, or 3D-rendered diorama/board-game miniatures.
- **No Modern Artifacts**: No concrete walls, asphalt, modern steel cables, electric floodlights, or modern eyeglasses/wristwatches.

## 4. 5-Shot Camera Rotation Matrix

Rotate continuously through these 5 camera setups across consecutive beats and sub-beats so no two adjacent cuts share the same scale and angle:

| Slot | Shot Type | Typical Lens / Angle | Narrative Function |
| :--- | :--- | :--- | :--- |
| **1** | **Wide Establishing** | 24mm–35mm, elevated or riverbank horizon | Geography, troop scale, river width, defensive line layout |
| **2** | **Medium OTS (Over-the-Shoulder)** | 50mm, shoulder-height behind commander/scout | Tactical perspective, tension before engagement, spatial orientation |
| **3** | **Tight Action Macro** | 85mm–100mm, shallow DoF, close-up | Hands stringing crossbow, ironwood stake tip, oar biting water, mud-splattered lamellar plates |
| **4** | **Atmospheric Landscape** | 35mm–50mm, crisp optical clarity / directional sunlight / torchlit chiaroscuro | Weather shift, tidal change, dawn/dusk passage of time, tension before battle |
| **5** | **Low-Angle Hero** | 28mm–35mm, looking upward at subject | Commander, standard-bearer, or vanguard warrior framed against dramatic sky or warm torchlight |

## 5. Modular FX Warehouse Integration & Bespoke-Per-Campaign Rule

`su_ke_lai` plugs directly into [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md) and the sharded `sys/fx_warehouse/` sub-modules (`archetypes`, `camera_vfx`, `hud_widgets`, `audio_sfx_bgm`, `selector`) via `selector.auto_select_beat_fx(..., channel_id="su_ke_lai", video_topic=...)`:

- **Shared Warehouse Mapping (Option 1 Cinema)**:
  - Pulls period-safe sub-pixel 2.5D camera moves (`camera_vfx`) aligned with the 5-shot camera rotation matrix.
  - Pulls `heroic_banner` (`>= 132px`, `<= 4` words) on Shorts or chapter stamps (`hud_widgets`) on Long while keeping `allowed_text=None` on 100% of raw Flow story frames.
  - Pulls era-appropriate battlefield & riverine foley/BGM stems (`audio_sfx_bgm`: war drums, bowstrings, river currents, storm thunder).
- **Non-Forced Bespoke Rule & Anti-Anachronism**: Strictly forbid modern digital radar reticles, oscilloscopes, or cyber HUDs on medieval/dynasty battles. Whenever a historical campaign requires unique tactical mechanics (e.g., Bạch Đằng tidal river-stake depth/tide chart, Như Nguyệt river fortification cross-section, siege trajectory arc) or era-specific procedural 48kHz SFX (e.g., bamboo fire-raft crackle, bronze war-horn resonance), MUST synthesize bespoke per-video/per-topic `bespoke_hud_spec` (`build_bespoke_topic_hud_patch`) and `bespoke_sfx_spec` (`synthesize_bespoke_topic_sfx`) instead of forcing anachronistic presets.

## 6. Short V3 100% 35mm Epic Live-Action & Screen-Text Law (`heroic_banner`)

- **100% 35mm Live-Action Epic Clarity (No Sand-Tables)**: Strictly **FORBID** clay/mud/wooden sand-tables (`tactical_sand_table`) and unlabelled symbol maps on `su_ke_lai` Shorts. Convey military maneuvers through immediately legible wide/aerial 35mm live-action cinema (torch-lit night sieges, monsoon cavalry ambushes, massed advancing columns, commander/king on war elephant, dawn banners unfurling).
- **Screen-Text Law (`VIETSUB_FONT_SIZE >= 132px`)**: All post-render Short banner overlays (`heroic_banner`, `anchor_y=150`) MUST render at **`font_size >= VietSub` (`>= 132px` on `1440x2560`, target `136px`)**, **`<= 4` UPPERCASE words**, sharp `NotoSans-Bold.ttf` with thick black outline. Strictly **FORBID** multi-line telemetry boxes, small kickers, or tiny sublines. Raw Flow frames remain `allowed_text=None`.

## 7. Anti-Smoke-Spam & 8-Effect Cinematic Diversity Rule (`su_ke_lai_viral_v4.1`)

- **Clear-Air 35mm Anamorphic Cinema Clarity Default**: Every prompt and style lock MUST replace blanket haze (`"river mist"`, `"drifting gunsmoke fog"`, `"dense battlefield mist"`) with `"crisp optical clarity, deep-focus 35mm anamorphic depth, dramatic directional sunlight or warm Caravaggio torchlight chiaroscuro, rich tactile armor and terrain detail"`.
- **`dust_smoke_cloud` Cap (`<= 1` per 20-beat Short)**: Allow **at most `1`** `dust_smoke_cloud` exit seam per 20-beat Short, and **ONLY** on genuine cannon or fire-weapon beats. Even there, `EXIT_SEAMS["dust_smoke_cloud"]` uses only a thin wisp of warm torch embers at the frame edge while keeping the hero subject and face razor-sharp (never opaque fog white-outs).
- **Mandatory Exit-Seam Rotation**: Rotate across the 5 clean cinematic exit seams so no two consecutive Veo clips repeat the same exit seam:
  - `edge_pass` — Kurosawa foreground architectural pillar / silk war-banner / shield edge wipe
  - `dark_opening` — Caravaggio deep torchlit shadow archway pass
  - `leaves_wipe` — 3D foreground bamboo / foliage parallax sweep
  - `white_flash` — warm golden anamorphic sunbeam / torch flare across the lens
  - `final_hold` — shallow-DoF anamorphic rack-focus settle onto the hero subject
- **Beat-Matched FFmpeg `xfade` Transitions (`sys/short_engine/render_single_pass.py`)**: Every clip boundary auto-rotates beat-matched cinematic `xfade` transitions (`fadeblack` for `dark_opening`; `smoothleft` / `smoothright` alternating for `edge_pass` / `truck_lateral` / `tracking_alongside`; `dissolve` / `circleopen` for `white_flash` / `crane_up`; `fade` / `dissolve` for `final_hold` / `push_in` / `pull_back` / `orbit`) instead of uniform `fade`.
