# KẾ HOẠCH CHI TIẾT KÊNH: VŨ TRỤ TÍ HON (`vu_tru_ti_hon`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `vu_tru_ti_hon` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/vu-tru-ti-hon` (`origin/channel/vu-tru-ti-hon`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-vu-tru-ti-hon`
- **Ngách nội dung:** Thiên văn học, vật lý lượng tử và các nghịch lý không-thời gian giải thích kiểu Feynman
- **Lời hứa thương hiệu (Value Proposition):** Đặt cả vũ trụ bao la vào một hình vẽ đơn giản để ai cũng chạm tới vẻ đẹp vật lý.
- **Khán giả mục tiêu:** Học sinh, sinh viên, người yêu khoa học vũ trụ và các câu hỏi lớn về thực tại
- **Nhân vật dẫn chuyện (Persona):** Người kể chuyện bầu trời đêm theo tinh thần Feynman đầy tò mò
- **Giọng văn (Tone):** Kinh ngạc, giàu hình ảnh ẩn dụ, chuẩn xác vật lý nhưng bình dị | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 40–55s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 12–17 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **MinutePhysics** (YouTube): Stick figure physics breakdowns solving mind-bending paradoxes in minutes.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Kurzgesagt – In a Nutshell** (YouTube): Optimistic nihilism and cosmos mysteries explained with charming 2D animation.
- **Vũ Trụ Trong Vỏ Hạt Dẻ (Stephen Hawking)** (Book/Scripture): Nghịch lý lỗ đen và vẻ đẹp của vật lý lượng tử qua những ẩn dụ thị giác giàu hình ảnh.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mở đầu bằng một câu hỏi ngây thơ nhưng chạm đến tận cùng bản chất vũ trụ.
- Tuyệt đối dùng tư duy Feynman: giải thích bằng quả bóng, tấm bạt cao su, không dùng phương trình khó.
- Khơi gợi cảm xúc ngạc nhiên, khiêm nhường trước quy luật của tạo hóa.
- Đảm bảo số liệu kích thước, khoảng cách được đối chiếu với vật thể quen thuộc.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Nếu bạn rơi vào lỗ đen, bạn sẽ nhìn thấy tương lai của vũ trụ trước khi chết.`
- `Thời gian thật ra không hề trôi: nghịch lý này khiến Einstein mất 10 năm chứng minh.`
- `Mỗi nguyên tử trên tay bạn đều từng được tôi luyện bên trong một ngôi sao nổ tung.`
- `Nếu vũ trụ vô tận, tại sao bầu trời đêm lại có màu đen?`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: câu hỏi vũ trụ nào khiến bạn tò mò nhất? Bình luận nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi câu hỏi kỳ vĩ tiếp theo về không-thời gian.
### Điều cấm kỵ (Avoid)
- Khoa học viễn tưởng giả danh vật lý lý thuyết
- Dùng công thức toán phức tạp làm nản lòng người xem
- Thần bí hóa tâm linh phản khoa học

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_cosmos_vector` — Vũ trụ vector hình học: phong cách Kurzgesagt rực rỡ, robot thám hiểm Tí Hon trên nền vũ trụ sâu
- **Bảng màu khóa cứng:** `#0B1026`, `#4CC9F0`, `#FF6B6B`, `#FFD166`, `#7209B7`, `#FFFFFF`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Adorable compact spherical robotic space-probe mascot Tí Hon with a glowing cyan visor eye and tiny thruster wings floating beside vibrant geometric planets
- **Trang phục (`DEFAULT_OUTFIT`):** Seamless white and polished gold chassis plating with glowing pulsar-cyan optic lens visor, no human clothes
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Glowing robotic probe Tí Hon near dramatic space phenomenon + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Luminous Kurzgesagt-inspired 2D flat geometric space vector illustration on deep cosmic indigo canvas (#0B1026 deep cosmic indigo canvas, #4CC9F0 pulsar cyan, #FF6B6B supernova coral, #FFD166 starlight gold, #7209B7 nebula violet) with crisp rounded vector shapes, radiant celestial bodies, orbital trajectories and zero black marker outlines; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **6 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **8–11 phút** cho 1 TikTok Short độc lập; **32–42 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Flat 2D planet orbits, light beams & time dilation diagrams animated via Remotion SVG layers.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Vũ Trụ Trong Lòng Bàn Tay: 5 Nghịch Lý Không-Thời Gian Kỳ Thú Nhất Giải Thích Kiểu Feynman*
- **Thời lượng:** 13 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Nếu vũ trụ chứa hàng trăm tỷ thiên hà với vô số ngôi sao rực sáng, tại sao khi nhìn lên bầu trời đêm chúng ta chỉ thấy một màu đen thẳm?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *ngắm nhìn bầu trời* (45s)
- **Spin-off #2 (0 ảnh mới):** *Hiệu ứng giãn nở thời gian: vì sao phi hành gia già chậm hơn người ở Trái Đất?* (45s)
- **Spin-off #3 (0 ảnh mới):** *Bên trong đường chân trời sự kiện của lỗ đen thực sự có những gì?* (50s)
- **Fast-Short #4 (6 ảnh Flow):** *Thí nghiệm khe đôi: một hạt có thể đi qua cả hai khe cùng lúc như thế nào?* (45s)

### Backlog chủ đề hạt giống tiếp theo
- ngắm nhìn bầu trời
- Nghịch lý Olbers: vì sao bầu trời đêm lại đen khi có vô số ngôi sao
- Hiệu ứng giãn nở thời gian: vì sao phi hành gia già chậm hơn
- Bên trong đường chân trời sự kiện của lỗ đen thực sự có gì
- Thí nghiệm khe đôi: một hạt có thể đi qua cả hai khe cùng lúc

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#vutrutihon #thienvanhoc #vatly #khoahocvutru #kienthuc`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate kính thiên văn / sách khoa học, Sponsor các tổ chức giáo dục STEM
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-vu-tru-ti-hon
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel vu_tru_ti_hon
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
