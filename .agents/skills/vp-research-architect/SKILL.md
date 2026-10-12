---
name: vp-research-architect
description: "Architect research-backed 5-part conversational narratives and downstream pipeline blueprints."
---

# VP Research Architect — Research & Narrative Architecture Skill

`vp-research-architect` là bộ kỹ năng thượng nguồn (upstream creative & technical engine) chịu trách nhiệm nghiên cứu đề tài, khai thác cứ liệu học thuật, phát hiện định kiến sai lầm và kiến trúc bộ hồ sơ kỹ thuật hoàn chỉnh (`brief.json` và `content.json` chuẩn Schema 3.0) cho toàn bộ băng chuyền sản xuất Video Pilot.

Kỹ năng này hoạt động như cầu nối giữa **nghiên cứu khoa học uy tín** và **bản thiết kế sản xuất đa phương tiện** (Audio, Flow CDP, Remotion, Foley, Legal Traceability), đảm bảo mọi video đều có chiều sâu trí tuệ, lối kể chuyện cuốn hút của một Conversational Essayist và độ chính xác kỹ thuật tuyệt đối.

---

## 1. Sứ Mệnh & Vai Trò (Core Mission & Role)

- **Vai trò:** **Research & Narrative Architect (Kiến trúc sư Nghiên cứu & Dẫn chuyện)**.
- **4 Tôn chỉ bất biến:** (1) Cứ liệu khoa học chuẩn mực (DOI, ISBN, tác giả, năm); (2) Lật ngược định kiến số đông (*Cognitive Reframe*); (3) Văn phong *Conversational Essayist* ([vp-scriptwriting](../vp-scriptwriting/SKILL.md)); (4) Hợp đồng kỹ thuật Schema 3.0 không lỗi.

---

## 2. Quy Trình 4 Trạm Nghiên Cứu & Kiến Trúc (4-Station Process)

```
[Trạm 1: Fact Mining] ──> [Trạm 2: 5-Part Arc] ──> [Trạm 3: Acoustic Cadence] ──> [Trạm 4: Blueprinting]
```

### Trạm 1: Khai Thác Dữ Kiện & Phát Hiện Định Kiến
- Khai thác nguồn học thuật tin cậy, xác định định kiến sai lầm (*Misconception Anchor*) và điểm neo đời thường (*Daily Life Relatability Anchor*). Chi tiết: [Fact Mining Guide](references/fact-mining-guide.md).

### Trạm 2: Kiến Trúc Cấu Trúc 5 Hồi Dẫn Chuyện
- Ánh xạ nội dung vào khung 5 hồi nhân quả (`SC01` Hook 0–15% $\to$ `SC02` Reframe 15–35% $\to$ `SC03` Causal 70/30 35–65% $\to$ `SC04` Contrast 65–85% $\to$ `SC05` Loop Payoff 85–100%) theo tỷ lệ thời lượng mở của kịch bản/WAV (không áp đặt khung thời lượng cố định). Chi tiết: [Conversational Structuring](references/conversational-structuring.md).

### Trạm 3: Soạn Thảo Lời Thoại & Cân Chỉnh Âm Học
- Tính số âm tiết mục tiêu theo công thức triệt tiêu dead-air $\text{Target Syllables} = \text{round}((\text{Scene Duration} - P_{\text{tail}} - T_{\text{pause}}) \times 4.0)$ (trong đó $P_{\text{tail}} = 0.70\text{s}$ cảnh giữa, $0.35\text{s}$ cảnh cuối, dấu phẩy $0.30\text{s}$) và kiểm định qua `sys/tools/script_cadence_checker.py` ($3.2 \le \text{Rate} \le 4.5$ âm tiết/s, drift $\le 0.3\text{s}$).

