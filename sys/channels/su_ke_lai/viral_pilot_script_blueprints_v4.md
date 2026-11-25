# Viral Short Episode Blueprints V4 (`EP07`, `EP08`, `EP09`) — Sử Kể Lại (`su_ke_lai_viral_v4`)

- **Channel:** **Sử Kể Lại** (`su_ke_lai`, `@SuKeLaiVN`)
- **Target View Tier:** **`100,000 – 1,000,000+` Views / Short** (Breakout from current `1.8K–3.2K` baseline diagnosed in `sys/channels/su_ke_lai/viral_pattern_brief_v4.json`)
- **Empirical Reference Benchmarks:** `CD Media - Quân Sự` (`XN05y-9LIKE` `456K`, `7pJgdZpuaNE` `154K`, `qR5LJRcJebA` `122K`) & `Dòng Máu Việt` (`n9oZSIRTLUo` `3.59M`, `7QrEPUHLzgI` `2.89M`, `exQOdR_i16A` `761K`, `a4uUFYSvJIc` `296K`, `UQrgEvoyGgo` `275K`)
- **Visual, Voice & Render Lock:** `su_ke_lai_35mm_live_action_v3` (100% full-bleed edge-to-edge 35mm anamorphic live-action, positive framing, zero film-stock/sprocket tokens, zero sand-tables, `1440x2560@30fps` 2K vertical, `hybrid_2k` = `12 veo_3_1_lite` Seam Mode + `8 2k_native_kenburns`, `VietNarrator_su_ke_lai` @ `1.30x`, 6-mode prosody + `heroic_vietnam_epic` 5-Act score `-11.0 LUFS / -1.0 dBTP`, `heroic_banner >= 132px` `<= 4` uppercase words, `watermark_150x150.png` at `W-w-36:H-h-36`, `publish_policy.short_attach_related_video: false`)
- **Executable Pilot Compiler (EP07):** [`sys/scratch/ep07_viral_pilot_100k_1m_spec.py`](../../scratch/ep07_viral_pilot_100k_1m_spec.py) *(Verified **9/9 deterministic gates PASS**, 0 errors, 0 warnings)*

---

## 0. Tổng Quan 3 Tập Pilot V4 (`EP07`, `EP08`, `EP09`) & Ma Trận Đối Chiếu Công Thức 100K–1M

| Episode | Viral Pillar (`su_ke_lai_viral_v4`) | Empirical Benchmark | Standalone YouTube Title (`<= 55` chars, zero `P1/P2`) | Flow Thumbnail (`<= 4` words) | Beat 0 Hook (`<= 16` syl, 0 pause) | Linter Status |
|---|---|---|---|---|---|---|
| **EP07** *(Executable Pilot)* | **Pillar 2** — Binh Chủng Tinh Nhuệ & Vũ Khí Bí Mật Đại Việt | `CD Media - Quân Sự` (`456K` views `XN05y-9LIKE`) | `Tượng Binh & Hỏa Hổ Tây Sơn: Vũ Khí Nghiền Nát Kỵ Binh` (`54` chars) | `VOI CHIẾN HỎA HỔ` (`4` words) | *"100 voi chiến Tây Sơn cùng hỏa hổ nghiền nát kỵ binh ra sao?"* (`15` syl) | **9/9 Gates PASS** (`0` err, `0` warn) |
| **EP08** | **Pillar 1** — Giải Mã Câu Nói Dân Gian Lịch Sử | `Dòng Máu Việt` (`275K` views `UQrgEvoyGgo`) | `Hăm Mốt Lê Lai, Hăm Hai Lê Lợi: Cú Thế Mạng Cứu Sơn Hà` (`54` chars) | `ĐỔI ÁO CỨU VUA` (`4` words) | *"Vì sao dân Việt cúng giỗ Lê Lai trước vua Lê Lợi đúng một ngày?"* (`15` syl) | **Cadence + CTA + Diversity PASS** |
| **EP09** | **Pillar 3** — Xếp Hạng / Đối Chiếu Hoàng Đế & Danh Tướng 1v1 | `Dòng Máu Việt` (`296K–761K` views `a4uUFYSvJIc` / `exQOdR_i16A`) | `3 Vị Hoàng Đế Đại Việt Trực Tiếp Cầm Gươm Xung Trận` (`51` chars) | `VUA CẦM GƯƠM CHIẾN` (`4` words) | *"Ba vị vua Việt Nam nào rời ngai vàng trực tiếp cầm gươm chém giặc?"* (`15` syl) | **Cadence + CTA + Diversity PASS** |

*(Ghi chú đồng bộ kho đề tài: Ba tập `EP07`–`EP09` tương ứng trực tiếp với 3 trụ cột mở đầu mạnh nhất trong `sys/channels/su_ke_lai/viral_topic_bank_100k_1m.json` và `sys/channels/su_ke_lai/notebooklm_viral_sources_pack.md`, được chuẩn hóa theo thứ tự triển khai pilot V4: EP07 Binh chủng Tây Sơn → EP08 Giải mã Lê Lai/Lê Lợi → EP09 Xếp hạng 3 Hoàng đế cầm gươm).*

### Quy Tắc Bất Biến Chung Cho Cả 3 Tập (`V4 Breakout Locks`)
1. **Standalone Mass-Curiosity Packaging:** Tuyệt đối cấm `P1/P2/P3`, `Tập 1/Tập 2` ở tiêu đề; độ dài `<= 55` ký tự; khán giả lạnh hiểu ngay nghịch lý trong `< 1.5s`.
2. **Beat 0 Instant Shock Hook:** Strictly `<= 16` âm tiết tiếng Việt, **0** `[pause:...]`, **0** địa danh vi mô khó hiểu ở giây `0.0–2.5s`.
3. **Chính Sử Đối Chiếu & Cách Ly Dã Sử:** 100% số liệu, niên đại, đơn vị quân sự đối chiếu từ *Hoàng Lê Nhất Thống Chí*, *Đại Việt Sử Ký Toàn Thư*, *Lam Sơn Thực Lục*, *Khâm Định Việt Sử Thông Giám Cương Mục*, *Đại Nam Chính Biên Liệt Truyện*, *Khâm Định An Nam Kỷ Lược*. Mọi giai thoại dân gian (`report-only`) bị cách ly tuyệt đối khỏi lời thoại.
4. **Debate-Trigger Ending & Pinned Comment Loop (`> 0.15%` Comm/View):** 15% cuối kịch bản (`close <= 24` từ, `bridge <= 22` từ, tổng `<= 38` từ, cấm *"like/share/subscribe/đăng ký/nhấn chuông"*) đặt câu hỏi tranh luận 2–3 lựa chọn khớp hoàn toàn với Bình luận ghim `@SuKeLaiVN`.
5. **Peak Publish Slots (GMT+7):** Ưu tiên `23:30–00:15 GMT+7` (`32.60%` view share) hoặc `18:45–19:15 GMT+7` (`15.44%` view share); giữ `publish_policy.short_attach_related_video: false`.

---

