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

### [ERR-20261011-01] Tách Biệt Hồ Sơ Định Dạng SSOT (`short_9x16` & `long_16x9`)
- **Triệu chứng (Symptom):** Trộn lẫn thông số phụ đề, vùng trống đáy ảnh (`caption_clearance`) và tỷ lệ khung hình giữa video ngắn `9:16` và video dài `16:9`.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_format_separation.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Thiếu nguồn chân lý duy nhất (SSOT) định nghĩa tách biệt hai hồ sơ `short_9x16` và `long_16x9`.
- **Giả định sai (Wrong Assumptions):** Cho rằng có thể dùng chung quy tắc ngắt dòng phụ đề và vùng trống đáy ảnh cho cả hai định dạng.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Thiết lập `sys/format_profiles.py` quản lý độc lập `short_9x16` (`1080x1920`, `speed=1.0`, `clearance=0.18`) và `long_16x9` (`1920x1080`, `speed=1.0`, `clearance=None` trên `full_frame_v1`).
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi thông số khung hình, tốc độ giọng và vùng phụ đề phải truy xuất tường minh từ `sys/format_profiles.py`.

### [ERR-20261011-05] Mở Khóa NVIDIA Headless EGL, NVENC `6M` & Chống Rơi Tile Trên Colab T4
- **Triệu chứng (Symptom):** Render Remotion trên Colab T4 bị rơi về CPU hoặc bị vẽ thiếu ô trắng (tile drops), hoặc NVENC bị tự động tắt.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_renderer_tile_integrity.py sys/tests/test_colab_bridge_skill.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Thiếu khai báo `/usr/share/glvnd/egl_vendor.d/10_nvidia.json`, thiếu cờ khóa đồng bộ compositor trước khi chụp frame và thiếu `videoBitrate: '6M'` cho `h264_nvenc`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng phải dùng `xvfb-run` hoặc chỉ cần truyền `hardwareAcceleration: 'if-possible'` là bật được NVENC.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Cấu hình `10_nvidia.json` + `--use-angle=gl-egl`, khóa đồng bộ 4 tầng (`--run-all-compositor-stages-before-draw`, `--disable-checker-imaging`, `<Img decoding="sync">`), đặt `videoBitrate: '6M'` và tự động dọn phiên qua `teardown_job_resources()`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Cấm dùng `xvfb-run`; luôn chạy Headless EGL + `videoBitrate: '6M'` qua `chrome-wrapper.sh` và giải phóng phiên Colab/Chrome CDP ngay sau khi xong job.
