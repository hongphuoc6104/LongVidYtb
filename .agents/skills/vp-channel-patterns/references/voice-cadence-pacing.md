# Quy chuẩn Phân tích Lời văn, Lời thoại, Giọng đọc, Tốc độ và Ngắt nhịp (Voice, Cadence & Pacing Playbook)

Tài liệu này chuẩn hóa toàn bộ phương pháp phân tích, công thức tính toán và quy chuẩn sản xuất về lời văn (*prose*), kịch bản thoại (*dialogue*), giọng đọc (*voice persona*), tốc độ (*pacing*), cách đọc (*delivery/prosody*), và ngắt nhịp (*pausing/breathing*) dựa trên kênh mẫu chuẩn mực **Ink Explainer (`@Inkexplainer96`)**, dữ liệu thực nghiệm Top 12 Thịnh Hành và các phép đo âm học độc lập trong Video Pilot.

Tài liệu được đóng gói để tái sử dụng độc lập cho cả **Mode A** (Structural Replication & Benchmark) và **Mode B** (Original Adaptation trên cả `long_16x9` lẫn `short_9x16`).

---

## 1. Lời văn & Văn phong Luận thuyết Kể chuyện (Story Prose & Rhetorical Style)

Phong cách kể chuyện **Conversational Essayist (Nhà luận thuyết trò chuyện)** kết hợp sự gần gũi, sắc sảo của một người đàn anh đi trước với tính học thuật chặt chẽ của các công trình nghiên cứu chuẩn quốc tế (Q1).

### 1.1. Bốn nguyên tắc văn phong cốt lõi

1. **Mở màn bằng Cú Tát Sự Thật (`Counter-Intuitive / Truth-Slap Hook <= 18 âm tiết`):**
   - Tuyệt đối tránh giọng văn đọc mục từ từ điển hoặc mở bài chậm chạp kiểu *"Hãy nghĩ về..."*, *"Hãy tưởng tượng..."*, *"Giờ đây, hãy thử..."*.
   - Câu đầu tiên của `SC01` phải $\le 18$ âm tiết, đi thẳng vào nghịch lý nhận thức gắn với trải nghiệm thực tế tại Việt Nam (đọc lại giáo trình 5 lần, mở Word gõ ngay khóa luận, 120 giây bước vào phòng bảo vệ, hoặc tiếng chuông báo thức 6:00 sáng đòi nợ thời gian).
2. **Cấu trúc phát triển nhân quả (Causal Chain):**
   - Mọi luận điểm phải tuân theo chuỗi 5 mắt xích logic:
     $$\text{Cú tát sự thật \& Trải nghiệm VN} \longrightarrow \text{Định kiến sai lầm} \longrightarrow \text{Bằng chứng \& Sơ đồ Q1} \longrightarrow \text{Tương phản trực diện 1/3} \longrightarrow \text{Đúc kết \& Khép vòng lặp}$$
3. **Kỹ thuật tương phản trực diện (Direct Contrast):**
   - Luôn đặt hai thực tại hoặc hai phương pháp đối lập cạnh nhau để tạo xung đột nhận thức:
     - *Học thuật:* Học vẹt / Mở Word gõ ngay từ trang 1 $\longleftrightarrow$ Tư duy gốc rễ Q1 / Đi theo chuỗi `Question → Gap → Method → Evidence → Paper`.
     - *Tiến hóa:* Máy móc tiện nghi nhưng làm việc kiệt sức 40–50h/tuần $\longleftrightarrow$ Công cụ đá thô sơ nhưng chỉ lao động ~17h/tuần.
4. **Vòng lặp kết thúc có hậu (Payoff & Loop Closure):**
   - Câu kết không được lơ lửng; phải quay trở lại hình ảnh hoặc câu hỏi ở giây đầu tiên để tạo sự trọn vẹn và thúc đẩy người xem bấm **Lưu (Bookmark)**.

---

## 2. Kịch bản Lời thoại (Narration & Dialogue Scripting)

