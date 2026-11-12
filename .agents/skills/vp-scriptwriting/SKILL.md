---
name: vp-scriptwriting
description: "Author and transform explainer video scripts into natural conversational spoken storytelling with counter-intuitive 3-second hooks and calibrated acoustic cadence."
---

# VP Scriptwriting — Conversational Essayist & Feynman Cadence

Authors and validates spoken Vietnamese/English explainer scripts (`long_16x9` and `short_9x16`) paired 1-to-1 with `full_frame_v1` visual actions.

## 1. Core Scriptwriting Invariants
1. **Voice & Human Editorial Spine (`human_editorial`)**: Warm, sharp **Conversational Essayist** tone grounded in `sys/pillars.py` (`ContentPhilosophy`). Lead with human analysis, critique, and value judgment (`editorial_stance` + `expanded_content_ideas`); never write neutral Wikipedia-style summaries.
2. **Relatable Grounded Hook (`SC01`)**: Open directly with a concrete everyday friction or counter-intuitive observation ($\le 18$ syllables in the first sentence for Shorts, zero `[pause:...]` in `SC01`). Never open with greetings (*"Xin chào"*), meta-announcements (*"Hôm nay chúng ta..."*), or slow lead-ins (*"Hãy nghĩ về/tưởng tượng..."*).
3. **Feynman Chained Simple Sentences**: One idea per declarative sentence; alternate short punchy sentences (`3–8` words) with clear causal explanations (`15–24` words). Never insert a comma between subject and verb. Prefer smooth native Vietnamese words over hyphenated loanwords (`"vi-đê-ô"`).
4. **Zero AI-Translationese & Canned Markers**: Strictly forbid throat-clearing clichés (*"Có một sự thật mất lòng là..."*, *"Bí mật/Nghịch lý/Mấu chốt nằm ở..."*, *"Đánh giá công bằng thì..."*, *"Ít ai biết rằng..."*, *"Tin vui/buồn là..."*, *"Tóm lại là..."*). State `Subject + Action/Fact` directly (full table in [spoken-narration-guide.md](references/spoken-narration-guide.md)).
5. **1-to-1 Sentence-Beat Pairing**: Pair each spoken sentence/clause (`split_long_sentence_into_beat_clauses()`) with `"shot_type|visual_action"` across the 10 standard shot types (`full_scene`, `variation`, `macro_prop`, `visual_diagram`, `concept_metaphor`, `cutaway_detail`, `white_card`, `white_isolated`, `still_life`, `environment`). Follow the Feynman Visual Formula (1 doodle stickman + 1 focal metaphor, $\ge 60\%$ negative space).
6. **V2 CTA & Short→Long Bridge (`cta_tone_linter.py`)**: Every short carries `parent_long_id`; final 15% contains exactly 1 close CTA ($\le 24$ syllables) + 1 channel-named bridge ($\le 22$ syllables) spoken verbatim in the last scene (zero CTA in the first 3s). Long videos allow $\le 1$ `mid_cta` at 35–45%. Never say *"like, share, subscribe, nhấn chuông, đăng ký kênh"*.
7. **Active Pause Authoring (`format_v1`)**: Default pauses come from `sys/format_profiles.py` via `narration_pauses.py`. Use intentional pivot tags sparingly (`450ms` short / `600ms` long; $\le 3$ dramatic `800–900ms` tags in `SC02+`).

## 2. Mandatory Linters
```bash
python3 sys/tools/script_cadence_checker.py path/to/content.json
python3 sys/tools/script_diversity_linter.py path/to/content.json
python3 sys/tools/cta_tone_linter.py path/to/content.json
```

## 3. Progressive Disclosure References
- **Conversational Essayist Framework & Exemplars**: [conversational-essayist-framework.md](references/conversational-essayist-framework.md)
- **Everyday Spoken Vietnamese & Banned Clichés**: [spoken-narration-guide.md](references/spoken-narration-guide.md)
- **Voice, Cadence & Pacing Specs**: [voice-cadence-pacing.md](../vp-channel-patterns/references/voice-cadence-pacing.md)
- **Production Script & Audio Guides**: [script.md](../vp-production/references/script.md) · [audio.md](../vp-production/references/audio.md) · [vp-full-frame-quality](../vp-full-frame-quality/SKILL.md)