## 1. EP07 BLUEPRINT (EXECUTABLE PILOT) — *Tượng Binh & Hỏa Hổ Tây Sơn: Vũ Khí Nghiền Nát Kỵ Binh*

### 1A. Packaging, Benchmarks & Technical Spec
- **Job ID:** `vn_su_ke_lai_ep07_tuong_binh_hoa_ho_tay_son_1789_short`
- **Viral Pillar:** **Pillar 2 — Binh Chủng Tinh Nhuệ & Vũ Khí Bí Mật Đại Việt** (modeled on `CD Media - Quân Sự` `456K` views elite-unit teardown + `Dòng Máu Việt` 5-Act heroic climax)
- **YouTube Title (`54` chars `<= 55`):** `Tượng Binh & Hỏa Hổ Tây Sơn: Vũ Khí Nghiền Nát Kỵ Binh`
- **Flow-Native Thumbnail Text (`4` uppercase words):** `VOI CHIẾN HỎA HỔ`
- **Beat 0 Shock Hook (`15` syl `<= 16`, `0` pause):** *"100 voi chiến Tây Sơn cùng hỏa hổ nghiền nát kỵ binh ra sao?"*
- **Primary Format (Executable Spec):** Mode B (`serialized_detail_short`, `20` beats `B00–B19`, `4` chunks × `5` beats, `348` syllables, est. `99.80s`, `12 veo_3_1_lite` Seam Mode + `8 2k_native_kenburns`, `120` Flow video credits)
- **Optional Mode A+ Cut-Down (`viral_fast_loop_short`, `16` beats / `~64s`):** Có thể rút gọn trực tiếp thành bản Fast Loop `>92%` APV bằng cách giữ trọn lõi `B00, B01, B02, B03, B04, B06, B07, B08, B09, B10, B11, B12, B13, B14, B15, B19` (bỏ `B05, B16, B17, B18`, tổng `278` syl / `~64s`, khớp chính xác khung `61–74s` của `CD Media - Quân Sự`).
- **Executable Compiler:** `sys/scratch/ep07_viral_pilot_100k_1m_spec.py` -> outputs `video/vn_su_ke_lai_ep07_tuong_binh_hoa_ho_tay_son_1789_short/{fact_vault.json, ep07_viral_pilot_100k_1m_short_spec.json, scene_map.json, metadata_youtube.md, skill1..3_output.md}`

### 1B. Primary Chronicle Citations & Quarantined `report-only` Claims
- **Verified Primary Sources (`F01–F12`):**
  1. *Hoàng Lê Nhất Thống Chí — Hồi thứ 14 (Ngô Gia Văn Phái):* Rạng sáng mùng 5 tháng Giêng năm Kỷ Dậu (30/1/1789), vua Quang Trung đánh đại đồn Ngọc Hồi của hơn 20 vạn quân Thanh; huy động hơn 100 voi chiến, ghép 3 tấm ván gỗ buộc dày rơm ướt làm mộc bài (10 người khiêng lưng giắt dao ngắn, 20 người cầm binh khí & hỏa hổ theo sau, lập 20 đội xung kích), vứt ván phóng hỏa hổ gặp gió bắc khói lửa mịt mù phá tan đồn trong buổi sáng, trưa mùng 5 tiến vào Thăng Long trong chiến bào đỏ ám đen khói thuốc súng.
  2. *Khâm Định An Nam Kỷ Lược (Thanh sử):* Tướng Thanh báo cáo kinh hoàng trước đội voi chiến Tây Sơn và thứ vũ khí phóng lửa nhựa thông gọi là *"hỏa hổ"*; ngựa chiến kỵ binh Mãn Thanh vừa nghe tiếng voi gầm và mùi lửa khói lập tức hoảng loạn lồng lên quay đầu giẫm đạp lên bộ binh nhà Thanh.
  3. *Khâm Định Việt Sử Thông Giám Cương Mục (Chính Biên Q.47)* & *Đại Nam Chính Biên Liệt Truyện (Sơ Tập Q.30 — Ngụy Tây Liệt Truyện):* Ghi nhận tổ chức hơn 100 tượng binh Tây Sơn bọc giáp da, bành gỗ cõng đại bác nhỏ và xạ thủ hỏa khí cơ động phối hợp chặt với bộ binh cảm tử.
  4. *Đại Việt Sử Ký Toàn Thư (Bản Kỷ Q.2, 5, 10):* Xác nhận truyền thống tượng binh xuyên suốt từ thời Lý, Trần đến Lam Sơn trước khi Tây Sơn nâng lên đỉnh cao hợp đồng binh chủng năm 1789.
- **Quarantined Folklore (`report-only` — CẤM đưa vào lời thoại):**
  - `RO01`: Voi Tây Sơn mặc giáp sắt nguyên khối nặng 2 tấn đúc kiểu châu Âu *(thực tế dùng giáp da trâu nhiều lớp + bành gỗ giữ tốc độ)*.
  - `RO02`: Ống hỏa hổ phun lửa xa 100 mét như súng phun lửa hiện đại *(thực tế là vũ khí hỏa công áp sát cự ly gần)*.
  - `RO03`: Huy động 500 voi chiến cùng lúc tại đồn Ngọc Hồi *(chính sử ghi hơn 100 voi chiến)*.

### 1C. Full 20-Beat 5-Act Production Script (`B00–B19`, Verified 9/9 Gates PASS)

