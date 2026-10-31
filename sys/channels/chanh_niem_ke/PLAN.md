# KẾ HOẠCH CHI TIẾT KÊNH: CHÁNH NIỆM KỂ (`chanh_niem_ke`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `chanh_niem_ke` (Đợt triển khai: Wave 3)
- **Nhánh GitHub độc lập:** `channel/chanh-niem-ke` (`origin/channel/chanh-niem-ke`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-chanh-niem-ke`
- **Ngách nội dung:** Triết lý Phật giáo ứng dụng, Chánh niệm (Mindfulness) và tâm lý học buông bỏ trong đời sống hiện đại
- **Lời hứa thương hiệu (Value Proposition):** Một tích truyện Thiền và bài học Chánh niệm giúp bạn lắng dịu tâm trí, chuyển hóa khổ đau trong 60 giây.
- **Khán giả mục tiêu:** Người đi làm căng thẳng, người muốn tìm sự bình an nội tâm và hiểu đúng triết lý Phật học nguyên thủy
- **Nhân vật dẫn chuyện (Persona):** Người kể chuyện nhà Thiền điềm đạm, giải thích Phật pháp bằng tâm lý học gần gũi, không mê tín
- **Giọng văn (Tone):** Trầm ấm, từ bi, tĩnh tại, sâu sắc, chữa lành | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–16 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Kinh Pháp Cú (Dhammapada)** (Book/Scripture): Kho ẩn dụ gốc: Mũi tên thứ hai, Chiếc thuyền rỗng, Con voi bị thuần hóa.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Làng Mai (Plum Village)** (YouTube): Kể chuyện đời thường dịu dàng, dùng ẩn dụ hạt giống tâm và hơi thở để chuyển hóa cơn giận, lo âu.
- **Doug's Dharma** (YouTube): Giải thích Phật học nguyên thủy (Tứ Diệu Đế, Mũi tên thứ hai, Vô thường) khách quan, rõ ràng cho người hiện đại.
- **Einzelgänger (Buddhism & Zen Series)** (YouTube): Mở đầu bằng tích truyện Thiền ngắn 15s rồi phân tích tâm lý học ứng dụng sâu sắc.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mở đầu bằng một tích truyện Thiền ngắn hoặc nỗi bất an tâm lý đời thường trong 3 giây.
- Dùng ẩn dụ mũi tên thứ hai hoặc hạt giống tâm để giải thích cơ chế khổ đau.
- Không mê tín dị đoan, không cầu xin ban phước; tập trung vào sự quán chiếu và buông bỏ của tự tâm.
- Kết thúc bằng 1 bài tập thở hoặc câu hỏi quán chiếu giúp an trú trong hiện tại.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Vì sao bạn càng cố xua đuổi [cơn giận/lo âu] thì nó lại càng lớn lên?`
- `Mũi tên thứ hai: bí mật Phật học giúp bạn thoát khỏi 90% nỗi khổ cuộc đời.`
- `Câu chuyện chiếc thuyền rỗng: vì sao bạn tức giận khi bị người khác va vào?`
- `Khi tâm trí quá tải lúc nửa đêm, hãy thử dừng lại và làm điều này.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: bạn đang vướng bận điều gì? Thở một hơi thật sâu và buông xuống nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi tích truyện Thiền và bài tập chánh niệm tiếp theo.
### Điều cấm kỵ (Avoid)
- Mê tín dị đoan hoặc cúng bái giải hạn
- Giáo điều tôn giáo áp đặt
- Phán xét nghiệp chướng của người khác

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_zen_sumie` — Tranh thủy mặc Sumi-e thiền định: mực tàu trên giấy xuyến chỉ, khoảng lặng tĩnh tại
- **Bảng màu khóa cứng:** `#F5EFE0`, `#1C1C1C`, `#5F7A61`, `#D98A76`, `#8C7A6B`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Peaceful minimalist brush-painted Zen practitioner with gentle facial contours, calm closed eyes, and flowing bamboo-sage linen robe
- **Trang phục (`DEFAULT_OUTFIT`):** Flowing unadorned bamboo-sage (#5F7A61) linen robe with wide sleeves, zero shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Serene Zen monk meditating near ink-wash ripples + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Serene 2D East-Asian Sumi-e ink-wash painting on handmade Xuan rice paper canvas (#F5EFE0 warm textured rice paper, #1C1C1C expressive calligraphy brush ink, #5F7A61 bamboo sage wash, #D98A76 soft lotus blush, #8C7A6B tea-earth) with generous meditative negative space, water ripples and swaying bamboo strokes; orthographic 2D, at least 65% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Lotus ripples and two-arrows animations handled via Remotion kinetic SVG layers.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Ẩn Dụ Mũi Tên Thứ Hai: Vì Sao Nỗi Đau Là Bắt Buộc Nhưng Khổ Đau Là Tự Chọn? (Thiền Phật Giáo Ứng Dụng)*
- **Thời lượng:** 12 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Khi một chuyện tồi tệ xảy ra, nỗi đau thực tế chỉ là mũi tên thứ nhất, chính cách tâm trí bạn suy diễn mới là mũi tên thứ hai gây ra đau khổ."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *lắng dịu tâm trí* (45s)
- **Spin-off #2 (0 ảnh mới):** *Khi cơn giận bốc lên: cách ôm ấp tâm mình theo tinh thần Thiền sư Thích Nhất Hạnh.* (40s)
- **Spin-off #3 (0 ảnh mới):** *Câu chuyện chiếc thuyền rỗng: vì sao ta luôn giận người khác dù họ vô tình?* (45s)
- **Fast-Short #4 (5 ảnh Flow):** *Nghệ thuật dừng lại 3 hơi thở khi tâm trí quá tải giữa đêm.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- lắng dịu tâm trí
- Ẩn Dụ Mũi Tên Thứ Hai: Vì Sao Nỗi Đau Là Bắt Buộc Nhưng Khổ Đau Là Tự Chọn?
- Khi Cơn Giận Bốc Lên: Cách Ôm Ấp Tâm Mình Theo Tinh Thần Thiền Sư Thích Nhất Hạnh
- Câu Chuyện Chiếc Thuyền Rỗng: Vì Sao Ta Luôn Giận Người Khác Dù Họ Vô Tình?
- Hiểu Đúng Về Chữ Duyên Và Chữ Nghiệp Để Không Tự Dằn Vặt Quá Khứ
- Nghệ Thuật Dừng Lại 3 Hơi Thở Khi Tâm Trí Quá Tải Giữa Đêm

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#chanhniemke #phatgiaoungdung #thien #buongbo #chualanh`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate sách chánh niệm & chuông xoay, Khóa thiền tĩnh tâm
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-chanh-niem-ke
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel chanh_niem_ke
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
