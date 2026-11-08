# Video Pilot — Historical Playbook Archive

This file archives older or superseded PLAYBOOK.md entries to keep `PLAYBOOK.md <= 200` lines.

### [ERR-20261018-10] Preserve Flow submission evidence across failures
- **Symptom:** Direct transport errors rewrote requests as not_submitted, and profile failover could send the same unresolved generation again.
- **Reproduction Path:** Run test_repository_checkpoint and test_multi_profile_manager with socket loss, provider refusal and partially completed batch fixtures.
- **Root Cause:** A transport wrapper edited engine journals, string matching treated post-send failures as pre-send, and a single unsent patch could classify a mixed batch as wholly unsent.
- **Wrong Assumptions:** A missing download proves generation was never submitted, or provider refusal makes account rotation safe.
- **Resolution & E2E Proof:** Let the engine own journal transitions; require explicit pre-send evidence, preserve ambiguous/partial batches, stop provider refusals and do not repeat their RPC. Disabled profiles return without waiting. Offline regressions verify no journal mutation or duplicate dispatch.
- **Golden Rule:** Reconcile the original request on its owner; see the Flow submission-safety reference. Never infer non-submission from error wording or missing media.

### [ERR-20261018-11] Preserve measured anchors when smoothing visual holds
- **Symptom:** A pacing repair moved image cuts away from measured word timestamps while still labeling the result acoustic.
- **Reproduction Path:** Run test_repository_checkpoint with measured anchors and densely spaced interpolated fallback beats.
- **Root Cause:** The smoothing loop moved every beat and forced an opening-density target without respecting the timing source.
- **Wrong Assumptions:** Meeting hold limits justifies altering measured speech alignment.
- **Resolution & E2E Proof:** Smooth only narration_anchor_interpolated beats, retain original estimates when adjusted and leave measured conflicts visible to validation. Restore the 0.83-second body minimum.
- **Golden Rule:** Measured timing is authoritative; repair the authored plan when real anchors cannot satisfy visual pacing.

### [ERR-20261018-12] Separate blueprint source from active job state
- **Symptom:** Production builders could overwrite initialized run inputs; source tests depended on unpublished live runs and media.
- **Reproduction Path:** Run source-factory validation, active-run export refusal and the production suites. Run media_acceptance separately against genuine local outputs.
- **Root Cause:** Source exports, mutable execution state and delivered media shared assumptions about directory ownership.
- **Wrong Assumptions:** A valid blueprint may be copied over an active job, or CI should contain local production MP4 files.
- **Resolution & E2E Proof:** Default source exports to blueprints, reject active-job destinations, read committed blueprint fixtures and explicitly separate real-media acceptance. Existing thumbnail/MP4 checks pass against local files without publishing them.
- **Golden Rule:** Use official job author/revision operations for live executions; source CI and genuine media acceptance remain separate evidence.

### [ERR-20261018-04] Bound Colab download path fallback
- **Triệu chứng (Symptom):** Three transport regressions fail because a broad download exception handler doubles collection attempts, including timeouts.
- **Tái hiện E2E (Reproduction Path):** Run `pytest sys/tests/test_colab_tts.py sys/tests/test_remote_render.py sys/tests/test_colab_download_paths.py`; the pre-fix recovery-limit test observes six calls instead of three.
- **Nguyên nhân cốt lõi (Root Cause):** Absolute-to-relative path fallback catches every exception instead of distinguishing a confirmed missing-file response from an uncertain operation outcome.
- **Giả định sai (Wrong Assumptions):** Any download failure means the path syntax is wrong and is safe to retry immediately.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Classify sanitized missing-file errors and share one typed download helper for TTS/render. Only a confirmed missing file under /content permits one relative-path retry; other failures preserve the original recovery contract. Tests use isolated transport fixtures, not live Colab observations.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Never multiply durable retry budgets on timeouts, auth/session failures or unknown errors; fallback requires a specific, observed path error.


