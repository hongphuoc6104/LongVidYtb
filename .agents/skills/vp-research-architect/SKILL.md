---
name: vp-research-architect
description: "Architect research-backed conversational narratives, 3-tier academic funnel packaging, and full_frame_v1 pipeline blueprints."
---

# VP Research Architect — Research, Packaging & Full-Frame Narrative Architecture Skill

`vp-research-architect` là bộ kỹ năng thượng nguồn (upstream creative & technical engine) chịu trách nhiệm nghiên cứu đề tài, khai thác cứ liệu học thuật chuẩn quốc tế (Q1), đóng gói CTR (Title/Thumbnail/SEO) và kiến trúc bộ hồ sơ kỹ thuật hoàn chỉnh (`brief.json` và `content.json` chuẩn Schema 3.0, `visual_pacing_profile: "full_frame_v1"`) cho băng chuyền Video Pilot (`long_16x9` và `short_9x16` Spin-offs).

Bộ kỹ năng này được thiết kế để **tự động hóa 100% phần tính toán kỹ thuật bằng code Python**, giúp Agent thực thi (kể cả dòng model nhẹ như Gemini Flash) không bao giờ phải đoán tọa độ `(x, y)` hay tính toán offset thủ công.

---

## 1. Định Vị Ngách & Phễu 3 Tầng Triết Lý Nội Dung (`ContentPhilosophy`)

- **Triết lý nội dung (`ContentPhilosophy` trong `sys/pillars.py`):** Mỗi job chọn `channel_philosophy` (hoặc `channel_pillar` tương thích ngược):
  - `cognition` (mặc định): Khóa vào ngách **"Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"** (kết hợp Tâm lý học Nhận thức, Mô hình Tư duy & Triết học Tri thức). Đơn giản hóa các ý niệm phức tạp theo tinh thần Feynman.
  - `research_guide`: **"Hướng Dẫn Nghiên Cứu Khoa Học Cho Người Mới"**: đa ngành; T1 sai lầm/ngộ nhận người mới, T2 bản chất từng bước (câu hỏi → tổng quan → thiết kế → dữ liệu → viết → nộp/phản biện), T3 công cụ (Zotero, Scholar, SPSS/R, LaTeX, chọn tạp chí). Hook kiểu tutorial (vấn đề thực tế + lời hứa kết quả rõ ràng). Nếu video T3 có cảnh `shot_type: screen_capture` thì PHẢI hỏi người dùng `screen_capture_source` (`user_recorded`/`cdp_auto`) trước khi chạy tiếp; không có cảnh đó thì không hỏi.
- **Quy tắc Chống Loãng Tệp (`Anti-Dilution Guard`):** Tuyệt đối **cấm** các mẹo vặt văn phòng hời hợt (gõ hàm Excel, làm Slide nhanh 4 tiếng, mẹo học vẹt ngắn hạn).
- **Mô hình Phễu 3 Tầng Linh Hoạt (`funnel_tier`):**
  1. **Tầng 1 — Phễu Rộng (`tier_1_broad`):** *"Tư Duy Nhận Thức, Hiện Tượng & Ảo Giác Tri Thức"* (Cognitive Biases, Mental Models, cơ chế nhận thức khi tiếp nhận và xử lý thông tin, khoảng cách giữa nhận biết hời hợt và thấu suốt bản chất).
  2. **Tầng 2 — Phễu Giữa (`tier_2_mid`):** *"Phương Pháp Luận, Phân Tích Căn Nguyên & Bản Chất Vấn Đề"* (Methodological Inquiry, First-Principles Thinking, giải phẫu cấu trúc nhân quả, cơ chế vận hành gốc rễ và kiểm chứng thực nghiệm).
  3. **Tầng 3 — Phễu Chuyển Đổi (`tier_3_conversion`):** *"Công Cụ & Khung Tư Duy Đào Sâu Tri Thức"* (Deep Intellectual Frameworks, mô hình phân tích hệ thống, ứng dụng công nghệ/AI để phản biện chéo và kết nối tri thức đa chiều).
