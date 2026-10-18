# Colab runtime manager delivery — 2026-10-18

## Observed account state

The final bounded audit at 16:20:58 Asia/Ho_Chi_Minh verified all 20 configured profiles. They represent 15 distinct Google identities. Two existing T4 kernels responded (account-01 and account-03); 13 identities had no active server VM. GPU allocation capacity on those idle identities was not tested.

Duplicate alias pairs: account-01/account-09, account-02/account-11, account-03/account-06, account-04/account-07 and account-05/account-14. Profile count must not be treated as independent GPU capacity.

## Changes and activation

- Production audio/render claims are atomic and keyed by Google identity, with compatible historical session locks.
- Unknown remote sends retain their journal ownership after the local runner exits. Exact collection is permitted without freeing other pending owners; identical inputs in another job cannot bypass the owner guard.
- Unbound jobs preserve automatic pool selection and filter workload role, frozen job pool, budget and current health. Exact job/runtime bindings remain exact.
- The global management selection is now automatic, with account-10 as the preferred default. Existing job snapshots and submitted request pins were verified unchanged by this activation. No GPU was allocated by activation.
- Allocation starts are staggered between controllers. Health probes also respect identity/session locks.
- The dashboard exposes cached account health, duplicate aliases and explicit background audits/credential renewal. The dedicated account resource endpoint returned actual local data in 1.1 seconds without hashing video jobs.
- Synthetic TTS test profiles, budgets and dispatch state are isolated from production. A synthetic dispatch record accidentally written during the first test run was archived and removed; production request journals were preserved.

Dashboard: http://127.0.0.1:8765/#accounts

PR: https://github.com/hongphuoc6104/LongVidYtb/pull/3

Revision: dfe182cca6569336b506b5d5f7547c6ff813278c

## Verification

The final isolated conveyor passed 276 tests, 16 subtests, AST assertion checks, critique, playbook schema checks, syntax and configured lint gates. Browser fixture checks verified the dashboard tabs and media/review flow. Focused regressions additionally covered cached account loading, duplicate identity locks, unresolved owner retention and credential renewal.

Both GitHub Actions runs for the final revision succeeded: push run 39115267012 and pull-request run 39115269918. These checks use isolated fixtures; live audit evidence demonstrates authentication and responding T4 kernels, not a completed new video generation.

## Flow diagnosis

No Flow cookies were cleared and no Flow page was reset by this investigation. Existing code has a recovery branch that clears Flow site storage and selected cookies before reloading. Historical logs show Flow recovery and lease-quota code adoption, followed by successful image collection, but do not prove that an individual cookie cleanup completed successfully. Clearing local browsing data is not evidence that a provider-side activity restriction has been lifted. Preserve in-flight requests during diagnosis.

## Existing production request

Adversarial 9:16's revised audio request remains owned by account-03/video-pilot-tts. The inspected remote directory contained uploaded input/support files and no output directory. Its original ambiguous journal is preserved; this management change did not resubmit or move the request.
