# Option 1 Visual Grammar — `su_ke_lai_35mm_live_action_v3`

Reference specification for generating 35mm live-action historical battle cinema docudrama frames for **Sử Kể Lại**. Every story frame MUST enforce `allowed_text=None` (`Zero AI-Drawn Text`).

## 1. 5-Block Option 1 Prompt Formula

Construct every image prompt in this exact 5-block order:

1. **Block 1 — Camera & Shot Framing**: Shot scale, angle, lens/perspective, and subject placement from the **V12 12-Slot Camera Rotation Matrix** (e.g., `Wide establishing 35mm anamorphic shot, eye-level across a clear-air riverbank embankment...`, or `100mm extreme macro prop insert, zero human face...`).
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

## 4. V12 12-Slot Camera Rotation Matrix & 6 Missing Live-Action Shot Classes

Replaces the legacy 5-shot system. Rotate continuously across all **12 camera slots** so **no two adjacent cuts share the same class code**, and every 5-beat window contains **>= 3 distinct classes**. `MACRO_PROP` and `ENV_SENSORY` must each appear **>= 1 per 8-beat sequence**.

| Slot | Class Code | Shot Type | Lens / Angle | Narrative Function & Veo Motion |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `GODS_EYE` | **God's-Eye Overhead** | 35–50mm, 70°–90° perpendicular-down, no horizon | Formation geometry, stake-field grids, V-wakes; slow crane-descend or orbit |
| **2** | `OTS_DIRTY` | **Over-The-Shoulder Dirty Single** | 50–85mm, 25–35% blurred foreground shoulder/helmet | Spatial depth tension, commander/scout POV; slow `1cm/s` push-in or lateral truck |
| **3** | `MACRO_PROP` | **Extreme Macro Prop Insert** | 100–135mm macro, f/2.0–2.8, **ZERO human face** | Subject >= 60% frame (cinnabar seal, ironwood stake tip, crossbow trigger); `0.3cm/s` push-in or rack-focus |
| **4** | `WIDE_ESTABLISHING` | **Wide Establishing** | 24–35mm anamorphic, elevated or riverbank horizon | Geography, troop scale, river width, defensive line layout |
| **5** | `REACTION_MICRO` | **Reaction Micro-Acting ECU** | 85–135mm, f/1.4–2.0, eyes-to-chin (>= 70% frame) | Eyes in upper 1/3 reflecting torchlight/tension; near-static `0.2cm/s` push |
| **6** | `GROUND_MUD` | **Ground-Level Boots POV** | 24–28mm ultra-wide, ankle height (0–30cm) | 40% mud/water foreground, towering figures/stakes; low tracking-alongside |
| **7** | `MEDIUM_COMMAND` | **Medium Command / Blocking** | 50mm, chest/waist framing | Tactical council blocking and command handoffs |
| **8** | `ENV_SENSORY` | **Environmental Sensory B-Roll** | 35–85mm, **ZERO human figures** | Rain on terracotta, current around stakes, frayed banner; static hold or slow tilt |
| **9** | `LOW_HERO` | **Low-Angle Hero** | 28–35mm, looking upward at subject | Commander, standard-bearer, or vanguard framed against sky/torchlight |
| **10** | `ATMOSPHERIC` | **Atmospheric Landscape** | 35–50mm, clear-air sunlight or torchlit chiaroscuro | Weather shift, tidal change, dawn/dusk passage of time |
| **11** | `TIGHT_ACTION` | **Tight Action Detail** | 85mm, shallow DoF | Combat impact, oar biting water, weapon clash |
| **12** | `SILHOUETTE_SCALE` | **Silhouette Scale Shot** | 135mm telephoto compression | Compressed army/fleet silhouettes against dawn or dusk |

