# KẾ HOẠCH CHI TIẾT KÊNH: POCKET COSMOS (`en_pocket_cosmos`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_pocket_cosmos` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-pocket-cosmos` (`origin/channel/en-pocket-cosmos`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-pocket-cosmos`
- **Ngách nội dung:** Astrophysics, black holes, quantum paradoxes & spacetime explained in Feynman style
- **Lời hứa thương hiệu (Value Proposition):** Explain mind-bending astrophysics and spacetime paradoxes using everyday analogies and gentle stick figures.
- **Khán giả mục tiêu:** Space lovers, students, science fiction thinkers, and curious cosmologists
- **Nhân vật dẫn chuyện (Persona):** Enthusiastic Feynman-style cosmic companion bringing relativistic physics down to Earth
- **Giọng văn (Tone):** Awe-inspiring, lucid, poetic yet rigorous, Feynman-esque | **Giọng TTS:** `OmniVoice_EnPocketCosmos` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Astronomy Shorts** (YouTube Shorts): 60-second cosmic scale comparisons and black hole facts.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Kurzgesagt – Space Series** (YouTube): Cosmic scale, existential risks, and theoretical astrophysics visualized.
- **ScienceClic English & Up and Atom** (YouTube): Relativistic spacetime physics and quantum mechanics rendered intuitively.
- **Six Easy Pieces by Richard Feynman** (Book/Scripture): Masterful reduction of fundamental physics to everyday analogies.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with a cosmic thought experiment that breaks common sense completely.
- Use clean stick figures and everyday physical props like clocks or rubber sheets.
- Explain the relativistic math intuitively without intimidating equations.
- End with a breathtaking existential realization about our place in the cosmos.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `If the Sun disappeared right now, how long would Earth actually survive?`
- `Why one hour near a black hole equals seven years on Earth.`
- `Fermi's paradox: where is everybody in a galaxy of billions of stars?`
- `Quantum entanglement explained without mysticism or jargon.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Does the scale of the cosmos blow your mind? Tell us below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Journey through the wonders of spacetime with Pocket Cosmos on YouTube.
### Điều cấm kỵ (Avoid)
- Sci-fi fantasy masquerading as real physics
- Overly mystical spiritual claims
- Dry tensor mathematics without physical intuition

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_cosmos_vector` — Deep-space geometric vector: Kurzgesagt-style cosmic indigo, vibrant nebula colors, robotic probe Nova
- **Bảng màu khóa cứng:** `#0B1026`, `#4CC9F0`, `#F72585`, `#FFD166`, `#7209B7`, `#FFFFFF`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Cute spherical golden-and-white deep-space probe mascot Nova with a glowing cyan digital eye and tiny solar-panel wings orbiting luminous geometric planets
- **Trang phục (`DEFAULT_OUTFIT`):** Polished white ceramic body shell with gold accents and solar-panel wings, no human clothing
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Mascot Nova orbiting a glowing ringed planet + 2-4 uppercase words on deep indigo.
- **Prompt Style gốc:**
  > Vibrant Kurzgesagt-inspired 2D flat geometric space vector art on deep space indigo canvas (#0B1026 deep space indigo, #4CC9F0 pulsar cyan, #F72585 nebula magenta, #FFD166 solar gold, #7209B7 cosmic violet) with clean lineless rounded vector forms, geometric celestial spheres, gravitational lensing curves; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion spacetime curvature mesh animations and relativistic clock warp effects.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *If the Sun Disappeared Right Now, How Long Would Earth Actually Survive?*
- **Thời lượng:** 13 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "If the Sun vanished this second, Earth would stay in light and gravitational orbit for eight minutes."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *cosmic spacetime scale* (45s)
- **Spin-off #2 (0 new images):** *Why one hour near a black hole equals seven years on Earth.* (45s)
- **Spin-off #3 (0 new images):** *Fermi's Paradox: where is everybody in a galaxy of billions of stars?* (40s)
- **Fast-Short #4 (5 Flow images):** *Quantum entanglement explained without mysticism or jargon.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- If the Sun Disappeared Right Now, How Long Would Earth Actually Survive?
- Why One Hour Near a Black Hole Equals Seven Years on Earth
- Fermi's Paradox: Where Is Everybody in a Galaxy of Billions of Stars?
- Quantum Entanglement Explained Without Mysticism or Jargon
- What Actually Happens If You Cross the Event Horizon of a Supermassive Black Hole?

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#space #astrophysics #cosmos #physics #blackhole #science`
- **Nguồn doanh thu:** YouTube AdSense (long), Illustrated cosmic infographic prints, Space exploration & science app sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-pocket-cosmos
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_pocket_cosmos
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
