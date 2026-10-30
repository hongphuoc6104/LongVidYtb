# Video Pilot — Sổ Tay Bài Học & Quản Trị Lỗi (PLAYBOOK)

> **Mục đích**: Lưu trữ quy tắc kỹ thuật cốt lõi và bài học vận hành hệ thống Video Pilot.
> **Quy chuẩn**: Mọi bài học ghi đủ **6 trường chuẩn hóa**. Luôn giữ `PLAYBOOK.md <= 200` dòng để bảo toàn hạn mức Token Quota; chi tiết dài đã được trích xuất vào `.agents/skills/`.

---

## I. Quy Trình 4 Bước Khắc Phục Lỗi Tối Thượng
$$\text{1. Tái hiện E2E} \longrightarrow \text{2. Phân tích gốc rễ} \longrightarrow \text{3. Sửa chuẩn kiến trúc} \longrightarrow \text{4. Kiểm chứng E2E & ghi Playbook}$$

---

## II. Danh Mục Bài Học & Sự Cố Chuẩn Hóa

> Historical entries [ERR-20261010-08], [ERR-20261010-09], [ERR-20261011-01], [ERR-20261011-05], [ERR-20261014-01], [ERR-20261016-02], [ERR-20261017-02], [ERR-20261017-03], [ERR-20261017-04], [ERR-20261017-05], [ERR-20261017-06], [ERR-20261018-01], [ERR-20261018-02], and [ERR-20261018-03] are archived in .agents/skills/vp-troubleshooting/references/historical-playbook.md.

### [ERR-20261028-01] Chuẩn Hóa Chữ Sạch Không Trang Trí (Clean Unadorned Text) & Triệt Tiêu Clipart AI Trong Visual 2D
- **Triệu chứng (Symptom):** Người xem phản ánh khung hình mang nặng tính "AI clipart" khi chứa tấm thẻ (`white_card`), băng keo 4 góc, ruy băng uốn lượn, rác sao/confetti, và hình vẽ não giải phẫu y khoa nhiều màu lạc quẻ so với phong cách doodle tối giản.
- **Tái hiện E2E (Reproduction Path):** Đặt `shot_type: "white_card"` hoặc viết `"A neat card with text..."` trong kịch bản; compiler Flow sẽ kích hoạt NanoBanana vẽ viền bưu thiếp, băng dính và họa tiết trang trí phức tạp.
- **Nguyên nhân cốt lõi (Root Cause):** (1) Khái niệm thẻ (`card/banner`) khiến mô hình khuếch tán hiểu nhầm là thiệp chúc mừng/sticker và tự động bù đắp các chi tiết trang trí thừa thãi; (2) Thiếu khai báo `allowed_text` đồng bộ dẫn đến chữ méo mó; (3) Vẽ hình giải phẫu não người phá vỡ giao ước hình học tối giản của stickman 2D.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng đóng khung thẻ giúp chữ dễ đọc hơn, hoặc chỉ cần cấm text là giải quyết được độ sạch mà bỏ qua nhu cầu neo giữ từ khóa học thuật của người xem tri thức.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Chuẩn hóa công thức prompt chữ sạch: chữ viết tay mực đen mộc mạc floating tự do trên nền phẳng (`#FFFFFF`/`#F8F0DC`), cấm tiệt khung viền, băng keo, ruy băng, sao rác (`>= 70%` negative space); (2) Tự động trích xuất `allowed_text` từ dấu nháy đơn/kép trong description; (3) Thay não giải phẫu bằng thanh đo năng lượng/đồng hồ bấm giờ/stickman tập trung; (4) Sinh thực tế 21 ảnh mới đạt 100% không lỗi và kiểm chứng trích xuất frame từ MP4 render trên Colab T4.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Từ khóa trong khung hình phải là chữ viết tay tự nhiên không trang trí (Zero card borders, zero tape, zero banners, zero confetti); luôn kết hợp đúng 1 ẩn dụ chức năng đơn lẻ và thanh lọc toàn bộ hình vẽ giải phẫu y khoa.

