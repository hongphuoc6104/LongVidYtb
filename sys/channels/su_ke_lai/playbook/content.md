# V4 (`V9.1`) Gold Standard & V9.2 `M1-Flex` Turnkey Engine — 9–15 Minute Analytical Military History & Minimalist Mẫu M1 IMAX Visual Lock (`su_ke_lai_long_v9_1_m1_v4_gold_standard` & `su_ke_lai_long_v9_2_m1_flex_engine`)

Permanently locked, user-approved production architecture, NotebookLM 3-Vault deep-extraction protocol, **Mẫu M1 V4 (`V9.1`) Minimalist IMAX `2.39:1` Gold Standard**, and **V9.2 Parameterized `M1-Flex` Turnkey Engine (`sys/tools/produce_su_ke_lai_long_m1.py` — "Tựa Tựa Khuôn, Không Phải Y Đúc")** specification for **Sử Kể Lại** (`su_ke_lai`, `@SuKeLaiVN`) flagship **`9–15` minute (`540s–900s`, sweet spot `~10–12m`, `6–12` Chapters [default `10`], `60–120` beats [default `100`])** Long `16:9` military-history documentaries.

Supersedes the older V9.0 draft (`su_ke_lai_long_v9_m1_imax_analytical_9_15m`) — permanently retiring 2-tier `46px` titles, horizontal whip-slide transitions (`directional_flow_chain_transition`), Pillow-drawn 2D/3D cartoon maps (`map_dive` / `_render_3d_map_dive`), black-bar header/footer clutter, every-beat titles, and multi-line chapter card subtitles. Synthesized from cross-market breakout forensics (`BATTLECRY` `139k/d`, `CLD Studio` `58k/d`, `CD Media - Quân Sự` `42k/d`, `Dòng Máu Việt` `746K` avg / `3.59M` peak, `Kings and Generals` `44.1k/d`, `Epic History TV` `258.1k/d`, `Yarnhub` `915.5k/d`, `The Operations Room`), Layer-0 **NotebookLM 3-Vault** grounding ([vp-content-studio](../../../../.agents/skills/vp-content-studio/SKILL.md)), the verified **V4 (`V9.1`)** reference engine (`sys/runs/vn_su_ke_lai_1789_ngoc_hoi_dong_da_full_m1/render_m1_from_scratch.py`), and the permanent **V9.2 Parameterized `M1-Flex` CLI Tool (`sys/tools/produce_su_ke_lai_long_m1.py`)**.

> **Scope & Compatibility Lock**: V4 (`V9.1`, `su_ke_lai_long_v9_1_m1_v4_gold_standard`) paired with V9.2 `M1-Flex` (`su_ke_lai_long_v9_2_m1_flex_engine`) is the active Long `16:9` flagship lock for `su_ke_lai`, superseding V9.0 draft and building on V8.0 zero-smoke discipline, V7.0 Zero-Box typography, V6.0 feudal materiality, and Clear-Air Option 1 (`su_ke_lai_35mm_live_action_v3`). Shared workflow skills (`vp-content-studio`, `vp-content-studio`, `vp-content-studio`, `vp-flow-cdp`, `vp-colab-bridge`, `vp-production`, `vp-production`) remain **100% unmodified**.

---

## 0. Six Non-Negotiable V4 (`V9.1`) Gold Standard Invariants

1. **100% From-Scratch Single-Campaign Cohesive 9–15m Narrative**: Every Long episode (**`10` Chapters `CHƯƠNG I`..`CHƯƠNG X`, `100` beats, `~10–12m`** inside `540s–900s`) is written, voiced, and shot 100% from scratch as one cohesive historical campaign. **Strict permanent ban on stitching unrelated older Short episodes** into a Long video.
2. **100% Native `16:9` Moving Flow `.mp4` Video Chains (`50` 2-Beat Chains Covering All `100` Beats)**: Every narration beat runs on native `16:9` moving Google Flow `.mp4` footage (`1280x720` native). **Zero static PNG slides**, **zero `9:16` portrait clips cropped into widescreen**, and **100% permanent ban on Pillow-drawn 2D/3D vector cartoon maps (`map_dive`)**.
3. **Zero-Dizziness Continuous Camera Chains**: **100% permanent ban on horizontal whip-slides (`directional_flow_chain_transition`)** and artificial pan/zoom jitter on moving video (**`zoom=1.0, dx=0.0, dy=0.0, cy=0.44`**). Within each 2-beat chain (`beat_{2k} -> beat_{2k+1}`), play the `8.0s` Flow clip continuously (**`0.00 -> 3.30 -> 6.60s`, `0.0s` blend, `MAE=0.0`**). Between distinct clips (`chain_k -> chain_{k+1}`), use **ONLY a calm stationary `0.20s` optical cross-dissolve (`0px` shift)**.
4. **Minimalist Chapter Title Cards (`CHƯƠNG I`..`CHƯƠNG X`) & Pure Black IMAX `2.39:1` Letterbox**: Render ONLY a small tracked `CHƯƠNG I`..`CHƯƠNG X` kicker + concise `3–4` word core title (**`30px@360p / 90px@1080p / 120px@1440p`**), **zero bottom subtitle sentence (`card_subtitle=""`)**, **zero gold divider line**, over a bright vivid moving cinema background (**`0.56..0.72` vignette**). Keep **100% pure cinema-black IMAX `2.39:1` letterbox bars** (zero top-left, top-right, or bottom-left bar text; **ONLY bottom-right `@SuKeLaiVN` logo**).
5. **Sparse Selective Single-Line Verbatim Emphasis Keywords**: Display keywords ONLY on **`~20–25%` of beats (`2–3` per chapter, spaced `18–25s` apart, NEVER on `beat_*0` right after a chapter card)** so **`75–80%` of beats remain 100% text-free pure cinema**. **Single line only (`top_word=""`)**, compact **`22px@360p / 66px@1080p / 88px@1440p`** ivory-gold **`#FFF5D6`**, subtle **`1.06x -> 1.00x` (`0.16s`)** pop-in synced verbatim via `_find_word_offset`, paired with **`-14dB` tactile 1789 SFX ONLY on keyword beats**.
6. **High-Resolution Master & Audio Lock**: Native **`1920x1080` Full HD** (`crf=16`, `1280x720` source → Golden-Dawn grade → **Lanczos-4** upscale + optical unsharp + native vector typography) OR **`2560x1440` 2K @ `30fps`**, mastered to **`-11.0 LUFS (±0.7) / <= -1.0 dBTP`** @ `48000Hz` stereo.

