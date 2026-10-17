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

### Bước 1: Khai Thác Dữ Kiện Văn Nói & Việt Hóa 60 Giây Đầu
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
  - Chọn `shot_type` trong 5 loại chuẩn: `full_scene`, `variation`, `macro_prop`, `white_card`, `white_isolated`.
  - Code Python trong `build_content_v3()` sẽ **tự động**:
    - Ghép câu, tính thời lượng chuẩn và trích xuất `anchor_quote` chính xác 100%.
    - Nối `based_on` + `Expression lock` qua `apply_room_continuity()` cho các cảnh cùng phòng.
    - Chọn chuyển động camera ngữ nghĩa không lặp qua `select_semantic_camera_effect()`.
    - Khóa tâm `focus` trong vùng an toàn trung tâm (`0.35..0.65`) và gắn sắc thái giọng `tone` (`narrative_warm`, `analytical_crisp`, `reflective_slow`).
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

For new jobs, declare `visual_pacing_profile: full_frame_v1` and follow [Full-frame quality contracts](../vp-full-frame-quality/SKILL.md). Plan local experience → experimental evidence → mechanism/metaphor → practical return. Use at most two consecutive scenes per physical setting; for ten or more scenes, keep each setting at or below 30%. Author source-backed comparisons without inventing numeric results. Preserve room and expression through `based_on` return shots; distinguish hard cuts from in-frame camera movement.
