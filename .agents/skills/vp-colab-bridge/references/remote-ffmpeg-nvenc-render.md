# Remote Full-frame Video Rendering (Native Colab Tesla T4 FFmpeg h264_nvenc)

This reference covers the canonical Google Colab Tesla T4 GPU render contract through [`job_worker.py`](../../../../sys/colab_bridge/job_worker.py) and [`flow_video_worker.py`](../../../../sys/colab_bridge/flow_video_worker.py).

---

## 1. Sole Canonical Video Renderer Architecture

Video Pilot designates Native Colab Tesla T4 `FFmpeg h264_nvenc` (`flow_video_worker.py`) as the **SOLE canonical renderer**:
- **Zero Runtime Setup Overhead**: `0.0s` setup time. Unlike legacy Remotion/Node.js which required 15–30s of `npm ci` and Chromium Playwright installation, native FFmpeg is pre-installed on Colab T4.
- **Ultra-Fast Rendering Throughput**: ~`17.14s` render duration for a 52s 9:16 video (~`91.13 fps`), eliminating the severe 393s `<OffthreadVideo>` CPU/IPC bottleneck and 341s TPU CPU bottleneck.
- **Prohibited Renderers**: Remotion, Chromium/Xvfb, Playwright, TPU (`--tpu`), and local CPU FFmpeg rendering are strictly forbidden and retired.

---

## 2. Hardware Acceleration & FFmpeg NVENC Pipeline

The worker verifies Tesla T4 GPU availability via `nvidia-smi` and queries `ffmpeg -c:v h264_nvenc`:

### 2.1 Video Encoding Parameters
- **Encoder**: `-c:v h264_nvenc`
- **Preset**: `-preset p4` (high quality / high throughput balance)
- **Rate Control**: `-cq 19 -b:v 6M`
- **Pixel Format**: `-pix_fmt yuv420p`
- **Container Flags**: `-movflags +faststart`

### 2.2 Subtitles & Overlays
- **9:16 Vertical Video**: Burned-in `.srt` subtitles via FFmpeg `subtitles` filter with calibrated font size and margins (`subtitles=<path>:force_style='Fontsize=18,PrimaryColour=&H00FFFFFF'`).
- **16:9 Landscape Video**: Sidecar `.srt` files packaged alongside the MP4 for YouTube/Facebook delivery.
- **Brand Watermark**: Rounded brand logo placed in the corner with automatic fade/hide on the endcard scene.

### 2.3 Audio Mastering
- **Loudness Normalization**: EBUR128 audio filter `loudnorm=I=-11.0:TP=-1.0:LRA=7.0` matching Video Pilot voice standards (`-11.0 LUFS` / `-1.0 dBTP`).
- **Resampling**: `aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo`.

---

## 3. Execution Contracts

### Workflow: Standard Single-Job Contract (`pilot.py` / `job_worker.py`)
1. `job_protocol.py:build_render_request()` hashes the render contract, story planner, subtitles, `colab_bridge/flow_video_worker.py`, and media assets into `input.zip` (`<= 512` files, `<= 1GB`).
2. `client.py:render()` uploads `input.zip` and `job_worker.py` to `/content/video-pilot-jobs/<request_id>/` and executes `job_worker.run(...)`.
3. `job_worker.py` invokes `flow_video_worker.py:render_props_package` to compose P1 `.mp4` video clips (with `trim_before`/`playback_rate`) or P2 static image beats.
4. Every rendered MP4 is verified with `ffprobe` (`h264`, `aac`, exact dimensions `1920x1080` or `1080x1920`, duration drift `<= 0.25s`).
5. `output.zip` is assembled and downloaded, and `validate_render_result()` verifies hashes and metadata on the host.
