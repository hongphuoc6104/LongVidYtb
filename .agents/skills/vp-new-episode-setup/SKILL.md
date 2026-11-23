---
name: vp-new-episode-setup
description: "Checklist trọn bộ A-Z để setup, kiểm định, render 2K trên Colab T4 và xuất bản YouTube cho một tập video mới (Long 16:9 + Short 9:16) theo đúng kiến trúc Video Pilot."
---

# New Episode Setup & Production Checklist (A -> Z)

Tài liệu chuẩn hóa toàn bộ các bước cần làm khi sản xuất **một tập video mới (Dual-Mode: `long_16x9` + `short_9x16`)**, ghép nối chuỗi skill hiện có (`vp-notebooklm-vault` -> `vp-research-architect` -> `vp-scriptwriting` -> `vp-channel-<id>` -> `vp-flow-cdp` -> `vp-colab-bridge` -> `vp-omni-platform` -> `vp-production`) thành 1 quy trình thực chiến duy nhất.

> **Thứ tự ưu tiên SSOT**: `AGENTS.md` > `.agents/rules/*` > `PLAYBOOK.md` > `vp-channel-<channel_id>/SKILL.md` > `SKILL.md` này.

---

## Pha 0: Đồng bộ dữ liệu kênh & Khởi tạo chủ đề
1. **Đọc thông số kênh**:
   - Đọc `.agents/skills/vp-channel-<channel_id>/SKILL.md`, `sys/channels/<channel_id>/channel_v2_production_lock.json`, và `sys/channels/youtube_channel_map.json`.
   - Kiểm tra xem kênh đang có `profile_id`, `youtube_channel_id`, `voice`, `recommended_speed`, vị trí watermark (`W-w-36:H-h-36` hoặc lock riêng của kênh như `W-w-48:H-h-48`).
2. **Analytics & Studio Sync (nếu dùng Fleet Manager)**:
   ```bash
   python3 sys/tools/vp_fleet_manager.py --mode single --channel <channel_id> --action analytics
   python3 sys/tools/vp_fleet_manager.py --mode single --channel <channel_id> --action studio_sync
   ```
3. **Khóa Packaging & Funnel**:
   - `youtube_title <= 55` ký tự cho **cả** Long và Short (Short thêm `#Shorts`).
   - Long thumbnail (`16:9`) + Short thumbnail (`9:16`): **2–4 chữ IN HOA** sinh trực tiếp bằng Flow BELUGA (`thumbnail_spec.prompt`), **cả 2 file xuất bản bắt buộc `< 2.0 MB`** (cấm dán chữ PIL/HTML; giữ bản gốc làm `*_master.png` nếu cần nén JPG `Q94` / PNG 8-bit `< 2 MB`).
   - Short khai báo `parent_long_id`, cầu nối thoại (`bridge`) + câu hỏi thảo luận (`close`) nằm gọn trong **15% cuối** (từ ~85% trở đi), kết hợp `12` beat `omni_flash` (`single_frame_i2v`, `end_image_path=null`).

---

## Pha 0.5: Khởi Tạo Fact Vault & Pattern Vault (`vp-notebooklm-vault`)
1. **Nạp 3-Vault trước khi viết kịch bản** (cấm tự bịa số liệu/trích dẫn từ trí nhớ LLM):
   ```bash
   python3 sys/tools/notebooklm_vault.py render-prompts --channel <channel_id> --topic "<TOPIC>" --format long_16x9
   python3 sys/tools/notebooklm_vault.py import-notes --channel <channel_id> --topic "<TOPIC>" --format long_16x9 --input sys/runs/<JOB_ID>/notes.md --output sys/runs/<JOB_ID>/fact_vault.json
   python3 sys/tools/notebooklm_vault.py validate --vault sys/runs/<JOB_ID>/fact_vault.json
   ```
