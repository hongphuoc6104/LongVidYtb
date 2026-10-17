---
name: vp-scriptwriting
description: "Author and transform explainer video scripts into natural conversational spoken storytelling with counter-intuitive 3-second hooks and calibrated acoustic cadence."
---

# VP Scriptwriting — Conversational Essayist, Truth-Slap Hook & Voice Cadence Skill

`vp-scriptwriting` là bộ kỹ năng cốt lõi dùng để sáng tác và thẩm định kịch bản video trong Video Pilot (cho cả `long_16x9` và `short_9x16`). Bộ kỹ năng này được tối ưu hóa cho **Agent Gemini Flash**: loại bỏ việc tính toán công thức phức tạp thủ công, tập trung 100% vào câu thoại tự nhiên, giàu nhịp điệu cảm xúc và gắn kết 1-1 với hành động hình ảnh toàn khung (`full_frame_v1`).

---

## 1. Bản Sắc Giọng Kể, Cú Tát Sự Thật Mở Màn & Nhịp Câu Con Người

- **Hình tượng (The Voice Archetype):** **Conversational Essayist (Nhà luận thuyết trò chuyện)** — điềm đạm, ấm áp, sắc sảo, như người đàn anh hướng dẫn nghiên cứu bên bàn cà phê, khóa cứng ngách **"Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật"**.
- **Counter-Intuitive / Truth-Slap Hook (Cú tát sự thật trong 2.5 giây đầu):**
  - Câu đầu tiên của `SC01` bắt buộc **$\le 18$ âm tiết** (`OPENING_HOOK_TOO_LONG`), đánh thẳng vào nghịch lý phản trực giác hoặc lật tẩy ảo giác học thuật của người xem (ví dụ: *"Trang sách vàng kín, đầu bạn vẫn trống."* — 8 âm tiết; hoặc *"Đọc lại giáo trình năm lần chỉ tạo ra ảo giác hiểu bài."* — 12 âm tiết).
  - **Tuyệt đối cấm** mở đầu bằng lời chào (*"Xin chào"*), giới thiệu đề tài (*"Hôm nay chúng ta..."*), hoặc câu dẫn nhập chậm (*"Hãy nghĩ về..."*, *"Hãy hình dung..."*, *"Hãy tưởng tượng..."*, *"Giờ đây, hãy thử..."*).
- **Zero Pause in First 15 Seconds (`SC01` — `OPENING_SCENE_PAUSE_FORBIDDEN`):**
  - **Nghiêm cấm** chèn bất kỳ thẻ `[pause:...]` nào trong cảnh mở đầu `SC01`.
- **Quy Tắc Nhịp Điệu Tự Nhiên (Chống "Văn Mẫu AI"):**
  - **Bắt buộc xen kẽ câu ngắn và câu dài (`stddev_syllables >= 1.8`):** Không bao giờ viết mọi cảnh đều chằn chặn 3 câu dài 18–20 chữ. Mỗi chương/kịch bản bắt buộc phải xen kẽ các câu ngắn đanh gọn (**3–8 âm tiết**, ví dụ: *"Đó là ảo giác năng lực."*, *"Mỏ vàng nằm ở cuối bài."*, *"Làm sao biết bạn hiểu thật?"*) với các câu giải thích cơ chế (**15–24 âm tiết**).
  - **Cấm ngắt dấu phẩy ngang xương giữa Chủ ngữ và Vị ngữ:** Tuyệt đối không chèn dấu phẩy vô lý giữa chủ ngữ và động từ (ví dụ sai: *"Bản chất của tổng quan tài liệu, là..."* hoặc *"Đó là nơi bạn vẽ nên, khoảng trống..."*) chỉ để lách luật đếm chữ. Hãy tách hẳn thành một câu ngắn tự nhiên.
  - **Tự động chuẩn hóa ở Backend:** Hệ thống (`sys/remote_audio.py`, `sys/adapters.py`, `sys/colab_bridge/worker.py`) đã tự động tách thẻ `[pause:...]` thành khoảng nghỉ âm học thực tế và tự động phiên âm số/từ mượn qua `vn_text_normalizer.py`. Agent chỉ cần tập trung viết câu tiếng Việt tự nhiên, giàu hình ảnh.

---

## 2. Khung Kể Chuyện Nhân Quả & Chuyển Cảnh Một Chiều

