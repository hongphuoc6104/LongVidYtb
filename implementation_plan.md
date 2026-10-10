# Implementation Plan: Phương Án B — Bổ Sung Hình Cắt Nhịp & Auto-Reframe

> **Mục tiêu**: Nâng cấp nhịp dựng video (Pacing & Visual Dynamic) cho toàn bộ series *Ancient Humans* (đặc biệt là Chương 3 và Chương 4), chia nhỏ các phân cảnh dài > 3.0s thành các sub-beat năng động từ 1.5s – 2.0s/hình, loại bỏ hoàn toàn hạn chế lùi viền 20% cho phụ đề, và kích hoạt cơ chế Smart Auto-Reframe khi tắt phụ đề (`hideSubtitles: true`).

---

## 1. Tổng Quan & Bối Cảnh Kỹ Thuật (Architecture & Context)

### 1.1 Vấn đề cốt lõi cần giải quyết
1. **Pacing gãy nhịp ở các phân cảnh tĩnh dài**: Hiện tại có tới **75/245 shots dài > 3.0s**, trong đó Chương 3 có shot dài tới **10.51s** (Shot #79) và Chương 4 có shot dài tới **12.15s** (Shot #115). Việc giữ nguyên một hình vẽ tĩnh trong suốt 6s–12s làm giảm đáng kể nhịp độ thu hút người xem.
2. **Khung hình bị lãng phí khoảng trống (Bottom 20% Subtitle Restriction)**: Toàn bộ prompt trước đây đều chứa câu chỉ thị:  
   `"Keep the bottom 20% of the frame plain and unobstructed for subtitles."`  
   Điều này khiến AI tạo ảnh ép nhân vật và chi tiết lên nửa trên, tạo ra dải trống trắng/nhạt ở 20% cạnh dưới. Khi tắt phụ đề (`hideSubtitles: true`), khoảng trống này khiến hình ảnh bị "lơ lửng".
3. **Giải pháp Phương án B**:
   - Chia tách các shot > 3.0s thành các sub-beat nhỏ (1.5s – 2.0s đổi 1 hình) tập trung vào cận cảnh biểu cảm (extreme close-up), đổi góc camera (medium shot -> macro details), và visual actions bổ trợ.
   - Bỏ hoàn toàn câu cấm 20% khỏi prompt, để AI render full-bleed tự nhiên.
   - Tích hợp **Smart Auto-Reframe** trong engine renderer: khi `hideSubtitles: true`, tự động scale ảnh nhẹ ~12–15% (1.14x) và hạ tâm ảnh xuống để mặt đất/mặt bàn hạ sát xuống đáy khung hình.

---

## 2. Thống Kê & Phân Tích Phân Cảnh Dài (> 3.0s) Toàn Bộ 8 Chương

| Chương | Tiêu đề | Tổng số shots | Số shots > 3.0s | Max duration | Tổng thời lượng shots dài | Số sub-beats bổ sung dự kiến |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **Ch 1** | The mystery of modern time | 39 | 3 | 3.50s | 10.2s | +4 shots |
| **Ch 2** | Skeletons as historical diary | 37 | 8 | 7.87s | 42.6s | +15 shots |
| **Ch 3** | Life as a hunter-gatherer | 28 | **10** | **10.51s** | **51.3s** | **+18 shots** |
| **Ch 4** | The 17-hour work week | 20 | **9** | **12.15s** | **48.0s** | **+18 shots** |
| **Ch 5** | The value of social time | 34 | 11 | 12.11s | 61.1s | +22 shots |
| **Ch 6** | Nighttime and birth of culture | 30 | 11 | 11.08s | 54.5s | +20 shots |
| **Ch 7** | The trap of agriculture | 36 | 16 | 12.01s | 64.5s | +28 shots |
| **Ch 8** | Trading freedom for security | 21 | 7 | 8.51s | 34.1s | +12 shots |
| **TỔNG** | **Toàn bộ 8 Chương** | **245** | **75** | **12.15s** | **366.3s** | **+137 shots** |

---

## 3. Kế Hoạch Chia Tách Sub-Beat Chi Tiết (Chương 3 & Chương 4)

### 3.1 Chương 3: Cuộc sống người săn bắt hái lượm (Life as a hunter-gatherer)
*Tổng thời lượng: 83.0s | 10 shots dài cần chia tách (+18 shots mới)*

1. **Shot #78 (`shot_02_159.76s.jpg`, 4.27s) -> Chia 2 Sub-beats**:
   - `Beat 78a (2.13s)`: *Wide shot* - Người que thức dậy thảnh thơi trên thảo nguyên, ánh bình minh ấm áp chiếu qua tán cây acacia.
   - `Beat 78b (2.14s)`: *Close-up reaction* - Cận cảnh khuôn mặt người que mỉm cười nhẹ nhõm, đôi mắt chấm tròn sáng ngời, không có bất kỳ tiếng chuông báo thức nào.
2. **Shot #79 (`shot_03_164.03s.jpg`, 10.51s) -> Chia 6 Sub-beats**:
   - `Beat 79a (1.75s)`: *Wide camp* - Lều trại nguyên thủy buổi sáng, bếp lửa tàn còn bốc làn khói mỏng.
   - `Beat 79b (1.75s)`: *Medium shot* - Người que vươn vai sảng khoái, gân cốt thả lỏng theo nhịp sinh học tự nhiên.
   - `Beat 79c (1.75s)`: *Close-up hands* - Bàn tay cầm lấy bầu nước bằng quả bầu khô, uống ngụm nước trong lành.
   - `Beat 79d (1.75s)`: *Infographic concept* - Mặt trời từ từ nhô lên trên đường chân trời, không có kim đồng hồ ép buộc.
   - `Beat 79e (1.75s)`: *Group interaction* - Hai người que ngồi trò chuyện thong thả bên tảng đá ấm.
   - `Beat 79f (1.76s)`: *Macro detail* - Đôi chân trần vững chãi bước trên nền đất thảo nguyên mềm mại.
3. **Shot #80 (`shot_04_174.54s.jpg`, 3.37s) -> Chia 2 Sub-beats**:
   - `Beat 80a (1.68s)`: *Medium shot* - Nhóm người que cùng thưởng thức hạt mongongo và trái cây dại.
   - `Beat 80b (1.69s)`: *Close-up gesture* - Người que giơ tay chỉ về phía đồi xa, thảo luận hướng hái lượm hôm nay.
4. **Shot #88 (`shot_12_190.26s.jpg`, 3.44s) -> Chia 2 Sub-beats**:
   - `Beat 88a (1.72s)`: *Wide group* - Cả bộ tộc ngồi vòng tròn cùng đưa ra quyết định dựa trên dấu chân thú.
   - `Beat 88b (1.72s)`: *Close-up track* - Cận cảnh một người que cúi xuống chạm tay vào dấu chân thú in trên cát ẩm.
5. **Shot #92 (`shot_16_198.83s.jpg`, 9.21s) -> Chia 5 Sub-beats**:
   - `Beat 92a (1.84s)`: *Medium shot* - Người que hái lượm dùng cành cây bới củ dại mọng nước từ lòng đất.
   - `Beat 92b (1.84s)`: *Macro nut basket* - Cận cảnh giỏ đan đầy ắp hạt mongongo giàu dinh dưỡng.
   - `Beat 92c (1.84s)`: *Smile expression* - Biểu cảm tươi vui, thoải mái của người que khi nguồn thức ăn dồi dào.
   - `Beat 92d (1.84s)`: *Tree canopy* - Bóng mát râm ran dưới túp cây bao báp xòe rộng.
   - `Beat 92e (1.85s)`: *Walking back* - Vác giỏ nhẹ nhàng trên vai, bước đi nhịp nhàng không vội vã.
6. **Shot #94 (`shot_18_208.88s.jpg`, 4.34s) -> Chia 2 Sub-beats**:
   - `Beat 94a (2.17s)`: *Establishing* - Quay về làng vào đầu giờ chiều, mặt trời mới đứng bóng.
   - `Beat 94b (2.17s)`: *Camp return* - Đặt giỏ thức ăn xuống giữa làng, mọi người cùng quây quần đón nhận.
7. **Shot #97 (`shot_21_216.02s.jpg`, 3.60s) -> Chia 2 Sub-beats**:
   - `Beat 97a (1.80s)`: *Full body nap* - Người que nằm ngả lưng dưới bóng râm gốc cây bao báp thiu thiu ngủ trưa.
   - `Beat 97b (1.80s)`: *Breeze mood* - Cận cảnh chiếc lá khẽ đung đưa trong gió, không gian yên bình tuyệt đối.
8. **Shot #101 (`shot_25_225.36s.jpg`, 3.37s) -> Chia 2 Sub-beats**:
   - `Beat 101a (1.68s)`: *Action wide* - Linh dương chạy trốn dưới nắng gắt, thở dốc vì không thoát được nhiệt cơ thể.
   - `Beat 101b (1.69s)`: *Close-up animal* - Cận cảnh con mồi thè lưỡi thở hổn hển, kiệt sức vì tích nhiệt nội tại.
9. **Shot #102 (`shot_26_228.73s.jpg`, 3.17s) -> Chia 2 Sub-beats**:
   - `Beat 102a (1.58s)`: *Pacing stride* - Người que thợ săn duy trì bước chạy bền bỉ, mồ hôi bốc hơi làm mát da.
   - `Beat 102b (1.59s)`: *Determined eyes* - Ánh mắt chấm tròn kiên định, hơi thở đều đặn qua hàng giờ đồng hồ.
10. **Shot #104 (`shot_28_233.43s.jpg`, 6.01s) -> Chia 3 Sub-beats**:
   - `Beat 104a (2.00s)`: *Triumphant walk* - Thợ săn mang chiến lợi phẩm trở về bộ tộc trong ánh hoàng hôn vàng rực.
   - `Beat 104b (2.00s)`: *Sharing meat* - Cảnh chia đều phần thịt cho các gia đình, không tích trữ, không tranh giành.
   - `Beat 104c (2.01s)`: *Community joy* - Nụ cười rạng rỡ của cả bộ tộc quây quần chuẩn bị lửa tối.

---

### 3.2 Chương 4: Tuần làm việc 17 giờ (The 17-hour work week)
*Tổng thời lượng: 77.0s | 9 shots dài cần chia tách (+18 shots mới)*

1. **Shot #106 (`shot_02_242.44s.jpg`, 4.77s) -> Chia 3 Sub-beats**:
   - `Beat 106a (1.59s)`: *Establishing* - Nhà nhân chủng học Richard Lee năm 1963 đến rìa sa mạc Kalahari cằn cỗi.
   - `Beat 106b (1.59s)`: *Tool macro* - Cận cảnh chiếc đồng hồ bấm giờ cơ học Thụy Sĩ và cuốn sổ tay ghi chép.
   - `Beat 106c (1.59s)`: *Observer stance* - Richard Lee đứng quan sát từ xa dưới bóng cây gai sa mạc.
2. **Shot #108 (`shot_04_249.15s.jpg`, 3.27s) -> Chia 2 Sub-beats**:
   - `Beat 108a (1.63s)`: *Preconception* - Minh họa định kiến: người nguyên thủy phải vật lộn đói khát đến cùng cực.
   - `Beat 108b (1.64s)`: *Reality clash* - Dấu chấm hỏi to lớn xuất hiện khi thực tế hoàn toàn trái ngược.
3. **Shot #111 (`shot_07_256.29s.jpg`, 6.37s) -> Chia 4 Sub-beats**:
   - `Beat 111a (1.59s)`: *Shadowing labor* - Richard Lee đi sau một người que đo thời gian tìm thức ăn bằng đồng hồ bấm giờ.
   - `Beat 111b (1.59s)`: *Stopwatch tick* - Cận cảnh kim đồng hồ chỉ đúng 2 tiếng rồi dừng lại.
   - `Beat 111c (1.59s)`: *Notes check* - Gạch một nét đậm trên trang sổ ghi chép ngày thứ Ba.
   - `Beat 111d (1.60s)`: *Surprised scientist* - Người que Richard Lee đẩy kính, mắt mở to vì không tin vào số liệu.
4. **Shot #113 (`shot_09_265.16s.jpg`, 4.34s) -> Chia 2 Sub-beats**:
   - `Beat 113a (2.17s)`: *Tool repair* - Người que mài lại mũi tên bằng đá chỉ mất vài phút mỗi tuần.
   - `Beat 113b (2.17s)`: *No maintenance* - Không có máy móc hỏng hóc, không có hóa đơn bảo trì cần thanh toán.
5. **Shot #115 (`shot_11_271.77s.jpg`, 12.15s) -> Chia 7 Sub-beats (Shot dài nhất toàn chương)**:
   - `Beat 115a (1.73s)`: *Big bold number* - Đồ họa con số khổng lồ nổi bật **"17 GIỜ / TUẦN"** khoanh tròn nét đỏ.
   - `Beat 115b (1.73s)`: *Daily breakdown* - Biểu đồ cột: chia đều mỗi ngày chỉ tốn vỏn vẹn **2.4 giờ lao động**.
   - `Beat 115c (1.73s)`: *Leisure open field* - Khoảng thời gian còn lại trong ngày hoàn toàn trống trải, tự do.
   - `Beat 115d (1.73s)`: *Contrast shadow* - Bóng mờ của nhân viên văn phòng hiện đại đang bị vây quanh bởi email.
   - `Beat 115e (1.73s)`: *Relaxing hunter* - Người que Ju/'hoansi thong thả nằm nghe tiếng gió thảo nguyên.
   - `Beat 115f (1.73s)`: *Children play* - Trẻ con bộ lạc chạy nhảy chơi trò ném sỏi mà không cần đi học thêm.
   - `Beat 115g (1.77s)`: *Calm conclusion* - Cân bằng tuyệt đối giữa sinh tồn và nghỉ ngơi trọn vẹn.
6. **Shot #117 (`shot_13_286.59s.jpg`, 3.90s) -> Chia 2 Sub-beats**:
   - `Beat 117a (1.95s)`: *Modern calendar* - Lịch làm việc 40 giờ: người hiện đại đã chạm mốc 17 giờ ngay từ trưa thứ Tư!
   - `Beat 117b (1.95s)`: *Exhausted clerk* - Nhân viên văn phòng gục đầu xuống bàn phím máy tính lúc 14:00 thứ Tư.
7. **Shot #119 (`shot_15_292.56s.jpg`, 4.24s) -> Chia 2 Sub-beats**:
   - `Beat 119a (2.12s)`: *Academic skepticism* - Giới học giả nghi ngờ: "Phải chăng bộ lạc Kalahari chỉ là ngoại lệ may mắn?"
   - `Beat 119b (2.12s)`: *World map transition* - Bản đồ thế giới mở ra với 4 mũi tên hướng tới các châu lục khác nhau.
8. **Shot #120 (`shot_16_296.80s.jpg`, 4.84s) -> Chia 3 Sub-beats**:
   - `Beat 120a (1.61s)`: *Tanzania Hadza* - Nghiên cứu độc lập tại bộ lạc Hadza ở Tanzania: cũng chỉ 14–18 giờ/tuần!
   - `Beat 120b (1.61s)`: *Hadza forager* - Người que Hadza trèo cây lấy mật ong rừng thoăn thoắt.
   - `Beat 120c (1.62s)`: *Badge verification* - Huy hiệu số liệu màu xanh lá "15h/week" đóng dấu xác thực.
9. **Shot #122 (`shot_18_303.54s.jpg`, 4.14s) -> Chia 2 Sub-beats**:
   - `Beat 122a (2.07s)`: *Australia Martu* - Người bản địa Martu tại sa mạc Tây Úc khắc nghiệt: cũng chỉ dưới 20 giờ/tuần.
   - `Beat 122b (2.07s)`: *Universal law* - Kết luận khoa học: 15–20 giờ là hằng số sinh học chung của loài người suốt 300,000 năm!

---

## 4. Quy Trình Điều Phối Tạo Ảnh Qua Chrome CDP (`vp-flow-cdp`)

### 4.1 Cấu hình 3 Chrome Profiles đồng thời
Theo đặc tả của Skill `vp-flow-cdp`:
- `Profile 1`: Port `9222`, thư mục `~/.config/google-chrome/Profile 1`
- `Profile 2`: Port `9223`, thư mục `~/.config/google-chrome/Profile 2`
- `Profile 3`: Port `9224`, thư mục `~/.config/google-chrome/Profile 3`

### 4.2 Chia Patch & Phân Phối (Patch Partitioning)
- **Patch Size**: 2 đến 4 shots/patch (mặc định cấu hình `patch_size: 3`).
- **Phân bổ song song 3 profiles**:
  - `Patch 1` (Shot 78a, 78b, 79a) -> Profile 1
  - `Patch 2` (Shot 79b, 79c, 79d) -> Profile 2
  - `Patch 3` (Shot 79e, 79f, 80a) -> Profile 3
  - `Patch 4` (Shot 80b, 88a, 88b) -> Profile 1
  - ... tuần tự xoay vòng đều đặn.
- **Dependency Guard (`based_on`)**: Các shot có quan hệ biến thể (`based_on`) từ cùng một bối cảnh phải được gom chung vào cùng 1 patch trên cùng 1 profile để giữ ngữ cảnh browser.

### 4.3 Failover & Cooldown Recovery
- Bắt lỗi tự động: Khi phát hiện `PUBLIC_ERROR_UNUSUAL_ACTIVITY`, `CAPTCHA`, HTTP 429:
  1. Profile gặp lỗi lập tức bị đưa vào trạng thái `COOLDOWN` (60s).
  2. Các shot chưa hoàn thành trong patch đó được tự động tái phân phối sang 2 profile còn lại đang `healthy`.
  3. Hoàn tất tải ảnh và metadata sidecar `.json` vào thư mục đích.

---

## 5. Quy Chuẩn Kỹ Thuật Render & Auto-Reframe (Colab Tesla T4)

### 5.1 Renderer Smart Auto-Reframe Invariants
- **Kích hoạt**: Tự động khi `hideSubtitles: true` (hoặc cờ `autoReframe: true`).
- **Scale Factor**: `1.14x` (tăng ~14% kích thước hình ảnh).
- **Trục dời tâm**: `translateY += 6.0%`, `focusY = Math.min(85, focusY + 18%)`.
- **Hiệu quả thực tế**:
  - Triệt tiêu hoàn toàn khoảng trắng 20% bên dưới chân khung hình do prompt cũ tạo ra.
  - Mặt bàn làm việc, mặt đất, thảm cỏ hạ sát xuống cạnh dưới tự nhiên, tạo bố cục điện ảnh vững chắc.
  - Toàn bộ chuyển động Ken Burns (`punch_in`, `zoom_in`, `pan_left`, `pan_right`, `line_boil`) tiếp tục hoạt động trơn tru trên nền reframed.

### 5.2 Verification & Packaging Contract
- Render video trên **Colab Tesla T4 GPU** với Playwright Chromium Headless an toàn (`--no-sandbox`, `--disable-dev-shm-usage`, `DISABLE_FROM_SURFACE=true`).
- Kiểm tra kỹ thuật với `ffprobe`:
  - Độ phân giải: `1920x1080` (16:9 Widescreen).
  - Codec: Video H.264 (`h264`), Audio AAC (`aac`).
  - Khớp thời lượng chính xác với audio lồng tiếng (sai lệch <= 0.25s).
- Đồng bộ vào các gói phát hành `sys/exports/ancient_humans_flowkit_bundle/` và `video/`.