2. **Cách ly `"report-only"` & localize Việt Nam**:
   - Mọi thông tin chưa có nguồn sơ cấp xác nhận bị chặn ở `report_only_claims[]`.
   - Lấy sẵn `vietnam_micro_bridges` (60s đầu), `spoken_numbers_vi` / `pronunciation_glossary`, và `export_chanh_niem_ke_manifest_seed()` (nếu là `chanh_niem_ke`).

---

## Pha 1: Tác quyền Kịch bản, Beat Visual & Linter Gates
1. **Lập Spec (`epXX_long_spec.json` & `epXX_short_spec.json`)**:
   - Long: tuân thủ số chapter (`8–12`), câu gốc và số beat ảnh (`240–350` beat, tách rõ 5 khối prompt theo `vp-channel-<id>`, `allowed_text=null` hoặc theo chuẩn kênh), bổ sung **Retention Reset mỗi 60–90s**, không có ký tự cấm / thuật ngữ hiện đại sai bối cảnh.
   - Short: `12–18` beat độc lập (tuyệt đối không cắt thô giữa chương Long); lập `SceneMap` (`scene_map_planner.py`) trước khi sinh prompt để khóa Cast/Ref DAG và chọn tuyến `dual_model_seam` (`veo_3_1_lite` 10c Seam vs `omni_flash` Frame-Link).
2. **Chạy đủ 4 Linter trước khi gọi TTS/Flow**:
   ```bash
   python3 sys/tools/fact_grounding_linter.py --content ... --vault sys/runs/<JOB_ID>/fact_vault.json --strict
   python3 sys/tools/cta_tone_linter.py ...
   python3 sys/tools/script_diversity_linter.py ... --strict
   python3 sys/tools/script_cadence_checker.py ...
   ```
   - **Cấm tuyệt đối** từ khóa kêu gọi máy móc: `like`, `share`, `subscribe`, `đăng ký`, `chia sẻ`, `thích`, `ấn/bấm chuông`.

---

## Pha 2: Giọng đọc Colab T4 OmniVoice & Master Audio `-11.0 LUFS`
1. **Kiểm tra tài khoản Colab rảnh trước khi chạy**:
   ```bash
   ./pipeline colab pool-status
   ```
   - Chọn tài khoản `state == "healthy"`, `external_lock_busy == false`, đủ `available_seconds >= 1200`, `local_sessions == []` và không đụng phiên job khác.
2. **Voice & Tốc độ chuẩn**:
   - Bắt buộc `VietNarrator_<channel_id>` qua **Colab T4 OmniVoice** (cấm `vi-VN-NamMinhNeural` / Edge-TTS).
   - Với kênh có tốc độ cao (như `su_ke_lai` `1.30x`): sinh `BASE_OMNIVOICE_SPEED` (ví dụ `1.12`) trên Colab -> WSOLA `atempo` ra tốc độ mục tiêu, ghép theo timeline thật.
3. **Bẫy kỹ thuật FFmpeg bắt buộc tránh**:
   - Trong `alimiter` **luôn truyền `:level=disabled`** kết hợp `aresample=192000` -> `alimiter` -> `aresample=48000` để FFmpeg không tự nâng gain lại lên `-10.0 LUFS` / `0 dBFS`.
   - Sau khi lắp xong `narration_master.wav`, đo kiểm `ffmpeg -af ebur128=peak=true`:
     - Đạt **`-11.2 .. -10.8 LUFS`** (mục tiêu `-11.0 LUFS`) và **`True Peak <= -1.0 dBTP`**.
4. **Đồng bộ Timeline & Phụ đề**:
   - Sinh `audio_timings.json`, `subtitles.srt` (cho Long sidecar & lưu trữ Short), `chapters_metadata.txt` (Long `FFMETADATA1`), và `_work_short/subtitles_kinetic_2k.ass` (Short: font `Noto Sans Bold`, Đỏ `#FF3B30` / Vàng `#FFE600`, `MarginV=470` né vùng UI dưới).
   - Tính `short_bridge_start_pct` từ `B11.start_sec / total_duration_sec * 100` (phải `>= 85%`).