### [ERR-20261017-02] Xuất Bản Đa Nền Tảng (`vp-omni-platform`) & Giữ Khóa Profile Flow CDP
- **Triệu chứng (Symptom):** Sinh trùng ảnh giữa các tỷ lệ khung hình hoặc mất liên kết profile trình duyệt cố định khi chạy đồng thời các tác vụ ảnh.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_omni_platform.py sys/tests/test_flow_cdp_bridge.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Tách rời `jobId` khỏi `testCase` khi gửi qua bridge và chưa tái sử dụng ảnh chung cho các bản xuất đa nền tảng.
- **Giả định sai (Wrong Assumptions):** Cho rằng `testCase` ID đại diện cho `jobId` và một trình duyệt cố định có thể nhận nhiều hàng đợi UI song song.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Truyền tường minh `jobId` qua bridge, tuần tự hóa khi khóa vào 1 profile (`sequential_close`) và đóng gói xuất bản đa nền tảng qua `sys/omni_platform.py`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Bảo toàn định danh `jobId` và quyền sở hữu trình duyệt xuyên suốt vòng đời job; tuân thủ [Omni-platform contracts](../../vp-omni-platform/SKILL.md).


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
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Implement format_v1 in format_profiles/narration_pauses, route both languages, preserve authored tags/learner holds and include per-boundary provenance in request identity. See [acceptance plan](../../../../sys/docs/narration-pause-implementation-plan.md); real-media acceptance remains pending.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Resolve pause policy from language outputs, count each boundary once, keep legacy snapshots immutable and verify PCM before claiming timing; listening is required before claiming naturalness.


### [ERR-20261023-02] Giọng Đọc Nhỏ & Thì Thầm Trên TikTok, Tăng Âm Lượng Bị Phô (AUDIO_MASTERING)
- **Triệu chứng (Symptom):** Narration đăng TikTok nhỏ hơn hẳn video khác, cảm giác thì thầm; tăng âm lượng thì giọng bị phô/gắt.
- **Tái hiện E2E (Reproduction Path):** Master `sys/assets/voices/viet_narrator/sample.wav` với chuỗi cũ ở `audio_lufs=-11`: chỉ đạt -12.4 LUFS, dải >3 kHz thấp hơn toàn dải ~25 dB.
- **Nguyên nhân cốt lõi (Root Cause):** OmniVoice tối & nhiều hơi; chuỗi cũ còn cắt -2.5 dB ở 7 kHz và không có compressor, crest factor cao khiến limiter phải ép mạnh (phô) mà vẫn không đạt target; target -14 LUFS quá nhỏ cho TikTok.
- **Giả định sai (Wrong Assumptions):** Cho rằng chỉ cần limiter là đạt loudness mà giữ được ngữ điệu; cho rằng mọi nền tảng đều tự chuẩn hóa về -14 LUFS.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** `audio_processing.VOICE_CHAIN` (highpass 80, -2 dB@250, +3.5 dB@3.2k, deesser, 2 tầng acompressor nhẹ) + vòng hiệu chỉnh gain sau limiter; một cấu hình duy nhất `sys/config.json` `audio_lufs=-11`, `audio_peak_db=-1.0` cho mọi format. Mẫu thật: -11.7 LUFS, -1.1 dBTP, khoảng cách dải cao 16.4 dB; frame giữ nguyên; 116 tests pass; người dùng nghe và chốt.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Một giọng, một cấu hình mastering trong `config.json`; không tách loudness theo nền tảng; luôn đo LUFS/TP/dải cao trên giọng thật trước khi đổi chuỗi.

