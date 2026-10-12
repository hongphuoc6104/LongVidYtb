# Causal Explanatory Script & Cadence Standards

Read the brief/profile, selected sense, audience and required points. Every video script must adhere to the **Conversational Essayist** standard and 5-part storytelling framework ([vp-scriptwriting](../../vp-scriptwriting/SKILL.md)):
1. **Hook & Empathy (0–15%):** Start with an intimate everyday situation or dilemma to ground viewer attention immediately.
2. **Reframe & Dilemma (15–35%):** Challenge conventional assumptions with an intriguing paradox or rhetorical question.
3. **Causal Evidence 70/30 (35–65%):** Balance 70% engaging conversational flow with 30% verified scientific/historical facts, figures, and causal mechanisms.
4. **Direct Contrast (65–85%):** Contrast two opposing realities side-by-side to deliver strong visual and intellectual tension.
5. **Loop Closure & Payoff (85–100%):** Revisit the opening metaphor to resolve the narrative arc with reflective depth.

## 1. Cadence, Syllable Formula & Duration Tolerance
To eliminate acoustic dead-air and maintain exact audio synchronization:
- Apply the acoustic dead-air formula:
  $$\text{Target Syllables} = \text{round}\Big((\text{Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$$
  where $P_{\text{tail}} = 0.70\text{s}$ for intermediate scenes (`para`) and $0.35\text{s}$ for the final scene (`tail`).
- Enforce strict timeline tolerance: absolute drift must be within **$\pm 0.5\text{s}$** (optimal drift $\le 0.30\text{s}$). See [voice-cadence-pacing.md](../../vp-channel-patterns/references/voice-cadence-pacing.md) and [adaptation-playbook.md](../../vp-channel-patterns/references/adaptation-playbook.md).
- Validate scripts before synthesis using `sys/tools/script_cadence_checker.py`. Reject scripts with speech rate outside 3.2 – 4.5 syllables/s or drift exceeding $\pm 0.5\text{s}$.
- **Direct & Concise Narration:** Start immediately with the core point (zero greetings, zero filler intros like *"Hãy nghĩ về..."* / *"Hãy hình dung..."*). Keep academic credentials (`Prof. A at Univ. B`, year, DOI) in `brief.json` (`sources[].reference`) only—never read researcher titles or universities in spoken narration. Every source fact and claim must be spoken Vietnamese $\le 20$ syllables (hard threshold $22$) with no `DOI:`, `et al.`, `ISBN:`, `%`, `/`.
- **Sentence Fragmentation Guard:** Avoid chopping scenes into $> 2$ micro-sentences ($< 6$ syllables) to prevent vocal stuttering.

## 2. Short Scene Splitting & Visual Beats
- **Prefer multiple short scenes (`5.0s–9.0s`, `1–2` concise sentences, `16–32` syllables) over long monologues:** Deliver one crisp idea per scene and split multi-idea paragraphs into separate scenes (keep floor $> 2.5\text{s}$ to avoid $P_{\text{tail}}$ padding inflation), paired with `beats[]` ($\le 3.8\text{s}$/shot) anchored to narration keywords.

## 3. Script Invariants & Repair Discipline
- Author outline purpose/transition and visible action before selecting scene/image counts for this job. Write complete narration first; freeze it before coverage, claims and verbatim anchors. A scene count stored after planning is a contract, not a universal recipe.
- Keep correct English pronouns (including I) and learner text in its actual language. Explain usage/grammar/pronunciation in context rather than reading headings. Keep all required points; change the brief through workflow if the request genuinely changes.
- On repair, quote the concrete affected line, preserve unrelated valid work and log the version impact. Do not fabricate self-approval or invoke a reviewer in auto.
