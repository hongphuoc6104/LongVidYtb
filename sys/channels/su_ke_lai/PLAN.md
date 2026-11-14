# KẾ HOẠCH CHI TIẾT KÊNH: SỬ KỂ LẠI (`su_ke_lai`)

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `su_ke_lai` (Đợt triển khai: Wave 1)
- **Nhánh GitHub độc lập:** `channel/su-ke-lai` (`origin/channel/su-ke-lai`)
- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/channel-su-ke-lai`
- **Ngách nội dung:** Lịch sử Việt Nam và thế giới kể như phim
- **Lời hứa thương hiệu (Value Proposition):** Lịch sử không khô: mỗi tập là một bộ phim ngắn có nhân vật và kịch tính.
- **Khán giả mục tiêu:** Người trẻ 16-35 yêu lịch sử nhưng sợ sách giáo khoa
- **Nhân vật dẫn chuyện (Persona):** Người kể chuyện trầm, biết nghỉ đúng lúc, thỉnh thoảng chêm câu hài
- **Giọng văn (Tone):** Kể chuyện điện ảnh, kịch tính, tôn trọng sự thật lịch sử | **Giọng TTS:** `VietNarrator` (1.0x)
- **Phân tách nền tảng bắt buộc:**
  - **TikTok (`short_9x16` — 9:16):** Video ngắn 60–90s, nhịp chuyển cảnh 2–5s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.
  - **YouTube (`long_16x9` — 16:9):** Video dài 15–25 phút, nhịp pattern-interrupt 20–30s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.

## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)
### Kênh mẫu TikTok Short (`short_9x16`)
- **Sử Lược - Tóm Tắt Lịch Sử** (TikTok/YouTube): Fast map-driven summaries with narrative pacing.
### Kênh mẫu YouTube Long (`long_16x9`)
- **OverSimplified** (YouTube): History as a multi-episode sitcom with recurring gags (format only).
- **Hồn Sử Việt** (YouTube): Illustrated storytelling of Vietnamese legends and heroes.

## 3. Luật Viết Kịch Bản & Công Thức Hook
### Nguyên tắc giọng kể
- Start in the middle of the decisive moment, then rewind.
- Every episode centers on one person and one choice.
- Separate documented facts from legend explicitly ('tương truyền...').
- Use recurring light gags sparingly; never mock national heroes.
### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)
- `Năm [năm], một [nhân vật] chỉ có [nguồn lực nhỏ] đối đầu [đối thủ lớn].`
- `Quyết định này của [nhân vật] đã thay đổi lịch sử Việt Nam.`
- `Sự thật đằng sau [sự kiện quen thuộc] không giống sách giáo khoa.`
- `Chỉ một sai lầm, cả [triều đại/đội quân] sụp đổ.`
### Cấu trúc giữ chân TikTok Short (`short_9x16`)
1. Hook <= 3s: shocking claim or relatable pain + striking first frame
1. Open loop: promise the answer, delay it
1. Escalation beats every 2-5s (new visual, number or twist)
1. Payoff: answer the loop in one clear image
1. Closing line
- **Câu kết (CTA):** Cắt ở cao trào: 'Phần tiếp theo có trên YouTube'.
### Cấu trúc giữ chân YouTube Long (`long_16x9`)
1. Cold open in the decisive moment
1. Rewind: who, where, what was at stake
1. Rising action in 3-4 acts with cliffhanger re-hooks
1. Climax and consequence
1. Legacy: what it means for Vietnam today
1. Next episode tease
- **Câu kết (CTA):** Gợi tập tiếp theo của series.
### Điều cấm kỵ (Avoid)
- Politically sensitive modern history
- Unverified legends presented as fact
- Graphic violence

## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native
- **Visual Profile ID:** `ch_dong_ho_folk` — Tranh dân gian Đông Hồ / khắc gỗ trên giấy dó
- **Bảng màu khóa cứng:** `#EFE4C8`, `#B5332E`, `#D9A520`, `#2C4A6E`, `#5E7D3A`, `#1E1E1E`
- **Tạo hình nhân vật (`CAST_APPEARANCE`):** Stylized Dong Ho folk-print human figures with round faces, simple almond eyes, rosy cheek dots and period-accurate Vietnamese costume for the episode's era
- **Trang phục (`DEFAULT_OUTFIT`):** Era-specific flat costume in vermilion, indigo or yellow pigment, woodcut line folds only
- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** One hero figure in action pose + 2-4 word title carved in woodcut letters on do paper.
- **Prompt Style gốc:**
  > 2D Vietnamese Dong Ho folk woodblock-print illustration: bold carved black woodcut outlines (#1E1E1E), flat natural-pigment fills in vermilion (#B5332E), pagoda-tree yellow (#D9A520), indigo (#2C4A6E) and leaf green (#5E7D3A) on a warm handmade do-paper canvas (#EFE4C8) with a subtle paper fiber texture; stylized flat folk figures in period costume, symmetrical decorative composition, orthographic 2D, no gradients, no photorealism, no 3D.

## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)
- **Chế độ Render chủ đạo:** `flow_full_frame` (Tỷ lệ đồ họa động Remotion/Hyperframes: **25%**)
- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **8 ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).
- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **4 video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).
- **Thời gian mục tiêu:** **10–14 phút** cho 1 TikTok Short độc lập; **40–50 phút** cho trọn bộ (1 YouTube Long + 4 TikTok Shorts).
- **Chiến thuật tốc độ riêng của kênh:** Invest full Dong Ho artwork into YouTube Long, then extract 4 cliffhanger TikTok Shorts via omni_platform (0 extra images).

## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)
### YouTube Long #1 (`long_16x9`)
- **Tiêu đề:** *Trận Bạch Đằng Năm 938: Ngô Quyền Đã Tính Toán Thủy Triều & Bẫy Cọc Gỗ Chính Xác Đến Từng Phút Ra Sao?*
- **Thời lượng:** 15 phút (28 cảnh bản đồ + Đông Hồ)
- **Câu mở đầu (Cold Open):** "Mùa đông năm 938, đoàn chiến thuyền khổng lồ của quân Nam Hán tiến vào cửa sông Bạch Đằng mà không hề biết dưới mặt nước phẳng lặng kia là một tử địa."
### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)
- **Spin-off #1 (0 ảnh mới):** *Vì sao tướng Nam Hán biết sông Bạch Đằng hiểm trở mà vẫn sa vào bẫy?* (60s)
- **Spin-off #2 (0 ảnh mới):** *Bí mật kỹ thuật đóng cọc gỗ đầu bịt sắt giữa dòng nước chảy xiết.* (60s)
- **Spin-off #3 (0 ảnh mới):** *Khoảnh khắc con nước rút quyết định 1.000 năm độc lập của dân tộc.* (60s)
- **Fast-Short #4 (8 ảnh Flow):** *Vì sao vua Quang Trung hành quân ra Thăng Long nhanh gấp đôi dự tính?* (65s)

### Backlog chủ đề hạt giống tiếp theo
- Trận Bạch Đằng 938: cái bẫy cọc gỗ của Ngô Quyền
- Vì sao Lý Công Uẩn dời đô về Thăng Long
- Nguyễn Huệ hành quân thần tốc 1789
- Trạng Quỳnh: thật hay chỉ là truyền thuyết
- Vì sao chữ Quốc ngữ thay thế chữ Nôm

## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)
- **Bộ Hashtag chuẩn TikTok:** `#lichsu #lichsuvietnam #sukelai #kechuyen #learnontiktok`
- **Nguồn doanh thu:** YouTube AdSense (watch time dài), Affiliate sách lịch sử, Series membership
- **Lệnh làm việc nhanh trên máy:**
  ```bash
  cd /home/hongphuoc6104/Desktop/vp-channels/channel-su-ke-lai
  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel su_ke_lai
  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv
  ```

## 8. Chuẩn Sản Xuất V2 Đã Chốt (Voice 1.30x & 3-Tier Epic Historical Visuals)
- **Trạng thái khóa:** `LOCKED_PRODUCTION_V2` (chi tiết máy đọc tại `sys/channels/su_ke_lai/channel_v2_production_lock.json`, đối chiếu chuẩn trên tập `vn_su_ke_lai_ep04_nhu_nguyet_1077_long` — 1169.801s, 240 beats, 10 chapters).
- **Giọng đọc & Tốc độ (`voice_lock`):**
  - **Voice Profile:** `VietNarrator_su_ke_lai` (`default_tone: "heroic_epic"`, reference SHA-256 `7bf3594d89a04c8ac3615ae50f192c3bf5bd904c4a5bb890816f4ca977d43808`).
  - **Tốc độ hiệu dụng:** `1.30x` (tổng hợp OmniVoice nền `1.12x` + WSOLA `atempo=1.161` + khoảng nghỉ giữa các beat `0.12s`).
  - **Chuỗi Studio EQ & Master Audio:** `highpass=f=80,equalizer=f=180:t=q:w=1.1:g=1.2,equalizer=f=3200:t=q:w=1.0:g=2.2,equalizer=f=6500:t=q:w=1.2:g=1.5,lowpass=f=15000`; chuẩn đầu ra `-11.0 LUFS` / `-1.0 dBTP`.
