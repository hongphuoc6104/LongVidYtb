# `heavy_local/` — Kho Lưu Trữ File Nặng & Dữ Liệu Lớn Cục Bộ

Thư mục chuyên dụng để lưu các tệp kích thước lớn (`> 1,024 KB`), dữ liệu JSON/research quá dài (`> 2,000` dòng) hoặc các bản dựng nặng cục bộ mà không làm phình lịch sử Git hay vi phạm `.githooks/pre-commit`.

## Quy tắc
- **Git:** Toàn bộ nội dung trong `/heavy_local/*` được bỏ qua trong `.gitignore` (chỉ file `README.md` này được track).
- **Bảo trì:** Không bị xóa bởi `sys/scripts/clean_production.py --periodic` (an toàn hơn `sys/scratch/`).
- **Liên kết:** Khi code cục bộ cần đọc từ vị trí cũ trong `sys/`, giữ symlink tương đối trỏ về `heavy_local/`.

## Cấu trúc thư mục con
- `audio/` — Các file BGM/SFX `.wav` dung lượng lớn (`> 1 MB`).
- `data/` — Các file JSON/vault/research dung lượng lớn (`> 2,000` dòng).
- `web/` — Các bundle JS/HTML/CSS cỡ lớn.
- `scripts/` — Các script đơn lẻ hoặc demo cỡ lớn không cần đưa lên Git.
