# Ma trận Ra Quyết định Kỹ thuật, Hợp Nhất Hình Ảnh & Chuyển Thể Spin-off (Decision Framework)

Tài liệu này cung cấp **Ma trận Ra Quyết định (Decision Matrix)** chuẩn hóa cho toàn bộ quy trình sản xuất video trong Video Pilot: từ khâu định vị phễu nội dung, đóng gói CTR, biên kịch, lựa chọn giọng đọc, ngắt nhịp đến dàn dựng hình ảnh phân lớp và chuyển thể **Long-to-Short Spin-off (`short_9x16`)**.

---

## 1. Ma trận Tổng quan: Khi nào Dùng Cái gì?

| Vấn đề cần quyết định | Lựa chọn A | Lựa chọn B | Tiêu chí quyết định (Khi nào dùng?) | Rủi ro nếu chọn sai |
|:---|:---|:---|:---|:---|
| **Chế độ sản xuất** | **Mode A** *(Structural Replication)* | **Mode B** *(Original Adaptation)* | Dùng **Mode A** khi chạy benchmark nội bộ, đo độ lệch timeline. Dùng **Mode B** khi sản xuất video mới ra kênh. | Chọn sai Mode A cho sản xuất công khai sẽ vi phạm bản quyền nội dung. |
| **Định dạng xuất bản (`sys/format_profiles.py`)** | **`long_16x9`** *(1920x1080, 11–13m, 8 chương / 48 cảnh)* | **`short_9x16`** *(1080x1920, 45–60s, 5 cảnh độc lập)* | Dùng **`long_16x9`** (`subtitles: false`, `voice: "VietNarrator"`, `speed: 1.0`) cho YouTube Long-form. Dùng **`short_9x16`** (`subtitles: true`, `voice: "VietNarrator"`, `speed: 1.0`, `max_line_chars: 28`) cho TikTok/YouTube Shorts. | Cắt ngang Chương 2–8 của video 16:9 đem đăng TikTok khiến video mất Hook 3 giây và kịch trần 200 view. |
| **Mật độ giữ hình (`Visual Hold`)** | **Cold open `0:00–0:12.5`** *(8–9 ảnh khi lời thoại hỗ trợ)* | **Vùng Thân Bài `> 0:15`** *(`0.83s – 3.80s`/beat)* | Hướng tới khoảng 4 ảnh trong 5 giây đầu và 8–9 ảnh trong 12–12,5 giây; neo cut vào lời thoại và xác nhận trên WAV. Từ `SC03` trở đi dùng cue window `0.83s–3.80s`. | Gắn cut theo nhịp đều mà không khớp ý lời thoại hoặc giữ một hình quá lâu ở đoạn mở đầu. |
| **Dàn dựng Visual Hợp Nhất** | **Sơ đồ và nhân vật trong cùng ảnh** *(`kind: "scene"`)* | **Cận cảnh đạo cụ / cảnh rộng / biến thể tại chỗ / thẻ khái niệm** | Tạo ảnh toàn khung có nhân vật, đạo cụ và môi trường cùng trong một bố cục; dùng `based_on` + `preserve`/`change` khi cần giữ bối cảnh giữa hai beat. | Tách nhân vật khỏi bối cảnh thành sticker hoặc giữ các thành phần không cùng một không gian vật lý. |
| **Giọng đọc & Tốc độ (SSOT)** | `VietNarrator` `1.0x` *(Thân bài / `long_16x9`)* | `VietNarrator` `1.0x` / `4.2–4.4` syl/s *(30s đầu / `short_9x16`)* | Mặc định duy nhất: `assets/voices/viet_narrator/profile.json` trên Colab T4 (`-14.0 LUFS`, `-1.5 dBTP`, dải hợp lệ `[0.90, 1.15]`, điều biến `tone` `0.98`, `1.02`, `0.92`). Đẩy nhịp câu 30s đầu lên `4.2–4.4` âm tiết/s. | Đọc chậm đều đều ở 15s đầu hoặc dùng TTS local làm rớt Retention. |
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
  1. **Cold open (`0:00–0:12.5`):** Khi lời thoại hỗ trợ, dùng khoảng 8–9 ảnh scene toàn khung, neo cut vào danh từ hoặc hành động cụ thể; duyệt timing theo WAV.
  2. **Vùng Thân Bài (`sau 0:15` / `SC03+`):** Phân bổ thời lượng theo *Cue-Window Allocation* trong dải **`0.83s–3.80s`** (sai số `0.000s` tại mọi đầu câu thoại `cue.start`).

