# KẾ HOẠCH CHI TIẾT KÊNH: WAIT, HOW? (`en_wait_how`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_wait_how` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-wait-how` (`origin/channel/en-wait-how`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-wait-how`
- **Ngách nội dung:** Everyday physics paradoxes, debunked school myths & surprising natural phenomena
- **Lời hứa thương hiệu (Value Proposition):** Answer everyday physical curiosities with delightful clarity so you see the world anew.
- **Khán giả mục tiêu:** Curious adults, students, and thinkers who love asking why everyday things work the way they do
- **Nhân vật dẫn chuyện (Persona):** Playful Feynman-style physics teacher who explains bizarre phenomena effortlessly
- **Giọng văn (Tone):** Playful, mind-expanding, intuitive, lucid, wonder-filled | **Giọng TTS:** `OmniVoice_EnWaitHow` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **MinutePhysics Shorts** (TikTok/YouTube Shorts): Punchy 45-second physics paradox and thought-experiment animations.
### Kênh mẫu YouTube Long (`long_16x9`)
- **MinutePhysics** (YouTube): Stick-figure animations explaining deep physical laws simply.
- **AsapSCIENCE** (YouTube): Fun, dynamic science answers to everyday curiosities.
- **What If? by Randall Munroe (xkcd)** (Book/Scripture): Serious scientific answers to absurd hypothetical questions.
- **Steve Mould** (YouTube): Hands-on physical demonstrations of bizarre fluid and mechanical paradoxes.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with an everyday observation that sounds intuitive but is completely misunderstood.
- Show why the popular schoolbook explanation is subtly incomplete.
- Use clear mechanical stickman doodles to illustrate the true physical force.
- End with an 'aha' moment that changes how viewers see that phenomenon forever.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `8 everyday science myths your school teachers got completely wrong.`
- `Why mosquitoes only bite one specific person in a crowded room.`
- `How airplanes actually stay up: why both popular explanations are incomplete.`
- `Why ice is slippery even below freezing temperatures.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Did your teacher teach you this myth too? Let us know below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Discover the wonder behind everyday physics on Wait How on YouTube.
### Điều cấm kỵ (Avoid)
- Overly formal university tensor equations
- Clickbait without legitimate physical answers
- Conspiracy pseudoscience

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_sticker_pop` — Electric sticker-pop science mascot: bouncy star-spark creature Quark with question-mark antenna
- **Bảng màu khóa cứng:** `#FFF6D6`, `#FFD23F`, `#FF6B6B`, `#2EC4B6`, `#7B2CBF`, `#1D3557`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Recurring mascot Quark — a bouncy round electric-lemon (#FFD23F) star-spark creature with huge curious oval eyes, tiny floating hands and a hovering question-mark antenna
- **Trang phục (`DEFAULT_OUTFIT`):** Natural golden spark glow, tiny teal bow tie and floating question-mark antenna, no human clothes
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Mascot Quark with giant shocked eyes looking at everyday mystery + 2-4 uppercase words.
- **Prompt Style gốc:**
  > Energetic 2D sticker-pop science cartoon on warm cream canvas (#FFF6D6 warm cream, #FFD23F electric lemon, #FF6B6B coral red, #2EC4B6 bright teal, #7B2CBF proton violet) with bold smooth outlines, chunky white sticker borders, and eye-opening everyday physics curiosities; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion trajectory particle bursts and optical ray path animations.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *8 Everyday Science Myths Your School Teachers Got Completely Wrong*
- **Thời lượng:** 12 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "Almost everything you were taught about how mirrors reflect or why ice is slippery is incomplete."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *science myth debunk* (45s)
- **Spin-off #2 (0 new images):** *Why mosquitoes only bite one specific person in a crowded room.* (40s)
- **Spin-off #3 (0 new images):** *How airplanes actually stay up: why popular explanations are flawed.* (45s)
- **Fast-Short #4 (5 Flow images):** *Why mirrors flip left and right, but never top and bottom.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- 8 Everyday Science Myths Your School Teachers Got Completely Wrong
- Why Mosquitoes Only Bite One Specific Person in a Crowded Room
- How Airplanes Actually Stay Up (Why Both Popular Explanations Are Incomplete)
- Why Ice Is Slippery Even Below Freezing Temperature
- Why Mirrors Flip Left and Right—But Never Top and Bottom

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#physics #science #waithow #curiosity #education #stem`
- **Nguồn doanh thu:** YouTube AdSense (long), Illustrated science paradox poster prints, Science educational app sponsor
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-wait-how
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_wait_how
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
