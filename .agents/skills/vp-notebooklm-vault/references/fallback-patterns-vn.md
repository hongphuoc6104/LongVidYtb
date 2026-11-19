# Offline Fallback Patterns (VN & EN, Short & Long)

Use this file when Notebook 1 (`Pattern Vault`) cannot be queried live. Copy **structure only**, never copy exact wording from reference channels. Enforced by `script_cadence_checker.py`, `script_diversity_linter.py`, `cta_tone_linter.py`, and `fact_grounding_linter.py`.

---

## 1. Hook Formulas (First Sentence `<= 18` Syllables VN Short / `<= 24` Syllables VN Long)
Zero `[pause:...]` in `SC01` (first 15s). Never start with *"Xin chào"*, *"Hôm nay chúng ta..."*, or *"Hãy tưởng tượng..."*.

| Hook Archetype | Structural Formula | Best Channels |
|---|---|---|
| **Counter-Intuitive Action** | `"[Ai đó] làm [hành động tưởng đúng] — ngay lập tức kích hoạt [hậu quả ngược]."` | `chanh_niem_ke`, `ho_so_ky_la`, `su_ke_lai` |
| **Hidden Price / Body Shock** | `"[Thói quen / món quen] chỉ mất [con số nhỏ], nhưng âm thầm lấy đi [thiệt hại thật]."` | `co_the_ke`, `tui_tien`, `dia_com`, `nao_luoi` |
| **Mechanism Paradox** | `"Nếu thiếu đúng [chi tiết nhỏ], [hệ thống lớn] sụp đổ chỉ trong [thời gian]."` | `ban_do_quyen_luc`, `banh_rang`, `ua_sao_vay`, `vu_tru_ti_hon` |
| **Everyday Trap** | `"Ký vào [thứ quen thuộc] mà bỏ qua [1 dòng/chi tiết], bạn mất trắng [quyền lợi]."` | `luat_doi_thuong`, `luat_ngam`, `nghe_song_sot`, `thuong_cho_kheo` |

---

## 2. Format Pacing Blueprints

### A. `short_9x16` (48–60s · 12–18 beats · Vietnamese ~4.0–4.4 syl/s)
- **0–5s (Beats 1–2):** Cold Open shock hook (`<= 18` syl) + open loop. Zero dead air.
- **5–18s (Beats 3–5):** Stakes + first everyday Vietnamese micro-bridge.
- **18–35s (Beats 6–9):** Core causal mechanism + **exact verified number & unit** from Fact Vault.
- **35–45s (Beats 10–12):** Twist ("Nhưng thực tế..." / "Sai lầm nằm ở...") overturning the common assumption.
- **45–58s (Last 15%, final 1–2 beats):** Close the loop + `close` CTA (`<= 24` syl) + `channel bridge` (`<= 22` syl, `<= 38` combined outro syllables) pointing to `parent_long_id`. Zero *"like/share/subscribe"*.

### B. `long_16x9` (8m30s–13m · 8–12 chapters / 5 acts · 240–350 beats)
- **0–45s (Chapter 1):** Counter-intuitive Cold Open (`<= 24` syl first sentence) -> personal/VN stakes -> Central Open Loop.
- **Every 60–90s (Chapters 2–8):** Mandatory **Retention Reset** (contrast pivot, false hypothesis elimination, concrete analogy, or map/scale shift) + one clear visual/causal step per clause.
- **35–45% Mark:** At most 1 natural `mid_cta` inviting perspective in comments.
- **Final 10% (Closing Chapter):** Answer original Open Loop -> actionable mental/practical takeaway -> calm debate question.

### C. `serialized_detail_short` (50–60s/tập · 12 beats · Series Tập 1 / Tập 2 / Tập 3)
- **Beats 0–1 (0–8s):** Counter-intuitive turning-point Hook (`<= 18` syl, exact hour/date) + strategic paradox.
- **Beats 2–5 (8–25s):** Granular chronological setup — terrain, hour-by-hour execution, specific verified mechanism (quarantine unverified folklore in `report_only_claims`).
- **Beats 6–9 (25–43s):** Tactical turning point & psychological collapse / micro-detail payoff (each beat adds 1 concrete verifiable action).
- **Beat 10 (43–49s):** Escalating historical **Cliffhanger** introducing the deadlier obstacle awaiting in Tập kế tiếp.
- **Beat 11 (49–58s, final 15%):** **Ending Pattern #4 — `Serialized Cliffhanger Loop`**: concise bridge (`<= 22` syl) teasing Tập 2 + naming the channel + open question (`<= 24` syl, `<= 38` combined outro syllables). Zero *"like/share/subscribe"*.

### D. 4 Ending Patterns (Quick Matrix)
1. **Answer + Sting:** Resolve loop + 1 sharp lingering consequence.
2. **Loop Back:** Closing clause echoes Beat 1 imagery to boost replays.
3. **Channel Bridge + Debate Question:** Standard standalone Short funnel to `parent_long_id`.
4. **Serialized Cliffhanger Loop:** End on the immediate next physical obstacle + tease `Tập tiếp theo trên [Tên Kênh]` + 1 prediction question for viewers.

---

## 3. Spoken Vietnamese & Banned Markers
- Alternate punchy short sentences (`4–9` words) with clean causal sentences (`14–22` words). Never place a comma between subject and verb.
- Spell out numbers and foreign symbols into `spoken_numbers_vi` / `pronunciation_glossary` before OmniVoice TTS.
- **Strictly Banned AI-Translationese:** *"Có một sự thật mất lòng là..."*, *"Mấu chốt/Bí mật/Nghịch lý nằm ở..."*, *"Đánh giá công bằng thì..."*, *"Ít ai biết rằng..."*, *"Tin vui/buồn là..."*, *"Tóm lại là..."*, *"Hãy cùng khám phá..."*.
