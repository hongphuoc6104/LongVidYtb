# KẾ HOẠCH CHI TIẾT KÊNH: KINDRED SKETCH (`en_kindred_sketch`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_kindred_sketch` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-kindred-sketch` (`origin/channel/en-kindred-sketch`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-kindred-sketch`
- **Ngách nội dung:** Attachment styles, relationship psychology, emotional intelligence & communication
- **Lời hứa thương hiệu (Value Proposition):** Make sense of relationship conflicts, attachment wounds, and emotional patterns with empathy.
- **Khán giả mục tiêu:** Couples, singles, and friends wanting emotionally mature, communicative relationships
- **Nhân vật dẫn chuyện (Persona):** Warm relationship counselor friend who validates emotional pain while guiding healthy repair
- **Giọng văn (Tone):** Warm, gentle, emotionally literate, compassionate, grounded in attachment research | **Giọng TTS:** `OmniVoice_EnKindredSketch` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Psych2Go Shorts** (TikTok/YouTube Shorts): Gentle relatable relationship queries.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Psych2Go** (YouTube): Gentle animated relationship breakdowns and attachment insights.
- **Cinema Therapy** (YouTube): Empathy-first relationship coaching and conflict resolution.
- **Attached by Amir Levine & The Seven Principles by John Gottman** (Book/Scripture): Foundational empirical relationship science and conflict repair.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Begin with an emotional tension anyone in a relationship recognizes immediately.
- Validate both sides without taking sides or assigning blame.
- Use physical metaphors like bridges or shields to explain emotional defense.
- End with one gentle phrasing shift for constructive communication.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Why anxious and avoidant partners always seem to attract each other.`
- `Why the silent treatment hurts the brain like physical pain.`
- `4 subtle signs of emotional burnout in long relationships.`
- `How one simple phrasing shift stops arguments before they escalate.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Has this dynamic ever shown up in your life? Let us know below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Discover the full relationship masterclass on Kindred Sketch YouTube.
### Điều cấm kỵ (Avoid)
- Toxic couple shaming
- Dating manipulation advice
- Armchair relationship diagnosis

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_pastel_duo` — Soft pastel warm-line duo: Psych2Go-inspired empathetic characters Leo and Maya on warm cream
- **Bảng màu khóa cứng:** `#FFF8F0`, `#5B4636`, `#F7C6C7`, `#CDB4DB`, `#BDE0C6`, `#FFF1B5`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Recurring expressive young couple and friends duo — Leo (warm wavy brown hair, kind eyes, flat mint sweater) and Maya (shoulder-length dark bob hair, expressive eyes, flat blush cardigan)
- **Trang phục (`DEFAULT_OUTFIT`):** Leo in flat sage-mint (#BDE0C6) crewneck sweater; Maya in soft blush-pink (#F7C6C7) button cardigan
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Leo and Maya having an honest conversation + 2-4 uppercase words on soft cream canvas.
- **Prompt Style gốc:**
  > Soft Psych2Go-inspired 2D pastel line-art illustration on warm cream canvas (#FFF8F0 warm cream canvas, #5B4636 smooth warm-espresso outlines, #F7C6C7 blush pink, #CDB4DB soft lavender, #BDE0C6 sage mint, #FFF1B5 butter yellow); gentle emotional storytelling, warm domestic and relational vignettes; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion gentle speech bubble transitions and emotional connection pulses.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Why Anxious and Avoidant Partners Always Attract Each Other (And How to Heal)*
- **Thời lượng:** 13 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "Why do the very qualities that drew you together in the beginning become the exact triggers in arguments?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *attachment loop* (45s)
- **Spin-off #2 (0 new images):** *Why the silent treatment hurts the brain like physical pain.* (40s)
- **Spin-off #3 (0 new images):** *4 subtle signs of emotional burnout in long-term relationships.* (45s)
- **Fast-Short #4 (5 Flow images):** *How one phrasing shift stops arguments before they escalate.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Why Anxious and Avoidant Partners Always Attract Each Other
- Why the Silent Treatment Hurts the Brain Like Physical Pain
- 4 Subtle Signs of Emotional Burnout in Long Relationships
- How One Phrasing Shift Stops Arguments Before They Escalate
- Why People Who Grow Up Hyper-Independent Struggle to Ask for Help

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#relationships #attachmentstyle #emotionalintelligence #communication #couples #mentalhealth`
- **Nguồn doanh thu:** YouTube AdSense (long), Couples communication prompt cards, Mental health therapy app sponsor
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-kindred-sketch
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_kindred_sketch
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
