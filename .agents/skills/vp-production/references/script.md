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
- **Conversational Spoken Facts (ERR-20261011-03):** Every source fact and claim must be spoken Vietnamese $\le 20$ syllables (hard threshold $22$). Dry academic notation (`DOI:`, `et al.`, `ISBN:`, `%`, `/`) is strictly prohibited.
- **Sentence Fragmentation Guard:** Avoid chopping scenes into $> 2$ micro-sentences ($< 6$ syllables) or $> 4$ sentences within a $\le 16.0s$ scene to prevent vocal stuttering.

## 2. Visual Beats vs Scene Splitting
- **Never chop continuous speech into micro-scenes ($D \le 2.5\text{s}$):** Accumulated $P_{\text{tail}}$ padding will inflate the overall timeline by +35% to +70% and fragment vocal naturalness.
- Maintain coherent 10–14s parent scenes and organize internal visual transitions using `beats[]` with semantic anchors mapped to specific narration keywords.

## 3. Script Invariants & Repair Discipline
- Author outline purpose/transition and visible action before selecting scene/image counts for this job. Write complete narration first; freeze it before coverage, claims and verbatim anchors. A scene count stored after planning is a contract, not a universal recipe.
- Keep correct English pronouns (including I) and learner text in its actual language. Explain usage/grammar/pronunciation in context rather than reading headings. Keep all required points; change the brief through workflow if the request genuinely changes.
- On repair, quote the concrete affected line, preserve unrelated valid work and log the version impact. Do not fabricate self-approval or invoke a reviewer in auto.
