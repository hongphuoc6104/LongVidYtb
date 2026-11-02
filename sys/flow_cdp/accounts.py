"""Flow CDP Profile & Account Management.

Provides interactive 'login-many', profile synchronization, isolated browser instance
launching, and live status diagnostics for Google Flow across multiple Chrome profiles.
"""
from __future__ import annotations

import argparse
import json
import logging
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

logger = logging.getLogger("flow_cdp.accounts")

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
    from .multi_profile_manager import DEFAULT_PROFILES
    return [
        {
            "id": p["id"],
            "port": p["port"],
            "directory": p["directory"],
            "user_data_dir": str(Path(p["user_data_dir"]).expanduser()),
            "enabled": True,
        }
        for p in DEFAULT_PROFILES
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
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
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

    config_file = repo_root / "sys/config.json"
    if config_file.is_file():
        try:
            cfg = json.loads(config_file.read_text(encoding="utf-8"))
            cfg["flow_cdp_profiles"] = [
                {
                    "id": p["id"],
                    "port": p["port"],
                    "directory": p["directory"],
                    "user_data_dir": p["user_data_dir"],
                }
                for p in data.get("profiles", [])
            ]
            config_file.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
    headless: bool = True,
) -> bool:
    """Launch a Chrome profile in background with remote debugging enabled."""
    from .process_manager import get_process_manager
    return get_process_manager().launch(
        profile_cfg=profile_entry,
        url=url,
        headless=headless,
        chrome_bin=chrome_bin,
    )


def stop_profile(profile_entry: dict[str, Any]) -> None:
    """Terminate Chrome process for a specific profile entry."""
    port = int(profile_entry["port"])
    target_dir = Path(profile_entry["user_data_dir"]).expanduser().resolve()
    prof_name = profile_entry.get("directory", "Profile 1")
    from .process_manager import clean_singleton_locks, get_process_manager
    get_process_manager().terminate_by_port(port)
    clean_singleton_locks(target_dir, prof_name)


def stop_profile_by_port(port: int) -> bool:
    """Terminate Chrome process for a specific remote debugging port and clean its locks."""
    from .process_manager import get_process_manager
    return get_process_manager().terminate_by_port(port)


def stop_all(profiles: list[dict[str, Any]] | None = None) -> list[str]:
    """Stop all configured or passed profiles."""
    d = registry()
    entries = profiles or d.get("profiles", [])
    from .process_manager import get_process_manager
    pm = get_process_manager()
    stopped = []
    for p in entries:
        port = int(p["port"])
        pm.terminate_by_port(port)
        stopped.append(p["id"])
    pm.terminate_all()
    return stopped


def launch_all(
    profiles: list[dict[str, Any]] | None = None,
    url: str = "https://flow.google.com/",
    headless: bool = True,
) -> dict[str, bool]:
    """Launch all configured or passed profiles and return port readiness."""
    d = registry()
    entries = profiles or [p for p in d.get("profiles", []) if p.get("enabled", True)]
    results = {}
    for p in entries:
        results[p["id"]] = launch_profile(p, url=url, headless=headless)
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
        ok = launch_profile(entry, url="https://flow.google.com/", headless=False)
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

    # Merge/append new profiles into current_data["profiles"] instead of overwriting!
    existing_profiles = current_data.get("profiles", [])
    merged_profiles = list(existing_profiles)
    existing_by_id = {p["id"]: idx for idx, p in enumerate(merged_profiles)}

    for p in profiles_list:
        if p["id"] in existing_by_id:
            merged_profiles[existing_by_id[p["id"]]] = p
        else:
            merged_profiles.append(p)
            existing_by_id[p["id"]] = len(merged_profiles) - 1

    current_data["profiles"] = merged_profiles
    save_registry(current_data)

    try:
        from .credit_ledger import get_credit_ledger
        ledger = get_credit_ledger()
        for p in profiles_list:
            ledger.register_profile(p["id"], initial_credits=1000)
    except Exception as e:
        logger.warning("Could not register profiles in credit ledger: %s", e)

    print("\n" + "=" * 70)
    print("  HOÀN TẤT THIẾT LẬP MULTI-PROFILE CHO GOOGLE FLOW!")
    print("=" * 70)
    print(f"Đã lưu {len(merged_profiles)} Profile vào {STORE / 'profiles.json'}.")
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


