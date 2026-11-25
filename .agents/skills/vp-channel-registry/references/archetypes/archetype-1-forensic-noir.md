# Archetype 1 — Forensic Noir & Dark Mysteries (`archetype_1_forensic_noir`)

- **Member Channels (6 total — 3 VN / 3 EN):**
  - **VN:** `ho_so_ky_la`, `luat_ngam`, `nghe_song_sot`
  - **EN Twins:** `en_cold_case_ink`, `en_crowd_strings`, `en_career_leverage`
- **Visual & HUD Signature:** 3D Noir Forensic Diorama / archival dossier lighting (`#0A0B0E`, `#181B22`, crimson `(205, 52, 48, 245)`, antique brass `(212, 168, 72, 255)`), Kodak 35mm fine film grain, evidence stamps, split hypothesis compares, laser dossiers, bottom-right `delogo` + `1.045x` overscan. Zero AI text on raw Flow frames (`allowed_text=None`).
- **Short V4 & Audio Defaults:**
  - `theme_id`: `forensic_noir_suspense` (`primary_bgm=bgm_forensic_noir_drone.wav`, `secondary_bgm=bgm_geopolitics_pulse.wav`, `vacuum_stem=heartbeat_lub_dub.wav`)
  - Nominal speaking rate: `1.14x` (override per channel playbook e.g. `1.10x` for `ho_so_ky_la`)
- **Non-Forced Bespoke Rule:** Match telemetry to the real domain (submarine sonar/depth for maritime, toxicology/lab for medical forensics, offshore ledger for financial crimes — never force aviation CVR HUDs onto non-aviation stories).
- **Per-Channel Playbooks:** Load `sys/channels/<channel_id>/playbook/{overview,content,visual,pacing}.md` or run `./vp playbook <channel_id>`.
