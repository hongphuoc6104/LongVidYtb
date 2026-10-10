# Troubleshooting Colab GPU T4 Headless Display Errors

## 1. Symptoms
- During Remotion video rendering on the remote Colab worker (`sys/colab_bridge/job_worker.py`), the Chromium process crashes with errors:
  - `TargetClosedError: Protocol error (Target.targetCreated): Target closed`
  - `Failed to connect to the bus: Could not parse server address`
  - Rendered video displays completely black or blank white frames.
- Root Cause: Google Colab T4 is a headless Linux virtual machine without an X11 display server or physical monitor. Remotion and Chromium expect a standard graphical environment by default, causing GPU draw and `/dev/shm` IPC failures in headless mode.

---

## 2. Proven Remedies

### Step 1: Always Wrap Chromium with an Executable Shell Wrapper
Remotion's `openBrowser` frequently omits `chromiumOptions.args` passed from Node. Therefore, wrapping the Chromium executable with a shell wrapper script is mandatory:

```bash
#!/usr/bin/env bash
exec "${chrome_path}" \
  --no-sandbox \
  --disable-dev-shm-usage \
  --run-all-compositor-stages-before-draw \
  --disable-gpu-rasterization \
  --enable-gpu \
  --ignore-gpu-blocklist \
  "$@"
```

### Step 2: Configure Mandatory Environment Variables
Before invoking `node render.mjs`, configure the environment variables:
```python
env = dict(
    os.environ,
    VP_CHROME_PATH=str(wrapper_script_path),
    DISABLE_FROM_SURFACE='true'
)
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