---

## Pha 3: Sinh Ảnh & Clip Flow CDP (An toàn Quota & Sạch Khung)
1. **Quy tắc Chrome & Pool ([.agents/rules/gpu-headless-chrome.md](../../rules/gpu-headless-chrome.md))**:
   - Tối đa `img_workers=8`, `vid_workers=6` tùy VRAM; luôn tôn trọng stagger & cooldown, giữ job >30s có `schedule(DurationSeconds=45, TimerCondition="any")`.
2. **Stage A (Ảnh & Thumbnail)**:
   - Sinh đủ `240–350` ảnh Long (`16:9`), `12` ảnh Short (`9:16`), `thumbnail_16x9.png` (`< 2 MB`), `thumbnail_9x16.jpg` / `thumbnail_9x16.png` (**bắt buộc nén `< 2 MB` (`<= 2,097,152` bytes)**, giữ bản nét đầy đủ ở `thumbnail_9x16_master.png`).
   - Xóa sao 4 cánh `clean_beluga_sparkle_pil` + overscan crop chuẩn tỷ lệ (`1920x1080` / `1080x1920`).
   - **Quét Letterbox Bar Đen bắt buộc**: quét toàn bộ PNG Long (`row_mean < 6.0 & row_std < 3.0` ở viền trên/dưới); nếu phát hiện bar đen do BELUGA vẽ, crop chặt lại từ ảnh raw gốc (`_flow_raw_staging/`) -> resize Lanczos -> kiểm chứng lại bằng `read_file`.
3. **Stage B (Short Video Dual-Model Router: `veo_3_1_lite` Seam + `omni_flash` Frame-Link)**:
   - Priority 1: `full_chain` chừng nào pool còn credit (`credits_remaining >= 10` cho `veo_3_1_lite` hoặc `>= 18` cho `omni_flash`). Chỉ rơi về `images_only` khi **100% pool về 0 credit** (`cooldown != 0 credit`). Tuyệt đối tránh model sắp khai tử 05/12/2026 (`veo_3_1_fast`, `veo_3_1_quality`, `omni_1_1`).
   - Dùng `routing_mode="dual_model_seam"` (`build_short_video_chain_spec`) hoặc `build_dual_model_chain_spec(scene_map)`: chuyển cảnh đổi nhân vật/bối cảnh đi qua `veo_3_1_lite` (`10c/clip` Seam Mode + `seam_dissolve_sec=0.18`); giữ `omni_flash` Frame-Link cho cặp cảnh cùng cast/cùng ánh sáng (kênh 2D Doodle/Mindful khóa `soft_fade 0.24s`).
   - **Nếu 1–2 clip kẹt xoay vòng `PUBLIC_ERROR_UNUSUAL_ACTIVITY`** trên nhóm profile free/1050-credit có `last_used_at == 0`: dừng an toàn, chạy `stop_all()`, rồi resume với **`VP_FLOW_PROFILES=<các_profile_sạch_đang_thành_công>`** (ví dụ profile có lịch sử thành công thực tế trong lần chạy đó).
   - Soi ít nhất 1–2 frame trích trực tiếp từ clip raw (`clip_00.mp4`, `clip_11.mp4`) để quyết định `--short-delogo off` (nếu góc dưới phải đã sạch) hay `--short-delogo on`.
4. **Verify Teardown Flow Chrome**:
   ```bash
   ./pipeline flow status   # Bắt buộc listening_count == 0
   ```

---

## Pha 4: Render 2K Trên Colab Tesla T4 (`h264_nvenc`)
1. **Cô lập tài khoản Colab**:
   - Dùng Colab Tesla T4 `h264_nvenc` (tuyệt đối không render local/CPU/Remotion).
   - Nếu chạy song song Long (3 worker shard) và Short (1 worker), truyền `VP_COLAB_EXCLUDE=<các_account_long>` cho Short để `stop_pool()` của Long không tắt nhầm session của Short.
   - Bật guard dừng failover sau tối đa `2` lỗi `COLAB_EXEC_UNCONFIRMED`.