---

## 1. 100% From-Scratch Single-Campaign 10-Chapter Analytical Spine (`100` Beats, `~10–12m`)

### 1.1 Why Surface Summaries & Stitched Compilations Fail
A 3-minute textbook summary collapses on Average View Duration (AVD), and **stitching unrelated older Short episodes** destroys tonal continuity, leaves orphan hooks/CTAs, and violates big-screen TV/Desktop viewer trust (`73.8%` of `@SuKeLaiVN` Long watch time is Male 35–44 on TV/Desktop). Every V4 (`V9.1`) Long episode is built **100% from scratch** around a single unified campaign expanded across **4 causal pillars**:

1. **Asymmetric Constraints & Logistics Math**: Distance, forced-march mechanics (*cáng 3 người thay phiên*, *ăn Tết trước*), river tides, winter/monsoon weather, rations, reload rates, and terrain bottlenecks that made victory look mathematically impossible on paper.
2. **Weapon / Unit Engineering & Failure Modes (*"Sai 1 bước chết ở đâu"*)**: Physical mechanics of weapons, armor, formations, and counter-measures — plus the exact vulnerability that would have destroyed the side if one engineering detail failed.
3. **Cognitive & Intelligence Warfare**: Why the opposing commander made a fatal decision (not because they were "stupid", but because deliberate operational secrecy and deception exploited their doctrine, arrogance, or blind spots).
4. **Operational Lineage & Frontline Leadership**: How combined-arms doctrine, terrain mastery, and frontline command turned asymmetric odds into decisive victory — grounded strictly in primary chronicles.

### 1.2 Canonical 10-Chapter, 100-Beat Cohesive Campaign Spine (`~10–12m` Sweet Spot inside `9–15m`)

Calibrated for `VietNarrator_su_ke_lai` (`speaking_rate=1.30`, `3.80–4.15 syl/s`), **`10` Chapters × `10` beats = `100` narration beats** (`50` continuous 2-beat native `16:9` Flow `.mp4` chains), plus `10 × 3.60s` minimalist chapter title cards (`~600s–750s` = **`10m00s–12m30s`**; verified flagship `621.70s` = `10m21.7s`; extendable up to `15:00` via beat count while keeping `10` `FFMETADATA1` chapters):

| Chapter (`CHƯƠNG I..X`) | Beats & Chains | Analytical & Narrative Mission | V4 (`V9.1`) Visual & Keyword Choreography |
| :--- | :--- | :--- | :--- |
| **CHƯƠNG I — Paradox Cold-Open & Impossible Odds** | `beat_000..009` (`5` chains) | Open straight into the numerical/tactical paradox (`beat_000 <= 24` syl, **zero `[pause:...]`**, zero greetings). Establish the invading force, capital occupation, and why frontal war looked hopeless. | Minimalist `CHƯƠNG I` card (`3–4` word title, zero subtitle/divider) → **`beat_000` 100% text-free** pure `16:9` cinema → `2–3` sparse single-line keywords (`#FFF5D6`, spaced `18–25s`). |
| **CHƯƠNG II — Strategic Mobilization & Forced March** | `beat_010..019` (`5` chains) | Dissect logistics math: proclamation/coronation, mobilization speed, *cáng 3 người thay phiên*, *ăn Tết trước*, and crossing mountains/rivers ahead of enemy timetables. | Continuous 2-beat `16:9` Flow chains (`0.00 -> 3.30 -> 6.60s`, `MAE=0.0`); aerial/wide moving 35mm terrain sweeps (**zero Pillow `map_dive`**). |
| **CHƯƠNG III — Operational Architecture & Multi-Column Plan** | `beat_020..029` (`5` chains) | Break down the multi-pronged strategic deployment (main shock column, flanking cavalry/elephants, riverine blocking fleets cutting off retreat). | Calm `0.20s` stationary dissolves (`0px` shift) between chains; `2–3` sparse verbatim keywords (`18–25s` apart); Retention Reset every `60–90s`. |
| **CHƯƠNG IV — Intelligence Blackout & First Night Strike** | `beat_030..039` (`5` chains) | Explain how forward scouts were neutralized and the first outer fortress fell with surgical speed and psychological intimidation. | Vivid night/torchlit Clear-Air 35mm cinema (no dark murk; `gamma <= 0.85`); **`beat_030` text-free**; `2–3` sparse single-line keywords with `-14dB` SFX. |
| **CHƯƠNG V — The Chokepoint / Fortress Dilemma** | `beat_040..049` (`5` chains) | Quantify the enemy's primary killing zone: earthworks, stakes, layered artillery, and why standard infantry charges meant guaranteed slaughter. | Pure `16:9` moving camera reveals of ramparts, cannon batteries, and terrain chokepoints (zero cartoon vector maps, zero whip-slides). |
| **CHƯƠNG VI — Counter-Measure Engineering Anatomy #1** | `beat_050..059` (`5` chains) | Deep-dive physics of the defensive/breaching counter-measure (e.g., *Mộc bài rơm ướt* 3-plank wet-straw mobile shields absorbing cannonballs & fire). | Native `16:9` close-up-to-wide moving chains showing tactile wood, wet straw, and 20-man shock squads; `2–3` sparse keywords on key engineering nouns. |
| **CHƯƠNG VII — Flagship Shock Unit & Weapon Anatomy #2** | `beat_060..069` (`5` chains) | Engineering & psychological breakdown of the decisive combined-arms strike units (e.g., **100 Armored War Elephants** with howdah cannons + **900°C *Hỏa Hổ*** sticky pine-resin fire tubes). | Continuous `8.0s` moving elephant/fire chains (`zoom=1.0, dx=0.0, dy=0.0`); verbatim single-line keywords (`ĐẠI BÁC TRÊN LƯNG`, `HỎA HỔ`) + `-14dB` `elephant_trumpet` / `fire_roar`. |
| **CHƯƠNG VIII — Synchronized Multi-Front Climax** | `beat_070..079` (`5` chains) | Pre-impact compression → **`[pause:450–650ms]`** → synchronized dawn assault, environmental/wind multiplier, and secondary-flank collapse (*Đầm Mực / Đống Đa*). | Uninterrupted moving battle cinema across all `10` beats (`75–80%` text-free so visual scale breathes); `0.20s` stationary dissolves between distinct clips. |
| **CHƯƠNG IX — Collapse, Capital Entry & Chronicle Proof** | `beat_080..089` (`5` chains) | Enemy rout, frontline commander entering the liberated capital (gunpowder-blackened royal war-robe), and primary-chronicle verification (`Hoàng Lê Nhất Thống Chí`, `Đại Nam Thực Lục`, `Thanh Thực Lục`). | Golden-dawn triumphant `16:9` cinema; sparse single-line archival keywords; zero rectangular quote boxes or paper cards. |
| **CHƯƠNG X — Post-War Statecraft, Legacy & 2-Choice Debate** | `beat_090..099` (`5` chains) | Strategic aftermath/diplomacy (*Nước cờ giả vương* / geopolitical legacy) closing over serene dawn cinema with **ONE polarizing 2-choice historical debate question** mirrored verbatim in `@SuKeLaiVN` pinned comment. | Breathing moving cinema; `<= 24` syl close CTA (zero *"like/share/subscribe/đăng ký/nhấn chuông"*); pure black IMAX bars with ONLY bottom-right `@SuKeLaiVN` logo. |

