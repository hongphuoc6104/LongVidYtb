# Thread 3B — Ultra Credit Ledger, Flow Rate-Limit & Colab T4 Throughput Plan (V12)

> **Audit Scope (READ-ONLY)**: Audited `sys/flow_cdp/credit_ledger.py`, `browser-profiles.json`, `cdp_direct_client.py`, `flow_rpc.py`, `resource_locks.py`, `sys/flow_video/orchestrator.py`, `chain_planner.py`, `sys/short_engine/flow_stage.py`, `audio_epic.py`, `render_single_pass.py`, `sys/tools/produce_serialized_short.py`, `produce_su_ke_lai_long_m1.py`, `produce_vn_dual_mode.py`, `synthesize_vn_long_omnivoice.py`, `sys/account_budget.py`, `sys/colab_bridge/*`, `PLAYBOOK.md`, `.agents/rules/gpu-headless-chrome.md`, and live state under `~/.config/video-pilot/`. **Zero Chrome or Colab sessions were launched.**

---

## 1. Host Hardware & Concurrency Envelope

| Resource | Measured Value | Enforcement in Code |
|---|---|---|
| Host RAM | `15,934 MiB` (`9,676 MiB` free) | `compute_optimal_browser_slots()` caps global Chrome slots at **`4`** on `<= 16,800 MiB` (`sys/flow_cdp/resource_locks.py:133-154`) |
| CPU / `/dev/shm` | `8` threads / `7.8 GiB` tmpfs (`74 MiB` used) | `/dev/shm` >= `512 MiB`, so `--disable-dev-shm-usage` is omitted (`gpu-headless-chrome.md`) |
| GPU VRAM | NVIDIA Quadro P620 (`2048 MiB`) | `--force-gpu-mem-available-mb=1843` (`90%`), `--ozone-platform=x11`, `--headless=new` |
| Flow Stage Workers | `stage="image": 3` / `stage="video": 2` | `flow_stage.py:41-48` resolves `auto` to `3` img / `2` vid when `DEFAULT_MAX_GLOBAL_BROWSERS <= 4` (rule doc mentions `3` vid for >4-slot hosts) |

---

## 2. Live Flow Credit Ledger & Profile Mapping (`4` Ultra + `36` Pool = `40` Profiles)

> **Baseline reconciliation**: Prior to recent V10/V11 Short (`S01..S10`) and Long (`L01` 7 clips) runs, the 4 Ultra accounts held ~`101,130` credits. Live `~/.config/video-pilot/flow/credits.json` now records **`99,876` Ultra credits** (`99,924` `subscription_credits`) + **`14,179` credits across the remaining 36 pool profiles** = **`114,055` total credits** across all 40 configured profiles (plus `3,990` in 4 legacy/unmapped keys `prof_1`, `prof_a`, `profile_en04`, `null`).

### 2.1 The 4 Google AI Ultra Accounts (`paygate_tier = 2`)

| Profile ID | Email | Chrome Dir / Port | Credits Remaining | Sub Credits | Expiry (UTC) | Live State & Readiness |
|---|---|---|---:|---:|---|---|
| `profile_22` | `thue2127@gmail.com` | `Profile 53` / `9270` | **25,459** | 25,483 | `2026-12-18` | **READY NOW** (`cd=0s`) |
| `profile_en01` | `admin6104@gmail.com` | `Default` / `9251` | **25,050** | 25,050 | `2026-12-24` | **COOLDOWN (`~17,695s` / `4.9h`)** — `NO_AT_TOKEN` (not in `unauthenticated_profiles.json`; refresh Flow tab or wait) |
| `profile_18` | `phuocnguyencoc4@gmail.com` | `Profile 22` / `9239` | **24,849** | 24,849 | `2026-12-24` | **READY NOW** (`cd=0s`; prior Error 8 cooldown expired) |
| `profile_en03` | `tiktokbeeby@gmail.com` | `Profile 12` / `9253` | **24,518** | 24,542 | `2026-12-24` | **READY NOW** (`cd=0s`) |
| **Subtotal** | **4 Ultra Accounts** | — | **99,876** | **99,924** | — | **`74,826` ready immediately**; `+25,050` after `NO_AT_TOKEN` refresh |

### 2.2 Remaining 36 Pool Profiles (`14,179` Credits)

1. **14 Authenticated Video-Ready (`>=10c`) Profiles — `6,588` credits**:
   - `profile_en18` (`1,544`), `profile_en15` (`1,050`), `profile_11` (`974`), `profile_6` (`900`), `profile_en19` (`848`), `profile_en02` (`636`), `profile_19` (`164`), `profile_en10` (`155`), `profile_9` (`105`), `profile_en08` (`54`), `profile_16` (`50`, `paygate_tier=3`), `profile_en14` (`50`, `paygate_tier=3`), `profile_en17` (`47`), `profile_en11` (`11`).
