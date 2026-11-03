# KẾ HOẠCH CHI TIẾT KÊNH: SCALE & BONE (`en_plain_sight_ai`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_plain_sight_ai` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-plain-sight-ai` (`origin/channel/en-plain-sight-ai`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-plain-sight-ai`
- **Ngách nội dung:** Reptile & amphibian evolution, egg-to-apex life-cycle survival stories & ancient biomechanics
- **Lời hứa thương hiệu (Value Proposition):** Follow the visceral life-cycle of reptiles from leathery egg to apex survivor across 300 million years of evolution.
- **Khán giả mục tiêu:** Nature documentary lovers, evolutionary biology fans, and viewers captivated by survival life-cycles
- **Nhân vật dẫn chuyện (Persona):** Field herpetologist and evolutionary anatomist narrating chronological survival from Day-1 hatchling to apex predator
- **Giọng văn (Tone):** Visceral, chronological, suspenseful, documentary-grade, grounded in evolutionary biomechanics | **Giọng TTS:** `OmniVoice_EnPlainSightAI` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Natural History Life-Cycle Shorts** (TikTok/YouTube Shorts): 60-second egg-to-apex reptile survival timelines.
### Kênh mẫu YouTube Long (`long_16x9`)
- **PBS Eons** (YouTube): Chronological deep-time evolutionary storytelling and fossil biomechanics.
- **TierZoo & Clint's Reptiles** (YouTube): Engaging herpetology, reptile survival mechanics, and evolutionary trade-offs.
- **Your Inner Fish by Neil Shubin & The Rise and Fall of the Dinosaurs** (Book/Scripture): Comparative vertebrate anatomy and amniotic egg evolution.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open inside the leathery egg or at Day 1 of the hatchling's survival gauntlet within 3 seconds.
- Follow a strict chronological life-cycle arc: Egg -> Hatchling Sprint -> Juvenile Molting -> Adult Biomechanics -> Deep-Time Evolution.
- Reveal anatomical cross-sections of venom glands, thermal pit organs, or osteoderm bone armor.
- End with how this ancient reptile body plan survived mass extinctions that wiped out rival species.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `From Day 1 to Year 15: how a tiny Komodo hatchling survives a forest of cannibal adults.`
- `Inside the leathery egg: how reptiles broke free from the ocean 310 million years ago.`
- `How snakes lost all four legs and evolved infrared thermal vision instead.`
- `Why the crocodile body plan has barely changed since before the dinosaurs.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Which stage of this reptile's life cycle amazed you most? Comment below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Explore our next evolutionary life-cycle chronicle on Scale & Bone YouTube.
### Điều cấm kỵ (Avoid)
- Plastic 3D CGI monsters
- Dry textbook taxonomy lists without chronological story
- Sensationalized fake creature myths

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_ai_doodle` — Darwin & Haeckel Zoological Field Codex: copperplate dip-pen cross-hatching & mineral watercolor on cotton rag paper
- **Bảng màu khóa cứng:** `#F2EAD7`, `#4A6B53`, `#C86D51`, `#D9C5A0`, `#2E4361`, `#1C1917`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Iconic 2D field-expedition doodle stickman naturalist with oversized hand-drawn white (#FFFFFF) bald circle head, dip-pen black outline, expedition pith-helmet brim, wire arms, and round circle hands holding brass calipers beside detailed copperplate reptile specimens
- **Trang phục (`DEFAULT_OUTFIT`):** Matte olive-khaki (#4A6B53) field naturalist waistcoat with brass specimen magnifying lens, zero digital shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Cross-section of reptile hatchling emerging from leathery egg on naturalist field codex + 2-4 uppercase inked words.
- **Prompt Style gốc:**
  > Authentic 19th-century Darwin and Haeckel naturalist zoological field codex illustration on aged cotton rag paper (#F2EAD7 deckle-edge paper grain): razor-sharp iron-gall dip-pen cross-hatching (#1C1917), muted mineral watercolor washes in reptile olive-scale (#4A6B53), venom-gland ochre (#C86D51), fossil bone ivory (#D9C5A0) and slate (#2E4361); chronological life-cycle specimen plates (leathery egg cross-section, Day-1 hatchling, skin-shedding ecdysis, hollow fang biomechanics, and osteoderm armor) alongside a field naturalistsketchingstickman observer; orthographic 2D, tactile museum engraving texture, at least 60% negative space, zero 3D CGI, zero plastic AI sheen, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **6–9 phút** cho 1 TikTok Short độc lập; **24–34 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion chronological Day-1 to Year-15 timeline counters and anatomical cross-section callouts.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *From Egg to Cannibal Forest: How a Baby Komodo Dragon Survives Its First 5 Years*
- **Thời lượng:** 13 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "The moment a baby Komodo dragon slices through its leathery egg, its biggest predator is waiting right outside the nest: its own mother."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *Komodo hatchling tree sprint* (45s)
- **Spin-off #2 (0 new images):** *How snakes lost their legs and evolved infrared thermal vision instead.* (45s)
- **Spin-off #3 (0 new images):** *Inside the leathery egg: how reptiles broke free from the ocean.* (45s)
- **Fast-Short #4 (5 Flow images):** *Why the crocodile body plan survived two mass extinctions unchanged.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- From Egg to Cannibal Forest: How a Baby Komodo Dragon Survives Its First 5 Years
- How Snakes Lost Their Legs—And Evolved Infrared Thermal Pit Organs Instead
- Inside the Leathery Egg: How Reptiles Conquered Dry Land 310 Million Years Ago
- Why the Crocodile Body Plan Survived Two Mass Extinctions Unchanged
- The Biomechanics of a Viper Fang: How a Saliva Gland Turned into a Hypodermic Syringe

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#reptiles #evolution #herpetology #lifecycle #naturedocumentary #biology`
- **Nguồn doanh thu:** YouTube AdSense (high documentary RPM), Naturalist copperplate reptile field prints, Wildlife & science documentary sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-plain-sight-ai
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_plain_sight_ai
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
