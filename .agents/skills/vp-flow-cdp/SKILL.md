---
name: vp-flow-cdp
description: "Generate images and seamless multi-clip video chains via Flow CDP across a 39+ profile pool with adaptive tab sizing, credit ledger, and strict teardown."
---

# VP Flow CDP & Video Chain Skill (`vp-flow-cdp` / `vp-flow-video`)

`vp-flow-cdp` is the specialized skill and engine for automated high-fidelity visual generation on Google Flow (`flow.google.com`) using Chrome DevTools Protocol (CDP). It orchestrates both **AI Image Generation** (BELUGA / Imagen 3) and the **Flow Video Chain Engine** (`vp-flow-video` — Start & End Frame video synthesis powered by **Omni 1.2 Flash (`omni_1_2_flash` / `omni_flash` default, family `macaron_cookie`)** and Veo 3.1) across a unified pool of 39+ Google accounts with multiprocess credit accounting and zero-stutter stitching.

---

## 1. Architecture & Verified `batchexecute` RPCs

Google Flow uses Google's internal `batchexecute` Angular frontend transport (`/_/AiSandboxAngularFrontend/data/batchexecute`). Automation communicates directly with signed-in Chrome instances via CDP (`sys/flow_cdp/cdp_direct_client.py` and `sys/flow_cdp/flow_rpc.py`), sending typed RPC envelopes and decoding multi-chunk responses.

### Verified RPC Endpoints

| RPC ID | Function | Quota Cost | Purpose & Mechanics |
|---|---|---|---|
| `nprQif` | `video_start_end_frames_request` | **12–30 credits** | Generates video transitioning from Start Frame to End Frame (`START_END_FRAMES`, Omni 1.2 Flash 4s=12c, 6s=18c, 8s=24c, 10s=30c; Veo 3.1: 10–100c). |
| `eb1hJf` | `video_start_frame_request` | **12–30 credits** | Generates video expanding outward from a single initial frame (`START_FRAME`, Omni 1.2 Flash 4s=12c, 6s=18c, 8s=24c, 10s=30c; Veo 3.1: 10–100c). |
| `maseQ` | `upload_image` | **0 credits** | Uploads local image frame into Google Flow project storage, returning `media_id` and CDN URL. Enables parallel multi-account rendering of a single chain by sharing local frames without cross-account permission blocks. |
| `nzlxg` | `credits_request` | **0 credits** | Queries live account credit balance (`credits_remaining`, `subscription_credits`, `expiry_epoch`, `paygate_tier`). |
| `jwpduf` | `operation_request` | **0 credits** | Polls status of ongoing video/image generation operations until state is `CAE` (Complete). |
| `ogiZ0b` | `image_request` | **1 credit** | Synthesizes 2D images across models (`BELUGA`, `NARWHAL`, `GEM_PIX_2`). |
| `jHPbke` | `create_project_request` | **0 credits** | Creates isolated working canvas project (`projects/*`) for scoped asset storage. |
| `as29s` | `media_request` | **0 credits** | Fetches detailed asset metadata for a single generated media item. |

---

## 2. Unified 39+ Profile Pool & Credit Ledger (`sys/flow_cdp/credit_ledger.py`)

Video Pilot manages a scalable fleet of 39+ isolated Google Chrome profiles (`profile_1`..`profile_39`, extending to `profile_40+` on ports `9270+`).

### Multiprocess Credit Ledger Mechanics

- **Persistence & Locking**: Thread-safe (`threading.RLock`) and multiprocess-safe (`fcntl.flock`) store located at `~/.config/video-pilot/flow/credits.json` (overridable via `VP_FLOW_CREDITS_PATH`).
- **Quota Accounting**: Tracks `credits_remaining`, `subscription_credits` (1,000 credits/account), `expiry_epoch`, and `last_used_at`.
- **LRU & Highest-Balance Allocation**: `CreditLedger.select_eligible_profiles()` prioritizes profiles with the highest remaining credits, using Least-Recently-Used (LRU) as a tie-breaker.
- **Automatic Subscription Reset**: When wall-clock time passes `expiry_epoch`, balances automatically reset to subscription quota.
- **Failover & Quarantine**: Profiles encountering `PUBLIC_ERROR_UNUSUAL_ACTIVITY`, 429 rate limits, or CAPTCHA are quarantined with exponential cooldown while healthy profiles take over remaining tasks.