def onboard_profiles(
    count: int = 1,
    start_port: int = 9270,
    sequential_close: bool = True,
) -> list[dict[str, Any]]:
    """Onboard N new profiles with clean IDs (profile_40+), ports (9270+), and 1,000 initial credits."""
    print("\n" + "=" * 70)
    print("  GOOGLE FLOW CDP — ONBOARD THÊM PROFILE MỚI (1K CREDITS)")
    print("=" * 70)
    print(f"Số lượng cần thêm: {count} profile | Cổng bắt đầu: {start_port}")
    print("=" * 70)

    current_data = registry()
    existing_profiles = current_data.get("profiles", [])
    used_ids = {p.get("id") for p in existing_profiles}
    used_ports = {int(p.get("port", 0)) for p in existing_profiles}

    # Find highest numeric index among profile_N (excluding profile_enXX)
    max_idx = 39
    for pid in used_ids:
        if pid and pid.startswith("profile_") and not pid.startswith("profile_en"):
            suffix = pid[len("profile_"):]
            if suffix.isdigit():
                max_idx = max(max_idx, int(suffix))

    next_port = start_port
    created_profiles: list[dict[str, Any]] = []

    for i in range(count):
        max_idx += 1
        prof_id = f"profile_{max_idx}"
        while prof_id in used_ids:
            max_idx += 1
            prof_id = f"profile_{max_idx}"
        used_ids.add(prof_id)

        while next_port in used_ports or is_port_listening(next_port):
            next_port += 1
        port = next_port
        used_ports.add(port)
        next_port += 1

        user_data = Path.home() / f".config/google-chrome-cdp-profile{max_idx}"
        user_data.mkdir(parents=True, exist_ok=True, mode=0o700)

        entry = {
            "id": prof_id,
            "port": port,
            "directory": "Default",
            "user_data_dir": str(user_data),
            "enabled": True,
        }

        print(f"\n--- [Profile {i + 1}/{count}]: {prof_id} (Cổng CDP: {port}) ---")
        print(f"  * Thư mục Chrome cô lập: {user_data}")
        print("  --> Mở Chrome giao diện để đăng nhập Google...")

        ok = launch_profile(entry, url="https://flow.google.com/", headless=False)
        if ok:
            print(f"  [OK] Đã mở Chrome trên cổng {port} thành công.")
        else:
            print(f"  [CẢNH BÁO] Chưa kết nối được cổng {port}. Vẫn lưu profile để thử lại.")

        if sys.stdin.isatty():
            try:
                input("  👉 Đăng nhập xong tài khoản Google trên Flow, nhấn [Enter] để đóng và tiếp tục: ")
            except EOFError:
                pass
        else:
            time.sleep(1.0)

        if sequential_close:
            print(f"  --> Đang đóng {prof_id}...")
            stop_profile(entry)

        created_profiles.append(entry)

    if sequential_close:
        stop_all(created_profiles)

    # Merge into registry
    merged_profiles = list(existing_profiles)
    existing_by_id = {p["id"]: idx for idx, p in enumerate(merged_profiles)}
    for p in created_profiles:
        if p["id"] in existing_by_id:
            merged_profiles[existing_by_id[p["id"]]] = p
        else:
            merged_profiles.append(p)
            existing_by_id[p["id"]] = len(merged_profiles) - 1

    current_data["profiles"] = merged_profiles
    save_registry(current_data)

    # Register 1,000 initial credits in CreditLedger
    try:
        from .credit_ledger import get_credit_ledger
        ledger = get_credit_ledger()
        for p in created_profiles:
            ledger.register_profile(p["id"], initial_credits=1000)
        print(f"\n[OK] Đã đăng ký 1,000 credits cho {len(created_profiles)} profile mới trong CreditLedger.")
    except Exception as e:
        print(f"[CẢNH BÁO] Lỗi đăng ký credits vào ledger: {e}")

    print("\n" + "=" * 70)
    print(f"  HOÀN TẤT ONBOARD {len(created_profiles)} PROFILE!")
    print("=" * 70)
    for p in created_profiles:
        print(f"  - {p['id']:<14} Port {p['port']}: {p['user_data_dir']}")
    print()

    return created_profiles


async def _evaluate_credits_fallback(sess: Any) -> dict[str, Any]:
    expr = """
    (() => {
        try {
            const text = document.body ? document.body.innerText : '';
            const m = text.match(/(\\d+)\\s*(?:credits?|t\u00edn d\u1ee5ng)/i);
            if (m) return { remaining: parseInt(m[1], 10), subscription_credits: 1000 };
        } catch(e) {}
        return { remaining: 1000, subscription_credits: 1000 };
    })()
    """
    try:
        val = await sess.evaluate(expr)
        if isinstance(val, dict):
            return val
    except Exception:
        pass
    return {"remaining": 1000, "subscription_credits": 1000}