### [ERR-20261018-05] Điều Tiết Nhịp Giữ Beat Hình Toàn Khung (Body Visual Hold Smoothing)
- **Triệu chứng (Symptom):** Lỗi `VISUAL_HOLD_INVALID` từ chối render khi nhịp beat rơi vào cụm từ quá ngắn (`SC06_B4 holds 0.440s < 0.80s`) hoặc câu đơn dài (`SC07_B4 holds 3.811s > 3.80s`) dù kịch bản và audio đạt chuẩn.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_full_frame_upgrade.py -k test_acceptance_package_has_valid_anchors_and_meets_estimated_density`.
- **Nguyên nhân cốt lõi (Root Cause):** `scripts/story_plan.py:timeline` ánh xạ trực tiếp mốc từ âm học sang thời điểm đổi hình mà không điều tiết vi mô (smoothing) để bảo toàn khoảng giữ tối thiểu và tối đa thân bài (`0.80s–3.80s`).
- **Giả định sai (Wrong Assumptions):** Giả định mọi mốc ngắt câu tự nhiên đều sinh ra khoảng giữ beat hình nằm gọn trong dải `[0.80s, 3.80s]` mà không cần kiểm soát ràng buộc biên.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Tích hợp thuật toán điều tiết nhịp giữ thân bài (`start >= 15s`) trong `scripts/story_plan.py`, tự động vi điều chỉnh mốc beat theo dải mục tiêu `[0.85s, 3.75s]` bảo toàn mốc `at = 0`, thứ tự hình ảnh và chống va chạm ở 30fps. Kiểm chứng 54/54 test pytest đạt 100% green và render video 16:9 `feynman-jargon-trap-16x9` thành công trên Colab T4.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi thuật toán sinh timeline thị giác từ audio/văn bản phải tích hợp bước điều tiết nhịp giữ (Hold Smoothing), bảo đảm $0.80\text{s} \le \text{hold} \le 3.80\text{s}$ trên thân bài trước khi chuyển sang renderer.

### [ERR-20261018-06] Điều Tiết Nhịp Giữ Cảnh Chuyển Tiếp Biên & Bảo Đảm Mật Độ Cold Open
- **Triệu chứng (Symptom):** Lỗi `VISUAL_HOLD_INVALID` ở cảnh chuyển tiếp vắt qua mốc 15s (`SC02_B3 holds 0.700s`), `OPENING_VISUAL_DENSITY` thiếu beat ở 5s đầu (`got 2`), và `LOW_VISUAL_BEAT_DENSITY` ở cảnh thân bài dài 6 beat.
- **Tái hiện E2E (Reproduction Path):** Chạy `check_see_say_beat_density(scenes)` trên timeline có câu mở đầu tự nhiên kéo dài qua 5s hoặc cảnh bắt đầu trước 15s nhưng kết thúc sau 15s.
- **Nguyên nhân cốt lõi (Root Cause):** (1) Logic điều tiết hold cũ chỉ kích hoạt khi `start >= 15s` nên bỏ sót cảnh vắt qua mốc 15s (`start < 15s, end > 15s`); (2) Thoại tự nhiên 2 câu đầu có thể dài quá 5.0s nếu không chủ động phân phối beat 3; (3) `MAX_AVERAGE_HOLD_SECONDS = 2.8s` quá hẹp so với trần giữ hình 3.80s của thân bài.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng phân cảnh mở đầu câu thoại tự nhiên luôn rơi vào trước 5s và chỉ những cảnh có `start >= 15s` mới cần kẹp hold.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Đổi điều kiện kẹp hold sang `end > 15s` trong `story_plan.py`; (2) Tự động điều tiết beat 3 mở đầu rơi vào trước 5s khi `start == 0.0`; (3) Nâng `MAX_AVERAGE_HOLD_SECONDS` lên 3.0s trong `visual_pacing.py`. Đã kiểm chứng render thành công video 9:16 `reviewer-2-nobel-rejections-9x16` (136.85s, 1080x1920) trên Colab T4 NVENC.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Thuật toán timeline phải kiểm tra điều tiết biên trên toàn bộ phân cảnh vắt qua mốc thân bài (`end > 15s`), chủ động bảo đảm mật độ Cold Open 3 beat trong 5s đầu và đồng bộ trần mật độ trung bình với độ dài phân cảnh thực tế.

### [ERR-20261018-07] Visual style and CI verification lessons
- **Triệu chứng (Symptom):** Heavy visual treatment, provider fixture leakage and unreadable CI evidence.
- **Tái hiện E2E (Reproduction Path):** Run style, prompt integration and full-frame upgrade suites.
- **Nguyên nhân cốt lõi (Root Cause):** Repeated heavy-line prompts, an unguarded transport fallback and TOON/JSON confusion.
- **Giả định sai (Wrong Assumptions):** Prompt text proves quality, one mocked sender isolates all transport, or --full forces JSON.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Version the light style, close every fixture boundary and decode a strict CI envelope. Full original ERR-07/08/09 records are preserved in [the extracted reference](../../vp-development/references/visual-ci-regressions.md).
- **Quy tắc phòng ngừa vàng (Golden Rule):** Inspect real media and retain exact transport/CI provenance; never infer success from fixture artifacts.


### [ERR-20261018-16] Chốt Chặn Sớm Sáo Rỗng Thị Giác (FLOW_CLICHE_FORBIDDEN)
- **Triệu chứng (Symptom):** Lỗi `FLOW_CLICHE_FORBIDDEN` (như split screen/brain cutaway) bị phát hiện quá muộn tại trạm sinh ảnh sau khi đã duyệt kịch bản và tổng hợp xong toàn bộ audio WAV.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_early_visual_cliche_gate.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Khâu duyệt `validate_content`/`validate_plan` và dựng cảnh `build_scenes_from_story_rows` chỉ kiểm tra cấu trúc/nhãn mà không đối chiếu từ khóa sáo rỗng trong `setting`, `action`, `description`, `preserve`, `change`, `visible_text`, `style` và `characters`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng linter prompt ở `image_pipeline.py` là đủ an toàn mà không tính đến chi phí token/TTS bị lãng phí khi crash muộn tại khâu ảnh.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Xuất `find_visual_cliche` và `check_visual_prompt_text` tại `flow_prompts`; chặn sớm lỗi `FLOW_CLICHE_FORBIDDEN` ngay tại `content_contract.py`, `story_plan.py`, `research_story_architect.py`, và `script_diversity_linter.py`. 27/27 tests early gate và test suite sản xuất pass 100%.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi ràng buộc từ khóa cấm của prompt AI phải được kiểm tra và chặn ngay từ khâu phê duyệt bản thảo nội dung (`content`); không bao giờ để lọt lỗi prompt xuống khâu sinh ảnh.

### [ERR-20261018-17] Khóa Sở Hữu Ảnh Phụ Thuộc & Cách Ly base_media_id Xuyên Profile
- **Triệu chứng (Symptom):** Lỗi `M2_FLOW: Pinned request ownership cannot be changed` khi sinh hoặc retry ảnh biến thể (`based_on`), khiến pipeline ảnh bị nghẽn.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_multi_profile_manager.py sys/tests/test_flow_cdp_bridge.py sys/tests/test_patch_partitioner.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Profile Google Flow cách ly ID dự án; chia patch lớn làm rớt ảnh con sang worker khác; failover chuyển ảnh con mang `base_media_id` ngoại lai; sidecar thiếu `profile_id`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng `forgeId` có giá trị toàn cục giữa các Chrome profile và patch có thể tùy ý failover sang profile khác.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Giữ chuỗi phụ thuộc nguyên tử qua `dependency_group_id`/`depends_on_patch_id`; cấm failover cho ảnh con phụ thuộc; điều phối DAG tuần tự khóa worker; ghi nhận và kế thừa `profile_id` qua sidecar `.json`. 43/43 tests pass 100%.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Ảnh phụ thuộc (`based_on`) phải gắn chặt vào profile của ảnh cha; tuyệt đối không chuyển giao ảnh phụ thuộc sang profile khác.

### [ERR-20261018-18] Tự Động Đối Soát Request Flow & Đồng Bộ Sổ Cái Ngân Sách (FLOW_BUDGET & M2_AMBIGUOUS)
- **Triệu chứng (Symptom):** Khi gặp timeout, mất kết nối websocket hoặc provider từ chối, pipeline ảnh bị kẹt vòng lặp `M2_AMBIGUOUS: reconcile request <key> before another submission` và `FLOW_BUDGET: Existing request: collect/reconcile, never resubmit`, treo cứng job chờ can thiệp thủ công.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_flow_auto_reconcile.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Khâu gỡ kẹt `reconcile_stuck_conflict()` chỉ ghi `request.json` cục bộ mà không gọi `flow_management.sync()` để cập nhật sổ cái `budgets.json`; ảnh đã tải về đĩa không được tự động đối soát sang `downloaded`; các lỗi tiền gửi (captcha, no at token, transport close) bị đánh nhãn sai thành `ambiguous`; lệnh `flow-reconcile` bắt buộc phải có `--asset`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng cập nhật `state: not_submitted` trên file request là đủ mà không nhận ra `account_budget.py` kiểm tra độc lập trên `budgets.json`; giả định mọi timeout đều đã gửi thành công lên máy chủ.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Bổ sung `auto_reconcile_attempt()` tự động xác nhận ảnh đã tải về đĩa; gắn cờ `generation_submitted = False` cho lỗi rớt mạng/tiền gửi; gọi `flow_management.sync()` trong mọi nhánh đối soát; cho phép `flow-reconcile` giải tỏa `not_submitted` kèm ảnh chụp bằng chứng UI khi không có asset. 5/5 test auto-reconcile và toàn bộ 37/37 test images v2 pass 100%.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi thay đổi trạng thái request (downloaded, not_submitted) phải lập tức đồng bộ sang sổ cái `budgets.json` qua `flow_management.sync()`; lỗi trước khi gửi phải ghi nhận `not_submitted` để không gây kẹt đối soát.

### [ERR-20261019-01] Tự Điều Tiết Số Tab Chrome & Đảm Bảo Vòng Đời Dọn Dẹp RAM (LIFECYCLE_TEARDOWN & ADAPTIVE_WORKERS)
- **Triệu chứng (Symptom):** Tạo ít ảnh (1–3 ảnh) vẫn mở cố định 10 tab Chrome ngốn ~7GB RAM; khi pipeline kết thúc hoặc crash, các tiến trình Chrome tiếp tục chạy ngầm làm nghẽn tài nguyên máy chủ.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_flow_lifecycle.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Hệ thống không phân bậc khối lượng công việc theo số lượng ảnh cần tạo và thiếu trình quản lý vòng đời theo dõi PID/cổng debug đã được mở để giải phóng.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng luôn mở tối đa số tab (10 tab) là tối ưu cho mọi tác vụ và hệ điều hành sẽ tự thu hồi RAM trình duyệt.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Xây dựng `calculate_optimal_workers` phân 5 bậc (Micro 1 tab, Short 2–3 tab, Chapter 3–5 tab, Standard 5–7 tab, Bulk 8–10 tab) và `ProfileLifecycleManager` đảm bảo nguyên tắc "mở bao nhiêu tắt bấy nhiêu", tích hợp trực tiếp vào `sys/image_pipeline.py`. 9/9 unit tests và thực nghiệm 300 ảnh pass 100%, giải phóng ~6.5GB RAM ngay khi xong.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Luôn tính toán số tab worker tối ưu theo khối lượng ảnh thực tế; mọi phiên sinh ảnh phải bọc trong `ProfileLifecycleManager` để đảm bảo dọn dẹp chính xác những tiến trình Chrome vừa mở mà không ảnh hưởng cửa sổ duyệt web của người dùng.

### [ERR-20261019-02] Tính Bất Biến Idempotent Của Hijack CDP Trên Window Tái Sử Dụng
- **Triệu chứng (Symptom):** Khi chạy batch ảnh liên tiếp trên cùng một tab Chrome, JS văng lỗi `TypeError: Cannot assign to read only property '__vp_cdp_hijack' of object '#<Window>'`.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_flow_cdp_resilience.py sys/tests/test_flow_cdp_bridge.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Khối `Object.defineProperty` khởi tạo `writable: false, configurable: false` trên `window.__vp_cdp_hijack`. Khi evaluate lại trên tab cũ, ném exception và nhánh `catch` cố gán lại thuộc tính read-only trong strict mode.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng mỗi batch evaluate luôn chạy trên ngữ cảnh window mới tinh mà không tính đến tab tái sử dụng.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Kiểm tra `if (!window.__vp_cdp_hijack)` trước khi define; đặt `writable: true, configurable: true`; bọc fallback gán trực tiếp trong `try...catch`. Đã kiểm chứng 12/12 unit tests đạt green.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi script tiêm vào window browser qua CDP phải bảo đảm tính idempotent, không định nghĩa thuộc tính read-only/non-configurable nếu trang có thể được evaluate nhiều lần.

### [ERR-20261023-01] Cô Lập Package sys/content/ & Guard Phụ Thuộc Chéo Giữa Core - Content - Images
- **Triệu chứng (Symptom):** Khi merge `module-content` vào `module-core` (đã tách các external engines), phát sinh 18 xung đột `modify/delete` và lỗi `ModuleNotFoundError: No module named 'visual_style'` / `'flow_prompts'` khi chạy bộ test của core.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_research_story_architect.py sys/tests/test_output_contract.py -v` trên môi trường chỉ có `module-core`.
- **Nguyên nhân cốt lõi (Root Cause):** `module-core` đã xóa các file engine khỏi `sys/tools/` và `sys/scripts/`, trong khi `module-content` cập nhật trực tiếp trên đường dẫn cũ và import cứng `visual_style` / `flow_prompts` thuộc `module-images`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng mọi module đều nằm chung một không gian phẳng `sys/tools/` và `visual_style` luôn tồn tại trong core.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Di chuyển toàn bộ `research_story_architect.py`, `visual_quality.py`, builders và blueprints vào package độc lập `sys/content/`; bọc import `visual_style` bằng guard `VISUAL_STYLE_AVAILABLE` và kiểm tra rõ ràng trong `ResearchedTopic.__post_init__`; dùng `pytest.importorskip` cho các test cần `module-images`. 183 passed trên core-only và 34/34 passed khi nạp kèm `module-images`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Giữ toàn bộ tài sản và bộ kiến trúc nội dung trong `sys/content/`; mọi tham chiếu sang module ngoại vi (`visual_style`, `flow_prompts`, `flow_dispatch`) phải qua lazy/guarded import để `module-core` luôn tự chủ.

