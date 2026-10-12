# Video Pilot — Implementation Roadmap: Phương Án B & Render Toàn Diện 8 Chương

> **Mục tiêu**: Nâng cấp nhịp dựng video (Pacing & Visual Dynamic), khống chế thời lượng 1 hình không vượt quá 2–4s (trung bình 1.5s–2.5s), chuẩn hóa toàn bộ kịch bản và giọng đọc sang giọng Adam (đồng bộ 100% tiếng - hình), sinh 142 ảnh thiếu qua 3 profile Chrome CDP (`vp-flow-cdp`), render lại độc lập toàn bộ 8 chương trên Colab GPU T4 với Smart Auto-Reframe (`VP_SMART_AUTOREFRAME=true`), ghép nối full video 11 phút và chạy Băng Chuyền 6 Bước (`./pipeline run`) đạt chứng nhận Green Certification.

---

## 1. Trọng Tâm Kiến Trúc (Architectural Focus)
- **Khống chế thời lượng hiển thị hình ảnh (Pacing Invariant $\le 2\text{--}4\text{s}$)**: Tách toàn bộ các shot tĩnh dài (> 3.0s) thành các sub-beats năng động từ 1.5s – 2.5s. Tổng số shots trong manifest chính thức `manifest_option_b_full.json` là **382 shots**.
- **Đồng bộ chuẩn 100% Giọng đọc Adam & Hình ảnh**:
  - Chuẩn hóa ngữ âm 100% bằng `phonetic_normalized_script_8ch.json` và `vn_text_normalizer.py`.
  - Tốc độ đọc 3.8 – 4.2 âm tiết/s, căn chỉnh chính xác bù trừ đuôi ngắt âm $P_{\text{tail}}$.
  - Đồng bộ timestamp `cues.json` khớp 1-1 với visual beats của từng chương.
- **Sinh ảnh song song 3 Profile Chrome CDP (`vp-flow-cdp`)**:
  - Chạy đồng thời trên 3 cổng remote debugging: 9222, 9223, 9224.
  - Phân bổ patch 2–4 shots/patch; tự động hồi phục khi gặp cảnh báo bất thường.
  - Xóa bỏ triệt để chỉ thị chừa đáy 20% phụ đề, bảo đảm hình vẽ full-bleed tự nhiên.
  - Tuân thủ nghiêm ngặt Cast Invariant: người que vô danh đầu tròn trắng viền đen 4px, thân que, nét vẽ marker đen, nền giấy sáng.
- **Smart Auto-Reframe & Render Colab T4 Headless**:
  - Remotion renderer chạy qua `sys/colab_bridge/chrome-wrapper.sh` với đầy đủ cờ headless compositor an toàn.
  - Tắt phụ đề (`hideSubtitles: true`) và bật `VP_SMART_AUTOREFRAME=true` (scale 1.14x – 1.18x, hạ tâm ảnh) triệt tiêu viền trắng đáy.
- **Ghép nối Full Video 11 Phút & Phụ đề**:
  - Ghép lossless 8 chương thành `video/ancient_humans_full_11m_final.mp4`.
  - Xuất file phụ đề đồng bộ `video/ancient_humans_full_11m.srt`.
- **Băng Chuyền 6 Bước (`./pipeline run`)**:
  - Đạt chuẩn Green Certification (Station 1 -> Station 6).

---

## 2. Thống Kê Shots & Trạng Thái Sản Xuất 8 Chương

| Chương | Tiêu đề | Thời lượng | Shots Option B | Ảnh hiện có | Cần sinh mới | Audio (Giọng Adam) |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
| **Ch 1** | The mystery of modern time | ~70s | 43 | 34 | +9 shots | Đã có `ch1_narration_spoken.wav` (Adam) |
| **Ch 2** | Skeletons as historical diary | ~95s | 52 | 37 | +15 shots | Đã có `ch2_narration_spoken.wav` (Adam) |
| **Ch 3** | Life as a hunter-gatherer | ~83s | 46 | 28 | +18 shots | Tổng hợp Adam trên Colab T4 |
| **Ch 4** | The 17-hour work week | ~77s | 38 | 20 | +18 shots | Tổng hợp Adam trên Colab T4 |
| **Ch 5** | The value of social time | ~102s | 56 | 34 | +22 shots | Tổng hợp Adam trên Colab T4 |
| **Ch 6** | Nighttime & birth of culture | ~91s | 50 | 30 | +20 shots | Đã có `ch6_narration_spoken.wav` (Adam) |
| **Ch 7** | The trap of agriculture | ~101s | 64 | 36 | +28 shots | Tổng hợp Adam trên Colab T4 |
| **Ch 8** | Trading freedom for security | ~68s | 33 | 21 | +12 shots | Tổng hợp Adam trên Colab T4 |
| **TỔNG** | **Series 8 Chương** | **~11 Phút** | **382 shots** | **240** | **+142 shots** | **Đồng bộ 100% Giọng Adam** |

---

## 3. Kế Hoạch Thực Hiện Tiếp Theo
1. **Kiểm tra trạng thái 3 Chrome CDP Profiles** (cổng 9222, 9223, 9224) và khởi chạy sinh batch 142 ảnh thiếu kèm metadata sidecar `.json`.
2. **Tổng hợp audio giọng Adam** cho các chương 3, 4, 5, 7, 8 trên Colab T4 qua OmniVoice, trích xuất `cues.json`.
3. **Render tuần tự các chương trên Colab T4** với Smart Auto-Reframe.
4. **Ghép nối video tổng 11 phút** và xuất file SRT.
5. **Chạy `./pipeline run`** thẩm định 6 trạm băng chuyền.
