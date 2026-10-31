# KẾ HOẠCH CHI TIẾT KÊNH: LỜI SÁNG SOI (`loi_sang_soi`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `loi_sang_soi` (Đợt triển khai: Wave 3)
- **Nhánh GitHub độc lập:** `channel/loi-sang-soi` (`origin/channel/loi-sang-soi`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-loi-sang-soi`
- **Ngách nội dung:** Dụ ngôn Kinh Thánh, lịch sử văn minh Kitô giáo và bài học yêu thương - tha thứ - hy vọng trong đời sống
- **Lời hứa thương hiệu (Value Proposition):** Giải mã một Dụ ngôn Kinh Thánh hoặc câu chuyện đức tin vượt thời gian bằng nét vẽ 2D trực quan, ấm áp.
- **Khán giả mục tiêu:** Người Công giáo, Tin Lành và mọi khán giả yêu thích triết lý nhân văn, lịch sử Kinh Thánh và sự nâng đỡ tâm hồn
- **Nhân vật dẫn chuyện (Persona):** Người kể chuyện Dụ ngôn gần gũi, truyền tải thông điệp ánh sáng, lòng bao dung và hy vọng
- **Giọng văn (Tone):** Ấm áp, nhân văn, tôn trọng lịch sử - kinh điển, truyền hy vọng | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–16 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **IMBeggar** (YouTube): Phong cách stickman/doodle tối giản giải thích các câu hỏi lớn về đức tin, sự tha thứ và lòng khiêm nhường.
- **Sách Châm Ngôn & Tân Ước** (Book/Scripture): Nguồn tích truyện gốc: Dụ ngôn Nén Bạc, Người Con Hoang Đàng, Người Samari Nhân Lành, Hạt Cải.
### Kênh mẫu YouTube Long (`long_16x9`)
- **BibleProject** (YouTube): Chuẩn vàng thế giới về vẽ 2D sketch giải thích Dụ ngôn Kinh Thánh, lịch sử và từ khóa Ân điển, Tình yêu thương.
- **Ascension Presents** (YouTube): Kết nối các dụ ngôn cổ xưa với khủng hoảng thực tế của con người hiện đại (cô đơn, thất bại, tha thứ).

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mở đầu bằng một Dụ ngôn cổ xưa đặt trong bối cảnh đời sống hiện đại.
- Nhấn mạnh giá trị nhân văn phổ quát: tha thứ, ân điển, tình yêu thương và sự khiêm nhường.
- Tôn trọng lịch sử và văn bản gốc; không tranh luận thần học giáo phái.
- Kết thúc bằng thông điệp nâng đỡ tâm hồn, thắp lên hy vọng cho người đang bế tắc.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Dụ ngôn 2000 năm trước giải thích vì sao bạn càng [hành vi] lại càng [kết quả]?`
- `Vì sao tha thứ cho kẻ làm tổn thương bạn lại là món quà dành cho chính bạn?`
- `Hạt cải nhỏ bé nhất: nghịch lý về niềm tin làm thay đổi toàn bộ số phận.`
- `Bài học quản trị cuộc đời từ Dụ ngôn Nén Bạc mà người hiện đại nên biết.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: bạn thấy bài học nào chạm vào lòng mình nhất? Bình luận nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi câu chuyện Dụ ngôn tiếp theo về lòng bao dung.
### Điều cấm kỵ (Avoid)
- Tranh cãi giáo phái Kitô giáo
- Lên án hay đe dọa trừng phạt
- Giải nghĩa sai lệch văn cảnh lịch sử Kinh Thánh

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_parable_woodcut` — Tranh khắc gỗ dụ ngôn: phong cách BibleProject, đường khắc thô mộc trên nền giấy cổ
- **Bảng màu khóa cứng:** `#EFE4C8`, `#1E1E1E`, `#D9A520`, `#5E7D3A`, `#9E3B33`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Dignified woodcut human storyteller in woven indigo and ochre cloak holding a warm glowing clay oil lamp
- **Trang phục (`DEFAULT_OUTFIT`):** Woven indigo tunic under draped terracotta and ochre cloak, carved woodcut texture, no modern clothing
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Woodcut storyteller holding radiant oil lamp in dark + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Bold BibleProject-inspired 2D carved linocut and woodblock parable print on aged parchment canvas (#EFE4C8 antique parchment, #1E1E1E carved woodcut ink outlines, #D9A520 radiant oil-lamp gold, #5E7D3A olive-branch green, #9E3B33 terracotta clay); expressive relief cuts, olive groves and radiant lanterns; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Warm parchment scrolls and glowing lantern rays animated in Remotion reduce Flow prompts.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Dụ Ngôn Nén Bạc: Bài Học Quản Trị Cuộc Đời & Nghệ Thuật Tha Thứ Để Giải Thoát Cho Chính Mình*
- **Thời lượng:** 12 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Dụ ngôn về những nén bạc cách đây 2000 năm không chỉ là câu chuyện đức tin, mà là bài học kinh điển về cách đầu tư cuộc đời mình."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *tha thứ bao dung* (45s)
- **Spin-off #2 (0 ảnh mới):** *Vì sao tha thứ cho người làm tổn thương mình lại là giải thoát cho chính ta?* (40s)
- **Spin-off #3 (0 ảnh mới):** *Dụ ngôn người con hoang đàng: khi nào cánh cửa bao dung vẫn mở đợi bạn về?* (45s)
- **Fast-Short #4 (5 ảnh Flow):** *5 lời khuyên về tiền bạc và sự khôn ngoan trong sách Châm Ngôn Salômôn.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- tha thứ bao dung
- Dụ Ngôn Nén Bạc: Bài Học Quản Trị Cuộc Đời Từ Câu Chuyện 2000 Năm Trước
- Vì Sao Tha Thứ Cho Người Làm Tổn Thương Mình Lại Là Giải Thoát Cho Chính Ta?
- Dụ Ngôn Người Con Hoang Đàng: Khi Nào Cánh Cửa Bao Dung Vẫn Mở Đợi Bạn Về?
- 5 Lời Khuyên Về Tiền Bạc Và Sự Khôn Ngoan Trong Sách Châm Ngôn Salômôn
- Câu Chuyện David Và Goliath: Cách Chiến Thắng Những Gã Khổng Lồ Mang Tên Sợ Hãi

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#loisangsoi #dungonkinhthanh #chualanh #baihoccuocsong #kienthuc`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate sách hạt giống tâm hồn & văn hóa lịch sử, Ủng hộ thiện nguyện cộng đồng
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-loi-sang-soi
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel loi_sang_soi
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