### Pool Management CLI

#### 1. Live Credit Balance Check
Inspect current credit ledger balances or query Google Flow live via RPC:

```bash
# View current local ledger snapshot:
PYTHONPATH=sys python3 -m flow_cdp.accounts credits

# Live RPC refresh against flow.google.com across all profiles:
PYTHONPATH=sys python3 -m flow_cdp.accounts credits --refresh

# Refresh specific target profiles with custom concurrency:
PYTHONPATH=sys python3 -m flow_cdp.accounts credits --refresh --profiles profile_1,profile_2,profile_3 --concurrency 3
```

#### 2. Unlimited 1,000-Credit Account Onboarding
Onboard $N$ new Google accounts on dedicated ports starting at `9270+`:

```bash
# Onboard 3 new accounts sequentially (profile_40, profile_41, profile_42):
PYTHONPATH=sys python3 -m flow_cdp.accounts onboard --count 3 --start-port 9270
```

Each onboarded profile receives an isolated Chrome user data directory (`~/.config/google-chrome-cdp-profileN`), opens a visible browser for one-time Google login, registers 1,000 initial credits into `credits.json`, and cleanly shuts down.

---

## 3. Flow Video Chain Engine (`vp-flow-video`)

Located in `sys/flow_video/` with execution via `sys/tools/run_flow_video_chain.py`, the Flow Video Chain Engine transforms sequences of still keyframes into continuous, high-definition cinematic video.

### Dual Video Chaining Modes

```
Mode A: Daisy Chain (Continuous Sequence)
[F0] ──clip 0──> [F1] ──clip 1 (trim 1f)──> [F2] ──clip 2 (trim 1f)──> [F3]
 Result: Seamless zero-stutter flow across keyframes

Mode B: Scene Pairs (Beat-Synchronized Transitions)
Scene 1: [A1] ──setpts speed-fit──> [B1] (lands exactly on audio beat)
Scene 2: [A2] ──tpad clone hold───> [B2] (natural speed + frozen hold)
```

#### Mode A: `daisy_chain` (`F0 -> F1 -> F2 -> ... -> FN`)
- **Use Case**: Continuous camera flight, evolving scenes, or linear journeys across multiple keyframes.
- **Zero-Stutter Boundary Deduplication**:
  - In a raw chain, clip 0 ends on frame $F_1$ and clip 1 begins on frame $F_1$. Concatenating them directly causes an unsightly 1-frame visual stutter/freeze at every seam.
  - Video Pilot automatically applies boundary deduplication:
    - Clip 0 retains its complete duration (`trim_first_frame = False`).
    - Every subsequent clip $i \ge 1$ sets `trim_first_frame = True`, invoking FFmpeg `trim=start_frame=1,setpts=PTS-STARTPTS` (or Remotion `trimBefore=1`).
  - Result: The boundary frame is never duplicated, yielding seamless, fluid 60fps/30fps motion.

#### Mode B: `scene_pairs` (`(A1 -> B1), (A2 -> B2), ...`)
- **Use Case**: Independent narrative beats or storyboard scenes where each clip has a designated target duration matching narration cadence.
- **Pacing Adaptation & Hold Governance**:
  - **Smooth Speed-Fit ($0.7 \le \text{raw}/\text{target} \le 1.35$)**: Applies `setpts=(target/raw)*PTS` to smoothly time-stretch or compress motion so the visual action hits the End Frame precisely on the narration beat.
  - **Final-Frame Hold ($\text{target} > \text{raw} \times 1.35$)**: Plays motion at natural speed and holds the completed final frame using `tpad=stop_mode=clone:stop_duration=...` for stable viewer contemplation.
  - **Speed Cap ($\text{target} < \text{raw} \times 0.7$)**: Speeds up to a maximum of $1.35\times$ and cleanly trims remainder, preventing unnatural hyper-speed artifacts.

### Default Model & Auto-Duration Architecture

