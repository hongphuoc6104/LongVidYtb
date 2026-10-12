# Colab CLI, Multi-Account Store, Smart Selection & Parallel T4 Pool Lifecycle

This reference covers the architecture and operational workflow of [`sys/colab_bridge/accounts.py`](../../../../sys/colab_bridge/accounts.py), [`sys/colab_bridge/account_cli.py`](../../../../sys/colab_bridge/account_cli.py), [`sys/colab_bridge/pool_manager.py`](../../../../sys/colab_bridge/pool_manager.py), [`sys/colab_bridge/assignment_probe.py`](../../../../sys/colab_bridge/assignment_probe.py), and [`sys/colab_bridge/client.py`](../../../../sys/colab_bridge/client.py).

---

## 1. Prerequisites & CLI Binary

Video Pilot uses the official `google-colab-cli==0.7.4` installed via `uv tool install`:

```bash
uv tool install google-colab-cli==0.7.4
```

- Binary lookup: `shutil.which('colab')` or `~/.local/bin/colab`.
- Underlying Python interpreter used by process-local wrappers: `~/.local/share/uv/tools/google-colab-cli/bin/python`.
- Never invoke `colab auth` on the host machine (`colab auth` is only for service authentication inside a Colab VM; host authentication always uses `--auth oauth2`).

---

## 2. Multi-Account Isolated Store & Lifecycle Management (`~/.config/video-pilot/colab`)

To support multiple Google accounts simultaneously without modifying the global `~/.config/colab-cli/` directory or leaking credentials into Git:

- **Registry File**: `~/.config/video-pilot/colab/accounts.json` (`0600` permissions) tracks `preferred` account and `accounts: [{"id": "account-01", "enabled": true, "role": "any"}, ...]`.
- **Profile Directories**: `~/.config/video-pilot/colab/profiles/<account-id>/` (`0700` permissions) stores:
  - `token.json` (`0600`): OAuth2 refresh/access credentials for that specific Google account.
  - `sessions.json` (`0600`): Local mapping of session names (e.g. `video-pilot-tts`) to active Colab proxy endpoints.
  - `history`: Process-local CLI command log.
- **Process-Local Wrapper ([`account_cli.py`](../../../../sys/colab_bridge/account_cli.py))**:
  - Dynamically binds `colab_cli.auth.TOKEN_CONFIG_PATH`, `state._history`, and `--config <profile>/sessions.json` in memory before invoking `colab_cli.cli.main()`.
  - Rejects manual overrides (`--config`, `--auth`, `--client-oauth-config`, `-c`) to guarantee strict profile isolation.

### Account Management & Selection Commands

Run from `sys/` (or with `PYTHONPATH=sys`):

```bash
# List all accounts, preferred selection, roles, token presence, and busy lock state
PYTHONPATH=sys python3 -m colab_bridge.accounts list

# Inspect all accounts with local sessions and live Google server assignment probe
PYTHONPATH=sys python3 -m colab_bridge.accounts status-all --probe

# Interactive multi-account OAuth onboarding (creates account-01, account-02, ...)
PYTHONPATH=sys python3 -m colab_bridge.accounts login-many

# Re-authenticate a specific existing or new account ID
PYTHONPATH=sys python3 -m colab_bridge.accounts login account-02

# Import an existing ~/.config/colab-cli token into a named profile
PYTHONPATH=sys python3 -m colab_bridge.accounts import-current account-01

# Set preferred default account
PYTHONPATH=sys python3 -m colab_bridge.accounts prefer account-01

# Enable or disable an account in the pool
PYTHONPATH=sys python3 -m colab_bridge.accounts enable account-02
PYTHONPATH=sys python3 -m colab_bridge.accounts disable account-03

# Assign a workload role ('any' [default], 'tts', or 'render')
PYTHONPATH=sys python3 -m colab_bridge.accounts role account-01 tts
PYTHONPATH=sys python3 -m colab_bridge.accounts role account-02 render
PYTHONPATH=sys python3 -m colab_bridge.accounts role account-02 any

# Remove an account from registry (pass --purge to also delete its profile folder)
PYTHONPATH=sys python3 -m colab_bridge.accounts remove account-04

# Select an idle account not locked by another process (optionally filtered by role)
PYTHONPATH=sys python3 -m colab_bridge.accounts select-idle
PYTHONPATH=sys python3 -m colab_bridge.accounts select-idle render

# List all ready accounts in the parallel T4 pool
PYTHONPATH=sys python3 -m colab_bridge.accounts pool

# Run any raw colab-cli subcommand under a specific account profile
PYTHONPATH=sys python3 -m colab_bridge.accounts run account-01 sessions
PYTHONPATH=sys python3 -m colab_bridge.accounts run account-01 new -s video-pilot-tts --gpu T4
```

