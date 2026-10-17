#!/usr/bin/env python3
"""
Đồng bộ đường dẫn máy đích sau khi giải nén gói dự án Video Pilot.
Cập nhật trường `project` trong `sys/.state/grants.json` và các đường dẫn markdown
trong `sys/runs/*/checkpoints/*/1/review.md` về đúng thư mục hiện tại trên máy của bạn.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYS = ROOT / "sys"
GRANTS_FILE = SYS / ".state/grants.json"

def main() -> int:
    new_root_str = str(ROOT)
    updated_grants = 0
    old_roots = set()

    if GRANTS_FILE.is_file():
        data = json.loads(GRANTS_FILE.read_text(encoding="utf-8"))
        for g in data.get("grants", []):
            old_p = g.get("project")
            if old_p and old_p != new_root_str:
                old_roots.add(old_p)
                g["project"] = new_root_str
                updated_grants += 1
        GRANTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    updated_reviews = 0
    for rev_md in (SYS / "runs").glob("*/checkpoints/*/*/review.md"):
        txt = rev_md.read_text(encoding="utf-8")
        new_txt = txt
        for old_p in old_roots:
            new_txt = new_txt.replace(old_p, new_root_str)
        if new_txt != txt:
            rev_md.write_text(new_txt, encoding="utf-8")
            updated_reviews += 1

    print(f"[+] Đã đồng bộ đường dẫn gốc của dự án về: {new_root_str}")
    print(f"    - Số quyền (grants) đã cập nhật: {updated_grants}")
    print(f"    - Số file review.md đã cập nhật đường dẫn: {updated_reviews}")
    print("\n[*] Danh sách các Job đã hoàn tất Outline & Dialogue (sẵn sàng chạy Audio -> Images -> Render):")
    for job_dir in sorted((SYS / "runs").iterdir()):
        if job_dir.is_dir():
            print(f"    - {job_dir.name}")
    print("\n[*] Bước tiếp theo trên máy của bạn:")
    print("    1. Mở Dashboard hoặc gắn phiên Colab T4 + Chrome Flow CDP:")
    print("       cd sys && python3 pilot.py bind-session <JOB_ID> --session <SESSION_ID> --source \"Bind local Colab and Flow session\"")
    print("    2. Chạy tiếp từ bước Audio -> Images -> Video Render:")
    print("       cd sys && python3 pilot.py run <JOB_ID>")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
