# 04 — Live-Action Historical Coverage & Micro-Detail Bible

> **Thread 1D** · V12 Cinema Research · `su_ke_lai` · 2026-11-25

---

## 1. Diagnosis: Why Our Prompts Produce Repetitive Shots

### Current 5-Shot Rotation Matrix (visual.md §4)

| Slot | Shot Type | Lens | The Problem |
|------|-----------|------|-------------|
| 1 | Wide Establishing | 24–35mm | ✅ Works — but overused (~25% of all beats) |
| 2 | Medium OTS | 50mm | ⚠️ "OTS" in name only — no foreground obstruction, renders as clean medium shot |
| 3 | Tight Action Macro | 85–100mm | ⚠️ Consistently includes face + torso; never true zero-face prop insert |
| 4 | Atmospheric Landscape | 35–50mm | ⚠️ Always contains human figure in frame |
| 5 | Low-Angle Hero | 28–35mm | ⚠️ Same front-facing composition at different angle |

### Root Causes

1. **All 5 slots include human subjects** — zero dedicated prop-only or environment-only slots
2. **Prompt Block 2** always specifies `"Primary Subject & Action"` with a named human actor → AI centers a person in every frame
3. **"Macro" slot** says "Hands stringing crossbow" but consistently generates medium-tight shot including face + torso because the prompt still mentions the person
4. **No prompt vocabulary** for overhead/perpendicular-down God's-eye geometry
5. **No "dirty single"** vocabulary — foreground obstruction that creates depth layering
6. **No dedicated environment-only sensory beat** in any style's `narrative_beat_roles`
7. **All 20 styles (S01..S10, L01..L10)** use variations of the same 5 camera slot structure — differences are in lens/angle but not in shot class diversity

---

## 2. Reference Channel Analysis

### Netflix — Rise of Empires: Ottoman (NRuOTkSgDbs)

**Key observations from 75 frames at 1fps:**

| Timestamp | Shot Class | Description |
|-----------|-----------|-------------|
| 0s–3s | `GODS_EYE` | Overhead battlefield aftermath — no human faces, geometric corpse patterns |
| 4s–7s | `OTS_DIRTY` | Past armored shoulder watching Constantinople walls approach |
| 8s–12s | `ENV_SENSORY` | Empty fortification silhouettes in dawn fog — zero humans |
| 13s–18s | `REACTION_MICRO` | Mehmed ECU in candlelight — only face from eyebrow to chin, pupils reflecting flames |
| 19s–24s | `OTS_DIRTY` | Past courtier's ear to Mehmed speaking — foreground blur 30% of frame |
| 25s–30s | `GODS_EYE` | City layout from bird's-eye — geometric walls and quarters visible |
| 31s–38s | `MACRO_PROP` | Candlelight on wet ink, hands on treaty document — zero face |
| 39s–44s | `GROUND_MUD` | Low-angle through battlements, soldiers towering above |
| 45s–55s | Mix | Rapid cross-cutting between all 6 missing classes |
| 60s–75s | `SILHOUETTE_SCALE` | Compressed telephoto army silhouettes against sunset |

**Coverage diversity score**: 8 distinct shot classes in 75 seconds (vs. our typical 3–4)

### Yarnhub — When Rangers Scaled Cliffs on D-Day (hInKZw88DaM)

**Key observations from 75 frames at 1fps:**

| Timestamp | Shot Class | Description |
|-----------|-----------|-------------|
| 0s–5s | `GROUND_MUD` | Ground-level explosion impact — debris spraying toward camera at ankle height |
| 6s–10s | `GODS_EYE` | Overhead fleet landing craft formation on water — geometric V-wakes |
| 11s–15s | `REACTION_MICRO` | Soldier's face in helmet, micro-expressions of fear, tight headroom crop |
| 16s–22s | `OTS_DIRTY` | Past soldier's helmet looking at cliff face ahead |
| 23s–28s | `ENV_SENSORY` | Dark cliff silhouette against pre-dawn sky — zero humans |
| 29s–35s | `MACRO_PROP` | Hands gripping rope, climbing gear detail — zero face |
| 36s–45s | `GROUND_MUD` | Low-angle through rocky outcrop, muzzle flashes in distance |
| 46s–55s | `REACTION_MICRO` | Multiple soldiers' faces in group close-up, fear and resolve |
| 56s–75s | Mix | Night assault with rapid cross-cutting, every class represented |