### 1.3 Mandatory Retention Reset Every `60–90s`
Every `60–90` seconds — and strictly at every chapter handoff — inject a **3-Step Causal Retention Reset** so viewers never feel a section has "ended":

```text
[Step 1: Causal "Why Didn't They Just..." Objection]  (1 punchy spoken question, 10-16 syl)
    ↓
[Step 2: Physical / Tactical Constraint]              (1-2 crisp sentences explaining the real-world law of physics/war)
    ↓
[Step 3: Counter-Intuitive Engineering Solution]      (Reveals the next chapter's weapon, deception, or doctrinal leap)
```

**Production Examples (Zero Clichés — Never *"Ít ai biết rằng..."* or *"Bí mật nằm ở..."*):**
1. *Objection*: *"Nhưng nếu quân Thanh dựng lũy đất cắm chông dày đặc và chĩa hàng trăm khẩu đại bác ra ngoài, đàn voi chiến chẳng phải sẽ trở thành bia thịt di động sao?"* → *Constraint*: Cannonball shockwaves spook untrained war elephants into trampling their own infantry. → *Solution*: Wet-straw mobile wooden shields (*Mộc bài rơm ướt*) advancing ahead in 20-man shock teams + acoustic gunpowder conditioning before the march.
2. *Objection*: *"Tại sao 5 vạn quân Xiêm không chia hạm đội đánh bọc hậu đường bộ thay vì chui vào khúc sông Rạch Gầm?"* → *Constraint*: Deep-draft Siamese war-junks depended on the Tiền River flood tide for speed and supply weight. → *Solution*: Nguyễn Huệ staged a calibrated feigned retreat timed to the exact 03:00 AM ebb tide, turning their heavy hulls into helpless drift targets.
3. *Objection*: *"Một ống tre phun lửa dài chưa tới hai mét làm sao uy hiếp được kỵ binh giáp sắt Bát Kỳ?"* → *Constraint*: Water cannot extinguish burning pine-resin mixed with sulfur and oil; flames cling directly to lamellar seams and horse hides. → *Solution*: Firing *Hỏa Hổ* in synchronized low-angle volleys immediately behind the wet-straw shield wall at `< 10m` range.

---

## 2. NotebookLM 3-Vault Deep Extraction Protocol for 9–15m Long Videos

Before writing a single sentence of a 9–15m script, ground 100% of historical facts, dates, weapon engineering details, and spoken pronunciations in **NotebookLM 3-Vault** (`sys/tools/notebooklm_vault.py`, zero LLM-memory invention).

### 2.1 Ready-to-Run CLI Workflow (`su_ke_lai` 9–15m Long)

