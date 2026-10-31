# KẾ HOẠCH CHI TIẾT KÊNH: CHOKE POINT MAPS (`en_choke_point`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_choke_point` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-choke-point` (`origin/channel/en-choke-point`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-choke-point`
- **Ngách nội dung:** Geopolitics, maritime choke points, resource geography & pivotal historical turning points
- **Lời hứa thương hiệu (Value Proposition):** Trace the narrow straits, canals, and geography that dictate world trade, power, and conflict.
- **Khán giả mục tiêu:** Geopolitics enthusiasts, history buffs, and global affairs observers
- **Nhân vật dẫn chuyện (Persona):** Strategic cartographer connecting global news directly to physical geography
- **Giọng văn (Tone):** Strategic, panoramic, authoritative, clear, illuminating | **Giọng TTS:** `OmniVoice_EnChokePoint` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **RealLifeLore Shorts** (YouTube Shorts): 60-second geographic trivia and bottleneck snapshots.
### Kênh mẫu YouTube Long (`long_16x9`)
- **RealLifeLore** (YouTube): Global geographic analysis of strategic straits, logistics, and resource constraints.
- **Map Men & Historia Civilis** (YouTube): Witty cartographic breakdowns and strategic military maneuver maps.
- **Prisoners of Geography by Tim Marshall** (Book/Scripture): Foundational geopolitical analysis of mountains, rivers, and choke points.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Hook with a single narrow geographical bottleneck that controls global commodity prices.
- Use flat 2D maps to illustrate why countries have fought over this geography for centuries.
- Connect the historical pattern directly to modern maritime and trade headlines.
- End with a strategic summary of what happens if that bottleneck closes.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Why one narrow strait controls the price of everything you buy.`
- `Why commercial planes almost never fly directly over the Tibetan plateau.`
- `How geography turned Panama and Suez into global bottlenecks.`
- `Why Russia's warm-water port obsession explains centuries of history.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Did you realize this strait carried so much trade? Share below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Explore our full geopolitical map library on Choke Point Maps.
### Điều cấm kỵ (Avoid)
- One-sided political propaganda
- Sensationalized ungrounded war predictions
- Nationalistic jingoism

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_tactical_atlas` — Strategic maritime atlas: Vox-style flat cartography, sand topographic landmasses, choke point straits
- **Bảng màu khóa cứng:** `#0D1B2A`, `#E6CCB2`, `#E63946`, `#FFB703`, `#4EA8DE`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Character-free strategic cartography emblem: precision compass rose, 2D flat tanker silhouettes, maritime choke-point contours, and glowing trade-corridor arrows (zero human characters)
- **Trang phục (`DEFAULT_OUTFIT`):** No human clothing; high-contrast gold and crimson cartographic vector overlays
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Glowing crimson blockade over strategic strait map + 2-4 uppercase words.
- **Prompt Style gốc:**
  > Crisp Vox and Johnny Harris-inspired 2D flat strategic cartography illustration on deep maritime navy ocean canvas (#0D1B2A deep maritime navy ocean, #E6CCB2 topographic sand landmasses, #E63946 blockade crimson, #FFB703 shipping-lane gold, #4EA8DE strait cyan); fine topographic contour lines, container vessel icons, blockade vectors, and maritime choke points; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion animated maritime route lines and choke point zoom reveals.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Why One Narrow Strait Controls the Price of Everything You Buy (Maritime Choke Points)*
- **Thời lượng:** 14 minutes (26 scenes)
- **Câu mở đầu (Cold Open):** "If a single narrow body of water closes tomorrow, global energy and grain markets halt in hours."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *strategic map check* (50s)
- **Spin-off #2 (0 new images):** *Why commercial planes almost never fly over the Tibetan plateau.* (45s)
- **Spin-off #3 (0 new images):** *How geography turned Panama and Suez into global economic bottlenecks.* (45s)
- **Fast-Short #4 (5 Flow images):** *Why Russia's warm-water port obsession explains centuries of history.* (50s)

### Backlog chủ đề hạt giống tiếp theo
- Why One Narrow Strait Controls the Price of Everything You Buy
- Why Commercial Planes Almost Never Fly Directly Over the Tibetan Plateau
- How Geography Turned Panama and Suez into Global Bottlenecks
- Why Russia's Warm-Water Port Obsession Explains Centuries of History
- How River Systems Quietly Decided Which Civilizations Became Superpowers

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#geopolitics #maps #geography #trade #history #worldaffairs`
- **Nguồn doanh thu:** YouTube AdSense (high RPM), Strategic geopolitical map prints, Global affairs newsletter sponsorship
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-choke-point
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_choke_point
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
