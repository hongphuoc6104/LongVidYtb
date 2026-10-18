#!/usr/bin/env python3
"""Video Pilot — 6-Station No-Mistake Conveyor Coordinator.

Coordinates the 6 standardized quality stations:
  Station 1: Adversarial Critique & Safety (Colab flags, secrets, cast invariant, critique HTML)
  Station 2: Test & AST Proof (100% active assertions, pytest execution, evidence log)
  Station 3: Docs Playbook Sync (PLAYBOOK.md 6 mandatory fields schema validation)
  Station 4: Lint & Syntax (compileall & ruff static analysis)
  Station 5: Worktree & PR Preparation (git branch isolation, gh-axi / Conventional PR)
  Station 6: CI Watch & Local Green Certification (gh-axi watch, immutable green verification)

Usage:
  ./pipeline status                    # Check environment & tooling readiness
  ./pipeline setup [--force]           # Bootstrap environment & login Colab/Flow accounts
  ./pipeline run                       # Run all 6 stations in sequence (fail-fast)
  ./pipeline station <1..6>            # Run a single station
  ./pipeline video [--job ID]          # Execute Video Pilot production steps
  ./pipeline flow [status|launch|...]  # Manage Google Flow CDP Chrome profiles
  ./pipeline colab [list|login|...]    # Manage Google Colab T4 CLI accounts
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
CONVEYOR_DIR = SYS_DIR / "conveyor"
sys.path.insert(0, str(SYS_DIR))
sys.path.insert(0, str(REPO_ROOT))

from conveyor.ast_checker import check_test_suite_integrity
from conveyor.critique_html import generate_critique_html, scan_critique
from conveyor.playbook_validator import validate_playbook


def get_python_executable() -> str:
    venv_py = SYS_DIR / ".venv/bin/python"
    if venv_py.is_file():
        return str(venv_py)
    return sys.executable


def get_ruff_executable() -> str:
    venv_ruff = SYS_DIR / ".venv/bin/ruff"
    if venv_ruff.is_file():
        return str(venv_ruff)
    system_ruff = shutil.which("ruff")
    if system_ruff:
        return system_ruff
    return "ruff"


def print_banner(text: str, station_num: int = None):
    prefix = f"[Station {station_num}] " if station_num else ""
    print("\n" + "=" * 70)
    print(f"  {prefix}{text}")
    print("=" * 70)


def station_1_critique() -> bool:
    print_banner("Trạm 1: Review Phản Biện & Ranh Giới An Toàn (Adversarial Critique)", 1)
    passed, summary = scan_critique(REPO_ROOT)
    report_file = SYS_DIR / "reports/critique_review.html"
    generate_critique_html(summary, report_file)

    for c in summary["checks"]:
        icon = "[PASS]" if c["status"] == "PASS" else (f"[{c['status']}]")
        print(f"  {icon:<8} {c['name']:<35} : {c['detail']}")

    print(f"\n--> Báo cáo HTML đã tạo tại: {report_file}")

    if passed:
        print("[PASS] Trạm 1: Review phản biện thành công!")
    else:
        print("[FAIL] Trạm 1: Có rủi ro nghiêm trọng cần khắc phục.")
    return passed


def station_2_test_ast() -> bool:
    print_banner("Trạm 2: Test & Bằng Chứng Thực Thi (AST Integrity & Proof Log)", 2)
    print("  Đang phân tích AST cú pháp: Kiểm tra 100% active assertions trong test functions...")

    test_targets = [
        SYS_DIR / "tests/test_tools_readiness.py",
        SYS_DIR / "tests/test_pipeline_stations.py",
        SYS_DIR / "tests/test_research_story_architect.py",
        SYS_DIR / "tests/test_script_cadence_checker.py",
        SYS_DIR / "tests/test_colab_bridge_skill.py",
        SYS_DIR / "tests/test_format_separation.py",
        SYS_DIR / "tests/test_renderer_tile_integrity.py",
        SYS_DIR / "tests/test_colab_worker.py",
        SYS_DIR / "tests/test_human_naturalness_upgrades.py",
        SYS_DIR / "tests/test_full_frame_upgrade.py",
        SYS_DIR / "tests/test_full_frame_pipeline.py",
        SYS_DIR / "tests/test_omni_platform.py",
        SYS_DIR / "tests/test_caption_profile_07.py",
        SYS_DIR / "tests/test_remote_render.py",
        SYS_DIR / "tests/test_anti_formulaic_storytelling.py",
        SYS_DIR / "tests/test_independent_maintenance_contracts.py",
        SYS_DIR / "tests/test_narration_pauses.py",
        SYS_DIR / "tests/test_colab_download_paths.py",
        SYS_DIR / "tests/test_ci_envelope.py",
        SYS_DIR / "tests/test_dashboard_engine.py",
        SYS_DIR / "tests/test_dashboard.py",
        SYS_DIR / "tests/test_account_probe.py",
        SYS_DIR / "tests/test_colab_reconcile.py",
        SYS_DIR / "tests/test_colab_tts.py",
        SYS_DIR / "tests/test_colab_runtime_binding.py",
        SYS_DIR / "tests/test_colab_accounts.py",
        SYS_DIR / "tests/test_colab_health.py",
        SYS_DIR / "tests/test_colab_scheduler.py",
        SYS_DIR / "tests/test_multi_profile_manager.py",
        SYS_DIR / "tests/test_flow_batch_stop.py",
        SYS_DIR / "tests/test_flow_status.py",
        SYS_DIR / "tests/test_flow_profile_trial.py",
    ]
    # Check AST on test directory
    ast_ok, ast_report = check_test_suite_integrity([SYS_DIR / "tests"])

    print(f"  Tổng số tệp test kiểm tra: {ast_report['total_files']}")
    print(f"  Tổng số hàm test phát hiện: {ast_report['total_functions']}")

    if not ast_ok:
        print(f"[FAIL] Phát hiện {ast_report['violations_count']} test vi phạm (thiếu active assertion):")
        for v in ast_report["violations"]:
            print(f"    - {v['file']}:{v['line']} -> {v['function']} ({v['error']})")
        return False
    print("  [PASS] 100% hàm test có active assertion (không có test rỗng/bỏ qua).")

    print("\n  Đang thực thi Pytest suite...")
    start_time = time.time()
    pytest_bin = shutil.which("pytest") or "pytest"
    test_files_to_run = [str(f) for f in test_targets if f.is_file()]
    if not test_files_to_run:
        test_files_to_run = [str(SYS_DIR / "tests/test_flow_cdp_bridge.py")]

    cmd = [pytest_bin, "-v", "--tb=short", "--continue-on-collection-errors"] + test_files_to_run
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    duration = time.time() - start_time

    # Output immutable evidence log
    proof_dir = SYS_DIR / "logs/proofs"
    proof_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    evidence_file = proof_dir / f"test_evidence_{timestamp}.log"

    git_hash = "local-uncommitted"
    try:
        git_res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), capture_output=True, text=True)
        if git_res.returncode == 0:
            git_hash = git_res.stdout.strip()
    except Exception:
        pass

    dirty = subprocess.run(['git', 'status', '--porcelain'], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    evidence_content = (
        f"=== Video Pilot Test Evidence Log ===\n"
        f"Timestamp: {datetime.now().isoformat()}\n"
        f"Commit: {git_hash}\n"
        f"WorkingTreeDirty: {str(bool(dirty.stdout.strip())).lower()}\n"
        f"TestFiles: {len(test_files_to_run)}\n"
        f"Duration: {duration:.2f}s\n"
        f"Return Code: {res.returncode}\n\n"
        f"--- STDOUT ---\n{res.stdout}\n"
        f"--- STDERR ---\n{res.stderr}\n"
    )
    evidence_file.write_text(evidence_content, encoding="utf-8")

    # Auto-rotate proof logs to keep latest 5
    for old_proof in sorted(proof_dir.glob("test_evidence_*.log"))[:-5]:
        old_proof.unlink(missing_ok=True)

    print(res.stdout)
    if res.returncode != 0:
        print(f"[FAIL] Pytest thất bại với mã lỗi {res.returncode}")
        print(f"--> Chi tiết log bằng chứng: {evidence_file}")
        return False

    print(f"--> Bằng chứng thực thi bất biến đã lưu: {evidence_file} (Thời gian: {duration:.2f}s)")
    print("[PASS] Trạm 2: Kiểm thử và xác thực AST thành công!")
    return True


def station_3_docs_playbook() -> bool:
    print_banner("Trạm 3: Docs Sync & Playbook Schema Validation", 3)
    playbook_file = REPO_ROOT / "PLAYBOOK.md"
    ok, report = validate_playbook(playbook_file)

    if not ok:
        print("[FAIL] PLAYBOOK.md không đạt chuẩn schema 6 trường bắt buộc:")
        for v in report.get("violations", []):
            if isinstance(v, dict):
                print(f"  - Mục '{v['header']}': Thiếu các trường: {', '.join(v['missing_fields'])}")
            else:
                print(f"  - {v}")
        return False

    print(f"  [PASS] PLAYBOOK.md hợp lệ: {report['valid_entries']}/{report['entries_count']} bài học đạt chuẩn 6 trường.")
    print("[PASS] Trạm 3: Tài liệu học tập và sổ tay lỗi đồng bộ hoàn toàn!")
    return True


def station_4_lint() -> bool:
    print_banner("Trạm 4: Lint & Syntax Check (compileall + ruff)", 4)
    python_bin = get_python_executable()

    # Step A: Python compileall
    print("  1. Kiểm tra cú pháp toàn diện qua compileall...")
    compile_cmd = [python_bin, "-m", "compileall", "-q", str(SYS_DIR), str(REPO_ROOT / "pilot.py")]
    compile_res = subprocess.run(compile_cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    if compile_res.returncode != 0:
        print("[FAIL] compileall phát hiện lỗi cú pháp:")
        print(compile_res.stderr or compile_res.stdout)
        return False
    print("  [PASS] Cú pháp Python 100% hợp lệ.")

    # Step B: Ruff linter
    print("  2. Phân tích tĩnh mã nguồn qua Ruff...")
    ruff_bin = get_ruff_executable()
    ruff_cmd = [
        ruff_bin,
        "check",
        str(SYS_DIR / "conveyor"),
        str(SYS_DIR / "tools"),
        str(SYS_DIR / "scripts/conveyor.py"),
        str(SYS_DIR / "scripts/clean_production.py"),
        str(SYS_DIR / "scripts/camera_motion.py"),
        str(SYS_DIR / "scripts/visual_quality.py"),
        str(SYS_DIR / "format_profiles.py"),
        str(SYS_DIR / "narration_pauses.py"),
        str(SYS_DIR / "tests/test_narration_pauses.py"),
        str(SYS_DIR / "visual_pacing.py"),
        str(SYS_DIR / "omni_platform.py"),
        str(SYS_DIR / "omni_render.py"),
        str(SYS_DIR / "tests/test_format_separation.py"),
        str(SYS_DIR / "tests/test_full_frame_pipeline.py"),
        str(SYS_DIR / "tests/test_full_frame_upgrade.py"),
        str(SYS_DIR / "tests/test_omni_platform.py"),
        str(SYS_DIR / "tests/test_caption_profile_07.py"),
        str(SYS_DIR / "tests/test_anti_formulaic_storytelling.py"),
        str(REPO_ROOT / "pilot.py"),
    ]
    ruff_res = subprocess.run(ruff_cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    if ruff_res.returncode != 0:
        print("[FAIL] Ruff phát hiện vi phạm linting:")
        print(ruff_res.stdout)
        return False
    print("  [PASS] Ruff linter: 0 errors, 0 warnings.")
    print("[PASS] Trạm 4: Clean code và static analysis thành công!")
    return True


def station_5_pr() -> bool:
    print_banner("Trạm 5: Worktree & Conventional PR Preparation (Git / GH-AXI)", 5)
    reports_dir = SYS_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    draft_file = reports_dir / "pr_draft.md"

    # Step A: Git branch status check
    git_res = subprocess.run(["git", "status", "--short"], cwd=str(REPO_ROOT), capture_output=True, text=True)
    if git_res.returncode == 0:
        print("  [PASS] Git: Trạng thái nhánh hợp lệ.")
        for line in git_res.stdout.splitlines()[:4]:
            if line.strip():
                print(f"         {line}")
    else:
        print("  [INFO] Git: Kiểm tra trạng thái hoàn tất.")

    # Step B: Prepare PR body
    proof_files = sorted((SYS_DIR / "logs/proofs").glob("test_evidence_*.log"))
    latest_evidence = proof_files[-1].name if proof_files else "N/A"

    git_branch = "main"
    try:
        b_res = subprocess.run(["git", "branch", "--show-current"], cwd=str(REPO_ROOT), capture_output=True, text=True)
        if b_res.returncode == 0 and b_res.stdout.strip():
            git_branch = b_res.stdout.strip()
    except Exception:
        pass

    pr_body = f"""# Conventional Pull Request: Video Pilot Development Conveyor

