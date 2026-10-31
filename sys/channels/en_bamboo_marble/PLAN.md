# KẾ HOẠCH CHI TIẾT KÊNH: BAMBOO & MARBLE (`en_bamboo_marble`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_bamboo_marble` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-bamboo-marble` (`origin/channel/en-bamboo-marble`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-bamboo-marble`
- **Ngách nội dung:** Stoicism meets Taoism: Marcus Aurelius, Lao Tzu, mindful night fables & inner calm
- **Lời hứa thương hiệu (Value Proposition):** Bridge Western Stoic strength with Eastern Taoist non-forcing for unshakeable inner peace.
- **Khán giả mục tiêu:** Nighttime thinkers, busy professionals, and seekers of stillness before sleep
- **Nhân vật dẫn chuyện (Persona):** Quiet evening philosopher blending ancient wisdom into soothing bedtime reflections
- **Giọng văn (Tone):** Soothing, reflective, philosophical, grounded, poetic | **Giọng TTS:** `OmniVoice_EnBambooMarble` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Daily Stoic Shorts** (TikTok/YouTube Shorts): 60-second Stoic mindset reflections.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Einzelgänger — Stoicism & Taoism** (YouTube): Harmonizing Western Stoic virtue with Eastern Taoist non-striving.
- **Daily Stoic** (YouTube): Practical dichotomy of control, Amor Fati, and evening reflection.
- **Dare to do. Motivation** (YouTube): Evening parable stories for inner stillness and restful sleep.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open with a quiet evening scene inviting the viewer to set aside daily anxiety.
- Blend a Stoic principle of fortitude with a Taoist principle of non-forcing (Wu Wei).
- Use concrete parables like cracked jars, bamboo stalks, or marble columns.
- Conclude with a peaceful goodnight blessing and invitation to rest.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Lao Tzu's philosophy of Wu Wei: why forcing your life only makes it fall apart.`
- `Socrates' three sieves: the 10-second rule before rumors ruin your peace.`
- `The Chinese farmer parable: why bad luck today might save you tomorrow.`
- `How Marcus Aurelius stayed calm surrounded by betrayal and chaos.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Let this thought bring stillness to your night. Rest well.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Unwind completely with our full nighttime philosophical fable on Bamboo & Marble.
### Điều cấm kỵ (Avoid)
- Harsh lecturing tones
- Cynical nihilism
- Complex academic philosophy without practical heart

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_twilight_stoic` — Twilight Stoic-Taoist gouache: deep slate-indigo canvas, warm marble ivory, celadon bamboo, golden crescent moon
- **Bảng màu khóa cứng:** `#1D2D44`, `#F0EBD8`, `#84A98C`, `#E9C46A`, `#748CAB`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Calm philosopher traveler painted in soft flat gouache wearing a draped ivory-and-slate cloak standing peacefully between a classical marble column and swaying celadon bamboo under a golden crescent moon
- **Trang phục (`DEFAULT_OUTFIT`):** Flowing flat ivory-and-slate philosopher cloak with clean soft edges, no modern details
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Philosopher traveler looking at golden moon between bamboo and marble + 2-4 uppercase words.
- **Prompt Style gốc:**
  > Tranquil 2D flat midnight gouache and classical ink bedtime illustration on deep twilight slate-indigo canvas (#1D2D44 deep twilight slate-indigo canvas, #F0EBD8 warm marble ivory, #84A98C bamboo celadon, #E9C46A warm lantern gold, #748CAB misty mountain blue); soft matte gouache silhouettes, tranquil bamboo groves, classical marble colonnades and moonlit water; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion gentle moonlight float and bamboo sway transitions.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Stoic Strength Meets Taoist Calm: Timeless Parables to End Overthinking at Night*
- **Thời lượng:** 14 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "Be like bamboo that bends with the wind, anchored by the unyielding marble of inner virtue."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *evening stillness reflection* (45s)
- **Spin-off #2 (0 new images):** *Lao Tzu's Wu Wei: why forcing your life only makes it fall apart.* (40s)
- **Spin-off #3 (0 new images):** *Socrates' three sieves: the 10-second rule before rumors disturb peace.* (45s)
- **Fast-Short #4 (5 Flow images):** *The Chinese farmer parable: why bad luck today might save you tomorrow.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Lao Tzu's Philosophy of Wu Wei: Why Forcing Your Life Only Makes It Fall Apart
- Socrates' Three Sieves: The 10-Second Rule Before Rumors Ruin Your Peace
- The Chinese Farmer Parable: Why Bad Luck Today Might Save You Tomorrow
- How Marcus Aurelius Stayed Calm Surrounded by Betrayal and Chaos
- The Cracked Water Jar: A Quiet Night Story About Imperfection

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#stoicism #taoism #philosophy #mindset #innerpeace #wisdom`
- **Nguồn doanh thu:** YouTube AdSense (long), Mindful evening journal & herbal tea curation, Meditation & sleep app sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-bamboo-marble
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_bamboo_marble
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