### [ERR-20261025-02] Điều Tiết Nhịp Giữ Beat Hình Toàn Khung Cho Video Dài 16:9 (EXPLAINER_VISUAL_PACING)
- **Triệu chứng (Symptom):** Lỗi `COLAB_EXEC_UNCONFIRMED: VISUAL_PACING_FAILED` khi render video giải thích 16:9 (3–4 phút), báo `LOW_VISUAL_BEAT_DENSITY` (>3.0s/beat), `VISUAL_HOLD_INVALID` (>3.80s) và `OPENING_VISUAL_DENSITY` (<6 starts) dù kịch bản 10 cảnh / 40 beat đạt chuẩn chiều sâu.
- **Tái hiện E2E (Reproduction Path):** Chạy `pilot.py run survivorship-bias-16x9` với brief `long_16x9` có cảnh dài 14–19s và 4 visual beats.
- **Nguyên nhân cốt lõi (Root Cause):** (1) `visual_pacing.py` cố định các hằng số nhịp cắt nhanh của video ngắn (`MAX_AVERAGE_HOLD_SECONDS = 3.0s`, `BODY_MAX_HOLD_SECONDS = 3.80s`) áp đặt lên cả video dài 16:9; (2) `smooth_interpolated_beats` dùng trần cứng `maximum = 3.75s` ép beat đầu vào 11.25s và dồn khoảng trống 8.0s vào beat cuối.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng mọi video 16:9 đều phải đổi hình dồn dập 2–3s/beat như TikTok mà không tính đến tính chất tĩnh tại, lắng đọng của thể loại phân tích nhận thức 3–4 phút.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Nâng cấp `check_see_say_beat_density` hỗ trợ linh hoạt format `long_16x9` / explainer (trần TB 6.0s, trần thân 8.5s, mở đầu 2–5 beat); (2) Động hóa trần giãn beat `maximum = max(3.75, avg_hold * 1.35)` trong `smooth_interpolated_beats`; (3) Truyền `format_profile` vào `job_worker.py`. 1097/1097 test pass 100%, render thành công video 16:9 `survivorship-bias-16x9_r1_final.mp4` (169.64s, 1920x1080@30fps NVENC).
- **Quy tắc phòng ngừa vàng (Golden Rule):** Phân tách rõ ràng ngưỡng nhịp thị giác giữa video ngắn 9:16 (nhịp cắt nhanh) và video giải thích 16:9 (nhịp tĩnh tại, tập trung nhận thức); thuật toán làm trơn beat phải tự co giãn theo thời lượng thực tế của phân cảnh.

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

### [ERR-20261023-01] Cô Lập Package `sys/content/` & Guard Phụ Thuộc Chéo Giữa Core - Content - Images
- **Triệu chứng (Symptom):** Khi merge `module-content` vào `module-core` (đã tách các external engines), phát sinh 18 xung đột `modify/delete` và lỗi `ModuleNotFoundError: No module named 'visual_style'` / `'flow_prompts'` khi chạy bộ test của core.
- **Tái hiện E2E (Reproduction Path):** Chạy `pytest sys/tests/test_research_story_architect.py sys/tests/test_output_contract.py -v` trên môi trường chỉ có `module-core`.
- **Nguyên nhân cốt lõi (Root Cause):** `module-core` đã xóa các file engine khỏi `sys/tools/` và `sys/scripts/`, trong khi `module-content` cập nhật trực tiếp trên đường dẫn cũ và import cứng `visual_style` / `flow_prompts` thuộc `module-images`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng mọi module đều nằm chung một không gian phẳng `sys/tools/` và `visual_style` luôn tồn tại trong core.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Di chuyển toàn bộ `research_story_architect.py`, `visual_quality.py`, builders và blueprints vào package độc lập `sys/content/`; bọc import `visual_style` bằng guard `VISUAL_STYLE_AVAILABLE` và kiểm tra rõ ràng trong `ResearchedTopic.__post_init__`; dùng `pytest.importorskip` cho các test cần `module-images`. 183 passed trên core-only và 34/34 passed khi nạp kèm `module-images`.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Giữ toàn bộ tài sản và bộ kiến trúc nội dung trong `sys/content/`; mọi tham chiếu sang module ngoại vi (`visual_style`, `flow_prompts`, `flow_dispatch`) phải qua lazy/guarded import để `module-core` luôn tự chủ.

