#!/usr/bin/env bash
set -e

echo "=== Setting up & Launching 3 Chrome Profiles for Video Pilot (Flow CDP) ==="

HEADLESS="${HEADLESS:-1}"
HEADLESS_FLAG=""
if [ "$HEADLESS" = "1" ] || [ "$HEADLESS" = "true" ]; then
  HEADLESS_FLAG="--headless=new"
  unset DISPLAY
else
  export DISPLAY="${DISPLAY:-:0}"
fi
CHROME_BIN="/opt/google/chrome/google-chrome"
if [ ! -f "$CHROME_BIN" ]; then
  CHROME_BIN="/opt/google/chrome/chrome"
fi
if [ ! -f "$CHROME_BIN" ]; then
  CHROME_BIN="$(which google-chrome 2>/dev/null || which google-chrome-stable 2>/dev/null || which chromium 2>/dev/null || echo '/opt/google/chrome/chrome')"
fi

ORIG_DIR="$HOME/.config/google-chrome"
P1_DIR="$HOME/.config/google-chrome-cdp-p1"
P2_DIR="$HOME/.config/google-chrome-cdp-p2"
P3_DIR="$HOME/.config/google-chrome-cdp-p3"

setup_profile_dir() {
  local target_dir="$1"
  local prof_name="$2"
  
  echo "Syncing $prof_name to $target_dir..."
  mkdir -p "$target_dir"
  
  if [ -f "$ORIG_DIR/Local State" ]; then
    cp -u "$ORIG_DIR/Local State" "$target_dir/Local State"
  fi
  
  if [ -d "$ORIG_DIR/$prof_name" ]; then
    mkdir -p "$target_dir/$prof_name"
    rsync -a --update \
      --exclude="Cache*" \
      --exclude="Code Cache*" \
      --exclude="GPUCache*" \
      --exclude="DawnWebGPUCache*" \
      --exclude="DawnGraphiteCache*" \
      --exclude="*.tmp" \
      "$ORIG_DIR/$prof_name/" "$target_dir/$prof_name/"
  fi
  
  rm -f "$target_dir"/Singleton* 2>/dev/null || true
  rm -f "$target_dir/$prof_name"/Singleton* 2>/dev/null || true
}

setup_profile_dir "$P1_DIR" "Profile 106"
setup_profile_dir "$P2_DIR" "Profile 127"
setup_profile_dir "$P3_DIR" "Profile 13"

echo "Launching Chrome Profile 106 on port 9225..."
nohup "$CHROME_BIN" \
  ${HEADLESS_FLAG} \
  --user-data-dir="$P1_DIR" \
  --profile-directory="Profile 106" \
  --remote-debugging-port=9225 \
  --remote-allow-origins="*" \
  --no-first-run \
  --no-default-browser-check \
  --disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,AutomaticTabDiscarding,MemorySaverMode \
  --disable-dev-shm-usage \
  "https://flow.google.com/" </dev/null > /dev/null 2>&1 &

sleep 2

echo "Launching Chrome Profile 127 on port 9223..."
nohup "$CHROME_BIN" \
  ${HEADLESS_FLAG} \
  --user-data-dir="$P2_DIR" \
  --profile-directory="Profile 127" \
  --remote-debugging-port=9223 \
  --remote-allow-origins="*" \
  --no-first-run \
  --no-default-browser-check \
  --disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,AutomaticTabDiscarding,MemorySaverMode \
  --disable-dev-shm-usage \
  "https://flow.google.com/" </dev/null > /dev/null 2>&1 &

sleep 2

echo "Launching Chrome Profile 13 on port 9224..."
nohup "$CHROME_BIN" \
  ${HEADLESS_FLAG} \
  --user-data-dir="$P3_DIR" \
  --profile-directory="Profile 13" \
  --remote-debugging-port=9224 \
  --remote-allow-origins="*" \
  --no-first-run \
  --no-default-browser-check \
  --disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,AutomaticTabDiscarding,MemorySaverMode \
  --disable-dev-shm-usage \
  "https://flow.google.com/" </dev/null > /dev/null 2>&1 &

disown -a 2>/dev/null || true
sleep 3


echo "=== Verifying CDP Remote Debugging Ports ==="
python3 -c "
import socket
for p in [9225, 9223, 9224]:
    try:
        with socket.create_connection(('127.0.0.1', p), timeout=2):
            print(f'Port {p}: LISTENING (READY)')
    except Exception as e:
        print(f'Port {p}: NOT READY ({e})')
"
