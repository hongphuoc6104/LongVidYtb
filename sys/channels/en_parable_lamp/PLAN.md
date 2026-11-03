# KẾ HOẠCH CHI TIẾT KÊNH: DEEP TIME STRATA (`en_parable_lamp`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_parable_lamp` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-parable-lamp` (`origin/channel/en-parable-lamp`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-parable-lamp`
- **Ngách nội dung:** Paleo-evolutionary turning points, geological strata epochs, mass extinctions & ancient ecosystems
- **Lời hứa thương hiệu (Value Proposition):** Excavate Earth's geological strata to witness how life survived five mass extinctions and conquered dry land.
- **Khán giả mục tiêu:** Paleontology enthusiasts, deep-time history fans, and viewers captivated by ancient Earth ecosystems
- **Nhân vật dẫn chuyện (Persona):** Deep-time paleontologist narrating Earth's ancient ecosystems and evolutionary bottlenecks layer by rock layer
- **Giọng văn (Tone):** Epic, investigative, chronological, grounded in paleontology and geological stratigraphy | **Giọng TTS:** `OmniVoice_EnParableLamp` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **PBS Eons Shorts** (YouTube Shorts): 60-second fossil mysteries and deep-time evolutionary twists.
### Kênh mẫu YouTube Long (`long_16x9`)
- **PBS Eons & Moth Light Media** (YouTube): Deep-time paleontology, obscure evolutionary lineages, and mass extinction reconstructions.
- **History of the Earth** (YouTube): Chronological epoch-by-epoch documentary storytelling of ancient biospheres.
- **The Ends of the World by Peter Brannen & Annals of the Former World** (Book/Scripture): Geological stratigraphy and the five mass extinctions.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open at a specific geological boundary layer (e.g. 252 million years ago during the Great Dying) within 3 seconds.
- Unpack the chain reaction across ocean chemistry, atmosphere, and ancient reptiles/flora chronologically.
- Use carved rock-strata cross-sections and fossil specimen plates to show what vanished and what adapted.
- End with how that ancient evolutionary bottleneck shaped the anatomy of living creatures today.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `When giant 100-foot fungi ruled the Earth before trees even evolved.`
- `The Great Dying: how a tiny burrowing synapsid survived the worst extinction in Earth's history.`
- `Why Evolution keeps turning completely unrelated animals into crabs (Carcinisation).`
- `How a 60-million-year gap without wood-eating microbes created all the coal on Earth.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Which prehistoric epoch would you be most terrified to visit? Comment below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Excavate our next deep-time geological chronicle on Deep Time Strata on YouTube.
### Điều cấm kỵ (Avoid)
- Hollywood movie monster clichés
- Creationist or pseudoscientific timelines
- Dry mineral lists without survival drama

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_parable_woodcut` — Carved Paleo-Lithograph & Geological Strata Woodcut: aged fossil parchment, relief gouge lines, amber & fern green
- **Bảng màu khóa cứng:** `#EFE4C8`, `#1E1E1E`, `#D9A520`, `#5E7D3A`, `#A44A3F`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Carved woodcut field paleontologist in rugged expedition canvas coat holding a brass geological hammer and oil lantern beside stratified fossil cliff layers and prehistoric tetrapod footprints
- **Trang phục (`DEFAULT_OUTFIT`):** Hand-carved terracotta-and-ochre expedition canvas coat with leather field satchel and geological hammer, zero modern plastic details
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Woodcut geological cliff strata revealing giant fossil skeleton and amber egg + 2-4 uppercase carved words.
- **Prompt Style gốc:**
  > Expressive 2D carved paleo-lithograph and linocut geological strata print on aged fossil-matrix parchment (#EFE4C8 aged fossil parchment, #1E1E1E bold carved woodcut ink, #D9A520 amber fossil gold, #5E7D3A Carboniferous fern green, #A44A3F Permian red-bed terracotta); textured woodblock relief gouge lines, geological rock-strata timelines, fossilized skeletons, amniotic eggs, and ancient giant fern forests; orthographic 2D, tactile hand-carved printmaking texture, at least 60% negative space, zero 3D CGI, zero plastic AI glow, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion Million-Year geological depth counter and rock-strata scroll transitions.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *When Giant 30-Foot Fungi Ruled the Continents Before Trees Evolved (Deep Time Strata)*
- **Thời lượng:** 14 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "Four hundred million years ago, before a single tree existed on dry land, towering twenty-six-foot spires of living fungus dominated every coastline on Earth."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *prehistoric giant fungi* (45s)
- **Spin-off #2 (0 new images):** *The Great Dying: how one burrowing creature survived the Permian extinction.* (45s)
- **Spin-off #3 (0 new images):** *Why evolution keeps turning unrelated crustaceans into crabs (carcinisation).* (45s)
- **Fast-Short #4 (5 Flow images):** *How the Carboniferous forest fire era created all the coal on Earth.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- When Giant 30-Foot Fungi Ruled the Continents Before Trees Evolved
- The Great Dying: How One Burrowing Creature Survived the Permian Extinction
- Why Evolution Keeps Turning Unrelated Crustaceans into Crabs (Carcinisation)
- How the Carboniferous Forest Fire Era Created Earth's Coal Seams
- How the First Tetrapods Crawled Out of Devonian Mud onto Dry Land

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#paleontology #deeptime #evolution #geology #fossils #prehistoric`
- **Nguồn doanh thu:** YouTube AdSense (long), Carved geological strata & fossil timeline prints, Natural history museum & science sponsor
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-parable-lamp
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_parable_lamp
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
