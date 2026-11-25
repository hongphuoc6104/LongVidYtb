# Troubleshooting Flow CDP Image Generation (Timeouts, Multi-Profile Failover & Anti-Ban)

## 1. Symptoms
- Running Flow CDP batch generation (`sys/flow_cdp/cdp_direct_client.py` or `sys/flow_cdp/bridge.py`) produces:
  - Error: `No page target found on CDP port <port>` or `CDP session socket not found`.
  - Error 7/8: `PUBLIC_ERROR_UNUSUAL_ACTIVITY` or `TOO_MUCH_TRAFFIC` (rate limiting / bot detection).
  - High CPU spikes (100%) due to Chrome falling back to software SwiftShader.
  - Cross-profile continuity error when generating `based_on` reference shots.

---

## 2. Five Mandatory Anti-IP-Ban & Purposeful Speed Invariants

1. **GPU Headless Chrome within 90% VRAM**:
   - MUST launch with:
     ```bash
     --headless=new --ozone-platform=x11 --disable-software-rasterizer --force-gpu-mem-available-mb=1843
     ```
   - Prevents CPU SwiftShader fallback and 100% CPU lockups.
2. **Cross-Process Staggered Chrome Launch**:
   - Stagger Chrome starts with `>= 3.2s + 0..0.6s` jitter via `stagger_cross_process_action("chrome_launch", gap=3.2, jitter=0.6)`.
   - Never boot all Chrome windows simultaneously into `flow.google.com`.
3. **Cross-Process Global Jittered RPC Pacer**:
   - Pacer `stagger_cross_process_action("flow_rpc_submit", gap=1.55, jitter=0.35)` caps host-wide RPC throughput at `~34–38 RPCs/min`, eliminating `TOO_MUCH_TRAFFIC`.
4. **Warm Session Preservation (`ERR-20261010-07`)**:
   - On Error 7/8 (`PUBLIC_ERROR_UNUSUAL_ACTIVITY` / `TOO_MUCH_TRAFFIC`), **NEVER kill or relaunch Chrome** and **NEVER reload the tab**.
   - Instead, refresh reCAPTCHA in-place (`_refresh_recaptcha_session`), keep the warm browser instance alive during cooldown, and quarantine `NO_AT_TOKEN` profiles to `unauthenticated_profiles.json`.
5. **Multi-Prompt `ogiZ0b` Batching**:
   - Batch 2–4 independent anchor prompts via `generate_images_batch()` on `ogiZ0b` for a 3X–4X throughput speedup and 75% fewer RPC calls.

---

## 3. Proven Remedies

### 1. Verify Chrome CDP Profiles Are Listening
Check profile readiness across configured CDP ports:
```bash
python3 -c "import sys; sys.path.insert(0, 'sys'); from flow_cdp.multi_profile_manager import MultiProfileManager; import json; print(json.dumps(MultiProfileManager().get_status(), indent=2))"
```

### 2. Multi-Profile Parallel Execution & `based_on` Continuity Chains
- Each connected Chrome profile has its own isolated Flow `project_id`. A `based_on` continuity shot (`base_media_id`) **must** be executed on the **exact same profile** that created its parent image; otherwise Google Flow rejects the foreign `media_id`.
- Group every `based_on` chain into a single atomic work unit (`PatchPartitioner` / dependency chain) pinned to one worker profile, and persist `shot_id -> {media_id, profile_index}` in `_media_state.json` for safe resume.

### 3. Nano Banana 2.1 (`BELUGA`) Wire Format
- Google Flow's internal model identifier for **Nano Banana 2.1** is `"BELUGA"` (`NANO_BANANA_2_1`) in `sys/flow_cdp/flow_rpc.py`.
- Fresh image generations (`base_media_id is None`) require a client UUID in `slot12` of the inner protobuf array; `based_on` edits require `slot12 = None` and `slot4 = [[base_media_id, 2]]`.
