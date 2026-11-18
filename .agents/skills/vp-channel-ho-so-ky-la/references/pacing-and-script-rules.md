# Pacing & Script Rules — Hồ Sơ Kỳ Lạ (v3)

Reference contract for crisp Vietnamese forensic investigative narration (`VietNarrator_ho_so_ky_la` at `1.10x` — deliberate articulate pronunciation), 4-mode visual beat mapping (`Long 16:9`), and `18`-beat `Short 9:16` viral-funnel spin-offs.

## 1. Acoustic Calibration & Hook Validation Gate (`script_hook_scorer.py >= 85/100`)

Every script for **Hồ Sơ Kỳ Lạ (`ho_so_ky_la`)** is calibrated for `VietNarrator_ho_so_ky_la`:
- **Voice Profile**: `recommended_speed = 1.10x` (V3.1 future TTS baseline: `base_omnivoice_speed = 1.00`, `atempo_factor = 1.10`, `inter_beat_gap_sec = 0.10s`, `default_tone = "forensic_investigative_crisp"`; local WSOLA retime from existing `1.05x` stems uses `atempo = 1.047619`).
- **Audio Chain & Master**: High-clarity EQ (`highpass=f=85,equalizer=f=210:t=q:w=1.2:g=-1.2,equalizer=f=2800:t=q:w=1.0:g=2.4,equalizer=f=4800:t=q:w=1.1:g=1.8,equalizer=f=7500:t=q:w=1.3:g=1.0,lowpass=f=15000`); reference WAV at `-14.0 LUFS / -1.2 dBTP`; final video master normalized to `-11.0 LUFS / -1.0 dBTP`.
- **Mandatory Hook & Open-Loop Rules**:
  - **Beat 1 / Cold Open**: `<= 18` syllables for `short_9x16`, `<= 24` syllables for `long_16x9`, zero `[pause:...]` tags in the opening line. Must combine curiosity triggers (`?`, numbers, paradox, hidden anomaly) and direct viewer address (`bạn`, `chúng ta`).
  - **Early Open Loop (`sents[1:4]`)**: Plant an unresolved forensic contradiction or hinge word (`nhưng`, `hóa ra`, `điều kỳ lạ`, `tại sao`) immediately after the hook so viewers stay past 15 seconds.
  - **Prohibited CTAs**: Never write "like", "share", "subscribe", "đăng ký kênh", or off-niche hashtags (`#learnontiktok`). Close with a Debate-Trigger investigative question + natural bridge to the Long dossier.

## 2. Long `16:9` Forensic Dossier Structure (`10` Chapters, `260` Beats, `~10–14m`)

Every `long_16x9` episode spans **`10` clear `FFMETADATA1` chapters (`00:00..`)** and **`260` visual beats** (`<= 30s/sentence`, `~3.290–7.417` syllables on scorer):
1. **Cold Open & Paradox (Chapter 1)**: Drop the viewer straight into the locked-room anomaly, ghost flight, or unexplained physical trace — zero channel intros.
2. **Dossier Setup & Timeline Escalation (Chapters 2–6)**: Walk systematically through witness logs, technical schematics, black-box timestamps, and forensic clues with a chapter-end micro-hook on every transition.
3. **Hypothesis Weighing & Elimination (Chapters 7–8)**: Contrast 2–3 competing theories (`MODE_2_HYPOTHESIS_CONTRAST` / `MODE_3_DOSSIER_CHECKLIST`) and eliminate impossible explanations using hard physics, chemistry, or official investigation records.
4. **Forensic Verdict & Open Debate (Chapters 9–10)**: Reveal the documented mechanical/forensic mechanism without sensational supernatural leaps, then pose an investigative Debate-Trigger question and tease the next dossier.

### Beat-to-4-Mode Visual Mapping (`Long 16:9`)
- **`MODE_1_EVIDENCE_STAMP` (~15% beats)**: Timestamp, altitude, pressure, or black-box numeric shock.
- **`MODE_2_HYPOTHESIS_CONTRAST` (~12% beats)**: Opposing hypotheses, `AUTO` vs `MAN` system states, or expectation vs reality.
- **`MODE_3_DOSSIER_CHECKLIST` (~15% beats)**: Multi-factor root-cause lists or official investigation steps `[01]`, `[02]`, `[03]`.
- **`MODE_4_NOIR_CINEMATIC_PACING` (~58% beats)**: Smooth 3D Noir progression (`2560x1440@30fps`, `xfade=fade:duration=0.24`).

## 3. Short `9:16` Funnel Arc (`18` Beats, `~52–90s`, `<= 5.0s/sentence`)

Every `short_9x16` spin-off is rewritten natively (never raw-sliced from middle chapters of Long) and linked via YouTube `Related Video` (`parent_long_id`):
1. **Beats 1–2 (`0–8s`) — Paradox Hook**: Immediate counter-intuitive anomaly (`<= 18` syllables, zero pause).
2. **Beats 3–10 (`8–40s`) — Forensic Clue Escalation**: Rapid `2–3.5s/beat` physical clue reveal (`<= 5.0s/sentence` average across `18` beats).
3. **Beats 11–15 (`40–65s`) — Key Turning Point**: Single decisive engineering/forensic detail (e.g., switch left on `MAN`).
4. **Beats 16–18 (last 15%) — Debate CTA & Long Bridge**: Open an investigative debate question ("Theo bạn...") and direct viewers to the full `parent_long_id` dossier on **Hồ Sơ Kỳ Lạ**.