### [ERR-20261028-02] Khử Lệch Âm "Lướt Dép" (`\bweb\b`), Dẹp Bỏ Clipart AI Slop & Khử Lặp Cụm Chuyển Tiếp (CLEAN_DOODLE_PHONETICS)
- **Triệu chứng (Symptom):** (1) TTS phát âm "lướt web" thành "lướt dép"; (2) Khung hình 16:9 bị quá AI/clipart rối rắm (lò xo sét, robot đồ chơi, pin vô cực, biển cảnh báo tam giác, sơ đồ hỗn loạn nhiều vật thể); (3) Test `test_script_diversity_and_chronology` bắt lỗi lặp cụm "câu trả lời nằm ở" giữa SC10 và SC14.
- **Tái hiện E2E (Reproduction Path):** Chạy `normalize_for_tts("lướt web")` ra `"lướt gép"` -> VietNarrator đọc thành "lướt dép"; kiểm tra 5 frame video 16:9 tại 10s, 50s, 55s, 113s, 120s; chạy `pytest sys/tests/test_willpower_paradox_production.py`.
- **Nguyên nhân cốt lõi (Root Cause):** (1) `vn_text_normalizer.py` và `worker.py` ánh xạ `\bweb\b` sang `"gép"` khiến TTS biến âm thành "dép"; (2) Prompt mô tả ẩn dụ cơ học công nghiệp và biểu tượng game khiến NanoBanana vẽ 3D clipart; (3) Câu dẫn chuyển ý bị trùng lặp.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng "gép" là phiên âm chuẩn tiếng Việt cho "web", và cho rằng AI tự động tối giản hóa các biểu tượng ẩn dụ phức tạp.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Đổi `\bweb\b` sang `"uép"` (/wɛb/) và trau chuốt câu thoại sang `"lướt mạng / tab tra cứu"`; (2) Tái thiết kế 5 prompt thành 2D Indie Doodle Clean Minimalist (stickman bám ghế `'CÀNG GỒNG CÀNG THÈM'`, stickman cứng đờ `'BẤT ĐỘNG 4 TIẾNG'`, stickman tự tin thái quá `'Ý CHÍ VÔ HẠN?'`, thước đo `'CẠN KIỆT'`, bàn tay đẩy đĩa `'MỖI LẦN CƯỠNG LẠI'`, nền kem `#F8F0DC` / trắng `#FFFFFF`, $\ge 75\%$ negative space); (3) Đổi SC14 thành `"Lời giải đến từ..."`, đạt 14/14 tests pass green.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Dùng bán nguyên âm `"uép"` cho từ mượn "web" hoặc ưu tiên từ khẩu ngữ thuần Việt; mọi visual metaphor phải lấy stickman làm trung tâm trên canvas phẳng sạch 100%, cấm nhồi nhét đa biểu tượng hoặc mô tả chi tiết cơ khí/game.

### [ERR-20261023-03] Tăng Tốc Đa Luồng Mặc Định Toàn Trình Audio/TTS & Khắc Phục 5 Lỗi Biên Âm Học (PARALLEL_TTS_DEFAULT)
- **Triệu chứng (Symptom):** (1) `audio_pipeline.py` chạy tuần tự từng câu và crash `TypeError: Client.__init__()` khi gọi remote; (2) `normalize_for_tts` nuốt thẻ `[pause:800ms]` thành chữ `"tám trăm mi-li giây"` và `detect_unnormalized_tokens` tự từ chối từ phiên âm có gạch nối (`Xô-crát`); (3) `master()` nổ gain `+inf dB` trên file im lặng tuyệt đối (`input_i: "-inf"`); (4) `subtitles.py` và `worker.py` chồng lấn mốc phụ đề 10ms (`CAPTION_TIMELINE`).
- **Tái hiện E2E (Reproduction Path):** Chạy `PYTHONPATH=sys:sys/tools ./.venv/bin/pytest sys/tests/test_vn_text_normalizer_adversarial.py sys/tests/test_adversarial_m2.py sys/tests/test_colab_pool.py sys/tests/test_parallel_audio_pipeline.py -v`.
- **Nguyên nhân cốt lõi (Root Cause):** (1) Thiếu điều phối song song qua `ColabPoolDispatcher` trong `audio_pipeline.py` và `remote_audio.py`; (2) `vn_text_normalizer` biến đổi số trước khi bảo vệ thẻ `[pause:...]` và thiếu whitelist âm tiết phiên âm chuẩn; (3) `master()` lấy `-11.0 - (-inf) = +inf` khi sườn âm bằng 0; (4) làm tròn biên từ không kẹp `t[i].end <= t[i+1].start`.
- **Giả định sai (Wrong Assumptions):** Giả định `audio_pipeline.py` chỉ chạy mock đơn luồng, thẻ `[pause]` không chứa chữ số, file WAV đầu vào luôn có năng lượng âm thanh `> -70 LUFS`, và các mốc từ độc lập không bao giờ chồng lấn sau khi làm tròn.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Mặc định hóa chạy song song đa luồng (`parallel=True, max_workers=3, batch_size=4`) trong `AudioPipeline._synthesize_segments_parallel()` và `remote_audio.produce_parallel()` qua `ColabPoolDispatcher`; (2) bảo vệ thẻ `[pause:...]` trước khi chuẩn hóa số và bổ sung `CANONICAL_TRANSLITERATION_SYLLABLES`; (3) chặn ngưỡng `input_i <= -70.0` (`gain_db = 0.0`) trong `master()` và `nframes <= 0` trong `mix_sound_design()`; (4) kẹp đơn điệu không chồng lấn `a = max(cues[-1]['end'], a)` trong `subtitles.py` và `worker.py`. Đạt 399/399 tests green.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Chế độ mặc định của tổng hợp giọng đọc luôn là **tăng tốc đa luồng đa tài khoản Colab T4** kết hợp gom lô (`batch_size=4`); luôn bảo vệ thẻ điều khiển `[pause:...]` trước khi chuẩn hóa văn bản, kẹp gain an toàn với tín hiệu im lặng và ép đơn điệu chặt các mốc thời gian phụ đề.

