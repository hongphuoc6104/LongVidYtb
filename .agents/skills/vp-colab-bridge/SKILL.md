---
name: vp-colab-bridge
description: "Manage Colab T4 sessions, multi-account failover, remote OmniVoice TTS synthesis, and headless Remotion video rendering."
---

# VP Colab Bridge — Remote GPU TTS & Video Rendering Skill

`vp-colab-bridge` is the authoritative Single-Source-of-Truth (SSOT) operational skill for managing Google Colab NVIDIA T4 GPU sessions, multi-account OAuth profiles, remote `OmniVoice` voice-clone audio synthesis, and headless `Remotion` video rendering across the Video Pilot pipeline (`sys/colab_bridge/`).

---

## 1. Architecture & Multi-T4 Execution Paths

Video Pilot offloads all heavy GPU/CPU media processing to remote Google Colab T4 instances while keeping the local machine strictly as an orchestrator, session manager, and asset collector:

1. **Multi-Account Isolated Profile Store & Smart Selection (`sys/colab_bridge/accounts.py` & `account_cli.py`)**:
   - Stores isolated OAuth tokens (`token.json`), session maps (`sessions.json`), workload roles (`any`, `tts`, `render`), and CLI history per account under `~/.config/video-pilot/colab/profiles/account-NN/` (`0700` dir / `0600` file permissions).
   - Binds `google-colab-cli==0.7.4` in-memory per process via `account_cli.py` without mutating `$HOME` or global packages.
   - Supports explicit account selection (`account-02`), default preferred selection (`auto`), idle-aware selection (`auto-idle` — skips any account whose session lock `~/.cache/video-pilot-colab/<hash>.lock` is held by another active process), and workload role filtering (`tts` vs `render`).
   - Probes live Google server assignments via `assignment_probe.py` (`userinfo` + `list_assignments()`) without leaking credentials.

2. **Multi-Account Parallel T4 Pool Manager (`sys/colab_bridge/pool_manager.py`)**:
   - Manages multiple Google Colab accounts simultaneously (**1 Google Account = 1 dedicated NVIDIA T4 GPU VM**) via `ColabPoolManager` and `ColabPoolDispatcher`.
   - Performs staggered T4 session allocation (`3.0s` minimum interval between `new --gpu T4` calls) to prevent IP rate-limiting or Captcha challenges.
   - Dispatches multi-chapter renders or concurrent TTS + Video Render workloads across up to $N$ active T4 sessions in parallel with automatic work-stealing failover if any account disconnects or exhausts quota.

3. **Remote Audio Synthesis Engine (`sys/colab_bridge/worker.py` & `protocol.py`)**:
   - Runs `kjanh/KhanhTTS-OmniVoice` (`omnivoice==0.2.1`, FP16, `cuda:0`) on a real NVIDIA T4 GPU.
   - Retains loaded model weights (`_MODEL`) and voice-clone prompts (`_PROMPTS`) inside the persistent Jupyter kernel across jobs.
   - Outputs measured `48kHz` mono PCM16 WAVs with dynamic batch OOM halving (`4 -> 2 -> 1`).

4. **Remote Full-frame Video Render (`sys/colab_bridge/job_worker.py` & `render_all_on_colab.py`)**:
   - **Standard Contract Path (`pilot.py` -> `client.py:render` -> `job_worker.py`)**: Verifies SHA-256 input bundles (`<= 512` files, `<= 1GB`), copies full-frame scene images, builds `.srt` subtitles, and executes `sys/renderer/render.mjs`. Layered content is rejected before upload; the render worker does not load `matte_sticker.py`.
   - Multi-output requests use the same contract. The orchestrator handles T4 session selection and output collection; there is no separate export-specific rendering path in the standard workflow.

---

## 2. Configuration (`sys/config.json`)

```json
{
  "schema_version": "1.0",
  "voices": {
    "vi": "assets/voices/viet_narrator/profile.json",
    "en": "assets/voices/viet_narrator/profile.json"
  },
  "tts_voice": "VietNarrator",
  "tts_speed": 1.0,
  "en_voice": "VietNarrator",
  "en_speed": 1.0,
  "colab_tts": {
    "enabled": true,
    "parallel_images": true,
    "session": "video-pilot-tts",
    "batch_size": 4,
    "num_step": 32,
    "timeout_seconds": 1800,
    "models": {
      "vi": {
        "id": "kjanh/KhanhTTS-OmniVoice",
        "revision": "20d056b8ea5d8d578b4cbaf1f703012fa3798a84"
      },
      "en": {
        "id": "kjanh/KhanhTTS-OmniVoice",
        "revision": "20d056b8ea5d8d578b4cbaf1f703012fa3798a84"
      }
    },
    "account": "auto",
    "render_estimate_seconds": 60
  }
}
```
*(Tip: Set `"account": "auto-idle"` or pass `--account auto-idle` when launching concurrent CLI jobs so each job automatically claims an idle account instead of waiting on `preferred`.)*

---

## 3. Core CLI Commands, Account Management & Multi-T4 Pool Lifecycle