---

### 2.3. Trục 3: Động cơ Tổng hợp Âm thanh & Giọng đọc (SSOT)
- **Voice duy nhất:** `VietNarrator` (`assets/voices/viet_narrator/profile.json`, model `kjanh/KhanhTTS-OmniVoice` trên Colab T4, hỗ trợ cả `vi` và `en`).
- **Tốc độ chuẩn hóa:** `1.0x` cho cả `long_16x9` và `short_9x16` (riêng 30s đầu viết câu ngắn gọn tạo nhịp `4.2–4.4` âm tiết/s, kết hợp điều biến `tone` `0.98`, `1.02`, `0.92` qua `resolve_tone_speed`).
- **Hậu kỳ âm thanh (`sys/audio_processing.py:master`):** `48kHz` Mono PCM16, cắt khoảng lặng nội sinh đầu/cuối (`lead_ms=25`, `trail_ms=30`), chuẩn hóa `-14.0 LUFS`, `-1.5 dBTP`, trộn Sidechain Ducking + Micro-SFX.

---

### 2.4. Trục 4: Ảnh Toàn Khung và Tính Liên Tục Hành Động
Mỗi visual beat là một ảnh `kind: "scene"` hoàn chỉnh. Dùng sơ đồ, đạo cụ, nhân vật và môi trường trong cùng bố cục; chọn cận cảnh hoặc cảnh rộng theo trọng tâm câu thoại. Với cùng địa điểm, dùng `based_on` cùng mô tả `preserve`/`change` để giữ bố cục và chỉ đổi hành động nhìn thấy được. Dùng ảnh độc lập cho scene cut, thẻ khái niệm nền trắng hoặc đổi góc lớn. Không tạo background/sticker cutout hay chu kỳ shot type cố định.

---

