# Staged Governance: Quy Chuẩn Chống Lặp Từ Vựng & Cấu Trúc Kịch Bản (Script Diversity & Forward Chronology)

> **Trạng thái:** ĐÃ PHÊ DUYỆT & ĐỒNG BỘ CHÍNH THỨC (RATIFIED & ACTIVE)  
> **Chỉ thị:** Đã đồng bộ trực tiếp vào `AGENTS.md` (Mục 4 & 6) và `.agents/skills/vp-scriptwriting/SKILL.md` (Mục 2.1 & 5.1).  
> **Xác thực:** Video `study_motivation_full_13m_final.mp4` và hệ thống kiểm tra đạt 100% PASS sau thẩm định của Người dùng.

---

## 1. Nội Dung Đề Xuất Bổ Sung Vào `AGENTS.md`

### Vị trí: Mục 6 (Anti-Hallucination & Anti-Laziness Guard)

```markdown
### 6.1. Lexical & Transition Diversity Invariant (Quy Chuẩn Chống Lặp Lời Thoại)
- **Zero Formulaic Bridges:** Nghiêm cấm tuyệt đối các câu dẫn chuyển cảnh sáo rỗng hoặc rập khuôn giữa các chương và phân cảnh:
  - CẤM: *"Nhưng rồi..."*, *"Bước sang..."*, *"Hãy cùng bước vào..."*, *"Hãy nhìn lại..."*, *"Hãy cùng khám phá..."*, *"Nhưng câu chuyện chưa dừng lại ở đó..."*.
  - THAY THẾ: Bắt buộc luân chuyển 5 thế chuyển cảnh tự nhiên: Sensory Jump (bước nhảy giác quan), Paradox Pivot (nghịch lý lật ngược), Perspective Shift (chuyển đổi góc nhìn), Micro-Moment Focus (tiêu cự vi mô), hoặc Cause-and-Effect Hook (móc xích nhân quả).
- **Strict Forward Chronology (Phân Vùng Lịch Sử Một Chiều):**
  - Tuyệt đối không kéo ngược bối cảnh về quá khứ (Backtracking Overload): Khi kịch bản đã bước sang thời kỳ mới (Cổ đại, Phong kiến, Công nghiệp, Kỷ nguyên số), nghiêm cấm nhắc lại vô căn cứ các hình ảnh thời kỳ trước như *"người tiền sử"*, *"thợ săn"*, *"thảo nguyên"*, *"đống lửa"*.
  - Mỗi thời kỳ lịch sử chỉ được xuất hiện trọn vẹn trong phân vùng thời gian của nó.
- **Corpus Uniqueness Guard (Bảo Vệ Độc Bản Toàn Hệ Thống):**
  - Cấm sao chép cấu trúc mở đầu từ các video trước trong hệ thống (ví dụ mẫu câu `[Thời gian] + Bạn ngồi [trạng thái tiêu cực] trước [vật thể]`).
  - Mọi kịch bản phải chạy qua `sys/tools/script_diversity_linter.py` và đạt 100% PASS (0 cảnh báo lặp từ gần, 0 câu nối rập khuôn, 0 backtracking) trước khi chuyển sang bước thu âm TTS.
```

---

## 2. Nội Dung Đề Xuất Bổ Sung Vào `.agents/skills/vp-scriptwriting/SKILL.md`

### Vị trí: Thêm Mục 2.1 (Nghệ Thuật Chuyển Cảnh Luân Phiên) và Mục 6 (Công Cụ Kiểm Định Đa Dạng Kịch Bản)

```markdown
## 2.1. Nghệ Thuật Chuyển Cảnh Luân Phiên (Rotating Transition Grammar)

Để duy trì sự lôi cuốn và độc bản của lời dẫn thoại, biên kịch viên tuân thủ nghiêm ngặt 5 thế chuyển cảnh sau đây:

1. **Sensory Jump (Bước nhảy giác quan):**
   - Mở đầu bằng âm thanh hoặc chi tiết vật lý sắc nét (tiếng cào móng trên phiến đất sét, tiếng còi hú tầm tan ca, giọt mực loang trên trang giấy).
2. **Paradox Pivot (Nghịch lý lật ngược):**
   - Đặt ngay một câu hỏi lật ngược niềm tin phổ biến thay cho câu nối liệt kê.
3. **Perspective Shift (Chuyển đổi góc nhìn):**
   - Chuyển từ góc nhìn bao quát vĩ mô sang hành động cụ thể của một cá nhân đang trải nghiệm khoảnh khắc đó.
4. **Micro-Moment Focus (Tiêu cự vi mô):**
   - Zoom sâu vào một hành vi rất nhỏ nhưng phản ánh toàn bộ bản chất của hệ thống.
5. **Causal Hook (Móc xích nhân quả trực tiếp):**
   - Đi thẳng từ hệ quả của cảnh trước vào tiền đề của cảnh sau mà không cần từ nối đệm rườm rà.

---

## 6. Bộ Kiểm Định Kịch Bản Đa Dạng (Script Diversity & Zero-Backtracking Linter)

Mọi kịch bản trước khi đưa vào sản xuất phải vượt qua công cụ kiểm định tự động:

```bash
python3 sys/tools/script_diversity_linter.py sys/runs/<job>/content.json
```

**Các tiêu chuẩn bắt buộc (Hard Constraints):**
1. `check_formulaic_transitions`: 0 vi phạm các mẫu câu chuyển cảnh rập khuôn.
2. `check_historical_backtracking`: 0 từ khóa thời kỳ cũ xuất hiện ở các chương sau.
3. `check_intra_video_repetitions`: 0 cụm n-gram (3-4 từ) lặp lại trong phạm vi 4 cảnh liền kề (trừ các câu fact học thuật bắt buộc).
4. `check_corpus_cross_similarity`: 0 sự trùng lặp cấu trúc mở đầu với các video đã xuất bản trong `sys/exports/`.
```

---

## 3. Nhật Ký Kích Hoạt (Activation Checklist)

Khi người dùng phản hồi xác nhận video `study_motivation_full_13m_final.mp4` mới đạt yêu cầu:
- [x] Chạy lệnh chèn nội dung mục 1 vào `AGENTS.md`.
- [x] Chạy lệnh chèn nội dung mục 2 vào `.agents/skills/vp-scriptwriting/SKILL.md`.
- [x] Kiểm tra xác nhận tự động: `pytest` đạt 8/8 PASS, `script_diversity_linter.py` đạt 0 lỗi vi phạm.
