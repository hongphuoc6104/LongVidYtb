# KẾ HOẠCH CHI TIẾT KÊNH: INSIDE THE VESSEL (`en_inside_vessel`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_inside_vessel` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-inside-vessel` (`origin/channel/en-inside-vessel`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-inside-vessel`
- **Ngách nội dung:** Human physiology, sleep neuroscience, immune battles & signals from your organs
- **Lời hứa thương hiệu (Value Proposition):** Take a fascinating journey inside your own biology to understand what your organs are telling you.
- **Khán giả mục tiêu:** Health-conscious individuals, curious learners, and anyone seeking to understand their body
- **Nhân vật dẫn chuyện (Persona):** Friendly anatomical explorer who turns human physiology into an epic adventure
- **Giọng văn (Tone):** Curious, awe-inspiring, scientifically grounded, empathetic | **Giọng TTS:** `OmniVoice_EnInsideVessel` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Kurzgesagt Shorts** (YouTube Shorts): 60-second cellular and biological animations.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Institute of Human Anatomy** (YouTube): Fascinating organ-level physiology explained with immense clarity.
- **Kurzgesagt – Immune & Body Series** (YouTube): Epic microscopic battles between white blood cells, viruses, and bacteria.
- **Why We Sleep by Matthew Walker & The Body by Bill Bryson** (Book/Scripture): Comprehensive anatomical storytelling and sleep architecture research.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with a strange physical sensation everyone feels but few understand.
- Zoom inside the cellular or organ level with clear doodle personifications.
- Explain the evolutionary survival mechanism behind the body's reaction.
- End with one gentle, practical habit to support your physiological system.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `What happens inside your organs during 24 hours without sleep hour by hour.`
- `Why high stress makes your brain crave sugar uncontrollably.`
- `How your gut microbiome secretly sends mood signals to your brain.`
- `What caffeine actually does to adenosine receptors in your brain.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Has your body sent you this signal lately? Share in the comments.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Journey deeper into your physiology with Inside the Vessel on YouTube.
### Điều cấm kỵ (Avoid)
- Prescribing medical diagnoses or treatments
- Promoting unproven miracle supplements
- Sensational health fearmongering

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_organ_buddies` — Vesalius & Gray's Anatomy Copperplate Medical Atlas: dip-pen anatomical cross-sections & mineral watercolor on vellum
- **Bảng màu khóa cứng:** `#FAF7F0`, `#1E1B18`, `#C85A5A`, `#D99B66`, `#4A7C9B`, `#5E8C6A`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Anatomical cross-section human silhouette drawn in fine Da Vinci and Gray's Anatomy copperplate dip-pen cross-hatching on vellum, revealing illuminated internal heart chambers, vagus nerve branches, and cellular structures
- **Trang phục (`DEFAULT_OUTFIT`):** Translucent classical anatomical muscle-and-vessel cross-section linework with brass surgical calipers and ink annotations, no modern clothing
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Copperplate anatomical cross-section of brain and heart under 24-hour stress + 2-4 uppercase engraved words on vellum.
- **Prompt Style gốc:**
  > Authentic 2D Vesalius and Gray's Anatomy medical copperplate ink etching and mineral watercolor cross-section atlas on warm archival vellum (#FAF7F0 fibrous vellum paper, #1E1B18 fine surgical dip-pen cross-hatching, #C85A5A arterial carmine wash, #D99B66 hepatic ochre, #4A7C9B venous slate-blue, #5E8C6A lymphatic sage); detailed anatomical organ cutaways, neural firing pathways, cellular capillaries, and handwritten Latin/English physiological callouts; orthographic 2D, tactile museum medical plate texture, at least 60% negative space, zero 3D CGI, zero kawaii cartoon faces, zero plastic AI glow, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion animated pulse beat lines and cellular magnification transitions.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *What Happens Inside Your Organs During 24 Hours Without Sleep (Hour by Hour)*
- **Thời lượng:** 13 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "When you pull an all-nighter, your internal organs trigger an escalating chemical alarm cascade."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *body sleep signals* (45s)
- **Spin-off #2 (0 new images):** *Why high stress makes your brain crave sugar uncontrollably.* (40s)
- **Spin-off #3 (0 new images):** *How your gut microbiome secretly sends mood signals to your brain.* (45s)
- **Fast-Short #4 (5 Flow images):** *What caffeine actually does to adenosine receptors in your brain.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- What Happens Inside Your Organs During 24 Hours Without Sleep (Hour by Hour)
- Why High Stress Makes Your Brain Crave Sugar Uncontrollably
- How Your Gut Microbiome Secretly Sends Mood Signals to Your Brain
- What Caffeine Actually Does to Adenosine Receptors in Your Brain
- Why Sitting for 8 Hours Triggers Low-Grade Alarm Signals Across Your Body

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#biology #physiology #health #neuroscience #sleep #humanbody`
- **Nguồn doanh thu:** YouTube AdSense (long), Sleep & physiology habits tracker, Ergonomic & health brand sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-inside-vessel
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_inside_vessel
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