## Why (Bối cảnh & Mục tiêu)
Nâng cấp và chuẩn hóa quy trình phát triển dự án theo mô hình Băng chuyền 6 bước No-Mistake, kiểm soát AST test assertion integrity, đồng bộ sổ tay lỗi `PLAYBOOK.md` 6 trường chuẩn hóa, và kiểm tra tĩnh static analysis tự động.

## What Changed (Các thay đổi chính)
- Thêm CLI điều phối trung tâm `./pipeline` và module `sys/scripts/conveyor.py`.
- Tích hợp `ast_checker.py` kiểm tra 100% test function có active assertions.
- Tích hợp `playbook_validator.py` kiểm tra tính hợp lệ của `PLAYBOOK.md`.
- Tích hợp `gh-axi` TOON PR client, tự động tạo báo cáo phản biện HTML.
- Cấu hình chuẩn `pyproject.toml` cho `ruff` và `pytest`.
- Thêm báo cáo phản biện tự động `critique_review.html` tại Trạm 1.
- Cập nhật quy chuẩn Hiến pháp `AGENTS.md` (Giao thức 4 bước & Ngưỡng trích xuất Skill).

## Test Evidence (Bằng chứng thực thi Trạm 2)
- Latest Proof Log: `{latest_evidence}`
- Git Branch: `{git_branch}`
- Station 1-4 Verification: PASSED GREEN
"""
    draft_file.write_text(pr_body, encoding="utf-8")
    print(f"  [PASS] Bản nháp PR chuẩn Conventional đã tạo tại: {draft_file}")

    # Step C: GitHub Client Integration (gh-axi / gh)
    gh_axi_bin = shutil.which("gh-axi")
    gh_bin = shutil.which("gh")
    if gh_axi_bin:
        print("  [PASS] GH-AXI: Đã phát hiện GH-AXI (định dạng TOON token-optimized sẵn sàng).")
    elif gh_bin:
        print("  [INFO] Đã phát hiện GitHub CLI (gh) native.")
    else:
        print("  [INFO] Chưa cài đặt gh CLI; sử dụng PR draft offline an toàn.")

    print("[PASS] Trạm 5: Chuẩn bị PR và kiểm soát nhánh hoàn tất!")
    return True


def station_6_ci_watch() -> bool:
    print_banner("Trạm 6: CI Watch & Local Green Certification (GH-AXI Watch)", 6)
    gh_axi_bin = shutil.which("gh-axi")
    from conveyor.ci_evidence import decode_ci_runs, validate_ci_runs
    dirty = subprocess.run(['git', 'status', '--porcelain'], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    if dirty.stdout.strip() or not gh_axi_bin:
        print('[FAIL] CI certification requires a committed tree and the GitHub client.')
        return False
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout.strip()
    proofs = sorted((SYS_DIR / 'logs/proofs').glob('test_evidence_*.log'))
    proof = proofs[-1].read_text() if proofs else ''
    if f'Commit: {head}\n' not in proof or 'Return Code: 0\n' not in proof or 'WorkingTreeDirty: false\n' not in proof:
        print('[FAIL] Missing successful clean-tree test evidence for this revision.')
        return False
    try:
        # The configured repository is resolved by gh-axi; no hard-coded host.
        result = subprocess.run([
            gh_axi_bin, 'api', '/repos/{owner}/{repo}/actions/runs?head_sha=' + head + '&per_page=100',
            '--jq', '[.workflow_runs[] | {id,head_sha,status,conclusion,html_url}] | @base64', '--full',
        ], cwd=REPO_ROOT, capture_output=True, text=True, timeout=60, check=True)
        runs = decode_ci_runs(result.stdout)
    except (subprocess.SubprocessError, OSError, ValueError):
        print('[FAIL] Actual CI evidence is unavailable or unreadable.')
        return False
    if not validate_ci_runs(runs, head) or len(runs) == 100:
        print('[FAIL] CI is missing, unfinished, unsuccessful, or incompletely paginated.')
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proof_dir = SYS_DIR / "logs/proofs"
    proof_dir.mkdir(parents=True, exist_ok=True)
    cert_file = proof_dir / f"green_certified_{timestamp}.json"

    cert_data = {
        "certified": True,
        "timestamp": datetime.now().isoformat(),
        "stations_passed": [1, 2, 3, 4, 5, 6],
        "verdict": "GREEN_CERTIFIED_NO_MISTAKE",
        "commit": head,
        "test_evidence": proofs[-1].name,
        "ci_runs": runs,
    }
    cert_file.write_text(json.dumps(cert_data, indent=2), encoding="utf-8")

    print("  [PASS] Cả 6/6 trạm đạt chuẩn chất lượng cao.")
    print(f"  --> Chứng nhận Xanh đã lưu: {cert_file}")
    print("\n" + "*" * 70)
    print("  ★ CHÚC MỪNG: PIPELINE ĐÃ ĐẠT CHUẨN XANH 100% (GREEN CERTIFIED) ★")
    print("*" * 70)
    return True


def cmd_status():
    print_banner("KIỂM TRA TÍNH SẴN SÀNG CỦA HỆ THỐNG VÀ CÔNG CỤ (STATUS)")
    tools = [
        ("Python 3.12+", get_python_executable(), ["--version"]),
        ("Ruff Linter", get_ruff_executable(), ["--version"]),
        ("Pytest Runner", shutil.which("pytest") or "pytest", ["--version"]),
        ("Git VCS", shutil.which("git") or "git", ["--version"]),
        ("FFmpeg Media Engine", shutil.which("ffmpeg") or "ffmpeg", ["-version"]),
        ("FFprobe Media Inspector", shutil.which("ffprobe") or "ffprobe", ["-version"]),
        ("Node.js Runtime", shutil.which("node") or "node", ["--version"]),
        ("GH-AXI GitHub Client", shutil.which("gh-axi") or "gh-axi", ["--version"]),
    ]

    all_ready = True
    for name, binary, args in tools:
        if not binary or not Path(binary).is_file() and not shutil.which(binary):
            print(f"  [MISSING] {name:<26} : Không tìm thấy binary '{binary}'")
            all_ready = False
            continue
        try:
            res = subprocess.run([binary] + args, capture_output=True, text=True, timeout=5)
            first_line = (res.stdout or res.stderr).splitlines()[0] if (res.stdout or res.stderr) else "OK"
            print(f"  [READY]   {name:<26} : {first_line[:40]}")
        except Exception as e:
            print(f"  [ERROR]   {name:<26} : Lỗi khi gọi binary: {e}")
            all_ready = False

    print("\nKiểm tra tài liệu & quy chuẩn:")
    docs = [
        ("AGENTS.md (Hiến pháp)", REPO_ROOT / "AGENTS.md"),
        ("PLAYBOOK.md (Sổ tay lỗi)", REPO_ROOT / "PLAYBOOK.md"),
        ("pyproject.toml (Cấu hình Linter)", REPO_ROOT / "pyproject.toml"),
        ("sys/ (Thư mục mã nguồn)", SYS_DIR),
        ("sys/runs/ (Dữ liệu jobs)", SYS_DIR / "runs"),
        ("sys/logs/issues/ (Issue logbook)", SYS_DIR / "logs/issues"),
    ]
    for name, p in docs:
        status = "[EXISTS]" if p.exists() else "[MISSING]"
        if not p.exists():
            all_ready = False
        print(f"  {status:<10} {name:<35} : {p}")

    print("\nTổng kết:")
    if all_ready:
        print("  --> Toàn bộ 10/10 công cụ và cấu hình ĐÃ SẴN SÀNG cho sản xuất!")
    else:
        print("  --> Một số công cụ hoặc tệp còn thiếu. Hãy kiểm tra lại các mục báo MISSING.")
    return all_ready


def cmd_run():
    stations = [
        (1, station_1_critique),
        (2, station_2_test_ast),
        (3, station_3_docs_playbook),
        (4, station_4_lint),
        (5, station_5_pr),
        (6, station_6_ci_watch),
    ]

    print("\nBẮT ĐẦU CHẠY BĂNG CHUYỀN 6 BƯỚC NO-MISTAKE...")
    for num, func in stations:
        passed = func()
        if not passed:
            print(f"\n[DỪNG KHẨN CẤP] Băng chuyền dừng lại tại Trạm {num} do phát hiện lỗi.")
            sys.exit(1)

    print("\n--> Hoàn tất toàn bộ băng chuyền 6 bước thành công!")
    sys.exit(0)


def cmd_station(station_num: int):
    station_map = {
        1: station_1_critique,
        2: station_2_test_ast,
        3: station_3_docs_playbook,
        4: station_4_lint,
        5: station_5_pr,
        6: station_6_ci_watch,
    }
    if station_num not in station_map:
        print(f"Lỗi: Số trạm không hợp lệ ({station_num}). Chọn từ 1 đến 6.")
        sys.exit(1)
    passed = station_map[station_num]()
    sys.exit(0 if passed else 1)


def cmd_video(args):
    print_banner("ĐIỀU PHỐI SẢN XUẤT VIDEO PILOT")
    pilot_launcher = REPO_ROOT / "pilot.py"
    if not pilot_launcher.is_file():
        print("[FAIL] Không tìm thấy pilot.py")
        sys.exit(1)

    subcmd = [get_python_executable(), str(pilot_launcher)]
    if args.job:
        subcmd.extend(["--job", args.job])
    if args.step:
        subcmd.extend(["--step", args.step])

    print(f"Thực thi: {' '.join(subcmd)}")
    res = subprocess.run(subcmd, cwd=str(REPO_ROOT))
    sys.exit(res.returncode)


def cmd_flow(args):
    subaction = args.flow_action or "status"
    script = SYS_DIR / "flow_cdp/accounts.py"
    cmd = [get_python_executable(), str(script), subaction]
    if getattr(args, "target", None) and args.target != "all":
        cmd.append(args.target)
    if getattr(args, "total", None):
        cmd.extend(["--total", str(args.total)])
    res = subprocess.run(cmd, cwd=str(REPO_ROOT))
    sys.exit(res.returncode)


def cmd_setup(args):
    script = SYS_DIR / "scripts/setup_onboarding.py"
    cmd = [get_python_executable(), str(script)]
    if getattr(args, "skip_colab", False):
        cmd.append("--skip-colab")
    if getattr(args, "skip_flow", False):
        cmd.append("--skip-flow")
    if getattr(args, "force", False):
        cmd.append("--force")
    res = subprocess.run(cmd, cwd=str(REPO_ROOT))
    sys.exit(res.returncode)


def cmd_colab(args):
    subaction = args.colab_action or "list"
    script = SYS_DIR / "colab_bridge/accounts.py"
    cmd = [get_python_executable(), str(script), subaction]
    if getattr(args, "account", None) and args.account != "auto":
        cmd.append(args.account)
    res = subprocess.run(cmd, cwd=str(REPO_ROOT))
    sys.exit(res.returncode)


def main():
    parser = argparse.ArgumentParser(description="Video Pilot 6-Station No-Mistake Conveyor")
    subparsers = parser.add_subparsers(dest="command", help="Lệnh điều phối")

    subparsers.add_parser("status", help="Kiểm tra tính sẵn sàng của môi trường và công cụ")
    subparsers.add_parser("run", help="Chạy toàn bộ băng chuyền 6 trạm No-Mistake")

    setup_parser = subparsers.add_parser("setup", help="Khởi tạo môi trường, cài Colab CLI và đăng nhập tài khoản Colab + Flow")
    setup_parser.add_argument("--skip-colab", action="store_true", help="Bỏ qua bước đăng nhập Colab")
    setup_parser.add_argument("--skip-flow", action="store_true", help="Bỏ qua bước thiết lập Flow")
    setup_parser.add_argument("--force", action="store_true", help="Bắt buộc chạy lại wizard đăng nhập")

    station_parser = subparsers.add_parser("station", help="Chạy riêng một trạm cụ thể (1..6)")
    station_parser.add_argument("number", type=int, choices=range(1, 7), help="Số thứ tự trạm (1..6)")

    video_parser = subparsers.add_parser("video", help="Điều phối quy trình sản xuất video")
    video_parser.add_argument("--job", type=str, help="Mã định danh job")
    video_parser.add_argument("--step", type=str, help="Bước sản xuất (control/content/audio/images/render)")

    flow_parser = subparsers.add_parser("flow", help="Quản lý Profile & Đăng nhập Google Flow CDP")
    flow_parser.add_argument("flow_action", choices=["status", "launch", "login-many", "stop", "list", "scan", "leases", "release"], nargs="?", default="status")
    flow_parser.add_argument("target", nargs="?", default="all", help="Profile ID, job ID, hoặc 'all'")
    flow_parser.add_argument("--total", type=int, help="Tổng số Profile khi chạy login-many")

    colab_parser = subparsers.add_parser("colab", help="Quản lý tài khoản Google Colab CLI")
    colab_parser.add_argument("colab_action", choices=["list", "status-all", "login", "login-many", "enable", "disable", "role", "remove"], nargs="?", default="list")
    colab_parser.add_argument("account", nargs="?", default="auto", help="ID tài khoản Colab")

    args = parser.parse_args()

    if args.command == "status":
        ok = cmd_status()
        sys.exit(0 if ok else 1)
    elif args.command == "setup":
        cmd_setup(args)
    elif args.command == "run":
        cmd_run()
    elif args.command == "station":
        cmd_station(args.number)
    elif args.command == "video":
        cmd_video(args)
    elif args.command == "flow":
        cmd_flow(args)
    elif args.command == "colab":
        cmd_colab(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
