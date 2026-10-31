# KẾ HOẠCH CHI TIẾT KÊNH: MINH TRIẾT SỐNG (`minh_triet_song`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `minh_triet_song` (Đợt triển khai: Wave 3)
- **Nhánh GitHub độc lập:** `channel/minh-triet-song` (`origin/channel/minh-triet-song`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-minh-triet-song`
- **Ngách nội dung:** Minh triết Phương Đông (Lão Tử, Trang Tử) kết hợp Chủ nghĩa Khắc kỷ (Stoicism) giúp giữ tâm bất biến
- **Lời hứa thương hiệu (Value Proposition):** Một nguyên lý cổ xưa từ Lão Trang hoặc Khắc kỷ giúp bạn điềm tĩnh trước mọi biến cố đời thường.
- **Khán giả mục tiêu:** Người trưởng thành, người làm quản lý, người tìm kiếm bản lĩnh nội tâm và triết học ứng dụng
- **Nhân vật dẫn chuyện (Persona):** Người bạn triết gia bình dị, đúc kết tinh hoa Đông - Tây thành nguyên tắc sống thực tế
- **Giọng văn (Tone):** Điềm tĩnh, sâu sắc, khúc chiết, bản lĩnh | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–16 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Daily Stoic** (YouTube): Mở đầu bằng nghịch lý cảm xúc đời thường rồi giải quyết bằng vòng tròn kiểm soát Khắc kỷ.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Einzelgänger (Taoism & Stoicism)** (YouTube): Kết hợp triết lý Vô Vi (Wu Wei) của Lão Tử và Khắc kỷ của Marcus Aurelius bằng cấu trúc 3 chương mạch lạc.
- **Tủ sách Thu Giang Nguyễn Duy Cần** (Book/Scripture): Chuẩn mực diễn giải triết học Đông phương sang tiếng Việt giản dị, sâu sắc.
- **The School of Life** (YouTube): Emotional philosophy and philosophical practical lessons.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mở đầu bằng một nghịch lý cuộc sống hoặc áp lực ganh đua thường nhật.
- Đối chiếu góc nhìn Vô Vi (Lão Tử) và Vòng tròn kiểm soát (Khắc kỷ).
- Không nói đạo lý sáo rỗng; tập trung vào hành động làm chủ tâm thức.
- Kết thúc bằng 1 thái độ sống giúp đứng vững trước thị phi và biến cố.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Vì sao người càng tranh giành lại càng dễ mất mát, người buông tay lại có tất cả?`
- `Hoàng đế La Mã Marcus Aurelius đã làm gì khi bị thuộc cấp phản bội?`
- `Quy luật con ngựa của Tái Ông: vì sao xui xẻo hôm nay lại là phúc lành ngày mai?`
- `Cái dũng của người điềm tĩnh: tại sao im lặng lại có sức mạnh hơn vạn lời cãi vã?`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: bạn chọn cách buông bỏ hay đối đầu? Chia sẻ góc nhìn nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi bài học minh triết tiếp theo về nghệ thuật sống an nhiên.
### Điều cấm kỵ (Avoid)
- Triết lý bi quan, yếm thế lánh đời
- Lý thuyết triết học hàn lâm khó hiểu
- Đạo lý suông thiếu ứng dụng thực tế

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_stoic_ink_scroll` — Cuộn thư triết học cổ điển: nét cọ phương Đông kết hợp cột đá Khắc kỷ phương Tây
- **Bảng màu khóa cứng:** `#F2E9D8`, `#222831`, `#4F6D5A`, `#C08552`, `#E8D8C8`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Composed bearded philosopher sage drawn in refined classical ink lines wearing a draped slate-and-linen tunic
- **Trang phục (`DEFAULT_OUTFIT`):** Draped slate-charcoal and unbleached linen philosopher tunic with a simple leather sash, no modern details
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Composed philosopher standing calmly beside marble column + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Timeless 2D brush-and-chisel philosophical scroll illustration on aged silk-scroll cream canvas (#F2E9D8 aged silk-scroll cream, #222831 charcoal ink, #4F6D5A pine-jade green, #C08552 warm bronze-ochre) blending Eastern bamboo brushwork with crisp classical marble colonnades and stone stelae; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Bamboo sway and Stoic dichotomy-of-control rings animated directly in Remotion.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Triết Lý Vô Vi Của Lão Tử & Bản Lĩnh Khắc Kỷ: Giữ Tâm Bất Biến Giữa Dòng Đời Vạn Biến*
- **Thời lượng:** 13 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Càng cố nắm chặt một nắm cát thì cát càng chảy qua kẽ tay: triết lý Vô Vi của Lão Tử giúp bạn làm chủ nghịch lý cuộc đời ra sao?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *giữ tâm điềm tĩnh* (45s)
- **Spin-off #2 (0 ảnh mới):** *Cái dũng của người điềm tĩnh: khi im lặng mạnh hơn vạn lời tranh cãi.* (40s)
- **Spin-off #3 (0 ảnh mới):** *Định luật con ngựa của Tái Ông: vì sao xui xẻo hôm nay có thể là may mắn ngày mai?* (45s)
- **Fast-Short #4 (5 ảnh Flow):** *Cách tách biệt thứ kiểm soát được và thứ phải buông bỏ theo triết học Khắc kỷ.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- giữ tâm điềm tĩnh
- Triết Lý Vô Vi Của Lão Tử: Vì Sao Càng Cố Cưỡng Cầu Mọi Thứ Càng Vỡ Vụn?
- Cái Dũng Của Người Điềm Tĩnh: Khi Im Lặng Mạnh Hơn Vạn Lời Tranh Cãi
- Định Luật Con Ngựa Của Tái Ông: Vì Sao Xui Xẻo Hôm Nay Có Thể Là May Mắn Ngày Mai?
- Bài Học Của Hoàng Đế Marcus Aurelius Khi Đối Mặt Với Kẻ Phản Bội Và Thị Phi
- Cách Tách Biệt Thứ Kiểm Soát Được Và Thứ Phải Buông Bỏ Theo Triết Học Khắc Kỷ

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#minhtrietsong #khacky #laotu #triethocungdung #binhtam`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate sách triết học ứng dụng, Khóa học tâm lý bản lĩnh lãnh đạo
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-minh-triet-song
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel minh_triet_song
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
