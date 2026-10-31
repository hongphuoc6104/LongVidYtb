# KẾ HOẠCH CHI TIẾT KÊNH: THE SECOND ARROW (`en_second_arrow`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_second_arrow` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-second-arrow` (`origin/channel/en-second-arrow`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-second-arrow`
- **Ngách nội dung:** Secular & classical Buddhist psychology, Zen parables, mindfulness & letting go
- **Lời hứa thương hiệu (Value Proposition):** Learn to drop the second arrow of mental suffering through timeless Zen parables and mindfulness.
- **Khán giả mục tiêu:** Overthinkers, seekers of calm, and anyone navigating stress, grief, or emotional turbulence
- **Nhân vật dẫn chuyện (Persona):** Gentle Zen companion sharing timeless parables with stillness and warmth
- **Giọng văn (Tone):** Tranquil, poetic, calming, compassionate, grounded in early Buddhist psychology | **Giọng TTS:** `OmniVoice_EnSecondArrow` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Mindful Shorts** (YouTube Shorts): 60-second breathing cues and parables.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Plum Village** (YouTube): Teachings of Thich Nhat Hanh on deep listening, anger transformation, and presence.
- **Doug's Dharma** (YouTube): Early Buddhist philosophical scholarship grounded in secular life.
- **Einzelgänger — Buddhism & Zen** (YouTube): Stoic and Zen allegories for modern mental peace.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open with an everyday moment of overthinking or emotional tension.
- Introduce a classic Buddhist or Zen parable naturally (e.g. empty boat, second arrow).
- Distinguish clean physical pain from the optional mental suffering created by our stories.
- End with a peaceful breathing cue and a compassionate takeaway for the evening.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `The parable of the second arrow: why pain is inevitable, but suffering is optional.`
- `The empty boat story: how to stop taking everything personally.`
- `Thich Nhat Hanh on anger: how to hold difficult emotions without exploding.`
- `Impermanence explained: why accepting change dissolves anxiety.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Can you feel yourself dropping the second arrow tonight? Share below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Find deep peace with our full mindful series on The Second Arrow.
### Điều cấm kỵ (Avoid)
- Dogmatic religious preaching
- Promoting superstitious rituals
- Toxic positivity or invalidating real grief

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_zen_sumie` — Sumi-e Zen brush-ink wash: handmade Xuan paper, bamboo sage wash, mindful monk and tranquil water ripples
- **Bảng màu khóa cứng:** `#F5EFE0`, `#1C1C1C`, `#5F7A61`, `#D98A76`, `#8C7A6B`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Serene brush-painted mindfulness monk in flowing sage-linen robes beside calm water ripples, lotus blossoms and bamboo
- **Trang phục (`DEFAULT_OUTFIT`):** Loose-fitting bamboo-sage (#5F7A61) linen meditation robe with gentle brush-edge contours
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Serene monk deflecting the second arrow with calm mind + 2-4 uppercase words.
- **Prompt Style gốc:**
  > Minimalist 2D Zen Sumi-e brush-ink wash illustration on warm Xuan rice paper canvas (#F5EFE0 handmade rice paper, #1C1C1C calligraphy brush ink, #5F7A61 bamboo sage wash, #D98A76 lotus coral) with tranquil negative space, spontaneous calligraphy strokes, lotus blossoms, and quiet water ripples; orthographic 2D, at least 65% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion gentle breathing circle pulses and calm water ripple effects.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *The Parable of the Second Arrow: Why Pain Is Inevitable, But Suffering Is Optional*
- **Thời lượng:** 13 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "When pain strikes your life, the first arrow is unavoidable, but the second arrow is the story you tell."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *mindful stillness* (45s)
- **Spin-off #2 (0 new images):** *The empty boat story: how to stop taking everything personally.* (40s)
- **Spin-off #3 (0 new images):** *Thich Nhat Hanh on anger: holding difficult emotions without exploding.* (45s)
- **Fast-Short #4 (5 Flow images):** *Impermanence explained: why accepting change dissolves anxiety.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- The Parable of the Second Arrow: Why Pain Is Inevitable, But Suffering Is Optional
- The Empty Boat Story: How to Stop Taking Everything Personally
- Thich Nhat Hanh on Anger: How to Hold Difficult Emotions Without Exploding
- Impermanence Explained: Why Accepting Change Dissolves Anxiety
- Why Overthinking Past Mistakes Feeds the Illusion of Control

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#mindfulness #zen #buddhism #peace #meditation #mentalhealth`
- **Nguồn doanh thu:** YouTube AdSense (long), Mindful meditation journal & chime, Mindfulness & calm sleep app sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-second-arrow
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_second_arrow
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
