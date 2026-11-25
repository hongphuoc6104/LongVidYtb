# Niche Archetypes & Bespoke Synthesis Rules (20 Vietnamese Channels)

Every channel in Video Pilot belongs to one of **5 Niche Archetypes** in `sys/fx_warehouse/archetypes.py`. Each archetype defines a default visual/audio signature, cross-warehouse pull permissions, forbidden jarring effects, and explicit rules for **when and how to synthesize bespoke per-video effects**.

---

## Archetype Overview

| Archetype ID | Label | Channels | Default Camera / VFX / BGM | Disallowed VFX |
| :--- | :--- | :--- | :--- | :--- |
| `archetype_1_forensic_noir` | Điều Tra Hồ Sơ Mật & Quy Luật Ngầm | `ho_so_ky_la`, `luat_ngam`, `nghe_song_sot` | `parallax_push_in` / `kodak_35mm_grain` / `bgm_forensic_noir_drone.wav` | None (all allowed when narrative fits) |
| `archetype_2_geopolitics_history` | Địa Chính Trị, Lịch Sử & Kinh Tế Vĩ Mô | `ban_do_quyen_luc`, `su_ke_lai`, `banh_rang` | `anamorphic_pan_lr` / `kodak_35mm_grain` / `bgm_geopolitics_pulse.wav` | None |
| `archetype_3_science_xray` | Khoa Học, Vũ Trụ & Giải Phẫu Cơ Chế | `vu_tru_ti_hon`, `co_the_ke`, `ua_sao_vay`, `dia_com` | `parallax_push_in` / `chromatic_glitch_pulse` / `bgm_scifi_biotech_pad.wav` | None |
| `archetype_4_doodle_explainer` | 2D Doodle Giáo Dục, Tài Chính, Luật & AI | `nao_luoi`, `tui_tien`, `luat_doi_thuong`, `ai_binh_dan`, `la_ban_hoc_thuat`, `thuong_cho_kheo` | `breathing_drift` / `clean_daylight_none` / `bgm_curious_acoustic_loop.wav` | `crimson_strobe_alert`, `camera_shake_impulse`, `hypoxic_vignette` |
| `archetype_5_mindful_healing` | Chánh Niệm, Minh Triết & Tâm Tình Đêm | `chanh_niem_ke`, `minh_triet_song`, `loi_sang_soi`, `tam_tinh_dem` | `breathing_drift` / `warm_dust_motes` / `bgm_zen_night_healing.wav` | `crimson_strobe_alert`, `camera_shake_impulse`, `chromatic_glitch_pulse`, `hypoxic_vignette` |

---

## Group 1: `archetype_1_forensic_noir` (Forensic Noir & Hidden Laws)

- **Signature**: Crimson `(205, 52, 48, 255)` + Brass `(212, 168, 72, 255)`, 35mm film grain, chiaroscuro tension, sharp dossier/telemetry overlays.
- **Allowed Cross-Warehouse Pulls**: Group 2 (`radar_bezier_trajectory`, `triptych_3col_evidence`, `verdict_lower_third`, `braaam_horn_low.wav`), Group 3 (`xray_mode_switch_particles`, `dual_oscilloscope_compare`).
- **Forbidden Jarring Effects**: Never use playful `doodle_spring_pop_badge`, bright yellow `highlighter_stroke_bar`, or `bgm_curious_acoustic_loop.wav`. Never force aviation HUDs (`altitude_stat_counter`, `countdown_cvr_waveform` with flight wording) onto non-aviation mysteries.

### Channels & Bespoke Per-Video Triggers
1. **`ho_so_ky_la`** (Strange Case Files / Aviation, Maritime, Cold Cases, Poisoning):
   - *Pulls*: `lemmino_dossier_card`, `kinetic_stamp_slam`, `dual_oscilloscope_compare`, `radar_bezier_trajectory`.
   - *Bespoke Protocol*:
     - **Maritime / Submarine Mystery**: Synthesize a bespoke **Bathymetric Depth & Hull-Pressure Gauge** (`bespoke_hud_spec`) + deep hydrophone sonar ping (`synthesize_bespoke_topic_sfx`) instead of aviation altitude counters.
     - **Toxicology / Poisoning Case**: Author a bespoke **Toxin Concentration & Half-Life Curve** HUD instead of oscilloscope audio waves.