### 4.1 Coverage Budget & Multi-Shot Scene Formulas
- **Short `9:16` (`20` beats, `48–60s`)**: `MACRO_PROP >= 2` (rec `3`), `OTS_DIRTY >= 1` (rec `2`), `GROUND_MUD + GODS_EYE >= 2`, `REACTION_MICRO >= 2`, `ENV_SENSORY >= 1`; **>= 30% non-human-centered beats** (`MACRO_PROP + ENV_SENSORY + GODS_EYE`).
- **Long `16:9` (`240–350` images / `100` beats)**: `>= 15%` `MACRO_PROP`, `>= 8%` `OTS_DIRTY`, `>= 5%` `GROUND_MUD + GODS_EYE`, `>= 8%` `REACTION_MICRO`, `>= 6%` `ENV_SENSORY`. Pre-render audit rejects any video with `MACRO_PROP < 2`, `ENV_SENSORY < 1`, or `(OTS_DIRTY + GROUND_MUD + GODS_EYE) < 2`.
- **Scene Coverage Formulas**:
  - *A — Command Decision*: `GODS_EYE -> OTS_DIRTY -> REACTION_MICRO -> MACRO_PROP`
  - *B — Ambush Eruption*: `ENV_SENSORY -> GROUND_MUD -> MACRO_PROP -> REACTION_MICRO -> GODS_EYE`
  - *C — Forensic Evidence*: `OTS_DIRTY -> MACRO_PROP -> REACTION_MICRO -> ENV_SENSORY`
  - *D — Battle Impact*: `GROUND_MUD -> OTS_DIRTY -> MACRO_PROP -> REACTION_MICRO -> GODS_EYE`
  - *E — Time-Passage Bridge*: `ENV_SENSORY -> MACRO_PROP -> ENV_SENSORY`
  - *F — Commander Duel*: `REACTION_MICRO A -> MACRO_PROP A -> REACTION_MICRO B -> MACRO_PROP B -> OTS_DIRTY -> GODS_EYE`

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

## 8. V12 100% Zero-Box Typography Ban & Visual Commentary

> **Auto-Fail Gate (`AF-01` -> `0/100 FAIL`):** Every `ImageDraw.rectangle(fill=(0,0,0,alpha))` and `ImageDraw.rounded_rectangle()` used as a text background MUST be deleted. Zero dark pills, zero gold-bordered `VS` plaques, zero left vertical accent bars, zero Kahoot A/B quiz boxes, and zero opaque CAD modals.

- **Universal Zero-Box Rules**:
  1. **Max 3 words** for any text overlaid on live footage (not full-frame cutaways).
  2. **Shadow only** (`2–4px` offset, `rgba(0,0,0,0.5–0.7)` or feathered Gaussian optical scrim) — never a background rectangle.
  3. **Negative space placement** (sky, water, shadow; zero face overlap).
  4. **Full-frame for dense text**: anything `> 5` words gets its own full-frame cutaway (aged Dó-paper parchment, dark tabletop evidence rig, or `#07080B` obsidian spotlight stage).
  5. **Font stack**: `Inter` Bold/Black (data), `Crimson Text` Italic (quotes), `Montserrat` Black / `BarlowCondensed-ExtraBold` (impact numbers/titles).
- **4 Approved Zero-Box Patterns**:
  - **Pattern A — Dates & Locations**: Upper-left white bold (`36–42px` on `16:9`, `48–56px` on `9:16`), max `5` words, max `2` lines, `3.0–4.5s`, drop shadow only.
  - **Pattern B — Anti-VS Statistical Contrasts**: (B1) Hard vertical `16:9` split-screen with `1–3` word negative-space labels (zero `VS` badge), (B2) Giant sequential number reveal (`40–60%` canvas height), (B3) Color territory fill contrast.
  - **Pattern C — Historical Documents & Quotes**: (C1) Full-frame aged Dó-paper parchment quote, (C2) Dark tabletop artifact rig, (C3) Giant sparse `120–180px` cinema quote over `0.15–0.25` brightness footage.
  - **Pattern D — Visual Commentary Cutaways**: Giant `1–3` word cinema type (`96–180px`), split-screen before/after, progressive spotlight vignette (`65–75%` peripheral dim), territory fill map, dark-tabletop evidence rig.

## 9. V12 Slow Giant-Type `tactical_battle_map_v9` Specification

Supersedes V8's fast `4.8s`, 23-string microscopic map dumps (`sys/fx_warehouse/tactical_battle_map_v9.py`):