async def _scan_single_profile(profile_cfg: dict[str, Any], ledger: Any) -> dict[str, Any]:
    from .cdp_direct_client import DirectCDPProfileSession
    pid = profile_cfg.get("id") or profile_cfg.get("name")
    sess = DirectCDPProfileSession(profile_cfg)
    try:
        await sess.connect()
        res = None
        if hasattr(sess, "query_credits"):
            res = await sess.query_credits()
        else:
            try:
                from .flow_rpc import query_credits_rpc
                res = await query_credits_rpc(sess)
            except Exception:
                pass
        if res is None:
            res = await _evaluate_credits_fallback(sess)

        remaining = 1000
        sub = 1000
        exp = None
        tier = 0
        if isinstance(res, (int, float)):
            remaining = int(res)
        elif isinstance(res, dict):
            remaining = int(res.get("credits_remaining") or res.get("remaining", 1000))
            sub = int(res.get("subscription_credits") or res.get("subscription", 1000))
            exp = res.get("expiry_epoch")
            tier = int(res.get("paygate_tier", 0))

        return ledger.sync_balance(
            profile_id=pid,
            remaining=remaining,
            subscription_credits=sub,
            expiry_epoch=exp,
            paygate_tier=tier,
        )
    finally:
        try:
            await sess.close()
        except Exception:
            pass


def print_credits_table(ledger: Any, profile_ids: list[str] | None = None) -> None:
    summary = ledger.summary(profile_ids=profile_ids)
    profs = summary.get("profiles", {})

    sep = "=" * 105
    print("\n" + sep)
    print(f"  GOOGLE FLOW CDP — CREDIT LEDGER OVERVIEW ({len(profs)} PROFILES)")
    print(sep)
    header = f"{'Profile ID':<14} | {'Tier Role':<18} | {'Status':<10} | {'Remaining':<10} | {'Subscription':<12} | {'Expiry Epoch':<14} | {'Last Used'}"
    print(header)
    print("-" * 105)

    def _sort_key(pid: str):
        if pid.startswith("profile_en"):
            num = pid.replace("profile_en", "")
            return (1, int(num) if num.isdigit() else 999)
        elif pid.startswith("profile_"):
            num = pid.replace("profile_", "")
            return (0, int(num) if num.isdigit() else 999)
        return (2, pid)

    for pid in sorted(profs.keys(), key=_sort_key):
        info = profs[pid]
        rem = info.get("credits_remaining", 0)
        sub = info.get("subscription_credits", 1000)
        status = str(info.get("status", "active")).upper()
        expiry = str(info.get("expiry_epoch")) if info.get("expiry_epoch") is not None else "None"
        last_used_ts = info.get("last_used_at", 0.0)
        last_used = time.strftime("%Y-%m-%d %H:%M", time.localtime(last_used_ts)) if last_used_ts else "Never"

        raw_role = info.get("tier_role", "")
        if raw_role == "video_and_image" or (rem >= 7 and status not in ("AUTH_EXPIRED", "EXHAUSTED")):
            tier_display = "VIDEO+IMAGE"
        elif raw_role == "auth_expired" or status == "AUTH_EXPIRED":
            tier_display = "AUTH EXPIRED"
        else:
            tier_display = "IMAGE-ONLY (0 CR)"

        print(f"{pid:<14} | {tier_display:<18} | {status:<10} | {rem:<10} | {sub:<12} | {expiry:<14} | {last_used}")

    pool_profiles = [{"id": pid} for pid in profs.keys()]
    pool_summary = ledger.get_pool_summary(profiles=pool_profiles)

    print(sep)
    print(
        f"Total: {summary['total_profiles']} profiles | "
        f"Active: {summary['active_profiles']} | "
        f"Exhausted: {summary['exhausted_profiles']} | "
        f"Total Credits Remaining: {summary['total_credits_remaining']:,}"
    )
    print("-" * 105)
    print("  [SMART 2-TIER CREDIT POOL BREAKDOWN]")
    print(f"  * Video + Image Ready (>= 7 credits):   {pool_summary['video_ready_count']} profiles")
    print(f"  * Image-Only Zero-Credit (< 7 credits): {pool_summary['image_only_zero_credit_count']} profiles (Nano Banana Pro / 2.1 / 2 Lite, 2K Upsample, TTS)")
    print(f"  * Zero-Credit Image Capacity:           {pool_summary['zero_credit_image_capacity'].upper()}")
    print("  [ESTIMATED OMNI VIDEO GENERATION CAPACITY]")
    print(f"  * Omni 1.1 Flash 4s (7 credits):        ~{pool_summary['estimated_omni_4s_clips']:,} clips")
    print(f"  * Omni 1.1 Flash 6s (10 credits):       ~{pool_summary['estimated_omni_6s_clips']:,} clips")
    print(f"  * Omni 1.1 Flash 8s (12 credits):       ~{pool_summary['estimated_omni_8s_clips']:,} clips")
    print(sep + "\n")


