# Colab CLI & Remote Runtime Error Recovery Matrix

This reference catalogs every error code and failure mode across `google-colab-cli`, [`sys/colab_bridge/client.py`](../../../../sys/colab_bridge/client.py), [`sys/colab_bridge/worker.py`](../../../../sys/colab_bridge/worker.py), [`sys/colab_bridge/job_worker.py`](../../../../sys/colab_bridge/job_worker.py), and [`PLAYBOOK.md`](../../../../PLAYBOOK.md), along with exact diagnostic and recovery commands.

---

## 1. CLI, Authentication & Session Allocation Errors

| Error Code / Symptom | Root Cause | Exact Recovery Action |
|---|---|---|
| `COLAB_CLI_MISSING` | `colab` binary (`google-colab-cli==0.7.4`) is not installed in `PATH` or `~/.local/bin/colab`. | Run `uv tool install google-colab-cli==0.7.4` and verify `~/.local/bin/colab --version`. |
| `COLAB_LOGIN_REQUIRED` | Missing `token.json` in `~/.config/video-pilot/colab/profiles/<account>/` or expired OAuth refresh token (`invalid_grant`). | Run `PYTHONPATH=sys python3 -m colab_bridge.accounts login <account>` (or `login-many`) in an interactive terminal and complete Google OAuth. |
| `COLAB_SESSION_NOT_FOUND` / `[colab] No active sessions found on server` (`ERR-20261009-02`) | The remote `video-pilot-tts` VM disconnected due to idle timeout, or local `sessions.json` no longer matches an active server VM. | 1. For standard jobs: run `PYTHONPATH=sys python3 -m colab_bridge reconcile --account <acc> --session video-pilot-tts`, then `start` once reconciled.<br>2. For multi-chapter renders: `ensure_colab_render_runtime()` automatically checks `sessions` and allocates `new -s video-pilot-tts --gpu T4` (failing over across `account-01..03`). |
| `COLAB_ALLOCATION_PENDING` | `allocation-<hash>.json` is already in `submitted`, `ambiguous`, or `allocated` phase. | **Never call `start` twice.** Run `PYTHONPATH=sys python3 -m colab_bridge reconcile --account <acc> --session <sess>` to inspect live server assignments first. |
| `COLAB_ASSIGNMENT_UNVERIFIED` | `assignment_probe.py` could not reach Google `userinfo` or `list_assignments()` (`network_unknown`, `refresh_required`, `capacity`). | Preserve the allocation (do not reset journal). Check network/OAuth token and re-run `reconcile`. |
| `COLAB_LOCAL_SESSION_MAPPING_MISSING` | Server has an active VM assignment (`assignment_count > 0`), but local `sessions.json` lacks the matching proxy endpoint. | Run `PYTHONPATH=sys python3 -m colab_bridge.accounts run <acc> sessions` to sync/inspect the active session or release it via the Colab web UI before reconciling. |
| `COLAB_RUNTIME_BINDING_INVALID` / `COLAB_RUNTIME_BINDING_ACCOUNT_MISMATCH` | Explicit `--account` or `--session` conflicts with the job's pinned runtime binding in `session_store.py`. | Use the exact account and session pinned to the job, or inspect `sys/.state/` session bindings. |
| `COLAB_VERIFIED_SETUP_REQUIRED` / `COLAB_SERVICE_RECHECK_REQUIRED` | Account identity is unverified in `account_budget.py`, internal budget is `0`, or session lacks confirmed T4 evidence. | Run `PYTHONPATH=sys python3 -m colab_bridge status` or `start`/`reconcile` on an authenticated account with available budget. |
| `COLAB_PROVIDER_BLOCKED` (`quota`, `429`, `503`, `captcha`, `bot`) | Google Colab rate-limited the account, exhausted T4 compute units, or returned HTTP 503. | For pinned single-job contracts: preserve owner/request and wait for cooldown. For chapter batch scripts (`render_all_on_colab.py`): allow automatic failover to `account-02` / `account-03`. |

---

## 2. Remote Execution, WebSocket & Request State Errors

