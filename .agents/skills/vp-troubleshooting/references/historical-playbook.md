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

### [ERR-20261014-01] Chốt Chặn Âm Học, Độ Lệch Chuẩn Nhịp Câu & Cú Tát Sự Thật `SC01`
- **Triệu chứng (Symptom):** Kịch bản bị nhồi câu dài $> 25$ âm tiết, đọc một lèo không phẩy $> 18$ âm tiết hoặc rải `[pause:800ms]` cơ học ngay ở `SC01`.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_script_cadence_checker.py sys/tests/test_human_naturalness_upgrades.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Thiếu chốt chặn trần âm tiết câu đơn, trần vế câu không phẩy, giới hạn tổng số pause kịch tính và kiểm tra Cú Tát Sự Thật mở màn.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng chỉ cần đạt `drift <= 0.30s` là kịch bản tự nhiên và có thể dùng `[pause]` để giảm chỉ tiêu âm tiết.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Bổ sung `SENTENCE_TOO_LONG`, `BREATHLESS_CLAUSE`, `EXCESSIVE_DRAMATIC_PAUSES`, `OPENING_SCENE_PAUSE_FORBIDDEN` và `OPENING_HOOK_TOO_LONG` (`<= 18` âm tiết) vào `sys/tools/script_cadence_checker.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Câu mở đầu `SC01` phải $\le 18$ âm tiết với `0` thẻ `[pause:...]`; toàn bài dùng tối đa 1–3 dramatic pause trước điểm bẻ lái.

### [ERR-20261016-02] Hợp Đồng Ảnh Toàn Khung (`full_frame_v1`) & Cấm Ghép Lớp Sticker Cut-out
- **Triệu chứng (Symptom):** Tạo ảnh nền và sticker tách rời (`kind: "background"`/`"sticker"`) khiến hình ảnh rời rạc và thiếu mật độ đổi hình trong Cold Open.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_full_frame_pipeline.py sys/tests/test_full_frame_upgrade.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Serializer cũ tách `ResearchedScene` thành layer rời và thiếu kiểm định mật độ beat hình theo từng câu thoại.
- **Giả định sai (Wrong Assumptions):** Giả định cần tách nền `matte_sticker.py` hoặc chừa dải trắng đáy ảnh `caption_clearance` trên khung ngang `16:9`.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Chuẩn hóa 100% sang ảnh toàn khung `kind: "scene"` (`shot_type` trong `full_scene|macro_prop|variation|white_card`), `caption_clearance: null` trên `16:9`, 6–10 ảnh trong `12.5s` đầu (`3–5` ảnh trong `5s` đầu) và xóa bỏ `matte_sticker.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Chỉ dùng ảnh toàn khung `kind: "scene"` có `anchor` theo câu thoại và `Expression lock` trên các biến thể `variation` (trừ khi khai báo `allow_expression_shift: true`).

### [ERR-20261017-02] Xuất Bản Đa Nền Tảng (`vp-omni-platform`) & Giữ Khóa Profile Flow CDP
- **Triệu chứng (Symptom):** Sinh trùng ảnh giữa các tỷ lệ khung hình hoặc mất liên kết profile trình duyệt cố định khi chạy đồng thời các tác vụ ảnh.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_omni_platform.py sys/tests/test_flow_cdp_bridge.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Tách rời `jobId` khỏi `testCase` khi gửi qua bridge và chưa tái sử dụng ảnh chung cho các bản xuất đa nền tảng.
- **Giả định sai (Wrong Assumptions):** Cho rằng `testCase` ID đại diện cho `jobId` và một trình duyệt cố định có thể nhận nhiều hàng đợi UI song song.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Truyền tường minh `jobId` qua bridge, tuần tự hóa khi khóa vào 1 profile (`sequential_close`) và đóng gói xuất bản đa nền tảng qua `sys/omni_platform.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Bảo toàn định danh `jobId` và quyền sở hữu trình duyệt xuyên suốt vòng đời job; tuân thủ [Omni-platform contracts](.agents/skills/vp-omni-platform/SKILL.md).

### [ERR-20261017-04] Chặn 6 Nguyên Nhân Khiến Nội Dung Thực Tế Bị Flop (Anti-Flop Content Gate)
- **Triệu chứng (Symptom):** Video xuất bản thực tế bị tuột giữ chân khán giả trong 15 giây đầu do lặp lại cùng một kịch bản tô sách vàng ở mọi job, câu thoại mở màn toàn lệnh vật lý 4 chữ vụn vặt, hoặc ngắt dấu phẩy giả tạo giữa chủ ngữ và vị ngữ (`, chỉ tạo ra`).
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_script_cadence_checker.py sys/tests/test_research_story_architect.py -v` để kiểm tra `UNNATURAL_SUBJECT_VERB_COMMA` và `MICRO_ACTION_FILLER_BABBLE`.
- **Nguyên nhân cốt lõi (Root Cause):** Các script tạo đề tài bị hardcode cùng một chủ đề; lách luật `BREATHLESS_CLAUSE` bằng dấu phẩy sai ngữ pháp trước động từ `là`, `chỉ tạo`; chia nhỏ hành động vật lý tầm thường.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng chỉ cần nhiều câu 4 chữ mô tả động tác tay là giữ chân được người xem và có thể nhét dấu phẩy bất kỳ đâu để qua mặt linter âm học.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Bổ sung `UNNATURAL_SUBJECT_VERB_COMMA` trong `script_cadence_checker.py` và `check_micro_action_filler()` trong `script_diversity_linter.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mỗi video chỉ xoay quanh 1 Nghịch Lý Cốt Lõi Duy Nhất, cấm lặp lại hook/chủ đề đã sản xuất và không đặt dấu phẩy ngăn cách chủ ngữ với vị ngữ.
