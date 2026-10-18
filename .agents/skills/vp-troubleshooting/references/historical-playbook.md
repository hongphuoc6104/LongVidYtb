# Video Pilot — Historical Playbook Archive

This file archives older or superseded PLAYBOOK.md entries to keep `PLAYBOOK.md <= 200` lines.

### [ERR-20261018-01] Khử Rung Giật & Triệt Tiêu Chu Kỳ Lặp Lại Của Camera Remotion (Superseded by ERR-20261018-02)
- **Triệu chứng (Symptom):** Chuyển động camera bị giật (micro-stutter) ở mép các nhịp beat, rung cầm tay gây nhòe/shimmer điểm ảnh và lặp khuôn mẫu sau 4 nhịp.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_renderer_effects.py -k test_camera_variety_and_sequence_constraints`.
- **Nguyên nhân cốt lõi (Root Cause):** Easing cũ có đạo hàm vận tốc lớn tại điểm cắt, organicNoise tần số cao và fallback chỉ xoay vòng 4 kiểu theo seed % 4.
- **Giả định sai (Wrong Assumptions):** Xoay vi mô rotate() mô phỏng camera cầm tay mà không nhận ra resample điểm ảnh tĩnh gây pixel shimmer.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Đổi sang bezier đối xứng hai đầu vận tốc bằng 0, trôi chậm hữu cơ 0.1Hz, mở rộng pool 8 kiểu chuyển động shuffle-bag khử lặp 3 nhịp.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Vận tốc camera tiệm cận 0 tại hai đầu chuyển cảnh, cấm rotate() trên ảnh tĩnh; chu kỳ dự phòng dùng shuffle-bag.

### [ERR-20261010-08] Chuẩn Hóa Ngữ Âm Tiếng Việt & Cắt Khoảng Lặng Nội Sinh OmniVoice
- **Triệu chứng (Symptom):** Giọng đọc `OmniVoice` (`VietNarrator`) phát âm sai chữ số/từ mượn tiếng Anh và bị khựng nhịp (`0.65s–1.35s`) giữa các câu.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_colab_worker.py sys/tests/test_script_cadence_checker.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Tokenizer đa ngữ đọc chữ số theo âm vị tiếng Anh, đồng thời `OmniVoice.generate()` tự sinh khoảng lặng nội sinh đầu/cuối câu.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng TTS tự đọc số sang tiếng Việt và xuất sóng âm sát mép âm tiết.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Chuẩn hóa 100% văn bản qua `sys/tools/vn_text_normalizer.py` và cắt khoảng lặng bằng `_trim_silence` trong `sys/colab_bridge/worker.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi kịch bản cấp cho `OmniVoice` phải đi qua `vn_text_normalizer.py` và cắt khoảng lặng nội sinh trước khi trộn âm.

### [ERR-20261010-09] Đồng Bộ Canonical JSON Hash Giữa Thượng Nguồn Và `pilot.py`
- **Triệu chứng (Symptom):** `pilot.py check_draft` từ chối `content.json` với lỗi `BRIEF_VERSION` dù nội dung hợp lệ.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_research_story_architect.py -k test_pilot_check_draft_direct_compatibility`.
- **Nguyên nhân cốt lõi (Root Cause):** Thượng nguồn băm JSON nén trong khi pilot.py băm file với `indent=2, ensure_ascii=False`.
- **Giả định sai (Wrong Assumptions):** Giả định mã băm dictionary trong bộ nhớ trùng khớp với `digest(file)` trên đĩa.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Dùng duy nhất `serialize_brief_json()` cho cả tính `brief_hash` và ghi đĩa.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Luôn tính `brief_hash` trực tiếp trên chuỗi byte canonical giống hệt định dạng ghi đĩa.

### [ERR-20261017-03] Centered Portrait Caption Profile 07
- **Triệu chứng (Symptom):** Portrait captions drift left and obscure the illustration with a large opaque panel.
- **Tái hiện E2E (Reproduction Path):** Run `pytest sys/tests/test_caption_profile_07.py` for replacement contract at 1080x1920.
- **Nguyên nhân cốt lõi (Root Cause):** Fixed left offset (56px) plus half width puts caption center at 466px rather than 540px.
- **Giả định sai (Wrong Assumptions):** Centered text inside a left-anchored box centers the box within the frame.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Profile 07 uses centered layout, transparent background, thin text outline and compact groups.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Center the entire caption group; preserve transcript tokens and measured timing.

