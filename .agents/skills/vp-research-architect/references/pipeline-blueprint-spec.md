# Đặc Tả Bộ Hồ Sơ Kỹ Thuật Pipeline (Pipeline Blueprint Specification)

Tài liệu quy định các tiêu chuẩn kỹ thuật bắt buộc khi **Research & Narrative Architect** đóng gói hồ sơ sản xuất (`brief.json` và `content.json` chuẩn Schema 3.0) để chuyển giao cho các khâu tiếp theo của Video Pilot.

---

## 1. Cấu Trúc Tổng Quan Của Hồ Sơ Kỹ Thuật (Blueprint Architecture)

Hồ sơ bàn giao gồm 2 tệp JSON chính đặt trong thư mục `sys/runs/<job>/`:
1. `brief.json`: Định nghĩa yêu cầu đề tài, đối tượng, thời lượng, dữ liệu nguồn (`sources`) và các ý bắt buộc (`required_points`).
2. `content.json`: Định nghĩa kịch bản 5 hồi, nhân vật, phân cảnh, phân tầng hình ảnh, các nhịp chuyển động (`beats[]`), bảng ánh xạ `coverage` và các khẳng định dữ kiện `claims`.

---

## 2. Tiêu Chuẩn Kỹ Thuật Cho Từng Khâu Downstream

