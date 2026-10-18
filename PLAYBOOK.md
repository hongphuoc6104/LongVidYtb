# Video Pilot — Sổ Tay Bài Học & Quản Trị Lỗi (PLAYBOOK)

> **Mục đích**: Lưu trữ quy tắc kỹ thuật cốt lõi và bài học vận hành hệ thống Video Pilot.
> **Quy chuẩn**: Mọi bài học ghi đủ **6 trường chuẩn hóa**. Luôn giữ `PLAYBOOK.md <= 200` dòng để bảo toàn hạn mức Token Quota; chi tiết dài đã được trích xuất vào `.agents/skills/`.

---

## I. Quy Trình 4 Bước Khắc Phục Lỗi Tối Thượng
$$\text{1. Tái hiện E2E} \longrightarrow \text{2. Phân tích gốc rễ} \longrightarrow \text{3. Sửa chuẩn kiến trúc} \longrightarrow \text{4. Kiểm chứng E2E & ghi Playbook}$$

---

## II. Danh Mục Bài Học & Sự Cố Chuẩn Hóa

### [ERR-20261017-03] Centered Portrait Caption Profile 07
- **Triệu chứng (Symptom):** Portrait captions drift left and obscure the illustration with a large opaque panel.
- **Tái hiện E2E (Reproduction Path):** At 1080×1920, the former 56 px left offset plus half the 820 px width puts the caption center at 466 px rather than 540 px. Run `pytest sys/tests/test_caption_profile_07.py` for the replacement contract.
- **Nguyên nhân cốt lõi (Root Cause):** Fixed left anchoring, opaque background, trailing token margins and full-cue karaoke increase visual imbalance and density.
- **Giả định sai (Wrong Assumptions):** Centered text inside a left-anchored box does not center the box within the frame.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Profile 07 uses centered layout, white/amber text, transparent background, thin text outline, no word scaling and compact groups from measured word starts. Regression tests verify token preservation, alignment fallback and responsive styles; static preview verifies appearance without rendering video.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Center the entire caption group; preserve transcript tokens and measured timing. Missing alignment must retain the full cue instead of inventing word timings. Static previews do not prove audiovisual sync.

### [ERR-20261010-08] Chuẩn Hóa Ngữ Âm Tiếng Việt & Cắt Khoảng Lặng Nội Sinh OmniVoice
- **Triệu chứng (Symptom):** Giọng đọc `OmniVoice` (`VietNarrator`) phát âm sai chữ số/từ mượn tiếng Anh và bị khựng nhịp (`0.65s–1.35s`) giữa các câu.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_colab_worker.py sys/tests/test_script_cadence_checker.py -v` với văn bản chứa số hoặc WAV chưa cắt lặng.
- **Nguyên nhân cốt lõi (Root Cause):** Tokenizer đa ngữ đọc chữ số theo âm vị tiếng Anh, đồng thời `OmniVoice.generate()` tự sinh khoảng lặng nội sinh đầu/cuối câu cộng dồn với khoảng nghỉ ghép câu.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng TTS tự đọc số sang tiếng Việt và xuất sóng âm sát mép âm tiết mà không có khoảng lặng dư thừa.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Chuẩn hóa 100% văn bản qua `sys/tools/vn_text_normalizer.py` và cắt khoảng lặng bằng `_trim_silence(lead_ms=25, trail_ms=30, fade_ms=8)` trong `sys/colab_bridge/worker.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi kịch bản cấp cho `OmniVoice` phải đi qua `vn_text_normalizer.py` (lọc sạch `[pause:...]`, số và từ ngoại lai) và cắt khoảng lặng nội sinh trước khi trộn âm.

