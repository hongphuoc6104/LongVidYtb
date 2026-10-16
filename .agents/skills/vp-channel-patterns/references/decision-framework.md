# Ma trận Ra Quyết định Kỹ thuật, Hợp Nhất Hình Ảnh & Chuyển Thể Spin-off (Decision Framework)

Tài liệu này cung cấp **Ma trận Ra Quyết định (Decision Matrix)** chuẩn hóa cho toàn bộ quy trình sản xuất video trong Video Pilot: từ khâu định vị phễu nội dung, đóng gói CTR, biên kịch, lựa chọn giọng đọc, ngắt nhịp đến dàn dựng hình ảnh phân lớp và chuyển thể **Long-to-Short Spin-off (`short_9x16`)**.

---

## 1. Ma trận Tổng quan: Khi nào Dùng Cái gì?

| Vấn đề cần quyết định | Lựa chọn A | Lựa chọn B | Tiêu chí quyết định (Khi nào dùng?) | Rủi ro nếu chọn sai |
|:---|:---|:---|:---|:---|
| **Chế độ sản xuất** | **Mode A** *(Structural Replication)* | **Mode B** *(Original Adaptation)* | Dùng **Mode A** khi chạy benchmark nội bộ, đo độ lệch timeline. Dùng **Mode B** khi sản xuất video mới ra kênh. | Chọn sai Mode A cho sản xuất công khai sẽ vi phạm bản quyền nội dung. |
| **Định dạng xuất bản (`sys/format_profiles.py`)** | **`long_16x9`** *(1920x1080, 11–13m, 8 chương / 48 cảnh)* | **`short_9x16`** *(1080x1920, 45–60s, 5 cảnh độc lập)* | Dùng **`long_16x9`** (`subtitles: false`, `speed: 1.22`) cho YouTube Long-form. Dùng **`short_9x16`** (`subtitles: true`, `speed: 1.26`, `max_line_chars: 28`) cho TikTok/YouTube Shorts. | Cắt ngang Chương 2–8 của video 16:9 đem đăng TikTok khiến video mất Hook 3 giây và kịch trần 200 view. |
| **Mật độ giữ hình (`Visual Hold`)** | **Vùng Nguy Hiểm `0:00–0:15`** *(`1.2s – 1.8s`/beat)* | **Vùng Thân Bài `> 0:15`** *(`0.83s – 3.80s`/beat)* | Trong **15 giây đầu (`SC01–SC02`)**, bắt buộc đổi beat camera hoặc nảy sticker mỗi **`1.2s – 1.8s`**. Từ `SC03` trở đi dùng ngưỡng chuẩn `0.83s – 3.80s`. | Để khung hình đứng yên 2.5s–3.8s ngay ở 15 giây đầu làm khán giả lạnh lướt bỏ ngay lập tức. |
| **Dàn dựng Visual Hợp Nhất** | **Editorial Diagram Background Plate** *(`kind: "background"`)* | **Sticker Nghiên Cứu Cut-out** *(`kind: "sticker"`, `x = 0.35 / 0.64`)* | Kết hợp cả hai trong **Layered Motion**: Background vẽ Sơ đồ Tháp học thuật (*Academic Pyramid*) / Flowchart `Question → Gap → Method → Evidence`; Sticker Nghiên Cứu đặt ở Quy tắc 1/3 tương tác trực tiếp với sơ đồ. | Dùng hình ẩn dụ cơ khí sáo rỗng (`brain cutaway`, bàn tính) hoặc đặt sticker chết cứng giữa màn hình `x = 0.50` gây "AI Feel". |
| **Giọng đọc & Tốc độ (SSOT)** | `Adam` `1.22x` *(Thân bài / `long_16x9`)* | `Adam` `1.26x` / `4.2–4.4` syl/s *(30s đầu / `short_9x16`)* | Mặc định duy nhất: `assets/voices/adam/profile.json` trên Colab T4 (`-14.0 LUFS`, `-1.5 dBTP`). Đẩy nhịp 30s đầu lên `4.2–4.4` âm tiết/s (`1.26x` cho `short_9x16`). | Đọc chậm đều đều ở 15s đầu hoặc dùng TTS local làm rớt Retention. |
| **Khoảng lặng âm thanh (`[pause:...]`)** | **Cấm tuyệt đối ở `SC01`** *(`OPENING_SCENE_PAUSE_FORBIDDEN`)* | **Tier-3 Dramatic Pause** *(Tối đa 1–3 lần ở `SC02+`)* | Tuyệt đối **0 thẻ `[pause:...]` trong `SC01`**. Chỉ dùng `[pause:800ms]` / `[pause:900ms]` tối đa 1–3 lần toàn video trước điểm lật ngược định kiến lớn. | Rải 48 thẻ pause cơ học vào mọi cảnh hoặc đặt pause ngay `SC01` làm rề rà nhịp đọc. |

