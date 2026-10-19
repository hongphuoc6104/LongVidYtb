---
name: vp-flow-cdp
description: "Generate images via Flow CDP across a 20-profile pool with adaptive tab sizing, failover and strict teardown."
---

# VP Flow CDP — Image Generation Skill

`vp-flow-cdp` is the specialized skill and engine for automated image asset generation on Google Flow using Chrome DevTools Protocol (CDP). It replaces external daemons and extensions with direct, resilient browser automation.

## 1. Architecture & Capabilities

- **Direct CDP Automation**: Communicates directly with running Chrome profiles through Chrome DevTools Protocol sockets/WebSockets (`sys/flow_cdp/`).
- **Dynamic 20-Profile Pool**: Maintains connections across up to 20 distinct Google Chrome profiles (`profile_1`..`profile_20` on ports `9222`–`9241`) located under `~/.config/google-chrome-cdp-p*`.
- **Intelligent Patch Partitioner**: Groups scene shots into moderate patches (2 to 4 shots per patch). Shots with reference dependencies (`based_on`) are kept strictly within the same patch and locked to the parent's profile.
- **Failover & Cooldown Protection**: Continuously detects abnormal signals (`PUBLIC_ERROR_UNUSUAL_ACTIVITY`, `CAPTCHA`, rate limit 429, timeouts). Automatically quarantines the affected profile with an exponential cooldown and rotates to healthy profiles in the 20-profile pool.
- **Workload-Aware Adaptive Sizing**: Dynamically calculates optimal worker count (`calculate_optimal_workers`) based on image volume to avoid RAM waste.
- **Strict Lifecycle Teardown Guarantee**: Employs `ProfileLifecycleManager` to track spawned browser instances. Upon task completion or exit, shuts down strictly the Chrome instances spawned during that run ("mở bao nhiêu tắt bấy nhiêu"), preserving user browser windows and freeing up to 7GB host RAM.
- **Relaxed Verification Contract**: Accepts valid downloaded images (`.png`, `.jpg`, `.webp`) matching required aspect ratio and technical integrity sidecars (`.json` with `forgeId`). Does **not** require UI screenshot proofs (`ui-proof.json` or snapshot captures).

## 2. Workload Allocation Tiers

| Workload Tier | Image Count | Worker Tabs | RAM Footprint | Typical Use Case |
|---|---|---|---|---|
| `MICRO` | 1–3 images | 1 worker | ~700 MB | Retakes, thumbnail, single scene repair |
| `SHORT` | 4–8 images | 2–3 workers | ~1.4–2.1 GB | Shorts/TikTok 9:16 standalone scenes (`SC01..SC05`) |
| `CHAPTER` | 9–20 images | 3–5 workers | ~2.1–3.5 GB | Single chapter generation |
| `STANDARD` | 21–50 images | 5–7 workers | ~3.5–4.9 GB | 5–8 min `full_frame_v1` explainers |
| `BULK` | >50 images | 8–10 workers | ~5.6–7.0 GB | 13 min full explainer / stress batches |

## 3. Workflow & Usage

### Step 1: Preflight & Pool Health Check
Before generating, inspect the readiness of the profile pool:

```bash
./pipeline flow status
# or directly:
python3 -c "from flow_cdp.multi_profile_manager import MultiProfileManager; import json; print(json.dumps(MultiProfileManager().get_status(), indent=2))"
```

### Step 2: Generation Invocation
When the pipeline reaches the `images` stage in `pilot.py` / `workflow.py`, `sys/image_pipeline.py` coordinates generation automatically with adaptive concurrency and lifecycle wrapping:

```python
from flow_cdp.lifecycle import ProfileLifecycleManager, calculate_optimal_workers
from flow_cdp.bridge import generate_cdp_batch

# Direct batch invocation with lifecycle tracking
with ProfileLifecycleManager(auto_teardown=True):
    batch_results = generate_cdp_batch(specs, timeout=240.0)
```

### Step 3: Local Error Recovery & Failover
If generation encounters an error or abnormal activity on one profile:
1. The profile is placed into cooldown (`PUBLIC_ERROR_UNUSUAL_ACTIVITY`).
2. Unsubmitted items are safely handed over to the next healthy profile in the 20-profile pool.
3. Dependent shots (`based_on`) remain pinned to their parent's profile to prevent foreign ID mismatches.

### Step 4: Teardown & RAM Reclamation
When run through `./pipeline run` or `pilot.py run ... images`, teardown occurs automatically via `ProfileLifecycleManager`.
To manually shut down all pool profiles:

```bash
./pipeline flow stop
# or directly:
PYTHONPATH=sys python3 -m flow_cdp.multi_profile_manager stop
```

## 4. Legacy Jobs Protocol (Các Job Tạo Trước Đó)

For older jobs created prior to the 20-profile and adaptive sizing upgrades:
1. **Automatic Code Adoption**: The pipeline execution engine (`sys/image_pipeline.py`) is shared across all jobs. Running an old job via `./pipeline run <job>` or `python3 sys/pilot.py run <job> images` automatically executes with adaptive worker sizing and lifecycle auto-teardown.
2. **Bound Profile Unbinding**: If an old job is bound to a single profile via `management_session.runtime_bindings.flow.target.profile_path` that enters cooldown, select a new job with explicit `flow_dispatch_policy: pool`; existing requests remain on their owners. A configured profile must also belong to the frozen authorized session pool.
3. **Transient Attempt Recovery**: Unfinished attempts retain submitted/ambiguous state until verified collection or explicit reconciliation. Error words, rate limits and absent downloads never establish non-submission. Only definitely unsent work may move to another healthy authorized profile.

## 5. Verification & Invariants

- **Binary Validity**: Every downloaded image must pass PIL verification (`Image.open(f).verify()`) with matching aspect ratio (9:16 or 16:9).
- **Metadata Sidecar**: Accompanied by `{image_stem}.json` containing `jobId`, `prompt`, `ratio`, `characters`, `source`, `status: "downloaded"`, and `forgeId` (or `media_id`).
- **No Synthetic Proof Hack**: Never fake screenshot proof files. The relaxed contract strictly relies on valid image binaries and sidecars.
