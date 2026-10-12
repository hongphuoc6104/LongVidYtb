# Cấu Trúc Dẫn Chuyện 5 Hồi & Định Ngân Sách Thời Lượng (Conversational Structuring)

Tài liệu hướng dẫn dành cho **Research & Narrative Architect** trong việc phân bổ cấu trúc kịch bản 5 hồi và lập ngân sách thời lượng chuẩn xác cho Video Pilot.

---

## 1. Khung Kể Chuyện 5 Hồi Bất Biến (The 5-Part Conversational Arc)

Mọi video trong Video Pilot được xây dựng dựa trên 5 phân cảnh cốt lõi:

```
[SC01: Hook & Empathy] ──> [SC02: Reframe] ──> [SC03: Causal 70/30] ──> [SC04: Contrast] ──> [SC05: Loop Payoff]
     (0% - 15%)               (15% - 35%)            (35% - 65%)           (65% - 85%)          (85% - 100%)
```

### SC01: Hook & Empathy (Mở đầu & Đồng cảm giác quan)
- **Mục đích:** Kéo người xem dừng ngón tay lại trong 3 giây đầu tiên.
- **Cách viết:** Mô tả một hành động đời thường cụ thể mang tính giác quan. Tránh xa mọi lời chào hỏi hay giới thiệu sáo rỗng.
- **Tốc độ nói:** Nhanh, năng động (~4.2 âm tiết/giây).

### SC02: Reframe & The Dilemma (Lật ngược định kiến & Nghịch lý)
- **Mục đích:** Xóa bỏ niềm tin sai lầm của số đông và tạo ra một khoảng trống tò mò (curiosity gap).
- **Cách viết:** Đặt niềm tin ngây thơ đối diện với phát hiện khoa học bất ngờ.
- **Khoảng ngắt âm học:** Thường kết thúc bằng một khoảng ngắt kịch tính `[pause:900ms]` trước khi bước sang giải thích cơ chế.

### SC03: Causal Explanation 70/30 (Bóc tách cơ chế theo tỷ lệ vàng 70/30)
- **Mục đích:** Giải thích nguồn gốc thực sự của vấn đề mà không biến video thành một bài giảng khô khan.
- **Quy tắc tỷ lệ vàng 70/30:**
  - **70% Lời dẫn dắt hình ảnh & cảm xúc:** Sử dụng ẩn dụ trực quan (ví dụ: con hổ tiền sử, chiếc phanh hãm của não bộ, còi báo động).
  - **30% Dữ kiện khoa học cứng:** Tên cơ quan thần kinh, số liệu thực nghiệm, tên nhà nghiên cứu.
- **Tốc độ nói:** Ổn định, rõ ràng (~4.0 âm tiết/giây).

### SC04: Direct Concrete Contrast (Tương phản trực diện)
- **Mục đích:** Cụ thể hóa bài học thông qua hai bức tranh hoặc hai hành vi đối lập.
- **Cách viết:** Đặt hai hình ảnh cạnh nhau: Người cầu toàn (chờ cảm hứng hoàn hảo) vs Người hành động (chia nhỏ 5 phút); hoặc Người hiện đại căng thẳng vs Người tiền sử tự do.
- **Nhịp điệu:** Tương phản nhịp nhàng giữa hai nửa vế câu.

### SC05: Loop Closure & Philosophical Payoff (Khép vòng lặp & Dư âm triết lý)
- **Mục đích:** Để lại ấn tượng sâu sắc, kích thích người xem chiêm nghiệm và chia sẻ.
- **Kỹ thuật khép vòng lặp hoàn hảo (Perfect Loop Closure):**
  - Quay trở lại chính xác hình ảnh hoặc hành động ở SC01 (ví dụ: việc mở tủ lạnh lúc nửa đêm).
  - Khán giả nhìn lại hành động quen thuộc đó với một tâm thức hoàn toàn mới.
- **Tốc độ nói:** Chậm rãi, sâu lắng (~3.6–3.8 âm tiết/giây).

---

## 2. Ma Trận Ngân Sách Thời Lượng & Âm Tiết Tham Khảo Cho Video Ngắn (Short-Form Reference Matrix)

Thời lượng video (`duration`) không bị khóa cứng mà mở tự nhiên theo kịch bản và file WAV thực tế (`sys/format_profiles.py`). Bảng dưới đây là ví dụ phân bổ tham khảo cho các mốc video ngắn 5 hồi (áp dụng công thức $P_{\text{tail}} = 0.70\text{s}$ cho cảnh 1–4 và $0.35\text{s}$ cho cảnh 5, tốc độ đọc danh định 4.0 âm tiết/s):

| Cảnh | Tỷ lệ % | Video 45s (Target ~45s) | Video 60s (Target ~60s) | Video 75s (Target ~75s) | Video 90s (Target ~90s) |
|---|---|---|---|---|---|
| **SC01** (Hook) | 12% – 15% | 6.0s (21 âm tiết) | 8.0s (29 âm tiết) | 10.0s (37 âm tiết) | 12.0s (45 âm tiết) |
| **SC02** (Reframe) | 18% – 20% | 9.0s (33 âm tiết) | 12.0s (45 âm tiết) | 15.0s (57 âm tiết) | 18.0s (69 âm tiết) |
| **SC03** (Causal 70/30) | 30% – 35% | 15.0s (57 âm tiết) | 19.0s (73 âm tiết) | 24.0s (93 âm tiết) | 29.0s (113 âm tiết) |
| **SC04** (Contrast) | 18% – 20% | 8.5s (31 âm tiết) | 12.0s (45 âm tiết) | 15.0s (57 âm tiết) | 18.0s (69 âm tiết) |
| **SC05** (Loop Payoff) | 14% – 16% | 6.5s (25 âm tiết) | 9.0s (35 âm tiết) | 11.0s (43 âm tiết) | 13.0s (51 âm tiết) |
| **Tổng cộng** | **100%** | **45.0s (167 âm tiết)** | **60.0s (227 âm tiết)** | **75.0s (287 âm tiết)** | **90.0s (347 âm tiết)** |

*Lưu ý:* Khi trong cảnh có khoảng ngắt `[pause:900ms]`, số âm tiết mục tiêu sẽ giảm đi: $\Delta \text{Syllables} = \text{round}(0.9 \times 4.0) = 4$ âm tiết.

---

## 3. Quản Trị Nhịp Điệu Động Học (Dynamic Pacing Rules)

1. **Không viết câu kéo dài quá 25 âm tiết liên tục:** Ngắt câu bằng dấu chấm hoặc dấu phẩy để giọng đọc lấy hơi tự nhiên.
2. **Khống chế sai số thời lượng (Timeline Drift):**
   - Độ lệch giữa thời lượng đọc audio ước tính và thời lượng cảnh không được vượt quá **$\pm 0.3\text{s}$**.
   - Chạy lệnh `python3 sys/tools/script_cadence_checker.py` sau mỗi lần chỉnh sửa lời thoại để đảm bảo không bị cảnh báo âm học.