### Account Selection Strategies (`accounts.select()`)
1. **Explicit (`--account account-02`)**: Targets that exact account profile.
2. **Preferred (`--account auto`)**: Selects the `preferred` account first, falling back to the next enabled authenticated account.
3. **Idle-Aware (`--account auto-idle` or `prefer_idle=True`)**: Checks `~/.cache/video-pilot-colab/<hash>.lock` via non-blocking `fcntl.flock` (`is_session_busy()`) and automatically selects an authenticated account whose T4 session is **not** currently executing another process.
4. **Role-Filtered (`role='tts' | 'render' | 'any'`)**: Matches accounts with `role == 'any'` (flexible default) or the requested specialized role, prioritizing exact role matches first.

---

## 3. Multi-Account Parallel T4 Pool (`pool_manager.py`)

Because Google Colab Free allows **1 GPU T4 VM per Google account**, [`sys/colab_bridge/pool_manager.py`](../../../../sys/colab_bridge/pool_manager.py) (`ColabPoolManager` & `ColabPoolDispatcher`) coordinates $N$ Google accounts to run $N$ concurrent T4 sessions simultaneously (`max_concurrency=3` by default, expandable via `--max-workers N`):

```bash
# Check status of all workers in the Multi-T4 Pool
PYTHONPATH=sys python3 -m colab_bridge pool-status --probe

# Start T4 sessions across up to 3 accounts concurrently (with 3.0s staggered allocation)
PYTHONPATH=sys python3 -m colab_bridge pool-start --max-workers 3
PYTHONPATH=sys python3 -m colab_bridge pool-start --accounts account-01,account-02,account-03

# Stop all active T4 sessions across the pool after work completes
PYTHONPATH=sys python3 -m colab_bridge pool-stop
```

### Key Safeguards in `ColabPoolManager` & `ColabPoolDispatcher`
- **Staggered Allocation (`stagger_seconds=3.0`)**: Serializes `new -s video-pilot-tts --gpu T4` calls with a 3-second gap so multiple accounts on the same IP never trigger Google rate limits or Captcha.
- **Role-Aware & Idle-Aware Worker Acquisition**: `acquire_healthy_worker(role=...)` skips any account that is `BUSY`, in `COOLDOWN`, `BLOCKED` (`quota`, `429`, `503`, `captcha`), or locked by an external process (`external_lock_busy`).
- **Work-Stealing Failover**: `ColabPoolDispatcher.dispatch_all()` runs tasks across `ThreadPoolExecutor(max_workers=max_concurrency)`. If one account disconnects or hits a T4 quota limit mid-run, only the failed task is re-queued onto another healthy T4 account in the pool while the remaining accounts continue uninterrupted.

---

## 4. Single-Session Allocation, Verification & Reconciliation

### 4.1. Starting & Confirming a T4 Session (`start` & `setup`)
1. `PYTHONPATH=sys python3 -m colab_bridge start --account account-01 --session video-pilot-tts`:
   - Acquires an exclusive lock on the account's allocation journal (`allocation-<identity_hash>.json.lock`).
   - Refuses to allocate if a prior allocation is still in `submitted`, `ambiguous`, or `allocated` state (`COLAB_ALLOCATION_PENDING`).
   - Calls `colab new -s video-pilot-tts --gpu T4` (timeout 120s).
   - Executes `nvidia-smi --query-gpu=name --format=csv,noheader` inside the remote kernel and verifies `'T4'` is present (`COLAB_T4_NOT_CONFIRMED` if not).
   - Checks if `omnivoice` and `soundfile` are importable; if not, automatically runs `setup()` (`pip install omnivoice==0.2.1 soundfile==0.13.1`).
2. Every remote `exec` appends a unique verification marker (`VP_EXEC_OK_<uuid>`) and verifies that the marker appears in `stdout` (`COLAB_EXEC_UNCONFIRMED` if missing).

### 4.2. Read-Only Server Assignment Probe ([`assignment_probe.py`](../../../../sys/colab_bridge/assignment_probe.py))
Because a local `sessions.json` file can become stale or missing while a server VM is still consuming T4 quota (or vice versa):
- `assignment_probe.py` uses `google.oauth2.credentials.Credentials` and `colab_cli.common.Client(Prod(), session).list_assignments()` to query Google's live assignment servers directly.
- Returns sanitized JSON (`verified`, `identity`, `assignment_count`, `local_session_present`, `named_assignment_active`) without ever printing email addresses, proxy tokens, or endpoints.

### 4.3. Reconciling Uncertain Allocations (`reconcile`)
If `start` times out or returns an uncertain state:
- **Never** run `start` a second time blindly.
- Run `PYTHONPATH=sys python3 -m colab_bridge reconcile --account account-01 --session video-pilot-tts`:
  - If the server reports `verified: True` and `assignment_count == 0`, the allocation journal is cleanly marked `released` and the internal budget ledger is freed.
  - If `assignment_count > 0` and `named_assignment_active: True`, it verifies `nvidia-smi` for T4 and marks the session `allocated`.
  - If network or auth is down (`verified: False`), it preserves the allocation as `uncertain` so no orphan VM is leaked.

