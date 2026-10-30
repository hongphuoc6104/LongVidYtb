# KẾ HOẠCH CHI TIẾT KÊNH: THƯƠNG CHO KHÉO (`thuong_cho_kheo`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `thuong_cho_kheo` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/thuong-cho-kheo` (`origin/channel/thuong-cho-kheo`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-thuong-cho-kheo`
- **Ngách nội dung:** Tình cảm, giao tiếp và cách cư xử
- **Lời hứa thương hiệu (Value Proposition):** Những tình huống tình cảm ai cũng gặp, và cách nói cho khéo.
- **Khán giả mục tiêu:** Người 18-30 đang yêu, độc thân hoặc mới chia tay
- **Nhân vật dẫn chuyện (Persona):** Người chị/anh tâm lý, tâm sự nhỏ nhẹ, không phán xét
- **Giọng văn (Tone):** Tâm sự, chạm cảm xúc, ấm áp, đôi khi hài nhẹ | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 30–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–15 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Giác Minh Luật** (TikTok): Gen Z language and everyday analogies about love and anxiety.
- **Hồng Trân (Naiverosie)** (TikTok): Reflective dating psychology and communication.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Tuệ An / Cửa Sổ Tình Yêu** (YouTube): Situation -> analysis -> advice structure.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open with a dialogue line from a real-feeling situation.
- Show the wrong reply and the better reply side by side as two moments.
- Validate feelings before giving advice.
- Never stereotype genders; advice works for everyone.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Khi người ấy nói '[câu nói]', thật ra họ đang muốn [điều ẩn].`
- `Đừng bao giờ trả lời '[câu sai]' khi người yêu [tình huống].`
- `[Số] câu nói làm người ấy thương bạn hơn.`
- `Bạn không cô đơn đâu, chỉ là [lý do].`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi: bạn đã từng nói câu sai này chưa? Tag người ấy.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi video tình huống tiếp theo.
### Điều cấm kỵ (Avoid)
- Manipulation or 'thao túng' tactics
- Gender stereotypes
- Shaming exes

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_pastel_duo` — Pastel đôi bạn: 2 nhân vật Tũn và Mây đối thoại, nét mềm
- **Bảng màu khóa cứng:** `#FFF8F0`, `#F7C6C7`, `#CDB4DB`, `#BDE0C6`, `#FFF1B5`, `#5B4636`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Recurring duo: 'Tũn', a young man with a round face, messy short black hair and dot eyes; and 'Mây', a young woman with a round face, shoulder-length black hair with a small clip and dot eyes; both drawn in simple chibi-like proportions
- **Trang phục (`DEFAULT_OUTFIT`):** Tũn wears a flat mint (#BDE0C6) hoodie; Mây wears a flat blush (#F7C6C7) cardigan
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Tũn and Mây with contrasting emotions + one short quoted phrase hand-lettered.
- **Prompt Style gốc:**
  > Soft 2D pastel line-art illustration: smooth thin warm-brown outlines (#5B4636), flat unshaded fills in blush pink (#F7C6C7), lavender (#CDB4DB), mint (#BDE0C6) and butter (#FFF1B5) on a flat solid cream canvas (#FFF8F0); two characters facing each other with speech-bubble-free composition, rounded gentle shapes, small heart and sparkle accents, orthographic 2D, no gradients, no 3D.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **6 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–11 phút** cho 1 TikTok Short độc lập; **32–42 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Use based_on in-place facial expression variations for Tũn & Mây dialogue pairs + Remotion wrong/right reply cards.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Vì Sao Hai Người Thương Nhau Thật Lòng Nhưng Cứ Mở Lời Là Làm Nhau Tổn Thương? (5 Bẫy Giao Tiếp Kinh Điển)*
- **Thời lượng:** 11 phút (24 cảnh đối thoại Tũn & Mây)
- **Câu mở đầu (Cold Open):** "Có bao giờ bạn nói ra một câu chỉ vì lo cho người ấy, nhưng vừa dứt lời thì không khí lập tức đóng băng?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *Khi người yêu nói 'Em không sao', tuyệt đối đừng trả lời theo bản năng.* (40s)
- **Spin-off #2 (0 ảnh mới):** *Khác biệt giữa người biết lắng nghe và người chỉ chờ đến lượt mình cãi.* (45s)
- **Spin-off #3 (0 ảnh mới):** *3 câu nói ngắn giúp hạ nhiệt mọi cuộc tranh cãi trong 10 giây.* (40s)
- **Fast-Short #4 (6 ảnh Flow based_on):** *Cách từ chối lời nhờ vả vô lý mà không làm mất lòng đối phương.* (45s)

### Backlog chủ đề hạt giống tiếp theo
- Khi người yêu nói 'em không sao', bạn nên làm gì
- 3 câu nói làm cuộc cãi vã tệ hơn
- Vì sao bạn hay thích người không thích mình
- Cách từ chối mà không làm mất lòng
- Dấu hiệu bạn đang yêu vì sợ cô đơn

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#tinhyeu #tamsu #giaotiep #couple #learnontiktok`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate sách / quà tặng, Booking app hẹn hò
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-thuong-cho-kheo
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel thuong_cho_kheo
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
