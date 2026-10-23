---
name: vp-research-architect
description: "Architect research-backed conversational narratives, 3-tier academic funnel packaging, and full_frame_v1 pipeline blueprints."
---

# VP Research Architect — Research, Packaging & Full-Frame Narrative Architecture Skill

`vp-research-architect` là bộ kỹ năng thượng nguồn (upstream creative & technical engine) chịu trách nhiệm nghiên cứu đề tài, khai thác cứ liệu học thuật chuẩn quốc tế (Q1), đóng gói CTR (Title/Thumbnail/SEO) và kiến trúc bộ hồ sơ kỹ thuật hoàn chỉnh (`brief.json` và `content.json` chuẩn Schema 3.0, `visual_pacing_profile: "full_frame_v1"`) cho băng chuyền Video Pilot (`long_16x9` và `short_9x16` Spin-offs).

Bộ kỹ năng này được thiết kế để **tự động hóa 100% phần tính toán kỹ thuật bằng code Python**, giúp Agent thực thi (kể cả dòng model nhẹ như Gemini Flash) không bao giờ phải đoán tọa độ `(x, y)` hay tính toán offset thủ công.

---

## 1. Định Vị Ngách & Phễu 3 Tầng (Core Mission & 3-Tier Pillar Lock)

- **Trụ cột nội dung cố định (`channel_pillar`):** Khóa cứng vào ngách **"Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật"** (kết hợp Tâm lý học Nhận thức & Khoa học Học tập).
- **Quy tắc Chống Loãng Tệp (`Anti-Dilution Guard`):** Tuyệt đối **cấm** các mẹo vặt văn phòng (gõ hàm Excel, làm Slide nhanh 4 tiếng, tình huống bạn Na học tiếng Anh).
- **Mô hình Phễu 3 Tầng (`funnel_tier`):**
  1. **Tầng 1 — Phễu Rộng (`tier_1_broad`):** *"Ảo Giác Hiểu Biết & Nghịch Lý Học Thuật"* (*Biết tính $\neq$ Hiểu bản chất*; *Ảo giác năng lực khi đọc lại giáo trình 5 lần*; *Kỹ thuật Feynman & cái bẫy thuật ngữ hàn lâm*).
  2. **Tầng 2 — Phễu Giữa (`tier_2_mid`):** *"Giải Phẫu Quy Trình Nghiên Cứu Chuẩn Quốc Tế (Q1) & Tâm Lý Hội Đồng"* (*Academic Pyramid 9 tầng*, chuỗi `Question → Gap → Method → Evidence → Paper`, *Tâm lý Hội đồng trong 120 giây đầu phòng bảo vệ*).
  3. **Tầng 3 — Phễu Chuyển Đổi (`tier_3_conversion`):** *"Vũ Khí Tư Duy Học Thuật (AI for Deep Research)"* (*Biến 30 bài báo Q1 thành Ma trận Khoảng trống Nghiên cứu — Research Gap Matrix*, *Dùng AI phản biện chéo lý thuyết thay vì viết hộ*).

---

## 2. Quy Trình Kiến Trúc Tối Giản Cho Agent Flash (`full_frame_v1`)

### Bước 1: Khai Thác Dữ Kiện Văn Nói, 1 Nghịch Lý Cốt Lõi & Việt Hóa 60 Giây Đầu
- **1 Nghịch Lý Cốt Lõi / Video (Cấm Frankenstein Bloat & Cấm Nhân Bản Đề Tài):** Mỗi video chỉ mổ xẻ sâu **1 nghịch lý duy nhất** kèm **1 thí nghiệm tâm điểm có cốt truyện** (ai làm gì, thiết lập đối chứng ra sao, cú lật kết quả bất ngờ thế nào). Tuyệt đối không nhồi nhét giáo trình đại cương nhiều chương rời rạc và không lặp lại đề tài/hook đã sản xuất trong `sys/exports/`.
- Mọi dữ kiện trong `sources[].facts` và `required_points` phải là câu văn nói tự nhiên $\le 20$ âm tiết (ngưỡng cứng $22$), không chứa `DOI`, `ISBN`, `et al.`, `%`, `/` (`check_conversational_spoken_facts()`).
- **Việt hóa 60 giây đầu:** Mở màn bằng bối cảnh sát sườn với người học tại Việt Nam (bàn học đêm khuya, bút dạ quang vàng, giảng đường, phòng bảo vệ khóa luận). Chi tiết: [Fact Mining Guide](references/fact-mining-guide.md).

### Bước 2: Đóng Gói CTR (`Packaging & SEO Contract`)
- Tách biệt `topic` nội bộ khỏi bộ trường `packaging`:
  1. `youtube_title`: $\le 55$ ký tự, tạo *Curiosity Gap*, không tự trả lời trong tiêu đề.
  2. `thumbnail_spec`: `visual_hook` + `text_overlay` đúng **2–4 từ in hoa**.
  3. `channel_pillar` & `funnel_tier`: Khóa cố định ngách Tư Duy Nghiên Cứu (`tier_1_broad` / `tier_2_mid` / `tier_3_conversion`).