```bash
# 1. Inspect available NotebookLM bridges (read-only; never auto-launches Chrome):
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py bridge-status

# 2. Generate ready-to-paste Master Prompts for Vault 1 (Pattern), Vault 2 (Flow Rules) & Vault 3 (Fact Vault):
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py render-prompts \
  --channel su_ke_lai \
  --topic "<TÊN CHIẾN DỊCH / BINH CHỦNG 9-15 PHÚT>" \
  --format long_16x9 \
  --audience "Khán giả nam Việt Nam 25-45 tuổi xem TV/Desktop, yêu thích phân tích lịch sử quân sự & chiến thuật chuyên sâu"

# 3. Parse exported NotebookLM Markdown notes into a validated Fact Vault JSON:
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py import-notes \
  --channel su_ke_lai \
  --topic "<TÊN CHIẾN DỊCH / BINH CHỦNG 9-15 PHÚT>" \
  --format long_16x9 \
  --input sys/runs/<job_id>/notebooklm_notes.md \
  --output sys/runs/<job_id>/fact_vault.json

# 4. Validate 9-15m Deep Fact Vault (MANDATORY >= 24 verified primary-chronicle & physics/tactics facts):
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py validate \
  --vault sys/runs/<job_id>/fact_vault.json \
  --min-facts 24

# 5. Export brief.sources[] JSON & YouTube "Nguồn tham khảo" block:
PYTHONPATH=sys sys/.venv/bin/python sys/tools/notebooklm_vault.py export-sources \
  --vault sys/runs/<job_id>/fact_vault.json

# 6. Run strict anti-hallucination & report-only quarantine gate on final content.json:
PYTHONPATH=sys sys/.venv/bin/python sys/tools/fact_grounding_linter.py \
  --content sys/runs/<job_id>/content.json \
  --vault sys/runs/<job_id>/fact_vault.json \
  --channel su_ke_lai \
  --strict
```

### 2.2 Vault 1 (Pattern Vault) & Vault 3 (9–15m Deep Fact Vault) Master Prompts

#### Vault 1 — 9–15m Analytical Military Documentary Pattern Prompt
```text
You are a military-history documentary retention analyst for Vietnamese long-form YouTube (Sử Kể Lại / su_ke_lai, 9-15 minute cohesive single-campaign analytical format).
Use ONLY the benchmark videos/transcripts loaded in this notebook. Analyze structure, causal escalation, and pacing ONLY — NEVER copy wording, scripts, or metaphors.
Output <= 550 words covering:
1. Cold-Open Paradox (0:00-0:45): exact structural mechanics (first sentence <= 24 Vietnamese syllables, zero pause, zero channel greeting) that hook big-screen TV/Desktop viewers.
2. 10-Chapter Cohesive Deepening Spine (100 beats, ~10-12m): how top videos expand a single campaign beyond Wikipedia timelines into asymmetric logistics, weapon engineering anatomy, counter-measure physics, operational deception, and frontline leadership.
3. 60-90s Retention Reset Formulas: top 5 "Why didn't they just... -> Physical constraint -> Counter-intuitive engineering solution" pivots.
4. Spatial Clarity & Climax Pacing: how unobstructed 35mm cinema sustains immersion without cartoon map interruptions or clutter, and how silence/foley compression builds climax.
5. Closing 2-Choice Debate Trigger: structural geometry driving >0.15% comment/view debate without saying like/share/subscribe.
Mark anything unsupported by sources as "not shown in sources".
```

#### Vault 3 — Episode Deep Research & Source-Grounded Extraction Prompt *(Clear Sources & Chat Before EVERY New Topic!)*
**Primary Chronicle & Technical Sources to Load:** `Đại Việt Sử Ký Toàn Thư`, `Hoàng Lê Nhất Thống Chí`, `Đại Nam Thực Lục`, `Khâm Định Việt Sử Thông Giám Cương Mục`, `Thanh Thực Lục` (Qing Veritable Records), `Nguyên Sử` / `Minh Thực Lục`, `Gia Định Thành Thông Chí`, peer-reviewed Vietnamese military-history monographs (Viện Lịch sử Quân sự Việt Nam), and historical ballistics / terrain / tide hydrology studies.

```text
TOPIC: [TÊN CHIẾN DỊCH / BINH CHỦNG / NHÂN VẬT]
CHANNEL: su_ke_lai (Sử Kể Lại) | FORMAT: long_16x9 (10 chapters, 100 beats, ~10-12 minutes from scratch)
AUDIENCE: Male 25-45 Vietnamese TV/Desktop history & military-tactics viewers.
Use ONLY the primary chronicles and authoritative studies imported into this notebook.
STRICT QUARANTINE RULE: If a Deep Research summary report mentions a claim, number, or legend ("dã sử / tương truyền") NOT directly verified by an imported primary source, DO NOT place it in Section 1 — quarantine it strictly inside Section 8 under `report_only_claims`. Never fill gaps from LLM memory.

Produce structured Vietnamese Research Notes with these EXACT 9 sections:
1. Verified Primary-Chronicle & Physics/Tactics Facts (>= 24 items, target 24-32):
   - Each item MUST state: exact date/hour/location, verified number & unit, tactical/engineering mechanism, and [Primary Source Name, Volume/Chapter] in brackets.
   - Cover all 4 pillars: (a) Force & Logistics Math, (b) Intelligence & Deception, (c) Weapon/Unit Engineering & Counter-Measures, (d) Battle Execution, Diplomacy & Aftermath.
2. Central Counter-Intuitive Paradox (`surprising_hook_fact`): why conventional military logic predicted defeat and the single verifiable factor that flipped the outcome.
3. 10-Chapter Causal Spine & 60-90s Retention Resets: map 8-10 "Why didn't they just..." objections -> real physical/tactical constraints -> verified counter-intuitive solutions.
4. Vietnam Scale & Everyday Micro-Bridges (`vietnam_micro_bridges`, 3-4 items): convert historical distances, march speeds, armor weights, or river widths into concrete modern Vietnamese equivalents.
5. Native 16:9 35mm Live-Action Visual & Period-Materiality Notes: verified 18th/13th-century Đại Việt armor, uniforms, banners (strictly feudal era — ZERO modern flags), terrain, weather, and time of day (for text-free native 16:9 Flow video prompts).
6. Common Textbook Misconceptions & Primary-Chronicle Corrections (3-4 items).
7. Spoken Numbers & Pronunciation Glossary (`pronunciation_glossary` + `spoken_numbers_vi`, >= 30 entries): spell out Sino-Vietnamese titles, Qing/Mongol/Siamese proper names, dates, weights, and river/fortress names for OmniVoice TTS (`VietNarrator_su_ke_lai`).
8. Report-Only Claims & Source Discrepancies (`report_only_claims`): quarantine every unverified folklore anecdote, inflated legend, or unconfirmed report claim (MUST be 0% leaked into final script).
9. Verified Geographic Reference Anchors (`chronicle_gis_anchors`, 10-12 entries):
   - Provide `[lon, lat]`, historical name, modern administrative equivalent, and tactical terrain description to keep aerial/establishing 16:9 cinema prompts geographically accurate (note: Pillow 2D/3D `map_dive` cartoon map inserts are permanently banned in V4/V9.1 video renders; any regional Vietnam sovereignty reference metadata retains explicit `HOÀNG SA` `[112.33, 16.53]` and `TRƯỜNG SA` `[114.22, 10.00]`).
```