**Coverage diversity score**: 7 distinct shot classes in 75 seconds

---

## 3. The 6 Missing Shot Classes

### Class 01: `MACRO_PROP` — Extreme Macro Tactile Prop/Action Insert

> **The subject is a THING, not a person.**

- **Lens**: 100–135mm macro, f/2.0–f/2.8, focus distance 30–60cm
- **Composition**: Subject fills 60–80% of frame. Human skin (hand, fingers) may appear at frame edge but face is NEVER visible. Background is 100% bokeh blur
- **Camera move**: Ultra-slow push-in (0.3cm/s drift) or static with rack-focus
- **Duration**: Short 2.0s · Long 3.5s

**Sử Kể Lại examples:**
1. Ironwood stake tip being sharpened — curling wood shavings falling, calloused fingers gripping charred wood
2. Cinnabar seal pressing into hot wax on bamboo-paper edict — red wax spreading under pressure
3. Bronze crossbow trigger loaded — iron bolt clicking into bamboo groove
4. Torch flame igniting pitch-soaked fire-raft ropes — sparks across wet river mud
5. Rain streaming down lacquered iron lamellar plates — droplets pooling in valleys

**BELUGA prompt template:**
```
{period_prop} in extreme 100mm macro close-up, shallow depth of field, only the
object and immediate tactile surface visible, NO human face, {lighting_key},
crisp fine detail of {material_texture}, natural film grain, 35mm Kodak Vision3
500T, no text, no captions, no watermarks
```

**Veo motion template:**
```
Ultra-slow 0.3cm/s push-in toward {prop}, subtle {material_interaction}
micro-movement, shallow rack focus drift, steady macro tracking
```

---

### Class 02: `OTS_DIRTY` — Over-The-Shoulder Dirty Single

> **Camera behind one character's shoulder/head, creating foreground blur depth layering.**

- **Lens**: 50–85mm, f/2.8–f/4.0, two-plane focus
- **Composition**: Foreground character occupies 25–35% of frame edge (shoulder/head in soft blur). Background subject in sharp focus. Dark natural vignette from foreground body
- **Camera move**: Static or very slow truck-lateral (1cm/s)
- **Duration**: Short 2.5s · Long 4.0s

**Sử Kể Lại examples:**
1. OTS past Lý Thường Kiệt's armored shoulder → Song war junks approaching at dawn
2. OTS past scout's bamboo hat → enemy torchlight procession through mountain pass
3. OTS past kneeling crossbow soldier's hemp shoulder → aiming across rain-swept estuary

**BELUGA prompt template:**
```
Over-the-shoulder shot from behind {foreground_character}'s {body_part_visible}
in soft bokeh foreground, sharp focus on {background_subject} in the middle
distance, {lighting_key}, 50mm-85mm cinema lens, 35mm Kodak Vision3 500T film,
spatial depth tension, {environment_detail}, no text, no captions
```

---

### Class 03: `GROUND_MUD` — Ground-Level / Boots-in-Mud / Low-Angle Scale

> **Camera at ankle height (0–30cm). Ground texture dominates foreground.**

- **Lens**: 24–28mm ultra-wide, f/4.0–f/5.6, deep focus 30cm to infinity
- **Composition**: Camera at ankle height. Foreground = 40% mud/water/terrain. Middle = boots/hooves/stakes. Background = towering figures/sky. Strong perspective exaggeration
- **Camera move**: Low tracking-alongside (following boots) or static with figures walking OVER camera
- **Duration**: Short 2.2s · Long 3.0s