- **Nguyên Tắc Đề Tài Mở (No Rigid Sample Overfitting):** Tập trung vào nguyên lý cốt lõi, cơ chế nhân quả và chiều sâu nhận thức; không ép buộc chủ đề mẫu cố định và không định nghĩa vấn đề quá hẹp hay gượng ép.
- **Thời Lượng Động & Ước Lượng Chiều Sâu (`content_depth_estimate` SSOT):** Thời lượng video và số phân cảnh hoàn toàn động theo ước lượng chiều sâu nội dung (`content_depth_estimate` trong `sys/pillars.py`) và độ dài audio thực tế từ WAV, loại bỏ các con số cứng cố định. Hàm `content_depth_estimate()` căn cứ vào số lượng luận điểm (`required_points`), tầng phễu (`funnel_tier`), và định dạng (`long_16x9` hay `short_9x16`) để đề xuất dải phân cảnh và thời lượng tối ưu.

---

## 2. Quy Trình Kiến Trúc Tối Giản Cho Agent Flash (`full_frame_v1`)

### Bước 1: Khai Thác Cứ Liệu Văn Nói & Định Hình Góc Tiếp Cận Trọng Tâm
- **Định Hình Góc Tiếp Cận Trọng Tâm (Feynman Focus):** Mỗi video tập trung mổ xẻ sâu **1 vấn đề nhận thức hoặc bài toán thực tế then chốt** kèm **cứ liệu minh họa cụ thể** (bối cảnh, cơ chế vận hành, kết quả thực nghiệm). Tránh dàn trải giáo trình đại cương nhiều chương rời rạc và không lặp lại đề tài/hook đã sản xuất trong `sys/exports/`.
- Mọi dữ kiện trong `sources[].facts` và `required_points` được diễn đạt bằng câu văn nói tự nhiên, rõ ràng, không chứa ký tự kỹ thuật khô khan (`DOI`, `ISBN`, `et al.`, `%`, `/`).
- **Mở đầu gắn kết thực tế:** Mở màn bằng tình huống hoặc bối cảnh đời thực quen thuộc giúp người xem kết nối ngay với câu chuyện. Chi tiết: [Fact Mining Guide](references/fact-mining-guide.md).

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
     - `visual_hook` + `text_overlay` đúng **2–4 từ in hoa** đánh trúng tâm lý tò mò.
     - **Integrated Poster Thumbnail Prompt (`thumbnail_prompt` / `build_thumbnail_poster_prompt()`):** 100% tạo thumbnail trực tiếp từ Flow CDP (prompt chuyên biệt). Tuyệt đối không dùng lại ảnh `SC01` rồi dán đè thẻ chữ HTML hay gradient đen che khuất tranh. Nghiêm cấm các sáo rỗng AI (`neon brain`, `matrix 0101`, `cyborg hand`). Thumbnail phải được thiết kế như **1 poster thống nhất**: **60% khung hình** là **1 ẩn dụ thị giác duy nhất** cực kỳ sắc nét; **40% khung hình** là khoảng trống sạch (*negative space*) nơi **chữ vẽ tay cỡ đại (`allowed_text`)** được AI tạo trực tiếp hòa quyện cùng nét vẽ và màu nền phẳng (`#F8F0DC` / `#FFFFFF`).
  3. `channel_philosophy` & `funnel_tier`: Theo triết lý đã chọn trong `sys/pillars.py` (`tier_1_broad` / `tier_2_mid` / `tier_3_conversion`).

### Bước 3: Kiến Trúc Mạch Truyện Thích Ứng & Cặp `(Nhịp Thoại, Hành Động Hình Ảnh)`
- **Mạch Truyện Thích Ứng (Adaptive Narrative Structuring):** Thay vì gò ép vào khung 8 chặng cố định, cấu trúc kịch bản phân bổ động qua hàm `infer_editorial_section()` dựa trên tiến trình nhận thức tự nhiên:
  - Khởi đầu (`hook` / `lead_in`): Tạo sự tò mò và gắn kết đời thực.
  - Khám phá (`problem` / `causal_mechanism`): Bóc tách mâu thuẫn và cơ chế nhân quả gốc rễ theo phương pháp Feynman.
  - Sâu sắc (`explanation` / `counter_argument`): Trực quan hóa mô hình và xem xét đa chiều.
  - Đúc kết (`takeaway` / `closing`): Khái quát hóa hành động thực tiễn và khép vòng lặp nhận thức.