### 2.3 Quantitative Validation Floors for 9–15m `fact_vault.json`

| Vault Field | Hard Minimum Floor | Verification Gate |
| :--- | :--- | :--- |
| `verified_facts[]` (`status == "verified"`) | **`>= 24` facts** (`24–32` target) | `notebooklm_vault.py validate --vault <path> --min-facts 24` |
| `chronicle_gis_anchors[]` (WGS84 `[lon, lat]`) | **`10–12` anchors** (sovereignty metadata retains **`HOÀNG SA` & `TRƯỜNG SA`**) | Verified for geographic prompt fidelity (zero Pillow cartoon map renders) |
| `pronunciation_glossary` + `spoken_numbers_vi` | **`>= 30` entries** | Normalized before OmniVoice TTS (`VietNarrator_su_ke_lai`) |
| `report_only_claims[]` leakage into `content.json` | **`0` leaks allowed** | `fact_grounding_linter.py --content ... --vault ... --channel su_ke_lai --strict` |

---

## 3. V4 (`V9.1`) Minimalist IMAX `2.39:1` Framing, Chapter Cards & Sparse Single-Line Typography

Canonical visual & motion specification permanently locked from `sys/runs/vn_su_ke_lai_1789_ngoc_hoi_dong_da_full_m1/render_m1_from_scratch.py`.

### 3.1 Absolute Bans (Zero-Negotiation V4 / V9.1 Purity Law)
1. **100% Ban on Full-Sentence Bottom Subtitles (*"Không đọc gì hiện đó"*)**: NEVER burn spoken narration sentences onto Long `16:9` frames. Accessibility subtitles live strictly in the external Vietnamese `.srt` closed-caption track.
2. **100% Ban on 2-Tier `46px` Every-Beat Titles & Rectangular Pillow Boxes**: Permanently retire V9.0 draft's 2-tier (`top_word` + `46px` `main_word`) every-beat typography, opaque/semi-opaque `ImageDraw.rectangle` / `rounded_rectangle` cards, vertical left accent stripes, `[ ]` corner ticks, floating paper cards, Kahoot quiz boxes, and arcade `VS` bars.
3. **100% Ban on Black-Bar Header/Footer Text**: Top and bottom IMAX `2.39:1` letterbox bars MUST remain **100% pure cinema-black** — ZERO top-left campaign title, ZERO top-right mode badge (`M1 · IMAX 2.39:1`), and ZERO bottom-left `>> micro_tag`. ONLY the bottom-right `@SuKeLaiVN` logo sits in the lower-right corner.
4. **100% Ban on Pillow-Drawn 2D/3D Vector Cartoon Maps (`map_dive`)**: Permanently ban `_render_3d_map_dive` and all Pillow-drawn 2D/3D synthetic cartoon map inserts. All `100` beats are **100% native `16:9` moving Google Flow `.mp4` footage**.
5. **100% Ban on Horizontal Whip-Slides & Camera Jitter**: Permanently ban `directional_flow_chain_transition` horizontal whip-slides, screen-shake, and artificial pan/zoom jitter on moving video (**`zoom=1.0, dx=0.0, dy=0.0, cy=0.44`**).
6. **100% Ban on Stitching Unrelated Older Short Episodes & Static PNG Slides**: Zero static PNG Ken Burns slides, zero `9:16` portrait clips cropped into `16:9`, and zero stitched Shorts compilations.

### 3.2 Pure Cinema-Black IMAX `2.39:1` Letterbox Geometry

| Parameter | Gate 0 Preview (`640x360 @ 30fps`, `S=1.0`) | Full HD Master (`1920x1080 @ 30fps`, `S=3.0`) | 2K Master (`2560x1440 @ 30fps`, `S=4.0`) | Visual Role |
| :--- | :--- | :--- | :--- | :--- |
| **Top & Bottom Pure Black Bars (`BAR_H`)** | `38px` top + `38px` bottom | **`114px` top + `114px` bottom** | `152px` top + `152px` bottom | Frames active window at IMAX **`2.39:1`** (`640x284` / **`1920x852`** / `2560x1136`) |
| **Burnished-Gold Gate Hairlines** | `1px` at `y = BAR_H` & `y = H - BAR_H` | **`3px` burnished gold** | `3–4px` burnished gold | Subtle tactile archival framing separating pure black matte from vivid footage |
| **Top-Left / Top-Right / Bottom-Left Bar Text** | **NONE (0px — 100% pure black)** | **NONE (0px — 100% pure black)** | **NONE (0px — 100% pure black)** | Zero visual clutter; pure theatrical IMAX framing |
| **Bottom-Right Channel Watermark** | `34x34`, `10px` margin | **`watermark_150x150.png` (`84x84`, `30px` margin)** | `watermark_150x150.png` (`W-w-36:H-h-36`) | ONLY element allowed in black bar; permanently unobstructed |

### 3.3 Minimalist Chapter Title Cards (`CHƯƠNG I`..`CHƯƠNG X`, `3.60s` Each)

