---
name: vp-colab-bridge
description: "Manage Colab T4 sessions, multi-account failover, remote OmniVoice TTS synthesis, and native FFmpeg h264_nvenc video rendering."
---

# VP Colab Bridge (`sys/colab_bridge/`)

Offloads all TTS (`kjanh/KhanhTTS-OmniVoice` FP16) and video rendering (`FFmpeg h264_nvenc`) to remote Google Colab NVIDIA T4 GPUs across a multi-account pool (`ColabPoolManager` / `ColabPoolDispatcher`, 1 account = 1 T4 VM, `3.0s` staggered allocation).

## 1. Core Operational Invariants
1. **Native T4 `FFmpeg h264_nvenc` Only (`ERR-20261102-01`)**: Render via `flow_video_worker.py` / `job_worker.py` (`-c:v h264_nvenc -preset p4 -b:v 6M`, `loudnorm=I=-11.0:TP=-1.0:LRA=7.0`, `/dev/shm` parallel chunk encoding + stream-copy concat). Remotion, Chromium, TPU, and silent local CPU fallbacks are strictly forbidden.
2. **Per-Channel Studio Voice (`ERR-20261108-03`)**: Production channels use human-cloned studio profiles `VietNarrator_<channel_id>` (`sys/assets/voices/ch_<id>/profile.json`, `speed: 1.0`, range `[0.90, 1.15]`). `sys/config.json` holds the default fallback `VietNarrator`. Never fallback to Edge-TTS / `vi-VN-NamMinhNeural`.
3. **Phonetic Normalization & Clean Audio (`ERR-20261025-01`)**: Normalize Vietnamese text via `sys/tools/vn_text_normalizer.py`; strip inter-letter hyphens before OmniVoice BPE; trim boundaries (`lead_ms=25, trail_ms=30, fade_ms=8`) preserving nasal codas (`-ng/-m/-n`) and auto-retrying (`batch_size=1`) if internal silence > `380ms`.
4. **45s Watchdog & 2-Account Fail-Fast (`WATCHDOG-45S`)**: Workers running tasks >30s MUST arm `schedule(DurationSeconds=45, TimerCondition="any")` and check logs/PIDs/`state.json`. Stop multi-account failover after `2` consecutive `COLAB_EXEC_UNCONFIRMED` errors and inspect remote stderr.
5. **Mandatory Post-Job Teardown (`ERR-20261012-01`)**: After verifying outputs with `ffprobe`, run `./pipeline colab teardown` (or `ColabPoolManager().teardown_job_resources()`) unless `--keep-warm` is requested.
6. **Single-Pass 4-GPU Render Architecture (`sys/short_engine/render_single_pass.py` via `sys/tools/produce_serialized_short.py`)**:
   - **Default `--render-mode single_pass` (`<= 15 phút` E2E, `~8–12 phút` goal)**: Splits `20` beats into `4` chunks (`0` overhang), runs `slice_ass_for_window()` per chunk, and dispatches via `ColabPoolDispatcher` (`--colab-render-workers 4`) so each T4 GPU renders a **complete 2K chunk in 1 pass** (`-bf 0 -g 30 -b:v 10M -preset p4`, `flags=bicubic` + `unsharp=3:3:0.45:3:3:0.25`, `heroic_banner` `>= 132px` at `anchor_y=150`, `.ass` subtitles, watermark), then joins locally via **lossless `<2s` concat (`ffmpeg -f concat -c:v copy -c:a copy`)**.
   - **Compatibility `--render-mode two_pass`**: Optional fallback (Pass 1 chunk fan-out + Pass 2 `xfade` composite).
   - **Session Safety Guards**: Both modes MUST clean up via `pm.stop_pool(..., unassign_server=True)` (protecting user external sessions) and abort multi-account failover after `2` consecutive `COLAB_EXEC_UNCONFIRMED` errors.

## 2. Quick CLI Reference
```bash
./pipeline colab pool-status --probe          # Inspect accounts, locks, and live T4 assignments
./pipeline colab teardown                     # Unassign T4 VMs and reap CDP Chrome instances
PYTHONPATH=sys python3 -m colab_bridge.accounts list
PYTHONPATH=sys python3 -m colab_bridge.accounts select-idle render
PYTHONPATH=sys python3 -m colab_bridge pool-start --max-workers 3
PYTHONPATH=sys python3 -m colab_bridge reconcile --account account-01 --session video-pilot-tts
```

## 3. Progressive Disclosure References
- **CLI, Accounts & Session Lifecycle**: [cli-and-accounts.md](references/cli-and-accounts.md)
- **Remote TTS (`OmniVoice` on T4)**: [tts-omnivoice-worker.md](references/tts-omnivoice-worker.md)
- **Remote Video Render (`FFmpeg h264_nvenc` on T4)**: [remote-ffmpeg-nvenc-render.md](references/remote-ffmpeg-nvenc-render.md)
- **Colab Error & Recovery Matrix**: [error-recovery-matrix.md](references/error-recovery-matrix.md)
