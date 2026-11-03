# KẾ HOẠCH CHI TIẾT KÊNH: SPAWN TO APEX (`en_wait_how`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_wait_how` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-wait-how` (`origin/channel/en-wait-how`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-wait-how`
- **Ngách nội dung:** Extreme animal & insect metamorphosis, deep-sea life cycles & parasite survival chronicles
- **Lời hứa thương hiệu (Value Proposition):** Trace nature's most extreme life cycles from microscopic spawn to final metamorphosis.
- **Khán giả mục tiêu:** Curious adults, biology lovers, and viewers hooked on bizarre chronological life-cycle transformations
- **Nhân vật dẫn chuyện (Persona):** Natural history metamorphosis chronicler tracking Day-1 larvae through impossible biological transformations
- **Giọng văn (Tone):** Riveting, chronological, wonder-filled, lucid, documentary-grade biological storytelling | **Giọng TTS:** `OmniVoice_EnWaitHow` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Deep Look Shorts** (TikTok/YouTube Shorts): High-retention 45-second close-up metamorphosis and survival hooks.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Ze Frank & Deep Look (KQED)** (YouTube): Macro biological storytelling of insect metamorphosis, parasites, and marine life cycles.
- **Metamorphosis Insectorum Surinamensium by Maria Sibylla Merian** (Book/Scripture): Pioneering chronological life-cycle illustration uniting egg, larva, pupa, and host plant.
- **Journey to the Microcosmos** (YouTube): Poetic, hypnotic narration of microscopic and larval life cycles.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open at the most fragile or bizarre stage of the creature's life cycle within 3 seconds.
- Track every metamorphosis instar chronologically with exact Day/Hour milestones.
- Use cutaway lithograph plates to show what happens inside the cocoon, shell, or deep-sea abyss.
- End with the evolutionary payoff that makes this extreme life cycle worth the 99% mortality rate.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Inside the chrysalis: how a caterpillar completely dissolves into soup and rebuilds its brain.`
- `Why every freshwater eel on Earth swims 4,000 miles to the Sargasso Sea just to die.`
- `Day 1 to Day 17 Years: how periodical cicadas count the seasons underground.`
- `How the immortal jellyfish reverses its own aging process back into a polyp.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Which stage of this metamorphosis blew your mind? Let us know below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Follow our next extreme life-cycle chronicle on Spawn to Apex on YouTube.
### Điều cấm kỵ (Avoid)
- Childish cartoon mascots
- Clickbait fake biology
- Skipping stages of the chronological life cycle

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_sticker_pop` — Merian Natural History Metamorphosis Plate: dip-pen lithograph & watercolor life-cycle rings on specimen vellum
- **Bảng màu khóa cứng:** `#F6F0DD`, `#2E6F65`, `#D97941`, `#8C3B4A`, `#1D3557`, `#1A1D24`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Sequential natural-history metamorphosis plate drawn in fine dip-pen cross-hatching and watercolor wash on specimen vellum, showing translucent egg, larva, cutaway chrysalis, and mature organism framed by a brass naturalist magnifier
- **Trang phục (`DEFAULT_OUTFIT`):** Natural biological exoskeletons, translucent chrysalis membranes, and engraved taxonomic stage markers, no human clothing
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Translucent cutaway of chrysalis or deep-sea larva metamorphosis + 2-4 uppercase engraved words on vellum.
- **Prompt Style gốc:**
  > Authentic 2D Maria Sibylla Merian and natural-history museum metamorphosis lithograph and dip-pen watercolor plate on warm specimen vellum (#F6F0DD fibrous specimen vellum, #1A1D24 fine lithographic dip-pen ink, #2E6F65 deep-sea bioluminescent teal wash, #D97941 chrysalis amber, #8C3B4A gill carmine); chronological life-cycle progression diagrams (Egg -> Larval Instar -> Translucent Chrysalis Cutaway -> Mature Specimen) with brass magnifying-lens callouts; orthographic 2D, tactile scientific lithograph texture, at least 60% negative space, zero 3D CGI, zero cartoon stickers, zero plastic AI glow, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion chronological Stage 1-4 metamorphosis wheel and cutaway zoom transitions.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Inside the Chrysalis: How a Caterpillar Dissolves into Liquid and Rebuilds Its Brain*
- **Thời lượng:** 13 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "If you cut open a monarch chrysalis on Day 4, you will not find a half-formed butterfly—you will find digestive enzymes dissolving the caterpillar into soup."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *chrysalis metamorphosis cutaway* (45s)
- **Spin-off #2 (0 new images):** *Why every freshwater eel on Earth swims 4,000 miles to the Sargasso Sea to die.* (45s)
- **Spin-off #3 (0 new images):** *17 years underground: how periodical cicadas count tree sap cycles in the dark.* (45s)
- **Fast-Short #4 (5 Flow images):** *The immortal jellyfish: how Turritopsis dohrnii reverses its own life cycle.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Inside the Chrysalis: How a Caterpillar Dissolves into Liquid and Rebuilds Its Brain
- Why Every Eel on Earth Swims 4,000 Miles to the Sargasso Sea Just to Spawn and Die
- 17 Years Underground: How Periodical Cicadas Count Tree Sap Cycles in the Dark
- The Immortal Jellyfish: How Turritopsis Dohrnii Reverses Its Own Life Cycle
- How the Axolotl Refused to Grow Up—And Unlocked Whole-Limb Regeneration

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#metamorphosis #lifecycle #biology #nature #evolution #science`
- **Nguồn doanh thu:** YouTube AdSense (long), Natural history metamorphosis lithograph prints, Science & wildlife documentary sponsor
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-wait-how
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_wait_how
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
