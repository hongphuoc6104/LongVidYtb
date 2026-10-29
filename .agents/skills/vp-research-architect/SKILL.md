---
name: vp-research-architect
description: "Architect research-backed conversational narratives, 3-tier academic funnel packaging, and full_frame_v1 pipeline blueprints."
---

# VP Research Architect — Research, Packaging & Full-Frame Narrative Architecture Skill

`vp-research-architect` là bộ kỹ năng thượng nguồn (upstream creative & technical engine) chịu trách nhiệm nghiên cứu đề tài, khai thác cứ liệu học thuật chuẩn quốc tế (Q1), đóng gói CTR (Title/Thumbnail/SEO) và kiến trúc bộ hồ sơ kỹ thuật hoàn chỉnh (`brief.json` và `content.json` chuẩn Schema 3.0, `visual_pacing_profile: "full_frame_v1"`) cho băng chuyền Video Pilot (`long_16x9` và `short_9x16` Spin-offs).

Bộ kỹ năng này được thiết kế để **tự động hóa 100% phần tính toán kỹ thuật bằng code Python**, giúp Agent thực thi (kể cả dòng model nhẹ như Gemini Flash) không bao giờ phải đoán tọa độ `(x, y)` hay tính toán offset thủ công.

---

## 1. Định Vị Ngách & Phễu 3 Tầng (Core Mission & 3-Tier Pillar Lock)

- **Đa pillar (`sys/pillars.py`):** Mỗi job chọn `channel_pillar` (`cognition` mặc định hoặc `research_guide`). Pillar `research_guide` ("Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới"): đa ngành; T1 sai lầm/ngộ nhận người mới, T2 bản chất từng bước (câu hỏi → tổng quan → thiết kế → dữ liệu → viết → nộp/phản biện), T3 công cụ (Zotero, Scholar, SPSS/R, LaTeX, chọn tạp chí). Hook kiểu tutorial (vấn đề thực tế + lời hứa kết quả), không bắt buộc nghịch lý/cảnh VN 60s; T3 long 10–15 phút (≥ 2700 âm tiết, ≥ 24 cảnh). Nếu video T3 có cảnh `shot_type: screen_capture` thì PHẢI hỏi người dùng `screen_capture_source` (`user_recorded`/`cdp_auto`) trước khi chạy tiếp; không có cảnh đó thì không hỏi.
- **Pillar `cognition` (mặc định):** Khóa vào ngách **"Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"** (kết hợp Tâm lý học Nhận thức, Mô hình Tư duy & Triết học Tri thức).
- **Quy tắc Chống Loãng Tệp (`Anti-Dilution Guard`):** Tuyệt đối **cấm** các mẹo vặt văn phòng hời hợt (gõ hàm Excel, làm Slide nhanh 4 tiếng, mẹo học vẹt ngắn hạn).
- **Mô hình Phễu 3 Tầng Linh Hoạt (`funnel_tier`):**
  1. **Tầng 1 — Phễu Rộng (`tier_1_broad`):** *"Tư Duy Nhận Thức, Nghịch Lý & Ảo Giác Tri Thức"* (Cognitive Biases, Mental Models, cơ chế nhận thức khi tiếp nhận và xử lý thông tin, khoảng cách giữa nhận biết hời hợt và thấu suốt bản chất).
  2. **Tầng 2 — Phễu Giữa (`tier_2_mid`):** *"Phương Pháp Luận, Phân Tích Căn Nguyên & Bản Chất Vấn Đề"* (Methodological Inquiry, First-Principles Thinking, giải phẫu cấu trúc nhân quả, cơ chế vận hành gốc rễ và kiểm chứng thực nghiệm).
  3. **Tầng 3 — Phễu Chuyển Đổi (`tier_3_conversion`):** *"Công Cụ & Khung Tư Duy Đào Sâu Tri Thức"* (Deep Intellectual Frameworks, mô hình phân tích hệ thống, ứng dụng công nghệ/AI để phản biện chéo và kết nối tri thức đa chiều).
- **Nguyên Tắc Đề Tài Mở (No Rigid Sample Overfitting):** Tập trung vào nguyên lý cốt lõi, cơ chế nhân quả và chiều sâu nhận thức; không ép buộc chủ đề mẫu cố định và không định nghĩa vấn đề quá hẹp hay gượng ép.
- **Thời Lượng Động (Dynamic Duration SSOT):** Thời lượng video và số phân cảnh hoàn toàn động theo chiều sâu kịch bản và độ dài audio thực tế từ WAV, loại bỏ các con số cứng cố định.

