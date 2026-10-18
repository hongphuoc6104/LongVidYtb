#!/usr/bin/env python3
"""Pre-flight smoke test for launching and verifying 10 Chrome CDP profiles simultaneously.

Validates:
1. Staggered launch across ports 9222..9231
2. System resource impact (RAM/CPU/Swap)
3. CDP WebSocket connectivity and Flow page readiness / login status
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import socket
import sys
import time
import urllib.request
from pathlib import Path

# Add sys directory to import path
REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from flow_cdp import accounts


def get_mem_stats() -> dict[str, str]:
    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        data = {}
        for l in lines:
            parts = l.split(":")
            if len(parts) == 2:
                data[parts[0].strip()] = int(parts[1].strip().split()[0])
        total_kb = data.get("MemTotal", 1)
        avail_kb = data.get("MemAvailable", 0)
        used_kb = total_kb - avail_kb
        swap_total_kb = data.get("SwapTotal", 1)
        swap_free_kb = data.get("SwapFree", 0)
        swap_used_kb = swap_total_kb - swap_free_kb
        return {
            "ram_used_gb": f"{used_kb / (1024**2):.2f}",
            "ram_total_gb": f"{total_kb / (1024**2):.2f}",
            "ram_percent": f"{(used_kb / total_kb) * 100:.1f}%",
            "swap_used_gb": f"{swap_used_kb / (1024**2):.2f}",
            "swap_total_gb": f"{swap_total_kb / (1024**2):.2f}",
        }
    except Exception:
        return {
            "ram_used_gb": "?", "ram_total_gb": "?", "ram_percent": "?",
            "swap_used_gb": "?", "swap_total_gb": "?",
        }


async def probe_cdp_flow_page(port: int, timeout: float = 8.0) -> dict[str, any]:
    """Connect over CDP and probe Flow tab readiness & WIZ token."""
    import websockets

    # 1. Fetch JSON list of pages
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/json/list", headers={"User-Agent": "smoke-test"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            pages = json.loads(resp.read().decode("utf-8"))
    except Exception as ex:
        return {"ok": False, "reason": f"HTTP json/list failed: {ex}"}

    target = None
    for p in pages:
        if p.get("type") == "page" and "flow.google" in p.get("url", ""):
            target = p
            break
    if not target:
        # Fall back to first page
        target = next((p for p in pages if p.get("type") == "page"), None)

    if not target or "webSocketDebuggerUrl" not in target:
        return {"ok": False, "reason": "No valid page target found"}

    ws_url = target["webSocketDebuggerUrl"]
    cur_url = target.get("url", "")

    # Check for login redirection
    if "accounts.google.com" in cur_url:
        return {
            "ok": False,
            "logged_in": False,
            "url": cur_url,
            "reason": "Needs Google login (accounts.google.com)",
        }

    # 2. Evaluate WIZ CSRF token and readyState inside page
    try:
        async with websockets.connect(ws_url, ping_interval=None, close_timeout=3.0) as ws:
            probe_expr = """
            (() => {
                const wiz = globalThis.WIZ_global_data || {};
                const at = Boolean(wiz.SNlM0e);
                const exec = typeof window.grecaptcha?.enterprise?.execute === 'function';
                return {
                    url: window.location.href,
                    readyState: document.readyState,
                    hasAtToken: at,
                    hasRecaptcha: exec
                };
            })()
            """
            eval_msg = {
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {"expression": probe_expr, "returnByValue": True, "awaitPromise": False},
            }
            await ws.send(json.dumps(eval_msg))
            resp_raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
            resp = json.loads(resp_raw)
            val = resp.get("result", {}).get("result", {}).get("value", {})
            return {
                "ok": True,
                "url": val.get("url", cur_url),
                "readyState": val.get("readyState"),
                "hasAtToken": val.get("hasAtToken", False),
                "hasRecaptcha": val.get("hasRecaptcha", False),
                "logged_in": "accounts.google.com" not in val.get("url", cur_url),
            }
    except Exception as ex:
        return {"ok": False, "url": cur_url, "reason": f"CDP evaluate failed: {ex}"}


def main():
    parser = argparse.ArgumentParser(description="Smoke test: Launch and probe 10 Chrome CDP profiles")
    parser.add_argument("--stop", action="store_true", help="Stop all profiles after test")
    parser.add_argument("--stagger", type=float, default=1.5, help="Seconds between launching each profile")
    args = parser.parse_args()

    reg = accounts.registry()
    profs = reg.get("profiles", [])
    if not profs:
        print("[!] No profiles found in registry.")
        sys.exit(1)

    print("=" * 80)
    print(f"  SMOKE TEST: KHỞI ĐỘNG VÀ KIỂM TRA {len(profs)} PROFILE CHROME CDP")
    print("=" * 80)
    mem_before = get_mem_stats()
    print(f"[*] Tài nguyên trước khởi động: RAM {mem_before['ram_used_gb']}/{mem_before['ram_total_gb']} GB ({mem_before['ram_percent']}) | Swap {mem_before['swap_used_gb']} GB")

    launched = []
    print(f"\n[*] Bắt đầu khởi động tuần tự (Stagger {args.stagger}s)...")
    for i, p in enumerate(profs, 1):
        port = p["port"]
        pid_name = p["id"]
        dir_name = p["directory"]
        is_open = accounts.is_port_listening(port)
        if is_open:
            print(f"  [{i:2d}/10] {pid_name:<10} (Port {port}): Cổng đã mở sẵn từ trước.")
        else:
            print(f"  [{i:2d}/10] {pid_name:<10} (Port {port}): Đang khởi động {dir_name}...", end="", flush=True)
            ok = accounts.launch_profile(p, url="https://flow.google.com/")
            if ok:
                print(" -> OK (Port đã mở).")
            else:
                print(" -> [!] THẤT BẠI (Timeout mở cổng).")
        launched.append(p)
        if i < len(profs):
            time.sleep(args.stagger)

    mem_after = get_mem_stats()
    print(f"\n[*] Tài nguyên sau khi mở {len(profs)} Profile: RAM {mem_after['ram_used_gb']}/{mem_after['ram_total_gb']} GB ({mem_after['ram_percent']}) | Swap {mem_after['swap_used_gb']} GB")

    print("\n[*] Đang kiểm tra chi tiết trạng thái trang Flow qua CDP WebSocket...")
    print("-" * 80)
    print(f"{'Profile ID':<12} | {'Port':<6} | {'Listening':<9} | {'Flow Status / URL':<45}")
    print("-" * 80)

    summary = []
    for p in profs:
        port = p["port"]
        listening = accounts.is_port_listening(port)
        status_desc = "Cổng đóng"
        logged_in = False
        if listening:
            diag = asyncio.run(probe_cdp_flow_page(port))
            if diag.get("ok"):
                at = "WIZ-Token: OK" if diag.get("hasAtToken") else "WIZ: No"
                rec = "Recaptcha: OK" if diag.get("hasRecaptcha") else "Recaptcha: No"
                status_desc = f"Flow OK ({at}, {rec})"
                logged_in = True
            elif diag.get("logged_in") is False:
                status_desc = f"Cần đăng nhập ({diag.get('reason')})"
            else:
                status_desc = f"Lỗi: {diag.get('reason') or diag.get('url')}"
        print(f"{p['id']:<12} | {port:<6} | {str(listening):<9} | {status_desc[:45]}")
        summary.append({
            "id": p["id"],
            "port": port,
            "listening": listening,
            "logged_in": logged_in,
            "details": status_desc,
        })

    print("-" * 80)
    total_listening = sum(1 for s in summary if s["listening"])
    total_ready = sum(1 for s in summary if s["logged_in"])
    print(f"\n[+] Tổng kết: {total_listening}/{len(profs)} cổng đang mở, {total_ready}/{len(profs)} profile sẵn sàng tạo ảnh.")

    if args.stop:
        print("\n[*] Đang tắt tất cả các profile...")
        accounts.stop_all(profs)
        print("[✓] Đã tắt toàn bộ Chrome instances.")


if __name__ == "__main__":
    main()
