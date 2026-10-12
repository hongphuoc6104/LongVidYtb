# Issue ancient-humans-day-ch1 — images (Flow CDP Multi-Profile Parallel & Nano Banana 2.1 `BELUGA`)

- **Date Recorded**: 2026-10-09 06:25:00
- **Job ID**: ancient-humans-day-ch1-16x9
- **Subsystem**: images (Flow CDP)
- **Status**: Resolved

---

## 1. Concrete Symptoms
- Triggering Command:
  ```bash
  python3 sys/exports/ancient_humans_bundle/scripts/generate_cdp_245.py 1 --workers 2 --model NANO_BANANA_2_1
  ```
- Error Messages / Tracebacks:
  1. Model resolution failure: `NANO_BANANA_2_1` not mapped to Google Flow's internal wire code (`BELUGA`).
  2. Cross-profile continuity error: When a `based_on` shot was routed to Profile `#1` while its parent image (`base_media_id`) was generated in Profile `#0`'s project (`9770a8b4-...`), Google Flow rejected the request because the `media_id` did not belong to Profile `#1`'s project (`5889e647-...`).
  3. Cooldown cascade (`PUBLIC_ERROR_UNUSUAL_ACTIVITY` / HTTP 400):
     ```text
     Batch response error: PUBLIC_ERROR_UNUSUAL_ACTIVITY
     reCAPTCHA protection broke: Object.assign modified
     ```
- Observed Behavior:
  - Automatic tab reload (`reload_flow_tab`) on cooldown caused a race condition where `hijack_bypass.js` missed `document_start`, causing subsequent `executeWithPristine` calls to trip Google Flow's `Object.assign` integrity check and trigger repeated `PUBLIC_ERROR_UNUSUAL_ACTIVITY` blocks.

---

## 2. Root Cause
1. **Missing `BELUGA` Wire Mapping & Slot12 Difference**: Google Flow uses internal model code `"BELUGA"` for **Nano Banana 2.1**. For fresh generations (`base_media_id is None`), the Flow web UI populates `slot12` with a client UUID, whereas `based_on` edits set `slot12 = None` and pass `[[base_media_id, 3]]` in `slot4`.
2. **Shared Single Concurrency Lock & Untargeted WebSocket Routing**: `flow_client.py` previously used a single global semaphore and routed requests to `sessions[0]` unless `project_id` was explicitly resolved per profile, and `based_on` chains were not grouped onto the same profile worker.
3. **Destructive Tab Reload & Unprotected `Object.assign` During `executeWithPristine`**: Reloading the Flow tab mid-run disrupted the extension's `document_start` script injection, and `executeWithPristine` did not wrap its execution with the `Object.assign` neuter guard.

---

## 3. Proven Remedies
1. **Concrete Resolution Steps**:
   - **Step 1**: Map `NANO_BANANA_2_1` / `NANO_BANANA_2.1` $\rightarrow$ `"BELUGA"` in `flow_batch.py` and `models.json`, and match the exact `BELUGA` protobuf array layout (`slot12` client UUID when `base_media_id is None`, `slot12 = None` + `slot4 = [[base_media_id, 3]]` when `base_media_id` is present).
   - **Step 2**: Add per-profile concurrency slots (`session["slot"]`), per-profile rate gates (`session["rate_gate"]`), `list_all_profiles()`, and `profile_index` routing in `flow_client.py` and `api/flow.py`.
   - **Step 3**: Group `based_on` continuity chains into atomic units in `generate_cdp_245.py` so an entire parent $\rightarrow$ child chain executes on the same `profile_index` and persists its `media_id` in `_media_state.json`.
   - **Step 4**: Remove automatic `reload_flow_tab` on cooldown (use in-place exponential backoff `20s -> 35s -> 50s` instead) and wrap `executeWithPristine` in `sys/flow_cdp/cdp_direct_client.py` with the `Object.assign` neuter guard.
2. **Diff or Code Modifications**:
   - [`sys/flow_cdp/flow_rpc.py`](sys/flow_cdp/flow_rpc.py)
   - [`sys/flow_cdp/flow_rpc.py`](sys/flow_cdp/flow_rpc.py)
   - [`sys/flow_cdp/cdp_direct_client.py`](sys/flow_cdp/cdp_direct_client.py)
   - [`sys/flow_cdp/bridge.py`](sys/flow_cdp/bridge.py)
   - [`sys/flow_cdp/cdp_direct_client.py`](sys/flow_cdp/cdp_direct_client.py)
   - [`sys/exports/ancient_humans_bundle/scripts/generate_cdp_245.py`](sys/exports/ancient_humans_bundle/scripts/generate_cdp_245.py)
3. **Live Verification Evidence**:
   - Successfully generated all **34/34 Chapter 1 Blind-Test images** across 2 Chrome profiles (`#0` and `#1`) at [`sys/exports/ancient_humans_bundle/generated_images/ch1/`](sys/exports/ancient_humans_bundle/generated_images/ch1).
   - Technical verification: 34/34 JPEG files (`Missing: 0`), resolution `1376x768` (16:9), total size `5.90 MB`, continuity chains verified in [`_media_state.json`](sys/exports/ancient_humans_bundle/generated_images/ch1/_media_state.json).
