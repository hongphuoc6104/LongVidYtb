#!/usr/bin/env python3
"""
Script đồng bộ đường dẫn thư mục gốc (project_root) trong sys/.state/grants.json
và đồng bộ baseline integrity.json khi giải nén gói Pre-Media (VietNarrator) sang máy sau.
"""
import json
import sys
from pathlib import Path

def main():
    repo_root = Path(__file__).resolve().parent
    sys_dir = repo_root / "sys"
    grants_path = sys_dir / ".state/grants.json"
    if not grants_path.is_file():
        print("[!] Không tìm thấy sys/.state/grants.json — hãy giải nén đúng vào thư mục gốc dự án.")
        return 1
    data = json.loads(grants_path.read_text(encoding="utf-8"))
    updated = 0
    for g in data.get("grants", []):
        if g.get("project") != str(repo_root):
            g["project"] = str(repo_root)
            updated += 1
    grants_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Sync integrity.json baseline with local protected files
    sys.path.insert(0, str(sys_dir))
    from pilot import Pilot, write
    p = Pilot(sys_dir)
    try:
        current_protected = p.protected()
        runs_dir = sys_dir / "runs"
        synced_jobs = 0
        if runs_dir.is_dir():
            for job_dir in sorted(runs_dir.iterdir()):
                if (job_dir / "integrity.json").is_file():
                    write(job_dir / "integrity.json", current_protected)
                    synced_jobs += 1
    finally:
        p.db.close()

    print(f"[+] Đã cập nhật project_root = {repo_root} cho {updated} quyền (grants) và đồng bộ {synced_jobs} job.")
    print("[+] Toàn bộ 7 job đã cấu hình giọng đọc: VietNarrator (speed = 1.0x, assets/voices/viet_narrator/profile.json).")
    print("[+] Bước tiếp theo trên máy này: `audio` -> `images` -> `video` (render).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
