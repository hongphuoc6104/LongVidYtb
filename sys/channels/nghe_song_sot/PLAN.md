# KẾ HOẠCH CHI TIẾT KÊNH: NGHỀ SỐNG SÓT (`nghe_song_sot`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `nghe_song_sot` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/nghe-song-sot` (`origin/channel/nghe-song-sot`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-nghe-song-sot`
- **Ngách nội dung:** Chiến lược sự nghiệp, quy luật ngầm chốn công sở và thích nghi thời đại AI
- **Lời hứa thương hiệu (Value Proposition):** Hiểu luật chơi thật sự của thị trường lao động để không bao giờ bị đào thải.
- **Khán giả mục tiêu:** Nhân viên văn phòng, sinh viên mới ra trường, quản lý cấp trung
- **Nhân vật dẫn chuyện (Persona):** Đàn anh đi làm 10 năm nói thẳng sự thật công sở không màu hồng
- **Giọng văn (Tone):** Thẳng thắn, thực tế, định hướng giải pháp nâng cấp giá trị bản thân | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–15 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **An Is Here** (TikTok): Direct, grounded workplace survival insights for Vietnamese corporate youth.
### Kênh mẫu YouTube Long (`long_16x9`)
- **The Futur (Chris Do)** (YouTube): Negotiation tactics and career value proposition frameworks.
- **Kỹ Năng Đàm Phán & Thăng Tiến Chốn Công Sở** (Book/Scripture): Nguyên tắc xây dựng giá trị cốt lõi không thể thay thế và thiết lập ranh giới nghề nghiệp.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mở đầu bằng một sự thật trần trụi chốn công sở mà trường học không bao giờ dạy.
- Nói thẳng nhưng mang tính xây dựng; không than vãn, tập trung vào đòn bẩy kỹ năng.
- Mọi lời khuyên đều phải giúp người xem tăng vị thế đàm phán lương và thăng tiến.
- Kết thúc bằng 1 hành động cụ thể có thể làm ngay vào sáng thứ Hai.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Người chăm chỉ nhất công ty thường là người dễ bị thay thế nhất: vì sao?`
- `3 dấu hiệu công ty sắp thanh lọc nhân sự mà bạn cần nhận ra trước 3 tháng.`
- `Đừng bao giờ nói câu này khi sếp hỏi: 'Em thấy dạo này công việc thế nào?'`
- `Quy luật ngầm tăng lương 50%: không phải làm thêm giờ, mà là nắm mắt xích này.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: công ty bạn có như vậy không? Bình luận chia sẻ nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi chiến lược sự nghiệp dài hạn tiếp theo.
### Điều cấm kỵ (Avoid)
- Lời khuyên độc hại: xúi giục phản bội đồng nghiệp
- Khoe khoang thành tích cá nhân
- Ru ngủ bằng những lời khuyên tích cực hời hợt

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_career_doodle` — Doodle công sở: stickman + bậc thang sự nghiệp/bàn cờ 2D tối giản
- **Bảng màu khóa cứng:** `#F8F0DC`, `#3B82C4`, `#F2B88B`, `#93A88C`, `#FFFFFF`, `#000000`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Iconic 2D Vietnamese indie webcomic doodle stickman (Nguệch Ngoạc / Vẽ Vời / Xấu Vê Nờ style): oversized slightly lopsided hand-drawn pure-white (#FFFFFF) bald circle head with bold pitch-black (#000000) marker outline, tiny solid-black dot eyes placed low on the face leaving a large open upper forehead/cranium, minimal single-stroke eyebrows and mouth, no nose or ears, thin single-line solid-black wire/stick arms (single black stroke with zero arm thickness) ending in small round white circle hands
- **Trang phục (`DEFAULT_OUTFIT`):** Flat royal-blue (#3B82C4) shirt with simple ID lanyard, no shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Stickman choosing leverage lever over endless stairs + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Hand-drawn 2D career strategy doodle explainer illustration: wobbly black marker outlines (#000000), flat unshaded fills in warm office cream (#F8F0DC), royal blue (#3B82C4), coral accent (#F2B88B), sage green (#93A88C) and white (#FFFFFF) on a flat solid cream canvas (#F8F0DC); simple flat 2D career ladders, office desks, lever metaphors and stickman with lanyard; orthographic 2D, at least 60% empty negative space, no 3D, no gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **35%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **6 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **8–11 phút** cho 1 TikTok Short độc lập; **32–42 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Desk props & leverage ladder metaphors in Remotion motion reduce need for complex Flow variations.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Quy Luật Ngầm Chốn Công Sở: Chiến Lược Nâng Cao Vị Thế & Đàm Phán Lương Không Bao Giờ Lép Vế*
- **Thời lượng:** 12 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Người chăm chỉ nhất công ty thường là người dễ bị thay thế nhất, nếu bạn không nắm được đòn bẩy giá trị mà sếp thật sự cần."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *đi làm chăm chỉ* (45s)
- **Spin-off #2 (0 ảnh mới):** *3 dấu hiệu công ty sắp thanh lọc nhân sự mà bạn cần nhận ra trước 3 tháng.* (45s)
- **Spin-off #3 (0 ảnh mới):** *Cách nói chuyện với sếp khó tính mà không bị mất lòng hay lép vế.* (45s)
- **Fast-Short #4 (6 ảnh Flow):** *Quy luật ngầm tăng lương: không phải làm thêm giờ, mà là nắm mắt xích này.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- đi làm chăm chỉ
- Bẫy thăng tiến: vì sao làm quản lý cấp trung là vị trí dễ kiệt sức nhất
- Cách nói chuyện với sếp khó tính mà không bị mất lòng hay lép vế
- Kỹ năng tạo đòn bẩy: làm sao để công việc tự chứng minh giá trị
- Khi nào nên nghỉ việc: 4 tín hiệu cho thấy công ty đã hết đất phát triển

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#nghesongsot #chuyencongso #kinhnghiemdilam #phattriensunghiep #kienthuc`
- **Nguồn doanh thu:** YouTube AdSense, Coaching 1-on-1 sự nghiệp, Khóa học đàm phán lương và giao tiếp công sở
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-nghe-song-sot
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel nghe_song_sot
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