2. **Thông số xuất 2K**:
   - **Long 2K**: `2560x1440@30fps`, `cas=0.28`, `xfade=fade (0.24s)`, **không** burn phụ đề, logo `W-w-48:H-h-48`, mux lossless `-c copy` kèm `narration.m4a` (`-11.0 LUFS / <= -1.0 dBTP`) và `chapters_metadata.txt` -> `final_long_2k.mp4`.
   - **Short 2K**: `1440x2560@30fps`, mở đầu `4` frame từ `thumbnail_9x16.png` + `12` clip `omni_flash` (`720x1280` gốc Flow upscale `lanczos + cas=0.55 + unsharp`) retime theo WAV, burn `_work_short/subtitles_kinetic_2k.ass`, logo `W-w-48:H-h-48`, `aac 256k` (`-11.0 LUFS / <= -1.0 dBTP`) -> `final_short_2k.mp4`. Lưu ý: clip video gốc từ Flow `omni_flash` có độ phân giải native `720x1280`, nên Short phụ thuộc vào bitrate `>= 20–34M` + bộ lọc sắc nét `cas/unsharp` và cần chờ YouTube xử lý xong `1440p VP9/AV1` trên `yt-dlp -F` trước khi kiểm tra độ nét trên player.
3. **Verify Teardown Colab**:
   ```bash
   ./pipeline colab pool-status   # Các account đã dùng bắt buộc local_sessions: []
   ```

---

## Pha 4B: Turnkey `M1-Flex V9.2` 8-Shard 1080p / 2K IMAX Moving-Cinema Workflow (`su_ke_lai` & Analytical Long)
Khi sản xuất tập Long `16:9` theo khuôn điện ảnh động **`M1-Flex V9.2` ("Tựa Tựa Khuôn, Không Phải Y Đúc" — `sys/tools/produce_su_ke_lai_long_m1.py`)**:
1. **Chọn 1 trong 4 Khuôn Kịch Bản (`--archetype`, `6–12` chương) & Tổ Hợp Preset Sáng Tạo**:
   - `blitz_campaign` (*Chiến dịch thần tốc*, `8–10` chương): `--color-preset golden_dawn_1789 --chapter-style minimal_center_card --chain-pattern balanced_2beat --keyword-density 0.22`
   - `siege_and_trap_anatomy` (*Giải phẫu vây thành & tử địa*, `6–8` chương): `--color-preset monsoon_siege_contrast --chapter-style minimal_center_card --chain-pattern dynamic_1_2_3beat --keyword-density 0.24`
   - `commander_rivalry_duel` (*Song đấu kỳ phùng địch thủ*, `8–11` chương): `--color-preset imperial_torch_amber --chapter-style in_scene_cinema_title --chain-pattern epic_3beat --keyword-density 0.20`
   - `naval_and_river_ambush` (*Thủy chiến & phục kích sông nước*, `7–9` chương): `--color-preset river_mist_teal_gold --chapter-style in_scene_cinema_title --chain-pattern dynamic_1_2_3beat --keyword-density 0.22`
