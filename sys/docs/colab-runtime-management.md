# Colab runtime management

Production audio and render requests claim an account atomically in `colab_bridge.scheduler.RuntimeScheduler` before setup/upload. Claims hold both the historical session lock and a process-shared Google identity lock. Two aliases of the same Google account cannot execute concurrently, including when their local session names differ. Allocation starts are staggered across controllers.

For unbound jobs, `auto-idle` keeps its pool meaning through `remote_audio.configure_accounts`; the preferred default no longer overrides it. Only accounts in the job's frozen pool and matching the workload role are considered. Recent unhealthy observations, exhausted budgets, unresolved allocations and service blocks prevent new pooled work. Exact runtime bindings stay exact and queue for a bounded interval; they never silently switch accounts.

Submitted or ambiguous journals retain their account after the runner exits. The scheduler imports existing job journals and maintains shared references for new requests. Missing pending evidence is a blocker, not proof of remote termination. Collection continues on the original account/session even if a newer default or health observation differs.

Run an observational audit from the repository root:

```sh
./pipeline colab pool-health --check-kernels
```

When existing OAuth access credentials have expired, renew them explicitly without an interactive login:

```sh
./pipeline colab pool-health --refresh-auth --check-kernels
```

This inspects Google identity and server assignments, then sends a small device/readiness observation to existing, unlocked kernels. It never allocates a GPU, installs packages or generates media. Provider GPU allocation capacity is not tested. Token files are replaced atomically with private permissions when renewal is requested; credentials and raw provider output are excluded from the report.

The private health snapshot is stored in `~/.config/video-pilot/management/colab-health.json`. The dashboard reads this snapshot without polling providers and shows its observation time, duplicate aliases and runtime health. Re-run the audit when current evidence is needed; a cached observation is not a liveness guarantee.

Status meanings:

| State | Meaning |
| --- | --- |
| authenticated_idle | Account authentication verified; no active server VM. GPU capacity untested. |
| t4_ready | An existing kernel answered the device probe and reported T4. |
| active_kernel_not_tested | Server assignment exists; kernel response has not been verified. |
| assignment_unmapped | Server VM exists but this alias has no matching local mapping. Preserve and reconcile. |
| kernel_timeout / kernel_unconfirmed | Existing kernel did not return bounded verification. |
| refresh_required / login_required | Existing credential needs renewal or interactive login. |
| external_session_protected | Local mapping identifies another project's session. |
| busy | Another process holds the historical execution lock. |

`COLAB_POOL_WAIT` identifies a queue/capacity condition rather than a logout. It does not authorize another submission of an uncertain request. Resume only after the original request or resource dependency is reconciled.
