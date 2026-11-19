# KẾ HOẠCH CHI TIẾT KÊNH: CƠ THỂ KỂ (`co_the_ke`) — v3.0

## 1. Định Vị Kênh & Khán Giả Mục Tiêu (Dữ Liệu Studio Thực Tế)
- **Mã kênh:** `co_the_ke` (`@CoTheKeVN` — Channel ID: `UCgehIaP3nZ5jdcZfI3eI7RQ`, Chrome `profile_1`, cổng `9225`, email `phuocnguyen010204@gmail.com`)
- **Ngách nội dung:** Giải phẫu 3D y sinh, sinh học cơ thể người, thần kinh học và miễn dịch học thực chiến
- **Lời hứa thương hiệu (Value Proposition):** Giải mã những phản ứng kỳ diệu bên trong cơ thể người bằng mô phỏng giải phẫu 3D y sinh sắc nét và dẫn chứng khoa học xác thực, dễ hiểu cho đời sống hàng ngày.
- **Tệp khán giả xác nhận từ YouTube Studio:**
  - Quốc gia: Việt Nam (`95.87%`)
  - Độ tuổi cốt lõi: 25–34 (`38.66%`) + 35–44 (`39.46%`) = **`78.12%` người trưởng thành quan tâm sức khỏe & hiệu suất sống**
  - Thiết bị: Mobile (`50.4%`) + TV (`40.79%`) — đòi hỏi khung hình **2K `2560x1440` (Long)** / **`1440x2560` (Short)** sạch nét trên màn hình lớn TV 4K lẫn điện thoại.
- **Nhân vật dẫn chuyện (Persona):** Người dẫn chuyện khoa học y sinh điềm tĩnh, đáng tin cậy (`authoritative_calm`), kể trực diện cơ chế sinh học bên trong từng cơ quan.
- **Khóa Giọng Kể & Master Âm Thanh (`VietNarrator_co_the_ke` v3.0):**
  - **Voice lock:** `VietNarrator_co_the_ke` (`sys/assets/voices/ch_co_the_ke/profile.json`, SHA256 `0e5b0ac35ccd31565e31dceabfd20e8f110465ad370b84465f404e1c10f2f490`)
  - **Nhịp độ:** `recommended_speed = 1.12x` (`default_tone = "authoritative_calm"`)
  - **Tone & EQ:** `highpass=f=85,equalizer=f=190:t=q:w=1.2:g=-2.0,equalizer=f=3000:t=q:w=1.2:g=1.4,lowpass=f=13500`
  - **Chuẩn phát sóng (Master Target):** `-11.0 LUFS` / `-1.0 dBTP` (`48kHz` stereo; WAV tham chiếu `-14.0 LUFS / -1.2 dBTP`).

## 2. Phân Tách Định Dạng & Phễu Chuyển Đổi Long <-> Short
- **YouTube Long (`long_16x9` — `2560x1440@30fps` NVENC, `8.5–13 phút` / `510–780s`, `240` beats, `10` chương `00:00..`):**
  - Bỏ vĩnh viễn lối 2D kawaii / stickman cũ của Wave 1 (`ch_organ_buddies`).
  - Dùng `3-Pillar 3D Endoscopic Biomedical Cinematography` + `4 Visual Modes`, dẫn chứng nghiên cứu uy tín (WHO, NIH, AHA, CDC, Walker 2017...), có `End Screens` + `Info Cards` nối vòng các tập dài.
- **YouTube Shorts (`short_9x16` — `1440x2560@30fps` NVENC, `48–60s`, `18` beats, `>= 3` beats trong `0–5s`):**
  - Viết mới bản địa 100% (không cắt thô từ Long), luôn gắn `Related Video` (`parent_long_id`) trỏ thẳng về bản Long cùng chủ đề để biến traffic Shorts (`95.3%` nguồn kênh) thành Watch Time và Subscriber cho kênh.

## 3. Chuẩn Hình Ảnh v3.0: `co_the_ke_3d_biomedical_v3` (2K)
- **Bảng màu khóa cứng:**
  - Deep Biomedical Navy: `#0A192F`
  - Anatomical Slate Shadow: `#0F172A`
  - Clinical X-Ray Cyan: `#06B6D4` (`archetype_3_science_xray` accent)
  - Arterial Danger Crimson: `#EF4444`
  - Clean Laboratory White: `#F8FAFC`
  - Bio-Energy Warm Amber: `#F59E0B`