2. **Quy Trình Turnkey 4 Bước (`sys/tools/produce_su_ke_lai_long_m1.py`)**:
   ```bash
   # Bước 1: Kiểm định cấu hình M1-Flex & khóa an toàn (0% bản đồ vẽ tay Pillow, 0% whip-slide, 0 chữ thanh đen IMAX)
   PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
     --stage validate-flex-spec \
     --archetype <blitz_campaign|siege_and_trap_anatomy|commander_rivalry_duel|naval_and_river_ambush> \
     --color-preset <golden_dawn_1789|river_mist_teal_gold|monsoon_siege_contrast|imperial_torch_amber> \
     --chapter-style <minimal_center_card|in_scene_cinema_title> \
     --chain-pattern <balanced_2beat|dynamic_1_2_3beat|epic_3beat> \
     --keyword-density 0.22 \
     --resolution <1080p|1440p|360p>

   # Bước 2: Dựng Timeline, Master Audio (-11.0 LUFS / <= -1.0 dBTP), Impact SRT & Full Vietnamese CC SRT
   PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
     --stage build-timeline \
     --job-dir sys/runs/<LONG_JOB_ID> \
     --script sys/runs/<LONG_JOB_ID>/script.json \
     --output-dir video/<LONG_JOB_ID> \
     --color-preset golden_dawn_1789 \
     --chapter-style minimal_center_card \
     --chain-pattern balanced_2beat \
     --keyword-density 0.22 \
     --resolution 1080p \
     --total-shards 8

   # Bước 3: Render 8 Shard song song (bắt buộc --require-moving-video xác thực 100% clip .mp4 động native 16:9)
   for sid in 1 2 3 4 5 6 7 8; do
     PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
       --stage render-shard --shard "$sid" \
       --job-dir sys/runs/<LONG_JOB_ID> --require-moving-video &
   done
   wait

   # Bước 4: Ghép Lossless (-c:v copy + pre-AAC brickwall alimiter=limit=0.77) + xuất Bảng Kiểm Định 20 Khung & Full CC SRT
   PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
     --stage assemble --job-dir sys/runs/<LONG_JOB_ID> --output-dir video/<LONG_JOB_ID>
   PYTHONPATH=sys sys/.venv/bin/python sys/tools/produce_su_ke_lai_long_m1.py \
     --stage full-cc-srt --job-dir sys/runs/<LONG_JOB_ID>
   ```
3. **Bất biến chất lượng M1-Flex V9.2 bắt buộc**:
   - `100%` clip `.mp4` động native `16:9` (`0` ảnh tĩnh PNG, `0` clip dọc `9:16` cắt ngang, `0%` bản đồ vector Pillow `map_dive`).
   - `0%` chuyển cảnh trượt ngang gây chóng mặt (`directional_flow_chain_transition` bị cấm vĩnh viễn); giữ cố định `zoom=1.0, dx=0.0, dy=0.0, cy=0.44` trong chuỗi và hòa mờ tĩnh `0.20s` (`0px` shift) giữa hai chuỗi.
   - Thanh đen IMAX `2.39:1` trên/dưới đen tuyền `100%` (`0` chữ header/footer/badge trên thanh đen; **chỉ đặt duy nhất logo kênh ở góc dưới phải**).
   - Từ khóa nhấn đơn dòng (`top_word=""`, `#FFF5D6`, `66px@1080p / 88px@1440p`) chỉ xuất hiện trên `15%–30%` số nhịp (`>= 70–72%` thuần điện ảnh không chữ, **cấm tuyệt đối hiện từ khóa ở nhịp mở đầu mỗi chương `beat_*0`**).

---

## Pha 5: Kiểm Định Media Thực Tế & Bộ Publish Kit
1. **Kiểm định Container & Loudness trên MP4 cuối**:
   - `ffprobe`: xác nhận độ phân giải (`2560x1440` / `1440x2560`), `30/1 fps`, `yuv420p`, `aac 48000 Hz stereo`, đủ `nb_frames` & `chapters` (Long).
   - `ffmpeg -nostats -i <final.mp4> -vn -af ebur128=peak=true -f null -`: xác nhận `I: ~ -11.0 LUFS`, `Peak <= -1.0 dBFS`.
2. **Soi Frame Thật qua `read_file`** (bắt buộc trích từ 2 file MP4 cuối):
   - Long: đầu/giữa/cuối (`long_00s`, `long_180s`, `long_550s`) -> kiểm tra độ nét 2K, không bar đen, không sub burn, logo đúng góc dưới phải.
   - Short: `short_poster` (frame 1), đầu/giữa/cuối (`short_03s`, `short_25s`, `short_50s`) -> kiểm tra poster `thumbnail_9x16.png`, phụ đề Đỏ/Vàng không mất dấu tiếng Việt, `MarginV=470` sạch vùng UI dưới, không hộp mờ behind logo.
