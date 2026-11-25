# Start here — Video Pilot

## Mandatory Pre-Task Reading Protocol (Priority Document Gate)
Before initiating any task, every agent MUST follow the 3-tier reading protocol:
1. **Tier 1 (Mandatory for ALL tasks)**: [AGENTS.md](AGENTS.md) and [PLAYBOOK.md](PLAYBOOK.md).
2. **Tier 2 (Domain Skill SSOT)**: Read one of the 7 Core `SKILL.md` modules below.
3. **Tier 3 (Channel Data & Deep Reference)**: Inspect `sys/channels/<channel_id>/playbook/{overview,content,visual,pacing}.md` (`./vp playbook <id>`) and `.agents/skills/<skill>/references/`.

---

## Task Routing Table (7 Consolidated Core Skills)

| Task | Guide | Core Skill |
|---|---|---|
| Lookup any of the 38 VN/EN channels (`wave_0..5`, 5 Archetypes, 3-pillar data playbooks) | `./vp playbook <id>` | [vp-channel-registry](.agents/skills/vp-channel-registry/SKILL.md) |
| Layer-0 3-Vault NotebookLM, Pattern Forensics, Research Architect, Scriptwriting & 4 Linters | [Story planning](sys/docs/story-planning.md) | [vp-content-studio](.agents/skills/vp-content-studio/SKILL.md) |
| Visual Grammar (`1.7.0 Nguệch Ngoạc`), Two-Stage SceneMap & Sharded 30fps FX Warehouse (`--fx-mode auto_niche`) | [Render capabilities](sys/docs/render-capabilities.md) | [vp-visual-fx](.agents/skills/vp-visual-fx/SKILL.md) |
| Automated Flow CDP image (`BELUGA`) & Dual-Model video generation (`veo_3_1_lite` / `omni_flash`) | [Flow prompts](sys/docs/flow-prompts.md) | [vp-flow-cdp](.agents/skills/vp-flow-cdp/SKILL.md) |
| Remote Colab T4 OmniVoice TTS (`-11.0 LUFS`) & native FFmpeg `h264_nvenc` render | [Colab TTS](sys/docs/colab-tts.md) | [vp-colab-bridge](.agents/skills/vp-colab-bridge/SKILL.md) |
| Dual-Format Production (`short_9x16`, `long_16x9`), New Episode Setup & Omni-Platform Publish (`./vp`) | [Workflow](sys/docs/workflow.md) | [vp-production](.agents/skills/vp-production/SKILL.md) |
| Engine development, 6-station conveyor (`./pipeline`), machine setup, maintenance/Git & troubleshooting | [Getting started](sys/docs/getting-started.md) · [Maintenance](sys/docs/maintenance.md) | [vp-engineering](.agents/skills/vp-engineering/SKILL.md) |

## Channel-to-Skill Routing & Composition Matrix (Mục Lục Điều Phối 7 Core Skills ↔ 38 Hồ Sơ Kênh)

All 38 physical channels share the **6-Core-Skill Production Spine** (`vp-channel-registry` -> `vp-content-studio` -> `vp-visual-fx` [`--fx-mode auto_niche` + `[PRO_FX]`/`[FULL_FX]`/`[BESPOKE_FX]`] -> `vp-flow-cdp` -> `vp-colab-bridge` -> `vp-production`) while isolating channel specs inside `sys/channels/<channel_id>/playbook/`:

| Channel Scope | Archetype / Format Focus | 3-Pillar Data Playbook (`overview`, `content`, `visual`, `pacing`) |
|---|---|---|
| **`su_ke_lai` (Sử Kể Lại — Wave 0 Active)** | `archetype_2_geopolitics_history` (`heroic_vietnam_epic` Short V4 + Option 1 35mm M1-Flex V9.2 Long, `1.30x`) | [su_ke_lai playbook](sys/channels/su_ke_lai/playbook/overview.md) |
| **`ban_do_quyen_luc` (Bản Đồ Quyền Lực — Wave 1)** | `archetype_2_geopolitics_history` (`ban_do_quyen_luc_4styles_photoreal_v3`, `1.15x`) | [ban_do_quyen_luc playbook](sys/channels/ban_do_quyen_luc/playbook/overview.md) |
| **`chanh_niem_ke` (Hiểu Tận Gốc — Wave 1)** | `archetype_2_geopolitics_history` (Web Mercator GIS + Bipolar V5.0 Hybrid Chronicle) | [chanh_niem_ke playbook](sys/channels/chanh_niem_ke/playbook/overview.md) |
| **`ho_so_ky_la` (Hồ Sơ Kỳ Lạ — Wave 1)** | `archetype_1_forensic_noir` (`ho_so_ky_la_3d_noir_forensic_v3`, `1.10x`) | [ho_so_ky_la playbook](sys/channels/ho_so_ky_la/playbook/overview.md) |
| **`co_the_ke` (Cơ Thể Kể — Wave 1)** | `archetype_3_science_xray` (`co_the_ke_3d_biomedical_v3`, `1.12x`) | [co_the_ke playbook](sys/channels/co_the_ke/playbook/overview.md) |
| **33 Remaining VN & EN Channels (Wave 2–5)** | Routed by [vp-channel-registry](.agents/skills/vp-channel-registry/SKILL.md) & `1.7.0` / Archetype 1–5 specs | `./vp playbook <channel_id>` -> `sys/channels/<channel_id>/playbook/overview.md` |

## System Layout & SSOT

- `sys/`: code, docs, schemas, configuration and channel playbooks (`sys/channels/<id>/playbook/`).
- `sys/format_profiles.py`: single source of truth for Dual-Format video profiles (`short_9x16` & `long_16x9`).
- `sys/runs/<job>/`: content, versions, requests and artifacts.
- `sys/assets/`: visual and studio voice references (`VietNarrator_<channel_id>` / `EnNarrator_<channel_id>`).
- `video/<job>/`: collected deliverables (MP4 / SRT / ASS).
- `.agents/skills/`: **7 consolidated Core Skills** (`vp-channel-registry`, `vp-content-studio`, `vp-visual-fx`, `vp-flow-cdp`, `vp-colab-bridge`, `vp-production`, `vp-engineering`).
- `PLAYBOOK.md`: operational lessons and root-cause fixes (mandatory reading).

[Active documentation index](sys/docs/INDEX.md).