### 2.1. Hợp đồng Âm thanh (Audio & TTS Contract)
- **Công thức tính âm tiết:**
  $$\text{Target Syllables} = \text{round}\Big((\text{Scene Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0\Big)$$
- **Tham số đuôi audio ($P_{\text{tail}}$):**
  - Cảnh trung gian (SC01 – SC04): $0.70\text{s}$ (`DEFAULT_PAUSE['para']`).
  - Cảnh kết thúc (SC05): $0.35\text{s}$ (`DEFAULT_PAUSE['tail']`).
- **Ký hiệu ngắt giọng kịch tính:**
  - Viết rõ ràng dưới dạng `[pause:800ms]` hoặc `[pause:900ms]`.
  - Bộ kiểm định âm học tự động trừ thời lượng pause vào ngân sách âm tiết.
- **Tiêu chuẩn chất lượng:**
  - Tốc độ đọc: $3.2 \le \text{Rate} \le 4.5$ âm tiết/s.
  - Độ lệch timeline so với target duration: $\le 0.3\text{s}$.

### 2.2. Hợp đồng Tạo hình (Flow CDP & Visual Layering Contract)
Để hỗ trợ hiệu ứng phân lớp cắt dán (Layered Cut-out Motion):
- **Phân tách Plate vs Sticker:**
  - **Background Plate (`kind: "background"`):** Ảnh nền bối cảnh thuần túy, tuyệt đối không chứa người hoặc đạo cụ chuyển động. Ví dụ: *"Góc bàn làm việc đêm muộn với ánh đèn học vàng ấm và màn hình laptop mở, phòng tối tĩnh mịch."*
  - **Cut-out Sticker (`kind: "sticker"`):** Chủ thể nhân vật stick-figure hoặc đạo cụ độc lập. Ví dụ: *"Người que stick-figure đầu tròn trắng viền đen dày, biểu cảm bối rối ôm đầu, tay cầm tách cà phê."*
- **Quy chuẩn Stick-Figure Cast Invariant:**
  - Nhân vật stick-figure chuẩn mực: Đầu tròn trắng viền đen dày, mắt chấm/bầu dục tối giản, thân mình một nét mực, tứ chi mảnh khảnh.
  - Vẽ trên nền trắng sáng đồng nhất (isolated on solid white background) với đường viền đen khép kín liên tục (continuous closed black outline) để thuật toán flood-fill bóc nền trong suốt sạch sẽ 100%.
- **Giới hạn Quota Flow:**
  - Mỗi cảnh tạo mới tối đa 4 sticker (`MAX_NEW_STICKERS_PER_SCENE = 4`).
  - Tái sử dụng sticker từ các cảnh trước (`layers[].image_id` trỏ về sticker đã có) để tiết kiệm quota và tạo tính nhất quán.
- **Quy tắc cấm nhãn nội bộ (No Internal Labels In Visible Prompts):**
  - Tuyệt đối không để lộ mã định danh như `SC01`, `CH01`, `SC01_I1` trong trường `description`, `preserve`, `change`, hoặc `visible_text`.

### 2.3. Hợp đồng Dựng Video (Remotion Composition & Visual Beats)
- Để tránh hiện tượng đơ hình (Scene Hold Stagnation), mỗi cảnh dài phải chia thành các nhịp thị giác trong mảng `beats[]`:
  - `anchor.vi.quote`: Trích nguyên văn cụm từ trong lời thoại làm điểm kích hoạt xuất hiện.
  - `occurrence`: Thứ tự xuất hiện của từ/cụm từ trong lời thoại (thường là 1).
  - `effect`: Hiệu ứng chuyển động camera hoặc lớp (`hold`, `zoom_in`, `pan_left`, `pan_right`, `ken_burns`).
  - `focus`: Tọa độ tâm điểm chú ý `{ "x": 0.5, "y": 0.5 }`.
- Điểm neo đầu tiên bắt buộc phải bắt đầu ngay từ đầu lời dẫn (`occurrence: 1`, vị trí ký tự 0). Các nhịp tiếp theo tăng dần theo thứ tự lời thoại.

### 2.4. Hợp đồng Âm thanh Hiệu ứng (Semantic SFX / Foley Cues)
- Xác định các điểm neo âm thanh đặc trưng trong lời dẫn:
  - Tiếng tích tắc đồng hồ hoặc gõ phím gấp gáp ở SC01.
  - Tiếng còi báo động hoặc tiếng hổ gầm trầm thấp ở SC03.
  - Tiếng mở cửa tủ lạnh hoặc tiếng thở phào nhẹ nhõm ở SC05.

### 2.5. Hợp đồng Pháp lý, Tính Toàn Vẹn & Tỷ Lệ Đa Dạng (Legal, Integrity & Multi-Output Contract)
- **Tính toán mã băm Brief Hash bất biến (`brief_hash`):**
  - `brief_hash` trong `content.json` bắt buộc phải là mã SHA-256 tính trên chuỗi JSON tuần tự hóa canonical của `brief.json` (`indent=2`, `ensure_ascii=False`).
  - Khớp 100% với hàm `digest(p/'briefs/1.json')` của bộ điều phối `pilot.py`, ngăn chặn hoàn toàn lỗi từ chối bản nháp `BRIEF_VERSION: Sai phiên bản yêu cầu`.
- **Hỗ trợ Tỷ lệ Kép (`aspect_ratio: "dual"`) & Đa Ngữ (Bilingual):**
  - Khi cấu hình `aspect_ratio: "dual"`, mảng `outputs` trong `brief.json` phải tách bạch thành 2 bản ghi: `9:16` (subtitles: true) và `16:9` (subtitles: false) theo đúng chuẩn `output_contract.py`.
  - Khi có kênh ngôn ngữ tiếng Anh (`en`), mọi `beats[]` và `layers[]` phải có cả 2 điểm neo `vi` và `en`, và bảng `coverage` phải cung cấp `quote_en` trích nguyên văn từ `narration_en`.
- **Bảng `sources` trong `brief.json`:** Khai báo đầy đủ `id`, `title`, `author`, `year`, `reference`, và mảng `facts`.
- **Bảng `required_points` trong `brief.json`:** Mỗi ý có một `id` duy nhất (`R01`, `R02`...) và nội dung tóm tắt.
- **Bảng `coverage` trong `content.json`:**
  - Mỗi ý bắt buộc phải được ánh xạ tới ít nhất một cảnh.
  - Trường `quote` phải trích dẫn nguyên văn 100% từ `narration` của cảnh đó.
- **Bảng `claims` trong `content.json`:**
  - Mọi phát biểu khoa học phải có bản ghi claim trỏ tới `scene_id`, `source_id`, `fact`, và `quote`.
  - Khẳng định tính trung thực học thuật 100%.

---

## 3. Quy Trình Kiểm Thử & Nghiệm Thu Blueprint

Trước khi chuyển giao hồ sơ cho khâu sản xuất, công cụ kiến trúc phải tự động chạy thẩm định:
1. `validate_brief(ROOT, brief_data)` trong `sys/content_contract.py`.
2. `validate_content(ROOT, brief_data, 1, brief_hash, content_data)` trong `sys/content_contract.py`.
3. `script_cadence_checker.py` kiểm định độ lệch âm học ($\le 0.3\text{s}$) và tốc độ nói.
