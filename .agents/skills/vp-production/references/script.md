# Causal Explanatory Script & Cadence Standards

Read the brief/profile, packaging contract, audience and required points. Every video script must adhere to the **Conversational Essayist** standard, the **3-Tier Academic Research Funnel** (*"Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật"*), and the 5-part storytelling framework ([vp-scriptwriting](../../vp-scriptwriting/SKILL.md)):
1. **Counter-Intuitive / Truth-Slap Hook & Empathy (0–15%):** Open with a counter-intuitive truth-slap statement ($\le 18$ syllables in the first sentence of `SC01`), **zero `[pause:...]` tags in `SC01`**, `4.2–4.4` syl/s pacing (`1.26x` on `short_9x16`), and 100% Vietnamese cultural localization in the first 60s (exam/thesis night, highlighting textbooks, opening Word at 2 AM, 120s before the defense committee).
2. **Reframe & Dilemma (15–35%):** Challenge conventional assumptions with an intriguing scientific/academic paradox + at most 1 `[pause:900ms]` before the reveal.
3. **Causal Evidence 70/30 (35–65%):** Balance 70% visual diagram-driven flow (*Academic Pyramid*, `Question → Gap → Method → Evidence` flowchart) with 30% verified spoken facts ($\le 20$ syllables).
4. **Direct Contrast (65–85%):** Contrast two opposing approaches side-by-side at Rule-of-Thirds coordinates (`x = 0.35` vs `x = 0.64`).
5. **Loop Closure & Payoff (85–100%):** Revisit the opening scene at `3.6–3.8` syl/s to resolve the narrative arc and trigger Save/Bookmark actions.

## 1. Cadence, Syllable Formula & Hard Guards
To eliminate acoustic dead-air and maintain exact audio synchronization:
- Apply the acoustic dead-air formula:
  $$\text{Target Syllables} = \text{round}\Big((\text{Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$$
  where $P_{\text{tail}} = 0.70\text{s}$ for intermediate scenes (`para`) and $0.35\text{s}$ for the final scene (`tail`).
- Enforce strict timeline tolerance: absolute drift must be within **$\pm 0.5\text{s}$** (optimal drift $\le 0.30\text{s}$). See [voice-cadence-pacing.md](../../vp-channel-patterns/references/voice-cadence-pacing.md) and [adaptation-playbook.md](../../vp-channel-patterns/references/adaptation-playbook.md).
- Validate scripts before synthesis using `sys/tools/script_cadence_checker.py --forbid-opening-pause --max-opening-hook-syllables 18 --max-sentence-syllables 25 --max-clause-syllables 18 --max-dramatic-pauses 4 --strict`:
  - `OPENING_SCENE_PAUSE_FORBIDDEN`: Zero `[pause:...]` tags allowed in `SC01` (first 15s).
  - `OPENING_HOOK_TOO_LONG`: First sentence of `SC01` must be $\le 18$ syllables.
  - `SENTENCE_TOO_LONG` & `BREATHLESS_CLAUSE`: Every sentence must be $15–25$ syllables ($\le 25$ hard cap); every clause without a comma must be $\le 18$ syllables.
  - `EXCESSIVE_DRAMATIC_PAUSES`: Reserve `[pause:800ms]` / `[pause:900ms]` for Tier-3 dramatic reveals only (1–3 times per video, hard cap 4).
- **Direct & Concise Narration:** Start immediately with the core point (zero greetings, zero banned intros like *"Hãy nghĩ về..."* / *"Hãy hình dung..."* / *"Hãy tưởng tượng..."* / *"Giờ đây, hãy thử..."*). Keep academic credentials (`Prof. A at Univ. B`, year, DOI) in `brief.json` (`sources[].reference`) only—never read researcher titles or universities in spoken narration. Every source fact and claim must be spoken Vietnamese $\le 20$ syllables (hard threshold $22$) with no `DOI:`, `et al.`, `ISBN:`, `%`, `/`.
- **Sentence Fragmentation Guard:** Avoid chopping scenes into $> 2$ micro-sentences ($< 6$ syllables) to prevent vocal stuttering.

## 2. Short Scene Splitting & Dual-Zone Visual Beats
- **Prefer concise scenes (`5.0s–15.0s`, floor $> 2.5\text{s}$ to avoid $P_{\text{tail}}$ padding inflation) paired with Dual-Zone Visual Beats:**
  - **Danger Zone (`0:00–0:15` / `SC01–SC02`):** Change camera beats or pop in stickers every **`1.2s–1.8s`**.
  - **Body Zone (`after 0:15` / `SC03+`):** Keep each visual beat hold within **`0.83s–3.80s`** anchored to narration keywords.

## 3. Script Invariants & Repair Discipline
- Author outline purpose/transition and visible action before selecting scene/image counts for this job. Write complete narration first; freeze it before coverage, claims and verbatim anchors.
- Keep correct English pronouns (including I) and learner text in its actual language. On repair, quote the concrete affected line, preserve unrelated valid work and log the version impact.
