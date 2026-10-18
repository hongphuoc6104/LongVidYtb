# Recent production job diagnosis — 2026-10-18

All times below use Asia/Ho_Chi_Minh (UTC+07:00). This is an observation report, not a production state change.

## Evidence and scope

- Read the event ledger using SQLite read-only mode and official `PilotView` / `execution.observe` / `execution.next_step` observations.
- Inspected revision failures, durable request journals, saved Colab execution history, runtime bindings and local processes.
- Independently inspected all six exported MP4s with ffprobe: H.264 video, AAC audio and the expected 1920x1080 or 1080x1920 dimensions were present.
- A bounded read-only remote directory probe on the original account-03 / video-pilot-tts session timed out after 35 seconds. Remote completion of its pending request remains unconfirmed.
- No engine changes, job reruns, generation, allocation, teardown or manual state/database changes were performed.

## Latest jobs

Elapsed time is job creation to the first collected video artifact, including authoring, scheduling gaps and recovery. It is not GPU execution time.

| Job | Created | Collected video | Elapsed | Observed current state |
| --- | --- | --- | --- | --- |
| adversarial-ai-16x9 | 11:13:40 | 11:44:06 | 30m 26s | Approved modules and collected MP4 |
| adversarial-ai-9x16 | 11:13:45 | 12:17:49 | 64m 04s | Old video exists; revised content is blocked at audio revision 2 |
| collectors-fallacy-16x9 | 11:26:16 | 12:43:09 | 76m 53s | Official observation: complete |
| collectors-fallacy-9x16 | 11:26:38 | 13:09:46 | 103m 08s | Official observation: complete |
| reviewer-2-novelty-bias-16x9 | 11:34:33 | 13:57:41 | 143m 08s | Official observation: complete |
| reviewer-2-nobel-rejections-9x16 | 11:34:37 | 13:46:34 | 131m 57s | Official observation: complete |

## Current blocker: adversarial-ai-9x16

1. The original 41.62-second MP4 was collected at 12:17:49.
2. At 13:48:53, `brief_revised` recorded “Upgrade to 19-scene long-form 9:16 explainer”. Content, audio, images and render were marked stale by the engine.
3. Content revision 2 was accepted at 13:49:00. The new TTS request contains 66 segments.
4. Audio revision 2 failed at 13:50:17 with `COLAB_COMMAND_FAILED: exec (exit 1, type=TimeoutError)`.
5. The durable request journal remains `ambiguous`, owned by account-03 / video-pilot-tts:
   `runs/adversarial-ai-9x16/cache/colab-tts/ddd144c3faae3f98a77f75852658f8653540abe8ad95360a44aa26d21ad2ae30/state.json`.
6. Saved remote history confirms request upload around 13:49:38, but has no successful TTS completion entry for this request. The local cache contains no collected result.
7. An existing account_cli directory-inspection process (PID 129634, started 13:54:04) was still waiting more than 70 minutes later. Its invocation lacked a command-line timeout and an outer subprocess timeout.
8. A separate diagnostic probe with both a CLI execution timeout and a 35-second outer deadline also timed out. This confirms that the control path is currently unresponsive; it does not prove that the remote GPU is idle, busy, out of memory, or disconnected.
9. No local Pilot production runner or active job owner was present. The next official action is `run_or_repair`, phase `audio`; it is not a user review checkpoint.

The immediate failure class is remote execution/transport timeout with an ambiguous submitted request. The precise remote kernel or network cause is not established by the available evidence. Recovery must reconcile or collect this exact request on its original owner before considering another send.

## Why completed jobs took so long

### Flow failures and request reconciliation

Repeated `PUBLIC_ERROR_UNUSUAL_ACTIVITY` failures occurred in both Reviewer jobs, Collector 16:9 and Adversarial 9:16, sometimes after four attempts. Follow-on attempts encountered `M2_AMBIGUOUS` or `FLOW_BUDGET: Existing request: collect/reconcile, never resubmit`. Those guards preserve uncertain request ownership and block another submission; repeatedly resuming without resolving the request does not advance production.

