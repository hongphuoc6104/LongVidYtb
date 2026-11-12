---
name: vp-flow-cdp
description: "Generate images and seamless multi-clip video chains via Flow CDP across a 39+ profile pool with adaptive tab sizing, credit ledger, and strict teardown."
---

# VP Flow CDP & Video Chain Skill (`vp-flow-cdp`)

Orchestrates Google Flow (`flow.google.com`) via CDP across a 39+ profile pool (`profile_1..39+`, ports `9222+` / `9270+`) for **BELUGA image generation** and **Omni 1.2 Flash (`macaron_cookie`) video chains**.

## 1. Five Mandatory Anti-IP-Ban & Speed Invariants
1. **GPU Headless Chrome (90% VRAM)**: Obey [gpu-headless-chrome.md](../../rules/gpu-headless-chrome.md) (`build_optimized_chrome_launch()`, `--headless=new --ozone-platform=x11 --force-gpu-mem-available-mb=1843`, zero SwiftShader CPU fallback).
2. **Staggered Chrome Launch**: `stagger_cross_process_action("chrome_launch", min_interval_sec=3.2, jitter_sec=0.6)`. Never launch browsers simultaneously.
3. **Global Jittered RPC Pacer**: `stagger_cross_process_action("flow_rpc_submit", min_interval_sec=1.55, jitter_sec=0.35)` (~34–38 RPCs/min host-wide).
4. **Warm Session Preservation (`ERR-20261108-02`)**: On Error 7/8 (`PUBLIC_ERROR_UNUSUAL_ACTIVITY` / `TOO_MUCH_TRAFFIC`), never kill/reload Chrome — call `_refresh_recaptcha_session` in place and put the profile on cooldown. Quarantine `NO_AT_TOKEN` profiles to `unauthenticated_profiles.json`.
5. **Multi-Prompt `ogiZ0b` Batching**: Batch independent anchor prompts in groups of 2–4 via `generate_images_batch()`.

## 2. Verified `batchexecute` RPCs & Credit Ledger (`sys/flow_cdp/credit_ledger.py`)
- **RPCs**: `ogiZ0b` (image, 1c, batch 2–4), `nprQif` (`start_end_frames` video, 12–30c), `eb1hJf` (`start_frame` video, 12–30c), `maseQ` (upload frame, 0c), `nzlxg` (credits, 0c), `jwpduf` (poll operation `CAE`, 0c), `jHPbke` (create project, 0c).
- **Ledger (`~/.config/video-pilot/flow/credits.json`)**: `fcntl.flock` multiprocess store; `select_eligible_profiles()` prioritizes `last_used_at > 0` + highest remaining balance (LRU tie-breaker).
- **Credit Fallback Hierarchy**:
  - **P1 (`full_chain`)**: Default while ANY pool profile has credit (`Omni 1.2 Flash` video chain + Colab T4 `h264_nvenc`).
  - **P2 (`images_only`)**: Automatic fallback ONLY when 100% of pool profiles hit 0 credits (cooldown ≠ 0 credits).

## 3. Core CLI Commands
```bash
# Pool status & teardown:
./pipeline flow status
./pipeline flow stop

# Credit balance snapshot or live RPC refresh:
PYTHONPATH=sys python3 -m flow_cdp.accounts credits
PYTHONPATH=sys python3 -m flow_cdp.accounts credits --refresh --concurrency 3

# Onboard new 1,000-credit accounts (interactive login):
PYTHONPATH=sys python3 -m flow_cdp.accounts onboard --count 3 --start-port 9270
```

## 4. Progressive Disclosure References
- **Video Chain Engine (`daisy_chain` / `scene_pairs`, auto-duration, CLI)**: [video-chain-engine.md](references/video-chain-engine.md)
- **Submission Safety & Journal Integrity**: [submission-safety.md](references/submission-safety.md)
