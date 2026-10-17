# Hướng Dẫn Chạy Tiếp Phần Âm Thanh, Tạo Hình & Render Trên Máy Của Bạn

Gói dự án này đã được chuẩn bị sẵn toàn bộ các khâu thượng nguồn (**Brief -> Outline -> Dialogue/Content -> Kiểm định Cadence & Anti-Flop -> Khởi tạo Job Engine v4 -> Biên dịch trước Request Colab TTS & Prompt Ảnh Flow**) và đã vá các lỗi chặn pipeline.

## 1. Các Job đã tạo sẵn trong `sys/runs/` và `prebuilt_packages/`

| Mã Job (`JOB_ID`) | Định dạng | Hồ sơ nhịp hình | Số cảnh | Số ảnh (`planned_units`) | Số câu TTS (`items`) | Trạng thái hiện tại | Bước kế tiếp trên máy bạn |
|---|---|---|---|---|---|---|---|
| `full-frame-16x9-001` | `16:9` (`long_16x9`) | `full_frame_v1` | 19 | 153 | 135 | Đã xong `outline` & `dialogue` | `audio` -> `images` -> `video` |
| `academic-paradox-q1-16x9` | `16:9` (`long_16x9`) | Chuẩn 5 cảnh + 3 Spin-offs | 5 | 40 | 12 | Đã xong `outline` & `dialogue` | `audio` -> `images` -> `video` |
| `academic-q1-short-t1` | `9:16` (`short_9x16`) | Spin-off Tầng 1 (Phễu Rộng) | 5 | 40 | 12 | Đã xong `outline` & `dialogue` | `audio` -> `images` -> `video` |
| `academic-q1-short-t2` | `9:16` (`short_9x16`) | Spin-off Tầng 2 (Hội đồng 120s) | 5 | 40 | 12 | Đã xong `outline` & `dialogue` | `audio` -> `images` -> `video` |
| `academic-q1-short-t3` | `9:16` (`short_9x16`) | Spin-off Tầng 3 (Gap Matrix) | 5 | 40 | 12 | Đã xong `outline` & `dialogue` | `audio` -> `images` -> `video` |
| `procrastination-paradox-16x9-001` | `16:9` (`long_16x9`) | Demo Benchmark 5 cảnh | 5 | 39 | 11 | Đã xong `outline` & `dialogue` | `audio` -> `images` -> `video` |

Trong mỗi thư mục `sys/runs/<JOB_ID>/precompiled_requests/` (và `prebuilt_packages/<JOB_ID>/`), bạn cũng có sẵn:
- `brief.json`, `outline.json`, `content.json`, `script.json`
- `cadence_report.json`, `diversity_report.json`
- `request-colab.json`: Gói yêu cầu tổng hợp giọng đọc `VietNarrator` (`speed: 1.0`, `assets/voices/viet_narrator/profile.json`) gửi lên Colab T4 (`OmniVoice`).
- `planned_image_units.json`: Toàn bộ danh sách đơn vị ảnh toàn khung (`kind: "scene"`), `shot_type`, liên kết `based_on` và prompt chi tiết gửi qua Google Flow CDP.

## 2. Cách chạy tiếp trên máy của bạn (3 bước)

### Bước 1: Giải nén và đồng bộ đường dẫn máy đích
Vì `sys/.state/grants.json` lưu đường dẫn tuyệt đối của thư mục dự án, ngay sau khi giải nén file zip trên máy của bạn, hãy chạy:
```bash
python3 sys/scripts/prepare_local_machine.py
```

### Bước 2: Gắn phiên tài khoản Google Colab T4 & Chrome Flow CDP của máy bạn
Đảm bảo bạn đã đăng nhập tài khoản Colab và Chrome Flow (qua dashboard hoặc `scripts/bootstrap.py`), sau đó gắn session vào job bạn muốn chạy (ví dụ `full-frame-16x9-001`):
```bash
cd sys
python3 pilot.py bind-session full-frame-16x9-001 --session <SESSION_ID_CỦA_BẠN> --source "Bind local Colab T4 and Flow session"
```

### Bước 3: Chạy phần Âm thanh (`audio`), Tạo hình (`images`) và Render (`video`)
```bash
cd sys
python3 pilot.py observe full-frame-16x9-001
python3 pilot.py run full-frame-16x9-001
```
Hệ thống sẽ tự động bắt đầu ngay từ checkpoint **`audio`** (bỏ qua `outline` và `dialogue` vì đã hoàn tất), tiếp tục sang **`images`** (Flow CDP) và **`video`** (Colab Remotion H.264 NVENC), rồi xuất MP4/SRT cuối cùng ra `video/<JOB_ID>/`.
