# KẾ HOẠCH CHI TIẾT KÊNH: ỦA SAO VẬY? (`ua_sao_vay`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `ua_sao_vay` (Đợt triển khai: Wave 1)
- **Nhánh GitHub độc lập:** `channel/ua-sao-vay` (`origin/channel/ua-sao-vay`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-ua-sao-vay`
- **Ngách nội dung:** Sự thật bất ngờ, khoa học gây tò mò
- **Lời hứa thương hiệu (Value Proposition):** Mỗi video trả lời một câu 'ủa sao vậy' trong chưa tới một phút.
- **Khán giả mục tiêu:** Học sinh, sinh viên, người lướt TikTok giải trí 13-30 tuổi
- **Nhân vật dẫn chuyện (Persona):** Linh vật 'Bé Ủa' tò mò, nói nhanh, hay há hốc mồm
- **Giọng văn (Tone):** Nhanh, dồn dập, hài kiểu Gen Z, có twist cuối | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 20–35s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Kiến Không Ngủ** (TikTok): Recurring mascot characters with personalities; Gen Z humor.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Kiến Thức Thú Vị** (YouTube): Hand-drawn visuals, calm logical narration, 'little-known secrets' angle.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- First sentence is the question itself, phrased like a friend asking 'ủa'.
- Give a wrong-but-common answer first, then flip it.
- Max 2 seconds per visual beat in the first 10 seconds.
- End on a second surprising fact to trigger rewatch/share.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Ủa, sao [hiện tượng quen thuộc] vậy?`
- `Ai cũng nghĩ [niềm tin phổ biến]. Sai bét.`
- `Điều gì xảy ra nếu [tình huống giả định]?`
- `[Vật quen thuộc] có một bí mật mà 99% người không để ý.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Tung thêm 1 sự thật bất ngờ, hỏi: bạn có biết không?
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open: the weirdest question of the episode
1. Compilation of 6-10 linked 'ủa sao vậy' questions
1. Each segment: question -> common wrong answer -> real answer -> visual proof
1. Running mascot gag between segments
1. Final mind-blowing fact + next episode tease
- **Câu kết (CTA):** Gợi video 'tổng hợp 10 câu ủa sao vậy' tiếp theo.
### Điều cấm kỵ (Avoid)
- Unverified viral myths
- Clickbait without payoff
- Pseudoscience

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_sticker_pop` — Sticker pop: hoạt hình màu nổi viền trắng dày, linh vật Bé Ủa
- **Bảng màu khóa cứng:** `#FFF6D6`, `#FFD23F`, `#FF6B6B`, `#2EC4B6`, `#7B2CBF`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Mascot 'Bé Ủa': a round lemon-yellow (#FFD23F) blob creature with huge white oval eyes, tiny black pupils, a wide open mouth, two short stubby arms and a single curly antenna shaped like a question mark
- **Trang phục (`DEFAULT_OUTFIT`):** No clothing; tiny coral (#FF6B6B) cheeks, chunky white sticker border
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Bé Ủa with open mouth next to the weird object + 2-3 word question in bold sticker letters.
- **Prompt Style gốc:**
  > Bold 2D sticker-pop cartoon illustration: thick smooth black outlines with a chunky white sticker border around every main object, saturated flat fills in lemon yellow (#FFD23F), coral (#FF6B6B), teal (#2EC4B6) and grape (#7B2CBF) on a single flat solid pastel background (#FFF6D6 or #DFF7F4); simple exaggerated proportions, big expressive eyes, comic motion lines and sparkle marks, orthographic 2D, no gradients, no realistic textures, no 3D.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **6 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **6–9 phút** cho 1 TikTok Short độc lập; **30–40 phút** cho trọn bộ (1 YouTube Long + 6 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** 1 YouTube Long = 6-8 modular question chapters -> slices directly into 6 TikTok Shorts with zero extra Flow images.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *8 Hiện Tượng Quen Thuộc Mỗi Ngày Nhưng 99% Chúng Ta Đều Hiểu Sai Bản Chất Khoa Học*
- **Thời lượng:** 10 phút (8 chương câu hỏi độc lập)
- **Câu mở đầu (Cold Open):** "Ai cũng nghĩ nước suối đóng chai có hạn sử dụng vì nước bị thiu, nhưng sự thật khoa học lại nằm ở một thứ hoàn toàn khác."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (Cắt thẳng Chương 1):** *Ủa, sao trong phòng có chục người mà muỗi chỉ đốt đúng một người?* (25s)
- **Spin-off #2 (Cắt thẳng Chương 2):** *Ủa, sao mình không bao giờ tự cù lét cho mình cười được?* (25s)
- **Spin-off #3 (Cắt thẳng Chương 3):** *Ủa, nước ngầm triệu năm không hỏng sao đóng chai lại có hạn sử dụng?* (30s)
- **Spin-off #4 (Cắt thẳng Chương 4):** *Ủa, sao ngủ nướng cuối tuần dậy lại đau đầu hơn ngày thường?* (28s)
- **Spin-off #5 (Cắt thẳng Chương 5):** *Ủa, sao nghe lại giọng ghi âm của chính mình ai cũng thấy kỳ cục?* (25s)

### Backlog chủ đề hạt giống tiếp theo
- Ủa, sao muỗi chỉ đốt một số người
- Ủa, sao dưa hấu ngâm nước lại nổi
- Ủa, sao mình không tự cù lét mình được
- Điều gì xảy ra nếu bạn không ngủ 3 ngày
- Ủa, sao chai nước suối có hạn sử dụng

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#uasaovay #kienthucthuvi #khoahoc #didyouknow #learnontiktok`
- **Nguồn doanh thu:** Tăng follow nhanh làm phễu, YouTube AdSense (compilation dài), Booking đồ chơi giáo dục
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-ua-sao-vay
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel ua_sao_vay
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
