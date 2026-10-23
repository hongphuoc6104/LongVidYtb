#!/usr/bin/env bash
set -e

echo "=== Launching 3 Chrome Profiles with CDP Remote Debugging ==="

HEADLESS="${HEADLESS:-1}"
HEADLESS_FLAG=""
if [ "$HEADLESS" = "1" ] || [ "$HEADLESS" = "true" ]; then
  HEADLESS_FLAG="--headless=new"
  unset DISPLAY
else
  export DISPLAY="${DISPLAY:-:0}"
fi

CHROME_BIN="/opt/google/chrome/chrome"
USER_DATA_DIR="$HOME/.config/google-chrome"

# Remove any stale singleton lock
rm -f "$USER_DATA_DIR"/Singleton* 2>/dev/null || true

# 1. Launch Primary Chrome process with Remote Debugging on port 9222 for Profile 1
echo "Launching Profile 1 with Remote Debugging on port 9222..."
"$CHROME_BIN" \
  ${HEADLESS_FLAG} \
  --user-data-dir="$USER_DATA_DIR" \
  --profile-directory="Profile 1" \
  --remote-debugging-port=9222 \
  --remote-allow-origins="*" \
  --no-first-run \
  --no-default-browser-check \
  --disable-dev-shm-usage \
  "https://flow.google.com/" > /dev/null 2>&1 &

sleep 2

# 2. Open Profile 2 window in the same Chrome instance
echo "Opening Profile 2 window..."
"$CHROME_BIN" \
  ${HEADLESS_FLAG} \
  --user-data-dir="$USER_DATA_DIR" \
  --profile-directory="Profile 2" \
  --disable-dev-shm-usage \
  "https://flow.google.com/" > /dev/null 2>&1 &

sleep 1

# 3. Open Profile 3 window in the same Chrome instance
echo "Opening Profile 3 window..."
"$CHROME_BIN" \
  ${HEADLESS_FLAG} \
  --user-data-dir="$USER_DATA_DIR" \
  --profile-directory="Profile 3" \
  --disable-dev-shm-usage \
  "https://flow.google.com/" > /dev/null 2>&1 &

sleep 1

# 4. Start port forwarder for 9223 and 9224 in background
echo "Starting CDP Port Forwarder (9223, 9224 -> 9222)..."
pkill -f "port_forwarder.py" 2>/dev/null || true
nohup "$(cd "$(dirname "$0")/.." && pwd)/.venv/bin/python" "$(cd "$(dirname "$0")" && pwd)/port_forwarder.py" > /tmp/port_forwarder.log 2>&1 &

sleep 1

echo "=== Chrome 3-Profile CDP Setup Complete ==="
echo "Port 9222 (Profile 1): Open"
echo "Port 9223 (Profile 2): Open (Forwarded)"
echo "Port 9224 (Profile 3): Open (Forwarded)"
