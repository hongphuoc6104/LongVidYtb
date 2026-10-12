# Remote Video Rendering & Sticker Matting (`Remotion` on Colab T4)

This reference covers remote video rendering on Google Colab T4 via both the standard job worker ([`sys/colab_bridge/job_worker.py`](../../../../sys/colab_bridge/job_worker.py) & [`sys/colab_bridge/job_protocol.py`](../../../../sys/colab_bridge/job_protocol.py)) and the multi-chapter batch orchestrator ([`render_all_on_colab.py`](../../../../sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py)).

---

## 1. Mandatory Headless Chromium Wrapper (`chrome-wrapper.sh`)

Google Colab T4 VMs are headless Linux containers without an X11 display server and with constrained `/dev/shm` shared memory. Furthermore, Remotion's `openBrowser` drops custom flags passed via Node options.

### Mandatory Headless Wrapper, NVIDIA EGL & NVENC Hardware Encoding
Every Colab render runtime (`/content/render-runtime` or `/content/render-runtime-<lock_hash>`) registers `/usr/share/glvnd/egl_vendor.d/10_nvidia.json` (so `libGLdispatch` discovers `/usr/lib64-nvidia/libEGL_nvidia.so.0`) and wraps Playwright's Chromium binary in `chrome-wrapper.sh` (`chmod 0755`):

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

And invoke Remotion directly in headless mode (strictly avoiding `xvfb-run` and unsetting `DISPLAY`):

```python
env = dict(
    os.environ,
    VP_CHROME_PATH="/content/render-runtime/chrome-wrapper.sh",
    DISABLE_FROM_SURFACE="true",
)
env.pop("DISPLAY", None)

cmd = ["node", "renderer/render.mjs", str(job_dir)]
subprocess.run(cmd, env=env, check=True)
```

### Why Each Setting Is Mandatory
- **NVIDIA Headless EGL (`10_nvidia.json` + `--use-gl=angle --use-angle=gl-egl`, No `xvfb-run`)**: Colab T4 containers pre-install `/usr/lib64-nvidia/libEGL_nvidia.so.0` but omit `10_nvidia.json` in `/usr/share/glvnd/egl_vendor.d/`. Writing `10_nvidia.json` and selecting `gl-egl` binds headless Chromium directly to `ANGLE (NVIDIA Corporation, Tesla T4/PCIe/SSE2, OpenGL ES 3.2)` without X11. `Xvfb` and `--use-angle=gl` are strictly prohibited because Xvfb is a CPU RAM framebuffer that deadlocks ANGLE GLX sockets (>300s timeout).
- `--no-sandbox`: Required inside containerized Colab root user environments.
- `--disable-dev-shm-usage`: Forces Chromium IPC buffers into `/tmp` instead of `/dev/shm`, preventing sudden `TargetClosedError` OOM kills on 1080p renders.
- **4-Layer Synchronous Tile Lock (`--run-all-compositor-stages-before-draw` + `--disable-checker-imaging` + `--disable-new-content-rendering-timeout` + `DISABLE_FROM_SURFACE=true` + `<Img decoding="sync">`)**: Prevents Chromium's compositor from capturing a frame before all GPU raster tiles and image decodes complete, eliminating rectangular missing-tile (checkerboarding) artifacts.
- **NVENC Acceleration (`videoBitrate: '6M'` + `hardwareAcceleration: 'if-possible'`)**: Explicitly setting `videoBitrate: '6M'` disables Remotion's default CRF flag so `h264_nvenc` hardware encoding activates on the Tesla T4 GPU.

---

## 2. Visual Effect & Performance Invariants on Colab T4

### 2.1. Never Enable Blanket Full-Frame `line_boil: true` on 1080p Raster Plates (`ERR-20261009-01`)
- Setting `"line_boil": true` on full-screen $1920 \times 1080$ raster beats forces Chromium to evaluate 2-octave SVG `<feTurbulence>` and `<feDisplacementMap scale={3}>` across 2,073,600 pixels per frame and pulls out-of-bounds pixels into top/left borders. Likewise, full-screen SVG `<feTurbulence>` Film Grain is opt-in only (`enable_film_grain: true`).
- **Consequences**: Severe render slowdown, bloated MP4 bitrate, and black dashed displacement artifacts along top/left borders at `scale = 1.0`.
- **Rule**: Keep `"line_boil": false` (or omitted) on full-frame 1080p background plates; use Remotion camera transitions (`zoom_in`, `zoom_out`, `punch_in`, `pan_left`, `pan_right`, `slide_left`, `shake`, `fade`, `hold`). Reserve `line_boil` / CSS `boilJitter` strictly for cut-out stickers (`scene.layers`).

