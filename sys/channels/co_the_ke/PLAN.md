# KẾ HOẠCH CHI TIẾT KÊNH: CƠ THỂ KỂ (`co_the_ke`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `co_the_ke` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/co-the-ke` (`origin/channel/co-the-ke`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-co-the-ke`
- **Ngách nội dung:** Sức khỏe và cơ thể được nhân hóa
- **Lời hứa thương hiệu (Value Proposition):** Các cơ quan trong người bạn tự kể chuyện, vui mà đúng khoa học.
- **Khán giả mục tiêu:** Người 18-40 quan tâm sức khỏe, thói quen sinh hoạt
- **Nhân vật dẫn chuyện (Persona):** Các cơ quan nội tạng biết nói, mỗi cơ quan một tính cách
- **Giọng văn (Tone):** Hài, nhân hóa, dễ thương nhưng chính xác về khoa học | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 30–45s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Zack D. Films** (YouTube Shorts/TikTok): Drop straight into 'what happens if' with zero intro (format only).
- **Bác sĩ Huy** (TikTok): Vietnamese doctor-backed health myths busting.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Kurzgesagt** (YouTube): Deep, well-sourced science explainers.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open with 'if you do X, this is what your body does'.
- Let one organ character narrate in first person.
- Every health claim must cite a medical source in the description.
- Never claim cures; end with 'hỏi bác sĩ nếu...' when relevant.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Nếu bạn [thói quen], đây là điều [cơ quan] phải chịu.`
- `Điều gì xảy ra với cơ thể khi bạn [hành động] trong [thời gian]?`
- `[Cơ quan] của bạn đang than phiền vì [thói quen].`
- `Đừng [thói quen phổ biến] nữa, [cơ quan] sẽ cảm ơn bạn.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi: bạn có thói quen này không? Lưu lại để nhắc mình.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi tập 'một ngày của cơ quan khác'.
### Điều cấm kỵ (Avoid)
- Cure or treatment claims
- Supplement promotion without evidence
- Body shaming

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_organ_buddies` — Nội tạng dễ thương: cơ quan có mặt và tính cách, nền trắng sạch
- **Bảng màu khóa cứng:** `#FFFFFF`, `#F4A6A6`, `#F6C28B`, `#A23E48`, `#F28C9B`, `#7FB3D5`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Recurring organ characters: Tim (heart) brave and loud, Dạ Dày (stomach) dramatic complainer, Gan (liver) tired hard worker, Não (brain-shaped round pink blob) overthinking boss; plus a simple doodle human host with a round white head
- **Trang phục (`DEFAULT_OUTFIT`):** Organs have no clothing; the human host wears a flat calm-blue (#7FB3D5) T-shirt
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** One organ character with a dramatic expression + 2-3 word warning in bold letters.
- **Prompt Style gốc:**
  > Clean 2D kawaii medical-explainer illustration: smooth medium black outlines (#222222), flat unshaded fills in soft organ pink (#F4A6A6), stomach peach (#F6C28B), liver maroon (#A23E48), lung rose (#F28C9B) and calm blue (#7FB3D5) on a flat solid white canvas (#FFFFFF); organs drawn as simplified anatomically recognizable characters with tiny faces, stubby arms and expressive eyebrows; orthographic 2D, no gore, no realistic anatomy textures, no gradients, no 3D.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **6 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **30–40 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Fixed 4 organ mascots (Tim, Dạ Dày, Gan, Não) + Remotion timeline timers ('Sau 15 phút...', 'Sau 2 giờ...').

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Hành Trình 24 Giờ Bên Trong Cơ Thể Khi Bạn Thức Trắng Đêm: Tim, Gan Và Não Bộ Phải Gồng Gánh Ra Sao?*
- **Thời lượng:** 10 phút (24 cảnh Kawaii y học)
- **Câu mở đầu (Cold Open):** "Nếu tối nay bạn quyết định thức trắng để cày phim hoặc chạy deadline, đây là cuộc họp khẩn cấp diễn ra ngay bên trong não và tim bạn lúc 2 giờ sáng."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *Dạ dày than phiền gì khi bạn ăn mì gói lúc 11 giờ đêm?* (35s)
- **Spin-off #2 (0 ảnh mới):** *Điều gì xảy ra trong não khi bạn bấm 'Ngủ nướng thêm 10 phút' liên tục?* (35s)
- **Spin-off #3 (0 ảnh mới):** *Một ca làm việc quá tải của lá gan sau ly nước ngọt khổng lồ.* (40s)
- **Fast-Short #4 (6 ảnh Flow):** *Vì sao cúi đầu nhìn điện thoại làm đốt sống cổ gánh sức nặng 27 kg?* (35s)

### Backlog chủ đề hạt giống tiếp theo
- Điều gì xảy ra khi bạn nhịn ăn sáng 1 tháng
- Dạ dày nói gì khi bạn ăn khuya
- Một ngày của lá gan sau bữa nhậu
- Vì sao ngồi lâu làm đau lưng
- Uống nước đá có thật sự hại không

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#suckhoe #cothe #songkhoe #bacsi #learnontiktok`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate đồ gia dụng sức khỏe (không tuyên bố chữa bệnh), Booking
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-co-the-ke
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel co_the_ke
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
