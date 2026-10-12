---
name: vp-scriptwriting
description: "Author and transform explainer video scripts into natural conversational spoken storytelling."
---

# VP Scriptwriting — Conversational Essayist & Voice Cadence Skill

`vp-scriptwriting` là bộ kỹ năng và quy chuẩn cốt lõi dùng để sáng tác, thẩm định và chuyển hóa kịch bản video trong Video Pilot. Bộ kỹ năng này xóa bỏ triệt để văn phong bách khoa thư hàn lâm ("văn viết khô khan"), thay thế bằng phong cách kể chuyện tự nhiên, cuốn hút của một **Conversational Essayist (Nhà luận thuyết trò chuyện)**, bảo đảm người nghe có cảm giác như một người bạn tri kỷ uyên bác đang tâm sự và cùng họ khám phá những chân trời mới.

---

## 1. Sứ Mệnh & Bản Sắc Giọng Kể (Core Mission & Archetype)

- **Hình tượng (The Voice Archetype):** **Conversational Essayist (Nhà luận thuyết trò chuyện)** — điềm đạm, ấm áp, tò mò chân thành, đạt **Phép thử chiếc bàn cà phê (The Coffee Table Test)**.
- **Nguyên tắc "4 Không":** (1) Không giáo điều/định nghĩa từ điển; (2) Không liệt kê kiểu Wikipedia; (3) Không từ đệm sáo rỗng (*"Như chúng ta đã biết"*, *"Thưa quý vị"*); (4) Không câu bị động gượng gạo.
- **Bất biến 100% về sự thật (100% Factual & Vocabulary Fidelity):** Giữ nguyên 100% số liệu, tên nhà khoa học, địa danh và thuật ngữ trọng tâm của brief.

---

## 2. Khung Kể Chuyện 5 Phần & Chuyển Cảnh Một Chiều

1. **Cấu trúc 5 hồi nhân quả** (Chi tiết tại [Khung Kể Chuyện Conversational Essayist](references/conversational-essayist-framework.md)):
   - **Hồi 1 — Hook & Empathy (0–15%):** Chạm ngay vào thói quen/nỗi niềm đời thường (~4.2 âm tiết/s).
   - **Hồi 2 — Reframe & Dilemma (15–35%):** Lật ngược định kiến số đông bằng nghịch lý khoa học + `[pause:900ms]`.
   - **Hồi 3 — Causal Evidence 70/30 (35–65%):** 70% dẫn dắt hình ảnh/cảm xúc $\leftrightarrow$ 30% dữ liệu thực nghiệm (~4.0 âm tiết/s).
   - **Hồi 4 — Direct Contrast (65–85%):** Đặt hai thực tại đối lập cạnh nhau.
   - **Hồi 5 — Loop Closure & Payoff (85–100%):** Quay lại hình ảnh mở đầu, hạ nhịp sâu lắng (~3.6–3.8 âm tiết/s).
2. **Luân phiên 5 thế chuyển cảnh động (Rotating Transition Grammar):**
   - Tuyệt đối cấm các câu dẫn sáo rỗng (*"Nhưng rồi..."*, *"Bước sang..."*, *"Hãy cùng bước vào..."*, *"Hãy nhìn lại..."*, *"Nhưng câu chuyện chưa dừng lại ở đó..."*).
   - Bắt buộc luân chuyển: (1) **Sensory Jump** (bước nhảy giác quan); (2) **Paradox Pivot** (nghịch lý lật ngược); (3) **Perspective Shift** (đổi góc nhìn vĩ mô $\to$ cá thể); (4) **Micro-Moment Focus** (tiêu cự hành động nhỏ biểu tượng); (5) **Causal Hook** (móc xích nhân quả trực tiếp).
3. **Phân vùng lịch sử một chiều (Strict Forward Chronology):**
   - Khi đã bước sang thời kỳ mới (Nông nghiệp, Trung cổ, Công nghiệp, Kỷ nguyên số), **nghiêm cấm** kéo ngược bối cảnh về quá khứ (*"thời tiền sử"*, *"thợ săn"*, *"bộ não 300.000 năm"*).

