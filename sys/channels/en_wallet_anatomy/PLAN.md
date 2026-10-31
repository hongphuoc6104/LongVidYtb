# KẾ HOẠCH CHI TIẾT KÊNH: WALLET ANATOMY (`en_wallet_anatomy`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_wallet_anatomy` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-wallet-anatomy` (`origin/channel/en-wallet-anatomy`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-wallet-anatomy`
- **Ngách nội dung:** Behavioral personal finance, spending traps, Buy-Now-Pay-Later & everyday economics
- **Lời hứa thương hiệu (Value Proposition):** Dissect everyday spending traps and hidden unit economics so you keep more of what you earn.
- **Khán giả mục tiêu:** Young professionals and students navigating consumer traps, credit, and personal wealth
- **Nhân vật dẫn chuyện (Persona):** Savvy financial older sibling who breaks down money psychology without boring spreadsheets
- **Giọng văn (Tone):** Engaging, practical, eye-opening, direct, grounded in behavioral economics | **Giọng TTS:** `OmniVoice_EnWalletAnatomy` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Humphrey Yang** (YouTube): Snackable visual financial literacy and hidden fee warnings.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Two Cents (PBS)** (YouTube): Approachable, illustrated personal finance and money psychology.
- **The Plain Bagel** (YouTube): Pragmatic, calm breakdown of financial schemes and unit economics.
- **The Psychology of Money by Morgan Housel** (Book/Scripture): Behavioral finance, compounding, and wealth preservation mindsets.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with an everyday purchase or financial habit that drains money silently.
- Break down the actual unit economics or cognitive bias behind the trap.
- Never shame modest spending; focus on structural leaks and compounding costs.
- End with one painless behavioral adjustment that protects your savings.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Why earning more money rarely makes you rich: the Diderot effect explained.`
- `How Buy Now Pay Later quietly rewires your brain's pain receptors.`
- `Why busy coffee shops still go bankrupt: the hidden unit economics.`
- `Lifestyle creep: how quiet upgrades steal your financial freedom.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Did this spending leak catch you this month? Tell us in the comments.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Build lasting financial clarity with our full breakdown on Wallet Anatomy.
### Điều cấm kỵ (Avoid)
- Specific stock picking or crypto speculation
- Get rich quick promises
- Shaming small everyday pleasures

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_ledger_grid` — Financial ledger notebook sketch: fountain-pen ink on graph paper, green dollars, deficit red ink
- **Bảng màu khóa cứng:** `#FAF6E9`, `#24364F`, `#2F9E5B`, `#F2C14E`, `#D64545`, `#E3DCC8`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Witty mid-century editorial bookkeeper character with neat side-parted hair, round tortoiseshell glasses, green visor and vest and fountain pen
- **Trang phục (`DEFAULT_OUTFIT`):** Forest green accountant vest over rolled-up sleeve ivory shirt with neat navy tie and tortoiseshell glasses
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Bookkeeper circling red deficit trap on giant ledger + 2-4 uppercase words.
- **Prompt Style gốc:**
  > Hand-inked 2D financial ledger notebook illustration on warm square-grid graph paper (#FAF6E9 ivory paper with faint #E3DCC8 grid, #2F9E5B dollar emerald, #F2C14E bullion gold, #D64545 deficit red, #24364F fountain-pen navy); clean balance-sheet columns, cashflow conduits, and financial anatomy charts; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion compounding coin bar animations and unit cost breakdown cards.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Why Earning More Money Rarely Makes You Rich: The Psychology of Money Traps*
- **Thời lượng:** 12 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "Why do people who double their income often feel just as financially stressed as before?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *lifestyle creep trap* (45s)
- **Spin-off #2 (0 new images):** *How Buy Now Pay Later quietly rewires your brain's pain receptor.* (40s)
- **Spin-off #3 (0 new images):** *Why busy coffee shops still go bankrupt: hidden unit economics.* (45s)
- **Fast-Short #4 (5 Flow images):** *The sunk cost trap that keeps you pouring money into bad choices.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Why Earning More Money Rarely Makes You Rich (The Diderot Effect Explained)
- How Buy Now, Pay Later Quietly Rewires Your Brain's Pain Receptor
- Why Busy Coffee Shops Still Go Bankrupt: The Hidden Unit Economics
- Lifestyle Creep: How Quiet Upgrades Steal Your Freedom
- The Sunk Cost Trap That Keeps You Pouring Money into Bad Choices

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#money #personalfinance #economics #financialfreedom #budgeting #wealth`
- **Nguồn doanh thu:** YouTube AdSense (long), Personal finance budgeting spreadsheets, High-yield savings platform sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-wallet-anatomy
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_wallet_anatomy
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