### 2.1. Cấu trúc câu và mật độ thông tin
- **Tỷ lệ 70/30:**
  - **70%** thời lượng là lời dẫn giải phẫu cơ chế gắn với sơ đồ trực quan (*Academic Pyramid*, *Research Gap Matrix*, *Flowchart*).
  - **30%** dành cho các con số và dữ kiện khoa học văn nói đắt giá ($\le 20$ âm tiết, lưu danh xưng giáo sư/đại học/DOI trong `brief.json`).
- **Trần độ dài câu & mệnh đề:**
  - Câu đầu tiên của `SC01`: **$\le 18$ âm tiết** (`OPENING_HOOK_TOO_LONG`).
  - Mọi câu đơn trong kịch bản: **15–25 âm tiết** (trần cứng $\le 25$ — `SENTENCE_TOO_LONG`).
  - Mọi vế câu không dấu phẩy: **6–14 âm tiết** (trần cứng $\le 18$ — `BREATHLESS_CLAUSE`).
- **Tiếng Việt chuẩn ngữ cảnh & Việt hóa 60s đầu:**
  - Không dịch thô từng chữ (*word-for-word*) và không đưa địa danh cổ đại ngoại lai (*Sumer, Edubba, Phổ, Kalahari*) vào 60 giây đầu tiên.

---

## 3. Giọng đọc & Hình tượng Âm thanh (Voice Profile & Vocal Persona)

### 3.1. Bản sắc giọng đọc (Vocal Persona)
- **Tông giọng:** Ấm áp, điềm đạm, sắc bén, có độ tin cậy học thuật cao.
- **Điều biến sắc thái (`tone`):** Hỗ trợ `narrative_warm` (mặc định `1.00x`), `analytical_crisp` (`1.02x` khi bóc tách sơ đồ/số liệu), và `reflective_slow` (`0.92x` khi đúc kết triết lý cuối bài).

### 3.2. Cấu hình Voice Chuẩn Duy Nhất (SSOT)

| Voice | Profile | Speed (`long_16x9` / `short_9x16`) | Engine | Mastering & Định dạng |
|:---|:---|:---:|:---|:---|
| `Adam` | `assets/voices/adam/profile.json` | `1.22x` (`16:9`) / `1.26x` (`9:16`) | Colab `kjanh/KhanhTTS-OmniVoice` (`num_step=32`, `batch_size=4`) | `48kHz` Mono PCM16, EQ `+1.5dB @ 200Hz`, `-2.5dB @ 7000Hz`, `-14.0 LUFS`, `-1.5 dBTP` |

---

## 4. Tốc độ Đọc (Pacing & Delivery Speed)

### 4.1. Định mức tốc độ theo ngôn ngữ
- **Tiếng Anh (Bản ngữ tham chiếu):** Trung bình **135 – 145 WPM** ($\approx 2.25 – 2.40$ từ/giây).
- **Tiếng Việt (Chuẩn hóa Video Pilot Pacing Model):**
  - Tốc độ danh định mục tiêu: **4.0 âm tiết/giây**.
  - Dải vận hành an toàn: **3.8 – 4.4 âm tiết/giây**.
  - *Cảnh báo kỹ thuật:* $> 4.5$ âm tiết/giây gây cảm giác vội vã, dồn ép; $< 3.2$ âm tiết/giây gây cảm giác chậm chạp, buồn ngủ.

### 4.2. Biến thiên nhịp điệu theo cấu trúc câu chuyện (Dynamic Pacing)
1. **Phân đoạn Mở đầu — 30 giây đầu (Truth-Slap Hook & Empathy - 0–15% thời lượng):**
   - Tốc độ: **`4.2 – 4.4` âm tiết/s** (Tiếng Việt, tương đương `speed: 1.26x` cho video ngắn `short_9x16`) / ~150–155 wpm (Tiếng Anh).
   - **Zero Pause in `SC01`:** Tuyệt đối không chèn `[pause:...]` trong 15 giây đầu tiên để tạo nhịp cuốn tức thì từ giây `0:00`.
