# Quy chuẩn Phân tích Lời văn, Lời thoại, Giọng đọc, Tốc độ và Ngắt nhịp (Voice, Cadence & Pacing Playbook)

Tài liệu này chuẩn hóa toàn bộ phương pháp phân tích, công thức tính toán và quy chuẩn sản xuất về lời văn (*prose*), kịch bản thoại (*dialogue*), giọng đọc (*voice persona*), tốc độ (*pacing*), cách đọc (*delivery/prosody*), và ngắt nhịp (*pausing/breathing*) dựa trên kênh mẫu chuẩn mực **Ink Explainer (`@Inkexplainer96`)** và các thực nghiệm đo đạc độc lập trong Video Pilot.

Tài liệu được đóng gói để tái sử dụng độc lập cho cả **Mode A** (Structural Replication & Benchmark) và **Mode B** (Original Adaptation).

---

## 1. Lời văn & Văn phong Luận thuyết Kể chuyện (Story Prose & Rhetorical Style)

Kênh Ink Explainer đạt hàng chục triệu lượt xem nhờ phong cách kể chuyện **Conversational Essayist (Nhà luận thuyết trò chuyện)** — kết hợp sự gần gũi của một người bạn tâm sự với tính học thuật chặt chẽ của các công trình khảo cổ/nhân học.

### 1.1. Bốn nguyên tắc văn phong cốt lõi

1. **Không giáo điều, không thuyết giảng (Anti-academic Lecturing):**
   - Tuyệt đối tránh giọng văn đọc mục từ từ điển hay bài viết bách khoa toàn thư Wikipedia.
   - Mở đầu bằng trải nghiệm sinh hoạt quen thuộc của người hiện đại (tiếng chuông báo thức 6:00, mệt mỏi công sở, máy giặt, siêu thị đầy ắp đồ).
2. **Cấu trúc phát triển nhân quả (Causal Chain):**
   - Mọi luận điểm phải tuân theo chuỗi 5 mắt xích logic:
     $$\text{Hiện tượng đời thường} \longrightarrow \text{Định kiến sai lầm} \longrightarrow \text{Bằng chứng khoa học mới} \longrightarrow \text{Nghịch lý cơ chế} \longrightarrow \text{Đúc kết triết lý}$$
3. **Kỹ thuật tương phản trực diện (Direct Contrast):**
   - Luôn đặt hai thực tại đối lập cạnh nhau để tạo xung đột nhận thức:
     - *Hiện đại:* Máy móc tiện nghi nhưng làm việc kiệt sức 40–50h/tuần.
     - *Tiền sử:* Công cụ đá thô sơ nhưng chỉ cần lao động ~17h/tuần để tìm thức ăn.
     - *Hình ảnh:* Bộ xương nông dân thoái hóa, còi cọc đối chiếu với bộ xương người săn bắt hái lượm cao lớn, khỏe mạnh.
4. **Vòng lặp kết thúc có hậu (Payoff & Loop Closure):**
   - Câu kết không được lơ lửng; phải quay trở lại hình ảnh hoặc câu hỏi ở giây đầu tiên (tiếng chuông báo thức cơ giá \$12.99, vòng xoay công việc không hồi kết) để tạo sự trọn vẹn và dư âm suy ngẫm sâu sắc cho người xem.

---

## 2. Kịch bản Lời thoại (Narration & Dialogue Scripting)

### 2.1. Cấu trúc câu và mật độ thông tin
- **Tỷ lệ 70/30:**
  - **70%** thời lượng là lời dẫn mang tính gợi mở, dẫn dắt cảm xúc tự nhiên.
  - **30%** dành cho các con số và phát hiện đắt giá (ví dụ: *17 giờ/tuần*, *90.000 giờ làm việc trong đời*, *nghiên cứu 2014 của Polly Wiessner*).
- **Câu văn ngắn gọn, giàu hình ảnh thị giác:**
  - Mỗi câu thoại tương ứng với một hành động cụ thể trên màn hình (nhân vật que gù lưng, kéo cày, đồng hồ cát quay ngược).
- **Tiếng Việt chuẩn ngữ cảnh:**
  - Không dịch thô từng chữ (*word-for-word*) làm câu văn bị gượng gạo.
  - Không chèn từ đệm sáo rỗng (*như chúng ta đã biết*, *thưa các bạn*, *hôm nay tôi sẽ chia sẻ*).
  - Từng từ ngữ tiếng Việt là một âm tiết đơn nghĩa, nhắm đúng trọng tâm giải thích.

