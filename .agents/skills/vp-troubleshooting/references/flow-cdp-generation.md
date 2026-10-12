# Troubleshooting Flow CDP Image Generation (Timeouts & Multi-Profile Failover)

## 1. Symptoms
- Running Flow CDP batch generation (`sys/flow_cdp/cdp_direct_client.py` or `sys/flow_cdp/bridge.py`) produces:
  - Error: `No page target found on CDP port <port>` or `CDP session socket not found`.
  - Requests timing out after 120s: `TimeoutError` or `PUBLIC_ERROR_UNUSUAL_ACTIVITY`.
  - Cross-profile continuity error when generating `based_on` reference shots.

---

## 2. Proven Remedies

### 1. Verify 3 Chrome CDP Profiles Are Listening
Check profile readiness across the 3 configured CDP ports (`9225`/`9222`, `9223`, `9224`):
```bash
python3 -c "import sys; sys.path.insert(0, 'sys'); from flow_cdp.multi_profile_manager import MultiProfileManager; import json; print(json.dumps(MultiProfileManager().get_status(), indent=2))"
```
If Chrome profiles are not running, launch them via:
```bash
bash sys/scripts/launch_chrome_profiles.sh
```

### 2. Ensure Signed-In Google Flow Tabs
- Each Chrome profile (`~/.config/google-chrome-cdp-p1..p3`) must have an active tab open on `https://flow.google.com/project/<project_id>`.
- Ensure tabs are not frozen or discarded.

### 3. Maintain Safe Request Throttling to Avoid Bot Detection
- When invoking generation across scene loops, maintain a minimum delay of `time.sleep(4.0)` between requests per profile.
- Never burst concurrent parallel requests into the same profile/session to avoid temporary Google Flow account lockouts.

### 4. Multi-Profile Parallel Execution & `based_on` Continuity Chains
- Each connected Chrome profile has its own isolated Flow `project_id`. A `based_on` continuity shot (`base_media_id`) **must** be executed on the **exact same profile** that created its parent image; otherwise Google Flow rejects the foreign `media_id`.
- Group every `based_on` chain into a single atomic work unit (`PatchPartitioner` / dependency chain) pinned to one worker profile, and persist `shot_id -> {media_id, profile_index}` in `_media_state.json` for safe resume.

### 5. Two-Tier Recovery for `PUBLIC_ERROR_UNUSUAL_ACTIVITY` (`ERR-20261010-07`)
- **Tier 1 — In-Flight Automatic Failover (No Destructive Tab Reload)**:
  - **Do NOT reload the tab mid-run**: Reloading mid-run races with `document_start` script injection and breaks `Object.assign` integrity checks.
  - `CDP_RECAPTCHA_GUARD_JS` in `sys/flow_cdp/cdp_direct_client.py` wraps `grecaptcha.enterprise.execute` with `executeWithAssignNeuter` and applies in-place backoff (`20s -> 35s -> 50s`) while `MultiProfileManager` places the profile on cooldown and routes remaining shots to another healthy profile.
- **Tier 2 — Persistent Profile Block Reset (7-Day Cookie & Site Data Cleanup)**:
  - If a profile remains persistently flagged across cooldown cycles, Google Flow has persisted bot-detection state in origin cookies/service workers:
    1. Clear Cookies and Site Data from the last 7 days for `https://flow.google.com/` (via CDP `Storage.clearDataForOrigin` or SQLite `Cookies` cleanup).
    2. Terminate the affected Chrome profile process and remove stale `SingletonLock` / socket files.
    3. Relaunch the Chrome profile on its assigned CDP port (`9222`/`9225`, `9223`, `9224`) and reopen the Flow Studio project tab.

### 6. Nano Banana 2.1 (`BELUGA`) Wire Format
- Google Flow's internal model identifier for **Nano Banana 2.1** is `"BELUGA"` (`NANO_BANANA_2_1`) in `sys/flow_cdp/flow_rpc.py`.
- Fresh image generations (`base_media_id is None`) require a client UUID in `slot12` of the inner protobuf array; `based_on` edits require `slot12 = None` and `slot4 = [[base_media_id, 2]]`.
