# KẾ HOẠCH CHI TIẾT KÊNH: KITCHEN MOLECULES (`en_kitchen_molecules`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_kitchen_molecules` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-kitchen-molecules` (`origin/channel/en-kitchen-molecules`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-kitchen-molecules`
- **Ngách nội dung:** Food chemistry, kitchen safety myths, cooking reactions & ultra-processed food science
- **Lời hứa thương hiệu (Value Proposition):** Unlock the fascinating science of cooking and debunk dangerous kitchen myths with microbiology.
- **Khán giả mục tiêu:** Home cooks, foodies, and curious minds curious about culinary chemistry and safety
- **Nhân vật dẫn chuyện (Persona):** Passionate food scientist who brings molecular kitchen reactions to life with stick figures
- **Giọng văn (Tone):** Lively, appetizing, scientific, accessible, myth-busting | **Giọng TTS:** `OmniVoice_EnKitchenMolecules` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **MinuteFood Shorts** (TikTok/YouTube Shorts): Bite-sized 45-second cooking science myth-busters.
### Kênh mẫu YouTube Long (`long_16x9`)
- **MinuteFood** (YouTube): Snackable physics and chemistry behind everyday kitchen processes.
- **Adam Ragusea** (YouTube): Practical food science, kitchen myths, and culinary culinary realities.
- **On Food and Cooking by Harold McGee & Ultra-Processed People** (Book/Scripture): Masterwork of culinary chemistry, industrial food science, and emulsions.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with a common kitchen habit or cooking myth people do every day.
- Explain the chemical or biological mechanism (e.g. Maillard reaction, bacterial curve).
- Use relatable kitchen analogies with pans, thermometers, and molecules.
- End with one simple chef-science technique that improves food quality or safety.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `The chemistry of reused cooking oil: what actually happens at 350 degrees?`
- `Never thaw frozen meat in hot water: here is the bacteria math.`
- `The Maillard reaction: why browning makes almost everything taste better.`
- `Is the 5-second dropped food rule real? What microbiology says.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Did this kitchen rule surprise you? Tell us your cooking habits below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Master the science of delicious food with Kitchen Molecules on YouTube.
### Điều cấm kỵ (Avoid)
- Extreme fad diet preaching
- Sensational food fearmongering
- Rejecting peer-reviewed nutritional science

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_culinary_sticker` — Food science sticker-pop cartoon: die-cut white borders, cheerful culinary mascots Sunny and Sizzle
- **Bảng màu khóa cứng:** `#FFF9EB`, `#FF6B6B`, `#FFD166`, `#06D6A0`, `#118AB2`, `#2B2D42`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Cheerful anthropomorphic culinary mascots — Sunny the golden egg, Sizzle the skillet sprite, and bouncy flavor-molecule buddies with big expressive eyes
- **Trang phục (`DEFAULT_OUTFIT`):** Tiny red chef kerchief on Sunny; cheerful blue steam plume on Sizzle sprite
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Sunny the egg character dodging a smoking pan + 2-4 uppercase words on buttercream canvas.
- **Prompt Style gốc:**
  > Vibrant 2D die-cut sticker-pop food-science cartoon on warm buttercream canvas (#FFF9EB warm buttercream canvas, #FF6B6B sear coral, #FFD166 butter gold, #06D6A0 basil green, #118AB2 steam blue) with thick smooth outlines, chunky white sticker borders, and lively Maillard reaction sprites; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **40%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion thermometer rise animation and molecular bonding visuals.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *The Chemistry of Everyday Cooking: 5 Myths Busted and Science-Backed Techniques*
- **Thời lượng:** 12 minutes (24 scenes)
- **Câu mở đầu (Cold Open):** "Why does browning meat or onions make them taste a hundred times richer than boiling?"
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *kitchen chemistry test* (45s)
- **Spin-off #2 (0 new images):** *The chemistry of reused cooking oil: what happens at 350 degrees?* (40s)
- **Spin-off #3 (0 new images):** *Never thaw frozen meat in hot water: here is the bacteria math.* (45s)
- **Fast-Short #4 (5 Flow images):** *The Maillard reaction: why browning makes almost everything taste better.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- The Chemistry of Reused Cooking Oil: What Actually Happens at 350 Degrees?
- Never Thaw Frozen Meat in Hot Water—Here Is the Bacteria Math
- The Maillard Reaction: Why Browning Makes Almost Everything Taste Better
- Is the 5-Second Dropped Food Rule Real? What Microbiology Says
- Why Honey Never Spoils While Fresh Bread Molds in Days

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#foodscience #cooking #chemistry #food #kitchen #science`
- **Nguồn doanh thu:** YouTube AdSense (long), Kitchen science temperature guide cheat sheets, High-quality kitchenware sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-kitchen-molecules
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_kitchen_molecules
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