- **4 Chế độ Hình ảnh (Long 2K):**
  - `MODE_1_BIOMETRIC_STAMP` (~15% beats): Card số liệu sinh học nổi bật (`27 KG`, `70% TẾ BÀO NK`, `02:00 AM`).
  - `MODE_2_NORMAL_VS_STRESS_SPLIT` (~12% beats): Chia đôi Cyan `#06B6D4` (Bình thường) vs Crimson `#EF4444` (Quá tải).
  - `MODE_3_CASCADE_CHECKLIST` (~15% beats): Bảng chuỗi cơ chế `[01]`, `[02]`, `[03]` bên phải khung X-ray 3D.
  - `MODE_4_ENDOSCOPIC_PACING` (~58% beats): Khung 3D nội soi y sinh toàn màn hình `xfade=fade:duration=0.20` + `omni_flash` I2V ở beat đinh.
- **Xử lý góc phải dưới & Watermark:** Áp dụng crop overscan `1.045x` + `delogo` góc phải dưới **trước khi** chèn `sys/channels/co_the_ke/assets/watermark_150x150.png` (`150x150` RGBA) tại `W-w-48:H-h-48` (2K) / `W-w-36:H-h-36` (HD).
- **Luật Thumbnail Flow-Native (`< 2MB`):** Cảnh 3D y sinh đắt giá + `2–4` từ in hoa tiếng Việt sắc nét đúc trực tiếp trong cảnh Flow (cấm PIL/HTML đè chữ thô, cấm dấu `✦`).

## 4. Luật Kịch Bản, An Toàn Y Khoa & Bộ Tag Chuẩn
- **Hook & Open Loop:** Beat 1 `<= 18` âm tiết (Short) / `<= 24` (Long), zero `[pause:...]`; câu 2–4 gài nghịch lý sinh học (`nhưng`, `hóa ra`, `bên trong`).
- **Quy tắc CTA (Tuyệt đối tuân thủ):** CẤM "like, share, subscribe, đăng ký kênh", CẤM `#learnontiktok`. Chỉ dùng câu hỏi sức khỏe / hành động thực tế + cầu nối sang **"Cơ Thể Kể"** (`<= 20` âm tiết ở 15% cuối Short).
- **An toàn y khoa:** Không khẳng định "chữa khỏi bệnh", không quảng cáo thực phẩm chức năng thiếu bằng chứng; luôn nêu nguồn tham khảo xác thực trong mô tả.
- **Hashtag chuẩn:** `#CoTheKe #KhoaHocCoThe #GiaiPhau3D #SucKhoeKhoaHoc #SinhHoc`

## 5. Tài Sản Video Đang Lưu Hành & Lộ Trình Bảo Toàn (KHÔNG XÓA VIDEO CŨ)
- **Week 1 Pair:** Long `yl8E1WKjvWY` (*24 Giờ Thức Trắng: Tim, Gan Và Não Gánh Ra Sao?*) <-> Short `LdlG4OiEjR8`
- **Batch 2 Pair:** Long `_JaLpnPf-q4` (*Cà Phê Lúc Đói: Dạ Dày Và Cortisol Trả Giá Ra Sao?*) <-> Short `MPnDTlsIPUw`
- **Batch 3 Pair:** Long `e3AElaVVXJ4` (*Bỏ Bữa Sáng 30 Ngày: Cơ Thể Đốt Mỡ Hay Tự Hủy Cơ?*) <-> Short `5vtJPGj_qM0`
- **Pilot 4 + 1:** Long `sgp65IoBMa8` (*24h Không Ngủ: Não 'Tự Ăn' & 70% Tế Bào Sát Thủ Tê Liệt*) (đang khuyết Short đôi — **NV #1 V3 2K sẽ sản xuất & ghép `related_video -> sgp65IoBMa8`**) & Short `-dNqAE-nzf0` (*TẠI SAO DA BẠN TỰ SẠM ĐI? Bí mật Tế Bào Sắc Tố...*)
- **Top 4 Danh sách phát công khai (Playlists):**
  1. `Cơ Thể Kể — Giải Mã Cơ Thể Chuyên Sâu (16:9)`
  2. `Phản Xạ Cơ Thể 60 Giây (Shorts)`
  3. `Giấc Ngủ, Não Bộ & Nhịp Sinh Học`
  4. `Dinh Dưỡng, Chuyển Hóa & Thói Quen Sống`

## 6. Khóa Sản Xuất V3 & SSOT Skill Đặc Thù Riêng Kênh
- **SSOT Skill:** [.agents/skills/vp-channel-co-the-ke/SKILL.md](../../../.agents/skills/vp-channel-co-the-ke/SKILL.md) (kèm [visual-grammar-biomedical-v3.md](../../../.agents/skills/vp-channel-co-the-ke/references/visual-grammar-biomedical-v3.md) và [pacing-and-script-rules.md](../../../.agents/skills/vp-channel-co-the-ke/references/pacing-and-script-rules.md))
- **File Khóa Tham Số:** [channel_v3_production_lock.json](channel_v3_production_lock.json) (`LOCKED_PRODUCTION_V3`)