---

## 3. Giọng đọc & Hình tượng Âm thanh (Voice Profile & Vocal Persona)

### 3.1. Bản sắc giọng đọc (Vocal Persona)
- **Tông giọng:** Ấm áp, điềm đạm (*unhurried*), tò mò chân thành, có độ tin cậy khoa học cao.
- **Không kịch hóa quá đà:** Không phấn khích kiểu YouTuber thử thách/giải trí, không đao to búa lớn giật gân, và không khô cứng như AI đọc bản tin thời sự.

### 3.2. Cấu hình Voice Chuẩn Duy Nhất (SSOT)

| Voice | Profile | Speed | Engine | Mastering & Định dạng |
|:---|:---|:---:|:---|:---|
| `Adam` | `assets/voices/adam/profile.json` | `1.22x` | Colab `kjanh/KhanhTTS-OmniVoice` (`num_step=32`, `batch_size=4`) | `48kHz` Mono PCM16, EQ `+1.5dB @ 200Hz`, `-2.5dB @ 7000Hz`, `-14.0 LUFS`, `-1.5 dBTP` |

---

## 4. Tốc độ Đọc (Pacing & Delivery Speed)

Tốc độ đọc quyết định tính tự nhiên và năng lượng của video:

### 4.1. Định mức tốc độ theo ngôn ngữ
- **Tiếng Anh (Bản ngữ tham chiếu Ink Explainer):**
  - Tốc độ trung bình: **135 – 145 từ/phút (WPM)** ($\approx 2.25 – 2.40$ từ/giây).
- **Tiếng Việt (Chuẩn hóa Video Pilot Pacing Model):**
  - Tốc độ danh định mục tiêu: **4.0 âm tiết/giây**.
  - Dải vận hành an toàn: **3.8 – 4.2 âm tiết/giây**.
  - *Cảnh báo kỹ thuật:* $> 4.5$ âm tiết/giây gây cảm giác vội vã, dồn ép; $< 3.2$ âm tiết/giây gây cảm giác chậm chạp, buồn ngủ.

### 4.2. Biến thiên nhịp điệu theo cấu trúc câu chuyện (Dynamic Pacing)
1. **Phân đoạn Mở đầu (Hook & Empathy - 0–15% thời lượng):**
   - Tốc độ: ~145–150 wpm (Tiếng Anh) / ~4.2 âm tiết/s (Tiếng Việt).
   - Nhịp điệu dồn dập, nhanh, kích thích sự tò mò của người nghe.
2. **Phân đoạn Giải thích & Cơ chế (Causal Explanation - 15–80% thời lượng):**
   - Tốc độ: ~135–140 wpm (Tiếng Anh) / ~4.0 âm tiết/s (Tiếng Việt).
   - Nhịp điệu cân bằng, rõ ràng từng chi tiết để người nghe kịp tiếp thu sơ đồ và số liệu.
3. **Phân đoạn Đúc kết & Triết lý (Philosophical Payoff - 80–100% thời lượng):**
   - Tốc độ: ~120–125 wpm (Tiếng Anh) / ~3.6–3.8 âm tiết/s (Tiếng Việt).
   - Nhịp điệu chậm rãi, sâu lắng, tạo khoảng không gian cho người xem suy ngẫm.

---

## 5. Cách đọc & Ngữ điệu (Reading Delivery, Inflection & Prosody)

Khắc phục triệt để hiện tượng **"Metronomic Cadence" (nhịp máy đếm nhịp vô hồn của AI)**:
1. **Ngữ điệu câu hỏi tu từ (Rhetorical Questions):**
   - Lên giọng nhẹ ở cuối câu hỏi để khơi gợi sự tham gia tư duy của khán giả (*"Ai mới thực sự là người phải lao động nhiều giờ hơn?"*).
2. **Nhấn trọng âm ngữ nghĩa (Semantic Stress):**
   - Đặt lực nhấn vào các từ then chốt đối nghịch: *thực sự*, *ngược lại*, *mười bảy giờ*, *cái bẫy*, *hài cốt*.
3. **Hạ giọng ở câu khẳng định:**
   - Đóng các mệnh đề chân lý hoặc đúc kết bằng một ngữ điệu trầm và dứt khoát.

---

## 6. Ngắt câu, Khoảng lặng & Trừ bù Đuôi Động cơ (Pauses & Dead-Air Elimination)

### 6.1. Hằng số Âm học Đuôi Động cơ ($P_{\text{tail}}$)

