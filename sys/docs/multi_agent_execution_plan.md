# Kế Hoạch Tổng Thể & Kiến Trúc Điều Phối Multi-Agent: Video Series "Ancient Humans"

> **Dự án**: Video Pilot — Tự động hóa sản xuất video giải thích kiến thức (*Ancient Humans: The Mystery of Time*)  
> **Phiên bản kế hoạch**: v2.0 (Thực thi Phương án B, Nâng cấp Lời thoại Kể chuyện, Chuẩn hóa 100% Ảnh AI & Render Colab T4)

---

## 1. Tổng Hợp & Sắp Xếp Trình Tự Thực Hiện (Execution Logic & Sequence)

Để đảm bảo video sau khi render có nhịp độ hoàn hảo, không bị lệch audio/visual và đáp ứng 100% các tiêu chuẩn khắt khe của người dùng, toàn bộ quy trình được tổ chức thành 5 giai đoạn tuần tự - song song:

```
[GIAI ĐOẠN 1: KỊCH BẢN & LỜI THOẠI KỂ CHUYỆN (vp-scriptwriting)]
   │ ── Phân tích văn kể video gốc ➔ Xây dựng Skill vp-scriptwriting ➔ Viết lại thoại 8 chương
   ▼
[GIAI ĐOẠN 2: THỊ GIÁC & HÌNH ẢNH (Option B & 100% Ảnh Flow AI)]
   │ ── Thay thế triệt để ảnh Ch2 (shots 40,41,42) & Ch6 ➔ Hoàn thiện Ch7 (35 ảnh) & Ch8 (21 ảnh)
   │ ── Cắt nhịp Sub-beats (< 2.0s) cho cảnh dài Ch3, Ch4 ➔ Bỏ giới hạn lùi viền 20%
   ▼
[GIAI ĐOẠN 3: ĐỒNG BỘ TIMELINE & PROPS TEMPLATES]
   │ ── Cập nhật cues, audioSrc, durations và sub-beats vào templates/ch{num}_props_template.json
   │ ── Bật cơ chế Smart Auto-Reframe (scale 1.14x, translateY offset) khi tắt phụ đề
   ▼
[GIAI ĐOẠN 4: RENDER TOÀN BỘ TRÊN COLAB TESLA T4 GPU]
   │ ── Render Ch2, Ch6, Ch7, Ch8 trên session Colab 'video-pilot-tts' (Headless Chromium an toàn)
   │ ── Kiểm tra thông số kỹ thuật từng chương bằng ffprobe (1920x1080 16:9, H.264/AAC @ 30fps)
   ▼
[GIAI ĐOẠN 5: GHÉP NỐI & NGHIỆM THU FULL 11 PHÚT]
   │ ── Concatenate 8 chương thành video hoàn chỉnh: ancient-humans-day-full-16x9_final.mp4
   │ ── Kiểm tra tính toàn vẹn và xuất báo cáo nghiệm thu
```

---

## 2. Chi Tiết Từng Hạng Mục Thực Hiện

### 2.1. Phân Tích Kịch Bản & Xây Dựng Skill `vp-scriptwriting`
- **Vấn đề của lời thoại cũ**: Quá trang trọng, mang đậm tính "văn viết hàn lâm", dùng nhiều câu bị động dịch thô từ tiếng Anh (*"ngày của bạn đã bị định sẵn"*, *"bao nhiêu giờ thuộc về kẻ khác"*, *"để trả lời câu hỏi đó, chúng ta phải bắt đầu từ..."*).
- **Văn phong chuẩn của video mẫu**:
  - Giọng điệu: Người bạn đồng hành tò mò, gần gũi, chia sẻ những phát hiện bất ngờ.
  - Móc câu (Hooks): Mở đầu bằng nhân hóa đồ vật thường nhật (*"một cỗ máy gắt gỏng gọi bạn dậy"*, *"bạn tắt nó đi"*), câu hỏi tu từ (*"Ai là ai? Thử đoán xem!"*), điểm lật tình thế (*"Thế nhưng đây mới là điều bất ngờ..."*).
  - Nhịp điệu câu thoại: Câu ngắn 6–14 từ, có khoảng nghỉ thở tự nhiên (micro-pauses) trước các thông điệp đắt giá.
