# KẾ HOẠCH CHI TIẾT KÊNH: TÂM TĨNH ĐÊM (`tam_tinh_dem`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `tam_tinh_dem` (Đợt triển khai: Wave 3)
- **Nhánh GitHub độc lập:** `channel/tam-tinh-dem` (`origin/channel/tam-tinh-dem`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-tam-tinh-dem`
- **Ngách nội dung:** Truyện ngụ ngôn tỉnh thức, bài học nhân quả, lòng biết ơn và chiêm nghiệm chữa lành trước khi ngủ
- **Lời hứa thương hiệu (Value Proposition):** Một câu chuyện ngụ ngôn lắng đọng mỗi tối giúp bạn gác lại âu lo và ngủ thật bình yên.
- **Khán giả mục tiêu:** Khán giả nghe đêm (21h-24h), người cần chữa lành tổn thương, yêu thích truyện ngụ ngôn nhân sinh
- **Nhân vật dẫn chuyện (Persona):** Người kể chuyện đêm khuya ấm áp, thủ thỉ những bài học nhân sinh sâu sắc
- **Giọng văn (Tone):** Thủ thỉ, lắng đọng, giàu cảm xúc, nhân văn | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–16 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Hạt Giống Tâm Hồn** (YouTube): Chạm đúng tâm lý người Việt về tình thân, nhân quả, áp lực mưu sinh và sự tử tế.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Dare to do. Motivation** (YouTube): Kể chuyện ngụ ngôn Zen/Cổ tích cho người lớn với nhịp độ lắng đọng, đúc kết bài học nhân sinh ở 2 phút cuối.
- **Hiểu Về Trái Tim (Minh Niệm)** (Book/Scripture): Nguồn cảm hứng phân tích tâm lý chữa lành, lòng biết ơn và luật nhân quả đời thường.
- **Web5ngay** (YouTube): Bài học nhân sinh đời thường thủ thỉ, sâu lắng.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mở đầu bằng không gian đêm yên ắng và một tình huống ngụ ngôn chạm đến cảm xúc.
- Nhịp kể chậm rãi, từ tốn; từng câu đều mang hơi thở chữa lành và vỗ về tâm hồn.
- Kết nối ngụ ngôn với lòng biết ơn cha mẹ, tình thân, sự tha thứ cho chính mình.
- Kết thúc bằng lời chúc ngủ ngon an yên, nhắc nhở gác lại muộn phiền của ngày hôm nay.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Đêm nay trước khi nhắm mắt, có một câu chuyện ngắn mình muốn kể cho bạn nghe.`
- `Bài học từ chiếc bình nứt: vì sao những khiếm khuyết của bạn lại tạo nên điều kỳ diệu?`
- `Ba chiếc sàng của Socrates: điều bạn sắp nghe có thật sự đáng để bận lòng?`
- `Vì sao chúng ta luôn bao dung với người ngoài nhưng lại khắt khe với người thương nhất?`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Gửi lời chúc: Đêm nay hãy ngủ thật ngon nhé, ngày mai sẽ là một ngày mới dịu dàng.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi câu chuyện ngụ ngôn chữa lành tiếp theo trước giờ đi ngủ.
### Điều cấm kỵ (Avoid)
- Nội dung kinh dị hay gây giật mình ban đêm
- Giọng điệu chỉ trích nặng nề
- Kịch tính hóa xung đột gây khó ngủ

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_midnight_gouache` — Màu bột gouache đêm ấm áp: phong cách Hoàng Tử Bé, bầu trời đêm nhung và trăng vàng
- **Bảng màu khóa cứng:** `#1B263B`, `#F4D35E`, `#E09F7D`, `#778DA9`, `#F8F4E3`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Gentle storybook traveler with tousled dark hair and a warm golden-amber knitted scarf holding a steaming ceramic teacup under starry night skies
- **Trang phục (`DEFAULT_OUTFIT`):** Cozy midnight-blue woolen coat with long warm golden-amber (#F4D35E) knitted scarf, zero shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Gentle traveler sitting under starry crescent moon + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Cozy Little Prince-inspired 2D flat matte gouache night-storybook illustration on velvety midnight indigo sky canvas (#1B263B velvety midnight indigo sky, #F4D35E warm crescent-moon and lantern gold, #E09F7D cozy amber tea glow, #778DA9 misty starlight blue, #F8F4E3 soft cream) with soft painterly edges, constellations and peaceful bedtime scenes; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Gentle floating lantern and moon glow transitions created via Remotion filters.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Gác Lại Âu Lo Trước Khi Ngủ: 3 Câu Chuyện Ngụ Ngôn Nhân Sinh Giúp Bạn Ngủ Thật Bình An*
- **Thời lượng:** 14 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Đêm nay trước khi nhắm mắt ngủ, có một câu chuyện ngắn về chiếc bình nứt và những đóa hoa nở rộ bên đường mình muốn gửi đến bạn."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *nghĩ về lòng biết ơn* (45s)
- **Spin-off #2 (0 ảnh mới):** *Ba chiếc sàng của Socrates: quy tắc lọc lời đồn trước khi để tâm trí tổn thương.* (40s)
- **Spin-off #3 (0 ảnh mới):** *Câu chuyện chiếc bình nứt và bài học chấp nhận những khiếm khuyết của chính mình.* (45s)
- **Fast-Short #4 (5 ảnh Flow):** *Trước khi đi ngủ đêm nay: 3 thứ cần đặt xuống để sáng mai thức dậy nhẹ lòng.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- nghĩ về lòng biết ơn
- Ba Chiếc Sàng Của Socrates: Quy Tắc Lọc Lời Đồn Trước Khi Để Tâm Trí Bị Tổn Thương
- Chiếc Bình Nứt Và Bài Học Chấp Nhận Những Khiếm Khuyết Của Chính Mình
- Câu Chuyện Bát Mì Đêm Mưa: Vì Sao Ta Hay Tử Tế Với Người Lạ Nhưng Gắt Gỏng Với Người Thân?
- Luật Nhân Quả Trong Lời Nói: Một Câu Nói Ấm Áp Có Thể Cứu Một Ngày Tồi Tệ Ra Sao?
- Trước Khi Đi Ngủ Đêm Nay: 3 Thứ Cần Đặt Xuống Để Sáng Mai Thức Dậy Nhẹ Lòng

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#tamtinhdem #truyenngungon #nhansinh #chualanhtamhon #binhyen`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate trà thảo mộc & nến thơm, Sách nói chiêm nghiệm đêm
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-tam-tinh-dem
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel tam_tinh_dem
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
