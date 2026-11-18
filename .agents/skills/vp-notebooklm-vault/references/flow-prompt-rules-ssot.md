# Official Google Flow Prompt Rules SSOT (Notebook 2 Vault)

Distilled from Google Flow official model behavior & Video Pilot empirical verification (`sys/flow_cdp/flow_rpc.py`, `sys/flow_video/`).

---

## 1. Model Lifecycle & Credit Economics (2026)

| Model Key | Nickname | Role in Video Pilot | Cost & Resolution | Status / Retirement |
|---|---|---|---|---|
| `BELUGA` | Nano Banana 2.1 | Primary 16:9 & 9:16 keyframe + thumbnail generator (`ogiZ0b` batch 2–4) | 0 credits (free pool image tiers) | Active SSOT |
| `macaron_cookie_i2v_fl_8s` (`_4s/_6s/_10s`) | Omni 1.2 Flash | **Frame-Link (`start_end_frames` / `nprQif`)** & `chanh_niem_ke` 3D mechanism clips | 12c (4s), 18c (6s), 24c (8s), 30c (10s) @ 720p | **Active Default `VIDEO_MODEL`** |
| `veo_3_1_i2v_s_lite` (`veo_3_1_interpolation_lite`) | Veo 3.1 Lite | **Seam Mode (`start_frame` / `eb1hJf`)** high-savings clip engine | **10 credits flat** for 4s, 6s, or 8s @ 720p | **Active Cost-Saver** |
| `veo_3_1_i2v_s_fast_fl`, `veo_3_1_i2v_s_fl`, `omni_flash_i2v_*` | Veo 3.1 Fast/Quality, Omni 1.1 | Legacy models (backward-compat aliases only) | 20–100c | **Retiring Dec 5, 2026** (do NOT select for new jobs) |
| Veo Video Extend | — | Legacy extension RPC | — | **Retired Nov 5, 2026** (use fresh clip + Boundary/Seam instead) |

---

## 2. Image Prompt Order (`BELUGA` / Nano Banana 2.1)
Follow this fixed sequence, **read dynamically from the target Channel Style Bible** (`vp-channel-<id>/SKILL.md`, `vn_flow_video_formulas.py`, `en_flow_video_formulas.py`, or `1.7.0 handdrawn_2d_explainer`):
1. **Reference Line** (only when `reference_media_ids` attached): `"Using the attached reference image(s), the same [person / people / object / location] as in the reference: [exact short unchanging visual lock]."`
2. **Hero Subject & Exact Count**: state `"exactly one ..."` / `"exactly two ..."` + frame third + physical material & state.
3. **Cast (only if present)**: age band, build, attire color, closed mouth, simple non-gesturing pose, max 3 individuals. Never alter clothes/hair on repeating cast.
4. **Setting & Time of Day**: concrete environment + atmospheric light matching neighboring scenes.
5. **Composition Rule for Planned Camera Move**: leave open ground for `push_in`, foreground parallax for `truck_lateral`, framing headroom for `crane_up`.
6. **Exit Seam Setup (if Seam Mode)**: natural occluder at travel edge (foliage, dark doorway, bright light source, drifting mist/dust, architectural pillar edge).
7. **Channel Style Block + Positive Framing**: translate negative bans into positive visual truths (`"plain unmarked metal surfaces"`, `"empty open studio ground"`, `"quiet closed mouth"`). Omit text/labels except explicit Flow-native 2–4 word thumbnail titles.

---

## 3. Video Prompt Rules: Seam Mode vs. Frame-Link Mode

| Dimension | Veo 3.1 Lite — Seam Mode (10c/clip) | Omni 1.2 Flash — Frame-Link Mode (12–30c/clip) |
|---|---|---|
| **When to Route** | **Always** when location, lighting, or cast changes; also when saving credits (`60%+` cheaper). | **Only** when consecutive frames share the **same cast** (or both character-free) AND **matching lighting/palette**. |
| **Prompt Length** | `70–100` words (explicit lens, single camera move, lighting, surface locks). | `40–70` words (clear start-to-end camera trajectory). |
| **Timecode Split (8s)** | `[0-6.5s]` main move + 1–2 subtle secondary motions -> `[6.5-8s]` exit seam (final scene: `[0-6s]` move -> `[6-8s]` complete still hold). | `[0-6.5s]` single continuous camera glide from Frame A to Frame B -> `[6.5-8s]` settle gently into Frame B composition. |
| **Anti-Artifact Guard** | Append surface-specific guard: `"Plain unmarked masts, hulls, buildings, and uniforms with zero flags, insignia, letters, or numbers; silent visual storytelling, no speech, no music, quiet ambient texture only."` | `"In one continuous unbroken shot, zero morphing, silent visual storytelling, no talking, no lip movement."` |
| **Post-Join Stitch** | `0.15–0.20s` FFmpeg `xfade=fade` dissolve (`seam_dissolve_sec=0.18`); `0.24s` `soft_fade` for Doodle / Archetype 5 Mindful channels. | Zero-seam `trim=start_frame=1` or clean cut when boundary matches. |

---

## 4. Viewing-Comfort Exceptions Across Archetypes
- **Archetype 1, 2, 3 & Photoreal Archetype 4:** Full `motion_library.py` camera moves + appropriate physical seams allowed (excluding `leaves_wipe` inside biomedical/space interiors).
- **`nao_luoi`, `en_lazy_brain` (2D Doodle) & Archetype 5 (`minh_triet_song`, `tam_tinh_dem`, `loi_sang_soi`, `en_second_arrow`, `en_bamboo_marble`):** Strictly block aggressive `white_flash` and fast `edge_pass` whips — lock to `soft_fade` (`0.24s`), `breathing_drift`, gentle `push_in`/`pull_back`, and `final_hold`.