| Beat | Hồi | Time | Syl | Delivery Mode | Asset Mode | Banner (`136px`) | Spoken Vietnamese Narration | 35mm Live-Action Visual Anchor (`allowed_text=None`) |
|---|---|---|---:|---|---|---|---|---|
| `B00` | Hồi 1 | `0.0–4.3s` | 15 | `climax_heroic` | `flow_video` | `VOI CHIẾN HỎA HỔ` | 100 voi chiến Tây Sơn cùng hỏa hổ nghiền nát kỵ binh ra sao? | Low-angle 28mm voi chiến bọc giáp da trâu cõng đại bác đồng xông qua khói lửa Ngọc Hồi cùng chiến binh cầm hỏa hổ |
| `B01` | Hồi 1 | `4.3–9.6s` | 19 | `narrative_cinema` | `flow_video` | — | Rạng sáng mùng 5 Tết 1789, hơn 20 vạn quân Thanh chốt chặt Ngọc Hồi. | Wide crane 28mm đại đồn Ngọc Hồi lũy đất cao dày, chông tre, đại bác sắt và hàng vạn kỵ binh Thanh trong sương đông |
| `B02` | Hồi 1 | `9.6–14.7s` | 17 | `tense_whisper` | `2k_native_kenburns` | — | Trước lũy dày đầy đại bác và kỵ binh thiện chiến, bộ binh thường khó tiến nổi. | Medium OTS 50mm từ mặt lũy nhìn qua họng đại bác đen ngòm xuống bãi chông và kỵ binh Mãn Thanh áo giáp xanh xám |
| `B03` | Hồi 1 | `14.7–19.1s` | 15 | `tactical_breakdown` | `flow_video` | — | Nhưng vua Quang Trung nắm trong tay hai át chủ bài khiến địch khiếp vía. | Low-angle orbit 35mm vua Quang Trung khăn đỏ-vàng, giáp vảy sắt, chiến bào đỏ ngồi uy nghiêm trên lưng voi chỉ huy *(post-pause 340ms)* |
| `B04` | Hồi 2 | `19.1–23.8s` | 16 | `tactical_breakdown` | `flow_video` | `100 VOI CHIẾN 1789` | Đòn đầu tiên là đội tượng binh, quy tụ hơn 100 voi chiến thiện nghệ. | Wide truck-lateral 28mm đội hình hơn 100 thớt voi chiến bọc giáp da trâu dàn hàng ngang tiến bước giữa sương lạnh |
| `B05` | Hồi 2 | `23.8–28.6s` | 17 | `narrative_cinema` | `2k_native_kenburns` | — | Lịch sử Đại Việt từ thời Lý, Trần đến Lam Sơn đều dùng voi làm mũi nhọn. | Atmospheric 35mm đoàn tượng binh và giáo binh Đại Việt vượt đèo núi sương sớm dưới ánh bình minh vàng ấm |
| `B06` | Hồi 2 | `28.6–33.7s` | 18 | `tactical_breakdown` | `flow_video` | `ĐẠI BÁC TRÊN LƯNG` | Nhưng Tây Sơn nâng tầm tượng binh thành pháo đài di động. Bành gỗ cõng đại bác nhỏ. | Tight macro orbit 85mm khẩu đại bác đồng nhỏ gắn chắc trên bành gỗ cứng buộc dây gai qua giáp da trâu lưng voi |
| `B07` | Hồi 2 | `33.7–38.6s` | 17 | `tactical_breakdown` | `2k_native_kenburns` | — | Lính xạ thủ ngồi cao trên lưng voi, dễ dàng nã hỏa lực xuống chiến hào giặc. | Elevated OTS 50mm từ bành voi nhìn xuống: hai xạ thủ Tây Sơn ngắm đại bác và hỏa mai xuống chiến hào đồn giặc *(post-pause 340ms)* |
| `B08` | Hồi 3 | `38.6–43.5s` | 17 | `tactical_breakdown` | `flow_video` | `HỎA HỔ PHUN LỬA` | Át chủ bài thứ hai mang tên hỏa hổ, thứ ống phun lửa nhựa thông rực cháy. | Tight macro push-in 85mm chiến binh Tây Sơn giữ chặt ống tre bọc đai sắt hỏa hổ phun tia lửa nhựa thông sáng rực |
| `B09` | Hồi 3 | `43.5–49.2s` | 20 | `tense_whisper` | `2k_native_kenburns` | — | Hỏa hổ chỉ mạnh khi áp sát. Nếu lao bừa qua làn đạn pháo, cảm tử quân sẽ ngã gục. | Atmospheric pull-back 35mm bãi bùn trống đầy hố đạn pháo và khói thuốc súng trước họng pháo Ngọc Hồi |
| `B10` | Hồi 3 | `49.2–54.1s` | 17 | `tactical_breakdown` | `flow_video` | — | Quang Trung ghép 3 tấm ván gỗ, bọc dày rơm ướt làm tường chắn đạn di động. | Medium orbit-left 50mm ba chiến binh Tây Sơn buộc chặt bó rơm rạ thấm đẫm nước lên tấm mộc bài ghép 3 ván gỗ dày |
| `B11` | Hồi 3 | `54.1–59.5s` | 20 | `urgent_escalation` | `flow_video` | — | Cứ 10 người khiêng ván, 20 người theo sau. 20 đội xung kích lặng lẽ áp sát lũy. | Wide push-in 28mm 20 đội cảm tử nối hàng sau bức tường mộc bài rơm ướt bốc hơi nước tiến sát lũy Ngọc Hồi *(post-pause 360ms)* |
| `B12` | Hồi 4 | `59.5–65.2s` | 17 | `tense_whisper` | `flow_video` | — | Khói đạn đặc quánh rạng sáng mùng 5. `[pause:550ms]` Đột nhiên, tiếng voi gầm xé toang bầu trời. | Tight macro orbit-right 85mm đôi mắt sắc lạnh của chiến binh Tây Sơn sau ván rơm ướt giữa làn khói đặc *(silence_vacuum tim đập)* |
| `B13` | Hồi 4 | `65.2–70.4s` | 19 | `climax_heroic` | `flow_video` | `NGỌC HỒI VỠ TRẬN` | Hơn 100 voi chiến tràn lên phá lũy! Ngựa kỵ binh Thanh nghe tiếng voi liền hoảng loạn. | Low-angle push-in 28mm voi chiến Tây Sơn húc gãy hàng rào tre Ngọc Hồi, chiến mã Mãn Thanh chồm vó kinh hoàng |
| `B14` | Hồi 4 | `70.4–74.7s` | 15 | `climax_heroic` | `flow_video` | — | Chiến mã giặc lồng lên quay đầu, giẫm đạp thẳng vào đội hình quân Thanh. | Wide truck-lateral 28mm đàn ngựa chiến Thanh chạy ngược hoảng loạn đâm sầm vào bộ binh giữa sân đồn mịt khói |
| `B15` | Hồi 4 | `74.7–79.8s` | 19 | `urgent_escalation` | `flow_video` | — | Tức thì, quân cảm tử vứt ván rơm. Hàng loạt ống hỏa hổ phun lửa thiêu rụi đồn giặc. | Medium push-in 35mm lính cảm tử bỏ ván rơm ướt dưới bùn, đồng loạt bắn luồng lửa nhựa thông hỏa hổ thiêu rụi lũy gỗ *(post-pause 360ms)* |
| `B16` | Hồi 5 | `79.8–84.6s` | 17 | `narrative_cinema` | `2k_native_kenburns` | — | Gió bắc thổi ngược khói lửa mịt mù. Đồn Ngọc Hồi sụp đổ ngay trong buổi sáng. | Wide pull-back 28mm đại đồn Ngọc Hồi ngập khói gió bắc, cờ đỏ Tây Sơn dựng lên trên đỉnh lũy dưới nắng sớm |
| `B17` | Hồi 5 | `84.6–89.6s` | 17 | `reflective_lesson` | `2k_native_kenburns` | — | Vua Quang Trung cưỡi voi tiến vào Thăng Long, chiến bào đỏ sạm đen vì khói súng. | Low-angle hero 35mm vua Quang Trung uy nghi trên lưng voi qua cổng thành Thăng Long, chiến bào đỏ ám đen khói súng |
| `B18` | Hồi 5 | `89.6–94.6s` | 17 | `reflective_lesson` | `2k_native_kenburns` | — | Tượng binh, mộc bài rơm và hỏa hổ tạo thành mũi khoan thép không thể cản phá. | Atmospheric truck-lateral 35mm tổ hợp voi chiến cõng đại bác, mộc bài rơm ướt và ống hỏa hổ trong nắng sáng |
| `B19` | Hồi 5 | `94.6–99.8s` | 19 | `reflective_lesson` | `2k_native_kenburns` | — | Theo bạn, voi chiến hay hỏa hổ làm địch vỡ trận? Chọn và xem tiếp trên Sử Kể Lại. | Symmetrical final-hold 28mm voi chiến bọc giáp đối xứng ánh lửa hỏa hổ trên nền trời rạng đông cờ đỏ tung bay |

