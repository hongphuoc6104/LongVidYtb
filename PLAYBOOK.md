# Video Pilot — Sổ Tay Bài Học & Quản Trị Lỗi (PLAYBOOK)

> **Mục đích**: Lưu trữ tri thức kỹ thuật tích lũy, các bài học xương máu và quy tắc phòng ngừa vàng khi phát triển và vận hành hệ thống Video Pilot.
> **Quy chuẩn ghi nhận**: Mọi lỗi sau khi giải quyết thành công bắt buộc phải được ghi lại đầy đủ theo **6 trường chuẩn hóa** bên dưới. Khi file vượt quá 200 dòng hoặc có $\ge 3$ bài học cùng chủ đề, bắt buộc phải trích xuất thành Skill độc lập trong `.agents/skills/`.

---

## I. Quy Trình 4 Bước Khắc Phục Lỗi Tối Thượng
$$\text{1. Tái hiện E2E} \longrightarrow \text{2. Phân tích gốc rễ} \longrightarrow \text{3. Sửa chuẩn kiến trúc} \longrightarrow \text{4. Kiểm chứng E2E & ghi Playbook}$$

---

## II. Danh Mục Bài Học & Sự Cố Chuẩn Hóa

### [ERR-20261009-01] Render Chậm Đột Biến (14m/64s) & Biến Dạng Viền Khung Do Blanket `line_boil` Trên Colab T4
- **Triệu chứng (Symptom):** Quá trình render video trên Colab T4 kéo dài bất thường (14 phút cho 64.25s video), khung hình xuất hiện răng cưa đứt đoạn màu đen ở mép viền trên/trái và dung lượng MP4 phình to gấp đôi.
- **Tái hiện E2E (Reproduction Path):** Chạy lệnh render chương 1 với cờ `line_boil: true` áp dụng hàng loạt trên tất cả các shot 1080p:
  ```bash
  python3 sys/exports/ancient_humans_flowkit_bundle/scripts/render_all_on_colab.py 1 --force --no-concat
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Trên môi trường headless Colab T4, Chromium bắt buộc phải chạy cờ `--disable-gpu-rasterization` để chống lỗi rơi tile trắng. Việc bật `line_boil: true` áp bộ lọc SVG `<feTurbulence>` và `<feDisplacementMap>` lên toàn bộ khung hình raster $1920 \times 1080$ khiến CPU phải tính toán Perlin noise trên hơn 2 triệu điểm ảnh mỗi frame bằng phần mềm (chỉ có 2 vCPU). Đồng thời, phép dịch chuyển điểm ảnh kéo các pixel ngoài biên vào trong khung hình.
- **Giả định sai (Wrong Assumptions):** Nhầm tưởng hiệu ứng rung viền `line_boil` có thể áp dụng tùy tiện cho mọi ảnh nền full-frame mà không gây sụt giảm hiệu năng trên máy ảo không có GPU rasterization.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Gỡ bỏ `line_boil: true` khỏi các shot full-bleed 1080p, chỉ sử dụng camera transitions tích hợp của Remotion (`zoom_in`, `pan_left`, `shake`). Kiểm chứng bằng `ffprobe` trên video output xác nhận thời gian render giảm xuống mức lý tưởng và hình ảnh sắc nét, không răng cưa viền.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Không bao giờ bật SVG `line_boil` trên toàn khung hình raster 1080p khi chạy Remotion trên Colab T4; chỉ dùng animation chuyển động camera hoặc CSS jitter cho sticker layer tách nền.

### [ERR-20261009-02] Lỗi Mất Phiên Colab Khi Upload Gói Build Render
- **Triệu chứng (Symptom):** Lệnh upload file zip build sang Colab báo lỗi `No active sessions found on server` và `CalledProcessError non-zero exit status 1`.
- **Tái hiện E2E (Reproduction Path):**
  ```bash
  account_cli.py upload -s video-pilot-tts /tmp/ch1_build.zip /content/ch1_build.zip
  ```
- **Nguyên nhân cốt lõi (Root Cause):** Phiên làm việc Colab `video-pilot-tts` tự động ngắt kết nối do không hoạt động (idle timeout). Script upload không thực hiện kiểm tra trạng thái liveness trước khi truyền file.
- **Giả định sai (Wrong Assumptions):** Giả định phiên Colab luôn tồn tại sẵn từ trước.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Bổ sung hàm tự phục hồi `ensure_colab_render_runtime()` tự động kiểm tra danh sách session, khởi tạo phiên mới `--gpu T4` khi cần và cài đặt sẵn wrapper headless Chromium trước khi upload.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Mọi tác vụ giao tiếp Colab đều phải có tầng kiểm tra phiên tự phục hồi (Self-Healing Session Liveness) trước khi thực hiện thao tác IO.

### [ERR-20261009-03] Tràn Quota Flow CDP Khi Tạo Ảnh Đồng Thời Đa Profile
- **Triệu chứng (Symptom):** Quá trình sinh ảnh hàng loạt gặp lỗi `PUBLIC_ERROR_UNUSUAL_ACTIVITY` hoặc timeout quá 120s khi tạo nhiều prompt liên tiếp.
- **Tái hiện E2E (Reproduction Path):** Chạy 1 profile đơn lẻ tạo liên tục $> 5$ ảnh cùng lúc không nghỉ.
- **Nguyên nhân cốt lõi (Root Cause):** Hệ thống Flow CDP của Google áp dụng rate-limit theo IP/Profile khi tần suất submit prompt quá dày đặc hoặc thiếu độ trễ điều hòa.
- **Giả định sai (Wrong Assumptions):** Cho rằng 1 tài khoản có thể xử lý luồng tạo ảnh liên tục mà không bị giới hạn tần suất.
- **Giải pháp & Kiểm chứng (Resolution & E2E Proof):** Tách luồng thành cơ chế 3 Chrome profile song song, chia patch nhỏ (2-4 shots/patch), tự động failover sang profile khác khi gặp lỗi và chờ cooldown an toàn.
- **Quy tắc phòng ngừa vàng (Golden Rule):** Luôn điều phối tạo ảnh qua patch nhỏ và cơ chế phân phối tải đa profile; không bao giờ dồn tải tuần tự trên 1 profile duy nhất.
