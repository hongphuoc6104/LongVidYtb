#!/usr/bin/env python3
"""Adversarial Critique Scanner & HTML Report Generator (Station 1).

Performs critical pre-flight checks:
1. Colab GPU T4 Headless Safety Flags (prevents white tile drops & crashes).
2. Secret & Credential Leakage Scanner (ensures tokens/keys are not committed).
3. Visual Cast & Script Invariants (stick-figure rules & vocabulary preservation).
4. Root Directory Hygiene (verifies zero clutter in root).

Generates a modern, self-contained HTML report at sys/reports/critique_review.html.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple


def scan_critique(root_dir: Path) -> Tuple[bool, Dict[str, any]]:
    root = Path(root_dir).resolve()
    sys_dir = root / "sys"
    checks = []

    # Check 1: Root directory hygiene
    root_files = [
        f.name
        for f in root.iterdir()
        if f.is_file() and not f.name.startswith(".")
    ]
    allowed_root_files = {
        "AGENTS.md", "GEMINI.md", "INDEX.md", "README.md", "PLAYBOOK.md",
        "pilot.py", "pipeline", "pyproject.toml", "implementation_plan.md", "treehouse.json"
    }
    unexpected_root = [f for f in root_files if f not in allowed_root_files]
    checks.append({
        "name": "Root Directory Hygiene",
        "category": "Architecture Invariant",
        "status": "PASS" if not unexpected_root else "FAIL",
        "detail": (
            "Thư mục gốc sạch sẽ, chỉ chứa các tệp điều phối và tài liệu được cấp phép."
            if not unexpected_root
            else f"Phát hiện tệp lạ trong thư mục gốc: {', '.join(unexpected_root)}"
        ),
    })

    # Check 2: Headless Colab Safety Flags
    wrapper_path = sys_dir / "colab_bridge/chrome-wrapper.sh"
    renderer_path = sys_dir / "renderer/render.mjs"
    mandatory_flags = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu-rasterization",
        "--run-all-compositor-stages-before-draw",
    ]
    colab_flag_missing = []

    checked_files = [wrapper_path, renderer_path]
    combined_content = ""
    for cf in checked_files:
        if cf.is_file():
            combined_content += cf.read_text(encoding="utf-8", errors="ignore")

    for pyf in (sys_dir / "colab_bridge").glob("*.py"):
        combined_content += pyf.read_text(encoding="utf-8", errors="ignore")

    for flag in mandatory_flags:
        if flag not in combined_content:
            colab_flag_missing.append(flag)

    env_var_ok = "DISABLE_FROM_SURFACE" in combined_content

    colab_ok = len(colab_flag_missing) == 0 and env_var_ok
    checks.append({
        "name": "Headless Colab T4 Safety Flags",
        "category": "Environment Risk",
        "status": "PASS" if colab_ok else "WARN",
        "detail": (
            "Đã cấu hình đủ cờ an toàn Chromium chống rơi tile và tràn bộ nhớ /dev/shm."
            if colab_ok
            else f"Thiếu cờ an toàn hoặc biến môi trường: {', '.join(colab_flag_missing)}"
            + (" (Thiếu DISABLE_FROM_SURFACE)" if not env_var_ok else "")
        ),
    })

    # Check 3: Secret & Credential Leakage Scanner
    key_tag = "PRIVATE" + " " + "KEY"
    suspicious_patterns = [
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
        (r"eyJhbGciOi[a-zA-Z0-9_-]{20,}", "Raw JWT Bearer Token"),
        (rf"-----BEGIN {key_tag}-----", "Raw Private Key"),
    ]
    leaks_found = []
    for text_file in list(sys_dir.rglob("*.py"))[:100]:
        # Exclude venv, cache, and conveyor's own scanner
        if "venv" in str(text_file) or ".cache" in str(text_file) or "conveyor" in str(text_file):
            continue
        try:
            content = text_file.read_text(encoding="utf-8", errors="ignore")
            for pattern, desc in suspicious_patterns:
                if re.search(pattern, content):
                    leaks_found.append(f"{text_file.name}: {desc}")
        except Exception:
            pass

    checks.append({
        "name": "Secret & Credential Scanner",
        "category": "Security Boundary",
        "status": "PASS" if not leaks_found else "FAIL",
        "detail": (
            "Không phát hiện khóa bí mật hay access token hardcode trong mã nguồn."
            if not leaks_found
            else f"Phát hiện nghi vấn rò rỉ secret: {'; '.join(leaks_found[:3])}"
        ),
    })

    # Check 4: Stick-figure Visual Cast Invariant
    compiler_path = sys_dir / "flow_prompts/compiler.py"
    registry_path = sys_dir / "flow_prompts/versions/1.2.0/registry.json"
    cast_ok = False
    cast_detail = "Visual cast tuân thủ chuẩn anonymous stick-figure."

    if compiler_path.is_file() and registry_path.is_file():
        compiler_code = compiler_path.read_text(encoding="utf-8", errors="ignore")
        registry_code = registry_path.read_text(encoding="utf-8", errors="ignore")
        if "stick-figure" in compiler_code.lower() and "stick figure" in registry_code.lower():
            cast_ok = True

    checks.append({
        "name": "Visual Cast Invariant (Stick-Figure)",
        "category": "Anti-Hallucination Guard",
        "status": "PASS" if cast_ok else "WARN",
        "detail": cast_detail if cast_ok else "Thiếu định nghĩa anonymous stick-figure trong flow_prompts.",
    })

    # Overall Status
    has_fail = any(c["status"] == "FAIL" for c in checks)
    is_passed = not has_fail

    summary = {
        "timestamp": datetime.now().isoformat(),
        "passed": is_passed,
        "checks": checks,
    }
    return is_passed, summary


def generate_critique_html(summary: Dict[str, any], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = summary.get("timestamp", datetime.now().isoformat())
    is_passed = summary.get("passed", False)
    checks = summary.get("checks", [])

    rows_html = ""
    for c in checks:
        badge_class = "badge-pass" if c["status"] == "PASS" else ("badge-warn" if c["status"] == "WARN" else "badge-fail")
        icon = "✓" if c["status"] == "PASS" else ("⚠" if c["status"] == "WARN" else "✗")
        rows_html += f"""
        <tr>
          <td><span class="badge {badge_class}">{icon} {c['status']}</span></td>
          <td><strong>{c['name']}</strong></td>
          <td><span class="category-tag">{c['category']}</span></td>
          <td class="detail-cell">{c['detail']}</td>
        </tr>
        """

    overall_badge = '<span class="status-badge green">CRITIQUE PASSED</span>' if is_passed else '<span class="status-badge red">ACTION REQUIRED</span>'

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Video Pilot — Adversarial Critique Report</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --pass: #22c55e;
      --warn: #f59e0b;
      --fail: #ef4444;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 30px;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
    }}
    header {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px 30px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    h1 {{
      margin: 0 0 6px 0;
      font-size: 24px;
      font-weight: 700;
      color: var(--accent);
    }}
    .subtitle {{
      color: var(--text-muted);
      font-size: 14px;
    }}
    .status-badge {{
      font-size: 14px;
      font-weight: 700;
      padding: 8px 16px;
      border-radius: 9999px;
      letter-spacing: 0.5px;
    }}
    .status-badge.green {{
      background: rgba(34, 197, 94, 0.2);
      color: var(--pass);
      border: 1px solid var(--pass);
    }}
    .status-badge.red {{
      background: rgba(239, 68, 68, 0.2);
      color: var(--fail);
      border: 1px solid var(--fail);
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }}
    th {{
      padding: 12px;
      border-bottom: 2px solid var(--border);
      color: var(--text-muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    td {{
      padding: 16px 12px;
      border-bottom: 1px solid var(--border);
      font-size: 14px;
      vertical-align: middle;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
    }}
    .badge-pass {{ background: rgba(34, 197, 94, 0.15); color: var(--pass); }}
    .badge-warn {{ background: rgba(245, 158, 11, 0.15); color: var(--warn); }}
    .badge-fail {{ background: rgba(239, 68, 68, 0.15); color: var(--fail); }}
    .category-tag {{
      background: #334155;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      color: #cbd5e1;
    }}
    .detail-cell {{
      color: #e2e8f0;
      line-height: 1.5;
    }}
    footer {{
      margin-top: 24px;
      text-align: center;
      font-size: 13px;
      color: var(--text-muted);
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>Trạm 1: Phản Biện & Ranh Giới An Toàn</h1>
        <div class="subtitle">Video Pilot No-Mistake Conveyor | Thời gian kiểm tra: {timestamp}</div>
      </div>
      <div>
        {overall_badge}
      </div>
    </header>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th style="width: 15%">Kết Quả</th>
            <th style="width: 30%">Hạng Mục Kiểm Tra</th>
            <th style="width: 20%">Phân Loại</th>
            <th style="width: 35%">Chi Tiết & Khuyến Nghị</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>

    <footer>
      Video Pilot Automated Quality Assurance • Báo cáo tạo tự động bởi Conveyor Station 1
    </footer>
  </div>
</body>
</html>
"""
    output_path.write_text(html_content, encoding="utf-8")


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).resolve().parents[2]
    out_file = repo_root / "sys/reports/critique_review.html"
    passed, res = scan_critique(repo_root)
    generate_critique_html(res, out_file)
    print(f"Critique report generated: {out_file} (Passed: {passed})")
    sys.exit(0 if passed else 1)