### 1D. Flow-Native Thumbnail Prompt (`VOI CHIẾN HỎA HỔ`, Positive Framing, Zero Sprocket Tokens)
```text
Full-frame edge-to-edge vertical historical live-action cinema shot on 35mm anamorphic cinema lens, natural film grain, full-bleed image to all four edges, explosive 1789 winter dawn Ngọc Hồi battle theatrical poster composition. In the upper-middle smoky sky band (15% to 33% height), massive bold weathered antique-gold uppercase Vietnamese cinematic title lettering with crisp heavy dark drop-shadow reading exactly "VOI CHIẾN HỎA HỔ", razor-sharp Vietnamese diacritics, centered cleanly against brooding indigo-and-ember dawn battle smoke. In the middle and lower frame (35% to 92%), a colossal battle-scarred Tây Sơn war elephant clad in layered dark-brown buffalo-hide armor and a carved hardwood howdah mounting a smooth cast-bronze swivel cannon charges straight forward through churning mud and sparks, flanked by a resolute Tây Sơn vanguard warrior in a solid crimson headband and dark-indigo tunic aiming a roaring iron-bound bamboo hỏa hổ fire-lance spewing bright amber resin flame across the smoky dawn air while panicked enemy cavalry horses rear back into mist behind them. Intense firelight-and-indigo chiaroscuro, unmarked silk banners, practical live-action historical cinema look.
```

### 1E. Polarizing 2-Choice Pinned Comment (`@SuKeLaiVN`)
> 📌 [GIẢI PHẪU BINH CHỦNG ĐẠI VIỆT — SỬ KỂ LẠI]: Tại đại đồn Ngọc Hồi rạng sáng mùng 5 Tết Kỷ Dậu (1789), hơn 20 vạn quân Thanh vỡ trận chỉ trong một buổi sáng! Theo góc nhìn của bạn, yếu tố nào mới là đòn chí mạng khiến kỵ binh Mãn Thanh kinh hoàng tháo chạy: (1) Đội hình hơn 100 Tượng Binh cõng đại bác làm chiến mã giặc hoảng loạn giẫm đạp nhau, hay (2) Chiến thuật lá chắn rơm ướt áp sát cùng ống phóng lửa Hỏa Hổ thiêu rụi lũy địch? Chọn số 1 hoặc 2 và để lại phân tích của bạn bên dưới!

### 1F. One-Command Production Execution (`EP07`)
```bash
# Step 1: Compile & Verify all 9 deterministic gates
PYTHONPATH=sys sys/.venv/bin/python sys/scratch/ep07_viral_pilot_100k_1m_spec.py

# Step 2: Run full 2K Turbo Single-Pass Production (Colab T4 OmniVoice + Flow Stage A/B + 4-GPU NVENC)
PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_serialized_short.py \
  --spec video/vn_su_ke_lai_ep07_tuong_binh_hoa_ho_tay_son_1789_short/ep07_viral_pilot_100k_1m_short_spec.json \
  --stage all --visual-mode hybrid_2k --render-mode single_pass \
  --colab-tts-workers 3 --colab-render-workers 4 --img-workers auto --vid-workers auto --nvenc-preset p4
```

---

## 2. EP08 BLUEPRINT — *Hăm Mốt Lê Lai, Hăm Hai Lê Lợi: Cú Thế Mạng Cứu Sơn Hà*

### 2A. Packaging, Benchmarks & Technical Spec
- **Job ID:** `vn_su_ke_lai_ep08_ham_mot_le_lai_ham_hai_le_loi_1419_short`
- **Viral Pillar:** **Pillar 1 — Giải Mã Câu Nói Dân Gian Lịch Sử** (modeled on `Dòng Máu Việt` `UQrgEvoyGgo` *"Hăm Mốt Lê Lai, Hăm Hai Lê Lợi"* — `275,792` views, `2.02%` like/view)
- **YouTube Title (`54` chars `<= 55`):** `Hăm Mốt Lê Lai, Hăm Hai Lê Lợi: Cú Thế Mạng Cứu Sơn Hà`
- **Flow-Native Thumbnail Text (`4` uppercase words):** `ĐỔI ÁO CỨU VUA`
- **Beat 0 Shock Hook (`15` syl `<= 16`, `0` pause):** *"Vì sao dân Việt cúng giỗ Lê Lai trước vua Lê Lợi đúng một ngày?"*
- **Format:** Mode B (`serialized_detail_short`, `20` beats `B00–B19`, `4` chunks × `5` beats, `340` syllables, est. `97.9s`, `12 veo_3_1_lite` Seam Mode + `8 2k_native_kenburns`)
- **Pre-Verified Grounded Fact Vault:** `sys/runs/vn_su_ke_lai_ep07_viral_pilot_short/fact_vault.json` (and Section 5 of `sys/channels/su_ke_lai/notebooklm_viral_sources_pack.md`, validated `12` verified facts, `0` errors)

### 2B. Primary Chronicle Citations & Quarantined `report-only` Claims
- **Verified Primary Sources:**
  1. *Đại Việt Sử Ký Toàn Thư — Bản Kỷ Thực Lục Quyển 10:* Tháng 4 năm Kỷ Hợi (1419), quân Minh vây chặt núi Chí Linh (Thanh Hóa); Lê Lợi hỏi tướng sĩ ai dám đổi áo xưng danh hiệu mình bắt chước Kỷ Tín thời Hán Cao Tổ; Lê Lai đứng ra nhận lệnh, xung trận bị giặc bắt xử cực hình; năm 1428 Lê Thái Tổ truy phong Lê Lai làm Đệ Nhất Công Thần (Thái Úy Phúc Quốc Công).
  2. *Lam Sơn Thực Lục — Quyển 1 (Nguyễn Trãi):* Nghĩa quân cạn sạch lương thực hơn 10 ngày chỉ còn vài trăm người; Lê Lai khoác hoàng bào khấn trời đất, chỉ huy 2 voi chiến cùng 500 quân cảm tử hô vang *"Chúa Lam Sơn ở đây!"*; quân Minh tưởng Lê Lợi đã chết bèn rút về Đông Quan.
  3. *Khâm Định Việt Sử Thông Giám Cương Mục — Chính Biên Quyển 13* & *Đại Việt Thông Sử (Lê Quý Đôn):* Xác nhận Lê Lai quê thôn Dựng Tú (Lương Giang, Thanh Hóa), đứng thứ 2 trong 19 người dự Hội thề Lũng Nhai (1416); trước khi băng hà ngày 22 tháng 8 âm lịch năm Quý Sửu (1433) — cách ngày Lê Lai hy sinh 14 năm — vua Lê Thái Tổ lập di chiếu truyền đời cúng giỗ Lê Lai vào ngày 21 tháng 8 âm lịch.