2. **`luat_ngam`** (Hidden Power Laws, Syndicate Mechanics, Shadow Finance):
   - *Pulls*: `triptych_3col_evidence`, `laser_split_screen`, `verdict_lower_third`.
   - *Bespoke Protocol*: For corporate shell-company networks or cartel logistics, synthesize a bespoke **Entity-Flow / Shell Ownership Node Card** + subtle vault/ledger lock SFX.
3. **`nghe_song_sot`** (Survival & Extreme Crisis Reconstruction):
   - *Pulls*: `countdown_cvr_waveform`, `xray_mode_switch_particles`, `heartbeat_lub_dub.wav`, `air_pressure_hiss.wav`.
   - *Bespoke Protocol*: Match the exact environmental hazard—e.g., **Avalanche / Hypothermia Core-Temp Meter** or **Cave Oxygen / CO2 PPM Meter** with bespoke muffled wind/water SFX.

---

## Group 2: `archetype_2_geopolitics_history` (Geopolitics, History & Macro Economy)

- **Signature**: Brass `(212, 168, 72, 255)` + Cyan `(32, 212, 248, 255)`, wide anamorphic sweeps, editorial triptychs, war drums & macro horns.
- **Allowed Cross-Warehouse Pulls**: Group 1 (`lemmino_dossier_card`, `kinetic_stamp_slam`, `dossier_slide_whoosh.wav`), Group 3 (`xray_mode_switch_particles` for industrial/tech chokepoints).
- **Forbidden Jarring Effects**: Never force modern digital radar or neon cyan sci-fi glitches onto ancient/medieval historical battles; avoid `doodle_spring_pop_badge`.

### Channels & Bespoke Per-Video Triggers
4. **`ban_do_quyen_luc`** (Geopolitics, Chokepoints, Semiconductor & Trade Wars):
   - *Pulls*: `radar_bezier_trajectory`, `laser_split_screen`, `triptych_3col_evidence`, `braaam_horn_low.wav`.
   - *Bespoke Protocol*: For **Semiconductor Supply Chain** or **Rare-Earth Chokepoints**, build a bespoke **Multi-Node Supply Dependency Matrix / Fab Yield Meter** (`bespoke_hud_spec`) + clean industrial fab hum SFX.
5. **`su_ke_lai`** (Historical Storytelling, Dynasties, Turning-Point Battles):
   - *Pulls*: `lemmino_dossier_card`, `verdict_lower_third`, `taiko_war_drum.wav`, `anamorphic_pan_lr`.
   - *Bespoke Protocol*: For **Ancient Dynasty Battle Maps** (e.g., Bạch Đằng, Chi Lăng, Waterloo), create a bespoke **Parchment Troop-Flank & Tide/Terrain Timeline** HUD (warm brass/parchment palette, zero modern neon radar) + bespoke wooden bow/arrow volley or bronze drum SFX.
6. **`banh_rang`** (Macro Economy, Industrial Engines, Monetary Policy):
   - *Pulls*: `altitude_stat_counter`, `laser_split_screen`, `triptych_3col_evidence`, `sub_bass_boom.wav`.
   - *Bespoke Protocol*: For **Central Bank Rate Cycles** or **Debt-Trap Spirals**, synthesize a bespoke **Inflation vs. Yield-Curve Gauge** HUD + mechanical gear/press SFX.

---

## Group 3: `archetype_3_science_xray` (Science, Cosmos & Mechanism X-Ray)

- **Signature**: Cyan `(32, 212, 248, 255)` + Crimson `(205, 52, 48, 255)`, crisp telemetry, X-ray cutaways, biotech/scifi pads.
- **Allowed Cross-Warehouse Pulls**: Group 1 (`dual_oscilloscope_compare`, `altitude_stat_counter`, `rotary_switch_click.wav`), Group 2 (`laser_split_screen`, `triptych_3col_evidence`).
- **Forbidden Jarring Effects**: Never use warm vintage parchment/calligraphy (`calligraphy_quote_dissolve`) on hard physics/biotech beats; avoid `taiko_war_drum.wav` unless illustrating cosmic collisions.