Trong Video Pilot (`sys/adapters.py`), động cơ tổng hợp TTS tự động chèn thêm khoảng đệm im lặng vào đuôi mỗi tệp audio:
- **Cảnh thường (SC01–SC05):** $P_{\text{tail}} = 0.70\text{s}$ (`DEFAULT_PAUSE['para']`).
- **Cảnh kết thúc (SC06):** $P_{\text{tail}} = 0.35\text{s}$ (`DEFAULT_PAUSE['tail']`).
- **Dấu phẩy (minor pause):** $P_{\text{comma}} = 0.30\text{s}$ (`DEFAULT_PAUSE['minor']`).

### 6.2. Công thức Tính Âm tiết Mục tiêu Triệt tiêu Dead-Air

Để thời lượng audio thực tế khớp chính xác với thời lượng cảnh dự kiến trong biên độ dung sai khắt khe **$\pm 0.5\text{s}$**:

$$\text{Target Syllables} = \text{round}\Big((\text{Scene Duration} - P_{\text{tail}}) \times 4.0\Big)$$

> **Quy tắc trừ bù dấu phẩy:** Mỗi dấu phẩy chiếm khoảng $0.30\text{s} \times 4.0 \approx 1.2$ âm tiết. Khi kịch bản có nhiều dấu phẩy, chủ động giảm 1 âm tiết trên mỗi dấu phẩy.

### 6.3. Bảng Kiểm chứng Thực nghiệm (Độ lệch $\le 0.30\text{s}$, Tích lũy $-0.15\text{s}$)

| Phân cảnh | Thời lượng dự kiến | $P_{\text{tail}}$ | Thời lượng nói thực | Số âm tiết mục tiêu | Câu thoại tiếng Việt đã căn chỉnh | Số âm tiết viết | Thời lượng Audio tổng | Độ lệch (Drift) |
|:---:|:---:|:---:|:---:|:---:|:---|:---:|:---:|:---:|
| **SC01** | 12.0s | 0.70s | 11.30s | 45 | "Hãy nghĩ về một buổi sáng quen thuộc của bạn: tiếng chuông báo thức réo vang inh ỏi phá tan giấc ngủ, bạn thức dậy trong mệt mỏi, và ngay tối nay bạn lại nơm nớp lo sợ ngày mai sẽ tiếp tục lặp lại." | 45 | 11.95s | **-0.05s** |
| **SC02** | 12.0s | 0.70s | 11.30s | 45 | "Giờ đây, hãy thử quay ngược dòng thời gian về năm mươi ngàn năm trước. Liệu tổ tiên săn bắt hái lượm của chúng ta có thực sự phải trải qua một kiếp sống khốn khổ và mệt mỏi như chúng ta vẫn hằng tưởng tượng?" | 46 | 12.20s | **+0.20s** |
| **SC03** | 14.0s | 0.70s | 13.30s | 53 | "Các cuốn sách giáo khoa lịch sử từ trước đến nay vẫn thường miêu tả cuộc sống tiền sử như một chuỗi ngày triền miên chìm trong đói khát, hiểm nguy rình rập và cuộc chiến sinh tồn tàn khốc không có lấy một phút giây nào được thảnh thơi ngơi nghỉ." | 52 | 13.70s | **-0.30s** |
| **SC04** | 14.0s | 0.70s | 13.30s | 53 | "Thế nhưng, khi các nhà khảo cổ học tiến hành khai quật cẩn thận hàng loạt bộ hài cốt cổ xưa trên khắp các châu lục, những lớp trầm tích địa tầng đã hé lộ một bức tranh hoàn toàn trái ngược với những định kiến sai lầm bấy lâu nay của chúng ta." | 54 | 14.20s | **+0.20s** |
| **SC05** | 12.0s | 0.70s | 11.30s | 45 | "Thời hiện đại chúng ta tự hào sở hữu máy giặt tự động, xe hơi tiện nghi và siêu thị đầy ắp thức ăn — nhưng đã bao giờ bạn tự hỏi ai mới thực sự là người phải lao động vất vả nhiều giờ hơn?" | 45 | 11.95s | **-0.05s** |
| **SC06** | 11.0s | 0.35s | 10.65s | 43 | "Bạn kiệt sức gục ngã trước những núi hồ sơ giấy tờ dưới tiếng đồng hồ tích tắc, trong khi người tiền sử đang nằm thảnh thơi tận hưởng buổi hoàng hôn êm đềm bên đống lửa ấm áp của bộ tộc." | 42 | 10.85s | **-0.15s** |
| **TỔNG** | **75.0s** | — | **71.15s** | **284** | — | **284** | **74.85s** | **-0.15s** |

