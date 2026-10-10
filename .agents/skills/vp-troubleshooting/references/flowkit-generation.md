# Troubleshooting Flow Kit Image Generation (Timeouts & Connection)

## 1. Symptoms
- Running `python3 sys/flowkit_pipeline.py generate-assets --job <job_id>` produces:
  - Error: `Flow Kit backend is unreachable or Chrome extension is not connected.`
  - Requests timing out after 120s: `URLError: <urlopen error timed out>`.
  - Google Flow flags account for unusual bot activity.

---

## 2. Proven Remedies

### 1. Verify Flow Kit Daemon Process
Check daemon status:
```bash
python3 sys/flowkit/run.py status
```
If daemon is not running, start it:
```bash
python3 sys/flowkit/run.py start
```

### 2. Ensure Chrome Extension Connectivity
- Launch Chrome with the profile containing the Flow Kit Extension (`sys/flowkit/extension`).
- Open the Google Flow tab (`https://labs.google/fx/tools/flow` or equivalent) and verify the extension icon shows `Connected` status.
- Ensure the tab is not frozen (Discarded / Sleeping tab).

### 3. Maintain Safe Request Throttling to Avoid Bot Detection
- When invoking generation across scene loops, maintain a minimum delay of `time.sleep(4.0)` between requests per profile.
- Never burst concurrent parallel requests into the same profile/session to avoid temporary Google Flow account lockouts.

### 4. Multi-Profile Parallel Execution & `based_on` Continuity Chains
- Each connected Chrome profile has its own isolated Flow `project_id` (`GET /api/flow/profiles`). A `based_on` continuity shot (`base_media_id`) **must** be executed on the **exact same `profile_index`** that created its parent image; otherwise Google Flow rejects the foreign `media_id`.
- Group every `based_on` chain into a single atomic work unit pinned to one worker thread (`profile_index`), and persist `shot_id -> {media_id, profile_index}` in `_media_state.json` for safe resume.

### 5. Handling `PUBLIC_ERROR_UNUSUAL_ACTIVITY` Without Tab Reload
- **Do NOT call `reload_flow_tab` automatically on cooldown**: Reloading the tab mid-run creates a race condition where `hijack_bypass.js` misses `document_start`, causing `Object.assign` integrity checks to fail on subsequent requests.
- Ensure `executeWithPristine` in `sys/flowkit/extension/injected.js` is wrapped with the `Object.assign` neuter guard (`installAssignNeuter`), and recover from `PUBLIC_ERROR_UNUSUAL_ACTIVITY` using in-place backoff (`20s -> 35s -> 50s`) on the same tab.

### 6. Nano Banana 2.1 (`BELUGA`) Wire Format
- Google Flow's internal model identifier for **Nano Banana 2.1** is `"BELUGA"` (`NANO_BANANA_2_1`).
- Fresh image generations (`base_media_id is None`) require a client UUID in `slot12` of the inner protobuf array; `based_on` edits require `slot12 = None` and `slot4 = [[base_media_id, 3]]`.