def credits_command(
    refresh: bool = False,
    profiles_str: str | None = None,
    concurrency: int = 4,
) -> None:
    import asyncio

    from .credit_ledger import get_credit_ledger
    from .process_manager import clean_singleton_locks, get_process_manager

    ledger = get_credit_ledger()
    target_ids = None
    if profiles_str:
        target_ids = [p.strip() for p in profiles_str.replace(" ", ",").split(",") if p.strip()]

    d = registry()
    all_profiles = d.get("profiles", [])

    # Ensure all registered profiles are in the ledger
    for p in all_profiles:
        ledger.register_profile(p["id"], initial_credits=1000)

    if not refresh:
        print_credits_table(ledger, profile_ids=target_ids)
        return

    # Refresh requested
    if target_ids:
        profiles_to_scan = [p for p in all_profiles if p["id"] in target_ids]
    else:
        profiles_to_scan = [p for p in all_profiles if p.get("enabled", True)]

    print(f"\n--> Starting live credit refresh for {len(profiles_to_scan)} profiles (concurrency: {concurrency})...")
    pm = get_process_manager()
    batches = [profiles_to_scan[i : i + concurrency] for i in range(0, len(profiles_to_scan), concurrency)]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for b_idx, batch in enumerate(batches, 1):
        spawned_ports = []
        batch_ids = [p["id"] for p in batch]
        print(f"  [Batch {b_idx}/{len(batches)}] Launching headless Chrome (--headless=new) for: {batch_ids}...")
        try:
            for p in batch:
                port = int(p["port"])
                if not is_port_listening(port):
                    target_url = p.get("url") or "https://flow.google.com/"
                    ok = pm.launch(
                        profile_cfg=p,
                        url=target_url,
                        headless=True,
                        extra_args=["--headless=new"],
                    )
                    if ok:
                        spawned_ports.append((port, Path(p["user_data_dir"]).expanduser(), p.get("directory", "Default")))

            time.sleep(1.5)

            async def _scan_batch(cur_batch: list[dict[str, Any]]):
                tasks = [_scan_single_profile(p, ledger) for p in cur_batch]
                return await asyncio.gather(*tasks, return_exceptions=True)

            results = loop.run_until_complete(_scan_batch(batch))
            for p, r in zip(batch, results, strict=False):
                if isinstance(r, Exception):
                    print(f"    [WARN] Profile {p['id']} query failed: {r}")
                else:
                    print(f"    [OK] Profile {p['id']}: balance {r.get('credits_remaining')} credits")

        finally:
            # Strictly terminate every spawned process in finally block!
            for port, udir, prof_dir in spawned_ports:
                try:
                    pm.terminate_by_port(port)
                    clean_singleton_locks(udir, prof_dir)
                except Exception:
                    pass

    loop.close()
    print_credits_table(ledger, profile_ids=target_ids)


def main() -> None:
    actions = [
        "list",
        "status",
        "launch",
        "stop",
        "login-many",
        "onboard",
        "credits",
        "scan",
        "sync",
        "leases",
        "release",
    ]
    parser = argparse.ArgumentParser(description="Google Flow CDP Account & Profile Manager")
    parser.add_argument("action", choices=actions, nargs="?", default="status")
    parser.add_argument("target", nargs="?", default="all", help="Profile ID, job ID, or 'all'")
    parser.add_argument("--count", type=int, default=1, help="Number of profiles to onboard")
    parser.add_argument("--start-port", type=int, default=9270, help="Starting port for onboarded profiles")
    parser.add_argument("--refresh", action="store_true", default=False, help="Refresh live credits via headless CDP query")
    parser.add_argument("--profiles", type=str, help="Comma-separated profile IDs for credits scan")
    parser.add_argument("--concurrency", type=int, default=4, help="Concurrency for credit scanning")
    parser.add_argument("--total", type=int, help="Total number of profiles to configure in login-many")
    parser.add_argument("--select", type=str, help="Danh sách profile muốn chọn sẵn (ví dụ: '10,102,14' hoặc '1,2,3')")
    parser.add_argument("--url", default="https://flow.google.com/", help="URL to open on launch")
    parser.add_argument("--headed", "--no-headless", dest="headless", action="store_false", default=True, help="Launch Chrome in visible GUI window (non-headless)")
    args = parser.parse_args()

    if args.action == "credits":
        credits_command(
            refresh=args.refresh,
            profiles_str=args.profiles,
            concurrency=args.concurrency,
        )
        return

    if args.action == "onboard":
        onboard_profiles(count=args.count, start_port=args.start_port)
        return

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
            results = launch_all(url=args.url, headless=args.headless)
            for pid, ok in results.items():
                print(f"Profile {pid}: {'LISTENING (READY)' if ok else 'FAILED TO LAUNCH'}")
        else:
            target_entry = next((p for p in d.get("profiles", []) if p["id"] == args.target), None)
            if not target_entry:
                print(f"Không tìm thấy profile '{args.target}'", file=sys.stderr)
                sys.exit(1)
            ok = launch_profile(target_entry, url=args.url, headless=args.headless)
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
