# KẾ HOẠCH CHI TIẾT KÊNH: PLAIN SIGHT AI (`en_plain_sight_ai`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_plain_sight_ai` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-plain-sight-ai` (`origin/channel/en-plain-sight-ai`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-plain-sight-ai`
- **Ngách nội dung:** Practical no-code AI workflows, prompt engineering & office automation for regular people
- **Lời hứa thương hiệu (Value Proposition):** Demystify AI tools and provide repeatable 3-step prompt workflows that save hours of work.
- **Khán giả mục tiêu:** Office workers, students, creators, and freelancers who want practical AI utility without coding
- **Nhân vật dẫn chuyện (Persona):** Down-to-earth tech guide who cuts through hype to deliver genuinely useful workflows
- **Giọng văn (Tone):** Direct, practical, encouraging, step-by-step, no-BS | **Giọng TTS:** `OmniVoice_EnPlainSightAI` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Jeff Su Shorts** (TikTok/YouTube Shorts): 60-second productivity and prompt tips.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Jeff Su** (YouTube): Practical productivity hacks, prompt structures, and office automation.
- **Matt Wolfe** (YouTube): Curated evaluations of genuinely useful AI software and workflows.
- **Anthropic & OpenAI Official Prompt Engineering Guides** (Book/Scripture): Systematic chain-of-thought and few-shot structuring benchmarks.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with a tedious office task that usually takes two hours.
- Demonstrate the exact prompt formula and structure step by step.
- Highlight the verification step to catch AI hallucinations cleanly.
- End with a copy-pasteable prompt template viewers can use immediately.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Why buying expensive AI tools wastes your time: 3 free workflows that work.`
- `Stop asking AI to write an email: use this 3-part prompt structure instead.`
- `How to audit any contract for hidden red flags in 60 seconds with AI.`
- `5 repeatable AI workflows that save 2 hours of office work every day.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Which repetitive task would you like automated next? Comment below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Download our free prompt workflow library on Plain Sight AI YouTube.
### Điều cấm kỵ (Avoid)
- Selling get-rich-quick AI gimmicks
- Promoting unverified AI wrapper tools
- Overly complex code installations

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_ai_doodle` — Plain Sight AI Doodle — Violet hoodie stickman, browser frames and prompt cards
- **Bảng màu khóa cứng:** `#FFFFFF`, `#7C5CFF`, `#3B82C4`, `#34D399`, `#2E4361`, `#000000`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Iconic 2D doodle stickman with oversized white (#FFFFFF) bald circle head, clean black outline, tech-savvy dot eyes, wire arms, and round circle hands
- **Trang phục (`DEFAULT_OUTFIT`):** Flat violet hoodie (#7C5CFF) with subtle cyan accent, no shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Stickman comparing an empty prompt vs a 3-part structure + 2-4 uppercase bold words.
- **Prompt Style gốc:**
  > Hand-drawn 2D practical AI workflow doodle explainer: wobbly black marker outlines (#000000), flat unshaded fills in clean white (#FFFFFF), electric violet (#7C5CFF), tech cobalt (#3B82C4), mint green (#34D399) and dark slate (#2E4361) on a solid white canvas (#FFFFFF); stickman in violet hoodie pointing at clean browser cards, clipboard checklists, and prompt tags; orthographic 2D, minimal, at least 60% negative space, zero 3D.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `screen_capture_hybrid` (Tỷ lệ đồ họa động Remotion/Hyperframes: **50%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **6–9 phút** cho 1 TikTok Short độc lập; **24–34 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion interactive prompt typing previews and verification checklists.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Why Buying Expensive AI Tools Wastes Time: 3 Practical Free Workflows That Work*
- **Thời lượng:** 11 minutes (22 scenes)
- **Câu mở đầu (Cold Open):** "Stop paying for fancy AI wrapper apps when three basic prompt structures do the job faster."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *prompt structure test* (45s)
- **Spin-off #2 (0 new images):** *Stop asking AI to write an email: use this 3-part prompt structure instead.* (40s)
- **Spin-off #3 (0 new images):** *How to audit any contract for hidden red flags in 60 seconds with AI.* (45s)
- **Fast-Short #4 (5 Flow images):** *Why AI hallucinates and the simple verification step most people skip.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Why Buying Expensive AI Tools Wastes Your Time (And 3 Free Workflows That Work)
- Stop Asking AI to Write an Email—Use This 3-Part Prompt Structure Instead
- How to Audit Any Contract for Hidden Red Flags in 60 Seconds with AI
- 5 Repeatable AI Workflows That Save 2 Hours of Office Work Every Day
- Why AI Hallucinates—And the Simple Verification Step Most People Skip

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#ai #artificialintelligence #productivity #promptengineering #chatgpt #automation`
- **Nguồn doanh thu:** YouTube AdSense (long), Curated prompt workflow repository, Productivity software sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-plain-sight-ai
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_plain_sight_ai
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