1. **Hành trình nhân quả (`full_frame_v1`):**
   - **Giai đoạn 1 — Trải nghiệm bản địa Việt Nam (0–20%, `tone: "narrative_warm"`):** Bối cảnh sát sườn với sinh viên/người nghiên cứu Việt Nam (bàn học 2 giờ sáng, tô bút dạ quang kín giáo trình, giảng đường, mở Word trắng tinh).
   - **Giai đoạn 2 — Thực nghiệm & Bằng chứng đối chứng (20–50%, `tone: "analytical_crisp"`):** Đặt hai nhóm học tập/nghiên cứu lên bàn cân thực nghiệm khoa học; trích dẫn dữ kiện văn nói $\le 20$ âm tiết.
   - **Giai đoạn 3 — Cơ chế & Ẩn dụ trực quan (50–80%, `tone: "analytical_crisp"`):** Giải phẫu cơ chế bằng ẩn dụ vật lý cụ thể (bản đồ bị sương mù che, cây cầu thiếu nhịp, Tháp Học Thuật 9 tầng, chuỗi `Question → Gap → Method → Evidence`, Ma trận Khoảng trống).
   - **Giai đoạn 4 — Ứng dụng thực chiến & Khép vòng lặp (80–100%, `tone: "reflective_slow"`):** Quay lại phòng bảo vệ khóa luận 120 giây đầu và bàn học mở màn với giải pháp hành động rõ ràng.
2. **Luân phiên thế chuyển cảnh động:**
   - Tuyệt đối cấm các câu dẫn sáo rỗng (*"Nhưng rồi..."*, *"Bước sang..."*, *"Hãy cùng bước vào..."*, *"Nhưng câu chuyện chưa dừng lại ở đó..."*).
3. **Phân vùng lịch sử một chiều (Strict Forward Chronology):**
   - Khi đã bước sang thời kỳ mới, nghiêm cấm kéo ngược bối cảnh về thời kỳ cũ. Trong 60 giây đầu (`SC01–SC02`), bắt buộc giữ 100% bối cảnh Việt Nam hiện đại.

---

## 3. Viết Kịch Bản Gắn Kết 1-1 Với Hình Ảnh Toàn Khung (`Sentence-Beat Pairing`)

Để Agent không bao giờ tính sai tọa độ hay trượt điểm neo (`anchor_quote`), hãy soạn kịch bản theo từng cặp **`(Câu thoại ngắn tự nhiên, "loại_shot|Hành động hình ảnh cụ thể")`** (như trong `sys/tools/build_full_frame_acceptance.py` hoặc hàm `build_scenes_from_story_rows` trong `sys/tools/research_story_architect.py`):

- **`full_scene`**: Nhân vật người que ẩn danh và đồ vật tương tác trực tiếp trong bối cảnh vật lý.
- **`variation`**: Giữ nguyên căn phòng và góc máy của ảnh trước (`based_on`), chỉ đổi cử chỉ tay/biểu cảm nhân vật (code tự động thêm `Expression lock`).
- **`macro_prop`**: Cận cảnh bàn tay 4 ngón hoạt hình cầm bút, trang sách tô vàng, đồng hồ hoặc chi tiết sơ đồ.
- **`white_card`**: Thẻ khái niệm nền trắng tinh `#FFFFFF` cô lập một biểu tượng đối sánh tối giản.

1. **Cold open (`0:00–0:12.5`):** Viết các câu ngắn gọn gắn với hành động dồn dập để đạt khoảng 4 hình trong 5 giây đầu và 8–9 hình trong 12,5 giây đầu.
2. **Thân bài (`sau 0:15`):** Giữ mỗi câu/nhịp hình trong khoảng **`0.83s–3.80s`**.

---

## 4. Công Cụ Kiểm Tra Tự Động

```bash
# Kiểm tra âm học, cấm pause ở SC01, trần câu mở đầu <= 18 âm tiết, trần câu <= 25 âm tiết
python3 sys/tools/script_cadence_checker.py path/to/content.json \
  --forbid-opening-pause \
  --max-opening-hook-syllables 18 \
  --max-sentence-syllables 25 \
  --max-clause-syllables 18 \
  --max-dramatic-pauses 4 \
  --strict

# Kiểm định tính đa dạng kịch bản và nhịp điệu câu tự nhiên (stddev_syllables & short_punchy_count)
python3 sys/tools/script_diversity_linter.py path/to/content.json
```

---

## 5. Danh Mục Tài Liệu Tham Khảo

- [Khung Kể Chuyện Conversational Essayist](references/conversational-essayist-framework.md)
- [Sổ Tay Lời Dẫn Văn Nói Tiếng Việt](references/spoken-narration-guide.md)
- [Quy Chuẩn Giọng Đọc, Tốc Độ & Ngắt Nhịp](../vp-channel-patterns/references/voice-cadence-pacing.md)
- [Chỉ Dẫn Kịch Bản Sản Xuất](../vp-production/references/script.md)
- [Chỉ Dẫn Âm Thanh Sản Xuất](../vp-production/references/audio.md)
- [Hợp Đồng Chất Lượng Toàn Khung](../vp-full-frame-quality/SKILL.md)
