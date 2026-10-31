# KẾ HOẠCH CHI TIẾT KÊNH: LUẬT NGẦM ĐÁM ĐÔNG (`luat_ngam`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `luat_ngam` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/luat-ngam` (`origin/channel/luat-ngam`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-luat-ngam`
- **Ngách nội dung:** Tâm lý xã hội, hiệu ứng bầy đàn và nghệ thuật đàm phán đời thường
- **Lời hứa thương hiệu (Value Proposition):** Bóc tách một hiệu ứng tâm lý đám đông hoặc mánh thao túng trong 60 giây để không bị dẫn dắt.
- **Khán giả mục tiêu:** Người đi làm, người tiêu dùng, người muốn đọc vị hành vi xã hội
- **Nhân vật dẫn chuyện (Persona):** Nhà quan sát hành vi sắc sảo, điềm tĩnh, vạch trần cơ chế ngầm
- **Giọng văn (Tone):** Sắc sảo, khách quan, cuốn hút, mở nút từng lớp tâm lý | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 10–15 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Psych2Go Vietnam** (TikTok): Everyday psychological hooks that make viewers identify immediately.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Academy of Ideas** (YouTube): Deep social psychology breakdowns with iconic 2D metaphors.
- **Nghệ Thuật Đàm Phán & Tâm Lý Học Hành Vi** (Book/Scripture): Nguyên lý đòn bẩy tâm lý đám đông, hiệu ứng mỏ neo và kỹ thuật nhượng bộ có đi có lại.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Bóc tách một cơ chế thao túng hoặc hiệu ứng bầy đàn trong 3 giây đầu.
- Đặt người xem vào vị trí nạn nhân trước, giải thích lý do tâm lý sau.
- Luôn dùng ví dụ đám đông đời thường tại Việt Nam (quán ăn đông khách, chen lấn, săn sale).
- Kết thúc bằng 1 bước tự vệ tâm lý cụ thể người xem dùng được ngay.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Vì sao bạn luôn [hành vi bầy đàn] dù biết [hậu quả]?`
- `3 mánh tâm lý đám đông khiến bạn [hành động] mà không hề hay biết.`
- `Bạn không tự quyết định món đồ đó: đám đông đã chọn thay bạn.`
- `Nếu thấy [dấu hiệu đám đông], bạn đang rơi vào bẫy thao túng này.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: bạn từng dính bẫy tâm lý này chưa? Bình luận số 1 nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi video tiếp theo về bẫy thao túng tâm lý đám đông.
### Điều cấm kỵ (Avoid)
- Lên án hay phán xét đạo đức người xem
- Lý thuyết tâm lý học hàn lâm thiếu ví dụ
- Mẹo thao túng phi đạo đức

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_crowd_noir` — Minh họa 2D noir trinh thám: hồ sơ giấy cũ, tương phản cao, sợi chỉ đỏ
- **Bảng màu khóa cứng:** `#111111`, `#E8E2D0`, `#5A5F66`, `#C0392B`, `#FFFFFF`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Stylized anonymous silhouette figures in sharp trench coats and shadowed crowd profiles with glowing white slit eyes, zero stick figures
- **Trang phục (`DEFAULT_OUTFIT`):** Sharp flat charcoal-black trench coat with crisp collar and single crimson lapel pin, no shading gradients
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Silhouette figure inspecting crimson case files + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > High-contrast 2D noir graphic-novel illustration on aged dossier paper canvas (#111111 heavy black ink, #E8E2D0 aged dossier paper, #5A5F66 smoke-slate, single #C0392B crimson accent for strings and stamps); shadowed crowd profiles, classified document dossiers, red connection threads and atmospheric silhouette contrasts; orthographic 2D, at least 60% negative space, zero 3D, zero shading gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **6 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **8–12 phút** cho 1 TikTok Short độc lập; **35–45 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Minimalist crowd stickmen vs focal red stickman; kinetic dominos & puppet strings in Remotion cut Flow generation.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Bóc Tách 5 Mẹo Thao Túng Tâm Lý Đám Đông Khiến Bạn Mất Tiền & Bị Dẫn Dắt (Kèm Cách Tự Vệ)*
- **Thời lượng:** 12 phút (24 cảnh)
- **Câu mở đầu (Cold Open):** "Bạn có bao giờ bước vào một quán ăn chỉ vì thấy ngoài cửa đông người xếp hàng, dù trước đó bạn chưa từng nghe tên quán?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *chọn theo đám đông* (45s)
- **Spin-off #2 (0 ảnh mới):** *Bẫy khan hiếm nhân tạo: mánh khóe khiến bạn chốt đơn trong 10 giây.* (40s)
- **Spin-off #3 (0 ảnh mới):** *Hiệu ứng người ngoài cuộc: vì sao giữa đám đông không ai chịu giúp đỡ?* (45s)
- **Fast-Short #4 (6 ảnh Flow):** *Thao túng bằng cảm giác tội lỗi trong đàm phán đời thường.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- chọn theo đám đông
- Hiệu ứng bầy đàn: vì sao quán càng đông người ta lại càng muốn vào ăn
- Bẫy khan hiếm nhân tạo: mánh khóe khiến bạn chốt đơn trong 10 giây
- Hiệu ứng người ngoài cuộc: vì sao giữa đám đông không ai chịu ra tay giúp đỡ
- Thao túng bằng cảm giác tội lỗi trong đàm phán đời thường

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#tamlyxahoi #hieuungbaydan #damphan #luatngam #kienthuc`
- **Nguồn doanh thu:** YouTube AdSense, Affiliate sách tâm lý & đàm phán, Khóa học tư duy phản biện
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-luat-ngam
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel luat_ngam
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
