# Video Pilot — Sổ Tay Bài Học & Quản Trị Lỗi (PLAYBOOK)

> **Mục đích**: Lưu trữ quy tắc kỹ thuật cốt lõi và bài học vận hành hệ thống Video Pilot.
> **Quy chuẩn**: Mọi bài học ghi đủ **6 trường chuẩn hóa**. Luôn giữ `PLAYBOOK.md <= 200` dòng để bảo toàn hạn mức Token Quota; chi tiết dài đã được trích xuất vào `.agents/skills/`.

---

## I. Quy Trình 4 Bước Khắc Phục Lỗi Tối Thượng
$$\text{1. Tái hiện E2E} \longrightarrow \text{2. Phân tích gốc rễ} \longrightarrow \text{3. Sửa chuẩn kiến trúc} \longrightarrow \text{4. Kiểm chứng E2E & ghi Playbook}$$

---

## II. Danh Mục Bài Học & Sự Cố Chuẩn Hóa

> Historical entries [ERR-20261010-08], [ERR-20261010-09], [ERR-20261011-01], [ERR-20261011-05], [ERR-20261014-01], [ERR-20261016-02], [ERR-20261017-02], [ERR-20261017-03], and [ERR-20261017-04] are archived in .agents/skills/vp-troubleshooting/references/historical-playbook.md.

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
- **Symptom:** Heavy visual treatment, provider fixture leakage and unreadable CI evidence.
- **Reproduction Path:** Run style, prompt integration and full-frame upgrade suites.
- **Root Cause:** Repeated heavy-line prompts, an unguarded transport fallback and TOON/JSON confusion.
- **Wrong Assumptions:** Prompt text proves quality, one mocked sender isolates all transport, or --full forces JSON.
- **Resolution & E2E Proof:** Version the light style, close every fixture boundary and decode a strict CI envelope. Full original ERR-07/08/09 records are preserved in [the extracted reference](.agents/skills/vp-development/references/visual-ci-regressions.md).
- **Golden Rule:** Inspect real media and retain exact transport/CI provenance; never infer success from fixture artifacts.

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

### [ERR-20261018-13] Colab identity leases and truthful pool readiness
- **Symptom:** Jobs contend for a pinned runtime while unused profiles are reported ready; an unknown request loses its local runner lock.
- **Reproduction Path:** The 2026-10-18 audit verified 20 profiles but only 15 Google identities, one live T4, five duplicate profile pairs and an exhausted preferred-account budget. Independent controllers reproduce the duplicate-alias race with real file locks.
- **Root Cause:** Production replaced auto-idle selection with the selected default; selection and reservation were separate, locks used profile aliases, and token-file presence was counted as readiness.
- **Wrong Assumptions:** Each profile is a distinct Google account; a free local lock proves the remote session is free; an authenticated account already has available GPU capacity.
- **Resolution & E2E Proof:** Add a bounded health audit and identity-based atomic claims in the actual audio/render client. Preserve exact bindings and unresolved request journals, filter blocked/exhausted accounts and stagger allocations across controllers. Scheduler, transport ownership and dashboard regression tests pass; live audit and account-03 observation verify authentication/T4 response only, not a completed production request.
- **Golden Rule:** Count unique verified identities, distinguish auth/allocation/kernel readiness, and collect an unknown request only on its original owner before another send.

