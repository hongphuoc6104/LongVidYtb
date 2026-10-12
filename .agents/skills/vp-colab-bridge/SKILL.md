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

4. **Remote Video Render & Sticker Matting Engine (`sys/colab_bridge/job_worker.py` & `render_all_on_colab.py`)**:
   - **Standard Contract Path (`pilot.py` -> `client.py:render` -> `job_worker.py`)**: Verifies SHA-256 input bundles (`<= 512` files, `<= 1GB`), performs remote cut-out sticker flood-fill matting (`sys/tools/matte_sticker.py`), builds `.srt` subtitles, and executes `sys/renderer/render.mjs`.
   - **Multi-Chapter Parallel Batch Path (`sys/exports/ancient_humans_bundle/scripts/render_all_on_colab.py`)**: Dispatches chapters in parallel across `account-01..03` (`--parallel 3`) or self-heals T4 sessions (`ensure_colab_render_runtime()`), stages clean chapter builds, renders 1080p MP4 chapters with WebSocket timeout protection, verifies `mp4_mtime >= template_mtime`, and concatenates final master deliverables.

---

## 2. Configuration (`sys/config.json`)

```json
{
  "schema_version": "1.0",
  "voices": {
    "vi": "assets/voices/adam/profile.json",
    "en": "assets/voices/reference-narrator/profile.json"
  },
  "tts_voice": "Adam",
  "tts_speed": 1.22,
  "en_voice": "reference-narrator",
  "en_speed": 0.92,
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

Run all `colab_bridge` module commands from `sys/` (or pass `PYTHONPATH=sys`):

```bash
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

# 4. Multi-T4 Pool Lifecycle (open, inspect, and stop multiple T4 sessions at once)
PYTHONPATH=sys python3 -m colab_bridge pool-status --probe
PYTHONPATH=sys python3 -m colab_bridge pool-start --max-workers 3
PYTHONPATH=sys python3 -m colab_bridge pool-start --accounts account-01,account-02,account-03
PYTHONPATH=sys python3 -m colab_bridge pool-stop --accounts account-01,account-02,account-03

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
2. **Mandatory Chromium Wrapper & Xvfb Virtual Framebuffer (`COLAB-HEADLESS`)**:
   - Colab T4 has no physical X11 display. Remotion and Chromium execute under `xvfb-run -a -s "-screen 0 1920x1080x24"` to unlock full GPU hardware rasterization on the Tesla T4.
   - The wrapper script `/content/render-runtime/chrome-wrapper.sh` supports dual-mode execution with `VP_CHROME_PATH` and `DISABLE_FROM_SURFACE=true`:
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
3. **No Blanket Full-Frame `line_boil: true` on 1080p Plates (`ERR-20261009-01`)**:
   - Because `--disable-gpu-rasterization` is mandatory on headless Colab T4, SVG `<feTurbulence>` + `<feDisplacementMap>` runs on 2 CPU vCPUs across $1920 \times 1080$ pixels, causing a 10x render slowdown (14m for 64s) and black dashed border teeth. Use camera transitions (`zoom_in`, `pan_left`, `shake`) for full-frame plates; reserve `line_boil` / `boilJitter` strictly for cut-out stickers (`scene.layers`).
4. **Mandatory Vietnamese Phonetic Normalization Before TTS (`ERR-20261010-08`)**:
   - Always pass Vietnamese narration through `sys/tools/vn_text_normalizer.py` before submitting to OmniVoice or Edge-TTS so digits (`0-9`), `%`, `/`, foreign names (`Richard Lee` -> `Ri-chát Li`), and ellipses (`...`, `—`) are normalized into clean Vietnamese phonetic words and standard punctuation.
5. **Hard Subprocess Timeouts, Orphan Process Cleanup & `mtime` Verification (`ERR-20261010-10`)**:
   - Always pair Colab CLI `--timeout <sec>` with a Python `subprocess.run(..., timeout=<sec+40>)` guard and 3-attempt retry loop to defeat silent WebSocket hangs.
   - Before each remote chapter render, kill orphaned processes (`pkill -9 -f 'chrome-linux64/chrome|render.mjs'`).
   - Always verify `mp4.stat().st_mtime >= template.stat().st_mtime` and inspect streams with `ffprobe` (`1920x1080` or `1080x1920`, `h264`, `aac`).
6. **Mandatory OmniVoice Boundary Silence Trimming Before Pause Insertion (`ERR-20261011-02`)**:
   - `OmniVoice.generate()` pads raw utterance tensors with `50–180ms` of leading silence and `180–420ms` of trailing silence. Always trim boundary silence (`_trim_silence` with `threshold=0.012`, `lead_ms=25`, `trail_ms=30`, `fade_ms=8`) before caching or appending inter-sentence pauses (`0.20s` short `< 8` words, `0.28s` regular, `0.48s` dramatic `[pause:800ms]`) to prevent double-padded hesitation/stutter.

---

## 5. Progressive Disclosure Reference Index

Open only the specific reference file needed for your active task or observed error symptom:

| Domain | Reference Document | When to Read |
|---|---|---|
| **CLI, Accounts & Session Lifecycle** | [cli-and-accounts.md](references/cli-and-accounts.md) | Onboarding accounts, switching profiles, understanding `account_cli.py`, `assignment_probe.py`, internal budgets vs server assignments, or multi-account failover. |
| **Remote TTS (`OmniVoice` on T4)** | [tts-omnivoice-worker.md](references/tts-omnivoice-worker.md) | Synthesizing audio via `worker.py`, configuring voice clone profiles (`adam`, `reference-narrator`), phonetic normalization, or debugging `COLAB_GPU_OOM`. |
| **Remote Video Render (`Remotion` on T4)** | [remote-remotion-render.md](references/remote-remotion-render.md) | Running `job_worker.py` or `render_all_on_colab.py`, bootstrapping `/content/render-runtime`, sticker matting, or Cue-Window Allocation. |
| **Colab CLI Error & Recovery Matrix** | [error-recovery-matrix.md](references/error-recovery-matrix.md) | Diagnosing any `ColabError` (`COLAB_SESSION_NOT_FOUND`, `COLAB_TIMEOUT`, `COLAB_ALLOCATION_PENDING`, `COLAB_PROVIDER_BLOCKED`, etc.) or WebSocket hang. |
| **System Docs & Playbook** | [colab-tts.md](../../../sys/docs/colab-tts.md) / [PLAYBOOK.md](../../../PLAYBOOK.md) | Reviewing architectural provenance and historical 6-field post-mortems. |