### [ERR-20261010-09] Đồng Bộ Canonical JSON Hash Giữa Thượng Nguồn Và `pilot.py`
- **Triệu chứng (Symptom):** `pilot.py check_draft` từ chối `content.json` với lỗi `BRIEF_VERSION` dù nội dung hợp lệ.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_research_story_architect.py -k test_pilot_check_draft_direct_compatibility`.
- **Nguyên nhân cốt lõi (Root Cause):** Công cụ thượng nguồn băm chuỗi JSON nén trong khi `pilot.py` băm byte file ghi với `indent=2, ensure_ascii=False`.
- **Giả định sai (Wrong Assumptions):** Giả định mã băm dictionary trong bộ nhớ trùng khớp với `digest(file)` trên đĩa.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Dùng hàm duy nhất `serialize_brief_json()` (`indent=2, ensure_ascii=False`) cho cả khâu tính `brief_hash` và ghi đĩa.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Luôn tính `brief_hash` trực tiếp trên chuỗi byte canonical giống hệt định dạng ghi xuống đĩa.

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
- **Triệu chứng (Symptom):** Video xuất bản thực tế bị tuột giữ chân khán giả trong 15 giây đầu do lặp lại cùng một kịch bản tô sách vàng ở mọi job, câu thoại mở màn toàn lệnh vật lý 4 chữ vụn vặt (`Cầm cây bút lên. Đặt xuống tờ giấy trắng.`), hoặc ngắt dấu phẩy giả tạo giữa chủ ngữ và vị ngữ (`, chỉ tạo ra`).
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_script_cadence_checker.py sys/tests/test_research_story_architect.py -v` để kiểm tra `UNNATURAL_SUBJECT_VERB_COMMA` và `MICRO_ACTION_FILLER_BABBLE`.
- **Nguyên nhân cốt lõi (Root Cause):** (1) Các script tạo đề tài bị hardcode và nhân bản cùng một chủ đề `Roediger & Karpicke 2006`; (2) lách luật `BREATHLESS_CLAUSE` bằng cách nhét dấu phẩy sai ngữ pháp trước động từ `là`, `chỉ tạo`; (3) chia nhỏ hành động vật lý tầm thường để lấy số lượng beat hình thay vì dùng đối trọng thị giác (Visual Counterpoint); (4) `BANNED_ACADEMIC_NAMEDROPS` cấm cả cụm `"tại đại học"` khiến kịch bản mất khả năng kể chuyện thí nghiệm thực tế.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng chỉ cần nhiều câu 4 chữ mô tả động tác tay là giữ chân được người xem và có thể nhét dấu phẩy bất kỳ đâu để qua mặt linter âm học.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Bổ sung `UNNATURAL_SUBJECT_VERB_COMMA` trong `script_cadence_checker.py` chặn dấu phẩy trước `là|chỉ tạo|bằng cách|nhằm`; (2) bổ sung `check_micro_action_filler()` (`MICRO_ACTION_FILLER_BABBLE`) và tinh chỉnh `BANNED_ACADEMIC_NAMEDROPS` trong `script_diversity_linter.py` để cho phép kể chuyện thí nghiệm tự nhiên nhưng chặn trích dẫn học thuật khô khan (`et al.`, `DOI:`, `(2008)`); (3) xóa bỏ 31 script hardcode đề tài cũ và thu gọn `research_story_architect.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mỗi video chỉ xoay quanh **1 Nghịch Lý Cốt Lõi Duy Nhất**, cấm lặp lại hook/chủ đề đã sản xuất, cấm dùng chuỗi câu lệnh vật lý vụn vặt làm đầy cảnh mở đầu, và tuyệt đối không đặt dấu phẩy ngăn cách chủ ngữ với vị ngữ để lách luật âm tiết.

### [ERR-20261017-05] Gỡ Bỏ 7 Ràng Buộc Khuôn Mẫu Cứng Nhắc & Mở Khóa Kể Chuyện Đa Ngữ Cảnh (Anti-Formulaic Storytelling)
- **Triệu chứng (Symptom):** Mọi video giải thích khoa học đều bị ép vào cùng 4 căn phòng cố định (`study_desk`, `laboratory`, `comparison_board`, `exam_hall`), nhịp giọng phẳng lì ở 60% thân bài (`analytical_crisp`), chuyển động camera lặp vòng 2 trạng thái (`push_in`/`pull_back`), và nhân vật ẩn danh bị ép mặc áo `#8CCFE8`.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_anti_formulaic_storytelling.py -v` trên kịch bản đa lĩnh vực (Kinh tế học Đô thị) không chứa bàn học sinh viên.
- **Nguyên nhân cốt lõi (Root Cause):** (1) `check_scene_narrative_progression` khóa cứng 4 danh từ địa điểm vật lý thay vì 4 pha chức năng nhận thức; (2) `check_see_say_beat_density` ép đúng `4` beat/5s và `8–9` beat/12.5s quá hẹp; (3) beat cuối cảnh bị rập khuôn `macro_prop` quay vào bàn tay; (4) `tone` chia cứng `20/60/20`; (5) `coverage` lấy mù quáng câu đầu `.split(".")[0]`; (6) `camera_motion.py` chỉ xoay vòng 2 hiệu ứng; (7) `image_pipeline.py` tiêm cứng áo `#8CCFE8` cho mọi version và cấm đổi biểu cảm ở các beat bước ngoặt.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng chỉ có từ khóa địa điểm học đường cố định và công thức chia cắt cơ học mới đảm bảo tính nhất quán của kênh.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Chuyển sang 4 pha chức năng `narrative_phase` (`lived_friction`, `empirical_conflict`, `structural_model`, `actionable_resolution`) trong `visual_quality.py` và `content-v3.json`; (2) mở rộng cửa sổ Cold Open hợp lệ thành `3–5` beat trong `[0, 5s)` và `6–10` beat trong `[0, 12.5s)`; (3) điều biến `tone` động qua `_infer_scene_tone()` và khớp câu `coverage` theo độ chồng lấp ngữ nghĩa qua `_select_best_coverage_quote()`; (4) xoay vòng 4 hướng camera (`push_in`, `pan_right`, `pull_back`, `pan_left`, `entropy >= 1.5` bits) và hỗ trợ `allow_expression_shift` cùng trang phục linh hoạt trên Flow prompt `1.3.0`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Kiểm định cấu trúc kể chuyện bằng **pha chức năng nhận thức** (`narrative_phase`), **độ đa dạng không gian** và **entropy nhịp điệu/camera**, tuyệt đối không khóa cứng danh từ phòng ốc hay công thức chia cắt cơ học.