2. **Phân đoạn Giải thích & Cơ chế (Causal Explanation - 15–80% thời lượng):**
   - Tốc độ: ~`4.0` âm tiết/s (Tiếng Việt, `speed: 1.22x`) / ~135–140 wpm (Tiếng Anh).
   - Nhịp điệu cân bằng, rõ ràng từng chi tiết để người nghe kịp tiếp thu sơ đồ học thuật và số liệu.
3. **Phân đoạn Đúc kết & Triết lý (Philosophical Payoff - 80–100% thời lượng):**
   - Tốc độ: ~`3.6–3.8` âm tiết/s (Tiếng Việt) / ~120–125 wpm (Tiếng Anh).
   - Nhịp điệu chậm rãi, sâu lắng, tạo khoảng không gian cho người xem suy ngẫm và bấm Lưu video.

---

## 5. Cách đọc & Ngữ điệu (Reading Delivery, Inflection & Prosody)

Khắc phục triệt để hiện tượng **"Metronomic Cadence" (nhịp máy đếm nhịp vô hồn của AI)**:
1. **Độ lệch chuẩn độ dài câu (`stddev_syllables >= 1.8`):** Xen kẽ các câu ngắn đanh thép (4–8 chữ) với câu phân tích nhân quả (15–22 chữ) để vượt qua `check_sentence_rhythm_variance()` trong `script_diversity_linter.py`.
2. **Nhấn trọng âm ngữ nghĩa (Semantic Stress):** Đặt lực nhấn vào các từ then chốt đối nghịch: *ảo giác*, *ngược lại*, *khoảng trống*, *bản chất*, *hai phút đầu*.

---

## 6. Ngắt câu, Khoảng lặng & Trừ bù Đuôi Động cơ (Pauses & Dead-Air Elimination)

### 6.1. Hằng số Âm học Đuôi Động cơ ($P_{\text{tail}}$)
- **Cảnh thường (SC01–SC05):** $P_{\text{tail}} = 0.70\text{s}$ (`DEFAULT_PAUSE['para']`).
- **Cảnh kết thúc (SC06):** $P_{\text{tail}} = 0.35\text{s}$ (`DEFAULT_PAUSE['tail']`).
- **Dấu phẩy (minor pause):** $P_{\text{comma}} = 0.30\text{s}$ (`DEFAULT_PAUSE['minor']`).

### 6.2. Công thức Tính Âm tiết Mục tiêu Triệt tiêu Dead-Air