### 2.5. Trục 5: Quản lý Khoảng lặng & Chốt Chặn `SC01` (Pauses & Cadence)
- **Công thức bắt buộc:** $\text{Target Syllables} = \text{round}\Big((\text{Scene Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$.
- **Chốt chặn cứng:**
  - **Cấm `[pause:...]` ở `SC01` (`OPENING_SCENE_PAUSE_FORBIDDEN`):** Cảnh mở đầu 15 giây đầu tiên phải liền mạch 100%.
  - **Trần câu đầu `SC01` (`OPENING_HOOK_TOO_LONG`):** Câu đầu tiên của `SC01` bắt buộc $\le 18$ âm tiết.
  - **Giới hạn Tier-3 Pause (`EXCESSIVE_DRAMATIC_PAUSES`):** Toàn bộ kịch bản chỉ dùng tối đa **1–3 thẻ `[pause:800ms]` / `[pause:900ms]`** tại điểm lật ngược định kiến lớn.

---

### 2.6. Trục 6: Ma trận Biểu cảm và Hành động Nhân vật Trong Cảnh

| Trạng thái kịch bản học thuật | Biểu cảm khuôn mặt | Hành động nhân vật trong toàn cảnh | Ứng dụng điển hình |
|:---|:---|:---|:---|
| **Ảo giác hiểu biết / Học vẹt** | Mắt nhắm nghiền gạch ngang (`- -`), miệng rũ sóng | Ngồi trước chồng giáo trình highlight kín chữ, vai rũ xuống | Mở đầu `SC01`: Đọc lại sách nhiều lần hoặc mở Word lúc 2 giờ sáng |
| **Phản biện / Hoài nghi khoa học** | Lông mày xếch, một mắt to một mắt nhỏ | Cầm kính lúp kiểm tra khe hở được vẽ ngay trên sơ đồ | `SC02–SC03`: Phát hiện lỗ hổng *Research Gap* |
| **Áp lực Hội đồng Bảo vệ 120s** | Mắt mở to căng thẳng, giọt mồ hôi bên thái dương | Đứng trước bục bảo vệ và bàn hội đồng, tay nắm chặt tập khóa luận | Giải phẫu tâm lý hội đồng trong 120 giây đầu |
| **Bừng tỉnh / Nắm bản chất Q1** | Mắt sáng rõ (`O O`), miệng mỉm cười tự tin | Chỉ vào đỉnh Tháp Học Thuật trong cùng khung hình | `SC04–SC05`: Làm chủ chuỗi `Question → Gap → Method → Evidence → Paper` |

---

### 2.7. Trục 7: Thiết kế Âm thanh & Micro-Foley
- **Từ neo âm thanh (Semantic Anchor):** Tiếng bút dạ quang gạch giấy, tiếng gõ phím xóa dòng chữ trên Word, tiếng đồng hồ đếm ngược 120 giây phòng bảo vệ (`sfx_clock_tick.wav`), và tiếng `cut`/`whoosh` ở điểm chuyển ý.
- **Sidechain Ducking BGM:** Hạ nhạc nền xuống **-20dB đến -24dB** khi có giọng đọc, nâng nhẹ lên **-14dB** tại khoảng nghỉ kịch tính (`[pause:900ms]`) hoặc đoạn kết payoff.

---

### 2.8. Trục 8: Chuyển Thể Video Dài Sang Ngắn (`Long-to-Short Spin-off Repurposing` — Giải quyết Bẫy 2)
- **Quy tắc Nghiêm Cấm:** **Tuyệt đối KHÔNG cắt ngang các chương giữa (`CH02..CH08`) của video `long_16x9` (11–13 phút) để đăng lên TikTok/Shorts.** Một đoạn cắt giữa chừng không có Hook phản trực giác trong 3 giây đầu, thiếu ngữ cảnh mở bài và sai bố cục khung hình dọc sẽ bị thuật toán TikTok chặn đứng ở ngưỡng ~200 view.
- **Quy trình Spin-off Độc Lập (`build_short_spinoff_topics`):**
  1. Từ 1 hồ sơ nghiên cứu gốc (`long_16x9`), chọn ra **2–3 nghịch lý đắt giá nhất** (mỗi nghịch lý tương ứng với 1 điểm chạm Lưu/Share cao).
  2. Kiến trúc từng nghịch lý thành một gói kịch bản **`short_9x16` độc lập** (`1080x1920`, thời lượng `45–60s`, đúng 5 cảnh `SC01..SC05`).
  3. Viết lại hoàn toàn **`SC01` bằng câu Counter-Intuitive Hook $\le 18$ âm tiết** độc lập, đặt tốc độ `speed: 1.0` (`VietNarrator`, nhịp `4.2–4.4` âm tiết/s ở 30s đầu), bật phụ đề nhảy chữ theo `word_timestamps` (`subtitles: true`, `max_line_chars: 28`, chừa đáy `18%`).

---

## 3. Bảng Tự kiểm tra Trước khi Duyệt Kịch bản (Pre-flight Checklist)

- [ ] **Đóng gói CTR & Ngách chuẩn (`brief.json`):** `youtube_title <= 55` ký tự, `thumbnail_spec` (2–4 từ in hoa), đúng ngách Tư Duy Nghiên Cứu (không có từ khóa Excel/Slide/Na).
- [ ] **Chốt chặn mở đầu (`SC01`):** Câu đầu $\le 18$ âm tiết, 0 thẻ `[pause:...]`, Việt hóa 100% trong 60s đầu; hướng tới 8–9 ảnh toàn khung trong 12–12,5 giây đầu khi lời thoại hỗ trợ.
- [ ] **Đã tính toán số âm tiết & trần câu:** Mọi câu đơn $\le 25$ âm tiết, vế câu $\le 18$ âm tiết, tổng thẻ `[pause:...]` toàn video $\le 3$, $|\text{drift}| \le 0.30\text{s}$.
- [ ] **Ảnh toàn khung:** Nhân vật, đạo cụ và Sơ đồ Học thuật cùng trong bố cục; dùng `based_on` khi cần giữ liên tục bối cảnh.
- [ ] **Tách biệt `long_16x9` và `short_9x16` Spin-offs:** Mọi video đăng TikTok đều là kịch bản `short_9x16` 5 cảnh độc lập có phụ đề nhảy chữ.