### [ERR-20261017-06] Đồng Bộ Giọng Đọc Duy Nhất `VietNarrator` (`1.0x`) & Gỡ Xung Đột `resolve_tone_speed` vs `remote_checks`
- **Triệu chứng (Symptom):** Kết quả âm thanh từ Colab trả về bị chặn bởi `Blocked('REMOTE_VOICE: effective request rate differs from contract')` khi phân cảnh có `tone` (`narrative_warm`, `analytical_crisp`, `reflective_slow`), hoặc các công cụ thượng nguồn ghi đè giọng mặc định `VietNarrator` (`1.0x`) của `config.json` bằng cấu hình cũ.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_colab_tts.py sys/tests/test_research_story_architect.py sys/tests/test_full_frame_pipeline.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** (1) `protocol.py:build_request` nhân tốc độ gốc `1.0` với hệ số `tone` (`0.98`, `1.02`, `0.92`) trong khi `pilot.py:remote_checks` và `media_packaging.py` kiểm tra cứng `item['speed'] == expected_voice['speed']`; (2) `research_story_architect.py` và `build_full_frame_acceptance.py` gán cứng tham số giọng cũ làm lệch cấu hình `sys/config.json`.
- **Giả định sai (Wrong Assumptions):** Giả định mọi câu thoại trong `request['items']` đều giữ nguyên tốc độ danh định `1.0` bất kể phân cảnh có điều biến `tone`.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Xóa toàn bộ định nghĩa giọng cũ, hợp nhất 100% sang `VietNarrator` (`assets/voices/viet_narrator/profile.json`, `speed: 1.0`, dải hợp lệ `[0.90, 1.15]`) trên cả `vi` và `en`; (2) lưu `base_speeds` trong `request`, đối chiếu `allowed_speeds` qua `resolve_tone_speed()` tại `pilot.py:remote_checks` và `protocol.py:validate_result`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Chỉ sử dụng duy nhất giọng đọc `VietNarrator` (`speed: 1.0`) xuyên suốt `sys/config.json`, `format_profiles.py` và các script tạo kịch bản; mọi bước hậu kiểm TTS phải chấp nhận tập tốc độ điều biến theo `TONE_SPEED_MULTIPLIERS`.