Run all `colab_bridge` module commands via `./pipeline colab <subcommand>` from the repo root, or from `sys/` (with `PYTHONPATH=sys`):

```bash
# Quick conveyor wrapper from repo root:
./pipeline colab pool-status --probe
./pipeline colab teardown

# 1. Inspect configured accounts, busy locks, roles, and live server assignments
PYTHONPATH=sys python3 -m colab_bridge.accounts list
PYTHONPATH=sys python3 -m colab_bridge.accounts status-all --probe

# 2. Onboard and manage multiple Google accounts (enable/disable/role/prefer/remove)
PYTHONPATH=sys python3 -m colab_bridge.accounts login-many
PYTHONPATH=sys python3 -m colab_bridge.accounts login account-02
PYTHONPATH=sys python3 -m colab_bridge.accounts prefer account-01
PYTHONPATH=sys python3 -m colab_bridge.accounts enable account-02
PYTHONPATH=sys python3 -m colab_bridge.accounts disable account-03
PYTHONPATH=sys python3 -m colab_bridge.accounts role account-01 tts
PYTHONPATH=sys python3 -m colab_bridge.accounts role account-02 render

# 3. Smart Account Selection (pick an idle account or list ready pool accounts)
PYTHONPATH=sys python3 -m colab_bridge.accounts select-idle
PYTHONPATH=sys python3 -m colab_bridge.accounts select-idle render
PYTHONPATH=sys python3 -m colab_bridge.accounts pool

# 4. Multi-T4 Pool Lifecycle (open, inspect, stop, and full post-job teardown)
PYTHONPATH=sys python3 -m colab_bridge pool-status --probe
PYTHONPATH=sys python3 -m colab_bridge pool-start --max-workers 3
PYTHONPATH=sys python3 -m colab_bridge pool-start --accounts account-01,account-02,account-03
PYTHONPATH=sys python3 -m colab_bridge pool-stop --accounts account-01,account-02,account-03
PYTHONPATH=sys python3 -m colab_bridge teardown

# 5. Single-Account T4 Session Lifecycle (explicit or auto-idle)
PYTHONPATH=sys python3 -m colab_bridge.accounts run account-01 sessions
PYTHONPATH=sys python3 -m colab_bridge start --account account-01 --session video-pilot-tts
PYTHONPATH=sys python3 -m colab_bridge setup --account account-01 --session video-pilot-tts
PYTHONPATH=sys python3 -m colab_bridge status --account account-01 --session video-pilot-tts

# 6. Reconcile an ambiguous allocation (NEVER call start twice on an uncertain state)
PYTHONPATH=sys python3 -m colab_bridge reconcile --account account-01 --session video-pilot-tts

# 7. Collect a previously submitted TTS/render request on its pinned owner
PYTHONPATH=sys python3 -m colab_bridge collect --request req.json --out out_dir --cache cache_dir

# 8. Reconcile a proven synchronous remote render failure
PYTHONPATH=sys python3 -m colab_bridge reconcile-render-failure --request req.json --cache cache_dir --source "reason"

# 9. Release a single T4 GPU VM after all durable outputs are collected
PYTHONPATH=sys python3 -m colab_bridge stop --account account-01 --session video-pilot-tts
```

---

## 4. Mandatory Operational Invariants (Golden Rules)

1. **Self-Healing Session Liveness (`ERR-20261009-02`)**:
   - Never assume `video-pilot-tts` is still alive before uploading bundles. Always check `sessions` first; if expired (`No active sessions found on server`), allocate a new `--gpu T4` session (failing over across `account-01..03` if needed) and verify `/content/render-runtime/chrome-wrapper.sh` exists.
2. **Mandatory Chromium Wrapper & Safe Headless Render (`COLAB-HEADLESS` / `ERR-20261011-05` / `ERR-20261011-06`)**:
   - Colab T4 lacks physical X11 display. Remotion and Chromium execute via runtime `chrome-wrapper.sh` (`VP_CHROME_PATH`, `DISABLE_FROM_SURFACE=true`) with mandatory flags (`--no-sandbox`, `--disable-dev-shm-usage`, `--run-all-compositor-stages-before-draw`, `--disable-checker-imaging`, `--disable-new-content-rendering-timeout`), registering `/usr/share/glvnd/egl_vendor.d/10_nvidia.json` (`/usr/lib64-nvidia/libEGL_nvidia.so.0`) with `--use-gl=angle --use-angle=gl-egl --enable-gpu-rasterization --ignore-gpu-blocklist` (or falling back to `--disable-gpu-rasterization` when NVIDIA EGL is absent).
   - **Prohibit `xvfb-run` & `--use-angle=gl`**: `Xvfb` is a CPU software framebuffer; forcing Desktop GL (`--use-angle=gl`) over Xvfb causes socket deadlocks (>300s timeout). Always unset `DISPLAY` (`env.pop('DISPLAY', None)`) before running `node render.mjs`.
   - **Hardware Acceleration via NVENC & Sync Image Decoding**: Configure `videoBitrate: '6M'` and `gl: 'angle-egl'` in `sys/renderer/render.mjs` to activate `h264_nvenc`, and enforce `<Img decoding="sync">` in `sys/renderer/index.tsx`. Full wrapper specification in [remote-remotion-render.md](references/remote-remotion-render.md).