- **Quarantined Folklore (`report-only` — CẤM đưa vào lời thoại):**
  - Lê Lai có khuôn mặt giống hệt Lê Lợi như hai giọt nước *(dã sử truyền miệng)*.
  - Bầu trời Thanh Hóa đổ mưa máu 3 ngày 3 đêm khi Lê Lai tử tiết *(tương truyền dân gian)*.
  - Dẫn 1.500 kỵ binh sắt phá vây *(sai khác so với 500 quân và 2 voi chiến trong Lam Sơn Thực Lục)*.
  - *Lưu ý sử liệu:* Ưu tiên mốc tháng 4 năm Kỷ Hợi **1419** theo *Đại Việt Sử Ký Toàn Thư* và *Cương Mục* (ghi chú phụ bản *Lam Sơn Thực Lục* có nơi chép 1418).

### 2C. Full 20-Beat 5-Act Production Script (`B00–B19`, Cadence/CTA/Diversity Verified PASS)

| Beat | Hồi | Time | Syl | Delivery Mode | Asset Mode | Banner (`136px`) | Spoken Vietnamese Narration | 35mm Live-Action Visual Anchor (`allowed_text=None`) |
|---|---|---|---:|---|---|---|---|---|
| `B00` | Hồi 1 | `0.0–4.3s` | 15 | `climax_heroic` | `flow_video` | `ĐỔI ÁO CỨU VUA` | Vì sao dân Việt cúng giỗ Lê Lai trước vua Lê Lợi đúng một ngày? | Low-angle 35mm trong lều tre tối sẫm trên núi Chí Linh: ánh đuốc hắt lên tấm áo hoàng bào thêu chỉ vàng giữa khói sương |
| `B01` | Hồi 1 | `4.3–9.1s` | 17 | `narrative_cinema` | `2k_native_kenburns` | — | Nhiều người tưởng hai ông mất liền kề nhau. Sự thật lại cách tới 14 năm. | Atmospheric 35mm điện miếu cổ thời Lê Sơ ngập khói trầm vàng ấm chuyển cắt về rừng núi Chí Linh u ám |
| `B02` | Hồi 1 | `9.1–14.8s` | 19 | `tense_whisper` | `flow_video` | `NÚI CHÍ LINH 1419` | Tháng 4 năm 1419, đại binh nhà Minh siết chặt vòng vây quanh núi Chí Linh. | Wide crane 28mm rừng già Chí Linh mù sương bao quanh bởi biển đuốc đỏ rực nhiều tầng của đại quân Minh dưới chân núi |
| `B03` | Hồi 1 | `14.8–19.4s` | 16 | `tactical_breakdown` | `flow_video` | — | Nghĩa quân Lam Sơn đứt sạch lương muối suốt 10 ngày, chỉ còn vài trăm người. | Medium truck-lateral 50mm chiến binh Lam Sơn áo vải sờn rách, hốc hác quây quanh nồi gỗ trống rỗng giữa mưa lạnh *(post-pause 340ms)* |
| `B04` | Hồi 2 | `19.4–24.3s` | 16 | `tense_whisper` | `2k_native_kenburns` | — | Cố thủ thêm một ngày, toàn bộ cuộc khởi nghĩa sẽ bị xóa sổ vĩnh viễn. | Tight macro push-in 85mm gương mặt trầm tư gầy gò của Bình Định Vương Lê Lợi nhìn xuống biển đuốc quân Minh |
| `B05` | Hồi 2 | `24.3–29.1s` | 17 | `narrative_cinema` | `flow_video` | — | Giữa đêm lạnh, Bình Định Vương Lê Lợi hỏi tướng sĩ ai dám đổi áo thế mạng. | Medium OTS 50mm bên trong lều tre nứa tối sẫm, Lê Lợi đặt tấm hoàng bào trên bàn gỗ thô trước hàng tướng lĩnh lặng im |
| `B06` | Hồi 2 | `29.1–33.8s` | 16 | `tactical_breakdown` | `2k_native_kenburns` | — | Ông nhắc điển tích Kỷ Tín xưa, chịu chết thay chúa để bảo toàn lực lượng. | Tight macro 85mm ngón tay chai sần của Lê Lợi vuốt lên đường chỉ vàng tấm hoàng bào trong ánh đèn dầu chập chờn |
| `B07` | Hồi 2 | `33.8–38.5s` | 17 | `climax_heroic` | `flow_video` | `ÁO BÀO THẾ MẠNG` | Trong lều tre tối sẫm, danh tướng Lê Lai bước ra nhận lệnh không chút do dự. | Low-angle orbit 35mm danh tướng Lê Lai gương mặt góc cạnh, ánh mắt kiên định bước thẳng lên đón lấy tấm hoàng bào *(post-pause 340ms)* |
| `B08` | Hồi 3 | `38.5–43.6s` | 18 | `narrative_cinema` | `2k_native_kenburns` | — | Ông là người thôn Dựng Tú, đứng thứ hai trong 19 hào kiệt Hội thề Lũng Nhai. | Atmospheric 35mm hồi tưởng đêm rừng Lũng Nhai 1416 với 19 hào kiệt đứng nghiêm trang quanh đàn thề sáng lửa đuốc |
| `B09` | Hồi 3 | `43.6–48.5s` | 16 | `tense_whisper` | `flow_video` | — | Lê Lai khoác hoàng bào của chúa, vái lạy trời đất xin thương lấy con cháu. | Medium push-in 50mm Lê Lai khoác hoàng bào vàng trên giáp da sờn, chắp tay cúi đầu trang nghiêm trước bình minh sương mù |
| `B10` | Hồi 3 | `48.5–52.9s` | 15 | `tactical_breakdown` | `flow_video` | — | Vì sao đòn đổi áo này đánh trúng tử huyệt của tổng binh nhà Minh? | Wide OTS 35mm từ trại chỉ huy nhà Minh dưới chân núi: các tướng Minh áo giáp sắt nóng lòng hướng mắt lên đỉnh Chí Linh |
| `B11` | Hồi 3 | `52.9–57.8s` | 17 | `tactical_breakdown` | `2k_native_kenburns` | — | Tướng Minh chỉ khát khao bắt sống một người duy nhất là Lê Lợi để lĩnh thưởng. | Medium close-up 50mm viên tổng binh Minh ánh mắt đầy tham vọng siết chặt chuôi đao nhìn về phía cổng trại trên núi *(post-pause 360ms)* |
| `B12` | Hồi 4 | `57.8–63.2s` | 16 | `tense_whisper` | `flow_video` | — | Bình minh sương dày phủ kín núi. `[pause:550ms]` Cổng trại bỗng mở toang trong tiếng trống thúc. | Tight macro orbit-right 85mm cánh cổng gỗ trại Chí Linh bật tung giữa màn sương đặc *(silence_vacuum tim đập)* |
| `B13` | Hồi 4 | `63.2–67.7s` | 16 | `climax_heroic` | `flow_video` | `500 QUÂN CẢM TỬ` | Lê Lai dẫn 2 voi chiến, cùng 500 quân cảm tử lao xuống chân núi! | Low-angle push-in 28mm Lê Lai khoác áo bào vàng cưỡi voi chiến bọc giáp dẫn 500 nghĩa quân cầm giáo khiên lao xuống dốc bùn |
| `B14` | Hồi 4 | `67.7–72.7s` | 18 | `climax_heroic` | `flow_video` | — | Ông hét vang chúa Lam Sơn ở đây! Toàn bộ cánh quân Minh liền bỏ chốt bâu vào. | Wide crane 28mm các cánh quân Minh khắp chân núi ồ ạt bỏ chốt chặn, đổ xô bủa vây quanh tấm áo bào vàng nổi bật |
| `B15` | Hồi 4 | `72.7–77.3s` | 17 | `urgent_escalation` | `flow_video` | — | Sườn núi phía sau hở toang. Lê Lợi nhờ đó vượt vòng vây giữ trọn ngọn lửa. | Medium truck-lateral 35mm phía sườn rừng sương mù đối diện trống không, Lê Lợi cùng toán cận vệ lặng lẽ thoát ra an toàn *(post-pause 360ms)* |
| `B16` | Hồi 5 | `77.3–82.4s` | 18 | `narrative_cinema` | `flow_video` | — | Lê Lai đánh kiệt sức rồi bị bắt hành hình. Quân Minh tưởng địch chết liền rút binh. | Wide pull-back 28mm sườn núi Chí Linh phủ mây trắng sau cơn ác chiến, các đạo quân Minh thu cờ rút về hướng Đông Quan |
| `B17` | Hồi 5 | `82.4–87.6s` | 18 | `reflective_lesson` | `2k_native_kenburns` | `DI CHIẾU ĐỀN ƠN` | Năm 1428 lên ngôi, Lê Thái Tổ truy phong ông làm đệ nhất công thần. | Heroic 35mm điện Kính Thiên ngập nắng sớm, vua Lê Thái Tổ trang nghiêm cúi đầu trước bài vị Đệ Nhất Công Thần |
| `B18` | Hồi 5 | `87.6–92.6s` | 17 | `reflective_lesson` | `2k_native_kenburns` | — | Trước lúc mất ngày 22 tháng 8, vua lập di chiếu giỗ ông ngày 21. | Tight macro push-in 85mm bàn tay già nua của vua Lê Thái Tổ ấn ngọc tỷ đỏ xuống tờ di chiếu lụa vàng trong khói trầm |
| `B19` | Hồi 5 | `92.6–98.0s` | 20 | `reflective_lesson` | `2k_native_kenburns` | — | Theo bạn, lòng trung nghĩa hay mưu tâm lý cứu Lam Sơn? Chọn và xem tiếp trên Sử Kể Lại. | Symmetrical final-hold 28mm hai nén trầm tỏa khói trước điện thờ cổ kính và dãy núi Chí Linh hùng vĩ dưới trời thu |

