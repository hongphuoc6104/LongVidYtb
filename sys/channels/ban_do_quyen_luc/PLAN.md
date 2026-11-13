# KẾ HOẠCH CHI TIẾT KÊNH: BẢN ĐỒ QUYỀN LỰC (`ban_do_quyen_luc`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `ban_do_quyen_luc` (Đợt triển khai: Wave 2)
- **Nhánh GitHub độc lập:** `channel/ban-do-quyen-luc` (`origin/channel/ban-do-quyen-luc`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-ban-do-quyen-luc`
- **Ngách nội dung:** Địa chính trị, kinh tế học tài nguyên và các tuyến hàng hải chiến lược
- **Lời hứa thương hiệu (Value Proposition):** Nhìn vào một tấm bản đồ để hiểu vì sao thế giới vận hành như hiện tại.
- **Khán giả mục tiêu:** Người quan tâm thời sự quốc tế, kinh tế vĩ mô, lịch sử địa lý
- **Nhân vật dẫn chuyện (Persona):** Người giải mã bản đồ chiến lược bằng ngôn từ đời thường
- **Giọng văn (Tone):** Mạch lạc, tầm nhìn lớn, dẫn chứng địa lý - tài nguyên xác đáng | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 50–60s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 12–18 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Johnny Harris** (YouTube): Fast-paced visual map journalism showing why geography dictates borders and conflicts.
### Kênh mẫu YouTube Long (`long_16x9`)
- **RealLifeLore** (YouTube): Strategic geography and choke-point logistics explained via clean maps.
- **Những Tù Nhân Của Địa Lý (Tim Marshall)** (Book/Scripture): Sách kinh điển giải thích địa lý tự nhiên định hình chính trị, chiến tranh và số phận các quốc gia.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Mở đầu bằng một điểm nghẽn địa lý hoặc tài nguyên bất ngờ ngoài thực địa hay trên sa bàn chiến lược.
- Mọi cuộc xung đột hay hiệp ước đều phải quy về dòng chảy tiền, dầu, khoáng sản hoặc hàng hóa.
- Hình ảnh tuân thủ 3 trụ cột nhiếp ảnh thực tế & vật lý: (1) Địa hình vệ tinh 3D màu tự nhiên & sa bàn bàn phân tích địa chất; (2) Nhiếp ảnh Macro 100mm cơ chế cơ khí/vật lý; (3) Ảnh phóng sự công nghiệp & địa chính trị thực địa — đa dạng góc máy, vật liệu và ánh sáng theo từng tập, tuyệt đối không dùng đồ họa vector 2D phẳng, vòng radar viễn tưởng, HUD hay chữ chèn trong các beat nội dung.
- Không thiên vị chính trị; chỉ phân tích lợi ích quốc gia và địa lý cốt lõi.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Tử huyệt địa lý này giải thích vì sao [quốc gia] luôn [hành động].`
- `Nếu [eo biển/tuyến đường] này bị đóng, bữa ăn của bạn sẽ đắt gấp đôi.`
- `Vì sao tấm bản đồ này quyết định giá xăng dầu thế giới tuần tới?`
- `3 điểm nghẽn địa chính trị có thể làm tê liệt toàn cầu trong 48 giờ.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Hỏi người xem: bạn nghĩ điểm nghẽn tiếp theo nằm ở đâu? Bình luận nhé.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gợi mở chương tiếp theo về bàn cờ địa chính trị toàn cầu.
### Điều cấm kỵ (Avoid)
- Tuyên truyền chính trị một chiều
- Kích động thù hằn dân tộc
- Dự đoán chiến tranh giật gân vô căn cứ

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_tactical_atlas` — Nhiếp ảnh thực tế 3 trụ cột: Địa hình vệ tinh/Sa bàn thật, Macro 100mm cơ khí & Phóng sự công nghiệp
- **Bảng màu khóa cứng:** `#10202E`, `#D8CBB8`, `#C83E3B`, `#D98A3C`, `#2A6F68`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Character-free physical realism: natural satellite terrain reliefs, real geological ore specimens, physical brass navigation instruments, precision laboratory wafers, and real maritime freight vessels (zero human cartoon figures)
- **Trang phục (`DEFAULT_OUTFIT`):** No cartoon clothing; authentic industrial metals, natural mineral textures, laboratory steel, and weathered maritime hulls
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Full-bleed dramatic studio macro & 3D physical terrain relief photography (crimson steel locking clamp gripping silicon wafer or metal bar over natural relief map) + 2-4 bold yellow uppercase VN words with thick black outline in clean dark upper safe zone.
- **Prompt Style gốc:**
  > Three-pillar photorealistic geopolitical documentary photography with diverse per-episode lighting, materials, and focal lengths: (1) True-color 3D orbital satellite relief photography and physical walnut tabletop geological relief maps with brass compasses, steel dividers, raw ore stones, and solid metal bars; (2) 100mm macro physical and mechanical photography of real machinery, copper motor coils, silver permanent magnets, cleanroom silicon wafers, and hydrometallurgical tanks; (3) Photorealistic industrial, maritime, and field documentary photography; strictly zero flat 2D vector graphics, zero sci-fi HUD or radar rings, zero on-screen text clutter in body beats.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **30–40 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Flat 2D contour maps with Remotion animated trade-route arrows & choke-point pulses save 50% Flow calls.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Bàn Cờ Địa Chính Trị: 4 Điểm Nghẽn Hàng Hải Quyết Định Dòng Chảy Kinh Tế & Năng Lượng Toàn Cầu*
- **Thời lượng:** 14 phút (26 cảnh)
- **Câu mở đầu (Cold Open):** "Nếu một chiếc tàu container bị kẹt ngang một con kênh hẹp chỉ vài trăm mét, toàn bộ chuỗi cung ứng thế giới sẽ thiệt hại hàng tỷ USD mỗi ngày."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *xem bản đồ thế giới* (50s)
- **Spin-off #2 (0 ảnh mới):** *Kênh đào Suez: vì sao một con tàu kẹt làm cả thế giới chao đảo?* (45s)
- **Spin-off #3 (0 ảnh mới):** *Bản đồ đất hiếm: cuộc chiến ngầm đằng sau mọi chiếc điện thoại thông minh.* (50s)
- **Fast-Short #4 (5 ảnh Flow):** *Kênh đào Panama khô hạn: giá hàng hóa toàn cầu bị bóp nghẹt ra sao?* (50s)

### Backlog chủ đề hạt giống tiếp theo
- xem bản đồ thế giới
- Eo biển Malacca: yết hầu năng lượng quyết định vận mệnh Đông Á
- Kênh đào Suez: vì sao một con tàu kẹt làm cả thế giới mất hàng tỷ đô
- Bản đồ đất hiếm: cuộc chiến ngầm đằng sau mọi chiếc smartphone
- Kênh đào Panama khô hạn: giá hàng hóa toàn cầu bị bóp nghẹt ra sao

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#diachinhtri #bandoquyenluc #kinhtethegioi #lichsudialy #kienthuc`
- **Nguồn doanh thu:** YouTube AdSense RPM cao, Sponsor dịch vụ tài chính vĩ mô / logistics, Affiliate sách địa lý & chiến lược
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-ban-do-quyen-luc
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel ban_do_quyen_luc
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
