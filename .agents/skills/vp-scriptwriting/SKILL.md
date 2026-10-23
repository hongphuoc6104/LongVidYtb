---
name: vp-scriptwriting
description: "Author and transform explainer video scripts into natural conversational spoken storytelling with counter-intuitive 3-second hooks and calibrated acoustic cadence."
---

# VP Scriptwriting — Conversational Essayist, Truth-Slap Hook & Voice Cadence Skill

`vp-scriptwriting` là bộ kỹ năng cốt lõi dùng để sáng tác và thẩm định kịch bản video trong Video Pilot (cho cả `long_16x9` và `short_9x16`). Bộ kỹ năng này được tối ưu hóa cho **Agent Gemini Flash**: loại bỏ việc tính toán công thức phức tạp thủ công, tập trung 100% vào câu thoại tự nhiên, giàu nhịp điệu cảm xúc và gắn kết 1-1 với hành động hình ảnh toàn khung (`full_frame_v1`).

---

## 1. Bản Sắc Giọng Kể, Cú Tát Sự Thật Mở Màn & Nhịp Câu Con Người

- **Hình tượng (The Voice Archetype):** **Conversational Essayist (Nhà luận thuyết trò chuyện)** — điềm đạm, ấm áp, sắc sảo, như người bạn đồng hành tri thức bên bàn cà phê, khóa cứng ngách **"Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"**.
- **Trục Phân Tích - Bình Luận - Đánh Giá Con Người (`human_editorial` Spine — Chống AI-Slop):**
  - Kịch bản bắt buộc lấy lập trường (`editorial_stance`) và các ý tưởng chi tiết mở rộng từ góc nhìn tác giả (`expanded_content_ideas` trong `brief.json`) làm **xương sống dẫn dắt**.
  - Tuyệt đối không viết theo lối tổng hợp thông tin trung tính kiểu Wikipedia/AI. Mỗi phân đoạn phải thể hiện rõ sự **phân tích nguyên nhân ngầm**, **bình luận phản biện**, và **đánh giá trọng số giá trị** của con người; dữ kiện khoa học (`sources`) chỉ được trích dẫn làm bằng chứng phục vụ cho trục bình luận đó.
- **Counter-Intuitive / Truth-Slap Hook (Cú tát sự thật trong 2.5 giây đầu):**
  - Câu đầu tiên của `SC01` bắt buộc **$\le 18$ âm tiết** (`OPENING_HOOK_TOO_LONG`), đánh thẳng vào nghịch lý phản trực giác hoặc lật tẩy ảo giác học thuật của người xem (ví dụ: *"Trang sách vàng kín, đầu bạn vẫn trống."* — 8 âm tiết; hoặc *"Đọc lại giáo trình năm lần chỉ tạo ra ảo giác hiểu bài."* — 12 âm tiết).
  - **Tuyệt đối cấm** mở đầu bằng lời chào (*"Xin chào"*), giới thiệu đề tài (*"Hôm nay chúng ta..."*), hoặc câu dẫn nhập chậm (*"Hãy nghĩ về..."*, *"Hãy hình dung..."*, *"Hãy tưởng tượng..."*, *"Giờ đây, hãy thử..."*).
- **Zero Pause in First 15 Seconds (`SC01` — `OPENING_SCENE_PAUSE_FORBIDDEN`):**
  - **Nghiêm cấm** chèn bất kỳ thẻ `[pause:...]` nào trong cảnh mở đầu `SC01`.
- **Quy Tắc Nhịp Điệu Tự Nhiên (Chống "Văn Mẫu AI"):**
  - **Bắt buộc xen kẽ câu ngắn và câu dài (`stddev_syllables >= 1.8`):** Không bao giờ viết mọi cảnh đều chằn chặn 3 câu dài 18–20 chữ. Mỗi chương/kịch bản bắt buộc phải xen kẽ các câu ngắn đanh gọn (**3–8 âm tiết**, ví dụ: *"Đó là ảo giác năng lực."*, *"Mỏ vàng nằm ở cuối bài."*, *"Làm sao biết bạn hiểu thật?"*) với các câu giải thích cơ chế (**15–24 âm tiết**).
  - **Cấm ngắt dấu phẩy ngang xương giữa Chủ ngữ và Vị ngữ:** Tuyệt đối không chèn dấu phẩy vô lý giữa chủ ngữ và động từ (ví dụ sai: *"Bản chất của tổng quan tài liệu, là..."* hoặc *"Đó là nơi bạn vẽ nên, khoảng trống..."*) chỉ để lách luật đếm chữ. Hãy tách hẳn thành một câu ngắn tự nhiên.
  - **Tự động chuẩn hóa ở Backend:** Hệ thống (`sys/remote_audio.py`, `sys/adapters.py`, `sys/colab_bridge/worker.py`) đã tự động tách thẻ `[pause:...]` thành khoảng nghỉ âm học thực tế và tự động phiên âm số/từ mượn qua `vn_text_normalizer.py`. Agent chỉ cần tập trung viết câu tiếng Việt tự nhiên, giàu hình ảnh.

---