3. **Hoàn thiện Bộ Hồ Sơ & Publish Kit**:
   - Long: `av_sync_audit_report.json`, `job_manifest.json`, `publish/youtube_metadata.json`, `publish/youtube_long.md`.
   - Short: `job_manifest.json`, `publish/youtube_metadata.json`, `publish/youtube_short.md`, `publish/tiktok_caption.md`, `publish/facebook_post.md`.
   - **Định dạng bắt buộc trong `youtube_long.md` & `youtube_short.md`** để `parse_metadata_file()` đọc 100% trường (**không để dòng trống giữa heading `## N.` và fence mở code block**):
     - `## 1. Tiêu đề` + xuống dòng ngay fence `` ````text `` (lưu ý: thực tế dùng 3 dấu backtick)
     - `## 2. Mô tả` + xuống dòng ngay fence code block (đính kèm mục `"Nguồn tham khảo:"` xuất từ `notebooklm_vault.py export-sources`)
     - `## 3. Thẻ từ khóa` + xuống dòng ngay fence code block (phân cách dấu phẩy)
     - `## 4. Cài đặt xuất bản` (`- **Ngôn ngữ video**: Tiếng Việt` & `- **Danh mục**: Giáo dục`)
     - `## 5. Bình luận ghim` + xuống dòng ngay fence code block (**cấm từ khóa `like/share/subscribe/đăng ký/chia sẻ`**; `publish_youtube_cdp.py` tự động đọc trường này để đăng và ghim bình luận khi xuất bản `PUBLIC`).

---

## Pha 6: Phê Duyệt & Xuất Bản Lên YouTube Studio CDP
1. **Ghi nhận Review Gate (khi người dùng duyệt video)**:
   - Đăng ký & duyệt cả 2 `job_id` trong `sys/channels/video_review_queue.json` qua `sys/tools/review_queue_manager.py` (`register_video_for_review` -> `set_review_decision(..., "APPROVED")`).
2. **Upload Long trước -> lấy URL -> Upload Short nối `--related-video` (bật đủ `--thumbnail`, `--subtitles`, và bình luận ghim)**:
   ```bash
   # 1. Long 16:9 (tự động đăng + ghim ## 5. Bình luận ghim khi --visibility PUBLIC)
   python3 sys/tools/publish_youtube_cdp.py \
     --channel <channel_id> \
     --job-id <LONG_JOB_ID> \
     --video video/<LONG_JOB_ID>/final_long_2k.mp4 \
     --metadata video/<LONG_JOB_ID>/publish/youtube_long.md \
     --thumbnail video/<LONG_JOB_ID>/thumbnail_16x9.png \
     --subtitles video/<LONG_JOB_ID>/subtitles.srt \
     --strict-thumbnail \
     --visibility <PRIVATE|UNLISTED|PUBLIC> \
     --edit-screenshot video/<LONG_JOB_ID>/publish/studio_edit_long.png \
     --comment-screenshot video/<LONG_JOB_ID>/publish/ep_long_pinned_comment.png

   # 2. Short 9:16 (BẮT BUỘC truyền --thumbnail <2MB với kênh Tier 2+, --subtitles để không dính ASR auto-caption lỗi chính tả, và --related-video trỏ URL Long)
   python3 sys/tools/publish_youtube_cdp.py \
     --channel <channel_id> \
     --job-id <SHORT_JOB_ID> \
     --video video/<SHORT_JOB_ID>/final_short_2k.mp4 \
     --metadata video/<SHORT_JOB_ID>/publish/youtube_short.md \
     --thumbnail video/<SHORT_JOB_ID>/thumbnail_9x16.jpg \
     --subtitles video/<SHORT_JOB_ID>/subtitles.srt \
     --strict-thumbnail \
     --short \
     --related-video <LONG_VIDEO_URL> \
     --visibility <PRIVATE|UNLISTED|PUBLIC> \
     --edit-screenshot video/<SHORT_JOB_ID>/publish/studio_edit_short.png \
     --comment-screenshot video/<SHORT_JOB_ID>/publish/ep_short_pinned_comment.png
   ```
   - Hỗ trợ sửa bù sau xuất bản qua CLI:
     - `--update-thumbnail <path> --video-id <ID> --strict-thumbnail` (cập nhật bìa)
     - `--attach-subtitles <path.srt> --video-id <ID>` (gắn bù phụ đề `.srt`)
     - `--post-pinned-comment --video-id <ID> --metadata <youtube_*.md> --comment-screenshot <png>` (đăng & ghim bình luận cho cả Long và Short)