### 2.2. Remote Sticker Matting ([`matte_sticker.py`](../../../../sys/tools/matte_sticker.py))
- For layered scenes (`scene.layers`), `job_worker.py` loads `tools/matte_sticker.py` on Colab:
  - Flood-fills background transparency from borders and adds a 10px white sticker halo (`create_sticker=True, border=10`).
  - Verifies non-empty alpha bounding box (`im.width >= 40`, `im.height >= 40`, `alpha.getbbox() is not None`) or raises `STICKER_MATTE_FAILED`.
  - Records dimensions and transparency fraction in `layers-report.json`.

### 2.3. Cue-Window Allocation & Full-Bleed Framing (`ERR-20261010-04` & `ERR-20261010-10`)
- Multi-chapter explainer videos must anchor shots directly to each spoken cue (`Cue-Window Allocation` with `0.000s` start drift and `0.83s <= hold <= 3.80s`).
- When rendering with subtitles disabled (`subtitles: false`), `caption_clearance` is `None` (`long_16x9` profile) so generated images fill the entire 16:9 canvas without any artificial zoom/shift compensation, and 100% of images come from `generated_images/ch{num}/` (zero reference frame fallback).

---

## 3. Execution Workflows

### Workflow A: Standard Single-Job Contract (`pilot.py` / `job_worker.py`)
1. `job_protocol.py:build_render_request()` hashes all source files (`output_contract.py`, `story_plan.py`, `subtitles.py`, `renderer/*`, `package.json`, `package-lock.json`, optional `matte_sticker.py`) and media assets into `input.zip` (`<= 512` files, `<= 1GB`).
2. `client.py:render()` uploads `input.zip` and `job_worker.py` to `/content/video-pilot-jobs/<request_id>/` and executes `job_worker.run(...)`.
3. `job_worker.py` renders the outputs, verifies every MP4 with `ffprobe` (`h264`, `aac`, exact `1920x1080` or `1080x1920` dimensions, duration drift `<= 0.25s`), packages `output.zip`, and `validate_render_result()` validates all hashes on the host.

### Workflow B: Multi-Chapter Parallel Batch Orchestrator ([`render_all_on_colab.py`](../../../../sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py))

```bash
# Render a single chapter on a specific Colab T4 account (with force overwrite, no concat)
python3 sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py 1 --force --no-concat --account account-01

# Render all 8 chapters in PARALLEL across 3 Colab T4 accounts simultaneously and concatenate
python3 sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py --force --parallel 3 --accounts account-01,account-02,account-03

# Render all 8 chapters using auto-discovered pool accounts (defaults to --parallel 3)
python3 sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py --force

# Render sequentially on 1 account only (legacy single-session mode)
python3 sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py --force --parallel 1

# Concatenate already-rendered chapters only
python3 sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py --concat-only
```

Safeguards built into `render_all_on_colab.py`:
- **Multi-Account T4 Parallel Dispatch (`render_chapters_parallel`)**: Uses `ColabPoolManager` and `ColabPoolDispatcher` (`sys/colab_bridge/pool_manager.py`) to open concurrent T4 sessions across `account-01..03` (staggered by `3.0s`) and distribute chapters in parallel with automatic work-stealing failover if any account disconnects or exhausts quota.
- **Orphan Process Cleanup**: Runs `pkill -9 -f 'chrome-linux64/chrome|render.mjs'` on Colab before each chapter build so hung browsers from prior attempts never block GPU/CPU resources.
- **Self-Healing Retry Loop**: Wraps upload, `exec` (`timeout=1000s` on Python `subprocess.run` wrapping `--timeout 960` on Colab CLI), and download (`timeout=180s`). On failure, forces a fresh runtime sync (`ensure_colab_render_runtime(force_sync=True)`).
- **Post-Render Freshness Verification**: Always verify `mp4.stat().st_mtime >= template.stat().st_mtime` and inspect the downloaded MP4 via `ffprobe`.