The inspected jobs share the same frozen Flow browser binding (Profile 1). Their `flow_account_active` events also name that browser account. This establishes shared logical ownership; downloaded sidecars do not record the physical worker profile, so these records alone cannot establish which profile executed every image or the precise cause of the provider activity flag.

### Long scheduling/recovery gaps

- Reviewer 16:9: image failure at 11:58:52; next image revision started at 13:17:03 — a 78m 11s gap. No new image revision started during this interval. Several engine-adoption/recovery events occurred in the gap.
- Reviewer 16:9: render revision 1 failed with `'wav'` at 13:23:28; revision 2 started at 13:47:04 — another 23m 36s gap. The bare exception message does not provide enough evidence to establish its exact field-access origin.
- Reviewer 9:16: content execution started at 12:14:54, approximately 40 minutes after job creation.
- Collector 9:16: audio was accepted at 11:43:44; the first image revision started at 12:29:33 — a 45m 49s gap.

These intervals should not be reported as GPU processing time. The event ledger does not establish whether every gap was an intentional operator wait, contention, diagnosis or an absent coordinator.

### Colab session preparation and contention

Observed errors include `COLAB_SESSION_NOT_FOUND`, `COLAB_VERIFIED_SETUP_REQUIRED`, `COLAB_SESSION_BUSY`, `COLAB_RUNTIME_BINDING_ACCOUNT_MISMATCH`, and `COLAB_ALLOCATION_PENDING`. Saved history repeatedly shows fresh runtimes initially lacking OmniVoice, followed by installation. A registry containing many accounts does not guarantee parallel execution when jobs remain bound to one exact runtime.

### Validation and implementation failures

- Reviewer 16:9 initially hit `FLOW_CLICHE_FORBIDDEN`, then `FLOW_TEMPLATE_PIN_CHANGED`, followed later by the bare render error `'wav'`.
- Collector 9:16 hit pinned-owner conflicts and a missing `ui-proof.json` requirement before later succeeding.
- Reviewer 9:16's render error was more specific than the generic local `COLAB_EXEC_UNCONFIRMED` label: saved remote history and its failed request journal show visual pacing validation errors (a 0.700-second hold, sparse body beats and only two opening starts where three to five were required).
- Reviewer jobs each recorded six `code_adopted` events. Changes included Flow recovery, lease quota handling, visual pacing and thumbnail generation. This was production interleaved with implementation/recovery work.

### Final successful render intervals

| Job | Final render started | Accepted | Interval |
| --- | --- | --- | --- |
| adversarial-ai-16x9 | 11:38:13 | 11:44:06 | 5m 53s |
| adversarial-ai-9x16, old version | 12:13:34 | 12:17:49 | 4m 15s |
| collectors-fallacy-16x9 | 12:26:57 | 12:43:08 | 16m 11s |
| collectors-fallacy-9x16 | 13:00:39 | 13:09:45 | 9m 06s |
| reviewer-2-novelty-bias-16x9 | 13:47:04 | 13:57:41 | 10m 37s |
| reviewer-2-nobel-rejections-9x16 | 13:36:42 | 13:46:34 | 9m 52s |

These intervals include preparation, upload, remote processing, download and acceptance, not only frame rendering. Collected outputs are technically readable; this investigation did not assess perceived picture, narration or editorial quality.

## Recommended order of remediation

1. Reconcile the exact pending Adversarial TTS request on account-03 / video-pilot-tts, preserving the existing journal and request identity.
2. Put outer deadlines and child-process cleanup around all operational probes; CLI execution timeouts alone do not bound runtime connection/setup.
3. Resolve ambiguous requests before resuming a stage. Route only eligible new work through accounts/profiles with verified readiness and available capacity.
4. Validate prompt policy, frozen template identity, audio contract and visual pacing before expensive remote stages where feasible.
5. Expose last progress, active runner, blocked reason, pending request owner and time spent waiting separately in status reporting.