### [ERR-20261024-01] Khôi Phục Biên Tích Hợp Đa Module (`audio/images/video/content/core`) & Chuẩn Hóa Flat 2D `Nguệch Ngoạc` 1.7.0
- **Triệu chứng (Symptom):** Sau khi hợp nhất các nhánh module vào core: (1) `remote_audio.produce` gửi toàn bộ 63 câu qua 1 phiên `Client.synthesize` đơn lẻ thay vì chia shard đa T4; (2) `cdp_direct_client.py` tự sửa prompt khi gặp `PUBLIC_ERROR_UNSAFE_GENERATION`, so chuỗi `'Profile 1'` đụng `'Profile 10'`, và đăng ký nhân vật 1.7.0 thiếu `has_character: True`; (3) `build_ai_sycophancy_9x16.py` nhét mô tả đèn ấm/quán cà phê (`pendant light`, `lamplight`, `glowing tablet`) khiến Flow sinh ảnh webtoon thay vì hoạt họa 2D phẳng kiểu `Nguệch Ngoạc`.
- **Tái hiện E2E (Reproduction Path):** Chạy `PYTHONPATH=sys:sys/tests pytest -q sys/tests/test_integration_recovery.py`.
- **Nguyên nhân cốt lõi (Root Cause):** Đường gọi `remote_audio.produce` chưa nối vào `colab_bridge.parallel_audio.synthesize`; `Client.synthesize` thiếu nhánh `reconcile() -> _ready(auto_start=True)` trước khi gửi; `flow_cdp/bridge.py` dùng `in` thay vì so khớp đường dẫn tuyệt đối; kịch bản `ai-sycophancy-9x16` viết `setting` tả thực nội thất thay vì nền màu phẳng 2D và thiếu nhãn `visible_text` đối lập trực quan.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng tương thích schema đồng nghĩa bảo toàn đường gọi đa tài khoản và phong cách hình ảnh; giả định thêm từ khóa tả thực ánh sáng không làm lệch compiler `1.7.0`.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Đóng băng `job_config`, ghi nhận `runtime.json` (`source_receipt`) và tách `technical_complete` khỏi `quality_approved`; (2) nối `parallel_audio.synthesize` vào `remote_audio.produce` kèm đối soát phiên `COLAB_SESSION_NOT_FOUND` và kiểm tra hash `support_files`; (3) bỏ sửa prompt ngầm, khớp chính xác `Path.resolve()` cho `Profile 1` vs `Profile 10`, truyền `has_character: True` trên 1.7.0; (4) hợp nhất `content/visual_quality.py` về `scripts/visual_quality.py`, khôi phục `human_editorial` trong `build_brief_v3`, và chuẩn hóa 12 cảnh / 97 beat `build_ai_sycophancy_9x16.py` sang nền màu phẳng 2D + nhãn in hoa đối chiếu theo chuẩn `Nguệch Ngoạc` (`IDk7jI83iYA`); (5) ghi `remotion_concurrency` và `stage_timings` trong `render.mjs`/`job_worker.py`. 11/11 tests tích hợp và 73/73 tests Flow/Workflow pass 100%.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Bảo toàn tuyệt đối biên hợp đồng của các module đã duyệt (`1.7.0` flat 2D explainer không tả thực đèn/nội thất, prompt bất biến khi lỗi, đa luồng T4 cho TTS, khớp chính xác đường dẫn profile, và tách bạch hoàn tất kỹ thuật với phê duyệt chất lượng).