- **100% Chrome Abolition**: Permanently remove top 3-line date/title/phase headers, compass rose, left/right `tide_bar` / depth gauges, bottom `factions` force-ratio bars, 2nd-line `callouts[].sub`, and dotted leader hairlines. Zero rectangles, zero pills, zero procedural smoke.
- **Hard Giant-Type Floor (`>= 5.0%` Canvas Height)**: `_fit_font` is forbidden from shrinking below `5.0%` H (`ceil(H * 0.050)`). Over-length strings fail `validate_v9_minimalist_map_spec()` at build time.
  - **`9:16` (`1440x2560`)**: Tier 1 Theater/Impact Stamp `148px` (`5.78%` H), Tier 2 Unit/Landmark `132px` (`5.16%` H), Hard Floor `128px` (`5.00%` H); Unit block `136x84px`; Arrow `38px` shaft / `86px` head. Safe label box: `x in [64..1210]`, `y in [150..1700]` (clears `y=1740..2120` subtitles, right Shorts rail, and `W-w-36:H-h-36` logo).
  - **`16:9` (`1920x1080`)**: Tier 1 `90px` (`8.33%` H), Tier 2 `68px` (`6.30%` H), Hard Floor `56px` (`5.19%` H); Unit block `110x68px`; Arrow `31px` shaft / `70px` head. Safe label box: `x in [96..1740]`, `y in [72..830]` (clears `y=860..1040` and `W-w-36:H-h-36` logo).
- **Strict Label & Pacing Caps (`AF-02` Compliance)**: **`1–3` words** (`<= 16` chars, single line only), **`<= 2` simultaneous labels** per frame, **`6.0s–12.0s`** duration (`9.0s` default) with strict **3-Act Temporal Separation**:
  1. **Phase 1 — Terrain Lock (`0.0s–2.5s`)**: Relief + river ripples (`zoom 1.00->1.03`), `0` units, `1` Tier-1 Theater Stamp + optional `1` terrain pin, fading out cleanly before `2.55s`.
  2. **Phase 2 — Bold Unit Block + Giant Name (`2.5s–5.5s`)**: Act 1 text cleared; `1–2` giant faction blocks + `1–2` Tier-2 Giant Names, fading out cleanly at `5.30–5.60s`.
  3. **Phase 3 — Slow Maneuver Arrow + Pincer Impact (`5.5s–9.0s+`)**: Unit labels cleared; thick arrows advance via `_ease_in_out_cubic` over `2.8–3.6s` + calm shockwave rings + `1` Tier-1 Impact Verdict (`>= 3.0s` hold).

## 10. Active Flagship V11.5 Reborn Anti-AI Omni Cinema Visual Grammar, Character Reference Lock, Kodak 2383 Color Harmony & Motion-Police Audit (`su_ke_lai_reborn_v11_omni_cinema`)

Active Long `16:9` visual standard (`1920x1080@30fps`, `REBORN_PIPELINE_VERSION = "11.5.0"`, `./vp long-reborn` -> `sys/tools/produce_reborn_long_pilot.py` + `sys/fx_warehouse/reborn_long_cinema.py`, `[ERR-20261125-03]`) permanently retiring static V10 slideshows, procedural OpenCV/Pillow blob maps, un-anchored AI faces, harsh cross-shot color jumps, and modern flag hallucinations:

1. **Character Bible & `reference_media_ids` Consistency Lock (`character_roster` + Stage A0 `--stage anchors`)**:
   - Define every recurring commander, antagonist, and troop archetype in `full_spec.json` -> `character_roster` (`CharacterAnchorSpec`: `{character_id, name_vi, faction, dynasty_era, face_and_age_dna, armor_and_wardrobe_lock, signature_props, color_palette_hex, anti_anachronism_bans}`).
   - Stage A0 (`--stage anchors` / `harvest_character_anchors()`, auto-run by `--stage visual`) generates canonical `16:9` character turnaround reference sheets (`character_anchors/<character_id>.png` + `anchor_manifest.json`) via `build_character_anchor_prompt()` on the active Flow profile, caching `media_id` per profile.
   - Every Stage A beat listing `character_ids` injects `reference_media_ids=[...]` (same-profile `pinned_profile`) + `inject_character_reference_prompt()` (*"Using the attached reference image(s), maintain the exact same face, age, costume, armor palette, and 35mm cinema realism..."*) so characters never morph across Acts I–VI.