- **Hệ thống Hình ảnh 3-Tier (`su_ke_lai_3tier_epic_v2`):**
  - **25% `TIER_1_WARROOM_MAP`:** Bản đồ sa bàn địa hình chiến thuật 3D (phong cách Kings and Generals / Fern), địa hình đá phiến trầm, đường đồng mức ánh đuốc, mũi tên và đội hình hành quân.
  - **25% `TIER_2_TACTICAL_CUTAWAY`:** Mặt cắt 3D & sơ đồ cơ khí quân sự (cọc gỗ lim đóng ngầm, máy bắn đá / nỏ / thuyền hỏa công, lớp phòng tuyến).
  - **50% `TIER_3_EPIC_BATTLE_PAINTING`:** Tranh sơn dầu lịch sử sử thi / khung hình điện ảnh ánh đuốc, giáp sắt đồng, bầu trời bão tố, khói lửa và cờ đỏ.
- **Chuẩn Render 2K & Chuyển cảnh:**
  - **Độ phân giải:** `long_16x9` xuất chuẩn 2K `2560x1440` (`watermark_pos_2k: W-w-48:H-h-48`); `short_9x16` `1080x1920` (`watermark_pos_hd: W-w-36:H-h-36`), `30 fps`.
  - **Chuyển cảnh:** `xfade=fade` thời lượng `0.24s` giữa các beat hình tĩnh Lanczos.

## 9. Khóa Sản Xuất V3 Option 1 (`su_ke_lai_35mm_live_action_v3` — 35mm Historical Live-Action Docudrama)
- **SSOT Skill Đặc Thù Riêng Kênh:** [.agents/skills/vp-channel-su-ke-lai/SKILL.md](../../../.agents/skills/vp-channel-su-ke-lai/SKILL.md) (kèm [visual-grammar-option1.md](../../../.agents/skills/vp-channel-su-ke-lai/references/visual-grammar-option1.md) và [pacing-and-script-rules.md](../../../.agents/skills/vp-channel-su-ke-lai/references/pacing-and-script-rules.md)).
- **Nguyên tắc phối hợp (Không ghi đè quy trình chung):** Giữ nguyên 100% các skill quy trình dùng chung (`vp-research-architect`, `vp-scriptwriting`, `vp-flow-cdp`, `vp-colab-bridge`, `vp-omni-platform`, `vp-production`); tách toàn bộ thông số và ngữ pháp riêng biệt của kênh vào [.agents/skills/vp-channel-su-ke-lai/SKILL.md](../../../.agents/skills/vp-channel-su-ke-lai/SKILL.md):
  - **Topic & Packaging:** Ghép nối thông số riêng của kênh vào `vp-research-architect` (`brief.json`/`content.json` v3.0, `youtube_title <= 55`, `parent_long_id`).
  - **Script & Pacing:** Ghép nối thông số nhịp riêng vào `vp-scriptwriting` (`10 chương × 12 câu zero-filler = 120 câu`, `~9m15s–9m45s`, tách `2` sub-beat/câu = `240` beats `~2.35s/ảnh`; Short `12` beats `~48–58s` với close CTA + cầu nối sang Long ở `15%` cuối).
  - **Visual System:** Chọn ngữ pháp hình ảnh riêng của kênh **Option 1 (`su_ke_lai_35mm_live_action_v3`)** thay cho phong cách 2D Doodle mặc định (`vp-full-frame-quality`) — `35mm Kodak Vision3 500T`, `allowed_text=None` trên 100% khung hình, `clean_beluga_sparkle_pil` + `1.045x` overscan.
  - **Flow Generation:** Ghép nối thông số asset vào `vp-flow-cdp` (`240` khung `16:9` BELUGA cho Long; `12` khung `9:16` + `12` clip `omni_flash` `single_frame_i2v` `end_image_path=None` cho Short; thumbnail Flow-native `2–4` từ in hoa `< 2MB`).
  - **Audio & Colab T4 Render:** Ghép nối profile riêng vào `vp-colab-bridge` với `VietNarrator_su_ke_lai` (`speaking_rate=1.30`, `inter_beat_gap=0.06s`, `chapter_gap=0.18s`, `-11.0 LUFS / -1.0 dBTP`); `h264_nvenc` `2560x1440@30fps` Long (`xfade=fade:duration=0.18`, `FFMETADATA1` 10 chương) & `1440x2560@30fps` Short (`cas=0.55`); bundle `DejaVuSans.ttf`/`DejaVuSans-Bold.ttf` cho `libass`, kiểm tra `delogo` góc trên `omni_flash` trước khi ghim `sys/channels/su_ke_lai/assets/watermark_150x150.png` tại `W-w-36:H-h-36`.
  - **Omni-platform & Publish:** Ghép nối mục tiêu `--channel su_ke_lai` vào `vp-omni-platform` + `vp-production`, xuất bản qua `sys/tools/publish_youtube_cdp.py --channel su_ke_lai` (**đăng Long trước**, lấy URL rồi đăng Short kèm `--related-video <LONG_URL>`).
- **Watermark Bronze/Stone (`150x150` RGBA):** `sys/channels/su_ke_lai/assets/watermark_150x150.png` (SHA-256: `3fc377fb162e880581a044d791e8524f2cf3a877223be42498a3f2604272f665`).


