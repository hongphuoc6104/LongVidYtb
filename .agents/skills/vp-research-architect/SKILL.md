---
name: vp-research-architect
description: "Architect research-backed conversational narratives, 3-tier academic funnel packaging, and full_frame_v1 pipeline blueprints."
---

# VP Research Architect (`sys/content/research_story_architect.py`)

Upstream engine that mines spoken-ready research facts, co-creates the human editorial stance, packages CTR metadata, and compiles Schema 3.0 `brief.json` + `content.json` (`visual_pacing_profile: "full_frame_v1"`).

## 1. Content Philosophy & 3-Tier Funnel (`sys/pillars.py`)
- **`ContentPhilosophy`**:
  - `cognition` (default): Cognitive psychology, mental models & epistemology simplified via Feynman.
  - `research_guide`: Step-by-step academic research for beginners. If a `tier_3_conversion` video uses `shot_type: "screen_capture"`, ask the user for `screen_capture_source` (`user_recorded` / `cdp_auto`) before proceeding.
- **Anti-Dilution Guard**: Zero shallow office hacks (Excel formulas, quick slide tips, rote tricks).
- **3-Tier Funnel (`funnel_tier`)**: `tier_1_broad` (cognitive phenomena & illusions) · `tier_2_mid` (first-principles methodology & causal mechanisms) · `tier_3_conversion` (deep analytical frameworks & tools).
- **Dynamic Depth (`content_depth_estimate`)**: Scene count and duration scale dynamically from `required_points`, `funnel_tier`, format (`long_16x9` vs `short_9x16`), and measured WAV duration.

## 2. 3-Step Blueprint Workflow
0. **NotebookLM Fact Vault Grounding (MANDATORY SSOT — Zero LLM-Memory Invention)**:
   - Before writing `brief.json` or `content.json`, load or import `fact_vault.json` via [vp-notebooklm-vault](../vp-notebooklm-vault/SKILL.md) (`sys/tools/notebooklm_vault.py`).
   - Populate `brief.sources[]` exclusively via `export_research_architect_sources(vault)` (`status == "verified"` ONLY — strictly quarantine/drop any `"report-only"` claims unless explicitly approved by user).
   - Pull `vietnam_micro_bridges` directly into the first 60s localization hook (`SC01–SC02` / `CH01`), copy `spoken_numbers_vi` / `pronunciation_glossary`, and export `format_youtube_sources_block(vault)` for YouTube descriptions.
1. **Spoken Fact Mining & Human Editorial Co-Creation**:
   - Focus on 1 core cognitive/practical paradox from `vault["surprising_hook_fact"]` with verified empirical evidence (`sources[].facts` written in clean spoken words — zero raw `DOI`, `et al.`, `%`, `/`).
   - Extract `topic_dilemmas` and generate topic-specific `dynamic_questions` (never hardcoded templates) to elicit human Analysis, Commentary, and Judgment into `brief.human_editorial` (`expanded_content_ideas`).
2. **CTR Packaging (`packaging` contract)**:
   - `youtube_title`: $\le 55$ chars with a curiosity gap (never self-answering).
   - `thumbnail_spec`: 100% Flow-native poster prompt (`build_thumbnail_poster_prompt()`) with 1 sharp visual metaphor (60% frame) + 2–4 uppercase hand-drawn words (`allowed_text`) in clean negative space (40% frame, `#F8F0DC`/`#FFFFFF`). Zero PIL/HTML card overlays.
3. **Adaptive Narrative & `build_scenes_from_story_rows()`**:
   - Pair `(spoken_clause_vi, "shot_type|visual_description")` across cognitive phases (`lived_friction` → `empirical_conflict` → `structural_model` → `actionable_resolution`) using registry `1.7.0` (`handdrawn_2d_explainer`, `sys/visual_style.py`).
   - `build_content_v3()` automatically computes coverage quotes, `based_on` room/expression locks, semantic camera effects, safe focus bounds, and `diversity_report`.

## 3. CLI & References
```bash
python3 sys/content/research_story_architect.py --demo
python3 sys/content/research_story_architect.py --topic academic-first-principles --spinoff-shorts
python3 sys/tools/build_full_frame_acceptance.py --output-dir sys/runs/full-frame-job
python3 sys/tools/fact_grounding_linter.py --content sys/runs/full-frame-job/content.json --vault sys/runs/full-frame-job/fact_vault.json --strict
```
- **References**: [vp-notebooklm-vault](../vp-notebooklm-vault/SKILL.md) · [fact-mining-guide.md](references/fact-mining-guide.md) · [conversational-structuring.md](references/conversational-structuring.md) · [pipeline-blueprint-spec.md](references/pipeline-blueprint-spec.md) · [vp-full-frame-quality](../vp-full-frame-quality/SKILL.md) · [visual-style.md](../vp-production/references/visual-style.md)
