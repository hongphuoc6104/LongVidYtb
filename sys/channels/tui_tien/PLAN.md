# KẾ HOẠCH CHI TIẾT KÊNH: TÚI TIỀN BIẾT NÓI (`tui_tien`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `tui_tien` (Đợt triển khai: Wave 1)
- **Nhánh GitHub độc lập:** `channel/tui-tien` (`origin/channel/tui-tien`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-tui-tien`
- **Ngách nội dung:** Tiền và kinh tế đời sống
- **Lời hứa thương hiệu (Value Proposition):** Bóc tách tiền bạc đằng sau những thứ bạn mua mỗi ngày.
- **Khán giả mục tiêu:** Sinh viên, người mới đi làm thu nhập 7-20 triệu
- **Nhân vật dẫn chuyện (Persona):** Người bạn mê con số, hay tính nhẩm giùm bạn
- **Giọng văn (Tone):** Tò mò, rõ ràng, có số liệu cụ thể bằng tiền Việt | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–15 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Sitcom Tài Chính** (TikTok): Turns economic concepts into short comedic skits.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Học Viện Bò và Gấu** (YouTube): Business-model breakdowns of familiar industries (trà sữa, cà phê, bán lẻ).

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Always anchor numbers in VND and everyday items (ly trà sữa, tô phở, tiền trọ).
- Show the calculation step by step, one number per sentence.
- End with one money action the viewer can take today.
- Cite the source of every statistic in the description.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Ly [món] [giá] nghìn, chủ quán thật ra lời bao nhiêu?`
- `Vì sao [thương hiệu/mô hình] lỗ mà vẫn mở thêm chi nhánh?`
- `Nếu mỗi ngày bạn bớt [khoản nhỏ], 5 năm sau bạn có [số tiền].`
- `Bạn đang trả tiền cho [thứ vô hình] mà không biết.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi: bạn muốn mình bóc tách món nào tiếp theo?
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi case study kinh doanh tiếp theo.
### Điều cấm kỵ (Avoid)
- Stock picks or investment advice
- Get-rich-quick claims
- Unsourced numbers

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_ledger_doodle` — Sổ tay kế toán vẽ tay: doodle trên giấy kẻ ô, tiền xu, biểu đồ vẽ tay
- **Bảng màu khóa cứng:** `#FAF6E9`, `#2F9E5B`, `#F2C14E`, `#D64545`, `#24364F`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Simple 2D doodle stickman with a white round head, black dot eyes, thin wire arms and round hands, small round glasses, always holding a pencil or a coin
- **Trang phục (`DEFAULT_OUTFIT`):** Flat coin-gold (#F2C14E) T-shirt and navy (#24364F) trousers, no folds, no shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** One big VND number or price tag + shocked stickman, hand-lettered on grid paper.
- **Prompt Style gốc:**
  > Hand-drawn 2D notebook-ledger explainer illustration: wobbly black marker outlines (#1F1F1F) on a flat warm grid-paper canvas (#FAF6E9 with faint #E3DCC8 square grid), flat unshaded fills in money green (#2F9E5B), coin gold (#F2C14E), loss red (#D64545) and ink navy (#24364F); hand-drawn bar charts, price tags and VND banknotes drawn as simple flat shapes; orthographic 2D, generous empty grid space, no gradients, no photorealism, no 3D.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **50%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **6 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **30–40 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** 50% scenes use Remotion/Hyperframes VND cost breakdown cards & animated bar charts; only 5-6 Flow images per short.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Giải Mã Đế Chế Trà Sữa & Cà Phê: Vì Sao Ly Nước 50 Nghìn Lãi Đậm Mà Hàng Loạt Quán Vẫn Sập?*
- **Thời lượng:** 12 phút (26 cảnh)
- **Câu mở đầu (Cold Open):** "Một ly trà sữa bán 50 nghìn đồng, tiền cốt trà và trân châu thật sự chỉ tốn chưa tới 7 nghìn, vậy 43 nghìn còn lại đi đâu?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *Ly trà sữa 35 nghìn: chủ quán thực sự đút túi bao nhiêu tiền?* (45s)
- **Spin-off #2 (0 ảnh mới):** *Bẫy tâm lý 'Thêm 5 nghìn lên size L': quán lời gấp đôi thế nào?* (40s)
- **Spin-off #3 (0 ảnh mới):** *Vì sao quán cà phê để khách ngồi điều hòa cả ngày vẫn sống khỏe?* (45s)
- **Fast-Short #4 (5 ảnh Flow + bảng tính Remotion):** *Mua trả góp 0% lãi suất: ai đang âm thầm trả lãi thay bạn?* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Ly trà sữa 35 nghìn: chủ quán lời thật bao nhiêu
- Vì sao siêu thị để sữa ở cuối cửa hàng
- Mua trả góp 0%: ai trả lãi cho bạn
- Vì sao quán cà phê sống được dù khách ngồi cả ngày
- Bớt 30 nghìn mỗi ngày, 5 năm sau bạn có bao nhiêu

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#taichinhcanhan #kienthuckinhte #kinhte #tienbac #learnontiktok`
- **Nguồn doanh thu:** YouTube AdSense (CPM cao nhất trong 8 kênh), Affiliate app tài chính / sách, Booking
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-tui-tien
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel tui_tien
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