---

## 3. Công Thức Âm Học Triệt Tiêu Dead-Air & Pacing Động Học

### 3.1. Hằng số âm học đuôi động cơ ($P_{\text{tail}}$)
Trong hệ thống Video Pilot (`sys/adapters.py`), động cơ tổng hợp TTS tự động chèn khoảng đệm im lặng vào đuôi mỗi tệp audio:
- **Cảnh thường / trung gian:** $P_{\text{tail}} = 0.70\text{s}$ (`DEFAULT_PAUSE['para']`).
- **Cảnh kết thúc:** $P_{\text{tail}} = 0.35\text{s}$ (`DEFAULT_PAUSE['tail']`).
- **Dấu phẩy (ngắt hơi nhỏ):** $P_{\text{comma}} = 0.30\text{s}$ (`DEFAULT_PAUSE['minor']`).

### 3.2. Công thức tính số âm tiết mục tiêu (Target Syllables)
Để thời lượng audio thực tế khớp chính xác với dòng thời gian cảnh trong dung sai khắt khe **$\pm 0.5\text{s}$**:

$$\text{Target Syllables} = \text{round}\Big((\text{Scene Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$$

- Khi kịch bản có nhiều dấu phẩy, mỗi dấu phẩy chiếm khoảng $0.30\text{s} \times 4.0 \approx 1.2$ âm tiết; chủ động trừ bớt 1 âm tiết trên mỗi dấu phẩy nếu cần tinh chỉnh sâu.
- Các khoảng ngắt kịch tính chủ đích được viết dưới dạng `[pause:800ms]` hoặc `[pause:900ms]` (được chuẩn hóa thành `0.48s` sau khi cắt khoảng lặng nội sinh `OmniVoice` theo `ERR-20261011-02`, trong khi câu ngắn `< 8` từ dùng `0.20s` và câu thường dùng `0.28s`) và được trừ hoàn toàn khỏi văn bản hiển thị phụ đề.
- **Chống vụn nhịp câu ngắn (`SENTENCE_FRAGMENTATION`):** Không đặt quá 2 câu siêu ngắn (`< 6` âm tiết) hoặc quá 4 câu trong một cảnh trung bình; ưu tiên ghép các mệnh đề ngắn cùng ý bằng dấu phẩy (`,`) để giọng đọc `OmniVoice` liền mạch, tự nhiên.
- **Giao thức Dữ kiện Văn nói (`Conversational Spoken Fact Protocol` — `ERR-20261011-03`):** Toàn bộ dữ kiện nguồn trong `brief.json` (`research_sources[].facts` và `required_points`) phải được chuyển hóa trước thành các câu văn nói ngắn gọn, đanh thép **$\le 20$ âm tiết** (ngưỡng cảnh báo nghiêm ngặt $\le 22$), tuyệt đối không copy-paste nguyên văn trích dẫn sách báo học thuật khô khan chứa mã DOI, ISBN, `et al.`, phần trăm hoặc công thức toán học (`check_conversational_spoken_facts()`).

### 3.3. Dải tốc độ động học 3 giai đoạn (Dynamic Pacing)
- **Giai đoạn Mở đầu (Hook & Empathy):** ~4.2 âm tiết/s (Tiếng Việt) / ~145–150 wpm (Tiếng Anh).
- **Giai đoạn Cơ chế (Causal Explanation):** ~4.0 âm tiết/s (Tiếng Việt) / ~135–140 wpm (Tiếng Anh).
- **Giai đoạn Đúc kết (Philosophical Payoff):** ~3.6–3.8 âm tiết/s (Tiếng Việt) / ~120–125 wpm (Tiếng Anh).
- **Ngưỡng cảnh báo kỹ thuật:** $> 4.5$ âm tiết/giây (quá vội, dồn ép); $< 3.2$ âm tiết/giây (chậm chạp, ru ngủ).

Chi tiết xem tại: [Quy chuẩn Giọng đọc, Tốc độ và Ngắt nhịp](../vp-channel-patterns/references/voice-cadence-pacing.md).

---

## 4. Đồng Bộ Visual Beats (`beats[]`) Triệt Tiêu Đơ Hình

Để tránh hiện tượng **Scene Hold Stagnation (hình ảnh bị giữ đơ quá lâu)** mà không làm hỏng dòng chảy âm thanh:

1. **Cấm chia nhỏ Scene dưới 2.5s:** Tuyệt đối không cắt câu thoại liên tục thành các Scene micro ($D \le 2.5\text{s}$) vì việc tích lũy các đuôi $P_{\text{tail}} = 0.70\text{s}$ sẽ làm tổng thời lượng audio bị phình to (+35% đến +70%) và làm đứt đoạn ngữ điệu tự nhiên.
2. **Tổ chức thành Visual Beats (`beats[]`):** Trong mỗi Scene dài (10–14s), giữ nguyên một tệp audio liền mạch, nhưng cấu hình 3–4 nhịp hình ảnh xuất hiện so le trong mảng `beats[]`:
   - `offset: 0.0s`, `3.5s`, `7.2s`...
   - Khóa chặt từ neo thoại (*semantic anchors*) vào hành động camera (`zoom_in`, `pan_left`, `ken_burns`) hoặc hiệu ứng sticker nảy lên.

---

## 5. Quy Trình Sản Xuất & Công Cụ Kiểm Tra Tự Động

Mọi kịch bản sau khi soạn thảo phải được kiểm tra thông qua công cụ tự động:

```bash
python3 sys/tools/script_cadence_checker.py path/to/script.json
```

Công cụ sẽ tự động:
1. Đếm chính xác số âm tiết tiếng Việt / tiếng Anh.
2. Áp dụng công thức trừ bù $P_{\text{tail}}$ và khoảng ngắt kịch tính `[pause:800ms]` / `[pause:900ms]`.
3. Đo lường tốc độ đọc danh định và cảnh báo nếu vượt ngưỡng ($> 4.5$ hoặc $< 3.2$ âm tiết/s).
4. Cảnh báo độ lệch dòng thời gian (drift) nếu vượt quá dung sai $\pm 0.5\text{s}$ và cảnh báo `SENTENCE_FRAGMENTATION` nếu cảnh bị băm vụn thành nhiều câu quá ngắn.

### 5.1. Bộ Kiểm Định Kịch Bản Đa Dạng (Script Diversity & Zero-Backtracking Linter)

Mọi kịch bản trước khi đưa vào sản xuất và thu âm bắt buộc phải vượt qua công cụ kiểm định tự động:

```bash
python3 sys/tools/script_diversity_linter.py path/to/content.json
```

**Các tiêu chuẩn bắt buộc (Hard Constraints):**
1. `check_formulaic_transitions`: 0 vi phạm các mẫu câu chuyển cảnh rập khuôn.
2. `check_historical_backtracking`: 0 từ khóa thời kỳ cũ xuất hiện ở các chương sau (Strict Forward Chronology).
3. `check_intra_video_repetitions`: 0 cụm n-gram (3-4 từ) lặp lại trong phạm vi 4 cảnh liền kề (trừ các câu fact học thuật bắt buộc).
4. `check_corpus_cross_similarity`: 0 sự trùng lặp cấu trúc mở đầu với các video đã xuất bản trong `sys/exports/`.

---

## 6. Danh Mục Tài Liệu Tham Khảo

- [Khung Kể Chuyện Conversational Essayist](references/conversational-essayist-framework.md)
- [Sổ Tay Lời Dẫn Văn Nói Tiếng Việt](references/spoken-narration-guide.md)
- [Quy Chuẩn Giọng Đọc, Tốc Độ & Ngắt Nhịp](../vp-channel-patterns/references/voice-cadence-pacing.md)
- [Chỉ Dẫn Kịch Bản Sản Xuất](../vp-production/references/script.md)
- [Chỉ Dẫn Âm Thanh Sản Xuất](../vp-production/references/audio.md)
