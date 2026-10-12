# Ma trận Ra Quyết định Kỹ thuật & Sản xuất (Decision Framework)

Tài liệu này cung cấp **Ma trận Ra Quyết định (Decision Matrix)** chuẩn hóa cho toàn bộ quy trình sản xuất video trong Video Pilot: từ khâu phân tích kênh tham chiếu, biên kịch, lựa chọn giọng đọc, ngắt nhịp đến dàn dựng hình ảnh và kỹ thuật dựng.

---

## 1. Ma trận Tổng quan: Khi nào Dùng Cái gì?

| Vấn đề cần quyết định | Lựa chọn A | Lựa chọn B | Tiêu chí quyết định (Khi nào dùng?) | Rủi ro nếu chọn sai |
|:---|:---|:---|:---|:---|
| **Chế độ sản xuất** | **Mode A** *(Structural Replication)* | **Mode B** *(Original Adaptation)* | Dùng **Mode A** khi chạy benchmark nội bộ, đo độ lệch timeline và kiểm thử động cơ kỹ thuật. Dùng **Mode B** khi sản xuất video mới ra kênh. | Chọn sai Mode A cho sản xuất công khai sẽ vi phạm bản quyền nội dung. |
| **Nhịp thay đổi hình ảnh** | **Tách Scene mới** *(Scene Cut)* | **Visual Beats** *(beats[] trong Scene)* | Dùng **Tách Scene** khi đổi hoàn toàn bối cảnh/địa điểm hoặc chuyển chương lớn ($D \ge 5\text{s}$). Dùng **Visual Beats** khi đổi đạo cụ, zoom/pan camera, phản ứng sticker ($D \le 3\text{s}$). | Cắt nhỏ Scene gây tích lũy đuôi $P_{\text{tail}} = 0.70\text{s}$, làm audio bị phình to (+35% đến +70%) và vỡ nhịp kịch bản. |
| **Dàn dựng Visual** | **Static Background Plate** | **Layered Motion** *(Plate + Stickers)* | Dùng **Static Plate** khi cảnh là biểu đồ toàn cảnh, bản đồ tĩnh, hoặc phong cảnh không nhân vật. Dùng **Layered Motion** khi có nhân vật que hành động, xuất hiện đồ vật hoặc tương tác. | Lạm dụng Static Plate gây hiện tượng "đơ hình AI" (Scene Hold Stagnation); lạm dụng Sticker không cần thiết gây chậm render. |
| **Giọng đọc tiếng Việt** | `vi-VN-NamMinhNeural` *(rate="+22%")* | `Adam` *(0.95x)* | Dùng `NamMinhNeural` cho video tài liệu 16:9, nhịp nhanh, thông tin dày đặc, benchmark. Dùng `Adam` cho câu chuyện tâm sự sâu lắng, video đơn cảnh hoặc thử nghiệm cảm xúc. | Dùng nhầm tốc độ khiến video bị lê thê (< 3.2 syl/s) hoặc dồn dập (> 4.5 syl/s). |
| **Giọng đọc tiếng Anh** | `reference-narrator` *(0.92x)* | `Alba MacKenna` *(0.92x)* | Dùng `reference-narrator` cho định dạng 9:16 giải thích từ vựng thương mại. Dùng `Alba MacKenna` khi kế thừa pipeline lịch sử v3. | Sai giọng clone làm mất tính nhất quán thương hiệu của kênh. |
| **Khoảng lặng âm thanh** | **Dramatic Pause** *(pause:900ms)* | **Engine Default Pauses** | Dùng `[pause:900ms]` trước điểm ngoặt bất ngờ, số liệu gây sốc hoặc câu hỏi tu từ. Dùng mặc định cho ngắt phẩy ($0.30\text{s}$) và ngắt đoạn ($0.70\text{s}$). | Lạm dụng dramatic pause làm loãng nhịp; thiếu dramatic pause gây cảm giác đọc như máy đếm nhịp. |
| **Phụ đề hiển thị** | **2 dòng cân bằng (Midpoint)** | **1 dòng ngắn** | Dùng **2 dòng** khi câu có 4–8 từ (ngắt giữa câu). Dùng **1 dòng** khi câu chỉ có 1–3 từ nhấn mạnh. | Để phụ đề tràn 3 dòng che mất hình vẽ hoặc va chạm giao diện. |

---

## 2. Chi tiết 7 Trục Quyết định Kỹ thuật