2. **3-Pillar Visual Mix Across Full `8m30s–11m30s` (`6` Acts, `~85–95` Beats)**:
   - **`~60%` `@Yarnhub` 1st/3rd-Person Hero-POV 35mm Clear-Air Moving Cinema (`moving_cinema`)**: Dynamic eye-level, OTS, ground-level, and commander/warrior POV camera moves grounded in `su_ke_lai_35mm_live_action_v3` (`allowed_text=None`, Clear-Air Kodak Vision3 500T clarity, zero blanket smoke/fog).
   - **`~22%` Google Flow `16:9` Aerial/Flycam & Split-Waterline Tactical Cinema**: Native moving Flow flycam terrain sweeps and underwater/surface `split-waterline` tactical shots paired with **seekbar-safe (`y <= 0.72*H`, target `<= 0.70*H`) transparent `1920x1080` RGBA elbow callouts** aligned to real BELUGA/Flow anchors (`0` OpenCV blob maps, `0` Pillow cartoon maps, `0` bottom-right `W-w-36:H-h-36` watermark overlap).
   - **`~18%` `@LEMMiNO` Zero-Box Optical Spotlight Forensic/Chronicle Reveals (`forensic_evidence_reveal`)**: Pure dark-stage optical spotlight reveals for primary chronicles, timelines, and weapon/hydrology mechanics (`0.18 <= y <= 0.72` seekbar-safe, **`0` rectangular boxes, `0` vertical left accent stripes**).
3. **Native Omni 1.2 Flash Variable-Duration Routing (`1.0x`) & Master Kodak 2383 35mm Color Harmony (`--color-grade kodak_2383_anti_ai`)**:
   - Select exact native clip duration via **`macaron_cookie_i2v[_fl]_{4s|6s|8s|10s}`** (`4s`, `6s`, `8s`, or `10s`, Seam or Frame-Link) so every moving shot plays at **`1.0x` real-time cadence** without unnatural `1.7x` speedup or slow-mo stutter.
   - **Master Color Harmony & Anti-AI De-Plasticizer (`--color-grade kodak_2383_anti_ai` default)**: Run `compute_act_reference_lab()` + `match_frame_to_act_palette()` (Reinhard Lab luminance/chrominance mean-std transfer toward each Act's `CANONICAL_ACT_PALETTES` / `act_palette` override) + `build_35mm_anti_ai_grade_filter()` in Stage 3 chunk FFmpeg filtergraphs to desaturate digital AI neon cyan/lime greens and waxy plastic skin, unify shadow toe and warm bronze/amber highlight roll-off across all 6 Acts, and apply subtle anti-CGI micro-softening + uniform fine 35mm temporal film grain (`noise=alls=4:allf=t+u`) prior to `h264_nvenc`.
   - Always sparkle-unblend the bottom-right Flow star on both `frames/` and `flow_clips/`, pin channel logo `watermark_150x150.png` at **`W-w-36:H-h-36`**, and generate Flow-native `16:9` posters with **`2–4` uppercase Vietnamese words** drawn natively (`< 2MB`, zero PIL/HTML overlay).
4. **Hard Anti-AI Historical/Crowd/Physics/Color QA Gate (`ANTI_AI_QA_RULES` + 6-Frame `motion-police`)**:
   - Programmatic gates (`validate_beat_anti_ai_contract()`, `audit_color_continuity()`, `--strict-anti-ai`) PLUS mandatory **6-frame temporal strip `motion-police` audit (`0%, 20%, 40%, 60%, 80%, 95%`)** on EVERY moving clip before Colab T4 render MUST block:
     - **Modern National Flag Hallucinations**: Zero red flags with yellow stars or modern emblems on historical 938/1288/1785/1789 vessels — enforce weathered period-accurate plain bronze, dark-indigo, or undyed hemp pennants only.
     - **Plastic CGI & Clone-Stamp Artifacts**: Zero waxy/over-smoothed plastic faces, zero symmetrical clone-stamp armies/crowds, zero miniature tilt-shift blur.
     - **Broken Action & Maritime Physics**: Zero deformed hands/gestures, detached mallets/weapons, floating oars, dry-deck hull waterfalls, 180° instant hull flips, opposite-wind sails, or modern bridges/ships/text.
     - **Cross-Shot Color Continuity**: Zero ungraded Lab ΔE luminance/chroma jumps between adjacent cuts.
   - **Enforcement**: Failing clips MUST trigger an immediate surgical re-roll (or `clean_window_sec` trim cap when only the trailing tail degrades) recorded in `motion_audit*.json` before 6-GPU Colab T4 `h264_nvenc` render. Zero unaudited AI clips are allowed in master MP4 output.
