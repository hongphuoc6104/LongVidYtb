# KẾ HOẠCH CHI TIẾT KÊNH: COLD CASE INK (`en_cold_case_ink`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `en_cold_case_ink` (Đợt triển khai: Wave 4)
- **Nhánh GitHub độc lập:** `channel/en-cold-case-ink` (`origin/channel/en-cold-case-ink`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-en-cold-case-ink`
- **Ngách nội dung:** Historical mysteries, vanished expeditions & scientific forensic investigations
- **Lời hứa thương hiệu (Value Proposition):** Re-examine history's greatest unexplained cases through primary documents and modern forensic science.
- **Khán giả mục tiêu:** Documentary enthusiasts, mystery solvers, and history lovers wanting rigorous investigations
- **Nhân vật dẫn chuyện (Persona):** Impartial historical investigator weighing forensic evidence with documentary restraint
- **Giọng văn (Tone):** Investigative, atmospheric, forensic, objective, suspenseful | **Giọng TTS:** `OmniVoice_EnColdCaseInk` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 35–50s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 8–12 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Documentary Shorts** (YouTube Shorts): Atmospheric 50-second historical enigma spotlights.
### Kênh mẫu YouTube Long (`long_16x9`)
- **Lemmino** (YouTube): Peerless documentary pacing, forensic neutrality, and primary-source rigor.
- **Brew** (YouTube): Compelling storytelling of historical survivals and unexplained events.
- **ETH Zurich Dyatlov Avalanche Study & Smithsonian Historical Archives** (Book/Scripture): Scientific forensic reconstruction and empirical records.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Open with the verified timeline of the event without sensationalizing rumors.
- Establish the geographic isolation and extreme stakes using clean maps.
- Examine competing theories against modern scientific and forensic evidence.
- Draw a measured conclusion while respecting the unresolved human loss.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `The Dyatlov Pass incident: how avalanche physics solved the 1959 mystery.`
- `Why did the Mary Celeste crew abandon a perfectly safe ship full of food?`
- `The Flannan Isles lighthouse: what happened to the three keepers in 1900?`
- `The Dancing Plague of 1518: mass hysteria or ergot poisoning?`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Which forensic theory makes the most sense to you? Comment below.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open 0-30s: strongest scene of the video, no channel intro
1. Stakes: why this matters to the viewer's own life
1. 3-5 chapters, each opens with a mini-hook and ends with a re-hook
1. Pattern interrupt every 20-30s (story, number, visual gag)
1. Synthesis + practical takeaway
1. Closing line pointing to the next video
- **Câu kết (CTA):** Explore our complete forensic archive on Cold Case Ink on YouTube.
### Điều cấm kỵ (Avoid)
- Supernatural or alien sensationalism
- Graphic gore or disrespecting victims
- Unverified conspiracy rumors as fact

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_en_forensic_noir` — Forensic noir graphic novel: deep ink black, aged case-file manila, red evidence tags, trench coat silhouette
- **Bảng màu khóa cứng:** `#111111`, `#E8E2D0`, `#5A5F66`, `#C0392B`, `#FFFFFF`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Shadowy faceless trench-coat detective silhouette in a fedora hat holding a warm lantern beam over crimson-tagged archival clues
- **Trang phục (`DEFAULT_OUTFIT`):** Classic flat charcoal trench coat with turned-up collar, wide-brim fedora hat, zero shading
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** Trench coat detective lantern beam highlighting clue + 2-4 uppercase words.
- **Prompt Style gốc:**
  > Classic 2D forensic noir graphic-novel illustration on aged case-file manila canvas (#111111 deep ink black, #E8E2D0 aged case-file manila, #5A5F66 fog-slate, #C0392B forensic evidence crimson); chalk contours, archive folders, magnifying lenses, and high-contrast shadow drama; orthographic 2D, at least 60% negative space, zero 3D, zero gradients.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `hybrid_motion` (Tỷ lệ đồ họa động Remotion/Hyperframes: **45%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **5 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **7–10 phút** cho 1 TikTok Short độc lập; **28–38 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Remotion documentary photo zoom and timestamp typewriter transitions.

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *The Dyatlov Pass Incident: How Avalanche Physics Solved the 1959 Mystery*
- **Thời lượng:** 14 minutes (28 scenes)
- **Câu mở đầu (Cold Open):** "In 1959, nine experienced hikers fled their tent in sub-zero cold without shoes or coats."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 new images):** *forensic mystery files* (50s)
- **Spin-off #2 (0 new images):** *Why did the Mary Celeste crew abandon a perfectly safe ship full of food?* (45s)
- **Spin-off #3 (0 new images):** *The Flannan Isles lighthouse: what happened to the three keepers?* (45s)
- **Fast-Short #4 (5 Flow images):** *The Dancing Plague of 1518: mass hysteria or ergot poisoning?* (50s)

### Backlog chủ đề hạt giống tiếp theo
- The Dyatlov Pass Incident: How Avalanche Physics Solved the 1959 Mystery
- Why Did the Mary Celeste Crew Abandon a Perfectly Safe Ship Full of Food?
- The Flannan Isles Lighthouse: What Happened to the Three Keepers in 1900?
- The Dancing Plague of 1518: Mass Hysteria or Ergot Poisoning?
- The Tunguska Event: How an Airburst Flattened 800 Square Miles Without a Crater

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#history #coldcase #documentary #mystery #forensics #investigation`
- **Nguồn doanh thu:** YouTube AdSense (long), Historical map & investigative dossier prints, Audiobook & documentary streaming partner
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-en-cold-case-ink
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel en_cold_case_ink
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```