### Bước 3: Soạn Kịch Bản Theo Cặp `(Câu Thoại, Hành Động Hình Ảnh)` — Không Đoán Tọa Độ
- Thay vì tự tính thời lượng, tự cắt `anchor_quote` hoặc tự đoán tọa độ `focus: {x, y}`, hãy sử dụng hàm **`build_scenes_from_story_rows()`** trong `sys/tools/research_story_architect.py` (hoặc cấu trúc `STORY` trong `sys/tools/build_full_frame_acceptance.py`):
  - Mỗi dòng là một cặp `(câu_thoại_tiếng_Việt, "shot_type|mô_tả_hình_ảnh_toàn_khung")`.
  - Chọn `shot_type` trong 7 loại chuẩn: `full_scene`, `variation`, `macro_prop`, `white_card`, `white_isolated`, `still_life` (cận cảnh vật thể/tài liệu không có nhân vật hay bàn tay), và `environment` (cảnh rộng kiến trúc/thiên nhiên không có người).
  - **Quy chuẩn Bối cảnh (Setting Brevity):** Chuỗi `setting` bắt buộc $\le 8$ từ, chỉ mô tả không gian vật lý và điều kiện ánh sáng (ví dụ: `"A student desk under green lamp light."`), tuyệt đối không liệt kê đồ vật, đạo cụ, bàn ghế trong `setting`.
  - **Khoảng thở Thị giác (Visual Breathing Room):** Để chống mệt mỏi nhận thức, trong mỗi cửa sổ 10 nhịp hình trượt (10-beat sliding window), bắt buộc có ít nhất 3 nhịp hình không có nhân vật ($\ge 30\%$ rest frames: `still_life`, `environment`, hoặc `white_card` thuần biểu tượng), và không bao giờ xuất hiện quá 4 nhịp nhân vật liên tiếp.
  - Code Python trong `build_content_v3()` sẽ **tự động**:
    - Ghép câu, tính thời lượng chuẩn và trích xuất `anchor_quote` chính xác 100%.
    - Khớp câu `coverage[].quote` với `required_points` theo độ chồng lấp từ vựng cao nhất (`_select_best_coverage_quote()`) thay vì lấy mù quáng câu đầu tiên.
    - Nối `based_on` + `Expression lock` qua `apply_room_continuity()` cho các cảnh cùng phòng (và tôn trọng `allow_expression_shift: true` khi cần đổi biểu cảm).
    - Chọn chuyển động camera ngữ nghĩa 4 hướng không lặp qua `select_semantic_camera_effect()` (`entropy >= 1.5` bits).
    - Khóa tâm `focus` trong vùng an toàn trung tâm (`0.35..0.65`), gắn `narrative_phase` (`lived_friction`, `empirical_conflict`, `structural_model`, `actionable_resolution`) và điều biến giọng `tone` động qua `_infer_scene_tone()`.
    - Kiểm định tự động `diversity_report` (`lint_script`) trong `write_production_package()`.
- Chi tiết: [Conversational Structuring](references/conversational-structuring.md) và [Pipeline Blueprint Spec](references/pipeline-blueprint-spec.md).

---

## 3. Công Cụ Hỗ Trợ Tự Động Hóa

```bash
# Tạo bộ blueprint mẫu (kèm kiểm định Packaging, Việt hóa 60s đầu & Cadence)
python3 sys/tools/research_story_architect.py --demo

# Tạo blueprint ngách Tư Duy Nghiên Cứu Q1 kèm các kịch bản Spin-off Short 9:16 độc lập
python3 sys/tools/research_story_architect.py --topic academic-paradox-q1 --spinoff-shorts

# Tạo gói full_frame_v1 chuẩn 19 cảnh (5-8 phút)
python3 sys/tools/build_full_frame_acceptance.py --output-dir sys/runs/full-frame-job
```

## Full-frame visual journey gate

For new jobs, declare `visual_pacing_profile: full_frame_v1` and follow [Full-frame quality contracts](../vp-full-frame-quality/SKILL.md). Plan across the 4 functional cognitive phases (`lived_friction` → `empirical_conflict` → `structural_model` → `actionable_resolution`). Keep setting descriptions concise at $\le 8$ words (space + lighting only). Maintain visual breathing room: at least 30% of beats in every 10-beat window must be character-free rest frames (`still_life`, `environment`), and never exceed 4 consecutive character beats. Use at most two consecutive scenes per physical setting; for ten or more scenes, keep each setting at or below 30%. Author source-backed comparisons without inventing numeric results. Preserve room and expression through `based_on` return shots (or set `allow_expression_shift: true` for intentional emotional turns); distinguish hard cuts from in-frame camera movement.

## Hand-drawn 2D explainer image authoring (`1.7.0`)

Use prompt registry `1.7.0` (`handdrawn_2d_explainer`) and the [visual style contract](../vp-production/references/visual-style.md) for new packages. Registry `1.7.0` enforces bold clean black outer contours, flat solid color fills (`terracotta`, `warm sand`, `ochre`, `sage green`, `slate blue`), pure `#FFFFFF` white fields for isolated objects/comparisons/diagrams, and flat solid backgrounds for contextual scenes. Import `STYLE_DESCRIPTION`, `CAST_APPEARANCE` and `DEFAULT_OUTFIT` from `visual_style`. Only include people when explicitly needed (`has_character: true`) using simple contextual 2D cartoon designs (no fixed round white head or white mittens), and never render white-on-black YouTube subtitle boxes or browser controls.
