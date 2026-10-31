#!/usr/bin/env bash
set -euo pipefail

DASHBOARD_SCRIPT="/home/hongphuoc6104/Desktop/vp-agent-core/sys/tools/youtube_dashboard.py"
PORT=8765
URL="http://127.0.0.1:${PORT}"

if [[ "${1:-}" == "--web" || "${1:-}" == "-w" ]]; then
    if ! ss -tln | grep -q ":${PORT} "; then
        nohup python3 "$DASHBOARD_SCRIPT" --serve --port "$PORT" >/tmp/vp_youtube_dashboard.log 2>&1 &
        sleep 1.2
    fi
    echo "🚀 Đang mở Web Dashboard tại: ${URL}"
    xdg-open "$URL" >/dev/null 2>&1 || true
    exit 0
fi

if [[ "${1:-}" == "--stop" ]]; then
    pkill -f "youtube_dashboard.py --serve" || true
    echo "🛑 Đã dừng Web Dashboard server."
    exit 0
fi

exec python3 "$DASHBOARD_SCRIPT" "$@"