| Element | V4 (`V9.1`) Locked Spec | Retired V9.0 Draft (BANNED) |
| :--- | :--- | :--- |
| **Chapter Kicker** | Small tracked uppercase **`CHƯƠNG I`..`CHƯƠNG X`** (`Oswald-Bold.ttf`, warm gold) | ~~Verbose date/location headers in top black bar~~ |
| **Core Chapter Title** | Concise **`3–4` word core title** (`30px@360p` / **`90px@1080p`** / `120px@1440p`, `BarlowCondensed-ExtraBold.ttf`, crisp ivory-gold) | ~~Oversized multi-line paragraphs~~ |
| **Bottom Subtitle Sentence** | **ZERO (`card_subtitle = ""`)** | ~~Multi-line chapter card subtitles~~ |
| **Gold Divider Line** | **ZERO (removed completely)** | ~~Horizontal gold divider bar between title and subtitle~~ |
| **Background Footage & Vignette** | Bright vivid native `16:9` moving cinema clip behind title with gentle **`0.56..0.72` vignette** | ~~Heavy dark blackout hiding footage~~ |
| **Letterbox Chrome** | **100% pure cinema-black** bars (ONLY bottom-right `@SuKeLaiVN` logo) | ~~Top-left / top-right / bottom-left mono stamps~~ |

### 3.4 Sparse Selective Single-Line Verbatim Emphasis Keywords (`~20–25%` of Beats Only)

| Parameter | V4 (`V9.1`) Locked Contract |
| :--- | :--- |
| **Density & Beat Eligibility** | Show keywords ONLY on **`~20–25%` of beats (`2–3` per chapter, spaced `18–25s` apart)** — e.g., verified `22/100` beats on the 1789 flagship. **`75–80%` of beats remain 100% text-free pure cinema.** |
| **Post-Card Breathing Rule** | **NEVER display a keyword on `beat_*0`** (`beat_000`, `beat_010`, ..., `beat_090`) immediately after a Chapter Title Card so the opening cinema shot breathes without text repetition. |
| **Line Count & Format** | **Single line only (`top_word = ""`)**, `1–3` verbatim uppercase words directly spoken in the narrator's sentence (`target_keyword`). Zero 2-tier kickers (`top_word` permanently empty). |
| **Typography & Size** | `BarlowCondensed-ExtraBold.ttf` — compact **`22px@360p` / `66px@1080p` / `88px@1440p`** in bold ivory-gold **`#FFF5D6`** with clean dark stroke + soft localized shadow (ROI-composited, zero Pillow boxes, zero face/subject overlap). |
| **Pop-In Animation & Sync** | Subtle **`1.06x -> 1.00x` (`0.16s`)** ease-out cubic pop-in (**zero screen-shake**), synced to the exact millisecond the narrator pronounces `target_keyword` via **`_find_word_offset`** (10ms RMS acoustic alignment). |
| **Tactile 1789 SFX Coupling** | Trigger **`-14dB` tactile 1789 SFX** (`elephant_trumpet`, `war_drum`, `fire_roar`, `steel_drum`) **ONLY on keyword beats** (`0` SFX hits on the `75–80%` text-free cinema beats). |

---

## 4. Zero-Dizziness Continuous Camera Chains, Bright Golden-Dawn Grade & High-Resolution Master

### 4.1 Zero-Dizziness Native `16:9` Flow Video Chains (`50` 2-Beat Chains = `100` Beats)

| Chain Rule | V4 (`V9.1`) Locked Specification |
| :--- | :--- |
| **Source Footage Purity** | **`50` native `16:9` (`1280x720`) moving Google Flow `.mp4` clips** covering all **`100` beats** (`2` consecutive beats per `8.0s` clip). **Zero static PNG slides**, **zero `9:16` portrait clips**, **zero Pillow `map_dive` cartoon maps**. |
| **Zero Artificial Pan/Zoom Jitter** | Lock moving video framing strictly to **`zoom=1.0, dx=0.0, dy=0.0, cy=0.44`** — trust the Flow camera's native optical motion without stacking artificial Ken Burns zoom or lateral drift that causes motion sickness. |
| **Intra-Chain Continuity (`beat_{2k} -> beat_{2k+1}`)** | Play the same `8.0s` Flow clip continuously across both paired beats: **`CHAIN_FIRST_HALF = (0.00, 3.30)`** → **`CHAIN_SECOND_HALF = (3.30, 6.60)`**, **`0.0s` blend**, **`MAE = 0.0`** frame-to-frame continuity (`CLIP_CLEAN_MAX_SEC = 6.60` trims trailing Flow exit seams/smoke). |
| **Inter-Chain Transition (`chain_k -> chain_{k+1}`)** | **ONLY a calm stationary `0.20s` optical cross-dissolve (`0px` horizontal/vertical shift)**. **100% permanent ban on `directional_flow_chain_transition` horizontal whip-slides**, whip-pans, and procedural smoke/fog/mist wipes (`0%` smoke pixels). |

### 4.2 Bright Golden-Dawn Cinema Grade & High-Resolution Mastering Pipeline

1. **L3-Cache Golden-Dawn Cinema Grade (`apply_bright_golden_dawn_grade`)**:
   - Decode native `1280x720` Flow clips → `1280x568` `2.39:1` crop → luminous midtone lift (**`gamma <= 0.85`**, zero dark murk) + warm golden highlights + controlled S-curve contrast.
2. **High-Resolution Master Scaling (`1920x1080` Full HD or `2560x1440` 2K @ `30fps`)**:
   - **Full HD Master (`1920x1080 @ 30fps`, `crf=16`, H.264 High@L4.1 `yuv420p`)**: Upscale graded `1280x568` active picture via **`INTER_LANCZOS4` (Lanczos-4)** to `1920x852` + C++ Gaussian optical unsharp detail pass + subtle 35mm fine film grain + native vector typography rendered at full `1920x1080` resolution (zero blurry upscaled text).
   - **2K Master (`2560x1440 @ 30fps`)**: Identical `S=4.0` geometry (`BAR_H=152`, `ACT_H=1136`, chapter title `120px`, keyword `88px`, `watermark_150x150.png` at `W-w-36:H-h-36`) rendered on Colab T4 `h264_nvenc` (always `colab stop` after render).
