# KẾ HOẠCH CHI TIẾT KÊNH: HỒ SƠ KỲ LẠ (`ho_so_ky_la`) — v3.0

## 1. Định Vị Kênh & Phân Tách Nền Tảng
- **Mã kênh:** `ho_so_ky_la` (`@HoSoKyLaVN` — Channel ID: `UCEWZEZJTFpNCbURgtNLHA1A`)
- **Nhánh GitHub độc lập:** `channel/ho-so-ky-la` (`origin/channel/ho-so-ky-la`)
- **Ngách nội dung:** Bí ẩn lịch sử, thảm họa kỹ thuật và hồ sơ pháp y có thật trên thế giới
- **Lời hứa thương hiệu (Value Proposition):** Giải mã những hồ sơ kỳ lạ có thật bằng chứng cứ vật lý, mô phỏng hiện trường 3D Noir sắc nét và lập luận khoa học khách quan.
- **Khán giả mục tiêu:** Khán giả trưởng thành 18–45 tuổi yêu thích trinh thám điều tra, tài liệu khoa học, hàng không — hàng hải và bí ẩn lịch sử.
- **Nhân vật dẫn chuyện (Persona):** Điều tra viên hiện trường điềm tĩnh, phân tích sắc sảo từng manh mối theo trình tự phá án.
- **Khóa Giọng Kể & Master Âm Thanh (`VietNarrator_ho_so_ky_la` v3.0):**
  - **Voice lock:** `VietNarrator_ho_so_ky_la` (`sys/assets/voices/ch_ho_so_ky_la/profile.json`, SHA256 `cd25365252033ee60333c92e3f071a8dae3a99c865fe9e527686c7cf04048a9d`)
  - **Nhịp độ:** `recommended_speed = 1.28x` (`base_omnivoice_speed = 1.12`, `atempo = 1.143`, `inter_beat_gap_sec = 0.06s`)
  - **Tone & EQ:** `forensic_investigative_crisp` — `highpass=f=80,equalizer=f=180:t=q:w=1.1:g=1.2,equalizer=f=3200:t=q:w=1.0:g=2.2,equalizer=f=6500:t=q:w=1.2:g=1.5,lowpass=f=15000`
  - **Chuẩn phát sóng (Master Target):** `-11.0 LUFS` / `-1.0 dBTP` (WAV tham chiếu giữ `-14.0 LUFS / -1.2 dBTP`).
- **Phân tách định dạng & phễu chuyển đổi:**
  - **YouTube Shorts (`short_9x16` — 9:16, `1440x2560` / `1080x1920`, `52–60s`):** Mở khóa ngay 3 giây đầu bằng nghịch lý hiện trường, giữ nhịp `2–3.5s/beat`, gắn `related_video` & link phễu dẫn trực tiếp sang bản Long tương ứng. Mục tiêu: Đạt triệu view Viral Discovery + kéo subscriber vào xem Long.
  - **YouTube Long (`long_16x9` — 16:9, `2560x1440` 2K NVENC, `10–14 phút`):** Tối thiểu 10 chương rõ ràng (Timestamps `00:00..`), phân tích từng lớp chứng cứ, đối chiếu giả thuyết, tạo chiều sâu Watch Time > 45% và RPM AdSense cao.

## 2. Kênh Mẫu Tham Chiếu & Tiêu Chuẩn Giữ Chân
- **Short (`short_9x16`):** Khởi đầu ngay giữa chi tiết phi lý nhất -> vòng lặp mở (Open Loop) ở câu 2–3 -> tăng tiến manh mối vật lý -> tiết lộ cơ chế khoa học -> CTA bình luận tranh luận + cầu nối sang video dài cùng vụ án.
- **Long (`long_16x9`):** Cold Open (`<= 24` âm tiết) -> Dossier Setup -> Chuỗi 7–8 manh mối vật lý/kỹ thuật có re-hook mỗi chương -> Cân đo 2–3 giả thuyết -> Nút thắt công nghệ/pháp y chốt hồ sơ -> Tease tập kế tiếp.

## 3. Luật Viết Kịch Bản & Điểm Kiếm Duyệt (`script_hook_scorer.py >= 85/100`)
- **Hook 3 giây đầu:** `<= 18` âm tiết cho Short (`<= 24` âm tiết cho Long), phải chứa yếu tố gợi tò mò (`?`, con số, nghịch lý, sự thật ít ai biết) và đại từ trực diện (`bạn`, `chúng ta`).
- **Open Loop sớm (`sents[1:4]`):** Gài ngay câu hỏi treo hoặc bước ngoặt (`nhưng`, `hóa ra`, `điều kỳ lạ`).
- **Mật độ nhịp:** Short `<= 5.0s/câu` (tổng thời lượng ước tính `220–445` âm tiết ~ `52–103s`), Long `<= 30s/câu` (tổng thời lượng ước tính `3.290–7.417` âm tiết ~ `13–25` phút theo `4.3 syl/s` của bộ chấm điểm).
- **Quy tắc CTA (Tuyệt đối tuân thủ):** CẤM hoàn toàn "like, share, subscribe, đăng ký kênh". Chỉ dùng câu hỏi điều tra tranh luận + hướng dẫn nhấn vào `related_video` / xem trọn hồ sơ dài.
- **Điều cấm kỵ:** Không máu me ghê rợn (no gore), không gán yếu tố siêu nhiên làm kết luận sự thật, không nêu thông tin đời tư cá nhân trong án mới.

