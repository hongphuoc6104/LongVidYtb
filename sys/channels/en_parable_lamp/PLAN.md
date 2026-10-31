# KẾ HOẠCH CHI TIẾT KÊNH: PARABLE & LAMP (`en_parable_lamp`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_parable_lamp` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-parable-lamp` (`origin/channel/en-parable-lamp`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-parable-lamp`
- **Ngách nội dung:** Biblical parables, wisdom of Proverbs & Ecclesiastes, forgiveness, grace & hope illustrated
- **Lời hứa thương hiệu (Value Proposition):** Illuminate timeless biblical parables, wisdom literature, and hope with heartwarming stick figures.
- **Khán giả mục tiêu:** Faith seekers, lovers of timeless moral parables, and viewers seeking forgiveness and hope
- **Nhân vật dẫn chuyện (Persona):** Kind biblical storyteller unpacking ancient wisdom with warmth, grace, and humility
- **Giọng văn (Tone):** Warm, inspiring, reflective, gracious, literary | **Giọng TTS:** `OmniVoice_EnParableLamp` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **BibleProject Shorts** (YouTube Shorts): 60-second word studies and visual parable summaries.
### Kênh mẫu YouTube Long (`long_16x9`)
- **BibleProject** (YouTube): Literary analysis and visual theology of biblical narratives.
- **IMBeggar** (YouTube): Poetic, hand-drawn reflections on forgiveness, humility, and grace.
- **Ascension Presents** (YouTube): Practical life wisdom derived from timeless moral scriptures.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Begin with an ancient moral parable and its immediate modern parallel.
- Unpack the historical context and original literary meaning with care.
- Emphasize forgiveness, self-examination, and stewardship over moral superiority.
- End with an uplifting message of hope, reconciliation, and quiet purpose.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `The Parable of the Talents explained: what a 2,000-year-old story reveals about fear.`
- `Why forgiving someone who hurt you is the only way to set yourself free.`
- `The Prodigal Son: why both brothers missed the father's heart.`
- `5 timeless lessons on wealth and humility from the Book of Proverbs.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Has this parable spoken to your journey today? Let us know below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Discover more timeless biblical wisdom on Parable & Lamp on YouTube.
### Điều cấm kỵ (Avoid)
- Sectarian doctrinal attacks
- Doomsday condemnation or fear-based messaging
- Twisting ancient texts out of context

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_parable_woodcut` — Carved woodblock parable print: BibleProject linocut relief, radiant oil-lamp gold, ancient parchment
- **Bảng màu khóa cứng:** `#EFE4C8`, `#1E1E1E`, `#D9A520`, `#5E7D3A`, `#A44A3F`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Warm woodcut human parable narrator in ancient woven cloak holding a radiant golden clay oil lamp and olive branch
- **Trang phục (`DEFAULT_OUTFIT`):** Hand-carved Galilean terracotta tunic draped under a woven ochre mantle, no modern garments
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Woodcut narrator holding radiant oil lamp in dark courtyard + 2-4 uppercase words.
- **Prompt Style gốc:**
  > Expressive BibleProject-inspired 2D carved woodblock and linocut parable print on aged parchment canvas (#EFE4C8 aged parchment, #1E1E1E bold carved woodcut ink, #D9A520 glowing lamp gold, #5E7D3A olive-leaf green, #A44A3F Galilean terracotta); textured relief gouge lines, radiant lamps, olive trees and timeless architectural arches; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion warm lamp glow overlays and parchment scroll unroll animations.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *The Parable of the Talents Explained: What a 2,000-Year-Old Story Reveals About Fear*
- **Thời lượng:** 13 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "The servant who buried his single talent did not fail from lack of skill, but from paralyzing fear."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *ancient parable study* (45s)
- **Spin-off #2 (0 new images):** *Why forgiving someone who hurt you is the only way to set yourself free.* (40s)
- **Spin-off #3 (0 new images):** *The Prodigal Son: why both brothers missed the father's heart.* (45s)
- **Fast-Short #4 (5 Flow images):** *5 timeless lessons on wealth and humility from the Book of Proverbs.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- The Parable of the Talents Explained: What a 2,000-Year-Old Story Reveals About Fear
- Why Forgiving Someone Who Hurt You Is the Only Way to Set Yourself Free
- The Prodigal Son: Why Both Brothers Missed the Father's Heart
- 5 Timeless Lessons on Wealth and Humility from the Book of Proverbs
- The Good Samaritan: Why Compassion Always Crosses Invisible Boundaries

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#parables #wisdom #hope #faith #proverbs #forgiveness`
- **Nguồn doanh thu:** YouTube AdSense (long), Illustrated proverb study cards, Christian literature and family audiobooks partner
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-parable-lamp
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_parable_lamp
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