### [ERR-20261018-14] Auto-Reclaim Stale Leases & Worker Availability Resilience
- **Triệu chứng (Symptom):** Pipeline văng lỗi `No Chrome profile workers available` hoặc `JOB_RUNNING` khi tiến trình trước crash để lại file lock mồ côi, hoặc khi pool chỉ có 1 profile gặp lỗi tạm thời.
- **Tái hiện E2E (Reproduction Path):** Chạy `PYTHONPATH=sys pytest sys/tests/test_lock_and_worker_resilience.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Handle mở lock thiếu `FD_CLOEXEC` gây rò rỉ FD sang subprocess; `clean_stale_leases` không kiểm tra liveness PID chết; `replace_profile` nhả profile duy nhất khi pool không có profile thay thế.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng `flock` luôn tự động nhả khi crash mà không tính đến subprocess kế thừa FD; giả định pool luôn có profile rảnh để thay thế.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Thiết lập `FD_CLOEXEC` trên mọi lock handle; bổ sung kiểm tra `is_pid_alive` để tự động thu hồi lease của PID chết; bảo vệ lease profile đơn trong `replace_profile`; bổ sung `refresh_workers` và chẩn đoán pool vào `dispatch_all`. Đạt 63/63 test pytest 100% green.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Luôn gán cờ `FD_CLOEXEC` cho lock descriptor; kiểm tra liveness PID trước khi coi profile là bận; không bao giờ nhả lease của worker suy biến nếu chưa tìm được profile thay thế hợp lệ.

### [ERR-20261018-15] Khôi Phục Kết Nối Direct CDP & Chống Rơi WebSocket Hàng Đợi Ảnh
- **Triệu chứng (Symptom):** Hàng đợi sinh ảnh bị sập toàn bộ các futures khi WebSocket CDP đóng bất thường (`no close frame received or sent`) hoặc báo lỗi `Socket Not Found` (`/tmp/video-pilot-1000/flow-*.sock`) trước khi Chrome kịp khởi động.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_flow_cdp_resilience.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** Chrome thiếu cờ ngăn Background Throttling/Memory Saver/AutomaticTabDiscarding khiến renderer bị ngủ; client `websockets` dùng `ping_interval=20s` gây rớt kết nối giả 1006 khi trang xử lý nặng; `b2_bridge` gọi `query_status()` ném lỗi socket missing trước khối bọc khởi tạo; `evaluate()` không tự động kết nối lại khi rơi transport.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng kết nối CDP qua WebSocket luôn duy trì mà không cần tắt chế độ tiết kiệm bộ nhớ của Chrome; giả định lỗi transport giữa chừng là unrecoverable khiến batch ngừng retry.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Bổ sung 6 cờ Chrome ngăn discard/throttling; thiết lập `ping_interval=None, ping_timeout=None`; triển khai auto-reconnect trong `evaluate()`; gắn nhãn `retryable_pre_submit=True` khi đứt kết nối transport; bắt lỗi socket missing để tự động launch Chrome. 81/81 tests Flow CDP và 6/6 tests resilience pass 100%.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Luôn khởi chạy Chrome CDP với các cờ vô hiệu hóa Tab Discarding/Memory Saver; tắt websocket ping heartbeat mặc định trên CDP và cô lập lỗi transport pre-submit để kích hoạt retry/failover mượt mà.

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
### [ERR-20261023-01] Giọng Đọc Nhỏ & Thì Thầm Trên TikTok, Tăng Âm Lượng Bị Phô (AUDIO_MASTERING)
- **Triệu chứng (Symptom):** Narration đăng TikTok nhỏ hơn hẳn video khác, cảm giác thì thầm; tăng âm lượng thì giọng bị phô/gắt.
- **Tái hiện E2E (Reproduction Path):** Master `sys/assets/voices/viet_narrator/sample.wav` với chuỗi cũ ở `audio_lufs=-11`: chỉ đạt -12.4 LUFS, dải >3 kHz thấp hơn toàn dải ~25 dB.
- **Nguyên nhân cốt lõi (Root Cause):** OmniVoice tối & nhiều hơi; chuỗi cũ còn cắt -2.5 dB ở 7 kHz và không có compressor, crest factor cao khiến limiter phải ép mạnh (phô) mà vẫn không đạt target; target -14 LUFS quá nhỏ cho TikTok.
- **Giả định sai (Wrong Assumptions):** Cho rằng chỉ cần limiter là đạt loudness mà giữ được ngữ điệu; cho rằng mọi nền tảng đều tự chuẩn hóa về -14 LUFS.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** `audio_processing.VOICE_CHAIN` (highpass 80, -2 dB@250, +3.5 dB@3.2k, deesser, 2 tầng acompressor nhẹ) + vòng hiệu chỉnh gain sau limiter; một cấu hình duy nhất `sys/config.json` `audio_lufs=-11`, `audio_peak_db=-1.0` cho mọi format. Mẫu thật: -11.7 LUFS, -1.1 dBTP, khoảng cách dải cao 16.4 dB; frame giữ nguyên; 116 tests pass; người dùng nghe và chốt.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Một giọng, một cấu hình mastering trong `config.json`; không tách loudness theo nền tảng; luôn đo LUFS/TP/dải cao trên giọng thật trước khi đổi chuỗi.

### [ERR-20261023-02] Tăng Tốc Đa Luồng Mặc Định Toàn Trình Audio/TTS & Khắc Phục 5 Lỗi Biên Âm Học (PARALLEL_TTS_DEFAULT)
- **Triệu chứng (Symptom):** (1) `audio_pipeline.py` chạy tuần tự từng câu và crash `TypeError: Client.__init__()` khi gọi remote; (2) `normalize_for_tts` nuốt thẻ `[pause:800ms]` thành chữ `"tám trăm mi-li giây"` và `detect_unnormalized_tokens` tự từ chối từ phiên âm có gạch nối (`Xô-crát`); (3) `master()` nổ gain `+inf dB` trên file im lặng tuyệt đối (`input_i: "-inf"`); (4) `subtitles.py` và `worker.py` chồng lấn mốc phụ đề 10ms (`CAPTION_TIMELINE`).
- **Tái hiện E2E (Reproduction Path):** Chạy `PYTHONPATH=sys:sys/tools ./.venv/bin/pytest sys/tests/test_vn_text_normalizer_adversarial.py sys/tests/test_adversarial_m2.py sys/tests/test_colab_pool.py sys/tests/test_parallel_audio_pipeline.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** (1) Thiếu điều phối song song qua `ColabPoolDispatcher` trong `audio_pipeline.py` và `remote_audio.py`; (2) `vn_text_normalizer` biến đổi số trước khi bảo vệ thẻ `[pause:...]` và thiếu whitelist âm tiết phiên âm chuẩn; (3) `master()` lấy `-11.0 - (-inf) = +inf` khi sườn âm bằng 0; (4) làm tròn biên từ không kẹp `t[i].end <= t[i+1].start`.
- **Giả định sai (Wrong Assumptions):** Giả định `audio_pipeline.py` chỉ chạy mock đơn luồng, thẻ `[pause]` không chứa chữ số, file WAV đầu vào luôn có năng lượng âm thanh `> -70 LUFS`, và các mốc từ độc lập không bao giờ chồng lấn sau khi làm tròn.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Mặc định hóa chạy song song đa luồng (`parallel=True, max_workers=3, batch_size=4`) trong `AudioPipeline._synthesize_segments_parallel()` và `remote_audio.produce_parallel()` qua `ColabPoolDispatcher`; (2) bảo vệ thẻ `[pause:...]` trước khi chuẩn hóa số và bổ sung `CANONICAL_TRANSLITERATION_SYLLABLES`; (3) chặn ngưỡng `input_i <= -70.0` (`gain_db = 0.0`) trong `master()` và `nframes <= 0` trong `mix_sound_design()`; (4) kẹp đơn điệu không chồng lấn `a = max(cues[-1]['end'], a)` trong `subtitles.py` và `worker.py`. Đạt 399/399 tests green.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Chế độ mặc định của tổng hợp giọng đọc luôn là **tăng tốc đa luồng đa tài khoản Colab T4** kết hợp gom lô (`batch_size=4`); luôn bảo vệ thẻ điều khiển `[pause:...]` trước khi chuẩn hóa văn bản, kẹp gain an toàn với tín hiệu im lặng và ép đơn điệu chặt các mốc thời gian phụ đề.

