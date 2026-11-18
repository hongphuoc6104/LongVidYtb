---
name: vp-notebooklm-vault
description: "3-Vault NotebookLM Grounded Pre-Production (Pattern Vault, Official Flow Prompt Rules Vault, and Bilingual Fact Vault) with Hybrid Dual-Mode CLI bridge and strict anti-hallucination verification across all 38 VN/EN channels."
---

# VP NotebookLM Vault (`vp-notebooklm-vault` — Layer 0 Grounding)

Layer-0 pre-production intelligence engine feeding `vp-research-architect`, `vp-channel-patterns`, `vp-scriptwriting`, `vp-full-frame-quality`, and `vp-flow-cdp`. Replaces LLM-memory fact invention with source-grounded vaults while preserving 100% of Video Pilot's automated execution stack (Flow CDP pool, Colab T4 OmniVoice `-11.0 LUFS`, `h264_nvenc` 2K, 5-Niche FX Warehouse, Bipolar GIS V5.0, YouTube Studio CDP).

## 1. The 3-Vault Architecture

| Vault | Scope & Lifecycle | Sources to Load | Output SSOT |
|---|---|---|---|
| **1. Pattern Vault** | Per channel / benchmark (`once`, refresh on breakout in `channel_learning_ledger.json`) | 10–15 top videos from **one** comparable channel + channel breakout records | `pattern_brief.json` (structure ONLY, zero copied phrasing; Short `<=18` syl hook, Long `<=24` syl cold open + 60–90s Retention Resets, Short→Long 15% bridge, zero `"like/share/subscribe"`) |
| **2. Official Prompt Rules Vault** | Global Flow SSOT (`once` + refresh when Google updates/retires models) | Official Google docs ONLY: Nano Banana 2.1 (`BELUGA`), Omni 1.2 Flash (`macaron_cookie`), Veo 3.1 Lite, Flow pricing/deprecation notes | [flow-prompt-rules-ssot.md](references/flow-prompt-rules-ssot.md) (Positive Framing, reference line phrasing, timecoded Veo Lite Seam vs Omni Frame-Link, Dec 5, 2026 deprecation locks) |
| **3. Episode Fact Vault** | Per episode (**clear sources & chat before every new topic**) | **Short (`short_9x16`)**: `Fast Research` (4–7 verified facts); **Long (`long_16x9`)**: `Deep Research` + primary PDFs (8–25 verified facts, bilingual EN + VN primary sources) | `fact_vault.json` (strictly drops `"report-only"` claims; generates `vietnam_micro_bridges`, `spoken_numbers_vi`, `pronunciation_glossary`, `chronicle_gis_anchors`, and YouTube `"Nguồn tham khảo"`) |

## 2. Vietnamese Localization & Dual-Language Channel Leverage
- **Bilingual Primary Grounding:** Match reputable source domains per archetype (e.g., NIH/WHO/Nature + Bộ Y Tế for `co_the_ke`, *Bộ luật Lao động/Dân sự/Nhà ở* for `luat_doi_thuong`, *Đại Việt Sử Ký Toàn Thư* for `su_ke_lai`, NTSB/IAEA/CSB/WHO for `ho_so_ky_la`/`chanh_niem_ke`, EIA/USGS/IMF for `ban_do_quyen_luc`/`banh_rang`).
- **Vietnam Micro-Bridges (`vietnam_micro_bridges`):** Mandatory scale/life translations for VN channels (`not channel_id.startswith("en_")`) feeding the first 60s localization gate in `vp-research-architect`.
- **VN ↔ EN Paired Leverage:** One verified `FactVault` can seed both a Vietnamese channel and its English twin (e.g., `co_the_ke` + `en_inside_vessel`, `ban_do_quyen_luc` + `en_choke_point`, `ho_so_ky_la` + `en_cold_case_ink`) without duplicating primary research.
- **Hiểu Tận Gốc V5.0 (`chanh_niem_ke`):** `export_chanh_niem_ke_manifest_seed()` extracts `pin_coordinates`, `pronunciation_glossary`, `vietnam_micro_bridges`, and causal domino anchors directly into `episode_manifest.json` while keeping 100% of GIS Map-Paper V5.0 untouched.

## 3. Hybrid Dual-Mode CLI (`sys/tools/notebooklm_vault.py`)
Supports both automated NotebookLM bridging (`notebooklm-py` / `nlm` CLI when installed, plus Chrome CDP pool planning obeying `.agents/rules/gpu-headless-chrome.md`) AND zero-dependency Web UI Markdown/JSON import + offline pattern fallback.

```bash
# 1. Inspect available bridge modes (read-only; never auto-launches Chrome):
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py bridge-status

# 2. Generate ready-to-paste Master Prompts for Notebook 1, 2 & 3 tailored to channel & topic:
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py render-prompts \
  --channel co_the_ke --topic "Cortisol 3 giờ sáng" --format long_16x9

# 3. Parse NotebookLM Web UI Markdown notes into validated fact_vault.json:
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py import-notes \
  --channel co_the_ke --topic "Cortisol 3 giờ sáng" --format long_16x9 \
  --input sys/runs/job/notes.md --output sys/runs/job/fact_vault.json

# 4. Validate Fact Vault & export verified brief.sources + YouTube source block:
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py validate --vault sys/runs/job/fact_vault.json
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py export-sources --vault sys/runs/job/fact_vault.json

# 5. Enforce zero unverified / report-only claims on final script (4th mandatory linter):
PYTHONPATH=sys sys/.venv/bin/python sys/tools/fact_grounding_linter.py \
  --content sys/runs/job/content.json --vault sys/runs/job/fact_vault.json --channel co_the_ke --strict
```

## 4. References
- [Master Prompts Pack (VN/EN Long & Short + Archetype Sources)](references/master-prompts-vn.md)
- [Offline Fallback Patterns (VN/EN Hooks, Pacing & Retention Resets)](references/fallback-patterns-vn.md)
- [Official Google Flow Prompt Rules SSOT (BELUGA, Veo 3.1 Lite, Omni 1.2 Flash)](references/flow-prompt-rules-ssot.md)