- **Giải pháp chuyển thể**:
  - Tạo Skill chuẩn hóa: `.agents/skills/vp-scriptwriting/SKILL.md` và cẩm nang hướng dẫn `references/spoken-narration-guide.md`.
  - Giữ nguyên 100% dữ liệu lịch sử, nhân vật khoa học (Richard Lee, Polly Wiessner, Ju/'hoansi, Hadza, Martu) và số liệu (15–20h/tuần, 10.000 năm, 50.000 năm, 75%, 81%).
  - Chuyển hóa toàn bộ câu thoại của cả 8 chương thành văn nói sinh động, tự nhiên.

### 2.2. Bất Biến 100% Ảnh AI & Thực Thi Phương Án B
- **Core User Invariant**: 100% hình ảnh trong video phải đến từ `sys/exports/ancient_humans_flowkit_bundle/generated_images/ch{num}/` (người que AI), tuyệt đối không lấy bất kỳ khung hình chụp mẫu nào từ video YouTube trong `sys/scratch/reference_49_Ph2q6uIM/`.
- **Chương 2**: Thay thế triệt để 3 shot đầu tiên (#40, #41, #42) bằng ảnh vẽ người que khảo cổ và sơ đồ hố khai quật. Cập nhật `_media_state.json` đạt 37/37 shot AI.
- **Chương 6**: Xác minh toàn bộ 30/30 shot đạt chuẩn ảnh AI, không trùng lặp video mẫu.
- **Chương 7 & Chương 8**: Sinh toàn bộ 35 ảnh còn lại của Ch7 (shots 190–224) và 21 ảnh của Ch8 (shots 225–245) theo đúng Visual Cast Invariant (người que đầu tròn trắng viền đen đậm, mắt chấm tròn, thân que đơn giản, nền kem sáng 16:9, không chữ/watermark).
- **Phương án B (Sub-beats & Auto-reframe)**:
  - Chia nhỏ các phân cảnh dài > 3.0s thành các sub-beat 1.5s – 2.0s để tạo sự thay đổi góc nhìn và biểu cảm liên tục.
  - Bỏ hoàn toàn câu cấm 20% chân khung hình khỏi prompt AI.
  - Kích hoạt Smart Auto-Reframe (scale 1.14x, dịch chuyển trục Y) trong engine renderer Remotion.

### 2.3. Quy Chuẩn Render Trên Colab Tesla T4 GPU
- Session GPU: `video-pilot-tts` (NVIDIA Tesla T4).
- Bộ cờ an toàn bắt buộc: `--no-sandbox`, `--disable-dev-shm-usage`, `--run-all-compositor-stages-before-draw`, `--disable-gpu-rasterization`, `--enable-gpu`, `--ignore-gpu-blocklist`, `DISABLE_FROM_SURFACE=true`.
- Kiểm tra `ffprobe`: Video H.264, Audio AAC, 1920x1080 @ 30fps.
- Nối video bằng `ffmpeg -f concat -c copy` đảm bảo không bị suy hao chất lượng.

---

## 3. Phân Công Nhiệm Vụ Cho Các Sub-Agents Chuyên Biệt (/boost)

Để tăng tốc độ xử lý tối đa theo yêu cầu `/boost`, khối lượng công việc được phân rã thành 5 Agent độc lập có thể phối hợp đồng thời:

| Agent ID | Tên vai trò | Trách nhiệm chính | Đầu ra bàn giao |
|---|---|---|---|
| **Agent-A** | *Scriptwriting & Voice Stylist* | Nghiên cứu văn kể video mẫu; soạn thảo guideline `vp-scriptwriting`; viết lại lời thoại 8 chương sang văn nói tự nhiên; tổng hợp audio narration mới. | `.agents/skills/vp-scriptwriting/`, kịch bản lời thoại văn nói 8 chương, narration WAV. |
| **Agent-B** | *Visual Direction & Image Generator* | Tạo ảnh người que cho Ch2 (3 ảnh sửa), Ch7 (35 ảnh), Ch8 (21 ảnh) và sub-beats; quản lý multi-profile Chrome & `_media_state.json`. | 240 ảnh JPEG `1376x768` trong `generated_images/ch1-ch8`, metadata sidecars. |
| **Agent-C** | *Timeline & Pacing Architect* | Thiết kế cấu trúc sub-beats Phương án B; căn chỉnh thời gian hiển thị từng hình theo nhịp giọng nói; cập nhật `props_template.json` cho cả 8 chương. | 8 file `templates/ch{1..8}_props_template.json` đã đồng bộ sub-beats và auto-reframe. |
| **Agent-D** | *Colab GPU Render Worker* | Đóng gói build độc lập từng chương; đồng bộ lên Colab Tesla T4; render song song / tuần tự trên `render.mjs`; chạy ffprobe nghiệm thu kỹ thuật. | `video/ancient-humans-day-ch{num}-16x9/` video MP4 hoàn chỉnh đạt chuẩn 1080p. |
| **Agent-E** | *Master Concatenator & QA Inspector* | Ghép nối 8 chương thành video Full 11 phút; kiểm tra trôi hình/tiếng, khớp tổng thời lượng ~650s–670s; lập biên bản nghiệm thu cuối cùng. | `ancient-humans-day-full-16x9_final.mp4`, biên bản nghiệm thu chi tiết. |
