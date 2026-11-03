# KẾ HOẠCH CHI TIẾT KÊNH: MACRO GEARS (`en_macro_gears`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_macro_gears` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-macro-gears` (`origin/channel/en-macro-gears`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-macro-gears`
- **Ngách nội dung:** Macroeconomics, inflation, central bank interest rates & global supply chains simplified
- **Lời hứa thương hiệu (Value Proposition):** Explain how global economic forces, interest rates, and inflation impact your wallet.
- **Khán giả mục tiêu:** Informed citizens, business builders, and curious viewers wanting macroeconomic clarity
- **Nhân vật dẫn chuyện (Persona):** Clear-headed economic explainer showing how the global economic engine works
- **Giọng văn (Tone):** Objective, clarifying, fascinating, grounded in empirical economic history | **Giọng TTS:** `OmniVoice_EnMacroGears` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Visual Capitalist Shorts** (YouTube Shorts): Infographic snapshots of macro trade routes and asset flows.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Economics Explained** (YouTube): Global macroeconomic systems, national economies, and currency dynamics.
- **How Money Works** (YouTube): Clear whiteboard-style explanations of complex economic phenomena.
- **Principles for Dealing with the Changing World Order by Ray Dalio** (YouTube/Book): Debt cycles, central bank policies, and monetary history.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with a global economic headline connected straight to everyday living costs.
- Trace the transmission mechanism step by step with physical mechanical metaphors.
- Remain strictly non-partisan; present trade-offs and unintended consequences.
- Summarize the practical takeaway for personal assets and economic resilience.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `How the economic machine actually works in 12 minutes without the jargon.`
- `Who actually gets poorer first when a central bank prints new money?`
- `Why economic crises make gold prices move so wildly.`
- `The Cantillon Effect: why inflation never hits everyone equally.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** How has inflation touched your area lately? Share your observations below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Explore our complete global economy series on Macro Gears.
### Điều cấm kỵ (Avoid)
- Political partisan blame games
- Short-term market forecasting
- Abstract dogma without historical data

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_swiss_macro` — Mid-Century Banknote Intaglio Engraving & Letterpress Infographic: salmon financial newsprint, cross-hatched ink
- **Bảng màu khóa cứng:** `#F3EFE6`, `#0F2C59`, `#D9381E`, `#2A9D8F`, `#E9C46A`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Mid-century financial-press correspondent drawn in fine steel-engraved cross-hatching wearing structured navy suit and vermilion tie beside engraved cargo vessels and monetary levers
- **Trang phục (`DEFAULT_OUTFIT`):** Hand-engraved central-bank navy (#0F2C59) two-button suit with cross-hatched lapel, white shirt, and letterpress vermilion tie
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Engraved correspondent pulling central-bank interest lever + 2-4 uppercase letterpress words on newsprint.
- **Prompt Style gốc:**
  > Tactile 2D mid-century banknote intaglio engraving and Swiss letterpress editorial print on warm salmon-ivory financial newsprint (#F3EFE6 fibrous financial-press paper, #0F2C59 intaglio central-bank navy, #D9381E letterpress vermilion, #2A9D8F maritime trade teal, #E9C46A bullion ochre) with fine steel-engraved cross-hatching, stamped freight manifests, container vessel woodcuts and mechanical monetary policy levers; orthographic 2D, authentic letterpress ink grain, at least 60% negative space, zero 3D CGI, zero flat corporate vector, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion interactive currency flow arrows and interest rate dial animations.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *How the Economic Machine Actually Works in 12 Minutes (Without the Jargon)*
- **Thời lượng:** 13 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "When a central bank changes interest rates, how does that decision ripple into your grocery bill?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *economic engine flow* (45s)
- **Spin-off #2 (0 new images):** *Who actually gets poorer first when a central bank prints new money?* (45s)
- **Spin-off #3 (0 new images):** *The Cantillon Effect: why inflation never hits everyone equally.* (40s)
- **Fast-Short #4 (5 Flow images):** *How one tiny semiconductor fab holds the global economy together.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- How the Economic Machine Actually Works in 12 Minutes (Without the Jargon)
- Who Actually Gets Poorer First When a Central Bank Prints New Money?
- Why Economic Crises Make Gold Prices Move So Wildly
- The Cantillon Effect: Why Inflation Never Hits Everyone Equally
- How One Tiny Semiconductor Fab Holds the Global Economy Together

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#macroeconomics #economy #inflation #interestrates #money #geopolitics`
- **Nguồn doanh thu:** YouTube AdSense (high RPM), Macro economic research briefing sponsor, Curated economic history books affiliate
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-macro-gears
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_macro_gears
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