- Sử dụng hàm **`build_scenes_from_story_rows()`** trong `sys/content/research_story_architect.py`:
  - Mỗi dòng là một cặp `(câu_hoặc_mệnh_đề_thoại_tiếng_Việt, "shot_type|mô_tả_hình_ảnh_toàn_khung")`. Với câu dài có bước ngoặt ý, dùng `split_long_sentence_into_beat_clauses()` để tách thành 2 nhịp hình tự nhiên.
  - Chọn `shot_type` trong các loại chuẩn: `full_scene`, `variation`, `macro_prop`, `visual_diagram`, `concept_metaphor`, `cutaway_detail`, `white_card`, `white_isolated`, `still_life`, và `environment`.
  - **Công Thức Thị Giác Feynman:** 1 nhân vật + 1 ẩn dụ trọng tâm trên nền phẳng sạch sẽ (`#FFFFFF`/`#F8F0DC`), các khung hình domino phát triển tuần tự từng chi tiết mà không gây rườm rà hay phân tán thị giác.
  - **Mô tả bối cảnh gọn gàng:** Mô tả không gian 2D tối giản và ánh sáng/màu nền, tập trung vào hành động và ý niệm biểu đạt.
  - Code Python trong `build_content_v3()` sẽ **tự động**:
    - Ghép câu, tính thời lượng chuẩn và trích xuất `anchor_quote` chính xác 100%.
    - Khớp câu `coverage[].quote` với `required_points` theo độ chồng lấp từ vựng cao nhất (`_select_best_coverage_quote()`).
    - Nối `based_on` + `Expression lock` qua `apply_room_continuity()`.
    - Chọn chuyển động camera có chủ đích qua `select_semantic_camera_effect()` (`hold` cho sơ đồ/`white_card`, `punch_in` cho cú lật/hook, `pan_right` cho chuỗi nhân quả, `zoom_out` cho đúc kết).
    - Khóa tâm `focus` trong vùng an toàn trung tâm (`0.35..0.65`), gắn `narrative_phase` và điều biến giọng `tone` động qua `_infer_scene_tone()`.
    - Kiểm định tự động `diversity_report` (`lint_script`) trong `write_production_package()`.
- Chi tiết: [Conversational Structuring](references/conversational-structuring.md) và [Pipeline Blueprint Spec](references/pipeline-blueprint-spec.md).

---

## 3. Công Cụ Hỗ Trợ Tự Động Hóa

```bash
# Tạo bộ blueprint mẫu (kèm kiểm định Packaging, định hình góc tiếp cận & Cadence)
python3 sys/content/research_story_architect.py --demo

# Tạo blueprint ngách nghiên cứu kèm các kịch bản Spin-off Short 9:16 độc lập
python3 sys/content/research_story_architect.py --topic academic-first-principles --spinoff-shorts

# Tạo gói full_frame_v1 chuẩn với thời lượng động theo content_depth_estimate
python3 sys/tools/build_full_frame_acceptance.py --output-dir sys/runs/full-frame-job
```

## Full-frame visual journey gate

For new jobs, declare `visual_pacing_profile: full_frame_v1` and follow [Full-frame quality contracts](../vp-full-frame-quality/SKILL.md). Plan across functional cognitive phases (`lived_friction` → `empirical_conflict` → `structural_model` → `actionable_resolution`). Keep setting descriptions concise, specifying 2D flat staging and lighting/palette. Apply the Feynman Visual Formula: 1 character + 1 focal metaphor object on a clean flat canvas with progressive domino frames adding detail incrementally without decorative clutter. Author source-backed comparisons without inventing numeric results. Preserve room and expression through `based_on` return shots (or set `allow_expression_shift: true` for intentional emotional turns); distinguish hard cuts from in-frame camera movement.

## Hand-drawn 2D explainer image authoring (`1.7.0`)

Use prompt registry `1.7.0` (`handdrawn_2d_explainer`) and the [visual style contract](../vp-production/references/visual-style.md) for new packages. Registry `1.7.0` enforces bold clean black outer contours, flat solid color fills (`terracotta`, `warm sand`, `ochre`, `sage green`, `slate blue`), pure `#FFFFFF` white fields for isolated objects/comparisons/diagrams, and flat solid backgrounds for contextual scenes. Import `STYLE_DESCRIPTION`, `CAST_APPEARANCE` and `DEFAULT_OUTFIT` from `visual_style`. Only include people when explicitly needed (`has_character: true`) using simple contextual 2D cartoon designs (no fixed round white head or white mittens), and never render white-on-black YouTube subtitle boxes or browser controls.