## 2. Khung Kể Chuyện 8 Phần Ngầm (`narrative_phase`) & Điều Biến Giọng Động

1. **Mạch Truyện 8 Chặng Nhận Thức (`NARRATIVE_ARC_8_STAGES` / `narrative_phase` trên `full_frame_v1`):**
   - Kịch bản luôn được chia thành **8 chặng tư duy rõ ràng** để người xem không bao giờ thấy đều đều, lộn xộn hay mất phương hướng:
     1. **`hook` (Mở bài):** Cú tát sự thật $\le 18$ âm tiết + lát cắt đời thực sát sườn.
     2. **`lead_in` (Phần dẫn):** Neo cảm xúc và bối cảnh thực tế tại Việt Nam (`tone: "narrative_warm"`).
     3. **`problem` (Phần vấn đề):** Phơi bày mâu thuẫn nhận thức — vì sao cách làm quen thuộc lại phản tác dụng.
     4. **`causal_mechanism` (Phần nhân quả):** Giải phẫu cơ chế nhân quả gốc rễ và bằng chứng thực nghiệm.
     5. **`explanation` (Phần giải thích):** Mô hình hóa trực quan qua sơ đồ nhân quả hoặc ẩn dụ vật lý (`visual_diagram`, `concept_metaphor`).
     6. **`counter_argument` (Phần phản biện):** Lật ngược giả định thông thường, xét góc nhìn đối lập hoặc giới hạn của giải pháp để tránh cảm giác giảng đạo một chiều.
     7. **`takeaway` (Phần nội dung rút ra):** Đúc kết nguyên lý/khung tư duy cốt lõi để người xem mang về áp dụng ngay.
     8. **`closing` (Phần kết bài, `tone: "reflective_slow"`):** Khép vòng lặp với chi tiết ở cảnh mở đầu.
   - *(Tương thích ngược với 4 pha macro: `lived_friction` $\leftrightarrow$ `hook`/`lead_in`; `empirical_conflict` $\leftrightarrow$ `problem`/`causal_mechanism`; `structural_model` $\leftrightarrow$ `explanation`/`counter_argument`; `actionable_resolution` $\leftrightarrow$ `takeaway`/`closing`).*
   - **Điều biến `tone` động (`_infer_scene_tone`):** Ở thân bài, không khóa cứng 100% vào `analytical_crisp`; hệ thống tự động xen kẽ `reflective_slow` hoặc `narrative_warm` ở các cảnh đặt câu hỏi bản chất (`?`, `tại sao`, `nghịch lý`, `sụp đổ`, `ảo giác`) để giữ sóng cảm xúc.
2. **Chuyển Ý Tự Nhiên (Cấm Khẩu Hiệu Mục Lục Kiểu AI):**
   - Tuyệt đối cấm các câu dẫn sáo rỗng hoặc thông báo mục lục máy móc (*"Phần 1 là..."*, *"Bước sang phần hai..."*, *"Đầu tiên chúng ta hãy..."*, *"Tóm lại là..."*, *"Trong kỷ nguyên số hiện nay..."*, *"Như một con dao hai lưỡi..."*, *"Nhưng rồi..."*, *"Hãy cùng khám phá..."*). Hãy chuyển chặng bằng câu hỏi kích hoạt tò mò hoặc từ nối tự nhiên (*"Vấn đề nằm ở chỗ..."*, *"Thế nhưng có một nghịch lý..."*, *"Nếu nhìn sâu vào cơ chế..."*, *"Khoan đã, liệu cách này có luôn đúng?"*).
3. **Phân vùng lịch sử một chiều (Strict Forward Chronology):**
   - Khi đã bước sang thời kỳ mới, nghiêm cấm kéo ngược bối cảnh về thời kỳ cũ. Trong 60 giây đầu (`SC01–SC02`), bắt buộc giữ 100% bối cảnh hiện đại gần gũi với người xem Việt Nam.

---

## 3. Viết Kịch Bản Gắn Kết Với Nhịp Hình Ảnh (`Clause/Sentence-Beat Pairing`)

Để Agent không bao giờ tính sai tọa độ hay trượt điểm neo (`anchor_quote`), hãy soạn kịch bản theo từng cặp **`(Câu hoặc mệnh đề thoại tự nhiên, "loại_shot|Hành động hình ảnh cụ thể")`** (như trong `sys/tools/build_full_frame_acceptance.py` hoặc hàm `build_scenes_from_story_rows` trong `sys/content/research_story_architect.py`):

