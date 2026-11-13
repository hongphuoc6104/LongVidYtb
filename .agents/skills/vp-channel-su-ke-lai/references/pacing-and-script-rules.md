# Pacing & Script Rules — Sử Kể Lại (v3)

Reference contract for zero-filler Vietnamese spoken narration, clause-level sub-beat splitting (`Long 16:9`), and `12`-beat `Short 9:16` spin-off arcs.

## 1. Zero-Filler 12-Sentence-Per-Chapter Structure (`Long 16:9`)

Every `long_16x9` episode is locked to:
- **`10` Chapters × `12` Core Sentences = `120` Core Sentences** total.
- **Zero Filler**: Every sentence must advance a concrete historical event, tactical mechanism, geographical constraint, causal consequence, or human stake. Cut throat-clearing intros ("Trong video hôm nay..."), repetitive summaries, and generic adjectives.
- **Spoken Cadence**: Write short, natural Vietnamese spoken sentences calibrated for `VietNarrator_su_ke_lai` at `1.30x` (`speaking_rate=1.30`) with `0.06s` inter-beat gaps and `0.18s` chapter gaps, targeting **`~9m15s–9m45s`** total runtime.
- **Chapter Hook & Payoff**:
  - Sentence 1 of Chapter 1 opens immediately with a counter-intuitive historical stake or visceral tactical problem (no channel intro).
  - Sentence 12 of each chapter bridges directly into the next chapter's escalation.

## 2. Two-Clause Sentence Rule (Eliminating Visual Drag)

Each of the `120` spoken sentences is split at its natural **clause boundary** (comma, conjunction, or cause-effect pivot) into **two visual sub-beats**, yielding **`240` BELUGA `1920x1080` frames** (average **`~2.30s–2.40s/image`**) connected by `xfade=fade:duration=0.18`:

| Sub-beat | Duration Share | Camera Role (from 5-Shot Matrix) | Visual Purpose |
| :--- | :--- | :--- | :--- |
| **Sub-beat A** | **`48%`** | **Wide Establishing** or **Medium OTS** (or Atmospheric Landscape) | Establishes the spatial/tactical context of the opening clause |
| **Sub-beat B** | **`52%`** | **Tight Action Macro** or **Low-Angle Hero** | Punches in on the physical detail, weapon, terrain hazard, or human reaction in the second clause |

### Split Example
- **Spoken Sentence**: *"Khi thủy triều bắt đầu rút xuống lòng sông Bạch Đằng, hàng nghìn cọc gỗ lim bịt sắt mới lộ mũi nhọn dưới làn nước đục."*
- **Sub-beat A (`48%`)**: Wide Establishing across the receding muddy tide of the Bạch Đằng estuary at dusk, dark wooden war junks drifting in the current.
- **Sub-beat B (`52%`)**: Tight Action Macro just above the swirling brown waterline as sharpened, charred ironwood stake tips emerge from the ebbing current.

## 3. Short 9:16 12-Beat Narrative Arc (`~48–58s`)

Standalone `short_9x16` spin-offs (`omni_flash` `single_frame_i2v`, `end_image_path=None`, `parent_long_id` linked) follow a compressed `12`-beat arc:

1. **Beats 1–2 (`0–8s`) — Counter-Intuitive Hook**: Immediate historical paradox or fatal tactical miscalculation in beat 1 (`<= 18` syllables, zero pause).
2. **Beats 3–5 (`8–22s`) — Terrain & Constraint**: Visualizes the exact physical bottleneck (river tide, mountain pass, supply line, armor/weapon mismatch).
3. **Beats 6–9 (`22–40s`) — Tactical Turn & Climax**: Step-by-step execution of the ambush, counter-strike, or engineered trap in `single_frame_i2v` motion.
4. **Beats 10–12 (`40–58s`, last 15%) — Consequence, Close CTA & Channel Bridge**: Lands the decisive historical outcome and delivers a natural close CTA + bridge to the full `parent_long_id` episode on **Sử Kể Lại** (never "like/share/subscribe").