---

## 2. Quy Trình Kiến Trúc Tối Giản Cho Agent Flash (`full_frame_v1`)

### Bước 1: Khai Thác Dữ Kiện Văn Nói, 1 Nghịch Lý Cốt Lõi & Việt Hóa 60 Giây Đầu
- **1 Nghịch Lý Cốt Lõi / Video (Cấm Frankenstein Bloat & Cấm Nhân Bản Đề Tài):** Mỗi video chỉ mổ xẻ sâu **1 nghịch lý duy nhất** kèm **1 thí nghiệm tâm điểm có cốt truyện** (ai làm gì, thiết lập đối chứng ra sao, cú lật kết quả bất ngờ thế nào). Tuyệt đối không nhồi nhét giáo trình đại cương nhiều chương rời rạc và không lặp lại đề tài/hook đã sản xuất trong `sys/exports/`.
- Mọi dữ kiện trong `sources[].facts` và `required_points` phải là câu văn nói tự nhiên $\le 20$ âm tiết (ngưỡng cứng $22$), không chứa `DOI`, `ISBN`, `et al.`, `%`, `/` (`check_conversational_spoken_facts()`).
- **Việt hóa 60 giây đầu:** Mở màn bằng bối cảnh sát sườn với người xem tại Việt Nam. Chi tiết: [Fact Mining Guide](references/fact-mining-guide.md).

### Bước 1.5: Trạm Khơi Gợi Động & Đồng Sáng Tạo Góc Nhìn Con Người (`Human Editorial Co-Creation` — Chống AI-Slop)
- **Bóc tách Vùng Xám đề tài (`topic_dilemmas`):** Ngay sau khi có đề tài, Agent phân tích đặc thù riêng của chủ đề (mâu thuẫn giữa lý thuyết và thực tế, các góc khuất tranh cãi hai chiều).
- **Sinh Bộ Câu Hỏi Động (`dynamic_questions` — Zero Hardcoded Questions):** Tuyệt đối **cấm dùng bộ câu hỏi cố định rập khuôn**. Agent phải tự sinh các câu hỏi hoàn toàn mới bám sát vùng xám của đề tài để khơi gợi 3 tầng chất liệu con người từ tác giả:
  1. **Phân tích (*Human Analysis*):** Nguyên nhân thực tế hoặc cơ chế ngầm đằng sau hiện tượng theo quan sát của tác giả.
  2. **Bình luận (*Human Commentary*):** Phản biện cá nhân trước các luồng quan điểm trái chiều xoay quanh đề tài.
  3. **Đánh giá (*Human Evaluation / Judgment*):** Trọng số giá trị thực tế (điều gì bị thổi phồng, điều gì mới là cốt lõi, giới hạn đúng/sai trong đời thực).
- **Phát triển Ý tưởng Chi tiết cho Video (`expanded_content_ideas`):** Từ chia sẻ/ý kiến của tác giả (`author_raw_input`), Agent phát triển rộng và sâu hơn thành các ý tưởng chi tiết phục vụ trực tiếp cho kịch bản video hiện tại (luận điểm phân tích sâu, tình huống/ví dụ đời thực tương đồng, đánh giá đa chiều về điều kiện biên) và đóng gói vào trường `human_editorial` trong `brief.json`.

### Bước 2: Đóng Gói CTR (`Packaging & SEO Contract` — Chống Thumbnail Kiểu Dán Đè AI)
- Tách biệt `topic` nội bộ khỏi bộ trường `packaging`:
  1. `youtube_title`: $\le 55$ ký tự, tạo *Curiosity Gap*, không tự trả lời trong tiêu đề.
  2. `thumbnail_spec`:
     - `visual_hook` + `text_overlay` đúng **2–4 từ in hoa** đánh trúng nghịch lý tâm lý.
     - **Integrated Poster Thumbnail Prompt (`thumbnail_prompt` / `build_thumbnail_poster_prompt()`):** Tuyệt đối không dùng lại ảnh `SC01` rồi dán đè một chiếc thẻ HTML rẻ tiền, và nghiêm cấm các sáo rỗng AI (`neon brain`, `matrix 0101`, `cyborg hand`). Thumbnail phải được thiết kế như **1 poster thống nhất**: **60% khung hình** là **1 ẩn dụ thị giác duy nhất** cực kỳ sắc nét; **40% khung hình** là khoảng trống sạch (*negative space*) nơi **dòng chữ vàng đậm cỡ đại (`#FACC15`) viền đen dày** được vẽ/thiết kế hòa quyện cùng một tone màu và ánh sáng với bức tranh.
  3. `channel_pillar` & `funnel_tier`: Theo pillar đã chọn trong `sys/pillars.py` (`tier_1_broad` / `tier_2_mid` / `tier_3_conversion`).