### 2D. Flow-Native Thumbnail Prompt (`ĐỔI ÁO CỨU VUA`, Positive Framing, Zero Sprocket Tokens)
```text
Full-frame edge-to-edge vertical historical live-action cinema shot on 35mm anamorphic cinema lens, natural film grain, full-bleed image to all four edges, tragic 1419 Chí Linh mountain dawn historical poster composition. In the upper-middle misty sky band (15% to 33% height), massive bold weathered antique-gold uppercase Vietnamese cinematic title lettering with crisp heavy dark drop-shadow reading exactly "ĐỔI ÁO CỨU VUA", razor-sharp Vietnamese diacritics, centered cleanly against cold slate-indigo mountain fog. In the middle and lower frame (35% to 92%), stern general Lê Lai wearing a mud-spattered golden-embroidered royal battle robe over worn dark leather lamellar armor rides atop a massive armored war elephant charging straight down a foggy steep mountain slope into a sea of glowing enemy torches and iron spears below, lips firmly closed in solemn sacrifice. Rich amber-and-indigo chiaroscuro, unmarked silk pennants, practical live-action historical cinema look.
```

### 2E. Polarizing 2-Choice Pinned Comment (`@SuKeLaiVN`)
> 📌 [GÓC TRANH LUẬN SỬ KỂ LẠI]: Nhiều người tưởng "Hăm mốt Lê Lai, hăm hai Lê Lợi" là hai ông mất cách nhau 1 ngày, nhưng chính sử ghi Lê Lai hy sinh từ năm 1419 — sớm hơn vua Lê Thái Tổ tới 14 năm! Theo bạn, yếu tố nào thực sự cứu sống cuộc khởi nghĩa Lam Sơn tại núi Chí Linh: (1) Lòng trung nghĩa dám đổi mạng không do dự của danh tướng Lê Lai, hay (2) Đòn tâm lý đánh thẳng vào lòng tham lập công của tổng binh nhà Minh khiến giặc tự rút quân? Chọn 1 hoặc 2 bên dưới!

---

## 3. EP09 BLUEPRINT — *3 Vị Hoàng Đế Đại Việt Trực Tiếp Cầm Gươm Xung Trận*

### 3A. Packaging, Benchmarks & Technical Spec
- **Job ID:** `vn_su_ke_lai_ep09_3_hoang_de_cam_guom_xung_tran_short`
- **Viral Pillar:** **Pillar 3 — Xếp Hạng / Đối Chiếu Hoàng Đế & Danh Tướng 1v1** (modeled on `Dòng Máu Việt` `exQOdR_i16A` `761K` views & `a4uUFYSvJIc` `296K` views)
- **YouTube Title (`51` chars `<= 55`):** `3 Vị Hoàng Đế Đại Việt Trực Tiếp Cầm Gươm Xung Trận`
- **Flow-Native Thumbnail Text (`4` uppercase words):** `VUA CẦM GƯƠM CHIẾN`
- **Beat 0 Shock Hook (`15` syl `<= 16`, `0` pause):** *"Ba vị vua Việt Nam nào rời ngai vàng trực tiếp cầm gươm chém giặc?"*
- **Format:** Mode B (`serialized_detail_short`, `20` beats `B00–B19`, `4` chunks × `5` beats, `354` syllables, est. `100.94s`, `12 veo_3_1_lite` Seam Mode + `8 2k_native_kenburns`)

### 3B. Primary Chronicle Citations, Dynastic Accuracy Note & Quarantined `report-only` Claims
- **Ghi chú chặt chẽ về danh hiệu Hoàng Đế (Chronicle Precision Note):**
  - Ba vị vua được chọn đều **chính thức xưng Hoàng Đế** trong chính sử và trực tiếp cầm quân xung trận: **(1) Hoàng đế Lê Đại Hành (Lê Hoàn)**, **(2) Hoàng đế Lê Thái Tổ (Lê Lợi)**, **(3) Hoàng đế Quang Trung (Nguyễn Huệ)**.
  - *(Đối chiếu: Đức Ngô Quyền đại thắng Bạch Đằng năm 938 xưng Vương — Tiền Ngô Vương — chứ chưa xưng Đế theo Đại Việt Sử Ký Toàn Thư, nên giữ đúng 3 vị Hoàng Đế giúp kịch bản chính xác tuyệt đối trước giới sử học và khán giả bình luận).*
