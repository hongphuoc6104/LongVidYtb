---
name: vp-scriptwriting
description: "Author and transform explainer video scripts into natural conversational spoken storytelling with counter-intuitive 3-second hooks and calibrated acoustic cadence."
---

# VP Scriptwriting — Conversational Essayist, Truth-Slap Hook & Voice Cadence Skill

`vp-scriptwriting` là bộ kỹ năng và quy chuẩn cốt lõi dùng để sáng tác, thẩm định và chuyển hóa kịch bản video trong Video Pilot (cho cả `long_16x9` và `short_9x16`). Bộ kỹ năng này xóa bỏ triệt để văn phong bách khoa thư hàn lâm ("văn viết khô khan") và lối dẫn nhập rề rà, thay thế bằng **Counter-Intuitive / Truth-Slap Hook (Cú tát sự thật trong 2.5 giây đầu)** kết hợp phong cách kể chuyện sắc bén, ấm áp của một **Conversational Essayist (Nhà luận thuyết trò chuyện)**.

---

## 1. Sứ Mệnh, Bản Sắc Giọng Kể & Cú Tát Sự Thật Mở Màn (Core Mission & Opening Hook)

- **Hình tượng (The Voice Archetype):** **Conversational Essayist (Nhà luận thuyết trò chuyện)** — điềm đạm, ấm áp, sắc sảo, đạt **Phép thử chiếc bàn cà phê (The Coffee Table Test)** và giữ vững vị thế ngách **"Giải Mã Tư Duy Nghiên Cứu, Bản Chất Tri Thức & Luật Ngầm Học Thuật"**.
- **Counter-Intuitive / Truth-Slap Hook (Cú tát sự thật trong 2.5 giây đầu — Giải quyết Bẫy 1):**
  - Câu đầu tiên của `SC01` bắt buộc **$\le 18$ âm tiết** (`OPENING_HOOK_TOO_LONG`), đánh thẳng vào một nghịch lý phản trực giác hoặc lật tẩy ảo giác học thuật của người xem (ví dụ: *"Đọc lại giáo trình năm lần không giúp bạn hiểu bài, nó chỉ ru ngủ não bạn."* — 17 âm tiết; hoặc *"Bài báo khoa học chuẩn quốc tế không bao giờ bắt đầu bằng việc mở Word."* — 15 âm tiết).
  - **Tuyệt đối cấm** mở đầu bằng lời chào (*"Xin chào"*), giới thiệu đề tài (*"Hôm nay chúng ta..."*), câu dẫn nhập chậm (*"Hãy nghĩ về..."*, *"Hãy hình dung..."*, *"Hãy tưởng tượng..."*, *"Giờ đây, hãy thử..."*, *"Để tìm câu trả lời..."*), định nghĩa từ điển hoặc danh sách kiểu Wikipedia.
- **Zero Pause in First 15 Seconds (`SC01` — `OPENING_SCENE_PAUSE_FORBIDDEN`):**
  - **Nghiêm cấm** chèn bất kỳ thẻ `[pause:...]` nào trong cảnh mở đầu `SC01` (15 giây đầu tiên). Mọi khoảng khựng ở 15 giây đầu đều làm đứt đà cuốn hút và khiến khán giả lạnh (0 sub) lướt qua ngay lập tức.
- **100% Factual Fidelity & Zero Academic Name-Drop Bloat:** Giữ nguyên 100% số liệu cốt lõi và từ vựng bắt buộc, nhưng cất toàn bộ danh xưng rườm rà (`Giáo sư A tại Đại học B`, năm xuất bản, mã `DOI`) vào `brief.json` (`sources[].reference`) — không bao giờ đọc danh xưng học thuật dài dòng trong `narration`.

---

## 2. Khung Kể Chuyện 5 Phần & Chuyển Cảnh Một Chiều