### Bước 3: Kiến Trúc Mạch Truyện 8 Phần Ngầm & Cặp `(Nhịp Thoại, Hành Động Hình Ảnh)`
- **Cấu trúc Kịch bản 8 Phần Ngầm (`NARRATIVE_ARC_8_STAGES`):** Mọi video giải thích cần dẫn dắt người xem đi qua 8 chặng nhận thức rõ ràng (nhưng chuyển ý tự nhiên, tuyệt đối không hô khẩu hiệu *"Phần 1 là..."*):
  1. `hook` (**Mở bài**): Cú tát sự thật $\le 18$ âm tiết + tình huống đời thực sát sườn.
  2. `lead_in` (**Phần dẫn**): Neo cảm xúc và bối cảnh khiến người xem thấy chính mình trong đó.
  3. `problem` (**Phần vấn đề**): Lật tẩy mâu thuẫn nhận thức — vì sao cách hiểu thông thường lại sai hoặc thất bại.
  4. `causal_mechanism` (**Phần nhân quả**): Giải phẫu cơ chế gốc rễ (`A dẫn đến B vì quy luật C`).
  5. `explanation` (**Phần giải thích**): Mô hình hóa trực quan bằng sơ đồ nhân quả hoặc thí nghiệm đối chứng.
  6. `counter_argument` (**Phần phản biện**): Lật ngược giả định, chỉ ra giới hạn hoặc bẫy ngụy biện để tăng chiều sâu trí tuệ.
  7. `takeaway` (**Phần nội dung rút ra**): Đúc kết nguyên lý/khung tư duy sắc bén có thể áp dụng ngay.
  8. `closing` (**Phần kết bài**): Khép vòng lặp với cảnh mở đầu và để lại dư âm sâu sắc.
- Thay vì tự tính thời lượng, tự cắt `anchor_quote` hoặc tự đoán tọa độ `focus: {x, y}`, hãy sử dụng hàm **`build_scenes_from_story_rows()`** trong `sys/content/research_story_architect.py` (hoặc cấu trúc `STORY` trong `sys/tools/build_full_frame_acceptance.py`):
  - Mỗi dòng là một cặp `(câu_hoặc_mệnh_đề_thoại_tiếng_Việt, "shot_type|mô_tả_hình_ảnh_toàn_khung")`. Với câu dài $> 14$ chữ có bước ngoặt ý, dùng `split_long_sentence_into_beat_clauses()` để tách thành 2 nhịp hình tự nhiên.
  - Chọn `shot_type` trong các loại chuẩn: `full_scene`, `variation`, `macro_prop`, `visual_diagram`, `concept_metaphor`, `cutaway_detail`, `white_card`, `white_isolated`, `still_life`, và `environment`.
  - **Trần tối đa 2 nhịp `variation` (`based_on`) liên tiếp (`MAX_CONSECUTIVE_VARIATION_BEATS = 2`):** Sau tối đa 2 nhịp `variation` giữ nguyên phòng, bắt buộc cắt sang góc máy mới (`macro_prop`, `visual_diagram`, `cutaway_detail`, hoặc `full_scene` góc mới) để tránh đứng hình nhàm chán và tránh lỗi biến dạng nét vẽ AI.
  - **Quy chuẩn Bối cảnh (Setting Brevity):** Chuỗi `setting` bắt buộc $\le 8$ từ, chỉ mô tả không gian vật lý và điều kiện ánh sáng (ví dụ: `"A student desk under green lamp light."`), tuyệt đối không liệt kê đồ vật, đạo cụ, bàn ghế trong `setting`.
  - **Khoảng thở Thị giác (Visual Breathing Room):** Để chống mệt mỏi nhận thức, trong mỗi cửa sổ 10 nhịp hình trượt (10-beat sliding window), bắt buộc có ít nhất 3 nhịp hình không có nhân vật ($\ge 30\%$ rest frames: `still_life`, `environment`, hoặc `white_card` thuần biểu tượng), và không bao giờ xuất hiện quá 4 nhịp nhân vật liên tiếp.
  - Code Python trong `build_content_v3()` sẽ **tự động**:
    - Ghép câu, tính thời lượng chuẩn và trích xuất `anchor_quote` chính xác 100%.
    - Khớp câu `coverage[].quote` với `required_points` theo độ chồng lấp từ vựng cao nhất (`_select_best_coverage_quote()`) thay vì lấy mù quáng câu đầu tiên.
    - Nối `based_on` + `Expression lock` qua `apply_room_continuity()` (tự động ngắt chuỗi ở nhịp thứ 3 để không vượt quá 2 `variation` liên tiếp).
    - Chọn chuyển động camera có chủ đích theo từng chặng và loại khung hình qua `select_semantic_camera_effect()` (`hold` cho sơ đồ/`white_card`, `punch_in` cho cú lật/hook, `pan_right` cho chuỗi nhân quả, `zoom_out` cho đúc kết; không bao giờ xoay vòng máy móc `% 4`).
    - Khóa tâm `focus` trong vùng an toàn trung tâm (`0.35..0.65`), gắn `narrative_phase` theo 8 chặng (`infer_editorial_section()`) và điều biến giọng `tone` động qua `_infer_scene_tone()`.
    - Kiểm định tự động `diversity_report` (`lint_script`) trong `write_production_package()`.