---

## 2. Chi tiết 8 Trục Quyết định Kỹ thuật

### 2.1. Trục 1: Chế độ Vận hành (Mode A vs Mode B)
- **Mode A (Structural Replication & Control Benchmark):** Chỉ dùng nội bộ (`sys/runs/`) để kiểm tra độ chính xác của timeline và động cơ render.
- **Mode B (Original Adaptation & Production):** Sản phẩm xuất bản chính thức. Giữ khung nhân quả 5 hồi nhưng thay đổi 100% đề tài, dữ liệu, lời dẫn và sơ đồ minh họa theo ngách **"Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật"**.

---

### 2.2. Trục 2: Cắt Phân cảnh (Scene Split) vs Nhịp Trực quan (Visual Beats) & Vùng Nguy Hiểm 15s Đầu
- **Quy tắc vàng:** *Đơn vị Scene là ranh giới câu thoại và không gian ($D \ge 5.0\text{s}$); đơn vị Beat là ranh giới chú ý thị giác.*
- **Phân tách 2 vùng tốc độ thị giác:**
  1. **Vùng Nguy Hiểm (`0:00 – 0:15` / `SC01–SC02`):** Bắt buộc bố trí các nhịp `beats[]` và `layers[]` xuất hiện dày đặc mỗi **`1.2s – 1.8s`** (`zoom_in`, `punch_in`, `pan_right`, sticker `pop`/`bounce`).
  2. **Vùng Thân Bài (`sau 0:15` / `SC03+`):** Phân bổ thời lượng theo *Cue-Window Allocation* trong dải **`0.83s – 3.80s`** (sai số `0.000s` tại mọi đầu câu thoại `cue.start`).

---

### 2.3. Trục 3: Động cơ Tổng hợp Âm thanh & Giọng đọc (SSOT)
- **Voice duy nhất:** `Adam` (`assets/voices/adam/profile.json`, model `kjanh/KhanhTTS-OmniVoice` trên Colab T4).
- **Tốc độ chuẩn hóa:** `1.22x` cho `long_16x9` (riêng 30s đầu viết câu ngắn gọn tạo nhịp `4.2–4.4` âm tiết/s) và `1.26x` cho kịch bản `short_9x16` độc lập.
- **Hậu kỳ âm thanh (`sys/audio_processing.py:master`):** `48kHz` Mono PCM16, cắt khoảng lặng nội sinh đầu/cuối (`lead_ms=25`, `trail_ms=30`), chuẩn hóa `-14.0 LUFS`, `-1.5 dBTP`, trộn Sidechain Ducking + Micro-SFX.

---

### 2.4. Trục 4: Hợp Nhất 2 Phong Cách Hình Ảnh Ăn View Trên Kênh (Unified Diagram Plate + Sticker Nghiên Cứu)
Thay vì tách rời 2 kiểu hình ảnh trên kênh — (A) *Sơ đồ Tư duy / Thước đo phân cấp* (ăn `22.1K`, `16.8K`, `3.042` view) và (B) *Nhân vật người que + Thẻ so sánh nền kem* (ăn `883` và `749` view) — bộ pipeline `vp-layered-motion` + Remotion hợp nhất cả hai thành một cấu trúc duy nhất:
1. **Background Plate (`kind: "background"`):**
   - Vẽ chính các **Sơ đồ Tháp học thuật (*Academic Pyramid 9 nguồn nghiên cứu*)**, **Thước đo phân cấp Lý thuyết gốc vs. Sao chép cơ học**, **Đồ thị hàm số tư duy ngược**, hoặc **Sơ đồ chuỗi quyết định `Question → Gap → Method → Evidence → Paper`** theo phong cách **Editorial Graphic** sắc nét (hỗ trợ cả bản nền tối tương phản cao lẫn nền giấy kem ấm áp, tuyệt đối không vẽ nhân vật dính cứng vào nền).