### Trạm 4: Đóng Gói Bản Thiết Kế Toàn Pipeline (Downstream Blueprinting)
- Đóng gói hồ sơ Schema 3.0 (`brief.json` & `content.json`) tuân thủ 4 trụ cột chống "AI Feel" (`ERR-20261011-03`):
  1. **Conversational Spoken Facts:** Mọi `facts` và `required_points` trong `brief.json` diễn đạt văn nói tự nhiên $\le 20$ âm tiết (ngưỡng cứng $22$), không chứa `DOI`, `et al.`, `%`, `/` (`check_conversational_spoken_facts()`).
  2. **Editorial Graphic Visuals:** Ưu tiên hình học kiến trúc và tư thế biểu cảm; cấm lặp lại các ẩn dụ cơ khí sáo rỗng (`brain cutaway`, bàn tính, van ống nước, mỏ neo sắt, chia đôi màn hình so sánh).
  3. **Rule-of-Thirds Layering:** Tách biệt Background Plates (`kind: "background"`) và Cut-out Stickers (`kind: "sticker"`), đặt sticker tại tọa độ Quy tắc 1/3 (`x ∈ [0.34, 0.38]` hoặc `[0.62, 0.66]`, chuẩn `RULE_OF_THIRDS_X = (0.35, 0.64)`) thay vì chính giữa `0.50`.
  4. **Semantic Camera Motion:** Gán hiệu ứng qua `select_semantic_camera_effect()` và `assign_scene_camera_effects()`, cấm lặp liên tiếp và cấm xoay vòng `% 5`.
- Khóa từ neo chính xác trong `beats[]` / `layers[]` theo quy tắc **See-Say Sync** (mọi đồ vật, nhân vật, mốc thời gian/con số được nhắc tới trong thoại phải bật sticker/hình ảnh đúng tại cụm từ đó; xem [layer-breakdown](../vp-layered-motion/references/layer-breakdown.md)) và lập bảng truy vết `coverage` + `claims` 100%. Chi tiết: [Pipeline Blueprint Spec](references/pipeline-blueprint-spec.md).

---

## 3. Hợp Đồng Đầu Vào & Đầu Ra (Input/Output Contracts)

### Đầu vào (Input Contract)
1. **Chủ đề nghiên cứu:** Tên đề tài, câu hỏi cốt lõi hoặc bài toán thực tế.
2. **Hồ sơ định dạng (`format_profile`) & Thời lượng (`duration`):** Khai báo rõ `short_9x16` (`9:16`), `long_16x9` (`16:9`), hoặc `dual` (theo SSOT `sys/format_profiles.py`); không khóa cứng thời lượng mặc định (`duration: null` khi để kịch bản và file WAV quyết định tự nhiên, hoặc truyền tùy chọn `min_seconds`/`max_seconds` khi đề bài yêu cầu).
3. **Đối tượng khán giả (`audience`) & Mục tiêu (`goal`):** Yêu cầu chuyển hóa nhận thức cụ thể.

### Đầu ra (Output Contract)
1. **`brief.json` (Schema 3.0):**
   - Đầy đủ `sources` với tác giả, năm công bố, tài liệu tham khảo và danh sách `facts`.
   - Đầy đủ `required_points` độc bản, đại diện cho 5 chặng tư duy.
2. **`content.json` (Schema 3.0):**
   - 100% cảnh có lời thoại đạt chuẩn âm học qua `script_cadence_checker.py` (drift $\le 0.3\text{s}$).
   - Đạt xác thực cấu trúc `validate_brief()` và `validate_content()` trong `sys/content_contract.py`.
   - Không chứa bất kỳ mã nội bộ (`SC01`, `CH01`, `SC01_I1`...) trong mô tả đồ họa hoặc văn bản hiển thị.

---

## 4. Công Cụ Hỗ Trợ Tự Động Hóa

Kiến trúc sư nghiên cứu có thể sử dụng công cụ tự động hóa trung tâm:

```bash
# Tạo bộ blueprint mẫu cho chủ đề thử nghiệm
python3 sys/tools/research_story_architect.py --demo

# Kiểm tra nhịp âm học và độ lệch timeline của kịch bản
python3 sys/tools/script_cadence_checker.py path/to/content.json
```
