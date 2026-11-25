# Pacing & Script Rules — Cơ Thể Kể (`co_the_ke` V3.0)

Reference contract for crisp Vietnamese biomedical storytelling narration (`VietNarrator_co_the_ke` at `1.12x`), `10`-chapter / `240`-beat `Long 16:9`, and `18`-beat `Short 9:16` viral-funnel spin-offs.

## 1. Acoustic Calibration & Hook Validation Gate (`script_hook_scorer.py >= 85/100`)

- **Voice Profile**: `VietNarrator_co_the_ke` (`sys/assets/voices/ch_co_the_ke/profile.json`, SHA256 `0e5b0ac35ccd31565e31dceabfd20e8f110465ad370b84465f404e1c10f2f490`).
- **Speed & Tone**: `recommended_speed = 1.12` (`default_tone = "authoritative_calm"` — clear, trustworthy, slightly energized scientific cadence).
- **Audio Chain & Master**:
  - Voice EQ: `highpass=f=85,equalizer=f=190:t=q:w=1.2:g=-2.0,equalizer=f=3000:t=q:w=1.2:g=1.4,lowpass=f=13500`
  - Reference WAV target: `-14.0 LUFS / -1.2 dBTP`
  - Final Video Master: `-11.0 LUFS / -1.0 dBTP` (`48kHz` stereo AAC `192k`)
- **Mandatory Hook & Open-Loop Rules**:
  - **Beat 1 / Cold Open**: `<= 18` syllables for `short_9x16`, `<= 24` syllables for `long_16x9`, **zero** `[pause:...]` tags in Beat 1. Combine physiological numbers/paradox (`?`, `70%`, `27 cân`, `24 giờ`) with direct address (`bạn`, `cơ thể bạn`).
  - **Early Open Loop (`sents[1:4]`)**: Introduce a surprising contrast or biological hinge (`nhưng`, `hóa ra`, `điều đáng sợ là`, `bên trong`) in the first 15 seconds.
  - **Prohibited CTAs**: Never use "like", "share", "subscribe", "đăng ký kênh", or `#learnontiktok`.
  - **Scientific Integrity**: Never claim miracle cures, never sell unverified supplements, cite peer-reviewed sources (`WHO`, `NIH`, `AHA`, `Harvard Health`, `CDC`, `Nature`) in descriptions, and include practical habit/doctor disclaimer when relevant.

## 2. Long `16:9` Physiological Dossier Structure (`10` Chapters, `240` Beats, `8.5–13m` / `510–780s`)

Every `long_16x9` episode spans **`10` `FFMETADATA1` chapters (`00:00..`)** and **`240` visual beats** (`<= 30s/sentence`):
1. **Cold Open & Physiological Shock (Chapter 1)**: Drop directly into the cellular/organ stress event at the 0-second mark — zero channel intros.
2. **Everyday Trigger -> Internal Cascade (Chapters 2–6)**: Trace the mechanism minute-by-minute or organ-by-organ with a re-hook before every chapter transition.
3. **Baseline vs Overload Comparison (Chapters 7–8)**: Contrast normal homeostasis vs chronic stress (`MODE_2_NORMAL_VS_STRESS_SPLIT`) and break down the 3 biological stages (`MODE_3_CASCADE_CHECKLIST`).
4. **Recovery Protocol & Next Episode Tease (Chapters 9–10)**: Summarize evidence-based protective habits, pose a reflective health question, and tease the next organ episode (`Một ngày của...`).

## 3. Short `9:16` Viral Funnel Structure (`18` Beats, `48–60s`, `<= 5.0s/sentence`)

Every `short_9x16` spin-off is authored natively (never raw-sliced from Long) and linked to `parent_long_id` via YouTube `Related Video` (`reel_multi_format_link`):
1. **Beats 1–3 (`0–5s`) — Rapid Sensory Paradox Hook**: At least `3` rapid cuts in the opening 5 seconds; Beat 1 `<= 18` syllables.
2. **Beats 4–10 (`5–32s`) — Microscopic Escalation**: Visual organ/cellular chain reaction (`2–3s/beat`).
3. **Beats 11–14 (`32–46s`) — Surprising Turning Point & Habit Fix**: One counter-intuitive scientific insight + actionable adjustment.
4. **Beats 15–18 (last 15%) — Close & Long Bridge**: `close` reflection + natural `bridge` `<= 20` syllables naming **"Cơ Thể Kể"** pointing directly to the full `parent_long_id` episode.


> **Core Visual & FX Skill:** [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md)