- Chi tiết: [Conversational Structuring](references/conversational-structuring.md) và [Pipeline Blueprint Spec](references/pipeline-blueprint-spec.md).

---

## 3. Công Cụ Hỗ Trợ Tự Động Hóa

```bash
# Tạo bộ blueprint mẫu (kèm kiểm định Packaging, Việt hóa 60s đầu & Cadence)
python3 sys/content/research_story_architect.py --demo

# Tạo blueprint ngách Tư Duy Nghiên Cứu Q1 kèm các kịch bản Spin-off Short 9:16 độc lập
python3 sys/content/research_story_architect.py --topic academic-paradox-q1 --spinoff-shorts

# Tạo gói full_frame_v1 chuẩn 19 cảnh (5-8 phút)
python3 sys/tools/build_full_frame_acceptance.py --output-dir sys/runs/full-frame-job
```

## Full-frame visual journey gate

For new jobs, declare `visual_pacing_profile: full_frame_v1` and follow [Full-frame quality contracts](../vp-full-frame-quality/SKILL.md). Plan across the 4 functional cognitive phases (`lived_friction` → `empirical_conflict` → `structural_model` → `actionable_resolution`). Keep setting descriptions concise at $\le 8$ words (space + lighting only). Maintain visual breathing room: at least 30% of beats in every 10-beat window must be character-free rest frames (`still_life`, `environment`), and never exceed 4 consecutive character beats. Use at most two consecutive scenes per physical setting; for ten or more scenes, keep each setting at or below 30%. Author source-backed comparisons without inventing numeric results. Preserve room and expression through `based_on` return shots (or set `allow_expression_shift: true` for intentional emotional turns); distinguish hard cuts from in-frame camera movement.

## Hand-drawn 2D explainer image authoring (`1.7.0`)

Use prompt registry `1.7.0` (`handdrawn_2d_explainer`) and the [visual style contract](../vp-production/references/visual-style.md) for new packages. Registry `1.7.0` enforces bold clean black outer contours, flat solid color fills (`terracotta`, `warm sand`, `ochre`, `sage green`, `slate blue`), pure `#FFFFFF` white fields for isolated objects/comparisons/diagrams, and flat solid backgrounds for contextual scenes. Import `STYLE_DESCRIPTION`, `CAST_APPEARANCE` and `DEFAULT_OUTFIT` from `visual_style`. Only include people when explicitly needed (`has_character: true`) using simple contextual 2D cartoon designs (no fixed round white head or white mittens), and never render white-on-black YouTube subtitle boxes or browser controls.