- **Verified Primary Sources:**
  1. *Đại Việt Sử Ký Toàn Thư — Bản Kỷ Quyển 1 (Kỷ Nhà Tiền Lê)* & *Khâm Định Việt Sử Thông Giám Cương Mục (Tiền Biên Q.1):* Năm Tân Tỵ (981), quân Tống xâm lược cả thủy lẫn bộ; vua Lê Đại Hành (Lê Hoàn) đích thân cầm quân ra sông Bạch Đằng đóng cọc chặn thuyền giặc, đánh tan thủy binh Tống và chém chết chủ tướng Hầu Nhân Bảo ngay tại trận; năm 982 tiếp tục thân chinh đánh Chiêm Thành bình định biên thùy phía nam.
  2. *Đại Việt Sử Ký Toàn Thư — Bản Kỷ Thực Lục Quyển 10* & *Lam Sơn Thực Lục (Nguyễn Trãi):* Suốt 10 năm khởi nghĩa Lam Sơn (1418–1427), Lê Lợi tự cầm binh trải qua hàng chục trận sinh tử từ núi Chí Linh, Khả Lưu, Trà Lân đến chiến dịch Chi Lăng – Xương Giang năm 1427 (phục kích chém Liễu Thăng tại núi Mã Yên, đè bẹp viện binh Minh), rồi lên ngôi Hoàng đế Lê Thái Tổ khai mở triều Hậu Lê năm 1428.
  3. *Hoàng Lê Nhất Thống Chí — Hồi thứ 14* & *Đại Nam Chính Biên Liệt Truyện (Sơ Tập Q.30):* Cuối năm 1788 (tháng 11 năm Mậu Thân), Nguyễn Huệ lên ngôi Hoàng đế Quang Trung tại núi Bân; chỉ trong 5 ngày Tết Kỷ Dậu (1789) hành quân thần tốc đánh tan hơn 20 vạn quân Thanh; rạng sáng mùng 5 tại Ngọc Hồi đích thân cưỡi voi xông thẳng vào làn đạn, trưa mùng 5 vào Thăng Long trong tấm chiến bào đỏ ám đen khói thuốc súng.
- **Quarantined Folklore (`report-only` — CẤM đưa vào lời thoại):**
  - Truyền thuyết Lê Lợi nhận thanh gươm thần Thuận Thiên do Rùa Vàng trao ở hồ Hoàn Kiếm *(huyền sử dân gian, không dùng thay thế chiến công thực địa chính sử)*.
  - Giai thoại Quang Trung một đao chém đứt đôi thân ngựa chiến của tướng Thanh *(dã sử truyền miệng chưa có trong chính sử)*.

### 3C. Full 20-Beat 5-Act Production Script (`B00–B19`, Cadence/CTA/Diversity Verified PASS)