3. **Hoàn thiện Studio Pro & Kiểm tra hậu xuất bản (Parity chuẩn EP04 & Major-Channel M1-Flex V9.2 Publication Checklist)**:
   - **Phụ đề Full CC Tiếng Việt (`subtitles_vi_full_cc.srt`)**: Với tập Long `M1-Flex V9.2`, luôn sinh và gắn file phụ đề lời thoại đầy đủ `subtitles_vi_full_cc.srt` (`produce_su_ke_lai_long_m1.py --stage full-cc-srt`) qua `--subtitles` hoặc `--attach-subtitles` để người xem TV/Desktop bật CC đọc trọn vẹn 100% câu thoại chuẩn dấu tiếng Việt (tránh YouTube ASR tự động nhận diện sai tên riêng lịch sử).
   - **Chuẩn Kênh Lớn (Major-Channel Packaging & Retention Loop)**:
     * Tiêu đề `<= 55` ký tự, độc lập 100% (cấm `P1/P2/Tập 1/Phần 2` ở đầu tiêu đề).
     * Mô tả mở đầu bằng 2 dòng hook nghịch lý + **Danh mục Chapters chuẩn YouTube (`00:00 Chương I ...`)** khớp 100% với `timeline` + khối `"Nguồn tham khảo:"` trích từ `notebooklm_vault.py export-sources`.
     * Thumbnail `16:9` Flow-native (`2–4` chữ IN HOA vẽ trực tiếp trong khung, `< 2.0 MB`, `--strict-thumbnail`), kiểm chứng `naturalWidth > 0` và `has_custom_thumbnail == true` sau khi reload trang `/edit`.
     * **Bình luận ghim 2 lựa chọn tranh luận (`--post-pinned-comment`)**: Đăng & ghim ngay câu hỏi phán xét lịch sử 2 phương án (khớp với đoạn kết video, tuyệt đối không dùng `like/share/subscribe/đăng ký`), kiểm chứng huy hiệu `@Channel đã ghim` trên trang watch.
   - Thêm cả Long & Short vào danh sách phát chính của kênh (nếu có), gắn End Screen & Info Card trên Long trong YouTube Studio.
   - Kiểm tra `yt-dlp -F <URL>` và `oEmbed HTTP 200` xác nhận video đã `PUBLIC` (không kẹt `"trạng thái nháp"`), YouTube đã xử lý xong độ phân giải HD/`2560x1440` (Long) và `1440x2560` VP9/AV1 (Short).
   - Đọc screenshot `/edit`, screenshot watch page bình luận ghim, và ảnh tab `/videos/short` bằng `read_file`: xác nhận **cả Long lẫn Short đều có `has_custom_thumbnail == true`, `subtitles` tiếng Việt, `@Channel đã ghim` ở comment đầu, `has_pill: true` trên Short**, `youtube_channel_map.json` & `video_review_queue.json` đã cập nhật, và Chrome Studio đã đóng sạch (`listening_count: 0`).