3. **Master Audio Lock (`48000Hz` stereo)**:
   - Mix `VietNarrator_su_ke_lai` (`1.30x`) + `10 × 3.60s` Chapter Card bronze gongs + **`-14dB` tactile 1789 SFX ONLY on the `~20–25%` keyword beats** + sidechain-ducked heroic war-drum undertone → pre-AAC brickwall `alimiter` → **`-11.0 LUFS (±0.7 LU) / <= -1.0 dBTP`**, muxed at `256k` AAC `48000Hz` stereo.

---

## 5. End-to-End V4 (`V9.1`) Production & 6-Gate QA Verification Checklist

1. **Vault & Single-Campaign Script Gate**: Validate `fact_vault.json` (`--min-facts 24`, `0` `report_only_claims` leaked). Confirm `100%` from-scratch single-campaign script (`10` chapters, `100` beats, `~10–12m`, zero stitched Shorts), `beat_000 <= 24` syl (zero `[pause:...]`), `60–90s` Retention Resets, 2-Choice Debate Outro (zero *"like/share/subscribe/đăng ký/nhấn chuông"*), and pass all 4 linters (`fact_grounding_linter.py --strict`, `script_cadence_checker.py`, `script_diversity_linter.py`, `cta_tone_linter.py`).
2. **100% Moving Video & Chain Continuity Gate**: Verify `50` native `16:9` Flow `.mp4` chains covering `100/100` narration beats (`0` static PNGs, `0` `9:16` portrait clips, `0` Pillow `map_dive` cartoon maps); confirm `0.00 -> 3.30 -> 6.60s` (`MAE=0.0`) intra-chain playback, `zoom=1.0, dx=0.0, dy=0.0, cy=0.44`, and `0.20s` stationary dissolves (`0px` shift, zero whip-slides, `0%` smoke).
3. **Minimalist Chapter Card & Pure Black Bar Gate**: Visually inspect extracted frames confirming ONLY `CHƯƠNG I`..`CHƯƠNG X` + `3–4` word title (`90px@1080p / 120px@1440p`), `card_subtitle=""`, zero gold divider line, bright `0.56..0.72` moving cinema background, and 100% pure black IMAX `2.39:1` bars (`max_top_luma <= 6/255`, zero black-bar text, ONLY bottom-right `@SuKeLaiVN` logo).
4. **Sparse Single-Line Keyword Gate**: Verify keywords appear ONLY on `~20–25%` of beats (`2–3`/chapter, `18–25s` apart, **NEVER on `beat_*0`**), `75–80%` text-free beats, `top_word=""`, `#FFF5D6` (`66px@1080p / 88px@1440p`), `1.06x->1.00x` (`0.16s`) pop-in synced via `_find_word_offset`, and `-14dB` SFX strictly on keyword beats.
5. **High-Res Container & Loudness Gate**: Verify via `ffprobe` (`1920x1080` or `2560x1440`, `30fps`, `h264`, `yuv420p`, `48000Hz` stereo `aac`) and `ffmpeg -af ebur128=peak=true` (**`-11.0 LUFS ±0.7 / <= -1.0 dBTP`**).
6. **Publish Gate**: Package `youtube_title <= 55` chars (zero `P1/P2/Tập` prefix), `10` exact YouTube chapters, Flow-native `16:9` thumbnail (`2–4` uppercase Vietnamese words, `< 2MB`, zero PIL/HTML overlay), external `.srt` captions, and pinned `@SuKeLaiVN` 2-choice debate comment.

---

## 6. V9.2 Parameterized `M1-Flex` Engine & 4 Narrative Archetypes ("Tựa Tựa Khuôn, Không Phải Y Đúc" — `sys/tools/produce_su_ke_lai_long_m1.py`)

To produce many future videos that share the exact same high-retention IMAX `2.39:1` moving-cinema DNA without feeling like rigid carbon copies (*"tựa tựa khuôn, không phải y đúc"*), use the permanent parameterized CLI engine **`sys/tools/produce_su_ke_lai_long_m1.py`** (`M1_FLEX_ENGINE_VERSION = "9.2.0"`). It locks all 6 V4/V9.1 Safety Invariants (`0%` Pillow cartoon maps, `0%` whip-slides, `0` black-bar text, `100%` moving `.mp4` verification, `beat_*0` always text-free, `top_word=""` single-line keywords) while allowing each episode to vary organically across **4 Narrative Archetypes**, **4 Color Presets**, **2 Chapter Styles**, **3 Chain Rhythms**, and **Keyword Density (`0.15..0.30`)**:

### 6.1 The 4 Narrative Archetypes (`6–12` Chapters)