**Sử Kể Lại examples:**
1. Through Red River Delta mud — ironwood stakes protruding upward, distant Song junks against dawn sky
2. Behind marching Đại Việt infantry boots in monsoon mud — puddles reflecting torchlight
3. Along river bank — oar tips slicing dark water, war-galley hull towering above

---

### Class 04: `GODS_EYE` — High-Angle God's-Eye Formation Geometry

> **Direct overhead (70°–90° perpendicular-down). No horizon. Pure geometry.**

- **Lens**: 35–50mm, orthographic perspective, deep focus
- **Composition**: Ground fills 100% of frame. Subjects seen from directly above as geometric formations. Strong patterns (circles, lines, triangles)
- **Camera move**: Slow crane-descend or static overhead
- **Duration**: Short 2.5s · Long 5.0s

**Sử Kể Lại examples:**
1. Overhead: ironwood stake-field geometry in Bạch Đằng river at low tide — stakes forming defensive grid
2. Overhead: Đại Việt infantry square from directly above — circular shield-wall on muddy terrain
3. Overhead: river battle — oar wakes forming V-patterns on dark water, burning fire rafts drifting downstream

---

### Class 05: `REACTION_MICRO` — Micro-Acting Reaction Close-Up

> **Extreme close-up. Face fills 80–100% of frame. The subject IS the emotion.**

- **Lens**: 85–135mm, f/1.4–f/2.0, razor-thin DoF on eyes
- **Composition**: Eyes occupy upper 1/3 rule line. Only eyes-to-chin visible. Background is 100% warm/cold bokeh. Lighting creates catchlights in iris
- **Camera move**: Static or ultra-slow push-in (barely perceptible drift toward eyes)
- **Duration**: Short 1.5s · Long 2.5s

**Sử Kể Lại examples:**
1. Commander's eyes reflecting torchlight as invasion report arrives — jaw muscles tensing
2. Soldier's trembling exhale in pre-dawn cold — pupils dilating as war drums begin
3. River pilot's eyes scanning tide mark — sweat bead rolling, hand grip tightening on tiller

---

### Class 06: `ENV_SENSORY` — Environmental Sensory B-Roll

> **ZERO human subjects. The environment IS the subject.**

- **Lens**: 35–85mm, f/2.8–f/5.6, selective focus
- **Composition**: No human in frame. Environmental element fills 70–100%. Movement from natural forces (water, wind, fire, light)
- **Camera move**: Static hold (3–5s) or slow tilt
- **Duration**: Short 2.0s · Long 4.0s

**Sử Kể Lại examples:**
1. Rain streaming down curved terracotta roof tiles of Đại La citadel at night
2. River current swirling around half-submerged ironwood stakes at sunrise
3. Smoke curling from dying campfire embers — bamboo chopsticks in the ashes
4. Wind rippling a weathered battle banner on bamboo pole — frayed edges catching last light
5. Morning mist lifting from still rice paddy — revealing distant watchtower silhouettes

---

## 4. Multi-Shot Scene Coverage Formulas

### Formula A — Command Decision Sequence

```
GODS_EYE (3.0s) → OTS_DIRTY (2.5s) → REACTION_MICRO (1.5s) → MACRO_PROP (2.0s)
```

**Narrative**: Establishing → Blocking → Reaction → Consequence

| Beat | Class | Prompt Focus |
|------|-------|-------------|
| 1 | `GODS_EYE` | Overhead: troop/terrain layout establishing the problem |
| 2 | `OTS_DIRTY` | Past scout's shoulder → commander receiving report |
| 3 | `REACTION_MICRO` | ECU commander's eyes processing intelligence |
| 4 | `MACRO_PROP` | Hand pressing seal onto deployment order |

---

### Formula B — Ambush Eruption Sequence

```
ENV_SENSORY (2.5s) → GROUND_MUD (2.0s) → MACRO_PROP (1.5s) → REACTION_MICRO (1.5s) → GODS_EYE (3.0s)
```

