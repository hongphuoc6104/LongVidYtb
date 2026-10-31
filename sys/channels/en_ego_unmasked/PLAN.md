# KẾ HOẠCH CHI TIẾT KÊNH: EGO UNMASKED (`en_ego_unmasked`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_ego_unmasked` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-ego-unmasked` (`origin/channel/en-ego-unmasked`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-ego-unmasked`
- **Ngách nội dung:** Carl Jung depth psychology, Shadow Work, ego defense mechanisms & self-awareness
- **Lời hứa thương hiệu (Value Proposition):** Examine the shadow parts of your psyche, dissolve ego defenses, and gain genuine self-knowledge.
- **Khán giả mục tiêu:** Self-reflective adults interested in Jungian depth psychology and inner sovereignty
- **Nhân vật dẫn chuyện (Persona):** Calm philosophical analyst exploring the unconscious mind with respect and clarity
- **Giọng văn (Tone):** Reflective, profound, grounded, psychologically penetrating | **Giọng TTS:** `OmniVoice_EnEgoUnmasked` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Jungian Reflections** (YouTube): Punchy 40-second reflections on projection and ego traps.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Eternalised** (YouTube): In-depth explorations of Jungian archetypes, shadow, and existential philosophy.
- **Academy of Ideas** (YouTube): Psychological sovereignty, individualism, and Carl Jung case studies.
- **Man and His Symbols by Carl Jung & The Courage to Be Disliked** (Book/Scripture): Unconscious symbolism, shadow integration, and Adlerian psychology.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open with an uncomfortable ego defense mechanism viewers immediately recognize.
- Deconstruct the unconscious drive using Carl Jung's concepts simply.
- Keep the exploration objective, compassionate, and empowering.
- Conclude with an integrative reflection question for quiet journaling.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Carl Jung's Shadow Work explained: why what you hate in others is hidden in you.`
- `The spotlight effect: why nobody is judging you as much as you think.`
- `How your ego uses busyness to hide deep insecurity.`
- `The persona trap: what happens when you become your social mask.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Does this shadow dynamic ring true for you? Reflect with us below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Continue your inner exploration with our deep-dive on Ego Unmasked.
### Điều cấm kỵ (Avoid)
- Superficial pop-spirituality clichés
- Demonizing psychological defenses
- Mystical jargon without grounding

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_jungian_noir` — Jungian chiaroscuro noir: dramatic graphic-novel engraving, golden alchemical mirror, shadow masks
- **Bảng màu khóa cứng:** `#141418`, `#EAE2D3`, `#C89B3C`, `#9E2A2B`, `#FFFFFF`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Refined graphic-novel protagonist in charcoal high-collar coat holding an ivory theater mask beside a golden mirror silhouette
- **Trang phục (`DEFAULT_OUTFIT`):** High-collared charcoal frock coat over dark vest with alchemical gold pocket-watch chain, no shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Character removing ivory mask revealing golden silhouette + 2-4 uppercase words.
- **Prompt Style gốc:**
  > Dramatic 2D chiaroscuro graphic-novel engraving on ivory parchment canvas (#141418 obsidian ink black, #EAE2D3 ivory parchment, #C89B3C alchemical mirror gold, #9E2A2B shadow crimson); high-contrast psychological shadow archetypes, dual theater masks, and symbolic golden mirrors; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion subtle shadow silhouette dissolve and mirror reflection animations.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Carl Jung's Shadow Work Explained: Why What You Hate in Others Is Hidden in You*
- **Thời lượng:** 13 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "What if the traits that irritate you most in other people are actually rejected parts of yourself?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *shadow projection* (45s)
- **Spin-off #2 (0 new images):** *The spotlight effect: why nobody is judging you as much as you think.* (40s)
- **Spin-off #3 (0 new images):** *How your ego uses non-stop busyness to hide deep insecurity.* (45s)
- **Fast-Short #4 (5 Flow images):** *The persona trap: what happens when you become your social mask.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Carl Jung's Shadow Work Explained: Why What You Hate in Others Is Hidden in You
- The Spotlight Effect: Why Nobody Is Judging You as Much as You Think
- How Your Ego Uses Busyness to Hide Deep Insecurity
- The Persona Trap: What Happens When You Become Your Social Mask
- 5 Defense Mechanisms Your Mind Uses Without Your Permission

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#psychology #carljung #shadowwork #philosophy #selfawareness #mindset`
- **Nguồn doanh thu:** YouTube AdSense (long), Shadow work guided workbook, Depth philosophy book curation
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-ego-unmasked
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_ego_unmasked
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