2. **1 Authenticated Cooldown Profile — `364` credits**: `profile_en09` (`NO_AT_TOKEN`, `~48,608s` remaining).
3. **7 Authenticated Zero-Credit / `<7c` `BELUGA` Specialists — `18` residual credits, UNLIMITED `0c` image capacity**:
   - `profile_5` (`0`), `profile_8` (`0`), `profile_10` (`0`), `profile_en05` (`2`), `profile_en07` (`6`), `profile_en13` (`6`), `profile_en16` (`4`).
   - *Critical Routing Optimization*: `credit_ledger.py:pick_for_image_task()` routes `BELUGA` (`0c`) to `<7c` specialists first, whereas `flow_stage.py:_ordered_stage_a_profiles()` currently sorts Ultra `25k+` first. For V12, pass `VP_FLOW_PROFILES` with these 7 zero-credit specialists during Stage A so the 4 Ultra Chrome sessions stay **unthrottled and pristine** for Stage B video.
4. **14 Quarantined Unauthenticated Profiles (`unauthenticated_profiles.json`) — `7,209` credits**:
   - `profile_1` (`0`), `profile_2` (`1,050`), `profile_3` (`97`), `profile_4` (`0`), `profile_7` (`848`), `profile_12` (`50`), `profile_13` (`2`), `profile_14` (`50`, `tier=3`), `profile_15` (`1,050`), `profile_17` (`1,050`), `profile_20` (`1,040`), `profile_21` (`52`), `profile_en06` (`870`), `profile_en12` (`1,050`). Require interactive re-login before use.
5. **`browser-profiles.json` Note**: Contains 40 directory entries matching `profiles.json`, with `"Default"` appearing twice (`profile_5` and `profile_en01`, disambiguated by `user_data_dir` in `profiles.json`).

---

## 3. Colab T4 Account Pool Audit (`20` Registered -> `15` Unique -> `8` Active + `1` Hot Spare)

`ColabPoolManager` deduplicates 5 duplicate OAuth identities (`account-06`=`03`, `07`=`04`, `09`=`01`, `11`=`02`, `14`=`05`), leaving **15 unique Google identities**, each governed by a `5h` (`18,000s`) usable / `1h` reserve 24h anchor window in `sys/account_budget.py`:

| Group | Accounts | Available GPU-Seconds | Notes & Required Action |
|---|---|---:|---|
| **Active 8 Production T4 Accounts** | `account-01` (`17,760.0s`), `account-04` (`16,759.4s`), `account-17` (`13,392.1s`), `account-12` (`12,121.8s`), `account-18` (`10,860.3s`), `account-19` (`10,768.5s`), `account-05` (`10,250.4s`), `account-20` (`9,967.7s`, resets to `18,000s` in `0.18h`) | **101,880.2s (`28.30h`)** | Zero active blocks (`blocks={}`). Run `colab_bridge reconcile` on `12` & `20` if stale `colab-health.json` assignment flag persists. |
| **9th Hot Spare** | `account-08` (`phuocnguyendb010204@gmail.com`) | **18,000.0s (`5.00h`)** | Untouched (`used=0s`), `blocks={}`, ready immediately. |
| **24h Window Exhausted (`3`)** | `account-10` (resets `2.48h`), `account-13` (resets `4.70h`), `account-02` (resets `6.25h`, stale local session `vp-r1-vn_su_ke_lai_ep2`) | **0.0s** | Unlocks automatically over the next `2.5–6.25h` for Wave 2/3. |
| **Provider Blocked (`3`)** | `account-03` (`429`), `account-15` (`503`), `account-16` (`503`) | *(blocked)* | Exclude (`VP_COLAB_EXCLUDE`) until provider block clears. |
| **Total Healthy Unblocked** | **9 unique T4 accounts** | **119,880.2s (`33.30h`)** | Over **4x** the compute needed for all 20 V12 episodes. |

---

## 4. V12 Flow Credit, Coverage & IP-Rate-Limit Schedule (`S01..S10` + `L01..L10`)