### 6.4. Khoảng ngắt kịch tính (Dramatic Pauses)
- Tại các bước chuyển ngoặt tư duy bất ngờ, chèn khoảng nghỉ chủ đích từ **0.8s đến 1.2s** (cú pháp chú thích kịch bản: `[pause:900ms]`).
- Ví dụ: *"Các cuốn sách nói rằng họ chết đói... [pause:900ms] nhưng các bộ hài cốt lại kể một câu chuyện hoàn toàn trái ngược."*
- Khoảng nghỉ này phải được bảo toàn trong kịch bản trước khi khóa neo (*anchors*) phụ đề và chuyển động hình ảnh.

---

## 7. Quy chuẩn Phụ đề An toàn & Đồng bộ Nhịp Trực quan (Safe Subtitles & Visual Beats)

### 7.1. Định dạng Phụ đề An toàn 2 dòng theo `sys/format_profiles.py`
Để chữ phụ đề không bị nhảy thành 3–4 dòng gây che khuất tranh minh họa hoặc va chạm vùng giao diện:
- **Giới hạn theo hồ sơ định dạng (`sys/format_profiles.py`):** Tối đa **2 dòng/cue**; hồ sơ ngang `long_16x9` tối đa **42 ký tự/dòng** (`84` ký tự/cue); hồ sơ dọc `short_9x16` tối đa **28 ký tự/dòng** (`54` ký tự/cue).
- **Cắt dòng cân bằng (Midpoint Wrapping):** Chia dòng tại điểm giữa số từ (`len(words) // 2`) khi câu dài hơn 3 từ.
- **Kẹp mốc thời gian không chồng lấn:** Luôn bảo đảm `end_sec <= next_start_sec`.

### 7.2. Nguyên tắc Fast-Cut ($D \le 2.5\text{s}$) & Visual Beats
- **Quy tắc cấm chia nhỏ Scene:** Tuyệt đối **KHÔNG cắt nhỏ các câu thoại liên tục thành các Scene ngắn ($D \le 2.5\text{s}$)** vì việc tích lũy các đuôi $P_{\text{tail}} = 0.70\text{s}$ sẽ làm tổng thời lượng audio bị phình to (+35% đến +70%) và xé vụn câu nói.
- **Tổ chức thành Visual Beats (`beats[]`):** Trong một câu thoại 10–12 giây của Scene cha, bố trí 3–4 nhịp hình ảnh xuất hiện so le (`offset: 0.0s`, `3.5s`, `7.2s`) với các hiệu ứng camera (`zoom_in`, `pan_left`, `ken_burns`) hoặc nảy sticker tương ứng theo từ neo thoại.

### 7.3. Thuật toán Khóa Hình Cấp Độ Câu Thoại — Cue-Window Allocation (`0.00s` Drift, Nhịp Cắt `1.5s–3.8s`)
- **Cấm giãn tỷ lệ thô cấp độ Scene (`Scene-Level Linear Scaling`):** Không được chỉ neo mốc đầu của 30 Scene lớn rồi chia đều hoặc cắt ngọn `max_hold` cho cả Scene, vì phần thời gian dư sẽ đẩy các bức ảnh sau trượt khỏi câu thoại từ `3s–27s`.
- **Khóa cửa sổ từng câu thoại (`Cue-Window Allocation`):**
  1. Mỗi câu thoại `i` trong `spoken_cues.json` định nghĩa một cửa sổ thời gian tuyệt đối `[cue_i.start, cue_{i+1}.start)` (câu cuối của Scene kết thúc tại `scene.end`).
  2. Ánh xạ tường minh `1:1` từng câu thoại tiếng Việt với danh sách các shot đúng ngữ nghĩa trong `cue_shot_mapping_8ch.json` (tự động đảo lại thứ tự shot nếu câu tiếng Việt biên tập đảo vế so với kịch bản gốc).
  3. Phân bổ thời lượng các shot hoàn toàn bên trong cửa sổ `[cue_i.start, cue_{i+1}.start)` (`rebuild_option_b_templates.py`), đảm bảo:
     - Shot đầu tiên của mọi câu thoại bắt đầu **chính xác tại `cue_i.start` (sai số `0.000s`)**.
     - Mọi bức ảnh đều có thời lượng hiển thị nằm trong ngưỡng **`0.83s – 3.80s` (`<= 4.0s`)**, không bao giờ giữ tĩnh một hình quá 4 giây.