**Narrative**: Establishing → Blocking → Tactile Insert → Consequence → Analytical Cut

| Beat | Class | Prompt Focus |
|------|-------|-------------|
| 1 | `ENV_SENSORY` | Eerie calm — river surface, rustling bamboo |
| 2 | `GROUND_MUD` | Boots/hooves suddenly breaking into motion at ankle height |
| 3 | `MACRO_PROP` | Bowstring releasing / crossbow trigger snapping |
| 4 | `REACTION_MICRO` | Enemy face registering shock |
| 5 | `GODS_EYE` | Full ambush geometry revealed from above |

---

### Formula C — Forensic Evidence Sequence

```
OTS_DIRTY (3.0s) → MACRO_PROP (3.5s) → REACTION_MICRO (2.0s) → ENV_SENSORY (2.0s)
```

**Narrative**: Spatial Context → Tactile Evidence → Emotional Impact → Breathing Beat

---

### Formula D — Battle Impact Sequence

```
GROUND_MUD (2.0s) → OTS_DIRTY (2.0s) → MACRO_PROP (1.5s) → REACTION_MICRO (1.5s) → GODS_EYE (3.0s)
```

**Narrative**: Ground-Level Chaos → Spatial Tension → Tactile Impact → Human Cost → Strategic Consequence

---

### Formula E — Time-Passage Sensory Bridge

```
ENV_SENSORY (3.0s) → MACRO_PROP (2.0s) → ENV_SENSORY (2.5s)
```

**Narrative**: Breathing Beat → Physical Time Marker → New Temporal Context

---

### Formula F — Commander Psychological Duel

```
REACTION_MICRO A (2.0s) → MACRO_PROP A (1.5s) → REACTION_MICRO B (2.0s) → MACRO_PROP B (1.5s) → OTS_DIRTY (2.5s) → GODS_EYE (3.0s)
```

**Narrative**: Intimate A → Tactile A → Counter B → Tactile B → Spatial Confrontation → Strategic Overview

---

## 5. Expanded 12-Slot Camera Rotation Matrix

Replaces the original 5-slot system. Rotate so no two adjacent cuts share the same class code.

| Slot | Class Code | Shot Type | Lens | Function |
|------|-----------|-----------|------|----------|
| 1 | `GODS_EYE` | God's-Eye Overhead | 35–50mm orthographic | Formation geometry |
| 2 | `OTS_DIRTY` | Over-The-Shoulder Dirty Single | 50–85mm | Spatial tension |
| 3 | `MACRO_PROP` | Extreme Macro Prop Insert | 100–135mm macro | Zero-face tactile detail |
| 4 | `WIDE_ESTABLISHING` | Wide Establishing | 24–35mm anamorphic | Geography & scale |
| 5 | `REACTION_MICRO` | Reaction Micro-Acting ECU | 85–135mm | Emotional processing |
| 6 | `GROUND_MUD` | Ground-Level Boots POV | 24–28mm ultra-wide | Physical immersion |
| 7 | `MEDIUM_COMMAND` | Medium Command/Blocking | 50mm | Tactical dialogue |
| 8 | `ENV_SENSORY` | Environmental Sensory B-Roll | 35–85mm | Breathing beat |
| 9 | `LOW_HERO` | Low-Angle Hero | 28–35mm | Commander authority |
| 10 | `ATMOSPHERIC` | Atmospheric Landscape | 35–50mm | Time passage |
| 11 | `TIGHT_ACTION` | Tight Action Detail | 85mm | Combat impact |
| 12 | `SILHOUETTE_SCALE` | Silhouette Scale Shot | 135mm telephoto | Epic compression |

**Rotation rule**: Never repeat same class in adjacent beats. Min 3 different classes in any 5-beat window. `MACRO_PROP` and `ENV_SENSORY` each appear ≥1 per 8-beat sequence.

---

## 6. Coverage Budget Per Video