| Archetype (`--archetype`) | Chapter Count | Narrative & Analytical Focus | Recommended `M1-Flex` Preset Combination | Canonical Campaign Examples |
| :--- | :--- | :--- | :--- | :--- |
| **`blitz_campaign`** (*Blitz Campaign / Chiến Dịch Thần Tốc*) | **`8–10` chapters** | Forced-march logistics math, intelligence blackout, multi-column encirclement, combined-arms dawn shock assault | `--color-preset golden_dawn_1789` · `--chapter-style minimal_center_card` · `--chain-pattern balanced_2beat` · `--keyword-density 0.22` | Ngọc Hồi – Đống Đa 1789, Chiến dịch mùa xuân 1789 |
| **`siege_and_trap_anatomy`** (*Siege & Trap Anatomy / Giải Phẫu Vây Thành & Tử Địa*) | **`6–8` chapters** | Mountain-pass terrain bottleneck, feigned retreat, relief-column decapitation, siege counter-measure engineering | `--color-preset monsoon_siege_contrast` · `--chapter-style minimal_center_card` · `--chain-pattern dynamic_1_2_3beat` · `--keyword-density 0.24` | Chi Lăng – Xương Giang 1427, Vây thành Đông Quan |
| **`commander_rivalry_duel`** (*Commander Rivalry Duel / Song Đấu Kỳ Phùng Địch Thủ*) | **`8–11` chapters** | Doctrinal & psychological chess match between two opposing generals, supply-line attrition, decisive counter-stroke | `--color-preset imperial_torch_amber` · `--chapter-style in_scene_cinema_title` · `--chain-pattern epic_3beat` · `--keyword-density 0.20` | Lý Thường Kiệt vs Quách Quỳ 1077, Trần Hưng Đạo vs Thoát Hoan |
| **`naval_and_river_ambush`** (*Naval & River Ambush / Thủy Chiến & Đại Phục Kích Sông Nước*) | **`7–9` chapters** | Flood-to-ebb tidal clock, hidden ironwood stake-fields or mud-bank cannon batteries, fire-raft kill-zone closure | `--color-preset river_mist_teal_gold` · `--chapter-style in_scene_cinema_title` · `--chain-pattern dynamic_1_2_3beat` · `--keyword-density 0.22` | Bạch Đằng 938, Bạch Đằng 1288, Rạch Gầm – Xoài Mút 1785 |

### 6.2 Creative Preset Reference Matrix (`sys/tools/produce_su_ke_lai_long_m1.py`)

- **`--color-preset {golden_dawn_1789,river_mist_teal_gold,monsoon_siege_contrast,imperial_torch_amber}`**:
  - `golden_dawn_1789`: Warm golden dawn (`lift=0.18, warmth=0.14`, default for open-field dawn campaigns).
  - `river_mist_teal_gold`: Crisp river-fog silver-teal shadows with warm bronze/fire highlights (`lift=0.17, warmth=0.06`, naval campaigns).
  - `monsoon_siege_contrast`: High-clarity slate & ember contrast (`lift=0.16, warmth=0.09`, mountain/fortress sieges).
  - `imperial_torch_amber`: Deep court bronze & torchlight clarity (`lift=0.19, warmth=0.16`, dynastic intrigue & strategic council episodes).
- **`--chapter-style {minimal_center_card,in_scene_cinema_title}`**:
  - `minimal_center_card`: `3.2s–3.6s` (`3.60s`) dimmed moving-cinema card (`0.56..0.72` vignette) with tracked `CHƯƠNG I..N` + 3–4 word core title (`0` bottom subtitle sentence, `0` divider bar).
  - `in_scene_cinema_title`: Netflix-style chapter title overlay directly on the first `3.5s` of the opening chapter scene (`beat_*0`) at full brightness without a separate card pause.
- **`--chain-pattern {balanced_2beat,dynamic_1_2_3beat,epic_3beat}`**:
  - `balanced_2beat`: `2` beats per `8.0s` Flow `.mp4` clip (`0.00->3.30s` + `3.30->6.60s` unbroken continuous playback).
  - `dynamic_1_2_3beat`: Adaptive pacing — `3`-beat (`0.0->2.2->4.4->6.6s`) continuous long-take chains for opening/aftermath chapters, `2`-beat (`0.0->3.3->6.6s`) chains for setup chapters, and `1`-beat (`0.0->5.2s` `1.0x` real-time speed) rapid cuts during battle climax chapters.
  - `epic_3beat`: `3` beats per `8.0s`/`10.0s` Flow `.mp4` clip (`0.0->2.2->4.4->6.6s`) for slower strategic/biographical episodes.
- **`--keyword-density <float 0.15..0.30>`** (default `0.22`): Automatically enforces sparse single-line verbatim emphasis keywords (`~18–28%` of beats, `>= 70–72%` text-free pure cinema, **never on the first beat of any chapter `beat_*0`**, `top_word == ""`, compact `66px@1080p / 88px@1440p` ivory-gold `#FFF5D6`).

### 6.3 Turnkey CLI Execution (`sys/tools/produce_su_ke_lai_long_m1.py`)

```bash
# 1. Validate M1-Flex V9.2 preset & safety invariants:
PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
  --stage validate-flex-spec \
  --archetype naval_and_river_ambush \
  --color-preset river_mist_teal_gold \
  --chapter-style in_scene_cinema_title \
  --chain-pattern dynamic_1_2_3beat \
  --keyword-density 0.22 \
  --resolution 1080p

# 2. Build timeline, -11.0 LUFS master WAV, impact SRT & full Vietnamese CC SRT:
PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
  --stage build-timeline \
  --job-dir sys/runs/<job_id> \
  --script sys/runs/<job_id>/script.json \
  --output-dir video/<job_id> \
  --color-preset golden_dawn_1789 \
  --chapter-style minimal_center_card \
  --chain-pattern balanced_2beat \
  --keyword-density 0.22 \
  --resolution 1080p \
  --total-shards 8

# 3. Render 8 parallel shards (with mandatory 100% moving .mp4 verification):
for sid in 1 2 3 4 5 6 7 8; do
  PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
    --stage render-shard --shard "$sid" \
    --job-dir sys/runs/<job_id> --require-moving-video &
done
wait

# 4. Losslessly assemble final MP4 + 20-panel showcase & regenerate full CC SRT:
PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
  --stage assemble --job-dir sys/runs/<job_id> --output-dir video/<job_id>
PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
  --stage full-cc-srt --job-dir sys/runs/<job_id>
```


> **Core Visual & FX Skill:** [vp-visual-fx](../../../../.agents/skills/vp-visual-fx/SKILL.md)
