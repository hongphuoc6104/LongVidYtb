# Local Management Dashboard

Run from `sys/`. Bootstrap uses the Python standard library, without needing to import Pilot:

```sh
python3 scripts/bootstrap.py plan
python3 scripts/bootstrap.py check
python3 scripts/bootstrap.py apply --install
.venv-management/bin/python -m dashboard.server --port 8765
```

Open `http://127.0.0.1:8765`. The server binds exclusively to loopback. If you already have another management Python environment, use `python3 -m dashboard.server --python /path/to/python`. `resume --install` continues setup; it does not run production, OAuth, GPU allocation, or generation. Bootstrap creates its own venv without requiring ensurepip; installs pinned management dependencies using existing uv/pip or Python's ensurepip. It does not install models or renderers locally.

Eight tabs read live job, checkpoint, revision, artifact, and event data. The official CLI handles stop/run/resume/mode/approve/reject; the engine retains authority and ownership. The API never writes SQLite or fakes decisions. Artifacts must reside in the manifest and within the job directory; it never serves symlinks escaping the job or arbitrary paths. WAV/images/MP4 serve collected files, with video byte-range support. JSON and text responses filter sensitive credentials; GET requests have no write permissions. All POST requests require a loopback Host, same-origin server, CSRF token, and valid JSON.

The Accounts tab inventories Linux browser metadata and Colab profiles; without probing, auth and capabilities remain `not_tested`. Choosing a pool or default does not reassign the owner of an in-flight request. "Bind Google Identity" records hashed email mappings based on verbatim user confirmation (source `user_confirmed`), not treated as live authentication. "Read-only Auth Check" uses the installed Colab CLI runtime, existing valid tokens, Google userinfo, and `Client.list_assignments`; it never refreshes tokens, initiates OAuth, syncs or deletes sessions, or allocates GPUs. Expired tokens hand off OAuth to the user via terminal. Never surface tokens, authorization codes, or cookies on the UI.

The default budget ledger is shared via chat/checkout: `~/.config/video-pilot/management`. Allocated T4 runtime accounts for idle time, 5 hours active usage, and 1 hour contingency; 24 hours is an internal rolling window, not a guaranteed Google quota. The ledger aliases by Google identity to prevent resetting counters when changing profiles. Submitted/unknown Flow requests continue holding slots. Ambiguous GPU allocations are displayed distinctly, never assumed to be confirmed T4; reconcile against exact accounts and sessions before executing new operations. Resources, auth, budgets, and artifact quality remain strictly decoupled states.

Isolated tests: `tests.test_dashboard`, `tests.test_dashboard_engine`, `tests.test_account_management`, `tests.test_account_probe`. `tests.test_dashboard_browser` launches Chromium when Node and Playwright are present; set `VP_PLAYWRIGHT_MODULE` to the installed module path, never downloading browsers automatically. Browser tests use WAV/PNG and engine fixtures, not proving voice, Flow, T4, or production MP4 outputs.

## In-Dashboard Setup

The Accounts tab features fields to select active setup/development grants with verbatim instructions. Flow plans, applies configurations, and opens the exact runtime profile configured via `profile_setup`; source Chrome profiles require dedicated user profiles or CDP, without copying cookies. The Accounts and Colab tabs permit exact runtime selection, on-demand T4 provisioning, remote environment preparation, reconciling original runtimes, collecting original requests, and tearing down dedicated runtimes. These are real operational service actions triggered upon user button clicks; inventory/check commands never execute these automatically.

The Setup API validates roles and path scopes prior to assigning work. Long-running tasks run asynchronously, maintaining locks keyed by canonical Google identity across controllers. Colab account and session IDs must match adapters and original allocation/request journals; collect only accepts job and request IDs to find saved journals, rejecting arbitrary paths. Raw provider stdout and CDP endpoints are never surfaced to the frontend. Flow uses per-session image counters; only Colab tracks hourly T4 cycles.

`Sessions.bind_runtime(service, account, runtime_session, grant=..., source=..., evidence=..., job=None)` is the authoritative binding operation. `snapshot(job=...)` freezes bindings per job; changing default bindings preserves preexisting snapshot and request pins. Bindings record actor, grant, and evidence/instructions, without replacing genuine auth or allocation checks. When selecting a job in the UI, "Bind runtime to job / session" invokes the engine's official `bind-session` command after saving the setup binding.