### Short 9:16 (20 beats, 48–60s)

| Class | Min Count | Recommended |
|-------|-----------|-------------|
| `MACRO_PROP` | **≥ 2** | 3 |
| `OTS_DIRTY` | **≥ 1** | 2 |
| `GROUND_MUD` | ≥ 1 (combined w/ `GODS_EYE`) | 1 |
| `GODS_EYE` | ≥ 1 (combined w/ `GROUND_MUD`) | 1 |
| `REACTION_MICRO` | **≥ 2** | 2 |
| `ENV_SENSORY` | **≥ 1** | 1 |
| Others (WIDE/MEDIUM/LOW/ATMO/TIGHT) | — | 10 |

> **Gate**: ≥30% of beats must be non-human-centered (`MACRO_PROP` + `ENV_SENSORY` + `GODS_EYE`)

### Long 16:9 (240–350 images, 8m30s–13m)

| Chapter Type | MACRO_PROP | OTS_DIRTY | GROUND_MUD | GODS_EYE | REACTION_MICRO | ENV_SENSORY |
|-------------|-----------|-----------|-----------|---------|---------------|-------------|
| Cold Open (60s) | 3 | 2 | 1 | 1 | 2 | 2 |
| Body Chapter | 5 | 3 | 2 | 2 | 3 | 3 |
| Climax | 6 | 4 | 3 | 2 | 4 | 2 |
| Epilogue | 3 | 2 | 1 | 1 | 2 | 3 |

> **Gate**: ≥15% `MACRO_PROP`, ≥8% `OTS_DIRTY`, ≥5% `GROUND_MUD`+`GODS_EYE`, ≥8% `REACTION_MICRO`, ≥6% `ENV_SENSORY`

---

## 7. Veo 3.1 Lite Motion Guidance Per Shot Class

| Class | Motion Speed | Motion Type | Required Element |
|-------|-------------|------------|-----------------|
| `MACRO_PROP` | Ultra-slow (0.3cm/s) | Push-in or rack-focus | Object micro-movement (dripping, flickering) |
| `OTS_DIRTY` | Slow (1cm/s) | Push-in past shoulder | Foreground-background parallax |
| `GROUND_MUD` | Medium (boot speed) | Low tracking-alongside | Terrain particles near lens |
| `GODS_EYE` | Slow | Crane descend or orbit | Geometric patterns from above |
| `REACTION_MICRO` | Near-static (0.2cm/s) | Barely perceptible push | Subject breathing rhythm |
| `ENV_SENSORY` | Static to slow | Static hold or slow tilt | Natural element movement |

---

## 8. Quality Gates

### Per-Frame Validation

| Class | Validation Rule |
|-------|----------------|
| `MACRO_PROP` | Subject fills ≥60% frame; no face detected in center 50% crop |
| `OTS_DIRTY` | Foreground blur occupies 25–35% of frame edge |
| `GROUND_MUD` | Horizon line in upper 15% of frame or absent |
| `GODS_EYE` | No horizon line visible; ground fills 100% |
| `REACTION_MICRO` | Face fills ≥70% of frame; eyes in upper third |
| `ENV_SENSORY` | No human figure detected anywhere in frame |

### Pre-Render Coverage Audit

Reject any video spec where:
- `MACRO_PROP` < 2
- `ENV_SENSORY` < 1
- (`OTS_DIRTY` + `GROUND_MUD` + `GODS_EYE`) < 2

---

## 9. Contact Sheet References

| File | Source | Description |
|------|--------|-------------|
| `rise_empires_ottoman_contact_sheet.png` | Netflix Rise of Empires: Ottoman S1 Trailer | 25 frames at 1fps showing OTS, candlelit ECU, God's-eye city, environmental fog |
| `yarnhub_dday_rangers_contact_sheet.png` | Yarnhub — D-Day Rangers | 25 frames at 1fps showing ground-level explosions, overhead fleet, micro-reaction group shots |