2. **Cut-out Stickers (`kind: "sticker"`):**
   - Đưa nhân vật **Sticker Nghiên Cứu** (đúng hình tượng Avatar kênh: đầu tròn trắng viền đen dày khép kín liên tục) xuất hiện tại tọa độ **Quy tắc 1/3 (`x = 0.35` hoặc `0.64`)** để tương tác trực tiếp với sơ đồ trên Background Plate:
     - Cầm kính lúp soi vào lỗ hổng *Research Gap* trên sơ đồ chuỗi quyết định;
     - Dùng bút đỏ gạch chéo thói quen *Mở Word gõ ngay* hoặc cuốn sách highlight thụ động;
     - Đổ mồ hôi hột trước *Bục Hội Đồng Bảo Vệ Khóa Luận* trong cửa sổ 120 giây đầu.

---

### 2.5. Trục 5: Quản lý Khoảng lặng & Chốt Chặn `SC01` (Pauses & Cadence)
- **Công thức bắt buộc:** $\text{Target Syllables} = \text{round}\Big((\text{Scene Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$.
- **Chốt chặn cứng:**
  - **Cấm `[pause:...]` ở `SC01` (`OPENING_SCENE_PAUSE_FORBIDDEN`):** Cảnh mở đầu 15 giây đầu tiên phải liền mạch 100%.
  - **Trần câu đầu `SC01` (`OPENING_HOOK_TOO_LONG`):** Câu đầu tiên của `SC01` bắt buộc $\le 18$ âm tiết.
  - **Giới hạn Tier-3 Pause (`EXCESSIVE_DRAMATIC_PAUSES`):** Toàn bộ kịch bản chỉ dùng tối đa **1–3 thẻ `[pause:800ms]` / `[pause:900ms]`** tại điểm lật ngược định kiến lớn.

---

### 2.6. Trục 6: Ma trận Biểu cảm Nhân vật Sticker Nghiên Cứu (Character Expression & Pose)

| Trạng thái kịch bản học thuật | Biểu cảm khuôn mặt | Tư thế cơ thể (Sticker Nghiên Cứu Pose) | Ứng dụng điển hình trên Sơ đồ Background |
|:---|:---|:---|:---|
| **Ảo giác hiểu biết / Học vẹt** | Mắt nhắm nghiền gạch ngang (`- -`), miệng rũ sóng | Ôm chồng giáo trình highlight kín chữ, hai vai rũ xuống mệt mỏi (`x = 0.35`) | Mở đầu `SC01`: Đọc lại sách 5 lần hay mở Word gõ ngay lúc 2 giờ sáng |
| **Phản biện / Hoài nghi khoa học** | Lông mày xếch, một mắt to một mắt nhỏ | Tay cầm kính lúp soi thẳng vào khe hở trên sơ đồ, đầu nghiêng 15 độ (`x = 0.64`) | `SC02–SC03`: Phát hiện lỗ hổng *Research Gap* hoặc lật tẩy định kiến học vẹt |
| **Áp lực Hội đồng Bảo vệ 120s** | Mắt mở to căng thẳng, giọt mồ hôi rơi bên thái dương | Đứng thẳng trước bục bảo vệ, hai tay nắm chặt tập khóa luận (`x = 0.35`) | Giải phẫu tâm lý Hội đồng bảo vệ khóa luận trong 120 giây đầu tiên |
| **Bừng tỉnh / Nắm bản chất Q1** | Mắt sáng rõ (`O O`), miệng mỉm cười tự tin | Tay cầm bút chỉ thẳng lên đỉnh Tháp Học Thuật (*Academic Pyramid*) (`x = 0.64`) | `SC04–SC05`: Làm chủ chuỗi `Question → Gap → Method → Evidence → Paper` |

---

### 2.7. Trục 7: Thiết kế Âm thanh & Micro-Foley
- **Từ neo âm thanh (Semantic Anchor):** Tiếng bút dạ quang gạch giấy, tiếng gõ phím xóa dòng chữ trên Word, tiếng đồng hồ đếm ngược 120 giây phòng bảo vệ (`sfx_clock_tick.wav`), tiếng `pop` khi Sticker Nghiên Cứu xuất hiện và `whoosh` khi chuyển tầng Tháp Học Thuật.
- **Sidechain Ducking BGM:** Hạ nhạc nền xuống **-20dB đến -24dB** khi có giọng đọc, nâng nhẹ lên **-14dB** tại khoảng nghỉ kịch tính (`[pause:900ms]`) hoặc đoạn kết payoff.

---

### 2.8. Trục 8: Chuyển Thể Video Dài Sang Ngắn (`Long-to-Short Spin-off Repurposing` — Giải quyết Bẫy 2)
- **Quy tắc Nghiêm Cấm:** **Tuyệt đối KHÔNG cắt ngang các chương giữa (`CH02..CH08`) của video `long_16x9` (11–13 phút) để đăng lên TikTok/Shorts.** Một đoạn cắt giữa chừng không có Hook phản trực giác trong 3 giây đầu, thiếu ngữ cảnh mở bài và sai bố cục khung hình dọc sẽ bị thuật toán TikTok chặn đứng ở ngưỡng ~200 view.
- **Quy trình Spin-off Độc Lập (`build_short_spinoff_topics`):**
  1. Từ 1 hồ sơ nghiên cứu gốc (`long_16x9`), chọn ra **2–3 nghịch lý đắt giá nhất** (mỗi nghịch lý tương ứng với 1 điểm chạm Lưu/Share cao).
  2. Kiến trúc từng nghịch lý thành một gói kịch bản **`short_9x16` độc lập** (`1080x1920`, thời lượng `45–60s`, đúng 5 cảnh `SC01..SC05`).
  3. Viết lại hoàn toàn **`SC01` bằng câu Counter-Intuitive Hook $\le 18$ âm tiết** độc lập, đặt tốc độ `speed: 1.26` (`4.2–4.4` âm tiết/s ở 30s đầu), bật phụ đề nhảy chữ theo `word_timestamps` (`subtitles: true`, `max_line_chars: 28`, chừa đáy `18%`).

---

## 3. Bảng Tự kiểm tra Trước khi Duyệt Kịch bản (Pre-flight Checklist)

- [ ] **Đóng gói CTR & Ngách chuẩn (`brief.json`):** `youtube_title <= 55` ký tự, `thumbnail_spec` (2–4 từ in hoa), đúng ngách Tư Duy Nghiên Cứu (không có từ khóa Excel/Slide/Na).
- [ ] **Chốt chặn 15s đầu (`SC01`):** Câu đầu $\le 18$ âm tiết, 0 thẻ `[pause:...]`, Việt hóa 100% trong 60s đầu, mật độ đổi hình `1.2s–1.8s`.
- [ ] **Đã tính toán số âm tiết & trần câu:** Mọi câu đơn $\le 25$ âm tiết, vế câu $\le 18$ âm tiết, tổng thẻ `[pause:...]` toàn video $\le 3$, $|\text{drift}| \le 0.30\text{s}$.
- [ ] **Hợp nhất Sơ đồ + Sticker Nghiên Cứu:** Background Plate vẽ Sơ đồ Học thuật sắc nét; Sticker Nghiên Cứu đặt tại Quy tắc 1/3 (`x = 0.35` hoặc `0.64`).
- [ ] **Tách biệt `long_16x9` và `short_9x16` Spin-offs:** Mọi video đăng TikTok đều là kịch bản `short_9x16` 5 cảnh độc lập có phụ đề nhảy chữ.
