# Đặc Tả Bộ Hồ Sơ Kỹ Thuật Pipeline, Đóng Gói CTR & Spin-off Ngắn (Pipeline Blueprint Specification)

Tài liệu quy định các tiêu chuẩn kỹ thuật bắt buộc khi **Research & Narrative Architect** đóng gói hồ sơ sản xuất (`brief.json`, `content.json` chuẩn Schema 3.0 và bộ kịch bản Spin-off `short_9x16`) để chuyển giao cho các khâu tiếp theo của Video Pilot.

---

## 1. Cấu Trúc Tổng Quan Của Hồ Sơ Kỹ Thuật (Blueprint Architecture)

Hồ sơ bàn giao đặt trong thư mục `sys/runs/<job>/` gồm:
1. `brief.json`: Định nghĩa đề tài nghiên cứu nội bộ (`topic`), trạm đồng sáng tạo góc nhìn con người (`human_editorial`), trạm đóng gói hiển thị (`packaging`: `youtube_title`, `thumbnail_spec`, `channel_pillar`, `funnel_tier`, `seo_keywords`), đối tượng, thời lượng động, nguồn học thuật (`sources`) và các ý bắt buộc (`required_points`).
2. `content.json`: Định nghĩa kịch bản (số phân cảnh động theo chiều sâu nội dung cho cả `long_16x9` và `short_9x16`), nhân vật, các nhịp chuyển động (`beats[]`), bảng ánh xạ `coverage` và các khẳng định dữ kiện `claims`.
3. `spinoff_shorts/` *(khi bật chế độ Spin-off)*: Chứa các gói kịch bản `short_9x16` độc lập (`spinoff_01/`, `spinoff_02/`...) được rút trích từ các nghịch lý đắt giá nhất của hồ sơ nghiên cứu gốc.

---

## 2. Tiêu Chuẩn Kỹ Thuật Cho Từng Khâu Downstream

### 2.1. Hợp đồng Đóng Gói YouTube, Định Vị Kênh & Góc Nhìn Con Người (`Packaging & Human Editorial Contract`)
Để ngăn chặn nội dung AI tự động vô hồn bị nền tảng đánh flop và tránh tiêu đề học thuật dài dòng, `brief.json` tách bạch `topic` với `packaging` và `human_editorial`:

```json
{
  "topic": "Nghịch lý Tri thức và Ảo giác Năng lực: Giải phẫu cơ chế nhận thức khiến việc tiếp nhận thông tin thụ động làm tê liệt tư duy gốc rễ",
  "channel_pillar": "Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức",
  "funnel_tier": "tier_1_broad",
  "youtube_title": "Ảo Giác Năng Lực: Vì Sao Càng Đọc Càng Thấy Hiểu?",
  "thumbnail_spec": {
    "visual_hook": "Nhân vật người que dùng kính lúp kiểm tra mô hình tư duy trong cùng khung với sơ đồ",
    "text_overlay": "BIẾT TÍNH ≠ HIỂU!",
    "contrast_pair": "Nhận thức hời hợt vs. Thấu suốt bản chất"
  },
  "seo_keywords": [
    "tư duy nhận thức",
    "ảo giác năng lực",
    "mô hình tư duy",
    "phương pháp luận",
    "bản chất tri thức"
  ],
  "human_editorial": {
    "topic_dilemmas": [
      "Mâu thuẫn giữa cảm giác thuộc lòng thông tin và khả năng tự suy luận khi gặp tình huống mới"
    ],
    "dynamic_questions": [
      "Trong thực tế quan sát của bạn, dấu hiệu rõ nhất cho thấy một người chỉ đang 'sưu tầm chữ' chứ chưa thực sự hiểu bản chất vấn đề là gì?"
    ],
    "author_raw_input": "Người chỉ đọc mà không tự phản biện thường rất tự tin khi nói lại lời người khác, nhưng hỏi vặn một câu về nguyên nhân gốc rễ là đứng hình.",
    "editorial_stance": "Độ trơn tru khi tiếp nhận thông tin tỉ lệ nghịch với độ sâu của tư duy; chỉ khi va vào ma sát phản biện mới hình thành tri thức thật.",
    "expanded_content_ideas": [
      {
        "angle_type": "analysis",
        "idea_summary": "Giải phẫu bẫy nhận diện quen thuộc (familiarity trap) khi não đánh đồng việc nhìn thấy lại mặt chữ với việc nắm được cấu trúc nhân quả.",
        "narrative_integration": "Triển khai ở phần mở đầu và đối chứng thực nghiệm."
      },
      {
        "angle_type": "evaluation",
        "idea_summary": "Đánh giá ranh giới: Đọc rộng giúp tạo bản đồ khái niệm ban đầu, nhưng nếu thiếu bước tự vặn hỏi nguyên lý đầu tiên thì mọi ghi chép đều trở thành gánh nặng nhận thức.",
        "narrative_integration": "Triển khai ở phần bình luận chiều sâu và kết luận mở nút."
      }
    ]
  }
}
```

