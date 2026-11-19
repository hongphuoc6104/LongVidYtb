# Master Prompts Pack — NotebookLM 3-Vault Workflow (VN & EN, Long & Short)

Paste the exact prompt matching your Vault and target format. Fill text in `[BRACKETS]`. Never skip `"report-only"` quarantine.

---

## Notebook 1: Pattern Vault (Run Once Per Benchmark Channel, Refresh on Breakout)
**Sources:** 10–15 top-performing videos (YouTube URLs) from **ONE** reference channel in the same format + 2–3 internal retention notes (or top videos from `channel_learning_ledger.json`).

### 1A. Short Pattern Prompt (`short_9x16`, 48–60s)
```text
You are a retention pattern analyst for [LANGUAGE: Vietnamese / English] vertical shorts ([CHANNEL_NAME], niche: [NICHE]).
Use ONLY the sources in this notebook. Study narrative structure and pacing ONLY — NEVER quote, translate, or reuse sentences/phrases from the videos.
Output 400 words max with these exact sections:
1. Hook types (top 4): name, fill-in-the-blank structural formula (first sentence <= 18 syllables in Vietnamese or <= 12 words in English), when to use, exact seconds (must land < 3.0s).
2. 48-60s Pacing Map: beat-by-beat job across 12-18 visual beats, syllable/word count per beat, where the primary number lands, where the twist turns.
3. Retention techniques (top 5): exact mechanism and timestamp range.
4. Ending & Long-Bridge patterns (top 3): how the final 15% closes the open loop, pivots naturally to the parent long video (NEVER say like/share/subscribe/nhấn chuông), and triggers debate comments.
5. Tone & Cadence rules: spoken sentence lengths, forbidden AI-translationese fillers, silence/pause discipline.
6. Patterns appearing in >= 70% of videos.
If sources do not confirm an item, write "not shown in sources".
```

### 1B. Long Pattern Prompt (`long_16x9`, 8m30s–14m)
```text
You are a documentary retention analyst for [LANGUAGE: Vietnamese / English] long-form explainers ([CHANNEL_NAME], niche: [NICHE]).
Use ONLY the sources in this notebook. Study narrative structure ONLY — NEVER copy phrasing or scripts.
Output 500 words max with these exact sections:
1. Cold Open & Open Loop (0-45s): structural formula, first sentence <= 24 syllables (VN), exact timing of the central paradox/stakes.
2. Chapter / Domino Architecture (8-10 chapters or 5 causal acts): progression from symptom -> root mechanism -> false assumption -> turning point -> resolution.
3. Retention Resets (every 60-90s): top 5 re-hook transitions that reset viewer attention without clickbait.
4. Everyday Translation Devices: how abstract data/science/law is converted into physical analogies and local scale comparisons.
5. Soft Mid-CTA (35-45%) & Closing Debate Trigger: exact phrasing geometry without begging for likes/subscribes.
6. Patterns appearing in >= 70% of videos.
If sources do not confirm an item, write "not shown in sources".
```

### 1C. Serialized Cinematic Tactical Short Pattern Prompt (`serialized_detail_short`, 140–170s/tập · 24–28 beats · < 180s)
```text
You are a serialized short-form documentary analyst for [LANGUAGE: Vietnamese / English] multi-part vertical tactical breakdowns ([CHANNEL_NAME], niche: [NICHE]).
Use ONLY the sources in this notebook. Study 5-act dramatic pacing, causal analysis, and cliffhanger architecture ONLY — NEVER quote or reuse phrases.
Output 500 words max:
1. Hook & Strategic Dilemma (Act 1, B00-B04): top 4 hook formulas (<= 18 syllables, zero pause), opening immediately inside a life-or-death strategic dilemma and counter-intuitive paradox.
2. 5-Act Cinematic Tactical Breakdown (140-170s, 24-28 beats/tập, strictly < 180s ceiling): how a campaign splits into Tập 1 / Tập 2 / Tập 3 following:
   - Act 1 (B00-B04): Strategic dilemma & paradox.
   - Act 2-3 (B05-B13): Dissecting 2-3 interlocking trap layers, causal/psychological mechanism, and exact failure mode if 1 step slips ("sai 1 bước chết ở đâu").
   - Act 4 (B14-B21): Tension compression (rapid short clauses) -> breath-hold climax inflection point ([pause:450-650ms] + silence vacuum) -> explosive payoff.
   - Act 5 (B22-B27): Human tactical takeaway lesson + serialized cliffhanger for Tập tiếp theo.
3. Causal & Psychological Mechanism Rules: how to weave verified terrain, timing, and human-psychology details explaining WHY the trap forced the enemy into error without textbook clichés.
4. Part-to-Next-Part & Long-Form Bridge Rules: natural final 15% outro (bridge <= 22 syl, close <= 24 syl, combined <= 38 syl) teasing Tập tiếp theo & parent_long_id without begging like/share/subscribe.
5. Source Hygiene: separating verified primary chronicles from unconfirmed folklore ("dã sử / tương truyền").
```

---

