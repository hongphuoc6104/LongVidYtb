# KẾ HOẠCH CHI TIẾT KÊNH: AI BÌNH DÂN (`ai_binh_dan`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `ai_binh_dan` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/ai-binh-dan` (`origin/channel/ai-binh-dan`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-ai-binh-dan`
- **Ngách nội dung:** Mẹo dùng AI và công nghệ cho người thường
- **Lời hứa thương hiệu (Value Proposition):** Một mẹo AI làm được ngay trong 1 phút, không cần biết code.
- **Khán giả mục tiêu:** Người đi làm văn phòng, sinh viên, chủ shop nhỏ
- **Nhân vật dẫn chuyện (Persona):** Đồng nghiệp rành công nghệ, chỉ từng bước 'làm theo liền'
- **Giọng văn (Tone):** Thực chiến, nhanh, hào hứng, chỉ từng bước | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 30–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–20 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Nghề Công Sở (Richard Võ)** (TikTok): 'One prompt does X' with instant visible result.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Văn Thế Web** (YouTube): Full step-by-step AI workflow tutorials.
- **Nam Hệ Thống AI** (YouTube): Data-driven tool walkthroughs.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Show the end result in the first 3 seconds, then how.
- Every step must be reproducible with free tools.
- Use screen_capture shots for tool steps (ask user to record or capture via CDP).
- State tool names and limits honestly; no fake results.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Một câu lệnh này giúp bạn [kết quả] trong [thời gian].`
- `Đừng [cách cũ] nữa, AI làm trong 30 giây.`
- `[Số] mẹo AI miễn phí dân văn phòng nên biết.`
- `Mình đã thử [công cụ] để [việc], và đây là kết quả.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi: bạn muốn mẹo cho công việc gì? Lưu lại để dùng.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open: final result demo
1. Who needs this and what it saves
1. Step-by-step screen walkthrough in chapters
1. Common mistakes and limits
1. Template / prompt recap
1. Next tutorial tease
- **Câu kết (CTA):** Gợi hướng dẫn chuyên sâu tiếp theo.
### Điều cấm kỵ (Avoid)
- Promising income from AI
- Paid-tool shilling without disclosure
- Unsafe privacy practices

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_tech_doodle` — Doodle công nghệ: stickman + khung màn hình, chèn quay màn hình thật
- **Bảng màu khóa cứng:** `#FFFFFF`, `#3B82C4`, `#7C5CFF`, `#34D399`, `#E5E7EB`, `#000000`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Iconic 2D Vietnamese indie webcomic doodle stickman (Nguệch Ngoạc / Vẽ Vời / Xấu Vê Nờ style): oversized slightly lopsided hand-drawn pure-white (#FFFFFF) bald circle head with bold pitch-black (#000000) marker outline, tiny solid-black dot eyes placed low on the face leaving a large open upper forehead/cranium, minimal single-stroke eyebrows and mouth, no nose or ears, thin single-line solid-black wire/stick arms (single black stroke with zero arm thickness) ending in small round white circle hands
- **Trang phục (`DEFAULT_OUTFIT`):** Flat violet (#7C5CFF) hoodie and slate-grey trousers, no folds, no shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Before/after result on a hand-drawn screen + stickman pointing + 2-3 word promise.
- **Prompt Style gốc:**
  > Hand-drawn 2D tech doodle explainer illustration: wobbly black marker outlines (#000000), flat unshaded fills in electric blue (#3B82C4), violet (#7C5CFF), mint (#34D399) and soft grey (#E5E7EB) on a flat solid white canvas (#FFFFFF); simple hand-drawn laptop, phone and browser-window frames with abstract placeholder content, cursor arrows and checkmarks; orthographic 2D, at least 60% empty space, no gradients, no glossy UI, no 3D.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `screen_capture_hybrid` (Tỷ lệ đồ họa động Remotion/Hyperframes: **60%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **4 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **5 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **5–8 phút** cho 1 TikTok Short độc lập; **25–35 phút** cho trọn bộ (1 YouTube Long + 5 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Fastest channel: 60% scenes are Remotion prompt terminal cards or screen_capture; only 3-4 Flow doodle images per short.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Trọn Bộ 5 Quy Trình Dùng AI Miễn Phí Giúp Dân Văn Phòng Tiết Kiệm 2 Giờ Mỗi Ngày (Kèm Câu Lệnh Mẫu)*
- **Thời lượng:** 12 phút (kết hợp Doodle + khung câu lệnh Remotion + quay màn hình)
- **Câu mở đầu (Cold Open):** "Đừng mất 2 tiếng ngồi đọc từng trang báo cáo dài nữa: chỉ với một câu lệnh miễn phí này, bạn sẽ có bảng tóm tắt chuẩn xác trong 30 giây."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *Tóm tắt file PDF 50 trang thành bảng việc cần làm trong 30 giây.* (40s)
- **Spin-off #2 (0 ảnh mới):** *Một câu lệnh biến ghi chú họp lộn xộn thành biên bản gửi sếp ngay.* (40s)
- **Spin-off #3 (0 ảnh mới):** *Cách nhờ AI viết email xin nghỉ phép hoặc từ chối khéo cực lịch sự.* (35s)
- **Fast-Short #4 (4 ảnh Flow + khung lệnh Remotion):** *Mẹo dùng AI rà soát lỗi hợp đồng trước khi đặt bút ký.* (40s)

### Backlog chủ đề hạt giống tiếp theo
- Dùng AI tóm tắt file PDF 50 trang trong 1 phút
- Viết email xin nghỉ phép khéo léo bằng một câu lệnh
- Tạo bảng chi tiêu tự động bằng AI và Google Sheets
- 3 mẹo chụp ảnh sản phẩm bằng điện thoại và AI cho chủ shop
- Dùng AI luyện phỏng vấn xin việc

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#ai #meocongnghe #chatgpt #vanphong #learnontiktok`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate phần mềm / khóa học (có công khai), Template bán kèm
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-ai-binh-dan
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel ai_binh_dan
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