1. **Cấu trúc 5 hồi nhân quả** (Chi tiết tại [Khung Kể Chuyện Conversational Essayist](references/conversational-essayist-framework.md)):
   - **Hồi 1 — Counter-Intuitive Hook & Empathy (0–15%):** Cú tát sự thật $\le 18$ âm tiết + bối cảnh Việt hóa sát sườn, **0 thẻ pause**, nhịp đọc cuốn **`4.2 – 4.4` âm tiết/s** (`1.26x` cho `short_9x16`).
   - **Hồi 2 — Reframe & Dilemma (15–35%):** Lật ngược định kiến số đông bằng nghịch lý khoa học + tối đa 1 thẻ `[pause:900ms]` trước điểm bùng nổ.
   - **Hồi 3 — Causal Evidence 70/30 (35–65%):** 70% dẫn dắt sơ đồ trực quan (Academic Pyramid / Flowchart `Question → Gap → Method → Evidence`) $\leftrightarrow$ 30% dữ liệu thực nghiệm (~`4.0` âm tiết/s).
   - **Hồi 4 — Direct Contrast (65–85%):** Đặt hai thực tại đối lập cạnh nhau (Học vẹt / Mở Word gõ ngay vs. Tư duy gốc rễ Q1).
   - **Hồi 5 — Loop Closure & Payoff (85–100%):** Quay lại hình ảnh mở đầu, hạ nhịp sâu lắng (~`3.6–3.8` âm tiết/s).
2. **Luân phiên 5 thế chuyển cảnh động (Rotating Transition Grammar):**
   - Tuyệt đối cấm các câu dẫn sáo rỗng (*"Nhưng rồi..."*, *"Bước sang..."*, *"Hãy cùng bước vào..."*, *"Hãy nhìn lại..."*, *"Nhưng câu chuyện chưa dừng lại ở đó..."*).
   - Bắt buộc luân chuyển: (1) **Sensory Jump**; (2) **Paradox Pivot**; (3) **Perspective Shift**; (4) **Micro-Moment Focus**; (5) **Causal Hook**.
3. **Phân vùng lịch sử một chiều (Strict Forward Chronology):**
   - Khi đã bước sang thời kỳ mới, **nghiêm cấm** kéo ngược bối cảnh về thời kỳ cũ. Trong 60 giây đầu (`CH01` / `SC01–SC02`), bắt buộc giữ bối cảnh đời sống Việt Nam hiện đại trước khi dẫn sang các bối cảnh quốc tế/lịch sử từ Chương 3 trở đi.

---

## 3. Công Thức Âm Học Triệt Tiêu Dead-Air & Pacing Động Học

### 3.1. Hằng số âm học đuôi động cơ ($P_{\text{tail}}$)
Trong hệ thống Video Pilot (`sys/adapters.py`), động cơ tổng hợp TTS tự động chèn khoảng đệm im lặng vào đuôi mỗi tệp audio:
- **Cảnh thường / trung gian:** $P_{\text{tail}} = 0.70\text{s}$ (`DEFAULT_PAUSE['para']`).
- **Cảnh kết thúc:** $P_{\text{tail}} = 0.35\text{s}$ (`DEFAULT_PAUSE['tail']`).
- **Dấu phẩy (ngắt hơi nhỏ):** $P_{\text{comma}} = 0.30\text{s}$ (`DEFAULT_PAUSE['minor']`).

### 3.2. Công thức tính số âm tiết mục tiêu (Target Syllables)
Để thời lượng audio thực tế khớp chính xác với dòng thời gian cảnh trong dung sai khắt khe **$\le 0.3\text{s}$**:

$$\text{Target Syllables} = \text{round}\Big((\text{Scene Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$$

- **Quy tắc Tier-3 Dramatic Pause (`[pause:800ms]` / `[pause:900ms]`):**
  - **Cấm tuyệt đối ở `SC01` (15 giây đầu):** Vi phạm sẽ kích hoạt cờ `OPENING_SCENE_PAUSE_FORBIDDEN`.
  - **Giới hạn toàn video:** Tối đa **1–3 lần** trong toàn bộ video (ngưỡng chặn cứng `DEFAULT_MAX_DRAMATIC_PAUSES = 4`, cảnh báo `EXCESSIVE_DRAMATIC_PAUSES` — `ERR-20261014-01`), chỉ đặt tại bước ngoặt lật ngược định kiến từ `SC02` trở đi.
- **Trần độ dài câu Mở đầu & Câu Thường (`OPENING_HOOK_TOO_LONG`, `SENTENCE_TOO_LONG` & `BREATHLESS_CLAUSE`):**
  - Câu đầu tiên của `SC01` phải **$\le 18$ âm tiết**.
  - Mọi câu thoại đơn trong kịch bản phải nằm trong khoảng **15–25 âm tiết** (trần tối đa $\le 25$), không có vế câu không dấu phẩy nào vượt quá **18 âm tiết**.
- **Chống vụn nhịp câu ngắn (`SENTENCE_FRAGMENTATION`):** Không đặt quá 2 câu siêu ngắn (`< 6` âm tiết) hoặc quá 4 câu trong một cảnh trung bình.
- **Giao thức Dữ kiện Văn nói (`Conversational Spoken Fact Protocol` — `ERR-20261011-03`):** Toàn bộ dữ kiện trong `brief.json` (`sources[].facts` và `required_points`) phải $\le 20$ âm tiết (ngưỡng cứng $22$), không chứa `DOI`, `ISBN`, `et al.`, `%`, `/`.

### 3.3. Dải tốc độ động học 3 giai đoạn (Dynamic Pacing)
- **Giai đoạn Mở đầu — 30 giây đầu (Truth-Slap Hook & Empathy):** **`4.2 – 4.4` âm tiết/s** (Tiếng Việt, tương đương `speed: 1.26x` cho `short_9x16` và nhịp cắt nhanh cho `long_16x9`) / ~150–155 wpm (Tiếng Anh) để tạo nhịp cuốn tức thì từ giây `0:00`.
- **Giai đoạn Cơ chế (Causal Explanation):** ~`4.0` âm tiết/s (Tiếng Việt, `speed: 1.22x`) / ~135–140 wpm (Tiếng Anh).
- **Giai đoạn Đúc kết (Philosophical Payoff):** ~`3.6–3.8` âm tiết/s (Tiếng Việt) / ~120–125 wpm (Tiếng Anh).
- **Ngưỡng cảnh báo kỹ thuật:** $> 4.5$ âm tiết/giây (quá vội, dồn ép); $< 3.2$ âm tiết/giây (chậm chạp, ru ngủ).

Chi tiết xem tại: [Quy chuẩn Giọng đọc, Tốc độ và Ngắt nhịp](../vp-channel-patterns/references/voice-cadence-pacing.md).

---

## 4. Đồng Bộ Lời Thoại Với Full-frame Visual Beats

Ưu tiên cụm từ cụ thể, đồ vật và hành động nhìn thấy được để visual planner có thể gắn từng beat vào đúng lời thoại. Giữ nhịp nói tự nhiên; không ép một vật thể vào mọi vế câu và không dùng số lượng beat để thay cho kiểm tra âm học.

1. **Cold open (`0:00–0:12.5`):** Khi lời thoại có đủ thay đổi hình ảnh, hướng tới 8–9 ảnh toàn khung, khoảng 4 ảnh trong 5 giây đầu. Neo mỗi ảnh vào đúng cụm từ hoặc hành động; xác nhận cut theo WAV.
2. **Thân bài (`sau 0:15`):** Dùng *Cue-Window Allocation* để giữ mỗi ảnh khoảng **`0.83s–3.80s`**, với anchor ngữ nghĩa và chuyển cảnh phù hợp.

---

## 5. Quy Trình Sản Xuất & Công Cụ Kiểm Tra Tự Động

```bash
# Kiểm tra toàn diện âm học, cấm pause ở SC01, trần câu mở đầu <= 18 âm tiết, trần câu <= 25 âm tiết
python3 sys/tools/script_cadence_checker.py path/to/content.json \
  --forbid-opening-pause \
  --max-opening-hook-syllables 18 \
  --max-sentence-syllables 25 \
  --max-clause-syllables 18 \
  --max-dramatic-pauses 4 \
  --strict

# Kiểm định tính đa dạng kịch bản, cấm mẫu câu "Hãy nghĩ về..." và chống lặp cấu trúc
python3 sys/tools/script_diversity_linter.py path/to/content.json
```

---

## 6. Danh Mục Tài Liệu Tham Khảo

- [Khung Kể Chuyện Conversational Essayist](references/conversational-essayist-framework.md)
- [Sổ Tay Lời Dẫn Văn Nói Tiếng Việt](references/spoken-narration-guide.md)
- [Quy Chuẩn Giọng Đọc, Tốc Độ & Ngắt Nhịp](../vp-channel-patterns/references/voice-cadence-pacing.md)
- [Chỉ Dẫn Kịch Bản Sản Xuất](../vp-production/references/script.md)
- [Chỉ Dẫn Âm Thanh Sản Xuất](../vp-production/references/audio.md)

## Anti-manual narrative gate

Follow [Full-frame quality contracts](../vp-full-frame-quality/SKILL.md) for new full-frame jobs. Spend the first 80–85% developing the paradox, evidence and causal explanation; use the final 15–20% for practice. Do not repeat the same operation pair in more than three scenes. Vietnamese Adam defaults to `1.22` for long videos; retain `1.26` for short spin-offs. Sentence chunks and acoustic checks govern delivery; speed alone does not certify pacing.
