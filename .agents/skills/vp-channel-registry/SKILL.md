---
name: vp-channel-registry
description: "Route any of the 38 VN/EN channels to its rollout wave, Niche Archetype pack, and 3-pillar data playbook (overview, content, visual, pacing)."
---

# VP Channel Registry & 3-Pillar Data Router (38 Channels)

Zero per-channel skills live in `.agents/skills/`. All **38 physical channels** (`20 VN + 18 EN`, deduplicated in `sys/channels/youtube_channel_map.json`) store their channel-specific identity and 3 pillars (`content.md`, `visual.md`, `pacing.md` + `overview.md`) as **data** inside `sys/channels/<channel_id>/playbook/`, charging `0` background context tokens until needed.

## 1. Progressive Channel Lookup (3 Steps)
1. **Resolve Channel Lifecycle, Wave & Archetype Pack:**
   - Run `./vp status` or `./vp channels` (SSOT: `sys/channels/lifecycle_ssot.py`, `sys/channels/fleet_lifecycle.json`, `sys/short_engine/archetype_packs.py` `get_channel_short_pack()`).
2. **Load Archetype Rules:**
   - [Archetype 1 — Forensic Noir](references/archetypes/archetype-1-forensic-noir.md) (`ho_so_ky_la`, `luat_ngam`, `nghe_song_sot` + EN)
   - [Archetype 2 — Geopolitics & History](references/archetypes/archetype-2-geopolitics-history.md) (`su_ke_lai`, `ban_do_quyen_luc`, `chanh_niem_ke`, `banh_rang` + EN)
   - [Archetype 3 — Science & X-Ray](references/archetypes/archetype-3-science-xray.md) (`co_the_ke`, `dia_com`, `ua_sao_vay`, `vu_tru_ti_hon` + EN)
   - [Archetype 4 — 2D Doodle & Explainability](references/archetypes/archetype-4-doodle-explainer.md) (`ai_binh_dan`, `la_ban_hoc_thuat`, `luat_doi_thuong`, `nao_luoi`, `thuong_cho_kheo`, `tui_tien` + EN)
   - [Archetype 5 — Mindful & Philosophy](references/archetypes/archetype-5-mindful-healing.md) (`loi_sang_soi`, `minh_triet_song`, `tam_tinh_dem` + EN)
3. **Read the Channel's 3-Pillar Playbook (`sys/channels/<channel_id>/playbook/`):**
   ```bash
   ./vp playbook <channel_id>                 # View overview + file paths
   ./vp playbook <channel_id> --pillar visual # Print specific pillar (overview|content|visual|pacing|all)
   ./vp playbook --validate-all               # Verify all 38/38 playbooks and links
   ```

## 2. Rollout Waves & Flagship Playbook Quick Links
- **Wave 0 (`ACTIVE`):** [Sử Kể Lại (`su_ke_lai`)](../../../sys/channels/su_ke_lai/playbook/overview.md) (`heroic_vietnam_epic`, V4 Short + M1-Flex V9.2 Long)
- **Wave 1 (`CANARY` Ready — VN 3D/GIS):** [Bản Đồ Quyền Lực](../../../sys/channels/ban_do_quyen_luc/playbook/overview.md) · [Cơ Thể Kể](../../../sys/channels/co_the_ke/playbook/overview.md) · [Hồ Sơ Kỳ Lạ](../../../sys/channels/ho_so_ky_la/playbook/overview.md) · [Hiểu Tận Gốc (`chanh_niem_ke`)](../../../sys/channels/chanh_niem_ke/playbook/overview.md)
- **Wave 2–3 (Remaining 15 VN)** & **Wave 4–5 (18 EN Twins):** Promote with `./vp activate <channel_or_wave> --state CANARY|ACTIVE` and clone verified VN Short V4 specs to EN twins via `./vp clone-en`.
