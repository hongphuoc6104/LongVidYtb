# KẾ HOẠCH CHI TIẾT KÊNH: CAREER LEVERAGE (`en_career_leverage`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_career_leverage` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-career-leverage` (`origin/channel/en-career-leverage`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-career-leverage`
- **Ngách nội dung:** Workplace strategy, salary negotiation, unspoken corporate rules & AI-era career resilience
- **Lời hứa thương hiệu (Value Proposition):** Master unspoken workplace dynamics and build career leverage so your effort actually pays off.
- **Khán giả mục tiêu:** Mid-career corporate employees, professionals, and remote workers aiming for advancement
- **Nhân vật dẫn chuyện (Persona):** Strategic corporate mentor who explains organizational power dynamics candidly
- **Giọng văn (Tone):** Strategic, candid, empowering, realistic, pragmatic | **Giọng TTS:** `OmniVoice_EnCareerLeverage` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **LoewHaley** (YouTube): Witty, hyper-accurate satire and unwritten rules of corporate office life.
- **Career Shapers** (YouTube Shorts): Punchy 30-second salary negotiation tactics.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Harvard Business Review Explainer** (YouTube): Evidence-based management, leadership, and workplace dynamics.
- **The Almanack of Naval Ravikant & So Good They Can't Ignore You by Cal Newport** (Book/Scripture): Specific knowledge, career capital, and leverage building.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with a painful workplace paradox (e.g. why the hardest worker rarely gets promoted).
- Reveal the underlying organizational power dynamic or evaluation bias.
- Provide an ethical, actionable tactic to increase visibility and leverage.
- End with a clear conversational phrasing script for tough discussions.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `The Peter Principle: why the hardest worker in the office rarely gets promoted.`
- `3 quiet signs your company is preparing for layoffs and how to prepare.`
- `Why visibility beats raw effort inside large organizations every time.`
- `How to negotiate your salary using anchors without sounding greedy.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Have you seen this rule in action at work? Tell us below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Gain complete career leverage with our full guide on Career Leverage.
### Điều cấm kỵ (Avoid)
- Toxic workplace sabotage tactics
- Whiny anti-work venting
- Generic resume formatting clichés

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_career_doodle` — New Yorker Editorial Fountain-Pen & Ink Wash Sketchbook: cotton rag paper, royal-blue ink wash, stickman
- **Bảng màu khóa cứng:** `#F8F0DC`, `#3B82C4`, `#F2B88B`, `#2E4361`, `#FFFFFF`, `#000000`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Iconic 2D editorial sketchbook stickman with oversized hand-drawn white (#FFFFFF) bald circle head, dip-pen black outline, professional lanyard, wire arms, and round circle hands
- **Trang phục (`DEFAULT_OUTFIT`):** Matte watercolor-wash royal-blue shirt (#3B82C4) with hand-inked company lanyard, zero digital gradients
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Dip-pen stickman lifting a heavy corporate staircase using a wooden fulcrum + 2-4 uppercase hand-lettered words.
- **Prompt Style gốc:**
  > Hand-inked 2D New Yorker-inspired editorial career sketchbook on textured warm cotton rag paper (#F8F0DC visible paper grain): dip-pen black ink cross-hatching (#000000) with graphite construction lines, matte watercolor washes in royal cobalt (#3B82C4), warm ochre (#F2B88B), deep slate (#2E4361) and raw white (#FFFFFF); expressive bald circle stickman in cobalt shirt with office lanyard beside hand-drawn wooden fulcrums, architectural staircases, and boardroom tables; orthographic 2D, tactile pen-and-ink grain, at least 60% negative space, zero 3D CGI, zero plastic AI sheen.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion salary anchor gauge animations and corporate ladder progress indicators.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *The Peter Principle: Why the Hardest Worker in the Office Rarely Gets Promoted*
- **Thời lượng:** 12 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "Working twelve hours a day is often the fastest way to get trapped in the exact same role."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *career leverage balance* (45s)
- **Spin-off #2 (0 new images):** *3 quiet signs your company is preparing for layoffs.* (40s)
- **Spin-off #3 (0 new images):** *Why visibility beats raw effort inside large organizations every time.* (45s)
- **Fast-Short #4 (5 Flow images):** *How to negotiate your salary using anchors without sounding greedy.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- The Peter Principle: Why the Hardest Worker in the Office Rarely Gets Promoted
- 3 Quiet Signs Your Company Is Preparing for Layoffs (And How to Prepare)
- Why Visibility Beats Raw Effort Inside Large Organizations
- How to Negotiate Your Salary Using Anchors Without Sounding Greedy
- Specific Knowledge vs Replaceable Busywork in the Age of AI

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#career #workplace #salarynegotiation #leadership #corporate #jobs`
- **Nguồn doanh thu:** YouTube AdSense (high RPM), Executive career strategy toolkit, Professional coaching platform sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-career-leverage
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_career_leverage
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
