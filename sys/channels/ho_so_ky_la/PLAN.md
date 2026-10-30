# KẾ HOẠCH CHI TIẾT KÊNH: HỒ SƠ KỲ LẠ (`ho_so_ky_la`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `ho_so_ky_la` (Đợt triển khai: Wave 1)
- **Nhánh GitHub độc lập:** `channel/ho-so-ky-la` (`origin/channel/ho-so-ky-la`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-ho-so-ky-la`
- **Ngách nội dung:** Bí ẩn và chuyện kỳ lạ có thật
- **Lời hứa thương hiệu (Value Proposition):** Những hồ sơ kỳ lạ có thật, kể bình tĩnh và có bằng chứng.
- **Khán giả mục tiêu:** Người 18-40 thích bí ẩn, trinh thám, phim tài liệu
- **Nhân vật dẫn chuyện (Persona):** Thám tử điềm tĩnh mở từng tập hồ sơ
- **Giọng văn (Tone):** Hồi hộp, chậm rãi, giọng trầm, mở nút thắt từng lớp | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 60–90s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 15–25 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Các kênh 'Kỳ Án / Hồ Sơ'** (TikTok): Start mid-mystery and cut at the peak with a part-2 call.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Dương FG** (YouTube): Calm, detailed investigative storytelling.
- **Độc Thám TV** (YouTube): Documentary-style reconstruction focused on evidence.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Start at the single most unexplainable detail.
- Reveal evidence one piece per beat; withhold the theory until late.
- Present 2-3 competing explanations fairly.
- No gore, no victim blaming, no naming private individuals in recent cases.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Năm [năm], [số] người biến mất và chỉ để lại [chi tiết kỳ lạ].`
- `Đến nay chưa ai giải thích được vì sao [hiện tượng].`
- `Tấm ảnh này có một chi tiết khiến các chuyên gia im lặng.`
- `Hồ sơ số [số]: [tên vụ việc].`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Dừng ở chi tiết gay cấn nhất: 'Phần 2 có trên kênh'.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open: the most unexplainable detail
1. Case file: setting, people, timeline
1. Evidence reveals one by one with re-hooks
1. Competing theories weighed fairly
1. What remains unexplained today
1. Next case tease
- **Câu kết (CTA):** Gợi hồ sơ tiếp theo.
### Điều cấm kỵ (Avoid)
- Graphic violence or gore
- Recent crimes involving private persons
- Supernatural claims as fact

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_noir_dossier` — Noir hồ sơ: minh họa 2D tương phản cao, đen trắng và một điểm đỏ
- **Bảng màu khóa cứng:** `#111111`, `#E8E2D0`, `#5A5F66`, `#C0392B`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Silhouette-style figures with simple faces, the narrator detective drawn as a faceless figure in a long coat and hat seen from behind or in profile
- **Trang phục (`DEFAULT_OUTFIT`):** Flat slate-grey long coat and hat; only evidence objects use the red accent
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** One mysterious object circled in red on off-white paper + 2-3 word case title.
- **Prompt Style gốc:**
  > 2D noir graphic-novel illustration: heavy black ink shapes and crisp linework with high-contrast flat shadows, limited palette of ink black (#111111), aged off-white paper (#E8E2D0), slate grey (#5A5F66) and a single accent of evidence red (#C0392B); case-file props such as folders, stamped documents, map pins and old photographs drawn flat; orthographic 2D, no gore, no blood, no gradients, no photorealism, no 3D.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `flow_full_frame` (Tỷ lệ đồ họa động Remotion/Hyperframes: **30%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **8 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **9–13 phút** cho 1 TikTok Short độc lập; **38–48 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Build 1 deep 15-min Noir dossier on YouTube, slice 4 'Evidence #1..#4' cliffhanger shorts for TikTok with zero extra images.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Hồ Sơ Con Tàu Mary Celeste: Vì Sao Toàn Bộ Thủy Thủ Đoàn Biến Mất Khi Bữa Ăn Vẫn Còn Nguyên Trên Bàn?*
- **Thời lượng:** 15 phút (28 cảnh Noir hồ sơ)
- **Câu mở đầu (Cold Open):** "Ngày 4 tháng 12 năm 1872, người ta tìm thấy con tàu Mary Celeste trôi dạt giữa Đại Tây Dương: hàng hóa nguyên vẹn, quần áo vẫn xếp gọn, nhưng không còn một bóng người."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *Manh mối #1: Chi tiết kỳ lạ nhất trên boong tàu Mary Celeste.* (60s)
- **Spin-off #2 (0 ảnh mới):** *Manh mối #2: Vì sao giả thuyết cướp biển tấn công bị bác bỏ ngay lập tức?* (55s)
- **Spin-off #3 (0 ảnh mới):** *Manh mối #3: Giả thuyết khoa học hợp lý nhất giải thích lệnh bỏ tàu khẩn cấp.* (60s)
- **Fast-Short #4 (8 ảnh Flow):** *Tín hiệu 'Wow!' năm 1977: 72 giây sóng vô tuyến bí ẩn từ vũ trụ.* (60s)

### Backlog chủ đề hạt giống tiếp theo
- Sự cố đèo Dyatlov: 9 người leo núi và chiếc lều bị rạch từ bên trong
- Chuyến bay MH370 biến mất như thế nào
- Con tàu Mary Celeste trôi không người lái
- Người đàn ông Somerton và mẩu giấy 'Tamám Shud'
- Tín hiệu 'Wow!' từ vũ trụ năm 1977

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#bian #hosokyla #chuyenkyla #mystery #learnontiktok`
- **Nguồn doanh thu:** YouTube AdSense (retention cao), Series dài kỳ, Membership
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-ho-so-ky-la
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel ho_so_ky_la
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
