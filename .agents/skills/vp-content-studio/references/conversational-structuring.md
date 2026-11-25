# Cấu Trúc Dẫn Chuyện 5 Hồi, Cú Tát Sự Thật & Định Ngân Sách Thời Lượng (Conversational Structuring)

Tài liệu hướng dẫn dành cho **Research & Narrative Architect** trong việc phân bổ cấu trúc kịch bản 5 hồi (cho cả `short_9x16` độc lập và từng macro-chapter của `long_16x9`), thiết kế câu mở đầu Counter-Intuitive Hook và lập ngân sách thời lượng chuẩn xác cho Video Pilot.

---

## 1. Khung Kể Chuyện 5 Hồi Bất Biến (The 5-Part Conversational Arc)

Mọi video ngắn độc lập (`short_9x16`) và mỗi chương lớn của video dài (`long_16x9`) được xây dựng dựa trên 5 chặng nhân quả:

```
[SC01: Truth-Slap Hook] ──> [SC02: Reframe] ──> [SC03: Causal 70/30] ──> [SC04: Contrast] ──> [SC05: Loop Payoff]
       (0% - 15%)              (15% - 35%)           (35% - 65%)          (65% - 85%)          (85% - 100%)
```

### SC01: Counter-Intuitive / Truth-Slap Hook & Empathy (Cú tát sự thật & Đồng cảm Việt hóa — 0–15%)
- **Mục đích:** Kéo khán giả lạnh (0 sub) dừng ngón tay ngay trong **2.5 – 3 giây đầu tiên**.
- **3 Quy tắc Bất biến của `SC01`:**
  1. **Câu đầu tiên $\le 18$ âm tiết (`Counter-Intuitive / Truth-Slap Hook`):** Đi thẳng vào nghịch lý phản trực giác hoặc lật tẩy sai lầm học thuật phổ biến (ví dụ: *"Đọc lại giáo trình năm lần chỉ đang ru ngủ bộ não của bạn."* — 14 âm tiết; hoặc *"Bài báo khoa học quốc tế không bao giờ bắt đầu bằng việc mở Word."* — 15 âm tiết). Tuyệt đối cấm mở đầu bằng *"Hãy nghĩ về..."*, *"Hãy tưởng tượng..."*, *"Hãy hình dung..."*.
  2. **Zero Pause in First 15 Seconds (`OPENING_SCENE_PAUSE_FORBIDDEN`):** Nghiêm cấm chèn bất kỳ thẻ `[pause:...]` nào trong `SC01`.
  3. **Bối cảnh Việt hóa 100% & Mật độ hình ảnh mở đầu:** Neo thẳng vào đời sống sinh viên/người đi làm Việt Nam; khi lời thoại hỗ trợ, hướng tới 8–9 ảnh toàn khung trong 12–12,5 giây đầu, mỗi ảnh bám một vật thể hoặc hành động được nhắc.
- **Tốc độ nói:** Nhanh, sắc bén, cuốn hút (**`4.2 – 4.4` âm tiết/giây**, với giọng chuẩn `VietNarrator` `speed: 1.0` cho cả `short_9x16` và `long_16x9`).

### SC02: Reframe & The Dilemma (Lật ngược định kiến & Nghịch lý — 15–35%)
- **Mục đích:** Xóa bỏ niềm tin sai lầm của số đông và mở ra khoảng trống tò mò (*Curiosity Gap*).
- **Cách viết:** Đặt thói quen học vẹt/sao chép cơ học đối diện với phát hiện của khoa học nhận thức hoặc luật ngầm của hội đồng phản biện Q1.
- **Khoảng ngắt âm học:** Có thể đặt 1 khoảng ngắt kịch tính `[pause:800ms]` hoặc `[pause:900ms]` ngay trước câu tiết lộ cơ chế cốt lõi (tổng toàn video tối đa 1–3 thẻ pause).

### SC03: Causal Explanation 70/30 (Giải phẫu cơ chế theo tỷ lệ vàng 70/30 — 35–65%)
- **Mục đích:** Giải phẫu quy trình nghiên cứu hoặc cơ chế thần kinh học mà không biến video thành bài giảng khô khan.
- **Quy tắc tỷ lệ vàng 70/30:**
  - **70% Lời dẫn dắt hình ảnh & sơ đồ trực quan:** Đặt Sơ đồ Tháp học thuật (*Academic Pyramid*) hoặc Flowchart `Question → Gap → Method → Evidence` trong một ảnh toàn khung; nhân vật và đạo cụ xuất hiện trong cùng không gian của sơ đồ.
  - **30% Dữ kiện khoa học văn nói (`<= 20` âm tiết):** Cơ chế nhận thức, con số thực nghiệm đắt giá (không đọc danh xưng giáo sư/đại học dài dòng).
