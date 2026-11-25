# Troubleshooting Headless Display & GPU Rendering (Colab T4 NVENC & Local Flow CDP)

## 1. Native Colab Tesla T4 FFmpeg NVENC (Zero Browser Overhead)

### Status: Remotion Compositor Retired
Legacy video compositing via Remotion/Chromium/Puppeteer has been completely replaced by **Native Colab Tesla T4 `FFmpeg h264_nvenc`** (`flow_video_worker.py` via `job_worker.py` / `sys/tools/produce_vn_dual_mode.py`).

### Key Invariants
- **No Headless Browser Required for Rendering**: Rendering runs purely inside native FFmpeg leveraging the Tesla T4 NVENC chip directly (`-c:v h264_nvenc -preset p4 -b:v 6M`).
- **Surface Probe**: NVENC capability probe requires minimum surface `s=256x256` (`ffmpeg -f lavfi -i testsrc=s=256x256 -t 0.1 -c:v h264_nvenc -f null -`).
- **Parallel RAM Disk Encoding**: Chunks encode in parallel across 3 workers on `/dev/shm`, followed by `<1.0s` lossless `stream-copy` concatenation.
- **Audio Loudness**: EBU R128 loudness normalization (`loudnorm=I=-11.0:TP=-1.0`) embedded directly into FFmpeg filtergraph.

---

## 2. Local Linux GPU Headless Chrome for Flow CDP

When running Flow CDP browser automation on headless Linux environments (no X11 display server):

### Symptoms
- Chrome `--headless=new` falls back to software SwiftShader rasterization, causing 100% CPU lockups and CDP handshake drops (`hasAt=False`).
- Stray orphan Chrome processes causing port conflicts.

### Mandatory Flags
All Chrome instances launched for Flow CDP MUST include:
```bash
--headless=new \
--ozone-platform=x11 \
--disable-software-rasterizer \
--force-gpu-mem-available-mb=1843
```

### Staggered Launch & Process Cleanup
1. **Staggered Launch**: All Chrome boots must adhere to cross-process staggering (`gap >= 3.2s + 0.6s` jitter via `stagger_cross_process_action("chrome_launch")`).
2. **Clean Process Teardown**: When handshake fails or session ends, invoke `terminate_by_port(port)` to kill orphaned processes cleanly.
3. **Warm Session Preservation**: On Error 7/8 (`PUBLIC_ERROR_UNUSUAL_ACTIVITY` / `TOO_MUCH_TRAFFIC`), never kill Chrome or reload tabs; refresh reCAPTCHA in-place via `_refresh_recaptcha_session`.
