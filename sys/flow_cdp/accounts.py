"""Flow CDP Profile & Account Management.

Provides interactive 'login-many', profile synchronization, isolated browser instance
launching, and live status diagnostics for Google Flow across multiple Chrome profiles.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

STORE = Path.home() / ".config/video-pilot/flow"
DEFAULT_SOURCE_DIR = Path.home() / ".config/google-chrome"
STANDARD_PORTS = [9225, 9223, 9224, 9222, 9226, 9227, 9228, 9229]


def detect_chrome_binary() -> str:
    """Find available Chrome or Chromium binary on the host system."""
    candidates = [
        "/opt/google/chrome/google-chrome",
        "/opt/google/chrome/chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    found = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
    if found:
        return found
    return "/opt/google/chrome/google-chrome"


def scan_system_chrome_profiles(source_dir: Path | None = None) -> list[dict[str, Any]]:
    """Scan existing Google Chrome profile directories and account names from Local State."""
    base = source_dir or DEFAULT_SOURCE_DIR
    local_state = base / "Local State"
    if not local_state.is_file():
        return []
    try:
        data = json.loads(local_state.read_text(encoding="utf-8"))
        info_cache = data.get("profile", {}).get("info_cache", {})
        profiles = []
        for prof_dir, info in sorted(info_cache.items()):
            profiles.append({
                "directory": prof_dir,
                "name": info.get("name", prof_dir),
                "gaia_name": info.get("gaia_name", ""),
                "email": info.get("user_name", ""),
            })
        return profiles
    except Exception:
        return []


def default_profiles() -> list[dict[str, Any]]:
    return [
        {
            "id": "profile_1",
            "port": 9225,
            "directory": "Profile 1",
            "user_data_dir": str(Path.home() / ".config/google-chrome-cdp-p1"),
            "enabled": True,
        },
        {
            "id": "profile_2",
            "port": 9223,
            "directory": "Profile 2",
            "user_data_dir": str(Path.home() / ".config/google-chrome-cdp-p2"),
            "enabled": True,
        },
        {
            "id": "profile_3",
            "port": 9224,
            "directory": "Profile 3",
            "user_data_dir": str(Path.home() / ".config/google-chrome-cdp-p3"),
            "enabled": True,
        },
    ]


def registry() -> dict[str, Any]:
    """Load configured Flow profiles from store, or initialize default registry."""
    path = STORE / "profiles.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "preferred": "profile_1",
        "profiles": default_profiles(),
    }


def save_registry(data: dict[str, Any]) -> None:
    """Save registry and synchronize sys/config.json and sys/flow_cdp/browser-profiles.json."""
    STORE.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = STORE / "profiles.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(path)

    # Sync to sys/flow_cdp/browser-profiles.json and config.json if accessible
    repo_root = Path(__file__).resolve().parents[2]
    browser_profiles_file = repo_root / "sys/flow_cdp/browser-profiles.json"
    if browser_profiles_file.is_file():
        try:
            bp = json.loads(browser_profiles_file.read_text(encoding="utf-8"))
            bp["executable_path"] = detect_chrome_binary()
            bp["priority"] = [p["directory"] for p in data.get("profiles", []) if p.get("enabled", True)]
            browser_profiles_file.write_text(json.dumps(bp, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass


def is_port_listening(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    """Check if TCP port is accepting connections."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def probe_profile(port: int, host: str = "127.0.0.1", timeout: float = 1.0) -> dict[str, Any]:
    """Probe Chrome CDP HTTP endpoints for version and active targets."""
    if not is_port_listening(port, host=host, timeout=timeout):
        return {"listening": False, "version": None, "flow_open": False}

    version_info = None
    flow_open = False
    try:
        req = urllib.request.Request(f"http://{host}:{port}/json/version", headers={"User-Agent": "video-pilot"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            version_info = json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass

    try:
        req = urllib.request.Request(f"http://{host}:{port}/json/list", headers={"User-Agent": "video-pilot"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            targets = json.loads(resp.read().decode("utf-8"))
            if isinstance(targets, list):
                flow_open = any("flow.google" in t.get("url", "") for t in targets)
    except Exception:
        pass

    return {
        "listening": True,
        "browser": version_info.get("Browser") if version_info else None,
        "flow_open": flow_open,
    }


def setup_profile_dir(
    target_user_data_dir: str | Path,
    source_profile_name: str = "Profile 1",
    source_root: str | Path | None = None,
) -> None:
    """Synchronize an isolated CDP user data directory from an existing Chrome profile."""
    target_dir = Path(target_user_data_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    orig_dir = Path(source_root or DEFAULT_SOURCE_DIR).expanduser().resolve()

    # Sync Local State
    if (orig_dir / "Local State").is_file():
        shutil.copyfile(orig_dir / "Local State", target_dir / "Local State")

    # Sync Profile directory preferences/cookies if source exists
    src_prof = orig_dir / source_profile_name
    dest_prof = target_dir / source_profile_name
    if src_prof.is_dir():
        dest_prof.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Run rsync excluding caches to keep profile fast and lightweight
        subprocess.run(
            [
                "rsync", "-a", "--update",
                "--exclude=Cache*",
                "--exclude=Code Cache*",
                "--exclude=GPUCache*",
                "--exclude=DawnWebGPUCache*",
                "--exclude=DawnGraphiteCache*",
                "--exclude=*.tmp",
                f"{src_prof}/", f"{dest_prof}/",
            ],
            capture_output=True,
            check=False,
        )

    # Clean Singleton locks so isolated Chrome can launch cleanly without conflict
    for lock in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        for p in (target_dir / lock, dest_prof / lock):
            if p.exists() or p.is_symlink():
                try:
                    p.unlink()
                except OSError:
                    pass


def launch_profile(
    profile_entry: dict[str, Any],
    url: str = "https://flow.google.com/",
    chrome_bin: str | None = None,
) -> bool:
    """Launch a Chrome profile in background with remote debugging enabled."""
    port = int(profile_entry["port"])
    if is_port_listening(port):
        return True

    target_dir = Path(profile_entry["user_data_dir"]).expanduser().resolve()
    prof_name = profile_entry.get("directory", "Profile 1")
    binary = chrome_bin or detect_chrome_binary()

    # Clean stale locks
    for lock in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        for p in (target_dir / lock, target_dir / prof_name / lock):
            if p.exists() or p.is_symlink():
                try:
                    p.unlink()
                except OSError:
                    pass

    env = dict(os.environ, DISPLAY=os.environ.get("DISPLAY", ":0"))
    cmd = [
        binary,
        f"--user-data-dir={target_dir}",
        f"--profile-directory={prof_name}",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
        url,
    ]

    subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    # Poll port readiness
    for _ in range(25):
        time.sleep(0.2)
        if is_port_listening(port):
            try:
                from .lifecycle import register_spawned_port
                register_spawned_port(port)
            except Exception:
                pass
            return True
    return False


def stop_profile(profile_entry: dict[str, Any]) -> None:
    """Terminate Chrome process for a specific profile entry."""
    port = int(profile_entry["port"])
    target_dir = Path(profile_entry["user_data_dir"]).expanduser().resolve()
    prof_name = profile_entry.get("directory", "Profile 1")

    subprocess.run(["pkill", "-f", f"remote-debugging-port={port}"], capture_output=True, check=False)
    subprocess.run(["pkill", "-f", f"user-data-dir={target_dir}"], capture_output=True, check=False)

    for lock in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        for p in (target_dir / lock, target_dir / prof_name / lock):
            if p.exists() or p.is_symlink():
                try:
                    p.unlink()
                except OSError:
                    pass


def stop_profile_by_port(port: int) -> bool:
    """Terminate Chrome process for a specific remote debugging port and clean its locks."""
    d = registry()
    entry = next((p for p in d.get("profiles", []) if int(p["port"]) == port), None)
    if entry:
        stop_profile(entry)
        return True
    subprocess.run(["pkill", "-f", f"remote-debugging-port={port}"], capture_output=True, check=False)
    return True


def stop_all(profiles: list[dict[str, Any]] | None = None) -> list[str]:
    """Stop all configured or passed profiles."""
    d = registry()
    entries = profiles or d.get("profiles", [])
    stopped = []
    for p in entries:
        stop_profile(p)
        stopped.append(p["id"])
    return stopped


def launch_all(
    profiles: list[dict[str, Any]] | None = None,
    url: str = "https://flow.google.com/",
) -> dict[str, bool]:
    """Launch all configured or passed profiles and return port readiness."""
    d = registry()
    entries = profiles or [p for p in d.get("profiles", []) if p.get("enabled", True)]
    results = {}
    for p in entries:
        results[p["id"]] = launch_profile(p, url=url)
    return results


def status_all() -> dict[str, Any]:
    """Diagnostic overview of all configured Flow profiles."""
    d = registry()
    profiles = []
    for p in d.get("profiles", []):
        port = int(p["port"])
        probe = probe_profile(port)
        profiles.append({
            "id": p["id"],
            "port": port,
            "directory": p.get("directory"),
            "user_data_dir": p.get("user_data_dir"),
            "enabled": p.get("enabled", True),
            "source_profile": p.get("source_profile"),
            "source_email": p.get("source_email"),
            "listening": probe["listening"],
            "browser": probe.get("browser"),
            "flow_open": probe.get("flow_open"),
        })
    return {
        "store": str(STORE),
        "total_profiles": len(profiles),
        "listening_count": sum(1 for p in profiles if p["listening"]),
        "profiles": profiles,
    }


def resolve_profile_selection(raw: str, system_profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Parse comma/space-separated selection of profile indices, directories, or emails."""
    tokens = [t.strip() for t in raw.replace(",", " ").split() if t.strip()]
    selected = []
    seen = set()
    for tok in tokens:
        match = None
        if tok.isdigit():
            val = int(tok)
            if 1 <= val <= len(system_profiles):
                match = system_profiles[val - 1]
            else:
                match = next((sp for sp in system_profiles if sp["directory"].lower() == f"profile {val}".lower()), None)
        if not match:
            match = next((sp for sp in system_profiles if sp["directory"].lower() == tok.lower()), None)
        if not match:
            match = next((sp for sp in system_profiles if tok.lower() in sp.get("email", "").lower()), None)
        if not match:
            match = next((sp for sp in system_profiles if tok.lower() in sp.get("name", "").lower()), None)

        if match and match["directory"] not in seen:
            seen.add(match["directory"])
            selected.append(match)
    return selected


def login_many(
    total: int | None = None,
    select_profiles: str | None = None,
    sequential_close: bool = True,
) -> None:
    """Interactive multi-profile onboarding wizard with sequential launch & auto-close to avoid lag."""
    print("\n" + "=" * 70)
    print("  GOOGLE FLOW CDP — THIẾT LẬP VÀ ĐĂNG NHẬP MULTI-PROFILE (LOGIN-MANY)")
    print("=" * 70)
    print("Hệ thống tuân thủ nguyên tắc TIẾT KIỆM TÀI NGUYÊN (Không mở cùng lúc tất cả):")
    print("  1. Quét danh sách Profile Chrome ĐÃ ĐĂNG NHẬP SẴN trên máy tính.")
    print("  2. Sao chép phiên đăng nhập & cookie sang thư mục độc lập.")
    print("  3. Phân bổ cổng Remote Debugging (9225, 9223, 9224...).")
    print("  4. Mở TUẦN TỰ từng Profile một để kiểm tra, sau đó ĐÓNG NGAY trước khi mở Profile kế tiếp.")
    print("=" * 70)

    system_profiles = scan_system_chrome_profiles()
    if system_profiles:
        print(f"\nTìm thấy {len(system_profiles)} Profile Chrome trên hệ thống:")
        for idx, sp in enumerate(system_profiles, 1):
            email_info = f"({sp['email']})" if sp.get("email") else "(Chưa liên kết email)"
            print(f"  [{idx:2d}] {sp['directory']:<12}: {sp['name']:<20} {email_info}")
    else:
        print("\nChưa tìm thấy Local State Chrome mặc định. Sẽ tạo Profile mới tách biệt hoàn toàn.")

    selected_list: list[dict[str, Any]] = []

    if select_profiles:
        selected_list = resolve_profile_selection(select_profiles, system_profiles)
        print(f"\nĐã nhận cấu hình từ tham số: {len(selected_list)} profile được chọn.")
    elif system_profiles:
        prompt_txt = (
            "\nBẠN CÓ THỂ CHỌN NHANH CÁC PROFILE ĐÃ ĐĂNG NHẬP SẴN:\n"
            "  * Nhập danh sách số thứ tự hoặc số Profile (ví dụ: '1, 2, 5' hoặc '10, 102, 14')\n"
            "  * Hoặc nhập số lượng (ví dụ: '3') nếu muốn hệ thống tự chọn 3 profile đầu tiên\n"
            "  * Nhấn Enter để tự động chọn 3 profile đầu tiên:\n"
            "Lựa chọn của bạn: "
        )
        user_input = input(prompt_txt).strip()
        if user_input:
            if "," in user_input or " " in user_input:
                selected_list = resolve_profile_selection(user_input, system_profiles)
            elif user_input.isdigit():
                val = int(user_input)
                if val > len(system_profiles):
                    # Assume profile number, e.g. "10" -> Profile 10
                    selected_list = resolve_profile_selection(user_input, system_profiles)
                elif val <= 10 and not any(sp["directory"].lower() == f"profile {val}".lower() for sp in system_profiles if val > len(system_profiles)):
                    # User input quantity e.g. "3" -> first 3
                    selected_list = system_profiles[:val]
                else:
                    selected_list = resolve_profile_selection(user_input, system_profiles)
            else:
                selected_list = resolve_profile_selection(user_input, system_profiles)

    if not selected_list:
        # Default to first 3 or total requested
        count = total or 3
        selected_list = system_profiles[:count] if system_profiles else []

    num_target = len(selected_list) if selected_list else (total or 3)
    print(f"\n--> Bắt đầu thiết lập {num_target} Profile theo quy trình tuần tự nhẹ máy...")

    current_data = registry()
    profiles_list = []
    used_ports = set()

    for i in range(num_target):
        prof_id = f"profile_{i + 1}"
        port = STANDARD_PORTS[i] if i < len(STANDARD_PORTS) else 9225 + i
        while port in used_ports:
            port += 1
        used_ports.add(port)

        target_user_data = Path.home() / f".config/google-chrome-cdp-p{i + 1}"
        if i < len(selected_list):
            sel = selected_list[i]
            source_dir = sel["directory"]
            source_email = sel.get("email")
        else:
            source_dir = f"Profile {i + 1}"
            source_email = None

        print(f"\n--- [Profile {i + 1}/{num_target}]: {prof_id} (Cổng CDP: {port}) ---")
        print(f"  * Profile nguồn: '{source_dir}' {f'({source_email})' if source_email else ''}")
        print(f"  * Thư mục cô lập: {target_user_data}")

        entry = {
            "id": prof_id,
            "port": port,
            "directory": source_dir,
            "user_data_dir": str(target_user_data),
            "source_profile": source_dir,
            "source_email": source_email,
            "enabled": True,
        }

        print("  --> Đang đồng bộ cookie & phiên đăng nhập...")
        setup_profile_dir(target_user_data, source_profile_name=source_dir)

        print(f"  --> Đang mở Chrome {prof_id} (Port {port})...")
        ok = launch_profile(entry, url="https://flow.google.com/")
        if ok:
            print(f"  [OK] Cổng {port} ĐÃ SẴN SÀNG! Đã kết nối Flow.google.com.")
        else:
            print(f"  [CẢNH BÁO] Chưa kết nối được cổng {port}. Vẫn lưu cấu hình để thử lại.")

        if sys.stdin.isatty():
            try:
                input("  👉 Kiểm tra/đăng nhập xong, nhấn [Enter] để ĐÓNG cửa sổ này và tiếp tục Profile kế: ")
            except EOFError:
                pass
        else:
            time.sleep(1.0)

        if sequential_close:
            print(f"  --> Đang đóng {prof_id} để giải phóng RAM cho hệ thống...")
            stop_profile(entry)

        profiles_list.append(entry)

    # Đảm bảo toàn bộ Chrome được đóng sau khi hoàn tất setup
    if sequential_close:
        stop_all(profiles_list)

    current_data["profiles"] = profiles_list
    save_registry(current_data)

    print("\n" + "=" * 70)
    print("  HOÀN TẤT THIẾT LẬP MULTI-PROFILE CHO GOOGLE FLOW!")
    print("=" * 70)
    print(f"Đã lưu {len(profiles_list)} Profile vào {STORE / 'profiles.json'}.")
    print("[TIẾT KIỆM TÀI NGUYÊN] Tất cả cửa sổ Chrome đã được ĐÓNG HOÀN TOÀN để tránh giật lag.")
    print("Khi chạy Job, hệ thống sẽ tự động mở on-demand ĐÚNG 2 Profile được cấp phát và tự đóng lại khi xong.")
    print("\nTrạng thái hiện tại:")
    st = status_all()
    for p in st["profiles"]:
        state_str = "READY (LISTENING)" if p["listening"] else "NOT READY"
        flow_str = " (Flow page open)" if p["flow_open"] else ""
        print(f"  - {p['id']:<12} Port {p['port']}: {state_str}{flow_str} [{p.get('source_email') or p['directory']}]")
    print("\nLần sau muốn khởi chạy lại toàn bộ, bạn chỉ cần chạy:")
    print("  python3 -m flow_cdp.accounts launch")
    print("hoặc:")
    print("  ./pipeline flow launch\n")


def main() -> None:
    actions = ["list", "status", "launch", "stop", "login-many", "scan", "sync", "leases", "release"]
    parser = argparse.ArgumentParser(description="Google Flow CDP Account & Profile Manager")
    parser.add_argument("action", choices=actions, nargs="?", default="status")
    parser.add_argument("target", nargs="?", default="all", help="Profile ID, job ID, or 'all'")
    parser.add_argument("--total", type=int, help="Total number of profiles to configure in login-many")
    parser.add_argument("--select", type=str, help="Danh sách profile muốn chọn sẵn (ví dụ: '10,102,14' hoặc '1,2,3')")
    parser.add_argument("--url", default="https://flow.google.com/", help="URL to open on launch")
    args = parser.parse_args()

    if args.action == "leases":
        try:
            from .lease_manager import FlowJobLeaseManager
        except ImportError:
            from lease_manager import FlowJobLeaseManager
        print(json.dumps(FlowJobLeaseManager().list_active_leases(), indent=2, ensure_ascii=False))
        return

    if args.action == "release":
        try:
            from .lease_manager import FlowJobLeaseManager
        except ImportError:
            from lease_manager import FlowJobLeaseManager
        job_id = args.target if args.target != "all" else None
        if not job_id:
            print("Cần chỉ định job_id để giải phóng profile (ví dụ: ./pipeline flow release job-001)", file=sys.stderr)
            sys.exit(1)
        rel = FlowJobLeaseManager().release_all_for_job(job_id)
        print(f"Đã giải phóng các profile cho job '{job_id}': {rel}")
        return

    if args.action == "scan":
        print(json.dumps(scan_system_chrome_profiles(), indent=2, ensure_ascii=False))
        return

    if args.action == "list":
        print(json.dumps(registry(), indent=2, ensure_ascii=False))
        return

    if args.action == "status":
        print(json.dumps(status_all(), indent=2, ensure_ascii=False))
        return

    if args.action == "stop":
        if args.target == "all":
            stopped = stop_all()
            print(f"Đã dừng {len(stopped)} profile: {', '.join(stopped)}")
        else:
            d = registry()
            target_entry = next((p for p in d.get("profiles", []) if p["id"] == args.target), None)
            if not target_entry:
                print(f"Không tìm thấy profile '{args.target}'", file=sys.stderr)
                sys.exit(1)
            stop_profile(target_entry)
            print(f"Đã dừng {args.target}")
        return

    if args.action == "launch":
        d = registry()
        if args.target == "all":
            results = launch_all(url=args.url)
            for pid, ok in results.items():
                print(f"Profile {pid}: {'LISTENING (READY)' if ok else 'FAILED TO LAUNCH'}")
        else:
            target_entry = next((p for p in d.get("profiles", []) if p["id"] == args.target), None)
            if not target_entry:
                print(f"Không tìm thấy profile '{args.target}'", file=sys.stderr)
                sys.exit(1)
            ok = launch_profile(target_entry, url=args.url)
            print(f"Profile {args.target}: {'LISTENING (READY)' if ok else 'FAILED TO LAUNCH'}")
        return

    if args.action == "login-many":
        login_many(total=args.total, select_profiles=args.select)
        return

    if args.action == "sync":
        d = registry()
        for p in d.get("profiles", []):
            setup_profile_dir(p["user_data_dir"], source_profile_name=p.get("directory", "Profile 1"))
            print(f"Đã đồng bộ {p['id']} -> {p['user_data_dir']}")
        return


if __name__ == "__main__":
    main()
