# KẾ HOẠCH CHI TIẾT KÊNH: ROOT & CANOPY (`en_kitchen_molecules`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_kitchen_molecules` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-kitchen-molecules` (`origin/channel/en-kitchen-molecules`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-kitchen-molecules`
- **Ngách nội dung:** Plant evolution through deep time, seed-to-giant life-cycle time-lapses & botanical warfare
- **Lời hứa thương hiệu (Value Proposition):** Witness the hidden time-lapse warfare of plants—from dormant seed to 2,000-year canopy giant.
- **Khán giả mục tiêu:** Nature documentary enthusiasts, botanical science fans, and viewers fascinated by time-lapse life cycles
- **Nhân vật dẫn chuyện (Persona):** Botanical time-lapse chronicler revealing plants as slow-motion gladiators and chemical engineers
- **Giọng văn (Tone):** Hypnotic, chronological, dramatic, revealing hidden underground and canopy survival battles | **Giọng TTS:** `OmniVoice_EnKitchenMolecules` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Botanical Time-Lapse Shorts** (TikTok/YouTube Shorts): 60-second seed-to-canopy growth and carnivorous plant traps.
### Kênh mẫu YouTube Long (`long_16x9`)
- **BBC Earth — The Green Planet (Sir David Attenborough)** (YouTube): Time-lapse cinematography framing plant growth as high-stakes predator-prey drama.
- **Crime Pays But Botany Doesn't & PBS Eons** (YouTube): Evolutionary botany, plant ecology, and deep-time floral history.
- **The Hidden Life of Trees by Peter Wohlleben & Finding the Mother Tree** (Book/Scripture): Mycorrhizal underground networks and forest survival strategies.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open at Day 0 inside the dormant seed coat or underground root network within 3 seconds.
- Use chronological time-lapse progression (Day 1 -> Month 6 -> Year 50 -> Century 10) to reveal plant movement as active warfare.
- Show split soil-and-canopy cross-sections of root xylem conduits, mycorrhizal fungal webs, and chemical defense toxins.
- End with how this botanical strategy reshaped Earth's atmosphere or forest ecosystems.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Year 1 to Year 200: how a strangler fig slowly devours a rainforest giant from the sky down.`
- `Why some pine cones refuse to open until a wildfire burns the forest alive.`
- `The 60-million-year hostage pact between a fig tree and a dying wasp.`
- `How carnivorous pitcher plants lure, drown, and digest prey in acid rainwater.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Did you know plants fought this fiercely in slow motion? Comment below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Watch the next botanical time-lapse survival story on Root & Canopy YouTube.
### Điều cấm kỵ (Avoid)
- Treating plants as passive static scenery
- Childish cartoon flower faces
- Dry gardening tips without evolutionary storytelling

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_culinary_sticker` — Kew Gardens & Audubon Botanical Time-Lapse Codex: copperplate engraving, herbarium watercolor & soil strata cutaway
- **Bảng màu khóa cứng:** `#F4EFE0`, `#3A6B4C`, `#B85D3B`, `#D4A359`, `#2B3A2E`, `#1E241E`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Botanical specimen cross-section plate drawn in fine copperplate dip-pen cross-hatching and mineral watercolor, tracing a living plant from buried seed coat cracking in dark terracotta soil strata up to mature forest canopy with brass magnifier callouts
- **Trang phục (`DEFAULT_OUTFIT`):** Natural botanical bark, root xylem vascular cross-sections, and copperplate taxonomic specimen labels, zero human clothing
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Split soil-and-canopy cross-section of giant root network and germinating seed + 2-4 uppercase engraved words.
- **Prompt Style gốc:**
  > Authentic 2D Kew Gardens and Audubon botanical copperplate ink engraving and pressed-herbarium watercolor wash on warm deckle-edge rag paper (#F4EFE0 fibrous herbarium paper, #1E241E botanical India ink cross-hatching, #3A6B4C chlorophyll forest green, #B85D3B underground soil-strata terracotta, #D4A359 amber resin gold); split above-and-below-ground soil strata cross-sections showing chronological seed germination (Day 1 to Year 200), root xylem networks, mycorrhizal fungal threads, and carnivorous leaf traps; orthographic 2D, tactile botanical museum plate texture, at least 60% negative space, zero 3D CGI, zero kawaii stickers, zero plastic AI glow, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion time-lapse Day/Year counters and underground root-growth cross-section reveals.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Year 1 to Year 200: How a Strangler Fig Slowly Devours a Rainforest Giant*
- **Thời lượng:** 13 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "It begins as a single sticky seed dropped by a bird high in the canopy, and ends two centuries later as a hollow cage around a dead forest giant."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *strangler fig time-lapse* (45s)
- **Spin-off #2 (0 new images):** *Why some pine cones refuse to open until a wildfire burns the forest alive.* (45s)
- **Spin-off #3 (0 new images):** *The 60-million-year hostage pact between a fig tree and a dying wasp.* (45s)
- **Fast-Short #4 (5 Flow images):** *How carnivorous pitcher plants lure, drown, and digest insects in acid water.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Year 1 to Year 200: How a Strangler Fig Slowly Devours a Rainforest Giant
- Why Some Pine Cones Refuse to Open Until a Wildfire Burns the Forest Alive
- The 60-Million-Year Hostage Pact Between a Fig Tree and a Dying Wasp
- How Carnivorous Pitcher Plants Lure, Drown, and Digest Insects in Acid Rainwater
- How Grass Conquered the Planet and Engineered Grazing Mammals

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#botany #plants #timelapse #evolution #naturedocumentary #lifecycle`
- **Nguồn doanh thu:** YouTube AdSense (long), Archival botanical copperplate herbarium prints, Nature & science documentary sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-kitchen-molecules
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_kitchen_molecules
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
