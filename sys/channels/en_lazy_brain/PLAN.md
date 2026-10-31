# KẾ HOẠCH CHI TIẾT KÊNH: LAZY BRAIN LAB (`en_lazy_brain`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_lazy_brain` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-lazy-brain` (`origin/channel/en-lazy-brain`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-lazy-brain`
- **Ngách nội dung:** Neuroscience of procrastination, dopamine habits, focus & behavioral psychology
- **Lời hứa thương hiệu (Value Proposition):** Decode why your brain procrastinates, in plain English with relatable stickman doodles.
- **Khán giả mục tiêu:** Busy thinkers, students, and professionals fighting dopamine traps and distraction
- **Nhân vật dẫn chuyện (Persona):** Curious neuroscience buddy who explains brain quirks without academic guilt
- **Giọng văn (Tone):** Conversational, witty, empathetic, grounded in cognitive psychology | **Giọng TTS:** `OmniVoice_EnLazyBrain` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Psych2Go Shorts** (TikTok/YouTube Shorts): High-relatability 3-second psychological hook questions.
### Kênh mẫu YouTube Long (`long_16x9`)
- **The Paint Explainer** (YouTube): Ultra-minimalist doodle explainer pacing and clear visual metaphors.
- **Better Ideas** (YouTube): Relatable self-improvement storytelling and procrastination deconstruction.
- **Atomic Habits & Dopamine Nation** (Book/Scripture): Clear behavioral habit loops and neuroscience frameworks.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with an everyday procrastination habit within 3 seconds.
- Explain the brain circuit using physical metaphors like leaky buckets or alarm bells.
- Zero shame or toxic hustle advice; focus on friction reduction.
- End with one frictionless 2-minute actionable experiment.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Why your brain loves procrastinating on goals that actually matter to you.`
- `You are not lazy. Your prefrontal cortex is simply stuck in a loop.`
- `The 2-minute dopamine rule that breaks doomscrolling immediately.`
- `Why does cleaning your desk feel urgent only when a deadline hits?`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Which brain habit caught you today? Share your number below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Join us next time as we explore more quirks of the human brain.
### Điều cấm kỵ (Avoid)
- Diagnosing clinical mental illness
- Toxic hustle culture advice
- Heavy peer-reviewed jargon without plain analogies

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_lazy_brain_doodle` — Lazy Brain Doodle — Cream canvas, blue-shirt stickman, brain & dopamine metaphors
- **Bảng màu khóa cứng:** `#F8F0DC`, `#3B82C4`, `#F2B88B`, `#93A88C`, `#2E4361`, `#FFFFFF`, `#000000`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Iconic 2D doodle stickman with oversized white (#FFFFFF) bald circle head, bold pitch-black (#000000) marker outline, tiny dot eyes, minimal smile, wire arms and round white circle hands
- **Trang phục (`DEFAULT_OUTFIT`):** Flat cobalt-blue (#3B82C4) t-shirt over slate-gray pants, no shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Stickman with exaggerated emotion staring at clock + 2-4 uppercase bold words on flat cream canvas.
- **Prompt Style gốc:**
  > Hand-drawn 2D neuroscience and focus doodle explainer: wobbly black marker outlines (#000000), flat unshaded fills in warm cream (#F8F0DC), bold cobalt blue (#3B82C4), coral (#F2B88B), sage (#93A88C) and white (#FFFFFF) on a solid cream canvas (#F8F0DC); oversized bald circle stickman in blue shirt with simple analog clock, neuron synapses and phone screens; orthographic 2D, minimal, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion dopamine meter pulse and countdown timer animations.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Why Your Brain Loves Procrastinating on Important Goals (And How to Trick It)*
- **Thời lượng:** 12 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "Why does cleaning your desk feel intensely urgent only when an important deadline hits?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *procrastination loop* (45s)
- **Spin-off #2 (0 new images):** *The 2-minute dopamine reset that stops doomscrolling instantly.* (40s)
- **Spin-off #3 (0 new images):** *Why perfectionism paralyzes your prefrontal cortex.* (45s)
- **Fast-Short #4 (5 Flow images):** *How micro-habits bypass your brain's threat detector.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Why Your Brain Loves Procrastinating on Important Goals (And How to Trick It)
- The 2-Minute Dopamine Reset That Stops Doomscrolling Instantly
- Why Perfectionism Paralyzes Your Prefrontal Cortex
- Revenge Bedtime Procrastination: Why You Stay Awake at 2 AM
- How Micro-Habits Bypass Your Brain's Threat Detector

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#neuroscience #procrastination #dopamine #focus #habits #productivity`
- **Nguồn doanh thu:** YouTube AdSense (long), Digital focus planners, Curated book club affiliate
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-lazy-brain
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_lazy_brain
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