### [ERR-20261025-01] Khử Lắp Bắp Âm Tiết Gạch Nối (`vi-đê-ô`), Rò Âm Mẫu Đầu Câu & Chặn Va Chạm Beat `smooth_interpolated_beats`
- **Triệu chứng (Symptom):** (1) Giọng đọc `OmniVoice` lắp bắp kéo dài khoảng lặng bất thường (`> 500ms`) giữa từ phiên âm có gạch nối (`"VI đê ...... ô"`), nuốt vế câu cuối hoặc dính âm mẫu `"định"` + `350–500ms` lặng ở đầu câu; (2) `smooth_interpolated_beats` đẩy `beats[10]` lên `12.55s` vượt qua `beats[11]` (`11.67s`) gây lỗi `Visual beats collide at 30 fps`.
- **Tái hiện E2E (Reproduction Path):** Chạy `PYTHONPATH=sys:sys/tools pytest sys/tests/test_colab_worker.py sys/tests/test_full_frame_upgrade.py -q` và nghe trực tiếp `narration.wav` của `SC01–SC02`.
- **Nguyên nhân cốt lõi (Root Cause):** (1) `vn_text_normalizer` xuất từ mượn có gạch nối liên chữ (`vi-đê-ô`) khiến BPE tokenizer của `OmniVoice` hiểu gạch nối là ranh giới ngắt nhịp prosody, đồng thời batch inference không tự retry khi có hố lặng nội câu hay rò âm cuối file mẫu tham chiếu; (2) `smooth_interpolated_beats` tịnh tiến `beats[10]` mà không kiểm tra `beats[11]['at']` khi `count > 11` và `end <= 15`.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng gạch nối phiên âm chuẩn trên mặt chữ giúp TTS đọc mượt hơn, kiểm tra RMS thô đầu file đủ bắt rò âm mẫu sau đoạn zero-padding, và `smooth_interpolated_beats` không bao giờ làm đảo thứ tự mốc đo âm học.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** (1) Tách gạch nối liên chữ thành khoảng trắng trong `_normalize_vi_tts_text` của `worker.py`, cắt cụm rò âm mẫu đầu câu + bảo toàn âm đuôi mũi nhẹ trong `_trim_silence`, và thêm vòng chấm điểm âm học `_utterance_acoustic_score` tự retry `batch_size=1` khi hố lặng nội câu `> 380ms` hoặc rớt mật độ âm tiết; (2) thêm guard `count == 11 or OPENING_WINDOW_SECONDS + .05 <= beats[11]['at'] - .5` trong `sys/visual_pacing.py` và viết lại lời thoại thực tế `SC01–SC02`. Kiểm chứng tests green, `PLAYBOOK.md <= 200` dòng và nghe thực tế `narration.wav` sạch 100%.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Không truyền gạch nối liên âm tiết (`vi-đê-ô`) vào model TTS BPE; luôn kiểm định hậu kỳ bằng điểm âm học + nghe thực tế file WAV để bắt rò âm mẫu/nuốt vế, và mọi phép làm trơn beat phải bảo toàn tính đơn điệu nghiêm ngặt ở 30 fps.

### [ERR-20261030-01] Chặn Thẻ Chữ HTML Phủ Mờ Lên Thumbnail & Chuẩn Hóa Poster Trực Tiếp Từ Flow CDP (FLOW_NATIVE_THUMBNAIL)
- **Triệu chứng (Symptom):** Thumbnail/Cover xuất ra bị thẻ chữ HTML, dải gradient đen mờ (`#0F172Aee`) hoặc badge đỏ đè lên che khuất nhân vật và hình vẽ nghệ thuật doodle.
- **Tái hiện E2E (Reproduction Path):** Kiểm tra `sys/renderer/thumbnail.tsx` khi render `Thumbnail` vẫn chèn `<AbsoluteFill style={{background: 'linear-gradient...'}}>` và text overlay đè lên `Img`.
- **Nguyên nhân cốt lõi (Root Cause):** Renderer Remotion kế thừa template cũ dán thẻ text HTML đè lên ảnh thay vì tạo toàn bộ poster hoàn chỉnh từ prompt Flow CDP với chữ vẽ tay tích hợp thẳng vào nền phẳng.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng dán chữ HTML sau khi render ảnh sẽ sắc nét hơn, vô tình phá vỡ tính thẩm mỹ 2D doodle thống nhất và che mất nét vẽ người que.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Cập nhật `Thumbnail.tsx` mặc định tắt `overlay_card` khi có `image`, khóa quy tắc thumbnail 100% sinh trực tiếp từ Flow CDP với `allowed_text` vẽ tay trên nền `#F8F0DC` / `#FFFFFF`. Đạt Station 1, 2, 3, 4 pass.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi thumbnail/cover phải được sinh trực tiếp 100% từ Flow CDP với chữ vẽ tay tích hợp sẵn trên nền phẳng; tuyệt đối cấm dùng thẻ chữ HTML, banner hay gradient đen dán đè lên hình vẽ.

