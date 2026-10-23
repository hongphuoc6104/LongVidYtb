#!/usr/bin/env python3
"""Video Pilot — Flow CDP Profile & Login Wizard launcher.

Guides the operator through multi-profile Chrome CDP onboarding for Google Flow.
Usage:
  python3 sys/scripts/login_flow_profiles.py [--total N]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

from flow_cdp.accounts import launch_all, login_many, status_all, stop_all


def main() -> int:
    parser = argparse.ArgumentParser(description="Google Flow CDP Multi-Profile Wizard")
    parser.add_argument("--total", type=int, help="Tổng số Profile muốn cấu hình (mặc định: 3)")
    parser.add_argument("--status", action="store_true", help="Kiểm tra trạng thái cổng và kết nối CDP")
    parser.add_argument("--launch", action="store_true", help="Khởi chạy toàn bộ các Profile đã cấu hình")
    parser.add_argument("--headed", action="store_true", help="Mở cửa sổ giao diện để thao tác trực tiếp")
    parser.add_argument("--stop", action="store_true", help="Dừng toàn bộ các Profile Chrome CDP")
    args = parser.parse_args()

    if args.status:
        import json
        print(json.dumps(status_all(), indent=2, ensure_ascii=False))
        return 0

    if args.launch:
        results = launch_all(headless=not args.headed)
        for pid, ok in results.items():
            print(f"Profile {pid}: {'LISTENING (READY)' if ok else 'FAILED TO LAUNCH'}")
        return 0

    if args.stop:
        stopped = stop_all()
        print(f"Đã dừng {len(stopped)} profile: {', '.join(stopped)}")
        return 0

    login_many(total=args.total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