- **Tốc độ nói:** Ổn định, mạch lạc (~`4.0` âm tiết/giây).

### SC04: Direct Concrete Contrast (Tương phản trực diện — 65–85%)
- **Mục đích:** Cụ thể hóa bài học thông qua hai cách tiếp cận đối lập.
- **Cách viết:** Đặt hai thực tại cạnh nhau trong một bố cục toàn khung dễ đọc hoặc bằng hai beat liên tiếp:
  - *Thực tại thứ nhất:* Người học vẹt / Mở Word gõ ngay từ trang 1 / Đọc bài báo từ đầu đến cuối rồi ngợp trong cơn bão thông tin.
  - *Bên phải (`x = 0.64`):* Nhà nghiên cứu Q1 / Xác định *Research Gap Matrix* trước khi viết / Đọc ngược từ Kết luận & Phương pháp để bóc tách bản chất.

### SC05: Loop Closure & Philosophical Payoff (Khép vòng lặp & Dư âm triết lý — 85–100%)
- **Mục đích:** Khép lại vòng lặp với hình ảnh mở đầu ở `SC01`, kích thích người xem bấm **Lưu (Bookmark)** và chia sẻ.
- **Tốc độ nói:** Chậm rãi, sâu lắng (~`3.6 – 3.8` âm tiết/giây), sử dụng hằng số đuôi $P_{\text{tail}} = 0.35\text{s}$ để kết thúc dứt khoát.

---

## 2. Ma Trận Ngân Sách Thời Lượng & Âm Tiết Tham Khảo Cho Video Ngắn (`short_9x16`)

Thời lượng video (`duration`) mở tự nhiên theo kịch bản và file WAV thực tế (`sys/format_profiles.py`). Bảng dưới đây là phân bổ tham khảo cho kịch bản `short_9x16` độc lập 5 hồi (áp dụng $P_{\text{tail}} = 0.70\text{s}$ cho cảnh 1–4 và $0.35\text{s}$ cho cảnh 5):

| Cảnh | Tỷ lệ % | Nhịp đọc mục tiêu | Video 45s (~45s) | Video 52.5s (~52.5s) | Video 60s (~60s) | Quy tắc Pause & Visual Hold |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **SC01** (Truth-Slap Hook) | 14% – 15% | `4.2 – 4.4` syl/s | 6.5s (24 âm tiết) | 8.0s (30 âm tiết) | 8.5s (32 âm tiết) | **0 Pause** (`OPENING_SCENE_PAUSE_FORBIDDEN`), câu đầu $\le 18$ syl; aim for roughly 4 full-frame images in first 5s |
| **SC02** (Reframe) | 18% – 20% | `4.2` syl/s | 9.0s (33 âm tiết) | 11.0s (38 âm tiết*) | 12.0s (45 âm tiết) | Tối đa 1 thẻ `[pause:900ms]` trước điểm lật ngược, đổi beat `1.5s–2.0s` |
| **SC03** (Causal 70/30) | 30% – 34% | `4.0` syl/s | 14.5s (55 âm tiết) | 13.0s (50 âm tiết) | 19.0s (73 âm tiết) | Sơ đồ toàn khung và các beat cụ thể (`0.83s–3.80s`) |
| **SC04** (Contrast) | 18% – 20% | `4.0` syl/s | 8.5s (31 âm tiết) | 11.5s (43 âm tiết) | 11.5s (43 âm tiết) | Đối chiếu toàn khung hoặc qua hai ảnh scene liên tiếp |
| **SC05** (Loop Payoff) | 14% – 16% | `3.6 – 3.8` syl/s | 6.5s (25 âm tiết) | 9.0s (34 âm tiết) | 9.0s (35 âm tiết) | Khép vòng lặp mở đầu, $P_{\text{tail}} = 0.35\text{s}$ |

*\*Ghi chú:* Khi `SC02` có 1 khoảng ngắt `[pause:900ms]`, số âm tiết mục tiêu giảm $\text{round}(0.9 \times 4.0) = 4$ âm tiết.

---

## 3. Quản Trị Nhịp Điệu Động Học & Chốt Chặn Kiểm Định

1. **Trần câu đơn & vế câu:** Không viết câu kéo dài quá **25 âm tiết** (`SENTENCE_TOO_LONG`) hoặc vế câu không dấu phẩy quá **18 âm tiết** (`BREATHLESS_CLAUSE`).
2. **Câu mở đầu `SC01`:** Bắt buộc $\le 18$ âm tiết (`OPENING_HOOK_TOO_LONG`) và tuyệt đối không có thẻ `[pause:...]` (`OPENING_SCENE_PAUSE_FORBIDDEN`).
3. **Khống chế sai số thời lượng (Timeline Drift):** Độ lệch $|\text{drift}| \le 0.30\text{s}$ qua `python3 sys/tools/script_cadence_checker.py`.