| Beat | Hồi | Time | Syl | Delivery Mode | Asset Mode | Banner (`136px`) | Spoken Vietnamese Narration | 35mm Live-Action Visual Anchor (`allowed_text=None`) |
|---|---|---|---:|---|---|---|---|---|
| `B00` | Hồi 1 | `0.0–4.3s` | 15 | `climax_heroic` | `flow_video` | `VUA CẦM GƯƠM CHIẾN` | Ba vị vua Việt Nam nào rời ngai vàng trực tiếp cầm gươm chém giặc? | Low-angle push-in 28mm bóng vị Hoàng đế Đại Việt khoác giáp vảy sắt tay nắm chuôi gươm đứng giữa mưa khói chiến trường |
| `B01` | Hồi 1 | `4.3–9.4s` | 18 | `narrative_cinema` | `2k_native_kenburns` | — | Nhiều hoàng đế phương Đông ngồi sau cung cấm. Riêng Đại Việt có những bậc vua chiến tướng. | Atmospheric 35mm ngai vàng gỗ sơn son trầm mặc tương phản bằng cú cắt sang dải cờ chiến tung bay trong gió bão |
| `B02` | Hồi 1 | `9.4–14.3s` | 17 | `tactical_breakdown` | `flow_video` | `1. VUA LÊ ĐẠI HÀNH` | Người đầu tiên mở đầu sử sách chính là Hoàng đế Lê Đại Hành, tức Lê Hoàn. | Low-angle orbit 35mm vua Lê Đại Hành (981) giáp da nâu-sắt thế kỷ 10, ánh mắt sắc lạnh trên mũi chiến thuyền gỗ sông Bạch Đằng |
| `B03` | Hồi 1 | `14.3–19.9s` | 19 | `tense_whisper` | `flow_video` | — | Năm 981, đại quân nhà Tống tràn sang cả thủy lẫn bộ hòng nuốt trọn đất Việt. | Wide crane 28mm hạm đội chiến thuyền buồm sẫm nhà Tống rợp mặt sông biên ải phủ sương mù xám lạnh *(post-pause 340ms)* |
| `B04` | Hồi 2 | `19.9–24.6s` | 17 | `climax_heroic` | `flow_video` | — | Không ngồi chờ ở Hoa Lư, vua Lê Hoàn đích thân cầm quân ra sông Bạch Đằng. | Medium truck-lateral 35mm vua Lê Hoàn vung kiếm chỉ thẳng ra cửa sông Bạch Đằng sóng đục giữa hàng trăm chiến thuyền nhẹ Đại Việt |
| `B05` | Hồi 2 | `24.6–29.3s` | 17 | `urgent_escalation` | `flow_video` | — | Ông đóng cọc chặn thuyền giặc. Thủy binh Tống vỡ nát, tướng Hầu Nhân Bảo bỏ mạng. | Tight action push-in 50mm chiến thuyền Tống đâm vỡ toác vào bãi cọc gỗ lim nhọn giữa làn nước đục cuộn sóng và khói lửa |
| `B06` | Hồi 2 | `29.3–34.4s` | 18 | `narrative_cinema` | `2k_native_kenburns` | — | Một năm sau, vị hoàng đế sắt thép ấy lại thân chinh bình định biên thùy phía nam. | Wide landscape 35mm đoàn chiến thuyền và bộ binh Tiền Lê hành quân dọc bờ biển miền Trung dưới trời bình minh rực đỏ |
| `B07` | Hồi 2 | `34.4–39.0s` | 16 | `tactical_breakdown` | `flow_video` | `2. VUA LÊ THÁI TỔ` | Vị hoàng đế thứ hai bước ra từ núi rừng Thanh Hóa: vua Lê Thái Tổ. | Low-angle orbit-right 35mm Lê Lợi mặc áo giáp da sờn bùn đất, gương mặt phong sương đứng trên đỉnh núi rừng Lam Sơn *(post-pause 340ms)* |
| `B08` | Hồi 3 | `39.0–44.1s` | 18 | `narrative_cinema` | `2k_native_kenburns` | — | Suốt 10 năm khởi nghĩa Lam Sơn, Lê Lợi tự cầm binh qua hàng chục trận sinh tử. | Wide 28mm nghĩa quân Lam Sơn hành quân xuyên mưa rừng già Thanh Hóa, giáo mác ánh thép lấp ló trong sương |
| `B09` | Hồi 3 | `44.1–49.5s` | 19 | `tactical_breakdown` | `flow_video` | — | Từ những ngày đói cơm trên núi Chí Linh, ông trực tiếp chỉ huy đánh Khả Lưu, Trà Lân. | Medium OTS 50mm Lê Lợi đứng sát bờ sông mưa lạnh quan sát chiến lũy giặc Minh, bàn tay chai sần đặt trên chuôi gươm |
| `B10` | Hồi 3 | `49.5–54.5s` | 18 | `climax_heroic` | `flow_video` | — | Năm 1427, quân Lam Sơn phục kích Chi Lăng. Tướng Liễu Thăng bị chém gục. | Dynamic push-in 28mm hẻm núi đá vôi Chi Lăng mịt khói tên bay, kỵ binh Minh sa lầy bùn sâu trước đòn phục kích hai bên vách đá |
| `B11` | Hồi 3 | `54.5–60.2s` | 20 | `reflective_lesson` | `2k_native_kenburns` | — | Rút gươm từ đất lửa, ông bước lên ngai vàng khai mở triều Hậu Lê năm 1428. | Low-angle 35mm vua Lê Thái Tổ trong long bào trang nghiêm bước qua bậc đá cổ kinh thành Thăng Long rực nắng *(post-pause 360ms)* |
| `B12` | Hồi 4 | `60.2–65.6s` | 16 | `tense_whisper` | `flow_video` | — | Nhưng đỉnh cao của tốc độ và uy lực gọi tên vị hoàng đế thứ ba. `[pause:550ms]` | Tight macro orbit-left 85mm ánh mắt rực lửa dưới khăn chiến đỏ-vàng trong đêm đông trước giờ xuất quân *(silence_vacuum tim đập)* |
| `B13` | Hồi 4 | `65.6–70.6s` | 18 | `climax_heroic` | `flow_video` | `3. VUA QUANG TRUNG` | Cuối năm 1788, Nguyễn Huệ lên ngôi Hoàng đế Quang Trung ngay tại núi Bân. | Wide low-angle 28mm đàn tế núi Bân rực sáng hàng nghìn ngọn đuốc đêm đông, Hoàng đế Quang Trung đứng hiên ngang giữa ba quân |
| `B14` | Hồi 4 | `70.6–75.9s` | 20 | `urgent_escalation` | `flow_video` | — | Chỉ trong 5 ngày Tết 1789, ông thần tốc đánh tan hơn 20 vạn quân Thanh. | Wide truck-lateral 28mm đại quân Tây Sơn và voi chiến băng đêm băng sương tiến như vũ bão về phía bắc dưới cờ đỏ |
| `B15` | Hồi 4 | `75.9–80.9s` | 18 | `climax_heroic` | `flow_video` | — | Rạng sáng mùng 5 tại Ngọc Hồi, nhà vua đích thân cưỡi voi xông thẳng vào làn đạn! | Explosive push-in 28mm Hoàng đế Quang Trung trên lưng voi chiến lao qua làn khói đạn đại bác và tia lửa rực sáng Ngọc Hồi *(post-pause 360ms)* |
| `B16` | Hồi 5 | `80.9–86.0s` | 18 | `narrative_cinema` | `2k_native_kenburns` | — | Trưa hôm đó vào Thăng Long, tấm chiến bào đỏ của vua đã ám đen khói thuốc súng. | Tight portrait 50mm chiến bào đỏ sạm đen tro khói súng của vua Quang Trung giữa ánh nắng trưa mùng 5 Tết tại Thăng Long |
| `B17` | Hồi 5 | `86.0–90.8s` | 16 | `reflective_lesson` | `2k_native_kenburns` | `KHÍ PHÁCH ĐẠI VIỆT` | Cả 3 vị vua đều đứng tuyến đầu. Chính khí phách ấy át vía kẻ thù. | Atmospheric 35mm ba hình bóng tượng trưng: mũi thuyền Bạch Đằng, vách đá Chi Lăng và voi chiến Ngọc Hồi nối tiếp trong ánh sáng hào hùng |
| `B18` | Hồi 5 | `90.8–95.5s` | 16 | `reflective_lesson` | `2k_native_kenburns` | — | Ngọn lửa thân chinh của họ đã giữ vững giang sơn Đại Việt suốt ngàn năm. | Wide crane-up 28mm dòng sông Hồng cuộn sóng và dãy núi trùng điệp Đại Việt rực rỡ dưới ánh bình minh vàng |
| `B19` | Hồi 5 | `95.5–100.9s` | 20 | `reflective_lesson` | `2k_native_kenburns` | — | Trong 3 vị vua này, ai uy dũng nhất theo bạn? Bình luận và xem tiếp trên Sử Kể Lại. | Symmetrical final-hold 28mm thanh bảo kiếm cắm vững trên bệ đá cổ trước chân trời rạng đông và cờ chiến tung bay |

### 3D. Flow-Native Thumbnail Prompt (`VUA CẦM GƯƠM CHIẾN`, Positive Framing, Zero Sprocket Tokens)
```text
Full-frame edge-to-edge vertical historical live-action cinema shot on 35mm anamorphic cinema lens, natural film grain, full-bleed image to all four edges, monumental Vietnamese dynasty warrior-emperor theatrical poster composition. In the upper-middle smoky sky band (15% to 33% height), massive bold weathered antique-gold uppercase Vietnamese cinematic title lettering with crisp heavy dark drop-shadow reading exactly "VUA CẦM GƯƠM CHIẾN", razor-sharp Vietnamese diacritics, centered cleanly against dramatic storm-indigo and ember battle clouds. In the middle and lower frame (35% to 92%), a commanding Vietnamese warrior-emperor clad in blackened-iron lamellar cuirass beneath a billowing soot-streaked crimson silk battle robe grips a gleaming battle-worn steel saber aloft atop an armored war elephant surging forward through dawn cannon smoke and glowing sparks, with unmarked crimson banners snapping sharply behind him. Intense amber-and-indigo chiaroscuro, practical live-action historical cinema look.
```

### 3E. Polarizing Debate Pinned Comment (`@SuKeLaiVN`)
> 📌 [BÌNH CHỌN HOÀNG ĐẾ CHIẾN TƯỚNG ĐẠI VIỆT — SỬ KỂ LẠI]: Cả 3 vị Hoàng đế đều rời ngai vàng đích thân xông pha tuyến lửa: (1) Vua Lê Đại Hành (981) chém tướng Tống Hầu Nhân Bảo trên sông Bạch Đằng, (2) Vua Lê Thái Tổ (1418–1427) 10 năm nằm gai nếm mật đánh tan quân Minh, và (3) Vua Quang Trung (1789) cưỡi voi xông thẳng vào làn đạn Ngọc Hồi đến mức chiến bào đỏ ám đen khói súng! Theo bạn, vị Hoàng đế nào uy dũng nhất lịch sử nước nhà — chọn số 1, 2 hay 3 và chia sẻ lý do bên dưới!