- **`full_scene`**: Nhân vật người que ẩn danh và đồ vật tương tác trực tiếp trong bối cảnh vật lý.
- **`variation`**: Giữ nguyên căn phòng và góc máy của ảnh trước (`based_on`), chỉ đổi cử chỉ tay/biểu cảm nhân vật (tối đa **2 nhịp `variation` liên tiếp**; đến nhịp thứ 3 bắt buộc đổi góc máy sang `macro_prop`, `visual_diagram` hoặc `full_scene` góc mới để tránh đứng hình nhàm chán).
- **`macro_prop`**: Cận cảnh bàn tay 4 ngón hoạt hình cầm bút, trang sách tô vàng, đồng hồ hoặc chi tiết sơ đồ.
- **`visual_diagram`**: Sơ đồ nhân quả hoặc biểu đồ so sánh vẽ tay trực quan trên nền sáng sạch (`camera: hold`).
- **`concept_metaphor`**: Ẩn dụ thị giác vật lý hóa cơ chế trừu tượng.
- **`white_card`**: Thẻ khái niệm nền trắng tinh `#FFFFFF` cô lập một biểu tượng đối sánh tối giản (`camera: hold`).
- **`white_isolated`**: Nền trắng tinh `#FFFFFF` với đối tượng hoặc nhân vật được cô lập hoàn toàn.
- **`still_life`**: Nhịp nghỉ thị giác (rest frame) cận cảnh hoặc trung cảnh tập trung vào vật thể, tài liệu, sách, thiết bị, đồng hồ — tuyệt đối không vẽ nhân vật người que hay bàn tay hoạt hình.
- **`environment`**: Nhịp nghỉ thị giác (rest frame) cảnh rộng thiết lập không gian, phòng ốc, phong cảnh, đại lộ — hoàn toàn vắng bóng nhân vật.

1. **Khoảng thở thị giác & Nhịp kể (Visual Breathing Room):**
   - Xen kẽ nhịp kể với các khung hình nghỉ (`still_life`, `environment`): bắt buộc có ít nhất 30% nhịp hình không có nhân vật trong mỗi chuỗi 10 nhịp trượt.
   - **Trần nhịp nhân vật & trần `variation` liên tiếp:** Tuyệt đối cấm viết quá 4 nhịp hình có nhân vật liên tiếp, và cấm quá 2 nhịp `variation` (`based_on`) liên tiếp.
   - **Quy chuẩn Bối cảnh (Setting Brevity):** Mỗi bối cảnh `setting` chỉ được dài $\le 8$ từ (chỉ nêu không gian và điều kiện ánh sáng, nghiêm cấm liệt kê đồ đạc/đạo cụ).
2. **Cold open (`0:00–0:12.5`) & Cấm Lệnh Vật Lý Vụn Vặt (`MICRO_ACTION_FILLER_BABBLE`):** Đạt **3–5 hình trong 5 giây đầu** và **6–10 hình trong 12,5 giây đầu** bằng **đối trọng thị giác (Visual Counterpoint)** lật tẩy mâu thuẫn nhận thức; tuyệt đối cấm viết $\ge 3$ câu lệnh vật lý 4 chữ tầm thường liên tiếp (*"Cầm cây bút lên. Đặt xuống tờ giấy trắng. Mở sách ra."*).
3. **Thân bài (`sau 0:15`):** Với câu dài $> 14$ chữ có bước ngoặt ý, tách thành 2 nhịp hình theo mệnh đề (`split_long_sentence_into_beat_clauses()`) để mỗi nhịp hình rơi vào khoảng **`1.2s–3.5s`**, kể chuyện thí nghiệm sinh động nhưng không trích dẫn khô khan kiểu `et al.`, `DOI:`, `(2008)`.

---

## 4. Công Cụ Kiểm Tra Tự Động

```bash
# Kiểm tra âm học, cấm pause ở SC01, trần câu mở đầu <= 18 âm tiết, trần câu <= 25 âm tiết
python3 sys/tools/script_cadence_checker.py path/to/content.json \
  --forbid-opening-pause \
  --max-opening-hook-syllables 18 \
  --max-sentence-syllables 25 \
  --max-clause-syllables 18 \
  --max-dramatic-pauses 4 \
  --strict

# Kiểm định tính đa dạng kịch bản và nhịp điệu câu tự nhiên (stddev_syllables & short_punchy_count)
python3 sys/tools/script_diversity_linter.py path/to/content.json
```

---

## 5. Danh Mục Tài Liệu Tham Khảo

- [Khung Kể Chuyện Conversational Essayist](references/conversational-essayist-framework.md)
- [Sổ Tay Lời Dẫn Văn Nói Tiếng Việt](references/spoken-narration-guide.md)
- [Quy Chuẩn Giọng Đọc, Tốc Độ & Ngắt Nhịp](../vp-channel-patterns/references/voice-cadence-pacing.md)
- [Chỉ Dẫn Kịch Bản Sản Xuất](../vp-production/references/script.md)
- [Chỉ Dẫn Âm Thanh Sản Xuất](../vp-production/references/audio.md)
- [Hợp Đồng Chất Lượng Toàn Khung](../vp-full-frame-quality/SKILL.md)

## Active pause authoring (format_v1)

- Default gaps come from `sys/format_profiles.py`; do not add a pause at every image cut.
- SC01 has short automatic breaths but rejects explicit `[pause:...]`.
- Suggested intentional pivots: 450 ms for standalone shorts, 600 ms for long narration. Existing tags remain exact; never silently compress them. Use a terminal tag for a deliberate major scene transition.
- Run `sys/tools/preview_narration_pauses.py` for planned silence; actual WAV determines timing. Legacy cadence estimates are not the new pause budget.
- Details and rollout: [pause implementation plan](../../../sys/docs/narration-pause-implementation-plan.md).