The video chain engine uses **`omni_1_2_flash` / `omni_flash` (`Omni 1.2 Flash`, family ID `macaron_cookie`)** as the default video generation model with **Auto-Duration** enabled by default:
- **`start_end_frames` (`nprQif`)**:
  - `target_duration <= 4.8s` $\rightarrow$ **4s clip** (**12 credits**) — `macaron_cookie_i2v_fl_4s`
  - `4.8s < target_duration <= 6.8s` $\rightarrow$ **6s clip** (**18 credits**) — `macaron_cookie_i2v_fl_6s`
  - `6.8s < target_duration <= 8.8s` $\rightarrow$ **8s clip** (**24 credits**) — `macaron_cookie_i2v_fl_8s`
  - `target_duration > 8.8s` $\rightarrow$ **10s clip** (**30 credits**) — `macaron_cookie_i2v_fl_10s`
- **`start_frame` (`eb1hJf`)**:
  - `target_duration <= 4.8s` $\rightarrow$ **4s clip** (**12 credits**) — `macaron_cookie_i2v_4s`
  - `4.8s < target_duration <= 6.8s` $\rightarrow$ **6s clip** (**18 credits**) — `macaron_cookie_i2v_6s`
  - `6.8s < target_duration <= 8.8s` $\rightarrow$ **8s clip** (**24 credits**) — `macaron_cookie_i2v_8s`
  - `target_duration > 8.8s` $\rightarrow$ **10s clip** (**30 credits**) — `macaron_cookie_i2v_10s`
- **Legacy Omni 1.1 Flash (`abra`)**: Supported for backward compatibility:
  - `start_end_frames`: 4s (7c), 6s (10c), 8s (12c) — `omni_flash_i2v_{4s,6s,8s}_first_last`
  - `start_frame`: 4s (7c), 6s (10c), 8s (12c), 10s (15c) — `abra_i2v_{4s,6s,8s,10s}`
- **Fixed Duration Override**: Passing `--no-auto-duration --duration 6` locks every clip to a fixed 6s duration.
- **Alternate Veo Models**:
  - `veo_3_1_fast`: 8s, 20 credits
  - `veo_3_1_lite`: 8s, 10 credits
  - `veo_3_1_quality`: 8s, 100 credits

### Audio & Lip-Sync Governance

1. **Default Muted Native Audio**: Synthesized video tracks are muted by default (`keep_veo_audio=False`) during stitching to prevent synthetic background noise and conflicting audio artifacts from interfering with professional voiceover.
2. **`no_talking_prompt_guard`**:
   - Spoken video clips with talking characters cause jarring lip-sync mismatches against narrator audio.
   - Unless `--allow-talking` is specified, the planner automatically appends:
     ```
     ", silent visual storytelling, no talking, no lip movement"
     ```
   - Characters remain visually expressive without flapping their mouths out of sync.
3. **External Voiceover & LUFS Normalization**:
   - Supports `--audio <path>` for narration dubbing.
   - Automatically normalizes external audio to Video Pilot's invariant broadcast standard: **`-11.0 LUFS` / `-1.0 dBTP`** (`--normalize-lufs`).
4. **Overrides**:
   - `--keep-veo-audio`: Retains Veo synthesized background audio / ambient SFX.
   - `--allow-talking`: Disables the silent visual storytelling prompt guard.

### Multi-Account Parallel Orchestration

The orchestrator (`FlowVideoChainOrchestrator`) leverages the 39+ profile pool to accelerate long video chains:
1. **0-Credit Frame Pre-Upload (`maseQ`)**: Uploads local keyframe images once per worker profile via `maseQ` RPC without credit consumption.
2. **Parallel Task Dispatch**: Distributes clip generation tasks across multiple independent Chrome instances simultaneously via `CreditLedger` LRU selection.
3. **Resilient Polling & Manifesting**: Polls status via `jwpduf`, records per-clip state in `chain_manifest.json`, and supports interrupted job resumption (`--resume`).
4. **Remotion Integration**: Exports `remotion_beats.json` containing exact frame offsets, durations, and `trimBefore` metadata for editing inside `sys/renderer/`.

---

## 4. Flow Image Generation Engine

### Workload Allocation Tiers

| Workload Tier | Image Count | Worker Tabs | RAM Footprint | Typical Use Case |
|---|---|---|---|---|
| `MICRO` | 1–3 images | 1 worker | ~700 MB | Retakes, thumbnail, single scene repair |
| `SHORT` | 4–8 images | 2–3 workers | ~1.4–2.1 GB | Shorts/TikTok 9:16 standalone scenes (`SC01..SC05`) |
| `CHAPTER` | 9–20 images | 3–5 workers | ~2.1–3.5 GB | Single chapter generation |
| `STANDARD` | 21–50 images | 5–7 workers | ~3.5–4.9 GB | 5–8 min `full_frame_v1` explainers |
| `BULK` | >50 images | 8–10 workers | ~5.6–7.0 GB | 13 min full explainer / stress batches |