## Notebook 2: Official Flow Prompt Rules Vault (Global SSOT)
**Sources:** Official Google documentation ONLY (Nano Banana 2.1 / `BELUGA`, Omni 1.2 Flash `macaron_cookie`, Veo 3.1 Lite, official Flow help & pricing/deprecation updates). Zero third-party blogs.
```text
You are a prompting-technique analyst. Use ONLY the official documentation in this notebook.
Give me a Prompt Rules Brief for Google Flow covering:
1. Image prompt element order (BELUGA / Nano Banana 2.1): subject, state/count, setting, composition/camera, lighting/palette, style block, and positive-framing rules.
2. Visual continuity across scenes: exact reference-image wording ("Using the attached reference image(s), the same ...") and verbatim style block locking.
3. Video prompt formula for image-to-video:
   - Veo 3.1 Lite (720p, 4s/6s/8s @ 10 credits flat): start-frame only, 70-100 words, one camera move + one secondary motion, explicit anti-symbol/anti-text surface rules, Seam Mode suitability.
   - Omni 1.2 Flash (`macaron_cookie`, 4s/6s/8s/10s @ 3 credits/sec 720p): 40-70 words, Frame-Link (first + last frame) rules and when lighting/cast mismatch causes morphing.
4. Retired/deprecating models to avoid (Veo Extend retired Nov 5 2026; Veo 3.1 Fast/Quality & Omni 1.1 retiring Dec 5 2026).
5. Starter templates with [brackets].
Mark anything absent from official docs as "not in docs".
```

---

## Notebook 3: Episode Fact Vault (Clear Sources & Chat Before EVERY New Topic!)

### Step 1 — Research Box (Select `Fast Research` for Short / `Deep Research` for Long)
**Channel Source Priorities by Archetype:**
- **Archetype 1 (`ho_so_ky_la`, `luat_ngam`, `nghe_song_sot`):** NTSB/AAIB/maritime official inquiry dockets, peer-reviewed behavioral studies, HBR/BLS/McKinsey workforce datasets.
- **Archetype 2 (`ban_do_quyen_luc`, `su_ke_lai`, `banh_rang`, `chanh_niem_ke`):** USGS/EIA/UN Comtrade/IMF/World Bank, IAEA/CSB/WHO disaster reports, *Đại Việt Sử Ký Toàn Thư* & primary military-geography studies.
- **Archetype 3 (`co_the_ke`, `vu_tru_ti_hon`, `ua_sao_vay`, `dia_com`):** NIH, PubMed, WHO, AHA, CDC, Nature, NASA/ESA, *Bộ Y Tế Việt Nam*, peer-reviewed food chemistry & physics journals.
- **Archetype 4 (`nao_luoi`, `tui_tien`, `luat_doi_thuong`, `ai_binh_dan`, `la_ban_hoc_thuat`, `thuong_cho_kheo`):** *Bộ luật Lao động 2019 / Bộ luật Dân sự 2015 / Luật Nhà ở*, *Thư Viện Pháp Luật*, official Vietnamese tax/banking schedules, peer-reviewed cognitive/relationship studies (Gottman, APA), official AI docs.
- **Archetype 5 (`loi_sang_soi`, `tam_tinh_dem`, `minh_triet_song`):** Historical-critical biblical/classical commentaries, primary translated texts (*Đạo Đức Kinh*, *Trang Tử*, Marcus Aurelius *Meditations*, Seneca).

```text
TOPIC: [TOPIC]
CHANNEL: [CHANNEL_ID] ([NICHE])
FORMAT: [short_9x16 | long_16x9 | serialized_detail_short]
AUDIENCE: [AUDIENCE]
Find authoritative primary sources in [RECOMMENDED_SOURCES].
Prioritize verified facts with exact numbers/units/dates, causal mechanisms, physical/visual appearance details, and Vietnam-relevant context where applicable.
```

### Step 2 — Source-Grounded Chat Prompt (After Importing Checked Sources)
```text
TOPIC: [TOPIC]
CHANNEL: [CHANNEL_ID] | FORMAT: [short_9x16 | long_16x9 | serialized_detail_short] | AUDIENCE: [AUDIENCE]
Use ONLY the original sources imported into this notebook.
If a Deep/Fast Research summary report is also attached, ONLY keep a claim from that report if at least one primary source in the notebook confirms it; otherwise place it inside section 8 labeled "report-only". Do NOT fill gaps from memory.

Produce Research Notes in Vietnamese (with exact English technical terms only in parentheses if needed):
1. Key facts ([4-7 for Short / 12-18 tactical & causal details for serialized_detail_short / 12-22 for Long]): each with exact number, unit, hour/date/scope, and [Source Name] in brackets. Separate verified primary chronicles from folklore ("dã sử / tương truyền" -> quarantine in section 8 as report-only if unverified).
2. Most surprising paradox / counter-intuitive hook fact and why audiences assume the opposite.
3. Step-by-step causal mechanism in plain spoken Vietnamese (easy to hear aloud; for serialized_detail_short also map the 5-act strategic dilemma, failure mode if 1 step slips, causal/psychological mechanism, breath-hold climax inflection point, human tactical takeaway lesson, and Tập 1 / Tập 2 / Tập 3 cliffhanger split).
4. Analogies & Vietnam Micro-Bridges (2-3 concrete comparisons to everyday Vietnamese life, VND/km/scale, safe for the first 60 seconds).
5. Visual appearance notes: concrete colors, textures, scale, instruments, locations, and time of day (for visual prompts without text on screen).
6. Common misconception and exact source-backed correction.
7. Spoken numbers & Pronunciation Glossary: spell out tricky foreign names, abbreviations, and numeric forms for TTS (e.g., "AZ-5" -> "A Zét năm").
8. Report-only & Conflicts/Gaps: list any unverified report-only claims, source disagreements, or missing facts.
(If channel is chanh_niem_ke, also append Section 9: Geographic coordinates [lon, lat], region bounds, and chronological causal chain steps.)
No medical diagnosis/cure promises, no guaranteed legal outcomes, and no financial advice guarantees.
```
