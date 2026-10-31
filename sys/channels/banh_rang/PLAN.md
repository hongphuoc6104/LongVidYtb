# KẾ HOẠCH CHI TIẾT KÊNH: BÁNH RĂNG THẾ GIỚI (`banh_rang`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `banh_rang` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/banh-rang` (`origin/channel/banh-rang`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-banh-rang`
- **Ngách nội dung:** Kinh tế vĩ mô, lạm phát, lãi suất và chuỗi cung ứng toàn cầu giải thích bình dân
- **Lời hứa thương hiệu (Value Proposition):** Thấy rõ các bánh răng kinh tế ngầm đang tác động tới lương và giá cả quanh bạn.
- **Khán giả mục tiêu:** Người đi làm, nhà đầu tư cá nhân F0, chủ doanh nghiệp nhỏ
- **Nhân vật dẫn chuyện (Persona):** Người tháo lắp cỗ máy kinh tế bằng sơ đồ bánh răng trực quan
- **Giọng văn (Tone):** Logic, nhân quả sắc bén, biến vĩ mô khô khan thành chuyện sát sườn | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 45–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 11–16 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Economics Explained** (YouTube): 60-second animated macro breakdowns connecting interest rates to daily life.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Ray Dalio (How The Economic Machine Works)** (YouTube): Visual machine metaphor explaining credit cycles and inflation simply.
- **Dòng Tiền Thông Minh & Chu Kỳ Kinh Tế** (Book/Scripture): Cơ chế dòng tiền luân chuyển giữa các lớp tài sản khi lãi suất và lạm phát đảo chiều.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mỗi video chỉ giải thích đúng 1 mắt xích nhân quả vĩ mô (A tăng -> B giảm -> C tác động tới bạn).
- Quy mọi thuật ngữ lớn (Fed tăng lãi suất, nới lỏng định lượng) về giá tô phở, tiền lãi ngân hàng.
- Dùng sơ đồ bánh răng hoặc đường ống tiền tệ trực quan.
- Không khuyến nghị đầu cơ lướt sóng; tập trung vào cơ chế vận hành dài hạn.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Ngân hàng Trung ương Mỹ vừa bấm một nút, vì sao giá bát phở ở Việt Nam lại tăng?`
- `Lạm phát thật ra không phải giá tăng: nó là tiền của bạn đang bốc hơi.`
- `Bánh răng kinh tế nào quyết định tiền lương của bạn sau 3 năm nữa?`
- `Vì sao lãi suất giảm mà người dân lại càng ngại chi tiêu?`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: bạn có cảm nhận rõ bánh răng này chưa? Bình luận nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi bánh răng kinh tế tiếp theo đang âm thầm quay chuyển.
### Điều cấm kỵ (Avoid)
- Khuyến nghị mua bán cổ phiếu, crypto cụ thể
- Dự đoán đáy đỉnh thị trường
- Lý thuyết kinh tế giáo điều thiếu số liệu

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_macro_blueprint` — Bản vẽ kinh tế vĩ mô: blueprint xanh Phổ, sơ đồ hệ thống tài chính Thụy Sĩ chuẩn xác
- **Bảng màu khóa cứng:** `#142B47`, `#F1FAEE`, `#F4A261`, `#4CC9F0`, `#1D3557`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Sleek flat geometric mid-century economist presenter with structured angular shoulders, neat hair, brass pointer rod, accompanied by technical cross-sections of container ships, central-bank vaults and currency scales
- **Trang phục (`DEFAULT_OUTFIT`):** Flat dark-slate minimalist vest over rolled-up technical drafting shirt, zero shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Macroeconomic blueprint schematic with glowing gold key lever + 2-4 uppercase VN words.
- **Prompt Style gốc:**
  > Crisp 2D Prussian-blue architectural blueprint and Swiss macroeconomic schematic on deep navy canvas (#142B47 Prussian blueprint navy background, #F1FAEE crisp white technical linework, #F4A261 brass-gold indicator accent, #4CC9F0 cyan grid lines); precision technical drafting lines, systemic feedback loops, trade corridors and currency flow vectors; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **50%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Rotating 2D gear SVG components & currency pipe flows animated directly in Remotion cut Flow reliance.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Cỗ Máy Kinh Tế Vận Hành Ra Sao: Lạm Phát, Lãi Suất Ngân Hàng & Tác Động Tới Túi Tiền Của Bạn*
- **Thời lượng:** 13 phút (26 cảnh)
- **Câu mở đầu (Cold Open):** "Khi Cục Dự trữ Liên bang Mỹ quyết định tăng lãi suất, vì sao giá bát phở và tiền lãi vay mua nhà của bạn ở Việt Nam lại thay đổi?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *lo lắng tiền bạc* (50s)
- **Spin-off #2 (0 ảnh mới):** *Cơ chế lãi suất ngân hàng: chiếc phanh hãm cỗ máy kinh tế hoạt động ra sao?* (45s)
- **Spin-off #3 (0 ảnh mới):** *Vòng xoáy giảm phát: vì sao giá hàng hóa hạ lại là cơn ác mộng kinh tế?* (45s)
- **Fast-Short #4 (5 ảnh Flow):** *Chuỗi cung ứng bán dẫn: bánh răng nhỏ quyết định nền công nghệ thế giới.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- lo lắng tiền bạc
- Vì sao Mỹ in thêm nghìn tỷ USD nhưng cả thế giới gánh lạm phát
- Cơ chế lãi suất ngân hàng: chiếc phanh hãm cỗ máy kinh tế hoạt động ra sao
- Vòng xoáy giảm phát: vì sao giá hàng hóa hạ lại là cơn ác mộng
- Bẫy nợ quốc gia và cơ chế tái cấu trúc dòng vốn toàn cầu

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#banhrangthegioi #kinhtevimo #lamphat #dongtien #kienthuc`
- **Nguồn doanh thu:** YouTube AdSense RPM cao, Sponsor nền tảng quản lý tài chính / ngân hàng, Khóa học kiến thức kinh tế vĩ mô căn bản
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-banh-rang
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel banh_rang
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
