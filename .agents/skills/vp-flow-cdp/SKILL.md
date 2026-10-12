---
name: vp-flow-cdp
description: "Generate images via Flow CDP across 3 Chrome profiles with patch partitioning and failover."
---

# VP Flow CDP — Image Generation Skill

`vp-flow-cdp` is the specialized skill and engine for automated image asset generation on Google Flow using Chrome DevTools Protocol (CDP). It replaces external daemons and extensions with direct, resilient browser automation.

## 1. Architecture & Capabilities

- **Direct CDP Automation**: Communicates directly with running Chrome profiles through Chrome DevTools Protocol sockets/WebSockets (`sys/flow_cdp/`).
- **Concurrent 3-Profile Pool**: Maintains connections across 3 distinct Google Chrome profiles (e.g. `Profile 1` on port 9222, `Profile 2` on port 9223, `Profile 3` on port 9224) located under `~/.config/google-chrome`.
- **Intelligent Patch Partitioner**: Groups scene shots into moderate patches (2 to 4 shots per patch). Shots with reference dependencies (`based_on`) are kept strictly within the same patch to preserve intermediate media context.
- **Failover & Cooldown Protection**: Continuously detects abnormal signals (`PUBLIC_ERROR_UNUSUAL_ACTIVITY`, `CAPTCHA`, rate limit 429, timeouts). Automatically places an offending profile on cooldown and routes remaining ungenerated shots to another healthy profile.
- **Relaxed Verification Contract**: Accepts valid downloaded images (`.png`, `.jpg`, `.webp`) matching required aspect ratio and technical integrity sidecars (`.json` with `forgeId`). Does **not** require UI screenshot proofs (`ui-proof.json` or snapshot captures).

## 2. Configuration (`sys/config.json`)

Configure the engine and profile endpoints:

```json
{
  "flow_image_engine": "cdp",
  "flow_cdp_profiles": [
    {"id": "profile_1", "port": 9222, "directory": "Profile 1"},
    {"id": "profile_2", "port": 9223, "directory": "Profile 2"},
    {"id": "profile_3", "port": 9224, "directory": "Profile 3"}
  ],
  "patch_size": 3,
  "flow_model": "Nano Banana 2 Lite",
  "flow_queue_trial_enabled": true
}
```

## 3. Workflow & Usage

### Step 1: Preflight & Profile Health Check
Before generating, inspect the readiness of all 3 Chrome profiles:

```bash
python3 -c "from flow_cdp.multi_profile_manager import MultiProfileManager; import json; print(json.dumps(MultiProfileManager().get_status(), indent=2))"
```

### Step 2: Generation Invocation
When the pipeline reaches the `images` stage in `pilot.py` / `workflow.py`, `sys/image_pipeline.py` coordinates generation:

```python
from flow_cdp.bridge import generate_cdp_image, generate_cdp_batch

# Single image generation
result = generate_cdp_image(
    prompt="A cheerful stick figure student writing notes",
    ratio="16:9",
    test_case="scene-01",
    out_dir="/path/to/download"
)

# Batch generation with auto-patching and 3-profile distribution
batch_results = generate_cdp_batch(specs, timeout=240.0)
```

### Step 3: Local Error Recovery
If generation encounters an error or abnormal activity on one profile:
1. The profile is placed into `COOLDOWN` (default 60s).
2. The `PatchPartitioner` identifies which shots in the patch already succeeded.
3. Only the remaining failed shots are re-assigned to the next available healthy profile.
4. Output assets are assembled seamlessly in `sys/runs/<job>/revisions/images/`.

## 4. Verification & Invariants

- **Binary Validity**: Every downloaded image must pass PIL verification (`Image.open(f).verify()`) with matching aspect ratio (9:16 or 16:9).
- **Metadata Sidecar**: Accompanied by `{image_stem}.json` containing `jobId`, `prompt`, `ratio`, `characters`, `source`, `status: "downloaded"`, and `forgeId` (or `media_id`).
- **No Synthetic Proof Hack**: Never fake screenshot proof files. The relaxed contract strictly relies on valid image binaries and sidecars.
