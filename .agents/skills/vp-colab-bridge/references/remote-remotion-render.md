# Remote Video Rendering & Sticker Matting (`Remotion` on Colab T4)

This reference covers remote video rendering on Google Colab T4 via both the standard job worker ([`sys/colab_bridge/job_worker.py`](../../../../sys/colab_bridge/job_worker.py) & [`sys/colab_bridge/job_protocol.py`](../../../../sys/colab_bridge/job_protocol.py)) and the multi-chapter batch orchestrator ([`render_all_on_colab.py`](../../../../sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py)).

---

## 1. Mandatory Headless Chromium Wrapper (`chrome-wrapper.sh`)

Google Colab T4 VMs are headless Linux containers without an X11 display server and with constrained `/dev/shm` shared memory. Furthermore, Remotion's `openBrowser` drops custom flags passed via Node options.

### Mandatory Wrapper Configuration & Xvfb Virtual Framebuffer
Every Colab render runtime (`/content/render-runtime` or `/content/render-runtime-<lock_hash>`) resolves Playwright's Chromium binary and wraps it in `chrome-wrapper.sh` (`chmod 0755`) supporting both Xvfb GPU Hardware Acceleration and safe headless fallback:

```bash
#!/usr/bin/env bash
if [ -n "$DISPLAY" ]; then
  exec "${chrome_path}" \
    --no-sandbox \
    --disable-dev-shm-usage \
    --run-all-compositor-stages-before-draw \
    --enable-gpu-rasterization \
    --enable-zero-copy \
    --enable-gpu \
    --ignore-gpu-blocklist \
    --use-gl=angle \
    --use-angle=gl \
    "$@"
else
  exec "${chrome_path}" \
    --no-sandbox \
    --disable-dev-shm-usage \
    --run-all-compositor-stages-before-draw \
    --disable-gpu-rasterization \
    --enable-gpu \
    --ignore-gpu-blocklist \
    "$@"
fi
```

And invoke Remotion through `xvfb-run` with these environment variables:

```python
env = dict(
    os.environ,
    VP_CHROME_PATH="/content/render-runtime/chrome-wrapper.sh",
    DISABLE_FROM_SURFACE="true",
)
cmd = (['xvfb-run', '-a', '-s', '-screen 0 1920x1080x24'] if shutil.which('xvfb-run') else []) + [
    'node', 'renderer/render.mjs', str(job_dir)
]
subprocess.run(cmd, env=env, check=True)
```

### Why Each Flag Is Mandatory
- `xvfb-run -a -s "-screen 0 1920x1080x24"`: Creates an active 1080p 24bpp virtual X11 display context so Chromium can bind to NVIDIA OpenGL/EGL hardware drivers.
- `--no-sandbox`: Required inside containerized Colab root user environments.
- `--disable-dev-shm-usage`: Forces Chromium IPC buffers into `/tmp` instead of `/dev/shm`, preventing sudden `TargetClosedError` OOM kills on 1080p renders.
- `--run-all-compositor-stages-before-draw` + `DISABLE_FROM_SURFACE=true`: Forces Chromium to finish all compositor stages before frame readback, eliminating white rectangular tile drops.
- `--enable-gpu-rasterization` (under `$DISPLAY`): Delivers 35–50+ fps render speed by offloading 2D rasterization to the Tesla T4 GPU.
- `--disable-gpu-rasterization` (fallback without display): Prevents asymmetric hybrid GPU raster tile corruption on pure headless mode without X11.

---

## 2. Visual Effect & Performance Invariants on Colab T4

### 2.1. Never Enable Blanket Full-Frame `line_boil: true` on 1080p Raster Plates (`ERR-20261009-01`)
- Because `--disable-gpu-rasterization` is active on headless Colab T4, setting `"line_boil": true` on full-screen $1920 \times 1080$ raster beats forces Chromium to evaluate 2-octave SVG `<feTurbulence>` and `<feDisplacementMap scale={3}>` in **CPU software across 2,073,600 pixels per frame** on only 2 vCPUs.
- **Consequences**: 10x render slowdown (~14 minutes for a 64s chapter), bloated MP4 bitrate, and black dashed displacement artifacts along top/left borders at `scale = 1.0`.
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
