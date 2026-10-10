# Issue ancient-humans-day-ch1 — render (Colab T4 Session Bootstrap & Full-Frame `line_boil` CPU Bottleneck)

- **Date Recorded**: 2026-10-09 06:25:00
- **Job ID**: ancient-humans-day-ch1-16x9
- **Subsystem**: render (Colab T4 / Remotion)
- **Status**: Resolved

---

## 1. Concrete Symptoms
- Triggering Command:
  ```bash
  python3 sys/exports/ancient_humans_flowkit_bundle/scripts/render_all_on_colab.py 1 --force --no-concat
  ```
- Error Messages & Observed Defects:
  1. **Expired Colab Session Upload Failure**:
     ```text
     subprocess.CalledProcessError: Command '[..., 'account_cli.py', ..., 'upload', '-s', 'video-pilot-tts', '/tmp/ch1_build.zip', '/content/ch1_build.zip']' returned non-zero exit status 1.
     [colab] No active sessions found on server.
     ```
  2. **Severe Render Slowdown (14 minutes for 64.25s video) & Frame Border Distortion**:
     - Rendering 1,928 frames (64.25s @ 30fps) stalled at `Rendering Ch1 on Colab Tesla T4 GPU...` for ~12.5 minutes (14 minutes total including bootstrap).
     - Inspecting extracted frames (`frame_22_0s.jpg`, `frame_49_0s.jpg`) revealed dashed black displacement artifacts along the top and left borders when `scale = 1.0`, wavy distortion of straight panel borders, and bloated MP4 file size (`19.65 MB` vs `11.38 MB` reference).

---

## 2. Root Cause
1. **Missing Auto-Session & Runtime Check in `render_all_on_colab.py`**:
   - When the Colab VM session (`video-pilot-tts`) timed out due to inactivity, `render_all_on_colab.py` attempted to upload `/tmp/ch1_build.zip` without first checking `sessions`, allocating a T4 instance (`new -s video-pilot-tts --gpu T4`), and verifying `/content/render-runtime/chrome-wrapper.sh`.
2. **Full-Frame `1920x1080` SVG `<feTurbulence>` + `<feDisplacementMap>` (`line_boil: true`) Under `--disable-gpu-rasterization`**:
   - On headless Colab T4, Chromium must run with `--disable-gpu-rasterization` (to prevent white tile drops).
   - Setting `"line_boil": true` on all 34 full-screen `1920x1080` raster beats in `ch1_props_template.json` forced Chromium to compute 2-octave Perlin noise (`<feTurbulence>`) and pixel displacement (`<feDisplacementMap scale={3}>`) **in CPU software across 2,073,600 pixels on every frame** across only 2 Colab vCPUs.
   - Additionally, applying `<feDisplacementMap>` to a full-bleed `1920x1080` raster image pulls out-of-bounds pixels into the top/left frame edges at `scale = 1.0` and warps straight panel dividers.
   - Note: `line_boil` is designed for cut-out stickers (`scene.layers` using lightweight CSS `boilJitter`) or selective emphasis, **never** enabled blanket-wide across all full-screen 1080p raster plates.

---

## 3. Proven Remedies
1. **Concrete Resolution Steps**:
   - **Step 1 (Self-Healing Colab T4 Bootstrap)**: Add `ensure_colab_render_runtime()` in `render_all_on_colab.py` to check `sessions`, automatically allocate `video-pilot-tts` (`--gpu T4`) when absent, and bootstrap `/content/render-runtime` (`npm ci`, Playwright Chromium, and `chrome-wrapper.sh` with all mandatory headless flags).
   - **Step 2 (Clean Staging Build Directory)**: Stage chapter builds in `/tmp/ch{N}_standalone_remotion_build` containing only `props.json`, `public/narration.wav`, and the active chapter images so old `video.mp4` or unused reference frames are never zipped and uploaded.
   - **Step 3 (Disable Blanket Full-Frame `line_boil` on 1080p Raster Plates)**: Remove `"line_boil": true` from full-frame 1080p raster beats in `ch1_props_template.json` and `ch1_blind_34_shots.json`, relying on Remotion's smooth camera transitions (`zoom_in`, `zoom_out`, `punch_in`, `pan_left`, `pan_right`, `slide_left`, `shake`, `fade`, `hold`).
   - **Step 4 (Strict Colab T4 Execution Discipline)**: Never propose or fall back to ad-hoc local CPU rendering when Colab is slow; diagnose the exact renderer/filter bottleneck on Colab first.
2. **Diff or Code Modifications**:
   - [`sys/exports/ancient_humans_flowkit_bundle/scripts/render_all_on_colab.py`](file:///home/hongphuoc6104/Desktop/flowkit-video-pipeline/sys/exports/ancient_humans_flowkit_bundle/scripts/render_all_on_colab.py)
   - [`sys/exports/ancient_humans_flowkit_bundle/templates/ch1_props_template.json`](file:///home/hongphuoc6104/Desktop/flowkit-video-pipeline/sys/exports/ancient_humans_flowkit_bundle/templates/ch1_props_template.json)
   - [`sys/exports/ancient_humans_flowkit_bundle/manifest/ch1_blind_34_shots.json`](file:///home/hongphuoc6104/Desktop/flowkit-video-pipeline/sys/exports/ancient_humans_flowkit_bundle/manifest/ch1_blind_34_shots.json)
3. **Live Verification Evidence**:
   - Rendered output: [`video/ancient-humans-day-ch1-16x9/ancient-humans-day-ch1-16x9_blind_test.mp4`](file:///home/hongphuoc6104/Desktop/flowkit-video-pipeline/video/ancient-humans-day-ch1-16x9/ancient-humans-day-ch1-16x9_blind_test.mp4) and [`video/ancient-humans-day-ch1-16x9/ancient-humans-day-ch1-16x9_r1_final.mp4`](file:///home/hongphuoc6104/Desktop/flowkit-video-pipeline/video/ancient-humans-day-ch1-16x9/ancient-humans-day-ch1-16x9_r1_final.mp4).
   - `ffprobe` verified: `1920x1080` (16:9), H.264 / AAC, `30/1` fps, `1928` frames, duration `64.27s`.
