---
trigger: always_on
description: Mandatory rules for launching hidden (headless) Chrome on local NVIDIA GPU (90% VRAM) and preventing orphan/CPU-fallback Chrome processes.
---

# Mandatory Rule: GPU Headless Chrome (`--headless=new` + `90%` VRAM)

All agents and subagents operating in `vp-agent-core` MUST strictly enforce the following invariants whenever launching, managing, or debugging Google Chrome / CDP (`Flow CDP` or `YouTube Studio CDP`):

## 1. 100% Hidden GPU Launch via SSOT (`build_optimized_chrome_launch`)
- **Single Source of Truth**: Every Chrome launch MUST go through [`build_optimized_chrome_launch()`](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/flow_cdp/resource_locks.py#L126-L218) and [`ProcessGroupManager.launch()`](file:///home/hongphuoc6104/Desktop/vp-agent-core/sys/flow_cdp/process_manager.py#L447-L545) with `headless=True`.
- **Forbidden Direct Spawns**: NEVER invoke `google-chrome` or `/opt/google/chrome/chrome` directly via raw `subprocess.Popen` outside `build_optimized_chrome_launch()`, and NEVER launch visible GUI Chrome (`headless=False` / `--no-headless` / `--headed`) during automated production or publishing (only one-time interactive `accounts onboard` may use a visible window).
- **Mandatory GPU Flags & Environment (`90%` VRAM = `1843 MiB` on `Quadro P620 2048 MiB`)**:
  ```bash
  DISPLAY=:0 \
  XAUTHORITY=~/.Xauthority \
  __NV_PRIME_RENDER_OFFLOAD=1 \
  __GLX_VENDOR_LIBRARY_NAME=nvidia \
  /opt/google/chrome/chrome \
    --headless=new \
    --ozone-platform=x11 \
    --enable-gpu-rasterization \
    --ignore-gpu-blocklist \
    --enable-zero-copy \
    --disable-software-rasterizer \
    --use-gl=angle \
    --use-angle=gl \
    --force-gpu-mem-available-mb=1843 \
    --hide-scrollbars \
    --mute-audio
  ```
- **RAM Shared Memory (`/dev/shm`)**: NEVER pass `--disable-dev-shm-usage` when `/dev/shm` has `>= 512 MiB` free (`has_sufficient_dev_shm()`).

## 2. Anti-IP-Ban Staggering, Concurrency & Warm Session Preservation
- **Staggered Launch**: Enforce `stagger_cross_process_action("chrome_launch", min_interval_sec=3.2, jitter_sec=0.6)` before every browser spawn. NEVER launch multiple Chrome instances simultaneously.
- **Global Jittered RPC Pacer**: Enforce `stagger_cross_process_action("flow_rpc_submit", min_interval_sec=1.55, jitter_sec=0.35)` (`~34–38 RPCs/min` host-wide).
- **Warm Session Preservation (`ERR-20261010-07`)**: On Error 7/8 (`PUBLIC_ERROR_UNUSUAL_ACTIVITY` / `TOO_MUCH_TRAFFIC`), NEVER kill/relaunch Chrome and NEVER reload the tab; refresh reCAPTCHA in-place (`_refresh_recaptcha_session`) and place the profile on cooldown.

## 3. Strict Process Group Teardown & Zero Orphans
- **Never Leave Orphan Chrome Instances**: If a parent Python runner is stopped or a profile fails authentication (`hasAt=False` / `NO_AT_TOKEN`), MUST immediately call `ProcessGroupManager.terminate_by_port(port)` or `clean_orphans_from_registry()` to reap the entire Chrome process group (`PGID`) and release VRAM.
- **GPU Verification**: Verify active Chrome GPU binding via `nvidia-smi` (`Type: G`, process attached to `Quadro P620`) and CDP `SystemInfo.getInfo` (`ANGLE (NVIDIA Corporation, Quadro P620/PCIe/SSE2, OpenGL 4.5.0)`).