| Error Code / Symptom | Root Cause | Exact Recovery Action |
|---|---|---|
| `COLAB_TIMEOUT` / Infinite `subprocess.run` Hang on `exec` (`ERR-20261010-10`) | Colab CLI WebSocket drops silently during long remote execution (e.g. chapter render), leaving the local process hung or leaving stale MP4s (`mp4_mtime < tpl_mtime`). | 1. Always pass both `--timeout <sec>` to `colab exec` AND `timeout=<sec+40>` to Python `subprocess.run`.<br>2. For pinned jobs: run `PYTHONPATH=sys python3 -m colab_bridge collect --request ... --out ... --cache ...` to check if `output.zip` finished remotely.<br>3. For chapter batch renders: `render_all_on_colab.py` kills orphan `chrome`/`render.mjs` processes and retries up to 3 times. Always verify `mp4_mtime >= template_mtime`. |
| `COLAB_EXEC_UNCONFIRMED` | Remote Python snippet exited or truncated stdout before printing the `VP_EXEC_OK_<uuid>` marker. | Inspect remote exception traceback in stdout/stderr; check if remote kernel crashed (OOM) or disconnected. |
| `COLAB_PENDING_OTHER_REQUEST` | Another request in the job cache is still in `submitted` or `ambiguous` state. | Collect or reconcile the existing pinned request first (`python3 -m colab_bridge collect ...` or `reconcile-render-failure`). Never delete `state.json` by hand. |
| `COLAB_RECOVERY_LIMIT` | `collect` was attempted $\ge 3$ times on an ambiguous request without finding `output.zip`. | Inspect the remote directory (`/content/video-pilot-tts/<id>` or `/content/video-pilot-jobs/<id>`). If `render.mjs` failed synchronously, run `reconcile-render-failure`. |
| `COLAB_FAILURE_UNVERIFIED` | `reconcile-render-failure` was called, but `render.mjs` is either still running in `/proc`, already produced `output.zip`/`*.mp4`, or did not exit with `CalledProcessError`. | If `output.zip` exists, run `collect` instead. If `active_renderers` is non-empty, wait for completion or terminate orphan processes. |

---

## 3. Hardware, TTS & Remotion Rendering Errors

| Error Code / Symptom | Root Cause | Exact Recovery Action |
|---|---|---|
| `COLAB_GPU_REQUIRED` / `COLAB_T4_NOT_CONFIRMED` | Colab allocated a CPU-only VM or non-T4 GPU. | Never fall back to CPU. Stop the non-T4 session (`python3 -m colab_bridge stop`) and allocate a fresh `--gpu T4` session on a healthy account. |
| `ValueError: Colab reference does not match current <lang> voice` | `cfg['tts_voice']` (or `cfg['en_voice']`) in `sys/config.json` does not match the `"voice"` field inside the `profile.json` pointed to by `cfg['colab_tts']['voices'][lang]` (e.g., `"tts_voice": "Minh Quân Pro"` while `colab_tts.voices.vi` points to `assets/voices/adam/profile.json` with `"voice": "Adam"`). | Align `tts_voice` and `colab_tts.voices.vi` in `sys/config.json` so both reference the same voice profile (`"Minh Quân Pro"` <-> `assets/voices/minh-quan-pro/profile.json`, or `"Adam"` <-> `assets/voices/adam/profile.json`). |
| `COLAB_GPU_OOM` | OmniVoice FP16 diffusion steps exhausted T4 VRAM even after batch halving (`4 -> 2 -> 1`). | Split overly long narration segments into shorter clause chunks (`tts_max_chars: 256`) and clear remote CUDA cache (`torch.cuda.empty_cache()`). |
| OmniVoice pronounces digits/names in English (`ERR-20261010-08`) or Edge-TTS raises `NoAudioReceived` (`ERR-20261010-06`) | Raw Vietnamese script contains digits (`0-9`), `%`, `/`, foreign names, `...`, or `—`. | Normalize all Vietnamese text through `sys/tools/vn_text_normalizer.py` before TTS synthesis. |
| Headless Chromium Crash (`TargetClosedError`, X11 bus error, white tiles) (`COLAB-HEADLESS`) | Missing `chrome-wrapper.sh` flags or missing `VP_CHROME_PATH` / `DISABLE_FROM_SURFACE=true`. | Verify `/content/render-runtime/chrome-wrapper.sh` contains `--no-sandbox`, `--disable-dev-shm-usage`, `--run-all-compositor-stages-before-draw`, `--disable-gpu-rasterization`, `--enable-gpu`, `--ignore-gpu-blocklist`. Run `pytest sys/tests/test_renderer_tile_integrity.py`. |
| 10x Render Slowdown (14m / 64s) & Dashed Black Frame Borders (`ERR-20261009-01`) | Blanket `line_boil: true` enabled on full-screen $1920 \times 1080$ raster beats under `--disable-gpu-rasterization`. | Remove `line_boil: true` from full-frame 1080p beats in `props.json` / templates; use camera transitions (`zoom_in`, `pan_left`, `shake`) and reserve `line_boil` only for cut-out stickers (`scene.layers`). |
| `STICKER_MATTE_FAILED` | `matte_sticker.py` produced an empty alpha bounding box or a sticker smaller than `40x40` px. | Inspect the source sticker image to ensure it has a clean bright background contrasting with the black stick-figure outline. |
