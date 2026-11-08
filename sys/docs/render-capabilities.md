# Video Pilot — Native Colab Tesla T4 FFmpeg NVENC Rendering Capabilities

> **SSOT**: Colab Tesla T4 Native GPU FFmpeg `h264_nvenc` is the authoritative video rendering engine of Video Pilot (replacing legacy Remotion/Chromium/CPU compositors).
> Execution is orchestrated via `sys/colab_bridge/flow_video_worker.py` and `sys/tools/produce_vn_dual_mode.py`.

---

## 1. Core Hardware & Codec Invariants

| Parameter | Specification | Purpose / Implementation |
|---|---|---|
| **GPU Encoder** | `-c:v h264_nvenc` | Hardware accelerated H.264 encode on Tesla T4 (`0.0s` startup overhead vs 300s+ Remotion). |
| **Preset & Bitrate** | `-preset p4 -b:v 6M` | Balanced NVENC preset p4, target video bitrate `6.0 Mbps` ensuring broadcast-grade sharpness. |
| **Audio Normalization** | `-af loudnorm=I=-11.0:TP=-1.0` | EBU R128 loudness normalization to `-11.0 LUFS` with `-1.0 dBTP` true peak limit. |
| **RAM Disk Encoding** | `/dev/shm` multi-worker | Parallel encoding of video chunks across 3 workers directly on `/dev/shm` RAM disk. |
| **Lossless Concatenation** | `<1.0s` `stream-copy` | Lossless concatenation (`-c copy`) of encoded chunk segments via FFmpeg concat demuxer. |

---

## 2. Dual-Format Delivery Profiles

### A. Short-Form (`short_9x16`, 1080x1920, 48–60s)
- **Engine**: 100% Full-Chain Video Generation (`Omni 1.2 Flash` continuous clips).
- **Stitching**: `trim=start_frame=1` zero-stutter frame blending.
- **Subtitles**: Kinetic 1-word `.ass` subtitles:
  - Font: Bold sans-serif (`MarginV=400`, `Outline=6`).
  - Palette: Alternating Red `#FF3B30` and Yellow `#FFE600` active word highlights.
- **Delivery**: Burned-in `.ass`/`.srt` video deliverable.

### B. Long-Form (`long_16x9`, 1920x1080, 8m30s–13m)
- **Engine**: High-Density Multi-Image (`240–350` `BELUGA` 8K frames: `~100–120` Base Anchors + `~140–230` 1-hop Progressive States).
- **Camera Dynamics**:
  - `1.25x` supersampled canvas (`2400x1350`).
  - Analytical zero-snap `zoompan`: continuous smooth function `z='1.06-0.06*(on/N)'` dependent strictly on `on/N` (prohibiting recursive state variables).
- **Transitions**: Directional `xfade` optical transitions (`0.24s` duration; `smoothleft`, `smoothright`, `smoothup`, `smoothdown`, `fade`).
- **Subtitles & Chapters**:
  - Sidecar `.srt` matching exact spoken cadence.
  - `8–12` YouTube Chapters embedded via `FFMETADATA1`.

---

## 3. Pacing Modes & Timing Contracts

Visual beats strictly conform to `sys/visual_pacing.py`:
- **Rapid**: `1.2–2.0s` hold (intense narrative conflict).
- **Normal**: `2.2–3.2s` hold (standard explanatory progression).
- **Slow**: `3.5–4.8s` hold (conceptual synthesis).
- **Hold**: `5.0–6.5s` hold (reflection, key takeaways).

---

## 4. Operational Commands

```bash
# Verify local render pipeline & schema
pytest sys/tests/test_colab_bridge_skill.py sys/tests/test_vn_dual_mode_pipeline.py -v

# Production rendering via Colab dispatcher
python3 sys/tools/produce_vn_dual_mode.py --mode build-short
python3 sys/tools/produce_vn_dual_mode.py --mode build-long
```