- **Quy tắc kiểm định cứng (`check_packaging_and_localization` & `validate_human_editorial`):**
  1. `youtube_title`: Độ dài lý tưởng **$\le 55$ ký tự** (ngưỡng cảnh báo cứng $60$ ký tự); phải đặt từ khóa kích thích tò mò ngay trong **5 chữ đầu tiên**; **tuyệt đối cấm tự trả lời câu hỏi ngay trong tiêu đề**.
  2. `thumbnail_spec`: Gồm 1 hình ảnh tương phản trực diện (`visual_hook`) + dòng chữ đè (`text_overlay`) ngắn gọn **2–4 từ in hoa** (không lặp lại nguyên văn tiêu đề video).
  3. `channel_pillar` & `funnel_tier`: Khóa cố định vào ngách *"Tư Duy Nhận Thức, Phương Pháp Luận & Bản Chất Tri Thức"*, phân tầng rõ `tier_1_broad`, `tier_2_mid`, hoặc `tier_3_conversion`. Nghiêm cấm chứa từ khóa lệch ngách văn phòng (*mẹo Excel, hàm Excel, làm Slide nhanh, hacks ngắn hạn*).
  4. `human_editorial`: `dynamic_questions` phải được sinh động riêng theo `topic_dilemmas` (không trùng lặp, không gán cứng); `expanded_content_ideas` phải phát triển thành các góc phân tích (`analysis`), bình luận (`commentary`), đánh giá (`evaluation`) hoặc tình huống thực tế (`real_world_case`) rõ ràng.