3. **No Blanket Full-Frame `line_boil: true` on 1080p Plates (`ERR-20261009-01`)**:
   - Full-screen SVG `<feTurbulence>` + `<feDisplacementMap>` across $1920 \times 1080$ pixels causes a 10x render slowdown and black dashed border teeth. Use camera transitions (`zoom_in`, `pan_left`, `shake`) for full-frame scene images and keep Film Grain opt-in (`enable_film_grain: true`).
4. **Mandatory Vietnamese Phonetic Normalization Before TTS (`ERR-20261010-08`)**:
   - Always pass Vietnamese narration through `sys/tools/vn_text_normalizer.py` before submitting to `OmniVoice` so digits (`0-9`), `%`, `/`, foreign names (`Richard Lee` -> `Ri-chát Li`), and ellipses (`...`, `—`) are normalized into clean Vietnamese phonetic words and standard punctuation.
5. **Hard Subprocess Timeouts, Orphan Process Cleanup & `mtime` Verification (`ERR-20261010-10`)**:
   - Always pair Colab CLI `--timeout <sec>` with a Python `subprocess.run(..., timeout=<sec+40>)` guard and 3-attempt retry loop to defeat silent WebSocket hangs.
   - Before each remote chapter render, kill orphaned processes (`pkill -9 -f 'chrome-linux64/chrome|render.mjs'`).
   - Always verify `mp4.stat().st_mtime >= template.stat().st_mtime` and inspect streams with `ffprobe` (`1920x1080` or `1080x1920`, `h264`, `aac`).
6. **Mandatory OmniVoice Boundary Silence Trimming Before Pause Insertion (`ERR-20261011-02`)**:
   - Trim boundary silence with `_trim_silence(threshold=0.012, lead_ms=25, trail_ms=30, fade_ms=8)` before caching/assembly.
   - Explicit-output `format_v1` jobs use `format_profiles.py` via `narration_pauses.py`: short/normal sentence gaps 0.16/0.22 s (short) or 0.20/0.28 s (long), shorter SC01 gaps, scene tails 0.30/0.40 s and final tails 0.15/0.25 s. Exact explicit tags override defaults; never remap 900 ms to 480 ms. Legacy jobs retain old timing. See [pause plan](../../../sys/docs/narration-pause-implementation-plan.md).
7. **Mandatory Post-Job Colab T4 Unassignment & Chrome CDP Teardown (`ERR-20261012-01`)**:
   - Once all durable outputs (MP4 + SRT) of a job are collected and verified via `ffprobe`, immediately execute `ColabPoolManager().teardown_job_resources()` (`PYTHONPATH=sys python3 -m colab_bridge teardown` or automatic `release_job_resources()`), unless `--keep-warm` is explicitly requested.
   - This reconciles both `~/.config/video-pilot/colab/profiles/<acc>/sessions.json` and `/tmp/vp_colab_profiles/<acc>/sessions.json`, calls `client.unassign(endpoint)` directly on the Google Colab server to stop idle T4 quota drain, and terminates isolated Chrome CDP instances (`google-chrome-cdp-p1..p3`) to free ~5GB of local RAM.

---

## 5. Progressive Disclosure Reference Index

Open only the specific reference file needed for your active task or observed error symptom:

| Domain | Reference Document | When to Read |
|---|---|---|
| **CLI, Accounts & Session Lifecycle** | [cli-and-accounts.md](references/cli-and-accounts.md) | Onboarding accounts, switching profiles, understanding `account_cli.py`, `assignment_probe.py`, internal budgets vs server assignments, or multi-account failover. |
| **Remote TTS (`OmniVoice` on T4)** | [tts-omnivoice-worker.md](references/tts-omnivoice-worker.md) | Synthesizing audio via `worker.py`, configuring canonical voice profile (`viet_narrator`), phonetic normalization, or debugging `COLAB_GPU_OOM`. |
| **Remote Video Render (`Remotion` on T4)** | [remote-remotion-render.md](references/remote-remotion-render.md) | Running `job_worker.py` or `render_all_on_colab.py`, bootstrapping `/content/render-runtime`, full-frame image timelines, or Cue-Window Allocation. |
| **Colab CLI Error & Recovery Matrix** | [error-recovery-matrix.md](references/error-recovery-matrix.md) | Diagnosing any `ColabError` (`COLAB_SESSION_NOT_FOUND`, `COLAB_TIMEOUT`, `COLAB_ALLOCATION_PENDING`, `COLAB_PROVIDER_BLOCKED`, etc.) or WebSocket hang. |
| **System Docs & Playbook** | [colab-tts.md](../../../sys/docs/colab-tts.md) / [PLAYBOOK.md](../../../PLAYBOOK.md) | Reviewing architectural provenance and historical 6-field post-mortems. |