### Image Engine Invariants

- **Intelligent Patch Partitioner**: Groups scene shots into 2–4 shot patches. Shots with reference dependencies (`based_on`) are locked strictly to the parent's profile.
- **Strict Teardown Guarantee**: `ProfileLifecycleManager` records all spawned Chrome instances and ensures strict termination upon completion ("mở bao nhiêu tắt bấy nhiêu"), freeing up to 7GB host RAM.
- **Relaxed Verification Contract**: Accepts downloaded images passing PIL binary verification with required aspect ratio (16:9, 9:16, 1:1) and `{image_stem}.json` technical sidecar (`forgeId`, `jobId`, `prompt`, `status: "downloaded"`). Does **not** require UI screenshot captures.

---

## 5. CLI Reference & Workflows

### Running Flow Video Chain (`run_flow_video_chain.py`)

#### Mode A: Daisy Chain from Frame Directory
```bash
# Seamless daisy chain across all sorted PNG/JPG frames in a directory (defaults to omni_flash + auto-duration):
PYTHONPATH=sys python3 sys/tools/run_flow_video_chain.py \
  --frames-dir sys/runs/explainer_v1/frames \
  --mode daisy_chain \
  --aspect 16:9 \
  --model omni_flash \
  --auto-duration \
  --prompt "smooth cinematic camera movement, 2d hand-drawn style" \
  --audio sys/runs/explainer_v1/audio/voiceover.wav \
  --output video/flow_video/explainer_chain.mp4 \
  --max-workers 6
```

#### Mode B: Scene Pairs from Specification JSON
```bash
# Execute storyboard scene pairs with beat matching:
PYTHONPATH=sys python3 sys/tools/run_flow_video_chain.py \
  --spec sys/runs/story_job/video_chain_spec.json \
  --output video/flow_video/story_final.mp4 \
  --max-workers 8
```

#### Dry-Run Mode (Zero Credit Consumption)
```bash
# Verify clip stitching, filtergraphs, and Remotion beats using synthetic test media:
PYTHONPATH=sys python3 sys/tools/run_flow_video_chain.py \
  --frames-dir tests/fixtures/sample_frames \
  --mode daisy_chain \
  --dry-run
```

### Pipeline Flow Service Control

```bash
# Inspect pool readiness and running Chrome instances:
./pipeline flow status

# Stop and reclaim RAM from all running pool profiles:
./pipeline flow stop
# or directly:
PYTHONPATH=sys python3 -m flow_cdp.multi_profile_manager stop
```

---

## 6. Technical Invariants & Governance Summary

- **Single Source of Truth**: Video Pilot invariants (`AGENTS.md`) take precedence. All voiceover dubs MUST hit `-11.0 LUFS` / `-1.0 dBTP`.
- **Zero-Stutter Guarantee**: Daisy chains MUST trim the first frame on clips $i \ge 1$ (`trim=start_frame=1`).
- **Lip-Sync Integrity**: Characters MUST NOT flap mouths during voiceover; prompts must enforce silent visual storytelling unless talking is explicitly requested.
- **Resource Safety**: All Chrome processes spawned for generation MUST be tracked and cleanly killed via `ProfileLifecycleManager` and `process_manager.py`.
- **Credit Safety & Fallback Hierarchy**:
  - **Priority 1 (Default while ANY Flow pool profile has credit)**: `100% Full-Chain` (`produce_unified_flow_remotion_e2e.py --motion-mode full_chain`, `Omni 1.1 Flash` continuous keyframe-to-keyframe video chain across 16 parallel GPU Chrome workers + Remotion VietSub/watermark/audio render).
  - **Priority 2 (Automatic Fallback ONLY when 100% of Flow pool profiles have 0 video credits left)**: Dense Multi-Image mode (`images_only` with high-density Flow keyframes: 10–14 images for `9:16` Short, 28–70+ images for `16:9` Long + Remotion camera motion/VietSub/audio render). Automatically triggered if all profiles reach 0 video credits or fail mid-chain.
  - Never perform dry-run tests with live RPC calls; use `--dry-run` to validate pipeline stitching without burning 1,000-credit account quotas.
