# KẾ HOẠCH CHI TIẾT KÊNH: NÃO LƯỜI (`nao_luoi`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `nao_luoi` (Đợt triển khai: Wave 1)
- **Nhánh GitHub độc lập:** `channel/nao-luoi` (`origin/channel/nao-luoi`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-nao-luoi`
- **Ngách nội dung:** Tâm lý và hành vi đời thường
- **Lời hứa thương hiệu (Value Proposition):** Giải thích vì sao bạn hành xử như vậy, bằng ngôn ngữ của bạn bè.
- **Khán giả mục tiêu:** Gen Z và người đi làm 18-30 tuổi, hay tự hỏi về bản thân
- **Nhân vật dẫn chuyện (Persona):** Người bạn thân hiểu tâm lý, hơi cà khịa nhưng thương người xem
- **Giọng văn (Tone):** Thân mật, cà khịa nhẹ, gọi người xem là 'bạn', có cảm xúc | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 30–45s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Psych2Go Vietnam** (TikTok/YouTube Shorts): Relatable 'signs you are...' questions; viewer sees themselves.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Psych2Go** (YouTube): 7-15 min listicles with a fixed cartoon cast; empathy over lecture.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open with a behavior the viewer recognizes in themselves within 3 seconds.
- Name the psychology effect only after the viewer feels it.
- Allow light teasing and slang; never shame the viewer.
- Every list item gets one concrete everyday Vietnamese example.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Nếu bạn hay [hành vi], não bạn đang [sự thật bất ngờ].`
- `[Số] dấu hiệu bạn đang [trạng thái] mà không biết.`
- `Bạn không lười. Não bạn đang [lý do].`
- `Vì sao càng [hành động] bạn lại càng [kết quả ngược]?`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: bạn có bị như vậy không? Bình luận số 1 hoặc 2.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi video tiếp theo cùng series tâm lý.
### Điều cấm kỵ (Avoid)
- Diagnosing mental illness
- Toxic-positivity advice
- Long academic definitions

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `handdrawn_2d_explainer` — Doodle stickman Nguệch Ngoạc (giữ phong cách hiện tại, biểu cảm mạnh hơn)
- **Bảng màu khóa cứng:** `#F8F0DC`, `#FFFFFF`, `#3B82C4`, `#F2B88B`, `#93A88C`, `#000000`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Iconic 2D Vietnamese indie webcomic doodle stickman (Nguệch Ngoạc / Vẽ Vời / Xấu Vê Nờ style): oversized slightly lopsided hand-drawn pure-white (#FFFFFF) bald circle head with bold pitch-black (#000000) marker outline, tiny solid-black dot eyes placed low on the face leaving a large open upper forehead/cranium, minimal single-stroke eyebrows and mouth, no nose or ears, thin single-line solid-black wire/stick arms (single black stroke with zero arm thickness) ending in small round white circle hands
- **Trang phục (`DEFAULT_OUTFIT`):** Unshaded 100% flat MS-Paint paint-bucket solid cerulean-blue (#3B82C4) simple pill/rectangular T-shirt torso and simple flat slate-gray (#8C857B) straight trousers or single-line black stick legs, with zero clothing folds, zero collar details, and zero shading gradients
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Stickman with exaggerated emotion + 2-4 uppercase hand-lettered words on flat canvas.
- **Prompt Style gốc:**
  > Hand-drawn 2D Vietnamese indie doodle explainer illustration (raw freehand MS-Paint / Flash webcomic aesthetic). Use clear black outer contours (#000000) with visible unpolished hand-drawn wobble, slightly crooked freehand lines drawn without a ruler, imperfect corner joints, and uniform marker stroke weight across both foreground and background (strictly forbid lighter background linework, Bezier curve smoothing, sleek rounded vector icons, or geometric perfection). Fill all shapes with 100% unshaded flat MS-Paint paint-bucket solid hex colors: warm paper-cream (#F8F0DC), muted apricot-peach (#F2B88B), soft sage-green (#93A88C), pale ice-blue (#CBE0E0), flat night slate-navy (#2E4361), or stark pure white (#FFFFFF). Strictly 2D front-on or side-on orthographic flat paper-cutout staging; never use 3/4 isometric furniture perspective, two-tone bevel shading, floating black oval drop shadows, floor cast shadows, glowing lamp light cones, warm sepia AI color grading, gradients, photorealism, or 3D rendering. Draw a complete scene image.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **35%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **7 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **8–12 phút** cho 1 TikTok Short độc lập; **35–45 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Reuse 1.7.0 stickman templates; Remotion kinetic psychology badges + camera beats cut image count by 50%.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Tại Sao Càng Tự Trách Bản Thân Bạn Lại Càng Trì Hoãn? (Giải Mã Cơ Chế Phòng Vệ Của Não Bộ)*
- **Thời lượng:** 10 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Bạn đã bao giờ nằm lướt điện thoại cả tiếng đồng hồ, trong lòng cực kỳ sốt ruột vì công việc chưa xong, nhưng tay vẫn không thể dừng lại?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *Vì sao càng gần deadline bạn lại càng muốn đi dọn phòng?* (35s)
- **Spin-off #2 (0 ảnh mới):** *Bạn không hề lười: não bạn đang bật chế độ đóng băng vì sợ hoàn hảo.* (35s)
- **Spin-off #3 (0 ảnh mới):** *Quy tắc 120 giây đánh lừa bộ não đang trì hoãn.* (30s)
- **Fast-Short #4 (6 ảnh Flow):** *Vì sao bạn thức tới 2 giờ sáng dù mắt đã díp lại? (Trả thù giờ đi ngủ)* (35s)

### Backlog chủ đề hạt giống tiếp theo
- Vì sao bạn lướt điện thoại tới 2 giờ sáng dù rất buồn ngủ
- Vì sao càng gần deadline bạn càng muốn dọn phòng
- 5 dấu hiệu bạn đang kiệt sức mà tưởng mình lười
- Vì sao bạn nhớ mãi một câu chê nhưng quên 10 lời khen
- Hiệu ứng chim mồi: vì sao bạn luôn chọn ly size vừa

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#tamly #tamlyhoc #hieubanthan #genz #learnontiktok`
- **Nguồn doanh thu:** YouTube AdSense (long), Affiliate sách tâm lý, Booking app sức khỏe tinh thần
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-nao-luoi
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel nao_luoi
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