### 4.1 Model Cost & Pacing Constraints
- **`BELUGA` (`ogiZ0b`, 1–4 prompt batches)**: **`0` credits** — unlimited multi-angle coverage frames (extreme macro tactile inserts, OTS, ground POV, God's-eye, reaction close-ups, Flow-native thumbnails).
- **`veo_3_1_lite` Seam (`eb1hJf`, `end_frame_path=None`)**: **`10` credits flat** (`4s/6s/8s @ 720p`). Default for cuts across changing cast, lighting, or camera angles.
- **`macaron_cookie` Omni 1.2 Flash (`nprQif` Frame-Link / `eb1hJf` Seam)**: **`12c` (`4s`) / `18c` (`6s`) / `24c` (`8s`) / `30c` (`10s`)**. Default for continuous identical-cast/lighting transitions and automatic `[TRAFFIC_MODEL_FAILOVER]` target after `>=2` `TOO_MUCH_TRAFFIC` blocks on `veo_3_1_lite`.
- **Anti-Ban Pacing (`.agents/rules/gpu-headless-chrome.md` & `vp-flow-cdp`)**:
  - `chrome_launch`: `3.2s + 0..0.6s` jitter; max `4` host browsers.
  - `flow_rpc_submit`: `1.55s + 0..0.35s` rule (`2.5s + 0..0.4s` enforced in `cdp_direct_client.py`).
  - `flow_video_rpc_submit`: **`4.2s + 0..0.8s` jitter** (~`12–14` submissions/min host-wide).
  - **Host-IP Rolling-Hour Cap**: **`<= 55` video clips per rolling 60 minutes** across `eb1hJf + nprQif` combined, followed by a **`10–15 min` quiet breather** (overlapped with Colab T4 TTS/NVENC!).
  - **Error 7/8 Guard**: Keep Chrome open, `_refresh_recaptcha_session` in place, `8.0s`/`30.0s` burst pause, persist `frames/beat_XX.json` `profile_media_ids`.

### 4.2 Per-Episode & Fleet Allocation (`10` Shorts + `10` Longs)

| Format | Scope | `BELUGA` (`0c`) Coverage Frames | Living Video Clips | Model Mix & Credit Cost | IP Waves (`<=55/hr`) |
|---|---|---|---|---|---|
| **Short (`S01..S10`)** (`48–88s`, 20 beats) | Per Short | `20` beat anchors + `6` extra macro/OTS/POV cutaways + `1` `9:16` thumb = **`27` frames (`0c`)** | **`16` living clips** (`4` beats reserved for bespoke slow giant-text maps / cutaways) | `10 × veo_3_1_lite` (`100c`) + `6 × macaron_cookie 6s` (`108c`) = **`208c`** *(or `264c` for 20/20 full-video)* | `0.3` waves (~20m/Short) |
| **All 10 Shorts** | `S01..S10` | **`270` frames (`0c`)** (`~70` 4-prompt `ogiZ0b` batches) | **`160` living clips** | **`2,080c`** nominal (**`2,600c`** w/ 25% retry buffer) | **`3` waves (~3.5h)** |
| **Long (`L01..L10`)** (`8m30s–13m`) | Per Long | `100` primary anchors + `40` extra multi-angle/macro/OTS frames + `1` `16:9` thumb = **`141` frames (`0c`)** | **`55` living clips** (`15` for **100%-motion First-60s Cold Open** + `40` M1 2-beat/3-beat windows covering `~95–110` narrative beats; `18–24` beats for slow `6–12s` giant-text maps & evidence boards) | `35 × veo_3_1_lite 8s` (`350c`) + `20 × macaron_cookie 8s` (`480c`) = **`830c`** *(stretch 80 clips = `1,220c`)* | **`1` wave/Long** |
| **All 10 Longs** | `L01..L10` | **`1,410` frames (`0c`)** (`~360` 4-prompt batches) | **`550` living clips** | **`8,300c`** nominal (**`10,375c`** w/ 25% retry buffer) | **`10` waves (~12.5h)** |
| **GRAND TOTAL** | **20 Videos** | **`1,680` `BELUGA` frames (`0` credits)** | **`710` living clips** | **`10,380c`** nominal / **`12,975c`** buffered (**`12.99%`** of `99,876` Ultra; **`86,901c` surplus**) | **`13` waves (~16.0h)** |

> **Key Bottleneck Finding**: Ultra credits are **~8x in surplus** (`12,975c` needed vs `99,876c` recorded). The **binding constraint is the Host-IP `55` clips/rolling-hour cap**, making `55` multi-beat living clips/Long (`1` wave/Long) + `16` clips/Short (`3` Shorts/wave) the optimal throughput-to-cinema ratio.

---

## 5. OmniVoice & Colab T4 `h264_nvenc` Parallelization Plan (Across 8 T4 Accounts)

### 5.1 OmniVoice Audio (`VietNarrator_su_ke_lai`, `-11.0 LUFS` / `<= -1.0 dBTP`)
- **Voice Contract (`sys/assets/voices/ch_su_ke_lai/profile.json`)**: `base_omnivoice_speed = 1.12`, `atempo = 1.161` (`1.30x` net), `inter_beat_gap_sec = 0.12`, studio presence EQ, `encode_calibrated_m4a()` verification (`<= -1.0 dBTP` post-AAC).
- **Parallelism**:
  - **Shorts**: `3` T4 workers (`--colab-tts-workers 3`) per Short (`~90–120s`), running concurrently with Stage A `BELUGA` (`~6` GPU-min/Short = **`60` GPU-min** total).
  - **Longs**: `4` T4 workers per Long (`25–30` sentence groups/VM, `batch_size=8`, `num_step=32` FP16) = `~3.0–3.5m` wall time (`~14` GPU-min/Long = **`140` GPU-min** total), scheduled **inside the 10–15 min Flow IP breathers**.

### 5.2 Colab T4 `FFmpeg h264_nvenc` Rendering & `ERR-20261125-02` Safety Invariants
1. **`<28 MB` Zip Sharding (`ERR-20261125-02`)**: Never pack all Long JPG/MP4/WAV assets into a single >35 MB archive. Split media into **`<= 28 MB` `ZIP_STORED` bundles** (`media_shard_01.zip .. media_shard_k.zip`) and extract to `/dev/shm`.
2. **`fps=30` Before `trim=end_frame` (`ERR-20261125-02`)**: On all retimed clips (`setpts < 1.0`, e.g. `pts=0.55` tactical maps or Flow segments), enforce `tpad=stop_mode=clone:stop_duration=1.5,fps=30,settb=1/30,trim=end_frame={rf},setpts=PTS-STARTPTS` so frame counts are exact and `xfade` offsets never truncate.
3. **Pre-Graded Static/Map Frames + Calibrated M4A**: Pre-grade non-video images once (never `-loop 1` + per-frame LUTs on 2-vCPU Colab VMs) and verify post-AAC `true_peak_dbtp <= -1.0` via `encode_calibrated_m4a()` (`-c:v copy` remux fallback if > `-0.85 dBTP`).
4. **Account Fan-Out (`8` Active T4 Accounts: `01, 04, 05, 12, 17, 18, 19, 20` + `08` Hot Spare)**:
   - **Shorts (`single_pass` 2K `1440x2560`)**: `4` T4 workers/Short (`--colab-render-workers 4`, `0` overhang, `-bf 0 -g 30 -b:v 10M -preset p4`) + `<2s` local lossless concat -> `~3m`/Short (`12` GPU-min/Short = **`120` GPU-min**). Two Shorts can run simultaneously on `4 + 4` accounts, serialized at final disk mux by `GlobalRenderIoLock`.
   - **Longs (`1080p` `1920x1080` NVENC)**: Dispatch **`4–8` Longs in parallel (`1` Long per T4 VM using `3` internal NVENC streams on `/dev/shm`, `~10–11m` wall time for up to 8 Longs)**, OR use `produce_su_ke_lai_long_m1.py --total-shards 8` (`~3m`/Long across all 8 VMs) for single-episode priority runs (`~12` GPU-min/Long = **`120` GPU-min**).
   - **Total Colab Compute**: `60 + 140 + 120 + 120 = 440` T4 GPU-minutes (**`7.33` GPU-hours**) = **`25.9%`** of the active 8 accounts' current `28.30h` (`22.0%` including `account-08`).
5. **Watchdogs & Teardown**: Arm `schedule(DurationSeconds=45, TimerCondition="any")` for any remote job `>30s`; stop multi-account failover after `2` consecutive `COLAB_EXEC_UNCONFIRMED`; run `pm.stop_pool(..., unassign_server=True)` / `./pipeline colab teardown` and `./pipeline flow stop` after each wave.

---

## 6. Phased Execution Schedule

1. **Wave 0 (Pre-Flight, 15m)**: Reconcile `account-12` & `account-20`; exclude `03, 15, 16`; park `02, 10, 13` until window reset; optionally refresh `profile_en01` (`+25,050c`); route Stage A `BELUGA` to the 7 zero-credit specialists.
2. **Wave 1 (`S01..S10`, 3 IP Waves, ~3.5–4.0h)**: Run `3` Shorts/hour in Flow Stage B (`<=55` clips/hr) overlapped with Stage A `BELUGA` (`0c`) + `3`-worker Colab OmniVoice, then render Shorts on `4`-worker Colab T4 during the `12m` IP breathers.
3. **Wave 2 (`L01..L05`, 5 IP Waves, ~6.0–6.5h)**: Run `1` Long/hour (`55` living clips, `830c`) across `profile_22, 18, en03` (+ `en01` / Standard fallback), synthesize `4`-worker OmniVoice during breathers, and fan out `L01..L05` NVENC renders across `5` T4 VMs concurrently.
4. **Wave 3 (`L06..L10`, 5 IP Waves, ~6.0–6.5h)**: Repeat `1` Long/hour wave + concurrent `5`-VM T4 NVENC render (`account-10/13/02` reset by Wave 3 if extra capacity desired), run `ffprobe` + `ebur128` + frame QA on all 20 MP4s, and execute full teardown.