### [ERR-20261018-01] Khử Rung Giật & Triệt Tiêu Chu Kỳ Lặp Lại Của Camera Remotion
> Camera playback guidance in this historical entry is superseded by ERR-20261018-02. Retain it as the record of an insufficient first mitigation.
- **Triệu chứng (Symptom):** Video xuất xưởng có cảm giác chuyển động camera bị giật (micro-stutter) ở mép các nhịp beat, chuyển động rung cầm tay gây nhòe/shimmer điểm ảnh, đồng thời các chuyển động camera bị lặp đi lặp lại một khuôn mẫu nhàm chán sau mỗi 4 nhịp.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_renderer_effects.py -k test_camera_variety_and_sequence_constraints` và kiểm tra chuyển động camera trong `sys/renderer/index.tsx` và `sys/renderer/camera.mjs`.
- **Nguyên nhân cốt lõi (Root Cause):** (1) Đường cong easing cũ `bezier(0.33, 1, 0.68, 1)` có đạo hàm vận tốc lớn ngay tại điểm cắt beat; (2) `organicNoise` cầm tay có tần số cao cộng thêm xoay vi mô `microRot` (0.18°) và pha rung nhảy giật theo `active` beat; (3) Cú `punch_in` đàn hồi nảy biên độ lớn (1.22→1.08) và rung 14px; (4) Fallback camera chỉ xoay vòng 4 kiểu cơ học theo công thức `(seed + beatIndex * 3) % 4` với biên độ cứng nhắc (zoom 8%, pan 3%).
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng xoay vi mô và rung tần số cao mô phỏng chân thực camera cầm tay mà không nhận ra resample điểm ảnh tĩnh gây lấp lánh (pixel shimmer/jitter), và cho rằng công thức `% 4` đủ đa dạng mà không kiểm soát chu kỳ lặp và sự chênh lệch biên độ theo nhịp.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Đổi sang đường cong easing đối xứng êm ái hai đầu vận tốc bằng 0 (`bezier(0.42, 0, 0.58, 1)` v.v.); (2) Chuyển rung camera thành trôi chậm hữu cơ vô cực (tần số thấp ~0.1Hz, biên độ $\le 1.2$px, pha trôi liên tục theo thời gian thực `t`, loại bỏ triệt để `microRot`); (3) Overdamp cú `punch_in` (damping 26, scale 1.14→1.06, rung 5px suy giảm theo $t^2$); (4) Mở rộng pool 8 kiểu chuyển động (`zoom_in`, `zoom_out`, `pan_left`, `pan_right`, `pan_up`, `pan_down`, `drift_diag_in`, `drift_diag_out`), chọn theo shuffle-bag seed triệt tiêu lặp lại trong cửa sổ 3 nhịp và chặn 2 cú zoom cùng chiều liên tiếp; (5) Hàm `cameraVariation` băm xác định theo seed sinh biên độ zoom/pan và đường cong bezier mềm mại biến thiên theo từng beat.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi chuyển động camera trên ảnh tĩnh phải đạt vận tốc tiệm cận 0 tại hai đầu chuyển cảnh, cấm áp dụng biến đổi xoay vi mô `rotate()` gây vỡ hạt/shimmer điểm ảnh, và chu kỳ camera dự phòng phải dùng bộ chọn shuffle-bag có cửa sổ khử lặp $\ge 3$ nhịp với biên độ điều biến theo seed.

### [ERR-20261018-02] Calm Camera Playback and Composition Continuity
- **Triệu chứng (Symptom):** Zoom pumping and framing jumps persist after reducing amplitudes and disabling breathing drift, particularly at rapid variation cuts.
- **Tái hiện E2E (Reproduction Path):** Run `sys/.venv/bin/python -m pytest sys/tests/test_full_frame_pipeline.py sys/tests/test_renderer_effects.py -q`. Sample the executable camera path at 24/30/60 fps, including a base image followed by variations at 1.15s and 2.19s with conflicting directions and focal origins. This proves trajectory contracts, not rendered-media comfort.
- **Nguyên nhân cốt lõi (Root Cause):** Per-beat camera time and randomized amplitudes reset at each image; punch bypasses velocity caps with a spring and shake; outgoing dissolves reuse incoming transforms and framing. Camera-intent diversity was treated as a requirement to move on every beat.
- **Giả định sai (Wrong Assumptions):** Lowering individual amplitudes or adding GPU transform hints guarantees visual comfort; alternating camera directions prevents pumping; zero endpoint velocity alone prevents a positional jump between two different camera paths.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Use a deterministic composition-level calm plan: hold short (<2.4s), macro and diagram shots; suppress pans/slides/shake and full-frame line-boil; map punch to a gentle push with <=1.5% zoom and <=0.004/s peak scale velocity including overscan. Share time/focal origin/framing across variations, retain outgoing dissolve framing and enforce 4s rest across scene boundaries. Regression tests execute the real shared camera module, test seek order, boundary continuity and speed. Real Flow image quality and remote MP4 comfort still require visual acceptance after rerendering.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Keep authored semantic diversity separate from executed motion. Plan camera movement over a continuous composition, budget peak velocity after easing, and test positional continuity at edits. Never certify perceptual smoothness from unit tests alone.


### [ERR-20261018-03] Format-aware narration pause planning
- **Triệu chứng (Symptom):** Explicit-output jobs insert 0.50 s after every sentence and 0.70 s after scenes; the sampled long WAV spends 18.9% on inserted silence despite calibrated settings in config.
- **Tái hiện E2E (Reproduction Path):** Inspect saved request segments and WAV padding; run `pytest sys/tests/test_narration_pauses.py sys/tests/test_colab_worker.py`. Synthetic-model PCM proves assembly, not listening quality.
- **Nguyên nhân cốt lõi (Root Cause):** Only legacy tts_pause was consumed; calibrated fields were unused and secondary tracks bypassed sentence planning.
- **Giả định sai (Wrong Assumptions):** Adding config values changes runtime timing, SC01 forbids all automatic breaths, or an image cut requires a voice pause.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Implement format_v1 in format_profiles/narration_pauses, route both languages, preserve authored tags/learner holds and include per-boundary provenance in request identity. See [acceptance plan](sys/docs/narration-pause-implementation-plan.md); real-media acceptance remains pending.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Resolve pause policy from language outputs, count each boundary once, keep legacy snapshots immutable and verify PCM before claiming timing; listening is required before claiming naturalness.

### [ERR-20261018-04] Bound Colab download path fallback
- **Triệu chứng (Symptom):** Three transport regressions fail because a broad download exception handler doubles collection attempts, including timeouts.
- **Tái hiện E2E (Reproduction Path):** Run `pytest sys/tests/test_colab_tts.py sys/tests/test_remote_render.py sys/tests/test_colab_download_paths.py`; the pre-fix recovery-limit test observes six calls instead of three.
- **Nguyên nhân cốt lõi (Root Cause):** Absolute-to-relative path fallback catches every exception instead of distinguishing a confirmed missing-file response from an uncertain operation outcome.
- **Giả định sai (Wrong Assumptions):** Any download failure means the path syntax is wrong and is safe to retry immediately.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Classify sanitized missing-file errors and share one typed download helper for TTS/render. Only a confirmed missing file under /content permits one relative-path retry; other failures preserve the original recovery contract. Tests use isolated transport fixtures, not live Colab observations.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Never multiply durable retry budgets on timeouts, auth/session failures or unknown errors; fallback requires a specific, observed path error.

### [ERR-20261018-07] Light-value 2D stick figures and moderately simplified backgrounds
- **Symptom:** Images retain the requested stick-figure style but look dark, heavy and cluttered; even bright rooms use strong black outlines and many small background objects.
- **Reproduction Path:** Inspect the eight historical images and saved prompts in the visual-tone audit; compare six genuine Flow recreations under sys/runs/soft-pastel-style-review-20261018. Run pytest sys/tests/test_soft_visual_style.py and the prompt/full-frame/remote suites.
- **Root Cause:** Registry 1.3.0 repeats heavy black contour instructions, muted colors do not imply light values, references encode dark clothes, and scene descriptions encourage exhaustive environments. Renderer vignette adds another dark treatment.
- **Wrong Assumptions:** Stick figures require thick black outlines; shorter prompts or lower saturation alone guarantee simplicity; improving appearance requires photorealism or a fixed room/palette.
- **Resolution & E2E Proof:** Add immutable registry 1.4.0, shared authoring defaults, finer/lighter background linework, light-value colors and optional style references. Preserve full-frame/reference/text contracts and legacy pins. Route the explicit new treatment through hashed remote requests and props to suppress vignette/grain. Six real Flow images with sidecars were downloaded and visually inspected; night remains intentionally darker. Unit tests verify contracts, not user aesthetic acceptance or a real rerendered MP4.
- **Golden Rule:** Keep 2D anonymous stick figures and story-specific settings. Simplify secondary detail, preserve the focal action and use restrained contours/light values. Verify actual provider images; never rewrite historical registries or certify perception from fixtures.

### [ERR-20261018-08] Isolate both Flow transport branches in integration fixtures
- **Symptom:** Legacy prompt-integration fixtures record zero mocked sends and can fall through to a real signed-in Flow browser when no session socket exists.
- **Reproduction Path:** Run test_flow_prompt_integration with the socket transport mocked while the direct fallback is unguarded. The old fixture does not intercept that alternate boundary.
- **Root Cause:** The bridge gained a direct CDP fallback after tests were authored against only the socket sender. A new capability import also sat inside the no-reference branch, leaving attached-reference requests without the symbol.
- **Wrong Assumptions:** Mocking the old sender isolates every provider path, or exercising only the no-reference branch covers reference routing.
- **Resolution & E2E Proof:** Use a private fixture Unix socket and an explicit failing guard on real direct dispatch. Retain the real compiler, adapter, before-send checks and fake response boundary. Move capability imports before all reference branches; verify old/new pins, attached-reference variations, saved replay and tamper refusal in the integration suite.
- **Golden Rule:** Test providers fail closed at every alternate transport boundary. Treat fixture images as contract evidence only, and cover optional-reference branches whenever prompt capabilities change.

### [ERR-20261018-09] Preserve machine-readable CI evidence through gh-axi
- **Symptom:** Station 6 rejects successful GitHub Actions runs as unreadable despite a clean committed tree and green checks.
- **Reproduction Path:** Compare gh-axi api output for the head commit with json.loads: nonempty run arrays are emitted as TOON tables, not JSON. The empty-array case hides the mismatch.
- **Root Cause:** The certification code assumes --full selects JSON; it actually preserves field values while retaining TOON formatting.
- **Wrong Assumptions:** A successful API command or visible green check guarantees machine evidence can be decoded, or only the first passing run needs validation.
- **Resolution & E2E Proof:** Request an explicit jq @base64 envelope, decode strictly, then apply the unchanged all-runs/exact-commit/success validation. Regression coverage preserves pending runs and rejects malformed/TOON envelopes; live API results confirm the envelope works.
- **Golden Rule:** Separate display formatting from the machine evidence protocol. Never weaken CI validation to obtain a certificate.