### Channels & Bespoke Per-Video Triggers
7. **`vu_tru_ti_hon`** (Quantum Physics, Micro-Cosmos, Astrophysics):
   - *Pulls*: `xray_mode_switch_particles`, `parallax_push_in`, `chromatic_glitch_pulse`.
   - *Bespoke Protocol*: For **Quantum Tunneling / Particle Colliders**, synthesize a bespoke **Wave-Function Probability / Electron-Volt Scale** HUD + crystalline resonant chime SFX.
8. **`co_the_ke`** (Human Anatomy, Neuroscience, Immune System):
   - *Pulls*: `xray_mode_switch_particles`, `heartbeat_lub_dub.wav`, `dual_oscilloscope_compare`.
   - *Bespoke Protocol*: For **Neurotransmitter Synapses** or **Hormone Cascades**, author a bespoke **Synaptic Firing / Receptor-Binding Ratio Card** + organic fluid/electrical snap SFX.
9. **`ua_sao_vay`** (Everyday Science Mysteries & Counter-Intuitive Physics):
   - *Pulls*: `laser_split_screen`, `altitude_stat_counter`, `ding_insight.wav`.
   - *Bespoke Protocol*: For **Optical Illusions / Acoustic Paradoxes**, create a bespoke **Stimulus-vs-Perception Delta Card** + custom frequency-sweep test tone SFX.
10. **`dia_com`** (Earth Sciences, Deep Ocean, Geology & Climate Systems):
    - *Pulls*: `radar_bezier_trajectory`, `orbital_tilt_down`, `cold_wind_gust.wav`.
    - *Bespoke Protocol*: For **Tectonic Subduction / Deep-Sea Vent Ecosystems**, synthesize a bespoke **Crustal Depth & Geothermal Pressure Profile** HUD + low seismic rumble SFX.

---

## Group 4: `archetype_4_doodle_explainer` (2D Doodle Education, Finance, Law & AI)

- **Signature**: Cerulean `(59, 130, 196, 255)` + Amber `(245, 158, 11, 255)`, `breathing_drift` / `static_clean`, `clean_daylight_none`, `bgm_curious_acoustic_loop.wav`.
- **Allowed Cross-Warehouse Pulls**: Group 2 (`laser_split_screen`, `triptych_3col_evidence`, `verdict_lower_third` restyled in light/clean palette), Group 3 (`altitude_stat_counter` for financial/data milestones).
- **Forbidden Jarring Effects**: **Strictly disallowed**: `crimson_strobe_alert`, `camera_shake_impulse`, `hypoxic_vignette`. Avoid dark-noir film grain (`kodak_35mm_grain`) on `#FFFFFF` / `#F8F0DC` flat canvases, and avoid heavy horror booms (`braaam_horn_low.wav`, `taiko_war_drum.wav`).

### Channels & Bespoke Per-Video Triggers
11. **`nao_luoi`** (Cognitive Biases, Habits, Productivity Psychology):
    - *Pulls*: `doodle_spring_pop_badge`, `highlighter_stroke_bar`, `pop_clean.wav`, `pen_highlight.wav`.
    - *Bespoke Protocol*: For **Dopamine Loops / Attention Residue**, build a bespoke **Cognitive Load / Focus-Decay Meter** in flat `#F8F0DC` doodle card style.
12. **`tui_tien`** (Personal Finance, Compounding, Investing, Taxes):
    - *Pulls*: `highlighter_stroke_bar`, `laser_split_screen`, `altitude_stat_counter`.
    - *Bespoke Protocol*: For **Tax Bracket Calculators** or **Compound-Interest vs. Inflation Charts**, synthesize a bespoke **Tiered Tax Bracket / Cashflow Split Card** (`bespoke_hud_spec`) + crisp coin/register chime SFX.
13. **`luat_doi_thuong`** (Everyday Civil Law, Labor Rights, Consumer Contracts):
    - *Pulls*: `triptych_3col_evidence`, `verdict_lower_third`, `page_flip.wav`.
    - *Bespoke Protocol*: For **Contract Clause Traps / Legal Deadline Windows**, author a bespoke **Clause Checklist / Statutory Deadline Bar** HUD.
