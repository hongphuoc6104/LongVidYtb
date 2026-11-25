---
trigger: model_decision
description: Activate whenever launching, managing, or debugging Google Chrome, Flow CDP, or YouTube Studio CDP browser processes.
---

# GPU Headless Chrome (`Flow CDP` & `YouTube Studio CDP`)

1. **SSOT launch only**: `build_optimized_chrome_launch()` (`sys/flow_cdp/resource_locks.py`) + `ProcessGroupManager.launch(headless=True)`. Never raw `subprocess` or headed Chrome in automation.
2. **GPU 90% VRAM (no SwiftShader CPU)**: env `DISPLAY=:0 XAUTHORITY=~/.Xauthority __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia`; flags `--headless=new --ozone-platform=x11 --use-gl=angle --use-angle=gl --enable-gpu-rasterization --ignore-gpu-blocklist --enable-zero-copy --disable-software-rasterizer --force-gpu-mem-available-mb=1843`. No `--disable-dev-shm-usage` when `/dev/shm` ≥ 512 MiB.
3. **Pacing**: `stagger_cross_process_action("chrome_launch", min_interval_sec=3.2, jitter_sec=0.6)` before launch; `stagger_cross_process_action("flow_rpc_submit", min_interval_sec=1.55, jitter_sec=0.35)` before Flow RPC; and `stagger_cross_process_action("flow_video_rpc_submit", min_interval_sec=4.2, jitter_sec=0.8)` (~13–14 video RPCs/min host-wide) before `eb1hJf`/`nprQif` video submissions (`--vid-workers auto` = `3`).
4. **Error 7/8 & Orphans**: On Error 7/8, never kill/reload Chrome for image pools — call `_refresh_recaptcha_session` in place and cooldown; for Stage B video traffic bursts (`TOO_MUCH_TRAFFIC`/`UNUSUAL_ACTIVITY`), pace rotation (`8.0s` fresh / `30.0s` exhausted), always persist `frames/beat_XX.json` sidecar `profile_media_ids`, and auto-failover `veo_3_1_lite -> omni_flash` Seam after `>= 2` traffic blocks. On teardown or `hasAt=False`, reap via `terminate_by_port(port)`.