### 2.1. Trục 1: Chế độ Vận hành (Mode A vs Mode B)
- **Khi nào chọn Mode A (Structural Replication & Control Benchmark):**
  - Mục tiêu: Kiểm tra độ chính xác của timeline, đo độ lệch dead-air audio, benchmark năng lực tách lớp sticker Remotion và render Colab T4.
  - Invariant: Sử dụng cấu trúc phân cảnh đối chứng gốc. **Tuyệt đối lưu hành nội bộ** (`sys/runs/`), nghiêm cấm phát hành công khai vì lý do bản quyền.
- **Khi nào chọn Mode B (Original Adaptation & Production):**
  - Mục tiêu: Tạo ra một sản phẩm video độc lập, nguyên bản, sẵn sàng xuất bản ra công chúng.
  - Invariant: Giữ nguyên khung cấu trúc 5 phần (Hook $\rightarrow$ Reframe $\rightarrow$ Causal Evidence $\rightarrow$ Direct Contrast $\rightarrow$ Loop Payoff), nhưng **thay đổi 100% đề tài, nhân vật, lời dẫn, số liệu và hình minh họa**.

---

### 2.2. Trục 2: Cắt Phân cảnh (Scene Split) vs Nhịp Trực quan (Visual Beats)
- **Quy tắc vàng:** *Đơn vị Scene là ranh giới câu thoại và không gian; đơn vị Beat là ranh giới chú ý thị giác.*
- **Chọn Tách Scene khi:**
  1. Thay đổi hoàn toàn không gian môi trường (Ví dụ: từ phòng ngủ hiện đại chuyển sang thảo nguyên tiền sử).
  2. Kết thúc một luận điểm lớn (Chapter boundary).
  3. Thời lượng câu thoại tự nhiên $\ge 5.0\text{s}$.
- **Chọn Visual Beats (`beats[]`) khi:**
  1. Câu thoại dài 8–14s nhưng cần thay đổi thị giác mỗi 2–3s để giữ chân người xem.
  2. Bổ sung đạo cụ mới vào tay nhân vật que (Ví dụ: giáo săn, cuốc đất, đồng hồ cát).
  3. Thay đổi tiêu cự camera: `zoom_in` vào khuôn mặt nhân vật, `pan_left` sang biểu đồ số liệu.
  4. Hiệu ứng rung giật (`shake`) khi có tác động mạnh (chuông reo, sấm chớp).

---

### 2.3. Trục 3: Động cơ Tổng hợp Âm thanh & Giọng đọc
- **Bảng ma trận chọn Voice:**
  - **Mục tiêu Benchmark 16:9 / Tài liệu học thuật tiếng Việt:** Chọn `vi-VN-NamMinhNeural` tại tốc độ `+22%`. Tốc độ đạt chuẩn 4.0 âm tiết/giây, âm sắc rõ nét, phát âm từ ngữ khoa học chuẩn xác.
  - **Mục tiêu Tự sự / Kể chuyện cảm xúc tiếng Việt:** Chọn `Adam` tại tốc độ `0.95x` qua Colab OmniVoice.
  - **Mục tiêu Tiếng Anh 9:16 Shorts:** Chọn `reference-narrator` tại tốc độ `0.92x` (giọng clone chuẩn từ video mẫu Ink Explainer).
  - **Xử lý thuật ngữ song ngữ (Vietnamese narration có từ tiếng Anh):** Bọc từ tiếng Anh trong dấu ngoặc kép `""` để router kích hoạt `english_parts` qua `reference-narrator`, phần còn lại chạy qua voice tiếng Việt.

---

### 2.4. Trục 4: Dàn dựng Thị giác (Static Plate vs Layered Motion)
- **Chọn Static Plate khi:**
  - Cần hiển thị sơ đồ phân nhánh, bảng đối chiếu 2 cột dữ liệu, bản đồ khảo cổ học hoặc cảnh đại cảnh tĩnh.
  - Không có nhân vật chuyển động riêng lẻ.
- **Chọn Layered Motion (Background Plate + Sticker Layers) khi:**
  - Có nhân vật que đóng vai trò chủ thể hành động (thức dậy, chạy trốn, kéo cày, gục ngã).
  - Cần hiệu ứng vật lý Remotion Spring (`damping: 12`) để sticker nảy vào khung hình tự nhiên.
  - Cần áp dụng chuyển động sống động (*Organic Motion*): nhịp thở nhẹ (*idle breathing*), hoặc rung lắc vi mô (*jitter*).

---

### 2.5. Trục 5: Quản lý Khoảng lặng (Pauses & Cadence)
- **Công thức bắt buộc:**
  $$\text{Target Syllables} = \text{round}\Big((\text{Scene Duration} - P_{\text{tail}}) \times 4.0\Big)$$
