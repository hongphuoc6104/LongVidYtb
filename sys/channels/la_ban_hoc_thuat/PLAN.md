# KẾ HOẠCH CHI TIẾT KÊNH: LA BÀN HỌC THUẬT (`la_ban_hoc_thuat`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `la_ban_hoc_thuat` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/la-ban-hoc-thuat` (`origin/channel/la-ban-hoc-thuat`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-la-ban-hoc-thuat`
- **Ngách nội dung:** Phương pháp tự học sâu, đọc hiểu tài liệu khoa học và nghiên cứu cho người mới
- **Lời hứa thương hiệu (Value Proposition):** Biến mọi tài liệu học thuật phức tạp thành quy trình từng bước ai cũng làm theo được.
- **Khán giả mục tiêu:** Sinh viên, học viên cao học, nhà nghiên cứu trẻ, người tự học chuyên sâu
- **Nhân vật dẫn chuyện (Persona):** Người hướng dẫn nghiên cứu tận tâm, giải nghĩa học thuật bằng tiếng Việt trong sáng
- **Giọng văn (Tone):** Chân phương, có hệ thống, truyền cảm hứng tự học và tư duy phản biện | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 11–16 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Tiến Sĩ Trẻ** (TikTok): Bite-sized research tips and academic writing templates for Vietnamese students.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Ali Abdaal** (YouTube): Evidence-based study techniques and active recall systems.
- **Kỹ Thuật Feynman & Cách Học Sâu (Deep Work - Cal Newport)** (Book/Scripture): Phương pháp tập trung sâu và chia nhỏ tài liệu phức tạp thành mô hình tư duy trực quan.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mở đầu bằng nỗi sợ hãi tài liệu học thuật dày đặc hoặc rào cản thuật ngữ tiếng Anh.
- Phá vỡ bài báo khoa học thành 3 câu hỏi cốt lõi: Vấn đề gì? Phương pháp nào? Kết quả ra sao?
- Luôn minh họa bằng kỹ thuật Feynman: giải thích cho một đứa trẻ 10 tuổi cũng hiểu.
- Kết thúc bằng 1 công cụ tra cứu hoặc quy trình ghi chú học tập thực chiến.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Đừng đọc bài báo khoa học từ đầu đến cuối: đây là cách đọc 15 phút nắm trọn ý.`
- `Kỹ thuật Feynman 4 bước giúp bạn làm chủ mọi kiến thức khó chỉ sau một buổi tối.`
- `Vì sao bạn đọc sách chuyên ngành càng nhiều lại càng thấy mình không nhớ gì?`
- `3 bước viết phần mở đầu bài nghiên cứu khiến giảng viên gật đầu ngay lập tức.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: môn học nào đang làm bạn đau đầu nhất? Bình luận nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi quy trình tự học sâu chủ đề tiếp theo.
### Điều cấm kỵ (Avoid)
- Biến kiến thức bình dân thành rắc rối hàn lâm
- Cổ xúy học vẹt, học để đối phó thi cử
- Đạo văn hoặc hướng dẫn gian lận học thuật

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_academic_sketchbook` — Sổ tay học thuật cổ điển: minh họa bút mực Da Vinci, giấy da vellum và sơ đồ phân loại
- **Bảng màu khóa cứng:** `#F6F1E3`, `#1F2D3D`, `#B8860B`, `#4F6D5A`, `#8C7A6B`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Warm scholarly human presenter with wavy dark hair, round brass spectacles, and flat olive-tweed vest over rolled white sleeves, holding a fountain pen or open leather notebook
- **Trang phục (`DEFAULT_OUTFIT`):** Flat olive-tweed vest over crisp rolled-sleeve ivory oxford shirt with brass spectacles, no shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Scholarly presenter holding open glowing manuscript + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Classical Da Vinci and Oxford archival ivory vellum fountain-pen illustration on warm archival vellum canvas (#F6F1E3 warm archival vellum, #1F2D3D deep indigo fountain-pen ink, #B8860B antique brass compass gold, #4F6D5A botanical library sage) with fine ink linework, index cards, marginalia annotations and taxonomy diagrams; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `screen_capture_hybrid` (Tỷ lệ đồ họa động Remotion/Hyperframes: **55%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **5 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **6–9 phút** cho 1 TikTok Short độc lập; **26–36 phút** cho trọn bộ (1 YouTube Long + 5 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Paper summary cards & knowledge tree nodes rendered cleanly via Remotion motion cards.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Làm Chủ Mọi Kiến Thức Khó: Kỹ Thuật Feynman & Quy Trình Đọc Hiểu Tài Liệu Nghiên Cứu Chuyên Sâu*
- **Thời lượng:** 12 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Đừng bao giờ đọc một bài báo khoa học từ đầu đến cuối như đọc tiểu thuyết: chỉ cần áp dụng phương pháp 3 bước này, bạn sẽ nắm trọn ý cốt lõi trong 15 phút."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *ghi chép cẩn thận* (45s)
- **Spin-off #2 (0 ảnh mới):** *Kỹ thuật Feynman 4 bước giúp bạn làm chủ mọi kiến thức khó sau một buổi tối.* (40s)
- **Spin-off #3 (0 ảnh mới):** *Phương pháp ghi chú Zettelkasten: biến tài liệu rời rạc thành mạng lưới tư duy.* (45s)
- **Fast-Short #4 (5 ảnh Flow):** *Cách đặt câu hỏi nghiên cứu sắc bén cho luận văn tốt nghiệp đại học.* (45s)

### Backlog chủ đề hạt giống tiếp theo
- ghi chép cẩn thận
- Cách đọc hiểu một bài báo khoa học chuẩn quốc tế trong vòng 20 phút
- Kỹ thuật Feynman: thước đo tối thượng để biết bạn thật sự hiểu
- Phương pháp ghi chú Zettelkasten: biến tài liệu rời rạc thành mạng lưới
- Cách đặt câu hỏi nghiên cứu sắc bén cho luận văn tốt nghiệp

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#labanhocthuat #phuongphaphoc #nghiencuukhoahoc #feynman #kienthuc`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate ứng dụng ghi chú / quản lý tài liệu (Notion, Obsidian), Khóa học phương pháp nghiên cứu cho sinh viên
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-la-ban-hoc-thuat
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel la_ban_hoc_thuat
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