14. **`ai_binh_dan`** (Practical AI Literacy, Prompting, Automation Workflows):
    - *Pulls*: `doodle_spring_pop_badge`, `laser_split_screen`, `typewriter_burst.wav`.
    - *Bespoke Protocol*: For **Token Context Windows / RAG Pipelines**, create a bespoke **Token-Budget / Input-Output Pipeline Card** in clean light-mode doodle aesthetic.
15. **`la_ban_hoc_thuat`** (Academic Research Methods, Critical Thinking, Study Systems):
    - *Pulls*: `highlighter_stroke_bar`, `triptych_3col_evidence`, `ding_insight.wav`.
    - *Bespoke Protocol*: For **P-Value / Sample-Size Fallacies**, build a bespoke **Confidence-Interval / Study Bias Comparison Card**.
16. **`thuong_cho_kheo`** (Negotiation, Behavioral Economics, Smart Commerce):
    - *Pulls*: `laser_split_screen`, `doodle_spring_pop_badge`, `whoosh_soft.wav`.
    - *Bespoke Protocol*: For **Anchoring Price / Asymmetric Information**, author a bespoke **Offer-vs-BATNA Anchor Slider** HUD.

---

## Group 5: `archetype_5_mindful_healing` (Mindfulness, Wisdom & Night Reflections)

- **Signature**: Warm Gold `(232, 200, 142, 255)` + Soft Mist `(182, 194, 210, 255)`, `breathing_drift`, `warm_dust_motes`, `bgm_zen_night_healing.wav`, `singing_bowl_zen.wav`, `night_rain_soft.wav`.
- **Allowed Cross-Warehouse Pulls**: `lemmino_dossier_card` (slowed down for literary quotes), `static_clean`, `whoosh_soft.wav`, `page_flip.wav`.
- **Forbidden Jarring Effects**: **Strictly disallowed**: `crimson_strobe_alert`, `camera_shake_impulse`, `chromatic_glitch_pulse`, `hypoxic_vignette`. Never use `kinetic_stamp_slam`, `stamp_slam_hit.wav`, `caution_chime_double.wav`, `stopwatch_urgent_tick.wav`, or harsh telemetry/oscilloscope HUDs.

### Channels & Bespoke Per-Video Triggers
17. **`chanh_niem_ke`** (Mindfulness Practice, Breathwork, Present-Moment Anchoring):
    - *Pulls*: `calligraphy_quote_dissolve`, `breathing_drift`, `singing_bowl_zen.wav`.
    - *Bespoke Protocol*: For **4-7-8 / Box Breathing**, synthesize a bespoke **Slow-Expanding Breath Cadence Ring** (`bespoke_hud_spec`) + warm low-passed chime SFX.
18. **`minh_triet_song`** (Stoicism, Eastern Philosophy, Life Principles):
    - *Pulls*: `calligraphy_quote_dissolve`, `warm_dust_motes`, `page_flip.wav`.
    - *Bespoke Protocol*: For **Classical Parables / Stoic Dichotomy of Control**, author a bespoke **Warm Parchment Dual-Circle ("Trong Tầm Kiểm Soát / Ngoài Tầm Kiểm Soát") Card**.
19. **`loi_sang_soi`** (Clarity, Emotional Intelligence, Inner Healing):
    - *Pulls*: `calligraphy_quote_dissolve`, `breathing_drift`, `whoosh_soft.wav`.
    - *Bespoke Protocol*: For **Cognitive Reframing / Grief & Letting-Go Arcs**, create a bespoke **Soft Dissolving Journal-Prompt Card** + gentle wind-chime SFX.
20. **`tam_tinh_dem`** (Late-Night Monologues, Solitude, Quiet Empathy):
    - *Pulls*: `calligraphy_quote_dissolve`, `night_rain_soft.wav`, `warm_dust_motes`.
    - *Bespoke Protocol*: For **Rainy-Night / 2AM Radio Reflections**, synthesize a bespoke **Minimalist Warm-Lamp Timestamp & Quote Card** + custom soft vinyl crackle or distant rain-on-window SFX.
