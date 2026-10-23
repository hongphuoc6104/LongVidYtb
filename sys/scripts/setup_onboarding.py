"""Video Pilot — Unified System Setup & Account Onboarding Wizard.

Automates the entire initial machine bootstrap:
1. Bootstraps environment (sys/.venv, sys/runs, video directories, pinned requirements).
2. Checks and auto-installs Google Colab CLI (uv tool install google-colab-cli==0.7.4) if missing.
3. Guides interactive Colab account login (colab_bridge.accounts login-many).
4. Guides interactive Google Flow Chrome CDP multi-profile setup (flow_cdp.accounts login-many).
5. Runs final system readiness verification.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
sys.path.insert(0, str(SYS_DIR))
sys.path.insert(0, str(REPO_ROOT))


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def ensure_colab_cli() -> str:
    """Check if colab binary exists; if not, automatically install it via uv tool or pip."""
    binary = shutil.which("colab") or str(Path.home() / ".local/bin/colab")
    if Path(binary).is_file() and os.access(binary, os.X_OK):
        print(f"[READY] Google Colab CLI đã có sẵn tại: {binary}")
        return binary

    print("[CÀI ĐẶT] Không tìm thấy Google Colab CLI trên hệ thống.")
    print("  --> Đang tự động cài đặt 'google-colab-cli==0.7.4'...")
    uv = shutil.which("uv") or str(Path.home() / ".local/bin/uv")
    installed = False

    if uv and Path(uv).is_file():
        try:
            res = subprocess.run([uv, "tool", "install", "google-colab-cli==0.7.4"], capture_output=True, text=True)
            if res.returncode == 0:
                installed = True
            else:
                # Retry with force/update
                res2 = subprocess.run([uv, "tool", "install", "--force", "google-colab-cli==0.7.4"], capture_output=True, text=True)
                if res2.returncode == 0:
                    installed = True
        except Exception:
            pass

    if not installed:
        # Fallback to pip install
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "google-colab-cli==0.7.4"], check=True)
            installed = True
        except Exception as e:
            print(f"[LỖI] Cài đặt pip thất bại: {e}")

    binary = shutil.which("colab") or str(Path.home() / ".local/bin/colab")
    if Path(binary).is_file() and os.access(binary, os.X_OK):
        print(f"[PASS] Đã cài đặt Colab CLI thành công tại: {binary}")
        return binary

    raise RuntimeError(
        "Không thể tự động cài đặt colab-cli. Vui lòng cài đặt thủ công:\n"
        "  uv tool install google-colab-cli==0.7.4\n"
        "hoặc: pip install google-colab-cli==0.7.4"
    )


def step_bootstrap_env() -> None:
    print_header("BƯỚC 1: KHỞI TẠO MÔI TRƯỜNG & THƯ MỤC HỆ THỐNG")

    # Invariant directories
    (SYS_DIR / "runs").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "video").mkdir(parents=True, exist_ok=True)
    (SYS_DIR / "logs/issues").mkdir(parents=True, exist_ok=True)
    (SYS_DIR / "logs/proofs").mkdir(parents=True, exist_ok=True)
    print("  [OK] Đã xác nhận cấu trúc thư mục quy chuẩn: sys/runs, video, sys/logs.")

    # Management environment
    bootstrap_py = SYS_DIR / "scripts/bootstrap.py"
    if bootstrap_py.is_file():
        state_file = SYS_DIR / ".state/bootstrap.json"
        if not state_file.is_file():
            print("  --> Đang thiết lập môi trường quản lý (.venv-management)...")
            subprocess.run([sys.executable, str(bootstrap_py), "apply", "--install"], cwd=str(SYS_DIR), check=True)
        else:
            print("  [OK] Môi trường quản lý (.venv-management) đã sẵn sàng.")

    # Main venv dependencies
    venv_py = SYS_DIR / ".venv/bin/python"
    if venv_py.is_file():
        print(f"  [OK] Môi trường ảo Python chính ({venv_py}) đã sẵn sàng.")
    else:
        print("  --> Đang tạo môi trường ảo Python 3.12 (sys/.venv)...")
        uv = shutil.which("uv") or str(Path.home() / ".local/bin/uv")
        if uv and Path(uv).is_file():
            subprocess.run([uv, "venv", "--python", "/usr/bin/python3.12", str(SYS_DIR / ".venv")], check=True)
            subprocess.run([uv, "pip", "install", "--python", str(venv_py), "-r", str(SYS_DIR / "requirements-dev.txt"), "pytest", "ruff"], check=True)
        else:
            subprocess.run([sys.executable, "-m", "venv", str(SYS_DIR / ".venv")], check=True)
            subprocess.run([str(venv_py), "-m", "pip", "install", "-r", str(SYS_DIR / "requirements-dev.txt"), "pytest", "ruff"], check=True)
        print("  [PASS] Cài đặt phụ thuộc Python hoàn tất.")


def step_colab_onboarding(force_login: bool = False) -> None:
    print_header("BƯỚC 2: CÔNG CỤ & ĐĂNG NHẬP TÀI KHOẢN GOOGLE COLAB")
    ensure_colab_cli()

    from colab_bridge.accounts import folder, registry

    reg = registry()
    existing_accounts = reg.get("accounts", [])
    authenticated = [a["id"] for a in existing_accounts if (folder(a["id"]) / "token.json").is_file()]

    print(f"\nHiện có {len(authenticated)}/{len(existing_accounts)} tài khoản Colab đã xác thực.")
    if authenticated:
        for acc in existing_accounts:
            is_auth = (folder(acc["id"]) / "token.json").is_file()
            status = "ĐÃ ĐĂNG NHẬP" if is_auth else "CHƯA XÁC THỰC"
            print(f"  - {acc['id']:<14}: {status} (Role: {acc.get('role', 'any')})")

    need_login = force_login or len(authenticated) == 0
    if not need_login:
        ans = input("\nBạn có muốn đăng nhập thêm tài khoản Colab mới không? [y/N]: ").strip().lower()
        if ans in ("y", "yes", "c", "có"):
            need_login = True

    if need_login:
        print("\nKhởi động Wizard đăng nhập Colab CLI (colab_bridge.accounts login-many)...")
        from colab_bridge import accounts
        accounts.main_action = "login-many"
        # Run via subprocess to maintain clean interactive TTY
        binary_py = str(SYS_DIR / ".venv/bin/python") if (SYS_DIR / ".venv/bin/python").is_file() else sys.executable
        subprocess.run([binary_py, "-m", "colab_bridge.accounts", "login-many"], cwd=str(SYS_DIR))
    else:
        print("  [OK] Giữ nguyên danh sách tài khoản Colab hiện tại.")


def step_flow_onboarding(force_setup: bool = False) -> None:
    print_header("BƯỚC 3: CÔNG CỤ & THIẾT LẬP GOOGLE FLOW CDP (MULTI-PROFILE)")
    from flow_cdp.accounts import detect_chrome_binary, login_many, registry

    chrome_bin = detect_chrome_binary()
    print(f"  [OK] Đã phát hiện trình duyệt Chrome: {chrome_bin}")

    reg = registry()
    configured_profiles = reg.get("profiles", [])
    print(f"Hiện có {len(configured_profiles)} Profile Flow CDP đã được cấu hình trong kho lưu trữ.")

    need_setup = force_setup or len(configured_profiles) == 0
    if not need_setup:
        ans = input("\nBạn có muốn thiết lập lại / đăng nhập Profile Flow CDP mới không? [y/N]: ").strip().lower()
        if ans in ("y", "yes", "c", "có"):
            need_setup = True

    if need_setup:
        login_many()
    else:
        print("  [OK] Giữ nguyên cấu hình Profile Flow hiện tại.")
        ans_check = input("\nBạn có muốn mở kiểm tra tuần tự từng Profile (mở từng cái rồi tắt để tránh lag)? [y/N]: ").strip().lower()
        if ans_check in ("y", "yes", "c", "có"):
            from flow_cdp.accounts import launch_profile, stop_profile
            for p in configured_profiles:
                print(f"\n--> Đang mở {p['id']} (Cổng {p['port']})...")
                ok = launch_profile(p, headless=False)
                if ok:
                    print(f"  [OK] Cổng {p['port']} sẵn sàng.")
                if sys.stdin.isatty():
                    try:
                        input("  👉 Nhấn [Enter] để ĐÓNG cửa sổ này và chuyển sang Profile kế: ")
                    except EOFError:
                        pass
                stop_profile(p)
                print(f"  --> Đã đóng {p['id']}.")
            print("  [PASS] Đã hoàn tất kiểm tra tuần tự. Toàn bộ cửa sổ đã được tắt an toàn.")


def step_final_report() -> None:
    print_header("TỔNG KẾT TRẠNG THÁI HỆ THỐNG SAU KHI THIẾT LẬP")
    from colab_bridge.accounts import folder
    from colab_bridge.accounts import registry as colab_reg
    from flow_cdp.accounts import status_all as flow_status

    c_reg = colab_reg()
    auth_colab = [a["id"] for a in c_reg.get("accounts", []) if (folder(a["id"]) / "token.json").is_file()]
    print(f"  [1] Tài khoản Colab T4 : {len(auth_colab)} tài khoản sẵn sàng ({', '.join(auth_colab) or 'Chưa có'})")

    f_stat = flow_status()
    listening_flow = sum(1 for p in f_stat["profiles"] if p["listening"])
    print(f"  [2] Flow CDP Profiles  : {len(f_stat['profiles'])} cấu hình, {listening_flow} đang lắng nghe")
    for p in f_stat["profiles"]:
        state = "SẴN SÀNG" if p["listening"] else "CHƯA BẬT (sẵn sàng khi chạy)"
        print(f"      - {p['id']:<12} Port {p['port']}: {state} [{p.get('source_email') or p.get('directory')}]")

    print("\nKiểm tra toàn diện 10/10 công cụ:")
    subprocess.run(["./pipeline", "status"], cwd=str(REPO_ROOT))
    print("\n" + "=" * 70)
    print("  CHÚC MỪNG: BẠN ĐÃ THIẾT LẬP TOÀN DIỆN HỆ THỐNG THÀNH CÔNG!")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Video Pilot Unified Setup Wizard")
    parser.add_argument("--skip-colab", action="store_true", help="Bỏ qua bước đăng nhập Colab")
    parser.add_argument("--skip-flow", action="store_true", help="Bỏ qua bước thiết lập Flow CDP")
    parser.add_argument("--force", action="store_true", help="Bắt buộc chạy lại toàn bộ wizard đăng nhập")
    args = parser.parse_args()

    step_bootstrap_env()

    if not args.skip_colab:
        step_colab_onboarding(force_login=args.force)

    if not args.skip_flow:
        step_flow_onboarding(force_setup=args.force)

    step_final_report()


if __name__ == "__main__":
    main()
