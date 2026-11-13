# Option 1 Visual Grammar — `su_ke_lai_35mm_live_action_v3`

Reference specification for generating 35mm live-action historical battle cinema docudrama frames for **Sử Kể Lại**. Every story frame MUST enforce `allowed_text=None` (`Zero AI-Drawn Text`).

## 1. 5-Block Option 1 Prompt Formula

Construct every image prompt in this exact 5-block order:

1. **Block 1 — Camera & Shot Framing**: Shot scale, angle, lens/perspective, and subject placement from the 5-shot rotation matrix (e.g., `Wide establishing 35mm anamorphic shot, eye-level across a misty river embankment...`).
2. **Block 2 — Primary Subject & Action**: Concrete physical action, posture, and period-accurate 10th–11th century Đại Việt or Northern Song combatants/craftspeople/commanders in motion.
3. **Block 3 — Period Costume, Armor & Props**: Explicit tactile materials (lamellar/laminar iron scales, lacquered leather, ramie/hemp tunics, ironwood stakes, bamboo shields, Song halberds) matching the faction vocabulary below.
4. **Block 4 — Environment, Lighting & Atmosphere**: 10th–11th century Red River Delta / northern frontier terrain, mud, river mist, rain, torchlight, campfire embers, or overcast storm sky.
5. **Block 5 — Film Stock & Clean-Frame Lock**: `Shot on 35mm Kodak Vision3 500T film, historical battle cinema docudrama, natural film grain, shallow cinema depth of field, photorealistic practical wardrobe and set, no text, no captions, no watermarks, no UI overlays.`

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
| **4** | **Atmospheric Landscape** | 35mm–50mm, low mist / storm sky / torchlit smoke | Weather shift, tidal change, dawn/dusk passage of time, dread or calm before battle |
| **5** | **Low-Angle Hero** | 28mm–35mm, looking upward at subject | Commander, standard-bearer, or vanguard warrior framed against smoke and sky |
