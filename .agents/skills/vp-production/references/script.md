# Causal Explanatory Script & Cadence Standards

Read the brief/profile, packaging contract, audience and required points. Every video script adheres to the **Conversational Essayist** standard, the **3-Tier Funnel** (*"Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"*), and the adaptive storytelling flow ([vp-scriptwriting](../../vp-scriptwriting/SKILL.md)):
1. **Relatable Hook & Problem Framing:** Open with a relatable real-world observation or counter-intuitive dilemma in `SC01` (`VietNarrator` `speed: 1.0` on `short_9x16` and `long_16x9`), establishing immediate viewer connection.
2. **Reframe & Cognitive Tension:** Challenge conventional assumptions, exposing the gap between common perception and underlying mechanism.
3. **Causal Evidence & Feynman Explanation:** Deconstruct the core mechanism using simple declarative sentences chained together (Feynman Technique), supported by clear visual diagrams and empirical evidence.
4. **Multi-Perspective & Contrast:** Examine counter-arguments, boundaries, or practical nuances to provide balanced, rigorous depth.
5. **Loop Closure & Actionable Payoff:** Revisit the opening concept to resolve the narrative loop and deliver concrete intellectual value.

## 1. Cadence, Syllable Formula & Advisory Guidance
To maintain natural acoustic flow and audio synchronization:
- Apply the acoustic dead-air formula:
  $$\text{Target Syllables} = \text{round}\Big((\text{Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$$
  where $P_{\text{tail}} = 0.70\text{s}$ for intermediate scenes (`para`) and $0.35\text{s}$ for the final scene (`tail`).
- Timeline tolerance guideline: absolute drift within **$\pm 0.5\text{s}$** (optimal drift $\le 0.30\text{s}$). See [voice-cadence-pacing.md](../../vp-channel-patterns/references/voice-cadence-pacing.md) and [adaptation-playbook.md](../../vp-channel-patterns/references/adaptation-playbook.md).
- Validate scripts using `sys/tools/script_cadence_checker.py` (runs in soft advisory mode by default; `--strict` is optional):
  ```bash
  python3 sys/tools/script_cadence_checker.py path/to/content.json
  ```
  Advisory notices highlight potential pacing improvements:
  - Opening scene pause guidance: keeps opening dialogue engaging without excessive pauses.
  - Opening hook brevity: encourages concise, punchy opening statements.
  - Sentence and clause flow: recommends natural breath pauses and warns against breathless clauses without commas.
  - Dramatic pause pacing: reserves intentional `[pause:...]` tags for key conceptual reveals.
- **Direct & Conversational Narration (Feynman Technique):** Start directly with the core observation or question. Express complex concepts through chained simple sentences (one idea per sentence). Keep academic credentials (`Prof. A at Univ. B`, year, DOI) in `brief.json` (`sources[].reference`) only—convey evidence in spoken, natural Vietnamese without clunky academic notation (`DOI:`, `et al.`, `ISBN:`, `%`, `/`).
- **Sentence Flow:** Balance punchy declarative takeaways with natural explanatory clauses to prevent vocal monotony.

## 2. Dynamic Scene Pacing & Dual-Zone Visual Beats
- **Concise, well-paced scenes paired with Dual-Zone Visual Beats:**
  - **Opening Zone (`0:00–0:15` / `SC01–SC02`):** Use narration-anchored full-frame images with dynamic visual pacing to establish immediate engagement against measured audio.
  - **Body Zone (`after 0:15` / `SC03+`):** Build visual beats progressively using the Feynman Visual Formula (1 character + 1 focal metaphor on a clean flat canvas), holding visual beats within natural comprehension windows (`0.83s–3.80s`).

## 3. Script Invariants & Repair Discipline
- Author outline purpose/transition and visible action before selecting scene/image counts for this job. Write complete narration first; freeze it before coverage, claims and verbatim anchors.
- Dynamic duration and scene counts are determined by `content_depth_estimate` and actual synthesized audio length, not fixed formulas.
- Keep correct English pronouns (including I) and learner text in its actual language. On repair, quote the concrete affected line, preserve unrelated valid work and log the version impact.