$$\text{Target Syllables} = \text{round}\Big((\text{Scene Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$$

### 6.3. Bảng Kiểm chứng Thực nghiệm (Độ lệch $\le 0.30\text{s}$, Tích lũy $-0.15\text{s}$, 0 Mẫu Câu Bị Cấm)

| Phân cảnh | Thời lượng dự kiến | $P_{\text{tail}}$ | Thời lượng nói thực | Số âm tiết mục tiêu | Câu thoại tiếng Việt đã căn chỉnh (Chuẩn Truth-Slap Hook, 0 mẫu câu cấm) | Số âm tiết viết | Thời lượng Audio tổng | Độ lệch (Drift) |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---:|:---:|
| **SC01** | 12.0s | 0.70s | 11.30s | 45 | "Chuông báo thức sáu giờ sáng thực chất là tờ hóa đơn đòi nợ thời gian của bạn. Tiếng chuông réo vang inh ỏi phá tan giấc ngủ ngon. Bạn thức dậy mệt mỏi, và tối nay lại nơm nớp lo ngày mai lặp lại." | 45 | 11.95s | **-0.05s** |
| **SC02** | 12.0s | 0.70s | 11.30s | 45 | "Quay ngược dòng thời gian về năm mươi ngàn năm trước, một nghịch lý lớn chợt hiện ra. Tổ tiên săn bắt hái lượm nơi hoang dã đã sống ra sao? Liệu họ có thực sự sống kiếp khốn khổ, mệt mỏi như ta lầm tưởng?" | 46 | 12.20s | **+0.20s** |
| **SC03** | 14.0s | 0.70s | 13.30s | 53 | "Các cuốn sách giáo khoa lịch sử từ trước đến nay vẫn thường miêu tả cuộc sống tiền sử như một chuỗi ngày triền miên chìm trong đói khát, hiểm nguy rình rập và cuộc chiến sinh tồn tàn khốc không có lấy một phút giây nào được thảnh thơi ngơi nghỉ." | 52 | 13.70s | **-0.30s** |
| **SC04** | 14.0s | 0.70s | 13.30s | 53 | "Thế nhưng, khi các nhà khảo cổ học tiến hành khai quật cẩn thận hàng loạt bộ hài cốt cổ xưa trên khắp các châu lục, những lớp trầm tích địa tầng đã hé lộ một bức tranh hoàn toàn trái ngược với những định kiến sai lầm bấy lâu nay của chúng ta." | 54 | 14.20s | **+0.20s** |
| **SC05** | 12.0s | 0.70s | 11.30s | 45 | "Thời hiện đại chúng ta tự hào sở hữu máy giặt tự động, xe hơi tiện nghi và siêu thị đầy ắp thức ăn — nhưng đã bao giờ bạn tự hỏi ai mới thực sự là người phải lao động vất vả nhiều giờ hơn?" | 45 | 11.95s | **-0.05s** |
| **SC06** | 11.0s | 0.35s | 10.65s | 43 | "Bạn kiệt sức gục ngã trước những núi hồ sơ giấy tờ dưới tiếng đồng hồ tích tắc, trong khi người tiền sử đang nằm thảnh thơi tận hưởng buổi hoàng hôn êm đềm bên đống lửa ấm áp của bộ tộc." | 42 | 10.85s | **-0.15s** |
| **TỔNG** | **75.0s** | — | **71.15s** | **284** | — | **284** | **74.85s** | **-0.15s** |

### 6.4. Khoảng ngắt kịch tính (Tier-3 Dramatic Pauses & Zero Pause in `SC01`)
- **Cấm tuyệt đối trong `SC01` (15 giây đầu tiên):** Mọi thẻ `[pause:...]` trong `SC01` đều bị chặn bởi `OPENING_SCENE_PAUSE_FORBIDDEN`.
- **Giới hạn 1–3 lần toàn video (`DEFAULT_MAX_DRAMATIC_PAUSES = 4`):** Chỉ chèn `[pause:800ms]` hoặc `[pause:900ms]` tại các bước ngoặt tư duy bất ngờ từ `SC02` trở đi.

---

## 7. Quy chuẩn Phụ đề An toàn & Đồng bộ Nhịp Trực quan 2 Vùng (Safe Subtitles & Dual-Zone Visual Beats)

### 7.1. Định dạng Phụ đề An toàn 2 dòng theo `sys/format_profiles.py`
- **Giới hạn theo hồ sơ định dạng (`sys/format_profiles.py`):** Tối đa **2 dòng/cue**; hồ sơ ngang `long_16x9` tối đa **42 ký tự/dòng** (`84` ký tự/cue); hồ sơ dọc `short_9x16` tối đa **28 ký tự/dòng** (`54` ký tự/cue) căn chỉnh theo năng lượng âm học `word_timestamps`.

### 7.2. Thuật toán Khóa Hình Cấp Độ Câu Thoại & Vùng Nguy Hiểm 15s Đầu
1. **Cold open (`0:00–0:12.5`):** Khi lời thoại hỗ trợ, hướng tới 8–9 ảnh toàn khung và khoảng 4 ảnh trong 5 giây đầu; neo cut vào cụm từ cụ thể và kiểm tra theo WAV.
2. **Vùng Thân Bài (`sau 0:15` / `SC03+`):** Phân bổ thời lượng theo *Cue-Window Allocation* (`0.000s` drift tại mọi `cue_i.start`), giữ mọi bức ảnh trong ngưỡng **`0.83s – 3.80s`**.
