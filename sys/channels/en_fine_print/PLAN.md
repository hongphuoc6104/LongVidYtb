# KẾ HOẠCH CHI TIẾT KÊNH: EVERYDAY FINE PRINT (`en_fine_print`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_fine_print` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-fine-print` (`origin/channel/en-fine-print`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-fine-print`
- **Ngách nội dung:** Consumer law literacy, rental & work contracts, hidden fees & subscription dark patterns
- **Lời hứa thương hiệu (Value Proposition):** Read between the lines of contracts and terms of service so you never sign away your rights.
- **Khán giả mục tiêu:** Renters, freelance workers, everyday consumers, and subscription users
- **Nhân vật dẫn chuyện (Persona):** Protective legal literacy ally who translates dense legal legalese into everyday English
- **Giọng văn (Tone):** Vigilant, clear, protective, informative, grounded in consumer protection law | **Giọng TTS:** `OmniVoice_EnFinePrint` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Law By Mike** (YouTube Shorts): Punchy 30-second consumer rights defense scenarios.
### Kênh mẫu YouTube Long (`long_16x9`)
- **LegalEagle** (YouTube): Entertaining yet rigorous legal analysis of real-world scenarios.
- **Lehto's Law** (YouTube): Consumer rights, warranties, and practical contract jurisprudence.
- **FTC Dark Patterns Reports & Consumer Contract Case Studies** (Book/Scripture): Documented predatory billing structures and deceptive UI cases.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with an everyday contract clause that costs ordinary consumers thousands.
- Translate the legal jargon into simple, plain English.
- Explain the exact legal distinction (e.g. deposit vs non-refundable fee).
- Give one specific clause to look for or ask to amend before signing.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `The hidden clauses in everyday contracts that cost you thousands every year.`
- `Why security deposit and non-refundable fee mean completely different things.`
- `Subscription dark patterns: how apps make canceling intentionally confusing.`
- `What actually happens legally when someone sends money to the wrong account?`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Have you ever been trapped by fine print like this? Share below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Protect your consumer rights with the full guide on Everyday Fine Print.
### Điều cấm kỵ (Avoid)
- Giving individualized legal counsel for pending lawsuits
- Advising illegal evasion of contracts
- Dense academic legal theory

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_risograph_law` — Vintage legal risograph print: 3-color mid-century New Yorker editorial, red seal ink on newsprint
- **Bảng màu khóa cứng:** `#F4EFE6`, `#1D3557`, `#E63946`, `#457B9D`, `#D8E2DC`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Sharp-witted human consumer advocate drawn in expressive fountain-pen ink with neat hair, spectacles, navy blazer and brass magnifying glass inspecting red-stamped contract clauses
- **Trang phục (`DEFAULT_OUTFIT`):** Unshaded navy blazer with steel-blue collar, spectacles, and brass magnifying glass in pocket
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Consumer advocate holding magnifying glass over giant hidden fee clause + 2-4 uppercase words.
- **Prompt Style gốc:**
  > Crisp 3-color mid-century New Yorker editorial risograph print on newsprint ivory canvas (#F4EFE6 newsprint ivory, #1D3557 navy ink, #E63946 red-seal ink, #457B9D steel blue); stippled halftone textures, magnifying-glass investigations and consumer protection clauses; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion animated red highlight pen and magnifying glass zoom reveals.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *The Hidden Clauses in Everyday Contracts That Cost You Thousands Every Year*
- **Thời lượng:** 12 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "Before you sign any lease or employment contract, look for these three predatory clauses."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *read the fine print* (45s)
- **Spin-off #2 (0 new images):** *Security deposit vs non-refundable fee: why the words matter legally.* (40s)
- **Spin-off #3 (0 new images):** *Subscription dark patterns: how apps make canceling intentionally hard.* (45s)
- **Fast-Short #4 (5 Flow images):** *5 lease clauses you should always check before signing an apartment lease.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- The Hidden Clauses in Everyday Contracts That Cost You Thousands Every Year
- Why Security Deposit and Non-Refundable Fee Mean Completely Different Things
- Subscription Dark Patterns: How Apps Make Canceling Intentionally Confusing
- What Actually Happens Legally When Someone Sends Money to the Wrong Account?
- 5 Lease Clauses You Should Always Check Before Signing an Apartment Contract

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#law #consumerrights #contracts #fineprint #legal #scams`
- **Nguồn doanh thu:** YouTube AdSense (long), Contract review checklist toolkit, Consumer advocacy legal tech partner
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-fine-print
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_fine_print
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
