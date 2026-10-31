# KẾ HOẠCH CHI TIẾT KÊNH: CROWD STRINGS (`en_crowd_strings`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_crowd_strings` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-crowd-strings` (`origin/channel/en-crowd-strings`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-crowd-strings`
- **Ngách nội dung:** Social psychology, herd behavior, subtle persuasion & everyday negotiation
- **Lời hứa thương hiệu (Value Proposition):** Expose the invisible social strings pulling your decisions, so you never get manipulated.
- **Khán giả mục tiêu:** Curious minds seeking psychological awareness, consumer defense, and smart negotiation
- **Nhân vật dẫn chuyện (Persona):** Sharp observer of social currents, dissecting herd psychology with calm clarity
- **Giọng văn (Tone):** Analytical, observant, intriguing, grounded in behavioral game theory | **Giọng TTS:** `OmniVoice_EnCrowdStrings` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Daily Negotiation Insights** (TikTok/YouTube Shorts): Punchy 30-second negotiation and psychological defense tips.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Charisma on Command** (YouTube): Deconstructing social dynamics and charisma in everyday conversations.
- **The School of Life** (YouTube): Philosophical and psychological human behavior explanations.
- **Influence by Robert Cialdini & Thinking, Fast and Slow by Daniel Kahneman** (Book/Scripture): Core cognitive biases, social proof, and decision architecture.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with a common social compliance trap within 3 seconds.
- Expose the subtle persuasion cue or herd dynamic clearly.
- Illustrate with everyday retail, workplace, or social scenarios.
- Provide one immediate psychological boundary rule.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `7 psychological traps stores use to empty your wallet without you noticing.`
- `The anchoring trick that makes you overpay every single time.`
- `Why good people do terrible things inside a crowd.`
- `The Benjamin Franklin effect: how a tiny favor builds instant trust.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Have you noticed this crowd trap before? Drop your reaction below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Explore our next deep-dive on social psychology on Crowd Strings.
### Điều cấm kỵ (Avoid)
- Promoting deceitful manipulation tactics
- Paranoid conspiracy rhetoric
- Academic jargon without tangible examples

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_crowd_noir` — Psychological crowd noir: high-contrast 2D graphic novel, aged dossier paper, crimson puppet strings
- **Bảng màu khóa cứng:** `#111111`, `#E8E2D0`, `#5A5F66`, `#C0392B`, `#FFFFFF`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Sharp-suited anonymous noir observer silhouette with glowing white lapel pin amidst shadowed crowd figures and crimson influence threads
- **Trang phục (`DEFAULT_OUTFIT`):** Sharp charcoal-black suit silhouette with crisp white collar and glowing crimson pin, no shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Noir silhouette cutting crimson puppet strings + 2-4 uppercase words on flat dossier background.
- **Prompt Style gốc:**
  > High-contrast 2D psychological noir graphic-novel art on aged dossier paper canvas (#111111 ink black, #E8E2D0 dossier paper, #5A5F66 slate shadow, #C0392B crimson puppet-strings); sharp chiaroscuro ink shadows, dossier pins, connecting string matrices and anonymous crowd silhouettes; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion animated puppet string overlays and crowd vector arrows.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *7 Psychological Traps Stores Use to Empty Your Wallet Without You Noticing*
- **Thời lượng:** 12 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "Have you ever entered a store to buy one item and walked out with five you never planned on?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *consumer compliance trap* (45s)
- **Spin-off #2 (0 new images):** *The anchoring trick that makes you overpay every single time.* (40s)
- **Spin-off #3 (0 new images):** *Why good people do terrible things inside an anonymous crowd.* (45s)
- **Fast-Short #4 (5 Flow images):** *The Benjamin Franklin effect: how a tiny favor builds instant trust.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- 7 Psychological Traps Stores Use to Empty Your Wallet Without You Noticing
- The Anchoring Trick That Makes You Overpay Every Single Time
- Why Good People Do Terrible Things Inside a Crowd
- The Benjamin Franklin Effect: How Asking for a Tiny Favor Builds Instant Trust
- 3 Negotiation Moves FBI Hostage Negotiators Use in Daily Life

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#psychology #persuasion #socialpsychology #negotiation #influence #mindset`
- **Nguồn doanh thu:** YouTube AdSense (long), Negotiation masterclass sponsorship, Recommended psychology books affiliate
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-crowd-strings
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_crowd_strings
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