- **Quy tắc gán Pause:**
  - Gán `[pause:900ms]` khi: Đang chuyển từ mệnh đề "sách vở nói..." sang "thực tế khai quật chứng minh...".
  - Giữ $P_{\text{tail}} = 0.70\text{s}$ cho tất cả Scene giữa chừng để người xem kịp ngấm thông tin trước khi sang cảnh mới.
  - Giữ $P_{\text{tail}} = 0.35\text{s}$ cho Scene kết thúc để video kết lại dứt khoát, không bị dead-air cuối clip.

---

### 2.6. Trục 6: Ma trận Biểu cảm Nhân vật (Character Expression & Pose)

| Trạng thái kịch bản | Biểu cảm khuôn mặt | Tư thế cơ thể (Stick Figure Pose) | Ứng dụng điển hình |
|:---|:---|:---|:---|
| **Báo thức / Kiệt sức** | Mắt nhắm nghiền gạch ngang (`- -`), miệng rũ sóng | Dáng ngồi bật dậy trên giường, hai vai buông thõng gù xuống | Mở đầu video hiện đại, áp lực công việc |
| **Nghi vấn / Hoài nghi** | Lông mày xếch, một mắt to một mắt nhỏ | Một tay chống cằm, đầu nghiêng 15 độ | Câu hỏi tu từ, lật lại định kiến sách giáo khoa |
| **Kinh ngạc / Phát hiện** | Mắt trợn tròn (`O O`), miệng chữ O | Hai tay giơ ngang ngực, thân hơi ngả về sau | Tiết lộ con số 17 giờ/tuần, phát hiện bộ xương |
| **Lao động cực nhọc** | Mắt nhắm nghiền nhăn nhó, giọt mồ hôi rơi | Dáng gập lưng kéo cày, hai tay nắm chặt dây kéo | Minh họa cái bẫy nông nghiệp sơ khai |
| **Thảnh thơi / Tự do** | Mắt cong hình vòng cung cười mỉm, miệng cười nhẹ | Dáng nằm ngả lưng trên bãi cỏ, hai tay gối sau đầu | Minh họa đời sống săn bắt hái lượm bên đống lửa |

---

### 2.7. Trục 7: Thiết kế Âm thanh & Micro-Foley
- **Khi nào chèn Foley SFX:**
  - Chỉ chèn khi kịch bản có **từ neo cụ thể (Semantic Anchor)**:
    - Từ *"chuông báo thức"* $\longrightarrow$ Kích hoạt `sfx_alarm_bell.wav` (0.0s – 1.2s, volume -12dB).
    - Từ *"trang sách giáo khoa"* $\longrightarrow$ Kích hoạt `sfx_page_turn.wav` (-15dB).
    - Từ *"đống lửa sưởi ấm"* $\longrightarrow$ Kích hoạt `sfx_fire_crackle.wav` loop (-24dB diegetic).
    - Từ *"đồng hồ tích tắc"* $\longrightarrow$ Kích hoạt `sfx_clock_tick.wav` (-18dB).
- **Quy tắc nhạc nền (BGM):**
  - Luôn ducking nhạc nền xuống **-20dB đến -24dB** khi có giọng đọc thoại.
  - Nâng nhẹ nhạc nền lên **-14dB** tại các khoảng nghỉ kịch tính (`[pause:900ms]`) hoặc đoạn kết payoff.

---

## 3. Bảng Tự kiểm tra Trước khi Duyệt Kịch bản (Pre-flight Checklist)

Trước khi chuyển kịch bản sang bước tạo âm thanh và hình ảnh, Agent kiểm tra 5 điều kiện tiên quyết:

- [ ] **Đã tính toán số âm tiết:** Tất cả các Scene đều tuân thủ công thức $\text{Syllables} = (D - P_{\text{tail}}) \times 4.0 \pm 1$ âm tiết.
- [ ] **Không có micro-scene audio:** Không có phân cảnh audio nào có thời lượng $D \le 2.5\text{s}$.
- [ ] **Đầy đủ Visual Beats:** Mỗi Scene dài $\ge 8\text{s}$ phải có ít nhất 2–3 mốc `beats[]` đổi góc quay hoặc đạo cụ.
- [ ] **Định dạng phụ đề an toàn (`sys/format_profiles.py`):** Tối đa 2 dòng/cue; không vượt quá `42` ký tự/dòng (`long_16x9`) hoặc `28` ký tự/dòng (`short_9x16`).
- [ ] **Vòng lặp kết thúc:** Câu kết bài ở Scene cuối cùng có liên kết ngữ nghĩa hoặc hình ảnh trở lại Scene mở đầu.