### 2.2. Hợp đồng Âm thanh & Chốt Chặn 15 Giây Đầu (Audio & TTS Contract)
- **Công thức tính âm tiết:**
  $$\text{Target Syllables} = \text{round}\Big((\text{Scene Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$$
- **Tham số đuôi audio ($P_{\text{tail}}$):**
  - Cảnh trung gian: $0.70\text{s}$ (`DEFAULT_PAUSE['para']`).
  - Cảnh kết thúc: $0.35\text{s}$ (`DEFAULT_PAUSE['tail']`).
- **Quy tắc Cú Tát Sự Thật & Cấm Pause ở `SC01` (`Zero Pause in First 15 Seconds`):**
  - Câu đầu tiên của `SC01` bắt buộc **$\le 18$ âm tiết** (*Counter-Intuitive / Truth-Slap Hook*), đi thẳng vào nghịch lý học thuật.
  - **Nghiêm cấm** chèn bất kỳ thẻ `[pause:...]` nào trong cảnh mở đầu `SC01` (`OPENING_SCENE_PAUSE_FORBIDDEN`).
  - Toàn bộ video chỉ được dùng tối đa **1–3 thẻ `[pause:800ms]` / `[pause:900ms]`** tại các khoảnh khắc lật ngược định kiến lớn (`DEFAULT_MAX_DRAMATIC_PAUSES = 4`).
- **Dải tốc độ động học (`Dynamic Pacing`):**
  - **30 giây đầu (`SC01–SC02`):** Đẩy lên **`4.2 – 4.4` âm tiết/giây** (với giọng `VietNarrator` `speed: 1.0`) để cuốn người xem ngay từ giây `0:00`.
  - **Phần thân & kết:** `4.0` âm tiết/s ở phần giải phẫu cơ chế và `3.6 – 3.8` âm tiết/s ở phần đúc kết triết lý.

### 2.3. Hợp đồng Tạo hình: Full-frame Visual Beats & Continuity (Flow CDP)
- Mỗi beat là một ảnh hoàn chỉnh `kind: "scene"`, áp dụng bảng 7 shot types chuẩn: `full_scene`, `variation`, `macro_prop`, `white_card`, `white_isolated`, `still_life` (cận cảnh vật thể, tài liệu, dụng cụ không có người/bàn tay), và `environment` (cảnh rộng bối cảnh, phòng học, phong cảnh không có người).
- **Khoảng thở thị giác & Chống mệt mỏi nhân vật:** Sử dụng `still_life` và `environment` làm các nhịp nghỉ nhận thức giữa các cảnh có nhân vật. Bắt buộc đạt ít nhất 30% nhịp hình không có nhân vật trong mỗi chuỗi 10 nhịp trượt; tuyệt đối cấm vượt quá 4 nhịp hình có nhân vật liên tiếp.
- **Quy chuẩn Bối cảnh (Setting Brevity):** Chuỗi `setting` của mỗi cảnh bắt buộc $\le 8$ từ (chỉ nêu không gian và ánh sáng), tuyệt đối cấm liệt kê bàn ghế, tài liệu, vật dụng trong trường `setting`.
- Với cùng địa điểm và bố cục, dùng `based_on` trỏ tới ảnh trước, nêu rõ phần giữ lại trong `preserve` và thay đổi trong `change`. Với chuyển cảnh hoặc đổi góc lớn, dùng ảnh độc lập.
- Trong cold open, hướng tới 8–9 hình trong 12–12,5 giây và khoảng 4 hình trong 5 giây đầu khi lời thoại có đủ ý hình ảnh. Đây là mục tiêu dựng cho phần mở đầu, không phải quota cho mọi cảnh. Các beat phải neo vào đúng cụm lời thoại và được kiểm tra theo WAV.
- Không tạo `kind: "background"`/`kind: "sticker"`, `layers[]`, ảnh cut-out nền trắng hay viền sticker. Không dùng cơ khí sáo rỗng (`brain cutaway`, bàn tính, van ống nước, mỏ neo sắt).
- Tuyệt đối không để lộ mã định danh (`SC01`, `CH01`, `SC01_I1`) trong `description`, `preserve`, `change`, hoặc `visible_text`.

### 2.4. Hợp đồng Dựng Video & Vùng Nguy Hiểm 15s Đầu (Remotion Composition & Visual Beats)
- **Tách ngưỡng giữ hình thành 2 vùng:**
  1. **Cold open (`0:00–0:12.5`):** Tạo khoảng 8–9 hình khi lời thoại hỗ trợ; dùng ngưỡng thời gian linh hoạt theo anchor và duyệt với WAV.
  2. **Vùng Thân Bài (`sau 0:15` / `SC03+`):** Giữ ngưỡng chuẩn **`0.83s – 3.80s`** theo thuật toán *Cue-Window Allocation* (`0.000s` drift tại mọi đầu câu thoại).

### 2.5. Kiến Trúc Chuyển Thể `Short-Form Spin-off Blueprint` (Giải quyết Bẫy 2)
- **Nghiêm cấm cắt ngang video dài đem đăng TikTok:** Tuyệt đối không cắt thô giữa video `long_16x9` để đăng TikTok vì thiếu Hook độc lập và sai khung hình.
- **Quy trình Spin-off chuẩn (`build_short_spinoff_topics`):**
  - Từ 1 hồ sơ nghiên cứu gốc, kiến trúc sư trích xuất **các nghịch lý đắt giá nhất** làm chủ đề cho các video ngắn độc lập.
  - Mỗi bản Spin-off được đóng gói thành một hồ sơ `short_9x16` độc lập (`aspect_ratio: "9:16"`, `format_profile: "short_9x16"`, `subtitles: true`, `voice: "VietNarrator"`, `speed: 1.0`, thời lượng động theo kịch bản và audio WAV), có câu mở đầu **Counter-Intuitive Hook $\le 18$ âm tiết** viết mới hoàn toàn và phụ đề nhảy chữ theo `word_timestamps` (`max_line_chars: 28`).

### 2.6. Hợp đồng Pháp lý & Tính Toàn Vẹn (Legal & Integrity Contract)
- **`brief_hash` bất biến:** Tính SHA-256 trên chuỗi JSON tuần tự hóa canonical (`serialize_brief_json`, `indent=2`, `ensure_ascii=False`), khớp 100% với `pilot.py`.
- **Truy vết `coverage` & `claims` 100%:** Mọi `required_points` phải có `quote` nguyên văn trong `coverage`; mọi phát biểu khoa học phải có bản ghi trong `claims` trỏ tới `scene_id`, `source_id`, `fact`, và `quote`.

---

## 3. Quy Trình Kiểm Thử & Nghiệm Thu Blueprint

Trước khi chuyển giao hồ sơ cho khâu sản xuất, công cụ kiến trúc tự động chạy thẩm định:
1. `validate_brief(ROOT, brief_data)` và `validate_content(ROOT, brief_data, 1, brief_hash, content_data)` trong `sys/content_contract.py`.
2. `check_packaging_and_localization(brief_data, scenes)` trong `sys/content/research_story_architect.py`.
3. `script_cadence_checker.py` với chốt chặn `forbid_opening_pause=True` và `max_opening_hook_syllables=18`.
