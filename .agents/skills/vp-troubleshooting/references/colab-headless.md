# Troubleshooting Colab GPU T4 Headless Display Errors

## 1. Symptoms
- During Remotion video rendering on the remote Colab worker (`sys/colab_bridge/job_worker.py`), the Chromium process crashes with errors:
  - `TargetClosedError: Protocol error (Target.targetCreated): Target closed`
  - `Failed to connect to the bus: Could not parse server address`
  - Rendered video displays completely black or blank white frames.
- Root Cause: Google Colab T4 is a headless Linux virtual machine without an X11 display server or physical monitor. Remotion and Chromium expect a standard graphical environment by default, causing GPU draw and `/dev/shm` IPC failures in headless mode.

---

## 2. Proven Remedies

### Step 1: Wrap Chromium with Safe Headless Shell Wrapper (NVIDIA Headless EGL, No Xvfb)
Remotion's `openBrowser` drops custom flags passed from Node, and Colab T4 images pre-install `/usr/lib64-nvidia/libEGL_nvidia.so.0` without `/usr/share/glvnd/egl_vendor.d/10_nvidia.json`. Chromium must execute via `chrome-wrapper.sh` which registers `10_nvidia.json` for hardware `gl-egl` (or falls back to `--disable-gpu-rasterization` when NVIDIA EGL is absent), enforces synchronous tile locks, and strictly avoids `xvfb-run` / `--use-angle=gl`:

```bash
#!/usr/bin/env bash
export LD_LIBRARY_PATH="/usr/lib64-nvidia:${LD_LIBRARY_PATH:-}"
if [ -f "/usr/lib64-nvidia/libEGL_nvidia.so.0" ]; then
  mkdir -p /usr/share/glvnd/egl_vendor.d 2>/dev/null || true
  if [ ! -f "/usr/share/glvnd/egl_vendor.d/10_nvidia.json" ]; then
    printf '{"file_format_version":"1.0.0","ICD":{"library_path":"/usr/lib64-nvidia/libEGL_nvidia.so.0"}}\n' > /usr/share/glvnd/egl_vendor.d/10_nvidia.json 2>/dev/null || true
  fi
  GPU_FLAGS="--use-gl=angle --use-angle=gl-egl --enable-gpu-rasterization --ignore-gpu-blocklist"
else
  GPU_FLAGS="--disable-gpu-rasterization"
fi
exec "${chrome_path}" \
  --no-sandbox \
  --disable-dev-shm-usage \
  --run-all-compositor-stages-before-draw \
  --disable-checker-imaging \
  --disable-new-content-rendering-timeout \
  $GPU_FLAGS \
  "$@"
```

Execute Remotion directly in headless mode on Colab (`gl: 'angle-egl'`, `videoBitrate: '6M'` for `h264_nvenc`):
```bash
node renderer/render.mjs <job_dir>
```

### Step 2: Configure Mandatory Environment Variables (Unset `DISPLAY`)
Before invoking `node render.mjs`, configure the environment variables and remove `DISPLAY`:
```python
env = dict(
    os.environ,
    VP_CHROME_PATH=str(wrapper_script_path),
    DISABLE_FROM_SURFACE='true'
)
env.pop('DISPLAY', None)
```

### Step 3: Check Shared Memory `/dev/shm`
Colab instances often have constrained `/dev/shm` allocations. The `--disable-dev-shm-usage` flag forces Chromium to utilize `/tmp` instead of `/dev/shm`, avoiding kernel OOM termination during high-resolution video renders.

### Step 4: Verify Active Session & Runtime Before Upload (`ensure_colab_render_runtime`)
Before calling `upload` or `exec` on `-s video-pilot-tts`, verify via `account_cli.py ... sessions` that `video-pilot-tts` is active on the server; if expired (`No active sessions found on server`), allocate a new T4 session (`new -s video-pilot-tts --gpu T4`) and verify `/content/render-runtime/chrome-wrapper.sh` exists before submitting chapter builds.

---

## 3. Automated Verification Command
Run the automated test suite to confirm all safety flags are active:
```bash
pytest sys/tests/test_renderer_tile_integrity.py
```
If 6/6 tests pass, the system is verified safe for rendering on headless Colab T4.
