---
name: vp-content-studio
description: "Pre-production intelligence: 3-Vault NotebookLM grounding, competitor pattern extraction, 3-tier funnel architecture, and conversational scriptwriting + 4 linter gates."
---

# VP Content Studio (`vp-content-studio`)

Unifies Video Pilot's 4 pre-production stages into one source-grounded workflow feeding [vp-visual-fx](../vp-visual-fx/SKILL.md) and [vp-production](../vp-production/SKILL.md):

1. **Stage 0 — 3-Vault NotebookLM Grounding (`sys/tools/notebooklm_vault.py`)**:
   - **Vault 1 (Pattern Vault):** Load 10–15 top videos from ONE comparable benchmark channel + `sys/channels/channel_learning_ledger.json` -> `pattern_brief.json` (structure ONLY, never copy phrasing).
   - **Vault 2 (Official Flow Rules Vault):** [flow-prompt-rules-ssot.md](references/flow-prompt-rules-ssot.md) (`BELUGA`, `Omni 1.2 Flash`, `Veo 3.1 Lite`, Dec 5, 2026 deprecation locks).
   - **Vault 3 (Episode Fact Vault):** Clear chat per new topic -> extract primary verified facts into `fact_vault.json` (strictly quarantine unverified `"report-only"` claims; export `vietnam_micro_bridges`, `spoken_numbers_vi`, `pronunciation_glossary`). Twin EN channels reuse the same verified Fact Vault via `./vp clone-en`.
2. **Stage 1 — Competitor & V4 Viral Forensics (`sys/channels/vn_competitor_script_formulas.py`)**:
   - **Standalone Mass-Curiosity Packaging:** `youtube_title <= 55` chars, zero `P1/P2/Tập` prefixes on Shorts, Beat 0 hook `<= 16–18` syllables (`0` pause tags, immediate human/curiosity stakes).
   - **Dual Short V4 Pacing:** `Mode A+ viral_fast_loop_short` (`15–16` beats, `54–72s`) and `Mode B serialized_detail_short` (`20–24` beats, `105–145s`) with final-15% debate-trigger ending + mirrored pinned comment loop.
3. **Stage 2 — Research & 3-Tier Funnel Architecture (`sys/content/research_story_architect.py`)**:
   - Follow `ContentPhilosophy` (`cognition` default, `research_guide` when requested — `tier_3_conversion` `screen_capture` requires `brief.screen_capture_source` from user) in `sys/pillars.py` across `tier_1_broad`, `tier_2_mid`, and `tier_3_conversion`.
   - Flow-native poster `thumbnail_spec` (`2–4` uppercase words drawn in, zero PIL/HTML overlay cards).
4. **Stage 3 — Conversational Scriptwriting & 4 Mandatory Linter Gates**:
   - Warm **Conversational Essayist** tone with Feynman chained simple sentences (`1-to-1` clause-to-visual pairing, zero comma between subject and verb, zero canned AI fillers like *"Bí mật nằm ở..."*, never *"like/share/subscribe"*).
   - Short (`short_9x16`): `parent_long_id` + close CTA (`<= 24` syl) + channel bridge (`<= 22` syl) inside the final 15% (`MAX_SHORT_OUTRO_SYLLABLES = 38`).

## Mandatory Commands & Progressive References
```bash
PYTHONPATH=sys python3 sys/tools/notebooklm_vault.py render-prompts --channel <id> --topic "<topic>" --format short_9x16
PYTHONPATH=sys python3 sys/tools/fact_grounding_linter.py --content <content.json> --vault <fact_vault.json> --strict
PYTHONPATH=sys python3 sys/tools/script_cadence_checker.py <content.json>
PYTHONPATH=sys python3 sys/tools/script_diversity_linter.py <content.json>
PYTHONPATH=sys python3 sys/tools/cta_tone_linter.py <content.json>
```
- **NotebookLM Vaults:** [master-prompts-vn.md](references/master-prompts-vn.md) · [fallback-patterns-vn.md](references/fallback-patterns-vn.md) · [flow-prompt-rules-ssot.md](references/flow-prompt-rules-ssot.md)
- **Research & Architecture:** [fact-mining-guide.md](references/fact-mining-guide.md) · [conversational-structuring.md](references/conversational-structuring.md) · [pipeline-blueprint-spec.md](references/pipeline-blueprint-spec.md)
- **Scriptwriting & Voice Cadence:** [conversational-essayist-framework.md](references/conversational-essayist-framework.md) · [spoken-narration-guide.md](references/spoken-narration-guide.md) · [voice-cadence-pacing.md](references/voice-cadence-pacing.md)
- **Pattern Analysis Playbooks:** [analysis-rubric.md](references/analysis-rubric.md) · [adaptation-playbook.md](references/adaptation-playbook.md) · [decision-framework.md](references/decision-framework.md) · [video-pilot-integration.md](references/video-pilot-integration.md)
