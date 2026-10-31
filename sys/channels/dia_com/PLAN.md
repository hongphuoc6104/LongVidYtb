# KẾ HOẠCH CHI TIẾT KÊNH: ĐĨA CƠM KHOA HỌC (`dia_com`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `dia_com` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/dia-com` (`origin/channel/dia-com`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-dia-com`
- **Ngách nội dung:** Hóa học ẩm thực, an toàn thực phẩm và khoa học trong căn bếp Việt
- **Lời hứa thương hiệu (Value Proposition):** Hiểu đúng từng phản ứng hóa học trong mâm cơm hàng ngày để ăn ngon và lành.
- **Khán giả mục tiêu:** Người nấu ăn gia đình, nhân viên văn phòng, người quan tâm sức khỏe ăn uống
- **Nhân vật dẫn chuyện (Persona):** Đầu bếp mê hóa học, giải thích chuyện bếp núc bằng thực nghiệm vui vẻ
- **Giọng văn (Tone):** Gần gũi, thực tế, khoa học rõ ràng, không hù dọa vô căn cứ | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 40–55s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–14 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Nhiệt Kế Ẩm Thực** (TikTok): Everyday kitchen chemistry myths busted in 60 seconds.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Ann Reardon (How To Cook That)** (YouTube): Debunking viral food hacks with verified food science experiments.
- **Hóa Học Ẩm Thực (On Food and Cooking - Harold McGee)** (Book/Scripture): Kinh thánh khoa học ẩm thực thế giới về cơ chế phân tử trong nhiệt độ, chất béo và gia vị.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Bắt đầu bằng một thói quen nấu nướng hoặc niềm tin ẩm thực quen thuộc trong mâm cơm Việt.
- Giải thích phản ứng hóa học bằng hình vẽ ẩn dụ phân tử 2D cực kỳ dễ hiểu.
- Tuyệt đối không hù dọa ung thư vô căn cứ; đưa ra khoảng liều lượng và nhiệt độ an toàn.
- Kết thúc bằng 1 mẹo bếp núc ứng dụng được ngay tối nay.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Vì sao [món ăn/thói quen bếp] tưởng vô hại lại biến chất ở [nhiệt độ]?`
- `Khoa học giải thích vì sao mẹ bạn luôn [thói quen nấu ăn] đúng đến kinh ngạc.`
- `Bí mật hóa học đằng sau miếng thịt kho tàu mềm rục mà không nát.`
- `Đừng [thói quen rã đông/bảo quản] kiểu này nếu không muốn vi khuẩn nhân đôi.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: nhà bạn có hay làm cách này không? Bình luận chia sẻ nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi thực đơn khoa học tiếp theo cho bữa cơm gia đình.
### Điều cấm kỵ (Avoid)
- Hù dọa ung thư giật gân (fear-mongering)
- Lời khuyên dinh dưỡng cực đoan
- Bác bỏ y học chính thống

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_culinary_mascots` — Sticker-pop ẩm thực: linh vật Bé Gạo, Bé Lửa và phân tử dinh dưỡng viền trắng nổi
- **Bảng màu khóa cứng:** `#FFFDF7`, `#FF6B6B`, `#FFD166`, `#06D6A0`, `#26547C`, `#FFFFFF`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Adorable recurring personified kitchen mascots led by Bé Gạo (plump white rice-grain character with rosy cheeks and tiny chef toque), Bé Lửa (cheerful kitchen flame sprite), and expressive amino and sugar molecule buddies with full rounded mascot anatomy and expressive faces
- **Trang phục (`DEFAULT_OUTFIT`):** Tiny white chef toque and red bandana on Bé Gạo; cheerful golden flame contour for Bé Lửa
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Expressive Bé Gạo mascot with food chemical reaction + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Bold 2D kawaii culinary sticker-pop illustration on warm porcelain white canvas (#FFFDF7 warm porcelain white canvas, #FF6B6B chili coral, #FFD166 egg-yolk gold, #06D6A0 herb mint, #26547C cast-iron navy) with smooth dark outlines and chunky white sticker borders; expressive culinary ingredients, kitchen utensils and nutritional molecules; orthographic 2D, at least 60% clean negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **35%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **6 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **8–12 phút** cho 1 TikTok Short độc lập; **35–45 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Kitchen props & flat 2D temperature gauges in Remotion kinetic motion reduce image generation needs.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Hóa Học Trong Mâm Cơm Việt: 5 Bí Quyết Nấu Ăn Ngon & 4 Sai Lầm An Toàn Thực Phẩm Thường Gặp*
- **Thời lượng:** 11 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Ai cũng nghĩ rã đông thịt bằng nước nóng cho nhanh, nhưng bạn có biết vi khuẩn đang nhân đôi sau mỗi 20 phút ở nhiệt độ ấm?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *nấu ăn tại nhà* (45s)
- **Spin-off #2 (0 ảnh mới):** *Vì sao rã đông thịt bằng nước nóng là sai lầm nguy hiểm cho sức khỏe?* (40s)
- **Spin-off #3 (0 ảnh mới):** *Hóa học của nồi nước dùng phở trong veo không bị đục ngầu.* (45s)
- **Fast-Short #4 (6 ảnh Flow):** *Cơm nguội hâm lại: cách bảo quản đúng để không sinh độc tố vi khuẩn.* (45s)

### Backlog chủ đề hạt giống tiếp theo
- nấu ăn tại nhà
- Phản ứng Maillard: bí quyết để thịt áp chảo dậy mùi thơm nức mũi
- Vì sao rã đông thịt bằng nước nóng là sai lầm nguy hiểm
- Hóa học của nồi nước dùng phở trong veo không bị đục
- Cơm nguội hâm lại: cách bảo quản đúng để không sinh độc tố

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#diacomkhoahoc #antoanthucpham #khoahocnhabep #suckhoe #kienthuc`
- **Nguồn doanh thu:** YouTube AdSense, Sponsor thiết bị bếp / đồ gia dụng lành mạnh, Affiliate sách ẩm thực & dinh dưỡng
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-dia-com
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel dia_com
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