### [ERR-20261023-03] Tăng Tốc Đa Luồng Mặc Định Toàn Trình Audio/TTS & Khắc Phục 5 Lỗi Biên Âm Học (PARALLEL_TTS_DEFAULT)
- **Triệu chứng (Symptom):** (1) `audio_pipeline.py` chạy tuần tự từng câu và crash `TypeError: Client.__init__()` khi gọi remote; (2) `normalize_for_tts` nuốt thẻ `[pause:800ms]` thành chữ `"tám trăm mi-li giây"` và `detect_unnormalized_tokens` tự từ chối từ phiên âm có gạch nối (`Xô-crát`); (3) `master()` nổ gain `+inf dB` trên file im lặng tuyệt đối (`input_i: "-inf"`); (4) `subtitles.py` và `worker.py` chồng lấn mốc phụ đề 10ms (`CAPTION_TIMELINE`).
- **Tái hiện E2E (Reproduction Path):** Chạy `PYTHONPATH=sys:sys/tools ./.venv/bin/pytest sys/tests/test_vn_text_normalizer_adversarial.py sys/tests/test_adversarial_m2.py sys/tests/test_colab_pool.py sys/tests/test_parallel_audio_pipeline.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** (1) Thiếu điều phối song song qua `ColabPoolDispatcher` trong `audio_pipeline.py` và `remote_audio.py`; (2) `vn_text_normalizer` biến đổi số trước khi bảo vệ thẻ `[pause:...]` và thiếu whitelist âm tiết phiên âm chuẩn; (3) `master()` lấy `-11.0 - (-inf) = +inf` khi sườn âm bằng 0; (4) làm tròn biên từ không kẹp `t[i].end <= t[i+1].start`.
- **Giả định sai (Wrong Assumptions):** Giả định `audio_pipeline.py` chỉ chạy mock đơn luồng, thẻ `[pause]` không chứa chữ số, file WAV đầu vào luôn có năng lượng âm thanh `> -70 LUFS`, và các mốc từ độc lập không bao giờ chồng lấn sau khi làm tròn.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Mặc định hóa chạy song song đa luồng (`parallel=True, max_workers=3, batch_size=4`) trong `AudioPipeline._synthesize_segments_parallel()` và `remote_audio.produce_parallel()` qua `ColabPoolDispatcher`; (2) bảo vệ thẻ `[pause:...]` trước khi chuẩn hóa số và bổ sung `CANONICAL_TRANSLITERATION_SYLLABLES`; (3) chặn ngưỡng `input_i <= -70.0` (`gain_db = 0.0`) trong `master()` và `nframes <= 0` trong `mix_sound_design()`; (4) kẹp đơn điệu không chồng lấn `a = max(cues[-1]['end'], a)` trong `subtitles.py` và `worker.py`. Đạt 399/399 tests green.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Chế độ mặc định của tổng hợp giọng đọc luôn là **tăng tốc đa luồng đa tài khoản Colab T4** kết hợp gom lô (`batch_size=4`); luôn bảo vệ thẻ điều khiển `[pause:...]` trước khi chuẩn hóa văn bản, kẹp gain an toàn với tín hiệu im lặng và ép đơn điệu chặt các mốc thời gian phụ đề.

### [ERR-20261024-01] Khôi Phục Biên Tích Hợp Đa Module (audio/images/video/content/core) & Chuẩn Hóa Flat 2D Nguệch Ngoạc 1.7.0
- **Triệu chứng (Symptom):** Sau khi hợp nhất các nhánh module vào core: (1) `remote_audio.produce` gửi toàn bộ 63 câu qua 1 phiên `Client.synthesize` đơn lẻ thay vì chia shard đa T4; (2) `cdp_direct_client.py` tự sửa prompt khi gặp `PUBLIC_ERROR_UNSAFE_GENERATION`, so chuỗi `'Profile 1'` đụng `'Profile 10'`, và đăng ký nhân vật 1.7.0 thiếu `has_character: True`; (3) `build_ai_sycophancy_9x16.py` nhét mô tả đèn ấm/quán cà phê (`pendant light`, `lamplight`, `glowing tablet`) khiến Flow sinh ảnh webtoon thay vì hoạt họa 2D phẳng kiểu `Nguệch Ngoạc`.
- **Tái hiện E2E (Reproduction Path):** Chạy `PYTHONPATH=sys:sys/tests pytest -q sys/tests/test_integration_recovery.py`.
- **Nguyên nhân cốt lõi (Root Cause):** Đường gọi `remote_audio.produce` chưa nối vào `colab_bridge.parallel_audio.synthesize`; `Client.synthesize` thiếu nhánh `reconcile() -> _ready(auto_start=True)` trước khi gửi; `flow_cdp/bridge.py` dùng `in` thay vì so khớp đường dẫn tuyệt đối; kịch bản `ai-sycophancy-9x16` viết `setting` tả thực nội thất thay vì nền màu phẳng 2D và thiếu nhãn `visible_text` đối lập trực quan.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng tương thích schema đồng nghĩa bảo toàn đường gọi đa tài khoản và phong cách hình ảnh; giả định thêm từ khóa tả thực ánh sáng không làm lệch compiler `1.7.0`.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Đóng băng `job_config`, ghi nhận `runtime.json` (`source_receipt`) và tách `technical_complete` khỏi `quality_approved`; (2) nối `parallel_audio.synthesize` vào `remote_audio.produce` kèm đối soát phiên `COLAB_SESSION_NOT_FOUND` và kiểm tra hash `support_files`; (3) bỏ sửa prompt ngầm, khớp chính xác `Path.resolve()` cho `Profile 1` vs `Profile 10`, truyền `has_character: True` trên 1.7.0; (4) hợp nhất `content/visual_quality.py` về `scripts/visual_quality.py`, khôi phục `human_editorial` trong `build_brief_v3`, và chuẩn hóa 12 cảnh / 97 beat `build_ai_sycophancy_9x16.py` sang nền màu phẳng 2D + nhãn in hoa đối chiếu theo chuẩn `Nguệch Ngoạc` (`IDk7jI83iYA`); (5) ghi `remotion_concurrency` và `stage_timings` trong `render.mjs`/`job_worker.py`. 11/11 tests tích hợp và 73/73 tests Flow/Workflow pass 100%.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Bảo toàn tuyệt đối biên hợp đồng của các module đã duyệt (`1.7.0` flat 2D explainer không tả thực đèn/nội thất, prompt bất biến khi lỗi, đa luồng T4 cho TTS, khớp chính xác đường dẫn profile, và tách bạch hoàn tất kỹ thuật với phê duyệt chất lượng).

### [ERR-20261025-01] Khử Lắp Bắp Âm Tiết Gạch Nối (vi-đê-ô), Rò Âm Mẫu Đầu Câu & Chặn Va Chạm Beat smooth_interpolated_beats
- **Triệu chứng (Symptom):** (1) Giọng đọc `OmniVoice` lắp bắp kéo dài khoảng lặng bất thường (`> 500ms`) giữa từ phiên âm có gạch nối (`"VI đê ...... ô"`), nuốt vế câu cuối hoặc dính âm mẫu `"định"` + `350–500ms` lặng ở đầu câu; (2) `smooth_interpolated_beats` đẩy `beats[10]` lên `12.55s` vượt qua `beats[11]` (`11.67s`) gây lỗi `Visual beats collide at 30 fps`.
- **Tái hiện E2E (Reproduction Path):** Chạy `PYTHONPATH=sys:sys/tools pytest sys/tests/test_colab_worker.py sys/tests/test_full_frame_upgrade.py -q` và nghe trực tiếp `narration.wav` của `SC01–SC02`.
- **Nguyên nhân cốt lõi (Root Cause):** (1) `vn_text_normalizer` xuất từ mượn có gạch nối liên chữ (`vi-đê-ô`) khiến BPE tokenizer của `OmniVoice` hiểu gạch nối là ranh giới ngắt nhịp prosody, đồng thời batch inference không tự retry khi có hố lặng nội câu hay rò âm cuối file mẫu tham chiếu; (2) `smooth_interpolated_beats` tịnh tiến `beats[10]` mà không kiểm tra `beats[11]['at']` khi `count > 11` và `end <= 15`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng gạch nối phiên âm chuẩn trên mặt chữ giúp TTS đọc mượt hơn, kiểm tra RMS thô đầu file đủ bắt rò âm mẫu sau đoạn zero-padding, và `smooth_interpolated_beats` không bao giờ làm đảo thứ tự mốc đo âm học.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Tách gạch nối liên chữ thành khoảng trắng trong `_normalize_vi_tts_text` của `worker.py`, cắt cụm rò âm mẫu đầu câu + bảo toàn âm đuôi mũi nhẹ trong `_trim_silence`, và thêm vòng chấm điểm âm học `_utterance_acoustic_score` tự retry `batch_size=1` khi hố lặng nội câu `> 380ms` hoặc rớt mật độ âm tiết; (2) thêm guard `count == 11 or OPENING_WINDOW_SECONDS + .05 <= beats[11]['at'] - .5` trong `sys/visual_pacing.py` và viết lại lời thoại thực tế `SC01–SC02`. Kiểm chứng tests green, `PLAYBOOK.md <= 200` dòng và nghe thực tế `narration.wav` sạch 100%.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Không truyền gạch nối liên âm tiết (`vi-đê-ô`) vào model TTS BPE; luôn kiểm định hậu kỳ bằng điểm âm học + nghe thực tế file WAV để bắt rò âm mẫu/nuốt vế, và mọi phép làm trơn beat phải bảo toàn tính đơn điệu nghiêm ngặt ở 30 fps.