## 4. Chuẩn Hình Ảnh v3.0: 3D Noir Forensic Diorama 2K
- **Phong cách chủ đạo:** *3D Noir Forensic Diorama* (Mô hình hiện trường thu nhỏ/điện ảnh 3D tối giản có chiều sâu vật lý, ánh sáng tương phản cao Volumetric Spotlight thay thế cho nét vẽ 2D phẳng cũ).
- **Bảng màu khóa cứng:**
  - Nền bóng đêm điều tra: `#0A0B0E`
  - Bảng hồ sơ / bê tông tối: `#181B22`
  - Giấy chứng cứ / hồ sơ cũ: `#E8DFC8`
  - Nhấn điểm chứng cứ & chỉ đỏ phá án: `#C0392B`
  - Ánh kim đồng thau / hộp đen / ghim bản đồ: `#C9A24D`
- **Thông số Render 2K (`HO_SO_KY_LA_PRODUCTION_LOCK`):**
  - Long `16:9`: `2560x1440` (`30 fps`, `h264_nvenc` trên Colab T4, `xfade=fade 0.24s`).
  - Short `9:16`: `1440x2560` (`30 fps`, `h264_nvenc`).
  - **Xử lý góc phải dưới bắt buộc:** Chạy bộ lọc `delogo` góc phải dưới để xóa sạch dấu Flow AI sparkle **trước khi** chèn `watermark_150x150.png` (`sys/channels/ho_so_ky_la/assets/watermark_150x150.png`) tại `W-w-48:H-h-48` (2K) / `W-w-36:H-h-36` (HD).
- **Luật Thumbnail Flow Native:** Khung hình 3D Noir điểm nhấn chứng cứ rực sáng + chỉ 2–4 từ in hoa đúc trực tiếp trong cảnh Flow (không chèn HTML/PIL đè thô).

## 5. Lộ Trình Hồ Sơ Đang Triển Khai & Tiếp Theo
- **Bộ 4 Hồ Sơ Nền Đã Tối Ưu Studio (Wave 1 Repair):**
  1. `Eu5QbfOg8wA` (`Chuyến Tàu Ma CSX 8888`, 11:51) <-> Short `A2CuZnlIRCg`
  2. `3TXAOpjmNj4` (`Bí Ẩn Tàu Mary Celeste`, 03:29) <-> Short `8CtmTqXCB7k`
  3. `gjx2Gv0GhS0` (`Giải Mã Đèo Dyatlov`, 03:24) <-> Short `bp9U0EtXqks`
  4. `cmYmJfbqJoM` (`Hồ Sơ Somerton Tamám Shud`, 02:49) <-> Short `Z72pJJ1TLGI`
- **Hồ Sơ Số 05 — Chuẩn v3.0 Đầu Tiên (Ready-to-Produce):**
  - **Episode 05 (`ep05_helios_522`):** *Chuyến Bay Ma Helios 522: Vì Sao Cả Khoang Lái Bất Tỉnh Trên Bầu Trời Hy Lạp?*
  - Files: `sys/channels/ho_so_ky_la/ep05_helios_522_v3_blueprint.json`, `ep05_content_short.json`, `ep05_content_long.json`
- **Backlog Hồ Sơ Kỹ Thuật & Hàng Hải Kế Tiếp (Wave 2):**
  - Ep 06: *Vụ Đắm Tàu Titanic vs Giả Thuyết Cháy Hầm Than & Khuyết Tật Đinh Tán*
  - Ep 07: *Thảm Họa Tàu Ngầm Titan: Vật Lý Sụp Nổ Áp Suất Ở Độ Sâu 3.800 Mét*
  - Ep 08: *Sự Cố Tín Hiệu 'Wow!' 1977: 72 Giây Sóng Vô Tuyến Lạ Từ Vũ Trụ*

## 6. Bộ Tag & Hashtag Chuẩn Kênh (Không dùng thẻ sai ngách)
- **Hashtag chuẩn:** `#HoSoKyLa #BiAnCoThat #HoSoDieuTra #GiaiMaBiAn #PhimTaiLieu`
- **CẤM dùng:** `#learnontiktok`, tag tiếng Anh sai tệp khán giả, hoặc chèn `@HoSoKyLaVN` làm dài/xấu tiêu đề video.
- **Lệnh kiểm định kịch bản & test kênh:**
  ```bash
  python3 sys/tools/script_hook_scorer.py --content sys/channels/ho_so_ky_la/ep05_content_short.json --channel ho_so_ky_la --format short_9x16
  python3 sys/tools/script_hook_scorer.py --content sys/channels/ho_so_ky_la/ep05_content_long.json --channel ho_so_ky_la --format long_16x9
  pytest -q sys/tests/test_channel_voice_profiles.py sys/tests/test_channel_ho_so_ky_la.py sys/tests/test_vn_dual_mode_pipeline.py
  ```
